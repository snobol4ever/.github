# FINDING — seat1, csnobol4-clean-fork: the census holds, and keeper 3 collides with upstream's generated-output policy

**Date:** 2026-08-21 · **Seat:** seat1 (`/home/claude1`, Claude Opus 5) · **Topic:** `csnobol4-clean-fork` · **Status:** keepers 1,2,4 LANDED + DONE-WHEN verified · BLOCKED only on the keeper-3 fire-points and the GitHub fork (both Lon's)

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
| `9a36adaa` | 2 + 3a | `monitor_ipc_runtime.c` +495, `test_monitor_ipc_runtime.c` +100, `Makefile2.m4` hook +6 |
| `8d35dbaa` | 4 | `lib/bsd/mstime.c` +47/−23 — `mstime()` returns CLOCK_MONOTONIC ns |

**Keeper 4 landed this session.** HQ's version arrived as `c5ead01` in the live tree after the first
half of this rung was written, so it was taken verbatim as the brief required ("take HQ's version, do
not invent one") rather than re-derived. Upstream's `lib/bsd/mstime.c` differs from our snapshot's by
**one line only** — the RCS `$Id$` keyword, unexpanded upstream, expanded in our tarball import — so
HQ's diff applied onto upstream's body unchanged; upstream's `$Id$` line was kept. Body verified
byte-identical to HQ's file; numstat +47/−23 matches HQ's exactly.

Cumulative keeper diff vs merge-base: `Makefile2.m4` +6 · `lib/bsd/mstime.c` +47/−23 ·
`lib/init.c` +10/−3 · `monitor_ipc_runtime.c` +495 · `test_monitor_ipc_runtime.c` +100.

Identity `LCherryholmes`; licence/copyright headers untouched; GPL-style `changed <file>: <what>, <date>` notes in both modified files; no upstream commit rewritten.

**Verification.** `./configure && make xsnobol4 -j4` → green, link line contains `monitor_ipc_runtime.o`. `./snobol4 -f` runs; `CSN_NO_SEGV_HANDLER` present in the binary.

**DONE-WHEN fence grep** over the new tree returns **exactly the 19 upstream-baseline files** — `CHANGES`, `History`, `TODO.soon`, `v311.sil`, `test/v311.sil`, `snolib/{fence,not,utf}.sno`, `test/atn.sno`, 5 `.ref` files, 3 `doc/*.pea`, `pkg/solaris/prototype`, `pkg/bsd/pkg/PLIST` — byte-identical to the pristine-clone list. **Zero FENCE(P) material of ours.**

**Differential — re-run against the real live oracle, whole corpus.** All **321** `.sno` in
`corpus/crosscheck` (every subdir; none uses `TIME()`/`DATE()`, so keeper 4 introduces no
nondeterminism), stdout + rc, `-f`, `< /dev/null`:

**256 identical · 65 differ**, and the 65 partition exactly:

- **64 = precisely the 64 programs that call `FENCE(`** — one-to-one, no program calling `FENCE(`
  is absent and no other program is present. Clean tree says `Error 5 · Undefined function or
  operation`; live tree runs them. **This is the removal working**, not a defect.
- **1 = `patterns/172_pat_fail_forces_retry.sno`, where the LIVE ORACLE IS THE WRONG ONE.** The clean
  tree matches both the `.ref` and SPITBOL (`a b c failed as expected`); the live oracle drops the
  `b`. Bisected to `723ac19`, whose subject claims "gate-neutral", and whose edit lives only in
  generated `isnobol4.c` — never in `v311.sil`. Full write-up:
  `FINDING-2026-08-21-seat1-the-fence-work-broke-plain-pattern-matching-and-the-fix-lives-only-in-generated-output.md`.

That second bullet also **answers §3's blocked question in favour of option (A)**: hand-patching
generated `isnobol4.c` is the precise practice that produced the regression and hid it from source
review, so the monitor fire-points must not follow it.

## 6. The live oracle now exists — superseding this section's earlier blocker

When the first half of this rung ran, `/home/claude/csnobol4/snobol4` and `xsnobol4` were **absent** and
`/usr/local/bin/snobol4` had to be substituted. HQ built the tree at 19:50 alongside `c5ead01`, so the
DONE-WHEN differential in §5 is now run against **the actual live oracle**, as the brief specified.

The live tree was left untouched throughout: `git status` clean, HEAD still `c5ead01`, binary mtime
still HQ's 19:50. Every historical build in the attribution bisect was done in a `git worktree`,
all since removed (`git worktree list` shows only the main tree).

Phil's release delta is still folded into the comparison (clean is 2.3.4+, live is 2.3.3) — but it
turns out to account for **none** of the 65 differences: upstream has not touched `lib/pat.c` since
`REL_2_3_3`, and its only post-2.3.3 `v311.sil` commits are `[PLB134]` case folding and `[PLB133]`
REAL-in-VARVAL, neither of which touches scanner retry.

## 7. Report-only items (confirmed verbatim, not fixed, per brief)

- `SCRIP/scripts/test_3way_snobol4.sh:12` — `CSNO="${CSNO:-$(command -v snobol4)}"`
- `SCRIP/scripts/test_smoke_self_beautify.sh:27` — bare `snobol4 -f -P256k ...`

Both resolve off PATH and pick up root-owned `/usr/local/bin/snobol4`, not the project tree. **Additionally:** `$S4A` is **unset** in this seat's environment, so `$S4A/x64/bin/sbl` on that same line 12 resolves to `/x64/bin/sbl`.

## 8. Blocked on — 2 of the 4 original questions have resolved themselves

| # | Question | State |
|---|---|---|
| 1 | fire-point strategy A/B/C | **STILL OPEN — Lon's call.** Evidence now strongly favours (A): see §5 and the `723ac19` finding. No partial extraction shipped, per the brief's clause (b). |
| 2 | HQ's `mstime.c` nanosecond `TIME()` | **RESOLVED.** Landed as `c5ead01`; taken verbatim as keeper 4 (`8d35dbaa`). |
| 3 | live-oracle baseline | **RESOLVED.** HQ built it at 19:50; full 321-program differential re-run against it (§5, §6). |
| 4 | rename → fork → push | **STILL OPEN — needs Lon.** `ssh -T git@github.com` **does** authenticate as `LCherryholmes`, so a push is mechanically possible; what is not possible from this seat is the *repo administration*. `gh auth status` → not logged in, and GitHub refuses a fork into a name already taken, so `snobol4ever/csnobol4` must be renamed before `philbudne/csnobol4` can be forked. Exact sequence sent to the question box. |

⛔ **Deliberately not done:** the keeper branch was **not** pushed to `snobol4ever/csnobol4`. That repo is
the FENCE tree destined for the attic, and it shares **no ancestry** with upstream — pushing `keepers`
into it would graft an unrelated history onto the very repo we are retiring. The branch waits locally.
