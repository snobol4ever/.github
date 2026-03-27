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
| Full milestone history | `ARCH-icon-jvm.md` | completed work, milestone IDs |
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
| **Icon JVM** | `main` IJ-56 — M-IJ-JCON-HARNESS 🔄 | `2074158` SD-30b | M-SD-4 (palindrome ICON-JVM silent fail) |

### IJ-56 progress — M-IJ-JCON-HARNESS (HEAD 708964d)

**rung01–35: 153/153 PASS. Zero regressions.**

**Work done this session:**
- Added `rung36_jcon/` — 75 JCON oracle tests (t01–t75)
- `icon_semicolon.c` — one-time converter: C-style semicolons (semi ends statement; no semi after `}`); `TK_RBRACE` removed from triggers
- **Corpus pre-converted**: all 75 `rung36_jcon/*.icn` now stored in semicolon-explicit form. `icon_semicolon` is a batch tool only, never called at test time.
- `run_rung36.sh` — simplified: compiles `.icn` directly, no SEMI arg
- `icon_parse.c` — `static` → `local`; omitted function args emit `&null`
- `icon_lex.c` — `NNrXX` radix literals

**rung36 status: 0 pass, 51 fail (all runtime), 24 xfail. Stream A (parse) DONE — all 51 compile.**

### NEXT ACTION — M-IJ-JCON-HARNESS

**Goal:** All non-xfail rung36 tests PASS (t01–t52, skipping t31/t53–t75 xfail). Currently 0/51.

**Stream B — Runtime bugs (all 51 compile, none pass):**
- `next` inside nested `every`/`if` — primes empty — t01
- `image(&null)` returns `0` not `&null` — t03, t32
- `center(s,n)` off by one — t07
- `trim(s)` / `image()` quoting — t08
- `level()` recursive depth tracking — t10
- (many more — full triage needed)

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
# Run rung36 (no icon_semicolon needed — corpus pre-converted):
bash test/frontend/icon/run_rung36.sh /tmp/icon_driver 2>/dev/null | grep -E "^PASS|^---"
# Expected: 0 pass, 51 fail (runtime), 24 xfail
```


**SD-27 blocker (list subscript) — PARTIALLY FIXED (commit 26eccbe):**

What was done:
- Added `'S'` type tag for string-element ArrayLists (vs `'L'` for numeric)
- `ij_emit_subscript()`: new ArrayList branch using `ArrayList.get(i-1)` + `checkcast Long`/`checkcast String`
- `ij_expr_is_string(ICN_SUBSCRIPT)`: returns 0 for numeric list subscript, 1 for string list
- Pre-pass registers `'S'` under BOTH `icn_pv_proc_var` AND `icn_gvar_var` names
- Assignment emitter: `is_strlist` branch in both local and global var paths
- `ij_expr_is_list()`: recognises `'S'`-tagged vars as lists
- Field emitter: `'S'` → `Ljava/util/ArrayList;`
- `ij_declare_static_typed()`: `'L'` cannot overwrite `'S'`

Current state: roman demo SNOBOL4 ✅ Prolog ✅ Icon **runs but outputs `0\n0\n0`**

**Remaining bug — `result` variable outputs `0` instead of roman numeral string:**

Root cause: `result := ""` is a String assignment inside procedure `roman`.
The `every i := 1 to *vals do { result ||:= syms[i]; ... }` body emits
`result` load before the assignment statement is processed by the pre-pass,
so `result` is typed `J` (long, default) instead of `A` (String).

Minimal repro:
```icon
procedure roman(n);
    result := "";
    every i := 1 to 3 do {
        result ||:= "X";
    };
    return result;
end
procedure main();
    write(roman(5));
end
```

Expected: `XXX`. Actual: `0`.

Fix needed in `icon_emit_jvm.c`:
- The pre-pass first loop (around line 5991 in `ij_emit_proc`) only scans
  **top-level** `stmt->kind == ICN_ASSIGN` statements. `result := ""` IS
  top-level — check why it's not being caught.
- Hypothesis: `result` variable has slot ≥ 0 (it's a local), so `fld` =
  `icn_pv_roman_result`. The pre-pass should call `ij_declare_static_str(fld)`.
  But then at every-body emit time, `result` is loaded as `J`.
- Likely cause: every-body is emitted BEFORE the statement chain (Byrd-box
  every emits generator first, body second in code layout — but body executes
  at runtime when generator yields). The pre-pass walk may miss body statements
  nested inside `ICN_EVERY`.

Pre-pass 3 (`ij_prepass_types`) IS a recursive walk — it should catch
`result := ""` even inside every-body. So the issue may be that `result`'s
`'A'` tag IS registered, but the load of `result` inside the every-body
uses the wrong field name (local vs global mismatch — same bug as `syms`).

Apply the same dual-registration fix used for `syms`:
In the pre-pass first loop AND `ij_prepass_types`, for string-typed vars,
also register under the alternate field name:
```c
if (ij_expr_is_string(rhs)) {
    ij_declare_static_str(fld);
    /* dual-register: */
    if (slot >= 0) { char g[80]; snprintf(g,80,"icn_gvar_%s",lhs->val.sval); ij_declare_static_str(g); }
    else           { char f2[128]; ij_var_field(lhs->val.sval,f2,sizeof f2); ij_declare_static_str(f2); }
}
```

Same fix needed in `ij_prepass_types` (the recursive walk, ~line 5917).
