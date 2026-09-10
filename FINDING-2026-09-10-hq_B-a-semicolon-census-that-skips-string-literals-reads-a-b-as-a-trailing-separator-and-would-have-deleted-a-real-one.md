# FINDING 2026-09-10 hq_B — a semicolon census that SKIPS string literals reads `{a; ""}` as a trailing separator, and would have deleted a real one

**Seat:** hq_B · **Rows:** `icon-empty-expression-after-a-semicolon-inside-braces-is-null-per-icont` (CEO-512 rank 1),
`icon-every-shipped-icn-file-our-conversion-added-semicolons-that-icont-refuses-are-removed-so-icont-compiles-it` (CEO-488, third arm).
**Trees:** SCRIP `84ad00fe9` + this landing · corpus `021a16bf0` + this landing.

## 1. THE DEFECT CURED — an empty expression inside braces is `&null`, and SCRIP printed the wrong value

Under Icon a `;` inside `{ }` is a **separator**, not a terminator, so a trailing one leaves an *empty expression* as the
last element of the compound, and an empty expression yields exactly one result, `&null`. Measured against
`/home/resources/icon-master/bin/icont`:

| witness | iconx | SCRIP before | SCRIP after |
|---|---|---|---|
| `image({1;2;})` | `&null` | `2` | `&null` |
| `image({1;2})` | `2` | `2` | `2` |
| `image({1;;2})` | `2` | **parse error** | `2` |
| `image({;1})` | `1` | **parse error** | `1` |
| `image({;})` | `&null` | **parse error** | `&null` |
| `if {1=2;} then …` | succeeds | fails | succeeds |
| `every c +:= { gen(); }` | run-time error 102, offending value `&null` | silent wrong sum | error 102, offending value `&null` |

The cure is two lines in `src/parsers/icon/icon_parse.c` `parse_block_or_expr()`: a `;` seen where an element was expected
is an empty element, and — because `parse_stmt()` eats its own terminator — a trailing separator is only visible after the
loop, as `p->prev_kind == TK_SEMICOL` at the `}`. The case-body arm (`case … of { 1: a; }` is a parse error, as icont says)
was already present and is confirmed to agree with icont's `"}": invalid case clause`.

⭐ **This is a ONE ORACLE defect that only a value probe could see.** Every one of these blocks *compiled* clean in both
modes before the cure, so no compile-arm census over the corpus — the whole CEO-488 instrument — could ever have reached
it. It took the ceo running `write(image({1;2;}))` under iconx. **A criterion phrased as "does the oracle accept it"
cannot detect a defect phrased as "and what does it print".**

## 2. THE INSTRUMENT DEFECT — a census that skips string literals over-counts trailing separators

To find "a `;` whose next token is `}`" over 1380 shipped `.icn` files I wrote a scanner that skips comments, strings and
csets. It skipped them **by consuming them and emitting nothing**, so a skipped literal left no token behind — and

```icon
if any(White_space) then {
    tab(many(White_space));
    ""
    }
```

(`packages/icon/ipl/progs/ipp.icn:382`) read as `; }`. That `;` is a **real separator** between two elements. Deleting it
took `scrip --compile` on `ipp.icn` from rc=0 to rc=1.

⛔ **It was caught by exactly one thing: measuring every affected file's `icont -s -c` and `scrip --compile` rc BEFORE the
edit as well as after, and diffing the pair.** The count itself (73 files / 257 sites) looked entirely plausible; the
verdict "no file's rc changed" is what failed, on one file, and named it. ⭐ **The general form: a census whose skip-step
DELETES a token rather than REPLACING it silently changes adjacency for every rule phrased on "the next token".** The fix
is one line — emit a placeholder for the skipped span — and the corrected census is 72 files / 256 sites, differing from
the wrong one by exactly that single file. **A one-file error in a 257-site mechanical repair is invisible to review and
fatal to the tree**; only the before/after arm makes it announce itself.

This is the same family as `command -v` answering *is it on PATH* when asked *does it exist*, and `$?` after a pipeline
answering for the pager — the instrument answered a narrower question (is the next *non-literal* token a `}`) than the one
being asked, and said nothing about the difference.

## 3. A CORRECT CHANGE THAT READS AS A REGRESSION ON A SELF-PIN

`board_icon_master.sh`'s ast-shape arm went 153/153 → **147/153**. All six drifted fixtures drift by exactly one appended
node, `(TT_VAR &null)` — the empty expression the cure now models. The pinned dumps are self-pins, not oracles, so this is
the pin describing the old parser rather than a defect. Both repairs are available and they are NOT equivalent:

- **regenerate the six pins** — records the new shape, and leaves the fixture text carrying a trailing `;` that CEO-512's
  third arm forbids;
- **apply the third arm to `tests/icon/ALL.icn`** (151 sites) — the shape reverts to the *existing* pin, no pin is
  regenerated at all, and the fixtures then test what they are named for.

The second is correct and is **not mine to do**: `ALL.icn`/`ALL.ref`/`ALL.csv` are a built artifact with one writer,
`hq_V` (CEO-452). Handed over by telegram with the count. The six loose fixtures under `tests/icon/parser/` are repaired
in this landing; `ALL.icn`'s embedded copies are not.

## 4. WHAT THE THIRD ARM COST, MEASURED

72 files, 256 semicolons, per-file `bytes removed == semicolons removed`. Verified **in place** (never from a staging
copy — the jcon demos `link` siblings by relative path): `icont -s -c` rc and `scrip --compile` rc are **unchanged on all
72 files**, in both directions. Icon master board 756/758 both modes before and after; Icon ladder PASS=66 FAIL=7 before
and after; rung36_all pass=39 bad=3 before and after; Arizona 82/90 both modes.

⭐ The refs did not need re-cutting, and that is the evidence for the provenance claim: these trailing semicolons were
added by our own 826-file conversion (corpus `f8fe5b83d`), **after** the refs were cut from the oracle on the upstream
originals. Deleting them restores the text the refs were cut from. Where a block's value was actually consumed the
oracle had been quietly printing `&null` ever since the conversion — the ceo's `rung36_jcon_others` cure (corpus
`021a16bf0`) is six instances of exactly that, and this landing is the same repair carried across the whole population.
