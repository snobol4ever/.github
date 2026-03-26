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

1. `demo/scrip/puzzle1.clues` (and 2–5) exist in `snobol4x`
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
| `puzzle1.clues` – `puzzle5.clues` | `snobol4x/demo/scrip/` | S-expression puzzle inputs |
| `puzzle1.expected` – `puzzle5.expected` | `snobol4x/demo/scrip/` | Expected outputs |
| `family.scrip` → `puzzle1.scrip` | `snobol4x/demo/scrip/` | Fenced polyglot source |
| `run_demo2.sh` | `snobol4x/demo/scrip/` | Build + run (reuses Demo #1 infra) |
| `README.md` (update) | `snobol4x/demo/scrip/` | Add Demo #2 section |

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
