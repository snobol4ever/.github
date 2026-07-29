# FINDING s214-ICN — Three completeness rungs, and 0(d) has been measuring the wrong thing for six sessions

**Session:** s214-ICN, 2026-07-29 · **Ladder:** ICON-RTX · **Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
**Directive:** *"Replace SCRIP's C runtime with ASM code. Do one at a time from small to large."*

## 1. What the directive changed

The ordering key became **C body size**, not dynamic share. All six step-0 checks still run, but 0(d)
moves from a GO/NO-GO on *worth* to a **falsifiability** gate: a port whose corruption cannot move any
board is still refused; "measures flat" no longer rejects. Size ranking is derived by sweeping
`scrip --compile` over 316 Icon programs (step 0(i)), extracting `call sym@PLT`, intersecting with
brace-counted C bodies in `src/runtime/**/*.c`.

## 2. ⭐⭐ The headline: FLAT IS NOT COLD. 0(d) measures frequency; the ladder has been reading it as importance.

`rt_proc_value` arrives **4 times and is FLAT** (4 at N=50, 4 at N=200) — the setup-only signature that
got `rt_call_arr` rejected at s188 and got `rt_proc_value` itself rejected at RTX-8.

**Corrupting its identity sentinel takes the Icon board from 252/11 to 1/262.**

A symbol the ladder twice wrote off as cold is the most load-bearing thing yet measured here. The two
questions are ORTHOGONAL:

| | frequency (0(d)) | importance (falsification) |
|---|---|---|
| `rt_proc_value` | 4, flat ⇒ bad SPEED target | 251 programs ⇒ maximal correctness weight |

This does not overturn s188 — `rt_call_arr` remains a bad *speed* target — it says the ladder has been
using one number for two questions. Under a completeness directive, flat symbols are legitimate targets.

## 3. Three rungs landed

| symbol(s) | gate | body | ported arm | falsification (ON → / OFF) |
|---|---|---|---|---|
| `rt_gen_spine_resume_enter`, `pass_γ`, `pass_ω` | `SCRIP_RTX_ICNGEN` (11th) | 1 line each | whole body | γ result: **244/19** / 252 · counter: `&level` 1→**199801**, 251/12 / 252 |
| `rt_proc_value` | `SCRIP_RTX_ICNCALL` (12th) | 3 lines | whole body | sentinel: **1/262** / 252 |
| `rt_str_coerce` | reuses `SCRIP_RTX_ICNREL` (**no new gate**) | 7 lines | `!IS_CSET_fn` identity arm (93.1%) | identity: **249/14** / 252 · cset predicate: **251/12** / 252 |

0(d): `resume_enter` 200→800 and `pass_γ` 199→799 at N→4N (exactly 4×); `pass_ω` flat 1→1 (correct
semantics — one terminating fail per exhausted generator); `rt_str_coerce` 100→400 (exactly 4×).

**⛔ NO SPEED CLAIM ON ANY OF THE THREE.** No benchmark was run and no isolation arm exists, so per s204
**no ratio may be quoted for the icnrel family after this edit.** What the ports remove is `-O0` frame
ceremony, which is precisely the class the s208 inbox's gap #1 says `-O2` also removes.

## 4. ⭐ A third arm regime — s212's law confirmed from a new direction

`bb_unop.cpp` emits `rt_str_coerce`/`rt_num_neg`/`rt_num_pos` with **NO inline tag guard**. So the guard
steers nothing and the CHEAP arm dominates: identity **802/861 = 93.1%**.

RTX-6: first arms dead. RTX-6b: both ends live, middle cold. Here: cheap guard arm live. **Three rungs,
three regimes. The regime is a property of the specific guard/callee pair and never transfers.**

## 5. ⭐ New 0(d) trap: a ZERO can come from a program that RAN CORRECTLY

s213's rule: *a zero is not a result until the program is proven to have RUN.* Sharper version measured
here: a cset-CONCAT loop **ran, printed the right answer, and reached `rt_str_coerce` zero times.** The
**construct** was wrong, not the program. Dead-program zeros and wrong-construct zeros are different
failures with identical symptoms.
⇒ **Rank corpus programs by arrivals, then build the scaling test from the winner.** Here that gave
`rung36_jcon_lexcmp` ⇒ lexical comparison (`<<` `<<=` `==` `~==` `>>=` `>>`). Guessing costs a rung.

## 6. ⚠ Two self-inflicted errors, both caught by the protocol, both worth writing down

1. **I made the §5(ii) Greek mistake myself** in my first inventory. An ASCII-only
   `call ([A-Za-z_0-9]*)@PLT` regex made **all four Greek-named runtime symbols invisible** — including
   two of the three I then ported — and silently falsified the "already asm" filter too. The doc warns
   about exactly this. **Use a byte-class pattern.**
2. **A `cmp` reported byte-identity PASS on two EMPTY files** (an `awk` quoting error emptied both
   inputs). **A comparison whose inputs are unverified is not evidence** — check non-emptiness first.
3. Twice I closed a block comment early by quoting canonical source that itself contained `*/`
   (`/* T_Proc */`, `/* adjust procedure level */`). Cheap to fix, but it is a build break every time.

## 7. Ownership: `rt_num_neg`/`rt_num_pos` NOT taken

Next by size (4 lines) but the allocation rule puts them with **SN4-RTX** (tie, ARITH family). Declined,
same class as s212 declining `rt_binop_overload`. Request + two free measurements are in `RTX-CLAIMS.md`.

## 8. Gates

All three languages, gates ON and all-OFF, identical: Icon **252/11/30** (fresh, re-derived pre-edit) ·
SNOBOL4 m4 smoke **7/0**, broad_corpus **324/2** · Prolog interp **164/0**, compile **164/0**.
⚠ Prolog measures 164/0 where the goal file's prose says 185/0/0 and 188/0/1 — same class of
prose-vs-measurement drift as s212/s213. Graded on the ON/OFF differential; **no culprit asserted.**
⚠ **Battery coverage is thin relative to arrivals:** `rt_str_coerce` arrives 861 times corpus-wide but
its identity corruption moves only 3 graded programs. That is a statement about the batteries.
⚠ **PROTOCOL DEVIATION (fourth session running): no credential.** Check-outs were not pushed before the
work; nothing is pushed now. `scripts/handoff_status.sh` is the only completion truth.
