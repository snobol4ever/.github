# FINDING — THE NV_* MEMO LANDED, AND THE KILLSWITCH CAUGHT AN UNSOUND FIRST DRAFT BEFORE IT COULD LIE

**Seat:** hq_P · **2026-08-22 s258** · **Class:** MEASURED · SCRIP `db8f96d6` · **Grant:** Lon in-chat, "Sure. Add a global variable."

## What landed

SPITBOL's `vrblk` discipline applied to our `NV_t` (Lon: *"follow SPITBOL's algorithm almost verbatim"* for NV_*).
`sbl.min` keeps every `vrblk` in the **static area** — *"allocated dynamically but never deleted or moved around"* —
so SPITBOL's variable hash table only ever **interns**; compiled code holds the block. That is why SPITBOL runs a
**127-bucket** table (`e_hnb`) and spends **3.97%** in variable access (`b_vra`) while we spent **45.5%**.

⭐ **Our `NV_t` already satisfied SPITBOL's precondition and nobody had used it:** `rt_ws_alloc` is a pure bump
allocator over an island whose cursor only advances; the GC **marks** `HB_WS` blocks but never moves or frees them
(`gc_heap.c:358` reuses `->fwd` as a **mark-stack link**, not a forwarding address); entries are only ever prepended;
and `NV_SET_fn` **reuses** an existing entry rather than shadowing it. So a resolved block is valid for program life.

**Measured, `roman.sno` N=20,000, RT_OPT=`-O0` corpus arm for gates / `-O2` for the number, output verified
(`check: 1102`, the clean oracle's answer, on every run):**

| | before | after (unsound draft) |
|---|---|---|
| Ir @ N=20,000 (m3) | 1,049,108,015 | 785,090,397 |
| Ir/iteration | 52,455 | 39,255 |
| vs clean SPITBOL 7,966 | 6.58x | 4.93x |
| `_var_bucket_find` | 227,096,499 (22.42%) | **absent** |
| `__strcmp_avx2` | 94,841,573 | 37,713,568 |

⛔ **That 25.2% figure belongs to the UNSOUND draft and is NOT the shipped number** — the hardened version pays a
`strcmp` per hit. The `-O2` re-measure is in flight and will be recorded when it lands.

## ⛔ THE PART WORTH KEEPING: THE KILLSWITCH IS THE CONTROL, AND IT CAUGHT ME

The first draft keyed the memo on the call site's name **pointer** with no validation, reasoning that a hit could
never become a different entry. The corpus A/B said otherwise, immediately and unambiguously:

| arm | mode-4 |
|---|---|
| memo **ON** (naive) | PASS=335 **FAIL=22** |
| memo **OFF** (killswitch — the old algorithm exactly) | PASS=355 FAIL=2 |

**Two hazards the naive version missed, both invisible to inspection:**
1. **A NAME POINTER IS NOT STABLE.** Emitted call sites pass a baked literal — but the **runtime** also passes stack
   buffers: `c_rt_defer_close` builds one in `char nb[40]`, `tbl_key_str` formats into the caller's `char kb[64]`.
   The same address holds different strings at different moments, so a pointer-keyed hit can hand back the wrong
   variable. **Cured** by validating every hit with `strcmp` against the block's own name.
2. **SHADOWING.** `_var_bucket_find` returns the **first** chain match and inserts are **prepended** — and unlike
   `NV_SET_fn`'s slow path it does *not* filter on `_nv_ordinary`, so a later insert can legitimately shadow a cached
   entry. `strcmp` cannot see that. **Cured** by a generation counter bumped at **all three** insertion sites (a
   missed site reintroduces the exact bug; the third was found only by grepping every `_var_buckets[h] = e`).

⭐ **The lesson, and it is the session's second instance of the same shape:** a soundness argument I found convincing
was wrong, and the thing that caught it was a **command** — the killswitch A/B — not review. Earlier the same day a
confident piece of arithmetic (5,600 Ir per pattern op) was disproven by a profile. **Every non-trivial optimisation
here ships with a killswitch precisely so the control exists before the claim does.**

**Gates, RT_OPT=`-O0`** (the arm where the standing reds are defined, since hq_C has C-0 reopening at `-O2`):
corpus **m3 357/2, m4 355/2 + 2 SKIP** — identical to the memo-OFF control, both failures the documented standing
reds (`160_pat_alt_inner_gen_resume`, `demo_treebank`). `test_gate_emit_no_lang.sh` OK.
`test_gate_template_medium_invisible.sh` 0 against ceiling 0.

## ⭐ THE NEXT BOTTLENECK IS ONE CALL SITE, AND THE CURE MAY ALREADY EXIST

After the memo, the deferred-pattern cluster is the largest thing in the program — larger than our emitted code
(15.77%): `c_rt_defer_close` 11.60% + `rt_defer_run_all` 8.40% + `rt_defer_get_pat_dtp` 6.26% + `rt_dfx_push` 3.58%
= **29.8%**, every one of them called **exactly 1,403,811 times** — one fixed pipeline, **70 per iteration**.

**It is a single static site.** `roman.s` contains exactly **one** defer call site, `n44_match_defer`, and it is the
bare `T` in `'0,1I,2II,…' T BREAK(',') . T`. With `&ANCHOR = 0` the match restarts at every position of the 40-char
subject, and we **re-read and re-close the deferred `T` at each starting position** — ~20 positions × ~4 recursion
levels ≈ 70.

⛔ **SPITBOL does not do this.** `REFERENCE-SPITBOL-BEAUTY-CONSTRUCTS.md` §7: deferral is what `*expr` *means* —
*"evaluated at use time, not construction time."* A **bare** variable operand is evaluated when the pattern
expression is built, once per statement. `lower_snobol4.c:1398` shows our `case TT_VAR:` in pattern position lowering
straight to `IR_MATCH_DEFER`.

⚠️ **This is a CORRECTNESS question before it is a performance one, and it belongs to hq_C.** If a pattern contains a
function that assigns the variable mid-match — beauty's `NRETURN` conditional-assignment idiom is exactly that —
SPITBOL still matches against the **already-built** pattern while our deferred read would see the new value. Answers
agree on `roman` today (`check: 1102` both ways), so nothing is wrong *now*; it is conservative deferral, not a wrong
answer. **No unilateral change from this seat.**

⭐ **AND THE MACHINERY TO FIX IT IS ALREADY IN THE TREE — three separate mechanisms, none reaching this case:**
- `cx->pre[]` — a pre-evaluation list the lowerer already builds beside every deferred node (`lower_snobol4.c:1399`),
  consumed at :1842 to hoist a value into a `PATV$n` global with `pat_static = 1`.
- `SCRIP_PAT_INLINE` + `sno_fz_tree()` — inlines a pattern variable's tree when its value is a known pattern. `T`
  holds a **string**, not a pattern, so `sno_fz_tree` finds nothing and it falls through to the deferred path.
- ⭐⭐ **`&user_defined_constants` (Lon s258) — the escape hatch, already built and already bypassing the defer.**
  `lower_snobol4.c:1393` — a sealed `&NAME` in pattern position is folded at lowering by `sno_const_val` (as a
  literal) or `sno_const_pat` (as a pattern tree) against the `g_sno_seal[]` table, and **never reaches
  `IR_MATCH_DEFER` at all**. ⛔ It cannot help `roman`'s `T`, which is the capture target of `BREAK(',') . T` and
  genuinely varies (sealing it would raise error 341). **Where it pays is a pattern variable assigned once and
  thereafter only read — beauty's `*Expr0…*Expr17` grammar is the textbook case.**
