# FINDING 2026-08-21 s248 (seat2) — PZ-1(d) LANDED: THE `:2065` TAUTOLOGY IS RETIRED, AND γ-RETAIN AS CURRENTLY FLAGGED IS **NOT SUFFICIENT** TO MAKE VAR_REF ADMISSION SOUND

**SCRIP `e92aebfe`** (commit `9c54afbf` rebased onto sibling `425c5d06`) · corpus `a998b750` · .github at handoff · RT_OPT `-O0` · every number below RUN this session, none transcribed.
⚠ The sibling landing `cfff4530..425c5d06` touched **`README.md` + one bench script only — zero compiler code**, so measurements taken at `cfff4530` remain valid at `e92aebfe`. Verified by `git diff --stat`, not assumed.

## 0. LON'S TWO RULINGS THIS SESSION (in-chat, supersede the goal file on the spot)
1. **PZ-1 ORDER: (d) BEFORE (b)/(c).** Retire the tautology and give `IR_VAR_REF` a real guard first, so `zdp_tier` supplies the ζ-ACTIVATION admission signal rather than a hand predicate.
2. **CP LIVES IN R15; THE CONTRACT IS AMENDED.** Σ/δ/Δ are **scan-only** reservations and a Prolog graph does no string scanning, so R15 is free there and carries CP. `fail` is uniformly `jmp [r15]`, cut is `r15 = [r15+16]`. ⛔ The reservation still binds any graph that scans — this releases R15 for **Prolog graphs only**, and PZ-2 must not assume it in shared code. Recorded in `GOAL-PROLOG-100.md` §register contract.

## 1. THE FLOOR, RE-DERIVED AT `cfff4530` (the cursor's numbers were pinned at `d2ade229` and never re-derived here)
| board | result | vs cursor |
|---|---|---|
| smoke | **3/5** m2+m3+m4 (`clause`, `recursion` red) | unchanged |
| rung suite | interp **110/164** · compile **109/164** | matches exactly |

## 2. ⭐ WORKLIST §0(3)'s ZERO-READERS CLAIM IS NOW **PROVEN BY INJECTION**, NOT ASSERTED
§0(3) said the `[kt-8]` slot has zero readers and told the next seat to *"prove the zero-readers claim by injection before relying on it."* Done. `SCRIP_PL_ZANCHOR_POISON=1` (new, `xa_flat.cpp`, default OFF) drops the store entirely. The asm diff is **exactly** the two `mov qword ptr [rsp + kt-8], rsp` stores and nothing else — surgical, no collateral motion.

With the store **completely removed**: Prolog rung **110/109 identical** · Prolog smoke **3/5 identical** · Icon smoke **14/14 both modes identical**. **356 program-runs, zero behavioural change.** The slot is dead on BOTH the Prolog and the Icon path, and PZ-1(b)'s caller-base save has a free, correctly-sized home. The killswitch's OFF arm is md5-identical to HEAD (`9f0e5fe6…` on `plz_p2`), so the instrument costs nothing.

## 3. ⭐⭐⭐ PZ-1(d): THE GUARD NOW NAMES THE PRECONDITION INSTEAD OF CONTRADICTING ITSELF
`emit.cpp:2065` returned `pl_cells_graph && !pl_cells_graph` — never 1 — from `069c2fd8` (PL-ZK-5B s13), whose own message says *"gated off via tautology pending correct TERM_VAR materialization."* PZ-0 measured its cost: **635 of 636 cells-arm refusals were `IR_VAR_REF`, 86% of all runs**, and `SCRIP_ZD_PL_VR` was a killswitch that could not move a byte.

Now: `pl_cells_graph && emit_rec_pin() && emit_pl_gamma_retain()`. The third term is the load-bearing one — PZ-0's own finding is that **a logic variable cannot live in a cell that γ RELEASES**, so admission is gated on RETENTION, the true semantic condition, and turns itself on when PZ-1(c) lands. A guard that names its precondition is falsifiable; a tautology is not.

**CENSUS** (`util_pl_zd_arm_census.sh`, 214 programs / 736 ZD runs), cells arm with admission active:

| | PZ-0 | now |
|---|---|---|
| ARMED | 100 / 736 | **534 / 736** |
| `IR_VAR_REF` refusals | **635** | **0 — the kind vanishes from the table** |
| next refusers | — | `IR_VAR` (162) · `IR_CALL_BUILTIN_GEN` (40) ⇒ **the next admission arm** |

**ONE AUTHORITY (s22k spelled-twice discipline):** `emit_pl_gamma_retain()` added to `emit.h` beside `emit_rec_pin()` — the file that already owns pin policy — and `xa_flat.cpp`'s `pl_gamma_retain_on()` now DELEGATES to it instead of spelling the same env read a second time. **No new globals**: a function, not state; `test_gate_pl_no_new_global.sh` ratchet holds **14/14**.

## 4. ⛔⛔ THE HEADLINE FOR PZ-1(c): **RETENTION, AS THE EXISTING FLAG IMPLEMENTS IT, IS NOT SUFFICIENT**
Three arms, same suite, measured this session — this is the finding that changes the next rung:

| arm | interp | compile |
|---|---|---|
| A — cells, retain OFF (guard admits nothing) | **103**/164 | 2/164 |
| B — cells, retain **ON** + `VAR_REF` admitted | **91**/164 | 2/164 |
| (pin-only guard, no retention term — earlier probe) | **91**/164 | 2/164 |

**Flipping `SCRIP_PL_GAMMA_RETAIN=1` and admitting `VAR_REF` still costs −12 on interp — the identical −12 the pin-only guard cost.** Retention as currently flagged buys **nothing**. The reason is structural, and it is in the goal file already: PZ-1(c) specifies a **five-site enabling pair** (prologue saves caller base + pins own · γ hands base in rax, no unwind · caller staged-call γ/β landings re-anchor · backtrack restores own base · ω restores caller base then releases · terminal top-graph exclusion). The existing `SCRIP_PL_GAMMA_RETAIN` flag implements **ONE** of those — the γ no-unwind arm in `xa_flat.cpp` — so arm B measures *partial* retention, not retention.

⛔ **A seat that trusts the flag's NAME would conclude "γ-retain doesn't work" and abandon the thesis.** It has not been tested yet. PZ-1(c) must land all five sites before the thesis is falsifiable, and the −12 is the *expected* reading until it does.
⛔ **THE CELLS ARM's `compile 2/164` IS PRE-EXISTING** — measured on BOTH sides of this change (before: 103/2, after: 103/2). It is not this commit's, and no board here should be read as a regression.

## 5. ⭐ A FIFTH DEAD GUARD THE WORKLIST DID NOT RECORD (same class as the tautology)
`x86_fb_pinned()` (`x86_asm.h:456`) is **`inline int x86_fb_pinned() { return 0; }`** — ONE definition tree-wide, hardcoded. It gates **six** sites, and kills every one of them:
- the **Icon half** of `:2065` (`icn_cells_graph && x86_fb_pinned()`) — so `IR_VAR_REF` was unreachable in **both** languages, not just Prolog;
- **all** of `:2072` (`IR_MAKE_LIST`);
- **two of three** admission clauses at `:2025` (`IR_VAR`/`IR_ASSIGN` locals);
- **three** `bb_match_defer.cpp` arms (`:155`, `:162`, `:178`).

⛔ And `rtx_abi.inc:26` states the invariant **`x86_fb_pinned() == emit_rec_pin()`** — **that invariant is FALSE today**: `emit_rec_pin()` is live and `x86_fb_pinned()` is a constant 0. `zeta_choices.h:124` likewise describes the per-graph `x86_fb_pinned()` rsp/fb selection as *"the duality that actually runs and is already complete."* It does not run. **Recorded, not chased** — but it is the same disease as `:2065` and the vacuous MEDIUM ratchet: *a predicate that cannot fire, documented elsewhere as live*, and it should be a rung of its own before anything is built on `x86_fb_pinned()`.

## 6. GATES + CANARY AT THE COMMIT
`test_gate_emit_no_lang.sh` **OK (LANG-BLIND)** · `test_gate_pl_no_new_global.sh` **PASS, ratchet 14/14** · Icon canary **14/14 both modes** · Prolog smoke **3/5** · shipped-default `.s` **md5-identical to HEAD**. Shipped default and Icon are provably untouched: the change is gated on `pl_cells_graph`, which only opt-in `SCRIP_PL_CELLS=1` ever sets.

## 6b. HANDOFF REGEN — ALL SIX RUN, `changed=0`, AND A SEVENTH TREE THAT WAS DRIFTING (NOT THIS SESSION'S)
All six RULES step-4 scripts run in order: benchmark · feature · demo · programs (**623**) · prolog_bench (**22**) · crosscheck (**487**) — **`changed=0` everywhere**, ~1,130 programs. That is the independent second path confirming the shipped default is byte-identical, exactly as RULES intends.

⛔ **The conditional seventh — `update_icon_bench_asm.sh` — found 20 of 23 icon bench `.s` STALE: 1,210 insertions / 14,692 DELETIONS** (queens −1144, rsg −1870, tgrlink −2412). **ATTRIBUTED BY MEASUREMENT, NOT ASSUMED:** `queens.icn` compiled at `e92aebfe` and at its parent `425c5d06` gives the SAME md5 (`3d5c52d5…`, 6707 lines) — **this session's commit is ICON-INERT** (gated on `pl_cells_graph`, which only `lower_prolog.c` sets). The drift is the sibling Icon era's; a seat had already landed the same regen upstream as corpus `96e894a9` ("THE DRIFT IS THE SIBLING'S r10/r11 ERA") — two seats reaching the same conclusion independently, so this session's duplicate commit was correctly dropped as empty on rebase.

⭐ **WHY IT SAT, AND THE GENERALISABLE POINT:** `update_icon_bench_asm.sh` is a **CONDITIONAL** step in RULES (*"Icon emitter/lowerer touched ⇒ also…"*), and `.s` artifacts are read by no gate and no board. A seat that moves Icon codegen without regenerating therefore leaves **no trace anywhere**. This is the s169/s192 pattern a **third** time: *the trees that drift are the ones no step names UNCONDITIONALLY.* Worth a queue row to make the icon-bench regen unconditional, the way `crosscheck` was added at s192 on exactly this evidence.

## 7. NEXT
PZ-1(c) — land the **five-site** enabling pair through the shared pin machinery (`emit_rec_pin`/`x86_fb`/heap-fb adopt), then re-run arm B. The guard committed here turns itself on the moment retention is real, so PZ-1(c)'s DONE-WHEN is simply *arm B stops costing −12*. PZ-1(b)'s caller-base save now has a proven-free home at `[kt-8]`.
