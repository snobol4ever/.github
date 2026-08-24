# Survey 03 — src/parser/{raku,rebus,pascal} (agent report, condensed verbatim)

## 1. INVENTORY
| Path | LOC | Purpose | Verdict |
|---|---|---|---|
| raku/raku.y | 1704 | Raku grammar/actions | LIVE |
| raku/raku.l | 279 | Raku lexer | LIVE |
| raku/raku.tab.c/.h | 6179/218 | generated | GENERATED |
| raku/raku.lex.c | 3684 | generated | GENERATED |
| raku/raku_driver.c/.h | 19/6 | raku_compile() entry (scrip.c + polyglot.c) | LIVE |
| raku/re.c/.h | 415/60 | standalone NFA regex+grammar engine | LIVE but **MISPLACED** |
| rebus/rebus.y | 536 | Rebus grammar | LIVE |
| rebus/rebus.l | 177 | Rebus lexer | LIVE |
| rebus/rebus.tab.c/.h | 2594/157 | generated | GENERATED |
| rebus/lex.rebus.c | 2043 | generated | GENERATED |
| rebus/rebus_lower.c/.h | 455/6 | AST→SNOBOL4-CODE_t transpile + rebus_compile() | LIVE |
| rebus/rebus.h | 37 | shared rebus AST helpers | LIVE |
| rebus/rebus_main.c | 49 | standalone rebus CLI | **DEAD/broken** |
| rebus/Makefile, .gitignore | 66/1 | builds the dead CLI | **DEAD** |
| pascal/pascal.y | 922 | grammar + full hand-rolled symbol table | LIVE, oversized |
| pascal/pascal.l | 102 | lexer | LIVE |
| pascal/pascal.tab.c/.h | 3022/164 | generated | GENERATED |
| pascal/pascal.lex.c | 2181 | generated | GENERATED |
| pascal/pascal_driver.c/.h | 19/7 | pascal_compile() + pas_is_nrec_idx decl | LIVE |

**Raku and Pascal are genuinely LIVE, not stubs** — deep rung histories (RAKU-100, RK-*, PAS-PINT-*), real corpora, dedicated gates (test_gate_raku_zframe.sh, test_gate_pascal_m3/m4.sh), end-to-end via lower_*_stage2 into scrip.c. CLAUDE.md's "in progress" undersells them.

## 2. DEAD PARTS
- **rebus_main.c + rebus/Makefile + .gitignore + scripts/build_rebus_frontend.sh: dead and unbuildable.** rebus_main.c calls rebus_print()/rebus_emit(), both git-mv'd to src/attic/ in commit e7d0a324 ("Dead-code sweep pass 3"); local Makefile SRCS still lists them. Real entry: rebus_compile() in rebus_lower.c:433 via scrip.c:987 + polyglot.c:106.
- No #if 0 blocks; no mode-1/2 residue; no other unreferenced functions.

## 3. MISPLACED
- **raku/re.c+re.h → src/runtime/ (e.g. runtime/core/re.c).** General-purpose NFA regex/grammar engine. Consumers: runtime/by_name_dispatch.c (builtins re_match, re_match_global, re_subst, re_capture, re_named_capture, nfa_compile, nfa_accepts @3815-3940), runtime/rt_runtime.c, driver/driver_private.h + driver_globals.c (g_match/g_subject globals @4-5). Not raku-gated. Update Makefile:334, 4 include sites, drop -I$(SRC)/parser/raku (Makefile:363 exists only for this).
- `lower/lower_pascal.c:520` calls `pas_is_nrec_idx()` which reads parser-time global tree_t* pointer array (`g_pas_nrec_marks[512]`, pascal.y:439) by pointer identity — lower reaching back into parser internals; fold into an AST node flag.

## 4. SPLIT/MERGE
- **pascal.y contains an entire hand-rolled symbol table: 89 distinct g_pas_* file-scope globals** with linear-scan helpers → extract `pascal_symtab.c/.h`; fixes most 200-char violations too.
- raku_driver/pascal_driver near-identical 19-line boilerplate (minor).
- rebus_lower.c does desugar + driver entry (not urgent).

## 5. VIOLATIONS
- 200-char: pascal.y ~95 lines over; worst pascal.y:427 (1851 chars!), :704 (1794), :799 (1050), :731-732. raku.l:104 = 233; pascal.l:353 = 207.
- Header-guard style: 3 conventions in 5 small headers; rebus_lower.h alone uses #pragma once.
- Blank lines: 0 everywhere (compliant).
- No LANG_* leakage.
- Globals census: raku.y:294-295 raku_meth_table static; rebus.y:8 static tree_t *prog; re.c:319 static Cap_snap g_snaps[MAX_STATES]. Pre-existing, census only.

## 6. DEPENDENCIES
- re.h included from driver/driver_private.h, runtime/by_name_dispatch.c, runtime/rt_runtime.c — confirms misplacement.
- pascal_driver.h is the only frontend driver header reached from src/lower/ (lower_pascal.c).
- All three grammars include ../snobol4/scrip_cc.h (18 files repo-wide include it).

## 7. NAMING
- Bison outputs uniform (<lang>.tab.c). **Flex outputs NOT: rebus alone generates `lex.rebus.c`** (regen script line 59) vs snobol4/raku/pascal `<lang>.lex.c`. Rename to rebus.lex.c (touch Makefile:336 + regen script).
- raku bison alone passes --warnings=none -Wno-yacc (suppressed grammar warnings — footnote for grammar quality).
- raku flex passes --prefix=raku_yy redundantly (also in .l).
- rebus_lower.c name implies parity with lower/lower_*.c but contract differs (returns SNOBOL4-shaped CODE_t re-lowered via lower_sno_stage2) — suggest rebus_to_snobol4.c.

## 8. MATURITY
- Raku + Pascal: wired end-to-end, gated, measured (M3 152/0 M4 152/0 commit messages) — NOT staging candidates. Carving either needs Makefile+scrip.c dispatch+lower.h edits; pascal also lower_pascal.c dependency.
- The one safe attic candidate: the dead rebus CLI set (§2).
