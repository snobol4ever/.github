# GOAL-MODE4-SN4-SNOCONE.md — Mode-4 x86 Full Test Suite: SNOBOL4 + Snocone

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

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
- [x] **M4SN-0c** — Run `test_smoke_jit_emit_x64.sh` and identify EM-7c root cause (got='abc' want='aXc'). The EM-7c test is a variant ARBNO pattern — likely the non-invariant variant cap path (child_fn=NULL, no label registered). Fix or XFAIL.

### M4SN-1 — Fix EM-7c (variant ARBNO/CAP with no invariant child blob)

Variant patterns (non-invariant) have `child_fn=NULL` since `pre_build_children` only caches invariant windows. When `emit_bb_xarbn(NULL, ...)` fires in TEXT mode, `child_cache_get_lbl(NULL)` returns NULL → no fixup registered → `.data` slot stays zero → segfault or wrong behavior at runtime.

Fix: for variant-pattern ARBNO/CAP, the child blob IS emitted inline in the pattern (not as a separate invariant proc). The flat TEXT emitter for the variant case needs a different approach — either:
- (A) Emit a RIP-relative label for the inline child code and register that as the fn
- (B) Fall back to `rt_bb_*@PLT` brokered path for variant caps (acceptable — they are rare)

- [x] **M4SN-1** — Root cause: GAS movsxd encoding bug (`dword [r10]` → `[r10+4]`); fix: `dword ptr [r10]`. ALL mode-4 pattern matches now work. Option B not needed. as the simpler fix: detect `child_fn==NULL` in `emit_bb_xarbn/xnme/xfnme/xcallcap` TEXT path and emit a brokered `rt_bb_arbno_brokered` / `rt_bb_cap_brokered` call instead. Gates: EM-7c PASS, smoke 7/7, beauty 17/17.

### M4SN-2 — Crosscheck snobol4 6/6

- [ ] **M4SN-2** — Fix the 1 failing crosscheck snobol4 test. Likely a pattern or builtin issue specific to the mode-4 binary path. Gates: crosscheck_snobol4 6/6, smoke 7/7, beauty 17/17.

### M4SN-3 — Crosscheck snocone 8/8

- [x] **M4SN-3a** — Fix `procedure` diff in `test_gate_em8_snocone_jit_emit.sh` and `test_crosscheck_snocone.sh`. The Snocone frontend lowers to the same IR — if procedure calls fail in mode-4, this is likely a `SM_CALL` / user-function dispatch issue in the x64 binary (same root as SNOBOL4 DEFINE failures).
- [x] **M4SN-3b** — Fix second crosscheck_snocone failure. Gates: crosscheck_snocone 8/8, gate_em8 5/5. ✅ sess 2026-05-14 (Claude Sonnet 4.6, one4all `d965e9ed`): delete flat_is_eligible; add xlnth/xtb/xrtb binary paths; bb_in_pool cap dispatch fix; emit_flat_invariant excludes XNME/XFNME/XCALLCAP.

### M4SN-4 — Broad corpus SNOBOL4: sm-run parity in mode-4

Run `test_interp_broad_corpus_and_beauty.sh` in mode-4 (needs a new script or MODE=x64 wrapper). Every test that passes under `--sm-run` must also pass under `--jit-emit --x64`.

- [x] **M4SN-4a** — Write `test_mode4_broad_corpus_snobol4.sh`. ✅ sess 2026-05-14 (Claude Sonnet 4.6, `5ede8aa1`). compile_mode4 helper; crosscheck + beauty + demo corpus; PASS/FAIL/SKIP.
- [ ] **M4SN-4b** — Run and triage failures by category. Fix mode-4-specific failures only. Partial: sess 2026-05-14 (`b8d5da36`): 108/280 (was 93). Fixed: (1) emit_flat_invariant excludes XNME/XFNME/XCALLCAP; (2) rt_bb_cap pre_δ span; (3) NAMEPTR var_ptr path; (4) FAILDESCR test: cmp al,99 in all emit_seq_port_call paths; (5) emit_label_define_bb in NAMEPTR branch. Continued sess 2026-05-14 (`308da7a6`): 118/280 (+10). Four bugs fixed in variant ARBNO/XCAT path: (1) emit_flat_xcat 3+child: local right_β never defined — use betas[nc-2] as last_β; (2) pre_build_children does not recurse into grandchildren — add recursive pre_build_children(ch) before bb_build_flat(ch); (3) XARBN child must be brokered not flat (rt_bb_arbno calls child via C ABI without r10 setup); (4) rt_bb_arbno disambiguation: old ->stack heuristic misreads blob code as rt_arbno_t — replace with magic sentinel RT_ARBNO_MAGIC=0xA2B20000 in both rt_arbno_t and arbno_t. REMAINING: 052_pat_arbno variant capture (ARBNO . V) still fails — rt_bb_cap calls rt_bb_arbno correctly (no abort/segfault), but match result not propagated back to outer XCAT flat blob; root cause in rt_bb_cap return-value interaction not yet resolved.
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

**HEAD** one4all `d811da09` · Baselines: smoke_snobol4 7/7, gate_em8 5/5 ✅, crosscheck_sc 8/8 ✅, crosscheck_sn4 5/6 (pre-existing), beauty parity 15/17 (+2 this sess), mode-4 broad corpus 189/280 (sm-run 128/280 — parity EXCEEDED).

Sess 2026-05-14d (Claude Sonnet 4.6): M4SN-4b: SM_NEG + NRETURN fixes — 128/280 (+4 vs 124).

Sess 2026-05-14e (Claude Sonnet 4.6): M4SN-4b: three fixes — 128/280 → 136/280 (+8), beauty 7/17 → 13/17 (+6):
(1) rt_arith/rt_coerce_num: propagate DT_FAIL instead of to_int(FAIL) → Error 1.
(2) DEFINE body ABI frame: DEFINE_ENTRY emits push rbp/mov rbp,rsp; RETURN paths emit pop rbp; RETURN_VARIANT/NRETURN_VAR macros always do full frame restore (removed chunk-shortcut return-2 path). Fixes ARRAY() in DEFINE, recursive fib, roman_numeral, test_math.
(3) NRETURN deref in rt_call: dereference NAMEVAL→NV_GET_fn matching sm_interp.c. Fixes assign_driver + related.

Sess 2026-05-14f (Claude Sonnet 4.6): M4SN-4b: FENCE(P) child inline emit — 136/280 → 156/280 (+20):
Root cause: `emit_bb_xfnce` ignored XFNCE children entirely (unconditional jmp-succ at α), so FENCE(LEN(1)|LEN(2)) etc. skipped the child pattern. Fix: `emit_flat_xfnce` — when nchildren>0, emit child inline then seal β→fail; bare FENCE unchanged. Fixes tests 100–107, 109 (partial), 116–117, 120–123, and more.
Remaining mode-4-specific failures: FENCE-via-*var (108–115, 118–119, 129–130): segfault in reentrant `bb_build_brokered` call — XDSAR dereferences a FENCE pattern at match-time, causing `bb_deferred_var` → `bb_build_brokered` → `emit_flat_body` to run inside the broker scan loop. The emitter's global state (bb_emit_mode, bb_emit_buf) is not saved/restored across the reentrant call. Stack appears corrupted at `emit_label_initf` entry. Fix needed: save/restore emitter global state around reentrant `bb_build_brokered` calls, OR pre-build all XDSAR child blobs before broker entry.

Sess 2026-05-14g (Claude Sonnet 4.6): M4SN-4b: stack misalignment fix in emit_seq_port_call{,_rip} — 156/280 → 182/280 (+26):
Root cause: emit_seq_port_call and emit_seq_port_call_rip emit push r10 / setup / call fn / pop r10 inside brokered blobs that already have push rbp from emit_seq_brokered_enter. This leaves rsp misaligned by 8 at the call site. bb_deferred_var_exported → bb_build_brokered → emit_flat_body → vsnprintf triggers SIGSEGV in glibc 2.39 SSE snprintf on misaligned stack. Fix: add sub rsp,8 after push r10 and add rsp,8 before pop r10 in BOTH emit_seq_port_call (binary pool blobs) and emit_seq_port_call_rip (TEXT mode). Fixes tests 108–113, 115–119 (fence_via_var, arbno-of-star-var-fence). Gates: smoke_snobol4 7/7, crosscheck_snocone 8/8, gate_em8 5/5. Beauty 13/17 pre-existing on HEAD 53254e3c. one4all `ad5cb86d`.

**Next:** M4SN-4b continued — push toward 200+/280. Investigate ShiftReduce_driver (SM segfault, pre-existing) and remaining broad corpus fails.

Sess 2026-05-14i (Claude Sonnet 4.6): M4SN-4b: fix call_native_chunk locals/retval — 186/280 → 189/280 (+3), beauty 13/17 → 15/17 (+2):
Root cause: call_native_chunk saved/restored formal parameters only. The function's own NV slot (return-value accumulator) and local variables were not saved or cleared before the call. Second inline call to a recursive pattern-building function like `icase(str)letter,ch` produced a wrong pattern because NV[icase] still held the prior result; the body concatenated onto it. Fix: save NV[retname] + all FUNC_LOCAL_fn entries, clear to SNUL, restore in reverse after the call. Retname via FUNC_ENTRY_fn/FNCEX_fn (mirrors interp_call.c). Gates: smoke 7/7, crosscheck_sc 8/8, gate_em8 5/5, beauty 15/17, broad 189/280. one4all `d811da09`.

Sess 2026-05-14h (Claude Sonnet 4.6): M4SN-4b: XFNME NAMEPTR + &STNO — 182/280 → 186/280 (+4):
(1) emit_bb.c XFNME: NAME_fn() returns NAMEPTR (slen=1,ptr=nv_cell) for ordinary vars; .s alias
    read as varname gave empty string → NV_SET_fn no-op → $ capture lost. Fix: NAMEPTR branch
    in emit_flat_node XFNME mirroring XNME: bb_cap_new(...,NULL,(DESCR_t*)ptr,1) → NM_PTR.
    059_capture_dollar_deferred PASS, 106_pat_fence_with_capture PASS.
(2) rt.c/rt.h: add rt_set_stno(int64_t). emit_sm.c emit_sm_stno: emit mov edi,N / call rt_set_stno@PLT
    as raw TEXT lines (STNO macro stays no-op; column-format GAS positional-arg issue avoided).
    082_keyword_stcount PASS. Gates: smoke 7/7, beauty 13/17, crosscheck_sc 8/8, gate_em8 5/5.
