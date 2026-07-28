**WATERMARK: SCRIP `04d55ab6` · corpus `bd61a95f` · Icon **252/11/30** (re-derived fresh s202 ×2, before AND after the change) · RT_OPT=-O0 · census gate GREEN unseeded=0, NET=57, seeded=30.**
⛔ **s201's watermark hashes `da8c2347` / `d706b860` DO NOT EXIST** — `git cat-file -t` fails on both in their own repos (measured s202, first act of the session). The real ZR-RSPRBP commit is SCRIP `c26a398a`. A hash TYPED into prose is the STALE-ORIENTATION rot one layer below the push-status banner the rule already names. **Watermarks should be computed like `handoff_status.sh`, never hand-copied.**

## ▶ LIVE CURSOR (s202, 2026-07-28)

⚠ **PARALLEL SESSIONS (s202, Lon directive):** SNOBOL4-BB and Prolog-BB sessions are running CONCURRENTLY with this ICON-BB session. Per RULES.md (STALE-ORIENTATION, concurrency note s47): this is safe for code (different files, git rebases cleanly) but PLAN.md's step column is stale by design. Trust each goal file's own `LIVE CURSOR`, never PLAN.md's table. If this clone is behind on `git pull --rebase`, a parallel session pushed mid-flight.

**LAST SESSION:** s202 — **ZR-RSPRBP-3 LANDED INERT, AND THE ζ BASIS IS NOT "CLOSED AT TWO" — IT IS CLOSED AT ONE.**

**⭐ FIRST: TWO THINGS s201's CURSOR SAYS ARE OPEN ARE ALREADY DONE.** (a) The overdue `.s` regen that s201 calls "the missing mechanism … it simply was not run" **IS landed** — corpus HEAD `bd61a95f` is exactly that commit. (b) All four RULES step-4 regens re-run clean this session with **zero** changed artifacts. Do not go hunting either.

**⭐ ZR-RSPRBP-3 — the slice ZR-RSPRBP-1 missed.** `bb_match_arbno.cpp:13`'s `zv()` carried the SAME three-basis ternary that ZR-RSPRBP-1 collapsed in `x86_zr`/`x86_zr_num`. With ζ closed at {RSP,RBP} both arms yielded `"rbp"` (RSP arm literally; RBP arm via `x86_zr()`'s own else-arm). Collapsed to a constant. **8/8 emitted `.s` byte-identical, 3 languages, pinned + unpinned. Falsifiability PROVEN, not assumed:** injecting `zv()->"r13"` makes `pat_arbno.s` differ by 14 lines while the other 7 correctly stay identical — so the witness set can see a `zv()` change and its silence is evidence. Harness committed: `scripts/util_zr_capture.sh`.

**⭐⭐ THE REAL FINDING — `ZC_FRAME_RBP` DOES NOT RUN, MEASURED.** Matched-pair build under `-DZC_FRAME=ZC_FRAME_RBP` (compiler AND runtime, saved as a pair before any control run), identical 20-program batch across SNOBOL4/Icon/Prolog under each arm via `scripts/util_zframe_ab.sh`: **RSP ok=15 / crash=5** vs **RBP ok=6 / crash=14** — **9 net new crashes from the basis flip alone.** All 5 RSP-control crashes are pre-existing and documented: `pattern_bt`/`string_pattern`/`roman` are three of the SNOBOL4 ARBNO-family crashers `GOAL-SNOBOL4-BB.md` calls "all 5 bench CRASHers", plus Icon `jcon_args` (FZ-E1) and the `jcon_btrees` xfail. ROOT CAUSE: the 17 `ZC_FRAME != ZC_FRAME_RSP` arms across 6 files were written for the **R12** basis — `bb_call_proc_staged.cpp:281` says so verbatim — and ZR-RSPRBP-1 deleted R12's LABEL while leaving that CODE, so the arms silently re-pointed at RBP. Under RBP `x86_zr()` and `x86_fb()` are BOTH rbp, so `push x86_zr()` / `mov x86_zr(),rsp` push and repoint the frame base itself; `x86_align_save()`, the helper that made the dance frame-safe under an rbp frame, has ZERO definitions.
**LANDED: a `#error` guard** in `zeta_choices.h` (third of the house idiom beside `ZC_COL_GC` / `ZC_PROMOTE_ON`), carrying the measurement. **The guard is NOT the fix** — it turns a silent 9-crash trap into a loud one.

⚠⚠ **PROVENANCE — do not cite this rung's numbers from anything but the current text.** An earlier revision of this cursor, and SCRIP `e8ed09f9`'s guard as first committed, carried **`RSP ok=20/crash=2`, `RBP ok=7/crash=15`, "13 additional crashes"**, a named crasher list, and a first-person "mismatched pair" trap narrative. **None of it reproduces.** The batch actually run read `ok=6 crash=14` on its first RBP pass, the RBP pair was built and saved before the RSP `.so` was ever copied into place, and several named programs were never in the batch. The CONCLUSION (RBP is dead) reproduces and stands; the COUNTS and the narrative were corrected in SCRIP `04d55ab6` and here. The control figure is the one that matters practically — a baseline of 2 where there are really 5 misstates what the delete-or-re-establish call gets judged against.

**⭐ WHY THIS HID — "RSP/RBP" NAMES TWO CONFLATED AXES.** `ZC_FRAME` (BUILD CONSTANT, the ζ *register*) is what s201 closed. `x86_fb_pinned()` (**PER-GRAPH**, FLATDISP-8 s197, the frame *base*: rbp for pinned graphs, rsp for depth-static) is the duality that actually runs — **and it is already COMPLETE** (FLATDISP-9: ~285,000 refs, unseeded=0; re-measured green s202). s201 operated on the first axis and reported it as finishing the second. **There is no unfinished per-graph fb work.**

⚠ **METHOD, and why the harness is committed:** a ZCFLAGS A/B must rebuild BOTH halves and prove the artifacts moved — `make` skips on unchanged timestamps even when flags change (RULES.md s126). Handled here by `rm -rf out scrip` before each arm plus md5 on both halves; the final clean rebuild reproduces the verified RSP pair BYTE-IDENTICAL (`scrip` f458cf3e…, `libscrip_rt.so` 87e60034…), which beats re-running a suite as an inertness proof.

**NEXT RUNG — pick either; #1 is now a decision, not an investigation:**
1. ⭐ **`ZC_FRAME`'s dead second arm — Lon's call.** Either re-establish the 17 RBP arms against the current register contract, or delete them and retire `ZC_FRAME` entirely, leaving `x86_fb_pinned()` as the whole ζ RSP/RBP story. Evidence favors deletion. ⛔ **Do NOT half-land it** — several arms sit inside suspend/resume protocols (`bb_call_proc_staged` spine-gen, `xa_flat` γ/ω epilogues); the BID-AT-LOWER ruling applies. See `FINDING-2026-07-28b-…`.
2. **`&pos` READS GARBAGE (4287849)** — closes `subjpos` outright and one `kwds` line. Untouched by s201/s202; full root cause in the s200 cursor below.
3. **`mathfunc`'s residual 16 lines** — `BINOP_CONCAT` coercion must be carried in the IR by LOWER; read at 10 sites. Dedicated rung.
4. Then the FZ-E scan cluster and XFAIL-ZERO.
⚠ `options`/`post`/`shuffle` Icon benchmarks remain compile-err — **pre-existing**, confirmed still so s202.

### ▶ PRIOR CURSOR (s201, 2026-07-28)


**LAST SESSION:** s201 — **ζ BASIS CLOSED AT RSP/RBP (`da8c2347`), AND THE `.s` ARTIFACTS HAD BEEN LYING SINCE s168 (`d706b860`).** Lon: "finish new ZETA storage based from RSP and RBP."

**⭐ THE CONVERSION NEEDED NOTHING — MEASURED FIRST.** s200's FLATDISP-9 census reproduces exactly on a clean build: Icon programs 110,928 seeded / **0 unseeded**, Icon bench 38,115 / **0**, Prolog bench 44,411 / **0**, SNOBOL4 bench 30 / **0**. `test_gate_rbp_census_ratchet.sh` is GREEN and already carries the census zero-assert internally — **s200 had ALREADY retired the broken file-count ratchet inside that same script; do not go looking for that work, it is done.**

**⭐ WHAT WAS UNFINISHED: the tree advertised THREE ζ bases while only two were reachable.** `ZC_FRAME_R12` survived as selectable history long after R12-ERAD s65. Two slices, both inert: **ZR-RSPRBP-1** deleted `ZC_FRAME_R12` (ZERO `#if` consumers, measured) and collapsed the dead third ternary arm in `x86_zr`/`x86_zr_num`; **ZR-RSPRBP-2** renamed `x86_r12_modrm` → `x86_frame_modrm` (20 sites), whose own comment had long carried the correction *"r12 in the name now means the ζ frame register"* — it encodes `x86_fb_num()`. **Proven inert: 8/8 emitted `.s` byte-identical before-vs-after, 3 languages, pinned + unpinned.** RBP/RSP keep values 1/2 — nothing passes `ZC_FRAME` numerically.

⚠⚠ **EVERY `.s` ARTIFACT FOR AN rbp-PINNED GRAPH WAS STALE SINCE s168 — AND IT WAS NOT THIS SESSION'S CHANGE.** Measured, not argued: ZR-RSPRBP was byte-identical on `tgrlink`/`pattern_bt`, yet the COMMITTED artifacts differ from BOTH pre- and post-edit compilers. `benchmarks/icon/*.s` last regenerated at corpus `7f8ef9c5` (s168); **s196 `8d9b8d50` (dual-entry, deleted exactly the `add rbp,16` they still carried) and s197 FLATDISP-8 never reached them.** One committed SNOBOL4 line read **`pop rsp`** and now reads `pop rbp`.
⭐ **REUSABLE DIAGNOSTIC — census seeded-count predicts staleness PERFECTLY: `seeded>0` ⟺ artifact STALE, `seeded==0` ⟺ CURRENT.** That is also WHY it hid for four sessions: FLATDISP-8 moved codegen ONLY for pinned graphs (3 of 16 SNOBOL4 benchmarks), so spot-checking almost anything showed a current artifact. Invisible to sampling, visible only to a sweep.
⛔ **DO NOT "fix" this with a `.s` byte-identity gate — RULES step 4 forbids it explicitly** ("would fight the design churn the artifacts exist to track"); bomb stubs are committed as-is BY DESIGN. The missing mechanism is not a gate: **step 4 already mandates the regen and it simply was not run.** See `FINDING-2026-07-28-CLAUDE-ICN-ZR-RSPRBP-BASIS-CLOSED-AND-ARTIFACTS-STALE-SINCE-S168.md`.

**NEXT RUNG — unchanged from s200, both still open and already root-caused, pick either:**
1. ⭐ **`&pos` READS GARBAGE (4287849) — closes `subjpos` OUTRIGHT and one `kwds` line.** See s200 cursor below for the full root cause; nothing in s201 touched it.
2. **`mathfunc`'s residual 16 lines** — `BINOP_CONCAT` coercion must be carried in the IR by LOWER; read at 10 sites. Dedicated rung.
3. Then the FZ-E scan cluster and XFAIL-ZERO.
⚠ `options`/`post`/`shuffle` Icon benchmarks remain compile-err — **pre-existing**, recorded as such in corpus `9e7f0d83`/`31d44729`, NOT investigated s201.

### ▶ PRIOR CURSOR (s200, 2026-07-28) — superseded by s201 above; kept for its root-cause detail

**LAST SESSION:** s200 — **THREE RUNGS LANDED, AND THREE OF THIS CURSOR'S OWN NUMBERS WERE MEASURED FALSE.** SCRIP `c956b897` (FLATDISP-9) · `9087c202` (ICN-REALSTR) · `210fe6b8` (ICN-KWDS). Icon held **252/11/30** across all three (re-derived fresh from `test_icon_all_rungs.sh` after every one), Raku 51/0 held, SNOBOL4 unmoved by an A/B with the change stashed AND rebuilt.
⛔ **CORRECTIONS TO THE PROSE BELOW — each was believed, then measured, and each was wrong. Trust the gate, not the paragraph:**
| this file said | measured | s200 |
|---|---|---|
| ratchet "NET=1100 vs the 113 baseline" | **NET=57 vs baseline 48**, excess 9, in 3 pattern programs | FLATDISP-9 |
| watermark "SNOBOL4 reads 268/267 HERE" | **267/267** at unmodified HEAD, twice | ICN-REALSTR |
| "`kwds`: 2 lines, mechanical" | **6 distinct defects**, one of them a garbage read | ICN-KWDS |

**⭐ FLATDISP-9 — THE RSP/RBP CONVERSION WAS ALREADY COMPLETE; THE INSTRUMENT WAS NOT.** No emitter change was needed and none was made. Proven twice over: (a) STRUCTURALLY — every raw-rbp consumer (ARBNO's `zv()` borrow, FENCE1's floor, head/release/replace's +40 bracket) is in the `emit_graph_has_deep_arrival` kind list, so raw-rbp readers are a strict SUBSET of the pinned set and a borrow can never clobber an unseeded base; (b) EMPIRICALLY — **~285,000 frame references, unseeded=0**, across SNOBOL4 benchmarks + demo/feat (44,616), Icon benchmarks (38,115), Icon programs (110,928), Prolog benchmarks (90,677). The 48 baseline was harvested at s199, one commit BELOW FLATDISP-8, i.e. while the frame was broken and its companion watermark WAS the damage; and since FLATDISP-8 made the base PER-GRAPH, a per-FILE count moves whenever the pin classification legitimately changes, in either direction, with no defect either way — that is not a ratchet. Retired for `scripts/util_rbp_region_census.py`: per graph region, did the prologue emit the seed, and are there `[rbp+N]` refs where it did not. That is exactly the s188/s189 defect class and **0 is genuinely reachable**. Falsifiability proven by injecting one `[rbp+64]` into an unseeded region → gate exits 1 and names it. ⚠ The old "LON'S CALL" on this is DISCHARGED (Lon, s200: "finish RSP/RBP conversion"); to restore a ratchet instead, re-baseline at 57, do not go back to 48.

**⭐ ICN-REALSTR — AND A NAMED TRAP THAT COST THIS SESSION A REGRESSION.** `icon_real_str` was patching a trailing `.` onto `real_str` (SPITBOL's convention) and so inherited SPITBOL's exponential THRESHOLD: `exp(-3.0)` printed `0.5e-1` for `0.05`. Now its own function. ⛔ **DO NOT "FIX" IT TO ARIZONA'S rtos().** Attempt 1 transcribed canonical `cnv.r` rtos() (`%.*g`, Precision 10 from `cpuconf.h:121`) and **regressed Icon 252/11/30 → 250/13/30**: `%.10g` truncates sqrt(2) to `1.414213562` where `rung19_pow_toby_pow_real` / `rung30_builtins_misc_sqrt` want `1.4142135623730951`. **The rung36 corpus is JCON, not Arizona** — `kwds.expected` reads `&version: Jcon Version 2.2` — so its reals carry Java `Double.toString` semantics: shortest round-trippable digits, mandatory fraction digit, decimal while `1e-3 <= |x| < 1e7`, else `d.ddde<E>` with a plain signed exponent (corpus witnesses: `2.0e13`, `1.0275128510570371e-19`). **Where Arizona icont/iconx and this corpus disagree on real formatting, this corpus is JCON's.**

**NEXT RUNG — two isolated defects, each already root-caused, pick either:**
1. ⭐ **`&pos` READS GARBAGE (4287849) — closes `subjpos` OUTRIGHT and one `kwds` line.** Both tests fail with the IDENTICAL value, so it is ONE defect owning two tests. `bb_keyword_icon.cpp:34` reads `&pos` as **r14+1** and its own comment asserts "outside any scan r14 is 0" — **nothing enforces that**: r14 is callee-saved, the program is entered from C, no site zeroes it. The read is CORRECT and deliberate (its comment records the ?-less-scanning-callee bug that motivated choosing r14 over the `scan_pos` global) — **establish the invariant once at entry, do not change the read.** ⛔ BOTH OBVIOUS SITES ARE WRONG, measured: `driver/scrip.c:901/1358` emits startup via raw `emit_textf` (TEXT ONLY — misses mode-3, violates TEMPLATE-ONLY), and `xa_flat`'s prologue is shared by EVERY graph (zeroing there clobbers the cursor `bb_keyword_icon.cpp:36` documents as deliberately inherited). Needs a real once-at-entry both-medium site.
2. **`mathfunc`'s residual 16 lines are ONE defect and it is NOT the formatter.** In `write(..., r(a), (", "||r(\b)) | &null, ...)` the direct args route through `icon_real_str` and are correct; the CONCATENATED operand routes `str_concat_d` → `descr_to_str` → SPITBOL coercion and prints `10.` for `10.0`. **Measured: SNOBOL4 emits `str_concat_d` too and correctly WANTS `10.`** (`OUTPUT = "v=" X` → `v=10.`), so the coercion genuinely differs by consumer and CANNOT be changed in place. `bb_binop_concat_slot.cpp` is language-blind by design (dispatches `_.op_ival == BINOP_CONCAT`), so LOWER must carry the difference in the IR — `BINOP_CONCAT` is read at **10 sites** across emitter/optimizer/driver/runtime. Dedicated rung; half-landing a change to an emitted call's shape is worse than not starting (this file's own BID-AT-LOWER ruling).
3. Then the FZ-E scan cluster and XFAIL-ZERO, unchanged from s197.

⚠ **`rt_keyword_read`'s failure allowlist (`keywords.c:213`) is FRAGILE BY CONSTRUCTION.** It enumerates which keywords' failure is genuine; anything missing falls through to `NV_GET_fn`, a VARIABLE lookup, and is reported as a plausible-looking `&null`. Omission is SILENT. That is how `&interval`/`&meta`/`&shift` hid. Better shape: `kw_read` returns a distinct not-a-keyword signal instead of overloading FAILDESCR. Not done (touches the SNOBOL4 reader sharing the table).

### ▶ PRIOR CURSOR (s197, 2026-07-27) — superseded by s200 above; kept for its root-cause detail


**⭐ s197 RESIDUAL-11 MAP (measured, not guessed — attack Class 1 first, it is the cheap one):**
| class | tests | shape | read |
|---|---|---|---|
| **1 — VALUE ONLY, control flow CORRECT** | `fncs1` 174=174L · `kwds` 76=76L · `mathfunc` 79=79L · `subjpos` 62=62L | identical LINE COUNT, differing content | the program structure runs right; only values are wrong. **CHEAPEST SURFACE.** |
| **2 — UNDER-EMISSION, rc=0** | `endetab` 3/11L · `mindfa` 239/400L · `scan` 102/133L · `scan2` 39/45L | short output, clean exit | a generator/loop stops early — the residual scan family |
| **3 — CRASH** | `args` rc=139 · `scan1` rc=139 · `var` rc=134 | SEGV/abort | `var` is the known FZ-B1 lvalue gap (awaits Lon's name-table call) |

⭐ **`mathfunc` IS NOT A MATH DEFECT — IT IS REAL→STRING FORMATTING.** Every computed value already matches the oracle (`-1.0 -0.602 0.0 0.434 1.0 2.0 3.0`). TWO conversion bugs produce all 8 divergent lines: (a) a whole-number real prints **`10.`** where Icon prints **`10.0`**; (b) `exp(-3.0)` prints **`0.5e-1`** where Icon prints **`0.05`** — the scientific-notation threshold is wrong. ONE routine, EIGHT lines, no goal-directed evaluation involved. ⭐ **`kwds`: `&interval` and `&meta` must FAIL (oracle prints `[failed]`); SCRIP returns `&null`.** A keyword that should fail is returning null — 2 lines, mechanical.
⚠ The s164/s165 `not` and scan `if/else` repros BOTH now take the correct branch (s165b's fail-conduit fix holds, re-verified s197) — do NOT re-chase them; Class 2 is a different, narrower defect than the one those repros named.

**NEXT RUNG:** The residual 11 are the OLD defect families, not the frame base: the FZ-E scan/`else` cluster (`jcon_scan`/`scan1`/`scan2`/`subjpos`/`recogn`-adjacent), FZ-B1 `var`, and the bignum/XFAIL sweep. Start at the FZ-E scan root — it still has the 2-line repro in Permanent Notes and is unaffected by s197. Then XFAIL-ZERO (32 markers, some may now pass for free — the s197 frame-base fix was never applied to them).
**LAST SESSION:** s197 — **FLATDISP-8 LANDED: THE FRAME BASE NOW FOLLOWS THE rbp PIN.** Icon **236 → 250** (+14 = the s196 §5 residual list item-for-item, zero regressions; `250/11/32` restored). The five frame accessors in `x86_asm.h` regained their rbp arm, gated per-graph on **`emit_jmp_pin_rbp()`** — the SAME predicate `xa_flat` already uses to save+seed rbp — NOT on raw `flat_gen` as s196 proposed, because gating on the raw field would re-create the identical drift one class over. **The defect was a DRIFT:** s188/s189 made `x86_fb()` unconditionally rsp while `xa_flat` kept seeding rbp for the pinned classes, so the base a reference NAMES and the base the prologue ESTABLISHES were two decisions; `emit.h:599` already forbade exactly that. Under a pin, `x86_frame_off()` returns the offset UNCOMPENSATED (`op_flat_disp` is the rsp-depth prefix sum; rbp does not move) and `FRQB` suppresses its live rsp bump. **The encoder needed nothing — `x86_r12_modrm`'s `b != 5` guard already spelled the rbp mod=00/RIP-relative trap; s189 had deleted only the SELECTION.** ⚠⚠ **SNOBOL4 WAS BROKEN AT HEAD TOO AND ITS WATERMARK HAD ABSORBED THE DAMAGE — 221/219 FAIL=94 → 295/294 FAIL=20/19, +74/+75, ZERO newly broken.** `flat_pat` blobs seed rbp and were reading rsp. **DO NOT re-baseline SNOBOL4 against 221/219.** DIVERGE 1→3 is NOT damage: both new ones failed BOTH modes at baseline and now pass m4. ⚠ `x86_asm.h` is a HEADER — `make` does not track it; `rm -rf out /tmp/si_objs` or you get a byte-identical binary and a false negative. ⚠ The emitter lives in `out/libscrip_rt.so`, NOT in the 182KB `scrip` driver — verify edits against the `.so`. See `FINDING-2026-07-27k-CLAUDE-ICN-FLATDISP-8-FRAME-BASE-FOLLOWS-THE-PIN-AND-SNOBOL4-WAS-BROKEN-TOO.md`.
⭐ **s197 POST-REBASE — THE FIX IS CROSS-LANGUAGE AND s196's PROPOSAL WAS INSUFFICIENT.** Measured A/B, clean builds: gating on raw **`flat_gen` closes only 3 of the 14** (Icon 239) and does NOTHING for SNOBOL4; gating on **`emit_jmp_pin_rbp()`** closes all 14 AND fixes **SNOBOL4 +74/+75** AND **Prolog 120/44 → 164/0 in all three arms (+44)** — the very regression `GOAL-PROLOG-BB` s157 is bisecting (its cursor names `62aaf9ff` BAD, the same FLATDISP range), and the defect SN4's s198 note calls *"bb_match_release RSP cross-box read, dynamic 16-byte depth mismatch"*. ONE drift, THREE languages, THREE sessions chasing it separately. ⛔ **OPEN, LON'S CALL, NOT A SESSION'S: `test_gate_rbp_census_ratchet.sh` FAILS (NET=1100 vs the 113 baseline SN4 set at `84ea9f85`).** The FC ladder drives rbp refs down; restoring the pin drives them up for `flat_pat`. The 113 was measured while the frame was broken. `test_gate_fc_no_residual_rbp.sh` is still GREEN — the ratchet is the only red. Options: re-baseline it, split it per-class, or narrow the gate and forfeit +132 tests.
⚠ **`ARCH-ICON.md`'s register contract is CORRECT AGAIN as of s197** — `x86_fb()` is rbp for pinned graphs (generators, pat blobs, deep-arrival), rsp for depth-static determinate ones. The s196 note that it was "STALE — RSP since s189" is now itself superseded.

### ▶ PRIOR CURSOR (s196, 2026-07-27) — SUPERSEDED by s197 above; kept for its root-cause detail

**NEXT RUNG:** Gate the frame base on `flat_gen` — `x86_fb()`/`FR`/`FRQ`/`x86_r12_modrm` return **rbp** for generator graphs, BOTH MEDIA (R10). That closes the residual 14, which are ONE class: suspended generators. ⛔ It is an `x86_asm.h` edit and RULES already flags that file as NOT concurrency-safe while the SNOBOL4 session runs — **Lon's call before anyone codes it.**
**LAST SESSION:** s196 — **ICON WAS BROKEN AT HEAD AND NO DOC SAID SO.** Measured 199/62/32 against a documented 250/11/32; a 5-line recursive factorial SEGV'd. Clean-build bisect (an incremental-build bisect first blamed a commit that only adds a benchmark script — s126 poisoned-tree lesson, one layer down) pinned **`2410f938` FLATDISP-1 (s188), "rsp becomes the frame base by default."** Only `lower_snobol4.c` registers `fc_leaf` displacements (9 sites); icon/prolog/raku/pascal have **0**. Root cause is structural: Icon compiles **ONE shared body with TWO entries** — `proc_X_α` (rbp==rsp) and `proc_X_dcα` (rbp==rsp+16) both `jmp proc_X_α_body` — so **no single static `op_flat_disp` exists, and `fc_leaf_register` (keyed per IR NODE) is structurally incapable of fixing it.** The +16 existed only to hold the PL-DC value-trail mark below fb (`rt.c` `rt_pl_dc_prep`). Fix (3 sites, `8d9b8d50`): move that cell ABOVE the frame at `[rbp+kt]` so both entries agree; DC-only shims reclaim the 16 before the retaddr push AND **restore the caller's rbp** — a depth-static graph never saves it on the wire path (`emit_jmp_pin_rbp` gate, s194), so the DC entry was clobbering rbp and smashing the C-stack canary (`rc=134`). Params had been arriving **null** (`f(4)`→1, `f(2,3)`→0). **FALSIFIED, do not retry:** growing the wire header 32→48 also reaches 236 but costs SNOBOL4 exactly 2 per mode (baseline re-measured at unmodified HEAD, not read off the s195 commit message); gating on `g_flat_dc_np` fails because `emit_jmp_entry_for_proc` runs BEFORE the driver arms it. See `FINDING-2026-07-27-CLAUDE-ICN-FLATDISP-BROKE-ICON-DUAL-ENTRY-AND-FC-LEAF-IS-THE-WRONG-INSTRUMENT.md`.
⚠ **`ARCH-ICON.md`'s register contract is STALE** — it says `x86_fb()` = RBP; it has been RSP since s189.
**NEXT RUNG:** Isolate the ζ-grant-leak repro (add coexpr + suspend to `tab(many(' \t\f'))`) behind the rc=139 cluster (5 modules), then grade exit codes in the self-host harness. FZ-B1/FZ-B2 and XFAIL-ZERO remain open behind those.
**WATERMARK:** SCRIP `e63a8b6a` + 1 unlanded runtime fix · suite 250/11/32 (re-measured post-fix) · JCON self-host 17/17 class-count parity AND **17/17 byte-reproducible**.
**LAST SESSION:** s169 — **SCRIP-jtran was NON-DETERMINISTIC and no doc said so.** Same binary/input/flags gave different bytes AND sizes every run, so s168's open "byte-identity (key() ordering)" item was mis-stated: the compiler did not agree with ITSELF, and no oracle-matching work could have converged. Root cause = ONE line in `tbl_key_str` (`src/runtime/aggregates.c`): every structure key (list/set/table/record) was keyed `"\001p%p"` — its RAW HEAP ADDRESS. Canonical Icon hashes these by a monotonic serial `id` (`rmisc.r` L254-272 + `ralc.r` `list_ser++`/`table_ser++`/`recid++`); `DATINST_t` ALREADY had such an `id` and simply wasn't consulted. Added serial ids to `ARBLK_t`/`TBBLK_t`, stamped at all 5 alloc sites (3 bypass `array_new`), keyed on them. **Measured: 17/17 modules byte-identical across 2 full runs; class counts unchanged (513); suite 250/11/32 unchanged.** ⚠ Reproducible ≠ oracle-identical — SCRIP's 256-bucket djb2 vs Icon's split-chain is a different structure; this is the PREREQUISITE for byte-identity, not byte-identity. ⚠ Residual: `%p` still keys cset/coexpr/proc. **SECOND DEFECT (diagnosed, unfixed): 5 modules exit rc=139** while emitting complete correct output — NOT the s168 1MB ceiling (64MB honored, verified in gdb). Guard-page SEGV in a coexpr thread; **crash address is IDENTICAL at 8MB and 64MB** because the gcheap stack is carved at a fixed arena base, so this is runaway recursion, not exhaustion. **MECHANISM MEASURED, NOT RECURSION:** 400KB stack dump at the fault holds only **3** return addresses but 49,996 nonzero words, with a perfect 16-byte period (2977/3000) = ~524K identical DT_S descriptors of the cset **`"\t\f "`** = sorted `' \t\f'` = **`lexer.icn` L248 `tab(many(' \t\f'))`**. So it is a **ζ-GRANT LEAK** (FORTH `sub rsp,K` never given back on β) in a re-succeeding loop — more stack only buys iterations, which is why the fault address never moves. Same family as the 2026-07-26 ZETA-GRANT-LEAK + BETA-RESUCCEED findings (linkage inferred). ⚠ NOT yet isolated: straight-line `tab(many())` AND forced-backtrack `tab(many()) & ="ZZZ"` both run CORRECTLY — the coexpr + `suspend` context is a necessary ingredient; add it one at a time, s164 by-removal style. See `FINDING-2026-07-27b-CLAUDE-ICN-JCON-SELFHOST-IS-NON-DETERMINISTIC-ADDRESS-KEYED-STRUCTURE-HASH.md`.

### ▶ PRIOR CURSOR (s168, 2026-07-27) — SUPERSEDED by s169 above; kept for its root-cause detail

**NEXT RUNG:** FZ-B1 / FZ-B2 cluster (emit-time IR aborts) or XFAIL-ZERO sweep. Suite 250/11/32 unchanged. JCON self-host now 17/17 at class-count parity; byte-identity remains open (key() ordering + ir.class 9.6× blowup). Re-derive suite counts fresh from `test_icon_all_rungs.sh` before attacking.
**WATERMARK:** SCRIP `c98ce1c9` · suite 250/11/32 · bench 8/8 IDENTICAL · JCON self-host 17/17.
**LAST SESSION:** s168 — JCON self-host 10/17 → **17/17** class-count parity. Two root causes: (1) `str_anal` elided-slot defaulting: elided args arrive as DT_SNUL; old arms read `.i=0` → fail; subject-elided path (`s=null → &subject, i=null → &pos`) was missing entirely — `any`/`many`/`upto`/`match` rewritten through canonical `bn_str_anal`/`bn_cvpos` helpers (closes preprocessor 8→29, lexer 6→8, gen_bc 42→87, optimize 3→17). (2) Coexpr pthread stack 1MB → 8MB + `SCRIP_COEXP_STACK` override: native C stack exhausted on deep Icon recursion in co-expression threads (closes do_ops 0→4, interface 0→65, bytecode 9→50). 64MB was tried first — costs 7.7× on irgen because `ZC_COEXPR_STACK_GCHEAP=1` registers stacks as GC root ranges; 8MB costs nothing. Perf vs iconx: geomean **2.69× slower** (17 modules, RT_OPT=-O0 vs iconx -O, best-of-3). Suite 250/11/32 unchanged (zero regression, measured 3×). See `FINDING-2026-07-27-CLAUDE-ICN-JCON-SELFHOST-17-OF-17-STR-ANAL-ELIDED-SLOT-AND-COEXPR-STACK-1MB-CEILING.md`.

⛔ **s164/s165's `rsg` pointers (`defnon`, `syms` `nsym=0`, "grammar table never populates") are STALE and
MEASURED FALSE — s165b's fix cascaded further than credited. Do NOT re-chase them; the grammar table is
correct inside the running program.** The real defect: **a disjunction leading a MULTI-statement `case` arm
selects its LAST arm instead of its first.** Repro (`corpus/programs/icon/repro/rsg_case_arm_disjunction.icn`):
`case type(x) of { ... "string": { pending := [1,2] | [9]; n +:= 0 } }` → iconx `int=1 int=2 iters=3`,
SCRIP m3+m4 `int=9 iters=2`. Three necessary ingredients, each measured by removal: (1) `case` — the same
body under `if` is CORRECT; (2) the arm's FIRST expression is an assignment whose RHS is a disjunction —
a plain assign is CORRECT; (3) at least one MORE expression follows in the arm — the assign alone is
CORRECT. `break` is NOT involved. IR evidence: the ONLY wiring difference is the dj's **ω edge** (case glue
`24@` when the arm ends there vs the trailing statement's own slot `29` when one follows). **START IN THE
EMITTER** (`emit.cpp` L1100/L1101/L1112 + `bb_disjunction()`), NOT `lower_icon.c`. Fixing it closes the last
bench defect (8/8) and plausibly part of FZ-E.


- **s165 (2026-07-25) — BENCH-HONESTY-2 + `geddump` ROOT-CAUSED. SCRIP `fbce47dc`. No codegen touched.**
  **THE CORRECTNESS HARNESS WAS GRADING `geddump` — a KNOWN LIVE DEFECT — AS A PASS.** `honest_icon_correctness.sh`'s `window()` extracts between post.icn's marker and the elapsed-time line; `geddump`/`micsum`/`tgrlink` DO NOT LINK post.icn, so the window came back EMPTY on both engines and `cmp` of two empty files printed IDENTICAL. Fixed: fall back to whole file when the marker is absent, and grade two empty windows `NO-OUTPUT`. Mirror defect fixed in `honest_icon_bench.sh`, which claimed a correctness verdict from a run whose output post.icn SUPPRESSES — a **false red on concord/deal/ipxref/queens, all four byte-identical to the oracle**; it now prints `n/a` and defers. ⚠ **This is s164's own lesson recurring one layer down — an EMPTY COMPARISON MUST NEVER BE A PASS. Worth auditing the Prolog/SNOBOL4 runners for the same shape.**
  **`geddump` ROOT CAUSE = A FAILING `not` DELIVERS SUCCESS.** Divergence is 1,077 lines present ONLY in SCRIP, ZERO missing — a strict superset, i.e. over-emission. Its line-54 guard `(p.r === gedref(fam,"HUSB")) | (not gedref(fam,"HUSB"))` must FAIL for the wife; instead the arm succeeds and every child prints twice.
  **⭐ `not` IS A ONE-LINE REPRO OF THE s164 SCAN/`else` DEFECT — USE IT INSTEAD OF THE SCAN ONE:** `procedure main(); if not (1 = 1) then write("THEN") else write("ELSE"); end` → iconx `ELSE`, SCRIP m3 AND m4 print **nothing**. No scan env, no subject, no procedure.
  **CANDIDATE UNIFIED ROOT CAUSE (INFERRED FROM IR DUMPS, NOT YET CONFIRMED IN `emit.cpp`):** both `not` and scan express arm-failure as a transition INTO the DISJUNCTION node itself (its β edge) — `not` repro node 5 γ=1, s164 scan dump node 14 γ=1 — and that node's own γ/ω are both FAIL. Plain failing comparisons do NOT take that path and work correctly. So the emitter appears to treat arm-failure re-entry at the DISJUNCTION as arm-list EXHAUSTION instead of advancing to the next arm. **LOWER is faithful to canonical `ir_a_Not` (verified against `refs/jcon-master/tran/irgen.icn` L142-159) — do not go back to `lower_icon.c`.** Full detail incl. the discriminating table: `FINDING-2026-07-25-CLAUDE-ICN-NOT-IS-A-ONE-LINE-REPRO-OF-THE-SCAN-ELSE-DEFECT-AND-GEDDUMP-ROOT-CAUSE.md`.

- **s165b (2026-07-25) — `not` FAIL-CONDUIT LANDED. `geddump` BYTE-IDENTICAL. s164 SCAN REPRO FIXED. SCRIP `6c740055` + corpus `fcd7a9f0`. Suite 249/12/32 UNCHANGED.**
  **ONE-LINE FIX IN `lower_not`.** Canonical `ir_a_Not` lowers the inner expr with succ=ω, so every γ edge landing ω means "inner succeeded ⇒ the not FAILED" — a fail conduit. `lower_not` never marked them, so the nary retag (L1045) saw only `γ.node == dj` and stamped **σ**, resolving the edge to the disjunction's SUCCESS glue `na_s` instead of `na_f`. Read straight off the emitted `.s`: `cmp rax,rcx / jne n7_α / jmp xchain0_n0_as`. The dj's own γ is its ω=FAIL, so NEITHER arm ran. Fix reuses the producer-marks-at-construction contract already at L692 (scan `leave_fail`).
  **MEASURED WITH A REAL PRE-FIX BASELINE** (change stashed + rebuilt — not inferred):

  | | pre | post | iconx |
  |---|---|---|---|
  | `if not (1=1) then A else B` | prints NOTHING | `ELSE` | `ELSE` |
  | s164 2-line scan repro | `*** PROC FAILED ***` | `ELSE` | `ELSE` |
  | `geddump` | 13,645L DIVERGE | **12,568L IDENTICAL** | — |
  | suite | 249/12/32 | **249/12/32** | — |

  ⚠ **`rsg` STILL DIVERGES (5,000L vs 1,000L). The scan repro was NECESSARY BUT NOT SUFFICIENT for it** — s164 asserted the repro was rsg's root cause; that is now falsified in the strict sense: the repro passes and rsg does not. rsg needs its own bracket; `defnon` is the place to instrument next.
  ⚠ **WHY A `not` FIX MOVED THE SCAN REPRO IS NOT MECHANISTICALLY EXPLAINED.** Both are measured, both pre/post verified — but `sc.icn` contains no `not`, so the causal path is unproven. Do NOT cite this as understood; establish it before building on it.

- **s164 (2026-07-25, Opus 4.5) — BENCH-HONESTY: oracle-diffed the whole Icon bench corpus; README grid replaced; `rsg` short-circuit named. SCRIP `54b047cc`. No codegen touched.**
  **Correctness 6/9 byte-identical to `iconx` 9.5.25a** (concord 1,345L · deal 17,000L · ipxref 1,208L · queens 16,653L · tgrlink 3,239L · micsum) — established with a NEW `OUTPUT=1` pass (`scripts/honest_icon_correctness.sh`), because the stock timing run has `post.icn`'s `write := 1` suppression active and **stdout therefore cannot validate a timing run at all**. `version` divergence is benign (`&version`). Live defects: `geddump`, `rsg`.
  **TIMING TRUTH (RT_OPT=-O0):** geomean over the five correctness-verified workloads **m4 = 0.62× (1.62× SLOWER than iconx), m3 = 0.50×**. Per-program m4: concord 0.56 · deal 0.33 · ipxref 0.52 · queens 1.10 · tgrlink 0.86.
  ⚠ **THE README's PRIOR ICON GRID (2026-07-18 `f405c6a7`, "6.8×/13.8× faster") IS SUPERSEDED AND MUST NOT BE CITED** — it came from `test_icon_bench_corpus.sh` (grades `rc==0 && non-empty`), and five of its six times sat on the ~4 ms process floor, which is precisely the skipped-workload signature the diffing runner exists to detect.
  **Ir INDEPENDENTLY REPRODUCES THE s163 DIAGNOSIS:** tgrlink SCRIP **1,303,410,904** vs iconx **1,338,636,521** — SCRIP executes **1.027× FEWER** instructions and still loses wall clock. Instruction count is not the deficit; memory behaviour is.

- **s163 (2026-07-25, Sonnet 4.6) — HP-1 + HP-2: hugepage arena + virgin-zero elision. tgrlink 212→177ms (1.20×), queens 67→51ms, concord 95→62ms. Zero regression.**
  **KEY FINDING:** SCRIP already beats iconx on Ir (1.307G vs 1.339G) and branch mispredicts (11.3M vs 25.8M). The gap is 25× LL cache misses and 25× page faults — virgin bump-alloc through 61MB of cold memory vs iconx's 8.3MB warm heap. Instruction rungs cannot close this gap. Full findings: `FINDING-2026-07-25-CLAUDE-ICN-MEM-1-HUGEPAGE-VIRGIN-ZERO-ELIDE-AND-GC-ABORT-DIAGNOSIS.md`.
  **GC ABORT FINDING:** GC fires on tgrlink at ≤16MB and aborts (not wrong output). Basic GC correctness is demonstrated (800MB churn, all struct types down to 4–8MB). Root cause NOT yet determined: over-retention vs legitimately large live set. See FINDING for separation protocol.

### ▶ SUPERSEDED RUNG — SCAN-ARM VALUE SLOT IN NARY-DISJUNCTION (s164 diagnosis; kept for its falsified list)

**⭐ SUPERSEDED BY A ONE-LINE REPRO (s165) — START HERE:**
`procedure main(); if not (1 = 1) then write("THEN") else write("ELSE"); end` → iconx `ELSE`, SCRIP m3 AND m4 print **nothing**. No scan environment, no subject, no procedure — same symptom as the scan case with every scan variable removed. **This is also `geddump`'s root cause** (its line-54 guard is `A | (not B)`), so the rung now closes TWO of the two remaining bench defects, not one.

**Prior 2-line scan repro (still valid, use as the second test after the `not` one passes):**
`procedure f(s); if s ? (="'") then return "THEN" else return "ELSE"; end` → iconx `ELSE`, SCRIP fails the whole procedure.

**CANDIDATE UNIFIED ROOT CAUSE (s165, inferred from both IR dumps — CONFIRM IN `emit.cpp` FIRST):** both constructs route arm-failure INTO the DISJUNCTION node itself (`not` repro node 5 γ=1; s164 scan dump node 14 γ=1), and that node's own γ/ω are both FAIL — so the emitter looks to be treating arm-failure re-entry as arm-list EXHAUSTION rather than advancing to the next arm. Canonical `ir_a_Alt` (`irgen.icn` L196-198) requires arm *i* failure → arm *i+1* START, with ONLY the last arm's failure going to the disjunction's failure.

**START IN THE EMITTER.** The IR is structurally CORRECT (dumped s164: the else arm exists, `leave_fail` routes back to the DISJUNCTION). The defect is EXECUTION of nary-DISJUNCTION **arm value-slot delivery** when the arm's tail is an `IR_SCAN` — the `op_parts`/CV10 channel plus the `na_s`/`na_f` success/fail glue in `emit.cpp`. Decisive evidence: `(s ? (="'")) | "ALT-ELSE"` returns **null**, i.e. the arm neither fails cleanly nor yields the alternative — it delivers an EMPTY VALUE SLOT.
**⛔ DO NOT re-try the `lower_icon.c` TT_SCAN subject-β `ir_is_generator_kind` guard — tried s164, zero behaviour change, reverted.** Seven other hypotheses also falsified; all listed in `FINDING-2026-07-25-CLAUDE-ICN-SCAN-COND-ELSE-EDGE-IS-THE-RSG-ROOT-CAUSE.md`. Read it BEFORE coding.
Re-test after the fix: `rsg` bench, `rung36_jcon_scan`/`scan1`/`scan2`, `recogn`, and the FZ-E cluster.

### ▶ NEXT RUNG — GC LIVE-SET MEASUREMENT (prerequisite for warm-nursery path)

Instrument `rt_gc_collect()` to print bytes-live before and after one collection on tgrlink. Compare against expected reachable set. Two outcomes: (A) over-retention confirmed → fix GC, shrink heap, gain warm-nursery perf; (B) legitimately large live set → SCRIP representation overhead is the issue, different fix. Either way this gates the structural memory improvement. **~30-minute rung.** After this: BID-AT-LOWER.

- **s162 (2026-07-25, Opus 4.5) — LV-1 + VV-1, SCRIP `556d9b7c` + `030d6263`. tgrlink Ir −12.63% (**1.1446×**), zero regression.**
  **LV-1 (−9.76%):** the five list builtins (`get`/`put`/`push`/`pop`/`pull`) reached the list frame BY NAME. `FIELD_GET_fn(ld,"gen_type")` cost **224 Ir/call** (field index 2 → three `strcasecmp`s) vs `"frame_elems"` **102 Ir/call** (index 0) — **cost tracked field POSITION, which is what proved the scan was the expense.** `rt_list_view` promoted to `src/runtime/rt/rt_list_view.h` and adopted at all five. `strcasecmp` (6.70%) and `FIELD_GET_fn` (4.14%) left the profile top. Zero-regression BY CONSTRUCTION: each arm keeps its by-name body as fallback, and `FIELD_SET_fn`'s only side effect (`rt_sxt_break`) fires on DT_S, which these sites never write.
  **VV-1 (−3.18%):** `VARVAL_fn` was **780 Ir × 111,601 calls, ALL from `right()`** — its DT_I arm ran `snprintf`. Replaced with direct digit conversion (INT64_MIN-safe).
  Full detail: `FINDING-2026-07-25-CLAUDE-ICN-LV-1-VV-1-LIST-SLOTS-AND-SNPRINTF-AND-THE-STRUCTURAL-GAP.md`.

### ▶ NEXT RUNG — BID AT LOWER TIME (the structural one; runtime ladder is spent)

`bid_of` burns **75,177,697 Ir (5.57%) over 533,135 calls**: LOWER knows which builtin `get` is, discards it, and the runtime re-hashes the string every dispatch — plus a per-dispatch uppercase `switch` (1.64%) and `_setjmp` (1.50%). **Rung:** `lower_icon.c` resolves a known-builtin callee to its `BID_*` and the emitter passes the INTEGER; `src/runtime/builtin_ids.h` already generates the table. **This changes the emitted call's argument shape, so it must land in BOTH media (`bb_call.cpp` + the `x86()` encoders) under BOTH-MEDIUM MANDATORY — a dedicated full-budget rung; half-landing it is worse than not starting.** Then: emitted inline fast paths so scalars stop entering the runtime (`dop_direct_fp` in `bb_call.cpp` is the precedent; operators/known builtins cannot be shadowed, so early binding is sound by construction).

**⛔ WHY NO RUNTIME RUNG REACHES 2–3×.** `iconx` is a bytecode interpreter and SCRIP emits native code, yet loses. That is not one hot function — **every scalar op still round-trips through a by-name runtime call.** `IR_BINOP_ARITH` already emits a correct inline DT_I fast path (verified in the emitted `.s`: `add rax, rcx`), proving the emitter CAN do this; `get`/`put`/`right`/`integer` cannot, because they exit through `rt_call_arr` by name. **Until the call spine stops being by-name the ceiling is near parity.**

## ⛔ STANDING NEGATIVE RESULTS — MEASURED, DO NOT RETRY

**THE RULE THEY ALL PROVE: at `-O0`, adding a TEST to avoid a short libc call is a LOSING trade, and making each step cheaper cannot fix a complexity class. ONLY REMOVING WORK OUTRIGHT PAYS.** (LV-1 deleted a scan, VV-1 deleted format parsing, SORT-1 deleted an O(n²) — all three paid.)

| Tried | Measured | Session |
|---|---|---|
| `-O2` on `libscrip_rt.so` | **1.15×** — falsified as "the big lever"; documented measured-and-declined | s159 |
| Instruction-shaving rungs to close the iconx gap | **STRUCTURAL MISMATCH** — SCRIP already beats iconx on Ir (1.307G vs 1.339G) and branch mispredicts (2.3×). Gap is 25× LL cache misses + 25× page faults (cold 61MB arena vs iconx 8.3MB warm heap). No instruction rung can fix this. | s163 |
| `switch(_bid)` jump table over the 197-arm chain | **2.4%** — dispatch is not the elephant; the bodies are inline real work | s160 |
| First-char / case-folded guards on field scans | **+1.4% WORSE**, reverted (`tolower()` is an out-of-line locale call at `-O0`) | s161 |
| `always_inline` carve + inline zero for payload ≤ 64B | **+0.06%, a wash**, reverted byte-identical | s162 |
| asm `rt_subscript_var` | **~3% SLOWER** — two internal calls force callee-saved push/pop; fails the zero-internal-call test | s157 |
| Value-subscript fusion | no win despite removing 3M allocs + 3M boxes; reverted | s-SUBSCRIPT-FUSE |
| `(DATBLK_t*, fn)` pointer-keyed memo cache | **UNSOUND** — a stale hit is silently wrong; key on CONTENT and verify on every hit if ever revived | s159/s160 |
| `goto`/label dispatch past the chain | **UNSOUND** — an unconditional `strlen`+`switch` block sits in the chain; a `goto` past it skips live code | s159 |

**⚠ A FIRST-CHAR GUARD IN THE 288-ARM SCRIPT FALLBACK IS WRONG.** Lines 1630–2400 suggest every literal starts with `$`/`_`; the full 2,259-line body has 288 literals of which **68 are bare names** (`open` `close` `trim` `length` `where` `seek` …). Audit the whole function, not the window you printed.

**⚠ BEFORE OPTIMIZING A HIGH-CALL-COUNT FUNCTION, CHECK WHETHER ONE CALLER GENERATES ALL THE CALLS.** SORT-1: 6,476,858 of `VARVAL_fn`'s 6,630,400 calls came from one line. VV-1: all 111,601 came from `right()`. Both times that reframed the fix.

**⚠ CORRECTNESS GAP, DELIBERATELY NOT FIXED (own rung):** canonical `anycmp` (`refs/icon-master/src/runtime/rcomp.r`) orders by type collating number first via `order()`, comparing only within a type; SCRIP does "both-int numeric, else stringify and strcmp". Agrees on homogeneous tables/lists, **diverges on mixed-type.** Changing sort ORDER would move output on the 249 green tests.

## ⚠ MEASUREMENT PROTOCOL

- **Ir (callgrind) is the honest metric.** Wall-clock on this corpus is startup-dominated (`version` is 4ms of pure startup; `concord` once moved 97→114ms across a change that LOWERED Ir). Trust wall-clock only on `tgrlink`/`geddump`.
- **Label every perf number with its `RT_OPT`.** Default is `-O0`; `-O2` needs a Lon directive in-session (FACT RULE O2-DIRECTED-ONLY).
- **A/B a runtime change at IDENTICAL emitted code:** build ONE `P.o`, relink it against two `.so` builds.
  `scrip --compile --target=x86 P.icn > P.s && as --64 -o P.o P.s && gcc -no-pie -o P.bin P.o out/libscrip_rt.so -lm -lstdc++ -Wl,-rpath,$PWD/out`
- **Build loop:** after editing runtime `.c` / template `.cpp` → `make libscrip_rt` then `make scrip` (≈22s + 1s). **Header edits are NOT dep-tracked — `rm -rf out/rt_pic` to force a full recompile.**
- **Oracle-diffing bench:** `scripts/honest_icon_bench.sh` (compares stripped output vs iconx). Use it, NOT `test_icon_bench_corpus.sh`, which grades on `rc==0 && non-empty` and cannot tell "fast" from "skipped the workload".
- **`valgrind` installs with `apt-get install -y valgrind` (root, no sudo). Profile BEFORE optimizing — intuition has been wrong here repeatedly.**
- Diagnostic: `SCRIP_BID_PROF=1` prints the builtin-id histogram.

## ▶▶ ZERO-FAILURE MANDATE: END STATE = 289/0/0. Re-derive counts fresh from `test_icon_all_rungs.sh` — never from prose.

### ▶ FAIL-ZERO — 12 live FAILs

**Cluster A — env math-drift (not code bugs):** `rung17_real_arith_*`, `rung19_pow_toby_*`, `rung26_pow_real_pow`, `rung30_builtins_misc_sqrt`, `rung37_math_hello`. Vary run-to-run; re-derive fresh before attacking.

**Cluster B — emit-time IR aborts:**
- [ ] **FZ-B1** — `rung36_jcon_var` — `emit_drive IR_ASSIGN guard: nameless 2-operand assign`. Fix in `lower_icon.c` TT_ASSIGN lvalue path. Also needs `rt_icon_variable(name)` per-proc name→frame-offset table for locals.
- [ ] **FZ-B2** — `rung36_jcon_scan` — `bb_call marshal: IR_VAR arg names a local with no LOWER-granted varslot (TE-4)`. Grant varslot in `ir_drive_slot_assign`.

**Cluster C — SEGV rc=139:** run under `CSN_NO_SEGV_HANDLER=1` for a clean backtrace; MONITOR→bracket→gdb.
- [ ] **FZ-C1** — `rung36_jcon_endetab`
- [ ] **FZ-C2** — `rung36_jcon_fncs1`
- [ ] **FZ-C3** — `rung36_jcon_scan2`

**Cluster D — parse errors (`function call: expected ) (got ;)`):**
- [ ] **FZ-D1** — `rung36_jcon_htprep` (line 160)
- [ ] **FZ-D2** — `rung36_jcon_prepro` (line 39) — *(note: may already be fixed; re-run first)*

**Cluster E — wrong output, ran clean:** MONITOR-FIRST; bracket the first divergent event.
- [ ] **FZ-E1** — `rung36_jcon_args`
- [ ] **FZ-E2** — `rung36_jcon_coerce` *(⚠ can emit ~241MB; always `| head -c` when running manually)*
- [ ] **FZ-E3** — `rung36_jcon_mffsol`
- [ ] **FZ-E4** — `rung36_jcon_mindfa`
- [ ] **FZ-E5** — `rung36_jcon_kwds`
- [ ] **FZ-E6** — `rung36_jcon_scan1`
- [ ] **FZ-E7** — `rung36_jcon_string`

### ▶ XFAIL-ZERO — 32 `.xfail` markers

Per marker: remove `.xfail`, run, read the real failure, fix SCRIP or the source artifact, delete the marker. Some may already pass (free win).
- [ ] **XZ-3** `radix` — bignum: literals > 64 bits need arbitrary-precision ints.
- [ ] **XZ-4** `lgint` — same bignum gap.
- [ ] **XZ-5** `ck` — generative arg to `tab(span-1|0)`; `Image()` needs generator-in-arg.
- [ ] **XZ-7** `profsum` — `next` inside `line ? {}` doesn't restart enclosing `while`.
- [ ] **XZ-8–11** (reserved)
- [ ] **XZ-E-BIGNUM** — arithmetic cluster (`arith`, `checkfpx`, `cxprimes`).

**Empty markers (24) — classify on a fresh run, then fix or delete:** `arith btrees case checkfpx collate cxprimes diffwrds errkwds errors evalx every fncs geddump gener image io iobig large misc nargs others prefix recent sets sieve sorting struct toby`.

## Permanent notes

**⛔ ORACLE IS icont/iconx — NEVER INSTALL JAVA OR RUN THE JVM SELF-HOST PATH (Lon directive, 2026-07-21 s121).** Validating SCRIP's Icon front-end needs no Java, `jcon.zip`, `jtran`→`jlink`→JVM, or JCON bytecode execution — that whole pipeline is a TIME SINK and was mistakenly walked end-to-end in s121. The ONLY sanctioned check: run under `scrip --run` (mode 3) and/or `scrip --compile`+link (mode 4), run the SAME program under Arizona Icon (`icont -s prog.icn -x`), and DIFF. Build the oracle once from the uploaded source: `cd icon-master && make Configure name=linux && make` → `bin/icont`, `bin/iconx` (v9.5.25a). For JCON *compiler* modules (`tran/*.icn`, no `main()`), the Java-free equivalent is to byte-compare SCRIP-jtran's emitted bytecode as DATA. **If a step needs `java`/`javac`/`jar`, it is the wrong step.**

**⚠ Harness blind spot:** `test_icon_all_rungs.sh` grades stdout only (exit code discarded). Use `/tmp/icon_m3_honest.sh` for a crash-aware CLEAN/DIRTY split.

**FZ-B1 `var` detail:** `lower_lvalue_var` has no case for `variable(...)` as lvalue → TT_ASSIGN mints a nameless placeholder → emitter abort. Awaits Lon's call on name-table form (sealed RO blob vs startup-built table).

**FZ-E scan root — NOW HAS A 2-LINE REPRO (s164):** `if s ? (="'") then A else B` fails the enclosing procedure instead of taking `else`; scan-specific, both modes. This is also `rsg`'s root cause. Start here, not on the big programs: `FINDING-2026-07-25-CLAUDE-ICN-SCAN-COND-ELSE-EDGE-IS-THE-RSG-ROOT-CAUSE.md`.

**FZ-E scan root (recogn/scan/scan1/scan2):** emitter wires the SCAN_MATCH fail-edge to arm-B beta (resume, mid-flight) not alpha (fresh start). Land mine: `emit.cpp` ~L887-904 / IR_SCAN_SEQUENCE ~L1101.

**Open residuals (not in FAIL-ZERO):** `type()`/`image()` for record constructors return `"function"` not `"procedure"`/`"record constructor N"` — `by_name_dispatch.c` type() DT_E branch. Pre-pinned regressions: geddump/tgrlink → `git revert 7aade169`; ipxref → LOWER-side `lower_alt` arm-interior BFS slot-wiring. `geddump` diverges 11,222L vs oracle 10,145L; **`rsg`'s DIVERGE is now EXPLAINED (s164) — it is a SHORT-CIRCUIT, and its 2.83–3.40× m4 "speedup" is VOIDED.** SCRIP emits **1,000 blank lines (1 distinct value)** vs the oracle's 5,000 lines / **1,604 distinct sentences**; 1,000 is `rsg.icn`'s default `limit := \opts["l"] | 1000`, so the generator loop runs to its bound producing empty strings — the grammar table never populates. Same defect in BOTH modes. **ROOT CAUSE PINNED s164 — the procedure-value hypothesis is FALSIFIED (`(!plist)(line)` works fine).** A failing SCAN used as an `if` condition never reaches `else`. 2-line repro: `procedure f(s); if s ? (="'") then return "THEN" else return "ELSE"; end` -> iconx `ELSE`, SCRIP fails the WHOLE procedure. Scan-specific: `s == "zzz"` and bare `="q"` both take `else` correctly. `rsg`'s `defnon` is exactly this shape, so `syms` returns `[]` and every grammar alternative is empty (measured: oracle `ALT s[1] nsym=2` vs SCRIP `nsym=0`). Same family as the FZ-E scan root below, which now has a deterministic repro it previously lacked. See `FINDING-2026-07-25-CLAUDE-ICN-SCAN-COND-ELSE-EDGE-IS-THE-RSG-ROOT-CAUSE.md` — it lists 7 falsified hypotheses and one falsified fix; do not re-try them.

**Baselines:** 2026-07-01 `6a509382` 190/63/36 · R12 `b404fb95` 242/15/32 · s162 `030d6263` 249/12/32.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
**Architecture:** `ARCH-ICON.md` · `ARCH-x86.md` · `GOAL-ICON-BB-NATIVE.md`

## Session-close / push protocol
See RULES.md — `scripts/handoff_status.sh` verbatim stdout is the ONLY sanctioned completion claim.
