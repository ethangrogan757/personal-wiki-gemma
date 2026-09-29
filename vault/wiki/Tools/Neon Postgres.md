---
type: tool
description: "Neon Postgres is used as the database, utilizing Row Level Security for authorization boundaries."
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
# Neon Postgres

<!-- wiki:begin src-networking-tracker -->
## From Networking Tracker

Part of the [[Networking Tracker]] project.

Neon Postgres is used as the database for the Networking Tracker, utilizing Row Level Security (RLS) to enforce authorization boundaries. The schema includes specific policies for select, insert, update, and delete operations based on the authenticated user's ID.

### Key details

- The `contacts` table schema includes a `user_id` that defaults to `auth.user_id()`, ensuring each row is stamped with its owner automatically at insert time.
- The `priority` column is constrained by a `CHECK` constraint to only allow values of 'low', 'medium', or 'high'.
- Row Level Security policies are defined for all four operations (`select`, `insert`, `update`, `delete`) to restrict access to rows where `auth.user_id() = user_id`.
- The database requires explicit grants for the `authenticated` role to run statements against the table, including `grant usage on schema public to authenticated` and specific `select, insert, update, delete` grants on `contacts`.
- RLS policies are the actual authorization boundary, while the Node backend's validation and client-side checks provide defense-in-depth.

### Sources

- [[Networking Tracker README#Schema and Row Level Security]] (lines 77–98)

### Related notes

- [[Row Level Security]]: RLS policies are the actual authorization boundary enforced in the database.
- [[Networking Tracker]]: This note describes how Neon Postgres is used within the Networking Tracker application.
<!-- wiki:end src-networking-tracker -->
