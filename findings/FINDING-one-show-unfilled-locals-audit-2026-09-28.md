# FINDING: one-show batch 3 part 2, locals the census calls unfilled (2026-09-28, cto r1 worker)

**Status: NOT CLASSIFIED.** The session ended before any row was read. Below is only the population, taken from `python3 scripts/audit_fixed_caps_census.py --tsv` on 911bb95ff: function-scope locals with an empty fill column and a bound of 16 or more, test files and `src/tools` skipped. Every row still needs its REAL / BOUNDED / DEAD class and one line of evidence. The filter kept only bounds that resolve to a number of 16 or more: that gives 38 rows here, against the coordinator's estimate of about 60. Three more have an unresolved macro bound (41 in all with them), and some example sites (for instance by_name_dispatch.c key[264] near 10037) do not appear under this filter, so re-derive the population before classifying. The seven file-scope rows the coordinator named are listed at the end, also unclassified.

| file:line | name | bound | class | evidence |
|---|---|---|---|---|
| src/ir/frame_layout.c:510 | rb_s | 8192 | not classified | |
| src/ir/frame_layout.c:538 | lv_sbuf | 1024 | not classified | |
| src/ir/frame_layout.c:544 | pool_free | 64 | not classified | |
| src/ir/frame_layout.c:1238 | nm | 16 | not classified | |
| src/lower/lower_icon.c:139 | seen | 256 | not classified | |
| src/lower/lower_snobol4.c:1326 | cb | 130 | not classified | |
| src/lower/lower_snobol4.c:1450 | cb | 130 | not classified | |
| src/lower/lower_snobol4.c:1451 | vb | 130 | not classified | |
| src/lower/lower_snobol4.c:2126 | cb | 130 | not classified | |
| src/parsers/pascal/pascal_sem.c:116 | gp | PAS_SEM_PATH_MAX | not classified | |
| src/parsers/prolog/prolog_lower.c:196 | b2 | 32 | not classified | |
| src/parsers/prolog/prolog_lower.c:361 | pld_seed | 256 | not classified | |
| src/runtime/arithmetic.c:504 | in | 256 | not classified | |
| src/runtime/by_name_dispatch.c:505 | stk | 64 | not classified | |
| src/runtime/by_name_dispatch.c:1227 | rb | 64 | not classified | |
| src/runtime/by_name_dispatch.c:4615 | rb | 64 | not classified | |
| src/runtime/by_name_dispatch.c:4739 | bits | PAS_SET_BYTES | not classified | |
| src/runtime/by_name_dispatch.c:4789 | bits | PAS_SET_BYTES | not classified | |
| src/runtime/by_name_dispatch.c:4884 | a | PAS_SET_BYTES | not classified | |
| src/runtime/by_name_dispatch.c:4884 | b | PAS_SET_BYTES | not classified | |
| src/runtime/by_name_dispatch.c:6659 | nb | 128 | not classified | |
| src/runtime/by_name_dispatch.c:7080 | mloc | 256 | not classified | |
| src/runtime/by_name_dispatch.c:7286 | ba | 64 | not classified | |
| src/runtime/by_name_dispatch.c:7286 | bb | 64 | not classified | |
| src/runtime/by_name_dispatch.c:7855 | _rb | 64 | not classified | |
| src/runtime/by_name_dispatch.c:8628 | stat | 320 | not classified | |
| src/runtime/by_name_dispatch.c:9288 | kb | 64 | not classified | |
| src/runtime/by_name_dispatch.c:9339 | stat | 320 | not classified | |
| src/runtime/by_name_dispatch.c:9351 | pb | 64 | not classified | |
| src/runtime/by_name_dispatch.c:9569 | in_set | 256 | not classified | |
| src/runtime/by_name_dispatch.c:10037 | key | 264 | not classified | |
| src/runtime/by_name_dispatch.c:10044 | key | 264 | not classified | |
| src/runtime/by_name_dispatch.c:10054 | key | 264 | not classified | |
| src/runtime/core/coerce.c:13 | tmp | 64 | not classified | |
| src/runtime/core/coerce.c:24 | tmp | 24 | not classified | |
| src/runtime/core/core.c:3489 | eb | 192 | not classified | |
| src/runtime/core/core.c:3513 | eb | 192 | not classified | |
| src/runtime/icn_extfn.c:177 | slots | 64 | not classified | |

## File-scope rows named by the coordinator (not classified)

| file:line | name | class | evidence |
|---|---|---|---|
| src/emitter/emit.cpp:281 | ops[6] | not classified | |
| src/runtime/builtin_ids.h | g_bid_tab[BID_TABSZ] | not classified | |
| src/runtime/pattern_match.c | k_one_char_str[513] | not classified | |
| rt_coexpr | regs[7] | not classified | |
| src/runtime/rt/rt_slab.c | k_bytes[NKLASS] | not classified | |
| x86_arg_roles.cpp | x86_argroles[123] | not classified | |
| gen_runtime.c | g_scan_empty[1] | not classified | |
