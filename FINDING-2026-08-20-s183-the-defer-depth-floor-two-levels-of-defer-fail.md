# FINDING s183 — ⭐⭐⭐ THE DEFER-DEPTH FLOOR: a pattern reached through **two** levels of `*defer` fails

**Session:** 2026-08-20 s183 · HQ (Fable 5) · SCRIP `3da13598`, corpus `probe/passthru/ptw_min_defer{1,2}_*`
**Queue row:** `defer-depth-floor` — **rank 0, topmost.** Probably subsumes `m1-composed-wild-jump` and `m1-class-b-stmt-parse-error`.

---

## 1. THE FLOOR, IN THREE LINES

```
G1 = 'aa'                 <- a plain STRING.  No ARBNO, no FENCE, no backtracking, no capture, no EVAL.
G0 = *G1
P  = *G0
'aa a' POS(0) *P          ->  ORACLE: match      SCRIP: nomatch
```

⛔ **m3 nomatch · m4 nomatch · `SCRIP_RTSEQ_RESUME=0` nomatch.** Pre-existing, both modes, three lines and a literal. `corpus/probe/passthru/ptw_min_defer2_floor`.

## 2. THE BOUNDARY IS EXACT, AND DEPTH IS THE ONLY VARIABLE

On Lon's own suggested shape `ARBNO(LEN(1) | LEN(2) | LEN(3))` against `'abcdef' POS(0) *P RPOS(0)`:

| witness | shape | verdict |
|---|---|---|
| `ptw_min_defer2_pp_L0` | `P = G1` (direct) | GREEN |
| `ptw_min_defer2_pp_L1` | `P = *G1` (one defer) | GREEN |
| — | `ARBNO(*A1 \| LEN(2) \| LEN(3))` (one **inner** defer) | GREEN |
| `ptw_min_defer2_pp_L2` | `P = *G0`, `G0 = *G1` (**two**) | ⛔ **RED** |
| `ptw_min_defer2_pp_L3` | three defers | ⛔ **RED** |

**ARBNO, ARB, ALT, FENCE and a plain deterministic literal all fail at depth 2 and all pass at depth 1.** The cleanest available pair is one defer level apart with nothing else changed: `ptw_min_defer1_arbno_ctl` (GREEN) vs `ptw_min_defer2_arbno` (RED). `ptw_min_defer2_depth9` shows a 9-level chain failing the same way.

## 3. WHY THIS IS THE M1 BLOCKER

beauty's grammar **is** a deep defer chain: `Parse → Command → Stmt → Label`, and `Expr0 → Expr1 → … → Expr17`. **Depth 2 is beauty's floor, not its ceiling.** Nothing in beauty's grammar could ever have matched.

It also explains the s183 beauty override sweep exactly, which HQ ran before finding this and could not account for at the time:

| override | levels | result |
|---|---|---|
| `*Comment nl` (`Comment = '*' BREAK(nl)`) | 1 | AGREE |
| `*Control nl`, `*Expr0 nl`, `*Id nl`, `*White nl`, … | 1 | AGREE |
| `*Stmt nl` (`Stmt = *Label`) | **2** | ⛔ SEGV |
| `*Label nl`, `*XList nl`, `*ExprList nl`, `*Commands nl` | **2+** | ⛔ SEGV |

## 4. ⭐ HOW IT WAS FOUND — LON'S DIAGNOSIS IS THE REASON IT WAS FOUND AT ALL

Lon, s183 in-chat, on being shown a green probe board beside a broken beauty:

> *"I see they all work. And beauty does not work. Does that say it all. The BB probes are NOT good enough tests."*
> *"Combos at 9 levels with `*P`, `P()`, ARBNO, FENCE, all crazy combinations."*

He was exactly right, and the numbers are the proof:

| battery | shape | result |
|---|---|---|
| HQ's first, **shallow** | 168 combos: one defer × one follower × one wrapper | **167 AGREE, 1 red** — found nothing |
| HQ's second, **deep** | 168 combos: chains of **3/5/7/9** levels interleaving defer · ARBNO · FENCE · ALT · capture · fn-call · variable-operand | **12 reds**, all sharing the prefix `D-A-F` |

Ablating those 12 collapsed to the floor above — and the collapse revealed FENCE and ARBNO were both **irrelevant**; only depth mattered. **The probe suite was never testing defer depth at all.** That is the durable lesson: a green board on shallow probes beside a red flagship program is not a puzzle, it is a statement about the probes.

## 5. SUSPECT AREA — A LEAD, NOT A CONCLUSION (verify, do not inherit)

The defer road is `rt_patv_defer_get_pat_dtp` → `dtp_fn_of` → the blob call in `bb_match_defer.cpp` (template loads `fn=[dtp+0]`, rides `dtp` in `rdx`, `r10`/`r11` carry the γ/ω wires). A defer whose **target is itself a defer** re-enters that road. Whether the inner activation clobbers the outer's `dtp`, its wires, or its resume record is **unmeasured** and is the row's first real question.

## 6. THE ROW

`defer-depth-floor` (rank 0). **DONE-WHEN:** root cause named; `ptw_min_defer2_{floor,pp_L2,pp_L3,arbno,depth9}` oracle-identical in **both** modes if killswitch-clean (else investigation-only with the mechanism named); `pp_L0`/`pp_L1`/`defer1_arbno_ctl` controls unchanged; `board_beauty_m1.sh --modes m3` re-run and the **new** first-red line recorded; corpus fail-set no worse (m3 332/5 · m4 325/11); FINDING.

---

## 7. ⭐ ADDENDUM — BATCHES 3 AND 4 (Lon's design): TWO MORE CLASSES, BOTH AT DEPTH 1

Lon, s183 in-chat: *"make up batches of 20 reasonable beauty.sno like Expr patterns, take subsets. Add combo crazy. And just see how many fail. You can keep going as long as you find varying classes of failures."*

Both batches were built so the rank-0 floor could **not** mask the result — every witness below is **one** defer level, verified rather than assumed.

### Batch 3 — 336 grammars of beauty's real Expr shape `E = <primary> <wrap>( <op> *E <reduce> | epsilon )`
**324 AGREE · 12 DIFF**, and all 12 shared one signature: `primary = ARBNO`, `wrap = bare ALT` (not FENCE). Ablating gave **two** distinct minimal reds:

| witness | oracle | SCRIP | |
|---|---|---|---|
| `ptw_min_arbno_nullalt_falseaccept` — `E = ARBNO('a') ('+' \| '')`, subj `'a+a+a'` | **nomatch** | **match** | ⛔⛔ **FALSE ACCEPT** |
| `ptw_min_arbno_altrec_falsereject` — `E = ARBNO('a') ('+' *E \| '')` | match | nomatch | false reject |

**The false accept is the campaign's first.** Every other red found in 4.5 months is a false *reject*; this is the direction that makes a parser silently swallow malformed input. It needs all three ingredients, each with a green control checked in beside it: ARBNO as the left element (`SPAN` is green), an ALT whose **last** arm is the null string (`('+' | 'z')` green), the null arm **last** not first (`('' | '+')` green), and a subject the whole pattern must reject (`'aa+'`, `'a+'`, `'aaa'` all agree).

### Batch 4 — 450 grammars over primary × capture × positional × anchoring
**358 AGREE · 90 ORACLE-BAD · 2 DIFF**, collapsing to one class:

| witness | oracle | SCRIP |
|---|---|---|
| `ptw_min_arb_immed_retry` — `E = ARB $ v`, `'a+aa' POS(0) *E RPOS(0)` | **match** (`v='a+aa'`) | **nomatch** |
| `ptw_min_arb_cond_ctl` — the same with conditional `.` | match | match ✓ |
| `ptw_min_span_immed_ctl` — `$` on a non-retrying element | nomatch | nomatch ✓ |

**An immediate assignment (`$`) kills a generator's retry; a conditional (`.`) does not.** ARB must extend to reach `RPOS(0)` and never does. The controls isolate it to the *conjunction* — not `$` alone, not ARB alone.

⛔ **The 90 ORACLE-BAD rows are not SCRIP verdicts.** Live `sbl` itself SIGSEGVs on many `$`-capture shapes. The runner classifies oracle failure *before* comparing, which is why they are excluded by construction — a harness that compared blindly would have booked 90 phantom passes or 90 phantom fails depending on which way it fell.

### Running tally of what the batteries have produced
| battery | rows | reds | new classes |
|---|---|---|---|
| 1 — shallow combos | 168 | 1 | 0 (found nothing) |
| 2 — deep 3/5/7/9-level chains | 168 | 12 | **1** — the defer-depth floor (rank 0) |
| 2b — depth-1 heavy backtracking | 120 | 19 | **1** — `arbno-alt-fence-L1` (15 of the 19 collapsed into the floor) |
| 3 — beauty Expr shapes | 336 | 12 | **2** — false accept + its false-reject twin |
| 4 — captures & positionals | 450 | 2 | **1** — `$` kills a generator's retry |

**Classes are still varying, so the method has not exhausted itself.** The next unexplored axes: replacement statements (`S PAT = X`), unanchored scanning with `&ANCHOR`/`&FULLSCAN`, `TAB`/`RTAB` as the forcing tail, and multi-statement programs where a pattern value is rebuilt between matches.
