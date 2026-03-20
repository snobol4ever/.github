# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `asm-backend` B-216 — M-EMITTER-NAMING: strip remaining per-backend prefixes from ASM/NET/JVM static internals
**HEAD:** `fd09e01` B-215
**Milestone:** M-EMITTER-NAMING ❌ — C backend done (B-215); ASM/NET/JVM static internals still prefixed
**Invariants:** 106/106 C · 26/26 ASM

**⚠ CRITICAL NEXT ACTION — Session B-216:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-backend
apt-get install -y libgc-dev nasm && make -C src
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must be 106/106
CORPUS=$CORPUS bash test/crosscheck/run_crosscheck_asm.sh  # must be 26/26

# M-EMITTER-NAMING remaining work — strip per-backend prefixes:
#
# ASM (emit_byrd_asm.c):
#   asm_out       → out
#   bss_slots[]   → vars[]  (bss_count→nvar, bss_add→var_register, bss_reset→var_reset)
#   asm_uid_ctr   → uid_ctr, asm_uid()→uid()
#   asm_named[]   → named_pats[]  (asm_named_count→named_pat_count, etc.)
#   emit_asm_node → emit_pat_node
#
# JVM (emit_byrd_jvm.c):
#   jvm_out            → out
#   jvm_vars[]         → vars[]  (jvm_nvar→nvar, jvm_var_register→var_register)
#   JvmNamedPat        → NamedPat
#   jvm_named_pats[]   → named_pats[]  (jvm_named_pat_count→named_pat_count, etc.)
#   JvmFnDef           → FnDef
#   JvmDataType        → DataType
#   jvm_emit_pat_node  → emit_pat_node
#   jvm_emit_stmt      → emit_stmt
#
# NET (emit_byrd_net.c):
#   net_out              → out
#   net_vars[]           → vars[]  (net_nvar→nvar)
#   NetNamedPat          → NamedPat
#   net_named_pats[]     → named_pats[]  (net_named_pat_count→named_pat_count, etc.)
#   net_named_pat_register → named_pat_register
#   net_emit_one_stmt    → emit_stmt
#
# After each file: make -C src, 106/106+26/26, then regenerate artifacts.
# Commit: "B-216: M-EMITTER-NAMING — ASM/NET/JVM static internals prefix strip complete"
```

---

## Last Two Session Summaries

**Session B-215 — Segfault fixed; C backend renamed; M-EMITTER-NAMING still ❌:**
- Segfault root cause: triple-push bug in cap-var tree-walk (`emit_byrd_asm.c` ~line 4004) — unguarded `e->children[0]` on leaf nodes. Fix: removed redundant explicit pushes, kept n-ary loop only.
- All three artifacts (beauty/roman/wordcount) regenerated and assemble clean. Committed `6f96ff7`.
- C backend rename complete: `snoc_emit→c_emit`, `sym_table→vars`, `sym_count→nvar`, `E()→C()`. Committed `fd09e01`.
- **Audit at session end revealed M-EMITTER-NAMING is NOT complete**: ASM/NET/JVM static internals still carry per-backend prefixes (asm_out, bss_slots, bss_count, asm_uid, net_out, net_vars, NetNamedPat, jvm_out, JvmNamedPat, jvm_named_pats, etc.). The rename was only partially executed in B-214. PLAN.md corrected.

**Session B-214 — M-EMITTER-NAMING Option B planned; ASM/NET/JVM rename attempted but incomplete:**
- Full naming audit across all 4 backends. Decision: Option B — drop per-backend prefix from all `static` internal names; file scope handles collision; identical names enable instant cross-backend correlation.
- ASM: `bss_slots→vars`, `bss_count→nvar`, `bss_add→var_register`, `asm_named→named_pats`, `asm_uid→uid`, `emit_asm_node→emit_pat_node`, `asm_emit_body→emit_stmt`, `asm_out→out`, etc.
- NET: `NetNamedPat→NamedPat`, `NetFnDef→FnDef`, `net_vars→vars`, `net_emit_one_stmt→emit_stmt`, `net_out→out`, etc.
- JVM: `JvmNamedPat→NamedPat`, `JvmFnDef→FnDef`, `JvmDataType→DataType`, `jvm_vars→vars`, `jvm_emit_stmt→emit_stmt`, `jvm_out→out`, removed self-referential `#define` aliases.
- 106/106 C + 26/26 ASM hold. NOT YET COMMITTED — beauty_prog.s artifact diverged (missing ret_γ/ret_ω .bss slots for named patterns). Root cause: Python uid→u rename script over-replaced. Needs diagnosis before commit.

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
