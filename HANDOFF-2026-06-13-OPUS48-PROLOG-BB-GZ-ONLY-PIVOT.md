# HANDOFF — 2026-06-13 · Opus 4.8 · Prolog BB — GZ-ONLY PIVOT (delete the old way)

## Watermark
SCRIP `(this commit)` · .github `(this commit)` (both build green).
**m2 114/115 · m3 89/115 · m4 48/115.** Ratchet floors RESET → m3 89, m4 48 (deliberate, per Lon's pivot).

## Gates
GATE-1 5/5/5 ✓ (HARD m2 gate intact). GATE-3 m2=114, m3=89, m4=48.
SNOBOL4 7/7/7 ✓ · Icon m2 12 / m3 10 / m4 10 ✓ (shared `x86_asm.h` + `emit_bb.c` touched — verified no other-language regression).

---

## What happened this session (two parts)

### Part 1 — rung29 float bug → `movq xmm,r64` both-medium fix (landed, then superseded for m4 by Part 2)
Root-caused rung29_float_constants m4 (`Y is exp(1.0)` → `1.0` instead of `2.718…`):
- `pi`/`e` lower to **IR_ATOM** (not IR_ARITH), so `X is pi` is NOT GZ-admitted → the whole clause dropped to the **flat tier** (`rt_is_cell`, `bb_is_cmp.cpp`).
- `rt_is_cell` is shared runtime C, so m3 (BINARY) computed `exp(1.0)` correctly; m4 (TEXT) returned `1.0`.
- The divergence: the `x86()` dispatch in `x86_asm.h` had **no `movq` arm** → `x86("movq","xmm0","rax")` returned EMPTY in TEXT (the "silent-empty fallthrough" the goal file flagged). The float bits in `rax` never reached xmm0 → `exp(0)=1.0`. BINARY hand-encodes the bytes (`\x66\x48\x0F\x6E\xC0`) in `icm_bin_is_cell`, so m3 was right.
- **Fix:** added `x86_movq_xmm_r64(dst,src)` + a `movq xmm,r64` dispatch case in `x86_asm.h`. Covers all 9 `x86("movq"...)` sites (all `xmm0/xmm1,rax`). Both-medium correct; also used by `bb_io.cpp`.
- This gave rung29 m4 +1 (87→88). **Part 2 then erased that** (rung29 isn't GZ-admitted). The encoder fix is KEPT — it's correct, shared, and on the GZ instruction layer.

### Part 2 — GZ-ONLY pivot (Lon's directive: "DELETE the old way and take the hit. Leave only our future.")
Both Prolog dispatches are now **GZ-ONLY**. This SUPERSEDES the C-FRAME B-1/B-2/B-3 ladder — we deleted the rich path rather than fixing its m4 GZ-TEXT compound-term emit.

**Dispatch (scrip.c):**
- m3 `--run`: `pl_gz_admit` → `pl_gz_build`, else loud `[PL-GZ FENCE]` abort. (Flat fallback removed.)
- m4 `--compile`: `pl_gz_admit` → `pl_gz_codegen`, else loud `[PL-GZ FENCE]` return 1. (Flat + rich fallback block removed.)

**Source deleted (build green at each step):**
- scrip.c: `pl_flat_body_root`, `pl_rich_node_emittable`, `pl_rich_graph_ok`, `pl_rich_body_root` (~135 lines).
- emit_bb.c: `codegen_graph_block`, `codegen_callee_block`, `pl_catch_collect_graph`, `codegen_pl_catch_blocks`, `codegen_clause_dispatch`, `codegen_pl_pred_table` (~132 lines).

**Kept on purpose:**
- `bb_build_flat` / `codegen_flat_build` / `gvar_flat_chain_build` — SHARED with SNOBOL4/Icon. Do not delete.
- A 4-line `pl_catch_block_index` stub (+ `g_pl_catch_nodes`/`g_pl_catch_n`) in emit_bb.c so the now-unreachable `bb_catch.cpp` template still links (returns -1; never reached since catch isn't GZ-admitted).
- `g_gz_no_struct_ptr = 1` in the m4 dispatch — LEFT AS-IS. Lifting it routes struct programs onto the GZ cell path where they **segfault** (m4 GZ-TEXT compound build is broken, the old C-FRAME B-1), which is worse than a clean abort. So m4's GZ stays narrower than m3's (this is why m4=48 ≪ m3=89 even though both are "GZ-only").

## The hit (deliberate)
| Mode | pre-pivot | post-pivot | Δ |
|------|-----------|------------|---|
| m2 (interp, KEEP) | 114 | 114 | 0 |
| m3 (--run) | 91 | 89 | −2 (flat tier carried only 2 beyond GZ — m3 is essentially pure-GZ already) |
| m4 (--compile) | 88 | 48 | −40 (flat + rich/heap-env tiers were carrying these) |

GATE-1 HARD gate (5/5/5) holds. This is a legitimate green commit with intentionally lowered *tracked* scores, not a broken build.

---

## NEXT SESSION — remaining old-way demolition (all currently dead-but-compiling, harmless)
The old way is already **unreachable** (dispatch is GZ-only). What remains is physical removal of dead code:

1. **Control-coupled templates → stub to loud bombs** (GUT-list "control-coupled bb_goal/bb_choice/bb_catch"): `bb_goal.cpp` (uses 8× `resolve_bb_env_*`), `bb_choice.cpp`, `bb_catch.cpp`. The GZ path uses the `bb_cell_*` boxes instead. Stubbing these is what unblocks step 2.
2. **`resolution.c` control engine + `resolve_bb_env_*`** — ENTANGLED with the KEEP files `unification.c` (9 refs) and `rt.c` (1 ref). After step 1, the `resolve_bb_env_*` callers are only resolution.c (3) + unification.c (9, mostly internal). Gut the GDE control engine; keep what the GZ path still calls (`rt_findall`, the `resolve_bb_pred_count/name_at/arity_at/graph_at` accessors used to build the pred table, trail helpers `rt_pl_trail_*`, choice ledger). Do this with the linker as guide: stub a function, rebuild, an "undefined reference" means GZ still needs it (keep), silence means it was dead (delete).
3. **meta rail** — GUT-list item; locate and remove.
4. Optionally re-measure and decide whether to also lift `g_gz_no_struct_ptr` once the GZ-TEXT compound-term emit is fixed (would close the m3/m4 gap toward parity) — but that is the old C-FRAME B-1 work Lon chose to defer.

## Don't-trip-over notes
- The goal file STATE block (`## ▶ STATE`) is the authoritative live state; the C-FRAME / C-LABEL forensics below it are retained as HISTORY (the B-1/B-2/B-3 ladder is superseded by this pivot).
- scrip.c still has two harmless unused `extern int codegen_flat_build/codegen_clause_dispatch` decls in the m4 block (decl-without-def is legal; remove if tidying).
- Floors were RAISED to 91/87 earlier today then RESET to 89/48 here — the reset is intentional; future sessions ratchet up from 89/48.
