# FINDING 2026-09-05 seat12 — the three CAPTURE-TARGET-IN-A-SCOPE-BOUNDARY xfails are cured: a function-call capture target reuses the existing SNO$WANTNM/NRETURN machinery, not a new one

**Seat:** seat12 (hq_T lane) · **Mode:** FLEET-16 · **Tree:** SCRIP `47f99b0c9`+this commit · corpus `94585e051`+this commit
**Task:** `snobol4-xfail-class-capture-target-in-a-scope-boundary-3-entries`
**Instrument:** `/home/resources/x64/bin/sbl -bf` (the oracle, via `lib_oracle_flags.sh`), both SCRIP modes.

## 1. The blocking condition named in the GOAL was already resolved

The task warned this class is adjacent to the `04d1b9cd2` lambda-deferred-target regression on
`user_function_len_defer_branch_6` and said not to start until hq_B's cure landed. Checked first: hq_B's
cure (`89eb03ef6`) is already on `origin/main` (pulled this session). That mechanism (`*(expr)` deferred
capture targets, AST shape `TT_DEFER`) is a wholly separate branch from this task's class (`TT_FNC`
capture targets) in `lower_snobol4.c`'s `TT_CAPT_COND_ASGN`/`TT_CAPT_IMMED_ASGN` case — read both, they
share no state. Not a moving node; safe to proceed.

## 2. What the three witnesses need (RUN THE ORACLE, NEVER ASSUME, per GOAL)

`GOAL-SNOBOL4-BB.md`, cited by the xfail reasons, no longer exists (retired into GOAL-SNOBOL4-100.md;
no surviving "GZ#5" definition). The FATAL's real, unchanged text (`lower_snobol4.c:372`) is `"capture
target in a runtime-built pattern is not a simple variable"`. All three witnesses are the classic
SPITBOL `NRETURN`-as-NAME idiom (manual p.133, STORE example): a DEFINE'd procedure sets its own
name-variable to `.X` (name-of X) and returns via `:(NRETURN)` instead of `:(RETURN)`, so the caller
receives a NAME datum pointing at X, not X's value. Using such a call as a capture target
(`LEN(1) . S()`) means: call S(), get back NAME(X), assign the captured substring into X.

## 3. The cure — one new branch, reusing an existing, already-proven mechanism

Capture-target lowering already special-cases `TT_INDIRECT` (`$(expr)`) by evaluating the target
expression at runtime to get a NAME and wiring it straight into `SNO$PBC` (pattern-build-capture).
Ordinary assignment (`TT_ASGN`) already has a *general* fallback for a `TT_FNC` LHS (e.g. `STORE() = 43`,
witness 2's own first statement): call `SNO$WANTNM` (sets the pre-existing global `rt_g_want_name = 1`,
consumed by `rt_nret_fix` at the call's NRETURN exit) immediately before evaluating the call, so the call
yields its NAME undereferenced instead of collapsing to a value. Capture-target lowering had the
`TT_INDIRECT` half of this but never the `TT_FNC` half — it fell straight into `sno_fatal`. The fix adds
exactly that missing branch, mirroring the existing `TT_ASGN` general-LHS shape (`lower_snobol4.c`, 8
lines added after the `TT_INDIRECT` arm):

```c
} else if (tgt && tgt->t == TT_FNC) {
    IR_t * wl = lc_build(cx->g, IR_LIT_STRING, NULL, ω); IR_LIT(wl).sval = (char *) "";
    IR_t * wm = lc_build(cx->g, IR_CALL, NULL, ω); IR_LIT(wm).sval = (char *) "SNO$WANTNM";
    lc_γ_to(wl, wm); ir_operand_push(wm, wl);
    IR_t * nv = NULL; IR_t * en = sx_lower(cx, tgt, NULL, ω, &nv);
    lc_γ_to(wm, en);
    es = sx_lower(cx, t->c[0], NULL, ω, &vs);
    lc_γ_to(kt, wl); lc_γ_to(nv, es); nl = nv;
}
```

No new global, no new runtime primitive, no new BID — `SNO$WANTNM`/`rt_g_want_name`/`rt_nret_fix`
already existed and are already exercised by production code (general assignment, and the `.`-name-of
operator over a general form). This is reuse, not new machinery.

## 4. Evidence — three-way agreement, both modes, all three witnesses

| witness | SCRIP m3 | SCRIP m4 | `sbl -bf` (oracle) | `ALL.ref` |
|---|---|---|---|---|
| `user_function_len_capture_1` | `g=A` | `g=A` | `g=A` | `g=A` |
| `user_function_len_capture_replace_1` | `DUMMY=43` / `DUMMY=AB` | same | same | same |
| `user_function_len_capture_branch_2` | `B dummy=AB` | same | same | same |

Byte-identical across all four columns, all three witnesses. Witness 2 exercises both forms in one
program: `STORE() = 43` (plain assignment, the pre-existing general path) and `LEN(2) . STORE()`
(pattern capture, this fix) — both correct.

## 5. Control arms (SHARED-NODE VERDICT SCOPE, per the task GOAL)

Icon watermark: `entries=754 · m3 PASS=599/601 · m4 PASS=599/601 · ast 153/153` — unmoved, as expected
(`lower_snobol4.c` is SNOBOL4-only).

SNOBOL4 master: `total=1859 m3_pass=1778 m3_fail=25 m3_crash=1 m3_hang=2 · m4_pass=1778 m4_fail=20
m4_crash=1 m4_hang=2`. **Not FAIL=0** — but this population is pre-existing and untouched by this fix,
proven two ways: (a) `git stash` on `lower_snobol4.c` alone, rebuild, re-run of all 10 then-visible
named entries reproduced byte-identical errors/hangs on the pre-fix binary; (b) the new branch is
reachable only when a capture target parses as `TT_FNC` — a shape the whole SNOBOL4 master uses in
exactly the three entries this row closes (grep-verified against `ALL.sno`) — so it cannot change
codegen for any other entry: every entry that used to compile still compiles by the identical path it
always used. See §6 for what this population actually is.

## 6. Adjacent finding, NOT fixed here, flagged to hq_T — out of this row's scope

All 27 non-passing entries are named `test_parser_*`, and all 27 carry `modes=UNKNOWN` in
`corpus/tests/snobol4/ALL.csv` (27 of 27 accounted for: 25 FAIL + 2 HANG). Their `.ref` files are
`--dump-ast` dumps (e.g. `(STMT :subj (TT_FNC F (TT_VAR X)))`), not program output — parser-ladder
fixtures whose `modes` column should read `ast` and never travelled, so the harness's
unknown-defaults-to-run rule executes them and diffs runtime output against an AST dump, guaranteed to
mismatch regardless of whether the parser itself is correct. This is exactly the failure class
`test_gate_modes_declaration_travels.sh` (wired today, 2026-09-05) exists to catch, but that gate did
not flag this population — worth hq_T checking why (possibly absorbed before the gate landed, or its
csv-sibling detection has a gap for this tree/these entries). Not investigated further; sent to hq_T via
`s4e_msg.sh ask` rather than silently absorbed into this row or silently dropped.

## 7. Corpus changes

`corpus/tests/snobol4/ALL.xfail`: removed the three now-cured entries' banner+reason blocks
(`user_function_len_capture_1`, `user_function_len_capture_replace_1`,
`user_function_len_capture_branch_2`) — matched and edited by NAME, per hq_T's own prior retraction that
the leading sequence number in this file is positional decoration, not load-bearing.

`corpus/tests/snobol4/ALL.csv`: flipped the `xfail` column 1→0 for the same three rows by hand, not via
`util_build_master_suite.py --reindex` — that tool refuses (rc=2) with ~30 unrelated, unacknowledged
loose families present in the tree right now, and acknowledging/absorbing those is a different row's
call, not mine to make as a side effect of a three-row promotion. No other column changed: the three
programs' text is untouched, so no feature-flag derivation changes — only the xfail boolean this fix
actually moved.
