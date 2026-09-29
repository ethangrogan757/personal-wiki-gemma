# Retrieval check: 01-baseline

Run 2026-09-29 10:42. BM25 over vault/raw, top 5, no model involved.

## Test 1: FAIL

**Question:** What learning rate did I use for the Pac-Man DQN?

**Query terms:** `learn rate use pac man dqn`

**Expected:** Pac-Man DQN README.md#L26 missing

| Rank | Score | Passage | Section | Matched terms |
|---|---|---|---|---|
| 1 | 12.99 | `Pac-Man DQN README.md#L3-L8` | Class 3: Training a DQN Agent to Play Ms. Pac-Man | learn, pac, man, dqn |
| 2 | 9.83 | `Pac-Man DQN README.md#L58-L67` | What the agent observes, does, and is rewarded for | learn, pac, man |
| 3 | 9.29 | `Pac-Man DQN README.md#L32-L40` | My three hyperparameters | learn, pac, man, dqn |
| 4 | 7.99 | `Pac-Man DQN README.md#L12-L17` | Overview and how to run | learn, use, dqn |
| 5 | 6.83 | `Custom LLM README.md#L165-L171` | How this model actually learns — traced through one real word | learn, rate |

## Test 2: PASS

**Question:** How much better did my Pac-Man agent get after training?

**Query terms:** `much better pac man agent train`

**Expected:** Pac-Man DQN README.md#L32 at rank 3

| Rank | Score | Passage | Section | Matched terms |
|---|---|---|---|---|
| 1 | 12.72 | `Pac-Man DQN README.md#L58-L67` | What the agent observes, does, and is rewarded for | pac, man, agent, train |
| 2 | 11.67 | `Pac-Man DQN README.md#L3-L8` | Class 3: Training a DQN Agent to Play Ms. Pac-Man | pac, man, agent, train |
| 3 | 9.51 | `Pac-Man DQN README.md#L32-L40` | My three hyperparameters | pac, man, agent, train |
| 4 | 4.84 | `Custom LLM README.md#L215-L223` | One limitation, explained, and what I tried next | much, train |
| 5 | 4.50 | `Custom LLM README.md#L302-L307` | Chat interface | man |

## Test 3: PASS

**Question:** What stops one user from seeing another user's contacts in my networking tracker?

**Query terms:** `stop one user seeing another user s contact network tracker`

**Expected:** Networking Tracker README.md#L118 at rank 1, Networking Tracker README.md#L100 at rank 5

| Rank | Score | Passage | Section | Matched terms |
|---|---|---|---|---|
| 1 | 19.53 | `Networking Tracker README.md#L118-L120` | Schema and Row Level Security | stop, one, user, seeing, another, s, contact |
| 2 | 11.13 | `Networking Tracker README.md#L278-L283` | Evidence | one, user, s, contact, network, tracker |
| 3 | 11.02 | `Networking Tracker README.md#L3-L13` | Networking Tracker | contact, network, tracker |
| 4 | 10.04 | `Networking Tracker README.md#L289-L291` | Evidence | user, s, contact, network |
| 5 | 9.23 | `Networking Tracker README.md#L100-L116` | Schema and Row Level Security | one, user, contact |

## Test 4: n/a (unanswerable)

**Question:** How much does it cost per month to host my Networking Tracker?

**Query terms:** `much cost per month host network tracker`

**Expected:** no passage is expected to contain the answer

| Rank | Score | Passage | Section | Matched terms |
|---|---|---|---|---|
| 1 | 8.71 | `Networking Tracker README.md#L3-L13` | Networking Tracker | network, tracker |
| 2 | 6.44 | `Networking Tracker README.md#L258-L258` | Deployment (Vercel) | network, tracker |
| 3 | 4.82 | `Networking Tracker README.md#L276-L276` | Evidence | network, tracker |
| 4 | 4.76 | `Networking Tracker README.md#L295-L295` | Evidence | network, tracker |
| 5 | 4.11 | `Custom LLM README.md#L156-L163` | How this model actually learns — traced through one real word | per, network |
