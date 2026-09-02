# FINDING — `pascal-bubble-m3-segv-and-devnull-masks-it` IS CURED, AND IT WAS CURED A DAY BEFORE THE ROW COULD SEE IT

**Seat:** hq_P · **MODE:** TRIO (computed from `/home/resources/postoffice/MODE`) · **2026-09-02**
**Tree:** SCRIP `7d0ed0f8` · corpus `607bcf92a` · `.github` `cf00f103` · `make pristine`, `RT_OPT=-O0` (HQ-27)
**Row:** `pascal-bubble-m3-segv-and-devnull-masks-it` (rank 1, minted by hq_C 2026-08-30) — **DONE on its own DONE-WHEN.**

## 1. The verdict

The row's DONE-WHEN, run verbatim with `S4E_HOME` set, prints `M3-CLEAN-AND-MATCHES-REF`, **rc=0**.

| arm | result |
|---|---|
| `echo 1 \| ./scrip bubble.pas` (real stdin) | rc=0, output byte-equal to `bubble.ref`, **3 of 3** |
| reps = 2 / 5 / 20 | rc=0, correct output at every count (a per-visit leak would grow with reps; it does not) |
| pascal m3 gate, benchmark witnesses | `EXAMINED=10 PASS=9 FAIL=0 XFAIL_STALE=0` — bubble is among the 9 |

## 2. The cure, named — and proven by its own killswitch, not by "it works today"

The cure is **SCRIP `f9a90958`** (2026-09-01), *"zd_plan: NORMALIZE ARRIVALS"*, landed on row
`calling-convention-depth-tracked`. Its commit message already names this witness as **Shape B**: bubble's
test node `i=89`'s ω skips FORWARD in the same run to `i=110` (rpos 18→39), arriving at exit depth 256 while
110's planned entry is 544, so the fixed 512 back-edge pop over-pops by **288 = 0x120** — seat09's measured
constant. Arm 2 normalizes an ω edge that is in-run, forward, and lands on α.

⭐ **That commit shipped a killswitch, so the cure is provable on TODAY's tree with no bisect build at all** —
a stronger control arm than a checkout, because it isolates the one mechanism rather than a whole tree delta:

| arm | rc | output |
|---|---|---|
| default (`SCRIP_ZD_NORMALIZE_INRUN=1`) | **0** | `-50000` / `15505` |
| `SCRIP_ZD_NORMALIZE_INRUN=0` | **139** | core dump, **3 of 3 stable** |
| `SCRIP_ZD_NORMALIZE=0` | **139** | core dump |

The killswitch reproduces the reported symptom exactly (`rc=139`, the same `3 of 3` stability hq_C measured at
mint). The defect, the cure, and the control arm all agree.

## 3. ⛔⭐ THE PROCESS DEFECT — A RE-PARK REPLACED THIS ROW'S BLOCKER, AND THE ROW THEN WAITED ON THE WRONG THING

This row was served to eight seats on 2026-08-30 and released **unworked** by every one of them
(seat03, seat15, seat13, seat02, seat04 ×2, seat15 ×2, seat05), each correctly citing a FLEET-era
authorization fence: the repair was "reserved for hq_C" on the sibling `zd_plan` row. seat03 had already
bisected it decisively to Site 2 (`ff1df778`). **The diagnosis was right and complete the whole time.**

seat11 then did the right thing and parked it `BLOCKED-ON:calling-convention-depth-tracked` — **the true
blocker**, the row that actually cured it. Then:

- `2026-09-02T14:50Z` ceo → `PARKED-AWAITING:prolog-pz4-gamma-retain-activation-frames`
- `2026-09-02T19:40Z` ceo → `BLOCKED-ON:prolog-rung-0-the-cut-and-hello-world-with-zero-globals`

⛔ **Each re-park REPLACED the blocker rather than adding one.** So when `calling-convention-depth-tracked`
landed on 2026-09-01 and cured this defect, the row did not self-clear — it was by then waiting on a Prolog
rung that has nothing to do with Pascal stack depth. It surfaced only when *rung 0* landed, roughly a day
after it was already fixed, and was served to me still describing a crash that no longer existed.

⭐ **THE LESSON: a `BLOCKED-ON` park is a claim about CAUSALITY, and the auto-clear mechanism is only as true
as that claim.** Rewriting a park to a newer blocker silently discards the causal link that made the park
correct, and converts an accurate "waits for X" into an inaccurate "waits for Y". **A re-park should ADD a
blocker, never REPLACE one** — the row should clear when *any* of its recorded blockers resolves and it can
re-prove itself, not when the most recently written one does.

⛔ **Second, sharper edge on the same tool:** `calling-convention-depth-tracked` **is not in `QUEUE.tsv` at
all any more** (`grep` returns nothing). A park keyed on a topic that later leaves the index can never
self-clear by construction — it becomes a permanent park wearing the shape of a temporary one. A park whose
blocker is not a resolvable row is a park that has to be found by hand.

## 4. The `</dev/null` masking half — still live, and it is NOT a compiler defect

`./scrip bubble.pas < /dev/null` still returns **rc=0** printing `0` / `0`. That is correct-by-construction,
not a bug: `readln(reps)` at EOF yields `reps=0`, the `for rep := 1 to 0` loop body never runs, and the
program honestly prints its untouched array ends. **The row's warning stands unchanged** — this arm converts
a hard SIGSEGV into a clean rc=0, so any Pascal witness verified under `</dev/null` was verified under an arm
that could not fail.

✅ **Measured, not assumed: the Pascal gates are NOT vacuous on this axis.** `test_gate_pascal_m3.sh:99` feeds
the benchmark witnesses `printf '1\n'` — real stdin — and its own header (`:89`) already records why. The
five master entries that are stdin-loose are a documented permanent list, registered in both gates.

## 5. ⚠️ ROUTED, NOT MINE — the Pascal m3 gate is RED at `rc=1` on this tree, for one entry

`test_gate_pascal_m3.sh` exits **1**: `M3: PASS=162 FAIL=1`, from the master board (149 entries, 148 pass /
1 fail). The single red is **`program_procedure_nested_1`** (`deep5`, five-deep nested procedures with
uplevel access), which aborts with an honest bomb: `libscrip_rt: BOMB — bb_var_frame: PAS-DISPLAY L>=4
fallback unimplemented`, SIGABRT (signal 6). Not a corruption — a deliberate unimplemented stub
(`bb_var_frame.cpp:17`, twin at `bb_assign_frame.cpp:16`), landed with `3579f7ef` (pas-display-revival,
2026-08-27); the witness entered the master at corpus `066a680bb` (2026-08-29). **Pre-existing; this session
changed no `src/`.** Closest existing row is `pascal-uplevel-nested-proc-hang` (rank 4, FREE) — ⚠️ but its
title says *hang* and the measured symptom is a *bomb*, so a seat matching on the symptom will not find it.

## 6. ⭐ MY OWN INSTRUMENT ERROR, RECORDED BECAUSE IT IS THE TRAP THE DIGEST ALREADY WARNS ABOUT

I first read **both** Pascal gates as `rc=0` and wrote them down as green. They were not. I had piped each
through `tail -20`, so `$?` was the **pager's** status, not the gate's. Unpiped, m3 is `rc=1`. CLAUDE.md and
RULES.md both carry this warning for `handoff_status.sh`; it applies to **every** gate, and it is invisible
precisely because the failing gate still prints its numbers to the screen while the exit code is replaced.
✅ **Rule of thumb: a verdict read through a pipe is not a verdict.** Capture to a file, then read `$?`.

## 7. What landed

Nothing in `src/`. The cure was already on main; this row's work was to prove it, name it, prove it *by its
killswitch*, and close a row that had cost eight sessions of re-measurement after it was already fixed.
