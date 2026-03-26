# SESSION-icon-jvm.md — Icon × JVM (snobol4x)

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

```bash
cd snobol4x
gcc -Wall -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
gcc -O2 -o /tmp/icon_semicolon src/frontend/icon/icon_semicolon.c
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

