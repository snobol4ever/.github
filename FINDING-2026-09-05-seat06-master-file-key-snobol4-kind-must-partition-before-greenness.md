# FINDING — 2026-09-05 (seat06, FLEET-8, hq_T's lane; row `three-master-builder-gates-are-red-at-head-and-none-is-in-make-test`, rank 1)
# THREE MASTER-BUILDER GATES CURED BY A ONE-TIME RESORT, PLUS A REAL TOOL BUG ONLY SNOBOL4 COULD EXPOSE

**Tree at measurement:** SCRIP `df9fe6af0` + this change, incremental `make` (RT_OPT `-O0`, `Makefile:34`). corpus `5e6367ccf` + this change. Box clock 2026-09-05. Measurer seat06.

## 0. THE THREE GATES, TRIAGED SEPARATELY AS THE ROW ASKED

`test_gate_master_order_is_the_builders_order.sh`, `test_gate_master_builder_reindex_only.sh` and `test_gate_master_suite_builder_contract.sh` were all red at HEAD and none was in `make test`. Per gate:

- **Order gate:** pascal/prolog/raku/snobol4 had simply never been re-sorted since the level-ordering law landed (ceo 2026-09-03) — a promotion changed entries' sort keys without a follow-up `--resort`. **GATE correct, BUILDER correct, DATA stale.** Cured by running `util_build_master_suite.py --resort` per language (corpus `5e6367ccf`); content-invariant per the tool's own round-trip verification (9106 insertions / 9106 deletions, same entries, same bytes, order only).
- **Reindex gate (LANG_T=prolog):** arm (a) failed because the committed prolog index disagreed with a fresh `--reindex` for the *same* stale-order reason as above; arm (b) ("corruption survived — copying, not recomputing") was a **downstream symptom, not an independent defect** — `reindex_csv_only()` demonstrably recomputes `n_lines` fresh from the re-read master (confirmed by code reading, then by test: both arms pass once the stale baseline is fixed). No code change needed here beyond the resort.
- **Builder contract gate:** two independent bugs, both in the gate script, neither in the builder:
  1. `added` (set only inside arm D's `else` branch) was read unconditionally by arm E under `set -u`, throwing "unbound variable" whenever arm D took its UNPROVEN branch. Fixed by binding `added=""` up front.
  2. Arm D's population (one loose absorbable icon pair, discovered at runtime specifically so no hardcoded witness could go stale — hq_T 2026-09-03) had gone empty from ordinary corpus absorption. **This is the third occurrence of the exact class the gate's own header already documents happening twice** (arms C and D both went stale from corpus churn absorbing away whatever witness was current). Cured structurally rather than by picking a fourth witness: `reset_icon()` now plants a synthetic, uniquely-named absorbable pair (`zz_contract_gate_synthetic_absorbable`, plus its `config/MODES.tsv` line) into the scratch tree on every reset, so arm D always has something to scope `--absorb-only` against regardless of how much of the real corpus has been absorbed by the time this runs.

## 1. ⭐⭐ THE PART THAT GENERALISES: `master_sort_key` NAMES AN ORDER THE FILE FORMAT CANNOT STORE FOR A MIXED-KIND MASTER

Resorting snobol4 (818 `kind="line"` + 1041 `kind="block"` entries) hit a THIRD failure `--resort` itself refused: *"re-read order does not match the intended order — not committing."* This is not stale data — the committed snobol4 ALL.sno physical order and ALL.csv row order **already agreed with each other** before I touched anything (verified: reading ALL.sno via `read_suite` and reading ALL.csv both produce the identical 1859-name sequence).

The actual defect: `write_suite()` **always** emits every `kind="line"` entry before every other entry, unconditionally — its own docstring explains why (a format-(B) block ends only at the next banner or EOF, so a one-liner written after a block is silently swallowed into it; measured before, hq_C 2026-08-28, `ev_fn_beauty_shape` duplicated). `resort_master()`'s own post-write verification, and separately the order gate, both compared the physical result against **plain `master_sort_key` order** — an order that ignores `kind` and that `write_suite` cannot physically produce whenever a `line` and a `block` entry would need to interleave. For every other language every entry shares one kind, so the bug was invisible; snobol4 is the only master where it could ever fire.

**Cure:** added `master_file_key(entry, flags)` beside `master_sort_key` — `(0 if kind=="line" else 1,) + master_sort_key(...)` — and switched every ordering call site (`resort_master`, the main absorb-path's level-ordering sort, and the order gate's `want` computation) to it. Byte-identical behaviour to `master_sort_key` for every single-kind master; for snobol4 it names the order the format can actually hold.

**Also cured while here, same root cause, higher blast radius:** the *main* absorb-path (`main()`'s plain, non-resort build) computes `all_entries` in this same order, writes it via `write_suite`, then writes `ALL.csv`'s `rank` column from that **pre-write** ordering rather than from what was actually written — and its round-trip check only compared entry **count**, never order. So a plain snobol4 rebuild could silently write a CSV whose `rank` disagreed with the physical file the next time absorption ran, which is exactly the *"silently mis-paired ALL.sno/ALL.ref/ALL.csv"* failure mode this row's own GOAL names as the expensive one. Strengthened that round-trip check to also refuse on order mismatch, not just count.

## 2. WHAT THIS DOES NOT CLAIM, AND THE QUESTION I'M ROUTING RATHER THAN DECIDING

`master_file_key` makes `kind` the **outermost** sort criterion, ahead of `xfail`. For snobol4 that means: within the physical-order constraint, `rank <= N` selects the greenest N **one-liners**, then the greenest N **blocks** — never a cross-kind interleave by pure greenness. That is a real, permanent property of the current file format (a one-liner literally cannot be stored after a block), not something I introduced or could avoid short of changing how the suite file itself is parsed (blocks would need an explicit end marker instead of "next banner or EOF"). I have not formed a view on whether that parser change is worth making versus living with kind-then-greenness as the level law's shape for the one mixed-format language. Routing to hq_T via `ask master-file-key-kind-before-greenness`.

## 3. WHAT LANDED

- SCRIP: `master_file_key()` added (`util_build_master_suite.py`); three call sites switched to it; main-path round-trip check strengthened to verify order; `added=""` bound and a synthetic arm-D fixture added in the contract gate; all three gates wired into `make test` (previously in none).
- corpus: pascal/prolog/raku/snobol4 masters resorted, content-invariant.
- DONE-WHEN (this row) proven GREEN verbatim, including the `grep` for the contract gate in `Makefile`.
