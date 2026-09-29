"""Command-line entry point: parses the command and hands it to the right mode.

    wiki ingest [PATH]     read sources, write linked wiki notes, rebuild the index
    wiki reindex           rebuild the search index from vault/raw (no model involved)
    wiki check             check vault links, headings and note names
    wiki search "QUERY"    show matching original passages (no model involved)
    wiki ask "QUESTION"    standalone factual answer with citations
    wiki chat              personal assistant with conversation memory
    wiki status            show model, mode and whether Ollama is ready
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from . import config, evidence, harness, ingest, llm, retrieval, vaultcheck

EXAMPLES = f"""
examples:
  wiki ingest ./vault/raw
  wiki ingest ./vault/raw --force
  wiki reindex
  wiki check
  wiki search "row level security"
  wiki ask "What learning rate did I use for the Pac-Man DQN?" --mode local
  wiki chat
  wiki status

configuration (environment variables):
  WIKI_MODEL    local Ollama model      (default: {config.MODEL})
  OLLAMA_HOST   Ollama server address   (default: http://localhost:11434)
  WIKI_NUM_CTX  context window, tokens  (default: {config.NUM_CTX})

required inputs:
  - Ollama running with the model pulled (ingest, ask, chat)
  - source files (.md or .txt) in vault/raw/
  - search needs only the index built by 'wiki ingest' or 'wiki reindex'; the model can be off
"""


def build_parser():
    parser = argparse.ArgumentParser(
        prog="wiki",
        description="Personal wiki over my coding-class projects, powered by local Gemma (offline).",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    p = sub.add_parser("ingest", help="read sources, generate linked wiki notes, update the index")
    p.add_argument("path", nargs="?", default=str(config.RAW_DIR),
                   help="source folder or file (default: vault/raw); files elsewhere are copied into vault/raw unchanged")
    p.add_argument("--force", action="store_true", help="regenerate notes even if the source is unchanged (overwrites review edits)")
    p.add_argument("--replan", action="store_true", help="let Gemma choose the notes again instead of reusing the saved plan")

    sub.add_parser("reindex", help="rebuild the search index from vault/raw (no model needed)")
    sub.add_parser("check", help="check the vault: broken links, headings, note names, duplicates")

    p = sub.add_parser("search", help="show original matching passages and paths (no answer generated)")
    p.add_argument("query", help="words to look for")
    p.add_argument("-k", type=int, default=5, help="number of passages to show (default: 5)")

    p = sub.add_parser("ask", help="standalone factual answer with citations, or 'insufficient evidence'")
    p.add_argument("question")
    p.add_argument("--mode", choices=["local", "online"], default="local", help="where the model runs (default: local)")
    p.add_argument("--show-prompt", action="store_true", help="print the exact prompt sent to the model")
    p.add_argument("--label", help="title for the saved evidence card, e.g. 'Test 1'")

    p = sub.add_parser("chat", help="personal assistant; uses conversation context, looks up notes when useful")
    p.add_argument("--mode", choices=["local", "online"], default="local", help="where the model runs (default: local)")

    sub.add_parser("status", help="show model, execution mode and whether the local model is ready")
    return parser


def require_local(mode):
    if mode != "local":
        sys.exit("error: online mode isn't implemented. This project runs locally only (the default).")


def cmd_status(args):
    print(f"model:     {config.MODEL}")
    print(f"mode:      local (Ollama at {config.OLLAMA_HOST})")
    print(f"context:   {config.NUM_CTX} tokens")
    print(f"vault:     {config.VAULT_DIR}")
    try:
        llm.check_ready()
        print("model ready: yes")
    except llm.ModelUnavailable as err:
        print(f"model ready: no\n  {err}")


def cmd_ingest(args):
    path = Path(args.path)
    if not path.exists():
        sys.exit(f"error: source folder or file not found: {path}")
    written, elapsed = ingest.run(path, force=args.force, replan=args.replan)
    print(f"\nwrote {len(written)} note blocks in {elapsed:.0f}s; updated vault/index.md and the search index")
    cmd_check(args)


def cmd_check(args):
    result = vaultcheck.check()
    print(f"vault check: {result['files']} files, {result['notes']} wiki notes, {result['links']} links")
    for problem in result["problems"]:
        print(f"  PROBLEM: {problem}")
    if not result["problems"]:
        print("  no problems found")


def cmd_reindex(args):
    if not config.RAW_DIR.is_dir():
        sys.exit(f"error: source folder not found: {config.RAW_DIR}")
    passages = retrieval.build_index()
    sources = sorted({p.source for p in passages})
    print(f"indexed {len(passages)} passages from {len(sources)} sources -> {retrieval.INDEX_FILE.relative_to(config.PROJECT_ROOT)}")
    for s in sources:
        print(f"  {sum(p.source == s for p in passages):3d}  {s}")


def cmd_search(args):
    hits = retrieval.search(args.query, k=args.k)
    print(f'search: "{args.query}"  (BM25 keyword search over vault/raw, no model used)\n')
    if not hits:
        print("No matching passages.")
        return
    for rank, hit in enumerate(hits, start=1):
        p = hit.passage
        print(f"[{rank}] {p.source}:{p.start_line}-{p.end_line}  score {hit.score:.2f}")
        print(f"    section: {p.section}")
        print(f"    matched: {', '.join(hit.matched)}")
        print("    " + p.text.replace("\n", "\n    "))
        print()
    path = evidence.save_search_card(args.query, hits)
    print(f"evidence card: {path.relative_to(config.PROJECT_ROOT)}")


def cmd_ask(args):
    require_local(args.mode)
    print(f'ask: "{args.question}"\n  (local · {config.MODEL} · standalone: no chat history, no persona)\n')
    result = harness.ask(args.question)
    if args.show_prompt:
        for m in result.messages:
            print(f"----- {m['role']} -----\n{m['content']}\n")
        print("----- end of prompt -----\n")
    if result.status == "insufficient_evidence":
        print("INSUFFICIENT EVIDENCE")
    print(result.answer + "\n")
    if result.cited:
        print("Citations:")
        for n in result.cited:
            if 1 <= n <= len(result.hits):
                p = result.hits[n - 1].passage
                preview = " ".join(p.text.split())[:110]
                print(f"  [{n}] {p.source}:{p.start_line}-{p.end_line}  ({p.section})\n      \"{preview}…\"")
    if result.retry_note:
        print("  (harness retried once: the first answer had no citations)")
    for w in result.warnings:
        print(f"  CITATION CHECK: {w}")
    r = result.reply
    print(f"\n{len(result.hits)} passages retrieved, {len(result.cited)} cited · {r.seconds:.1f}s · "
          f"{r.prompt_tokens} prompt tokens")
    path = evidence.save_ask_card(result, label=args.label)
    print(f"evidence card: {path.relative_to(config.PROJECT_ROOT)}")


CHAT_HELP = """commands:
  /notes <topic>   look up the wiki for this topic, even if the router wouldn't
  /reset           forget this conversation
  /help            show this help
  /exit            quit (the transcript is saved to evidence/chat/)"""


def cmd_chat(args):
    require_local(args.mode)
    llm.check_ready()
    session, started = harness.ChatSession(), datetime.now()
    piped = not sys.stdin.isatty()   # e.g. printf "hi\n/exit\n" | wiki chat, for recorded checks
    print(f"Scout · chat mode (local · {config.MODEL})")
    print("Personal assistant with conversation memory; looks up your notes only when needed. /help for commands.\n")
    try:
        while True:
            try:
                line = input("you> ").strip()
            except EOFError:
                break
            if piped:
                print(line)
            if not line:
                continue
            if line in ("/exit", "/quit"):
                break
            if line == "/help":
                print(CHAT_HELP + "\n")
                continue
            if line == "/reset":
                session.reset()
                print("(conversation cleared)\n")
                continue
            forced = None
            if line.startswith("/notes"):
                forced = line[len("/notes"):].strip()
                if not forced:
                    print("usage: /notes <topic>\n")
                    continue
                line = f"What do my notes say about {forced}?"
            turn = session.send(line, forced_query=forced)
            print(f"\nscout> {turn.reply}\n")
            if turn.looked_up:
                scope = ", ".join(turn.projects) or "all projects"
                print(f'  [looked up notes · {scope} · search: "{turn.query}" · {len(turn.hits)} passages]')
                for n in turn.cited:
                    if 1 <= n <= len(turn.hits):
                        p = turn.hits[n - 1].passage
                        print(f"  [{n}] {p.source}:{p.start_line}-{p.end_line}  ({p.section})")
            else:
                print("  [no notes lookup]")
            for w in turn.warnings:
                print(f"  CITATION CHECK: {w}")
            print(f"  ({turn.seconds:.1f}s)\n")
    finally:
        if session.turns:
            path = evidence.save_chat_transcript(session, started)
            print(f"transcript saved: {path.relative_to(config.PROJECT_ROOT)}")


COMMANDS = {"status": cmd_status, "ingest": cmd_ingest, "reindex": cmd_reindex, "check": cmd_check,
            "search": cmd_search, "ask": cmd_ask, "chat": cmd_chat}


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return
    try:
        COMMANDS[args.command](args)
    except (llm.ModelUnavailable, retrieval.IndexMissing) as err:
        sys.exit(f"error: {err}")
    except KeyboardInterrupt:
        sys.exit("\ninterrupted")


if __name__ == "__main__":
    main()
