# FINDING-2026-07-29-CLAUDE-ICN-RTX-1-ASSIGN-VAR-LANDED-AND-THE-GC-SAFEPOINT-IS-THE-PORTABLE-FRACTION

**Session:** s209-ICN · **Rung:** RTX-1-ICN (re-targeted per the s203 0(d) re-order) · **Landed:** asm
port of `rt_assign_var` behind new family gate `SCRIP_RTX_ICNVAR`. **⛔ NO SPEED CLAIM — see §4, and
§7, which falsifies this rung's own design premise and names the arm that should have been ported.**

---

## 1. WHAT LANDED

`src/runtime/rtx/rtx_icnvar.S` — new family `ICNVAR`, gate default ON, C body renamed
`c_rt_assign_var` in the same commit (`src/runtime/pattern_match.c:1196`).

**Ported: the two fast arms only.** Frame-slot store (`var.slen==1` ⇒ `*(DESCR_t*)var.ptr = val`) and
named global (`var.slen==0` ⇒ `NV_SET_fn`). **NAMETRAP/VCELL, table stores and the tvsubs string-splice
arm stay in C** — that arm allocates, memcpy's three times and recurses; porting it is volume, not speed.

**⭐ THE PORTABLE FRACTION IS THE GC SAFEPOINT, AND IT IS NOT `-O0` CEREMONY.** The C opens **every**
call with an unconditional safepoint: build a 2-slot `DESCR_t` shadow array, `lea` it, `call
rt_gc_point_arr@PLT`, reload `var`/`val` back out. That callee's entire body is
`int pv = g_gc_pending; if (!pv) return;`. So the common path spends ~6 memory ops and a PLT call to
read one `int`. The port tests `g_gc_pending` inline and reaches C only when a collect is genuinely
pending — **which is also exactly when the shadow array matters**, because a real collect may relocate
`var` and `val`. The fast path is therefore only ever taken in the window where the array is provably
dead. ⚠ This is the fraction s208 told ICON-RTX was UNMEASURED for `rt_call_arr`; for `rt_assign_var`
it is now *identified*, though still not *timed*.

**Not inlined, deliberately:** `rt_sxt_break`. `g_sxt_owner` is not a symbol — it is
`#define g_sxt_owner (g_sxt_fr.owner)`, so inlining hardcodes a struct offset that no `_Static_assert`
guards. The C already guards the call on `DT_S`. Kept as a call.

**Safe fallthrough, and why partial work then re-entering C is not a bug:** every cold exit re-runs the
two leading hooks inside `c_rt_assign_var`. Both are idempotent at that point — `rt_gc_point_arr` sees
`g_gc_pending == 0` and returns, `rt_sxt_break` has already cleared the owner. Order is preserved: a
pending collect jumps to C **before** the sxt break, exactly as the C sequences them.

## 2. STEP 0 — ALL SIX CHECKS, AND 0(c) PAID FOR ITSELF AGAIN

(a) live def `pattern_match.c:1196` ✅ · (b) spelling round-trips ✅ · (c) ⭐ **`g_gc_pending` is `B` in
`nm -D` — EXPORTED, therefore PREEMPTIBLE, therefore `@GOTPCREL` and never a direct `[rip+sym]`.**
Verified in the object: `R_X86_64_REX_GOTPCRELX`, not `R_X86_64_PC32`. **This is the third time this
rule has been the first thing to bite on this ladder** (it broke the s203 interposer's first link). ·
(d) DONE at s203: **15,871 calls at queens N=8, scales 14.2×, dynamic #1 unported** · (e) grep
`--include=*.S` clean, not already asm ✅ · (f) **147 `call rt_assign_var@PLT` sites across 8 of the 265
live artifacts — reproduces the ledger exactly**, so that row is not rotted ✅

## 3. GATES — ALL THREE LANGUAGES, EACH AGAINST ITS OWN GATE-OFF CONTROL

| battery | gate ON | gate OFF (control) |
|---|---|---|
| Icon `test_icon_all_rungs.sh` | **252 / 11 / 30** | 252 / 11 / 30 |
| SNOBOL4 `broad_corpus` M4 | **276 / 50** | 276 / 50 |
| Prolog `test_prolog_bb_honest.sh` | **185 / 0 / 0** | 185 / 0 / 0 |

Icon watermark re-derived **fresh before any edit** and matched the quoted 252/11/30 — the baseline is
not stale this time.

**⭐ TWO-SIDED FALSIFICATION, AND IT WAS NOT SILENT.** Per s187 a gate-off pass is *vacuous* evidence
(its output equals the C output by construction), so a RESULT was broken, not a route: fast-path B made
to store a `DT_FAIL` tag. **Gate ON ⇒ 247 / 16 — five tests flipped. Gate OFF ⇒ 252 / 11 unchanged.**
The asm demonstrably executes and the switch demonstrably switches.

⚠ **BUT FIVE IS A SMALL SIGNAL FOR A SYMBOL WITH 15,871 CALLS, AND THAT IS A COVERAGE STATEMENT.** The
15,871 came from `queens`, a **benchmark**; the rung battery is a different corpus and evidently drives
the frame-slot arm only lightly. Per s204 this is recorded as a known gap, not smoothed over: **the
battery is a correctness gate here, not a coverage gate.**

## 4. ⛔ NO SPEED CLAIM — THE WINDOW IS BOGUS AND THE RATIO IS SUPPRESSED

Interleaved A/B, first round discarded, `queens` at its default N: the whole run is **16–20 ms**.
The ladder's own floor is **`MIN_MS=800`**, and its own rule is that a shorter window is reported
`BOGUS-WINDOW` **with the ratio SUPPRESSED, not printed small**. So it is suppressed. The nominal
numbers were not even directionally favourable, which at a 16 ms window is noise about process startup
and says nothing either way.

⇒ **RTX-0b-ICN (the famset instrument) is confirmed as the blocking prerequisite it was declared to be
at s203** — not for ranking the board this time, but because *the ladder currently cannot time its own
landed work.* A correct, proven-executing, no-regression port whose benefit is unmeasurable is a
**half-rung**, and it should be recorded as one.

## 5. ⛔⛔ TWO DEFECTS IN THE HQ RECORD, BOTH FOUND WHILE FOLLOWING IT

**(1) `scripts/util_rtx_claims.sh` DOES NOT EXIST — AND A FINDING CLAIMS IT RAN GREEN.**
`GOAL-ICON-RTX.md:12`, `GOAL-SNOBOL4-RTX.md:64`, `RTX-CLAIMS.md:86` and `RTX-CLAIMS.md` §THE GATE all
mandate it at session start and close. `FINDING-2026-07-29-…-RTX-0D-…` states it ran at **"fatal 0 ·
warnings 0 · GREEN"** and describes escalating a silent double-claim probe against it. Measured:
`find` finds nothing, `grep -rn` across the SCRIP tree finds nothing, and **`git log --all --
scripts/util_rtx_claims.sh` is empty — it has never existed in any branch at any commit.**
⇒ **The ledger's anti-rot mechanism is itself the rotted thing.** This is precisely the failure mode
that file's own §THE GATE enumerates ("a pointer naming a deleted section"), one level up. ⛔ Until the
script is written, **every `OUT:` row in `RTX-CLAIMS.md` is hand-maintained and unverified**, including
the DOUBLE-CLAIM assertion that two concurrent ladders depend on. **This session's claim check was done
by hand.**

**(2) `rt_call_arr` OWNERSHIP IS CONTRADICTORY IN THE RECORD.** `RTX-CLAIMS.md` and
`GOAL-ICON-RTX.md`'s s208 INBOX both say **Lon ruled option (a): it goes to ICON-RTX, SN4-RTX becomes
beneficiary**, and the row reads `OUT:ICON-RTX`. But the s203 FINDING §"WHAT THIS SETTLES" says
**"RULING: ICON-RTX DROPS ITS CLAIM. `rt_call_arr` stays with SN4-RTX"** on the measured grounds that at
1,822 calls it is 8.7× *colder* than `rt_assign_var` and not Icon's best target. **Both are on the board
simultaneously.** The net state is that ICON-RTX is recorded as owning a symbol it deliberately
declined for a stated reason that Lon's ruling does not address. ⛔ **Not self-resolvable — it needs
Lon.** It did not block this rung (`rt_assign_var` is separately owned and separately measured), but it
will block the next one that touches the call path.

## 6. NEXT

1. **RTX-0b-ICN** — now blocking twice over: it owes the board a scanning program, an I/O program and a
   call-heavy program, **and it owes this rung its ratio.**
2. **Write `util_rtx_claims.sh`** or delete the six references. Do not leave a mandated gate that no one
   can run.
3. **Lon: the `rt_call_arr` contradiction** (§5.2), and RTX-0-RULING(b), the SCAN-family destination,
   still open from s203.

⚠ **NEW GATE = LEDGER EVENT** (`RTX-CLAIMS.md` hard rule 3): `SCRIP_RTX_ICNVAR` is the **seventh** family
gate and is shared state across all six languages.

---

## 7. ⭐⭐ ADDENDUM s209b — THE PORT'S OWN PREMISE IS FALSIFIED, AND I FALSIFIED IT MYSELF

**§4 said the ladder could not time its own work. It can now — and the first legal window says the two
arms this rung ported are DEAD for Icon's emitted code.**

**(a) WHICH CONSTRUCT ACTUALLY EMITS THE SYMBOL — MEASURED, NOT ASSUMED.** Compiled five assignment
forms and counted `call rt_assign_var@PLT` in the emitted `.s`:

| Icon source | sites |
|---|---:|
| `b := a` (local) | **0** |
| `g := 2` (global) | **0** |
| `a +:= 1` (augmented) | **0** |
| `a :=: b` (swap) | **0** |
| **`L[1] := 3` (subscripted)** | **1** |

⇒ **All 147 of Icon's static sites are SUBSCRIPTED assignment.** Every other assignment form is emitted
inline by its own BB template and never reaches the runtime symbol at all.

**(b) AND SUBSCRIPTED ASSIGNMENT TAKES NEITHER PORTED ARM.** A subscript lvalue arrives as a NAMETRAP
(`slen==2`) over a `VCELL_t`, so it falls straight through `.Lav_c` into `c_rt_assign_var` and stores via
`vc->cellp`. **Proven by probe, not by reading:** fast-path B was corrupted to store a `DT_FAIL` tag and
the 4M-iteration subscript workload **still printed the correct answer**, while the rung battery still
broke to 247/16 on the same build. ⇒ **fast path B is never entered by subscripted assignment**; it and
fast path A are reached only by the runtime's own internal callers (`pattern_match.c:713/804`,
`rt_swap_var`) — which is also why the falsification only ever moved five battery tests.

**(c) THE FIRST LEGAL A/B ON THIS LADDER.** Workload: 100-element list, 4M subscripted stores — i.e. the
symbol's **maximum possible exposure**. Interleaved, first round discarded, 6 rounds, medians:

| | median | range |
|---|---:|---|
| `SCRIP_RTX_ICNVAR=on` | **2587 ms** | 2566–2804 |
| `off` | **2651 ms** | 2566–2789 |

Window ≫ `MIN_MS=800` ⇒ **legal, not BOGUS**. Output md5 identical both arms.
Median ratio **1.0247 (+2.47%)** — ⛔ **but the two distributions overlap heavily and the MINIMA are
IDENTICAL (2566 both), which is the cleanest estimator here. This is reported as ≤2.5% and WITHIN NOISE,
not as a speedup.** A 240 ms sub-scale run of the same program gave −0.41%. **No speed claim survives.**

**(d) WHAT THIS MEANS FOR THE LADDER, AND IT IS BIGGER THAN ONE RUNG.** On a workload that is *100%* the
ported symbol, the measured effect is ~0. That is not a failure of the port — the port is correct, gated,
and provably executing — it is **evidence that porting a C body's fast arms to asm is worth ~nothing when
the emitted code does not take those arms.** The `-O0` frame ceremony that `-O0` RTX ports are supposed
to win is, here, entirely inside a callee the real caller reaches anyway.

⭐ **THE ACTIONABLE TARGET IS NOW NAMED AND MEASURED: the NAMETRAP → `vc->cellp` store.** That is the arm
Icon's 147 sites actually take, it is currently C, and §1 explicitly and wrongly excluded it as "cold".
**It is the opposite of cold — it is the only live arm.** Next rung ports it.

⚠ **THE GENERAL LESSON, AND IT IS THE SAME ONE THIS LADDER KEEPS PAYING FOR:** step 0(d) proved the
*symbol* was hot (15,871 calls, scales 14.2×) and that was TRUE. It said nothing about **which arm inside
the symbol** was hot, and the port was designed against an assumption about that. ⇒ **STEP 0(g) PROPOSED:
for any symbol with internal dispatch, identify which ARM the emitted code takes before choosing what to
port.** The check is one compile and one grep, exactly like 0(f).

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
