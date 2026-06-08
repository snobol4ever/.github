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

**OPEN — IRD-3 bulk (c): RING CLUSTER + SEQ α-ORPHAN COMPLETE
(2026-06-07-H, Opus 4.8, Lon attending).**
This session, SCRIP commits (each fully gated, all pushed):
8af31d1 RING CONSUMERS — interp arms for every
icn_ring_to_tree-served kind → operands-first dual-read
(BINOP_GEN/TO/TO_BY hoisted ir_pair_arg Lc/Hc locals incl
ring-mode discriminators; UNOP/NEG/POS/NONNULL/NOT/SIZE
single-child c0 idiom; EVERY already dual since 3e); emitter
side pre-verified dual BEFORE edits (flat_drive_* via
bb_child0/1, bb_every.cpp via ir_call_arg,
descr_chain_operand_refs already operands SCAN-exempt,
bb_walk_rec operands-aware, ir_is_single_shot walks operands);
m2-safety proof: lowering carries these kinds via
γ-chain/aux/operands so α/β NULL in m2 — NULL-for-NULL
identical. 21add4c RING WRITER FLIP — icn_ring_to_tree
ar==2/ar==1 → operands[0..1], order [0]=left [1]=right matching
ir_pair_arg + descr_chain_operand_refs; function now ZERO α/β
writes; PROOFS: gdb live-path (pre-flip bp scrip.c:92 fires on
write(*&subject) ring-live probe; post-flip ir_operand_push
frame#1 = icn_ring_to_tree:94 same probe), stash A/B behavior
parity ×2 probes (both hit PRE-EXISTING GROUND-ZERO-3
rt_call_builtin abort downstream, rc=134 parity — B-ladder
scope), static dump A/B EMPTY-class (ring conversion runs in
m3/m4 driver AFTER --dump-bb, faa9b52 precedent). 6c12e26 SEQ
α-ORPHAN DELETIONS — zero writers by broadened census (LAW 8) +
builder proof (wire_seq γ-chains children, never stores
node->α); deleted flat_drive_seq dead BFS (~45 lines, guard
pair-jmp path IS the function, still serves SEQ + SEQ_EXPR
dispatch) + orphan seq_node_label + interp raku-SUSPEND arm +
tail return-α→NULL fold; dval==1.0 concat arm has no α
dependence, STAYS; proof = bake byte-identity (A/B-EMPTY
deletion standard).
GATES per commit: full bake scripts/bake_ird3_baseline.sh diff
vs pristine /tmp/base_pre = prove_lower col-7 pointer ivals ONLY
(LAW 6) masked-identical PASS=68; 5 sweeps (sno 153/icn 9/pl 8/
pas 5/sco 191) + 5 smokes byte-identical; icon m2 12/12 HARD
m3/m4 10/2 floors.
RACE ABSORBED ×1: pull-rebase pulled ed5fe6e + 8f4f773 (IRD-2b
gz reader flip units[j]->β→operands[1], pl rungs m3 22→29) +
0af3eb7 + 66c7bdf (BB-FIXUP bb_unify/bb_unop); merged head
REBUILT + FULL RE-BAKE byte-identical (LAW: clean rebase is NOT
a gate). gz-synth therefore ACTIVE-CONCURRENT — see REMAINING.
COUNTS: IR_interp.c α/β refs 184→105; emit_bb.c →46;
icn_ring_to_tree →0 writes.
FINDING (IRD-4 lever): lower_internal.h iref() ALREADY writes
IR_ref_t{node,"α"/"β"} — the target carrier exists in lowering.
NEXT (goal order):
1. Bulk (c) — gz-synth regime FIRST but FRESH census + IRD-2b
coordination mandatory (8f4f773 owner active in those files);
then SCAN ruling (pattern-BB joint), flat_drive_gz_query
γ-walks, emit_bb 2045 arm-via-ω, bb_call.cpp:93, operand_aux
sub-cluster (LOAD-BEARING) LAST. Residue verifies opportunistic:
IR_SEQ_EXPR α-chain; raku_nfa ruling from Lon.
2. IRD-4 → 3. IRD-5 (incl. prove_lower ops column + CATCH kname
+ sno sweep timeout bump).
HANDOFF 2026-06-07-H CLOSED (Opus 4.8): SCRIP origin = f06732d
(6c12e26 + handoff doc), .github origin = this commit; both
trees CLEAN, all pushed. See
HANDOFF-2026-06-07-OPUS48-IR-REDESIGN-IRD-3C-RING-SEQ.md.
Next session: clone/pull BOTH repos (authenticate origin with
Lon's token: git remote set-url origin
https://TOKEN@github.com/snobol4ever/<repo>), git identity
LCherryholmes/lcherryh@yahoo.com per repo, apt-get install -y
libgc-dev; make; make libscrip_rt (MANDATORY for m4), clone
canonical refs (proebsting/jcon + gtownsend/icon → refs/,
gitignored), bake scripts/bake_ird3_baseline.sh /tmp/base_pre
FOREGROUND BEFORE touching code, git pull --rebase both repos
before working, then bulk (c) per NEXT. Concurrent sessions:
IRD-2b/PROLOG (owns the gz reader sites — coordinate),
BB-FIXUP (owns BB_templates + tracker, cursor at bb_var.cpp,
rebase before touching bb_*.cpp), B0/B-ladder (runtime purges +
GROUND-ZERO-3 box rebuilds), pattern-BB design (joint owner of
the SCAN-subject ruling). ALWAYS re-verify any rebased head.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
