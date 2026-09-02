# FINDING 2026-09-02 (hq_B) — the construct-ladder runner and the rung 0–5 witnesses are on origin, measured failed-once / passed-once / refused-once on the pre-cut tree; the r9-reload veneer patch is a parked row, not a landing

**Tree:** SCRIP `6faa3215` (runner + trace-gate extension) · corpus `1d4ff901` (12 `ladder__rungNN_*` entries, swipl refs, 24 trace blocks) · measured against the pre-cut compiler `f4532dea` · `RT_OPT=-O0` · MODE `TRIO` (file read). Lane: `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § E *instrument lane, parallel to rung 0, never on `src/`* (ceo telegram `rung-0-landed`, .github `9fd7c67a`); law `RULES.md` § THE PROLOG REBUILD GATE clause 4. Coordination: hq_C owns `src/` (the cut + hello) and was told by mail (`ladder-runner-landed`) not to mint a duplicate runner.

## What landed

| piece | where | shape |
|---|---|---|
| `scripts/test_prolog_ladder.sh` | SCRIP | `--to N` grades rungs 0..N cumulatively; population = every `ladder__rungNN_<slug>` origin of `corpus/tests/prolog/ALL.csv` (keyed on the CSV `origin` column, never the builder-renamed entry name, never a filename glob), extracted by origin through `lib_master_extract.sh`; each witness ALONE in m3 (`--run`) and m4 (`--compile -o` + `as --64` + `gcc -no-pie` + run); verdict = stdout byte-equal to the `.ref` AND rc equal to `ALL.wantrc`'s declared rc; prints its denominator; REFUSES rc=2 on zero witnesses, a missing master, a bad `--to`; `--list` prints the population. ⛔ XFAIL markers are ignored on purpose — the ladder is the landing gate for the rung that owns the witness. |
| `scripts/test_gate_pl_port_trace.sh` | SCRIP | graded population is now `FAMILIES="${FAMILIES:-probe_plz ladder}"` (was `probe_plz` only); `--cut` stays the ONE way `ALL.trace` changes. |
| 12 witnesses | corpus `tests/prolog/ALL.{pl,ref,csv,trace}` | rung 0 `hello` (text exactly `:- initialization(main). main :- write(hello_world), nl.`), rung 1 `fact_rule`, rung 2 `choice_redo`, rung 3 `disjunction`, rung 4 `cut_commit` / `cut_prunes_later_clause` / `cut_under_backtrack`, rung 5 `ite_both_branches` / `ite_condition_committed` / `ite_condition_throws` / `negation` / `once_forall_ignore`. Refs from `/usr/bin/swipl -q -g halt`. `config/MODES.tsv` declares `ladder m3,m4` with the runner named as evidence. |

Absorption path: `corpus_suite_harness.py capture-oracle-refs --lang prolog` (writes the nine green refs and **refuses to write a ref for a red witness** — the three reds got the identical swipl invocation by hand) → `convert-blocks prolog --modes m3,m4 --xfail <the three>` (the harness refuses a non-green original unless it is named; on-disk re-validation 12/12 byte-equal both modes) → `util_build_master_suite.py --lang prolog --absorb-only ladder --delete-absorbed --only ladder` → `util_master_content_diff.py` vs HEAD: **12 gained, 0 lost, 0 differing** (371 → 383 entries; the 700-line byte diff is the builder's seq renumbering, exactly as its docstring warns).

## Measured — the instrument's capacity to fail, before its passes mean anything (INSTRUMENT LAWS, fifth batch)

| arm | command | reading on `f4532dea` / corpus `1d4ff901` |
|---|---|---|
| passed once | `test_prolog_ladder.sh --to 2` | PASS 6/6 (3 witnesses × 2 modes), rc=0 |
| failed once | `test_prolog_ladder.sh --to 5` | RED PASS=18 FAIL=6 of 24: `rung03_disjunction` prints wrong output (m3 and m4, rc=0); `rung04_cut_prunes_later_clause` and `rung04_cut_under_backtrack` exit rc=139 in both modes |
| refused once | `S4E_HOME=/nonexistent … --to 0` · `--to x` | rc=2 both, with the reason named |
| trace gate before `--cut` | `test_gate_pl_port_trace.sh` | 12 NOREF, rc=1 (its own failing arm on the new family) |
| trace gate after `--cut` | same | 21 witnesses ok in both modes, rc=0, examined 42; the nine `probe_plz` blocks byte-identical to before (`git diff` on `ALL.trace`: +2112 lines, 0 removed) |

The three red witnesses carry an explicit, named `XFAIL` marker in the master because they ARE red on the pre-cut tree; the runner grades them strictly and says so in its header. Promoting a marker is three places (`lib_master_extract.sh` § INTERIM PROMOTION PROTOCOL) and belongs to the rung that lands the witness. Expected post-cut: every ladder witness red until its rung lands — that is the runner's honest "failed once" arm for hq_C's rung 0, as hq_C themselves predicted by mail.

## ⭐ Two things the brief did not know

1. **The capture tool will not write a red witness's ref.** `capture-oracle-refs` leaves a witness SCRIP fails without a `.ref` on purpose (a human decides), so a ladder whose whole point is to hold witnesses ahead of their rung needs the same swipl invocation run by hand for those — the ref is the oracle's output regardless of SCRIP's verdict. Recorded so the next rung's owner does not read the missing `.ref` as "the oracle refused".
2. **The trace gate's `--cut` rewrites the whole file from the live traces of its population.** Adding a family to `ALL.trace` therefore means adding it to the gate's population, never appending blocks by hand (the header's rule). The `FAMILIES` env exists for a seat that wants to cut one family without re-running the other; the default cuts both.

## The rung 2.0 row — superseded, and the r9 patch parked as its own row

Claimed at session start, measured (339 `r12` lines, 168 `rtccb+48` reloads on `nreverse`, all 168 the `rtcc_rl` veneer), then HELD by ceo mid-session (Lon's rung-0 ruling deletes the 16 sink sites) and unclaimed. Nothing of it was landed. Two brief corrections are kept at ARCH § E.2 (the corpus is a sibling root; `rcx` is live in the PL-DC γ/ω shims so the temp there is `r8`). The language-blind part survived as a patch developed in a scratch worktree and is now **row `rtcc-veneer-drops-the-r9-gva-reload-when-the-gva-table-is-empty`** (rank 1, parked `BLOCKED-ON:prolog-rung-0-the-cut-and-hello-world-with-zero-globals`, owner after the cut hq_P; patch at `/home/resources/postoffice/tasks/<topic>.patch`, outside every root). Its measurement on `f4532dea` is in the baton; the one design finding worth repeating: **the reload must be keyed per COMPILE on the GVA table (`gva_count()==0`), not per graph** — `rt_gen_spine_resume_enter` / `rt_gen_spine_pass_γ/ω` are mask-0 LEAF calls in `x86_rtcc_clob_raw`, so a GVA-referencing graph resumed from a non-GVA generator graph would read an `r9` the generator's own C calls clobbered and nobody reloaded. Control arms measured: SNOBOL4 board 1679/1679 both modes, Icon all-rungs `PASS=263 FAIL=6 BADEXIT=1` with an identical failure set on both trees, SNOBOL4 and Icon programs with globals keep every reload. Every number is void the moment origin moves past `f4532dea` (REBASE-BASELINE COROLLARY).

**Receipts:** SCRIP `6faa3215`, corpus `1d4ff901`; postoffice mails `ladder-runner-landed` (to hq_C) and the ceo telegram of the same name; row `rtcc-veneer-drops-the-r9-gva-reload-when-the-gva-table-is-empty` and its baton.
