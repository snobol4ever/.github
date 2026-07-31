# FINDING 2026-07-31 (PL s162) — PROLOG HAS **ZERO** ZD ARMING; THE NON-POPPING LADDER'S RUNG ORDER **INVERTS** FROM SNOBOL4'S; THE WHOLE-LANGUAGE GAP IS **EIGHT IR KINDS**

**Session:** s162 · `GOAL-PROLOG-BB.md` · Lon PIVOT directive, this session: *"Climb the ladder to NON-POPPING FORTH-style RSP ZETA stack with a C-style RBP used occasionally only when absolutely necessary. See what SNOBOL4's sessions have been up to. Then do the same."* Then, after the first measurement pass: *"All your choices. I'm with you on this."*

**SCRIP baseline:** `417add3c` (unmodified at session start; HEAD of the day). Build `-O0` throughout — **no `-O1`/`-O2` used or sought**, no Lon directive for one requested or given.

**WATERMARK:** SCRIP `src/emitter/emit.cpp` (+1 line, the `SCRIP_ZD_GAP` instrument — LOCAL, push state NOT claimed here per RULES.md (a); `scripts/handoff_status.sh` run live is the only ground truth) / corpus `<none>` / `.github` `this finding + cursor`.

---

## ⭐⭐ THE HEADLINE — "DO THE SAME AS SNOBOL4" IS THE ONE THING THAT CANNOT BE DONE, AND IT IS WRONG BY MEASUREMENT

SNOBOL4's head rung is **verbatim this directive** (`FINDING-2026-07-31d` names it: *"NON-POPPING FORTH-style RSP ζ stack with a C-style RBP used occasionally only when absolutely necessary"*). So this is a continuation, not a new idea, and the obvious move is to copy their rung order: widen `zd_wl_kind` one kind at a time (their ZD-2a…2m → ZD-7 → ZD-8).

**MEASURED: that path reaches 6% of Prolog and stops.**

| | SNOBOL4 (positive control) | Prolog |
|---|---|---|
| ZD armed nodes | **32,159** (60 programs) | **0** (250 programs, 65 compiling) |
| graphs | — | **1137** |
| jmp-entry graphs (never reach `zd_plan`'s run loop) | minority (EVAL/CODE/PAT$ blobs) | **1072 = 94.3%** |
| graphs with zero carve | many (`flat_all_zd`) | **0 of 1137** |
| total whole-graph carve | shrinking | **1,356,320 bytes** |

**Prolog is 100% on the LEGACY FLAT CARVE.** Not Gen-1 FC (SNOBOL4's second corpse, the one that pops). Gen-2 ZD — the ratified non-popping model — **has never touched Prolog at all.**

⭐ **AND THE ζ LADDER IN THIS GOAL FILE HAS BEEN REFINING THE CORPSE.** s158→s161 (RSP-F-4, ZETA-FB-1/2/3) are all about *which register the whole-graph carve is based on* — `x86_fb_pinned()`, `emit_rec_pin()`, `emit_heap_fb_adopt()`, `op_flat_disp`. Every one of those predicates is a property of a carve that the non-popping model **deletes**. That work is correct on its own terms and it closed real land mines; it is also, with respect to this directive, **motion along an axis the destination does not have.**

---

## ⭐⭐ THE TWO GATES, STACKED — BOTH FALSIFIED BY INJECTION, NOT INFERRED

`zd_plan` (emit.cpp:1868) is the ONE execution-order walk. Prolog is stopped twice:

**GATE A — STRUCTURAL (1072 of 1137 graphs, 94%).** Every Prolog *predicate* graph is `jmp=1 gen=1`; `zd_plan` early-returns on `g_emit.flat_jmp_entry` **before the run loop**. Measured via the existing `SCRIP_LP_DIAG=1`: `palindrome.pl` = `proc_palindrome$2F2 jmp=1 gen=1 region=688` · `proc_reverse$2F2 jmp=1 gen=1 region=464` · `proc_$reverse_$2F3 jmp=1 gen=1 region=1248` · `main jmp=0 gen=0 region=768`.

**INJECTION (probe, reverted):** drop the `flat_jmp_entry` conjunct → palindrome's declined-run count goes **1 → 4**, i.e. all predicate graphs now reach the loop. The gate is live and it is exactly this conjunct.

**GATE B — KIND WHITELIST (the remaining 65 = one `main` per compiling program).** `zd_wl_kind` (emit.cpp:1840) names **only SNOBOL4-family kinds**. Not one Prolog kind appears in it. All 65 `main` graphs decline at node 0.

⛔ **WHY THIS INVERTS THE LADDER.** `zd_plan`'s own comment says jmp-entry citizens *"speak their OWN enter/exit protocol (32B wire header, value handoff through the protocol's slots)"* and that *"this family converts later on its own rung by teaching the protocol the cell convention."* For SNOBOL4 that family is EVAL/CODE/PAT$ — deferrable indefinitely. **For Prolog it is every predicate, i.e. the entire language.** The rung SNOBOL4 postponed is the rung Prolog must open with; the kind-whitelist work is the cheap follow-on, not the opening move.

---

## ⭐⭐ THE WHOLE-LANGUAGE GAP IS **EIGHT KINDS** — NEW INSTRUMENT `SCRIP_ZD_GAP=1`

The existing `[ZD]` diag reports only the **first** blocker, which structurally cannot size an **all-or-nothing** run: it says `IR_CALL_BUILTIN_PROLOG` forever and never reveals which *set* of templates must arm. New env-gated instrument walks the whole declined run and prints each node's `zd_wl_kind` verdict.

**Gap census, 250 programs (nodes in declined runs):**

| kind | full language (10,110 nodes) | `main` only (696 nodes) |
|---|---|---|
| `IR_VAR_REF` (72) | **4168 (41%)** ⬅ the elephant | 100 |
| `IR_CALL_BUILTIN_PROLOG` (11) | 2787 (28%) | **198** ⬅ leads here |
| `IR_CALL_PROC_STAGED` (12) | 645 | 92 |
| `IR_SUSPEND` (64) | 477 | — |
| `IR_VAR` (71) | 93 | 25 |
| `IR_CUT` (19) | 86 | — |
| `IR_MOVE_LABEL` (39) | 72 | 42 |
| `IR_CALL_BUILTIN_GEN` (8) | 30 | — |
| **already admitted** | `IR_LIT_STRING` 1354 · `IR_LIT_INTEGER` 394 · `IR_LIT_REAL` 4 = **17.3%** | 239 = 34% |

⭐ **THE RANKING INVERTS BETWEEN `main` AND THE PREDICATES.** A census taken on `main` alone ranks `IR_CALL_BUILTIN_PROLOG` first and would have aimed the first rung at the wrong template. `IR_VAR_REF` is invisible-ish in `main` (100) and is **41% of the whole language** (4168). **A census scoped to the graphs that currently reach the planner measures the graphs that are least representative of the language.**

⭐ **THE GAP IS SMALL AND CLOSED.** Eight kinds, and the LIT family already arms. This is not a 224-opcode problem; it is a short, ranked, finite list.

---

## ⚠ INSTRUMENT DEFECT FOUND — `bb_op_name` HAS HOLES ON PROLOG KINDS

`bb_op_name` returns NULL for **`IR_CALL_BUILTIN_PROLOG` (11)** and **`IR_CUT` (19)**, so the existing `[ZD]` decline diag prints `DECLINED at i=0 ((null) op=11)`. Every first-blocker histogram a Prolog session has ever read reports its top entry as `(null)`. Cheap fix, real cost: it is why the blocker was an opaque number rather than a name. Not fixed this session (kept the diff to one line); **named here so the next rung does not re-derive it.**

## ⚠ METHODOLOGY — I NEARLY FILLED THE DISK WITH MY OWN INSTRUMENT

The gap census appended **raw stderr** for 250 programs, of which **185 fail to compile** and spew. Result: `/tmp/gap1.txt` 3.4G + `/tmp/gap2.txt` 5.9G → **device full**, which then surfaced as a *build failure* (`error writing to /tmp/ccXXXX.s: No space left on device`) and briefly looked like a code error. **Filter an instrument's output at the source; a census over a corpus with a 74% compile-failure rate is a stderr amplifier.** (That 185/250 compile-failure rate is itself unexamined and is NOT claimed here as a defect — it may be unsupported-construct programs by design. **UNMEASURED.**)

---

## GATES (all `-O0`, full build from clean HEAD)

- Prolog rung suite **164/164 `--mode interp` · 164/164 `--mode compile` · FAIL=0** — exactly the s161 baseline, unchanged.
- `test_gate_emit_no_lang.sh` **OK** (instrument is file-static `_gp` + env string `SCRIP_ZD_GAP`; no language token in code).
- `test_gate_pl_no_new_global.sh` **PASS**, doomed-ratchet **14 / floor 14** (unchanged — file-static, not a `g_*`).
- Instrument inertness A/B: **120/120 `--compile` outputs byte-identical** with `SCRIP_ZD_GAP` unset, instrumented vs pre-instrument binary. ⚠ **SCOPED:** 4 of those 120 were *killed* under both binaries, so their "identical" is vacuous; the honest figure is **116 substantive + 4 vacuous**.
- Injection probe **REVERTED**; `git diff --stat` = 1 file, +1 line; baseline decline count re-verified 1 (not 4).

---

## NEXT — THE LADDER, RANKED BY MEASUREMENT

- **(a) ⭐⭐ ZD-PL-0 — THE PROTOCOL RUNG (the 94%).** Teach the jmp-entry enter/exit protocol (32B wire header) the cell convention, so predicate graphs can reach `zd_plan` at all. This is the gate SNOBOL4 deferred and Prolog cannot. ⛔ Do NOT simply delete the conjunct — that was this session's *probe*, and it lands `op_zres` on templates with no ZD arm (the "017 falsification shape": silently wrong code, not a crash).
- **(b) ZD-PL-1 — `IR_VAR_REF` (4168 nodes, 41%).** The elephant, and the natural first template arm. Precondition per SN4's ZD-2a law: confirm it dispatches to **ONE** template unconditionally before admitting the kind.
- **(c) ZD-PL-2 — `IR_CALL_BUILTIN_PROLOG` (2787).** Also fix `bb_op_name`'s hole while here.
- **(d) `bb_op_name` holes (11, 19)** — one-line, unblocks readable diagnostics for every future census.
- **(e) ⚠ RECONCILE WITH THE LIVE CURSOR.** s161's NEXT (a) is ζ-FB-4, an rbp-pin probe **on the flat carve**. If (a)+(b) land, a large part of the ζ-FB ladder becomes **vacuous by construction** — the same shape as `FINDING-2026-07-30-CLAUDE-PL-RTX-0`'s "SINK makes RTX vacuous for Prolog". Lon ruling wanted before spending a session refining the base register of a carve we are deleting.

**BANKED (carried, unchanged):** `unary_not.sno` uninitialised-`.string` non-determinism; engine-wide silent-fail on undefined predicates; int/float standard-order conflation (two-oracle); lexer escape three-site/two-behaviour; NO-LCO segfault; nested-`\+` binding leak; retractall/1 gaps.

---

## ⛔⭐ REBASED MID-SESSION — THE SUBSTRATE MOVED ONTO THIS RUNG'S OWN CONJUNCT, AND EVERY NUMBER WAS RE-MEASURED

At close, `handoff_status.sh` reported origin ahead on SCRIP and `.github`. The incoming SCRIP commit is **`5c1f99bf` "ZD-9: refine zd_plan's BLANKET jmp-entry decline to admit DEFINE stubs"** — a parallel session landed a refinement of **the exact `flat_jmp_entry` conjunct this rung measured against**, changing it to `flat_jmp_entry && !zd_stub_ok()`.

Per the s159 rule (*a claim without the SHA it was measured on silently expires under parallel sessions*), the pre-rebase figures — taken on `417add3c` — could not be carried. **RE-MEASURED on the rebased tree (`f88ce472`, SCRIP now `5c1f99bf`+):**

- Prolog **ARMED_NODES = 0 · DECLINED_RUNS = 65** — **IDENTICAL to the pre-rebase measurement.**
- Gates re-run: rung suite **164/164 interp + 164/164 compile FAIL=0** · `emit_no_lang` **OK** · `pl_no_new_global` **PASS** ratchet 14/floor 14.

**The headline survives, and the reason is informative:** ZD-9's `zd_stub_ok()` admits **DEFINE stubs** — a SNOBOL4 construct. It widens the jmp-entry gate along the SNOBOL4 axis and moves Prolog by exactly zero. That is this finding's thesis reproduced by an independent session's commit: **work aimed at SNOBOL4's shape of the jmp-entry problem does not reach Prolog's shape of it.** ZD-9 is correct and welcome; it is also evidence that ZD-PL-0 is a genuinely separate rung and will not arrive as a side effect of the SNOBOL4 ladder.
