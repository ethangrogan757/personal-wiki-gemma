---
type: concept
description: "Postgres Row Level Security enforces cross-user data access control for all CRUD operations."
sources:
  - "[[Networking Tracker README]]"
source_ids:
  - src-networking-tracker
original_paths:
  - "Assignment1/README.md"
generated_by: gemma4:e2b-it-qat (local, Ollama)
reviewed: false
updated: 2026-09-29
---
# Row Level Security

<!-- wiki:begin src-networking-tracker -->
## From Networking Tracker

Part of the [[Networking Tracker]] project.

Postgres Row Level Security (RLS) is used to enforce cross-user data access control for all CRUD operations on the contacts table. The project implements policies to ensure that users can only select, insert, update, or delete rows where the `user_id` matches their own, acting as the actual authorization boundary.

### Key details

- RLS policies are defined for the `contacts` table to restrict access based on the authenticated user's ID.
- Policies are created for `select`, `insert`, `update`, and `delete` operations.
- The policies use `auth.user_id() = user_id` for selection and `auth.user_id() = user_id` with a `WITH CHECK` clause for insert and update.
- The `auth.user_id()` function reads the `sub` claim from the caller's validated JWT.
- RLS policies only restrict which rows a statement can touch; they don't grant access on their own. Postgres also needs an explicit `GRANT` (`grant select, insert, update, delete on contacts to authenticated`) before the `authenticated` role can run any statement on the table at all.

### Sources

- [[Networking Tracker README#Schema and Row Level Security]] (lines 100–127)

### Related notes

- [[Networking Tracker]]: This project uses Postgres RLS to enforce cross-user data access control for all CRUD operations.
- [[Node Backend Architecture]]: The architecture details how the Node backend forwards the caller's JWT to the Data API, which then relies on RLS for final authorization.
- [[Neon Postgres]]: The database is a Neon Postgres instance where RLS policies are applied to the contacts table.
<!-- wiki:end src-networking-tracker -->
