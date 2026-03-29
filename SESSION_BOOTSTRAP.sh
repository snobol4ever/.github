#!/usr/bin/env bash
# SESSION_BOOTSTRAP.sh — Run this at the start of every session, no exceptions.
#
# Does six things:
#   WHO   — sets git identity
#   WHAT  — confirms what we are building
#   WHERE — clones all required repos
#   WHERE — installs all required tools
#   WHY   — prints the current milestone from PLAN.md
#   HOW   — runs all nine invariants (3x3 matrix) and reports pass/fail
#
# Usage:
#   TOKEN=ghp_xxx bash SESSION_BOOTSTRAP.sh
#
# If TOKEN is not set, will prompt. Never hardcode the token in this file.

set -euo pipefail
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; BOLD='\033[1m'; RESET='\033[0m'

ok()   { echo -e "${GREEN}  OK${RESET}  $*"; }
fail() { echo -e "${RED}FAIL${RESET}  $*"; ERRORS=$((ERRORS+1)); }
info() { echo -e "${YELLOW}    ${RESET}  $*"; }
ERRORS=0

echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  snobol4ever SESSION BOOTSTRAP${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo ""

# ── TOKEN ────────────────────────────────────────────────────────────────────
if [[ -z "${TOKEN:-}" ]]; then
    echo -n "GitHub token (ghp_...): "
    read -rs TOKEN
    echo ""
fi
[[ -z "$TOKEN" ]] && { echo "ERROR: TOKEN required"; exit 1; }
GH="https://${TOKEN}@github.com/snobol4ever"

# ── WHO — git identity ────────────────────────────────────────────────────────
echo -e "${BOLD}WHO — git identity${RESET}"
git config --global user.name  "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"
ok "All commits will be authored as LCherryholmes <lcherryh@yahoo.com>"
echo ""

# ── WHAT — project summary ────────────────────────────────────────────────────
echo -e "${BOLD}WHAT — project${RESET}"
info "SNOBOL4/SPITBOL compiler/runtime"
info "6 frontends (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip)"
info "4 backends  (x86, JVM, .NET, WASM)"
info "Grand Master Reorg (G-8): Phase 2+4 done; M-G-INV-EMIT next (emit-diff harness)"
info "Reference docs: one4all/doc/EMITTER_AUDIT.md · IR_AUDIT.md · SIL_NAMES_AUDIT.md"
echo ""

# ── WHERE — clone repos ───────────────────────────────────────────────────────
echo -e "${BOLD}WHERE — repos${RESET}"
cd /home/claude

clone_or_pull() {
    local repo="$1" dir="$2"
    if [[ -d "$dir/.git" ]]; then
        git -C "$dir" pull --rebase --quiet 2>/dev/null && ok "$dir (updated)" || info "$dir (pull skipped — local changes)"
    else
        git clone --quiet "$GH/${repo}" "$dir" && ok "$dir (cloned)"
    fi
}

clone_or_pull ".github"       ".github"
clone_or_pull "one4all"      "one4all"
clone_or_pull "corpus" "corpus"
clone_or_pull "harness" "harness"
echo ""

# ── WHERE — install tools ─────────────────────────────────────────────────────
echo -e "${BOLD}WHERE — tools${RESET}"

install_if_missing() {
    local cmd="$1" pkg="${2:-$1}"
    if command -v "$cmd" &>/dev/null; then
        ok "$cmd ($(command -v $cmd))"
    else
        info "Installing $pkg..."
        apt-get install -y "$pkg" -qq 2>/dev/null && ok "$cmd installed" || fail "$cmd — install failed"
    fi
}

install_if_missing nasm
install_if_missing mono   mono-complete
install_if_missing ilasm  mono-complete
install_if_missing java   default-jre

# jasmin.jar — bundled in repo
JASMIN="/home/claude/one4all/src/backend/jvm/jasmin.jar"
[[ -f "$JASMIN" ]] && ok "jasmin.jar ($JASMIN)" || fail "jasmin.jar not found at $JASMIN"

# scrip-cc binary — built from one4all
SNO2C="/home/claude/one4all/scrip-cc"
if [[ ! -x "$SNO2C" ]]; then
    info "Building scrip-cc..."
    (cd /home/claude/one4all && bash setup.sh -q 2>/dev/null) && ok "scrip-cc built" || fail "scrip-cc build failed"
else
    ok "scrip-cc ($SNO2C)"
fi
echo ""

# ── WHY — current milestone ───────────────────────────────────────────────────
echo -e "${BOLD}WHY — current milestone${RESET}"
PLAN="/home/claude/.github/PLAN.md"
if [[ -f "$PLAN" ]]; then
    grep "GRAND MASTER REORG" "$PLAN" | head -1 | sed 's/^[ |*]*/  /' || true
    grep "Next milestone" "$PLAN" | head -1 | sed 's/^[ |*]*/  /' || true
fi
echo ""
info "Read these before touching any code:"
info "  tail -80 /home/claude/.github/SESSIONS_ARCHIVE.md    # handoff"
info "  cat /home/claude/.github/RULES.md                    # mandatory rules"
info "  cat /home/claude/.github/PLAN.md                     # NOW table"
info "  cat /home/claude/.github/GRAND_MASTER_REORG.md       # phase detail"
echo ""

# ── HOW — emit-diff invariant check (fast, emitter-only, ~4s) ─────────────────
echo -e "${BOLD}HOW — emit-diff invariants (must be green before any work)${RESET}"
cd /home/claude/one4all
if [[ -d test/emit_baseline ]]; then
    info "Running emit-diff check (test/run_emit_check.sh)..."
    if CORPUS=/home/claude/corpus bash test/run_emit_check.sh 2>&1; then
        ok "Emit-diff: all green"
    else
        fail "Emit-diff: mismatches found — do not proceed until green"
        ERRORS=$((ERRORS+1))
    fi
else
    info "No emit baseline yet — run: bash test/g8_session.sh --only-baseline"
    info "Falling back to run_invariants.sh (slow — builds + runs programs)..."
    if CORPUS=/home/claude/corpus bash test/run_invariants.sh 2>&1; then
        echo ""
    else
        echo ""
        ERRORS=$((ERRORS+1))
    fi
fi
echo ""

# ── SUMMARY ──────────────────────────────────────────────────────────────────
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}  BOOTSTRAP COMPLETE — session ready${RESET}"
else
    echo -e "${RED}${BOLD}  BOOTSTRAP COMPLETE — ${ERRORS} problem(s), review above${RESET}"
fi
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
