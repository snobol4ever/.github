# FINDING — 2026-08-10 — Claude Opus 5 — RTCC RC-5: THE GVA RAIL NUMBER IS VOID (the OFF arm was never OFF), THE KILLSWITCH IS DEFINED TWICE, AND MY OWN FIX PRODUCED A SPLIT BUILD

**Session:** s9 (Opus 5). **SCRIP HEAD at open and close:** `c7e085fd`. **Net code change: ZERO** — tree verified clean at close; the one edit attempted was probed, FALSIFIED, and reverted. Scripts/docs class, CONCURRENCY-SAFE (RC-0 class).

---

## 0. WHAT WAS RE-PROVED GREEN AT OPEN

- `scripts/test_gate_rtcc_claimed_regs.sh --strict` → **PASS** at `c7e085fd`. s8's "collision class empty" holds one commit later. Hazard surface 19 sites / 8 files; GVARQ readers 6 files; intersection empty.
- Build green from scratch (`-O0`, RULES.md O2-DIRECTED-ONLY honoured). `scrip` + `libscrip_rt.so` both modes smoke-clean.

### 0a. NEW SCREEN — the 19 arg-staging sites are clean of the s8 CORRECTED LAW's fatal shape
s8's corrected law: the hardening protects ARG-STAGING clobbers but does NOT rescue a site that carries a value **across** a crossing. The claim-gate cannot see that shape — its collision class is `writes r9 ∧ reads GVARQ`, which is a different predicate. Screened all 8 writer files for `W → C → R` (write r9, emit call, re-read r9) by textual order within the `+`-chain, comments stripped: **all 8 clean.** Every r9 write is `lea r9, FRQ(..)` immediately before a call — r9 doing its SysV arg-5 job. This independently corroborates s8's claim that the remaining 19 are all arg-staging. **Recommend folding this as a second check into the claim gate** (see §6).

---

## 1. HEADLINE — THE RC-5-GVA RAIL NUMBER (1.036x / 1.028x) IS VOID, NOT MERELY STALE

The cursor carried this as *"NOT RE-PROVED on current HEAD — re-prove with min-of-N before claiming."* That framing is too generous. The number cannot be re-proved on any HEAD, because **the two arms of the s5 A/B were the same configuration.**

`FINDING-2026-08-09-...-RC5-GVA-R9-GVA-BASE-LANDED.md` §"Rail" states: *both arms `SCRIP_RTCC=1`; two binaries: `RTCC_GLOBAL_R9_GVA=0` built via `CPPFLAGS=-DRTCC_GLOBAL_R9_GVA=0` vs `=1` default.* That OFF arm was not OFF. Three independent proofs:

1. **The define is unguarded.** `rtcc.h:54` is a bare `#define RTCC_GLOBAL_R9_GVA 1` with no `#ifndef`. A command-line `-D` is processed *before* the header, so the header's redefinition wins. Reproduced twice: minimal repro, and against the real `rtcc.h` — both print `1` under `-DRTCC_GLOBAL_R9_GVA=0`.
2. **The Makefile never consumes `CPPFLAGS`.** `grep -nE "CPPFLAGS" Makefile` → zero hits. Compile rules are explicit (lines 338/340/342), so the flag never reached a gcc command line at all. The real hook is **`$(ZCFLAGS)`** (`Makefile:36`, `ZCFLAGS ?=`), threaded onto every compile line.
3. **The value was never 0 in any commit.** `git log -p --all -- src/runtime/rtx/rtcc.h | grep '^[+-]#define RTCC_GLOBAL_R9_GVA'` yields exactly one line, `+... 1`, introduced by `bcac52c4` — the RC-5-GVA landing commit itself. It was never hand-flipped either.

**Why nobody saw it:** gcc *does* emit `warning: "RTCC_GLOBAL_R9_GVA" redefined` — but the tree builds `-w` tree-wide. The guard-rail existed and was suppressed by our own build flags.

**Consequence.** 1.036x and 1.028x are noise between two identical binaries. This is fully consistent with both landing below `bench_min_of_n.sh`'s own `RATIO_FLOOR=1.10` (they would print `~null(<1.10x)`), and with the s224 lesson that this rail cannot resolve small effects. The s5 acceptance test — *"Rail 1.036x > 1.00x (no revert)"* — applied the RC-5 rung's `revert if ≤1.00×` rule to a number the instrument itself classifies as untrustworthy. **RC-5-GVA was retained on a measurement that cannot support retention.**

**NOT in question:** the FEATURE is live and correct. The poison probe (s5) and the asm census both use the *runtime* gate `SCRIP_RTCC`, which is unaffected by this defect. Re-confirmed this session: `SCRIP_RTCC=0` → 0 r9-relative GVA accesses; `SCRIP_RTCC=1` → 116 (fibonacci) / 54 (var_access) / 106 (roman). Only the RAIL NUMBER is void.

---

## 2. ROOT CAUSE, DEEPER THAN THE MISSING GUARD — THE KILLSWITCH IS DEFINED TWICE

`RTCC_GLOBAL_R9_GVA` has **two definitions**, neither guarded:

| file | line | consumer |
|---|---|---|
| `src/runtime/rtx/rtcc.h` | 54 | runtime (`rtcc_init.c` seeds the R9 slot) |
| `src/templates/x86_asm.h` | 17 | **every template** (`bb_var_global.cpp`, `bb_func_activate.cpp`, …) |

Templates **never include `rtcc.h`.** `x86_asm.h:12-18` hand-copies the externs and the constants (`RTCC_SLOT_R9`, `RTCC_GLOBAL_R8_ANCHOR`, `RTCC_GLOBAL_R9_GVA`, `RTCC_GVA_REG`) with the comment *"slot layout per rtcc.h"*. Confirmed against the recorded dependency file: `out/rt_pic/bb_var_global.d` lists 18 project headers and **`rtcc.h` is not among them.**

This is a live latent hazard independent of the A/B question: **editing one copy and not the other silently desynchronises emitter and runtime** — templates emit `[r9+k*16]` while `rtcc_init.c` never seeds the slot, so r9 = 0 and generated code dereferences null. That is the same *class* as the s6/s7 bug the claim-gate was built for, and the claim-gate cannot see it (it greps register usage, not macro definitions).

---

## 3. ⛔ MY OWN CLAIM FALSIFIED — TWICE, AND THE SECOND ONE WAS THE USEFUL PART

**(a) I truncated a grep and concluded from it.** My first census was `grep -rn RTCC_GLOBAL_R9_GVA src/ Makefile | head -12`. The `x86_asm.h` definition fell past line 12 of the output. I concluded "only one `#define`" and designed a fix on that basis. **A `head -N` on a census is a silent denominator error** — the same shape as the s8 "already done was a denominator error" conviction.

**(b) The fix was a hypothesis and the probe killed it.** I guarded `rtcc.h` and rebuilt with `make ZCFLAGS=-DRTCC_GLOBAL_R9_GVA=0`. Macro-level probe passed (`-D` now yields 0, default still 1). The **downstream probe falsified it**: emitted asm still showed 116 r9-relative accesses, and `fibonacci` now **SIGSEGV'd** — because only 3 objects rebuilt (`rtcc_init.o`, `core.o`, `keywords.o`); the templates read the *other* copy and were never recompiled. Net result: runtime with the claim OFF + templates with the claim ON = null dereference. **A one-sided guard is strictly worse than no guard**, because it makes the documented recipe produce a silently-split build. Reverted; tree verified clean; default arm re-verified at 116 accesses and both gates correct.

---

## 4. THE MECHANISM ARGUMENT — RC-5-GVA CANNOT MOVE A WALL CLOCK, BY CONSTRUCTION

Exact encoding delta, measured from emitted asm at the same annotated site (`# N`):

| arm | instruction | encoding | bytes |
|---|---|---|---|
| OFF | `mov rax, qword ptr [1879052304]` | `48 8B 04 25 + disp32` | 8 |
| ON | `mov rax, qword ptr [r9 + 16]` | `49 8B 41 + disp8` | 4 |

**4 bytes saved per access — and identical dynamic behaviour.** Same instruction, same one memory load, same traffic. RC-5-GVA changes **zero dynamic instruction counts**; the only benefit channel is I-cache footprint. On benchmarks whose entire text is 400–3000 instructions, that channel is nil. There is no mechanism by which this rung *could* produce an effect the rail can resolve. The rung was structurally ungradeable on a wall-clock instrument from the day it was written.

### Static census (deterministic, machine-independent, 23 benchmarks, `SCRIP_RTCC=0` vs `1`)

- GVA sites: **1,076** (vs s5's census of 1,038 — HEAD drift) → **4,304 bytes saved** corpus-wide.
- Veneer instructions added: **11,438** (+26% to +60% static instruction count per program).

The GVA rung recovers roughly 8.6% of the veneer's static footprint, in bytes, with no dynamic delta.

---

## 5. RUNTIME A/B — REPORTED WITH ITS LIMITS

Legitimate A/B (both arms genuinely differ): `SCRIP_RTCC=0` vs `1`, min-of-5, `-O0`, this box. **Measures the NET rung (veneer toll + GVA gain), not GVA alone.**

| program | RTCC=0 min | RTCC=1 min | ratio | note |
|---|---|---|---|---|
| fibonacci | 507 | 552 | 1.089 | ~null(<1.10x) |
| var_access | 387 | 418 | 1.080 | ~null(<1.10x) |
| string_manip | 1415 | 1478 | 1.045 | NOISY(A 146%, B 88%) ~null |
| roman | 225 | 232 | 1.031 | NOISY(A 17%) ~null |
| table_access | 1191 | 1207 | 1.013 | NOISY(A 275%) ~null |

⛔ **DO NOT QUOTE THESE.** Every row is below the trust floor and three are NOISY. **This box is 1 core** (`nproc`=1) with intra-arm spreads to 275% — s5's raws showed ~5% spread, so s5 ran on a materially better machine. The only defensible reading: the veneer is *slower* on all five, consistently signed, magnitude unresolved. **The RC-7 fold decision needs a better box or bigger workloads than this container provides.**

**Instrument gap:** `bench_min_of_n.sh` can only A/B `SCRIP_RTX_<FAMILY>` env gates. The goal that *owns* the RC-0(a) instrument cannot express its own A/B on it; the above was measured inline. See §6.

---

## 6. WHAT SHOULD HAPPEN NEXT (Lon's call)

1. ⛔ **ROUTED WINDOW REQUIRED — 2-line fix, byte-neutral at default.** Guard **both** copies with `#ifndef`/`#endif`, in ONE commit, or leave both alone. `x86_asm.h` is NOT-CONCURRENCY-SAFE. Better still, delete the `x86_asm.h` duplicate and have it include `rtcc.h` — one source of truth for a killswitch — but that is a larger include-graph change and wants its own rung.
2. **Correct the recipe of record everywhere it appears:** `make ZCFLAGS=-D…`, never `CPPFLAGS=-D…`.
3. **Grade RC-5 by static encoding delta, not by the rail.** It is deterministic, needs no quiet box, and it is the only instrument with the resolution to see a rung whose dynamic instruction delta is zero.
4. **Claim gate v2** (scripts-only, concurrency-safe): add the §0a `W → C → R` screen, and add a **macro-coherence check** — assert every RTCC constant has exactly one definition, or that duplicates hold equal values. That converts §2's hazard from latent to mechanical, and it is precisely the defect class the gate was chartered for.
5. **RC-5 should CLOSE, not continue.** GVA is the largest candidate at 1,076 sites and yields 4.3 KB with zero dynamic delta. The remaining candidates — `g_call_args` (13), `g_scan_hit_start` (8), `g_cap_gen` (8) — are two orders of magnitude smaller and cannot clear any instrument. This converts s8's *recommendation* to go to **RC-6** into a mechanism-backed *conclusion*: RC-6 changes instruction counts (crossings become direct jumps, writebacks vanish), so it is gradeable where RC-5 is not.

---

## 7. LEDGER

- Gate at open and close: `test_gate_rtcc_claimed_regs.sh --strict` PASS.
- HEAD unchanged `c7e085fd`; `git status` clean at close; killswitch default arm re-verified (116 r9-relative accesses, fibonacci correct both gates).
- No `.s` regen owed — zero emitter bytes touched.
- Cursor move: RC-5 rail claim reclassified **VOID (not stale)**; RC-5 recommended CLOSED; RC-6 promoted on mechanism, not preference.

## 8. SESSION AUTHORS
LCherryholmes · Claude Opus 5
