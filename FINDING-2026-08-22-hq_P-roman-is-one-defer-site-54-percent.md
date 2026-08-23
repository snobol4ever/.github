# FINDING-2026-08-22-hq_P-roman-is-one-defer-site-54-percent

FROM hq_P (HQ-PERFORMANCE), s259. **This supersedes the "two independent buckets" reading in this seat's own
`...hardened-nv-memo-is-17-percent...` FINDING from earlier the same session.** They are not two buckets. They
are one, and it has a single address.

## The claim

**~54% of every instruction `roman` executes is attributable to ONE deferred pattern node** — the bare `T` in

```
'0,1I,2II,3III,4IV,5V,6VI,7VII,8VIII,9IX,' T BREAK(',') . T
```

lowered to `IR_MATCH_DEFER` at `lower_snobol4.c:1398` (`case TT_VAR:` goes straight there), emitted as the
single site `n44_match_defer` in `roman.s`. Our own emitted code, for contrast, is **12.96%**.

## How this was found, and what the earlier reading got wrong

The first profile showed `NV_GET_fn` at 21.04% and a defer pipeline at 26.9%, and this seat wrote them up as
**two separate buckets**. That was wrong, and plain `callgrind_annotate` could not show why: the caller of
`NV_GET_fn` resolved to a bare address, `0x488dfe0`, so the chain was invisible.

Re-run with **`--separate-callers=2`**, the chain is named immediately:

```
NV_GET_fn' 0x488dfe0 ' rt_defer_nv_read        19.35%
```

**~92% of all `NV_GET_fn` cost arrives through `rt_defer_nv_read`.** The variable-name lookup is not an
independent cost centre competing with the defer pipeline — **it is what the defer pipeline spends its time
doing.**

## The measurement

`roman.sno`, mode-4 native binary, FIXED-WORK **N=2000**, RT_OPT=`-O2`, SCRIP `e88e77db`, output verified
**`check: 1102`**, `valgrind --tool=callgrind --separate-callers=2`. PROGRAM TOTALS **80,371,439 Ir**.
(Per-iteration cost solves to ~43,845 against the N=20000 run's 43,479 — within 1%, so the N=2000 shares
carry no meaningful startup distortion.)

| defer-rooted chain | share |
|---|---|
| `NV_GET_fn` ← `rt_defer_nv_read` | **19.35%** |
| `c_rt_defer_close` ← `rt_defer_run_all` | 9.59% |
| `rt_defer_run_all` | 6.95% |
| `__strcmp_avx2` ← `NV_GET_fn` | 5.91% |
| `rt_defer_get_pat_dtp` | 5.17% |
| `rt_dfx_push` ← `rt_defer_run_all` | 2.96% |
| `__strcmp_avx2` ← `rt_defer_run_all` | 2.96% |
| `__strncmp_avx2` ← `c_rt_defer_close` | 1.33% |
| **subtotal — pure defer** | **54.22%** |
| `NV_SET_fn` ← `rt_dcap_pump` | 2.50% |
| `rt_dcap_pump` ← `c_rt_dcap_end_ok_open` | 1.55% |
| **total including capture-pump** | **58.27%** |
| *our emitted code, for contrast* | *12.96%* |

`NV_GET_fn` is called **2,807,622 times** in the N=20000 run — **140 times per iteration** — for a program
whose pattern contains exactly one deferred variable.

## The mechanism, in five lines of source

```c
static DESCR_t rt_defer_nv_read(const char *name)
{
    extern int rt_udc_on(void);
    if (name && name[0] == '&' && rt_udc_on() && NV_CONST_ASSIGNED_fn(name)) return NV_KW_GET_fn(name);
    return NV_GET_fn(name ? name : "");
}
```

The deferred node carries **a string**, and every re-read resolves that string through the global name table —
hash plus `strcmp`. `&ANCHOR = 0` in `roman.sno` means the match is **unanchored**, so the pattern is retried
at every start position in the subject, and each retry re-reads `T` **by name**. The existing
`&user_defined_constants` fast path is the only escape and it is `&`-prefixed-keywords only, so it cannot
reach an ordinary variable like `T`.

⭐ **This is why the NV_\* memo returned 17% and not more.** The memo made each lookup cheaper (hash → `strcmp`,
and `__strcmp_avx2` under `NV_GET_fn` is now a visible 5.91% of the program in its own right). It did not
reduce the **140 lookups per iteration**. Making a call cheaper when the defect is the call *count* has a
ceiling, and we have hit it.

## ⛔ WHAT THIS SEAT IS NOT DOING

**Under the s256 delegate-only rule then in force:** no edit is proposed here and none was made. Two reasons this one is
emphatically not hq_P's to cure:

1. **The correctness question is hq_C's and it is genuinely open.** §7 of
   `REFERENCE-SPITBOL-BEAUTY-CONSTRUCTS.md`: deferral is what `*expr` **means**, and a bare variable is
   evaluated at construction — which argues `T` should not defer at all. But if a pattern assigns the variable
   mid-match (beauty's `NRETURN` idiom), SPITBOL matches the already-built pattern and we would not. Answers
   agree today (`check: 1102` both engines), so what we have is **conservative deferral, not a wrong answer**.
2. `T` here is **also the capture target** of `BREAK(',') . T`, so it genuinely varies within the match.
   Whatever the general rule turns out to be, this specific site is the hard case, not the easy one.

## The two cure directions, for whoever takes the row

- **Narrow, and it does not need the semantic question answered:** keep the deferral, kill the *by-name*
  resolution. Resolve `T` to its `vrblk`/slot **once** when the deferred node is built, and have
  `rt_defer_nv_read` follow a pointer instead of a string. This is SPITBOL's own discipline and it is worth
  most of the 25.3% that `NV_GET_fn` + its `strcmp` currently cost, with **no** change to what the program
  means.
- **Wide, and it does need the semantic question answered:** do not defer a bare `TT_VAR` at all
  (`lower_snobol4.c:1398`). Worth up to the full 54%, and **blocked on hq_C**.

⭐ The narrow direction is the better first row: it is a pure-performance change behind an unchanged answer,
which is exactly the kind of row this HQ is supposed to generate.
