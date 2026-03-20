# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)
→ Full session history: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `asm-backend` B-220 — M-ASM-RUNG8
**HEAD:** `5999162` B-219
**Milestone:** M-ASM-RUNG8 ❌
**Invariants:** 100/106 C (6 pre-existing) · 26/26 ASM

**⚠ CRITICAL NEXT ACTION — Session B-220:**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git pull --rebase origin asm-backend
apt-get install -y libgc-dev nasm && make -C src
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh    # 100/106 (6 pre-existing)
CORPUS=$CORPUS bash test/crosscheck/run_crosscheck_asm.sh # 26/26

# Sprint M-ASM-RUNG8: REPLACE/SIZE/DUPL assertion harness 3/3 PASS via ASM backend
# See PLAN.md milestone dashboard for next ❌ milestone in sequence
```

---

## Last Session Summary

**Session B-219 — M-EMITTER-NAMING complete: C backend merged into emit_byrd_c.c:**
- Merged `emit.c` + `emit_byrd.c` into single `emit_byrd_c.c` — now peers with `emit_byrd_asm.c`, `emit_byrd_jvm.c`, `emit_byrd_net.c`.
- All four backends now in one file each with canonical names: `var_register()`, `collect_vars()`, `collect_fndefs()`, `next_uid()`, `escape_string()`, `emit_stmt()`, `emit_pat_node()`, `NamedPat`, `FnDef`, `DataType`, `vars[]`, `nvar`.
- Removed all `byrd_emit_*` / `byrd_cond_*` externs — now static internals.
- `B()` aliased to `C()` for pattern emitter heritage; `ARG_MAX` aliased to `FN_ARGMAX`.
- Clean build. 100/106 C (6 pre-existing, unchanged) + 26/26 ASM hold. HEAD `5999162`.


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
