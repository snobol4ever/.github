# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `asm-backend` B-212 — M-ASM-RUNG11: fix ITEM lvalue emitter + PROTOTYPE/VALUE verification
**HEAD:** `15e818b` B-211
**Milestone:** M-ASM-RUNG11 ❌ (2/7 — ITEM lvalue emitter path broken; PROTOTYPE/VALUE need verification)
**Invariants:** 100/106 C · 26/26 ASM

**⚠ CRITICAL NEXT ACTION — Session B-212:**

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
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh $CORPUS/rung11
# current: 2/7 — see B-211 summary for root causes

# Step 1: fix ITEM lvalue emitter in emit_byrd_asm.c
#   The B-211 ITEM lvalue block has duplicated register loads — rewrite it
#   to exactly mirror the E_IDX write path (lines ~3757-3822): push arr,
#   push key, eval RHS into [rbp-32/24], then load regs from stack and call stmt_aset.
#   Also skip prescan for ITEM lvalue (add to the has_eq guard list at ~line 3653).

# Step 2: verify PROTOTYPE works (1110/005, 1112/002, 1113/005)
# Step 3: verify VALUE works (1115/005, 1116/002)
# Step 4: re-run rung11 → target 7/7 → M-ASM-RUNG11 fires

# Step 5: fix beauty.sno segfault — add recursion depth guard in prog_emit_expr
#   Search for the deepest call chain on beauty.sno line 788 (APPLY_FN_N S_AL truncated)
#   Add: static int emit_depth = 0; if (++emit_depth > 500) { --emit_depth; return 0; }

# Step 6: regenerate artifacts/asm/beauty_prog.s (once segfault fixed)
# Step 7: commit + update PLAN.md + append SESSIONS_ARCHIVE + push
```

---

## Last Two Session Summaries

**Session B-211 — PROTOTYPE + ITEM + VALUE + array default-fill (partial):**
- Added `_b_PROTOTYPE`, `_b_ITEM`, `_b_VALUE` to `snobol4.c` and registered in `SNO_INIT_fn`.
- Fixed `_b_ARRAY` default-fill (second arg was ignored; now fills all slots).
- Added ITEM lvalue emitter path in `emit_byrd_asm.c` — but register loads are duplicated/wrong; needs rewrite to mirror E_IDX write path exactly.
- Also: slimmed TINY.md (155KB→4KB) and DOTNET.md (57KB→3KB); added L2 size discipline rule to RULES.md.
- rung11: 0/7 → 2/7. Invariants: 100/106 C ✅ · 26/26 ASM ✅. HEAD `15e818b`.

**Session B-210 — M-ASM-RUNG9 fires:**
- Bug A: `inc_init()` duplicate LGT/LLT/LGE/LLE/LEQ/LNE registrations removed. rung9 5/5 ✅.
- Bug C: E_IDX read fix — push arr before key eval to avoid clobber. 1110/001–004 pass.
- Remaining rung11 blockers: PROTOTYPE/item()/default-fill/VALUE (addressed in B-211).

---

## Active Milestones (next 5)

| ID | Status | Notes |
|----|--------|-------|
| M-ASM-RUNG11 | ❌ 2/7 | ITEM lvalue emitter fix + PROTOTYPE/VALUE verify — B-212 |
| M-ASM-LIBRARY | ❌ | Gates on RUNG11 |
| M-SC-CORPUS-R2 | ❌ | do_procedure body emission fix (sc_cf.c) — F-211 |
| M-JVM-CROSSCHECK | ❌ | 89/92 (J-208 progress) |
| M-NET-R1 | ❌ | 74/82 NET — ARB backtrack SEQ-omega bug (N-205 WIP) |

Full milestone history → [PLAN.md](PLAN.md)

---

## Concurrent Sessions

| Session | Branch | Focus |
|---------|--------|-------|
| B-212 | `asm-backend` | M-ASM-RUNG11 |
| F-210 | `main` | M-SC-CORPUS-R2 |
| J-208 | `jvm-backend` | M-JVM-CROSSCHECK (89/92) |
| N-205 | `net-backend` | M-NET-R1 — fix ARB SEQ-omega ptr bug → word1-4/cross |
| D-156 | `net-perf-analysis` | M-NET-PERF |

Per RULES.md: `git pull --rebase` before every push. Update only your row in PLAN.md NOW table.
