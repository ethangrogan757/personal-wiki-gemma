---
type: concept
description: "A Node backend is used to perform trusted, non-bypassable validation steps before forwarding requests to the Data API."
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
# Node Backend Architecture

<!-- wiki:begin src-networking-tracker -->
## From Networking Tracker

Part of the [[Networking Tracker]] project.

A Node backend is implemented to provide a trusted, non-bypassable validation step for requests before they are forwarded to the Data API. This backend checks for the presence of a bearer token and validates the request body against Zod schemas.

### Key details

- The Node backend checks if a bearer token is present in the request.
- It validates the request body using `api/_lib/validate.ts`.
- The backend forwards the caller's own Better Auth JWT to the Neon Data API using the `dataApi.getToken` function.
- The backend never holds an elevated/service-role credential and only forwards the caller's JWT, ensuring a compromised backend cannot do more than a compromised frontend.
- The backend uses the `createClient` function with an 'external auth provider' form to build a per-request client from the frontend's JWT.

### Sources

- [[Networking Tracker README#Architecture]] (lines 17–37)

### Related notes

- [[Networking Tracker]]: This project utilizes the Node backend to perform trusted, non-bypassable validation steps before forwarding requests to the Data API.
- [[Row Level Security]]: Row Level Security is the final authorization boundary that restricts which rows a statement can touch, complementing the backend's validation.
<!-- wiki:end src-networking-tracker -->
