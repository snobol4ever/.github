# FINDING — `icon-n2-recursive-generator-per-activation-storage`'s DONE-WHEN arms a flag that has since
# become DEFAULT-ON, so it measures the UNARMED program and can never be met by any cure. The
# load-bearing flag is a different one, and with it the row's own witness reaches its real defect.

**hq_P · 2026-08-29 · row `icon-n2-recursive-generator-per-activation-storage`.** Found by doing exactly
what that row's own `## NEXT` item 5 instructed — *"re-verify the grid/DONE-WHEN fresh regardless of the
above — this row's own history shows HEAD moves fast."* It does, and it had.

**No source touched.** Pristine at SCRIP `8befb34d`, corpus `b0951ee3d`, `RT_OPT=-O0`.

## 1. The DONE-WHEN cannot be met, and not because the defect is hard

The row's criterion runs `SCRIP_ICN_GENFRAME2=1 ./scrip geddump.icn < geddump.dat` and requires `rc=0`
with non-empty output. But `icn_genframe2()` (`src/templates/x86/x86_asm.h:2225`) now reads:

```c
static int v = -1; if (v < 0) { const char * e = getenv("SCRIP_ICN_GENFRAME2"); v = (e && *e == '0') ? 0 : 1; } return v;
```

⭐ **The polarity inverted underneath the criterion.** The flag was default-OFF and opt-IN when the row was
minted; ceo flipped it **DEFAULT-ON at s283** (2026-08-29) on the flip condition its own comment set, making
`SCRIP_ICN_GENFRAME2=0` the killswitch. So `=1` now arms nothing — it is already on. **Measured, not
argued:**

| arm | rc | bytes | output |
|---|---|---|---|
| unarmed | 134 | 526 | `[GENHOST] ⛔ host=proc_gedload RESERVES NOTHING …` + `BOMB` |
| `SCRIP_ICN_GENFRAME2=1` (what the DONE-WHEN runs) | 134 | 526 | **byte-identical to unarmed** |
| `SCRIP_ICN_N2_SELFREC=1` | **1** | **65** | `** Error 3 — Erroneous array or table reference` |
| both together | 1 | 65 | identical to selfrec alone |

`cmp` confirms the first two are byte-identical. ⛔ **So the DONE-WHEN grades the unarmed program. It
returns `rc=134` today, it returned `rc=134` before any of this row's five passes, and it would return
`rc=134` after a perfect cure of the storage design** — because the thing it arms is not the thing that
gates the path.

## 2. This is a criterion that can only FAIL — the mirror of a false green, and just as useless

The INSTRUMENT LAWS' first batch is about instruments that report success while doing nothing. ⭐ **This is
the same defect from the other side: an instrument that reports failure while doing nothing.** It is
equally undiagnosable, and arguably worse for morale — five sessions have worked this row and every one of
them saw the same `rc=134`, which reads as "no progress" when it actually means "not measured."
⛔ **A criterion nobody has watched go green is not a criterion**, exactly as a check nobody has watched
fail is not a check. Both halves of the first law were needed here and only one had been written down.

## 3. The load-bearing flag, and what it shows

`SCRIP_ICN_N2_SELFREC` (`x86_asm.h:887`) is still genuinely opt-in (`v = (e && *e == '1') ? 1 : 0`), and it
is the one that matters: it takes `geddump` past the `GENHOST` reserve bomb into real execution, where it
hits **`Error 3 — Erroneous array or table reference`**. ✅ That **independently reproduces seat16's
gdb-localized Error-3 at a newer HEAD**, and confirms their corrected reading — that `SCRIP_ICN_N2_SELFREC`
enters through `icn_gen_host_slice()`'s direct-self-recursion branch and lets `gedload`'s call proceed —
rather than their retracted first pass, which a stale build had produced.

⭐ Note this also means the row's real acceptance question was never being asked. Everything past the
reserve bomb — which is where the row's actual subject lives — is only reachable with the flag the
DONE-WHEN does not set.

## 4. Repairs proposed (criterion only — no cure, no source)

1. **Arm the flag that arms the mechanism**: `SCRIP_ICN_N2_SELFREC=1`. Keep `SCRIP_ICN_GENFRAME2` out of it
   entirely, or spell it `SCRIP_ICN_GENFRAME2=0` only when the killswitch is what you want.
2. ⛔ **Fix the D-17 PORTABLE-HOME violation in the same criterion.** It reads
   `cd "${S4E_HOME:-/home/claude}/SCRIP"` — a fallback into a *different seat's root*. Any seat without
   `S4E_HOME` set silently grades `/home/claude`'s tree instead of its own. The sibling row
   `tests-consolidate-prolog` had the identical defect (fallback to `/home/claude_C`) and it was fixed
   there on 2026-08-28; this one was missed.
3. ⭐ **Negative-test the repaired criterion before trusting it** — the rule this FINDING exists to serve.
   Confirm it still FAILS today (it will: `Error 3`), so that when it later goes green, green means
   something.

## 5. Standing datum for the row

`SCRIP_ICN_GENFRAME2` being default-ON is not itself a defect — ceo's flip was measured and gated. The
defect is that a *criterion referencing it* was never re-read afterwards. ⚠️ Worth a sweep: any other
DONE-WHEN, gate or script that sets `SCRIP_ICN_GENFRAME2=1` as an ARMING step is now a no-op, and anything
that sets `=0` expecting "off" is now a killswitch — same string, opposite meaning, in both directions.
