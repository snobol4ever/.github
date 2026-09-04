# FINDING 2026-09-04 hq_T — snocone and rebus ladder origins are DOUBLED because their rungs were absorbed as one file per rung

**Measured**, `corpus/tests/*/ALL.csv`, 2026-09-03 ~22:5x CDT box clock:

| language | rung-0 origin as recorded | shape |
|---|---|---|
| snobol4 | `ladder__rung00_hello` | correct |
| icon | `ladder__rung00_hello` | correct |
| prolog | `ladder__rung00_hello` | correct |
| raku | `ladder__rung00_hello` | correct |
| pascal | `ladder__rung00_hello` | correct |
| **snocone** | `ladder__rung00_hello__ladder__rung00_hello` | **doubled** (all 10 rungs) |
| **rebus** | `ladder__rung00_hello__ladder__rung00_hello` | **doubled** (all 11 rungs) |

Reproduce:

```bash
cd corpus/tests && for l in snobol4 icon prolog snocone rebus raku pascal; do
  printf '%-9s %s\n' "$l" "$(grep -o 'ladder__rung00[a-z0-9_]*' $l/ALL.csv | head -1)"; done
```

## CAUSE — not a naming slip, a recipe divergence

`util_build_master_suite.py:1236` sets `e.origin = "%s__%s" % (fam, e.name)`, where `fam` is the **source file
stem** and `e.name` is the entry's name inside that file. The five correct languages absorbed **one
`ladder.<ext>` file carrying all rungs as banner-delimited entries**, so `fam`=`ladder` and
`e.name`=`rung00_hello` compose to `ladder__rung00_hello`.

Snocone and Rebus instead absorbed **one file per rung**, named `ladder__rung00_hello.<ext>`. A bannerless
single-program pair is read as ONE entry whose name is the file stem, so `fam` and `e.name` are the SAME
string and compose to `ladder__rung00_hello__ladder__rung00_hello`.

This is exactly the recipe the umbrella row's own baton already wrote down and that these two absorptions did
not follow: *"one `ladder.<ext>` + `ladder.ref` at the suite root, rungs delimited by `<comment>------ <n>
<entry_name>` banners (a family is a SOURCE FILE, never a directory)."*

## IMPACT — real but bounded, and NOT a false board

- The ladder runners still grade these rungs correctly: `lib_ladder.sh` selects on `^ladder__rung0*([0-9]+)_`,
  which matches the doubled form, and the CSV `family` column is `origin.split("__", 1)[0]` = `ladder`, also
  correct. **Nothing is mis-graded and no number on SCORE.md is wrong because of this.**
- What it does break is **identity across the seven**: any cross-language tool that joins on the documented
  `ladder__rungNN_<slug>` origin shape gets 5 of 7. The umbrella row exists to make the seven consistent, and
  this is a consistency defect in the one column that names a witness.

## THE CURE IS NOT A `sed`, AND THAT IS THE POINT WORTH RECORDING

The origin column is a database attribute (`util_build_master_suite.py:117` says so explicitly), so renaming it
looks like a one-line `sed` on `ALL.csv`. It is not safe as one: the builder's own drop-detector
(`util_build_master_suite.py:1307-1321`) compares written origins against the origins known to HEAD's CSV, so a
rename presents as a **DROP plus an ADD** and REFUSES the next rebuild unless each old name is spelled out
under `--allow-drop-origin`. Renaming without that turns a cosmetic inconsistency into a builder refusal for
the next seat who touches either master.

**The correct cure**, for whoever holds the Snocone/Rebus ladder rows: re-absorb the rungs from a single
`ladder.<ext>`/`ladder.ref` pair under the sandbox recipe (`util_build_master_suite.py:31` — the builder writes
to shared corpus even on `--help`), or perform the rename through the builder with every old origin named in
`--allow-drop-origin`. Not by hand, and not while a board is reading the tree.

⭐ **The general form:** a naming convention enforced only by *how the input happened to be shaped* is not
enforced at all. Five languages got the right origin because their authors put the rungs in one file; two got
the wrong one because their authors put them in many. Nothing in the builder, and no gate, states the
`ladder__rungNN_<slug>` shape as a rule — so the shape survives on habit, and habit diverged the first time two
different people did the same job.
