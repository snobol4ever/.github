# A starved witness and a starved oracle AGREE, so oracle agreement can never guard a run directory — only an absolute floor can

**hq_P, 2026-09-10, CEO-532.** SCRIP `2bdee91cc`+, corpus `9e9319641`+, `.github` `019c0c80`, `RT_OPT=-O0`,
graded on an incremental `make`. Oracle: `icont`/`iconx` v9.5.25a by absolute path via `icont_bin()`.
Downstream of hq_I's `FINDING-2026-09-10-hq_I-icon-open-of-a-directory-read-zero-entries…`, whose fed
`recent` this repairs the *runner* half of.

## The answer to the brief's question, and it is better than the brief predicted

CEO-532 named `io` at 3 lines and `recent` at 1. **Both are ZERO.** Fed their declared environments, SCRIP
is **byte-identical to the live Arizona oracle** for both — three runs each, same md5:

| witness | contracted answer | SCRIP vs live oracle | stability |
|---|---|---|---|
| `rung36_jcon_io` | 135 lines | **0 diff lines** | `fbcc4c51…` ×3 |
| `rung36_jcon_recent` | 443 lines | **0 diff lines** | `af61c798…` ×3 |

There was no SCRIP defect left in either. What was missing was a runner that builds the room the program
was written to run in.

## ⛔ The `io` ref is from the wrong oracle, and that is the whole of its remaining 10 lines

`corpus/tests/icon/rung36_jcon_io.expected` is a **byte-for-byte copy of jcon's own `io.std`** — `diff`
against `/home/resources/jcon-master/test/io.std` is empty. It is a JVM-jcon reference, not an
`icont`/`iconx` cut. All 10 lines it disagrees on are `nonseq:` rows, where jcon **fails** a `seek()` past
end-of-file and prints `-` while Arizona **succeeds** and prints `?`. SCRIP already matches Arizona on every
one. The cut is the coo's (CEO-532); the gate pins the row as DISPUTED and **fails on XPASS**, so the re-cut
cannot land and leave a stale pin behind.

⚠️ One contract subtlety the coo has to rule on, because the program **reads its own source as data**:
`sed 's/^/=()= /' io.icn` echoes the first 10 lines of whatever `io.icn` sits in the rundir. The existing ref
shows the **upstream, semicolon-free** text, not our semicolon-added corpus copy, so the fixture pins
upstream. Change the fixture and the ref moves with it.

## ⭐ The finding: my own negative test showed ARM 2 cannot do this job

The gate's first ARM 1 compared `NAME.fixtures/` against its own copy in the rundir — so **deleting** a
fixture made the declaration smaller and ARM 1 passed. Removing `recogn.dat` to prove otherwise produced the
result worth writing down:

```
PASS ARM2 rung36_jcon_recent (SCRIP == icont/iconx, 442 lines, contracted rundir)
```

**Both arms starved to 442 lines and agreed.** That is hq_I's class reproduced on demand inside the very
instrument built to stand over it. An oracle diff answers *do these two implementations agree*, and two
implementations reading the same impoverished environment agree about it perfectly. ⛔ **So no amount of
oracle agreement can guard a run directory.** The same shape as hq_U's two-crashes-that-agree: agreement is
exactly the property the check is built to trust, which is why its failure there is silent.

✅ **The cure is an ABSOLUTE FLOOR on the contracted answer**, pinned per witness — the only arm that bites
when both sides starve together, and the only live arm on the ref-disputed row where ARM 4 is muted.
Re-tested: `recogn.dat` removed → `442 < 443` red; `io.std` removed → `133 < 135` red **on the disputed row**.
A floor that *rises* prints a re-pin line rather than passing quietly.

⭐ **Generalization worth carrying:** wherever two arms can fail the same way for the same external reason,
their agreement is not evidence and an absolute bound on the WORK DONE is the only guard. `MASTER_ENTRY_FLOOR`
is the same instrument for the same reason.

## Three more defects found by negative-testing rather than by review

1. **My own `set -e` abort, and it was invisible in the worst way.** `cmd; [ $? -eq 2 ] && {…}` inside
   `test_icon_all_rungs.sh` (which runs `set -euo pipefail`) returns 1 whenever the test is FALSE — i.e. on
   every healthy witness — and killed the board mid-list. `rung36_jcon_io` and everything after it vanished
   **with no message and no summary line**, which reads as a *shorter suite*, not an aborted one. Cured to
   `if`-form in both the runner and the gate, so nobody has to know which file sets `-e`.
2. **A too-loose env validator refused nothing.** `[A-Za-z_]*=*` accepts `this is not VAR=value` and arms a
   "variable" whose name contains spaces; the gate then reported a wrong **answer** (rc=1) instead of a
   malformed **declaration** (rc=2) — which sends a reader hunting a compiler bug over a typo in a sidecar.
   Anchored.
3. **Two of my header's negative-test claims named the wrong arm.** `JCONT=WRONG` reddens ARM 4, not ARM 2 —
   ARM 2 stays correctly green, both sides reading the same wrong environment. Corrected in place: a
   negative-test record naming the wrong arm is worth less than none.

## What landed

- `SCRIP/scripts/lib_icn_rundir.sh` — the ONE authority for a `tests/icon` witness's stdin/argv/fixtures/env.
  ⭐ **No new sidecar formats**: it *sources* `ipl_argv_read`/`ipl_fixtures_stage` rather than restating them,
  so a fixture cannot mean one thing under ipl and another here. Only `NAME.env` is new. The three runners
  each carried their own byte-identical copy of the stdin lookup — the shape that let `test_prolog_ladder.sh`
  and its Raku twin diverge.
- `SCRIP/scripts/test_gate_icn_rundir_contract.sh` — four arms, every one negative-tested, wired blocking into
  `make test` (~0.3s) and adopted into `gate_wiring.tsv`.
- `corpus/tests/icon/rung36_jcon_{io,recent}.{argv,fixtures/}` + `rung36_jcon_recent.env`.

**Control arm**, same 8-witness temp corpus, origin's runner vs mine: `rung36_jcon_recent` **FAIL → PASS**,
`rung36_jcon_io` FAIL → FAIL (ref disputed), and **six contract-free witnesses PASS → PASS, unmoved**.

## Two things left on the floor for their owners

- **`loadfunc`'s fixture half is permanently unreachable, not merely un-vendored.** `load1.zip`/`load2.zip`/
  `jfuncs.zip` are JVM artifacts `loadfunc.sh` builds with `javac`+`jar`, and Arizona's `loadfunc()` wants a
  `.so`. Only the ERROR path is ever gradable, so that ref memorializes a missing file. Two real SCRIP defects
  live on it: SCRIP omits the `dlopen` diagnostic `loadfunc("load1.zip","proc1a"): <dlerror>` on `&errout`,
  and images the arguments **without** the trailing NUL where Arizona prints `"load1.zip\x00"`. Also
  `packages/icon/jcon_tests/ALL.excluded.txt:9` still says *"loadfunc: oracle produced EMPTY output"* — the
  oracle produces **10 lines**; and that `.std`'s traceback carries the source path **as given on the command
  line**, so it is only reproducible if the runner names the source relatively from the rundir.
- **`test_gate_harness_refusal_is_rc2.sh` is RED 6/15 on a clean tree** (proved by stashing: identical count
  with and without my changes). Its probe runs trip today's new `lib_one_runner.sh` guard and read the
  ONE-RUNNER refusal as the harness's own. Not mine, not cured, named here so it is not re-diagnosed.
