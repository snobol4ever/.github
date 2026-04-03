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
# ⛔ ALWAYS pass FRONTEND= and BACKEND= — installs only what you need:
#   FRONTEND=snobol4 BACKEND=jvm  TOKEN=ghp_xxx bash /home/claude/.github/SESSION_SETUP.sh
#   FRONTEND=snobol4 BACKEND=x64  TOKEN=ghp_xxx bash /home/claude/.github/SESSION_SETUP.sh
#   FRONTEND=snobol4 BACKEND=net  TOKEN=ghp_xxx bash /home/claude/.github/SESSION_SETUP.sh
#   (omit FRONTEND/BACKEND only for grand-master / multi-cell sessions)
#
# After this completes, run the appropriate test script for your session type:
#
#   JVM interpreter sessions (DYN-, J-, one4all-SNOBOL4-NET):
#     cd /home/claude/one4all && CORPUS=/home/claude/corpus bash test/run_interp_broad.sh
#     (do NOT run run_invariants.sh or run_emit_check.sh for interpreter sessions)
#
#   Emit sessions (x86, JVM emitter, .NET):
#     cd /home/claude/one4all && CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_jvm
#     cd /home/claude/one4all && CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_x86
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

# bison/flex: NEVER installed -- rebus.tab.c, rebus.tab.h, lex.rebus.c are committed
# and always kept current. If rebus.y/rebus.l are modified, regenerate on your own
# machine and commit the result. See RULES.md.

# WASM backend tools
if need_backend wasm; then
    apt_install wat2wasm  wabt
    if command -v node &>/dev/null; then
        ok "node $(node --version)"
    else
        apt_install node nodejs
    fi
else
    info "Skipping wabt/node (BACKEND=${BACKEND})"
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
# DEPRECATED — CSNOBOL4 is no longer needed on a regular basis.
# SPITBOL (position zero) is the authoritative oracle for all sessions.
# CSNOBOL4 is NOT a valid oracle for Snocone (lacks FENCE + SPITBOL extensions).
# snobol4.org is broken as of 2026-03-30. If CSNOBOL4 is ever needed, ask Lon
# to upload snobol4-2_3_3_tar.gz and build manually — do NOT attempt here.
step "WHERE — oracle: CSNOBOL4 (deprecated — skipped)"
if command -v snobol4 &>/dev/null; then
    info "snobol4 (CSNOBOL4) present but not required — SPITBOL is primary oracle"
else
    info "CSNOBOL4 not installed — not required. SPITBOL is the authoritative oracle."
fi

# ── WHERE — oracle: SPITBOL x64 ──────────────────────────────────────────────
# SPITBOL is the PRIMARY oracle (position zero). Required for snocone + all sessions.
# CSNOBOL4 is NOT a valid Snocone oracle — it lacks FENCE and SPITBOL extensions.
# Install from snobol4ever/x64 (pre-built bin/sbl) — never from github.com/spitbol/spitbol.
step "WHERE — oracle: SPITBOL"
if [[ "$FRONTEND" == "all" || "$FRONTEND" == "snocone" || "$FRONTEND" == "snobol4" ]]; then
if command -v spitbol &>/dev/null; then
    ok "spitbol"
else
    # Use snobol4ever/x64 pre-built binary (TOKEN required)
    if [[ -n "$TOKEN" ]]; then
        SPIT_BUILD=/tmp/spit_x64_$$; mkdir -p "$SPIT_BUILD"
        if git clone --depth=1 "https://oauth2:${TOKEN}@github.com/snobol4ever/x64" "$SPIT_BUILD/x64" 2>/dev/null \
            && cp "$SPIT_BUILD/x64/bin/sbl" /usr/local/bin/spitbol \
            && chmod +x /usr/local/bin/spitbol; then
            ok "spitbol installed from snobol4ever/x64"
        else
            fail "SPITBOL — install from snobol4ever/x64 failed — provide TOKEN"
        fi
        rm -rf "$SPIT_BUILD"; cd /home/claude
    else
        fail "SPITBOL — TOKEN not set; cannot clone snobol4ever/x64"
    fi
fi
else
    info "Skipping SPITBOL (FRONTEND=${FRONTEND} does not require it)"
fi

# ── WHERE — build scrip-cc ────────────────────────────────────────────────────
# scrip-cc is the x86/JVM/WASM emit compiler — not used in .NET sessions.
if need_backend net && ! need_backend all; then
    step "WHERE — scrip-cc (project compiler)"
    info "Skipping scrip-cc build (BACKEND=net — .NET sessions use dotnet, not scrip-cc)"
else
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
fi

# jasmin.jar — bundled in repo (JVM backend only)
if need_backend jvm; then
    JASMIN=/home/claude/one4all/src/backend/jvm/jasmin.jar
    [[ -f "$JASMIN" ]] && ok "jasmin.jar" || fail "jasmin.jar missing at $JASMIN"
fi

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
    if need_backend net && ! need_backend all; then
        echo -e "${GREEN}${BOLD}  SETUP COMPLETE — .NET session, run:${RESET}"
        echo -e "${GREEN}    cd /home/claude/one4all${RESET}"
        echo -e "${GREEN}    dotnet build src/driver/dotnet/scrip-interp.csproj -c Release -o /tmp/sni${RESET}"
        echo -e "${GREEN}    dotnet /tmp/sni/scrip-interp.dll /home/claude/corpus/crosscheck/hello/hello.sno${RESET}"
        echo -e "${GREEN}    INTERP=/tmp/sni_run.sh CORPUS=/home/claude/corpus TIMEOUT=10 bash test/run_interp_broad.sh${RESET}"
    else
        echo -e "${GREEN}${BOLD}  SETUP COMPLETE — now run the two test scripts:${RESET}"
        echo -e "${GREEN}    cd /home/claude/one4all${RESET}"
        echo -e "${GREEN}    CORPUS=/home/claude/corpus bash test/run_emit_check.sh${RESET}"
        echo -e "${GREEN}    CORPUS=/home/claude/corpus bash test/run_invariants.sh${RESET}"
    fi
else
    echo -e "${RED}${BOLD}  SETUP COMPLETE — ${ERRORS} problem(s) above — fix before running tests${RESET}"
fi
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
exit $ERRORS
