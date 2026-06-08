# HANDOFF — 2026-06-08 26th attended run (Opus 4.8) — FIX-3 design reduction + 3-i pre-flight

**Result:** NO code landed. Read-only investigation run (builds + probes). SCRIP @ **187ae78** (local==origin, no commit from this run). `.github` this commit. Cursor UNMOVED (`bb_aggregate_nb.cpp`). No rung closed; LADDER 5-kind spike text STANDS.

## What this run was
Lon ran a Socratic dialogue over FIX-3 (the `bb_call` 522-line / 312-violation split) and steered the design. The substance:

1. **The asm-tail "duplication" I first flagged was a non-issue.** The four-port α/β/γ/ω tail every box emits is the contract, and `x86_asm.h` is already the sole asm producer. Sharing lives at IR→template (one kind, one template, language-blind), not at the asm tail. Lon dismissed the tangent; correct.

2. **"Did not reduce."** The 25th-run grid split IR_CALL into ~5 kinds — but the enum was already ~5 call-type opcodes, so the count is a wash. Lon's point: splitting always ADDS enum rows; counting opcodes measures the wrong thing. The real reduction is at the EMISSION layer — `bb_call_str`'s 9 arms + the neighbor-inspection soup (`dval∈{2,3,5}` + `rt_proc_is_registered`/`rt_builtin_is_known` + `fn=="write"`+`a0->t`) collapse to N single-logic templates with LOWER deciding.

3. **The 3-topology floor.** Keyed on the only axis that emits a different PORT BODY — who fills the args + whether ω/re-entry is wired:
   - **IR_CALL_DIRECT** — `rt(name,nargs)`, args already in slots, NO FAIL port. Subsumes builtin + userproc + write.
   - **IR_CALL_MARSHAL** — template fills `[r12+argbase+i*16]`, `rt(name,args*,n)`, FAIL `eax==99→ω`. Subsumes named_proc + byname + gvar_userproc.
   - **IR_CALL_STAGED** — Prolog clause β-scan / chain re-entry.
   - Two folds make 5→3: **DEFINE folds into DIRECT** (both non-failing single rt-call; differ only by stamped symbol/args — iff one parameterized DIRECT template is accepted over re-introducing an arg-style discriminator). **GEN_SCAN is not a call** — suspendable generator with β-re-pump resume; re-parent OUT of the call family to the generator set. The 9 `bb_scan_*` templates are already correct; Icon merely mis-parents them under IR_CALL via `dval==3`+`g_icn_scan_regs_live` (the `emit_core.c` 469-485 peel).

## ⛔ FOR LON — pending ratification
**3 vs 5 topologies.** Does DEFINE fold into DIRECT? Does GEN_SCAN re-parent out of the call family? Until ratified, the LADDER 3-i/3-ii/3-iii text is left verbatim (the OPERATION three-revert lesson: don't restructure pinned design text without the pin).

## FIX-3-i pre-flight (turnkey for a full-headroom run)
- **Proof path confirmed empirically:** `write("hi")` m2=hi=m3; `write(40+2)` m2=42=m3. The oracle backs the native path, so the asm-diff/behavior proof has a real m2==m3==m4 target.
- **⛔ Law-5 caveat pinned:** `write(1 < 2)` is **m2=2, m3=EMPTY** — relop-as-value sub-shape (boolean-INTVAL branch, `marshal_call_arg` 265-300). 3-i's proof MUST show m3 stays empty post-split (identical-to-baseline), not "fixed." Owner ICON-BB/Lon.
- **Edit site:** `lower_icon.c:458` (the `n==2 && write|writes` branch). The same pattern is duplicated in SIX lowerers (icon:458, pascal:190, raku:235, sno:1145, value:494, + prolog:466 path) — WRITE_SLOT/WRITE_EXPR is language-blind; land Icon first (m2-backed), the other five follow.
- **dval∈{2,3} set-sites** (3-iii cross-frontend scope, Lon-pin earned): lower_icon:75(3.0)/345/363/383(2.0), lower_value:375(3.0), lower_raku:18/144(2.0); lower_program:503 is RETURN not CALL.

## Baseline (green at floors, head 3ffd319)
prove_lower 68 PASS rc=0 (3 inherited law-5 FAILs: PL-GZ-7 ITE pair + PL-GZ-8 arith-is) · sno_pat_reg HARD 0 r10-refs · scrip builds clean. `bb_call.cpp` = **312** violations (returns_plus 52, local_vars 81, emit_fmt 47, bypass 50, medium_any 24, neighbor_walk 19, port_english 11) — ring top, matches the 23rd-run re-baseline.

## Concurrent absorbed
IRD-3 TO **187ae78** (lower_value.c −2, dead v_to aux SET drop) fast-forwarded onto my clean tree. No SCRIP code touched this run → no rebase/re-cert needed.

## Next-session order (unchanged)
ratify 3-vs-5 floor → open **FIX-3-i** (Icon write de-walk, turnkey per above) → 3-ii DEFINE → 3-iii PINNED (dval 2/3 + GEN_SCAN re-parent, IRD/ICN co-owned) → FIX-4 / 7c per standing order.

## Outstanding verdicts (6 + 1 new)
3-vs-5 topology-floor ratification (NEW, FOR LON) · x86_movimm uint32-trunc (bb_call_fn) · prove rc=0-on-FAIL hardening · PL-GZ-8 arith-is 2-vs-5 (PL-GZ) · m2 disj-backtrack silent-empty (PROLOG-BB) · IRD-2b IR_t.own DEVIATION ratification · ml comment-substring false-positive (FOR LON).
