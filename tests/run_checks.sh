#!/bin/bash
# Full demonstration run: device + network status, ingest, the four ask tests,
# search and chat mode checks, memory and timing. Everything is saved to
# evidence/runs/<timestamp>-<online|offline>/ (terminal.log plus evidence cards).
#
#   ./tests/run_checks.sh
#
# For the required offline run: turn Wi-Fi off first, then run this. The log records
# whether the internet was reachable, so the evidence can't be mixed up.

cd "$(dirname "$0")/.." || exit 1
WIKI=".venv/bin/wiki"
[ -x "$WIKI" ] || { echo "error: $WIKI not found. Set up the venv first (see README)."; exit 1; }

if curl -s -m 5 -o /dev/null https://www.google.com; then NET="online"; else NET="offline"; fi
RUN_DIR="evidence/runs/$(date +%Y-%m-%d_%H%M%S)-$NET"
mkdir -p "$RUN_DIR"
export WIKI_EVIDENCE_DIR="$PWD/$RUN_DIR"   # cards from this run land next to its log

step() { echo; echo "================================================================"; echo "\$ $*"; echo "================================================================"; }
timed() { step "$@"; local t0=$SECONDS; "$@"; echo "[took $((SECONDS - t0))s]"; }

{
  echo "Personal wiki CLI: full check run"
  echo "date:    $(date)"
  echo "network: $NET (checked by trying https://www.google.com with a 5 s timeout)"
  step "device specs"
  system_profiler SPHardwareDataType 2>/dev/null | grep -E "Model Name|Chip|Total Number of Cores|Memory:"
  echo "macOS $(sw_vers -productVersion)"
  df -h ~ | tail -1 | awk '{print "free disk: " $4 " of " $2}'
  memory_pressure 2>/dev/null | grep -i "free percentage"
  step "runtime and model"
  ollama --version
  ollama list | grep -E "NAME|gemma4"

  timed $WIKI --help
  timed $WIKI status

  # Ingest: regenerate the smallest source's notes with local Gemma. The saved plan is reused,
  # so note names stay the same; wiki check then confirms no duplicates or broken links.
  timed $WIKI ingest "./vault/raw/Pac-Man DQN README.md" --force

  timed $WIKI ask "What learning rate did I use for the Pac-Man DQN?" --label "Test 1 (direct)"
  timed $WIKI ask "How much better did my Pac-Man agent get after training?" --label "Test 2 (reworded)"
  timed $WIKI ask "What stops one user from seeing another user's contacts in my networking tracker?" --label "Test 3 (known evidence)"
  timed $WIKI ask "How much does it cost per month to host my Networking Tracker?" --label "Test 4 (unanswerable)"

  step "memory while the model is loaded"
  ollama ps
  ps -axo rss=,comm= | grep -i ollama | awk '{printf "%-40s %6.0f MB\n", $2, $1/1024}'

  timed $WIKI search "row level security" -k 3

  step "chat mode checks: capabilities, draft + follow-up, factual lookup"
  t0=$SECONDS
  printf '%s\n' "what can we do?" "what can you help me with?" \
    "Draft a short study plan for reviewing my three class projects before my final exam." \
    "make that shorter" "What learning rate did I use for the Pac-Man DQN?" "/exit" | $WIKI chat
  echo "[took $((SECONDS - t0))s]"

  step "chat claim vs ask evidence"
  printf '%s\n' "Quick note: hosting my Networking Tracker costs \$20 a month." \
    "So how much does hosting my Networking Tracker cost per month?" "/exit" | $WIKI chat
  timed $WIKI ask "How much does it cost per month to host my Networking Tracker?" --label "Chat claim check"

  echo
  echo "run finished: $(date) · network was $NET · evidence in $RUN_DIR"
} 2>&1 | tee "$RUN_DIR/terminal.log"
