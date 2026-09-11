# FINDING — a generated sidecar failed two OPPOSITE ways, and a keeper declaration was invisible to the machine that enforces it

**hq_V, 2026-09-10 19:xx – 2026-09-11 (`date`-read), MODE NONET, ICON ONLY.** Trees: SCRIP `a3eab74ad` → `c265bdcc1`,
corpus `98c3e82ea` → `379837dcc`. Rulings: CEO-545 (the sidecar), CEO-463 (a red you did not cause).
No board run — ONE RUNNER, ONE BOARD (CEO-523). Every number below is a per-entry or scratch-tree measurement.

## 1. `ALL.excluded.txt` COULD BE EDITED AND NOT HONOURED — IN TWO OPPOSITE DIRECTIONS

The file is written by a MERGE (`_excl_existing.update(...)`), which produces two failures that look nothing alike:

| edit | what happened | why it matters |
|---|---|---|
| **DELETE** a line the builder still computes | **silently reverted** by the next full build | the retraction vanishes with no word said |
| **ADD** a line the builder never computes | **survived forever**, unchallenged | this is how a WRONG exclusion becomes permanent |

Both measured in a scratch tree BEFORE any code changed: `rung36_jcon_io` deleted by hand came back;
an invented `zzz_invented_family` was still present after two full builds.

⛔ **THE SECOND IS THE WORSE HALF AND IT IS THE SHAPE THAT ALREADY COST FOUR CYCLES.** A bare name in this
file makes the suite runner `continue`, so the program leaves the denominator entirely — **it cannot be red,
so nobody looks, so the ruling is never re-read.** That is precisely how jcon `kwds` was carried by a closed
exclusion I wrote myself. An artifact that accepts an invention and never challenges it is a machine for
manufacturing invisible rulings.

**CURE (CEO-545):** the builder stamps `# builder-digest: <sha256>` over the sorted `key<TAB>value` DATA lines
and REFUSES rc=2 when the file no longer matches. Comments and order are excluded from the digest: the header
is prose a human maintains, the data is what the builder owns. All three writers covered in one change.

**COSTS, named because the ruling asked:** (1) a hand edit now needs a rebuild — the point, and it convicts my
own edit an hour earlier, so the escape hatch is documented *in the refusal message*; (2) the digest cannot
tell an invention from another RUN's legitimate output, so every writer had to be covered at once — a missed
writer would refuse the next honest build; (3) other languages migrate on their next build rather than refuse,
because a guard that fires on its own introduction is not a guard; (4) a git merge conflict here now surfaces
as a refusal, which is correct and will surprise someone once.

⛔ **THE NON-REGRESSION THAT MATTERED MOST: `MODES.tsv` SHARES THE HELPER AND MUST NOT BE GUARDED.** Its
contract is DECLARED, NEVER DERIVED — every row is hand-written with its evidence. Guarding it would refuse the
file's own intended use on the next build. The digest is opt-in per call site, and an arm proves MODES.tsv
takes a hand row, keeps it, and receives no digest.

**Nine arms wired** into `test_gate_master_suite_deferral_and_scope.sh` (21 → 30 assertions) **and proved to
bite**: with the builder reverted to its unguarded HEAD the two detector arms and the migration arm read RED
while the false-positive control stayed GREEN. ⭐ A detector arm that fails open reads as *"there was never a
bug here"* — checking the direction is not optional.

## 2. A KEEPER DECLARATION WAS INVISIBLE TO THE MACHINE THAT ENFORCES IT

`an_ordinary_call_chain_prints_every_frame_in_the_traceback` was declared in `tests/icon/KEEP.md` — correctly,
in its own landing commit, with its reason. The deferral contract is a **delimited substring search for the
file's BASENAME** (`_declared_in_keep`, and the same shape in the conversion gate's grep). The declaration was
spelled **without the `.icn` suffix**, so it matched nothing.

**MEASURED, two arms in a scratch tree:** name bare → `--absorb-only` **ABSORBED** it (956 entries); `.icn`
added → the same command **REFUSED** it, *"KEEPER, declared in KEEP.md"*. Absorbing it would have renamed a
program whose ref carries its own file name on **4 lines** — a red manufactured out of a rename, the exact
outcome that entry exists to prevent.

⛔ **A DECLARATION THAT READS CORRECTLY TO A HUMAN AND TO NOTHING ELSE IS NOT A DECLARATION**, and it fails in
the direction nobody re-checks: the file just sits there looking declared.
⚠ **THIS CORRECTS MY OWN HQV-28**, which called that file's orphan status *"bookkeeping lag, no build had run
since"*. It was not lag. The declaration was unreadable, and a build would have made it **worse**, not better.
⭐ And the opposite spelling is deliberate three sections above it: `rung03`'s names are bare **on purpose** so
a RETIRED entry stops holding the block live. **Same mechanism, opposite intent; only the entry's direction
tells them apart.** Both are now named in the file so the next reader cannot guess wrong.

## 3. THE "UNCONVERTED" BACKLOG WAS MOSTLY DUPLICATES, WHICH IS WHY IT DID NOT MOVE FOR A DAY

`test_gate_suite_conversion_complete.sh icon` reported 20 files *"neither converted nor declared"*. **Eighteen
were already IN the master** — their loose copies had simply never been deleted — and only two were genuinely
new. ⭐ **A duplicate left beside its absorbed entry is indistinguishable, to both that gate and the orphan
census, from a witness nobody converted — and the two want OPPOSITE cures, delete versus absorb.** Reading the
gate's own message as its diagnosis is what kept the number frozen while it looked like a mountain of work.

All 18 were content-verified against their existing entries by the builder's own `--delete-absorbed` before
removal. Result: **icon orphans 0/201, the first language to reach that ratchet's intended terminal value**,
and the icon conversion gate GREEN. Icon master across the sitting: **939 → 950 → 953 → 955 → 957**.

## NAMED, NOT MINE
- `scripts/test_icon_ir_rung_03.sh` globs `/home/corpus/icon`, which does not exist here, and is wired into
  nothing. It exits **rc=1**, so it fails closed rather than passing vacuously — a dead instrument, not a false
  green. Its sources now live in the master as `procedure_every_suspend_8/9/10/11`. → hq_T.
- `test_gate_icn_port_trace.sh` reads 22 failed checks of 24; reachable from SCRIP `a3eab74ad` (the `&trace`
  suspend/resume landing), not from anything here.
- `test_gate_snobol4_master_named_set_equality.sh` is RED on two long-deleted SNOBOL4 pairs
  (`rtx11_dynvar_include`, `m1_include_sort_loop`). **Proved pre-existing rather than argued:** the verdict is
  byte-identical with my edit reverted. Its `cut -f1` fragility IS repaired here, because this change made a
  latent bug reachable — that file has always been able to carry comment lines, and now it always will.
