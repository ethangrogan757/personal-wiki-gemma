# Obsidian check

Vault opened in Obsidian 1.13.7 (macOS) with `vault/` as the vault root, not the whole project folder.

## Screenshots

| File | Shows |
|---|---|
| [01-open-note.png](screenshots/01-open-note.png) | `wiki/Concepts/Row Level Security.md` in reading view: heading matches filename (breadcrumb wiki / Concepts / Row Level Security), properties with the source link, original path, source id and generating model |
| [01b-open-note-sources.png](screenshots/01b-open-note-sources.png) | Same note scrolled down: Key details, **Sources** (link to the exact README section and line range) and **Related notes** with a reason for each link |
| [02-index.png](screenshots/02-index.png) | `index.md` grouped into Projects / Concepts / Tools with one-line descriptions, and the file panel expanded to show every note name |
| [03-graph.png](screenshots/03-graph.png) | Graph of the curated notes with readable labels |

## Settings used

- **Graph filter:** `path:wiki/` (hides `index.md` and the raw READMEs, so only curated notes show)
- **Attachments:** off · **Existing files only:** on
- **Color groups:** `path:wiki/Projects` (red), `path:wiki/Concepts` (tan), `path:wiki/Tools` (black)
- **Text fade threshold:** minimum, so every label shows
- **Show inline title:** off (`vault/.obsidian/appearance.json`). Otherwise Obsidian shows the filename as a second title above each note's own heading.

## Walkthrough (reader check)

index → [[Networking Tracker]] → [[Row Level Security]] → Sources link `Networking Tracker README#Schema and Row Level Security` opens the original README at that section. The shared note [[Model Evaluation]] has sections from both Custom LLM and Pac-Man DQN. `wiki check` reports 18 files, 14 wiki notes, 133 links, no problems.

Expected, not a bug: the raw READMEs in `raw/` show broken images, because their image files live in the original project repos and the originals are kept unchanged.

## What the graph shows

Three project hubs. Networking Tracker connects to Row Level Security, Node Backend Architecture, Neon Postgres and Vercel Deployment. Pac-Man DQN and Custom LLM are joined through meaningful shared notes: Model Evaluation (both projects' evaluation methods), Learning Rate (0.0001 vs 0.001) and Model Training. No links were added just to connect the graph.

## Correction found during this check

While checking screenshot 01b, the Row Level Security note's GRANT bullet turned out to misstate the source. It was corrected; see [wiki-review.md](wiki-review.md), item 3.
