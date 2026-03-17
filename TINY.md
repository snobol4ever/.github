# TINY.md — snobol4x (L2)

snobol4x: multiple frontends, multiple backends.
**Co-authored by Lon Jones Cherryholmes and Claude Sonnet 4.6.** When any milestone fires, Claude writes the commit.

→ Frontends: [FRONTEND-SNOBOL4.md](FRONTEND-SNOBOL4.md) · [FRONTEND-REBUS.md](FRONTEND-REBUS.md) · [FRONTEND-SNOCONE.md](FRONTEND-SNOCONE.md) · [FRONTEND-ICON.md](FRONTEND-ICON.md) · [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md)
→ Backends: [BACKEND-C.md](BACKEND-C.md) · [BACKEND-X64.md](BACKEND-X64.md) · [BACKEND-NET.md](BACKEND-NET.md) · [BACKEND-JVM.md](BACKEND-JVM.md)
→ Compiler: [IMPL-SNO2C.md](IMPL-SNO2C.md) · Testing: [TESTING.md](TESTING.md) · Rules: [RULES.md](RULES.md)

---

## NOW

**Sprint:** `asm-backend` — Sprint A5, ARBNO node
**HEAD:** `426da47` session146 (session147 work pending commit)
**Milestone:** M-ASM-ALT ✅ session147 → **M-ASM-ARBNO** next → M-ASM-CROSSCHECK → M-ASM-BEAUTY

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
| **M-ASM-ARBNO** | ARBNO: arbno_match/empty/fail PASS | ❌ | A5 |
| **M-ASM-CHARSET** | ANY/NOTANY/SPAN/BREAK PASS | ❌ | A6 |
| **M-ASM-ASSIGN** | $ capture: assign_lit/digits PASS | ❌ | A7 |
| **M-ASM-NAMED** | Named patterns: ref_astar_bstar/anbn PASS | ❌ | A8 |
| **M-ASM-CROSSCHECK** | 106/106 crosscheck via ASM backend | ❌ | A9 |
| **M-ASM-BEAUTY** | beauty.sno self-beautifies via ASM backend | ❌ | A10 |
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

## Session Start

```bash
cd /home/claude/snobol4x
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3   # verify HEAD matches above

apt-get install -y libgc-dev && make -C src/sno2c

mkdir -p /home/snobol4corpus
ln -sf /home/claude/snobol4corpus/crosscheck /home/snobol4corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh   # must be 106/106
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
| 147 | **M-ASM-ALT fires** — three oracles: `alt_first.s` (cat→first arm), `alt_second.s` (dog→second arm after left fail), `alt_fail.s` (fish→both fail, exit 1). ALT wiring: α saves `cursor_at_alt`; `left_ω` restores+jumps `right_α`; both γ→`alt_γ`; `right_ω`→`alt_ω`. Proebsting §4.5 compile-time wiring. All PASS. Next: Sprint A5 (ARBNO). | |
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
