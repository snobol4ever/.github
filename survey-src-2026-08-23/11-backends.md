# Survey 11 — src/backends (34 text files + jasmin.jar, ~26.0k LOC) (agent report, condensed verbatim)

## 1. INVENTORY
| Sub-tree | Files·LOC | What it is | Verdict |
|---|---|---|---|
| driver/net/ | 8·~3810 | Standalone C# SNOBOL4 tree-walk interpreter (scrip-interp) incl. Reflection.Emit BoxFactory | **DEAD — does not compile**: .csproj includes ../../runtime/boxes/*.cs which does not exist anywhere; IByrdBox/MatchState/Spec/ByrdBoxExecutor/bb_capture/bb_atp/bb_dvar undefined in any .cs. Zero scripts/Makefile invoke it |
| driver/jvm/ | 6·~3850 | Parallel Java tree-walk interpreter | **DEAD — does not compile**: imports package `bb` (~28 classes) which exists nowhere. Zero references |
| driver/js/ | 1·1629 | Pure-JS tree-walk interpreter, self-contained | **DEAD** — one-line require-path bug (sno_runtime.js is in sibling dir); test script computes the fix in a comment, never applies it; closest to salvageable |
| driver/wasm/ | 1·30 | README-only honest placeholder | DEAD (stub by design) |
| runtime/js/ | 3·2604 | bb_boxes.js/sno_engine.js/sno_runtime.js — complete Byrd-box JS runtime | DEAD (complete library, no live caller) |
| runtime/jvm/ | 5·4564 | bb_boxes.j/SnoRt.j etc (Jasmin asm) for scrip's own --target=jvm output; ~20 scripts assemble via jasmin.jar | DEAD (target flag hard-rejected upstream) |
| runtime/net/ | 9·5151 | bb_boxes.il/SnoRt.il MSIL + 3 standalone C# ABI utilities | DEAD (--target=net rejected; no ilasm/mono in container) |
| runtime/wasm/ | 5·4319 | bb_boxes.wat + TWO overlapping SNOBOL4 WASM runtimes + prolog_runtime.wat + sno_host.mjs; bb_boxes.wat header cites src/runtime/boxes/bb_*.c which no longer exists | DEAD |
| jasmin.jar | 128KB | vendored third-party JVM assembler | dependency of a dead path |

**Single git provenance: entire tree landed in ONE commit 12bed48a "GMR-6: backends/ — consolidate dormant non-x86 trees" (2026-06-02), a pure git mv — already labeled dormant by its mover, zero commits since.** driver/net + driver/jvm trace to repo's first commit (713c581b) with no intervening edits.

## 2. LIVE REFERENCES (everything pointing in)
- Makefile:47-48 JASMIN/SCRIP_CC_BIN; :493-527 run-jvm/run-net targets → call `scrip -jvm/-net` — **confirmed broken by execution: `./scrip -jvm f.sno` → "cannot open '-jvm'"** (flags don't exist in scrip.c's parser).
- scrip.c:811,850 parses --target= and lists "x86, jvm, js, wasm" in usage, but :1591-1593 rejects non-x86 ("[SMX] --target=%s removed"). Confirmed live by execution.
- emit.h:89-109 BB_PLATFORM_* enum; emit.cpp:25,195,204 hardcode X86 both modes — permanently-dead branches.
- **templates/xa_prologue.cpp (105) + xa_epilogue.cpp (26) are the ONLY files left in the live template set with PLATFORM_JVM/JS/NET/WASM branches** (commit d6c593cf scrubbed the other 12 — these two were missed). xa_prologue's dead JS arm hardcodes a broken absolute require path.
- ~52 scripts reference backends/ (smokes/rungs/installers) — all blocked upstream by the --target rejection; none in the blocking gate set.

## 3. OVERLAP with sibling repos
- snobol4jvm = mature independent **Clojure** implementation (README: 1,896 passing tests). No code in common.
- snobol4dotnet = "SNOBOL4.NET", separate mature C#/.NET compiler. No code in common.
- **Zero overlap, zero lineage either direction.** src/backends is SCRIP's own abandoned first-pass multi-target attempt (sprint tags M-NET-INTERP-*, SJ-6, SJ4-JVM-*, SN4-NET-*).

## 4. RECOMMENDATION (announcement-aware)
- Announcement risk is naming confusion: "SCRIP also has a JVM/.NET backend" would read as true and is false.
- **Move entire tree out of src/** to e.g. archive/backends-dormant/ or top-level legacy/ via git mv (history intact), preserving driver/runtime split.
- **Strip the two live-code footholds in the same motion**: delete PLATFORM_* dead branches from xa_prologue.cpp/xa_epilogue.cpp (finishing d6c593cf), delete run-jvm/run-net Makefile targets + JASMIN plumbing. The ~52 scripts move with the tree or die.
- Do NOT extract into snobol4jvm/snobol4dotnet (independent, further along; this code wouldn't compile as a starting point).
- Suggested announcement sentence: "SCRIP explored JVM/.NET/JS/WASM output early on; those experiments are archived, unmaintained, and superseded by the independent sibling snobol4jvm/snobol4dotnet projects."
