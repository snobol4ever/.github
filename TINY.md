# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `asm-backend` B-211 — M-ASM-RUNG11: PROTOTYPE + array default-fill + item() + beauty.sno depth guard
**HEAD:** `3133497` B-210
**Milestone:** M-ASM-RUNG9 ✅ 5/5 · M-ASM-RUNG10 ✅ 8/8 · M-ASM-RUNG11 ❌ (0/7 → in progress B-211)
**Invariants:** 100/106 C · 26/26 ASM

**⚠ CRITICAL NEXT ACTION — Session B-211:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 100/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
# Step 1: PROTOTYPE + default-fill + item() + VALUE added to snobol4.c (B-211 in progress)
# Step 2: fix ITEM lvalue emitter path in emit_byrd_asm.c (item(arr,i)=val)
# Step 3: re-run rung11 → target 7/7 → M-ASM-RUNG11 fires
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/rung11
# Step 4: fix beauty.sno segfault — add recursion depth guard in prog_emit_expr
# Step 5: regenerate artifacts/asm/beauty_prog.s
# Step 6: commit + update PLAN.md + append to SESSIONS_ARCHIVE.md + push
```

---

## Last Two Session Summaries

**Session B-210 — M-ASM-RUNG9 fires:**
- Bug A (LGT NULVCL): `inc_init()` re-registered LGT/LLT/LGE/LLE/LEQ/LNE with `_w_*` wrappers overwriting `SNO_INIT_fn`'s correct `_b_*` versions. Fix: removed 6 duplicate `register_fn` calls from `inc_init()`. rung9 5/5 ✅.
- Bug C (rung11 E_IDX read): `prog_emit_expr(key, -16)` clobbered array descriptor. Fix: push arr before key eval. Tests 1110/001–004 pass.
- Remaining rung11 blockers going into B-211: PROTOTYPE not registered; `_b_ARRAY` default-fill ignored; `item()` not registered; VALUE needs verification.
- beauty.sno segfault: pre-existing deep recursion in `prog_emit_expr` — depth guard needed.

**Session B-209 — 7 root-cause fixes:**
- `expr_has_pattern_fn` whitelist; `_func_hash` case-insensitive; `E_KW` emitter uppercase; CONC2 fast-path guard; E_IDX read/write children[0]/[1] fix; prescan OOB + null guard.
- Runtime: LGT/LLT/LGE/LLE/LEQ/LNE registered in SNO_INIT_fn.
- Result: rung8 2/3 · rung9 4/5 · 100/106 C ✅ · 26/26 ASM ✅.

---

## Active Milestones (next 5)

| ID | Status | Notes |
|----|--------|-------|
| M-ASM-RUNG11 | ❌ 0/7 | PROTOTYPE + default-fill + item() + VALUE — B-211 |
| M-ASM-LIBRARY | ❌ | Gates on RUNG11 |
| M-SC-CORPUS-R2 | ❌ | do_procedure body emission fix (sc_cf.c) — F-211 |
| M-JVM-CROSSCHECK | ❌ | 88/92; word1/cross remain — J-207 |
| M-NET-R1 | ❌ | Sprint N-204 in progress |

Full milestone history → [PLAN.md](PLAN.md)

---

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-211 | `asm-backend` | M-ASM-RUNG11 |
| F-210 | `main` | M-SC-CORPUS-R2 |
| J-207 | `jvm-backend` | M-JVM-CROSSCHECK |
| N-204 | `net-backend` | M-NET-R1 |
| D-156 | `net-perf-analysis` | M-NET-PERF |

Per RULES.md: `git pull --rebase` before every push. Update only your row in PLAN.md NOW table.
