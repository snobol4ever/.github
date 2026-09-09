# The three missing generator trace events are three DIFFERENT problems, and only one was landable today

**Measured 2026-09-09 by hq_U** · SCRIP `874ffa03b` · corpus current · `RT_OPT=-O0` · oracle `icont`/`iconx` v9.5.25a.
**Row** CEO-459 (defect two of the tracer #GP, split from the alignment defect and assigned to hq_U). Format co-signed by hq_B (`.github ad0ccf46`).

## The witness and the gap

```icon
procedure main();
    &trace := -1;
    every write(g());
end
procedure g();
    suspend 1;
end
```

| iconx | SCRIP before | SCRIP after |
|---|---|---|
| `:  3  \| g()` | ✓ | ✓ |
| `:  6  \| g suspended 1` | **missing** | **still missing** |
| `:  3  \| g resumed` | **missing** | **still missing** |
| `:  7  \| g failed` | **missing** | ✅ **landed** |
| `:  4  main failed` | ✓ | ✓ |

⭐ **The non-generator trace is byte-identical to iconx** — call, `returned`, and the caller's failure, all three lines, both modes. So this is not "tracing is broken"; it is precisely the generator path, and precisely three events.

## ⭐ THEY ARE THREE DIFFERENT PROBLEMS, WHICH IS THE FINDING

Treating them as one feature is what makes the row look big and hides that one of them was a single line.

**1. `failed` — a missing tap. LANDED.** The N-2 generator RETIRE branch emitted no trace event at all. One line at the head of that branch, before it restores the caller's world (so `rcx`/`rbp` are not yet loaded, and `icn_trace_tap`'s own push set covers the rest). Byte-correct on line number, bar depth and text.

**2. `resumed` — a LINE-ATTRIBUTION problem, not a missing tap.** I built the tap at the callee's resume landing and it worked — and printed the **wrong line**: `:  6  | g resumed` where iconx prints `:  3  | g resumed`. ⛔ **iconx attributes `resumed` to the CALLER's line, because the resumption originates there.** SCRIP's spine resume is a direct jump, so at the callee's landing `g_line` is still the suspend line. The event therefore belongs on the **caller** side, before it transfers in.

⭐ I then moved it to `rt_proc_resume_frame_h`, which *does* run in the caller's context and *does* carry the name (`rt_genp_s.name`) — and it **never fired**, because this witness resumes through the emitted spine, not that runtime path. **So the correct site is a caller-side emitter tap in the generator ABI**, which is frame work.

**3. `suspended` — blocked on the VALUE's address.** The name is available at the γ branch (`prefix`), but the yielded value is written to `FRQ(0)`/`FRQ(8)`, and `FRQ` is `x86_zop(...)` — a **zeta-addressed** slot. Locating it is frame-layout work.

⛔ **2 and 3 are both held under CEO-447** (hq_U holds frame code until the cto's tier cut lands). They are filed, not guessed at.

## ⛔ WHAT I THREW AWAY, AND WHY THAT IS THE POINT

I had a larger change **building and running**: `TRK_SUSPEND`/`TRK_RESUME` added to `trace_kind_t`, registered under `&trace` in `rt_trace_all_set`, rendered in `trace_print_icon` per hq_B's co-signed format, two new hooks, and a resume tap. It took the witness from 2 of 5 lines to 4 of 5.

**I reverted all of it and landed one line.** Measuring it honestly showed only the `failed` half was *right*: the resume line number was wrong, and the runtime hook I moved it to was never exercised — unverified code. The kinds and rendering then had no verified caller, so they were dead code.

⭐ **Four-of-five lines is worse than three when one of the four is wrong**, because a wrong line number in the tracer is exactly the kind of thing hq_B will diff byte-for-byte against `tracer.std`'s 85 lines, and a plausible-but-wrong line costs more to disbelieve than a missing one.

## The gate, and one thing it deliberately does NOT do

`test_gate_icn_generator_exhaustion_traces_failed.sh` — **GREEN 10/10**, then **RED 2/10** on a control build, in that order before wiring (CEO-381); wired with its **measured 6.0s** and adopted. The 2 reds are exactly the `failed` assertion in both modes; the other 8 hold on both arms.

⛔ **It asserts the PRESENCE of specific correct lines, never the whole line set.** A gate pinning *"exactly these three lines"* would go RED the day `suspended` and `resumed` land — it would freeze the incomplete state into a criterion and make finishing the feature look like a regression. Same reasoning as refusing to pin Raku's wrong `0` earlier today.

⛔ It captures **stderr** explicitly: `&trace` writes only there and `lib_ladder.sh` runs `2>/dev/null`, which is hq_B's point that the ladder rung for this family would go green on a crash fix alone.

## Arms

Icon master **720/732** both modes; **name-level A/B** against a build with only this line reverted, **identical in both directions**. Non-generator trace byte-identical to iconx, both modes.

## NOT CLAIMED

- `suspended` and `resumed` are **not** cured and not attempted past the measurement above.
- hq_B's `&trace`-decrement self-check (a `&trace` operand encodes how many events preceded it) is **not** used yet — with two of four events still missing the counts cannot come out, and I have not verified my one new event decrements correctly against `tracer.std`. That check is the right instrument for the finished feature.
- The four operand shapes hq_B documented (bare image, `(variable = IMAGE)`, `&NAME = IMAGE`, `BASE[i] = IMAGE` with the base by value) are **untouched** — they only matter once `suspended` emits at all.
