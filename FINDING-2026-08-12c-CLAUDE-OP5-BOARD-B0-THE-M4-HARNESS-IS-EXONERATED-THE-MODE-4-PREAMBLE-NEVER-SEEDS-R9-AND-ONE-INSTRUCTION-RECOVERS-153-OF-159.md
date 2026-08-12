# FINDING 2026-08-12c — BOARD B-0: the m4 harness is EXONERATED; the mode-4 preamble never seeds r9/GVA; one instruction recovers 153 of 159

**Seat:** BOARD (`GOAL-SN4-HOME-BOARD.md`), rung B-0. **Compiler bytes written: ZERO** (charter). Diagnosis + instrument only; the repair is assigned, not applied.

---

## 1. THE INHERITED CLAIM IS FALSE

Carried since 2026-08-10 in `GOAL-SN4-ZETA-CLIMB.md` line 37 and `FINDING-2026-08-10f` §57, verbatim in substance:

> *"`run_suite.sh MODE=compile` returns EMPTY output for all 135 probes … Mode 4 compiles/links/runs correctly BY HAND (`--compile` → as+gcc → `hello` rc=0). **Harness defect, not compiler.** Possibly the absolute-path class of FINDING-2026-08-10h."*

**Every clause of the conclusion is wrong.** The harness is correct and was reporting a true result. Mode 4 is genuinely broken. The absolute-path class is not involved — in this container the pinned `/home/claude/...` paths all resolve, `SCRIP` defaults correctly, and `RTOUT="$(dirname "$SCRIP")/out"` is exactly where `out/libscrip_rt.so` is built (Makefile:343).

**How the error was made — and it is a named trap:** the by-hand witness was `hello`. `hello` has **zero user globals**, therefore zero GVA slots, therefore it never touches r9 — the one register the defect leaves null. It cannot fail. RULES.md §9 already names this: *"a passing sibling is NOT evidence."* The witness was structurally incapable of reproducing the class it was used to exonerate. `run_suite.sh` was then edited out of trust for two days on the strength of it.

Second contributing cause: **`run_suite.sh` lines 52–55 discard every diagnostic** (`2>/dev/null` on all four stages of the `&&` chain). A link failure, a compile failure, and a SIGSEGV are indistinguishable in its output — all three surface as `got =[]`. The harness was not lying, but it was mute, and mute got read as dark. (The suite *did* print `(CRASH)` / `(signal 11)` on every line; that was overlooked.)

## 2. THE MEASUREMENT (this HEAD, one build, both modes, 163 probes / 163 refs)

| mode | pass | xfail | XPASS | REGRESSION |
|---|---|---|---|---|
| m3 `--run` | **157** | 1 | 0 | **5** — D12 · D13 · H31 · X01 · X10 |
| m4 `--compile` at HEAD | **2** | 2 | 0 | **159** |
| m4 with the r9 seed restored | **155** | — | — | **8** |

m4's only survivors at HEAD are `X12` and `zleak_matchbegin_stfh`. `FINDING-2026-08-10e` recorded m4 at **133 pass** — so the collapse is real, dated, and has been carried as "harness dark" ever since.

## 3. ROOT CAUSE — ONE MISSING INSTRUCTION

`n4_assign_α` stores a global through the GVA base register:

```
mov qword ptr [r9 + 0], rax    # SUBJ
```

At the fault, **`r9 = 0x0`**. The emitted mode-4 `main` preamble is:

```
call core_lib_init@PLT
mov  edi, 1
call rt_gva_island@PLT      <- returns the GVA island base in RAX
mov  rsi, rax               <- base goes to RSI, as gva_register's ARGUMENT
lea  rdi, [rip + __gva_names]
mov  edx, 1
call gva_register@PLT
mov  r12, qword ptr [0x70000000]
xor  esi, esi
jmp  main_α                 <- body entered with r9 STILL ZERO
```

The base is produced, passed as an argument, and then **dropped**. It never reaches r9. Every later `mov r9, qword ptr [r11 + 48]` in the body is the RTCC *reload after a C crossing* — a restore of a value that was never established. First global access ⇒ null store ⇒ SIGSEGV.

**Emit site:** `src/driver/scrip.c:1473` (SNOBOL4, m4 text) and the identical shape at `:1265` (Icon, m4).

**The mode-3 asymmetry that hid it:** `src/driver/scrip.c:1538–1542` seeds the arena in C (`m3_gva_arena = rt_gva_island(n_gva_m3)`, `gva_register(...)`, `g_gva_active = 1`). Mode 3 establishes the base in-process; mode 4 emits the calls and lands nothing in the register. The two halves of the GVA rail were never joined on the m4 side — which is precisely the **H2 class already documented in `x86_asm.h:292–319`** ("THE R9/GVA SLOT IS NOT WRITTEN BACK … C and generated code then disagree about where RT_GVA_VA lives, which is exactly the H2 SIGSEGV class"). The static_assert guards the *offset*; nothing guarded the *seed*.

## 4. PROOF (scratch `.s` only — no compiler byte touched)

`rt_gva_island` (`src/runtime/rt/rt.c:549`) returns the constant `RT_GVA_VA` and is idempotent at preamble time. Inserting into the **generated** `.s`, immediately before `jmp main_α`:

```
mov  edi, 1
call rt_gva_island@PLT
mov  r9, rax
```

A01: `rc=139`, 0 bytes ⇒ `rc=0`, output `=S`, **byte-identical to `A01.ref`**. Swept across all 163 probes: **153 of the 159 failures recover.** Instrument: `SCRIP/scripts/util_board_m4_gva_seed_probe.sh` (patches only a scratch copy; re-runnable; prints the recovered set).

## 5. WHAT THIS MEANS FOR THE PLAN

- **B-0 is discharged as diagnosis.** The rung was written as "m4 HARNESS REPAIR". The harness needs no repair. What needs repair is the m4 preamble, and that is **compiler bytes — outside BOARD's charter by construction.** Assigned, not applied.
- **P0 was blocked for two days on a false attribution.** Every m4 number published since 2026-08-10 across every seat is void — not because the instrument was dark, but because mode 4 was genuinely dead below the first global assignment. `GOAL-SN4-ZETA-CLIMB.md`'s "DO NOT TRUST A ZERO" banner is corrected in the same push.
- **The residual 8 is the honest m4 gap** and the first real m3/m4 divergence set (m4 155 vs m3 157). It is not characterised here; characterising it is B-1 work once the seed lands.
- **Do not treat 153/159 as the fix's acceptance.** The proof patches the *output*; the real repair must emit the seed from the driver, both language arms (`:1473` SNOBOL4 and `:1265` Icon), and must survive the RTCC reload convention — the seed must dominate every consumer, including the `[r11+48]` restores.

## 6. OWNER

The GVA rail is the **RTCC** surface (`R9 = GVA base, RTCC LIVE claim`, HOME register contract). Under the consolidation, RTCC "stays law + history" with RC-8b/8c adopted at **HOME-RBX X-5**, and the m4/C-boundary wire half sits with **WIRES**. The edit itself is three lines in `src/driver/scrip.c` and belongs to whichever of RBX/WIRES claims it first — **first push wins, per RULES 2026-08-10.** BOARD does not claim it and will re-referee the board at its own HEAD once it lands.

**⛔ Standing correction for every seat:** an m4 number taken between 2026-08-10 and this finding is void. Re-measure at your own HEAD. And the liveness check named in the HOME self-gating protocol (`run_suite.sh MODE=compile` returns non-empty) was **passing the whole time** — non-empty output is not liveness when every line reads `got =[]`. The check should be: *at least one probe PASSES*.
