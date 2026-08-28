# FINDING 2026-08-28 (hq_C) — ONE trailing space on any SNOBOL4 statement line is a SCRIP parse error; SPITBOL accepts it. 3 corpus programs are blocked by nothing else.

Raised by **seat02** (`m1-trailing-ws-may-be-new-defect`, from row `probe-consolidate-m1-and-small`) as "may be a previously-uncharacterized defect, could not find a `.github` citation by name". **Confirmed a real defect, oracle-graded, and sized.** seat02 was right that no citation existed — this file is it.

## The defect, minimally

A **single** trailing space (or tab) after any SNOBOL4 statement makes `scrip` refuse the whole file. SPITBOL compiles and runs it.

Ablation, five one-ingredient variants (`X = 1` / `OUTPUT = X` / `END`, oracle `/home/resources/x64/bin/sbl -bf`, both `< /dev/null`):

| variant | SCRIP | ORACLE |
|---|---|---|
| no trailing ws | rc=0, prints `1` | rc=0, prints `1` |
| trailing spaces on assignment line | **rc=1 parse error** | rc=0, prints `1` |
| **exactly one** trailing space | **rc=1 parse error** | rc=0, prints `1` |
| trailing ws on the `OUTPUT` line instead | **rc=1 parse error** | rc=0, prints `1` |
| trailing **tab** | **rc=1 parse error** | rc=0, prints `1` |

The passing sibling differs by exactly one space, so ASM-DIFF-FIRST step 1 is already done: **the witness is `no_ws` vs `one_sp`.** It never reaches codegen — this dies in the frontend, `no code generated`, identically in m3 and m4 (both rc=1).

## ⭐ Why nobody found a citation for it: the error is reported on the WRONG LINE

The offending trailing whitespace is on line N; the diagnostic names **line N+1**:

```
snobol4:2: error: parse error: syntax error     <- trailing ws is on line 1
snobol4:0: error: missing END statement
```

Confirmed on both placements (ws on line 1 → error "2"; ws on line 2 → error "3"). Anyone grepping citations or reading the diagnostic goes to look at a line that is *correct*, which is exactly why this sat uncharacterized. The `missing END statement` at line 0 is a knock-on of the first error, not a second defect — `END` is present in every witness above.

## Blast radius — measured, not estimated

```bash
cd corpus && find . -name '*.sno' | wc -l                                   # 1293 total
find . -name '*.sno' -exec grep -lP '[ \t]+$' {} + | wc -l                  # 27 carry trailing ws
```

27 of 1293 carry trailing whitespace, but trailing ws on a `*` comment line is harmless. Narrowing to a **non-comment, non-blank** line leaves **8** files. Causation proven per file by stripping (`sed 's/[ \t]*$//'`) and re-counting parse errors — **all 7 non-probe files improve, and 3 go to ZERO**:

| file | parse errors as-is | stripped |
|---|---|---|
| `packages/snobol4/csnobol4_suite/genc.sno` | 2 | **0** |
| `packages/snobol4/csnobol4_suite/bench.sno` | 2 | **0** |
| `packages/snobol4/csnobol4_suite/lexcmp.sno` | 2 | **0** |
| `packages/snobol4/snoflake_suite/lexical-comparison.sno` | 2 | 1 |
| `packages/snobol4/csnobol4_suite/trim1.sno` | 2 | 1 |
| `packages/snobol4/csnobol4_suite/trim0.sno` | 2 | 1 |
| `packages/snobol4/dotnet/1brc.sno` | 2 | 1 |
| `probe/m1/m1_trailing_ws.sno` (seat02's witness) | 2 | 0 |

**Three real third-party programs are blocked by trailing whitespace and nothing else.** The other four have it as one of several blockers, so fixing this is necessary-not-sufficient for them. The concentration in `packages/` is the point: this is imported real-world code, which is where trailing whitespace naturally lives. Hand-written corpus is clean because seats write it clean.

⛔ **Do not "fix" this by stripping the corpus.** The oracle accepts these files; SCRIP must too. Editing the witnesses would launder a live frontend defect into a corpus-hygiene chore and destroy the evidence — the transcription-kills-provenance class (`RULES.md:105`). The 8 files above are the regression set, and they must pass **as they are on disk**.

## Scope note

SNOBOL4 only, as measured. Whether the Icon/Prolog/Raku/Pascal frontends share the lexer path that does this is **not measured here** and is not assumed — if the cure lands anywhere shared, SHARED-NODE VERDICT SCOPE binds and every frontend reaching that node needs grading.

## Reproduction

```bash
cd /home/claude_C/corpus
printf '                  X              =  1 \n                  OUTPUT         =  X\nEND\n' > /tmp/one_sp.sno
/home/claude_C/SCRIP/scrip /tmp/one_sp.sno < /dev/null   ; echo "SCRIP  rc=$?"   # rc=1, parse error
/home/resources/x64/bin/sbl -bf /tmp/one_sp.sno < /dev/null ; echo "ORACLE rc=$?" # rc=0, prints 1
```

Row minted: `snobol4-trailing-whitespace-parse-error`. Witness already in the tree at `corpus/probe/m1/m1_trailing_ws.sno` with an oracle-verified `.ref` (`1`) — it is one of the 23 files seat02 could not convert, and under the now-landed XFAIL format it converts as an XFAIL today (see `FINDING-2026-08-28-hq_C-the-xfail-gap-three-seats-were-blocked-on-had-already-landed.md`).
