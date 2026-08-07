# FINDING-2026-08-07h — MECH2 BLOB ASSIGN_SAVE RSP OFFSET STALE: M4 SIGSEGV CLASS IS FOUR PROBES (A05 A06 F02 G15)

**Session:** Sonnet 4.6, 2026-08-07 s6 · SCRIP `466c5334` · corpus `fa3973fc`

## CLAIM

A05, A06, F02, G15 all crash m4 (rc=139) with the same root cause: the `IR_MATCH_CAPTURE_SAVE push` arm (`rt_cap_push` path, `op_fc_bytes=0`) emits `lea rdi,[rsp+op_off]` where `op_off` is the flat blob slot offset, but at runtime RSP ≠ blob_base — the mech2 `push rbp` boundary shifts RSP by 8 before `sub rsp,Kc_zwr`, so the slot lives at `[rsp + op_off + 8]`, not `[rsp + op_off]`. m3 survives by main-stack slack (same wrong address, but blob/stack padding absorbs the overshoot); m4 CRT stack geometry puts the over-shot pointer into unmapped memory → SIGSEGV.

## MECHANISM

The mech2 match boundary (`bb_match_begin.cpp`) emits:
```
push rbp          ; rsp = α−8
mov  rbp, rsp     ; rbp = α−8
sub  rsp, Kc_zwr  ; rsp = α−8−Kc_zwr (= blob_base)
```
The designed blob slot addressing is `[rsp + 8 + off] = [α − Kc_zwr + off]` (the `+8` accounts for push rbp). But `IR_MATCH_CAPTURE_SAVE` on the `rt_cap_push` path (phase=0, `fc_geom` returns false, `sfc()=false`) uses `FR(_.op_off)` → `x86_zop(op_off, 0, 0)` → regime 4 (`x86_fb_data()=false`, since `flat_fb_refine=1` and `op_fb_rbp=0` for blob-interior nodes) → `[rsp + op_flat_disp + op_zdepth]`. With `op_flat_disp=0` (CARVE-DATA-ERAD `s23a` permanently zeroed) and `op_zdepth=0` (ASSIGN_SAVE has no own fc cell), result is `[rsp + op_off]` — missing the +8.

Additionally: any fc_geom-granted suspended ZD cells stacked above the ASSIGN_SAVE node (e.g., a `lit_integer` node's 16B cell from `n13_lit_integer_α: sub rsp,16`) further displace RSP downward, adding more error. In A05, the lit_integer cell adds −16 → `[rsp + 232]` reaches `blob_base + 216` instead of `blob_base + 232` (slot displaced by 16 from the lit_integer + 8 from push_rbp = 24B total error).

**Why `zvo_resolve` doesn't fix it:** mech2 explicitly suppresses UCLAIM (`!zwr` at emit.cpp:2101), so `op_uhead = -1` for blob members; the `zvo_resolve` branch in `x86_frame_off` is skipped; the raw fallback fires.

**Why `x86_fb_data()` doesn't fix it:** the `flat_fb_refine` census classifies these nodes as NOT in a "deep match statement" (they ARE deep — inside a mech2 blob — but the census excludes blob-interior nodes from the rbp-based regime). So `op_fb_rbp=0`, `x86_fb_data()=false`, regime 4 fires.

## EVIDENCE

```
; A05 generated .s — n23_match_assign_save_α:
lea rdi, [rsp + 232]    ; WRONG: should be [rsp + 240] or [rbp + 232]
```
At runtime (m4): rsp = α−8−312−16 (= α−336); `[rsp+232]` = α−104; correct slot at blob_base+232 = α−8−312+232 = α−88. Delta = 16B from lit_integer suspension (the push_rbp delta was already baked into op_off by the LOWER-side prefix walk and is thus "correct" in the flat coordinate — but lit_integer's own ZD cell suspension is the live delta unaccounted).

`SCRIP_CAP_DIAG=1` m3 output: `[CAP] SAVE nd=... save_active=1 fc_bytes=0 port=6` — confirming the software-array path is taken in both modes identically.

## SCOPE

Four probes: **A05 A06** (C-4 ALT captures) · **F02** (FENCE backward abort + ARBNO capture) · **G15** (FENCE0 + capture before FENCE). All m4 XFAIL.compile. m3 passes all four (luck — main-stack slack absorbs the overshoot).

The pattern is: any mech2 blob containing an `IR_MATCH_CAPTURE_SAVE` that does NOT get a `fc_geom` FORTH-cell grant will produce a stale `[rsp+off]` address in m4.

## FIX DIRECTION (MECH-M-2 territory)

Three equivalent remedies — MECH picks one:

1. **`op_fb_rbp=1` for blob-interior ASSIGN_SAVE:** extend the `flat_fb_refine` census to classify blob-interior SAVE nodes as rbp-relative (`op_fb_rbp=1`). Then `x86_fb_data()=true`, `x86_zop` takes regime 3, `x86_frame_off` returns `off + 8` (the W-1b mech2 fix). Depth-immune; no ZD-suspension delta.

2. **Teach `fc_geom` to grant ASSIGN_SAVE a FORTH cell:** if SAVE always gets `fc_bytes=16` via `fc_geom`, `sfc()=true`, and the `rspd(0)` path fires — always depth-correct (own TOS). Eliminates the `FR(op_off)` address entirely for the SAVE case.

3. **`op_flat_disp` bakes the +8:** for mech2 blob members whose `LOWER` prefix walk already accounts for the blob structure, add 8 to the prefix sum. Risk: touches the permanently-zeroed CARVE-DATA-ERAD field — may interact with other sites.

**Option 1 is the lightest touch.** Option 2 is cleanest and retirement-aligned.

## CROSS-REQUEST

MECH cursor: add to M-2 or a named sub-rung. CLIMB cursor: C-4 gate blocked on this fix landing; C-5 witnesses all green except `*P`-deferred (G24/H20 m3, C-6 class). When M-2 delivers, remove A05/A06/F02/G15 from XFAIL.compile in the same commit.
