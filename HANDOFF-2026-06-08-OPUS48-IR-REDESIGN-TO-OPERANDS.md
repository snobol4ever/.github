# HANDOFF 2026-06-08 OPUS48 — IR-REDESIGN: IRD-3 TO operand_aux fold (interp half)

**State:** SCRIP origin/main = `e8c9d49`, .github origin = this commit. Both trees CLEAN, pushed.
Lon directive this session: "this refactor of the lower stage is straightforward, so it is all on
you" — i.e. land changes without per-commit review.

## What landed — `e8c9d49` (one commit, fully gated)

IRD-3 TO, INTERP half of the operand_aux fold:
- `lower.c` `v_to`: now `ir_operand_push(node, lo/hi)` in addition to the existing
  `bb_operand_aux_set` (aux SET retained — it still feeds the emit slot machinery, migrated later).
- `IR_interp.c` `case IR_TO`: reads bounds via `ir_pair_arg(bb,0/1)` (Lc/Hc) instead of
  `bb_operand_aux_get`; the static-ag guard now tests `sval[0]=='a'` instead of `!Lc && !Hc`.

## The finding that drove it (NEW LAW — operand_aux)

The aux kinds encode **operands[]-emptiness as a static-vs-dynamic discriminator**. TO's
`!Lc && !Hc` (and `ir_pair_arg` is operands-first) double-served as "this is a static-ag node,
read its bounds from aux". So naively pushing operands[] flips static-ag TO into the dynamic
branch → `roman.icn` m2 went empty (caught in a reverted probe, then root-caused). RULE: never
populate operands[] for an aux kind without first re-expressing its discriminator on a real marker.
`v_to` is the SOLE IR_TO producer and never sets a/b, so the dynamic branch is unreachable and the
guard swap is byte-identical.

## Gate (the discipline that held all session)

Bake = `scripts/bake_ird3_baseline.sh`. Floors: prove_lower **PASS=68**, icon m2 12 / m3 10 / m4 10,
prolog 5/5/5, sweeps sno153/icn9/pl8/sco191/pas5 byte-identical, smokes identical.
- Verified byte-identical on the ORIGINAL base, then A/B vs a FRESH origin bake after rebase.
- Absorbed **3 concurrent races** (re-baseline `4554a14`, M34-4, PB-28 `71d0d49`) via the pre-push
  GUARD (assert `origin/main == HEAD~1` else rebase+rebuild+re-gate, never `--force`). LAW reaffirmed:
  a clean rebase is NOT a gate — rebuild + re-bake the merged head every time.

## NEXT (goal-file REMAINING order)

1. TO **emit** half: move `bb_to.cpp` `op_sa`/`op_sb` (descr_chain_arity slot path) off aux, then
   DROP the `v_to` aux SET → TO fully migrated. (Probe proved operands[] doesn't disturb m3/m4, so
   emit reads slots/chain not aux — verify the op_sa/op_sb assignment site first.)
2. BINOP — easier than TO (guard reads a/b FIELDS not operands[], so population won't flip it);
   consumers include BB-FIXUP-owned `bb_binop_*`/`bb_gvar_assign`/`bb_assign_frame_ref`/`bb_call`.
3. ALT/DISJ arm-lists; APPLY/call-args; single-child; THEN delete `bb_operand_aux_set/get` + the
   `operand_aux` field/typedef.
4. PENDING LON RULINGS (unchanged): SCAN subject a (joint pattern-BB owner); `raku_nfa_bb.c`
   154/158 a-writers (missed cluster vs NFA exemption) — both cleaner at IRD-4.
5. Then IRD-4 (γ/ω → IR_ref_t, delete a/b, t→op) → IRD-5 (sizeof fence + ARCH-IR.md).

## Next-session boot

Clone/pull both repos; `git remote set-url origin https://TOKEN@github.com/snobol4ever/<repo>`;
identity LCherryholmes/lcherryh@yahoo.com per repo; `apt-get install -y libgc-dev; make;
make libscrip_rt` (MANDATORY for m4); bake `scripts/bake_ird3_baseline.sh /tmp/base_pre`
FOREGROUND before touching code. Concurrent sessions live: BB-FIXUP (owns BB_templates), Pascal
(PB-*), SNOBOL4-BB (B*) — `git pull --rebase` both repos before working, A/B-gate every flip.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
