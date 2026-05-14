# GOAL-ICON-BB-JCON.md — Icon ir-run FAIL triage

**Repo:** one4all + corpus + .github
**Prereq:** GOAL-ICON-BB-NATIVE ✅ `7efdf09a`

## Objective

Fix ir-run FAILs left after GOAL-ICON-BB-NATIVE. Steps by risk-to-reward.

## Remaining FAILs by cluster

| # | Cluster | Tests | Root cause |
|---|---------|-------|------------|
| C | Missing builtins — proc/image | rung36_jcon_args, rung36_jcon_record, rung36_jcon_lists, rung36_jcon_fncs1 | residual after IJ-3 |
| E | Missing builtins — string | rung36_jcon_endetab, rung36_jcon_prepro | `&error`/`$define` |
| H | Lex string comparison | rung36_jcon_lexcmp | upto(!cset) arg semantics |
| I | Radix literals | rung36_jcon_radix | large binary overflow |
| J | String builtins partial | rung36_jcon_string, rung36_jcon_string1 | repl/trim edge cases |
| K | Scan alternation | rung36_jcon_scan, rung36_jcon_scan1, rung36_jcon_scan2 | upto(!cset) arg semantics |
| L | &pos / &subject negative | rung36_jcon_substring | negative-index substring assignment |
| M | Keywords table | rung36_jcon_kwds | generative keywords (&features, &allocated, etc.) |
| N | Level / profsum / ck | rung36_jcon_level, rung36_jcon_profsum, rung36_jcon_ck | level() + &allocated |
| O | Output routing | rung36_jcon_htprep, rung36_jcon_meander, rung36_jcon_kross | write(fh,s) needs DT_FH |
| Q | stdin programs | rung36_jcon_parse, rung36_jcon_mindfa, rung36_jcon_mffsol | stdin fixtures |
| R | Random | rung36_jcon_random | `&random` seeding |

## Session Setup

  cd /home/claude/one4all && bash scripts/build_scrip.sh

**⚠️ BB RULE:** Every step touching a BB must first read `.github/jcon_irgen.icn`
(`ir_a_Call` + `ir_a_Ident`). Do not infer BB semantics from C source alone.

## Gates

  GATE-1  bash scripts/test_smoke_icon.sh                 # PASS=5
  GATE-2  bash scripts/test_smoke_unified_broker.sh       # PASS=23
  GATE-3  bash scripts/test_icon_ir_all_rungs.sh          # PASS >= prev
  GATE-4  bash scripts/test_icon_sm_no_ast_walk.sh        # honest PASS >= 273

## Closed steps (trail)

IJ-1..6: TT_SEQ, table keys, proc/image/indirect, math/bitwise, detab/cset, augop.
IJ-7 `b50d8180` operator dispatch + coerce (~~, to-by, ^neg, cset image). Clusters G ✅.
IJ-8 `340bccc3` bb_strrel: coerce int/real to string before strcmp.
IJ-9 `4008701c` coro_bb_scan_gen b: advance subject not resume body. rung37_scan_alt ✅.
IJ-10 `259e1aec` ICN_KW_SWAP: icn_frame_env_store + preserve lhs/rhs order. Cluster L partial ✅.
IJ-11 icn_kw_read() centralises keyword reads; type()/image() cset fixes. Cluster M partial ✅.
IJ-12 `6b20b4a2` static parent-frame fallback for recursive procs. Cluster P ✅.
IJ-13a `d2453ecc` ast_gc_clone: only GC_strdup sval for string-typed nodes (crash fix).
IJ-13b `2d5567ca` &input/&output/&errout -> INTVAL(0/1/2); read(infile:=&input) works.
IJ-14 `00cec4c3` fix coro_bb_iterate static-alias bug: z->ch (in-struct 2-byte buf) returned directly caused all put(L,!s) entries to alias same ptr → last char. GC_strdup(z->ch) each tick. Same fix in coro_value.c TT_ITERATE. mindfa/mffsol still FAIL: cset ++/--/** missing from inline interp_eval (SM_CALL_FN only); separate gap.
IJ-13c `1e4a6d7f` DT_FH=12 sentinel in descr.h; FHVAL(idx) macro; &input/&output/&errout return FHVAL; open() returns FHVAL; write/writes/read/reads/close all route via DT_FH first-arg. honest 273→274. Cluster O htprep/meander/kross still FAIL (root: while-loop/scan bug in in(), not DT_FH).

## Active steps

### IJ-13c — write(fh, s) routing (Cluster O) NEXT

htprep/meander/kross no longer crash but produce empty/wrong output.
Root: `write(outfile, s)` where `outfile := &output` is INTVAL(1).
write/writes cannot distinguish fh from plain int without a typed descriptor.

- [x] Introduce DT_FH sentinel (DT_S slen=0xFFFFFFFE ptr=slot, or new DT_ tag).
- [x] Update write/writes/read/reads/close/open to use it.
- [x] rung37_file_io.icn + .expected. GATE-1..4. Commit.

### IJ-14 — stdin programs: mindfa / mffsol (Cluster Q)

- [x] Write .stdin fixtures. GATE-1..4. Commit. (fixtures pre-existed; fixed coro_bb_iterate static-alias `00cec4c3`; mindfa/mffsol still blocked by cset ++/-- missing from inline interp_eval)

### IJ-15 — cset literal/builtin/ops + parse program (Cluster Q)

- [x] rung36_jcon_parse: already passing at session start (no code change needed).
- [x] cset literal (TT_CSET) now pushes CSETVAL via SM_PUSH_LIT_CS opcode.
- [x] cset(x) builtin added to icn_try_call_builtin_by_name.
- [x] TT_CSET_UNION/DIFF/INTER/COMPL lowered to SM_CALL_FN instead of emit_push_expr.
- [x] TK_AUGCSET_UNION/DIFF/INTER in lower_augop fast-path.
- [x] ICN_BANG_NEXT + coro_bb_iterate slen fix (CSETVAL 0xFFFFFFFF sentinel).
- [x] coro_stmt.c default delegates to bb_eval_value (unblocks mindfa/mffsol startup).
- [x] rung37_cset_ops.icn + .expected. GATE-1..4. Commit `52db8b96`.
  mindfa/mffsol still FAIL (algorithm logic; not cset infrastructure). Cluster Q partial.

### IJ-16 — &random seeding + radix literals (Clusters R, I)

- [ ] Fix &random r/w. Fix radix overflow. rung37_random_radix.icn. GATE-1..4. Commit.

### IJ-17 — level / profsum / ck (Cluster N)

- [ ] level() builtin. &allocated. XFAIL if needed. GATE-1..4. Commit.

## rung37_* test sources

| File | Step | Status |
|------|------|--------|
| rung37_proc_lookup.icn | IJ-3 | done |
| rung37_math_builtins.icn | IJ-4 | done |
| rung37_string_format.icn | IJ-5 | done |
| rung37_augops.icn | IJ-6 | done |
| rung37_coerce.icn | IJ-7 | done |
| rung37_str_relop.icn | IJ-8 | done |
| rung37_scan_alt.icn | IJ-9 | done |
| rung37_neg_pos.icn | IJ-10 | done |
| rung37_keywords.icn | IJ-11 | done |
| rung37_mutual.icn | IJ-12 | done |
| rung37_file_io.icn | IJ-13c | done |
| rung37_cset_ops.icn | IJ-15 | done |
| rung37_random_radix.icn | IJ-16 | pending |

## Done when

  ir-run PASS >= 230. Honest PASS >= 268. All rung37 tests passing. GATE-1..4 green.

## Invariants

1. GATE-1: smoke_icon PASS=5. Never regress.
2. GATE-2: broker PASS=23. Never regress.
3. GATE-3: ir-run PASS must not decrease.
4. GATE-4: honest PASS must not decrease.
5. One cluster per step, own commit.
6. New test source has matching .expected in same commit.
7. No corpus source modified to work around runtime bugs.
8. scrip Icon requires explicit `;` after every statement (non-standard vs real Icon/JCON). All rung37_*.icn must use semicolons.

## Watermark

  one4all: 6b351a91  corpus: 2ba5a92
  ir-run:  PASS=201 FAIL=34 XFAIL=30
  honest:  PASS=276 FAIL=1 ABORT=0   broker: 23/49
  NEXT: IJ-16 (&random seeding + radix literals)

---

## Missing JCON BB steps (IJ-18 onward)

Each ir_a_* procedure in jcon_irgen.icn = one Byrd Box. Status per construct:

| JCON ir_a_ | coro_bb_ | Status |
|------------|----------|--------|
| ToBy | coro_bb_to / coro_bb_to_by / coro_bb_to_by_real / coro_bb_to_nested | ✅ done |
| Alt | coro_bb_alternate | ✅ done |
| Every | coro_bb_every | ✅ done |
| Limitation | coro_bb_limit | ✅ done |
| Binop (closure/bang) | coro_bb_bang_binary / coro_bb_binop | ✅ done |
| Mutual (seq) | coro_bb_mutual | ✅ done |
| Scan | coro_bb_scan_gen | ✅ done |
| Suspend | coro_bb_suspend | ✅ done |
| Ident (!E iterate) | coro_bb_iterate / coro_bb_list_iterate / coro_bb_tbl_iterate / coro_bb_tbl_key_iterate / coro_bb_record_iterate | ✅ done |
| Not | — | ❌ missing |
| RepAlt | — | ❌ missing |
| Case | — | ❌ missing |
| Repeat | — | ❌ missing |
| Until | — | ❌ missing |
| While | — | ❌ missing |
| Create | — | ❌ missing |
| Next | — | ❌ missing |
| Break | — | ❌ missing |
| Sectionop | — | ❌ missing |
| Key (generative) | — | ❌ missing |
| ListConstructor (!L) | — | ❌ missing |
| Compound | — | ❌ missing |
| Field (generative) | — | ❌ missing |
| CoexpList | — | ❌ missing |
| Return (from suspend) | — | ❌ missing |
| Fail | — | ❌ missing |

Non-generative (handled inline in bb_eval_value — no separate BB needed):
NoOp, Global, If, Initial, Invocable, Link, Intlit, Reallit, Stringlit,
Csetlit, ProcDecl, ProcBody, ProcCode, Record, Call, Unop, Arglist.

### IJ-18 — ir_a_Not (negation-as-failure)

`!E` in negation context: succeeds (null) if E fails, fails if E succeeds.
Maps to `coro_bb_not`. No state; purely structural.

- [ ] Implement coro_bb_not in coro_runtime.c. Wire in coro_eval TT_NOT. GATE-1..4. Commit.

### IJ-19 — ir_a_RepAlt (|E repeated alternation)

`|E` — pump E to exhaustion then restart. Maps to `coro_bb_repalt`.
State: gen (the sub-box). On omega restart gen from alpha.

- [ ] Implement coro_bb_repalt. Wire in coro_eval TT_REPALT (if present) or TT_ALTERNATE path. GATE-1..4. Commit.

### IJ-20 — ir_a_While / ir_a_Until / ir_a_Repeat (loops)

`while E do B`, `until E do B`, `repeat B`.
Maps to coro_bb_while, coro_bb_until, coro_bb_repeat.
State: expr_gen, body_gen. While/Until gate on expr success/failure.
Repeat loops unconditionally.

- [ ] Implement coro_bb_while, coro_bb_until, coro_bb_repeat. Wire TT_WHILE/UNTIL/REPEAT in coro_eval. GATE-1..4. Commit.

### IJ-21 — ir_a_Case (case expression)

`case E of { C1: B1 ... Cn: Bn default: D }`.
Maps to coro_bb_case. State: expr val, current clause index, body_gen.
Compares E === clause expr; on match pumps body; on body omega tries next clause.

- [ ] Implement coro_bb_case. Wire TT_CASE in coro_eval. GATE-1..4. Commit.

### IJ-22 — ir_a_Next / ir_a_Break (loop control)

`next` — continue to next loop iteration (goto nextlabel in JCON terms).
`break E` — exit loop with value E.
Both short-circuit the enclosing loop BB.

- [ ] Implement loop-control signaling in BB context. GATE-1..4. Commit.

### IJ-23 — ir_a_Create (co-expression creation)

`create E` — creates a co-expression that generates E lazily.
Maps to coro_bb_create. State: suspended bb_node_t.
On alpha: freeze E as a bb_node_t, return co-expression descriptor.
On activate (@coexp): resume the frozen node.

- [ ] Implement coro_bb_create + co-expression activation. Wire TT_CREATE. GATE-1..4. Commit.

### IJ-24 — ir_a_Sectionop (s[i:j] generative)

`s[gen:j]` or `s[i:gen]` — generative subscript.
Maps to coro_bb_section_gen. Pumps the generative bound, yields each section.

- [ ] Implement coro_bb_section_gen. Wire TT_SECTION/PLUS/MINUS when bounds are generative. GATE-1..4. Commit.

### IJ-25 — ir_a_Key (generative keywords: &features, &allocated, etc.)

`&features` generates strings; `&allocated` generates 3 integers; etc.
Maps to coro_bb_kw_gen per keyword. Currently one-shot.

- [ ] Implement generative keyword BBs. Wire icn_kw_read generators. GATE-1..4. Commit.

### IJ-26 — ir_a_ListConstructor generative ([gen, ...])

`[1 to 3, "x"]` — list where elements may be generators.
Currently non-generative. Generative form pumps each element slot.

- [ ] Implement coro_bb_list_constructor_gen. Wire TT_MAKELIST when children generative. GATE-1..4. Commit.

### IJ-27 — ir_a_Compound generative (E1; E2; ... EN all-must-succeed)

`(E1; E2; E3)` — compound expression, all succeed or fail.
Maps to coro_bb_compound_gen when any sub-expr is generative.

- [ ] Implement coro_bb_compound_gen. Wire TT_COMPOUND generative path. GATE-1..4. Commit.

### IJ-28 — ir_a_Field generative (r.field where r is generative)

`(!L).field` — field access on generative object.
Maps to coro_bb_field_gen. Pumps object generator, yields field each time.

- [ ] Implement coro_bb_field_gen. Wire TT_FIELD when object is generative. GATE-1..4. Commit.


### IJ-29 — wire icn_bb_proc_call: replace coro_bb_suspend for all proc calls

Per JCON irgen.icn: coroutines are ONLY for `create E` / `@coexp` (co-expression feature).
Every other construct — suspend, every, while, generators — is pure BB alpha/beta.
icn_bb_proc_call already written in icon_gen_missing.c.

- [ ] In coro_eval TT_FNC user-proc path: replace `coro_bb_suspend` with `icn_bb_make_proc_box`.
- [ ] In coro_pump_proc_by_name: same replacement.
- [ ] Verify frame push only on alpha, pop only on omega/return. No double push.
- [ ] Test recursive procs (queens), suspend-with-alt (recogn), every-suspend. GATE-1..4. Commit.

### IJ-30 — rip out all swapcontext/coro_t machinery except co-expression

Once IJ-29 is verified green, delete the dead code:

- [ ] Remove proc_trampoline, gather_trampoline (no longer called for procs).
- [ ] Remove coro_t struct fields: stack, gen_ctx, caller_ctx (keep only for create/@ path).
- [ ] Remove active_coro, FRAME.suspending, FRAME.suspend_val, FRAME.suspend_do globals (dead after IJ-29).
- [ ] Remove sm_yield_to_caller (dead — only called from SM_SUSPEND_VALUE which is SM-path only).
- [ ] Keep coro_bb_suspend ONLY for the create/@ co-expression activation path.
- [ ] GATE-1..4. Commit.

### IJ-31 — fix suspend expr generator resume (the core suspend bug)

`suspend (1|2|3)` currently yields only `1` because bb_exec_stmt re-evaluates from alpha on resume.
After IJ-29/30: icn_bb_proc_call naturally fixes this — it saves the bb_node_t and pumps beta.
This step is: verify recogn, roman, and other suspend-heavy tests pass. Add rung37_suspend_gen.icn.

- [ ] Verify `suspend E|F|G` generates all values via icn_bb_proc_call. GATE-1..4. Commit.
