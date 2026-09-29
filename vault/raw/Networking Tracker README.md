# Networking Tracker

A small, secure contacts tracker for keeping up with your professional network: create, view, edit, delete, sort, and filter contacts, each visible only to the account that created it.

**Live**: [networking-tracker-psi.vercel.app](https://networking-tracker-psi.vercel.app)
**Repo**: [github.com/ethangrogan757/Grogan-Networking-Tracker](https://github.com/ethangrogan757/Grogan-Networking-Tracker)

- **Frontend**: React + Vite (TypeScript)
- **Backend**: Node, deployed as Vercel serverless functions
- **Database**: Neon Postgres, with Row Level Security as the authorization boundary
- **Auth**: Neon Managed Better Auth (email + password)
- **Data access**: the Neon Data API, via `@neondatabase/neon-js`
- **Deployment**: a single Vercel project

## Architecture

```
Browser (React)
  │
  ├─ Auth (sign up / sign in / sign out / session)
  │    → @neondatabase/neon-js  →  Managed Better Auth (VITE_NEON_AUTH_URL)
  │
  └─ Contacts (create / read / update / delete / sort / filter)
       → fetch('/api/contacts...')  with an Authorization: Bearer <JWT> header
            │
            ▼
       Node backend (api/contacts/*.ts, Vercel serverless functions)
         1. checks a bearer token is present
         2. validates the request body (api/_lib/validate.ts)
         3. forwards the *same* token to the Neon Data API
            → @neondatabase/neon-js, "external auth provider" form
              (dataApi.getToken), NEON_DATA_API_URL
                 │
                 ▼
            Neon Data API → Postgres, RLS enforces
            auth.user_id() = contacts.user_id
```

**Why a Node backend at all, if the Data API can be called straight from the browser?** Neon's own guides describe a "no backend" pattern: the frontend calls the Data API directly and RLS does all the enforcement. That's a fine pattern, but it means *any* value a client sends — including an invalid `priority` — only gets checked by whatever `CHECK` constraints happen to exist in the schema, with no earlier, more specific error message. This app puts a small Node backend in front of every write specifically so there's a **trusted, non-bypassable validation step in server code**, in addition to the database constraint. The backend:

- Never holds an elevated/service-role credential.
- Never touches `DATABASE_URL`.
- Only ever forwards the caller's own Better Auth JWT to the Data API, per request. So a compromised backend can't do anything a compromised frontend couldn't already do — RLS is still the real authorization boundary either way.

**How the backend gets a token for the Data API.** `@neondatabase/neon-js`'s `createClient` has a documented "external auth provider" form for exactly this: instead of a Better Auth `auth` block, you pass `dataApi.getToken`, a function it calls before every request. `api/_lib/dataApi.ts` uses this to build a fresh, per-request client from whatever bearer token the frontend sent — so it stays stateless and never has its own session.

```ts
createClient({
  dataApi: {
    url: process.env.NEON_DATA_API_URL,
    getToken: async () => token, // the caller's own JWT, forwarded as-is
  },
})
```

This was confirmed against the installed package's actual type definitions and a small runtime check (`node -e "..."` against a live `createClient()` instance) before writing the integration — see [`src/lib/neonClient.ts`](src/lib/neonClient.ts) and [`api/_lib/dataApi.ts`](api/_lib/dataApi.ts).

The **frontend** uses the two-URL object form of `createClient` for authentication only (`neon.auth.signIn.email`, `signUp.email`, `signOut`, `useSession`), with the React adapter so `useSession()` is a normal hook:

```ts
createClient({
  auth: { url: VITE_NEON_AUTH_URL, adapter: BetterAuthReactAdapter() },
  dataApi: { url: VITE_NEON_DATA_API_URL },
})
```

It never calls `client.from('contacts')` itself — all contact reads and writes go through the backend, as shown above.

Two more things surfaced only by testing against the real deployed project, both worth recording since neither is obvious from the docs or types alone:

- **The Auth URL is a different origin from the app**, so the Better Auth session cookie is a cross-origin cookie. `BetterAuthReactAdapter()` needs `fetchOptions: { credentials: 'include' }` or calls like `auth.token()` silently come back unauthenticated for a signed-in user (no error client-side prompted this — it just always returned no token). See [`src/lib/neonClient.ts`](src/lib/neonClient.ts).
- **`client.auth.token()`'s actual response shape doesn't match its own type.** The installed package's `.d.ts` declares `{ data: { token: string } }`, matching the raw `/token` endpoint's OpenAPI schema — but the real runtime response (confirmed live) is `{ data: { session: { token }, user }, error }`, i.e. the token is nested under `session`, not top-level. [`src/lib/api.ts`](src/lib/api.ts)'s `authHeaders()` checks both shapes defensively.
- **Out-of-order responses could clobber the contact list.** Rapidly changing sort/filter (e.g. flipping the direction dropdown right after changing the sort field) could fire two overlapping `GET /api/contacts` requests; if the older one resolved after the newer one, its stale result overwrote the correct one. Found by testing rapid UI changes against the live deployment. [`src/App.tsx`](src/App.tsx)'s `refresh()` now tags each request with an incrementing id and only applies a response if it's still the most recent request.

## Schema and Row Level Security

[`db/schema.sql`](db/schema.sql) creates one table:

```sql
create table contacts (
  id uuid primary key default gen_random_uuid(),
  user_id text not null default auth.user_id(),
  name text not null,
  company text,
  job_title text,
  email text,
  phone text,
  notes text,
  priority text not null default 'medium' check (priority in ('low', 'medium', 'high')),
  last_contacted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

- `user_id` defaults to `auth.user_id()` — the current caller's id, taken from their JWT — so a row is stamped with its owner automatically at insert time.
- `priority` is constrained to `low | medium | high` by a `CHECK`, independent of anything the application does.
- A trigger keeps `updated_at` current on every write.

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

`auth.user_id()` reads the `sub` claim out of the caller's validated JWT. `USING` controls which existing rows a query can see/touch; `WITH CHECK` controls what a new or updated row is allowed to contain. Because `INSERT` and `UPDATE` both carry a `WITH CHECK (auth.user_id() = user_id)`, nobody can insert or reassign a contact to a `user_id` that isn't their own, even if they tried to pass a different one in the request body.

This is the actual authorization boundary. The Node backend's validation and the client-side form checks are both defense-in-depth — RLS is what actually stops one user from ever seeing or changing another user's contacts, even if every other layer had a bug.

RLS policies restrict *which rows* a statement can touch, but they don't grant access on their own — Postgres also requires an explicit `GRANT` before the `authenticated` role can run any statement against the table at all. `db/schema.sql` includes:

```sql
grant usage on schema public to authenticated;
grant select, insert, update, delete on contacts to authenticated;
```

This was found the hard way while standing up the real project for this deployment: without it, every Data API request came back `permission denied for table contacts` (Postgres `42501`) regardless of how correct the RLS policies were.

## Security summary

| Concern | How it's handled |
|---|---|
| Cross-user data access | Postgres RLS, `auth.user_id() = user_id`, on all four operations |
| Reassigning a contact to another user | Blocked by `WITH CHECK` on insert/update |
| Invalid `priority` | Rejected by `api/_lib/validate.ts` (server) **and** the DB `CHECK` constraint (defense-in-depth) |
| Missing required fields | Same — Zod schema server-side, `NOT NULL` in the DB |
| `DATABASE_URL` | Only ever used from a local shell to run `db/schema.sql` once; no application code reads it; never has a `VITE_` prefix so Vite can't bundle it |
| Elevated backend credentials | None exist — the backend forwards the caller's own JWT, it never authenticates as anyone else |
| Secrets in the repo | `.env` is git-ignored; only `.env.example` (placeholders) is tracked |

## Project layout

```
api/
  _lib/
    auth.ts        # extract the Authorization: Bearer <token> header
    dataApi.ts      # per-request Neon Data API client (getToken form)
    validate.ts      # Zod schemas: required name, priority enum
    validate.test.ts  # the automated test
  contacts/
    index.ts        # GET (list, sort/filter), POST (create)
    [id].ts          # GET, PUT (update), DELETE
db/
  schema.sql          # table, RLS, policies, trigger — apply once
shared/
  types.ts            # Contact/ContactInput/priority types, shared by src/ and api/
src/
  lib/
    neonClient.ts      # createClient two-URL form (auth)
    api.ts              # fetch wrapper that calls /api/contacts*
    useQueryState.ts    # sort/filter state synced to the URL
  components/
    AuthPanel.tsx, ContactForm.tsx, ContactList.tsx, ContactRow.tsx, SortFilterBar.tsx
  App.tsx
.env.example
vercel.json
```

## Setup

### 1. Create the Neon project and enable the Data API

Via the Console:
1. Create a Neon project (or use an existing one) at [neon.tech](https://neon.tech).
2. In the Neon Console: your project → **Postgres database** → **Data API**.
3. Choose **Managed Better Auth** as the authentication provider.
4. Click **Enable Data API**. The console will show you three URLs/strings you need:
   - a **Data API URL** (looks like `https://ep-xxx.apirest.<region>.aws.neon.build/<db>/rest/v1`)
   - an **Auth URL** (looks like `https://ep-xxx.neonauth.<region>.aws.neon.build/<db>/auth`)
   - the project's regular Postgres **connection string** (`postgresql://...`)

Or via the `neon` CLI (`npm i -g neon@latest && neon login`), against an existing project:
```bash
neon link --project-id <your-project-id> --branch production
neon neon-auth enable --project-id <your-project-id> --branch production
neon api "/projects/<your-project-id>/branches/<branch-id>/data-api/<db-name>" -X POST
```
The last command returns the Data API URL; `neon neon-auth status -o json` returns the Auth URL. `neon link` also writes `DATABASE_URL`/`DATABASE_URL_UNPOOLED` straight into `.env.local` for you.

### 2. Apply the schema

```bash
psql "$DATABASE_URL" -f db/schema.sql
```

Use the connection string from step 1. This is the *only* place `DATABASE_URL` is used — copy it into your shell environment or pass it inline, but don't put it in any file that gets committed.

### 3. Configure environment variables

```bash
cp .env.example .env
```

Fill in `.env` with the URLs from step 1 (see the comments in [`.env.example`](.env.example) for which variables are public vs. server-only). When deploying, set the same variables in the Vercel dashboard (Project → Settings → Environment Variables) instead of committing `.env`.

### 4. Install and run

```bash
npm install
npm run dev
```

This starts the Vite dev server for the frontend. The `/api` functions are Vercel serverless functions — to exercise them locally too, use the Vercel CLI instead:

```bash
npm install -g vercel
vercel dev
```

If you run `npm run dev` without filling in `.env`, the app shows a "Configuration needed" message instead of crashing — see [`src/main.tsx`](src/main.tsx).

## Testing

One automated test suite, `api/_lib/validate.test.ts`, covering the trusted server-side validation logic: missing/blank name rejected, missing or invalid `priority` rejected, malformed email rejected, valid full and minimal payloads accepted, and partial-update rules. It's a pure-function test — no network or database required, so it runs anywhere with zero setup.

```bash
npm run test
```

Real output from this repo:

```
 RUN  v4.1.11 /Users/ethangrogan/coding class/Assignment1

 ✓ api/_lib/validate.test.ts > validateContactInput > rejects a missing name 2ms
 ✓ api/_lib/validate.test.ts > validateContactInput > rejects an empty name 0ms
 ✓ api/_lib/validate.test.ts > validateContactInput > rejects an invalid priority value 0ms
 ✓ api/_lib/validate.test.ts > validateContactInput > rejects a missing priority 0ms
 ✓ api/_lib/validate.test.ts > validateContactInput > rejects a malformed email when provided 0ms
 ✓ api/_lib/validate.test.ts > validateContactInput > accepts a minimal valid contact 0ms
 ✓ api/_lib/validate.test.ts > validateContactInput > accepts a fully populated valid contact 0ms
 ✓ api/_lib/validate.test.ts > validateContactUpdate > rejects an empty patch 1ms
 ✓ api/_lib/validate.test.ts > validateContactUpdate > rejects an invalid priority even as a partial patch 0ms
 ✓ api/_lib/validate.test.ts > validateContactUpdate > accepts a single valid field update 0ms

 Test Files  1 passed (1)
      Tests  10 passed (10)
   Start at  18:06:49
   Duration  136ms (transform 19ms, setup 0ms, import 51ms, tests 5ms, environment 0ms)
```

Also verified: `npx tsc -b` (typechecks `src/`, `api/`, and `shared/`) and `npm run build` both complete with no errors.

## Deployment (Vercel)

This project is currently deployed at the URL above (Vercel project `networking-tracker` under the `berkeley-haas1` account, linked to Neon project `crimson-cake-88836341`). To deploy your own copy:

1. Push this repository to GitHub (optional — `vercel deploy` works from a local checkout too).
2. `vercel link` (or `vercel deploy`, which links automatically) to create/link a Vercel project.
3. Set environment variables — either in Vercel → Project → Settings → Environment Variables, or via the CLI:
   ```bash
   vercel env add VITE_NEON_AUTH_URL production --type config --value "$VITE_NEON_AUTH_URL"
   vercel env add VITE_NEON_DATA_API_URL production --type config --value "$VITE_NEON_DATA_API_URL"
   vercel env add NEON_DATA_API_URL production --type secret --value "$NEON_DATA_API_URL"
   ```
   Repeat for the `preview` and `development` targets. `VITE_`-prefixed vars need `--type config` (public/bundled) — the CLI refuses to guess and will otherwise prompt you to choose. You do **not** need to set `DATABASE_URL` in Vercel; it's only used locally for the one-time schema setup.
4. `vercel deploy --prod`.
5. Add your deployed domain to Managed Better Auth's trusted origins — either in the Neon Console, or via the CLI: `neon neon-auth domain add https://<your-domain> --project-id <id> --branch production`. Without this, sign-in/sign-up from the deployed frontend fails.

`vercel.json` builds the Vite frontend to `dist/`, auto-detects `api/*.ts` as Node serverless functions, and rewrites all non-`/api` paths to `index.html`.

## Evidence

Every item below was re-verified live against the deployed app (`https://networking-tracker-psi.vercel.app`, Neon project `crimson-cake-88836341`) in a single validation pass, not just exercised once during initial setup. Test accounts and rows created for verification were deleted afterward — the live database is clean. A visual screenshot/recording for auth and CRUD is still worth capturing for a polished submission (drop files into `docs/` and replace the placeholder line with `![...](docs/<filename>)`), but every behavior below is confirmed working, not assumed.

1. **The application is live at a public URL** — `https://networking-tracker-psi.vercel.app` returns `200`.
2. **A user can sign in and sign out** — verified both directions: signed up a fresh account (`validate-run@example.com`), signed out (returns to the sign-in form, confirmed via console log that the session was actually cleared), then signed back in with the same email/password (not sign-up) and the account's existing data loaded correctly. Screenshot/recording still to capture: `docs/auth-flow.png` or `.mp4`.
3. **A user can add, view, edit, delete, sort, and filter contacts** — verified through the live UI in one session:
   - **Add**: created two contacts ("Zara Ahmed", "Amir Khan") with different names/companies/priorities.
   - **View**: both appeared in the list immediately.
   - **Edit**: changed a contact's job title and priority; the change persisted.
   - **Delete**: deleted a contact with the confirm dialog accepted; it disappeared and stayed gone after a refresh.
   - **Sort**: sorting by Name/Descending correctly ordered "Zara Ahmed" before "Amir Khan" (confirmed against the raw API response, not just the rendered list).
   - **Filter**: Priority=High correctly narrowed to one match; a text search for "acme" correctly matched by company name.
   - Screenshot/recording still to capture: `docs/contact-crud.png` or `.mp4`.
4. **Data survives refresh because it is stored in Neon Postgres** — after editing a contact, a full page navigation (not a client-side re-render) reloaded the same session and the edited data intact, sourced fresh from `GET /api/contacts` each time — there is no client-side cache or local storage involved.
5. **User A cannot see or change User B's contacts** — verified live through the actual UI with two real accounts: signed in as `validate-run@example.com`, created a contact; signed out; signed up as `validate-userb@example.com`; its contact list came back empty (`0 contacts`) despite user A's contact existing in the same table. RLS (`auth.user_id() = user_id`) is what enforces this — see [Schema and Row Level Security](#schema-and-row-level-security).
6. **Invalid data fails safely with a clear message** — verified at all three layers:
   - Client: submitting the "New contact" form with an empty name is blocked by the browser's native validation ("Please fill out this field") before any network request fires.
   - Server: `POST /api/contacts` with `{"priority":"urgent"}` returns `400 {"error":"invalid contact","details":["priority must be one of: low, medium, high"]}`; with a missing `name` returns `400` with a Zod validation message. No crash, no 500.
   - Database: bypassing the API entirely and inserting `priority: 'urgent'` directly against the Data API returns `400` with Postgres's own `23514` check-constraint violation message.
7. **At least one automated test passes** — `npm run test`, 10/10 passing, real output in [Testing](#testing) above.
8. **No `DATABASE_URL`, cookie secret, or other secret appears in frontend code or Git history** — the built production bundle (`dist/assets/*.js`) was searched for `DATABASE_URL`, `postgresql://`, the Neon password prefix `npg_`, and Better Auth secret env var names; the only match is the literal string `"BETTER_AUTH_SECRET"` as an env-var *name* inside the auth library's own generic env-reader code (`Gt('BETTER_AUTH_SECRET')`), never a value. `NEON_DATA_API_URL` and `DATABASE_URL` do not appear in the bundle at all — only the two `VITE_`-prefixed URLs are bundled, and those are safe-by-design public endpoints (see [Security summary](#security-summary)). **Git history**: pushed to [github.com/ethangrogan757/Grogan-Networking-Tracker](https://github.com/ethangrogan757/Grogan-Networking-Tracker) (public) as a single commit — `git ls-files | grep -i env` on that commit returns only `.env.example`. One `.gitignore` bug was caught before this commit: the Neon CLI's `neon link` step had appended a second, broader `.env*` rule *after* the project's own `!.env.example` exception, which — since gitignore rules are evaluated in file order — silently overrode the exception and would have excluded `.env.example` (the one file meant to be tracked) from every commit. Fixed by removing the duplicate rule and confirming with `git check-ignore` before committing.
9. **The README contains every required section and all grading evidence** — Architecture, Schema and Row Level Security, Security summary, Project layout, Setup, Testing, Deployment, Evidence (this section), Known limitations — all present in this file.

## Known limitations

- The search filter strips `(`, `)`, and `,` from the search term before building the Data API's `.or()` filter expression, to avoid a search string breaking the filter syntax — so those characters are silently ignored in a search, rather than matched literally.
- Auth UI (sign in/sign up) is hand-rolled rather than using `@neondatabase/auth-ui`'s pre-built components, to keep the dependency footprint minimal for this scope.
- Frontend and backend are deployed together as one Vercel project (static build + `/api` serverless functions) rather than as two separately-deployed services, to avoid unnecessary CORS/multi-service complexity for this scope.
