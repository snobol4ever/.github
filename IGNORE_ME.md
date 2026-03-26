# HOLD_ARCHIVE.md — Milestones On Hold

All milestones below were moved here from PLAN.md on 2026-03-21 (session F-211 / clean-slate reset).
They are **not deleted** — they are on hold pending a fresh strategic plan.
Completed milestones (✅) remain in PLAN.md. Only incomplete/deferred milestones live here.

---

## TINY (snobol4x) — On Hold

| ID | Trigger | Last Known Status |
|----|---------|-------------------|
| **M-ASM-TREEBANK** | treebank.sno correct output via ASM backend; artifacts/asm/samples/treebank.s assembles clean and diff vs CSNOBOL4 oracle empty | ❌ treebank.s assembles clean (B-226); runtime correctness not yet verified |
| **M-ASM-CLAWS5** | claws5.sno correct output via ASM backend; artifacts/asm/samples/claws5.s assembles clean and diff vs CSNOBOL4 oracle empty | ❌ claws5.s ~95% — 3 undefined beta labels (NRETURN fns); gates on NRETURN fix |
| **M-ASM-RUNG10** | rung10/ — DEFINE/recursion/locals/NRETURN/FRETURN/APPLY 9/9 PASS via ASM backend | ❌ 4/9 WIP |
| **M-ASM-RUNG11** | rung11/ — ARRAY/TABLE/DATA types 7/7 PASS via ASM backend | ❌ Sprint A-RUNG11 |
| **M-ASM-LIBRARY** | library/ crosscheck tests PASS via ASM backend; -include resolved correctly | ❌ Sprint A-LIBRARY |
| **M-ENG685-TREEBANK-SNO** | treebank.sno correct via CSNOBOL4: nPush/nInc/nPop + Shift/Reduce; .ref oracle committed | ❌ Sprint B-ENG685-SNO |
| **M-ENG685-CLAWS** | claws5.sno — CLAWS5 POS corpus tokenizer; .ref oracle committed; PASS via CSNOBOL4 and ASM backend | ❌ Sprint B-ENG685 — ~95%: 3 undefined β labels (NRETURN fns) |
| **M-ENG685-TREEBANK** | treebank.sno — Penn Treebank S-expr parser; .ref oracle committed; PASS via CSNOBOL4 and ASM backend | ❌ Sprint B-ENG685 |
| **M-ASM-MACROS** | NASM macro library `snobol4_asm.mac` — every emitted line is `LABEL  MACRO(args)  GOTO` | ❌ Sprint A12 |
| **M-ASM-IR** | ASM IR phase: AsmNode tree between parse and emit | ⏸ DEFERRED — premature unification risks blocking ASM progress |
| **M-BOOTSTRAP** | sno2c_stage1 output = sno2c_stage2 | ❌ |
| **M-SC-CORPUS-R2** | control/control_new all PASS via `-sc -asm` | ❌ |
| **M-SC-CORPUS-R3** | patterns/capture all PASS via `-sc -asm` | ❌ |
| **M-SC-CORPUS-R4** | strings/ all PASS via `-sc -asm` | ❌ |
| **M-SC-CORPUS-R5** | keywords/functions/data all PASS via `-sc -asm` | ❌ |
| **M-SC-CORPUS-FULL** | 106/106 SC equivalent of SNOBOL4 crosscheck | ❌ |
| **M-SNOC-ASM-SELF** | snocone.sc compiles itself via `-sc -asm`; diff oracle empty | ❌ Sprint SC6-ASM |
| **M-SNOC-EMIT** | `-sc` flag in sno2c; `OUTPUT = 'hello'` .sc → C binary PASS | ❌ deferred — C backend |
| **M-SNOC-CORPUS** | SC corpus 10-rung all PASS (C backend) | ❌ Sprint SC4 (deferred) |
| **M-SNOC-SELF** | snocone.sc compiles itself via C pipeline; diff oracle empty | ❌ Sprint SC5 (deferred) |

---

## JVM backend — snobol4x TINY — On Hold

| ID | Trigger | Last Known Status |
|----|---------|-------------------|
| **M-JVM-ROMAN** | roman.sno correct output via JVM backend | ❌ Jasmin error: L_RETURN label not added — RETURN routing bug in emit_byrd_jvm.c |
| **M-JVM-TREEBANK** | treebank.sno correct output via JVM backend | ❌ Jasmin error: L_FRETURN label not added — FRETURN routing bug |
| **M-JVM-CLAWS5** | claws5.sno correct output via JVM backend | ❌ Jasmin error: L_StackEnd (included label) not defined — include/label scope bug |

---

## JVM (snobol4jvm) — On Hold

| ID | Trigger | Last Known Status |
|----|---------|-------------------|
| M-JVM-EVAL | Inline EVAL! — arithmetic no longer calls interpreter | ❌ Sprint `jvm-inline-eval` |
| M-JVM-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| M-JVM-BOOTSTRAP | snobol4-jvm compiles itself | ❌ |

---

## NET backend — snobol4x TINY — On Hold

| ID | Trigger | Last Known Status |
|----|---------|-------------------|
| **M-NET-R4** | functions/ data/ — Rungs 10–11 PASS | ❌ Sprint N-R4 — 8 remain: ARRAY/TABLE/DATA + roman |
| **M-NET-INDR** | harness 111/111 — fix `$varname` indirect read: Dictionary/stsfld desync | ❌ Sprint N-210 |
| **M-NET-BEAUTY** | beauty.sno self-beautifies via NET backend | ❌ Gates on M-NET-INDR |
| **M-NET-TREEBANK** | treebank.sno correct output via NET backend | ❌ Gates on M-NET-INDR |
| **M-NET-CLAWS5** | claws5.sno correct output via NET backend | ❌ Gates on M-NET-INDR |

---

## DOTNET (snobol4dotnet) — On Hold

| ID | Trigger | Last Known Status |
|----|---------|-------------------|
| **M-NET-SAVE-DLL** | `-w file.sno` → `file.dll` (threaded assembly); `snobol4 file.dll` runs it | ❌ Sprint `net-save-dll` |
| **M-NET-EXT-NOCONV** | SPITBOL noconv pass-through: ARRAY/TABLE/PDBLK passed unconverted | ❌ Sprint `net-ext-noconv` |
| M-NET-SNOCONE | Snocone self-test: compile snocone.sc, diff oracle | ❌ |
| **M-NET-POLISH** | 106/106 corpus rungs pass, diag1 35/35, benchmark grid published | ❌ see DOTNET.md |
| M-NET-BOOTSTRAP | snobol4-dotnet compiles itself | ❌ |

---

## Shared — On Hold

| ID | Trigger | Last Known Status |
|----|---------|-------------------|
| M-FEATURE-MATRIX | Feature × product grid 100% green | ❌ |
| M-BENCHMARK-MATRIX | Benchmark × product grid published | ❌ |

---

*To resurrect a milestone: move it back to PLAN.md with updated status and sprint assignment.*

---
## RENAME.md (one-time rename plan — org rename complete 2026-03)
# RENAME.md — SNOBOL4-plus → snobol4ever

One-time rename execution plan. Eight phases, strict order. Do not reorder — sequencing is load-bearing.

---

## Locked Naming Rules

| context | format | example |
|---------|--------|---------|
| marketing name | no dashes, all lowercase | `snobol4jvm` |
| github repo slug | one dash separator, all lowercase | `snobol4-jvm` |
| cli command | `sno4` prefix, no dashes | `sno4jvm` |
| package manager | all lowercase, no dashes | `snobol4jvm` |
| the language itself | ALL CAPS, unchanged | `SNOBOL4` (technical/historical refs only) |

---

## Complete Name Grid

| product | marketing | repo | cli | package mgr | namespace |
|---------|-----------|------|-----|-------------|-----------|
| **ORG** | | | | | |
| organization | `snobol4ever` | `github.com/snobol4ever` | — | — | — |
| **COMPILERS** | | | | | |
| native kernel | `snobol4x` | `snobol4x` | `sno4x` | — | `snobol4x.c` / `snoc` (internal) |
| jvm backend | `snobol4jvm` | `snobol4-jvm` | `sno4jvm` | Maven: `snobol4/jvm` | `snobol4.jvm` |
| .net backend | `snobol4dotnet` | `snobol4-dotnet` | `sno4net` | NuGet: `snobol4dotnet` | `Snobol4.Dotnet` ¹ |
| **PATTERN LIBRARIES** | | | | | |
| python | `snobol4python` | `snobol4-python` | — | PyPI: `snobol4python` | `import snobol4python` |
| c# | `snobol4csharp` | `snobol4-csharp` | — | NuGet: `snobol4csharp` | `Snobol4.CSharp` ¹ |
| **INFRASTRUCTURE** | | | | | |
| test corpus | `snobol4corpus` | `snobol4-corpus` | — | — | — |
| test harness | `snobol4harness` | `snobol4-harness` | — | — | — |
| **EXPERIMENTAL** | | | | | |
| cpython ext | `snobol4artifact` | `snobol4-artifact` | — | PyPI: `snobol4artifact` | `import snobol4artifact` |

¹ C# namespaces follow PascalCase by platform convention — the one intentional exception to the all-lowercase rule.

---

## Phase 1 — Text edits in `.github` repo

Edit all `.md` files. **Do not push yet.**

### URL substitutions

| find | replace |
|------|---------|
| `github.com/SNOBOL4-plus/SNOBOL4-tiny` | `github.com/snobol4ever/snobol4x` |
| `github.com/SNOBOL4-plus/SNOBOL4-jvm` | `github.com/snobol4ever/snobol4jvm` |
| `github.com/SNOBOL4-plus/SNOBOL4-dotnet` | `github.com/snobol4ever/snobol4dotnet` |
| `github.com/SNOBOL4-plus/SNOBOL4-corpus` | `github.com/snobol4ever/snobol4corpus` |
| `github.com/SNOBOL4-plus/SNOBOL4-harness` | `github.com/snobol4ever/snobol4harness` |
| `github.com/SNOBOL4-plus/SNOBOL4-python` | `github.com/snobol4ever/snobol4python` |
| `github.com/SNOBOL4-plus/SNOBOL4-cpython` | `github.com/snobol4ever/snobol4artifact` |
| `github.com/SNOBOL4-plus/SNOBOL4-csharp` | `github.com/snobol4ever/snobol4csharp` |
| `github.com/SNOBOL4-plus/.github` | `github.com/snobol4ever/.github` |

### Brand text substitutions

| find | replace |
|------|---------|
| `SNOBOL4ever` | `snobol4ever` |
| `SNOBOL4now` | `snobol4now` |
| `SNOBOL4-tiny` (repo refs) | `snobol4x` |
| `SNOBOL4-jvm` (repo refs) | `snobol4jvm` |
| `SNOBOL4-dotnet` (repo refs) | `snobol4dotnet` |
| `SNOBOL4-corpus` (repo refs) | `snobol4corpus` |
| `SNOBOL4-cpython` (repo refs) | `snobol4artifact` |
| `SNOBOL4-python` (repo refs) | `snobol4python` |
| `SNOBOL4-csharp` (repo refs) | `snobol4csharp` |
| `SNOBOL4-plus` (org refs) | `snobol4ever` |

### Files to touch

`README.md` · `PLAN.md` · `SESSION.md` · `TINY.md` · `JVM.md` · `DOTNET.md` · `CORPUS.md` · `HARNESS.md` · `STATUS.md` · `MISC.md` · `PATCHES.md` · `profile/README.md`

### SESSIONS_ARCHIVE.md — special handling

Append-only. Do not find/replace. Add one line at the very top only:

```
> Org renamed SNOBOL4-plus → snobol4ever, March 2026. Historical entries use old names.
```

---

## Phase 2 — Commit (do not push yet)

```bash
git add -A
git commit -m "rename: SNOBOL4-plus -> snobol4ever, brand casing, naming rules"
```

---

## Phase 3 — Rename the GitHub org

GitHub Settings → Organization → Rename:

`SNOBOL4-plus` → `snobol4ever`

GitHub creates redirects from all old URLs automatically.

---

## Phase 4 — Rename each GitHub repo

Settings → General → Repository name, one at a time:

| from | to |
|------|----|
| `SNOBOL4-tiny` | `snobol4x` |
| `SNOBOL4-jvm` | `snobol4jvm` |
| `SNOBOL4-dotnet` | `snobol4dotnet` |
| `SNOBOL4-corpus` | `snobol4corpus` |
| `SNOBOL4-harness` | `snobol4harness` |
| `SNOBOL4-python` | `snobol4python` |
| `SNOBOL4-cpython` | `snobol4artifact` |
| `SNOBOL4-csharp` | `snobol4csharp` |
| `.github` | `.github` (unchanged — GitHub requires this name) |

---

## Phase 5 — Update all local git remotes

Run in each cloned repo on every machine:

```bash
git remote set-url origin https://github.com/snobol4ever/snobol4x
git remote set-url origin https://github.com/snobol4ever/snobol4jvm
git remote set-url origin https://github.com/snobol4ever/snobol4dotnet
git remote set-url origin https://github.com/snobol4ever/snobol4corpus
git remote set-url origin https://github.com/snobol4ever/snobol4harness
git remote set-url origin https://github.com/snobol4ever/snobol4python
git remote set-url origin https://github.com/snobol4ever/snobol4artifact
git remote set-url origin https://github.com/snobol4ever/snobol4csharp
git remote set-url origin https://github.com/snobol4ever/.github
```

---

## Phase 6 — Push `.github`

```bash
git push
git log --oneline -1
```

---

## Phase 7 — Source code and comments in each repo

For each repo, audit and update:
- Comments referencing `SNOBOL4-plus` org name
- Hardcoded GitHub URLs in source files
- `README.md`, `INSTALL.md`, `CONTRIBUTING.md` in each repo root
- CI/CD config (`.github/workflows`) referencing old org or repo names

**`snobol4x` internal note:** `snoc` stays as the internal compiler binary name. `sno4x` is the user-facing command. Do not rename `snoc`.

Commit each repo:
```bash
git commit -m "rename: org SNOBOL4-plus -> snobol4ever, brand casing update"
```

**PyPI — `snobol4artifact`:** If `SNOBOL4-cpython` is published on PyPI under the old name, publish a new `snobol4artifact` package and add a deprecation notice to the old one. PyPI does not support renames.

**NuGet — namespace convention:** Coordinate with Jeffrey. Package name is `snobol4dotnet` (lowercase) but namespace is `Snobol4.Dotnet` — intentional PascalCase exception for C# convention.

---

## Phase 8 — Verify

```bash
grep -ri "SNOBOL4-plus" . --include="*.md"   # expect: empty
grep -ri "SNOBOL4-plus" . --include="*.c"    # expect: empty
grep -ri "SNOBOL4-plus" . --include="*.clj"  # expect: empty
grep -ri "SNOBOL4-plus" . --include="*.cs"   # expect: empty
```

Check redirects (GitHub grace period is generous but not infinite):
```bash
curl -I https://github.com/SNOBOL4-plus/SNOBOL4-tiny
# expect: 301 Moved Permanently → github.com/snobol4ever/snobol4x
```

---

## Open Items

| item | question | owner |
|------|----------|-------|
| `snoc` vs `sno4x` | `snoc` = internal build tool, `sno4x` = user command. Confirm. | Lon |
| `snobol4x` naming | ✅ Decided 2026-03-17. `snobol4x` replaces `snobol4all` and `snobol4tiny`. Fast, cross-platform, no ceiling implied. | Lon |
| PyPI `snobol4artifact` | Is SNOBOL4-cpython currently on PyPI? If yes, new package needed. | Lon |
| NuGet casing | `Snobol4.Dotnet` namespace — coordinate on C# convention exception. | Jeffrey |
| `SESSIONS_ARCHIVE.md` | Header note only. Do not rewrite history. | Lon |

---
## BEAUTY_BUG_HANDOFF.md (stale blocked-bug note 2026-03-24)
# M-BUG-BOOTSTRAP-FENCE — FENCE Pattern Matching Broken in ASM Backend

**Date:** 2026-03-24  
**Sprint:** M-BEAUTIFY-BOOTSTRAP  
**Status:** BLOCKED — root cause identified, fix not yet implemented  
**Invariant:** 106/106 ASM corpus ALL PASS ✅

---

## Summary

`FENCE(pat)` always fails when used as a pattern match in the ASM backend. This is the **actual root cause** of the "Parse Error" in beauty.sno's bootstrap. All other fixes (NAMED_PAT_MAX, buffer bumps, E_NAM binary, stmt_concat DT_N) are correct and necessary but not sufficient.

---

## How to Reproduce

```bash
cd /home/claude/snobol4ever/snobol4x
cat > /tmp/fence_test.sno << 'SNOEOF'
               'hello world' FENCE('hello')  :F(FAIL)
               OUTPUT = 'OK'   :(END)
FAIL           OUTPUT = 'FAIL'
END
SNOEOF

./sno2c -asm /tmp/fence_test.sno -o /tmp/fence_test.asm
nasm -f elf64 -I src/runtime/asm/ -o /tmp/fence_test.o /tmp/fence_test.asm
WORK=/tmp/beauty_build
RT_OBJS="$WORK/stmt_rt.o $WORK/snobol4.o $WORK/mock_includes.o $WORK/snobol4_pattern.o $WORK/mock_engine.o $WORK/blk_alloc.o $WORK/blk_reloc.o"
gcc -no-pie /tmp/fence_test.o $RT_OBJS -lgc -lm -o /tmp/fence_bin
echo "" | /tmp/fence_bin
# Expected: OK
# Actual:   FAIL
```

---

## Root Cause Chain

The Parse Error in beauty.sno traces back through this chain:

1. **beauty.sno** uses `Command = FENCE(*Comment | *Control | *Stmt)`
2. `Parse = ARBNO(*Command)` — depends on Command working
3. `FENCE(...)` always fails → Command never matches → Parse fails → "Parse Error"

### Why FENCE fails

`FENCE('hello')` is compiled as:
```asm
CALL1_STR   S_FENCE, S_hello    ; calls APPLY_fn("FENCE", "hello") → DT_P
CALL_PAT_α  cpat0_t, ...        ; calls stmt_match_descr with that DT_P
```

`stmt_match_descr` → `match_pattern_at` → `try_match_at` → `engine_match_ex`.

With `PAT_DEBUG=1`, every cursor position returns `matched=0 end=0`. The `XFNCE` node type is not being handled correctly by `engine_match_ex` / `materialise`.

### Where to look

The bug is in `src/runtime/snobol4/snobol4_pattern.c` in the `materialise()` function or `engine_match_ex()`. Search for `XFNCE`:

```bash
grep -n "XFNCE\|case.*XFNCE\|T_FENCE\|FENCE" src/runtime/snobol4/snobol4_pattern.c
```

The `materialise()` function handles `XFNCE` and must produce a `T_FENCE` pattern node for `engine_match_ex`. Check whether:
- `materialise` returns epsilon for XFNCE (wrong)
- `T_FENCE` is handled in `engine_match_ex` 
- The `XFNCE` node's `left` child is being set but not materialised

### Note: FENCE is not in the corpus

The 106/106 corpus tests do NOT exercise `FENCE` — so this bug was latent and never caught. The beauty bootstrap is the first test that hits it.

---

## What Has Been Fixed (Do Not Revert)

All changes in `src/backend/x64/emit_byrd_asm.c` since B-288:

| Fix | What it does |
|-----|-------------|
| `NAMED_PAT_MAX 64→512` | Was silently dropping Parse/Command/Compiland |
| `MAX_BOXES 64→512` | Was silently missing DATA block templates |
| `call_slots 256→4096` | Was silently dropping BSS slots for user function calls |
| `MAX_VARS/LITS/STRS/LABELS` bumped | General capacity for beauty's 420 named patterns |
| `E_NAM binary case` in `emit_expr` | `epsilon . *PushCounter()` now calls `stmt_concat` correctly |
| `stmt_concat DT_N` fix | Treats name-refs as capture targets in pattern concat |

All fixes confirmed: **106/106 corpus ALL PASS**.

---

## Current State of beauty Build

```bash
cd /home/claude/snobol4ever/snobol4x
WORK=/tmp/beauty_build
./sno2c -asm -Idemo/inc -I./src/frontend/snobol4 demo/beauty.sno -o $WORK/beauty.asm
nasm -f elf64 -I src/runtime/asm/ -o $WORK/beauty.o $WORK/beauty.asm
# Runtime objects (rebuild stmt_rt.o with DT_N fix):
RT=src/runtime; SNO2C_INC=src/frontend/snobol4
gcc -O0 -g -c "$RT/asm/snobol4_stmt_rt.c" -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/stmt_rt.o"
gcc -O0 -g -c "$RT/snobol4/snobol4.c"         -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/snobol4.o"
gcc -O0 -g -c "$RT/mock/mock_includes.c"       -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/mock_includes.o"
gcc -O0 -g -c "$RT/snobol4/snobol4_pattern.c" -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/snobol4_pattern.o"
gcc -O0 -g -c "$RT/mock/mock_engine.c"         -I"$RT/snobol4" -I"$RT" -I"$SNO2C_INC" -w -o "$WORK/mock_engine.o"
gcc -O0 -g -c "$RT/asm/blk_alloc.c"            -I"$RT/asm"                              -w -o "$WORK/blk_alloc.o"
gcc -O0 -g -c "$RT/asm/blk_reloc.c"            -I"$RT/asm"                              -w -o "$WORK/blk_reloc.o"
RT_OBJS="$WORK/stmt_rt.o $WORK/snobol4.o $WORK/mock_includes.o $WORK/snobol4_pattern.o $WORK/mock_engine.o $WORK/blk_alloc.o $WORK/blk_reloc.o"
gcc -no-pie "$WORK/beauty.o" $RT_OBJS -lgc -lm -o "$WORK/beauty_bin"
# Run:
$WORK/beauty_bin < demo/beauty.sno > $WORK/beauty_asm_out.sno
diff /tmp/beauty_oracle.sno $WORK/beauty_asm_out.sno
# Still shows Parse Error — blocked on FENCE bug
```

---

## Next Steps

1. **Fix XFNCE in `materialise()`** — inspect `snobol4_pattern.c` around line 176 and in `materialise()`. Add a test case:
   ```c
   // In materialise(), case XFNCE:
   // Must produce T_FENCE with inner child properly materialised
   ```

2. **Add FENCE to corpus** — add `test_fence.sno` / `test_fence.ref` to the crosscheck corpus so this never regresses.

3. **Re-run beauty bootstrap** — after fixing FENCE, diff against oracle.

4. **Add corpus test for `epsilon . *Var` pattern** — the E_NAM binary fix should also be regression-tested.

---

## Oracle

```bash
# Verified oracle (CSNOBOL4):
INC=demo/inc snobol4 -f -P256k -Idemo/inc demo/beauty.sno < demo/beauty.sno > /tmp/beauty_oracle.sno
# /tmp/beauty_oracle.sno = 784 lines, fixed-point ✅
```
