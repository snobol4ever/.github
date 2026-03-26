# FRONTEND-ICON-JVM.md — Tiny-ICON → JVM Backend (L4)

Icon → JVM backend emitter. The Icon **frontend** (lex → parse → AST) is shared
and lives in `src/frontend/icon/`; this sprint is about `icon_emit_jvm.c` — the
**JVM backend emitter** that consumes the `IcnNode*` AST and emits Jasmin `.j` files,
assembled by `jasmin.jar` into `.class` files. Despite the file's location under
`src/frontend/icon/`, the work here is backend emission, not parsing.

**Session trigger phrase:** `"I'm working on Icon JVM"` — also triggered by `"playing with ICON frontend ... with JVM backend"` or any phrasing that combines Icon with JVM.
**Session prefix:** `IJ` (e.g. IJ-1, IJ-2, IJ-3)
**Driver flag:** `icon_driver -jvm foo.icn -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `icon_driver foo.icn -o foo.asm -run` (the x64 ASM backend)

*Session state → this file §NOW. Backend reference → BACKEND-JVM.md.*

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon JVM** | `main` IJ-37 — M-IJ-RECORD 4/5 PASS; t03 xfail | `90bd967` IJ-37 | M-IJ-RECORD-PROCARG |

### CRITICAL NEXT ACTION (IJ-38)

**Baseline: 65/65 JVM rungs (rung05–23) PASS. rung24: 4 pass, 0 fail, 1 xfail.**

**THE XFAIL — t03 `sum(q)` where q is a record:** `ij_emit_call` passes record args as `lconst_0` (long). The callee param var (`icn_pv_sum_p`) is declared `J`, not `Ljava/lang/Object;`. Pre-pass only scans `ICN_ASSIGN(VAR, record_call)` — param passing goes through call machinery, not assign.

**Fix:** In `ij_emit_call` user-proc path, after computing each arg: detect if arg is a record type (`ij_expr_is_record`). If so, after emitting the arg (which stores `icn_retval_obj`), store `icn_retval_obj` into the param's Object field (`icn_pv_{proc}_{param}`). Also pre-declare that param field as `O` in a pre-pass or at call-site.

```bash
# Bootstrap IJ-38:
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x
gcc -Wall -Wextra -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
bash test/frontend/icon/run_rung24.sh /tmp/icon_driver   # expect 4/0/1
# Fix t03 → 5/5 → remove xfail → commit "IJ-38: M-IJ-RECORD-PROCARG ✅"
```

**Also note:** `run_rung22.sh` and `run_rung23.sh` had a path bug (`../../..` fix applied in IJ-37, committed). The old scripts used `../..` and always reported 0/0.

---

## §BUILD
```bash
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x && gcc -Wall -Wextra -g -O0 -I. src/frontend/icon/icon_driver.c \
    src/frontend/icon/icon_lex.c src/frontend/icon/icon_parse.c \
    src/frontend/icon/icon_ast.c src/frontend/icon/icon_emit.c \
    src/frontend/icon/icon_emit_jvm.c src/frontend/icon/icon_runtime.c \
    -o /tmp/icon_driver
```

## §TEST
```bash
# Full corpus:
bash test/frontend/icon/run_corpus_jvm.sh /tmp/icon_driver
# Single rung:
bash test/frontend/icon/run_rung_jvm.sh /tmp/icon_driver 23
```

### IJ-36 findings — M-IJ-TABLE ✅ (HEAD 9635570)

**119/119 PASS. rung23 5/5.**

**Two bugs fixed (not one as documented in IJ-35):**

**Bug3a — `kinit` re-snapshot:** Added `icn_N_kinit I` static. `key(T)` α port checks kinit; if non-zero jumps straight to `kchk` (skip re-snapshot). `ktr` sets `kinit=1` after first init.

**Bug3b — table subscript β wiring (new):** `ij_emit_subscript` table path had `JL(b); JGoto(ports.ω)` ("one-shot"). Broke `every total +:= t[key(t)]` because every-pump chain went `gbfwd → augop.β → subscript.β → ports.ω` (exit after 1 key). Fix: `JL(b); JGoto(kb)` — subscript β now resumes idx_child's β (= key generator β).

### Next session checklist (IJ-37)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x
gcc -Wall -Wextra -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
# Confirm 119/119 PASS baseline before touching code
# Next milestone: M-IJ-RECORD (Tier 1)
#   record decl → static inner class with public Object fields
#   r.field access (ICN_FIELD) → getfield/putfield
#   Constructor call foo(v1,v2) → new foo + field stores
#   Corpus: test/frontend/icon/corpus/rung24_records/ (5 tests)
```

### IJ-33 findings — M-IJ-LISTS ✅

**114/114 PASS (rung01–22).** HEAD `51c7335`.

**New in `icon_emit_jvm.c`:**

1. **`ij_expr_is_list()`** — type predicate (forward-declared at line ~381). Handles `ICN_MAKELIST`, `ICN_ASSIGN` with list RHS, `ICN_CALL` for `push`/`put`/`list`, and vars with statics type tag `'L'`.
2. **Pre-pass** — extended forward-scan loop to call `ij_declare_static_list(fld)` for list-typed assignments. Required so `ij_expr_is_list` sees the type during reverse-order emit.
3. **`ij_emit_var`** — detects `is_list`, loads via `ij_get_list_field`.
4. **`ij_emit_assign`** — detects `is_list`, stores/restores via `ij_put/get_list_field`; drains with `pop` not `pop2`.
5. **Statement drain** — `stmt_is_ref = stmt_is_str || stmt_is_list`; uses `pop` for both ref types.
6. **List builtins in `ij_emit_call`**: `push(L,v)`, `put(L,v)`, `get(L)`/`pop(L)`, `pull(L)`, `list(n,x)`.
   - `pull` uses `pull_fail` trampoline to pop the dup'd `size` int before jumping to `ports.ω` (avoids "Inconsistent stack height 0 != 1").
7. **`ij_emit_bang` list branch** — `store`/`chk` labels; iterates by index; unboxes `Long.longValue()J`.
8. **`ij_emit_size` list branch** — `ArrayList.size()I` when child is list.
9. **`ij_expr_is_string(ICN_BANG)`** — returns 0 when child is a list.
10. **rung22 corpus** — 5 tests: `!L`, `push`+`*L`, `get`, `pull`, `put`+`!L`.

### IJ-32 findings — M-IJ-LISTS scaffold (WIP, HEAD ae9e611)

**109/109 PASS baseline preserved.**

Infrastructure in `icon_emit_jvm.c`: type tags `'L'`/`'O'`; `.field` emitter extended; ArrayList + Object field helpers; `ij_emit_makelist` (box+add each child); `ICN_MAKELIST` dispatch. AST+parser: `ICN_MAKELIST` enum + parse rule for `[e1,e2,...]`.

Remaining: list builtins, bang/size list branches, rung22 corpus.



*(IJ-7 through IJ-31 session findings moved to SESSIONS_ARCHIVE.md)*
>>>>>>> 38b5401 (IJ-36: M-IJ-TABLE ✅ — update PLAN.md NOW, FRONTEND-ICON-JVM.md §NOW, milestone+session archive)

## Key Files

| File | Role |
|------|------|
| `src/frontend/icon/icon_emit_jvm.c` | JVM backend emitter (main work file) |
| `src/frontend/icon/icon_emit.c` | x64 ASM emitter — Byrd-box logic oracle |
| `src/frontend/icon/icon_driver.c` | `-jvm` flag → `ij_emit_file()` branch |
| `src/backend/jvm/jasmin.jar` | Assembler — `java -jar jasmin.jar foo.j -d outdir/` |
| `test/frontend/icon/corpus/` | `.icn` tests; oracle = ASM backend output |

---

## Session Bootstrap (every IJ-session)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x
gcc -Wall -Wextra -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
# tail -80 SESSIONS_ARCHIVE.md → find last IJ entry
# Read §NOW above → start at CRITICAL NEXT ACTION
```

---

## Milestone Table

| ID | Feature | Status |
|----|---------|--------|
| M-IJ-SCAFFOLD | `-jvm` flag wired, null.icn → null.j assembles | ✅ |
| M-IJ-HELLO | `write("hello")` → JVM output | ✅ |
| M-IJ-ARITH | Integer arithmetic, relops | ✅ |
| M-IJ-STRINGS | String ops, concatenation | ✅ |
| M-IJ-GENERATORS | `every`/`suspend`/`fail`/`return` | ✅ |
| M-IJ-CONTROL | `if`/`while`/`until`/`repeat`/`break`/`next` | ✅ |
| M-IJ-SCAN | `?` scanning, `find`/`match`/`tab`/`move`/`any`/`many`/`upto` | ✅ |
| M-IJ-CSETS | Cset literals, `&ucase`/`&lcase`/`&digits` | ✅ |
| M-IJ-ALTLIM | Alternation `|`, limitation `\` | ✅ |
| M-IJ-BANG | `!E` bang generator over strings | ✅ |
| M-IJ-REAL | Real arithmetic + relops | ✅ |
| M-IJ-SUBSCRIPT | `s[i]` string subscript, `*s` size | ✅ |
| M-IJ-CORPUS-R18 | 94/94 PASS rungs 01–18 | ✅ |
| M-IJ-LISTS | `list`, `push/put/get/pop/pull`, `[a,b,c]`, `!L` | ✅ |
| M-IJ-CORPUS-R22 | 114/114 PASS rungs 01–22 | ✅ |
| **M-IJ-TABLE** | `table`, `t[k]`, `key/insert/delete/member` | ❌ **NEXT** |
| M-IJ-RECORD | `record` decl, `r.field` access | ❌ |
| M-IJ-GLOBAL | `global` vars, `initial` clause | ❌ |
| M-IJ-BUILTINS-STR | `repl/reverse/left/right/center/trim/map/char/ord` | ❌ |
| M-IJ-BUILTINS-TYPE | `type/copy/image/numeric` | ❌ |
| M-IJ-SORT | `sort/sortf` (depends: LISTS+TABLE) | ❌ |
| M-IJ-POW | `^` exponentiation | ❌ |
| M-IJ-CASE | `case E of { ... }` | ❌ |
| M-IJ-READ | `read()`, `reads(n)` | ❌ |
| M-IJ-SCAN-AUGOP | `s ?:= expr` | ❌ |
| M-IJ-COEXPR | `create E`, `@C` co-expressions | 💭 |
| M-IJ-MATH | `atan/sin/cos/exp/log/sqrt` | 💭 |
| M-IJ-MULTIFILE | `link`, multi-file programs | 💭 |

**Sprint order:** TABLE → RECORD → GLOBAL → POW → READ → BUILTINS-STR → BUILTINS-TYPE → SORT → CASE → SCAN-AUGOP → COEXPR → MATH → MULTIFILE.

---

*FRONTEND-ICON-JVM.md = L4. §NOW = ONE bootstrap block only — current session's next action. Prior session findings → SESSIONS_ARCHIVE.md only. Completed milestones → MILESTONE_ARCHIVE.md. Size target: ≤8KB total.*
