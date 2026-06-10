# GOAL-IR-REDESIGN.md — LOWER REWRITE (the `src/lower/nl/` lowerers ARE the goal)

**Owner repo:** SCRIP + this file. **Scope: ALL LANGUAGES** — five segregated per-language lowerers.

## WHAT THIS GOAL IS (Lon 2026-06-09)

The lower rewrite is the ONLY thing. The five new lowerers at `src/lower/nl/lower_*_nl.c` ARE the
goal. The old-`IR_t`-struct work is DONE and REMOVED from this file — git history preserves every
rung. **CONVERTED (production default = NL): ICON, PASCAL, SNOBOL4.** Raku + Prolog stay OLD until
their lowerers mature. Per-language defaults flip ONLY on execution-parity evidence, never on dump
MATCH alone.

## TARGET NODE SHAPE — what the lowerers build

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
    int        idx;         /* sidecar key — lit[]/exec[] parallel arrays */
    IR_graph_t * own;       /* owning graph — resolves idx for IR_LIT/IR_EXEC */
};
```

Box = operator + two outbound port wires + operand list. NOTHING else. A box's α/β are not
fields — they are this node at "α"/"β" in someone's `IR_ref_t`. Result value: NOT in `IR_t`.
Literal payload (sval/ival/dval): SIDECAR. Runtime state: SIDECAR or per-activation. Use literal
"α" "β" strings in code, never named constants.

## THE FOUR-ATTRIBUTE GRAMMAR — lower guide

JCON `ir_OpFunction(coord, lhs, fn, argList, failLabel)` maps: fn→op, failLabel→ω, success→γ,
lhs→IMPLICIT (box's own result), argList→operands. **γ/ω are INHERITED** (passed down by parent);
**α/β are SYNTHESIZED** (the node's own blocks). So `lower(cx, t, γ, ω) -> IR_t*` IS the
four-attribute grammar. The live interp (`interp/IR_interp.c`) is a goal-directed γ/ω-FOLLOWER,
NOT a tree-walker. The new lower must REPRODUCE the OLD graph's goal-directed shape.

## DO NOT

- **LOWER REBUILD — DO NOT LOOK AT / TRANSCRIBE THE OLD LOWER (Lon ruling 2026-06-08).**
  Never read or replicate the OLD lowering source (`lower.c`, `lower_program.c`, `lower_icon.c`†,
  `lower_snobol4.c`, `lower_raku.c`, `lower_pascal.c`, `lower_prolog.c`). The SOLE spec is the
  GRAPH RESULT: `scrip --dump-bb FILE` (old = oracle) vs `--dump-bb2 FILE` (new). Compare graphs,
  fix the new lower to match. For dump-INVISIBLE execution channels the spec = the INTERP arms
  (the consumer) + empirical probe of old graphs via `SCRIP_DUMP_X=1`.
  († lower_icon.c already DELETED `3546ea2`; lower_snobol4.c deletion = Lon's SNOBOL4 session.)

## METHOD + TOOLING (Lon 2026-06-08, graph-only)

- Five lowerers at `src/lower/nl/lower_*_nl.c`, compiled INTO `scrip` beside the OLD ones (both
  symbol sets coexist; `_nl` suffix avoids basename collision; in the Makefile explicit recipe
  ~540 + prereqs ~238). `emit()` helper is named `build()` (emit is reserved for emitters).
- `scrip --dump-bb2 FILE` routes the parsed AST through the new lowerer; `--dump-bb` = oracle.
- `scripts/scoreboard.sh LANG [--raw]` = the yardstick: MATCH/DIFFER/NEWFAIL/SKIP per suite
  (langs: icon snobol4 snocone prolog pascal raku). Oracle leg pinned `SCRIP_NL=0`. Has the
  ORACLE-CRASH SKIP LIST (Lon ruling 2026-06-09): 7 programs where the OLD lower segfaults
  mid-dump (`cross.sno` @N cursor scan + 6 B07 Snocone compound-assigns) — parked OLD-lower bugs.
- THE LOOP: oracle vs new → normalized diff (`ival≥7digits→PTR`) → fix FIRST divergence →
  `make scrip` → re-diff → COMMIT each green rung + guarded push. Never theorize past the bytes.
- DISPATCH = flat `switch (t->t)` top level; within a case, ordered tree-pattern matches (the
  SNOBOL4-pattern analogue), lightweight hand-rolled `pmatch` style — no inline field-poke
  `if/else` chains. (NOTE: the working Icon/Pascal lowerers use plain switch + inline tests; the
  gauntlet design is aspirational vs the working reference style.)

## CONVERSION MECHANISM (lower_program.c)

`nl_on(dflt)` reads `SCRIP_NL` (env overrides compiled per-language defaults); `SCRIP_NL=0` is the
full oracle escape hatch. Gate sites: `lower_icon_body` / `lower_pascal_body` (nl_on(1)) /
LANG_SNO `lower_sno_nl` (nl_on(1), pure-SNO only); `pas_rewrite_graph` is OLD-PATH-ONLY. Flip a
default ONLY at full execution parity: dump sweep + m2 cross-check old-vs-new + smoke gates at
baseline (sno: `scripts/xcheck_sno_nl.sh`).

## NODE-EXACT CONVENTIONS — the live spec (byte-verified vs `--dump-bb`)

### Value layer
- **Leaves** chained via `γ`. **Statements REVERSE-threaded:** alloc `IR_SUCCEED`@0 / `IR_FAIL`@1
  first, then stmts in reverse source order so entry = first-executed (highest index).
- **BINOP:** `ival=BinopKind`; operands ride the value-ring (NO `ops:[]`); chained LEFT→RIGHT;
  entry=left. **UNOP:** `ival=(tree_e)t->t`; operand chained.
- **CALL arg model:** ONLY `write`/`writes` CHAIN args via the value-ring (visible). EVERY other
  call SUB-GRAPHS its args (invisible; entry = the call node).
- **subscript** `a[i]` → CALL `[]` `ival=n`. **list** → CALL `MAKELIST` `ival=count`.
- **ASSIGN** simple-var-LHS = `sval`=name + EXACTLY ONE operand (rhs result), goal-directed.
- **AUGOP** decomposes to ASSIGN+BINOP. **RETURN:** contextual passed `γ`/`ω` (NOT forced PSUCC).
- **MULTI-PROC:** `collect_procs` DFS; `--dump-bb2` iterates procs in source order emitting
  `; proc <name>` + `bb_print`.

### Control flow
- **CONJ** = multi-statement braced block in expression context. Single-statement blocks get NO
  CONJ. NOT the loop back-edge.
- **Failure-ω rule:** each stmt's RESULT `ω` → nearest PRECEDING resumable stmt's result, else
  enclosing `ω`. Icon resumable = IF/SCAN/EVERY/TO/TO_BY/ALTERNATE/REPEAT/WHILE/UNTIL. PASCAL
  resumable = IF/UNLESS ONLY — loops EXHAUST on normal exit.
- **WHILE:** body γ AND ω loop to condition-entry; WHILE node = loop EXIT (reached via cond-fail
  `ω`); entry = condition entry; `ops:[cond-entry]`. No fabricated CONJ.
- **IF:** condition INLINED as the if-entry; IF node = resume anchor; `ops:[cond-entry]`.

### Generators (Icon)
- **EVERY/TO:** `TO`/`TO_BY` `sval="ag"`, `ops:[lo,hi]`, entry=lo; TO_BY drops the by-expression
  from the dump. `EVERY` `γ=ω=`next-stmt, `ops:[gen-entry]`. Body loop-back = the generator node
  IF body is_resumable, ELSE the EVERY node.
- **IDX_SET:** `lhs[idx]:=val` → operands `[base, index.., value]`, each operand `γ`→IDX_SET,
  entry = base.

### Pascal
Per-proc graph, no PROG wrapper; γ→α, ω→β (proper split — NOT icon α-uniform). CALL `sval`=callee,
`ival`=nargs, args INVISIBLE; `writeln`→`__pas_writeln` w/ trailing ILIT −1. ASSIGN sval=LHS, RHS
on γ-ring. VAR_FRAME `ival` = SLOT in the DECLARING proc; own vars frame ONLY when nesting
(outer || byref || has_children); childless-proc locals = plain VAR. Bool-chain `__pbtN`
materialization; case fully parser-desugared; statement-position nested TT_SEQ_EXPR FLATTENS (one
CONJ for the outermost block only). Remaining oddity log lives in git history of this file.

### SNOBOL4 (sweep COMPLETE — kept as cross-language reference)
ω port sz=α (α-UNIFORM like icon). Labels: one SUCCEED per stmt; gotos wire γ/ω via `resolve()`
(END→PSUCC, RETURN/NRETURN→PRET, FRETURN→PFRET). NULL-body label chain: honors go_u UNLESS target
is IR_RETURN; if the body ALLOCATED orphan nodes before bailing, chains nxt regardless. ORPHAN
family (γ=· ω=·, label chains nxt): IDX/INDIRECT/VLIST/DEFER value-RHS → bare ASSIGN; SEQ-concat
containing IDX → ASSIGN_CONCAT+bare SEQ; binop containing IDX → edgeless ASSIGN+BINOP(ival)+left
VAR(ω only); capture value-RHS → bare ASSIGN; FNC w/ IDX/INDIRECT/OPSYN arg → bare CALL; pattern
shaped TT_ASSIGN/TT_OPSYN or containing user FNC → bare SCAN. LIVE pattern-value assigns:
all-QLIT ALT → DTP_ASSIGN+PATTERN_LIT×n+PATTERN_ALT chain; single primitive w/ QLIT arg
(SPAN/ANY/NOTANY/BREAK/BREAKX → sval) or ILIT arg (LEN/POS/RPOS/TAB/RTAB → ival) →
DTP_ASSIGN+PATTERN_*; 2-arm ALT of clean SEQs → ASSIGN+ALT+SEQ(arm2)+SEQ(arm1) w/ arg-block ptrs,
arm1.ω→arm2.β. Pattern sub-graphs: SCAN `EXEC.counter`=pat graph, `operands[0]`=subject graph,
`operands[1]`=replacement graph (ival=1); top-level concat (succ==SUCCEED@0) takes the PAT_CAT
path like captures; backtrack-ω targets = is_pat_consumer family (LEN TAB RTAB REM BREAK BREAKX
SPAN ANY NOTANY LIT ARB ARBNO), PAT_DEFER = its own retry target, capture ω → inner operand.

### EXECUTION CHANNELS (dump-invisible; spec = interp arms + SCRIP_DUMP_X probe)
`bb_print` prints NEITHER `IR_LIT.dval`, `IR_EXEC.counter`, nor `operand_aux` — dump MATCH alone
never licenses a flip. CALL `dval` taxonomy: 1.0 write/writes ring-chained; 2.0 synthetic ops +
SNOBOL name-save; 3.0 other named calls; 5.0 DEFINE. Arg blocks = `IR_graph_t **` in
`IR_EXEC(call).counter`, each FAIL@0 + ring-chained expr, result γ=NULL. BINOP carries
`operand_aux=[lres,rres]` (RETURN re-interprets; aux must be RESULT nodes, not entry leaves).
GEN_SCAN: dval=1.0, subject→counter, body→ival. SNO: IR_SEQ concat dval=1.0 ctr=LEFT argblk
ival=RIGHT argblk; PAT_ARBNO ctr=bb_arbno_state_t*; positional dvals POS(var)=2.0 RPOS(var)=1.0
LEN(var)=1.0 TAB(var)=2.0 RTAB(var)=1.0; RETURN dval=1.0 / FRETURN 2.0. **GC HAZARD:** proc_table
+ exec[] sidecars are plain-realloc/calloc — Boehm never scans them; store ONLY plain
strdup/calloc there, NEVER lp_strdup/GC_MALLOC.

## STANDING CAVEATS — open / need Lon's ruling

1. **Pointer-`ival` normalization (LAD-0b).** `ival≥7digits→PTR` sed is load-bearing (icon −2
   matches under `--raw`). Needs Lon's ruling, then bake into `scoreboard.sh` as a named flag.
2. **Execution validation.** RESOLVED for ICON+PASCAL+SNOBOL4 by their CONVERSIONS.
   snocone/raku/prolog MATCHes remain dump-only until converted.
3. **xcheck_sno_nl.sh `^\[lower\]` filter** (old lower NARRATES its punts, NL punts silently;
   program bytes identical) — yardstick normalization, FLAGGED for Lon like the PTR sed.

## LADDER — per-language gauntlet, gate each rung

Arc per language: (a) value layer + multi-proc structure, (b) control flow, (c) generators/
backtracking, (d) the deep construct. Commit per green program.

### Phase 0 — HARNESS
- [ ] **LAD-0b** — pointer-ival ruling baked into scoreboard.sh (caveat 1).

### Phase 1 — ICON (6/8; CONVERTED)
- [ ] **LAD-1a — queens.** scope=global IR_VAR annotation + generator procedures. NOTE queens is
  broken on the OLD engine too (0 solutions) — predates conversion. GATE: MATCH, 6→7.
- [ ] **LAD-1b — generators.icn.** suspend / generator caching / IR_PROC_GEN — deepest Icon
  construct. GATE: 8/8.

### Phase 2 — PASCAL (89/93; CONVERTED, m2 parity SAME=91 DIFF=0)
- [ ] **LAD-2d — heavy tails:** pcom, ppp (old path reachable via SCRIP_NL=0).

### Phase 3 — SNOBOL4 + SNOCONE + REBUS ✅ COMPLETE + CONVERTED (2026-06-10)
sno153 **152/153 MATCH DIFFER=0** (1 SKIP=cross oracle-segfault) · sco191 **142/142** ·
m2 exec cross-check **SAME=153 DIFF=0** · default flipped `b11a963`.
- [ ] **Old `lower_snobol4.c` deletion** — Lon's SNOBOL4 session (mirror icon `3546ea2`).
- [ ] Snocone/Rebus conversion verify (share lower path; snocone smoke 2/5 pre-existing both legs).

### Phase 4 — PROLOG (7/7 dump COMPLETE 2026-06-10; OLD default — conversion pending)
Dump sweep DONE (LAD-4a/4b/4c collapsed into one session): 7/7 MATCH DIFFER=0 NEWFAIL=0 (1 SKIP =
coverage_pl_nodes, pre-existing). The dump spec is MAIN's clause-body graph ONLY (oracle never dumps
other predicates), so the dump bar is shallow for prolog — conversion is the real ladder.
- [ ] **LAD-4d — CONVERSION.** m2 exec cross-check old-vs-new; clause graphs for ALL predicates +
  exec channels (GOAL/GCONJ/findall arg blocks are placeholder calloc PTRs today — spec = interp
  arms + SCRIP_DUMP_X). Default stays OLD until execution parity.

### Phase 5 — RAKU (1/29; OLD default; unparked 2026-06-10)
Value-ring model pinned at `0ecd99c`: lower_raku_enum/proc, opcodes +0 −1 *2 /3 %4 relops 5-10
~=11, say/print→write/print, CALL alloc'd BEFORE its arg.
- [ ] **MULTI-SUB ORACLE DEGENERACY — NEEDS LON RULING.** Oracle collapses multi-sub programs to
  ONE graph (shared-node-array artifact). Matchable set = ~17 single-sub programs. Rule needed
  like the oracle-crash SKIP list.
- [ ] **Next constructs** for ~16 single-sub DIFFERs: `my $x=expr`, for/while, string interp,
  junctions, regex. rk_join oracle ival QUIRK — likely unmatchable, defer.

### Done-condition
Per-language bar set by Lon; CONVERSION = the terminal rung per language.

CURRENT (SCRIP `cb127cb`, 2026-06-10, normalize=1): icon **9/9 DIFFER=0 CONVERTED** (suite grew;
queens+generators now MATCH — LAD-1a/1b dump bar appears met, verify before closing) · pascal
**CONVERTED, scoreboard UNSCOREABLE in fresh container** (OLD oracle leg aborts silently → 102
SKIP; see OPEN 9) · snobol4 **152/153 DIFFER=0 CONVERTED** · snocone **142/142** · prolog
**7/7 dump COMPLETE, OLD default** · raku **1/29** · NEWFAIL=0 everywhere.

## OPEN FOR LON (consolidated)

(1) LAD-0b pointer-ival ruling; (2) xcheck `^\[lower\]` filter ruling (caveat 3); (3) raku
multi-sub degeneracy ruling; (4) OLD leg segfaults on beauty self-beautify from the beauty dir
(NL leg runs; blocks old-vs-new beauty baseline); (5) sno smoke m4 + icon m4 need
`make libscrip_rt` in fresh containers (artifact, not code); (6) `--dump-ast` segfaults on all
multi-proc pascal (AST-printer bug); (7) NL lowerers not yet 200-char style-swept;
(8) SCRIP_DUMP_X extended dump — keep or fold into LAD-0b; (9) pascal OLD-leg `--dump-bb`
ABORTS silently (no output) on every corpus .pas in a fresh container while the NL leg runs —
scoreboard pascal = 102 SKIP, UNSCOREABLE; verified pre-existing at `984cd27` baseline (likely kin
of open items 4/5).

## Watermark

**▶ SESSION (2026-06-10, Fable 5, in progress) — PROLOG DUMP SWEEP COMPLETE 0→7/7.**
Goal-directed rewrite of `src/lower/nl/lower_prolog_nl.c` landed in 2 pushed rungs (SCRIP `984cd27`
→ `cb127cb`, HEAD==origin/main): MAIN clause-body graph = SUCCEED@0/FAIL@1/GCONJ@2(ival=argblk PTR),
goals REVERSE-allocated (entry=first source goal, each node before its args), BUILTIN
(write/nl/format/aggregate_all: visible ops + ival=nargs; findall: ival=PTR, goal arg
dump-invisible) vs GOAL (user pred + once/forall/member, sval=name ival=argblk PTR, args reified
after but NOT in ops), `=`/2→UNIFY (visible ops, non-resumable), failure-ω → nearest PRECEDING
IR_GOAL's β else base, terms reified (ATOM/LIT_I/LIT_F/LOGICVAR ival=AST slot, STRUCT node-first
args-in-order ival=arity, MAKELIST desugar tail-first `.`/2 cells, n-ary `,`/`;` re-nested binary
in term position), disjunction goal = DISJ anchor + branches LAST-FIRST (atom→SUCCEED/FAIL node,
conj→GCONJ wrapper) ω-chained branch→next-branch→base, construct entry = first branch's first goal;
frontend emits BINARY right-nested `,`-chains inside `;` (n-ary only at clause top) — collect_conj
flattens both. Gates held every rung: sno 152/153, icon 9/9, NEWFAIL=0. FLAGS: pascal scoreboard
UNSCOREABLE (OPEN 9); icon suite now 9/9 incl. queens/generators (LAD-1a/1b verify). NEXT: LAD-4d
prolog conversion (exec channels + all-predicate graphs) · raku single-sub (pending ruling).**

**▶ HANDOFF (2026-06-10, Fable 5, Lon "perform hand off") — SNOBOL4 SWEEP COMPLETE + CONVERTED.
sno153 dump 148→152/153 MATCH, DIFFER 4→0 (1 SKIP=cross oracle-segfault); m2 exec cross-check
SAME=153 DIFF=0 SKIP=0; production default FLIPPED to lower_sno_nl per Lon's ruling. SHAs: SCRIP
`b11a963` (HEAD==origin/main, build GREEN rc=0, tree clean), .github THIS COMMIT. Five guarded-push
rungs; snocone 142/142 + scoreboards held every rung; NEWFAIL=0 throughout.**

  **RUNGS:** `99aa151` 1016_eval (TT_DEFER value-assign → orphan ASSIGN) · `c6735f6` expr_eval
  (NULL-body label honors go_u UNLESS target IR_RETURN — blanket always-nxt regressed 41 programs,
  reverted+refined; NRETURN→PRET; pattern-value-assign shapes: general 2-arm ALT live/orphan,
  single-primitive DTP_ASSIGN, capture-RHS orphan; PAT_DEFER backtrack + non-builtin-VAR spine
  detection) · `c49c28a` roman (IDX-in-concat orphan; partial-orphan binop w/ left-VAR ω-only;
  label rule refined again: orphan-ALLOCATING NULL body chains nxt, wholly-punted honors go_u —
  n_before node-count probe) · `ec51d29` coverage → DIFFER=0 (TT_ASSIGN/TT_OPSYN pattern → orphan
  SCAN; ILIT-arg primitive family; top-level concat PAT_CAT path; is_pat_consumer += ARB, ARBNO) ·
  `adc93cc`→`b11a963` THE FLIP (nl_on(1) at the LANG_SNO site).

  **KEY FINDING — the dump fixes WERE the exec fixes:** the concurrent conversion workstream
  (`f617d67`/`78124a5`) had parked 4 m2 exec DIFFs (ARBNO cluster + test_case); this session's
  backtrack-ω/PAT_CAT dump corrections closed all 4 without touching execution code — graph shape
  was the bug. xcheck went 149→153 SAME purely from dump-parity work.

  **FLIP EVIDENCE (the conversion bar):** dump sweep DIFFER=0 NEWFAIL=0; m2 cross-check SAME=153
  DIFF=0; smoke at baseline both legs: sno m4 7/7 HARD, icon m3 10/12 m4 10/12 (same 2
  pre-existing), prolog m3+m4 5/5, snocone 2/5 pre-existing; snocone scoreboard 142/142 held.
  SCRIP_NL=0 = oracle escape hatch; harness legs env-pinned so yardsticks unchanged.

  **NEXT:** old `lower_snobol4.c` deletion (Lon's SNOBOL4 session) · prolog LAD-4a (hello.pl
  cheapest) · raku single-sub constructs (pending multi-sub ruling) · icon queens/generators.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
