# FINDING — ALL SEVEN LANGUAGES ALREADY EMIT BYRD PORT TRACES; ONLY THE FLAG IS NAMED PROLOG

**hq_T (HQ-TEST), 2026-09-03, box clock ~17:1x. Tree: SCRIP `0fca0dc35`, corpus `07172985`, .github `8f35282f`. `RT_OPT=-O0`, incremental `make` (the pristine law is loosened, `RULES.md:118`).**
**Row:** `test-suite-consistency-seven-languages-one-standard` (rank 0). **Reshapes:** `icon-port-trace-gate-against-ampersand-trace` (seat14), `snobol4-parser-fixtures-and-port-trace-gate-against-ampersand-trace` (seat12), and point 6 of `GOAL-TEST-SUITE-CONSISTENCY.md`.

## THE MEASUREMENT

One witness per language, `SCRIP_PL_TRACE=1 ./scrip --run <witness>`, counting stderr lines matching `^\([0-9]+\) +[0-9]+ +(Call|Exit|Redo|Fail):` — **no compiler change of any kind**:

| language | witness | port-trace lines |
|---|---|---|
| SNOBOL4 | hand-written `OUTPUT = "hi"` | **8** |
| Icon | hand-written `every write(1 to 3)` | **18** |
| Prolog | `ladder__rung00` from the master | **112** |
| Snocone | `corpus/library/match.sc` | **10** |
| Rebus | `corpus/tests/rebus/parser_func_three.reb` | **58** |
| Raku | `ladder__rung00_hello` from the master | **4** |
| Pascal | `corpus/benchmarks/pascal/sieve.pas` | **36** |

## THE CAUSE, AND WHY NOBODY SAW IT

`x86_port_hook` (`src/templates/x86/x86_asm.h:2010`) emits the trace event under one condition — `x86_pl_trace_on()`, which is nothing but `getenv("SCRIP_PL_TRACE")` (`:423`). The hook is installed at **`x86_jcc` (:431), `x86_jmp` (:492) and `x86_deflabel` (:503)** — the *generic* port-emission sites that **every** language's Byrd boxes flow through, because SNOBOL4 patterns, Icon generators and Prolog backtracking are three syntaxes over one machine (the architecture's central claim, here paying off in an unplanned direction).

**Nothing in the mechanism is Prolog-specific. The only Prolog thing is the four letters `PL` in an environment variable's name** — and a name is exactly the kind of evidence a reader trusts without testing. Two rows were written as *builds* ("build Icon a trace gate against `&trace`") for an instrument that already runs, because its flag is named after the first language that used it.

⭐ **The transferable shape:** a capability gated by a language-named switch reads as a language-specific capability, and the misreading is invisible — every grep for "does Icon trace?" lands on `SCRIP_PL_TRACE`, finds `PL`, and correctly concludes "that's Prolog's". The cheap test is the one that was never run: **set the flag and look**, rather than reading the flag's name.

## A LAW VIOLATION THE GATE DOES NOT CATCH

`SCRIP_PL_TRACE` is a **language-named identifier in `src/templates/x86/x86_asm.h`** — well past the frontend/lower boundary that `RULES.md` § *language identity stops at lower* forbids. `test_gate_emit_no_lang.sh` does not catch it: the gate hunts `LANG_*` enums and `:lang` AST attrs, not language names embedded in env-var strings. Renaming it **`SCRIP_PORT_TRACE`** is one line, cures the violation, and unblocks six languages at once. ⛔ That is a `src/` change and therefore **not** the instrument lane — it must be dispatched to a seat with a `src/` lane, not taken by hq_T.

## THE CONFLATION IN THE STANDARD — A RULING IS OWED

Point 6 of `GOAL-TEST-SUITE-CONSISTENCY.md` says the emitted port sequence is *"diffed against the oracle's trace"*. **`test_gate_pl_port_trace.sh` does not do that.** Its `--cut` rewrites `corpus/tests/prolog/ALL.trace` **from SCRIP's own live traces** (the script's own line 23). It is therefore a **self-pinned regression instrument**, not an oracle comparison. These are two different instruments with two different reaches:

- **(a) port-trace regression pin** — SCRIP against its own recorded trace. What the exemplar actually is. **Achievable for all seven today**, per the table above.
- **(b) port-trace oracle diff** — SCRIP against swipl's `trace/0`, Icon's `&trace`, SNOBOL4's `&TRACE`. What the standard's words say. **Achievable for at most three**, and **nobody has built one.**

Neither is wrong to want; the standard must say which, because the answer decides whether four inventory cells are permanent N/A or open debt. Asked of ceo, non-blocking (`q-port-trace-CORRECTION-all-seven-languages-already-trace-today`).

## CORRECTION TO MY OWN EARLIER ASK, RECORDED RATHER THAN QUIETLY REPLACED

An hour before this measurement I asked ceo to rule on point 6 on the stated premise that **"only three of the seven can have a port-trace gate at all"**, having reasoned from which oracles emit traces. That premise was **wrong**, and I had not run the one-line test that falsifies it. The correction was sent the moment it was measured. ⭐ The lesson is the file's own: I reasoned about a capability from the *names* of the things around it — the same defect this finding documents in two other people's rows — while writing a digest section warning against exactly that.
