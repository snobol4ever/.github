# FINDING seat15 — reprofile-after-byname-bake: beauty self-host still holds the TRUE fixed point at current HEAD (not the stale pinned md5 seat04/seat2 used); the SCRIP-vs-SPITBOL beauty ratio lineage is orphaned because BEAUTY-CN's `&`-constant conversion (landed the same day) means neither available SPITBOL oracle can parse it any more — independently cross-validated same-session by hq_P (`FINDING-...-hq_P-the-m1-board-grades-beauty-against-an-oracle-that-refuses-it.md`, the fuller and more consequential account: MILESTONE 1's own board misreads this as an all-RED regression), whose fix row this FINDING's own task now hands off to.

**Session:** 2026-08-23 seat15 (`/home/claude15`), THE LOOP queue row `reprofile-after-byname-bake`, rank 0 (fresh claim, protocol v2/picker-v2 — an earlier same-session claim on a *different* row, `table-int-keys-and-nd-subscript`, was released via `unclaim` after being traced to a stale pre-pull v1 picker; see that row's own LEDGER).
**Status:** Scoped deliberately narrow. This row's brief asks for the same re-profile-and-rerank deliverable `perf-board-rebaseline` (rank 0, DONE 2026-08-22, seat04) already delivered comprehensively (§0, §6 below flags the apparent row duplication to HQ rather than re-deriving it). What follows is what changed since that row closed, discovered by actually re-running the check rather than trusting the carried-forward number — twice, both times catching my own mistake before it shipped (§1, §3).
**SCRIP tree:** unchanged, HEAD `f704b1b1` (main, clean working tree, pristine-built once this session). `.github`/`corpus` pulled current before writing this (25 / 86 commits respectively — the corpus fetch target moved again mid-pull, see §1's own correction). No code touched anywhere, no `.s` regen owed.

---

## 0. Why this row still had open work after perf-board-rebaseline's DONE closure

seat04's own FINDING (§0) reported beauty self-host **still broken** at their HEAD `2659558e` — regression bisected to `62017f8a`, reconfirmed from scratch that session (md5 `1c75f97d1907f92f4c0a8a3ef49eb9ee`, the BAD "Parse Error"/`mainErr1` signature). Because of that live regression, their beauty-side profile had to use `0ff71be8` (last pre-regression commit) as a proxy, and their §8 item 1 flagged this explicitly: *"beauty's own Ir number cannot be trusted at HEAD until this is fixed."* My clone pulled 83 new SCRIP commits this session (their `2659558e` → my `f704b1b1`) — that is the one SCRIP-side fact that could have changed, so it is the one thing worth re-checking rather than re-deriving everything else in their already-DONE finding.

## 1. ⛔ SELF-CORRECTION: the first version of this check used a now-stale pinned md5, exactly the anti-pattern `board_beauty_m1.sh` was written to forbid

seat04's finding (and mine, on the first pass) treated `6f1671c0757729992ae01a6bdf16f081` as "the GOOD fixed-point md5" and diffed fresh output against that **string**. `board_beauty_m1.sh`'s own header is explicit that this is wrong practice for the actual M1 property: *"NO md5 IS EVER PINNED (GOAL-SNOBOL4-100 DOD item 2) — the oracle is re-run every time."* Lon's own commit `336f49d28` (corpus, 2026-08-22 17:48, same day as seat04's and seat2's sessions) — *"beauty.sno: reach the true self-host fixed point after the BEAUTY-CN promotion"* — rewrote the checked-in `beauty.sno` itself (622 → 630 lines, 40,971 → 41,492 bytes) specifically so that **the file is its own oracle** (Lon ruling s117, quoted in that commit message). The old pinned md5 describes text that no longer exists in the tree.

**I reproduced this exact mistake before catching it**: my first run (against a corpus checkout still 86 commits behind, pre-dating `336f49d28`) matched `6f1671c0757729992ae01a6bdf16f081` and I drafted a finding declaring the regression fixed on that basis. Pulling `corpus` current and re-running produced a **different** output that did NOT match the pinned hash — not a new regression, but the expected result of the reference text having moved. Caught by actually diffing against the live checked-in file instead of trusting a number carried in from another session's finding.

**The corrected check** (no pinned hash, matches Lon's s117 ruling and `board_beauty_m1.sh`'s own method): `diff <(./scrip beauty.sno < beauty.sno) beauty.sno` — **exits 0, byte-identical**, both plain and under callgrind, at HEAD `f704b1b1`, against the current 630-line checked-in text. **Beauty self-host is genuinely fine at current HEAD** — the `62017f8a` regression seat04 chased does not reproduce — but the evidence for that has to be "diff against today's checked-in file," not "match this string from yesterday's finding." Flagging this as a general risk for the perf-board lineage, not just this row: any DONE-WHEN or FINDING that pins a beauty self-host md5 will silently go stale the next time the checked-in file legitimately changes, and will read as a false regression (or, as very nearly happened here, a false non-issue) to whoever runs it next without checking. §7 below writes this row's own DONE-WHEN as a live diff for exactly this reason.

## 2. Fresh Ir total, current beauty.sno, `f704b1b1`, m3, RT_OPT=`-O0` — NOT COMPARABLE to the old lineage, and here is why

```
15,938,160,081 Ir   (callgrind, true fixed point confirmed both plain and under instrumentation)
```

Top of `callgrind_annotate --threshold=98`: `codegen_flat_chain_body` 3,412,006,692 (21.41%) · `zd_plan` 1,609,864,188 (10.10%) · `__strcmp_avx2` 1,478,820,723 (9.28%) · `zls_node_bytes` 1,063,641,507 (6.67%) · `zls_mark_value_refs` 645,342,180 (4.05%) · `cap_in_repeat_body` 574,314,498 (3.60%) · `bb_slot_get` 524,109,960 (3.29%) · `emit_label_intern` 473,182,476 (2.97%) · `zx_cmp` 438,674,561 (2.75%) · `bb_src_of` 415,998,017 (2.61%) · `meth_is_user_proc` 363,986,804 (2.28%, **runtime**) · `msort_with_tmp` 319,348,980 (2.00%). Same functions, same order, as every prior beauty profile in this lineage (seat1, seat04) — qualitatively nothing structurally changed.

**⛔ Do not diff this number against `15,870,550,520` (seat1, post-byname-bake) or `15,845,933,856` (seat04's `0ff71be8` proxy) and report a percentage.** Those measured a 622-line, 40,971-byte input. This measures the current 630-line, 41,492-byte input (+1.27% bytes) — commit `336f49d28` changed the workload itself, independent of anything SCRIP's compiler did, the same day those baselines were taken. A raw delta conflates "compiler got faster/slower" with "input got bigger" and would be exactly the kind of confident-but-wrong number ARCH-PERF-TOOLING.md §7 ranks measurement-integrity bugs above optimization work for producing. (For the same reason I am not reporting `meth_is_user_proc`'s count as a cross-session identity check the way I initially drafted — it isn't identical here, 363,986,804 vs seat04's 360,810,576, because the BEAUTY-CN conversion added by-name-relevant lookups to the program itself. Expected, not a compiler signal.) If a byte-comparable before/after number is wanted, it would have to be re-taken on both sides of `336f49d28` specifically, which is out of this row's scope.

## 3. ⛔⛔ No SPITBOL oracle on this box can run the current beauty.sno — CROSS-VALIDATED INDEPENDENTLY BY hq_P this same session, who found the bigger version of this and has already minted the fix row

Attempting the obvious next step — a fresh clean-SPITBOL Ir count on the current file, to replace seat2's `228,144,314` (measured against the same now-superseded 622-line text) — both available oracles fail identically:

```
$ sbl_clean_bin() [/home/resources/spitbol-bench-oracle/sbl] -bf beauty.sno < beauty.sno
$ sbl_correctness_bin() [/home/resources/x64/bin/sbl] -bf beauty.sno < beauty.sno
```
Both: **exit 0**. ⛔ **Correction made before this FINDING was pushed** (caught by inspecting stdout *content*, not just its byte count, on a re-check prompted by hq_P's finding landing mid-session — see below): the error is not silent and stdout is not empty. SPITBOL prints its real error **to stdout**, at rc=0:
```
.../beauty.sno(10) : ERROR 251 -- keyword operand is not name of defined
keyword


in file              .../beauty.sno
in line              10
in statement         2
stmts executed       2
...
REGENERATIONS        0
memory used (bytes)  217512
memory left (bytes)  831056
```
(393 bytes, plain run — matches `FINDING-...-hq_P-...` §2's own byte count exactly.) Line 10 is `&USER_DECLARED_CONSTANTS = 1`, the BEAUTY-CN conversion's opening declaration (corpus commits `53dd9ac0d`/`336f49d28`, 2026-08-22).

**This is a known, already-tracked language-support gap** — `ARCH-SN4-CONSTANTS.md` §"Oracle amplification": *"Extension programs are oracle-fail by construction"*; fix is the amplified oracle pair `sbl-x`/`csnobol4-x` (`GOAL-SCRIP-HQ.md` D-12/D-13, READY/queued). `FINDING-2026-08-22-seat07-beauty-cn-convert.md` already exercised this on a minimal witness and got the same `ERROR 251`.

**hq_P independently found the same mechanism this same session**, from a completely different angle (A/B-testing an unrelated codegen fix against the full gate ladder, noticed `board_beauty_m1.sh` reading 0/10 in both modes on the project's flagship milestone) and landed the fuller, more consequential account first: **`FINDING-2026-08-23-hq_P-the-m1-board-grades-beauty-against-an-oracle-that-refuses-it.md` — read that one, not this section, for the complete picture.** It correctly identifies the bigger stakes: `board_beauty_m1.sh` diffs this error text against expected output and reports **every rung DIFF, including the one-line rung** — a false all-RED on MILESTONE 1 itself, not just an orphaned perf ratio, and PLAN.md's HQ-CORRECTNESS row may currently carry a stale regression claim resting on exactly this. hq_P has already minted the fix row `m1-board-judge-is-a-refusing-oracle` and (via cross-session doorbell, arriving as this FINDING was being finalized) assigned it to me — picked up next, see this task's LEDGER.

**My own run cross-validates hq_P's independently, for what that's worth**: identical fixed-point byte count (**41,492**, exact match), identical failure line (10), identical error (`ERROR 251`) — two unrelated measurement paths, same session, same numbers.

**Consequence for THIS row's own original ask** (a current SCRIP-vs-SPITBOL beauty ratio): the entire chain — HQ's original "2.1x," seat2's clean-oracle "3.53x / 5.8x-equalized," the `806,084,475`/`228,144,314` pair — was built on the pre-`336f49d28` beauty.sno and cannot currently be reproduced against today's checked-in file by any oracle on this machine, pending `sbl-x`/D-12. Not a SCRIP regression and not an error in those earlier findings (correct for the text that existed when they ran) — the workload changed out from under the ratio, same day, for an unrelated reason. Any "which engine is faster" question that can't wait for `sbl-x` should route to seat04's other, unaffected measurement (`fibonacci.sno`, ~1.92x SCRIP-favorable — their §3a).

## 4. Composition/ranking verdict — unaffected by §§1–3, not re-derived

Nothing above changes which functions dominate beauty's compile-side cost, nor seat04's §5 (five-entry re-pricing) or §6 (by-name verdict on ~20 queued perf rows) — those were computed from the per-function *shares and mechanisms*, not from the beauty Ir total or a SPITBOL ratio, and remain valid. QUEUE.tsv has continued to churn heavily since their session (BOARD.md shows many rows CLOSED across many seats in the hours since) — **their §6 table should be read as "current as of 2026-08-22," not re-swept here**; not re-checked row-by-row against today's QUEUE.tsv, flagging the staleness risk rather than guessing.

## 5. ⛔ Flag to HQ — likely un-deduped row pair

`reprofile-after-byname-bake` and `perf-board-rebaseline` read as an un-deduped pair from the V2-2 prose→baton conversion — same trigger (byname-bake), same deliverable shape, apparently minted independently (possibly one each from hq_C/hq_P). Recommend HQ either retires this row citing `perf-board-rebaseline`'s FINDING plus this addendum, or states why they're actually scoped differently (not visible to me from either brief's text). Same posture as seat04's own §8 item 2 and seat13's `FINDING-2026-08-23-seat13-rung-e1-already-closed-by-free-r11-duplicate-queue-rows.md` (pulled this session, independent instance of the same class of defect) — flagging a cross-row inconsistency rather than unilaterally resolving it.

## 6. DONE-WHEN

This row's baton shipped with a permanently-refusing placeholder (hq_C: *"its old completion test was prose... write a command that can exit non-zero, then close"*). Written now as a **live diff against whatever is currently checked in**, not a pinned hash — the exact discipline §1 is about:

```
f=corpus/programs/snobol4/demo/beauty/beauty.sno; diff <(SCRIP/scrip "$f" < "$f") "$f" >/dev/null && test -f .github/FINDING-2026-08-23-seat15-reprofile-after-byname-bake-beauty-fixed.md
```

Verified with the exact invocation `done` itself uses (`cd "$S4E" && timeout 900 bash -c "$dw"`) before wiring it into the task file — passes. Contains `$f`/paths so `done`'s vacuity probe skips it (by design, per that probe's own carve-out for path-bearing commands); it would refuse in a pre-build/pre-checkout tree regardless (no `scrip` binary, no `.github` checkout). Necessary, not sufficient: re-checks the mechanical fact §1 rests on, not the judgement in §§2–5.

Row complete for this session's contribution. Handing off via `s4e_msg.sh done reprofile-after-byname-bake`.
