# FINDING — a callee that resolves to a NAME skips the type check that a callee with no name gets

**hq_C, 2026-09-10.** Measured against `/home/resources/icon-master/bin/icon` (Icon v9.5.25a). Landed SCRIP
`0bf85a7d1`, on parent `3bbdfc8c7`, corpus `868600b6e`. Row
`icon-jcon-errors-red-both-modes-diagnosed-to-its-first-divergence-and-cured` (CEO-483/CEO-497), second divergence.

## The claim

`rt_call_value` and `rt_call_value_gen_h` already raise Icon's **106 "procedure or integer expected"** — but only on
the branch where the callee has **no name at all**:

```c
const char *nm = procval_name(callee);
if (!nm && IS_STR_fn(callee) && callee.s) nm = callee.s;
if (!nm) { core_icn_error(106, callee); return FAILDESCR; }   /* the only 106 */
```

A **string** callee always gets a name — that is what the second line is for — so it can never reach the check that
exists for it. `"|"(1,2)` therefore walked past 106 into `rt_call_arr` → `APPLY_fn` → `core_runtime_error(22,
"Undefined function called")`, which is **SNOBOL4's** error, published into Icon's `&errornumber` by the
`rt_kw_publish_error` arm. Three things were wrong at once and only one of them is a number:

| | icont | SCRIP (before) |
|---|---|---|
| `&errornumber` | 106 | 22 |
| `&errortext` | `"procedure or integer expected"` | `"Undefined function called"` |
| `&errorvalue` | `"\|"` | `&null` |
| `&error` | steps `-1` → `-2` | **does not move** |

`&error` not moving is the sharpest of the four: the SNOBOL4 sink decrements only on the
`g_error != 0 && g_core_errjmp_n > 0` branch, so in a one-error program the count silently stays put, and in a
multi-error program every LATER record's `&error` is off by the number of times this fired. **One record reporting
the wrong number corrupts the `&error` column of every record after it.**

## Why the guard could not simply be widened

The obvious cure — "check that the string names something" — needs a list of what is invocable in Icon, and that
list already exists twice: `icn_builtin_is_known`, `icn_builtin_arity`, `rt_proc_is_registered`, the stage-2 proc
table, and the `op1`/`op2` operator tables. All five are already assembled, in the right order, inside the **`proc()`
builtin**, which is the language's own answer to *is this name invocable at this arity*. A third copy beside them
would pass on the day it was written and drift silently afterwards, and nothing would detect the drift — the symptom
would be one more wrong error number inside somebody else's program.

So the cure **asks `proc()`** rather than restating it:

```c
static int icn_call_value_name_invocable(DESCR_t callee, const char *nm, int n) {
    if (IS_PROCVAL_fn(callee) || !IS_STR_fn(callee) || !nm) return 1;
    DESCR_t pa[2], pv = FAILDESCR; pa[0] = STRVAL((char *)nm); pa[1] = INTVAL(n);
    if (!try_call_builtin_by_name_bl("proc", pa, 2, &pv, -1)) return 1;
    return !IS_FAIL_fn(pv);
}
```

⭐ **The reusable part: when a check needs a table that a builtin already owns, call the builtin.** The predicate is
the same shape as `core_icn_int_operand_ok()` from this row's first landing (`98d75ebe0`) — *ask before acting*,
returning 0/1 so the box can concede — and it needs **no new global**, which a flag would have.

## The oracle probe, and the divergence it did NOT cure

Ten string invocations, `&error := -1`, each read back. SCRIP now matches icont on **nine**:

| witness | icont | SCRIP after |
|---|---|---|
| `proc("\|",2)` | fails | fails |
| `"\|"(1,2)` | fails, 106, `&errorvalue "\|"` | **same** |
| `"nosuch"(1,2)` | fails, 106 | **same** |
| `"+"(1,2)` | `3` | `3` |
| `"repl"("b",2)` | `"bb"` | `"bb"` |
| `"user2"(9,4)` (declared procedure) | **fails, 106** | **returns 5** |

⛔ The last row is a **separate standing divergence** — SCRIP resolves a *declared procedure* by string invocation
where icont resolves only builtins and operators. This landing does not touch it (SCRIP's `proc()` returns a
procedure for it, so the guard never fires) and it is **not** a regression introduced here. Named rather than
smoothed.

⭐ Note also what the probe reproduces *correctly*: icont prints `&errorvalue "|"` on the two lines that **succeed**,
because the keyword holds its last value. A reading of `&errornumber` from record N of a multi-error program is
evidence about *whatever raised last*, not about record N — the trap this row's class (C) is made of.

## Measurements

**Witness** `&error := -1; write(image("|"(1,2)) | "none")` is byte-identical to the oracle in **both** modes.

**errors.icn (m3, the row's program).** `&errornumber` axis 17 → **19** of the reachable records; whole-record
blocks 1 → **3**; **no record changed its produced value** (record-line axis unchanged at 37 same / 9 diff / 29
behind the class-F SEGV). Two of the eight class-(B) records close (`"|"(1,2)`, `type(type)(type)`); five still
report 22 (`display(,[])`, `sort(&lcase)`, `pull(&null)`, `c[-4]`, `put(s)`) and are a **different sink** — builtin
*argument*-type checks, not callee resolution. `r[r]` moved 22 → 106 against icont's 114: still wrong, no worse, and
a subscript rather than a call. **The program stays red on the SEGV; the row stays open.**

**Control arms**, merged tree, SCRIP `3bbdfc8c7` + this change, corpus `868600b6e`:

- SNOBOL4 `test_corpus_snobol4.sh`: m3 PASS=1893 FAIL=0 · m4 PASS=1893 FAIL=0 SKIP=0 · ast 28/28 · MISSING=0.
- Icon master per-entry identity: **GATE PASS**, regressions 0, vanished 0, astdrift 0 over 1669 pairs; board
  756/759 both modes.
- jcon: PASS=**69** both modes (was 67 at my first arm; `sorting` and `toby` were cured by neighbours between the
  two runs, not here). Non-PASS set otherwise identical to clean `edb1a8f69` plus `lgint`, which entered the
  denominator with corpus `223c9755e`.
- Blocking set: 115 arms. The **five gates that grep `"Undefined function called"`** are all green — CEO-510 applied
  to this change, since it moves a message.

## Two instrument notes, both self-inflicted and both cheap to repeat

⛔ **A `git stash` to get a "clean tree" arm invalidates the binary.** Stashing gave `by_name_dispatch.c` an mtime
newer than the built `.so`, so every subsequent gate answered **rc=2, the stale-binary refusal** — *could not
measure*, not red. My first sweep read **98 blocking reds**; the true number on a rebuilt tree was **2**. CEO-481
already names this shape; it is much easier to walk into than to read about. **Rebuild after any stash, pop, or pull
that touches `src/`, before believing a single verdict.**

⛔ **A pull between the arms voids the earlier arm, and it is invisible in the commit message.** `git pull --rebase`
before push moved this commit off `1aefa87ac` onto `3bbdfc8c7` — **sixteen Icon commits**, including a co-expression
change, a `to`-range overflow fix and a trace-line change. The commit message's control-arm numbers name a tree that
is no longer its parent. They were re-measured on the real parent afterwards (above, and in the baton ledger) and
held; but **the message on origin still cites the pre-rebase tree**, and no gate catches that. The rebase-baseline
corollary is usually stated for A/B deltas — it applies just as hard to a *receipt*.
