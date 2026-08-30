# FINDING 2026-08-30 hq_C — `descr_identical` judged any string BEGINNING with NUL to be empty

**Tree:** SCRIP `85b877d4` (hq_P's strlen sweep) → cured `55b69790` · measured 2026-08-30, seat `hq_C`.
Found by reviewing hq_P's sweep at their explicit request ("I want your eyes on the boundary I drew").

## The claim

Lon's ruling — *"A NUL character is a valid string element"* — was swept through 13 on-demand `strlen`
sites and fixed at the constructor. **One site survived because it does not call `strlen`. It
open-codes the same assumption:**

```c
int an = (a.v == DT_SNUL) || (a.v == DT_S && (!a.s || !*a.s));
```

`!*a.s` asks *"is the first byte NUL"*, not *"is this value empty"*. Same defect, different spelling.

## Witness — scrip vs SPITBOL (`sbl -bf`), one program

| program | scrip (before) | oracle |
|---|---|---|
| `X = CHAR(0) 'abc'` · `SIZE(X)` | 4 | 4 |
| `IDENT(X,'')` | **SUCCEEDS** | differs |
| `Y = CHAR(0)` · `SIZE(Y)` | 1 | 1 |
| `IDENT(Y,'')` | **SUCCEEDS** | differs |
| `IDENT(X,Y)` | **SUCCEEDS** | differs |

⭐ The last row is the sharpest: **a 4-character value reported IDENTICAL to a 1-character one.** And
the run contradicts itself — `SIZE(X)` reads `.slen` and answers 4 while `IDENT` reads `.s[0]` and
answers "empty", in the same program, on the same descriptor.

## ⭐⭐ Why the sweep missed it — the generalizable part

hq_P swept **call sites of `strlen`**, which is the obvious and correct search, and it found 13. This
site was invisible to that search **because it implements strlen's assumption without calling
strlen**. `!*s` is the one-byte special case of "measure this as a C string".

**The rule: when you retire an ASSUMPTION, grepping for the FUNCTION that embodies it finds only the
places that were honest enough to call it.** The dangerous residue is the hand-inlined special cases —
`!*s`, `s[0] == 0`, `*s == '\0'` — which are the same premise written small enough to look like a
null-pointer check. This is a sibling of the WHEN YOU CHANGE A MECHANISM, GREP FOR PROSE THAT DESCRIBES
IT rule already in the pool, with the search target moved from prose to *idiom*.

## A second, LATENT inconsistency — recorded, not claimed

One line below, the two operands of a single comparison were measured under **different rules**:

```c
l1 = (a.slen > 0 && a.slen != 0xFFFFFFFF) ? a.slen : strlen(s1)   /* retired sentinel */
l2 = (b.slen != 0xFFFFFFFF)               ? b.slen : strlen(s2)   /* new rule */
```

so `descr_identical(a,b)` and `descr_identical(b,a)` could disagree — a non-commutative equality.
⚠️ **I could not reach it.** Every SNOBOL4 witness I built (zero-length captures at offset 0 and at
non-zero offsets, across two subjects, compared both ways) materializes before comparison and matches
the oracle exactly. **It is fixed for consistency, on argument, not on evidence** — stated that way
deliberately, because a defect claimed without a reproduction is how a false lead enters the record.

## Also confirmed while here, so nobody re-derives it

- **`xpass=2` is PRE-EXISTING**, not caused by this fix — verified by rebuilding the pre-fix `values.c`
  and re-running: the identical two names (`user_function_indirect_replace_2`,
  `user_function_eval_arbno_replace_branch_2`). hq_P's floor of `xpass=1` predates something else.
- **hq_P's boundary is drawn in the right place**: `strlen` is legitimate only where a genuine C string
  enters the system. The `DT_N` branch's `strcmp` at `values.c:23` is on that boundary — names are C
  strings — and is correct as it stands.
- **The cset carve-out is correctly left open.** `slen == 0xFFFFFFFF` is a type tag, so a cset has
  nowhere to carry a count, and `&ALPHABET` contains NUL. Naming it open rather than letting a sweep
  imply completeness is the right call; it needs a representation change, not a sweep.

## Verdict scope

Core value representation is reached by every frontend, so SHARED-NODE VERDICT SCOPE applies. Pristine:
SNOBOL4 m3 1672/0 · m4 1672/0 · icon 14/0 both · prolog 5/0 both · snocone 5/0 · rebus 4/0 · raku
722/0 REFUSED=2 of 724. `make test` rc=0.
