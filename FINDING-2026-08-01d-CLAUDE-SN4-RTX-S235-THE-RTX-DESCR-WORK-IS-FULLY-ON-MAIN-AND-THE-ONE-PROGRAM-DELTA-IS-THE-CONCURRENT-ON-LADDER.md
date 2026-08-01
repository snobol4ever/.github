# FINDING s235 (2026-08-01) — THE RTX ASM + DESCR WORK IS ALREADY FULLY ON MAIN; THE −1 WATERMARK DELTA IS THE CONCURRENT ON LADDER, NOT THE TAG RENUMBER

**Session goal as given:** "finish moving RTX asm and DESCR changes into the main branch."
**Outcome:** the move was ALREADY COMPLETE on origin/main. This session MEASURED that claim instead of inheriting it, found the s234 cursor wrong on push state, established main's true watermark, and ATTRIBUTED a one-program delta that would otherwise have been billed to the RTX/DESCR work by the next session.

---

## 1. ⭐⭐ THE s234 CURSOR'S PUSH CLAIM IS FALSE — (a)-CLASS ROT, EXACTLY AS `RULES.md` §97(a) PREDICTS

s234's LIVE CURSOR reads **"NOT PUSHED (credential owed)"** and names SCRIP `5ddd5738`+`026f1cb5`, corpus `2b2f0ab9`+`92a882e4` as "COMMITTED LOCAL ONLY".

**MEASURED:** both repos are clean, and `HEAD == origin/main` on both.
- SCRIP `03cecd87` == `origin/main`, working tree 0 modified.
- corpus `e6eee1d9` == `origin/main`.

The cursor's four hashes do not exist; the landed hashes are SCRIP `e0bd5738`/`03cecd87` and corpus `35b59d1c`/`e6eee1d9` — **the signature of a `pull --rebase` at push time, which rewrites hashes.** The work was pushed; the doc froze a pre-push sentence and nobody edited it afterward.

⇒ **This is the THIRD independent recurrence of the rule's own named failure.** `GOAL-SNOBOL4-BB.md` carried eleven false PUSH-PENDING banners (s47); this is the same shape in the RTX goal file. **`handoff_status.sh` remains the only push truth.** A session that had trusted this banner would have opened by re-pushing work already on origin, or worse, by "recovering" it from a branch.

## 2. ⭐⭐ MAIN'S TRUE WATERMARK — AND IT IS NOT s234's NUMBER

Full SNOBOL4 crosscheck, `setarch -R` (ASLR off, s231's root cause), **N=4, BYTE-REPRODUCIBLE — all four runs identical**, `RT_OPT=-O0`:

| leg | s234 CLAIMED | MEASURED AT HEAD `03cecd87` |
|---|---|---|
| m3 `--run` | 295 / 22 / 0 | **294 / 23 / 0** |
| m4 `--compile` | 280 / 35 / 2 | **280 / 35 / 2** (EXACT) |
| DIVERGE | 16 | **17** |

m3 fail-set md5 (sorted names) = **`2192860a5d539b4fe1a6b5aea0ee16df`**, identical across all 4 runs.
⛔ s234's fail-set md5 `ac8908de8333d6a2f9879b86a2032e18` is **STALE — do not quote it.**

Set-diff HEAD vs s234's baseline: **ONE program ADDED, ZERO removed — `152_pat_json_keyvalue_renamed`.** Same shape as s232.

## 3. ⭐⭐ THE ATTRIBUTION — AND WHY IT MATTERS THAT IT WAS MEASURED, NOT ARGUED

The obvious-and-wrong reading is "the tag renumber cost a program." Three builds settle it:

| tree | contents | m3 | DIVERGE | `152` m3 |
|---|---|---|---|---|
| `afbcab9b` | s234's stated baseline | **295/22/0** | 16 | PASS |
| `37dbf795` | + ON-3 + ON-5, **TAG-3 re-apply ABSENT** | **294/23/0** | 17 | **FAIL** |
| `03cecd87` (HEAD) | + s234's TAG-3 re-application | **294/23/0** | 17 | FAIL |

⇒ **`152` was ALREADY BROKEN before s234's commits existed in the line.** The regression entered with the concurrent ζ/ON ladder — `154a3fa8` (ON-3 ARG-NOTE, 189 `rt_*` argument loads renamed through the 4col choke point) or `efc11e5f` (ON-5 CLAIM-ZERO raw destination spelling). **The TAG-3 re-application holds EXACT on top of it (294/23/17 → 294/23/17).**

⭐ **s234's measurement was HONEST AND CORRECT — it reproduces to the digit at `afbcab9b`.** What defeated it is that `pull --rebase` replayed its commits on top of two commits from a parallel session, **producing a combination nobody ever measured.** The gate was run against a tree that never reached origin.

⇒ ⭐⭐ **NEW RULE — A REBASE IS AN UNMEASURED MERGE.** `RULES.md` already warns that parallel sessions make `PLAN.md` stale by design and that `git pull --rebase` at handoff is what catches a moved main. It does **not** say the obvious consequence: **the rebase silently manufactures a tree combination that no gate has ever been run against.** s232 caught a defect *created* by a merge only because it re-gated after merging. **A watermark measured BEFORE `pull --rebase` does not describe what you pushed.** ⇒ **Re-run the watermark AFTER the rebase and BEFORE claiming EXACT HOLD**, or state plainly that the number describes the pre-rebase tree.

⇒ ⭐ **AND THE INVERSE OF s232 IS THE MORE DANGEROUS DIRECTION.** s232's merge-created defect was loud (the branch was on trial). Here the rebase *revealed* a pre-existing regression from someone else's ladder while the RTX work sat on top of it — so the delta presents as "the tag renumber broke a program," which is FALSE, and the cheap response (revert the renumber) would have destroyed correct work and left `152` broken anyway.

## 4. ✅ THE MOVE ITSELF — AUDITED, NOT ASSUMED

Everything the ladder owed to main is present and gated:
- `src/contracts/descr_tags.inc` present (syntax-neutral `#define`, shared by Intel asm + AT&T asm + C).
- `descr.h` carries the zero-preserving layout exactly as designed: `DT_SNUL=0x00 DT_S=0x02 DT_I=0x03 DT_R=0x05`, aggregates stride 8 from `0x08`, `DT_FAIL=0x68`, `DT_DATA=0x70`.
- **All 16 `.S` files include the shared tag header.** Manual sweep for bare/packed tag literals returned only NON-TAG hits, each classified under the s230 reading rule (`[reg+0]`=TAG, `[reg+4]`=SLEN): `rtx_alloc.S:161` aggregate-KIND clamp 0..2 · `rtx_icnvar.S:84/88` SLEN dispatch under a symbolic `cmp edi,DT_N` · `rtx_match.S:306` single-byte length fast path · `rtx_str.S:110` byte-count copy ladder · `rt_asm_helpers.S:36/38` nametrap SLEN 1/2 under symbolic `cmpl $DT_N`. **s230's `$9/$99/$6` in `rt_asm_helpers.S` are GONE; the packed `0x200000009` class in `rtx_icnsub.S` is GONE.**
- s234's two late finds are symbolic on main: `bb_call_fn.cpp:197,200` packed `cmp64 rax,(long)DT_I` · `bb_call.cpp:451,453` `(long)DT_I`/`(long)DT_S`.
- Tree-wide emitter sweep for tag-shaped bare literals in `x86()` calls returns **exactly one hit, and it is correct**: `bb_glue_flat.cpp:91` `x86("mov32","edi",1)` is the **argument to `exit(1)` in TEXT medium**, not a tag; both BINARY ports beside it are symbolic (`DT_S` at `:83` γ, `DT_FAIL` at `:92` ω) — i.e. **the s234 fix is intact.**
- The s231 rail `scripts/bench_min_of_n.sh` and the extended gate `scripts/util_tag_layout_verify.py` are both on main (they were NOT stranded on the branch, which was the live risk).

**GATES RUN AT HEAD:** tag layout **13/13 PASS** (incl. its own `descr.h ↔ descr_tags.inc` 22-define cross-check and "no hand-encoded tags in .S, 2 asm dirs swept" — the machine confirming the manual sweep) · build **EXIT=0, zero errors** · RTX unit **ALL PASS, 8426/0** (matches s234 exactly) · store-width **PASS, 16 GOT-tainted stores** · m3 smoke green · 17 `rtx_gate` bytes linked.

⛔ **NO SPEED NUMBER.** Measurement/attribution session; the rail was deliberately not run. `RT_OPT=-O0` throughout — no `-O2` was directed.
⛔ **NO `.s` REGEN OWED:** this session changed ZERO source files. The three regen scripts were correctly NOT run.

## 5. ⛔ THE BRANCHES ARE CONFIRMED DEAD WEIGHT — DELETION IS THE ONLY REMAINING STEP AND IT NEEDS A CREDENTIAL

`origin/tag-renumber-s229` (6 commits ahead of merge-base) and `origin/trial-merge-s233` (8) contain **nothing main lacks**: the renumber, the five s231 emitter mint fixes, the extended layout gate, and the min-of-N rail are all verified present on main above. Their remaining diff vs main is entirely main having ADVANCED past them (`x86_arg_roles.h`, `gen_callee_arg_roles.py`, the CARVE-KILL deletion of `xa_flat.cpp`).

⚠ Keeping them is an active hazard, not neutral: s232 recorded a fresh clone landing on `tag-renumber-s229` instead of `main`. That specific claim was falsified at s233 (a fresh clone lands on `main` — re-confirmed this session), **but the branches remain a standing invitation to re-merge finished work.**

## 6. ⛔ STILL OPEN (unchanged by this session, re-stated so the cursor is honest)
1. ⭐⭐ **`152_pat_json_keyvalue_renamed` — NEW REGRESSION, OWNER IS THE ζ/ON LADDER, NOT RTX.** Bisect `154a3fa8` vs `efc11e5f` and route to that goal file. MONITOR-FIRST per `RULES.md`.
2. ⭐⭐ **m4 EVAL IS SILENTLY EMPTY** — `1016_eval` produces no output in m4 (rc=0) while hello-world runs; sits in FAIL(m4)+DIVERGE. Pre-existing, not caused here.
3. deferred ARITH `*(n + 3)` SEGVs in m3 on pristine main.
4. delete the two dead branches (needs credential).
5. then the untouched s231 queue: `SCRIP_NO_CU=1` Prolog gate · TAG-4 vs `rtx_arith.S` · `VARVAL_fn` (rank 1, 29M entries) · `eval_dynamic` 430×.

## 7. ENVIRONMENT FACTS ADDED
- **This container has `nproc == 1`.** A full `make scrip` is ~4 min single-core; budget three builds per A/B triple.
- **`setsid` survives a tool-call boundary; plain `&`/`nohup` does not** (s234's fact — re-confirmed, four detached builds completed cleanly).
- `Makefile` uses `ROOT := $(shell pwd)`, so an in-place `git checkout` A/B is path-safe; **save `scrip` + `out/libscrip_rt.so` aside and restore rather than rebuilding twice** (the ARCH §7 step-4 pristine-arm recipe, applied to commit A/B).
- The full crosscheck is **46 s** for both modes, so N=4 costs ~3 min. **There is no excuse for an N=1 watermark in this container.**

---

# PART II (same session, s235) — `152` BISECTED TO ONE COMMIT, AND ITS "MODE-3 UNTOUCHED BY CONSTRUCTION" CLAIM IS FALSIFIED BY A ONE-LINE PROBE

## 8. ⭐⭐ THE GUILTY COMMIT IS `154a3fa8` (ON-3 ARG-NOTE), ALONE

`154a3fa8`'s parent is exactly `afbcab9b`, so one build isolates it. Measured, `setarch -R`:

| tree | m3 | DIVERGE | `152` |
|---|---|---|---|
| `afbcab9b` (parent) | 295/22/0 | 16 | **PASS** |
| `154a3fa8` (ON-3 alone) | **294/23/0** | **17** | **FAIL** |

⇒ **ON-3 alone. `efc11e5f` (ON-5 CLAIM-ZERO) is EXONERATED** — it was a coin-flip suspect and it is now ruled out by measurement, not by argument.

## 9. ⭐ THE SYMPTOM IS A DETERMINISTIC SEGV, AND THE PROGRAM PAIR IS THE TELL

`152_pat_json_keyvalue_renamed` **SEGVs** in m3 (expected `k=age s= n=42 b=`). It differs from `127_pat_json_keyvalue` in **NOTHING BUT CAPTURE-VARIABLE NAMES** (`K/S/N/B` → `KVAL/SVAL/NVAL/BVAL`); `152` exists precisely because `127`'s `S` collides with input `s` under case folding. Both now SEGV; `127` was already in the fail set, so **the gate is STRUCTURALLY BLIND to `127` degrading from wrong-value to SEGV** — a failure-mode change among already-failing programs is invisible to a pass/fail count. ⚠ Do not assume the blast radius is one program.

**NOT s231's ASLR/load-address class — FALSIFIED:** 8 runs `setarch -R` + 12 runs ASLR ON = **20/20 identical empty output**. The fault is DETERMINISTIC. My own layout-perturbation hypothesis died in one experiment.

## 10. ⭐⭐⭐ THE ONE-LINE PROBE — AN UNREACHABLE CALL BREAKS MODE 3

ON-3 is **558 insertions, ZERO deletions**; only two files compile (`x86_arg_roles.h` +134 table, `x86_asm.h` +61). The whole `x86_asm.h` delta is `x86_argnote()` plus ONE call site at `:1384`, and that call sits **inside `x86_4col`, whose FIRST LINE is `:1343` `if (MEDIUM_BINARY || MEDIUM_MACRO_DEF || !PLATFORM_X86) return s;`**. The commit's own comment states: *"TEXT-only: x86_4col returns early for BINARY, so mode-3 bytes are untouched BY CONSTRUCTION."*

**PROBE: comment out `x86_argnote(o);` at `:1384` and NOTHING ELSE. Rebuild. Result: `152` prints `k=age s= n=42 b=` correctly, rc=0, 3/3.**

⇒ ⭐⭐ **THE CLAIM IS FALSE. A call guarded behind a `MEDIUM_BINARY` early-return demonstrably changes mode-3 behaviour.** Deleting it, and only it, converts a deterministic SEGV into the correct answer.

⇒ ⭐⭐ **NEW RULE — "BY CONSTRUCTION" IS A HYPOTHESIS UNTIL A PROBE KILLS THE ARM.** This is the SIXTH failure of a same-shaped claim in this tree (`GOAL-DESCR-TAG-ENCODING §5`'s "the asm is symbolic" failed five times; s230 §48 records that class). The pattern is identical: **a safety property asserted from reading the guard, never tested by removing the guarded code.** ⚠ The reasoning is seductive because the guard IS there and I verified it by reading at `:1343` — reading was not enough. **A one-line deletion plus one rebuild is the whole cost of knowing.**

**LEADING HYPOTHESIS, NOT MEASURED, DO NOT INHERIT AS FACT:** `x86()` returns a string that in BINARY carries the **in-band `L`/`J`/`D`/`E`/`F` records** `bb_emit_x86` later walks (RULES.md TEMPLATE-ONLY EMISSION). `x86_argnote` MUTATES that string — it splits on `'\n'`, appends `#` annotations with 88-column padding, and does `o.swap(out)`. If `g_medium` is ever TEXT during a mode-3 emission (runtime EVAL/CODE chain, artifact path, or a dual-label/STNO desync of the class `FINDING-2026-07-25-...MONITOR-DARK-FOR-SN4-DUAL-LABEL-EMITTERS-AND-STNO-DESYNC` names), the guard does not hold and the record stream is corrupted → wrong bytes → SEGV. ⇒ **Next step is MONITOR-FIRST per RULES.md, plus printing `g_medium` at `:1343` on a mode-3 run of `152`.**

## 11. ⛔ ROUTING — THIS IS NOT MINE TO LAND
The defect, the file (`src/templates/x86_asm.h`), and the gates all belong to the **ζ/ON ladder**, not SNOBOL4-RTX. Per RULES.md ("DO NOT READ UNRELATED GOAL FILES") I stopped at diagnosis and did **NOT** land the one-line fix: it touches `x86_asm.h`, which fires `.s` regen ×3 and needs that ladder's own gates and watermark. **The probe is reproducible in two commands and is recorded above.** ⛔ **The probe was REVERTED; the tree is clean at `03cecd87` and the committed artifacts are the pristine main build.** Lon routes it.

## 12. ⛔⛔ STILL BROKEN FIVE COMMITS LATER — THE LADDER IS BUILDING ON IT (measured at session end)

Origin moved DURING this session. SCRIP `03cecd87` → **`7ba87345`**, five commits, **all from the same note-column family**: `39cfbbbc` (ON-1 operand-kind + ON-3 restore side), `f3e3fe3a` (s23e ON-4 partial), `47936e39` (s23f note column, "three defects"), plus two `.s` artifact commits.

**Rebuilt at `7ba87345` and re-tested: `152` AND `127` BOTH STILL SEGV.** The regression is NOT fixed, and four further annotation commits have landed on top of a note path that is **measured** not mode-3-safe.

⇒ ⭐⭐ **THE WATERMARK NUMBERS IN PART I DESCRIBE `03cecd87` AND NOTHING ELSE** — stated per this session's own new rule. The `152` fault, the bisect to `154a3fa8`, and the `:1384` probe all still reproduce at `7ba87345`.
⇒ ⚠ **URGENCY: the family is under active development while broken.** The one-line probe in §10 is the fastest known reproduction and costs one rebuild.
