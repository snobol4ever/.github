# FINDING s174 (seat5) — regen-hygiene: the shared scratch path was TRUNCATING artifacts, not just swapping them

**Queue row 19 `regen-hygiene`.** Brief: *seat2 s169 regen-catchup FINDING: prolog_bench regen has no git
block; regen scripts share fixed /tmp scratch paths.* First step: add the git block (mirror the 5 siblings)
+ mktemp per invocation in all regen scripts. DONE-WHEN: both fixed, one concurrent two-seat regen dry-run
clean, pushed.

**Landed:** SCRIP `47064a1c` — 6 scripts, ONE commit, pushed. Both items closed and both NEGATIVE-TESTED.

---

## 1. The headline: the hazard was real, and one class worse than the receipt described

s169 §7.5 predicted *"two seats regenerating concurrently would corrupt each other's artifacts."* Measured:
two seat roots holding **disjoint** program sets, regenerating concurrently, 5 trials each, every artifact
md5'd against a serial reference produced alone in the same tree:

| scripts | trial 1 | 2 | 3 | 4 | 5 | total |
|---|---|---|---|---|---|---|
| **old** (shared /tmp) | 8+13 | 9+9 | 7+11 | 13+16 | 8+10 | **104 contaminated** |
| **new** (`mktemp -d`) | 0+0 | 0+0 | 0+0 | 0+0 | 0+0 | **0** |

The old counts vary every trial — the signature of a genuine race, not a deterministic diff. Two corruption
shapes appeared, and only the first was predicted:

1. **Wrong-program asm.** In one trial `rung05_backtrack_backtrack.s` and `rung06_lists_lists.s` both landed
   on md5 `1fc03fec…` — one program's bytes written into two different artifacts.
2. ⭐ **TRUNCATION TO ZERO BYTES.** `d41d8cd98f00b204e9800998ecf8427e` (the empty-file md5) recurs throughout
   the old-script runs. Seat A opens `/tmp/prog_regen.s` with `>` — truncating it — while seat B is between
   its own write and its `cmp`/`cp`. Seat B then commits a **zero-byte `.s`** as honest current compiler
   output. This is not a swap that a reader would notice; it is the artifact silently becoming nothing.

**The scripts' own safety design is what the race defeats.** All six are carefully non-destructive on
emit-fail/AS-FAIL/timeout — "leave the last-good `.s` untouched and flag loudly." That guard reads `$t`,
and `$t` was the shared file. A seat can therefore see a *neighbour's* AS-FAIL and preserve — or clobber —
its own artifact on the strength of it. The graceful-skip philosophy was only ever sound single-seat.

## 2. Scope was five scripts, not the two named

s169 named `/tmp/cc_regen.s` and `/tmp/prog_regen.s` (fully fixed paths, `util_regen_{crosscheck,programs}`).
Three more collide, one rung less obviously:

| script | old scratch | collides when |
|---|---|---|
| `util_regen_crosscheck` | `/tmp/cc_regen.{s,o,aserr}` | ALWAYS — two seats, any programs |
| `util_regen_programs` | `/tmp/prog_regen.{s,o,aserr}` | ALWAYS |
| `util_regen_benchmark` | `/tmp/bench_<name>.{s,o,aserr}` | two seats sweeping the same tree (i.e. the normal case) |
| `util_regen_feature` | `/tmp/feat_<base>.{s,o,aserr}` | same |
| `util_regen_demo` | `/tmp/demo_<name>.{s,o}` + `/tmp/demo_as_err.txt` **fixed** | same |
| `util_regen_prolog_bench` | `mktemp` ✅ + `/tmp/regen_{cerr,aserr}.$$` | never (PID-keyed) — but the `.s` temps escape on SIGKILL |
| `update_icon_bench_asm` | `mktemp -d` + trap ✅ | never — **this was already the correct pattern** |

Program-keyed is NOT per-seat: two seats sweeping one tree walk the same names, so they collide on *every*
program rather than on a lucky few. All six now take one `mktemp -d` per invocation under `trap ... EXIT`,
copying `update_icon_bench_asm.sh:41` — the sibling that already had it right.

**Physical evidence the paths were live, not theoretical:** `/tmp/demo_as_err.txt` was sitting in this
container at 15:55 today, timestamped *before* this seat started — another seat's regen, at the shared path.

## 3. The missing commit block (s169 ⭐§3) — confirmed by direct A/B

Same forced delta (two bench `.s` staled), same corpus, old script vs new:

```
OLD: WROTE queens.s, changed=2 -> HEAD did NOT move; `git status` shows
       M benchmarks/prolog/bench/nrev.s
       M benchmarks/prolog/bench/queens.s        <- exactly the drift mechanism s169 described
NEW: WROTE queens.s, changed=2 -> "Committed: 2 files changed, 18873 insertions(+)"; worktree CLEAN
```

The pathspec is **derived from `$B`**, not hardcoded `benchmarks/prolog/bench`: `BENCH_DIR` pointed outside
the corpus repo now prints `SKIP commit — … is not inside the corpus git repo` and leaves HEAD alone, rather
than committing a tree it did not regenerate. Verified.

## 4. Two receipts from s169 that do NOT reproduce — do not navigate by them

- **`git add benchmarks/*.s` (benchmark) and `crosscheck/**/*.s` (crosscheck) are NOT broken.** Both look
  broken: the corpus `.s` sit at `benchmarks/snobol4/*.s` and 147 of 485 crosscheck artifacts sit one level
  deeper than `crosscheck/*/*.s` reaches. This seat nearly filed them as two more no-commit bugs. They are
  fine, for a reason worth writing down: **git pathspec `*` crosses `/`** (wildmatch without `WM_PATHNAME`),
  and when bash finds no match it hands the pattern through literally, so git's own globbing catches every
  depth. Proved in a scratch repo with real modifications at depths 2 and 3 — both staged. *A shell glob and
  a git pathspec that read identically do not mean the same thing; test before filing.*
- **The `$$`-suffixed temp s169 offered as "the one-line fix" is not sufficient**, though it is safe against
  the concurrency case. `mktemp -d` + trap is what landed, because PID-keyed temps still leak on SIGKILL and
  still leave the cleanup as a line someone must remember to write.

## 5. Harness note — the first verification run was wrong, and how it announced itself

The first pass reported 5 and 8 "contaminated" artifacts under the *new* scripts. They were **identical
across all 5 trials** — and a race does not repeat itself byte-for-byte. The control (same seats, run
serially) reproduced the same 13 files exactly, so concurrency was not the variable. Cause: the harness reset
seats with `git reset --hard base` against a ref that does not exist, silently no-op'd through `|| true`, so
contamination the *old-script* trials had committed persisted in HEAD — and it persisted specifically in
AS-FAIL artifacts, which regen by design never overwrites. Rebuilt from a pristine tarball; 0 thereafter.
**A "failure" that is bit-identical across trials is a property of the measuring rig, not of the thing
measured** — the same class as s169 §2's monitor-build `__gva_names`, hit again one row later.

## 6. Out of lane, flagged not fixed

- `util_regen_programs_s_artifacts.sh:32` reads `[ -z "$ALL" ]` with `$ALL` never defaulted. Correct today
  only because that script omits `set -u`; adding `set -u` (as three siblings have) breaks it on line 1 of
  the loop. One-character fix (`${ALL:-}`), not taken here.
- `util_regen_{demo,programs}` call `git diff --cached --quiet` / `git commit` with **no pathspec**, so they
  test and commit the whole index. Harmless across seat roots (separate indexes), wrong if two lanes ever
  share one worktree. The other four scope theirs with `--`.

## 7. For HQ

1. Both open items from s169 §7 are closed (§7.2 commit block, §7.5 scratch paths). §7.1 was already closed —
   RULES step 4 now names all five `util_regen_*` scripts.
2. Still open from s169 §7: the **ruling on the four `*.byrd-reference.s` NASM fossils** (§5 there).
3. The regen scripts have **no gate**. Nothing would have caught either defect, and nothing would catch a
   regression. A cheap one exists: `grep -n '/tmp/' scripts/util_regen_*.sh` must match only comment text,
   and every script must contain a commit block. Say the word and it lands as `test_gate_regen_hygiene.sh`.
