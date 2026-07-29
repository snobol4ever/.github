# FINDING — ICN-RTX-6 ICNNUM LANDED AT 1.783×, AND STEP 0(g) HAS A SECOND HALF: THE CALLER TEMPLATE'S INLINE GUARD DECIDES WHICH CALLEE ARM IS LIVE — AND IT IS SYSTEMATICALLY THE EXPENSIVE ONE

**Session:** s211-ICN · **Ladder:** `GOAL-ICON-RTX.md` · **Rung:** RTX-6-ICN (re-targeted) + RTX-0b-ICN (first half)
**Landed:** SCRIP `eb81508d` · corpus `97499dae` · `.github` `4c952538` (check-out)
**Gates at close:** Icon **252/11/30** (re-derived fresh 3×) · SNOBOL4 **m3 280/54 · m4 276/50/8** ·
Prolog **185/0/0** — each identical gate ON and OFF. Pristine `.so` md5 `9a83beff3e8ab0586df34f83c0f660cd`.

---

## 1. ⭐⭐ THE HEADLINE — AND IT IS A METHOD FINDING, NOT A PERF FINDING

**Step 0(g) as written (s209b) says: for a symbol with internal dispatch, find which ARM the emitted
code takes. That is necessary and it is NOT SUFFICIENT, because it looks in the wrong place first.**

The arm a callee takes is decided **by the caller template's inline guard**, and the guard is written
to skim off the CHEAP cases. `bb_coerce_numeric.cpp:18-31` already inlines DT_I+DT_I and DT_R, copies
16 bytes and reaches γ **without calling anything**. The `call rt_coerce_num2_d@PLT` at line 37 sits on
the `L(0)` arm — the arm the guard REJECTS.

⇒ **the callee is left holding only the expensive cases.** Measured, two authored workloads, same symbol:

| workload | calls to `rt_coerce_num2_d` | `rt_parse_num_d` entries | live arms |
|---|---:|---:|---|
| pure-integer arithmetic | **0** | **0** | *never entered* |
| string→numeric | 60,000 | 120,000 (exactly 2×) | **STR_INT 60,000** + DT_I 60,000 |

**STR_REAL, SNUL and FAIL are all ZERO.** So `rt_parse_num_d`'s two textually-first arms — `DT_I` at
line 272 and `DT_R` at 273, the ones any "port the fast path" instinct reaches for, and the ones both
the C source's reading order and s210's handoff point at — **are unreachable from Icon.**

⛔ **A port of those arms would have measured ~0. That is RTX-1-ICN's exact error, one rung over, and
reading the callee alone would not have caught it.** RTX-1-ICN ported two arms its caller never enters;
RTX-1b then found the live arm and got +12%. This session would have repeated the first half of that
sequence if it had started from the C file instead of the template.

⭐ **THE RULE, proposed for `ARCH-ICON-RTX.md` §8 as 0(g) second half:** *before choosing an arm, read
the EMITTING TEMPLATE and grep it for an inline `cmp`/`je` over the descriptor tag. If the template
guards the call, port the arm the guard REJECTS, not the arm the callee tests first.* Cost: one grep.

---

## 2. WHAT THE PORT ACTUALLY DOES, AND WHY IT IS NOT `-O0` CEREMONY REMOVAL

s210's inbox gap #1 warned that the portable fraction may be the small half — for `rt_coerce_num2_d`
specifically, that **the wrapper is 10 lines and the elephant `rt_parse_num_d` is 2× hotter inside it.**
That framing is correct and it is why the naive rung was wrong. The resolution is not to port the
wrapper and not to expose the static:

**ABSORB the static callee into the exported wrapper's asm body.** The live arm's real cost is a libc
`strtoll` call (locale-aware, base-detecting, overflow-modelling) plus two `-O0` frames plus three
out-parameter memory round-trips — `*iv`/`*rv`/`*isreal` are written through pointers into the caller's
stack slots and immediately reloaded. The asm replaces `strtoll` with an inline decimal scan and keeps
everything in registers. **A libc call is deleted; this is a mechanism, not ceremony.**

⭐ **AND IT SIDESTEPS THE CONTRACT QUESTION s210 RAISED.** `rt_parse_num_d` is `static` — no `@PLT`, no
exported symbol — so the kill-switch idiom (`RTX_GATE`, C body → `c_*`) "does not apply unchanged" and
s210 correctly refused to improvise. **Absorption needs no contract change at all:** the gate lives on
the exported wrapper, which already has one, and the static stays static and stays in C for the
fallback path. **No `ARCH-ICON-RTX.md` §4 amendment is owed.**

### Soundness — the one property the file rests on

**The asm decides "this is definitely a simple decimal integer" or it defers. It never decides a hard
case.** Every bail is a bare `jmp c_rt_coerce_num2_d` with `rdi/rsi/rdx/rcx` untouched, and nothing is
stored through `rdx` until the final two instructions, so a bail can never leave a half-written result.
⭐ **Scratch is therefore stashed in `xmm1`/`xmm2`, NOT on the stack** — precisely so that "a bail is a
bare `jmp` valid at any point" holds unconditionally rather than depending on stack discipline.

Deliberate deferrals, each matching a real C behaviour the asm does not model: tabs/newlines around the
digits (C's loop skips only `' '`, `strtoll` skips `isspace`) · >18 digits (C inherits `strtoll`
saturation) · no digits / `inf` / `nan` / hex float (C's `strtod` arm may still accept) · trailing junk ·
any tag but I/R/SNUL/S (the `core_runtime_error` path stays entirely in C).

---

## 3. MEASUREMENT — 3-ARM, AND THE FIRST BENCHMARK WAS UNGRADEABLE

Expected band was **stated before running**, per the harness caveat: 1.05–1.25×, on the reasoning that
the loop also allocates and GCs. **The prediction was wrong in the useful direction and the reason is
itself the finding of §4.**

| arm | median | raw samples |
|---|---:|---|
| PRISTINE | 1535 ms | 1583 1533 1524 1540 1523 1545 1535 |
| OFF | 1580 ms | 1548 1598 1634 1506 1580 1645 1578 |
| **ON** | **861 ms** | 859 900 846 841 861 922 876 |

**ON/PRISTINE = 1.783× · ON/OFF = 1.835× · kill-switch tax OFF/PRISTINE = 0.972× · RT_OPT=`-O0`.**
Intra-arm spreads 1.039/1.092/1.096× against a **1.783× gap**; ON and PRISTINE do not overlap at all.
⭐ The PRISTINE arm's `.so` was verified **byte-identical to the session baseline md5**, so the honest
baseline is provably the untouched runtime and not a rebuild artifact.

⛔ **SCOPE, AND DO NOT LET THIS NUMBER TRAVEL WITHOUT IT: 1.783× is an ISOLATION benchmark** — the
coerced string is hoisted out of the loop so the allocator never enters the window. It measures what
the symbol's own path is worth, not what a program is worth. **On the allocation-mixed variant the
harness REFUSED TO GRADE** (intra-arm spread 1.566× > inter-arm gap 1.188×); the indicative 1.188× is
**recorded as not-a-result** and is not claimed.

### Falsification — two-sided, not silent, and self-confirming

Corrupting the live arm's result (`mov r8, rax` → `lea r8, [rax+1]`) gives gate-ON `1800150000` against
the correct `1800090000`. ⭐ **The delta is exactly 60,000 — the independently measured call count.**
Gate OFF returns the correct value. So the asm provably executes, the gate provably switches, and the
probe is a *result* break rather than a route break (s187).

---

## 4. ⭐ THE SECONDARY FINDING: THE ALLOCATOR WAS THE BIMODALITY, NOT THE BOX

The first benchmark's arms were bimodal (PRISTINE 1180 1684 1153 1672 1301) and the s209 arm-stability
precondition correctly refused it. **More rounds cannot fix this** — the bimodality is multiplicative,
so the spread does not shrink with N. **Hoisting the per-iteration `string(i)` allocation out of the
loop fixed it outright**, taking spreads from 1.57× to 1.04×.

⇒ **When an RTX benchmark comes back ungradeable, suspect the allocator in the window before suspecting
the box.** s209 attributed a 25% intra-arm spread to "run-to-run noise on this box"; at least one
instance of that class has a cause and a fix. Both programs are committed (`corpus` `97499dae`) — the
ungradeable one deliberately, as a worked example.

---

## 5. RTX-0b-ICN — FIRST HALF DISCHARGED, AND THE FIX WAS NOT A BIGGER N

RTX-0b has blocked every ICON-RTX speed claim since s203 (RTX-1-ICN landed as an explicit HALF-RUNG
with its ratio suppressed). **The fix is `&time`, not scale:** a self-timed window measured inside the
Icon program excludes the compile phase *by construction*, so the ~20:1 confound s210 had to cancel
arithmetically never enters. It is also exactly the `ms: <n>` contract `bench_rtx_3arm.sh` requires.

⚠ **RTX-0b IS NOT CLOSED.** Its second half stands: `scrip --run p.icn -n8` ⇒ `cannot open '-n8'`,
**mode 3 still does not forward argv**, so N is edited into the source. That remains open.

---

## 6. FOR LON — THIS IS A FIFTH FALSIFICATION OF STATIC RANKING, AND A NEW KIND

Your open item #1 proposes allocating ownership on dynamic counts. **This session adds a case the
dynamic count also would not have caught:** `rt_coerce_num2_d`'s 209 static sites are real AND its
240k dynamic count (s210) is real, **yet its two textually-first arms are unreachable from Icon.**
Static counts cannot see arm liveness even when the dynamic count is correct.
⇒ **Recommend: dynamic-count allocation as you proposed, PLUS arm-liveness as a rung PRECONDITION
rather than a rung step.** Ownership and priority are different questions and only the first is
answered by counting.

⛔ **STILL OPEN AND UNTOUCHED BY THIS SESSION:** RTX-0-RULING(a) symbol ownership · RTX-0-RULING(b) the
SCAN family's destination (still blocks RTX-2-ICN, since `rt_substr` is in that family) ·
`rt_subscript_var` (Icon's #1 exported run-phase symbol at 315k, checked out to SN4-RTX). I opened none
of them.

⚠ **PROTOCOL DEVIATION, STATED PLAINLY:** `RTX-CLAIMS.md` requires the check-out to be **pushed before
the work**. No credential was available this session, so the claim was committed ahead of the port
(`4c952538` precedes `eb81508d`) but **not pushed ahead of it**. The ordering is honest in the history;
the protective property — another session seeing the claim before spending its own — was not obtained.
Per the s202 rule a rung is `[x]` only when its commits are ancestors of `origin/main`, which is not
yet checkable, so the ladder rows are left accordingly and `scripts/handoff_status.sh` remains the only
sanctioned completion claim.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
