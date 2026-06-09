# GOAL-IR-REDESIGN.md — LOWER REWRITE (the `src/lower/nl/` lowerers ARE the goal)

**Owner repo:** SCRIP + this file. **Scope: ALL LANGUAGES** — five segregated per-language lowerers.

## WHAT THIS GOAL IS (Lon 2026-06-09)

The lower rewrite is the ONLY thing. The five new lowerers at
`src/lower/nl/lower_*_nl.c` ARE the goal. The old-`IR_t`-struct work
(operand_aux retirement, γ/ω carrier flip, t→op rename, α/β field deletion,
sizeof fence) is DONE and has been REMOVED from this file — git history
preserves every rung. Do not re-add old-system steps here.

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

Box = operator + two outbound port wires + operand list. NOTHING else.
A box's α/β are not fields — they are this node at "α"/"β" in someone's
`IR_ref_t`. Result value: NOT in `IR_t` (multi-instance; interp/emitted code
memory-manage it). Literal payload (sval/ival/dval): SIDECAR. Runtime state:
SIDECAR or per-activation. Use literal "α" "β" strings in code, never named
constants (IDE color).

## THE FOUR-ATTRIBUTE GRAMMAR — lower guide

JCON `ir_OpFunction(coord, lhs, fn, argList, failLabel)` maps: fn→op,
failLabel→ω, success→γ, lhs→IMPLICIT (box's own result; identity names the
slot), argList→operands. Arity 0..N proven required: 0=literals, 1=unop,
2=binop, 3=sectionop x[i:j], N=call args/MakeList. **γ/ω are INHERITED
attributes** (passed down by parent); **α/β are SYNTHESIZED** (the node's own
blocks, selected by op). So `lower(cx, t, γ, ω) -> IR_t*` IS the four-attribute
grammar: γ/ω come in as params, α/β are the returned node addressed via
`IR_ref_t.sz`. The live interp (`interp/IR_interp.c`) is a goal-directed
γ/ω-FOLLOWER — each arm returns `bb->γ.node`/`bb->ω.node` as the next node and
`bb_print` hardcodes the α(γ)/β(ω) labels — NOT a tree-walker. The new lower
must REPRODUCE the OLD graph's goal-directed shape.

## DO NOT

- **LOWER REBUILD — DO NOT LOOK AT / TRANSCRIBE THE OLD LOWER (Lon ruling 2026-06-08).**
  Never read or replicate the OLD lowering source (`lower.c`, `lower_program.c`,
  `lower_value.c` if present, `lower_icon.c`, `lower_sno`/`lower_snobol4.c`,
  `lower_raku.c`, `lower_pascal.c`, `lower_prolog.c`). The SOLE spec for the new
  lowering is the GRAPH RESULT read in memory: `scrip --dump-bb FILE` (old = the
  oracle) vs `scrip --dump-bb2 FILE` (new). Compare graphs, fix the new lower to
  match — never by copying old code. Replicating the old source recreates its mess;
  the rebuild's whole point is clean code. The new lower is a proper switch/case
  hierarchy derived from the AST + the target graph ONLY.

## LOWER REBUILD — method + tooling (Lon 2026-06-08, graph-only)

- Five new lowerers live at `src/lower/nl/lower_*_nl.c` (externs
  `lower_icon`/`lower_snobol4`/`lower_raku`/`lower_pascal`/`lower_prolog`,
  signature `IR_graph_t * lower_X(const tree_t *)`), compiled INTO `scrip` next to
  the OLD ones — both symbol sets coexist (old `lower_icn`/`lower_sno`/`lower_pas`/
  `lower_rku` + new). The `_nl` suffix avoids the flat-object-dir basename collision;
  added to the EXPLICIT compile recipe in `Makefile` (the `scrip:` recipe, ~line 540)
  AND the prereq list (~line 238). `emit()` helper renamed `build()` in all five
  (emit is reserved for emitters). Default build path unchanged so gates are safe.
- `scrip --dump-bb2 FILE` routes the parsed AST through the new lowerer for that
  language and prints via `bb_print` (handler in `scrip.c`, opt-in flag, default path
  untouched). `--dump-bb` = old (oracle).
- SCOREBOARD loop (reconstruct in `/tmp`; does NOT survive a new container): for each
  program run both dumps, strip `^; proc` + blank lines, `diff`, tally
  MATCH/DIFFER/NEWFAIL. BASELINE 2026-06-08 on `icn9` (test/icon/*.icn):
  MATCH=0 DIFFER=9 NEWFAIL=0 — new lowering produces a graph for all 9, none match,
  new ~1.5-2x node count. TARGET: drive MATCH up on icn9, then the other sweeps.
- hello target SHAPE (read off `--dump-bb`, no source): per-proc graph (NO PROG/PROC
  wrapper); allocate `IR_SUCCEED`(idx0)+`IR_FAIL`(idx1) FIRST; `lower()` threads
  `(γ,ω)` and RETURNS THE ENTRY node (leftmost-evaluated leaf, not the result);
  CALL = `sval`=name + `ival`=argcount with args γ-threaded (arg is the entry);
  success wires target port `α`, failure wires target port `β`.
- **DISPATCH = TREE-PATTERN GAUNTLET, model-tree applied like a SNOBOL4 pattern
  (Lon rulings 2026-06-08, refined).** TOP level is a flat `switch (t->t)` over TT_*.
  WITHIN a case, NO `if/else-if/else` field-poking. Instead a GAUNTLET: a sequence of
  TREE-PATTERN matches tried in order, first hit builds + returns; sub-casing = more
  patterns (the tree analogue of SNOBOL4 `|`). CRUCIAL — a "tree match" is NOT a
  procedural helper. It is a MODEL TREE (data) that describes the AST form to match AND
  marks CAPTURE, APPLIED to the node by a generic engine — EXACTLY a SNOBOL4 PATTERN
  applied to a string: the pattern is a first-class value; capture binds matched
  subtrees / values (the tree analogue of `. VAR`). A lowering rule = build pattern P →
  apply to node → use the captures to build the IR. This is the SAME design the
  self-hosted bootstrap lower stage (written in Icon) will use — tree patterns over the
  AST — so the C `nl` version must use it too, never ad-hoc conditionals. Core shape: a
  pattern node = { require-kind | capture-into-slot | wildcard } + a child-pattern
  list (+ an sval constraint to match TT_ATTR names like `:subj`); engine
  `pmatch(pat, t, caps[])` recurses on kind+children and fills `caps[]`. NO inline
  `t->c[0]->t == TT_X` conditionals anywhere.
- **PRIOR ART + SUBSTRATE (scan 2026-06-08).** Tree-pattern-matching codegen is the
  BURS / twig / burg / iburg family (tree patterns + dynamic programming). iburg is
  Fraser/Hanson/Proebsting — SAME Proebsting as the canonical JCON (RULES) — and is
  ~200-700 lines of Icon / ~950 C (vs ~3000 twig, ~5000 burg); lcc uses a burg-style
  matcher. DECISION (Lon 2026-06-08): patterns are simple, so the C bootstrap lower
  uses a LIGHTWEIGHT hand-rolled `pmatch` (~50 lines), NOT a heavyweight lib — twig/
  burg are instruction-SELECTION (cost-optimal covering), overkill for structural
  lowering. Reference paths it grows into: OPTIMIZATION matching = BURS/iburg-in-Icon
  (cost-based optimal, = "Icon for optimization"); self-hosted matcher = Prolog
  unification (logic vars = captures) / term rewriting. Same tree matching either way.

## NODE-EXACT CONVENTIONS — the live spec (byte-verified vs `--dump-bb`)

These are reverse-engineered node-for-node from the oracle and confirmed
byte-identical in the matched programs. The Icon lowerer (`lower_icon_nl.c`)
implements all of them; the other four `_nl` files follow the same shapes.

### Value layer
- **Leaves** chained via `γ`. **Statements REVERSE-threaded:** alloc
  `IR_SUCCEED`@0 / `IR_FAIL`@1 first, then stmts in reverse source order so
  entry = first-executed (highest index).
- **BINOP:** `ival=BinopKind`; operands ride the value-ring (NO `ops:[]`);
  chained LEFT→RIGHT (alloc op, then left, then right; `left.result.γ→right.entry`;
  `right.result.γ→op`; entry=left).
- **UNOP:** `ival=(tree_e)t->t`; operand chained.
- **CALL arg model:** ONLY `write`/`writes` CHAIN args via the value-ring
  (visible). EVERY other call — `map`, all other builtins, `[]`, `MAKELIST`,
  user procs — SUB-GRAPHS its args (invisible; entry = the call node).
  *(Supersedes the earlier "user-proc detected by name ∈ PROC_DECL set" heuristic,
  which was wrong: `map(s)` sub-graphs while `write(count)` chains.)*
- **subscript** `a[i]` → CALL `[]` `ival=n`. **list** `[…]` → CALL `MAKELIST`
  `ival=count`.
- **ASSIGN** simple-var-LHS = `sval`=name + EXACTLY ONE operand (rhs result),
  goal-directed (complex LHS → 2-operand fallback).
- **AUGOP** `x OP:=y` DECOMPOSES to ASSIGN+BINOP.
- **RETURN:** contextual passed `γ`/`ω` (NOT forced PSUCC/PFAIL). Oracle's last-stmt
  `return "yes"` has `γ=PSUCC` only because threading passes PSUCC there; a nested
  `return "no"` inside an if has `γ`=next-stmt. *(Corrected from the initial
  forced-PSUCC/PFAIL version.)*
- **MULTI-PROC:** `collect_procs` (DFS, STMT→:subj→PROC_DECL, skip globals/records);
  `--dump-bb2` iterates procs in source order emitting `; proc <name>` + `bb_print`
  exactly like `--dump-bb`. AST note: top is `STMT` whose `:subj` is the
  `TT_PROC_DECL`; body = `c[2]`; `TT_FNC` = c[0] callee VAR + c[1..] args.

### Control flow
- **CONJ** = a multi-statement braced block (`TT_SEQ_EXPR`) used in expression
  context (while/then/else body). Single-statement blocks get NO CONJ (parser
  unwraps `nc==1`). Built first, `γ`/`ω` = passed; stmts reverse-threaded to it.
  NOT the loop back-edge.
- **Failure-ω rule for block stmts:** each stmt's RESULT node `ω` → the nearest
  PRECEDING resumable stmt's result, else the enclosing `ω`. `is_resumable` =
  TT_IF/SCAN/EVERY/TO/TO_BY/ALTERNATE/REPEAT/WHILE/UNTIL. (Sub-nodes keep
  `ω`=enclosing.) Explains palindrome later-stmts→IF vs meander else-block
  both-assignments→loop-resume.
- **WHILE:** body success AND failure both loop to condition-entry; WHILE node =
  loop EXIT (reached via condition-fail `ω`); while-entry = condition entry;
  `ops:[cond-entry]`. No fabricated CONJ.
- **IF:** condition INLINED as the if-entry; IF node = resume anchor (reached only
  via `ω`); `ops:[cond-entry]`; no-else wires condition-fail → passed `ω`;
  else-branch supported.

### Generators
- **EVERY/TO:** `TO`/`TO_BY` node `sval="ag"`, `ops:[lo,hi]`, chained lo→hi→node,
  entry=lo (leftmost leaf). **TO_BY drops the by-expression entirely — it produces
  NO visible node** (matches oracle; by value not materialized in the dump — flag if
  execution ever matters). `EVERY` node `γ=ω=`next-stmt (loop exit), `ops:[gen-entry]`.
  For `every VAR := GEN do BODY`: the generator (TO) is the assignment's single
  operand; assignment.`γ`→body-entry (fixup), generator.`ω`→EVERY. **Body loop-back =
  the generator node IF the body is_resumable (roman `while`→TO), ELSE the EVERY node
  (sieve `sieve[j]:=0`→EVERY).**
- **IDX_SET:** subscripted assignment `lhs[idx]:=val` → `IR_IDX_SET`, operands
  `[base, index.., value]`, each operand `γ`→the IDX_SET node (NOT chained to each
  other), entry = base.

## STANDING CAVEATS — open / need Lon's ruling

1. **Scoreboard pointer-`ival` normalization is MINE and UNRULED.** `/tmp/scoreboard.sh`
   (scratch, not in repo) does `sed -E 's/ival=[0-9]{7,}/ival=PTR/g'` because the oracle
   stores a non-deterministic heap pointer in `GEN_SCAN.ival` (observed 921023984 then
   164042224 across runs). Defensible (heap addresses aren't semantic) but it changes the
   yardstick — **Lon should confirm it's legitimate** before MATCH counts are fully
   trusted. Legit ivals are ≤3 digits (opcodes/argcounts/tree-codes); the 7-digit floor
   only catches pointers. wordcount + meander both rely on it.
2. **`--dump-bb2` is DUMP-ONLY — zero execution validation, and it's STRUCTURAL.**
   `scrip.c` returns right after `bb_print`; mode-2 interp (`IR_interp_once`) runs the OLD
   lowerer's graph from `s2->bbp.table`, never the new `lower_icon` graph. Every "MATCH" =
   dump bytes agree, NOT "runs correctly." Wiring `--dump-bb2`→mode-2 is a separate
   prerequisite-for-trust task.
3. **`TT_SCAN` is still a NODE-ONLY STUB.** Emits `IR_GEN_SCAN` with `ival` = a
   freshly-alloc'd EMPTY sub-graph; subject+body are NOT lowered into it. Dump-correct
   (`bb_print` doesn't recurse GEN_SCAN, so body is legitimately invisible) but
   executionally empty. wordcount/meander match because of that invisibility, not because
   the scan is complete. TODO: lower subject+body into the sub-graph.

## LADDER — per-language gauntlet, strict order, gate each rung

Method is fixed (see `## LOWER REBUILD`): `--dump-bb` oracle vs `--dump-bb2` new → diff →
fix first divergence → rebuild → re-diff → COMMIT each green rung + guarded push. Each
language repeats the arc Icon proved: **(a)** value layer + multi-proc/clause structure,
**(b)** control flow, **(c)** generators/backtracking, **(d)** the deep construct (patterns /
suspend / unification). Commit per green program; never theorize past the bytes. ALL FIVE
already dispatch through `--dump-bb2` (scrip.c:1664-1689); only `lower_icon_nl.c` is
goal-directed today — the other four are the same null-wired skeleton Icon had before `8bd1ebf`
and need the same rewrite. ORDER RATIONALE: finish the reference language (Icon), then the
easiest (Pascal), then the highest-leverage (SNOBOL serves snobol4+snocone+rebus), then the
structurally-unique (Prolog), then the parked one (Raku). **Lon may reprioritize SNOBOL ahead of
Pascal for strategic reasons — flagged.**

### Phase 0 — DURABLE HARNESS (prerequisite; do first)
- [x] **LAD-0a — Commit the scoreboard.** ✅ LANDED SCRIP `a103ae7`. It is `/tmp` scratch and dies with the container.
  Write `scripts/scoreboard.sh LANG` (LANG ∈ icon|snobol4|snocone|prolog|pascal|raku) that
  enumerates that language's corpus (icon→`test/icon/*.icn`; snobol4→`test/snobol4/*.sno`;
  snocone→`test/snocone` + `corpus/crosscheck/snocone/*.sc`; prolog→`test/prolog/*.pl`;
  pascal→`corpus/programs/pascal/*.pas`; raku→`test/raku/*`), runs `--dump-bb` vs `--dump-bb2`
  per program, strips `^; proc` + blank lines, diffs, tallies MATCH/DIFFER/NEWFAIL, prints a
  per-program table + totals. GATE: re-run icon and reproduce 6/8 (parity with the retired /tmp
  version) before trusting it on any other language. RESULT: reproduces icon MATCH=6
  DIFFER=2 (queens, generators) NEWFAIL=0 SKIP=1 — the SKIP class catches oracle-unparseable
  programs (`coverage_x64_gaps.icn`) that the retired /tmp version would have false-MATCHed,
  and explains the prior 8-vs-9 count gap.
- [ ] **LAD-0b — Pointer-ival ruling baked in (caveat 1).** Get Lon's ruling on the
  `ival=[0-9]{7,}→PTR` normalization, then encode it in `scoreboard.sh` as a named, commented
  flag (default = Lon's ruling) so the yardstick is explicit and in-repo, not a hidden sed.
  EVIDENCE (a103ae7): `--raw` (normalization OFF) drops icon 6→4 — wordcount + meander flip to
  DIFFER — so the normalization is LOAD-BEARING for 2 of 6 matches, not cosmetic.
- [ ] **LAD-0c — (trust, optional) wire `--dump-bb2`→mode-2 (caveat 2).** Converts every MATCH
  from "dump bytes agree" to "runs correctly." Defer if it blocks momentum, but it is the only
  thing that makes a MATCH an execution guarantee.

### Phase 1 — ICON to floor (closest to done: 6/8)
- [ ] **LAD-1a — queens.** First divergence = `scope=global` annotation on IR_VAR (collect
  top-level `TT_GLOBAL`/decl names, thread through `icx_t`, annotate matching IR_VAR; check how
  `bb_print` sources the scope field). Then generator PROCEDURES (`safe`/`try_col` are user procs
  in `every…if…`/recursive-backtracking) + `if…then fail`. TRACE oracle `safe`/`try_col`
  node-exact BEFORE coding (datapoint: my `safe` n=18 vs oracle n=33 — not yet understood). GATE:
  queens MATCH, icn9 6→7, full sweep byte-identical.
- [ ] **LAD-1b — generators.icn.** `suspend`, generator caching, `IR_PROC_GEN` — the deepest Icon
  construct; expect real work, may stay DIFFER a while. GATE: generators MATCH → icn9 8/8.
- [ ] **LAD-1c — scan sub-graph (caveat 3).** Lower TT_SCAN subject+body into the GEN_SCAN
  sub-graph so wordcount/meander matches are EXECUTION-real, not invisibility artifacts. GATE:
  re-MATCH wordcount/meander with the sub-graph populated (under LAD-0c if wired).

### Phase 2 — PASCAL (easiest second language; structured, no generators/patterns)
Corpus = `corpus/programs/pascal/*.pas` (test/pascal is empty); curated floor = pas5.
- [ ] **LAD-2a — goal-directed rewrite of `lower_pascal_nl.c`.** Replace the null-wired skeleton
  (`push_kids`/`lower_nary`/`lower(...,NULL,NULL)`) with the goal-directed γ/ω-threading model
  proven in `lower_icon_nl.c`. Start at the smallest corpus program; reproduce the oracle per-proc
  shape. GATE: first Pascal MATCH.
- [ ] **LAD-2b — value layer + procedures/functions.** BINOP/UNOP/ASSIGN/CALL per the conventions;
  Pascal proc/func decls + params; reverse-threaded statement blocks. GATE: pas5 MATCH climbs.
- [ ] **LAD-2c — control flow.** if/then/else, while, `for` (bounded → reuse the TO/EVERY wiring
  family), repeat/until, case. GATE: broaden across `corpus/programs/pascal/*.pas`; record
  MATCH/total.
- [ ] **LAD-2d — types/records/sets/pointers** as divergences demand. GATE: large-portion MATCH on
  the Pascal corpus.

### Phase 3 — SNOBOL4 + SNOCONE + REBUS (highest leverage: ONE lowerer, two suites)
`--dump-bb2` routes all three through `lower_snobol4` (scrip.c:1688 default arm), so this phase
scores against BOTH sno153 (`test/snobol4/*.sno`) AND sco191 (`test/snocone` +
`corpus/crosscheck/snocone`). Statement model: TT_STMT carries `:subj`/`:pat`/`:repl` +
TT_GOTO_S/F/U; gotos wire onto γ/ω (the `stmt_subj` helper already extracts `:subj`).
- [ ] **LAD-3a — goal-directed rewrite of `lower_snobol4_nl.c`.** Skeleton→goal-directed. Start
  NON-pattern (assignment, arithmetic, write, function calls, goto control flow). GATE: first
  SNOBOL MATCH.
- [ ] **LAD-3b — value layer + statement/goto control flow.** ASSIGN, BINOP, CALL, `:subj`
  extraction, S/F/U goto→γ/ω wiring, DEFINE function bodies. GATE: the goto/arith subset of sno153
  climbs.
- [ ] **LAD-3c — PATTERN MATCHING (the deep core).** `:pat`/`:repl` + pattern constructors
  (concatenation, alternation `|`, deferred eval, conditional/immediate assignment, cursor,
  builtin patterns). The bulk of SNOBOL semantics and the hardest part — stage sub-pattern by
  sub-pattern, each gated. GATE: pattern programs MATCH; large-portion sno153 + sco191.
- [ ] **LAD-3d — Snocone/Rebus deltas.** AST forms specific to Snocone/Rebus (not covered by the
  SNOBOL core) surface as sco191 divergences; address them. GATE: large-portion sco191.

### Phase 4 — PROLOG (own goal-spine: clauses, unification, backtracking)
Corpus = `test/prolog/*.pl` (pl8). Structurally distinct: clauses→goals, compound terms→IR_STRUCT
(the skeleton already emits IR_STRUCT for binop/unop).
- [ ] **LAD-4a — goal-directed rewrite of `lower_prolog_nl.c`.** Reproduce the oracle clause/goal
  graph (read the GRAPH only — never the old `pl_lower_goal` source). GATE: first Prolog MATCH.
- [ ] **LAD-4b — facts/rules/queries + unification + arithmetic (`is/2`, comparisons).** GATE: pl8
  climbs.
- [ ] **LAD-4c — backtracking / cut / control (`,` `;` `->` `!`)** as divergences demand. GATE:
  large-portion pl8.

### Phase 5 — RAKU (parked; frontend on hold)
- [ ] **LAD-5 — DEFERRED.** smoke_raku is 100% pre-existing FAIL (Tiny-Raku frontend on hold). The
  lowerer can be brought up opportunistically the same way, but MATCH cannot be execution-trusted
  until the frontend resumes. Resume on Lon's word.

### Done-condition (Lon's "large portion of the test suites")
A tracked MATCH/total per suite in `scoreboard.sh` output. Target = large-portion, NOT 100% —
generators/suspend/full-pattern depth may legitimately lag. Lon sets the per-language bar.

## Watermark

**▶ MID-SESSION UPDATE (2026-06-09, Opus 4.8, Lon attending "your choice, continue") —
LADDER added to this file + LAD-0a LANDED. SHAs: SCRIP `a103ae7` (durable scoreboard harness;
HEAD==origin/main, build green rc=0), .github THIS COMMIT. Old `IR_t`-struct system stripped at
`c20e000c`. `scripts/scoreboard.sh LANG [--raw]` reproduces icon 6/8. OPEN FOR LON: (1) LAD-0b
pointer-ival ruling — concrete stakes: `--raw` drops icon 6→4 (wordcount + meander depend on it);
(2) Phase order — Pascal (my pick: fast rungs, proves the goal-directed model generalizes) vs
SNOBOL (the two-suite lever) next. Then Phase 1 queens (LAD-1a).**

**▶ HANDOFF (2026-06-09, Opus 4.8, Lon "perform hand off" — GOOD SESSION) — LOWER REWRITE
(Icon): control flow + generators landed, icn9 MATCH 1→6 of 8. SHAs: SCRIP `4fa4b74`
(HEAD==origin/main, pushed; build GREEN rc=0; working tree clean), .github THIS COMMIT. Six
commits this session, each an immediately-pushed green rung. New `lower_icon_nl.c` is 195 lines
/ ~17.7 KB. MATCH: hello, wordcount, palindrome, meander, roman, sieve. DIFFER: queens,
generators (NEWFAIL=0 throughout). Live spec → `## NODE-EXACT CONVENTIONS`; open items →
`## STANDING CAVEATS`; the ordered plan → `## LADDER`.**

  **METHOD THAT WORKED (vs prior sessions that ended in analysis+handoff):** tight `--dump-bb`
  (oracle) vs `--dump-bb2` (new) → diff → fix the first divergence → rebuild → re-diff → COMMIT
  each green rung immediately + push (guarded). Treat the oracle as correct-by-construction (it's
  the old lower the interp already runs); do NOT theorize about whether its graph is
  "semantically right" — reproduce the bytes. Each of the last four matches was 1–2 fixes found
  straight from the diff.

  **COMMITS THIS SESSION (all on origin/main, guarded fast-forward, no --force):** `8bd1ebf`
  value layer + multi-proc (1→2) · `ca6dc4d` WHILE/IF/CONJ + write-only arg chaining → palindrome
  (2→3) · `b135278` CONJ = braced-block conjunction not loop back-edge → meander (3→4) · `d2a56b1`
  EVERY/TO generators → roman (4→5) · `4fa4b74` IDX_SET + TO_BY-2-operand + every-body loop-back →
  sieve (5→6).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
