---
type: tool
description: "The project is deployed as a single Vercel project using static build and serverless functions."
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
# Vercel Deployment

<!-- wiki:begin src-networking-tracker -->
## From Networking Tracker

Part of the [[Networking Tracker]] project.

The project is deployed as a single Vercel project, utilizing a static build for the frontend and Vercel serverless functions for the backend API. The deployment process involves pushing the repository, linking to a Vercel project, and configuring environment variables via the Vercel dashboard or CLI.

### Key details

- The project is deployed at the URL [https://networking-tracker-psi.vercel.app](https://networking-tracker-psi.vercel.app) under the Vercel project `networking-tracker`.
- Deployment involves pushing the repository to GitHub, linking to a Vercel project, and setting environment variables using the CLI commands like `vercel env add`.
- Environment variables prefixed with `VITE_` (e.g., `VITE_NEON_AUTH_URL`) need to be set with `--type config` when using the CLI.
- The `vercel.json` file builds the Vite frontend to `dist/` and auto-detects `api/*.ts` files as Node serverless functions.
- The deployment process requires adding the deployed domain to Managed Better Auth's trusted origins to allow sign-in/sign-up functionality.

### Sources

- [[Networking Tracker README]] (introduction) (lines 3–13)
- [[Networking Tracker README#Deployment (Vercel)]] (lines 260–270)

### Related notes

- [[Networking Tracker]]: This note describes the overall project which is currently deployed on Vercel.
- [[Node Backend Architecture]]: This note details how the Node backend is structured and deployed as Vercel serverless functions.
- [[Neon Postgres]]: This note explains the database used, which is connected to the Vercel deployment via environment variables.
<!-- wiki:end src-networking-tracker -->
