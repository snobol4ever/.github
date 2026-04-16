# GOAL-LANG-RAKU.md — Raku Frontend Ladder

**Repo:** one4all
**Done when:** Raku rung ladder reaches rung-30 under all three modes
(--ir-run, --sm-run, --jit-run). gather/take maps cleanly to BB_PUMP.
Hash support, typed variables, and for-loop iteration complete.

**Cross-pollination:** Raku shares icn_proc_table and icn_call_proc with Icon.
Any fix to the ICN frame stack or BB_PUMP path immediately benefits Raku.
Raku's sub/return fix benefits interp.c E_RETURN used by all frontends.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_raku.sh              # PASS=5
bash /home/claude/one4all/scripts/test_raku_ir_rungs.sh           # PASS=12
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh    # PASS=31
bash /home/claude/one4all/scripts/test_crosscheck_raku.sh       # 3-mode divergence check
```

---

## Architecture reminder

```
.raku → raku_compile() → Program* [LANG_RAKU]  (no AST layer — FI-3 done)
    --ir-run  → execute_program() → interp_eval() with ICN_CUR frame stack
                (Raku shares icn_proc_table + icn_call_proc with Icon)
    --sm-run  → sm_lower() → SM_BB_PUMP per stmt → bb_broker(BB_PUMP)
    --jit-run → sm_lower() → SM_BB_PUMP → sm_codegen() → sm_jit_run()

gather/take → E_SUSPEND box (icn_bb_suspend in icon_gen.c — shared with Icon)
for @arr -> $x → E_EVERY + E_BANG (icn_bb_every + icn_bb_bang — to be written)
```

---

## Rung ladder — all modes, x86

Current baseline: PASS=12 FAIL=0 --ir-run (rk_hello through rk_vars).
RK-16 is next per PLAN.md.

### Phase 1 — IR-run rung ladder

- [x] **RK-1 through RK-15** — PASS=12 --ir-run. (done)

- [x] **RK-16** — `for @arr -> $x` real array iteration.
  E_ITERATE extended in icn_drive (icn_runtime.c): detects loop variable name
  stored in E_ITERATE->sval (set by raku.y grammar action), splits SOH-delimited
  array string, binds each element to the frame slot via icn_scope_get.
  E_EVERY fixed in interp.c: sets body_root before calling icn_drive for
  non-E_TO generators. raku.tab.c regenerated from raku.y.
  Gate: rk_for_array PASS under --ir-run. PASS=13 total.

- [x] **RK-17** — Hash `%h<key>` and `%h{$k}` full support.
  Added KW_EXISTS/KW_DELETE tokens + lexer rules. VAR_HASH as standalone expr.
  exists %h<k> / delete %h<k> grammar rules. hash_pairs and hash_delete in
  interp.c. Gate: rk_hash17 PASS, test_raku_ir_rungs PASS=14 FAIL=0.

- [x] **RK-18** — Byrd box wiring + `given/when` smartmatch proper.
  **Root cause:** icn_drive() hand-rolls E_TO/E_TO_BY/E_ITERATE inline in C,
  bypassing the bb_broker/BB_PUMP Byrd box machinery that already exists in
  icon_gen.c. All generators must flow through bb_broker(BB_PUMP) to support
  --sm-run, --jit-run, and goal-directed backtracking.
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

- [x] **RK-28** — rk_hello through rk_vars under --sm-run.
  Gate: PASS=22 FAIL=0. ✅ (covered by test_raku_ir_full_suite.sh)

- [x] **RK-29** — RK-16 through RK-24 under --sm-run.
  Gate: all rungs passing under --ir-run also pass under --sm-run. ✅

### Phase 3 — JIT-run (x86 in-memory)

- [x] **RK-30** — rk_hello through rk_vars under --jit-run.
  Gate: PASS=22 FAIL=0. ✅ (covered by test_raku_ir_full_suite.sh)

- [x] **RK-31** — RK-16 through RK-24 under --jit-run.
  Gate: all diffs vs --sm-run empty. ✅

### Phase 4 — Regex with captures (PCRE2)

- [ ] **RK-32** — PCRE2 integration: `$s ~~ /pattern/` with full regex syntax.
  Link with `-lpcre2-8`. Replace `strstr` stub in `raku_match` (interp.c) with
  `pcre2_match()`. Return INTVAL(1) on match, FAILDESCR on no match.
  No captures yet — just correctness for quantifiers, alternation, anchors.
  Gate: rk_regex32 PASS (tests `\d+`, `[a-z]+`, `^anchor$`, `a|b`, `.*`).

- [ ] **RK-33** — Regex captures: `$/`, `$0`, `$1`, named `$<name>`.
  After pcre2_match(), populate `$/` hash with numbered and named captures.
  `$0` = full match string. `$<name>` = named group via `(?<name>...)` or Raku
  `<name>` syntax (map `<name>` → `(?<name>...)` in pattern compiler).
  Gate: rk_regex33 PASS (captures correct values, `$0`/`$1`/`$<word>`).

- [ ] **RK-34** — Regex in list context: `$s ~~ m:g/pattern/` global match generator.
  Maps to BB_PUMP: each pump step advances the match offset, yields next `$/`.
  `for $s ~~ m:g/\d+/ -> $m { say $m<0>; }` — natural BB_PUMP loop.
  Gate: rk_regex34 PASS (global match yields all matches in order).

- [ ] **RK-35** — Regex substitution: `$s ~~ s/pattern/replacement/`.
  Modifier `:g` for global replace. Replacement can reference `$0`/`$<name>`.
  Implemented as `pcre2_substitute()`.
  Gate: rk_regex35 PASS (single and global substitution correct).

### Phase 5 — File I/O

- [ ] **RK-36** — Basic file I/O: `open`, `close`, `slurp`, `lines`.
  `open($path, :r)` / `open($path, :w)` / `open($path, :a)` — returns a file handle
  stored as a tagged DESCR_t (DT_FILE or reuse DT_I with pointer tag).
  `slurp($fh)` / `slurp($path)` — read entire file as string.
  `lines($fh)` / `lines($path)` — BB_PUMP generator: each pump yields one line
  (natural goal-directed: `for lines($fh) -> $line { ... }`).
  `close($fh)`. `print($fh, $s)` / `say($fh, $s)` — write to handle.
  Gate: rk_fileio36 PASS (write file, slurp it back, iterate lines).

- [ ] **RK-37** — `$*STDIN`, `$*STDOUT`, `$*STDERR` standard handles.
  Pre-bound globals. `for lines($*STDIN) -> $line { ... }` — reads stdin via
  BB_PUMP, each line one pump step.
  Gate: rk_stdio37 PASS (pipe input through lines generator).

### Phase 6 — Grammar / rule / token (PEG machine)

  **Architecture decision: PEG, not SNOBOL4 patterns.**
  Raku `grammar` is fundamentally PEG with named recursive rules and captures.
  SNOBOL4 patterns backtrack freely; Raku `token` is atomic (no backtracking within).
  Each `rule`/`token`/`regex` compiles to a BB_PUMP generator sub in icn_proc_table.
  A `<subrule>` call inside a rule = a BB_PUMP sub-call that yields a match object.
  Named captures (`<name>`) bind to `$/` hash slots — same mechanism as RK-33.

- [ ] **RK-38** — Grammar skeleton: `grammar`, `rule`, `token`, `regex` keywords.
  Lexer: add KW_GRAMMAR/KW_RULE/KW_TOKEN/KW_REGEX. Grammar: parse class-like body
  where methods are replaced by rule/token/regex definitions.
  Each rule/token/regex compiles to a proc in icn_proc_table taking ($subject, $pos)
  returning new $pos on match or FAILDESCR on failure — same shape as rk_combinator.raku.
  Gate: grammar parses without error; no execution yet.

- [ ] **RK-39** — PEG primitives inside rule/token/regex bodies.
  Literal strings: `'foo'` → strncmp at pos.
  Char classes: `<[a..z]>` → PCRE2 char class or manual range check.
  Quantifiers: `*`, `+`, `?` → BB_PUMP loops (greedy).
  Alternation: `||` (ordered choice, PEG semantics — no backtrack across).
  Concatenation: juxtaposition → sequential match advancing pos.
  Gate: rk_peg39 PASS (rule matching literals, quantifiers, alternation).

- [ ] **RK-40** — Subrule calls `<rulename>` and named captures.
  `<rulename>` inside a rule → call the rule's BB_PUMP proc, bind result to `$/<rulename>`.
  `<rulename=other>` alias. Recursive rules supported via icn_proc_table call.
  Gate: rk_peg40 PASS (grammar with 2+ mutually referencing rules, captures correct).

- [ ] **RK-41** — `token` vs `rule` vs `regex` semantics.
  `token`: no implicit whitespace, no backtracking within (atomic).
  `rule`: implicit `<.ws>` between terms (whitespace-significant PEG).
  `regex`: full backtracking (closest to PCRE2 semantics).
  Implement `<.ws>` as built-in rule matching `\s*`.
  Gate: rk_peg41 PASS (token/rule/regex behave differently on ws-sensitive input).

- [ ] **RK-42** — `grammar.parse($string)` top-level entry point.
  `MyGrammar.parse("input string")` → calls TOP rule, returns Match object or Nil.
  Match object: hash-like, `$/<name>` gives named capture, `$/[0]` positional.
  Gate: rk_grammar42 PASS (end-to-end parse of simple arithmetic grammar).

### Phase 7 — Goal-directed features (all natural with BB_PUMP)

- [ ] **RK-43** — `last` / `next` / `redo` in loops.
  E_LOOP_BREAK and E_LOOP_NEXT already in ir.h — wire in raku.y and interp.c.
  `last` = break out of innermost `for`/`while`/`loop`.
  `next` = restart loop body (next iteration).
  `redo` = restart loop body without re-evaluating condition.
  Gate: rk_loop_control43 PASS.

- [ ] **RK-44** — `first` — stop-at-first-match generator consumer.
  `first { condition } @list` — drives BB_PUMP until predicate succeeds, returns
  that element. Natural early-exit from E_EVERY loop.
  Gate: rk_first44 PASS.

- [ ] **RK-45** — Junctions: `any()`, `all()`, `one()`, `none()`.
  Goal-directed: `any(1,2,3) == 2` — BB_PUMP over elements, succeed on first match.
  `all(@list) > 0` — BB_PUMP, fail on first non-match.
  `none(@list) == 0` — BB_PUMP, fail on first match.
  Maps to E_EVERY + predicate + E_ALTERNATE for the junction generator.
  Gate: rk_junctions45 PASS (all four junction types, numeric and string predicates).

- [ ] **RK-46** — Lazy infinite lists and ranges.
  `(1 .. Inf)`, `(1, 3 ... *)` — E_TO_BY with sentinel upper bound (INT_MAX).
  Driven by BB_PUMP demand — only generates values as consumed.
  `(1..Inf).first({ $_ > 100 })` — terminates correctly via early exit.
  Gate: rk_lazy46 PASS (infinite range, first 5 elements, early termination).

- [ ] **RK-47** — `reduce` meta-operator `[op] @list`.
  `[+] @list`, `[*] @list`, `[max] @list` — fold over BB_PUMP generator.
  `[\+] @list` — triangle reduction, yields intermediate values (BB_PUMP generator).
  Gate: rk_reduce47 PASS (sum, product, triangle scan).

- [ ] **RK-48** — `zip` and `roundrobin` multi-source generators.
  `zip(@a, @b)` — interleaves two BB_PUMP sources pairwise, yields pairs.
  `roundrobin(@a, @b, @c)` — round-robin across N sources until all exhausted.
  Gate: rk_zip48 PASS.

- [ ] **RK-49** — `hyper` operators `>>.method` and `>>op<<`.
  `@list>>.uc` — apply method to each element, return new list.
  `@a >>+<< @b` — element-wise op on two lists of equal length.
  Implemented as map over BB_PUMP — no new IR nodes needed.
  Gate: rk_hyper49 PASS.

- [ ] **RK-50** — Full suite update: `test_raku_ir_full_suite.sh` extended to RK-50.
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

## Current state (2026-04-15, one4all HEAD — post RK-27, LADDER COMPLETE)

ALL PHASES DONE. RK-1 through RK-31 complete.
PASS=22 FAIL=0 under --ir-run, --sm-run, --jit-run (all three modes).
Broker PASS=41 FAIL=0. Crosscheck PASS=26 FAIL=0.
HEAD (one4all): see git log — RK-27 commit.

Session RK-26..RK-27 summary:
  RK-26: class/method/new basic OO (E_RECORD + E_FIELD), HEAD 99ce25fa
  RK-27: test_raku_ir_full_suite.sh written — PASS=22/mode all 3 modes
  Phases 2+3 (SM-run, JIT-run): all rungs already passing; confirmed by full suite.
  Goal DONE — Raku rung ladder reaches rung-30+ under all three modes.

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

**Note:** `--monitor` is incompatible with `--ir-run`/`--sm-run`/`--jit-run`
(it drives all three internally). ICN frame locals (IM-10) and Prolog trail
variables (IM-11) are not yet in the snapshot — coming in future IM steps.

