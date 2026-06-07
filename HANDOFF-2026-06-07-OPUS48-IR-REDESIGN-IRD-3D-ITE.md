# HANDOFF 2026-06-07-F OPUS48 — IR-REDESIGN: IRD-3d-ITE LANDED

## Commits (SCRIP origin/main)

- `c03d46b` IRD-3d-ITE — prolog ITE cond-entry α → operands[0]

Rebased at push over the parallel BB-FIXUP lap + Lon's `d3907e8`
DUMP-V2; merged tree re-baked GREEN (all sweeps byte-identical vs
the pre-change bake).

## What landed

**IRD-3d-ITE.** Writers `g_ite` / `g_neg_goal` / `g_not_unify`
(lower_prolog.c 312/333/354): `ite->α = cα` DELETED →
`ir_operand_push(ite, cα)`. Sole runtime α reader, interp
`case IR_ITE` `return bb->α` → `return ir_call_arg(bb, 0)`
(dual-read). Resume path reads `zi->then_/else_` sidecar —
untouched.

**Census-proven invariant (no edits needed):** emit
`flat_drive_ite` + driver `pl_gz_count_synth_goal` /
`pl_gz_build_goal` / `pl_ite_then_branch_trivial` classifier ALL
read the `zi` sidecar (cond/then_/else_/*_root) — zero α reads;
emit_core op_a priming is already operands-first dual-read, so ITE
gaining operands[0] primes the SAME node it primed via α;
`ir_is_single_shot`'s generic default arm walks α AND β AND
operands[] — invariant; `bb_reset` port-free; `bb_ite.cpp` template
has zero op_a/α reads; zero IR_ITE refs in m4 marshal outside
emit_bb/emit_core.

## Gate

- sno 153 / icn 9 / pl 8 / pas 5 / sco 191 sweeps + 5 smokes +
  rebus: BYTE-IDENTICAL pre/post, and again on the merged tree
  after the rebase.
- prove_lower PASS=68 both sides; git-stash A/B dump diff is
  EXACTLY the ITE α column (8→-1 ite-else row, 7→-1 bare-if row).
  The two ITE rows' node-count FAILs (10 vs expected 8, 9 vs 7)
  are PRE-EXISTING and identical both sides.
- LIVE-KIND PROBE m2: scratch-instrumented build printed
  `[ITE-LIVE ops=1]` ×2 on an `->`-probe with correct `lt`/`ge`
  output — the case fires and the operands[0] read is live.
- m4 probe: emitted asm shows xite then/else arms wired via the
  sidecar, correct shape, rc=0.
- m3 probe rejection (`pl_gz_admit` no-blob FATAL; interp fallback
  deleted 2026-06-06) A/B-PROVEN PRE-EXISTING at `c9e018e` —
  identical rc=134. LAW-5: not chased.

## Laws recorded this session

1. **prove_lower ival column prints sidecar POINTERS** — ASLR
   run-to-run noise. md5 comparison is INVALID for prolog rows;
   STRUCTURAL diff is the comparator.
2. **prove_lower.sh RECOMPILES lower*.c from source.** A bake
   taken after source edits is contaminated for the prove_lower
   log even when the `./scrip` binary is stale. git-stash A/B for
   the true pre-change dump.
3. **Environment: background jobs are REAPED between tool calls.**
   Run `bake_ird3_baseline.sh` FOREGROUND (~2-3 min).

## Banked census for the NEXT sub-clusters (do not re-derive)

**Pair-name set is EXACTLY the routing at lower_prolog.c
~495-511:** g_compare `<` `>` `=<` `>=` `=:=` `=\=` · g_is `is` ·
g_term_compare `==` `\==` `@<` `@>` `@=<` `@>=` `succ`. ALL other
names/arities γ-chain via g_builtin.

**Pair needs its own accessor** `ir_pair_arg(nd, j)`:
operands-first, else `j ? β : α`. `ir_call_arg`'s fallback is
WRONG for pair arg1 — `lα->γ` may be wired into arith-subgraph
internals, the γ-hop lands inside the lhs subgraph, not on rhs.
γ-chain shapes (STRUCT, g_builtin) reuse `ir_call_arg` as-is —
identical α + γ-hop topology to CALL.

**Driver scrip.c ~517 guard** (`ival==2 && gg->α && gg->β`)
currently shape-sniffs by β-presence (γ-chain never writes β).
Post-conversion BOTH shapes have n_operands==2 — the name set
(is_cmp) must gate instead. Return-0 semantics proven equal both
regimes (γ-chain hit → !is_cmp → 0 either way).

**γ-chain consumer surface:** interp resolve 352 STRUCT walk +
`case IR_STRUCT` 4725; ~40 builtin `a0=bb->α, a1=a0->γ, a2=a1->γ`
sites interp 4836-5500 (incl. `a1->α` at 5055 = nested STRUCT arg0
→ `ir_call_arg(a1,0)`); bb_atom_string.cpp BUILTIN template sites;
driver classifiers ~293-335 (`is`/`succ`/`plus`/io) + 505-523 +
gz-synth LOWERED-node reads 617-700. gz-synth SYNTHESIZED-node
writes (CELL_UNIFY/DET_*) stay — bulk stage (c).

**kind 380 g_catch** (`bb->α = cα` catcher): interp 4763 reads
`bb->α`; driver 1242 reads `zc->catcher` sidecar.

All lower_prolog.c line numbers LIVE-GREPPED at c03d46b (the ITE
edits were 1:1 line replacements — numbering held): pair 178/193/
208, STRUCT 228/253, g_builtin 271, catch 380.

## Coordination

- **DUMP-V2 (Lon, `d3907e8`, mid-session):** print_port DELETED;
  `--dump-bb` one-line revamp; α/β dump columns dropped (dying
  fields); PORT-LAW idx+entry-letter convention until IRD-4
  IR_ref_t.sz. Anticipates IRD-4 — the prove_lower "harness lacks
  ops column" note is now partially addressed by Lon's design.
- BB-FIXUP runs concurrently and owns BB_templates — rebase before
  touching any bb_*.cpp.
- pattern-BB design co-owns the SCAN-subject ruling (deferred).

## Next session start

clone/pull BOTH repos (token per Lon), git identity
LCherryholmes/lcherryh@yahoo.com per repo,
`apt-get install -y libgc-dev; make; make libscrip_rt`, bake
`scripts/bake_ird3_baseline.sh /tmp/base_pre` FOREGROUND before
touching code, then IRD-3d remainder: γ-chained STRUCT+g_builtin →
pair (ir_pair_arg) → kind 380, per GOAL-IR-REDESIGN.md NEXT.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
