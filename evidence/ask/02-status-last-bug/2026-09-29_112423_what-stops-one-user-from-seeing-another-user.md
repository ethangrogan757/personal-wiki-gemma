# Ask evidence card

- **Question:** What stops one user from seeing another user's contacts in my networking tracker?
- **Mode:** ask (standalone; no chat history, no persona)
- **Execution:** local, `gemma4:e2b-it-qat` via Ollama at http://localhost:11434
- **Run at:** 2026-09-29 11:24:23
- **Response time:** 2.7s (1406 prompt tokens, 74 output tokens)

## Answer

**Status:** `insufficient_evidence`

Row Level Security (RLS) is what stops one user from seeing another user's contacts [4]. This is enforced by the policy `contacts_select` which uses the condition `auth.user_id() = user_id` [2].

## Citations

- [4] `vault/raw/Networking Tracker README.md` lines 289–291 (Evidence)
- [2] `vault/raw/Networking Tracker README.md` lines 100–116 (Schema and Row Level Security)

**Citation check warnings:**
- status says insufficient evidence, but the answer cites passages; check it by hand

## Retrieved passages (exactly as sent to the model)

### [1] `vault/raw/Networking Tracker README.md` lines 118–120
Section: Schema and Row Level Security · BM25 score 20.05 · matched: stop, one, user, seeing, another, contact, network, tracker

```text
`auth.user_id()` reads the `sub` claim out of the caller's validated JWT. `USING` controls which existing rows a query can see/touch; `WITH CHECK` controls what a new or updated row is allowed to contain. Because `INSERT` and `UPDATE` both carry a `WITH CHECK (auth.user_id() = user_id)`, nobody can insert or reassign a contact to a `user_id` that isn't their own, even if they tried to pass a different one in the request body.

This is the actual authorization boundary. The Node backend's validation and the client-side form checks are both defense-in-depth — RLS is what actually stops one user from ever seeing or changing another user's contacts, even if every other layer had a bug.
```

### [2] `vault/raw/Networking Tracker README.md` lines 100–116
Section: Schema and Row Level Security · BM25 score 10.83 · matched: one, user, contact, network, tracker

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

### [3] `vault/raw/Networking Tracker README.md` lines 133–141
Section: Security summary · BM25 score 9.66 · matched: user, another, contact, network, tracker

```text
| Concern | How it's handled |
|---|---|
| Cross-user data access | Postgres RLS, `auth.user_id() = user_id`, on all four operations |
| Reassigning a contact to another user | Blocked by `WITH CHECK` on insert/update |
| Invalid `priority` | Rejected by `api/_lib/validate.ts` (server) **and** the DB `CHECK` constraint (defense-in-depth) |
| Missing required fields | Same — Zod schema server-side, `NOT NULL` in the DB |
| `DATABASE_URL` | Only ever used from a local shell to run `db/schema.sql` once; no application code reads it; never has a `VITE_` prefix so Vite can't bundle it |
| Elevated backend credentials | None exist — the backend forwards the caller's own JWT, it never authenticates as anyone else |
| Secrets in the repo | `.env` is git-ignored; only `.env.example` (placeholders) is tracked |
```

### [4] `vault/raw/Networking Tracker README.md` lines 289–291
Section: Evidence · BM25 score 9.14 · matched: user, contact, network, tracker

```text
5. **User A cannot see or change User B's contacts** — verified live through the actual UI with two real accounts: signed in as `validate-run@example.com`, created a contact; signed out; signed up as `validate-userb@example.com`; its contact list came back empty (`0 contacts`) despite user A's contact existing in the same table. RLS (`auth.user_id() = user_id`) is what enforces this — see [Schema and Row Level Security](#schema-and-row-level-security).
6. **Invalid data fails safely with a clear message** — verified at all three layers:
   - Client: submitting the "New contact" form with an empty name is blocked by the browser's native validation ("Please fill out this field") before any network request fires.
```

### [5] `vault/raw/Networking Tracker README.md` lines 278–283
Section: Evidence · BM25 score 8.45 · matched: one, user, contact, network, tracker

```text
1. **The application is live at a public URL** — `https://networking-tracker-psi.vercel.app` returns `200`.
2. **A user can sign in and sign out** — verified both directions: signed up a fresh account (`validate-run@example.com`), signed out (returns to the sign-in form, confirmed via console log that the session was actually cleared), then signed back in with the same email/password (not sign-up) and the account's existing data loaded correctly. Screenshot/recording still to capture: `docs/auth-flow.png` or `.mp4`.
3. **A user can add, view, edit, delete, sort, and filter contacts** — verified through the live UI in one session:
   - **Add**: created two contacts ("Zara Ahmed", "Amir Khan") with different names/companies/priorities.
   - **View**: both appeared in the list immediately.
   - **Edit**: changed a contact's job title and priority; the change persisted.
```

## Assessment

_To fill in: does each claim follow from the cited passage? Is retrieval correct?_
