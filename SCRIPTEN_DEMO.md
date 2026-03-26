# SCRIPTEN_DEMO.md — Polyglot Proof of Concept

**Goal:** Demonstrate three languages (SNOBOL4, Icon, Prolog) coexisting in one
fenced source file, compiled by a thin driver to three JVM classes, wired together
with "funny linkage" — static method calls across class boundaries — and running
as a single Java program. No real ABI. No real linker. No object files. Just proof
that the idea works end-to-end.

**Target:** One working day. All infrastructure already exists.

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Scripten Demo** | SD-3 WIP — 3 fixes landed (`81b4166`): MAX_STATICS 256→512, AND drain ICN_ALT type guards removed, mixed-ALT pop+lconst_0. VerifyError persists: root cause is VAR type inference ordering — `lo`/`hi` declared `J` because `ij_expr_is_string(VAR)` checks static registry which is populated at emit-time, but AND drain-type query fires before assignment to that var is emitted. Fix: add `ij_prepass_types(root)` pre-pass that walks all ICN_ASSIGN nodes and calls `ij_declare_static_str/dbl` eagerly before `ij_emit_expr`. Minimal reproducer: `(a > b & (lo := b) & (hi := a)) \| ((lo := a) & (hi := b))` — single expression, fails immediately. | `81b4166` SD-3 | M-SCRIPTEN-DEMO |

### CRITICAL NEXT ACTION (SD-4)

**Blocker: VerifyError "Expecting to find long on stack" in `icn_main` — VAR type inference ordering.**

**Root cause (confirmed, minimal reproducer isolated):**
```icon
(a > b & (lo := b) & (hi := a)) | ((lo := a) & (hi := b))
```
Variables `lo` and `hi` are assigned String values, but their static fields are declared as `J` (long). The AND drain-type query for the outer structure calls `ij_expr_is_string(VAR)` which checks `ij_static_types[]` — but that registry is populated at **emit time** when `ij_emit_assign` fires `ij_declare_static_str(fld)`. The drain-type query fires **before** emission, so `hi`/`lo` aren't in the registry yet → default `J` → VerifyError.

**The fix: `ij_prepass_types(IcnNode *root)` pre-pass.**

Add before `ij_emit_expr` is ever called (in the procedure emit entry point). Walk the entire AST and for every `ICN_ASSIGN` node where LHS is `ICN_VAR`, call `ij_declare_static_str/dbl/list/tbl` on the LHS field based on the RHS type — same logic as in `ij_emit_assign` lines 997–1031, but without emitting any bytecode.

```c
static void ij_prepass_types(IcnNode *n) {
    if (!n) return;
    if (n->kind == ICN_ASSIGN && n->nchildren >= 2) {
        IcnNode *lhs = n->children[0];
        IcnNode *rhs = n->children[1];
        if (lhs && lhs->kind == ICN_VAR) {
            char fld[128]; ij_var_field(lhs->val.sval, fld, sizeof fld);
            if (ij_expr_is_string(rhs))     ij_declare_static_str(fld);
            else if (ij_expr_is_list(rhs))  ij_declare_static_list(fld);
            else if (ij_expr_is_table(rhs)) ij_declare_static_table(fld);
            else if (ij_expr_is_real(rhs))  ij_declare_static_dbl(fld);
            else                            ij_declare_static(fld);
        }
    }
    for (int i = 0; i < n->nchildren; i++) ij_prepass_types(n->children[i]);
}
```

Call it from `ij_emit_proc` right before the first `ij_emit_expr` call on the procedure body.

**Why the three prior fixes weren't enough:**
1. `MAX_STATICS 256→512` — fixed silent field truncation ✓
2. AND drain `kind != ICN_ALT` guards removed — fixed drain type for ALT children ✓ (but drain type query still wrong because VAR type wrong)
3. mixed-ALT `pop+lconst_0` — fixed stack for mixed-type ALT relay ✓
4. **This fix** — makes VAR type registry accurate before any type queries fire

**After this fix:** rerun `java -cp /tmp/td Test_dedup` — VerifyError should be gone. Then rebuild family_icon.icn and run the full stub test.

**Files to edit:** `snobol4x/src/frontend/icon/icon_emit_jvm.c` — add `ij_prepass_types` before `ij_emit_proc` calls `ij_emit_expr`.

**Bootstrap SD-3:**
```bash
cd /home/claude && git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x && gcc -Wall -g -O0 -I src/frontend/icon \
    src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver_jvm
# Verify rung28-30 still pass (baseline: 15/15)
# Then tackle the 8 remaining stack-height conflicts
```

**Invariant to maintain:** rung28–30 15/15 PASS throughout SD-3 work.

**Blocker: `"Register pair N/N+1 contains wrong type"` VerifyError in `icn_main`.**

**Root cause:** Comparator relay emit (`lrelay`/`rrelay` pattern in relop/cmp) stores a long into a local slot pair only on one control path. The Java 21 type-inference verifier (class file v45) sees the slot as uninitialised-or-incompatible on the other path.

**Fix (SD-2 step 1):** In `icon_emit_jvm.c`, at `icn_main` method header emit (or at `ij_emit_cmp`/relop entry), emit `lconst_0; lstore N` for every comparator relay slot pair used in the method before any branching occurs. ~5 lines; slot numbers are known at emit time.

**Fix path (SD-2):**
1. Fix register-pair VerifyError in `icon_emit_jvm.c` — zero-init comparator relay slots at method entry.
2. Rebuild `icon_driver_jvm`, recompile `family_icon.icn`, confirm `java ScriptenFamily < family.csv` runs without VerifyError.
3. Verify injected `.j` files contain real `invokestatic` calls (not just `return ""`).
4. Capture actual output, write `demo/scripten/family.expected`.
5. Write `demo/scripten/scripten_split.py`, `demo/scripten/run_demo.sh`, `demo/scripten/README.md`.
6. `run_demo.sh` clean, diff against `family.expected` → commit `SD-2: M-SCRIPTEN-DEMO ✅`.

**Bootstrap SD-2:**
```bash
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/snobol4x
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/.github
apt-get install -y default-jdk nasm libgc-dev
cd snobol4x/src && make -j4
gcc -Wall -Wextra -g -O0 -I src/frontend/icon \
    src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver_jvm
# Fix register-pair VerifyError (see above), then:
./sno2c -jvm        demo/scripten/family_snobol4.sno  -o /tmp/sd/Family_snobol4.j
./sno2c -pl -jvm    demo/scripten/family_prolog.pro    -o /tmp/sd/Family_prolog.j
/tmp/icon_driver_jvm -jvm demo/scripten/family_icon.icn -o /tmp/sd/Family_icon.j
cp demo/scripten/ScriptenFamily.j /tmp/sd/
python3 demo/scripten/inject_linkage.py /tmp/sd/
java -jar src/backend/jvm/jasmin.jar /tmp/sd/*.j -d /tmp/sd/classes
java -cp /tmp/sd/classes ScriptenFamily < demo/scripten/family.csv
```

**Files done (commit c6ef225):**
- `demo/scripten/family.csv` ✅
- `demo/scripten/family_snobol4.sno` ✅ — compiles + assembles clean
- `demo/scripten/family_prolog.pro` ✅ — compiles + assembles clean
- `demo/scripten/family_icon.icn` ✅ — `| (i:=i)` fix applied; compiles + assembles clean
- `demo/scripten/inject_linkage.py` ✅ — filename fix applied; all 3 blocks inject clean
- `demo/scripten/ScriptenFamily.j` ✅ — hand-written driver

**Files still needed:**
- `demo/scripten/scripten_split.py`
- `demo/scripten/run_demo.sh`
- `demo/scripten/family.expected`
- `demo/scripten/README.md`

---

## The Demo Program: Family Tree

A CSV file of family data is read, parsed, stored relationally, and queried.
Each language does exactly what it is best at — and crucially, what the *other*
languages cannot do as cleanly.

### The Input: `family.csv`

```
name,uid,birthyear,gender,parent_uid
Eleanor,U001,1921,F,
George,U002,1923,M,
Margaret,U003,1948,F,U001
Thomas,U004,1950,M,U002
Alice,U005,1975,F,U003
Robert,U006,1977,M,U003
Diana,U007,1978,F,U004
James,U008,2001,M,U005
Sophie,U009,2003,F,U006
```

Four field types: name (alpha), uid (alphanumeric), birthyear (integer),
gender (single char), parent_uid (alphanumeric or empty).

### Expected Output

```
Parsed 8 family members.

=== Grandparent relationships ===
  Eleanor is grandparent of Alice
  Eleanor is grandparent of Robert
  George is grandparent of Diana

=== Siblings ===
  Alice and Robert are siblings

=== Cousins ===
  Alice and Diana are cousins
  Robert and Diana are cousins

=== Generations (root=0) ===
  Eleanor : generation 0
  George  : generation 0
  Margaret: generation 1
  Thomas  : generation 1
  Alice   : generation 2
  Robert  : generation 2
  Diana   : generation 2
  James   : generation 3
  Sophie  : generation 3

=== Ancestors of James (U008) ===
  Alice (generation 2)
  Margaret (generation 1)
  Eleanor (generation 0)
```

**Why a dict cannot do this:** A dict answers "who is Alice's parent?" — one hop,
hardcoded. Prolog's `ancestor/2` rule answers "who are all of James's ancestors,
transitively, to any depth?" in two lines of inference rules. No hand-written
traversal. No visited set. No queue. The relational query *is* the algorithm.

---

## Top-Level Three-Way Breakout

### SNOBOL4 — The File Consumer

SNOBOL4's job: one wholesale pass through the CSV file using named structural
patterns. This is SNOBOL4's core strength — not character-by-character parsing,
not `split(",")`, but a structural description of the data that *is* the parser.

Four named lexical patterns cover all field types:

```snobol4
PAT_NAME   = SPAN(&UCASE &LCASE)              * alphabetic name
PAT_UID    = SPAN(&UCASE &LCASE '0123456789') * alphanumeric id
PAT_YEAR   = SPAN('0123456789')               * birth year
PAT_GENDER = ANY('MF')                        * single char
PAT_EMPTY  = POS(0) RPOS(0)                  * missing parent_uid
```

One composite row pattern concatenates them:

```snobol4
PAT_ROW = PAT_NAME   . F_NAME   ','
          PAT_UID    . F_UID    ','
          PAT_YEAR   . F_YEAR   ','
          PAT_GENDER . F_GENDER ','
          (PAT_UID | PAT_EMPTY) . F_PARENT
```

One loop reads the file. Per row it calls across to Prolog to assert facts.
SNOBOL4 never touches the relational logic — it just parses and hands off.

### Prolog — The Relational Engine

Prolog's job: receive asserted facts from SNOBOL4, then answer relational queries
that no array or dict could answer without hand-written traversal code.

The dynamic database:

```prolog
:- dynamic person/4.   % person(Name, UID, BirthYear, Gender)
:- dynamic parent/2.   % parent(ChildUID, ParentUID)
```

Populated at runtime via `assertz`. The inference rules — the payoff — are tiny:

```prolog
grandparent(GP, GC) :- parent(GC, P), parent(P, GP).

ancestor(A, D) :- parent(D, A).
ancestor(A, D) :- parent(D, P), ancestor(A, P).

sibling(X, Y) :- parent(X, P), parent(Y, P), X \= Y.

cousin(X, Y)  :- parent(X, PX), parent(Y, PY), sibling(PX, PY).

generation(UID, 0) :- \+ parent(UID, _).
generation(UID, G) :- parent(UID, P), generation(P, PG), G is PG + 1.
```

Transitive ancestor lookup across arbitrary depth: two lines. Cousin detection
through sibling inference: three lines. This is the demonstration that relational
data belongs in Prolog, not in a table or dict.

### Icon — The Report Generator

Icon's job: iterate over Prolog's multi-valued solution sets using generator
pipelines, then format and emit the report. Icon's `every`/`suspend`/`fail` model
is the natural bridge between Prolog's backtracking answer sets and formatted output.

```icon
every pair := Prolog.query_pairs("grandparent") do
    write("  " || pair)

every entry := Prolog.query_generations() do
    write("  " || entry)

every name := Prolog.query_ancestors("U008") do
    write("  " || name)
```

Neither SNOBOL4 nor Prolog has a clean idiom for "pull results lazily, format
each one, stop when the query is exhausted." Icon does. That is `every`. The
Icon block is the report engine — it owns output, formatting, and result iteration.

### The Data Flow

```
family.csv
    │
    ▼  SNOBOL4: 4 named patterns, one-pass file consumer
    │  PAT_NAME / PAT_UID / PAT_YEAR / PAT_GENDER / PAT_ROW
    │
    ├──► assertz(person(eleanor, u001, 1921, f))   ─┐
    ├──► assertz(person(george,  u002, 1923, m))   ─┤
    ├──► assertz(parent(u003, u001))               ─┤► Prolog dynamic DB
    └──► assertz(parent(u005, u003))               ─┘
                │
                ▼  Prolog: inference rules over dynamic facts
                │  grandparent/2  ancestor/2  sibling/2
                │  cousin/2       generation/2
                │
                ▼  Icon: generator pipelines over solution sets
                   every result := Prolog.query_X() do ...
                   Formatted report to stdout
```

---

## Architecture: Funny Linkage

### What Each Block Compiles To

```
family.scripten
│
├── ```Prolog   ──► sno2c -pl -jvm  ──► FamilyProlog.j  ──► FamilyProlog.class
├── ```SNOBOL4  ──► sno2c -jvm      ──► FamilySnobol4.j ──► FamilySnobol4.class
└── ```Icon     ──► icon_driver -jvm ──► FamilyIcon.j    ──► FamilyIcon.class
                                              │
                                   ScriptenFamily.j  (hand-written, ~40 lines)
                                   java ScriptenFamily
```

### Cross-Language Call Table

| Caller | Callee | Method | What |
|--------|--------|--------|------|
| Icon | SNOBOL4 | `parse_csv(String)String` | parse file → row count |
| SNOBOL4 (per row) | Prolog | `assert_person(String)V` | assertz person fact |
| SNOBOL4 (per row) | Prolog | `assert_parent(String,String)V` | assertz parent link |
| Icon | Prolog | `query_pairs(String)String` | grandparent/sibling/cousin results |
| Icon | Prolog | `query_generations()String` | all generation entries |
| Icon | Prolog | `query_ancestors(String)String` | ancestor chain for one UID |

**Currency:** `java/lang/String` throughout. Pipe-delimited for multi-field values.
Multiple Prolog results are newline-delimited; Icon's `split_lines()` generator
converts them to an `every`-iterable sequence. All three JVM emitters already use
String as their primary inter-operation type — no new marshaling layer needed.

---

## Implementation Plan: One Day

### Phase 1 — Splitter (1 hour)

`scripten_split.py` (~50 lines of Python). Reads triple-backtick fences,
writes each block to a named temp file, emits a manifest.

```python
fence_open  = re.compile(r'^```(\w+)\s*$')
fence_close = re.compile(r'^```\s*$')
# State machine: outside | inside(lang)
# Write block lines to lang-named temp files
# Emit manifest: lang, classname, filename
```

### Phase 2 — Per-Language Compilation (1 hour)

```bash
sno2c -pl -jvm demo_prolog.pro    -o /tmp/FamilyProlog.j
sno2c -jvm     demo_snobol4.sno   -o /tmp/FamilySnobol4.j
icon_driver -jvm demo_icon.icn    -o /tmp/FamilyIcon.j
```

Confirm each `.j` assembles and runs independently with stub inputs
before touching anything.

### Phase 3 — Funny Linkage Injection (3 hours)

**The only new compiler code** — ~20 lines in `icon_emit_jvm.c`:

```c
/* In ij_emit_call(): detect cross-language calls by dot notation */
if (strchr(fname, '.') != NULL) {
    char *dot = strchr(fname, '.');
    char lang[32], method[64];
    strncpy(lang, fname, dot - fname);
    lang[dot - fname] = '\0';
    strcpy(method, dot + 1);
    const char *classname = scripten_class_for_lang(lang);
    fprintf(out,
        "    invokestatic %s/%s(Ljava/lang/String;)Ljava/lang/String;\n",
        classname, method);
    return;
}
```

`scripten_class_for_lang("Snobol4")` → `"FamilySnobol4"`,
`scripten_class_for_lang("Prolog")` → `"FamilyProlog"`.

Everything else in Phase 3 is stub methods hand-inserted into the generated
`.j` files by `inject_linkage.py`:

- `FamilySnobol4.j`: add `parse_csv(String)String` public static entry point
- `FamilyProlog.j`: add `assert_person`, `assert_parent`, `query_pairs`,
  `query_generations`, `query_ancestors` public static entry points
- The Prolog backtracking loop in `query_*` methods accumulates results into
  a `StringBuilder` across retry cycles — this is the one genuinely new piece

### Phase 4 — Driver + Assembly + Run (1 hour)

`ScriptenFamily.j` (~40 lines Jasmin):

```jasmin
.class public ScriptenFamily
.super java/lang/Object
.method public static main([Ljava/lang/String;)V
    .limit stack 4
    .limit locals 1
    invokestatic FamilyProlog/scripten_init()V
    invokestatic FamilySnobol4/scripten_init()V
    invokestatic FamilyIcon/icn_main()V
    return
.end method
.end class
```

```bash
java -jar jasmin.jar FamilyProlog.j FamilySnobol4.j FamilyIcon.j ScriptenFamily.j -d /tmp/classes
java -cp /tmp/classes ScriptenFamily
```

### Phase 5 — Build Script (30 minutes)

`run_demo.sh` — fully automated:

```bash
#!/bin/bash
set -e
DEMO=demo/scripten
TMP=/tmp/scripten_demo
mkdir -p $TMP
python3 $DEMO/scripten_split.py $DEMO/family.scripten $TMP
./sno2c -pl -jvm  $TMP/prolog.pro    -o $TMP/FamilyProlog.j
./sno2c -jvm      $TMP/snobol4.sno   -o $TMP/FamilySnobol4.j
./icon_driver -jvm $TMP/icon.icn     -o $TMP/FamilyIcon.j
python3 $DEMO/inject_linkage.py $TMP
cp $DEMO/ScriptenFamily.j $TMP/
java -jar src/backend/jvm/jasmin.jar $TMP/*.j -d $TMP/classes
java -cp $TMP/classes ScriptenFamily
```

---

## Milestone

**M-SCRIPTEN-DEMO** fires when:

1. `demo/scripten/family.scripten` exists in `snobol4x`
2. `run_demo.sh` runs clean from a fresh clone
3. Output matches `family.expected` (diff clean)
4. Session note written to `SESSIONS_ARCHIVE.md`

---

## Files to Create

| File | Location | What |
|------|----------|------|
| `family.scripten` | `snobol4x/demo/scripten/` | Fenced polyglot source |
| `family.csv` | `snobol4x/demo/scripten/` | Input data (9 rows) |
| `family.expected` | `snobol4x/demo/scripten/` | Expected output (for CI) |
| `run_demo.sh` | `snobol4x/demo/scripten/` | End-to-end build + run |
| `scripten_split.py` | `snobol4x/demo/scripten/` | Fence splitter |
| `inject_linkage.py` | `snobol4x/demo/scripten/` | Stub injector into .j files |
| `ScriptenFamily.j` | `snobol4x/demo/scripten/` | Hand-written driver class |
| `README.md` | `snobol4x/demo/scripten/` | Explains the demo |

All in `snobol4x`. No new repos. No `.github` changes until M-SCRIPTEN-DEMO fires.

---

## What Comes After

1. **Real polyglot parser** — `scripten_split.py` is its seed
2. **Real ABI** — replaces funny linkage; Session B in SCRIPTEN.md
3. **Bidirectional backtracking** — Icon generators resuming into Prolog
4. **Auto-injection** — emitters generate cross-language stubs natively
5. **Code reorganization** — shared runtime across all three JVM emitters
   (next step after M-SCRIPTEN-DEMO fires, per the plan)

---

*This is a one-day sprint document. The demo proves Scripten works.
Everything else builds on that proof.*
