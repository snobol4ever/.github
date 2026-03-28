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
info "Grand Master Reorg (G-7): collapsing all IRs into src/ir/ir.h (59 EKind nodes)"
info "Reference docs: snobol4x/doc/EMITTER_AUDIT.md · IR_AUDIT.md · SIL_NAMES_AUDIT.md"
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
clone_or_pull "snobol4x"      "snobol4x"
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
JASMIN="/home/claude/snobol4x/src/backend/jvm/jasmin.jar"
[[ -f "$JASMIN" ]] && ok "jasmin.jar ($JASMIN)" || fail "jasmin.jar not found at $JASMIN"

# sno2c binary — built from snobol4x
SNO2C="/home/claude/snobol4x/sno2c"
if [[ ! -x "$SNO2C" ]]; then
    info "Building sno2c..."
    (cd /home/claude/snobol4x && bash setup.sh -q 2>/dev/null) && ok "sno2c built" || fail "sno2c build failed"
else
    ok "sno2c ($SNO2C)"
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

# ── HOW — run all nine invariants (3x3: SNOBOL4/Icon/Prolog × x86/JVM/.NET) ─
echo -e "${BOLD}HOW — invariants (must be green before any work)${RESET}"
cd /home/claude/snobol4x
if bash test/run_invariants.sh 2>&1; then
    echo ""
else
    echo ""
    ERRORS=$((ERRORS+1))
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
