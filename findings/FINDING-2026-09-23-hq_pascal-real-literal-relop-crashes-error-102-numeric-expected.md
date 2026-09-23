# FINDING-2026-09-23-hq_pascal-real-literal-relop-crashes-error-102-numeric-expected

## SUMMARY
Any Pascal relational comparison (`=`,`<>`,`<`,`<=`,`>`,`>=`) between two REAL-typed
operands crashes at runtime with `scrip: error 102: numeric expected / offending
value: &null`, in BOTH m3 and m4. This is a pre-existing defect (confirmed present
before this sitting's five Pascal landings; bisected by stashing all uncommitted
work and rebuilding on origin HEAD). It is not Pascal-parser-local: the identical
AST shape works correctly when the same program is written in Icon, so the fault
lives downstream of `lower()`, in shared box/emitter machinery (`bb_binop_relop.cpp`
/ `rt_jct_relop` / zeta-storage wiring) that CLAUDE.md's Architecture section marks
as the cto's node -- not landed here for that reason.

## MINIMAL REPRO (5 lines, no `.in`, deterministic)
```pascal
program teq2;
begin
  if 1210.0 = 1210.0 then writeln('EQ') else writeln('NEQ');
end.
```
`./scrip --run` and the `--compile`+link m4 binary both die identically:
```
scrip: error 102: numeric expected
  at :0
  offending value: &null
```
Confirmed NOT specific to `=`: `1210.0 < 1211.0` and `1210.0 > 1000.0` crash the
same way. Confirmed NOT specific to literals: `var x:double; x:=1210.0; if
x=1210.0 then ...` crashes identically. Confirmed NOT specific to the value 1210:
reproduces with any real pair tried.

## WHAT IS RULED OUT
- Not caused by this sitting's five Pascal commits (SwapEndian, the Delphi
  `Result` pseudo-var + string-relop, the single-char-const char-tag fix, the
  `{$if}` conditional-compilation feature, or the uncommitted real-target
  assignment coercion) -- reproduces on origin HEAD with all of this sitting's
  uncommitted work stashed and the tree rebuilt clean.
- Not a Pascal-parser/AST-shape problem: `scrip --dump-ast` on the Icon program
  `if 1210.0 = 1210.0 then write("EQ") else write("NEQ")` and on the Pascal repro
  above produce byte-identical `(TT_EQ (TT_FLIT 1210) (TT_FLIT 1210))` trees, and
  the Icon one runs correctly (`EQ`) while the Pascal one crashes -- so the two
  languages reach `lower_binop`/`lower()`'s shared TT_EQ case with the same input
  and diverge downstream of it, which CLAUDE.md's own "language identity stops at
  lower" invariant says should not happen.
- Not int-vs-real dispatch inside `rt_jct_relop_impl` itself in the abstract:
  reading that function directly, `relop_num_coerce()` explicitly accepts
  `IS_REAL_fn(v)` (line ~5703) and the `IS_REAL_fn(L)||IS_REAL_fn(R)` branch
  (~5773) does the right double compare -- the function's C source looks correct
  for this case, which is why this reads as an ARGUMENT-MARSHALLING or
  zeta-storage-OFFSET bug feeding it garbage, not a logic bug in the comparison
  itself.

## WHAT DIFFERS, ASM-DIFF-FIRST (m4, `--compile`, same rung: two LIT_REAL boxes
feeding one BINOP_TEST, no intervening variable)
- Pascal's `main_α:` label has NO `sub rsp` of its own before the box chain
  starts writing to `[rsp+NNN]` offsets (confirmed on two separate Pascal repros,
  one with zero locals and one with a declared `double` local -- same shape both
  times). Icon's `main_α:` label opens with `sub rsp, 320` before anything else.
  Whether this is Pascal's normal (different, still-correct) zeta-storage
  strategy -- the outer `main:` label's own `sub rsp, 65544` may already cover
  the whole procedure's needs statically -- or the actual fault, was NOT
  resolved before this session's budget on it ran out; flagging the asymmetry
  rather than asserting it is the cause, since Pascal's 246-entry master suite
  clearly gets frame layout right for the overwhelming majority of programs.
- The INTEGER sibling (`1210 = 1210`) gets an inline fast-path
  (`cmp rax,rcx; je ...`) before ever reaching `call rt_jct_relop`
  (`bb_binop_relop.cpp`'s `!_.op_num_real` guard); the REAL case has no such
  fast path and goes straight to the call. Did not get far enough to prove
  whether the fast-path's absence is itself load-bearing for correctness here,
  or just a missing optimization.

## LIKELY BLAST RADIUS
This is a real, load-bearing ISO 7185 construct (`real = real`, `real < real`,
etc. are ordinary, common code) -- worth checking whether it explains more than
one currently-red fpc_tests witness before assuming it is narrowly scoped.
`tbs_tb0012` (fpc_tests) is a confirmed witness: it prints its real accumulator
correctly (`1.2100000000000000e+003`) but then crashes on `if stemp<>1210.0`.

## NEXT ACTOR
Needs the box-wiring/zeta-offset computation for `BINOP_TEST` walked against a
real operand pair specifically (ASM-DIFF-FIRST step 3: gdb breakpoint at
`rt_jct_relop`, inspect what `rdi/rsi/rdx/rcx` actually hold vs what the two
preceding `LIT_REAL` boxes stored) -- this is shared emitter code per CLAUDE.md
Architecture (`src/templates/bb/bb_binop_relop.cpp`, box wiring), so routed to
cfo rather than landed from this lane.
