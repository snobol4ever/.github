# GOAL-BEAUTIFY.md — Snocone reimplementation of SNOBOL4 beauty pretty-printer

**Repo:** corpus (new `beautify/` folder + ~19-program test suite),
one4all (Snocone runtime invocation in test scripts), `.github`
(this Goal file)

**Status:** Hand-off from session-#NN. Next session begins here.
No code written yet; design captured.

**Done when:**
- `beautify.sc` exists as a Snocone implementation of the SNOBOL4
  pretty-printer.
- BEAUTIFY self-host gate passes: `beautify.sc` reads `beauty.sno`
  and emits SNOBOL4 source byte-identical to the original. md5 of
  the output matches the existing BEAUTY md5
  `abfd19a7a834484a96e824851caee159`.
- The ~19-program beauty test suite has Snocone drivers
  (`*_driver.sc`) that exercise `beautify.sc` against the same
  SNOBOL4 inputs the SNOBOL4 BEAUTY suite uses. All produce
  output matching the existing `.ref` oracle files byte-for-byte.
- `scripts/test_beautify_self_host.sh` exists and is part of the
  smoke gate suite.

---

## Critical clarification — what BEAUTIFY is and is not

**BEAUTIFY processes SNOBOL4 source.** It does not (yet) process
Snocone source.

The naming might suggest "beautify Snocone code." It does not.
BEAUTIFY is a **Snocone-language implementation** of the **SNOBOL4
pretty-printer**. Its input is SNOBOL4 source. Its output is the
same SNOBOL4 source, pretty-printed.

So:

| Program | Implemented in | Reads | Writes |
|---------|----------------|-------|--------|
| BEAUTY   | SNOBOL4 (`beauty.sno`)   | SNOBOL4 source | SNOBOL4 source (formatted) |
| BEAUTIFY | Snocone (`beautify.sc`)  | SNOBOL4 source | SNOBOL4 source (formatted) |

A future BEAUTIFY-extended could pretty-print Snocone source,
but that is not this Goal.

### Self-host terminology

The word "self-host" is doing something specific in both names:

- **BEAUTY self-host:** the SNOBOL4 program `beauty.sno` reads
  its own SNOBOL4 source file and emits it unchanged. The
  "self" is `beauty.sno` itself.
- **BEAUTIFY self-host:** the Snocone program `beautify.sc`
  reads `beauty.sno` (the *SNOBOL4* program) and emits it
  unchanged. The "self" here is the SNOBOL4 BEAUTY corpus —
  *not* `beautify.sc`'s own source. BEAUTIFY does not read
  its own Snocone source.

The gate constants are therefore:

- **BEAUTY md5 of `beauty.sno` after self-printing:** `abfd19a7a834484a96e824851caee159`
- **BEAUTIFY md5 of `beauty.sno` after Snocone-printing:** **must equal the BEAUTY md5**, because both produce the same SNOBOL4 file from the same input.

This makes the BEAUTIFY gate auto-cross-checked against the
BEAUTY gate. They share an oracle: if they produce the same
md5, both are correct (or both wrong in the same way, which
is unlikely given independent implementations).

---

## Why this Goal exists

The SCRIP Bootstrap goal (`GOAL-SCRIP-BOOTSTRAP.md`) targets
a multi-language bootstrap where SNOBOL4, Snocone, Icon, Prolog,
Rebus, and Raku all reach self-hosting on five backends (C/x86-64,
JVM, .NET, WASM, JS). Today the SNOBOL4 leg of that grid is
mature; Snocone is significantly less so.

A canonical milestone for "Snocone is real enough to bootstrap"
is having a non-trivial program *implemented* in Snocone that
reproduces a known-correct SNOBOL4 program's behavior. The
beauty pretty-printer is an excellent target because:

1. It is non-trivial — ~19 modules with substantial logic.
2. It has a hard, byte-level gate (md5 of self-printed output).
3. It exercises the same SNOBOL4 features Snocone is trying to
   support: pattern matching, replacement, capture, includes,
   functions, control flow.
4. The oracle (`*.ref` files) already exists. No new oracle
   work required — the BEAUTIFY gate compares against the
   existing BEAUTY oracle.
5. Failure points are diagnosable. If `beautify.sc` produces
   wrong output, the diff against BEAUTY's `.ref` file
   localizes the bug.

This Goal is the path from "Snocone exists" to "Snocone runs
a substantial program correctly," as a precondition for
extending the SCRIP Bootstrap grid into the Snocone row.

---

## File-by-file port plan

The SNOBOL4 BEAUTY corpus today lives at
`corpus/programs/snobol4/beauty/` and contains 64 entries.
A representative sample of what needs porting:

### Main pretty-printer modules (likely 6 modules)

Each `<module>.sno` becomes `<module>.sc`:

- `Gen.sno` → `Gen.sc`
- `Qize.sno` → `Qize.sc`
- `ReadWrite.sno` → `ReadWrite.sc`
- `ShiftReduce.sno` → `ShiftReduce.sc`
- `TDump.sno` → `TDump.sc`
- `XDump.sno` → `XDump.sc`

### Drivers (one per module)

Each `<module>_driver.sno` becomes `<module>_driver.sc`:

- `Gen_driver.sno` → `Gen_driver.sc`
- `Qize_driver.sno` → `Qize_driver.sc`
- `ReadWrite_driver.sno` → `ReadWrite_driver.sc`
- `ShiftReduce_driver.sno` → `ShiftReduce_driver.sc`
- `TDump_driver.sno` → `TDump_driver.sc`
- `XDump_driver.sno` → `XDump_driver.sc`

### Reference files (kept verbatim)

Each `<module>_driver.ref` is **kept exactly as-is**. The
Snocone driver must produce byte-identical output to these
oracle files. Do not re-derive from SPITBOL; the existing
`.ref` files are the gate.

### Tracepoint configs (carried over)

Each `<module>_tracepoints.conf` may need a Snocone equivalent
or carry over directly, depending on whether the Snocone
runtime has equivalent tracepoint mechanism. Investigate
during the port; this is not blocking.

### Per-feature test files

Beyond the 6 module drivers, there are smaller per-feature
test `.sno` files (visible in the directory listing as
`assign.sno`, etc.). Each gets a `.sc` port. The exact list
needs enumeration at session start.

### Includes — open question

The SNOBOL4 BEAUTY suite uses `.inc` files for shared
declarations (the 16 includes mentioned in the
self-contained-demo exception in RULES.md). The Snocone
language may use a different include mechanism. Three
possibilities:

1. **Snocone `.inc` files:** if Snocone has its own include
   directive that reads `.inc`-style files, port each `.inc`
   to a Snocone-flavored `.inc`. Naming risks confusion with
   the SNOBOL4 includes; possibly use `.sc.inc` or just `.inc`
   in the Snocone subfolder where context disambiguates.
2. **Snocone modules:** Snocone may use a module/proc system
   instead of textual includes, in which case the SNOBOL4
   `.inc` content gets refactored into Snocone procs/modules
   and not literally ported as `.inc`.
3. **No includes needed:** the Snocone runtime may obviate
   some of what the SNOBOL4 `.inc` files provided (e.g. utility
   procedures already in the Snocone runtime library).

**Action at session start:** consult the Snocone manual / 
existing Snocone programs in the corpus to determine which
of these applies. The `programs/snocone/` folder and any
`build_*` scripts referencing Snocone are the starting points.

---

## Folder location — open question

Lon described creating "another folder in `demo/`," named
`beautify/`. Two candidate locations in the current pre-reorg
corpus layout:

**Option A** — `corpus/programs/snobol4/demo/beautify/`

- Sits alongside the existing SNOBOL4 demos.
- Reflects "this is in the snobol4 area because it's about
  SNOBOL4 source."
- But the *implementation* is Snocone, which is misleading
  for a folder labeled `snobol4`.

**Option B** — `corpus/programs/snocone/demo/beautify/`

- Sits in the Snocone area, where Snocone implementations
  belong.
- Requires `programs/snocone/demo/` to exist or be created.
- Reflects "this is a Snocone program, regardless of what
  language its input is in."

**Option C** — `corpus/programs/beautify/` (top-level concept folder)

- Anticipates the GOAL-CORPUS-LAYOUT.md reorganization where
  concept-first becomes the rule for `programs/`.
- The folder would have `snocone/beautify.sc` as its single
  language sub-folder today; could grow to `icon/beautify.icn`,
  `prolog/beautify.pl`, etc., later.
- Makes the eventual reorg a no-op for this folder — no move
  required.

**Recommendation: Option C.** It's forward-compatible with the
corpus-layout goal, makes the language axis explicit at the
language sub-folder level, and avoids the misleading
`programs/snobol4/` parent for a Snocone implementation. The
small cost is creating a new top-level concept folder before
the broader reorg has happened — but that costs nothing
operationally; it's just a directory.

If Lon prefers staying within the current pre-reorg layout's
conventions, Option B is acceptable. **Confirm with Lon at
session start.**

The shape under any chosen parent is the same:

```
beautify/                           ← concept folder (Option C)
└── snocone/                        ← language sub-folder
    ├── README.md
    ├── beautify.sc                 ← main pretty-printer
    ├── Gen.sc
    ├── Qize.sc
    ├── ReadWrite.sc
    ├── ShiftReduce.sc
    ├── TDump.sc
    ├── XDump.sc
    ├── Gen_driver.sc
    ├── Qize_driver.sc
    ├── ReadWrite_driver.sc
    ├── ShiftReduce_driver.sc
    ├── TDump_driver.sc
    ├── XDump_driver.sc
    ├── Gen_driver.ref              ← oracle, byte-identical to BEAUTY's
    ├── Qize_driver.ref
    ├── ReadWrite_driver.ref
    ├── ShiftReduce_driver.ref
    ├── TDump_driver.ref
    ├── XDump_driver.ref
    ├── beautify_self_host.ref      ← =`beauty.sno` itself, byte-identical
    ├── (per-feature test .sc files matching the .sno tests)
    └── (per-feature test .ref files, byte-identical to BEAUTY's)
```

The `.ref` files **are physical copies** (not symlinks — RULES.md
forbids them) of the BEAUTY oracle files. Sync discipline: when
a BEAUTY `.ref` updates, the BEAUTIFY copy updates in the same
commit. CI byte-diff verifies they stay identical.

(This duplication is justified by RULES.md's self-contained
demo exception: the BEAUTIFY suite is a self-contained
verification target. The duplicates aren't "two different oracles
of the same program" — they're two different *consumers* of the
same byte-identical oracle file.)

---

## Implementation rungs

### BFY-0 — Snocone runtime sanity check

Before any porting, verify the Snocone runtime in `one4all/`
can run a Snocone program end-to-end and produce expected
output.

- Locate the Snocone runtime entry point. Likely
  `build_snobol4_frontend.sh` produces something Snocone-aware,
  or there's a separate `build_snocone_*.sh`. Search:
  ```
  ls one4all/scripts/ | grep -i snocone
  grep -lir snocone one4all/scripts/
  ```
- Find one Snocone program in the corpus that's known to work.
  Run it. Compare to its `.ref` file.
- If no Snocone program runs, this Goal is blocked on Snocone
  runtime work — escalate to a separate Goal first.

**Gate:** at least one Snocone program in the corpus runs
successfully against its `.ref`.

### BFY-1 — Folder location decision and skeleton

- Confirm folder location with Lon (Options A/B/C above).
- `mkdir -p` the chosen path's `snocone/` sub-folder.
- Add a placeholder `README.md` describing what BEAUTIFY is
  (referencing this Goal file).
- Commit the empty skeleton.

**Gate:** folder exists; Lon has confirmed the location.

### BFY-2 — Include strategy decision

- Determine Snocone's include mechanism (consult manual,
  existing Snocone programs).
- Decide: literal `.inc` ports, refactor to procs/modules, or
  drop entirely (if Snocone runtime obviates).
- Document the decision in the BEAUTIFY README.

**Gate:** include strategy documented; ready to begin porting.

### BFY-3 — Port the smallest module first (likely Gen)

- Port `Gen.sno` → `Gen.sc` and its driver `Gen_driver.sno`
  → `Gen_driver.sc`.
- Copy `Gen_driver.ref` byte-identical from BEAUTY's folder.
- Run `Gen_driver.sc` through the Snocone runtime; capture
  output.
- Diff against `Gen_driver.ref`. If identical, BFY-3 is
  green. If not, debug Snocone implementation.

**Gate:** `Gen_driver.sc` produces output matching
`Gen_driver.ref` byte-for-byte.

### BFY-4..BFY-8 — Port remaining modules

In order: Qize, ReadWrite, ShiftReduce, TDump, XDump.
Each is a sub-rung; gate is byte-identical output for that
module's driver.

### BFY-9 — Per-feature tests

Port the per-feature `.sno` test files (assign, etc.).
Each gets its `.sc` port and copies its `.ref` byte-identical.
Gate: every per-feature test passes.

### BFY-10 — BEAUTIFY self-host gate

The capstone test:

- `beautify.sc` reads `beauty.sno` (the SNOBOL4 source) as input.
- `beautify.sc` outputs to a file.
- md5 of output must equal `abfd19a7a834484a96e824851caee159`
  (the BEAUTY md5).
- Add `scripts/test_beautify_self_host.sh` to one4all
  containing this test.

**Gate:** BEAUTIFY self-host md5 matches BEAUTY self-host md5.

### BFY-11 — Wire into smoke suite

Add BEAUTIFY tests to the broader smoke gate so future
changes can't silently regress them. Update
`test_smoke_unified_broker.sh` or equivalent to include
the BEAUTIFY suite. Confirm broker pass count increases
appropriately (current 49 → 49 + N for new Snocone tests).

**Gate:** smoke suite includes BEAUTIFY tests; total smoke
count is the new larger number; all pass.

### BFY-12 — Update GOAL-SCRIP-BOOTSTRAP.md

Mark the Snocone leg of the bootstrap grid as having a
non-trivial reference program. Adjust the active rung in
`GOAL-SCRIP-BOOTSTRAP.md` if BEAUTIFY's completion unlocks
the next CB-* sub-rung for Snocone.

---

## SPITBOL/Snocone manual notes

The corpus contains a SPITBOL manual (mentioned by Lon as
the reference for SNOBOL4 syntax/semantics). Snocone-specific
documentation lives somewhere in the corpus or one4all
trees — investigate at session start. The author/origin of
the Snocone language is relevant background; check
`programs/snocone/` for README files or `corpus/snobol4corpus/`
for documentation.

Key questions the manual should answer:

- Snocone include / module mechanism syntax
- Pattern matching primitives (LEN, SPAN, BREAK, etc.)
  and whether Snocone's are 1:1 equivalent to SNOBOL4's
- Procedure/function declaration syntax
- I/O model (read SNOBOL4 source from a file, write
  pretty-printed SNOBOL4 to stdout or another file)
- String operations (SIZE, SUBSTR, REPLACE, TRIM, DUPL)
- Whether Snocone has direct equivalents for SNOBOL4 keywords
  (`&FTRACE`, etc.) used in the BEAUTY suite

If Snocone is missing primitives BEAUTY relies on,
implementing those primitives in Snocone (or in the runtime)
is a prerequisite. That work would block BFY-3 onward
until the missing primitives are available.

---

## Cross-references

- **GOAL-SCRIP-BOOTSTRAP.md** — parent goal; Snocone leg of
  the bootstrap grid is advanced by this Goal's completion.
- **GOAL-CORPUS-LAYOUT.md** — proposes the eventual
  concept-first layout. Option C above (placing BEAUTIFY at
  `programs/beautify/snocone/`) anticipates this layout.
- **REPO-corpus.md** — current layout authority. If Option C
  is chosen, REPO-corpus.md doesn't need updating because
  `programs/<concept>/` as a top-level pattern is already
  consistent with what REPO-corpus.md sketches.
- **RULES.md** — self-contained demo exception applies; `.ref`
  files duplicated from BEAUTY into BEAUTIFY are sanctioned
  copies (not symlinks).
- The original `programs/snobol4/beauty/` corpus folder — the
  source material being ported.

---

## Active rung

**BFY-0 — Snocone runtime sanity check**

Begin next session by verifying Snocone can run a non-trivial
program end-to-end. If it can, proceed to BFY-1 (folder
location and skeleton). If not, this Goal is blocked on
Snocone runtime maturity; surface the blocker to Lon and
adjust the active rung in GOAL-SCRIP-BOOTSTRAP.md
accordingly.

---

## Authorship

This Goal file captures Lon's hand-off direction at the end
of a session that primarily produced GOAL-CORPUS-LAYOUT.md.
Per RULES.md, commits authored as LCherryholmes; substantive
direction comes from Lon, captured here for session continuity.

---

## Latent follow-ups (not gating BEAUTIFY)

- **BEAUTIFY-extended** — a future Goal where `beautify.sc`
  is generalized to also pretty-print Snocone source (its own
  language). Different self-host concept: `beautify.sc` reads
  its own Snocone source and emits it unchanged. New md5 gate.
  Tracked here so the naming distinction is clear when that
  work begins.
- **BEAUTY ports to other languages** — the same pattern
  (Icon implementation of SNOBOL4 pretty-printer, Prolog
  implementation, etc.) extends across the bootstrap grid.
  Once BEAUTIFY validates the Snocone leg, the same approach
  unlocks BEAUTYICON, BEAUTYPL, etc. Naming convention TBD.
- **Tracepoint config porting** — the `*_tracepoints.conf`
  files may have Snocone-specific equivalents or may carry
  over. Investigate in BFY-2.
