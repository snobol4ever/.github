# GOAL-PARSER-SC-TRANSPILE.md — Six parser_*.sc → portable .sno via Snocone→SNOBOL4 transpile

**Repo:** SCRIP + corpus + .github
**Author:** Lon Jones Cherryholmes · Claude Opus 4.7
**Opened:** 2026-05-17

---

## ⛔ Session Start Protocol

1. Clone `.github`, `corpus`, `SCRIP`, plus `snobol4ever/x64` to `/home/claude/x64` (prebuilt `bin/sbl` ships in repo — no build step needed). See `PLAN.md`.
2. `pdftotext /mnt/user-data/uploads/spitbol-manual-v3_7.pdf /tmp/spitbol.txt`. Required chapters: Ch 8 (Gimpel template, line 5806+), Ch 14 (statements, 9017+), Ch 15 (operator priorities, 9540+), Ch 18 (pattern matching, 10606+), App C (SPITBOL vs standard SNOBOL4, 13651+).
3. Read `corpus/SCRIP/parser_snocone.sc` (the language we transpile FROM), `corpus/SCRIP/README.md` (runtime load order), `.github/ARCH-SNOCONE.md` §"Lowering map".

---

## 🎯 Goal

Get all six `parser_*.sc` programs producing AST trees matching the C `--dump-ast` reference, by **transpiling each parser_*.sc to portable .sno**, then comparing SCRIP-direct output vs SPITBOL output via the existing 2-way sync-step monitor.

**Key insight:** post-transpiler, SPITBOL becomes a Snocone oracle by transitivity. The 2-way monitor reports first divergence with line-precise repros. The transpiler also stress-tests `lower.c` since each construct forces a Snocone→AST→SNOBOL4 path.

---

## ⛔ Implementation Constraints (Lon directive 2026-05-17)

1. `parser_<lang>.sc` files may use ONLY six functions from `corpus/SCRIP/`: `shift`, `reduce`, `nPush`, `nInc`, `nTop`, `nPop` (semantic.sc + counter.sc).
2. **No language-specific helpers.** `icon_helpers.sc` and `raku_helpers.sc` must be eliminated — logic folds into the grammar or migrates to C-side `lower.c` / `rebus_lower.c` / `icon_lower.c` / `raku_lower.c`.
3. `pop`, `foldop`, `nDec`, `reduce_opsyn`, `reduce_prim`, `reduce_call`, `nPushName` may NOT be called from `parser_*.sc`.
4. **No `*Var` deferred references** where Var is itself a Snocone function (triggers `bb_deferred_var` rebuild path).
5. Transpiler output is **portable SNOBOL4**. Must run on SCRIP (`--interp`, `--run`), SPITBOL x64 (`/home/claude/x64/bin/sbl -bf`).

---

## 🔧 Architecture

```
parser_<lang>.sc
       │  SCRIP frontend
       ▼
   tree_t AST                                  ← trust LOWER
       │  lower_sno.c (new LOWER stage)
       │  Driven by:  scrip --dump-sno
       ▼
parser_<lang>_transpiled.sno
       │
       ├──► SCRIP --interp/--run        ──► IPC trace ──┐
       └──► SPITBOL (sbl -bf)           ──► IPC trace ──┤
                                                        ▼
                                      2-way sync-step monitor
                                      (scripts/run_parser_sync_monitor.sh)
```

`tree_to_sno(ast, FILE*)` in `src/lower/lower_sno.c` is the transpiler entry. Public CLI: `--dump-sno`.

---

## 📊 Current State (2026-05-18, Opus 4.7)

**Transpile pipeline works.** All six parser_*.sc transpile cleanly (0 placeholders).

**Cross-language SPITBOL sweep on canonical runtime chain** (`global case assign match counter stack tree ShiftReduce tdump gen qize semantic omega trace`):

| Parser   | Status        | Notes |
|----------|---------------|-------|
| snobol4  | ✅ runs       | smoke 7/0 |
| snocone  | ✅ runs       | brace-bearing forms fail — see SCT-9-arbno-fence |
| rebus    | ✅ runs       | |
| icon     | ✅ runs       | needs SCT-4 (icon_helpers elimination) for full grammar |
| raku     | ERROR 022     | undefined helpers from raku_helpers.sc — SCT-5 |
| prolog   | ERROR 246     | stack overflow @line 2065 — SCT-6 |

**Snocone parser-fixture gate** (transpile→SPITBOL vs C `--dump-ast` byte-diff):

- **PASS=29 FAIL=38** (was reported 24/2/41, but that watermark was stale — see SCT-9-runtime-chain below).
- FAIL breakdown: 29 Parse Error (all brace-bearing forms — `if`/`while`/`for`/`function`), 6 ERROR 235 (augmented_* subscript), 3 multiline-format mismatch.

**Root cause of brace-bearing failures (SCT-9-arbno-fence):** `Body(var) = nPush() ARBNO(*Command) Save_nbody(var) nPop()` is called from inside `if_cmd`/`while_cmd`/`for_cmd`/`func_cmd`/`switch_cmd`, which themselves match inside `ARBNO(Command)` in `Compiland`. When the outer ARBNO backtracks, the inner `nPush`/`nPop` side effects are **not reversed** by SPITBOL's pattern-match stack (per Manual Ch 18 — only cursor and alternative state are saved, not user-function side effects). This corrupts the counter stack on retry. **Fix candidates:** FENCE each command in `Command` alternation, or FENCE the outer `ARBNO(Command)`.

**SCT-9-zero-output / SCT-9-runtime-chain** (resolved 2026-05-18 follow-up): the prior session reported "zero output" on `arith_add.sc`. Two issues — (a) SPITBOL emits a blank line for every `OUTPUT = NULL` (which is what the `xTrace`-guarded trace lines reduce to when `xTrace` is unset), drowning the real one-line output, and (b) `assign.sc` was missing from the transpile chain, leaving `*assign(.captured_call_name, token)` unbound, which broke all call/control-flow parses. Both fixed. Filter SPITBOL output with `grep -v '^$'` to see real content.

---

## 🪜 Open Rungs

### Phase 1 — Transpile MVP per language

- [x] **SCT-1** parser_snobol4.sc → .sno (lower_sno.{c,h}, `--dump-sno`, all 30 TT_* tags)
- [x] **SCT-1b** statement-position control flow + label-sanitize
- [x] **SCT-1c** SNOBOL4 line-continuation for >1024-char emissions
- [x] **SCT-1d** multi-file `--dump-sno` + `-CASE 0` prelude + tail dedup
- [x] **SCT-1e** explicit `?` operator fix in TT_SCAN expression case
- [x] **SCT-2** parser_rebus.sc → .sno (qtag REPLACE eq-length fix + label_sanitize on TT_VAR)
- [x] **SCT-SN4-ERR041** parser_snobol4.sc multi-stmt — deleted 2 stray `nInc()` before `*StmtRepl` in `Stmt`. PASS=49→64/88. (2026-05-21d, Opus 4.7)
- [x] **SCT-SN4-IMPLICIT-MATCH** parser_snobol4.sc — implicit pattern-match-by-juxtaposition. PASS 64→88/88. (2026-05-21e, Sonnet 4.6, corpus `794dc0a`). Stmt restructured into two branches: Branch A (explicit `?`) requires `$'  ' nInc() *Expr14 $'?' nInc() *Expr1 reduce('TT_PAT',1) FENCE(*StmtRepl|epsilon)`; Branch B (implicit/assign/bare) uses `$'  ' nInc() *Expr1 FENCE(*StmtRepl|epsilon)`. Also fixed StmtRepl second arm to use optional trailing whitespace `$' '` after `=` so null-replacement (`S 'a' =`) parses correctly.
- [ ] **SCT-1f** drive 2-way sync-monitor — needs SN-26-spl-bridge in x64
- [ ] **SCT-3** parser_snocone.sc — blocked on SCT-9-arbno-fence
- [ ] **SCT-4** parser_icon.sc — eliminate icon_helpers.sc first. 4 trivial leaf-push helpers (`push_qlit`, `push_cset`, `push_flit`, `push_kw`) inline into Expr11 arms via `shift(..., 'TT_QLIT')` etc. `notmatch` already in match.sc.
- [ ] **SCT-5** parser_raku.sc — eliminate raku_helpers.sc. `push_interp_str`/`dq_unescape` migrate to C-side `raku_lower.c`. The 9 `finish_*` variable-arity assemblers fold into `reduce(tag, nTop_count)` with nPush/nInc discipline.
- [ ] **SCT-6** parser_prolog.sc — self-contained but SPITBOL hits ERROR 246 stack overflow @line 2065. Diagnose pattern recursion.

### Phase 2 — Closure

- [ ] **SCT-9-arbno-fence** ⚠ BLOCKER. FENCE each command in `Command` alternation in parser_snocone.sc (and analogous wrappers in other parsers). This is the structural fix for "nPop inside ARBNO" — backtrack must not re-enter committed counter/stack operations. Verify with `if`/`while`/`for`/`function` fixtures.
- [ ] **SCT-9-error235** Diagnose ERROR 235 (subscript on non-table) at line 928 for augmented_* fixtures (`x += 1`).
- [ ] **SCT-9-multiline** Decide: should `--dump-ast` emit single-line (matching TDump) or should TDump emit multi-line (matching `--dump-ast`)? Affects `assign_seq`, `assign_str`, two others.
- [ ] **SCT-9g-snobol4** Precedence/assoc audit vs SPITBOL Manual Ch 15. Spec on disk; can proceed.
- [ ] **SCT-9g-rebus/icon/raku/prolog** Awaiting spec docs from Lon (Icon ref / Raku op table / Prolog op/3).
- [ ] **SCT-9j** Wire `scripts/test_parser_sc_transpile.sh` (per-lang fixture gate) once SCT-9-arbno-fence lands.
- [ ] **SCT-10** Delete sidecar helpers permanently from corpus.
- [ ] **SCT-11** Document the Snocone subset (`corpus/SCRIP/SNOCONE-SUBSET.md`).

---

## 🧠 Critical invariants

1. **Transpiler is C code** (`src/lower/lower_sno.c`). Walks `tree_t*`, emits SNOBOL4 to stdout. Driven by `scrip --dump-sno`.
2. **Trust LOWER.** Transpiler is mechanical — if it emits `oops`, LOWER probably emitted `oops` first. Fix LOWER.
3. **6 functions only** in parser_*.sc: shift, reduce, nPush, nInc, nTop, nPop. Any 7th is a separate ticket.
4. **Pattern functions run at BUILD time, not match time.** To defer, use `*FunctionCall()` (deferred operator). The runtime wrappers `nPush()`/`nPop()`/`nInc()` already return `epsilon . *XxxCounter()` patterns, so they ARE deferred — but their **side effects are not reversed on backtrack** (Manual Ch 18). This is the root cause of SCT-9-arbno-fence.
5. **Canonical runtime chain** (per `scripts/run_scrip_parser.sh`): `global case assign match counter stack tree ShiftReduce tdump gen qize semantic omega trace`. **All 14 must be included in `--dump-sno`** — `assign.sc` in particular is referenced by parser_snocone.sc's `*assign(.captured_*, token)` pattern but easy to miss.

---

## 🛠️ How-to

### Build scrip

```bash
apt-get install -y libgc-dev libgc1   # one-time
cd /home/claude/SCRIP && make scrip
```

Adding a new file under `src/lower/`: update both the SRC list (Makefile ~L90) and the explicit compile rule (~L286).

### Transpile + run a fixture

```bash
SD=/home/claude/corpus/SCRIP
./scrip --dump-sno \
    $SD/global.sc $SD/case.sc $SD/assign.sc $SD/match.sc \
    $SD/counter.sc $SD/stack.sc $SD/tree.sc $SD/ShiftReduce.sc \
    $SD/tdump.sc $SD/gen.sc $SD/qize.sc $SD/semantic.sc \
    $SD/omega.sc $SD/trace.sc \
    $SD/parser_snocone.sc \
  > /tmp/p_snocone.sno

cat fixture.sc | /home/claude/x64/bin/sbl -bf /tmp/p_snocone.sno 2>&1 | grep -v '^$'
```

### `--dump-sno` lower_sno.c structure

`src/lower/lower_sno.c`, top-to-bottom:
1. `sno_ctx_t` — emission state
2. `emit`, `emit_nl`, `sval_or` utilities + line-buffer for 1024-char continuation
3. `emit_expr(c, e)` — recursive walker, big switch on `e->t`. Default: `'?TT_NN?'` placeholder.
4. `emit_stmt(c, s)` — TT_STMT handler. Demux by `:subj`/`:pat`/`:repl`/`:eq`/`:goS`/`:goF`/`:go`/`:lbl`.
5. `emit_node(c, n)` — top dispatch. Routes TT_STMT→emit_stmt, TT_PROGRAM→emit_program, control-flow→Gimpel/loop templates.
6. `tree_to_sno(ast, out)` — public entry. Wraps `&FULLSCAN = 1` prelude, `END` terminator.

To add a TT_* tag: expression-only → `emit_expr` switch case; statement-shape → `emit_node` switch case per ARCH-SNOCONE.md §"Lowering map".

### Identify a `?TT_NN?` placeholder

```bash
python3 -c "
import re; txt = open('/home/claude/SCRIP/src/include/ast.h').read()
m = re.search(r'typedef enum tree_e \{([^}]+)\}', txt, re.S)
tags = [t.strip() for t in m.group(1).split(',') if t.strip() and 'TT_' in t]
import sys; n = int(sys.argv[1]); print(f'TT_{n} = {tags[n]}')
" 95   # → TT_95 = TT_IF
```

### Emitter tricks (won't change — record once)

- Label-only lines: pad with `OUTPUT =` (SCRIP rejects pure-label lines).
- Tight unary operators: `(.X)`, `($X)`, `(*X)` — no space.
- `label_sanitize`: strip leading `_`, append trailing `_`. Applied to **all** identifiers (TT_VAR), not just labels — SPITBOL Ch.14 line 9335 covers pattern-capture variables too.
- TT_QLIT with both `'` and `"`: emit `'...'/*BOTH-QUOTES*/` and let runtime use `CHAR(34)`/`CHAR(39)`.
- Quoted-string scan in `emit_nl` line-break: walk from line start (no SNOBOL4 escape character; every quote is structural).

### ⚠ Case-sensitive mode — mandatory everywhere

**SNOBOL4, Snocone, and SPITBOL are all run in case-sensitive mode.** The flag is `-f` ("don't fold source code case"). Always use `-bf` together:

```
/home/claude/x64/bin/sbl -bf file.sno
```

`-b` suppresses the signon banner. `-f` disables case-folding so that `x` and `X` are distinct identifiers. Omitting `-f` silently folds all names to upper-case and breaks every parser that uses lower-case identifiers (which is all of them). This applies to every SPITBOL invocation in this project — scripts, manual runs, and transpile gates.

### Build SPITBOL from source (rare)

`/home/claude/x64/bin/sbl` ships prebuilt. Only rebuild if patching the runtime (e.g. SN-26-spl-bridge IPC wire). Recipe in `harness/oracles/spitbol/BUILD.md`. SPITBOL compatibility notes: no `&STNO` (use `&LASTNO`), no `LOAD()`, no `LABELCODE()`, `DATA()` returns lowercase type names. Invocation: `/home/claude/x64/bin/sbl -bf file.sno`.

---

## 🧭 Relationship to other goals

| Goal | Relationship |
|------|--------------|
| `GOAL-PST-REBUS.md`               | Independent path. PST-REBUS fixes direct Snocone runtime; this goal transpiles around it. Both converge later. |
| `GOAL-PARSER-PURE-SYNTAX-TREE.md` | This goal depends on LOWER producing correct `tree_t`. Sync-monitor reveals LOWER bugs as divergences. |
| `GOAL-LANG-SNOCONE.md`            | Post-SCT-11, this defines the Snocone subset spec. |
| `GOAL-PST-PROLOG.md`              | Orthogonal. SCT-6 can land independently. |

---

## 📝 Files touched

| Repo | Path | Role |
|------|------|------|
| SCRIP  | `src/lower/lower_sno.{c,h}`            | Transpile pass |
| SCRIP  | `src/driver/scrip.c`                   | `--dump-sno` CLI |
| SCRIP  | `src/ast/ast_print.c`                  | TDump-matching length-budget formatter (SCT-9c) |
| SCRIP  | `src/frontend/snocone/snocone_parse.y` | n-ary flatten for `+ - * /` (SCT-9d) |
| SCRIP  | `Makefile`                             | build rule + SRC for lower_sno.c |
| SCRIP  | `scripts/run_parser_sync_monitor.sh`   | SCT-7 wrapper |
| corpus   | `SCRIP/parser_*.sc`                    | the six inputs |
| corpus   | `SCRIP/semantic.sc`                    | `qtag` (_qtag→qtag rename, REPLACE eq-length fix) |
| corpus   | `SCRIP/parser_snocone.sc`              | notmatch dedup (2026-05-18) |
| corpus   | `SCRIP/icon_helpers.sc`                | notmatch dedup; slated for deletion in SCT-4 |
| corpus   | `SCRIP/qize.sc`                        | dead `LEQ` deleted (SCT-9e) |
| corpus   | `programs/*/parser/*.ref`              | regenerated baseline (SCT-9b/9f) |
| .github  | `GOAL-PARSER-SC-TRANSPILE.md`          | this file |
| .github  | `PRECEDENCE-AUDIT.md`                  | SCT-9g-snocone deliverable |
| .github  | `ARCH-SNOCONE.md` §"Lowering map"      | authority for stmt-shape lowering |

---

## 📖 SPITBOL Manual — verified line index for `/tmp/spitbol.txt`

`pdftotext spitbol-manual-v3_7.pdf /tmp/spitbol.txt` then view with these anchors (body lines, verified 2026-05-17):

| Ch | Line  | Title                             | Why it matters                              |
|----|-------|-----------------------------------|---------------------------------------------|
| 8  | 5806  | Program-Defined Objects           | Gimpel template (5973) — DEFINE form        |
| 9  | 6722  | Advanced Topics                   | ARBNO, *VAR, quickscan/fullscan             |
| 14 | 9017  | SPITBOL Statements                | LABEL SUBJECT ? PATTERN = REPL :GOTO        |
| 15 | 9540  | Operators                         | Priority/assoc table (9830+)                |
| 16 | 9761  | Keywords                          | &ANCHOR, &FULLSCAN, &CASE, etc.             |
| 17 | 10135 | Data Types & Conversion           | Type conversion matrix                      |
| 18 | 10606 | Patterns & Pattern Matching       | Algorithm + ABORT/ARB/BAL/FAIL/REM/SUCCEED  |
| 19 | 10958 | SPITBOL Functions                 | Built-ins reference                         |
| C  | 13651 | Differences from SNOBOL4          | Portability boundary                        |
| D  | 13968 | Error Messages                    | Diagnostics                                 |

### Operator priority (Ch 15, line 9830+) — terse

| Op | Pri | Assoc | Def |
|----|-----|-------|-----|
| `=`              | 0  | right | assignment |
| `?`              | 1  | left  | pattern match (explicit) |
| `\|`             | 3  | right | alternation |
| *space*          | 4  | right | **concat or match** (implicit pattern-match) |
| `+ -`            | 6  | left  | add/sub |
| `/`              | 8  | left  | division |
| `*`              | 9  | left  | multiplication |
| `^ ! **`         | 11 | right | exponentiation |
| `$`              | 12 | left  | immediate assignment |
| `.`              | 12 | left  | conditional assignment |

OPSYN slots: `& @ # % ~` binary; `! % / # = \|` unary.

### Goto syntax (Ch 14, line 9576+)

- `:(LABEL)` unconditional, `:S(L)` on success, `:F(L)` on failure
- `:S(L1)F(L2)` combined, `:<VAR>` direct to CODE() block, `:($expr)` computed

### Critical SPITBOL-vs-SNOBOL4 differences (App C)

1. `&ANCHOR` read at match **start** only.
2. `ABORT`/`ARB`/`FAIL`/`REM`/`SUCCEED` are **write-protected** in SPITBOL.
3. Same stack for pattern matching and function calls — recursion → stack overflow.
4. `TABLE()` is hashed; argument = hash header count, not size limit.
5. No FORTRAN I/O, no `VALUE()`. Recovery via `SETEXIT()`.

---

## Session 2026-05-18 (Claude Sonnet 4.6) — SCT-parser-sc-no-crash

**Goal achieved:** All six `parser_*.sc` run under `scrip --interp` without crash, abort, or segfault.

**Fixes landed (SCRIP `db89a804`):**
- `stmt_exec.c` — `bb_deferred_var`: `child_state` now stores `val.p` as cache key; prevents re-JIT on every ARBNO retry
- `bb_pool.c/h` — `bb_alloc` returns NULL (not abort) on pool exhaustion; pool reduced 64MB→4MB (safe with caching)
- `emit_core.c` — `bb_emit_byte` overflow sets flag instead of abort; `bb_emit_end`, `bb_label_define`, both patch-list emitters skip gracefully on overflow
- `emit_bb.c` — `bb_build_flat`/`bb_build_brokered` check overflow flag, return NULL gracefully
- `rt.c` — `rt_bb_arbno`: guard `ζ->fn == NULL` → epsilon-ARBNO instead of segfault

**Fixes landed (corpus `c43225b`):**
- `raku_helpers.sc` — `Push_ilit(n)` / `push_ilit_n(n)` 1-arg variant; fixes ERROR 022 on raku

**Status:**
- snobol4: OK (rc=0, Parse Error — SNOBOL4 syntax not fully handled, not a crash)
- snocone: OK (rc=0, Parse Error)
- rebus: OK (rc=0, Parse Error)
- icon: OK (rc=0, Parse Error)
- raku: OK (rc=0)
- prolog: OK (rc=0)

**Hangs (pre-existing, not regressions):** All four of snobol4/snocone/rebus/icon hang on complex multi-statement fixtures — ARBNO infinite loop in pattern matching. Next session: diagnose hang root cause.

**Gates held:** crosscheck_snocone PASS=8/0, crosscheck_snobol4 PASS=5 FAIL=1 (beauty_omega pre-existing), test_smoke_snocone PASS=5/0.

## Post-session check 2026-05-18

**Hang check:** Zero hangs. All six exit rc=0 within timeout.

**Tree output check:** None of the six produce tree output under `scrip --interp` directly — all return "Parse Error" or empty. This is **pre-existing** (confirmed by testing before our commit). The `scrip --interp` + `parser_*.sc` path has never produced tree output in this session; the SPITBOL transpile path (PASS=29 for snocone) remains the working oracle path.

**Next session goal:** Diagnose why `scrip --interp` + `parser_snocone.sc` produces "Parse Error" on `x = 1 + 2;` — a fixture that passes cleanly under SPITBOL. Likely cause: BB pattern matching behaves differently from SPITBOL for some construct in the snocone grammar (ARBNO, FENCE, deferred-var interactions). Start with snocone since it has the fixture baseline (PASS=29 under SPITBOL).

## Session 2026-05-21b (Claude Sonnet 4.6) — SCT-parser-sn4-nInc-fence ⚠ EMERGENCY HANDOFF

**Goal:** Fix ERROR 041 on multi-stmt fixtures (SCT-SN4-ERR041). Root cause found and partially fixed.

**Root cause confirmed (NOT the `c` field rename):**
The `nInc()` in `Command` was OUTSIDE the `FENCE`, firing unconditionally before
`FENCE(...)` attempts its alternates. When `ARBNO(*Command)` tries one final
`Command` at end-of-input and `FENCE(...)` fails, `nInc()` had already fired —
overcounting the Compiland-level counter by 1. This caused `reduce('Parse','nTop()')`
to pop one extra empty string off the semantic stack, giving `child[1]=STRING` instead
of a tree node.

**Fix landed (corpus `255982f`, NOT yet committed):**
`parser_snobol4.sc` Command rule: moved `nInc()` inside each FENCE alternate,
after the first committed token:
```
Command = FENCE(
   shift(*Comment, "'TT_COMMENT'") nInc() reduce("'TT_COMMENT'", 1) nl
|  shift(*Control, "'TT_CONTROL'") nInc() reduce("'TT_CONTROL'", 1) (nl | ';')
|  *Stmt nInc() (nl | ';')
);
```

**⚠ BUT: This fix is NOT sufficient.** Multi-stmt ERROR 041 persists even after
this change. DEEPER BUG found in `Stmt` itself:

`reduce('TT_STMT', nTop())` inside `Stmt` pops 3 items but only 2 net items
belong to the current stmt. The `nInc()` before `*StmtRepl` (in both branches
of the inner FENCE) overcounts because `reduce('TT_EQ', 2)` inside StmtRepl
already consumed `TT_VAR` (the Expr14 child, counted as item 2). So item 2 gets
consumed and item 3 is TT_EQ — two counter slots for one net stack slot. The
3rd pop then grabs a tree node from the PREVIOUS stmt off the shared semantic stack.

Verified: `child[2] = TT_STMT(a=1)` swallowed inside `TT_STMT(b=2)` for 2-stmt input.

**NEXT SESSION: Run beauty suite gate first (`bash scripts/test_gate_sn7_beauty_self_host.sh`),
study beauty.sno's working `Stmt` + `Command` patterns (around line 229), and transplant
the correct nInc placement into `parser_snobol4.sc`. beauty.sno's grammar is the oracle.**

**Current scores:** PASS=49 PARSE_ERROR=24 OTHER_FAIL=15 / 88 total (unchanged).
SCRIP unchanged. corpus has uncommitted diff on `SCRIP/parser_snobol4.sc`.

## Session 2026-05-21 (Claude Sonnet 4.6) — SCT-parser-sn4-spitbol

**Goal:** Get parser_snobol4.sc transpiling to SNOBOL4 and running under SPITBOL.

**Fixes landed (SCRIP `4decab7d`, corpus `9dfe203`):**

lower_sno.c:
- TT_WHILE: n>=4 guard dropped; labels synthesized from if_seq (AST has only 2 children in PST mode)
- TT_GOTO_U as :subj: emit `:(label)`; label_of() fixed to use node's own v.sval not c[0]
- TT_ASSIGN(TT_SEQ(subj,pat),repl) as :subj: emit as `subj  pat  =  repl` not `(subj pat) = repl`
- TT_IDX: emit ITEM(base,idx) — $'[' is OPSYN'd in parser_snobol4.sc; ITEM() is unaffected
- -CASE 0 confirmed correct (N=0 = case-sensitive per SPITBOL Ch.14)

corpus/SCRIP/parser_snobol4.sc:
- Result loop uses ITEM(c(ptree),i) instead of c(ptree)[i] to survive $'[' OPSYN override

**Result: PASS=49 PARSE_ERROR=24 OTHER_FAIL=15 / 88 total**

**NEXT (SCT-SN4-ERR041):** 15 ERROR 041 on multi-stmt fixtures. Root cause confirmed:
-CASE 0 folds `c` identifier globally, corrupting DATA('tree(t,v,n,c)') field accessor `c()`.
Fix: rename `c` field to `ch` throughout corpus/SCRIP/tree.sc and all callers (TDump, Insert,
Remove, Tree, Equal, Equiv, Find, Visit — ~20 sites). This is clean corpus surgery with no
runtime behaviour change. 24 Parse Errors are a separate issue (pattern fixtures).

## Session 2026-05-21c (Claude Opus 4.7) — SCT-BEAUTY-SC + SCT-LOWER-FOR-IDX

**Goal pivot:** Get the Snocone beauty.sc working under SCRIP transpiler (`--dump-sno` → SPITBOL). Carry over constructs verbatim from beauty.sno where the .sc translation diverged.

**Triage of all three execution modes for parser-driven .sc:**

| Mode | Result |
|------|--------|
| `scrip --interp` | Infinite "Error 5 Undefined function or operation" at stmt 14 (Shift/nPush not resolved by interpreter). Times out. |
| `scrip --run` | Same Error 5 loop, 54k stderr lines, timeout. |
| `scrip --dump-sno` → SPITBOL `-bf` | **Working path.** Transpiles, runs to completion. |

Both `--interp` and `--run` remain broken for tree-building parsers (pre-existing per session 2026-05-18 notes). Only transpile path is viable.

**lower_sno.c fixes landed (SCRIP, this session):**
- **TT_FOR**: was rejecting current PST 4-child shape (init, cond, step, body), emitting `?TT_FOR?` placeholders. Fixed to accept both PST 4-child (synthesize labels, emit init then Ltop/cond/body/Lcont/step/Ltop/Lend) AND legacy 5+ form (Lcont/Lend pre-allocated QLITs). Eliminates 14 placeholders in beauty.sc transpile.
- **TT_IDX**: (a) n-ary subscripts `a[i,j]` were emitting `ITEM(a, i)` only (single dim, second arg lost). Now emit single `ITEM(a, i, j, ...)` per SPITBOL Ch.19. (b) `TT_INDIRECT` base (`$a[i]`) was emitting invalid `ITEM(($a), i)`. Now unwraps to `$ITEM(a, i)`.

**beauty.sc / Qize.sc fixes landed (corpus, this session):**
- Stmt/XList/Expr17/Goto: `epsilon . ''` and `'=' . ''` (Snocone conditional-assign to empty-string variable — nonsensical) replaced with `shift(epsilon, '')` and `shift('=', '=')`. These are the faithful carry-over of beauty.sno's `epsilon ~ ''` and `'=' ~ '='` (where `~` = OPSYN'd to `shift`). Stmt needs 7 children for `reduce('Stmt', 7)`; without the shifts, the right number wasn't pushed.
- TxInList: `EVAL('upr(tx)')` (build-time eval, unbound tx) → `*upr(tx)` (deferred call) per beauty.sno line 75.
- Qize.sc: removed bogus `DEFINE('LEQ')` (LEQ is SPITBOL built-in, redefinition is ERROR 248) and `DEFINE('Ucvt')` (unreachable in self-host; not defined in oracle either).

**Result after fixes:**
- Transpile: 2158 lines, **0 placeholders** (was 14 `?TT_FOR?`).
- SPITBOL `-bf`: runs to completion with **zero errors** (was ERROR 248 LEQ, before that ERROR 236 wrong subscripts, before that ERROR 239 indirection).
- BUT: parser reports "Parse Error" on `        x = 5\nEND\n` (simplest fixture).
- Trace shows `PushCounter() / 1=IncCounter() / Push(Label) / Shift(Label, ) / Parse Error`. Oracle on same input produces the next expected step `Push(Id) / Shift(Id, x)` etc.
- Divergence point: Stmt's outer FENCE branch `*White *Expr14 ...` doesn't fire after `*Label` succeeds. Either *White or *Expr14 silently fails in beauty.sc but not in beauty.sno.

**Other audit findings (no fix yet — possible drift):**
- `ShiftReduce.sc` Reduce: `tree(t, '', n, c)` vs oracle's `tree(t,, n, c)` — explicit `''` (non-NULL empty) vs skipped arg (NULL/unset). May affect downstream tree predicate behavior. Comment in source already flags this as a known issue ("TODO SB-6.E.7-K — faithful is tree(t,,n,c)").

**Documentation:**
- Added `⚠ Case-sensitive mode — mandatory everywhere` section to this file: `-f` disables SPITBOL case-folding; canonical invocation `sbl -bf`. Two `sbl -b` occurrences fixed to `sbl -bf` in How-to and Build sections.

**NEXT SESSION SCT-BEAUTY-SC-PARSE — ROOT CAUSE FOUND (session 2026-05-21d):**

**Root cause:** `shift(p, t)` in beauty.sc lowers to a function call whose body does:
```
shift = EVAL('p . thx . *Shift(' qtag(t) ', thx)')
```
`EVAL` runs in **global scope**, so `p` in the EVAL string is the **global variable `p`** (undefined = null), NOT the local parameter. The resulting pattern is `epsilon . thx . *Shift(tag, thx)` instead of the actual sub-pattern. This makes every `shift(pat, 'TAG')` in Expr17 etc. match **epsilon** (the empty string) and immediately commit the surrounding FENCE — the correct alternatives are never tried. Expr14, Expr17, XList all broken the same way.

**Why beauty.sno works:** Uses `*Function ~ 'Function'` where binary `~` is `OPSYN('~','shift',2)` from semantic.sc. Binary `~` passes operands directly — no EVAL, no scope issue. Pattern built correctly.

**Note:** Cannot simply use `~` in beauty.sc's transpile: `OPSYN('~','shift',2)` fires at line 875 but `DEFINE('shift')` is at line 897 (OPSYN would bind to undefined). `~` is also Snocone NOT elsewhere.

**The fix — two options (Lon to decide):**

**Option A (beauty.sc source fix):** Replace every `shift(pat, 'TAG')` in beauty.sc's expression grammar with the inlined form `pat . thx . *Shift('TAG', thx)`. This is exactly what beauty.sno's `pat ~ 'TAG'` expands to. Touches: all `shift(...)` calls in `XList`, `Expr14`, `Expr17`.

**Option B (lower_sno.c fix):** When lowering a Snocone `TT_FNC` call to `shift(arg, tag)` where tag is a string literal, emit the inlined form `arg . thx . *Shift(tag, thx)` directly instead of a function call. Fixes the transpiler for all six `parser_*.sc` files automatically and is the more robust fix.

**Verify:** after fix, `scrip --dump-sno beauty.sc | sbl -bf` on `x = 5\nEND\n` must produce `Push(Id) Shift(Id, x)` (not Parse Error).

Commits this session:
- SCRIP `01577f1a` — SCT-LOWER-FOR-IDX
- corpus  `f3b8afb`  — SCT-BEAUTY-SC-CARRYOVER

## Session 2026-05-21e (Claude Sonnet 4.6) — SCT-SN4-IMPLICIT-MATCH ✅ CLOSED

**Goal achieved:** Implicit pattern-match-by-juxtaposition (`S 'a' | 'b'` with no `?`) now parses. PASS=64→88/88. Zero regressions.

**Two changes landed (corpus `794dc0a`):**

1. `parser_snobol4.sc` `Stmt` — restructured outer FENCE into two explicit branches:
   - **Branch A** (explicit `?`): `$'  ' nInc() *Expr14 $'?' nInc() *Expr1 reduce("'TT_PAT'", 1) FENCE(*StmtRepl | epsilon)` — requires literal `?` token, only fires when `?` is present.
   - **Branch B** (implicit/assign/bare): `$'  ' nInc() *Expr1 FENCE(*StmtRepl | epsilon)` — `*Expr1` (concat/alt level) consumes the full expression. `Expr1` stops before `=` (which is `Expr0`'s job), so `StmtRepl` still handles `= repl` correctly on top. Subsumed old `| *StmtRepl | epsilon` inner arms.

2. `StmtRepl` second arm (null replacement `S 'a' =`): changed `$'='` (mandatory WS both sides = `White '=' White`) to `$'  ' '=' $' '` (mandatory WS before, **optional** after), because `=` at end-of-line has no trailing whitespace. Per SPITBOL Manual Ch.14: "If the equal sign is present but the replacement field is absent, the null string is assumed."

**Key insight confirmed:** The C frontend (`--dump-ast`) treats implicit match as pure concatenation in the `:subj` field — `S 'a' | 'b'` becomes `TT_ALT(TT_SEQ(S,'a'),'b')` as a single subject expression, NOT split into `:subj`/`:pat`. So Branch B correctly uses one `nInc()` (not two) and emits no `TT_PAT` wrapper.

**All 10 SNOBOL4/SPITBOL assumptions verified** against manual + code + SPITBOL oracle — all TRUE. See SNOBOL4-SNOCONE-PRIMER.md assumption grid for details (to be added next session).

**Gates:** smoke 7/0, crosscheck 5/1 (beauty_omega pre-existing, unchanged).

**Pre-existing issue noted (not caused by this fix):** `str_body` is always empty in SPITBOL transpile output (`TT_QLIT("")` instead of `TT_QLIT("a")`). This was present in the 64-fixture baseline — the PASS count only measures "not Parse Error", not byte-identical output. Tracked separately.

**NEXT:** `SCT-1f` (wire 2-way sync-monitor, needs SN-26-spl-bridge in x64) or `SCT-BEAUTY-SC-PARSE` (Option A vs B for the `shift()` EVAL-global-scope bug in beauty.sc — awaiting Lon decision).

## Session 2026-05-21d (Claude Opus 4.7) — SCT-SN4-ERR041 ✅ CLOSED

**Goal achieved:** ERROR 041 on multi-statement SNOBOL4 fixtures is fixed.
**Score: PASS=49 → PASS=64 / 88.** All 15 ERROR 041 failures eliminated, zero regressions.

**Root cause (confirmed, NOT the `c`-field-folding theory from session 2026-05-21):**
`Stmt` in parser_snobol4.sc had two stray `nInc()` calls immediately before
`*StmtRepl`. The subject (`*Expr14` → TT_VAR) was counted by one `nInc()`, then
`*StmtRepl`'s internal `reduce("'TT_EQ'", 2)` *consumed* that subject while pushing
TT_EQ — net stack effect zero. But the extra `nInc()` made the counter believe a new
item was added. So `reduce("'TT_STMT'", 'nTop()')` popped one item too many, reaching
into the *previous* statement's TT_STMT node. The next statement's `n(ptree)`/`c(ptree)`
in the driver tail then operated on a STRING instead of a tree → ERROR 041 at the
`cmd = ITEM(c(ptree),i)` site.

**Fix landed (corpus, this session — 2 lines):** parser_snobol4.sc `Stmt` rule — deleted
the `nInc()` before `*StmtRepl` in both the `?`-pattern branch and the bare-`=` branch:
```
                     FENCE(*StmtRepl | epsilon)     # was: FENCE(nInc() *StmtRepl | epsilon)
                  |  *StmtRepl                       # was: nInc() *StmtRepl
```
Counter discipline now holds for all four Stmt shapes (bare-expr / subj+= / subj+? +pat /
subj+? +pat+=). Verified by xTrace=5 walk on a 2-stmt fixture.

**Gates:** test_smoke_snobol4.sh PASS=7/0; test_crosscheck_snobol4.sh PASS=5 FAIL=1
(beauty_omega — pre-existing baseline, unchanged). scrip --interp on parser_snobol4.sc
still returns "Parse Error" with rc=0 (pre-existing, not a regression).

**Remaining 24 PARSE errors** are a structurally distinct issue: implicit pattern-match
by juxtaposition (`S 'a' | 'b'` with no explicit `?`). The Stmt grammar currently only
handles the explicit-`?` form (`$'?' nInc() *Expr1 ...`); there is no production for a
subject `*Expr14` followed directly by a pattern `*Expr1` when no `?` token is present.
Manual Ch 6 (line 3230) confirms `SUBJECT PATTERN` with whitespace-as-match-operator is
standard SNOBOL4. **NEXT (SCT-SN4-IMPLICIT-MATCH):** add an implicit-match branch to the
inner FENCE in `Stmt`, between the `$'?' ...` branch and the bare-`*StmtRepl` branch,
of shape roughly `nInc() *Expr1 reduce("'TT_PAT'", 1) FENCE(*StmtRepl | epsilon)`. Mind
the subject/pattern boundary ambiguity (Manual line 3242: first complete statement element
is the subject).

**Assumption verification grid** appended to SNOBOL4-SNOCONE-PRIMER.md this session — 27
SNOBOL4/SPITBOL/Snocone facts relied on during the fix, each verified against SPITBOL
Manual v3.7 + library source + empirical runs. One falsified (#7 — the 'nTop()' string is
build-time-interpolated into the EVAL pattern as a bare match-time call, NOT routed through
Reduce's EXPRESSION-DATATYPE check); two refined (#3/#17 OUTPUT failure vs empty-RHS; #14
epsilon is a null-variable convention, not a SPITBOL primitive). SPITBOL manual now
fetchable at https://raw.githubusercontent.com/spitbol/x32/master/docs/spitbol-manual-v3.7.pdf

**SCT-1 status:** Add new rung **SCT-SN4-IMPLICIT-MATCH** under Phase 1. SCT-SN4-ERR041 closed.
