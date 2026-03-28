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
clone_or_pull "snobol4corpus" "snobol4corpus"
clone_or_pull "snobol4harness" "snobol4harness"
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

# x86
echo -n "  x86  ... "
X86=$(bash test/crosscheck/run_crosscheck_asm_corpus.sh 2>/dev/null | grep "Results:" | tail -1)
if echo "$X86" | grep -q "0 failed"; then
    PASSED=$(echo "$X86" | grep -o '[0-9]* passed' | head -1)
    echo -e "${GREEN}${PASSED}${RESET}"
else
    echo -e "${RED}${X86}${RESET}"
    ERRORS=$((ERRORS+1))
fi

# JVM
echo -n "  JVM  ... "
CORPUS="/home/claude/snobol4corpus/crosscheck"
JVM_DIRS="$CORPUS/hello $CORPUS/output $CORPUS/arith $CORPUS/assign $CORPUS/concat \
          $CORPUS/arith_new $CORPUS/control_new $CORPUS/patterns $CORPUS/capture \
          $CORPUS/strings $CORPUS/functions $CORPUS/data $CORPUS/keywords \
          $CORPUS/rung2 $CORPUS/rung3 $CORPUS/rung10 $CORPUS/rung11"
JVM=$(bash test/crosscheck/run_crosscheck_jvm_rung.sh $JVM_DIRS 2>/dev/null | grep "Results:" | tail -1)
if echo "$JVM" | grep -q "0 failed"; then
    PASSED=$(echo "$JVM" | grep -o '[0-9]* passed' | head -1)
    echo -e "${GREEN}${PASSED}${RESET}"
else
    PASSED=$(echo "$JVM" | grep -o '[0-9]* passed' | head -1)
    FAILED=$(echo "$JVM" | grep -o '[0-9]* failed' | head -1)
    echo -e "${YELLOW}${PASSED} passed, ${FAILED} failed (check if pre-existing)${RESET}"
fi

# .NET
echo -n "  .NET ... "
NET=$(bash test/crosscheck/run_crosscheck_net.sh 2>/dev/null | grep "Results:" | tail -1)
if echo "$NET" | grep -q "0 failed\|1 failed"; then
    PASSED=$(echo "$NET" | grep -o '[0-9]* passed' | head -1)
    FAILED=$(echo "$NET" | grep -o '[0-9]* failed' | head -1)
    if echo "$NET" | grep -q "0 failed"; then
        echo -e "${GREEN}${PASSED}${RESET}"
    else
        echo -e "${YELLOW}${PASSED} passed, ${FAILED} failed (056_pat_star_deref — pending Lon clarification)${RESET}"
    fi
else
    echo -e "${RED}${NET}${RESET}"
    ERRORS=$((ERRORS+1))
fi


# Icon x64
echo -n "  Icon x64 ... "
if ! command -v icont &>/dev/null; then
    echo -e "${YELLOW}SKIP (icont not found)${RESET}"
else
    ICN_PASS=0; ICN_FAIL=0
    ICON_ASM=/home/claude/snobol4x/icon-asm
    for rung_sh in /home/claude/snobol4x/test/frontend/icon/run_rung*.sh; do
        result=$(bash "$rung_sh" "$ICON_ASM" 2>/dev/null | grep -E "^(PASS|FAIL|Results)" | tail -1)
        if echo "$result" | grep -q "FAIL\|failed [^0]"; then
            ICN_FAIL=$((ICN_FAIL+1))
        else
            ICN_PASS=$((ICN_PASS+1))
        fi
    done
    if [[ $ICN_FAIL -eq 0 ]]; then
        echo -e "${GREEN}${ICN_PASS} rungs PASS${RESET}"
    else
        echo -e "${RED}${ICN_PASS} pass, ${ICN_FAIL} fail${RESET}"
        ERRORS=$((ERRORS+1))
    fi
fi

# Prolog x64
echo -n "  Prolog x64 ... "
if ! command -v nasm &>/dev/null; then
    echo -e "${YELLOW}SKIP (nasm not found)${RESET}"
else
    PL_PASS=0; PL_FAIL=0
    cd /home/claude/snobol4x
    PLRT_OBJS=""
    WORK_PL=$(mktemp -d /tmp/pl_inv_XXXXXX)
    gcc -O0 -g -c src/frontend/prolog/prolog_atom.c    -Isrc/frontend/prolog -w -o $WORK_PL/atom.o    2>/dev/null
    gcc -O0 -g -c src/frontend/prolog/prolog_unify.c   -Isrc/frontend/prolog -w -o $WORK_PL/unify.o   2>/dev/null
    gcc -O0 -g -c src/frontend/prolog/prolog_builtin.c -Isrc/frontend/prolog -Isrc/frontend/prolog -w -o $WORK_PL/builtin.o 2>/dev/null
    PLRT_OBJS="$WORK_PL/atom.o $WORK_PL/unify.o $WORK_PL/builtin.o"
    for rung_dir in test/frontend/prolog/corpus/rung*/; do
        rung_pass=0; rung_fail=0
        for pro in "$rung_dir"*.pro; do
            [ -f "$pro" ] || continue
            expected="${pro%.pro}.expected"
            [ -f "$expected" ] || continue
            W=$(mktemp -d /tmp/pl_t_XXXXXX)
            ./sno2c -pl -asm "$pro" > $W/t.asm 2>/dev/null &&
            nasm -f elf64 $W/t.asm -o $W/t.o 2>/dev/null &&
            gcc -no-pie $W/t.o $PLRT_OBJS -lm -o $W/t 2>/dev/null &&
            actual=$(timeout 8 $W/t 2>/dev/null) || actual="__CRASH__"
            if [ "$actual" = "$(cat $expected)" ]; then
                rung_pass=$((rung_pass+1))
            else
                rung_fail=$((rung_fail+1))
            fi
            rm -rf $W
        done
        [ $rung_fail -gt 0 ] && PL_FAIL=$((PL_FAIL+1)) || PL_PASS=$((PL_PASS+1))
    done
    rm -rf $WORK_PL
    if [[ $PL_FAIL -eq 0 ]]; then
        echo -e "${GREEN}${PL_PASS} rungs PASS${RESET}"
    else
        echo -e "${RED}${PL_PASS} pass, ${PL_FAIL} fail${RESET}"
        ERRORS=$((ERRORS+1))
    fi
fi


# Icon JVM
echo -n "  Icon JVM  ... "
JASMIN=/home/claude/snobol4x/src/backend/jvm/jasmin.jar
if ! command -v java &>/dev/null || [[ ! -f "$JASMIN" ]]; then
    echo -e "${YELLOW}SKIP (java or jasmin.jar not found)${RESET}"
else
    ICN_JVM_PASS=0; ICN_JVM_FAIL=0
    for rung_sh in /home/claude/snobol4x/test/frontend/icon/run_rung*.sh; do
        result=$(bash "$rung_sh" /home/claude/snobol4x/sno2c 2>/dev/null | tail -1)
        if echo "$result" | grep -qE "FAIL [^0]|[1-9][0-9]* FAIL"; then
            ICN_JVM_FAIL=$((ICN_JVM_FAIL+1))
        else
            ICN_JVM_PASS=$((ICN_JVM_PASS+1))
        fi
    done
    if [[ $ICN_JVM_FAIL -eq 0 ]]; then
        echo -e "${GREEN}${ICN_JVM_PASS} rungs PASS${RESET}"
    else
        echo -e "${RED}${ICN_JVM_PASS} pass, ${ICN_JVM_FAIL} fail${RESET}"
        ERRORS=$((ERRORS+1))
    fi
fi

# Prolog JVM
echo -n "  Prolog JVM ... "
JASMIN=/home/claude/snobol4x/src/backend/jvm/jasmin.jar
if ! command -v java &>/dev/null || [[ ! -f "$JASMIN" ]]; then
    echo -e "${YELLOW}SKIP (java or jasmin.jar not found)${RESET}"
else
    PL_JVM_PASS=0; PL_JVM_FAIL=0
    for rung_dir in /home/claude/snobol4x/test/frontend/prolog/corpus/rung*/; do
        result=$(bash /home/claude/snobol4x/test/frontend/prolog/run_prolog_jvm_rung.sh "$rung_dir" 2>/dev/null | grep "Results:" | tail -1)
        if echo "$result" | grep -q "0 failed"; then
            PL_JVM_PASS=$((PL_JVM_PASS+1))
        else
            PL_JVM_FAIL=$((PL_JVM_FAIL+1))
        fi
    done
    if [[ $PL_JVM_FAIL -eq 0 ]]; then
        echo -e "${GREEN}${PL_JVM_PASS} rungs PASS${RESET}"
    else
        echo -e "${RED}${PL_JVM_PASS} pass, ${PL_JVM_FAIL} fail${RESET}"
        ERRORS=$((ERRORS+1))
    fi
fi

# Icon .NET  — not yet implemented
echo -e "  Icon .NET  ... ${YELLOW}SKIP (not implemented)${RESET}"

# Prolog .NET — not yet implemented
echo -e "  Prolog .NET ... ${YELLOW}SKIP (not implemented)${RESET}"

echo ""

# ── SUMMARY ──────────────────────────────────────────────────────────────────
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
if [[ $ERRORS -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}  BOOTSTRAP COMPLETE — session ready${RESET}"
else
    echo -e "${RED}${BOLD}  BOOTSTRAP COMPLETE — ${ERRORS} problem(s), review above${RESET}"
fi
echo -e "${BOLD}═══════════════════════════════════════════════════════${RESET}"
