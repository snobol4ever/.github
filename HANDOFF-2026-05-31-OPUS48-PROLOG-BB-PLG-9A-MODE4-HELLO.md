# HANDOFF — PLG-9a: Prolog mode-4 (`--compile --target=x86`) hello-world emits, assembles, links, runs

**Author:** Claude Opus 4.8 · **Date:** 2026-05-31 · **SCRIP HEAD (pre-commit):** `8a01bb3`
**Goal:** GOAL-PROLOG-BB.md
**Directive (Lon):** continue GOAL-PROLOG-BB — climb the mode-4 ladder; PLG-9a is the first sub-rung.

## What landed

**Prolog mode-4 (`--compile --target=x86`) for the proven hello-world tier — un-EXCISED.**

`hello.pl`:
```prolog
:- initialization(main).
main :- write(hello), nl.
```
`scrip --compile --target=x86 hello.pl` now emits a standalone GAS `.s`; `as --64` + `gcc -no-pie …
libscrip_rt.so` links it; running prints `hello`. This is the first Prolog program to cross onto
mode-4 native x86 since Ground-Zero excised the Stack Machine.

The emitted body (abridged) — note it mirrors the Icon mode-4 shape exactly, and the write atom is a
sealed `.rodata` constant read directly by its consumer (no ring, no value stack):
```asm
main:
  push rbp ; mov rbp, rsp
  call rt_frame@PLT
  mov rdi, rax ; xor esi, esi
  call main_α
  xor eax, eax ; pop rbp ; ret
main_α:
  push r12 ; mov r12, rdi ; lea r10, [rip + Δ]
main_α_body:
 # BOX RESOLVE_BUILTIN(write/1)
 lea rcx, [rip + .S0] ; mov rdi, rcx ; call rt_pl_write_atom@PLT
 jmp plseq0_g1_α
 # BOX RESOLVE_BUILTIN(nl/0)
 mov edi, 10 ; call putchar@PLT
 jmp main_γ
main_γ: mov eax, 1 ; xor edx, edx ; pop r12 ; ret
main_ω: mov eax, 99 ; xor edx, edx ; pop r12 ; ret
.section .rodata
.S0: .string "hello"
.text
```

## Mechanism (additive, Prolog-only, +99/−6 across 4 files)

1. **`src/driver/scrip.c`** — new `if (is_prolog)` arm in the `mode_compile_x86` block, AFTER the Icon
   arm, BEFORE the SNOBOL abort (per-language guard; the global `[SMX]` gate was already removed —
   `scrip.c` per-language-dispatches `mode_compile_x86` since `5c97162`). It reuses the **same**
   `pl_flat_body_root` recognizer the PLG-8-native mode-3 arm uses (single-clause body = conjunction
   of constant-arg builtins write/writeln/print/nl + IR_SUCCEED/IR_CUT/IR_ATOM, `nslots==0`). On a
   match: `g_frame_active=1` → emit the SAME `main:`→`rt_frame`→ζ(rdi),esi=0→`call main_α` C-ABI
   wrapper Icon emits → `codegen_flat_build(flat_root, stdout, "main")` (MEDIUM_TEXT walk reaching the
   `bb_builtin.cpp` write/nl TEXT arm — the byte-twin of the MEDIUM_BINARY arm mode-3 JITs, per
   MIGRATION-MODE4-IS-MODE3-DUMP: one template, two output sinks) → the strtab bridge. NULL root →
   `[SMX]` banner + `return 1` (smoke/rung report EXCISED, not FAIL; zero regression). The dead
   `[SMX] pending` stub was removed.

2. **`src/emitter/emit_core.c` + `emit_core.h`** — new `xa_emit_strtab_rodata()`. The write/1 IR_ATOM
   arg label is produced by `strtab_label` (the `g_flat_intern_str` hook is never set, so in TEXT mode
   `bb_intern_into` falls to strtab — Prolog differs from Icon here, whose `bb_call` emits rodata
   inline). `strtab_label` interns into the private `g_strtab[]`; the `XA_STRTAB_RODATA` template reads
   the separate `g_emit.xa_strtab_*` arrays. The bridge marshals one into the other (label `.S<idx>:`
   WITH the definition colon — reference sites use `.S<idx>` without; `gas_escape_str` for the quoted
   literal) and dispatches the template. This is exactly the "driver fills g_emit.xa_strtab_*, then
   calls xa_dispatch" contract the template's own header documents — the driver half was deleted at
   Ground-Zero. **It emits ZERO x86 bytes** (the template emits the `.rodata` section); FACT-clean.
   Only reachable from the Prolog mode-4 arm → siblings untouched.

3. **`scripts/test_prolog_rung_suite.sh`** — per-file `[SMX]`-banner detection → EXCISED. Mode-4 is
   now PARTIALLY live: the whole-mode probe (`mode_is_excised`) used to mark all of mode-4 EXCISED
   because a trivial probe printed `[SMX]`; now the probe emits real code, so the suite runs every
   file, and a shape the flat tier does not cover declines with `[SMX]`. Per the testing discipline
   ("a mode whose probe prints the SMX banner is reported EXCISED … and auto-starts counting the
   moment it emits real output"), those declines are EXCISED, not FAIL. Added an `EXCISED=` column,
   matching `test_smoke_prolog.sh`'s long-standing per-file handling.

## Gates (all green, no regression)

| Gate | Before | After |
|---|---|---|
| GATE-1 smoke m2 | 5/5 | 5/5 |
| GATE-1 smoke m3 | 5/5 | 5/5 |
| GATE-1 smoke m4 | 0/5 (EXCISED) | **1 PASS** (`write_atom`) / 4 EXCISED |
| GATE-3 rung m2 | 111/111 | 111/111 |
| GATE-3 rung m3 | 111/111 | 111/111 |
| GATE-3 rung m4 | EXCISED | **2 PASS / 0 FAIL / 109 EXCISED** |
| prove_lower2 | 51/51 | 51/51 |
| FACT grep | 0 | 0 |
| Icon smoke | m2/m3/m4 6/6 | m2/m3/m4 6/6 (unaffected) |
| SNOBOL4 smoke | m2 7/7 (m3/m4 SBL-RING-REMOVE abort) | m2 7/7 (unchanged) |

SNOBOL4 m3/m4 remain at the pre-existing `SBL-RING-REMOVE` abort state (`58dff40`); not touched here.

## Findings for the next rung

- **`halt` lowers to `IR_GOAL`**, not `IR_BUILTIN` (it is not in `lower.c`'s `det_builtins`), so it is
  NOT in the native flat tier yet — `pl_flat_body_root` correctly declines a body containing it. This
  is an upstream lowering matter, orthogonal to mode-4. (The `bb_builtin.cpp` `halt` TEXT arm exists
  and would light up the moment `halt` lowers to `IR_BUILTIN`.)
- The 2 rungs passing m4 are the corpus hello-tier shapes; everything else is EXCISED by the same
  recognizer mode-3 uses, so m3 and m4 stay in lockstep automatically as the recognizer widens.

## NEXT — PLG-9b (first per-box RW slot)

`X = world, write(X)` and `X is 2+3, write(X)` have `nslots>0` (one logic-variable slot). Per the
PER-BOX LOCAL STORAGE FACT RULE the slot must live in the ζ-frame (`[r12+off]`), not the ring and not
`g_resolve_env`. Steps:
1. Extend `pl_flat_body_root` to accept `IR_UNIFY` (var=const) and `nslots>0` (the recognizer is
   shared with mode-3, so mode-3 native widens in the same commit — keep both byte-identical).
2. Confirm `bb_unify` (TEXT arm) writes the slot via the per-sequence frame and `rt_pl_write_var(slot)`
   reads from the same frame.
3. Then PLG-9c arith (`is`, IR_ARITH TEXT arm — already present), PLG-9d facts/choice (IR_GOAL +
   IR_CHOICE + predicate-registry emit via `walk_bb_flat` in TEXT, `flat_drive_pl_choice`), PLG-9e
   recursion (mirror the Icon `rt_proc_register` loop in the mode-4 arm).

Each rung: verify the program emits+assembles+links+runs AND GATE-1/GATE-3 m3 == m2 hold throughout.

## Files

- `src/driver/scrip.c` — Prolog `mode_compile_x86` arm; dead `[SMX] pending` stub removed.
- `src/emitter/emit_core.c` / `emit_core.h` — `xa_emit_strtab_rodata` strtab→template bridge.
- `scripts/test_prolog_rung_suite.sh` — per-file `[SMX]` → EXCISED classification + column.
- `.github/GOAL-PROLOG-BB.md` — PLG-9a sub-rung marked done + gate-table refresh.
