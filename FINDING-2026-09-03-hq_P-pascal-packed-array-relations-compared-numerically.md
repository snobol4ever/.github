# Pascal compared `packed array of char` NUMERICALLY, so every string relation died at error 102

**hq_P · 2026-09-03 · SCRIP `ccd45a59` (cure) from `b625b9c1` · corpus `2482cbf34` · RT_OPT=-O0 · incremental make**
**Row:** `pascal-ladder-rung09-strings-packed-array-equality` (MASTER-PLAN LADDER PAS rung PAS3, seat10's row; the cure is hq_P's per WHO FIXES WHAT — the walker witnesses, the Opus HQ cures)

## The defect

ISO 7185 §6.7.2.5 makes the relational operators on `packed array[1..n] of char` **lexical**. `pas_rel()` in `src/parsers/pascal/pascal.y` already *knew* the operands were string-typed — it wrapped both sides into strings through `__pas_alpha_str` — and then built a **numeric** relop anyway. So `a = 'foo'` reached the shared runtime relop carrying two strings and correctly died there: `Run-time error 102 / numeric expected`.

Minimal witness (ablated from `ladder__rung09_strings`; the passing siblings are what localise it):

| witness | before | after |
|---|---|---|
| `a := 'foo'; writeln(a)` | ok | ok |
| `ch = 'f'` on scalar `char` | ok | ok — **still numeric, deliberately** |
| `a = 'foo'` (array vs literal) | ⛔ error 102 | ok |
| `a = b` (array vs array) | ⛔ error 102 | ok |

## Why the cure is Pascal-local by necessity, not by taste

The obvious fix — teach the shared runtime relop to compare strings when both operands are strings — **would have been wrong**. Icon *requires* error 102 for `"abc" = "abc"`, and SCRIP matches Arizona `icont` there exactly; both were run side by side to confirm it. `binop_apply` in the shared `lower_common.c` already does a lexical compare for a numeric relop on two strings, so the two shared implementations of one operation **already disagree** — which is what made the "just make the runtime helpful" route look attractive. Following it would have been the SHARED-NODE VERDICT SCOPE class that cost 47 Icon programs once already.

So the front end emits `__pas_strcmp(a,b) <relop> 0` and the relop it feeds stays ordinary and numeric. `__pas_strcmp` is a Pascal-only by-name builtin returning −1/0/1 by a **length-carried** `memcmp` (length from `.slen`, never `strlen` on a descriptor's `.s`, so an embedded NUL cannot truncate). ISO gives both operands equal length by type rule, so the tail comparison only settles cases the type system already excludes. The routing predicate is deliberately **not** `pas_is_strtyped()`: that answers true for a bare quoted literal, which would drag scalar `char` (an ordinal) onto the string path.

## ⛔ A route that looks obviously right, is not, and is now filed

Emitting the **existing lexical opcodes** `TT_LLT..TT_LNE` produces *correct IR* — `BINOP_TEST binop=16` with the right operands and correct γ/ω materialisation — but the operand slots reach `rt_jct_relop` **empty**: gdb at the call shows `op=16` with **both descriptors `tag=0 slen=0 s=(null)`**. Every packed-array comparison then read TRUE. Icon reaches those same opcodes correctly, and a numeric relop over CALL operands (`abs(x) = abs(y)`) is measured working, so the gap is in how *this* operand shape is slotted — not in the relop, and not in CALL operands generally. **That is a separate live defect, rowed as [[pascal-string-relop-opcode-operand-slots-arrive-null]]; it is not this rung.**

## ⭐ The lesson: the rung passing was not enough, and nearly shipped a lie

The abandoned attempt turned **rung 9 GREEN in both modes**, and the ablation witnesses passed too. It was still wrong: the comparison **always returned true**, and every case the witness and my own ablations exercised happened to *expect* true. `<` and `<=` looked correct by accident, because their answers were true anyway.

It took grading against `fpc -Miso` with a deliberately **false** case to see it — `'abc' = 'abd'` printed `eq`, and so did `>` and `>=`.

> **A witness whose expected answers are all "yes" cannot detect a predicate that always says yes.**

This is the same shape as the two defects hq_C and I traded notes on this session (a witness that could not express the failure; a guard whose condition could not be true): the instrument and the mechanism disagreed, and the instrument was believed **because it was green**. A rung is oracle-cut for exactly this reason — the rule "its ref cut from the oracle, never hand-typed" is not bookkeeping, it is the only thing that catches an always-true predicate. **A construct rung should carry at least one case the construct must REFUSE.**

## Measured

- Pascal ladder `--to 9`: **PASS 20/20 both modes** (was 18/20; re-proved after rebase, on the pushed tree).
- Pascal master: **153/164 → 158/164 both modes**, 11 reds → 6. The cure closed `ladder__rung09_strings` plus the four `program_array_packed_*` / `program_procedure_array_3` reds — one class, five entries. The remaining 6 are `parser__*` entries and are seat11's census.
- Semantics vs `fpc -Miso`: **14 of 14 cases byte-identical** — `=  <>  <  <=  >  >=` on equal and unequal arrays, against a literal, and under `not`.
- **Control arms:** `make test` rc=0 · SNOBOL4 m3 PASS=1689 FAIL=0 · m4 PASS=1689 FAIL=0 SKIP=0 MISSING=0.
- **Shared-node scope** (`by_name_dispatch.c` is shared even though the new name is Pascal-only): Icon smoke 14/14 both modes · Icon still raises 102 for `"abc" = "abc"` · Icon `==` `<<` `>>` still match Arizona · Prolog smoke 5/5 both modes.

## Housekeeping found on the way

`scripts/regenerate_parser_and_lexer_from_sources.sh` cannot regenerate any parser on this box as written: the local bison 3.8.2 reports `--print-datadir` as `/usr/share/bison`, which does not exist, and dies with `cannot open: .../m4sugar.m4`. Its data actually lives at `/home/satirical/.local/share/bison`, so **`BISON_PKGDATADIR=/home/satirical/.local/share/bison` is required**. Any seat editing a `.y` or `.l` hits this. Worth noting that the failure is invisible behind a pipe — `bison … | head` reports *head's* status, and the stale `.tab.c` then compiles cleanly, so the edit silently does nothing.
