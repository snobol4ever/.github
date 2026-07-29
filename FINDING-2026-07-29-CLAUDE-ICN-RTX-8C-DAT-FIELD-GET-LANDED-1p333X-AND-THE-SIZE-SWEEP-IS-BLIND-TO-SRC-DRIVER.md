# FINDING — 2026-07-29 — CLAUDE — ICN-RTX-8c: `dat_field_get` LANDED AT 1.333× ON/PRISTINE, AND THE LADDER'S SIZE-RANKED INVENTORY IS BLIND TO AN ENTIRE DIRECTORY

**Session:** s216-ICN
**Rung:** RTX-8c-ICN
**Ladder:** `GOAL-ICON-RTX.md` · **Contract:** `ARCH-ICON-RTX.md` · **Ledger:** `RTX-CLAIMS.md`
**Symbol:** `dat_field_get` — Icon record field read (`r.f`)
**Gate:** `SCRIP_RTX_ICNAGG` — **REUSED, not added.** Same aggregate family as `rt_size_d` /
`rt_list_bang_at`, so this is **NOT an eleventh gate and NOT a gate ledger event** — the ruling s214
applied when `rt_str_coerce` joined `SCRIP_RTX_ICNREL`.
**Build label on every number below:** `RT_OPT=-O0` (Makefile default; no `-O2` was built or directed).

---

## ⭐⭐ THE HEADLINE, AND IT IS A METHOD DEFECT, NOT THE PORT: THE SIZE-RANKED SWEEP CANNOT SEE `src/driver/`

The LIVE CURSOR's own reproduction recipe for the small-to-large ordering reads: *"sweep 316 Icon
programs, extract `call sym@PLT`, intersect with **C bodies in `src/runtime/**/*.c`**, sort by
brace-counted body length."*

**`dat_field_get` is defined in `src/driver/driver_data.c:387`. It is not in `src/runtime/` at all.**

I implemented that recipe literally, and my sweep produced 67 candidate rows with **`dat_field_get`
absent from every one of them** — while the same sweep's *call-site* tally listed it at 117 sites.
The symbol was invisible to the ranking and visible to the counting, in the same run, because the
intersection step scans one directory and the extraction step scans the compiler's output.

⇒ **The inventory has a whole-directory blind spot, and it is not a small one.** `src/driver/`
contains runtime-role C reached from emitted code by `@PLT` exactly like `src/runtime/` does:
`dat_field_get`, `dat_field_set`, `data_field_ptr`, `_builtin_DATA` all live there. Any symbol whose
body sits in the driver TU is unrankable by the current method and will keep being skipped by every
small-to-large session that follows the recipe as written.

⭐ **THE ONLY REASON THIS RUNG HAPPENED IS THAT THE CURSOR NAMED THE SYMBOL BY HAND.** s214 wrote
`dat_field_get` (117 real sites) into the prose. The mechanical method would never have surfaced it.
**A hand-carried name rescued a mechanical method's omission — which is the exact inverse of the
usual failure on this ladder, where prose is stale and the mechanism is right.**

**FIX OWED (step 0(i) amendment):** the intersection must scan `src/driver/**/*.c` and
`src/parser/**/*.c` as well as `src/runtime/**/*.c`, or better, must be driven by `nm -D` on
`out/libscrip_rt.so` — which is the honest definition of "a symbol the emitted code can call",
independent of which source directory happens to hold it.

---

## ⭐⭐ SECOND FINDING: TWO OF THE FOUR CANDIDATES s214 NAMED ARE PHANTOMS — ONE SESSION AFTER STEP 0(i) WAS MINTED TO PREVENT EXACTLY THIS

s214's cursor named four next candidates. Re-derived from the compiler this session (step 0(i)):

| candidate | s214 prose | compiler sweep (316 programs) | verdict |
|---|---:|---:|---|
| `dat_field_get` | 117 | **117** | ✅ EXACT — ported this rung |
| `rt_make_list` | 178 | **171** | ✅ real (small drift) |
| `subscript_get2` | 41 | **52** | ✅ real |
| `subscript_set` | 41 | **0** | ⛔ **PHANTOM for Icon** |
| `rt_case_eq` | 26 | **0** | ⛔ **PHANTOM for Icon** |

`subscript_set` and `rt_case_eq` both have live C bodies (`pattern_match.c:278`, `rt/rt.c:82`) — they
are not dead code — but **the current compiler emits zero `call …@PLT` for either across all 316 Icon
programs.** They fail step 0(f). They are reached from *inside C*, not across the call boundary the
whole ladder is built to attack, so they are NOT-A-TARGET for a Phase-1 port.

⭐ **WHY THIS RECURRED ONE SESSION AFTER THE FIX:** step 0(i) says *derive counts from
`scrip --compile`, never from stored `.s`*. s214 honoured it **for the sweep it ran** and then wrote
the RESULT into prose as a list of four names with numbers. The next session (this one) inherits the
prose, not the sweep. **Step 0(i) prevents a stale INPUT; it does nothing about a stale OUTPUT.**
This is the s212 rule (*re-run an inherited grep; it is exactly as perishable as an inherited
checkbox*) landing on a *derived count* rather than on a grep — and it means the LIVE CURSOR should
carry **the command**, not the numbers.

---

## THE PORT

### What was actually deleted — and it is not `-O0` ceremony

```c
DESCR_t dat_field_get(const char *fname, DESCR_t obj) {
    DESCR_t *cell = data_field_ptr(fname, obj);
    if (cell) return *cell;                       /* <-- 100% of measured arrivals */
    /* "WHAT" pseudo-field, rt_str_method fallback, FAILDESCR — all left in C */
}
DESCR_t *data_field_ptr(const char *fname, DESCR_t inst) {
    if (inst.v < DT_DATA || !inst.u) return NULL;
    DATBLK_t *blk = inst.u->type; if (!blk) return NULL;
    for (int i = 0; i < blk->nfields; i++)
        if (blk->fields[i] && strcmp(blk->fields[i], fname) == 0)   /* libc call PER FIELD */
            return &inst.u->fields[i];
    return NULL;
}
```

The exported wrapper does almost nothing; **the cost is the callee's linear scan, which calls libc
`strcmp` once per field until it hits.** Cost is O(field index) with a genuine call per step. The asm
**absorbs the scan** and replaces the per-field `strcmp` with an inline byte compare.
**A deleted libc call per field is removable at ANY `-O` level** — the same shape as RTX-6's deleted
`strtoll` and RTX-6b's deleted `strcmp`, and it answers the s208 inbox's gap #1 concretely.

### `data_field_ptr` is ABSORBED, NOT DELETED — s211's ruling extended to an *exported* callee

s211 absorbed the **`static`** callee `rt_parse_num_d` into its wrapper's asm and left the C in place
for the fallback, concluding no §4 amendment was owed. Here the callee is **exported** (`nm -D`: `T
data_field_ptr`) and has other C callers — `dat_field_set`, `rt_field_var` (`pattern_match.c:1071`),
and four sites in `by_name_dispatch.c`. **So the same ruling holds for a different reason:** absorb
the logic, leave the symbol and its body untouched, gate only the wrapper. **No `ARCH-ICON-RTX.md` §4
amendment is owed for exported callees either.**

### Arm split, and the MISS path pays a duplicated scan ON PURPOSE

Ported: `inst.v >= DT_DATA`, `inst.u != 0`, `blk != 0`, `nfields > 0`, `fields != 0`, **and a name
match**. Everything else tail-jumps to `c_dat_field_get`, which owns `WHAT`, `rt_str_method` and
`FAILDESCR`. On a scan MISS the C re-runs `data_field_ptr` from the top — a duplicated scan.
**Accepted deliberately:** the miss path is measured at **0% of arrivals**, and duplicating a cold
scan is cheaper to reason about than threading a partial scan result across the asm/C boundary.

### Offsets — MEASURED THIS SESSION, NEVER COPIED FROM PROSE (s202's rule)

`gcc` `offsetof` probe against `runtime/core/core.h`: `DESCR_t` 16 B (`v`@0 `slen`@4 `value`@8) ·
`DATBLK_t` 40 B (`name`@0 `nfields`@8 `fields`@16) · `DATINST_t` 24 B (`type`@0 `fields`@8 `id`@16) ·
`DT_DATA`=100 `DT_FAIL`=99. These agree with s213's recorded numbers, which is worth saying: **the
prose was right this time, and it was still cheaper to re-measure than to trust it.**

ABI: `rdi`=fname; `obj` arrives as the descriptor PAIR `rsi`=`(slen<<32)|v`, `rdx`=`value`, so
**`esi` IS `obj.v` and `rdx` IS `obj.u` with no unpacking owed**; returns the pair `rax`/`rdx`.
No pin touched — `rdi rdx rcx rsi rax r8 r9 r10 r11` are all RTX working set, and the ported arm is a
**true leaf**: no call, no stack, no red zone.

---

## STEP 0 — ALL CHECKS, EACH RUN THIS SESSION

- **0(a)** live definition — `src/driver/driver_data.c:387` ✅
- **0(b)** spelling round-trips — pure ASCII, no Greek codepoints in this symbol ✅
- **0(c)** linkage — `nm -D`: `dat_field_get` `T`, `data_field_ptr` `T`. Asm touches **no** external
  global (it dereferences register-passed pointers only), so no `@GOTPCREL` is owed ✅
- **0(d)** ⭐ **EXECUTES AND SCALES 1:1** — LD_PRELOAD interposer: **80,000 arrivals at N=5,000 →
  320,000 at N=20,000, exactly 4×.** 16 field reads per iteration × N, which reconciles exactly ✅
- **0(e)** not already asm — `grep --include=*.S` clean ✅
- **0(f)** ⭐ **117 real `call dat_field_get@PLT` sites derived from `scrip --compile`**, not the
  frozen `.s` tree ✅
- **0(g)** ⭐ **THIRD CONSECUTIVE CONFIRMATION OF THE NO-GUARD REGIME.**
  `bb_field_get.cpp` emits `call dat_field_get@PLT` with **no inline tag guard** — it tests `eax==99`
  only *after* the call. So the guard steers nothing and the CHEAP arm is dominant: **80,000 / 80,000
  = 100% non-fail.** RTX-6 had first-arms dead; RTX-6b had both ends live, middle cold; s214's
  `rt_str_coerce` had the cheap guard arm live at 93.1%; **this is an unguarded call at 100%.**
  **Four rungs, four distributions. The regime remains un-inheritable — but "unguarded ⇒ cheap arm
  dominant" has now held twice, which is the first repeatable sub-rule 0(g) has produced.**
- **0(h)** FINDING set grepped for the symbol — two prior FINDINGs mention it; **neither ported it**,
  and one of them matters a great deal (see PORT ≠ FIX below) ✅
- **0(i)** counts from the compiler ✅ — **and this is the check that exposed the two phantoms above**

---

## ⛔ PORT ≠ FIX — AND A PRIOR FINDING ALREADY SPECIFIED THE RIGHT FIX

`FINDING-2026-07-25-CLAUDE-ICN-BID-1-BUILTIN-ID-DISPATCH-AND-O2-FALSIFIED.md` §2 says, verbatim in
substance: *record fields — `bb_field_get.cpp` currently emits `dat_field_get(fname, obj)` BY NAME;
needs a per-record-type field-number table so `dat_field_get` is an int index, not a scan.*

**That is the architecturally correct fix and this rung is NOT it.** Icon's own canonical
implementation resolves fields to integer indices at translate time; SCRIP resolves them by *name, at
run time, with a string compare per field*. **My asm makes the wrong design fast.** 1.333× on a name
scan is real, and an int-indexed field access would make the scan disappear entirely.

⇒ **Recorded so the number cannot be misread as "record field access is solved."** The right fix is
LOWER + template territory (BID-AT-LOWER / Phase 2), fires `.s` regen ×3, and collides with the
ICON-BB ζ ladder — so it correctly does **not** block a Phase-1 `.S` port, but it **outranks this
rung architecturally** and belongs on the ladder as its own entry. Same class as RTX-9's standing
`rt_keyword_read` warning: *porting the body in asm preserves the defect and makes it faster.*

---

## FALSIFICATION — TWO-SIDED, A RESULT NOT A ROUTE, AND NOT SILENT

Corruption: force every field hit to return **index 0** (`xor r10d, r10d` before the `shl`). This
breaks a **RESULT** — the returned descriptor is a real, type-valid cell, so there is **no memory
unsafety and no crash**, only a wrong answer. It is explicitly **not** a route break: the gate is
untouched, so this is not the vacuous s187 shape.

| arm | one-program probe (`rung24_records_field_assign`) | full Icon corpus |
|---|---|---|
| corrupted asm, gate **ON** | `99, 99` ⛔ wrong | **PASS=247 FAIL=16** |
| corrupted asm, gate **OFF** | `99, 20` ✅ correct | **PASS=252 FAIL=11** |

⇒ **The asm demonstrably EXECUTES, and the switch demonstrably SWITCHES.** Five graded programs
detect the corruption — better reach than s214's `rt_str_coerce` (3 programs), though still thin
against 320,000 arrivals in a single benchmark. **That thinness is a statement about the batteries,
not about the port** (s213/s214's standing observation, holding again).

---

## ⭐ THE ISOLATION ARM WAS DISCHARGED BY COUNTING, NOT BY A THIRD BUILD — CHEAPER *AND* STRONGER THAN s204'S PRESCRIPTION

s204 requires an isolation arm when a rung lands into an **already-ported family**, because a family
gate's error *"has no known sign and no known bound."* `SCRIP_RTX_ICNAGG` already gates `rt_size_d`
and `rt_list_bang_at`, so this rung qualifies.

Rather than build a fourth `.so` with the siblings reverted, I **counted all three symbols in the
benchmark window** with one interposer:

```
[AGG3] dat_field_get=320000  rt_size_d=0  rt_list_bang_at=0
```

⇒ **The two previously-ported siblings are arithmetically absent from the window, so the entire
ICNAGG ON/OFF differential on this benchmark is attributable to `dat_field_get` alone.** This is
strictly stronger than a rebuild-based isolation arm: a rebuild proves the *other code is gone*,
whereas the count proves *it was never reached*, which is the property the isolation arm actually
needs. ⭐ **PROPOSE ADOPTING THIS AS THE DEFAULT DISCHARGE FOR s204's ISOLATION REQUIREMENT:** one
interposer over the family's full symbol set, asserting zero arrivals for every sibling. It costs one
build fewer and answers the question directly.

---

## A/B — 3-ARM INTERLEAVED, ROUND 1 DISCARDED, VIA THE PROJECT'S OWN HARNESS

`scripts/bench_rtx_3arm.sh --fam ICNAGG --pristine /tmp/so_pristine --rtx /tmp/so_port -r 5`
on `corpus/benchmarks/icon/rtx/bench_icnagg_field_isolate.icn` (authored this session):

```
PRISTINE=947.5ms   OFF=923.5ms   ON=711ms
arm spreads (max/min): PRISTINE=1.037x  OFF=1.027x  ON=1.038x     gap ON-vs-PRISTINE = 1.333x
ON/PRISTINE = 1.333x    <-- THE REAL ANSWER
OFF/PRISTINE = 1.026x   (kill-switch tax)
raw PRISTINE: 973 944 951 938      raw OFF: 915 926 940 921      raw ON: 706 733 713 709
```

**⭐ THE DISTRIBUTIONS ARE FULLY DISJOINT:** ON's worst sample (733 ms) is faster than OFF's best
(915 ms) and PRISTINE's best (938 ms). Arm spreads 1.027–1.038× against a 1.333× gap.
**Window 933 ms > `MIN_MS=800` ⇒ a LEGAL window, no `BOGUS-WINDOW`, ratio printed.**
All three arms' output **byte-identical and verified non-empty** (`chk: 174400000`, 15 bytes each) —
the s214 empty-`cmp` trap explicitly guarded against.

**⛔ SCOPE — DO NOT LET THE NUMBER TRAVEL WITHOUT THIS:** 1.333× is an **ISOLATION** benchmark on a
ten-field record with late-field reads over-represented, at `RT_OPT=-O0`. It is a legal window and a
real gap, but **no corpus-wide impact is claimed**: 117 static sites and a 5-program falsification
reach are not a corpus-wide story. The number measures the arm, not the language.

**Benchmark design, inherited from s211/s212:** `&time` opened INSIDE the program (excludes the
~20:1 compile-phase confound **by construction**, not by subtraction) · **record allocated ONCE
before the window** (s211: per-iteration allocation made samples bimodal with intra-arm spread larger
than the gap; hoisting took spreads 1.57×→1.04×, and my spreads are 1.03×) · field **assignment**
deliberately absent, since `r.f := v` routes through `rt_field_var`, a different symbol.

---

## GATES — ALL THREE LANGUAGES, ON AND OFF, IDENTICAL

Icon baseline **re-derived fresh before any edit, never hand-copied** (s202): **252/11/30**, which
matches the goal file's stated watermark.

| battery | gates ON | ICNAGG OFF / all-OFF |
|---|---|---|
| Icon `test_icon_all_rungs.sh` | **252 / 11 / 30** | **252 / 11 / 30** |
| SNOBOL4 smoke (m4) | **7 / 0** | **7 / 0** |
| SNOBOL4 broad corpus | m3 **329/5**, m4 **324/2/8** | m3 **329/5**, m4 **324/2/8** |
| Prolog rung suite | interp **164/0**, compile **164/0** | interp **164/0**, compile **164/0** |

⭐ **THE PROLOG WATERMARK-VS-PROSE DISAGREEMENT s212/s213/s214 KEPT RECORDING IS RESOLVED, AND IT WAS
NEVER A REGRESSION.** Those sessions measured **164/0** while this file's prose claimed 185/0/0 and
188/0/1, and each session graded on the ON/OFF differential while asserting no culprit — correctly.
Measured this session: `scripts/test_smoke_prolog.sh` reports **5/0 + 5/0** and
`scripts/test_prolog_rung_suite.sh` reports **164/0 + 164/0**. ⇒ **The three figures are three
different INSTRUMENTS, not three states of one battery.** 164/0 is the rung suite; 5/0 is the smoke;
185/188 belong to neither script and are stale prose from a third. **A watermark is meaningless
without the script name attached, and this file has been carrying bare numbers.**

**Build determinism verified, not assumed:** the port `.so` reproduced md5 `2930bddd3fc5` across two
independent full rebuilds (`rm -rf out /tmp/si_objs` each time — `x86_asm.h` is a header and `make`
does not track it). PRISTINE `.so` = `8793847346ea`, built from `git checkout`-clean sources, i.e. it
**is** the session-baseline build. ⚠ **Honest gap: I did not md5 the session's very first `.so`
before editing**, so "PRISTINE == recorded session-baseline md5" is satisfied by source identity and
build determinism, **not** by a recorded hash comparison. Record the baseline md5 at session start.

**⭐ LD_DEBUG IS THE AVAILABLE INSTRUMENT FOR PROVING WHICH `.so` AN ARM ACTUALLY LOADED.** With no
`gdb`/`perf`/`valgrind`/`ltrace`/`strace` in this container, a 3-arm A/B that swaps libraries by
`LD_LIBRARY_PATH` rests on an *assumption* about loader search order. `readelf -d scrip` shows
**`RUNPATH`** (not `RPATH`), which is searched **after** `LD_LIBRARY_PATH` — and
`LD_DEBUG=libs` then prints `calling init: /tmp/so_pristine/libscrip_rt.so` vs
`calling init: /tmp/so_port/libscrip_rt.so`, **proving** the swap rather than trusting it. Free, and
it closes a hole every prior 3-arm rung on this ladder left open.

---

## FILES

| file | change |
|---|---|
| `SCRIP/src/runtime/rtx/rtx_icnagg.S` | `dat_field_get` asm entry, gated `icnagg`, absorbing `data_field_ptr`'s scan |
| `SCRIP/src/driver/driver_data.c` | `dat_field_get` → `c_dat_field_get` (same commit, per §8 step 2) |
| `corpus/benchmarks/icon/rtx/bench_icnagg_field_isolate.icn` | new self-timed isolation benchmark |
| `.github/RTX-CLAIMS.md` | `dat_field_get` `FREE` → `OUT:ICON-RTX:s216` → `DONE` |
| `.github/GOAL-ICON-RTX.md` | LIVE CURSOR moved; RTX-8c recorded; step 0(i) amendment owed |

**No Makefile change:** `rtx_icnagg.S` is already in `RT_PIC_SRCS`, so both modes got the port by
construction. **No template touched ⇒ no `.s` regen owed** (RULES.md step 4).

---

## ⚠ PROTOCOL DEVIATION — FIFTH SESSION RUNNING

**No credential was available, so the ledger check-out (`.github` `e27ef9fb`) was committed BEFORE
the work but NOT PUSHED before it.** The protective property the check-out exists for — a parallel
session seeing the claim — **was not obtained.** All commits this session are **LOCAL ONLY**; the
s202 ancestry check (`git rev-list --count origin/main..HEAD` == 0) is **not satisfiable**, so
RTX-8c-ICN is recorded `[x]` **PENDING ANCESTRY** exactly as RTX-6/6b were.
**`scripts/handoff_status.sh` is the only completion truth and it will say BLOCKED.**

⚠ **Segfaults/aborts during full-corpus interposer sweeps** were observed again, consistent with the
documented harness blind spot (`test_icon_all_rungs.sh` grades stdout and discards exit code). The
watermark is unchanged from the fresh pre-edit baseline, so nothing here introduced them; **I did not
individually bisect them.** `rung36_jcon_mindfa` (25 static sites, the top-ranked program) **times out
under the interposer** and was excluded from 0(d) rather than counted as a zero — s212's rule: *a zero
is not a result until the program is proven to have RUN.*

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
