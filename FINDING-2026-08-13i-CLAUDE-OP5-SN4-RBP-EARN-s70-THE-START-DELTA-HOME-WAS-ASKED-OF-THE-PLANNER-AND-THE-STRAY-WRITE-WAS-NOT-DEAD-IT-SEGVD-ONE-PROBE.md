# FINDING 2026-08-13i — CLAUDE-OP5 — **s68's HALF-LANDED PREDICATE WIRED: THE START-δ HOME QUESTION WAS BEING ASKED OF THE PLANNER'S CARVE AUTHORITY, AND THE RESULTING "STRAY" WRITE WAS NOT DEAD — IT SEGV'D A PROBE.**

**Fingerprint:** SCRIP `0ef28ee0` (code) + `caed718a` (feature regen) · corpus `190b44b3` (benchmark regen) + `5282cece` (demo regen). Measured on the tree AFTER a concurrent `pull --rebase` brought in s68 `89b39492` + `4e183a1f`; every number below was RE-MEASURED at that HEAD (see CONCURRENCY, last section).

---

## ⛔⭐⭐⭐ THE INHERITED TREE WAS PRE-STAGED AND THE UNWIRED PREDICATE WAS A LOADED GUN

A fresh clone of SCRIP presented HEAD `f207d8f2` (s65e MATCH-RBP) with **two uncommitted lines** in the working tree — the definition (`emit.cpp`) and declaration (`emit.h`) of `emit_match_owns_startd()`, both citing **s68**, a session later than anything in the log. **Measured caller count: 0** (2 references tree-wide, being the decl and the def). s68 diagnosed a real defect, minted THE ONE AUTHORITY for it, and ended before wiring it to a single consumer.

**That predicate is not optional hygiene, and leaving it unwired is not a neutral state.** See the repair below.

## THE DEFECT — TWO PREDICATES, TWO QUESTIONS, AND MATCH-RBP IS WHERE THEY DIVERGE

`bb_match_defer.cpp` and `bb_match_value.cpp` both guarded their start-δ writeback on `!emit_match_begin_stfh_k()`. That is the **PLANNER's** predicate — "how many bytes must the depth model account?" — and MATCH-RBP *deliberately* zeroes it through the s65e wrapper, because the rbp frame releases itself. But these two sites are asking the **HOME** question: *does MATCH_BEGIN already own start_δ?* That is TRUE for **both** head-frame flavors (legacy carve → HKD, mrbp frame → `[rbp-40]`).

| graph class | `stfh_k()` | guard fires? | writeback target | correct? |
|---|---|---|---|---|
| stfh legacy | 64 | no | — (MATCH_BEGIN owns HKD) | ✓ |
| carve-less legacy | 0 | yes | `FR(op_scan_head_off)` = its real home | ✓ |
| **MATCH-RBP** | **0** (wrapper) | **yes** | `FR(op_scan_head_off)` — but home is `[rbp-40]` | ✗ |

Same spelled-twice disease `FINDING-2026-08-09g` named for the CARVE, recurring for the HOME.

## ⭐⭐⭐ THE WRITE WAS NOT DEAD — 139 → 0, ORACLE-VERIFIED

s68 called the writeback "a stray 4-byte writeback that NOTHING reads." **That is too generous and the difference matters.** Behavioral A/B on the 28 affected programs (base-ON vs fix-ON, m3, same binary lineage, 3-second rebuild between arms):

- **25 of 28 byte-identical output+rc.**
- **1 REPAIRED: `probe/earn0/earn0_stored_capture.sno` `rc=139` (SIGSEGV) → `rc=0` with output byte-identical to its `.ref` AND to the live SPITBOL oracle (`x64/bin/sbl`): `MATCH V=[a]` / `DONE`.**
- **2 unchanged in kind** (`probe/bb/probes/X12.sno`, `demo/scrip/family_net/family_snobol4.sno`): both keep `rc=134` and the same pre-existing m3 `unresolved label='RETURN'` abort (the s63 m3-only class); only the REPORTED SITE INDEX shifts (1691→1674, 5929→5909 — deltas 17 and 20, consistent with three removed instructions). **Not behavior changes; do not score them as movers.**
- **0 REGRESSED.**

⇒ The site's own comment already warned this class lands "in CRT territory above the outer frame's RSP, corrupting environ, SEGV in getenv()". Under mrbp it was doing exactly that again on at least one witness. **A positive-offset write into a slot the current frame protocol does not own is the s22r/environ-smash family, not litter.**

## THE FIX — TWO GUARDS, ONE AUTHORITY

`!emit_match_begin_stfh_k()` → `!emit_match_owns_startd()` at both sites. No new global, no new field, no new env var; the predicate already existed and already had a killswitch upstream.

⛔ **RECORDED, NOT FIXED:** the ternary at `bb_match_defer.cpp` (`emit_match_begin_stfh_k() > 0 ? "[rsp# + 0]" : FR(...)`) is **PROVABLY DEAD and always was** — the guard admits only `!owns_startd`, which implies raw stfh==0, which implies the wrapper is 0, so the `[rsp# + 0]` arm cannot be selected from this site. Left in place so this rung's diff stays one line per file; **named at the site** so the next reader does not trust it. Deleting it is byte-inert cosmetic work for whoever wants it.

## GATES — COMPILE-TIME BLAST RADIUS, NOT THE BOARD

Per s66's measurement that the 226-program board's noise floor is ~5 and flips green→red (the direction that manufactures false convictions), the gate is byte-identity over emitted `.s`, which has no such floor. New instrument persisted: `scripts/test_sweep_startd_md5.sh` (312 programs = `corpus/probe` + `corpus/programs/snobol4/demo`).

1. **KILLSWITCH LAW — `SCRIP_MATCH_RBP=0`: 312/312 byte-identical, pre vs post.** Legacy world provably untouched.
2. **BLAST RADIUS — `SCRIP_MATCH_RBP=1`: 284/312 byte-identical; exactly 28 changed.** The changed set is **set-equal** to the independently-derived stray-write census. Regression outside the 28 is impossible by construction, not merely unobserved.
3. **SHAPE — 28 of 28 CONFORMING:** each diff is exactly 3 lines removed (`lea rcx,[rip+g_scan_hit_start]` / `mov rax,[rcx]` / `mov dword ptr [rsp+N],eax`) and 1 line rewritten (the label retaining its `jmp`). Zero nonconforming. No instruction moved anywhere else in 312 programs.
4. **STRAY CENSUS: 28 → 0.**

Witness reproduction (`ab_defer_call`, s68's own): ON emitted `mov dword ptr [rsp + 208], eax` — **the exact `[rsp+208]` s68 named** — while MATCH_BEGIN wrote start_δ to `[rbp-40]`; OFF emitted zero such sites. Post-fix ON emits zero.

## ⛔ INSTRUMENT DISCIPLINE — ab_defer_call IS DARK AS A BEHAVIORAL GATE

`ab_defer_call` is **red at HEAD in both modes and BOTH ARMS**, for two unrelated pre-existing reasons: m3 aborts on `unresolved label='RETURN'`; m4 links and runs but prints `[GZ-10] rt_call_proc_descr: procedure 'EXPR$0' has no stackless slab` and then the wrong answer (`no match cnt=0`). **Both arms produce the SAME wrong output**, so by the STANDING INSTRUMENT RULE the witness cannot discriminate this class behaviorally. It is valid for STATIC ASM INSPECTION ONLY — which is exactly how s68 used it. It was not scored as a pass here and must not be scored as one later.

## ⛔ THREE INHERITED CLAIMS RE-TESTED AT ORIENTATION (VERIFY-INHERITED-BLOCKERS)

1. **"gdb never installed this session" (s65e) — FALSE HERE.** `/usr/bin/gdb`, GNU gdb 15.1, present. This is the `gdb-404` class that cost s33–s39 seven sessions; the standing corrective worked, it just has to actually be run.
2. **"the install script produced zero output" (s65e, flagged as suspicious) — THAT IS CORRECT BEHAVIOR.** `install_system_packages.sh` prints nothing when `MISSING` is empty. All 8 packages present ⇒ **the `FINDING-2026-08-12d` phantom-m4-SEGV precondition DOES NOT APPLY to this container.**
3. **The Makefile header still lists `libgc-dev` as a prerequisite — STALE.** The install script's own note records Boehm was deleted from the tree by GC-U-4; reading the Makefile comment instead of the script produces a false MISSING.

## ⛔⭐⭐ CONCURRENCY — THE REPO MOVED UNDER ME MID-SESSION, AND THE FIRST BASELINE DIED WITH IT

Mid-rung, `git stash` reported "No local changes to save" against a tree that `git diff` had just shown as modified. The reflog explains it: **another seat committed this working tree as `69cad4a1`, ran `pull --rebase` (pulling s68 `89b39492` + `4e183a1f`, both touching `emit.cpp`/`frame_need_of`/`bb_classify_node`), and rebased it to `0ef28ee0`.** That is the file's own "THE REPOS MOVE UNDER YOU" clause working as designed, plus s64's law: **a baseline captured before a rebase is NOT a control.**

**Every gate above was therefore RE-MEASURED at the post-rebase HEAD** via an in-place A/B (revert the two guards with `sed`, rebuild — 3s — measure, restore, rebuild) rather than a `git checkout`, deliberately, so as not to yank the working tree out from under the concurrent seat. The defect reproduced at the new HEAD at the same magnitude (28), and all four gate results held.

⛔ **PROVENANCE WRINKLE FOR THE LEDGER:** commit `0ef28ee0` carries s68's two inert `emit_match_owns_startd` lines under an s70 message, because they were uncommitted in the tree when the concurrent seat committed it. The predicate is s68's work; the wiring is this rung's.

⛔ **ATTRIBUTION HELD BACK DELIBERATELY:** the three artifact regens show large net reductions (benchmark −105 net, feature −319 net, demo −304 net). **That delta is the artifacts catching up with s68's TWO COMMITS PLUS this rung combined, and is NOT this rung's product.** This rung's own compile-time footprint is exactly 3 instructions × 28 programs. Recorded per the s65b/s64 attribution convictions.

⛔ **NOT CLAIMED:** the 28 include `claws5-match`, `json-match`, `treebank-match`, `calculator-1/2` — names that also appear in the watermark's m4 failing set. **Causation was NOT measured and is NOT asserted.** It is a cheap next probe, not a result.

## NEXT

- The rung s65e named — **widen mrbp qualification to shallow mains (`flat_deep_arrival=0`)** — was DEFERRED to close this one first, and that ordering was the point: widening mrbp widens the population of the defect above. With the home question now wired, the widening is safe to attempt.
- `earn0_stored_capture` should be promoted to a standing regression witness for the START-δ home (it is the only program in the corpus whose verdict moves on this predicate).
