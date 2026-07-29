# FINDING-2026-07-29-CLAUDE-ICN-RTX-6B-JCT-RELOP-LANDED-1p761X-AND-THE-INHERITED-RECON-WAS-FALSIFIED-BEFORE-IT-WAS-SPENT

**Session:** s212-ICN · **Ladder:** `GOAL-ICON-RTX.md` · **Rung:** RTX-6b-ICN
**Rung:** RTX-6b-ICN · **Symbol:** `rt_jct_relop` · **Gate:** `SCRIP_RTX_ICNREL` (ninth family gate)
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude

---

## ▶ RESULT

`rt_jct_relop` ported to `src/runtime/rtx/rtx_icnrel.S` behind `SCRIP_RTX_ICNREL`; C body renamed
`c_rt_jct_relop` in the same commit. **ON/PRISTINE = 1.761×**, `RT_OPT=-O0`.

| arm | median | raw samples |
|---|---|---|
| PRISTINE | 1872.5 ms | 1887 1846 1892 1858 |
| OFF | 1811 ms | 1803 1874 1819 1792 |
| ON | **1063.5 ms** | 1051 1130 1076 1026 |

Arm spreads 1.025× / 1.046× / 1.101× against a **1.761× gap** — the widest arm spread is a sixth of
the gap, and **ON's slowest sample (1130) is 63% faster than PRISTINE's fastest (1846)**: the
distributions do not approach each other. Kill-switch tax OFF/PRISTINE **1.034×**. Legacy two-arm
number would have read 1.703×, so **the artifact in this rung is small but real (0.058)**.

**PRISTINE `.so` md5 `646f9cb351f2bfa2dd0b757fe9db5941` — byte-identical to the session baseline
taken before any edit**, so the honest arm is provably the untouched runtime, and `nm` shows it
carries no `c_rt_jct_relop` residue. All three arms print `chk: 305000000` byte-identically.

**Gates, each re-derived fresh, identical ON and OFF:** Icon **252/11/30** · SNOBOL4 m4 broad
**284/42** · Prolog **188/0/1**.

**Falsification two-sided and NOT silent.** Corrupting a RESULT (not a route) on the hottest arm —
the `SEQ`-on-equal-strings answer — gave gate ON **244/19** (8 tests broke ⇒ the asm executes) and
gate OFF **252/11** (⇒ the switch switches). Restored `.S` md5-verified against the pre-corruption
backup and the watermark re-derived to 252/11/30.

---

## ⭐⭐ THE TRANSFERABLE CONTENT #1 — THE INHERITED RECON WAS WRONG, AND CHECKING IT COST ONE GREP

s211's handoff and the RTX-6b rung text both state, as a free gift to this session:

> `bb_binop_relop.cpp` has **NO inline tag guard**: zero `cmp DT_*`/`je` before any call, and
> `rt_jct_relop` is called **unconditionally at five sites**.

**Both halves are false.** Measured s212 on the same file at the same HEAD:
- it **has** guards — `cmp eax, DT_DATA` ×2 and `cmp eax, DT_I` ×2, at lines 23-32 and again 107-116;
- `rt_jct_relop` is called at **four** sites, not five.

The consequence was not cosmetic. The recon's conclusion was *"no guard ⇒ the callee's own dispatch is
the whole story ⇒ the textually-first arms may genuinely be live."* Acting on it means porting the
int-int arm. **The `DT_I` guard means int-int is inlined by the template and reaches the symbol ZERO
times** — measured: a positive-control program comparing `i < 1000` 2,000 times produced **0** arrivals
under that op while its string and real comparisons produced 8,000. Porting on the inherited recon
would have measured **~0**, which is RTX-1-ICN's error for the **third** time on this ladder.

⭐ **THE RULE THIS PAYS FOR: A RECON HANDED FORWARD IS A CLAIM, NOT A MEASUREMENT — RE-RUN IT.**
`GOAL-ICON-RTX.md` already says *"do not inherit any of this as settled"* about the s208 inbox and
step 0(h) already says *"the FINDING set is truth; the checkbox is a claim."* **Extend 0(h) explicitly
to recon prose:** a previous session's grep result is exactly as perishable as its checkbox, and the
grep that re-checks it is as free as the one that produced it. s211 recorded the recon *"on the rung
rather than in the handoff alone so the next session cannot route off a bare checkbox"* — the
mechanism worked, the content was wrong, and only re-running caught it.

---

## ⭐⭐ THE TRANSFERABLE CONTENT #2 — THIS IS A THIRD ARM REGIME, AND BOTH ENDS ARE LIVE

Step 0(d)+0(g) were run as one instrument: an `LD_PRELOAD` interposer binning **every** call by
operand tag pair and by op, across the **whole 303-program Icon corpus**.

**Reach:** only **34 of 303** programs call the symbol at all; **4,308 calls** total.

| operand pair | calls | | op | calls |
|---|---|---|---|---|
| **S/S** | **2892 (67.1%)** | | **SEQ** | **2012 (46.7%)** |
| I/I | 428 (9.9%) | | EQV | 805 (18.7%) |
| R/I | 358 | | SNE | 325 |
| S/I | 219 | | GE | 292 |
| R/R | 192 | | NEQV | 265 |
| I/S | 118 | | GT · EQ · SGT · LT · SLT · LE · NE · SLE · SGE | ≤109 each |

Mapping ops onto `rt_jct_relop_impl`'s arm chain:
- **SEQ+SNE+SGT+SGE+SLT+SLE = 2577 (59.8%)** fall past every numeric arm to the **textually LAST**
  block, the `VARVAL_fn` + `strcmp` tail.
- **EQV+NEQV = 1070 (24.8%)** are caught by the **textually FIRST** block.
- the numeric arms in between are **~15% combined**.

⭐ **BOTH ENDS LIVE, MIDDLE COLD.** RTX-6-ICN found the textually-first arms *dead* because a caller
guard skimmed the cheap cases off. s211 predicted this rung would be *"the opposite regime, first arms
live."* Neither describes it. **The regime is a property of the specific guard/callee pair and cannot
be predicted from the previous rung in either direction — 0(g) must be re-run per rung, and its answer
is a distribution, not a binary.** This port takes both live ends and bails to C on everything else.

---

## ⛔⛔ THE TRANSFERABLE CONTENT #3 — SIX OF THIRTEEN ICON BENCHMARKS HAVE NEVER RUN THEIR WORKLOAD

This is a **new, named half of the RTX-0b-ICN blocker** and it invalidated my own first measurement.

My first 0(d) sweep read **0 calls** for `queens`, `deal`, `concord`, `rsg`, `ipxref`. Per §8's *"a
silent probe is a question, not an answer"* I checked whether the programs had run at all. **They had
not.** All five printed the identical `&features` banner — not queens output, not deal output.

**Root cause, measured:** `concord · deal · ipxref · queens · rsg · tgrlink` all carry `link options,
post`, and **neither `options.icn` nor `post.icn` exists anywhere in `corpus/`**. They die at link and
never reach their workload. `scrip --run queens.icn` ⇒ `icon: link: cannot open ./options.icn`.

⇒ **six of the thirteen Icon benchmarks are structurally incapable of profiling anything.** After
stripping the `link` line and the `Init__`/`Term__` calls and hardcoding `n`, queens runs properly
(92 solutions, 1749 lines) — and *then* honestly measures **0** `rt_jct_relop` calls at both n=6 and
n=8, because queens compares integers and the template inlines those.

⚠ **This does NOT contradict `GOAL-ICON-RTX.md`'s standing note that `options`/`post`/`shuffle` are
pre-existing compile errors — it names their CAUSE for the first time** (a missing IPL link target,
not a front-end gap), and it shows the failure is **silent at the measurement layer**: a dead
benchmark and a genuinely cold symbol produce the same `0`. ⭐ `options.icn` **does** exist in
`refs/icon-master/ipl/procs/`; `post.icn` does not. Per the goal file's *"exclude, do not investigate"*
I did not chase it — **recorded for whoever owns RTX-0b.**

⭐ **RULE: A ZERO FROM 0(d) IS NOT A RESULT UNTIL THE PROGRAM IS PROVEN TO HAVE RUN.** Cheapest check
is that the output is the program's own, not a banner. I made this mistake before catching it.

---

## ▶ WHAT THE PORT REMOVES — ANSWERING INBOX GAP #1 CONCRETELY

The exported wrapper runs a **`setjmp` on every single call** (`by_name_dispatch.c:4776-4785`). On the
dominant S/S arm the C additionally makes **two `junction_is` calls, two `VARVAL_fn` calls, one libc
`strcmp`**, and walks ~24 compares of arm dispatch. The asm fast path deletes the setjmp, all five
calls and the whole dispatch walk, replacing them with an inline byte compare.

**A deleted `setjmp` and a deleted libc call are removable at any `-O` level** — this is not `-O0`
frame ceremony, the same way RTX-6's deleted `strtoll` was not. Inbox gap #2's `-O0`-only caveat still
applies to the *magnitude*; it does not apply to the *mechanism*.

**PORT ≠ FIX preserved.** The string arm reproduces `strcmp`'s NUL-terminated, **slen-IGNORING**
semantics exactly, because that is what the C tail does. Making it slen-aware would be a behaviour
change wearing a port's clothes — the defect class the ladder names on RTX-9.

**Soundness:** the asm decides *"simple case"* or *"let C do it"*, never a hard case. Every bail is a
bare `jmp c_rt_jct_relop` with **rdi/rsi/rdx/rcx/r8 untouched**, and nothing is written before the
final `ret`, so a bail can never leave partial state. Junctions (first byte `0x03`), csets
(`slen == 0xFFFFFFFF`), NULL `.s`, non-`DT_S` operands on the string arm, and every op outside the two
live families all bail.

---

## ⚠ SCOPE — DO NOT LET THE NUMBER TRAVEL WITHOUT THIS

1. **1.761× is an ISOLATION benchmark** (`corpus/benchmarks/icon/rtx/bench_icnrel_isolate.icn`),
   allocation hoisted out of the timed loop per s211's bimodality lesson. It is a string-comparison
   workload by construction.
2. **`RT_OPT=-O0`.** Never quote the number without the clause.
3. ⛔ **THE CORPUS REACH IS SMALL: 4,308 calls across all 303 programs.** The 163 static sites are
   **the sixth falsification of static ranking on this ladder.** The speed is real and measured on a
   legal window; **the corpus-wide impact is not, and no claim is made about it.** A program that does
   not compare strings gets nothing from this rung.
4. **`rt_binop_overload` was NOT ported** — see below.

---

## ⛔ THE RUNG AS MINTED IS HALF-ILLEGAL — LON'S CALL

RTX-6b-ICN's text pairs `rt_jct_relop` (163) with **`rt_binop_overload` (141)**. But `RTX-CLAIMS.md`
is *"the single source of truth for who owns which runtime symbol"*, and its contested table allocates
`rt_binop_overload` to **SN4-RTX at 1.4×** (197 SNO vs 141 ICON — past the 1.3× tie bar). Its state is
`FREE`, i.e. unclaimed, but **the allocation rule gives it to the other ladder**, exactly as it gives
`rt_call_arr`/`rt_num_arith`/`rt_subscript_var`.

**I ported only `rt_jct_relop`**, which is an **Icon-EXCLUSIVE** row (zero SNOBOL4, zero Prolog call
sites) and needed no arbitration. Taking the other half would have been a silent cross-ladder grab.

⇒ **Either re-assign `rt_binop_overload` to ICON-RTX, or re-mint RTX-6b's remainder around
`rt_relop_overload` (51, COERCE, Icon-EXCLUSIVE, FREE)** — which is the legal same-family companion
and is what I would pick absent a ruling.

---

## ⚠ THINGS I WOULD NOT WANT INHERITED SILENTLY

1. **PROTOCOL DEVIATION, SAME AS s211.** The check-out (`427b3ab4`) was **committed before** the port
   but **not pushed** before it — no credential was available at that point. The ordering is honest in
   history; **the protective property was not obtained.**
2. **THE SNOBOL4 WATERMARK'S ABSOLUTE NUMBER DISAGREES WITH THE HANDOFF PROSE AGAIN.** s211 records
   m4 276/50/8; I measure **284/42** at HEAD, gate ON *and* OFF *and* on the pristine build. This is
   the condition `RTX-CLAIMS.md` already names (*"the shared watermark is FALSE AT HEAD"*), so I
   graded on the **ON/OFF differential**, which is identical, and assert **no culprit**.
3. **`scripts/util_rtx_claims.sh` STILL DOES NOT EXIST.** The ledger's own gate — the script that is
   supposed to make it un-rottable — is absent from `scripts/`. Every row remains hand-asserted,
   including the allocation I relied on above to decline `rt_binop_overload`. **The ledger caught a
   real cross-ladder conflict this session on hand-asserted data alone; that is an argument for
   writing the script, not for trusting the rows.**
4. **A `make -j4` RACE PRODUCED ONE FALSE BUILD FAILURE.** Removing the gate line for the pristine
   build failed to link against `rtx_gate_icnrel` from a `rtx_init.o` whose source no longer mentioned
   it; a second identical clean rebuild succeeded. **If a clean rebuild contradicts the source, run it
   once more before believing it.**

---

## ▶ FILES

**SCRIP:** new `src/runtime/rtx/rtx_icnrel.S` · `src/runtime/by_name_dispatch.c`
(`rt_jct_relop` → `c_rt_jct_relop`; `rt_jct_relop_impl` untouched and still `static`) ·
`src/runtime/rtx/rtx_init.c` (gate) · `Makefile` (`RT_PIC_SRCS`).
**Zero templates, zero `x86_asm.h` ⇒ no `.s` regen owed.**
**corpus:** `benchmarks/icon/rtx/bench_icnrel_isolate.icn`.
**.github:** this FINDING · `GOAL-ICON-RTX.md` cursor · `RTX-CLAIMS.md` check-in.
