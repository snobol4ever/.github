# SCRIP_DEMO.md — Polyglot Proof of Concept

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
| **Scrip Demo** | SD-7 ✅ — String-valued table subscript ClassCastException resolved. 7 fixes in `icon_emit_jvm.c`: dflt-type tracking, prepass registration, `ij_expr_is_string` ICN_SUBSCRIPT, ts_got/null checkcast, drelay String boxing, k_relay String keys, stray putstatic. rung35 2/2 PASS; rung28-34 35/35. | `bc686de` SD-7 | M-SCRIP-DEMO |

### CRITICAL NEXT ACTION (SD-8)

**Next blocker: Build `family_icon.icn` and verify end-to-end Scrip demo pipeline.**

Now that String-valued tables work, the Icon side of the family tree demo can proceed. SD-8 tasks:
1. Compile `family_icon.icn` with `icon_driver -jvm` — expected: clean `.j` output
2. Run the full `run_demo.sh` pipeline (scrip_split → compile × 3 → inject_linkage → jasmin → java)
3. Diff output against `family.expected`
4. Fix any remaining issues in cross-language call emission (`ij_emit_call` dot-notation path)

**Bootstrap SD-8:**
```bash
cd /home/claude/snobol4x
gcc -Wall -Wno-unused-function -g -O0 -I src/frontend/icon \
    src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver_jvm
ln -sf /tmp/icon_driver_jvm /tmp/icon_driver
# Check if demo files exist:
ls demo/scrip/
# If not: create family.scrip, family.csv, family.expected per SCRIP_DEMO.md spec
```

**File:** `snobol4x/src/frontend/icon/icon_emit_jvm.c` — `ij_emit_subscript` table path, around `ts_got` label (after `ij_emit_subscript` line ~5020–5035).

**Bootstrap SD-7:**
```bash
cd /home/claude && git clone https://TOKEN@github.com/snobol4ever/snobol4x
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y default-jdk
cd snobol4x && gcc -Wall -g -O0 -I src/frontend/icon \
    src/frontend/icon/icon_driver.c src/frontend/icon/icon_lex.c \
    src/frontend/icon/icon_parse.c src/frontend/icon/icon_ast.c \
    src/frontend/icon/icon_emit.c src/frontend/icon/icon_emit_jvm.c \
    src/frontend/icon/icon_runtime.c -o /tmp/icon_driver_jvm
# Verify rung28-30: 15/15
# Apply ts_got String fix
# Test: java -cp /tmp/td_test Td3 should print hello|world without exception
# Then test family_icon.icn
```---

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
family.scrip
│
├── ```Prolog   ──► sno2c -pl -jvm  ──► FamilyProlog.j  ──► FamilyProlog.class
├── ```SNOBOL4  ──► sno2c -jvm      ──► FamilySnobol4.j ──► FamilySnobol4.class
└── ```Icon     ──► icon_driver -jvm ──► FamilyIcon.j    ──► FamilyIcon.class
                                              │
                                   ScripFamily.j  (hand-written, ~40 lines)
                                   java ScripFamily
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

`scrip_split.py` (~50 lines of Python). Reads triple-backtick fences,
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
    const char *classname = scrip_class_for_lang(lang);
    fprintf(out,
        "    invokestatic %s/%s(Ljava/lang/String;)Ljava/lang/String;\n",
        classname, method);
    return;
}
```

`scrip_class_for_lang("Snobol4")` → `"FamilySnobol4"`,
`scrip_class_for_lang("Prolog")` → `"FamilyProlog"`.

Everything else in Phase 3 is stub methods hand-inserted into the generated
`.j` files by `inject_linkage.py`:

- `FamilySnobol4.j`: add `parse_csv(String)String` public static entry point
- `FamilyProlog.j`: add `assert_person`, `assert_parent`, `query_pairs`,
  `query_generations`, `query_ancestors` public static entry points
- The Prolog backtracking loop in `query_*` methods accumulates results into
  a `StringBuilder` across retry cycles — this is the one genuinely new piece

### Phase 4 — Driver + Assembly + Run (1 hour)

`ScripFamily.j` (~40 lines Jasmin):

```jasmin
.class public ScripFamily
.super java/lang/Object
.method public static main([Ljava/lang/String;)V
    .limit stack 4
    .limit locals 1
    invokestatic FamilyProlog/scrip_init()V
    invokestatic FamilySnobol4/scrip_init()V
    invokestatic FamilyIcon/icn_main()V
    return
.end method
.end class
```

```bash
java -jar jasmin.jar FamilyProlog.j FamilySnobol4.j FamilyIcon.j ScripFamily.j -d /tmp/classes
java -cp /tmp/classes ScripFamily
```

### Phase 5 — Build Script (30 minutes)

`run_demo.sh` — fully automated:

```bash
#!/bin/bash
set -e
DEMO=demo/scrip
TMP=/tmp/scrip_demo
mkdir -p $TMP
python3 $DEMO/scrip_split.py $DEMO/family.scrip $TMP
./sno2c -pl -jvm  $TMP/prolog.pro    -o $TMP/FamilyProlog.j
./sno2c -jvm      $TMP/snobol4.sno   -o $TMP/FamilySnobol4.j
./icon_driver -jvm $TMP/icon.icn     -o $TMP/FamilyIcon.j
python3 $DEMO/inject_linkage.py $TMP
cp $DEMO/ScripFamily.j $TMP/
java -jar src/backend/jvm/jasmin.jar $TMP/*.j -d $TMP/classes
java -cp $TMP/classes ScripFamily
```

---

## Milestone

**M-SCRIP-DEMO** fires when:

1. `demo/scrip/family.scrip` exists in `snobol4x`
2. `run_demo.sh` runs clean from a fresh clone
3. Output matches `family.expected` (diff clean)
4. Session note written to `SESSIONS_ARCHIVE.md`

---

## Files to Create

| File | Location | What |
|------|----------|------|
| `family.scrip` | `snobol4x/demo/scrip/` | Fenced polyglot source |
| `family.csv` | `snobol4x/demo/scrip/` | Input data (9 rows) |
| `family.expected` | `snobol4x/demo/scrip/` | Expected output (for CI) |
| `run_demo.sh` | `snobol4x/demo/scrip/` | End-to-end build + run |
| `scrip_split.py` | `snobol4x/demo/scrip/` | Fence splitter |
| `inject_linkage.py` | `snobol4x/demo/scrip/` | Stub injector into .j files |
| `ScripFamily.j` | `snobol4x/demo/scrip/` | Hand-written driver class |
| `README.md` | `snobol4x/demo/scrip/` | Explains the demo |

All in `snobol4x`. No new repos. No `.github` changes until M-SCRIP-DEMO fires.

---

## What Comes After

1. **Real polyglot parser** — `scrip_split.py` is its seed
2. **Real ABI** — replaces funny linkage; Session B in SCRIP.md
3. **Bidirectional backtracking** — Icon generators resuming into Prolog
4. **Auto-injection** — emitters generate cross-language stubs natively
5. **Code reorganization** — shared runtime across all three JVM emitters
   (next step after M-SCRIP-DEMO fires, per the plan)

---

*This is a one-day sprint document. The demo proves Scrip works.
Everything else builds on that proof.*
