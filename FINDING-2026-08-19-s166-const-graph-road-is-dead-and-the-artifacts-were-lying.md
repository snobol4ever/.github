# ⛔⛔⛔ RETRACTED IN FULL BY ITS OWN AUTHOR, SAME SESSION (s166) — THE "DEAD ROAD" WAS A STALE GREP PATTERN, NOT A DEAD ROAD

**Status: VOID. Do not act on any version of this file's original claims.** The retraction and the correct measurements are below; the original text is kept underneath as the record of the error, exactly as HQ-21 was kept.

## WHAT I CLAIMED, AND WHY IT WAS WRONG

I claimed the emitted shared-pattern-graph road (`proc_PAT$N`) was **unreachable at HEAD** — "0 of 59 programs", "no source shape resurrects it", "the fz table gates both roads so there is no middle tier", "zero live coverage, reviving it is reviving bit-rot".

**Every one of those claims is FALSE, and they all came from ONE defect: I grepped a label that had been RENAMED.** The emitted graph is no longer spelled `proc_PAT$N_α`; the s62 STUB-BLOB-DELETE bare-chain change emits kind-2 thunks with an `FN__` face and no `proc_` wrapper, so the live spelling is **`FN__PAT$N` + `PAT$N_α_body` / `PAT$N_β` / `PAT$N_γ` / `PAT$N_ω` / `PAT$N_res`**. My sweep searched for the OLD string and found nothing, and I read "no matches" as "no road".
The second sweep compounded it: it searched `grep -rl "proc_PAT" corpus --include=*.s` **after I had already regenerated every one of those artifacts into the new spelling**, so the file list was empty and the loop reported "of 0 programs" — a denominator of zero read as a result. A third pass used `grep -q "FN__PAT\$"` inside double quotes, where `\$` collapses to `$` and grep reads it as END-OF-LINE, giving another false zero.

## THE CORRECT MEASUREMENTS (label-agnostic, fixed-string `grep -F`, live compiles at HEAD)

- **58 of 318 crosscheck programs emit a `PAT$N` graph at HEAD.** The road is LIVE and has real, broad coverage — including `expr_eval`, the whole `066/068/105/108/109` FENCE-via-var family, and `070_pat_arbno_star_var_digits`.
- **`word4.sno` — the program I declared one of the "zero" — emits `FN__PAT$0` with the complete four-port CLASS D shape** (`PAT$0_α_body`, `PAT$0_γ` pushing the `{res,r10,r11}` record, `PAT$0_res`, `PAT$0_β`, `PAT$0_ω`).
- **The middle tier EXISTS.** Re-run of the shape sweep with the correct label: `P = BAL`, `P = SPAN(…) . W`, `P = ARB . W` each emit a `PAT$` graph; `FENCE 'a'`, `BREAK(' ')`, `SPAN(…)` inline. So capture/BAL shapes are exactly the population that qualifies for a graph and is refused by inlining — the tier I claimed could not exist.

## WHAT SURVIVES THE RETRACTION (re-verified, unaffected by the grep defect)

- **The artifact staleness is real.** The CN-14 regen rewrote **414 of 484 crosscheck `.s` artifacts (net −23,654 lines)** while CN-14's own measured blast was **24 of 527** — so the tree carried large accumulated staleness, part of it this very label rename. `.s` = HONEST CURRENT OUTPUT does decay silently between regens.
- **The CN-13 economics are real** (measured independently of any label): marginal cost of one more use site = **136 lines** (today's substitution) vs **205** (dynamic) vs ~5 target, exactly linear in site count; and of the **17 instructions** a live defer site spends entering a shared graph, **13 are dynamic resolution** a declaration makes unnecessary.
- **CN-13's original scoping therefore STANDS, and is better news than the retracted version:** the road is live and covered, so rung 1 is the linkage + policy work as first scoped, NOT a resurrection. The "prove it still works before linking" precondition I invented is unnecessary — 58 programs prove it every crosscheck run.

## THE ACTUAL LESSON, WHICH IS SHARPER THAN THE ONE I WROTE

I wrote "REGENERATE BEFORE YOU DIFF". That is still good advice but it is not what bit me. What bit me is one level down and worse:

⛔ **A GREP THAT RETURNS ZERO IS NOT EVIDENCE OF ABSENCE UNTIL THE PATTERN IS PROVEN TO MATCH SOMETHING.** Three times in one investigation a zero came back — renamed label, empty file list, `$` eaten as end-of-line — and each time I read the zero as a fact about the compiler instead of a fact about my pattern. **Every one would have been caught in seconds by a positive control: run the pattern against a case it MUST match before trusting a zero.** The project already has this law for gates (the s165 "prove the gate goes red" discipline, and the KILLSWITCH BYTE-IDENTITY law); it applies to measurement greps identically. **A negative result needs a positive control, always.**

Related and unchanged: the s149 `COMPILE_RC_<rc>` law in `util_s_md5_sweep.sh` exists because a *truncated* artifact once masqueraded as a result. Same family — an instrument returning something that is not what the reader thinks it is.

---
## THE RETRACTED TEXT, kept as the record of the error
The original claimed: `proc_PAT$N` cannot be produced by any SNOBOL4 source program at HEAD; 0 of 59 programs emit one; no source shape resurrects it; the fz table gates both roads so no middle tier exists; the road has zero live coverage and reviving it is reviving bit-rotted untested code of the B1c/B2c provenance; and CN-13 rung 1 must therefore begin with a resurrection test. **All VOID per the measurements above.**
