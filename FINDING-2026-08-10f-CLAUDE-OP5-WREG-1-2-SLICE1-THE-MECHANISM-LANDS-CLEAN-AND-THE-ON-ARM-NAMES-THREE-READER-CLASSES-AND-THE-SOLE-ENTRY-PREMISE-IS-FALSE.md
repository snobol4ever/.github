# FINDING 2026-08-10f — WREG-1/2 SLICE 1: THE MECHANISM LANDS CLEAN, THE ON ARM NAMES ITS OWN THREE READER CLASSES, AND "THE DEFER FAST ARM IS THE SOLE flat_pat ENTRY" IS FALSE

**Seat:** Claude Opus 5, session 15. **Goal:** `GOAL-PASSTHRU-RBP-ERAD.md` LADDER WREG.
**Watermark:** SCRIP `1e26e27d` (parent `565ecfa8`) · corpus `bea31de0` UNTOUCHED · `.github` this commit.
**Lon directive, verbatim:** *"Remove PROC overhead to pattern BLOBS and begin using R10 and R11 for GAMMA and OMEGA."*

## WHAT LANDED (killswitch `SCRIP_WREG`, DEFAULT OFF)

`wreg_on()` + `bb_glue_pass_wires_blob()` = `lea r10,γ · lea r11,ω · jmp rax`; `bb_match_defer`
fast arm converted; blob α shim suppressed; CLASS D exits collapsed to `jmp r10` / `jmp r11`.

⭐ **NO NEW ENCODER WAS NEEDED, IN EITHER MEDIUM.** `x86_lea_id` already sets REX.R for `m>=8`
and `x86_jmp_reg` already emits the `0x41` REX.B prefix. The ladder budgeted encoder work that
does not exist. This is the one place the design was *pessimistic*.

⭐ **THE CONVERGENCE.** The `g_zctx` push deleted by WREG-2 **is** the sharpest r10/r11 scratch
user in the product (`mov r10,[rax]` depth · `mov r11,[rax+8]` cur · `lea r11,[rsp+kt-40]`) — the
"WREG landmine, live-on-arrival" MECH s37 flagged. **The rung that claims the registers deletes
the code that was clobbering them.** These are not two racing edits needing a scheduling window;
they are one mechanism. This retires the landmine as a *scheduling* concern for the blob α path
specifically (it does NOT retire the other 285-occurrence sweep surface).

## KILLSWITCH LAW — SATISFIED BY MEASUREMENT, NOT BY ARGUMENT

`SCRIP_WREG=0` is **byte-identical to pre-edit HEAD**, md5-verified on three witnesses:
`dc_sib_bt` `9fe25ab5d01334ae53044402c8d2501e` · `dc_nest_bt` `d1e47d5debc577cd61fc58721c489f6d` ·
`pt_inline_1` `8a54a2619b5ab8845dbd3d7ce5e9b247`.

## MEASURED m3, SAME CONTAINER, BY SET

| arm | probe (39) | fail set |
|---|---|---|
| **OFF** | **33 / 5** | `{ab_freturn ab_nret_lvalue ab_redefine dc_recur z4_arbno}` — **== s12b/s13 floor name-for-name, ZERO regression** |
| **ON** | **21 / 17** | above **+12**: `ab_defer_call dc_nest_bt dc_sib_bt mv_arbno_callcap mv_valheld_cap os1_runtime_k pb_stitch_defer w_cap_ay w_cap_group w_cap_novowel w_cap_stored w_cap_xxay` |

## ⛔⭐⭐⭐ WHY ON IS RED — THE CARVE-ERAD CONVICTION, REPRODUCED AND NOW ITEMIZED

This file already carried the rule: *"never cut the region under unconverted readers."* Slice 1
cut it. The result is a **measured reproduction of the DEL-T1 revert** (`c4ef2176`), and its value
is that the readers are now **named from emitted asm** rather than inferred from source:

1. **`scanhit`** — `mov rdx,[g_zctx]` → `mov rdx,[rdx+8]` → reads scan flag `[rdx+8]`, δ0 `[rdx+0]`.
2. **`scanfail`** — same reads, plus **`mov rsp,[rdx+32]`** (retry re-base) + `jmp α_attempt`.
3. **`proc_PAT$N_res`** — re-**PUSHES** `g_zctx` *and uses r10/r11 as its scratch to do it*; its
   `β` is `jmp qword ptr [rbp+32]` — the `g_resumable_callable_active` resume-slot leak the ladder
   already names at emit.cpp:2443/3060.

⭐ **These are exactly WREG-4 and WREG-3, and the ladder already assigns them.** (1)+(2) die when
the retry is recast as a **statement-side ω stub** (WREG-4); (3) is **suspension capture** (WREG-3,
MECH's single-authority zone). **The 12 failures are therefore NOT a falsification of LADDER WREG —
they are the ladder's own unexecuted rungs, billed at the right addresses.** The fail set is
diagnostic of that: `w_cap_*` ×5 and `mv_*_cap` are capture/suspension (WREG-3), `dc_nest_bt` +
`dc_sib_bt` are the deep-arrival pair the ladder pre-named as the deciding witnesses.

⛔ **DEEP-ARRIVAL QUESTION IS NOT YET ANSWERED.** The ladder says: if `dc_nest_bt`/`dc_sib_bt` do
not ride the wires, deep-arrival is FRAMED-licensed rather than WREG. They currently fail — but
they fail **with the res/β resume path unconverted**, so this is NOT the measurement that decides
it. Recording the question as still open, with the reason, so the next seat does not read this
red as the answer.

## ⛔⭐⭐ SECOND FINDING — A LADDER PREMISE IS FALSIFIED

**PT-2 records: *"the defer fast arm is the SOLE flat_pat entry."*** Emitted asm falsifies it.
`dc_sib_bt`'s asm carries **three further** `lea rcx / lea rdx / jmp rax` blob entries
(`.Lx75_4/5`, `.Lx75_7/8`, `.Lx77_2/3`) from other `bb_glue_pass_wires` callers. Full caller list:
`bb_match_capture` ×3 · `bb_match_end`:47 · `bb_match_value`:38 · `bb_call_value`:62 ·
`bb_call_proc_staged` ×7 · `bb_match_defer`:112 (second site).

**Consequence for the ladder:** WREG-1 is **not one site**, and the converted-site count is not
the entry count. Slice 1 converted one entry path, so the ON arm ran blobs whose α no longer
stores wires but whose *callers* still deliver them in rcx/rdx — a second, independent reason ON
is red. ⛔ **OWED BEFORE THE SWITCH FLIPS: a per-caller blob-vs-proc target census** — each
`jmp rax` needs its rax provenance classified, because a site targeting a DEFINE'd proc must keep
rcx/rdx while a site targeting a PAT$ blob must carry r10/r11.

## NEXT SEAT, IN ORDER

1. **Per-caller entry census** (above) — cheap, mechanical, and it sizes WREG-1 honestly for the
   first time. Do this before any further deletion.
2. **WREG-4 first, not last** — the scanhit/scanfail retry recast is the *prerequisite* for the α
   cut, not a follow-up to it. Slice 1's red proves the ordering: the ladder lists WREG-4 fourth,
   but readers (1)+(2) block the ON arm today.
3. **WREG-3 coordination with MECH** for `proc_PAT$N_res` / β and the `[rbp+32]` resume-slot leak.
4. Only then flip default-ON, and re-run BY SET in both modes.
5. **m4 is confounded independently of WREG**: MECH s37 measured RTCC-default-ON at 3/16/0/**132**,
   restored to 133/16/0/2 by `SCRIP_RTCC=0`. Any m4 number taken now is measuring that, not this.

## HONEST LIMITS OF THIS SEAT

- **m3 only.** No m4, no crosscheck-122, no broad-336. The probe suite alone.
- **The 285-occurrence sweep is UNTOUCHED.** Only the blob-α ZCTX subset dies here.
- **The veneer question s14 routed to Lon is NOT addressed** and is not addressable from here: it
  straddles GOAL-RTCC. Nothing in slice 1 depends on it, because the switch is off.
- No corpus bytes changed; no regen ×3 (lower/emitter touched, but the OFF arm is byte-identical
  so artifacts are unmoved — regen becomes owed at the moment the default flips, not before).

---

# ⛔⭐⭐⭐ SAME-SEAT CORRECTION (s15b) — I RETRACT THE "SOLE flat_pat ENTRY IS FALSIFIED" CLAIM. IT WAS AN INSTRUMENT ERROR, AND THE INSTRUMENT WAS MINE.

**The title of this file is wrong and is retained only so the retraction is findable at the same path.**

## THE ERROR

I measured wire emission with `grep -c 'lea r10'`. The emitter pads mnemonics with **multiple
spaces** (`lea              r10`), so that pattern **cannot match** and returned 0 on an arm that
was emitting the wires correctly. I read the 0 as "the site glue never fired," and built two
downstream conclusions on it.

⭐ **This is the SAME CLASS of defect s14 convicted in the WREG claim gate** (`grep -c` counting
LINES and being reported as `mentions`). Two consecutive seats, same instrument family, same
failure mode: **a grep whose units were never verified against the text it greps.** Recording it
as a class, not an incident.

## RE-MEASURED, WHITESPACE-TOLERANT (`grep -cE 'lea +r10\b'`)

`dc_sib_bt` ON: `lea r10` **1** · `lea r11` **1** · `jmp r10` **1** · `jmp r11` **1** · `lea rcx`
8→6. **The mechanism fired end-to-end all along** — site glue AND both CLASS D exits.

## CORRECTED ENTRY CENSUS (ON arm, m3)

| program | PAT$ blobs | blob entries (`lea r10`) | exit pairs (`jmp r10`) | proc entries (`lea rcx,[rip`) |
|---|---|---|---|---|
| dc_sib_bt | 1 | 1 | 1 | 6 |
| dc_nest_bt | 1 | 1 | 1 | 6 |
| w_cap_ay | 2 | 2 | 2 | 5 |
| pb_stitch_defer | 1 | 3 | 1 | 7 |
| mv_valheld_cap | 1 | 2 | 1 | 5 |

**`PAT$ blobs == exit pairs` in every row**, and entries ≥ blobs (several call sites into one
blob — expected). **Every blob's entries and exits converted through the single `bb_match_defer`
site.** ⛔ **THEREFORE: PT-2's "the defer fast arm is the SOLE flat_pat entry" is NOT falsified —
it is CONSISTENT with every row above, and my claim against it is WITHDRAWN.**

**What the three trios at `.Lx75_4/5`, `.Lx75_7/8`, `.Lx77_2/3` actually are:** `.Lx75_4/5` is
the defer blob entry (it converts to r10/r11 under the switch). The other two are preceded by
`call rt_proc_open_fn@PLT` — they are **DEFINE'd-proc / one-shot entries**, which MUST keep
rcx/rdx and correctly do. I mistook the shared pass-thru *contract* for a shared *target class*.
`bb_glue_pass_wires` having many callers does not make many of them blob entries.

## WHAT SURVIVES THE CORRECTION, UNCHANGED

The **three reader classes** — `scanhit`, `scanfail`, `proc_PAT$N_res`/β + the `[rbp+32]` leak —
were read from emitted asm, not from the broken grep, and are unaffected. They remain the sole
explanation of ON 21/17, which **strengthens** the conclusion: with entries and exits now known to
be fully converted, the surviving readers are the *only* remaining cause. **WREG-4-before-WREG-2
re-ordering stands, and stands on cleaner evidence than when I first wrote it.**

## ⭐⭐ NEW EVIDENCE THE CORRECTION TURNED UP — s14's VENEER HAZARD, NOW AT INSTRUCTION LEVEL

Tracing rax provenance surfaced the RTCC veneer bracketing a real entry site verbatim:

```
mov [rax+56], r10        <- veneer writeback: r10 -> g_rtcc_block[7]
mov [rax+64], r11        <- r11 -> g_rtcc_block[8]
call rt_proc_open_fn@PLT
mov r11, [g_rtcc_block]
mov r10, [r11+56]        <- reload
mov r11, [r11+64]
```

s14 derived the flat-cell hazard *"by construction from a measured mechanism, NOT demonstrated by
a failing program."* **This is that mechanism as shipped instructions at a live call site** — one
evidentiary step further, still short of a failing witness. The save area is `g_rtcc_block[32]`,
flat, no depth index: correct at leaf depth, **destroys the outer wires under nesting**. Note the
sequence sits at a **proc** entry, so it is not yet on the blob wire path — but the manual (p.123)
guarantees deferred `*F()` mid-match re-entry, which is exactly how a blob's live wires reach a
veneered crossing. **The routing question s14 put to Lon is unchanged and still owed; this seat
adds evidence, not a decision.**

## COST OF THE ERROR, STATED PLAINLY

Two false claims were committed (`31cd2fd6`, `1629f576`) and stood for one seat: a retracted
falsification of PT-2, and a false second cause for the ON red. No code was written on their
basis, no rung was re-ordered on their basis (the re-ordering rests on the readers, which were
measured correctly), and the killswitch/floor numbers are unaffected. **Caught by this seat, in
this seat, before handoff — but it should have been caught by verifying the instrument against
one line of its own input before trusting a zero.** A zero from a grep is a claim about text, and
it must be proven the same way any other claim is.
