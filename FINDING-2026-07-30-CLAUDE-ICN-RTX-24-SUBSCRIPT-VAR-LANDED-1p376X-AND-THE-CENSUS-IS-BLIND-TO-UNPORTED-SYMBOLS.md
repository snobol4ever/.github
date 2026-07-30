# FINDING-2026-07-30-CLAUDE-ICN-RTX-24-SUBSCRIPT-VAR-LANDED-1p376X-AND-THE-CENSUS-IS-BLIND-TO-UNPORTED-SYMBOLS

**Rung:** RTX-24-ICN · **Session:** s222-ICN · **Ladder:** `GOAL-ICON-RTX.md` · **Contract:** `ARCH-ICON-RTX.md`
**Symbol:** `rt_subscript_var` (ledger: released s214 → ICON-RTX) · **Gate:** `SCRIP_RTX_ICNSUB`, the **fourteenth** family gate
⛔ **PUSH STATE IS NOT RECORDED IN THIS FILE.** Per RULES.md s47(a) a doc cannot know it. `scripts/handoff_status.sh` is the only ground truth.

---

## 1. RESULT

`rt_subscript_var`'s VARREF→DT_DATA-list arm is asm. **1.376× median, 1.373× min-min, DISJOINT sets** —
ON 83/96/88/86/84/83/87/87/86/110 ms vs OFF 115/143/119/117/123/119/114/119/336/119 ms, 10 interleaved
rounds, warmup discarded, `RT_OPT=-O0`, window `corpus/benchmarks/icon/bench_icnsub_list_dispatch.icn`.
Median and min-min agreeing to three digits is the robust signal; **the expectation (1.3–1.8×) was stated
in the source header BEFORE measuring** and the result fell inside it.

Gates: 0(j) **2,000,000 entries / 0 bailed / 2,000,000 commits** · two-sided falsification passed ·
Icon **252/11/30** unmoved (re-derived on the final bytes) · SNOBOL4 m4 **324/2** unmoved.

**Where the win comes from:** `rt_list_view` (`pattern_match.c:21`, `static inline`) discriminates a list
from a record by **`strcmp(fields[2].s, "list")` on EVERY subscript**, plus `strcmp(type->fields[0],
"frame_elems")` on every cache miss. At `-O0` those are real calls. The asm replaces them with a dword
compare + a NUL test, and a qword+dword compare, inline. ⭐ **This is the RTX-13-ICN by-name disease in a
SECOND family** — SCRIP is comparing a STRING at run time, per access, to answer "is this a list".

---

## 2. ⭐⭐ THE CENSUS IS STRUCTURALLY BLIND TO AN UNPORTED SYMBOL, AND IT REPORTS THAT BLINDNESS AS A ZERO

`util_rtx_arm_census.sh` measures by counting `sym` vs `c_sym` — it derives its symbol list from the built
`.so` and keeps only names that have BOTH halves (`scripts/util_rtx_arm_census.sh:43-49`). **An unported
symbol has no `c_` half, so it is omitted entirely**, and the tool's footer then reads *"symbols with zero
entries are omitted: this workload cannot grade them at all."*

Run on a subscript-saturated window, it printed **no `rt_subscript_var` row at all** while the symbol was
in fact taking **2,000,000 calls per run**. Read naively that is a refusal signal — the same shape as a
genuine COLD verdict, and step 0(h) says `COMMITS==0 ⇒ must not be written`.

⇒ **RULE, PROPOSED FOR `ARCH-ICON-RTX.md` §8: 0(d) and 0(j) are TWO INSTRUMENTS FOR TWO PHASES AND THE
LADDER HAS BEEN CITING ONE NAME FOR BOTH.** 0(d) on an unported symbol MUST use the LD_PRELOAD interposer
(`scripts/util_rtx_icn_0d_*.c`). 0(j) is a POST-port instrument only. A census silence on an unported
symbol is **not** evidence of coldness; it is evidence of nothing.

---

## 3. ⭐⭐ PORT THE ARM THE GUARD REJECTS — RTX-6'S LESSON, RE-LEARNED THE EXPENSIVE WAY

The arm was first written to reject VARREF bases, on reasoning that looked airtight: a varref is `DT_N`,
so `cmp edi, DT_DATA` excludes it *for free*, and the guard doubles as the IS_VARREF test.

**The live traffic is 100% varref.** Measured shape (interposer, first five calls, identical):
`base.v=9 (DT_N) · base.slen=1 · base.p=<frame-slot address>` and `idx.v=6 (DT_I)`. Because
`rt_subscript_var`'s own first act is `DESCR_t bvar = base; if (IS_VARREF_fn(base)) base = rt_deref(base);`
— the function is *designed* to be handed a variable.

First census after building: **2,000,000 entries / 2,000,000 bailed / 0 COMMITS. VACUOUS.**

Fix: call the already-asm `rt_deref` at entry, and spill the four original argument registers to the frame
so **every** bail still tail-jumps to C with byte-identical arguments — the byte-identity proof path
survives the fact that the arm must deref before it can even tell whether it applies.
⇒ **s211's rule generalises past templates: it is not only "read the emitting template for an inline tag
guard", it is "read what the CALLEE does to its own first argument before you decide which tag arm is live."**

---

## 4. ⭐⭐⭐ AN INSTRUMENT THAT EXCEEDS WALL TIME IS NOT AN INSTRUMENT — AND ITS ANSWER WAS CONVENIENT

To discharge (d2) on an unported symbol I built an rdtsc self-cost interposer: bracket the target
inclusive, bracket each already-asm callee inclusive, report `SELF = INCLUSIVE − Σcallees`. It reported
**`subvar_incl=813,676,867` cycles (~271 ms at 3 GHz)** and a very quotable **`self_pct_of_incl=91.8%`**.

The same program's entire **uninstrumented** run is **36 ms**. The instrument attributed to one symbol
~7.5× the whole program's runtime. `rdtsc` itself was measured at 29.8 cycles (not trapped), so the
inflation is in the attribution, not the clock.

**It was DISCARDED, not reported.** Replacement, which cannot exceed wall time by construction:
**wall-clock differential** — run the window, then run the identical window with the construct deleted and
the arithmetic retained. Subscript present **904/940/952/920 ms**; subscript deleted **96/96/91/93 ms**
⇒ ~836 of ~930 ms, **~90% dominance**, spreads 1.05× each arm, non-overlapping.

⇒ **PROPOSED §8 CLAUSE: any cost-share instrument must be bounded by a wall-clock total measured in the
same session, and the bound must be stated next to the share.** §8 already says *"A SILENT PROBE IS A
QUESTION, NOT AN ANSWER"*; this adds the sibling — **a probe that lies LOUDLY is worse than one that says
nothing, because its number is publishable.** 91.8% and ~90% agreeing was luck, not validation.

---

## 5. ⚠ AN ALLOCATION-SCALING WINDOW GOES BIMODAL, AND MORE ROUNDS CANNOT FIX IT

The 8M-iteration window carves 8M × 72 B ≈ **576 MB** of `VCELL_t`. Spreads: **OFF 3.44×** (927→3187 ms),
**ON 1.93×** (813→1565 ms) — the `RTX-0C` hugepage-compaction instability, and s211's documented refusal
condition (*"the spread is multiplicative"*). The 2M window: ON spread 1.33×, arms DISJOINT.
⇒ **Graded at 2M deliberately, below the MIN_MS=800 preference, because a disjoint pair of tight arms is
worth more than a bimodal pair of long ones.** s221's "use more rounds" applies to an OUTLIER; it does not
apply to a multiplicative spread.

---

## 6. ⛔ TWO ASSEMBLER TRAPS, ONE OF WHICH WOULD HAVE SHIPPED SILENTLY

**(a) `DT_DATA` IS ABSENT FROM `rtx_abi.inc`** — the tag list stops at `DT_FAIL 99`. With it undefined,
**`cmp edi, DT_DATA` ASSEMBLES CLEANLY** as a relocation against an undefined external symbol. Only the
memory-operand form (`cmp dword ptr [r9+k], DT_DATA`) is ambiguous enough for `as` to reject. **One line of
two was caught, by accident.** The register compare guards the entire arm — it would have linked against
whatever the loader resolved and admitted the wrong datatype. Defined locally in `rtx_icnsub.S` (not in the
shared header — that is SN4-RTX rebase surface) and pinned by `_Static_assert`.

**(b) GNU as Intel syntax parses `k*CONST` inside brackets as index\*scale, not a constant fold.**
`[r9 + 0*DESCR_SIZE]` is "index register 0, scale 16" and fails to assemble. Precomputed literal offsets
(`FIELD0_V`/`FIELD0_P`/`FIELD1_P`/`FIELD2_V`/`FIELD2_P`) with the arithmetic in the NAME.

**(c) Alignment.** Entry `rsp == 8 (mod 16)`; SysV wants `0 (mod 16)` AT the call ⇒ the frame adjustment
must be `== 8 (mod 16)`: **8/24/40/56 work, 16/32/48 do NOT.** An earlier draft used four pushes
(`8+4*8 ⇒ rsp==8` at the call) and would have handed `rt_agg_alloc` a misaligned stack — which does not
fault, it corrupts quietly the moment anything below uses an aligned SSE spill. Final form touches **zero**
callee-saved state: no pin borrowed, and r12 not taken as scratch-by-fiat.

Six drift guards added to `rtx_init.c` pinning the **probed** (`offsetof`, not remembered) layouts:
`VCELL_t` size 72 and all six field offsets · `DATINST_t.type/.fields` · `DATBLK_t.nfields/.fields` ·
`sizeof(DESCR_t)==16` (the `shl rcx,4` scale) · the four DT tags.

---

## 7. ⭐ THE GOAL FILE DISAGREED WITH THE LEDGER ON ALL THREE CONCURRENCY ROWS, AND THE LEDGER WINS

`GOAL-ICON-RTX.md` §Concurrency read *"Already claimed by SN4-RTX: `rt_call_arr` · `rt_num_arith` ·
`rt_subscript_var`."* `RTX-CLAIMS.md` — the file that declares itself **THE SINGLE SOURCE OF TRUTH** —
says `rt_call_arr` is **ICON-RTX's by Lon's s208 ruling** (`OUT:ICON-RTX`) and the other two were
**RELEASED at s214** under the ABANDON rule after nine and ten unworked sessions.

**Following the goal file would have parked a symbol that had been ours for eight sessions.** RULES.md s47
class (a): stale prose in a block nobody re-reads. Corrected. ⇒ **Orientation must read `RTX-CLAIMS.md`
for ownership and treat every goal-file ownership restatement as a copy that may have rotted.**

Also corrected: the s221 benchmark seeds are in `corpus/benchmarks/icon/`, **not** `benchmarks/icon/rtx/`
as RTX-21/RTX-23 state.

---

## 8. WHAT THIS RUNG DOES **NOT** FIX — AND IT IS BIGGER THAN THE RUNG (⇒ RTX-25-ICN)

`t := L[i]` in an **RVALUE** context carves a **72-byte `VCELL_t` purely to NAME a cell**, and
`bb_subscript.cpp`'s consumer immediately `rt_deref`s it and discards it. Measured: 2,000,000 subscripts ⇒
**2,000,000 `rt_agg_alloc` calls**, none of them needed; at 8M the resulting carve is what makes the window
bimodal (§5). Canonical Icon does not allocate to fetch a list element
(`refs/icon-master/src/runtime/fstruct.r`, `oasgn.r`).

This is why RTX-24's ceiling is 1.376× and not more: **the allocation is not removed.** Stated in the
source header before measuring, so the number is a confirmation rather than a surprise — the RTX-4 /
RTX-8d shape in miniature, predicted in advance and then observed.

⇒ **RTX-25-ICN: an rvalue subscript arm that returns the VALUE and never mints a VCELL.** DESIGN rung of
the RTX-14-ICN class, not an asm port. ⛔ Touches `bb_subscript.cpp` ⇒ `.s` regen ×3 and direct ζ-ladder
collision ⇒ **SERIALIZE WITH LON.** RTX-24's asm is not wasted by it: that arm remains the **lvalue** path
(`L[i] := v`).

---

## 9. STILL LON'S, UNTOUCHED BY THIS SESSION

- **RTX-23-ICN / RTX-17-ICN** — both need the **§7 re-assignment of `str_concat_d` / `rtx_str.S`** from
  SN4-RTX (row is `DONE:SN4-RTX`). Premise re-verified s222: **2,000,000 entries / 2,000,000 bailed /
  0 commits**, and `rt_str_alloc` fires **4,000,000** (2×/iteration), confirming s221's ⅓-dispatch
  constraint. A broad session grant does not dissolve a cross-ladder collision rule.
- **RTX-0-RULING (a)/(b)** — unchanged.
- ⚠ **The Prolog watermark is unobtainable in this container.**
  `scripts/test_corpus_prolog_parser.sh` reports **737/737 crash at gate ON *and* gate OFF** ⇒ the
  differential is an identity and it is pre-existing/environmental, **not this rung's**. Same shape as
  s210's "the shared watermark is FALSE AT HEAD": use the three-way ON/OFF/PRISTINE differential until the
  harness is repaired. **I assert no culprit** — naming one on a guess is the s209 mistake.
- ⚠ **Pre-existing ledger rot, reproduced exactly, not fixed:** `util_rtx_claims.sh` BLOCKED, 3 fatal —
  `rt_frame` phantom; `rt_defer_open`/`rt_defer_close` asm with rows not `DONE` (SN4-RTX's to close).

---

## 10. PROTOCOL DEVIATION, STATED PLAINLY

`RTX-CLAIMS.md` requires the check-out **pushed before the work**. No credential was available in s222, so
the claim was **committed** ahead of the port but **not pushed** ahead of it. The ordering is honest in the
history; **the protective property — another session seeing the claim before spending itself — was NOT
obtained.** Identical in shape to s211's deviation. The s202 ancestry check
(`git rev-list --count origin/main..HEAD == 0`) is **unsatisfiable this session**, so RTX-24-ICN's `[x]`
must not be read as landed on origin.

---

## FILES

**SCRIP** (`93b247f`, local): new `src/runtime/rtx/rtx_icnsub.S` · `src/runtime/pattern_match.c`
(`rt_subscript_var` → `c_rt_subscript_var`) · `src/runtime/rtx/rtx_init.c` (gate + 6 asserts + `core.h`) ·
`Makefile` (`RT_PIC_SRCS`) · new `scripts/util_rtx_icn_0d_subscript.c` ·
new `scripts/util_rtx_icn_selfcost.c` (**the discarded instrument, kept as a NEGATIVE result** — §4).
**Zero templates, zero `x86_asm.h` ⇒ no `.s` regen owed.**
**corpus** (`aee2357`, local): `benchmarks/icon/bench_icnsub_list_dispatch.icn`.
**.github** (`2bb42ac`, local): this FINDING · `GOAL-ICON-RTX.md` cursor s222 + RTX-25/RTX-26 minted +
three stale-doc corrections · `RTX-CLAIMS.md` row.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
