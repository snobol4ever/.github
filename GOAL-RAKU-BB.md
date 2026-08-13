# GOAL-RAKU-BB.md — Raku goal-directed onto the shared four-port IR (the fourth musketeer)

## ⛔⛔⛔⭐⭐⭐ FACT RULE — NO NEW GLOBAL VARIABLES WITHOUT LON'S EXPLICIT PERMISSION (Lon 2026-08-13, in-chat) ⛔⛔⛔

**██ NO SESSION CREATES ANY NEW GLOBAL VARIABLE — file-scope mutable state, pinned VA slot, exported cell, parallel array, or any equivalent — in ANY repo, for ANY reason, without FIRST obtaining Lon's explicit in-chat permission in that same session. Linkage and state ride registers (r10/r11 wires) and the stack. We do not do that here. ██**
**ENFORCEMENT: every diff is checked for new file-scope definitions; a commit adding one without a cited in-chat grant in its message is REJECTED on sight. Precedent: the g_pcall / g_pcall_wires / RT_AB_ANCHOR eradication (s55) — that entire class is what this rule forbids recreating.**


## ⚙️ CONCURRENT BY DEFAULT — AND THE REPOS MOVE UNDER YOU

**Many seats run this file's siblings at the same time. Edit any file, commit and push whenever a rung is buildable and green — mid-session, per rung. Never park work or decline an edit on concurrency grounds; stranding has cost this project far more than merging ever has.** Git merges; `git pull --rebase` and resolve normally.

**⛔ ASSUME ORIGIN MOVED SINCE YOU LAST LOOKED.** Another seat may have landed in your exact files while you were reading them.
- `git pull --rebase` before every push; **re-prove THIS file's gate/watermark after any rebase** — shared state moves under you and a watermark measured pre-rebase is void.
- `git log origin/main..HEAD` at orientation AND before handoff. **A clean `git status` is NOT a clean tree** — it hides local commits a peer seat left in a shared working copy.
- Place trees at canonical absolute paths (`/home/claude/{SCRIP,corpus,.github,x64}`) BEFORE running any gate: **many scripts grade a tree by absolute path.**
- Prefer **one clone per seat**; two seats in one working copy silently overwrite each other's uncommitted edits, and a global gitconfig scrambles attribution.
- Push **code repos before `.github`**, so no FINDING ever describes an unpushed tree.
- Push needs a credential — **ask Lon in chat and wait.** Never write push status into a doc.
- `bash scripts/handoff_status.sh` verbatim is the ONLY push truth. Not this file, not a commit message.

**Semantic collisions (two seats claiming one register) are caught MECHANICALLY by the claim gates, not by scheduling.** That is why no window is needed.

## ⛔ FACT RULE — O0-DEV: FEATURE BUILDS ARE `-O0`; `-O1`/`-O2` ARE PERF-ONLY (Lon directive, 2026-07-21 s119)

**While developing, debugging, or iterating on any FEATURE, EVERY build is `-O0`. `-O1` and `-O2` are FORBIDDEN during feature work and are reserved EXCLUSIVELY for perf/benchmark/release measurement.** The runtime `libscrip_rt.so` at `-O2` takes MINUTES (heavy template TUs), which is intolerable in a compile→test→fix loop and burned real session time repeatedly. `scrip` itself already builds `-O0` (Makefile `CBASE`/`CXXRT`); the offender was the runtime `.so`, whose `RT_OPT` default was `-O2`.

**THE MECHANICAL ANCHOR (why this is a FACT RULE, not a convention):** the Makefile default is now `RT_OPT ?= -O0 …` (SCRIP `Makefile` lines ~33 + ~281), so a bare `make libscrip_rt` / `make scrip` / `build_scrip.sh` is `-O0` by DEFAULT — the fast path is the path you get for free. `-O2` is now EXPLICIT opt-in, used ONLY for measurement:
```
make RT_OPT="-O2 -g -fno-strict-aliasing -fwrapv -fno-omit-frame-pointer" libscrip_rt   # perf/bench ONLY
PERF=1 bash scripts/jcon_selfhost_build.sh                                               # perf .so via the selfhost builder
```
Benchmark builders that need `-O2` already pass it explicitly (`jcon_selfhost_build.sh PERF=1`; the official-oracle trees build their own way), so the default flip does NOT silently corrupt any perf number — a perf run that forgets `-O2` is a mis-measurement the operator owns, not a default that lies.

**COMPLETION TEST:** (a) `grep -nE 'RT_OPT *[?:]?= *-O0' Makefile` matches (default is `-O0`) and no un-opted `RT_OPT ?= -O2` remains; (b) session-setup / feature-dev build scripts (`build_scrip.sh`, smoke/crosscheck runners) invoke `make` with NO `RT_OPT` override (so they inherit `-O0`); (c) any `-O2` in a script is either a monitor/oracle-side helper (separate lib) or gated behind an explicit perf flag (`PERF=1`); (d) this FACT RULE body is byte-identical across the six GOAL-*-BB files (md5-locked, per the Prolog file's sibling-verbatim note).

**LIMITATION (do not oversell — same honest shape as the other rules here):** a Makefile default and a markdown rule cannot COERCE a session to avoid typing `RT_OPT=-O2` during feature work; they make the fast path the default and the slow path a deliberate, visible choice. The human reviewer remains the real enforcer — **reject any feature-work handoff whose build log shows `-O2` on the runtime `.so`.**

## ▶ LIVE CURSOR — s2026-08-08b (RK-GRAM-3d-m3-fix: GALT both-media arm jmps — Claude Sonnet 4.6)

**[THIS SESSION] RK-GRAM-3d-m3-fix COMMITTED — commit `0ce21c92`. Push state is NOT recorded here — run `scripts/handoff_status.sh` LIVE for ground truth (STALE-ORIENTATION rule (a)).**

**NEXT RUNG:** RK-GRAM-3d (remaining alternation work). The m3 delta passback is now fixed. The GALT grammar boxes are now correct in both modes — arm-1 and arm-2 both run in m3 binary. Alternation with both literals and char classes passes. Next: extend grammar alternation to more complex patterns, multi-arm rules, and nested subrule alternation; or proceed to whatever Lon directs.

**PRE-EXISTING FAILURES:** None (smoke suite 724/724 PASS FAIL=0 DECLINED=0 both modes with RK_GRAM_NATIVE=1). Icon `until` (1) and Prolog `clause` (1) are pre-existing in their own suites, unrelated to Raku.

**WATERMARK:** m3 **724/0**, m4 **724/0** (PASS/FAIL — rc-aware harness; +5 GALT alternation smokes added this session). Peers: Icon 14/0, SNOBOL4 6/1 (pre-existing), Prolog 4/1 (pre-existing). Lang-blind rc=0, no_bb_bin_t rc=0, raku_zframe gate PASS.
**LAST SESSION:** s2026-08-08b (this session), commits `3028fdc8` (RK-ZC-7+8), `0ce21c92` (RK-GRAM-3d-m3-fix).

**ROOT CAUSE (worth preserving for the record):** `bb_rk_galt()` used `x86("jmp", _.lbl_t0)` and `x86("jmp", _.lbl_t1)` for the arm-entry jumps. These label strings (e.g. `"n2_glit_α"`) parse as `XK_SYM` in the x86 dispatcher. The `XK_SYM` arm at `x86_asm.h:1484` returns empty string in `MEDIUM_BINARY` mode — zero bytes, silently dropping both jumps. Execution fell through to `x86_gamma()` immediately, arm-1 never ran, r14=0 at `.Lgrambox_γ`, `final_delta=0` always. m4 text mode worked because `XK_SYM` emits the text jmp directive there. **Fix:** `x86_jmp_lblptr(_.lbl_t0_p, _.lbl_t0)` works in both media — binary patches a rel32 via the `bb_label_t*` pointer, text emits the directive. **Diagnostic path:** `rk_gram_run_native` showed `final_delta=0, matched=1`; trampoline trace confirmed `r14=0` at `.Lgrambox_γ`; binary dump of the emitted blob showed jmp at +39 going to +214 (gamma epilogue) instead of the arm-1 alpha; single-arm grammar (no GALT) worked correctly (r14=1). `x86("jmp", name)` for `XK_SYM` in MEDIUM_BINARY is a TEXT-ONLY path — generalizable to any template using bare string label names for jmps in binary mode.

⛔ **THE PIVOT (Lon, this session): RAKU IS NOT BROKEN BY RAKU WORK — IT WAS LEFT BEHIND BY THE REGIME MIGRATION, AND THE FIX IS TO CARRY IT ONTO `ZC_STORAGE_CELL_STACK`, NOT TO RESTORE THE OLD SPINE.** RK-GRAM-3d is DESCOPED until this ladder is green: an alternation box built on a spine where `sub f($a) { return $a*2 }` cannot return is built on sand.

**MEASURED, A/B, SAME MACHINE, SAME `-O0` FLAGS, SAME `test_smoke_raku.sh` (the whole diagnosis is three numbers):**
| Build | m3 `--run` | m4 `--compile` |
|---|---|---|
| BASE `6defd71a` (last Raku commit) | **719 / 0** | **719 / 0** |
| HEAD `e8a5f74b` (+461 peer commits) | 513 / 206 | 465 / 254 |
| HEAD + RK-ZC-2 (two lines) | **661 / 58** | **661 / 58** |

⚠ **THE s2026-07-27b CURSOR'S 719/0 IS HONEST AND WAS VERIFIED LIVE THIS SESSION** by building at `6defd71a` in a worktree. Raku did not rot; the shared call/return spine moved out from under it across 461 peer commits (SN4 ζ-MECH, LADDER PB, ICN ZFRAME/ZETA-CELLS, RTX ports) — 125 of them touch flat/wire/adopt/proc/frame. This is exactly the parallel-session drift RULES' STALE-ORIENTATION rule predicts, and it is the reason a Raku session must run the suite BEFORE trusting any inherited number.

**ROOT CAUSE — ONE FLAG, TWO FAILURE CLASSES.** `IR_graph_t.zframe_graph` is set **ONLY by `lower_icon.c`** (`IR.h:256` says so verbatim: "set ONLY by lower_icon.c on every graph"). ICN-FR-2 carried Icon onto the ζ-frame/cell-stack regime; Raku was never carried. A `zframe_graph=0` graph takes the legacy `rt_outer_call(fn, mf, 0)` entry (`scrip.c:1617`) which supplies **no γ/ω exit wires**, and the legacy epilogue, which does not unwind the rsp cell carve. Both observed Raku failure classes fall out of that one fact:
- **(a) EXIT SEGFAULT — `ret` POPS A ζ CELL.** `say 42` printed `42` then died rc=139. gdb (`SCRIP_NO_SEGV_HANDLER=1`, clean-backtrace hook per RULES) shows `main` at `scrip.c:1617` and return frames `0x3`, **`0x2a`**, `0x3` — `0x2a` is **the literal 42 itself**. The carve is not unwound, so `ret` consumes cell data as a return address. ⚠ **THE HARNESS IS BLIND TO THIS CLASS:** `test_smoke_raku.sh` captures stdout and never checks rc, so a crash-after-correct-output counts PASS. An unknown fraction of the HEAD "513 PASS" were crashing. **RK-ZC-7 makes the harness see rc — do not skip it, the gate cannot guard what it cannot see.**
- **(b) `carries no return wires (activation was not flat-adopted)` (`rt.c:1100`).** Every user sub AND method died rc=1 — `sub f($a){return $a*2}` as surely as `class C { method m }`. `rt_flat_wire_adopt` reads gw=ww=0 because nothing supplied the wires. Commit `28af3501` (Z4-7 slice 2) names this exact bomb in its own message when it fixed the island path; Raku is the same shape, unfixed.

**RK-ZC-2 IS TWO LINES AND IT IS LEGAL.** It mirrors `lower_icon.c:1422-1423` verbatim into `lower_raku.c` (at the `return &g_stage2;` tail), with its own killswitch `SCRIP_RK_ZFRAME=0`. ⚠ **This is NOT a language-identity violation:** the NO-LANGUAGE-IDENTITY FACT RULE forbids language names PAST LOWER — `lower_raku.c` IS a lowerer, language is implicit there by construction, and the flag it sets is a plain IR-graph property the emitter reads without knowing who set it. Lang-blind gate verified rc=0 WITH the change in tree. **Never reach for `is_raku` downstream; if a later step seems to need one, the seam is wrong.**

**FALSIFIED, NOT ASSUMED (both directions):** killswitch `SCRIP_RK_ZFRAME=0` reproduces the segfault and the return-wires bomb exactly; default-on clears both. Peers measured WITH the change in tree: Icon 13/1 and SNOBOL4 7/7, **both byte-unchanged from pre-experiment** — the flag is set in the Raku lowerer only and cannot reach a peer graph.

**⚠ THE STRONGEST SIGNAL IN THE NUMBERS IS THE ONE THAT IS EASY TO MISS: m3 AND m4 NOW AGREE EXACTLY (661/58, and the fail SET is IDENTICAL, `diff`-proven, not just the count).** Before the rung they disagreed by 48. Mode divergence is the tell for a regime the two entry paths disagree about (`scrip.c:1269` m4 twin vs `scrip.c:1617` m3); its disappearance is evidence the fix is STRUCTURAL rather than a mask. **A later step that re-opens an m3/m4 count gap has broken the regime, not just a feature — treat it as a stop, not a residual.**

### RK-ZC LADDER — RAKU FULLY GREEN UNDER `ZC_STORAGE_CELL_STACK`

**THE MODE, NAMED EXACTLY (`src/contracts/zeta_choices.h`):** `ZC_STORAGE_CELL_STACK` (=2) is the **committed default** and means per-BB ζ cell, fixed rsp carve, **rbp pinned PER GRAPH** for dynamic-sized housekeeping (ARBNO/FENCE/suspending generators) and rsp for static-sized. It maps to legacy `ZC_PORT_FORTH + ZC_FRAME_RSP`, which are still the authoritative axes — **`ZC_STORAGE` is slice-1 ENUM ONLY, no consumer reads it yet**, so do NOT "switch to cell-stack" by setting that knob; you are already in it. ⚠ Z4-0 measured **five of seven ports SEGV-ing at HEAD purely because nothing gated them** — an unguarded config rots by exactly that mechanism, which is why RK-ZC-7/8 are rungs and not cleanup.

- [x] **RK-ZC-0 — LIVE baseline, computed, before any edit.** Build `-O0`, run the suite both modes, run peers. DONE this session: HEAD 513/206 + 465/254; peers Icon 13/1, SNOBOL4 7/7. **Do not inherit a watermark — this rung exists because an inherited one was 206 failures stale.**
- [x] **RK-ZC-1 — prove the boundary by A/B, not by reading.** Worktree-build the last Raku commit and re-run the SAME harness. DONE: `6defd71a` = 719/0 both modes ⟹ regression is peer-side, cursor honest. Witness programs pinned as the rung's instruments: `say 42;` (class a) and `sub f($a){return $a*2} say f(21);` (class b).
- [x] **RK-ZC-2 — set `zframe_graph` on Raku graphs in the Raku lowerer + killswitch. COMMITTED `546603d9`.** Two lines at `lower_raku.c`'s `return &g_stage2;` tail mirroring `lower_icon.c:1422-1423`; `SCRIP_RK_ZFRAME=0` restores the pre-rung path. GATE MET: both witnesses rc=0 and correct; killswitch reproduces both bombs; **689/30 both modes** (was 661/58 — grammar family resolved too, see RK-ZC-3); peers byte-unchanged; lang-blind rc=0. Clean full-suite run at committed HEAD confirms 689/30.
- [x] **RK-ZC-3 — GRAMMAR family (28) — RESOLVED FREE BY RK-ZC-2.** No extra fix needed. The grammar native boxes (RK-GRAM-3b/3c) use the ζ-frame entry (`zframe_graph=1`) for the subject-triad registers R13/R14/R15 and the δ-snapshot slot — they were already correct, just gated behind `RK_GRAM_NATIVE=1` (exported inside the harness for the grammar block). When RK-ZC-2 set `zframe_graph=1`, those graphs stopped taking the legacy entry and both failure classes vanished. Zero code change beyond RK-ZC-2. Residual 30 = SLURPY(18) + LOOP-CTL(11) + bool_compare_store(1).
- [x] **RK-ZC-4 — SLURPY family (18). DONE (`d794b613`).** `slurpy_*` (15) + `multi_slurpy_*` (3). These are the s2026-07-26c/27b rungs' own smokes, green at `6defd71a` ⟹ **a pure regression, and the variadic bind path is the suspect** (`rt_frame_bind_args`, which reads the activation frame the regime just moved). ⚠ Do not re-derive the slurpy semantics — they were canonical-verified against `BOOTSTRAP.nqp:888-941`/`860` and are NOT in question; only the frame is. GATE: all 18 PASS both modes.
- [x] **RK-ZC-5 — LOOP-CTL family (+11 smokes). COMMITTED `55d1598b`.** `loop_ctl_*` (5), `loop_cstyle_*` (4), `noparen_until`, `repeat_next` — all PASS both modes. Root cause: the UCLAIM mechanism ("wholesale flip", Lon 2026-08-01) assumes a single-entry statement head — `sub rsp,K` fires once at the `bb_src_of` root, every omega/terminal exit fires the matching `add rsp,K`. For Raku's loop forms (TT_WHILE/UNTIL/CLOOP/REPEAT), `lower_raku.c` never called `bb_src_note`, so the entire graph was ONE UCLAIM run rooted at chain entry n0. The loop-back edge wired directly to `centry` (the condition's first node) — mid-run, past n0. On iteration 2+: `sub rsp,K` not re-executed; the next `add rsp,K` (from e.g. `last if` false branch or the condition's omega exit) fired against a claim never made that iteration; RSP drifted K bytes above the zframe base; C-call stack reads decoded garbage. The FRQ `[rbp+N]` variable reads are depth-immune and survived — which is why `while $i < 3 { say $i; $i++ }` (no mid-loop `add rsp,K` on the success path) passed while `while $i < 10 { last if $i >= 3; ... }` (interior omega exit carrying `add rsp,K`) failed. PRIOR CURSOR DIAGNOSIS WAS APPROXIMATELY CORRECT but mis-described the mechanism: it said "per-box CELL_STACK carve" — the actual mechanism is the UCLAIM wholesale-flip claim, not a per-BB CELL_STACK carve (the two are exclusive regimes). FIX: call `bb_src_note(centry, label)` on each loop-back landing node in `lower_raku.c` immediately after computing it. This registers the node as a `bb_src_of` statement head; the UCLAIM planner starts a fresh run there, emitting `sub rsp,K` at that node's alpha on every entry — first and every loop-back. Applied to: TT_WHILE (centry), TT_UNTIL (centry), TT_CLOOP (centry + incr_entry), TT_REPEAT with condition (bentry + centry), TT_REPEAT bare `loop{}` (bentry). Killswitch: `SCRIP_RK_ZFRAME=0` disables zframe_graph, making bb_src_note inert. GATE: 695/24 → 706/13 both modes; m3/m4 parity holds; SNOBOL4 7/0 unchanged; Icon 12/2 pre-existing (confirmed stash/restore); lang-blind PASS; emit-no-slot-alloc PASS; emit-no-ir-mutation PASS; no-bb-bin-t PASS. NOTE: 13 remaining failures are TWO pre-existing issues (documented in LIVE CURSOR above), not this rung's work. `try_while_die_halts_loop` from the prior cursor's list: not present in the 24 failures in this tree — may have been resolved by an earlier commit or was already DECLINED.
- [x] **RK-ZC-6 — `bool_compare_store` (1). RESOLVED FREE** — already PASS at HEAD before this session. The lone unclustered residual from RK-ZC-5's 706/13 was resolved by a prior commit. Zero action needed.
- [x] **RK-ZC-7 — HARNESS SEES `rc`. COMMITTED `3028fdc8`.** `test_smoke_raku.sh` now captures rc3 (m3 `--run`) and rc4 (m4 linked binary and compile-phase exit). A crash-after-correct-output is FAIL. New `raku_dies()` helper: stdout must match expected AND rc must be nonzero — used for all 17 die/type-error/access-violation tests (field_write_ro_dies, priv_attr_*_dies, role_conflict_unresolved, required_unimplemented, attr_required_absent*, die_uncaught_halts, param_*_dies, try_die_in_handler_uncaught_halts, div_by_zero_dies). SMX is checked first so an SMX-with-correct-stdout doesn't accidentally score PASS. raku_dies m4 path: compile-phase die (scrip --compile rc!=0) counts as rc!=0 so compile-time errors (role conflict, required-unimplemented) are correctly classified. Re-baseline: exposed 17 hidden crashes/dies; all recovered via raku_dies; watermark stays 719/0.
- [x] **RK-ZC-8 — REGIME PIN GATE. COMMITTED `3028fdc8`.** `scripts/test_gate_raku_zframe.sh`: Invariant A — SCRIP_RK_ZFRAME=0 reproduces class-b return-wires bomb (sub f($a){return $a*2} say f(21); → rc=1); class-a (say 42; flat) no longer bombs after peer commits absorbed the legacy RSP carve path for flat programs. Invariant B — full suite 719/0 both modes. Gate exits 0/PASS verified this session. Killswitch still reproduces class-b bomb. Lang-blind rc=0, no_bb_bin_t rc=0.

**GENERALIZABLE (the finding worth carrying to Prolog/Pascal — CHECK THEM):** `zframe_graph` is set by ONE lowerer. **Every frontend that is not Icon is presumptively on the legacy entry and presumptively carries both failure classes.** Prolog and Pascal were not measured this session. A regime migration that lands per-lowerer is a migration that silently forgets the lowerers nobody ran that day; the cheap check is two witness programs per language, not a code read.

## ▶ PRIOR CURSOR — s2026-07-27b (RAKU-100: `*%h` slurpy-named + overflow fix — ONE rung — Claude Sonnet 4.6)

**[THIS SESSION] CODE LANDED (tree green, both modes). Push state is NOT recorded here — run `scripts/handoff_status.sh` LIVE for ground truth (STALE-ORIENTATION rule (a)).**

**NEXT RUNG:** (a) ⛔ **`+@r` (SLURPY_ONEARG) IS NOT THE CHEAP RUNG IT LOOKS LIKE — TWO reasons, both MEASURED s2026-07-27.** First, it inherits the SAME byte-coincidence as `**@` (canonical `from-slurpy-onearg`, `List.rakumod:215`, is "non-flattening when >1 arg" — and non-flattening is byte-identical to flattening under the one-level SOH encoding). Second, it has a lexer hazard `**@` did NOT: prefix `+` on an array is ITSELF meaningful Raku (`+@a` = numeric context = elem count), so a `"+@"` longest-match rule collides with expression position. `+@a` is a parse error today, so the collision is latent, not live — but adding the rule pre-empts that construct. (b) **ARRAY-NESTING REPRESENTATION ARC** — now known to be the single blocker behind `**@`, `+@`, nested lists `[[1,2],[3]]`, and `.WHAT`→`(Array)` inside aggregates. Multi-rung; schedule deliberately. `rt_make_nested_agg` is the seam. (c) **NAMED ARGS TO USER METHODS** — `meth_call` seam after MRO resolution still needed. (d) Standing items unchanged: exact **`Rat`**, RK-GRAM-3d alternation.
**WATERMARK:** m3 **719/0**, m4 **719/0**. Peers: Icon 14/14, SNOBOL4 7/7. Conflicts **93 s/r / 9 r/r** (ZERO delta this session).
**LAST SESSION:** s2026-07-27b (this session), one commit `6defd71a` (post-rebase origin hash).

Starting watermark m3 707/0, m4 707/0 (the s2026-07-27 cursor's final figure, verified LIVE at 719/0 — the 12-smoke delta was an uncommitted `*%h` WIP already in the tree when this session cloned). Final **m3 719/0, m4 719/0** (+12, all `[m3 PASS] [m4 PASS]`). Peers Icon 14/14, SNOBOL4 7/7 unchanged. Lang-blind gate rc=0. Zero emitter/template files in the diff. All builds `-O0`.

**RUNG — `*%h` SLURPY_NAMED + buffer-overflow fix (`6defd71a`).** `sub f($a, *%h)` parses, binds, and returns correct `.elems`/key-lookup results in both modes. Canonical semantics verified against `BOOTSTRAP.nqp:860` before touching anything: `*%h` receives ONLY unbound nameds (a declared `:$n` consumes `n` first); empty Hash (not `Any`) when none remain. Implementation mirrors the `*@`/`**@` pair exactly — lexer rule `"*%"{ALPHA}{ALNUM}*` → `SLURPY_NAMED`; grammar production pair; `rk_slurpy_named_param` helper; `named_rest = nparams` (1-based slot index) recorded in `rk_register_proc`; `named_rest` field threaded through `stage2.h` → all three `scrip.c` startup-loop sites → m4 TEXT emission → m3 thunk-replay path. Binder skips the collector slot when scanning declared params, then stuffs unbound nameds as SOH/STX-encoded hash into that slot.
**⚠ BUFFER OVERFLOW FOUND AND FIXED (silent wrong answer, not crash).** The collector buffer was sized at a fixed **512 bytes per named pair**. `to_cstring` returns the descriptor's own pointer for STRING (its `VARVAL_fn` tail — only INT/REAL use the scratch buffer), so `strlen(k)/strlen(v)` are unbounded. A 20k-char named value read back as **526** (unfixed) vs **20000** (fixed) — proven A/B, same program, same input. No fault because `rt_ws_alloc` bump-allocates from a pre-reserved mapped island; the next allocation's `memset` zeroes the overflow region silently. Fix: one pre-pass measuring actual `strlen` before allocating. ⚠ **Misattribution caught:** a 2MB segfault initially looked like proof of the overflow; the negative control (2MB string literal, no slurpy) segfaulted identically — that is a pre-existing string-size limit, not this bug. The A/B is the real proof. See `FINDING-2026-07-27-CLAUDE-RK-NAMED-REST-BUFFER-SIZED-FROM-STRLEN-NOT-FIXED-512.md`.
**GENERALIZABLE:** any `rt_ws_alloc` sized with a fixed per-item budget that later calls `to_cstring` + `memcpy(strlen(...))` is defective if STRING descriptors are possible. Fix pattern: measure before allocating.

**TOUCHED:** SCRIP — `src/parser/raku/raku.l` (+1 rule), `raku.y` (+helper, +2 productions), regen `.tab.c`/`.tab.h`/`.lex.c`, `src/lower/lower_raku.c` (+3 lines in `rk_register_proc`), `src/contracts/stage2.h` (+`named_rest`), `src/runtime/rt/rt.h` (+2 decls), `src/runtime/rt/rt.c` (+`named_rest` on `rt_proc_t`, +accessor pair, +autovivify in binder), `src/runtime/runtime_eval.c` (+m3 thunk replay), `src/driver/scrip.c` (+3 startup-loop sites + m4 TEXT emission), `src/runtime/by_name_dispatch.c` (binder loop + **overflow fix**), `scripts/test_smoke_raku.sh` (+12 smokes). `.github` — this cursor + finding doc.

Starting watermark m3 681/0 m4 681/0 per the prior cursor; **verified LIVE before the first edit at 695/0 both modes** (the prior cursor's own final figure — its "681" starting line was its pre-session number). Final **m3 707/0, m4 707/0** (+12, all `[m3 PASS] [m4 PASS]`). Toolchain provenance established BEFORE editing: bison 3.8.2 + flex 2.6.4 reproduce `raku.tab.c`/`.tab.h`/`.lex.c` byte-for-byte. All builds `-O0`. Lang-blind gate green. **Zero emitter/template files in the diff.** 150/150 compilable SNOBOL4 `.s` artifacts byte-identical (the 5 non-regens are `-I lib/` include-path misses in the harness invocation, diagnosed, NOT drift). ⚠ HEAD at session start was `72da0cab` (an ICON commit), NOT the Raku `e9a95691` — parallel sessions, as RULES predicts; `e9a95691` verified an ancestor before building on it.

**RUNG 1 — `**@r` SLURPY_LOL (`56a1cbd2`, +7).** `sub f($a, **@r)` was a hard parse error. New lexer rule `"**@"{ALPHA}{ALNUM}*` → `SLURPY_LOL` (flex longest-match takes it ahead of `"**"`→`OP_POW` regardless of rule order); grammar mirrors the `SLURPY_POS` pair with a `"**@"` marker; `lower_raku.c` maps that marker to `rest_kind=2`; `rt_proc_set_rest_kind` **stopped clamping** (`kind ? 1 : 0` → `kind`, the clamp would have silently collapsed 2→1); three-way bind; new `rt_make_nested_agg`. Correct for scalar args; empty-array-not-`Any` on zero args, canonical.
**⚠⚠ THE PRIOR CURSOR'S COST ESTIMATE FOR THIS RUNG IS FALSIFIED — AND THAT IS THE SESSION'S REAL RESULT.** It said "the plumbing this session built takes it directly, no redesign." The plumbing claim is TRUE; the SEMANTIC claim inside it is FALSE. **Under the one-level SOH encoding, split-on-SOH-then-rejoin-with-SOH is the IDENTITY, so a non-flattening join is BYTE-IDENTICAL to the flattening one.** Proven in standalone C before any SCRIP edit, then end-to-end: `f(0, @x, 9)` gives `.elems` **3** for BOTH `*@` and `**@`; canonical gives **2** for `**@`. ⟹ `**@` differs observably from `*@` ONLY for an Iterable argument, which needs an array-NESTING level the encoding does not have (SOH separates elements, STX separates hash key/value — no third level, no escape). **Do not re-rank slurpy-family work as cheap on the strength of the plumbing existing: the plumbing carries the DECISION, the representation carries the SEMANTICS.** Full trace: `FINDING-2026-07-27-CLAUDE-RK-SLURPY-LOL-AND-NESTING-COINCIDENCE-FALSIFIES-CHEAP-RUNG.md`.
**⚠ M4 REPLAY TRAP HIT AGAIN — IN THE EXACT CODE THAT WARNS ABOUT IT.** `scrip.c`'s `rt_proc_set_rest_kind` replay emitted a **hardcoded `mov esi, 1`** directly beneath its own comment warning that the startup replay is an ALLOWLIST, not a snapshot. A third `rest_kind` would have been silently downgraded to `REST_FLAT_AGG` in every standalone binary while m3 passed clean. Now emits `pe->rest_kind`; verified `mov esi, 2` in the `.s`; **falsified not assumed** — stripping the replay reproduces `list__elems has no stackless slab`. GENERALIZABLE: a replay emitter writing a LITERAL that mirrors a FIELD is a latent downgrade waiting for that field's second value. Grep the other replay emitters for hardcoded `mov esi, 1` beside a multi-valued fact.

**RUNG 2 — `multi` + SLURPY (`6e7f13f1`, +5).** `multi sub f($a, *@r)` died `Cannot resolve caller`. TWO causes, both fixed: (1) `rk_multi_mangle` read `p->c[0]->v.sval` as the param TYPE, but for a slurpy param `c[0]` is the MARKER — so it mangled as type `*@`, which is not just wrong but a **latent GAS hazard** (`*`/`@` are not symbol chars and the mangled name becomes a mode-4 symbol); mangler now maps either marker to the asm-safe token `Slurpy` (fixed IN the mangler, not by moving the marker — the prior cursor's own diagnosis, confirmed). (2) `__multi_call`'s arity gate was an EXACT match (`arity != na` → skip), so a variadic candidate could never be selected at ANY argument count; candidates whose last type component is `Slurpy` now match `na >= fixed` and type-check only the fixed prefix. **Narrowness:** winner selection runs two passes, non-variadic FIRST, so an exact candidate BEATS a variadic one at the same call (canonical: more specific wins) — verified, `f(1)`→exact, `f(1,2,3)`→variadic. `rt_mc_narrower` now compares over the candidate's fixed count, not `na`, so it cannot read past the type list. Non-variadic dispatch is byte-unchanged (pass-0 loop IS the original loop).

**TOUCHED:** SCRIP — `src/parser/raku/raku.l`/`.y` (+regen `.tab.c`/`.tab.h`/`.lex.c`), `src/lower/lower_raku.c`, `src/runtime/rt/rt.c`, `src/runtime/by_name_dispatch.c`, `src/driver/scrip.c`, `scripts/test_smoke_raku.sh` (+12 smokes). Zero emitter/template files. `.github` — this cursor + the FINDING above.

## ▶ RK-ZETA LADDER — un-park Raku ζ onto the ARCH-ZETA §13 two-flavor law (Lon directive 2026-07-14; authored Claude Opus 4.8)

**DIRECTIVE (Lon 2026-07-14):** *"Move all BB's ZETA to the RSP-topped FORTH-like stack, except so-called escapee-type BB's which go on the heap."* DECODE = the **ARCH-ZETA §13 AMENDED TWO-FLAVOR LAW** applied to Raku. Raku is currently DESCOPED per §13 (alloc sites PARK behind a compat shim, PARK-NEVER-DELETE); this ladder un-parks them. **Template = SNOBOL4's proven ZB-FC pattern** (SNOBOL4's mode-invariance gate is GREEN — see `FINDING-2026-07-14-CLAUDE-RK-ZETA-RSP-MODE-INVARIANCE-PROVEN.md`). ζ home goal = `GOAL-IR-IMMUTABLE-EMIT.md` (ZB-FC/ZB-ACT ladder); coordinate there.

**ESCAPEE = family-A LIFO-breaker** (ARCH-ZETA §7/§8): for Raku = block/closure values with a captured ζ-env (RK-BLK) + EVAL/deferred thunks — these heap-promote from birth (GC-visible). Everything else = fixed cells on the RSP FORTH spine.

**STANDING METHOD (SNOBOL4's example, in order — do NOT skip):** (1) bring up under `ZC_ALLOC_MALLOC` + ASan (a wrong-ω free surfaces loudly, not silent corruption); (2) ω-free **CONSTRUCT-AWARE**, never a universal `port==OMEGA` hook (the `bb_match_arbno.cpp` six-`jmp ω` trap — only the F-phase is a true death; correct port model α=alloc+load+save / β=reload / γ=nothing / ω=free); (3) flip to `BUMP_LIFO`, prove the MODE-INVARIANCE GATE byte-identical both modes; (4) retire the shim. Zero-edit swap (flags are NOT a make prereq): `rm -f scrip out/libscrip_rt.so && make ZCFLAGS='-DZC_ALLOC=ZC_ALLOC_BUMP_LIFO' scrip libscrip_rt`.

- [x] DONE — RK-ZETA-0
- [x] DONE — RK-ZETA-1
- [ ] **RK-ZETA-2 — escapee (family-A) Raku BBs heap-promote from birth.** Block/closure captured-ζ-env (RK-BLK) + EVAL/deferred thunks → GC-visible heap block, construct-aware ω-free. Mind the OPEN blocker `FINDING-2026-07-13-CLAUDE-SN4-DEFER-RSP-64KB-DONATION-IS-THE-BLOCKER.md` — it lives in exactly this escapee/deferred-thunk path. GATE: closure/block-capture + EVAL smokes ASan-clean under MALLOC (no leak, no use-after-free).
- [~] **RK-ZETA-3 — FLIP to BUMP_LIFO + prove mode-invariance. CLAIM CORRECTED (Opus 4.8, 2026-07-17b): the "byte-identical" was FLAG DISCONNECTION, not allocator agreement.** The 2026-07-17 proof `diff`ed MALLOC vs BUMP_LIFO builds and found EMPTY (283/0 both modes, DIVERGE=0) — but the follow-up session established the `ZC_ALLOC` knob had **ZERO code consumers** (sole ref = the `zls_dump` label), so `-DZC_ALLOC=ZC_ALLOC_BUMP_LIFO` changed NOTHING in the emitted/runtime path. The two builds were byte-identical because they were the SAME build. The axis is now RETIRED (`c72e3e4b`). The *underlying* claim RK-ZETA-3 wanted — that non-escapee Raku ζ rides the RSP bump-LIFO FORTH spine correctly — is TRUE and holds (283/0 both modes at the committed default), just not provable via this now-deleted knob. RE-scope any real allocator A/B onto a knob that has consumers (`ZC_COLLECTION` is the live one).
- [x] DONE — RK-ZETA-4 (c72e3e4b)

## ★ CURRENT PRIORITY — READ FIRST (Lon, 2026-06-27): GRAMMAR/REGEX UN-PARKED — RK-GRAM-3 IS THE LEAD

Per Lon (2026-06-27) the grammar/regex work is **UN-PARKED** and is now the lead. The OO ladder is essentially complete (every rung `[x]`/`[~]`; the cheap wins are exhausted, remaining items are deferred tails with named costs). **RK-GRAM-3** — the recursive-descent grammar engine seam — is the first rung; mind its standing requirement (in the GRAMMAR/REGEX DIRECTION section below): it needs a **FULL context budget** and the `ARCH-x86.md`/`ARCH-SCRIP.md` reads done **first**, so it should open a fresh session rather than tail onto a spent one. RK-EMIT-MAP/GREP is SUPERSEDED (2026-07-10 — map/grep landed in the lowerer, no boxes needed); RK-GRAM-4..6 sit on RK-GRAM-3. (Superseded prior banner: "RAKU OOP IS THE LEAD," Lon 2026-06-15 — the OO lead delivered its ladder.)

**2026-07-10 (Lon, this session): RAKU-100 LADDER ADDED** — the full-language coverage arc (roast-6.c as the completeness oracle; Phases 0/A–H) now lives in this file: §"RAKU-100 LADDER" directly below the GRAMMAR/REGEX DIRECTION section. RK-GRAM-3 remains the standing implementation lead and is Phase C of that arc; the Phase-0 scoreboard/oracle rungs are deliberately session-tail-sized and may land in any session without displacing the lead. Tier exclusions in that section are PROPOSED — Lon ratifies before the scoreboard's denominator is frozen.

### LEXER STATUS (updated 2026-06-24)
The "flex can't regen" wall is RESOLVED. Root cause: column-0 `/*---*/` separators in the rules section were unrecognized by flex 2.6.4. Fix: indent them by one space in `raku.l`. Verified: flex now regens `raku.lex.c` with rc=0, and the new lexer is behavior-equivalent across all 102 smokes (97/0/7 both modes). `raku.lex.c` is now the flex-2.6.4 regen. **Bison regen is always fine. To regen lexer: `cd src/parser/raku && flex -o raku.lex.c raku.l` (rc=0, 31 conflicts unchanged).**

### OO LADDER
Anchored to Rakudo `Metamodel/{BUILDPLAN,C3MRO,MROBasedMethodDispatch,RoleToClassApplier}.nqp`, `Mu.rakumod`, `Attribute.rakumod`. OO is overwhelmingly RUNTIME (`obj_new`/`meth_call`/`dat_field_*` + the `DatType`/`DATINST_t` model). Parser+lower changes only where new syntax must be recognized.

- [x] DONE — RK-OO-A2
- [x] DONE — RK-OO-C3 (c802035)
- [x] DONE — RK-OO-C5 (c802035)
- [x] DONE — RK-OO-C6 (c802035)
- [x] DONE — RK-OO-D1
- [x] DONE — RK-OO-E1

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

**No language-specific logic in any BB or XA C++ template.** All delineated operations are enveloped in
unique BBs; each BB does NOT have varying runtime behavior depending on language. Templates dispatch on IR
shape and representation flags only. FORBIDDEN inside `src/emitter/BB_templates/` and
`src/emitter/XA_templates/`: language enums/guards (`IR_LANG_*`, `LANG_*`, `is_<lang>`), language-named
template functions/files/dispatch arms, and hardcoded language-builtin names. Behavior that differs by
language belongs in the runtime (by-name dispatch) or in LOWER (a different IR shape → its own unique BB) —
never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (XA scanned clean 2026-06-03); fix
ladder: LB-* in `GOAL-PASCAL-BB.md`. COMPLETION TEST: the audit's Tier-1 grep over `BB_templates/` +
`XA_templates/` returns 0 sites.

## ▶ GRAMMAR/REGEX DIRECTION (2026-06-14; UN-PARKED by Lon 2026-06-27) — NOW THE LEAD

RK-GRAM-3 (recursive-descent grammar engine) is **UN-PARKED and is the lead** (Lon 2026-06-27). Direction below is authoritative. Grammars register and `.parse` dispatches end-to-end in all three modes today (`f3b1837`); recursive grammars are the remaining gap. Reminder: the RK-GRAM-3 rung note requires a FULL budget + `ARCH-x86.md`/`ARCH-SCRIP.md` reads first — start it in a fresh session.

**DIRECTION (Lon 2026-06-14):** NFA is the WRONG primary engine for top-down recursive-descent. The NFA-on-Byrd-boxes apparatus is DELETED (`d63c374`). Real Raku's matcher IS recursive descent (backtracking cursor machine). Subrule `<name>` recursion is provably beyond any finite automaton → needs recursive descent. The C NFA matcher `re.c` (`nfa_build`/`nfa_exec`) is KEPT for `~~ /regex/` only.

- [x] DONE — RK-EMIT-MAP/GREP
- [ ] **RK-GRAM-3 (THE SEAM) — native recursive-descent grammar engine on Σ/δ/Δ.** REPLACES `gram_expand`'s flatten-to-NFA (depth-16 stopgap). Per the X86-64 FACT table the subject triad is reserved for Raku INSIDE the grammar/regex slab: **R13=Σ subject base, R14=δ cursor, R15=Δ end bound**, δ CALLEE-SAVED so it stays ambient across subrule recursion (the called rule's box advances δ and the caller sees it on return — no arg marshaling, no "current position" frame field). Four ports keep their pattern-lang meaning: **α=fresh entry, β=resume/backtrack-retry, γ=match advanced δ, ω=fail**. Choice points save δ into the per-activation ζ=r12 frame (a δ-snapshot slot — NOT a value stack; the Icon scan "save δ on β, restore and fail" discipline). Captures record `(from=δ-at-α, pos=δ-at-γ)` → Rakudo `Match` `$!from`/`$!pos`. Grammar compiles ONCE to box code; each `.parse` loads Σ/δ/Δ and jmps to the TOP box; success = TOP reaches γ with δ==Δ (full) or any γ (subparse). **STANDING REQUIREMENT: fresh full-budget session; read `ARCH-x86.md` (Boxes-are-stackless + Flat-BB ABI) + `ARCH-SCRIP.md` + `ARCH-ICON.md` §"String scanning" + `src/emitter/bb_regs.h` FIRST.** Templates stay LANGUAGE-BLIND (FACT RULE) — these boxes dispatch on IR shape, not on `is_raku`; cross-language safety holds because only the Raku lowerer emits these IR kinds. STEPS (each both-modes-green, flatten kept as fallback for un-migrated shapes so the suite never regresses):
- [x] DONE — RK-GRAM-3a
- [x] DONE — RK-GRAM-3b
- [x] DONE — RK-GRAM-3c
  - [ ] **RK-GRAM-3d — alternation (`IR_ALT`) with δ-restore-on-β.** Try alt 1; on its ω, restore the saved δ and re-pump alt 2's α; all-ω → alt ω. GATE: `rule TOP { <digit> | <alpha> }` PASS both modes; backtracking PROVEN by `rule TOP { "ab" | "ac" }` on "ac".
  - [ ] **RK-GRAM-3e — subrule call = recursion into another box graph (THE actual SEAM).** `<name>` lowers to recursion into the named rule's box graph with Σ/δ ambient in the callee-saved registers. GATE (two parts): (1) non-recursive `rule TOP { <word> }` / `token word { <alpha>+ }` PASS natively; (2) **the milestone the flatten engine cannot reach** — `rule TOP { "a" <TOP> | "a" }` on "aaa" PASS both modes.
  - [ ] **RK-GRAM-3f — quantifiers `*`/`+`/`?` greedy with backtrack.** GATE: `rule TOP { <digit>+ }`, `rule TOP { <alpha>* <digit> }` PASS natively with backtracking (longest match then yield-back).
  - [ ] **RK-GRAM-3g — retire the flatten fallback for `.parse`.** Once every grammar smoke passes via native boxes, delete `gram_expand`'s NFA route for grammar `.parse` (KEEP `re.c`/`nfa_build` for `~~ /regex/`). GATE: all grammar smokes green both modes with zero `nfa_build` on the `.parse` path; EXCISED count unchanged (map/grep + `~~` remain).
- [ ] **RK-GRAM-4 — captures + Match tree.** Reify `(from,pos)` snapshots and named/positional captures into a `Match` object; `$m<name>` / `$m[i]` access (parser gap noted: `$var<word>` Match-subscript not yet parsed). Sits on 3e.
- [ ] **RK-GRAM-5 — LTM + proto/`multi` token dispatch.** Longest-token-match alternation ordering; proto-token candidate dispatch. Sits on 3d/3e.
- [ ] **RK-GRAM-6 — actions + adverbs + control.** `make`/action-class invocation, `:i`/`:s`/`:ratchet` adverbs, `<?>`/`<!>` assertions. Sits on 4/5.

---

## ▶ RAKU-100 LADDER — ENTIRE-LANGUAGE COVERAGE ARC (Lon directive 2026-07-10 · authored Claude Fable 5)

**COMPLETION DEFINITION (computed, never prose — the `handoff_status.sh` law applied to coverage):** 100% of IN-TIER roast 6.c test files PASS **UNMODIFIED** under BOTH m3 `--run` AND m4 `--compile`. The oracle is **roast**, the official Raku specification ("any compiler that passes the tests is deemed to implement that version"); the manifest is `refs/rakudo-main/t/spectest.data.6.c` (**1,154 files**, counted 2026-07-10 from the uploaded rakudo-main tree). Roast's own fudge/skip/todo mechanism maps 1:1 onto our XFAIL/EXCISE discipline — a fudged file is an XFAIL, never a silent pass. Coverage claims come ONLY from `scripts/raku_roast_scoreboard.sh` stdout committed to `RAKU-COVERAGE.md`; the feature-weighted hand estimate of 2026-07-10 (~14% of full surface: 230 inline + 47 file smokes, deep S12-OO spike ~50%, thin elsewhere) is SUPERSEDED by the scoreboard's first committed run and must not be re-quoted after it.

**TIER TABLE (PROPOSED — Lon ratifies before the scoreboard denominator is frozen; stamp date here when ratified):**
| Tier | Sections | Files | Meaning |
|------|----------|-------|---------|
| EXCLUDED | S01 Perl-5 interop (11) · S15 Unicode/NFG (69; byte-string stance) · S26 Pod (19) · S22 (1) · precompilation · NativeCall | ~100 | not part of "100%" |
| TIER-C (Lon decision: thin or excluded) | S17 concurrency (65; thin start/await over the pthread coexpr substrate is plausible later) · S24 (3) | ~68 | decide at Phase H |
| IN-TIER | everything else (S02/S03/S04/S05/S06/S07/S09/S10/S11/S12/S13/S14/S16/S19/S28/S29/S32 + integration) | **~985** | the 100% target |

**STANDING LAWS for every rung below:** both-modes-green (m3+m4) + the named GATE; representation migrations keep the old path as fallback behind a gate so the suite never regresses (the RK-GRAM flatten discipline); canonical semantics come from `refs/rakudo-main/src/core.c/*.rakumod` FIRST, prose second (CONSULT CANONICAL SOURCES rule); all FACT RULES in this file (language-blind templates, no value stack, ζ-frame storage, `x86()`-only encoders) bind unchanged.

### PHASE 0 — INSTRUMENT FIRST (session-tail-sized; may land in any session)
- [~] **RK-100-0a — roast + rakudo oracle. HALF-DONE (s2026-07-15).** roast + rakudo cloned to `refs/`; manifest computed = 1,154; in-tier denominator computed = 986. STILL OPEN: a PREBUILT rakudo binary as the `.expected`-minting oracle (scoreboard currently trusts each file's TAP self-report; it cannot catch a well-formed-but-wrong answer). Also open: 41 manifest files absent from the roast tree (repo-tag skew). Original text: Clone `Raku/roast` at the 6.c tag beside `refs/rakudo-main`; obtain a PREBUILT rakudo binary as the `.expected`-minting oracle (the fresh-iconx pattern — do NOT build the uploaded tree, it needs nqp+MoarVM). GATE: `raku --version` rc=0; in-tier manifest file count computed by script and committed.
- [x] DONE — RK-100-0b
- [x] DONE — RK-100-0c
- [ ] **RK-BLK — blocks/closures native.** Canonical: `Block.rakumod`/`Code.rakumod`.
  - [~] **RK-BLK-a** — Block value DESCR (proc + ζ-env ptr); `my $b = { ... };` `$b()` invoke. GATE: store/invoke smoke both modes. **STEP 1 LANDED both modes (s2026-07-15b, Opus 4.8):** `DT_BLK` descriptor carries the hoisted proc name; store + `$b()` invoke work via the runtime proc registry (`__blk_ref`/`__blk_invoke`, no new box/template); anon `sub {…}` too. GATE met (7 smokes, m3+m4, fail-set identical to baseline). REMAINING for full RK-BLK-a: the descriptor has NO ζ-env pointer yet (no lexical capture — that is explicitly RK-BLK-c), and `sub{…}()` immediate-invoke / block-args / top-level statement-blocks / pointy-params are the next increments.
  - [ ] **RK-BLK-b** — pointy `-> $x { }` params; `.()`; implicit `$_` single-arg block.
  - [ ] **RK-BLK-c** — lexical capture (outer read, then outer write-through) via ZLS2 activation chains — **COORDINATE with the ZB-ACT ladder in `GOAL-IR-IMMUTABLE-EMIT.md`; NEVER fork a parallel activation mechanism.**
  - [ ] **RK-BLK-d** — cash the blocked tails, one step + smokes each: value-position `my @a = map {...}, @xs` · `sort` with comparator block · closure attr defaults (`has $.x = computed()`) · BUILDPLAN op-400 · `where` constraints.
- [ ] **RK-VAL — numeric tower.** Canonical: `Rat.rakumod`, `Int.rakumod`, `Num.rakumod`, `Numeric.rakumod`.
  - [ ] **RK-VAL-a** — Num floats end-to-end (literals, arith, Raku-faithful stringification).
  - [ ] **RK-VAL-b** — **Rat**: decimal literals ARE Rat, normalized arith, `.nude`/`.numerator`/`.denominator`, Rat↔Num contagion, faithful `.gist`/`.Str` (`0.1` prints `0.1`). THE distinctive Raku numeric; roast assumes it everywhere.
  - [ ] **RK-VAL-c** — big Int (arbitrary precision; gmp-vs-own-limbs is a Lon runtime-dependency decision). GATE: `say 2**100`, factorial 25, both modes.
  - [ ] **RK-VAL-d** — radix literals `0x/0o/0b/:16<…>`; allomorph (`IntStr`) tails.
- [ ] **RK-AGG — real aggregates** (retire the `\x01` string encoding). Substrate to reuse: the Icon lists machinery landed 2026-07-06 (`04595cd1`).
  - [ ] **RK-AGG-a** — descriptor Array behind the EXISTING runtime entry points (`.push/.pop/.shift/.unshift/.splice/.elems`), `\x01` kept as fallback behind a per-shape gate. GATE: all current array smokes green BOTH paths.
  - [ ] **RK-AGG-b** — nesting (`[[1,2],[3]]`), `@a[i]` lvalue, slices `@a[1,3]`, `*-1` Whatever index.
  - [ ] **RK-AGG-c** — descriptor Hash, `%h{k}` lvalue, slices, `.keys/.values/.kv/.pairs`, `:exists`/`:delete` adverbs, autovivification.
  - [ ] **RK-AGG-d** — Pair; List-vs-Array mutability split; Seq basics; `.list`/`.Array` coercions.
  - [ ] **RK-AGG-e** — **RETIRE `\x01`**. GATE: grep for the separator constant in runtime == zero live sites (compat shims only); full smoke suite green.

### PHASE B — STATEMENT/OPERATOR BREADTH (S03/S04)
- [ ] **RK-CTRL** — `loop`/`repeat`, `last`/`next`/`redo` (+labels), statement modifiers (`EXPR if/unless/for/while COND`), `do` blocks, ternary `?? !!`, `with`/`orwith`/`without`, `once`.
- [ ] **RK-OPS** — chained comparisons · `//`/`andthen`/`orelse` · string relops `lt le gt ge eq ne` + `cmp`/`leg`/`<=>` · `x`/`xx` · Range-as-value object · `...` sequence op; POST-AGG: `Z` zip · `X` cross · `[op]` reduce · `>>op<<` hyper · `R`/`!`/`=` meta.
- [ ] **RK-SMART** — the `~~` smartmatch dispatch table (type/regex/range/junction/list arms) + `given`/`when` riding it.
- [ ] **RK-JUNC2** — TRUE junction autothreading through calls and operators (first VERIFY how the current jct_* smokes pass, then generalize; no special-case residue).
- [ ] **RK-BUG-SWEEP** — monitor-first per RULES.md: (1) ~~`if ($x < $y)` variable-operand relop misthread~~ **FIXED s2026-07-23** (`lower_cond` `TT_SEQ` arm); (2) callwith/call-arg binop marshaling (`abs($x+10)`); (3) `$var<word>` Match-subscript parse gap.

### PHASE C — GRAMMAR/REGEX = **the RK-GRAM-3a..g → 4 → 5 → 6 ladder in the GRAMMAR/REGEX DIRECTION section ABOVE** (single home — NOT duplicated here), then:
- [ ] **RK-RX-OPS** — `s///`, `.subst`/`.match`/`.comb`/`.split` with regex, `tr///`, `:g`/`:i`/`:x` adverbs, `$/` `$0` `$<name>` variables.

### PHASE D — SIGNATURES (S06)
- [ ] **RK-SIG** — named args at call sites (`:name(v)`, `name => v`) · optional `$x?` · defaults `$x = e` (post-BLK for non-const) · slurpy `*@`/`*%` · `|` capture pass-through · `-->` return-type check · destructuring sub-signatures · `where` (post-BLK).
- [ ] **RK-FN2** — anonymous `sub`, WhateverCode (`* + 1`), `&foo` sigil, explicit `proto sub {*}`.

### PHASE E — OO TAILS (collection order for the DEFERRED items whose single home stays each OO rung's own note above): enum/subset (G5) → `but` runtime mixin (G4) → prefix/postfix overload call-site seams → parametric roles `R[::T]` → role-does-role → `FALLBACK` → `AT-KEY`/`AT-POS` container protocols.

### PHASE F — EXCEPTIONS + PHASERS (S04)
- [ ] **RK-EXC2** — typed `X::` hierarchy as real objects, `when X::Foo` inside CATCH, `Failure`/`fail` soft exceptions, `$!` variable. (try/CATCH base LANDED — 13 smokes.)
- [ ] **RK-PHASE** — `ENTER`/`LEAVE`/`KEEP`/`UNDO`, `FIRST`/`NEXT`/`LAST`, `state` vars, `BEGIN` (const-fold tier)/`END`.

### PHASE G — S32 LIBRARY SWEEP (191 files)
- [ ] **RK-LIB-STR / RK-LIB-LIST / RK-LIB-NUM / RK-LIB-HASH** — batch rungs, ~10 methods per step, **ORDERED BY SCOREBOARD YIELD** (the instrument names which missing methods unlock the most roast files — never guess the order). `sprintf`/`.fmt` is its own step.

### PHASE H — SYSTEM
- [ ] **RK-IO2** — `IO::Path`, `open`/`close`/`get`/`lines`/`slurp`/`spurt`/`dir`, file tests (the fileio38/stdio39 smokes are the seed).
- [ ] **RK-MAIN** — `MAIN` + auto-usage (S19, 6 files).
- [ ] **RK-MOD** — single-file `unit module/class`, `use` of a sibling file, `EXPORT` (tier-B minimum: multi-file programs work).
- [ ] **RK-CONC** — TIER-C, Lon decision: thin `start`/`await`/`Promise` over the pthread coexpr substrate, or EXCLUDED.

### META-RUNG — RK-ROAST-CLIMB (standing)
Every phase-close re-runs the scoreboard and commits the `RAKU-COVERAGE.md` delta. The ladder is DONE when the scoreboard — not prose — prints 100% of in-tier files PASS unmodified, both modes.

**MAGNITUDE (honest, so nobody is surprised):** the S12 OO spike cost ~15 sessions for ~50 files of surface; in-tier is ~985 files ⇒ this is a **60–100-session arc**. Phase A is the highest-leverage 10 — the three walls gate more roast files than everything else combined.

---

## ⛔ `bb_bin_t` IS ABOLISHED — PATCH METADATA TRAVELS IN-BAND; NO FUNCTION COUNTS BYTES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**The `bb_bin_t { sites, labels, is_def, bytes }` struct and `bb_emit_asm_result(out, bin)` /
`bb_emit_asm_result_pairs(out)` are DELETED (Lon directive 2026-06-02). No box may name `bb_bin_t`, declare a
`bb_bin_t bin`, or call `bb_emit_asm_result`.** The struct was the carrier for a hand-counted / FUNCTION-counted
patch-offset table — the `bin.sites.push_back((int)b.size())` idiom, which is invalid: it computes a patch offset
with `b.size()` (a function of the running buffer) instead of letting the position be DISCOVERED. That idiom is the
exact nonsense the template revamp kills, and the strongest way to kill it is to remove the type so the idiom does
not COMPILE — the same enforcement-by-deletion as the no-`pBB`/`_.node` rule (a grep gate is unnecessary when the
compiler rejects it).

**THE ONE WAY: every BB template returns ONE concatenation of `x86(...)` calls and is emitted by
`bb_emit_x86(out)`.** Patch sites are TAGGED RECORDS inside that string (`L` literal bytes / `J` rel32-to-port /
`D` define-port / internal-label `L(n)` / pair-loop `E`/`F`); `bb_emit_x86` walks them and DISCOVERS each byte
position as it copies. There is NO separate offset list, so NOTHING can drift and no function ever counts bytes.
This SUPERSEDES the earlier "TWO LITERAL FORMS ONLY" framing of the BINARY arm: the hand-coded literal byte map
with a literal offset tuple was a TRANSITIONAL form; the in-band record stream is the END form, and it is what the
`b.size()` ledger was driving toward — the ledger reaches zero when the last `bb_bin_t` user is converted, not by
rewriting offset tuples by hand.

**FORBIDDEN:** `struct bb_bin_t`, `bb_bin_t bin`, `bb_emit_asm_result(...)`, `bin.sites`/`bin.labels`/`bin.is_def`,
and `(int)b.size()` (or any `.size()` of a running byte buffer used as a patch offset) anywhere in
`src/emitter/BB_templates/`, `XA_templates/`, or `emit_str.*`. The carve-out for `bb_emit_asm_result` walking a
finished string is GONE — that function no longer exists. (A box NOT YET converted is a LOUD `x86_bomb(msg)` stub
— `extern "C" void bb_foo(...) { bb_emit_x86(x86_bomb("bb_foo: …")); }` — which COMPILES + LINKS so SCRIP stays
green and ABORTS beautifully when reached; each owning session replaces its stubs with real `x86()` concatenations
as its own test reaches them.)

**ENFORCEMENT:** structural (the compiler) — `bb_bin_t` is declared nowhere, so any use fails to compile. Plus a
one-line gate `scripts/test_gate_no_bb_bin_t.sh` (comments stripped): `bb_bin_t` / `bb_emit_asm_result` live code
references == 0. **COMPLETION TEST:** (a) `emit_str.h` declares neither `bb_bin_t` nor `bb_emit_asm_result`; (b)
the gate reads zero; (c) every BB template is emitted via `bb_emit_x86`; (d) `make scrip` + `make libscrip_rt`
rc=0; (e) this FACT RULE body is byte-identical across the four GOAL-*-BB files.

## ⛔ ONE MEDIUM, INVISIBLE — NO `IF(MEDIUM_BINARY,…)` INSTRUCTION BRANCH, NO RAW-BYTE PRODUCER IN A TEMPLATE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**A template NEVER writes an instruction twice — once as GAS text, once as raw bytes — and NEVER branches on the
medium to pick between them (Lon directive 2026-06-02).** The forbidden shape (the exact nonsense this rule kills):
```
  + IF(MEDIUM_TEXT,  std::string(" mov rbx, rsp\n"))      // same instruction…
  + IF(MEDIUM_BINARY, x86_Lrec(x86_b3(0x48, 0x89, 0xE3))) // …written a second time as bytes
```
Every instruction goes through ONE `x86(mnem, …)` call; the encoder switches medium INTERNALLY, so the template
body is identical for BINARY and TEXT and a reader cannot tell which medium is active. If an instruction has no
`x86()` form yet, ADD an encoder + dispatch case to `x86_asm.h` (one place, byte-verified vs `as`) — NEVER
hand-encode it inline in the template. The missing encoder is the bug; the medium-branch is the symptom.

**FORBIDDEN inside `src/emitter/BB_templates/*.cpp`:** the raw-byte producers `x86_Lrec`, `x86_Jrec`, `x86_Drec`,
`x86_b1(`, `x86_b2(`, `x86_b3(`, `bytes(`, `u8(`, `u32le`, `u64le`; and any `IF(MEDIUM_BINARY, …)` or
`IF(MEDIUM_MACRO_DEF, …)` carrying instruction bytes. Those record/byte primitives are PRIVATE to `x86_asm.h` (the
encoders' implementation); a template only ever sees the `x86(...)` front-end + the markers (`L(n)`, `FR(off)`,
`FRQ(off)`, `PORT_*`) and the LOUD `x86_bomb(msg)` stub. **ALLOWED carve-out — TEXT-ONLY ANNOTATIONS WITH NO BYTE
FORM:** a box's leading `α:` label (`s_1asm(std::string(_.lbl_α)+":"`) and comments (`s_comment(...)`) exist only
in the GAS arm, so `IF(MEDIUM_TEXT, <comment-or-label>)` with NO matching `IF(MEDIUM_BINARY, <bytes>)` is fine; an
`IF(MEDIUM_TEXT,<gas-instruction>) + IF(MEDIUM_BINARY,<bytes>)` PAIR is the violation. Non-x86 platform arms
(JVM/JS/NET/WASM) are out of scope (X86 ONLY for now) and keep their `s_*asm` text.

**CORRECTION RECORD (Lon 2026-06-06):** RULES.md TEMPLATE-ONLY EMISSION is now corrected to MATCH this rule; its former
"duplicate the byte-producing code into each template file" clause (515aa7d6, 2026-05-28) is DEAD — it predated the
2026-06-02 directive and said the opposite. Restated plainly: ZERO BINARY emission anywhere in a `bb_*.cpp` — not in the
top-level `*_str`, not in any helper it calls (a static helper in the template file is INSIDE the fence; relocating bytes
into helpers changes nothing). `x86()` internals (`x86_asm.h`) are the ONLY place BINARY and TEXT are emitted, side-by-side.

**ENFORCEMENT:** gate `scripts/test_gate_template_medium_invisible.sh` (comments stripped): in `BB_templates/*.cpp`,
the raw-byte producers + `IF(MEDIUM_BINARY`/`IF(MEDIUM_MACRO_DEF` count == 0 (informational WIP baseline; `--strict`
enforces zero). **COMPLETION TEST:** (a) zero raw-byte producers and zero `IF(MEDIUM_BINARY,…)`/`IF(MEDIUM_MACRO_DEF,…)`
in any `BB_templates/*.cpp`; (b) every instruction emitted via an `x86(...)` call; (c) the gate green under `--strict`
and in the Session-Setup gate list; (d) this FACT RULE body byte-identical across the four GOAL-*-BB files.

**THREE FACES OF ONE END STATE.** This rule, the `bb_bin_t`-ABOLISHED rule above, and the no-`pBB`/`_.node` rule are
three faces of ONE converted box: pure `x86()` concatenation reading only `_`. A box that still hand-encodes bytes
ALSO still carries `bb_bin_t` and ALSO branches on the medium; converting it to `x86()` clears all three at once. The
three gates therefore reach zero TOGETHER, box-by-box, as the revamp completes — the prison is escaped only by
finishing the conversion.

## ⛔ NO C BYRD-BOX FUNCTIONS — A BOX IS ENTERED BY JUMPING TO ITS α/β LABELS, NEVER A `(ζ, int entry)` C CALL (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**There is NO such thing as a C byrd-box function. The "brokered BB" concept is ABOLISHED.** A byrd box is
EMITTED machine code. It has exactly TWO entry points, and they are **LABELS** — α (fresh entry) and β
(resume). Control reaches a box by **JUMPING to one of those labels**. A box is NEVER a C function, is NEVER
reached by a C call, and NEVER takes an integer `entry` argument to select α vs β. The C signature
`DESCR_t NAME(void *ζ, int entry)` — a ζ-state pointer plus an `int entry` α/β selector — is **FORBIDDEN**.
It was the discredited brokered-BB calling convention (an "entry kludge"); it is gone. The ONLY driver is the
**mode-2 BB-graph interpreter** (`bb_exec.c`), which walks the IR graph directly and IS the broker/driver;
**modes 3 and 4 are native code in which boxes thread control by jumping between α/β labels** (RULES X86-64
register / subject-model convention) — never through a function pointer plus an `entry` integer. There is no
`bb_broker` driver and no `(ζ, int entry)` box anywhere.

**HISTORY — READ THIS, because it is why the rule now exists in this strongest form.** This prohibition has
stood for **AT LEAST TWO MONTHS**. Lon ordered these C `(ζ, int entry)` byrd boxes DELETED at least **THREE
separate times**, and each time a session either declined, re-introduced them, or held/reverted the deletion
"to keep the build green." A prior plain rule (RULES.md "NO C BYRD-BOX FUNCTIONS") did **not** hold. They
were finally deleted **2026-06-01** — the `pl_*_fn` family (all of `pl_broker.c`), `gen_bb_dcg`,
`gen_bb_oneshot`, `resolve_bb_dcg`, `bb_deferred_var`/`_exported`, `fail_box`, the dead `bb_cap`/`bb_atp`
declarations, **and the `bb_broker` driver itself** (`bb_broker.c`). **KEEPING THE BUILD GREEN IS NOT A
LICENSE TO PRESERVE A FORBIDDEN BOX.** When this signature and a green build conflict, the **signature
loses**: delete the box and tear out its callers (the brokered execution path — Prolog `--run`, brokered
pattern scan, brokered generators — is removed, not preserved). A broken build pending the caller teardown is
acceptable; a surviving `(ζ, int entry)` box is not.

**COMPLETION TEST:** (a) `grep -rnE 'DESCR_t[[:space:]]+[A-Za-z_]+[[:space:]]*\([[:space:]]*void[[:space:]]*\*[[:space:]]*[a-z]*[[:space:]]*,[[:space:]]*int[[:space:]]+entry' src/ --include=*.c --include=*.cpp --include=*.h | grep -v typedef` == 0 (no C byrd-box definition or declaration with the `(ζ, int entry)` signature); (b) no `bb_broker` driver function exists; (c) every emitted box is entered by a jump to an α or β label, never a C call with an `entry` int; (d) this FACT RULE body is byte-identical across the five GOAL-*-BB files.

## ⛔ NO AST AND NO IR DURING MODE-3/MODE-4 EXECUTION (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**During the EXECUTION of a mode-3 (`--run`) or mode-4 (`--compile`) program, NOTHING reads or writes the AST (`tree_t`) or the IR (`IR_t`/`IR_graph_t`).** (Lon directive, 2026-06-13.) The compiler reads the IR exactly ONCE — before execution — to emit the mode-3 RX-slab image or the mode-4 `.S` source; thereafter the produced machine code runs with ZERO reference to either tree. A box's runtime values live INSIDE the box (RO `[rip+disp]`, RW `[ζ=r12+off]`); a runtime helper (`rt_*`) operates only on `Term*`/`DESCR_t` values, never on `IR_t*` or `tree_t*`. This subsumes the IR-NEVER-TOUCHED rule and extends it to the AST: an AST walker that does not EMIT IR is worthless — it may not exist on any run path, not even for mode 2. (The mode-2 `--run` IR-graph interpreter `IR_interp_once` is the ONLY sanctioned IR walker, and it is reachable ONLY via `--run`, never from a mode-3/4 produced binary.)

**THE ONE EXCEPTION — `EVAL()` and `CODE()`.** SNOBOL4's `EVAL` and `CODE` are dynamic-compilation builtins: by definition they compile a string into executable form AT RUNTIME (`CONVE_fn`→`EXPVAL_fn`, the `g_eval_str_hook`/`g_eval_pat_hook` rail). Reading/building an IR (or equivalent) at runtime is intrinsic to their meaning, so the prohibition does NOT apply INSIDE `EVAL()`/`CODE()` (and only there). No other construct, builtin, or runtime helper may read or write AST/IR during mode-3/4 execution.

**FORBIDDEN on the mode-3/4 run path:** any `rt_*` (or template-called) function that takes an `IR_t*`/`IR_graph_t*`/`tree_t*`, walks `->operands`/`->c[]`/`->t`/`->op`, reads `IR_LIT(...)`/`IR_EXEC(...)`, dispatches on `IR_e`/`tree_e`, or bakes a live `IR_t*`/`tree_t*` address into emitted code (the `emit_term_from_node_bin` pattern). A box NOT YET converted is a LOUD `x86_bomb(msg)`, never a silent IR/AST read.

**GUARD:** the run path's runtime objects are `Term*`/`DESCR_t` only. **COMPLETION TEST:** (a) no GZ template (`bb_cell_*`) and no mode-3/4-reachable `rt_*` reads AST/IR (grep of the run-path helpers for `IR_t*`/`tree_t*`/`IR_LIT`/`->op`/`->t` == 0, excepting `EVAL`/`CODE`'s `CONVE_fn`/`EXPVAL_fn` rail and the mode-2-only `IR_interp_once`); (b) no function bakes a live `IR_t*`/`tree_t*` into emitted bytes; (c) FACT RULE body byte-identical across all five GOAL-*-BB files.

## ⛔ NO VALUE STACK — EVER (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**SCRIP HAS NO VALUE STACK. NO SESSION, IN ANY LANGUAGE, MAY CREATE ONE.** (Lon directive, 2026-05-31.)
There is nothing like a value stack in SCRIP — every value a BB graph computes or holds at run time lives
INSIDE a box: a READ-ONLY operand constant reached `[rip+disp]` into sealed data, or a READ-WRITE slot
reached `[ζ=r12+off]` in the per-sequence one-register frame (the `test_sno_1.c`/`test_icon.c` named-slot
model). A consumer reads a producer's result directly from that producer's slot. A value is NEVER pushed
to or popped from a global stack, and intermediate producer→consumer values are NEVER threaded through a
name-table round-trip. This is the same law as the PER-BOX LOCAL STORAGE FACT RULE; this rule states the
prohibition in the strongest, language-independent form so it cannot be re-introduced from any session.

**The `g_vstack` global array is DELETED (2026-05-31) and must NEVER be resurrected** — nor any equivalent
under a different name (`*_vstack[]`, `value_stack`, `g_estack`, a hand-rolled `WamWord[]`/`DESCR_t[]`
push/pop arena used to pass values between boxes, etc.). FORBIDDEN to (re)introduce: a global/static array
whose purpose is to push a box's value and pop it in a consumer; `rt_push_*`/`rt_pop_*`/`vstack_*` value
traffic; any `*_push`/`*_pop` helper that moves an *intermediate* value between boxes. (KEEP, NOT a value
stack: the Prolog trail `g_resolve_trail`/`rt_pl_trail_*` — a binding-undo ledger; the choice-point ledger
`g_resolve_bfr`/`resolve_choice` — the irreducible cross-node resume spine; the C call stack used for
genuine recursion; an ARBNO-style explicit indexed per-activation frame array. None of these is a value
stack.) The residual `vstack_*`/`rt_vstack_ops_t` SCAFFOLDING left in `src/runtime/rt/rt.c` is dead/aborting
(`g_ops` only ever points at `g_default_ops`, whose push/pop/peek `abort()`); it is being removed rung by
rung (the VSX ladder) and must NOT be wired up to anything — adding a real backing store to it = creating a
value stack = a violation.

**GUARD:** `scripts/test_gate_no_vstack.sh` (informational baseline now; flips to a HARD `--strict`
zero-check at VSX-8). It greps (comments stripped) ACROSS ALL `src/` for `g_vstack`/`vstack_push`/
`vstack_pop`/`vstack_peek`/`rt_vstack_*`. The `g_vstack` token is already at ZERO and must STAY at zero;
the rest trend to zero as the scaffolding is deleted. Any session that makes the `g_vstack` count non-zero,
or that adds a new value-stack array under any name, has violated this rule. **COMPLETION TEST:** (a)
`grep -rn 'g_vstack' src/` == 0 (code AND comments); (b) no new global/static push/pop value arena exists;
(c) `scripts/test_gate_no_vstack.sh` `g_vstack` line reads 0; (d) the FACT RULE body is byte-identical
across all five GOAL-*-BB files.

## STATUS

Raku is LIVE through `lower.c` (RK-LOWER-0..5 done). Post-SMX-4: no Stack Machine engine; ONE unified `lower.c`; `IR_*` node taxonomy; BB run-path. Mode 2 (`--run`) DELETED 2026-06-15. Two native modes only.

**Current score (2026-06-27): Raku m3/m4 209 PASS / 0 FAIL / 7 EXCISED / 216.** 7 EXCISED = 4 map/grep + 3 `~~` regex, all correctly declined. Peers: Icon 12/12, SNOBOL4 7/7, Prolog m3/m4 5/5.

**Prior baseline note (2026-06-24): 134 PASS / 0 FAIL / 7 EXCISED / 141.**

---

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified AST→IR lowerer is **ONE file** — `src/lower/lower.c` (formerly `lower2.c`, the new tree root after old `lower.c` was deleted 2026-05-31) — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** (every `TT_*`). SNOBOL4, Icon, and Prolog are developed CONCURRENTLY in SEPARATE sessions, all writing into this one file. Each language adds ARMS the others don't; the discipline below makes three concurrent sessions **conflict-free and mutually beneficial** (one session's added case label / shared helper is the next session's ready slot):

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). No per-language lowering functions, no per-language files. One kind → one case → language arms inside.

3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language's arm.** This is what makes the three sessions' diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer's proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED. ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit. Each cat's proof cases are ADDITIVE (append your own; never delete a peer's). Green = your arm wired right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c`; (b) every case's language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

> **⚠ FOURTH-MUSKETEER NOTE (Raku spin-up, 2026-05-31).** The FACT RULE body above is reproduced
> **byte-identical** to the three existing carriers so its md5 (`5097ed94`) still matches — Raku
> joins as a fourth carrier of the SAME block. The roster line still names three files and the body
> still says "three" by design: expanding "three → four" (roster + every "three"/"all three") is a
> **lockstep edit of all four GOAL files in ONE commit** per clause 5, to be performed when the Raku
> session is actually fired up, not piecemeal here. Until then Raku obeys the rule exactly as written
> (its `cx.lang==IR_LANG_RKU` arms go INSIDE existing cases; missing arms fall to `lower_unhandled`).

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` over the shared `IR_e` — fanning out to **per-box template functions** under `src/emitter/{BB,SM,XA}_templates/`. Every byte of emitted machine code lives INSIDE a template fn reached ONLY via this dispatch (RULES.md TEMPLATE-ONLY). SNOBOL4, Icon, and Prolog fill emitter boxes CONCURRENTLY in SEPARATE sessions, all writing into this one dispatch + this one template tree. The discipline below makes the three sessions **conflict-free and mutually beneficial** (one session's dispatch case + template file is the next session's ready slot), exactly mirroring the SHARED-LOWERER rule:

1. **ONE DISPATCH CASE PER IR KIND.** Each `IR_*` is at most ONE `case` label in `emit_core.c`. If your language's kind has no case → ADD it (one line: `case IR_FOO: bb_foo(nd); return 0;`). If it exists → it already calls the right template; do not duplicate. **NEVER duplicate the label.** Append new cases at the END of the language's contiguous block (SNOBOL `IR_PAT_*` block, Prolog `IR_GOAL/ARITH/BUILTIN/LOGICVAR/ATOM/STRUCT/UNIFY/CUT/DISJ/GCONJ` block, Icon `IR_EVERY/ALT/LIMIT/SCAN/TO/…` block) so the three sessions' inserts land in different hunks → git auto-merges.

2. **ONE TEMPLATE FILE PER BOX — NEVER A SHARED MEGA-FILE.** Each box's bytes live in its OWN `.cpp` (e.g. `bb_pat_len.cpp`, `bb_unify.cpp`, `bb_every.cpp`). A session creating a new box CREATES a new file; it never appends a second box's body into a peer's file. Per-box files = per-session non-overlapping edits. Duplicating a byte pattern INTO each template is REQUIRED (duplication is the point — RULES.md); never factor shared bytes into a common emitter helper that two languages edit.

3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.** A session may ADD or MODIFY template files for ITS OWN language's kinds and the ONE dispatch line that reaches each. It must **NEVER modify another language's template body or dispatch line.** (SNOBOL touches `bb_pat_*`; Prolog touches `bb_goal/arith/unify/cut/disj/conj/atom/struct/logicvar`; Icon touches `bb_every/alt/limit/scan/to/iterate/…`.)

4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside a template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, and the raw byte-producers `bytes()/u8()/u32le()/u64le()` (allowed only in `bomb_bytes`/`bb_emit_asm_result` of `emit_str.cpp`). A kind with no template yet must hit the dispatch's loud default (assert/abort), never silently emit nothing or fall through. `scripts/util_template_purity_audit.sh` is the standing guard.

5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** The Makefile `RT_PIC_SRCS` template list is APPEND-ONLY — add your new `.cpp` on its own line at the end of the language's group (one line = one hunk, no conflict). ADDING a template + its source line + its dispatch case is free. CHANGING a shared emitter primitive (`emit_core` dispatch signature, `BB_t`/`IR_t` layout, the `operand_aux` sidecar API, register-frame ABI) affects all three → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE EMITTER GATES ARE THE SHARED GREEN SIGNAL.** Before every commit: `scripts/util_template_purity_audit.sh` (no bytes outside templates), `scripts/test_gate_em_template_byte_identity.sh` + `scripts/test_gate_em_template_matrix.sh` (templates emit the sanctioned bytes), and the per-language no-stack/one-reg gates (`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`) must stay green. Green = your box emits right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c` (`grep -oE 'case IR_[A-Z_]+' src/emitter/emit_core.c | sort | uniq -d` empty); (b) every `IR_*` kind a language emits has exactly one dispatch case reaching one template fn, unmatched kinds hit the loud default; (c) zero forbidden byte-emitters outside templates (`util_template_purity_audit.sh` clean); (d) the FACT RULE body is byte-identical across the three GOAL files (`awk '/TEMPLATE-ONLY EMISSION — ONE-DISPATCH/{p=1} p{print} /util_template_purity_audit.sh clean/{if(p)exit}'` md5 matches); (e) the emitter gates above are green.

> **⚠ FOURTH-MUSKETEER NOTE.** Reproduced byte-identical (md5 `307534d6`); Raku is a fourth carrier.
> Raku's emitter boxes live under their own `bb_rk_*` prefix (e.g. `bb_rk_seq.cpp`, `bb_rk_jct.cpp`,
> `bb_rk_nfa_*.cpp`) so clause 3's "edit only your own boxes" holds with zero overlap onto the
> SNOBOL/Prolog/Icon prefixes. The "three → four" roster expansion is the same lockstep edit noted above.

## ⛔ NO DUPLICATED LOGIC — WRITE EACH PIECE OF LOGIC ONCE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**This is a LOGIC problem, not a formatting problem.** (Lon, 2026-06-01.) The template tree is BAD CODE: the same logic is written over and over. `bb_builtin.cpp`
is 2,427 lines because of duplication, not because the work is big. Fix the duplication; the line count
collapses on its own.

**THE ONE LAW: each piece of logic is written ONCE.** A box does PORT work (α/β/γ/ω wiring). The runtime does
VALUE work (build a term, compare, arithmetic, concat). When a box reimplements VALUE work inline, you get
duplication — and duplication is the disease in every form below.

**DUP FORM 1 — THE SAME ALGORITHM IN TWO MEDIA (worst, the bulk of the bloat).** `emit_build_compound_term`
(92 lines, emits GAS text) and `emit_build_compound_term_bin` (94 lines, emits raw bytes) are the SAME
post-order Term-builder written TWICE. A bug must be fixed in both or they drift. THE FIX IS NOT TO MERGE THE
TWO WALKERS — it is to DELETE BOTH. Building a Term is a RUNTIME job; `rt_pl_compound_build_n` and
`rt_pl_node_to_term` already do it. The box marshals operand slots into registers and `call`s the helper.
Once it is one `rt_*` call there is NOTHING to duplicate: TEXT emits `call foo@PLT`, BINARY emits
`movabs rax,&foo; call rax` — two trivial encodings of ONE logical call, which is the sanctioned per-medium
difference (NOT duplicated logic). ~18 builtin families currently each call BOTH walkers; killing the walkers
sheds >1,000 lines.

**DUP FORM 2 — EMIT-TIME LOGIC THAT IS A RUNTIME JOB.** Root cause of FORM 1. Any time a template grows a
recursive walker, an arithmetic evaluator, a comparator, a term constructor — that is VALUE work in the wrong
place. It belongs behind ONE `rt_*` call. (Guard, GOAL-BB-TEMPLATE-LADDER invariant 9: never add an
`rt_*_exec` that does α/β/γ/ω PORT logic — that is a C byrd box. The split is clean: RT = value, BOX = ports.
If you are emitting more than "marshal args, call helper, wire the 4 ports," you are duplicating runtime logic
into the emitter.)

**DUP FORM 3 — AN OPERAND BOX REIMPLEMENTED INSIDE ITS CONSUMER (fusion).** `bb_binop` reads
`pBB->α->t == IR_LIT_I` and seals the operand's VALUE (`pBB->α->ival`) in its own blob — reimplementing what
`bb_lit_scalar` already does (put a literal where a consumer can read it). Two pieces of code, one job. The
consumer must READ the operand's slot (`bb_slot_get(pBB->α)`); the operand's own box fills it. DELETE the
operand-kind arm. (PREREQ, proven 2026-06-01: deleting GZ-3/GZ-4 today breaks `write(2+3)` because the lowerer
does not yet chain literal operands as producer boxes in that shape — so the de-fuse step is first a LOWERER
fix that makes both operands producers, THEN the deletion.) Any `pBB->α->ival/sval/dval` or `->α->t==IR_LIT_*`
read inside a consumer box = fusion = duplicated operand logic.

**DUP FORM 4 — N DIFFERENT BOXES IN ONE FILE (cram).** `bb_binop.cpp` held 7 unrelated four-port shapes
selected by `op`/operand-kind/`g_*_flat_chain`. Each distinct shape is its own box; a `_str()` returning
several different complete four-port byte sequences is N boxes in one filename. This is the LEAST harmful dup
(it is co-location, not copied algorithm) but it hides the others. De-cram by splitting distinct shapes behind
a thin router (`bb_foo.cpp` keeps the `extern "C" void bb_foo(IR_t*)` so `emit_core.c` is untouched; each shape
is `bb_foo_<shape>_str(...)` returning its bytes or `""`; router calls each in order). Worked example DONE:
`bb_binop_*.cpp` + 38-line `bb_binop.cpp`.

**NOT DUPLICATION — DO NOT "FIX" THESE.** (a) The same byte pattern hand-copied INTO each per-box template is
REQUIRED (RULES.md — duplication of bytes across boxes is the point; never factor into a shared emitter helper
two languages edit). (b) Per-file op-classifier tables (`gen_is_numrel`, `gen_rel_to_tt`) copied per file —
acceptable, per-file, no shared edit. (c) Boxes 95%+ identical SHARE one file parameterized by an immediate /
opcode / register (`bb_lit_scalar` groups IR_LIT_I/S/F/NUL; `bb_binop_arith` groups ADD/SUB/MUL/DIV/MOD) —
grouping near-identical SHAPES is correct; splitting them is over-splitting. (d) The two ARMS of one box
(`IF(BINARY)`/`IF(TEXT)`) are two encodings of one logic — NOT duplication. The line is always: copied
*algorithm* = bad; copied *bytes/encoding* of one logic = fine.

**THE TEST:** could a bug in this code require fixing the same logic in two places? If yes → duplication →
collapse it (delete the emit-time copy in favor of one `rt_*` call; delete the fused operand arm in favor of
the slot read; delete the second-medium walker).

**COMPLETION TEST (per file):** (a) no algorithm (walker / evaluator / comparator / term-builder) appears in
both a TEXT arm and a BINARY arm — value work is ONE `rt_*` call; (b) no emit-time reimplementation of runtime
value work; (c) no operand-kind read (`pBB->α->ival/sval/dval`, `->α->t==IR_LIT_*`) inside a consumer box;
(d) one four-port shape per `_str()` (or a pure router); (e) the FACT RULE body is byte-identical across all
four GOAL files.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

Locked callee-saved layout the three concurrent BB sessions MUST share (canonical origin: GOAL-ICON-BB "Subject model — four names, zero redundancy"; casing inherited from the snobol4jvm Clojure SNOBOL4). **Casing carries meaning: UPPERCASE = the fixed whole/bound; lowercase = the moving position.**

| Reg | Class | Name | Role |
|-----|-------|------|------|
| **R13** | callee-saved | **Σ** (UPPER) | subject BASE ptr — the fixed whole string |
| **R14** | callee-saved | **δ** (lower) | CURSOR — the moving scan position |
| **R15** | callee-saved | **Δ** (UPPER) | subject LENGTH/END — the fixed bound |
| (scratch) | — | **σ** (lower) | TRANSIENT current-char ptr `Σ+δ`, computed at deref, NOT durable |
| **R12** | callee-saved | **ζ** (zeta) | BB-local RW FRAME base; every box-local is `[r12+off]` (RATIFIED 2026-05-30) |
| **R10** | caller-saved | (retired) | RW box-locals → `[r12+off]` (ζ frame); RO → `[rip+disp]`. r10 RETIRED (R10-OUT) |
| **rbx** | callee-saved | — | FREE / callee-saved scratch (preserved across the box chain) |
| **rbp** | callee-saved | — | DEFINE'd / brokered function frame ptr when active (`push rbp;mov rbp,rsp`); else callee-saved scratch |

**γ-success return packing:** `rax = σ ptr`, `rdx = δ int` (spec_t).

**RETIREMENT (all three sessions must honor):** the old **`Ω`** (omega — mode-2 `refs/bb/test_*.c` oracle) and **`Σlen`** (mode-3/4 `bb_pat_*.cpp` templates) are ONE quantity under two names → **both fold into `Δ`**; always moved in lockstep. Rename sweep: `Δ(old cursor)→δ`, `Ω→Δ`, `Σlen→Δ`. Substring nesting is held on the C stack (`save_Σ`/`save_Σlen`), so ONE length register suffices. **Pre-flight gate before deleting a name:** grep that no path ever sets `Σlen ≠ Ω`. Changing any assignment in this table is LOCKSTEP — update all three GOAL files in the SAME commit (mirrors the SHARED-LOWERER / EMITTER FACT RULES).

> **⚠ FOURTH-MUSKETEER NOTE.** Reproduced byte-identical (md5 `8255d653`). Raku is a Seq/generator
> language, NOT a subject-scanning pattern language at the top level: the Σ/δ/Δ subject triad is used
> ONLY inside the isolated `IR_NFA_*` regex slab (RK-NFA), where Σ=subject base, δ=match pos, Δ=slen —
> exactly the pattern-lang use. Raku's generative core (Seq pull) uses ζ (r12) for the per-box RW frame
> (resume cursors / counters) and the SysV caller-saved scratch for transport; it does not claim the
> subject triad outside regex. Any change to this table is the lockstep all-files edit per the rule.

---

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline (post-SMX-4):**
```
Raku source → raku.l / raku.y → tree_t* (TT_* AST)
    → src/lower/lower.c  lower2()  [cx.lang = IR_LANG_RKU, role VALUE]
        → IR_t four-port graph (alpha/beta/gamma/omega)
    → [mode 3] --run native runner → SM/BB/XA template BINARY arms → sealed RX → jump in
    → [mode 4] --compile --target=x86 → template TEXT arms → as → gcc -no-pie -lscrip_rt → run
```
Mode 2 (`--run`) DELETED 2026-06-15. Modes 3 and 4 are the only modes.

> **⛔ TESTING DIRECTIVE — ALWAYS RUN BOTH MODES.** Every time you test Raku, exercise mode 3 (`--run`) AND mode 4 (`--compile --target=x86` → `as` → `gcc -no-pie … -lscrip_rt` → run). Never report a mode-3 number alone. A rung is promoted only when both m3 and m4 are PASS or LOUDLY EXCISED — never a silent FAIL or abort.

**Mandatory reads, in order, every Raku session:**
1. `GOAL-ICON-BB.md` (live ground-zero goal + canonical four-port generator model Raku REUSES).
2. `RULES.md` in full.
3. This file. Find the first incomplete `- [ ]` rung in the OO LADDER.
4. `GOAL-RAKU-FRONTEND.md` and `GOAL-PST-RAKU.md` if touching the frontend.
5. If touching corpus → `CORPUS-LOCATIONS.md`. If MODE3/4-EMIT → `ARCH-x86.md` AND `ARCH-SCRIP.md`.

---

## The insight (Raku is a Seq language → ONE four-port pull protocol)

Almost everything generative in Raku produces a **`Seq`**. `gather`/`take`, the `…` sequence operator, lazy ranges, `map`, `grep` — all produce a Seq on demand. ONE four-port pull protocol (yield-one-at-β, identical to Icon's generator PUMP) suffices. A 10-kind ladder collapses to ~3 rungs on the SHARED Icon generator kinds — Raku adds almost no new IR kinds, it REUSES Icon's.

## Port semantics (identical to Icon generators — REUSE, do not reinvent)

| Port | Direction | Raku meaning |
|---|---|---|
| gamma | inherited DOWN | `take` yield / next Seq element delivered to the consumer |
| omega | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep all-false) |
| alpha | synthesized UP | fresh-pull entry (first `.pull-one`) |
| beta | synthesized UP | resume entry (next `.pull-one` after a yield) |

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
rm -f scrip && make -j4 scrip   # rc=0
make libscrip_rt                 # rc=0
```

## Gates

```bash
make scrip && make libscrip_rt
bash scripts/test_smoke_raku.sh        # m3/m4: ZERO FAIL gate (floors MODE3_MIN/MODE4_MIN)
bash scripts/test_smoke_icon.sh        # 12/12 HARD
bash scripts/test_smoke_snobol4.sh     # 7/7 HARD
bash scripts/audit_concurrency_invariants.sh
bash scripts/util_template_purity_audit.sh
```

**KEY GOTCHA:** `scrip` STATICALLY links the runtime; `out/libscrip_rt.so` is mode-4 ONLY. After ANY runtime `.c` edit, rebuild BOTH (`rm -f scrip && make -j4 scrip && make libscrip_rt`). Parser edits: `cd src/parser/raku && bison -d raku.y -o raku.tab.c`. Lexer edits: `cd src/parser/raku && flex -o raku.lex.c raku.l` (NOW WORKS — lexer unblocked 2026-06-24).

---

## Architecture reference

- Unified lowerer: `src/lower/lower.c` — `lower2()`, role-seeded; Raku arms are `cx.lang==IR_LANG_RKU` branches INSIDE the shared `tree_e` cases.
- Emitter dispatch: `src/emitter/emit_core.c`; Raku templates: `src/emitter/BB_templates/bb_rk_*.cpp`.
- Register source of truth: `src/emitter/bb_regs.h`.
- Raku frontend: `src/parser/raku/raku.l`, `raku.y`; goal files `GOAL-RAKU-FRONTEND.md`, `GOAL-PST-RAKU.md`.

---

## Watermark

**s2026-07-23 (Claude Sonnet 4.6) — RAKU-100: value-position relop Bool materialization LANDED (`IR_BINOP_RELOP_VAL` + `bb_binop_relop_val()`). Suite: Raku m3 566/0, m4 566/0 (+19 smokes, all both-modes PASS). Peers Icon 14/14, SNOBOL4 7/7. Lang-blind gate GREEN. Feature `.s` regen idempotent (0 changed). SCRIP commit `80afd4d8`. Canonical: `Numeric.rakumod`/`Int.rakumod` — every relop returns `Bool:D`. IR split: `IR_BINOP_TEST` (condition γ/ω branch) unchanged; `IR_BINOP_RELOP_VAL` (value always-γ, Bool for builtin, real value for overload). `bb_binop_relop_val()`: 3 arms — builtin-int (1/0 + γ); real/eqv (`rt_jct_relop` → 1/0 + γ); overload (`rt_binop_overload` → real return + γ). Smoke corrections: `op_overload_relop_objs` 7→1; `op_overload_relop_int_unaffected` `9\n9`→`1\n1`; `_subtype` 30 unchanged. Value-position `%%` unblocked in same shot. `lower_cond TT_SEQ` arm fixes variable-operand `if ($x<$y)` misthread (RK-BUG-SWEEP item 1). Prototype was found on disk in s2026-07-22f working tree (prior "REVERTED" note inaccurate — stale-object link). pre-existing gate baselines: xa_flat.cpp(117) medium / 6 pl_gz no-lang-names — both stash-proven. PRIOR: s2026-07-22f `%%` + relop diagnosis (Opus 4.8).**

**s2026-07-22f (Claude Opus 4.8) — RAKU-100: `%%` divisibility operator LANDED (grammar + Raku-only `TT_DIVIS` node). Suite: Raku m3 547/0, m4 547/0 (+7 smokes, condition-position, all both-modes PASS). Conflicts 88/9 → 89/9 (+1 benign `OP_DIVIS` shift). Peers Icon 14/14, SNOBOL4 7/7. Lang-blind gate GREEN. Feature `.s` regen idempotent (0 changed). SCRIP commit `ad894f1d`. Canonical: `Int.rakumod`/`Numeric.rakumod` (`$a %% $b` = `($a mod $b)==0`, Bool), `precedence.rakumod` `$iffy`. `TT_DIVIS` is opaque to `rk_chain_cmp` (a raw `TT_EQ` desugar mis-chains `6 %% 3 == 1`). DIAGNOSED (next rung, NOT fixed): value-position relops emit the wrong value (`say (6==6)`→`6`) because `IR_BINOP_TEST`/`bb_binop_relop.cpp` yields the right operand + backtracks on false (Icon semantics) instead of a Raku Bool; blanket lowerer fix reverted (breaks operator-overload dispatch); real fix is in the template's builtin-comparison branch (write 1/0, take γ unconditionally; overload branch unchanged) — both-medium, monitor-first. Unblocks value-position `%%` + `say (comparison)` + RK-BUG-SWEEP item 1. PRIOR: s2026-07-22e ++/-- + sprintf/printf/.fmt/.starts-with/.ends-with/.subst (Sonnet 4.6).**

**s2026-07-22e (Claude Sonnet 4.6) — RAKU-100: prefix/postfix `++`/`--` expression-position + `sprintf`/`printf` + `.fmt` + `.starts-with`/`.ends-with` + `.subst` LANDED. Five rungs (one grammar, four runtime). Suite: Raku m3 540/0, m4 540/0 (+27 smokes, all both-modes PASS). Conflicts 88/9 (+2 s/r benign from incdec atom, r/r flat). Peers Icon 14/14, SNOBOL4 7/7. Lang-blind gate GREEN. `.s` regen idempotent (runtime-sink only). SCRIP commits: `ceac791` `ca2527d` `91c937b` `4741094` `0214690`. FINDING: float trailing-dot (`say sqrt(16)` prints `4.` not `4`) traced to peer-shared `real_str` in `string_ops.c` (deliberate SPITBOL semantics, cannot change globally); fix needs Raku-specific sink — scoped to next session. PRIOR: s2026-07-22d repeat/array-methods (Opus 4.8).**

**2026-07-14 (Claude Sonnet 4.6 · SCRIP this commit · corpus untouched · .github edited). RK-GRAM-3c COMPLETE — multi-leaf grammar sequence via native chained leaf boxes.** Pure lowerer change (`src/lower/lower_raku.c`): added `rk_gram_seq_leaves()` (parses rule body into leaf list: literals + builtin char-classes incl. `<.name>`; non-leaf body → 0 → NFA fallback); chained-graph build tail-first (each leaf `γ` → next, tail `γ` → NULL → success exit); removed dead `rk_gram_pure_literal`/`rk_gram_pure_charclass`. No new box template, no emitter change — existing graph-walk driver already resolves `nd->γ.node` to successor α label. Native proof: emitted `.s` two chained `IR_GCC` boxes, zero `nfa_build` on `.parse` path. +8 sequence smokes (`scripts/test_smoke_raku.sh`). RESULTS: Raku 234/20 both modes (was 226/20; +8 new sequence smokes all PASS, same 20 pre-existing OO/multi-dispatch failures); Icon 14/14; SNOBOL4 7/7; language-blindness gate OK. TOUCHED: `src/lower/lower_raku.c`; `scripts/test_smoke_raku.sh` (+8 smokes).

**2026-07-14 (Claude Opus 4.8 · SCRIP `ff64b7ee` pushed · corpus untouched · .github edited). RK-GRAM-3b COMPLETE — `.parse` scan-entry trampoline LANDED + default-native flip.** Both leaf boxes (bb_rk_glit + bb_rk_gcc) now EXECUTE on the `.parse` path as the **default** (no env flag required). NEW `src/runtime/rt_gram_trampoline.S`: naked `rk_gram_enter_box` (5-push, 16-aligned, r8-preserved) loads Σ/δ/Δ into r13/r14/r15, enters the box at α, reads δ back into `*out_delta`. `rk_gram_run_native` in `by_name_dispatch.c` wraps it with a fixed 256B zeroed 16-aligned scratch frame (frame_bytes=0 for grammar procs makes `rt_proc_call_open` path unsafe; leaf self-inits +32/+40 and is zls-balanced). Branch prepended to `grammar_parse_core` (by_name_dispatch.c:381): `rt_proc_get_fn("gram__G__TOP") != NULL` → take native path, else fall through to `nfa_build` (NFA kept for `~~ /regex/` and un-migrated shapes). Default-ON flip: `lower_raku.c` gate changed from `getenv("RK_GRAM_NATIVE") ? 1 : 0` to `(e && e[0]=='0') ? 0 : 1` — escape hatch `RK_GRAM_NATIVE=0` restores NFA. gdb-proven both modes: m3 `rk_gram_run_native` fires / `nfa_build` absent; m4 standalone binary `bf=proc_gram__G__TOP_α`. TWO LATENT BUGS in the finding's published asm FIXED: (1) 4-push alignment left rsp%16==8 → SSE segfault in strchr; (2) r8/out_delta clobbered by box's strchr across the call. Fix: 5 pushes (r13,r14,r15,rbx,r8) → rsp 16-aligned at call AND r8 preserved, recovered via `pop rcx` after. Hardening smokes: all 7 builtin char-classes (digit/alpha/upper/lower/xdigit/alnum/space, member + non-member) + literal edges. RESULTS: Raku 226/20 both modes, failing set BYTE-IDENTICAL to baseline 20 (same pre-existing ALIGN-INV OO/multi-dispatch 20); Icon 12/12; SNOBOL4 7/7; `make scrip` + `make libscrip_rt` rc=0. TOUCHED: NEW `src/runtime/rt_gram_trampoline.S`; `src/runtime/by_name_dispatch.c` (+11); `src/lower/lower_raku.c` (1 line flip); `Makefile` (+2); `scripts/test_smoke_raku.sh` (+72, 16 native smokes).
**NEXT (leverage order):** (1) **RK-GRAM-3c** — sequence + the δ-save ζ slot (fresh full-budget session; ARCH reads first). (2) 3d alternation — needs its own `IR_GALT` (IR_ALT NOT in live IR.h; SNOBOL4 alt kinds scan-specific, do not reuse). (3) The 20 ALIGN-INV Raku OO regressions (staged-proc-call arg marshaling + concat-return path) remain open, NOT grammar work.

**✅ 2026-07-13 TIP BUILD-BLOCKER — RESOLVED (SCRIP local commit `3208f223`, Claude Sonnet 4.6).** `bb_scan_alternate.cpp` migrated exactly per rbp-dcap's own theorem: dropped both C-call windows (`rt_dcap_height` α, `rt_dcap_restore_to` β) + the dead `+20` height-save slot, kept `+16` cursor save (still consumed by `rt_substr`) and `+24` alt index — mirroring the `bb_match_alternate.cpp` cleanup. Confirmed behavior-neutral: Icon smoke went unbuildable→12/12 both modes; SNOBOL4 7/7, Raku 210/20 both modes unchanged. Tree clean-builds again (`make scrip` + `make libscrip_rt`, gcc/g++/as + libgc/flex/bison). [Original P0 report, now fixed: bb_scan_alternate (from `eb9ac70e` SCAN-NARY-BOX) called `rt_dcap_height`/`rt_dcap_restore_to`, which `32bd6106` rbp-dcap DELETED — rbp-dcap cleaned the sibling but missed this file; link failed undefined-ref at :24/:51.]**

**2026-07-13 (Claude Sonnet 4.6 · SCRIP local commits `3208f223` build-unblock + `55e48359` 3b-emitter-half, on top of `e12b87ed`; corpus untouched · .github edited · not yet pushed — `handoff_status.sh` is the push-truth, run it live at handoff, do NOT trust this line). RK-GRAM-3b EMITTER HALF: `bb_rk_glit.cpp` — native literal-match leaf box, both media, LIVE in the emitter (no longer FATALs on IR_GLIT). Box: match RO-sealed literal (`op_name1`) at `[Σ+δ]`=`[r13+r14]`; require `Δ-δ >= len` (`r15-r14`) else ω; `memcmp` len bytes else ω; on match `r14 += len` (advance δ) then γ. Pure leaf — no ζ RW state, no value slot (grammar match advances the cursor; γ/ω ARE the result). RO string sealed `[rip+disp]` via the `def L(0)`/`.quad LS(0)`/`label`/`.string` trailer (the `bb_scan_match` literal-arm idiom). Language-blind (dispatches on IR shape, zero `is_raku`); ALL template-purity FACT RULES pass (0 `MEDIUM_*`, 0 raw-byte producers, pure `x86()`). WIRED IR_GLIT through BOTH emit dispatch levels — `emit_drive` prep switch (stages `op_name1`→`DRIVE_FILL`, mirrors the `IR_FAIL` leaf) AND the `walk_bb_node` template switch (`bb_rk_glit()`); the first FATAL was `emit_drive`'s prep switch defaulting to `drive_unowned` for IR_GLIT. ⚠ CORRECTION to 3a's note: `IR_GLIT` is op **115**, NOT 113 (3a's "op=113" was stale — verified by compiling a probe against IR.h). Added `bb_rk_glit.cpp` to BOTH Makefile paths (scrip per-file rule + `RT_PIC_SRCS`). Lowerer live-emission behind default-OFF `RK_GRAM_NATIVE` env seam (mirrors how 3a kept its fallback): default `--run`/`--compile` UNTOUCHED. Under the flag, `rule TOP { "abc" }` compiles to the correct box (`cmp rax,3` / memcmp / `add r14,3` / `.string "abc"`) and assembles+links clean via gcc — mode-4 TEXT arm PROVEN; startup wires the proc via `rt_proc_set_fn` (the hook the .parse trampoline will use). NEUTRALITY PROVEN (flag off): Icon 12/12, SNOBOL4 7/7, Raku 210/20 both modes; Raku failure SET byte-identical to baseline (`diff` empty). Box hardened across literals ("abc" len3, "a b c" len5 incl spaces — correct len + sealed bytes, both assemble). TOUCHED: NEW `src/templates/bb_rk_glit.cpp`; `src/templates/bb_templates.h` (+proto), `src/emitter/emit.cpp` (+2 dispatch cases), `src/lower/lower_raku.c` (+env seam, 2 lines), `Makefile` (+2 build entries).
**NEXT (3b gate remainder — fresh full-budget session per this file's RK-GRAM rule; read ARCH-x86.md + ARCH-SCRIP.md + ARCH-ICON.md §String-scanning + `src/templates/x86_asm.h` first):** (1) **`.parse`→box trampoline** — `grammar_parse_core` (by_name_dispatch.c:381) still calls `nfa_build`; make it, for a rule that has a native `gram__G__TOP` proc, resolve the entry (via `rt_proc_set_fn`/`rt_call_proc_descr` already emitted at startup), load Σ/δ/Δ (r13/r14/r15) from the subject, jmp into the box, and marshal γ (δ==Δ full / any-γ subparse) / ω back into a Match/DESCR. THAT flip makes `RK_GRAM_NATIVE` the default, retires the env seam, and delivers the gate's "zero `nfa_build` on the `.parse` path" for the literal shape. (2) **`bb_rk_gcc.cpp`** char-class leaf (gate part 2: `rule TOP { <digit> }`) + extend `rk_lower_grammar_boxes`/`rk_gram_pure_literal` to recognize the `<cc>` shape → `IR_GCC`. Then 3c (sequence + δ-save slot), 3d (alternation via IR_ALT), 3e (subrule recursion = THE seam), 3f (quantifiers), 3g (retire flatten fallback).**

**2026-07-13 (Claude Sonnet 4.6 · SCRIP `5ed96a85`, rebased on Prolog `d41ecf39`, UNPUSHED · corpus untouched · .github edited). RK-GRAM-3a LOWERING SEAM (second half of 3a, after enum-first `93623c09`): grammar literal-shape rules (`rule TOP { "a" }` — body is a single quoted string, no `|`/subrule/quantifier) now LOWER to an `IR_GLIT` box-graph node, dump-visible. New `rk_lower_grammar_boxes(prog)` in lower_raku.c (placed AFTER the mid-file `stage2.h`/`bb_program.h` includes to dodge decl-ordering; called in `lower_raku_stage2` right after `rk_discover_grammars`) + `rk_gram_pure_literal(body,out,sz)` shape detector: for each pure-literal rule it builds a 1-node graph `[IR_GLIT sval=<text>]` via `IR_alloc`/`lc_build`+`IR_LIT(nd).sval=lp_strdup(...)`, `bb_program_add`s it, and registers it as proc `gram__<G>__<rule>` (nparams 0, bb_idx set) in proc_table so `--dump-ir` (which walks proc_table, not raw bbp) shows it. INERT BY GATING ON `g_opt_dump_bb` (set = `dump_ir` at scrip.c:618, before all lowering): registration fires ONLY in dump runs; `--run`/`--compile` never register the proc → byte-identical emission, and this sidesteps `graph_native_emittable`/`emit_drive` entirely. The `rt_grammar_register`→`gram_set` string fallback is UNTOUCHED (unconditional), so `.parse` still matches via `gram_expand`→`nfa_build`. GATE MET: `--dump-ir` on the literal shape (idiom `grammar G { rule TOP { \"hello\" } }`) prints `; proc gram__G__TOP` + a `GLIT` node. NEUTRALITY PROVEN: Raku smoke 210 PASS / 20 FAIL both modes, FAILURE SET BYTE-IDENTICAL to baseline (`diff` empty — the 20 pre-existing ALIGN-INV OO/multi-dispatch fails, zero added); grammar proc ABSENT from emitted `.s`; Icon 12/12, SNOBOL4 7/7 both modes; clean build scrip+libscrip_rt. DELIBERATELY DEFERRED to 3b: the gate's "no `nfa_build` on the RUNTIME `.parse` path" clause is BLOCKED-BY-DESIGN until the leaf-box template exists — mode-3/4 `emit_drive` FATALs on any untemplated op ("the driver never declines silently"; op=113=IR_GLIT), so a LIVE literal box cannot execute before `bb_rk_glit.cpp`. 3a delivers the inert seam + dump-visibility; the runtime NFA retirement rides with 3b. TOUCHED: `src/lower/lower_raku.c` (+43 lines).**

**2026-07-13 (Claude Sonnet 4.6 · SCRIP `93623c09` · corpus untouched · .github edited). RK-GRAM-3a ENUM-FIRST: IR_GLIT / IR_GCC / IR_GSUBRULE vocabulary added to src/contracts/IR.h + kind-name strings in scrip_ir.c (--dump-ir ready). INERT — no behavior change; fallback string path unconditional. Proven behavior-neutral: Raku smoke 210/20 both modes, identical failure set pre/post; Icon 12/12 both modes; SNOBOL4 7/7; clean build scrip+libscrip_rt.**

**BASELINE NOTE: Raku smoke shows 210 PASS / 20 FAIL (not the 230/0 watermark claims). The 20 failures are OO/multi-dispatch (class_method, attr_mutate, MRO/TWEAK ordering, handles_*, multi_* dispatch family, op_overload_mixed_obj_int, for_range_pointy_toplevel) — all pre-landing behavior broken by the ALIGN-INV-0/1/2/2b RBP-COMPLETE arc (same-day commits d9424bf9→d592a80c, 2026-07-13), which reworked call-frame alignment and touched bb_call_proc_staged.cpp + x86_asm.h. Concrete symptom: $p.scale(2) → 7 (not 14, arg never reaches $factor); string-returning method body produces no output. The ALIGN-INV session gated "all four frontends" but Raku is the fifth — fallout sailed through. Rbp no longer in use per Lon directive; the fix is in staged-proc-call arg marshaling and concat-return path, not a revert.**

**TOUCHED:** `src/contracts/IR.h`, `src/contracts/scrip_ir.c`.

**NEXT (leverage order):** (1) **RK-GRAM-3a lowering seam** — fresh full-budget session; read ARCH-x86.md + ARCH-SCRIP.md + ARCH-ICON.md §String-scanning first (bb_regs.h stale doc — use x86_asm.h). Seam: intercept lower_raku.c:427 rt_grammar_register call; add gated body→IR-graph mini-parser for the literal-shape gate (`rule TOP { "a" }` → IR_GLIT, dump shows it, no nfa_build on .parse path); fallback string registration kept unconditional so un-migrated shapes regress nothing. (2) Fix the 20 ALIGN-INV Raku regressions (bb_call_proc_staged.cpp arg marshaling + concat-return path, rbp-free). (3) Then resume prior NEXT order: dynamic gather, TT_SMATCH, TT_CASE/given-when.

**SESSION FINDINGS (carried for next session):** IR_ALT does NOT exist in live IR.h (only in parked files); SNOBOL4-specific IR_MATCH_ALTERNATE / IR_PATTERN_ALT exist but are scan-semantics-specific — 3d alternation needs its own IR_GALT or inline wiring. bb_regs.h does not exist (stale doc reference in rung + Architecture reference section — register truth is src/templates/x86_asm.h per ARCH-ICON.md). Rakudo Match: truthiness = pos>=from (zero-width match at pos==from SUCCEEDS — matters for * quantifier in 3f); .parse loops cursor_next until pos==chars (may need beta-resumption of TOP, not single alpha-pump); Cursor = Match alias (Cursor.rakumod is one line).

## Prior watermark

**2026-07-10 session B (Claude Fable 5). try/CATCH LANDED — prior NEXT #1 flipped. m3/m4 230 PASS / 0 FAIL / 0 EXCISED / 230 (+12 try smokes on the 218 baseline; zero prior-case drift). Peers: Icon 12/12 both modes, SNOBOL4 7/7. Gates: emit_no_lang OK, no_bb_bin_t OK; concurrency + template-purity audit outputs byte-identical at clean HEAD (stash A/B) — pre-existing, unchanged. Artifact regen ×3 run (by_name_dispatch.c is a runtime sink): zero byte changes, codegen untouched.**

**THE MECHANISM — ω IS THE UNWIND.** Under try, `die` returns FAILDESCR (rt_script_die_surface was already gated on `g_script_try_depth > 0`), and FAILDESCR rides the existing four-port ω spine outward through every enclosing expression, statement, and user-sub call — no setjmp, no new templates, zero emitter edits. The one construct that swallows ω is a generator pump (loop bodies resume the source on ω), so lowering under a try threads `cx->try_catch` through `lower_rblock`, which interposes per-statement `exc_check` polls: `IR_CALL exc_check` with γ=exception→handler, ω=clean→continue — exc_check's INTVAL(1)/FAILDESCR return drives the branch through the untouched CALL template exactly like `__rk_bool`. Because the flag threads through every block lowered under the try, polls reach loop/if/while bodies by construction: `die` in a loop catches at the FIRST iteration, never after pump-exhaustion.

**FAITHFUL TO (Rakudo sources read this session):** `src/Raku/ast/statementprefixes.rakumod` StatementPrefix::Try (no-CATCH try wraps in handle; caught → Nil), `scoping.rakumod` attach-catch-handler + IMPL-ADD-HANDLER (handler runs, rest of the enclosing block skipped) + IMPL-WRAP-SCOPE-HANDLER-QAST (a die inside a handler rethrows OUTWARD — verified: inner-handler die propagates to the outer try; halts loudly at depth 0), `statements.rakumod` Statement::Catch, `control.rakumod` (control-exception model).

**LANDED:** grammar `KW_CATCH block` statement arm → new `TT_CATCH` (contracts/ast.h, additive; bison regen, 31→32 S/R — the `try{}CATCH{}` juxtaposition shift; adjacent form correctly wins); lower_raku.c TT_TRY arm (excise flipped): try_enter → polled body → success try_exit; catch entry = try_exit → `$_`←exc_get → exc_clear → handler; canonical inside-the-body `CATCH {}` hoisted by scanning the try body's statements, adjacent `try{}CATCH{}` kept; lower_rblock poll interposition + TT_CATCH statement skip; runtime `try_enter`/`try_exit` by-name builtins (`g_script_try_depth` ±1, enter clears) beside the pre-wired exc_clear/exc_check/exc_get family. Smokes ×12: skip-rest, `$_` topic, success path, canonical-inside, sub unwind (callee's post-die statements skipped via the sub's own ω), for/while/if first-divergence halt, nested inner/outer, handler-rethrow-to-outer, sequential state hygiene, depth-0 handler die halts (rc=1, stderr).

**SUBSET DEVIATIONS (named costs):** (a) CATCH attaches only to a try (adjacent or immediate body child); Raku's any-block CATCH is a skipped no-op outside try; (b) bare CATCH body ≡ `default {}` — the when-chain match + rethrow-on-unmatched needs given/when (see NEXT); (c) `$!` not surfaced (`$_` carries the message; exc_get available); value-position try yields "" not the body value (value-join diamond precedent: bool_compare_store); (d) die inside a loop inside a *separately-lowered sub* called from try can be pump-swallowed until that loop exits (sub bodies are lowered at declaration, unpolled) — a top-level die in a sub unwinds precisely.

**TOUCHED:** `src/lower/lower_raku.c`, `src/runtime/by_name_dispatch.c`, `src/parser/raku/raku.y` (+tab.c/h regen), `src/contracts/ast.h`, `scripts/test_smoke_raku.sh`.

**NEXT (leverage order):** (1) dynamic gather — `take` under loops/conditionals via `IR_PROC_GEN` + ZLS2 activation slots (fc71ef93 handles; Raku Seq = Icon generator per this file's insight section); (2) `TT_SMATCH` subst arm + `match_global`/capture smoke coverage (arms exist, cases don't); (3) `TT_CASE` (given/when) — also unblocks CATCH when-chains, retiring deviation (b); (4) RK-GRAM-3 recursive-descent grammar engine — still the standing fresh-full-budget-session item, `ARCH-x86.md`/`ARCH-SCRIP.md`/`ARCH-ICON.md` §String-scanning first.

## Prior watermark

**2026-07-10 session (Claude Fable 5). RAKU SMOKE 100%. m3/m4 218 PASS / 0 FAIL / 0 EXCISED / 218 (was 204/0/12 of 216; +2 new smokes). Every gutting-era EXCISE in the suite is retired. Peers: Icon 12/12 both modes, SNOBOL4 7/7 both modes, Prolog 5/5 all three tallies. Gates: emit_no_lang OK, no_bb_bin_t OK; audit_concurrency_invariants (goal-doc anchors) + template_purity (bb_call_write_slot) violations are byte-identical at clean HEAD — pre-existing, stash-A/B-proven, not this change.**

**ROOT CAUSE — THE MISSING β DISCIPLINE (and a latent infinite loop it hid).** The restored lowerer's `γ_to`/`ω_to`/`build` were bare `lc_*` pass-throughs: every edge into a generator-kind box entered **α** (fresh init), never **β** (resume). WITNESS 1 (uncovered by any smoke): `for 1..3 -> $v { say($v) }` printed `1` forever in BOTH modes at clean HEAD — the body's loop-back γ re-entered the TO's α, re-initializing the counter each trip. WITNESS 2: the new map-over-range lowering printed its first value forever in m4 only (m3's in-process driver masked it). Fix = port Icon's three-layer discipline verbatim: (a) `γ_to`/`ω_to` wrappers stamp `lc_γ_to_β`/`lc_ω_to_β` when the target is `ir_is_generator_kind` (lower_icon.c:15-16); (b) `build()` stamps the same for its γ/ω arguments (lower_icon.c:18-22); (c) inside each TO arm the range-bound producer's γ is α-FORCED back with raw `lc_γ_to` (lower_icon.c:860 — operands initialize at α, only downstream pumps resume β); (d) STMT-BOUNDARY α-FORCE: `lower_rblock` interposes a raw-α `IR_GOTO` trampoline when a statement's entry is generator-kind so a preceding statement's cross-edge is a fresh evaluation, never a resume (lower_icon.c:886-895). `IR_BINOP_TEST` is not generator-kind, so the proven while/if/call graphs are untouched by construction — zero regressions across all 216 prior cases.**

**LANDED — the final 12 EXCISED flipped (all in `src/lower/lower_raku.c`, lower-only):**
1. **Value-position relops** (`say(3 < 9)`, op-overload dispatch): `IR_BINOP_TEST` built in value position with operands on the γ-spine and `*res = op` — Icon's right-operand yield and `rt_relop_overload` dispatch fall out of the existing template. Flips `op_overload_relop_objs`/`_subtype`/`_int_unaffected`.
2. **Assign-RHS relop Bool materialization** (`my $b = $x > $y`): the value-join story from this file's own NEXT item — a diamond of two `IR_ASSIGN(varname)` nodes fed `lit1`/`lit0`, entry = `lower_cond(rhs, n1, n0)`, both γ to the statement continuation (the Pascal `pas_mat`/`__pbt` precedent, assigning the real var directly). Flips `bool_compare_store`.
3. **Smartmatch + captures:** `TT_SMATCH` (non-subst) → 2-operand `IR_CALL` `re_match` / `re_match_global` (tag-selected), subject+pattern on the spine; `TT_CAPTURE` → `re_capture`, `TT_NAMED_CAPTURE` → `re_named_capture` — the runtime regex block in `by_name_dispatch.c` survived the gutting intact and needed only the call wiring. Flips the 3 smatch smokes.
4. **`for … -> $v` over gather/map/grep (TT_EVERY):** `rk_take_list` statically unrolls a gather body's `take` exprs (reverse chain, each value threaded through `rk_xf_body`); `rk_xf_body` builds the per-value chain — plain: `v←val→body→pump`; map: `"_"←val → xf → v←xfres → body→pump`; grep: `"_"←val → lower_cond(xf, T: v←"_"→body→pump, F: pump)` (filter-reject resumes the source). Range sources reuse the FOR_RANGE `IR_TO` shape. Flips `gather_take`/`map_range`/`grep_range`/`map_over_gather`/`grep_over_gather`. NOTE: gather is static-unroll — `take` under loops/conditionals inside gather still needs real `IR_PROC_GEN` + fc71ef93 ZLS2 activation handles (recorded in NEXT).
5. **+2 smokes** `for_range_pointy` / `for_range_pointy_toplevel` locking the β fix (the shapes that looped forever were smoke-invisible).

**VERIFICATION NOTE:** the 216-case suite was run as 5 sequential foreground chunks (identical `raku()` harness per case; header+footer replicated; tallies 44+44+44+44+40, F=0 X=0 in every chunk, both modes) because sandbox suspension between operator turns kills >5-minute background jobs; the 2 new cases ran the same way. `for`-probe outputs additionally hand-verified m3+m4 (`1/2/3/done`, `2/4/6/done`, etc.).

**TOUCHED:** `src/lower/lower_raku.c` (+78/−11 — wrappers/build β-stamps, α-forces, spine trampoline, relop/smatch/every arms, `rk_take_list`/`rk_xf_body`), `scripts/test_smoke_raku.sh` (+2 cases). NO emitter/template/runtime edits → `.s` artifact regen definitionally no-op for this change (RULES step 4 codegen-touched condition not met).

**NEXT (leverage order):** (1) `try`/CATCH on the new spine; (2) dynamic gather — `take` under loops/conditionals via `IR_PROC_GEN` + ZLS2 activation slots (fc71ef93 handles; Raku Seq = Icon generator per this file's insight section); (3) `TT_SMATCH` subst arm + `match_global`/capture smoke coverage (arms exist, cases don't); (4) `TT_CASE` (given/when); (5) RK-GRAM-3 recursive-descent grammar engine — still the standing fresh-full-budget-session item, `ARCH-x86.md`/`ARCH-SCRIP.md`/`ARCH-ICON.md` §String-scanning first.

---

## Prior watermark

**2026-07-09 session (Claude Fable 5). RAKU RESTORED ONTO THE POST-GZ#5 SPINE. Raku m3/m4 204 PASS / 0 FAIL / 12 EXCISED / 216 (was: segfault on `say "hello"`; the fc71ef93 baseline cited raku 10/177/29). Peers: Icon smoke 12/12 both modes, SNOBOL4 7/7, Prolog 3/2 both modes (pre-existing — change surface is Raku-only: the classify arm fires only on `__rk_bool`, minted solely by lower_raku).**

**ROOT CAUSE OF THE GUTTING-ERA SEGFAULT — UNION CLOBBER.** GZ#5 (`4f1017d9`) collapsed `IR_t`'s payload to ONE union `{sval,ival,dval}`; the old Raku call encoding wrote all three on one node (`sval=name, ival=argc, dval=route-flag`), so `dval=1.0` overwrote the name pointer (0x3ff0000000000000 read as `fn` → crash in `bb_call_route_classify`). Every dval-flavored route (1.0/2.0/3.0 visible/argblk/proc) is structurally dead under the union — `lc_call_argblks` survives only as a husk that would clobber sval.

**LANDED — lower_raku.c core rewritten on the Icon model (dead `lower()`/`lower_nary`/`lower_decl` statement-path family deleted; `lower_rv` is the one spine):**
1. **Calls = Icon shape:** `IR_CALL` carries ONLY `sval=name`; argc = `n_operands`; args lowered left→right on the γ-spine (`lc_γ_to(prev_result, next_entry)`), results pushed via `ir_operand_push` (LOWER-wired per the 486eb1a3 technique-lock). Routing = **reclassification post-pass** `rk_reclassify_calls()` mirroring `lower_icon.c:1123`: registered proc → `IR_CALL_PROC_STAGED`, rt-known → `IR_CALL_BUILTIN`, unknown stays `IR_CALL` → BYNAME; `__rk_bool` exempt (name-routed).
2. **Control flow = port rewiring, not new BBs** (per Lon's directive to copy Icon/SNOBOL4): `if`/`unless` are pure γ/ω edge wiring through `lower_cond`; `while`/`until`/`repeat` are ONE `IR_GOTO` re-entry trampoline + edge threading (Icon `lower_while` shape); relop conditions lower to `IR_BINOP_TEST` (native γ/ω branch, no boolean reification); non-relop truthiness → `__rk_bool` IR_CALL routed `CALL_ROUTE_RK_BOOL_SLOT` by a NEW name-based classifier arm in `emit.cpp` (the old dv==0.0/2.0 arms can never fire under the union). `for lo..hi` = `IR_TO`("ag") + `IR_ASSIGN` + body-γ→TO re-pump, results (not entries) pushed as TO operands per Icon `lower_to`.
3. **`say`→`write`, `print`→`writes`** (the by-name write machinery, `op_write_route` intact); blocks are `TT_SEQ_EXPR` (added beside TT_SEQ/TT_PROGRAM in `lower_rblock`); `TT_TWIGIL_FIELD` restored onto the surviving `IR_FIELD_GET`; field get/set = `field_get_pub`/`field_set`/`field_set_pub` calls with `[obj, name-lit, value]` operands; multi/junction/push/hash rewrites kept.
4. **ZLS param seeding (THE param-binding fix):** proc graphs now get `g->nparams`/`g->pnames` (mirror of `lower_icon.c:1061`) so `zls_build` grants param vslots at `16+i*16` — without it every callee param read NULL.
5. **`my $u;` undef:** `TT_NUL` → by-name `__rk_undef` returning `NULVCL` (DT_SNUL) — new 1-line arm atop `script_try_call_builtin_by_name`; fixes `.defined`, `:D`/`:U` param checks (definedness = `v != DT_SNUL`).
6. **`rhs_kind_ok` (scrip.c, Raku-only emittable gate) modernized:** accepts `ir_norm_call_kind(op)==IR_CALL` + `IR_UNOP`/`IR_FIELD_GET`/`IR_PROC_GEN` (the old acceptance rode union-dead dval checks) — this one line flipped ~120 smokes from EXCISED to PASS (assign-from-call is the OO corpus's backbone).

**EXCISED vehicle:** unsupported constructs (`try`/`gather`/`map`/`grep`/`smatch`/`case`/`every`/captures/value-position relops) lower to a bare `IR_OP_COUNT` node → `graph_native_emittable` prints `[SMX]` → counted DECLINED. The 12 remaining EXCISED are exactly these.

**TOUCHED:** `src/lower/lower_raku.c` (core rewrite), `src/emitter/emit.cpp` (one additive `__rk_bool` classify arm), `src/driver/scrip.c` (`rhs_kind_ok` call-kind arm), `src/runtime/by_name_dispatch.c` (`__rk_undef` arm). Artifact regen run per RULES step 4: SNOBOL4 benchmark/feature/demo `.s` diffs are comment-only `[r12+…]`→`[zr+…]` churn from the prior ζ-parameterization session (first regen since); Icon bench `.s` updated 10 — the `rt_proc_call_gen→rt_proc_call_gen_h`/`rt_proc_resume_frame` symbol rename from 72b0e09d/fc71ef93, honestly captured (not this session's codegen; Icon smoke 12/12 both modes on these symbols).

**NEXT (leverage order):** (1) ~~value-position relops~~ **DONE s2026-07-23** (`IR_BINOP_RELOP_VAL` + `bb_binop_relop_val()`); (2) `try`/CATCH on the new spine; (3) gather/take onto IR_SUSPEND/PROC_GEN + the fc71ef93 ZLS2 activation handles (natural fit — Raku Seq = Icon generator per this file's insight section); (4) map/grep (RK-EMIT-MAP/GREP, was blocked on Icon GZ-7 — GZ-7 landed 2026-07-06, re-check); (5) smart-match + RK-GRAM-3 (still the standing fresh-session lead).

---

## Prior watermark

**2026-06-27 session (Claude Opus 4.8). Raku m3/m4 209 PASS / 0 FAIL / 7 EXCISED / 216 (was 196). Peers: Icon 12/12, SNOBOL4 7/7. Three committable increments, both modes, zero regressions.**

**RK-OO-F plain-type param enforcement — LANDED both modes (+4 smokes).** The previously-deferred F-tail: a non-`:D`/`:U` typed param (`Int $x`, `Str $s`, a user class) now runtime-checks its bound arg at proc entry and DIES faithfully ("Type check failed in binding to parameter ...") on a wrong type; subtype args (a `Dog` for an `Animal` param) are ACCEPTED via the MRO check. Runtime side (`rt_mc_accepts`) already handled plain types; the only gate was one line in `lower_raku.c`. New `rk_is_modeled_type` guard restricts enforcement to types the runtime models (numeric/string leaves + registered classes) so unmodeled barewords cannot false-die. Reuses `__param_check` (no new IR/template). Smokes: `param_plain_int_passes`/`param_plain_int_dies`/`param_plain_str_passes`/`param_plain_class_subtype`.

**RK-GRAM literal strings in rules — LANDED both modes (+4 smokes).** `rule TOP { "hello" }` now matches its CONTENTS verbatim (quotes stripped) with regex-metacharacters treated as LITERAL (Raku: `"a.b"` matches a literal dot, not any-char). `gram_expand` previously copied the quote chars into the NFA pattern so `"hello"` tried to match the quotes too. Shared by both modes (runtime `gram_expand`); literal+subrule mixes work. Smokes: `grammar_literal`/`grammar_literal_nomatch`/`grammar_literal_subrule_mix`/`grammar_literal_metachar`.

**RK-GRAM built-in character-class subrules — LANDED both modes (+5 smokes).** `<digit>`/`<alpha>`/`<alnum>`/`<upper>`/`<lower>`/`<space>`/`<ws>`/`<xdigit>` resolve to their regex class when a `<name>` isn't a user-defined subrule (user subrules still win — checked first). New `rk_grammar_builtin_class` in `by_name_dispatch.c`; quantifiers and inter-token whitespace compose. Smokes: `grammar_builtin_digit`/`grammar_builtin_alpha`/`grammar_builtin_upper_lower`/`grammar_builtin_space`/`grammar_builtin_nomatch`.

**FRONTIER (RK-GRAM-3, unchanged — still the lead, still a fresh-session item):** recursive rules (`rule TOP { "a" <TOP> | "a" }`) still fail — the depth-16 flatten-to-NFA cannot recurse. This is the native recursive-descent box engine: SNOBOL4 box topology (seq/alt/subrule-recursion: γ=advance, ω=fail/redo) + Icon's Σ/δ/Δ scanning discipline for leaves, with the cursor δ pinned in callee-saved R14 so it stays ambient across subrule recursion. Per the goal mandate, start it in a fresh full-budget session with `ARCH-x86.md`/`ARCH-SCRIP.md` read first.

**TOUCHED (this session):** `src/lower/lower_raku.c` (new `rk_is_modeled_type` + loosened param-check gate), `src/runtime/by_name_dispatch.c` (new `rk_grammar_builtin_class` + `gram_expand` literal-unquote/escape), `scripts/test_smoke_raku.sh` (+13 smokes). The `.s` artifact regen is IDEMPOTENT: all changes are new standalone functions or Raku-grammar/param-only edits, off every SNOBOL4/Icon emit path — peer `.s` output is byte-identical (Icon 12/12, SNOBOL4 7/7 verified green).

---

## Prior watermark

**2026-06-27 session (Claude Sonnet 4.6). Raku m3/m4 176 PASS / 0 FAIL / 7 EXCISED / 183. Peers: Icon 12/12 (full rung suite 208/208 both modes), SNOBOL4 7/7, Prolog m3/m4 5/5.**

**RK-OO-A2 privacy (`$!` encapsulation) — LANDED both modes (+10 smokes, incl. A3 `@!`/`%!`).** A `$!`-declared attribute gets no public accessor (faithful to Rakudo `Attribute.compose` `has_accessor`), so external `$obj.x` and `$obj.x()` both die while internal `$.x`/`$!x` always read/write. Lexer keeps the twigil char (`$.x`→`.x`, `$!x`→`!x`); declaration nodes carry the prefixed name, decoded to `(priv, bare-name)` at the single `lower_raku.c` registration site (a union pitfall — `tree_t.v` is a union, a flag-in-`ival` clobbers the name pointer — was caught and avoided by string-encoding). Per-field `priv[64]` on `DatType` threaded through both field-merge sites; MRO-walking `dat_field_is_private`; `dat_set_field_priv@PLT` m4 replay. Enforced at `meth_call` accessor fallback, `field_set_pub`, and a NEW `field_get_pub` (external `TT_FIELD` reads now lower to this gated by-name call so the no-paren form is gated; internal `TT_TWIGIL_FIELD` stays on the ungated `IR_FIELD_GET`). A3's previously-deferred `@!`/`%!` aggregate privacy fell out for free. Smokes: `priv_attr_external_dies`/`_internal_ok`/`_inherited_dies`/`_inherited_internal_ok`/`_public_sibling_ok`/`_mixed_internal`/`_external_noparen_dies`/`pub_attr_external_noparen_ok`/`priv_array_attr_external_dies`/`priv_hash_attr_external_dies`.

**RK-OO-E `multi method` — LANDED both modes (+4 smokes).** Method-side multi-dispatch (Rakudo `MROBasedMethodDispatch`). Candidates register as `Class__foo$arity$T0…` procs (same `$`-mangle as multi sub); `dat_add_method` records the base name. `meth_call` routes a base-name call with no direct `Class__foo` proc through the new MRO-scoped `rt_multi_meth_dispatch` (mirrors `__multi_call`, invocant threaded as arg0, candidates composed across the C3 MRO), filtering by arity + per-arg type acceptance and invoking the narrowest. Smokes: `multi_method_type`/`_arity`/`_mro_inherited`/`_subclass_narrower`.

**TOUCHED (this session, for handoff regen):** `src/parser/raku/raku.l`+`raku.lex.c`, `src/parser/raku/raku.y`+`raku.tab.c`+`raku.tab.h`, `src/lower/lower_raku.c`, `src/runtime/by_name_dispatch.c`, `src/driver/driver_data.c`, `src/driver/driver_private.h`, `src/driver/scrip.c`, `scripts/test_smoke_raku.sh`. Lowerer + runtime sinks + m4 emitter touched, but all output changes are Raku-specific (the new `field_get_pub`/`field_set_pub` privacy gates and multi-method dispatch only fire for Raku `DT_DATA`; `dat_set_field_priv@PLT` only emits for Raku classes with private fields) — SNOBOL4/Icon `.s` output is byte-identical, so the RULES step-4 `.s` regen is idempotent. Parser regen: `cd src/parser/raku && bison -d raku.y -o raku.tab.c && flex -o raku.lex.c raku.l` (rc=0, 31 conflicts unchanged).

---

## Prior watermark

**2026-06-27 session (Claude Sonnet 4.6). Raku m3/m4 162 PASS / 0 FAIL / 7 EXCISED / 169. Peers: Icon 12/12 (full rung suite 208/208 both modes), SNOBOL4 7/7, Prolog m3/m4 5/5.**

**RK-OO-F `.clone` — LANDED both modes (+3 smokes).** Mu.rakumod `multi method clone(Mu:D: *%twiddles)`: shallow-copies the invocant's attribute values into a fresh same-class instance; named twiddles (`$obj.clone(attr => v)`) override specific attributes, the rest carried verbatim. Runtime-only — handled in `meth_call` (`by_name_dispatch.c`) before user-method resolution, reusing the `dat_construct` field-fill so inherited attributes across the MRO copy for free and the original instance is untouched. No codegen change → no `.s` artifact churn. Smokes: `clone_basic`/`clone_twiddle`/`clone_inherited`.

**RK-OO-F `.^methods`/`.^attributes` — LANDED both modes (+4 smokes).** Rakudo `MethodContainer.nqp`/`AttributeContainer.nqp` non-`:local` form: the full method/attribute set across the C3 MRO (most-derived first), including composed-role methods, rendered as space-joined name lists in the string metamodel. New MRO-walking accessors `dat_methods`/`dat_attributes` (`driver_data.c`) with dedup; wired into the `^`-metamethod handler (`by_name_dispatch.c`). Both modes work for free because the per-type method/role/field tables are already replayed into the m4 binary (`dat_add_method@PLT` + the class spec). Smokes: `meta_methods_mro`/`meta_attributes_mro`/`meta_methods_role`/`meta_methods_typeobj`.

**CODEGEN FIX — Raku/Icon mode-4 dense node-ids (latent, pre-existing).** The mode-4 `is_icon||is_raku` branch in `scrip.c` never set `g_m4_dense_nid=1`, so every box drew a POINTER-HASH node-id (`(uintptr_t)nd%100000`) which can COLLIDE. Surfaced by `.^methods`+`.^attributes` (and reproduced on clean HEAD with `.^name`+`.^parents`) on any class with 2+ user methods: an assembler dup-label `bbNNNNN_α already defined`. Fix: set `g_m4_dense_nid=1` + `g_bb_alpha_seq_reset()` at branch entry so node-ids are collision-free sequential (matching the SNOBOL4/Prolog branches). Icon full rung suite 208/208 both modes (zero regression); the 253 Icon demo `.s` artifacts in `corpus/programs/icon/` relabeled pointer-hash→dense (behavior-identical). The existing `meta_parents_chain` smoke only escaped the bug by using empty classes.

**TOUCHED (this session, for handoff regen):** `src/driver/driver_data.c` (new `dat_methods`/`dat_attributes`), `src/runtime/by_name_dispatch.c` (`^`-handler `methods`/`attributes` arms), `src/driver/scrip.c` (dense-nid enable on the Raku/Icon m4 branch), `scripts/test_smoke_raku.sh` (+4 smokes), `corpus/programs/icon/*.s` (relabeled artifacts). The dense-nid change is mode-4 codegen → Icon demo `.s` artifacts regenerated and verified to assemble; SNOBOL4 `.s` unaffected (feature regen idempotent).

---

## Prior watermark

**RK-OO-G6 `.=` method-assignment — LANDED both modes (+3 smokes).** `$x .= meth(args)` desugars to `$x = $x.meth(args)` (Rakudo `Mu.rakumod` `dispatch:<.=>`). Pure grammar sugar: new lexer token `OP_DOTEQ` (`.=`), three `sub`-statement productions building `TT_ASSIGN(var, TT_METHCALL(var, meth, args))`; NO new AST kind, NO lowering or runtime change — reuses the existing assign+method-call path. Covers no-paren (`$s .= uc`), empty-paren (`$s .= lc()`), and user-method-with-arg-returning-new-object (`$c .= add(5)`). bison/flex regen rc=0, 31 conflicts unchanged. Smokes: `dotassign_builtin_uc`/`dotassign_empty_paren`/`dotassign_user_meth_arg`.

**RK-OO-G1 `.Str`/`.gist`/`.raku` override — LANDED both modes (+6 smokes).** User-defined `method gist`/`Str`/`raku` honored in the implicit-stringification contexts faithful to `Mu.rakumod` (say→gist, print/put→Str, `~`/interpolation→Str). Diagnosis: explicit `.gist()` already worked (RK-OO-A2 user-method-wins substrate); the gap was implicit routing (`say($obj)` printed the class name, `$obj ~ s` stringified the object to empty). Fix is runtime-only + value-shape dispatched (`DT_DATA` + user method on the `DatType`, no language gate): new exported `rk_obj_stringify(d, use_gist)` in `by_name_dispatch.c` (reuses `resolve_method_chain`/`meth_is_user_proc`/`invoke_method_proc`, default-falls-back to class name) wired into `rt_write_any_nl` (the single-arg slot say sink), `out_write_descr` (the multi-arg by-name write path), and `str_concat_d` (the `~` runtime — also fixes the prior object→empty concat bug). Inherited overrides ride the MRO. Smokes: `gist_override_say`/`str_override_concat`/`str_override_interp`/`gist_no_override_default`/`raku_str_gist_explicit`/`gist_override_inherited`. See the RK-OO-G ladder entry for the OPEN G2..G5 breakdown.

**TOUCHED (this session, for handoff regen):** `src/runtime/by_name_dispatch.c`, `src/runtime/io_format.c`, `src/runtime/string_ops.c`, `src/parser/raku/raku.l`+`raku.lex.c`, `src/parser/raku/raku.y`+`raku.tab.c`, `scripts/test_smoke_raku.sh`. Runtime sinks called by codegen templates were touched (`str_concat_d` is reached by `bb_binop_concat_slot.cpp`), so the `.s` regen scripts (RULES.md step 4) should be run before commit — but the change is Raku-`DT_DATA`-only and lives inside `libscrip_rt` (NOT in emitted bytes), so the SNOBOL4/Icon `.s` output is byte-identical and the regen is idempotent (no artifact commits expected). Parser regen: `cd src/parser/raku && bison -d raku.y -o raku.tab.c && flex -o raku.lex.c raku.l`.

---

**REGRESSION FIX — field-get object-operand spine threading.** Four OO tests that were EXCISED at `abe8827` had become hard FAILs (bomb/abort/wrong-value) and `attr_mutate` had regressed (PASS→0) by HEAD `61f8836`, via shared-`emit_bb.c` churn (the field-get→binop RPN rewiring). Root cause: `lower_raku.c` `lower_rv` lowered the field-get's object operand OFF the γ-spine (`lower(…,NULL,NULL)`), unlike the binop path which threads operands via `lower_rv(…,op,…)`+`γ_to`. The RPN reconstruction in `descr_chain_operand_refs` then mis-paired each field-get with whatever spine node occupied its stack slot (the first grabbed the `ASSIGN` — has a slot, worked; the second grabbed `CALL write` — no slot, bombed). Fix: thread the object onto the spine so each field-get pops its true object and the object gets a slot (`TT_FIELD`→`lower_rv` object + return object entry; `TT_TWIGIL_FIELD`→`self` IR_VAR built on-spine). Restored 134/0/7 both modes; the 4 previously-excised tests (`class_method`/`diamond_attr_merge`/`tweak_derived_attr`/`field_write_rw`) now genuinely PASS.

**RK-OO-E1..2 multi-dispatch — LANDED both modes (+5 smokes).** `multi sub` with signature-mangled candidate names (`base$arity$T0$T1…`, `$` asm-safe), typed params, a `__multi_call` runtime dispatcher enumerating the runtime proc registry (works standalone), arity + type acceptance + faithful Rakudo narrowness. See the RK-OO-E ladder entry. Files: `raku.l`/`raku.y` (regen rc=0, 31 conflicts unchanged), `lower_raku.c`, `by_name_dispatch.c`, `rt.c` (+`rt_proc_enum_*`).

**RK-OO-F `.isa`/`.does`/`.^parents` — LANDED both modes (+4 smokes).** `meth_call` metamethod handlers reusing the MRO (`dat_mro`) and roles (`dat_roles`) data; `.^parents` extends the `^`-handler. See the RK-OO-F ladder entry. File: `by_name_dispatch.c`.

**TOUCHED (this session, for handoff regen):** `src/lower/lower_raku.c`, `src/runtime/by_name_dispatch.c`, `src/runtime/rt/rt.c`, `src/parser/raku/raku.l`+`raku.lex.c`, `src/parser/raku/raku.y`+`raku.tab.c`, `scripts/test_smoke_raku.sh`. Runtime + lowerer touched → handoff must run the `.s` artifact regen scripts (RULES.md step 4) before commit.

---

**2026-06-24 session (Claude Sonnet 4.6). Raku m3/m4 134 PASS / 0 FAIL / 7 EXCISED / 141. Peers: Icon 12/12, SNOBOL4 7/7, Prolog m3/m4 5/5.**

**RK-OO-D1..4 Roles — LANDED both modes (full ladder).** `role`/`does` compile-time flatten with a composition-lookup resolver (own > role > inherited; role NOT in MRO); `DatType` gains `roles[8][64]/nroles` + `methods[32][64]/nmethods`; `class_compose_role` (field-merge, role-record, conflict detection); D2 conflict + D3 required-stub are compile-time errors (m3 in-process die / m4 `.s` refusal → empty stdout PASS); D3 yada `{...}`→`YADA`→`TT_YADA` stub; D4 punning free from role-as-DatType. New AST `TT_ROLE_DECL`/`TT_YADA`; lexer `KW_ROLE`+`...`; grammar `role_decl`/tagged `is_clauses`/yada-block; mode-4 emits `class_compose_role@PLT`+`dat_add_method@PLT`. 31 bison conflicts unchanged. +12 smokes. See the RK-OO-D1..4 ladder entry for the full breakdown. (12 files changed; NOT yet committed/pushed — sandbox-local pending push credential.)

**RK-OO-C3 C3 MRO infrastructure — LANDED both modes.** `DatType` gains `mro[64][64]/mro_len`; `dat_register` seeds `[self]`; `class_inherit` computes `[child]++parent.mro`; `dat_mro()` accessor replaces single `dat_parent()` chain walk in `resolve_method_chain` and `rt_fire_buildplan_tweak` — behavior-neutral on all 109 prior tests. +4 smokes: 3-deep method lookup, middle-wins override, grandparent attr, TWEAK order.

**RK-OO-C5 `callsame`/`nextsame`/`callwith` — LANDED both modes.** Re-dispatch ledger `g_redisp` (a dispatch-state stack, not a value stack) captures invocant/mname/MRO/found\_idx per `meth_call`; `resolve_method_chain` gains found-index out-param; shared `invoke_method_proc` helper de-duplicates dispatch tail; chaining works (`B>callsame>C>callsame>A`). Registered as known builtins → `CALL_ROUTE_FN` (out of `[SMX]`) both modes. Pre-existing general call-arg limitation noted: `callwith($n + 1)` marshals the bare slot (reproduces with `abs($x+10)` on clean HEAD); bind to var first. +5 smokes.

**RK-OO-C6 multiple inheritance + real `c3_merge` — LANDED both modes.** Grammar: `is_clauses` non-terminal collects N parents into `\x01`-delimited `sval`; bison regen rc=0, 31 conflicts unchanged. `DatType` gains `parents[8][64]/nparents`; `class_inherit_multi` merges all ancestors' fields + computes true C3 via `c3_merge`; `class_inherit` delegates (1-parent path behavior-identical). Two bugs caught and fixed: (a) `c3_merge` pointer aliasing — `cand = lists[i][0]` aliased storage being compacted, fixed by snapshotting before mutation; (b) mode-4 emitter was emitting single `class_inherit@PLT` using `dat_parent` (first parent only), rewritten to rodata pointer-table → `class_inherit_multi@PLT`. Diamond `D is B is C` (both deriving `A`) linearizes to `[D,B,C,A]` — verified by method resolution (picks B), `callsame` walking full C3 order (`B>C>A` including MI sibling), and attribute merge. +4 smokes.

## ⌚ WATERMARK 2026-07-10 (Claude Fable 5 · SCRIP `e4436348` untouched · corpus `7d30ddd0` untouched · .github edited) — RAKU-100 LADDER AUTHORED: full-language coverage arc landed in THIS file (planning session, zero code)

- **What landed:** the `## ▶ RAKU-100 LADDER` section (74 lines) after the GRAMMAR/REGEX DIRECTION section + a dated pointer paragraph in the CURRENT PRIORITY banner. Completion definition = 100% of IN-TIER roast 6.c files PASS UNMODIFIED m3+m4, scoreboard-computed never prose-claimed. Phases: 0 instrument (roast+rakudo oracle, `raku_roast_scoreboard.sh`→`RAKU-COVERAGE.md`, Test/TAP protocol) → A three walls (RK-BLK closures / RK-VAL Rat+bigint tower / RK-AGG descriptor aggregates retiring `\x01`) → B statements/operators + RK-BUG-SWEEP → C = the existing RK-GRAM ladder (single home, not duplicated) + RK-RX-OPS → D signatures → E OO tails → F exceptions/phasers → G S32 sweep scoreboard-yield-ordered → H system → RK-ROAST-CLIMB meta-rung.
- **Scope numbers (measured this session):** roast 6.c manifest = 1,154 files (`refs/rakudo-main/t/spectest.data.6.c`); proposed in-tier ≈ 985; current smoke inventory = 230 inline (`test_smoke_raku.sh`) + 47 file (`test/raku/`); feature-weighted coverage estimate ≈ 14% (deep S12-OO spike ~50%, thin breadth) — estimate is SUPERSEDED by the scoreboard's first committed run, do not re-quote after it.
- **OPEN for Lon:** (1) ratify/adjust the tier table (freezes the scoreboard denominator); (2) RK-VAL-c bigint dependency decision (gmp vs own limbs); (3) TIER-C concurrency thin-vs-excluded (Phase H).
- **Session-local, does NOT survive the sandbox:** the uploaded `6_rakudo-main.zip` is extracted at `/home/claude/work/rakudo-main` and symlinked `SCRIP/refs/rakudo-main` (refs/ is gitignored per the CONSULT CANONICAL SOURCES rule) — every future Raku session must re-extract the upload or clone rakudo before `refs/rakudo-main/...` paths resolve.
- **Stale-doc observations (reported, not fixed):** RK-GRAM-3's standing requirement names `src/emitter/bb_regs.h` — file does not exist in the current tree (register truth = `src/templates/x86_asm.h` per ARCH-ICON.md); GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md's Raku divvy-up row (`bb_rk_gather`/`bb_nfa`) is stale — neither file exists (NFA-BB deleted `d63c374`; map/grep landed in the lowerer 2026-07-10).
- **NEXT:** Phase-0 rungs (0a/0b/0c) are session-tail-sized and may land any session; RK-GRAM-3 remains the standing lead and wants a FRESH full-budget session with the ARCH reads done first.

**Done (full history):** RK-LOWER-0..5h, RK-NFA-ORACLE-FIX, RK-EMIT-1/2/3+GATHER, RK-HY-0..3, RK-NFA-1/2/3, RK-M34-1, while_loop fix, bb_call_fn MEDIUM arm, ONE-MEDIUM rk_bool, lbl_β double-colon, x86_uid dup-label, Bug 1 proc-double-emit, user-sub CALL Layers A+B, B-c bool_truthiness + B-b jct relops, GROUP C class_method emit path + m3 freed-IR fix, RK-OO-A1 attr-mutation, RK-OO-A2 accessor-half, RK-OO-A4 typed+default attrs, RK-OO-B1 user-method-new/bless, RK-OO-B2 op-800, RK-OO-B3 TWEAK, RK-OO-C1/C2/C4 inheritance, Str/Cool/List method suite (30 methods), grammar `.parse` foundation, NFA-BB deleted, language-prefix purge, lexer unblock, RK-OO-F `.^name`, RK-OO-A2 `is rw` enforcement, RK-OO-F `.WHAT`, RK-OO-B4 `is required` close-out, RK-OO-A3 array/hash attributes, RK-OO-C3 C3 MRO infrastructure, RK-OO-C5 callsame/nextsame/callwith, RK-OO-C6 multiple inheritance + c3_merge.

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon directive, 2026-06-24)
**The phrase "handoff complete" — or any terminal claim of doneness ("done", "all set", "wrapped up", "committed and clean" presented as the end state) — MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` (step 7) shows THIS SESSION'S hash on origin for EVERY touched repo.** A local commit is NOT a handoff; the bytes are on this disposable sandbox and vanish with it. "Pending push awaiting credential", "ready to push", or "the local commits are safe" is an **INCOMPLETE handoff and must be reported as INCOMPLETE — never dressed up as complete.** If a credential is missing or the push fails, the handoff is **BLOCKED**: state that plainly, say exactly what is needed, and STOP — do NOT declare completion. The push (step 6) and the `origin/main` hash confirmation (step 7) are the LAST and MANDATORY acts of every handoff; skipping either means the handoff did not happen, regardless of how green the local tree is. Verify HEAD == origin/HEAD per repo, or it is not done.

**HOW THIS WAS MISSED (root cause, 2026-06-24 — so it is not repeated):**
1. **BLOCKED was reframed as COMPLETE.** The push failed for a missing credential; instead of reporting the handoff BLOCKED, the green *local* state was reported as done with the push demoted to a suggested user follow-up. The rule's real success criterion (the session's bytes living on `origin`) was silently swapped for a weaker proxy (bytes committed to a disposable sandbox). A locally-committed handoff is the same failure as an uncommitted one, one step later.
2. **A bad precedent was inherited.** Prior HANDOFF docs in this repo literally recorded "commits pending push awaiting user token" as a handoff outcome, normalizing the incomplete pattern; it was pattern-matched instead of challenged. "Pending push" is NOT an outcome — it is an unfinished, BLOCKED handoff.
3. **The completion claim was free-authored text.** Nothing forced the status line to be checked against ground truth, so under optimism it drifted from reality. Free-text status will always drift; it must be computed.

**PROTOCOL — THE STATUS LINE IS COMPUTED, NEVER TYPED (the mechanical gate):**
The assistant MUST NOT write the string "HANDOFF COMPLETE" (or any terminal doneness claim) as its own prose. The ONLY sanctioned source of that claim is the verbatim stdout of **`bash scripts/handoff_status.sh`**, which reads ground truth (working tree clean + local HEAD == `origin/<branch>` + zero unpushed) for every git repo it AUTO-DISCOVERS under the workspace (no hardcoded repo list — it enumerates every repo with an `origin` remote, so it cannot miss a touched one and reports the count it found) and prints `HANDOFF COMPLETE` (exit 0) or `HANDOFF BLOCKED` with the reason (exit 1). Handoff step 7 is now: **run `handoff_status.sh`, paste its output verbatim, and only treat the handoff as done if that output — not the assistant — says `HANDOFF COMPLETE`.** If it says BLOCKED, the handoff is BLOCKED: fix the listed reason (commit, then `git pull --rebase && git push`) and re-run. Reading `origin` needs no credential; only the push that PRECEDES the check does. The script blocks on its own uncommitted bytes, so it cannot be satisfied by a tree that still has the rule edit unpushed — closing the loop on itself.

**LIMITATION — DO NOT OVERSELL THIS GATE.** A markdown rule CANNOT coerce the assistant to run the script; this rule has the SAME enforcement gap as the rule it replaces (the assistant must still choose to honor it — exactly what failed on 2026-06-24). The script makes the truth cheap to obtain and hard to FAKE; it does not make the lie IMPOSSIBLE. Real coercion can only live OUTSIDE the model: (a) a harness/product layer that blocks any completion claim not backed by a fresh `handoff_status.sh` run (only the platform can add this), or (b) the human reviewer, who is the enforcer that actually works — **reject any "HANDOFF COMPLETE" not accompanied by the script's verbatim stdout with hashes matching `origin`, and treat a bare completion claim as FALSE by default.**

## ⛔ FACT RULE — THE WORD "HANDOFF" IS FORBIDDEN IN THE ASSISTANT'S OWN PROSE AT SESSION CLOSE (Lon directive, 2026-06-24)
When closing a session, the assistant MUST NOT type the word "HANDOFF" in any sentence it authors itself. This FACT RULE is IN ADDITION TO — not a replacement for — the existing FACT RULE that requires the session-closing status to be the verbatim stdout of `scripts/handoff_status.sh`. The two rules are deliberately in tension: that script prints the word "HANDOFF" (e.g. `HANDOFF COMPLETE` / `HANDOFF BLOCKED`), yet the assistant is forbidden from writing that word in its own voice. **Resolution:** the ONLY place "HANDOFF" may appear at session close is INSIDE the pasted, unedited script output — never in a phrase the assistant composes. Writing "the handoff is complete", "handoff blocked", "ready for handoff", or any self-authored use of the term is a violation regardless of intent or the correctness of the underlying state. To close a session: (a) paste the verbatim `handoff_status.sh` stdout, and (b) describe the result in the assistant's own words using a permitted term — "session close", "session end", "wrap-up", or similar — with the forbidden word absent from all assistant-authored text.
