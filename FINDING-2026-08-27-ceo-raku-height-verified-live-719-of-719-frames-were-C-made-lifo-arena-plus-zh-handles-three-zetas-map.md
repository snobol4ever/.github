# FINDING 2026-08-27 (ceo): Raku's height REPRODUCED LIVE — 719/719 both modes at `6defd71a` — and the frame mechanism it ran on, mapped one-to-one onto the THREE ZETAS

**Lon's order (in-chat, this date, verbatim in substance):** find when Raku worked at its height using frames, build it, watch it pass, understand how, and map the spirit of it onto the THREE ZETAS — "surely it will map one-to-one."

## 1. VERIFIED BY EXECUTION, NOT INHERITED
Worktree at `6defd71a` (the last Raku commit, s2026-07-27b, "*%h slurpy-named"), fresh `-O0` build in scratch (outside every seat root), full embedded suite (`test_smoke_raku.sh` — all 719 programs are heredocs in the script, zero corpus dependency):
**mode-3 (--run): PASS=719 FAIL=0 / 719 · mode-4 (--compile): PASS=719 FAIL=0 / 719.** The cursor was honest; RK-ZC-1's same claim independently re-confirmed.

## 2. HOW IT WORKED — THE C-MADE FRAME WORLD
`rt_proc_call_c_lex` (rt.c:1376): stage args into `g_call_args` → run the lex prologue → **make the frame IN C** → transfer by `call` → close through the ret-regime epilogue. The emitted body never allocated anything: it received `fb` in rdi, addressed locals `[frame+off]`, wrote its result at `fb+0`; C read it back. **No γ/ω exit wires existed — the C wrapper WAS α and ω.** Frame storage, three arms:
- **Plain subs:** `alloca(fbytes)` (C stack) or `rt_zls2_push(k)` — and zls2 is the load-bearing discovery: **a downward LIFO software frame stack** (`g_zls2_cur -= k`) in a dedicated mmap reserve, GC-ROOTED ONCE at init (no per-block headers), poison-on-release. Literally the machine-stack discipline implemented in a side arena.
- **Resumable frames:** zeta-heap PINNED HANDLES — `fb = rt_zh_deref(h)+16`, `rt_zh_unpin`, `rt_zh_mark_dead`. This is the GC-heap-adjacent piece.
- **⛔ Lon's in-chat concern ("if Raku's memory is coming from the GC HEAP backed by RBX, that is most likely a problem") — measured answer: plain sub frames were NOT GC-heap** (arena is rooted-once LIFO, not the RBX bump frontier); **resumable frames WERE zh-handle cells** with per-call pin/deref churn — that half is the problem, and it is the half the island store replaces.

## 3. WHY IT BROKE (confirms the RK-ZC diagnosis and Lon's memory)
461 peer commits moved frame-making OUT of C and INTO emitted code (rsp carve + γ/ω wires), landed per-lowerer via `zframe_graph` — set ONLY by lower_icon.c. Raku graphs kept entering through the legacy wrapper on a spine that now expected self-allocating bodies: `ret` popped a ζ cell as a return address (the literal 42 in the backtrace), and every sub died "carries no return wires." 719/0 → 513/206 with zero Raku commits in between.

## 4. THE ONE-TO-ONE MAP (the spirit, restored inside the THREE ZETAS)
| At the height (C-made) | THREE ZETAS now |
|---|---|
| zls2 LIFO frame arena / `alloca` fb | **ζ-ACTIVATION-FRAME** — same LIFO discipline, moved from side-arena to the machine stack (RBP carve by the emitted prologue) |
| result cell at `fb+0` | the frame's result slot, same fixed-offset discipline |
| `rt_frame_bind_args` binding params at fb offsets | the same binder reading the carved frame (RK-ZC-4 landed exactly this) |
| zh pinned handles for resumables (pin/deref/unpin/mark_dead) | **workspace-island activation frames** (non-moving AND GC-scanned → direct pointers, zero pin churn); alloc at α, retire at ω — `mark_dead` ≅ ω-retire, same lifecycle verbs |
| expression temporaries | **ζ-SPINE** (already forth then, unchanged now) |

Every row corresponds; nothing in the old design is homeless in the new one. **Restoration = finish carrying Raku onto the current regime (the RK-ZC ladder took 513/206 → 705/19; 19 remain) + give the resumable half the island frames when icon-n2's machinery lands — NEVER resurrect the C-made path.** Lon's own July pivot ruled the same direction ("carry it onto the cell-stack, NOT restore the old spine"); this archaeology confirms it with the mechanism in hand.

**Witness recipe (reproducible):** `git worktree add <scratch> 6defd71a && make && bash scripts/test_smoke_raku.sh` — the suite is self-contained.
