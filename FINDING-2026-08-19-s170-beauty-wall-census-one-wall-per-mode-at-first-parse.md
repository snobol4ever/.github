# FINDING s170 (HQ, Fable 5) — BEAUTY WALL CENSUS: exactly ONE wall per mode, both at the FIRST Shift/Reduce parse; the -INCLUDE theory is dead; comments are the only thing beauty has ever beautified in either mode

**Front:** GOAL-SNOBOL4-100 · M1. Pristine build at SCRIP `b7e10d3c` (post GC-W1), corpus `a3604cc9`. Oracle `x64/bin/sbl -bf beauty.sno`. Beauty at `corpus/programs/snobol4/demo/beauty/beauty.sno` (compile with `SNO_LIB=<its dir>`).

## The bracket (tiny-input matrix, default AND `SCRIP_B1C_PARITY=1` arms — the arm changes NOTHING here)
| input | oracle | m4 | m3 |
|---|---|---|---|
| `* c` (comment) | echo | echo ✓ | echo ✓ |
| `START` (bare label) | `START` | **`Parse Error` + raw echo** | **SEGV** |
| `      X = 1` (indented assign) | beautified | **`Parse Error` + raw echo** | **SEGV** |
| `START` + `-INCLUDE 'g.inc'` | both lines | `Parse Error` at line 1, dies | SEGV |

**Corollary:** the earlier "beauty m4 runs the Shift/Reduce machine, echoes START, Parse Error at -INCLUDE line 2" reading (FINDING s168, HQ-54 cursor) was WRONG — the echoed `START` is the error-recovery raw echo, the Parse Error is on `START` itself, and the 7 "header" lines are `*`-comments that bypass the parser entirely. **Beauty's grammar has never successfully matched ONE statement in either mode at this HEAD.** The grammar OBJECT is exonerated (36/36 oracle-identical datatypes, T4/D-18 era) — the defect class is MATCHING with a fragment-built grammar.

## WALL-1 — m4: clean `Parse Error` on every real statement
Both arms. The grammar's match takes the F-path cleanly — consistent with the deferred calls inside the grammar rules (`*match(...)`, `*upr(tx)` etc., beauty.sno:63–75) failing at match time in an m4 process, i.e. **FINDING s168 residue R1's face** (armed TINY admission not engaging in m4 processes — hypothesis: `bb_tiny_shim_ok`/`bb_scc_probe` consult emit-side knowledge absent at m4 runtime; `probe/b1` witnesses all still SEGV m4 under `=1`). Owner: queue row 4 `b1c-m4-seam` (seat6, in flight) — beauty's tiny-input is now that rung's acceptance witness.

## WALL-2 — m3: SEGV on every real statement, `zls_g_region` signature
gdb (`SCRIP_NO_SEGV_HANDLER=1`, input `START`): fault pc=`0x7fffee202000` (page-aligned slab address, never-written class) with `#1 zls_g_region (g=…) at src/contracts/zeta_storage.c:936` live in the frame — **the documented B2/B2c class** (the "m3 dirty-quad carve-zeroing" wall, formerly parked D-7, formerly HQ-owned; delegation per Lon s168). Pre-existing: identical at `f44be5f1` (before GC-W1 landed).

## WALL-3 — semantics behind the walls: R2 retreat wrong-answer
`probe/b1` `*_retreat` witnesses run clean armed-m3 but report `match` where the oracle retreats `nomatch` (FINDING s168). Beauty's parse is DRIVEN by match-failure-driven retreat between grammar alternatives — R2 will produce wrong parses the moment walls 1–2 fall. Owner: queue row 5 `b1c-retreat`.

## Repro commands (no new corpus files needed; seats re-run these)
```
cd SCRIP && make pristine
B=../corpus/programs/snobol4/demo/beauty/beauty.sno
printf 'START\n' | ./scrip $B                                        # WALL-2 (m3 SEGV)
SNO_LIB=$(dirname $B) ./scrip --compile -o /tmp/b.s $B < /dev/null && gcc /tmp/b.s -Lout -lscrip_rt -lm -Wl,-rpath,$PWD/out -o /tmp/b
printf 'START\n' | stdbuf -o0 /tmp/b                                 # WALL-1 (m4 Parse Error)
printf 'START\n' | ../x64/bin/sbl -bf $B                             # oracle: echoes START
```

## The M1 ladder cut from this census (rungs + steps in GOAL-SNOBOL4-100 s170 cursor; queue rows both channels)
M1-R1 `b1c-flip` (row 3) → M1-R2 `b1c-m4-seam`+WALL-1 (row 4, seat6) → M1-R3 `beauty-m3-zls` WALL-2 (new row 6) → M1-R4 `b1c-retreat` WALL-3 (row 5) → M1-R5 `beauty-fixed-point` (new row, gate-only: self-input byte-diff both modes + beauty_suite drivers; **M1 EARNED in capitals** on green).
