# FINDING — seat1, csnobol4-clean-fork: the census holds, and keeper 3 collides with upstream's generated-output policy

**Date:** 2026-08-21 · **Seat:** seat1 (`/home/claude1`, Claude Opus 5) · **Topic:** `csnobol4-clean-fork` · **Status:** BLOCKED on HQ (`q-csnobol4-clean-fork` sent)

## 1. The brief's census is exact — reproduced, not trusted

`/home/claude/csnobol4` (path is **literal**, not a `/home/claude1` translation — the repo does not exist under this seat's root; `SCRIP/csnobol4` is an unrelated 3-file stub).

- Root commit `a509cd73ddc1720df6d1914505b5b56a47789f14` = "Initial import of CSNOBOL4 2.3.3 with FENCE(P) groundwork". 49 commits.
- `git remote -v` → only `snobol4ever/csnobol4`. **No upstream remote, no merge base, no ancestry.** The "not a fork" ruling is confirmed mechanically.
- `git diff --numstat <root>..HEAD` → **73 files**, of which **34** are `docs/F-*`.
- Every figure the brief quoted verifies: `v311.sil` +116/-4 · `monitor_ipc_runtime.c` +495 · `test_monitor_ipc_runtime.c` +100 · `lib/init.c` +5/-3 · `lib/pat.c` +7.
- Working tree carries **one uncommitted edit: `lib/bsd/mstime.c`** (keeper 4). Left untouched.

## 2. What Phil has changed since our snapshot — the reason the rung exists

Upstream `philbudne/csnobol4` cloned to `/home/claude/csnobol4-clean`: **4505 commits**, ancestry back to "Initial revision".

`REL_2_3_3..HEAD` = **39 commits, 89 files, +1932/−222** — new `modules/jsmn` JSON module, `v311.sil` +32/−4, `configure` +152/−73, `.gitignore` +149. Upstream tag `REL_2_3_4` exists. New tree self-reports **2.3.4+ (April 24, 2026)** against our snapshot's **2.3.3 (May 19, 2025)**.

## 3. ⛔ The load-bearing finding: keeper 3 cannot be committed as written

Checked upstream file-by-file as the brief demanded. **Of the 20 named candidates, upstream tracks exactly ONE: `Makefile2.m4`.**

Upstream `.gitignore` explicitly ignores `Makefile2`, `isnobol4.c`, `snobol4.c`, `syn.c`, `version.h`, `config.{h,m4,sno}`, `data_init.h{,2}`, `equ.h{,2}`, `res.h{,2}`, `proc.h{,2}`, `bsdtsort`, `callgraph`, and the `snobol4`/`xsnobol4` binaries. They are build products by design.

Keeper 3 names "the Makefile2 / isnobol4.c / snobol4.c hooks". Committing those as tracked edits would diverge from upstream's choice — which the brief forbids in the same sentence. The two halves split cleanly:

- **Build hook — SOLVED.** `c1843eb` touched **both** `Makefile2` (+6) and the tracked generator `Makefile2.m4` (+6). Only the generator half is needed; it is landed and builds.
- **Fire-points — BLOCKED.** The `monitor_emit_*` calls injected into generated `isnobol4.c`/`snobol4.c` come from 5 commits: `4ade8a4`, `ad993fe`, `b83db40`, `64652ed`, `b3aeb9f`. FENCE and monitor edits **do not interleave at commit granularity** (every other commit touching those files is FENCE/F-2), but they interleave *in the same generated files*. Options put to HQ: (A) re-express in `v311.sil`, which IS tracked upstream; (B) maintained post-generation patch; (C) track the generated `.c` files and accept divergence. Recommended (A), else (B). **No partial extraction shipped**, per the brief's clause (b).

## 4. Generated files whose tracked/untracked status I changed

**None.** The branch adds two new first-party source files (`monitor_ipc_runtime.c`, `test_monitor_ipc_runtime.c`) and edits two already-tracked files (`lib/init.c`, `Makefile2.m4`). No build product was added to the index; no upstream-tracked file was removed from it.

## 5. Landed on branch `keepers` (`/home/claude/csnobol4-clean`, unpushed)

| Commit | Keeper | Content |
|---|---|---|
| `4577cb7b` | 1 | `lib/init.c` — `CSN_NO_SEGV_HANDLER` bypass around `signal(SIGSEGV/SIGBUS, err_catch)` |
| `9a36adaa` | 2 | `monitor_ipc_runtime.c` +495, `test_monitor_ipc_runtime.c` +100, `Makefile2.m4` hook +6 |

Identity `LCherryholmes`; licence/copyright headers untouched; GPL-style `changed <file>: <what>, <date>` notes in both modified files; no upstream commit rewritten.

**Verification.** `./configure && make xsnobol4 -j4` → green, link line contains `monitor_ipc_runtime.o`. `./snobol4 -f` runs; `CSN_NO_SEGV_HANDLER` present in the binary.

**DONE-WHEN fence grep** over the new tree returns **exactly the 19 upstream-baseline files** — `CHANGES`, `History`, `TODO.soon`, `v311.sil`, `test/v311.sil`, `snolib/{fence,not,utf}.sno`, `test/atn.sno`, 5 `.ref` files, 3 `doc/*.pea`, `pkg/solaris/prototype`, `pkg/bsd/pkg/PLIST` — byte-identical to the pristine-clone list. **Zero FENCE(P) material of ours.**

**Differential: 24/24 identical** (stdout + rc) over `corpus/crosscheck/{arith,arith_new,assign,capture}` — empty diff.

## 6. ⛔ The live oracle does not exist

`/home/claude/csnobol4/snobol4` **and** `xsnobol4` are both **absent** — that tree was never built. The DONE-WHEN's "same output as the live snobol4" therefore has no baseline. I substituted `/usr/local/bin/snobol4` (CSNOBOL4B 2.3.3, root-owned) and label every number above accordingly. Consequence: the differential compares **2.3.4+ against 2.3.3**, so it folds Phil's release delta in with ours. Nothing under `/home/claude/csnobol4` was modified.

## 7. Report-only items (confirmed verbatim, not fixed, per brief)

- `SCRIP/scripts/test_3way_snobol4.sh:12` — `CSNO="${CSNO:-$(command -v snobol4)}"`
- `SCRIP/scripts/test_smoke_self_beautify.sh:27` — bare `snobol4 -f -P256k ...`

Both resolve off PATH and pick up root-owned `/usr/local/bin/snobol4`, not the project tree. **Additionally:** `$S4A` is **unset** in this seat's environment, so `$S4A/x64/bin/sbl` on that same line 12 resolves to `/x64/bin/sbl`.

## 8. Blocked on

HQ answers to `q-csnobol4-clean-fork`: (1) fire-point strategy A/B/C · (2) HQ's `mstime.c` nanosecond `TIME()` · (3) live-oracle baseline · (4) Lon to run the rename→fork→push sequence (`gh` is not authenticated in this seat; no push credential held).
