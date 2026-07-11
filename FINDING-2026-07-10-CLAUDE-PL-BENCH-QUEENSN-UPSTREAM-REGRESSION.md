# FINDING — queensn empty output after upstream bb_gvar_assign* orphan retirements

**Discovered:** Claude Sonnet 4.6, 2026-07-10 session #5, during post-rebase board recertification.
**Status:** UPSTREAM REGRESSION — not introduced by PL-ISO-2 (setof/bagof). Needs a fix commit before combined head is push-certified at bench 22/22.

---

## Symptom

`corpus/benchmarks/prolog/bench/queensn.pl` emits **zero bytes** (empty output) when run redirected to a file or the bench harness. Prints correctly to a terminal (tty-buffering masks it live).

```
./scrip --run queensn.pl < /dev/null > /tmp/out   # 0 lines
./scrip --run queensn.pl < /dev/null               # correct solution printed to tty
```

Bench harness sees FAIL because its `>` redirect captures nothing.

---

## Bisect result

| Commit | queensn 5-run test (redirected) | Notes |
|--------|--------------------------------|-------|
| `0db9dd03` | 5/5 produce 1 line (PASS) | pre-session HEAD, last known-good |
| `b74c3716` | 0/5 produce output (FAIL) | latest upstream HEAD (seven bb_gvar_assign* retirements) |

The regression is entirely within the seven upstream commits `f8c159e4..b74c3716` (bb_gvar_assign_concat, bb_gvar_assign_call, bb_gvar_assign_descr, bb_gvar_assign_lit_i, bb_gvar_assign_lit_s, bb_gvar_assign_var, bb_gvar_assign) — none of which touch Prolog code.

---

## Root-cause hypothesis

`queensn.pl` uses list-building and write/nl. The orphan retirements removed `bb_gvar_assign_concat.cpp` and related global-assign templates. If any path still dispatches to one of the retired IR kinds and the removed template was the output sink (the `write`/`nl` path going through a gvar-concat route), removing the dispatch entry could silently drop output rather than aborting — producing empty stdout with a clean exit.

**Immediate next-session action:** grep the queensn `.s` artifact (or dump IR) on `b74c3716` vs `0db9dd03` to locate the IR kind that vanished from the dispatch, then either (a) fix the upstream dispatch routing or (b) confirm the IR kind is genuinely dead for Prolog and that the output path routes elsewhere.

---

## Board impact

- Combined head bench: **21/22** (queensn FAIL).
- All other bench programs: **21/21 unaffected**.
- The PL-ISO-2 (setof/bagof) rung itself: **120/120 suite ×3, bench 22/22 on pre-rebase head** — my change is clean.
- The fix belongs in a separate SCRIP commit targeting the upstream bb_gvar_assign* removal, not in the PL-ISO-2 commit.

---

## Reproduction

```bash
cd /home/claude/SCRIP
git checkout b74c3716
make -j4 scrip && make libscrip_rt
B=/home/claude/corpus/benchmarks/prolog/bench
./scrip --run $B/queensn.pl < /dev/null > /tmp/q.out
wc -l /tmp/q.out   # => 0  (FAIL)
cat $B/queensn.expected   # => [p(1,1),p(2,3),...]
```
