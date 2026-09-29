# Ask-mode test questions

Written before building retrieval. This file is the answer key and lives **outside** `vault/`, so the harness can never retrieve it.

All four tests run in `ask` mode, independent of chat history, with local Gemma (`gemma4:e2b-it-qat`) and the internet disconnected.

---

## Test 1: direct question, one source

**Question:** What learning rate did I use for the Pac-Man DQN?

**Expected source:** `vault/raw/Pac-Man DQN README.md`, section "My three hyperparameters"

**Expected passage:**
> | **Learning rate** | `0.0001` | The notebook's reference Adam learning rate, tuned to stay stable with the small (5,000-transition) replay buffer and batch size 32 used in this classroom-scale setup. …

**Expected answer:** 0.0001 (Adam), with a citation to the Pac-Man DQN source.

**What this tests:** the question uses the same words as the source, so keyword retrieval should find it easily.

---

## Test 2: reworded question

**Question:** How much better did my Pac-Man agent get after training?

**Expected source:** `vault/raw/Pac-Man DQN README.md`, section "My three hyperparameters" ("What I observed")

**Expected passage:**
> **What I observed:** mean evaluation score rose from 492.0 (untrained) to 692.0 (trained) — a ~41% improvement — but the gain was **not uniform across seeds** (4 of 5 seeds improved; one got worse than baseline).

**Expected answer:** The mean evaluation score went from 492.0 to 692.0 (about 41%), but not every seed improved. Cited to the Pac-Man DQN source.

*Note added after testing:* the source contradicts itself here. Its text says "4 of 5 seeds improved", but its before/after table (lines 104–111) shows only 3 of 5 improved (seeds 404 and 505 got worse). The source file is left unchanged as evidence; the expected answer above no longer repeats the "4 of 5" count.

**What this tests:** the question avoids the source's wording ("mean evaluation score", "improvement"). Only "Pac-Man" and "training" overlap, so keyword retrieval could miss the exact passage. If it does, that's a real finding to document.

---

## Test 3: question with known supporting evidence

**Question:** What stops one user from seeing another user's contacts in my networking tracker?

**Expected source:** `vault/raw/Networking Tracker README.md`, section "Schema and Row Level Security"

**Expected passages:**
> Row Level Security is enabled, with one ownership policy per operation:
> … `using (auth.user_id() = user_id);`

> This is the actual authorization boundary. The Node backend's validation and the client-side form checks are both defense-in-depth — RLS is what actually stops one user from ever seeing or changing another user's contacts, even if every other layer had a bug.

**Expected answer:** Postgres Row Level Security: each policy checks `auth.user_id() = user_id` (the user id from the caller's JWT), so users only see and change their own rows. Backend and form validation are only defense-in-depth. Cited to the Networking Tracker source.

**Secondary supporting evidence (same source, testing checklist item 5):** a live test where User B's contact list came back empty despite User A's contact existing in the same table.

---

## Test 4: unanswerable question

**Question:** How much does it cost per month to host my Networking Tracker?

**Expected source:** none. No source mentions hosting cost, pricing or a monthly bill for Vercel or Neon.

**Expected behavior:** an explicit statement that the wiki doesn't contain enough evidence to answer. No guessed dollar amount, and no general-knowledge answer about Vercel or Neon free tiers.

**Likely distractors:** "price" appears only in an unrelated training-corpus sentence in the Custom LLM README ("compared the offering after checking the price ."), and "Vercel" appears in the Networking Tracker architecture/deployment text. Retrieval may return these, but the model must not treat them as an answer.

**Replaced question (kept for honesty):** the first draft of Test 4 was "What GPU did I use to train the custom LLM in Colab?". It was dropped before any testing because the Custom LLM README *does* answer it (trained "on Colab's free CPU tier", "CPU-only (Colab)"), so it wasn't truly unanswerable.
