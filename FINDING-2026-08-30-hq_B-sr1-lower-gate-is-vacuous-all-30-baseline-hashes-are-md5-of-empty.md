# FINDING 2026-08-30 hq_B — SR-1's lower gate is vacuous: all 30 baked baseline hashes are md5("")

**Tree:** SCRIP `3fa3f557` · corpus `2f552159` · measured 2026-08-30T02:24Z, seat `hq_B` (`/home/claude_B`).

## The claim, in one line

`scripts/test_lower_byte_identical.sh` — the "SM bytecode byte-identical gate (SR-1)", one of the two
harnesses `corpus_coverage_manifest.tsv` names as GATING `demos/icon` and `demos/prolog` — has never
measured anything, and has said `PASS` while not measuring it.

## Evidence, three commands

```
$ grep -c dump-sm src/driver/scrip.c
0
$ ./scrip --dump-sm corpus/tests/rebus/binary_trees.reb </dev/null; echo "rc=$?"
scrip: cannot open '--dump-sm'
rc=1
$ awk '{print $1}' scripts/lower_baseline.txt | sort | uniq -c
     30 d41d8cd98f00b204e9800998ecf8427e
$ printf '' | md5sum
d41d8cd98f00b204e9800998ecf8427e  -
```

`--dump-sm` is not a flag. It hits the driver's treat-any-unrecognised-argument-as-a-filename
fallthrough (the same behaviour that makes `./scrip --help` print `cannot open '--help'`), so every one
of the 30 cases produces **empty stdout**. The gate hashes that empty output and compares it against a
baked hash that is *also* md5 of the empty string. Not some of the 30 — **all thirty**.

Its last green run before the cure: `PASS=5 FAIL=0 SKIP=25`, exit 0. The five passes were five empties
matching five empties.

## ⭐ Why it survived: a bake step is not an independent check

`--bake` runs the **same broken invocation** and writes down whatever it gets. A baseline generated
through the instrument it is meant to police cannot disagree with that instrument — the defect is
laundered into the expected values, and the gate becomes perfectly self-consistent and perfectly empty.

This is the general form and it is not specific to SR-1: **every bake-and-compare gate has this hole.**
The cure is that the bake must assert its own output is non-trivial *before* writing it. That is the same
law `corpus_suite_harness.py` already carries three separate copies of one layer up ("agreement on
nothing is not agreement"; `all_agree and not ora_text.strip()` refuses to mint). SR-1 is that law's
counterexample at the gate layer, where nobody had applied it.

## ⚠️ A second defect hid the first

25 of the 30 case paths went stale in the corpus re-grid (`corpus/demo/` → `corpus/demos/`,
`tests/{icon,prolog}/demo/` → `demos/`, and 19 witnesses absorbed into their language masters). The
loop `SKIP`ped them, so only 5 cases ran and the gate read as *partial*. **Had all 30 paths resolved it
would have printed `PASS=30 FAIL=0` and read as a comprehensive six-frontend byte-identity gate.** The
staleness was the only thing making the number look small enough to be uninteresting.

## What was done, and what was deliberately not

The gate now **REFUSES rc=2**, naming the missing flag, the md5("") evidence, and the two acceptable
cures. Its six recoverable paths are repointed so the table is accurate for whoever takes it.

Deliberately **not** done: silently rebasing SR-1 onto `--dump-ir`/`--dump-bb`. The question SR-1 asks is
legitimate, but pinning IR hashes as goldens is a design call with a live precedent against it
(`RULES.md`: `.s` artifacts must never be wired into a gate), and that is not a ruling to make inside a
repair. The other 19 witnesses are all recoverable **by origin** through `lib_master_extract.sh` —
`feat__f01_core_labels_goto`, `parser__arr_get`, `corpus__sc1_literals`, … — so a rebase has no
rediscovery cost.

**Row wanted:** `sr1-lower-gate-instrument-is-gone-rebase-or-retire`. Either rebase onto a real dump flag
with a non-trivial-output assertion in `--bake`, or retire SR-1 and drop `demos/{icon,prolog}` from the
manifest's GATED bucket — because right now the manifest declares them gated by this.

## The cheap test this generalizes to

For any gate you rely on: **run its instrument by hand once and look at the bytes.** Not the summary
line, the bytes. `PASS=5 FAIL=0` and `PASS=30 FAIL=0` are the same sentence whether the underlying
output is a bytecode dump or nothing at all, and the summary is the only thing anybody ever reads.

Related: `RULES.md` § A CORRECT PROCEDURE WITH A FALSE EXPLANATION; the `make test` no-recipe false-green
trap (hq_P s268); `FINDING-2026-08-30-hq_B-a-deleted-guard-has-no-failing-test-two-were-removed-unmentioned.md`.
