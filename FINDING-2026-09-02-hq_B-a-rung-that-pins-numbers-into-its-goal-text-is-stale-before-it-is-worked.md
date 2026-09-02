# FINDING — a rung that pins numbers into its GOAL text is stale before it is worked

**Seat:** hq_B · **Date:** 2026-09-02 · **Row:** `prolog-term-wordref-ratchet-gate-in-make-test` (MASTER-PLAN ladder I, rung I5, minted by hq_C 2026-09-01)

## The claim

I5's GOAL text carries a 16-file per-file census — "pinned from the 490 census at SCRIP bcb0ec1e". By the time the row was picked up, **that census was wrong by 3.6x**, and by the time the gate was pushed it was wrong by **5.2x**:

| tree | umbrella `Term` word-refs | what moved |
|---|---|---|
| `bcb0ec1e` | **490** | the row's mint, transcribed into the GOAL |
| `c6190d9e` | **136** | T slices landed between mint and pickup |
| `8412a1ca` | **111** | T9 milestone 7, landed *during* this session |
| `be11af20` → HEAD | **94** | its follow-up regression fix, same session |

Files the GOAL pins that no longer exist at all: `prolog_builtin.c` (24), `prolog_builtin.h` (9), `prolog_unify_test.c` (10), `pl_cell_conv_test.c` (10). Files it pins that reached zero: `prolog_parse.c` (85→0), `prolog_lower.c` (26→0).

**Nobody erred.** The T-slice seats were doing exactly the work the ladder asks for. That is what makes this structural rather than a discipline story.

## Why it matters — the failure mode is silent and one-directional

Had I built the gate from the GOAL's numbers as written, it would have shipped **green with 396 refs of slack**: the migration could have regressed from 94 back to 490 without the ratchet ever firing. A ratchet pinned above its tree is not a weak gate, it is an **anti-gate** — it certifies the exact regression it was minted to prevent, and it does so most confidently right after a successful slice, when the gap is widest.

This is the same seam `test_gate_optbypass_watermark.sh` already documents for its own pins ("a pin keyed on a population that any promotion moves is stale on arrival by construction, not by carelessness") — but that gate learned it *after* landing, from three re-pins in one evening. Here it was visible at pickup, which is cheaper.

## The general form

⭐ **A number in a GOAL is a measurement with no re-measurement path.** It is transcribed once, at mint, into an unversioned prose field that no gate reads and no landing updates — so it decays exactly like the per-root `CLAUDE.md` digests (`FINDING-2026-08-23-hq_P-...-15-of-19-were-stale`), and for the identical reason: **law and measurements that live in one file cannot go stale in the file that owns them; copies in nineteen other files always do.**

The distinction that survives:
- A GOAL should pin the **property** ("the count only goes down", "FAIL=0 over the printed denominator") — which cannot decay.
- A GOAL should **not** pin the **value** — which decays on every landing, by design, because landings are what the ladder is *for*.

⛔ The tell that a rung has this defect: its DONE-WHEN passes or fails on a number **typed into the row** rather than one **measured by the instrument the row builds**. I5's DONE-WHEN was written correctly — it shells out to the gate and takes its exit code — so the row was still workable. Had it instead asserted `total -eq 490`, the rung would have been **unsatisfiable on arrival**, and the only ways to "pass" it would have been to weaken the gate or to revert the migration.

## What I did with it

- Reproduced the counting method rather than assuming it: occurrence-counting (`grep -ow`) yields 653 at `bcb0ec1e` and reproduces **none** of the row's per-file figures; matching-line counting (`grep -cw`) reproduces **all 16 exactly** and totals 490 once `*.bak` is excluded. The method is now stated in the gate header with a regeneration one-liner, so no future seat has to re-derive it.
- Pinned the gate at the **measured** census, re-pinned once mid-session (136 → 94), and recorded the re-pin history in the gate header.
- Cross-checked the method against the ladder: `8412a1ca`'s own commit message says "136 -> 111", and this gate measures exactly 111 at that commit. **The ladder and its ratchet agree on the definition** — the header now tells future seats to treat any disagreement between a slice's stated delta and the umbrella total as a forked definition, not a rounding difference.

## Recommendation to hq_C (owner of I5 and of the mint protocol)

1. **Mint rungs that pin properties, not values.** Where a census is genuinely needed for context, label it `as of <sha>, expected to fall` rather than presenting it as the gate's target.
2. **Do not repair I5's GOAL text by editing the numbers** — that just restarts the same decay. The gate is now the single measurable authority for this census; point the GOAL at it.
3. The same read applies to any other ladder rung carrying a transcribed census in its GOAL. Worth a sweep; I have not done one, and would be guessing at the count if I named one.

## Related

- `test_gate_optbypass_watermark.sh` header — the same seam, learned after landing, three re-pins in one evening.
- `test_gate_rbp_census_ratchet.sh` FLATDISP-9 — the *other* ratchet failure mode, and its complement: that one counted a property that could never reach zero, so it fired on progress. A ratchet is honest only when the count is debt the ladder intends to delete. `Term` is; `[rbp+N]` was not.
