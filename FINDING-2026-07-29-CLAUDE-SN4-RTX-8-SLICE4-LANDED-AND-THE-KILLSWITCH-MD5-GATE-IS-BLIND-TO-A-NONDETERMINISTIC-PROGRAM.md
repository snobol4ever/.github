# FINDING — s217 (2026-07-29, Claude) — RTX-8 SLICE 4 LANDED, AND THE KILL-SWITCH MD5 GATE REPORTED A FALSE VIOLATION BECAUSE ONE PROGRAM IN THE SUITE IS NON-DETERMINISTIC

**Session:** s217 · **Ladder:** `GOAL-SNOBOL4-RTX.md` · **Contract:** `ARCH-SNOBOL4-RTX.md`
**Rung:** RTX-8 MATCH SINKS, slice 4 — `rt_match_ctx_restore` · **Gate:** `SCRIP_RTX_MATCH`
**Baseline `.so` md5 (pristine, session start):** `8793847346ea254344129da85953b12a` · **Post-port:** `9fd91f67b711e7e8124814d625631331` · **RT_OPT=`-O0`** (no `-O2` directed)

---

## ✅ LANDED: `rt_match_ctx_restore` IN ASM

`src/runtime/rtx/rtx_match.S`, behind `RTX_GATE(match, …)`; C body renamed `c_rt_match_ctx_restore` at `src/runtime/builtins/gen_runtime.c:145` in the same commit. **ZERO templates touched ⇒ no `.s` regen owed** (phase-1 by construction). 10 instructions vs the C fallback's 20, both counted from the OBJECT (`objdump`), not estimated.

Also landed: **`scripts/util_rtx_count_syms.sh`** — the pre-port half of step 0(d), closing the scope gap the ladder itself named ("generalizing it is an open rung"). `util_rtx_arm_census.sh` derives its symbol list from `RTX_FUNC(...)` ∩ dynamic table and therefore **cannot see a symbol that is still pure C**; this one takes names on the command line and **fails loudly on a typo** rather than silently reporting zero (the phantom-family failure mode). Machinery lifted verbatim from s216 so its three defect fixes are inherited, not re-earned: hidden counters (so `inc [rip+cnt]` is legal in a `.so`), an `inc`+`jmp *ptr` thunk that clobbers EFLAGS only and so forwards any signature, and constructor arming conditional on `libscrip_rt.so` being present in THIS process (the two-process destructor-zeroing defect).

---

## ⭐⭐ THE FINDING: A KILL-SWITCH MD5 SWEEP CANNOT GRADE A NON-DETERMINISTIC PROGRAM, AND THE SUITE CONTAINS ONE

The ON/OFF byte-identity sweep over all 316 `crosscheck/*.sno` reported **exactly one MOVER: `160_pat_alt_inner_gen_resume`.** Read at face value that is a kill-switch violation and the port must be reverted (the s216 discipline). **It is not one.** Re-run four times per arm:

| arm | run 1 | run 2 | run 3 | run 4 |
|---|---|---|---|---|
| gate **ON** | `62dfbab3` | `62dfbab3` | `6e137e45` | `6e137e45` |
| gate **OFF** | `627a34ed` | `62dfbab3` | `6e137e45` | `6e137e45` |

**Three distinct hashes on the OFF arm alone, and the two ON hashes BOTH appear on the OFF arm.** ⇒ `160` is non-deterministic run-to-run, and the instability is **on the pure-C path**: gate OFF *is* the C fallback, i.e. byte-for-byte the code that ran before this session. **An asm port cannot cause instability in the arm where its asm does not execute.**

⛔ **CONSEQUENCE FOR EVERY PRIOR RUNG'S HEADLINE CLAIM.** s215 and its predecessors record "kill-switch **ON == OFF BYTE-IDENTICAL over all 315 programs, both modes**" as a passed gate. That gate, as practiced, is **one run per arm per program**. Against a non-deterministic program a single-run comparison returns PASS or FAIL *by coin flip* — so the recorded pass was luck, not evidence, and a future session that draws the other way will revert a correct port and hunt a bug that is not there. **The claim is not wrong about the other 314; it is unfounded about this one, and nothing in the gate's output distinguishes the two cases.**

⭐ **THIS IS THE SAME SHAPE AS s216'S SILENT VALUE-PROBE, ONE LEVEL UP.** s216 minted "prefer a HARD probe when a silent result reads two ways." Here a *differing* result reads two ways — "the gate leaks" or "this program never had a stable answer" — and the byte-identity gate has no arm to tell them apart. ⇒ **FIX THE GATE, NOT THE PORT: run N≥4 per arm and compare the SET of hashes, or carry an explicit non-determinism quarantine list that the gate prints.** Comparing sets would have passed `160` immediately and for the right reason.

⚠ `160` is already a known-bad program (fails BOTH modes, differently — m3 rc=0 wrong output vs m4 rc=134, s214's "divergence in MANNER"). **Its non-determinism is a NEW fact and is not the same defect as its failure.** Not chased this session; it belongs to the latch/EVAL family rungs.

⚠ **Suite size reconciled while chasing this:** `find` gives **316** `.sno`, the crosscheck grades **315**. Cause: `coverage_sno_nodes.sno` has no `.ref`. s215's "315" is correct; my sweep counted the un-refed one. Named so the next session does not re-derive it.

---

## ⭐ WHY THIS TARGET WAS SAFE WHERE `rt_cap_push` WAS NOT — 0(f) DISCHARGED *BEFORE* THE ASM EXISTED

s216 reverted a correct, oracle-exact, byte-identical port because it **never committed** (57,578 entries, 57,578 bails, 0 commits) and minted step 0(f). 0(f)'s tool is post-port by construction — it needs a `c_*` edge to count — so a pre-port arm check is a source-reading obligation. **Here the source discharges it outright: the C body is three unconditional stores. ZERO arms, ZERO calls, no early return, no predicate. There is no cold arm to bail to, therefore no bail edge, therefore ENTRIES ARE COMMITS BY CONSTRUCTION.** A straight-line body is the one shape where 0(f) is provable in advance.

Confirmed after the fact by the s216 instrument on its **first prospective use** — `pattern_bt.sno` m3:

| symbol | entries | bailed→C | COMMITS | verdict |
|---|---|---|---|---|
| **`rt_match_ctx_restore`** | **500,001** | **0** | **500,001** | asm handles all |
| `rt_cap_match_begin` | 500,001 | 0 | 500,001 | (other slice) |
| `rt_str_alloc` | 500,006 | 1 | 500,005 | (control, other family) |
| `rt_gcheap_alloc` | 1 | 1 | **0** | **VACUOUS — re-confirms the s216 flag** |

**Step 0, all six checks, re-measured on the tree this session, not cited:**
- **0(a)** live definition + **two real template call sites** (`bb_match_head.cpp:89`, `bb_match_release.cpp:77`).
- **0(b)** name round-trips byte-identical — plain ASCII, no Greek codepoints, no truncation.
- **0(c)** ⭐ **run ON THE OBJECTS, then on the DYNAMIC TABLE — both tiers, because they answer different questions.** Objects: `Σ`/`Σlen` = `B` in `stmt_exec.o`, `g_cap_gen` = `D` in `pattern_match.o` ⇒ all three GLOBAL, linkable from `.S`. Dynamic table: all three present with DEFAULT visibility, **`g_cap_gen_next` correctly ABSENT (it is `hidden`)** — which is what proves the instrument discriminates rather than merely agreeing. ⇒ **`@GOTPCREL` mandatory on all three**; a direct `[rip+sym]` would bind A DIFFERENT VARIABLE via copy relocation from a `-no-pie` executable with no diagnostic at any stage (s214). Idiom copied verbatim from the existing `.Ldc_str` code.
- **0(d)** 500,001 entries at `LT(N,500000)`; **250,001 at half the literal ⇒ EXACTLY 2.000×**, scaling proven at two counts.
- **0(e)** zero `.S` hits pre-commit ⇒ not already ported.
- **0(f)** discharged by structure above, confirmed 500,001/0/500,001 by the tool.

---

## ⛔⛔ NO SPEED NUMBER, AND THE REFUSAL IS THE HONEST RESULT — NOT A GAP

This is an **ERADICATION rung (RTX-12), not a speed rung**, and the FINDING says so rather than quoting a ratio — the **RTX-7 precedent**, where the ladder's own row says "if ever done, it is a correctness/eradication rung … and the FINDING must say so rather than quoting a speed number." Two independent reasons, both measured:

1. **THE WINDOW IS UNGRADEABLE.** `pattern_bt.sno` self-times at **205 ms** against the harness floor `MIN_MS=800` ⇒ `BOGUS-WINDOW`. Quoting a ratio here would be the RTX-0b/0c/0d mistake a **fifth** time. ⚠ And the short window is visibly unstable on its own: halving the loop literal took 205 ms → **65 ms**, a **3.15× swing for a 2× workload**, while the CALL COUNT scaled exactly 2.000×. **The count is linear and the clock is not** — at this window size the clock is measuring warmup, not work.
2. **THE CEILING IS BELOW THE NULL FLOOR.** 20 → 10 instructions × 500,001 calls, all L1-resident single-cycle stores and GOT loads ⇒ order of 1 ms against 205 ms, i.e. **≲0.5%**, versus the ladder's established **±3% null floor**. A *perfect* port wins less than the noise. Same arithmetic that bounded RTX-7 at 0.58%.

⭐ **THE CHEAP FIX EXISTS AND IS NAMED, NOT DONE: `pattern_bt.sno` has exactly one scalable `LT(N,500000)` literal, so ~4× (2,000,000) clears 800 ms** — unlike RTX-0f's `json.sno` problem, where the defer count tracks input STRUCTURE and not bytes so scaling the input is awkward. **If any MATCH-family rung ever needs a graded window, scale this literal — do not author a new grammar.** Still owed before any ratio is quoted off it: checksum PREDICTED IN ADVANCE at two pass counts, interleaved rounds, round 1 discarded (hugepage warmup), 3-arm `ON/PRISTINE` per ARCH §7 step 4.

---

## ✅ GATES — ALL RE-DERIVED FRESH THIS SESSION

- **Falsification TWO-SIDED, with a HARD probe per s216:** `ud2` planted on the commit path ⇒ gate **ON: rc=132 (SIGILL)**, no output — the asm provably executes; **SAME BUILD, gate OFF: rc=0** with correct output (`result: 500000`, `W: ccccddddaaaa`) — the switch provably routes to C. A value probe was not attempted: s216's rule is to prefer the hard probe when a silent result would read two ways.
- **Revert of the probe verified THREE ways** (s212's interrupted-revert lesson): `grep -c ud2` = 0 · source md5 back to `72fd89a6…` · **and the `.so` relinked to the SAME md5 `9fd91f67…` as pre-probe** — a bit-identical rebuild, the strongest revert proof available.
- **Crosscheck BOTH MODES, gate ON:** m3 **311/4** · m4 **311/2** · **DIVERGE=2**. **Identical at gate OFF**, and the FAILURE SETS match line-by-line (`test_case`, `140`, `141`, `160` on m3; `test_case`, `160` on m4; DIVERGE `140`/`141`). **This is exactly the s215 watermark, re-proven on the tree — zero movers.**
- **Kill-switch byte-identity ON vs OFF, md5 of stdout+rc, all 316 programs m3: 315 identical, 1 unfalsifiable** — see the FINDING above; that one is `160`, non-deterministic on the C path.
- **Unit batteries, both arms:** 21/21 + 36/36 + STR differential 8426/0 ⇒ ALL PASS.
- **Smokes:** hello-world matrix 6/6, `ROWS_DRIFT=0`.
- **`test_gate_no_hidden_global_in_emitted.sh`: GATE CLEAN.** The `g_pcall_top` WARN is the **known comment-only near-miss** in `bb_call_proc_staged.cpp` (s214) — pre-existing, not this rung's.
- **`test_gate_rtx_inventory_live.sh`:** runs; 26 ARCH §5 names still advisory-flagged as absent from the linked runtime (the standing phantom advisory, untouched here).
- **No-regression for the C-side rename ONLY (⚠ NOT asm evidence — ARCH §7 step 2b):** Prolog **189/0/0**, Icon **4/0** + m4 tracked 4/4. Per s165 these batteries do not move under an asm probe and citing them as asm gates would be a FALSE CLAIM.

**SCORE, derived from the tree at close:** 29 gated `RTX_FUNC` symbols · 32 `c_*` fallbacks · 12 family gates · 2,509 asm LOC across `src/runtime/rtx/*.S`. ⚠ These exceed s214's recorded 24/22/11 partly because the **parallel ICON-RTX ladder** has been landing symbols in the same directory (s211 `eb81508d`) — **the count is shared state between two ladders and must be re-derived, never inherited.**

---

## ⚠ NOT RUN, NOT CLAIMED

**beauty** · **15-demo board identity** · the **3-arm `ON/PRISTINE` rail** (deliberately — see the refusal above; a pristine arm would grade a 205 ms window) · **m4 kill-switch md5 sweep** (m3 only; m4 crosscheck itself was run and is identical ON/OFF) · Snocone/Raku/Rebus/Pascal batteries. `handoff_status.sh` is the push truth — not this block.

## ⛔ FLAGGED, NOT FIXED (inherited, unchanged)

`rtx_abi.inc` lines 10-15 still carry the **stale r12 pin** that ARCH §2 corrected at s205 ("r12 is FREE — NOT A PIN"). Directive is to fix it in the same commit that first uses r12; **this port does not use r12** (it touches `r10` scratch only), so the correction is still owed and still sitting inside the executable half of the contract.

## NEXT RUNG

1. **FIX THE KILL-SWITCH GATE** — N≥4 runs per arm, compare hash SETS, print a quarantine list. It is cheap, it is static, and every future rung's headline claim depends on it.
2. **RTX-0f** still blocks any MATCH/defer ratio — but note the `pattern_bt.sno` literal-scaling route above is far cheaper than a new grammar.
3. **THE DEFER LATCH FIX** (own rung, graded on `140`/`141`, never on json) — and `160`'s newly-measured non-determinism is a lead for that same family.
4. Remaining RTX-8 MATCH sinks. ⛔ **`rt_match_enter` still NOT first** despite its identical 500,001 count: multi-arm and call-heavy. Equal heat, opposite portability.
