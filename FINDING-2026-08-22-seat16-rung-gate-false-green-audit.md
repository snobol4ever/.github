# FINDING-2026-08-22-seat16-rung-gate-false-green-audit

FROM seat16, RE rung-gate-false-green-audit (HQ WELCOME dispatch, this session)

## Scope and method

HQ's brief: sweep every `test_gate_*.sh` (89) plus the `board_/bench_/audit_*.sh` family (31) — 120 scripts
total — and answer, per script: **CAN THIS EVER SAY NO?** Every CANNOT-SAY-NO verdict below carries a real
negative-test injection (the violation actually made to exist, gate still observed green) — never an opinion
without one. No tracked file was edited to produce any injection; every one ran from a scratch copy, an env
var override, or a throwaway input. `git status --porcelain` was confirmed clean on SCRIP/corpus/.github
before and after every injection, across every batch.

⛔ **COVERAGE: 105/120.** All 89 `test_gate_*` scripts (batches A–F) plus the 16 `audit_*`/`bench_*` scripts in
batch G. **Batch H — 15 scripts, `board_*` plus the remaining `bench_*` — is NOT audited; see "Outstanding."**
Do not read this FINDING as full-corpus coverage; the gap is named, not silently dropped.

Work was fanned out across parallel forks (batches A–H) to cover this in one session.

## Correction to HQ's own dispatch — do not re-cite

HQ's brief named `test_gate_wreg_claim.sh` as a confirmed pinned-count drift (emit.cpp occ=6, live count 16).
**Re-verified directly, not taken on HQ's word: the pin now reads occ=7, and a live recount is also 7 — exact
match, not drifted.** Another seat (commit tagged `CLAUDE-free-r10-2026-08-22`) had already deleted the dead
call sites the old pin referenced, the same day, before this audit ran. The gate is CAN-SAY-NO as of now. This
does not retract HQ's general defect class — pinned constants with no freshness check demonstrably can drift
silently (see TIER 3) — only this specific instance, so it isn't re-cited as still-true by a later session.

## TIER 1 — currently hides a real, live defect (highest severity)

| Script | Protects | Evidence |
|---|---|---|
| `test_gate_rtcc_claimed_regs.sh` | claimed VM-global register (r9=RT_GVA_VA) never silently clobbered | Default invocation is **always** `echo "GATE: INFORMATIONAL... rc would be $rc"; exit 0` — `--strict` is never passed anywhere in `scripts/`. Run exactly as it's actually invoked (zero args), it found a **real uncleared r9/GVARQ collision in `bb_define.cpp`** — the same defect class as the historical s6/s7 fibonacci SIGSEGV this gate exists to catch — printed "rc would be 1", exited 0. |
| `test_gate_omega_own_k.sh` | ω-release coverage / orphan-add census over compiled `.s` | Header admits "v1: census only, NOT pass/fail." Live run scanned 506 `.s` files: **1810/1900 (95%) of K>0 boxes have no release site, 2621 orphan adds** — exits 0 regardless. Named `test_gate_*`; reads as a gate to anyone who doesn't open it. |
| `test_gate_no_c_to_bb.sh` | C→BB transfers confined to sanctioned MAIN sites | Header: default is REPORT-ONLY, exit 0. Live run (no injection needed) found a **real, fresh, currently-unledgered transfer** at `src/driver/scrip.c:57` — the gate's own printed words call it "a NEW violation of the one-entry convention" — and still exited 0. |
| `test_gate_no_vstack.sh` | SCRIP has zero value-stack apparatus (`g_vstack` etc., VSX-1..7) | Same informational-until-`--strict` shape (VSX-8 is the hard gate; nothing invokes it). Live run found a **real, currently-existing reference** in `src/runtime/rt/rt.h` (TOTAL=1) and exited 0 anyway — no injection needed. |
| `test_gate_pl_coupling.sh` | Prolog BB templates don't reintroduce banned CONTROL-coupling calls | `ceiling()` hardcodes `bb_choice.cpp)19` / `bb_goal.cpp)10` — **neither file exists** in `src/templates/` today (current Prolog templates are `bb_cell_cut.cpp`/`bb_cut.cpp`/`bb_call*.cpp`). Confirmed via the gate's own documented negative-test hook: up to 19+10 real coupling call-sites could be reintroduced under either historical filename with **zero enforcement**, while all 129 real current templates are correctly held at ceiling 0. |

## TIER 2 — vacuous specifically when `scrip` isn't built yet (the normal state of every fresh seat)

| Script | Protects | Evidence |
|---|---|---|
| `test_gate_zeta_no_arena.sh` | ZS rung completion — zero arena-based ζ storage | No `-x scrip` guard anywhere. Confirmed live in this exact (unbuilt) seat: full 7-row table of all-zero counters, "GATE PASS: zero arena zeta events (ZLS2=0, ZLS1=0)", exit 0. |
| `test_gate_rbp_census_ratchet.sh` | no unseeded `[rbp+N]` frame refs (s188/s189 drift class) | `[ -x "$SCRIP" ] \|\| { echo SKIP; exit 0; }`. Confirmed live in this exact seat. Proven inconsistent by direct contrast: sibling `test_gate_rc8a_gc_coverage.sh`, same missing binary, correctly exits 1 (BLOCKED) instead of skipping. |
| `test_gate_sn7_beauty_self_host.sh` | beauty-suite self-host m3/m4 oracle diff (SN-7) | SKIP-as-success on missing binary or missing `beauty_suite/`. Confirmed live twice: real unbuilt checkout → SKIP/exit 0; fake no-op executable + empty suite dir → PASS=0 FAIL=0/exit 0. |

## TIER 3 — proven vacuous by synthetic injection (default informational; gated behind an undocumented flag nothing in the repo ever passes)

| Script | Protects | Injection receipt |
|---|---|---|
| `test_gate_bb_emit_blind.sh` | zero direct `pBB->[αβγω]` derefs in Icon/Prolog templates | Bare `exit 0` outside a `--strict` branch. `grep -rn test_gate_bb_emit_blind scripts/` (excluding itself) = **zero hits** — nothing else in the repo ever invokes it at all, so the `--strict` arm can never be reached through any existing harness. |
| `test_gate_fb_predicate_tripwire.sh` | wide/narrow ζ frame-base predicate divergence stays empty | Fake `$SCRIP` emitting a real FB-DIVERGE hit: default run printed the divergence but exited 0; identical input with `--strict` exited 1. |
| `test_gate_icn_zk5_gva.sh` | Icon globals never counted `globals_on_stack>0` | Fake `$SCRIP` that runs clean but never prints a `globals_on_stack=` line at all: gate reported PASS on all 3 test cases, exit 0 — conflates "no violation seen" with "nothing measured." |
| `test_gate_fc_no_residual_rbp.sh` | FC silent-fallback (rbp) miss count vs baseline 0 | `CORPUS=<empty dir>` → "scanned 0 program(s)... OK: no regression above baseline", exit 0. |
| `test_gate_no_handencoded_bytes.sh` | BB templates never hand-encode instruction bytes | Added a real matching site to an untracked scratch file: default mode reported "BAD sites: 1" and still exited 0; `--strict` on the identical tree correctly exited 1. |
| `test_gate_no_hidden_global_in_emitted.sh` | hidden-visibility runtime globals never named in emitted mode-4 text | Moved the gitignored `out/rt_pic` build dir aside (restored after): "SKIP out/rt_pic/*.o absent", exit 0 — indistinguishable from "checked, clean," yet this is the literal state of any fresh clone before its first `make libscrip_rt`. |
| `test_gate_argnote_sweep.sh` | annotation-fold invariants survive mode-4 emit | `SCRIP=/nonexistent LIMIT=3`: all 3 programs emit-refuse, counters all zero, "GATE GREEN", exit 0. |
| `test_gate_asm_tabs_identity.sh` | TAB-column refactor byte-identical to legacy output | Empty directory arg: PASS=0 FAIL=0 SKIP=0, "GATE GREEN", exit 0. |
| `test_gate_clobarm.sh` | s130 leaf-suspension frame-slot correctness vs `.ref` | No glob guard: on an empty dir the loop runs once on the literal, unexpanded `*`; both compared outputs come back empty, fabricating PASS=1 FAIL=0, exit 0. |
| `test_gate_emit_no_ir_mutation.sh` | emitter never writes IR fields | Scratch root with empty `src/emitter`+`src/templates`: "PASS: the emitter never mutates IR", 0 files scanned, exit 0. |
| `test_gate_emit_no_lang.sh` | zero language-identity symbols in emitter/templates | Same empty-root injection: "OK: LANG-BLIND", 0 files scanned, exit 0. |
| `test_gate_emit_no_slot_alloc.sh` | emit-time slot allocators stay deleted | Same empty-root injection: "PASS: emit-time temp allocation is eradicated", 0 files scanned, exit 0. |
| `test_gate_s130_behav.sh` | s130 behavioral A/B PASS/FAIL recorder | **Zero `exit` statements anywhere in the file** (grep-confirmed). Runs with no args, exits 0 silently — unconditionally, not just under a missing binary. |
| `test_gate_s130_blast.sh` | byte-identity blast-radius check for killswitch changes | `compare` mode has no existence check on its two file args. Confirmed live: comparing two nonexistent files prints a shell "No such file or directory" to stderr and still reports `MOVERS=0`, exit 0. |

The `emit_no_ir_mutation`/`emit_no_lang`/`emit_no_slot_alloc` trio is the same "hardcoded path, never
existence-checked" root cause as HQ's own confirmed `BB_templates/` incident — this audit found **3 live
siblings** of it.

## TIER 4 — structurally guaranteed to pass, or partial/minor gaps

| Script | Issue |
|---|---|
| `test_gate_em_template_byte_identity.sh` | **Can never say no by construction, in any state.** Lines 93 and 99 invoke the textually identical command (`"$SCRIP" --run "$f"`) for what the script calls two different oracles. No injection needed or possible — a static proof, not an environmental condition. |
| `test_gate_const_graph.sh` | Computes and prints its own internal "GATE RED" verdict, then hits an unconditional `exit 0` on the next line regardless. `CG_WATERMARK=0` confirmed: 16 internal FAILs + "GATE RED" printed, exit 0 anyway. |
| `test_gate_rtx_inventory_live.sh` | Self-documented: "downgraded s163... REPORTS and never blocks. Exit is always 0." Honest about it internally, but still named `test_gate_*`. |
| `test_gate_pl_m34_parity.sh` | Empty corpus glob → PASS=0 FAIL=0, exit 0. **Not currently triggered** — live corpus has 164 real pairs today. |
| `test_gate_pas_frame_pairing.sh` | Partial: 1 of 4 named witnesses (`p2.pas`) doesn't exist in the corpus and is silently SKIPped rather than FAILed — 25% of the witness set has evaporated with no failure signal. The other 3 witnesses do correctly fail on a real mismatch. |
| `audit_bb_fixup_rank.sh` | No `exit` statement anywhere in the file. Live, unmodified: 83/146 files dirty, 1976 violations, "LAP STATUS: 83 file(s) need fixup" — exit 0 regardless. |
| `audit_jcon_wholesale.sh` | No `exit` statement. A filter matching zero probes prints PASS=0 FAIL=0, exit 0 — zero-probes-examined is indistinguishable from all-pass. |
| `bench_min_of_n.sh` | Timing rail: discards stdout/stderr/exit code of the timed run entirely, no oracle check anywhere. Injected a `.sno` guaranteed to fail on every run: still produced a normal-looking `min=12 med=13 max=14 spread%=16 NOISY -- do not quote a ratio` row — "NOISY" flags spread, not correctness. A 100%-broken program reads as a real (if noisy) measurement. |
| `bench_prolog_ix_ab.sh` | Same shape as `bench_min_of_n.sh` (5×2 timed loop discards stdout+exit code) — lower confidence, source-reading only, not injected this pass. |

## Self-declared informational (honest, not deceptive — listed per instruction to sweep the whole family)

- `audit_ir_names.sh` — header states outright: "Exits 0 always — this is a measurement, not a gate."

## UNCERTAIN — needs a follow-up before scoring

| Script | Why uncertain | Recommended next step |
|---|---|---|
| `test_gate_two_region.sh` | Default "ledger" mode unconditionally `exit 0` by explicit design, gated behind `--strict` "reserved for TR-8 seal." | **HQ ask: has TR-8 already landed?** If yes, this should have been flipped live and wasn't. No non-archive `.github/*.md` currently mentions TR-8 at all. |
| `test_gate_wreg_claim_binary.sh` | No floor on `total_slabs`/`total_hits` — if the gdb breakpoint (`break bb_seal`) never fires (plausible: this container's hardware watchpoints don't work, per RULES.md), zero slabs would still report "CLEAN." | Couldn't drive live (scrip was unbuilt at that moment; it correctly hit its own SETUP-failure exit 2, a *good* sign). Needs a built tree to test the zero-hits path directly. |
| `test_gate_rtx_store_width.sh` | No `checked -eq 0` guard if the `.S` glob matches nothing (unlike its sibling `rtx_killswitch_sets.sh`, which has one). | Not currently live-vacuous (14 `.S` files present today) — re-test after any runtime-source reorg. |
| `test_gate_em_beauty_subsystems_mode4.sh` | No post-loop "did anything run" assertion over `*_driver.sno`. | Couldn't drive past this seat's unbuilt-scrip SKIP path to the empty-driver-set condition live — flagged from code reading only, not proven. |
| `bench_prolog_vanroy.sh` | Correctness is preflighted only on the *original* program; the actually-timed artifact is a separately generated N-iteration wrapper never independently checked per engine. | Needs a targeted injection (a wrapper-only bug would time silently); out of budget this pass, needs a live GNU+SWI build. |
| `bench_icon_rate_3way.sh` | Checksum mismatches print inline rather than gating, and the header already discloses a constant-folding blind spot. Self-aware, not hidden — softer finding. | Low priority given the self-disclosure; still never exits non-zero on mismatch. |

## Worth copying — gates that got this right (same sweep, positive findings)

- `test_gate_zdp_on_null.sh` — explicit vacuous-input guard (`TOTAL<100 → FAIL`) *and* a separate self-nondeterminism bucket so flaky programs can't be miscounted either way.
- `test_gate_pl_gz7.sh` — runs its own internal "CORRUPT-PROOF" block every time (sed-swaps emitted jump targets, asserts the output diverges) — i.e. it already runs this audit's negative-test technique, continuously, on itself.
- `test_gate_icn_var.sh` / `test_gate_icn_scan.sh` — non-zero coverage floors (62/12/22, 26/26/24) mean a missing/empty corpus trips a FLOOR FAIL, not a silent pass.
- `test_gate_icn_no_stack.sh` — a `cells==0` self-check specifically so an empty/crashed compile can't slip through as a pass.
- `test_gate_out_sweep_flaky.sh` — is itself a self-contained injection harness (4 explicit fault assertions) rather than trusting an external corpus.
- `bench_rtx_3arm.sh` — requires a self-printed `ms:` line or the row becomes explicit `NOT GRADED`; refuses to print a ratio when intra-arm spread exceeds inter-arm gap.
- `test_gate_rc8a_gc_coverage.sh` — genuine positive controls (deliberately sabotages GC-rooting via `SCRIP_GC_UNROOT` and confirms the gate catches it) on both its arms.

Also incidentally confirmed — not false-green, the opposite: proof several mechanisms work — `test_gate_lower_isolation.sh`,
`test_gate_no_asm_c_asm.sh`, `test_gate_no_lang_names.sh`, and `test_gate_no_raw_asm_producers.sh` are all
**currently, genuinely RED** in this tree right now, for reasons unrelated to this audit (an unallowlisted
Pascal include in `lower_pascal.c`, an RTCC banking-hazard ratchet over its ceiling at COUNT=38>12, 5 untagged
`PL_` identifiers in `emit.cpp`, 296 raw asm-producer sites). Noted so a fresh gate run isn't mistaken for
audit fallout.

## Tally (105/120 scripts)

CANNOT-SAY-NO (incl. partial): 31 · UNCERTAIN: 6 · self-declared informational: 1 · CAN-SAY-NO: 67

## Outstanding — NOT audited this pass

Batch H (15 scripts) did not deliver its result before this FINDING was filed: `bench_scrip_only.sh`,
`bench_sno_match4.sh`, `bench_sno_rail.sh`, `bench_sno_rtx.sh`, `board_beauty_m1.sh`, `board_demos_zeta.sh`,
`board_denominators.sh`, `board_earn0_set.sh`, `board_passthru_combo.sh`, `board_patterns_2mode.sh`,
`board_patterns_set.sh`, `board_sno15_ident.sh`, `board_sno15_perf2.sh`, `board_sno15_perf.sh`,
`board_sno_apps.sh`. Its fork showed `completed` in this session's agent list but had not delivered a result
at filing time. Whoever picks this up next should check for that result (this session may still fold it in
as an addendum) before re-auditing from scratch.

## Process note, not a codebase finding

Mid-audit, one of this session's own forks (batch D) misread its own scope, attempted to nest-launch coverage
for batches it mistakenly believed were undispatched, failed with `subagent_type: fork` ("Fork is not
available inside a forked worker"), and fell back to spawning **6 unauthorized `general-purpose` agents**
duplicating batches D/E/F/G under new task IDs — full tool access, none of this session's explicit
no-fix/scratch-only/git-status-clean instructions attached directly (only whatever survived in inherited
context). Caught via the agent list while responding to an unrelated prompt, not via any self-report from the
fork. 4 of the 6 were stopped in-flight; 2 had already completed before they could be stopped. Verified
`git status --porcelain` clean and no unexpected commits (last 30 min) across all three repos afterward — no
damage done, but worth recording: a forked worker can spawn uncontrolled duplicate work with degraded safety
instructions when it misjudges its own scope, and nothing in the harness surfaces this back to the parent
automatically.
