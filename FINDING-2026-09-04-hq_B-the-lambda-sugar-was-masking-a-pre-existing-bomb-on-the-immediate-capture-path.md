# FINDING 2026-09-04 hq_B — reverting the lambda sugar cured the `.` path and UNMASKED a pre-existing bomb on the `$` path

**Seat:** hq_B (HQ-BEAUTIFY) · **Mode:** QUARTET · **Tree:** SCRIP `89eb03ef6` (the cure) · corpus `cfa277fa9`
**Instrument:** hand witnesses against `sbl -bf` (the ref, Lon 2026-09-04 18:37), plus a clean worktree built at `04d1b9cd2~1`.

## 1. What was ruled, and what the cure is

Lon, 2026-09-04 18:37: **"SPITBOL's answer is the ref."** `p = LEN(1) . *(n = n + 1)` must FAIL the match as
SPITBOL does; the `04d1b9cd2` lambda sugar made it succeed. The cure reverts that sugar's two dispatch
sites, keeping the genuine `LAMBDA(expr)` pattern primitive (a separate route via `sno_lambda_kind`) and
another seat's later `TT_IDX` work on the same lines.

Measured, three-way agreement on `user_function_len_defer_branch_6`, **both modes**:

```
SCRIP m3   before / nomatch n=1
SCRIP m4   before / nomatch n=1
sbl -bf    before / nomatch n=1        <- the ref
ALL.ref    before / nomatch n=1        <- the pinned oracle-cut ref
```

⭐ Note SPITBOL **evaluates and then fails** — `n=1`, not `n=` — so the cure could not be "stop evaluating
the target." The pre-sugar path already does exactly this: the synthetic `EXPR$` procedure is called (the
side effect happens), returns a VALUE not a NAME, and `strict && !by_name` sets `rc=1` so the match fails
at END. The sugar's `void_yield` arm short-circuited precisely that refusal.

## 2. The divergence surface, before and after

Measured against `sbl -bf` on seven forms. The sugar diverged on exactly the class it claimed
(assignment / arithmetic / concatenation), for **both** `.` and `$`; bare variables were never involved.

| form | before (sugar) | after (cure) | sbl |
|---|---|---|---|
| `. *(n = n + 1)` | MATCH n=1 | **NOMATCH n=1** | NOMATCH n=1 |
| `. *(n + 1)` | MATCH | **NOMATCH** | NOMATCH |
| `. *("x" "y")` | MATCH | **NOMATCH** | NOMATCH |
| `$ *(n = n + 1)` | MATCH n=1 | ⛔ BOMB | NOMATCH n=1 |
| `$ *(n + 1)` | MATCH | ⛔ BOMB | NOMATCH |
| `. *v`, `$ *v` | MATCH | MATCH | MATCH |

## 3. ⛔ The unmasked bomb, and the proof it is not mine

After the cure, the **immediate** (`$`) form of the same class aborts rather than failing the match:

```
[IDX] BOMB rt_assign_var: lvalue is not a variable (dtype=3) — string/record subscript
assignment is the tvsubs rung (GOAL-IR-IMMUTABLE-EMIT IDX-UNIFY)
```

**This is pre-existing, not a regression.** Proved by building a clean worktree at `04d1b9cd2~1`
(`908b3cbb3`, the sugar's own parent) and running the same witness: byte-identical bomb. The sugar had
been *masking* it — routing that class into `IR_MATCH_LAMBDA` before it could reach `rt_assign_var`.

⛔ **And the check that makes that claim trustworthy**, because this repo convicted exactly this error
tonight: `ldd` was used to confirm each binary resolves its **own** `libscrip_rt.so` —
`<worktree>/out/libscrip_rt.so` vs `SCRIP/out/libscrip_rt.so`. `scrip` is a thin driver and the whole
engine lives in that `.so`; a copied executable resolves the *other* tree's engine through the unhashed
symlink, so an A/B done by copying the binary compares a build with itself (hq_C retracted a FINDING on
that exact mechanism, `.github c6afe690`). The two RT hashes here are legitimately identical — my cure
reverts `pattern_match.c` to the parent's own content — which is why resolving the path mattered rather
than comparing hashes.

## 4. Scope, honestly stated

- The whole SNOBOL4 master contains **exactly one** entry using this construct — the ruled one. The
  revert therefore moves one corpus entry, and it is the entry that had to move.
- The `$` bomb has **no corpus dependents at all**; it is reachable only by a program written by hand.
  It is a real defect and it is **not** what Lon ruled on, so it is filed rather than folded into this
  cure — a row, not a silent extra fix.

## 5. The lesson

⭐ **A cure premised on "this class is useless today" needs the oracle consulted about the class, not
about the code.** The sugar's own commit message is explicit and honest: the fall-through was "a
guaranteed match failure for that class today," so it gave the class new meaning. That premise was
correct about SCRIP and wrong about SPITBOL — the guaranteed match failure *is* SPITBOL's answer. Under
RULES.md § Semantics a construct SPITBOL accepts is graded by SPITBOL's answer, so "nothing useful
happens here" was never ours to redefine.

⭐ **And a masked defect is a second cost of the same decision.** Routing a class away from a crashing
path makes the crash unobservable without fixing it; the next person to restore correct semantics
inherits a bomb with no history attached. Reverting is how it was found, which is an argument for
grading a "this can't matter" change against the oracle *before* it lands, not after.

## 6. Control arms (SHARED-NODE VERDICT SCOPE)

Graded before the push, on the tree carrying the cure:

```
SNOBOL4 master   m3 PASS=1791 FAIL=0 · m4 PASS=1791 FAIL=0 SKIP=0 MISSING=0   ✅ GATE OK
Icon master      entries=754 · m3 PASS=599 · m4 PASS=599/601 · ast 153/153    ✅ watermarks held
porter.sno       matches porter.ref exactly, 23531 lines (a real LAMBDA(expr) user)
```

⭐ **The m4 gate that had been blocking every SNOBOL4 landing is green.** The ruled entry is a real
graded entry, not an xfail — checked against `ALL.xfail` before claiming the green, because a board
that goes green by acquiring a marker is not the same event as a board that goes green by a cure.

⛔ Icon's watermark moved 596 → 599 during this work. That is **other seats' commits**, not this one,
and is deliberately **not** re-pinned here — the board's own instruction is to re-pin in the commit that
earned it.
