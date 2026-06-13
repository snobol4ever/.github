# HANDOFF — 2026-06-13 — BB-FIXUP 72nd run (Opus 4.8) — gvar_arith family LANDED (71st-run park certified)

## TL;DR
Two ring stops landed, both **live-proven byte-identical** on the real corpus:
- `bb_binop_gvar_arith.cpp` 22→0 — **SCRIP `648740e`** (this is the 71st-run PARKED change, finally certified; the missing piece was the corpus, now cloned).
- `bb_binop_gvar_arith_slot.cpp` 24→0 — **SCRIP `a6e0a18`**.

GRAND 1238→1216→**1192** (−46 exact). 76 dirty / 52 clean. All floors green pre+post every commit. No LADDER rungs closed. Cursor advanced to **`bb_call.cpp`** (the FIX-3 monster, TOTAL=324).

## State
- SCRIP HEAD **`a6e0a18`** (verified on origin). Clean tree.
- `.github` — 72nd-run watermark in `GOAL-BB-FIXUP-A-to-Z.md` + this doc.
- `# CURSOR: bb_call.cpp`.
- Workspace: SCRIP + corpus both cloned at `/home/claude/`. Corpus is the separate repo `snobol4ever/corpus` (293 icon programs etc.) — **the 71st run lacked it; clone it every session that runs C2 probes.** `.github` remote needed re-tokenizing before push this run (clone stored a tokenless URL); `git remote set-url origin https://TOKEN@github.com/snobol4ever/.github` if push 128s.

## Session open
Cloned SCRIP at `cba8a04`; 4 concurrents had landed past the 71st-run park `758d7b1` (all clean ancestors, none touching the gvar_arith path): `9f0d809` SNOBOL4 M3/M4 parity · `2d6487a` bb_resolve relocate 57→18 · `694e7d9` bb_retract_throw CV9/CV10 · `cba8a04` Pascal frame-hops. Full baseline battery GREEN before any edit.

## Stop 1 — bb_binop_gvar_arith.cpp 22→0 (SCRIP 648740e)
Reproduced the 71st-run parked edits from its handoff (template + `bb_fill_alpha` CV10 prep), then certified on the live corpus.
- **CV1** terse `IR_BINOP_GVAR_ARITH` · **CV7** `x86_load_ro`→`x86("lea",reg,"[rip + __]",ptr,lbl)` + `x86_call_ro`→`x86("call",sym,fp)` (routing-identity: x86_asm.h:577/587 RIPSEAL→x86_load_ro, :549 SYM-tag2→x86_call_ro) · **CV8** explicit `if(PLATFORM_X86)return…;return std::string();` · **CV9** parameterless · **CV10** `op_parts_lbl[0..2]` interned in `bb_fill_alpha` op-keyed block (op_sval gated `op_kind=="POW"` — ungated interning caused the spurious-strtab `.S`-renumber the 71st run caught) · **LANGUAGE-BLIND** strip (removed `g_gvar_flat_chain` reads + extern; redundant-with-dispatch → byte-identical).
- **C2 LIVE**: normalized A/B asm-diff EXACTLY 0 across all 5 arms (litlit/varvar/varlit/litvar/pow, all firing, comment-counts 2/2/2/2/1); only raw delta = sanctioned verbose→terse comment. Behavior m2=m3=m4 IDENTICAL ×5 (pow = `1024.` real, parity holds).

## Stop 2 — bb_binop_gvar_arith_slot.cpp 24→0 (SCRIP a6e0a18)
Same recipe; the gvar_arith sibling.
- 11 `gvs_*` helpers (lhs/rhs/op/arith/llit/lvar/rlit/rvar/disp/ok/name) inlined into one platform-return IF-combinator. `gvs_name` is character-identical to `bga_name`, so its CV7 forms were **already live-proven in Stop 1**.
- **CV10**: `op_name1`/`op_name2` interned in `bb_fill_alpha` under an op-keyed `IR_BINOP_GVAR_ARITH_SLOT` block (gated `bb_lk/bb_rk==IR_VAR`). **LANGUAGE-BLIND** strip. Two over-200 slot-displacement lines wrapped (guard on one physical line, single `x86()` on the next — multi_x86 stays 0).
- **C2 LIVE**: normalized A/B asm-diff EXACTLY 0 across 4 probes (9 box-firings total); only delta = terse comment. Behavior m2=m3=m4 IDENTICAL ×4 (60/14/10/16).

### ⛔ Firing correction (recorded so it is NOT re-litigated)
The slot box **IS corpus-reachable.** An early "non-reachable" reading was a **grep artifact**: I grepped the terse `IR_BINOP_GVAR_ARITH_SLOT` string the *converted* template emits, but the baseline emits a *verbose* `BOX IR_BINOP gvar-arith-slot…` comment, so the count read 0. Firing is set by dispatch (`emit_bb.c:2803`), template-independent. Nested-arith probes fire it: `D=A+B+C`(2) · `E=A+B*C`(2) · `F=A+B+C+E`(3) · `G=(A-B)*(A+B)`(2). Caught via the Stop-1 sibling regression check before committing, then did the proper live A/B proof (which is stronger than the by-construction route I had started).

## Probes (reusable; in `/home/claude/gva/`, run with `LD_LIBRARY_PATH=/home/claude/SCRIP/out`)
gvar_arith: litlit `X=3+4` · varvar `C=A+B` · varlit `C=A+5` · litvar `C=5+B` · pow `X=2**10`.
gvar_arith_slot: slot `D=A+B+C` · slot2 `E=A+B*C` · s3 `F=A+B+C+E` · s5 `G=(A-B)*(A+B)`. (All `OUTPUT = …`; SCRIP is CASE-SENSITIVE — uppercase `OUTPUT`.)
A/B method: build baseline (`git stash` the edits → `build_scrip.sh` → save binary → `stash pop` → rebuild) → `--compile` both → strip `#`-comment lines + normalize `bb[0-9]+_`/`.Lcall[0-9]+`/`.S[0-9]+`/`.Lpb[0-9]+` → diff.

## Gate floors (held pre+post every commit)
sno m4 7/7 HARD · pat M2 19 M4 19/0 · icon m2 12/12 HARD m3=m4 10/2 · prolog 5/5 ×3 · prove_lower 0P+0F rc=0 VACUOUS · purity 1 (bb_call_write_slot) · bin_t 0 · vstack 3 · handencoded 0 · med_inv 75 · sno_pat_reg HARD · emit_blind 0.

## Open PINs (need Lon's word)
1. **LANGUAGE-BLIND audit category** (carried from 71st run). Claude's stated sequence this session: certify gvar_arith first [DONE] → add a LANGUAGE-BLIND check to `audit_bb_fixup_file.sh` that flags reads of driver-mode/language state-globals (`g_gvar_flat_chain`, `g_descr_flat_chain`, `g_icn_scan_regs_live`, `g_gvar_callarg_live`) inside `bb_*.cpp` — distinct from legitimate `extern` FUNCTION decls (`rt_*`, `POWER_fn`) → strip siblings as the sweep reaches them. **DEFERRED — did not trigger unilaterally** because adding the check retroactively flips ~7 BEHIND-cursor files dirty (`bb_binop_gvar_relop`, `bb_var`, `bb_var_frame`, `bb_assign_frame`, `bb_assign_frame_ref`, `bb_binop_gvar_arith_slot` [stripped this run], `bb_call`), INCLUDING bb_call/324 → forces a cursor-reset cascade. Options: (a) extend byte-neutral strip to siblings now, (b) add audit category + accept the reset, (c) defer to FIX-FENCE.
2. **FIX-3-iii PIN** for `bb_call.cpp`: the `dval==2/3` mass (byname/userproc/named-proc/staged) — how `IR_CALL_GEN_SCAN` (Icon scan builtins) peels off `IR_CALL_PROC_STAGED`/`NAMED_PROC` so the native fast-path keys on a KIND, not `dval==3+sval`. Co-owned with IRD/ICN. PIN before touching the dval channel (the OPERATION-section three-revert lesson).

## Standing verdicts (carried, none new)
m2 disj-backtrack (PROLOG-BB) · prove_lower VACUOUS ratify (IR-REDESIGN) · pK m4 silent-empty (PROLOG-BB/RAKU-BB) · brokered-catch m3/m4 silent (PROLOG-BB) · str-relop m3-empty (ICON-BB) · gvar-relop box ungated (ICON/lowering) · rank rp-patch ratify · ceiling-ratify 1192.

## NEXT SESSION
Cursor `bb_call.cpp` (TOTAL=324, FIX-3). FIX-3-i (write-family de-walk) + FIX-3-ii (DEFINE carve) are **PIN-FREE** and can proceed per their LADDER step recipes; FIX-3-iii needs the PIN above — surface live and **STAY on the file** per SOP (no advance, no "skipped"). Clone SCRIP + corpus; baseline battery GREEN before first edit. SCRIP @ `a6e0a18` · `.github` @ this commit.
