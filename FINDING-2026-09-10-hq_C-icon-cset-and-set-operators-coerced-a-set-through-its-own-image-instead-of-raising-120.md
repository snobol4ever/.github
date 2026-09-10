# FINDING — the last link in a coercion chain was `VARVAL_fn`, so a set became the characters of its own image

**hq_C, 2026-09-10.** Measured against `/home/resources/icon-master/bin/icon` (Icon v9.5.25a). Landed SCRIP
`e4f88be6e`, parent `e6390409d`, corpus `5795c1cd8`. Row `icon-jcon-errors-…` (CEO-483/CEO-497), third divergence.

## The claim

`set([]) ++ 'a'` returned the cset `'(),01ABELTa'` and raised nothing. icont raises **120 "two csets or two sets
expected"** with `&errorvalue set_1(0)`.

Those characters are not arbitrary: they are the distinct characters of the string **`"set_1(0)"`**. The `++`/`--`/
`**` arm of `rt_num_arith_impl` tries the two-sets branch, then walks a chain of coercions — cset, string, integer,
real — ending in

```c
else { as = VARVAL_fn(a); if (!as) as = ""; }
```

and `VARVAL_fn` on a set, list or table hands back its **image**. So the operand that could not be converted was
converted anyway, into the text of its own printed form. Seven shapes reached it: `set++cset`, `cset++set`,
`cset++list`, `list**str`, `null++cset`, `table++cset`, `set++str`.

⭐ **This is the third time this row has produced the same shape, and it is worth naming as a class rather than a
bug: a helper whose return type cannot express failure supplies a plausible value instead.** `core_icn_to_int_check`
returned `int64` and supplied `0` (`98d75ebe0`); `procval_name` supplied the string itself, so the 106 check for a
nameless callee could never see a string (`0bf85a7d1`); `VARVAL_fn` returns `const char *` and supplies an image.
**The wrongness of the value is what determines how long the bug survives, not the frequency of the path** — a wrong
cset looks far more like a cset than `0` looks like an answer, which is why this one outlived the other two.

## The rule, pinned by the oracle rather than by reading the book

Twelve shapes, `&error := -1`, each read back:

| | icont | SCRIP before | after |
|---|---|---|---|
| `'ab' ++ 'cd'` | `'abcd'` | `'abcd'` | `'abcd'` |
| `"ab" ++ "cd"` | `'abcd'` | `'abcd'` | `'abcd'` |
| `1 ++ 2` | `'12'` | `'12'` | `'12'` |
| `1.5 ++ 'a'` | `'.15a'` | `'.15a'` | `'.15a'` |
| `set([1]) ++ set([2])` | `set_3(2)` | `set_3(2)` | `set_3(2)` |
| `set([]) ++ 'a'` | **120** | `'(),01ABELTa'` | **120** |
| `'a' ++ set([])` | **120** | `'(),01ABELTa'` | **120** |
| `&cset ++ []` | **120** | `&cset` | **120** |
| `[] ** "abc"` | **120** | `''` | **120** |
| `&null ++ 'a'` | **120** | `'a'` | **120** |
| `table() ++ 'a'` | **120** | `'(),01ABELTa'` | **120** |
| `set([]) ++ "a"` | **120** | `'(),01ABELTa'` | **120** |

**Both sets → a set; otherwise both operands must be cset-convertible, and strings, integers and reals all are.**
`&null`, lists and tables never are. `&errorvalue` names the **first** operand that fails, which is what icont
reports.

⛔ **The oracle's own output is easy to misread here, and I misread it once.** Under `&error := -1` a raise converts
to failure, so a call whose *argument* raised is never made and prints **nothing at all**. My first probe wrapped
each case in a `show(tag, v)` procedure and the oracle printed five lines out of twelve — which reads as "the oracle
crashed after five" and is really "seven arguments raised". The same run of SCRIP printed **zero** lines, which
reads as a catastrophic divergence and was in fact **a defect in my own witness**, not in either implementation.
Take the expression out of the argument position before concluding anything.

## The cure

```c
static int icn_cset_operand_ok(DESCR_t v) {
    return IS_CSET_fn(v) || v.v == DT_S || v.v == DT_I || v.v == DT_R;
}
```

asked for both operands after the two-sets branch, raising `core_icn_error(120, …)` on the first failure.
Unconditional, and **not** a language branch: only `icon_parse.c` produces `TT_CSET_UNION`/`DIFF`/`INTER`, and
Raku's `"++"` is `OP_INC` in an unrelated lowering, so these three ops are Icon's alone. No new global.

## Measurements

`errors.icn` m3: record-line axis **37 → 40** same, **9 → 6** diff; `&errornumber` axis **19 → 22**; whole-record
blocks **3 → 4**. Locals, globals, set elements under `every !s ++ 'z'`, and generator resumption are byte-identical
to the oracle in both modes. **The program stays red on the class-F SEGV; the row stays open.**

**Control arms**, SCRIP `e6390409d` + this change, corpus `5795c1cd8`: SNOBOL4 m3 PASS=1893 FAIL=0 · m4 PASS=1893
FAIL=0 SKIP=0 · ast 28/28 · MISSING=0. Icon master per-entry identity **GATE PASS**, regressions 0 / vanished 0 /
astdrift 0 over 1669 pairs. jcon PASS=69 both modes, non-PASS set unchanged. `make test` **rc=0 over 133 arms, zero
reds**.

## Two refusals that are not reds, both met in one sitting

⛔ **The SNOBOL4 arm first returned rc=2 — killed by SIGTERM.** Another seat's box-wide
`pkill -f corpus_suite_harness.py` kills *every* seat's board. The gate says so itself, in its own refusal text, and
tells you to re-run; re-run alone it was green. **A refusal is could-not-measure. Never diagnose the compiler from
one.**

⛔ **`pull --rebase` before push moved this commit twenty-one commits off the tree I had just measured — and I had
pulled first specifically to prevent that.** SCRIP was genuinely unchanged at the moment I committed; the window
between a pull and a push is simply never empty on a thirteen-seat box. Several of the twenty-one were cset work
(`a literal cset registers once`, `cset membership is a bit test`) that touches this very arm, so this was not a
formality: every witness and every arm was re-run on the real parent, and all held. **The lesson is not "pull
first" — I did. It is that a receipt must name the tree it measured, and the arms must be re-run after the push
tells you what your parent actually became.**
