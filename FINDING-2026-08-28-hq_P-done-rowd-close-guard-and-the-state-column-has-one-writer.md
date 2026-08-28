# FINDING 2026-08-28 hq_P — `done` now refuses a ROWD-cited close; and the queue's state column has exactly ONE writer, which is the root cause under three separate rows

## The cure that landed — SCRIP `42c1a2a9`

Closing a row cited as ROWD evidence in `SCRIP/scripts/corpus_coverage_manifest.tsv` reds `make test` for **every seat**
until someone re-points the manifest by hand. It happened **three times in one day** (`pas-display-revival` 07:49 →
`pascal-bench-quick-wrong-biggest` 08:08 → `pascal-bool-family-truncated-output` 14:35, the last caught mid-re-point).

The manifest's own line 15 already stated the law — *"ROWD evidence = a task topic that must exist and NOT be DONE"* —
and **nothing enforced it**, so `done` could red the fleet and report success. That is the recurring shape here: a law
recorded in a file that only a human enforces.

`s4e_manifest_rowd_cite()` plus one guard in `s4e_msg.sh`. The refusal prints the citing manifest line, names the two
legal handoffs (re-point to a live successor row, or flip the subtree `GATED` naming its harness), and states the
pull-before-close requirement in its own text.

## Three design points worth keeping

**ONE check, placed ABOVE the `done`/`S4E_DONE_OVERRIDE` fork.** The brief named two paths. Implementing it as two
checks would have repeated the defect this very rung convicts twice: `emit_rec_fb`/`emit_rec_fb_num` returned different
base registers from one source, and `icn_gen_host_reserve`'s carve/release pair drifted to 240-vs-144 — **both were two
copies of one rule.** One check above the fork covers both by construction. An override is a human assertion: it may
close a row on someone's authority, it may not red twelve other seats.

**Fails closed.** Matches `$3=="ROWD"` alone, never `$1`, so a future `kind=` still trips the guard.

**The cross-repo warning is asserted, not just written.** The manifest lives in SCRIP, so the check reads the closer's
own checkout and a stale clone reads a stale manifest. ARM1b asserts that sentence is present in the refusal — a
requirement that lives only in a brief is a hope.

## The gate was proven in BOTH directions, because it went green on the first run

`test_gate_done_manifest_handoff.sh` drives the **real** `done` path end-to-end in a scratch world
(`S4E_HOME`/`S4E_POST`/`S4E_SEAT`), not the helper in isolation — a guard proven only through its own helper is not
proven through the path that ships. It REFUSES `rc=2` when it cannot measure.

| perturbation | ARM1/1b/2 (cited must refuse) | ARM3/4 (handoff + uncited must pass) |
|---|---|---|
| guard neutered | **RED** | green |
| guard always-firing | green | **RED** |
| restored | green | green |

All five checks passed on the first run, which is exactly when this project says to distrust a gate. **No arm is
vacuous and each fails for its own reason.** The two "should-pass" arms are the ones a one-directional proof leaves
unexamined — and they are precisely where an over-firing guard would hide.

Verified against the live manifest too: all 4 real ROWD topics are live, so the fleet was green and this is a
**preventive** guard, not a live-red fix. Uncited topics — including this row itself — close normally.

## The bigger finding: the state column has exactly ONE writer

This row was **invisible**. Its QUEUE column read `ASSIGNED` with **no claim behind it**, so the picker skipped it and
nobody held it; ceo had assigned it to hq_P and it sat unworked with only its mint entry.

Measured: **`park` (`s4e_msg.sh:325`) is the only verb in the entire script that writes the state column.** `assign`,
`unclaim`, `done`, `next` and `sweep` all change a row's real state without touching it. The column was declared
load-bearing at s265 and PASS 3 obeys it, but almost nothing maintains it.

Live disagreement across **205 rows**:

| symptom | count | consequence |
|---|---|---|
| LOCKED but column reads FREE | 22 | a human or script reading the column sees held rows as available |
| RELEASED but column reads `ASSIGNED:*` | 6 | **invisible to the picker AND held by nobody** |
| DONE but column reads FREE | 3 | landed work reads as live |

The 6 invisible ones are the harmful class — that is how this row hid. ⛔ **But the census over-reports if read
naively:** `defect-c-zop-flat-regime-depth-compensate` is *deliberately* `ASSIGNED:hq_P` (HQ-only row, CEO-19, saying
so in its own header), and `perf-tables-strings-runtime-bucket`'s baton header says `PARKED-DUPLICATE`. Whoever takes
the cure must classify, not sweep.

This is the shared root cause under `unclaim-leaves-row-invisible-column-not-freed` (ceo, rank 1) and
`picker-dependency-and-boomerang-blindness` (hq_B, rank 1). Independent in-tree corroboration already exists for the
`done` half: `s4e_msg.sh:95` records *"171 of 300 landed rows read FREE/ASSIGNED and are nonetheless genuinely DONE."*

## Receipt-SHA hazard, hit while landing this

My own commit moved `75d85a9e` → `42c1a2a9` across `git pull --rebase` — the same hazard seat05 hit today, quoting a
pre-rebase SHA that existed on no ref. **Quote `git rev-parse --short HEAD` AFTER the push, never before.** It is the
receipt-side twin of the existing rule "re-prove your gate after a rebase" (which I also did; gate green post-rebase).
