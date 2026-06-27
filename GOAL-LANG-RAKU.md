# GOAL-LANG-RAKU.md — Raku Frontend Ladder

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO AST WALKING IN MODES 2/3/4 — see RULES.md § "NO AST WALKING IN MODES 2, 3, OR 4"         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Sess 2026-05-15g removed all tree_t* dereferences from sm_interp.c (mode 2) and                ║
║  sm_jit_interp.c (mode 3). Stubs print [NO-AST] <opcode> on stderr.                              ║
║                                                                                                  ║
║  If a gate breaks with [NO-AST] FOO — write fresh SM/BB lowering for FOO.                       ║
║  Do NOT restore the AST-walking call.  Do NOT route through proc_table_call or any              ║
║  other back-door that hands a tree_t* to mode-2/3/4 code.                                       ║
║                                                                                                  ║
║  Mode 1 (`--run` standalone AST interp) is unchanged and remains the reference path.        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Done when:** Raku rung ladder reaches rung-30 under all three modes
(--run, --run, --run). gather/take maps cleanly to BB_PUMP.
Hash support, typed variables, and for-loop iteration complete.

**Cross-pollination:** Raku shares icn_proc_table and icn_call_proc with Icon.
Any fix to the ICN frame stack or BB_PUMP path immediately benefits Raku.
Raku's sub/return fix benefits interp.c E_RETURN used by all frontends.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
```

Gate after setup — run all four, all must pass:
```bash
bash /home/claude/SCRIP/scripts/test_smoke_raku.sh              # PASS=5  (hello/arith/var/while/concat)
bash /home/claude/SCRIP/scripts/test_raku_ir_rungs.sh           # PASS=29 (all rk_* fixtures, --run)
bash /home/claude/SCRIP/scripts/test_raku_ir_full_suite.sh      # PASS=29 per mode, all 3 modes
bash /home/claude/SCRIP/scripts/test_smoke_unified_broker.sh    # PASS=48 FAIL=0
```

Additional targeted scripts (run when working on specific subsystems):
```bash
bash /home/claude/SCRIP/scripts/test_raku_fileio.sh             # RK-38/39/56: open/slurp/lines/spurt/$*STDIN
bash /home/claude/SCRIP/scripts/test_crosscheck_raku.sh         # 3-mode divergence check
bash /home/claude/SCRIP/scripts/regenerate_parser_and_lexer_from_sources.sh  # after .y/.l edits
```

Rules:
- After every .y or .l edit: run regenerate_parser_and_lexer_from_sources.sh first, then build_scrip.sh.
- After every commit touching shared files (interp.c, ir.h, sm_lower.c, bb_broker.c):
  run test_smoke_unified_broker.sh before pushing.
- Never run ad-hoc shell commands for build/test — always use a script in scripts/.
- If a new test fixture is added, add a matching .expected file and verify it runs
  in test_raku_ir_rungs.sh (auto-discovered by glob).

---

## Architecture reminder

```
.raku → raku_compile() → CODE_t* [LANG_RAKU]  (no AST layer — FI-3 done)
    --run  → execute_program() → interp_eval() with ICN_CUR frame stack
                (Raku shares icn_proc_table + icn_call_proc with Icon)
    --run  → sm_lower() → SM_BB_PUMP per stmt → bb_broker(BB_PUMP)
    --run → sm_lower() → SM_BB_PUMP → sm_codegen() → sm_jit_run()

gather/take → E_SUSPEND box (icn_bb_suspend in icon_gen.c — shared with Icon)
for @arr -> $x → E_EVERY + E_BANG (icn_bb_every + icn_bb_bang — to be written)
```

---

## Rung ladder — all modes, x86

Current baseline: PASS=12 FAIL=0 --run (rk_hello through rk_vars).
RK-16 is next per PLAN.md.

### Phase 1 — IR-run rung ladder

- [x] **RK-1 through RK-15** — PASS=12 --run. (done)

- [x] **RK-16** — `for @arr -> $x` real array iteration.
  E_ITERATE extended in icn_drive (icn_runtime.c): detects loop variable name
  stored in E_ITERATE->sval (set by raku.y grammar action), splits SOH-delimited
  array string, binds each element to the frame slot via icn_scope_get.
  E_EVERY fixed in interp.c: sets body_root before calling icn_drive for
  non-E_TO generators. raku.tab.c regenerated from raku.y.
  Gate: rk_for_array PASS under --run. PASS=13 total.

- [x] **RK-17** — Hash `%h<key>` and `%h{$k}` full support.
  Added KW_EXISTS/KW_DELETE tokens + lexer rules. VAR_HASH as standalone expr.
  exists %h<k> / delete %h<k> grammar rules. hash_pairs and hash_delete in
  interp.c. Gate: rk_hash17 PASS, test_raku_ir_rungs PASS=14 FAIL=0.

- [x] **RK-18** — Byrd box wiring + `given/when` smartmatch proper.
  **Root cause:** icn_drive() hand-rolls E_TO/E_TO_BY/E_ITERATE inline in C,
  bypassing the bb_broker/BB_PUMP Byrd box machinery that already exists in
  icon_gen.c. All generators must flow through bb_broker(BB_PUMP) to support
  --run, --run, and goal-directed backtracking.
  Sub-steps:
  - [x] RK-18a: icn_drive E_TO  → bb_broker(icn_bb_to, BB_PUMP, body_cb, &ctx)
  - [x] RK-18b: icn_drive E_TO_BY → bb_broker(icn_bb_to_by, BB_PUMP, body_cb, &ctx)
  - [x] RK-18c: icn_drive E_ITERATE → bb_broker(icn_bb_iterate, BB_PUMP, body_cb, &ctx)
  - [x] RK-18d: add icn_bb_smartmatch Byrd box in icon_gen.c; given/when uses it
  - [x] RK-18e: gate: smoke PASS=5, rungs PASS=14+, broker PASS=31
  Gate: all gates green after Byrd box refactor.

- [x] **RK-19** — Typed variables: `my Int $x`, `my Str $s`.
  Added 6 grammar rules to raku.y: typed scalar/array/hash with and without initialiser.
  Type annotation (IDENT token) consumed and free()'d at parse time — no IR change needed.
  raku.tab.c regenerated. Gate: rk_typed_vars PASS, test_raku_ir_rungs PASS=16 FAIL=0.

- [x] **RK-20** — `unless`, `until`, `repeat/until`.
  Added KW_UNLESS/KW_UNTIL/KW_REPEAT tokens to raku.l and raku.y.
  unless → E_IF(E_NOT(cond), body); until → E_UNTIL(cond, body);
  repeat → E_REPEAT(body) grammar wired (runtime test deferred — needs 'last').
  Gate: rk_unless_until PASS, test_raku_ir_rungs PASS=17 FAIL=0.

- [x] **RK-21** — `gather { take $_ for @list }` end-to-end.
  gather → anonymous proc __gather_N registered in icn_proc_table.
  E_ITERATE(E_FNC_call) in icn_eval_gen → icn_bb_suspend via icn_gather_trampoline
  (proc stored in ss->gather_proc, bypassing icn_coro_stage staging race).
  E_EVERY saves caller_depth before pump; body runs at caller_depth so
  E_VAR reads hit caller frame, not suspended coroutine frame.
  raku.tab.c/raku.lex.c regenerated. rk_gather.raku/.expected replaced with
  real gather/take test. Gate: PASS=17 smoke PASS=5 broker PASS=36. HEAD 915680ce.

- [x] **RK-22** — String ops: `substr`, `index`, `rindex`, `uc`, `lc`, `trim`, `chars`/`length`.
  Implemented in interp.c E_FNC dispatch block (same site as arr_get/hash_get).
  All ops use correct Raku semantics (0-based indexing, both-ends trim).
  INDEX/RINDEX written from scratch in C (no APPLY_fn equivalent).
  Gate: rk_str22 PASS, rungs PASS=18 FAIL=0, broker PASS=37. HEAD 08a5ef8a.

- [ ] **RK-23** — Regex basic: `$s ~~ /pattern/`.
  Maps to E_SCAN + pattern IR nodes (shared with SNOBOL4).
  Gate: basic regex match test PASS.

- [ ] **RK-24** — `map`, `grep`, `sort` list ops.
  Higher-order functions using E_FNC + BB_PUMP generators.
  Gate: map/grep/sort test PASS.

- [x] **RK-25** — `try`/`CATCH`/`die` exception handling.
  Lexer: "try","catch"/"CATCH","die" keywords. Grammar: try block and
  try block CATCH block as block-level stmts (no semicolon).
  Interp: g_raku_exception global; raku_die sets it; raku_try fires
  CATCH only when g_raku_exception non-empty (distinguishes real die
  from Icon fall-off-end FAILDESCR).
  Also fixed SN-6 build break: match_pattern_at stub in snobol4_stmt_rt.c.
  Gate: rk_try_catch25 PASS, rungs PASS=21 FAIL=0, broker PASS=40. HEAD 839ef99e.

- [x] **RK-26** — `class` / `method` / `new` basic OO.
  Raku OO maps to E_RECORD (class def) + E_FIELD (method call).
  Gate: basic class test PASS. HEAD 99ce25fa.

- [x] **RK-27** — Write `scripts/test_raku_ir_full_suite.sh`.
  Runs all RK-1 through RK-26 tests in all 3 modes.
  Gate: PASS=22 FAIL=0 per mode, all three modes. ✅

### Phase 2 — SM-run (BB_PUMP, x86)

- [x] **RK-28** — rk_hello through rk_vars under --run.
  Gate: PASS=22 FAIL=0. ✅ (covered by test_raku_ir_full_suite.sh)

- [x] **RK-29** — RK-16 through RK-24 under --run.
  Gate: all rungs passing under --run also pass under --run. ✅

### Phase 3 — JIT-run (x86 in-memory)

- [x] **RK-30** — rk_hello through rk_vars under --run.
  Gate: PASS=22 FAIL=0. ✅ (covered by test_raku_ir_full_suite.sh)

- [x] **RK-31** — RK-16 through RK-24 under --run.
  Gate: all diffs vs --run empty. ✅

### Phase 4 — BB-native RE engine (NFA simulation)

  **Architecture: BB-native NFA, not PCRE2 for the core.**
  Classical RE (no backrefs, no code assertions) → NFA → parallel BB_PUMP simulation.
  Each NFA state is a BB box. Epsilon transitions = BB_PUMP yields without consuming.
  Character transitions = BB_PUMP consumes one char, advances pos, or returns FAILDESCR.
  Parallel active-state-set = E_ALTERNATE over N active BB generators → O(n) match.
  PCRE2 kept as fallback only for `regex` keyword (full backtracking, code assertions).
  Lon has existing NFA/DFA C code — integrate as the compiler from pattern AST → NFA graph.

- [x] **RK-32** — RE compiler: pattern syntax → NFA state table.
  New file: raku_re.c / raku_re.h. Table-driven NFA (Thompson construction).
  Supports: literals, `.`, `\d\w\s\D\W\S`, `[cls]` with ranges and negation,
  `^`/`$` anchors (zero-width in epsilon-closure), `*`/`+`/`?` quantifiers,
  `|` alternation, `(...)` grouping. Nfa_state[] flat array with bb_id field
  reserved for Phase-3 BB lifter. raku_nfa_compile() builtin prints state count.
  Gate: rk_re32 PASS (states=4/4/5/4/4 for the five gate patterns). ✅

- [x] **RK-33** — NFA simulation: table-driven Thompson parallel active sets.
  raku_nfa_match() in raku_re.c: two State_set bitsets (cur/nxt), epsilon-closure
  with anchor-aware ss_add (BOL/EOL fire only at correct position), unanchored
  unless ^ present. raku_match interp.c dispatch upgraded from strstr to NFA.
  Gate: rk_re33 PASS (all patterns match/reject correctly). ✅

- [x] **RK-34** — Captures: `(...)` positional, `$0`, `$1`.
  NK_CAP_OPEN/NK_CAP_CLOSE states added to Nfa_state (cap_idx field).
  Cap_snap struct carries per-thread group_start/group_end through ss_add.
  raku_nfa_exec() does leftmost-longest: records best_end/best_snap across
  full active-set exhaustion (fixes early-exit bug where + exited after 1 char).
  VAR_CAPTURE token ($0/$1) added to raku.l/raku.y; raku_capture(n) builtin
  in interp.c slices g_raku_subject using g_raku_match group offsets.
  Gate: rk_re34 PASS ($0/$1 correct, two-group match correct). ✅

- [x] **RK-35** — Named captures `<n>` and `$<n>`.
  `<n>(...)` syntax parsed in raku_re.c parse_atom: collects name, assigns gidx,
  stores in nfa->group_name[gidx]. group_name[MAX_GROUPS][64] added to Raku_nfa.
  group_name copied to Raku_match at commit. raku_nfa_group_by_name() lookup.
  VAR_NAMED_CAPTURE token in raku.l: `$<n>` -> sval name.
  VAR_NAMED_CAPTURE rule in raku.y -> make_call("raku_named_capture", name).
  raku_named_capture(name) builtin in interp.c: linear scan of group_name[].
  Mix of named + positional groups in same pattern works correctly.
  Gate: rk_re35 PASS ($<word>/$<first>/$<last>/$<num> all correct). ✅

- [ ] **RK-36** — Code assertions inside RE: `{ }`, `<{ }>`, `<?{ }>`, `<!{ }>`, `<&sub>`.
  `{ code }` — unconditional side-effect at match pos; always succeeds.
    Maps to E_CAPT_COND_ASGN-style side-effect fired during NFA step.
  `<{ code }>` — predicate: evaluate code; fail NFA branch if false.
    Maps to E_INTERROGATE on NFA epsilon edge; kills that state on false.
  `<?{ code }>` — zero-width lookahead predicate (no pos advance).
  `<!{ code }>` — negative: E_NOT wrapping E_INTERROGATE.
  `<&sub>` — call named sub as rule; E_DEFER(E_FNC) at match time
    (pat_user_call infrastructure already in interp.c line 2627).
  When code assertions present: pattern falls back to BB-backtrack mode
  (NFA states with code edges run serially, not in parallel).
  Gate: rk_re36 PASS (all five forms fire correctly, predicate failure backtracks).

- [x] **RK-37** — Global match `m:g/pat/` and substitution `s/pat/repl/[g]`.
  LIT_MATCH_GLOBAL token (raku.l: m:g/ prefix sets raku_match_global flag).
  LIT_SUBST token: s/.../.../ lexed as "pat\x01repl\x01flag" single token.
  raku_match_global() builtin: NFA exec loop, collects SOH-delimited match list
  for for-loop iteration. raku_subst() builtin: single and global replace,
  updates frame variable in-place. Parser regen'd.
  Gate: rk_re37 PASS (global match yields all digits; single and global subst). ✅

### Phase 5 — File I/O

- [x] **RK-38** — Basic file I/O: `open`, `close`, `slurp`, `lines`.
  File handle table (RAKU_FH_MAX=64, indices 0/1/2 = stdio). open() returns INTVAL(idx).
  slurp(path|fh): fread whole file. lines(path|fh): SOH-delimited line list for for-loop.
  print($fh,str)/say($fh,str) grammar rules + raku_print_fh/raku_say_fh builtins.
  scripts/test_raku_fileio.sh: self-contained gate script.
  Gate: rk_fileio38 PASS. ✅

- [x] **RK-39** — `$*STDIN`, `$*STDOUT`, `$*STDERR` standard handles.
  Lex rules in raku.l: $*STDIN/$*STDOUT/$*STDERR → VAR_CAPTURE(0/1/2).
  raku_fh_ensure_init() pre-binds indices 0/1/2 to stdin/stdout/stderr.
  Gate: rk_stdio39 PASS (print/say to $*STDOUT/$*STDERR). ✅

### Phase 6 — BB-native Grammar machine (rule / token / regex)

  **Architecture: BB-native grammar — every rule/token/regex is a BB_PUMP proc.**
  Each `rule`/`token`/`regex` definition compiles to a named BB_PUMP proc registered
  in icn_proc_table. Signature: (subject_str, pos_int) → new_pos_int | FAILDESCR.
  This is identical to rk_combinator.raku — the combinator demo already proved the shape.

  Primitive matchers inside a rule body are BB boxes in raku_re.c:
    Literal `'foo'`      → bb_lit(subject, pos, "foo") — strncmp, advance or FAILDESCR
    Char class `<[a..z]>`→ bb_cls(subject, pos, range) — single char test
    `.` any char         → bb_dot(subject, pos) — advance 1 or FAILDESCR at end
    `\d`, `\w`, `\s`  → bb_cls variants
    `^` / `$`            → bb_anchor — zero-width, checks pos==0 or pos==len

  Quantifiers are BB_PUMP loops:
    `pat*` → bb_star: E_ALTERNATE(match | epsilon); `token` variant: possessive (no retry)
    `pat+` → bb_plus: match once then bb_star
    `pat?` → bb_opt:  E_ALTERNATE(match | epsilon)

  Alternation:
    `token`/`rule`: `||` ordered choice — try left; if FAILDESCR try right; done
    `regex`:        `|`  full E_ALTERNATE backtrack

  Subrule call `<rulename>`:
    Look up BB proc in icn_proc_table, call with (subject, pos).
    Result pos = new pos. Bind matched substring to `$/<rulename>`.

  `rule` implicit whitespace:
    Juxtaposition `a b` in a `rule` inserts `<.ws>` (bb_ws = `\s*` box) between terms.
    `token` juxtaposition: no implicit ws.

  `regex` full backtracking:
    Uses E_ALTERNATE retry chain — same as Icon/SNOBOL4 pattern backtracking.
    Code assertions `<{ }>` from Phase 4 active.

  Match object (`$/`):
    Hash DESCR_t: `$/[0]` = full matched substring, `$/<n>` = named subrule capture,
    `$/[n]` = positional group. Populated as each subrule call succeeds.

- [ ] **RK-40** — Grammar skeleton: keywords + BB proc registration.
  Lexer: KW_GRAMMAR / KW_RULE / KW_TOKEN / KW_REGEX in raku.l.
  Grammar (raku.y): `grammar Name { rule/token/regex Name { body } ... }`.
  Each definition lowers to a BB_PUMP proc registered in icn_proc_table as
  `"GrammarName::RuleName"`.
  Gate: grammar declaration parses and registers procs; no body execution yet.

- [ ] **RK-41** — Primitive BB boxes for rule bodies (new file: raku_re.c).
  Implement bb_lit, bb_cls, bb_dot, bb_anchor, bb_ws in raku_re.c.
  Wire into interp.c E_FNC dispatch under names `raku_bb_lit` etc.
  Gate: rk_grammar41 PASS (token matching literal strings and char classes).

- [ ] **RK-42** — Quantifier BB boxes: `*`, `+`, `?`.
  bb_star / bb_plus / bb_opt as BB_PUMP loops in raku_re.c.
  `token` variant: possessive (no retry after consuming input).
  `regex` variant: backtracking via E_ALTERNATE retry.
  Gate: rk_grammar42 PASS (quantifiers correct in token and regex modes).

- [ ] **RK-43** — Alternation and subrule calls `<rulename>`.
  `token`/`rule` ordered choice `||`: try left, FAILDESCR → try right, done.
  `regex` alternation `|`: full E_ALTERNATE backtrack.
  `<rulename>`: icn_proc_table lookup + call, bind `$/<rulename>`.
  Recursive rules: mutual recursion through icn_proc_table (no special handling).
  Gate: rk_grammar43 PASS (2+ mutually recursive rules, captures correct).

- [ ] **RK-44** — `token` vs `rule` vs `regex` full semantics.
  `token`: atomic, no backtrack within, no implicit ws.
  `rule`: `<.ws>` inserted between juxtaposed terms.
  `regex`: full backtracking, code assertions from Phase 4 active.
  Gate: rk_grammar44 PASS (same input, different results under token/rule/regex).

- [ ] **RK-45** — `grammar.parse($string)` and Match object.
  `MyGrammar.parse("input")` → call TOP rule BB proc with (subject, pos=0).
  Success: return Match object (hash DESCR_t, `$/` populated). Failure: return Nil.
  `$match<rulename>` → named sub-capture. `$match[0]` → full matched string.
  Gate: rk_grammar45 PASS (end-to-end parse of arithmetic grammar, captures correct).

- [ ] **RK-46** — Grammar actions: `{ code }` blocks in rules.
  `rule expr { <term> '+' <term> { make($<term>[0].ast + $<term>[1].ast) } }`
  `{ code }` after match → side-effect BB node, runs unconditionally.
  `make($value)` → sets `$/.ast` on current match object.
  Gate: rk_grammar46 PASS (grammar with actions builds AST via `make`).

### Phase 7 — Goal-directed features (all natural with BB_PUMP)

- [ ] **RK-47** — `last` / `next` / `redo` in loops.
  E_LOOP_BREAK and E_LOOP_NEXT already in ir.h — wire in raku.y and interp.c.
  `last` = break out of innermost `for`/`while`/`loop`.
  `next` = skip to next iteration (restart condition check).
  `redo` = restart loop body without re-evaluating condition or iterator.
  Gate: rk_loop_control47 PASS.

- [ ] **RK-48** — `first` — stop-at-first generator consumer.
  `first { pred } @list` → drive BB_PUMP until predicate true, return that element.
  Natural early-exit from E_EVERY — kill pump on first success.
  Gate: rk_first48 PASS.

- [ ] **RK-49** — Junctions: `any()`, `all()`, `one()`, `none()`.
  Goal-directed smartmatch over a set:
    `any(1,2,3) == 2` → E_ALTERNATE over elements, succeed on first match.
    `all(@list) > 0`  → E_EVERY, fail immediately on first non-match.
    `none(@list) == 0`→ E_EVERY, fail immediately on first match.
    `one(@list) == x` → E_EVERY counting matches, succeed only if count == 1.
  Gate: rk_junctions49 PASS (all four types, numeric and string predicates).

- [ ] **RK-50** — Lazy infinite lists and ranges.
  `(1..Inf)`, `(1, 3 ... *)` → E_TO_BY with sentinel upper bound (INTMAX).
  BB_PUMP demand-driven: only generates values as consumed by loop body.
  `(1..Inf).first({ $_ > 100 })` terminates correctly via early pump kill.
  Gate: rk_lazy50 PASS (infinite range, take first N, early termination).

- [ ] **RK-51** — `reduce` meta-operator `[op] @list`.
  `[+] @list`, `[*] @list`, `[max] @list` → fold over BB_PUMP generator.
  `[\+] @list` → triangle scan: yields intermediate partial results as new generator.
  Gate: rk_reduce51 PASS (sum, product, triangle scan).

- [ ] **RK-52** — `zip` and `roundrobin` multi-source generators.
  `zip(@a, @b)` → paired BB_PUMP: each pump pulls one from each source, yields pair.
  Stops when shortest source exhausts.
  `roundrobin(@a, @b, @c)` → cycles sources until all exhausted.
  Gate: rk_zip52 PASS.

- [ ] **RK-53** — `hyper` operators `>>.method` and `>>op<<`.
  `@list>>.uc` → map method over BB_PUMP elements, return new list.
  `@a >>+<< @b` → element-wise op on two equal-length lists via BB_PUMP.
  No new IR nodes needed.
  Gate: rk_hyper53 PASS.

- [ ] **RK-55** — `loop { }` bare infinite loop.
  Wire KW_LOOP in raku.l/raku.y → E_REPEAT (already in ir.h).
  `last` from RK-47 exits it. `next`/`redo` also apply.
  Gate: rk_loop55 PASS.

- [x] **RK-56** — `spurt($path, $content)` write-file shorthand.
  Implemented alongside RK-38: fopen/fputs/fclose in one call.
  Gate: covered by rk_fileio38 (spurt+slurp round-trip). ✅

- [ ] **RK-57** — `dir($path)` directory listing as BB_PUMP generator.
  Each pump yields one filename string via POSIX `readdir`.
  Natural `for dir('.') -> $f { say $f; }` loop.
  Gate: rk_dir57 PASS.

- [ ] **RK-58** — `flat` / `slip` list flattening.
  `flat(@nested)` → BB_PUMP that recurses into sub-lists, yields scalars.
  `slip(@a)` inside a list constructor flattens one level inline.
  Gate: rk_flat58 PASS.

- [ ] **RK-59** — `unique` / `squish` deduplication generators.
  `unique(@list)` → BB_PUMP with seen-hash filter; yields only first occurrence of each value.
  `squish(@list)` → yields only when value differs from previous (run-length dedup).
  Gate: rk_unique59 PASS.

- [ ] **RK-60** — `rotor($n)` and `batch($n)` chunking generators.
  `@list.rotor(3)` → BB_PUMP yielding N-element sublists; partial final chunk included.
  `batch($n)` = rotor but drops partial final chunk.
  Gate: rk_rotor60 PASS.

- [ ] **RK-61** — `pairs` iterator.
  `@arr.pairs` → BB_PUMP yielding (index => value) Pair objects.
  `%hash.pairs` → (key => value) Pair objects.
  Natural `for @arr.pairs -> $p { say "$p.key: $p.value"; }`.
  Gate: rk_pairs61 PASS.

- [ ] **RK-62** — `combinations($n)` and `permutations()` combinatoric generators.
  `@list.combinations(2)` → BB_PUMP over all k-element subsets in order.
  `@list.permutations` → BB_PUMP over all orderings.
  Each pump step advances the combinatoric cursor — pure GDE, no special runtime needed.
  Gate: rk_combgen62 PASS.

- [ ] **RK-63** — `multi sub` / `multi method` basic dispatch.
  Multiple subs with same name, different signatures — dispatch by arity first
  (type enforcement deferred to full type system).
  Stored as dispatch table in icn_proc_table keyed by `"name/arity"`.
  Gate: rk_multi63 PASS (dispatch by argument count correct).

- [ ] **RK-65** — `<rulename=other>` subrule alias syntax.
  `<name=otherrule>` inside a rule → call `otherrule` BB proc, bind result to `$/<name>`.
  Gate: rk_alias65 PASS (alias capture binds under correct name).

- [ ] **RK-66** — `$/` full Match object interface.
  `.Str` = matched substring. `.from` = start pos. `.to` = end pos.
  `.prematch` = subject before match. `.postmatch` = subject after match.
  Implemented as field accessors on the Match hash DESCR_t.
  Gate: rk_match_obj66 PASS (all five accessors correct).

- [ ] **RK-67** — `lazy` / `eager` adverbs on lists.
  `lazy @list` → wraps list in a demand-driven BB_PUMP (no evaluation until consumed).
  `eager @list` → forces full evaluation of a lazy list into a concrete array.
  Gate: rk_lazy_eager67 PASS (lazy defers work; eager forces it).

- [ ] **RK-68** — `produce` named triangle-scan generator.
  `produce &op, @list` → like `[\op] @list` but as a named builtin.
  Each pump yields the next partial result: produce(+, 1,2,3,4) → 1,3,6,10.
  Gate: rk_produce68 PASS.

- [ ] **RK-69** — Full suite update: `test_raku_ir_full_suite.sh` extended to RK-68.
  Gate: PASS=N FAIL=0 per mode, all three modes.
---

## Key files

| File | Role |
|------|------|
| `src/frontend/raku/raku.y` | Bison grammar |
| `src/frontend/raku/raku.l` | Flex lexer |
| `src/frontend/raku/raku_driver.c` | `raku_compile()` entry point |
| `src/frontend/icon/icon_gen.c` | Generator boxes — shared with Raku |
| `src/runtime/interp/icn_runtime.c` | Frame stack — shared with Raku |
| `scripts/test_raku_ir_rungs.sh` | Full rung sweep |

---

## Invariants

- Gate = PASS=31 FAIL=0 on test_smoke_unified_broker.sh after every commit.
- Never modify icn_proc_table layout — Icon shares it.
- Share generator boxes with Icon session — write once in icon_gen.c.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-16, SCRIP HEAD -- post RK-38/39/56)

RK-32 through RK-39 complete (RK-36 deferred). PASS=29 FAIL=0 all three modes.
Broker PASS=48 FAIL=0.
HEAD (SCRIP): dce09689

Session summary:
  RK-32: raku_re.c/raku_re.h -- Thompson NFA compiler, Nfa_state[] flat table.
  RK-33: raku_nfa_match() -- parallel active-set simulation, anchor-aware closure.
  RK-34: NK_CAP_OPEN/CLOSE, Cap_snap, leftmost-longest, VAR_CAPTURE, raku_capture().
  RK-35: <n>(...) named groups, VAR_NAMED_CAPTURE, raku_named_capture().
  RK-36: deferred -- NFA infra (NK_CODE_ASSERT/PRED/SUB_CALL) committed, executor skipped.
  RK-37: m:g/pat/ global match + s/pat/repl/[g] substitution.
  RK-38: open/close/slurp/lines, raku_fh_table, scripts/test_raku_fileio.sh.
  RK-39: $*STDIN/$*STDOUT/$*STDERR as handle indices 0/1/2, print/say($fh,str).
  RK-56: spurt(path,content) done alongside RK-38.
  Makefiles: both Makefile and src/Makefile updated with raku_re.c.
  Next: RK-47 -- last/next/redo loop control.

---

## --monitor: in-process sync comparator (IM-7/IM-8 complete)

`--monitor` runs IR, SM, and JIT step-by-step over the same program,
snapshot/restoring all mutable state between runs, and reports the first
statement where any two executors diverge.

```bash
./scrip --monitor file.sno    # SNOBOL4
./scrip --monitor file.icn    # Icon
./scrip --monitor file.pl     # Prolog
./scrip --monitor file.raku   # Raku
./scrip --monitor file.snc    # Snocone
./scrip --monitor file.reb    # Rebus
```

**On agreement:** prints per-stmt progress, exits 0.
**On divergence:** exits 1 and prints:
```
DIVERGE at stmt N [label: LABEL, line LL]
  IR   last_ok=?
  SM   last_ok=1
  JIT  last_ok=1
  IR vs SM (N var(s) differ):
    VARNAME    IR=<value>    SM=<value>
```

**Workflow for finding bugs:**
1. Run `./scrip --monitor suspect.sno` to find the first diverging statement.
2. The statement number + variable name pinpoint the root cause.
3. Fix in the appropriate layer (interp.c for IR bugs, sm_interp.c or
   sm_codegen.c for SM/JIT bugs).
4. Re-run `--monitor` to confirm divergence is gone.
5. Run `test_smoke_unified_broker.sh` — must stay PASS=31 FAIL=0.

**Note:** `--monitor` is incompatible with `--run`/`--run`
(it drives all three internally). ICN frame locals (IM-10) and Prolog trail
variables (IM-11) are not yet in the snapshot — coming in future IM steps.

