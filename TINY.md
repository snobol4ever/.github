# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md) · Monitor: [MONITOR.md](MONITOR.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `t2-impl` — M-T2-INVOKE
**HEAD:** `b606884` B-242 (asm-t2)
**Milestone:** M-MACRO-BOX ✅ → M-T2-INVOKE (next)
**Invariants:** 96/106 ASM corpus (9 known failures + 053 runtime)

**⚡ CRITICAL NEXT ACTION — Session B-243:**

```bash
cd /home/claude/snobol4x && git checkout asm-t2
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-t2   # HEAD should be b606884 B-242
export INC=/home/claude/snobol4corpus/programs/inc
export CORPUS=/home/claude/snobol4corpus/crosscheck

# Invariant check first:
bash test/crosscheck/run_crosscheck_asm_corpus.sh   # expect 96/106

# M-T2-INVOKE: emit T2 call-sites at every named-box invocation
# At each function call site (before jmp box_α):
#   1. save caller r12 on stack  (push r12)
#   2. t2_alloc(box_X_data_size) → rax = new_data ptr
#   3. memcpy(rax, box_X_data_template, box_X_data_size)
#   4. mov r12, rax
#   5. jmp box_X_α
# At γ/ω return labels (currently: jmp [ret_γ] / jmp [ret_ω]):
#   replace with: t2_free(r12, box_X_data_size); pop r12; jmp [ret_slot]
# Use FN_α_INIT to remove the static lea r12 self-init from α entry
# Acceptance: bash test/crosscheck/run_crosscheck_asm_corpus.sh → 96/106
#             roman.sno recursive test: ./snobol4-asm demo/roman.sno → correct output
```

## Last Session Summary

**Session B-242 (2026-03-21) — M-MACRO-BOX ✅ (complete):**
- ARB_α/ARB_β macros: replaced 8 raw A() lines in emit_arb
- NAMED_PAT_γ/ω and FN_α_INIT/FN_γ/FN_ω macros: replaced all raw A() lines in emit_named_def
- Greek letters throughout: all 55 macro names renamed _ALPHA→_α, _BETA→_β, _GAMMA→_γ, _OMEGA→_ω
- Comments in .mac (121 lines) and emitter strings (30 lines) updated to Greek
- bref() gap fixed for DOL (entry_cur, cap_len) and continuation-line saved args (12 more fixes)
- 5 artifacts regenerated from demo/ — all 4 clean ones assemble with 0 errors; claws5=3 (known)
- 96/106 corpus — invariant holds; commit b606884 pushed

**Session B-241 (2026-03-21) — M-MACRO-BOX partial:**
- bref() fix: 18 emitter call sites; ARBNO macroized (4 ports)

## Active Milestones

| ID | Status |
|----|--------|
| M-MACRO-BOX     | ✅ `b606884` B-242 |
| M-T2-INVOKE     | ❌ next |
| M-T2-RECUR      | ❌ |
| M-T2-CORPUS     | ❌ |
| M-T2-FULL       | ❌ |

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-next | `asm-t2` | M-T2-INVOKE |
| J-next | `jvm-t2` | TBD |
| N-next | `net-t2` | TBD |
| F-next | `main`   | TBD |
