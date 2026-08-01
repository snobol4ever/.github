# FINDING — ICN: THE WHACK OUTLIVED ITS ENTER, AND FOUR CURSOR NUMBERS DO NOT REPRODUCE

**Session:** s206 (2026-08-01) · **Goal:** `GOAL-ICON-BB.md` → ICN-FB-0 / ICN-CARVE
**Tree:** SCRIP `dda156eb` (fresh clone, origin/main), from-scratch build, **RT_OPT=`-O0`**
**Corpus:** `corpus` @ origin · Icon benchmarks (20) · `test_icon_all_rungs.sh` (293)

---

## ⭐⭐⭐ HEADLINE 1 — FOUR INHERITED NUMBERS DO NOT REPRODUCE AT ORIGIN HEAD

Re-derived fresh, never from prose:

| quantity | s204/s205 cursor | **measured s206** |
|---|---|---|
| Icon suite (`--run`) | 238 / 25 / 30 | **184 / 79 / 30** |
| `SCRIP_BB_ALLOC=0` | 245 / 18 / 30 | **184 / 79 / 30 — INERT** |
| Icon `[rbp±N]` data refs | 39,193 | **37,872** |
| unseeded refs (s200: Icon benches) | 0 | **6,264** |

`SCRIP_NOFC=0` is also **inert on Icon**: it moves 96 of 37,872 data refs (0.25%).
`SCRIP_NOFC_CARVE=1` is inert. Ceremony re-measured **1,327** (873 under the narrower
seed+push/pop definition, vs the cursor's ~830).

**WHY, AND IT IS NOT A REGRESSION TO BE REVERTED.** All four of s204/s205's cited SCRIP
hashes (`7b974446`, `ed3d95a9`, `85fc743e`, `8f1a1a21`) are **ABSENT FROM ORIGIN** — the
numbers were measured on working trees carrying unpushed local commits, which is exactly the
shape `RULES.md` → STALE-ORIENTATION (a) forbids. ⚠ The ICN-JCC fix is nonetheless present at
HEAD, because a THIRD session re-landed it independently (`91b623a0`), and a FOURTH hit the
same defect from the js/jns side (`2aec9a4b`). **That fix has now been paid for three times.**

The suite gap is explained by HEADLINE 2, not by the JCC fix.

---

## ⭐⭐⭐ HEADLINE 2 — THE OUTER WHACK FIRES UNCONDITIONALLY; ITS ENTER DOES NOT

**Two predicates that must agree had drifted into logical complements:**

- **seed** (`emit.cpp:2153`) fires iff `nparams==0 && !flat_jmp_entry && !flat_pat && !flat_gen && !g_gen_proc_active`
- **whack** (`bb_glue_flat.cpp` `bb_glue_outer_whack()`) returned **`true` unconditionally**, and
  both `bb_glue_outer_γ/ω` emit `IF(whack, bb_glue_framed_leave())` = `mov rsp,rbp; pop rbp`

So **every pat / gen / jmp-entry / gen-proc graph whacks against a base it never established.**
`bb_glue_framed.cpp`'s own header names this shape four lines above the offending function:
*"Reversing (1)/(3) or omitting (1) while keeping (3) loads the CRT caller's rbp into rsp."*
**The tree was in the exact state its own comment names as the failure mode.**

**7-LINE REPRO** (`/tmp/gen.icn`) — the deterministic witness this rung previously lacked:
```icon
procedure g()
  suspend 1;
  suspend 2;
end
procedure main()
  every write(g());
end
```
`proc_g` region: **push rbp = 0 · mov rsp,rbp = 2 · pop rbp = 3** → rc=139.
Discriminator confirmed: swap `suspend`→`return` and the same procedure emits **seed=YES,
rbp_data=0**. The `suspend` (⇒ `flat_gen`) is what splits enter from whack.

**THIS IS NOT A REGRESSION — IT IS INHERITED DEBT FROM AN INTENDED DEMOLITION.** `CARVE-KILL`
(`ef9a7d2c` + `1ba33ea6`, Lon: *"Delete the prolog and epilog … We want a nice broken system to
build from with just the BB's to build around"*, **"Breakage accepted by explicit instruction"**)
deleted `xa_flat_prologue`, which is precisely what used to seed rbp for those classes. The
surviving whack kept a `true` written when the prologue still covered the remainder. **The
6,264 unseeded refs are therefore NOT the s188/s189 drift defect — they are the CONVERSION WORK
LIST**, and any instrument that zero-asserts them on this tree asserts the wrong contract.

---

## ⛔ THE OBVIOUS FIX WAS TRIED FIRST AND FALSIFIED — DO NOT RE-DERIVE IT

**Forcing the ENTER to fire** for pat/gen/jmp-entry (so it matched the unconditional whack)
scored **184/79/30 → 181/82/30, THREE PROGRAMS WORSE.** The pinned classes decline the push
**deliberately**: a jmp-entry graph's base is established by its CALLER, a dc-prep graph's by
`rt_pl_dc_prep`, so an extra `push rbp` shifts rsp under offsets computed against the real base.
**The enter is right; the whack was the drifted spelling.**

**LANDED (opt-in, default OFF): `SCRIP_GLUE_SYM=1`** — `g_glue_entered` is recorded at the enter
site and read by `bb_glue_outer_whack()`. One decision, recorded once, consulted by its own
counterpart — the shape `zc_nofc` and `x86_jcc_invert` were both collapsed into after drifting
as two spellings.
**MEASURED: Icon 184/79/30 → 184/79/30, EXACTLY INERT**, while the repro's whack goes 2→0 and
its pop imbalance 3→1. A provable ABI violation removed at zero suite cost: **correct but
dominated.** ⛔ Default flip needs SNOBOL4 + Prolog watermarks re-proven (shared emitter) —
per the s203 ZW-1 lesson that an opt-OUT flip of a shared default cost Icon 30 programs while
the ledger recorded a SNOBOL4 accounting.

⚠ The repro still SEGVs with the flag on (push=0 / pop=1 residual). **The whack was one of at
least two faults on that path; the remaining stray pop is the next bracket.**

---

## ⭐⭐ WHERE THE LADDER ACTUALLY STANDS (the directive is already the architecture)

`bb_glue_flat.cpp` / `bb_glue_framed.cpp` — the "simple glue" that replaced the prologue —
already implement the target model:
- **flat glue** — `sub rsp,K` at α, `add rsp,K` at γ/ω, per-BB, no prologue.
- **framed glue** — `push rbp; rbp=rsp` at outermost α ONLY; *"graph body runs, rsp wanders
  freely (non-popping FORTH spine)"*; `mov rsp,rbp; pop rbp` at γ/ω discards the activation
  wholesale, *"no per-box pop"*.

That IS non-popping FORTH RSP ζ with C-style RBP only where necessary. **The residue is that
Icon's 37,872 data refs still NAME rbp**, and 6,264 sit in graphs receiving neither glue.
**NEXT RUNG: route every Icon graph to one glue or the other**, then convert flat-glue graphs'
refs `[rbp+N]` → `[rsp+off−fc_base]`. The 6,264 is the exact target list, per-file in the census.

---

## ▶ INSTRUMENT LANDED — ICN-FB-0

`scripts/util_icn_rbp_census.py` + `scripts/test_gate_icn_rbp_census_ratchet.sh`.
A (ceremony) / C (data) / D (scratch) + per-region prologue-seed split. Class D = **0** on Icon,
re-confirming s204.

**FALSIFIABILITY PROVEN BEFORE FIRST USE** (the s203 instrument law), 4 synthetic fixtures:
seeded → A=4/C=2/rc=0 · unseeded → drift=1/rc=1 naming the offending line · clean → all-zero ·
scratch → D=1/C=0. It discriminates at BOTH ends.

⛔ **ITS DRIFT ZERO-ASSERT IS THE WRONG CONTRACT FOR THIS TREE** and must be converted to a
DESCENDING RATCHET (work-remaining) before use as a gate — see HEADLINE 2. Left failing
deliberately rather than silently re-baselined, so the next session sees the real state.

---

## ⚠ METHOD NOTES (two of my own errors, recorded so they are not repeated)

1. **A DRIFT↔CRASH CORRELATION WAS BUILT AND WITHDRAWN.** 7 of 9 drifting benchmarks return
   rc=139, which looked decisive. It is not: `options`/`post`/`shuffle` are **link-dependency
   libraries with no `main`** (`LINKDEPS` in `honest_icon_bench.sh`), so running them standalone
   is meaningless, and `bench_icnint_loop` **prints its correct answer `2000001000000` and only
   then dies on teardown**. Benchmark rc is not a correctness signal without the harness.
2. **INSTRUMENT-AGREES-WITH-INSTRUMENT IS NOT GROUND TRUTH.** `util_rbp_region_census.py` and
   the new one agreed on 6,264 — they share region-splitting logic, so the agreement was
   worthless. The bytes settled it. Note `ENTRY_RE` matches neither `main_α:` nor
   `proc_*_dcα:`, so those regions are absorbed into whatever precedes them; the seed can
   therefore be attributed to the wrong region. **Verify by reading the .s, not by a second run.**

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
