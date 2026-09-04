# FINDING 2026-09-04 hq_B — a duplicate entry name in the icon master disabled the builder for the whole language

**Row:** `icon-every-non-package-source-that-runs-with-output-absorbed-into-the-master-with-oracle-refs`
**Tree at measurement:** SCRIP `ae9ebfc20` · corpus `a0bc89d89` · RT_OPT=-O0 · build: incremental `make`

## What was measured

`python3 scripts/util_build_master_suite.py --lang icon` — any form, dry run included — exited **rc=2** and
refused, for every seat, on every tree:

```
⛔ REFUSED: this rebuild would DROP 1 origin(s) the master already holds.
   Dropped origin(s):
     probe_witness__witness_icn_carve_leak_lucky
```

The named origin **was not missing**. `corpus/tests/icon/probe_witness.icn` still carries
`witness_icn_carve_leak_lucky` at its line 50. The refusal's own explanation — *"absorbed from outside this
tree, or their sources retired"* — was false in both halves, and it is the explanation a reader acts on.

## The actual mechanism

`corpus/tests/icon/ALL.icn` held **two different programs under one name**, `procedure_scan_tab_2`, at seq
631 and seq 748 (a `tab(2)` scan witness and a real-coercion `tab(0)` witness — unrelated bodies). The flat
master namespace is documented as one that *"cannot collide; a collision REFUSES"*.

The collision then propagated through a dictionary, not through the collision check:

```python
# util_build_master_suite.py:1070-1076
_csv_origin[_row["entry"]] = _row.get("origin", "")   # keyed by entry NAME
for e in base_entries:
    e.origin = _csv_origin.get(e.name) or ("master__%s" % e.name)
```

Two CSV rows share the key, so the second overwrites the first. **Both** base entries were then handed
origin `probe_witness__icon_real_scan_coercion_exponent_threshold`, and
`probe_witness__witness_icn_carve_leak_lucky` vanished from `base_origins` — whereupon
`dropped = known_origins - written_origins` reported it as about to be destroyed.

⭐ So the guard fired correctly on evidence that its own reconstruction step had manufactured. The
identity check is right (`A COUNT CANNOT DETECT A SUBSTITUTION`, per its own comment); the *input* to it
was lossy, one layer up, in a dict literal that has no idea it is holding an identity.

## Where the duplicate came from

`probe_witness` holds **15** entries in the master and **11** banners in its source. Ranks 746, 747, 748,
749 — the last four in the file — carry origins (`icon_image_missing_serial_number_suffix`,
`icon_level_keyword`, `icon_real_scan_coercion_exponent_threshold`, `icon_scan_subject_size`) that appear
nowhere in `probe_witness.icn`, whose entries are all named `witness_icn_*`.

They were appended to the master by some path other than the builder. That path did not run the builder's
counter seeding —

```python
for e in base_entries:  # seed the counters PAST every existing name so new names never collide
```

— so `procedure_scan_tab` was numbered from scratch and minted `_2` a second time. **The seeding logic is
correct and was simply not on the path that did the writing.** ⛔ The builder's end-of-run `dup` refusal
would also have caught it; the drop-origin check runs earlier and refused first, so for months the
symptom presented as a retired source rather than as a name collision.

## Cure landed

Renamed the seq-748 entry to `procedure_scan_tab_10` (next free; `_1`..`_9` were taken) in `ALL.icn`,
`ALL.ref` and `ALL.csv` — three lines. Banners were re-minted through `h.make_banner_cfg`, the harness's
own authority, **not** hand-computed: a hand-computed dash run produced an 81-char banner where the format
is 80, and nothing would have complained until a reader hit it.

After the rename the builder runs (rc=0) and the board is unchanged and green: entries 749, run-graded m3
598/598 · m4 598/598, ast 153/153, FAIL=0.

## What is worth keeping

⛔ **A guard that reconstructs its own input can accuse the wrong party.** The refusal named a *source
file* as retired; the defect was two rows in a CSV sharing a key. Anyone who trusted the message would have
gone looking in `corpus/` for a file that was sitting right there, or — as the message explicitly offers —
reached for `--allow-drop-origin=probe_witness__witness_icn_carve_leak_lucky`, which would have **deleted a
live entry from the master** to silence a report that the entry was missing.

⭐ **An append path that bypasses a builder inherits none of its invariants.** The four hand-appended
entries are individually fine — they pass in both modes. What they skipped was the numbering discipline,
and the cost landed on a completely different seat, months later, as a refusal about something else.

## Follow-on

- The four entries at ranks 746-749 remain attributed to `probe_witness` with origins its source does not
  contain, so `probe_witness` can never satisfy byte-equal-or-no-delete and stays permanently
  `UNVERIFIED (kept)`. Correct behaviour by the builder; a provenance defect in the data. Not cured here —
  re-attributing them needs whoever appended them.
