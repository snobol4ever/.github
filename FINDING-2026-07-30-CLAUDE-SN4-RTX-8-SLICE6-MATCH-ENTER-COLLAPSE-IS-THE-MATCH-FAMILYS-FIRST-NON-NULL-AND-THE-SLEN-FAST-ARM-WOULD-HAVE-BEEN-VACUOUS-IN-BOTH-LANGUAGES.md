# FINDING s220 — `rt_match_enter`'s HOT-PATH COLLAPSE IS THE MATCH FAMILY'S FIRST NON-NULL (1.135× ON/PRISTINE), AND THE OBVIOUS `slen` FAST ARM WOULD HAVE BEEN VACUOUS — IN BOTH LANGUAGES

**Artifact of record: `.so` md5 `f07ae4a413fe` from the committed source (`make -q` rc=0); the watermark was re-proven on these exact bytes after the `_Static_assert`s landed. `69e8f480` is the pre-assert build the `ud2` revert was proven bit-identical against, not the committed artifact.**

**Session s220, 2026-07-30. Goal `GOAL-SNOBOL4-RTX.md`, rung RTX-8 SLICE 6. Base: SCRIP `99fd76e4` (s219b), `local == origin` at orientation. RT_OPT=`-O0` on every number below.**

---

## 0. WHAT LANDED

`rt_match_enter` in `src/runtime/rtx/rtx_match.S`, gate `SCRIP_RTX_MATCH`, C body renamed `c_rt_match_enter` (`gen_runtime.c:127`) in the same commit. **ZERO templates ⇒ no `.s` regen owed** (phase-1 property).

It is the first MATCH rung that removes **calls** rather than instructions. The C performed five calls per match; four are inlined:

| callee | per-match | disposition |
|---|---|---|
| `rt_cap_match_begin` | 1 | **inlined** (generation bump + zero-wrap) |
| `rt_dcap_lazy_init` | 1 | **inlined test** (pinned VA, absolute disp32) |
| `rt_patstk_lazy_init` | 1 | **inlined test** (GOT, exported) |
| `VARVAL_fn` | 1 | **inlined** DT_S arm (`return v.s`) |
| `strlen` | 1 | **retained** — C semantics demand a fresh length; glibc SSE beats any hand byte-loop |

Object instruction counts, counted **from the object**: asm **55** (including both cold arms) vs C **97**.

---

## 1. ⛔⛔ THE FINDING THAT SAVED THE RUNG: THE `slen` FAST ARM FIRES ZERO TIMES

The obvious fast arm is "DT_S carrying a cached `slen` ⇒ return `slen`, skip `strlen`." **Measured on `pattern_bt` at K=2,000,000 with an interposer classifying `rdi`/`rsi` per call:**

```
ARM-FAST  DT_S s!=0 slen!=0    0            <-- the arm I first designed
ARM-SLEN0 DT_S s!=0 slen==0    2000001      <-- 100%
ARM-CSET / ARM-SNULL / ARM-NOTS  0 / 0 / 0
```

Cause: `STRVAL` (`core.h`) mints DT_S with `.slen = 0`; only `BSTRVAL` populates it, so a plain SNOBOL4 string assignment never carries its length. **A port built on that arm would have assembled, gated green, been byte-identical over all 316 programs, and moved nothing** — the s217 slice-3 vacuous-rung mode exactly. It was caught **only** because the rung text said *census the arms BEFORE choosing*, and for once that instruction was obeyed before the asm was written rather than after.

⭐⭐ **THIS IS NOW A CROSS-LANGUAGE FACT WITH TWO INDEPENDENT MEASUREMENTS.** The Icon side reached the identical conclusion at s217-ICN (`FINDING-...-ICN-RTX-9-SUBSCRIPT-GET2-FAST-ARM-WOULD-HAVE-BEEN-VACUOUS-AND-SLEN-IS-NEVER-POPULATED`): `arr.slen == 0` on 100% of arrivals, "slen usable = 0" on both a synthetic and a real corpus. Two languages, two front-ends, two sessions, same result.

⇒ **RULE: NO RTX FAST ARM IN EITHER LANGUAGE MAY BE KEYED ON `slen != 0` UNTIL A LOWER-SIDE RUNG POPULATES IT.**

⇒ **AND THE BIGGER PRIZE IS NOT THIS RUNG.** Populating `slen` at assignment would delete **2,000,001 `strlen` calls per run** on this workload alone, on a string whose length is known at assignment time. That is a **LOWER/descriptor rung, not an RTX rung** — recorded, not acted on, same discipline as RTX-5's *"an asm port would faithfully reproduce a poor algorithm at high speed."*

---

## 2. THE SPEED NUMBER, AND WHY IT IS QUOTED WHEN s219's WAS REFUSED

s219 measured the whole MATCH family gate at **ZERO** (903 vs 890 ms) and correctly refused a number, concluding that the only remaining lever was `rt_match_enter`'s hot path. **That conclusion is now confirmed by measurement.**

Three-arm rail per ARCH §7 step 4, `pattern_bt_deep` (8M), min-of-N, discard run 1:

| arm | fixed-order min | rotated-order min |
|---|---|---|
| ON (ported) | 1565 ms | 1589 ms |
| OFF (kill-switch) | 1752 ms | 1826 ms |
| PRISTINE | 1778 ms | 1804 ms |

**ON/PRISTINE = 1.135×** — and it reproduced across two independent harness layouts (**1.136×** and **1.135×**). ON/OFF = 1.149× within one binary (the cleanest attribution: one byte differs). OFF/PRISTINE ≈ 0.99–1.02× ⇒ **the kill-switch tax is ~0 on this program**, consistent with s209's finding that the tax is program-dependent and not a subtractable constant.

⚠ **THE VARIANCE IS STATED PLAINLY BECAUSE IT IS SEVERE: individual runs swing up to 4.7× within one arm** (PRISTINE read 1804 → 7545 ms). **Only the minimum is stable; medians are worthless here.** My first single-run read was ON=219 / OFF=128 ms — i.e. it said the port was 1.7× SLOWER — at a ~130 ms window. That reading was pure noise and would have reverted a correct port had I trusted it. **RE-STATING THE LADDER'S OWN RULE BECAUSE I NEARLY BROKE IT: a window below MIN_MS is not weak evidence, it is anti-evidence.**

⚠ **AND THE ARM ORDER IS A CONFOUND, WHICH IS NEW:** the fixed-order rail was **bimodal and anti-correlated by position** — ON fast on rounds 1/3/5, OFF fast on 2/4. That alternation is positional, not arm-related, so a fixed-order harness can hand any arm the fast slot. **ROTATE ARM ORDER SO EACH ARM VISITS EACH POSITION**; min-of-N survived rotation, which is why the number is quotable.

---

## 3. ⭐⭐ THE OWED SUITE-WIDE KILL-SWITCH SWEEP COULD NEVER HAVE RUN — THE GATE VIOLATES RULES.md's OWN `< /dev/null` RULE

The suite-wide both-modes sweep has been owed since s217 and re-owed at s219. **It was not expensive. It was broken, and it reported PASS while broken.**

`scripts/test_gate_rtx_killswitch_sets.sh:46` invoked `scrip --run` inside a `while read` loop fed by process substitution **with no stdin redirect**. The first program that reads stdin (`fileinfo`) swallowed the remaining `find` list, so the sweep silently truncated. **Pointed at `corpus/crosscheck`, it graded 1 program of 316 and printed `GATE PASS`.** Pointed at a typo'd path it graded **0** programs and printed `GATE PASS`.

**RULES.md line 80 already mandates the fix: "`< /dev/null` on scrip calls."** The gate minted at s219 to repair a coin-flip instrument was itself defeated by a rule the project wrote down long ago. Two fixes landed:
1. `< /dev/null` on the scrip invocation.
2. **`total == 0` is now `GATE FAIL`, not PASS** — a typo'd path must not report success.

Regression-checked: the 121-program pattern run is **unchanged** (121 / 120 / 1 / 0).

**SUITE-WIDE RESULT, FIRST TIME IT HAS EVER RUN — 316 programs, N=4, 48 SECONDS:**

```
IDENTICAL = 313    QUARANTINE = 3    MOVER = 0
```

⭐ **THE QUARANTINE POPULATION IS 3, NOT 1.** Two programs beyond the known `160_pat_alt_inner_gen_resume` are non-deterministic on this suite:

```
160_pat_alt_inner_gen_resume  ON{5d701824,d7772c55}  OFF{5d701824,6a68d667,d7772c55}
413_arith_mixed               ON{b99e715c}           OFF{3e562a8b,b99e715c}
W06_len                       ON{3e562a8b}           OFF{3e562a8b,66edaec1}
```

⭐ **IN BOTH NEW CASES THE ON ARM IS STABLE AND THE OFF ARM IS UNSTABLE, AND ON's HASH IS A MEMBER OF OFF's SET.** Gate-OFF **is** the pure-C fallback, so instability visible with the gate OFF cannot have been caused by the asm — the gate's own discrimination principle, now doing real work on programs nobody knew were unstable.

⚠ **AND `160`'s SET IS STILL NOT ENUMERATED AT N=4:** s217 saw 3 hashes, s219 recorded a 2-element set `{6a68d667,d7772c55}`, s220 sees `{5d701824,d7772c55}` / `{5d701824,6a68d667,d7772c55}` — **three sessions, three different memberships.** s219's two-element reading was itself a sample artifact. N=4 detects non-determinism; it does not characterise it. Do not quote a hash set for `160` as if it were closed.

⚠⚠ **SCOPE, STATED PLAINLY SO IT IS NOT OVERCLAIMED: THIS IS `--run` (m3) ONLY. The script has no `--compile` arm at all**, so "suite-wide **both modes**" is discharged for m3 and **still owed for m4**. Growing the m4 arm is the next instrument rung.

---

## 4. CORRECTNESS: WHY BAIL-BEFORE-MUTATE IS NOT FREE HERE

s219's `rt_patstk_lazy_init` got bail-before-mutate for free because its asm mutates nothing. **This rung does not.** `rt_cap_match_begin` is **not idempotent** — it bumps the monotonic generation well every call. A delegation placed *after* the inlined bump would make `c_rt_match_enter` bump a **second** time, issuing two generations for one match and retiring capture brackets the outer match still owns: silent, links fine, passes short tests — the s215 double-push/double-pop hazard.

⇒ **All three delegation edges are placed BEFORE `.Lme_mutate`, and nothing above that label writes memory.** The two cold edges below it call the **individual** helpers, never the whole body, for the same reason. Delegated arms: `v != DT_S`; `s == NULL` (that arm of `VARVAL_fn` **allocates** — never replicate an allocation in asm); and `slen == 0 && *s == 0`, where `IS_NULL_fn` is true and C returns the `""` **literal**, a different pointer than `v.s`, which `Σ` must receive.

**0(c), read on the objects and never on the `.so`:** `Σ` `B`@0x0, `Σlen` `B`@0x14, `g_cap_gen` `D`@0x0, `g_patstk_sp` `B`@0x8 — all four present in the dynamic table ⇒ `@GOTPCREL` mandatory. `g_cap_gen_next` `D`@0x4 is **absent** from the dynamic table (hidden) ⇒ direct `[rip+sym]`. `g_cap_gen`/`g_cap_gen_next` are adjacent at +0/+4, so every store is `dword ptr` **and each global is addressed by its own name** rather than as `[r10+4]` off its sibling — the port carries no dependency on a layout it cannot enforce.

`g_dcap_top` is **not a symbol**: it is `#define g_dcap_top (*(const char **)RT_CAS_TOP)`, a build-constant pinned VA (`pin_va.h`, `0x70000000`), reached by absolute disp32 (`48 8b 04 25`) — the same form `ABSQ()` bakes in the templates, no GOT and no RIP-relative.

The cold edges deliberately **do not** use `RTX_CALL_ALIGN`, because that macro borrows `rbp`, which is a **per-graph pin** (FLATDISP-8). They align by push count instead: entry `rsp` is 8 (mod 16), so `push`+`push`+`sub 8` reaches 0, and on the `strlen` edge a single `push rsi` both aligns **and** preserves the subject pointer.

---

## 5. GATES — ALL GREEN, AT THE WATERMARK

- **Two-sided HARD `ud2`:** planted on the fast path ⇒ gate ON `rc=132` SIGILL; **SAME BUILD** gate OFF ⇒ `rc=0` and correct output.
- **Revert verified THREE ways:** `grep ud2` = 0 · source md5 `4214f1df` · `.so` relinked **BIT-IDENTICAL** (`cmp` clean) to the pre-probe ported build `69e8f480`.
- **Pristine arm bit-identical to the session-start build** (`b5f1736f`), which discharges the revert proof for the whole port for free.
- **Watermark RE-PROVEN:** m3 **311/4/0** · m4 **311/2/2** · **DIVERGE=2**, failure sets **line-by-line identical** to session start, **ZERO movers**. `140`/`141` still red-m3 / green-m4 ⇒ **the defer-latch canary is intact**. 26 s.
- **0(f) post-port census:** entries **2,000,001** · BAILED_C **0** · COMMITS **2,000,001** ⇒ the asm handles 100%, zero delegation.
- **0(d):** entries = K+1 **predicted in advance**, measured 2,000,001 → 4,000,001 = exactly **2.000×**; `descr_to_str` flat at **6** (the DT_S fast path holds, coercion is NOT the cost); `VARVAL_fn` 2,000,011 → 4,000,011, constant +10 preserved.
- **Store-width gate** PASS (12 GOT-tainted stores checked against ELF symbol sizes). **RTX unit** ALL PASS (8426 cases, 0 mismatches).
- **Kill-switch hash-set gate** suite-wide m3: 313 / 3 / **0 movers**.

**NOT RUN / NOT CLAIMED:** beauty (still m3-BLOCKED at EMIT on `emit_chain returned NULL`, gate-invariant, cannot be evidence either way) · 15-demo board · m4 arm of the kill-switch sweep (the script has none) · Prolog/Icon/Snocone/Raku. ✅ smokes 7/7×2 PASS (m4 HARD GATE), 1 s .

---

## 6. §ENVIRONMENT FACTS IS PESSIMISTIC BY 3.4× FOR THE FULL BUILD, AND THE WARM/COLD GAP IS 2.3×

All timed with `date +%s`, not estimated:

| operation | documented | **measured s220** |
|---|---|---|
| full runtime rebuild (248 objects) | ~8.5 min | **149 s** |
| one `.S` edit + reassemble + relink | 3 s | **1 s** |
| full both-modes 315-program crosscheck | 25 s | **26 s** ✓ |
| suite-wide kill-switch sweep, 316 progs × 8 runs | (assumed expensive) | **48 s** |

⇒ The rebuild figure is **3.4× pessimistic** in this container. s218 already corrected the ladder for treating probe rebuilds as expensive; the same correction applies one level up — **even a FULL rebuild is under three minutes here.** Know which container you are in before budgeting anything.

⚠ **WARM/COLD IS A 2.3× EFFECT ON THE SAME PROGRAM** (hugepage compaction, the s201 class): `pattern_bt` at 2M read **932 ms cold** and **~400 ms warm**. ⇒ **s219's recorded "4M ≈ 870 ms" is a COLD reading; warm, 4M is ~800 ms, i.e. AT the MIN_MS floor rather than clear of it.** Apply MIN_MS to the **warm** window or every rung grades on a cold flier. `pattern_bt_deep.sno` (8M, ~1.6 s warm) is committed to corpus with a `.ref` whose checksum was predicted in advance — the s219-owed instrument, now durable instead of living in `/tmp`.

---

## 7. INSTRUMENT DEFECT: `util_rtx_count_syms.sh` SEGFAULTS ON `rt_dcap_lazy_init`

`bash scripts/util_rtx_count_syms.sh <prog> rt_dcap_lazy_init` ⇒ **rc=139**, "NO DATA — every named symbol counted zero." `rt_match_enter`, `VARVAL_fn` and `descr_to_str` all thunk correctly in the same harness, so it is symbol-specific, not a harness-wide fault. Most likely the preload copy interposes libscrip_rt's **internal** calls to an exported symbol whose `RTLD_NEXT` resolution is not yet valid at first call. **Consequence for future rungs: this symbol's 0(d) cannot be obtained with the standard tool** — the arm census (`util_rtx_arm_census.sh`) and a hand-rolled classifier both work and were used here. Not fixed this session; recorded so the next rung does not read the zero as "never called."

---

## 8. THE s218 `_Static_assert` ITEM IS NOT EXPRESSIBLE AS WORDED — CLOSED AS CORRECTED

s218 asked for a `_Static_assert` on the `g_cap_gen`/`g_cap_gen_next` and `Σ`/`Σlen` **adjacencies**, and it stayed undone for three sessions. **C cannot express it:** `offsetof` works only inside an aggregate, and two independent globals have no statically-known relative address, so no `_Static_assert` can name their distance.

**What IS expressible is the WIDTH, and width is the whole of what the adjacency endangers** — the hazard is never "they moved apart," it is "a store wider than the target reached the neighbour." Landed in `rtx_init.c`: `sizeof(g_cap_gen) == 4 && sizeof(g_cap_gen_next) == 4` and `sizeof(Σlen) == 4`, plus `RT_CAS_TOP == 0x70000000` anchoring the absolute disp32 this port bakes. `test_gate_rtx_store_width.sh` (s219b) enforces the same property dynamically from ELF symbol sizes and additionally covers globals these asserts do not name. **Item closed as CORRECTED, not as done-as-asked.**

---

## 9. DOC ROT OBSERVED AT ORIENTATION

**HEAD was `99fd76e4` (s219b), one commit AHEAD of what the LIVE CURSOR describes** (`a84435fd` = s219), and s219b had **already landed** the `rtx_abi.inc` r12/rbp correction the cursor still lists as owed item (4), plus the store-width gate. RULES' (a)-class rot, mild and self-correcting here only because `git log` was read before the prose was trusted. Per s218's rule every project claim in this FINDING names its ref.

---

## 10. NEXT RUNG

1. ⭐⭐ **POPULATE `DESCR_t.slen` AT ASSIGNMENT — a LOWER/descriptor rung, and by measurement it is worth more than any remaining MATCH asm port.** It deletes 2,000,001 `strlen`s per run on `pattern_bt_deep` and is confirmed dead weight in **both** SNOBOL4 and Icon. It is NOT an RTX rung; it needs Lon's routing.
2. **Grow the kill-switch gate an m4 (`--compile`) arm** — "suite-wide both modes" is still owed and the script cannot express it.
3. **Characterise the 3 quarantine programs** (`160`, `413_arith_mixed`, `W06_len`) with N≫4. All three are C-side by the gate's own OFF-arm argument; none blocks this rung.
4. **THE DEFER LATCH FIX** — unchanged, still gated free by `140`/`141`, still must never quote a speed number.
5. `util_rtx_count_syms.sh` `rt_dcap_lazy_init` segfault.

**`handoff_status.sh` is the push truth — not this block.**
