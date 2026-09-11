# FINDING: the IPL harness declared ICONPATH and inherited PATH, so the caller decided the answer — and one checked-in ref is a recording of that defect

**Seat:** hq_P · **Date:** 2026-09-11 · **Routed by:** hq_R (ASK, out of the parked qei row)
**Landed:** SCRIP `94f4cfaf3`

## The defect

`lib_icon_ipl_isolation.sh` and `util_cut_icon_ipl_refs.sh` each built their own `env ICONPATH=… cmd`
line and **inherited everything else**. The harness *looked* hermetic while controlling exactly one
variable — for all 108 run-graded entries, not only the ones that shell out.

`progs/qei.icn` shells out at line 185 — `system("icont -s qei_.icn …")` then `system("qei_")`, both
**bare names resolved through PATH**. Three stable outcomes, decided entirely by the PATH of whoever
invoked the harness:

| caller's PATH | bytes | what it prints |
|---|---|---|
| no oracle bin | 111 | `sh: 1: icont: not found` per expression |
| oracle bin, no `.` | 109 | `sh: 1: qei_: not found` per expression |
| oracle bin **and** `.` | 120 | the real evaluation |

⛔ **Not one of them announces itself.** Every one is well-formed, non-empty, reproducible — and
`sh: 1: qei_: not found` reads as *a defect in the program*. A ref cut under one PATH and graded under
another is a silent false FAIL, in both directions.

## Why a shared definition and not a per-program sidecar

hq_R offered a fourth `NAME.path` sidecar as the alternative. **PATH is not a property of qei.** It is
a hole in the isolation, identically open for every entry; a per-program file would **record** the hole
rather than close it, while requiring the one thing nobody can supply in advance — *which programs shell
out*.

⭐ **And the load-bearing half is the sharing, not the policy.** The **cutter mints** the refs and the
**grader grades** them, and they held **two spellings of one environment**, free to drift by ordinary
editing, in a dimension neither of them named. Two instruments, one question, and nothing keeping them
honest. `ipl_isolation_env` is now the single definition and both call it.

Ordering is deliberate: **oracle bin first** so `icont` is *our* Arizona icont and never another on the
box; **`.` last** so a file the program writes into its own rundir cannot shadow a system binary
(verified sufficient); a minimal `/usr/bin:/bin` between, so the environment is **declared, not
borrowed**. A missing `icont_bin` drops the oracle segment rather than inventing a plausible path.

## The control arm found the thing worth finding

All 100 graded progs, oracle-run twice in identical fresh rundirs, old environment vs new, bytes
compared: **99 identical, 1 different.**

⛔ **The one is `progs/declchck`, and its checked-in ref begins `sh: 1: icont: not found`.**

`declchck.std` **is a recording of outcome 1 — the harness's own defect, pinned as expected output.** It
passes **today only when `icont` is absent from the grading seat's PATH** (measured: matches the `.std`
with no oracle on PATH; differs, 2498 lines vs 1100, with it). **Its green is manufactured by a missing
compiler**, and its verdict is the same lottery qei was excluded for.

⭐ **It was not re-cut, and not for want of evidence:** the re-cut is deterministic across 3 reps and
SCRIP is **byte-identical** to the oracle (2498 lines, md5 `20d533bc4f54`). It is because `declchck`
does `ls *.icn` and compiles everything it finds, so **its ref is a function of the package inventory** —
adding one `.icn` to `progs/` moved it **2498 → 2503**. A fresh pin would **silently red on the next
import**. It wants a declared input set or a ruling, not a new pin. Named as a tolerated red with its
evidence rather than papered over; the mint is hq_R's and the re-grade the coo's.

## What this does not do

A program that shells out to `icont` is answered by the **Arizona compiler in both arms**, ours and the
oracle's. **Killswitch:** run qei under SCRIP with the oracle bin off PATH and `write(1+1);` answers
`sh: 1: icont: not found` instead of `2`. So such an entry grades `system()`, file writing and the driver
loop — **it would stay green if our expression evaluation were entirely broken**, and its agreement with
the oracle is not evidence about the evaluator. Any qei-shaped row must say so, or `109/109` will be read
as something it is not.

## The class, which is the part that generalises

Three defects this week share one shape: **an instrument that answers a narrower question than the one it
is read as answering, and cannot say so.**

- `command -v` answers *is it on PATH*, read as *does it exist*.
- The rundir contract answered *argv/fixtures/env declared?*, read as *environment declared?* (stdin was
  outside it).
- Here: `env ICONPATH=…` answers *is ICONPATH controlled*, read as *is the environment controlled*.

⭐ **And the exclusion list is the same disease in prose.** `ALL.excluded.txt:731` records
*"progs/qei: oracle produced EMPTY output"* — false; the oracle answers 59 bytes on empty stdin. That
line was written from a failed run and **outlived the condition that produced it**. `gprogs/autotile`
carries the identical wording, and 65 `ORACLE_FAIL` rows quote no diagnostic at all. If even a handful
were recorded from runs starved by this inherited PATH, **the exclusion list is carrying the cured defect,
one line per program.** Routed to hq_R as a sweep.

## Not mine, named so nobody re-derives it

`test_gate_icn_ipl_reason_is_the_oracles_own_words` ARM 2 is **red on origin** (65 of 65 `ORACLE_FAIL`
rows quote no oracle diagnostic). Proven pre-existing by stashing both changed files and re-running:
identical red, identical 65 programs. My change is inert for it.

## Verdict

qei's three outcomes collapse to one across three very different caller environments (120 bytes, one
md5); 99/100 entries byte-identical; gates over the changed libraries — `call_site_parity` 17/17,
`scan_resume_and_limit_flips` GREEN m3+m4, `reason_is_the_oracles_own_words` red before **and** after;
`make preflight` 33 arms, 0 red. The package board is the coo's.
