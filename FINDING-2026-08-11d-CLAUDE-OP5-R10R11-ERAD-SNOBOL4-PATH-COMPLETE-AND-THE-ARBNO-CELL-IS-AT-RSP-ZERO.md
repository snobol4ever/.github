# FINDING 2026-08-11d (Opus 5, s24) — R10/R11 eradicated from the SNOBOL4 path; the ARBNO cursor cell is at literal `[rsp+0]`, so s22's K>0 escape hatch is closed

## 1. What was asked and what was done
Directive: *"eradicate all usage of R10 and R11 to free that up."* Done for the SNOBOL4
path, artifact-verified, with zero regression and zero repair. The remaining sites are
named in §6 and are off that path.

## 2. Why the class is real
`855a12a5` (D-1) made PASS-THRU the only blob linkage, so `r10`/`r11` are rΓ/rΩ
product-wide; `7c903000` (W-MAP 3) added the 32B `{res,r10,r11,pad}` record. Any template
writing r10/r11 as scratch destroys the linkage of every blob in flight. s23 convicted one
site (`match_end_α`). It missed a worse one: `bb_func_activate`'s `AB_TC_REG` resolved to
**`r10` on every function activation** whenever `RTCC_GLOBAL_R9_GVA` was live — a wire
collision in the function-call path, conditional on a flag that is default-ON.

## 3. The shape of the fix, and why not a bracket
The scan templates protect the wires with `push r10 … pop r10`. That shape is
**unavailable in `bb_match_end` by construction**: r10 was live across `mov rsp,[r10+8]`,
so a pushed save is discarded by the very instruction it must survive. s23 flagged the
bracket as UNCONFIRMED; it is not merely unconfirmed, it is wrong here. Register
substitution to `r8` is the correct shape — `r8` is veneer-preserved (RTCC slot 5,
offset 40), the same property that made r10 attractive to the original author.
`bb_callee_frame` took `rax`, not `r8`, because `bcf_areg(3)` **is** `"r8"` and an r8
spelling self-clobbers the source pointer at i=3 before the `[r8+8]` read.

## 4. ⛔ Correction on myself — the first zero-residue claim was vacuous by construction
Slice 1 (`89ff6994`) claimed zero scratch residue. The classifier counted **every**
`lea r10,[rip+…]` as wire setup, so `lea r10,[rip+g_call_args]` was absolved: it could not
have reported a violation of that shape. Real residue was claws5 1, calculator-1 20.
Corrected rule, now the gate: **legitimate IFF `lea` to a `.L` SITE label, or `mov` from
`[rsp` (the record reload); a lea to a GLOBAL SYMBOL is scratch, always.** Post-fix:
claws5 8=6+2+0 · json 112=86+26+0 · calculator-1 48=32+16+0 · treebank-list 26=16+10+0.
The raw write counts FELL (calculator-1 68→48, treebank-list 66→26) — that fall, not the
reclassification, is the evidence. Same family as s37's vacuous killswitch A/B.

## 5. ⭐⭐⭐ s22's SCRUTINY 1 is answered: K=0
s22 closed with *"the real question is whether the first ARBNO iteration leaves K=0 at the
γ edge — compile and measure."* Measured, in shipped instructions:

    n16_match_arbno_α:  sub rsp,16
                        mov dword ptr [rsp + 0], r14d
                        mov dword ptr [rsp + 4], r14d
    proc_PAT$0_γ:       sub rsp,8 · push r11 · push r10 · push rax(res)   = 32B

ARBNO carves its own 16B cell and addresses it at **literal `[rsp+0]`/`[rsp+4]`**, not at
`[rsp+K]` for positive K. **Carving first is precisely what puts the cell at offset 0.**
γ's 32B record therefore displaces the cursor by exactly 32, and the `af` (exhaustion) arm
reads `[rsp+0]` — the pushed `res` address. s22's candidate (a) as written is FALSIFIED.
Witness (12 lines, sub-second, no input file) reproduces `181`'s signature exactly: T1, a
single successful `ARBNO(*P)`, prints; T2, the exhaustion path, SEGVs.

    P = LEN(1) ; T1 = 'ab'  ; T1 POS(0) ARBNO(*P) RPOS(0)
                 T2 = 'abc' ; T2 POS(0) ARBNO(*P) 'zz' RPOS(0)

⇒ The rung is LAYOUT: make ARBNO's cell address survive a spine push (anchor/ζ-relative,
or a held cell address), or push γ below the interior frontier. Not landed — 88% context,
and this file's law is that an edit at end-of-context is a broken tree by construction.

## 6. Gate, attribution, and a stale watermark
Probe suite m3 (`SCRIP_RTCC=0`): **157/163**, non-pass `{D12 D13 H31 X01 X10 fence_probe}`.
Attributed by stashing the edits, rebuilding pristine HEAD, re-running: **identical set**.
Zero regression, zero repair. Separately this shows GOAL-SN4-ZETA-MECH's s38b watermark
(**160/1/0/2**, non-pass `{D12,D13,fence_probe}`) is **stale at HEAD by three probes** —
H31, X01, X10 went red between that measurement and origin HEAD, none of them by this
session. H31 is the probe s37 celebrated as repaired. Suspects: the D-1 / W-MAP(3)
landings themselves.

Still outstanding, off the SNOBOL4 path (hence 0 residue in these artifacts):
`bb_call_fn` Prolog trail/heap fast paths (`g_pl_trail`, `g_plw_*`, `g_hp_fr` — r10 base +
r11 value, needs TWO scratch registers and `r8` is already live in those arms),
`xa_flat.cpp:247/474`, `bb_idx_get`/`bb_idx_set` (r11 array-data pointer; `r8` AND `r9`
both already live), `bb_var.cpp:19`. Each needs liveness analysis, not substitution.

## 7. Measured non-result, stated plainly
The eradication does **not** move the demo board. CLAWS5 / JSON / CALCULATOR / TREEBANK
m3 = **0/16 before and after, by set** (HANG 4 · DIFF 2 · SIG11 10). Harness validated:
the SPITBOL oracle reproduces all four `.ref` files exactly, and `hello.sno` passes, so
the instrument is not dark. The r10/r11 clobber was a genuine latent landmine; it is not
the demo blocker. ⛔ `scripts/board_demos_zeta.sh`'s m4 arm is WRONG as written —
`--compile` emits asm to stdout and `-o` writes asm text, not an executable. The m4 column
was never measured; do not read one from it until it is fixed.
