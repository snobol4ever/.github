# FINDING s189 — THE SIX FUZZ HANGS ARE **THREE** CLASSES, AND THE ONE I CURED WAS HALF A MECHANISM LEFT RUNNING AFTER THE OTHER HALF WAS DELETED

**Seat8 `/home/claude8`, Claude Opus 5, 2026-08-20. Queue row `fuzz-hang-batch` (rank 1).**
**SCRIP: 2 files (`src/emitter/emit.cpp`, `src/templates/bb_match_arbno.cpp`), one staged fact + one gated edge. corpus: 6 reduced witnesses + live-oracle `.ref`s. RT_OPT `-O0`.**

---

## ⭐ THE ROOT CAUSE (class A), IN ONE SENTENCE

**`emit.cpp:1436` re-aims a FENCE-rooted ARBNO body's resume onto the ARBNO's own `af` glue, so `bb_match_arbno_frameless()`'s φ edge `jne PAIR(1)` is a LITERAL SELF-LOOP — it re-tests an unchanged δ against an unchanged Δ0 forever — because the compensating seal handling was deleted while the re-aim kept firing.**

The emitted asm says it without interpretation. Failing witness vs its passing sibling, **the same program modulo one `FENCE(...)`**, whole-graph diff = **three lines**:

| site | `ARBNO(LEN(1)) TAB(3)` — PASS | `ARBNO(FENCE(LEN(1))) TAB(3)` — HANG |
|---|---|---|
| σ null-progress guard | `je n2_match_len_β` | `je n0_match_arbno_af` |
| φ retract test | `jne n2_match_len_β` | `jne n0_match_arbno_af` ⛔ **itself** |

`n2_match_len_β` is `sub r14d, 1; jmp n0_match_arbno_af` — **the only instruction in the whole graph that restores δ.** It is still emitted, still correct, and under the seal **nothing jumps to it**: measured, that label carries **2 jump refs unsealed and 0 sealed.** Aim the retract at the exhaust test itself and the exhaust test can never become true.

## ⭐⭐ THE COMPENSATING HALF WAS DEAD, AND HAD BEEN SINCE THE D-1 TAIL DELETE

`op_tail_seal` — the flag that says "this body is FENCE-rooted" — is assigned in exactly one place, `emit.cpp:1182`, inside

```c
if (!_k16r && 0 && _tailc) { ... g_emit.op_tail_seal = (nd->n_operands>3 && nd->operands[3]==nd) ? 1 : 0; ... }
```

⛔ **`&& 0`.** Permanently false since the D-1 "carry-the-tail arm is GONE" delete. Its only reader was `bb_match_arbno_tail()`, which the dispatcher no longer selects. So the seal fact read **0 for every node in the tree** while the `:1436` re-aim it was supposed to compensate for went on running.

⛔ **AND THE TREE ALREADY KNEW.** Three independent places state this exact defect and none of them reached the frameless arm:
- `emit.cpp:1192` states the contract in words: *"with the seal present, emit.cpp:1386 retargets body resumes to the fail glue, so an admitted af->PAIR(1) edge **loops af->fail-glue->af forever**. **Exhaustion under seal IS ω.**"*
- s126 measured this shape and named it a LIVELOCK (`rc=124`).
- **`bb_match_arbno_frame()` has never had the bug** — it omits the identical edge under seal via `op_arbno_body_actframe`.

The frameless arm is the one place the guard was never spelled. ⭐ **The generalisable move: when one arm of a family is cured by a flag, the flag's *staging* must outlive the arm that introduced it — a delete that removes the last READER of a fact silently removes the fact.**

**MEASURED, the exposure is exactly the frameless arm:** sealed bodies routing to ARBNO-FRAME (`ARBNO(FENCE(LEN(1) . v0))`, `ARBNO(FENCE('a'|'ab'))`) are **green**; sealed bodies routing to FRAMELESS (`ARBNO(FENCE(LEN(1)))`, `ARBNO(FENCE(LEN(1) LEN(1)))`, `fz_hang_06`) **hang**. `SCRIP_ARBNO_DIAG=1` is the instrument.

## ⛔⭐⭐ THE ROW'S REAL ANSWER: SIX WITNESSES, **THREE** MECHANISMS — AND ARBNO IS NOT THE COMMON FACTOR

The brief warned several might be faces of one mechanism. They are faces of three, and the framing that put them in one row (they all look like ARBNO bugs) is wrong for five of the six.

| witness | minimal trigger, by ablation | ARBNO needed? | class |
|---|---|---|---|
| `fz_hang_06` | `ARBNO(FENCE(x))` | yes | **A — SEAL** ✅ **CURED** |
| `fz_hang_04` | capture `. v0` over a choice-bearing span | ⛔ **NO** | **B — CAPTURE** |
| `fz_hang_11` | ARBNO + ALT + `$ v0` | yes | **B — CAPTURE** |
| `fz_hang_16` | `$ v1` (no ARBNO in the program at all) | ⛔ **NO** | **B — CAPTURE** |
| `fz_hang_21` | `. v1` | ⛔ not for the hang | **B — CAPTURE** |
| `fz_hang_12` | nested ALT `(A \| (B \| C))` | ⛔ **NO** | **C — NESTED-ALT** |

**Class B is not an ARBNO defect, and — corrected against seat6's sibling row — it is not a *capture* defect either. It is a CONJUNCTION OF THREE, each independently ablatable to green:** (1) a capture (`. v` / `$ v`) applied to (2) a span of **two or more** elements whose (3) **last element is a choice point**.

| variant | verdict |
|---|---|
| `(BREAK('abc') (BREAK('+') \| REM)) . v0` | ⛔ **HANG** |
| `(BREAK('abc') REM) . v0` — alternation removed | PASS |
| `BREAK('abc') (BREAK('+') \| REM)` — capture removed | PASS |
| `((BREAK('+') \| REM)) . v0` — leading element removed | PASS |
| `(LEN(0) (BREAK('+') \| REM)) . v0` | ⛔ **HANG** |

`fz_min_capture_span_red` contains **no ARBNO** and hangs. The leading element is not about *what* it matches — `LEN(0)` reproduces it — only that one exists. The gdb spins agree: 04/16/21 sample inside `n*_match_assign_cond_α/β`, `PAT$N_γ` and `PAT$N_res`, never in an ARBNO box.

⭐ **THIS RECONCILES WITH seat6's s189 `fuzz-diff-batch`, which found "the alternation is the ingredient, every time" and falsified that row's capture framing.** Consistent, and it sharpens both: the alternation is **necessary** here too — it is simply not **sufficient**. My first cut said "capture class" on the strength of capture-removal alone, which is exactly the inference seat6's row convicts; the three-way ladder above is what the claim actually rests on. Class B and seat6's D-2 plausibly share one alternation-composition root under different wrappers, and should be read together before either is opened.

⛔ One honest ragged edge: `fz_hang_11` with the capture removed becomes **SIG11, not green** — capture is necessary for its *hang*, but a second defect sits underneath it.

**Class C is nested alternation.** `fz_min_nested_alt_red` survives ablating ARBNO **and** FENCE **and** the capture **and** the defer; flattening `(A | (B | C))` to `(A | B)` is green. This is the same nested-ALT-record class `emit.cpp:1192` already refuses for the ARBNO carrier (`_altnest`, s126: *"one-deep records compose by contiguity, two-deep do not yet"*) — the refusal protects the ARBNO carrier and this shape reaches the livelock by another road.

## ⭐ THE ANSWER THE BRIEF ASKED FOR FIRST: RETRY, NOT THE C ROAD — AND NOT A SLOW SEARCH

- **`--compile` terminates on all six** (rc=0, 30–53 KB of `.s` each). The loop is at RUNTIME.
- Every gdb sample lands in **emitted BB wiring** — `n0_match_arbno_af`, `n*_match_assign_cond_α`, `n*_match_alternate_β`, `n*_match_defer_α`, `PAT$N_γ`. Never in `pattern_match.c`. **The loop is in the RETRY.**
- ⛔ **All six still hang at 240 s in BOTH modes** while the oracle answers each in under a second. These are non-termination, not exponential blowup. (`ptrace_scope=1` here blocks `gdb -p` on a sibling; run the inferior under gdb and stop it with SIGINT.)

## ⛔ SAME OR DIFFERENT vs `ptw_min_defer2_hang` — **DIFFERENT MECHANISM**, and the row's guess is refuted

The brief asked this explicitly and expected "check whether these are the same **BEFORE** opening a new one." Five independent pieces of evidence say different:

1. **Different re-aim target, in the emitted asm.** `fz_hang_06`'s af is `jne n0_match_arbno_af` (itself). `ptw`'s af is `jne n1_match_alternate_β` — a different label, a real box.
2. **Different arm.** 06 rides **FRAMELESS**; ptw rides **ARBNO-FRAME**.
3. **Different defer depth.** 06 reproduces with **ZERO** defer levels (`P = ARBNO(FENCE(LEN(1))) TAB(3)`, plain `P`). ptw needs **TWO**: at one level (`P = ARBNO('a'|'ab') RPOS(0)`, `*P`) it **PASSES**, and inline it **PASSES**.
4. **Different body trigger.** 06 needs FENCE-rooted; ptw needs an ALT body — `ARBNO('a')` passes.
5. ⛔ **The cure separates them, measured.** `ptw_min_defer2_hang` is **not among the 4 `.s` movers** and **still hangs** after the fix, at pristine. Stated plainly rather than buried: **this row does not clear it.**

`ptw` remains what HQ recorded — a residue of the rank-0 defer-depth floor that seat2's cure did not reach. Its ALT-body + two-defer shape is nearer class B/C than class A.

## RECEIPTS

**WATERMARK — pristine at SCRIP `47135a86` (re-proven after the mid-session rebase onto seat2's `4a3f8606`, which touches the emitter, so the re-proof was not a formality), corpus `2ae84618`, RT_OPT `-O0`, oracle verified alive, all `.ref`s re-verified live with ZERO drift:**

- **corpus board `m3 332/5 · m4 325/11 · SKIP 1 (337)`** — the LIVE CURSOR baseline **to the digit**, fail-set identical **by name**.
- **`.s` sweep, default vs `SCRIP_ARBNO_SEAL_OMEGA=0`, 1067 comparable programs: 4 MOVERS**, all four the FENCE-in-ARBNO class — `fz_hang_06` **CURED both modes**; `ptw_min_arbno_fence_lit` green before and after; `fz_diff_13` red before and after with its answer unmoved; `parser/unary_not` unmoved. **ZERO regressions.**
- **RULES step-4 regens ×5: `changed=0`** on 623+22 programs — an independent second path to the same blast radius.
- **Killswitch proven, not asserted:** `SCRIP_ARBNO_SEAL_OMEGA=0` returns `fz_hang_06` and `fz_min_arbno_fence_seal` to `rc=124` **verbatim**.
- `fz_hang_06` m3 **and** m4 now answer `nomatch` == its live-oracle `.ref`.

**Checked in (corpus `2ae84618`), three reds kept red per law 0d:** `fz_min_arbno_fence_seal` (+`_nofence_control`) · `fz_min_capture_span_red` (+`_control`) · `fz_min_nested_alt_red` (+`_control`).

## ⛔ A PROBE RETRACTION, KEPT VISIBLE

Two probe batches this session produced confident, entirely false tables before being caught: a quoting bug wrote literal `'\''` into every generated `.sno` (every row read as an oracle syntax error), and a `$(... | head -1)` captured **`head`'s** exit status, so a hang reported `rc=0`. Both were caught only by looking at the generated file and re-running with the rc taken directly. **s188's rule holds and cost me twice: a probe not shown to do the thing it claims to do is not evidence.**

## NEXT

1. **Class B (capture over a choice-bearing span)** — 4 of the 6, the largest class, and `fz_min_capture_span_red` is a 2-line witness with no ARBNO. Own row.
2. **Class C (nested ALT)** — `fz_min_nested_alt_red`; connect to `_altnest` at `emit.cpp:1192`.
3. `fz_hang_11`'s SIG11 underneath its capture — a second defect, own witness.
4. ⛔ **Sweep for the other `&& 0` staging blocks.** `op_tail_seal` was not special: the D-1 delete removed readers, and any fact staged only inside a retired arm is now silently 0 for the whole tree. This one cost a livelock; there may be siblings.
