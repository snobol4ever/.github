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
gcc -O2 -o /tmp/icon_semicolon src/frontend/icon/icon_semicolon.c
export JAVA_TOOL_OPTIONS=""
```

## §TEST

```bash
for s in test/frontend/icon/run_rung*.sh; do bash $s /tmp/icon_driver 2>/dev/null; done | grep -E "^---"
bash test/frontend/icon/run_rung36.sh /tmp/icon_driver /tmp/icon_semicolon 2>/dev/null | grep -E "^PASS|^---"
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
| **Icon JVM** | `main` IJ-56 — M-IJ-JCON-HARNESS 🔄 | `52e575c` IJ-56 | M-IJ-JCON-HARNESS |

### IJ-56 progress — M-IJ-JCON-HARNESS (HEAD 52e575c)

**rung01–35: 153/153 PASS. Zero regressions.**

**Work done this session:**
- Added `rung36_jcon/` — 75 JCON oracle tests (t01–t75), `.expected` from JCON `.std`, `.stdin` from JCON `.dat`, `.xfail` for SET/BIGINT/COEXPR/errors
- `run_rung36.sh` — pipes each `.icn` through `icon_semicolon` before compilation
- `icon_semicolon.c` — auto-semicolon converter (Icon LRM §3.1 rule); build: `gcc -O2 -o /tmp/icon_semicolon src/frontend/icon/icon_semicolon.c`
- `icon_parse.c` — `static` declarations now handled same as `local`; omitted function args `f(,x)` `f(x,)` emit `&null`
- `icon_lex.c` — `NNrXX` radix literals (16rff, 3r201, 36rcat, etc.)
- `icon_semicolon.c` — JCON preprocessor: `$<`→`[`, `$>`→`]`, `$(`→`{`, `$)`→`}`

**rung36 baseline: 38 compile errors, 13 compile+run, 0 pass (all backend content bugs)**

### NEXT ACTION — M-IJ-JCON-HARNESS

**Goal:** All non-xfail rung36 tests PASS (t01–t52, skipping t31/t53–t75 xfail). Currently 0/51.

**Two work streams:**

**Stream A — Remaining parse gaps (compile errors):**
Fix these in `icon_parse.c` / `icon_lex.c` to reduce 38 CE to ~0:
1. `if/then/else` without braces multi-line — affects t25, t32, t44, t47 (`got else`)
2. `++` cset union op — not in lexer — affects t38, t39, t43, t44 (`got +`)
3. `=:=` swap-assign op — `=:=` differs from `:=:` — affects t34, t21
4. `!expr` as function argument — `every (-3|-2|-1|0|1|2|3) ! [201,202]` — affects t02, t52
5. `initial { block }` — `initial` with brace body — affects t27
6. `s[i+:n]` / `s[i-:n]` M+:N slice forms — affects t22
7. `?E` in expression position — affects t16, t17
8. Block `do { }` in certain positions — affects t27, t50, t51

**Stream B — Backend content bugs (13 compile but produce wrong output):**
- `image(&null)` returns `0` not `&null` — affects t03, t32
- `center(s,n)` off by one — affects t07
- `trim(s)` doesn't quote output — affects t08 (actually image() issue)
- `primes` empty output — `next` inside nested `every`/`if` — t01
- `level()` empty — recursive depth tracking — t10

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
gcc -O2 -o /tmp/icon_semicolon src/frontend/icon/icon_semicolon.c
# Confirm rung01-35 clean:
for s in test/frontend/icon/run_rung*.sh; do bash $s /tmp/icon_driver 2>/dev/null; done | grep -E "^---"
# Run rung36:
bash test/frontend/icon/run_rung36.sh /tmp/icon_driver /tmp/icon_semicolon 2>/dev/null | grep -E "^PASS|^---"
# Expected: 0 pass, 38 CE, 13 run, 24 xfail — fix Stream A then Stream B
```


**SD-27 blocker (list subscript VerifyError):**
- `vals[i]` → `Bad type in putfield/putstatic` in `icon_emit_jvm.c`
- Minimal repro: `vals := [10,5,1]; i := 1; write(vals[i]);`
- Fix in: `ij_emit_subscript()` — list subscript path (not string, not table)
- Blocks: M-SD-3 roman demo
