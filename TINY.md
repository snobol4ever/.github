# TINY.md — SNOBOL4-tiny (L2)

SNOBOL4-tiny: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `beauty-crosscheck` — Sprint A — rung 12 crosscheck tests
**HEAD:** `100eb50` — session105: $ left-assoc parse fix + E_DOL chain emitter (compile error pending)
**Milestone:** M-BEAUTY-CORE → M-BEAUTY-FULL

**Next action:**
1. Build beauty_full_bin (commands below) — verify 106/106
2. **Active bug:** E_DOL computed-right label duplication in `emit_byrd.c`
   - Two fixes applied this session but label dup remains:
     (a) `parse_expr12` changed right→left associative for `$`/`.` ✅
     (b) E_DOL case: computed-right path emits left then right as concat-chain ✅
   - Current error: `dolc_N_rb` defined twice — once by E_INDR via raw B(), once by PLG(mid_b, l_lb)
   - Fix needed: use separate `l_lb` (left beta, PLG-defined) and `l_rb` (right beta, B-defined),
     then wire `l_rb → l_lb` with raw `B("%s: goto %s;\n", l_rb, l_lb)`
   - The Python replace failed last session because exact string didn't match — read the block
     with `sed -n 'NNN,MMMp'` first, then apply carefully
3. After label dup fixed: rebuild, run run_beauty.sh — expect 102_output to pass
3. Once pat_Function correctly gatekeeps, run beauty crosscheck — expect 102+ to pass

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
