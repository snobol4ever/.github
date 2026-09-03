# FINDING — jcon test suite censused by class; &level's missing entry-side increment cured

**seat02 · 2026-09-03 · FLEET-8 (Lon 2026-09-03 ~14:10 CDT) · row `icon-jcon-suite-39-non-pass-censused-by-class-and-cured`, dispatched by ceo, HQ target hq_B**

## Baseline (fresh, two independent measurements agree)

`bash scripts/test_icon_jcon_suite.sh` (`corpus/packages/icon/jcon_tests`, 81 programs, oracle = vendored JCON `.std` files):
- ceo's own reading at SCRIP `4f847224`, 13:52 CDT: m3 PASS=42 FAIL=25 CRASH=12 HANG=2; m4 PASS=40 FAIL=31 CRASH=8 HANG=2.
- seat02's independent re-run at SCRIP `a3faade1` (post-pull, before any edit): **identical** — m3 PASS=42 FAIL=25 CRASH=12 HANG=2; m4 PASS=40 FAIL=31 CRASH=8 HANG=2. Two agreeing runs, different sessions, different trees a few commits apart, same result — the baseline is solid.

## Cured: &level's missing entry-side increment (SCRIP, this session)

`kwds.icn` and `level.icn` (2 of jcon's 25 m3 FAILs) both failed on a single wrong value: `&level: -60` (kwds) instead of a small positive integer. This is the **known, already half-cured** bug from `FINDING-2026-08-30-seat01-icon-level-exact-fix-sites-located-implementation-ready.md`: `xa_flat_zframe_epilogue_{γ,ω}_str()` (`src/templates/xa/xa_flat.cpp:396-469`) already decrements `rt_k_level`/`kw_fnclevel` on every ICN-FR-2/wire-stack activation's exit (landed by seat01, 2026-08-30), but the matching **entry-side increment was never landed** — so every call decremented a counter nothing had incremented, driving it negative over repeated calls (exactly `-60`'s shape).

**Landed the entry side**, `src/emitter/emit.cpp`, inside `else if (g_emit.flat_lcl_proc)` (~line 2932-2975), gated identically to the existing exit side (`_use_zframe_install && _iws`, i.e. `icn_cells_graph` under wire-stack): a single `x86(...)`-DSL block (`_level_incr`) mirroring `bb_define_activate`'s own `enter_env` pair verbatim (`bb_define.cpp:94-101`: `rt_k_level++; kw_fnclevel = rt_k_level - 1;`), inserted via `bb_emit_x86()` in **both** the TEXT and BINARY arms at the same point the existing `_lseed` NULVCL block is inserted — this sidesteps the FINDING's original concern about hand-verifying new raw BINARY bytes entirely, since `x86(...)`/`bb_emit_x86` are BOTH-MEDIA by construction (TEMPLATE-ONLY law) and the surrounding raw-byte frame-carve is untouched.

**Also required** (found empirically, not anticipated by the original FINDING): `rt_k_level`'s initial value was `1` (`src/runtime/rt/rt.c:392`), which double-counted `main`'s own activation once the entry-side increment landed (`main` itself is a `flat_lcl_proc`/`icn_cells_graph` activation like any other Icon procedure) — every read was off by exactly +1 (`2 3 2` instead of `1 2 1` on the minimal repro). Changed the initial value to `0` — matching "0 activations deep before `main`'s own entry runs".

**Verification** (both directions, per RULES.md's two-part-proof law):
- Minimal repro from the original FINDING (`main` writes `&level`, calls `f`, writes again; `f` writes `&level`): **`1 2 1`, both modes, byte-identical** — exactly the documented target.
- `kwds.icn`: m3 now byte-identical to `.std` (was the sole diff line).
- jcon board: **m3_pass 42→44, m4_pass 40→42** (kwds and level both flip FAIL→PASS, both modes; CRASH/HANG buckets untouched by this change, as expected — it's a FAIL-bucket cure).
- Icon smoke: `PASS=14/14` both modes, unmoved.
- **Icon STRICT rung suite watermark MOVED** (control arm, not untouched — see below).
- SNOBOL4 floor (shared-emitter control arm, fresh `test_corpus_snobol4.sh`): `PASS=1679 FAIL=0` both modes, `SKIP=0`, GATE OK — the shared `emit.cpp` edit does not leak into the non-Icon path (gated on `icn_cells_graph`, which SNOBOL4 graphs never set).

### ⚠️ Discrepancy: the pinned Icon STRICT watermark improved, and the task's own DONE-WHEN names the old number

The doorbell/task brief pins `test_icon_rung_suite.sh` at `PASS=264 FAIL=6 BADEXIT=1 XFAIL=27 TOTAL=298` as a **no-regression control arm**. After this cure, three fresh, mode-agreeing runs read:

```
PASS=266 FAIL=4 BADEXIT=1 XFAIL=26 XPASS=1 TOTAL=298
```

+2 PASS / −2 FAIL, all three modes (interp/run/compile) identical — **a real improvement, not a regression or a flake**: `&level` is exercised by rung-suite witnesses too (the goal file's own 2026-08-30 cursor names `level`/`kwds`/`rung37_keywords` as `&level`-half-cure casualties), and this session finished what seat01 started. The **XPASS=1** means one witness carries a now-stale `.xfail` marker (a program marked expected-fail that now genuinely passes) — per `test_icon_rung_suite.sh`'s own semantics this should be promoted (`rm` its `.xfail`), but this session did not track down which witness it is (a `VERBOSE=1` run to identify it did not complete before this session's time budget closed) — left for whoever picks this up, or hq_B.

Per this session's own doorbell precedent (hq_B's Icon-master-board correction, same day) and RULES.md's own rule that a bare quoted number is not a measurement: **this is not a blocker.** Routed as an ask below; the fresh, three-mode-agreeing `266/4/1/26/1 of 298` is the honest current watermark and should replace the stale `264/6/1/27` string in the task's DONE-WHEN and anywhere else it's pinned.

## Census: the 12 CRASHes, by class (5 classes; rows minted for each, see below)

1. **`icon-jcon-class-genhost-recursive-generator`** (5 progs: btrees, collate, geddump, genqueen, recogn) — the existing `[GENHOST] ... RESERVES NOTHING` / `BOMB -- N-2 armed` refusal for recursive/forward-referenced generator callees. Not new: this is `[[icon-n2-recursive-generator-per-activation-storage]]`'s own target, and that row's blocker (`coexpr-stack-leaves-the-compacting-gc-heap`) was cured 2026-09-02 — **the design row is unblocked** and these 5 programs are ready-made acceptance witnesses for it.
2. **`icon-jcon-class-coexpr-create-arg-capture`** (cxprimes confirmed; likely contributes to cxtrace) — **new discovery, fully root-caused via direct asm inspection**, deep architectural gap. `create PROC(x)` where `PROC`'s body reads its own parameter (of ANY type — confirmed with both a coexpression value and a plain integer, the latter silently reading `0` instead of crashing) is broken: `scrip_coexpr_create` (`rt_coexpr.c:144`) snapshots `frame_region` bytes of the *caller's* stack into a heap `frame_copy`, and `scrip_coexpr_trampoline_entry` sets **RBP** to that snapshot before jumping to the deferred body-entry label — but the deferred body-entry chain's own nodes are emitted via ordinary `x86_fb()` (=RSP) addressing, so on first activation they read the coexpression's own fresh, unrelated pthread stack instead of the captured snapshot. Minimal 8-line repro and full asm trace in the minted task file. **Deliberately not fixed this session** — the correct fix routes the deferred-body chain through the ONE-DEPTH-AUTHORITY / seam-crossing machinery (`op_xf_off`/`xop_frame_slot`/`zone_ref`) shared across every language, which is a dedicated, N-2-scale design effort, not a patch.
3. **`icon-jcon-class-assign-lv-nameless-guard`** (errors.icn) — the known, already-named `AWAITING LON` ASSIGN-LV gap (`GOAL-IR-IMMUTABLE-EMIT.md`, N-6). Routed, not touched.
4. **`icon-jcon-class-forward-ref-deferred-emit`** (evalx, proto) — `bb_emit_end: N unresolved forward reference(s)`, a BB port that's referenced but never wired. Both are syntax-torture-test programs (proto.icn's own header: "samples of all the basic syntactic forms in Icon"); evalx has zero `create` calls, so this is **not** the same mechanism as class 2. Not yet root-caused to a specific construct — needs its own ablation pass.
5. **`icon-jcon-class-coexpr-thread-resource-crash`** (cxtrace, iobig) — bare SIGSEGV, no self-diagnosing message. cxtrace segfaults inside glibc `create_thread()` called from `scrip_coswitch` (deep nested `create`/`dcreate`/`dsusp` chains — possibly address-space exhaustion from many 8MB pthread stacks, one per co-expression, since the 2026-09-02 pthread-stack change). iobig segfaults inside `kw_cset_reg`/`kw_cset_prime` (one-time lazy keyword-cset init) with a coexpr-switch frame nearby (`__new_sem_wait_slow64`) — possibly that lazy init isn't safe to re-enter from a freshly-activated coexpression thread. gdb backtraces in the minted task file. Not confirmed to share one root cause.
6. **`icon-jcon-class-recursive-scan-corruption`** (others.icn) — SIGSEGV in `__strlen_evex` with a corrupted/NULL return address. Plain (non-generator) recursion combined with string-scan (`?`) at every recursion level; possibly gap-census item 8 (scan cursor has two homes) but not confirmed against this witness specifically.

**Not censused as classes** (documented, not routed as rows): the 2 HANGs. `lgint.icn` is large-integer/bignum arithmetic — explicitly `⛔ Lon scopes` per `GOAL-ICON-100.md`'s PARKED section (N-7 bignum cluster); not opened. `toby.icn`'s own header says "only for Jcon; does not work under Icon v9" and exercises behavior at the exact int64 boundary (`16r7fffffffffffffff`) — likely a range-generator overflow, but the program self-declares non-standard/JCON-only semantics, so it's lower priority and left unrowed.

## Oracle check (per the task's own instruction to verify before trusting a red)

`jcon_tests/*.std` are the suite's own vendored oracle files (per `test_icon_jcon_suite.sh`'s header comment, JCON's own `addtest` harness expected outputs) — not icont/iconx. All diffs and crash signatures above are graded against `.std`, consistent with every other reading in this FINDING.

## Rows minted (6, `icon-jcon-class-*`, all FREE, DONE-WHEN verified to say NO on current state — see each task file)

`icon-jcon-class-genhost-recursive-generator` (rank 1) · `icon-jcon-class-coexpr-create-arg-capture` (rank 0) · `icon-jcon-class-assign-lv-nameless-guard` (rank 2) · `icon-jcon-class-forward-ref-deferred-emit` (rank 1) · `icon-jcon-class-coexpr-thread-resource-crash` (rank 2) · `icon-jcon-class-recursive-scan-corruption` (rank 2).

## Board delta

jcon suite: m3 PASS **42→44** / FAIL 25→23, m4 PASS **40→42** / FAIL 31→29 (CRASH 12/8, HANG 2/2 unchanged — this cure came from the FAIL bucket, not CRASH; the crash classes above are real work for a future session, most of it beyond one sitting's scope). Icon STRICT rung suite (control arm): `264/6/1/27→266/4/1/26/1(XPASS) of 298`, all three modes agreeing — **ask hq_B to bless this as the fresh pinned watermark and to promote the stale XFAIL marker.**

## Ask (routed to hq_B, Icon ask target per this session's doorbell)

1. Bless `PASS=266 FAIL=4 BADEXIT=1 XFAIL=26 XPASS=1 TOTAL=298` as the current Icon STRICT watermark (supersedes `264/6/1/27`); identify and promote the stale XFAIL marker behind the XPASS.
2. `icon-jcon-class-coexpr-create-arg-capture` (this FINDING's largest discovery) is design-scale work, same shape as N-2 — worth a dedicated session/rung of its own rather than sitting as a jcon-suite sub-row indefinitely.
