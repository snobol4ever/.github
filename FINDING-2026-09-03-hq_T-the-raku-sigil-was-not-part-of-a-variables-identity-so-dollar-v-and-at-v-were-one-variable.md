# FINDING — the Raku sigil was not part of a variable's identity, so `$v` and `@v` were one variable

**Measured** 2026-09-03 by hq_T, cured in SCRIP `2b3048068` / corpus `50d17c27` (pushed `d6e902592` / `f4f1146e`), RT_OPT=-O0, incremental `make` (no pristine build — the 2026-09-03 FACT RULE).

## The claim

`var_node()` in `src/parsers/raku/raku.y` called `strip_sigil()` on **every** variable, so `my @v` and `my $v` both interned the bare name `v`. They were not two variables that printed alike — they were **one variable**, provable straight off `--dump-ast`, which emitted `(TT_VAR v)` for both.

```
my @v = 7, 8, 9;  my $v = 5;    say($v)       -> [5]    want 5
                                say(@v.elems) -> 1      want 3
                                for @v        -> 5      want 7 8 9
```

The scalar assignment **destroyed the array**. That is the serious half and it is silent: no diagnostic, no crash, a plausible answer.

On top of the storage collision, "is this name an array" was answered by `rk_array_names[]` — a file-scoped, append-only registry keyed on the **bare** name, with no scope and no sigil. Once `@r` appeared anywhere in a file, the name `r` was an array *forever*, in every later scope, which is what drove the rendering half.

## Why it surfaced as a list-method bug, and why that mattered

The Raku master's one red (`method_sub_for_replace_1`, both modes) failed only on these three lines:

```
my @r = @a.reverse;              # marks bare name r as an array, permanently
for @a.reverse -> $r { say($r) } # -> [2] [1] [3]   want 2 1 3
```

Idiomatic Raku, and silently wrong. The entry's own next line, `for @a.head(2) -> $hh`, was correct — so the board pointed at `.reverse`. **Ablating the method forms alone came back completely clean**: `.reverse`, `.unique`, `.head`, `.head(2)`, `.tail(2)` all correct in isolation. The defect needed BOTH an array and a later same-named scalar, and neither half is visible on its own.

⭐ **The reusable shape: a symptom that only appears when two correct-looking halves are combined will point at whichever half the test happens to name.** The first ablation exonerated the accused construct and *that was the finding* — the exoneration is what said "the trigger is context, not this method". A red that ablates clean is evidence about where the defect is NOT, and should redirect the search rather than close it.

Second trap, met inside the first: the ablation's own labels were double-quoted Raku strings — `say("-- loop var $r with NO @r in scope")` — and Raku **interpolates** in double quotes, so the label silently *referenced* the variables under test and contaminated the experiment (a case printed `[2] [1] [3]` with no `@r` declared, which briefly falsified a correct hypothesis). Single-quoted labels fixed it. Same family as this repo's backtick lesson: **the medium interpolates whether or not you meant prose.**

## The cure

`rk_var_ident()` keeps the sigil in the interned identity for `@` and `%` and leaves `$` bare — so every existing scalar name is byte-identical and only array/hash names move. Every array/hash name in the grammar already funnels through `var_node()` (including `rk_byref_param` / `rk_arr_index` / `rk_arr_pick` / `rk_arr_end_index`), so one function carries the whole change. The single path that did **not** was `lower_interp_str()`'s `@` branch, which rebuilt the name from identifier characters only; it now seeds the sigil, so `"@r"` in a string resolves to the array rather than a same-named scalar. `has $.x` attributes keep stripping — that is the attribute namespace, not the variable one.

**Safe by measurement, not assumption:** Raku variable names never reach the assembler. A variable named `arrname` appears **0** times in its own emitted `.s` (control: `main` appears 20), so a sigil in a name cannot break gas. That check cost one command and removed the only structural objection to the approach.

## Boards

| arm | before | after |
|---|---|---|
| master **run** (42 entries) | m3 41/42 · m4 41/42, one red | **42/42 both modes, FAIL=0** |
| master **ast** (97 entries) | 83 pass, FAIL=0, 14 xfail | 83 pass, **FAIL=0**, 14 xfail |
| ladder `--to 9` | 20/20 | 20/20 PASS=20 FAIL=0 |
| smoke | 724/724 both modes | 724/724 FAIL=0 REFUSED=0 |
| `make test` | rc=0 | rc=0 |

## The 24 re-cut ast refs, and how a re-cut was kept honest

Changing the AST moved 24 `--dump-ast` goldens (`ast_fail` 0 → 24 before the re-cut) — every array/hash/for-array/smartmatch fixture, and no others. **"Re-cut the goldens" is otherwise indistinguishable from editing a test until it passes**, so the sigil-only claim was proven mechanically before any ref was touched, two independent ways:

- **per entry** — removing the sigil from the new `--dump-ast` output reproduces the stored ref **byte-exact, 24 of 24, 0 exceptions**;
- **per file** — all 35 changed lines of `ALL.ref`, normalized the same way, reproduce the old lines exactly (empty diff).

Only then were the blocks rewritten, and exactly 24 blocks changed. ⭐ **The normalization diff is the thing that separates a legitimate re-cut from a cover-up**, and it is cheap; a re-cut asserted without one should not be believed, including from me.

⚠️ A by-product worth its own line: the first proof run reported 2 entries as "not sigil-only". Both were **artifacts of the proof harness**, whose header regex did not match headers carrying an `XFAIL` suffix, so one entry absorbed the next entry's header. The instrument was wrong, not the tree — and a proof harness that mis-parses in the *conservative* direction (reporting a false exception) is the harmless direction for this class; the same bug reporting a false *clean* would have signed off on a real semantic change.

## Related

- The row this closes was minted on a false watermark; see the baton's ledger and `SCORE.md`'s raku row. The `ast_fail=42` that named it was never 42 defects — it was `--lang raku` without `--modes` collapsing both populations into the ast bucket. That trap now REFUSES rc=3 (SCRIP `ca96ba948`).
