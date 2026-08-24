# Survey 01 — src/parser/snobol4 + src/parser/snocone (agent report, verbatim)

## 1. INVENTORY

**snobol4/**
| File | LOC | Purpose | Verdict |
|---|---|---|---|
| `Makefile` | 47 | Standalone per-dir build (bison/flex regen + `.o`) | **DEAD/ORPHANED** — not invoked by root build; only `scripts/build_snobol4_frontend.sh` calls it, and that script itself is called by nothing |
| `scrip_cc.h` | 111 | Shared AST/STMT_t/CODE_t contract types + inline helpers | LIVE — but **cross-language**, see §3 |
| `snobol4.h` | 33 | `Token`/`Lex` types, `SnoLine`/`LineArray` (unused), lexer decls | MIXED (live + dead residue) |
| `snobol4.l` | 420 | Flex grammar: reentrant lexer, statement-field FSM, include/copy/nofail directives | LIVE |
| `snobol4.y` | 327 | Bison grammar: full SNOBOL4 expression/statement grammar + AST-building actions | LIVE |
| `test_lex.c` | 211 | Unit tests for lexer | **DEAD/TEST-SCAFFOLD** — references types/tokens (`Program`, `TokKind`, `T_ERR`, `ILITYP`, `T_LBRACKET`, `T_PCT`, …) that don't exist anywhere in current codebase; not built by any Makefile target or script |
| `unicode_alpha_ranges.h` | 661 | Static table of 657 Unicode alphabetic codepoint ranges | **DEAD** — not included anywhere; lexer's `ALPHA` class is only `[A-Za-z\x80-\xFF]` |
| `snobol4.tab.c` | 2388 | GENERATED (bison 3.8.2) | GENERATED, in sync with `.y` |
| `snobol4.tab.h` | 150 | GENERATED | GENERATED, in sync |
| `snobol4.lex.c` | 3131 | GENERATED (flex 2.6.4) | GENERATED, in sync with `.l` |

**snocone/**
| File | LOC | Purpose | Verdict |
|---|---|---|---|
| `README.md` | 3 | Dir description | **STALE** — says "planned frontend (not yet implemented)"; frontend is fully built, wired into `RT_PIC_SRCS`, gated by `test_gate_em8_snocone_jit_emit.sh` / smokes |
| `snocone_driver.c` | 12 | `snocone_compile()` entry point | LIVE — called from `src/driver/scrip.c:989` |
| `snocone_driver.h` | 4 | Decl for above | LIVE |
| `snocone_lex.c` | 416 | Hand-written threaded-code (computed-goto) FSM lexer — **not flex-generated** | LIVE, MIXED (2 declared-never-defined fns, dead trailing statics) |
| `snocone_lex.h` | 16 | `LexCtx` + lexer API | MIXED — declares 2 functions never defined |
| `snocone_parse.y` | 842 | Bison grammar: C-like statement/expr grammar → shared AST | LIVE, contains dead helpers + a 29-line no-op macro block |
| `snocone_parse.tab.c` | 2985 | GENERATED (bison 3.8.2) | **GENERATED, STALE** relative to `.y` (§8) |
| `snocone_parse.tab.h` | 210 | GENERATED | paired with above, same staleness |

## 2. DEAD PARTS (grep-verified)

- `scrip_cc.h:109-110` — `extern char *yyfilename; extern int lineno_stmt;` — neither defined/referenced anywhere else. Pre-reentrant-lexer residue.
- `snobol4.y:258` (mirrored in generated `snobol4.tab.c:2316`) — `parse_program(LineArray*)` ignores its argument, always returns empty program; zero callers in src/.
- `snobol4.h:29-32` — `SnoLine`/`LineArray` exist solely to feed dead `parse_program()`.
- `test_lex.c` (whole file) — orphaned test scaffold, API mismatch with current token scheme.
- `unicode_alpha_ranges.h` (whole file, 661 lines) — never included.
- `snobol4.l:36` — exclusive lexer state `INCL` declared, no `<INCL>` rule exists — unused state.
- `snocone_lex.h:14-15` — `sc_kind_has_payload(int)` / `sc2_kind_name(int)` declared, never defined, never called. `snocone_lex.c:415-416` unused trailing statics (`sc_name_table[512]`, `sc_name_table_built`).
- `snocone_parse.y:36-64` — 29 consecutive self-referential no-op macros (`#define TT_ASSIGN TT_ASSIGN` …).
- `snocone_parse.y:123,566` — `sc_label_new()` defined, never called.
- `snocone_parse.y:135,712` — `sc_loop_find_innermost()` defined, never called.
- `snocone_parse.y:765-767` — `sc_switch_emit_implicit_break()` empty body, never called.
- `snobol4/Makefile` + `scripts/build_snobol4_frontend.sh` — orphaned divergent build path; only reference each other.

## 3. MISPLACED

- **`scrip_cc.h` is a cross-language shared contract header living under one frontend.** Included by ≥25 files outside its home dir (all other parsers, lower, runtime/core, runtime/builtins, contracts/ast_*, driver). Defines `STMT_t`/`CODE_t`/`ExportEntry`/`ImportEntry` + `ast_stmt_new`/`ast_attr_*`/`stmt_attr_*` API. **Move to `src/contracts/`.**
- `snobol4.h` `SnoLine`/`LineArray` — delete with dead `parse_program()`.
- `unicode_alpha_ranges.h` — wire in or delete.

## 4. SPLIT/MERGE

- No oversized files. `snobol4.h` mixes live lexer API with dead structs — trim.

## 5. VIOLATIONS

- Zero-blank-line rule: all hand-written .h/.c comply.
- 200-char: `snobol4.y` 12 lines over (84,85,95-100,117,181,182,191 — up to 228 chars); `snobol4.l` 2 (264, 414).
- Globals census: `snobol4.l:12-14` non-static `inc_dirs[64]`, `n_inc`, `sno_nerrors` (used from scrip.c, legit pre-existing); `snobol4.y` static `g_lx`, `g_err_lineno`, `g_tal[]` arg-accumulator family; `snobol4.l` statics `strbuf[65536]` etc — NOTE: `%option reentrant` but token payload is shared statics, two concurrent Lex instances would corrupt each other; `snocone_lex.c:30-32` `sc_value_table[512]` etc.
- No LANG_* leakage past lower; no misplaced AST walking.

## 6. DEPENDENCIES

- `scrip_cc.h` included by ≥25 files outside its dir (see §3).
- Root `Makefile:363` adds `-I$(SRC)/parser/snobol4` **globally** — the dir is architecturally a shared-header host.
- **Backward dep**: `snocone_parse.y:33` includes `../icon/icon_lex.h` for `TK_AUG*` token constants (used :352-365). Hoist constants to shared location.
- `snobol4.h` correctly scoped (own dir only).

## 7. NAMING

- `snobol4.tab.c` vs `snocone_parse.tab.c` — inconsistent generated-file basename schemes.
- Three prefix families within snocone alone: `sc_*`, `sc2_*`, `snocone_*`.
- No shared lexer-API naming across frontends (`lex_next` vs `flex_lex_*` vs `sc_lex`).

## 8. GENERATED-FILE STATUS

- Canonical regen path: `scripts/regenerate_parser_and_lexer_from_sources.sh` (covers snobol4+snocone+rebus+raku+pascal) + `scripts/util_style200_oracle_yl.sh`.
- Per-dir `snobol4/Makefile` is a second divergent regen path nothing reaches; its flex invocation omits `--noline` (flag drift vs canonical script).
- snobol4 generated files IN SYNC with sources (token-set diff zero).
- **snocone generated files STALE, proven**: `.y` mtime 2026-08-20 23:06:22 > `.tab.c` 23:03:40; `sc_switch_emit_implicit_break` in `.y`, zero occurrences in `.tab.c`; `sc_loop_find_innermost` body missing from `.tab.c`. Both drifted fns are the dead ones — harmless today, but proof of edit-without-regen.
- Recommendation: keep generated files checked in (project policy), delete orphaned per-dir Makefile + build_snobol4_frontend.sh, regenerate snocone before reorg, fix snocone README.
