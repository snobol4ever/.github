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
| **Icon JVM** | `main` IJ-56 — M-IJ-JCON-HARNESS 🔄 | `708964d` IJ-56 | M-IJ-JCON-HARNESS |

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


**SD-27 blocker (list subscript VerifyError):**
- `vals[i]` → `Bad type in putfield/putstatic` in `icon_emit_jvm.c`
- Minimal repro: `vals := [10,5,1]; i := 1; write(vals[i]);`
- Fix in: `ij_emit_subscript()` — list subscript path (not string, not table)
- Blocks: M-SD-3 roman demo
