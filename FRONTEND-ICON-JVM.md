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
| **Icon JVM** | `main` IJ-3 — pop2 fix at ICN_EVERY gbfwd (Bug 2 partial); Bug 1 diagnosed, not yet fixed; 12/14 rung02 | `5170ebc` IJ-3 | M-IJ-CORPUS-R2 |

### Next session checklist (IJ-4)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x/src/frontend/icon
gcc -Wall -g -O0 -I. icon_driver.c icon_lex.c icon_parse.c icon_ast.c \
    icon_emit.c icon_emit_jvm.c icon_runtime.c -o /tmp/icon_driver
# Read FRONTEND-ICON-JVM.md §NOW
# Fix Bug 1 (t02_fact) in icon_emit_jvm.c — see IJ-3 findings below
# Verify t03_locals now passes after IJ-3 pop2 fix
# Run full corpus: target 14/14 rung02 → fire M-IJ-CORPUS-R2
```

### IJ-3 findings — one fix applied, one bug open for IJ-4

**Bug 2 — t03_locals VerifyError `Inconsistent stack height 4 != 2` — FIXED in IJ-3 (5170ebc):**
Root cause: `ICN_EVERY`'s `gbfwd` label was used as `ports.succeed` for the
generator. Generator (e.g. ICN_TO) pushes a `long` then jumps to `gbfwd`.
`gbfwd` also reachable from zero-stack paths → verifier rejects. Fix applied in
`ij_emit_every`: `JL(gbfwd); JI("pop2",""); JGoto(gb);` — drain before β retry.
Also `bstart` (body entry) now has `pop2` before `JGoto(ba)`.

**Bug 1 — t02_fact recursion gives `1` instead of `120` — OPEN for IJ-4:**
Root cause (CONFIRMED by reading generated .j): `ij_emit_binop` and
`ij_emit_relop` allocate static fields `icn_N_lc`, `icn_N_rc`, `icn_N_bf`
for operand staging. These are class-global. In a recursive call chain like
`fact(5) → fact(4) → ... → fact(0)`, each level's `icn_1_lc`/`icn_1_rc`
fields are clobbered by the deeper call before the outer multiply executes.
Result: all multiplications see the same overwritten values → returns 1.

**Fix for IJ-4 (precise):**
In `ij_emit_binop`, replace the three static-field declarations with local slots:
```c
// REMOVE these three lines:
ij_declare_static(lc_field);
ij_declare_static(rc_field);
ij_declare_static_int(bf_field);

// REPLACE with local slot allocations:
int lc_slot = ij_locals_alloc_tmp();   // long: JVM slots slot_jvm(lc_slot), slot_jvm(lc_slot)+1
int rc_slot = ij_locals_alloc_tmp();   // long
int bf_slot = ij_locals_alloc_tmp();   // used as int — lstore/lload, cast to int as needed
                                        // OR: alloc separately and use istore/iload slot_jvm(bf_slot)
```
Then replace every `ij_put_long(lc_field)` with `J("    lstore %d\n", slot_jvm(lc_slot))`,
`ij_get_long(lc_field)` with `J("    lload %d\n", slot_jvm(lc_slot))`, etc.
For `bf_field` (int): use `J("    istore %d\n", slot_jvm(bf_slot))` /
`J("    iload %d\n", slot_jvm(bf_slot))`.
Apply the same change in `ij_emit_relop` for `lc_field`/`rc_field`.
Note: `ij_locals_alloc_tmp()` increments `ij_nlocals` — call these AFTER params
and locals are registered (they already are, since binop emit happens during body
emit, after proc setup). The `.limit locals` directive already has padding (+10).

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
