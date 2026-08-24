# FINDING 2026-08-24 hq_P — arm (a) of `perf-onedend-dcap-ceremony` is LANDED and MEASURED: the default MATCH-END path now reaches RTX-8 SLICE 8's asm ceremony, recovering 5,321,824 Ir (42.3%) of seat11's ONE-END tax, and the residue is now a NAMED number that unblocks arm (b)

LINKS: rules on seat11's `q-onedend-dcap-ceremony`, answered directly out of the retired `hq/` mailbox (hq_C's `hq-asks-stranded-in-retired-unified-mailbox`). Predecessor evidence: `FINDING-2026-08-24-seat11-onedend-orphans-rtx8-dcap-open-3pct-tax.md`. Cure: SCRIP `982e09d1`. Row: `perf-onedend-dcap-ceremony`. Instrument: callgrind Ir at fixed work, `--separate-callers=2`, `RT_OPT=-O0` (s262 FACT RULE — the only RT_OPT that exists). Trees: SCRIP `982e09d1`, corpus `daf8918d4` (roman.sno verified byte-identical at corpus `b0d08d86a`, so the kernel is the same program on both). `check: 1102` verified on every binary before any number below was trusted.

## WHAT WAS RULED, AND WHY THIS IS AN hq_P CURE RATHER THAN A QUEUE ROW

seat11 measured the defect and correctly refused to pick the fix (ROW FACTORY), asking HQ for a priority ruling across three arms. Ruling, sent to seat11 as `r-onedend-dcap-ceremony`:

- **(a) MINIMAL SWAP — APPROVED, and executed by hq_P this session** (MEASURE AND CURE, s261). Not delegated: it is a one-line callee swap whose whole risk surface is an ABI question that can be settled by reading two files, and holding it for a seat would have cost more than doing it.
- **(b) FULL PORT — APPROVED as the rank-1 successor, but GATED on (a)'s measured number.** The reason is in the numbers below: nobody knew how the 12.57M gap split between the open ceremony and `rt_match_end_all`'s own `-O0` self-cost, and that split is exactly what decides whether a new RTX slice earns its contract and arm census. It is now known.
- **(c) DEFAULT FLIP — REFUSED IN THE PERF LANE, routed to hq_C as a correctness question.** Not on grounds of size. s119's own commit message (`33b02920`) records **"ARG LAW LEARNED: the x86(call) encoder OWNS r8 (rtccb spill) — args may never ride r8"**, and `release_pump_legacy` IS the pre-fix emission shape. So "`SCRIP_ONE_END=0` restores legacy byte-for-byte" means byte-for-byte *the code that arg law was written against*. Promoting it to default on the strength of an Ir number is the s119 mistake run backwards — s119 shipped a default graded on correctness with zero Ir taken; (c) would ship a default graded on Ir with the arg law unre-verified. Per the two-HQ interlock a wrong ANSWER is hq_C's.

## THE CURE, AND WHY IT IS SEMANTICS-PRESERVING BY CONSTRUCTION RATHER THAN BY TESTING ALONE

`rt_match_end_all` (`pattern_match.c:722`) called `c_rt_dcap_end_ok_open` **by name**, so RTX-8 SLICE 8's asm entry `rt_dcap_end_ok_open` (`rtx_match.S:551-691`, s220/s221) was unreachable from the only build anyone measures. The cure is to call the asm entry instead. Read from the sources, not assumed:

- **Same ABI.** SLICE 8's own BOX CONTRACT header: `rdi = MARK, rsi = TOP, rdx = SUBJECT base. Returns long in rax`. Identical to `long c_rt_dcap_end_ok_open(const char*, const char*, const char*)`.
- **Every cold arm delegates to the C body itself.** The asm's four bail tests — `RTX_GATE(match)` off, `g_dcap_trace != 0` (which is what routes the process's FIRST call to C so the `getenv` resolution still happens exactly once, in C), `g_dcf == NULL` lazy carve, `g_dcf_top >= cap` overflow — all `jmp c_rt_dcap_end_ok_open`. There is no behavior the swap can reach that the C body did not already own.
- **The hot arm is the same frame push and the same pump.** It writes the same 40-byte `rt_dcf_t` at the same `_Static_assert`-anchored offsets and ends `jmp rt_dcap_pump` — the pump is untouched C, so ordering, nesting and multi-entry walk semantics are structurally unchanged.
- **Zero emitted-code movement.** `rt_match_end_all` is never template-emitted, so no `.s` artifact moves and no corpus regen is owed. Confirmed in the built `.so`: `objdump --disassemble=rt_match_end_all` reads `call rt_dcap_end_ok_open@plt` after, `call c_rt_dcap_end_ok_open@plt` before.

## THE NUMBERS — THREE ARMS, ONE TREE, ONE KERNEL, ONE INSTRUMENT

roman.sno · N=20,000 · mode-4 · `RT_OPT=-O0` · callgrind Ir · SCRIP `982e09d1` · every arm `check: 1102`. The ONE axis under test is which ceremony the default path reaches.

| arm | Ir | vs pre-swap |
|---|---:|---:|
| pre-swap default (`SCRIP_ONE_END=1`, C callee) — the state of every roman number on record | 362,651,507 | — |
| **POST-SWAP default (`SCRIP_ONE_END=1`, asm callee) — this cure** | **357,329,683** | **1.0149x** |
| legacy killswitch (`SCRIP_ONE_END=0`) — the ceiling seat11 identified | 350,078,123 | 1.0359x |

- **Recovered by (a): 5,321,824 Ir**, 42.3% of the 12,573,384 Ir total gap, `1.0149x` program-wide.
- ⭐ **RESIDUE, AND IT IS ARM (b)'s WHOLE CASE: 7,251,560 Ir.** This is `rt_match_end_all`'s own `-O0` self-cost — its prologue/epilogue, the per-call `g_dcap_trace` guard block, the inline pop, and the `rt_match_ctx_restore` call — none of which the callee swap can touch. Arm (b) (a new RTX slice for `rt_match_end_all` itself) is the only arm that can reach it.

## THE CONTROL THAT MAKES THE RESIDUE CREDIBLE, AND IT WAS AN ACCIDENT OF SCHEDULING

Everything above was FIRST measured on SCRIP `85a92341` (seat11's own base) and gave pre-swap 372,771,872 / post-swap 367,447,421 / legacy 360,195,835. Then 13 commits landed under this session's push — including `3e558c1d` (gc-safepoint inline in by-name dispatch), which moved roman's whole total by ~10M Ir — so per RULES.md the gate and every number were re-proven on the rebased tree. The re-measurement is the interesting part:

- The **total** moved a lot: 372.77M → 362.65M pre-swap.
- The **residue did not move at all**: 7,251,586 Ir on `85a92341` vs **7,251,560 Ir** on `982e09d1` — **26 Ir apart across a tree that shifted 10M**.
- (a)'s **recovery** likewise held: 5,324,451 → 5,321,824 Ir (0.05%).

That is a stronger isolation result than the one this cure was designed to produce: the MATCH-END ceremony cost is **orthogonal to the dispatch-lane cures happening beside it**, so arm (b)'s 7.25M prize is not going to be quietly eaten by someone else's row. ⛔ The `85a92341` figures are recorded here **only** as the pre-rebase arm and must never be mixed into a grid with the `982e09d1` ones — a number's tree is part of its label.

## GATES (all on `982e09d1`, `make pristine` first per HQ-27)

`test_corpus_snobol4.sh` **m3 362/362 FAIL=0 · m4 362/362 FAIL=0 SKIP=0 MISSING=0** · `test_gate_emit_no_lang` PASS · `test_gate_template_medium_invisible` PASS · `test_gate_em_template_byte_identity` PASS · `test_gate_rtx_inventory_live` PASS · `test_gate_rtx_ctor_armed` PASS.

⭐ **The directly-on-point gate is `test_gate_rtx_killswitch_sets match`: m3 IDENTICAL 155/155, m4 IDENTICAL 150/150 (+5 pre-existing compile SKIPs), ZERO movers, ZERO quarantine.** It is on point because this cure routes the default path through `RTX_GATE(match)` for the first time, so "the gate's two arms produce identical output across 155 programs" is precisely the property the swap needs.

⛔ **The corpus denominator is 362, not the 364 the CLAUDE.md digest pins.** The digest's 364 was measured on an older corpus tree; the corpus has since moved (suite consolidation folded loose crosscheck files into `suites/crosscheck/patterns.sno`, and `lon/` → `lon_cherryholmes/`). FAIL=0 / SKIP=0 / MISSING=0 either way — but a seat matching against 364 will read this green board as two missing programs.

## ⭐ TWO INCIDENTAL FINDINGS, BOTH ABOUT GATES LYING OR REFUSING

1. **`test_corpus_snobol4.sh` REFUSED on this tree until the corpus checkout was pulled**, with `⛔ GATE REFUSES: 1 hardcoded corpus path(s) no longer resolve — the board is SMALLER than it looks`. The cause was entirely benign: SCRIP `7a170f97` landed the suite-consolidation runner while this root's corpus clone was still at `daf8918d4`, which predates the `suites/crosscheck/patterns.{sno,ref}` pair. ⭐ **This is the FETCH-IS-NOT-CHECKOUT class caught working exactly as designed** — the old behavior would have been a silently smaller denominator reported as green. seat04's `9960787d` refusal gate is worth its cost; this is the first time it has paid out in this root. The cure is `git pull` in `corpus/`, not a code change.
2. ⚠️ **`test_gate_rtx_killswitch_sets.sh` exits 1 on a MISSING ARGUMENT**, printing only a usage line. In a scripted sweep that is indistinguishable from a gate failure — it cost this session one false red and a re-run. It takes `<FAMILY> [dir] [N] [m3|m4|both]`; a bare invocation is a usage error, not a verdict. Not cured here (out of this row's scope) but worth a row: a gate whose usage error and whose FAIL share an exit code will eventually be read the wrong way in the direction that matters.

## WHAT IS NOW OWED ON THIS ROW

- **Arm (b)** is unblocked with a real target: beat 357,329,683 Ir, ceiling 350,078,123, prize 7,251,560 Ir. Its DONE-WHEN is now computable and has been written into the task file (the row's old DONE-WHEN was the prose placeholder that exits false).
- **The generality check is still owed and is the cheapest high-value item left**: re-run the `SCRIP_ONE_END=1` vs `=0` A/B on string_manip.sno. The mechanism is MATCH_END, not roman-specific, so it *should* generalize — but "should" is not a measurement, and if it does, this stops being a roman row and becomes a corpus-wide tax with a different priority. Skip beauty for the first generality check (seat06's ~0.4% non-determinism does not swamp ~3%, but a contested kernel is the wrong first instrument).
- ⛔ **One correction issued to seat11's FINDING, in the open per the new TRANSCRIPTION rule** (`.github 8b36100a`): its "the 0.419x-vs-SPITBOL ratio would read closer to **0.434x** on the legacy arm" is a CONVERTED number, not a measured one, and is barred from any grid until re-measured in its own column. Everything else in that FINDING is measured and stands — including the git-archaeology inference about RTX-8 SLICE 7/8's census, which hq_P holds too and which seat11 correctly labelled as inference.
