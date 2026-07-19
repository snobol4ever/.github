# FINDING 2026-07-19 — JCON self-host: two fixes land (pos builtin, unary-bang generator-resume); ucode pipeline blocked at yylex line-pump (@ inside resumed generator double-reads)

Session goal (Lon): jtran (JCON translator, Icon source) self-hosting under SCRIP. SCRIP base
`c313580d` (7e9e414f + PAS-SELFHOST-2 in HEAD). Corpus `fd381248`. Re-derive all counts fresh.
Two source fixes are in the sandbox tree, VERIFIED + regression-checked, but NOT committed (the
full regen + rung suite ceremony was not run — out of session budget). Diffs reproduced below so
they survive the sandbox.

## Build + merge (verified working this session)
- `bash scripts/install_system_packages.sh; rm -f scrip && make -j4 scrip && make libscrip_rt`
- do_ops.icn / interface.icn are GENERATED: compile+run `oplexgen.icn` and `interfacegen.icn`
  (standalone m4), then `python3 tools/semicolonize_icon.py raw.icn out.icn`.
- Canonical 17-module TRANSRC order (jcon-master/tran/Makefile): dump, **do_ops(gen)**, preprocessor,
  lexer, ast, parse, ir, keyword, irgen, gen_bc, gen_symbolic, gen_dot, gen_ucode, optimize,
  **interface(gen)**, bytecode, jtran_main. Compile under `SCRIP_BETA_ELIDE_OFF=1`; link `-L out
  -lscrip_rt`. Result: **0 bombs, links (≈5.0MB), rc=0.** 3 canonical pipelines from bin/jcont:
  `preproc F.icn : stdout` (ppsrc) ✓; `preproc F.icn : yylex : parse : u_gen_File -out:F` (ucode);
  bytecode adds `ast2ir : optim : bc_File` (bc_File = JVM-class stage, WONTFIX under single-unit).

## FIX 1 — missing `pos(i)` scan builtin  [src/runtime/by_name_dispatch.c, libscrip_rt]
17-module ucode run raised `** Error 5 (Undefined function or operation)` — gdb bp on
`core_runtime_error(code=5)` → `APPLY_fn(name="pos", nargs=1)` from a coexpr stage. `pos` had tab/move
siblings but no arm. Added, mirroring canonical `refs/icon-master/src/runtime/fscan.r` (function{0,1}:
succeed only when cvpos(i)==&pos). Placed just before the `match` arm (~L4719):
```c
if (!strcmp(fn,"pos") && nargs == 1 && scan_pos > 0) {
    if (!scan_subj) { *out = FAILDESCR; return 1; }
    int slen = (int)strlen(scan_subj);
    int target = (int)to_int(args[0]);
    if (target <= 0) target = slen + 1 + target;
    if (target < 1 || target > slen + 1 || target != scan_pos) { *out = FAILDESCR; return 1; }
    *out = INTVAL(target); return 1;
}
```
After rebuild `make libscrip_rt`: Error 5 gone, ucode run rc=0. (yylex's lex_yylex0 calls `pos(1)`.)

## FIX 2 — unary-bang (`!`) generator-operand resume wiring  [src/lower/lower_icon.c] ★ real codegen bug
Root-caused via MONITOR-FIRST bracketing (below). SCRIP miscompiles `!X` when X is itself a generator:
it drives only the FIRST operand value, never re-pumping X for the rest. Repro (m3):
`l:=[["a","b"],["c"],["d"]]` (bucketed), `every i := !l[3 to 1 by -1] do write(i)` → prints only `d`;
**correct is `d c a b`** (iterate l[3]=["d"], l[2]=["c"], l[1]=["a","b"]). The `!` box (IR_ITERATE)
exhausts the current value's elements then FAILS to ω instead of resuming the operand generator for the
next value. `lower_to` already does the analogous `lc_ω_to_β(to, resume_op)` ("range-exhausted resumes
the generator operand"); the bang arm (`case TT_ITERATE`) simply lacked it. Fix (L587):
```c
case TT_ITERATE: {
    IR_t * nd = build(cx, IR_ITERATE, γ, ω);
    IR_t * orr = NULL; IR_t * ee = lower(cx, (t->n > 0) ? t->c[0] : NULL, NULL, ω, &orr);
    IR_t * opβ = cx->beta;                                 /* operand's resume point (generator inside, or ω) */
    ir_operand_push(nd, orr);
    lc_γ_to(orr, nd);
    if (opβ && opβ != ω) lc_ω_to_β(nd, opβ);               /* exhausted elements -> resume operand generator */
    cx->beta = nd; *res = nd; return ee; }
```
Gated on `opβ != ω`, so plain `!L` (IR_VAR operand, no resume) is untouched. VERIFIED: repro → `d c a b`;
plain `!L` + `!L`-with-arith unchanged; Icon smoke 14/14 ×2 (m3+m4).

### Why FIX 2 matters for self-host (the chain)
`oplexgen.icn` `lexgen_reserveds()` emits the reserved-word table via
`every i := !l[10 to 1 by -1] do write("reserved_sym_tbl[...] := lex_...")`. Pre-fix, SCRIP-compiled
oplexgen emitted **ZERO** `reserved_sym_tbl[...]` lines → `do_reserveds` returned a table populated only
with `table(&null)` → EVERY keyword (procedure/record/global/…) lexed as **IDENT**. Post-fix, regenerated
do_ops.icn carries all **30** `reserved_sym_tbl["procedure"] := lex_PROCEDURE` (etc.) lines;
`do_reserveds("procedure")` returns lex_PROCEDURE and `do_reserveds("write")` fails — verified in isolation.

## Board after both fixes (fresh, this sandbox)
Icon smoke 14/14 ×2. jtran 17-module merge: 0 bombs, links, ucode run rc=0 (no Error 5). Full rung
suite NOT re-run this session (budget) — MUST run `test_icon_all_rungs.sh` before commit to confirm the
252/9/32 no-regression baseline holds.

## OPEN BLOCKER — yylex loses input lines pumping preproc (@ inside a resumed generator)  [precisely bracketed]
Post-both-fixes, ucode still yields empty `.u1/.u2` (rc=0). Bracket by pipeline length (m3 AND m4,
mode-INDEPENDENT — so NOT the cursor's m4-only blocker B):
- `preproc:stdout` (2-stage) ✓ prints all 4 lines.
- `preproc:yylex:stdout` (3-stage) ✓ yields lex_TOK records.
- `preproc:yylex:parse:stdout` (4-stage) ✗ EMPTY.
Instrumented parse → `member(program_set, parse_tok_rec)` fails on the first token (guard never fires →
parse_program suspends nothing). Instrumented lexer (`LEX-RESERVED`/`LEX-IDENT`) → only ONE token reaches
it: `LEX-IDENT write`. Instrumented `lex_nextline` (`NEXTLINE=[...]`) → the smoking gun:
```
NEXTLINE=[#line 0 "hello_t.icn"]      <- @getline #1  (line 1)
NEXTLINE=[#line 0 "hello_t.icn"]      <- @getline #2  (line 1 AGAIN — DUPLICATE)
NEXTLINE=[   write("hello")]          <- @getline #3  (line 3 — line 2 `procedure main()` SKIPPED)
```
So `@getline` (activating the preproc coexpr) **re-reads its first value, then desyncs**, dropping
`procedure main()`. yylex activates the upstream coexpr from DEEP inside a resumed generator:
`yylex(coexpr) → "" ? { every t := lex_yylex0(getline) do {…suspend t…} }`, and `lex_yylex0` (a
`repeat`-generator that `suspend`s tokens) calls `lex_nextline → s := @getline`. The bare shallow
`@\c` in `stdout` works; the failure is the `@` executed while lex_yylex0 is being RESUMED by `every`
(same family as FIX 2, but for coexpr activation `@` rather than element-generation `!`).

### MINIMAL REPRO FOUND — R8 (≈20 lines, m3), reproduces the blocker
```icon
procedure src();  suspend "AA" | "BB" | "CC" | "DD";  end
procedure gen0(gl);
   local s;
   "" ? {                               # generator's suspend is lexically INSIDE its own scan block
      repeat {
         if pos(0) then { &subject := @gl | fail };   # pull next "line" into &subject at end
         s := tab(0);
         suspend s;
      };
   };
end
procedure consumer(gl);  local t;  every t := gen0(gl) do { write("got: ", t) };  end
procedure main();  local a, b;  a := create src(); b := create consumer(a); @b;  end
```
Prints `got: AA` FOREVER (should be AA BB CC DD). The `@gl` re-reads src's first value on every generator
resume; src never advances.

### Discriminators (pin the trigger to: `&subject := @` INSIDE a `s ? {}` scan block in a resumed generator)
- R9 = R8 with the `"" ?` wrapper REMOVED (`&subject := @gl` at generator top level) → **WORKS** (AA BB CC DD).
- R10 = R8 with `cur := @gl` (plain local, no `&subject`, no scan) → **WORKS**.
- R1 depth-3 shallow chain ✓; R2 depth-2 deep pump ✓; R5 `@gl` inside `"" ?` (consumer, not generator) ✓;
  R6 same no scan ✓; R7 generator pumps coexpr driven by `every`-in-scan, but suspend NOT inside gen0's
  own scan ✓.
=> Necessary combination: a GENERATOR whose `suspend` sits inside its OWN `s ? {}` scan block, which does
`&subject := @coexpr`. On resume, the scan environment is mis-restored (subject reset) AND the pumped
coexpr fails to advance (re-reads its prior/first value). This is exactly lex_yylex0's shape
(`"" ?`-less at top, but the `repeat` body runs under yylex's `"" ?`… NOTE: in the real code the scan
block `"" ?` is in YYLEX, and lex_yylex0 runs *inside* that every-body — so the generator whose suspend
is inside a scan is lex_yylex0 driven under yylex's `"" ?`; R8 collapses the two procs into one, which
still triggers). NEXT: fix the interaction of `s ? {}` (IR_SCAN save/restore of &subject/&pos) with a
generator suspend that crosses it, and/or the coexpr-activate (`@`) resume when executed under a
suspended scan frame. gdb on m3 with R8: watch &subject/&pos and src's coexpr cursor across the second
`@gl`.

### CONCRETE ROOT-CAUSE LEAD (verified read-only, this session)
`grep scan_subj|scan_pos src/runtime/rt/rt_coexpr.c` → **empty**: the coexpr switch does NOT save/restore
SCRIP's scan state, and that state is a set of **GLOBALS** (`scan_subj`/`scan_pos`/`scan_depth`/`scan_stack`
in by_name_dispatch.c, driven by ICN_SCAN_PUSH/POP). Real Icon makes `&subject`/`&pos` **per-co-expression**.
So the R8/yylex shape breaks because: gen0 runs a live `"" ?` (scan_depth++, scan_subj set); its `suspend`
exits the scan body WITHOUT executing the leave/POP (non-local exit), so the global scan state stays gen0's;
on resume the generator re-enters and `&subject := @gl` activates src while the global scan cursor is in an
inconsistent state — and `@gl` returns src's first value again (src not advanced). Two things to fix, likely
together: (1) make scan state per-co-expression (save/restore scan_subj/scan_pos/scan_depth on every coexpr
switch in rt_coexpr.c, or move them into the coctx), and (2) ensure a generator `suspend` that crosses a
scan body preserves/restores the scan frame on resume (IR_SCAN enter/leave vs suspend). Start with (1) — it
is a clear correctness gap on its own and is the smallest change that could fix R8.

### Fix-shape hypotheses for the blocker (unverified)
Family = "coexpr activation `@` inside a RESUMED generator does not advance the activated coexpr
(re-reads the prior value)." Candidate roots: (a) the generator-resume path restores/replays the
`@`-call's activation record instead of continuing past it (a β-wiring gap on IR_CORET/activate akin to
FIX 2's IR_ITERATE gap); (b) `&subject`/`&pos` (per-coexpr keyword state) save-restore across the `@`
switch interacts with lex_yylex0's suspend so the resumed generator re-enters the pos(1) branch and
re-pulls; (c) `every EXPR do BODY` where BOTH EXPR (lex_yylex0) and BODY (yylex) suspend — nested
generator drive mis-sequences the inner `@`. Start by checking IR_CORET / coexpr-activate β-wiring in
lower_icon.c the same way TT_ITERATE was found lacking `lc_ω_to_β`.

## Repro pack (rebuild from this doc; /tmp dies with sandbox)
`hello_t.icn` = `procedure main()\n   write("hello")\nend`. rr.icn (bang repro, FIX 2 proof), r1/r2/r5/
r6/r7 (rule-outs) — bodies inline above / trivially re-derivable. parse_probe.icn, lexer_probe.icn =
the corpus modules + the stderr probes quoted above.

## Commit ceremony NOT done (next session)
Two edits (`by_name_dispatch.c` pos, `lower_icon.c` bang) still need: rebuild + regen artifacts
(`util_regen_*_s_artifacts.sh`, `update_icon_bench_asm.sh` — FIX 2 touches codegen), full
`test_icon_all_rungs.sh` (confirm 252/9/32, zero regressions), commit with identity
`git config user.name "LCherryholmes"` / `lcherryh@yahoo.com`, push, then `scripts/handoff_status.sh`.
Update GOAL-JCON-IN-SCRIP.md LIVE CURSOR (correct blocker B characterization: the parse-stage failure
is mode-INDEPENDENT and is this yylex line-pump bug, distinct from the m4 computed-descr layer).
Authors: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
