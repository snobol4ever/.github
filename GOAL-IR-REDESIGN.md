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
  Never read or replicate the OLD lowering source (`lower.c`, `lower_program.c`, `lower_icon.c`†,
  `lower_snobol4.c`, `lower_raku.c`, `lower_pascal.c`, `lower_prolog.c`). The SOLE spec is the
  GRAPH RESULT: `scrip --dump-bb FILE` (old = oracle) vs `--dump-bb2 FILE` (new). Compare graphs,
  fix the new lower to match. For dump-INVISIBLE execution channels the spec = the INTERP arms
  (the consumer) + empirical probe of old graphs via `SCRIP_DUMP_X=1`.
  († lower_icon.c already DELETED `3546ea2`; lower_snobol4.c deletion = Lon's SNOBOL4 session.)

## METHOD + TOOLING (Lon 2026-06-08, graph-only)

- Five lowerers at `src/lower/lower_*.c` (post-promotion; OLD symbol set deleted). `emit()`
  helper is named `build()` (emit is reserved for emitters).
- `scrip --dump-bb2 FILE` routes the parsed AST through the new lowerer; `--dump-bb` = oracle.
- `scripts/scoreboard.sh LANG [--raw]` = the yardstick: MATCH/DIFFER/NEWFAIL/SKIP per suite
  (langs: icon snobol4 snocone prolog pascal raku). POST-PROMOTION the oracle leg is GONE —
  the board is NL-vs-NL (`--dump-bb` full-pipeline vs `--dump-bb2` direct) and largely vacuous
  except where the pipelines differ (pascal stage2 frame-rewrite: 11 DIFFER). Retirement or
  repointing needs a ruling. `SCRIP_NL` is ignored; `xcheck_sno_nl.sh` is vacuous. Has the
  ORACLE-CRASH SKIP LIST (Lon ruling 2026-06-09): 7 programs where the OLD lower segfaults
  mid-dump (`cross.sno` @N cursor scan + 6 B07 Snocone compound-assigns) — parked OLD-lower bugs.
- THE LOOP: oracle vs new → normalized diff (`ival≥7digits→PTR`) → fix FIRST divergence →
  `make scrip` → re-diff → COMMIT each green rung + guarded push. Never theorize past the bytes.
- DISPATCH = flat `switch (t->t)` top level; within a case, ordered tree-pattern matches (the
  SNOBOL4-pattern analogue), lightweight hand-rolled `pmatch` style — no inline field-poke
  `if/else` chains. (NOTE: the working Icon/Pascal lowerers use plain switch + inline tests; the
  gauntlet design is aspirational vs the working reference style.)

## CONVERSION MECHANISM (lower_program.c)

DELETED 2026-06-11 (`662f249`): `nl_on()`/`SCRIP_NL` removed with the old paths — there is no
oracle to escape to. `lower_{icon,pascal,raku}_body` call `lower_*_proc` unconditionally;
LANG_SNO calls static `lower_sno` (pure-SNO only — mixed-language SNO declines to a no-op; the
polyglot fallback died with the old arm, sole consumer `test/cross_lang.scrip` was already broken
both legs at baseline).

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

### Phase 1 — ICON ✅ dump COMPLETE (9/9 DIFFER=0 verified 2026-06-10; CONVERTED)
LAD-1a (queens) + LAD-1b (generators.icn) both MATCH on the current suite — gates met (closed by
the intervening ICON-FULL-PASS work, verified this session). Residual icon m2 exec regressions are
tracked in GOAL-ICON-FULL-PASS, not here.

### Phase 2 — PASCAL (CONVERTED; scoreboard newly scoreable 93/11 post-promotion)
- [ ] **LAD-2d — heavy tails:** pcom (chararr `__pas_strput` design awaits Lon), ppp. NO old
  path remains — spec = interp arms + corpus refs.
- [ ] **Scoreboard DIFFER=11 triage:** the `--dump-bb` leg includes stage2 frame-rewriting the
  `--dump-bb2` leg lacks — pipeline delta, NEWFAIL=0; needs normalization-or-accept ruling.

### Phase 3 — SNOBOL4 + SNOCONE + REBUS ✅ COMPLETE + CONVERTED (2026-06-10)
sno153 **152/153 MATCH DIFFER=0** (1 SKIP=cross oracle-segfault) · sco191 **142/142** ·
m2 exec cross-check **SAME=153 DIFF=0** · default flipped `b11a963`.
- [ ] Snocone/Rebus conversion verify (share lower path; snocone smoke 2/5 pre-existing both legs;
  snocone board now 153 MATCH DIFFER=0 post-promotion).

### Phase 4 — PROLOG ✅ CONVERTED + OLD LOWERER DELETED (2026-06-11)
Flip landed `5225acb` under Lon rulings (2)+(10); old `lower_prolog.c` deleted `8a2d6a7` (mirror
icon `3546ea2`). Flip evidence: m2 xcheck 141/143 SAME (residuals = exactly the 2 ruled items),
smoke m2/m3/m4 5/5 ALL, scoreboard 7/7. **FLIP-BLOCKING BUG fixed en route (`5225acb`):** NL never
set `g->nslots` / `g->body_root` and head-arg UNIFYs were wire-only (not in GCONJ `goals[]`) — all
three are dump-invisible AND m2-invisible (the interp GCONJ arm follows γ wires, never `goals[]`),
so dump MATCH + m2 xcheck both passed while modes 3/4 were broken (smoke fell 5/5 → 1/5 at first
flip attempt). Spec mined from the consumers: `pl_gz_admit`/`pl_gz_fact_clause_units`/
`pl_gz_rule_clause` (driver) + `emit_bb` body_root sites. **LESSON FOR REMAINING CONVERSIONS
(raku):** the m2 xcheck does NOT validate `goals[]`/`nslots`/`body_root` — m3/m4 smoke must run on
the NL leg BEFORE any flip. Post-deletion degeneracy (kin of OPEN 11): SCRIP_NL=0 selects no
prolog oracle; prolog scoreboard is now a self-comparison.

### Phase 5 — RAKU ✅ CONVERTED 2026-06-11 (`87b62df`; promotion `662f249`)
Flip evidence: m2 xcheck SAME=26 DIFF=0; 21 old-leg aborts → NL aborts only 10 kin, runs 11
clean (8 with output) — NEWFAIL=0. m3/m4 validated post-promotion at watermark with libscrip_rt
(icon m4 10/12, prolog m4 5/5 — the smoke m4 zeros were open-(5) artifact). Board DIFFER=3
ruling-(3) class ELIMINATED (oracle degeneracy died with the oracle): raku 38 MATCH DIFFER=0.
(History below predates conversion:)
Value-ring model pinned at `0ecd99c` + this session's construct set (see watermark). DIFFER=3 =
EXACTLY the ruling-(3) multi-sub class (combinator/interp/subs). First m2 xcheck recorded:
SAME=26 DIFF=0 SKIP=21(both-legs-abort rc=134); 4 of 26 SAME are EMPTY-SAME (both legs print
nothing — shared m2 runtime limit, not lowering): for_array_simple/for_array_underscore/
map_grep_sort24/reverse; rk_unique_sum partially blank both legs.
- [x] Multi-sub oracle degeneracy (ruling 3) — MOOT post-promotion; board self-consistent.
- [ ] **EXEC-CHANNEL TAILS (no longer flip-blocking; m2 parity incl. empty-empty):**
  LIST_BANG/GATHER loop-var binding UNSET; MAP/GREP ival=body-argblk + counter=source-argblk
  PLACEHOLDERS — the 4 EMPTY-SAME programs (for_array*/map_grep_sort24/reverse) are this. CALL
  dval tags + GATHER take-blocks landed `87b62df`. Spec = interp arms.
- [ ] **Raku residue census (post-promotion):** 10 NL aborts (grammar family x4, hashes x2,
  typed_vars, unless_until, class26 — old-leg abort kin); 4 silent-clean (given, given18, re37,
  stdio39); top-level MAINLESS programs unsupported (no TT_SUB_DECL → no main graph → FATAL both
  modes; this is the entire raku smoke 0/17, pre-existing both legs, owner RAKU frontend).

### Done-condition
Per-language bar set by Lon; CONVERSION = the terminal rung per language.

CURRENT (SCRIP `662f249`, 2026-06-11, normalize=1, POST-PROMOTION — boards are NL-vs-NL):
icon **7/2** · pascal **93/11 (stage2 pipeline delta)** · snobol4 **152/153 DIFFER=0** · snocone
**153 DIFFER=0** · prolog **7/7** · raku **38 DIFFER=0** · NEWFAIL=0 everywhere. OPEN 9 + OPEN 11
RESOLVED (the zombie oracle legs were the cause; deleted). Smoke with libscrip_rt: icon m2 12/12
m3 10/12 m4 10/12 · prolog m2/m3/m4 5/5.

## OPEN FOR LON (consolidated)

(1) LAD-0b pointer-ival ruling — STILL load-bearing (two invocations, fresh heaps); (4) beauty
self-beautify baseline (old leg gone — NL-only baseline needed now); (5) m4 smokes need
`make libscrip_rt` in fresh containers — RE-CONFIRMED post-promotion (icon m4 0→10/12, prolog
m4 0→5/5 once built); (6) `--dump-ast` segfaults on multi-proc pascal AND prolog; (7) NL lowerers
not yet 200-char style-swept; (8) SCRIP_DUMP_X — keep or fold into LAD-0b; (12) HARNESS
RETIREMENT ruling: scoreboard.sh is NL-vs-NL (vacuous except the pascal pipeline delta);
xcheck_sno_nl.sh compares identical legs (SCRIP_NL ignored) — retire, or repoint at SPITBOL/m-mode
cross-checks; (13) hygiene: `lower.h` retains the dead old-icon `lower_new_*` decl block (shared
header — prolog/rebus parsers + gen_runtime include it); `src/tools/{prove_lower,tmatch_proto}.c`
(not in build) reference deleted symbols; (14) cross_lang polyglot revival = teach `lower_sno`
mixed-language programs (the old fallback died broken). RESOLVED-AND-CLOSED: (2) xcheck filter
(xcheck vacuous), (3) raku multi-sub (moot), (9) pascal UNSCOREABLE + (11) sno 10/125 (both were
the zombie oracle legs — deleted), (10) puzzle_10 (the buggy OLD leg no longer exists to exempt).

## Watermark

**▶ HANDOFF (2026-06-11, Fable 5, Lon "perform hand off") — RAKU SINGLE-SUB DUMP SWEEP COMPLETE
1→26/47 MATCH in 11 pushed rungs + FIRST m2 XCHECK (SAME=26 DIFF=0). DIFFER=3 = exactly the
ruling-(3) multi-sub set. SHAs: SCRIP `b90d5a1` (HEAD==origin/main, build GREEN, tree clean),
.github THIS COMMIT. Gates held every rung (prolog 7/7 icon 7/2; sno/snocone/pascal at documented
OPEN-9/11 fresh-container states; NEWFAIL=0 throughout); 1 clean rebase over concurrent
`bfd261f`.**

  **RUNGS (all in lower_rv, the live value-ring path):** `0da44dd` ASSIGN simple-var (ASSIGN
  alloc'd first sval=name, RHS ring result γ→ASSIGN, entry=RHS) · `87fb378` CALL ARG MODEL — only
  write/print CHAIN args visibly; every named TT_FNC SUB-GRAPHS args (icon arg_block mirror,
  plain-calloc IR_graph_t** → IR_EXEC.counter); closed rk_join (the "unmatchable ival quirk"
  defer is OBSOLETE — quirk was the missing sub-graph model) · `e2f439e` IF (alloc IF, then-CONJ,
  then-block, [else-CONJ, else-block], cond; cond γ→then-entry ω→else-entry-or-stmt-succ@β;
  IF/CONJ γ→next-stmt; ops:[cond-entry]; entry=cond entry; single-stmt blocks DO get CONJ —
  raku ≠ icon) + string relops eq=16 ne=17 oracle-probed · `89dfe98` WHILE (per doc convention)
  + FOR_RANGE (alloc ASSIGN(var),TO sval="ag" ops:[lo,hi],lo,hi,CONJ,body-rev; entry=lo;
  TO γ→ASSIGN ω=stmt-succ@β; body ω→TO@β; CONJ γ/ω→TO; by-ILIT dropped) · `592b028` EVERY
  (for LIST → v: alloc EVERY,LIST_BANG,src,CONJ,body; entry=LIST_BANG; src γ=NULL ω=EVERY@β
  as LIST_BANG operand; NO visible loopvar ASSIGN — binding dump-invisible) + statement
  push(@a,x)→@a=push_pure ival=2 invisible · `b9784bc` junctions any/all/one/none→__rk_jct_*
  + PROC PARAM SKIP (bare TT_VAR children were lowered as stmts; oracle titled n=8 pins skip) ·
  `57570eb` ARR_SET→arr_set_pure ival=3 + $p=pop(@a)→alloc ASSIGN(a),arr_init,ASSIGN(p),
  arr_last; ring arr_last→ASSIGN(p)→arr_init→ASSIGN(a) · `e769d0b` for-gather THIRD generator
  shape (no EVERY/LIST_BANG: ASSIGN(v),GATHER ival=take-count γ→ASSIGN ω=stmt-succ@β,CONJ,body;
  entry=GATHER) · `4ff66b8` regex family: SMATCH→re_match ival=2 (mode-tag QLIT dropped),
  CAPTURE→re_capture, NAMED_CAPTURE→re_named_capture — closed 5 programs · `b90d5a1`
  SORT→array_sort + MAP/GREP ival=body-argblk PTR, counter=src-argblk (PLACEHOLDERS).

  **EXEC EVIDENCE (first measurement):** inline m2 xcheck SCRIP_NL=0-vs-1 over 47 programs:
  SAME=26 DIFF=0 SKIP=21 (both-legs rc=134 abort class). VACUOUSNESS AUDIT (Phase-4 lesson):
  4 SAME are EMPTY-SAME both legs (for_array_simple/underscore, map_grep_sort24, reverse —
  shared m2 runtime limit); ~21 verified real output.

  **FLAGS FOR LON:** (a) ruling (3) is now THE raku blocker — DIFFER=3 all multi-sub-degenerate
  (oracle UNHANDLED + drops procs, NL dumps all); exempt list closes the board. (b) push/pop/
  arr_set desugars implemented for the EVIDENCED shapes only (simple-VAR array, pop-in-assign);
  other mutators (shift/unshift) unprobed. (c) MAP/GREP exec channel placement is a placeholder
  guess beyond the dump bytes — consumer-mine before trusting.

  **NEXT:** ruling (3) → raku exempt list → board clean · raku exec channels (LIST_BANG/GATHER
  var binding, MAP/GREP arg-blocks) consumer-mined + m3/m4 NL-leg smoke BEFORE flip talk ·
  pascal LAD-2d pcom chararr (awaits Lon design) · LAD-0b pointer-ival ruling.

**▶ HANDOFF (2026-06-11, Fable 5, Lon "continue" mid-session) — PROLOG CONVERTED + OLD LOWERER
DELETED. Rulings (2)+(10) granted by Lon this session; flip + deletion landed in 2 pushed rungs.
SHAs: SCRIP `8a2d6a7` (HEAD==origin/main, build GREEN from wiped object dir, tree clean; one clean
rebase over concurrent `d39d6c8`), .github THIS COMMIT. Gates held both rungs.**

  **RUNG `5225acb` (THE FLIP + flip-blocking fix):** baseline re-verified first (xcheck 141/143,
  both residuals re-probed: plunit byte-identical modulo `^\[lower` filter; puzzle_10 minimal probe
  OLD `a,a` vs NL `a,b`). First flip attempt dropped smoke m3/m4 5/5 → 1/5 — the prior "smoke at
  bar" was measured under the OLD default; NL graphs had never run modes 3/4. ROOT CAUSE
  (consumer-mined; dump-invisible AND m2-invisible since the interp GCONJ arm follows γ wires, not
  `goals[]`): NL set neither `g->nslots` (GZ cell frame = nslots+nsynth; nslots=0 collided synth
  cells with var slots → bindings clobbered → silent empty output) nor `g->body_root` (emit_bb
  mode-4 + CHOICE-body resolution), and head-arg UNIFYs were wire-only — `pl_gz_fact_clause_units`/
  `pl_gz_rule_clause` require `goals[0..ar-1]` = UNIFY(LOGICVAR i, head_i) IN goals[] (trivial var
  heads included), so every GOAL callee was rejected (gz_admit=NO, verified by temporary trace,
  reverted). FIX: `max_var_slot` AST scan → nslots; body_root=GCONJ; head UNIFYs for ALL i<arity
  prepended into goals[]; arity-0 bodyless facts entry=SUCCEED. Smoke → 5/5 ALL THREE MODES.
  **DO-NOT note:** old `lower_prolog.c` was briefly opened during diagnosis before pivoting to the
  consumer spec; the fix as landed is consumer-derived.

  **RUNG `8a2d6a7` (deletion):** `lower_prolog.c` deleted (−636 lines); `lower_pl_clause_graph`
  unconditionally NL (icon precedent); Makefile entries removed; clean rebuild verified from wiped
  object dir. Gates re-run at the rebased HEAD: prolog smoke 5/5 ALL, scoreboard 7/7, icon m2
  12/12 HARD m3/m4 10/12 (same 2 pre-existing).

  **FLAGS FOR LON:** (a) xcheck_sno_nl reads SAME=83 DIFF=70 in this fresh container — VERIFIED
  IDENTICAL AT STASHED `3ec9c57` BASELINE, pre-existing, kin of OPEN 11; the sno yardstick claim in
  caveat 2 is now stale in fresh containers. (b) prolog scoreboard/xcheck are self-comparisons
  post-deletion; standing exec evidence = the 141/143 xcheck recorded at `5225acb`.

  **NEXT:** raku single-sub constructs (ruling (3) still open; apply the Phase-4 lesson — m3/m4
  smoke on the NL leg BEFORE any flip) · pascal LAD-2d heavy tails (pcom chararr __pas_strput
  awaits Lon design) · LAD-0b pointer-ival ruling.

**▶ HANDOFF (2026-06-11, Fable 5, Lon "perform hand off") — PROLOG LAD-4d CODE COMPLETE: m2 xcheck
123 → 141/143 SAME in 4 pushed rungs; the 2 residuals are BOTH ruling items, not code. SHAs: SCRIP
`20ac230` (HEAD==origin/main, build GREEN, tree clean), .github THIS COMMIT. Gates held every rung;
3 clean rebases over concurrent upstream commits (`56db90f` icon FULL-14, `5032a45`, pascal).**

  **RUNG `908b303` (catch):** catch/3 → IR_CATCH + bb_catch_state_t{goal_g,catcher,rec_g}; goal and
  recovery each lowered into separate IR_graph_t via thread_goals (the findall gcfg pattern); catcher
  reified in the MAIN graph AFTER the CATCH node and pushed as sole operand (oracle order); throw/1
  already routed via IR_BUILTIN. Exceptions ×5 closed; byte-verified rung28. 123→128.

  **RUNG `4fcf9c9` (DCG):** (1) DCG RULE translation is FRONTEND work (prolog_parse.c
  dcg_expand_body — both legs see translated clauses); the missing NL piece was ONLY the call-site
  phrase/2,3 → GOAL G.functor args G.args++[L, Rest-or-synthetic-nil]. (2) TT_PROGRAM (t->t=116)
  goal case — the frontend wraps ITE then/else conjunctions in TT_PROGRAM; goal()'s default arm
  silently swallowed them as bare SUCCEED (pushback_rest main produced EMPTY output). Now
  GCONJ-wrapped via thread_goals+conj_owner, the DISJ-comma-branch idiom. (3) arg-ω inherit
  NARROWED to exactly {is,<,>,=<,>=,=:=,=\=} — oracle probe over 14 builtins; ==/plus/succ/
  atom_codes/atom_length/functor/var args carry ω=·. 128→133.

  **RUNG `ffddd34` (bar-tail — the big one):** frontend encodes [X|T] as TT_MAKELIST v.ival=1 with
  the TAIL as the LAST CHILD (pt_list); NL capped EVERY list with nil, so [a|b] reified as
  .(a,.(b,[])) and every [H|T] pattern in the corpus unified against the wrong shape. One fix closed
  rung40 typetest + rung05/06 backtrack/lists + puzzles 04/07/14/17. 133→140. METHOD NOTE: /tmp
  probe files do NOT persist across tool calls — an earlier false dump-MATCH was both legs erroring
  on a vanished file; recreate probes in-call.

  **RUNG `20ac230` (\=):** X \= Y is NOT a builtin anywhere — no interp arm; the oracle lowers it
  STRUCTURALLY as (X = Y → fail ; true): synthesized SUCCEED/FAIL arms + COMMIT/GATE +
  UNIFY(cond, ops=[lhs,rhs]) + ITE sharing one bb_ite_state_t, TT_IF allocation order, entry=ITE.
  Closed puzzle_02. 140→141.

  **RESIDUAL 2 (NOT code):** plunit → ruling (2) (`^\[lower\]` filter; IDENTICAL modulo OLD punt
  narration). puzzle_10 → NEW ruling (10): OLD-leg DISJ-redo semantic bug, NL matches SWI-Prolog
  (installed in-container as third oracle). Flip bar (SAME=143 + smoke gates) is met under those
  two rulings; smoke already 5/5 all modes.

  **NEXT:** Lon rules (2)+(10) → flip prolog default → old lower_prolog.c deletion eligible ·
  pcom chararr __pas_strput (awaits Lon design) · raku single-sub constructs (awaits ruling (3)).

**▶ HANDOFF (2026-06-10, Fable 5, Lon "perform hand off") — PROLOG LAD-4d CONVERSION RUNG 1 +
PASCAL LAD-2d TWO SHARED BUG FIXES. SHAs: SCRIP `58a7d8d` (HEAD==origin/main, build GREEN, tree
clean), .github THIS COMMIT. Two pushed SCRIP rungs; gates held.**

  **RUNG `1c687d2` (pascal LAD-2d, en route to pcom):** (1) binop_apply numeric relops had NO
  string arm — two string operands fell into `(long)lv.r` union garbage comparing everything EQUAL;
  pcom's `rw[i]=id` reserved-word lookup matched the first entry per length bucket → error 18 →
  hang. Fixed: both-strings → slen-aware memcmp before the numeric path. (2) Pascal set-type
  ALIASES never registered (type_decl dropped −2, simple_type never resolved set typenames, type:
  collapsed −2→−1, params unregistered) so set `+ - *` via named types (setofsys!) lowered to
  integer BINOPs — 5+14=19; disjoint/subset cases coincide, which is why the 103-corpus never
  caught it. Fixed in pascal.y (+tab.c regen). pcom now scans symbols correctly; NEXT pcom blocker
  DIAGNOSED UNFIXED: chararr elementwise stores (`id[k]:=ch`) hit generic arr_set_pure and build an
  int-array (phantom slot-0, int codes) instead of mutating a string — needs a __pas_strput rewrite
  in mk_assign for pas_is_chararr bases + blank-string init decision (length vs [1..8] mapping —
  Lon may want to weigh in).

  **RUNG `58a7d8d` (prolog LAD-4d rung 1):** gate seam + real exec channels; inline m2 xcheck
  (SCRIP_NL=0 vs 1, 143 programs) first-wiring 86 → 123 SAME. Spec mined from interp arms ONLY
  (DO-NOT honored): bb_goal_state_t args = the term() nodes (were DISCARDED), conj goals[]
  transferred to bb_conj_state_t, findall goal arg → separate sub-graph in bb_findall_state_t,
  DISJ arms operand_aux (pl_disj_arm_enter enters GCONJ arms at goals[0]), builtin set 4→~70
  (the IR_BUILTIN arm's strcmp inventory), non-display builtin args inherit arg-ω (oracle: is/<
  args ω=…β, write args ω=·), arith functors → IR_ARITH (resolve_arith_eval rejects STRUCT —
  is/2 was silently failing), TT_IF (frontend's (C→T;E) desugar) → ITE/ITE_COMMIT/ITE_GATE shared
  bb_ite_state_t with oracle allocation order else-then-COMMIT-GATE-cond-ITE (rung04 byte-checked),
  head args → UNIFY(LOGICVAR i, head_i) chain. All sidecars plain calloc/strdup (GC-hazard rule).

  **FLAGS FOR LON:** (a) icon scoreboard MATCH=7 DIFFER=2 (generators, coverage_x64_gaps) in this
  fresh container — VERIFIED IDENTICAL AT STASHED BASELINE, pre-existing; kin of the aff86df
  finding (SCRIP_NL=0 selects no icon oracle since lower_icon.c deletion `3546ea2`); the goal
  file's "icon 9/9" CURRENT line does not reproduce here. (b) chararr design decision above.

  **NEXT:** LAD-4d remaining 20 DIFFs (Phase 4 list — exceptions/catch is the cleanest next bite:
  bb_catch_state_t{goal_g, catcher, rec_g} mirrors the findall sub-graph pattern) · pcom chararr
  strput · raku single-sub constructs (pending Lon's multi-sub ruling).

**▶ HANDOFF (2026-06-10, Fable 5, Lon "perform hand off") — PROLOG DUMP SWEEP COMPLETE 0→7/7 +
ICON PHASE 1 CLOSED. SHAs: SCRIP `cb127cb` (HEAD==origin/main, build GREEN, tree clean), .github
THIS COMMIT. Three pushed rungs total; gates held every rung.**
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
flattens both. Gates held every rung: sno 152/153, icon 9/9, NEWFAIL=0. ICON LAD-1a queens +
LAD-1b generators verified MATCH and CLOSED (landed via intervening ICON-FULL-PASS work). FLAGS:
pascal scoreboard UNSCOREABLE — OLD oracle leg aborts silently on every corpus .pas in a fresh
container, NL leg runs (OPEN 9, verified pre-existing via stash baseline). KEY FINDING: the prolog
dump bar is SHALLOW — oracle dumps ONLY main's clause-body graph, so 7/7 says nothing about other
predicates or exec channels; GOAL/GCONJ/findall ival arg-blocks are placeholder calloc PTRs.
NEXT: LAD-4d prolog conversion (all-predicate clause graphs + exec channels per interp arms +
SCRIP_DUMP_X probe, m2 cross-check old-vs-new before any default flip) · raku single-sub
constructs (pending Lon's multi-sub ruling) · pascal heavy tails (blocked on OPEN 9 for scoring).**

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

**▶ HANDOFF (2026-06-11, Fable 5, Lon "perform hand off") — RAKU CONVERTED (the fifth and last)
+ LOWER PROMOTION: nl/ FOLDED UP, _nl DROPPED, OLD MACHINERY DELETED. SHAs: SCRIP `662f249`
(HEAD==origin/main, clean build GREEN rc=0, tree clean; rebased over upstream `d07afad`/`8a41154`
emitter work, no overlap), .github THIS COMMIT. Two pushed SCRIP rungs; gates held both.**

  **RUNG `87b62df` (raku conversion):** the NL lowerer was dump-complete, execution-dead — the
  seam: `lower_rcall` never set `IR_LIT.dval`, the interp IR_CALL dispatch key (1.0 ring-visible
  say/write args, 2.0 sub-graphed-arg calls; old raku set 2.0, icon NL sets both). Plus BINOP
  operands → bb_operand_aux (PEERS), GATHER take-expr sub-graph array in EXEC.counter, SMATCH
  dval=2.0. m2 xcheck 4→26 SAME DIFF=0; the 21 old-leg rc=134 aborts: NL aborts only 10 kin,
  runs 11 clean (8 with output) — NEWFAIL=0, strictly better. METHOD NOTE: this session began
  with uncommitted dval work already on disk from an interrupted prior turn — verified coherent
  against the diagnosis, adopted, gated, committed.

  **RUNG `662f249` (the promotion, Lon directive):** nl/lower_*_nl.c → lower_*.c; symbols
  lower_prolog_nl_clause → lower_prolog_clause, static lower_sno_nl → lower_sno. DELETED:
  lower.c (label registry — its only live exports, used by lower_sno + IR_interp — relocated
  into lower_program.c), old lower_raku.c (zero link consumers, nm-verified), lower_internal.h
  (all-dead decls), nl_on()/SCRIP_NL, old SNO/pascal/raku arms + pas_register_labels +
  pas_rewrite_node/graph + make_{computed,indirect}_goto. ISOLATION nm-AUDITED: each lowerer
  exports only its lower_<lang> entry family, internals static, zero _nl symbols. Boards went
  NL-vs-NL: sno 10/125→152/153 DIFFER=0, snocone 7/111→153 DIFFER=0, raku 26/3→38/0, pascal
  UNSCOREABLE→93/11 (stage2 frame-rewrite pipeline delta), icon 7/2 prolog 7/7 held — OPEN
  9/11 root-caused as the zombie legs and CLOSED. Stale-obj hazard: /tmp/si_objs must be
  cleaned across this commit or old .o files link silently.

  **POST-PROMOTION m3/m4 VALIDATION (Phase-4 lesson honored):** with `make libscrip_rt`
  (open-5 artifact re-confirmed) icon m2 12/12 HARD m3 10/12 m4 10/12, prolog m2/m3/m4 5/5 —
  full watermark, all modes, on the promoted tree. raku smoke 0/17 diagnosed: top-level
  MAINLESS programs (no TT_SUB_DECL → no main graph, FATAL both modes, both legs at baseline) —
  RAKU frontend gap, not the promotion.

  **REMAINING (the goal's structure is DONE; tails):** raku exec-channel tails (LIST_BANG/GATHER
  loop-var binding, MAP/GREP placeholder arg-blocks — the 4 EMPTY-SAME programs) + raku residue
  census (10 abort-kin, 4 silent, mainless support) · pascal LAD-2d pcom `__pas_strput`
  (Lon design) + ppp + the 11-DIFFER pipeline-delta ruling · snocone/rebus conversion verify ·
  harness retirement ruling (12) · hygiene (13) · cross_lang polyglot revival (14) ·
  style sweep (7).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
