# Survey 07 — src/templates xa_* + x86_asm.h encoder (agent report, condensed verbatim)

## 1. INVENTORY
| Path | LOC | Verdict |
|---|---|---|
| x86_asm.h | 2239 | LIVE — sole emission point |
| x86_arg_roles.h | 126 | LIVE, single consumer (x86_asm.h:1328) |
| xa_template_common.h | 7 | LIVE trivial umbrella |
| xa_templates.h | 23 | LIVE, included only by emit.cpp |
| xa_flat.cpp | 429 | LIVE load-bearing (flat/zframe/chain/dc-stub prologues+epilogues) but contains worst emission violations (dead cluster, §3) |
| xa_coexpr_entry.cpp | 15 | LIVE (used by bb_create.cpp) |
| xa_csettab_rodata.cpp | 29 | LIVE (TEXT-only rodata) |
| xa_strtab_rodata.cpp | 30 | LIVE (TEXT-only rodata) |
| ALL OTHER 13 xa_*.cpp (bb_macro_library 61, bb_ptr_slot 22, cap_fixup 22, epilogue 26, exec_stmt_blob 7, expression_registry 20, file_header 26, js_label_register 16, macro_library 22, pattern_blobs 14, prologue 105, stubs 6, wasm_main 21) | ~370 | **DEAD** (§4) |

## 2. x86_asm.h MAP (2239 lines)
1-114 ports/regs · 115-322 primitive BINARY/TEXT dual encoders · 323-425 RTCC r8-r11 clobber-veneer · 427-594 jcc table + α/β/γ/ω control-flow core + TGT0/TGT1 · 595-753 numbered labels, forth-cell early-exit, external-label-by-ptr, sealed rip-slots · 756-1209 LARGEST: frame/ζ operand addressing, x86_zop regime dispatcher, ZTOS/ZRES/ZLOC/ZOP*, zone family ZREF*/LFC/AFC/CFC/FFC/CROQ, reg+disp32, abs-VA · 1210-1320 xop/opnd tagged-union + x86_parse() string-sniffing parser · 1326-1457 TEXT 4-column formatter + arg-role annotator · 1458-1709 **x86_core_** single dispatch (unhandled operand pairs abort loudly — ZB-FC-1 anti-silent-drop invariant) · 1710-2031 composite glue FROM x86(...) incl. x86_port_hook · 2032-2100 ZDP teardown + ZSM events · 2101-2219 x86_bomb, fn-cell jumps, PAIR dual-entry, 2-retval RTCC calls · 2221-2238 bb_emit_x86 BINARY tape interpreter (L/J/D/Q/E/F/X/Y tags).

Coverage: ~40 bespoke mnemonics, purpose-built, no general table.

**Split recommendation**: 3 headers re-exported through umbrella x86_asm.h (134 include sites untouched): x86_encoders.h (1-425 + 756-1209), x86_operand.h (1210-1709 + formatter + x86_arg_roles.h), x86_glue.h (427-753 + 1710-2239). Do NOT split further; x86_core_ must stay one switch for the abort-loudly invariant.

## 3. EMISSION AUDIT (repo-wide raw-byte census outside x86_asm.h)
- **xa_flat.cpp:54-122 — VIOLATION, not granted**: nine static fns (xaf_push_frame, xaf_pop_frame, xaf_ld64_from_zr8, xaf_lea_rsp_zr32, xaf_frame_store_imm32, xaf_frame_rsp_rm, xaf_ld64_rsp, xaf_addq_rsp, xaf_add_rdi_imm_bin) hand-encode REX/ModRM/SIB (`bytes(3,"\x48\x89\xEC")`, u32le, manual 0x80| math). Mitigating: **whole cluster dead** — zero call sites beyond one intra-cluster call. Delete.
- emit_str.cpp:19-22,46-51 — u8/u32le/u64le/bytes DEFINED here, consumed by x86_asm.h (infrastructure); bomb_bytes = the documented exception but has **zero callers repo-wide** (superseded by x86_bomb, x86_asm.h:2121). u8() itself: zero callers anywhere including x86_asm.h.
- No other raw-byte producers anywhere in src/. Discipline holds except the dead xa_flat cluster.

## 4. DEAD PARTS
- **xa_dispatch() (emit.cpp:356ff) has 18 arms; only 3 ever invoked** (call sites: emit.cpp:425 XA_STRTAB_RODATA, :475 XA_CSETTAB_RODATA, :3184 XA_FLAT_DATA_SECTION). The other 15 arms + their functions (xa_file_header, xa_file_footer, xa_prologue, xa_epilogue, xa_bb_ptr_slot, xa_entry_dispatch, xa_cap_fixup, xa_pattern_blobs, xa_macro_library_open/close, xa_exec_stmt_blob, xa_bb_macro_library, xa_wasm_main_open/close, xa_js_label_register, xa_expression_registry) unreachable — zero call sites repo-wide. **The real mode-4 file header/main: prologue is hand-inlined via emit_textf in scrip.c (~1297, 1485)** — an undocumented duplicate of what xa_file_header/xa_prologue claim to produce.
- g_platform assigned 3× repo-wide, always BB_PLATFORM_X86; driver rejects --target≠x86 (scrip.c:1591). xa_wasm_main + xa_js_label_register doubly dead (driving state xa_expr_count, hdr_has_expr_reg, xa_label_* never written).
- No #if 0 anywhere in scope.

## 5. MISPLACED
- **Move x86_asm.h + x86_arg_roles.h + xa headers + surviving xa_*.cpp into src/templates/x86/ subdir**; bb_*.cpp stay above. x86_asm.h has ZERO includers outside templates/ — already templates-private foundation.
- Delete the 15 dead xa_ arms + files rather than migrate.

## 6. VIOLATIONS
- MEDIUM_* in bb_*.cpp: zero (rule holds). In xa_: 4 files gate on MEDIUM_TEXT/BINARY/MACRO_DEF (csettab:10-12, strtab:10-12, flat:21-23,44,126-128) — legitimate TEXT-only rodata dumps; rule scoping worth making explicit.
- Blank lines: zero in x86_asm.h/x86_arg_roles.h/all xa. (bb_assign_global.cpp:31,69 whitespace-only pair noted.)
- LANG_*: zero in templates/ + emitter/.

## 7. DEPENDENCIES
- x86_asm.h included by 134 files, ALL inside templates/. x86_arg_roles.h: 1 includer (x86_asm.h). xa_templates.h + bb_templates.h: single external includer = emit.cpp (the one emitter↔templates seam).
- xa_coexpr_entry.cpp uses bb_template_common.h (odd one out, bb-adjacent, feeds bb_create.cpp).

## 8. NAMING — the three-tier convention (keep + document)
- bb_* = one file per IR node kind, α/β/γ/ω body via x86(...).
- xa_* = program/graph-shape scaffolding (per-compile or per-procedure, never per-node) — verified empirically.
- x86_* = ISA/encoder layer.
- xa_flat.cpp (429) doing 4 scaffolding jobs → split by idiom (xa_flat_zframe/chain/dc) after dead-cluster removal.
