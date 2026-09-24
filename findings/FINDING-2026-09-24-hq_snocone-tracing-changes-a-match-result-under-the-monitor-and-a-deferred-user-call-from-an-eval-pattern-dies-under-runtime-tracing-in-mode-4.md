# FINDING 2026-09-24 hq_snocone -- tracing changes a pattern-match result under the monitor, and a deferred user call from an EVAL-built pattern dies under runtime tracing in mode 4

**Measured by hq_snocone on SCRIP `669054c29` (origin/main), corpus `e37f7e483`, RT_OPT=-O0, incremental `make`, box load 9-38.**
Found by Lon's method (transpile, SPITBOL first, then `monitor_run.sh --oracle`) on the first two bootstrap parsers that pass
step 2: the monitor's own MONITOR-SAFE check refuses every parser because **the traced run answers `Parse Error` where the
untraced run prints the tree**. This is the defect that blocks Lon's step 3 for all seven parser_*.sc, and it is not in a parser.

## W1 -- the parsers (mode 3, the compile flag)

    scrip --transpile bootstrap/{global,case,assign,match,counter,stack,tree,ShiftReduce,tdump,gen,qize,semantic,omega,trace}.sc bootstrap/parser_rebus.sc > parser_rebus.sno
    printf 'function main()\n  OUTPUT := 1\nend\n' > fn.reb
    scrip --run parser_rebus.sno < fn.reb            # (FUNC_DECL (TT_VAR main) (PARAMS) (LOCALS) (RB_INITIAL) (BODY (ASSIGN ...)))
    scrip --trace --run parser_rebus.sno < fn.reb    # Parse Error   (after 2634 **** records)

The same for `parser_snocone.sno` on `tests/snocone/ladder/prog/hello.sc` (tree untraced, `Parse Error` traced). `SCRIP_GC_STRESS=1`
and `=5` on the UNTRACED run print the tree, so it is not a latent collector fault that the hooks' allocations trigger; spelling a
traced PATTERN value without allocating changes nothing; `SCRIP_NV_MEMO=0` changes nothing.

## W2 -- twenty lines, mode 4, no compile flag: a deferred user call inside an EVAL-built pattern dies at the callee's entry when the RUNTIME traces

```
	DEFINE('Shift(t,v)')	:(SE)
Shift	OUTPUT = 'shift ' t ' ' v
	Shift = .dummy	:(NRETURN)
SE
	DEFINE('shift(p,t)')	:(sE)
shift	shift = EVAL("p . thx . *Shift('" t "', thx)")	:(RETURN)
sE
	P = shift('ab', 'TT_X')
	'abc' ? P	:S(Y)F(N)
Y	OUTPUT = 'S'	:(E)
N	OUTPUT = 'F'
E
END
```

    scrip --compile -o ta6.s ta6.sno && as --64 -o ta6.o ta6.s && gcc -no-pie -o ta6.bin ta6.o -L out -lscrip_rt -Wl,-rpath,out -lm
    ./ta6.bin                              # shift TT_X ab / S          (SPITBOL: the same)
    SCRIP_TRACE=2000000000 ./ta6.bin       # ****1  Shift()  then SIGSEGV rc 139
    SCRIP_TRACE=2000000000 scrip --run ta6.sno   # mode 3: shift TT_X ab / S -- correct

gdb: the fault is inside `n16_define_bx` (Shift's first statement) with r9 = 0x70001000 (an address inside the rtccb block,
reloaded from rtccb+48 after every runtime call), rcx pointing nowhere useful and rdx holding code bytes. The hook is called
from the runtime's slim call prologue (`src/runtime/rt/rt.c` `if (g_trace_budget != 0) sno_trace_call(p->name)`), i.e. in C,
between the argument binding and the transfer into the emitted body. Remove the deferred user call (`EVAL("p . thx")`, ta8) and
the traced run is correct, so the shape is: **a user function entered from a deferred pattern element while tracing is on**.
The parser's `shift` is exactly `EVAL("p . thx . *Shift(...)")`, so every parser hits it at the first shift.

## W3 -- an artefact worth knowing before bisecting by budget: the runtime compiler reads the LIVE budget as its compile-time trace flag

```
	DEFINE('G(v)')	:(GE)
G	G = .dummy	:(NRETURN)
GE
	DEFINE('mk(t)')	:(ME)
mk	mk = EVAL("'a' . thx . *G(thx)")	:(RETURN)
ME
	p = mk('')
	'abc' ? p	:S(Y)F(N)
Y	OUTPUT = 'S ' thx	:(E)
N	OUTPUT = 'F'
E
END
```

    SCRIP_TRACE=1 scrip --trace --run ta4.sno     # scrip: error 22: Undefined function called  at ta4.sno:8
    scrip --trace --run ta4.sno                   # S a   (correct)

`emit.cpp` decides `op_mon_stmt_tap` and the lowerers decide `trace_wanted()` from `g_trace_budget != 0`; an EVAL compiled after a
finite budget ran out is compiled UNTRACED inside a TRACED program, and its deferred call to a DEFINE'd function then fails as
undefined. A budget bisection over the parser therefore never shows the tree at any N (below the flip it dies of W3, above it of W1),
which cost this sitting an hour: the boundary it finds (event 735, `shift = PATTERN` in parser_rebus.sno) is where W3 stops masking
W1, not a cause.

## What was ruled out, and what was cured beside it

- The collector (stress 1 and 5 untraced: trees). The pattern spelling allocation in `trace_spell_value` (made static: no change,
  reverted). The name-value memo. The zero-K planner rule (a separate defect, cured at SCRIP `669054c29`, which is why W2 can be
  run at all now).
- Cured on the way, each with its receipt in the commit: SIZE(CHAR(1)) read 2 (`d874c2cae`); a traced value with newlines broke
  the monitor's stripper (`f4a7ab5ef`); a failing match in expression position inside a function leaked its subject slot
  (`669054c29`, gate witness w5 in both forms).

## Where this goes

The node is the trace protocol between the runtime's proc-call path and emitted code (`rt.c` prologue/epilogue hooks, `bb_define.cpp`
lines 212-222 and 348-356, the runtime compiler's use of `g_trace_budget`), reached by every frontend under `--trace` and by the
monitor for every language. It is the ceo's monitor coordination and the cto's spine; hq_snocone has the witnesses and can run them
on demand. Until it is cured, `monitor_run.sh --oracle` refuses every bootstrap parser as NOT MONITOR-SAFE, and Lon's step 3 is
blocked for all seven; steps 1, 2 and 4 are not.
