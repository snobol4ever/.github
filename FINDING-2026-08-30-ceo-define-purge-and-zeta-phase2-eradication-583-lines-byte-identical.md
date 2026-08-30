# FINDING 2026-08-30 (ceo) — Lon's #define purge + zeta phase-2 eradication landed together: 41 files, 583 lines deleted, four witness .s byte-identical, census 62 → 1

**Orders, verbatim in substance (Lon, in-chat to ceo, 2026-08-30):** *"The SCRIP has too many #defines. Remove the unneeded ones. The ones that are not useful for debugging or telemetry. Keep ones that have reasonable choices for varying features. We had so many experiments that created these, that most can just be removed."* Then: *"Take seat09's and finish the job once and for all"* — row `zeta-choice-shape-eradication-phase2` reassigned seat09→ceo via the verb and driven to its DONE-WHEN bar in the same landing.

## The purge (measured, not assumed)

- **Census instrument:** every `#define` name in `src/` (1,414 distinct), readers counted across `src/` + `scripts/` + `Makefile` (gates grep macro names; `rtx/*.s` is cpp-assembled — both are real readers), include-guards and flex/bison generated output (`*.lex.c`, `*.tab.*`, `lex.rebus.c`) excluded, `zeta_choices.h` initially fenced off for seat09's row.
- **315 names had zero readers**; ~200 of those were generated-parser boilerplate (left alone — they regenerate). **167 hand-written dead defines deleted** across 22 files, each re-verified by whole-repo word-boundary scan immediately before its edit, plus a token-paste (`##`) family check (zero hits). The nests are exactly the experiment residue named in the order: **78 raw-x86 encoding macros in `emit.h`** from before the `x86(...)`-only discipline (`MODRM_*`, `REX_*`, `JMP_REL8`, …), **26 SIL-era macros** (`sil_macros.h` — file kept, 15 includers), **13 runtime shims**, `EMIT_PAIR_*`/`RESOLVE_IDX_*` families in `emit.cpp`/`emit.h`, the self-holding `aref`/`aset`/`INDEX_fn` cluster (alive only via their own `#undef` lines). All 15 debug/telemetry-named defines kept per the order.
- **No hand-written never-defined `#ifdef` switches exist** — census 2 (conditional names never defined anywhere, minus compiler builtins and Makefile `-D`) returned only bison/flex boilerplate. The zeta eradication (s270, SCRIP 6da13973) had already killed that class. Makefile carries exactly one real feature `-D`: `WITH_CSNOBOL4`.

## Zeta phase-2 (seat07's Commit A + the ZC_ZETA_ZH subsystem + full accessor eradication)

- **Commit A landed as scoped** (all five verified-by-construction collapses: `rfc()`/`hfc()` in match_end/match_begin, the `bb_glue_flat` storage tautology, `lower_snobol4.c:1943`, the `ZC_HEAP_STRINGS` telemetry field), plus `bb_match_defer`'s `dswap()`.
- **The dead ZC_ZETA_ZH subsystem is gone wholesale** (seat07's census-invisible find, executed exactly per their ledger): both `rt_zeta_mode()==ZC_ZETA_ZH` blocks in `rt.c`, the two literal-`2` guards in `by_name_dispatch.c` (functions collapse to their live `plw_cw_*` call; `plw_zhpair_t`/`g_plw_zhp*` orphans deleted), **`zeta_heap.c`/`.h` deleted with their Makefile line**, `rt_zh_bump_slow(_addr)`/`x86_zeta_mode`/`rt_zeta_mode` all zero-caller-verified then deleted. ⛔ The landmine honored: **`g_zeta_mode` and `ZC_ZETA` survive untouched** — `bb_call_fn.cpp:375` bakes the global's address into emitted code; whether that codegen mechanism is itself dead stays a separate uninvestigated question.
- **Every choice accessor is gone**: `x86_zc_frame`/`x86_port_mode`/`x86_zstorage`/`x86_port_cstack`/`rt_zc_frame_live`/`rt_zeta_port_mode`/`rt_zeta_storage_get`/`rt_zeta_cstack` — ~40 call sites collapsed to their always-taken arm (emit.cpp 20 collapses incl. the wholly-dead `emit_zeta_selfload()` with its raw `ef_b2/ef_b3` bytes — a raw-byte producer outside `x86_asm.h` gone as a bonus; scrip.c's dead 65536-byte legacy-frame arms; staged-call's dead `is_dyn`/frame-sink ternary arms). The always-false arms were DELETED, not folded.
- **`zeta_choices.h` is 11 lines**: the six size constants, the two ZLS2 op bits, `ZC_ZETA`. The `ZC_*` ζ-cell-KIND enum in `x86_asm.h:1071` (unrelated family, overloaded prefix) untouched per the DONE-WHEN's exclusion.
- **Row DONE-WHEN census: 62 → 1** (`zeta_alloc.c:145`, the g_zeta_mode initializer — inside the ≤2 bar). ZLS dump keeps its title + ARENA_MB; the "choices:" banner and its three name arrays are gone — a dump that names a menu that no longer exists is the choice remembering itself.

## Honesty arms

- **Four witness `.s` byte-identical** across the whole landing (fibonacci.sno, array_sum.sno, bench_icnint_loop.icn, cal.pl — pre-purge snapshots from a pristine baseline vs the final tree): every collapsed guard was genuinely always-taken; nothing semantic moved. Per the row's law, a byte-different .s would have reverted that collapse.
- **Floor:** pristine + `test_corpus_snobol4.sh` + both live gates + icon/prolog/snocone/rebus smokes + a real-backtracking Prolog witness (crypt.pl) — the by_name_dispatch trail-path blast radius per seat07's battery note. Results in the landing commit / cursor.

## Deliberately not done

- Generated flex/bison defines (regenerate; churn).
- `SCRIP_OPT=0` / `SCRIP_ZD=0` env switches — Lon's order was #defines; those flags are seat10's live root-cause row, and the working-bypass-or-delete question is with Lon.
- The r12/`g_zeta_mode` codegen-liveness investigation (own future row if wanted).
