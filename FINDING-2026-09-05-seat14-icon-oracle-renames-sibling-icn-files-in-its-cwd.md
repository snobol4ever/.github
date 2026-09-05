# FINDING 2026-09-05 seat14 — the shared Icon oracle renames every sibling `.icn` file in its cwd

**Seat:** seat14 · **Row:** `every-vendored-package-absorbed-into-the-one-liner-or-multi-liner-python-harness-with-oracle-cut-refs` (hq_T lane) · **Mode:** FLEET-20
**Trees graded:** SCRIP `674319235` + this fix · corpus `4e11cb9ee` + this container · .github `e8acdfe7`
**Build:** incremental `make`. Box clock 2026-09-05 ~14:00–14:36 CDT.

## 1. The defect, in one sentence

Running `icon_bin()`'s resolved oracle (`/home/resources/icon-master/bin/icon`, a symlink to `icont`) against
a `.icn` file whose `cwd` (per `run_oracle()`'s own contract) contains sibling `.icn` files renames **every**
sibling in that directory to an all-uppercase filename, byte-identical content, as a side effect — reproduced
**3/3**, confined each time to exactly the one directory being worked (`corpus/packages/icon/ipl/progs/`, 335
of 851 shipped files, every file in that directory, none outside it).

## 2. How it was found, and the two shapes of damage

Building `util_build_package_suite.py`'s container for `ipl` (851 files, the last OWED Icon package) crashed
837/851 files in with `FileNotFoundError: .../progs/url2link.icn` — a file `glob()` had listed as lowercase
at the top of the run no longer existed by the time the loop reached it alphabetically. `git status` on the
untouched corpus tree showed **335 tracked-as-deleted / 340 untracked** paths under `progs/` — every
byte-identical to `git show HEAD:<path>`, confirmed programmatically for all 335 before touching anything
(not sampled). `core.ignorecase` is unset (ext4, case-sensitive, confirmed directly), the reflog shows nothing
but ordinary rebases/commits, and mtimes are unchanged by the rename (`mv`/`rename()` don't touch mtime) — so
this is not a git artifact, not a stale prior session's leftover, and not filesystem case-folding. It
reproduced **identically** across three independent from-clean attempts, always confined to `progs/`, always
this same file set. The regenerated debris each time is also a clue to the mechanism, not just noise: two
always-empty files (`FOO.ICN`, `FOO.ICN.BAK`), a differently-random-numbered empty file each run
(`48476091` / `57300786` / `78026074`), and once a file named literally `XXXXXX.ICN` — an unsubstituted
`mktemp`-style template used as a real filename — holding a **different** shipped program's content
(`zipsort.icn`'s). I did not chase this into `icont`'s own internals (a vendored third-party binary, not this
project's source); the isolation fix below sidesteps the mechanism rather than explaining it.

**A second, worse shape only surfaced by verifying the container was CORRECT, not just non-crashing**
(this project's own standing rule). A first attempt at a fix made `read_text_tolerant()`'s call site tolerant
of the file having vanished — read via whichever case exists on disk right now, keep the container's own
entry name at its original (glob-time) casing. That stopped the crash but not the damage: `progs/what`'s own
output echoes its invocation name (`Usage: what.icn ...` / `Usage: WHAT.ICN ...` depending on whether the
mutation had already fired by the time ITS oracle ref was cut). Spot-checking 4 absorbed entries against a
fresh independent oracle run (this project's own "verify correct, not just green" standard) found **3 of 4
mismatched** under that first fix — one of them (`what`) because the ref had been cut against a mutated
filename the container never records the entry under. A ref cut under the wrong name is worse than a crash:
it is a **false-disagreement generator** — SCRIP would be blamed later for disagreeing with ground truth that
was never really this program's own.

## 3. The cure

`scripts/util_build_package_suite.py`: every oracle invocation now runs against a **byte-copy of the one
source file, in its own fresh `tempfile.TemporaryDirectory()`**, instead of the file in place. Nothing else is
present in that directory for the oracle to rename; the real corpus tree is never touched by this builder
again, for any package, in any language. This is not a novel invocation contract — it is exactly this
package's own `README.md`: `cp progs/hello.icn /tmp/t.icn && cd /tmp && icont -s t.icn`.

**Regression, measured not assumed:** rebuilt `aisnobol` (already-committed, smallest SNOBOL4 package) with
the isolated builder — `ALL.sno` / `ALL.ref` / `ALL.csv` all **byte-identical** to what's on disk already.
The `run_oracle()` design note this touches (`corpus_suite_harness.py:302-307`, ARGV IS THE BARE BASENAME,
CWD IS THE FILE'S OWN DIRECTORY) is about **argv** staying a bare name so a diagnostic that echoes it is
reproducible across runs — isolation changes *which* directory that stable name lives in, never what gets
passed as argv, so that guarantee survives untouched; confirmed empirically, not just by re-reading the
comment.

**Re-verified after the fix:** `ipl`'s real corpus tree shows **zero** mutation across a full 851-file run
(`git status` clean but for the 5 new `ALL.*` container files); `progs/what` now matches an independent fresh
oracle run exactly; the container's `SUITE_BOARD` is unchanged (`m3 23p/53f/2c`, `m4 23p/20f/2c/33s` of 78) —
the fix corrects a fidelity defect in how the ref was cut, it does not (in this case) flip any verdict, and
would not be expected to unless a future SCRIP change makes this specific name-echo class of output start
mattering to a comparison.

## 4. Why this matters beyond `ipl`

The cure lives in the ONE shared builder every package/language container goes through
(`util_build_package_suite.py`), so every future package this task's own row builds is protected by
construction — nobody has to remember "isolate Icon specifically," and nothing about the fix is Icon-specific
(it isolates by construction, regardless of which oracle or language triggers a directory-wide side effect).

## 5. Net result on the row's own DONE-WHEN

`ipl` (icon, 851 shipped): **78 absorbed, 773 excluded, balanced.** Committed: SCRIP (builder isolation fix),
corpus (`ALL.icn`/`ALL.ref`/`ALL.csv`/`ALL.excluded.txt`/`ALL.wantrc`). Task file's own NEXT block carries the
current DONE-WHEN re-run and what remains.
