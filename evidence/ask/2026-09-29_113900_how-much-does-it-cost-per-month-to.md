# Ask evidence card

- **Question:** How much does it cost per month to host my Networking Tracker?
- **Mode:** ask (standalone; no chat history, no persona)
- **Execution:** local, `gemma4:e2b-it-qat` via Ollama at http://localhost:11434
- **Run at:** 2026-09-29 11:39:00
- **Response time:** 2.0s (1387 prompt tokens, 40 output tokens)

## Answer

**Status:** `insufficient_evidence`

The provided sources do not contain information about the monthly hosting cost for the Networking Tracker.

## Citations

- (none)

## Retrieved passages (exactly as sent to the model)

### [1] `vault/raw/Networking Tracker README.md` lines 41–45
Section: Architecture · BM25 score 4.09 · matched: per, network, tracker

```text
- Never holds an elevated/service-role credential.
- Never touches `DATABASE_URL`.
- Only ever forwards the caller's own Better Auth JWT to the Data API, per request. So a compromised backend can't do anything a compromised frontend couldn't already do — RLS is still the real authorization boundary either way.

**How the backend gets a token for the Data API.** `@neondatabase/neon-js`'s `createClient` has a documented "external auth provider" form for exactly this: instead of a Better Auth `auth` block, you pass `dataApi.getToken`, a function it calls before every request. `api/_lib/dataApi.ts` uses this to build a fresh, per-request client from whatever bearer token the frontend sent — so it stays stateless and never has its own session.
```

### [2] `vault/raw/Custom LLM README.md` lines 215–223
Section: One limitation, explained, and what I tried next · BM25 score 3.44 · matched: much

```text
1. **Category mismatch.** The 24 `extend_corpus` cases span all 8 extension categories, and I'd
   only written material for 2 of them. The other 6 categories (spatial relations,
   categories/analogies, reference, grammar, sequence, everyday knowledge) were always going to
   be unscorable, independent of how much training happened.
2. **Single-occurrence words and the random split.** Even within negation/opposites, some needed
   words only appeared once in my sentences. Vocabulary is built only from the training split,
   and the notebook's 90/10 passage split is random — a word appearing in exactly one passage has
   roughly a 1-in-10 chance of that passage landing entirely in validation, taking the word out of
   the trained vocabulary with it.
```

### [3] `vault/raw/Networking Tracker README.md` lines 100–116
Section: Schema and Row Level Security · BM25 score 3.42 · matched: per, network, tracker

```text
Row Level Security is enabled, with one ownership policy per operation:

```sql
alter table contacts enable row level security;

create policy contacts_select on contacts for select to authenticated
  using (auth.user_id() = user_id);

create policy contacts_insert on contacts for insert to authenticated
  with check (auth.user_id() = user_id);

create policy contacts_update on contacts for update to authenticated
  using (auth.user_id() = user_id) with check (auth.user_id() = user_id);

create policy contacts_delete on contacts for delete to authenticated
  using (auth.user_id() = user_id);
```
```

### [4] `vault/raw/Custom LLM README.md` lines 87–95
Section: Prediction vs. what actually happened · BM25 score 3.33 · matched: much

```text
Going into the full 3,000-step runs, I expected the much larger loss drop to produce fully
grammatical sentences (it did — see below), and I expected the corpus extension to noticeably
improve the `extend_corpus` eval scores (my first attempt completely missed that — 0/24 correct).
Diagnosing *why* was the most useful part of the assignment: it wasn't a training bug, it was a
vocabulary-coverage gap I could actually fix, so I predicted that covering all 8 extension
categories instead of 2 would raise the scorable count substantially even if it didn't get every
case right. My second attempt confirmed that: `extend_corpus` scorable cases went from 1/24 to
7/24, and correct answers from 0/24 to 3/24 — a real, measurable improvement, though still far
from solved (details below).
```

### [5] `vault/raw/Networking Tracker README.md` lines 3–13
Section: Networking Tracker · BM25 score 3.28 · matched: network, tracker

```text
A small, secure contacts tracker for keeping up with your professional network: create, view, edit, delete, sort, and filter contacts, each visible only to the account that created it.

**Live**: [networking-tracker-psi.vercel.app](https://networking-tracker-psi.vercel.app)
**Repo**: [github.com/ethangrogan757/Grogan-Networking-Tracker](https://github.com/ethangrogan757/Grogan-Networking-Tracker)

- **Frontend**: React + Vite (TypeScript)
- **Backend**: Node, deployed as Vercel serverless functions
- **Database**: Neon Postgres, with Row Level Security as the authorization boundary
- **Auth**: Neon Managed Better Auth (email + password)
- **Data access**: the Neon Data API, via `@neondatabase/neon-js`
- **Deployment**: a single Vercel project
```

## Assessment

_To fill in: does each claim follow from the cited passage? Is retrieval correct?_
