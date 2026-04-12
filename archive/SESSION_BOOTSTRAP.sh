#!/usr/bin/env bash
# SESSION_BOOTSTRAP.sh — Run this at the start of every session, no exceptions.
#
# Does six things:
#   WHO   — sets git identity
#   WHAT  — prints project summary and current milestone
#   WHERE — clones/updates all required repos
#   WHERE — installs ALL required tools (apt + build from source, internet)
#   WHY   — prints the four docs to read before coding
#   HOW   — runs emit-diff check then full 7-cell crosscheck gate
#
# Usage:
#   TOKEN=ghp_xxx bash /home/claude/.github/SESSION_BOOTSTRAP.sh
#
# All tool installation is fully automatic. Network access required.
# Never hardcode the token — TOKEN env var only.
# Use TOKEN_SEE_LON as placeholder in any doc that references it.

set -uo pipefail
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; BOLD='\033[1m'; RESET='\033[0m'

ok()   { echo -e "${GREEN}  OK${RESET}  $*"; }
fail() { echo -e "${RED}FAIL${RESET}  $*"; ERRORS=$((ERRORS+1)); }
info() { echo -e "${YELLOW}INFO${RESET}  $*"; }
step() { echo -e "\n${BOLD}$*${RESET}"; }
ERRORS=0

echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  snobol4ever SESSION BOOTSTRAP${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"

# ── TOKEN ─────────────────────────────────────────────────────────────────────
if [[ -z "${TOKEN:-}" ]]; then
    echo -n "  GitHub token (ghp_...): "; read -rs TOKEN; echo ""
fi
[[ -z "$TOKEN" ]] && { echo "ERROR: TOKEN required"; exit 1; }
GH="https://${TOKEN}@github.com/snobol4ever"

# ── WHO — git identity ────────────────────────────────────────────────────────
step "WHO — git identity"
git config --global user.name  "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"
ok "All commits authored as LCherryholmes <lcherryh@yahoo.com>"

# ── WHAT — project summary ────────────────────────────────────────────────────
step "WHAT — project"
info "SNOBOL4/SPITBOL compiler/runtime — 6 frontends × 4 backends"
info "Frontends: SNOBOL4 · Icon · Prolog · Snocone · Rebus · Scrip"
info "Backends:  x86 (nasm) · JVM (Jasmin) · .NET (MSIL) · WASM (stub)"
info "Grand Master Reorg (G-9): infrastructure hardened; M-G4-SHARED-OR next"

# ── WHERE — repos ─────────────────────────────────────────────────────────────
step "WHERE — repos"
cd /home/claude

install_push_guard() {
    local dir="$1"
    mkdir -p "$dir/.git/hooks"
    cat > "$dir/.git/hooks/pre-push" << 'HOOK'
#!/bin/bash
if [ ! -f /tmp/handoff_authorized ]; then
    echo "⛔ PUSH BLOCKED — Lon has not said 'perform hand off'."
    echo "   Do not push until handoff is called."
    exit 1
fi
HOOK
    chmod +x "$dir/.git/hooks/pre-push"
}

clone_or_pull() {
    local repo="$1" dir="$2"
    if [[ -d "$dir/.git" ]]; then
        git -C "$dir" pull --rebase --quiet 2>/dev/null \
            && ok "$dir (updated)" \
            || info "$dir (pull skipped — local changes)"
    else
        git clone --quiet "$GH/${repo}" "$dir" && ok "$dir (cloned)"
    fi
    # snobol4dotnet is Jeff's repo — no push guard there
    [[ "$dir" != *"snobol4dotnet"* ]] && install_push_guard "$dir"
}

clone_or_pull ".github"  ".github"
clone_or_pull "one4all"  "one4all"
clone_or_pull "corpus"   "corpus"
clone_or_pull "harness"  "harness"

# ── WHERE — apt packages ──────────────────────────────────────────────────────
step "WHERE — tools (apt)"

apt_install() {
    local cmd="$1" pkg="${2:-$1}"
    if command -v "$cmd" &>/dev/null; then
        ok "$cmd"
    else
        info "Installing $pkg ..."
        apt-get install -y "$pkg" -qq 2>/dev/null && ok "$cmd installed" \
            || fail "$cmd — apt install failed"
    fi
}

apt_install gcc
apt_install make
apt_install nasm
apt_install ar     binutils
apt_install curl
apt_install unzip
apt_install java   default-jre
apt_install javac  default-jdk

# libgc (Boehm GC) — -lgc for x86 test link
if ldconfig -p 2>/dev/null | grep -q 'libgc\.so'; then
    ok "libgc (Boehm GC)"
else
    info "Installing libgc-dev ..."
    apt-get install -y libgc-dev -qq 2>/dev/null && ok "libgc-dev installed" \
        || fail "libgc-dev install failed"
fi

# mono / ilasm — .NET backend (non-fatal if unavailable)
if command -v mono &>/dev/null && command -v ilasm &>/dev/null; then
    ok "mono + ilasm"
else
    info "Installing mono-complete (optional — .NET cell) ..."
    apt-get install -y mono-complete -qq 2>/dev/null \
        && ok "mono-complete" \
        || info "mono unavailable — .NET cell will SKIP"
fi

# ── WHERE — oracle: SWI-Prolog ───────────────────────────────────────────────
step "WHERE — oracle: SWI-Prolog"
if command -v swipl &>/dev/null; then
    ok "swipl ($(swipl --version 2>&1 | head -1))"
else
    info "Installing swi-prolog via apt ..."
    apt-get install -y swi-prolog -qq 2>/dev/null \
        && ok "swipl installed" \
        || fail "swipl install failed"
fi

# ── WHERE — oracle: Icon (icont / iconx) ─────────────────────────────────────
step "WHERE — oracle: Icon"
if command -v icont &>/dev/null; then
    ok "icont"
else
    info "Trying apt install icont ..."
    if apt-get install -y icont -qq 2>/dev/null; then
        ok "icont installed via apt"
    else
        # Build from github.com/gtownsend/icon (v9.5.x)
        info "Building Icon from github.com/gtownsend/icon ..."
        ICON_BUILD=/tmp/icon_build_$$; mkdir -p "$ICON_BUILD"
        if curl -sL "https://github.com/gtownsend/icon/archive/refs/heads/master.zip" \
                -o "$ICON_BUILD/icon.zip" \
            && unzip -q "$ICON_BUILD/icon.zip" -d "$ICON_BUILD" \
            && cd "$ICON_BUILD"/icon-master \
            && make X=0 2>/dev/null \
            && cp bin/icont bin/iconx /usr/local/bin/; then
            ok "icont + iconx built from source"
        else
            fail "icont — build failed"
        fi
        rm -rf "$ICON_BUILD"; cd /home/claude
    fi
fi

# ── WHERE — oracle: SPITBOL (CSNOBOL4 removed) ────────────────────────────────
# CSNOBOL4 is not used. SPITBOL is the sole oracle. Installed above from snobol4ever/x64.

# ── WHERE — oracle: SPITBOL x64 ──────────────────────────────────────────────
step "WHERE — oracle: SPITBOL"
if command -v spitbol &>/dev/null; then
    ok "spitbol"
else
    info "Building SPITBOL from github.com/spitbol/spitbol ..."
    SPIT_BUILD=/tmp/spit_build_$$; mkdir -p "$SPIT_BUILD"
    if curl -sL "https://github.com/spitbol/spitbol/archive/refs/heads/master.zip" \
            -o "$SPIT_BUILD/spitbol.zip" \
        && unzip -q "$SPIT_BUILD/spitbol.zip" -d "$SPIT_BUILD" \
        && cd "$SPIT_BUILD"/spitbol-master \
        && make 2>/dev/null \
        && cp spitbol /usr/local/bin/; then
        ok "spitbol installed"
    else
        fail "SPITBOL — build failed (non-fatal for most cells)"
    fi
    rm -rf "$SPIT_BUILD"; cd /home/claude
fi

# ── WHERE — build scrip-cc ────────────────────────────────────────────────────
step "WHERE — scrip-cc (project compiler)"
SCRIP_CC=/home/claude/one4all/scrip-cc
if [[ ! -x "$SCRIP_CC" || ! -s "$SCRIP_CC" ]]; then
    info "Building scrip-cc from one4all/src/ ..."
    (cd /home/claude/one4all/src && make -j"$(nproc)" 2>/dev/null) \
        && ok "scrip-cc built" \
        || fail "scrip-cc — build failed"
else
    ok "scrip-cc (already built)"
fi

# jasmin.jar — bundled in repo
JASMIN=/home/claude/one4all/src/backend/jvm/jasmin.jar
[[ -f "$JASMIN" ]] && ok "jasmin.jar" || fail "jasmin.jar missing at $JASMIN"

# ── WHY — what to read ────────────────────────────────────────────────────────
step "WHY — read before coding (mandatory)"
PLAN=/home/claude/.github/PLAN.md
[[ -f "$PLAN" ]] && grep -E "GRAND MASTER REORG|Next milestone" "$PLAN" \
    | head -2 | sed 's/^/  /'
echo ""
info "tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md   # last handoff"
info "cat  /home/claude/.github/RULES.md                   # mandatory rules"
info "cat  /home/claude/.github/PLAN.md                    # NOW table"
info "cat  /home/claude/.github/GRAND_MASTER_REORG.md      # phase detail"

# ── HOW — crosscheck gate ──────────────────────────────────────────────────────
step "HOW — emit-diff (493/0 baseline)"
cd /home/claude/one4all
if SCRIP_CC="$SCRIP_CC" bash test/crosscheck.sh 2>&1; then
    ok "Emit-diff: green"
else
    fail "Emit-diff: mismatches — do not proceed"
fi

step "HOW — 7-cell runtime crosscheck gate"
if SCRIP_CC="$SCRIP_CC" CORPUS=/home/claude/corpus \
   bash test/crosscheck.sh 2>&1; then
    ok "All crosschecks: PASS"
else
    fail "Crosscheck: failures present — review matrix above"
fi

# ── SUMMARY ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}  BOOTSTRAP COMPLETE — session ready${RESET}"
else
    echo -e "${RED}${BOLD}  BOOTSTRAP COMPLETE — ${ERRORS} problem(s) above${RESET}"
fi
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
exit $ERRORS
