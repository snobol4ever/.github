# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `asm-backend` B-214 — M-EMITTER-NAMING: naming audit (step 2)
**HEAD:** `7d7f9e8` B-213
**Milestone:** M-EMITTER-NAMING ❌ — 106/106 C ✅ restored; naming audit not yet started
**Invariants:** 106/106 C · 26/26 ASM

**⚠ CRITICAL NEXT ACTION — Session B-214:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-backend
apt-get install -y libgc-dev nasm && make -C src
git clone https://github.com/snobol4ever/snobol4corpus ../snobol4corpus 2>/dev/null || true
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh               # must be 26/26

# Naming audit — compare across all 4 emitters:
#   - Entry points: c_emit? / asm_emit? / jvm_emit ✓ / net_emit ✓
#   - Variable registries: jvm_var_register/net_var_register — C/ASM equivalent?
#   - Named-pat registries: jvm_named_pat_register/net_named_pat_register — C/ASM equiv?
#   - UID functions: asm_uid/jvm_pat_node_uid/net_pat_uid_early — normalize to *_uid()
#   - Output macros: A()/J()/N()/B() — document or rename
# → 106/106 C + 26/26 ASM hold → M-EMITTER-NAMING fires
```

---

## Last Two Session Summaries

**Session B-213 — 106/106 C restored; E_IDX/E_INDR flat-tree fixes; scripts relative paths:**
- Root cause: emit_cnode.c E_IDX included children[0] (array) in subscript keys AND as first arg — so keys[0] was the array descriptor not the index. Fixed: children[0]=array, children[1..]=subscripts.
- emit_assign_target rewritten to use PP_EXPR/build_expr throughout (same single-emitter pattern as ASM/JVM/NET) — eliminates dead emit_expr() calls in lvalue path.
- E_INDR lvalue: dropped stale children[1] fallback.
- All test/crosscheck/*.sh scripts: hardcoded /home/ paths → $TINY/../snobol4corpus relative. No symlinks.
- 106/106 C + 26/26 ASM. HEAD 7d7f9e8.

**Session B-212 — PIVOT to M-EMITTER-NAMING; E_INDR flat-tree fix:**
- Fixed emit.c E_INDR: stale children[0]/children[1] sentinel from pre-M-FLAT-NARY binary tree.
- 100/106 → 102/106 C (014/015 indirect assign PASS). 4 remain: array/table/roman.
- HEAD 6d3cba9.

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
