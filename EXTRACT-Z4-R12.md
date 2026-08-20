# EXTRACT-Z4-R12.md — CONFIG 1 (R12 ISLAND FRAMES) EXTRACTION RECORD

Z4-1 deliverable for `GOAL-ZETA-FOUR.md`. Source: worktree `f7de3863` (s65 R12-ERAD), built + measured **5/5 correct** (see `FINDING-2026-07-28-CLAUDE-Z4-0-...-ROTTED.md` ADDENDUM 1). Compare tree: HEAD `cca948c5`. Everything below is MEASURED from the two trees, not recalled.

## 1. ⭐ THE STRUCTURAL FACT THAT EXPLAINS THE WHOLE ROT — R12 NEVER NAMED ITSELF
**Measured at the R12 epoch: `grep -c "ZC_FRAME == ZC_FRAME_R12"` in `src/` = ZERO.** R12 was never selected by a positive test. It was selected by the NEGATIVE predicate `ZC_FRAME != ZC_FRAME_RSP` — "not RSP" meant "take the island path," with R12 as the fall-through arm of the accessor ternary.

**THIS IS THE ROOT CAUSE OF THE `#error` IN HEAD's `zeta_choices.h`.** `c26a398a` (ZR-RSPRBP-1) deleted the R12 *label* while leaving that *code*, so every `!= ZC_FRAME_RSP` arm silently re-pointed at RBP — a basis they were never written for. s202's A/B then measured RSP ok=15/crash=5 vs RBP ok=6/crash=14 and correctly concluded "the ζ basis is reachable at RSP only." The arms were not broken; they were **orphaned from the basis they encoded**.

**CONSEQUENCE FOR Z4-7 (the reconstruction):** config 1 does NOT need positive `== R12` tests scattered through the templates. It needs (a) the `!= ZC_FRAME_RSP` predicate to resolve for the R12 selector value, and (b) the two accessors to return r12. The arms are already R12-shaped — that is exactly what `bb_call_proc_staged.cpp:281`'s surviving comment ("configs where r12 IS the zeta frame") is telling us. **Restoring config 1 is closer to re-connecting a disconnected basis than to writing a new one.**

## 2. THE CRUX ACCESSOR, BOTH EPOCHS
R12 epoch (`x86_asm.h:312-313`):
```c
x86_zr()     = ZC_FRAME==RSP ? (_.flat_pat ? "r12" : "rsp") : ZC_FRAME==RBP ? "rbp" : "r12";
x86_zr_num() = ZC_FRAME==RSP ? (_.flat_pat ? 12    : 4    ) : ZC_FRAME==RBP ?  5    :  12;
```
⭐ **NOTE WHAT THE RSP ARM DOES: `_.flat_pat ? "r12"`.** Even under the RSP default, **suspending PAT$ pattern blobs KEPT their r12 island** — the epoch's own comment: *"PAT$ suspending blobs are r12-frame ISLANDS on the side stack — their interior keeps the immune-base architecture verbatim."* The island was never wholly abandoned; it was NARROWED to the class that provably needs a depth-immune base.

HEAD (`x86_asm.h:359-361`):
```c
x86_fb_pinned() = emit_rec_pin();                                  /* per-GRAPH */
x86_fb()        = x86_fb_pinned() ? "rbp" : "rsp";
x86_frame_off(off) = x86_fb_pinned() ? off : off + _.op_flat_disp; /* depth compensation, rsp arm only */
```
**HEAD's per-graph rbp pin is the DIRECT DESCENDANT of the epoch's `flat_pat ? r12` special case** — same idea (give the suspension classes an immune base), generalized from one hardcoded predicate to a per-graph classifier, with the register changed r12→rbp. Lon's framing ("RBP for dynamic-sized housekeeping, RSP for static") is that lineage's end state. The four configs are therefore not four unrelated inventions; **configs 1→3 are one idea migrating registers and shrinking granularity.**

## 3. ARM PAIRING TABLE — `ZC_FRAME != ZC_FRAME_RSP` SITES, RECOUNTED (do not inherit s202's number on faith; this is a fresh count)
| file | HEAD `cca948c5` | R12 epoch `f7de3863` | note |
|---|---|---|---|
| `src/templates/bb_match_release.cpp` | 5 | — | largest cluster; s202 names it as a site where `push x86_zr(); mov x86_zr(),rsp` repoints the frame base itself under RBP (harmless under R12) |
| `src/templates/bb_match_capture.cpp` | 4 | — | capture slots — the class HEAD gets WRONG and both frame configs get RIGHT |
| `src/templates/xa_flat.cpp` | 3 | — | prologue/epilogue anchor |
| `src/driver/scrip.c` | 2 | — | main-frame alloca (`ZC_FRAME != ZC_FRAME_RSP ⇒ alloca(65536)`) |
| `src/templates/bb_match_head.cpp` | 1 | — | |
| `src/templates/bb_call_proc_staged.cpp` | 1 | — | carries the verbatim "r12 IS the zeta frame" comment |
| `src/contracts/zeta_storage.c` | 1 | — | |
| `src/contracts/zeta_choices.h` | 1 | — | the `#error` guard, not a code arm |
| **TOTAL** | **18 (17 code arms + 1 guard)** | **12** | **s202's "17" CONFIRMED** when the header guard is excluded |

**HEAD GREW 12 → 17 CODE ARMS SINCE s65** — five net-new arms written while no reachable basis exercised them. Treat all 17 as SUSPECT-BY-DEFAULT at Z4-7: the 12 with epoch ancestors can be paired against working code; **the ~5 net-new have never run under any basis but RBP-by-accident and must be derived from the contract, not trusted.**

Wider `ZC_FRAME` mention census at HEAD (any form): `xa_flat.cpp` 27 · `x86_asm.h` 17 · `bb_call_proc_staged.cpp` 11 · `bb_match_release.cpp` 9 · `emit.cpp` 7 · `scrip.c` 6 · `bb_match_head.cpp` 5 · `bb_match_capture.cpp` 4 · `rt.c` 2 · `lower_snobol4.c` 2 · `zeta_storage.c` 2 · `bb_match_defer.cpp` 1 · `emit.h` 1. **This is Z4-9's deletion surface for the `ZC_FRAME` axis: ~94 mentions across 13 files.**

## 4. BUILD RECIPE (reproducible; both worktrees currently exist on disk)
```bash
git worktree add /home/claude/wt-r12 f7de3863
apt-get install -y libgc-dev        # epoch dep; HEAD dropped it at GC-U-4 s67
cd /home/claude/wt-r12 && make -j4 scrip && make libscrip_rt
# select config 1:
sed -i 's/#define ZC_FRAME ZC_FRAME_RSP/#define ZC_FRAME ZC_FRAME_R12/' src/contracts/zeta_choices.h
rm -f scrip && make -j4 scrip && make libscrip_rt     # BOTH — or compiler and runtime disagree on the basis
./scrip --run prog.sno < /dev/null                    # best-of-3; first run is ~145x cold
```

## 5. WHAT HAS NO MODERN TWIN (net-new work for Z4-7, as opposed to re-connection)
- The **side-stack island allocator** for suspending PAT$ blobs (`f7de3863`'s own headline). HEAD has no side stack — the pinned-rbp graph replaced it.
- `x86_r12_modrm` — RENAMED to `x86_frame_modrm` at `c26a398a`. It already encodes `x86_fb_num()` generically, so it serves R12 unchanged once the accessor returns 12; **no encoder work is expected here** (verify, do not assume).
- The **r12 chain anchor** in `rt_chain_enter`, deleted at `cc624e92` (s67) as redundant once epilogues unwound both edges absolutely. Config 1 may not need it back — s65 already ran without it.
- **Co-expressions**: the historical limitation (R-D). Six-register coexpr save in `bb_create.cpp` covers r12 regardless; refuses must be LOUD.

## 6. HONEST LIMITS
(a) The epoch's `.s` artifacts and corpus are NOT contemporaneous with today's corpus — only the fixed Z4 probe set is legitimate for cross-epoch comparison. (b) The 12-vs-17 pairing is by FILE COUNT; the per-site pairing (which HEAD arm descends from which epoch arm) is NOT yet done and is the first task of Z4-7. (c) Nothing here is a claim that config 1 is *fast* — it measured ~8-15% slower than config 2 on every probe. Its value is **correctness-oracle status (5/5)** and the call-path number (`z4_fib` 71ms, the best of all three generations).
