# GOAL-CORPUS-LAYOUT.md — Corpus reorganization formula

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** corpus (primary), `.github` (REPO-corpus.md update), SCRIP (script path updates)

**Status:** Design captured, not yet executed. CB-0-corpus in
`GOAL-SCRIP-BOOTSTRAP.md` is the operational rung that will implement
this formula when the design settles. This Goal file captures the
exploration so it isn't lost between sessions.

**Done when:** the corpus on disk matches the formula in this file:
- The three-relationship taxonomy (port set / single-source-with-emit /
  polyglot) is reflected in the folder layout.
- `.scrip` files have a documented place in the layout for polyglot
  programs.
- The smoke / feat / bench / collections / crosscheck / lib / lon
  top-level categories each have the correct first-axis (concept-first
  vs language-first) per their workflow.
- All gate scripts (`test_smoke_snobol4.sh` PASS=7,
  `test_smoke_unified_broker.sh` PASS=49, beauty self-host md5
  `abfd19a7a834484a96e824851caee159`) still pass after the moves.
- REPO-corpus.md is updated to reflect the new layout as authority.

---

## Why this Goal exists

CB-0-corpus in `GOAL-SCRIP-BOOTSTRAP.md` is the corpus reorg rung
that gates all subsequent emit-artifact work. Before any `--compile`
output gets committed alongside its source, the corpus needs a
clean layout that knows where to put generated artifacts, where
canonical sources live, and how multi-language programs are
organized.

The CB-0-corpus text in `GOAL-SCRIP-BOOTSTRAP.md` describes
mechanical moves (merge duplicate `beauty/` folders, sort
`csnobol4-suite/*` into `feat/`, rename opaque `rung*` directories)
but does not acknowledge:

1. **The three-relationship taxonomy.** Programs in this corpus
   come in three structurally different shapes (port set,
   single-source-with-emit-artifacts, polyglot), and conflating
   them in one folder-shape is a category error.
2. **The two-dimensional concept × language tension.** Different
   workflows pull different dimensions to the outermost level
   of the path; one-size-fits-all is wrong.
3. **The SCRIP/SCRIPtix/SCRIPten container language.** A seventh
   "language" exists — `.scrip` files that hold mixed-language
   content. They live somewhere; the layout has to say where.
4. **The cross-language call/return/forward/backtrack semantics.**
   A "program" in this system is not necessarily single-language.

This Goal file documents the formula that addresses all four,
so CB-0-corpus can implement it deterministically.

---

## Background — the four axes the corpus has to organize

Any program in this corpus sits in some position along multiple
axes at once. The filesystem is one-dimensional (paths are a
single hierarchy), so the layout privileges some axes and
suppresses others. Naming the axes explicitly makes the design
choices honest.

### 1. Concept axis — what the program *does*

Examples: `roman` (numeral conversion), `stack` (data structure),
`beauty` (SNOBOL4 source pretty-printer), `claws5` (corpus tagger),
`treebank-list` (parse tree printer), `porter` (English stemmer),
`fibonacci`, `primes`, `tower-of-hanoi`.

The concept is the abstract idea. Multiple implementations of
the same concept share the concept axis position.

### 2. Language axis — what the program is *written in*

Six source languages today:
- SNOBOL4 (`.sno`)
- Snocone (`.sc`)
- Icon (`.icn`)
- Prolog (`.pl`)
- Rebus (`.rbs`)
- Raku (`.raku`)

Plus a seventh "container" language — SCRIP (`.scrip`) — which
holds mixed-language content. SCRIP is not a peer of the six;
it is a *container* of them. See "SCRIP container language"
section below.

### 3. Emit-target axis — what the program is *compiled to*

Five emit targets per the Milestone-3 grid:
- C / x86-64 (NASM `.s`, linked `.o`/binary)
- JVM (Jasmin `.j`, assembled `.class`)
- .NET (MSIL `.il`, assembled `.dll`)
- WASM (`.wat` text, `.wasm` binary)
- JS (`.js` source emission)

For any canonical source program, up to five emit-target
artifacts can exist alongside it. They are derived, not
canonical; their content is reproducible from the canonical
source via the SCRIP emitter.

### 4. Provenance axis — where the program *came from*

- **Lon's own work** — programs Lon wrote
- **Gimpel's book** — classic SNOBOL4 programs from Gimpel
- **AI/SNOBOL4 papers** — programs from academic literature
  (`programs/aisnobol/` today)
- **csnobol4 test suite** — feature isolation tests
  (`programs/csnobol4-suite/` today)
- **Published corpora** — tagged English corpora (CLAWS5, TASA),
  bench inputs

Provenance is metadata. The same concept (a stack data structure)
might be implemented by Lon, by Gimpel in his book, and by
academic authors — three sources, three implementations, same
concept. Provenance shapes the *grouping* of programs that
came together as a published unit.

### 5. Purpose axis — what the program is *for*

- **Demo** — substantial reference programs that exercise the
  language (beauty, roman, claws5, treebank, porter, expression)
- **Smoke** — minimal rung tests (rung 1 = single token,
  rung 12 = beauty.sno) for ladder verification
- **Feat** — single-feature isolation tests (one file per
  language feature: patterns, capture, functions, data types)
- **Bench** — timing-focused programs (Fibonacci, primes, sort)
  where cross-runtime comparison is the point
- **Library** — reusable code intended to be `-INCLUDE`d or
  imported by other programs
- **Crosscheck** — engine-comparison harnesses (`crosscheck/rung*`
  today, run identical inputs through every runtime, diff outputs)

Purpose dictates which other axis is the natural outermost
dimension. Per-language libraries are language-first because
the consumer is a single-language program looking up an include
path. Cross-language demos are concept-first because the reader
is comparing implementations.

---

## The three relationships between source files

Once the axes are named, the next observation is that source
files in the corpus relate to each other in three structurally
different ways. Conflating these three in one folder shape was
the original design error in this Goal's exploration.

### Relationship 1 — Port set (peer implementations)

**Definition:** N independent canonical implementations of the
same concept, each in a different language. None is derived
from another. Each is a separately-authored SOURCE.

**Example:** `roman` implemented in SNOBOL4, Snocone, Icon, and
Prolog. Each version is a complete program in its own language.
A reader chooses one implementation to study or run.

**Workflow:** "Show me every implementation of roman."
"Compare how roman is expressed across languages." "Run the
SNOBOL4 version." "Run the Icon version."

**Folder shape (concept-first, language second):**
```
roman/
├── README.md
├── snobol4/
│   ├── roman.sno          ← canonical SNOBOL4 source
│   ├── roman.ref          ← oracle output
│   ├── roman.s            ← x64 emission (derived)
│   ├── roman.j            ← JVM emission (derived)
│   ├── roman.il           ← .NET emission (derived)
│   ├── roman.wat          ← WASM emission (derived)
│   └── roman.js           ← JS emission (derived)
├── snocone/
│   ├── roman.sc
│   ├── roman.ref
│   └── ... (emissions)
├── icon/
│   ├── roman.icn
│   ├── roman.ref
│   └── ...
├── prolog/
│   ├── roman.pl
│   ├── roman.ref
│   └── ...
├── rebus/
└── raku/
```

**Three levels deep at the leaf:** `concept/language/file`.
Each language sub-folder is flat; canonical source, oracle ref,
and derived emissions sit as siblings, distinguished by
extension.

### Relationship 2 — Single-source with emit artifacts

**Definition:** One canonical source file in one language,
plus N derived emit-target artifacts. The artifacts are
generated by the SCRIP emitter; they are not separately
authored.

**Example:** `beauty.sno` — exists only in SNOBOL4. Has no
peer ports today. But when emitted by `--compile --target=x64`,
produces `beauty.s`. By `--target=js`, produces `beauty.js`.

**Workflow:** "Run the program." "Diff the x64 emission against
the SM-interp output." "Regenerate emissions after an emitter
change."

**Folder shape:** identical to Relationship 1's *language
sub-folder* — flat, canonical source plus oracle ref plus
derived emissions. The folder is just unique because there's
only one language present.

```
beauty/
├── README.md
└── snobol4/
    ├── beauty.sno         ← canonical
    ├── beauty.ref
    ├── (16 .inc files)    ← see "include files" section below
    ├── beauty.s           ← derived
    ├── beauty.j
    ├── beauty.il
    ├── beauty.wat
    └── beauty.js
```

The single-language case is structurally a degenerate port
set (N=1). It uses the same folder shape, just with one
language sub-folder populated. If `beauty` ever gets ported
to Snocone, the shape extends naturally — `beauty/snocone/`
joins as a peer.

### Relationship 3 — Polyglot program (collaborating files)

**Definition:** N source files in M ≤ N languages, all required,
working together at runtime via cross-language call/return/
forward/backtrack. The files are not peer ports; they are
collaborators in one program.

**Example:** `polycalc` — driver in SNOBOL4 (`main.sno`),
AST evaluator in Snocone (`ast.sc`), symbolic rules in Prolog
(`rules.pl`). The driver calls the evaluator calls the rules.
Removing any one breaks the program.

**Workflow:** "Run the program." "Inspect the polyglot
composition." "Edit the Snocone evaluator." This is one
program, expressed in multiple languages because each language
fits its sub-problem.

**Folder shape (flat, no language sub-folders):**
```
polycalc/
├── README.md              ← who calls whom, entry point
├── main.sno               ← driver / entry point
├── ast.sc                 ← Snocone AST evaluator
├── rules.pl               ← Prolog rule database
├── polycalc.input         ← test input
├── polycalc.ref           ← oracle output
├── polycalc.s             ← x64 emission of THE WHOLE program
├── polycalc.j
├── polycalc.il
├── polycalc.wat
└── polycalc.js
```

**Two levels deep at the leaf:** `concept/file`. No language
sub-folder because the languages are not peers — they are
collaborators in one combined program. Emissions are named
after the *program* (`polycalc.s`), not after a source file,
because the emission is of the composition, not of one
participant.

### How a reader distinguishes the three relationships

By inspection of the folder contents:

| Folder contains | Relationship |
|-----------------|--------------|
| Language sub-folders, multiple populated | Port set (N≥2) |
| Language sub-folders, one populated | Single-source with emit artifacts (degenerate port set) |
| Source files at concept level (no language sub-folders) | Polyglot program |

The folder *shape* is the label. No category prefix in the
path is needed; the contents make the kind obvious.

---

## SCRIP container language

SCRIP is not a peer of SNOBOL4 / Snocone / Icon / Prolog /
Rebus / Raku. It is a *container* — a file format that holds
mixed-language content with explicit language-switch markers.

Two flavors are under consideration:

### SCRIPtix — Markdown literate programming

`.scrip` files are Markdown documents with fenced code blocks.
Each fence declares its language; the runtime walks fences in
order, executing each in its language. State (variable bindings,
name table, call stack) carries across fences via the
cross-language call/return ABI.

````markdown
# Polycalc — polyglot calculator

This program parses arithmetic expressions in SNOBOL4, evaluates
them in Snocone, and applies symbolic simplification rules in
Prolog.

## Lexer

```snobol4
                 digits = SPAN('0123456789')
                 operators = ANY('+-*/')
                 ...
END
```

## Evaluator

```snocone
proc evaluate(ast) ...
end
```

## Simplification rules

```prolog
simplify(X + 0, X).
simplify(X * 1, X).
```
````

The file reads like documentation. Notebook semantics: each
fence is a cell.

### SCRIPten — tight inline code-switching

`.scrip` files use inline `@language { ... }` blocks for
fine-grained code-switching, including inside expressions:

```scrip
@snobol4 {
    pattern = SPAN(digits) . n
    @snocone { return n * 2 }
}
@prolog {
    fact(X) :- X > 0, @snocone { return X - 1 }.
}
```

Code-switching at sub-statement granularity. A SNOBOL4 pattern
action can contain a Snocone expression which contains a Prolog
query. The runtime handles language transitions inside a single
statement.

### Open question — one extension or two?

Both flavors share the `.scrip` extension with the parser
detecting flavor by content (Markdown structure vs `@lang { }`
blocks), or `.scriptix` for one and `.scripten` for the other,
or some other split. **Not yet decided.**

For corpus layout purposes, treat them as the same extension
until the question settles. The folder shape doesn't depend on
the answer.

### Where `.scrip` files live in the corpus

Two cases:

**Case A — `.scrip` is the canonical form of a polyglot program:**

```
polycalc/
├── README.md
├── polycalc.scrip         ← THE source
├── polycalc.ref
└── polycalc.{s,j,il,wat,js}  ← emissions of the whole .scrip
```

The `.scrip` file is the source of truth. There is no parallel
`main.sno` + `ast.sc` + `rules.pl` split form sitting alongside —
that would be redundant and would drift. If the multi-file split
form is ever needed (to feed tools that don't speak `.scrip`),
it's *generated* from the `.scrip` and not committed.

**Case B — `.scrip` accompanies a port-set concept folder:**

A `.scrip` file may sit at the concept level of a port-set
folder, alongside language sub-folders, when the polyglot
composition is *itself* a notable artifact distinct from any
single-language port:

```
roman/
├── README.md
├── snobol4/roman.sno (+ emissions)
├── snocone/roman.sc (+ emissions)
├── icon/roman.icn (+ emissions)
├── prolog/roman.pl (+ emissions)
└── roman.scrip            ← polyglot composition that USES roman as a building block
```

This is rarer. Most concepts will be either port set OR polyglot,
not both. The combined form is allowed when both genuinely exist.

### Notebook integration

The `.scrip` format suggests a notebook UI (Jupyter kernel for
`.scrip` would be the natural editor). Notebook cells map to
fences (SCRIPtix) or `@lang { }` blocks (SCRIPten).

Important hygiene: corpus `.scrip` files **do not contain
embedded outputs**. Run results live in `.ref` files
alongside, the same way SNOBOL4 oracle output works today.
This keeps `.scrip` files diffable and version-control-friendly.

---

## The corpus formula

Putting axes, relationships, and SCRIP together, the corpus
top-level layout is:

```
corpus/
├── programs/                ← demos, concept-first
│   ├── <port-set-concept>/         ← peer ports (Relationship 1)
│   │   ├── README.md
│   │   ├── snobol4/<concept>.sno + .ref + emissions
│   │   ├── snocone/<concept>.sc + .ref + emissions
│   │   ├── icon/<concept>.icn + .ref + emissions
│   │   └── ... (other languages)
│   ├── <single-source-concept>/    ← Relationship 2 (degenerate N=1)
│   │   ├── README.md
│   │   └── snobol4/<concept>.sno + .ref + emissions
│   └── <polyglot-concept>/         ← Relationship 3
│       ├── README.md
│       ├── <concept>.scrip         (or per-language files if not consolidated)
│       ├── <concept>.ref
│       └── <concept>.{s,j,il,wat,js}
├── lib/                     ← libraries, language-first
│   ├── snobol4/
│   │   ├── is.inc
│   │   ├── fence.inc
│   │   ├── io.inc
│   │   └── ... (more includes)
│   ├── snocone/
│   ├── icon/
│   ├── prolog/
│   ├── rebus/
│   ├── raku/
│   └── scrip/                      ← polyglot libraries (rare)
│       └── polylib.scrip
├── smoke/                   ← rung tests, language-first
│   ├── snobol4/
│   │   ├── rung01.sno              ← single token
│   │   ├── rung02.sno              ← assign
│   │   └── ... (rung03..rung12)
│   ├── snocone/
│   ├── icon/
│   ├── prolog/
│   ├── rebus/
│   └── raku/
├── feat/                    ← single-feature isolation, language-first
│   ├── snobol4/
│   │   ├── f01_core_labels_goto.sno
│   │   ├── f02_string_ops.sno
│   │   └── ... (sorted from csnobol4-suite)
│   └── (other languages as ports complete)
├── bench/                   ← benchmarks, concept-first
│   ├── fibonacci/
│   │   ├── snobol4/fib.sno + emissions
│   │   ├── snocone/fib.sc + emissions
│   │   └── ...
│   ├── primes/
│   ├── sort/
│   └── ...
├── collections/             ← provenance-defined, frozen as published
│   ├── gimpel/
│   │   └── snobol4/                ← Gimpel's book — flat list of .sno files
│   │       ├── AGT.sno + .ref
│   │       ├── AI.sno + .ref
│   │       └── ... (150 files)
│   ├── aisnobol/
│   │   └── snobol4/                ← AI/SNOBOL4 papers
│   └── csnobol4-suite/
│       └── snobol4/                ← csnobol4 test suite (or: extract into feat/)
├── crosscheck/              ← engine-comparison harnesses
│   ├── README.md            ← document each rung's purpose
│   ├── arith/
│   ├── assign/
│   ├── beauty/
│   ├── (rung* dirs renamed to descriptive names)
│   └── ...
└── lon/                     ← Lon's personal programs (kept verbatim)
    ├── eng685/
    ├── rinky/
    └── sno/
```

### Per-category outermost-axis rationale

| Top-level dir | Outermost axis | Rationale |
|---------------|----------------|-----------|
| `programs/`   | Concept | Demos compare across languages; reader's verb is "show me every roman" |
| `lib/`        | Language | Consumer is a single-language program looking up include paths |
| `smoke/`      | Language | Per-language ladder; smoke runner walks one language tree |
| `feat/`       | Language | Single-feature tests are language-specific by nature |
| `bench/`      | Concept | Cross-runtime timing comparison is the whole point |
| `collections/`| Provenance | Unit of grouping is the source (Gimpel's book), then language under that |
| `crosscheck/` | Concept | Engine comparison runs same input across runtimes |
| `lon/`        | (Lon's own structure) | Personal programs, kept as Lon organized them |

### Provenance handling — `collections/` deep dive

The provenance axis becomes the outer dimension only for
`collections/`, where the unit of meaning *is* the source.
`gimpel/AGT.sno` matters because it is *Gimpel's AGT* —
extracting it into a port-set folder under `programs/AGT/`
loses the provenance information.

Inside a collection folder, the next axis is language (not
concept), because collections are typically published in one
language. Gimpel's book is SNOBOL4. AI/SNOBOL4 papers are
SNOBOL4. The csnobol4 test suite is SNOBOL4. So:

```
collections/gimpel/snobol4/AGT.sno
collections/aisnobol/snobol4/<file>.sno
collections/csnobol4-suite/snobol4/<file>.sno
```

If a collection ever spans multiple languages (a published
multi-language anthology, hypothetically), the same shape
extends — `collections/<source>/<language>/<file>`.

### csnobol4-suite split decision

`csnobol4-suite/` (253 files today) sits in `collections/`
*as published*. But many of its files are single-feature
isolation tests, which belong in `feat/snobol4/`. Two paths:

- **Path A — keep whole, extract for use:** `collections/csnobol4-suite/`
  stays intact as the published artifact. Files used as feature
  tests get *copied* into `feat/snobol4/` with appropriate names.
  Duplication is the cost of preserving provenance.
- **Path B — extract and dissolve:** files get sorted into
  `feat/snobol4/`, `programs/<concept>/snobol4/`, or wherever
  they fit. The `csnobol4-suite` collection is dissolved — its
  bytes live elsewhere. A `collections/csnobol4-suite/README.md`
  records the original provenance and lists where each file
  went.

**Recommendation:** Path B. Provenance is preserved as
metadata (the README), not as duplicated bytes. RULES.md bans
duplicate corpus source files for good reason.

### Self-contained demos exception

RULES.md carves out an exception for self-contained demo
programs: a folder that ships with its own copies of shared
includes (`is.inc`, `FENCE.inc`, `io.inc`) so it's portable
to runtimes without `-INCLUDE` path support. Today this
applies to `programs/snobol4/demo/beauty/`.

In the new layout, this exception still applies. The
`beauty/snobol4/` folder under `programs/` carries its own
copies of the includes alongside `beauty.sno`. The canonical
copies live in `lib/snobol4/`. Synchronization is by
hand-discipline: when `lib/snobol4/io.inc` changes, every
self-contained folder carrying a copy updates in the same
commit. CI verification: byte-diff between the canonical
`lib/` copy and each self-contained copy must be empty.

---

## Naming conventions

### Concept folder names

- Lowercase, hyphenated for multi-word: `tower-of-hanoi`,
  `treebank-list`, `tower-of-hanoi`.
- Match the conventional name of the program (`beauty`,
  `roman`, `claws5`, `porter` — all already in use).
- Avoid abbreviations unless the abbreviation is the
  conventional name (`agt` is fine if AGT is what Gimpel
  called it).

### Source file names

- Match the concept folder name: `roman/snobol4/roman.sno`,
  not `roman/snobol4/main.sno`.
- For polyglot programs (Relationship 3), file names indicate
  *role* not concept: `polycalc/main.sno`, `polycalc/ast.sc`,
  `polycalc/rules.pl`. The folder name is the program; the
  file names describe their roles within it.
- Companion files: `<concept>.input` for input fixtures,
  `<concept>.ref` for oracle output, `<concept>.dat` for
  data files used at runtime.

### Emission file names

- Match the canonical source's basename, with the emission's
  natural extension: `roman.sno` → `roman.s` (NASM), `roman.j`
  (Jasmin), `roman.il` (MSIL), `roman.wat` (WASM), `roman.js`.
- For polyglot programs, the emission is named after the
  program: `polycalc.scrip` → `polycalc.s`, `polycalc.j`, etc.
- If a future emit target collides with an existing extension
  (e.g. ARM64 also producing `.s`), disambiguate with a
  target-prefix segment: `roman.x64.s` vs `roman.arm64.s`.
  Today no collision exists; plain extensions work.

### Conflict — `.js` as both source and emission

`.js` is potentially a source language extension (if JS becomes
a SCRIP source language) and is the JS emission extension. No
conflict today (JS is emit-target only). If JS ever becomes
a source language, the emission gets disambiguated:
`roman.emit.js` or similar. Deferred decision; not blocking.

---

## Open questions

These need answers before the formula can be executed. Some
are operational, some are foundational.

### Layout questions

1. **Concept-first scope:** Is `programs/` the *only* top-level
   that uses concept-first ordering, or do other categories
   (e.g. `bench/`) also? Current proposal: yes, `bench/` is
   concept-first too. Confirm.

2. **Single-language degenerate case:** Is wrapping a
   single-language program (`beauty/snobol4/beauty.sno`) in
   a one-language-folder folder always preferred over flat
   (`beauty/beauty.sno`)? Tradeoff: the folder makes the
   layout uniform with the port-set case (Relationship 1),
   so a future port adds naturally. Flat saves a level when
   the port will never come. Current proposal: always
   wrap, for uniformity.

3. **`feat/` extraction from `csnobol4-suite/`:** Path A or
   Path B (above)? Current proposal: Path B (extract and
   dissolve, preserve provenance in README).

4. **`collections/csnobol4-suite/` per-feature extraction
   classification:** 253 files need sorting by feature.
   Some are obvious by name (`alt1.sno` → alternation);
   some are opaque (`a.sno`, single-letter names). Real
   classification requires reading file contents. Who does
   this and when? Current proposal: hand-classify in a
   separate sub-rung after the bonepile move; not blocking
   the layout decision.

5. **`crosscheck/rung*` renaming:** ~30 opaque-named subdirs
   need descriptive names with READMEs. Same separation:
   layout move first, content classification later.

6. **Existing extras under `programs/snobol4/`:** `jvm_j3/`,
   `linker/`, `subexpr/` — what are these and where do they
   go in the new layout? Need investigation.

7. **`run/`, `generated/`, `snobol4corpus/`:** purpose
   unclear. Document or remove. Not blocking layout decision.

8. **`programs/include/` vs `programs/include-sc/` vs
   `lib/`:** three include locations today. The new layout
   consolidates to `lib/<language>/`. Move plan: include
   files migrate to `lib/snobol4/`, `lib/snocone/`, etc.,
   with the self-contained-demo exception preserving
   `beauty/snobol4/` copies.

### SCRIP questions

9. **SCRIPtix vs SCRIPten — one extension or two?** Both
   flavors share `.scrip` with content-detection, or split
   into `.scriptix` and `.scripten`. **Not yet decided.**
   Layout shape doesn't depend on the answer; defer.

10. **SCRIP as 7th source language in the bootstrap grid?**
    PLAN.md's Milestone-3 grid is six rows (SNOBOL4, Snocone,
    Icon, Prolog, Rebus, Raku) × five columns (C, JVM, .NET,
    WASM, JS). Does it grow to seven (add SCRIP), or is
    SCRIP categorically different (the *containing* form,
    not a peer source)? Current intuition: SCRIP is *above*
    the grid, not in it — a `.scrip` file's emission is
    determined by its constituent languages' rows.

11. **Notebook UI implementation:** Is Jupyter integration
    planned, or is the notebook framing currently aspirational?
    Doesn't affect layout; affects future tooling.

12. **`.scrip` as canonical for polyglot vs split form
    co-canonical:** Layout proposes `.scrip` is canonical
    when polyglot is consolidated; multi-file split is
    derived. Confirm. Alternative: both forms are canonical,
    with sync discipline like the self-contained-demo
    exception.

13. **Bidirectional split/bundle tooling:** Does the
    toolchain include scripts that bundle multi-file
    polyglot folders into `.scrip`, and vice versa? If
    yes, the corpus only commits one form. If no, both
    might genuinely live, with explicit canonical-vs-derived
    rules per program.

### Authority questions

14. **REPO-corpus.md vs Goal file authority:** RULES.md
    says REPO-corpus.md is authoritative for layout. The
    formula in this Goal file proposes a layout that is
    *richer* than what REPO-corpus.md currently describes.
    When the formula is executed, REPO-corpus.md must be
    updated to match. This is part of CB-0-corpus's gate.

15. **`gimpel/` and `lon/` sibling-of-snobol4 placement:**
    REPO-corpus.md currently places `gimpel/` and `lon/` as
    siblings of `snobol4/` under `programs/`. The formula
    in this Goal file relocates them: `gimpel/` →
    `collections/gimpel/snobol4/`, `lon/` → `lon/` (top
    level, not under `programs/`). Update REPO-corpus.md as
    part of the move.

### Test gate questions

16. **Gate-critical paths during reorg:** the moves must
    preserve gate-critical paths or update gate scripts in
    lockstep. Beauty self-host points at
    `corpus/programs/snobol4/demo/beauty/`. After reorg this
    becomes `corpus/programs/beauty/snobol4/`. The gate
    script (`scripts/test_smoke_unified_broker.sh` and the
    `BEAUTY=` env var in CB-0-corpus's gate snippet) must
    update in the same commit.

17. **`SNO_LIB` paths in tests:** all gate scripts referencing
    `SNO_LIB=$BEAUTY` or `SNO_LIB=...` must be audited and
    updated. Same for `SETL4PATH` (SPITBOL include path).

---

## Implementation plan (when this Goal is executed)

This sequence is the proposed execution order. Each sub-rung
has its own gate; later sub-rungs assume earlier ones landed.

### Sub-rung CL-1 — Bonepile move

Move all of `corpus/programs/` into `corpus/bonepile/programs/`
in a single `git mv` commit. Other top-level dirs (`benchmarks/`,
`crosscheck/`, `lib/`, `run/`, `generated/`) move too unless
they survive the formula unchanged. After this commit, the
working tree at the corpus's top level looks like:

```
corpus/
├── bonepile/                ← everything that was here before
│   ├── programs/
│   ├── benchmarks/
│   ├── crosscheck/
│   ├── lib/
│   ├── run/
│   └── generated/
└── (top-level docs unchanged: README.md, LICENSE, etc.)
```

**Gate:** the move is a single `git mv`-only commit. No content
changes. Test scripts in `SCRIP/scripts/` are *expected to
break* at this point — that's accepted; the next sub-rung
re-emerges the gate-critical paths.

### Sub-rung CL-2 — Re-emerge gate-critical paths

Move the minimum set of files out of `bonepile/` to satisfy
the smoke=7 / broker=49 / beauty-md5 gate. This means at
minimum:

- The files referenced by `test_smoke_snobol4.sh`.
- The files referenced by `test_smoke_unified_broker.sh`.
- The beauty self-host path: `corpus/programs/beauty/snobol4/`
  with `beauty.sno`, `beauty.ref`, all 16 includes.

Update the gate scripts in `SCRIP/scripts/` to point at
the new paths in the same commit.

**Gate:** smoke=7, broker=49, beauty-md5 all green again
on the new paths. Bonepile remains; everything else still
in it.

### Sub-rung CL-3 — Build out new layout skeleton

`mkdir -p` the new top-level skeleton:
```
programs/
lib/snobol4/  lib/snocone/  lib/icon/  lib/prolog/  lib/rebus/  lib/raku/
smoke/snobol4/  smoke/snocone/ ...
feat/snobol4/  feat/snocone/ ...
bench/
collections/gimpel/snobol4/  collections/aisnobol/snobol4/  collections/csnobol4-suite/snobol4/
crosscheck/
lon/
```

Empty directories with `.gitkeep` files where Git needs them.
This makes the layout visible; subsequent sub-rungs populate it.

**Gate:** layout matches the formula. No content moved yet
beyond CL-2's gate-critical paths.

### Sub-rung CL-4 — Migrate per category

One commit per top-level category, in order of risk:

- CL-4a — `lib/<language>/` from bonepile/programs/include,
  bonepile/programs/include-sc, bonepile/lib
- CL-4b — `lon/` from bonepile/programs/lon
- CL-4c — `collections/gimpel/snobol4/` from
  bonepile/programs/gimpel
- CL-4d — `collections/aisnobol/snobol4/` from
  bonepile/programs/aisnobol
- CL-4e — `collections/csnobol4-suite/snobol4/` from
  bonepile/programs/csnobol4-suite (whole, before
  feat/ extraction)
- CL-4f — `programs/<concept>/<language>/` for each
  concept program (per-program migration, one commit
  per concept or one bulk commit per category — TBD)
- CL-4g — `bench/<concept>/<language>/` from
  bonepile/benchmarks
- CL-4h — `crosscheck/` rename rung* to descriptive
  names (this is its own work; can defer)
- CL-4i — `smoke/<language>/rung01..rung12` from
  bonepile/programs/snobol4/smoke and equivalent
- CL-4j — `feat/<language>/` extraction from
  collections/csnobol4-suite (provenance preserved
  in collection's README)

After each CL-4x: gate scripts updated, smoke=7,
broker=49, beauty-md5 green.

### Sub-rung CL-5 — Document the layout

- Update `REPO-corpus.md` with the new layout as authority.
- Update `corpus/README.md` and `corpus/LAYOUT.md` to match.
- Add `crosscheck/README.md` documenting each rung's purpose.
- Add `collections/<source>/README.md` for each collection
  documenting its provenance.
- Add `programs/<concept>/README.md` for each port-set or
  polyglot concept folder explaining what the concept is.

### Sub-rung CL-6 — Delete the bonepile

When every directory and file under `bonepile/` has been
either re-emerged into the new layout OR explicitly noted
as obsolete (with the reason in a closing commit message),
delete `corpus/bonepile/` entirely.

**Gate:** `corpus/bonepile/` does not exist. Smoke=7,
broker=49, beauty-md5 still green. The corpus's layout
matches the formula in this Goal file.

### Sub-rung CL-7 — Update SCRIP/scripts/

Audit and update all scripts in `SCRIP/scripts/` that
reference corpus paths. Rationalize the env vars (`SNO_LIB`,
`SETL4PATH`, `BEAUTY`) to point at the new canonical paths.

**Gate:** every script in `SCRIP/scripts/` runs without
"file not found" errors. Smoke and broker still green.

### Sub-rung CL-8 — Mark CB-0-corpus complete

`GOAL-SCRIP-BOOTSTRAP.md` CB-0-corpus is gated by this
Goal's CL-7. Mark CB-0-corpus done; CB-0a (the first
`--compile` work) becomes the active rung in the parent
goal.

---

## Open questions are *gating* — answer before CL-1

CL-1 (the bonepile move) is a one-way street. Doing it before
the formula is settled risks moving files into a layout that
gets revised, requiring re-moves. Before CL-1 lands:

- Open questions 1–7 (layout questions) need answers.
- Open questions 9–13 (SCRIP questions) need *enough*
  decision to know whether `.scrip` files exist in the
  corpus today — if they don't, the layout's `.scrip`
  provisions are forward-looking and don't block CL-1.
- Open questions 14–17 (authority and gate questions)
  need answers as commitments, not as code; they shape
  REPO-corpus.md and the gate scripts.

The questions about feature classification, rung renaming,
and provenance details (questions 4, 5) are *internal* to
sub-rungs (CL-4i, CL-4j, etc.) and can be deferred without
blocking CL-1.

---

## Why this is one Goal, not folded into CB-0-corpus

CB-0-corpus in `GOAL-SCRIP-BOOTSTRAP.md` is the *gate* — it
says "the corpus must be reorganized before emit work begins."
This Goal file is the *substance* — the formula that explains
what "reorganized" means.

Splitting the substance from the gate matters because:

1. The formula here applies beyond CB-0-corpus. Every future
   `.sno` added to the corpus uses these rules. Every emit
   artifact placed during CB-0a..f respects this layout. The
   formula is reusable; CB-0-corpus is consumed once.
2. The active rung in `GOAL-SCRIP-BOOTSTRAP.md` should remain
   short and operational. Inlining 600 lines of taxonomy and
   open questions into one rung's text obscures the parent
   goal's structure.
3. Goal files in this repo are the unit of work. A separate
   Goal makes the corpus reorg legible as its own destination,
   with its own done-when, its own rungs, its own session
   handoff state.

When this Goal is executed, CB-0-corpus in
`GOAL-SCRIP-BOOTSTRAP.md` reduces to: "implement
GOAL-CORPUS-LAYOUT.md CL-1..CL-8."

---

## Cross-references

- **GOAL-SCRIP-BOOTSTRAP.md** — contains the operational rung
  CB-0-corpus that is gated by this Goal's completion.
- **REPO-corpus.md** — current layout authority, will be
  updated to reflect this Goal's formula at CL-5.
- **RULES.md** — "Casing belongs at the ingress layer", "No
  duplicate corpus source files", "No symlinks", "Self-contained
  scripts" — all bind on this Goal's execution.
- **GOAL-POLYGLOT-CALC-DEMO.md** — the polyglot calculator
  demo; will exemplify Relationship 3 (polyglot program) when
  it lands. May produce the first canonical `.scrip` file.
- **GOAL-UNIFIED-BROKER.md** — the cross-language call/return/
  forward/backtrack runtime mechanism. Makes Relationship 3
  (polyglot programs) actually runnable.
- **PLAN.md** — Milestone-3 grid (6 languages × 5 backends)
  is the bootstrap target. This Goal organizes the corpus to
  hold (6 × 5 = 30) emission cells per program, plus the
  cross-relationship variations.

---

## Active rung

**(none — Goal is in design state, not yet executed)**

When ready to execute: open question list above must be
answered. Once answered, the first rung is **CL-1 — Bonepile
move**.

---

## Authorship

This Goal file captures a session-#NN design exploration
between Lon and Claude Sonnet. The conversation surfaced
the three-relationship taxonomy, the SCRIP container language
implications, and the per-category outermost-axis decisions.
Per RULES.md, commits are authored as LCherryholmes; the
substantive design work is recorded here.

---

## Latent follow-ups (not gating)

- **A "view" generator** — once the canonical layout is
  concept-first or language-first per category, a small tool
  that walks the canonical tree and produces the *other* axis
  as an HTML or Markdown index would be useful for browsing.
  No file duplication; the alternate-axis view is regenerated
  on demand. Out of scope for this Goal; tracked here so it
  isn't lost.
- **Per-program README templates** — concept folders need
  READMEs explaining what the concept is and which languages
  have ports. A small template + checker would help keep
  these consistent. Out of scope; tracked.
- **Emit-artifact gitignore policy** — whether to commit
  `.s` / `.j` / `.il` / `.wat` / `.js` files alongside their
  sources, or gitignore them and require regeneration. Trade-off
  between checkout reproducibility and tree size. RULES.md
  hints at "generated files committed" for `.tab.c`/`.lex.c`;
  whether this extends to emitter outputs is a separate
  decision. Tracked, not blocking.
- **`.scrip` Jupyter kernel** — the notebook story. Would be
  a big piece of work in its own right. Tracked, not blocking
  the corpus layout.
