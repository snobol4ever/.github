# GOAL-IR-REDESIGN.md — IR_t = pure BB wiring: {op, γ, ω, operands}

**Owner repo:** SCRIP + this file. **Scope: ALL LANGUAGES** — IR_t is shared.

## TARGET SHAPE (Lon ratified 2026-06-07)

```c
typedef struct {
    IR_t  * node;
    char    sz[4];      /* literal "α" or "β" — the target block name */
} IR_ref_t;

struct IR_t {
    IR_e       op;          /* the operator — selects α and β templates */
    IR_ref_t   γ;           /* success wire → some box's α or β          */
    IR_ref_t   ω;           /* failure wire → some box's α or β          */
    IR_t    ** operands;    /* realloc array: boxes whose RESULT feeds this op */
    int        n_operands;
    int        idx;         /* sidecar key — lit[]/exec[] parallel arrays (Lon ruling 2026-06-07) */
    IR_graph_t * own;       /* owning graph — resolves idx for IR_LIT/IR_EXEC (Lon ruling 2026-06-07) */
};
```

Box = operator + two outbound port wires + operand list. NOTHING else.
A box's α/β are not fields — they are this node at "α"/"β" in someone's
IR_ref_t. Result value: NOT in IR_t (multi-instance; interp/emitted code
memory-manage it). Literal payload (sval/ival/dval): SIDECAR. Runtime
state (value/counter/state): SIDECAR or per-activation. Use literal "α"
"β" strings in code, never named constants (IDE color).

## RATIONALE RECORD

JCON ir_OpFunction(coord, lhs, fn, argList, failLabel) maps: fn→op,
failLabel→ω, success→γ, lhs→IMPLICIT (box's own result; identity names
the slot), argList→operands. Arity 0..N proven required: 0=literals,
1=unop, 2=binop, 3=sectionop x[i:j], N=call args/MakeList. γ/ω are
INHERITED attributes (passed down by parent); α/β are SYNTHESIZED (the
node's own blocks, selected by op). The 4-pointer α/β/γ/ω IR_t conflated
operand links, chain edges, port wires, and runtime state — 876
value/counter/state hits in IR_interp.c, 0 in emit_bb.c.

## LADDER — strict order, gate after each

- [ ] **IRD-3 — OPERANDS: α/β children → operands[]/n_operands.**
  STATUS: sno/icon/raku/pascal/program AND prolog lowering files
  carry ZERO child α/β writes (IRD-3d/3e, session -G). RING
  CLUSTER COMPLETE (session -H, commits 8af31d1 21add4c):
  icn_ring_to_tree carries ZERO α/β writes; every ring-served
  kind's interp arm (BINOP_GEN/TO/TO_BY/UNOP/NEG/POS/NONNULL/
  NOT/SIZE) operands-first dual-read. SEQ α-orphan DELETED
  (6c12e26): flat_drive_seq dead BFS + interp raku-SUSPEND arm
  + tail, zero-writer + builder-source proven, bake-identical.
  Remaining α/β writes live ONLY in driver gz-synth (+ raku NFA,
  ruling pending below).
  REMAINING:
  (c) BULK: SCAN subject α (gvar writer ONLY — SCAN operands hold
  IRD-3a type-punned subj/repl GRAPHS so the slot map is a
  pattern-BB joint ruling; op_a, bb_walk_rec and both chain
  writers carry the SCAN exemption);
  gz-synth (⚠ ACTIVE-CONCURRENT since 8f4f773 IRD-2b fix flipped
  reader units[j]->β→operands[1] mid-session-H — FRESH census
  mandatory before touching; driver pl_gz_* writes α/β on
  synthesized CELL_UNIFY/DET_IS/DET_CMP/DET_WRITE/ARITH-copy
  nodes ~598-1099 — emit marshal arms + bb_det_is.cpp + bb_is_cmp
  rhs-ARITH internals + bterm_arith read that regime, dual-read);
  flat_drive_gz_query γ-walks ~572-595 (synthesized DET chains);
  emit_bb 2045 arm-list-via-ω;
  bb_call.cpp:93 CALL fallback helper; operand_aux callers fold
  in THEN operand_aux DELETED at sweep end — ⚠ LOAD-BEARING,
  census 2026-06-07-G: 8+ live get callers (emit_bb 315/360/382/
  689/2481/2607 ALT-arms/chain-child + bb_alt.cpp:34 +
  bb_call.cpp:96), set callers uncounted — a real sub-cluster,
  NOT a micro-commit. RETURN chain:
  descr_chain_arity RETURN STAYS 1 — the slot-priming consumer is
  emit_core.c:440 dual-read (arity→0 empirically broke proc m3 at
  fbfd71c).
  LAWS: census every kind in driver/ too — classifiers ARE
  consumers; never truncate the consumer grep (fbfd71c). Generic
  WALKERS and the generic op_a_* template feed are consumers
  (d20c45e RED cycle: bb_walk_rec missed operand-held literals →
  empty .rodata strings; op_a_* was the hidden SCAN-α reader —
  same-line greps lie for switch-case consumers). Any walker over
  operands[] MUST exempt IR_SCAN (operands hold IRD-3a subj/repl
  GRAPHS cast as IR_t*). bb_child0/bb_child1 (emit_bb.c) = the
  dual-read accessors; ir_call_arg/ir_pair_arg (IR.h) = the
  contract-level pair. NEW LAW (2026-06-07-G, bb_term_io 141/155):
  α-keyed censuses MISS freestanding RELATIVE γ-hops on
  already-fetched arg locals (a1 = a0->γ) — at every flip, grep
  '->γ' in the kind's consumer files too, not just '->α'. NEW LAW:
  guards that name a kind by sval/ival WITHOUT mentioning α/β
  hide parallel readers from α-keyed sweeps (pl_gz_rule_callee_body
  write arm, caught+fixed in 9134387) — grep by BUILTIN NAME too.
  NEW LAW (8) (2026-06-07-H): writer censuses MUST include
  dot-access / deref / memcpy write shapes, not just '->field ='
  (broadened sweep caught only audit-tool dot-writes this time;
  the shape gap was real).
  RESIDUE FLAGS (bulk scope): interp IF/WHILE/UNTIL/EVERY ->β
  then/body reads have ZERO writers in src (write census
  2026-06-07-D, re-verified -G at the 3e-rest flip) —
  verify-then-delete candidates, NOT chain-fed. interp
  IR_SEQ_EXPR α-chain reads: same zero-writer class (census -H),
  needs its own verify pass before deletion. raku_nfa_bb.c
  154/158 NFA α writers (self-loop init + out2) are OUTSIDE this
  goal's enumerated remaining list — LON RULING NEEDED: missed
  cluster vs NFA exemption.
  COVERAGE GAP (fence-era, owner=admission layer NOT IRD): compound
  format/2 (format("~w~n",[42])) m3 ABORTS at PL-GZ FENCE
  ('not admitted by pl_gz_admit or pl_flat_body_root'), m4 rc=1
  empty, m2 correct — worktree-PROVEN PRE-EXISTING at 6e3cb1e~1
  (pre-IRD-3d); BB-FIXUP b8e3a04 tracker attribution to the
  IRD-3d flip is WRONG on causality (answered in 3cedeea). Smoke
  corpus has no compound-format case — add one when admission
  lands.
  GATE per cluster: build = apt-get install -y libgc-dev; make;
  make libscrip_rt (MANDATORY for m4). Bake
  scripts/bake_ird3_baseline.sh BEFORE touching code (script now
  includes sco sweep 191 + rebus smoke; rebus PASS=0 FAIL=4
  pre-existing); post-bake and diff: all sweeps byte-identical;
  smoke rows identical; prove_lower PASS count (68); live-kind
  probes per kind; A/B git-stash for any anomaly. KNOWN FLAKE:
  test/snobol4/keywords/100_roman_numeral.sno runs 7.7-7.9s vs
  the 8s sweep timeout — flaked rc=124 once under bake load
  (415e465 gate), 153/153 identical on idle re-run; pre-existing,
  bump the timeout when convenient.

- [ ] **IRD-4 — WIRES: γ/ω become IR_ref_t; α/β fields DELETED.**
  Change IR_t.γ/ω from IR_t* to IR_ref_t{node, sz}. Every wire write
  states its target block: strcpy(r.sz,"α") fresh-entry, "β" resume
  (conjunction right-ω→left-β, every body→expr-β, etc. per irgen.icn).
  Interp/emitter follow ref.node + dispatch on ref.sz[1] (0xB1/0xB2).
  Chain-edge abuses of γ/ω (arm lists via ->ω, arg lists via ->γ)
  already migrated in IRD-3. DELETE α/β fields; rename t→op.
  GATE: build green; full suites; grep '->t\b' == 0 in IR consumers;
  baselines identical.

- [ ] **IRD-5 — FENCE: audit + doc.**
  sizeof(IR_t) recorded before/after. Grep gates: no ->value/->counter/
  ->state outside exec sidecar; no ->sval/->ival/->dval outside lit
  sidecar; IR_t struct has exactly 7 members (5 ratified + idx/own
  sidecar key, Lon ruling 2026-06-07). Update ARCH-IR.md.

## DO NOT

- Touch chunk.h/.c or the JCON chunk-IR path (GOAL-ICON-IRGEN owns it).
- Fix ival-pointer / dval-flag abuses inside IRD-2 (move, don't fix).
- Reorder ladder: BREAKOUT FIRST (Lon 2026-06-07) — per-language sweeps
  in IRD-3/4 need the per-language files to exist.
- Change γ/ω SEMANTICS — only their carrier type.

## Watermark

**IRD-3(c) GZ-SYNTH CLUSTER + gen_alt/arith_operands/SEQ_EXPR — ✅ LANDED ON MAIN at
1d3b397 (2026-06-08, Opus 4.8, Lon attending). Recovery complete: reconstructed by taking the
25 non-Pascal GZ files from origin/ird3-gz-recovery onto origin/main, then REBASED over a
concurrent parallel push (M34-2-complete 2127c82, PB-24 2D-arrays f90afa4, FIX-7b x86_asm.h
11a3062). IR_interp.c was the only shared file; its hunks were disjoint (M34=rt_is_cell 667-793,
GZ=IR_interp_node 2504+) so the rebase auto-merged clean. Landed via GUARDED fast-forward (NO
force) — a parallel push moved origin mid-session and the pre-push guard correctly aborted then
rebased. Post-rebase gate GREEN: prove_lower PASS=68, prolog 5/5/5 (arith ratchet holds under
M34-2-complete), icon m2 12 / m3 10 / m4 10 at floors. origin/ird3-gz-recovery now redundant —
safe to delete on Lon's word.**

### Done this session (all gated: full bake vs pristine = prove_lower LAW-6 col-7
pointer ivals masked-identical PASS=68; all sweeps + smokes byte-identical; reconciled
final bake GREEN, prolog 5/5/5, icon m2 12 / m3 10 / m4 10 at floors):
- GZ CONSUMERS dual-read (was SCRIP c526ad3): gz_fill_goal DET_WRITE, flat_drive_gz_query
  QUERY_FRAME hd/hdB=bb_child0/1 (9 fetches; gamma-walks STAY = legitimate success chain),
  marshal DET_IS/DET_CMP arms, bb_det_is 3 helpers, bb_is_cmp rhs+pBB child-hops, bterm_arith,
  scrip.c:890 units twin (8f4f773 sibling, fprintf-probe-proven DEAD on full pl corpus).
- GZ WRITERS flip (was f8b3a91): all 15 a/b writes in pl_gz_* synth (scrip.c 603-1108) ->
  ir_operand_push, [0]=a-role [1]=b-role; null-guards locals-first; QUERY_FRAME four-combo-
  exact (push head iff head||headB, push headB iff headB); ARITH-copy mirrors m0/m1.
- flat_drive_gen_alt arm-via-omega DELETED + bb_call arith_operands operands-first (was fb4ffcc):
  verify-then-delete, zero-writer (a-writers EXTINCT src-wide post-flip) + builder proof.
- interp IR_SEQ_EXPR alpha-chain DELETED (9c42343): guard !bb->a always-true -> fold to NULVCL/gamma.

### RATCHET (proven, stash-A/B): prolog smoke arith m3+m4 FAIL->PASS (4->5 both). Pristine
rc=134 'unresolved gzq0_g0_b' = bb_is_cmp is-arm guard read ->a/b NULL on LOWERED operands-only
ARITH rhs (scrip.c:960); IRD-2b producer flip had STRANDED these readers; consumer dual-read
repaired it. Live IRD-2b-class fix, not refactor anomaly.

### FINDINGS
- IR_GEN_ALT kind is CONSTRUCTOR-LESS (zero builders src-wide; flat_drive_gen_alt serves IR_ALT
  non-flat-chain branch; interp 4295 arm is exec-sidecar DCG, its a/b are port-CONSTANTS not
  fields). Kind-garden deletion candidate — OUTSIDE IRD scope, flag for Lon.
- 053_pat_alt_commit.sno m2 output delta is B3-owned (7a12aed TT_ALT lowering), not IRD.
- flat_drive_gz_query gamma-walks = legitimate success wiring, NOT chain-edge abuse; stay until
  IRD-4 carrier-type change.

### HISTORY (resolved — git preserves full detail): the IRD-3c gz commits c526ad3/f8b3a91/
fb4ffcc were erased from main by TWO force-pushes (a stale-clone reset, then a Pascal/M34
landing), preserved meanwhile on origin/ird3-gz-recovery (reconciled tree 4a8236b), and
re-landed this session as recorded in the watermark above. LON: WORKFLOW RULING STILL WANTED —
mandate --force-with-lease / ban hard resets / require fetch+rebase-before-push. The pre-push
GUARD (assert origin/main == HEAD~1 parent, else abort+rebase, never --force) is what prevented
a THIRD incident this session when a parallel push moved origin mid-work; recommend adopting it
as the standard push wrapper.

### REMAINING IRD-3 (c): SCAN subject a (joint pattern-BB ruling); operand_aux sub-cluster
(LOAD-BEARING, 8+ live get callers, LAST); raku_nfa_bb.c 154/158 a-writers (Lon ruling: missed
cluster vs NFA exemption). Then IRD-4 (gamma/omega -> IR_ref_t, delete a/b, t->op; iref() carrier
already exists) -> IRD-5 (sizeof fence + ARCH-IR.md).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
