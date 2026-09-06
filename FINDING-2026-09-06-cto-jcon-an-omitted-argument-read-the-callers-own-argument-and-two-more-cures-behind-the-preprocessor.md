# FINDING 2026-09-06 cto — Jcon, defect two: an omitted argument read the caller's own argument, a `break` inside `case` fell through, and a call with omitted arguments returned `&null`

Row: `flip-jcon-compiler-jtran` (CEO-359/360, Lon's word: *"maybe CTO should take the JCON compiler"*). Defect ONE (mutually
recursive generators) is hq_B's, landed at SCRIP `dd148e2cf`. This FINDING is defect TWO: with the cycle cure in, the
preprocessor stage of the SCRIP-built 17-module `jtran` emitted 75 bytes against the icont-built oracle's 58. Three cures
landed on origin/main on top of `dd148e2cf`: SCRIP `c1233069b`, `76c29d53e`, `76d64253e` (measured as `c5a557b87`/`5d9cfe5d6`/`b6aa82c00` before two rebases onto a moving origin; the fast proofs were re-run on the pushed tree, binary 17:44:50). Measured on incremental `make`,
`RT_OPT=-O0`, scrip and `libscrip_rt.so` both rebuilt after every pull (CEO-355), every witness cut from iconx v9.5.25a.

## The claim

The preprocessor stage of `jtran` now matches the oracle byte for byte in both modes (58 bytes, `#line 0 "t1.icn"` then the
three source lines, each once), and the row's own end-to-end criterion passes that stage for the first time and is red on the
next one (the symbolic stage, 0 bytes against 3376). None of the three cures is Jcon-specific; each is an engine defect that
Jcon's preprocessor happened to exercise on its first three lines of input.

## The technique, because it is the answer to Lon's question about sync-stepping Jcon

hq_B handed over two symptoms behind a pipeline of co-expressions and a generator cycle. The stage that produced them,
`preprocessor.icn`, is a plain generator, so I drove it directly: `every write(preprocessor("t1.icn", predefs()))`, no
co-expression, no cycle, two files. Both symptoms reproduced. Then the sync-step: add `write(&errout, …)` of the four state
variables at the top of `preproc_sync_lines`, run the identical instrumented source under iconx and under SCRIP, diff the two
traces. The first differing line named the defect in both cases (a call that never happened; a parameter holding the wrong
value). A witness of under twenty lines followed from the trace, and ASM-DIFF settled the mechanism. The same technique
then found the next divergence (the lexer stage) in one step: drive `yylex` over three lines through a co-expression,
print the tokens, diff against the oracle's twelve.

## THE HEADLINE — an omitted trailing argument to a generator read the caller's own argument (`76c29d53e`)

`preproc_scan_text()` is called with its one parameter `done_set` omitted. Under SCRIP `done_set` held `"t1.icn"`, the first
parameter of the calling procedure `preprocessor(fname, …)`, so `if /done_set then suspend preproc_sync_lines()` never fired
and the `#line` generator was never entered; the directive appeared once, after the file, with the wrong number.

Mechanism: every Icon callee's prologue calls `rt_icn_zframe_args_install(base, nparams, nlocals)`, which copies `nparams`
descriptors out of the shared staging array `g_call_args` — regardless of how many the call passed. Two of the call openers
(`rt_proc_call_open_det0`, `rt_proc_call_open_det1`) nulled the slots above `nargs` themselves; the generator-path opener
(`rt_proc_call_open_det`) and the lexical by-name path did not. So a generator callee with an omitted argument read whatever
the previous call had staged in that slot. Here the previous call was `preprocessor("t1.icn", …)` itself.

This is the class hq_B asked to see named on its own: **a caller's value appearing in a callee**, a wrong answer in any
language that shares this prologue, never a crash. Cure: `rt_proc_call_prologue_lex`, which every opener reaches, nulls
`[nargs, nparams)` before anything reads the staging array. Nine lines of witness (`om.icn`: plain call, `suspend` call, inside
a scan, inside a loop, two omitted, one of two omitted, `return` of a generator) match iconx on every row in both modes.

## A `break` inside a `case` branch continued the loop (`c1233069b`)

The duplicated `write("hello");` line. `preproc_scan_text` leaves the `repeat` of its string-literal case with `break break`
through a `case`; SCRIP honoured one level, so the line was yielded inside the `repeat` and again after the outer `while`.
Reduced: a plain `break` inside any `case` arm did not exit the enclosing loop (`next` did). Mechanism: the break lowered to
`&null → __break_result := &null → loop-exit` and handed its parent the `&null` variable node as its result, whose γ edge *was*
the exit; `case` (like any parent that assigns an arm's value) re-pointed that edge to its own result assignment. `next` was
already correct because its result is an `IR_GOTO`, which `icn_arm_result` refuses to rewire. The break now ends in the same
shape: a trailing `IR_GOTO` to the exit is its result node on the plain path, the scan-restoring path, and the `break expr` path.

## A call with omitted arguments returned `&null` (`76d64253e`)

Found behind the first two: `procedure q7(a) return "y" end` returned `&null` when called as `q7()` and `"y"` as `q7(9)`, and only
from a caller in the per-node carve regime. Mechanism: `bb_call_proc_staged` carries two copies of the general call path; the
one selected under that regime ended every call in the s112 *named* epilogue twins (`11be98d9b`: the SNOBOL4 contract — result
by the function's name, save set restored), which an Icon `return` never fills; the sibling copy already used the bare epilogue.
The callee's γ exit already moves the returned value into `rdi:rsi` before the landing (confirmed in the asm), so the bare
epilogue is correct for a lexical callee. Cure: a callee registered at emit time as lexical (`det_idx_z >= 0`, which the arm
already requires to reach its opener) takes the bare epilogue; an unknown or dynamically-scoped callee keeps the twins.

## Measured

| arm | before | on `b6aa82c00` (binary 17:27:07) |
|---|---|---|
| jtran `preproc t1.icn : stdout`, both builds | 75 bytes vs 58 (hq_B) | **58 = 58**, both modes; zero GENHOST warnings |
| row DONE-WHEN | red on preproc | passes preproc, **red on the symbolic stage** (0 vs 3376 bytes) |
| omitted-argument witnesses (`om`, `z4`, `z5`, `z7`) | 4 of 7 rows wrong | **all match iconx, both modes** |
| Icon master (`board_icon_master.sh`) | 696/702 | **697/702 both modes**, watermarks held |
| Icon ladder | 626/634 | 626/634 (the 8 = inherited rung-41 `rt_chdir_getenv`, `rt_delay`, `rt_getch_getche_kbhit_on_eof`, `rt_loadfunc_refusal`, both modes) |
| Prolog ladder | 533/568 (hq_C on origin) | 533/568 |
| SNOBOL4 corpus (`test_corpus_snobol4.sh`) | m3 1854/1855 · m4 1854/1855 (origin) | **m3 1854 · m4 1854**, FAIL=1 by CEO-340 |

`make test` halts on `test_gate_raku_paren_call_passes_its_arguments.sh`, a nondeterministic segfault compiling `until.raku`
that reproduces on the parent lowerer in 2 of 4 runs (rebuilt with the parent's file, run, restored) — inherited, named to the
ceo, not cured here. The three commits were rebased once more before the push; the boards above are on `b6aa82c00`.

## The next divergence, already located

The lexer stage: `yylex` over the three source lines emits twelve tokens under iconx and one under SCRIP, then hangs. The
sync-step trace shows the resumption after the first `suspend` seeing `pos=10 len=0`: the subject installed by
`&subject := lex_nextline(getline)` inside the scan-less inner generator reverts to the enclosing `"" ? {}` subject of `yylex`
when the OUTER generator's suspend is resumed, while the position survives. Eleven-line witness `v6_twolevel.icn` (iconx
`ab cd ef`, SCRIP `ab`); controls (inner alone, outer without a scan) match. Pre-existing: identical on `dd148e2cf` without
these three commits. Same family as the FREE row `icon-jcon-scan-scan2-hang-nested-scan-break-next`.

## Disposition

Landed at SCRIP `c1233069b`, `76c29d53e`, `76d64253e` on origin/main. The row stays claimed by the cto; its DONE-WHEN is unchanged
and red on the symbolic stage. Not taken: the newline-termination question (Lon's absolute rule, CEO-363, raised to Lon by the ceo).
