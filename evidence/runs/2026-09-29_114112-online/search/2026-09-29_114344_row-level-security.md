# Search evidence card

- **Query:** row level security
- **Mode:** search (BM25 keyword search over vault/raw; no model involved, no answer generated)
- **Run at:** 2026-09-29 11:43:44
- **Passages returned:** 3

## [1] `vault/raw/Networking Tracker README.md` lines 100–116
Section: Schema and Row Level Security · BM25 score 11.08 · matched: row, level, security

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

## [2] `vault/raw/Networking Tracker README.md` lines 296–296
Section: Evidence · BM25 score 10.11 · matched: row, level, security

```text
9. **The README contains every required section and all grading evidence** — Architecture, Schema and Row Level Security, Security summary, Project layout, Setup, Testing, Deployment, Evidence (this section), Known limitations — all present in this file.
```

## [3] `vault/raw/Networking Tracker README.md` lines 289–291
Section: Evidence · BM25 score 9.22 · matched: row, level, security

```text
5. **User A cannot see or change User B's contacts** — verified live through the actual UI with two real accounts: signed in as `validate-run@example.com`, created a contact; signed out; signed up as `validate-userb@example.com`; its contact list came back empty (`0 contacts`) despite user A's contact existing in the same table. RLS (`auth.user_id() = user_id`) is what enforces this — see [Schema and Row Level Security](#schema-and-row-level-security).
6. **Invalid data fails safely with a clear message** — verified at all three layers:
   - Client: submitting the "New contact" form with an empty name is blocked by the browser's native validation ("Please fill out this field") before any network request fires.
```
