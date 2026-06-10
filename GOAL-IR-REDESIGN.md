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

### Pascal (verified `c5225c7` / `e1b25a3`)

Per-proc graph, NO PROG wrapper; SUCCEED@0/FAIL@1 allocated first; `entry` = the body's leftmost
leaf; statements reverse-threaded (alloc in reverse source order so entry=first-executed). `lang=?`
(IR_LANG_PAS=7 is out of the print table's 1–6 range → prints "?"). γ wires target port **α**, ω
wires target port **β** (the proper success/failure split — NOT the icon α-uniform). CALL: `sval`=
callee name (TT_FNC c[0] is a TT_VAR), `ival`=nargs (TT_FNC n−1), args INVISIBLE (not lowered, so
n_operands=0 and no `ops:[]` prints); `writeln` lowers `__pas_writeln` and its AST carries a
trailing `TT_ILIT -1`, so hello's ival=2. ASSIGN simple-var: `sval`=LHS name, RHS rides the γ
value-ring (no visible operand, entry=RHS leaf). Literals are leaves: TT_ILIT→LIT_I(ival),
TT_FLIT→LIT_F(dval), TT_QLIT→LIT_S(sval). AST top: `STMT :subj → TT_PROC_DECL(VAR main, VLIST,
TT_PROGRAM(body…), VLIST)`; the body is PROC_DECL c[2]; `lower_pascal` DFS-finds the first
TT_PROC_DECL.

## STANDING CAVEATS — open / need Lon's ruling

1. **Scoreboard pointer-`ival` normalization is MINE and UNRULED.** `/tmp/scoreboard.sh`
   (scratch, not in repo) does `sed -E 's/ival=[0-9]{7,}/ival=PTR/g'` because the oracle
   stores a non-deterministic heap pointer in `GEN_SCAN.ival` (observed 921023984 then
   164042224 across runs). Defensible (heap addresses aren't semantic) but it changes the
   yardstick — **Lon should confirm it's legitimate** before MATCH counts are fully
   trusted. Legit ivals are ≤3 digits (opcodes/argcounts/tree-codes); the 7-digit floor
   only catches pointers. wordcount + meander both rely on it.
2. **Execution validation status (was: dump-only).** RESOLVED FOR ICON by the CONVERSION
   (2026-06-10): the production interp/emitters now RUN the new icon graphs (default flipped);
   RESOLVED FOR PASCAL by the CONVERSION (e5ee443, 2026-06-10): m2 parity SAME=91 DIFF=0.
   sno/snocone/raku/prolog MATCHes remain dump-only until their conversions. Beware the
   INVISIBLE EXECUTION CHANNELS (dval / EXEC.counter / operand_aux) — see the 2026-06-10
   watermark; dump MATCH alone never licenses a flip.
3. ~~TT_SCAN node-only stub~~ RESOLVED (LAD-1c CLOSED, SCRIP `a875c77`): GEN_SCAN carries real
   subject (`EXEC.counter`) + body (`LIT.ival`) blocks; wordcount/meander execution-real.

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
LAD-0a ✅ DONE — `scripts/scoreboard.sh LANG [--raw]` (SCRIP `a103ae7`); reproduces icon 6/8, SKIP
class skips oracle-unparseable programs. Corpus map + behaviour live in the script header.
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

### Phase 2 — PASCAL (easiest second language; structured, no generators/patterns)
Corpus = `corpus/programs/pascal/*.pas` (test/pascal is empty); curated floor = pas5.
LAD-2a ✅ DONE (SCRIP `c5225c7`: goal-directed `lower_pascal` + a real `--dump-bb2` dispatch-bug
fix — is_pascal had come from a stale `argi`, so `.pas` ran `lower_snobol4`; now parse-time).
LAD-2b value layer ✅ DONE (SCRIP `e1b25a3`: ASSIGN sval=LHS with RHS on the γ-ring + LIT_I/F/S
leaves → pascal **8/91**). Pascal node-exact shapes are in `## NODE-EXACT CONVENTIONS`.
LAD-2b′ multi-proc + function bodies ✅ DONE (SCRIP `e4833e2`: the parser flattens all procs into a
single top-level TT_STMT list in bottom-up reduction order = the oracle's post-order, program LAST
and named "main" by the parser → naming = `pd->v.sval`, no special-case like Icon. `lower_pascal_enum`
iterates the list; `lower_pascal_proc` lowers one body; is_function ⟺ `c[3]==TT_VAR` → synthesized
`RETURN(γ→SUCCEED, ω→SUCCEED) ops:[bare VAR funcname]`, body threaded succ=RETURN; BINOP has NO ival,
operands leaf-chain on the γ-ring; function-result LHS is a 0-arg TT_FNC (mk_ident returns a call for
known function names) so ASSIGN sval falls back to `lhs->c[0]->v.sval`. scrip.c is_pascal `--dump-bb2`
arm mirrors the Icon enum + `; proc` loop. intparam.pas MATCH → pascal **8→12/91**, icon held 6/8,
NEWFAIL=0; new: forward1/intparam/m4asg/m4wexpr.) CORRECTED (5959b33): VAR_FRAME `ival` = SLOT in the
DECLARING proc (params then locals), NOT depth — depth rides an invisible channel (execution-side TBD);
own vars frame ONLY when the proc participates in nesting (outer || byref || has_children). nestfunc MATCH.
CORRECTION to the
side-finding below: `--dump-ast` SEGFAULTS on ALL multi-proc pascal (procedure-only too), not just
nested functions — a pre-existing AST-printer bug, NOT in the `--dump-bb/bb2` lowering path.
- [x] **LAD-2c — control flow.** ✅ DONE (SCRIP `41b7deb`→`e5ee443`, 2026-06-10): goto (TT_LABEL_DEF
  scan + landings), bool-chain (`__pbtN` materialization), case (parser-desugared; seq flattening),
  resumable-ω, framing rule. Pascal **89/93** dumps + full m2 exec parity SAME=91 DIFF=0 → FLIPPED.
- [ ] **LAD-2d — types/records/sets/pointers** as divergences demand. GATE: large-portion MATCH on
  the Pascal corpus. Remaining DIFFER: pcom, ppp (heavy multi-construct tails).

### Phase 3 — SNOBOL4 + SNOCONE + REBUS (highest leverage: ONE lowerer, two suites)
`--dump-bb2` routes all three through `lower_snobol4` (scrip.c:1688 default arm), so this phase
scores against BOTH sno153 (`test/snobol4/*.sno`) AND sco191 (`test/snocone` +
`corpus/crosscheck/snocone`). Statement model: TT_STMT carries `:subj`/`:pat`/`:repl` +
TT_GOTO_S/F/U; gotos wire onto γ/ω (the `stmt_subj` helper already extracts `:subj`).
LAD-3a ✅ DONE (SCRIP `bd1e868`, Sonnet) — goal-directed `lower_snobol4_nl.c` rewrite; first SNOBOL MATCH, sno 0→22.
LAD-3b ✅ DONE (SCRIP `b28440b`/`1916489`, Sonnet) — value layer + S/F/U goto→γ/ω wiring; sno→104.
LAD-3d ✅ DONE — **Snocone CLEAN SWEEP 0→142/142 (SCRIP `5a8968c`..`fbdd37f`, Opus, 7 rungs)**. The Snocone
parser builds a DIFFERENT AST than SNOBOL4 (assignment = `TT_ASSIGN(VAR,RHS)` not `:eq/:repl`; control flow
= TT_IF/TT_WHILE/TT_FOR/… not gotos). KEY SHAPES decoded: TT_ASSIGN routes to `lower_assign`; control-flow
+ decl statements PUNT to NULL (label chains to nxt) — UNLESS the oracle allocates an ORPHAN node: **TT_IF →
bare `IR_IF` (γ=· ω=·), TT_WHILE → bare `IR_WHILE` + its condition lowered (γ=orphan, ω=WHILE); a TT_SCAN
condition → bare orphan `IR_SCAN`; a TT_ASSIGN condition (`while(s=INPUT)`) → `lower_assign(γ=orphan, ω=WHILE)`.**
The discriminator: oracle `[lower] UNHANDLED` reporting the construct's OWN kind ⇒ pure punt; reporting the
BODY kind (116 TT_PROGRAM) ⇒ oracle allocated a node. Also: VLIST RHS (tuple `('','')`) → orphan ASSIGN;
TT_SEQ statement subj (`%=` augmented assign) → orphan `IR_SEQ`; TT_ALT-of-literals pattern-VALUE assign
(`p='foo'|'hello'`) → `DTP_ASSIGN`(ops:[ALT]) + `PATTERN_LIT`×n chained + `PATTERN_ALT` (entry=first lit).
NOTE the PATTERN_*/DTP_ASSIGN value-assign family is DISTINCT from the PAT_*/match-context family below.
- [ ] **LAD-3c — PATTERN MATCHING (the deep core; sno153 only — snocone is done).** Capture cluster
  CLOSED this session (Opus): 060 (multiple captures) — nested left-capture concat was allocating a
  spurious SECOND `PAT_CAT`; fix = apply the SAME `need_cat` guard the `rc_is_capture` branch already had
  to the `lc_is_capture` branch (only a fresh PAT_CAT when `succ` is the graph SUCCEED@0; an inner concat
  whose succ is a real continuation chains directly). 062/063 (pattern REPLACEMENT `SUBJ PAT = REPL`) —
  the `has_eq` branch with a `TT_SCAN` subject now emits the replacement SCAN (`ival=1`) instead of bailing
  to NULL: pattern→`IR_EXEC.counter`, subject→`operands[0]`, NEW replacement sub-graph→`operands[1]`
  (`lower_repl_graph` = FAIL+LIT_S, mirrors `lower_subj_graph`), replacement value rides the main graph as
  the entry leaf chaining into SCAN; empty replacement (deletion) shares the path. The earlier (Sonnet
  `2354a73`) backtrack-ω rule + PAT_ALT n-way + FAIL-builtin work stands. REMAINING pattern work lives in
  the harder DIFFERs below (`cross.sno` is now SKIP — oracle segfaults). GATE: pattern programs MATCH.
- [x] **LAD-3e — SNOBOL4 multi-proc DEFINE — DONE (Opus 2026-06-09, SCRIP `a968d81`).** Resolved NOT by an
  enum/proc API but by a FEATURE FIX Lon directed: `--dump-bb` was re-dumping the SAME whole-program graph
  once per DEFINE. Each DEFINE shallow-copies the `IR_graph_t` (`*fg = *g` in `lower_program.c`), sharing
  the identical `all[]` node array and changing only `entry=`; the dump loop walked `proc_table` and printed
  that shared graph N+1 times (`; proc main` + one per function). The new `--dump-bb2` already produced the
  correct single graph. FIX: in the `--dump-bb` loop, dedup by shared node-array pointer (`->all`) — print
  each DISTINCT graph once (LINEAR SEQUENCE); Icon/Pascal (genuinely distinct per-proc graphs, different
  `all`) untouched. Also made the `--dump-bb2` SNOBOL/Prolog/etc fall-through arm emit the matching
  `; proc main` header. **scrip.c WAS touched — but only the dump-feature loop, NOT the lowering dispatch;
  no enum/proc contortion needed.** Unblocked all 8 `functions/*`: sno 130→138.
- [ ] **LAD-3f — remaining 5 sno DIFFERs (the heavy tail).** `1016_eval` (eval builtin), `expr_eval`
  (likely shares eval), `100_roman_numeral`, `library/test_case`, `coverage/coverage_sno_nodes`. Each is
  65–289 diff lines = multi-fix rungs, unlike this session's one-shot fixes. CLOSED this session by single
  fixes: 1015_opsyn (orphan CALL on `TT_OPSYN` arg), 1112/1110 arrays (bare `TT_IDX` stmt subject punts to
  NULL — was hitting `lower_expr`'s SUCCEED default), 1013_func_nreturn (`TT_NAME` RHS `.var` → ASSIGN_VAR +
  empty-name VAR, no UNOP; + NULL-body label chains to nxt not the success-goto target). GATE: each MATCH.

### Phase 4 — PROLOG (own goal-spine: clauses, unification, backtracking)
Corpus = `test/prolog/*.pl` (pl8). Structurally distinct: clauses→goals, compound terms→IR_STRUCT
(the skeleton already emits IR_STRUCT for binop/unop).
- [ ] **LAD-4a — goal-directed rewrite of `lower_prolog_nl.c`.** Reproduce the oracle clause/goal
  graph (read the GRAPH only — never the old `pl_lower_goal` source). GATE: first Prolog MATCH.
- [ ] **LAD-4b — facts/rules/queries + unification + arithmetic (`is/2`, comparisons).** GATE: pl8
  climbs.
- [ ] **LAD-4c — backtracking / cut / control (`,` `;` `->` `!`)** as divergences demand. GATE:
  large-portion pl8.

### Phase 5 — RAKU (UNPARKED 2026-06-10 on Lon's word; lowerer live, execution-trust still gated)
- [x] **LAD-5 — UNPARKED.** Lon unparked Raku ("new plan"). Lowering resumed via the standard graph-diff
  method (execution-trust still gated on the Tiny-Raku frontend per the original note). Skeleton
  lower_raku used the WRONG model (single IR_PROG + ops:[]); oracle emits per-proc VALUE-RING graphs
  (BINOP ival=opcode, CALL ival=argcount invisible-args, gamma-chaining) like Icon/Pascal. PIVOT LANDED
  (0ecd99c): lower_raku_enum (TT_SUB_DECL; name=c[0], stmts=c[1..]) + lower_raku_proc (value-ring lower_rv,
  res out-param) + is_raku dump-bb2 dispatch; omega marker alpha->beta. Opcodes +0 -1 *2 /3 %4, relops
  5-10, ~(concat)=11; say/print -> write/print. Old lower_raku kept as np<=0 fallback. **raku 0->1/29
  (rk_arith MATCH), NEWFAIL=0; risk-free (raku was 0, changes raku-scoped).**
- [ ] **RAKU MULTI-SUB ORACLE DEGENERACY — NEEDS LON RULING.** `--dump-bb` (OLD) emits only ONE proc graph
  for MULTI-sub programs (rk_subs 5, rk_interp 2, rk_combinator 9 -> all 1 proc), a shared-node-array dedup
  artifact; NOT cleanly byte-matchable. SINGLE-sub programs (oracle_procs=1=source_subs=1: rk_arith, rk_join,
  rk_control, rk_forloop, rk_gather, rk_range_for, rk_for_array*, rk_junctions/nest/prec, rk_re33/34/35/38,
  rk_reverse, rk_array_literal, rk_arrays, rk_strings, rk_str22, rk_map_grep_sort24 ~17) are the matchable set.
  Rule needed like the oracle-crash SKIP list.
- [ ] **NEXT CONSTRUCTS** for the ~16 remaining single-sub DIFFERs: `my $x=expr` (TT_ASSIGN/DECL value-ring,
  not yet handled), for/while (TT_FOR_RANGE/TT_WHILE), string interp, junctions (TT_ALT), regex. NOTE rk_join
  has an oracle ival QUIRK (join ival=2 vs 4 for structurally identical calls) — likely unmatchable, defer.

### Done-condition (Lon's "large portion of the test suites")
A tracked MATCH/total per suite in `scoreboard.sh` output. Target = large-portion, NOT 100% —
generators/suspend/full-pattern depth may legitimately lag. Lon sets the per-language bar.

BASELINE (SCRIP `a103ae7`, 2026-06-09, normalize=1): icon **6/8** · pascal **8/91** (SKIP 2; was 0 pre-dispatch-fix — .pas had mis-run lower_snobol4) ·
prolog[pl8] **0/7** (SKIP 1) · snobol4[sno153] **0/153** (SKIP 0) · snocone[sco191] **0/142**
(SKIP 49). NEWFAIL=0 everywhere — the four skeleton lowerers already emit a graph for every
oracle-parseable program, so this is pure SHAPE-correction, not crash-fixing. LEVER: SNOBOL +
Snocone = **295 scoreable through the single `lower_snobol4`** (Phase 3) vs 91 for Pascal
(Phase 2). Re-run any suite with `scripts/scoreboard.sh LANG` to refresh.

CURRENT (SCRIP `e5ee443`, 2026-06-10, normalize=1): icon **6/8** · pascal **89/93** (DIFFER 2: pcom ppp, SKIP 2; **CONVERTED**, m2 parity SAME=91 DIFF=0) · snobol4[sno153]
**147/153** (DIFFER 5, SKIP 1) · snocone[sco191] **142/142** (DIFFER 0, SKIP 49) · NEWFAIL=0 everywhere.
**ORACLE-CRASH SKIP LIST** now in `scoreboard.sh` (Lon ruling 2026-06-09): the OLD lower (`--dump-bb`)
SEGFAULTS partway through 7 programs, emitting a PARTIAL dump before crashing (so they scored DIFFER or
hid in the empty-oracle SKIP bucket). `oracle_crashes()` forces them to SKIP by path: `cross.sno`
(@N cursor-capture scan) + 6 B07 Snocone compound-assign (`+= -= *= /= ^=`). These are real OLD-lower
bugs, parked until the oracle is fixed.

## Watermark

**▶ HANDOFF (2026-06-10, Opus 4.8, Lon "convert this session") — THE CONVERSION BEGAN: ICON PRODUCTION
LOWERING IS NOW `lower_icon_nl` (default flipped); PASCAL CONVERTED (e5ee443, LAD-2c complete). SHAs: SCRIP
`a7842c6` (HEAD==origin/main, build GREEN rc=0, tree clean), .github THIS COMMIT. Six guarded-push rungs,
every gate held, zero regressions.**

  **THE HEADLINE FINDING — dump-byte MATCH ≠ execution parity.** `bb_print` HARDCODES the port α/β labels and
  prints NEITHER `IR_LIT.dval`, NOR `IR_EXEC.counter`, NOR the `operand_aux` side table — three INVISIBLE
  EXECUTION CHANNELS the interp dispatches on. A graph can be dump-byte-identical and still execute wrong
  (icon hello m2 was silent; fact(3)=12). The channels, decoded from the INTERP arms (the consumer = the
  legitimate spec; the old lower source stayed unread) + empirically from old graphs via the NEW
  `SCRIP_DUMP_X=1` env-guarded extended dump (scrip_ir.c bb_print; default dump bytes UNCHANGED; recurses
  CALL arg-blocks + GEN_SCAN blocks):
  - **CALL `IR_LIT.dval` taxonomy:** 1.0 = write/writes ring-chained args (`ag_ring_peek`); 2.0 = synthetic
    ops ([]/MAKELIST icon; arr_get/arr_set_pure/__pas_deref_set pascal) w/ arg-block array; 3.0 = all other
    named calls (frame model, generators, pascal static links) w/ arg-block array; 2.0/5.0 also = SNOBOL
    name-save/restore model. Arg blocks = `IR_graph_t **` in `IR_EXEC(call).counter`; each block = FAIL@0 +
    expr ring-chained + result γ=NULL (value falls out of IR_interp_once).
  - **BINOP `operand_aux`** (`bb_operand_aux_set(g, op, [lres,rres], 2)`): IR_RETURN RE-INTERPRETS its
    operand; without aux the re-run ring-peeks POST-ADVANCE stale values (fact(3): 2×6=12). Aux re-reads only
    VAR/KEYWORD fresh + uses cached CALL values. Relop BINOPs (ival 5–10) also carry dval=1.0.
  - **GEN_SCAN (icon `s ? e`):** dval=1.0, subject block → `IR_EXEC.counter`, body block → `IR_LIT.ival`
    (both arg-block convention). LAD-1c CLOSED — wordcount/meander matches are now execution-real.

  **THE MECHANISM (lower_program.c):** `nl_on(dflt)` reads `SCRIP_NL` (env overrides per-language compiled
  defaults); `g_nl_prog` root captured at lower_stage2 entry; `lower_icon_body`/`lower_pascal_body` route to
  `lower_*_proc` under the gate; `pas_rewrite_graph` is OLD-PATH-ONLY (NL graphs are already frame-aware;
  nslots still set). `scoreboard.sh` oracle leg pinned `SCRIP_NL=0` so --dump-bb-vs--dump-bb2 keeps meaning
  OLD-vs-NEW. `SCRIP_NL=0` is the full oracle escape hatch.

  **ICON = CONVERTED (default NL, `c3b1dbb`).** Gates: smoke m2 12/12 m3 10/12 m4 10/12 == old baseline
  (same 2 pre-existing m3/m4 emitter fails: proc_zeroarg/proc_recursion); icn corpus execution cross-check
  m2 7/8 + m3 6/6 SAME incl generators; scoreboard 6/8 NEWFAIL=0. queens (sole execution DIFF) is BROKEN ON
  BOTH ENGINES (old: 0 of 4 solutions; new: 1, garbled board) — LAD-1a, not a regression vector. Icon rungs
  also landed: bodiless `every f(gen)` (icx_t last_gen; expr-result γ loops to the inner generator, no
  fabricated SUCCEED), TT_UNTIL (WHILE w/ inverted cond: γ→exit, ω→body), TT_REPEAT (γ→body back-edge),
  TT_LOOP_BREAK (loop_exit ctx), `&`-prefix TT_VAR → IR_KEYWORD (mirrors FULL-13).

  **PASCAL = CONVERTED (default NL, `e5ee443`, 2026-06-10).** Eight rungs `41b7deb`→`e5ee443`: goto
  cluster (TT_LABEL_DEF scan, name = the node's OWN sval per the pascal parser; lower arm returns the
  LANDING so the preceding stmt chains to it, landing γ→child entry); framing rule (above); bool-chain
  (`__pbtN` materialization: parser desugars or→TT_ADD and→TT_MUL not-a→EQ(a,0); relop operands of
  arithmetic BINOPs spill per-operand as LIT1,LIT0,ASN_T,ASN_F,VAR + relop γ→LIT1 ω→LIT0; mats execute
  first, then ring reads; npbt counter program-global); resumable-ω fixup in lower_seq (anchor.ω →
  nearest PRECEDING resumable's anchor; **resumable = IF/UNLESS ONLY — loops EXHAUST on normal exit, a
  following stmt's failure resumes the ENCLOSING construct, never the completed loop** — read4/markrel/
  sieve diff-proved this scoping); case (parser desugars fully: __pct0 assign + IF-else chain, multi-label
  → NE(ADD(EQ,EQ),0) riding the pbt path; **statement-position nested TT_SEQ_EXPR FLATTENS — one CONJ for
  the outermost block only**); exec-channel fix (mixed-path BINOP aux must carry RESULT nodes not entry
  leaves — 3-label case arms read the leaf value, dump-invisible, caught ONLY by the m2 cross-check —
  char3). FLIP GATES (all green at `e5ee443`): full-corpus m2 old-vs-default SAME=91 DIFF=0 SKIP=2;
  scoreboards pascal 89/93 + icon 6/8 NEWFAIL=0 (oracle leg pinned SCRIP_NL=0); icon smoke m2 12/12 HARD
  m3 10/12 m4 10/12 == c3b1dbb baseline (m4 needs `make libscrip_rt` in fresh containers — artifact, not
  code); prolog smoke 5/5 HARD; sno smoke m4 7/7 HARD. Remaining pascal DIFFER: pcom, ppp (heavy tails;
  old path reachable via SCRIP_NL=0).

  **CONVERSION LADDER REMAINING:** (a) SNOBOL4 — NL WIRED + FULL m2 PARITY at SCRIP `3e7fed3`, FLIP NOT YET
  COMMITTED. `lower_sno_nl()` in lower_program.c gated `nl_on(0)` (SCRIP_NL=1 opt-in): registers main +
  DEFINE procs (sno_parse_define_proto, label-landing export lower_snobol4_label feeds bb_label_registry).
  Evidence at 3e7fed3: scripts/xcheck_sno_nl.sh **SAME=153/153 DIFF=0** (filters '^\[lower\]' diagnostic
  lines BOTH legs — old NARRATES punts, NL punts silently, program bytes identical — FLAGGED FOR LON);
  dump scoreboard sno **148/153** NEWFAIL=0 (test_case now graph-matches too); sno smoke **m2 7/7 m3 7/7**
  under SCRIP_NL=1 (m4 0/7 on BOTH legs — container toolchain, pre-existing, NOT conversion). REMAINING
  FLIP GATES: (i) beauty — from corpus/programs/snobol4/demo/beauty/ (cwd matters for -INCLUDE): NL leg
  RUNS self-beautify (md5 1c75f97d1907f92f4c0a8a3ef49eb9ee) but the OLD leg SEGFAULTS there in a fresh
  container — old can't establish the baseline; run scripts/test_gate_ec_uni_complete.sh (carries baseline
  md5 6bf2e9da…/882524B + drifted M1 oracle abfd19a7…) under both legs and judge; FLAG the old-leg segv for
  Lon. (ii) snocone scoreboard re-run (shares lower_snobol4). (iii) icon/pascal/prolog smoke holds. Then
  flip `nl_on(0)`→`nl_on(1)` in lower_sno_nl and commit. EXECUTION-CHANNEL CONTRACTS DECODED THIS PASS
  (dump-invisible; spec = interp arms + SCRIP_DUMP_X): IR_SEQ concat dval=1.0 ctr=LEFT argblk ival=RIGHT
  argblk; PAT_ARBNO ctr=bb_arbno_state_t* (IR_interp_state.h: inner=lower_pat_graph(child), cap=64,
  calloc'd pos_stack); positional dvals POS(var)=2.0 RPOS(var)=1.0 LEN(var)=1.0 TAB(var)=2.0 RTAB(var)=1.0;
  ω port sz=α (sno is α-UNIFORM like icon — m3/m4 emitters dispatch on sz); user-FNC-in-pattern = ORPHAN
  SCAN, stmt falls through ignoring :S/:F; literal-subject scan = LIT_S entry + FAIL+LIT_S subject block,
  SCAN sval empty; bare RETURN/FRETURN stmt = spine γ straight to PRET/PFRET landing, no node. GC HAZARD
  CLASS (rung 3 root cause): proc_table is plain-realloc — Boehm never scans it; anything stored there or
  in the plain-calloc exec[] sidecar must be plain strdup/calloc, NEVER lp_strdup/GC_MALLOC (old path
  survives on conservative false roots; NL layout shift exposed it as the roman APPLY_fn↔_usercall_hook
  infinite recursion). (b) snocone stays on shared lower_snobol4 — verify at flip; (c) raku (1/29) +
  prolog (0/7) stay OLD until their lowerers mature. Per-language defaults flip ONLY on execution-parity
  evidence, never on dump MATCH alone.

  **OPEN FOR LON (new):** (1) xcheck_sno_nl.sh '^\[lower\]' diagnostic-line filter — legitimate yardstick
  normalization or not (program output identical; only the old lower's UNHANDLED narration differs); (2) the
  OLD leg SEGFAULTS on beauty self-beautify from the beauty dir in a fresh container (NL leg runs fine) —
  pre-existing old-path bug, blocks old-vs-new beauty baseline; (3) sno smoke m4 0/7 on BOTH legs in fresh
  containers — toolchain artifact, not conversion; (4) icon/pascal NL lowerers calloc + exec-channel code
  200-char-wrapped but NOT style-swept; (5) SCRIP_DUMP_X recursion prints argblk/scan blocks — keep or fold
  into LAD-0b ruling; (6) queens broken on the OLD engine too (0 solutions) — predates conversion.

  **METHOD THAT WORKED:** interp arm = the spec for invisible channels; SCRIP_DUMP_X probe of old graphs =
  the empirical oracle; fix; gate on EXECUTION suites old-vs-new (never dump alone); commit each green rung;
  flip a default only at full parity with regressions impossible.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude


**▶ HANDOFF (2026-06-09, Opus 4.8, Lon "Hand off") — LOWER REWRITE: SNOBOL4 130→147/153, DEFINE UNBLOCKED.
SHAs: SCRIP `e887217` (HEAD==origin/main, build GREEN rc=0, tree clean), .github THIS COMMIT. Seven
guarded-push rungs this session, NEWFAIL=0 every rung, snocone held 142/142 throughout, zero regressions.**

  **SCORES AT HANDOFF:** snobol4 **147/153** (DIFFER 5, SKIP 1) · snocone **142/142** · icon **6/8** ·
  pascal **12/91** · NEWFAIL=0. Full detail in `## NODE-EXACT CONVENTIONS` is unchanged; the per-rung
  story is in LAD-3c/3e/3f above; the current scores line is `CURRENT (SCRIP e887217 …)` under LADDER.

  **THE DEFINE UNBLOCK (the headline, SCRIP `a968d81`) — a FEATURE FIX, not the feared scrip.c contortion.**
  LAD-3e ("multi-proc DEFINE, BLOCKED on Lon") turned out to be a DUMP problem, not a lowering problem: the
  new `--dump-bb2` already produced the correct single whole-program graph. The OLD `--dump-bb` oracle was
  re-dumping that SAME graph once per DEFINE — each DEFINE shallow-copies the `IR_graph_t` (`*fg = *g` in
  `lower_program.c`), sharing the identical `all[]` node array, changing only `entry=`; the dump loop walked
  `proc_table` printing the shared graph N+1 times. Lon directed: make `--dump-bb` a LINEAR SEQUENCE. FIX =
  dedup the dump loop by shared node-array pointer (`->all`), printing each DISTINCT graph once; Icon/Pascal
  (real distinct per-proc graphs) untouched; `--dump-bb2` fall-through now prints the matching `; proc main`.
  All 8 `functions/*` flipped MATCH (130→138). NOTE scrip.c was edited — but ONLY the dump-feature loop.

  **THE OTHER SIX RUNGS (all one-shot diff→fix→commit, sno 138→147):** `f2c983c` capture 060 — spurious 2nd
  PAT_CAT; the `lc_is_capture` branch needed the same `need_cat`-guard the `rc_is_capture` branch had (138→139).
  `2aaafce` pattern replacement 062/063 — `has_eq` + `TT_SCAN` subject emits SCAN `ival=1` + 3 sub-graphs
  (pattern/subject/NEW replacement via `lower_repl_graph`), replacement value as entry leaf; empty-replacement
  deletion shares it (139→143). `95179f8` 1015_opsyn — orphan CALL when an arg is `TT_OPSYN` (opsyn-redefined
  operator), same rule as TT_IDX/TT_INDIRECT complex-arg (143→144). `b592a59` bare `TT_IDX` stmt subject punts
  to NULL — was hitting `lower_expr`'s SUCCEED default and emitting a spurious node; fixes 1112+1110 (144→146).
  `9805ee8` 1013_func_nreturn — `TT_NAME` RHS (`.var` name-of) → `ASSIGN_VAR` + empty-name VAR (no UNOP), AND
  NULL-body label chains to `nxt` not the success-goto target (only unconditional `:go` honored) (146→147).
  `e887217` scoreboard oracle-crash SKIP list (Lon ruling) — no lowering touched.

  **REMAINING 5 sno DIFFERs (the heavy tail, all 65–289 diff lines = multi-fix rungs, see LAD-3f):**
  `1016_eval`, `expr_eval` (likely shares the eval builtin), `100_roman_numeral`, `library/test_case`,
  `coverage/coverage_sno_nodes`. Unlike this session's one-shot fixes, expect each to need several.

  **OPEN FOR LON (carried + new):** (1) LAD-0b pointer-ival ruling — `scoreboard.sh`'s `ival≥7-digit→PTR` sed
  is load-bearing (`--raw` drops icon 6→4); still needs sign-off + a named in-repo flag. (2) **NEW — 7 OLD-LOWER
  ORACLE CRASHES** now parked in the scoreboard SKIP list (`cross.sno` + 6 B07 Snocone compound-assign): real
  segfaults in `--dump-bb`; if execution-trusted coverage there is wanted, the OLD lower needs fixing. (3)
  `--dump-ast` segfaults on ALL multi-proc Pascal (pre-existing AST-printer bug, not the lowering path). (4)
  Icon/Pascal/SNOBOL lowerers use plain switch + inline field tests, NOT the prescribed pmatch gauntlet
  (aspirational vs working reference). (5) LAD-0c — `--dump-bb2` is dump-only, no execution validation. (6)
  TT_SCAN sub-graph is node-only for execution. (7) the icon/pascal/prolog/raku 200-char wrap (carried,
  mechanical) — `lower_snobol4_nl.c` re-verified 0 lines >200 this session (including all rungs above).

  **NEXT-RUNG OPTIONS (by leverage):** (a) LAD-3f `1016_eval`/`expr_eval` (the eval builtin — likely one
  mechanism unlocks two programs); (b) LAD-2c Pascal control flow (if/while/for/repeat/case + VAR_FRAME +
  nested-operand BINOP) — Pascal is at 12/91, the biggest headroom; (c) LAD-1a Icon queens; (d) the
  icon/pascal/prolog/raku 200-char wrap (clears the carried mechanical task).

  **METHOD (held all session):** `--dump-bb` oracle vs `--dump-bb2` new → normalized diff (`ival=PTR`) → fix
  FIRST divergence → rebuild (isolate `make` in its own command) → re-diff → COMMIT each green rung + guarded
  push. Reproduce oracle BYTES; never theorize past them; never read the OLD lower source. When the oracle
  itself crashes (cross/B07), do NOT chase it — SKIP and flag for Lon.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude


**▶ HANDOFF (2026-06-09, Opus 4.8, Lon "Hand off") — LOWER REWRITE: SNOCONE CLEAN SWEEP 0→142/142 +
SNOBOL4 120→121. SHAs: SCRIP `7d326de` (HEAD==origin/main, build GREEN rc=0, tree clean), .github THIS
COMMIT. Eight guarded-push rungs this session, NEWFAIL=0 every rung, zero regressions to icon/pascal.**

  **SCORES AT HANDOFF:** snobol4 **121/153** · snocone **142/142 (DIFFER=0)** · icon **6/8** · pascal
  **12/91** · NEWFAIL=0 everywhere. (snocone shares `lower_snobol4` — held at 142 through every later edit.)

  **THE SNOCONE 0→142 STORY (7 rungs, all detail in LAD-3d above):** root cause it was 0 — the Snocone
  parser emits a DIFFERENT AST than SNOBOL4 (TT_ASSIGN / TT_IF / TT_WHILE, not `:eq`/gotos), so the
  SNOBOL-shaped lowerer produced nothing. `5a8968c` TT_ASSIGN→lower_assign (0→66) · `318a21b` control-flow
  punts (66→78) · `9ba0670` IF/WHILE orphan nodes + WHILE lowers its condition (78→135, the big unlock) ·
  `41c29b3` WHILE-SCAN condition→bare orphan SCAN (135→136) · `3f1669e` VLIST RHS→orphan ASSIGN + WHILE-
  assign condition (136→140) · `ec424e4` TT_SEQ subj→orphan IR_SEQ (140→141) · `fbdd37f` TT_ALT-of-literals
  →DTP_ASSIGN+PATTERN_ALT (141→142 CLEAN SWEEP). The diff→fix→commit discipline held throughout.

  **THE SNOBOL4 PATTERN RUNG (`7d326de`):** capture backtrack-ω → preceding deterministic-consumer element
  (fixes 046_pat_tab). The COMPLETE backtrack rule + the two blockers that stop the general threading are
  written into LAD-3c above — that is the highest-value next-session spec: implement the `lower_pat_node`
  TAIL out-param (concatenation is left-associative) + the left-side-capture `PAT_CAT` insertion, gate on
  `IR_PAT_POS` alone (RPOS shares it). Verified rule unblocks 048/052/054/055 and contributes to 049.

  ⛔ **CARRIED-FORWARD TASK (NOT done this session, predates it — see the `2c3e466` block below):** the code
  one-liners in the OTHER FOUR `_nl` files (icon/pascal/prolog/raku) still exceed the 200-char line max and
  must be wrapped ≤200. `lower_snobol4_nl.c` IS clean (re-verified 0 lines >200 this session). The exact
  violator list in the `2c3e466` block may have shifted since the Sonnet SNOBOL work — RE-MEASURE per file
  before wrapping. WRAP STYLE + verify-whitespace-only procedure unchanged (in that block).

  **OPEN FOR LON (carried):** (1) LAD-0b pointer-ival ruling — `scoreboard.sh`'s `ival≥7-digit→PTR` sed is
  load-bearing (`--raw` drops icon 6→4); needs sign-off + a named in-repo flag. (2) LAD-3e SNOBOL multi-proc
  DEFINE — how to expose >1 proc graph through the single-graph `--dump-bb2` path WITHOUT touching scrip.c
  (8 programs blocked). (3) `--dump-ast` segfaults on ALL multi-proc Pascal (pre-existing AST-printer bug,
  not the lowering path). (4) Icon/Pascal/SNOBOL lowerers use plain switch + inline field tests, NOT the
  prescribed pmatch tree-pattern gauntlet (aspirational vs the working reference style). (5) LAD-0c —
  `--dump-bb2` is dump-only, no execution validation; (6) TT_SCAN is a node-only stub for execution.

  **NEXT-RUNG OPTIONS (by leverage):** (a) LAD-3c general pattern backtrack threading (spec ready above —
  the deep core; unblocks ~4-5 pattern programs); (b) the icon/pascal/prolog/raku 200-char wrap (mechanical,
  safe, clears the carried task); (c) LAD-2c Pascal control flow (if/while/for/repeat/case + VAR_FRAME nested
  vars + nested-operand BINOP); (d) LAD-1a Icon queens (IR_VAR scope=global + generator procedures).

  **METHOD (held again this session):** `--dump-bb` oracle vs `--dump-bb2` new → normalized diff
  (`ival=PTR`) → fix FIRST divergence → rebuild (isolate `make` in its own command — dash aborts a whole
  line on a `<(...)` syntax error, silently skipping a bundled make) → re-diff → COMMIT each green rung +
  guarded push. Reproduce oracle BYTES; never theorize past them; never read the OLD lower source.


**▶ HANDOFF (2026-06-09, Opus 4.8, Lon "perform hand off") — C-STYLE: separators standardized to
200 chars total + RULES.md reconciled. SHAs: SCRIP `2c3e466` (HEAD==origin/main, build GREEN rc=0,
tree clean), .github THIS COMMIT. This turn resolved a 120-vs-200 separator conflict in the HQ docs:
GOAL-STYLE-200COL.md + the 2026-05-31 ground-zero purge established 200-char-total separators
tree-wide, but RULES.md line 59 had drifted to "120-char" and the five new-lower files (incl. the
Icon reference) sat at 120-dash/124-char separators. Lon ruled 200 official + consistent everywhere.
LANDED: (1) SCRIP `2c3e466` — normalized every `/*---*/`/`/*===*/` line in src/lower/nl/*.c to
exactly 200 chars (`/*` + 196 + `*/`); 80 ins / 80 del, 100% separator lines, ZERO code touched;
build GREEN, intparam.pas still EXACT MATCH, pascal 12/91, icon 6/8, NEWFAIL=0 (unchanged —
comment-only). (2) .github THIS COMMIT — RULES.md line 59 now reads "200 chars total". ⛔ NEXT TASK
(session interrupted mid-measure, NOT started): the code one-liners in the five new-lower files
exceed the 200-CHAR line max and must be wrapped to ≤200 (Lon: "the new lower_*.c should follow the
200 max line rule"). MEASURE CHARACTERS NOT BYTES (γ/α/β/ω are 2 bytes each; the 2026-05-31 precedent
tolerates slight byte-overflow from Greek — but these lines exceed 200 in CHARS too). EXACT >200-char
violator list (already measured, don't re-measure): icon lines
13,15,17,21,23,25,53,62,68,76,80,81,83,90,182 (15); pascal 7,17,19,21,23,42,44,46 (8); prolog
7,23,25 (3); raku 7,23,25,120 (4); snobol4 7,23,25,139,140 (5). WRAP STYLE: split at top-level
`;`/`case`/`{`/`}` boundaries, 4-space body indent, pack short statements up to ≤200, zero blank
lines, NEVER split a string literal, match the existing multi-line fns in the same files
(lower_while/lower_if/lower_proc_body in icon). VERIFY per file: the change is WHITESPACE-ONLY (token
stream identical), build GREEN, scores unchanged (icon 6/8, pascal 12/91, NEWFAIL=0), then re-run the
python char-count check → 0 lines >200. These are the PROVEN reference + working files; a misplaced
newline breaks them. THEN the ladder fork stands: (a) LAD-2c Pascal control flow
(if/while/for/repeat/case) + the VAR_FRAME frame-variable layer & nested-operand BINOP nestfunc/ppp
need; (b) LAD-3a SNOBOL goal-directed rewrite (the 295-program lever). OPEN FOR LON: (1) LAD-0b
pointer-ival ruling — `--raw` drops icon 6→4, normalization load-bearing; (2) Pascal-vs-SNOBOL order;
(3) `--dump-ast` segfaults on ALL multi-proc pascal (procedure-only too) — pre-existing AST-printer
bug, not in the lowering path; (4) Icon/Pascal use plain switch + inline field tests, not the
prescribed pmatch gauntlet. Method: oracle vs new → diff → fix first divergence → rebuild → commit
each green rung + guarded push.**

**▶ HANDOFF (2026-06-09, Opus 4.8, Lon "your choice / continue") — LOWER REWRITE: Pascal LAD-2b′
(multi-proc + function bodies) landed green. SHAs: SCRIP `e4833e2` (HEAD==origin/main, build GREEN
rc=0, tree clean), .github THIS COMMIT. ONE pushed rung this session. The parser flattens all
procs/functions into a single top-level TT_STMT list (g_pascal_procs) in bottom-up reduction order =
the oracle's post-order (nested/earlier first, program LAST and named "main" by the parser, so
naming = pd->v.sval, no special-case like Icon). lower_pascal_enum iterates that list;
lower_pascal_proc lowers one body (SUCCEED@0/FAIL@1); is_function ⟺ c[3]==TT_VAR → synthesized
RETURN(γ→SUCCEED, ω→SUCCEED) ops:[bare VAR funcname], body threaded succ=RETURN; BINOP carries NO
ival (operands leaf-chain on the γ-ring); function-result LHS is a 0-arg TT_FNC (mk_ident returns a
call for known function names) so ASSIGN sval falls back to lhs->c[0]->v.sval. scrip.c is_pascal
--dump-bb2 arm now mirrors the Icon enum + "; proc" loop. SCORE: **pascal 8→12/91** (new:
forward1/intparam/m4asg/m4wexpr), icon held **6/8**, NEWFAIL=0 everywhere. Gate intparam.pas: EXACT
MATCH. NEXT RUNG OPTIONS: (a) Pascal LAD-2c control flow (if/while/for/repeat/case) + the VAR_FRAME
frame-variable layer and nested-operand BINOP that nestfunc/ppp now need; (b) Phase 3 SNOBOL LAD-3a
— the 295-program two-suite lever (highest leverage). OPEN FOR LON: (1) LAD-0b pointer-ival ruling —
`--raw` drops icon 6→4, normalization is load-bearing; (2) Pascal-vs-SNOBOL ordering; (3) CORRECTION:
`--dump-ast` segfaults on ALL multi-proc pascal (not just nested fns) — pre-existing AST-printer bug,
not in the lowering path; (4) the Icon & Pascal lowerers use plain switch + inline field tests, NOT
the prescribed pmatch tree-pattern gauntlet — the gauntlet design is aspirational vs the working
reference style. Method that worked again: oracle vs new → diff → fix first divergence → rebuild →
commit each green rung + guarded push.**

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

**▶ HANDOFF (2026-06-09, Sonnet 4.6, Lon "Continue") — LOWER REWRITE: LAD-3c pattern cluster landed; snobol4 121→130/153; snocone 142 held; icon 6 held; NEWFAIL=0. SHA: SCRIP `2354a73` (HEAD==origin/main, build GREEN rc=0, tree clean), .github THIS COMMIT.**

**COMMITS THIS SESSION (one guarded push, NEWFAIL=0):**
- `2354a73` LAD-3c patterns: PAT_ALT n-way chain (TT_ALT flattened left-recursively, right-to-left alloc, intermediate γ→final_alt); FAIL builtin → IR_FAIL (not PAT_DEFER); capture backtrack-ω: rc.ω→le_tail if consumer or capture operand; chained captures share single PAT_CAT (need_cat fires only when succ==pg->all[0]); lc_has_capture path: pre-alloc PAT_CAT, lower rc with succ=PAT_CAT, lower lc with succ=rc_entry, backtrack-ω via le_tail operand; lower_assign TT_ALT: flatten nested ALT tree, interleaved PATTERN_LIT+PATTERN_ALT alloc, intermediate ALT γ→next literal. NEW MATCHES: 048 REM.V, 049 ARB.V, 050/051 ALT 2/3-way, 052/054 ARBNO+RPOS, 053 P=alt value-assign, 055 chained captures, 057 FAIL. **sno 121→130/153**.

**SCORES AT HANDOFF:** snobol4 **130/153** · snocone **142/142** · icon **6/8** · pascal **12/91** · NEWFAIL=0 everywhere.

**REMAINING 23 DIFFERs (updated clusters):**
- functions: 8 — DEFINE multi-proc (LAD-3e, blocked on Lon's API ruling)
- capture: 3 — 060/062/063 (complex multiple-capture backtracking)
- strings: 2 — cross/wordcount (complex SCAN with capture)
- rung10: 3 — 1013/1015/1016
- rung11: 2 — 1110/1112 arrays
- keywords: 1 — 100_roman_numeral
- library: 2 — test_case/test_stack
- control: 1 — expr_eval
- coverage: 1 — coverage_sno_nodes

**NEXT-RUNG OPTIONS:** (a) LAD-3c remaining — capture 060/062/063 (multiple captures, complex backtrack ω chain); (b) LAD-2c Pascal control flow; (c) LAD-1a Icon queens (scope=global + generator procs).

**▶ HANDOFF (2026-06-09, Sonnet 4.6, Lon "perform hand off") — LOWER REWRITE: SNOBOL4 LAD-3a through LAD-3h complete; sno153 climbed 0→120/153, NEWFAIL=0 throughout. SHAs: SCRIP `1d3f6c2` (HEAD==origin/main, build GREEN rc=0, tree clean), .github THIS COMMIT.**

**COMMITS THIS SESSION (all on origin/main, guarded fast-forward, NEWFAIL=0 every rung):**
- `bd1e868` LAD-3a: complete goal-directed `lower_snobol4_nl.c` rewrite. Oracle graph structure decoded from `--dump-bb` (n=4+N prefix nodes + N SUCCEED labels + body nodes; entry=label[0]). AST structure decoded from `stmt_ast.c` (TT_GOTO_S/F/U direct children, TT_ATTR for `:subj`/`:repl`/`:eq`/`:lbl`). Implemented: ASSIGN_LIT_S/I, ASSIGN_VAR, ASSIGN (complex expr), BINOP, UNOP, CALL (FNC), SCAN stub, label→SUCCEED map, END-marker filtering. **sno 0→22/153.**
- `6889e92` LAD-3b (batch 1): BINOP ival via `sno_binop_code()` (same codes as Icon: ADD=0 SUB=1...); TT_FNC name from `t->v.sval` not `c[0]` (SNOBOL4 FNC stores name in node sval, all children are args); TT_SEQ concat: constant-fold all-TT_QLIT → `ASSIGN_CONCAT + LIT_S("combined")`, else `ASSIGN_CONCAT + IR_SEQ(ival=100000000LL → normalizes PTR)`; non-VAR LHS guard (indirect/indirect assigns → NULL body → label chains nxt). **sno 22→61/153.**
- `b28440b` LAD-3b (batch 2): `ASSIGN_CALL + CALL` when RHS is TT_FNC (oracle uses IR_ASSIGN_CALL not IR_ASSIGN for function-call RHS); unknown label → NULL fallback → nxt (lowercase "freturn" not in label map → chains to next stmt, not PSUCC); TT_KEYWORD LHS → lower_assign handles it; SCAN sub-graph lowering: `bb_print` recursively prints SCAN sub-graphs via `IR_EXEC(bb).counter` (pattern graph ptr) and `bb->operands[0]` (subject graph ptr) — built PAT_LIT/PAT_DEFER/PAT_*  sub-graphs + subject FAIL+VAR sub-graph, main graph gets SCAN+VAR entry chain. **sno 61→88/153.**
- `6d619b1` LAD-3c: TT_FLIT → plain `IR_ASSIGN` (not IR_ASSIGN_LIT_I); orphan CALL when any arg is TT_IDX/TT_INDIRECT (oracle allocates CALL with γ=·, ω=·; label chains nxt — confirmed from `differ(t<"cat">)` vs `GT(N,5)` comparison); TT_IDX as assignment RHS → orphan IR_ASSIGN + return NULL. **sno 88→99/153.**
- `1916489` LAD-3d: split `lower_assign` to take separate γ/ω targets (for `:goF DONE` threading, ASSIGN.ω → DONE label, not nxt); KEYWORD LHS (`&TRIM=1`) uses IR_ASSIGN not IR_ASSIGN_LIT_I/S. **sno 99→104/153.**
- `1497f6c` LAD-3e: `PAT_ASSIGN_COND` / `PAT_ASSIGN_IMM` via `ir_operand_push(nd, child_entry)` — entry=nd (the capture node itself), child pattern lowered and pushed as `ops:[idx]` operand (oracle shows `ops:[3]` in dump); previously was returning child as entry (wrong). **sno 104→113/153.**
- `f27beba` LAD-3f: TT_SEQ in pattern context → no PAT_CAT (straight chain: left.γ→right entry); TT_VAR builtins in pattern ctx (REM→IR_PAT_REM, ARB→IR_PAT_ARB, FENCE→IR_PAT_FENCE, ABORT→IR_PAT_ABORT, BAL→IR_PAT_BAL); `sno_has_pat()` detector: pattern-containing TT_SEQ as assignment RHS → ORPHAN ASSIGN_CONCAT+SEQ (γ=·, ω=·), label chains nxt. **sno 113→115/153.**
- `26abcea` LAD-3g: PAT_CAT inserted before TT_SEQ right-child when that child is TT_CAPT_COND_ASGN/TT_CAPT_IMMED_ASGN — oracle allocates PAT_CAT FIRST (becomes index 2) as success continuation, PAT_ASSIGN_COND.γ→PAT_CAT (not directly to SUCCEED). **sno 115→117/153.**
- `1d3f6c2` LAD-3h: PAT_RTAB sval="r"; TT_DEFER node → IR_PAT_DEFER with child var name in sval + ival=1; TT_VAR/TT_KEYWORD children in TT_POS/TT_LEN/TT_TAB/TT_RPOS → use sval not ival (oracle stores var name for dynamic pos/len/tab args). **sno 117→120/153.**

**SCORES AT HANDOFF:** icon **6/8** · pascal **12/91** · snobol4 **120/153** · NEWFAIL=0.

**REMAINING 33 DIFFERs (by cluster):**
- patterns: 12 — complex backtracking in PAT_ASSIGN_COND.ω (oracle chains to another PAT node for retry, not FAIL); PAT_ALT sub-graph structure; PAT_CAT needed in non-SEQ contexts (049/052/054/057 class)
- functions: 8 — DEFINE functions need multi-proc emission (oracle emits separate `; proc funcname` graphs for each DEFINE body — `lower_snobol4` returns ONE graph currently)
- strings: 2 — word3/wordcount use complex SCAN with PAT_ASSIGN patterns (CAPT_COND_ASGN in SCAN subject/pattern)
- capture: 4 — multiple captures in one pattern (backtracking ω wiring between capture nodes)
- rung10: 3, rung11: 2 — `differ(prototype(ta), "2,2")` style CALL with TT_FNC first arg (currently connected — oracle also connects it, so something else is off)
- library: 2, keywords/coverage/control: 1 each

**KEY DISCOVERIES THIS SESSION:**
1. TT_STMT/AST structure: gotos are TT_GOTO_S/F/U direct children (label in c[0]->v.sval from make_goto_node); TT_FNC sval=function name, all children are args (n=nargs, not n-1 as in Icon).
2. Oracle SCAN sub-graph: `IR_EXEC(scan_node).counter = (int64_t)(intptr_t)pat_graph`; `scan_node.operands[0] = (IR_t*)(void*)subj_graph`. `bb_print` recurses both.
3. Orphan body pattern: when oracle can't lower inline (TT_IDX/INDIRECT args, pattern assignments), it allocates nodes with γ=·, ω=· and chains label to nxt — same n but different wiring.
4. PAT_ASSIGN_COND wiring: entry=PAT_ASSIGN_COND (not child), child goes in `ir_operand_push(nd, child_entry)` → shows as `ops:[idx]` in dump.
5. Separate γ/ω to lower_assign: for stmts with `:goF`, ASSIGN.ω ≠ nxt (failure goes to goF target; success goes to nxt).

**NEXT RUNG OPTIONS (ordered by leverage):**
1. **Multi-proc DEFINE emission** (8 functions programs): oracle emits one graph per DEFINE body with separate `; proc funcname` headers. `lower_snobol4` needs to return the HEAD of a linked structure, or the `--dump-bb2` path (scrip.c:1703) needs a `lower_snobol4_enum`+`lower_snobol4_proc` API (like Pascal/Icon). RULE: MUST NOT modify scrip.c — so the solution must be within the graph structure returned by `lower_snobol4` (linked list via operands? or multiple graphs stored as SCAN-style operands?). NOTE: scrip.c:1703 calls `lower_snobol4(ast_prog)` → `bb_print(g)` ONCE — so all proc graphs must be reachable from that one call. The oracle for snobol4 `--dump-bb` uses a different path (the oracle's `lower_snobol4.c` internal representation). The `--dump-bb2` path only prints one graph. OPEN QUESTION for Lon: how to expose multi-proc output through the `--dump-bb2` single-graph path?
2. **Complex PAT_ASSIGN_COND backtracking ω** (patterns cluster): oracle wires PAT_ASSIGN_COND.ω → a retry/fallback node (not FAIL). For `LEN(1) . FIRST  REM . LAST`, oracle has complex ω-chaining between capture nodes for SNOBOL4 backtracking semantics.
3. **PAT_ALT sub-graph** (patterns 050/051 class): oracle has n=6 for `'cat' | 'dog'` but mine n=4 — two extra nodes for the ALT structure.

**OPEN FOR LON:** (1) LAD-0b pointer-ival ruling (--raw drops icon 6→4; normalization is load-bearing; ival≥7-digit floor catches all heap pointers); (2) Multi-proc DEFINE API for `--dump-bb2` path; (3) Pre-existing: `--dump-ast` segfaults on all multi-proc Pascal (AST-printer bug, not lowering path); (4) Snocone/Rebus (sco191) not yet re-run — they share lower_snobol4 but were not measured this session.

**METHOD:** `--dump-bb` (oracle) vs `--dump-bb2` (new) → normalized diff (ival=PTR for 7+ digit ivals) → fix first divergence → rebuild → commit each green rung + push. Scoreboard `scripts/scoreboard.sh snobol4` gives authoritative MATCH/DIFFER/NEWFAIL counts.
