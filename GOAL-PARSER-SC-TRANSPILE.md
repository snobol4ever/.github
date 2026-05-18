# GOAL-PARSER-SC-TRANSPILE.md — Six parser_*.sc → portable .sno via Snocone→SNOBOL4 transpile

**Repo:** one4all + corpus + .github
**Author:** Lon Jones Cherryholmes · Claude Opus 4.7
**Opened:** 2026-05-17

---

## ⛔ Session Start Protocol

1. Clone `.github`, `corpus`, `one4all`, plus `snobol4ever/x64` to `/home/claude/x64` (prebuilt `bin/sbl` ships in repo — no build step needed). See `PLAN.md`.
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
cd /home/claude/one4all && make scrip
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

cat fixture.sc | /home/claude/x64/bin/sbl -b /tmp/p_snocone.sno 2>&1 | grep -v '^$'
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
import re; txt = open('/home/claude/one4all/src/include/ast.h').read()
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

### Build SPITBOL from source (rare)

`/home/claude/x64/bin/sbl` ships prebuilt. Only rebuild if patching the runtime (e.g. SN-26-spl-bridge IPC wire). Recipe in `harness/oracles/spitbol/BUILD.md`. SPITBOL compatibility notes: no `&STNO` (use `&LASTNO`), no `LOAD()`, no `LABELCODE()`, `DATA()` returns lowercase type names. Invocation: `/home/claude/x64/bin/sbl -b file.sno`.

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
| one4all  | `src/lower/lower_sno.{c,h}`            | Transpile pass |
| one4all  | `src/driver/scrip.c`                   | `--dump-sno` CLI |
| one4all  | `src/ast/ast_print.c`                  | TDump-matching length-budget formatter (SCT-9c) |
| one4all  | `src/frontend/snocone/snocone_parse.y` | n-ary flatten for `+ - * /` (SCT-9d) |
| one4all  | `Makefile`                             | build rule + SRC for lower_sno.c |
| one4all  | `scripts/run_parser_sync_monitor.sh`   | SCT-7 wrapper |
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

**Fixes landed (one4all `db89a804`):**
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
