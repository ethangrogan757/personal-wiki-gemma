"""The harness: turns a user's request into retrieval, a prompt, a model call and a checked result.

ask mode (RAG, standalone):
    question -> retrieve top passages from vault/raw -> number them [1]..[k]
             -> research rules + passages + question -> local Gemma (JSON: answer, found?)
             -> check every [n] citation against the passages -> display + save evidence card
It never sees chat history or the assistant persona, so each question is answered on its own.

chat mode (personal assistant, see ChatSession below):
    message -> router call: does this need the notes? (JSON: yes/no + search query)
            -> if yes, retrieve passages for this turn only
            -> persona + recent conversation + message (+ passages) -> local Gemma
            -> check citations -> display; conversation kept in memory for follow-ups
"""
import json
import re
from dataclasses import dataclass, field

from . import config, ingest, llm, retrieval

ASK_K = 5              # passages sent to the model (~1,500 tokens)
ASK_TEMPERATURE = 0.1  # factual answers should be consistent between runs
CITATION = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")

# The model writes its answer first, then judges it with a yes/no field. An earlier version
# used a text field {"status": "answered" | "insufficient_evidence"}: Gemma E2B chose
# "insufficient_evidence" even right after writing a correct, cited answer, in both field
# orders. A boolean judged correctly (see evidence/ask/01-status-first-bug, 02-status-last-bug).
ASK_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string"},
        "answer_found_in_passages": {"type": "boolean"},
    },
    "required": ["answer", "answer_found_in_passages"],
}


@dataclass
class AskResult:
    question: str
    hits: list                 # retrieval.Hit objects, in the order numbered for the model
    messages: list             # the exact prompt sent
    status: str = ""
    answer: str = ""
    cited: list = field(default_factory=list)      # passage numbers cited, in order
    invalid: list = field(default_factory=list)    # cited numbers that don't exist
    warnings: list = field(default_factory=list)
    reply: object = None       # llm.Reply (timing, tokens)
    retry_note: str = ""       # set when the harness had to ask again for citations


def load_prompt(name):
    path = config.PROMPTS_DIR / name
    if not path.exists():
        raise llm.ModelUnavailable(f"Missing instructions file: {path.relative_to(config.PROJECT_ROOT)}")
    return path.read_text()


def format_passages(hits):
    blocks = []
    for n, hit in enumerate(hits, start=1):
        p = hit.passage
        blocks.append(f"[{n}] source: {p.source}, lines {p.start_line}-{p.end_line}, section: {p.section}\n{p.text}")
    return "\n\n".join(blocks)


def build_ask_messages(question, hits):
    passages = format_passages(hits) if hits else "(no passages matched the question)"
    return [
        {"role": "system", "content": load_prompt("wiki-instructions.md")},
        {"role": "user", "content": f"SOURCE PASSAGES:\n\n{passages}\n\nQUESTION: {question}"},
    ]


def check_citations(result):
    """Record which passages the answer cites, and flag citations that point at nothing."""
    numbers = []
    for group in CITATION.findall(result.answer):
        numbers += [int(n) for n in group.split(",")]
    result.cited = list(dict.fromkeys(numbers))
    result.invalid = [n for n in result.cited if not 1 <= n <= len(result.hits)]
    if result.invalid:
        result.warnings.append(f"cites passage(s) {result.invalid}, which weren't provided")
    if result.status == "answered" and not result.cited:
        result.warnings.append("answered without citing any passage, so the answer is unsupported")
    valid = [n for n in result.cited if n not in result.invalid]
    if result.status == "insufficient_evidence" and valid:
        result.warnings.append("status says insufficient evidence, but the answer cites passages; check it by hand")


CITE_REMINDER = ("Your answer has no passage citations. Rewrite the same answer, ending each factual "
                 "sentence with the [n] number of the passage that states it.")


def _call(result, messages):
    reply = llm.chat(messages, temperature=ASK_TEMPERATURE, schema=ASK_SCHEMA)
    data = json.loads(reply.text)
    result.status = "answered" if data["answer_found_in_passages"] else "insufficient_evidence"
    result.answer, result.reply = data["answer"].strip(), reply
    result.warnings, result.cited, result.invalid = [], [], []
    check_citations(result)
    return reply


def ask(question):
    hits = retrieval.search(question, k=ASK_K)
    result = AskResult(question, hits, build_ask_messages(question, hits))
    first = _call(result, result.messages)
    if result.status == "answered" and not [n for n in result.cited if n not in result.invalid]:
        # Harness-enforced citations: one retry, recorded in the result.
        retry = result.messages + [{"role": "assistant", "content": first.text},
                                   {"role": "user", "content": CITE_REMINDER}]
        uncited = result.answer
        _call(result, retry)
        result.messages = retry
        result.retry_note = f"first answer had no citations and was retried: {uncited!r}"
        result.reply.seconds += first.seconds
    return result


# ---------- chat mode ----------

CHAT_K = 4                 # passages per lookup
CHAT_TEMPERATURE = 0.7     # more natural voice than ask
HISTORY_MESSAGES = 10      # last 5 exchanges are resent each turn (~fits in 8K with passages)

def wiki_projects():
    """Project name -> source file, from the ingest catalog (e.g. 'Pac-Man DQN' -> vault/raw/Pac-Man DQN README.md)."""
    catalog = ingest.load_catalog()
    return {s["plan"]["project"]["title"]: (s["raw_path"], s["plan"]["project"]["description"])
            for s in catalog["sources"] if s.get("plan")}


def router_schema(project_names):
    return {
        "type": "object",
        "properties": {
            "look_up_notes": {"type": "boolean"},
            "projects": {"type": "array", "items": {"type": "string", "enum": sorted(project_names)}},
            "search_query": {"type": "string"},
        },
        "required": ["look_up_notes", "projects", "search_query"],
    }


@dataclass
class ChatTurn:
    user: str
    reply: str = ""
    looked_up: bool = False
    decided_by: str = ""       # "router" or "/notes"
    query: str = ""
    projects: list = field(default_factory=list)   # projects the router said the message is about
    hits: list = field(default_factory=list)
    cited: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    seconds: float = 0.0


class ChatSession:
    """One conversation. History lives only in memory; nothing is saved as a memory the assistant reads back."""

    def __init__(self):
        self.persona = load_prompt("persona.md")
        self.projects = wiki_projects()
        project_list = "\n".join(f"- {name}: {desc}" for name, (_, desc) in self.projects.items())
        self.router_rules = f"{load_prompt('chat-router.md')}\nPROJECTS IN THE WIKI:\n{project_list}\n"
        self.history = []   # plain {"role", "content"} turns, without the looked-up passages
        self.turns = []

    def reset(self):
        self.history = []

    def route(self, message):
        """Ask the model (cheaply) whether this message needs the notes, which projects, and what to search for."""
        recent = "\n".join(f"{m['role'].upper()}: {m['content'][:300]}" for m in self.history[-4:])
        messages = [
            {"role": "system", "content": self.router_rules},
            {"role": "user", "content": f"RECENT CONVERSATION:\n{recent or '(start of conversation)'}\n\nLATEST MESSAGE: {message}"},
        ]
        reply = llm.chat(messages, temperature=0, schema=router_schema(self.projects))
        data = json.loads(reply.text)
        projects = [p for p in dict.fromkeys(data["projects"]) if p in self.projects]
        return data["look_up_notes"], data["search_query"].strip(), projects, reply.seconds

    def send(self, message, forced_query=None):
        turn = ChatTurn(user=message)
        if forced_query:
            turn.looked_up, turn.query, turn.decided_by = True, forced_query, "/notes"
        else:
            turn.looked_up, turn.query, turn.projects, turn.seconds = self.route(message)
            turn.decided_by = "router"

        if turn.looked_up:
            sources = [self.projects[p][0] for p in turn.projects]
            turn.hits = retrieval.search_sources(turn.query or message, sources, k=CHAT_K)
            notes = format_passages(turn.hits) if turn.hits else "(the search found no matching passages)"
            content = f"{message}\n\nNOTES LOOKED UP FOR THIS MESSAGE (search: \"{turn.query}\"):\n\n{notes}"
        else:
            content = f"{message}\n\n(No notes were looked up for this message, so don't cite anything.)"

        messages = [{"role": "system", "content": self.persona}] + self.history[-HISTORY_MESSAGES:] \
            + [{"role": "user", "content": content}]
        reply = llm.chat(messages, temperature=CHAT_TEMPERATURE)
        turn.reply, turn.seconds = reply.text, turn.seconds + reply.seconds

        numbers = []
        for group in CITATION.findall(turn.reply):
            numbers += [int(n) for n in group.split(",")]
        turn.cited = list(dict.fromkeys(numbers))
        if turn.cited and not turn.looked_up:
            turn.warnings.append(f"cites {turn.cited} but no notes were looked up this turn")
        elif any(not 1 <= n <= len(turn.hits) for n in turn.cited):
            turn.warnings.append(f"cites passages that weren't provided: {turn.cited}")

        # Only the plain message and reply are remembered, so old passages don't crowd the context.
        self.history += [{"role": "user", "content": message}, {"role": "assistant", "content": turn.reply}]
        self.turns.append(turn)
        return turn
