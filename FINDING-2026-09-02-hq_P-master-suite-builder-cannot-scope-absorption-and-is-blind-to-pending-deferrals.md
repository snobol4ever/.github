# FINDING 2026-09-02 hq_P — `util_build_master_suite.py` cannot scope ABSORPTION, and it is blind to `PENDING.md`/`KEEP.md`

**Row:** `icon-rung-ladder-absorption` (hq_P). **Tree:** SCRIP `c6190d9e` (pristine `-O0`), corpus `6a9f01fe4`.
**Status of the tree after this work: CLEAN.** Every experiment below was reverted; `corpus` md5s match the
pre-session baseline exactly (`ALL.icn` `4cdb8958…`, `ALL.csv` `d143c7c4…`, 534 entries / 308 families).

## 1. The two halves of the consolidation workflow disagree by construction

`test_gate_suite_conversion_complete.sh` **enforces** the deferral contract: a loose file may stay loose only
if `PENDING.md` points it at a **live** row, and a deferral whose row has gone `DONE` is a **stale-deferral**
gate failure (*"convert these now"*).

`util_build_master_suite.py` **does not read `PENDING.md` or `KEEP.md` at all** — `grep` returns zero
references to either. The gate polices deferrals; the builder cannot see them.

⛔ **Consequence: there is no supported way to convert the files the gate demands you convert, without also
absorbing every other eligible loose file — including the ones deliberately deferred to other seats' live rows.**

## 2. `--only` / `--family` scope DELETION, never ABSORPTION — measured

The script says so itself when it refuses: *"`--family`/`--only` scope what `--delete-absorbed` deletes"*.
So the selector does not narrow what is absorbed. Witnessed on `tests/icon`:

```
util_build_master_suite.py --lang icon --only rung36_jcon_scan,rung36_jcon_scan2 --delete-absorbed
  -> master WRITTEN: 534 -> 536 entries, 308 -> 310 families
  -> families actually absorbed: coexpr_gc_stack_witness, rung38_all
  -> families requested:         rung36_jcon_scan, rung36_jcon_scan2   (NOT absorbed)
  -> then: REFUSED rc=2 "--only ... matches zero of the 179 verified families this run -- nothing to delete"
```

Three separate defects visible in that one run:

- **It absorbed the families that were NOT asked for, and not the ones that were.**
- ⛔ **It writes the master BEFORE it refuses.** `rc=2` here is **not** a no-op — the caller must `git checkout`
  to undo it. A refusal that has already mutated shared state is not a refusal.
- ⛔ **`coexpr_gc_stack_witness` is the live DONE-WHEN witness of row `coexpr-stack-leaves-the-compacting-gc-heap`.**
  Absorbing it reaches into another row's acceptance test. It and `rung38_all` are both on the builder's own
  **MODE UNKNOWN / UNPROVEN** list, so the run silently promotes unproven families into the graded master.

## 3. The script has no `--help`, and probing it with one MUTATES A DIFFERENT LANGUAGE'S MASTER

`sys.argv` is parsed by hand (`:519–580`); there is no `argparse`, so an unrecognized flag is **silently ignored**
and the run proceeds **with defaults — `--lang snobol4`**.

⛔ Measured: `python3 util_build_master_suite.py --help` rebuilt the **SNOBOL4** master, modifying six shared files
(`tests/snobol4/ALL.{csv,excluded.txt,in,ref,sno,xfail}`, **2335 insertions / 2344 deletions**). Reverted immediately;
no damage. ⭐ **The lesson is the shape: for this script the universal "ask it what it does" gesture is a write to
shared corpus.** Read the argv block; never probe it with a flag.

## 4. What is NOT broken, so nobody re-derives it

- ⭐ **`rung36_jcon_scan.icn` and `rung36_jcon_scan2.icn` are genuinely CURED and ready to convert.** Their row
  `icon-scan-env-value-residue` is `DONE`, and both files, **both modes**, now exit 0 with output **byte-identical
  to their `.expected`** (`scan` was 115 lines against `.expected`'s 133; it is now 133 and matches). The
  stale-deferral gate failure is correct and actionable — it is the *absorb tooling* that blocks it, nothing else.
- ⚠️ **Do not grade `scan` against Arizona `icont`.** It cannot compile it: line 3 `record array(a,b,c,d,e,f,g);`
  → *"`;`: invalid declaration"*, the documented SCRIP semicolon-required divergence. `.expected` is the reference.
  ⛔ I nearly filed a false "oracle differs" from this: `icont` failing meant **no output file was produced**, and
  the diff ran against a **nonexistent file**, printing as *"0 differing lines"*. **A diff against a missing file is
  not a comparison** — the same false-signal class as an absent oracle printing a plausible all-FAIL board.

## 5. The cure (routed to ceo, not taken here)

Either one closes the gap; the second also fixes it for **every** language's consolidation row:

1. An **absorb-side** selector (`--absorb-only <families>`), so the set absorbed can be narrowed to what a row owns; or
2. Make the builder **honour `PENDING.md` and `KEEP.md`**, so deferred and keeper files are never absorbed and the
   builder agrees with the gate that polices it.

Independently worth doing: give the script a real `--help` (or make an unknown flag `REFUSE rc=2` rather than run
with defaults), and make it write the master **only after** its selector checks pass.

## 6. Also landed this pass

`icon-rung-ladder-absorption`'s `DONE-WHEN` was the mint placeholder — *"MUST BE MADE RUNNABLE BEFORE done CAN EVER
PASS"* — so the row was **unclosable by construction**. (My own defect: I minted it 2026-08-30 without one.) It now
runs and checks: suite-conversion gate green · **0 duplicate origins** in `ALL.csv` (the no-dedupe doubling hazard
the GOAL names) · families `>= 308` · entries `>= 534` · icon smoke `FAIL=0` both modes. ⭐ **Proven by making it
FAIL** — it exits 1 today at the gate check. `test_gate_baton_donewhen_runnable.sh` no longer lists this row
(74 batons of 632 still do).
