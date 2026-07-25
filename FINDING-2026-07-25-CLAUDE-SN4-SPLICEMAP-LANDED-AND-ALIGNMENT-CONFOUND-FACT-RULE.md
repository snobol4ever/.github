# FINDING 2026-07-25 (s156, Claude) — R3 SPLICEMAP LANDED (opt-in): the anonymous blob is NAMED · DB-2a slot0 seed PROVEN DEAD but worth ~2.6%, not the 6–10% the wall clock claimed · ⛔ NEW FACT RULE: WALL-CLOCK A/B ON A SMALL CODEGEN CHANGE MEASURES CODE ALIGNMENT, NOT THE CHANGE

## HEADLINE

R1 (DB-2 α-diet) was the ruled next rung. Measuring α anatomy first — as the s155 cursor directed — surfaced two things the ladder did not expect:

1. **The primary metric was unaimable.** 92.1% of treebank's D1 write misses (168,928 of 183,501) were attributed to `???`. The s155 cursor already recorded this blindness for claws5/json at 97–100% and scheduled it as R3 (SPLICEMAP) *behind* R1/R2 — but R1's own headline number is a **miss** count, so R1 was scheduled to be tuned blind against its own metric. **R3 is a PREREQUISITE of R1, not a successor.** It is now landed (opt-in) and treebank's write-miss cost is fully named.
2. **The wall-clock A/B protocol cannot resolve changes of this size.** Eliding two stores produced a reproducible **10% "regression"** on claws5 that turned out to be a pure code-alignment artifact. See the FACT RULE below — this invalidates the measurement method for every remaining α-diet rung, not just this one.

## R3 SPLICEMAP — LANDED, OPT-IN (`SCRIP_SYMMAP=1`)

**Root cause (measured, not guessed):** `src/driver/scrip.c` emits `.globl <blob>_α` for every emitted chain and *nothing else* — no `.type`, no `.size`. The ELF symbols therefore carry `st_size=0` and no address RANGE, so every profiler samples inside a blob and attributes it to `???`. `nm -S` on the pre-change binary shows 36 `proc_PAT` symbols, all sizeless.

**Fix:** `.type <blob>_α, @function` before `emit_chain`, `.size <blob>_α, .-<blob>_α` after it, at BOTH emission sites (the patproc site ln 755 and the proc site ln 1185). Pure ELF metadata — **not one instruction byte changes**.

**Result on treebank (cachegrind, `--smc-check=all-non-file`, `ulimit -s unlimited`):**

| blob | D1 write misses | share of total |
|---|---|---|
| `proc_PAT$2_α` | 89,265 | **48.6%** |
| `proc_PAT$1_α` | 40,192 | 21.9% |
| `proc_PAT$0_α` | 37,551 | 20.5% |
| `proc_PAT$3_α` | 863 | 0.5% |
| still `???` | 1,075 | 0.6% |

**99.4% of the formerly-blind region is now named.** First aimable heat map the α campaign has had.

**⭐ IMMEDIATE READING — FRAME SIZE IS NOT THE DRIVER.** `PAT$3` has the LARGEST carve on the board (368B) and owns 0.5% of the misses; `PAT$2` (288B) owns 48.6%. The cost is **activation count × distinct cache lines touched per activation**, not bytes carved. This directly re-aims DB-2c: "right-size the frame" is the wrong lever stated that way — **reduce the number of distinct lines an activation touches** is the right one (cluster the touched offsets, do not merely shrink the span).

Opt-in per house style (ARBNO_LATCH / SEQ_FOLD precedent): this session's default `.s` stays byte-identical and the change is provably inert. **Default-flip is its own rung** and carries the `.s` regen ×3 it implies.

## DB-2a — slot0 seed: DEAD, and worth ~2.6%

**Census (new, all 5 demos / 31 PAT$ blobs):** every α prologue is a fixed 13-instruction shape touching exactly two regions — offsets `0,8` (cache line 0) and the top 64 bytes. For every blob with carve ≥160B those are **2–5 cache lines apart**; line 0 is touched for nothing but the two slot0 zero-fills, at the coldest end of a downward carve.

**Liveness PROVEN.** `SCRIP_SLOT0_POISON=1` seeds slot0 with `0xA5A5A5A5A5A5A5A5` instead of 0. Full crosscheck, **both modes, 315 programs**: watermark-identical (m3 314/1 · m4 309/4 · DIVERGE=3, failing sets unchanged). Poison is strictly more aggressive than the elision it licenses — elision leaves whatever the stack held, which can coincidentally be zero and hide a reader; poison never can. **Nothing reads slot0 expecting an implicit zero for flat_lex=0 jmp-entry citizens.**

**Worth (deterministic, layout held constant via the pad lane):**

| metric | OFF | ELIDE+PAD | delta |
|---|---|---|---|
| Ir | 7,418,976 | 7,476,844 | +57,868 (the nops) |
| D refs | 3,356,495 | 3,243,715 | −112,780 (−3.4%) |
| D1 write miss | 183,501 | 178,827 | −4,674 (−2.6%) |
| LL write miss | 181,964 | 177,299 | −4,665 (−2.6%) |

The Ir delta pins activations at **~57.9k** and D-refs drop by exactly 2× that — the arithmetic closes. Only ~8% of activations actually took a cold-line miss on slot0; the rest reuse warm stack lines. **So the honest value of DB-2a's slot0 arm is ~2.6% of the write-miss pot, not the 6–10% the wall clock suggested.** Left OPT-IN (`SCRIP_SLOT0_ELIDE=1`), default OFF: the gain is real but small and the unpadded form perturbs layout (see below), so the default flip should ride with a layout-aware rung rather than land alone.

## ⛔ FACT RULE — A WALL-CLOCK A/B ON A SMALL CODEGEN CHANGE MEASURES CODE ALIGNMENT, NOT THE CHANGE (Claude, s156)

Eliding slot0 removes **17 bytes** from every blob prologue, shifting every downstream byte's address and re-rolling branch/loop alignment throughout the blob. Measured on claws5 with an adequate 3.3s window, repeated:

| claws5 lane | ratio |
|---|---|
| OFF | 0.67, 0.67 |
| ELIDE **+PAD** (17 nop bytes, layout held) | **0.68** |
| ELIDE (layout shifted) | 0.74, 0.75 |

**The 10% "regression" was entirely alignment.** Two stores in a prologue cannot cost 10% of wall in either direction; the arithmetic above (2.6% of write misses) confirms they do not. The same confound inflated treebank's apparent 6.5% "gain," and treebank's OFF lane itself swung 1.23 → 1.32 between passes twenty minutes apart — a noise band that RIVALS the effect being attributed.

**THE RULE:** any codegen change that adds or removes bytes gets a **layout-held control lane** (`SCRIP_SLOT0_PAD` is the reference implementation — pad the delta with multi-byte nops so every downstream address is preserved) **and** a deterministic counter reading (cachegrind Ir / D1mw / DLmw), before ANY wall-clock number is quoted as the change's effect. A wall-clock A/B alone is admissible only for changes large enough that alignment cannot plausibly account for the delta. ⚠ THE TELL: this session was one measurement away from reporting "slot0 elision: +6.5% treebank, −10% claws5, mixed verdict, needs per-blob gating" — a conclusion that is *entirely an artifact*, and which would have sent the next session building a per-blob gating heuristic to solve a problem that does not exist.

LIMITATION (do not oversell): a markdown rule cannot force a session to build the pad lane. It makes the control cheap (the mechanism now exists and is copyable) and the omission reviewable. **Reviewer enforcement: reject any α-diet perf claim quoted from wall clock alone.**

## GATES (all green)

- Crosscheck **×4 lanes** — default / SLOT0-POISON / SLOT0-ELIDE / SYMMAP — all **m3 314/1 · m4 309/4 · DIVERGE=3**, identical failing sets (`test_case`; m4 `214/215/216_indirect_goto`), watermark-exact vs s155.
- 10 working-set demos m3: **10/10** under default, poison, elide, and symmap.
- Smokes **7/7** both modes.
- Default `.s` **byte-identical** to the pre-change compiler, verified 3× across the session (after each of the three edits).
- R10 medium agreement verified: `as` on the TEXT poison immediate (`-1515870811`) reproduces the BINARY arm's hand-encoded `48 c7 04 24 a5 a5 a5 a5` exactly.
- Demo output under cachegrind byte-compared to `.ref`.


## ⚠ SIDE CATCH — THE `.s` ARTIFACTS WERE STALE SINCE s154 (all three corpora)

The step-4 regen sweep committed **30 changed artifacts** across all three scripts (4 benchmark, 21 feature, 5 demo) — despite this session's default compiler output being byte-identical (verified 3×). **None of the drift is from s156.** Verified mechanically: `grep -c` for `.type`/`.size`/slot0 markers in every one of the three diffs returns **0**; every changed line is a jmp-target rename of the form `jmp xchain0_n0_af` → `jmp proc_PAT$0_ω` / `jmp xchain0_n0_as` → `jmp proc_PAT$0_γ`.

That is the **s154 H1b SEQ-GLUE FOLD** signature (trivial FC/SEQ-STATIC `as:jmp γ` / `af:jmp ω` stubs aliased at mint and chased at every jmp funnel). So the artifacts had been stale for TWO sessions: s154's cursor listed "`.s` regen ×3" as OWED, and s155's cursor then reported "regen ×3 zero drift" — but zero drift was reported against an artifact set that had never absorbed s154's own fold. Whatever s155 regenerated, it did not cover these 30 files.

This is exactly the failure mode RULES.md step 4 warns about in its own scope clause — artifacts that **LIE about the compiler's real output**. Two consequences worth carrying forward: (a) a "regen ×N zero drift" claim is only meaningful if the run is shown to have touched the corpora it names — quote the script's file-changed count, not just the word "zero"; (b) when a regen after an inert change produces drift, that drift is EVIDENCE OF A PRIOR MISSED SWEEP and should be diffed for provenance before being attributed to the current session — the marker-grep above is the cheap way to do it.

## TOOLING NOTE (cost me a cycle — record it)

Cachegrind **segfaults** on SCRIP m4 binaries without `ulimit -s unlimited` and `--smc-check=all-non-file`. `scripts/profile_callgrind.sh` already carries both; a hand-rolled harness will not. Copy the flags from that script rather than reinventing. `valgrind` is NOT preinstalled in the container — `apt-get install -y valgrind` (no sudo; sudo is absent and returns 127).

## NEXT

1. **SPLICEMAP default-flip rung** (+ `.s` regen ×3). It is inert metadata and every subsequent rung wants it on.
2. **Re-aim DB-2c** as "reduce distinct lines touched per activation," not "shrink the frame" — `PAT$3` disproves the size framing. With SPLICEMAP on, take the per-instruction annotation inside `proc_PAT$2_α` (48.6% of the pot) and see which of its 10 touched offsets actually miss.
3. R2 granted-ALT defer arms unchanged.
4. Every rung from here: pad lane + cachegrind counters before quoting wall.

RT_OPT=`-O0` throughout. **`handoff_status.sh` is the push truth — not this block.**
