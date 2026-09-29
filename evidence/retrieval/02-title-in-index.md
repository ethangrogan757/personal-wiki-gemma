# Retrieval check: 02-title-in-index

Run 2026-09-29 10:42. BM25 over vault/raw, top 5, no model involved.

## Test 1: PASS

**Question:** What learning rate did I use for the Pac-Man DQN?

**Query terms:** `learn rate use pac man dqn`

**Expected:** Pac-Man DQN README.md#L26 at rank 3

| Rank | Score | Passage | Section | Matched terms |
|---|---|---|---|---|
| 1 | 9.65 | `Pac-Man DQN README.md#L3-L8` | Class 3: Training a DQN Agent to Play Ms. Pac-Man | learn, pac, man, dqn |
| 2 | 9.37 | `Pac-Man DQN README.md#L12-L17` | Overview and how to run | learn, use, pac, man, dqn |
| 3 | 9.24 | `Pac-Man DQN README.md#L26-L30` | My three hyperparameters | learn, rate, pac, man, dqn |
| 4 | 8.85 | `Pac-Man DQN README.md#L134-L140` | Limitation and next experiment | learn, rate, pac, man, dqn |
| 5 | 7.81 | `Pac-Man DQN README.md#L32-L40` | My three hyperparameters | learn, pac, man, dqn |

## Test 2: PASS

**Question:** How much better did my Pac-Man agent get after training?

**Query terms:** `much better pac man agent train`

**Expected:** Pac-Man DQN README.md#L32 at rank 3

| Rank | Score | Passage | Section | Matched terms |
|---|---|---|---|---|
| 1 | 9.14 | `Pac-Man DQN README.md#L3-L8` | Class 3: Training a DQN Agent to Play Ms. Pac-Man | pac, man, agent, train |
| 2 | 8.87 | `Pac-Man DQN README.md#L58-L67` | What the agent observes, does, and is rewarded for | pac, man, agent, train |
| 3 | 8.08 | `Pac-Man DQN README.md#L32-L40` | My three hyperparameters | pac, man, agent, train |
| 4 | 7.52 | `Pac-Man DQN README.md#L101-L113` | Evidence > Before/after evaluation — all five scores | pac, man, agent, train |
| 5 | 7.06 | `Pac-Man DQN README.md#L157-L160` | Scope note | pac, man, agent, train |

## Test 3: PASS

**Question:** What stops one user from seeing another user's contacts in my networking tracker?

**Query terms:** `stop one user seeing another user contact network tracker`

**Expected:** Networking Tracker README.md#L118 at rank 1, Networking Tracker README.md#L100 at rank 2

| Rank | Score | Passage | Section | Matched terms |
|---|---|---|---|---|
| 1 | 20.05 | `Networking Tracker README.md#L118-L120` | Schema and Row Level Security | stop, one, user, seeing, another, contact, network, tracker |
| 2 | 10.83 | `Networking Tracker README.md#L100-L116` | Schema and Row Level Security | one, user, contact, network, tracker |
| 3 | 9.66 | `Networking Tracker README.md#L133-L141` | Security summary | user, another, contact, network, tracker |
| 4 | 9.14 | `Networking Tracker README.md#L289-L291` | Evidence | user, contact, network, tracker |
| 5 | 8.45 | `Networking Tracker README.md#L278-L283` | Evidence | one, user, contact, network, tracker |

## Test 4: n/a (unanswerable)

**Question:** How much does it cost per month to host my Networking Tracker?

**Query terms:** `much cost per month host network tracker`

**Expected:** no passage is expected to contain the answer

| Rank | Score | Passage | Section | Matched terms |
|---|---|---|---|---|
| 1 | 4.09 | `Networking Tracker README.md#L41-L45` | Architecture | per, network, tracker |
| 2 | 3.44 | `Custom LLM README.md#L215-L223` | One limitation, explained, and what I tried next | much |
| 3 | 3.42 | `Networking Tracker README.md#L100-L116` | Schema and Row Level Security | per, network, tracker |
| 4 | 3.33 | `Custom LLM README.md#L87-L95` | Prediction vs. what actually happened | much |
| 5 | 3.28 | `Networking Tracker README.md#L3-L13` | Networking Tracker | network, tracker |
