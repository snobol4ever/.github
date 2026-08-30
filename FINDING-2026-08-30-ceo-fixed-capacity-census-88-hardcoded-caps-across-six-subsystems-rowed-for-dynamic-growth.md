# FINDING 2026-08-30 (ceo, Lon direct) — Fixed-capacity census: every hard-coded table cap in src/, classified, and rowed for dynamic growth

Lon's order, verbatim in substance: *"Make note of all the CAPS... Make tasks to fix each and every FIXED array of this type which should really be dynamic versus static."* Trigger: the gprolog 60-module compiland died on four successive `zls:` overflow walls the same day. Census instrument: `#define *MAX*/*_CAP*` grep over `src/` plus an enum/bare-bracket sweep (which found 26 MORE fixed arrays carrying no `#define` at all — e.g. `PL_DET_MAX 4096`, `PL_INIT_GOALS_MAX 256` as enums in lower_prolog.c — so every row below carries a census-completion step for its own files; the define grep alone undercounts).

## NOT caps — excluded, with reasons (so nobody re-litigates them)
- `YYMAXUTOK` (all .tab.c): bison token-id bound, semantic, not a capacity.
- `ZC_CSET_CHAIN_MAX 3` (zeta_choices.h): a design choice constant, not a table size.
- `TBL_LINEAR_MAX 12` / `TBL_LOAD_MAX 4` (aggregates.c): tuning thresholds of an ALREADY-dynamic table.
- `ATOM_INIT_CAP 256` / `TRAIL_INIT_CAP 64` / `NFA_INIT_CAP 64`: initial sizes of grow-on-demand structures — these are the house EXEMPLARS of the desired pattern (realloc doubling, loud abort only on allocator failure).
- `BB_LABEL_NAME_MAX 80`: a name-length buffer, included in the emitter row but flagged as string-buffer class, not table class.

## THE CAPS — every fixed table, by owning row (rank 2 each, minted this sitting)
**`zls-tables-static-caps-vs-dynamic`** (existed since this morning; EXTENDED to cover the whole ir/ layer): ZLS_MAX_ENTRIES 262144 · ZLS_MAX_FIELDS 524288 · ZLS_MAX_SCOPES 16384 · ZLS_MAX_GRAPHS 16384 · ZLS_MAX_VSLOTS 16384 · ZLS_MAX_MARKS 262144 (zeta_storage.c) + ZDP_CAP 8192 (zeta_depth.c). Acceptance witness: the 60-module gprolog compiland.

**`emitter-fixed-caps-to-dynamic`**: emit.cpp — AB_FNCELL_MAX 1024 · WASM_STRTAB_MAX 4096 · WASM_USERFNS_MAX 256 · WASM_MAX_PARAMS 16 · PL_CATCH_MAX 64 · SMX_STRTAB_CAP 8192 · SMX_CSETTAB_CAP 256 · FLAT_CHAIN_SET_MAX 512 · FLAT_DATA_LBL_MAX 32 · CHILD_CACHE_MAX 64; emit.h — BB_PATCH_MAX 65536 · XA_BB_EMIT_PAIR_MAX 1024 · BB_LABEL_NAME_MAX 80 (string-buffer class).

**`lower-fixed-caps-to-dynamic`**: ICN_LOOP_STK_MAX 64 (lower_icon.c) · PAS_MAX_SCOPE 64 (lower_pascal.c) · RK_GRAM_MAX 64 (lower_raku.c) · SNO_DEF_MAX 128 · SNO_DEF_NAMES_MAX 64 · SNO_EXPR_MAX 4096 · SNO_PAT_MAX 256 · SNO_FZW_MAX 256 (lower_snobol4.c) · SNO_LOOP_STACK_MAX 64 (tree_to_sno.c) · PL_DET_MAX 4096 + PL_INIT_GOALS_MAX 256 (lower_prolog.c, enum-declared).

**`parser-fixed-caps-to-dynamic`**: prolog — TERM_STACK_MAX 512 · TR_SLOT_MAX 256 · PL_MAX_CLAUSES 2048 · MAX_PREDS 512 (prolog_lower.c) · MAX_VARS 256 · IF_STACK_MAX 32 · TS_MAX_VARS 256 (prolog_parse.c); pascal — PAS_REC_MAX 512 · PAS_FIELD_MAX 32 · PAS_NEST_MAX_PV 16 · PAS_LOCAL_MAX 64 · PAS_NEST_MAX 16 · PAS_WITH_MAX 8 (pascal.tab.c user blocks); raku — RK_ARRNAME_MAX 256 · RAKU_METH_MAX 256 (raku.tab.c) · MAX_STATES 512 (re.c) · MAX_GROUPS 16 (re.h); snobol4 — MAX_INCL_NEST 64 (lex) · TAL_MAX 512 (tab.c); icon — ICN_STACK_MAX 256 (icon_runtime.c). ⚠ .tab.c caps live in grammar user blocks; grammar REGEN is blocked (row bison-pkgdatadir-missing...) so edits land in .tab.c AND the .y source in the same commit.

**`driver-fixed-caps-to-dynamic`**: SC_DAT_MAX_FIELDS 64 · SC_DAT_MAX_TYPES 1024 (driver_data.c) · FH_MAX 64 (driver_globals.c + driver_private.h, ONE cap in two files) · CALL_STACK_MAX 256 · SHADOW_MAX 32 · INIT_MAX 64 (driver_private.h).

**`runtime-fixed-caps-to-dynamic`** (the big one, and the careful one — hot paths, rtx asm twins): gen_runtime.h — FRAME_DEPTH_MAX 16 · FRAME_STACK_MAX 256 · EVERY_GEN_SLOT_MAX 16 · SCAN_STACK_MAX 16 · GLOBAL_MAX 4096; resolution.c/h — RESOLVE_CP_STACK_MAX 4096 · RESOLVE_CATCH_STACK_MAX 64 · RESOLVE_SCOPE_SLOT_MAX 64 · RESOLVE_BB_TABLE_MAX 256; by_name_dispatch.c — GRAMMAR_MAX 128 · RK_NAMED_MAX 32 · RT_SYN_MAX 64; core.c — CLEAR_MAX_EXCEPT 64 · DATA_MAX_TYPES 64 · DATA_MAX_FIELDS 16 · NSTACK_MAX 256 · NHOME_MAX 256 · VSTACK_MAX 1024 · TRACE_SET_CAP 256 · IO_CHAN_MAX 32; name_binding.c — STATIC_MAX 256; pattern_match.c — RT_XPAT_CHAIN_MAX 256 · RT_CAS_SPK_MAX 256; rt.c — EXPRESSION_REG_MAX 256 · RT_DC_FNS_MAX 8192 · RT_MAX_CAPTURES 256 · RT_FRAME_STACK_MAX 256 · RT_FRAME_SLOT_MAX 64 · CALL_ARGS_MAX 64 · RT_INITIAL_MAX 8192; rt_runtime.c — BB_DCAP_MAX 32 · SAVE_MAX 4096 · SEQ_CACHE_MAX 64 · SUSP_GEN_CACHE_MAX 64; unification.c — RT_MARK_STACK_MAX 32; bbprof.c — BBPROF_PC_CAP 2048.

## Laws that bind every one of these conversions (stated once, cited by each baton)
1. **Loud refusal survives**: today every overflow aborts with a named message — the conversion may only move the abort to allocator failure. A silently-truncating "dynamic" table is worse than any cap.
2. **No-new-globals**: converting `static T arr[N]` to `static T *arr; static int cap;` re-types EXISTING file-scope state, adds no new global cell — inside the law. A conversion that wants a genuinely NEW global follows the banner procedure.
3. **Runtime hot paths**: any table an rtx_*.s twin or the asm/C equivalence comments touch (rt.c, by_name_dispatch.c) must keep its access shape or update the twin in the same commit — the length-authority precedent (fix the consumer, never quietly change the helper).
4. **Emitted-code contracts**: a cap whose value is baked into emitted code as an immediate (the `add rsp, N` class hq_C flagged on calling-convention work) is NOT a plain table and needs its own design note before conversion.
5. Every row sweeps its own files for enum/bare-bracket fixed arrays beyond this census (26 known to exist).

Queue: 5 new rows + the zls extension, all rank 2, batons carry their cap lists verbatim. Trees: census at SCRIP `89d4e38a`.
