# FINDING 2026-08-24 seat12 — `snobol4-trailing-star-comment-not-lexed`: root cause was in `snobol4.l`, not `stmt_ast.c`; two-rule flex fix, oracle-verified, gate-clean

**Row:** `snobol4-trailing-star-comment-not-lexed` (rank 1, minted hq_C s272 from seat07's finding while working `corpus-suites-consolidation`). GOAL text: *"SCRIP's comment detection is a physical-line preprocessing check, not lexer-integrated... `src/driver/stmt_ast.c:184,186` tests `t[0]=='*'` against `g_src_lines`."*

## Correction to the row's own diagnosis — the cited site is not the mechanism
`stmt_ast.c:184,186` (`stmt_src_slice`) only reconstructs a `:src` diagnostic-string AST attribute (consumed nowhere that affects parse success). Traced the real failure via the actual error site (`sno_error(...,"missing END statement")` in `snobol4.l:414`) back through `parse_program_tokens_ast` into the reentrant flex lexer itself (`src/parser/snobol4/snobol4.l`, compiled to `snobol4.lex.c`). Comment detection **is** already lexer-integrated (the `SKIP` start-condition), contra the row's premise — the bug is a scoping error inside that existing mechanism, not a missing design. This makes the row's STEP 1 choice between "(a) preprocess `;*` boundaries" and "(b) make comment detection lexer-integrated" moot: (b) already existed; the fix is a two-rule correction inside it, not a new subsystem.

## Root cause, traced by hand through the flex states (`INITIAL` → `LABEL` → `BODY_START` → `BODY`)
Two adjacent bugs in `snobol4.l`, both stemming from `;` being treated identically to `*`/`!`/`|` when the real semantics differ:

1. `<INITIAL>[*!|;] { BEGIN(SKIP); }` (line 48) — a **lone `;`** encountered at a fresh statement-start position (true column 1, or immediately after a prior `;` mid-line) was grouped with the genuine comment-trigger characters and sent to `SKIP`, which consumes the **entire rest of the physical line** (`<SKIP>[^\n]*`). For `;END;` this swallows `END` itself as "comment" text; the program never registers an END statement.
2. `<LABEL>[^ \t\n]+ { ...accumulate... }` (line 126) — the greedy label-continuation rule excluded only space/tab/newline, so scanning a label that happens to contain a `;` (e.g. `END;* abc` immediately following the OUTPUT statement's own terminating `;`) swallows straight through the `;` and the following `*` as if they were ordinary label characters. For `OUTPUT = 1;END;* abc`, the label buffer accumulates `END;*` (5 bytes) — not `"END"` — so the `strcmp(strbuf,"END")==0` check in `flex_lex_next` (`snobol4.l:337`) never fires and the statement becomes a bogus label+identifier pair instead of the END statement.

Both defects produce the same downstream symptom: `saw_end` stays 0 in `sno_parse_ast` (`snobol4.l:414`), so every affected program reports "missing END statement" regardless of whether it has one.

## Fix — two narrow rule changes, no new state, no new subsystem
```diff
 <INITIAL>\n             { lineno++; return T_STMT_END; }
-<INITIAL>[*!|;]         { BEGIN(SKIP); }
+<INITIAL>[*!|]          { BEGIN(SKIP); }
+<INITIAL>";"            { return T_STMT_END; }
 <INITIAL>[ \t]          { g_stmt_lineno = lineno; BEGIN(BODY_START); }
```
A lone `;` at INITIAL now falls out as an empty statement (identical token shape to a blank physical line, which the parser already tolerates today) instead of a full-line comment trigger. `*`/`!`/`|` are untouched — they still start a comment exactly as before, so a `*` seen immediately after this new rule fires (i.e. a genuine `;*` boundary) still reaches the unmodified `<INITIAL>[*!|]` rule on the very next lexer call and starts a comment correctly.
```diff
-<LABEL>[^ \t\n]+  {
+<LABEL>[^ \t\n;]+  {
     int take = yyleng < (int)sizeof(strbuf)-strpos-1
                ? yyleng : (int)sizeof(strbuf)-strpos-1;
     memcpy(strbuf+strpos, yytext, take); strpos += take;
 }
```
A `;` now stops label accumulation early; the pre-existing (previously dead-code, because `[^ \t\n]+` matched everything) `<LABEL>. { yyless(0); ...; return T_LABEL; }` catch-all now fires, pushes the `;` back, and ends the label cleanly. Neither change touches `BODY`/`STR1`/`STR2` (string-literal handling), `LABEL_DONE` (which already excludes `;`/`*`/`!`/`|` correctly for its own, unrelated case), or any other frontend.

Regenerated `snobol4.lex.c` from the edited `snobol4.l` via the project's sanctioned `flex --noline -o snobol4.lex.c snobol4.l` (same invocation as `scripts/regenerate_parser_and_lexer_from_sources.sh`; `bison` unavailable in this environment but not needed since `snobol4.y`/`.tab.c` are untouched). Used a locally-extracted flex 2.6.4 at `/tmp/flexbison/root/usr/bin/flex` — byte-identical version to the one that produced the checked-in `snobol4.lex.c` (its own header records `YY_FLEX_MAJOR/MINOR/SUBMINOR_VERSION 2.6.4`).

## Grading against the oracle (STEP 2), not against taste — one witness came out differently than the row's table implied
Ran all four of the row's witnesses plus the mandatory string-literal guard through `x64/bin/sbl -bf` (`sbl_correctness_bin`, per `lib_oracle_flags.sh`) before and after:

| witness | oracle | scrip (before) | scrip (after) |
|---|---|---|---|
| `        OUTPUT = 1;END;* abc` | `1`, rc=0 | missing END, rc=1 | `1`, rc=0 |
| `;END;` | (no output), rc=0 | missing END, rc=1 | (no output), rc=0 |
| `;END*abc` | **`No END statement found in source file(s).`, rc=1** | missing END, rc=1 | missing END, rc=1 (unchanged) |
| `;END X` | (unchanged control witness) | survives | survives (unchanged) |
| `OUTPUT = ';* not a comment';END` (added, mandatory guard) | `;* not a comment`, rc=0 | `;* not a comment`, rc=0 (already correct — `STR1` state is untouched by this bug) | `;* not a comment`, rc=0 |

The row's table listed `;END*abc` as "wanted: parses" — **the oracle itself rejects this input** (`*` jammed directly onto `END` with no separating `;`/whitespace/column-1 is not a valid trailing-comment start in SPITBOL either; its own lexer's label/keyword scan does not split on a bare `*`, matching the class of defect this row fixes, just on the oracle's own side). Per the row's explicit STEP 2 instruction ("where SPITBOL and intuition disagree, SPITBOL wins"), treated "parses" as "resolves deterministically to the oracle's own PASS/FAIL verdict," not "must compile" — scrip's pre-fix and post-fix behavior for this witness are identical (a controlled `missing END statement` diagnostic, rc=1), which **is** the correct, oracle-matching outcome, not a residual bug. Confirmed by adding it as a `test_error_paths_vs_oracle.sh` witness (`end_star_no_boundary`, verdict `SAME`) rather than a crosscheck success case.

## Regression protection added (permanent, not scratch)
- `corpus/crosscheck/comments/{trailing_star_comment,leading_empty_semicolons,semicolon_star_not_string_comment}.{sno,ref}` — three new crosscheck pairs, graded automatically by `test_corpus_snobol4.sh` (finds `corpus/crosscheck/**/*.sno`) in both modes forever after. Each `.ref` was verified byte-equal to a fresh `x64/bin/sbl -bf` run, not hand-typed from assumption.
- `corpus/probe/errpath/end_star_no_boundary.sno` + one new TSV row in `SCRIP/scripts/test_error_paths_vs_oracle.sh` (verdict `SAME`, rationale inline) — covers witness 3's correct-rejection behavior under the project's existing error-path-vs-oracle ratchet (`WRONG` count unchanged at 0/13).
- Rewrote the task's own `DONE-WHEN` from unexecutable prose into a real command (`s4e_msg.sh done` runs `bash -c` on that line verbatim — the original text, opened with a markdown-code-span backtick-quoted shell fragment, would have failed on syntax before checking anything). New DONE-WHEN composes the two gates above; both witnesses are now permanent, so the check is meaningful on every future run, not just this session's.

## Gates (all on `make pristine` rebuilds, HQ-27; `RT_OPT=-O0` throughout, no `-O2` anywhere per the FACT RULE)
- `test_corpus_snobol4.sh`: **PASS=365 FAIL=0** (m3) / **PASS=365 FAIL=0 SKIP=0** (m4), `✅ GATE OK`, MISSING=0. (Total grew from the row's earlier 338/362 citations elsewhere in this session's traffic — corpus additions from concurrent sessions, including this row's own 3 new witnesses and the `corpus-suites-consolidation` pilot's `crosscheck/patterns` conversion, which landed mid-session via `git pull --rebase` on both the `SCRIP` and `corpus` repos; re-ran the full gate after both pulls to grade the actual current tree, not a stale one.)
- `test_error_paths_vs_oracle.sh`: **TOTAL=13 SAME=7 DEFENSIBLE=6 WRONG=0**, `GATE PASS`.
- `test_smoke_icon.sh`: 14/14 both modes (Icon has its own hand-written lexer, `icon_lex.c` — unaffected by construction, checked anyway).
- `test_smoke_prolog.sh`: 3/5 (`clause`/`recursion` fail) — pre-existing, already independently documented by seat08/seat05 in the unrelated `perf-dispatch-callsite-cache` LEDGER this same day; not re-verified by a fresh A/B here since it shares no code path with this fix (`prolog_lex.c`).
- `test_smoke_snocone.sh`: 4/5 (`procedure` fails, `got: `) — **new to this session's traffic, verified pre-existing by git-stash A/B** (stash fix, `make pristine`, rebuild, re-run: identical `FAIL procedure (got: )`; `stash pop`, pristine-rebuild again before citing final numbers above). Snocone's lexer (`snocone_lex.c`) is a hand-written threaded-code FSM, not flex-generated, and shares no file with this change.

## Original DONE-WHEN, preserved verbatim (postoffice has no VCS — row `postoffice-git-home` — so this is the only durable copy)
> `        OUTPUT = 1;END;* abc` compiles and runs correctly under BOTH modes (m3 and m4), AND `;END;` and `;END*abc` both parse, AND SNOBOL4 corpus stays FAIL=0 SKIP=0 both modes. ⛔ Assert FAIL=0/SKIP=0 and the named witnesses — never a denominator (see the tdump-probe lesson, same session).

## Pushed commits
`SCRIP` `1d020651` (lexer fix + error-paths witness, rebased twice over concurrent Icon/perf pushes, gate re-proven clean each time). `corpus` `4d097667` (three crosscheck pairs + one errpath probe).

## STEP 3 (told the suites row)
Sent `s4e_msg.sh send hq_C corpus-suites-consolidation` (also left in that task's own QA) noting the `;*`-join defect their harness was working around is fixed as of this commit — their one-line join no longer needs to fall back to a multi-line block purely because of a trailing-comment tag on a joined line.
