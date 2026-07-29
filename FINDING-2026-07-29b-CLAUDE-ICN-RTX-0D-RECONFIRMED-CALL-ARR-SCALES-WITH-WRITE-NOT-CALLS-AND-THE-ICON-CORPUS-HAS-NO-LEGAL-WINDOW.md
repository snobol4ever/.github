# FINDING-2026-07-29b-CLAUDE-ICN-RTX-0D-RECONFIRMED — `rt_call_arr` SCALES WITH `write`, NOT WITH CALLS; AND THE ICON BENCHMARK CORPUS HAS NO LEGAL WINDOW ANYWHERE

**Session:** s210-ICN · **Rung:** RTX-0d-ICN (re-measurement) + RTX-0b-ICN (blocker characterised)
**Landed:** measurement only, NO asm, NO source edits to `src/`.
**Gate:** Icon watermark re-derived fresh BEFORE any work: **PASS=252 FAIL=11 XFAIL=30 TOTAL=293** — exact
match to `GOAL-ICON-BB.md` s202. Nothing was edited, so nothing was re-gated after.

---

## ⛔⛔ PROCESS FAILURE FIRST — I DUPLICATED A LANDED RUNG

**RTX-0d-ICN was already closed at s203-ICN**
(`FINDING-2026-07-29-CLAUDE-ICN-RTX-0D-STATIC-RANK-IS-WRONG-AND-THE-TOP-THREE-ARE-COLD.md`).
I rebuilt the interposer and re-measured it from scratch before reading that file.

**Root cause:** `GOAL-ICON-RTX.md`'s LIVE CURSOR still reads *"NEXT: RTX-0b-ICN → RTX-0d-ICN on
`rt_call_arr` — the measurement that decides…"*, and the PHASE-0 ladder still shows
`- [ ] RTX-0d-ICN`. **The cursor and the checkbox were never moved when the finding landed.** I followed
the cursor and it pointed at finished work.

⭐ **THIS IS STEP 0(e) WEARING A NEW COSTUME.** 0(e) says *confirm the symbol is not already assembly*.
The same failure exists one level up: **confirm the RUNG is not already measured.** The check is free and
it is a grep:

```bash
grep -l "Rung:.*RTX-0d-ICN" FINDING-*.md      # before opening any rung
```

⇒ **PROPOSED STEP 0(h), for `ARCH-ICON-RTX.md` §8:** before opening a rung, grep the FINDING set for the
rung name. A `- [ ]` in the ladder is NOT evidence the rung is open — the ladder is hand-maintained and
was measured stale here. **The FINDING set is the truth; the checkbox is a claim.**

---

## ⭐⭐ THE FINDING — THE MECHANISM UNDER `rt_call_arr`'s ICON SCALING IS `write`, AND IT IS 1:1

s203-ICN measured `rt_call_arr` at 134 (queens N=6) → 1,822 (queens N=8), concluded **"it SCALES 13.6× …
it is genuinely executed in the window … the two languages reach it differently"**, and on that basis
distinguished Icon from SNOBOL4's flat-8 s188 result. **The scaling is real. The attribution was not
tested.** It is not procedure dispatch.

**MEASURED, mode 3, LD_PRELOAD interposer, two counts each:**

| workload | shape | N | 4×N | verdict |
|---|---|---:|---:|---|
| `up` | user proc, `return` (determinate) | **1** | **1** | **FLAT — bypasses the symbol** |
| `gen` | user proc, `suspend` (generator) | **1** | **1** | **FLAT — bypasses the symbol** |
| `bi` | builtin `find()` in the hot loop | **1** | **1** | **FLAT — resolved at emit time (BID)** |
| `wr` | `write()` in the loop | **500** | **2000** | ⭐ **1:1 EXACT** |

The single call in the first three rows **is** the trailing `write()`. Loop bodies of 200,000 and 800,000
iterations move it by zero. Denominator scaling confirms the workload really grew: total cycles
91.8M→210.1M (`bi`) and 14.8M→45.9M (`up`) while `rt_call_arr` held ~100–155k cycles and exactly 1 call.

⇒ **For Icon, `rt_call_arr` is the BY-NAME BUILTIN INVOCATION path, and on every measured board it is
dominated by `write`.** queens' count tracks its printed output, not its recursion. **Neither
determinate nor generator user-procedure calls reach it at all in mode 3.**

**CROSS-VALIDATION AGAINST THE LANDED BOARD (the reason to trust this instrument):** independently
rebuilt, my `deal` count is **126 — identical to s203-ICN's 126**; queens default N=6 gives **128 vs
their 134** (they drove mode-4 linked binaries with `-n` args; mode 3 cannot take program args, see
below). Two instruments, two sessions, same numbers.

### What this changes

1. **ICON-RTX's decision to drop the `rt_call_arr` claim was RIGHT, and now rests on a stronger reason.**
   Not merely *"1,822 is smaller than 15,871"* — but *"the traffic is `write`, so an asm port buys a
   faster by-name lookup in front of an I/O call whose cost is inside libc."* Ruling 2 (keep libc) caps
   the win at the `-O0` dispatch ceremony. **Recorded as beneficiary; claim stays closed.**
2. **It sharpens RTX-4-ICN (I/O).** s203-ICN measured `rt_write_any_nl` (static rank 3, 566 sites) at
   **ZERO** on queens/deal — yet queens demonstrably writes 30 lines through `rt_call_arr`. **The live
   write path is therefore NOT `rt_write_any_nl`.** Static rank 3 is confirmed dead, and RTX-4-ICN as
   written targets the wrong symbol. **Find the real callee before opening that rung.**
3. ⭐ **STEP 0(g) GENERALISES FROM ARMS TO CALL SHAPES.** 0(g) (s209b) says *identify which ARM the
   emitted code takes.* This board shows the same trap one level out: **four call SHAPES, one symbol,
   and three of the four never arrive.** A count aggregated over a mixed workload hides which shape paid
   for it. **Attribute the traffic, not just the total.**

---

## ⛔⛔ SECOND FINDING — RTX-0b-ICN IS NOT "WRITE FAMSETS". THE CORPUS HAS NO TIMEABLE PROGRAM.

RTX-1-ICN reported `BOGUS-WINDOW` (16–20 ms vs `MIN_MS=800`) and called RTX-0b *"blocking twice over."*
**Measured: this is corpus-wide, not incidental.** Wall clock, mode 3, whole process:

| micsum | deal | queens | geddump | ipxref | rsg | tgrlink | concord |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 6 ms | 13 ms | 13 ms | 17 ms | 21 ms | 21 ms | 21 ms | 30 ms |

**Every Icon benchmark is 27×–133× below the floor. Not one legal window exists in `benchmarks/icon/`.**
`micro` aborts (rc=134); `options`/`post`/`shuffle` are the known pre-existing compile errors.

**AND THE OBVIOUS FIX IS BLOCKED:** `scrip --run prog.icn -n8` reports `scrip: cannot open '-n8'` — **the
mode-3 driver does not forward program arguments**, so the corpus's own scaling knobs are unreachable.
(s203-ICN drove mode-4 linked binaries, which is why it could scale queens at all.) queens additionally
routes its `-n` through `options()`, itself a pre-existing compile error.

⇒ **RTX-0b-ICN's real content is: (a) decide whether mode 3 forwards argv or Icon famsets carry N
internally, and (b) author scaled workloads, because none exist.** Until then **this ladder can measure
COUNTS (which need only scaling) but cannot measure TIME (which needs a legal window)** — exactly the
half-rung state RTX-1-ICN landed in. **RTX-1b-ICN's +12.11% is the sole timed result on the board and it
got there on a hand-written 4M-store workload, not on the corpus.**

---

## INSTRUMENT — `tools/rtx_icn_interpose.c` (NEW, tools/ only, links nothing)

`LD_PRELOAD` counter + inclusive-`rdtsc` share for `rt_call_arr` · `rt_call_arr_gen` · `rt_arg_stage` ·
`rt_call_proc_descr`, plus `rt_assign_var` as the **positive control**.

**Why it reaches mode-3 emitted code:** `bb_call.cpp:291` takes `&rt_call_arr` inside `libscrip_rt.so`
(`-fPIC`) and bakes the address into the blob. Address-of an exported global in a shared object resolves
through the GOT at load time, so a preloaded definition wins. **The blob calls the interposer.**

**POSITIVE CONTROL PASSED BEFORE ANY NUMBER WAS READ (s201):** `rt_assign_var` — 1000 calls at N=1000,
**4000 at N=4000, exact 1:1 at 4×.** Counting and scaling both proven on a symbol RTX-1b independently
showed hot. Without it, every zero in this document would be uninformative.

⚠ **TWO NEAR-MISSES, RECORDED BECAUSE THE TAXONOMY IS ONLY USEFUL WITH THE NEAR-MISSES IN IT:**
1. **I first modelled `rt_arg_stage` as `(void*, long)` from its call sites.** It is
   **`void rt_arg_stage(int idx, DESCR_t v)`** — descriptor **BY VALUE**, a register pair (`rsi:rdx`).
   The wrong signature **compiles clean and corrupts the ABI silently.** Caught by reading `rt.c:603`.
   ⇒ **an interposer signature is step 0(a)/0(b) territory: read the definition, never infer it.**
2. **My first positive control produced 0 calls and 0 output** — a parse error, not a null. Had I trusted
   it I would have recorded `rt_call_arr` COLD from a program that never ran. **A null from an
   unvalidated instrument is not evidence.**

⚠ **INCLUSIVE, NOT SELF.** The share covers everything the symbol reaches. The portable-fraction split
(dispatch prologue vs. callee) remains **UNMEASURED** — inbox gap #1 is still open.

---

## STATE — NOTHING PORTED, NOTHING CLAIMED, NOTHING TO REBASE

No `src/` edit, no gate, no `.s` regen, no ledger row moved. `RTX-CLAIMS.md` is unchanged and correct.
New file is `tools/rtx_icn_interpose.c` only.

**RECOMMENDED NEXT — and it is a re-rank, not a port.** The dynamic board that ranked
`rt_assign_var` #1 was taken **before RTX-1b-ICN ported it.** `rt_deref` and `to_int` sat above it and
are already asm. ⇒ **the hottest UNPORTED C symbol on Icon's board is now unknown.** Re-run the dynamic
rank post-RTX-1b — over C-function *counts*, not static sites — and let the measurement pick RTX-2-ICN.
**Do not open RTX-2-ICN on `rt_arg_stage`: the ledger already carries it `BLOCKED:MEASURED-ZERO`, and
s203-ICN measured it 0/0/0.**

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
