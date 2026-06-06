# HANDOFF 2026-06-06 — BB-FIXUP 4th attended run: LAP 1 stops 12–14 + BUILTIN RENAME (Opus 4.8)

## Commit ledger (SCRIP, all pushed, oldest first)
| Commit | Unit |
|--------|------|
| 5e4141c | FIXUP bb_findall (then bb_builtin_findall): ef 4→0 pe 1→0 lv 2→0 (bff_goal helper); 13→6+pe |
| d7ea5f3 | FIXUP bb_io: ef 6→0 pe 4→0 lv 8→0 (bio_succ/bio_write_body/bio_fbits_str/bio_bin_write_arg); 51→30 |
| 7f3384d | REPAIR stops 12–13: BINARY ports `_.lbl_*` → literal Greek glyphs + stop-13 tracker annotation (prior replace was a silent no-op — match exact bare lines, assert in python) |
| 75662d3 | RENAME family: 11 arms bb_builtin_X → bb_X (+_str), bb_builtin_common.h → bb_common.h, dispatcher bb_builtin.cpp → bb_resolve.cpp (extern bb_resolve; RESOLVE_BUILTIN→RESOLVE emitted comment), Makefile + 4 gate scripts + tracker |
| b633af1 | RENAME bb_call_builtin → bb_call_fn (collision-avoiding; Icon canon: builtins are functions, pairs bb_call_userproc) |
| 10b83cf | FIXUP bb_is_cmp: ef 39→0 pe 2→0 lv 28→0 (icm_arith/ord/cmp/op/tail/k/i/fb/floaty helpers, V-2 prose purged); 121→64; asm-diff EMPTY on LIVE arms |

.github: 4b8b7cf9 watermark (superseded by this handoff's prune commit).

## ⛔ THE PORT BUG (read before touching any pe count in a BINARY arm)
Stops 12–13 initially swapped `x86("jmp", PORT_GAMMA)` → `x86("jmp", _.lbl_γ)` in MEDIUM_BINARY arms. `x86_parse` (x86_asm.h): a 2-byte Greek glyph (s[2]==0) → XK_PORT → real Lrec(0xE9)+Jrec(port) record; any other string → XK_SYM, and the jmp/def XK_SYM branches are `!MEDIUM_BINARY`-guarded → **BINARY emits empty string**. Mode-3 jumps silently vanished while every gate stayed green (corpus fires the resolve family mode-4 only; the asm-diff was TEXT). Caught by reading the parse path before propagating the pattern into the rename. Sanctioned form (bb_arith precedent, pat-rung-proven): literal `"γ"` `"β"` `"ω"` strings in BINARY arms; `_.lbl_*` in TEXT arms only. Now a permanent ⛔ block in GOAL-BB-FIXUP.md.

## RENAME state
- BB template layer: zero `builtin` in any file/symbol name. Dispatcher = `bb_resolve.cpp` / `extern "C" void bb_resolve` (IR_BUILTIN wiring in emit_core.c updated). `bb_call_fn.cpp` named per Icon canon.
- Tracker ring kept DOCUMENT ORDER (re-sorting mid-lap scrambles the lap); re-sort at lap end on Lon's word.
- RESIDUE = runtime/contracts layers where "builtin" names language builtins: `rt_call_builtin`, `rt_builtin_is_known`, `src/runtime/builtins/`, `by_name_dispatch`, `IR_BUILTIN`, driver/interp hooks, generated parser `.tab.c`, `backends/runtime/js`, `is_builtin` local in HOT bb_call.cpp. Sweeping those = RUNTIME RENAME / LI-CORE territory — Lon decides.

## State at close
- `# CURSOR: bb_list.cpp` (06-04 snapshot eb=8 nw=6 rb=39 ef=22 pe=2 lv=23 — renamed file, RE-AUDIT on arrival).
- Lap metric 1656→1586; 93 files (bb_pat_breakx joined via 7a24653 SNO-HY-1) / 83 dirty / 10 clean; emit-blind 219 (stop-14 de-aliasing raised eb/nw honestly — reads were always there, now counter-visible).
- Gates at floors: smoke 19/0 · pat-rung M2=18/M4=18 (053_pat_alt_commit M2-fail pre-existing) · prove_lower2 67/67 (note: its tables print `PFAIL` sentinel rows — grep `"; PASS"` or rc, not bare FAIL) · purity 2-floor · bb_bin_t 0 · sno_pat_reg TIER1+TIER2 HARD (TIER2 flipped HARD by ba7622c) · vstack 3 · one_box PASS.
- icn_scan/icn_var fences need `/home/claude/corpus` cloned or their corpus buckets floor-fail spuriously (probes all pass). Not in the FIXUP battery; only relevant if touching Icon families.
- Concurrent landings merged green ×4: ba7622c, 3ec6470, 1ad0019, 7a24653. Main is busy — law 3 (pull/push every file) earned its keep.

## Next session
Standard open ("here we go") → LOOP at `bb_list.cpp`. FIX-3 (bb_call family) = next pinned-pending TIER S, design NOT pinned, flag on arrival; bb_call.cpp profile changed 3× today (PB-9f, PB-10b, ICN-HY-7c) — trust nothing but a fresh audit.
