# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `asm-backend` B-213 — M-EMITTER-NAMING: fix remaining 4 C backend failures + naming audit
**HEAD:** `6d3cba9` B-212
**Milestone:** M-EMITTER-NAMING ❌ — 102/106 C (4 remain: 091/092 array, 093 table, 100 roman); naming audit not yet started
**Invariants:** 102/106 C · 26/26 ASM

**⚠ CRITICAL NEXT ACTION — Session B-213:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin HEAD:main
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must be 102/106
bash test/crosscheck/run_crosscheck_asm.sh               # must be 26/26

# Step 1: diagnose remaining 4 C failures: 091/092 array, 093 table, 100 roman
#   ./sno2c <test>.sno > /tmp/t.c && compile and run, diff vs .ref
#   Likely root: E_IDX lvalue (array subscript assign) still uses old children[] layout

# Step 2: fix emit.c E_IDX and any other stale children[1] references

# Step 3: naming audit — compare across all 4 emitters:
#   - Entry points: c_emit? / asm_emit? / jvm_emit ✓ / net_emit ✓
#   - Variable registries: jvm_var_register/net_var_register — C/ASM equivalent?
#   - Named-pat registries: jvm_named_pat_register/net_named_pat_register — C/ASM equiv?
#   - UID functions: asm_uid/jvm_pat_node_uid/net_pat_uid_early — normalize to *_uid()
#   - Output macros: A()/J()/N()/B() — document or rename

# Step 4: 106/106 C + 26/26 ASM → M-EMITTER-NAMING fires
```

---

## Last Two Session Summaries

**Session B-212 — PIVOT to M-EMITTER-NAMING; E_INDR flat-tree fix:**
- Diagnosed C backend emit.c: E_INDR used stale `!children[0]` / `children[1]` sentinel from old binary tree (pre-M-FLAT-NARY). New tree: both `$X` and `*X` use `children[0]=operand`.
- Fixed `emit_expr` E_INDR case and `iset()` lvalue case in emit.c.
- 100/106 → 102/106 C (014/015 indirect assign now PASS). 4 remain: array/table/roman.
- Milestone pivoted from M-ASM-RUNG11 to M-EMITTER-NAMING per Lon direction.
- HQ updated: PLAN.md M-FLAT-NARY marked ⚠, M-EMITTER-NAMING added. HEAD `6d3cba9`.

**Session B-211 — PROTOTYPE + ITEM + VALUE + array default-fill (partial):**
- Added `_b_PROTOTYPE`, `_b_ITEM`, `_b_VALUE` to `snobol4.c`. Fixed `_b_ARRAY` default-fill.
- ITEM lvalue emitter added but broken (duplicate register loads). rung11: 2/7.
- Invariants: 100/106 C · 26/26 ASM. HEAD `15e818b`.

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
