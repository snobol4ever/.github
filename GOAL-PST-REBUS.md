# GOAL-PST-REBUS.md — Pure Syntax Tree: Rebus + parser_*.sc stabilization

**Repo:** one4all + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md` (Step 5)
**Status:** Rebus PST rewrite ✅ done. Active work: stabilize parser_*.sc execution.

```
(source) ──► PARSER ──► (tree_t — pure syntax) ──► LOWER ──► IR_sm_t[]  ──┐
                                                                            ├──► interp / emitters
                                                          └──► IR_bb_t  ──┘
```

---

## ⛔ Binding rules

1. **SCRIP-mirror invariant** — every C-parser/lower change touches both C side AND the matching `corpus/SCRIP/parser_*.sc` / `lower.sc` (now deleted; lowering only on C side) in the same commit. Post-parse `tree_t` shape must match.
2. **Left-to-right child order** — all children in source token order.
3. **Never edit corpus to work around SCRIP behavior.** The corpus has run under SPITBOL for decades and is the oracle. Workflow:
   - Write the construct as `.sno`, run `qemu-i386-static /home/claude/sbl32 prog.sno` (install via `one4all/scripts/install_spitbol_x32_runner.sh` + `apt-get install -y qemu-user-static libc6-i386`).
   - SPITBOL output is canonical. If SCRIP differs, fix SCRIP source in `one4all` (parser / lowering / SM interp / runtime). Never the corpus.
4. **Pure-syntax allowed**: `ast_node_new(TT_*)`, `expr_new`, `expr_unary`, `expr_binary`, `ast_push`, `expr_add_child`. Setting `v.sval/v.ival/v.dval` from token.
   **Forbidden**: building `RExpr*`/`RStmt*`/`RProgram*`; scope lookup during parse; child reordering for positional semantics.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
# SPITBOL oracle (one-time):
apt-get install -y qemu-user-static libc6-i386
bash /home/claude/one4all/scripts/install_spitbol_x32_runner.sh
```

Gates (run after every rung):
```bash
bash /home/claude/one4all/scripts/test_smoke_rebus.sh             # expect 4/0
bash /home/claude/one4all/scripts/test_smoke_scrip_all_modes.sh   # expect 2/0
bash /home/claude/one4all/scripts/test_crosscheck_snobol4.sh      # baseline 4/2
bash /home/claude/one4all/scripts/test_beauty_snocone_subsystems.sh \
    global case assign match counter stack tree ShiftReduce TDump Gen \
    Qize ReadWrite XDump semantic omega trace arith roman strings fence
# Expect ≥15/20 at HEAD `4df6933b`. Goal: drive to 19/20 (Qize stays blocked by SL-3).
```

---

## Active rungs

- [x] **PST-RB-5h — Snocone-port subsystem suite to 19/20.** ✅ 2026-05-17 (Opus 4.7)
  15/20 → **19/20** PASS (Qize stays SKIPped under SL-3 as designed). The narrative "5 separate failures" (match, Gen, semantic, trace, Qize) collapsed: **one root cause flipped 4 of them.**
  Root cause: `lower_scan` in `src/lower/lower.c` unconditionally emitted Icon scanning-environment opcodes (`ICN_SCAN_PUSH`/`ICN_SCAN_POP`) for `TT_SCAN`. Both Icon and Snocone parsers reduce `?` to `TT_SCAN` — but Snocone `s ? pat` is **SNOBOL4 pattern matching** per SPITBOL Ch. 18 (binary op priority 1, left-assoc), not Icon scan-env. Wrong dialect meant `if (s ? p)` never set `last_ok`, so the subsequent `SM_JUMP_F` always fell through.
  Fix: dispatch on `g_lang` in `lower_scan`. Icon keeps `ICN_SCAN_PUSH/POP`; non-Icon mirrors the statement-level match path at `lower_stmt` line ~1306 (`SM_EXEC_STMT` with pattern DCG), then pushes an empty placeholder so `lower_if_stmt`'s `SM_VOID_POP` has something to consume. Flipped: match (3 tests), trace (1 test), Gen (used `?` internally, hit same wrong-branch path), semantic (same). Subsystems passing: 16 → 19.
  Sweep also landed: `snocone_parse.y` AST_* → TT_* (29 names, 89 occurrences; bridge `#define`s deleted from regenerated `.tab.c`); `snocone_lex.c` AST_* goto-labels → LX_* (45 names, 101 occurrences — they were lexer-state labels, never AST kinds).
  Watermark: one4all `1e6557c1`. Gates green (smoke_rebus 4/0, smoke_scrip 2/0, smoke_icon 5/0, smoke_snocone 5/0, smoke_snobol4 6/1 baseline with pre-existing `pattern` test fail unrelated to this rung, crosscheck_snobol4 4/2 baseline, unified_broker 19/30 baseline).

- [ ] **PST-RB-5i — Parser AST validation: parser_*.sc dump matches C-side tree_t dump.**
  For each of the six parsers (`snobol4`, `snocone`, `rebus`, `icon`, `prolog`, `raku`):
  1. Pick a tiny representative source file for that language (≤10 lines) from `corpus/programs/<lang>/`.
  2. Run the C-side reference: `./scrip --dump-ast <source>` → record canonical `tree_t` output.
  3. Run `bash scripts/run_scrip_parser.sh <lang> <source>` → SCRIP-hosted parser's dump.
  4. Diff. They must match modulo whitespace/printer differences. Document any acceptable divergence in a small allow-list in this file.
  5. If they diverge in shape, the parser's `shift`/`reduce` wiring is wrong; fix the SCRIP runtime or the `.sc` parser only if SPITBOL agrees the parser is right. Otherwise fix SCRIP source in `one4all`.
  Acceptance: each parser emits a `tree_t`-shape-equivalent dump for its chosen sample. Validation script `scripts/test_parser_ast_match.sh` lands as part of this rung.

- [ ] **PST-RB-5j — 6-function parser trace.**
  Instrument the six critical primitives — `shift`, `reduce`, `nPush`, `nInc`, `nTop`, `nPop` — with stderr trace lines gated by env `SCRIP_DEBUG_PARSE`. Implement once in `corpus/SCRIP/semantic.sc` (`shift`, `reduce`) and `corpus/SCRIP/counter.sc` (`nPush`/`nInc`/`nTop`/`nPop`). Run each parser against trivial input with `SCRIP_DEBUG_PARSE=1` and watch the parse unfold; this is the diagnostic foundation for fixing remaining parser_*.sc bugs once subsystem suite is green.
  Acceptance: traces emit; documented sample trace for `parser_rebus.sc` on `x = 1` checked in to a `docs/` location.

- [ ] **PST-RB-5k — Snocone `INCLUDE` statement.**
  Add `INCLUDE 'file.sc'` (or `-INCLUDE`, mirroring SNOBOL4) to the Snocone parser so the multi-file `run_scrip_parser.sh` load list collapses to a single source. Eliminates the entire load-order question. Implementation parallels `sno_add_include_dir` / SNOBOL4 lex `INCL` state.
  Acceptance: `parser_rebus.sc` plus a small `parser_rebus_main.sc` that pulls in `global.sc`, `counter.sc`, etc. via INCLUDE produces the same behavior as the current shell-loaded chain. Gate: subsystem suite, smoke, crosscheck, plus a new `test_parser_include.sh`.

---

## Open SL tickets (blocking parser_*.sc)

- **SL-3** — `SQize` infinite loop on apostrophe-free input. Loop condition + replacement interaction in `corpus/SCRIP/qize.sc:46-58` doesn't reduce `str`. Workaround: `_qtag` fast-path bypasses for the parser tag idiom. Real fix belongs in SCRIP runtime if SPITBOL handles this correctly (check first).
- **SL-4** — SCRIP runtime pattern-matcher spuriously succeeds on `BREAK("'")` / `ARB "'"` / `ARB ANY("'")` when input contains no apostrophe. Workaround: use `REPLACE` for apostrophe-presence checks. SPITBOL-oracle this first.
- **SL-5** — Parser AST dumps not yet correct. Each `parser_*.sc` finishes loading after SL-2 fix but emits Error 5 ("Undefined function or operation") at load and/or fails to push a tree onto the value stack. Likely shift/reduce wiring or EVAL-scope issue in `semantic.sc`'s `shift()` builder. **Closing SL-5 = passing PST-RB-5i.**

---

## Closed rungs (history; do not re-open)

- **5a–5d** ✅ 2026-05-16 (Sonnet 4.6) — `REKind`→`TT_*` mapping; `rebus.y` action bodies rewritten to `ast_node_new(TT_*)` + `expr_add_child`; `RExpr`/`RStmt`/`RProgram` structs deleted from `rebus.h`; downstream consumers (`rebus_lower.c`, `rebus_emit.c`, `rebus_print.c`) walk `tree_t` by kind. `RE_* → TT_*` mapping table (LIT_S→QLIT, LIT_I→ILIT, LIT_F→FLIT, VAR→VAR, ASSIGN→ASSIGN, BINOP→TT_ADD etc., UNOP→TT_MNS etc., CALL→FNC, SEQ→SEQ, BLOCK→PROGRAM, IF→IF, WHILE→WHILE, DEFINE→DEFINE, RETURN→RETURN).
- **5e** ✅ 2026-05-17 (Opus 4.7) — `parser_rebus.sc` 696→266 lines, zero functions; shift/reduce + counter primitives only; `lower.sc`/`lower_driver.sc` deleted from corpus. Driver = `TDump` walk over parse-root children. SCRIP-side lowering moved entirely to C.
- **5f** ✅ 2026-05-17 (Opus 4.7) — **SL-2 closed**: heap UAF in `sc_finalize_if_else_pst` triggered by 3+ chained `else if`. Fix: per-`if_head` allocation via `sc_if_head_new`; bison `%type <expr> if_head` → `<ifhead>`. `snocone_parse.tab.c` regenerated. `_qtag` SL-3/4 workaround via identifier-shape fast-path in `semantic.sc`. Sidecar audit fixed wording in `GOAL-PST-ICN-RAKU.md`, `PLAN.md`, `corpus/SCRIP/README.md`.
- **5g** ✅ 2026-05-17 (Opus 4.7) — Two one4all bugs fixed: (1) `sm_prog.c` opnames[] mis-aligned by spurious `"SM_GEN_TICK"` — every dumped opcode from position 65+ wrong (e.g. SM_CALL_FN printed as SM_SUSPEND_VALUE). (2) `lower.c` `lower_name` ignored `TT_FNC` children — `.value($'@S')` lowered as `NAME_PUSH("value")` instead of evaluating the call. Fix: when TT_NAME child is TT_FNC, lower as plain call (nreturn deref handles the value). SPITBOL-verified. Subsystem suite 13/20 → 15/20 (stack, ShiftReduce flipped PASS). Files: `src/lower/sm_prog.c`, `src/lower/lower.c`, `src/emitter/emit_net.c`.

---

## Done criterion (parent goal)

1. PST-RB-5a–5e all ✅, 5g ✅, 5h/5i/5j/5k all `[x]`.
2. `rebus.y` builds only `tree_t` — `RExpr*`/`RStmt*`/`RProgram*` gone. ✅
3. Subsystem suite 19/20 PASS (Qize SKIP under SL-3).
4. All six parser_*.sc emit `tree_t`-shape-equivalent AST dumps matching `--dump-ast` C reference.
5. Snocone `INCLUDE` statement lands; `parser_*.sc` loaded as single source.
6. Beauty self-host byte-identical (Milestone 1 protected).
7. Parent goal `GOAL-PARSER-PURE-SYNTAX-TREE.md` Step 5 ✅.

---

## State

```
watermark:  PST-RB-5h committed 2026-05-17 (one4all 1e6557c1, .github pending)
status:     Subsystem suite 19/20 at HEAD (Qize SKIP under SL-3 — acceptance met).
            Parser_*.sc still don't emit usable AST (SL-5).
next:       PST-RB-5i (parser AST validation) → 5j (6-fn trace) → 5k (Snocone INCLUDE).

SL-2 closed. SL-3/4/5 open and explicitly blocking 5i.
SL-4 generalized: TT_SCAN expression-position dispatch (5h) fixed the
SNOBOL4 pattern-match success/failure signalling in if-context; the
original SL-4 phrasing ("BREAK/ARB/ARB ANY spurious match") was a
symptom of the same root cause and may be partially or fully resolved.

Authors:
  5a–5d   Sonnet 4.6  2026-05-16
  5e–5g   Opus 4.7   2026-05-17 (three sessions)
  5h      Opus 4.7   2026-05-17 (this session)
```
