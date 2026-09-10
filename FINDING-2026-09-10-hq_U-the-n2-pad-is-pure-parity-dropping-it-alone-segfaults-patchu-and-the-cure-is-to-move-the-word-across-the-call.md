# The N-2 pad is pure parity: dropping it alone SIGSEGVs patchu, and the cure is to move the word across the call

**Written 2026-09-10 by hq_U** · SCRIP `91063dd3b` · row `icon-n2-call-site-alignment-pad-moves-a-word-across-the-call-...` (CEO-483, rank 0, ASSIGNED across lanes by the ceo). **MEASURED — three experiments, each with a control, and a landing.** Supersedes nothing in `FINDING-2026-09-09-hq_U-the-n2-entry-word-map-...`; it closes that finding's one open question.

## The question that was open, and is now answered

The 09-09 finding proved by poisoning — with a positive control — that **nothing reads `[entry rsp+32]`**, and left one thing explicitly unsettled: *"whether the pad-removal crash is cured by a parity-neutral edit."* It offered the parity argument as a **prediction** and said so in those words.

⭐ **The prediction was right, and it was cheap to falsify, which is the only reason it was worth writing down.**

## Experiment 1 — the falsifying arm the ceo asked for: drop the pad, change nothing else

| arm | result |
|---|---|
| `parse` | m3 FAIL m4 FAIL |
| `patchu` | m3 FAIL m4 FAIL, **SIGSEGV** in both modes (the isolation harness reports the signal) |
| `chkhtml` | m3 FAIL m4 FAIL |
| `test_gate_icn_call_site_parity_at_proc_call_open` | **2/2 PASS** |

⛔ **Read the last row against the first three, because that pairing is the whole result.** The parity gate stayed green while the programs crashed. The gate measures `rsp % 16` at `rt_proc_call_open{,_det}` — a **caller-side** call that happens *above* the push block — and the pad removal moves parity **below** it, at the `jmp` into the callee. So the gate is correct, is not weakened, and **could never have caught this**; a seat who ran only the gate would have shipped the crash. The symptom and the invariant live on opposite sides of one instruction.

## The baseline, which nobody had stated in this shape

⛔ **The row's own DONE-WHEN was GREEN before I touched anything**, and that is a fact the ceo needs more than it needs the cure:

- `parse` m3 PASS m4 PASS · `patchu` m3 PASS m4 PASS · `chkhtml` m3 FAIL m4 FAIL — a **FAIL, not a CRASH or a HANG**, so the DONE-WHEN's crash-or-hang test does not see it.
- arizona `tracer.icn` m3 rc=1, no fault (the cto had already cured it and said so on the bus).
- parity gate 2/2.

⭐ **The crashes the row is named after were never on origin.** They existed only *inside the cto's bisection*, i.e. only under candidate edits. So this DONE-WHEN cannot be proven red before the work starts — it is a **no-regression** criterion wearing the shape of a cure criterion. Named here rather than smoothed, because "a real DONE-WHEN is proven red before you start" is a live rule and this row cannot satisfy it.

## Experiment 2 — the cure: the word moves across the call

The 8 bytes are **not deleted**. They move from the caller's push block into the callee's own carve, which is parity-neutral by construction:

| site | before | after |
|---|---|---|
| `bb_call_proc_staged.cpp` pad push | unconditional `sub rsp,8` | `IF(!icn_gen_regime(), …)` — pushed only where a pad is still needed |
| `bb_call_proc_staged.cpp` ω landing | `add rsp,16` | `icn_gen_regime() ? 8 : 16` |
| `emit.cpp` callee carve | `align16(ft) + 48` | `align16(ft) + 48 + 8` |
| `emit.cpp` ANCHOR | `lea rcx,[rsp+48]` | `lea rcx,[rsp+40]` |
| `rt.c` `rt_genp_spine_enter_n2` | 6 words | 5 words — one `pushq $0` dropped |

Generator entry frame is now **five words**: `[rsp+0]=γ [rsp+8]=ω [rsp+16]=REGION [rsp+24]=L7 [rsp+32]=ABI word`, `ANCHOR=[rsp+40]`.

⭐ **Why the ω landing had to move too, and why it is the easiest half to miss:** the landing pops what the call site pushed. Leave it at 16 where the site now pushes 8 and rsp walks **over the caller's own live spine** on the way out — a corruption with no crash at the site that caused it.

⛔ **The runtime twin was shrunk in the SAME landing, on purpose.** `rt_genp_spine_enter_n2` and `bcps_spine_gen_arm` are two hand-written copies of one ABI with **no gate comparing them**; `b49fd7a4` grew one without the other and the file's own comment records how long that took to find. The two doors have **opposite base parity** — the twin is entered by a `CALL`, the compiled site sits at a 0-mod-16 BB depth — and the shared callee constant is only right for both because the twin carries a private extra word. That still holds after the shrink: compiled entry `rsp0−40 ≡ 8`, twin entry `X−48 ≡ 8`, and the now-odd carve (`align16(ft)+56`) lands the body at `0 mod 16` on **both** doors.

The whole emitted change, for a generator witness, is **four instructions**: carve `-176 → -184`, ANCHOR `48 → 40`, the pad `sub` gone, the landing pop `16 → 8`.

## Experiment 3 — the cross-language control arm, and its own positive control

This is a shared-engine edit, so SHARED-NODE VERDICT SCOPE binds. `icn_gen_regime()` is `g_emit_cfg->icn_cells_graph`, a per-graph flag — but **that is an argument, not a measurement**, so I measured it. Emitted `.s`, old binary vs new, trailing comments stripped, over the SNOBOL4 / Prolog / Pascal / Snocone corpora:

```
CROSS_LANG_INSTRUCTION_IDENTITY graded=87 byte_identical=50 comment_text_only=37 instructions_moved=0
```

⭐ **And the same arm on three Icon programs reports instructions moved = 14, 7 and 7.** Without that row the zero above is worthless: it cannot distinguish *"no other frontend moved"* from *"my comparison never ran"*. This is the `[rsp+0]` γ-poison lesson from the 09-09 finding, applied to a diff instead of a store — **a null result is only evidence when the instrument has been watched saying yes.**

⚠️ The 37 comment-text-only rows are the annotation rename (`PL-CALL-ALIGN` → `PL-CALL-ALIGN (NON-GENERATOR SITES ONLY since CEO-483)`) reaching every non-generator call site in the tree. Worth naming because a byte-compare alone reported **38 of 104 differing** and looked exactly like a cross-language regression for as long as it took to strip one `sed`'s worth of comments.

## What this closes, and the one thing it does not

- **Closed:** the pad has no reader (09-09, poisoned with a control); the crash under pad removal is parity, not a lost datum (Experiment 1); a parity-neutral edit turns the whole bisection table green at once (Experiment 2); no other frontend's instructions move (Experiment 3).
- ⛔ **NOT closed, and not mine to close:** `chkhtml` m3/m4 FAIL is an **output mismatch that is red on origin too** — it is not a crash, it is not this row, and this landing does not move it either way.
- ⛔ **NOT claimed:** `board_icon_master.sh` reads **749/756** both modes against floors of 748/748 and reports the watermark moved up. **I did not attribute that +1 to this change and deliberately did not re-pin the floor** — the Icon master pair has exactly one writer (CEO-452), and a floor re-pinned on an unattributed, once-measured entry reds the gate fleet-wide if it turns out to be flaky. Named to the ceo instead.
- ⚠️ **A third disagreement about this frame survives, exactly as it did on 09-09:** `emit.cpp` calls `[rsp+16]` **`unused`** while both twins call it **REGION**, and the poison arm found no reader there either. That makes it the *next* removable word — and removing it is the same shape of edit as this one, not a new problem. I did not fold it in: one bug at a time, and a second word out of the same frame in the same landing would have made the four-instruction diff unreadable.
