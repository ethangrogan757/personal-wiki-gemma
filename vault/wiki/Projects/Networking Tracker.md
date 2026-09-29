---
type: project
description: "A small, secure contacts tracker for keeping up with your professional network: create, view, edit, delete, sort, and filter contacts, each visible only to the account that created it."
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
# Networking Tracker

<!-- wiki:begin src-networking-tracker -->
The Networking Tracker is a small, secure contacts tracker built with React and Node.js, allowing users to create, view, edit, delete, sort, and filter contacts, with access restricted to the account that created them. The project utilized a Node backend to provide a trusted validation step before interacting with the database, and implemented Row Level Security (RLS) in Postgres as the primary authorization boundary.

## Key details

- Frontend is built with React + Vite (TypeScript), and the backend uses Node deployed as Vercel serverless functions.
- The architecture involves the frontend calling a Node backend, which in turn forwards the caller's JWT to the Neon Data API for data access.
- Row Level Security (RLS) policies are defined in `db/schema.sql` to enforce that users can only select, insert, update, or delete rows where `auth.user_id() = user_id`.
- The Node backend performs validation using Zod schemas (`api/_lib/validate.ts`) and the database enforces constraints on fields like `priority`.
- Security measures include ensuring the backend never holds elevated credentials and that secrets are not present in the frontend bundle.

## Topics in this project

- [[Row Level Security]]: Postgres Row Level Security enforces cross-user data access control for all CRUD operations.
- [[Node Backend Architecture]]: A Node backend is used to perform trusted, non-bypassable validation steps before forwarding requests to the Data API.
- [[Neon Postgres]]: Neon Postgres is used as the database, utilizing Row Level Security for authorization boundaries.
- [[Vercel Deployment]]: The project is deployed as a single Vercel project using static build and serverless functions.

## Sources

- [[Networking Tracker README]] (introduction) (lines 3–13)
- [[Networking Tracker README#Architecture]] (lines 17–37)
- [[Networking Tracker README#Security summary]] (lines 133–141)

## Related notes

- [[Row Level Security]]: RLS policies are the actual authorization boundary that restricts which rows a statement can touch.
- [[Node Backend Architecture]]: The project uses a Node backend specifically to provide a trusted, non-bypassable validation step in server code.
- [[Neon Postgres]]: The project uses Neon Postgres for the database, which enforces data access rules via RLS.
<!-- wiki:end src-networking-tracker -->
