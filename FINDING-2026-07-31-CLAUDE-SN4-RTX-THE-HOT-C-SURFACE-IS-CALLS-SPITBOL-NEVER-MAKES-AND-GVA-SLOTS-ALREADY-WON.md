# FINDING — s228 (2026-07-31): THE HOT STILL-C SURFACE IS DOMINATED BY CALLS SPITBOL NEVER MAKES, AND THE FIX IS ALREADY IN THE TREE

**Session:** s228 · **Goal:** `GOAL-SNOBOL4-RTX.md` · **Lon directive:** *"Replace SCRIP's C runtime with ASM code. Do ones used by SNOBOL4 benchmarks first."* then *"All your choices."*

---

## 0. THE s227 BLOCKER DOES NOT REPRODUCE — IT WAS ζ-LADDER CHURN, NOT A REGRESSION IN THIS LADDER

s227 recorded **BLOCKER — NO PORT LANDED**, on a fresh clone of `2220cb19` measuring m3 211/105/0 with `a = ARRAY(3); x = a<1>` failing `Illegal data type`.

**MEASURED s228 at HEAD `bc4a3467` (60 commits later): the repro is GREEN.** `a<1>` returns `hello`. The ARRAY/TABLE/DATA/GC families are no longer red. s227's instruction to "bisect between a known-green ancestor and HEAD before any port" is **DISCHARGED — by a parallel session, not by this one.**

⚠ **THE LESSON IS ABOUT CONCURRENCY, NOT ARRAYS.** The ζ ladder's commit messages carry their own watermarks (`e26d4584`: *"watermark EXACT m3 232/104"*), so the corpus score at any moment is a reading of **whatever the ζ ladder is mid-way through**, not of the RTX ladder's health. An RTX session that reads a depressed watermark and concludes "something is broken" has misattributed another ladder's in-flight state to its own. **The RTX gate is a NO-REGRESSION gate — re-prove at session start, require EXACT hold, and do not care what the absolute number is.**

**WATERMARK OF RECORD, s228, said out loud: m3 276/41/0 · m4 275/41/1 · DIVERGE=2**, all 41 failures ARBNO/FENCE/capture pattern programs. Held EXACTLY across this session's change, all three fail sets byte-identical.

---

## 1. ⭐⭐ THE CENSUS INSTRUMENT WAS CONTAMINATED ON ITS FIRST EVER RUN — RANKS 1 AND 2 WERE NOT SYMBOLS

`util_rtx_whole_surface_census.sh` was minted s227 and committed **UNRUN**. Its first execution ranked:

| rank | "symbol" | entries |
|---|---|---|
| 1 | `result:` | 153,885,529 |
| 2 | `iterations:` | 101,000,000 |
| 39 | `ms:` | 22,026 |

**None of these is a symbol.** `util_rtx_count_syms.sh` deliberately appends the measured program's own stdout after a `--- program stdout` banner (so a broken run cannot masquerade as a measurement — a good design), and the census `awk` kept parsing past that banner. Any benchmark output line of the shape `<word>: <number>` became a row with an enormous entry count.

⭐ **THE FAILURE MODE IS THE ONE THIS LADDER KEEPS RE-LEARNING, INVERTED ONCE MORE.** s226's rule was *"0(d) is not a filter over a static shortlist — run it over the WHOLE surface."* s227 built that tool. But a whole-surface tool has no shortlist to sanity-check it against, so **a contaminant at rank 1 has nothing to contradict it.** The narrower the instrument, the more likely garbage is caught by a human recognising a name; the wider it is, the more it must validate its own rows.

**FIXED (`97099fec`):** guard the parse at the banner AND intersect field 1 with the derived candidate list, so a contaminant cannot be minted even if the banner text changes. Verified: re-run yields zero contaminant rows and the single-program census now agrees with a direct `util_rtx_count_syms.sh` measurement (NV_SET_fn 26, comm_var 24 on `arith_int`).

⚠ **ANY PORT QUEUE DERIVED FROM THE UNFIXED SCRIPT IS VOID.** Nothing was ported from it — s227 never ran it — but do not resurrect its output from a log.

---

## 2. ⭐⭐ I QUOTED A NUMBER BEFORE VERIFYING ITS SHAPE, AND THE CORRECTION IS THE VALUABLE PART

On first reading the census I reported to Lon that SCRIP *"identifies variables by string name at runtime, 22.7 million times."* The 22.7M total is real. **The framing was wrong, and the true distribution is the actual finding:**

| benchmark | `NV_SET_fn` | `comm_var` |
|---|---|---|
| string_pattern | 10,000,026 | 10,000,024 |
| pattern_bt_deep | 8,000,028 | 8,000,025 |
| eval_fixed | 2,000,026 | 2,000,024 |
| roman | 1,200,038 | 1,200,036 |
| mixed_workload | 1,000,046 | 1,000,044 |
| pattern_bt | 500,028 | 500,025 |
| **the other 14 benchmarks** | **26** | **24** |

⭐⭐ **FOURTEEN OF TWENTY BENCHMARKS ALREADY DO IT SPITBOL'S WAY.** They enter `NV_SET_fn` 26 times — startup only — because the **GVA slot work (s208) already taught the emitter to bind those names at compile time and store direct**. Every one of the 22.7M calls comes from six programs, and **all six are pattern-match or EVAL.** The name-string waterfall is not the general assignment path; it is the fallback the pattern/conditional-assignment path still drops into.

⚠ **A SUM OVER A CORPUS HIDES ITS OWN SHAPE. `PROGS=20` MEANT "20 PROGRAMS WERE NONZERO", NOT "20 PROGRAMS WERE HOT"** — 14 of them contributed 26 each. The census prints a PROGS column precisely so this is checkable; **read it before quoting the ENTRIES column.** Same class as s223's *"do not over-read the 315."*

---

## 3. ⭐⭐ THE ORACLE COMPARISON, RUN AS LON DIRECTED — AND IT ARGUES AGAINST TRANSLITERATION

**SPITBOL `asg01` (`bootstrap/sbl.asm:10545`) — the entire assignment path:**
```
add  xl,wa          ; xl already IS the variable's VRBLK pointer
mov  xr,[xl]
cmp  [xr],b_trt     ; trapped-variable check
je   asg02
mov  [xl],wb        ; the assignment: one store
ret
```

**SCRIP `NV_SET_fn(const char *name, DESCR_t val)` — same operation:** `_var_init()` call → `rt_sxt_break()` call → `is_protected_pat_name()` call (up to 2 `strcmp`) → `_var_bucket_find(name)` **hashes the name string** → a linear `for` loop of `strcmp` over `_var_reg` → `comm_var()` call → and on a fast-path miss a waterfall of ~20 sequential `strcmp`s against `"OUTPUT"`, `"STLIMIT"`, `"ANCHOR"`, `"TRIM"`, …

**SIZE, MEASURED:** SPITBOL `sbl.asm` = **19,064 lines** implementing the whole language. SCRIP's C runtime = **20,189 lines**. Already asm = 4,368 lines / 40 functions. ⇒ **"647 functions" is not inflation; it is the same quantity of work, cut into C-shaped pieces.** The count is not the problem.

⭐⭐ **THEREFORE THE PER-FUNCTION TRANSLITERATION STRATEGY CANNOT REACH SPITBOL, AND THIS EXPLAINS FIVE CONSECUTIVE SESSIONS WITHOUT A SPEED NUMBER.** Porting `comm_var` to asm preserves 22.7M calls and makes each marginally cheaper. **There is nothing in `sbl.asm` to port it *to* — SPITBOL never introduced it.** A rung that transliterates a C function inherits the C call graph, the C ABI boundary, and the C memory traffic; the win in the oracle comes from the *absence* of those, not from better instruction selection inside them.

⇒ **RULE: BEFORE PORTING A SYMBOL, FIND ITS COUNTERPART IN `sbl.asm`. IF THERE IS NONE, THE RUNG IS "DELETE THE CALL", NOT "WRITE IT IN ASM."** This is step 0(d)'s missing sibling: 0(d) proves the symbol is *executed*; this proves it is *warranted*.

---

## 4. ✅ LANDED — `comm_var` GUARDED AT THE `NV_SET_fn` FAST-PATH CALL SITE (`fe25de51`)

`comm_var`'s body is an immediate return unless `dbg || trace_set_n != 0 || monitor_fd >= 0`. **In production it is a no-op called 22.7 million times.** The call site now tests that same predicate first.

**SEMANTICALLY IDENTICAL BY CONSTRUCTION:** when the predicate is false, `comm_var` returned at its third statement anyway, so skipping the call cannot change behaviour. `g_comm_dbg` replaces the function-static `dbg` so the predicate is readable at the call site; it stays `-1` until first use and `-1 != 0`, so **the first call always goes through and initialises it** — no constructor, no init ordering hazard. `trace_set_n` and `monitor_fd` are already in this TU ⇒ **ZERO visibility promotions needed** (contrast s223, where three `static`→`hidden` promotions were the hard part).

**MEASURED: `comm_var` 22,700,514 → 165 entries** over the same 20 benchmarks (24–25 per program, startup only).

**TWO-SIDED:** armed (`SCRIP_DEBUG_TRACE=1`) still emits its 24 trace events; unarmed prints correct output. ⛔ **NOT AN RTX ASM PORT — pure C, no family gate, no kill-switch arm exists to toggle it, and none is claimed.** (The s225 fabricated-gate lesson: name the gates you did NOT run.)

**GATES:** watermark HELD EXACTLY (§0), all three fail sets byte-identical · RTX unit **ALL PASS 8426/0** · store-width **GATE PASS** · zero templates ⇒ no `.s` regen owed, verified not inherited.

⛔ **NO SPEED NUMBER CLAIMED.** The 3-arm rail still refuses on this machine (s224 hugepage bimodality) and that rung is still unfixed. Min-of-5 wall clock recorded as an **OBSERVATION ONLY, NOT A RESULT**: `string_pattern` 1636 ms, `pattern_bt_deep` 1650 ms. No board may quote these.

---

## 5. ⚠⚠ NEW, AND IT TOUCHES THE PROJECT'S MANDATED DEBUGGING INSTRUMENT: THE MONITOR IS BLIND TO GVA-SLOTTED VARIABLES

While proving the guard did not break tracing, `SCRIP_DEBUG_TRACE=1` on a two-line program (`X = 'alpha'; X = 'beta'`) emitted **24 trace events and ZERO for `X`.**

**NOT CAUSED BY THIS CHANGE — PROVEN WITHOUT A REBUILD:** `NV_SET_fn` records **25 entries (startup only)** on that program, and `--compile` shows the store going through `rt_gva_island` + `__gva_names`. **`X`'s assignment never reaches `NV_SET_fn`, so `comm_var` was never called for it, before or after.**

⚠⚠ **CONSEQUENCE: `comm_var` is what feeds `mon_send("VALUE", …)`. RULES.md makes the 2-way IPC sync-step MONITOR the MANDATORY first instrument for every divergence — and that monitor cannot see any variable the emitter resolved to a GVA slot.** The optimisation that made 14 of 20 benchmarks fast is the same one that made them invisible to the debugger. **This is not hypothetical: a monitor DIVERGE table that never names the variable actually carrying the wrong value sends the bracket hunt to the wrong statement.**

⇒ **OWED RUNG (NEW, and it outranks a port): give the GVA slot store path a monitor feed, or make the monitor read slots directly.** Until then, **do not read a clean monitor trace as evidence a variable is correct** — it may simply be unobservable. Scope with Lon; it touches the emitter, so it is NOT concurrency-safe with the ζ ladder.

---

## 6. NEXT RUNG

1. ⭐⭐ **The rail's min-of-N / hugepage mode.** Still blocks every speed claim on this machine; s224 named it, s225/s226/s227 all deferred it, and this session could not quote a number either. **It now outranks every port for the fourth consecutive session.**
2. ⭐⭐ **§5's monitor blindness** — it degrades the instrument RULES.md mandates for all bug-finding.
3. ⭐⭐ **Extend GVA-style compile-time slot binding to the pattern/EVAL assignment path** (the six hot programs). This is the real `asg01` equivalence and it DELETES the remaining `NV_SET_fn` traffic rather than accelerating it. ⛔ Touches LOWER + emitter ⇒ **NOT concurrency-safe while the ζ ladder holds 41 red pattern programs.** Lon's routing.
4. `rt_sxt_break` — 20.7M calls on a 2-instruction body, same shape as `comm_var` but the inline needs `g_sxt_fr` promoted `static`→`hidden` across three files (a widening, safe on the m4 axis per ARCH §7 0(c)).
5. Re-run the FIXED whole-surface census and rebuild the port queue from it; **the pre-fix ranking is void.**
6. `util_rtx_count_syms.sh`'s `rt_dcap_lazy_init` segfault is recorded as OPEN in the ladder but the script's own header says it was **FIXED at s221** — reconcile the rung text with the tree (the ARCH §7 step 0 "strike dead names in the same commit" clause, applied to a rung's premise rather than a symbol).

**`handoff_status.sh` is the push truth — NOT this block.**
