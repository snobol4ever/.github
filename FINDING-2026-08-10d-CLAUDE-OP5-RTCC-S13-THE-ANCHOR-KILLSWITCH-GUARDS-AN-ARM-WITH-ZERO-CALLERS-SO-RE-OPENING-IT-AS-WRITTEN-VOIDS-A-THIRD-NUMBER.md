# FINDING — 2026-08-10 s13 (Opus 5) — RTCC RC-5-ANCHOR: THE KILLSWITCH GUARDS AN ARM WITH ZERO CALLERS, SO THE PLAN'S OWN "RE-OPEN THE ANCHOR REVERT" WOULD PRODUCE TWO IDENTICAL BINARIES FOR THE THIRD TIME

**Session class:** RC-0 (orientation + watermark + census). ZERO emitter bytes, ZERO source edits, no regen owed.
**Tree at open:** SCRIP `bce9a4b0` · corpus `bea31de0` · `.github` `37e0273c` — all three CLEAN, zero unpushed, HEAD == origin/main.

---

## 0. THE s11/s12 "STRANDED" BANNER IS DISCHARGED — NOTHING IS OWED

GOAL-RTCC.md's LIVE CURSOR closes with **"PUSH REQUIRED — credential needed... until it lands, s11's work is STILL stranded and s12's is stranded with it."** Measured at this session's open, on a fresh clone from origin:

```
SCRIP    HEAD=bce9a4b0  origin/main=bce9a4b0  unpushed=0  porcelain=clean
corpus   HEAD=bea31de0  origin/main=bea31de0  unpushed=0  porcelain=clean
.github  HEAD=37e0273c  origin/main=37e0273c  unpushed=0  porcelain=clean
```

All four s11 SCRIP commits (`9f451e55` `405009cd` `de2f9920` `5962917e`), the five-constant fix (`502dbb2d`), and s12's `.github` recovery are present at origin and are ancestors of HEAD. **The banner is stale in the project's favour.** It is an instance of the STALE-ORIENTATION (a) rule the project already owns — *never write push status into a doc* — reproduced verbatim one session after the law was restated. The cursor edit below removes it.

## 1. WATERMARK RE-PROVED AT OPEN (fresh container, plain `make`, RT_OPT=-O0)

- claim-gate `test_gate_rtcc_claimed_regs.sh --strict` → **PASS**, `COLLISION CLASS: EMPTY`, `HAZARD SURFACE : 19` — identical to s11 and s12.
- `fibonacci.sno` m3 `result: 832040` at **SCRIP_RTCC=0 (509 ms)** and **SCRIP_RTCC=1 (555 ms)**. (Timings are NOT a rail claim — single runs, and this box cannot resolve below ~1.12x.)
- Build note, inherited and confirmed: this box is **1 core**; `install_system_packages.sh` is required first (bison/flex/nasm absent in a fresh container). Launch builds under `setsid` — a tool timeout killing the process group cost s11 a build.

## 2. ⛔ THE FINDING — `RTCC_GLOBAL_R8_ANCHOR` IS A DECORATIVE KILLSWITCH

The plan's PLAN SCRUTINY item **#1** and the s9/s11 cursors all instruct: *"RE-OPEN the ANCHOR revert (`f1fddf55` was decided on two identical binaries)"*, on the strength of s11's ⭐⭐ result *"THE KILLSWITCH SWITCHES ARMS FOR THE FIRST TIME — RC-5 IS GENUINELY A/B-ABLE NOW."*

**That result was measured on GVA, and it does not transfer to ANCHOR.**

### 2a. Value history — the define was never off
`git log -S` over both headers returns exactly two commits. `RTCC_GLOBAL_R8_ANCHOR` was **born as `1` in `f1fddf55` (2026-08-09) and has never held another value**; `502dbb2d` only added the `#ifndef` guard. So the rung was never disabled *by its killswitch*.

### 2b. The revert was executed at the CALL SITES, not the killswitch
`rtcc_anchor_cmp` has **zero callers**. The only occurrence outside the encoder body is `rtcc.h:43`, a comment that states it outright:

> `RC-5 rung 1: R8 = rt_anchor_g (&ANCHOR value, int64_t).  REVERTED 1.000x rail (anchor retry path too cold).`
> `Infrastructure COMMITTED (block-canonical write companions in keywords.c / core.c; encoder arm wired).`
> `Template changes (bb_match_begin/bb_match_advance rtcc_anchor_cmp) REVERTED.`

`bb_match_begin.cpp:82` still emits the original GOT-deref directly via `x86("mov","rcx","[rip@got + __]", …, "rt_anchor_g")`. **The encoder arm is unreachable code guarded by a live killswitch.**

### 2c. PROBE — falsified by measurement, with a positive control (BY CONSTRUCTION IS A HYPOTHESIS UNTIL A PROBE KILLS THE ARM)
Emitted mode-4 asm for `roman.sno` at the **maximum-ON** configuration (killswitch compiled `=1`, `SCRIP_RTCC=1`):

| grep | RTCC=0 | RTCC=1 |
|---|---|---|
| `test r8, r8` (ANCHOR **ON** form) | **0** | **0** |
| `rt_anchor_g@GOTPCREL` (ANCHOR **OFF** form) | 4 | 4 |
| `[r9 +` (GVA **ON** form — POSITIVE CONTROL) | 0 | **106** |
| md5 / lines | `38755f91…` / 2383 | `1f86b190…` / 3825 |

**The positive control is the load-bearing half.** In the *same* emission, the GVA rung fires **106 times** — reproducing s10's recorded static census for roman (*"roman 106 sites / 424 B"*) **to the site** — while ANCHOR fires **zero**. The instrument is therefore proven capable of seeing an RC-5 assignment, so the ANCHOR null is a real null and not an instrument failure. This is the s11 `LD_AUDIT` lesson applied prospectively: *check the census against a quantity you already know* before trusting it.

### 2d. ⇒ THE CONSEQUENCE, AND IT IS A TRAP IN THE PATH OF THE NEXT ACTION
Flipping `-DRTCC_GLOBAL_R8_ANCHOR=0/1` changes **nothing** in the emitted bytes, because the arm it guards has no callers. **Executing PLAN SCRUTINY #1 as written — flip the killswitch, A/B it on the rail — would produce two identical binaries for the THIRD time**, which is the precise failure that voided the number in the first place (s9) and voided its correction (s10/s11). The "genuinely A/B-able now" conclusion is TRUE for GVA (116 sites vs 0, s11-measured) and FALSE for ANCHOR (0 vs 0, measured here).

**To genuinely re-open ANCHOR, restore the REVERTED HALF: the template call sites in `bb_match_begin.cpp` (and `bb_match_advance`).** The killswitch, the encoder arm, and the block-canonical write companions in `keywords.c`/`core.c` are all already committed and are NOT the missing piece. Until the call sites exist, the ANCHOR killswitch is a no-op and any number taken across it is void by construction.

## 3. ⭐ SECOND FINDING — "RC-5 HAS ZERO DYNAMIC DELTA" WAS MINTED FROM GVA AND OVER-GENERALIZED

s9/s10's law reads: *"`[r9+16]` vs `[abs32]` is the SAME load… **Zero dynamic instruction delta**; the only channel is I-cache footprint ⇒ grade RC-5 by STATIC ENCODING DELTA, never the rail."* That is correct **for GVA** and was derived entirely from GVA's mechanism. **ANCHOR's mechanism is a different shape:**

| | instructions | bytes (BINARY) | memory access |
|---|---|---|---|
| ANCHOR **OFF** | 3 — `movabs r11,addr` · `mov rax,[r11]` · `cmp rax,0` | 17 | one dependent load |
| ANCHOR **ON** | 1 — `test r8,r8` | 3 | **none** |

ANCHOR removes **2 instructions and a dependent memory load per site** — 14 bytes, versus GVA's 4. It therefore *does* have a real dynamic delta and is gradeable in principle, exactly as RC-6 is. **The blanket "RC-5 is never gradeable by wall clock" should be narrowed to the rungs whose mechanism is encoding-only.** Sorting RC-5 candidates by mechanism *shape* (encoding-only vs instruction/load-removing) is a free, noise-free discriminator that no rung has applied.

## 4. ⚠ THE REVERT REASON ITSELF HAS NEVER BEEN MEASURED
`rtcc.h` records the revert rationale as **"anchor retry path too cold."** That is a **hotness claim**, and the number beside it (1.000x) is void. Note the static census: **4 anchor sites in roman vs 106 GVA sites** — ANCHOR is thin *statically*, which is precisely the signal this project has now convicted **four separate times** as ANTI-correlated with hotness (*"hot code is loop-resident and needs ONE call site"*). The 4 sites sit inside `bb_match_begin`, which executes once per pattern-match statement execution; `roman.sno` calls `ROMAN()` ~400,000 times for `'1776'` with 2 matches per call.

⛔ **State this as a hypothesis, not a result: I did not measure it.** `LD_AUDIT` cannot — the anchor read is an inline load in generated code, not a PLT crossing, so `util_rtcc_crossing_audit.c` is structurally blind to it (same class as the mode-3 blindness s11 caught). A cheap honest instrument would be a gdb breakpoint at the emitted site with an ignore-count, or a counter in the C fallback path. **The revert may well be correct on the merits — but it currently rests on a void number and an unmeasured adjective.**

## 5. RECOMMENDED NEXT
1. **Do NOT A/B the ANCHOR killswitch.** It cannot switch arms. Either restore the template call sites first, or close RC-5-ANCHOR as *"reverted, correctly or not, and not re-openable without redoing the reverted half."* ⛔ **LON'S CALL** — the restoration is real template work in `bb_match_begin.cpp`, not a flag flip, and it lands in files the WREG/PASSTHRU seat is actively editing.
2. If restored, grade it by **static delta (14 B/site × sites) plus a measured execution count of `bb_match_begin`** — never this box's rail (floor ~1.12x).
3. Carry forward unchanged: RC-6 still needs Lon's **STATED WORKLOAD MIX**, and RC-0(a)'s ≤1.05x exit criterion is still unmet on this hardware.

## 6. LAWS MINTED
- **A KILLSWITCH IS NOT A GATE UNTIL SOMETHING CALLS THE ARM IT GUARDS.** A `#define` that is live, guarded, `-D`-overridable and correct can still be decorative if the arm has no callers. Before A/B-ing any killswitch, **grep its arm for call sites and confirm the ON form appears in emitted output** — the encoder arm existing is not the arm firing. Three RC-5 numbers have now been voided by three *different* mechanisms of the same class: same binary (s9), noise below floor (s10/s11), and now unreachable arm (s13).
- **A POSITIVE CONTROL IN THE SAME EMISSION IS THE CHEAPEST GUARD AGAINST A NULL RESULT.** GVA firing 106 times in the identical `.s` is what converts "ANCHOR greps to zero" from an ambiguous null into a measurement. Any census reporting a zero should name the non-zero it measured alongside it.
- **A MECHANISM-DERIVED LAW INHERITS THE MECHANISM'S SCOPE.** "Zero dynamic delta" was true of GVA's mechanism and was carried across the whole rung; ANCHOR's mechanism removes an instruction and a load. Attach mechanism laws to the mechanism, not to the rung number.
