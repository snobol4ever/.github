# FINDING 2026-09-02 hq_B — post-cut the Prolog rung suite is 0/15 both modes, every red self-classifies to a ladder rung, and three greens were vacuous refusals

Row `prolog-rung-suite-reds-rowed-by-class` (MASTER-PLAN ladder C3). MODE `TRIO`. Trees: SCRIP `7432838a` (measured on `c182977e`, re-proven after the rebase), corpus `542de174`. Build: `make pristine`, `RT_OPT=-O0`.

## Measured

| arm | before (I4 tree, `f01b7c254`) | post-cut, suite as it was | post-cut, suite fixed |
|---|---|---|---|
| interp (m3) | PASS=3 FAIL=12 | PASS=3 FAIL=12 TOTAL=15 | PASS=0 FAIL=15 |
| compile (m4) | PASS=0 FAIL=15 | PASS=0 FAIL=15 TOTAL=15 | PASS=0 FAIL=15 |

Every post-cut red is `lower_prolog.c` `pl_refuse()`: rc=2 with empty stdout in m3, rc=1 through `run_prolog_via_x86_backend.sh` in m4. First-refusal histogram (witness × mode): rung 1 ×2, rung 2 ×18, rung 3 ×4, rung 6 ×2, rung 8 ×4. The whole run takes under a second.

**The three greens were vacuous.** `rung15_abolish_abolish_{existing,one_of_two,then_query_fail}` carry no `:- initialization(main)`, so swipl prints nothing and their `.expected` is empty (PENDING.md § abolish). The suite graded stdout only, so a refusal that printed nothing matched. Cure in `test_prolog_rung_suite.sh`: a PASS needs stdout == expected AND rc == 0; stderr is kept and a refusal prints `REFUSED-LADDER rung N -- <construct> (rc=…)`. Failed once (live corpus 3 → 0 greens, 15 named reds each mode) and passed once (a scratch `--corpus` holding hello world: PASS=1 both modes). Blast radius: this one script; no other script parses its output (Makefile does not name it).

## Classification — by the HIGHEST construct, not the first refusal

The driver names the FIRST missing construct, a lower bound. Read against ARCH § E and the driver's rung tables, the 15 witnesses fall into four classes, each now a `prolog-rung-red-class-*` row PARKED-UMBRELLA beside the ceo's 28 old-machine rows, each with a DONE-WHEN that runs both modes and demands a `PASS` line per witness (watched to FAIL rc=1; REFUSES rc=2 on a missing witness or summary):

| ladder rung (owner) | witnesses | row |
|---|---|---|
| 6 det builtins (hq_P) | `rung22_write_canonical_write_canonical_list` | `…-write-canonical-is-ladder-rung-6` |
| 8 findall/bagof (hq_P) | `rung11_findall_findall_arith` `rung11_findall_findall_filter` `rung44_setof_group` `rung50_between_enum` `rung50_for_alias` | `…-findall-bagof-between-is-ladder-rung-8` |
| 9 catch/existence (hq_C) | `rung66_current_stream` (already named by ARCH § E rung 9) | `…-rung66-streams-and-existence-error-is-ladder-rung-9` |
| 10 dynamic DB (hq_C) | `rung14_retract_*` (2) `rung15_abolish_*` (4) `rung45_reflect_clause_*` (2) | `…-dynamic-db-assert-retract-abolish-clause-is-ladder-rung-10` |

So the ladder C gate "rung suite 15/15 both modes with red names printed" is reached at rung 10 by construction and is a REPORTED number until then (RULES § THE PROLOG REBUILD GATE cl. 4). Reported alongside: `test_prolog_ladder.sh` rung 0 PASS 2/2, rungs 1–5 FAIL 22/22 (rung 1 in flight at hq_C); `nm -D` names 0 Prolog-only globals.

## Corpus hygiene landed, and debt seen

- 11 orphan `.expected` files (rung05_backtrack_backtrack, rung27_aggregate_×4, rung28_exceptions_×5, rung30_dcg_generate) deleted: their `.pl` moved into the master at `c7f86c08` and every one has an origin in `ALL.csv`. The suite's denominator (needs a `.pl`) is unchanged at 15.
- `rung22_write_canonical_write_canonical_list.expected` re-pinned from `'.'(a,'.'(b,[]))` (SCRIP's own pre-cut output) to the swipl oracle `[a,b]` (`/usr/bin/swipl -q -g halt`, rc=0).
- Not touched under wrap-up: `test_gate_pl_coupling.sh:48` and `test_prolog_rung30.sh:44` still name `.pl` files that moved into the master — they were already pointing at nothing before this session.

## The lesson

An instrument that grades one channel cannot tell "printed nothing, correctly" from "refused before printing". The exit code is the second channel, and the driver's refusal text is a third that classifies for free. And a `git pull --rebase` renames every hash you already wrote down: the class rows cite the rebased ones.
