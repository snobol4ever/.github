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

- [ ] **IRD-4b — CARRIER FLIP: γ/ω become IR_ref_t.** (t→op rename DONE
  + pushed, SCRIP `aae8686`; grep '->t' == 0 in pure consumers, baselines
  byte-identical, 35-file 761/761 pure rename.) REMAINING = carrier flip:
  Change IR_t.γ/ω from IR_t* to IR_ref_t{node, sz}. Every wire write
  states its target block: strcpy(r.sz,"α") fresh-entry, "β" resume
  (conjunction right-ω→left-β, every body→expr-β, etc. per irgen.icn).
  Interp/emitter follow ref.node + dispatch on ref.sz[1] (0xB1/0xB2).
  Chain-edge abuses of γ/ω (arm lists via ->ω, arg lists via ->γ)
  already migrated in IRD-3. iref() carrier already exists. DO NOT change
  γ/ω SEMANTICS — only carrier type (all targets currently fresh-entry, so
  sz="α" initially preserves behavior; β-targeting is a later semantic
  step). GATE: build green; full suites; baselines identical. Fresh +
  atomic; NO safe partial (field-type change breaks every deref at once).

- [ ] **IRD-5 — FENCE: audit + doc.**
  sizeof(IR_t): BEFORE 64 (t+α+β+γ+ω+operands+n_operands+idx+own), AFTER
  α/β deletion 48 (53f861b). MEMBER COUNT NOW 7 (target met:
  op,γ,ω,operands,n_operands,idx,own — t→op DONE aae8686; only γ/ω
  carrier-type remains, IRD-4b sub-task 2). Grep gates: no ->value/->counter/->state outside exec
  sidecar; no ->sval/->ival/->dval outside lit sidecar; IR_t struct has
  exactly 7 members (5 ratified + idx/own sidecar key, Lon ruling
  2026-06-07). ARCH-IR.md currently documents tree_t (AST) + the SM/broker
  model, NOT the IR_t struct fields (the α/β/γ/ω there are conceptual
  PORTS, still valid) — ADD an IR_t struct-shape section here after IRD-4b.

## DO NOT

- Touch chunk.h/.c or the JCON chunk-IR path (GOAL-ICON-IRGEN owns it).
- Fix ival-pointer / dval-flag abuses inside IRD-2 (move, don't fix).
- Reorder ladder: BREAKOUT FIRST (Lon 2026-06-07) — per-language sweeps
  in IRD-3/4 need the per-language files to exist.
- Change γ/ω SEMANTICS — only their carrier type.

## Watermark

**▶ HANDOFF (2026-06-08, Opus 4.8) — IRD-4b SUB-TASK 1 (t→op) DONE + PUSHED. SHAs: SCRIP `aae8686`,
.github THIS COMMIT — SCRIP builds green from clean (scrip + libscrip_rt), pushed to origin. Re-bake
recipe + PASS criteria UNCHANGED (see the demoted block directly below). DONE THIS SESSION: the IR_t
kind field renamed `IR_e t -> IR_e op` across every consumer that touches it — IR_interp.c, all
emitter/** (BB_templates + emit_bb.c + emit_core.c), scrip_ir.c (alloc+dump), the AST→IR producers'
IR-side accesses (lower_program.c, lower_value.c, driver/scrip.c gz-synth, parser/raku/raku_nfa_bb.c),
runtime/unification.c, and the SEPARATELY-COMPILED harnesses tools/prove_lower.c +
tools/emit_per_kind_audit.c (⚠ NOT built by `make` — the gate caught them; a future field-touching
step MUST include them). tree_t (AST) ->t left untouched, verified PER-LINE (textual `->t` count ==
compiler-flagged count on every edited line ⇒ no mixed IR_t/tree_t line was blanket-edited; the lone
scrip.c tree_t->t and a 1-line lower_value mixed case were correctly excluded). GATE PASSED: clean
build 0 errors both targets; grep '->t' == 0 in pure consumers (interp/emitter/scrip_ir); 5 sweeps
(sno153/icn9/pl8/sco191/pas5) + 5 smokes byte-identical; prove_lower PASS=68 rc=0 byte-identical
(col-7 ptr-masked). Changeset = clean 761/761 ins/del pure rename, 35 files. **IR_t is now {op, γ, ω,
operands, n_operands, idx, own}.** NEXT = **IRD-4b SUB-TASK 2 — γ/ω CARRIER FLIP** (do FRESH + ATOMIC;
⚠ NO SAFE PARTIAL — changing the γ/ω field type breaks every deref at once, so it is all-or-nothing
through to green build + byte-identical gate + commit; do NOT start near a context limit). Change
IR_t.γ/ω from IR_t* to IR_ref_t{node, sz[4]}; interp/emitter follow ref.node + dispatch on ref.sz[1]
(0xB1='α' fresh / 0xB2='β' resume); iref() carrier helper already exists — update it. DO NOT change
γ/ω SEMANTICS: every current target is fresh-entry, so set sz="α" UNIFORMLY first (behavior-
preserving); β-targeting wires (conjunction right-ω→left-β etc. per irgen.icn) are a SEPARATE later
semantic step. Then IRD-5 (sizeof fence already 64->48; ADD the IR_t struct-shape section to
ARCH-IR.md — best done AFTER the carrier flip so γ/ω's type is documented correctly). NOTES: (a)
src/parser/icon/icon_lex_test.c is DEAD/unbuilt and ALREADY-broken independent of this work — its 37
"member t" errors are about IcnToken, NOT IR_t — out of scope, latent cleanup only. (b) bash_tool
runs /bin/sh — use `bash -c` for process substitution; mask prove_lower col-7 with
`awk '{if(NF>=7)$7="PTR";print}'`. (c) COORDINATE with BB-FIXUP — emit_bb.c is shared; the pre-push
GUARD held (rebased cleanly onto concurrent FIXUP commits 793a613/ed50f54/97b5f5e — disjoint files,
their bb_fail.cpp has zero IR_t refs); push code repos first, .github last, never --force.**

**▶ HANDOFF (2026-06-08, Opus 4.8, Lon attending). SHAs: SCRIP `53f861b`, .github THIS COMMIT —
SCRIP builds green from clean, pushed to origin. /tmp baselines are EPHEMERAL (gone next session) —
re-bake before any gate: `make && make libscrip_rt && bash scripts/bake_ird3_baseline.sh <outdir>`.
PASS = 5 sweeps (sno153/icn9/pl8/sco191/pas5) + 5 smokes byte-identical (ignore wall-clock TIME
lines; smoke_raku is 100% PRE-EXISTING FAIL — Tiny-Raku frontend on hold) + prove_lower col-7(ptr)-
masked PASS=68 rc=0 (3 inherited FAILs: PL-GZ-7 ITE-pair, PL-GZ-8 arith-is). bash_tool runs /bin/sh
-> use `bash -c` for process substitution; mask col-7 with `awk '{if(NF>=7)$7="PTR";print}'`.
STATE: **α AND β FIELDS DELETED from IR_t (53f861b)** — sizeof 64->48, member count now 7 (target).
SCAN SUBJECT RULING (Lon, this session) = operands[2]: IR_SCAN slot layout is now operands[0]=subj
GRAPH, operands[1]=repl GRAPH (both IRD-3a type-punned IR_graph_t*), operands[2]=runtime subject
NODE (formerly α; set by scan_set_subj_node in the gvar-chain walker; emit_core op_a reads it).
Generic walkers already exempt IR_SCAN operands, so [2] is walker-safe. Full IRD-4a detail in commit
53f861b. IR_t is now {t, γ, ω, operands, n_operands, idx, own}. NEXT = IRD-4b CARRIER FLIP (do FRESH +
ATOMIC, it is delicate):
  1. t→op rename — ⚠ `->t` is AMBIGUOUS (tree_t/AST also uses ->t). Disambiguate: rename ONLY IR_t
     consumers (interp/IR_interp.c, emitter/*, lower/*, contracts/scrip_ir.c, driver dispatch). Do a
     scoped census first; the RULES "no ->t in modes 2/3/4" refers to AST tree_t, not IR_t. Gate
     grep '->t\b' == 0 in IR consumers when done.
  2. γ/ω carrier IR_t* -> IR_ref_t{node, sz[4]} dispatching on sz[1] (0xB1='α' fresh / 0xB2='β'
     resume). DO NOT change γ/ω SEMANTICS — every current target is fresh-entry, so set sz="α"
     uniformly first (behavior-preserving); β-targeting wires (conjunction right-ω→left-β etc. per
     irgen.icn) are a SEPARATE later semantic step. iref() carrier helper already exists.
  3. Then IRD-5: record sizeof fence (done: 64->48), ADD an IR_t struct-shape section to ARCH-IR.md
     (it currently documents only tree_t/AST + the SM/broker model, NOT the IR_t struct). COORDINATE with BB-FIXUP — emit_bb.c is shared; the pre-push
     GUARD (assert origin/main==HEAD~1 else rebase, never --force) caught a concurrent push this
     session (e9e8b7f tracker-only); push code repos first, .github last. Full detail + independent-
     confirmation history in the entries below.**

**RAKU-NFA NOW COMMITTED (resolves decision 2 below) + honest scope. (2026-06-08, Opus 4.8, "Yes
migrate to operands; remove fields first, 5 min" — a SECOND IR-REDESIGN session, coordinating with
the delete-first session's entry directly below; identical diagnosis reached independently.) Per
Lon's "Yes, migrate to operands," committed the raku_nfa α/β->operands migration at SCRIP 3a0bf21
(rebased onto BB-FIXUP 69b3417; prove_lower rc=0; raku NFA isolation re-confirmed — IR_NFA_*/raku_nfa
absent from shared interp/emit, so the delta cannot move any gated artifact). This REMOVES β's LAST
WRITER pipeline-wide (β now has ZERO writers -> the β-only-deletion raku prerequisite is MET) and α's
self-loop write (α's sole remaining writer is now the 2 IR_SCAN subject sites). CAVEAT (in commit):
smoke_raku is pre-existing-FAIL, so the SPLIT path is byte-identical but behaviorally UNVERIFIED;
raku is on hold so verification defers to resumption regardless. STILL OPEN for Lon: the SCAN
α->operands slot ruling (decision 1) — the SOLE remaining α blocker; precise sites in the entry
below (writes emit_bb.c:2689/2800; reads emit_core.c:386 + emit_bb.c:2038/2576/2589/2627). HONEST
SCOPE CORRECTION on "5 min": the β-only deletion is the clean partial win but is a ~50+-site
byte-identical bb->β-read->NULL sweep across IR_interp.c + emit_bb.c (incl IR_EXEC(bb->β)/walk_bb_flat
/bb->β->t·γ) — minutes of edits but error-prone; best run ATOMICALLY in a fresh context (delete field
-> compiler flags every site -> fix -> gate -> commit) to honor the no-broken-commit rule, not
started near a context limit. Recommend: (a) land β-only deletion fresh; (b) Lon rules SCAN α slot;
(c) α deletion + t->op + γ/ω->IR_ref_t follows.**

**IRD-4 ATTEMPT (delete-fields-first, per Lon) — BLOCKED ON α BY IR_SCAN; β CLEAN. (2026-06-08,
Opus 4.8, "remove bogus fields FIRST then fixup, 5 min"). Executed the delete-first plan: bulk-swept
all 186 always-NULL α/β READS -> ((IR_t*)0) across IR_interp.c(126)/emit_bb.c(33+1 chained
bb_child0(pBB)->β)/emit_core.c(4)/scrip.c(1)/prove_lower.c(16) — COMPILES + BYTE-IDENTICAL (verified:
5 sweeps + 4 smokes identical, prove_lower cols 3-4 stay -1 -1 since idx_of(NULL)=-1, PASS=68). The
bb_every/bb_cell_ite 'body.β/Then.α/Else.α' + emit_bb 'bb->α' hits were FALSE POSITIVES (string/
comment text, not field access). raku_nfa MIGRATED off α/β -> operands (3 edits: drop dead α
self-loop@154, SPLIT out2 β->ir_operand_push@158, reader s->β->ir_pair_arg(s,0)@77).
*** CENSUS CORRECTION (supersedes the entry below): α is NOT dead-storage — IR_SCAN WRITES it. ***
Field deletion BROKE at emit_bb.c:2689 & :2800 (lvalue error): both chain-walkers
(descr_chain_arity / gvar_chain_arity), arity-1 case, do `if (n->t != IR_SCAN){...operands...} else {
n->α = stk[sp-1]; }` — α is IR_SCAN's LIVE SUBJECT SLOT, distinct from its operands (which hold
IRD-3a type-punned subj/repl GRAPHS). Census missed it (buried in conditional else). So:
  • β — CLEANLY DELETABLE NOW (only raku_nfa used it, now migrated; ~5 min as Lon said): β-reads->NULL
    sweep + raku_nfa(done) + delete β field. No SCAN entanglement.
  • α — BLOCKED. Needs the SCAN joint pattern-BB ruling (Lon): where does SCAN's subject go in
    operands[] without colliding with the subj/repl graph slots? Cannot freelance (RULES reserve it).
REVERTED the α-touching sweep -> main green at SCRIP ab515ff (now absorbed into BB-FIXUP's 42f07cd).
raku_nfa migration HELD UNCOMMITTED + UNVERIFIED: smoke_raku is 100% PRE-EXISTING FAIL (Tiny-Raku
frontend on-hold/broken — every rung 'say string literal'/arithmetic returns EMPTY output), so the
suite is byte-identical but does NOT exercise the migrated NFA SPLIT path. DECISIONS NEEDED: (1) SCAN
α->operands slot ruling (unblocks α); (2) commit raku_nfa now (mechanically correct, removes β's last
writer) or hold for a real raku regex test; (3) land β-only deletion now as the clean partial win?**

**IRD-4 PREP + STRATEGIC FINDING — ✅ LANDED ab515ff (2026-06-08, Opus 4.8, "I want what you
want"). HOW-SOON-TO-DELETE-α/β ANSWERED: α/β are ALREADY DEAD STORAGE for 6 of 7 languages.
Whole-pipeline α/β WRITER census (arrow+dot+all forms): the ONLY non-NULL writers are
raku_nfa_bb.c:154/158 (NFA self-loop α=b + out2 β; ISOLATED — consumed by its own nfa_bt_ir_*
backtracker, IR_NFA_* appears NOWHERE in shared interp/emit) + emit_per_kind_audit.c (diagnostic
tool, not pipeline) + scrip_ir.c:215 (allocator NULL-init). So SNOBOL/Icon/Prolog/Snocone/Rebus/
Pascal nodes ALL have α/β==NULL always. KEY CONSEQUENCE: FIELD DELETION IS DECOUPLED FROM IRD-3
COMPLETION — aux-using kinds (BINOP/ALT/APPLY/single-child) work via operands-empty->NULL in
bb_child0, which `(n_operands>0)?operands[0]:NULL` reproduces exactly once α is gone. So α/β can be
removed AFTER (1) raku_nfa migrated off α/β->operands[] (self-contained ~2 writes + its own readers;
the 'Lon ruling pending' item — ruling is FORCED: can't keep a field one subsystem uses while
deleting it) + (2) the reader sweep (mechanical, byte-identical: every ->α/->β read is NULL-valued
or in a dead branch). NOT gated on finishing BINOP/ALT/APPLY operand migration. Estimate 2-3 focused
sessions to fields-gone. THIS COMMIT = reader-sweep chunk 1: bb_child0/bb_child1 (emit_bb.c) +
ir_pair_arg/ir_call_arg (IR.h) dropped their α/β/α-γ-chain fallback -> operands-only, byte-identical
(raku NFA never reaches these; other nodes' α/β==NULL; IR_BINOP aux discriminator at emit_bb.c:2288
preserved exactly). GATE: 5 sweeps (sno153/icn9/pl8/sco191/pas5) + smokes byte-identical (snobol4
only a wall-clock TIME line), prove_lower col-7-masked PASS=68 rc=0. Guard passed clean.
SUGGESTED LADDER REORDER FOR LON: promote α/β field-deletion ahead of full IRD-3 — gate it on
raku_nfa + reader-sweep only. The remaining reader-sweep chunks: interp direct ->α/->β reads (all
dead branches, e.g. BINOP arm fall-through, since the guard !bb->α&&!bb->β is now always-true) +
emit EMIT-BLIND ->α->t residue + the audit-tool + raku_nfa. Then field delete + t->op + γ/ω->IR_ref_t.**

**IRD-3 TO emit half — ✅ LANDED ON MAIN at 187ae78 (2026-06-08, Opus 4.8, Lon attending,
"your choice, continue"). TO NOW FULLY MIGRATED OFF operand_aux. Dropped the dead
bb_operand_aux_set in v_to (lower_value.c:224): consumer census proved NOTHING reads IR_TO's
aux — interp reads operands[] via ir_pair_arg (e8c9d49), emit reads flat_drive_to via
bb_child0/bb_child1 (operands-first dual-read, slots derived by bb_slot_get on the operand node).
The two emit_bb aux GETs at 2558/2617 serve IR_REF_INVARIANT; 321/366/388/697/2432 serve ALT
arm-lists + chain-children; bb_alt.cpp:34 + scrip.c:113/1033 are ALT; bb_call.cpp:94 is CALL —
none TO. So the v_to aux SET was a dead write; deleting it is byte-identical (operands push lines
RETAINED unchanged). GATE vs pristine bake: 5 sweeps (sno153/icn9/pl8/sco191/pas5) BYTE-IDENTICAL,
5 smokes (icon/prolog/snobol4/raku/rebus) BYTE-IDENTICAL, prove_lower col-7-pointer-ival-masked
IDENTICAL PASS=68 rc=0, IR_TO live m2=m3=m4 (every write(1 to 5)+(2 to 10 by 3) -> 1 2 3 4 5 / 2 5 8
on all three modes). Pre-push GUARD passed clean (origin/main==HEAD~1, no race this push).**

**IRD-3 TO operand_aux fold (INTERP half) — ✅ LANDED ON MAIN at e8c9d49 (2026-06-08, Opus 4.8,
Lon attending, "it's all on you"). v_to now populates node->operands[]=[lo,hi] (the aux SET is
RETAINED, serving ONLY the emit slot machinery, not yet migrated). The IR_TO interp arm reads
bounds via ir_pair_arg(bb,0/1) (Lc/Hc) instead of bb_operand_aux_get, and the static-ag guard
tests the 'a' sval marker instead of !Lc&&!Hc. ROOT-CAUSE FINDING + NEW LAW: the aux kinds encode
operands[]-EMPTINESS AS A STATIC-vs-DYNAMIC DISCRIMINATOR — TO's !Lc&&!Hc (ir_pair_arg is
operands-first) double-served as "this is a static-ag node, read bounds from aux", so naively
populating operands[] silently flipped static-ag TO into the dynamic branch (caught as roman.icn
m2 -> empty in a reverted probe, then root-caused). Any operand_aux flip MUST re-express that
discriminator on a real marker BEFORE populating operands[]. v_to (lower.c:252) is the SOLE IR_TO
producer and never sets a/b, so the dynamic interp branch is unreachable and the change is
byte-identical. GATE: 5 sweeps (sno153/icn9/pl8/sco191/pas5) byte-identical, prove_lower PASS=68,
all smokes identical — VERIFIED ON TWO BASES (A/B bake vs fresh origin), landed via GUARDED
fast-forward after absorbing 3 concurrent races (re-baseline 4554a14, M34-4, PB-28 71d0d49) by
rebase+rebuild+re-gate each time.**

**Prior milestone — IRD-3(c) GZ-SYNTH CLUSTER ✅ at 1d3b397 (git history + the
HANDOFF-2026-06-07-*-IRD-3D/3E docs preserve the full recovery saga). origin/ird3-gz-recovery
redundant, safe to delete on Lon's word. Workflow ruling STILL WANTED: the pre-push GUARD (assert
origin/main == HEAD~1 else rebase, never --force) prevented races on BOTH the GZ session and this
one — recommend mandating it as the standard push wrapper.**

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

### REMAINING IRD-3 (c) — operand_aux retirement, now kind-by-kind GATED flips (TO FULLY MIGRATED
187ae78). Each flip: re-express the kind's discriminator off operands[]-emptiness FIRST, then
populate operands[], migrate consumers, and A/B-gate vs a FRESH origin bake (concurrent
BB-FIXUP/Pascal pushes are constant — 3 races last session alone):
- BINOP — NEXT. EASIER interp profile than TO: its interp guard reads the a/b FIELDS
  (!bb->a && !bb->b), NOT ir_pair_arg, so populating operands[] does NOT flip the INTERP arm.
  ⚠ EMIT HAZARD (found this session, 187ae78 census): the emit IR_BINOP case (emit_bb.c:2207)
  reads children via bb_child0/bb_child1 which are operands-FIRST-then-field, and its
  g_gvar_flat_chain arith/relop arms GUARD on `&& bb_child0(nd) && bb_child1(nd)` — for a
  v_binop BINOP those are NULL today (aux-only), so pushing operands[] would newly-SATISFY those
  guards = a TO-style discriminator flip on the EMIT side. Re-express that emptiness guard on a
  real marker BEFORE populating, exactly as TO required. Producers lower.c (v_binop, lower_value.c:188)
  + lower_pascal.c:51/68/80; consumers interp 325(gen_resume)/2616 + the emit op_a_* feed across
  bb_binop_*/bb_gvar_assign/bb_assign_frame_ref/bb_call (BB-FIXUP-owned — coordinate/rebase).
  PRECISE DISCRIMINATOR (187ae78 census): emit_bb.c:2288 `else if (!bb_child0(nd) && !bb_child1(nd))`
  is the operands-emptiness fall-through (aux-only binop → EMIT_PAIR_FILL as-is, bb_binop_* template
  reads AUX); the g_gvar_flat_chain arith/relop arms (2212-2266) and the descr-slot arm (2281) all
  GUARD on `bb_child0(nd)` being non-NULL. v_binop is aux-only (sets aux, never operands/α — sole
  non-pascal producer, lower_sno 881/903 push onto PATTERN_ALT/CAT not binop), so EVERY v_binop
  binop currently takes the 2288 fall-through. CONFIRMED LIVE-SNOBOL BLAST RADIUS: `X = 3 + 4` m4
  fires the gvar-arith template — integer arith codegen flows through this exact region. THEREFORE
  the BINOP flip MUST (per the operands-emptiness LAW) re-express BOTH the 2288 fall-through AND the
  bb_child0-guarded arm guards on a REAL MARKER (v_binop already writes IR_LIT.dval=1.0 for relop /
  0.0 for arith and sval=op-name — a third marker or reusing these can encode "operands available")
  BEFORE pushing operands[]; then migrate the bb_binop_* template + interp 325/2616 off aux. This is
  a multi-file change touching live SNOBOL emit — NOT a one-commit flip. OPEN (pin next session with
  a focused --compile dump of `X=3+4`): the exact path by which gvar-arith fires today given
  bb_child0==NULL on a v_binop binop (re-kind elsewhere vs a populated sibling path) — resolve before
  the marker design so the re-expression covers the true firing site.
- ALT/DISJ arm-lists: interp 3009/4493, scrip 113/1012, emit 321/697 + bb_alt.cpp.
- APPLY/call-args: lower.c:103 + lower_prolog.c:115; consumers bb_call.cpp:94 + emit 366/388.
- single-child: lower.c:494.
- THEN DELETE bb_operand_aux_set/get + the operand_aux field/typedef (IR.h + scrip_ir.c).
- STILL PENDING LON RULINGS (unchanged): SCAN subject a (joint pattern-BB owner); raku_nfa_bb.c
  154/158 a-writers (missed cluster vs NFA exemption) — both cleaner to absorb at IRD-4 since
  their a/b writes change with the carrier type anyway.
Then IRD-4 (gamma/omega -> IR_ref_t, delete a/b, t->op; iref() carrier already exists; lower_sno
is AG-clean, should need zero touches) -> IRD-5 (sizeof fence + ARCH-IR.md).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
