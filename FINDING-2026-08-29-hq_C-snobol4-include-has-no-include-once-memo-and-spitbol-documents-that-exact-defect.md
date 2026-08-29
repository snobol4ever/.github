# FINDING 2026-08-29 hq_C — `-INCLUDE` has no include-once memo, so a diamond in the include graph redefines every label; SPITBOL's manual documents this exact defect as the reason include-once exists

## THE DEFECT

`src/frontend/snobol4/snobol4.l` implements `-INCLUDE '…'`, `-INCLUDE "…"` and `-COPY '…'` as **three near-identical actions** (`:56`, `:76`, `:97`), each of which resolves the file, pushes a flex buffer, and reads it. **None of the three records that the file was already read.** So when a file appears twice in an include graph — directly and again transitively — its text is compiled twice and every label in it is a duplicate.

**MINIMAL WITNESS — three files, and it reproduces the whole class:**

```
A.INC:  L<TAB>OUTPUT = "in A"<TAB><TAB>:(L_END)
        L_END
B.INC:  -INCLUDE "A.INC"
w.sno:  -INCLUDE "A.INC"
        -INCLUDE "B.INC"
        <TAB>OUTPUT = "main"
        END
```

| arm | result |
|---|---|
| `sbl -bf` | `in A` / `main`, rc=0 |
| `csnobol4` | `in A` / `main`, rc=0 |
| **`scrip`** | ⛔ `duplicate label 'L'` · `duplicate label 'L_END'` · *"no code generated"*, rc=1 (both modes) |

## ⭐⭐ THE ORACLE'S MANUAL DOCUMENTS THIS DEFECT BY NAME, AND PRESCRIBES THE CURE

`spitbol-manual-v3.7.txt` (the `–COPY`/`–INCLUDE` reference section, p.173) — quoted rather than paraphrased because the second sentence is the whole implementation:

> "**To avoid compilation errors due to duplicate labels, SPITBOL will only include a particular file once.** That is, if files a.inc and b.inc are both included in a program, and both a.inc and b.inc attempt to include file c.inc, only one copy of c.inc will be read. In situations where you deliberately wish to include multiple copies of a file, simply append a blank after the file name. **SPITBOL remembers only the "trimmed" names of files included so far, so the comparison with the blank-padded name will fail, and the file will be included again.**"

So the specified semantics are precise and slightly quirky, and the quirk is load-bearing:
1. **Include-once**, keyed on the file name **as written in the directive** — not the resolved path.
2. The memo stores the **trimmed** name; the lookup compares the **raw** name. A trailing blank inside the quotes therefore misses the memo and re-includes deliberately.
3. **`–COPY` is a synonym for `–INCLUDE`** and shares the memo.

⭐ **AND THE ESCAPE HATCH IS REAL, NOT FOLKLORE — BOTH ORACLES IMPLEMENT IT.** `-INCLUDE "A.INC"` followed by `-INCLUDE "A.INC "` (one trailing blank) includes twice on **both** `sbl` and `csnobol4`, each then reporting duplicate labels. That is the documented behaviour working as designed: the second inclusion is the user's explicit request, and the duplicate-label error is the user's own problem. **A cure that keys the memo on the RESOLVED PATH would silently break this**, because both spellings resolve to the same file — the trimmed-vs-raw distinction is the mechanism, not an implementation detail to be tidied away.

## THE CENSUS — 18 FIXTURES, MEASURED, AND ALL 18 ARE BLOCKED BY IT TODAY

The Gimpel library (`corpus/packages/snobol4/snoflake_suite/gimpel/`) is **written for a compiler that includes once**: each `.INC` declares its own dependencies with `-INCLUDE`, so any fixture pulling two libraries with a shared dependency forms a diamond. Computed over the transitive include closure of every fixture:

**18 of the suite's fixtures have a diamond.** Worst offenders by duplicate-inclusion count: `gimpel-bnorm-inorm-image-line` (+27, `REVERSE.INC` pulled **9** times), `gimpel-poker-game` (+14), `gimpel-print-width-functions` (+8), `gimpel-stone-game` (+7), `gimpel-real-math-functions` (+6, `DEXP.INC` **5** times).

⛔ **ALL 18 CURRENTLY FAIL m3 — AND I CHECKED RATHER THAN ASSUMED, WHICH CORRECTED MY OWN FRAMING.** At the start of this sitting only **13** of the 18 reached the duplicate-label wall; the other **5** (`gimpel-numeric-random-functions`, `-poker-game`, `-random-string-functions`, `-real-math-functions`, `-stone-game`) died **earlier**, on a parse error — a *separate* defect (trailing-dot real literals; see the sibling FINDING, now cured). After that cure landed, **all 5 advanced to the duplicate-label wall**, so the census is now uniform: **18 of 18 blocked here.** ⭐ I was one keystroke from writing "all 18 are blocked by include-once" before measuring it, and it would have been false at the time of writing and true an hour later — the kind of claim that is impossible to audit afterwards because it eventually becomes true.

**Against the row's partition** (`snoflake-suite-scrip-only-gap` SF-0): **3 of the 18 are in set (c)**, the honest defect surface — `gimpel-array-functions`, `gimpel-combinatorics`, `gimpel-sorting-functions`. The other 15 fail `sbl` too and sit in set (b) (dialect/superset work, SF-7-approved). ⛔ **That does not make include-once a 3-fixture fix.** Set (b) membership says *sbl's answer differs from the snoflake `@expect`*; it says nothing about whether SCRIP can compile the program at all. Include-once is the **first wall for all 18** — the 15 cannot even reach their dialect gap until it falls. Expect a **+3 m3 gain and 15 fixtures unblocked**, not +18.

## ⛔ NOT LANDED — BLOCKED ON THE NO-NEW-GLOBALS LAW, AND THE ASK IS ROUTED

A memo set is irreducibly **new file-scope mutable state** (a name array plus its count). RULES.md § *NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION* covers this exactly — *"file-scope mutable state, pinned VA slot, exported cell, **parallel array**, or equivalent"* — and requires the ask to be an in-chat ⛔ banner naming the variable, type, owning file, purpose, and why registers/the stack cannot carry it.

⭐ **I looked for a way to need no new state and there is none.** The include machinery's existing state cannot serve: `inc_dirs[]`/`n_inc` is a *directory search path* (appending each resolved include's directory), and `incl_start_stack[]`/`incl_stack_depth` is a **stack popped at EOF** — a memo must outlive the pop, which is the entire point. Reusing either would be a semantic abuse that happens to compile.

⛔ **AND THE STACK IS SPECIFICALLY THE WRONG SHAPE HERE, WHICH IS WHY THE RULE'S USUAL ANSWER DOES NOT APPLY.** The law's standing alternative is *"linkage/state ride registers and the stack"*. That answer is for **runtime** state. This is **compile-time** state whose defining property is that it must survive every buffer pop to the end of the compilation — a stack discipline is precisely what it must not have.

**The proposed cure, so the ask is concrete:** one static name array + count in `snobol4.l`, consulted by a single helper that all three include actions call (which also removes the existing triplication rather than making it a quadruplication). Store trimmed, compare raw, per the manual. `-COPY` shares the memo.

## ⭐ THE REUSABLE LESSON — A LIBRARY THAT DECLARES ITS OWN DEPENDENCIES IS EVIDENCE ABOUT THE COMPILER THAT COMPILED IT

Every one of the ~70 `.INC` files opens by including what it needs. That style is **only writable against an include-once compiler** — without the memo, no library author could let two headers share a dependency. So the corpus itself encodes the semantics, and the diamond count (18 fixtures, up to 9 inclusions of one file) is a measurement of how thoroughly its authors relied on it. ⛔ **We read this corpus for three sessions as "gimpel fixtures fail" without asking why a library would be written this way if it could not work.** The shape of third-party source is testable evidence about the toolchain it was written for, and it is free.

## RECEIPTS
- Witness, oracle triangulation, escape-hatch check: this document, reproducible from the three files quoted above.
- Census script: transitive closure over `-INCLUDE` edges in `corpus/packages/snobol4/snoflake_suite/gimpel/*.INC`.
- Row: `snoflake-suite-scrip-only-gap` (hq_C, open). Sibling FINDING: trailing-dot real literals (landed this sitting).
