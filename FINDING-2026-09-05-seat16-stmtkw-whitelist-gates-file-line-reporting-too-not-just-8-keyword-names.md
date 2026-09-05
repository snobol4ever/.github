# FINDING 2026-09-05 seat16 — `sno_kw_is_stmt`'s 8-keyword whitelist is the SAME gap behind
# seat04's file/line-reporting bug (hq_C) AND this row's &DUMP defect (hq_T) — one root cause, two lanes

**Seat:** seat16 · **Mode:** FLEET-16 (hq_T lane) · **Tree:** SCRIP `2aff59c4c`, corpus `ead8fcb8d`
**Row:** `snobol4-xfail-class-unimplemented-feature-gaps-ord-and-dump-2-entries` (parked)

## 1. This answers seat04's open question directly

`FINDING-2026-09-05-seat04-system-fn-protection-errors-carry-no-file-line-rt-stmt-enter-never-fires.md`
(hq_C lane) measured, under gdb, that `rt_stmt_enter` never fires for a `DATA('ITEM(X)')` repro, leaving
`g_file`/`g_line`/`g_stno` at their initial values so every `core_runtime_error` diagnostic prints
`(0) : ERROR NNN -- ...` instead of the real `file(line)`. It closed with: *"Whether it's conditionally
emitted only for programs that reference certain keywords... is not yet determined."*

It is conditional, and here is the exact gate: `src/lower/lower_snobol4.c:33-41`, `sno_kw_is_stmt()` +
`sno_scan_stmtkw()`. Before lowering statements, the whole AST is scanned for a `TT_KEYWORD` node whose
name (case-folded) is one of exactly eight strings: `stno stcount lastno line lastline file lastfile
stlimit`. Only if one is found does the lowerer emit the per-statement `"SNO$STMT"` hook
(`lower_snobol4.c:2350-2369`) that drives `rt_stmt_enter` at runtime (confirmed live via gdb breakpoint +
backtrace: `rt_stmt_enter <- try_call_builtin_by_name_bl("SNO$STMT") <- rt_call_arr_impl <- JIT-emitted
call`, and separately by grepping mode-4's plain-text `.s` for the hook's presence/absence). seat04's
`DATA('ITEM(X)') / OUTPUT = 'unreached' / END` repro references none of the eight names, so the scan finds
nothing, `g_sno_uses_stmtkw` stays 0, and the hook is never emitted for that program — not "skipped at
runtime", never generated in the first place, exactly as seat04's `.s`-grep already showed.

## 2. Why this is bigger than either row

This row's own defect (`keyword_19`/&DUMP, see task ledger) hit the identical gate from a different
direction: a program using `&DUMP` but none of the eight names also gets zero statement tracking, so
`&DUMP`'s "dump of keyword values" section prints `&STNO = 0 &LINE = 0 &STCOUNT = 0` etc. regardless of
what actually executed. Fixed narrowly here by adding `"dump"` to the whitelist (SCRIP commit `dc50554a9`)
— correct for &DUMP specifically, but it is the same shape of patch seat04 declined to make for DATA/
DEFINE/OPSYN, and it will recur for every future consumer of `g_file`/`g_line`/`g_stno`/`g_stcount` that
isn't one of the two known cases: **every `core_runtime_error`/`kwb_error` call site is such a consumer**,
because the diagnostic format is `file(line) : ERROR NNN -- msg` unconditionally, whether or not the
*source program* ever mentions `&STNO`/`&LINE`/etc. A whitelist keyed on "does the SOURCE reference these
keyword names" cannot cover "might this statement raise a runtime error" — nearly any statement can, so
the true trigger condition the whitelist is approximating is closer to "always", not "these eight names."

## 3. Not fixed here, on purpose, for the same reason seat04 named

Making `sno_kw_is_stmt` return true unconditionally (or widening it to also fire on any use of a function/
operation that can runtime-error) is a real architecture and performance question, not a one-line follow-
up: `SNO$STMT` is a per-statement call through the generic by-name dispatcher (`rt_call_arr_bl` ->
`try_call_builtin_by_name_bl`, a string-keyed switch), and this project's whole culture around `RT_OPT`/
`-O2`/perf multiples (`.github/RULES.md` § FACT RULES) means "make it unconditional" is a real cost that
wants measuring, not assuming — and it touches every SNOBOL4 program compiled, in both modes, which is a
far wider blast radius than either the DATA-protection row or this &DUMP row. Whether the right fix is
(a) unconditional emission, (b) widening the scan to also trigger on any `core_runtime_error`-reachable
construct (DATA/DEFINE/OPSYN protection checks, arithmetic errors, etc. — a much longer and harder-to-
enumerate list than eight keyword names), or (c) something else (e.g., a cheap register-resident counter
synced to the globals only lazily, right before a diagnostic prints) is a call for whoever owns codegen
performance, not this FINDING.

## 4. Repro reference

Same repro as seat04's FINDING (`DATA('ITEM(X)')` / `OUTPUT = 'unreached'` / `END`) reproduces the file/
line gap; `keyword_19` (this row's corpus witness, `corpus/tests/snobol4/ALL.xfail`) reproduces the &DUMP
angle. Both trace to the same eight-name check.

**Routed, not silently absorbed:** flagging to hq_C (owns seat04's row/lane) and hq_T (owns this row) —
whoever mints the general fix should read both FINDINGs together, not just one.
