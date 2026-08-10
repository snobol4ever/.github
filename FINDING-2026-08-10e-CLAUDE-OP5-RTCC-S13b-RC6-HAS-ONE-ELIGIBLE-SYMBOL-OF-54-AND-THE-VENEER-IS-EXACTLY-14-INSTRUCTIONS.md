# FINDING — 2026-08-10 s13b (Opus 5) — RTCC RC-6: THE ELIGIBLE SET IS 1 SYMBOL OF 54 AND IT IS A ONE-SHOT INIT; THE VENEER IS EXACTLY 14 INSTRUCTIONS PER CROSSING

**Goal:** GOAL-RTCC.md · **Class:** RC-0 (census/scripts/docs) · **Emitter bytes:** ZERO · **Regen owed:** none
**SCRIP HEAD:** `bce9a4b0` (unmoved across session) · **Watermark re-proved at open AND close.**
**Lon in-chat:** *"All your choices."* — the three rulings the file was blocking on were taken here and are flagged as MINE, not his, so he can veto any of them.

⛔ **CONCURRENT SEAT — TWO RTCC SESSIONS RAN ON ONE FILESYSTEM, THIRD OCCURRENCE OF THE s11/s12 HAZARD AND THE FIRST ON ONE GOAL FILE.** A second RTCC seat (also self-labelled s13) committed `6edc899e` at **23:04:33** into this same working tree while this session was mid-census — which is also what produced the unexplained `.so` in §1. **ITS WORK STANDS IN FULL AND IS COMPLEMENTARY, NOT CONFLICTING:** it proves `RTCC_GLOBAL_R8_ANCHOR` is decorative (`rtcc_anchor_cmp` has ZERO callers) and that RC-5's "zero dynamic delta" was minted from GVA and over-generalised to ANCHOR. This session is relabelled **s13b** and its cursor block is inserted ABOVE that one without touching it. ⇒ **THE SEAT HEARTBEAT IS NO LONGER A SUGGESTION** (s11 PLAN SCRUTINY §5): two seats on one goal cannot see each other, and neither `git status` nor the cursor reveals it — only a commit TIMESTAMP does.

---

## 0. WATERMARK (re-proved, HEAD-stamped)
- `fibonacci` m3 `result: 832040` at **RTCC=0 (498 ms)** and **RTCC=1 (553 ms)**.
- `scripts/test_gate_rtcc_claimed_regs.sh --strict` → **PASS**, COLLISION CLASS **EMPTY**, HAZARD SURFACE **19** — independently reproducing s8/s11/s12's 19.
- Tree clean, `git status --porcelain` = 0 lines, HEAD unmoved at open and close.

## 1. ⛔ AN UNEXPLAINED BUILD ARTIFACT WAS PRESENT AT OPEN AND WAS DESTROYED, NOT TRUSTED
At session open `out/libscrip_rt.so` existed (linked 23:00) with all 512 `out/rt_pic` objects dated 22:57 — **after** this session's 22:47 clone, and **not** built by this session. `ps` showed no live build; no seat heartbeat existed. Provenance could not be established, and s11's trap is precisely that `make` tracks timestamps and not `-D` flags, so a leftover `.so` can be a killswitch variant that silently mislabels every subsequent measurement.
⇒ `rm -rf out /tmp/si_objs scrip`, full rebuild, watched: **184 s**, `SCRIP_RC=0`, `RT_RC=0`. Every number below comes from a binary this session built from a clean tree at HEAD with default flags.
⭐ **LAW (generalising s11/s12's concurrency hazard to ARTIFACTS, not just worktrees):** an uncommitted worktree is not the only thing another seat can leave behind. **A BUILD ARTIFACT WITH UNEXPLAINED PROVENANCE IS NOT A BUILD ARTIFACT** — it is indistinguishable from a `-D` variant, and it is cheap to replace (184 s here). Rebuild before measuring; never inherit a `.so` you did not watch link. The heartbeat convention s11 proposed (§5 of the s11 PLAN SCRUTINY) is now adopted here in its cheapest form: `touch /home/claude/.seat-<goal>-$$` at open.

## 2. ⭐⭐⭐ RC-6's PREMISE IS FALSE AT HEAD — THE ELIGIBLE SET IS **1 OF 54**, AND IT IS A LAZY ONE-SHOT INIT
RC-6 (orig) reads: *"A family already in asm (`rtx_*.S`) adopts the SCRIP convention natively; the registry reclassifies it NO-VENEER; its crossings become direct jumps/calls with zero writeback."*

**That is sound only if the asm body can never reach C with claimed registers live and unsaved.** BLOCK-CANONICAL LAW says a C function reading a claimed register reads garbage BY CONTRACT — and the sharper half is that C *clobbers* it freely, so generated code would resume on garbage. **Every escape edge from an asm body into C is a disqualifier.**

Census (`scripts/util_rtcc_escape_census.sh`, landed this session):

| | |
|---|---|
| PORTED SYMBOLS (`RTX_FUNC(...)` in `src/runtime/rtx/*.S`) | **54** |
| ESCAPE-FREE (GATE=0 **and** explicit-edges=0) | **1** |
| the one | **`rt_patstk_lazy_init`** — a lazy one-shot initialiser |

**The disqualifier is the family gate itself.** `RTX_GATE(fam, cfallback)` expands (`rtx_abi.inc:~77`) to:
```
cmp byte ptr [rip + rtx_gate_##fam], 0 ;  je cfallback
```
so **every gated symbol carries a runtime branch into its C fallback**, taken whenever the family gate is OFF. 53 of 54 carry a gate; most carry explicit `jmp/jcc c_*` fast-path bailouts on top (`rt_defer_open` 3, `rt_subscript_var` 9, `rt_size_d` 3).

⇒ **THE ENABLING CONDITION FOR RC-6 IS NOT "PORTED" (RTX migration step 2). IT IS "ERADICATED" (step 3: gate folded ON, C fallback deleted).** The RTCC charter's claim to *invert* the RTX dependency is half true: the register convention did flip first (RC-1..RC-5, landed), but **RC-6's payoff still sits behind per-family RTX eradication** — the dependency the charter believed it had removed. This is a sequencing fact the rung text does not state and a session opening RC-6 would discover only after choosing a target.

⛔ **AND THE ONE ELIGIBLE SYMBOL IS WORTHLESS AS A RUNG:** `rt_patstk_lazy_init` is the s223 `entries − 1 = commits` shape. A one-shot initialiser crosses O(1) times per program; bypassing it saves ~14 instructions **total**. **RC-6 as chartered has no measurable payoff available at HEAD.**

## 3. ⭐⭐ MY OWN INTERMEDIATE CONCLUSION WAS FALSIFIED ONE STEP LATER — RECORDED BECAUSE THE SHAPE REPEATS
Cross-referencing s11's measured crossings against the 54 ported symbols, I concluded **"roman's defer trio is RC-6's first lane"** (all three of roman's top-3 are in asm, 2,200,022 crossings each). One command later the escape census killed it: the trio carries 4, 2 and 2 escape edges. I then briefly held `rt_proc_open_fn`/`rt_flat_wire_adopt` as escape-free — **also wrong**, and wrong for an instrument reason worth naming:

⛔ **THE `.globl` / `RTX_GATE` MACRO TRAP (two faces, both bit me):**
(a) `grep '\.globl' rtx_*.S` returns **ZERO symbols** — entry points are declared through the `RTX_FUNC` macro. A census built on `.globl` reads as *"nothing is ported"*, the exact inverse of the truth (54).
(b) A census built on literal `jmp|call c_*` reads `rt_proc_open_fn` as **escape-free**, because its escape is the `RTX_GATE` **macro**, not a literal branch. **The most important edge in the file is invisible to the obvious grep.**
⭐ Same class as ARCH-SNOBOL4-RTX §0(c)'s exported/hidden split and s11's `LD_AUDIT` complement: *two things that are identical through the instrument you happened to pick.* **A census over assembly must expand the project's own macros, or it measures their absence.**

## 4. ✅ THE VENEER IS EXACTLY 14 INSTRUCTIONS PER CROSSING — MEASURED TWO WAYS, EXACT AGREEMENT
Emitted `fibonacci` mode-4, both arms, HEAD binary. Per crossing:

| part | count | detail |
|---|---|---|
| writeback | **9** | `mov [g_rtcc_block+0],rax` · `mov rax,[rip+g_rtcc_block@GOTPCREL]` · 7 stores `rcx rdx rsi rdi r8 r10 r11` |
| reload | **5** | `mov r11,[rip+…@GOTPCREL]` · 4 loads `r8 r9 r10 r11` |
| **total** | **14** | |

**CORROBORATION (the "check the census against a quantity you already know" law, and it caught a real denominator error):** the ON−OFF line delta is **784**. Naively `784 / 73 PLT sites = 10.73`, which contradicts 14. The denominator is wrong, not the cost: **only 56 of the 73 PLT sites are veneered** (17 are generated/libc targets, correctly excluded per NEVER-VENEER-A-GENERATED-TARGET). **56 × 14 = 784 — exact, to the instruction.** Counted independently: 56 `rax` absolute stores · 112 block-base loads (56 writeback + 56 reload) · 224 reload loads = 56 × 4 exactly.

✅ **H2 IS LIVE AT HEAD, VERIFIED IN EMITTED CODE:** `[rax+48]` (R9/GVA) is **absent from the writeback and present in the reload** — s8's BLOCK-CANONICAL EXCEPTION is true in code, not just documented. The writeback stores 7 and the reload restores 4; the asymmetry is coherent (writeback must keep the block canonical for inbound re-entrant edges, reload need only restore what generated code reads without re-staging).

⇒ **RC-6 NOW HAS THE STATIC, NOISE-FREE PRIMARY INSTRUMENT s12 DEMANDED:** `crossings_removed × 14 instructions`. It needs no rail and is immune to this box's ~1.12× floor.

## 5. THE PRIZE, QUANTIFIED (what RC-6b would remove; measured crossings from s11 × 14)
| workload | symbols (all already in asm) | crossings | instructions removed |
|---|---|---|---|
| **fibonacci** | `rt_proc_open_fn` · `rt_flat_wire_adopt` · `rt_sub` (2,692,537 ea) + `rt_add` (1,346,268) | 9,423,879 | **131,934,306** |
| **roman** | `rt_defer_open` · `rt_defer_get_pat_fn` · `rt_defer_close` (2,200,022 ea) | 6,600,066 | **92,400,924** |

⛔ Note what is NOT here: fibonacci's four hottest symbols (`rt_gc_point_arr`, `rt_arg_stage`, `rt_proc_get_fn`, `rt_goto_transfer`, 2.69 M each) are **not ported at all**, so they are not RC-6-eligible however hot they are. And the inherited target `rt_call_arr` is **doubly** disqualified — not in asm, and 4 executions on fibonacci (s11).

## 6. 📌 PROPOSED — **RC-6b · GATED BYPASS: MOVE THE VENEER FROM THE CROSSING TO THE ESCAPE EDGE** (⛔ LON RULES)
Instead of waiting for per-family eradication, make each hot asm body **SCRIP-convention-native**:
1. the asm fast path **preserves the claimed set itself** (it is asm; it simply must not clobber `r8 r9 r10 r11` and must re-stage rather than destroy the arg tier);
2. the asm body **brackets its own escape edges** — writeback immediately before `je c_fallback`, reload on return from C;
3. the registry then reclassifies the symbol NO-VENEER and **the call site emits zero of the 14 instructions.**

⛔ **THE TRAP THAT MAKES THE NAIVE FORM WRONG, STATED SO NOBODY REDISCOVERS IT:** if the fast path skips the writeback but generated code still reloads unconditionally, the reload restores **stale block contents** — silent state corruption, strictly worse than the toll. The writeback and the reload must be removed *together*, which is why this is per-symbol asm work and **not a registry flag.**
Cost: bounded, per-symbol, in `rtx_*.S` only — zero emitter bytes, zero template churn, both media unaffected. Prize: the §5 table. Grading: static (§4), no rail.

## 7. RULINGS I TOOK ON "ALL YOUR CHOICES" — EACH IS VETOABLE
1. **Workload mix (the file's ⛔ LON block) → per-family, option (b).** s11's data forbids a single rank (`rt_call_arr`: 4 on fibonacci, 100,005 on roman); an equal-weighted average blends a proc-call path with a deferred-eval path that share almost nothing and describes no program.
2. **Grading → static primary, rail as corroboration only above ~1.12×.** This box fails RC-0(a)'s own ≤1.05× criterion in three independent measurements. §4 supplies the static instrument, so RC-6 no longer needs the rail at all.
3. **RC-5 → CLOSE as landed/statically graded; the ANCHOR revert stays re-openable.** Untouched this session; §4's method (assemble, count, corroborate against a known quantity) is exactly what re-grading it requires.

## 8. NEXT
1. **Lon rules on RC-6b (§6).** If yes, first lane = **roman's defer trio** (one family, 3 symbols, 92.4 M instructions, one workload that exercises all three) — not fibonacci's, whose hot half is unported.
2. If no: RC-6 is **BLOCKED on per-family RTX eradication** and should be marked so in the rung text rather than left open — a session that opens it today will spend the rung rediscovering §2.
3. `scripts/util_rtcc_escape_census.sh` re-runs the eligibility count in ~1 s; re-run it after any RTX landing, since eradicating one family moves symbols from INELIGIBLE to ELIGIBLE and is the only thing that does.
