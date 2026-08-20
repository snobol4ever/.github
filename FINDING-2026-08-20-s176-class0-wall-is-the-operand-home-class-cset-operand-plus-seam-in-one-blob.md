# FINDING s176 (HQ, Fable 5) — **THE CLASS-0 WALL IN TWO LINES: A CSET-OPERAND BOX SHARING A BLOB WITH A SEAM WRONG-ANSWERS, REGARDLESS OF ORDER. IT IS s174's OPERAND-HOME CLASS — NO ALT ARM, NO RETREAT, NO ALLOCATION REQUIRED.**

**Front:** ARCH-PASSTHRU class 0 · witnesses `corpus/probe/passthru/pt0_*` (all oracle-refed, both modes agree on every row). Pristine HEAD. HQ hands-on.

## Census (class 0, both roads)
`pt0_len_var` PASS · `pt0_lit_any_func` (two func-seams, LIT+ANY across them) PASS · `pt0_len_var_retreat` (β across one seam) PASS · **`pt0_3layer_mixed` FAIL (silent `nomatch`, both modes)**.

## The ablation chain (one variable at a time, oracle green on every shape)
| swap | verdict | eliminates |
|---|---|---|
| INNER LEN→TAB | still FAIL | the inner box |
| OUTER tail NOTANY→LEN | still FAIL | the outer layer |
| drop OUTER entirely (2 layers) | still FAIL | depth |
| MID's ANY→TAB | **PASS** | ⇒ the ingredient is the cset box |
| ANY in a blob with NO seam (`MID = LEN(2) ANY('c')`) | PASS | blob-membership alone |
| NOTANY after the seam | FAIL | ANY-specific |
| **ANY BEFORE the seam** (`MID = ANY('a') *INNER`) | **FAIL** | ordering — the seam poisons the WHOLE graph |

**Minimal witnesses:** `pt0_any_before_seam.sno` / `pt0_notany_after_seam.sno` (2 pattern lines each); passing control `pt0_any_noseam_ctl.sno`.

## The mechanism, unified with s174
ANY/NOTANY read their **cset operand through a flat rsp slot** (the ZD notes: "dynamic arm reads ZOPQ(0,8)"). A DEFER anywhere in the same blob graph interposes runtime state the compile-time flat coordinate never priced — so the operand read misses, in BOTH media, in EITHER order. The boxes that survive class 0 are exactly the ones with **no operand memory read**: TAB/LEN carry integer operands ON THE NODE (CONST-AT-LOWER), LIT is rip-relative. s174's SPAN(*expr) needle-pair read inside an ALT arm is the SAME class wearing pattern clothes. And `pt1_retreat_3layer_bare` (`MID = *INNER . V`) plausibly reduces to it too — the CAPTURE's home inside a blob-with-seam — to be separated from the β-refusal hypothesis by asm-diff in the fix rung.

## What this means for the ladder
Class 0 is not blocked by control flow at all — γ, β, and 3-layer crossings all work for boxes whose operands/results have real homes (registers, node-resident consts, rip). **The one repair is Lon's RESULT law mechanized: every operand and result gets a DECLARED, seam-valid home (node-resident, rip, register, or rbp-side cell) — flat rsp guesses die.** Fix rung: re-home the cset/needle operand reads (likely: operand descriptor banked into the blob/frame head beside the wires at graph entry), gate = the whole pt0+pt1 family oracle-identical both modes, then classes 1–8 walk.

## ADDENDUM (same slice, Lon's two questions answered from the tree)
**Patch vs glue:** WITHIN a graph = true patching (Lrec/Jrec resolved at `bb_seal`; wiring is the execution; `bb_pat_build.cpp` re-runs the emitter at store time so even runtime-built blob INTERIORS are patched). ACROSS graphs = glue (DTP record, `bb_glue_pass_wires_blob`, pushed pads — all four protocols; measured link-not-fuse proof: `b1c_cross_medium_concat_seam`). The `*P`/`*F()`/EVAL/CODE boundary is irreducible by language semantics — but the two-continuation law makes it a TWO-SLOT RUNTIME STITCH (banking {γ,ω} IS patching, at exactly two offsets, as the graphs move). Target: patch complete where the value is owned at build; stitch two slots where it is not; glue dies.
**Why CSET:** nothing semantic — it is the FIRST OPERAND WITH NO LEGAL HOME under current conventions. Survivor operands ride the node (TAB/LEN immediates, CONST-AT-LOWER) or rip (LIT; `xa_csettab_rodata` for compile-time graphs). A cset is too big for an immediate and, in a runtime-built blob, too late for rip (`ANY('c')`'s "literal" arrives at `bb_pat_build` as a runtime descriptor → dynamic arm → flat rsp slot read). The RESULT-law home: operand descriptors banked beside the wires in the graph head at entry — the stitch discipline extended from continuations to operands.
