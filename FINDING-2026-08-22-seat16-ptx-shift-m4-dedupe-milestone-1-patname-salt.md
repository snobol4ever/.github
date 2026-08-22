# FINDING 2026-08-22 (seat16) — `ptx-shift-m4`: DOES NOT REPRODUCE AT HEAD, DEDUPE OF FINDING-2026-08-21-s197 (MILESTONE 1 PAT$ SALT)

**One sentence:** the m4-only silent-nomatch defect named by queue row `ptx-shift-m4` (`ptx_shift_alt_arms{,_2layer}` + `ptx_shift_chain_3layer`, s179 "not this class") is the SAME defect `FINDING-2026-08-21-s197-milestone-1-both-modes-the-wall-was-one-unsalted-name.md` already fixed at SCRIP `1f6cea4d` — unsalted runtime `PAT$` mints colliding with a mode-4 image's static `PAT$` names — confirmed here by direct killswitch A/B on the *same* binary, not by inference from commit messages.

## Standing state at pristine HEAD (SCRIP `2659558e`)
All three named witnesses PASS both modes, repeatably (5x rerun on `ptx_shift_alt_arms`, zero flake):
```
ptx_shift_alt_arms          m3=PASS  m4=PASS
ptx_shift_alt_arms_2layer   m3=PASS  m4=PASS
ptx_shift_chain_3layer      m3=PASS  m4=PASS
```
`.sno`/`.ref` history confirms no tampering: each pair has exactly one commit ever (`a5a566a4`, s178 mint) — the fix is in the compiler, not a rewritten oracle. Full `board_passthru_combo.sh` (every `corpus/probe/passthru/{pt,ptc,ptx,ptw}*` witness, both modes): `ptx` class **5/5** (the 3 named witnesses + the 2 `ptx_bare_mid_*` controls), board total 170/182 m4 — the 12 reds are all `ptw_min_*` (arbno/altrec/opsyn/rseal), an unrelated pre-existing family, none in the `ptx` class.

## Attribution method: git bisect + direct killswitch A/B, not narrative
The brief's own QUEUE.tsv note said the bug "persists at -O0 pristine" as of an earlier session (this claim's own prior holder). Reproduced that exactly at SCRIP `23ec6e29` (s194, still inside the s179-named red window) via a git worktree + pristine build: m3 PASS / m4 `nomatch` rc=0, **zero** SH output — matches the brief's "no SH fires, no diagnostics" verbatim, on all three witnesses, in three independent worktrees spanning `2a06ad0a`/`656431d1`/`23ec6e29` (ruling out the two same-day m4-alpha-seal fixes as the cure — both landed and both left this red).

Bisected forward from `23ec6e29` (good-role, ancestor, bug present) to main HEAD `2659558e` (bad-role, descendant, bug absent) with `git bisect run` over a script that grades all 3 witnesses' m4 `.ref` diff (92-commit range; automated run in the background under heavy 16-seat build-box contention, several minutes per pristine rebuild). The automated run narrowed the window to `0b8e8fbf` confirmed still broken (`all_pass=0`) with 2 revisions left; rather than grind through the remaining slow steps I built the one candidate its own commit message already named — SCRIP `1f6cea4d`, `0b8e8fbf`'s immediate child, titled "MILESTONE 1 COMPLETE — BOTH MODES" — directly in a fourth worktree:
```
0b8e8fbf  (Milestone 1, mode 3 only)          m4: nomatch rc=0, all 3 witnesses   <- automated bisect result
1f6cea4d  (Milestone 1, BOTH MODES, =s197)    m4: PASS, all 3 witnesses           <- built + tested directly
```
Killswitch confirms causation on that exact commit, same binary:
```
1f6cea4d  SCRIP_PATNAME_SALT=1 (default)      m4: all 3 PASS
1f6cea4d  SCRIP_PATNAME_SALT=0                m4: all 3 -> nomatch rc=0  (bug returns verbatim)
```

## Why this is the same defect, not a coincidental fix
s197's mechanism section names the exact symptom on its own witness `corpus/probe/fw/fw_stmt_skeleton.sno`: a mode-4 image's runtime `EVAL` road (`eval_build_chain` → `lower_snobol4` → `sno_pat_thunks_build` → `rt_proc_set_fn`) re-mints unsalted `PAT$0..` over the image's own static `PAT$` names, and the registration SHADOWS the static entry — every static defer slot resolving through that name fires the WRONG fragment. s197, verbatim: *"the two static `*PC()` slots fired the two runtime `*SH(...)` thunks — static slot k = runtime mint k."* Our three `ptx_shift_*` witnesses are s179's own characterization realized: *"EVAL-built shift patterns = the beauty skeleton shape"* — the identical `DEFINE('SH(t,v)')` / `shift = EVAL("p . thx . *SH('"t"', thx)")` deferred-callout-inside-an-EVAL'd-pattern construct as `fw_stmt_skeleton`, exercised at 2 and 3 layers of `*X` chaining instead of `fw_stmt_skeleton`'s own topology. Both families collide on the identical unsalted counter for the identical reason; s197's cure (salt runtime `PAT$` mints exactly as `EXPR$` already was) fixes both without distinguishing them — which is exactly what the killswitch A/B above demonstrates directly.

Two same-day, same-mechanism-sounding candidates were checked and ruled OUT by direct build+test, not assumed innocent: `656431d1` (APPLY-SNODEF-M4, general by-name-to-DEFINE'd-proc sealing) and `23ec6e29` (M4-ALPHA-SEAL, zero-arg deferred-call sealing) both left all three witnesses red — neither touches the PAT$-naming road our 2-arg `*SH('...', thx)` calls actually take (an EXPR$-thunk-fragment lookup, not the bare-name zero-arg road either commit's own text scopes itself to).

## DONE-WHEN, checked against the brief
- **Minimal witness pair:** the 3 standing `corpus/probe/passthru/ptx_shift_*` files (unchanged since their s178 mint) ARE the witness set the brief names; no new minimization was needed since the defect and its cure are already fully characterized by s197's own witness (`fw_stmt_skeleton`) — minting a fourth near-duplicate would add nothing.
- **Root-cause FINDING:** this document + the pre-existing `FINDING-2026-08-21-s197-milestone-1-both-modes-the-wall-was-one-unsalted-name.md` it dedupes to.
- **Green m4 if killswitch-clean:** confirmed above, both directions, on the fixing commit itself.
- This row required **zero code changes** — SCRIP and corpus are unmodified (verified `git status` clean in both before and after).

## Receipts (SCRIP `2659558e`, pristine, RT_OPT `-O0`)
- `test_corpus_snobol4.sh`: m3 357/2, m4 355/2/2skip (FAIL-M3 `160_pat_alt_inner_gen_resume` + `demo_treebank`; SKIP `132_pat_fence_eps_recur_shallow` + `demo_porter`) — same fail-set class other standing cursors already log as pre-existing/deliberate (`demo_treebank` is a known-deliberate red).
- `test_smoke_snobol4.sh`: 7/7 both modes (HARD GATE m4 7/7).
- `board_beauty_m1.sh --modes both`: m4 **10/10 ⭐M1-FIXED-POINT** (unchanged, PLAN.md DoD item 2 intact); m3 3/10 first-red-10 is the same pre-existing HEAD-churn drift seat09's cursor already named — unrelated to this row, m3 was never broken for these witnesses.
- `test_gate_emit_no_lang.sh`: OK. `test_gate_template_medium_invisible.sh`: 0 BOTH-MEDIUM sites in `bb_*.cpp` (ratchet ceiling 0); the standing 8-site `xa_flat.cpp` WIP debt is untouched, informational-only.
- Bisect scratch work (3 A/B worktrees + the automated `git bisect run` + the direct 1f6cea4d worktree) was done entirely in `/tmp` scratch worktrees, never in the tracked checkout; `git worktree list` / `git status` confirm the tracked SCRIP tree is untouched and still at `2659558e` throughout.

## Recommendation
Retire queue row `ptx-shift-m4` as a dedupe of the already-closed `m4-fragment-lowering-parity` (FINDING-2026-08-21-s197). No further action needed on this row; if HQ wants a permanent regression lock beyond `board_passthru_combo.sh`'s existing coverage of the `ptx` class, that is a new row, not this one.
