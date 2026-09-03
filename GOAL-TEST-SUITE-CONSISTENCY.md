# ⛔⭐⭐⭐ GOAL-TEST-SUITE-CONSISTENCY — ONE TEST STANDARD FOR ALL SEVEN LANGUAGES

**Opened 2026-09-03 ~16:25 CDT box clock by the ceo on Lon's order, in-chat to ceo, verbatim:** *"Make the testing of all 7 languages consistent with each other. If one has many rungs with tiny increments then create that for the other lanugages. If one has a nice regressions suite, then we want regression for all languages. Let's get our test suite up to snuff and improved greatly."* Owner: **hq_T (HQ-TEST, opened 2026-09-03 16:30 on Lon's word)** for the program — `GOAL-HQ-TEST.md`; each language's rows to that language's seat (07, 10, 11, 12, 14 → hq_T as ask target). Law: RULES.md § THE INSTRUMENT LAWS (fail once, pass once; names beside counts; the leaderboard FACT RULE); the one-flat-suite ruling (tests live in `corpus/tests/<lang>/ALL.*`); the ONE-IDENTITY law.

## LIVE CURSOR

**2026-09-03 16:25 (ceo):** inventory measured (below), the standard written, the umbrella row `test-suite-consistency-seven-languages-one-standard` (hq_B, rank 0) and one gap row per language minted and assigned by lane. Nothing built yet. Whoever resumes: the per-language rows in the queue are the work; this file's table is rewritten by the seat that closes each gap (tree-labelled), and `SCORE.md` gets the new instruments' rows the day they print.

**2026-09-03 ~16:35 (seat11):** Raku's "ladder / rungs" cell closed — see INVENTORY row below. `test_raku_ladder.sh` built (mirrors `test_prolog_ladder.sh` exactly: `--to N`/`--only N`/`--list`, both modes m3+m4, REFUSE rc=2 when it can't measure). 10 witnesses, `ladder__rung00_hello` through `ladder__rung09_string_methods` (one construct-topic per rung: hello, variables, arithmetic, strings, arrays, hashes, if/while, subs, for-loops, string methods), refs oracle-cut from real Rakudo (`rakudo-local`, `rakudo_bin()`) — not hand-authored. `--to 9` (the whole ladder built so far) is PASS 20/20, not just the `--to 5` DONE-WHEN floor. Row raku-construct-ladder-from-rung-0 stays OPEN for whoever climbs past rung 9 (subs+signatures beyond a bare 2-arg sub, classes/roles, regexes/grammars, exceptions, lazy lists are the named-but-unbuilt topics) — this session scoped to a solid, fully-green rung 0-9 foundation rather than reaching for red stretch rungs.

## THE STANDARD — what every language has when this is done (the best of each today, made the rule for all)

1. **A CONSTRUCT LADDER with tiny rungs** (Prolog's shape, `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § E; Icon's 41 IR rungs are the precedent): `ladder__rungNN_<slug>` entries in the master from rung 0 (hello world) upward, one construct per rung, graded by `test_<lang>_ladder.sh --to N | --only N` in both modes, refs cut by the language's oracle, witnesses that fail once before their rung lands.
2. **A REGRESSION MASTER** `corpus/tests/<lang>/ALL.<ext> + ALL.ref + ALL.csv` (SNOBOL4's 1,726 is the model), oracle-cut refs, both modes, on the leaderboard, never stale more than 25 commits.
3. **A SMOKE floor gate** of 4–14 programs (`test_smoke_<lang>.sh`), the HARD zero-FAIL bar, inside `make test`'s reach.
4. **PARSER FIXTURES** graded by `--dump-ast` (`modes=ast` in the master; Icon/Prolog/Raku have them).
5. **VENDOR / ORACLE SUITES** under `corpus/packages/<lang>/` graded by their own oracle (SNOBOL4 5, Icon 5, Prolog 2, Pascal 2 + the ISO 7185 PAT, Raku the roast).
6. **A PORT-TRACE GATE** where the oracle can trace (Prolog has it; Icon's `&trace`, SNOBOL4's `&TRACE`): the emitted Byrd-port sequence diffed against the oracle's trace — the literature's debugging model turned into the execution model's instrument.
7. **A LEADERBOARD ROW** per instrument, rewritten by every run (FACT RULE).

## THE INVENTORY (measured 2026-09-03 16:20 box clock, SCRIP `d24e99d8`; rewrite a cell when you close its gap)

| language | master (entries · xfail · families) | ladder / rungs | smoke | parser fixtures | vendor suites | trace gate | leaderboard row |
|---|---|---|---|---|---|---|---|
| SNOBOL4 | 1726 · 80 · 388 (THE model) | ⛔ none (one pattern rung suite) | 4-program smoke | ⛔ none | aisnobol, csnobol4_suite, dotnet, gimpel, snoflake (5) | ⛔ none (`&TRACE` exists) | yes |
| Icon | 534 · 1 · 308 (259 rung-tagged) | 41 IR rung scripts + STRICT suite 298 | 14/14 | yes (153 ast) | arizona, ipl, jcon-compiler, jcon-ref, jcon_tests (5) | YES (`test_gate_icn_port_trace.sh`, 4 blocks, rung 3 generator witnesses only — plain non-suspend calls are a follow-up gap) | yes |
| Prolog | 404 · 10 · 114 | construct ladder 33 witnesses (rungs 0–8 + 30 legacy rung scripts) | 5-program smoke | yes | gnu_prolog, swi_tests (2) | YES (`test_gate_pl_port_trace.sh`, 66 blocks) | yes |
| Snocone | 273 · 24 · 43 (STALE 08-29) | ⛔ none | 5-program smoke + 10 parser smokes | ⛔ none | none (the library ports) | ⛔ none | yes |
| Rebus | 48 · 0 · 34 (STALE 08-29) | ⛔ none | 4-program smoke | ⛔ none | none | ⛔ none | yes |
| Raku | 139 · 14 · 57 (STALE 08-29; 724 inline probes being absorbed) | ✅ construct ladder rungs 0-9, 10 witnesses (`test_raku_ladder.sh`, seat11 2026-09-03), refs cut from real Rakudo | 724-probe script (a rung suite in disguise) | yes | roast (in `refs/`, scoreboard script) | ⛔ none | yes |
| Pascal | 159 · 0 · 71 (fresh 2026-09-03, seat10) | ✅ construct ladder rungs 0-9, 10 witnesses (`test_pascal_ladder.sh`, seat10 2026-09-03), refs cut from real `fpc -Miso`; rung 9 honestly RED | ✅ 9/9 both modes (`test_smoke_pascal.sh`, seat10 2026-09-03) | ⛔ none | fpc_tests, p5, ISO 7185 PAT (row) | ⛔ none | yes |

## THE ROWS (one per gap; the umbrella closes when every cell above reads yes)

`test-suite-consistency-seven-languages-one-standard` (hq_T, rank 0, the program) · `pascal-smoke-floor-gate-and-construct-ladder-from-rung-0` (seat10) · `snobol4-construct-ladder-from-rung-0-with-trace-refs` (seat12) · `snocone-construct-ladder-and-parser-fixtures` (seat12) · `rebus-construct-ladder-parser-fixtures-and-a-real-master` (seat12) · `raku-construct-ladder-from-rung-0` (seat11) · `icon-port-trace-gate-against-ampersand-trace` (seat14) · `snobol4-parser-fixtures-and-port-trace-gate-against-ampersand-trace` (seat12) · `pascal-parser-fixtures-and-the-iso-7185-pat-suite` (seat10). Masters that read STALE are re-measured by the seat that touches the lane (FACT RULE).
