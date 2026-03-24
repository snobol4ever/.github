# FRONTEND-ICON-JVM.md — Tiny-ICON → JVM Backend (L3)

Tiny-ICON frontend targeting JVM bytecode via Jasmin.
Reuses the existing Icon pipeline (lex → parse → AST) unchanged.
New layer: `icon_emit_jvm.c` — consumes `IcnNode*` AST and emits Jasmin `.j` files,
assembled by `jasmin.jar` into `.class` files.

**Session trigger phrase:** `"I'm working on Icon JVM"`
**Session prefix:** `IJ` (e.g. IJ-1, IJ-2, IJ-3)
**Driver flag:** `icon_driver -jvm foo.icn -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `icon_driver foo.icn -o foo.asm -run` (the x64 ASM backend, rungs 1–2 known good)

*Session state → this file §NOW. Backend reference → BACKEND-JVM.md.*

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon JVM** | `main` IJ-4 — Bug1 fix (binop/relop local slots); α/β/γ/ω port names; warnings clean | `254045e` IJ-4 | M-IJ-CORPUS-R2 |

### Next session checklist (IJ-5)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x/src/frontend/icon
gcc -Wall -Wextra -g -O0 -I. icon_driver.c icon_lex.c icon_parse.c icon_ast.c \
    icon_emit.c icon_emit_jvm.c icon_runtime.c -o /tmp/icon_driver
# Read FRONTEND-ICON-JVM.md §NOW
# Run rung01 JVM corpus — pre-existing VerifyError: diagnose write(long) stack issue
# Run rung02 JVM corpus — target 14/14
# Fire M-IJ-CORPUS-R2 when 14/14 pass
```

### IJ-4 findings

**Bug 1 — FIXED in IJ-4 (254045e):** `ij_emit_binop` and `ij_emit_relop` now use
`ij_locals_alloc_tmp()` local slots (`lstore`/`lload`, `istore`/`iload`) instead of
class-global static fields for operand staging. Recursion no longer clobbers operands.

**Port naming — DONE in IJ-4:** All four Byrd Box ports now use Greek letters
throughout source and generated output:
- C identifiers: `IjPorts.γ`/`.ω`, `lbl_α()`/`lbl_β()`, `out_α`/`out_β`, `oα`/`oβ`
- Generated Jasmin labels: `icn_N_α`, `icn_N_β`
- Generated NASM labels: `icon_N_α`, `icon_N_β` (NASM 2.x accepts UTF-8)

**Warnings — FIXED in IJ-4:** Zero warnings with `-Wall -Wextra`. Fixes:
- `ij_jmp_if_ok` removed (unused)
- `buf[128]` → `buf[384]` for classname/field/sig snprintf
- `va[64]/vb[64]` → `va[80]/vb[80]` for `_noval`/`_nvlb` suffixes

**Pre-existing Bug 3 — rung01 JVM VerifyError — OPEN for IJ-5:**
`Unable to pop operand off an empty stack` in `icn_main` for all rung01 tests.
Confirmed pre-existing (present in IJ-3 HEAD before IJ-4 changes).
Root cause: `write(long)` call — the `lstore scratch; getstatic stream; lload scratch;
invokevirtual println(J)V` sequence has a stack accounting error the verifier rejects.
Diagnose by reading the generated `.j` for `t01_to5.icn` and tracing stack depth at
each instruction through the `write` call path.

---


## Key Files

| File | Role |
|------|------|
| `src/frontend/icon/icon_emit_jvm.c` | **TO CREATE** — this sprint's deliverable |
| `src/frontend/icon/icon_emit.c` | x64 ASM emitter — Byrd-box logic oracle (49KB) |
| `src/frontend/icon/icon_driver.c` | Add `-jvm` flag → `ij_emit_file()` branch |
| `src/backend/jvm/emit_byrd_jvm.c` | JVM output format oracle — copy helpers verbatim |
| `src/backend/jvm/jasmin.jar` | Assembler — `java -jar jasmin.jar foo.j -d outdir/` |
| `test/frontend/icon/corpus/` | Same `.icn` tests; oracle = ASM backend output |

---

## Oracle Comparison Strategy

```bash
# ASM oracle
icon_driver foo.icn -o /tmp/foo.asm -run   # produces output via nasm+ld

# JVM candidate
icon_driver -jvm foo.icn -o /tmp/foo.j
java -jar src/backend/jvm/jasmin.jar /tmp/foo.j -d /tmp/
java -cp /tmp/ FooClass

diff <(icon_driver foo.icn -o /tmp/foo.asm -run 2>/dev/null) \
     <(java -cp /tmp/ FooClass 2>/dev/null)
```

Both must produce identical output for each milestone to fire.

---

## Session Bootstrap (every IJ-session)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
make -C snobol4x/src
# Read FRONTEND-ICON-JVM.md §NOW → start at first ❌
```

---

*FRONTEND-ICON-JVM.md = L3. ~3KB sprint content max per active section.*
*Completed milestones → MILESTONE_ARCHIVE.md on session end.*
