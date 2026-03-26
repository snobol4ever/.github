# FRONTEND-ICON-JVM.md — Icon × JVM (snobol4x)

**Repo:** snobol4x · **Frontend:** Icon · **Backend:** JVM (Jasmin)
**Session prefix:** `IJ` · **Trigger:** "playing with Icon JVM"
**Driver:** `icon_driver -jvm foo.icn -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `icon_driver foo.icn -o foo.asm -run` (x64 ASM backend)

## Subsystems

| Subsystem | ARCH doc | Go there when |
|-----------|----------|---------------|
| Full milestone history | ARCH-icon-jvm.md | reviewing completed work, milestone IDs |
| JCON test analysis | ARCH-icon-jcon.md | understanding rung36 oracle expectations |
| JVM bytecode patterns | ARCH-overview.md | Byrd box → JVM mapping, stack discipline |

---
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`
---

## §BUILD

<<<<<<< HEAD
| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon JVM** | `main` IJ-57 — M-IJ-JCON-HARNESS 🔄 | `14400a9` IJ-57 | M-IJ-JCON-HARNESS |

### IJ-57 progress — M-IJ-JCON-HARNESS (HEAD 14400a9)

**rung01–35: 153/153 PASS. Zero regressions.**

**Work done this session (Stream A — all parse gaps resolved):**
- `icon_lex.c/h`: `++`/`--`/`**` cset ops; `=:=` (`AUGEQ`) and `==:=` (`AUGSEQ`); `.NN` leading-dot float literals
- `icon_parse.c`: `?E` unary random; `+E` unary pos; `{ }` block as primary expr; `if`/`every`/`while`/`until`/`repeat` in expression context; cset binary `++`/`--`/`**`; binary `E!E` list-invoke; `s[i+:n]`/`s[i-:n]` slice forms; scan RHS uses `parse_block_or_expr`; `initial { }` uses `parse_block_or_expr`; forward decl added
- `icon_ast.h`: `ICN_POS` `ICN_RANDOM` `ICN_COMPLEMENT` `ICN_CSET_UNION` `ICN_CSET_DIFF` `ICN_CSET_INTER` `ICN_BANG_BINARY` `ICN_SECTION_PLUS` `ICN_SECTION_MINUS`

**rung36 after IJ-57: 0 pass, 51 fail, 24 xfail — ALL tests now compile and reach JVM**
- Previous: 38 compile errors, only ~13 reached JVM
- Now: 0 compile errors — every non-xfail test generates a `.class` and runs
- Failure mode: `VerifyError: Unable to pop operand off an empty stack` — new AST node kinds hit emitter `default:` branch which emits `goto ω` with no stack value, corrupting surrounding expression stack frames

### CRITICAL NEXT ACTION — IJ-58

**Stream B: Add emit stubs for new node kinds in `icon_emit_jvm.c`**

New node kinds with no emit handler (cause VerifyError):
1. `ICN_POS` — unary `+E` → identity: emit child, same stack shape as `ICN_NEG`
2. `ICN_RANDOM` — unary `?E` → call `icn_builtin_random(val)J` (add to runtime)
3. `ICN_COMPLEMENT` — unary `~E` → call `icn_builtin_cset_complement` (stub → fail ok)
4. `ICN_CSET_UNION` / `ICN_CSET_DIFF` / `ICN_CSET_INTER` — binary cset ops → stubs
5. `ICN_BANG_BINARY` — `E1 ! E2` list-invoke → generate elements of E2, invoke E1 on each
6. `ICN_SECTION_PLUS` — `s[i+:n]` → compute `hi = i + n`, emit as `ICN_SECTION(s, i, hi)`
7. `ICN_SECTION_MINUS` — `s[i-:n]` → compute `lo = i - n`, emit as `ICN_SECTION(s, lo, i)`

**Then fix Stream B content bugs (same list as before, now reachable):**
- `image(&null)` returns `0` not `"&null"` — t03, t32
- `center(s,n)` off-by-one — t07
- `trim(s)`/`image()` quoting — t08
- `next` inside nested `every`/`if` — t01 (primes empty)
- `level()` recursive depth — t10

**Bootstrap IJ-58:**
=======
>>>>>>> ad7a4abb3dc12790abbb08ff7386c5c42d9567cf
```bash
cd snobol4x
gcc -Wall -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
gcc -O2 -o /tmp/icon_semicolon src/frontend/icon/icon_semicolon.c
<<<<<<< HEAD
# Confirm rung01-35 clean:
for s in test/frontend/icon/run_rung*.sh; do bash $s /tmp/icon_driver 2>/dev/null; done | grep -E "^---"
# Run rung36:
bash test/frontend/icon/run_rung36.sh /tmp/icon_driver /tmp/icon_semicolon 2>/dev/null | grep -v "^XFAIL"
# Expected: 0 pass, 51 fail — all compile, all get VerifyError or wrong output
# Start: add emit stubs for ICN_POS/RANDOM/COMPLEMENT/CSET_*/BANG_BINARY/SECTION_PLUS/MINUS
```


## §BUILD
```bash
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x && gcc -Wall -Wextra -g -O0 -I. src/frontend/icon/icon_driver.c \
    src/frontend/icon/icon_lex.c src/frontend/icon/icon_parse.c \
    src/frontend/icon/icon_ast.c src/frontend/icon/icon_emit.c \
    src/frontend/icon/icon_emit_jvm.c src/frontend/icon/icon_runtime.c \
    -o /tmp/icon_driver
=======
>>>>>>> ad7a4abb3dc12790abbb08ff7386c5c42d9567cf
```

## §TEST

```bash
# Full corpus (rungs 01-35):
for s in test/frontend/icon/run_rung*.sh; do bash $s /tmp/icon_driver 2>/dev/null; done | grep -E "^---"
# rung36 JCON:
bash test/frontend/icon/run_rung36.sh /tmp/icon_driver /tmp/icon_semicolon 2>/dev/null | grep -E "^PASS|^---"
# Single rung:
bash test/frontend/icon/run_rung_jvm.sh /tmp/icon_driver 23
```

## Key Files

| File | Role |
|------|------|
| `src/frontend/icon/icon_emit_jvm.c` | JVM emitter — main work file |
| `src/frontend/icon/icon_emit.c` | x64 ASM emitter — Byrd-box logic oracle |
| `src/frontend/icon/icon_driver.c` | `-jvm` flag → `ij_emit_file()` branch |
| `src/backend/jvm/jasmin.jar` | Assembler |
| `test/frontend/icon/corpus/` | `.icn` tests |

---

## §NOW — IJ-56

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon JVM** | IJ-56 — M-IJ-JCON-HARNESS 🔄 | `52e575c` | M-IJ-JCON-HARNESS |

**rung01–35: 153/153 PASS.**

### NEXT ACTION — M-IJ-JCON-HARNESS

**Goal:** All non-xfail rung36 tests PASS (t01–t52). Currently 0/51.

**Stream A — Parse gaps (38 CE):**
1. `if/then/else` without braces multi-line — t25, t32, t44, t47
2. `++` cset union op — t38, t39, t43, t44
3. `=:=` swap-assign op — t34, t21
4. `!expr` as function argument — t02, t52
5. `initial { block }` — t27
6. `s[i+:n]` / `s[i-:n]` slice forms — t22
7. `?E` in expression position — t16, t17
8. Block `do { }` in certain positions — t27, t50, t51

**Stream B — Backend bugs (13 compile, wrong output):**
- `image(&null)` returns `0` not `&null` — t03, t32
- `center(s,n)` off by one — t07
- `primes` empty output — `next` inside nested `every`/`if` — t01
- `level()` empty — recursive depth tracking — t10

**SD-27 blocker (list subscript VerifyError):**
- `vals[i]` → `Bad type in putfield/putstatic` in `icon_emit_jvm.c`
- Minimal repro: `vals := [10,5,1]; i := 1; write(vals[i]);`
- Fix in: `ij_emit_subscript()` — list subscript path (not string, not table)
- Blocks: M-SD-3 roman demo

