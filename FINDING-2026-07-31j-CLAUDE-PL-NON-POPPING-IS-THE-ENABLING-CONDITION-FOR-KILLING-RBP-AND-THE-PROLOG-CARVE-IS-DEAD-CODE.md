# FINDING 2026-07-31j — PL: NON-POPPING IS THE ENABLING CONDITION FOR KILLING RBP, AND THE PROLOG CARVE IS DEAD CODE

**Session:** s164 (Claude) · **SCRIP HEAD:** `548c5637`, tracked source UNMODIFIED all session · **All builds `-O0`** (Makefile default; no `-O1`/`-O2` used or sought)
**Directive:** Lon — *"Get benchmarks working using NON-POPPING FORTH-style RSP ZETA stack with a C-style RBP used occasionally only when absolutely necessary."* Then: *"All your choices."*

---

## 0 ⛔ PROVENANCE — THE s163b UNEXPLAINED-COMMIT QUESTION IS ANSWERED: A PARALLEL WRITER IS LIVE IN THIS CLONE

The s163 cursor asked: *"LON: the s163b UNEXPLAINED COMMIT wants an explanation — if a parallel session can write into this clone, the SHA-rule and every A/B baseline in flight are unsound."* **It can, and it did.** Concrete, dated evidence this session:

| artifact | state | timestamp |
|---|---|---|
| `SCRIP/scripts/census_pl_rsp.sh` | untracked, executable | 2026-08-01 00:10:55 |
| `.github/GOAL-PROLOG-RSP.md` | untracked, 213 lines | same window |

Both appeared DURING this session. This assistant never wrote to `SCRIP/scripts/` or created any `.md` in `.github` before the file you are reading. The pair is internally coordinated (the script is the goal file's named instrument), and the script **hardcodes this session's own measurements to the digit** — `rbp=45741 rsp=685 seed=145 carve=2831` — while the goal file quotes a **Lon directive dated 2026-07-31 s164 that never appeared in this session's conversation** (*"ensure that ALL operands in EVERY BB is accessed via RSP, NOT RBP … allocations to happen gradually not all in ONE BIG FRAME. It eats TOO MUCH memory"*), and carries measurements this session did not take (SNOBOL4 fresh 0 rbp/909 rsp; Icon 38,552/3,207).

**CONCLUSION: a parallel session shares this container's filesystem and is writing into the same clones.** This is the standing explanation for s163b's `1c4830d2`.

⭐ **BUT THE CONTAMINATION WAS BOUNDED, AND IT WAS CHECKED, NOT ASSUMED.** `git status --porcelain` at session end: **0 tracked files modified**, 1 untracked. `HEAD` never moved off `548c5637`. The writer ADDED files; it did not edit source or rebuild. Therefore every measurement below stands. **The rule this implies:** a session must verify `HEAD` + `0 tracked-modified` *at the point of measurement*, not merely at session start — start-of-session cleanliness is not evidence about a build that happens twenty minutes later. The SHA-rule is not sound on its own; it needs the tracked-modified count beside it.

⚠ Related, independent: the cursor records `1cc10758` for the `SCRIP_ZD_GAP callee=` commit; HEAD carries that exact message as **`548c5637`**. The pushed history was rewritten. SHA-keyed baselines are unsound here for that reason too.

---

## 1 BENCHMARKS ARE GREEN AT HEAD — THE DIRECTIVE'S FIRST CLAUSE WAS ALREADY SATISFIED

Measured before changing anything (22 Prolog benchmarks, `corpus/benchmarks/prolog/bench`):

| mode | result |
|---|---|
| interp (default) | **22/22 PASS** |
| mode-3 `--run` native | **22/22 PASS** |
| mode-4 `.s` → `as` → `gcc` | **22/22 PASS** |

So the rung was never "make them work"; it was "move to non-popping ζ without losing that."

---

## 2 ⭐⭐ THE PROLOG CARVE IS DEAD CODE — 2,642 ALLOCATE/RELEASE PAIRS NO INSTRUCTION ADDRESSES

`SCRIP_NOFC=1` (`zc_nofc()`, `zeta_storage.c:724`) suppresses the ZW-1 universal carve at `emit.cpp:822`.

| | `sub rsp` | `add rsp` (pops) |
|---|---|---|
| baseline | 2831 | 2831 |
| NOFC | 189 | 233 |

**91.8% of pops and 93.3% of carves vanish.** And the diff is *only* that: `diff base/nrev.s nofc/nrev.s` = **93 `sub rsp,` + 92 `add rsp,` lines and NOTHING ELSE.** Zero addressing changes, zero operand changes.

⭐ **THEREFORE: on Prolog the universal carve allocates cells that NO instruction ever addresses.** It is pure dead weight. The `[rsp+..]` reference count is *identical* (685) in both regimes — proof the carved cells were never read.

**CORRECTNESS — behaviour-preserving on the whole corpus:**
- rung corpus **185/185 identical** stdout+rc (mode-3, baseline vs NOFC, differential)
- benchmarks **22/22 mode-3**, **22/22 mode-4**

**INSTRUMENT SELF-VALIDATION:** the pop census (2831→233) proves `SCRIP_NOFC=1` genuinely reached the compiler, so the green is not a no-op env var. This matters because the identical-output result would otherwise be indistinguishable from the switch never firing.

---

## 3 ⛔ THE SN4 "POPS COST 20–48%" FIGURE DOES NOT TRANSFER TO PROLOG — AND WALL TIME CANNOT RESOLVE THIS LADDER

Wall-time A/B, min-of-5, mode-4 binaries, `-O0` runtime:

| bench | base | NOFC | delta |
|---|---|---|---|
| queensn | 649 ms | 672 ms | −3% |
| queens | 133 ms | 131 ms | +2% |
| tak | 23.0 ms | 22.9 ms | 0% |
| meta_qsort | 19.7 ms | 19.7 ms | 0% |

Removing 2,598 pop sites bought **nothing measurable**. Consistent with §2: they were dead instructions, and `sub/add rsp` is ~free anyway.

⛔ **NOISE BOUND — REPORTED BECAUSE IT DISQUALIFIES THE INSTRUMENT, NOT AS A CAVEAT.** 7 interleaved reps of queensn: base `1246, 649, 1217, 659, 656, 652, 697` ms; nofc `677, 648, 710, 661, 660, 1212, 674` ms. Both bimodal, ~1.9× spread, distributions indistinguishable. **Wall time in this container cannot resolve anything smaller than ~2×.** Neither `perf` nor `valgrind` is installed. **No perf claim on this ladder is admissible until a deterministic instrument exists.** (Cheapest credible next step: user-CPU time via `getrusage`, or the repo's existing PLT-interposition counting.)

---

## 4 ⭐⭐ HEADLINE — NON-POPPING IS THE *ENABLING CONDITION* FOR KILLING THE RBP FRAME

The directive's two clauses are not two tasks. They are **one mechanism**.

Mid-body RSP movement, per graph, over 145 rbp-pinned graphs (mechanically checked: walk from `mov rbp,rsp` to the epilogue marker `pop rbp`/`mov rbp,[..]`, flag any `sub/add rsp` or `push/pop` more than 4 lines from the body end):

| regime | fully stable | epilogue-only | **genuine mid-body movement** |
|---|---|---|---|
| baseline (popping) | 22 | 6 | **117 / 145** |
| **NOFC (non-popping)** | 44 | 101 | **0 / 145** |

⭐ **Under NOFC, `rbp == rsp` INVARIANTLY through every graph body, so every `[rbp+off]` IS `[rsp+off]` at the same offset. The C-style frame pointer is 100% VESTIGIAL on Prolog.**

**You cannot drop RBP while the carve pops — and once it stops popping, RBP has no remaining job.** That is why the directive names both halves in one sentence.

⚠ **COST NOT YET PAID (do not assume this is free):** `[rsp+disp]` requires a SIB byte; `[rbp+disp]` does not. RSP addressing is **+1 byte per operand reference** — 45,741 refs ≈ **+45 KB text**. The win is freeing `rbp` as a GPR and deleting the pin/save/restore. **The tradeoff is real and must be measured, not asserted** — and per §3 the instrument to measure it does not yet exist.

---

## 5 THE RBP FRONTIER IS *ONE PREDICATE*, NOT 45,741 SITES — AND ITS BAIL IS PRINCIPLED

There is a single frame-base authority — `x86_asm.h:374`:
```c
inline const char * x86_fb() { return x86_isle() ? "r12" : x86_fb_data() ? "rbp" : "rsp"; }
```
FB-STMT (`x86_fb_stmt_on()`, `x86_asm.h:371`) is **DEFAULT-ON** and already ships the 2026-07-29 directive *"Change every RBP to RSP that can be."* Prolog is nonetheless **98.5% rbp** (45,741 vs 685). `SCRIP_FB_DEBUG=1` on `nrev.pl` localizes why:

```
[FB-STMT] hook skip deep=1 pat=0 gen=1 gp=1 rc=0   (×8 graphs)
[FB-STMT] hook skip deep=1 pat=0 gen=0 gp=0 rc=0   (×1)  ->  [FB-STMT] bail kind IR_DISJUNCTION @2
```

⚠ **READ THE GATE CAREFULLY — `flat_deep_arrival` IS A PRECONDITION, NOT A BLOCKER.** (This finding's author misread it once; recording the correction so the next session does not repeat it.)
```c
flat_fb_refine = (flat_deep_arrival && !flat_pat && !flat_gen && !_rc_own) ? emit_fb_stmt_scan(cfg) : 0;
```
So Prolog has **TWO** blockers, and the prize splits:

| population | `[rbp+N]` refs | share | blocker |
|---|---|---|---|
| predicate/generator graphs | 32,173 | **70.3%** | `flat_gen` — the FLATDISP-5 suspend/resume wall |
| main-class graphs | 13,144 | **28.7%** | `emit_fb_stmt_scan` bails on `IR_DISJUNCTION` |

⛔ **THE 28.7% IS NOT FREE, AND ADMITTING IT WOULD BE THE SILENTLY-GREEN CLASS.** `emit_fb_stmt_scan`'s own contract (`emit.cpp:2590`) states eligibility is *"every deep kind present is statement-bracketed (DEFER/ARBNO/FENCE1/VALUE); any suspend-class, generator-class, ABORT or CALLOUT kind disqualifies the whole graph (their arrivals are not rebalanced by the HEAD..RELEASE bracket)."* **Prolog's `IR_DISJUNCTION` IS a choice point** — a backtracking re-entry whose arrival is precisely *not* bracket-rebalanced. The bail is **correct and load-bearing**, not an oversight. Blind-widening it would pass every correctness gate and plant the s158 land mine (store and load naming different base registers). Admitting it requires *proving* Prolog disjunction arrivals are rsp-rebalanced — a proof obligation, not a whitelist edit.

---

## 6 ⚠ NOFC IS DEAD-CODE REMOVAL — DO NOT MISTAKE IT FOR PROGRESS TOWARD GRADUAL ALLOCATION

The end state wants per-BB self-allocation on RSP (cells that ARE addressed) and no whole-graph frame. NOFC deletes the per-box carve *machinery* — which is currently dead, but is the very machinery the end state must make **live**. Measured whole-graph carve (the "ONE BIG FRAME"), baseline:

**145 sites · 320,352 B total · mean 2,209 B per graph activation.**

That 2.2 KB is per-activation C stack, multiplied by Prolog recursion depth — the concrete form of the memory complaint. **NOFC does not touch it** (it removes per-box carves; the `sub rsp, 512`-class whole-graph carve survives). So NOFC and "gradual allocation" pull in *opposite* directions on the same machinery, and a session that lands NOFC as "the non-popping rung" and moves on will have removed the scaffolding rather than raised the building.

---

## 7 ZD-PL-A SLICE 2a — BLOCKER SETTLED, RUNG DELIBERATELY NOT SPENT

The s163c cursor's blocker was: *"whether `rt_pl_dop_trail_mark` dereferences that pointer when `esi==0` was NOT verified."* **Verified: it does not.** Three-level trace:
1. `rt_pl_dop_trail_mark` (`by_name_dispatch.c:1559`) uses `args` in exactly one place: `rt_gc_point_arr(args, 0, NULL)`.
2. `rt_gc_point_arr` (`gc_heap.c:382`) never dereferences — it only *stores* into `g_gc_shield_arr` with `g_gc_shield_n = n`.
3. Sole consumer, `gc_heap.c:632`: `for (int si = 0; si < g_gc_shield_n; si++) …` — with `n == 0` the body never runs; the address is never even formed.

`dop_direct_fp` matches `narg == 0` for `$trail_mark` (ar=0) with no internal arity filter. **The `(nargs > 0)` conjunct is conservative, not load-bearing.**

⛔ **NOT LANDED, ON PURPOSE.** §3 shows the pops are worth ~0% on Prolog, and §2 shows why. Spending the rung on `$trail_mark` dispatch would repeat the trap this ladder has already caught twice (s163's "vacuous by construction"). The blocker is cleared and banked so the rung is *cheap when it is justified* — it is not justified by anything measured here.

---

## 8 ⛔ DEFECT — `32f45cd2` IS MISLABELLED "diagnostic only"; THE COMMITTED `.s` ARE STALE

`emit.cpp:46 flat_label_kind` calls `bb_op_name(op)` and falls back to `"op%d"` on NULL. Filling the 8 NULL holes therefore **renamed emitted labels in every Prolog artifact** (`n0_op11_α` → `n0_call_builtin_prolog_α`). Regenerating at HEAD: **changed=22/22, ~114k insertions.** The s163 cursor's "43/43 byte-identical" was **pre- vs post-*compiler*** (two freshly generated sets), never against the committed artifacts — which is why this stayed invisible. Both claims can be true at once; only one of them is about the repo's contents.

**RULE THIS IMPLIES:** "diagnostic only" is a claim about the emitted bytes and must be *measured against the committed artifacts*, not inferred from the diff touching only a name table.

---

## 9 ⛔ TRAP CAUGHT — A FALSE LANGUAGE-ASYMMETRY FINDING, KILLED BY ITS OWN CONTROL

First pass showed SNOBOL4 **18/21 divergent** under NOFC against Prolog's 0/185 — a dramatic asymmetry story. **The control killed it:** the *same binary run twice* diverges on **17/21**, because those benchmarks print a `ms:` wall-clock line. The signal was ~entirely instrument noise.

**The SNOBOL4 NOFC number therefore remains UNKNOWN** — the filtered re-run timed out and is not reported here. Recorded as unknown rather than as the noisy figure. **Any differential over the SNOBOL4 benchmark corpus MUST filter `^ms:` and MUST run the same-binary-twice control first.**

---

## 10 STATE / NEXT

**Nothing committed, nothing pushed.** Working trees: SCRIP tracked-clean at `548c5637`; corpus holds 22 regenerated `.s` (honest HEAD output per the regen script's own contract — §8); `.github` holds this finding.

1. ⭐⭐ **Deterministic instrument FIRST** (§3). Until it exists, no rung on this ladder can be justified or falsified on perf. This gates everything below.
2. ⭐ **The RBP conversion is one predicate wide** (§5), and 70.3% of it sits behind the FLATDISP-5 suspend/resume wall — that wall, not the whitelist, is the real rung.
3. ⛔ **Do NOT blind-widen `emit_fb_stmt_scan` to `IR_DISJUNCTION`** (§5). It needs a rebalancing proof.
4. **NOFC as Prolog default: EVIDENCE IS STRONG BUT THE VEHICLE IS WRONG.** 185/185 + 22/22 + zero addressing delta says the carve is dead for the kinds Prolog uses. But `SCRIP_NOFC` is a *global* switch shared with SNOBOL4, where its effect is unmeasured (§9) — and per the RULES.md FACT RULE no language identity may exist past LOWER, so the landing may **not** be "on for Prolog." The correct formulation is the one `emit.cpp:822` already names as unanswered: **which node KINDS' carve helps and which hurts.** §2 answers it for the Prolog-resident kinds — *a carve whose cells no instruction addresses should not be emitted* — and that is checkable at emit time, language-neutrally.
5. ⛔ **Provenance (§0) needs a Lon ruling** before any measured A/B is trusted across sessions.
