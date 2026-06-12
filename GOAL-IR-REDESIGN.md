# GOAL-IR-REDESIGN.md — LOWER REWRITE (the `src/lower/lower_*.c` lowerers ARE src/lower)

**Owner repo:** SCRIP + this file. **Scope: ALL LANGUAGES** — five segregated per-language lowerers.

## WHAT THIS GOAL IS (Lon 2026-06-09)

The lower rewrite is the ONLY thing. **PROMOTION COMPLETE (Lon ruling 2026-06-11, SCRIP
`662f249`):** the five lowerers ARE `src/lower/lower_{icon,snobol4,raku,pascal,prolog}.c` — `nl/`
folded up, `_nl` dropped from files and symbols, ALL FIVE production-active, the OLD machinery
(`lower.c`, old `lower_raku.c`, `lower_internal.h`, `nl_on()`/`SCRIP_NL`, the old SNO/pascal/raku
arms in `lower_program.c`) DELETED. Each lowerer is segregated: only its `lower_<lang>{,_enum,
_proc,_clause,_labels}` entries are extern (nm-audited), all internals static, each with its own
local `lcx_t`. Remaining work = exec-channel maturation tails, NOT lowering structure.

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
  Never read or replicate the OLD lowering source. The SOLE spec is the GRAPH RESULT:
  `scrip --dump-bb FILE` (old = oracle) vs `--dump-bb2 FILE` (new). Compare graphs, fix the new
  lower to match. For dump-INVISIBLE execution channels the spec = the INTERP arms (the consumer)
  + empirical probe of old graphs via `SCRIP_DUMP_X=1`.

## METHOD + TOOLING (Lon 2026-06-08, graph-only)

- Five lowerers at `src/lower/lower_*.c`. `build()` helper (not `emit()`).
- `scrip --dump-bb2 FILE` routes AST through the new lowerer; `--dump-bb` = oracle.
- `scripts/scoreboard.sh LANG [--raw]` = yardstick. POST-PROMOTION = NL-vs-NL (vacuous except
  pascal stage2 frame-rewrite: 11 DIFFER). ORACLE-CRASH SKIP LIST (Lon ruling 2026-06-09):
  `cross.sno` @N cursor scan + 6 B07 Snocone compound-assigns.
- THE LOOP: oracle vs new → normalized diff (`ival≥7digits→PTR`) → fix FIRST divergence →
  `make scrip` → re-diff → COMMIT each green rung + guarded push. Never theorize past the bytes.

## CONVERSION MECHANISM (lower_program.c)

DELETED 2026-06-11 (`662f249`): no oracle to escape to. `lower_{icon,pascal,raku}_body` call
`lower_*_proc` unconditionally; LANG_SNO calls static `lower_sno` (pure-SNO only).

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
CONJ for the outermost block only).

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
3. **xcheck_sno_nl.sh `^\[lower\]` filter** — yardstick normalization, FLAGGED for Lon.

## LADDER — open steps only

### Phase 0 — HARNESS
- [ ] **LAD-0b** — pointer-ival ruling baked into scoreboard.sh (caveat 1).

### Phase 1 — ICON ✅ COMPLETE (9/9 DIFFER=0; CONVERTED)

### Phase 1b — ICON JCON-CANON EXEC TIGHTENING ⏸ ON HOLD (Lon 2026-06-11)
Authority: refs/jcon-master/tran/irgen.icn ir_a_*. Rung 1 landed `5a73b45`. Open steps:
- [ ] **ICX-0 NEWFAIL FIRST:** break/next inside a SEQ_EXPR generator cause infinite-loop (break_op,
  next_op). Fix loop_exit/loop_next context for the no-body every case before resuming.
- [ ] **ICX-1** fall-off-end of procedure body must FAIL (canon ir_Fail; flip lower_proc_body final stmt γ).
- [ ] **ICX-2** `e\n` lowers LIMIT FIRST: entry=limit, limit γ→expr entry, expr ω→limit resume.
- [ ] **ICX-3** break WITH expression: evaluate break-expr with loop continuations (γ→exit, ω→loop ω).
- [ ] **ICX-4** small canon set: (J) every-in-expression exhaustion→FAIL · (K) icn_call_allow_gen += bal/seq/key · (L) Sectionop val→left→right resume chain.
- [ ] **ICX-5** interp-arm canon deltas: IF resume re-evaluates cond entry leaf · WHILE exit re-runs cond chain · runtime !S/!T/key(T) skip DELETED elements · TT_CREATE co-expressions unsupported · MAKELIST isolated arg_blocks lose canon cross-arg backtracking.

### Phase 2 — PASCAL ✅ CONVERTED (scoreboard 104/11 post-promotion)
- [ ] **LAD-2d** — pcom chararr `__pas_strput` (Lon design awaited): `id[k]:=ch` hits arr_set_pure and builds an int-array instead of mutating a string. Needs `mk_assign` rewrite for pas_is_chararr bases + blank-string init decision (Lon design call). ppp also open.
- [ ] **DIFFER=11 triage** — `--dump-bb` leg includes stage2 frame-rewriting the `--dump-bb2` leg lacks; normalization-or-accept ruling needed.

### Phase 3 — SNOBOL4 + SNOCONE + REBUS ✅ COMPLETE + CONVERTED (2026-06-10)
- [ ] Snocone/Rebus conversion verify (share lower path; snocone smoke 2/5 pre-existing both legs).

### Phase 4 — PROLOG ✅ CONVERTED + OLD LOWERER DELETED (2026-06-11)

### Phase 5 — RAKU ✅ CONVERTED (2026-06-11, `87b62df`; promotion `662f249`)
- [ ] **EXEC-CHANNEL TAILS (queued behind Phase 6):** `list_bang_at` (IR_interp.c:2122) falls through
  to frame-string branch for push_pure arrays — iterates \x01-separated chars. Fix: detect DT_DATA
  before string fallthrough (line 2151) OR unify push_pure repr with DT_DATA "list" gen_type (line
  2123 already correct). Blocks 4 EMPTY-SAME programs (rk_for_array, rk_for_array_underscore,
  rk_map_grep_sort24, rk_reverse); MAP/GREP likely resolve with it. Target: 42+/0 MATCH/DIFFER.
- [ ] **Raku residue census:** 10 abort-kin (grammar×4, hashes×2, typed_vars, unless_until, class26);
  4 silent-clean (given, given18, re37, stdio39); top-level MAINLESS programs unsupported.

### Phase 6 — LOWER CONSOLIDATION ✅ COMPLETE (Rungs A+B+C, 2026-06-12)
wc -l final: common 267 · icon 457 · pascal 613 · prolog 529 · raku 377 · sno 1020 · lower.h 54 (=3317).

### Done-condition
Per-language bar set by Lon; CONVERSION = the terminal rung per language.

CURRENT (SCRIP `1df0cb5`, 2026-06-12): icon **7/2** · pascal **104/11** · snobol4 **152/0** ·
snocone **153/0** · prolog **7/0** · raku **38/0** · NEWFAIL=0 everywhere.

## OPEN FOR LON (consolidated)

(1) LAD-0b pointer-ival ruling — load-bearing (two invocations, fresh heaps); (4) beauty
self-beautify baseline (NL-only baseline needed); (5) m4 smokes need `make libscrip_rt` in fresh
containers; (6) `--dump-ast` segfaults on multi-proc pascal AND prolog; (7) NL lowerers not yet
200-char style-swept; (8) SCRIP_DUMP_X — keep or fold into LAD-0b; (12) HARNESS RETIREMENT ruling:
scoreboard.sh is NL-vs-NL (vacuous except pascal pipeline delta); xcheck_sno_nl.sh compares
identical legs — retire or repoint; (13) hygiene: `lower.h` retains dead old-icon decl block;
`src/tools/{prove_lower,tmatch_proto}.c` reference deleted symbols; (14) cross_lang polyglot revival.

## Watermark

**▶ HANDOFF (2026-06-12, Sonnet 4.6) — Phase 6 Rung C COMPLETE (canonical section ordering,
all five lower_<lang>.c). SCRIP `1df0cb5` (origin/main), .github THIS COMMIT. Gates held,
NEWFAIL=0. IMMEDIATE NEXT: Raku \x01 exec-channel tail (ICX queued behind Phase 6 closed).**

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
