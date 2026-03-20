# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `asm-backend` B-217 — M-EMITTER-NAMING: execute renames per EMITTER_NAME_GRID.tsv
**HEAD:** `646e7dd` B-216
**Milestone:** M-EMITTER-NAMING ⚠ WIP
**Invariants:** 106/106 C · 26/26 ASM

**⚠ CRITICAL NEXT ACTION — Session B-218:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-backend
apt-get install -y libgc-dev nasm && make -C src
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh    # must be 106/106
CORPUS=$CORPUS bash test/crosscheck/run_crosscheck_asm.sh # must be 26/26

# THE WORK — read EMITTER_NAME_GRID.tsv in .github first
# cat /home/claude/.github/EMITTER_NAME_GRID.tsv
#
# EMITTER_NAME_GRID.tsv is the naming law for all four backends.
# It has a Status column: rename | extract | add | done
# Work top to bottom through Status=rename rows first, then extract, then add.
# Each row shows Canon name (what it should be) and Notes (what it currently is).
# After all renames: make -C src, 106/106+26/26, regenerate artifacts, commit.
# Milestone M-EMITTER-NAMING fires when all four backends match the grid.
```

---

## Last Session Summary

**Session B-217 — M-EMITTER-NAMING audit and naming grid:**
- Cloned snobol4corpus (was missing). Verified 106/106 C + 26/26 ASM hold at HEAD 646e7dd.
- Full audit of all four emitters: every symbol, typedef, #define, static var, static fn.
- Produced EMITTER_NAME_GRID.tsv (94 rows) committed to .github — this IS the naming law.
- Grid has 7 columns: Concept | Canon | C | ASM | JVM | NET | Status | Notes
- Status values: done=already correct, rename=wrong name exists, extract=inlined needs factoring out, add=missing entirely.
- Key renames still needed: NET pat_uid_early→uid_ctr, NET scan_prog_vars→collect_vars, NET scan_fndefs→collect_fndefs, NET stmt_in_any_fn→stmt_in_fn, JVM collect_functions→collect_fndefs, ASM emit_asm_*→emit_*, ASM emit_body→emit_stmt, C byrd_named_pat_reset→named_pat_reset, C emit_fail_node→emit_fail, C emit_abort_node→emit_abort.
- No source files were modified this session (audit only — prior edit to emit_byrd_asm.c was rolled back in discussion).
- M-EMITTER-NAMING remains ⚠ WIP.


## Last Two Session Summaries

**Session B-216 — M-EMITTER-NAMING source naming complete across all four backends:**
- Full prefix strip: all `asm_`, `jvm_`, `net_`, `byrd_` private prefixes removed from all four emitter files. Only extern-visible entry points (`asm_emit`, `jvm_emit`, `net_emit`, `byrd_emit_*`) retain prefixes.
- Concept-class rename pass: `current_fn→cur_fn`, `out_col→col`, `MAX_BSS→MAX_VARS`, `JVM/NET_NAMED_PAT_MAX→NAMED_PAT_MAX`, all name-buffer constants→`NAME_LEN`, `ucall_uid→call_uid`, `extra_bss→extra_slots`, `ucall_bss_slots→call_slots`, `prog_strs→str_table/StrEntry`, `prog_flts→flt_table/FltEntry`, `prog_labels→label_table`, `MAX_PROG_*→MAX_*`, `ASM_NAMED_MAXPARAMS→MAX_PARAMS`.
- Duplicate `safe_name` definition removed (dead code from rename).
- 106/106 C + 26/26 ASM held throughout. HEAD `646e7dd`.
- M-EMITTER-NAMING remains ⚠ WIP: generated output Greek port labels not yet done.

**Session B-215 — Segfault fixed; C backend renamed; M-EMITTER-NAMING still ❌:**
- Segfault root cause: triple-push bug in cap-var tree-walk (`emit_byrd_asm.c` ~line 4004) — unguarded `e->children[0]` on leaf nodes. Fix: removed redundant explicit pushes, kept n-ary loop only.
- All three artifacts (beauty/roman/wordcount) regenerated and assemble clean. Committed `6f96ff7`.
- C backend rename complete: `snoc_emit→c_emit`, `sym_table→vars`, `sym_count→nvar`, `E()→C()`. Committed `fd09e01`.
- **Audit at session end revealed M-EMITTER-NAMING is NOT complete**: ASM/NET/JVM static internals still carry per-backend prefixes. PLAN.md corrected.

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
