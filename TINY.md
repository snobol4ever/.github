# TINY.md — SNOBOL4-tiny (L2)

SNOBOL4-tiny: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `bug7-bomb` — find and fix Bug7 ghost frame via counter-bomb protocol
**HEAD:** `07d4b14` EMERGENCY WIP session116
**Milestone:** M-BEAUTY-CORE

**Next action:**
1. Session start checklist (see bottom) — verify 106/106.
2. Execute Bug7 Bomb Protocol (see below) — Pass 1 then Pass 2.
3. Fix emit_byrd.c at the identified location.
4. Run beauty crosscheck ladder: 104 → 105 → 109 → 120 → 130 → 140.
5. 140_self PASS → **M-BEAUTY-CORE fires**.

---

## Bug7 Bomb Protocol

**Background:** Dual-stack trace diff on `109_multi.input` found first divergence at trace line 2:
- Oracle line 1: `NPUSH depth=1 top=0` ← last matching event (start point)
- Oracle line 2: `NINC  depth=1 top=1` ← expected next event
- Compiled line 2: `NPUSH depth=2 top=0` ← spurious second NPUSH (end point = bug)

The spurious NPUSH fires between trace line 1 and line 2. The bomb protocol finds exactly which emitted C label fires it.

**Pass 1 — Count bomb**

In `snobol4.c`, add a global counter to `NPUSH_fn()`:
```c
static int _npush_count = 0;
void NPUSH_fn(void) {
    _npush_count++;
    fprintf(stderr, "NPUSH #%d depth=%d top=0
", _npush_count, _ntop+1);
    /* ... existing code ... */
}
```
Also add at program exit (or at first OUTPUT):
```c
fprintf(stderr, "TOTAL NPUSH calls: %d
", _npush_count);
```
Run: `./beauty_full_bin < 109_multi.input 2>pass1.txt`
Read pass1.txt — identify which call number is the spurious one (call #2 from trace diff).

**Pass 2 — Limit bomb**

Set `bomb_limit = 2` (the spurious call number from Pass 1).
When `_npush_count == bomb_limit`, dump everything:
```c
if (_npush_count == bomb_limit) {
    fprintf(stderr, "=== BOMB at NPUSH #%d ===
", bomb_limit);
    fprintf(stderr, "  _ntop=%d
", _ntop);
    for (int i = 0; i <= _ntop; i++)
        fprintf(stderr, "  _nstack[%d]=%d
", i, _nstack[i]);
    /* print C call stack */
    void *bt[32]; int n = backtrace(bt, 32);
    backtrace_symbols_fd(bt, n, 2);
    fprintf(stderr, "=== END BOMB ===
");
}
```
Run: `./beauty_full_bin < 109_multi.input 2>pass2.txt`
The backtrace in pass2.txt shows exactly which C label in `beauty_full.c` fired the spurious NPUSH.
Map that label back to the emit_byrd.c node that generated it.
That node is missing an `NPOP_fn()` emit on its failure/ω path.

**Fix:** Add `NPOP_fn()` emit at the identified ω path in `emit_byrd.c`. Rebuild. Rerun trace diff — line 2 must now match. Run crosscheck.


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
| 119 | M-STACK-TRACE fires. oracle_stack.txt == compiled_stack.txt for all rung-12 inputs. | Stack trace matched — sprint beauty-crosscheck begins |
| 121 | Dual-stack trace infra built: oracle (patched counter.sno→TERMINAL) + compiled (fprintf in NPUSH/NINC/NPOP). 109_multi.input trace diff: first divergence line 2 — oracle NINC, compiled spurious NPUSH. Bug7 Bomb Protocol designed (Pass1 count, Pass2 limit+backtrace). emit_imm NPOP-on-fail drafted but emit_seq Expr15 fix caused double-pop regression on 105_goto. All WIP reverted. Bomb protocol is next. | Bomb protocol ready — awaiting next session |
| 120 | beauty.sno PATTERN read in full (lines 293–419). Bug7 confirmed: Expr17 FENCE arm 1 calls nPush() then $'(' fails — nPop() never called on ω path. Expr15 FENCE arm same issue. Fix target: emit_byrd.c FENCE backtrack path. HQ updated with full pattern structure. ~55% context at session start. | Plan only — awaiting instruction |
| 122 | Pivot: diag1-corpus sprint before bug7-micro. 35 tests 152 assertions rungs 2–11, 35/35 PASS CSNOBOL4 2.3.3. M-FLAT documented (flat() Gray/White bypass of pp/ss). HQ updated. Context ~94% at close. | diag1 corpus ready to commit with token; bug7-micro is next |
| 122b | PIVOT: M-DIAG1 now top priority. Run diag1 35-test suite on JVM + DOTNET. Fix failures. Fire M-DIAG1. Then bug7-micro. Priority order: M-DIAG1 → M-BEAUTY-CORE → M-FLAT → M-BEAUTY-FULL → M-BOOTSTRAP. | New session opens on SNOBOL4-jvm |
