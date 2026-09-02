# FINDING 2026-09-02 (hq_B) — two committed generated parsers had been hand-pruned and could not be regenerated; both style200 oracles graded zero files while printing OK, and had three more holes behind the stale `-I` list

**Tree:** SCRIP `e01327e4` (parsers) + `a29ea1fd` (oracles) over `922cfaf4` (R5) · `RT_OPT=-O0` · MODE `TRIO` · ceo standup `oracles-and-generated-parsers-standup`, four items, all four landed. Wrap-up on Lon's 2026-09-02 checkpoint call.
**Re-run, never quote:** every number below has its command in the commit messages of the two hashes or in this file.

## Measured
| what | command | reading |
|---|---|---|
| objects after regenerating all 14 outputs vs the `922cfaf4` pristine build | `objdump -d -r` + every non-debug section, 267 objects | **266/267 identical**; `lex.rebus.o` differs |
| `lex.rebus.o` delta | per-function compare modulo layout (`fncmp`), `nm` | 24/24 pre-existing functions identical · **18 flex API functions added** (`yy_delete_buffer yyfree yylex_destroy yy_scan_{buffer,bytes,string} yy{push,pop}_buffer_state yyget_{debug,in,leng,lineno,out,text} yyset_{debug,in,lineno,out}`) — the set `pascal.lex.o`/`raku.lex.o` already export · 0 removed |
| `snocone_parse.tab.o` after deleting the three dead helpers from the `.y` | same | byte-identical to the committed object |
| C oracle over R5's 98 files, `STYLE200_BASE=46db4457` | `git diff --name-only 46db4457 922cfaf4 \| STYLE200_BASE=46db4457 xargs bash scripts/util_style200_oracle.sh` | **78 byte-identical · 0 BREAK/DIFF · measured 78 of 98** (14 headers, 6 not-a-TU) · rc=0 · 65 s |
| Y/L oracle at HEAD | `bash scripts/util_style200_oracle_yl.sh src/parsers/*/*.y src/parsers/*/*.l` | at HEAD `a29ea1fd` on a pristine tree: **9 byte-identical · 0 BREAK/DIFF · measured 9 of 9** (before the parsers commit landed it read 6 identical + the 3 deliberate cures as 1 BREAK + 2 DIFF — the instrument saying so is the point) |
| `strip_comments.py --check` | | 0 of 389 |
| flex-aware strip, round trip over the 4 committed lexers | `strip_flex(x) == x` | identity, 4/4; with 7–9 comments injected per file at every position class, the round trip returns the original 4/4; the blind C lexer over `raku.l` drops 143 of 299 lines |
| rung 13 (ARCH-PROLOG-BYRD-BOX-TRANSLATION § E) | `grep -rcw Term src` · `grep -cw resolve_choice src/runtime/builtins/resolution.{c,h}` | 0 · 0 — clause 2 now policed by `test_gate_term_wordref_ratchet.sh` |
| witnesses for the two regenerated parsers whose text changed most | smokes + parser fixtures | rebus 4/4 · rebus fixtures 15/15 · snocone 5/5 · snocone fixtures 67/67 |

## What was actually wrong (five defects, one class: an instrument answering a narrower question than it was read as)
1. **Both oracles' `-I` list** named `src/parser/`, `src/contracts`, `src/machine` — pre-reorg homes. Every TU failed to compile on both sides → SKIP → `OK · 0 byte-identical`. Cure: `scripts/lib_build_flags.sh` reads `RT_OPT/RT_INCS/ZCFLAGS/CBASE` from the Makefile (`make -pn buildinfo`) at call time and REFUSES rc=2 if any `-I` directory does not exist; both oracles REFUSE rc=2 when the measured count is zero.
2. **`objdump -d` without `-r`** cannot see a call retargeted to another function (the bytes are `e8 00 00 00 00` either way), and `-j .data -j .rodata -j .bss` never sees the `-fPIC` pointer tables in `.data.rel.local`/`.data.rel.ro`. Cure: `obj_fingerprint` = `-d -r` plus every non-debug section.
3. **`before.cpp`/`after.cpp` copies** give a C++ TU with global constructors two different `_GLOBAL__sub_I_<file>` symbols — `emit.cpp` read DIFF against `46db4457` for exactly that reason and for no other (2 fingerprint lines). Cure: both sides compiled under the file's own basename in two directories.
4. **Grammars generated as `out.tab.c`**: `pascal.y` and `raku.y` `#include` their own `X.tab.h`, so the generated parser found the committed header beside the generated one and compiled on **neither** side (2 of 9 SKIPped even after the `-I` cure). Cure: generate under the real `X.tab.c` name, identical on both sides.
5. **Two generated files were hand-edited**: `a98a7d24` (2026-06) excised `input`/`yyunput` from `lex.rebus.c`; `b9726d7b` removed three dead static helpers from `snocone_parse.tab.c`. Neither touched the source, so neither output could be regenerated — and the R5 proof ("8/8 grammar objects identical") compared regenerated-vs-regenerated, which cannot see this. Cured at the source: `%option noinput nounput` in `rebus.l` (the sibling form), the three helpers deleted from `snocone_parse.y`; `rebus.y`'s `../../ast/ast.h` repointed to `"ast.h"`.

⭐ **The general form, again:** a SKIP that exits 0, a DIFF whose only line is the instrument's own filename, a `-d` that cannot see a relocation. None of these announces itself; each was found by running the instrument on a case whose answer was already known.

## Not done, stated, routed to the GOAL-HQ-BEAUTIFY cursor
- `scripts/test_parser_snocone.sh` prints `SKIP scrip not found: …/scripts/scrip` and **exits 0** (`SCRIP="${SCRIP:-$HERE/scrip}"` points into `scripts/`; `corpus/tests/snocone/parser-fixtures` holds 0 files). A SKIP-as-success, the class RULES.md bans. Not fixed this sitting.
- `pascal.y`: bison reports `nonterminal useless in grammar: selector_list` (2 rules). Pre-existing; not touched.
- `test_gate_optbypass_watermark.sh` was not run by this seat (ceo re-pinned it at `2748100d` during this session; the binary is byte-identical to `922cfaf4` in every object except the 18 added rebus lexer functions).
