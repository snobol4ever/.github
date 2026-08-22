# FINDING — 2026-08-21 s249 (seat2 `/home/claude2`, Claude Opus 5; queue row `setexit-write-only-stub`, rank 1) — ⛔⭐⭐⭐ SETEXIT WAS **THREE** MISSING MECHANISMS, NOT ONE, AND A LITERAL OPERAND HIDES TWO OF THEM

Measured at SCRIP `ec34eba0` + `64e2d763`, RT_OPT `-O0`, oracle `x64/bin/sbl -bf` verified alive first.
Witnesses: `corpus/probe/setexit/` (9 rows, every `.ref` oracle-baked and generated twice before check-in).

## 1. THE ROW WAS RIGHT AND INCOMPLETE

The row said *"`_setexit_label` is WRITTEN by `_SETEXIT_` and READ BY NOTHING"* — three writes, zero reads, and
it called that *"not a missing builtin, a missing MECHANISM."* Both true. But the mechanism is **three**:

| | what it is | state |
|---|---|---|
| **RAISE** | turning a fault into an error the engine can see | ⛔ mostly absent, **and this is the big one** |
| **TRAP** | `SETEXIT`'s read side — where control goes | ⭐ **CURED, this rung** |
| **RESUME** | `:(CONTINUE)` / `:(SCONTINUE)` returning to the failed statement | ⛔ needs a statement-indexed trampoline |

⭐ **THE RAISE GAP IS WIDER THAN THE ROW AND WAS NOT SUSPECTED.** `X = 1 / D` with `D = 0` is **silently
degraded to statement failure** in SCRIP: no message, `:F()` taken, program runs on. The oracle raises
`ERROR 014` and, `&ERRLIMIT` being 0 by default, **aborts**. Same for `CHAR(N)` out of range and `LEN(-1)`.
Only two of the errors probed reach `core_runtime_error` at all (5 undefined function, 164 prototype).
**So `&ERRLIMIT` has never been observable on arithmetic, and no SETEXIT witness built on `1/0` can
distinguish a missing TRAP from a missing RAISE.**

## 2. ⛔⛔⛔ THE TRAP THAT MIS-MEASURES THIS ROW, AND I FELL IN IT FIRST

Probed with **literal** operands — `X = 1 / 0`, `OUTPUT = CHAR(1000)` — the oracle terminates and the handler
never runs, while `TRACE(...)` and `&Z = 1` errors **are** caught. That reads exactly like *"SPITBOL's SETEXIT
is selective by error code,"* and I wrote that conclusion down before falsifying it.

**It is false.** Those errors are **CONSTANT-FOLDED AND DIAGNOSED AT COMPILE TIME**, before `SETEXIT` can
arm. Hide the operand in a variable (`D = 0` … `1 / D`) and the identical errors trap normally. A seat that
had not caught this would have built a bogus error-class table into the cure. **Every witness in
`probe/setexit/` uses the variable form on purpose and the README says why.**

## 3. THE CONTRACT IS NOT FOLKLORE — IT IS THE ORACLE'S OWN DECISION CODE

`x64/sbl.min:29377-29420` (`err05`/`err06`/`err07`), comment *"the action taken on an error is as follows"*:

1. **`&ERRLIMIT` zero ⇒ ABORT**, however armed (`bze kverl,labo1`).
2. Set `&ERRTEXT`/`&ERRTYPE`, then **abort anyway if 3+ fatal errors** — *"regardless of errlimit and setexit
   — looping is all too probable otherwise."*
3. **Decrement `&ERRLIMIT`** (`dcv kverl`).
4. Save the failure offset (`:(CONTINUE)`) and the code offset (`:(SCONTINUE)`).
5. **No trap ⇒ the erroring statement takes its OWN FAILURE EXIT** and execution continues.
6. **Trap ⇒ clear the trap (`zer r_sxc`), reset the stored argument to null (`mov stxvr,=nulls`), jump to it.**

So **`SETEXIT` is ONE-SHOT** (which is why SPITBOL's own `test/setexit.sbl` re-arms inside its handler), and
**`&ERRLIMIT` is a separate load-bearing half**: it decides *whether* an error is survivable, `SETEXIT` only
*where* control goes. Argument must be a label name or null else **ERROR 187** (`sbl.min:15596`).

## 4. THE CURE — THREE SMALL EDITS, NO NEW MECHANISM, NO NEW GLOBAL

The brief said to read `core_runtime_error`'s existing longjmp arm *"before inventing a second mechanism"*.
Read, and reused:

1. **`core.c` `_SETEXIT_` returns the PREVIOUSLY ARMED LABEL** (it returned `NULVCL` unconditionally).
2. **`core.c` `core_runtime_error` grows a read side** *after* the existing EVAL-boundary `longjmp` arm, which
   is untouched and keeps priority: trap armed **and** `kw_errlimit != 0` ⇒ copy the label, **clear it**
   (one-shot), decrement `kw_errlimit`, publish the error keywords, `rt_goto_transfer()`.
   ⭐ `rt_goto_transfer`/`rt_goto_resolve` **already existed** for indirect goto — the transfer road is
   reused, not respelled (s68/s70's "do not spell it twice", which the brief invoked).
3. **`lower_snobol4.c`: `SETEXIT` joins `CODE` in `sno_scan_code_use`.** A program that can transfer to a
   label at RUNTIME must have its labels registered as `LBL__` procs. Without this the trap fired **correctly**
   and then died at `transfer to undefined label: H` — **the mechanism was right and the label table was empty.**

`&ERRLIMIT` is load-bearing here and not decoration: zero falls through to today's abort — the oracle's own
first rule — and the trap decrements it. **Measured:** a handler reading `&ERRLIMIT` after one catch answers
**9** from 10.

## 5. RECEIPTS

- **faces `1/9` → `3/9`, m3 AND m4, identical by name** (`se_retval`, `se_notrap_failexit`, `se_trap_undef`).
  m3 ≡ m4 on **every** row — a lowering/runtime gap, not an m3≢m4 divergence.
- **killswitch `SCRIP_SETEXIT=0` returns exactly `1/9` both modes — NON-VACUOUS**, one env var reverts.
- **unarmed programs untouched, MEASURED not asserted:** A/B `.s` sweep armed vs killswitched over **130**
  crosscheck programs = **0 movers**, and none of the 130 contains `SETEXIT`. ⭐ **And an independent second
  path, far wider:** RULES step-4 regen, all six scripts in order, **`changed=0` on every tree** —
  programs 623, crosscheck 487, prolog bench 22, benchmark/feature/demo current.
- **crosscheck m3 319/1 · m4 318/1 SKIP 1 · DIVERGE 0**, sole FAIL `160_pat_alt_inner_gen_resume` **both
  modes** — the standing front red the s197 cursor already names. Fail-set no worse **by name**.
- smoke SNOBOL4 **7/7 m3 AND m4**; gates `emit_no_lang` · `template_medium_invisible` · `icn_no_stack` green.

## 6. ⭐ `f12_load_unload` RE-STATED, AS THE ROW REQUIRED — AND ITS REMAINING FAILURE IS **NOT SETEXIT'S**

`f12` is oracle `PASS`, SCRIP `FAIL`, **unchanged by this rung**, and the reason is now exact:

- ✅ **The SETEXIT half f12 needs WORKS.** `f12` arms with the **string** form `SETEXIT('OK')`, and that form
  arms and fires correctly after this rung (witnessed standalone: string-armed trap on a raising error prints
  `HANDLER`). Both `.L` and `'L'` spellings are covered.
- ⛔ **The blocker is the RAISE half, and it is seat7's already-named row.** An UNLOADed call **still runs and
  returns its value** — `MYFN('b')` answers `b` after `UNLOAD('MYFN')`, where the oracle raises `ERROR 022`.
  No error is raised, so no trap can fire, and `f12` falls to its `FAIL` line. This is seat7's s192 gap (3),
  *"an unloaded call STILL RUNS because the call site jumps through a CELL DEFINE baked and never asks the
  registry"* — and seat7 already **excluded the obvious cure by measurement** (`rt_proc_set_fn(name,NULL)`
  gave a wild call and a core dump, reverted), so it is a TEMPLATE rung, not a runtime one.

**`f12` therefore needs two more rungs, neither of them this row's:** the UNLOAD call-cell, and RESUME.

## 7. ⛔ A SECOND DEFECT FOUND, PRE-EXISTING AND NOT MINE — A LABEL IS LOST BY THE CONTENT OF ITS OWN STATEMENT

Proven **with this change disabled** (`SCRIP_SETEXIT=0`) and **no `SETEXIT` anywhere**, on the plain
indirect-goto road:

```
L = "H" ; :($L)   with   H  OUTPUT = "REACHED"            ->  REACHED
L = "H" ; :($L)   with   H  OUTPUT = "REACHED " &LASTNO   ->  [SNO] transfer to undefined label: H
```

**A label whose statement reads a keyword is never registered as an `LBL__` proc**, so the *existing*
indirect-goto road silently loses labels. `bb_label_landing()` is the site to look at. This is its own row;
`se_trap_lastno` is checked in RED and will notice when it is cured. ⛔ Note it is red for **two** independent
reasons — this one, and `g_core_err_stmt` never advancing (seat8 s194, named not fixed), which is why the
oracle says `S3` and SCRIP would say `S0`.

## 8. WHAT IS OWED NEXT, NAMED

1. **RESUME rung** — `:(CONTINUE)`/`:(SCONTINUE)` + the no-trap survivability half
   (`se_errlimit_survives`, `se_oneshot`, `se_rearm` are its witnesses and are checked in red).
   Both need a statement-level resume boundary; the oracle saves *two* offsets for exactly this reason.
2. **RAISE rung** — the fault-to-error road (`se_trap_fires`, `se_reset_null` are its witnesses).
   Blast radius is every error-recovery program in the corpus, as the row said.
3. **`bb_label_landing` keyword-statement row** (§7) — a silent lost transfer in shipped machinery.
4. **`g_core_err_stmt` never advances** — seat8's, still standing.

## 9. ROUTED

`GOAL-SNOBOL4-100.md` LIVE CURSOR (s249) · row `setexit-write-only-stub` · SCRIP `64e2d763` · corpus
`probe/setexit/`. Siblings: seat7's s192 UNLOAD finding (gaps 2 and 3), seat8's s194 subscript finding
(`g_core_err_stmt`).
