# FINDING 2026-09-10 hq_I — the BID generator refuses to run, so builtin ids are frozen, while emitted code bakes and trusts them

MEASURED on SCRIP `edb1a8f69` (+ the ^/copy cure in the working tree), 2026-09-10 08:3x CDT, while adding one
internal builtin name for the Icon `^` refresh row. Nothing here is inferred from reading the generator; every
claim below was produced by running it against a scratch copy.

## What I set out to do, and what stopped me

`scripts/gen_builtin_ids.py` is the sanctioned generator for `src/runtime/builtin_ids.h`, whose header says
`GENERATED ... DO NOT EDIT BY HAND`. I needed one new builtin name (`ICN_REFRESH`), so the obvious move was
to add the arm and re-run the generator.

**It refuses.** Run against a scratch copy of `by_name_dispatch.c`:

    $ python3 scripts/gen_builtin_ids.py $S/by_name_dispatch.c ; echo rc=$?
    ERROR: no !strcmp(fn,"...") sites found
    rc=1

and it writes no header at all — the scratch directory gets no `builtin_ids.h`.

## Why, exactly

`FUNC_RE = ^int try_call_builtin_by_name\(` matches **the one-line forwarder**, not the real body:

    4921: int try_call_builtin_by_name(const char *fn, ...) { return try_call_builtin_by_name_bl(fn, args, nargs, out, -1); }
    4946: int try_call_builtin_by_name_bl(const char *fn, DESCR_t *args, int nargs, DESCR_t *out, int bidlen)

`find_func_span` then scans forward for the first line starting with `}` and harvests that span, which holds
none of the file's 178 live `!strcmp(fn,` sites. The generator predates the `_bl` split and never learned about
it. ⭐ The instrument is not broken in the dangerous direction: it fails CLOSED, refusing with a message,
rather than emitting a short header.

## The correction I owe my own first reading

My first reading of this was that re-running the generator would **silently renumber** every BID. That was
wrong in the direction that matters, and I only found out by running it. It cannot renumber, because it cannot
run. The renumber hazard is real as a MECHANISM but currently unreachable, and the difference between
"silently corrupts" and "refuses with rc=1" is the whole risk assessment. Measuring beat reasoning here.

## Why the mechanism still deserves a banner

BIDs are **baked into emitted code** and **trusted on the way back in**:

    src/templates/bb/bb_call.cpp:445     s += x86("mov32", "ecx", bid_bake_of(fn));
    src/templates/bb/bb_call_fn.cpp:62   s += x86("mov32", "ecx", bid_bake_of(fn));
    src/runtime/by_name_dispatch.c:4978  const int _bid = (bidlen >= 0) ? (int)(bidlen & 0xFFFF) : bid_of(fn, (unsigned)_fnlen);

`bid_bake_of` packs `(namelen << 16) | bid` into an immediate in the `.s`. Line 4978 takes the baked value at
face value and never revalidates it against `fn`. So a `.s` artifact baked under one numbering, linked against
a `libscrip_rt.so` built under another, dispatches **a different builtin** with no diagnostic — the exact shape
this digest already records for globals only emitted code reads.

⛔ **Therefore: whoever repairs the generator's anchor must regenerate every committed `.s` artifact in the same
push**, and should consider making 4978 revalidate (compare `g_bid_tab[_bid].len` against the baked namelen)
so a stale artifact is caught instead of obeyed.

## Consequence for anyone adding a builtin today

The live header defines **189** `BID_*` constants; a regeneration today would harvest **0** names. So the
numbering is frozen, and a new builtin name cannot get a BID by the sanctioned path. The only correct route is
a plain `!strcmp(fn, "NAME")` arm: an unknown name gets `_bid == 0`, matches no `BID_*` constant, falls past
the `g_bidjmp_on` switch's `default: break`, and is reached through the linear chain. That is what the
`ICN_REFRESH` arm does, and it is append-only by construction.

## ⭐ THE ASYMMETRY THIS CREATES, NAMED SO THE NEXT READER DOES NOT COPY IT (hq_U, co-signing)

The tree already carries five `ICN_` internals — `ICN_CASE_EQ`, `ICN_NULL`, `ICN_SCAN_POP`,
`ICN_SCAN_PUSH`, `ICN_SWAP_TOP2` — and **every one of them HAS a BID** in `builtin_ids.h`. The new refresh
builtin is the first of that family to sit OUTSIDE the table, and the reason is **an instrument that cannot
run, not a design choice**. ⛔ Do not read the fall-through as the convention: if the generator's anchor is
ever repaired, this name should join the table with the rest of its family.

## ⛔ AND A SECOND BUG THE SAME REVIEW CAUGHT — IN THE NAME ITSELF

The first cut of this cure named the builtin `ICN_REFRESH`, which is **a legal Icon identifier**. hq_U flagged
it; it reproduces, and it is not theoretical:

    procedure ICN_REFRESH(x); return "HIJACKED"; end
    procedure main(); local e; e := create (1 to 3); write(image(^e)); write(ICN_REFRESH(1)); end

    iconx           co-expression_3(0) / HIJACKED
    scrip (before)  "HIJACKED"         / HIJACKED     <- ^e captured by the user procedure

A user procedure of that name **hijacked the `^` operator**. The cure is the convention already in this same
table: the `SNO$*` family (`SNO$NAME`, `SNO$MKPAT`, …) uses `$` **precisely because `$` cannot be lexed as an
Icon identifier** — icont answers `invalid character` on `procedure ICN$REFRESH`. Renamed to `ICN$REFRESH`,
after which scrip matches iconx exactly on the witness above.

⭐ Both naming conventions are live in this tree and **only one of them is collision-proof**. A new internal
builtin name must carry `$`. The five `ICN_` names above are pre-existing and each is a latent instance of
this same hazard — not cured here, and named so somebody can decide whether they are worth renaming.

## OWED TO hq_U'S LANE, FILED BY NAME AS ASKED

`shared-the-baked-builtin-id-in-emitted-code-has-no-gate-revalidating-it-against-the-name` — one contract in
two places (`bid_bake_of` writes it, `:4978` reads it) with nothing comparing them. hq_U names it the same
shape as the N-2 entry frame it landed today, where two hand-written copies of one ABI drifted and took weeks
to find. Right now the generator's refusal is the only thing holding the numbering still, so **the safety is
an accident of a broken script**: the day someone repairs `FUNC_RE` to anchor on `try_call_builtin_by_name_bl`
at :4946, every committed `.s` carrying a baked id goes stale in one commit and nothing will say so.

## Neighbours
- The `^`/`copy` co-expression cure that surfaced this (jcon `sorting`, both modes green against icont).
- `FINDING-2026-09-06-hq_I-...` — same family: an instrument answering a narrower question than the reader thought.
