# ARCH-PROLOG-RTX.md — Contract for the `PL-RTX` ladder

**Minted s221-PL (2026-07-30).** Ladder: `GOAL-PROLOG-RTX.md`. Ledger: `RTX-CLAIMS.md`.

## ⛔⭐⭐⭐⭐ LON DIRECTIVE 2026-09-26 — UNIFICATION MIRRORS THE SNOBOL4 MATCHER: r13/r14/r15 THE SUBJECT, r12 THE BINDING STACK (CEO-1279)

**Lon, in-chat to the ceo, 10:2x CDT, verbatim:** *"The Prolog unification needs to mirror SNOBOL4's pattern matching, using R13, R14, and R15, and also R12 as a stack."*

**The plane it names** (`ARCH-SNOBOL4-RTX.md` §1): r13 = Σ the subject base, r14 = δ the subject cursor, r15 = Δ the subject length/end, r12 = the conditional-assignment stack top (Lon's directive of 2026-08-02; the CAS base is a MATCH_BEGIN frame slot, never a register). **Read for Prolog:** unification is pattern matching over a term's cells — r13 the base of the term being walked, r14 the cursor over its cells, r15 its end — and a binding is a conditional assignment: pushed on the r12 stack as it is made, undone from that stack on backtracking (the trail IS the CAS twin, which is what this plane already keeps in r12). The get, put and unify steps are emitted boxes with α/β/γ/ω ports exactly as a SNOBOL4 pattern node is (`ARCH-PROLOG-BYRD-BOX-TRANSLATION.md`), and the C walk — `plw_unify_cells`, `plw_cell_deref_slow`, `plw_bind`, `plw_mkc_kids`, `rt_pl_deref_val`, `rt_pl_dop_unify_ci_c` in `src/runtime/by_name_dispatch.c` — is deleted, not wrapped.

**What the plane pins today, measured 2026-09-26 (SCRIP `b6d8c9bb8`):** r12 = TR, the trail top (`rtx_plunify.s` CTX_TR); r13 = B, the choice point / barrier (`rtx_plunify.s` CTX_B; `bb_bound.cpp:22` saves it at a fence); r14 = nothing in a Prolog graph (the Σ/δ scan reservation of `GOAL-PROLOG-100.md`'s contract of record, line 89; scratch inside the unify leaf); r15 = the exception ball, a collected-heap pointer (`PL_BALL_ARM`/`PL_BALL_DROP`; the 2026-09-20 finding at line 362: r15 is an integer LENGTH in the SNOBOL4 plane and a POINTER here, and the shared GC shield hard-codes the SNOBOL4 reading). **The consequence the directive carries:** B and the ball leave the registers for slots — the trail arena header already carries a ball slot (`PL_TR_BALL_SLOT`, the finding's candidate A, ζ-STANDING), and B takes a frame or arena slot the same way — so that r13/r14/r15 mean the same kind in every plane and the collector's register shield needs no per-language reading. The cost was measured before the directive: unification, dereference and binding as C calls are 30–45% of nreverse (0.05x swipl), queens_8 (0.30x), zebra (0.10x) and fib (0.51x) in mode 4 (README § Prolog at SCRIP `a6d057a31`; CEO-1278). The row: `prolog-speed-get-put-and-unify-are-emitted-inline-not-c-calls-per-cell-…` (hq_prolog, rank 1, criterion `bench_prolog_bar.sh kernel nreverse 1.0`).

## 0. ⛔ THIS CONTRACT DELIBERATELY DOES NOT RESTATE STEP 0

**The shared checklist is `ARCH-SNOBOL4-RTX.md` §7. READ IT THERE.** Icon's additions live in
`ARCH-ICON-RTX.md` §5(ii) and §8. Nothing is copied here.

**REASON, and it is a measured one, not a preference:** `GOAL-PROLOG-BB.md` §"SESSION-CLOSE RULES" deleted
two FACT RULES it had carried verbatim from `RULES.md` as *"pure duplication … the copy could only ever go
stale against its own source"*, and its §"NOTE ON BYTE-IDENTICAL CLAIMS" measured **12 of 14** cross-file
lockstep assertions FALSE. A third copy of step 0 would rot the same way. ⇒ **this file records only
where Prolog DIFFERS.**

⚠ **THE STEP LETTERS HAVE ALREADY FORKED between the two existing contracts** (s216-ICN: SN4 filed the arm
check as step (f), Icon's (f) was already the `@PLT` check, so Icon adopted it as 0(j)). **PL-RTX refers to
shared checks BY NAME — "THE ARM CHECK", "THE RELEVANCE CHECK", "THE ALREADY-PORTED CHECK", "THE OBJECT-FILE
LINKAGE CHECK", "THE EMITTING-TEMPLATE CHECK" — never by letter.** A shared check needs a shared name.

## 1. WHAT IS THE SAME
Register discipline, pin conventions, `.intel_syntax noprefix`, per-family gate byte + `c_*` fallback,
`RTX_FUNC` macros, `rtx_abi.inc`, the ON/OFF/PRISTINE 3-arm rule, the kill-switch hash-SET gate
(N≥4/arm), TEMPLATE-ONLY EMISSION and BOTH-MEDIUM from `RULES.md`. **Phase 1 keeps every exported C
signature exactly** — speed comes from bodies, not the call convention, so **no `.s` regen fires.**

## 2. ⭐⭐ WHAT IS DIFFERENT — PROLOG'S THREE DELTAS

**(1) THE SINK COLLISION IS THIS LADDER'S GOVERNING CONSTRAINT, AND IT HAS NO ANALOGUE ON THE OTHER TWO.**
`GOAL-PROLOG-BB.md`'s PL-SINK ladder makes the EMITTER inline a fast path for a lowered `$op`. That
**removes the arrivals an asm port of the callee would accelerate.** ⇒ **A LANDED SINK RUNG MAKES THE
CORRESPONDING RTX RUNG VACUOUS BY CONSTRUCTION.** Measured: `rt_pl_dop_trail_mark`, **5,814 static sites,
22 dynamic calls corpus-wide** (= 1/program = setup floor), because `src/templates/bb_call_fn.cpp:347` is
PL-SINK-8's inline path and names the runtime symbol *"the slow-path oracle."*
⇒ **MANDATORY PER-RUNG PRECONDITION, before the shared step 0 even starts: grep the target's `$op` in
`GOAL-PROLOG-BB.md`'s PL-SINK ladder and record the rung's status (landed / open / none).** A landed SINK
rung is a REFUSAL. An open one is a **collision** requiring the §SCOPE ruling.

**(2) THE COMPILE-PHASE FLOOR IS ZERO FOR THE `dop` FAMILY — MEASURE IT, DO NOT INHERIT EITHER VERDICT.**
ICON-RTX's ranking was ~100% compile phase (voided s220) and its method of record is
`count(4N) − count(N)`. Prolog's `rt_pl_dop_*` symbols are **emitted-code-only**: measured **ZERO on
`hello.pl`**, so absolute counts already ARE run-phase counts. The delta method stays correct and is not
load-bearing here. ⇒ **Every ladder measures its own floor with one trivial-program run. The confound is
family-specific.** ⚠ Non-`dop` targets (`rt_proc_*`, `rt_arg_stage`, `core_lib_init`) are **not** covered
by this result — re-measure per family.

**(3) SCALED DRIVERS DIFFER IN EXACTLY ONE TOKEN.** The van Roy benchmarks carry their size as an inlined
constant, so scaling them changes the program TEXT and therefore the compile phase. **Generate N and 4N
drivers whose `diff` is one line** (the loop count), which makes the compile phase identical by
construction rather than by argument — and only then is the floor measurement in (2) interpretable.

## 3. ⛔ TWO PROLOG-SPECIFIC HAZARDS
**(a) THE `dop` DISPATCH IS NOT THE COST — THIS IS ALREADY MEASURED AND TWO RUNGS DIED ON IT.**
`GOAL-PROLOG-BB.md` PL-SINK-6/7 were sold on deleting `dop_ax`/`dop_cmp`'s per-call `strcmp` dispatch
chains. **Measured s147: those chains are DEAD CODE** — `rt_pl_dop_ax_add/sub/mul` and `dop_cmp_fast`
already fast-path int×int and **return before the dispatch is entered**; an opcode-dispatch fix measured
**1.018×/0.989×/0.997× = noise** and was reverted. ⇒ **the remaining cost is the CALL (marshal + PLT +
`DESCR_t` return), not the dispatch.** Do not re-sell either rung on the dispatch. **Do not 'fix' the
dead chain again.**
**(b) THE DOUBLE-COMPARE TRAP IS A CORRECTNESS TRAP, NOT A PERF ONE.** The C compare path compares ints
**via `double`**, so a naive inline int-compare **DIVERGES above 2⁵³** (a=2⁵³, b=2⁵³+1: C says
equal-not-less, int compare says less). Range-guard with `movabs ±2⁵³` and bail outside, or replicate
exactly with `cvtsi2sd`/`comisd` — ⚠ `x86_asm.h` has only ~12 xmm hits, so **verify the encoder forms
exist for BOTH media before choosing** (RULES.md: add the encoder, never hand-encode in a template).

## 4. GATES — THE PROLOG WATERMARK
`bash scripts/test_prolog_rung_suite.sh` ⇒ **164/164 interp + 164/164 compile, FAIL=0** (established
s221-PL at `b1ca896e`, full build `-O0`). ⛔ **Re-prove at session start before touching anything and say
the numbers out loud** — the SN4 contract's §7 step 3 records its own watermark constant going stale for
five sessions, and `RTX-CLAIMS.md`'s s210 inbox records a shared watermark that was **false at HEAD**.
⛔ **This ladder owes SNOBOL4 and Icon watermarks on any SHARED symbol** (ledger hard rule 2) — and per
§7 step 2b **may cite none of them as evidence the asm executes.**

## 5. MODES
Two only: mode 3 (`--run`, BINARY in-process) and mode 4 (`--compile`, TEXT → as+gcc). One `.S` source
links into both, so they are identical by construction. ⛔ **Do not close a session on m3 alone**
(s214-SN4: m4 had not been run for ≥11 commits and was dead tree-wide on one hidden symbol).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
