# FINDING 2026-09-05 hq_P — the goto-field function call is a call BY NAME, and the "6 m4 BUILDFAIL" xfail group is FIVE mechanisms, not one class

Row: `snobol4-every-xfail-fixed-as-a-faulty-test-or-cured-as-a-defect` (hq_P, OCTET).
Tree at measurement: SCRIP `23c6e45d6`, corpus `7ffe8b899`, .github `a3c6664a` (all three were BEHIND origin at
session start and were fast-forwarded BEFORE measuring — the fetch-is-not-checkout rule, hit again).
Census re-run from the row's own DONE-WHEN: `XFAIL_CENSUS snobol4 csv=39 of 1880 allxfail=78 files=1`.

## 1. The group my own prior FINDING sold as "the cheapest real class left" is not a class

`FINDING-2026-09-05-hq_P-snobol4-xfail-class-census-…` grouped 6 entries as **`m4 BUILDFAIL (compile/link)`**
and the row's NEXT block named them step 1 *"the only untouched group whose failure is at COMPILE time, so they
need no runtime archaeology"*. Both halves of that sentence are wrong, and I wrote them.

⛔ **They are not m4-only.** All six exit non-zero in **m3 as well** — measured, one run each, same tree.
⭐ Stated exactly, because the provenance of my own mistake is not something I can reconstruct and should not
guess at: **the label says m4; the measurement says both modes.** Whatever produced the grouping, it was not a
probe of m3 — that much the disagreement proves on its own.

⭐ **Six entries, FIVE unrelated mechanisms:**

| entry | mechanism | oracle (`sbl -bf`) says |
|---|---|---|
| `simple_program_1` | faulty test — ref is UNMATCHABLE (below) | listing + ERROR 285 |
| `simple_output_68` | faulty test — `-INCLUDE` companion exists nowhere in corpus | listing + ERROR 285 |
| `simple_output_63` | faulty test — lowercase `end`; the oracle rejects it too | `No END statement found in source file(s).` |
| `array_replace_branch_2` | ⭐ **fixture-VISIBILITY artifact hiding a REAL defect** (§2) | `3 permutations` — correct |
| `user_function_indirect_replace_1` | ⭐ **real: goto-field call, by-name** (§3) | rc=0, matches ref exactly |
| `trim_alt_keyword_replace_branch_1` | unlanded feature: conditional pattern lambda | rc=231 |

⛔ **`simple_program_1`'s ref can never match anything.** It is SPITBOL *listing* output that embeds a wall-clock
timestamp (`x86-64  Sat Aug 29 17:00:50 2026`) and names a DIFFERENT file than the entry
(`missing_include_target.sno(4,10)`). A ref carrying a date is not a slightly-stale ref; it is a test that is
red by construction on every future run. Resolving it is a ref re-cut or an attributed retirement, never a
compiler change.

## 2. `array_replace_branch_2` — the missing include is NOT missing, and a real defect was hiding behind it

`gimpel_triage_class8_sig6_perm_module.sno` **exists**, at `corpus/tests/snobol4/`. The entry fails only because
the harness extracts each entry into its own fresh temp dir and the companion does not travel with it. Run with
the companion visible on cwd:

* oracle → `3 permutations` (the ref, exactly)
* `scrip` m3 → `[WSI] workspace island exhausted (1024 MB, 25165244 blocks) — raise ZC_WSI_MB`, then **core dump**

⭐ **The instrument lesson is the transferable part:** a fixture-path artifact and a missing fixture print the
same diagnostic (`cannot open include`), and the first one is indistinguishable from the second until you look
for the file. Two of these six were classified as "missing corpus fixture" on that diagnostic alone. One was.
⛔ **Never classify an include failure without `find`-ing the named file first** — the cheap check flips the
entry from paperwork to a live crash.

## 3. THE CURE AND ITS DISPROOF — `:(GO())` is a call BY NAME, and we are exactly INVERTED

`user_function_indirect_replace_1` (distilled from gimpel `STATEF_driver`, batch F) is the one entry here whose
oracle arm is clean: `sbl -bf` runs it rc=0 with output matching the ref. SCRIP refused it at PARSE time —
`snobol4:25: error: parse error: syntax error` — on `:(GO())`, a goto whose operand is a **function call**.
Its two siblings in the same program are the built-in control pair: a direct goto `:(L1)` and an indirect goto
`:($W)` both pass, so the refused ingredient is THE CALL IN THE GOTO.

**The parser gap is real and is cured here** (§4). ⛔ **But the parse error was hiding a second, deeper defect,
and a three-probe control set against the oracle names it exactly:**

| probe | function body | oracle | SCRIP after the parser cure |
|---|---|---|---|
| `a_str` | `F = 'L3'` `:(RETURN)` | **ERROR 021** — function called by name returned a value | `go` / `landed` |
| `b_name` | `F = .L3` `:(NRETURN)` | `go` / `landed` | **ERROR 239** — indirection operand is not name |
| `c_namerv` | `F = .L3` `:(RETURN)` | **ERROR 021** | `go` / `landed` |

⭐⭐ **SCRIP is EXACTLY INVERTED against the oracle: we accept both forms SPITBOL refuses and refuse the one
form SPITBOL accepts.** The reason is one sentence: **a function call in the goto field is invoked BY NAME.**
SPITBOL requires the callee to `NRETURN` and raises ERROR 021 on a value return; the NAME that comes back IS
the transfer target. My cure reused `sno_goto_computed_target`, which wraps the result in `$` — correct for a
STRING label name, wrong for a NAME, hence ERROR 239 on the only legal arm.

⛔⭐ **THIS IS NOT AN EXOTIC CORNER — IT IS THE ENTIRE PUBLISHED CONTRACT OF `STATEF.inc`**, and that is what
makes it announcement work rather than a one-entry cleanup. `corpus/packages/snobol4/gimpel/STATEF.sno`:

```
RET	NAME  =  POP()
	$NAME  =  NEXT
	RET  =  .RETURN				:(NRETURN)
```

Every state function in the family returns via `:(RET(label))`, and `RET` ends `RET = .RETURN :(NRETURN)` — the
by-name arm, the one still broken. **The parser cure alone gets these programs NOWHERE.**

⭐ **Census of the idiom, counted honestly:** 13 occurrences in **4 real programs** — `STATEF_driver.sno` (4),
`POKEV.sno` (6), `STATEF.sno` (1), `snoflake_suite/gimpel-state-functions.sno` (2) — in **gimpel** (289-entry
package suite) and **snoflake** (180), both on the announcement's SNOBOL4 100% list. ⛔ A raw grep reports
*20 across 6 files*; the extra two "files" are `ALL.sno` suite CONTAINERS, which hold copies of the same
programs. **A container is not a program and must not be counted beside one** — the same category error that
makes `./scrip ALL.sno` look like a pile of duplicate-label defects. `POKEV.sno` carries the argument-bearing
form, `:S(PR(6,W V))F(PR(3,W))`, which is why the cure needs `T_COMMA` and digits in the goto field and not
just the zero-argument shape the row's own witness uses.

## 4. What landed, and what did NOT

✅ **Parser + lexer only** (`src/parsers/snobol4/snobol4.y`, `snobol4.l`, and their regenerated twins):
 * `goto_label_expr` gains `( IDENT ( args ) )` → a `TT_FNC` node, which `sx_lower` already lowers. **No lowerer,
   emitter, template or runtime change; no new globals.**
 * `goto_fnc_args` + `T_INT` in `goto_atom`, so `RET('C2')`, `PR(8)` and `PR(6,W V)` parse.
 * ⛔ **A REAL LEXER BUG, found by a probe and fixed:** `<GT>[Ss]/"("` and `<GT>[Ff]/"("` returned the
   success/failure goto markers **at any paren depth**, so a user function named `S` or `F` was unreachable in a
   goto field — `:(F())` lexed `F` as T_GOTO_F. Now guarded on `gt_depth > 0`. My first probe was named `F` and
   this is the only reason I found it.
 * ⛔ **`<GT>.` SILENTLY DROPS every unmatched character**, which is why a comma and a digit inside a goto-field
   call vanished with no diagnostic. `,` and `{DIGIT}+` now lex; the silent-drop catch-all remains and is worth
   its own sweep.
 * Grammar conflict count is UNCHANGED at 1 shift/reduce, and it is **pre-existing** (T_CONCAT, in the
   expression grammar) — verified by running bison against the pre-edit `.y`. My additions add zero.

⛔ **NOT landed, and minted instead: the by-name half.** Making the goto-field call a by-name call — NRETURN's
name becomes the target, a value return raises ERROR 021 — is a coordinated m3+m4 codegen change over
`rt_g_ret_by_name` / `bcps_nret_consult` whose control arm is the whole 1880-entry master in both modes. That is
more than this sitting could honestly land, and the row's own standing rule is to mint rather than leave code
half-changed. ⛔ **So the witness entry stays xfail and this row's census does not move.** Landing the parser
alone leaves a KNOWN, documented permissive divergence (we run what SPITBOL errors 021 on); no currently-green
program can reach it, because every program that reaches it previously failed to parse at all.

## 5. ⛔ THE GENERATED-PARSER TRAP CAUGHT A THIRD SESSION TODAY — ME

I edited `snobol4.y`, ran `make`, watched it relink, and tested a binary that **did not contain my grammar
change**. The top-level `Makefile` compiles `snobol4.tab.c` / `snobol4.lex.c` as committed files with **no
bison/flex rule**, so a grammar edit changes nothing and the build still succeeds, greenly.
`test_gate_parser_generated_files_in_sync.sh` exists precisely for this and its header records two sessions
losing a build to it on 2026-09-04 (ceo on `raku.y`, hq_C on `snobol4.l`). ⭐ **The gate catches it at
`make test`; it does not catch it at the moment of the edit, which is where the hour is lost.** The cure is one
command and belongs in muscle memory the way `pull --ff-only` does:
`bash scripts/regenerate_parser_and_lexer_from_sources.sh`, then commit `.y`/`.l` **and their outputs together**.
