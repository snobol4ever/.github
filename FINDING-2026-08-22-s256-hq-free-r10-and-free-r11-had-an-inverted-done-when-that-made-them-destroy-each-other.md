# ⛔⛔⛔ RETRACTED IN FULL — s256 HQ WAS WRONG. DO NOT ACT ON ANY PART OF THIS FILE.

**Retracted 2026-08-22 by HQ (s256), same session, corrected by Lon in-chat.** The original text of this FINDING ruled that `free-r10`/`free-r11` had an "inverted" DONE-WHEN, that ordinary scratch use of r10/r11 was legal, that both rows were DONE, and that no seat should re-open them on a grep count. **Every one of those conclusions is wrong.** The original text is deleted rather than preserved, because a seat skimming it would act on it.

## What HQ got wrong

HQ read Lon's *"R10 and R11 are free"* as **released into the general scratch pool**. It means the opposite: **freed from their old job so they can be given a NEW one.** Lon, correcting HQ in-chat 2026-08-22, verbatim in substance: *"R10 and R11 usage was to be totally eradicated first. Then used for two new things. That was the plan."*

The plan is the three-row telemetry ladder, and it was already written down correctly in the queue: `free-r10` → `free-r11` → **`diag-regs-stmt-and-bb`**, whose brief states the two new uses in Lon's own words — *"setting R10 at STATEMENT_BEGIN and setting R11 at ALPHA and BETA at every BB."*

- **r10 = the SNOBOL4 statement number**, one `mov r10, imm32` at every `IR_STATEMENT_BEGIN`.
- **r11 = the BB node id**, loaded at every α and every β of every box.

These are **permanent dedicated claims across all emitted code**. A single surviving scratch use of either register clobbers the telemetry at the exact moment it is wanted — a crash. That is why the DONE-WHEN says **ZERO uses in `src/templates` and `src/emitter`**, and why it is not invertible, not negotiable, and not a grep-count pedantry. It is the whole point of the rung.

## What follows from the retraction

1. **`free-r10` and `free-r11` are NOT done.** Their original DONE-WHEN stands, unamended. Current state, measured at HEAD `261cafcb`: **r10 = 65** sites, **r11 = 152** sites in `src/templates` + `src/emitter`. Both must reach zero.
2. **`diag-regs-stmt-and-bb` is CORRECTLY BLOCKED.** seat8 read its brief right and was right to refuse to start; *"a half-freed register is the s194 collision"* is the brief's own words and they are sound. HQ's "unblocked" ruling is withdrawn.
3. **seat3's 71-site move (`ef553d3a`) was counterproductive and must be redone.** It moved scratch off r10 **onto r11** — measured `0ff71be8` r10=136/r11=91 → `ef553d3a` r10=65/r11=152. Under the real plan both registers are claimed, so the sibling is not a destination. Those sites need relocating to a register that is genuinely free. ⛔ **Not r8 or r9** — `RTCC_GLOBAL_R9_GVA` is hardcoded `1` and `g_rtcc_on` defaults `1`, so r9 carries GVA and r8 ANCHOR in every default build (seat3's own caveat, and it is correct). The available set is **rax / rcx / rdx / rsi / rdi**, per-site liveness reviewed — seat3 already landed `rcx` and `rax` at several sites successfully, so the approach is proven, only the destination was wrong.
4. **seat3's eradication half (`0ff71be8`, 34 sites) stands and was right** — the dead WREG register-wire fallback genuinely had to go.
5. **seat6's census stands and was better than HQ's.** Its bigger numbers (248 in templates+emitter across 25 files, plus 225 in the RTX hand-asm `.S` files never in scope) are the real burn-down, and the `.S` files matter now: `diag-regs` claims the registers **product-wide**, so hand-asm sites can clobber the telemetry exactly as templates can. ⛔ HQ's earlier dismissal of `test_gate_wreg_claim.sh` as "policing a superseded design" is **withdrawn** — it is a SCOPE gate that answers precisely the question this ladder asks ("who mentions r10/r11 outside the licensed sites"), which is the same question whether the claim is γ/ω or statement/BB-id. It should be **re-pointed at the new claim and flipped LIVE at `diag-regs`**, not retired.
6. **seat3's open question is real and now has an answer.** `bb_define.cpp:138-145` pushes all eight non-rax caller-saved GPRs around the `g_monitor_bin` diagnostic call. Under a *dedicated* claim a save/restore pair is **not a clobber — it preserves the value across the call**, which is what the telemetry needs. That site may therefore keep naming r10/r11, but it must be **re-stated in `ARCH-SNOBOL4-RTX.md` §2 as preserving the diagnostic registers**, not as generic scratch protection, and the gate registry must license it explicitly. Everything else goes to zero.

## The lesson, which is HQ's alone

HQ had the answer in front of it: the row is titled **TASK 1 OF 3** and names its own successor `diag-regs-stmt-and-bb` in the first line of its brief. HQ read the word "free" out of Lon's sentence, built a theory on it, measured hard in support of that theory, and never opened the third row that says what the registers are *for*. ⭐ **A ladder's rung cannot be judged without reading the rung it feeds.** Three seats — seat3, seat6, seat8 — each behaved correctly and each asked HQ the right question; the only broken component was HQ's ruling, which then contradicted all three at once. That is the tell HQ should have caught: **when a ruling makes three independent seats wrong simultaneously, suspect the ruling.**

**Supersedes:** nothing. **Superseded by:** the original briefs, which were correct as written and remain in force verbatim.
