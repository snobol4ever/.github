# FINDING 2026-08-19 s170 (seat7, Opus 5, queue row `b1c-retreat`) — **THE DEFERRED CAPTURE TARGET IS A NAME CONTEXT, AND THE ONE PLACE SCRIP RESOLVED IT CANNOT RETREAT**

**Row:** rank 5 `b1c-retreat` — *"FINDING-2026-08-19-s168 residue R2 (retreat wrong-answer). Under SCRIP_B1C_PARITY=1, three `*_retreat` witnesses run clean but report match where oracle retreats to nomatch — deferred-call failure not propagating as pattern retreat. DONE-WHEN: root-cause FINDING + the three witnesses oracle-identical m3."*
**Watermark:** SCRIP `97ad2912` · corpus `de42b605` · oracle cloned (`x64/bin/sbl`, alive) · `make pristine` · RT_OPT=`-O0`. **Everything below was RE-PROVED after the push rebased onto six concurrent commits** — among them `c6245f60`, which flipped **`SCRIP_B1C_PARITY` DEFAULT ON**, so the three witnesses are now RED at the plain default arm and the A/B is simply default → strict.

## 1. THE ROW'S FRAMING WAS ONE LAYER OFF, AND THE CORRECTION IS THE WHOLE FINDING

The brief reads the defect as a **B1c/EVAL fragment** problem — three witnesses that "run clean under `SCRIP_B1C_PARITY=1` but report match". It is not. The same wrong answer is reachable with **no EVAL, no fragment, no cross-medium seam, and the parity killswitch OFF**:

```
	DEFINE('F()')	:(Fe)
F	OUTPUT = 'F called'	:(RETURN)
Fe	P = 'A' . *F()
	OUTPUT = 'built dt=' DATATYPE(P)
	S = 'A'
	S POS(0) P	:S(Y)F(N)
Y	OUTPUT = 'match'	:(END)
N	OUTPUT = 'nomatch'
END
```
`sbl` → `built dt=PATTERN / F called / nomatch`. SCRIP (default, m3) → `... / F called / match`. B1c parity is what stops the three witnesses from SEGVing *before* they reach the defect; it neither causes nor masks it. **The class is `pat . *E` in the main medium, and it was never a fragment bug.**

## 2. THE ORACLE LAW, MEASURED (sbl 4.0f, 14 ablations)

The right operand of `.`/`$` is a **NAME CONTEXT**. A deferred expression is resolved there **for its name, not its value**:

| witness | shape | `sbl` | why |
|---|---|---|---|
| p1/p2 | `'A' . TH`, `'A' . TH . NM` | match, both assigned | ordinary target |
| p4 | `'A' *F()` (concat) | F called, **match** | pattern position — value context, unaffected |
| p15 | `Q='q0'; 'A' . *Q` | match, **Q=[A]**, q0 untouched | the name of a deferred VARIABLE is **that variable** |
| p3 | `F='ZZ' :(RETURN)`, `'A' . *F()` | F called, **nomatch** | plain RETURN yields a VALUE — not a name |
| p5/p13 | `F=.ZZ :(RETURN)` | F called, **nomatch**, ZZ unassigned | **even a NAME-datatype value fails** — the discriminator is the RETURN, not the datatype |
| p16 | `F='ZZ' :(NRETURN)` | F called, **match ZZ=[A]** | NRETURN supplies a name |
| p17 | `F=.ZZ :(NRETURN)` | F called, **match ZZ=[A]** | ditto |
| q3 | `P = EVAL('LEN(0) . *F()'); 'abc' ? P` | **one** `F called`, then OK | the failure **abandons the statement** — it does not retreat into a rescan |

Two consequences the fix turns on: **(a) the discriminator is RETURN-vs-NRETURN, which the returned DESCR cannot express** (`F='ZZ'` returns the identical STRING either way, and sbl matches one and retreats on the other); **(b) the failure aborts the match with the anchor NOT advanced** — q3 proves it, because a retreating rescan would print `F called` four times.

## 3. ROOT CAUSE — TWO DEFECTS, ONE MISREADING

SCRIP read `. *E` as **`. $E`**: *evaluate E, use the resulting VALUE as the name to assign into, and always succeed.*

* **`lower_snobol4.c` (both capture sites, `TT_CAPT_COND_ASGN`/`TT_CAPT_IMMED_ASGN`)** synthesizes a target *string* `"*<expr>"` for any `TT_DEFER` target, collapsing `*VAR` and `*F()` into one spelling.
* **`pattern_match.c :: rt_dcap_pump`** resolves that `"*…"` name at flush time: `rt_call_proc_descr(name+1, 0)` with `rt_g_want_name = 1`, then `if (IS_STR_fn(nm)) NV_SET_fn(VARVAL_fn(nm), d)` — **spending a plain-RETURN value as an indirect name** — and `if (IS_FAIL_fn(nm))` merely `fprintf`s a WARN and `continue`s. Every path returns 0. That is the wrong answer, and the two sub-cases are:
  * `pat . *F()` → assigns through F's return value and answers **match** (oracle: retreat). ⇐ the row's R2.
  * `pat . *VAR` → assigns to `$VAR` instead of `VAR` (`q0` gets `A`, `Q` does not). Right answer for the match, **wrong variable** — a second, previously unrecorded defect in the same three lines.

**Why the failure could not propagate (the row's own words, now mechanized):** `rt_dcap_pump` runs from `c_rt_dcap_end_ok_open` ← `rt_match_end_all` ← **`bb_match_end`**, the pattern's *commit-time* terminus, and `bb_match_end` ends in an unconditional `x86_gamma()`. `IR_MATCH_END` was built `lc_build(g, IR_MATCH_END, sJ, NULL)` — **ω literally NULL**. The one place SCRIP resolved the deferred target sat downstream of every decision point in the machine and had no failure edge to take. It could only warn.

## 4. THE FIX — `SCRIP_CAP_NAME_STRICT`, THREE HALVES, DEFAULT OFF

Same killswitch name in all three files so a flip moves them together (the s121 both-halves-land-together law). **DEFAULT OFF**, mirroring how s168 landed `SCRIP_B1C_PARITY`; the flip is a separate row's deliverable.

1. **`lower_snobol4.c` half A** — a `*VAR` target lowers to the **plain variable**: `pat . *VAR` ≡ `pat . VAR`. It never reaches the pump's `*` arm again.
2. **`lower_snobol4.c` half B** — `IR_MATCH_END` gains the ω it never had, wired to **`cx->pat_seal`**: the φ-tagged unwind `TT_ABORT` already uses (BEGIN's `na_f` — CAS pop, rsp restore, PATCTX restore, claim release; ω tail = statement-fail, **anchor not advanced**). This is §2(b) exactly.
3. **`pattern_match.c` + `rt/rt.c`** — the pump reads the **RETURN-vs-NRETURN** discriminator. `rt_nret_fix` already owns `rt_g_ret_by_name` but *cleared* it before the caller could look; under strict it now leaves it standing for a name-context caller (`wn==1` — only the deferred-capture sites ever set it) and the pump reads-and-clears it. Plain RETURN ⇒ `rc = 1` ⇒ the terminus takes ω. NRETURN keeps both pre-s170 assigning arms verbatim.
4. **`bb_match_end.cpp`** — under strict only, a `test rax,rax / je` guard and a 4-instruction ω stub that undoes exactly what this box's α established (two pushes, anchor, xfer) and jumps ω. **No new globals** (the discriminator is an existing flag; the switch readers are functions).

⛔ **The first wiring of half B was WRONG and the corpus caught it, not the witnesses.** ω → `head` (the pattern's own fail continuation) looked obviously right and passed all 14 ablations. It re-entered the scanner with the outer Σ/δ/Δ un-restored, so every lap re-matched at the same position and leaked a frame — `probe/eval/ev_beauty_shape.sno` (the beauty grammar shape, `epsilon . *Reduce(…)`) went **PASS → SEGV**, and the minted `q3` went to an infinite `F called`. The pass **COUNTS were identical** (483→485 either way); only the **BY-SET diff** showed a repair and a break cancelling. `cx->pat_seal` is the correct target and q3/ev_beauty_shape are now green.

## 5. MEASUREMENTS (pristine `make pristine`, RT_OPT=-O0)

* **KILLSWITCH BYTE-IDENTITY — 0/318.** Every `.s` over `corpus/crosscheck` (318 programs, 316 distinct md5s, zero empty) is **byte-identical** to stashed-baseline HEAD at default. The strict arm emits nothing unless armed.
* **BY-SET corpus A/B, 541 graded programs** (`probe/`, `programs/snobol4/`, `gimpel/`, `lon/`), at the rebased HEAD: default → `CAP_NAME_STRICT=1` = **REPAIRED 3, BROKEN 0** (483→486), and the three are exactly `b1c_eval_fn_pattern_retreat`, `b1c_patvalued_formal_retreat`, `b1_eval_pattern_defer_call`. **The row's DONE-WHEN, measured.** (Pre-rebase, with parity still default OFF, the same pair read REPAIRED 0 / BROKEN 0 for strict alone and REPAIRED 3 / BROKEN 0 for parity→parity+strict — i.e. the two switches are independent and strict alone moves nothing that parity has not already reached.)
* **Corpus gate at default:** m3 **326/337**, m4 **322/337** at the rebased HEAD (m3 +1 from concurrent work; my arm is OFF there, so this is the seat's non-regression proof, not a claim of credit).
* **Gates:** `test_gate_emit_no_lang` OK · `test_gate_template_medium_invisible` OK — the guard-site ratchet is now **5** (the `medium-retire` rungs landed in the same rebase) and this rung **added none**.
* **18/18 oracle-identical** under strict across the three witnesses + `ev_beauty_shape` + the 14 ablations.

## 6. WITNESSES MINTED (`corpus/probe/b1/`, oracle `.ref` beside each)

`b1c_capname_call_return` (plain RETURN ⇒ nomatch) · `b1c_capname_call_nreturn` (NRETURN ⇒ match) · `b1c_capname_var_target` (`. *Q` names Q, not `$Q`) · `b1c_capname_abandon_once` (called once, statement abandoned). All four are **oracle-identical under `=1` and honestly RED at default** — the two RED ones are the two defects of §3.

## 7. ROUTED, NOT DONE HERE

* ⭐ **The flip.** Strict ships OFF. The A/B above is the whole case for turning it on; it wants the same treatment row `b1c-flip` is giving `SCRIP_B1C_PARITY` (6-suite + md5 sweep, then flip). **Suggest HQ mint `capname-flip`.** The two switches are independent: strict alone moves nothing (`REPAIRED 0 BROKEN 0`), so it can flip before, after, or with parity.
* ⭐ **`b1c-m4-seam` (rank 4) — a free datapoint.** Its brief hypothesizes an m4 *fragment* seam. The minimal `p8` above has **no EVAL and no fragment and still SEGVs in m4** (m3 is fine). The m4 crash class therefore extends to plain main-medium `. *F()`, and the fragment hypothesis cannot be the whole story. m4 is untouched by this rung — the strict arm is m3-verified only.
* **An inherited blocker is FALSIFIED.** `bb_match_capture.cpp`'s header and its two bomb arms cite *"blocked on the :(NRETURN) lowering bug (s82: does not compile at all today)"*. At HEAD, `:(NRETURN)` compiles and runs **oracle-identical** in both the string and NAME-datatype forms (p16/p17, green in the default arm before this rung touched anything). Whatever s82 hit is gone; the deletion Lon directed there is no longer gated on it. Not acted on — it belongs to the box's own owner.

## 8. THE LESSON WORTH KEEPING

Two of them. **(a) A wrong answer attributed to a killswitch's territory may just be visible there** — B1c parity only bought the witnesses enough life to reach a defect that was always in the main medium, and taking the brief's framing literally would have sent this seat into `runtime_eval.c` for the whole session. Ablate to a witness that drops the named ingredient *before* trusting the attribution. **(b) Pass counts are not a verdict.** The bad ω wiring scored 485 vs 483 — a two-program *improvement* — while silently SEGVing the beauty grammar shape. Only the BY-SET diff named it. Every arm A/B in this file is BY-SET for that reason.
