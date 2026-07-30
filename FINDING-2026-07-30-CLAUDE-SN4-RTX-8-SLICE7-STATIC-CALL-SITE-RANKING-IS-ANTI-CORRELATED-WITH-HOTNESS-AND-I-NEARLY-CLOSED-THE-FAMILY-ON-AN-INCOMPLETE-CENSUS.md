# FINDING — s221 (2026-07-30, Claude): RTX-8 SLICE 7 LANDED, AND THE LADDER'S OWN NEXT-RUNG LIST WAS AIMED AT THREE DYNAMICALLY DEAD SYMBOLS

**SCRIP `294a0464`.** `RT_OPT=-O0`. `.so` `ae2e0bca1e92efcd`. Session-start `.so` reproduced s220's artifact of record `f07ae4a413fe` EXACTLY, so every claim below was derived on the bytes s220 recorded.

---

## 1. THE HEADLINE IS A METHOD RESULT, NOT A PORT

`rt_dcap_end_ok_close` is 4 instructions and will never be interesting by itself. **What matters is that it was not on the list, and the list was wrong in a way that is now measurable.**

Candidates were taken from a DYNAMIC census of the graded window. The corpus-wide STATIC ranking over the 48 `benchmarks/snobol4/*.s` + `programs/snobol4/demo/*.s` artifacts disagrees with measurement on EVERY row:

| symbol | static sites | dynamic on `pattern_bt_deep` |
|---|---|---|
| `rt_call_arr` | 586 | **6** |
| `rt_defer_step` | 432 | **0** |
| `dtp_fn_of` | 200 | **0** |
| `rt_subscript_var` | 195 | **0** |
| `rt_dcap_end_ok_close` | **1** | **8,000,001** |

⭐⭐ **ON THIS WORKLOAD STATIC CALL-SITE COUNT IS ANTI-CORRELATED WITH HOTNESS, AND THE REASON IS STRUCTURAL:** a hot symbol sits in a LOOP BODY, so the emitter needs exactly ONE call site for millions of entries; a cold setup symbol is emitted at many sites and entered once each. ARCH §5 caveat (a) says a static count measures the CALL BOUNDARY, a property of program TEXT — this is that caveat with a sign attached. **A ranked static sweep is not a weak proxy for hotness here; it is an inverted one.**

⛔ `rt_defer_step` measured **0 on BOTH** `pattern_bt_deep` AND `json.sno` despite 432 static sites. That is the s213 vacuous-batch mistake set up perfectly, and it was avoided by running the 0(d) prefilter rather than by luck. **The defer family is emitted-but-unreached in normal programs** — consistent with the ladder's own note that the latch fix must gate on `140`/`141`, never on json.

⚠ **MY OWN STATIC REGEX WAS SILENTLY WRONG AND THE TOOL CAUGHT IT:** `[A-Za-z0-9_]*` cannot match the literal UTF-8 Greek in `rt_proc_call_epilogue_γ`/`_ω`, so my ranking TRUNCATED the name — the exact RTX-4 step-0b failure. `util_rtx_count_syms.sh` FAILED LOUDLY on the truncation, as designed. The loud-failure design paid for itself.

## 2. I NEARLY CLOSED THE MATCH FAMILY ON AN INCOMPLETE CENSUS

My first census read **"only `rt_match_enter` is hot (8,000,001); everything else 0/6/10"** and I was one step from writing "the MATCH family is exhausted; further speed must come from the emitter." **That conclusion would have been FALSE, and it would have retired a live family.** The completion sweep over the remaining unported symbols in the graded artifact found THREE more at one call per match:

- `NV_SET_fn` **8,000,028**
- `rt_dcap_end_ok_open` **8,000,001**
- `rt_dcap_end_ok_close` **8,000,001** ⬅ this port

⇒ **RULE: A CENSUS IS NOT EVIDENCE UNTIL IT COVERS THE ARTIFACT'S WHOLE UNPORTED CALL SET.** A partial census does not read as partial — it reads as a finished answer with a clean shape ("one hot symbol, everything else cold"), which is exactly why it is dangerous. Enumerate the `.s` call targets, subtract the already-ported set, and measure the REMAINDER before quoting a family verdict.

## 3. THE TWO WORKLOADS ARE COMPLEMENTARY IN THE WORST WAY

| workload | time-gradeable? | unported symbol live? |
|---|---|---|
| `pattern_bt_deep` (8M) | **YES** — 1.6 s warm, min-of-N stable | YES (this rung) |
| `json.sno` + `twitter.json` | **NO** — allocation-bound, ±19%, 8× < 6× (s219) | YES — `rt_subscript_var` 106,909 |

⭐ **AND `rt_subscript_var` IS A PREDICTED-NULL PORT, PROVABLE FROM THE SOURCE:** every one of its arms calls `rt_agg_alloc` — it mints a `VCELL_t` on EVERY call, and `rt_agg_alloc` is ALREADY ASM. A port would be an asm wrapper around an asm allocator, saving arm dispatch against an allocation. **This also explains WHY json is allocation-bound: 106,909 subscripts × one alloc each.** Do not port it expecting time.

## 4. SLICE 5 IS NOW DEAD CODE ON THE GRADED WINDOW

`rt_patstk_lazy_init` = **0** and `rt_cap_match_begin` = **0**. Slice 6 inlined their call sites away. This CONFIRMS slice 6 did what it claimed — and it means **0(f) applied to slice 5 TODAY would reject it.** ⇒ **THE LADDER IS ACCRETING PORTS WHOSE CALL SITES THE NEXT RUNG THEN ELIMINATES.** Not a correctness problem; a bookkeeping one. Before porting a leaf, ask whether the rung above it will subsume the call site — if the plan is to collapse the caller, the leaf port is dead on arrival.

## 5. 0(c) WAS A HARD BLOCKER AND THE `.so` WOULD HAVE HIDDEN IT (s209 CLASS, REPRODUCED)

`g_dcf_top` was `static` — lowercase `b` in `out/rt_pic/pattern_match.o`, **UNREFERENCEABLE FROM A `.S` AT ALL.** In the `.so` a `static` and a visibility-hidden global print the SAME lowercase letter, so reading 0(c) off the `.so` returns "localized, use direct `[rip+sym]`" and CONCEALS that the symbol cannot be linked. Promoted to `__attribute__((visibility("hidden")))`: verified **`GLOBAL HIDDEN`, size 4, ABSENT from the dynamic table**. `dword ptr` not `qword` — size is 4, the s219b store-width class.

## 6. NO SPEED NUMBER, AND THE CEILING WAS COMPUTED BEFORE THE ASM

~8–12 cycles saved × 8,000,001 calls ≈ **20–30 ms of a ~1600 ms warm window = ~1.5–2%, BELOW the ±3% floor.** Same arithmetic that bounded RTX-7 at 0.58% and slice 4 at ≤0.5%. **The 3-arm rail was deliberately NOT run** — quoting a ratio at this ceiling would be the RTX-0b mistake a sixth time. Graded on correctness and eradication per the RTX-7/s217 precedent.

⭐ **THE GRADEABLE LEVER IS NAMED, NOT TAKEN:** four calls now remain at 8M-per-match — `rt_match_enter`, `NV_SET_fn`, `rt_dcap_end_ok_open`, `rt_dcap_end_ok_close`. Slice 6 earned 1.135× by COLLAPSING calls, not by porting leaves. Collapsing these is the same mechanism — **but it edits `bb_match_release` and fires `.s` regen ×3, so it is RTX-11 and NOT concurrency-safe.** Needs Lon's routing.

## 7. INSTRUMENT FIX — `util_rtx_count_syms.sh` HAD NO STDIN REDIRECT

Line 78 ran `scrip --run "$PROG"` with no redirect, so scrip inherited the caller's stdin. On any program that slurps stdin via plain `INPUT` — `json.sno`, whose own line 262 records that raw mode *"never signals EOF under scrip, so it spins forever"* — the measurement **HANGS instead of failing**, which reads as "the tool is slow," not "the tool is wrong." Cost a 500 s timeout. **RULES.md line 80 already mandated `< /dev/null` on scrip calls; this is the s220 gate defect INVERTED** (there stdin leaked IN and swallowed a `find` list; here its absence hung the run). Default is now `/dev/null` with `COUNTSYMS_IN` as the explicit opt-in — a blanket redirect would have DELETED a measurement the ladder depends on, since 0(d) on json genuinely needs `COUNTSYMS_IN=twitter.json`. Both arms verified.

## 8. ⚠⚠ UNEXPLAINED WORKING-TREE MODIFICATION — NOT COMMITTED, MUST BE INVESTIGATED

`scripts/test_gate_rtx_killswitch_sets.sh` appeared in `git status` with **+92/−34** that I DID NOT AUTHOR. Its added prose claims an m4 arm *"verified s221 over 6 pattern programs"* and *"~154 ms/program"* — **measurements that were never taken in this session.** mtime `01:58:25` falls INSIDE this session (start `01:23:06`), around when the gate was run; the file now contains a `--compile` arm absent from the version I read at orientation. **I cannot account for it.** It was `git restore`d to HEAD and is NOT in `294a0464`.

⛔ **WHY THIS MATTERS MORE THAN THE PORT: had it been committed, a future session would inherit "m4 arm, suite-wide, verified s221" as FACT and stop re-checking the one thing ARCH §7 step 3 has been owed since s217.** That is the (a)-class rot of the STALE-ORIENTATION rule in its most dangerous form — a false claim of DISCHARGED WORK, self-consistent and plausibly worded.

⚠ **CONSEQUENCE FOR THIS SESSION'S OWN GATE RESULT, STATED PLAINLY:** the kill-switch PASS I observed (**316 programs, N=4: IDENTICAL 315 · QUARANTINE 1 · MOVER 0**) was produced by a script whose on-disk state at that moment I cannot fully account for. **It should be RE-DERIVED by the next session against the committed instrument before it is quoted.** I am not withdrawing it and I am not relying on it.

⭐ Independently of the above, my draw quarantined **1** program (`160_pat_alt_inner_gen_resume`, `ON{5d701824,6a68d667,d7772c55}` ⊃ `OFF{6a68d667,d7772c55}`) where s220 reported **3** (`160` + `413_arith_mixed` + `W06_len`). **That is not a discrepancy to explain away — it CORROBORATES s220's own caution that N=4 DETECTS non-determinism but does not CHARACTERISE it. The quarantine membership is itself a sample artifact.** Four sessions have now reported four different memberships. `5d701824` was already recorded on both arms in prior sessions, so this is the same hash population sampled differently, not a new leak — and the gate agrees (`MOVER=0`).

---

## GATES

Watermark re-proven at session start **m3 311/4/0 · m4 311/2/2 · DIVERGE=2** (26 s), and **IDENTICAL post-port**, failure sets line-by-line equal (m3 `test_case`/`140`/`141`/`160`; m4 `test_case`/`160`; diverge `140`/`141`), **ZERO movers** · two-sided HARD `ud2` (ON ⇒ **rc=132 SIGILL**; SAME BUILD OFF ⇒ rc=0, `W=hello` correct) · revert verified THREE ways (grep 0 · src md5 · `.so` **BIT-IDENTICAL** `ae2e0bca…`) · RTX unit **ALL PASS (8426/0)** · smokes **PASS=6 FAIL=0 ROWS_DRIFT=0** · `g_dcf_top` absent from dynamic table · zero templates ⇒ no `.s` regen owed.

**NOT RUN / NOT CLAIMED:** 3-arm rail (deliberate, §6) · m4 arm of the kill-switch sweep (STILL absent from the committed script — §8) · beauty (m3-blocked at EMIT, gate-invariant) · 15-demo board · Prolog/Icon/Snocone/Raku · `util_rtx_count_syms.sh` segfault on `rt_dcap_lazy_init` (inherited, untouched).

`handoff_status.sh` is the push truth — not this block.
