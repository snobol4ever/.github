# Survey 02 — src/lower (agent report, condensed verbatim)

## 1. INVENTORY
| Path | LOC | Purpose | Verdict |
|---|---|---|---|
| `lower.h` | 59 | Shared lowering API: `lc_*` helpers, per-language `lower_*_stage2` entries, `binop_apply` decl | LIVE (spine header) |
| `lower_snobol4.h` | 7 | Sole prototype for `tree_to_sno()` | LIVE (misfiled) |
| `lower_common.c` | 300 | γ/ω wiring primitives, `lc_vec`, label registry, src-line notes, `binop_apply` const-fold evaluator | LIVE — the real spine |
| `lower_snobol4.c` | 2611 | SNOBOL4 expr/stmt lowering + entire SN4-PAT pattern lowering subsystem + DEFINE/program assembly | LIVE, MIXED (3 concerns) |
| `lower_icon.c` | 1399 | Icon expr/stmt/generator lowering, scan boxes, call-kind resolution | LIVE |
| `lower_prolog.c` | 1381 | Prolog goal/clause→IR, determinism analysis, findall desugaring, indexing | LIVE |
| `lower_raku.c` | 1011 | Raku lowering, grammar/class registration | LIVE |
| `lower_pascal.c` | 840 | Pascal proc/scope lowering, nested-proc upvalue capture | LIVE |
| `tree_to_sno.c` | 730 | `--transpile`: AST→SNOBOL4 text, zero IR_t usage | LIVE, MISPLACED |
| `lower_snobol4.gz5-parked-41b53078.c` | 1327 | Pre-GZ5-purge SNOBOL4 lowering (old tree-walker) | PARKED — not built, zero external refs; feature-recovery reference |

- Prolog boundary: `parser/prolog/prolog_lower.c` (866 lines) is a DIFFERENT stage despite its name — Term*/PlProgram* → tree_t* AST desugaring (bagof, var slots, ;/-> rewrite), never touches IR_t. `lower/lower_prolog.c` is the real IR-lowering half.
- No lower_snocone/lower_rebus: rebus has `parser/rebus/rebus_lower.c` (includes lower.h); snocone routes through the SNOBOL4 path via shared tree_t shapes. `tree_to_sno.c` is not a lowering path for any frontend.

## 2. DEAD PARTS
- `lc_call_argblks` (`lower_common.c:241`, decl `lower.h:48`) — zero live callers; only caller is the PARKED file. Dead in current build.
- The parked gz5 file entirely (not in Makefile, never included, name appears nowhere in src/ or scripts/). `IR_LANG_SNO`/`LANG_SNO`/`:lang` usage exists ONLY inside it — live code has zero (rule compliant).
- No `#if 0` blocks in live lower files.

## 3. MISPLACED
- **`tree_to_sno.c` → out of lower/** (to driver/ or a transpile/ home; `lower_snobol4.h` moves with it). Invoked directly from `scrip.c:1071-1072` on raw AST, bypasses lower/optimizer/emitter.
- **`binop_apply` (`lower_common.c:67-176`) → runtime/**: pure DESCR_t const-fold interpreter; only real caller `runtime/rt/rt.c` (2 sites); nothing in lower/ calls it.
- **`#include "emit.h"` in lower_common.c:4, lower_icon.c:1207, lower_prolog.c:6 → delete**: zero symbols used; vestigial backward dep (lower→emitter).
- **TK_AUG* tokens** defined in `parser/icon/icon_lex.h`, consumed by lower_snobol4.c and tree_to_sno.c for SNOBOL4 TT_AUGOP — hoist to contracts/.

## 4. SPLIT/MERGE
- lower_common.c is genuinely the spine (lc_build/lc_γ_to/lc_ω_to; shared label registry).
- **lower_snobol4.c split into 3**: (1) sx_lower expr/stmt ~1-900; (2) SN4-PAT pattern subsystem ~900-1900 (~1000 lines, ~15 file-scope caches g_sno_fz*/seal*/t4*/pro*/encl*) → `lower_snobol4_pattern.c`; (3) program/DEFINE assembly + stage2 registration ~1900-2611 → `lower_snobol4_program.c`.
- Per-language `register_program()` duplication (~20-30 near-identical lines ×5) → shared `lc_register_program()` would cut ~120 lines.
- 5 identical per-language `build()` wrappers — macro in lower.h could collapse.

## 5. VIOLATIONS
- Backward dep: unused emit.h includes (3 files, see §3).
- 200-char lines: lower_snobol4.c **69**, lower_prolog.c 17, lower_icon.c 9, parked 8, lower_pascal.c 4, lower_raku.c 1, rest 0. Blank lines: 0 everywhere.
- PEERS: compliant (zero BB_t refs in lower/; ir_operand_push only).
- No LANG_* downstream: compliant in live files.
- **`sno_lower_fragment_at()` (lower_snobol4.c:2585-2603) calls optimizer_run() + ir_drive_slot_assign() directly** — lower reaching forward past its stage; load-bearing for runtime CODE()/EVAL() fragment compilation, but a real exception to "one path".

## 6. DEPENDENCIES
- lower.h: 11 external includers (driver ×5, parser/prolog ×4, parser/rebus, runtime ×3). `lower_snobol4.h`: exactly 1 (tree_to_sno.c itself).
- Legit downward: contracts/bb_program.h, contracts/stage2.h.
- Runtime reach-in: scattered `extern` hooks into runtime/builtins (global_register, record_register, rt_dat_field_of_any, rt_builtin_is_known, …) instead of a consolidated header — noisy, not a violation.
- No templates/x86_asm.h includes anywhere in lower/ — clean.

## 7. NAMING
- `pl_` prefix = Prolog in lower_prolog.c but reads ambiguously vs Pascal; Pascal uses `pas_`.
- `lower_sno_stage2` vs file `lower_snobol4.c` — only language whose stage2 entry abbreviates differently from filename.
- "lower" used for two different stages (parser/prolog/prolog_lower.c AST-desugar vs lower/lower_prolog.c IR-emit) — confusing.
- gz5-parked hash suffix churns across reactivations — docs hardcoding it rot.
