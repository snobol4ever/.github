# SESSION-icon-jvm.md — Icon × JVM (snobol4x)

**Repo:** snobol4x · **Frontend:** Icon · **Backend:** JVM (Jasmin)
**Session prefix:** `IJ` · **Trigger:** "playing with Icon JVM"
**Driver:** `icon_driver -jvm foo.icn -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `icon_driver foo.icn -o foo.asm -run` (x64 ASM backend)
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Icon language, IR nodes, milestones | `FRONTEND-ICON.md` | parser/AST questions |
| Full milestone history | `ARCH-icon-jvm-history.md` | completed work, milestone IDs |
| JCON test analysis | `ARCH-icon-jcon.md` | rung36 oracle, four-port templates |
| JVM bytecode patterns | `ARCH-overview.md` | Byrd box → JVM mapping |

---

## §BUILD

```bash
cd snobol4x
gcc -Wall -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
# icon_semicolon is a one-time batch conversion tool — NOT used at test time
gcc -O2 -o /tmp/icon_semicolon src/frontend/icon/icon_semicolon.c
export JAVA_TOOL_OPTIONS=""
```

## §TEST

```bash
for s in test/frontend/icon/run_rung*.sh; do bash $s /tmp/icon_driver 2>/dev/null; done | grep -E "^---"
# rung36 corpus is pre-converted — compile directly, no icon_semicolon
bash test/frontend/icon/run_rung36.sh /tmp/icon_driver 2>/dev/null | grep -E "^PASS|^FAIL|^---"
```

## Key Files

| File | Role |
|------|------|
| `src/frontend/icon/icon_emit_jvm.c` | JVM emitter — main work file |
| `src/frontend/icon/icon_emit.c` | x64 ASM emitter — Byrd-box oracle |
| `src/backend/jvm/jasmin.jar` | Assembler |
| `test/frontend/icon/corpus/` | Test corpus |

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon JVM** | `main` IJ-57 — TK_AUGCONCAT fix ✅ | `87325b3` IJ-57 | M-IJ-JCON-HARNESS |

### IJ-57 progress

**Fix landed:** `TK_AUGCONCAT` with numeric RHS now emits `invokestatic Long/toString(J)` before `putstatic` — resolves VerifyError on `out ||:= i` (sieve demo6, t01 primes).

**ICN_SEQ_EXPR failure-relay bug (next blocker):**
In a compound block `{ stmt1; stmt2; }`, when `stmt1` is an `if`-without-`else` and its condition fails, the ω port goes to `icn_2_pump` (outer every loop) instead of continuing to `stmt2`.

Root cause: `ij_emit_seq_expr` does not apply the failure-relay pattern for `if`-no-else children. The `while/do` body emitter (lines 3826–3863) has `relay_f[i]: goto cca[i+1]` which is exactly correct. `ij_emit_seq_expr` needs the same treatment.

**Fix location:** `icon_emit_jvm.c`, function `ij_emit_seq_expr` — when emitting a sequence `(E1; E2; ... En)`, each non-last child's ω must go to the next child's α (not propagate to outer ω). Pattern already proven in the while/do body emitter at line 3826.

### IJ-56 progress — M-IJ-JCON-HARNESS (HEAD f10a133)

**rung01–35: 153/153 PASS. Zero regressions.**

**Work done this session:**
- `TK_AUGCONCAT` hardcoded as 35, actual value 36 (TK_AUGPOW=35) — fixed in both `ij_emit_augop` and `ij_expr_is_string` ICN_AUGOP case; arithmetic augop switch converted to symbolic constants
- Dual-register string-typed vars under both `icn_pv_<proc>_<var>` and `icn_gvar_<var>` in pre-pass 1 flat loop and `ij_prepass_types`
- **Pass 1e** (new): run type pre-passes for all procs before "mark string-returning procs" scan so `ij_statics` is populated when `ij_expr_is_string(ICN_VAR)` is called — fixes string-returning procs (e.g. `roman`) not being marked → call sites picking up `icn_retval J` instead of `icn_retval_str`
- `ij_jasmin_ldc()` helper: escapes `"`, `\`, `\n`, `\r`, `\t` in `ldc` strings — fixed 11 Jasmin compile errors from string literals containing double quotes
- `ICN_SUSPEND` added to no-sdrain skip list — suspend fires γ with empty stack (value stored to icn_retval before sret), `pop2` on resume path caused VerifyError
- `ij_expr_is_obj()` new predicate: union of String + list + table + record + key/sort/put/open builtins; all `pop`/`pop2` drain decisions now use `ij_expr_is_obj` instead of just `ij_expr_is_string`
- `ICN_IDENTICAL`, `ICN_NONNULL`, `ICN_SECTION_PLUS/MINUS`, `ICN_MATCH` added to `ij_expr_is_string`
- `icon_lex.h` now included in `icon_emit_jvm.c` for TK_* symbolic constants
- Conflict resolution: remote had SD-29 (same TK_AUGCONCAT fix in different context), PJ-81b, PJ-81c commits

**rung36 status: 0 pass, 51 fail (all runtime), 24 xfail.**
- compile_err: 11 → 0 ✅
- verify_err: 33 → 40 (was hidden behind compile errors; newly unblocked tests hit verify)
- wrong_output: 7 → 11 (same reason)

### NEXT ACTION — M-IJ-JCON-HARNESS

**Goal:** All non-xfail rung36 tests PASS (t01–t52, skipping t31/t53–t75 xfail). Currently 0/51.

**Critical discovery — `icn_s5_sdrain` mystery:**
In `icn_meander` (t15), `icn_s5_sdrain: pop2` appears in the Jasmin but has NO goto pointing to it — it's dead code. The backward emit loop debug-traced only i=1,2,3 for `proc=meander`, so the label is NOT generated by the `ij_emit_proc` sdrain loop. It must come from **a second sdrain-label emission site** elsewhere in `icon_emit_jvm.c`. Search for all places that `snprintf` or `J(` a string containing `sdrain` — the bug is there.

**Remaining VerifyErrors (40/51):**

Two dominant patterns:
1. **"Expecting object/array on stack"** — String/ref expected but long found (or vice versa). String-returning expressions not detected by `ij_expr_is_obj`. Likely culprits: user-defined procs that return strings (now partially fixed by Pass 1e, but multi-proc programs may still have ordering issues), `write()` return type in complex contexts.
2. **"Unable to pop operand off an empty stack"** — `pop2` on dead/empty-stack path. The `icn_s5_sdrain` mystery above is one instance. Others may come from the same unknown second emission site.

**Wrong output tests (11/51):**
- t01: empty output — `next` inside nested `every/if` — primes (listed in original §NOW)
- t02: labels print but no values — multi-arg `write` losing non-string args
- t03: `0` instead of `&null` — `image(&null)` bug
- t07: `center()` off by one
- t08: `image()` quoting — should wrap strings in `"`
- t11: real printed as `19683.0` instead of `19683` — `real || int` formatting
- t13: write with multiple args losing values
- t21, t24, t34: augop result not returned / image(&null)
- t30: substring/bang issue

**Bootstrap IJ-57:**
```bash
git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y default-jdk
cd snobol4x
gcc -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
# Confirm rung01-35 clean:
for s in test/frontend/icon/run_rung*.sh; do bash $s /tmp/icon_driver 2>/dev/null; done | grep -E "^---"
# Run rung36:
bash test/frontend/icon/run_rung36.sh /tmp/icon_driver 2>/dev/null | grep -E "^PASS|^---"
# Expected: 0 pass, 51 fail, 24 xfail

# Triage all failures:
JASMIN=src/backend/jvm/jasmin.jar
CORPUS=test/frontend/icon/corpus/rung36_jcon
compile_errs=0; verify_errs=0; wrong_out=0; pass=0
for icn in $CORPUS/t*.icn; do
  base="${icn%.icn}"
  [ -f "${base}.xfail" ] && continue
  [ -f "${base}.expected" ] || continue
  /tmp/icon_driver -jvm "$icn" -o /tmp/t36.j 2>/dev/null
  cls=$(grep -m1 '\.class' /tmp/t36.j 2>/dev/null | awk '{print $NF}')
  asm_out=$(java -jar $JASMIN /tmp/t36.j -d /tmp/ 2>&1 | grep -v "Generated\|JAVA_TOOL")
  if [ -n "$asm_out" ]; then compile_errs=$((compile_errs+1)); continue; fi
  run_out=$(java -cp /tmp $cls 2>&1 | grep -v JAVA_TOOL)
  if echo "$run_out" | grep -q "VerifyError\|LinkageError\|Unable to initialize"; then
    verify_errs=$((verify_errs+1))
  elif [ "$run_out" = "$(cat ${base}.expected)" ]; then
    pass=$((pass+1))
  else
    wrong_out=$((wrong_out+1))
  fi
done
echo "compile_err=$compile_errs verify_err=$verify_errs wrong_output=$wrong_out pass=$pass"
```

**Immediate next steps:**
1. Find the second `sdrain`-label emission site (grep `snprintf.*sdrain\|J.*sdrain` in `icon_emit_jvm.c` — there may be one inside `ij_emit_seq_expr` or `ij_emit_and` or similar that generates per-child drains using the same naming)
2. Fix remaining "Expecting object/array" VerifyErrors — check `ij_expr_is_obj` coverage for user-proc return types and complex call chains
3. Fix wrong-output tests starting with t03 (`image(&null)`) and t08 (`image()` quoting) — these are runtime issues in `icon_runtime.c` or the `image` builtin emitter
