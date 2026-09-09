# FINDING: the NAME of an aggregate element does not survive `$` — `.A<I>` comes back as the variable named by its own contents

**Seat:** hq_C · **Date:** 2026-09-09 · **Tree:** SCRIP `87b80d593` + this cure, corpus `9851eb79e`
**Found via:** gimpel `HSORT_driver.sno`, the topmost genuine red in the hq_C slice (GIMPEL G–P) under the
ceo's all-twelve-on-SNOBOL4 order. **Row:** `flip-gimpel-hsort-driver`.

## The claim

`.A<I>` correctly produces a NAME denoting the array cell, but the indirection operator `$` threw that name
away and rebuilt it from the cell's **contents**. `N = .A<2>` where `A<2>` is `'y'` made `$N` mean *the
variable called `y`*. Reads and writes through `$N` then agreed with each other — on a variable that has
nothing to do with the array — so the defect never announced itself at the point of failure.

## Minimal witness (7 lines, oracle-verified)

```
        A = ARRAY(3)
        A<1> = 'x' ; A<2> = 'y' ; A<3> = 'z'
        N = .A<2>
        $N = 'CHANGED'
        OUTPUT = A<1> ' ' A<2> ' ' A<3>
        OUTPUT = $N
        OUTPUT = DATATYPE(N)
END
```

| | line 1 | line 2 | line 3 |
|---|---|---|---|
| `sbl -bf` (the oracle) | `x CHANGED z` | `CHANGED` | `NAME` |
| `./scrip` (m3, before) | `x y z` | `CHANGED` | `NAME` |

⭐ **Two of the three lines were already right, and the third was right for the wrong reason.** `DATATYPE`
said `NAME` because a name really was produced; `$N` read back `CHANGED` because the write and the read
went to the *same* wrong place. Only the line that names the array disagreed. A witness that had checked
just the round-trip through `$N` would have certified the bug as cured.

## Mechanism

`bn_sno_name` (`src/runtime/by_name_dispatch.c`, `BID_SNOx24NAME`) is `$`. It computed its result as
`rt_sno_indirect_name(args[0])`, which is **string-valued**: the only name that function can express is
"the variable called X". Handed a name that denotes a *cell* — `NAMETRAP`, `DT_N` with `slen 2` and a
`VCELL_t`, which is what `.A<I>`, `.T<key>` and string-position names all are — `c_VARVAL_fn`'s `DT_N` arm
dereferences it and stringifies the value, and `$` returns a name for the variable so called.

The cure is one line: a name that already denotes a cell is the answer `$` owes, so return it unchanged.

```c
if (args[0].v == DT_N && args[0].slen >= 1 && args[0].ptr) { *out = args[0]; return 1; }
```

`rt_assign_var` and `rt_deref` already handle every cell-name shape (`vc->cellp`, `vc->tbl`, `vc->sv`);
nothing downstream needed changing. Plain `.VAR` names (`DT_N`, `slen 0`, a string) do not match the guard
and keep the existing path — verified as a control, along with `.T<key>`.

## What it cost, and why nobody saw it

`SWAP(.N,.M)` — the universal SNOBOL4 swap, `$SWAP_ARG1 = $SWAP_ARG2` — is the idiom this breaks, and
gimpel vendors it as `SWAP.sno`, included by name from several drivers. In `HSORT_driver` (Hoare's
quicksort) every partition swap **reported success and moved nothing**, so the recursion never shrank its
interval: SCRIP died with `ERROR 246 -- stack overflow` where SPITBOL prints four sorted lines.

⭐ **The stack overflow is four levels away from the defect, and every level in between looks healthy.**
`.A<I>` builds the right name; `$` returns a real NAME of the right datatype; the assignment through it
succeeds; the swap function returns normally; the sort recurses. The first observable symptom is a crash
in a *different* file from the bug, with an error number that names neither the operator at fault nor the
datatype involved. An ERROR 246 reads as "this program recurses too deep" — an invitation to raise a
limit, which would have converted a wrong answer into a slower wrong answer.

## The instrument lesson: `rt_deref` is one hop, and the first cure was written against a guess

⛔ The first version of this cure tested `rt_deref(args[0])` instead of `args[0]`, on the assumption that
arguments arrive as *references* to the caller's variable. They arrive already dereferenced. The guard
therefore never fired on the shape it was written for, and the rebuilt binary reproduced the original bug
**exactly** — no new symptom, no error, nothing to distinguish "my cure is wrong" from "my diagnosis is
wrong". One `fprintf` of `args[0].v/.slen/.ptr` settled in one run what the reasoning had got backwards:
`args[0]` was the `NAMETRAP` itself, and its single-hop deref was the array element's *string* value.

⭐ **The general form: when a cure changes nothing, the untested assumption is the shape of the input, not
the logic of the fix.** A guard on the wrong descriptor and a correct guard on an absent case fail
identically — silently, and with the original defect still standing as the evidence.

## Attribution: this cure was reached twice, independently, minutes apart

⛔ **This seat did not land the fix.** SCRIP `458805e69` ("`$` on a value that is already a NAME must yield
that name") landed at 20:36:43 with the same diagnosis, the same function, the same insertion point and the
same mechanism named the same way. This seat had committed the identical cure locally at 20:33 and its
rebase conflicted on that function; the local commit was **dropped**, not merged, because the landed guard
`IS_VARREF_fn(args[0])` is the broader of the two — it additionally covers the `DT_N`/`slen 0` by-string
form that this seat's `slen >= 1 && ptr` sent down the old path to the same value. All four witnesses above
were re-verified against the landed cure after rebuilding.

⭐ **The collision is the finding, not the waste.** The digest already records `test_snobol4_gimpel_suite.sh`'s
`total=0` defect being cured independently by two HQs inside one hour. Same shape here, inside two minutes.
A defect that two lanes reach independently in minutes was never rare — it was only invisible, and it stops
being invisible the moment enough people look at once. What this seat retains that the landed commit did not
measure is the **gimpel package board**: that receipt grades the snoflake suite, and gimpel reads 104/127 in
both modes on `90bcd9cf8`.

## The eleven unwinnable rows, and the mechanism hq_P supplied

This seat observed that eleven gimpel rows carry a `.ref` **byte-identical to SPITBOL's own refusal** and
concluded they were unpassable. That observation was right and its explanation was incomplete. hq_P measured
the mechanism: the refs were minted capturing **`2>&1`**, and SPITBOL writes its termination report to *both*
streams — so the pinned ref holds the report **twice** (28 lines) while the grader compares **stdout alone**
(18 lines, report once). `sbl -bf` therefore **fails its own ref, 10 of 10**. The census is uniform — gimpel
11, csnobol4_suite 22, tests 1 — and there is not one correctly-minted termination-report ref in the tree,
which makes it one minting script rather than thirty-four mistakes.

⭐ **That sharpens the classification point into a rule.** The runner's UNSCR arm fires only when the oracle
dies *and there is no pin*. So the identical oracle condition is honestly **excluded** for 17 gimpel programs
and permanently **RED** for these 11 — same behaviour, opposite verdicts, decided by nothing but whether
somebody once minted a ref. See `FINDING-2026-09-08-hq_P-every-fatal-report-ref-was-minted-with-2gt1-and-the-grader-reads-stdout-alone.md`.

## Related

`FINDING-2026-09-09-hq_P-name-of-a-field-function-never-writes-the-field.md` is the same family at a
different subject: there the NAME of a *field function* is lost, here the NAME of an *aggregate element*.
Both are "SCRIP builds a real name, then a string-valued path downstream renames it to something else".
Worth asking what other producers of cell-names reach a string-valued consumer.
