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
  carry ZERO child α/β writes. IRD-3d COMPLETE (γ-chain STRUCT/
  BUILTIN arg lists, pair cluster + ir_pair_arg, g_catch) and
  IRD-3e-rest COMPLETE (icon LIST_BANG/EVERY/UNTIL/REPEAT +
  IR_PROC_GEN self-loops DELETED — zero-reader census) this
  session: commits 470cdd0 9134387 e7e1e22 415e465 28dad0b
  5334ead 3cedeea faa9b52. Remaining lowering-side α/β writes
  live ONLY in driver gz-synth + ring builders (bulk).
  REMAINING:
  (c) BULK: icn_ring_to_tree (driver/scrip.c 89/92) BINOP/
  UNOP arms still write α/β — its CALL arm CONVERTED to
  operands[0] at CHAIN-2 — plus the interp tree reads those ring
  shapes serve (BINOP ~2598 / UNOP ~2712 / SEQ ~2508 — icon/raku
  scope); SCAN subject α (gvar writer ONLY — SCAN operands hold
  IRD-3a type-punned subj/repl GRAPHS so the slot map is a
  pattern-BB joint ruling; op_a, bb_walk_rec and both chain
  writers carry the SCAN exemption);
  gz-synth (driver pl_gz_* writes α/β on synthesized CELL_UNIFY/
  DET_IS/DET_CMP/DET_WRITE/ARITH-copy nodes at ~598/617-23/
  652-3/673-7/683-4/693-5/701/882/917-8/944/952/961/1099 — emit
  marshal arms + bb_det_is.cpp + bb_is_cmp rhs-ARITH internals +
  bterm_arith all read that regime, already dual-read);
  flat_drive_gz_query γ-walks ~572-595 (synthesized DET chains);
  flat_drive_seq ~927 (raku/ring); emit_bb 2045 arm-list-via-ω;
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
  RESIDUE FLAGS (bulk scope): interp IF/WHILE/UNTIL/EVERY ->β
  then/body reads have ZERO writers in src (write census
  2026-06-07-D, re-verified -G at the 3e-rest flip) —
  verify-then-delete candidates, NOT chain-fed.
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

**OPEN — IRD-3d + IRD-3e COMPLETE (2026-06-07-G, Opus 4.8, Lon
attending): prolog lowering AND icon-scope single-child carries
fully on operands[]; PROC_GEN self-loops deleted.**
This session, SCRIP commits (each fully gated, all pushed):
470cdd0 γ-chain TEMPLATE consumers (9 files, strict count
asserts, bnth deleted); 9134387 γ-chain WRITER FLIP (STRUCT
228/253 MAKELIST cons-pairs, g_builtin 271) — REGRESSION CAUGHT
IN-COMMIT: pl_gz_rule_callee_body write arm (scrip.c ~697) was a
SECOND parallel gz write-arg reader whose guard names write by
sval/ival only (no α mention → α-keyed census missed it;
admission validates name+ival only so flipped bodies were
ADMITTED then builder deref'd NULL) — gdb bt diagnosis, fixed
via ir_call_arg(gg,0), post-fix residue audit banked; e7e1e22
PAIR consumers + NEW ir_pair_arg(nd,j) in contracts/IR.h
(operands-first else j?β:α) — flip-safety analysis: post-flip
guards over-admit γ-chain 2-arg names ONLY where in-body is_cmp
checks reject identically (519/686/953) or gz admission
name-filters; NO separate name-set gate needed; 415e465 PAIR
WRITER FLIP (178/193/208, A/B = exactly 6 BLTIN rows α+β→-1
together); 28dad0b g_catch FLIP (zero α readers — all consumers
read zc->catcher sidecar — but bare deletion forbidden:
bb_walk_rec reaches the catcher subgraph through the child carry,
d20c45e class; operands[0] preserves reachability); 5334ead
IRD-3e-rest ICON FOUR KINDS (LIST_BANG 181 / EVERY 346 / UNTIL
423 / REPEAT 436 → operands[0], REPEAT rp->γ=eα loop-back STAYS
— A/B-proven γ=4 both sides; v_while precedent mirror: cond push
only, β-body reads in those arms serve other producers and stay
VERBATIM; writers+consumers one commit justified by
single-consumer-per-kind dual-read); 3cedeea bb_term_io format
a1 hybrid (a0->γ → ir_call_arg(pBB,1) ×2) + INHERITED-RED TRIAGE:
BB-FIXUP b8e3a04's format/2-compound m3/m4 failure is
worktree-PROVEN PRE-EXISTING at 6e3cb1e~1 — fence-era admission
gap, NOT an IRD-3d interaction; faa9b52 PROC_GEN self-loops
DELETED (zero-reader census; bb_walk_rec revisit-guard verified;
operands-push rejected as arity/dump pollution; A/B EMPTY —
runtime-synthesized graphs never in static prove corpus).
GATES per commit: 5 sweeps (sno 153/icn 9/pl 8/pas 5/sco 191)
byte-identical vs pristine /tmp/base_pre; 5 smokes clean;
prove_lower PASS=68; pl smoke m2 5/5 HARD m3 3/2 m4 3/2; icon
m2 12/12 HARD m3 10/2 m4 10/2; git-stash masked-ival A/B dump
diff per writer flip showing EXACTLY the flipped kind's columns.
RACES ABSORBED ×3 (BB-FIXUP b8e3a04 bb_term_io regen
re-certified on my raced heads, their PUSH-RACE ABSORPTION note;
27c797f pattern_match stub text — libscrip_rt rebuilt; b7a2717
B0 AST-evaluator deletion) — each rebase followed by merged-tree
rebuild + smoke re-verify; LAW: a clean rebase is NOT a gate,
re-verify the merged head.
LAWS RECORDED THIS SESSION: (4) freestanding RELATIVE γ-hops on
fetched arg locals (a1 = a0->γ) escape α-keyed censuses — grep
'->γ' per kind at every flip (bb_term_io 141/155). (5) guards
naming kinds by sval/ival without α/β mention hide parallel
readers — grep by BUILTIN NAME too (9134387). (6) prove_lower
LVAR/ITE/GCONJ rows carry pointer-punned ivals — mask column 7
before structural diff. (7) sno 100_roman_numeral.sno is a
7.7-7.9s/8s timeout-boundary flake under load — idle re-run
adjudicates.
NEXT (goal order):
1. Bulk stage (c) — START WITH ring BINOP/UNOP (scrip.c 89/92 +
interp tree reads ~2508/2598/2712), then gz-synth regime, SCAN
ruling (pattern-BB joint), flat_drive_gz_query γ-walks,
operand_aux sub-cluster (LOAD-BEARING — see census above) LAST.
2. IRD-4 → 3. IRD-5 (incl. prove_lower ops column + CATCH kname
+ sno sweep timeout bump).
HANDOFF 2026-06-07-G CLOSED (Opus 4.8): SCRIP origin = faa9b52,
.github origin = this commit; both trees CLEAN, all pushed. See
HANDOFF-2026-06-07-OPUS48-IR-REDESIGN-IRD-3D-3E-COMPLETE.md.
Next session: clone/pull BOTH repos (authenticate origin with
Lon's token: git remote set-url origin
https://TOKEN@github.com/snobol4ever/<repo>), git identity
LCherryholmes/lcherryh@yahoo.com per repo, apt-get install -y
libgc-dev; make; make libscrip_rt (MANDATORY for m4), bake
scripts/bake_ird3_baseline.sh /tmp/base_pre FOREGROUND BEFORE
touching code, then bulk stage (c) per NEXT. Concurrent
sessions: BB-FIXUP (owns BB_templates + BB-REVAMP-TRACKER.md,
rebase before touching bb_*.cpp, answer tracker notes in commit
messages not their tracker), B0 (runtime/AST purges), and
pattern-BB design (joint owner of the SCAN-subject ruling).
ALWAYS git pull --rebase both repos before working.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
