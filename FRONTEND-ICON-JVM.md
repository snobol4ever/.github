# FRONTEND-ICON-JVM.md — Tiny-ICON → JVM Backend (L3)

Icon → JVM backend emitter. The Icon **frontend** (lex → parse → AST) is shared
and lives in `src/frontend/icon/`; this sprint is about `icon_emit_jvm.c` — the
**JVM backend emitter** that consumes the `IcnNode*` AST and emits Jasmin `.j` files,
assembled by `jasmin.jar` into `.class` files. Despite the file's location under
`src/frontend/icon/`, the work here is backend emission, not parsing.

**Session trigger phrase:** `"I'm working on Icon JVM"` — also triggered by `"playing with ICON frontend ... with JVM backend"` or any phrasing that combines Icon with JVM.
**Session prefix:** `IJ` (e.g. IJ-1, IJ-2, IJ-3)
**Driver flag:** `icon_driver -jvm foo.icn -o foo.j` → `java -jar jasmin.jar foo.j -d .` → `java FooClass`
**Oracle:** `icon_driver foo.icn -o foo.asm -run` (the x64 ASM backend, rungs 1–2 known good)

*Session state → this file §NOW. Backend reference → BACKEND-JVM.md.*

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Icon JVM** | `main` IJ-35 — M-IJ-TABLE 4/5; Bug3 key α re-snapshot | `6e41be2` IJ-35 | M-IJ-TABLE |

**⚠ Grand Master Reorg plan published — sessions continue normally. See GRAND_MASTER_REORG.md.**

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
# Full corpus (rungs 01–21, should show 109/109):
bash test/frontend/icon/run_corpus_jvm.sh /tmp/icon_driver
# Single rung quick check:
bash test/frontend/icon/run_rung_jvm.sh /tmp/icon_driver 21
# Oracle diff for one file:
diff <(icon_driver foo.icn -o /tmp/t.asm -run 2>/dev/null) \
     <(icon_driver -jvm foo.icn -o /tmp/t.j && java -jar src/backend/jvm/jasmin.jar /tmp/t.j -d /tmp && java -cp /tmp FooClass 2>/dev/null)
```

### Next session checklist (IJ-34)

```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x
gcc -Wall -Wextra -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
# Confirm 114/114 PASS (rungs 01-22) baseline before touching code
# M-IJ-CORPUS-R22 fires with M-IJ-LISTS already done — 114/114 IS the milestone
# Mark M-IJ-CORPUS-R22 ✅ immediately, then proceed to M-IJ-TABLE
#
# M-IJ-TABLE plan (from FRONTEND-ICON-JVM.md §Tier 1):
#   table(default), t[k] subscript, key/insert/delete/member builtins
#   JVM: HashMap<String,Object>. table(x) constructs with default x.
#   t[k]: ICN_SUBSCRIPT with string key — check map, return value or default.
#   key(t) generator: per-site static index + keySet().toArray().
#   Corpus: test/frontend/icon/corpus/rung23_table/ (5 tests)
```
#
# READ THIS BEFORE CODING — JCON source corrections (from session IJ-32 analysis):
#
# 1. list(n,x) MUST create n copies of x (not empty list).
#    JCON fList.java: vList.New(i, b.Deref()) — n elements all initialized to x.
#    Impl: eval n→int, eval x→box, loop n times calling ArrayList.add(boxed_x).
#
# 2. Unboxing on get/pop/pull: use ij_expr_is_string/ij_expr_is_real inference on
#    the list's declared static type to choose the right unbox:
#      long:   checkcast java/lang/Long;   invokevirtual Long/longValue()J
#      String: checkcast java/lang/String  (no unbox, already String ref)
#      double: checkcast java/lang/Double; invokevirtual Double/doubleValue()D
#    Per-site statics table type tag 'L' marks the field as ArrayList.
#    Track element type separately: new tag 'LE'=long-list, 'LS'=string-list.
#    OR simpler: at ij_emit_call get/pop/pull site, look up the list var's elem type
#    from a separate ij_list_elem_types[name] → 'J'/'A'/'D' map populated at push/put.
#
# 3. !L bang list branch: use per-site icn_N_bang_idx I static (same as string bang
#    but calling ArrayList.size() for bounds and ArrayList.get(idx) + unbox for value).
#    JCON uses vClosure heap object; we use static index — functionally equivalent.
#
# 4. *L size list branch: detect list operand via statics type 'L';
#    call ArrayList.size()I → i2l → long at ports.γ.
#
# Complete M-IJ-LISTS:
#   Step 1 — List builtins in ij_emit_call (before "user procedure call" ~line 1223):
#     push(L,v): load L; box v; invokevirtual ArrayList/add(0,Object)V; reload L → γ
#     put(L,v):  load L; box v; invokevirtual ArrayList/add(Object)Z; pop; reload L → γ
#     get(L)/pop(L): load L; size==0→ω; remove(0) → unbox → γ
#     pull(L): load L; size==0→ω; remove(size-1) → unbox → γ
#     list(n,x): eval n→int; eval x→box; new ArrayList; loop add → γ
#   Step 2 — ij_emit_bang list branch (after string branch)
#   Step 3 — ij_emit_size list branch
#   Step 4 — rung22_lists corpus (5 tests):
#     t01: L:=[1,2,3]; every write(!L)       → 1\n2\n3
#     t02: L:=[]; push(L,10); push(L,20); write(*L)  → 2
#     t03: L:=[5,6,7]; write(get(L)); write(get(L))   → 5\n6
#     t04: L:=[1,2,3]; write(pull(L))        → 3
#     t05: L:=[]; put(L,4); put(L,5); put(L,6); every write(!L) → 4\n5\n6
#   Step 5 — build, confirm 114/114, commit, push → M-IJ-LISTS ✅
```


### IJ-35 findings — M-IJ-TABLE 4/5 (HEAD 6e41be2)

**114/114 PASS baseline preserved. rung23: t01✅ t02✅ t03✅ t04✅ t05❌**

**Bug 1 FIXED — `t[k] := v` VerifyError:** Early-exit at top of `ij_emit_assign` before any generic emit. Detects `ICN_ASSIGN(ICN_SUBSCRIPT(T,k), v)`, handles as one clean chain: eval v → `v_relay` → box+save; eval k → `k_relay` → `Long.toString`+save; load T+k_str+val_obj → `HashMap.put`; pop; load `val_long` → γ.

**Bug 2 FIXED — `table(dflt)` default value:** Naming convention `{varfld}_dflt`. Pre-pass declares `{fld}_dflt` as Object static for `ASSIGN(VAR, CALL("table",...))`. `table()` emitter sets `ij_pending_tdflt`. Assign table store emits JVM copy `icn_N_tdflt` → `{varfld}_dflt`. Subscript null-branch loads `{varfld}_dflt` by appending `_dflt` to table var field name.

**Also fixed:** `ij_expr_is_table` ICN_CALL now includes `insert`/`delete` — fixes `pop2`→`pop` drain VerifyError for their table return values.

**Bug 3 REMAINS — `key(T)` α re-snapshot (t05):** `key(T)` generator's α port goes to `ktr` (full init: snapshot keySet, reset kidx=0) on every `every`-loop resume. Fix for IJ-36: add `icn_N_kinit I` static. α checks kinit, if set jumps to `kchk` directly. `ktr` sets kinit=1 after init.

**IJ-36 session checklist:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x
gcc -Wall -Wextra -g -O0 -I. src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver
# Confirm rung23 4/5 baseline (t01-t04 PASS, t05 FAIL)
# Fix key(T) α re-snapshot:
#   grep -n "ktr\|kchk\|kidx\|karr\|ktbl\|kinit" src/frontend/icon/icon_emit_jvm.c
#   In key(T) emitter: add icn_N_kinit I static
#   α port: getstatic kinit; ifne kchk  (skip re-snapshot if already init'd)
#   ktr entry: iconst_1; putstatic kinit  (mark init done)
# Build → rung23 5/5 → total 119/119 → M-IJ-TABLE ✅
# Commit "IJ-36: M-IJ-TABLE ✅ — 119/119 PASS"
# Update PLAN.md NOW, FRONTEND-ICON-JVM.md §NOW, SESSIONS_ARCHIVE.md
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

---

## Tiny-Icon Enhancement Roadmap — JCON/Icon Gap Closure

**What we have (IJ-27 baseline, 94/94 PASS, rungs 01–18):**
All arithmetic, string ops, scanning (`?`), csets, generators (`every`/`suspend`/
`fail`/`return`), control flow (`if`/`while`/`until`/`repeat`/`break`/`next`),
alternation (`|`), limitation (`\`), augmented ops, `!E` bang generator,
string relops, real arithmetic + relops, `*s` size, subscript `s[i]`,
`write`/`find`/`match`/`tab`/`move`/`any`/`many`/`upto` builtins.

**What JCON and real Icon have that we don't (the gap):**

From the AST nodes present but not yet JVM-emitted:
`ICN_RECORD`/`ICN_FIELD`, `ICN_GLOBAL`, `ICN_CREATE` (co-expressions),
`ICN_CASE`, `ICN_POW`, `ICN_SCAN_AUGOP` (`s ?:= pat`), `ICN_SEQ_EXPR`.

From real Icon builtins not yet implemented:
`list/push/pop/put/get/pull`, `table`, `set/insert/delete/member`,
`sort/sortf`, `key`, `type`, `copy`, `image`, `char/ord`,
`left/right/center/repl/reverse/trim/map`,
`string/integer/real` (already partial), `read`, math builtins.

From JCON IR nodes we have no equivalent for:
`ir_Create`/`ir_CoRet`/`ir_CoFail` — co-expressions.
`ir_ScanSwap` — scanning augmented assignment (`s ?:= expr`).
`ir_MakeList` — list constructor `[a,b,c]`.

---

### Tier 1 — High Impact (unblock real Icon programs immediately)

#### M-IJ-LISTS
**Feature:** `list/1` constructor, `push/put/get/pop/pull`, list literal `[a,b,c]`
(`ICN_MakeList`), `*L` size of list.
**Why first:** Lists are the primary Icon data structure alongside strings.
Almost every non-trivial Icon program uses lists. `ICN_MakeList` is the list
literal `[e1,e2,e3]` — maps to a JVM ArrayList. `push`/`put` add to front/back,
`get`/`pop`/`pull` remove from front/back. `!L` (bang generator) already works
for strings — extend to lists.
**Impl:** JVM `ArrayList<Object>` as the list representation. Static field per
list variable. `ICN_MakeList` emits ArrayList construction + adds.
Extend `ij_emit_bang` to handle list operands (iterate index 0..size-1).
**Rung:** `rung19_lists/` — construct, push/put, iterate with `!`, size, get/pop.
**Sprint:** 1–2 sessions.

#### M-IJ-TABLE
**Feature:** `table(default)`, `t[key]` subscript for tables,
`insert/delete/member/key` builtins.
**Why second:** Tables (hash maps) are Icon's dict. Required for word-frequency
programs, symbol tables, any associative data. `key(t)` generates all keys —
natural `every` partner. `member(t,k)` tests membership as a generator (succeeds/
fails). Table subscript reuses `ICN_SUBSCRIPT` but with String key instead of
integer index.
**Impl:** JVM `HashMap<String,Object>`. `table(x)` constructs with default value x.
`t[k]` subscript: check map, return value or default. `key(t)` generates keys via
iterator — per-site static index + `keySet().toArray()`.
**Rung:** `rung20_table/`
**Sprint:** 1 session.

#### M-IJ-RECORD
**Feature:** `record` declarations, field access `r.field` (`ICN_RECORD`/`ICN_FIELD`).
**Why third:** Icon records are user-defined types. Required for any program using
structured data beyond strings/lists/tables. JCON has `ir_Record` and `ir_Field` —
maps cleanly to a JVM inner class with public fields.
**Impl:** Each `record foo(f1,f2,f3)` declaration emits a static inner class
`class foo { Object f1,f2,f3; }`. Field access `r.f1` emits `getfield`/`putfield`.
Constructor `foo(v1,v2,v3)` emits `new foo` + field stores.
**Rung:** `rung21_records/`
**Sprint:** 1 session.

#### M-IJ-GLOBAL
**Feature:** `global` variable declarations (`ICN_GLOBAL`), `initial` clause in
procedures.
**Why fourth:** Programs with multiple procedures that share state need globals.
Without them, every procedure is stateless. `initial` blocks initialize static
state on first call — required for memoization patterns and self-initializing tables.
**Impl:** Globals become static fields on the main class (same as current
variable statics, but shared across all procedures). `ICN_GLOBAL` in the parser
already exists. `initial` block: per-procedure boolean static `proc_N_initialized`
+ branch on first entry.
**Rung:** `rung22_global_initial/`
**Sprint:** 1 session.

---

### Tier 2 — Medium Impact

#### M-IJ-BUILTINS-STR
**Feature:** `left/right/center/repl/reverse/trim/map/char/ord/string`.
String manipulation builtins present in real Icon and JCON, missing from Tiny-Icon.
All are straightforward JVM String operations.
- `repl(s,n)` — repeat string n times (`s.repeat(n)` in Java 11+)
- `reverse(s)` — reverse string (`new StringBuilder(s).reverse()`)
- `left/right/center(s,n,fill)` — pad to width
- `trim(s,cset)` — strip trailing chars in cset
- `map(s,from,to)` — character translation table
- `char(i)` — int to one-char string (`String.valueOf((char)i)`)
- `ord(s)` — first char to int (`s.charAt(0)`)
**Rung:** `rung23_strbuiltins2/`
**Sprint:** 1 session. All additive to builtin dispatch.

#### M-IJ-BUILTINS-TYPE
**Feature:** `type(x)` → type name string, `copy(x)`, `image(x)` → string
representation, `numeric(x)`.
`type` returns `"string"/"integer"/"real"/"list"/"table"/"record"`.
`image` returns a printable representation (useful for debugging).
`copy` does a shallow copy.
**Rung:** `rung24_type_image/`
**Sprint:** 1 session.

#### M-IJ-SORT
**Feature:** `sort(L)`, `sort(T,i)`, `sortf(L,i)`.
Sort a list or table. `sort(T,1)` sorts table by keys, `sort(T,2)` by values.
`sortf(L,i)` sorts list of records by field i.
**Depends on:** M-IJ-LISTS, M-IJ-TABLE.
**Rung:** `rung25_sort/`
**Sprint:** 1 session.

#### M-IJ-POW
**Feature:** `ICN_POW` — exponentiation operator `x^y`.
Maps to `Math.pow()`. Simple arithmetic extension.
**Rung:** extend `rung17_real_arith/` or add `rung17b`.
**Sprint:** 30 minutes. One new case in `ij_emit_binop`.

#### M-IJ-CASE
**Feature:** `case E of { pat: expr; ... }` — `ICN_CASE`.
Icon's `case` is value-based (not pattern matching). Each arm is `value: expr`.
Maps to a series of equality tests with the JCON indirect-goto dispatch pattern.
**Rung:** `rung26_case/`
**Sprint:** 1 session.

#### M-IJ-READ
**Feature:** `read()`, `reads(n)` — read from stdin.
`read()` returns the next line (or fails on EOF — generator behavior).
**Impl:** Wrap `BufferedReader.readLine()`. Failure on null return.
**Rung:** `rung27_io/`
**Sprint:** 1 session.

#### M-IJ-SCAN-AUGOP
**Feature:** `s ?:= expr` — scanning augmented assignment (`ICN_SCAN_AUGOP`).
Scans s, and if expr succeeds, assigns the matched portion back to s.
JCON handles this via `ir_ScanSwap`. Currently `ICN_SCAN` (plain `?`) is emitted
but `?:=` is not.
**Rung:** extend `rung05_scan/` or add `rung05b`.
**Sprint:** 1 session.

---

### Tier 3 — Advanced / Future

#### M-IJ-COEXPR (future, no sprint assigned)
**Feature:** Co-expressions — `create E`, `@C`, `^C`, `activate`.
`ICN_CREATE` is already in the AST enum (marked "intentionally omitted" in a
comment in `icon_ast.h`). JCON has `ir_Create`/`ir_CoRet`/`ir_CoFail`.
Co-expressions are Icon's coroutines — first-class suspended computations that
can be resumed explicitly with `@`. They are the most powerful and distinctive
Icon feature beyond basic generators.
**Why deferred:** Requires JVM thread or continuation infrastructure. Each
co-expression is a separate execution context. Not trivial on JVM — JCON used
JVM threads (one thread per co-expression). The Scripten demos don't require
co-expressions. Revisit after Tier 1+2 complete.
**When ready:** Follow JCON's `ir_Create` model. Each `create E` spawns a JVM
thread that blocks waiting for `@` activation. The `@C` operator sends/receives
values between the current thread and C's thread via a `SynchronousQueue`.

#### M-IJ-MATH
**Feature:** `atan/sin/cos/exp/log/sqrt` — math builtins.
Real Icon has these; maps trivially to `java.lang.Math`. Low priority because
Tiny-Icon already covers the arithmetic needed for the Scripten demos.
**Sprint:** 30 minutes when needed.

#### M-IJ-MULTIFILE
**Feature:** Multi-procedure programs across files, `link` declaration.
Currently each `.icn` file compiles to one self-contained class. `link` would
allow splitting a program across files and linking them. Required for large
Icon programs. Design reference: JCON's `ir_Link` + `linker.icn`.
**Sprint:** 2–3 sessions (significant infrastructure).

---

### Enhancement Milestone Summary

| ID | Feature | Tier | Depends on | Status |
|----|---------|------|-----------|--------|
| **M-IJ-LISTS** | `list`, `push/put/get/pop`, `[a,b,c]` literal, `!L` | 1 | — | ❌ |
| **M-IJ-TABLE** | `table`, `t[k]`, `key/insert/delete/member` | 1 | — | ❌ |
| **M-IJ-RECORD** | `record` decl, `r.field` access | 1 | — | ❌ |
| **M-IJ-GLOBAL** | `global` vars, `initial` clause | 1 | — | ❌ |
| **M-IJ-BUILTINS-STR** | `repl/reverse/left/right/center/trim/map/char/ord` | 2 | — | ❌ |
| **M-IJ-BUILTINS-TYPE** | `type/copy/image/numeric` | 2 | — | ❌ |
| **M-IJ-SORT** | `sort/sortf` | 2 | LISTS+TABLE | ❌ |
| **M-IJ-POW** | `^` exponentiation | 2 | — | ❌ |
| **M-IJ-CASE** | `case E of { ... }` | 2 | — | ❌ |
| **M-IJ-READ** | `read()`, `reads(n)` | 2 | — | ❌ |
| **M-IJ-SCAN-AUGOP** | `s ?:= expr` | 2 | — | ❌ |
| **M-IJ-COEXPR** | `create E`, `@C` co-expressions | 3 | — | 💭 |
| **M-IJ-MATH** | `atan/sin/cos/exp/log/sqrt` | 3 | — | 💭 |
| **M-IJ-MULTIFILE** | `link`, multi-file programs | 3 | — | 💭 |

**Recommended sprint order:**
M-IJ-CORPUS-R19 (corpus catchup) →
M-IJ-LISTS → M-IJ-TABLE → M-IJ-RECORD → M-IJ-GLOBAL →
M-IJ-POW → M-IJ-READ → M-IJ-BUILTINS-STR → M-IJ-BUILTINS-TYPE →
M-IJ-SORT → M-IJ-CASE → M-IJ-SCAN-AUGOP →
M-IJ-COEXPR (when ready) → M-IJ-MATH → M-IJ-MULTIFILE.

**Rung numbering:** Enhancement rungs start at rung19.
`test/frontend/icon/corpus/rung19_lists/` through `rung27_io/`.
Each rung: 5 tests, `.icn` + `.expected`, oracle = ASM backend.

**Co-expression note:** JCON implements co-expressions with one JVM thread per
`create`. This is correct but expensive. A future optimization: implement as
JVM virtual threads (Project Loom, Java 21+) — much cheaper, same semantics.

