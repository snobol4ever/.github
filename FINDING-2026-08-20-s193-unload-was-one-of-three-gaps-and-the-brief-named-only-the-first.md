# FINDING — s193 (seat7, `/home/claude7`, Claude Opus 5) — queue row `unload-missing`

## ⭐ THE HEADLINE: THE ROW SAID "UNLOAD IS NOT REGISTERED". TRUE — AND IT IS **ONE OF THREE** GAPS BETWEEN `f12_load_unload.sno` AND A PASS. THE OTHER TWO ARE NOT UNLOAD DEFECTS AND THE BRIEF'S DONE-WHEN CANNOT BE MET WITHOUT THEM.

`f12` is a three-mechanism acceptance test — UNLOAD **and** `&ERRLIMIT`/`SETEXIT` recovery **and** the
undefined-function error. It was measured, not assumed:

| # | gap | evidence it is independent |
|---|---|---|
| 1 | **`UNLOAD` unregistered** | `LOAD` at core.c:1826, no `UNLOAD` anywhere. **FIXED THIS RUNG.** |
| 2 | **`SETEXIT` is a WRITE-ONLY STUB** | `_setexit_label` (core.c:1277) is written by `_SETEXIT_` and **read by nothing** — grep across `src/` returns the three lines that write it and **zero** that read it. Probe `u_setexit.sno` contains **no UNLOAD at all** (just `&ERRLIMIT=1` + `SETEXIT('OK')` + a call to a never-defined function): **oracle PASS, SCRIP aborts.** `keywords.c:187`'s own comment still says *"SETEXIT does not exist in SCRIP yet, so the no-label arm IS the whole mechanism"* — that comment is TRUE and the DONE-WHEN contradicts it. |
| 3 | **an unloaded call still runs** | UNLOAD's registry removal never reaches the CALL SITE — see below. |

## ⭐ THE ORACLE CONTRACT FOR UNLOAD — NINE ARMS, ALL MEASURED, NONE CHOSEN

The brief said *"⛔ THE MANUAL IS THE AUTHORITY"*. The manual (v3.7 p.245) gives two sentences —
*"undefines the user-defined function name"* and *"In SPITBOL, only user-defined functions can be
UNLOADed"* — and the live `sbl -bf` supplies everything else:

| argument / situation | oracle | SCRIP after this rung |
|---|---|---|
| user-defined name | SUCCEEDS, returns the **null string** | ✅ same |
| **the same name's VARIABLE VALUE** | **SURVIVES** — only the function binding goes | ✅ same |
| name never `DEFINE`d | SUCCEEDS, in silence | ✅ same |
| unloaded twice | SUCCEEDS | ✅ same |
| a **builtin** (`'SIZE'`) | **ERROR 248** *attempted redefinition of system function* | ✅ same code, same text |
| a non-name string `'1BAD'` | SUCCEEDS | ✅ same |
| an integer `3` | SUCCEEDS | ✅ same |
| null / no argument | **ERROR 201** *unload argument is not natural variable name* | ✅ same code, same text |
| an **ARRAY** | **ERROR 201** | ✅ same code, same text |
| **self-unload, then call again** | current call completes; next call **ERROR 022** | ⛔ **SCRIP CALLS IT ANYWAY** |

Two of these are counter-intuitive and would certainly have been guessed wrong: **the variable value
survives**, and **the argument is TYPE-validated but never NAME-validated** (`'1BAD'` is accepted; an
array is not). Guessing here was exactly what the brief forbade.

## THE CURE, AND THE ONE PLACE IT DOES NOT REACH

`register_fn` is a thin wrapper over `DEFINE_fn`, so **builtins and user functions share ONE table** and
the system/user discriminator is `->fn` — `register_fn` is its only writer, and `_DEFINE_` registers a
SNOBOL4 function with `fn` NULL down both its arms. `UNLOAD_fn` unlinks the entry, answering *removed /
system / unusable-name*, and `_UNLOAD_` turns those into null / 248 / 201. No new global, no new killswitch.

⛔ **BUT THE CALL SITE NEVER ASKS THE REGISTRY.** A SNOBOL4 call jumps through a **cell** that `DEFINE`
baked; nothing tests it. Measured, not reasoned: I tried the obvious symmetric cure — also
`rt_proc_set_fn(name, NULL)` — and it made the witness **worse**, turning a wrong answer into a wild call
and a core dump. That is the proof the call road is the cell, not the registry, so **curing it means a
NULL test at the cell routed to error 22 — a template rung**, which per PLAN.md step 7 requires the
BB-codegen design set first. Reverted; the experiment's only lasting value is that it excluded a road.

## EVIDENCE

Probes checked in at `corpus/probe/unload/`, refs minted from the live oracle:
`un_ret.sno` (succeeds, returns null) · `un_never.sno` (never-defined, and twice) ·
`un_var_survives.sno` (**the arm most likely to be got wrong**) — **all three PASS in BOTH modes**.
`un_self_exec.sno` is checked in **RED and deliberately without a `.ref`**: the oracle's answer to it is an
error **termination dump**, and class (ii) of row `ref-the-ungraded-suites` says a ref is not minted from
one. The 248/201 arms are likewise not reffable — SCRIP emits the right **code and message text** but not
SPITBOL's dump, a whole-codebase format gap, not an UNLOAD defect.

Fail-sets **identical by name** before and after: crosscheck m3 319/1 · m4 315/4 · DIVERGE 3; broad corpus
m3 339/1 · m4 332/7 SKIP 1. RT_OPT `-O0`.

## ⭐ THE `LOAD` STUB, AUDITED AS THE ROW ASKED — IT IS ITS OWN DEFECT

`_b_LOAD_stub` (core.c:433) answers **only names beginning `MON_`** and returns `FAILDESCR` for everything
else. So `LOAD('NOSUCH(X)')` **silently fails** where the oracle raises **ERROR 142 *load function does not
exist***. It is a **monitor hook wearing LOAD's name** — the brief's *"a stub that silently succeeds is its
own defect"*, in its silently-**fails** form. Not sound. **Wants its own row**; left untouched so the
monitor keeps working.

## ⛔ WHAT THIS ROW DID NOT CLOSE, STATED PLAINLY

`f12_load_unload.sno` still prints `FAIL` — but it has **moved**, from *"Error 5 — Undefined function or
operation"* (UNLOAD itself unknown, program aborted at statement 0) to running all the way to its own
verdict line. It cannot pass until gaps 2 and 3 land, and **neither is an UNLOAD defect**. No `.ref` was
minted for it: pinning one now would pin a lie. Asked of HQ (`s4e_msg.sh ask unload-missing`), answer not
yet received at handoff; three rows are implied — SETEXIT transfer-on-error, the unloaded-call cell test,
and the LOAD stub.
