# FINDING-2026-08-12v — HOME-RBX X-3: census complete, `fc_alt_active` lands clean, `op_subj_cell` regresses 19/122 — root cause is `x86_fc_hit`, not the registration side

**Seat:** RBX. **Session:** fresh clone, this session (Claude Sonnet 5). **HEAD at measurement:** `5547de99` (moved past this file's `a037b637` reference point — three RBP-EARN commits touched `emit.cpp`/`x86_asm.h` in between: `4174782e`, `0954198b`, `e73f66b4`. Re-verified everything against the live tree per this file's own "TREE STATE IS READ FROM THE TREE" offer to RULES.md).

## Answers the s42 rung directly: "CENSUS THE CLASS BEFORE RE-WIDENING ANYTHING"

Every bare `x86_port_mode() == / != ZC_PORT_FORTH` in `emit.cpp` + `x86_asm.h`, current HEAD, producer traced for each:

| site | gates | producer | verdict |
|---|---|---|---|
| `emit.cpp:1381` `op_subj_cell` | subject-cell TOS-pop read | `zls_build` (`zeta_storage.c:430`) — zero port checks anywhere in the function | **mismatch, but see below — fixing it regresses** |
| `emit.cpp:1213` `fc_alt_active` | ALT fpmax read | `fc_alt_register`, called `lower_snobol4.c:1677` — gated only on `fc_linear`/`fc_walk_range`, zero port checks in that file | **mismatch, LANDED, verified safe** |
| `emit.cpp:1216` `fc_seq_on` | SEQUENCE cell read | `fc_seq_active()` → `{ return 0; }` unconditionally, SEQ-ERAD deleted the feature | dead, not a bug — the FORTH gate is moot |
| `emit.cpp:2076` `zd_plan` entry gate | whole ZD carve-planner | self-contained: same function grants+self-declines; output arrays (`zon`/`zout`/`zgpop`/`zwpop`) are locally `alloca`'d per call, not a persistent side-table like `fca[]`/`fvr[]` — nothing downstream can read a stale grant | consistent, cleared |
| `emit.cpp:2662` ZPOP-FOLD | trampoline ΣK accumulation | targets `x86_asm.h:2287`'s `X86H_JMP/OMEGA` hook (`add rsp,op_wpop`), itself port-blind — but `op_wpop` is staged ONLY by this same FORTH-gated fold. Cross-checked against §C.5 of this file: HEAP allocation is monotone bump-alloc, "ω emits nothing... never a pop." There is nothing to release under HEAP. | consistent by architecture, cleared |
| `emit.cpp:1014`/`1016` ARBNO K16 `_chain` | chained vs simple ARBNO layout | LOWER's admission gate `sno_arbno_chain_on()` (`lower_snobol4.c:885`) is *also* bare FORTH — "the s52 rsp linked-frame-chain is active (ZC_PORT_FORTH); the zcol default... cannot nest." Same condition at both ends. | consistent, cleared |
| `x86_asm.h:460`/`462` `x86_fc_on`/`x86_fc_hit` | — | — | already known — the s40b/s41 site itself, unchanged since the revert |

**Census is now closed.** Matched set was exactly two: `op_subj_cell`, `fc_alt_active` — both flagged by FINDING-2026-08-12p, neither previously verified.

## fc_alt_active — landed

Producer (`fc_alt_register`) genuinely port-blind, consumer widened from bare `x86_port_mode()==ZC_PORT_FORTH` to the new `fc_cells_active()` public accessor (see below). Measured BY SET, own-HEAD before/after (not the file's stale `a037b637` floors, which have drifted — see next section):

- FORTH: 84/122 before, 84/122 after. 0 REPAIRED, 0 BROKEN, identical failure-mode histogram.
- HEAP: 36/122 before, 36/122 after. 0 REPAIRED, 0 BROKEN.

Zero risk, currently zero corpus impact (nothing in `crosscheck/patterns` exercises a path where this particular mismatch produces observably different bytes) — but it is a real fix for a real bug and the accessor it needed is a legitimate, minimal, ONE-AUTHORITY-respecting addition (below). Landing it now per RULES.md's "commit and push freely," not holding a zero-risk fix hostage to the other half.

## op_subj_cell — attempted, measured regressive, REVERTED

Same fix shape (`x86_port_mode()==ZC_PORT_FORTH` → `fc_cells_active()`) on `emit.cpp:1381`. BY SET against the freshly-measured HEAP baseline:

```
[base_heap]  PASS 36 / 122   (59 DIFF, 22 SIG11, 3 HANG, 2 SIG6)
[patch_heap] PASS 19 / 122   (66 DIFF, 26 SIG11, 9 HANG, 2 SIG6)
REPAIRED: 0.  BROKEN: 17.
  038_pat_literal 039_pat_any 040_pat_notany 043_pat_len 044_pat_pos 045_pat_rpos
  050_pat_alt_two 051_pat_alt_three 053_pat_alt_commit 055_pat_concat_seq
  072_pat_star_var_alt_backtrack 073_pat_star_var_capture 074_pat_star_var_cursor
  155_pat_cap_output_order 156_pat_cap_alt_abandon_pop 170_pat_abort_kills_match 172_pat_fail_forces_retry
```

Isolated (fc_alt_active reverted to baseline, only this site changed): identical 19/122, identical 17-file set — confirms the whole regression is this one site, `fc_alt_active` contributes nothing to it either way.

**`038_pat_literal`/`039_pat_any` are the same two witnesses this file's own s42 cursor names** from re-testing s40b's *original, different* patch locally ("found two NEW small two-sided witnesses... both trivial single-primitive subject-position matches"). Two different code changes, same failure signature, on the same programs — that's not coincidence.

### Root cause: the census checked the wrong producer

`zls_build`'s registration (`fvr[]`/`fca[]` side tables) only marks *intent* — "this node is eligible for fc-cell treatment." Whether a value **physically lands at a TOS-poppable address** is a separate, downstream decision:

`FR`/`FRQ` (`x86_asm.h:1062`/`1087`) → `x86_zop` (`:1017`) → `x86_zop_regime` (`:1013`): `if (x86_fc_hit(off)) return 2;` — regime 2 is the only regime that resolves to `[rsp# + N]` (TOS-relative). Every other regime resolves to the flat `[rbp+off]`/`[rsp+op_flat_disp+off]` slot. And `x86_fc_hit` (`:462`) is **still bare `x86_port_mode() == ZC_PORT_FORTH`** — untouched since the s41 revert.

So under HEAP: `zls_build` registers the subject as fc-eligible (port-blind, as measured) — but the actual write, routed through `FR`/`FRQ`, never gets regime 2 (`x86_fc_hit` says no), so it lands at the flat slot exactly as it always did. My fix told the *consumer* to trust the registration and `pop` TOS anyway. There was nothing correct at TOS to pop — the real value sat at the flat slot the whole time, and the pop read whatever unrelated bytes happened to be on the stack.

**The registration/consumer mismatch (FINDING-2026-08-12p's framing) is real but not sufficient on its own to explain or fix this family.** `x86_fc_hit`/`x86_fc_on` are the actual physical authority, and they are the exact site s40b widened and s41 measured net-regressive (20/122 vs the 36/122 floor) and reverted. `op_subj_cell` and `fc_alt_active` are downstream of that same foundational gate; `fc_alt_active` happens not to route through `x86_zop_regime` for anything this corpus exercises, so widening it alone is safe. `op_subj_cell` routes through it directly via the literal TOS `pop`, so widening it alone is not.

**This adds direct, measured evidence to OPEN ASK #2 (this file, "IS X-3's RESIDENCE HALF ACTUALLY REQUIRED FOR HOME?"):** any further consumer-side fix in this family is capped in value until `x86_fc_hit`/`x86_fc_on` themselves move — already tried once, already reverted, still unresolved as a scope question for Lon. This session's result is a second, independently-derived data point for the seat's existing recommendation: **(i) X-3 = fork (a) only, stop, spend the seat on X-4/X-5.**

## Floor drift (own-HEAD, per STALE-ORIENTATION law)

FORTH baseline measured **84/122** this session vs the **77/122** this file had recorded at `69b51acc`/s41b — a +7 move, larger than the prior +1 drift noted at s41b but the same phenomenon: ordinary concurrent-seat movement, most likely from the three intervening RBP-EARN commits (`4174782e` WIRE-SAVE fix, `0954198b` EARN-1 frame_need_of, `e73f66b4` EARN-1 diag fix — all FORTH-side correctness fixes, consistent with a FORTH-only floor rise). HEAP baseline matched the recorded 36/122 exactly, unmoved. Recorded so the next seat doesn't read a phantom +7 as its own repair, mirroring this file's existing floor-drift note.

## What's in the tree now

- `SCRIP` — `fc_alt_active` fix landed: `src/emitter/emit.cpp` (one line), `src/contracts/zeta_storage.c` + `.h` (new public accessor `fc_cells_active()` — `fc_cells_on()` stays private per its own ONE-PORT-OPINION law; this is the one sanctioned external read, for future cross-file consumers in this family too). Committed locally, **not pushed** — credential pending per RULES 6b.
- `op_subj_cell` — reverted to HEAD exactly (`git checkout`), zero trace left in the diff.
- No `.s` artifact regen needed: the landed change is source-only, no corpus `.s` files were regenerated or need to be (RULES.md step 4 applies to codegen the session touched in ways that change compiled output — `fc_alt_active` measured byte-identical everywhere, so there is nothing to regen).

## RUNGS update

X-3 is unchanged (`[ ]`, still blocked on Lon's OPEN ASK #2 ruling) — this finding narrows *why* rather than closing it. The `fc_alt_active` half of the matched set is done; it was never its own rung line, just a census byproduct.

---

## ⛔ POST-WRITEUP CORRECTIONS (same session, before push — recorded rather than silently edited above)

**1. "Byte-identical" was an overclaim.** The BY-SET sweeps measure SET-IDENTICAL pass/fail, not emitted bytes. The commit message has been amended to say so explicitly. Byte-identity for `fc_alt_active` is UNVERIFIED. Offer to RULES.md: *a BY-SET sweep licenses "set-identical", never "byte-identical" — they are different claims and only one of them was measured.*

**2. The `.s` A/B that was supposed to verify #1 was CONFOUNDED, and the confound is the real headline.** Method: build `HEAD~1` in a worktree, compare `--compile` output. Result: 8/8 programs differed on BOTH ports, including FORTH where the change is provably inert (`fc_cells_active()` and `port==FORTH` are the same predicate under FORTH). Controls run: same-binary-twice = deterministic (so not nondeterminism); `make clean` full rebuild = same result (so not staleness). The actual diff was the RTCC arg-tier writeback stores — code this change cannot touch.

**Explanation, found in the reflog:** another seat was committing into the SAME clone. `HEAD~1` was not "my change minus one"; it was that seat's `RTCC RC-8b` landing. Every "byte difference" measured was their trim.

**3. This seat clobbered that seat's commit message.** Their `pull --rebase` moved HEAD; a `git commit --amend` intended for this seat's own commit rewrote theirs instead. Detected, original message recovered verbatim from reflog and restored as `9a85b10f`. Their hash moved from `04a1a577` — unavoidable after an amend, and a history rewrite in a clone another seat is actively using. **If that seat holds a reference to `04a1a577`, it is stale and must be re-derived.**

**4. Both seats independently did the whole RC-8b analysis in one session.** This seat's independent derivation (12 `x86("rtcc_wb")` sites catalogued with their bracketed calls; arg-tier slots 0/8/16/24/32 proven read by nothing codebase-wide — `rtcc_load_scratch()`, `keywords.c`'s ANCHOR companion write, and all three inline-asm reload sites in `rt.c`/`runtime_eval.c` touch only offsets 40+; `x86_rtcc_call()` has zero callers) reached the identical conclusion and the identical instruction count. Independent corroboration is worth something — but the duplication is a partition failure, and it is escalated as OPEN ASK #0 in `GOAL-SN4-HOME-RBX.md`.

**Standing lesson, offered for RULES.md:** *an instrument that spans two builds assumes the tree belongs to you. In a shared clone that assumption is false and fails SILENTLY — it produced a plausible, reproducible, clean-rebuild-surviving wrong answer. Read `git reflog` at orientation and before any history rewrite.*
