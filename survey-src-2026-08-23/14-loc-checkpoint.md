# LOC CHECKPOINT — the before-picture (Lon's request: "a starting checkpoint to see the difference when we end up smaller")

**Tree:** SCRIP `f110760f` (2026-08-23) · **Measured:** CEO s268 · **Instrument:** `wc -l` per directory over four categories — HAND = hand-written `.c/.cpp/.h/.hpp/.S/.inc` · GEN = generated parsers (`*.tab.c/.tab.h/*.lex.c/lex.*.c`) · GRAM = grammar sources (`.y/.l`) · OTHER = backends' `.cs/.java/.js/.il/.j/.wat/.mjs`. Re-measure the after-picture with the same command (recorded in survey git history) on the post-strip tree.

## THE SUMMARY (the numbers to diff)
| Aggregate | LOC |
|---|---|
| **Hand-written src/ (minus backends)** — the strip's target | **74,437** |
| Generated parsers (regenerable, not strip material) | 29,106 |
| Grammar sources (.y/.l) | 5,309 |
| backends/ (dormant, zero C — Phase-2 move) | 25,899 (+ jasmin.jar binary) |
| **Everything under src/** | **134,751** |

## PER FOLDER (files/LOC per category)
| Folder | HAND | GEN | GRAM | OTHER | TOTAL |
|---|---|---|---|---|---|
| contracts | 18/2,836 | — | — | — | 2,836 |
| driver | 18/4,032 | — | — | — | 4,032 |
| emitter | 4/4,615 | — | — | — | 4,615 |
| include | 4/126 | — | — | — | 126 |
| lower | 10/9,665 | — | — | — | 9,665 |
| machine | 5/156 | — | — | — | 156 |
| optimizer | 24/734 | — | — | — | 734 |
| parser/icon | 11/2,728 | — | — | — | 2,728 |
| parser/pascal | 2/26 | 3/5,367 | 2/1,024 | — | 6,417 |
| parser/prolog | 27/4,407 | — | — | — | 4,407 |
| parser/raku | 4/500 | 3/10,081 | 2/1,983 | — | 12,564 |
| parser/rebus | 4/547 | 3/4,794 | 2/713 | — | 6,054 |
| parser/snobol4 | 4/1,016 | 3/5,669 | 2/747 | — | 7,432 |
| parser/snocone | 4/448 | 2/3,195 | 1/842 | — | 4,485 |
| runtime (top) | 22/13,931 | — | — | — | 13,931 |
| runtime/builtins | 7/654 | — | — | — | 654 |
| runtime/core | 11/3,812 | — | — | — | 3,812 |
| runtime/rt | 23/4,555 | — | — | — | 4,555 |
| runtime/rtx | 25/5,048 | — | — | — | 5,048 |
| templates | 155/13,878 | — | — | — | 13,878 |
| tools | 5/723 | — | — | — | 723 |
| backends/driver/{js,jvm,net} | — | — | — | 15/9,261 | 9,261 |
| backends/runtime/{js,jvm,net,wasm} | — | — | — | 22/16,638 | 16,638 |

## Reading notes for the diff
- The interesting delta is the **HAND 74,437** line: the strip (Phase 1) and the reorg carves (Phase 2) act there. GEN shrinks only if grammars shrink; GRAM barely moves; OTHER goes to zero in src/ when backends/ relocates (Phase 2) — a −25,899 that is a MOVE, not a strip, and must be reported separately per FACT RULE (apples to apples).
- Known strip-scope inputs against this baseline: hq_C's verified carve list (22 files), ~343 never-set switches + guards, the platform-guard sweep (193 sites), the ζ-selector complex, dead xa_ arms, tools/ (723).
- Per-folder expectation shape (not promises): templates and runtime-top carry the largest switch/residue density; parser/prolog and parser/icon carry the dead test scaffolds; tools/ approaches zero.
