# TINY.md — SNOBOL4-tiny (L2)

SNOBOL4-tiny: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `beauty-crosscheck` — Sprint A — rung 12 crosscheck tests
**HEAD:** `session115` — Bug6 fully fixed; 101–105 PASS, 106/106 rung 1–11 PASS
**Milestone:** M-BEAUTY-CORE → M-BEAUTY-FULL

**Next action:**
1. Port Bug6 WIP patches to `emit_byrd.c`, regenerate `beauty_full.c`, verify 5/5 still PASS.
2. Continue ladder: 109_multi → 120_real_prog → 130_inc_file → 140_self → M-BEAUTY-CORE.

   **Bug6a — spurious `Reduce(.., 2)` for `1 :(END)`:** `pat_X4`/`FENCE(*White *X4)` is consuming the
   space before `:(END)` and treating it as a second concat atom. The goto token `:(END)` should be left
   for `pat_Goto` in `pat_Stmt`. Probe shows `Reduce(..,2)` fires for `[1, END]` where `END` should be
   the goto target, not a subject expression atom. Diagnose whether `pat_Expr5..Expr14` rejects `:(END)`
   at the `:` character or whether `pat_Stmt`'s subject/goto split has a precedence bug.

   **Bug6b — `Reduce(*(':' Brackets), 1)` instead of `Reduce(:(), 1)`:** The goto Reduce type uses the
   literal string `*(':' Brackets)` instead of evaluating it. In beauty.sno: `("*(':' Brackets)" & 1)` —
   the string is an unevaluated SNOBOL4 expression that should be EVALed. Fix in `emit_byrd.c`: when
   `E_OPSYN &` has an `E_QLIT` type whose value starts with `*`, emit EVAL call not STRVAL.

   **Probe trace (oracle vs ours):**
   ```
   Oracle:  Shift(Integer,1) Shift(SpecialNm,END) Reduce(:(),1) Shift(,) Reduce(Stmt,7)
   Ours:    Shift(..) Reduce(..,2) Shift(..) Reduce(*(':' Brackets),1) Reduce(Stmt,7)
   ```

   **Prior bugs resolved:**

   **Bug5 — FIXED `3f5bfda` (session114):** `ntop()` frame displacement in `pat_Parse`/`pat_Compiland`/
   `pat_Command`. Nested `NPUSH` calls from `pat_Expr4/X4/Expr16` displaced `_ntop` above Parse-level
   frame. Fix: save `NTOP_INDEX_fn()` at both NPUSH sites in Parse/Compiland into `z->_saved_frame` +
   `_command_pending_parent_frame`; Command reads frame at init; `NINC_fn()→NINC_AT_fn(_cmd_parent_frame)`;
   `Reduce(Parse,ntop())→Reduce(Parse,NSTACK_AT_fn(_parse_frame))`.
   New runtime symbols: `_command_pending_parent_frame` (snobol4.c/h).
   Fix in `beauty_full_wip.c` only — `emit_byrd.c` NOT yet updated.

   **Bug3 — FIXED `4c2ad68`:** emit_seq NPUSH backtrack omission.
   **Bug4 — FIXED `4c2ad68`:** emit_imm literal-tok `$'('` guard + stack rollback.

2. After 105_goto PASS: continue ladder (109_multi → 120_real_prog → 130_inc_file → 140_self).
3. After WIP passes all rung-12 tests: port all saved-frame fixes to `emit_byrd.c`, recompile, verify.

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

## Session Start

```bash
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD matches above

apt-get install -y libgc-dev && make -C src/sno2c

mkdir -p /home/SNOBOL4-corpus
ln -sf /home/claude/SNOBOL4-corpus/crosscheck /home/SNOBOL4-corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must be 106/106
```

## Build beauty_full_bin

```bash
RT=src/runtime
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
src/sno2c/sno2c -trampoline -I$INC $BEAUTY > beauty_full.c
gcc -O0 -g beauty_full.c \
    $RT/snobol4/snobol4.c $RT/snobol4/mock_includes.c \
    $RT/snobol4/snobol4_pattern.c $RT/mock_engine.c \
    -I$RT/snobol4 -I$RT -Isrc/sno2c -lgc -lm -w -o beauty_full_bin
```

## Session End

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
| `beauty-crosscheck` | Crosscheck | beauty/140_self → **M-BEAUTY-CORE** | ⏳ A |
| `beauty-probe` | Probe | All failures diagnosed | ❌ B |
| `beauty-monitor` | Monitor | Trace streams match | ❌ C |
| `beauty-triangulate` | Triangulate | Empty diff → **M-BEAUTY-FULL** | ❌ D |

### Planned → M-BOOTSTRAP (SNOBOL4 × C, self-hosting)

| Sprint | Gates on |
|--------|----------|
| `trampoline` · `stmt-fn` · `block-fn` · `pattern-block` | M-BEAUTY-FULL |
| `code-eval` (TCC) · `compiler-pattern` (compiler.sno) | M-BEAUTY-FULL |
| `bootstrap-stage1` · `bootstrap-stage2` | M-SNO2C-SNO |

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
