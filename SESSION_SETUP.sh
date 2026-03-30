#!/usr/bin/env bash
# SESSION_SETUP.sh — Run ONCE at the start of every session, before any test scripts.
#
# Does everything except run tests:
#   WHO   — sets git identity
#   WHAT  — prints project summary and current milestone
#   WHERE — clones/updates all required repos
#   WHERE — installs ALL required tools (apt + build from source)
#   WHERE — builds scrip-cc
#   WHY   — prints the four docs to read before coding
#
# Usage:
#   TOKEN=ghp_xxx bash /home/claude/.github/SESSION_SETUP.sh
#
# After this completes, run the two test scripts:
#   cd /home/claude/one4all && CORPUS=/home/claude/corpus bash test/run_emit_check.sh
#   cd /home/claude/one4all && CORPUS=/home/claude/corpus bash test/run_invariants.sh
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
echo -e "${BOLD}  snobol4ever SESSION SETUP${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"

# ── TOKEN ─────────────────────────────────────────────────────────────────────
if [[ -z "${TOKEN:-}" ]]; then
    echo -n "  GitHub token (ghp_...): "; read -rs TOKEN; echo ""
fi
[[ -z "$TOKEN" ]] && { echo "ERROR: TOKEN required"; exit 1; }
GH="https://${TOKEN}@github.com/snobol4ever"

# ── FRONTEND / BACKEND switches ───────────────────────────────────────────────
# Optional: set FRONTEND= and/or BACKEND= to skip unneeded tool installs.
# See SETUP-tools.md for the full matrix.
# Default (omitted): install everything.
FRONTEND="${FRONTEND:-all}"
BACKEND="${BACKEND:-all}"
info "Session target: FRONTEND=${FRONTEND}  BACKEND=${BACKEND}"
info "See SETUP-tools.md for tool matrix."

# need_backend VAL  — true if BACKEND matches VAL or is "all"
need_backend()  { [[ "$BACKEND"  == "all" || "$BACKEND"  == "$1" ]]; }
# need_frontend VAL — true if FRONTEND matches VAL or is "all"
need_frontend() { [[ "$FRONTEND" == "all" || "$FRONTEND" == "$1" ]]; }

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

clone_or_pull() {
    local repo="$1" dir="$2"
    if [[ -d "$dir/.git" ]]; then
        git -C "$dir" pull --rebase --quiet 2>/dev/null \
            && ok "$dir (updated)" \
            || info "$dir (pull skipped — local changes)"
    else
        git clone --quiet "$GH/${repo}" "$dir" && ok "$dir (cloned)"
    fi
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
apt_install curl
apt_install unzip
apt_install ar     binutils

# Rebus frontend only — bison/flex needed to regenerate parser; generated files are
# committed to the repo so normal builds don't require them.
if need_frontend rebus; then
    apt_install bison
    apt_install flex
else
    info "Skipping bison/flex (FRONTEND=${FRONTEND} — only needed to regenerate Rebus parser)"
fi

# x64 backend tools
if need_backend x64; then
    apt_install nasm
    if ldconfig -p 2>/dev/null | grep -q 'libgc\.so'; then
        ok "libgc (Boehm GC)"
    else
        info "Installing libgc-dev ..."
        apt-get install -y libgc-dev -qq 2>/dev/null && ok "libgc-dev installed" \
            || fail "libgc-dev install failed"
    fi
else
    info "Skipping nasm + libgc (BACKEND=${BACKEND})"
fi

# JVM backend tools
if need_backend jvm; then
    apt_install java   default-jre
    apt_install javac  default-jdk
else
    info "Skipping java/javac (BACKEND=${BACKEND})"
fi

# .NET backend tools
if need_backend net; then
    if command -v mono &>/dev/null && command -v ilasm &>/dev/null; then
        ok "mono + ilasm"
    else
        info "Installing mono-complete (optional — .NET cell) ..."
        apt-get install -y mono-complete -qq 2>/dev/null \
            && ok "mono-complete" \
            || info "mono unavailable — .NET cell will SKIP"
    fi
else
    info "Skipping mono/ilasm (BACKEND=${BACKEND})"
fi

# SnoHarness — compile if absent or stale (JVM backend only)
if need_backend jvm; then
HARNESS_DIR="/home/claude/one4all/test/jvm"
if command -v javac &>/dev/null && \
   [[ ! -f "$HARNESS_DIR/SnoHarness.class" || \
      "$HARNESS_DIR/SnoHarness.java" -nt "$HARNESS_DIR/SnoHarness.class" ]]; then
    info "Compiling SnoHarness ..."
    if javac "$HARNESS_DIR/SnoRuntime.java" "$HARNESS_DIR/SnoHarness.java" \
             -d "$HARNESS_DIR" 2>/dev/null; then
        ok "SnoHarness compiled"
    else
        fail "SnoHarness compile FAILED"
    fi
else
    ok "SnoHarness.class"
fi
else
    info "Skipping SnoHarness (BACKEND=${BACKEND})"
fi

# ── WHERE — oracle: SWI-Prolog ───────────────────────────────────────────────
step "WHERE — oracle: SWI-Prolog"
if need_frontend prolog; then
if command -v swipl &>/dev/null; then
    ok "swipl ($(swipl --version 2>&1 | head -1))"
else
    info "Installing swi-prolog via apt ..."
    apt-get install -y swi-prolog -qq 2>/dev/null \
        && ok "swipl installed" \
        || fail "swipl install failed"
fi
else
    info "Skipping swipl (FRONTEND=${FRONTEND})"
fi

# ── WHERE — oracle: Icon (icont / iconx) ─────────────────────────────────────
step "WHERE — oracle: Icon"
if need_frontend icon; then
if command -v icont &>/dev/null; then
    ok "icont"
else
    info "Trying apt install icont ..."
    if apt-get install -y icont -qq 2>/dev/null; then
        ok "icont installed via apt"
    else
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
else
    info "Skipping icont/iconx (FRONTEND=${FRONTEND})"
fi

# ── WHERE — oracle: CSNOBOL4 2.3.3 ───────────────────────────────────────────
step "WHERE — oracle: CSNOBOL4"
if need_frontend snobol4 || need_frontend snocone; then
if command -v snobol4 &>/dev/null; then
    ok "snobol4 (CSNOBOL4)"
else
    fail "CSNOBOL4 — NOT installed. NEVER download from snobol4.org (broken). Ask Lon to upload snobol4-2_3_3_tar.gz, then build with: mkdir -p /tmp/sno_build && tar -xzf <tarball> -C /tmp/sno_build && cd /tmp/sno_build/snobol4-2.3.3 && apt-get install -y m4 && ./configure --prefix=/usr/local && make -j\$(nproc) && make install"
fi
else
    info "Skipping CSNOBOL4 (FRONTEND=${FRONTEND})"
fi

# ── WHERE — oracle: SPITBOL x64 ──────────────────────────────────────────────
step "WHERE — oracle: SPITBOL"
if [[ "$FRONTEND" == "all" ]]; then
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
else
    info "Skipping SPITBOL (full-install mode only — FRONTEND=${FRONTEND})"
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
info "tail -120 /home/claude/.github/SESSIONS_ARCHIVE.md   # last handoff — FIRST"
info "cat  /home/claude/.github/RULES.md                   # mandatory rules"
info "cat  /home/claude/.github/PLAN.md                    # NOW table"
info "cat  /home/claude/.github/GRAND_MASTER_REORG.md      # phase detail"
info "cat  /home/claude/.github/SETUP-tools.md             # tool matrix (FRONTEND × BACKEND)"

# ── SUMMARY ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}  SETUP COMPLETE — now run the two test scripts:${RESET}"
    echo -e "${GREEN}    cd /home/claude/one4all${RESET}"
    echo -e "${GREEN}    CORPUS=/home/claude/corpus bash test/run_emit_check.sh${RESET}"
    echo -e "${GREEN}    CORPUS=/home/claude/corpus bash test/run_invariants.sh${RESET}"
else
    echo -e "${RED}${BOLD}  SETUP COMPLETE — ${ERRORS} problem(s) above — fix before running tests${RESET}"
fi
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
exit $ERRORS
