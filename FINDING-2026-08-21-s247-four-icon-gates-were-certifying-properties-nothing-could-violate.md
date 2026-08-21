# FINDING — s247 (seat1, Claude Fable 5): four Icon gates were certifying properties nothing could violate, and each rotted a DIFFERENT way

**Repo/commit:** SCRIP `0b1b7d4f` (pristine build, RT_OPT `-O0`), rung **N-0** of the re-chartered `GOAL-ICON-100.md`.
**One line:** Of the eleven `test_gate_icn_*` gates, **six** could not report anything about their own subject — four stuck green, two stuck red — and the rot mechanisms are distinct, silent, and each looks like a healthy gate.

## THE FOUR ROT MECHANISMS (this is the transferable part)

**(a) THE SURFACE WAS NAMED AS A FILE, AND THE FILE DIED.** `test_gate_icn_no_stack.sh` censused `src/templates/ src/emitter/emit_bb.c`. `emit_bb.c` has not existed for many sessions. `grep` prints *No such file* to **stderr**, keeps going with the surviving path, and the pipe to `wc -l` discards its exit status — so half the declared surface was absent and the gate said nothing. **A directory cannot be renamed out from under a census the way a file can.** Cure: the surface is a TREE, and its existence is ASSERTED (`exit 2` if missing). A gate that cannot see its subject must say so, never return OK.

**(b) THE SUBJECT CONSTRUCT WAS ABOLISHED, SO THE COUNT IS STRUCTURALLY ZERO.** `test_gate_icn_one_reg_frame.sh` counted `(uintptr_t)&(pBB|a0)->(value|counter|state)` — the mode-3 `bb_bin_t` box structs, **abolished 2026-06-02** by the template-revamp FACT RULE. The count is 0 and cannot be anything else. Worse, `test_gate_icn_var.sh` re-runs this gate as a **HARD** lock, so a hard lock in another gate was certifying nothing too. **A ratchet whose subject has been deleted reports success forever** — and it looks *healthier* than a live gate, because it never flickers.

**(c) THE DRIVER VARIABLE BECAME A NO-OP, SO BOTH ARMS OF AN A/B ARE ONE ARM.** `test_gate_icn_zcells_gva.sh` and `test_gate_icn_zk5_gva.sh` drive with `SCRIP_ICN_CELLS=1`. Z-1 (s230, `db728001`) made that variable **inert unless `SCRIP_ICN_LEGACY=1` is also set**: `lower_icon.c` stamps `icn_cells_graph=1` unconditionally otherwise. `zcells_gva`'s CHECK 1 therefore compared a baseline run against a "cells" run that was **the same configuration** and called the equality a correctness result. The gate was measuring the right arm — but by accident, and it would have gone on printing PASS if the cells arm had been switched off entirely.


**(d) THE GATE ENCODED AN ERA, AND THE COMPILER OUTGREW IT — SO IT IS STUCK *RED*.** `test_gate_icn_scan.sh` and `test_gate_icn_var.sh` have been RED at every pristine HEAD since s241, which recorded the fact honestly (INHERITED-CLAIM LAW, re-run on the baseline binary) and moved on. Every reason for the red is instrument rot:

- **Both bucket selectors name spellings the dump no longer emits.** `var` admits a program when `--dump-bb` carries `IR_ASSIGN`; the dump is JSON and spells it `"kind":"ASSIGN"` — no `IR_` prefix. `scan` admits on `GEN_SCAN`; **`IR_GEN_SCAN` no longer exists in `src/contracts/` at all** (it survives only as a stale row in `src/tools/emit_per_kind_audit.c`), and live scan boxes dump as `SCAN`/`SCAN_ENTER`/`SCAN_TAB`/`SCAN_UPTO`/`SCAN_MATCH`/`SCAN_MOVE`/`SCAN_FIND`. Both buckets therefore selected **N=0 out of 295 corpus programs**, making the floors (`scan` 31/11/11, `var` 62/12/22) **unreachable by construction**.
- **Six probes pinned defects the compiler has since fixed.** Four in `scan`, two in `var`. `upto_oneshot` pinned `"3"` for `"hello" ? every write(upto('l'))` and `find_oneshot` pinned `"2"` for `"banana" ? every write(find("an"))` — the ONE-SHOT answers, labelled in-gate as the "ORACLE GENERATIVITY" marker. Both are canonically `{*}` **generators** (`refs/icon-master/src/runtime/fstranl.r:237` `function{*} upto`), and SCRIP now emits the correct `3 4` and `2 4`. The other four (`any_dynamic_arg`, `eq_match_var`, `augop_concat`, `neg_unassigned`) carried policy **X34 = "m3/m4 must LOUDLY REFUSE"**; all four are now implemented natively and produce the oracle answer in every mode with no refusal, so the gate was failing *because the compiler improved*.

- **Neither bucket honored the XFAIL law.** `test_icon_all_rungs.sh` skips a program carrying a `.xfail` marker (30 exist) and reports XFAIL as its own column. The gate buckets had no such skip, so every known-unimplemented program landed in the "unexpected FAIL" tally against a HARD rule requiring **zero** of them — a second, independent reason the gates could not go green. Both buckets now apply the same marker test the suite uses: one law, two readers.

- **And the bucket graded programs that have no oracle at all.** `test_gate_icn_scan.sh` walks `find $CORPUS -name '*.icn'` **recursively** — 1,348 files across `jcon-ref/`, `jcon-compiler/`, `ipl/`, `parser/`, `repro/` — of which **1,048 carry no `.expected`**. Those were compared against the EMPTY STRING, so **a library file that prints nothing scored a PASS.** Of the 53 programs its GEN_SCAN filter admitted, 22 had no oracle, and skipping them removed **18 passes and 4 fails** (18+4 = 22, exactly). ⭐ **The honest pass count did not move — 44 − 18 = 26 — so no real program regressed**, which is the arithmetic that distinguishes re-deriving a floor from lowering a bar to buy a green. Floors re-derived 31/11/11 → **26/26/24** (m3 and m4 are large *tightenings*), with that reasoning written into the gate.

**A stuck-red gate is as uninformative as a stuck-green one, and it is more corrosive**: it trains every seat that reads the board to file the red as "pre-existing" and skip it — which is exactly what happened for six sessions. Fixes: both selectors accept the live spelling (and keep the legacy one), the two pinned defects are promoted to their true expectations, and the four X34 probes are promoted to **STRICT** — the strongest policy in the table, since a construct that answers *correctly* satisfies X34's safety property ("never a silent wrong answer") strictly better than one that refuses. ⛔ The floors were **not** touched: they date from the era when the buckets last worked, and editing a floor to manufacture a pass is the failure mode this rung exists to end.

A milder fifth case: `test_gate_icn_local_no_nv.sh`'s header prose names `[r12+off]` for locals and `[rbx+k*16]` for the GVA array, while its own greps already test `rsp` and `r9`. **r12 was freed of frame duty at s65 (R12-ERAD) and is today SNOBOL4's live DCAP/CAS top; the GVA base has been r9 since RC-5 (`bcac52c4`); rbx is the heap bump-frontier.** Prose that disagrees with its own code teaches the wrong register to every seat who reads the header before reading the body — and both retired spellings were still being quoted in goal-file prose as late as s246.

## ⭐ THE REAL FIND, FROM REPLACING (b) WITH A LIVE LOCK: 22 HAND-BUILT MEMORY BASES, AND THREE OF THEM BYPASS THE RE-HOMING MECHANISM

The FACT RULE says per-box RW lives in ONE frame at `[reg+off]`; the template rules say a box reaches storage through the ACCESSORS (`FR/FRQ/FRQB`, `ZRES/ZLOC/ZOPQ`, `XSAQ/XSAD`, `zone_ref`) and "never movabs a process addr, never rip-rel .data". The accessors are what make BINARY == TEXT **and what let a slot be RE-HOMED**: PF-1a..1d move a seam-crossed cell into the activation frame by changing what the accessor *answers*, not by editing call sites.

Census of string literals `"[rsp…"`/`"[rbp…"` built inside templates (comments stripped; `x86_asm.h` exempt as the sanctioned encoder; `strstr` search needles excluded): **22 sites** — `bb_call.cpp` 4, `bb_call_fn.cpp` 4, `bb_make_list.cpp` 4, `xa_flat.cpp` 7, `bb_define.cpp` 3.

**This is not a style count.** The arg-marshalling trio (`bb_call`, `bb_call_fn`, `bb_make_list` — the last is Icon's list constructor) hand-builds

```
x86("mov", "r8", ("[rsp + " + to_string(_.op_zread[i] + narg*16 + 0) + "]"))
```

— a **raw flat spine coordinate** — where `ZOPQ(k,w)` would answer with the operand's **activation-frame home** whenever PF-1c has re-homed it (`op_zread_xf[k]`). Those sites are structurally incapable of seeing a re-homed operand. That is the exact "flat ZLS coordinate vs re-homed cell" class the SNOBOL4 campaign spent 2026-08 killing (s129/s130 leaf cell, s177 seam-enterable leaf, s184 armed carve, s189 ALT choice record). It is latent today only because Icon's crossed operands are not yet re-homed — **and rung N-2 re-homes them by giving generators activation frames.** So this must be fixed as an N-2 prerequisite, not after it: converting the frames first would arm the defect.

The remaining sites are the pre-wire-stack crossing itself — `xa_flat.cpp`'s ICN-FR-2 wire header (`[kt-24]=γ`, `[kt-16]=ω`, `[kt-8]=caller`) and the CLASS-C chain prologue — which rung N-1 deletes outright, plus `bb_define`'s role-4 shim (SNOBOL4's, left alone).

## ⛔ THE Z-1 TRANSITION KILLSWITCH NO LONGER RESTORES A WORKING CONFIGURATION

`SCRIP_ICN_LEGACY=1` is documented at `lower_icon.c` as restoring "the s229-era routing **byte-exactly**". Measured this session on the ZK-5 witness (`test/icon/zk5_global_cells_zero.icn`): the default arm prints `2 / hello`; **`SCRIP_ICN_LEGACY=1` dumps core.** (`SCRIP_ICN_LEGACY=1 SCRIP_ICN_CELLS=1` — i.e. legacy routing with cells opted back in — is fine, which is the same routing as default.) Consequences: (1) the byte-identity completion criterion attached to Z-1 is **unverifiable at this HEAD**; (2) the killswitch's only remaining value is documentary; (3) this is direct evidence for the N-5 fold — a switch that cannot restore what it claims should be deleted, not preserved. ⛔ It also means no future seat should "repair" the two GVA gates by putting `SCRIP_ICN_CELLS=1` back: the arm it selected no longer exists as a separate configuration.

## WHAT LANDED

| gate | before | after |
|---|---|---|
| `no_stack` | surface named a deleted file; ceiling **127** vs measured **0** — 127 units of silent headroom | whole-`src` tree + surface assertion; ceiling **0** (zero-assert); `g_vstack` added to the pattern; **negative-tested by injection** |
| `one_reg_frame` | one vacuous grep (abolished structs) | LOCK 1 keeps it as a cheap zero-assert; **LOCK 2** = hand-built-base ratchet, ceiling **22**, target 0; **negative-tested by injection** |
| `zcells_gva` | CHECK 1 tautology; no-op driver var; missing `.expected` passed through the else-branch | default arm vs pinned `.expected`, missing oracle is a hard fail |
| `zk5_gva` | no-op driver var | drives the default arm (which IS the cells arm) |
| `local_no_nv` | header prose named r12/rbx | prose corrected to rsp-cells / r9-GVA, with the retirement history |

## ⭐ AND THE ONE LIVE INSTRUMENT SAYS THE DIRECTIVE IS ALREADY MET — WHICH SETS UP A RULING COLLISION AT N-2

`test_gate_icn_rbp_census_ratchet.sh` is the one Icon gate that was neither stuck nor vacuous, and it reports **A_ceremony=0, C_data=0, D_scratch=0, DRIFT=0 on all 23 benchmarks** — every number zero, which is precisely the shape a dead instrument produces, so it was checked by hand rather than believed: `queens.icn` compiles to **6,707 asm lines carrying 0 `rbp` mentions of any kind and 2,700 `[rsp` references**. The zero is real. **Lon's s204 directive — "ALL operands in EVERY BB accessed via RSP, NOT RBP" — is achieved on the benchmark surface**, C_data having gone 37,872 (s206) → 0, and the ceiling had quietly become 37,872 units of headroom. Lowered to **0** per the gate's own TIGHTEN instruction.

⛔⛔ **That ceiling now collides with rung N-2 by design.** N-2 gives Icon generators an RBP ζ-ACTIVATION frame (the SN4 R-4(b) shape) because Lon's **later** s242 ruling says a BB owns an RBP frame exactly where compile-time depth is unknowable — *"Icon's only dynamic-growth sites are generator procedures and co-expressions"*. The two rulings do not conflict (s242 names where the exception lives), but **encoding that exception in this gate is a relaxation of a zero-assert Lon personally directed, so it is his call, not a side effect of the rung that needs it.** The collision is left armed on purpose: leaving the ceiling at 37,872 would have let N-2 add frames with the instrument silent, which is the failure this rung exists to end. Proposed shape when the ruling is sought: a fifth class beside A/C/D/DRIFT — ζ-ACTIVATION refs in genuinely-dynamic graphs, counted separately, with C_data staying a zero-assert everywhere else.

## THE RESULT: TEN GREEN, ONE RED, AND THE RED IS NOW A CONVERSION TRACKER

Board at SCRIP `0b1b7d4f` (pristine, RT_OPT `-O0`, `pgrep scrip`=0, tree clean): **`no_stack` · `one_reg_frame` · `semicolon_required` · `tag_single_source` · `local_no_nv` · `zk5_gva` · `zcells_gva` · `rbp_census_ratchet` · `global_no_nv_m3` · `scan` GREEN; `var` RED.**

`var`'s red is the one worth having. With the four input laws aligned to the suite (XFAIL marker, `.stdin`, cwd, oracle-exists), its bucket walks **156 assignment-carrying programs** and reports **143 PASS / 13 unexpected FAIL (m3)**, and those 13 are a **strict subset of the suite's 16** — the three the suite also fails (`rung03_suspend_return`, `rung36_jcon_level`, `rung36_jcon_scan2`) simply carry no assignment and are not in the bucket. Before this session the same gate reported 28 failures against a suite watermark of 16 and could not have gone green at any compiler quality. **It is now a second, independent read on exactly the programs rungs N-2 and N-3 exist to fix, and it goes green when they do.**

Watermark re-proven on the same pristine binary either side of this work: **Icon m3 247/16/30, two agreeing runs**, binary mtime unmoved, canary rc=0 on all three arms — the sibling's `0b1b7d4f` MON-VARS commit is Icon-invariant.

## THE LAW THIS EARNS

**A gate's subject can be deleted out from under it, and every way that happens is silent.** Six mechanisms found in eleven gates: the surface moves (file-named census), the construct is abolished (structurally-zero count), the driver variable goes inert (A/B collapses to one arm) — all three print **PASS** — the gate's selector and expectations name an era the compiler has left (prints **FAIL** forever and gets filed as "pre-existing"); the gate re-implements the runner's grading contract and drifts from it (XFAIL markers, `.stdin`, cwd); or it grades programs that have no oracle, where "no output == no expectation" scores as success. None is caught by running the gate — they are only caught by *reading* it against the tree. So: **(1)** name a TREE, never a file, and assert the surface exists; **(2)** state the measured number and the date it was measured beside the ceiling — a ceiling far above the measurement is headroom for the defect, not safety margin; **(3)** **negative-test every gate by injection at the moment it is written**, and say so in the header. An injection test is the only thing that distinguishes "green because the property holds" from "green because nothing can violate it".

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Fable
