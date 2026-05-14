# GOAL-MODE4-SN4-SNOCONE.md — Mode-4 x86 Full Test Suite: SNOBOL4 + Snocone

⛔ **Read before any source file:** `ARCH-x86.md` then `ARCH-SCRIP.md` then `ARCH-EMITTER.md`.

**Repo:** one4all+corpus+.github.
**Done when:** every SNOBOL4 and Snocone test that passes under `--sm-run` also passes under `--jit-emit --x64` (linked binary via libscrip_rt.so). Zero regressions vs the `--sm-run` baseline.

**Mode-4 pipeline recap:** `scrip --jit-emit --x64 file.sno` → `.s` → `gcc -c` → `gcc link -lscrip_rt` → ELF binary → run. All test harness scripts use this pipeline with the working dir set to `/home/claude/one4all` (for macro includes).

---

## Baselines (one4all `4f0e2996`, 2026-05-14)

| Suite | Script | Mode-4 now | SM-run baseline | Target |
|---|---|---|---|---|
| smoke_snobol4 | `test_smoke_snobol4.sh` | 7/7 ✅ | 7/7 | 7/7 |
| jit_emit_x64 | `test_smoke_jit_emit_x64.sh` | 11/13 (EM-7c pre-existing) | — | 13/13 |
| beauty subsystems mode-4 | `test_gate_em_beauty_subsystems_mode4.sh` | 17/17 ✅ | 17/17 | 17/17 |
| crosscheck_snobol4 | `test_crosscheck_snobol4.sh` | 6/6 ✅ | 6/6 | 6/6 |
| crosscheck_snocone | `test_crosscheck_snocone.sh` | 6/8 | 8/8 | 8/8 |
| gate_em8_snocone | `test_gate_em8_snocone_jit_emit.sh` | 5/5 ✅ | 5/5 | 5/5 |
| broad corpus (sm-run parity) | `test_interp_broad_corpus_and_beauty.sh` | 128/280 sm-run | 128/280 | ≥128/280 (no regression) |
| regression x64 | `test_regression_full_corpus.sh MODE=x64` | 13/430 | — | maximize |
| snobol4 jit parity | `test_smoke_snobol4_jit.sh` | ir=129 sm=128 jit=128 | — | jit≥sm |

**Key failing categories in `test_regression_full_corpus.sh MODE=x64` (430 total, 417 failing):**

The `test_regression_full_corpus.sh` x64 mode uses an old pipeline (mock_includes, not libscrip_rt.so) — its 13/430 is NOT the real mode-4 number. The real mode-4 health is beauty 17/17 + crosscheck 5/6 + 6/8.

The true failing SNOBOL4 crosscheck tests (via `test_crosscheck_snobol4.sh`):
- **1 fail:** `test_crosscheck_snobol4.sh` — identify which one
- **2 fails:** `test_crosscheck_snocone.sh` — `procedure` and one other

The true failing categories in broad corpus under mode-4 (via the beauty parity gate and manual tests):
- Pattern matching: SPAN, BREAK, LEN, TAB, RTAB, REM, ARBNO, ALT — failing in `--sm-run` too (pre-existing)
- Arrays, tables, DATA, DEFINE — failing in `--sm-run` too (pre-existing)
- Indirect/eval — failing in `--sm-run` too (pre-existing)

Only mode-4-specific failures matter here. From beauty: 0 (17/17 perfect). From crosscheck: identify specifically.

---

## Steps

### M4SN-0 — Identify exact crosscheck failures and their cause

- [x] **M4SN-0a** — Run `test_crosscheck_snobol4.sh` and `test_crosscheck_snocone.sh` with verbose output. For each failure: diff mode-4 output vs sm-run output. Categorize: emit error / asm error / link error / wrong output / segfault.
- [x] **M4SN-0b** — Run `test_gate_em8_snocone_jit_emit.sh` verbose. Diff `procedure` driver mode-4 vs sm-run.
- [ ] **M4SN-0c** — Run `test_smoke_jit_emit_x64.sh` and identify EM-7c root cause (got='abc' want='aXc'). The EM-7c test is a variant ARBNO pattern — likely the non-invariant variant cap path (child_fn=NULL, no label registered). Fix or XFAIL.

### M4SN-1 — Fix EM-7c (variant ARBNO/CAP with no invariant child blob)

Variant patterns (non-invariant) have `child_fn=NULL` since `pre_build_children` only caches invariant windows. When `emit_bb_xarbn(NULL, ...)` fires in TEXT mode, `child_cache_get_lbl(NULL)` returns NULL → no fixup registered → `.data` slot stays zero → segfault or wrong behavior at runtime.

Fix: for variant-pattern ARBNO/CAP, the child blob IS emitted inline in the pattern (not as a separate invariant proc). The flat TEXT emitter for the variant case needs a different approach — either:
- (A) Emit a RIP-relative label for the inline child code and register that as the fn
- (B) Fall back to `rt_bb_*@PLT` brokered path for variant caps (acceptable — they are rare)

- [ ] **M4SN-1** — Implement option B as the simpler fix: detect `child_fn==NULL` in `emit_bb_xarbn/xnme/xfnme/xcallcap` TEXT path and emit a brokered `rt_bb_arbno_brokered` / `rt_bb_cap_brokered` call instead. Gates: EM-7c PASS, smoke 7/7, beauty 17/17.

### M4SN-2 — Crosscheck snobol4 6/6

- [ ] **M4SN-2** — Fix the 1 failing crosscheck snobol4 test. Likely a pattern or builtin issue specific to the mode-4 binary path. Gates: crosscheck_snobol4 6/6, smoke 7/7, beauty 17/17.

### M4SN-3 — Crosscheck snocone 8/8

- [x] **M4SN-3a** — Fix `procedure` diff in `test_gate_em8_snocone_jit_emit.sh` and `test_crosscheck_snocone.sh`. The Snocone frontend lowers to the same IR — if procedure calls fail in mode-4, this is likely a `SM_CALL` / user-function dispatch issue in the x64 binary (same root as SNOBOL4 DEFINE failures).
- [ ] **M4SN-3b** — Fix second crosscheck_snocone failure. Gates: crosscheck_snocone 8/8, gate_em8 5/5.

### M4SN-4 — Broad corpus SNOBOL4: sm-run parity in mode-4

Run `test_interp_broad_corpus_and_beauty.sh` in mode-4 (needs a new script or MODE=x64 wrapper). Every test that passes under `--sm-run` must also pass under `--jit-emit --x64`.

- [ ] **M4SN-4a** — Write `test_mode4_broad_corpus_snobol4.sh`: same logic as `test_interp_broad_corpus_and_beauty.sh` but uses the emit→link→run pipeline. SCRIP=./scrip, RT_DIR=./out, assemble in /home/claude/one4all (for macros). Compare output vs `.ref` files.
- [ ] **M4SN-4b** — Run and triage failures by category. Fix mode-4-specific failures only (those passing in `--sm-run` but failing in mode-4).
- [ ] **M4SN-4c** — Target: mode-4 broad corpus PASS ≥ sm-run PASS (128/280). No regression.

### M4SN-5 — Full regression: test_regression_full_corpus.sh MODE=x64 with libscrip_rt pipeline

The existing `test_regression_full_corpus.sh MODE=x64` uses the old mock-include pipeline (13/430). Rewrite or add a new script using the libscrip_rt.so pipeline.

- [ ] **M4SN-5a** — Write `test_mode4_full_regression.sh`: iterate all crosscheck .sno files, emit→link→run via libscrip_rt.so, compare vs .ref. Report PASS/FAIL/SKIP.
- [ ] **M4SN-5b** — Run and establish true mode-4 baseline count.
- [ ] **M4SN-5c** — Fix mode-4-specific failures. Target: PASS count ≥ sm-run PASS count on same corpus.

### M4SN-6 — beauty self-host in mode-4

- [ ] **M4SN-6** — Run `test_gate_sn7_beauty_self_host.sh` with mode-4. beauty.sno parsed and run as mode-4 binary should produce byte-identical output to SPITBOL oracle. Gates: beauty_self_host PASS, smoke 7/7, beauty 17/17.

---

## Session Setup

```bash
git config --global user.name "LCherryholmes"
git config --global user.email "lcherryh@yahoo.com"
# repos already cloned: one4all, corpus, .github, x64
bash /home/claude/one4all/scripts/build_scrip.sh
make -C /home/claude/one4all libscrip_rt
make -C /home/claude/one4all out/sm_codegen_x64_emit_test
make -C /home/claude/one4all out/sm_phase2_sim_test
make -C /home/claude/one4all out/bb_flat_text_test
# Confirm HEAD
cd /home/claude/one4all && git log --oneline -1  # expect 4f0e2996 or later
```

**Mode-4 compile+link helper** (use this inline in scripts):
```bash
compile_mode4() {
  local sno="$1" out="$2"
  local tmp=$(mktemp -d)
  /home/claude/one4all/scrip --jit-emit --x64 "$sno" > "$tmp/p.s" 2>/dev/null || { rm -rf "$tmp"; return 1; }
  (cd /home/claude/one4all && gcc -c "$tmp/p.s" -o "$tmp/p.o" 2>/dev/null) || { rm -rf "$tmp"; return 1; }
  gcc "$tmp/p.o" -L/home/claude/one4all/out -lscrip_rt -lgc -lm \
      -Wl,-rpath,/home/claude/one4all/out -o "$out" 2>/dev/null || { rm -rf "$tmp"; return 1; }
  rm -rf "$tmp"
}
```

---

## Watermark

**HEAD** one4all `e2f94c6e` · Baselines: smoke_snobol4 7/7, jit_emit 11/13, beauty 17/17, crosscheck_sn4 6/6 ✅, crosscheck_sc 6/8, gate_em8 5/5 ✅.

Sess 2026-05-14 (Claude Sonnet 4.6): M4SN-0a/0b done; M4SN-3a fixed (two bugs in emit_sm.c: expression_registry missing fn .quad + DEFINE_ENTRY push rbp stack corruption). one4all `e2f94c6e`.

**Next:** M4SN-0c — EM-7c root cause (variant ARBNO got='abc' want='aXc'), then M4SN-1.
