"""Paths and model settings in one place.

Every setting can be overridden with an environment variable, so the same code
runs on another machine without edits.
"""
import os
from pathlib import Path

# Folders (all relative to the project root, wherever it's cloned)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VAULT_DIR = PROJECT_ROOT / "vault"          # the Obsidian vault
RAW_DIR = VAULT_DIR / "raw"                 # unchanged original sources
WIKI_DIR = VAULT_DIR / "wiki"               # generated, reviewed notes
INDEX_NOTE = VAULT_DIR / "index.md"         # human landing page
DATA_DIR = PROJECT_ROOT / "data"            # machine files: chunks, catalog (kept out of the vault)
PROMPTS_DIR = PROJECT_ROOT / "prompts"      # persona and research rules
EVIDENCE_DIR = Path(os.environ.get("WIKI_EVIDENCE_DIR", PROJECT_ROOT / "evidence"))  # saved runs and transcripts

# Local model (Ollama)
_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_HOST = _host if _host.startswith("http") else f"http://{_host}"
MODEL = os.environ.get("WIKI_MODEL", "gemma4:e2b-it-qat")
NUM_CTX = int(os.environ.get("WIKI_NUM_CTX", "8192"))   # context window in tokens
INGEST_NUM_CTX = 16384   # ingest reads a whole source at once; the largest is ~6,250 tokens
REQUEST_TIMEOUT = 300                                   # seconds; an 8 GB M1 can be slow on long prompts
