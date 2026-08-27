# FINDING — N-2 item 2 step 2a: the host reservation size is computable from graph fields alone

**Seat:** hq_P (HQ-PERFORMANCE, `/home/claude_P`) · **Date:** 2026-08-27 · **Mode:** FLEET-16
**Row:** `icon-n2-generator-activation-frames` (rank 0, ASSIGNED:hq_P) — item 2, step 2a
**Acceptance row:** `icon-bench-correct-zero-of-eight` (still BLOCKED; `bench_correct` NOT re-scored)
**Tree:** SCRIP `67845333` · RT_OPT `-O0`

## What was owed

ceo's ruling (2026-08-27) settled step 2's design: a graph hosting a suspend-surviving call **promotes to a real RBP
activation frame**, and a **direct** call **reserves the callee's compile-time-known frame bytes inside the host's own
carve at a fixed offset** — nothing moves at the landing. That requires the host to know the callee's frame size **at
host-α time**. Step 1b (`b6703276`) proved `jcon_value_region` is valid pre-emission once `drive_slots_all()` has run.
This step proves the rest of the size.

## What was measured

⭐ **THE FORMULA, and every input is an `IR_graph_t` field:**

```
ft == ((48 + jcon_value_region + 15) & ~15) + (nparams + nlocals) * 16
```

`jcon_value_region` (`IR.h:205`), `nparams` (`:206`), `nlocals` (`:208`). So a host can size the reservation
**without the callee having been emitted first** — no table, no two-pass emission, and **no new global**.

| arm | graph observations | agree | generator graphs |
|---|---|---|---|
| gate OFF | 654 | **654** | 18 / 18 |
| `SCRIP_ICN_GENFRAME2=1` | 654 | **654** | 18 / 18 |
| **total** | **1308** | ✅ **1308** | ✅ **36 / 36** |

Across 400 Icon programs. ⭐ **The two arms being identical is the load-bearing part**, not a redundancy: a formula
that only held unarmed would be useless to step 2, which runs armed.

## Why it is a GATE and not a logged number

`flat_frame_bytes` is assigned on several emitter paths — `emit.cpp:3358`, `:3464`, and the `_stfj` arm which forces
**48** outright. Any one of them drifting from this formula silently re-sizes **every** host carve; **too small is
stack corruption**, and it would surface as a generator bug three layers away from the edit that caused it. So the
invariant is re-proved on every run by `scripts/test_icn_n2_ft_formula.sh`, never quoted from this session's log.

⭐ **Gate proven before trusted:** REFUSES `rc=2` with no `./scrip`, and **also refuses when zero generator graphs are
observed** — the formula untested where it matters is not a pass, it is an empty denominator wearing a green tick.
FAILS `rc=1` on a deliberately poisoned `predft` (`+16`), caught **1308/1308**.

## A stale design struck from the code

`icn_gen_zeta_ft()`'s comment in `x86_asm.h` still told the next reader that item 2 is *"re-point rbp at the heap
island `e->frame`"*. ⛔ Lon **deleted that island** (`rt_icn_gen_frame_alloc`/`_retire` removed at `915bdaa4`) and
`RULES.md:72` § THE STORAGE ANSWER rules that a suspend-surviving frame carves in the **enclosing graph's RBP
activation frame, never the heap**. Left standing, that sentence sends the next session to implement a retracted
design — the same class as the DUO/FLEET banner and the `command -v icont` probe: **a confident sentence in the place
a reader looks first outranks the correction filed elsewhere.** Replaced with the ruled target and this formula.

## Noted, not fixed

⚠️ **`g_last_flat_frame_bytes` holds `jcon_value_region`, NOT `flat_frame_bytes`** (`emit.cpp:3475`). The name says
the wrong thing, and this rung has already lost time to reading it as the carve size. Not renamed here — a rename is
behavioural surface across `runtime_eval.c`, `scrip.c` and `emit.cpp` and deserves its own attributed commit.

## Inertness and control arms

- `.s` **byte-identical** probe-on vs probe-off on the four-line witness **and** `rsg.icn`; negative control
  armed-vs-unarmed = **77 lines**, so the diff is not vacuous.
- ⛔ **SHARED-NODE VERDICT SCOPE** — `x86_asm.h` is shared by every frontend, so all four boards are owed and were
  measured (`-O0`, incremental, **not** a pristine gate verdict): SNOBOL4 `m3 366/366 · m4 366/366 SKIP=0 MISSING=0`
  rc=0 · Icon smoke **14/14** both modes · Prolog **4/5** · Snocone **5/5** (both = recorded baseline; CLAUDE.md's
  3/5 and 4/5 are stale) · `emit_no_lang` rc=0 · `template_medium` rc=0 · step-1b guard **429/429 AGREE**.
- **D2 gate-OFF = pinned baseline**: five suspend shapes `CRASH 10/10` m3=m4, controls CORRECT. **Unmoved is correct.**
- ⭐ Boards re-measured **after** a rebase landed `perf-onedend-dcap-ceremony` (a codegen change threading rc through
  rax instead of a stack push/pop) under this work — the first reading graded a tree that no longer existed.
- ⚠️ The SNOBOL4 denominator moved **365 → 366** on a corpus add (`crosscheck/capture 067`). `FAIL=0/SKIP=0/MISSING=0`
  is the invariant; the total is not. Do not pin 365.

## Not claimed

⛔ **No cure.** `bb_call_proc_staged.cpp:733`'s `lea rsp,[rax+32]` is untouched; `bench_correct` remains **0/8** and
was deliberately **not re-scored**.
⛔ **Step 2b — the host promotion emission — is NOT written.** This lands the number it needs, measured and gated.
⛔ The formula was measured on **Icon** graphs. It is expressed in language-blind graph fields, but agreement was not
measured on SNOBOL4/Prolog/Snocone graphs — do not upgrade it to a cross-frontend invariant without measuring it.
⛔ Says nothing about **indirect/dynamic** generator dispatch, which ceo left explicitly UNRULED (70 `IR_CALL_VALUE`
sites) and handed to hq_C's one-shape-test design. No indirect premise entered this slice.
