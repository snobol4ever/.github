# ARCH-icon-jvm-history.md — Icon × JVM Milestone History
Operational §NOW → SESSION-icon-jvm.md.
### IJ-44 findings — M-IJ-BUILTINS-MISC ✅ (HEAD fe87efc)

**102/102 PASS (rung05–30). rung30 5/5, 0 xfail.**

**Five builtins in `icon_emit_jvm.c`:**

1. **`abs(x)`** — `Math.abs(J)J` for integer, `Math.abs(D)D` for real. Single-arg, single relay.
2. **`max(x,y,...)`** / **`min(x,y,...)`** — varargs relay chain: emit all arg exprs first, wire with relay labels. `relay[1]` stores arg0 to `tmp` field; each subsequent `relay[i+1]` loads `tmp`, calls `Math.max/min(JJ)J` or `(DD)D`, stores result back to `tmp`; final load after loop. Varargs-safe for N≥2.
3. **`sqrt(x)`** — `l2d` promotion if integer, then `Math.sqrt(D)D`. Always real result.
4. **`seq(i[,j])`** — infinite generator. α: eval start (and optional step), store to `icn_N_seq_cur`/`step` statics, fall to `produce`. β: `cur += step`, fall to `produce`. `produce`: `ij_get_long(cur_fld)` → `ports.γ`. Never reaches `ports.ω`.

**`ij_expr_is_real` extended:** `sqrt` always real; `abs/max/min` real if any arg real.

**Root-cause fixes:** `ij_declare_static_long` → `ij_declare_static`; `ij_put/get_real` → `ij_put/get_dbl`; `ij_declare_static_real` → `ij_declare_static_dbl`.

### IJ-43 findings — M-IJ-BUILTINS-TYPE ✅ (HEAD 495cb65)

**97/97 PASS (rung05–29). rung29 5/5, 0 xfail.**

**Four builtins:** `type(x)` — compile-time pop+`ldc "integer"/"real"/"string"`; `copy(x)` — identity pass-through; `image(x)` — `Long.toString`/`Double.toString`/no-op; `numeric(s)` — `icn_builtin_numeric(String)J` helper with Jasmin `.catch NumberFormatException`, `Long.MIN_VALUE` sentinel → `ports.ω` on failure. `ij_expr_is_string` extended for `type`/`image`/`copy`.

### IJ-38 findings — M-IJ-RECORD-PROCARG ✅ (HEAD 4e09418)

**70/70 PASS (rung05–24). rung24 5/5, 0 xfail.**

**Root cause:** `ij_expr_is_record` only detected direct constructor calls, not VAR nodes holding a record. `ij_emit_call` user-proc path stored all args as `J` (long) into `icn_arg_N`. Callee param-load loaded `J` into `icn_pv_{proc}_{param}` as long.

**Three-part fix in `icon_emit_jvm.c`:**
1. Added `ij_field_type_tag(name)` helper; extended `ij_expr_is_record` to return true for `ICN_VAR` whose static field is `'O'`-typed.
2. **Pass 1c** (new pre-pass): scans all user-proc call sites; for each record arg at position `i`, pre-declares `icn_arg_obj_i` as Object AND pre-declares the callee's param var field as Object (saving/restoring `ij_cur_proc`).
3. **Call site** (`ij_emit_call` user-proc loop): if `ij_expr_is_record(arg)`, pops `lconst_0`, loads `icn_retval_obj`, stores into `icn_arg_obj_N` (Object).
4. **Callee param-load** (non-gen + gen fresh_entry): if `ij_field_type_tag("icn_arg_obj_N") == 'O'`, loads from `icn_arg_obj_N` into Object param field; else long path unchanged.

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
| **M-IJ-TABLE** | `table`, `t[k]`, `key/insert/delete/member` | ✅ |
| **M-IJ-RECORD** | `record` decl, `r.field` access, record proc args | ✅ |
| **M-IJ-STRING-RETVAL** | String procedure returns: `icn_arg_str_N` + Pass 1d fixpoint | ✅ |
| M-IJ-NULL-TEST | `\E` (non-null test) and `/E` (null/failure test) unary ops | ✅ |
| **M-IJ-BLOCK-BODY** | `{ stmt; stmt }` compound body in `while`/`every`/`if` | ✅ |
| M-IJ-GLOBAL | `global` vars, `initial` clause | ✅ |
| M-IJ-POW | `^` exponentiation (int+real) | ✅ |
| M-IJ-READ | `read()`, `reads(n)` | ✅ |
| **M-IJ-BUILTINS-STR** | `repl/reverse/left/right/center/trim/map/char/ord` | ✅ |
| **M-IJ-BUILTINS-TYPE** | `type/copy/image/numeric` | ✅ |
| M-IJ-SORT | `sort/sortf` (depends: LISTS+TABLE) | ✅ |
| M-IJ-ALT-VALUE | ALT relay passes actual values through (not lconst_0 sentinel) | ✅ |
| M-IJ-CASE | `case E of { ... }` | ✅ |
| M-IJ-SCAN-AUGOP | `s ?:= expr` | ✅ |
| **M-IJ-TABLE-VERIFY** | rung23 5/5 — int+str keys, str defaults, member/delete | ✅ |
| M-IJ-RECURSION | Save/restore `icn_pv_*` statics around user proc calls | ✅ |
| M-IJ-INITIAL | `initial` block once-only flag | ✅ |
| M-IJ-STRRET-GEN | β re-pumps last arg for non-gen procs | ✅ |
| **M-IJ-JCON-HARNESS** | rung36 JCON oracle suite: icon_semicolon + all t01–t52 PASS | ❌ **NEXT** |
| M-IJ-COEXPR | `create E`, `@C` co-expressions | 💭 |
| M-IJ-MATH | `atan/sin/cos/exp/log/sqrt` | 💭 |
| M-IJ-MULTIFILE | `link`, multi-file programs | 💭 |

**Sprint order:** TABLE → RECORD → GLOBAL → POW → READ → BUILTINS-STR → BUILTINS-TYPE → SORT → ALT-VALUE → STRING-RETVAL → CASE → NULL-TEST → BLOCK-BODY → SCAN-AUGOP → COEXPR → MATH → MULTIFILE.

---

*FRONTEND-ICON-JVM.md = L4. §NOW = ONE bootstrap block only — current session's next action. Prior session findings → SESSIONS_ARCHIVE.md only. Completed milestones → MILESTONE_ARCHIVE.md. Size target: ≤8KB total.*
