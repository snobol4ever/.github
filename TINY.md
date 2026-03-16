# TINY.md — SNOBOL4-tiny (L2)

SNOBOL4-tiny: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `stack-trace` — dual-stack instrumentation and oracle comparison
**HEAD:** `session116` (session117 = diagnosis only, no commit; session118 = this plan)
**Milestone:** M-STACK-TRACE → M-BEAUTY-CORE

**Next action:**
1. **Instrument beauty.sno** — replace nPush/nInc/nPop/Shift/Reduce with tracing
   wrappers. Run under CSNOBOL4 → `oracle_stack.txt`. This is ground truth.
2. **Instrument the compiled runtime** — add fprintf traces to NPUSH_fn/NPOP_fn/
   NINC_fn/Shift_fn/Reduce_fn in snobol4.c / mock_engine.c. Rebuild beauty_full_bin.
3. **Diff the two traces** for input `104_label.input` (LOOP X = X 1).
   First diverging line = exact location of the nPush/nPop imbalance.
4. **Binary search emit_byrd.c** between last-matching event and first-diverging
   event. Find the γ exit path of pat_Expr4/X4 that calls nPush without nPop.
5. **Fix emit_byrd.c.** Ensure nPop fires on ALL exit paths (γ and ω).
6. **Regenerate beauty_full.c**, rebuild, verify 104+105 PASS.
7. **Port complete** → M-STACK-TRACE fires.
8. Continue ladder: 109_multi → 120_real_prog → 130_inc_file → 140_self → M-BEAUTY-CORE.

**Confirmed symptom (session117 dual-stack trace):**
For `X 1` (two concat atoms), counter stack trace shows:
```
NPUSH idx=6   ExprList frame
NINC  idx=6 count=1   atom X
NPUSH idx=7   ← spurious — from inside pat_Expr parsing X
NPUSH idx=8   ← another spurious
NPOP  idx=8
NPOP  idx=7
              ← second NINC fires at wrong level — idx=6 stays at 1
              ← ntop()=1, guard (>1) skips Reduce(..,2)
```

**Root cause:** a sub-pattern of `pat_Expr` (likely `pat_Expr4` or `pat_X4`) calls
`nPush()` and does NOT call `nPop()` before returning γ (success). This leaves an
extra frame on the counter stack, displacing subsequent NINC calls.

**Reduce comes before nPop.** The correct sequence:
```
nPush → ... nInc ... nInc ... Reduce(type, ntop()) → nPop
```
ntop() must be read INSIDE Reduce. nPop discards the frame AFTER.

**Do NOT touch `_saved_frame` or `pending_npush_uid`** until imbalance is fixed.

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
| **M-STACK-TRACE** | oracle_stack.txt == compiled_stack.txt for all rung-12 inputs | ❌ |
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
| `stack-trace` | Dual-stack instrumentation | oracle == compiled stack trace → **M-STACK-TRACE** | ⏳ NOW |
| `beauty-crosscheck` | Crosscheck — diff vs oracle | beauty/140_self → **M-BEAUTY-CORE** | ❌ gates on M-STACK-TRACE |
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
| 116 | emit_byrd.c port attempt: snobol4.h NTOP_INDEX/NSTACK_AT decls; pending_npush_uid + _pending_parent_frame globals; Bug5 saved-frame in emit_seq+E_FNC nPush; Bug6a colon guard in *X4 deref; Bug6b CONCAT_fn in E_OPSYN; output_str suppression gated on suppress_output_in_named_pat(); _parent_frame field in all named pat structs. 101-103 PASS from regen; 104-105 FAIL — pending_npush_uid not surviving nested CAT levels | EMERGENCY WIP — pending_npush_uid fix next session |
| 117 | Diagnosis: 104/105 fail because Reduce(..,2) never fires — ntop()=1 at ExprList level instead of 2. Dual-stack trace confirmed: spurious NPUSH idx=7/8 inside pat_Expr displaces counter stack so second NINC fires at wrong level. Root cause: nPush/nPop imbalance in pat_Expr4/X4 sub-pattern. Option A (parameter threading) attempted and backed out — correct diagnosis but wrong fix target. All files restored to session116 state. | Diagnosis only — no commit |
| 118 | Pivot: stack-trace sprint. Understand two-stack engine model fully. Instrument both oracle and compiled binary. Use diff to find exact imbalance location, not inference. New milestone M-STACK-TRACE gates on beauty-crosscheck. HQ updated. | Plan only — no commit |
