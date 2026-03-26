# REPO-snobol4x.md

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.**

→ Rules: [RULES.md](RULES.md) · Beauty plan: [BEAUTY.md](BEAUTY.md) · History: [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md)

---

## NOW

**Sprint:** `main` — B-292 (JVM nchildren fix ✅; L_io_end missing-label WIP)
**HEAD:** `acbc71e` B-292
**B-session:** Fixed JVM segfault: fi < e->nchildren guard in DATA ctor loop (emit_byrd_jvm.c:1156). beauty.sno now emits 872K-line beauty.j without crash. Jasmin still fails: `L_io_end has not been added to the code`. Root cause fully diagnosed (see CRITICAL NEXT ACTION). 106/106 ✅.
**Invariants:** 106/106 ASM corpus ALL PASS ✅

## §BUILD
```bash
cd snobol4x && bash setup.sh   # installs deps, builds all drivers
```

## §TEST
```bash
# ASM corpus (must be 106/106 before any work):
bash run_crosscheck_asm_corpus.sh
# JVM corpus:
bash run_crosscheck_jvm_rung.sh
# NET corpus:
bash run_crosscheck_net.sh   # must be 110/110
```

**⚡ CRITICAL NEXT ACTION — B-293 (L_io_end missing-label fix):**

**Root cause diagnosed:** `jvm_emit_fn_method` for `output_` (fn5) sweeps source statements until it hits `fn->end_label`. `output_->end_label` is NULL (DEFINE has no goto, next stmt also has no goto). So body scan runs unbounded — absorbs `io_end` label, emitting it as `Lf5_io_end` inside the output_ method instead of `L_io_end` in main(). Meanwhile `goto L_io_end` in main() references the unseen label → Jasmin error.

**Fix strategy:** When `fn->end_label` is NULL, terminate body scan at the next function entry label in source order. Add to `jvm_emit_fn_method` body loop (line 4153), after the existing end_label check:
```c
/* When end_label is NULL, stop at next fn entry */
if (in_body && !fn->end_label && s->label && strcasecmp(s->label, entry) != 0) {
    for (int fi2 = 0; fi2 < jvm_fn_count; fi2++) {
        const JvmFnDef *fn2 = &jvm_fn_table[fi2];
        const char *e2 = fn2->entry_label ? fn2->entry_label : fn2->name;
        if (e2 && strcasecmp(s->label, e2) == 0) { in_body = 0; break; }
    }
    if (!in_body) break;
}
```
Note: earlier attempt added this to the wrong loop (main() pass at 4451 instead of fn-method pass at 4153). Apply to `jvm_emit_fn_method` loop only.

**After fix:** Jasmin assembles beauty.j → run JVM beauty bootstrap → fire M-BEAUTIFY-BOOTSTRAP.
    ...
}
```
Then: beauty.j completes → Jasmin assembles → JVM beauty subsystem ladder begins.

**B-286 summary:**
- D-001: SPITBOL is primary compat target (CSNOBOL4 FENCE issue disqualifies it).
- D-002: DATATYPE() = UPPERCASE always. SPITBOL lowercase is an ignore-point.
- D-003: Test suite case-insensitive on DATATYPE output.
- D-004: .NAME = third dialect (DT_N). Matches SPITBOL observable behaviour.
- D-005: Monitor swapped — SPITBOL is participant 0 (primary oracle).
- Single-line fix in emit_byrd_asm.c (arg staging always -32): resolves M-BUG-IS-DIALECT,
  M-BUG-SEMANTIC-NTYPE, M-BUG-TDUMP-TLUMP, M-BUG-GEN-BUFFER. 19/19 beauty PASS.
- DECISIONS.md created in .github.
C backend: ☠️ DEAD — removed from matrix. 99/106, sno2c fails on word*/pat_alt_commit. Not maintained.

---

## Last Two Sessions (3 lines each)

**B-292 (2026-03-25) — JVM nchildren segfault fixed; L_io_end diagnosed; 106/106:**
(1) Fixed SIGSEGV in emit_byrd_jvm.c:1156 — fi < e->nchildren guard prevents OOB access on tree(t,v,n,c) DATA ctor with <4 args. beauty.sno now emits 872K-line beauty.j.
(2) Jasmin fails: L_io_end missing. Root cause: output_->end_label NULL → fn body scan unbounded → absorbs io_end top-level label → emits as Lf5_io_end inside output_ method.
(3) Fix strategy documented in CRITICAL NEXT ACTION. HEAD `acbc71e`.

**B-291 (2026-03-25) — BSS heap fix; Sprint M5 unblocked; 106/106:**
(1) Heap-allocated 4 large BSS statics (named_pats/str_table/call_slots/lit_table). BSS 8.4MB→2.0MB.
(2) sno2c -asm/-jvm beauty.sno no longer segfaults. beauty_asm_bin builds, runs 10 lines then Parse Error.
(3) TRACE_SET_CAP 64→256. Oracle trace: 92,601 events. HEAD `309a2f9`.
