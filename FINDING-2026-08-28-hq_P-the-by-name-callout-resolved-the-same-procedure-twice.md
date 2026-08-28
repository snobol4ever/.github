# The by-name callout resolved the SAME procedure twice — half of `rt_proc_find` was pure duplicate work

**Seat:** hq_P · **Date:** 2026-08-28 (s278) · **Mode:** DUO (`MODE` file, computed — not assumed from prose)
**Row:** Lon's tier-1 demo campaign (`MODE` scope: *pattern matching + THE DEMOS ONLY* · method: *profile the few target
programs, cure ONLY the RT functions THEY use*) · **Cures a slice of:**
`FINDING-2026-08-28-hq_P-json-match-loses-on-callouts-not-on-matching.md`
**Instrument:** callgrind **Ir at fixed work**, m4, `RT_OPT=-O0`, `json-match` on `citm_catalog.json` (86% match share).
**Tree:** SCRIP `0125bc8d` (cure) over `104ca904` · corpus `49adbb852`.

## The claim

`rt_call_proc_descr` resolved the procedure name, then handed the **same name** to `rt_proc_call_open`, which
resolved it **again**. Every by-name callout paid the by-name lookup **twice**.

Measured, `json-match`, before the cure — and the call counts are the whole finding:

| caller | calls to `rt_proc_find` |
|---|---|
| `rt_call_proc_descr` | 92,945 |
| `rt_proc_call_open` | 92,945 |
| setup (`set_nparams`, `set_frame_bytes`, `set_nformals`) | 30 |
| **total** | **185,890 for 92,945 callouts** |

`rt_proc_find` was **7.50%** of the program (11,526,326 Ir) and `__strcmp_avx2` a further **4.84%** — the strcmp each
cache hit pays to revalidate, because the registration-site name pointer and the callsite literal are separate rodata
labels for the same string (ceo's second-cut comment at `rt.c` explains why pointer-only validation was measured worse).

## The cure

Split the **post-resolution** half of `rt_proc_call_open` into `rt_proc_call_open_p(rt_proc_t *p, int nargs)`.
`rt_proc_call_open` keeps its signature and delegates; `rt_call_proc_descr` passes the record it already holds.

**The two resolutions provably cannot disagree**, which is what makes this a redundancy and not a shortcut:
nothing between them mutates the procedure table — `rt_dyn_alpha_fn_p` only READS an alpha cell — and
`rt_call_proc_descr` **already dereferences its own `p` after that call** (`p->dyn_scope`, `p->jmp_entry`, `p->fn`),
so the code relies on exactly this invariant today. The cure removes a second lookup; it does not add an assumption.

## Measured

⭐ **Against a REBUILT pre-cure baseline, not against the disarmed arm.** The disarmed arm carries the killswitch's own
per-callout cost (156,027,480 Ir, **1.57% above** the true baseline), so arm-vs-arm reads **−6.20%** and **overstates
the gain**. The honest number is the tree-before/tree-after one. Shared axes: callgrind Ir · fixed work · m4 · `-O0`.

| program | pre-cure Ir | cured Ir | delta |
|---|---|---|---|
| `json-match` (citm) | 153,610,836 | 146,361,201 | **−4.72%** |
| `json-match-fence` (citm) | 164,206,925 | 154,540,646 | −5.89% *(arm-vs-arm)* |
| `calculator-1-match` | 736,705,541 | 736,705,541 | **+0.00%, byte-identical** |
| `calculator-2-match` | 13,366,422 | 13,366,422 | **+0.00%, byte-identical** |

Two independent pre-cure readings agree to **0.018%** (153,582,515 without the env var, 153,610,836 with it), which is
the instrument spread.

⭐ **THE ZERO ROWS ARE THE CONFIRMATION, NOT A GAP.** `calculator-1/2-match` profile as **emitted match boxes with zero
procedure callouts** (78% of calculator-1 is four BB blobs). A cure aimed at callout ceremony must be *exactly* inert
there — and it is, to the instruction. A bulk number that moved everything would have been evidence the attribution
was wrong. **`rt_proc_find` itself went 11,526,326 → 5,763,736 Ir — exactly halved**, which is the predicted mechanism
rather than a summary statistic.

## Killswitch + control arm

`SCRIP_PROC_OPEN_P=0` restores the re-resolution **in one binary with no rebuild**. Default **ON, opt-OUT** — same
polarity and spelling as `defer_xpat_on` / `defer_ic_on` / `patv_fast_on`.
⛔ Deliberately not opt-in: **a default-OFF killswitch on a cure is a deletion with a comment explaining what it used
to do** (s275 — the PT-3 collapse shipped dark for eight days that way).

## Gates

Pristine build first (HQ-27). **SNOBOL4 blocking set: m3 PASS=893 FAIL=0 · m4 PASS=893 FAIL=0 · SKIP=0 · MISSING=0**,
rc=0. `test_gate_emit_no_lang.sh` OK · `test_gate_template_medium_invisible.sh` OK.

⛔ **SHARED-NODE VERDICT SCOPE honoured** — `bb_call_proc_staged.cpp` is lowered to by SNOBOL4, Icon *and* Prolog, so a
board was owed on each: **Icon smoke 14/14 both modes · Snocone 5/5 · Rebus 4/4 · Prolog 4/5.** The Prolog `clause`
FAIL is **pre-existing**: the smoke returns *identical* counts with the cure disarmed, and 4/5 is better than the 3/5
CLAUDE.md documents as baseline. It belongs to hq_C's parked `prolog-multiclause-*` rank-0 family.

`.s` artifacts unchanged **and proven so**: the regen chain resolved all 21 sanctioned demos and reported `same` for
each (the full list, not just the summary line — that summary string is the exact false-green my s275 FINDING caught,
so it was read past deliberately).

## ⚠️ Two corrections to standing numbers, both found while running this row

1. ⛔ **The SNOBOL4 board denominator is now 893, not 365.** CLAUDE.md's *"expected totals are `m3 365/365, m4 365/365`"*
   is stale by ~2.4×. `FAIL=0 / SKIP=0 / MISSING=0` is the invariant and it holds; **the total is not the invariant**,
   exactly as that file warns two paragraphs later. A seat matching on 365 reads today's green as missing programs.
2. ⚠️ **Callgrind needs `--main-stacksize=2000000000` on the recursive pattern demos.** Without it `calculator-1-match`
   and `json-match` die `Stack overflow in thread #1: can't grow stack to 0x1ffe801000` — **rc=139 while still writing a
   plausible 185 KB profile**. A partial profile of a crashed run is not a fixed-work measurement, and it does not
   announce itself; `calculator-2-match` succeeded in the same sweep, so the failure is per-program, not per-session.

## What this does NOT claim

⛔ The callout ceremony is **~31.6%** of json-match's match phase (companion FINDING). This cure takes one slice of it —
the duplicate resolution. `rt_name_save_push` (7.87% self, still **two calls per callout**), `rt_proc_call_prologue`,
and the argument `memmove` are **untouched and remain the largest remaining lever on the worst tier-1 row**.
⛔ No aspect-2 multiple is published here. The Ir gain is measured; converting it to a `x` multiple against the clean
oracle requires the two-aspect board, which is a separate run — and s275's 1.76x wall-clock swing with no code between
readings is why that conversion is not done by arithmetic.
