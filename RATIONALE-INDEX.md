# RATIONALE-INDEX — symbol/function -> recovered design rationale

**What this is.** `e25a5daf` (2026-08-20, GOAL-STYLE-200COL REACTIVATION 4) stripped 6,919 comments across 162 files enforcing the C style rule (RULES.md: 200-char lines, zero blank lines, exactly one comment form). Most of that was decoration; a real fraction was the project's hardest-won measured rationale — the only record of *why* a piece of code refuses the case it refuses. RULES.md's comment restriction is not being relitigated (do not put prose back in the source); this index is the promised alternative home: an "indexed appendix" mapping a symbol name to wherever its rationale now lives, so a session grep on the *symbol* finds the doc instead of needing to know a doc exists first. See `.github/FINDING-2026-08-22-recover-stripped-design-rationale-classification.md` for the recovery methodology and counts.

**How to use this file.** Looking for "why does X do Y": `grep -n "^- \`X\`" .github/RATIONALE-INDEX.md`. Adding a new relocation: append one line per symbol it covers, pointing at the doc (ARCH file, FINDING, or this file's own inline section for something too small to deserve a standalone doc).

## Index

- `sn4_blob_choice_scan` -> `.github/ARCH-ENGINE.md` §3.2
- `resume_carrier_ok` -> `.github/ARCH-ENGINE.md` §3.3 (the seat04 cluster: tier-3 admission, `lf`/`fn`/`nc` witnesses)
- `blob_choice_rbp_scan` -> `.github/ARCH-ENGINE.md` §3.4
- `sn4_choice_rbp_off` -> `.github/ARCH-ENGINE.md` §3.4
- `sn4_alt_carrier` -> `.github/ARCH-ENGINE.md` §3.1
- `blob_frame_bytes` -> `.github/ARCH-ENGINE.md` §3.5
- `zdp_tier` / ZDP lattice (`zeta_depth.c`/`.h`) -> `.github/ARCH-ENGINE.md` §3.6 (⛔ verified NOT the live admission path for the choice-carrier decisions as of the recovery commit — re-verify before trusting either way)

## Remaining clusters, not yet relocated (see QUEUE.tsv / tasks/ for the dispatched rows)

Ranked by stripped-RATIONALE-comment count (heuristic classifier, see the FINDING above for the caveat that this is a lower bound):

| rank | file | stripped RATIONALE (est.) | queue row |
|---|---|---|---|
| 1 | `src/emitter/emit.cpp` (remainder, beyond §3 above) | ~600 | `rationale-emit-cpp-remainder` |
| 2 | `src/templates/x86_asm.h` | 253 | `rationale-x86-asm-h` |
| 3 | `src/lower/lower_snobol4.c` | 232 | `rationale-lower-snobol4-c` |
| 4 | `src/contracts/zeta_storage.c` | 132 | `rationale-zeta-storage-c` |
| 5 | `src/emitter/emit.h` | 119 | `rationale-emit-h` |
| 6 | `src/runtime/rt/rt.c` | 106 | `rationale-rt-c` |
| 7 | `src/driver/scrip.c` | 105 | `rationale-scrip-c` |
| 8 | `src/templates/bb_call_proc_staged.cpp` | 81 | `rationale-bb-call-proc-staged` |

Each row's baton carries the file, the recovery method (`scripts/` extraction under `/tmp/.../scratchpad/rationale/` this session — not yet promoted to a checked-in script; see the FINDING), and the same DECORATION/RATIONALE split instructions as this row. Row-factory rule carried forward: a session picking one of these should relocate its highest-value sub-cluster and spin off further rows rather than trying to clear an entire file's ~100-600 comments in one sitting.
