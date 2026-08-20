# FINDING — 2026-08-20 s186 (seat1, Opus 5; queue row `lon-include-root`, SUSPENDED BY RULING)

## ⛔⭐⭐⭐⭐ HEADLINE — THE SNOBOL4 SCORECARD RUNS THE ORACLE IN A DIFFERENT NAME-SEMANTICS MODE THAN SCRIP IMPLEMENTS

`scripts/scorecard_snobol4.sh` invokes the oracle as `sbl -b -d512m -i64m` for **13 of its 14 suites**. Per the SPITBOL v3.7 manual (l.1205, l.1386) **SPITBOL CASE-FOLDS NAMES BY DEFAULT** — *"lower-case alphabetic characters are changed to upper-case when they appear in names"* — and `-f` (l.6945, *"don't fold lower-case names to upper case"*) is the flag that turns folding OFF. `RULES.md` declares **SCRIP IS CASE-SENSITIVE**. So the harness grades a case-sensitive engine against a case-FOLDING oracle, on every suite except one.

**`beauty_self` is the only suite that passes `-bf`** — and `-bf` is `-b` + `-f`. The flag CLAUDE.md documents purely as a crash workaround (*"beauty.sno needs `-bf`; plain `-b` SIGSEGVs rc=139"*) is **also a language-semantics switch**, and beauty_self is therefore the only suite whose oracle obeys SCRIP's name rule.

### The witness is four lines
```
Shift       OUTPUT            =     'upper'                                      :(nxt)
shift       OUTPUT            =     'lower'
nxt         OUTPUT            =     'SURVIVED'
END
```
| engine | result |
|---|---|
| `sbl -b` (13 suites) | `ERROR 217 -- syntax error: duplicate label` |
| `sbl -bf` (beauty_self only) | `upper` / `SURVIVED` |
| SCRIP m3 | `upper` / `SURVIVED` |
| SCRIP m4 | `upper` / `SURVIVED` |

**SCRIP agrees with `-bf` in BOTH modes.** Under `-b` the oracle folds `Shift` and `shift` into one name; SCRIP does not. Any corpus program using two names differing only in case is graded against oracle behaviour SCRIP is required by RULES not to reproduce — as a false FAIL where the oracle errors, or as a silent wrong answer where the oracle merges two variables into one.

### It was masking a real result
While pricing the `lon-include-root` residue, a program whose includes resolved died `ERROR 217` at `demo/beauty/semantic.inc(16)`: label `shift` colliding with `Shift` in `demo/beauty/ShiftReduce.inc` — **a collision that exists only under folding**, since the two files define `Shift`/`Reduce` and `shift`/`reduce` respectively and nothing includes either twice (`-INCLUDE` is idempotent by name — proven by witness, both same-file and two-different-includers forms). Under `-bf` that wall vanishes entirely and the program advances to a genuine `ERROR 105` (exit action) in its own line 9. **An apparent "next wall" behind 24 programs was an oracle-flag artifact.**

⛔ **THIS IS NOT A DRIVE-BY FLIP.** `-b` → `-bf` is one word in the harness with corpus-wide blast radius and it wants the `fz3-flip` / `span-frame-flip` treatment: a full two-arm sweep, status-by-name, before any flip. Not attempted this session. It also interacts with the documented `-b` SIGSEGV class (stock `sbl -b` SIGSEGV'd once during this session on a beauty-family program), so the two arms may not even be comparable on every row. **Recommended as its own queue row.**

## ⭐⭐ THE `Trace` RULING WAS ANSWERED BY THE ORACLE, NOT BY TASTE — AND THE MECHANICAL RULE WOULD HAVE PICKED THE BROKEN FILE

`q-lon-include-root` asked which of two `Trace` variants is canonical. Measurement answers it: **`beauty_suite/trace.sno` is the ONLY case-fold match for the cited name and it is the BROKEN one.** Every path in the module ends `:(NRETURN)` while its line 6 sets `T8Trace = ''`:

| variant | line 6 | stock sbl |
|---|---|---|
| `beauty_suite/trace.sno` | `T8Trace = ''` | `ERROR 243 -- function result in nreturn is not name` |
| `demo/beauty/trace.inc` | `T8Trace = .dummy` | clean |

⛔ **THE GENERALISABLE LESSON: CASE-FOLDING IS NOT A SAFE MECHANICAL RULE FOR INCLUDE NAMES.** HQ-73's blessed "minimal normalization = case only" precedent (129 gimpel spellings) would have resolved this citation to the `ERROR 243` file. A name match is not a content match; the oracle must rule on the file, not the spelling.

## ⭐ AND THE MISMATCH WAS OUR OWN RENAME, NOT THE PROGRAM'S TEXT

`git blame` puts both citation lines at `e33dbdd4` (2026-03-23, *"revert 69fcdda: restore .inc extensions, rename inc/ -> include/"*). The pre-refactor text was `-INCLUDE 'Trace.inc'`; **the revert mis-restored it as `'Trace.sno'`.** The sibling line was never wrong: `'RANDOM.inc'` reads as authored, nothing anywhere in the corpus cites `RANDOM.INC`, and the file has been uppercase since the first import (`43989230`, `inc/RANDOM.INC`) — a DOS/Windows case-insensitive-filesystem assumption that only breaks on ext4. **Before editing a corpus program's text to match our tree, blame the line: the divergence may be ours.**

## RESIDUE, NAMED FILE-BY-FILE (the row's DONE-WHEN clause — complete, and independent of running anything)

Transitive resolver mirroring `sc_libpath` (program dir first, lib column as colon list): **35 of 99** programs carry unresolved includes; **24 turn on exactly two names** (`Trace.sno` 23, `RANDOM.inc` 21, both cited from `programs/include/5ivesAlive.inc`). The floor is **11 programs / 14 genuinely-absent names** — the s185 cursor said 10; it is 11 (`Extractor` cites `findname.sno` as well as `Trace.sno`):

`Extractor`(findname.sno) · `addMsg`(../modules/random/random.sno) · `atif`(portable.sno) · `blob`(BCP.sno,+) · `Blogzilla`(8 `../` forms; 5 absent, 3 exist only under `beauty_suite/`) · `build`(nmake.sno, external/directs.sno) · `mkblddir`(/home/build/bin/portable.sno) · `ssls`(host.sno) · `ssreorg`(host.sno, assign.sno) · `TZ`(transl8tweetish.sno) · `verify`(utility.sno, ss.sno, ini.sno)

## ⛔⛔⛔ AND THEN THE ROW WAS VOIDED BY A RULING — `corpus/programs/lon/` IS OFF LIMITS

Lon, in-chat s186, verbatim in substance: *"you should NEVER run this program. It should never be compiled even. These programs are off limits."* — confirmed: *"So we will not run those programs."* Landed as the **first entry under `RULES.md` ABSOLUTE RULES** (`.github a7fea108`). They are live network/database clients: `5ivesAlive.inc` pulls `curl.inc` + `sqlncli.inc` + `HTTP.inc`, and `rinky/Listen2*` are social-media API listeners.

⛔ **TWO CONSEQUENCES ARE LIVE VIOLATIONS TODAY, NOT HYPOTHETICALS:**
1. **`scorecard_snobol4.sh` EXECUTES the lon suite** via `run_one` (BOTH engines, m3 AND m4) on every SNOBOL4 scorecard run, and every board/bench script calling it inherits that. *Running the SNOBOL4 scorecard is currently an instance of the violation.* The harness-only skip is not landed — HQ must choose its form (drop the suite row vs a SKIP status preserving the weight column, since dropping changes META).
2. **`lon-include-root`'s landed harness half (SCRIP `fb2d505c`) points the wrong way under the ruling** — it is what took lon UNSCR 78 → 43 by *widening* what that suite can see and therefore run. Revert or fence: HQ's call. Untouched this session.

**ROW DISPOSITION: SUSPENDED, NOT DONE.** Its DONE-WHEN is unreachable by construction — the row exists to make more of these programs resolve and be SCORED, i.e. RUN. It should be RETIRED or REWRITTEN by HQ, not picked up by another seat. **The claim is deliberately left un-`done` so the row stays locked and no seat can `next` into it.** ⭐ **THE BOUNDARY IS SETTLED — ASKED AND ANSWERED IN-CHAT THE SAME SESSION:** *"We'll not run any programs/lon programs."* ALL of `corpus/programs/lon/`, not merely the `5ivesAlive` network family. The broad reading seat1 was holding is now the ruling, so the harness skip is the WHOLE SUITE and no seat need re-ask.

**DISCLOSURE:** seat1 ran four of these programs (`rinky/Extractor`, `rinky/Geo`, `sno/Dictionary`, `sno/ebnf`) BEFORE the ruling, while pricing the row. All four died at compile/load time (`ERROR 285` / `217` / `105`); none reached execution; no `curl`/`sqlncli`/`HTTP` path was entered. Recorded in the `RULES.md` entry itself, not only here.

## WATERMARK
Unchanged and untouched: corpus **m3 332/5 · m4 325/11 SKIP 1**, RT_OPT `-O0`. **This session touched NO compiler source and NO corpus file** — one doc (`RULES.md`) plus this FINDING. RULES step-4 `.s` regen not applicable.
