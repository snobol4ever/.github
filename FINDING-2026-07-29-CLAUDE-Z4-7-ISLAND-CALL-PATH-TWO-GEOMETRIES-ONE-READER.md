# FINDING — Z4-7 slice 2: the island call failure was TWO FRAME GEOMETRIES, ONE READER (and a wire quad one register too narrow)

**Session:** 2026-07-29, Claude (GOAL-ZETA-FOUR s7). **Tree:** SCRIP `ec307c3c` → `28af3501`.

## THE DEFECT, bracketed to the instruction
`z4_fib` under `--zeta-storage=frame-r12` died rc=1 at `rt.c:1056` ("open call carries no return wires"). gdb (breakpoint on `rt_flat_wire_adopt`): **the adopt fired on every call — with `gw=0, ww=0`.** Not a missing call; a null marshal.

Cause: the island `JMP_NONRSP` prologue (xa_flat.cpp, BINARY and TEXT twins byte-agreeing) parks the **LOW header** — outside-γ at `[rsp+8]`, outside-ω at `[rsp+16]`, caller zr at `[rsp+24]`, pad at `[rsp+0]`, region base `zr = rsp+32` — the epoch's own layout. The s176 WIRE-ADOPT box (SN4-FLAT-PROC, one of EXTRACT-Z4-R12.md's ~5 net-new suspect arms) reads the **RSP HIGH header** `[rsp+kt-24]/[rsp+kt-16]` — which under the island carve is freshly rep-stosb'd region. Two geometries, one reader: every island activation adopted `(0,0)` and the first RETURN bombed. The extraction doc's suspect-by-default classification called this arm exactly right.

## THE SECOND DEFECT, latent behind the first
The wire quad `{γ, ω, rsp, rbp}` restores caller machine state at RETURN — but under the island config the callee prologue **seeds zr(r12)** after saving the caller's at `[rsp+24]`, and the floaters never restored it: the caller would have resumed with its island base pointing at the dead callee frame. The RSP configs never noticed because r12 is free there (R12-FREE-1).

## THE FIX (SCRIP `28af3501`, 3 files — the call protocol made config-invariant)
1. `bb_save_restore.cpp` role 3: leading island arm mirroring the low-header geometry; caller rbp marshals LIVE (the island arm never clobbers rbp); the saved caller r12 rides as a **5th marshal (r8)**. Roles 1/2 floaters restore r12 from the widened quad — island-emit-gated, so RSP bytes are untouched.
2. `rt.c`: `rt_flat_wires_t` gains `r12` (sizeof 40, static assert extended; the three push-site compound literals zero the new field by C initializer semantics). `rt_flat_wire_adopt_isle(gw,ww,rsp,rbp,r12v)` is the island leaf; the 4-arg leaf zeroes the field.
3. `bb_call_proc_staged.cpp`: ISLE rides the **modern wire arm** (`open_fn` forced under !RSP; the det elide's new RSP conjunct is dead-identical under RSP because det+RSP is captured by the earlier arm). The legacy `push r12 / mov r12,rsp` anchor-bracket arm — epoch residue mixing two protocols — is now unreachable under every live basis and awaits Z4-9's delete.

## VERIFIED
frame-r12 **5/5 m3 AND 5/5 m4** (gcc -no-pie link; all match refs) — Z4-7 probe completion criterion met; z4_capture CORRECT (the frame-config oracle property, now reproducible at HEAD with one flag) · default `.s` **byte-identical ×5** probes pre→post + deterministic ×3 · frame-rsp 5/5 unchanged · default 4/5 unchanged (capture DIFF pre-existing `d79a427a..cca948c5`) · heap arbno rc=139 preserved (Z4-8 pre/post proof intact) · **regen ×3 zero drift corpus-wide** (crosscheck watermark held by byte-identity) · medium-invisible gate: xa_flat(106) fails at BASELINE identically — pre-existing WIP backlog, not regressed; this slice added zero raw bytes.

## WHAT THIS TEACHES THE CUT (Z4-9)
The header geometry is per-config but the READER was config-blind — the same one-authority disease Z4-6 cured for fc grants, on the frame axis. Whatever survives the cut, the header layout must have ONE authority both prologue and adopt read, or the gate (Z4-10) must run frame-r12 so a re-split dies loudly.
