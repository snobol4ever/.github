# FINDING seat05 — END-ONLY-PROGRAM-ABORTS CLOSED: PINS DELETED, GATE ADDED, REGEN CLEAN, AND A SEPARATE 0-BYTE DIVERGENCE FLAGGED FOR HQ

**seat05 (`/home/claude05`, Claude Sonnet 5), 2026-08-22, THE LOOP queue row `end-only-program-aborts` (rank 0), resumed as an unfinished claim. SCRIP HEAD `568bf098` at session start (this session adds one new file, `scripts/test_gate_end_only_program.sh`, no other src/ changes). The fix itself landed a prior session at SCRIP `f7c25eb6` — this session closes the three items that commit's own message explicitly left open: the four wrong `.ref` pins, a regression gate, and codegen-regen artifacts.**

## (1) HEADLINE — VERIFIED LIVE, BOTH SCRIP MODES, AGAINST THE REAL ORACLE

The smallest legal SNOBOL4 program — a bare `END` statement, 4 bytes — now agrees exactly between SCRIP and the real oracle. `x64/` was **absent** from this checkout at session start (cloned fresh this session, per the mandatory oracle-clone step); with it cloned:

```
x64/bin/sbl -bf /tmp/e.sno   -> rc=0, 0 bytes
```

SCRIP mode-3 (`./scrip /tmp/e.sno < /dev/null`): rc=0, 0 stdout bytes, empty stderr.
SCRIP mode-4, checked **fully assembled/linked/executed**, not just emitted: `scrip --compile` → `gcc -c` → `gcc -no-pie ... -L out -lscrip_rt -lm -Wl,-rpath,out` → run (the identical recipe `scripts/test_mode34_parity.sh` already uses for exactly this comparison) → rc=0, 0 stdout bytes, empty stderr.

All four `corpus/programs/csnobol4-suite/preload{1,2,3,4}.sno` witnesses (each independently confirmed byte-identical to the 4-byte `END\n` file) plus `end.sno` from the same suite (dedupe corroboration, §8) pass identically in both modes.

## (2) THE DRIVER SEAM, NAMED

Two sites, same shape, one per mode, both in `src/driver/scrip.c`:

- **Mode-3** (`scrip.c:1670-1673`): `if (main_bb_idx < 0 || ...) { fprintf(stderr, "[IBB] FATAL: mode-3 driver: main BB graph not found\n"); abort(); }` — `abort()` raises SIGABRT, i.e. the observed rc=134 (128+6).
- **Mode-4** (`scrip.c:1385-1391`, `[SBB]` tag): the SNOBOL4-specific twin, same `main_bb_idx` guard, `return 1` instead of `abort()` — the observed clean `COMPILE_FAIL`.

Both guards fire when no `proc_table` entry named `"main"` was ever registered. Root cause (per `f7c25eb6`'s own message, reconfirmed by reading the guard sites this session): for a zero-statement program, `lower_sno_stage2()` bailed out **before** registering that entry, so `main_bb_idx` stayed at its `-1` initializer and tripped the guard on the very next line. `sno_build_graph()` already handled `nst==0` correctly (entry wired straight to the SUCCEED node) — the early return was the only thing stopping it from running. A second, independent bug shared the same blast radius: `emit_chain`'s existing "jump straight to γ/ω when the body is empty" shortcut (`flat_empty_body_succ`/`flat_empty_body_fail`) was gated on `flat_jmp_entry`, so it only ever fired for empty jmp-entry procedures, never for the plain top-level `main` graph — hoisted out of that gate.

## (3) DISPOSITION OF THE FOUR WRONG PINS — DELETED, NOT REGENERATED

`corpus/programs/csnobol4-suite/preload{1,2,3,4}.ref` were 3, 6, 6, and 6 bytes respectively (`aa\n`, `aa\nbb\n`, `pa\npb\n`, `pa\npb\n`) — wrong on a program that provably cannot produce output. **Deleted**, not regenerated to an empty file: there is no oracle-dependent behavior to pin here — a bare-END program's correct output is definitionally zero bytes for *any* correct SNOBOL4 implementation, so a `.ref` fixture adds no coverage that a direct rc/byte-count assertion (§4) doesn't already give more directly. Confirmed both harnesses that scan this suite treat a missing `.ref` as SKIP, not FAIL: `test_regression_full_corpus.sh:128` (`[ -f "$ref" ] || continue`) and `test_csnobol4_budne_suite.sh:75` (`[ ! -f "$ref" ] && return`) — so the deletion is a clean no-op for existing harnesses, and the real regression coverage now lives in the new gate.

## (4) THE NEW GATE

`scripts/test_gate_end_only_program.sh`: asserts a synthetic bare-`END` file plus all five real witnesses (`preload1-4`, `end`) exit rc=0 with zero stdout bytes, in mode-3 directly and in mode-4 fully assembled/linked/executed (same recipe as §1). All 12 checks green:

```
OK   m3 bare-END: rc=0, 0 bytes      OK   m4 bare-END: rc=0, 0 bytes
OK   m3 preload1: rc=0, 0 bytes      OK   m4 preload1: rc=0, 0 bytes
OK   m3 preload2: rc=0, 0 bytes      OK   m4 preload2: rc=0, 0 bytes
OK   m3 preload3: rc=0, 0 bytes      OK   m4 preload3: rc=0, 0 bytes
OK   m3 preload4: rc=0, 0 bytes      OK   m4 preload4: rc=0, 0 bytes
OK   m3 end:      rc=0, 0 bytes      OK   m4 end:      rc=0, 0 bytes
```

## (5) REGEN — RUN IN FULL PER THE HANDOFF RULE; ZERO BYTES MOVED ANYWHERE

`f7c25eb6`'s own commit message flagged "codegen regen artifacts have not been run" as open. This session ran all six, in the documented order: `util_regen_benchmark_s_artifacts.sh` → `util_regen_feature_s_artifacts.sh` → `util_regen_demo_s_artifacts.sh` → `util_regen_programs_s_artifacts.sh` → `util_regen_prolog_bench_s_artifacts.sh` → `util_regen_crosscheck_s_artifacts.sh`. **Every one reports `changed=0` / "already current" / all-`same`.** `git status --short` in both `SCRIP` and `corpus` confirms zero bytes touched by the whole run.

This is reassuring, not suspicious: none of the six regen-covered corpora (SCRIP `test/snobol4` feature tests, the demo suite, `corpus/benchmarks`, `corpus/crosscheck`, the Prolog bench set, or — `programs`-regen's own log line self-labels this explicitly — `programs/{icon,prolog,rebus}`) contains a zero-statement top-level program, and `corpus/programs/csnobol4-suite` (where the actual witnesses live) is not in scope for **any** of the six scripts and never had committed `.s` siblings for `preload1-4`/`end` to begin with. The emit_chain change genuinely has no other surface to move.

Pre-existing `EMIT-FAIL`/`AS-FAIL` noise surfaced by the `programs` and `crosscheck` regen passes (Icon `rung36_jcon_*`, `programs/prolog/gnu_prolog/**`, several `snocone/rung{A,B}*` files) is long-standing WIP debt in unrelated frontends — the regen scripts themselves skip-not-overwrite on a failed emit/assemble, by design (`(empty/crash; NOT updated)`). Not this row's concern; not investigated further.

## (6) CORPUS NO WORSE

- `test_smoke_snobol4.sh`: 7/7 both modes.
- `test_corpus_snobol4.sh`: m3 PASS=355 FAIL=2, m4 PASS=353 FAIL=2 SKIP=2 — byte-identical to today's standing baseline (cross-checked against the count already cited in seat4's `free-r11` FINDING from earlier the same day).
- `test_gate_emit_no_lang.sh`: green (LANG-BLIND invariant unaffected, as expected — this row never touched emitter/template language-conditioning).

## (7) ⛔ FLAGGED, NOT FIXED — A SEPARATE, REAL 0-BYTE-FILE DIVERGENCE

While scoping the new gate, this session checked a natural adjacent case — a **genuinely empty (0-byte) source file**, no `END` at all — expecting it might belong in the same gate. It does not, and the reason is itself worth recording:

```
x64/bin/sbl -bf /tmp/empty.sno   -> rc=1, stderr: "No END statement found in source file(s)."
scrip /tmp/empty.sno (both modes) -> rc=0, 0 bytes  (identical to legal bare-END handling)
```

SCRIP currently treats a missing `END` exactly like a legal bare-`END` program; the oracle treats it as an error. This is a real, measured divergence, **separate from and not covered by** this row's brief (which is specifically the bare-END floor case, already oracle-confirmed correct in §1). It was deliberately **excluded** from `test_gate_end_only_program.sh` — asserting "0-byte succeeds" would have gated in the divergence as if it were correct — and deliberately **not fixed** here, since it is outside this row's DONE-WHEN and this session's claim. Proposing a new queue row (suggested name: `empty-file-no-end-diverges-from-oracle`) for HQ to rank; no corpus or source change made for it.

## (8) DEDUPE CROSS-REFERENCE — `lower-fatal-bombs-two`

That row's bomb (2) — `csnobol4-suite/end` producing `[IBB] FATAL: mode-3 driver: main BB graph not found` — is the same mechanism as this row, independently confirmed by seat07 via inbox message this session: `end.sno` is byte-identical to the four `preload*.sno` witnesses (all exactly `END\n`, 4 bytes), and seat07 re-verified `f7c25eb6` cures it on the merged tree, both modes. `end.ref` was already correct (0 bytes) and needed no pin repair — folded into the new gate as a fifth witness per seat07's suggestion (§4, §1). See `FINDING-2026-08-22-seat7-comment-sno-fatal-was-a-missing-indirect-pattern-arm-and-end-dedupes-fully.md` for the full seat07 receipt. That row's bomb (1) (`comment.sno`'s GZ#5 pattern-shape refusal) is unrelated to this row and remains seat07's to close.

## DISPOSITION

Row `end-only-program-aborts`: **CLOSED.** All DONE-WHEN items satisfied: both modes exit 0 with zero output on the 4-byte END program (§1); the driver seam named (§2); `preload1-4` green via the new gate, no longer scored by the corpus-diff harnesses that would otherwise need wrong pins (§3-4); the four wrong pins deleted with justification (§3); a gate covers the floor case (§4); codegen regen run clean (§5); corpus no worse (§6). One adjacent divergence flagged, not fixed, with a proposed follow-up row (§7).
