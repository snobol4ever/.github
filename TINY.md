# TINY.md — SNOBOL4-tiny (L2)

SNOBOL4-tiny: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `beauty-crosscheck` — Sprint A — rung 12 crosscheck tests
**HEAD:** `session111` — Bug3: traced to NPUSH skipped on backtrack path in E_OPSYN emitter
**Milestone:** M-BEAUTY-CORE → M-BEAUTY-FULL

**Next action:**
1. **Active bug:** 102_output FAIL — `Reduce("Stmt",7)` pops wrong 7 children

   **Confirmed by session111 full trace:**
   ```
   [Reduce] t=Parse  depth=1        ← Parse sentinel (correct)
   [Shift]  t=Label  v=             depth=2
   [Shift]  t=Function v=OUTPUT     depth=3
   [Shift]  t=  v=                  depth=4  (empty pattern)
   [Shift]  t==  v==                depth=5
   [Shift]  t=String v='hello'      depth=6
   [Reduce] t=..  ntop=0  depth=6   ← WRONG: ntop should be 1, pops 0 pushes 1
   [Reduce] t=|   ntop=0  depth=7   ← WRONG: same, pops 0 pushes 1
   [Shift]  t=  v=  depth=9         ← goto1 epsilon
   [Shift]  t=  v=  depth=10        ← goto2 epsilon
   [Reduce] t=Stmt  n=7  depth=10   ← pops c[7..1] = goto2,goto1,|,..,String,=,empty-pat
                                       Label and Function/OUTPUT LEFT on stack → ppSubj=""
   ```

   **Root cause (session111 — CONFIRMED):**
   `emit_byrd.c` E_OPSYN `&` emitter structure for `nPush() *X4 ("tag" & n) nPop()`:
   ```c
   cat_l_161_α:  NPUSH_fn();          // forward path only
   cat_r_161_α:  pat_X4(entry=0)
   cat_r_161_β:  pat_X4(entry=1)      // backtrack: NPUSH NEVER FIRES
   cat_r_160_α:  Reduce(tag, ntop())  // ntop()=0 → pops 0, pushes extra node
   cat_r_159_α:  NPOP_fn()
   ```
   NPUSH only on `_entry_np==0` path. Backtrack enters via `cat_r_161_β`, skips NPUSH.
   `ntop()=0` → `Reduce(".."/"|", 0)` inflates stack instead of collapsing it.

   **Fix location: `src/sno2c/emit_byrd.c` E_OPSYN case (~line 2108)**
   NPUSH must fire on both forward AND backtrack entry. Two options:
   - **Option A (preferred):** Emit NPUSH before the cat_l dispatch so both paths hit it:
     ```c
     // alpha entry:
     B("%s: NPUSH_fn(); goto %s_inner_α;\n", alpha, uid);
     // beta entry — add NPUSH here too:
     B("%s: NPUSH_fn(); goto %s_inner_β;\n", beta, uid);
     ```
   - **Option B:** Emit `if (!NHAS_FRAME_fn()) NPUSH_fn();` at Reduce site.

   Also done session111:
   - `emit_simple_val` E_QLIT: any value containing `nTop()` → `INTVAL(ntop())` ✅
   - beauty_full.c: 3x `STRVAL("*(GT(nTop(),1) nTop())")` → `INTVAL(ntop())` ✅
   - Deleted 31 stale artifact snapshots (sessions 50–105) ✅ commit `d72606a`

2. After 102_output PASS: run `bash test/crosscheck/run_beauty.sh`, continue ladder.
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
