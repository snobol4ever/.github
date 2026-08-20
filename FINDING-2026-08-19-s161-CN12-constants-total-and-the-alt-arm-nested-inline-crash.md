# FINDING s161 (2026-08-19, local seat: Claude Fable 5, CN front) — CN-12: every &constant admitted everywhere; and the ALT-arm nested-substitution m4 crash that bounds inline depth

**Order executed (Lon, in-chat, verbatim in substance):** *"There are no unsupported kinds. Get &constant working. You are not allowed to REFUSE a SINGLE ONE."* This supersedes the s158 parking of CN-3c/T2b behind T4. "Refuse" was never an error — it was every consumer of the constant machinery *refusing to trust* a declared tree and falling back to the dynamic road. CN-12 makes the machinery total: **every declared `&constant` now works in every position** (bare pattern position, `*&defer`, chained through other constants, as cset arguments, recursive, mutually recursive, forward-referenced), and the only depth question left is *how much gets inlined*, bounded by two named engine defects, not by shape tests.

## What landed (SCRIP `5a12e050` = CN-12, over `2e69c21c` = CN-10/11; corpus `5fc94f9f` witnesses)

| consumer | before | after |
|---|---|---|
| `sno_cset_fold` | keyword knowledge = a **hardcoded two-name table** (lcase/ucase); measured: `SPAN(" " &T)` refused for the `&T` leaf alone | chases declared scalars, constant chains, ILIT stringify, and — behind `SCRIP_PAT_INLINE` — **single-write bare vars** via new `sno_var_val` (guard-for-guard the mirror of `sno_seal_pat`: same table, same wrcount/fz-poison/fragment gates) |
| `sno_pat_inline_ok` | frozen-literals-only; VAR arm admitted the string "REM" | admits VAR leaves (PB-1s snapshot-defer is the standard statement mechanism; fz trees are closed over plain names so the inference path cannot widen through this), KEYWORD leaves, DEFER leaves. FENCE/captures/BAL stay excluded per **may-only-add-passes** — each exclusion already names its deleting rung |
| `sno_pat_supported` | no TT_KEYWORD arm ("the ONLY blocker", s148) | `TT_KEYWORD → sval != NULL` — honest only now, because emission is total (next row) |
| `sno_pat_node` | bare `&Name` in pattern position = **sno_fatal compile bomb** | new TT_KEYWORD arm, total: declared-scalar QLIT → literal box; declared pattern → compile-time substitution; everything else → PB-1s snapshot-defer (pre-chain `sx_lower`s the keyword tree itself, so T1 folds scalars there and 342/251 semantics hold at build time; PATV$ cells born `pat_static=1`) |
| registration pre-scan | `&Name = pattern` only | also notes **bare-var QLIT scalars** into the same seal table (the T1 widening precedent — never a second table); resolver applies the guards |

Recursion is handled by `sno_kw_chase` (function-local static stack, kdepth precedent): `&R = 'q' *&R | 'z'` and mutual `&A`/`&B` inline one level and recurse dynamically below — correct semantics, never a hang, never a bomb.

## Three substitution guards, each convicted by a minted witness (none guessed)

1. **`!g_sno_in_patproc`** — substitution inside the PAT$ blob builder core-dumped (witness t7 arm B): blob geometry predates big inlined structures. Same guard `sno_fz_tree` already carries.
2. **`g_sno_pat_match_ctx`** — substitution while lowering a pattern **value build** (`Line = ARBNO(*&Command " ")`) corrupted the blob/value duality; the crash detonated only at the first match *through* `Line` (t8 "built ok" vs t7 crash). Same guard `sno_fz_tree` carries.
3. **TOP-LEVEL-ONLY** (`sno_kw_chase` op 3) — the real find of the slice, next section.

## ⛔ THE OPEN ENGINE DEFECT THE DEPTH LIMIT ROUTES AROUND (next-seat rung, witness pinned)

**Nested keyword substitution inside an ALT arm crashes m4 and passes m3.** Minimal witness u3 (pinned as `corpus/probe/cn/cn_nest_alt_defer.sno`): `&P = &W2 | &N2` with `*&P` — substituting `&P` and then its members mid-ALT-emission produced a binary whose match end dies in `getenv` (`c_rt_dcap_end_ok_open`, pattern_match.c:721 → `rt_match_end_all`) — **environ/stack corruption of the B2 record class**, detonating far from the cause. The FINAL graph is exonerated: its literal twin `(SPAN|SPAN)` compiles and passes m4 (witness u4/t9/aa), and CAT-nesting passes (u2) — the defect is in the *emission mechanics of substituting mid-ALT-collection*, not the shape. **Rung:** root-cause via asm-diff u3-vs-u4 match regions (gdb frame recorded above); when it lands, delete the op-3 depth limit and `cn_nest_alt_defer`'s defer count drops while its output stays byte-identical — the witness is built to flag exactly that.

Until then: nested refs take the defer road — correct, working, mode-identical.

## Measured (worktree baseline at pushed `2e69c21c`, same-arm law)

- **Shapes:** `SPAN("a" &T)` defer 3→0 · bare `&Cmd` 3→0 · direct chain `*&Item` 5→0 · `SPAN("a" t)` single-write var 3→0 · recursion/mutual/forward-ref all match, m3+m4.
- **Boards:** probe/cn **36/36** (m3 × both killswitch arms + m4; includes the two mid-slice reds, both cured) · UDC gate **27/0** · crosscheck **307/10 m3 · 306/10 m4 · DIVERGE=0**, FAIL-sets byte-identical to pre-CN-12 · smoke 6/1 (the `define` red is pre-existing B1, reproduced on baseline).
- **Blast radius:** OFF-arm (`SCRIP_CONST_STATIC=0 PAT_INLINE=0 CONST_INLINE=0 CONST_T1=0 CONST=0`) **0 movers of 318** crosscheck compiles vs baseline — killswitch byte-identity exact. Default arm moves **4** programs (`063–066_pat_fence_fn_*`), all PASS vs ref, defer structure unchanged.
- **beauty_c census** (compile-time — the honest medium while T4/B1 mask behavior): `rt_keyword_read` PLT sites **196 → 151**; defers hold 216 — beauty's `*&Name` sites live inside pattern *value builds*, where guard (2) correctly keeps the defer road. That conversion belongs to the T4/B1 lane, not to admission.

## Also recorded this slice (context for the ledger)

- s161 opened with CN-9b (corpus `ec03830e`): beauty_c regenerated **with** the `&USER_DECLARED_CONSTANTS = 1` declaration; census reproduced s151 exactly — **falsifying the s157/s158 premise** that T1/T2 "cannot fire" on an undeclared beauty_c (the namespace is born open; they were firing all along). The declaration is today a runtime no-op and becomes load-bearing at the default flip (SEAT-KW's gated step).
- CN-10 (SCRIP `2e69c21c`): `NV_EXISTS_fn` → `NV_CONST_ASSIGNED_fn` (is_const made truthful at both creators; the bare-`return;` in `NV_SET_fn` fixed).
- CN-11 (same commit): **live silent wrong answer** — the shared `kw_read` cascade let Icon's `&pi` shadow a sealed `&Pi = 3.14` (read back `3.141592653589793` under `SCRIP_CONST_T1=0`; killswitch arms disagreed on a value). Declared binding now beats the shared cascade; gate widened (`cn_t1_scalar_fold` swept in the T1=0 arm) and the UDC gate's **m4 column de-vacuumized** (it compiled once at the default arm and varied a lowering switch on the finished binary — s68 class; now compiles inside the loop; proven: 25/2 without the fix, 27/0 with).

## Next-seat items, in order
1. **ALT-arm nested-substitution root-cause** (above) → delete the depth limit.
2. **LEN/TAB/POS/RTAB/RPOS integer args through constants** (`LEN(&N)`) — needs a small int-fold at the five arms; currently correct via the defer road.
3. **WAVE-2 beauty_c regen**: declare `nl/tab/digits/epsilon` as literals (`&tab = " "` etc. — cset_fold chases QLIT and CHAR(ILIT) but the T1 note site admits literals only), then re-census — the 50 BREAK boxes' args fold next.
4. `$()` ruling implementation + the pinned write-half witness (was mid-write when the CN-12 order arrived).
