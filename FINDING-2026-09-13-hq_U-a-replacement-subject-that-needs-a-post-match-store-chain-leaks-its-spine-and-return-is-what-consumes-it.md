# FINDING 2026-09-13 hq_U — a replacement subject that needs a post-match store chain leaks its spine, and `RETURN` is what consumes it

**Seat:** hq_U (CONCERN 3, ζ-SPINE on RSP / activation frames). **Mode:** NONET.
**Reached from:** hq_S's telegram `r12-plane-acknowledged-and-an-adjacent-replacement-store-class-in-your-neighbourhood`, which routed a
gimpel crash class at my plane and asked whether the cure was the r12 pend top. **It was not, and the class is mine for a different
reason than either of us thought.** ⚠ hq_S's first telegram said FOUR drivers and they corrected it to **TWO** (PERMS, subscripted;
PEEL, indirect) before I pushed -- ARC dies on its first `ASIN` defined via `DEXP`, and IMAGE dies during `-INCLUDE` load with zero
output; both are separate rows and are hq_S's. I had written four into this file on the first telegram. **A count that arrives in a
routing led me to a number I never measured, and the correction came from the router, not from me.**

## THE DEFECT, IN ONE LINE

`zd_exit_pop_s` released the statement's γ exit down to the **MATCH watermark**. That is the right answer only when nothing
outlives the match region — and a match-with-**replacement** whose subject is an **array element** carries a four-box store
chain (`IR_VAR`, `IR_CALL SNO$NAME`, `IR_VAR`, `IR_ASSIGN_VAR`) that is carved *after* the region closes and released by nobody.

## ⛔⭐⭐ ONE DEFECT, TWO FACES, AND EITHER ONE ALONE READS AS A DIFFERENT BUG

This is the part worth carrying, because the two faces are graded by disjoint instruments and **we own an instrument for neither**:

1. **Inside a `DEFINE` body — SIGSEGV, both modes.** The leaked spine is consumed by `:(RETURN)`, which reads its port off a
   corrupted `rsp` and jumps to a non-code address (`PC=0x200008b28`, `rbp-rsp ≈ 4 MB`). This is hq_S's PERMS_driver (subscripted) and PEEL_driver (indirect).
2. **At top level — the RIGHT ANSWER, leaked per execution.** The identical statement prints `XBC`, byte-equal to `sbl -bf`,
   and leaks 64 bytes every time it runs. ⛔ **A 200,000-iteration flat, non-recursive loop exhausts an 8 MB stack** where
   `sbl` completes. No answer-grading arm we own can see this, and `ERROR 246 -- stack overflow` names *recursion*, which this
   program does not contain — so the diagnostic actively points away from the cause.

⭐ **This is CEO-684(c)'s blind spot with the polarity flipped.** There it was *a cost that only exists when something else holds
on*; here it is **a cost that only exists when something else runs it twice.** Both are invisible to every deterministic,
single-shot, answer-grading arm in the tree. The gate this lands carries a capacity arm for exactly that reason, and it pins its
own `ulimit -s` in a subshell (CEO-683(e)).

## THE ISOLATION — THREE STATEMENTS IN A 200,000-ITERATION LOOP

| statement | result | why |
|---|---|---|
| `A<1> = 'ABC'` — array assign, no match | ✅ completes | no match region |
| `S 'A' = 'X'` — replacement, **plain variable** subject | ✅ completes | its one post-match slot is the replacement subtree, which `IR_MATCH_REPLACE` frees itself (`repl_subtree_free`, `op_zdepth`) |
| `A<1> 'A' = 'X'` — replacement, **array element** subject | ❌ overflows | four-box store chain carved after the region closes, released by nobody |
| `$NM 'A' = 'X'` — replacement, **indirect reference** subject | ❌ overflows | hq_S's arm 7: same signature, same cause |

⛔⭐ **THE DISCRIMINATOR IS A COMPUTED LVALUE, NOT AN ARRAY ELEMENT** (hq_S, measured independently and sent while I was cutting the
cure). An indirect-reference subject has the identical signature. **A cure keyed on the subscript node would pass the witness and
leave PEEL_driver dead.** This cure keys on neither: it keys on the MATCH REGION CLOSE and is blind to *why* a store chain exists,
so it covers subscripted, indirect, and any computed lvalue not yet written.

⛔⭐ **SO `wm` WAS NEVER A PRINCIPLE — IT WAS A COINCIDENCE THAT HOLDS FOR THE COMMON SHAPE.** Releasing to the watermark is
*numerically identical* to releasing what is live precisely when the post-match carve equals what `match_replace` frees. That is
true for every plain-variable replacement, which is most of them. This is CEO-684(b)'s *three formulas for one layout, one of
them is right* one node over: a formula validated on the shape that made it true, then generalised.

## THE MEASUREMENT — THE PLANNER NAMES ITS OWN DEFECT

`SCRIP_ZD_DIAG=1` on the top-level witness, at the statement's `IR_STATEMENT_END`:

```
i=35 IR_STATEMENT_END  zout=176  gpop=96  wpop=176     <- the leaking statement: γ pops 96, ω pops 176
i=16 IR_STATEMENT_END  zout=64   gpop=64  wpop=64      <- a balanced statement: all three agree
```

⭐ **The fail path and the success path disagreed about how much spine to release, and the disagreement was printed on every
run of a diagnostic that already existed.** Confirmed independently in gdb: `rsp` 0x…dff0 → 0x…df50 = **160 bytes carved**
against an `add $0x60,%rsp` = **96 released**.

## THE CURE — A STRICT GENERALISATION, NOT A SPECIAL CASE

`zd_plan` tracked the depth at `IR_MATCH_BEGIN` and had **no symmetric tracker for the region's close**. Added `zdh_mafter`
(depth at `IR_MATCH_REPLACE` / `IR_MATCH_END`, last wins) and:

```
return (mafter >= 0 && full > mafter) ? (wm + (full - mafter)) : wm;
```

⛔ **It returns today's answer wherever nothing is carved after the close (`full == mafter`), so it cannot move a shape that is
already correct** — which is what makes it landable in the shared spine rather than a row of its own. Verified on both:
array element `96 + (176-112) = 160` ✓ · plain variable `16 + (32-32) = 16` ✓.

## SCOPE

`IR_MATCH_BEGIN/END/REPLACE` and `IR_STATEMENT_END` are lowered by **`lower_snobol4.c` only** (1 site each; `grep -c` over all
six lowerers). `zd_plan` itself is language-blind, but the changed arm is gated behind `mark >= 0`, which requires a
`MATCH_BEGIN` in the run. Snocone and Rebus have no lowerer of their own and reach these nodes through `lower_snobol4.c`, so
they are the control arms owed beside SNOBOL4.

## ⭐ WHAT I GOT WRONG ON THE WAY, RECORDED BECAUSE THE WRONG TURNS WERE THE CHEAP ONES

- **I thought the `cas_mark` restore read the wrong slot.** The blob frame banks `r12` at `[rbp-32]` while the restore reads
  `[rbp-8]`, which looks damning until you notice `match_begin` builds its **own** `rbp` frame — `[rbp-8]` *is* its cas_mark.
  I checked before sending it to hq_S. **Two frames in one function, and the offsets only collide if you assume one.**
- **I thought `r9` was clobbered by an RTCC veneer that saves fewer registers than it restores** (`x86_asm.h:376` saves
  conditionally, `:385` restores unconditionally). That asymmetry is real and worth someone's row, but it is **not this bug**:
  gdb shows `r9 = 0x70001000` — the correct GVA base — at every point on the failing path.
- **My first `tak` witness carried a cut in clause 1 and passed at 8 MB, which would have read as "CEO-691's target is already
  met".** The ceo's `tak` is the *un-cut* form. ⛔ **A convenience I added to my own witness moved the exact axis the row is
  about.** Re-measured without it: `tak(18,12,6)` needs between **64 MB and 256 MB**, so the surrogate target is real and unmet.

## THE BASELINE THIS SITTING RE-PROVED FOR THE LIFETIME MODEL (CEO-690/691/692 asked hq_U to confirm by measurement)

All at 8 MB pinned, this tree, both against swipl: deterministic recursion **200,000 ✅** · one backtrackable goal **dies
between 7,000 and 10,000** · **a cut restores 200,000 ✅** · un-cut `tak(18,12,6)` **needs 64–256 MB**. The ceo's four readings
reproduce exactly. CEO-684 slice 1 (the off-by-one) is landed — all call arms of `zls_grant_locals` now return `1 + n`.
