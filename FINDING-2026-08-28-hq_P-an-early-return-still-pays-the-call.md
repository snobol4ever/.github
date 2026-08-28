# An early return still pays the call — shortening the body bought 0.175%, skipping the call bought 1.89%

**Seat:** hq_P · **Date:** 2026-08-28 (s279) · **Mode:** FLEET-6 · **Lane:** json remainder (mine per ceo's split)
**Instrument:** callgrind **Ir at fixed work**, m4, `RT_OPT=-O0`, `json-match` on `citm_catalog.json`.
**Tree:** SCRIP `18c6b597` over `79873cc3` · baseline pinned on the same tree at **146,345,152 Ir**.

## The mechanism

`rt_proc_call_prologue` is entered **92,945** times on json-match and calls `rt_name_save_push` **185,890** times —
twice per callout, once for the parameter list and once for the result name — while only **92,945 elements are ever
pushed**. The parameter push arrives with `np == 0`: the `EXPR$n` procedures json drives carry **no formals**.
**Half the calls did nothing at all.** (Call counts, not shares — `rt_name_save_grow` fires exactly 92,945 times, once
per element actually pushed, which is what pins the split.)

## ⭐ THE RESULT WORTH KEEPING: WHERE THE COST LIVED WAS NOT WHERE THE PROFILE POINTED

`rt_name_save_push` was the **#1 RT symbol at 8.26%** (12,082,850 Ir over 185,890 calls ≈ 65 Ir/call). The obvious cure —
return early when `n <= 0` — is provably correct and **measured −0.175%**. Nearly nothing.

**Line-level annotation said why:** the function's opening brace alone costs **1,858,900 Ir = 10 Ir of prologue per
entry**, and 185,890 entries make that **1.27% of the whole program in function ENTRY**. ⭐ **An early return still pays
the prologue, the argument setup, and the epilogue — it shortens the body, and the body was not the cost.** Moving the
same test to the *call site*, so the call is never made, took the same cure from **−0.175% to −1.89%**.

| shape | vs pinned baseline |
|---|---|
| early return inside the callee (`n <= 0`) | −0.175% |
| **+ guard at the call site (`np <= 0` → use `g_name_save_top`)** | **−1.89%** |

`146,345,152 → 143,579,020`. With `0125bc8d` (s278), json-match is **153,610,836 → 143,579,020 = −6.53%**.

⛔ **This is NOT the shape s278 cured, and I checked rather than assumed.** There, the second `rt_proc_find` was
*redundant work* — the same answer computed twice. Here **both calls are necessary and different** (parameters vs result
name); one of them merely happens to be *empty for json's shape*. A resemblance in the call-count ratio (2× per callout)
is not a shared mechanism, and treating it as one would have aimed the cure at the wrong half.

## What it does not claim

⛔ `rt_name_save_push`'s remaining ~110 Ir per *populated* element is **intrinsic** — `DESCR_t` copies at `-O0`, with the
fast path always taken (its only callee on this workload is `rt_name_save_grow`; `NV_GET_fn`/`NV_SET_fn` are **never**
reached, so the expensive branch is not live here). **Shrinking that is an RTX/ASM question, not a C one**, and no
further C micro-optimisation is on the table.
⛔ No `x` multiple is published. Ir does not convert to a multiple by arithmetic, and per the campaign's standing
constraint **wall clocks stay refused until seat05's noise row lands**.

## Killswitch + gates

`SCRIP_NSAVE_FAST=0` restores all three shapes in one binary, no rebuild. Default **ON, opt-OUT**, `always_inline` so the
arm is a load+test rather than a call.
⭐ **Boarded in BOTH arms** — hq_C's law, adopted: pristine, **SNOBOL4 m3 893/893 · m4 893/893 · SKIP=0 · MISSING=0,
armed AND disarmed**, rc=0 each. `emit_no_lang` OK · `template_medium_invisible` OK.
⛔ **SHARED-NODE VERDICT SCOPE** (`rt_proc_call_prologue` is the shared proc-call path for every frontend): **Icon 14/14
both modes · Snocone 5/5 · Rebus 4/4 · Prolog 4/5**, the `clause` FAIL pre-existing with *identical counts disarmed*.
`.s` artifacts unchanged and proven: the regen resolved all **21** sanctioned demos and reported `same` for each.
