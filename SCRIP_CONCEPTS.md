# SCRIP_CONCEPTS.md — Polyglot Proof of Concept Designs

Three concept sketches for advanced SCRIP demos beyond the M-SD-1..10 ladder.
Status: concepts only — not yet scheduled. See SCRIP_DEMOS.md for active ladder.

---

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
cd /home/claude/one4all
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

**File:** `one4all/src/frontend/icon/icon_emit_jvm.c` — `ij_emit_subscript` table path, around `ts_got` label (after `ij_emit_subscript` line ~5020–5035).

**Bootstrap SD-7:**
```bash
cd /home/claude && git clone https://TOKEN@github.com/snobol4ever/one4all
git clone https://TOKEN@github.com/snobol4ever/.github
apt-get install -y default-jdk
cd one4all && gcc -Wall -g -O0 -I src/frontend/icon \
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
├── ```Prolog   ──► scrip-cc -pl -jvm  ──► FamilyProlog.j  ──► FamilyProlog.class
├── ```SNOBOL4  ──► scrip-cc -jvm      ──► FamilySnobol4.j ──► FamilySnobol4.class
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
scrip-cc -pl -jvm demo_prolog.pro    -o /tmp/FamilyProlog.j
scrip-cc -jvm     demo_snobol4.sno   -o /tmp/FamilySnobol4.j
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
./scrip-cc -pl -jvm  $TMP/prolog.pro    -o $TMP/FamilyProlog.j
./scrip-cc -jvm      $TMP/snobol4.sno   -o $TMP/FamilySnobol4.j
./icon_driver -jvm $TMP/icon.icn     -o $TMP/FamilyIcon.j
python3 $DEMO/inject_linkage.py $TMP
cp $DEMO/ScripFamily.j $TMP/
java -jar src/backend/jvm/jasmin.jar $TMP/*.j -d $TMP/classes
java -cp $TMP/classes ScripFamily
```

---

## Milestone

**M-SCRIP-DEMO** fires when:

1. `demo/scrip/family.scrip` exists in `one4all`
2. `run_demo.sh` runs clean from a fresh clone
3. Output matches `family.expected` (diff clean)
4. Session note written to `SESSIONS_ARCHIVE.md`

---

## Files to Create

| File | Location | What |
|------|----------|------|
| `family.scrip` | `one4all/demo/scrip/` | Fenced polyglot source |
| `family.csv` | `one4all/demo/scrip/` | Input data (9 rows) |
| `family.expected` | `one4all/demo/scrip/` | Expected output (for CI) |
| `run_demo.sh` | `one4all/demo/scrip/` | End-to-end build + run |
| `scrip_split.py` | `one4all/demo/scrip/` | Fence splitter |
| `inject_linkage.py` | `one4all/demo/scrip/` | Stub injector into .j files |
| `ScripFamily.j` | `one4all/demo/scrip/` | Hand-written driver class |
| `README.md` | `one4all/demo/scrip/` | Explains the demo |

All in `one4all`. No new repos. No `.github` changes until M-SCRIP-DEMO fires.

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
-e 
---

# SCRIP_DEMO2.md — Puzzle Solver: Polyglot Proof of Concept #2

**Companion to:** SCRIP_DEMO.md (family tree — Demo #1)
**Difficulty:** One step harder. Same funny linkage architecture.
**The inversion:** Prolog does NOT search. Icon searches. Prolog is the constraint oracle.
**Target:** One working day, back-to-back with Demo #1 or standalone.

---

## The Thesis

Every language in Scrip is a **tool**, not a religion.

Prolog does not have to do the search. Icon does not have to be a formatter.
SNOBOL4 does not have to read CSV.

This demo makes that argument in executable form:

- **SNOBOL4** reads a structured puzzle definition in S-expression syntax,
  using a reduced treebank `group()` to build a tree and populate Prolog
  simultaneously — one pattern match, one pass, two things done
- **Prolog** stores clues as dynamic facts and answers one-hop constraint
  queries: "does this person/job assignment violate any clue?" — pure
  fact lookup, zero search, zero inference rules
- **Icon** does the combinatorial search using `suspend` in a recursive
  generator — depth-first assignment search, Prolog as the constraint
  oracle, `every` at the top to collect solutions

The paradigm reversal is the demo. Prolog as a typed constraint store.
Icon as the search engine. SNOBOL4 as the S-expression reader.

---

## The Puzzle

Puzzle 1 from the corpus — the smallest. Three people, three jobs, three clues.

```
Who holds which job?
People:  Brown, Jones, Smith
Jobs:    cashier, manager, teller
Clues:   Jones is not the cashier.
         Smith is not the cashier.
         Smith is not the manager.
```

Answer: Brown=cashier, Jones=manager, Smith=teller.
(Only one assignment satisfies all three constraints.)

---

## The Input: `puzzle1.clues` — S-Expression Format

```lisp
(puzzle bank-positions
  (persons brown jones smith)
  (jobs cashier manager teller)
  (clue jones not cashier)
  (clue smith not cashier)
  (clue smith not manager))
```

Nested. Recursive. Shallow enough to be readable. Deep enough to demonstrate
the treebank pattern technique. Each list is a typed node: `persons`, `jobs`,
`clue`. The structure is uniform — tag followed by atoms — exactly the shape
that `group()` was designed for.

**For Demo #2b (puzzles 2–5):** add more `(clue ...)` lines and extend
`(persons ...)` / `(jobs ...)`. The SNOBOL4 reader, Prolog store, and Icon
search are all data-driven — no code changes for harder puzzles.

---

## Top-Level Three-Way Breakout

### SNOBOL4 — Reduced Treebank Reader

The full treebank uses five functions over `DATA('cell(hd,tl)')` cons-cells:
`do_push_list`, `do_push_item`, `do_pop_list`, `do_pop_final`, and the
recursive `group()`. For the puzzle demo, three functions suffice — and the
third is new and more interesting:

```
do_push_list   — open a new node; tag becomes the node head
do_push_item   — append an atom to the current open node
do_pop_assert  — close the node AND assertz it to Prolog simultaneously
```

`do_pop_assert` is the philosophical heart of the demo. In treebank.sno,
`do_pop_list` builds a generic tree that is walked afterward. Here, closing
a node fires the Prolog assertion immediately, inside the pattern match.
**Tree building and database population happen in one pass, simultaneously,
as a side effect of the pattern consuming the input.**

This is the wholesale pattern philosophy at its most expressive: the pattern
match IS the parser IS the database loader. Nothing happens after the match
completes — it was all done during.

```snobol4
*--- Three functions (reduced from treebank's five) --------------------------

               DATA('cell(hd,tl)')

               DEFINE('do_push_list(v)')                    :(do_push_list_end)
do_push_list   stk          = cell(cell(v,), stk)
               do_push_list = .dummy                        :(NRETURN)
do_push_list_end

               DEFINE('do_push_item(v)')                    :(do_push_item_end)
do_push_item   hd(stk)      = cell(v, hd(stk))
               do_push_item = .dummy                        :(NRETURN)
do_push_item_end

               DEFINE('do_pop_assert()p,n,i,a,tag')         :(do_pop_assert_end)
do_pop_assert  p            = hd(stk)
               n            = 0
dpa_cnt        DIFFER(p)                                    :F(dpa_bld)
               n            = n + 1
               p            = tl(p)                         :(dpa_cnt)
dpa_bld        a            = ARRAY('1:' n)
               p            = hd(stk)
               i            = n + 1
dpa_fill       i            = GT(i,1) i - 1                 :F(dpa_done)
               a[i]         = hd(p)
               p            = tl(p)                         :(dpa_fill)
dpa_done       stk          = tl(stk)
               tag          = a[1]
*              --- assertz to Prolog based on node tag ---
               IDENT(tag, 'persons')                        :F(dpa_jobs)
               dummy        = Prolog.assert_persons(a)      :(dpa_ret)
dpa_jobs       IDENT(tag, 'jobs')                           :F(dpa_clue)
               dummy        = Prolog.assert_jobs(a)         :(dpa_ret)
dpa_clue       IDENT(tag, 'clue')                           :F(dpa_ret)
               dummy        = Prolog.assert_clue(a)
dpa_ret        hd(stk)      = cell(a, hd(stk))
               do_pop_assert = .dummy                       :(NRETURN)
do_pop_assert_end

*--- group() — recursive descent, identical structure to treebank.sno --------
*   Locals tag, wrd give each recursive invocation its own bindings.

               DEFINE('group()tag,wrd')                     :(group_end)
group          buf          POS(0) '(' =                    :F(FRETURN)
               buf          POS(0) word . tag =             :F(FRETURN)
               dummy        = do_push_list(tag)
group_loop     buf          POS(0) SPAN(SPCNL) =            :F(group_close)
               buf          POS(0) '('                      :S(group_recurse)
               buf          POS(0) word . wrd =             :F(group_close)
               dummy        = do_push_item(wrd)             :(group_loop)
group_recurse  group()                                      :S(group_loop)F(FRETURN)
group_close    buf          POS(0) ')' =                    :F(FRETURN)
               dummy        = do_pop_assert()
               group        =                               :(RETURN)
group_end

*--- word pattern (same as treebank.sno) -------------------------------------

               WBRKS        = '( )' NL
               word         = NOTANY(WBRKS) BREAK(WBRKS)

*--- Wholesale single-pattern file consumer (claws5 philosophy) --------------
*   One match on buf consumes the entire puzzle file.
*   All Prolog assertions happen as side effects during the match.

               puzzle_pat  = POS(0)
+                             *do_push_list('puzzle')
+                             ARBNO(
+                                 SPAN(SPCNL)
+                               | '(' group() ')'
+                             )
+                             *do_pop_assert()
+                             RPOS(0)

*--- Main: read file into buf, fire one match --------------------------------

               buf          = ''
               NL           = CHAR(10)
               SPCNL        = ' ' NL
rdloop         line         = INPUT                         :F(scan)
               buf          = buf line NL                   :(rdloop)
scan           buf          puzzle_pat                      :S(END)
               OUTPUT       = '*** parse error'
END
```

**What this demonstrates about SNOBOL4:**
The `NRETURN` zero-advance side-effect function technique (from claws5) combined
with the recursive `group()` descent (from treebank) gives you a parser that
reads an entire structured file in one pattern match, building a tree and
populating a database simultaneously. No separate parse phase. No tree walk.
The pattern IS the pipeline.

### Prolog — Constraint Store (One-Hop Lookup Only)

Prolog's job is deliberately limited to prove the point: it does **not** search,
it does **not** use inference rules, it does **not** backtrack through solution
space. It stores facts and answers constraint queries.

```prolog
:- dynamic person/1.
:- dynamic job/1.
:- dynamic clue/3.    % clue(Person, Relation, Job)

%% Facts are asserted by SNOBOL4 during the parse.
%% No rules. No search. No ancestor/2. No member/2.
%% Just assertz and one-hop lookup.

%% The one query Prolog answers:
%% valid_assign(Person, Job) — true if no clue contradicts this pairing.
valid_assign(Person, Job) :-
    \+ clue(Person, not, Job).
```

That is the entire Prolog program. Four dynamic declarations, one rule.
The rule says: this assignment is valid if there is no `not` clue blocking it.
One `\+` call. One fact lookup. No search.

The point: Prolog is used for what it is actually best at in this context —
typed storage and declarative constraint expression. The search happens elsewhere.

### Icon — The Combinatorial Search Engine

Icon's job: generate all valid complete assignments using nested `every` and
a recursive `suspend` generator. This is the canonical demonstration of Icon's
evaluation model — the thing no other language in the suite does.

```icon
# The search: recursive generator with suspend
procedure try_assign(persons, jobs, idx, partial)
    if idx > *persons then {
        suspend partial    # yield a complete valid assignment
        fail               # force backtrack to find more (or signal exhaustion)
    }
    p := persons[idx]
    every j := !jobs do {
        if Prolog.valid_assign(p, j) &
           not(find(j, partial)) then {    # j not already used
            suspend try_assign(
                persons, jobs,
                idx + 1,
                partial ||| [p || "=" || j]
            )
        }
    }
end

procedure main()
    # Get persons and jobs lists from Prolog store
    persons := split_bar(Prolog.get_persons())   # ["brown","jones","smith"]
    jobs    := split_bar(Prolog.get_jobs())       # ["cashier","manager","teller"]

    write("=== Puzzle: Bank Positions ===")
    count := 0
    every assignment := try_assign(persons, jobs, 1, []) do {
        count +:= 1
        write("Solution " || count || ":")
        every pair := !assignment do
            write("  " || pair)
    }
    if count = 0 then write("No solution found.")
    else if count = 1 then write("Unique solution confirmed.")
    else write(count || " solutions found.")
end
```

**What `suspend` does here:**

`try_assign` is a generator — a procedure that can produce multiple values.
When it reaches a complete valid assignment (`idx > *persons`), it `suspend`s,
yielding the assignment to the caller. The `every` loop in `main` consumes that
value, then re-enters `try_assign` which `fail`s to force backtracking.
Backtracking unwinds through the nested `every j := !jobs` loops,
trying the next job at each level, calling `Prolog.valid_assign` at each step.

The Icon runtime handles all of this. The programmer writes:
```
every assignment := try_assign(...) do write(assignment)
```
and gets depth-first constraint search with automatic backtracking for free.

**The Prolog call inside Icon search:**

`Prolog.valid_assign(p, j)` is a cross-language call that returns `"true"` or
`"false"`. Icon treats a non-empty string as a truthy value — the `&` conjunction
short-circuits if `valid_assign` returns `"false"`, pruning that branch
immediately without going deeper. Prolog cuts the search tree; Icon traverses it.

---

## Expected Output

```
=== Puzzle: Bank Positions ===
Solution 1:
  brown=cashier
  jones=manager
  smith=teller
Unique solution confirmed.
```

For puzzle 3 (larger, multiple solutions exist until all clues applied):
the same Icon search finds them all, reports count. Data-driven — same code.

---

## Architecture: Funny Linkage

### Cross-Language Call Table

| Caller | Callee | Method | What |
|--------|--------|--------|------|
| SNOBOL4 (per node close) | Prolog | `assert_persons(array)V` | assertz person/1 facts |
| SNOBOL4 (per node close) | Prolog | `assert_jobs(array)V` | assertz job/1 facts |
| SNOBOL4 (per node close) | Prolog | `assert_clue(array)V` | assertz clue/3 fact |
| Icon (per candidate pair) | Prolog | `valid_assign(String,String)String` | constraint check → "true"/"false" |
| Icon (once) | Prolog | `get_persons()String` | bar-delimited person list |
| Icon (once) | Prolog | `get_jobs()String` | bar-delimited job list |

**Same funny linkage mechanism as Demo #1.** String currency.
`inject_linkage.py` from Demo #1 extended with these new stub signatures.

### Data Flow

```
puzzle1.clues
    │
    ▼  SNOBOL4: group() recursive descent
    │  one match on buf — wholesale consumption
    │  do_pop_assert fires per node close
    │
    ├──► assertz(person(brown))          ─┐
    ├──► assertz(person(jones))          ─┤
    ├──► assertz(job(cashier))           ─┤► Prolog dynamic DB
    ├──► assertz(clue(jones, not, cashier)) ─┤
    └──► assertz(clue(smith, not, manager)) ─┘
                │
                ▼  Icon: try_assign() recursive suspend generator
                │  every j := !jobs — drive permutation space
                │  Prolog.valid_assign(p,j) — prune at each step
                │  suspend — yield valid complete assignments
                │
                ▼  Output: solution(s) formatted to stdout
```

---

## Implementation Plan: One Day

### Phase 1 — Puzzle input files (30 min)

Write `puzzle1.clues` through `puzzle5.clues` in the S-expression format.
These are the existing puzzles from the Prolog corpus, translated to the
new input format. Puzzle 1 (3×3) is the acceptance test.
Puzzles 2–5 exercise the same code with more persons/jobs/clues.

### Phase 2 — SNOBOL4 reader (2 hours)

The `group()` function is copied almost verbatim from `treebank.sno`.
New work: `do_pop_assert()` — the combined pop-and-assertz function.
This replaces `do_pop_list()` from treebank.
The cross-language calls from `do_pop_assert` use the same
`invokestatic` stub mechanism from Demo #1.

Test standalone: run SNOBOL4 reader with a stub Prolog that just
prints each `assertz` call. Verify all facts extracted correctly.

### Phase 3 — Prolog constraint store (1 hour)

The Prolog block is the simplest of the three. Four `dynamic` declarations,
one `valid_assign` rule. The `assert_*` entry points from funny linkage are
straightforward wrappers — split bar-delimited input, call `assertz`.
`get_persons()` and `get_jobs()` collect all `person/1` and `job/1` facts
into a bar-delimited string for Icon.

Test standalone: assert some facts manually, call `valid_assign` in a loop,
verify correct true/false responses.

### Phase 4 — Icon search (2 hours)

`try_assign` is the centerpiece. Write and test it first against a mock
`valid_assign` that always returns `"true"` — verify it generates all 6
permutations of 3 people into 3 jobs. Then connect to real Prolog and
verify constraint pruning works: with all three clues asserted, only
one solution should survive.

The `suspend` recursive generator is standard Icon — this runs
on the existing Icon JVM emitter with the rung03 `suspend` support
already in place (M-IJ-CORPUS-R3 ✅).

### Phase 5 — Integration + run_demo2.sh (1 hour)

Same structure as `run_demo.sh` from Demo #1:
split → compile three blocks → inject linkage → assemble → run.

Test with puzzle1 (one solution), then puzzle3 (verify multiple
solutions or unique, depending on clue set).

---

## The Two-Demo Arc

Together, Demo #1 and Demo #2 make a complete pedagogical statement:

| | Demo #1: Family Tree | Demo #2: Puzzle Solver |
|---|---|---|
| Input format | CSV (flat) | S-expressions (nested, recursive) |
| SNOBOL4 role | Structural CSV parser, 4 named patterns | Recursive descent reader, treebank technique |
| Prolog role | Dynamic DB + relational inference | Dynamic DB + constraint lookup only |
| Icon role | Generator pipeline over solution sets | Combinatorial search engine with suspend |
| Prolog searches? | Yes — ancestor/2, cousin/2 | **No** — Icon searches |
| Icon searches? | No — formats results | **Yes** — suspend generator |
| Key technique | assertz + inference rules | suspend + backtracking + pruning |
| Difficulty | Entry level | One step harder |

Demo #1 shows what each paradigm does naturally.
Demo #2 shows that the paradigms are **interchangeable tools** —
Prolog can be a store, Icon can be a solver, SNOBOL4 can read anything.

---

## Milestone

**M-SCRIP-DEMO2** fires when:

1. `demo/scrip/puzzle1.clues` (and 2–5) exist in `one4all`
2. `run_demo2.sh` runs clean from a fresh clone
3. Output for puzzle1 matches `puzzle1.expected` (diff clean)
4. Output for puzzle3 is verified against swipl reference
5. Session note written to `SESSIONS_ARCHIVE.md`

**Dependency:** M-SCRIP-DEMO (Demo #1) should fire first —
the splitter, inject_linkage, and funny linkage infrastructure
are shared and only built once.

---

## Files to Create

| File | Location | What |
|------|----------|------|
| `puzzle1.clues` – `puzzle5.clues` | `one4all/demo/scrip/` | S-expression puzzle inputs |
| `puzzle1.expected` – `puzzle5.expected` | `one4all/demo/scrip/` | Expected outputs |
| `family.scrip` → `puzzle1.scrip` | `one4all/demo/scrip/` | Fenced polyglot source |
| `run_demo2.sh` | `one4all/demo/scrip/` | Build + run (reuses Demo #1 infra) |
| `README.md` (update) | `one4all/demo/scrip/` | Add Demo #2 section |

No new repos. No new compiler files beyond the ~20-line Icon cross-call addition
from Demo #1 (already planned). `inject_linkage.py` extended with new stub
signatures for the puzzle entry points.

---

## The One Insight Worth Saying Aloud

The puzzle demo's SNOBOL4 block does something elegant that is worth naming:

`do_pop_assert()` combines tree-close with database-assert in one NRETURN
side-effect function. The pattern match does not produce a tree that is
later walked to extract facts. The pattern match *is* the extraction.
When `group()` closes a node — fires `do_pop_assert` — the facts are
already in Prolog before the next character of the input is consumed.

This is the λ side-effect technique from `claws5.sno` (NRETURN zero-advance
functions as embedded actions) combined with the recursive descent from
`treebank.sno` (mutual reference, `group()` calling itself via `group_recurse`).
Two proven techniques from the existing corpus, composed into something new.

That is Scrip working as designed.

---

*Demo #2 of 2. Together with SCRIP_DEMO.md, these two programs constitute
the proof that Scrip is real. Everything else in SCRIP.md builds on
what these demos establish.*
-e 
---

# SCRIP_DEMO3.md — Tiny Compiler: Polyglot Proof of Concept #3

**Status: CONCEPT — not yet cooked. Capture only. No implementation plan yet.**

**Companion to:** SCRIP_DEMO.md (family tree) · SCRIP_DEMO2.md (puzzle solver)
**Difficulty:** Hardest of the three. Four languages. Three compiler phases. One orchestrator.
**The thesis:** A real compiler — parse → codegen → optimize → format — built from
four languages each owning exactly the phase it is best at.

---

## The Concept

A tiny infix arithmetic expression compiler targeting a simple stack machine:

```
input:   "3 + 4 * (2 - 1)"
output:  PUSH 3
         PUSH 4
         PUSH 2
         PUSH 1
         SUB
         MUL
         ADD
```

Each compiler phase is owned by the language built for it.

---

## The Four-Language Breakdown

### Snocone — Phase 1: Parse

Snocone reads the infix expression string and builds a parse tree.
This is Snocone's core strength: pattern-driven structural decomposition.
Operator precedence handled by named patterns. Output: a flat serialized
tree format (S-expression or pipe-delimited node list) passed to Prolog.

```snocone
expr    := term (('+' | '-') term)*
term    := factor (('*' | '/') factor)*
factor  := '(' expr ')' | number
number  := [0-9]+
```

One pass. No recursion in the host language — the pattern grammar *is* the parser.

### Prolog — Phase 2: Codegen

Prolog takes the serialized parse tree and applies rewrite rules to produce
raw stack instructions. This is exactly what Prolog does best: tree-to-tree
transformation via structural pattern matching on term shapes.

```prolog
compile(num(N),   [push(N)]).
compile(add(L,R), Code) :- compile(L, CL), compile(R, CR), append(CL, CR, [add|Code]).
compile(sub(L,R), Code) :- compile(L, CL), compile(R, CR), append(CL, CR, [sub|Code]).
compile(mul(L,R), Code) :- compile(L, CL), compile(R, CR), append(CL, CR, [mul|Code]).
compile(div(L,R), Code) :- compile(L, CL), compile(R, CR), append(CL, CR, [div|Code]).
```

No search. No backtracking. Pure deterministic tree rewriting.
Output: flat instruction list, newline-delimited, passed to Icon.

### Icon — Phase 3: Optimize + Orchestrate

Icon owns two things:

**Orchestrator:** Icon drives the full pipeline. It calls Snocone to parse,
calls Prolog to compile, runs its own optimizer pass, then calls Snocone
to format. The `every`/`suspend` model makes the pipeline lazy and composable.

**Peephole optimizer:** Icon's generator model is the natural fit for
sliding-window pattern matching over an instruction stream:

```icon
# Constant-fold PUSH a / PUSH b / ADD → PUSH (a+b)
procedure optimize(instrs);
  local i;
  every i := 1 to *instrs - 2 do
    if instrs[i][1:5] == "PUSH " & instrs[i+1][1:5] == "PUSH " &
       instrs[i+2] == "ADD" then {
      suspend "PUSH " || (integer(instrs[i][6:0]) + integer(instrs[i+1][6:0]));
      i +:= 2; next;
    };
    suspend instrs[i];
  suspend instrs[*instrs];
end
```

Sliding window, generator output — exactly what `every`/`suspend` is for.

### Snocone — Phase 4: Format

The same Snocone instance (or a second call) takes the optimized instruction
list and formats it: right-aligns opcodes, pads operands, adds a column header,
optionally adds an address column. Output: human-readable assembly listing.

```
Addr  Instr
----  -----
0000  PUSH 3
0001  PUSH 4
0002  PUSH 2
0003  PUSH 1
0004  SUB
0005  MUL
0006  ADD
```

Snocone's OUTPUT formatting patterns handle alignment without manual padding logic.

---

## Why This Demo Is The Best Argument For Scrip

- Demo 1 (family tree): three languages, data pipeline, each does its specialty
- Demo 2 (puzzle solver): paradigm reversal — Prolog as store, Icon as search
- **Demo 3 (tiny compiler): a real software artifact — a compiler — assembled from parts**

A compiler is the canonical example of a multi-phase pipeline. Every CS student
knows: lex → parse → codegen → optimize → emit. Scrip Demo 3 shows that
each phase can be written in the language that owns it, wired together with funny
linkage, and the result is smaller and clearer than any single-language version.

The optimizer in Icon is ~10 lines. The codegen in Prolog is ~5 rules.
The parser in Snocone is ~5 patterns. The formatter in Snocone is ~3 patterns.
Total: ~25 lines of actual logic. The rest is plumbing — and the plumbing
is what Scrip provides.

---

## What Needs To Be True Before This Can Be Built

- **M-SCRIP-DEMO** ✅ (funny linkage architecture proven)
- **M-SCRIP-DEMO2** ✅ (four-language orchestration proven)
- **Snocone JVM emitter** — Snocone currently has no JVM backend (only x64 ASM)
- **Icon as orchestrator** — needs M-IJ-STRING-RETVAL fix + multi-call sequencing

## Open Design Questions (not yet cooked)

1. **Snocone → JVM:** Does Snocone get a JVM emitter, or does it compile to a
   String-passing interpreter called from Icon via `invokestatic`?
2. **Parse tree serialization format:** S-expression? Pipe-delimited? JSON?
   Must be something both Snocone (output) and Prolog (input) can handle easily.
3. **Two Snocone phases:** Same `.scrip` block used twice (parse + format),
   or two separate fenced blocks? The formatter is a different program.
4. **Optimizer scope:** Constant folding only, or also dead-push elimination,
   strength reduction (x*2 → x+x), etc.?
5. **Error handling:** What does the pipeline do with malformed input?

---

## Milestone

**M-SCRIP-DEMO3** fires when:
1. `demo/scrip3/expr.scrip` exists
2. `run_demo3.sh` compiles and runs clean
3. Output matches `expr.expected` (diff clean)
4. Optimizer demonstrably fires on at least one constant-fold case

*Not scheduled. Concept capture only. Revisit after M-SCRIP-DEMO2 fires.*

---

*SCRIP_DEMO3.md = L4. Concept doc. No session state here until work begins.*
