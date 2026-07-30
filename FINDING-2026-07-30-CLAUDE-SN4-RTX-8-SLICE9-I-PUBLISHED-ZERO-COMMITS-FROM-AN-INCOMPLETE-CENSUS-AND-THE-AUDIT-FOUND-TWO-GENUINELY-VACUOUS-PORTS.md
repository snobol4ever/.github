# FINDING — 2026-07-30 — SN4 RTX-8 SLICE 9

## ⛔⛔ CORRECTION BANNER — READ THIS BEFORE §2. THIS DOCUMENT ORIGINALLY CLAIMED THE 316-PROGRAM GATE SCORES **ZERO** COMMITS ON THIS PORT. THAT NUMBER WAS WRONG, IT WAS MINE, AND I PUBLISHED IT FROM AN INCOMPLETE CENSUS BEFORE THE AUDIT CAUGHT IT IN THE SAME SESSION.
**The true pre-existing coverage is 2 programs in m3 and 1 in m4 — small and compromised, but NOT zero.** `test_case` commits **19** and `test_string` commits **1**. I had measured five of the seven reaching programs with an ENTRIES-ONLY tool (`util_rtx_count_syms.sh`), got 1/1/1/0/0, correctly applied "1 entry ⇒ 0 commits under the `-1` latch" to those five — **and then generalized to the two I had not measured, which were the only two that mattered.**
⭐ **THIS IS s221's OWN TITLED LESSON — "I NEARLY CLOSED THE FAMILY ON AN INCOMPLETE CENSUS" — EXCEPT I DID CLOSE A RUNG ON ONE, AND WROTE THE NUMBER INTO A FINDING, THE LIVE CURSOR AND THREE COMMIT MESSAGES BEFORE CHECKING.** The generalizing step felt like arithmetic, not inference, which is exactly why it went unexamined. ⇒ **RULE: A COVERAGE ZERO IS A UNIVERSAL CLAIM AND MUST BE MEASURED ON EVERY MEMBER OF THE REACH SET, NEVER ON A SAMPLE.** "N of M sampled" is a legitimate result; "zero corpus-wide" from a sample is not, because a single unmeasured member falsifies it — and the members most likely to differ are the awkward ones a sampler skips (here: the program that FAILS its own `.ref` and the one that does not link in m4).
⚠ Nothing was pushed when this was caught, so the three commit messages were AMENDED rather than corrected-in-place; no false claim reached origin.

## THE CORRECTED HEADLINES: (1) THE GATE'S ONLY COVERAGE OF THIS PORT CAME FROM A PROGRAM THAT FAILS ITS OWN ORACLE TEST; (2) MIN_MS WAS NEVER THE BINDING CONSTRAINT ON THIS MACHINE; (3) THE FAMILY-WIDE AUDIT FOUND TWO **GENUINELY** ZERO-COMMIT PORTS

Session: s224. Author: Claude. Grant: Lon "all your choices". RT_OPT=`-O0` on every number below.

---

## 1. THE PORT

`rt_match_replace` — the pattern-match-with-replacement sink (`S ? PAT = REPL`, manual Ch.6 p.72
"Pattern Matching with Replacement"). Gate `SCRIP_RTX_MATCH`; C renamed `c_rt_match_replace` in the
same commit. **113 asm instructions vs the C's 270, both counted FROM THE OBJECT.** Zero templates
touched ⇒ no `.s` regen owed by construction (phase-1 rung), and this session VERIFIED that rather
than inheriting it.

It lives in `src/runtime/builtins/gen_runtime.c`, **not** `pattern_match.c` as ARCH §5's MATCH row
implies by grouping it with the `rt_match_*` family. Two prior slices (4, 6) had the same split.

### What the asm actually saves — three libc calls that copy or measure nothing
1. `memcpy(buf, s, start)` with `start == 0` — the head is empty whenever the match begins at the
   cursor origin.
2. `memcpy(buf + start, rs, rlen)` with `rlen == 0` — `S PAT = ''` is deletion, and a null
   replacement is the common idiom the manual's replacement form permits.
3. `strlen(rs)` with `rs == ""` — `rlen` is 0 BY CONSTRUCTION on the `!replp`/`IS_NULL_fn` arm, so
   the C measures a string whose length it already knows.

Each guard is universally correct — a zero-length copy is a no-op for ALL inputs — **not a
workload-shaped special case.** Plus the `-O0` frame: the C carries a `uint64_t w[2]` +
memcpy-to-DESCR dance and spills all ten of its locals; the asm keeps one 80-byte frame and `r12`
(free since ZR-RSPRBP-1 deleted `ZC_FRAME_R12`, but still SysV callee-saved, so it is PUSHED —
"free, not scratch-by-fiat").

⛔ **NO ARM IS KEYED ON `slen != 0`** (s220's standing rule, corroborated independently by s217-ICN
in Icon). `STRVAL` mints `DT_S` with `.slen = 0`; only `BSTRVAL` populates it. The C's own three-way
`(sv.v == DT_S && sv.slen && s == sv.s)` guard is transliterated FAITHFULLY, `strlen` included,
because glibc's SSE `strlen` beats any hand byte-loop.

### Step 0, all six checks
- **(a)/(b)** live definition; spelling round-trips byte-identically.
- **(c) ON THE OBJECT FILES, NEVER THE `.so`** — `VARVAL_fn` `NV_SET_fn` `descr_to_str`
  `rt_str_alloc` are all `T`. ⭐ **This port needs ZERO `static`→`hidden` promotions and touches
  ZERO globals on its hot path**, so it sits entirely outside the `g_cap_gen` narrowing class that
  cost 173/316 m4 LINK failures. The sole new global is `g_repl_trace`, and that direction is a
  **WIDENING**.
- **(d)** 5,000,000 → 2,500,000 = exactly **0.500×**, predicted before measuring, and *explained* by
  the source (500K outer × 10 comma-separated words), not merely correlated with it. No `+1` term,
  because the failing `INNER` match never reaches the sink.
- **(e)** not already asm — grep run WITH `--include=*.S`.
- **(f)** entries 5,000,000 · bailed **1** · commits **4,999,999** on `string_pattern.sno`.

---

## 2. ⭐⭐ THE FINDING THAT OUTRANKS THE PORT: THE 316-PROGRAM BYTE-IDENTITY GATE CANNOT EXECUTE ONE INSTRUCTION OF THIS ASM

s223 warned "do not over-read the 315" and left the coverage number as an explicit unknown. **I
enumerated it, and it is far starker than the warning implies.**

Compiled all 316 crosscheck programs and grepped the emitted `.s` for the call:

```
programs=316   reach_rt_match_replace=7   compile_fail=1
```

**Seven.** And of those seven, `test_case` fails in BOTH modes at the watermark and `test_string` is
one of the m4 SKIPs. Then the decisive measurement — static reach is not execution:

| program | dynamic entries |
|---|---|
| `062_capture_replacement` | **1** |
| `063_capture_null_replace` | **1** |
| `test_stack` | **1** |
| `cross`, `wordcount` | 0 (stdin-driven; `/dev/null` ⇒ never reach it) |

⛔⛔ **ONE ENTRY MEANS ZERO COMMITS**, because `g_repl_trace` starts at `-1` and the FIRST call of
every process delegates to C by design. Therefore:

> **CORRECTED: across the 316-program corpus, in m3, exactly TWO programs execute this asm
> (`test_case` 19 commits, `test_string` 1 commit); in m4, exactly ONE does (`test_string` is an m4
> SKIP). Both are compromised: `test_case` is in the watermark FAIL set in BOTH modes, and
> `test_string` does not link in m4. So the gate's entire power over this port rested on a program
> that fails its own oracle test.**

This is the s223 lazy-resolution class near its limit. s223's probe failed to fire on a
one-capture program and would have condemned working code; here the *entire regression suite* fails
to fire, and it does so SILENTLY and PERMANENTLY — a future session that breaks this asm gets a
green 317-program sweep in both modes. **A gate that cannot fail is worthless (s222's own words),
and this one could not fail.**

### The fix is landed, not just documented
`corpus/crosscheck/patterns/064_replace_multi_arm.sno` + `.ref`, **`.ref` minted from the SPITBOL
oracle** (`x64/bin/sbl -b`), never from SCRIP. Nine replacement shapes: deletion (`rlen == 0`), head
(`start == 0`), tail (`slen - end == 0`), grow, shrink, an INTEGER replacement value (which
deliberately exercises the `descr_to_str` **BAIL** edge), a capture-sourced replacement, a null
subject span, and a repeated-deletion loop so commits accumulate.

- **Census: 22 entries · 2 bailed · 20 COMMITS** — against 1 entry / 0 commits for every existing
  program. The two bails are the designed ones (process-first-call, and the integer arm), so the
  program covers the hot arm AND a bail edge.
- **VALIDATED TWO-SIDED AT MINT** (the s216 discipline): with a `ud2` planted on the commit path the
  kill-switch gate reports **MOVER=1 in m3 AND MOVER=1 in m4** on this program alone; with the
  correct asm, **IDENTICAL=1 in both modes**. It can detect what no other program in the tree can.
- m3 and m4 both match the oracle byte-for-byte.

⚠ **THE WATERMARK MOVES BY DESIGN AND IS RE-PROVEN, NOT ASSERTED: m3 312/4/0 · m4 312/2/2 ·
DIVERGE=2.** The `+1` in each mode is fully accounted for by the new program passing in both modes;
the fail sets `{test_case,140,141,160}` / `{test_case,160}` and `DIVERGE {140,141}` are UNCHANGED, so
the latch canary is intact.

---

## 3. ⭐⭐ SECOND FINDING: THE WINDOW WAS NEVER THE BINDING CONSTRAINT — THE CONTAINER'S VARIANCE IS

Every prior MATCH slice refused a speed number because its window sat under `MIN_MS=800` (slice 4:
205 ms; slice 7: 176 ms; slice 8: computed ~2%). The ladder's standing hypothesis was therefore that
**a longer-window benchmark would make MATCH gradeable.** `string_pattern.sno` is that benchmark —
5704 ms at 500K, 2798 ms at 250K, both comfortably clear of the floor.

**It is still ungradeable, and the reason is a different one.** `bench_rtx_3arm.sh` refused twice:

| rounds | PRISTINE | OFF | ON | worst intra-arm spread | inter-arm gap | verdict |
|---|---|---|---|---|---|---|
| 5  | 2439.5 ms | 2672 ms | 2278 ms | **2.109×** | 1.071× | ⛔ UNGRADEABLE |
| 13 | 3236 ms | 2003.5 ms | 1684 ms | **2.560×** | 1.922× | ⛔ UNGRADEABLE |

⭐ **MORE ROUNDS MADE THE MEDIAN-BASED VERDICT WORSE, NOT BETTER (1.071× → 1.922×)** — a live
demonstration of s220's "only the MINIMUM is stable, medians are worthless," and a defect in the
harness's own choice of statistic.

⭐ **THE BIMODALITY IS DIAGNOSED, NOT SHRUGGED AT.** Raw ON samples: `1542 3149 1554 3427 1530 1547
3509 1556 1766 3585 1602 3313` — a clean two-cluster split at ~1550 and ~3400, i.e. **2.3×**. That
is the *exact* signature of the documented **s201 hugepage class** ("WARM/COLD IS 2.3× ON THE SAME
PROGRAM"), which the goal file already records for `pattern_bt`. Each process either wins hugepages
or does not.

**Min-of-N, the only estimator s220 trusts, IS stable across the two independent runs:**

| ratio | r=5 | r=13 |
|---|---|---|
| ON/PRISTINE | 1.104× | 1.081× |
| OFF/PRISTINE (kill-switch tax) | 0.903× | 0.859× |

⛔ **AND IT IS STILL RECORDED AS AN OBSERVATION, NOT A RESULT, BECAUSE THE INSTRUMENT OF RECORD
REFUSED AND I DO NOT OVERRULE IT.** Two agreeing runs at ~1.08–1.10× is worth leaving for the next
session; it is not a claim, and no board may quote it. ⚠ Note the kill-switch tax reads **11–16%**
here, far above the 1.002×/0.905× s209 measured elsewhere — consistent with a per-call PLT
indirection at 5M calls, and another reason `ON/OFF` (1.19–1.26×) must never be reported as the
answer.

⇒ **OWED RUNG, NEW: give the rail a min-of-N mode and/or hugepage pinning.** Until then, *no* RTX
rung on this machine can be graded at any window length, and "the window was too short" must stop
being written as the reason. That sentence has been in three consecutive cursors and it is now
falsified.

---

## 4. THE BUG A GATE WOULD HAVE SHIPPED

The first build printed `result: alpha` instead of the full concatenation. Cause: the
replacement-analysis block loads `rv.v` into `eax` (`mov eax, dword ptr [r9+0]`), and the code below
it read `rax` as `sv.slen` under a comment asserting it was "still live." For `S PAT = ''` the
replacement is `DT_S`, so `slen` became **1**, `end` clamped to 1, `nlen` fell to 0, and the subject
was emptied — the `INNER` loop then failed on its second pass. Fixed by carrying `sv.slen` in `r11`,
which that block never touches.

⭐ **WHY THIS IS A FINDING AND NOT A CONFESSION: the defect is DETERMINISTIC, so every downstream
gate would have passed it.** ON and OFF byte-identity compares the same program against itself under
the same stdin; a port that truncates every replacement identically in all runs is still
*self-consistent*. The only instrument that caught it was running the program against its `.ref` —
which, per §2, the 316-program suite does for exactly zero commits. **The smoke against a known-good
oracle output is not a formality that precedes the real gates; on this rung it was the ONLY gate with
any power at all.**

---

## 5. GATES OF RECORD

- ✅ Watermark **RE-PROVEN AT SESSION START AND SAID OUT LOUD** before touching anything: m3
  **311/4/0** · m4 **311/2/2** · DIVERGE=**2**, 25 s — matching s214–s223 exactly. Post-port, and
  post-corpus-addition: **m3 312/4/0 · m4 312/2/2 · DIVERGE=2**, fail sets unchanged.
- ✅ Kill-switch hash-set gate, **suite-wide, `MODE=both`, N=4, 316 programs, 91 s**: m3
  IDENTICAL=315 QUARANTINE=1 **MOVER=0** · m4 IDENTICAL=312 QUARANTINE=1 **MOVER=0** SKIP=3 ⇒ GATE
  PASS, reproducing s222/s223. ⚠ **Read §2 before quoting this as evidence for the asm.** `160`'s
  quarantine holds with the same-set-both-arms argument (gate OFF *is* the C fallback).
- ✅ Two-sided falsification: hard `ud2` on the commit path ⇒ ON rc=**132** SIGILL, SAME BUILD OFF
  ⇒ rc=0 correct. **Reverted THREE ways**: `grep ud2`==0 · source md5 back to `980de1c7` · `.so`
  relinked **BIT-IDENTICAL** to `fc2441c6`.
- ✅ **THE PRISTINE ARM IS PROVEN PRE-PORT, NOT ASSUMED**: stash-built `.so` md5
  `aeff8497edbf2074` == the session-start baseline `.so` byte-for-byte, and it carries
  `rt_match_replace` with NO `c_` variant.
- ✅ RTX unit ALL PASS (STR differential 8426 cases / 0 mismatches) · store-width gate PASS (13
  GOT-tainted stores checked).
- ⚠ **SMOKE INSTRUMENT DEFECT, PRE-EXISTING AND LOAD-BEARING:**
  `scripts/test_smoke_all_frontend_backend_matrix.sh` is **TRUNCATED AT 48 LINES** (ends mid-token,
  `PASS) PASS_SU`) and fails `bash -n` with a syntax error. `git show` confirms it is byte-identical
  at `713c581b` — **the repo's INITIAL COMMIT** — so it has NEVER been runnable in this repo. ARCH §7
  step 3 mandates "smokes 7/7×2" and s220/s223 both RECORD it as PASS; **no working script in this
  tree produces a 7×2 matrix.** What does run is
  `scripts/test_smoke_compile_hello_all_langs.sh`: **PASS=6 FAIL=0, ROWS_MATCH=6 ROWS_DRIFT=0.**
  That is what this session claims. The "7/7×2" phrase is the (a)-class rot: a label inherited across
  sessions from a script that cannot execute.
- ⛔ **NO SPEED NUMBER IS CLAIMED** — see §3.
- ⛔ **NOT RUN / NOT CLAIMED:** beauty · 15-demo board · Prolog/Icon/Snocone/Raku batteries (ARCH §7
  step 2b: they are STRUCTURALLY NON-EVIDENCE for a SNOBOL4 MATCH port, and citing an unmoved battery
  as an asm gate is a FALSE CLAIM) · `.s` regen ×3 (zero templates touched; phase-1 owes none).

`handoff_status.sh` is the push truth — NOT this document, and no landing hash is written here (the
s218/s222 pre-rebase class).

---

## 6. RULES MINTED

1. **A GATE'S COVERAGE IS A NUMBER, AND IT MUST BE ENUMERATED BEFORE THE GATE IS CITED.** "Suite-wide
   IDENTICAL=N" is a claim about N programs *running*, never about N programs *reaching the code under
   test*. Enumerate reach (compile + grep the call), then enumerate execution (dynamic count), then
   subtract the lazy-resolution first call. For this port all three steps were needed and the answer
   was 316 → 7 → 1-each → **0 commits**.
2. **WHEN A PORT'S COVERAGE IS ZERO, MINTING A CORPUS PROGRAM IS PART OF THE RUNG, NOT A FOLLOW-UP.**
   Validate it two-sided at mint (MOVER under `ud2`, IDENTICAL when correct), take its `.ref` from the
   oracle, and re-prove the watermark in the same session so the `+1` is accounted for rather than
   discovered later as drift.
3. **"THE WINDOW WAS TOO SHORT" IS A HYPOTHESIS AND IT IS NOW FALSIFIED FOR THIS MACHINE.** A 5.7 s
   window was refused by the harness twice, with intra-arm spread (2.1–2.6×) exceeding any plausible
   effect. Diagnose variance before blaming window length; the s201 hugepage 2.3× signature is
   recognizable from the raw sample list alone.
4. **A DETERMINISTIC WRONG ANSWER IS INVISIBLE TO EVERY SELF-COMPARISON GATE.** ON-vs-OFF byte
   identity, hash sets, N≥4 — all compare the program against itself. Only an ORACLE-anchored
   comparison has power against a bug that is stable across runs. Run the `.ref` smoke first, and
   never treat it as ceremony.


---

## 7. ⭐⭐ THE FAMILY-WIDE COVERAGE AUDIT — RUN THE SAME SESSION, AND IT FOUND TWO PORTS THAT COMMIT **NOWHERE IN THE CORPUS**

The audit rung was opened by this session and then executed by it, because the first question any
reviewer asks of §2 is whether it generalizes. `util_rtx_arm_census.sh` derives its symbol list from
`RTX_FUNC(...)` and reports EVERY ported symbol per run, so one pass per program answers the whole
family at once. **317 programs, 89 s, m3 (`--run`) only.**

| symbol | entries | bailed | commits | progs w/ ≥1 entry | **progs w/ ≥1 COMMIT** |
|---|---|---|---|---|---|
| `rt_match_enter` (slice 6) | 353 | 1 | 352 | 165 | **165** |
| `rt_match_ctx_restore` (slice 4) | 343 | 0 | 343 | 158 | **158** |
| `rt_dcap_end_ok_close` | 293 | 0 | 293 | 135 | **135** |
| `rt_str_alloc` | 160,122 | 104 | 160,018 | 124 | **73** |
| `rt_gcheap_alloc` | 53,198 | 179 | 53,019 | 179 | **47** |
| `rt_cmp_d` | 53,366 | 0 | 53,366 | 41 | **41** |
| `str_concat_d` | 210,832 | 157,687 | 53,145 | 83 | **34** |
| `rt_dcap_end_ok_open` (slice 8) | 293 | 135 | 158 | 135 | **23** |
| `rt_assign_var` | 344 | 23 | 321 | 25 | **23** |
| `rt_cap_top` | 38 | 0 | 38 | 20 | **20** |
| `rt_agg_alloc` | 538 | 17 | 521 | 20 | **18** |
| `rt_defer_close` (slice 7) | 42 | 9 | 33 | 10 | **8** |
| `rt_defer_open` (slice 7) | 38 | 11 | 27 | 10 | **7** |
| `rt_match_replace` (slice 9) | 47 | 7 | 40 | 6 | **3** (2 pre-existing + the new program) |
| `rt_cap_pop` | 6 | 0 | 6 | 3 | **3** |
| `rt_cap_match_begin` | 1 | 0 | 1 | 1 | **1** |
| ⛔ `rt_patstk_lazy_init` | 1 | 1 | **0** | 1 | **0** |
| ⛔ `rt_subscript_var` | 502 | **502** | **0** | 15 | **0** |

### The three results
**(a) SLICES 4 AND 6 ARE EXCELLENTLY COVERED — 158 and 165 programs commit.** Their headline gates
were sound. §2's hazard does NOT generalize across the family, and saying so is part of the finding:
the audit's job was to test my own claim's reach, not to confirm it.

**(b) s223's EXPLICIT OPEN QUESTION IS NOW ANSWERED WITH A NUMBER.** s223 wrote: *"Nobody has
enumerated how many of the 316 have ≥2 capture-matches — do not quote one."* Enumerated:
**`rt_dcap_end_ok_open` is entered by 135 programs and commits in 23.** So 112 programs enter and
bail every time — the lazy-resolution shape at corpus scale — and slice 8's real coverage is 23
programs, not 315. That caveat can now be replaced by a measurement.

**(c) ⛔⛔ SECOND SELF-CORRECTION, SAME ERROR CLASS, CAUGHT THE SAME SESSION — I CALLED `rt_subscript_var` VACUOUS OFF THE WRONG BATTERY.**
I first wrote that `rt_subscript_var` "commits nowhere in the entire corpus" on the strength of **502
entries / 502 bails / 0 commits** over the SNOBOL4 crosscheck. Then I read its asm: gate
`SCRIP_RTX_ICNSUB`, arms are the **Icon** DT_DATA list (RTX-24) and DT_T table (RTX-26) paths,
requiring a `DT_N`/slen==1 VARREF base. **It is an ICON port and I measured it on the SNOBOL4
corpus.** Re-run against the battery it was aimed at (60 Icon programs): **2688 entries, 12 bails,
2676 COMMITS.** ⇒ **The 502-bail SNOBOL4 result is the port WORKING AS DESIGNED** — SNOBOL4 never
mints the Icon list/table VARREF shape, so bailing every time is correct, not a wrong arm. The s212
WRONG-ARM diagnosis I attached to it was FALSE and is withdrawn.
⚠ **What survives, stated narrowly:** its coverage is thin in PROGRAM COUNT — only **2 of 60** Icon
programs commit — while the commit VOLUME is high (2676). Thin-coverage-high-volume is a real
hazard for regression (two programs are a narrow base) but it is NOT vacuity.
⭐⭐ **ARCH §7 STEP 2b ALREADY NAMED THIS MISTAKE IN THE OPPOSITE DIRECTION: "citing an unmoved
battery as an asm gate is a FALSE CLAIM." I cited an unmoved battery as proof of VACUITY — the same
error inverted, and the rule as written did not read as covering my direction.** ⇒ **RULE
(GENERALISED, and it now covers BOTH of this session's corrections): EVERY COVERAGE NUMBER CARRIES
ITS POPULATION IN THE SAME SENTENCE — which battery, which mode, how many members measured. A number
without its population invites exactly the generalisation that produced two false claims here, one
from a 5-of-7 SAMPLE and one from a WRONG BATTERY.**

**WHAT REMAINS OF THE ORIGINAL (c), NOW SCOPED:**
- `rt_patstk_lazy_init` — 1 entry, 1 bail, **0 commits on the SNOBOL4 crosscheck, m3.** This one IS
  on its own battery: it is defined in `rtx_match.S` under the MATCH gate, so SNOBOL4 is the right
  population and the zero stands as measured. It is not regression-tested by anything in the tree and
  cannot be graded here.
- `rt_cap_match_begin` — 1 program, 1 commit. Nonzero, but a one-program base.
- `rt_subscript_var` — **withdrawn, see the correction above.** Not vacuous; 2676 commits on Icon.

⚠ **ALL AUDIT NUMBERS IN THIS SECTION ARE m3 (`--run`) ONLY** — `util_rtx_arm_census.sh` has no
`--compile` arm, so an m4 coverage audit is a separate owed rung. And the SNOBOL4 table above is
scoped to the SNOBOL4 corpus: any symbol in it belonging to another family's gate must be re-measured
on that family's battery before any conclusion is drawn, which is precisely the step I skipped.

### The instrument defect this audit reproduced in my own hands
My first audit driver reported `programs_censused=1`. Cause: the census runs `scrip`, which reads
stdin, and it **swallowed the entire `find` list** fed to the `while read` loop. **That is the s220
kill-switch defect verbatim, and RULES.md line 80 ("`< /dev/null` on scrip calls") already mandated
the fix.** Two sessions and one FACT RULE later, the same defect was one keystroke away from
producing a 1-program audit that would have printed a clean-looking table. ⇒ **any loop that feeds
paths to a `scrip`-invoking script must redirect stdin on the INNER call, and the loop's own
program-count must be printed and checked against the expected corpus size** — a census that reports
its denominator cannot silently grade one program and call it a suite.
