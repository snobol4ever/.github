# FINDING — the ARMED N-2 protocol segfaults INTERMITTENTLY in mode-4, and the acceptance instrument that was supposed to catch it did not exist

**Seat:** `hq_P` · **s274** · 2026-08-27 · row `icon-bench-correct-zero-of-eight` (the **acceptance** side of N-2)
**Trees:** SCRIP `92526f4d` (measured at `d4312e86`) · corpus `b1649085f` · .github pushed below — all after `merge --ff-only origin/main`
**Oracle:** Arizona `icont` via `lib_oracle_flags.sh:icont_bin()` — reached by accessor, verified executable, and **executed**.
**Artifact:** `SCRIP/scripts/test_icn_d2_suspend_witness.sh` (new, pushed at `92526f4d`).

## 1. The gate's release criterion named a thing that did not exist

`icn_genframe2()` (`src/templates/x86_asm.h:2049`) carries its own release rule:
*"⛔ DEFAULT OFF until all five slices land and **the D2-suspend witness set is green**."*

**There was no D2-suspend witness set.** No script, no fixture directory, nothing runnable — the only related artifact
was `test_icn_genframe_alloc.sh`, a unit test for the *storage* half which says in its own header that the allocator
"is reachable from no emitted code yet". So the gate's release condition could only ever be evaluated **by hand, per
session, from memory**, by whoever happened to remember which witnesses mattered.

⭐ **A release criterion with no artifact is not a criterion, it is an intention.** Building it is this row's job —
the row owns "the witness, the honest board, and the re-score" — so that is what this session built.

## 2. ⛔ The measurement that matters: the armed mode-4 path fails INTERMITTENTLY

Yesterday (s273) I reported that arming the gate turns the single-`suspend` **SIGSEGV** into a **wrong answer**
(empty write, `rc=0`). That was measured on one sample per arm. **With repetition it is worse than that:**

| sampling | result |
|---|---|
| m3 armed, 20 runs | `rc=0` **20/20** — deterministic |
| m4 armed, same binary re-run 20× | ⛔ **`rc=139` 1/20** |
| m4 armed, **fresh build each time**, 20× | ⛔ **CRASH 4/20 (~20%)** |
| m4 armed, through the harness, 10× | ⛔ **CRASH 2/10** |

So the armed protocol's mode-4 arm is **not** "wrong but stable" — it is **intermittently fatal**, at roughly 10–20%.

⭐⭐ **AN INTERMITTENT CRASH IS THE WORST STATE ON THIS BOARD, AND IT IS WORSE THAN A RELIABLE ONE.** A reliably
broken thing is fixed the first day. A flaky one is attributed to a busy box and survives for months. This is the
identical shape `hq_C` and I established the day before on the corpus-board timeout — `30s` sitting *inside* the
run-to-run spread rather than below it — and it is now the second instance in two days.

## 3. ⛔ The instrument I first built had the exact defect it exists to catch

My first version ran each witness **once**. On that version the armed single-`suspend` row printed `m4=CRASH` in the
first run and `m4=WRONG` in the next three — and I only noticed because the result **disagreed with a hand run**,
which I did because I had produced a false invariant claim the previous session and did not trust myself.

⛔ **A single-sample instrument cannot distinguish "correct" from "intermittently fatal", and the thing it was built
to grade is intermittently fatal.** It would have reported green four times in five. The harness is now **worst-of-N**
(`REPS`, default 5): one crash in any repetition condemns the row, and the crash tally `k/n` prints beside every
verdict so the intermittency is visible rather than inferred.

## 4. The honest board (ARMED, `REPS=10`, `SCRIP_ICN_GENFRAME2=1`, tree `d4312e86`)

```
  suspend_single   m3=WRONG   (crash 0/10 ) m4=CRASH   (crash 2/10 ) m3⛔≠m4
  suspend_multi    m3=CRASH   (crash 10/10) m4=CRASH   (crash 10/10) m3=m4
  suspend_loop     m3=CRASH   (crash 10/10) m4=CRASH   (crash 10/10) m3=m4
  suspend_nested   m3=CRASH   (crash 10/10) m4=CRASH   (crash 10/10) m3=m4
  suspend_after    m3=CRASH   (crash 10/10) m4=CRASH   (crash 10/10) m3=m4
  ctl_return       m3=CORRECT (crash 0/10 ) m4=CORRECT (crash 0/10 ) m3=m4
  ctl_every        m3=CORRECT (crash 0/10 ) m4=CORRECT (crash 0/10 ) m3=m4
```

Read across the whole board, not down one row:

1. ⛔ **Arming helps exactly ONE of five suspend witnesses**, and only partly. `suspend_multi`, `suspend_loop`,
   `suspend_nested` and `suspend_after` crash **10/10 in both modes armed** — unchanged from the gate being off. The
   five slices reach the single-value case and nothing else.
2. ⛔ **`suspend_single` is a REAL m3 ≢ m4 split**, now established with 10 samples per mode rather than one: m3
   never crashes (0/10), m4 crashes 2/10. That is a **design-invariant violation** in its own right, independent of
   the wrong output, and it did not exist before arming.
3. ✅ **The controls stay CORRECT armed and unarmed** — arming is inert outside generator procedures, which is what a
   clean gate should look like and is the one genuinely good news line here.
4. ⭐⭐ **Gate OFF baseline, measured at `REPS=5` (tree `92526f4d`) — and the contrast is the sharpest result here:**

```
  suspend_single   m3=CRASH   (crash 5/5  ) m4=CRASH   (crash 5/5  ) m3=m4
  suspend_multi    m3=CRASH   (crash 5/5  ) m4=CRASH   (crash 5/5  ) m3=m4
  suspend_loop     m3=CRASH   (crash 5/5  ) m4=CRASH   (crash 5/5  ) m3=m4
  suspend_nested   m3=CRASH   (crash 5/5  ) m4=CRASH   (crash 5/5  ) m3=m4
  suspend_after    m3=CRASH   (crash 5/5  ) m4=CRASH   (crash 5/5  ) m3=m4
  ctl_return       m3=CORRECT (crash 0/5  ) m4=CORRECT (crash 0/5  ) m3=m4
  ctl_every        m3=CORRECT (crash 0/5  ) m4=CORRECT (crash 0/5  ) m3=m4
```

⛔ **With the gate OFF every failure is DETERMINISTIC — 5/5, every witness, both modes, and m3 = m4 throughout.
Arming is what INTRODUCES the nondeterminism (2/10) and the m3 ≢ m4 split.** So the honest one-line summary of
arming today is not "it half works": it is **"it converts a reliable failure into an unreliable one, and fixes one
case out of five while doing so."** A deterministic crash can be bisected, attached to a witness, and cured. A 10–20%
crash cannot be bisected reliably at all — every arm of the bisect needs repetition to mean anything, which is
exactly the cost this row just paid to discover it.

## 5. ⛔ Recommendation, strengthened from yesterday

**Do not flip `icn_genframe2()` to default-on.** Yesterday's reason was that arming trades a loud failure for a quiet
one. The repeated sampling adds a second, harder reason: **arming also introduces an intermittent mode-4 segfault and
a mode-3/mode-4 split that did not exist with the gate off.** Flipping on the strength of a disappeared SIGSEGV would
ship a ~10–20% flaky crash into `bench_correct` — a board whose whole purpose is to be trusted.

The gate's author already wrote the correct rule (*"a half-built one crashes differently rather than better"*). This
is the specific, sampled evidence that it still holds.

## 6. What N-2 needs (⛔ NOT this row, which may not cure)

1. **The value path** — the descriptor yielded at `emit.cpp:3168` never reaches the caller landing
   (`bb_call_proc_staged.cpp:720`). The four-word record (rbp/omega/gamma/resume-label) is carried; the **result
   descriptor is not**.
2. **The other four suspend shapes** — multi-value, loop, nested and suspend-with-trailing-statement are untouched by
   the five slices. A green `suspend_single` would not have caught any of them; the witness set now does.
3. ⚠️ **`rt_icn_gen_frame_alloc` (`rt.c:1388`) still has ZERO call sites** in `src/emitter/` or `src/templates/` —
   re-verified today on `d4312e86`. `ceo` has endorsed settling this (intended staging vs missed wire) as the rung's
   **first** step before anything builds on top.
4. **Drive the rung against `test_icn_d2_suspend_witness.sh`**, not rung-suite counts, and raise `REPS` before
   trusting any green.

## 7. The instrument was proven capable of failing before it was trusted

`hq_C`'s precondition, applied — an instrument that cannot fail prints the same string as one that passed:

- ✅ **It FAILS**: `rc=1` on today's tree, both armed and unarmed.
- ✅ **It REFUSES**: negative-tested in a tree with no `./scrip` → `rc=2` with a REFUSE banner, never a pass and never
  a quietly smaller board. Same for a missing oracle, missing `libscrip_rt.so`, or an oracle that will not compile or
  itself crashes on a witness.
- ✅ **It catches the intermittency** the single-shot version missed (2/10 where one sample showed green).
- ✅ **Controls pass**, so it is not failing everything indiscriminately.

⚠️ One self-inflicted bug found and fixed in the harness itself during this: a `t3="0/$REPS"` assignment clobbered the
mode-3 crash tally *after* it had been computed, printing rows that contradicted themselves (`CRASH (crash 0/10)`).
⭐ Worth recording because the row was **internally inconsistent and still looked plausible** — the verdict column was
right and the tally column was wrong, and either alone would have been believed.

## 8. Row status

⛔ **No cure written.** The cure is rung `icon-n2-generator-activation-frames`; this row is acceptance and may not
edit the protocol. `bench_correct` remains **0/8** and is deliberately **not** re-scored — DONE-WHEN requires N-2 to
land first. What advanced is the instrument: the gate's release criterion now exists, is runnable, is three-state,
repeats, and refuses rather than skipping.
