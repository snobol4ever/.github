# FINDING — `bench_correct` is 8/8: the last residue program was behind an OPT-IN flag, not a defect

**Seat:** hq_C (HQ-CORRECTNESS) · **Mode:** FLEET-16 · **Date:** 2026-09-04 ~16:20–17:30 CDT box clock
**Row:** `icon-bench-correct-suspend-residue` (rank 0, ASSIGNED:hq_C by ceo CEO-230) · **Tree:** SCRIP `0d482dac9` (= origin/main `59589ee97` + one line) · corpus `34cf6472d` · .github `dea6d593` · RT_OPT `-O0` · incremental `make`

## THE CLAIM

`honest_icon_correctness.sh` (the eight `corpus/benchmarks/icon/` programs, mode 4, each compared against a live `iconx` run of the same source and input) reads **8/8 IDENTICAL** with **0 CRASH / RUNAWAY / HANG**. It read 7/8 with `geddump` CRASH from 2026-08-30 (seat09) through the baseline run this sitting. The cure is one line: `SCRIP_ICN_N2_SELFREC` is now DEFAULT-ON and `=0` is the killswitch (`src/templates/x86/x86_asm.h`, `icn_genframe2_selfrec()`), the same shape ceo gave `SCRIP_ICN_GENFRAME2` at s283.

## THE MEASUREMENTS (every number below was produced this sitting by the command beside it)

| arm | command | before (`59589ee97`) | after (`0d482dac9`) |
|---|---|---|---|
| the row's DONE-WHEN | `honest_icon_correctness.sh` | 7/8 — `geddump` CRASH SIGABRT after 0 lines (GENHOST reserve bomb) | **8/8 IDENTICAL** (concord 1345 · deal 17000 · geddump 12568 · ipxref 1230 · micsum 2 · queens 16653 · rsg 5000 · tgrlink 3239 lines) |
| geddump by hand, m3 | `./scrip geddump.icn < geddump.dat` | bomb, rc=134, 0 bytes | 322839 bytes, md5 `ca9c831d28cc` == `iconx` |
| geddump by hand, m4 | `--compile --target=x86` → gcc → run | (harness: CRASH) | 322839 bytes, md5 `ca9c831d28cc` == `iconx` |
| killswitch | `SCRIP_ICN_N2_SELFREC=0 ./scrip geddump.icn` | — | the old GENHOST bomb, rc=134 |
| control: emission | `--compile` `.s`, flag unset vs `=1`, all 8 benchmarks | — | 7 byte-identical (`cmp`); only `geddump` differs (256 lines) |
| Icon master board, same binary A/B | `board_icon_master.sh` with `SCRIP_ICN_N2_SELFREC=0` and with default | — | **IDENTICAL both arms**: entries=749 · run-graded m3 595 / m4 595 of 596 · ast 153/153 · watermarks held |
| Icon smoke | `test_smoke_icon.sh` | — | m3 15/15 · m4 15/15 |
| SNOBOL4 blocking board (shared-node arm) | `bash scripts/test_corpus_snobol4.sh` (the Makefile's own form) | — | **✅ GATE OK: m3 PASS=1711 FAIL=0 · m4 PASS=1711 FAIL=0 SKIP=0 · MISSING=0** (master total=1749, xfail 61 both modes, xpass 0; the runner rewrote its own SCORE.md row in the same run) |

The three flag sites (`bb_call_proc_staged.cpp:693`, `emit.cpp:2922`, `x86_asm.h:875`) all gate on `icn_gen_is_selfrec(...)` — the depth-banking push, the H+40 depth slot, and the `(N2_SELFREC_SLOTS-1)` reserve multiplier fire only for a generator whose own graph calls itself by name. That is why the seven non-recursive benchmarks and the whole 749-entry master are byte-for-byte / count-for-count unmoved: the default changes nothing except for programs that bombed before.

## WHY IT SAT AT 7/8 FOR A DAY WITH NO DEFECT LEFT ANYWHERE — THE LESSON

The residue row (`icon-n2-recursive-generator-per-activation-storage`) closed on 2026-09-03 (seat06) the moment `coexpr-stack-leaves-the-compacting-gc-heap` landed. Its DONE-WHEN was **`SCRIP_ICN_N2_SELFREC=1 ./scrip geddump.icn < geddump.dat` → rc=0 with output** — and hq_P had repaired it into exactly that form on 2026-08-29, for a good reason: the previous form armed `SCRIP_ICN_GENFRAME2=1`, which ceo had meanwhile made default-on, so it graded the UNARMED program and could never be met by any cure. The repair proved the *mechanism*. This row's DONE-WHEN grades the *default path*. Both criteria were correct for their rows, and the gap between them is where geddump sat CRASH for a day.

⭐ **A flag-armed DONE-WHEN is a proof that the mechanism works, never that the product does.** When a row's criterion arms a flag, the closing seat owes one more line: either flip the flag on (and grade the consumers) or mint the flip as the consumer's next step. seat06's closing ledger did check for a stricter oracle (found `jcon_tests/geddump.std` pairs with a different `.dat`, correctly rejected it) — it checked the *oracle* and not the *flag*, which is the natural blind spot: the flag was in the criterion they were told to run.

⭐ **The general form, same family as RULES.md § A SIGNAL REACHABLE BY TWO CAUSES THAT NAMES ONLY ONE:** "the row went green" is reachable by "the product is right" and by "the instrument armed what the product does not", and the receipt names only the first. The cheap check for any green that arms an env var: run the criterion once more with the var unset.

## ⭐ RE-PROVEN ON THE MERGED TREE, BECAUSE A REBASE VOIDS THE EARLIER ARM

Everything above was measured at `59589ee97` + the cure. Pushing meant rebasing onto **11 new upstream commits**, and the REBASE-BASELINE COROLLARY says a before/after pair is a measurement only while both arms are the same tree plus the one change. So the whole verdict was re-taken at SCRIP `f36f3fff9`, on a rebuilt binary (`scrip` md5 `5211673a36ff`, `libscrip_rt.so` md5 `af11597cef15d5` — the `.so` hash moved, the driver's did not, which is the expected shape for a templates-only change):

| arm | merged-tree reading |
|---|---|
| `honest_icon_correctness.sh` | **8/8 IDENTICAL**, same eight line counts |
| `test_smoke_icon.sh` | m3 15/15 · m4 15/15 |
| `test_corpus_snobol4.sh` | **m3 PASS=1714 FAIL=1 · m4 PASS=1714 FAIL=0 SKIP=1**, ⚠ see below — the one m3 red is not mine |

⚠ Worth noting what those 11 commits contained, because two of them touch the very instrument this row grades on: `board_icon_master.sh` had a **double-zero `grep -c` bug cured and its floors re-pinned**, and a separate commit added a **stale-binary rc=2 refusal to every suite runner**. Both landed between my baseline and my push. Neither changed the verdict, but a seat who had skipped the re-measure would have been quoting a board from an instrument that has since been repaired — the reading would have been right by luck, not by method.

⚠ **AND THE SNOBOL4 BOARD CAME BACK WITH `m3 FAIL=1` UNDER A `✅ GATE OK`.** Attributed before trusting the push, not after: the entry is `ladder__rung04_replacement_expression_value` (`simple_output_276`), it fails **identically with `SCRIP_ICN_N2_SELFREC` forced off and on**, and it is a *deliberate* red — corpus `74e0336d0`, landed by another seat at 17:03 today, whose own commit subject reads *"snobol4 ladder rung04 (pattern match + replace): FORMS complete, 5/5 witnesses, 1 deliberate red"*. The witness is `OUTPUT = (T ? "ADO" = "FUSS")`; SCRIP answers `FATAL lower_snobol4 (GZ#5 subset): pattern element not in the SN4-PAT subset`, SPITBOL answers `MUCH FUSS ABOUT NOTHING`. A rung witness minted ahead of its cure, which is the ladder's normal practice. Not mine, and the pre-rebase board (1711/1711 FAIL=0 both modes) plus the same-flag A/B are the two arms that say so.

⛔⭐ **BUT THE REASON IT READS `✅ GATE OK` IS A DOCUMENTED CONTRACT THAT HAS OUTLIVED ITS PREMISE, AND I AM ROUTING IT RATHER THAN CHANGING IT.** `test_corpus_snobol4.sh` exits non-zero on `FAIL4` only; its header says *"Mode-4 gate (hard). Modes 2+3 informational. Reinstated 2026-06-08."* **Mode 2 was DELETED**, and mode 3 is now the primary native correctness mode — `test_smoke_icon.sh`'s own header says exactly that, and the SHARED-NODE VERDICT SCOPE law asks for FAIL=0 *per mode*. So the blocking set's largest board cannot currently fail on a mode-3 regression: a real m3 red and a deliberate m3 red are the same green. ⭐ The mitigation the script already has is real and worth keeping — the count is printed **inside** the ✅ line, so it cannot hide from a reader — but a number that only a reader can act on is not a gate. **This is a ruling, not a seat's edit**: today's ladder practice of minting a witness ahead of its cure depends on m3 being non-blocking, so tightening it without a home for deliberate reds would break a working method. Routed to ceo (and hq_T, whose lane the suite standard is).

## ⛔⭐ A FOURTH REGEN SCRIPT WAS NEEDED, AND THE THREE NAMED BY LAW REPORTED "NO CHANGES" WHILE A STALE ARTIFACT SAT ON DISK

RULES.md item 4 names three regen scripts for a codegen-touching session: `util_regen_benchmark_s_artifacts.sh` · `util_regen_demo_s_artifacts.sh` · `util_regen_prolog_bench_s_artifacts.sh`. All three were run in that order and all three correctly reported **no changes** — they cover `corpus/benchmarks/snobol4/`, the demos, and the Prolog benchmarks.

⛔ **`corpus/benchmarks/icon/` is none of those, and it carries 20 checked-in `.s` artifacts — `geddump.s` among them.** It is maintained by a fourth script, `update_icon_bench_asm.sh`, which the handoff list does not name. Run for `geddump.icn` alone: `total=1 updated=1`, and the diff is exactly the cure — `FN__gedload`'s carve `sub rsp, 3072` → `sub rsp, 25600` (the `N2_SELFREC_SLOTS` multiplier) and `n00102_proc_gen_α` losing its `lea rdi, [rip + .S1]` / `call rt_bomb@PLT` / `ud2` stub for a real generator box. Committed corpus `293e99e8d`.

⭐ **THE SHAPE, and it is this file's own family:** three instruments each answered *my* population honestly, none of them answers *the* population, and "no changes" three times reads as "nothing to do". The artifact policy is stated by DIRECTORY KIND (Lon s269: artifacts beside benchmarks and demos), while the handoff step is written as a LIST OF SCRIPTS — so a benchmark directory that grows a maintainer the list never learned about goes stale silently, and the only signal is a `.s` in git that disagrees with the compiler nobody diffs. **A rule stated as a policy and executed as a list decays at exactly the gap between them.** Routed to ceo: RULES.md item 4 should name the population (every benchmark and demo tree) and let the four scripts be its implementation, or name the fourth script.

## WHAT DID NOT HAPPEN

- No `make pristine` (Lon 2026-09-03: a landing grades on an incremental `make`). One binary graded every arm above: `scrip` md5 `5211673a36ff`, `out/libscrip_rt.so` md5 `6b857bdaa33b` — the templates are in the `.so`, which is why the driver's hash is unchanged across the flip.
- The SNOBOL4 entry `arbno_pos_rpos_branch_81` (origin `probe_passthru__ptw_min_defer2_hang`) hangs identically with the flag on and off, `timeout 10` both — pre-existing, flag-independent, an xfail on the master, not a regression. ⚠ It cost this session ~14 wasted minutes because the first board run inherited `TIMEOUT=600` from a neighbouring baton's DONE-WHEN: that is the PER-ENTRY knob, not the whole-board wrapper, so every hanging entry costs ten minutes each. The Makefile's own form (`bash scripts/test_corpus_snobol4.sh`, per-entry default 10s) is the honest cadence, and a DONE-WHEN that exports `TIMEOUT=600` around this runner should be read as a mistake, not a setting.
- The SNOBOL4 entry `arbno_pos_rpos_branch_81` (origin `probe_passthru__ptw_min_defer2_hang`) hangs identically with the flag on and off, `timeout 10` both — pre-existing and flag-independent, an XFAIL on the master, not a regression. ⚠ Running the board with `TIMEOUT=600` (the per-entry knob, not the whole-board wrapper) as several batons' DONE-WHENs do makes every such entry cost ten minutes; the Makefile's own form (`bash scripts/test_corpus_snobol4.sh`, per-entry default 10s) is the honest cadence.
