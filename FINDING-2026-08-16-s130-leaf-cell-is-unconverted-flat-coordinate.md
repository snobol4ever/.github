# FINDING s130 — THE LEAF SUSPENSION CELL IS AN UNCONVERTED FLAT COORDINATE; THE BLOB ONLY MAKES IT LETHAL

**Measured** 2026-08-16 s130 (Claude Opus 5, Lon in-chat *"using the IPC sync-step MONITOR, take us home"*).
SCRIP `1ecb68ec` (was `2e18a2f3`), corpus `adfdb4a1` unchanged.
Witnesses: `corpus/probe/clobarm/` (minted s129). Gates: `scripts/test_gate_clobarm.sh`, `test_gate_s130_blast.sh`, `test_gate_s130_behav.sh`.

---

## 1. THE HEADLINE

`clob_altarm_arm2direct_red.sno` — **rc=139 on the DEFAULT build, m3 AND m4 — is CURED.** It now prints
`id=iffoo` in both modes, and the 2-way IPC sync-step monitor goes from **DIVERGE at step 6** to
**exit 0, all 9 steps agreeing**.

The cure is behind `SCRIP_SPAN_FRAME` (default OFF, byte-identical 961/961). The default flip is
Lon's to grant; the sibling widening is a named rung below.

## 2. THE ROOT CAUSE — s129's FRAMING IS ACCURATE BUT UNDERSTATES THE CLASS

s129 named this *"a framed blob's leaf suspension cell overshoots into the caller's standing frame."*
That is true of the witness. Measured from the emitted asm, the **blob does not create the defect**:

`IR_MATCH_SPAN` spells its suspension cell `FR(_.x86_scratch_off + N)` — a **RAW FLAT ZLS COORDINATE** —
while carving **nothing** at its own α. `x86_frame_off`'s single `op_zdepth` term is *the box's own carve*,
so a box that carves nothing gets **zero compensation** and the flat coordinate is emitted verbatim
against whatever `rsp` happens to be.

Every other box in the same emission is pure FORTH and converts correctly:

```
main_α_body:            sub rsp, 0                  <- NOBODY reserves a flat region
n22_lit_string_α:       sub rsp, 16 ; [rsp+0] ...   <- carves K, cells at [rsp+0..K)
n0_match_alternate_α:   sub rsp, 32
                        [rsp+0] [rsp+8] [rsp+16]    <- flat 16/24/32 CONVERTED correctly
n2_match_span_α:        (no carve)
.Lx12_240:              mov dword ptr [rsp + 164], r14d   <- flat 160+4, NEVER CONVERTED
```

`--dump-zeta` confirms the coordinate: `graph 1 'PAT$0' … +160 16 RAW span.cnt/cur IR_MATCH_SPAN`.

**Inside an ALT arm that coordinate has NO OWNER IN EITHER MEDIUM.** `zd_plan` grants per RUN and the arm
interior is the s66/s71 ungranted-arm denial class — *precisely the denial `cap_in_alt_arm` already
re-homes the CAPTURE half of into the frame registry* (s93 R-0). The leaf half was simply never done.

| where the same unconverted spelling lands | outcome |
|---|---|
| PAT$ blob (`rsp` = `blob_rbp-104`, cell `rsp+164`) | `blob_rbp+60` = `standing_rbp-4` = upper half of the CAS MARK qword → truncated mark → `rt_dcap_pump` walks a wild arena → **rc=139** |
| inline in `main` (cell `rsp+260`) | `standing_rbp+156`, up in caller stack slack → **passes BY COINCIDENCE** |

⭐ **INDEPENDENT CORROBORATION, ALREADY IN THE TREE:** `x86_asm.h:1098` convicted this exact shape from the
ARB direction in an earlier session — *"SPAN's identical FR(x86_scratch_off) shape happened to PASS only
because … **a coincidence, not evidence the address was right**."* Two seats, two directions, one defect.

## 3. THE FIX — A RE-HOME, NEVER A DELTA

The s129 cursor's warning was explicit and is upheld: naive `+56` sends the cell further into the caller,
naive `−56` above the frame; ~1065 readers convert through `x86_frame_off` and the pinned/island arms are
depth-IMMUNE and must not be touched (FRQ/FRQB double-add class).

So the cell becomes **the FOURTH customer of THE ONE activation-frame slot registry** (`frame_slot_scan`),
beside ARBNO / CAPTURE-SAVE / FENCE1, in the **same shared numbering** — four classes, one index space,
no collision however they nest. rbp-relative ⇒ **depth-immune**, so the encoder keeps its single term and
there is no pricing delta to double-add. Decided in the **PLANNER**, so the coordinate arrives correct;
the carve widens through the **same scan** (`blob_frame_bytes` / `emit_match_begin_frame_extra`), so
planner and template cannot disagree — the s66 coherent-worlds law, now four parties.

ONE AUTHORITY held: `alt_arm_member()` is **extracted from `cap_in_alt_arm`'s own loop**, so the ALT-arm
containment *fact* is spelled once and its two customers cannot drift (the s68/s70 spelled-twice disease).
All 26 span cell references route through **one** accessor pair (`SPC`/`SPCQ`) so no arm can be half-homed.

Witness, ON: frame 56 → 72 bytes; the cell moves `[rsp+164]` → `[rbp-60]`, inside the blob's own frame.

## 4. ⛔ THE 8-BYTE USABLE-WINDOW LAW — MEASURED, AND THE DECLINE IT FORCES

The registry tiles **one 16B granule per slot with the base 8 bytes ABOVE the granule floor**. For a blob:
`blob_frame_bytes()` = `24 + 16*count` carved below the r10/r11/rdx entry wires at `[-24,0)`, slots at
`-(32 + 16*idx)`. The three-candidate case tiles `[-72,-24)` **exactly**, floor to ceiling, no slack:

| idx | base | granule |
|---|---|---|
| 0 | −32 | [−40,−24) |
| 1 | −48 | [−56,−40) |
| 2 | −64 | [−72,−56) |

So a slot offers `d ∈ {0,4}` **and nothing more** — `d=8` is the neighbour's cell.

`bb_match_span.cpp`'s `SPAN(*var)` deferred-by-name arm (`sval[0]=='*'`) is the ONE arm that spends the
full 16B — `lea rsi,SPC(0)` / `lea rdx,SPC(8)` / `mov r8,SPCQ(0)` / `mov eax,SPC(8)`, the `{ptr,len}` pair
`rt_pat_prim_str` fills. It is therefore **DECLINED in the planner** and keeps its legacy spelling
byte-identically. Framing it would hand a neighbouring capture SAVE's cell to a runtime writer — the same
cross-owner overwrite this rung exists to kill, moved indoors — and it would have been **invisible in the
witness**, which uses a literal charset and never reaches that arm.
**Follow-up named, not forgotten:** grant the 16B class two consecutive slots (or widen the granule) — a
registry change that moves ARBNO/CAPTURE/FENCE1 offsets too, hence its own rung with its own blast radius,
never a quiet widening of this one.

## 5. ⭐⭐⭐ s128 IS UNBLOCKED — AND s129's REFUSAL TO BLAME IT IS VINDICATED

| arm | arm2direct | blobvar | samevar | trueinline | varcross |
|---|---|---|---|---|---|
| default (both OFF) | rc139 | wrong | wrong | PASS | wrong |
| `SCRIP_CHOICE_RBP=1` alone | **rc139** | **rc139** | **rc139** | PASS | wrong |
| `SCRIP_SPAN_FRAME=1` alone | **PASS** | wrong | wrong | PASS | wrong |
| **both =1** | **PASS** | **PASS** | **PASS** | **PASS** | wrong |

`SCRIP_CHOICE_RBP=1` measured **alone** SEGVs `blobvar`/`samevar`: it only controls whether the corrupt
cell is REACHED — exactly what s129 argued when it exonerated the s128 slice. The choice-record mechanism
was **correct all along and was MASKED by this corruption**; this rung is its missing prerequisite.
Composed, clobarm goes **4/5**, m3+m4.

## 6. GATES (all measured; the `.so` is swapped IN PLACE — never `LD_PRELOAD`, never the driver alone)

- **Killswitch OFF: 961/961 BYTE-IDENTICAL** over 962 programs (crosscheck + programs/snobol4 + probe).
- ⭐ **THE NULL IS NON-VACUOUS.** The noise floor was measured by recording the **baseline against itself**;
  it returns the **same single mover**, `programs/snobol4/parser/unary_not.sno`, which is **RUN-TO-RUN
  nondeterministic on the baseline binary too** (3 runs → 3 distinct md5s, on *both* compilers). A
  pre-existing defect, banked below, **not this rung's**.
- ON blast radius **36 programs**. crosscheck m3 **OFF 298/19 == ON 298/19, ZERO row-level movers**
  (298/19 is the s128 watermark exactly, so the baseline is true HEAD, not a stale tree).
- **s127's five retraction movers 120/131/165/181/182 PASS BOTH ARMS**, plus 130 / 150 / 151.
- arbnostore 10/10 · seam 4/4 · arbnofence 4/4 · m1 24/25 (known `m1_nret_cap` FATAL) · altdepth 0/2 —
  every suite arm-identical.
- **MONITOR** (RULES MONITOR-FIRST step 4): `spitbol_vs_run` on the witness **DIVERGE step 6 → exit 0**.
  The pre-fix bracket was minted **before any code was touched**.
- **beauty self-host 10/622, ON == OFF byte-identical — NEUTRAL, no regression.**

## 7. ⛔ AN UNRELATED DEFECT FOUND AND BANKED, NOT CHASED (END-OF-CONTEXT LAW)

**`corpus/programs/snobol4/parser/unary_not.sno` compiles NONDETERMINISTICALLY.** Three consecutive
`--compile` runs of the *same* binary produce three different md5s, on the baseline compiler as well as
the new one. This is stronger than s119's *"build-to-build nondeterminism"* — it is **run-to-run, same
binary**. It is the entire noise floor of the 962-program md5 instrument, so **any future killswitch
byte-identity claim over this corpus must either exclude it or measure the null against itself**, exactly
as this rung did. Cheapest next step: diff two runs of its emitted `.s` and look for a baked pointer,
address, or hash-order artefact. Not opened here.

## 8. WHAT IS NOT DONE

- **SPAN only.** BREAK / BREAKX / TAB / RTAB / REM / ARB / BAL share the identical unsound
  `FR(x86_scratch_off)` spelling and are UNTOUCHED. The widening is mechanical (same accessor pair, same
  predicate, add the ops to `leaf_frame_candidate`'s whitelist) but needs its own blast radius.
- **`SPAN(*var)` declined** — §4.
- **`varcross_red` still red** — the cross-blob `MATCH_VALUE` class, untouched by this rung.
- **Default stays OFF** pending the corpus-wide ON sweep and Lon's flip grant (R-7/s124 protocol).
