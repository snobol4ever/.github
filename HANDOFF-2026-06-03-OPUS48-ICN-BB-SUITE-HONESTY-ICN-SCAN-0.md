# HANDOFF-2026-06-03-OPUS48-ICN-BB-SUITE-HONESTY-ICN-SCAN-0.md

**Goal:** `GOAL-ICON-BB.md` — ICN-SCAN ladder, first two steps.
**Session focus:** SUITE-HONESTY (rc-aware rung suite + honest re-baseline) → ICN-SCAN-0 (registerize the `?` scan env).
**Commits:** SCRIP `991a26b` (SUITE-HONESTY) + `f13838f` (ICN-SCAN-0); `.github` `f15ae42a` (goal file, both steps marked, watermark prepended).

---

## What landed (all verified, gates green)

### SUITE-HONESTY — `991a26b`
- `scripts/test_icon_rung_suite.sh` `run_corpus` now captures `run_prog`'s rc: **rc≠0 without the `[SMX]` banner ⇒ FAIL in EVERY mode (m2 included)**, even when stdout matches `.expected` (verbose prints `FAIL name (rc=N)`).
- `run_prog`'s compile arm returns nonzero (was `return 0`) on emit/as/gcc failure so m4 failures are rc-visible. `[SMX]`-before-rc ordering in `run_corpus` keeps loud declines classified EXCISED.
- Kills the `rung36_jcon_proto` vacuous pass (rc=134 abort, empty stdout vs empty `.expected`, counted PASS in all 3 modes). Note the abort site moved since the original diagnosis — it now dies at `[lower2] UNHANDLED kind=107` → "main BB graph not found" (peer `715daa5` shifted it; vacuous condition identical).
- **Gate verified surgically:** per-mode PASS-set diff shows the ONE vacuous passer as the ONLY change in every column; EXCISED counts byte-identical (152/91); zero genuine regressions.
- **HONEST THREE-MODE BASELINE:** m2 **129**/118/36 (the HARD GATE is now 129) · m3 **13**/82/**152 EXC** · m4 **20**/136/**91 EXC**. The four LIVE "m2 130" gate references in the goal file are updated to 129; historical watermark entries keep their as-was numbers.

### ICN-SCAN-0 — `f13838f`
- `src/runtime/builtins/gen_runtime.h/.c`: `ScanEntry` += `sigma/delta/Delta`; **`rt_icn_scan_enter(lo,hi,sigma,delta,Delta)`** pushes the caller's live r13/r14/r15 on the scan ledger and returns the coerced subject `{ptr,len}` in rax:rdx (`ScanSubjRegs`); **`rt_icn_scan_leave(uint64_t *out3)`** pops (restoring `&subject`/`&pos`) and writes the prior triple through `out3`.
- `src/emitter/BB_templates/bb_gen_scan.cpp`: ENTER glue (op_sb=1) marshals subject DESCR slot → rdi:rsi + current triple → rdx/rcx/r8, then sets **Σ=r13←rax, Δ=r15←rdx, δ=r14←0 (pos=1)**. LEAVE glue (op_sb=2) `lea rdi,[r12+op_off]` → call → reloads r13/r14/r15 from the 24-byte frame out-area. Pure `x86()`, 0 raw-byte producers.
- `src/emitter/emit_bb.c`: `flat_drive_scan_glue` gains `regs_off` (carried in `op_off`); `flat_drive_gen_scan` claims the out-area once per scan node via `bb_slot_claim(24)` (unbound — does NOT shadow a future scan-result slot).
- **Design keystone: paired enter/leave IS the callee-saved preservation.** Net effect on r13–r15 across every gated scan shape is identity, so the flat-chain prologue (saves only r12) needed NO change. This is WHY the ledger carries the triple.
- SYNC CONTRACT (δ↔`scan_pos`) trivially holds at this rung — no native box writes δ yet, so δ==scan_pos−1 is invariant through the body. It becomes load-bearing at ICN-SCAN-7/8 (tab/move).
- m2 oracle untouched: its `IR_GEN_SCAN` arm manages the env inline and never called enter/leave (verified by grep before changing signatures).
- **Verified:** rung05 scan_subject + scan_concat_subject m2==m3==m4; nested probe `"outer" ? ("inner" ? write(&subject))` → `inner` m2==m3==m4 (the triple round-trip); sequential two-scan probe → `a`,`b` m2==m3==m4 (post-leave caller state intact). Corpus ALL THREE columns byte-identical to the honest baseline — zero PASS-set drift in any mode.

---

## Footguns surfaced (for future probe-writers)
1. **This parser needs explicit `;` statement terminators.** A bare-newline two-statement `procedure main()` silently drops the second statement in ALL modes (`write(1)\nwrite(2)` prints only `1`). A /tmp probe without semicolons mimicked a regression until checked at the parent commit. Corpus programs all use `;`.
2. `--rung` filter globs `${RUNG}_*.icn` — `--rung rung36` works, `--rung rung36_jcon_proto` matches nothing.

## Standing peer condition (not Icon, not this session)
`test_gate_template_medium_invisible.sh --strict` is RED on **343 sites, ALL in the Prolog-lane `bb_builtin_*` family** — the documented peer WIP (same condition the `e09dcc2`-era watermark recorded). `bb_gen_scan.cpp` has 0. The gate's own banner tags it informational-WIP-baseline.

## Peer commits rebased under, both orthogonal, re-verified after each
- `715daa5` (pre-session): SNOBOL m2 IR_CALL FNCEX/APPLY registry — moved NO Icon numbers (BEFORE re-measured = `d46b943` baseline exactly).
- `62426a6` (mid-session): Prolog PT-0/1a/2a predicate-table substrate.

---

## Next session entry point — ICN-SCAN-1
`bb_keyword` register arms: inside a native scan, `&pos` = `lea rax,[r14+1]` packed INTVAL straight into the slot (no rt call); `&subject` marshals Σ/Δ → rt string-DESCR helper → slot. m2 keeps `rt_icn_keyword_*`. Gate: same rung05 probes byte-identical. Then ICN-SCAN-2 (nine IR kinds + routing + loud EXCISE). Canonical sources are extracted at `SCRIP/refs/icon-master/` + `refs/jcon-master/` (re-extract the uploaded zips if absent); `fstranl.r`/`fscan.r` semantics summarized in the goal-file ladder header.

## Files changed this session
- `scripts/test_icon_rung_suite.sh` — rc capture + compile-arm nonzero returns.
- `src/runtime/builtins/gen_runtime.h` — ScanEntry triple, `ScanSubjRegs`, new prototypes.
- `src/runtime/builtins/gen_runtime.c` — enter/leave bodies.
- `src/emitter/BB_templates/bb_gen_scan.cpp` — register-loading ENTER/LEAVE glue.
- `src/emitter/emit_bb.c` — `flat_drive_scan_glue` regs_off; `bb_slot_claim(24)` per scan.
- `.github/GOAL-ICON-BB.md` — both steps `[x]`, four live 130→129 gate refs, watermark ×2.

## Gates at handoff (all measured at `f13838f`)
m2 corpus **129 (HARD, byte-identical PASS-set)** · m3 13/82/152EXC · m4 20/136/91EXC · Icon smoke m2 12/12 (HARD), m3 5/12, m4 5/12 · Prolog smoke m2 5/5 · unified-broker 32 · bb_bin_t=0 · no-handencoded `--strict` PASS · no-vstack PASS · icn-no-stack PASS · icn-one-reg-frame PASS · prove_lower2 PASS · FACT bytes-outside-templates 0 · bb_gen_scan.cpp raw-byte producers 0.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
