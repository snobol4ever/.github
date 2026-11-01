# JVM-SPEED-NOTES -- what moved snobol4jvm's instruction counts, what did not, and how it was measured (hq_jvm, 2026-10-31)

Basis: CEO-2035, `perf stat -e instructions:u` (user instructions retired by the whole process, JIT and collector threads included), median of 3 runs, `util_instr_count.sh` for the
fleet's numbers. The box was idle or lightly loaded; an instruction count does not move with load, a wall clock does. The table of the 23 SnoBench kernels is `JVM-BENCH-TABLE.md`.

## Landed (the empty program, user instructions)

| change | where | empty program | note |
|---|---|---|---|
| start | | 16.7 G | the AppCDS archive already in use |
| the grammar's EBNF compiled with the namespace (instaparse builds a parser from its compiled map in 1 ms, from the text in 180-200 ms, and it was built twice) | snobol4jvm cd4470c | 11.6 G | 47,716 parse comparisons over ALL.sno, 0 differ |
| the JIT waits four times as long, `-XX:CompileThresholdScaling=4` | harness ba1396e (launcher) | 6.6 G | long loops 6 percent cheaper, wall unchanged |
| the program runs on a thread sized from its declared stack, error 246 on overflow | snobol4jvm 164477c, harness ea0f2f2 | n/a | correctness row, not speed: depth 90 -> 50,000+ |
| RETURN, FRETURN, NRETURN and END are thrown constants, not `ex-info` (which reads the whole Java stack trace) | snobol4jvm 4cd6529 | n/a | fib(24) 281.9 G / 22.2 s -> 26.5 G / 2.16 s; 5000-deep 40.8 G / 3.8 s -> 13.7 G / 1.3 s |
| huge methods compiled, `-XX:-DontCompileHugeMethods` | harness a1b70ff (launcher) | 6.4 -> 6.2 G | arithmetic loop -15 percent instructions, -33 percent wall |

## Landed 2026-10-31 (harness a1b70ff): huge methods compiled

`-XX:-DontCompileHugeMethods`: HotSpot never compiles a method over 8,000 bytecodes, and `operators/INVOKE` (a `case` of every builtin) is one, so the hottest function of the engine ran
in the bytecode interpreter (19 percent of all CPU in the Interpreter frame, called from `INVOKE.doInvoke`). With the flag, on the same jar and launcher flags:

| program | instructions | wall (box under load) |
|---|---|---|
| empty | 6.4 G -> 6.2 G | 1.20 s -> 1.09 s |
| 20k pattern loop | 23.3 G -> 22.6 G | 3.01 s -> 2.60 s |
| 700k arithmetic loop | 73.8 G -> 62.7 G (-15 percent) | 9.85 s -> 6.59 s |
| 300k pattern loop | 135.8 G -> 115.4 G (-15 percent) | 17.3 s -> 12.0 s |

## Landed 2026-10-31 (snobol4jvm 4cd6529): a SNOBOL4 return does not read a stack trace

`perf record -g` on fib(19): 73.6 percent of the CPU in libjvm.so, the top symbols `Method::line_number_from_bci`, `CompressedReadStream::read_signed_int`, `StackTraceElement::fill_in`,
`Throwable::get_stack_trace_elements`, called from `runtime/dispatch-special!` -> `clojure.core/ex-info` -> `elide-top-frames` -> `Throwable.getOurStackTrace`. Every RETURN raised an `ex-info`, which
reads and decodes the stack trace of the whole recursion so far (dozens of Java frames per SNOBOL4 level). The four signals now throw a preallocated `ExceptionInfo`. Final numbers through the launcher
(instructions): fib(24) 281.2 G -> 24.7 G, fib_recur kernel 274 G -> 17 G of work, summed work of the 23 kernels 392 G -> 121 G (jar/sbl 2,411 -> 744 times, jar/csnobol4 469 -> 145 times). The other
`ex-info` sites (about 100, mostly errors: `{:snobol/error n}`) are rare paths; a program that loops on SETEXIT errors would pay the same price per error and is the next place to look.

## Tried and rejected (do not retry without a new reason)

- `-XX:TieredStopAtLevel=1` (C1 only): empty program 3.7 G, but a long arithmetic loop 33.5 s against 12.6 s and 265 G against 150 G.
- `-XX:CompileThresholdScaling` 8, 16, 32: empty 5.5 G, 5.3 G, 5.6 G, but the 300k pattern loop takes 10.9 s, 12.9 s, 12.7 s against 10.1 s at 1 and 4.
- `--engine vm`: within 4 percent of `interp` (the default) on two programs; the README's "Transpiler / Stack VM / JVM code" columns are API backends, and the bytecode backend only compiles the
  statement dispatch (every body is still `EVAL!` through an `IFn`), so it is no shortcut.
- `env/reference` and `snobol-set!` using the symbol as it stands instead of `(symbol (name x))`: 75.2 G against 75.1 G on the arithmetic loop, 25.4 against 25.4 on the pattern loop. Noise. The JIT
  already removes that allocation.
- A membership gate in `EVAL!` that sends a symbol no special clause names straight to the last clause (the 16 `(equal op ...)` tests skipped, behaviour identical): 64.8 G -> 61.9 G (-4.5 percent) on the
  arithmetic loop, nothing on the pattern loop. Real but small; not landed. Patch kept by the session as `dropped_eval_gate.patch`: the set is `#{pattern-constant ? . at-op $ = ?= & SEQ *}` plus the subscript meta, the
  two unused-operator maps and non-symbol heads, and the last clause moves verbatim into a helper.
- Preallocated signal exceptions for RETURN/FRETURN, tried on the snoflake tictactoe workload (2026-10-31, earlier): no gain, 38.9 s against 37.6 s. It was the wrong workload: on recursion (fib) it is the whole cost. Measure the lever on a workload that exercises it.

## What the cost is made of (6f91618 and later)

- Start-up of an empty program, board launcher shape: bare JVM 0.06 G, bare Clojure runtime 4.2 G, the rest the engine (namespace loads from the AOT jar: instaparse.core 184-304 ms, env 80-112 ms, grammar was 514 ms
  and is 7 ms) and the C2 compiler threads (about 7 G before the scaling flag).
- Source parsing: 22 lines of mixed_workload take 129-164 ms cold (6-7 ms a line), about 1 ms a line warm: instaparse's GLL parser. About half of the extra cost of a tiny program, never the whole of it; the
  run phase of a kernel (92-302 ms for arith_loop, mixed_workload, pattern_bt) is as large.
- Per-operation cost, the hot path of a loop (perf record, below): `INVOKE` and `EVAL!`, symbol equality (`env/equal`, `Symbol.equals`, `Util.equiv`: about 10 percent), array-map scans, megamorphic
  `vtable chunks` (4 percent). The call path was the worst (fib_recur 273 G against 47 M on sbl) until RETURN stopped reading a stack trace; func_call is still about 7,000 times sbl's work on a
  millisecond kernel, which is one-time cost, not calls.

## The gprof-like profile of a JVM run, as done here (JFR and perf; async-profiler is not installed)

```
# whole process, JIT frames resolved, call graph (what showed the Interpreter frame):
/usr/lib/linux-tools-6.8.0-138/perf record -F 499 -g -o perf.data -- java -XX:+UseSerialGC -XX:CompileThresholdScaling=4 \
    -XX:+PreserveFramePointer -XX:+UnlockDiagnosticVMOptions -XX:+DumpPerfMapAtExit -jar SNOBOL4clojure-0.2.0-standalone.jar prog.sno
/usr/lib/linux-tools-6.8.0-138/perf report -i perf.data --stdio --no-children --sort symbol -g none | head -30     # self time by symbol
/usr/lib/linux-tools-6.8.0-138/perf report -i perf.data --stdio --no-children --sort dso                           # [JIT] versus libjvm (GC, compiler)
# sampled Java stacks with line numbers, aggregated inclusively by a script (JFR, in the JDK):
java -XX:StartFlightRecording=filename=x.jfr,settings=profile,jdk.ExecutionSample#period=5ms -jar ... ; jfr print --events jdk.ExecutionSample --stack-depth 80 x.jfr
```
The `perf` on the PATH is Ubuntu's wrapper and fails on kernel 6.17.0-1032; the 6.8 binary reads the same counters. Verify that a flag variant really started (perf stat hides a failed start): run it once on a
program that prints, and look at the exit code and the output.
