# FINDING-2026-08-23-seat10-rung-gate-false-green-audit-continued

FROM seat10, RE rung-gate-false-green-audit (continuing seat16's FINDING-2026-08-22 audit + hq_P's V2-5 cure
of the 31 gates it found — this is the SAME row, carried forward across the V2-2 task-baton conversion).
FLEET MODE confirmed live at time of writing (ARCH-FLEET-CEO.md CURRENT MODE line: FLEET-16 as of s266).

⚠️ **This FINDING was itself interrupted once and resumed.** An earlier pass of this same session wrote a
version of this document, got cut off before filing rows or closing the task baton, and left it uncommitted.
This version supersedes it: one entry below (`test_gate_m1_self_host_fixed_point.sh`) has been **corrected**
from that draft (it had wrongly called the gate CAN-SAY-NO), and the coverage tally has been **recomputed by
`comm`/`wc -l` set arithmetic** rather than trusted from any hand-typed summary — which, fittingly for this
audit, took two tries to get right. The draft's own "42/56" didn't match its own content (actual was higher).
Then THIS document's own first pass also mis-stated the pool size as 56 when the actual `comm -23` output
computed earlier in the session (101 total `test_gate_*.sh` minus 44 mentioned anywhere in seat16's FINDING or
the V2-5 pinned list) is **57**, and separately undercounted `covered` by missing that `test_gate_fz_release.sh`
and `test_gate_port_functions.sh` already had real, evidenced, filed rows from this same session's earlier
(interrupted) pass. Every number in "Coverage status" below was re-derived with three explicit set files
(`pool57`, `covered`, `core-IR dispatched`) and a printed arithmetic identity (`33 + 14 + 10 = 57`), not
retyped from memory. Treat any prior verbal summary of this row's coverage — including this session's own
earlier messages — as superseded by this document.

## Scope and method

seat16's original sweep covered 105/120 scripts (the 89 `test_gate_*.sh` that existed then, plus the 16
`audit_*`/`bench_*` scripts) and named 31 CANNOT-SAY-NO. hq_P's V2-5 (`FINDING-2026-08-22-hq_P-v2-5-thirty-one-gates-can-now-say-no.md`)
cured all 31 and pinned them in `scripts/test_gate_gates_can_say_no.sh` as a permanent ratchet (re-verified
live this session: 31/31 REFUSED on an empty tree, 0 vacuous — still true at time of writing).

Two gaps remained, neither previously touched:
1. **Batch H** — 15 `bench_*`/`board_*` scripts seat16's own FINDING named as undelivered ("Outstanding"). Now 15/15 audited.
2. **The 56 `test_gate_*.sh` scripts** that had grown to 101 total (vs the 89 seat16 audited) and were never
   mentioned by name anywhere in seat16's FINDING or the V2-5 pinned list. By direct enumeration against this
   document's own content: **29 of 56 audited, 27 remain** (see "Coverage status" at the end — 14 of the 27 are
   an in-flight background fork not yet returned at time of writing; 13 are not yet dispatched to anyone).

Method: identical discipline to seat16/hq_P. Per script: **CAN THIS EVER SAY NO?** A CANNOT-SAY-NO verdict
requires a real negative-test injection (the violation actually made to exist, script still observed green),
never an opinion without one — except where a static/structural proof is conclusive on its own (no branch in
the file can reach a nonzero exit; the em_template_byte_identity / s130_behav precedent from seat16's audit).
No tracked file was edited to produce any injection — every one ran from a scratch copy under the session
scratchpad or an environment-variable override the script already supports (verified per-script which one
applies — `test_gate_icn_one_reg_frame.sh` hardcodes its path relative to `$0` and does NOT respect
`S4E_HOME`/`CORPUS`-style overrides the way most gates do; a scratch *copy of the script itself* was required
to test it, and an env-var attempt against the real tree silently no-ops instead of erroring, which is itself
worth knowing before trusting any override-based injection against an unfamiliar gate). `git status --porcelain`
verified clean in SCRIP before and after every batch. Work was fanned out across parallel forks; each was
explicitly forbidden from spawning further sub-agents (seat16's own FINDING recorded a fork mis-nesting into 6
unauthorized general-purpose agents; this session hit the same "Fork is not available inside a forked worker"
error repeatedly from the **top level** while dispatching against a system-wide-busy 19-session FLEET-16 run —
confirmed via the harness's own agent roster, not assumed — so some planned coverage did not launch and is
named as outstanding below rather than silently dropped).

## NEW CANNOT-SAY-NO — confirmed by live injection or exhaustive static proof, ranked

| Script | Class | Evidence | Severity |
|---|---|---|---|
| `test_gate_m1_self_host_fixed_point.sh` + its probe `.github/probes/m1-bisect/check_m1_fixedpoint.sh` | argument-validation gap | The probe sets `rc=0` once, then runs `case "$ARM" in m3\|both) ...` and a **separate** `case "$ARM" in m4\|both) ...`. Any `$ARM` value other than exactly `m3`, `m4`, or `both` — a typo, wrong case, anything — matches **neither** pattern; both blocks are skipped entirely, `rc` never leaves its initial 0. Live, unmodified, no scratch copy needed: `bash .github/probes/m1-bisect/check_m1_fixedpoint.sh bogus-arm` → `M1 FIXED POINT HOLDS (bogus-arm)`, exit 0, having compiled and run **nothing**. The wrapper propagates it identically: `bash scripts/test_gate_m1_self_host_fixed_point.sh bogus-arm` → `M1 GATE: PASS`, exit 0. Neither script validates its own argument against the three-value contract its own usage comment documents. | **HIGHEST** — this is the gate for the project's single headline correctness claim (Milestone 1: beauty self-host is a byte-identical fixed point). The wrapper's header explicitly says it was written *because* "a milestone with no gate is a milestone nobody is defending" and even hand-documents the missing-binary case being handled correctly — the argument-validation gap sits right next to that fix, unexamined. An earlier pass of this same audit read only the missing-binary path and wrongly called this gate CAN-SAY-NO; this correction supersedes that. |
| `test_gate_baton_donewhen_runnable.sh` | blocklist evasion by decoration | Blocklists exact strings `true`/`:`/`exit0`/`/bin/true` after stripping whitespace. `DONE-WHEN: exit 0 # nothing to verify`, `: ok, done`, and `echo done` all parse as shell, resolve as a real command (`exit`/`:`/`echo` are real builtins), and are NOT exact string matches for the blocklist — all three sail through as "runnable" in a live scratch-postoffice run (`S4E_POSTOFFICE=<scratch>`, 3 evasions + 9 filler batons: `examined 12 baton(s): runnable=12 UNCLOSEABLE=0`, exit 0). Positive control confirmed the gate correctly catches literal `true` and real prose in the same run. | **HIGH** — this is the meta-gate meant to stop exactly this disease (per hq_P's own FINDING, which flagged the underlying hole but reported it "source-verified... not executed"); every row across the whole fleet depends on a DONE-WHEN this gate is supposed to have vetted. |
| `test_gate_pascal_m3.sh` / `test_gate_pascal_m4.sh` | zero-work-scanned reads as green | `CORPUS=<empty dir>`: unexpanded glob runs one literal iteration, hits NOREF, never increments FAIL. Both: `PASS=0 FAIL=0 NOREF=1 XFAIL=0`, exit 0. | **HIGH** — a corpus-path typo or unpopulated clone reads as a clean pass on both media. |
| `test_gate_icn_rbp_census_ratchet.sh` | dir-exists guard, not contents-exist | `[ -d "$BENCH" ]` passes on an empty dir; unexpanded `*.icn` glob is passed literally to the census tool, which reports `C_data=0 D_scratch=0 drift=0 OK`, `RATCHET_C=0`, exit 0 — indistinguishable from "37,872→0 directive fully met." | **HIGH** — load-bearing SNOBOL4-directive-parity gate for Icon. |
| `test_gate_icn_one_reg_frame.sh` | dir-exists guard, not contents-exist | Re-verified independently this pass (first attempt used the wrong injection method — `S4E_HOME` override silently no-ops since this gate hardcodes `SRC="${HERE}/../src"`; corrected by copying the script itself into a scratch tree with an empty `src/templates/`). Confirmed live: `sites=0`, script prints **"RATCHET IMPROVED: 0 < 22 — lower HANDBUILT_RATCHET... to lock the gain in"** then "OK: both locks hold", exit 0. | **HIGH** — actively recommends ratcheting a ceiling down based on scanning nothing; acting on the message would entrench a false "target reached" permanently. |
| `test_gate_em_beauty_subsystems_mode4.sh` | zero-work-scanned reads as green + never migrated to V2-5 | Doesn't source `lib_gate.sh`, not in the V2-5 pinned worklist. `for sno in "$BEAUTY"/*_driver.sno` with a populated-but-non-matching directory: `PASS=0 FAIL=0 (emit=0 link=0 diff=0)`, final line `[ "$((FAIL_EMIT+FAIL_LINK+FAIL_DIFF))" -eq 0 ]` → exit 0. Resolves seat16's own UNCERTAIN entry for this script to CONFIRMED (they couldn't drive past the unbuilt-scrip SKIP path; scrip is built in this tree now). | **MEDIUM-HIGH** — the mode-3/mode-4 parity gate for the entire beauty driver family; an accidentally-emptied or renamed driver set reads as full agreement. |
| `test_gate_raku_zframe.sh` (Invariant A) | any-nonzero-rc conflated with the-specific-expected-failure | No `-x $SCRIP` guard, fixed (non-overridable) `$SCRIP` path. `SCRIP=/nonexistent/scrip`: witness command fails with rc=127 (command not found, not the expected class-B killswitch bomb), gate's `[ "$RC" -ne 0 ]` treats it as "bomb reproduced correctly." | **MEDIUM** — masked today because scrip is normally built, but a fresh/broken-build seat gets a false OK on the one invariant meant to prove the killswitch works. |
| `board_patterns_2mode.sh` | zero-work-scanned reads as green, no distinguishing tag | Real `exit 1` prerequisite guards exist (better than TIER2 precedent), but the corpus loop has no nullglob/floor. `PAT_CORPUS=<empty dir>`: zero per-file rows print, summary shows `TOTAL 0 AGREE 0 m4-only-fail 0 m3-only-fail 0 both-fail 0` — uniform zeros, no `NO-REF`-style tag distinguishing it from a perfect run. | **MODERATE** — this is the board specifically meant to catch *silent* m3/m4 divergence; its own empty state is silent in exactly the same way. |
| `bench_scrip_only.sh` | structurally cannot fail + zero-work-scanned | Zero `exit` statements in the file. `CORPUS_SRC=<empty dir>`: all 10 programs fail to open, table prints `scrip-m3(--run)=0/10 scrip-m4(--compile)=0/10 m3==m4 byte-identical=0/10`, exit 0. | **MEDIUM** — same shape as seat16's `bench_min_of_n.sh` (TIER4). |
| `bench_sno_match4.sh` | env-var empty-check evasion | `PROGS=" "` (a single space) defeats `${PROGS:-default}` (bash treats only unset/`""` as falling back, not `" "`): zero output lines, exit 0 — silent, contentless success, worse than a printed all-zero table. | **MEDIUM** — a subtle shell-quoting-class bug distinct from the usual empty-glob shape. |
| `bench_sno_rtx.sh` | zero-work-scanned reads as green | `BENCH=<empty dir>`: all 3 family programs print MISSING (the `continue` never touches `FAILED`), summary footer still prints, exit 0. | **MEDIUM** — this corpus has precedent for programs being retired mid-flight, so this is not a hypothetical trigger. |
| `board_sno15_ident.sh` | structurally cannot fail | Full file read (71 lines) + `grep -n exit`: exactly one exit statement in the whole file, a setup guard (missing `lib_oracle_flags.sh`). Nothing is keyed to the pass/fail counters; the last statement is an unconditional `echo`, always rc 0. | **HIGH** — the script's own header documents "13 broken demo-board programs" historically under this exact board, i.e. it has already reported DIVERGE/HANG/CRASH rows while exiting 0. |
| `test_gate_fz_release.sh` | SKIP-as-success on missing prerequisites | `[ -x "$SCRIP" ] || { echo SKIP; exit 0; }` and `[ -d "$FZ" ] || { echo SKIP; exit 0; }` — structurally identical to seat16's already-convicted TIER2 siblings (`test_gate_zeta_no_arena.sh`, `test_gate_rbp_census_ratchet.sh`, `test_gate_sn7_beauty_self_host.sh`), all cured under V2-5; this one was never migrated. Confirmed by direct code reading, not independently re-injected (the class is proven elsewhere many times over). Dormant today (scrip built, corpus/probe/fz exists) but fires on any fresh/unbuilt seat. | **MODERATE** — a known, already-cured-elsewhere class recurring in one gate the cure missed; not in the V2-5 pinned worklist so nothing prevents regression. |
| `test_gate_port_functions.sh` | zero-work-scanned reads as green (missing-dir variant) | `find` over `src/templates`/`src/emitter` with no existence check. Scratch root with neither directory present: `find` prints "No such file or directory" to stderr ×2, script continues, `total=0`, "OK: all port operations route through the four port functions.", exit 0. Same root-cause class as the historically-convicted MEDIUM_* "grepped a deleted directory" incident. | **MODERATE** — `GOAL-SRC-REORG.md` is a currently active goal, so a src/ reorg landing mid-flight is a real, not hypothetical, trigger. |
| `test_gate_template_medium_invisible.sh` | informational-until-a-flag-nothing-ever-passes (partial) | Its FIRST check (raw-byte-producer / medium-branch census across all `src/templates/*.cpp`) is honestly self-labeled "Informational WIP baseline; --strict enforces zero" — but across every real invocation found (`grep -rn "test_gate_template_medium_invisible.sh" scripts/*.sh` → `test_gate_icn_var.sh`, `test_gate_icn_scan.sh`; plus `/home/resources/postoffice/tasks/rung-E3-xa-flat.task.md`'s own DONE-WHEN, which calls it as one of two live gates guarding that rung's closure) **none pass `--strict`**. The xa_flat DONE-WHEN's primary check (a direct `grep` for `r1[01]` registers) still correctly gates the rung's main concern even without `--strict` on the secondary check, and that row is `STATE -> SUPERSEDED` as of today — so this is not live-blocking anything right now, but it is a second confirmed real-world call site relying on the non-enforcing arm, not just the two report-scraping ones. Live, unmodified, on the real tree right now: default invocation reports 8 real hits in `xa_flat.cpp`, prints the WIP disclaimer, exits 0; `--strict` on the identical tree correctly exits 1. The gate's SECOND check (the BOTH-MEDIUM ratchet over `bb_*.cpp` specifically) is NOT gated behind `--strict` and does enforce unconditionally (currently 0/0, clean) — so the gate as a whole is not vacuous, only its broader, older half is. | **MODERATE** — RULES.md cites this gate's `--strict` arm as enforced ("Gates: greps == 0; scripts/test_gate_template_medium_invisible.sh --strict green"), which is easy to misread as "continuously checked"; it is not, in any real invocation path. The 8 live `xa_flat.cpp` hits are not a new defect — they belong to the already-active `rung-E3-xa-flat` row (seat06, OPEN on today's BOARD) — this is a finding about the *gate's* enforcement, not a new code bug. |

## Structural finding, not live-triggered today (recorded, lower priority)

- **`test_gate_wreg_claim_binary.sh`** — `total_slabs`/`total_hits` are computed and printed but never checked
  against a floor before the CLEAN verdict; if gdb ever fails to hit `bb_seal` (wrong symbol, stripped binary,
  gdb/version mismatch), zero slabs would still print "BINARY MEDIUM CLEAN." **Not currently triggered** — the
  mechanism was run live this session (`--quick`, 3 programs) and correctly found real, pre-existing debt
  (`mov N(%rcx),%r10`/`%r11` in D09/D12/X02, unallowlisted shapes, exit 1) — that red is genuine and belongs to
  the already-active `free-r11`/WREG-eradication lineage, not a new unfiled defect. Static proof only; no live
  reproduction attempted (would require defeating a working gdb mechanism).

## UNCERTAIN

| Script | Why uncertain | Recommended next step |
|---|---|---|
| `bench_sno_rail.sh` | Identity between SCRIP and SPITBOL is diffed only once at N=4; `arange` then scales the actually-timed artifact up to N=16384 with no re-diff at the timed scale. | Same shape as seat16's `bench_prolog_vanroy.sh` entry — needs a real scale-dependent divergence to force live. |
| `test_gate_sno_pat_reg.sh` | If `src/templates/bb_match_*.cpp` ever globbed to zero files, both tiers would read 0/pass — not tested live because the template family being empty is practically implausible. | Low priority; flagged for completeness only. |
| `test_gate_pl_no_new_global.sh` | Real, live-confirmed defect, but the injection proved a **false RED**, not a false green: with none of its 8 target paths present in a scratch tree, `PL_FILES` comes back empty, and `grep -rhoE ... $PL_FILES` with `$PL_FILES` empty silently falls back to scanning the current directory, reporting fabricated violations against nothing real. The same root cause could in principle also produce a false CLEAN in a cwd with zero `g_*` text, but that direction was not demonstrated. | Add `[ -n "$PL_FILES" ] || exit 2` before the grep, drop `-r` (targets are already explicit). |
| `test_gate_rtcc_block_coverage.sh` | The per-register round-trip census (one of the gate's own stated 3-part invariant) is computed and printed but not wired into the FAIL verdict. Self-disclosed in the gate's own text as a deliberate division of labor with sibling gates — not independently injected to confirm. | A human familiar with the RTCC rollout should confirm the split is intentional. |

**Incidental, unrelated to false-green (flagged per seat16's convention so it isn't mistaken for audit fallout):**
`test_gate_pl_gz2.sh` produced a genuine, pre-existing, unprompted RED on a plain live run — "hello m4 .s lacks
gzq labels (GZ path not taken)", exit 1 — the gate correctly catching a real defect. Not chased (out of scope);
belongs wherever Prolog GZ-rung work is tracked.

## Confirmed CAN-SAY-NO / SELF-DECLARED-INFORMATIONAL (positive findings, not defects)

`test_gate_queue_is_an_index.sh` (verified live: malformed QUEUE.tsv with a missing baton + bad field arity
both correctly caught, exit 1) · `test_gate_icn_global_no_nv_m3.sh` · `test_gate_icn_local_no_nv.sh` ·
`test_gate_icn_semicolon_required.sh` · `test_gate_icn_tag_single_source.sh` · `test_gate_icn_zcells_gva.sh` ·
`test_gate_kw_direct.sh` · `test_gate_kw_static.sh` (positive example: already guards the exact empty-glob
defect that broke both Pascal gates above) · `board_beauty_m1.sh`, `board_demos_zeta.sh`,
`board_denominators.sh` (self-declared, no aggregate verdict claimed) · `board_earn0_set.sh`,
`board_passthru_combo.sh` (empty state visibly tagged NO-REF/REDS) · `board_patterns_set.sh` (diff utility, no
pass/fail claim) · `board_sno15_perf.sh`, `board_sno15_perf2.sh`, `board_sno_apps.sh` (X-DIV/NOISY honesty
mechanisms, explicitly disclosed methodology) · `test_gate_wreg_claim_binary.sh`'s core detection mechanism
(mechanism verified working live, modulo the floor gap above) · `test_gate_pl_gz2.sh` through `pl_gz6b.sh`
(uniform `cmd || fail` harness, negative admission probes; gz2 verified live for real, siblings by structural
analysis) · `test_gate_pl_no_value_stack.sh` check 1 (recursive forbidden-pattern grep, no floor issue) ·
`test_gate_rtcc_callee_class.sh` · `test_gate_rtcc_noclob_injection.sh` (self-contained positive+negative
control, "worth copying" tier — same bucket as `pl_gz7.sh`'s CORRUPT-PROOF block) · `test_gate_rtx_ctor_armed.sh`
(three-arm control/trap/repair, verified live: A=ARMED B=DISARMED C=ARMED exactly as designed).

Minor, non-blocking note: `board_sno_apps.sh`'s header claims "FIVE whole-application demos" but only 4 `run`
calls exist — a stale count, not a correctness issue.

## Coverage status (computed by enumeration against this document's own content, not typed as a summary)

**Batch H: 15/15 audited** (`bench_scrip_only`, `bench_sno_match4`, `bench_sno_rail`, `bench_sno_rtx`,
`board_beauty_m1`, `board_demos_zeta`, `board_denominators`, `board_earn0_set`, `board_passthru_combo`,
`board_patterns_2mode`, `board_patterns_set`, `board_sno15_ident`, `board_sno15_perf2`, `board_sno15_perf`,
`board_sno_apps`) — a further independent re-verification of this batch via 3 parallel forks was dispatched
this session; not yet returned at time of writing, will be folded in as an addendum if it surfaces anything
this document doesn't already show.

**The never-mentioned `test_gate_*.sh` pool is 57 scripts, not 56** (101 total today minus the 44 mentioned
anywhere in seat16's FINDING or the V2-5 pinned list — `comm -23`, computed, not retyped). Of those 57:

**33 audited by name**: `test_gate_baton_donewhen_runnable`, `icn_global_no_nv_m3`, `icn_local_no_nv`,
`icn_one_reg_frame`, `icn_rbp_census_ratchet`, `icn_semicolon_required`, `icn_tag_single_source`,
`icn_zcells_gva`, `raku_zframe`, `kw_direct`, `kw_static`, `m1_self_host_fixed_point`, `queue_is_an_index`,
`template_medium_invisible`, `pascal_m3`, `pascal_m4`, `sno_pat_reg`, `rtx_ctor_armed`, `rtcc_block_coverage`,
`rtcc_callee_class`, `rtcc_noclob_injection`, `pl_gz2`, `pl_gz3`, `pl_gz4`, `pl_gz5a`, `pl_gz5b`, `pl_gz5c`,
`pl_gz6`, `pl_gz6b`, `pl_no_new_global`, `pl_no_value_stack`, `fz_release`, `port_functions`. The last two were
found by this same session's interrupted first pass (real, filed, evidenced rows already existed for them —
`fz-release-skip-as-success.task.md`, `port-functions-empty-src-false-ok.task.md`) but had been mislabeled
"never dispatched" in this document's own previous revision; folded back in here.

**24 remain, in two buckets, and 33 + 14 + 10 = 57 (checked, not assumed):**
- **14 dispatched, in flight, not yet returned**: `test_gate_ir_field_discipline`, `ir_tmp_slots`, `no_bb_bin_t`,
  `no_brokered`, `sm_dead`, `stage2_isolation`, `runtime_isolation`, `rbx_quarantine`, `zpop_whitelist`,
  `rtx_killswitch_sets`, `bb_one_box`, `call2bb_stub_regime`, `me6_reentry_hazard`, `udc`. A background fork
  has been running this group for 10+ minutes under heavy system-wide FLEET-16 load; will be folded in as an
  addendum on return, or left for the next session if this one ends first.
- **10 never dispatched to anyone**: `test_gate_ec_uni_complete`, `em8_snocone_native_emit`, `end_only_program`
  (may already be resolved — cross-reference `FINDING-2026-08-22-seat05-end-only-program-aborts-witnesses-cleared-and-gated.md`
  before re-auditing from scratch), `fb_adopt_one_predicate`, `fleet_protocol_e2e` (hq_P already adversarially
  poked at this once and could not break it — a fresh angle would be needed, not a repeat), `instr_budget`,
  `oracle_bf_capable`, `postoffice_identity`, `preflight_complete`, `s4e_picker_v2`. Attempts to dispatch these
  this session failed at launch (system-wide agent-spawn capacity), not from any finding about the scripts
  themselves — genuinely untouched, named here so the gap is visible rather than silently dropped.

## Rows filed this session (16 total, QUEUE.tsv ranks 0-4)

`m1-fixedpoint-arm-validation` (rank 0, HIGHEST — new this pass) · `donewhen-decorated-noop-evasion` (rank 1,
HIGH) · `em-beauty-subsystems-empty-driver-glob`, `pascal-m3-empty-corpus-false-pass`,
`pascal-m4-empty-corpus-false-pass`, `icn-rbp-census-empty-dir-false-ok`,
`icn-one-reg-frame-empty-dir-false-ratchet`, `board-sno15-ident-no-exit-path`,
`port-functions-empty-src-false-ok` (rank 2, HIGH) · `raku-zframe-rc127-conflated-with-bomb`,
`board-patterns-2mode-empty-corpus-silent`, `bench-scrip-only-no-exit-statement`,
`bench-sno-match4-progs-space-evasion`, `bench-sno-rtx-empty-dir-all-missing-ok`,
`fz-release-skip-as-success` (rank 3, MODERATE) · `wreg-claim-binary-no-slab-floor` (rank 4, LOW — structural,
not currently live-triggered). All 16 verified indexed in `QUEUE.tsv` with a matching task baton
(`test_gate_queue_is_an_index.sh` green at 127 rows, 0 bad-arity, 0 missing-baton, 0 prose).
