# FINDING — demo/calculator-1 is an RT_OPT split, NOT a codegen regression; 53819b4a is CLEARED

**Seat:** hq_C (HQ-CORRECTNESS) · **Date:** 2026-08-23 · **Reported by:** hq_P, who named a suspect and asked for confirmation before anyone acted.

## Verdict

`corpus/benchmarks/snobol4/demo/calculator-1.sno` splits on the **C runtime optimisation level**, at the same HEAD:

| arm | RT_OPT | result |
|---|---|---|
| dev default | `-O0 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer` | ✅ `check: 103002` (matches `.ref`) |
| benchmark | `-O2 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer` | ⛔ stream of `rt_dcap_pump: CORRUPT CAPTURE ENTRY refused`, rc=141 |

Both arms measured at HEAD `dd91bcd0`, `-O2` runtime **rebuilt at HEAD** (tag `96f0326c19`) — the pre-existing `-O2` .so on disk was from 21:47, i.e. older than both commits under suspicion, and testing against it would have proved nothing.

## ⭐ Why 53819b4a is cleared

`53819b4a` ("RTCC veneer: r10/r11 join the protected set") is a **codegen** change. The `scrip` compiler is **hardcoded `-O0` and does not honour `RT_OPT`** (Makefile:86). So the emitted code is *identical across both arms* — the only variable is the optimisation level of the C runtime. **A codegen commit cannot cause a failure that flips on runtime opt-level with codegen held constant.** Do not revert it on this evidence.

⭐ hq_P's report was sound work: three bisect arms (`SCRIP_DEFER_INLINE=0`, plus `SCRIP_DEFER_MERGE=0`, plus a full stash-and-rebuild at `3970f54a`) all reproduced byte-identical, correctly proving NOT-MINE. The suspect was named as a suspect, not a culprit, and asked to be confirmed — which is exactly why this was cheap to clear.

## ⛔ The other commit in that same pull — and the trap in the timeline

hq_P dated the appearance to "the first run after I rebased and pulled". That pull carried **two** relevant commits, not one:

- `53819b4a` 00:02 — RTCC veneer (the named suspect) — **cleared above**
- `53c1323a` 00:09 — *"jstring capture: refuse a capture entry that cannot lie inside the subject"* — **the guard that prints the refusal hq_P saw**

So the *message* is new in that pull even if the *corruption* is not. Before `53c1323a` this path did a silent out-of-bounds `memcpy`; the guard converted it into a named refusal. **"It appeared after the pull" is therefore consistent with a pre-existing latent defect newly made visible, and must not be read as "the pull broke it."**

## ⛔ The guard is measuring the wrong quantity (named, not fixed)

The refused entries are not corrupt. `len=2 saved_delta=6 end=8` is an ordinary capture. They are refused only because the comparison is against `Σlen == 0`.

`rt_dcf_t` carries a **per-frame** subject pointer (`subj`), but `rt_dcap_pump` (`src/runtime/pattern_match.c:660-666`) validates the entry against the **global** `Σlen` — the length of whatever subject is current *now*, not the subject this frame captured against. When the pump runs after the global has moved on, every entry in the frame is compared against the wrong length and refused wholesale.

Also note the message says **`frame depth 1`** — `g_dcf_top == 1`, a single frame. So the "a reentrant push invalidated the outer frame" explanation written in the guard's own comment **does not apply to this witness**, and that comment is now known to be too narrow.

⭐ The shape of the real fix: the frame must carry its own subject length and the guard must validate against *that*. ⛔ Blocked by a hard constraint that must not be papered over — `_Static_assert(sizeof(rt_dcf_t) == 40)` plus per-field offset asserts, because `rtx_match.S` (RTX-8 slice 8) hardcodes stride 40 and the field offsets. Adding a field is an ASM-contract change, not a C-only edit.

## Status: PARKED BY LON, not by analysis

⛔ **Lon, in-chat 2026-08-23, verbatim: _"Do NOT fix -O2 bug for BEAUTY. Do not care. Next."_** Work stopped at the diagnosis above. Nothing was changed in the runtime; the `-O0` symlink was restored and re-verified green (`check: 103002`).

This sits in the same class as the parked RUNG C-0 (an optimisation-level split in C runtime capture machinery, culprits slated for ASM replacement) — recorded so the next seat does not re-derive it, and above all so nobody reverts `53819b4a` on a suspicion this measurement already cleared.
