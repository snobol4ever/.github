# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `asm-backend` A-R1 — corpus ladder rung 1
**HEAD:** `ba178d7` session187
**Milestone:** M-ASM-CROSSCHECK ✅ session151 → **M-ASM-R1** active

**Session187 — corpus ladder infrastructure + R1-R4 fixes; 23/28 PASS:**
- `test/crosscheck/run_crosscheck_asm_rung.sh` — new per-rung ASM corpus driver
- Baseline R1–R4: 21/28 → after fixes: **23/28 PASS**
- Fixed: `E_FLIT` real literals (`003_output_real_literal` ✅), null-RHS `X =` (`012_assign_null` ✅)
- Added: `LOAD_REAL`/`ASSIGN_NULL`/`SET_VAR_INDIR` macros; `stmt_realval`/`stmt_set_null`/`stmt_set_indirect` shims
- M-ASM-R3 (concat/ 6/6) ✅ — fires this session
- Remaining failures: `014`/`015` indirect-`$` (E_DOL LHS path not reached), `literals` (coerce_numeric bug), `fileinfo`/`triplet` (deferred R8)
- Artifacts: beauty_prog.s + roman.s + wordcount.s updated, all NASM-clean
- 106/106 C ✅  26/26 ASM ✅

**⚠ CRITICAL NEXT ACTION — Session188 (backend session):**

Sprint A-R1/R2 — fix 3 remaining R1–R4 issues:

**Fix A — indirect `$` LHS (`014`/`015`):** E_DOL subject path was added to emitter
but not firing. Diagnose: generate .s for 014, check what subject node kind is.
```bash
cd /home/claude/snobol4x
./sno2c -asm /home/claude/snobol4corpus/crosscheck/assign/014_assign_indirect_dollar.sno > /tmp/014.s
grep -A5 "SET_VAR_INDIR\|E_DOL\|indirect" /tmp/014.s | head -20
# If not present: parser puts $'X' as E_INDR not E_DOL — check parse tree
```

**Fix B — `literals` coerce_numeric:** `'' + 1` returns real `0.` instead of int `0`.
Root cause: `coerce_numeric` on empty string `""` calls `atof("")=0.0` → DT_R instead of INTVAL(0).
Fix in `snobol4.c`: in `coerce_numeric`, if string is empty/whitespace → return INTVAL(0).
```c
/* snobol4.c coerce_numeric — before atof/atoll dispatch */
if (!s || !*s) return INTVAL(0);   /* empty string → integer 0 */
```

**Quick-check target after fixes:**
```bash
cd /home/claude/snobol4x && make -C src
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh \
    $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/concat $CORPUS/arith 2>&1
# target: 26/28 PASS (fileinfo + triplet deferred R8)
# M-ASM-R1 fires (hello+output clean), M-ASM-R2 fires (assign clean)
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must stay 106/106
```

**Session start commands:**
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = ba178d7
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh \
    $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/concat $CORPUS/arith
# expected: 23/28 (session187 baseline)
```

**⚠ CRITICAL NEXT ACTION — Session187 continued (backend session):**

Sprint A-R1 — fix three root causes to clear R1+R2:

**Fix 1 — E_FLIT (real literals):** add `case E_FLIT:` to `prog_emit_expr` in
`emit_byrd_asm.c`. Add `stmt_realval(double)` to `snobol4_stmt_rt.c`.
Add `LOAD_REAL` macro to `snobol4_asm.mac`.

**Fix 2 — null RHS (`X =`):** `X =` parses as `has_eq=1`, replacement=`E_NULV` or NULL.
The `ASSIGN_STR` fast path is taken with empty sval → writes garbage.
Fix: detect NULL/E_NULV replacement → emit `ASSIGN_NULL varlab` macro.
Add `ASSIGN_NULL var` macro to `snobol4_asm.mac` that calls `stmt_set(name, NULVCL)`.

**Fix 3 — indirect `$` LHS (`$'X'=`, `$V=`):** subject is `E_DOL(E_QLIT)` or `E_DOL(E_VART)`.
Currently the `has_eq` path only handles `E_VART`/`E_KW` subjects.
Add `E_DOL` subject case: eval inner expr → get string name → call `stmt_set_indirect`.
Add `stmt_set_indirect(DESCR_t name_val, DESCR_t val)` to `snobol4_stmt_rt.c`.
Add `SET_VAR_INDIR` macro.

Quick-check after fixes:
```bash
cd /home/claude/snobol4x && make -C src
CORPUS=/home/claude/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_rung.sh \
    $CORPUS/hello $CORPUS/output $CORPUS/assign $CORPUS/concat $CORPUS/arith 2>&1
# target: 26/28 PASS (fileinfo + triplet deferred to R8)
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh  # must stay 106/106
```

**Session186 — Sprint SC3 partial: sc_driver.h/c + main.c -sc wiring + Makefile; 106/106:**
- `src/frontend/snocone/sc_driver.h` — `sc_compile(source, filename) → Program*` API
- `src/frontend/snocone/sc_driver.c` — full pipeline: sc_lex → per-stmt sc_parse → sc_lower;
  ported directly from proven `pipeline()` helper in `sc_lower_test.c` (50/50 PASS session185)
- `src/driver/main.c` — `-sc` flag + `.sc` auto-detect via `ends_with()`; `read_all()` reads
  FILE* into heap buffer; Snocone path: `read_all → sc_compile → snoc_emit/asm_emit`;
  SNOBOL4 path unchanged
- `src/Makefile` — `FRONTEND_SNOCONE` block: `sc_lex.c sc_parse.c sc_lower.c sc_driver.c`;
  added to SRCS; `-I frontend/snocone` added to CFLAGS
- Build: zero errors/warnings (all 4 new objects + main.o recompile clean)
- 106/106 C crosscheck invariant unaffected
- BLOCKED: M-SNOC-EMIT not yet fired — `snoc_emit` generates no epilogue
  (`_SNO_END:` / `finish()` / `return 0;`) for Snocone path. SNOBOL4 frontend
  appends implicit END STMT_t; `sc_lower` does not. Fix: append synthetic END
  STMT_t in `sc_driver.c` after `sc_lower()` returns.

**Session185 — M-SNOC-LOWER: sc_lower.h + sc_lower.c + test; 50/50 PASS:**
- `src/frontend/snocone/sc_lower.h` — ScLowerResult (prog + nerrors), sc_lower() API,
  sc_lower_free() API; full operator mapping table in header comment
- `src/frontend/snocone/sc_lower.c` — postfix RPN evaluator: EXPR_t* operand stack
  (1024 slots), per-kind dispatch for all 40+ ScKind values;
  binary: E_ADD/E_SUB/E_MPY/E_DIV/E_EXPOP/E_CONC/E_OR/E_NAM/E_DOL;
  unary: E_MNS (SC_MINUS), E_INDR (SC_STAR/SC_DOLLAR), E_KW (SC_AMPERSAND),
         E_ATP (SC_AT), NOT/DIFFER (SC_TILDE/SC_QUESTION);
  fn-ops: EQ/NE/LT/GT/LE/GE/IDENT/DIFFER/LLT/LGT/LLE/LGE/LEQ/LNE/REMDR → E_FNC;
  SC_CALL → E_FNC(name, nargs); SC_ARRAY_REF → E_IDX(name, nargs);
  SC_ASSIGN → E_ASGN(lhs, rhs) then assembled into STMT_t at SC_NEWLINE boundary;
  statement assembly: E_ASGN → subject+replacement+has_eq; other → subject-only stmt
- `test/frontend/snocone/sc_lower_test.c` — 50 assertions: hello assign (trigger),
  arith (E_ADD/E_ILIT), fnc call (GT nargs=2), eq op (== → EQ), multi-stmt (2 stmts),
  OR (|| → E_OR), concat (&& → E_CONC), percent (% → REMDR), array ref (E_IDX),
  unary minus (E_MNS)
- Pipeline helper: splits at SC_NEWLINE, parses each segment independently, keeps
  ScParseResult alive until after sc_lower (text pointers shared), then frees
- M-SNOC-LOWER trigger: OUTPUT = 'hello' lowers to assignment STMT_t with E_QLIT rhs PASS
- 106/106 C crosscheck invariant unaffected

**⚠ CRITICAL NEXT ACTION — Session187 (frontend session):**

Sprint SC3 — M-SNOC-EMIT: fix program epilogue for Snocone path

**What's done (session186):**
- `src/frontend/snocone/sc_driver.h` + `sc_driver.c` — `sc_compile()` pipeline: sc_lex → per-stmt sc_parse → sc_lower; ported from proven pipeline() helper (50/50 PASS)
- `src/driver/main.c` — `-sc` flag + `.sc` auto-detect; `read_all()`; routes through `sc_compile()` then existing `snoc_emit`/`asm_emit`
- `src/Makefile` — `FRONTEND_SNOCONE` block; `sc_lower.c` + `sc_driver.c` in SRCS; `-I frontend/snocone` in CFLAGS
- Build clean, 106/106 ✅

**Blocking issue:** `snoc_emit` generates no program epilogue (`_SNO_END:` / `finish()` / `return 0;`) for the Snocone path. The SNOBOL4 parser appends an implicit `END` STMT_t; `sc_lower` does not.

**Fix — in `sc_driver.c`, after `sc_lower()` returns:**
```c
/* Append synthetic END statement so snoc_emit closes main() correctly */
static void prog_append_end(Program *prog) {
    STMT_t *end = calloc(1, sizeof(STMT_t));
    end->kind   = S_END;   /* or whatever the END sentinel kind is */
    end->lineno = 0;
    if (prog->tail) prog->tail->next = end;
    else            prog->head = end;
    prog->tail  = end;
    prog->nstmts++;
}
```

Check the actual STMT_t kind constant for END in `sno2c.h` / `emit.c` — search for `S_END` or `"END"` handling in `snoc_emit`. The SNOBOL4 parser adds it via `snoc_parse` → check `parse.c` for how it appends the END node.

After the fix, the M-SNOC-EMIT quick-check trigger must pass:
```bash
cd /home/claude/snobol4x
make -C src
echo "OUTPUT = 'hello'" > /tmp/t.sc
INC=/home/claude/snobol4corpus/programs/inc
RT=src/runtime
./sno2c -sc /tmp/t.sc > /tmp/t.c
gcc /tmp/t.c $RT/snobol4/snobol4.c $RT/mock/mock_includes.c \
    $RT/snobol4/snobol4_pattern.c $RT/mock/mock_engine.c \
    -I$RT/snobol4 -I$RT -Isrc/frontend/snobol4 -lgc -lm -w -o /tmp/t_bin
/tmp/t_bin
# expected output: hello
# PASS → M-SNOC-EMIT fires → begin Sprint SC4
```

Session start commands:
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = d01fb57
apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must be 106/106
```

**Session183 — M-SNOC-LEX: sc_lex.h + sc_lex.c + test; 187/187 PASS:**
- `src/frontend/snocone/sc_lex.h` — ScKind enum (48 kinds), ScToken, ScTokenArray, API
- `src/frontend/snocone/sc_lex.c` — tokenizer: # comment strip, continuation detection,
  semicolon split, longest-match 4→1 char operator table, keyword reclassification,
  integer/real/string/ident scanning. Direct port of snobol4jvm snocone.clj +
  snobol4dotnet SnoconeLexer.cs (both consulted — C# was the closest model to C)
- `test/frontend/snocone/sc_lex_test.c` — 187 assertions mirroring C# TestSnoconeLexer.cs:
  helpers, literals, all 12 keywords, all operators (longest-match), punctuation,
  statement boundaries, semicolons, line numbers, 12 E2E snippets
- M-SNOC-LEX trigger: `OUTPUT = 'hello'` → IDENT ASSIGN STRING NEWLINE EOF PASS
- 106/106 C crosscheck invariant unaffected; 26/26 ASM unaffected

**⚠ CRITICAL NEXT ACTION — Session184 (frontend session):**

Sprint SC1 — M-SNOC-PARSE: `src/frontend/snocone/sc_parse.c`

Recursive-descent parser consuming `ScToken[]` from sc_lex.
Produces `ScNode` AST. Port from snobol4jvm `snocone.clj` `parse-expression` +
snobol4dotnet `SnoconeParser.cs`.

Files:
- `src/frontend/snocone/sc_parse.h` — ScNode kinds + struct + `sc_parse()` API
- `src/frontend/snocone/sc_parse.c` — recursive descent: expr (shunting-yard from
  Clojure parse-expression), stmt, if/while/do/for/procedure/struct/goto/return/block
- `test/frontend/snocone/sc_parse_test.c` — mirrors TestSnoconeParser.cs

Quick-check trigger (M-SNOC-PARSE):
```bash
gcc -I src/frontend/snocone -o /tmp/sc_parse_test \
    test/frontend/snocone/sc_parse_test.c \
    src/frontend/snocone/sc_lex.c src/frontend/snocone/sc_parse.c
/tmp/sc_parse_test
# PASS → M-SNOC-PARSE fires → begin Sprint SC2
```


- `src/frontend/snobol4/` ← lex, parse, sno.l/y, sno2c.h (from src/sno2c/)
- `src/frontend/rebus/` ← rebus frontend (from src/rebus/)
- `src/frontend/icon/` ← Python parser prototypes (from src/parser/)
- `src/frontend/{snocone,prolog}/` ← placeholders
- `src/ir/byrd/` ← emit_cnode.c/.h + byrd_ir/ir/lower.py (from src/sno2c/ + src/ir/)
- `src/backend/c/` ← emit.c, emit_byrd.c, trampoline files (from src/sno2c/)
- `src/backend/x64/` ← emit_byrd_asm.c (from src/sno2c/)
- `src/backend/{jvm,net}/` ← Python stubs (from src/codegen/)
- `src/driver/main.c` ← compiler entry point (from src/sno2c/)
- `src/runtime/mock/` ← mock_engine.c, mock_includes.c (from src/runtime/ + src/runtime/snobol4/)
- `src/runtime/engine/` ← engine.c/.h, runtime.c/.h (from src/runtime/)
- `src/runtime/runtime.h` + `src/runtime/engine.h` ← forwarding shims for relative includes
- `artifacts/c/beautiful.c` ← generated file moved out of runtime source tree
- `test/frontend/snobol4/` ← .sno fixtures (from test/sprintN/)
- `test/backend/c/` ← .c + .py oracles (from test/sprintN/)
- `scratch/` ← gitignored working dir
- `sno2c` ← binary now at repo root (was src/sno2c/sno2c)
- `src/Makefile` ← new build root
- Scan-retry omega fix: `jg next_lbl` → `jg tgt_f` in omega block of `asm_emit_program`
  Fixes 034_goto_failure, 057_pat_fail_builtin, 098_keyword_anchor
- beauty_prog.s artifact updated, NASM clean
- 106/106 C PASS ✅, 26/26 ASM PASS ✅

**Session168 — FAIL_BR/FAIL_BR16/SUBJ_FROM16 renames; CONC2/ALT2 macros; COL2_W=12; CONC2_N/CONC2 fast paths:**
- `IS_FAIL_BRANCH` → `FAIL_BR` (14→7 chars); `IS_FAIL_BRANCH16` → `FAIL_BR16` (16→8 chars)
- `SETUP_SUBJECT_FROM16` → `SUBJ_FROM16` (20→11 chars)
- `CALL2_SS` → `CONC2`, `CALL2_SN` → `CONC2_N`; `ALT2`/`ALT2_N` aliases added (same expansion)
- All back-compat `%define` aliases preserved — existing `.s` files still assemble
- `COL2_W=12`, `COL_CMT=72` defined in `emit_byrd_asm.c`; `ALFC` comment column uses `COL_CMT`
- `CONC2_N`/`CONC2` fast paths in `E_OR`/`E_CONC` for `QLIT+NULV` and `QLIT+QLIT` children (7 sites)
- Three emit sites updated: `FAIL_BR`, `FAIL_BR16`, `SUBJ_FROM16`
- beauty_prog_session168.s: 12689 lines (down 56 from session167), assembles clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**Session171 — CONC2_SV/VS/VN/VV fast paths; 12444 lines:**
- `CONC2_SV/VS/VN/VV` + `ALT2_SV/VS/VN/VV` macros added to `snobol4_asm.mac`
- Six new fast paths in `emit_byrd_asm.c` E_OR/E_CONC — all two-atom shapes now covered
- 12689 → 12444 lines (−245); 529 verbose `sub rsp,32` blocks remain (nested expr trees)
- 106/106 26/26

**Session170 — REF/DOL/ARBNO block-header comments to col2 on label line:**
- `asmLC(lbl, comment)` helper: emits `label: ; comment\n` with no instruction
- Three standalone `A("\n; ...")` sites (REF/DOL/ARBNO) converted to `asmLC` on alpha label
- `ALFC` empty-label guard: suppresses bare `:` when label is `""`
- 12689 lines unchanged, NASM clean, 106/106 26/26

**Session169 — SEP_W 80→120:**
- `SEP_W` 80 → 120; separator lines now 120 chars (Cherryholmes standard)
- Four-column layout retained as-is per Lon's decision
- 12689 lines, 106/106 26/26

**Session175 — col3 alignment perfected; emit_instr() helper; 11594→11654 lines:**
- `emit_instr(instr)` helper added: emits opcode word, pads to COL_W+COL2_W=40, then operands
- Three paths fixed: `asmLB()` (ALF), `ALFC` macro inline expansion, `A()` pending-label fold
- Before: 901 instruction lines misaligned (706 `jmp`/`sub`/`mov` at col 37, 38 macros at col 42)
- After: 0 misaligned instruction lines; every line: label@0, opcode@28, operands@40
- `asmLC` comment-only lines (`label: ; comment`) correctly exempt — no opcode/operand split
- beauty_prog_session175.s: 11654 lines, NASM clean, 106/106 26/26

**session177 — housekeeping; artifact reorg; test baseline:**
- M-ASM-IR deferred — IR shape unknown until both backends mature
- M-MONITOR retargeted to ASM backend
- Artifact protocol: canonical files only, asm/c/jvm/net folders, no numbered copies
- ASM corpus baseline: 47/113 PASS; 16 NASM_FAIL (2 root causes); 38 FAIL; 12 TIMEOUT
- Next: fix arithmetic (7 tests), fix 2 NASM_FAIL root causes (15 tests), then M-MONITOR

**⚠ CRITICAL NEXT ACTION — Session178:**

Fix corpus tests in priority order:
1. **Arithmetic (023–029, 7 tests):** `prog_emit_expr` for `E_ADD`/`E_SUB`/`E_MPY`/`E_DIV`/`E_EXP`/`E_NEG` — currently returning empty. Check `stmt_apply` calls in `snobol4_stmt_rt.c` for arithmetic ops.
2. **NASM_FAIL `P_X_ret_gamma`** (9 tests: 009–013, 019, 056 + others) — named pattern return slot not declared when pattern appears inline in assignment RHS. Fix: ensure `AsmNamedPat` registry entries are emitted for all referenced patterns.
3. **NASM_FAIL `P_1_α_saved`** (6 tests: 033–035, 038, 062–064) — ALT cursor save slot missing in statement-context pattern. Fix: ensure `.bss` slot is declared for every ALT node regardless of context.

Then Sprint M1 (M-MONITOR): build `snobol4harness/monitor/` runner targeting ASM backend.
1. Declare `.bss` scratch pair: `conc_tmp0_rax resq 1` / `conc_tmp0_rdx resq 1`
2. For each complex child: evaluate normally (result in `[rbp-32/24]`), then `mov rax,[rbp-32]; mov [conc_tmp0_rax],rax` etc.
3. Build args array using scratch values
4. New macros `CONC2_TV/VT/TS/TN` for temp+atom patterns
5. Target: 15 → 0 verbose blocks; further line-count reduction toward M-ASM-BEAUTIFUL

**Session174 — CALL1_VAR + integer-arg fast paths; 12594→11594 lines:**
- `CALL1_VAR fn, varlab` macro + emitter fast path: 1-arg calls with E_VART arg (100 cases) → single macro
- `CONC2_VI/IV/II/NI/SI/IS` + `*16` variants: 2-arg calls with integer-literal args → macros
- `CONC2_NN` macro added (NULVCL+NULVCL)
- 77 verbose `sub rsp,32` blocks → 15; all 15 have genuinely complex children (E_IDX/E_SUB/E_FNC/E_NAM)
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS
- beauty_prog_session174.s: 11594 lines (−1000 from session173), NASM clean

**⚠ CRITICAL NEXT ACTION — Session175:**

The 15 remaining verbose blocks all have complex children (confirmed by debug probe: a0kind/a1kind ∈ {E_IDX=20, E_SUB=9, E_FNC=18, E_NAM=16}). These cannot use atom fast paths.

**Generic fallback path explanation:**
The `prog_emit_expr` generic fallback fires when no fast path matches. It allocates an N-slot args array on the stack (`sub rsp, N*16`), then for each arg calls `prog_emit_expr(arg, rbp_off)` recursively — which stores the result into `[rbp-32/24]`, then `STORE_ARG32 k` copies it into `[rsp + k*16]`. After all args: `APPLY_FN_N fn, N` calls the function, `add rsp, N*16` restores the stack, then `STORE_RESULT` / `mov [rbp±n]` saves rax/rdx.

The problem: when a complex child is evaluated, `prog_emit_expr` recurses and overwrites `[rbp-32/24]`. If that child is itself an `APPLY_FN_N` call, it issues another `sub rsp,32` — nested `sub rsp` is what we see in the output. The result-temp strategy breaks this cycle:

**Result-temp strategy:**
1. Declare `.bss` scratch pair: `conc_tmp0_rax resq 1` / `conc_tmp0_rdx resq 1`
2. For each complex child: evaluate it normally (gets result in `[rbp-32/24]`), then `mov rax,[rbp-32]; mov [conc_tmp0_rax],rax` etc. to save into scratch
3. Then build the args array using `mov rax,[conc_tmp0_rax]` → `mov [rsp],rax` etc.
4. One scratch pair per nesting depth suffices since children are evaluated sequentially

Implementation in `prog_emit_expr` E_FNC generic path: detect when any arg is complex, emit scratch `.bss` declarations in the `.bss` section header pass, then use save/restore around each complex arg evaluation.

**Session173 — col3 alignment; no fourth column; sep→label fold:**
- col3: operands now at COL_W+COL2_W=40 — A() scans opcode end, pads to col 40 before operands
- No 4th column: ALFC uses one space before `;` (was padding to COL_CMT=72)
- Sep→label: emit_sep_major buffers into pending_sep; A() fold path emits `; sep` immediately before `label:  INSTR` (no blank gap between sep and label)
- Non-label sep sites (PROGRAM BODY, END, NAMED PATTERN BODIES, STUB LABELS, STRING TABLE) use flush_pending_sep()
- 12594 lines; 496 verbose sub-rsp,32 blocks remain (unchanged — formatting only); NASM clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**Session172 — CONC2_*16/ALT2_*16 macros; E_FNC 2-arg fast paths; 529→496 verbose blocks:**
- `CONC2_16/CONC2_N16/CONC2_SV16/CONC2_VS16/CONC2_VN16/CONC2_VV16` + `ALT2_*16` aliases added to `snobol4_asm.mac` — result stored at `[rbp-16/8]` (subject slot)
- E_FNC 2-arg fast paths added in `emit_byrd_asm.c`: detect atom arg shapes (SS/SN/SV/VS/VN/VV) for both `rbp_off==-32` and `rbp_off==-16`, emit CONC2_* macros (which work for any fn label, not just CONCAT/ALT)
- Diagnosis: 529 blocks split into two root causes: (a) E_FNC 2-arg with atom children at rbp_off==-16 (now fixed), (b) E_CONC/E_OR/E_FNC with complex (non-atom) children (440 blocks remain — need result-temp strategy)
- 12444 → 12100 lines (−344); 529 → 496 verbose blocks; NASM clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION — Session173:**

Remaining 496 verbose `sub rsp, 32` blocks have at least one complex (non-atom) child. Survey the shapes: from prior classification, ~188 are `E_CONC/E_OR` with `left=other right=NUL slot=-32` (left child is itself `E_CONC`/`E_OR`/`E_FNC`). Strategy: **CONC3 survey** — check if the dominant nested shape is `CONCAT(CONCAT(atom,atom), atom)` collapsible with a 3-arg macro.

Steps:
1. Classify remaining 496 blocks: for each, what is the left child's shape (E_CONC? E_FNC? depth?)
2. If dominant shape is depth-2 left-associative CONCAT chains → add `CONC3` macro + emitter fast path
3. Otherwise → result-temp strategy per session172 plan

Evaluate complex child into a `.bss` scratch pair (`conc_tmp_rax`, `conc_tmp_rdx`), then collapse with new macros:
- `CONC2_TV fn, tmplab, varlab` — fn(pre-computed-temp, variable)
- `CONC2_VT fn, varlab, tmplab` — fn(variable, pre-computed-temp)
- `CONC2_TS fn, tmplab, strlab` — fn(pre-computed-temp, str)
- `CONC2_TN fn, tmplab`         — fn(pre-computed-temp, NULVCL)

Emitter change: in `E_OR`/`E_CONC` generic path, detect when left/right is a simple atom vs complex; for complex-left+atom-right patterns, emit `sub rsp,32` + inline-evaluate-left + `STORE_ARG32 0` + macro for right half.

Alternatively: survey the 230 double-sub (nested) cases — these may all be `CONCAT(CONCAT(atom,atom), atom)` and collapsible with a `CONC3` 3-arg macro.

The dominant `CONCAT(E_QLIT, E_VART)` shape — string literal left, variable right — accounts for the bulk of the ~409 remaining verbose blocks (each 10 lines). Add `CONC2_SV` macro and fast path:

**Macro** (`snobol4_asm.mac`):
```nasm
; CONC2_SV fn, strlab, varlab  — fn(str_literal, variable) → [rbp-32/24]
%macro CONC2_SV 3
    sub     rsp, 32
    lea     rdi, [rel %2]
    call    stmt_strval
    mov     [rsp], rax
    mov     [rsp+8], rdx
    lea     rdi, [rel %3]
    call    stmt_get
    mov     [rsp+16], rax
    mov     [rsp+24], rdx
    lea     rdi, [rel %1]
    mov     rsi, rsp
    mov     rdx, 2
    call    stmt_apply
    add     rsp, 32
    mov     [rbp-32], rax
    mov     [rbp-24], rdx
%endmacro
%define ALT2_SV CONC2_SV
```

**Emitter** (`emit_byrd_asm.c`, `E_OR`/`E_CONC` case, after existing fast paths):
```c
int right_is_var = e->right && e->right->kind == E_VART;
if (left_is_str && right_is_var && rbp_off == -32) {
    const char *mac_sv = (e->kind == E_OR) ? "ALT2_SV " : "CONC2_SV";
    const char *slab = prog_str_intern(e->left->sval);
    const char *vlab = prog_str_intern(e->right->sval);
    A("    %s %s, %s, %s\n", mac_sv, fnlab, slab, vlab);
    return 1;
}
```

Also add `CONC2_VN` (variable left, NULVCL right) and `CONC2_VV` (two variables) for further coverage.

**Session169 start commands:**
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = d872625

apt-get install -y libgc-dev nasm && make -C src/sno2c
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```
- `ASSIGN_INT var, n, fail_lbl` — collapses LOAD_INT + IS_FAIL_BRANCH + SET_VAR (6 lines → 1)
- `ASSIGN_STR var, s, fail_lbl` — collapses LOAD_STR + IS_FAIL_BRANCH + SET_VAR (6 lines → 1)
- `CALL1_INT fn, n` — collapses sub rsp + LOAD_INT + STORE_ARG32 + APPLY_FN_N + add rsp + mov-pair (9 lines → 1)
- `CALL1_STR fn, s` — same with string literal arg
- Redundant `mov [rbp-32],rax` / `mov [rbp-24],rdx` after LOAD_INT/LOAD_STR eliminated
- Post-APPLY_FN_N mov pair → STORE_RESULT macro
- `emit_sep_major(tag)` — `; === tag ====...` (80 cols, configurable SEP_W) at every SNOBOL4 stmt, section headers, named pattern headers; source label embedded when present
- `emit_sep_minor(tag)` — `; --- tag ----...` before γ/ω trampolines in named pattern defs
- STMT_SEP NASM macro bypassed — separators are raw comment text, visible without expansion
- beauty_prog_session167.s: 12745 lines (down 919 from session166), assembles clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION — Session168:**

Continue M-ASM-BEAUTIFUL: the multi-arg E_OR/E_CONC (ALT/CONCAT) 2-arg calls still emit verbose sub/LOAD/STORE/APPLY/add sequences. Add `CALL2_SS`, `CALL2_SN` macro fast-paths in emit_byrd_asm.c E_OR/E_CONC case (macros already in snobol4_asm.mac from session167). Also: L_sn_10 still has a deeply nested raw sequence — the CALL2_SS/SN paths will collapse it.

**Session165 — inline column alignment (COL_W=28):**
- Added `out_col` tracker + `oc_char()`/`oc_str()`/`emit_to_col()` in emit_byrd_asm.c
- `oc_char()` counts display columns, skips UTF-8 continuation bytes (α/β/γ/ω = 1 col each)
- `emit_to_col(n)`: pads to col n; if already past n, emits newline then pads
- Every instruction (labeled or unlabeled) now starts at display column 28
- ALFC fixed: was using `%-28s` printf padding (byte-based), now uses `oc_str`+`emit_to_col`
- STMT_SEP/PORT_SEP/directives/section/.bss exempt from col-28 alignment
- Comment column: COL_W+44=72; non-wrapping (one space if instruction already past col 72)
- beauty_prog_session165.s: 13664 lines, assembles clean, 0 misaligned lines
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION — Session166:**

Lon reviews `beauty_prog_session165.s` → M-ASM-BEAUTIFUL fires, OR next step toward decoupled emitter/beautifier (separate concerns as done for C backend).

**Session167 start commands:**
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3
apt-get install -y libgc-dev nasm && make -C src/sno2c
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```

**Session163 — four-column format complete: label: MACRO args ; comment**
- DOL_SAVE macro: 3 raw instructions → 1 line
- DOL_CAPTURE macro: 9 raw instructions → 1 line
- ALT_ALPHA macro: absorbs trailing jmp lα
- ALT_OMEGA macro: absorbs trailing jmp rα
- All \n\n double-newlines removed (45 instances)
- Every state is one line: `label:  MACRO args ; comment`
- beauty_prog_session163.s: 14448 lines (down 3772 from session159), assembles clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION:**
Lon reviews `artifacts/asm/beauty_prog_session163.s` → M-ASM-BEAUTIFUL fires.

**HEAD (previous):** `6ed79c5` session162
**Milestone:** M-ASM-CROSSCHECK ✅ session151 → **M-ASM-BEAUTIFUL** (A14, active)

**Session162 — three-column format: label: MACRO args ; comment:**
- Added `ALFC(lbl, comment, fmt, ...)` — folds preceding comment line onto instruction line
- Result: `seq_l26_alpha:  LIT_ALPHA lit_str_6, 2, ... ; LIT α`
- ALT emitter fully uses ALT_SAVE_CURSOR/ALT_RESTORE_CURSOR macros
- beauty_prog_session162.s: 14950 lines (down 3270 from session159), assembles clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION:**
Lon reviews `artifacts/asm/beauty_prog_session162.s` → M-ASM-BEAUTIFUL fires.

**HEAD (previous):** `0f7f20b` session161
**Milestone:** M-ASM-CROSSCHECK ✅ session151 → M-ASM-BEAUTY (A10, blocked 102-109) → **M-ASM-BEAUTIFUL** (A14, active)

**Session161 — label: MACRO args on one line:**
- Added `ALF(lbl, fmt, ...)` helper — emits `label:  INSTRUCTION args` on one line
- 40 `asmL()+A()` and `asmL()+asmJ()` pairs folded into single `ALF()` calls
- Every Byrd box port: `seq_l26_alpha:  LIT_ALPHA lit_str_6, 2, saved, cursor, ...`
- beauty_prog_session161.s: 15883 lines (was 16421 — 538 more eliminated), assembles clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION — Sprint A14 (M-ASM-BEAUTIFUL):**
Lon reviews `artifacts/asm/beauty_prog_session161.s` → M-ASM-BEAUTIFUL fires.

**Session160 — M-ASM-BEAUTIFUL: all pattern port macros landed:**
- All primitive emitters replaced with one macro call per port:
  LIT_ALPHA/LIT_BETA, SPAN_ALPHA/SPAN_BETA, BREAK_ALPHA/BREAK_BETA,
  ANY_ALPHA/ANY_BETA, NOTANY_ALPHA/NOTANY_BETA, POS_ALPHA/POS_BETA,
  RPOS_ALPHA/RPOS_BETA, LEN_ALPHA/LEN_BETA, TAB_ALPHA/TAB_BETA,
  RTAB_ALPHA/RTAB_BETA, REM_ALPHA/REM_BETA, SEQ_ALPHA/SEQ_BETA,
  ALT_SAVE_CURSOR/ALT_RESTORE_CURSOR, STORE_RESULT/SAVE_DESCR
- snobol4_asm.mac extended with all port macros (811 lines)
- emit_byrd_asm.c: all raw instruction sequences replaced; each port = 1 emitted line
- Body-only (-asm-body) now emits `%include "snobol4_asm.mac"`
- run_crosscheck_asm.sh: nasm -I src/runtime/asm/ added
- beauty_prog_session160.s: 16421 lines (was 18220 — 1799 eliminated), assembles clean
- 106/106 C crosscheck PASS, 26/26 ASM crosscheck PASS

**⚠ CRITICAL NEXT ACTION — Sprint A14 (M-ASM-BEAUTIFUL):**

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 0f7f20b

apt-get install -y libgc-dev nasm
make -C src/sno2c

mkdir -p /home/snobol4corpus
ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```

**M-ASM-BEAUTIFUL fires** when Lon reads `beauty_prog_session160.s` and declares it beautiful.

**Session158 — M-ASM-BEAUTY progress — 101_comment PASS:**
- `section .text` before named pattern bodies (was `.data` → segfault → **root cause**)
- Stack alignment: `sub rsp,56` (6 pushes + 56 = 112, 112%16=0 ✅)
- `PROG_END`: explicit pops (not `leave`)
- `E_FNC` → `stmt_apply()` in `prog_emit_expr`
- Case 1 S/F dispatch: expression-only stmts with `:F(label)` now check `is_fail`
- `stmt_set_capture()`: DOL/NAM captures materialised into SNOBOL4 variables
- Pattern capture: `X *PAT . V` → `V='bc'` PASS ✅
- **101_comment PASS ✅** — 102-109 `Parse Error`
- Root cause of Parse Error: `E_OR`/`E_CONC` → NULVCL for named pattern assignments

**⚠ CRITICAL NEXT ACTION — Sprint A10 (M-ASM-BEAUTY):**

**102-109 fail with `Parse Error`** — beauty's `*Parse` named pattern is assigned
using `E_OR` (alternation `|`) and `E_CONC` (concatenation) expressions.
These are currently fallback → NULVCL in `prog_emit_expr`.
Fix: register `pat_alt()` and `pat_concat()` as callable functions `ALT`/`CONCAT`,
add `E_OR` and `E_CONC` cases to `prog_emit_expr` that call `stmt_apply()`.

**File:** `src/sno2c/emit_byrd_asm.c` — `prog_emit_expr()` switch
**File:** `src/runtime/snobol4/snobol4.c` — add `_b_PAT_ALT`, `_b_PAT_CONCAT`, register

**Session151 — M-ASM-CROSSCHECK fires — 26/26 ASM PASS:**
- Per-variable capture buffers: `CaptureVar` registry, `cap_VAR_buf`/`cap_VAR_len` in `.bss`
- `cap_order[]` table in `.data` — harness walks it at `match_success`, one capture per line
- `E_INDR` case added to `emit_asm_node` — `*VAR` indirect pattern reference resolved via named-pattern registry
- `/dev/null` dry-run collection pass: replaces `open_memstream` two-pass; uid counter saved/restored so real pass generates identical labels
- `.asm.ref` convention: capture tests with harness-specific output use `TEST.asm.ref`; `run_crosscheck_asm.sh` prefers `.asm.ref` over `.ref`
- `run_crosscheck_asm.sh`: `extract_subject` now finds subject var from match line first; `build_bare_sno` keeps plain-string assignments when var referenced as `*VAR`
- 106/106 main crosscheck invariant holds; HEAD `3624d9d`

**⚠ CRITICAL NEXT ACTION — Sprint A10 (M-ASM-BEAUTY):**

Session154 state:
- `asm_emit_program()` walks all stmts, emits `main()` with `stmt_*` C-shim calls
- Label scheme: `_L_<alnum_base>_<N>` — N guarantees uniqueness, base aids readability
- `emit_jmp()` handles RETURN/FRETURN/END → `_SNO_END`; stub labels for undefined/computed gotos
- beauty.sno assembles and links cleanly via `-asm`
- Statement-only programs work: `OUTPUT = 'hello'` → correct output ✅
- **beauty.sno hangs**: pattern-match stmts (Case 2) fall through without running the pattern

**Next step — pattern-match stmt execution:**
Case 2 must: (1) get subject string via `stmt_get()`, (2) set `subject_data`/`subject_len_val`/`cursor` globals, (3) call `root_alpha` (Byrd box), (4) on `match_success` → apply replacement + goto S-label; on `match_fail` → goto F-label.
Approach: inline Byrd box + C-shim `match_success`/`match_fail` as ASM labels per stmt.

- `ref_astar_bstar.s`: ASTAR=ARBNO("a"), BSTAR=ARBNO("b") on "aaabb" → `aaabb\n` PASS ✅
- `anbn.s`: 4 sequential named-pattern call sites (2×A_BLOCK + 2×B_BLOCK) on "aabb" → `aabb\n` PASS ✅
- `emit_byrd_asm.c`: `AsmNamedPat` registry + `asm_scan_named_patterns()` pre-pass + `emit_asm_named_ref()` call-site + `emit_asm_named_def()` body emitter; `E_VART` wired in `emit_asm_node`
- Named pattern calling convention: Proebsting §4.5 gate — caller stores γ/ω absolute addresses into `pat_NAME_ret_gamma/omega` (.bss qwords), then `jmp pat_NAME_alpha/beta`; body ends `jmp [pat_NAME_ret_gamma/omega]`. No call stack.
- 106/106 crosscheck invariant confirmed; end-to-end `.sno → sno2c -asm → nasm → ld → run` verified

**⚠ CRITICAL NEXT ACTION — Sprint A9 (M-ASM-CROSSCHECK):**

The crosscheck corpus (`crosscheck/patterns/038_pat_literal.sno` etc.) are full SNOBOL4 programs using `OUTPUT`, variables, `:S(YES)F(NO)` gotos — **not** standalone pattern tests. The ASM backend currently only handles pattern-match nodes; it cannot yet compile full SNOBOL4 statements.

**Sprint A9 is therefore scoped differently than A0–A8:**

The path to M-ASM-CROSSCHECK is NOT "run existing crosscheck suite via -asm" — those tests require the full runtime (OUTPUT, goto, variables). Instead:

**Sprint A9 plan — ASM crosscheck harness:**
1. Write `src/runtime/asm/snobol4_asm_harness.c` — thin C harness:
   - Reads subject string from `argv[1]` (or stdin)
   - Declares `extern` symbols: `cursor`, `subject_data`, `subject_len_val`, `match_success`, `match_fail`
   - Provides `_start`-equivalent in C: initialises slots, calls `root_alpha` via function pointer or inline asm `jmp`
   - On `match_success`: prints matched span `subject[0..cursor]` to stdout, exit 0
   - On `match_fail`: exit 1
2. Update emitter: body-only mode (no `_start`, no `match_success/fail`) — extern the cursor/subject symbols
3. New crosscheck driver: for each `crosscheck/capture/*.sno` and `crosscheck/patterns/*.sno`, extract the pattern + subject, compile body-only `.s`, link with harness, run, diff
4. First target: `038_pat_literal` via harness PASS → grow to 106/106

**Key insight from corpus survey (session148):**
- `crosscheck/patterns/` has `038_pat_literal.sno` through `047_pat_rtab.sno` — pure pattern tests
- `crosscheck/capture/` has `058_capture_dot_immediate.sno` through `062_capture_replacement.sno`
- These are the natural first targets for ASM crosscheck since they exercise only pattern nodes

**Sprint A9 steps:**
1. `snobol4_asm_harness.c` — subject from argv[1], `extern` ASM symbols, C `_start`
2. `emit_byrd_asm.c` body-only mode: `-asm-body` flag, no `_start`/`match_success`/`match_fail`, emit `global root_alpha, root_beta` + `extern cursor, subject_data, subject_len_val`
3. `test/crosscheck/run_crosscheck_asm.sh` — new driver extracting pattern+subject from `.sno`, compiling+linking with harness, diffing output
4. `038_pat_literal` PASS → iterate to all patterns/ + capture/ rungs → M-ASM-CROSSCHECK

**PIVOT (session144):** Abandoned `monitor-scaffold` / `bug7-bomb` in favor of x64 ASM backend.
Rationale: C backend has a fundamental structural problem — named patterns require C functions
with reentrant structs, three-level scoping (`z->field`, `#define`/`#undef`), and `calloc` per
call. x64 ASM eliminates all of this: α/β/γ/ω become real ASM labels, all variables live flat
in `.bss`, named patterns are plain labels with a 2-way `jmp` dispatch. One scope. No structs.

**Architecture (session144):**
```
Frontend (lex/parse)     →     IR (Byrd Box)     →     Backend (emit/interpret)

SNOBOL4 reader                                          C emitter       ← existing, keep
Rebus reader              α/β/γ/ω four-port IR          x64 ASM emitter ← NEW PIVOT TARGET
Snocone reader            (byrd_ir.py / emit_byrd.c)    Interpreter     ← future debug tool
Icon reader
Prolog reader
```
5 frontends × 3 backends = 15 combinations. One IR. One compiler driver.

**Next steps (Sprint A0):**
1. Create `src/sno2c/emit_byrd_asm.c` — skeleton, mirrors emit_byrd.c structure.
2. Add `-asm` flag to `main.c` selecting ASM backend, output `.s` file.
3. NASM syntax, x64 Linux ELF64.
4. Emit null program: assemble (`nasm -f elf64`), link (`ld`), run → exit 0.
5. **M-ASM-HELLO fires** → begin Sprint A1 (LIT node).

---

## Milestone Map

| Milestone | Trigger | Status | Sprint |
|-----------|---------|--------|--------|
| **M-ASM-HELLO** | null.s assembles, links, runs → exit 0 | ✅ session145 | A0 |
| **M-ASM-LIT** | LIT node: lit_hello.s PASS | ✅ session146 | A1 |
| **M-ASM-SEQ** | SEQ/POS/RPOS: cat_pos_lit_rpos.s PASS | ✅ session146 | A2–A3 |
| **M-ASM-ALT** | ALT: alt_first/second/fail PASS | ✅ session147 | A4 |
| **M-ASM-ARBNO** | ARBNO: arbno_match/empty/fail PASS | ✅ session147 | A5 |
| **M-ASM-CHARSET** | ANY/NOTANY/SPAN/BREAK PASS | ✅ session147 | A6 |
| **M-ASM-ASSIGN** | $ capture: assign_lit/digits PASS | ✅ session148 | A7 |
| **M-ASM-NAMED** | Named patterns: ref_astar_bstar/anbn PASS | ✅ session148 | A8 |
| **M-ASM-CROSSCHECK** | 26/26 ASM crosscheck PASS | ✅ session151 | A9 |
| **M-ASM-R1** | hello/ + output/ — 12 tests PASS via run_crosscheck_asm_rung.sh | ❌ | A-R1 |
| **M-ASM-R2** | assign/ — 8 tests PASS | ❌ | A-R2 |
| **M-ASM-R3** | concat/ — 6 tests PASS | ✅ session187 | A-R3 |
| **M-ASM-R4** | arith/ — 2 tests PASS | ❌ | A-R4 |
| **M-ASM-R5** | control/ + control_new/ PASS | ❌ | A-R5 |
| **M-ASM-R6** | patterns/ program-mode 20 tests PASS | ❌ | A-R6 |
| **M-ASM-R7** | capture/ — 7 tests PASS | ❌ | A-R7 |
| **M-ASM-R8** | strings/ — 17 tests PASS | ❌ | A-R8 |
| **M-ASM-R9** | keywords/ — 11 tests PASS | ❌ | A-R9 |
| **M-ASM-R10** | functions/ — DEFINE/RETURN/recursion PASS | ❌ | A-R10 |
| **M-ASM-R11** | data/ — ARRAY/TABLE/DATA PASS | ❌ | A-R11 |
| **M-ASM-SAMPLES** | roman.sno + wordcount.sno PASS | ❌ | A-S1 |
| **M-ASM-BEAUTY** | beauty.sno self-beautifies via ASM backend | ❌ | A10 |
| **M-ASM-READABLE** | Label names: special-char expansion (pp_>= → S_pp_GT_EQ); _ literal passthrough; uid on collision only. Original bijection spec revised — expanding _ destroys readability for normal names. M-ASM-READABLE-A. | ✅ `e0371fe` session176 | A11 |
| **M-ASM-BEAUTIFUL** | beauty_prog.s as readable as beauty_full.c. Lon reads it and declares it beautiful. | ✅ `7d6add6` session175 | A14 |
| **M-REORG** | Full repo layout: frontend/ ir/ backend/ driver/ runtime/; binary at snobol4x/sno2c; 106/106 26/26 | ✅ `f3ca7f2` session181 | — |
| M-BOOTSTRAP | sno2c_stage1 output = sno2c_stage2 | ❌ | final goal |



**ASM backend design (session144):**

Why ASM solves the C structural problem:
- C named patterns require functions with reentrant structs (`pat_X_t *z`), `calloc` per call,
  three-level scoping (`z->field` + `#define`/`#undef` aliases), and `open_memstream` two-pass
  declaration collection. Bug5/Bug6/Bug7 all trace back to this complexity.
- x64 ASM: α/β/γ/ω become real labels. All variables are flat `.bss` qwords declared once at
  top of file. Named patterns are plain labels with a 2-instruction entry dispatch. One scope.
  No structs. No malloc. No scoping tricks.

**Sprint detail:**

| Sprint | What | Key oracle |
|--------|------|-----------|
| A0 | Skeleton + `-asm` flag + null program | `test/sprint0/null.s` |
| A1 | LIT node — inline byte compare | `test/sprint1/lit_hello.s` |
| A2 | POS / RPOS — pure compare, no save | `test/sprint2/pos0_rpos0.s` |
| A3 | SEQ (CAT) — wire α/β/γ/ω between nodes | `test/sprint2/cat_pos_lit_rpos.s` |
| A4 | ALT — left/right arms + backtrack | `test/sprint3/alt_*.s` |
| A5 | ARBNO — depth counter + cursor stack in `.bss` | `test/sprint5/arbno_*.s` |
| A6 | Charset: ANY/NOTANY/SPAN/BREAK — inline scan | corpus rungs |
| A7 | $ capture — span into flat `.bss` buffer | `test/sprint4/assign_*.s` |
| A8 | Named patterns — flat labels, 2-way jmp dispatch | `test/sprint6/ref_*.s` |
| A9 | Full crosscheck 106/106 via ASM backend | crosscheck suite |
| A10 | beauty.sno → ASM → self-beautify | M-ASM-BEAUTY |
| A11 | Label named expansion: pp_>= → L_pp_GT_EQ_N | M-ASM-READABLE |
| A12 | NASM macro library snobol4_asm.mac; emit uses macros; 3-column .s | M-ASM-MACROS |
| A13 | ASM IR phase (CNode-equivalent); separate tree walk from emit | M-ASM-IR |
| A14 | Generated .s as readable as generated .c | M-ASM-BEAUTIFUL |

**Build commands (ASM backend):**
```bash
cd /home/claude/snobol4x
# Install NASM once:
apt-get install -y nasm
# Compile a .sno to .s:
src/sno2c/sno2c -asm myprog.sno > myprog.s
# Assemble + link:
nasm -f elf64 myprog.s -o myprog.o
ld myprog.o src/runtime/snobol4/snobol4_asm.o -o myprog
# Run:
./myprog
```


---

## Confirmed Passing (session116 WIP)

- 101_comment ✅
- 102_output  ✅
- 103_assign  ✅
- 104_label   ✅ (WIP binary)
- 105_goto    ✅ (WIP binary)
- 106/106 rungs 1–11 ✅

---

## Bug History

**Bug7 — ACTIVE:** Ghost frame from Expr17 FENCE arm 1 (nPush without nPop on ω).
**Also check Expr15:** FENCE(nPush() *Expr16 ... nPop() | epsilon) same issue.
**Bug6a — FIXED in WIP (session115):** `:` lookahead guard in pat_X4 cat_r_168.
**Bug6b — FIXED in WIP (session115):** NV_SET_fn for Brackets/SorF; CONCAT_fn Reduce type.
**Bug5 — FIXED in WIP (session114); emit_byrd.c port IN PROGRESS (session116).**
**Bugs 3/4 — FIXED `4c2ad68`.**

---

## Frontend × Backend Frontier

| Frontend | C backend | x64 ASM | .NET MSIL | JVM bytecodes |
|----------|:---------:|:-------:|:---------:|:-------------:|
| SNOBOL4/SPITBOL | ⏳ Sprint A | — | — | — |
| Rebus | ✅ M-REBUS | — | — | — |
| Snocone | — | — | — | — |
| Tiny-ICON | — | — | — | — |
| Tiny-Prolog | — | — | — | — |

✅ milestone fired · ⏳ active · — planned

---

## M-BEAUTY-CORE Sprint Plan

### What beauty.sno does (essential model)

One big PATTERN matches the entire source. Immediate assignments (`$`) orchestrate
two stacks simultaneously during the match:

**Counter stack** — tracks children per syntactic level:
```
nPush()                  push 0       entering a level
nInc()                   top++        one more child recognized
Reduce(type, ntop())     read count   build tree node — fires BEFORE nPop
nPop()                   pop          exit the level — fires AFTER Reduce
```

**Value stack:**
```
shift(p,t)   pattern constructor — builds p . thx . *Shift('t', thx)
reduce(t,n)  pattern constructor — builds '' . *Reduce(t,n)
Shift(t,v)   match-time worker — push leaf node
Reduce(t,n)  match-time worker — pop n nodes, push internal node
~ is opsyn for shift · & is opsyn for reduce
```

**Invariant:** every `nPush()` must have exactly one `nPop()` on EVERY exit path —
success (γ) AND failure (ω). Missing `nPop` on FENCE backtrack = ghost frame.

### Bug7 — Active

`Expr17` arm1: `FENCE(nPush() $'(' *Expr ... nPop() | *Id ~ 'Id' | ...)`
→ nPush fires, `$'('` fails, FENCE backtracks to arm2 — **nPop SKIPPED**

`Expr15`: `FENCE(nPush() *Expr16 (...) nPop() | '')`
→ same issue when no `[` follows

**Fix location:** `emit_byrd.c` — emit `NPOP_fn()` on ω path of nPush arm.

### Skeleton ladder (Sprint steps)

Build minimal SNOBOL4 test programs, each a strict superset of previous.
Diff oracle vs compiled stderr traces. First diverging SEQ#### line = bug.

**All 5 instrumented primitives share `int _nseq` counter:**
```
SEQ0001 NPUSH depth=N top=N    <- snobol4.c NPUSH_fn
SEQ0002 NINC  depth=N top=N    <- snobol4.c NINC_fn
SEQ0003 NPOP  depth=N top=N    <- snobol4.c NPOP_fn
SEQ0004 SHIFT type=T val='V'   <- mock_includes.c Shift()
SEQ0005 REDUCE type=T n=N      <- mock_includes.c Reduce()
```

| Step | Input | Status |
|------|-------|--------|
| `micro0_skeleton.sno` | `N` | ✅ Bug7 does NOT fire — baseline |
| `micro1_concat.sno` | `N + 1` | Bug7 FIRES — next |
| `micro2_call.sno` | `GT(N,3)` | Expr17 arm2/3 — TODO |
| `micro3_grouped.sno` | `(N+1)` | Expr17 arm1 full path — TODO |
| `micro4_full.sno` | `109_multi.input` | Full 5-line program — TODO |

### In-PATTERN Bomb Technique

Place diagnostic calls **directly inside a PATTERN** at any edge using `'' . *fn()`.
The function fires exactly when the match engine reaches that point, including on backtrack.

```snobol4
* Sequence stamp at any pattern edge
        DEFINE('seq_(label)', 'seq_B')          :(seq_End)
seq_B   seqN = seqN + 1
        OUTPUT = 'SEQ' LPAD(seqN,4,'0') ' ' label
        seq_ = .dummy                           :(NRETURN)
seq_End

* Embed at FENCE edges to see exactly which path fires:
        Expr17 = FENCE(
+                   '' . *seq_('E17_arm1_enter')
+                   nPush()
+                   $'('
+                   '' . *seq_('E17_arm1_after_paren')   <- never fires if ( fails
+                   nPop()
+                |  '' . *seq_('E17_arm2_enter')         <- fires on backtrack
+                   *Id ~ 'Id'
+                )
```

**Bomb variant** — abort on wrong state:
```snobol4
        DEFINE('assertDepth(expected)', 'assertB') :(assertEnd)
assertB EQ(_ntop, expected)                        :S(RETURN)
        OUTPUT = '*** BOMB depth=' _ntop ' expected=' expected
        &STLIMIT = 0                               * force abort
assertEnd
```
Place `'' . *assertDepth(1)` immediately after `nPush()` in arm1 to confirm
depth is correct before `$'('` runs.

### Crosscheck ladder (one at a time, never skip)

```
104_label → 105_goto → 109_multi → 120_real_prog → 130_inc_file → 140_self
```
`140_self` PASS → **M-BEAUTY-CORE fires**.

### Diagnostic tools

- **&STLIMIT binary search** — set limit, halve on hang
- **&STCOUNT** — increments correctly on CSNOBOL4 (verified 2026-03-16)
- **TRACE:** `TRACE('var','VALUE')` works; `TRACE(...,'KEYWORD')` non-functional
- **DUMP():** full variable dump at any point

---

## Session Start (session168)

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = 8e5e9cb

apt-get install -y libgc-dev nasm && make -C src/sno2c

mkdir -p /home/snobol4corpus
ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26
```

## Build beauty_full_bin

```bash
RT=src/runtime
INC=/home/claude/snobol4corpus/programs/inc
BEAUTY=/home/claude/snobol4corpus/programs/beauty/beauty.sno
src/sno2c/sno2c -trampoline -I$INC $BEAUTY > beauty_full.c
gcc -O0 -g beauty_full.c \
    $RT/snobol4/snobol4.c $RT/snobol4/mock_includes.c \
    $RT/snobol4/snobol4_pattern.c $RT/mock_engine.c \
    -I$RT/snobol4 -I$RT -Isrc/sno2c -lgc -lm -w -o beauty_full_bin
```

## Session End

⛔ **ARTIFACTS FIRST — before any HQ update:**
```bash
# 1. Archive any new .s files that fired a milestone:
#    cp <generated>.s snobol4x/artifacts/asm/<name>.s
#    Update artifacts/README.md with entry (status, milestone, assemble cmd, design notes)
#    git add artifacts/ && git commit -m "sessionN: archive <sprint> oracle .s files"
#
# 2. Then update TINY.md HEAD, sprint status, next action
# 3. Then update PLAN.md milestone dashboard
# 4. Push all repos, .github last
```

```bash
# Artifact check — see IMPL-SNO2C.md §Artifact Snapshot Protocol
# Update this file: HEAD, frontier table, next action, pivot log
git add -A && git commit && git push
# Push .github last
```

---

## Milestones

| ID | Trigger | ✓ |
|----|---------|---|
| M-SNOC-COMPILES | snoc compiles beauty_core.sno | ✅ |
| M-REBUS | Rebus round-trip diff empty | ✅ `bf86b4b` |
| M-COMPILED-BYRD | sno2c emits Byrd boxes, mock_engine only | ✅ `560c56a` |
| M-CNODE | CNode IR, zero lines >120 chars | ✅ `ac54bd2` |
| **M-STACK-TRACE** | oracle_stack.txt == compiled_stack.txt for all rung-12 inputs | ✅ session119 |
| **M-BEAUTY-CORE** | beauty_full_bin self-beautifies (mock stubs) | ❌ |
| **M-BEAUTY-FULL** | beauty_full_bin self-beautifies (real -I inc/) | ❌ |
| M-CODE-EVAL | CODE()+EVAL() via TCC → block_fn_t | ❌ |
| M-SNO2C-SNO | sno2c.sno compiled by C sno2c | ❌ |
| M-COMPILED-SELF | Compiled binary self-beautifies | ❌ |
| M-BOOTSTRAP | sno2c_stage1 output = sno2c_stage2 | ❌ |

---

## Sprint Map

### Active → M-BEAUTY-FULL (SNOBOL4 × C)

| Sprint | Paradigm | Trigger | Status |
|--------|----------|---------|--------|
| `stack-trace` | Dual-stack instrumentation | oracle == compiled stack trace → **M-STACK-TRACE** | ✅ session119 |
| `bug7-bomb` | Bomb protocol → fix emit_byrd.c | trace diff clean + 109_multi PASS → ladder → **M-BEAUTY-CORE** | ⏳ NOW |
| `beauty-probe` | Probe | All failures diagnosed | ❌ B |
| `beauty-monitor` | Monitor | Trace streams match | ❌ C |
| `beauty-triangulate` | Triangulate | Empty diff → **M-BEAUTY-FULL** | ❌ D |

### Planned → M-BOOTSTRAP (SNOBOL4 × C, self-hosting)

| Sprint | Gates on |
|--------|----------|
| `trampoline` · `stmt-fn` · `block-fn` · `pattern-block` | M-BEAUTY-FULL |
| `code-eval` (TCC) · `compiler-pattern` (compiler.sno) | M-BEAUTY-FULL |
| `bootstrap-stage1` · `bootstrap-stage2` | M-SNO2C-SNO |

### Sprint A12 — M-ASM-MACROS

**Goal:** Generated `.s` is readable. Every emitted line follows:

```
LABEL          ACTION          GOTO
```

Three columns. No exceptions. The LABEL is a Byrd box port or SNOBOL4 label.
The ACTION is a NASM macro. The GOTO is the succeed or fail target — a label, never a raw address.

**NASM macro library: `src/runtime/asm/snobol4_asm.mac`**

One macro per Byrd box primitive. Each macro expands to whatever register
shuffling is needed, but the call site is always one readable line:

```nasm
; Pattern nodes — one line each:
P_12_α         SPAN            letter_cs,   P_12_γ,  P_12_ω
P_14_α         LIT             "hello",     P_14_γ,  P_14_ω
P_16_α         SEQ             P_14, P_12,  P_16_γ,  P_16_ω
P_18_α         ALT             P_14, P_16,  P_18_γ,  P_18_ω
P_20_α         DOL             ppTokName,   P_20_γ,  P_20_ω

; Statement — subject, match, replace, goto:
L_LOOP         SUBJECT         ppLine
               MATCH_PAT       P_16,        L_WRITE, L_END
L_WRITE        REPLACE         ppOut,       ppLine
               GOTO                         L_LOOP
```

Parallel C output for comparison:

```c
L_LOOP:   subj = GET("ppLine");
          if (MATCH(P_16, subj)) { SET("ppOut", subj); goto L_WRITE; }
          goto L_END;
L_WRITE:  SET("ppLine", GET("ppOut"));
          goto L_LOOP;
```

**Sprint A12 steps:**
1. Write `src/runtime/asm/snobol4_asm.mac` — macros for LIT/SPAN/SEQ/ALT/ALT/DOL/ARBNO/ANY/NOTANY/BREAK/POS/RPOS/REM/ARB/SUBJECT/MATCH_PAT/REPLACE/GOTO/GOTO_S/GOTO_F
2. Change `emit_byrd_asm.c` to `%include "snobol4_asm.mac"` at top of every `.s`
3. Change every `A("    mov rax...")` emission to `A("  MACRO_NAME  args")` 
4. Verify beauty_prog.s assembles clean with macros expanded
5. Diff generated .s before/after — three-column structure visible throughout
6. **M-ASM-MACROS fires** when beauty_prog.s is fully macro-driven and assembles

### Sprint A13 — M-ASM-IR

**Goal:** Separate the tree walk from code generation. Same architecture as C backend's CNode IR.

The ASM emitter currently does parse → emit in one pass. This makes it hard to:
- Inject comments and separators
- Optimise label names
- Share structure between C and ASM emitters

**Architecture:**
```
Parse → EXPR_t/STMT_t → [ASM IR walk] → AsmNode tree → [ASM emit] → .s file
```

The AsmNode tree is a list of `(label, macro_name, args[], goto_s, goto_f)` tuples.
The emit pass just prints them in three-column format. No logic in the emit pass.

**Sprint A13 steps:**
1. Define `AsmNode` struct: `{char *label; char *macro; char **args; int nargs; char *gs; char *gf;}`
2. Write `asm_ir_build(Program*)` → `AsmNode[]` — the tree walk, no emission
3. Write `asm_ir_emit(AsmNode[])` — pure pretty-printer, three columns
4. Replace current `asm_emit_program()` with `asm_ir_build()` + `asm_ir_emit()`
5. **M-ASM-IR fires** when beauty_prog.s generates identically via the new path

### Sprint A14 — M-ASM-BEAUTIFUL

**Goal:** beauty_prog.s is as readable as beauty_full.c. A human can follow the SNOBOL4 logic by reading the `.s` file directly.

**Trigger:** Open beauty_prog.s and beauty_full.c side by side. Every SNOBOL4 statement is recognisable in both. The Byrd box four ports are visible as α/β/γ/ω. Statement boundaries are clear. No raw register names in the body — only macro calls.

**M-ASM-BEAUTIFUL fires** when Lon reads beauty_prog.s and says it is beautiful.

### Completed

| Sprint | Commit |
|--------|--------|
| `space-token` | `3581830` |
| `compiled-byrd-boxes` | `560c56a` |
| `crosscheck-ladder` — 106/106 | `668ce4f` |
| `cnode` | `ac54bd2` |
| `rebus-roundtrip` | `bf86b4b` |
| `smoke-tests` — 21/21 | `8f68962` |
| sprints 0–22 (engine foundation) | `test/sprint*` |

---

## Pivot Log

| Sessions | What | Why |
|----------|------|-----|
| 159 | **PIVOT: M-ASM-BEAUTIFUL (A14) activated.** E_OR/E_CONC → ALT/CONCAT builtins registered; test 101 PASS. snobol4_asm.mac extended with STORE_ARG32/16, LOAD_NULVCL, APPLY_FN_0/N, SET_CAPTURE, IS_FAIL_BRANCH/16, SETUP_SUBJECT_FROM16. prog_emit_expr + asm_emit_program raw register sequences replaced with macro calls throughout. beauty_prog_session159.s archived (18220 lines, nasm clean). 106/106 26/26. HEAD a361318. | Lon requested M-ASM-BEAUTIFUL pivot. M-ASM-BEAUTY (102-109 Parse Error) deferred. |
| 158 | **M-ASM-BEAUTY progress — 101_comment PASS:** section .text fix; stack align; E_FNC/Case1-SF/capture; 106/106 26/26. Root cause of 102-109: E_OR/E_CONC → NULVCL. | — 3 issues diagnosed, sprint steps written.** Multi-capture (055): per-variable cap buffers + cap_order table in emitter + harness walk. E_INDR (056): add case + fix build_bare_sno to keep *VAR-referenced plain assigns + fix extract_subject to use subject var from match line. FAIL/057: already wired, unblocked once script continues past 055. SPITBOL p_imc studied for canonical multi-capture semantics. HQ updated. |
| 150 | **Sprint A9 — 17/20 ASM crosscheck PASS.** New emitters: ANY/NOTANY/SPAN/BREAK/LEN/TAB/RTAB/REM/ARB/FAIL all wired into E_FNC switch. E_VART: REM/ARB/FAIL intercepted as zero-arg builtins. Harness rewritten with setjmp/longjmp unanchored scan loop. DOL writes to harness cap_buf/cap_len externs. cap_len sentinel UINT64_MAX distinguishes no-capture from empty-string capture. build_bare_sno keeps pattern-variable assignments. DATATYPE lowercase fix (106/106). 038–054 PASS. 055 fails (multi-capture). Script stops early at first FAIL — next session fix extract_subject + skip multi-capture + wire E_INDR. HEAD d7a75cc. | |
| 149 | **Sprint A9 begun.** `snobol4_asm_harness.c`: flat `subject_data[65536]` array (preserves `lea rsi,[rel subject_data]` semantics), `match_success`/`match_fail` as C `noreturn` functions, inline `jmp root_alpha`. `-asm-body` flag: `asm_emit_body()` emits `global root_alpha,root_beta` + `extern cursor,subject_data,subject_len_val,match_success,match_fail`. `run_crosscheck_asm.sh`: extracts subject, builds bare `.sno`, sno2c→nasm→gcc→run, capture tests diff stdout vs `.ref`, match/no-match tests check exit code. **038_pat_literal PASS** end-to-end. Next: wire `emit_asm_any/span/break/notany/tab/rtab/len/rem/arb` into `E_FNC` switch. 106/106 holds. HEAD a7c324e. | |
| 148 | **M-ASM-ASSIGN + M-ASM-NAMED fire.** ASSIGN: assign_lit.s (LIT $ capture) + assign_digits.s (SPAN $ capture unanchored) PASS; emit_asm_assign() DOL Byrd box from v311.sil ENMI; E_DOL+E_NAM wired. NAMED: ref_astar_bstar.s (ASTAR=ARBNO("a"), BSTAR=ARBNO("b") on "aaabb") + anbn.s (4 sequential named-pattern call sites on "aabb") PASS; AsmNamedPat registry + asm_scan_named_patterns() pre-pass + emit_asm_named_ref() call-site + emit_asm_named_def() body emitter; E_VART wired; Proebsting §4.5 gate convention (pat_NAME_ret_gamma/omega .bss indirect-jmp, no call stack). End-to-end .sno→sno2c -asm→nasm→ld→run verified. 106/106 invariant holds. HEAD de085e1. Next: Sprint A9 — snobol4_asm_harness.c + body-only emitter + ASM crosscheck driver. | |
| 147 | **M-ASM-ALT + M-ASM-ARBNO + M-ASM-CHARSET fire; emit_byrd_asm.c real emitter written.** ALT: alt_first/second/fail. ARBNO: arbno_match/empty/alt (cursor stack 64 slots, zero-advance guard, v311.sil ARBN/EARB). CHARSET: any_vowel/notany_consonant/span_digits/break_space — all PASS. emit_byrd_asm.c: real recursive LIT/SEQ/ALT/POS/RPOS/ARBNO emitter — generates correct NASM but needs harness to connect to crosscheck (subject currently hardcoded). Next: Sprint A7 — snobol4_asm_harness.c + body-only emitter + first crosscheck pass. HEAD a114bcf. | |
| 147 | **M-ASM-ALT + M-ASM-ARBNO fire** — ALT: three oracles (alt_first/second/fail). ARBNO: three oracles (arbno_match "aaa", arbno_empty "aaa" vs 'x' → fail, arbno_alt "abba" vs ARBNO('a'\|'b')). ARBNO design: flat .bss cursor stack 64 slots + depth counter; α pushes+succeeds; β pops+tries one rep; zero-advance guard; rep_success pushes+re-succeeds. Proebsting §4.5 for ALT; v311.sil ARBN/EARB/ARBF for ARBNO. All PASS. Next: Sprint A6 (CHARSET). | |
| 146 | **M-ASM-LIT fires** — `lit_hello.s` hand-written: α/β/γ/ω real NASM labels, cursor+saved_cursor flat .bss qwords, repe cmpsb compare. Assembles, links, runs → `hello\n` exit 0. Diff vs oracle CLEAN. `artifacts/asm/null.s` + `artifacts/asm/lit_hello.s` placed in artifacts/asm/. HQ updated. No push per Lon. Next: Sprint A2 (POS/RPOS). |
| 145 | **M-ASM-HELLO fires** — `emit_byrd_asm.c` created, `-asm` flag added to `main.c`+`Makefile`, `null.s` assembles+links+runs → exit 0. 106/106 crosscheck clean. Next: Sprint A1 (LIT node). | Sprint A0 complete. |
| 144 | **PIVOT: x64 ASM backend** — abandon monitor-scaffold/bug7-bomb | C backend has structural flaw: named patterns require reentrant C functions, `pat_X_t` structs, `calloc`, three-level scoping. ASM eliminates all of it: α/β/γ/ω = real labels, all vars flat `.bss`, named patterns = labels + 2-way jmp. One scope. Sprint plan A0–A10 documented in NOW. |
| 80–89 | Attacked beauty.sno directly | Burned — needed smaller test cases first |
| 89 | Pivot: corpus ladder | Prove each feature before moving up |
| 95 | 106/106 rungs 1–11 | Foundation solid |
| 96–97 | Sprint 4 compiler internals | Retired — not test-driven |
| 97 | Pivot: test-driven only | No compiler work without failing test |
| 98–99 | HQ restructure (L1/L2/L3 pyramid) | Plan before code |
| 100 | HQ: frontend×backend split | One file per concern |
| 101 | Sprint A begins | Rung 12, beauty_full_bin, first crosscheck test (Session 101) |
| 103–104 | E_NAM~/Shift fix; E_FNC fallback fix | 101_comment PASS; 102+ blocked by named-pattern RHS truncation in byrd_emit_named_pattern |
| 105 | $ left-assoc parse fix + E_DOL chain emitter | Parser correct; emitter label-dup compile error blocks 102+ |
| 106 | E_DOL label-dup fixed (emit_seq pattern); 4x crosscheck speedup | 101 PASS; 102_output FAIL — assignment node blank in pp() |
| 108 | E_INDR(E_FNC) fix in emit_byrd.c; beauty_full.c patched; bug2 diagnosed: pat_ExprList epsilon | 102_output still FAIL — bug2 is pat_ExprList matching epsilon without '(' |
| 109 | bug2 '(' guards added (both Function+Id arms); pop_val()+skip; doc sno* names fixed in .github | 102_output still FAIL — OUTPUT not reaching subject slot; bare-Function arm not yet found |
| 110 | bug2 FIXED: bare-Function/Id go to fence_after_358 (keep Shift, succeed); parse tree verified correct by trace | 102_output still FAIL — Bug3: pp_Stmt drops subject; INDEX_fn(c,2) suspect |
| 107 | Shift(t,v) value fix; FIELD_GET debug removed; root cause diagnosed | 106/106 pass; 102 still FAIL — E_DEREF(E_FNC) in emit_byrd.c drops args |
| 111 | NPUSH not firing on backtrack in pat_Expr3/4; ntop()=0 at Reduce | Full stack probe confirmed; emit_simple_val E_QLIT fix applied; structural NPUSH hoist pending in emit_byrd.c |
| 112 | Bug3 FIXED (emit_seq NPUSH on backtrack); Bug4 FIXED (emit_imm literal-tok $'(' guard + stack rollback via STACK_DEPTH_fn) | 101/102/103 PASS; 104_label FAIL — next |
| 113 | Bug5 diagnosed: ntop() frame displacement by nested NPUSH; NINC_AT_fn + saved-frame fix in beauty_full.c; Reduce("..",2) fires; pp_.. crash unresolved | EMERGENCY WIP 7c17ffa |
| 114 | Bug5 FIXED: saved-frame pattern extended to pat_Parse/pat_Compiland/pat_Command; _command_pending_parent_frame global; Reduce(Parse,1) correct; 104_label PASS. Bug6 diagnosed: Bug6a spurious Reduce(..,2) for goto token; Bug6b unevaluated goto type string | EMERGENCY WIP 3f5bfda |
| 115 | Bug6a FIXED: `:` lookahead guard in pat_X4 cat_r_168. Bug6b FIXED: NV_SET_fn for Brackets/SorF in pat_Target/SGoto/FGoto; CONCAT_fn Reduce type; suppressed output_str+cond_OUTPUT in all pat_ gammas (23 sites). 101–105 PASS, 106/106. WIP only — emit_byrd.c port pending | EMERGENCY WIP — commit next session |
| 116 | emit_byrd.c port attempt: snobol4.h NTOP_INDEX/NSTACK_AT decls; pending_npush_uid + _pending_parent_frame globals; Bug5 saved-frame in emit_seq+E_FNC nPush; Bug6a colon guard in *X4 deref; Bug6b CONCAT_fn in E_OPSYN; output_str suppression gated on suppress_output_in_named_pat(); _parent_frame field in all named pat structs. 101-103 PASS from regen; 104-105 FAIL — pending_npush_uid not surviving nested CAT levels | EMERGENCY WIP — pending_npush_uid fix next session |
| 117 | Diagnosis: 104/105 fail because Reduce(..,2) never fires — ntop()=1 at ExprList level instead of 2. Dual-stack trace confirmed: spurious NPUSH idx=7/8 inside pat_Expr displaces counter stack so second NINC fires at wrong level. Root cause: nPush/nPop imbalance in pat_Expr4/X4 sub-pattern. Option A (parameter threading) attempted and backed out — correct diagnosis but wrong fix target. All files restored to session116 state. | Diagnosis only — no commit |
| 118 | Pivot: stack-trace sprint. Understand two-stack engine model fully. Instrument both oracle and compiled binary. Use diff to find exact imbalance location, not inference. New milestone M-STACK-TRACE gates on beauty-crosscheck. HQ updated. | Plan only — no commit |
| 119 | M-STACK-TRACE fires. oracle_stack.txt == compiled_stack.txt for all rung-12 inputs. | Stack trace matched — sprint beauty-crosscheck begins |
| 121 | Dual-stack trace infra built: oracle (patched counter.sno→TERMINAL) + compiled (fprintf in NPUSH/NINC/NPOP). 109_multi.input trace diff: first divergence line 2 — oracle NINC, compiled spurious NPUSH. Bug7 Bomb Protocol designed (Pass1 count, Pass2 limit+backtrace). emit_imm NPOP-on-fail drafted but emit_seq Expr15 fix caused double-pop regression on 105_goto. All WIP reverted. Bomb protocol is next. | Bomb protocol ready — awaiting next session |
| 120 | beauty.sno PATTERN read in full (lines 293–419). Bug7 confirmed: Expr17 FENCE arm 1 calls nPush() then $'(' fails — nPop() never called on ω path. Expr15 FENCE arm same issue. Fix target: emit_byrd.c FENCE backtrack path. HQ updated with full pattern structure. ~55% context at session start. | Plan only — awaiting instruction |
| 122 | Pivot: diag1-corpus sprint before bug7-micro. 35 tests 152 assertions rungs 2–11, 35/35 PASS CSNOBOL4 2.3.3. M-FLAT documented (flat() Gray/White bypass of pp/ss). HQ updated. Context ~94% at close. | diag1 corpus ready to commit with token; bug7-micro is next |
| 122b | PIVOT: M-DIAG1 now top priority. Run diag1 35-test suite on JVM + DOTNET. Fix failures. Fire M-DIAG1. Then bug7-micro. Priority order: M-DIAG1 → M-BEAUTY-CORE → M-FLAT → M-BEAUTY-FULL → M-BOOTSTRAP. | New session opens on snobol4jvm |

**Session180 — CAT/SEQ naming; CAT2 macros; scan retry; path revert; 056 fix:**
- Naming decision: E_CONC value-context → **CAT** (string concat); E_CONC pattern-context → **SEQ** (already). E_OR → **ALT**. `CAT2_SS/SV/VS/VV/VN/SN` macros added to `snobol4_asm.mac` — call `stmt_concat` directly (not `stmt_apply("CONCAT")`).
- `expr_is_pattern_expr`: E_CONC now requires a pattern fn call — pure literal concat `'a' 'b'` is VALUE not pattern. E_OR always remains a pattern.
- `E_CONC` in `prog_emit_expr` now routes to `CAT2_*` macros; E_OR still uses `ALT2_*`.
- All 6 concat tests now pass (017–022).
- Unanchored scan retry loop added to Case 2 pattern statement emission: `scan_start_N` bss slot, `scan_retry_N` label, advance+retry on omega. 056 program-mode fixed.
- **Regression introduced**: scan retry omega exits via `jg next_lbl` instead of `jg tgt_f` — `034_goto_failure`, `057_pat_fail_builtin`, `098_keyword_anchor` now fail. **Fix is one line — `jg next_lbl` → `jg <tgt_f label>`** in the omega block.
- `/home/socrates` path experiment reverted — all repos back to `/home/claude`. All pushed.
- Corpus: **75 PASS** (up from 64 session179). 106/106 C ✅. 26/26 ASM ✅.
- HEAD: `ee4b118`

**Session182 — archive src/ir; emit_cnode relocated to backend/c:**
- `src/ir/byrd/emit_cnode.c/.h` → `src/backend/c/` (live production code, was misplaced)
- `src/Makefile`: drop `-I ir/byrd`, merge `IR_BYRD` into `BACKEND_C`, update header dep
- `src/ir/byrd/{byrd_ir,ir,lower}.py` → `archive/ir/` with README.md
- `src/ir/jvm/.gitkeep`, `src/ir/net/.gitkeep` deleted
- `lower.py` preserved in archive as design reference for `emit_byrd.c` four-port wiring
- 106/106 C PASS ✅, 26/26 ASM PASS ✅ confirmed after rebuild

**⚠ CRITICAL NEXT ACTION — Session183:**

1. **Run corpus** — scan-retry fix should recover 034, 057, 098. Target 78+ PASS.
2. **Continue corpus fixes** per session180 priority order:
   - NASM_FAIL remaining (4 tests: 019, 056, 086, wordcount)
   - Capture fixes (060–064)
   - Define/functions (083–090)
3. **Update beauty_prog.s artifact** if emit_byrd_asm.c changed.

**Session182 start commands:**
```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD = f3ca7f2

apt-get install -y libgc-dev nasm && make -C src
mkdir -p /home/snobol4corpus && ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
gcc -c src/runtime/asm/snobol4_asm_harness.c -o src/runtime/asm/snobol4_asm_harness.o
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh        # must be 106/106
bash test/crosscheck/run_crosscheck_asm.sh                   # must be 26/26

# Then run full corpus
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck_asm_prog.sh 2>&1 | tail -5
```

**Session180 — arithmetic ops, named-pattern fix, label rename, artifacts reorg:**
- `E_ADD/E_SUB/E_MPY/E_DIV/E_EXPOP/E_MNS` cases added to `prog_emit_expr` in `emit_byrd_asm.c`
- `add/sub/mul/DIVIDE_fn/POWER_fn/neg` registered as builtins in `SNO_INIT_fn` (`snobol4.c`)
- `E_MNS` operand fixed: `e->left` not `e->right` (unop() convention)
- `expr_is_pattern_expr()` guard: only register `VAR=expr` as named pattern when replacement contains E_FNC/E_OR/E_CONC — plain value assignments (`X='hello'`, `OUTPUT=X`) no longer generate spurious Byrd-box bodies
- `E_VART/E_KW` added to .bss skip list
- Synthetic labels renamed: `L_sn_N` → `Ln_N` (next/fall-through), `L_sf_N` → `Lf_N` (fail dispatch)
- `artifacts/asm/` reorganised: `beauty_prog.s` at top; `fixtures/` for sprint oracles; `samples/` for programs
- Corpus: **47 → 64 PASS**, 16 → 4 NASM_FAIL; 106/106 C crosscheck ✅; 25/26 ASM crosscheck
- `056_pat_star_deref` FAIL: `PAT = 'hello'` (E_QLIT) skipped by expr_is_pattern_expr — `*PAT` indirect ref has no .bss slots; fix next session

**⚠ CRITICAL NEXT ACTION — Session180:**
1. Fix `056_pat_star_deref`: `PAT = 'hello'` assigns E_QLIT but `*PAT` uses it as indirect pattern ref. The expr_is_pattern_expr guard correctly skips it as non-pattern, but the `*VAR` (E_INDR) emit path in `emit_asm_node` still tries to reference `P_PAT_ret_γ`. Fix: when E_INDR references a variable that is NOT in the named-pattern registry, fall back to value-based pattern matching instead. Restore 26/26 ASM crosscheck.
2. Continue NASM_FAIL fixes: 4 remaining (`019_concat_var_string`, `056_pat_star_deref`, `086_define_locals`, `wordcount`)
3. Fix remaining FAILs: concat (017–022), capture (060–064), define/functions (083–090)

---

## NOW (session183 — frontend session)

**⚠ TWO CONCURRENT SESSIONS — different concerns, same repo:**
- **Frontend session** (this chat): `snocone-frontend` sprint — SC0→SC5 → M-SNOC-SELF
- **Backend session** (other chat): `asm-backend` sprint — corpus fixes (72/106) → M-MONITOR

Each session edits `snobol4x` independently. Both push to `.github`. Per RULES.md: `git pull --rebase` before every `.github` push. No `--force` ever.

**Frontend session sprint: `snocone-frontend`**
**HEAD:** `583c5a5` session182
**Active milestone:** M-SNOC-LEX (Sprint SC0)

### Sprint SC0 — M-SNOC-LEX

**Goal:** `src/frontend/snocone/sc_lex.c` — tokenize any `.sc` file.
Ported from `snobol4jvm/src/SNOBOL4clojure/snocone.clj` (tested, complete).

**Files:**
- `src/frontend/snocone/sc_lex.h` — token kinds + `ScToken` struct + `sc_lex()` API
- `src/frontend/snocone/sc_lex.c` — lexer implementation
- `test/frontend/snocone/sc_lex_test.c` — quick-check: `OUTPUT = 'hello'` → 3 tokens PASS

**Token kinds** (from JVM KIND table):
```c
SC_INTEGER, SC_REAL, SC_STRING, SC_IDENT,
SC_KW_IF, SC_KW_ELSE, SC_KW_WHILE, SC_KW_DO, SC_KW_FOR,
SC_KW_RETURN, SC_KW_FRETURN, SC_KW_NRETURN,
SC_KW_GO, SC_KW_TO, SC_KW_PROCEDURE, SC_KW_STRUCT,
SC_LPAREN, SC_RPAREN, SC_LBRACE, SC_RBRACE, SC_LBRACKET, SC_RBRACKET,
SC_COMMA, SC_SEMICOLON, SC_COLON,
SC_ASSIGN, SC_QUESTION, SC_PIPE, SC_OR, SC_CONCAT,
SC_EQ, SC_NE, SC_LT, SC_GT, SC_LE, SC_GE,
SC_STR_IDENT, SC_STR_DIFFER, SC_STR_LT, SC_STR_GT, SC_STR_LE, SC_STR_GE,
SC_STR_EQ, SC_STR_NE,
SC_PLUS, SC_MINUS, SC_SLASH, SC_STAR, SC_PERCENT, SC_CARET,
SC_PERIOD, SC_DOLLAR, SC_AT, SC_AMPERSAND, SC_TILDE,
SC_NEWLINE, SC_EOF, SC_UNKNOWN
```

**Continuation chars:** `@ $ % ^ & * ( - + = [ < > | ~ , ? :`

**Quick-check trigger (M-SNOC-LEX):**
```bash
cd /home/claude/snobol4x
gcc -o /tmp/sc_lex_test test/frontend/snocone/sc_lex_test.c src/frontend/snocone/sc_lex.c
/tmp/sc_lex_test
# PASS → M-SNOC-LEX fires → begin Sprint SC1
```

### Sprint SC1 — M-SNOC-PARSE

`src/frontend/snocone/sc_parse.c` — recursive-descent parser consuming `ScToken[]`.
Produces `ScNode` AST covering: expr (full prec table), stmt, if/while/do/for/procedure/struct/goto/return/block.

### Sprint SC2 — M-SNOC-LOWER

`src/frontend/snocone/sc_lower.c` — walks `ScNode` tree, emits `EXPR_t`/`STMT_t` IR.
Operator mapping from `snocone.sc` bconv table (already read).
**No changes to emit.c or the C backend.**

### Sprint SC3 — M-SNOC-EMIT

`-sc` flag in `src/driver/main.c`: if input ends `.sc`, run `sc_lex → sc_parse → sc_lower → emit`.
Quick-check: `echo "OUTPUT = 'hello'" > /tmp/t.sc && ./sno2c -sc /tmp/t.sc > /tmp/t.c && gcc /tmp/t.c ... && ./a.out`
Expected output: `hello`

### Sprint SC4 — M-SNOC-CORPUS

10-rung corpus in `test/frontend/snocone/`:
SC1 literals · SC2 assign · SC3 arith · SC4 control · SC5 while/do · SC6 for · SC7 procedure · SC8 struct · SC9 patterns · SC10 snocone.sno word-count example

### Sprint SC5 — M-SNOC-SELF

`snocone.sc` → `./sno2c -sc` → binary → run → diff vs `snocone.snobol4` oracle (or fresh compile).
**M-SNOC-SELF fires** when diff is empty.


**Session183 (backend session) — diagnosis 79/106; correct DEFINE design:**
- Corpus confirmed: 79/106 PASS
- DEFINE calling convention: **user-defined functions ARE named patterns** (BACKEND-C.md)
- Wrong approach (C-ABI trampoline) identified and discarded
- Correct design: extend AsmNamedPat with is_fn/nparams/arg_slots/save_slots
- α port binds args + saves old param vars; γ/ω ports restore; RETURN → jmp [ret_γ]
- No runtime changes — compile-time only
- See CRITICAL NEXT ACTION above for Session184 implementation steps
