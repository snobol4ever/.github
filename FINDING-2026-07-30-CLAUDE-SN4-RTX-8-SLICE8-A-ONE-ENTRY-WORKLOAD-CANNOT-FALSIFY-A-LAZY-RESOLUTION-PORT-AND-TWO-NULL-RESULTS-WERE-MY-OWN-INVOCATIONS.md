# FINDING — s223 (2026-07-30) — SN4-RTX-8 SLICE 8

**RTX-8 SLICE 8 LANDED (`rt_dcap_end_ok_open`, the DCAP ctx PUSH — the other half of slice 7's pop). THE RESULT THAT
OUTRANKS THE PORT: MY FALSIFICATION PROBE CAME BACK CLEAN AND CORRECT WITH THE GATE ON, WHICH READS AS "THE ASM NEVER
EXECUTES" AND WOULD HAVE REVERTED A CORRECT PORT. THE WORKLOAD HAD EXACTLY ONE ENTRY, AND FOR A LAZY-RESOLUTION PORT
`entries - 1 = commits` MEANS A ONE-ENTRY WORKLOAD HAS ZERO COMMITS AND IS STRUCTURALLY INCAPABLE OF FALSIFYING
ANYTHING. TWICE MORE IN THE SAME SESSION A NULL RESULT TURNED OUT TO BE MY OWN INVOCATION, NOT THE TREE.**

Session: s223. Base HEAD at session start: SCRIP `a08bfe56`. RT_OPT=`-O0` throughout.
`handoff_status.sh` is the push truth — NOT this document. No commit hash is written here for the landing commit,
because a hash recorded before the push that rebases it is the s218/s222 class of rot (see RULES (a) sibling below).

---

## 1. WHAT LANDED

`rt_dcap_end_ok_open` (`src/runtime/pattern_match.c:696`) in `src/runtime/rtx/rtx_match.S`, gate `SCRIP_RTX_MATCH`,
C body renamed `c_rt_dcap_end_ok_open` in the same commit. ~20 instructions; the hot arm pushes one `rt_dcf_t` frame
and **tail-jumps the untouched C pump**. Zero templates touched. `.so` = `9a4cf9c2e7a3e8d2`.

**BOX CONTRACT** (`bb_match_release`): `rdi`=MARK, `rsi`=TOP, `rdx`=SUBJECT base by value; returns `long` in `rax`
(nonzero ⇒ a `*VAR` transfer is pending and the box drives `rt_dcap_step`).

**THREE `static`→`visibility("hidden")` PROMOTIONS** in the same commit: `g_dcf`, `g_dcf_cap`, `rt_dcap_pump`.

---

## 2. ⭐⭐ THE HEADLINE: A ONE-ENTRY WORKLOAD CANNOT FALSIFY A LAZY-RESOLUTION PORT

I planted a hard `ud2` immediately after `.Ldeoo_mutate` (the first instruction of the hot arm) and ran a program
built directly from the SPITBOL manual's own nested-capture example — `((‘B’|‘F’|‘N’).FIRST ‘EA’ (‘R’|‘T’).LAST).WORD`
against `'XXNEATXX'`. Result: **gate ON → rc=0, output `N T NEAT`, exactly correct.** Gate OFF, identical. A `ud2` in
the hot path and the program ran to completion twice.

Read literally that says *the asm is dead code and the port is vacuous* — the s213 wasted-batch diagnosis. **It is the
wrong diagnosis, and taking it would have reverted a correct port and sent the next session hunting a defect that does
not exist.**

**ROOT CAUSE.** `g_dcap_trace` is initialised to `-1` (unresolved). `-1` is NONZERO, so ARM A routes the call to C,
where the cached `getenv` resolves and the ARM B lazy carve also retires. ⇒ **THE FIRST CALL OF EVERY PROCESS ALWAYS
DELEGATES TO C, BY DESIGN.** The manual's example performs exactly ONE capture-match ⇒ exactly ONE entry ⇒ that entry
is consumed by the lazy-resolution arm ⇒ **ZERO commits ⇒ nothing for the probe to fire on.**

Re-run at 5 iterations of `pattern_bt_deep`: **gate ON → rc=132 SIGILL · SAME BUILD gate OFF → rc=0, correct output.**
Two-sided falsification proven.

⭐⭐ **RULE, AND IT GENERALISES BEYOND THIS FAMILY: A FALSIFICATION PROBE MUST RUN ON A WORKLOAD WITH ≥2 ENTRIES
WHENEVER THE PORT HAS A LAZY-RESOLUTION OR ONE-SHOT-INIT ARM.** Read the arm census for `entries − 1 = commits` (the
slice-5 shape, and slice 8 is the second instance) and size the probe workload from the COMMIT count, never the ENTRY
count. This INVERTS the s217 vacuous-probe class: s217's probe passed every check and proved nothing; this one FAILED
to fire and would have condemned working code. **Both failure directions come from the same omission — not asking how
many times the arm under test actually runs.**

⚠ **CONSEQUENCE FOR THE KILL-SWITCH GATE, STATED SO IT IS NOT OVER-READ:** any program in the 316 that performs
exactly one capture-match exercises only the C path for this slice and contributes ZERO evidence about the asm. The
suite-wide `IDENTICAL=315` below is therefore a correct no-regression result and NOT a claim that 315 programs
exercised slice 8. Nobody has enumerated how many of the 316 have ≥2 capture-matches; **do not quote one.**

---

## 3. ⭐⭐ TWO MORE NULL RESULTS, BOTH MY OWN INVOCATION — THE 0(d) FALSE-NULL CLASS, APPLIED TO MYSELF

**(a) `.s` REGEN — I REPORTED "DIFFERS" AND IT WAS FALSE.** I hand-rolled `scrip --compile f.sno -o out.s` and
`cmp`'d against the committed artifacts: 3 of 3 DIFFERED. The real cause was that `--compile` writes to **stdout**;
`-o` produced no file at all, so `cmp` was comparing against a nonexistent path. The canonical form is
`scrip --compile f.sno > out.s` (`util_regen_benchmark_s_artifacts.sh:30`).
**CORRECTED, AND THEN SETTLED WITH THE TREE'S OWN INSTRUMENT RATHER THAN MY `cmp`: all three regen scripts report
`No changes — already current` (0 changed).** ⇒ **NO `.s` REGEN IS OWED, AND THE PHASE-1 "ZERO TEMPLATES ⇒ NO REGEN
BY CONSTRUCTION" CLAIM IS NOW *VERIFIED AT THIS HEAD* INSTEAD OF INHERITED.**

**(b) FIVE `EMIT-FAIL`s THAT ARE AN INSTRUMENT GAP, NOT A DEFECT.** `util_regen_feature_s_artifacts.sh` reported
EMIT-FAIL (empty/crash) on `coverage_sno_nodes`, `test_case`, `test_math`, `test_stack`, `test_string`. Gate-OFF
discrimination first (gate OFF *is* the C fallback): all five emit **0 bytes at gate ON and gate OFF alike ⇒ not
caused by the asm.** Then the real cause: **the crosscheck sets `SNO_LIB` (`test_crosscheck_snobol4.sh:25`) and the
feature-regen script does not.** With `SNO_LIB` set, `test_math` emits **271,435 bytes** and `test_stack` **344,256**.
⇒ pre-existing, unrelated to this rung, and it means **those five committed `.s` artifacts are never refreshed by the
script that exists to refresh them.** Written up as its own rung (§7) — deliberately NOT fixed here, see §7 for why.

⭐ **THE COMMON RULE FOR (a) AND (b), AND IT IS THE SAME ONE THE LADDER LEARNED AT 0(d) ABOUT SYMBOLS: A NULL RESULT
FROM A HAND-ROLLED INVOCATION IS NOT EVIDENCE ABOUT THE TREE UNTIL THE INVOCATION MATCHES THE INSTRUMENT OF RECORD.**
Three times in one session (`-o`, missing `SNO_LIB`, the one-entry probe) a zero meant "I measured it wrong," and each
zero was individually plausible as a real defect. **Read the instrument's own source for the invocation; do not
reconstruct it from the flag's name.**

---

## 4. STEP 0 PROTOCOL — MEASURED, IN ORDER

**0(a)/0(b)/0(e) NAME ROUND-TRIPS:** live definition at `pattern_match.c:696`, spelling byte-identical, `--include=*.S`
present (the load-bearing flag). One template call site, `bb_match_release.cpp:33`.

**0(c) ON THE OBJECT FILE, NEVER THE `.so` — AND IT WAS AGAIN A HARD BLOCKER (s209 class, third time on this family).**
In `out/rt_pic/pattern_match.o`: `g_dcf` `b` · `g_dcf_cap` `b` · `rt_dcap_pump` `t` — **all three `static`, i.e. NOT
REFERENCEABLE FROM A `.S` AT ALL.** The `.so` lists none of them, so reading 0(c) there would have said "linker-
localized, use direct `[rip+sym]`" and concealed that the symbols cannot be linked. Post-promotion, verified from the
object: `g_dcf` `B` · `g_dcf_cap` `B` · `rt_dcap_pump` `T` · `c_rt_dcap_end_ok_open` `T`, with `rt_dcap_end_ok_open`
now `T` in `rtx_match.o` and `c_*` `U` there; **0 of the promoted symbols appear in the `.so` dynamic table** ⇒ direct
`[rip+sym]` correct, interposition-proof.

⭐⭐ **THE DIRECTION IS WHAT MAKES THIS SAFE ON THE MODE-4 AXIS, AND IT IS THE EXACT OPPOSITE OF THE `g_cap_gen`
DISASTER.** That was `default`→`hidden`, a **NARROWING**, and cost **173/316 mode-4 LINK failures while mode 3 stayed
GREEN** (`pattern_match.c:737`). `static`→`hidden` is a **WIDENING** and cannot break a link that resolves today,
because a `static` symbol is unreferenceable from outside its TU *by definition*. Verified anyway: **0 template refs,
0 emitted-`.s` refs** across the benchmark+demo artifacts. ⇒ the two directions must never be discussed as one
"visibility change"; only one of them can break m4.

**0(d) THE RELEVANCE CHECK — SCALING PROVEN AT TWO LOOP COUNTS.** `pattern_bt_deep` at 1M/2M:
`rt_dcap_end_ok_open` **1,000,001 → 2,000,001**, exactly **2.000×** with the `+1` constant preserved ⇒ **8,000,001 at
the 8M graded window, reproducing the s221 census INDEPENDENTLY.** `rt_dcap_end_ok_close` identical. `rt_match_enter`
identical. ⭐ **`rt_dcap_step` = 0** — the `*VAR` arm never fires on this workload, so the hot arm always returns the
pump's 0 here; the nonzero path is real, ungraded, and NOT reimplemented.
⚠ `rt_dcap_pump` **cannot be counted by the interposer while it is `static`** — the tool correctly refuses it as "not
an exported text symbol." That refusal is 0(c) agreeing with itself, not a tool defect.

**0(f) ARM CENSUS, READ FROM THE C *BEFORE* THE ASM (the s220 discipline that saved slice 6):**
| arm | condition | disposition | measured |
|---|---|---|---|
| A | `g_dcap_trace != 0` | → C. Unresolved (`-1`) or trace on. Swallows the process's FIRST call. | 1 |
| B | `g_dcf == NULL` | → C. The lazy carve. **Delegating it is what keeps `rt_cas_carve` `static`** — the 4th promotion this port would otherwise have needed. | 1 (same call) |
| C | `g_dcf_top >= g_dcf_cap` | → C, which aborts loudly. | 0 |
| D | HOT | push frame + tail-jump pump. | 1,000,000 of 1,000,001 |

**BAIL-BEFORE-MUTATE IS FREE, AND THAT IS A CLAIM ABOUT INSTRUCTION ORDER.** All four bail tests sit ABOVE
`.Ldeoo_mutate` and nothing above that label writes memory. This matters concretely: a delegation AFTER the
`g_dcf_top` bump would push TWO frames for one match and the outer pop would leave a stale frame owning a dead
`[mark,top)` — the s215 hazard that made slice 6 delicate. This is the s219 PREFERRED test-and-return shape instead.

---

## 5. WHAT THE MANUAL REQUIRED, AND WHY THE PUMP STAYED IN C

SPITBOL manual **Ch.6 p.62–63** (read this rung, per the standing directive):
1. Conditional assignment "assigns the matching subject substring to a variable ... assignment occurs only if the
   pattern match is successful" ⇒ this function IS the on-success flush and must be reached on no other path.
2. "Conditional assignment may appear at any level of pattern nesting, and **may include other conditional
   assignments within its embrace**", with `((..).FIRST 'EA' (..).LAST).WORD` flushing **THREE** captures from ONE
   match. ⇒ **nesting is BY DESIGN**, which is what dictates a per-match frame with a FIXED `[mark,top)` walk range so
   a nested match's entries (pushed above our top) are swept by its own open/close and never by ours.
3. p.63 ordering: conditional assignments are performed first, **THEN** the replacement field is evaluated — the
   box's sequencing, not ours.

⇒ **THE PORT REIMPLEMENTS THE FRAME PUSH ONLY.** Ordering, nesting and multi-entry walk semantics are structurally
unchanged because the pump is untouched C. Verified behaviourally: the manual's own example yields `FIRST=N`,
`LAST=T`, `WORD=NEAT` identically at gate ON and gate OFF.

⭐ Layout is **`_Static_assert`-anchored in the C** (the s204 `HB_AGGV` precedent): stride 40 plus all four field
offsets plus `sizeof(DESCR_t)==16`. A future field added to `rt_dcf_t` breaks the BUILD rather than silently writing
the pump's frame at wrong offsets. `dword ptr` for `g_dcf_top`/`g_dcf_cap` (both `int`) — the s219b store-width class.

⚠ **`g_dcap_trace` IS A HOIST, NOT A NEW FLAG, AND THE ALTERNATIVE WAS A SILENT REGRESSION.** The cached-`getenv`
`static int _dct` lived INSIDE the C function where no `.S` can reach it. Dropping the test would have silently killed
`SCRIP_DCAP_TRACE` for every gate-ON run — a debugging facility vanishing with no diagnostic. The `-1` sentinel is
load-bearing: nonzero ⇒ ARM A routes call 1 to C, which resolves the cache AND performs the carve, so both cold arms
retire on one delegation. It is also the direct cause of §2.

---

## 6. GATES — ALL GREEN, AND THE WATERMARK SAID OUT LOUD

**WATERMARK RE-PROVEN AT SESSION START, BEFORE TOUCHING ANYTHING (23 s): m3 `311/4/0` · m4 `311/2/2` · DIVERGE=`2`.**
m3 fails {`test_case`,`140`,`141`,`160`} · m4 fails {`test_case`,`160`} · DIVERGE {`140`,`141`} ⇒ **LATCH CANARY
INTACT.** Post-port: **line-by-line IDENTICAL** — the watermark did not move.

- ⭐⭐ **KILL-SWITCH HASH-SET GATE, `MODE=both`, 316 programs, N=4, 78 s: m3 IDENTICAL=315 · QUARANTINE=1 · MOVER=0
  ‖ m4 IDENTICAL=312 · QUARANTINE=1 · MOVER=**0** · SKIP=3 ⇒ GATE PASS.** Reproduces s222's numbers exactly. This is
  the first rung to land *with* the m4 arm existing, so "suite-wide both modes" is discharged for the landing itself
  rather than owed. ⚠ See §2's caveat on how much of that 315 is slice-8 evidence.
- **TWO-SIDED FALSIFICATION** proven (§2), reverted **THREE WAYS**: `grep ud2`==0 · source md5 identical to pristine ·
  `.so` relinked **BIT-IDENTICAL** to `9a4cf9c2e7a3e8d2`.
- **RTX unit: ALL PASS. Store-width gate: PASS** (12 GOT-tainted stores checked against ELF symbol sizes — the gate
  that exists for exactly the `dword ptr` decision above). **Smokes 7/7 × 2.**
- **`.s` regen: NOT OWED, verified** (§3a).

**ARCH §7 STEP 2b — WHICH OTHER BATTERIES ARE EVIDENCE, MEASURED RATHER THAN ASSUMED.** Icon `4/0` · Prolog `189/0` ·
Snocone `8/0`, all unchanged. AND the interposer counted **ZERO** entries to `rt_dcap_end_ok_open` from both an Icon
and a Prolog program ⇒ **those batteries are STRUCTURALLY NON-EVIDENCE for this port**; they remain valid
no-regression evidence for the C-side and visibility changes only. **Citing them as an asm gate would be a FALSE
CLAIM.** ⚠ Snocone shares the SNOBOL4 pattern path and MIGHT reach the symbol — **not measured, not claimed.**

---

## 7. ⛔ NO SPEED NUMBER, AND THE REFUSAL IS THE RESULT

**CEILING COMPUTED BEFORE THE ASM WAS WRITTEN:** ~15 `-O0` prologue/epilogue/stack instructions saved × 8,000,001
calls ≈ 20–30 ms of a ~1600 ms window ≈ **~2%, BELOW the ±3% null floor** this ladder has established three times
(RTX-7's 0.58% `rdtsc` bound · slice 4's ≤0.5% · slice 7's 1.5–2%). **The 3-arm rail was deliberately NOT run: there
is nothing gradeable to grade, and quoting a ratio off a sub-floor window is precisely how a correct port gets
reverted** — the s220 anti-evidence lesson, where a 130 ms window read **1.7× SLOWER** for a port that was in fact
1.135× faster. This is an **ERADICATION slice serving RTX-12.**

**NOT RUN / NOT CLAIMED:** beauty (m3-BLOCKED at EMIT, gate-invariant) · 15-demo board · 3-arm rail (deliberate) ·
`160` characterisation at N≫4 · Snocone symbol reach · Prolog/Icon/Raku ladders · **no second port attempted this
session — see below.**

**⭐ WHY ONLY ONE PORT, STATED AS A CHOICE NOT AN OMISSION.** Under a Lon "all your choices" grant I closed this rung
completely — probe, revert-three-ways, suite-wide both-modes gate, the `.s` question actually answered, FINDING —
rather than opening a second port and leaving two rungs half-gated. **A half-gated port is worse than no port: it
enters the tree as an unfalsified claim, which is the (a)-class rot this project fights.** RTX-11 was NOT taken: it
edits `bb_match_release` and fires `.s` regen ×3, and its non-concurrency-safety is a FACT ABOUT PARALLEL SESSIONS,
not a preference a grant can override.

**NEW RUNGS RAISED BY THIS SESSION (not taken):**
1. ⭐ **`util_regen_feature_s_artifacts.sh` DOES NOT SET `SNO_LIB`** ⇒ permanent EMIT-FAIL on 5 programs whose `.s`
   are therefore never refreshed (§3b). **DELIBERATELY NOT FIXED HERE:** fixing it mints 5 large NEW `.s` artifacts as
   a side effect of an unrelated RTX rung, and unreviewed artifact minting is the s26 F12/F13 class — artifacts that
   then LIE about the compiler's output. It deserves its own rung with its own review.
2. **RULES (a) NEEDS THE SIBLING s222 ALREADY NAMED:** never write a commit hash into a doc before the push that
   rebases it. This document complies by writing none.
3. **ENUMERATE how many of the 316 perform ≥2 capture-matches**, so the kill-switch's slice-8 coverage is a number
   instead of an unknown (§2).
