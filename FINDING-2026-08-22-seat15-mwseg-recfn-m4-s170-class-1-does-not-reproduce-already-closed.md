# FINDING — queue row `mwseg-recfn-m4` (s170 §2a / "class 1"): the SIGSEGV does not reproduce at pristine HEAD. Already closed before s193, independently corroborated twice now.

seat15, 2026-08-22. THE LOOP queue row `mwseg-recfn-m4` (rank 2), picked up via `s4e_msg.sh next`.

## What the brief asked

> FINDING s170 (seat4 BM-2) class 1: an UNCALLED self-recursive DEFINE changes the codegen of the
> REST of the program -- mixed_workload m4 SEGV at loop count 0; 3-ingredient witness set in
> corpus/probe/mwseg/, one-ingredient asm-diff pair named (mwseg_recfn_capture_table vs
> mwseg_flatfn_capture_table). First: ASM-DIFF-FIRST on the named pair. DONE-WHEN: root-cause
> FINDING; mwseg witnesses + mixed_workload green m4 if killswitch-clean, else investigation-only.

"class 1" is §2a of the original discovery FINDING (`FINDING-2026-08-19-s170-bm2-one-copy-and-two-m4-segv-classes-the-ungraded-were-hiding.md`) — the `mixed_workload`/`probe/mwseg/` SIGSEGV, minted at pristine SCRIP `b7e10d3c` and re-confirmed still crashing at the pushed HEAD `e4449403` the same session. It is a **different, unrelated** bug from that FINDING's §2b (`indirect_dispatch` / APPLY-to-SNOBOL-defined-target, owned by a separate row, `apply-snodef-m4`) — not touched here.

## Before starting ASM-DIFF-FIRST: the goal file already says this class is closed

`GOAL-SNOBOL4-100.md`'s cursor history carries a side-note inside a **different** row's entry (seat4, s193, 2026-08-20, working `apply-snodef-m4`, **not** this row):

> ⛔ NOT MINE, SAID OUT LOUD: `mixed_workload` XPASSes with the killswitch OFF too, and all four
> `probe/mwseg/` witnesses are green in both arms — the s170 §2a class was closed by an EARLIER
> rung. Marker retired as stale by measurement, not claimed as a cure.

That is a live contradiction of the still-open QUEUE.tsv row, so per THE LOOP (a scope/premise mismatch is a FINDING, not a blocker) the right first step was to **measure current reality before diffing anything**, not trust either source.

## Evidence — pristine build, current HEAD

```
git log -1: 2e601a2ecffe7a8ae6c5799b2f31f32a4e343beb 2026-08-22 16:14:05 -0500
            "rung E-4 (bb_define.cpp): eradicate r11/omega, license the monitor-save class (6)"
make pristine: clean (HQ-27)
```

| witness | expect (`.ref`) | m3 | m4 |
|---|---|---|---|
| `mwseg_recfn_capture_table.sno` (the SIGSEGV witness) | `tot: 30` | `tot: 30` rc=0 | **`tot: 30` rc=0** |
| `mwseg_flatfn_capture_table.sno` | `tot: 30` | `tot: 30` rc=0 | `tot: 30` rc=0 |
| `mwseg_recfn_capture_novar.sno` | `tot: 30` | `tot: 30` rc=0 | `tot: 30` rc=0 |
| `mwseg_recfn_table_nopat.sno` | `tot: 3` | `tot: 3` rc=0 | `tot: 3` rc=0 |
| `benchmarks/snobol4/mixed_workload.sno` (the original, harness-driven) | `check: 12100` | `check: 12100` rc=0 | `check: 12100` rc=0 |

All five oracle-identical, both modes, at pristine HEAD. m4 built via the canonical sequence (`--compile > p.s`, `gcc -c p.s`, link against `out/libscrip_rt.so`), same as `scripts/test_corpus_snobol4.sh`'s `compile_mode4()`. Re-run twice — once at HEAD `2659558e`, again after a mid-session `git pull --rebase` landed `2e601a2e` (touches `bb_define.cpp` directly) — identical result both times, then a third time from a full `make pristine` for the citable verdict above.

**DONE-WHEN is met on its stated first branch: "mwseg witnesses + mixed_workload green m4."**

## Attribution attempt — investigation-only on this part, by the brief's own sanctioned fallback

Tried to pin the fixing commit by checking out the leading candidate, `c893d236` ("ab-cell-hoist (row 10): the last three MEDIUM_ guards retire — the AB fn-cell store moves to emit.cpp", 2026-08-19 21:26, ~1h after the mwseg mint at 2026-08-19 20:24 and mechanistically on-point: AB fn-cell / `bb_define.cpp` relocation is exactly the kind of change that would affect how an uncalled self-recursive `DEFINE`'s presence perturbs codegen for the rest of the program) and rebuilding there. The build did not finish inside a 5-minute window — this machine is a genuinely shared 16-seat build farm (confirmed via `pgrep`: `/home/claude02`, `/home/claude10`, `/home/claude01` all had live `gcc`/`cc1plus` processes mid-compile at the same moment), so a clean bisection point costs real wall-clock under contention. Judgment call: abandoned the bisect rather than burn more of this row's budget on attribution when the DONE-WHEN explicitly accepts "investigation-only" — checked back out to `main`, `git pull --rebase` (picked up 3 commits including `2e601a2e`), rebuilt, re-confirmed green (table above). **`c893d236` is a plausible, unverified candidate — not a proven one.** Whoever next touches `bb_define.cpp`/AB-cell code and wants a clean data point: `git checkout c893d236 -- ` is the next bisection step, ideally scheduled off-peak.

## Why the QUEUE.tsv row survived past the point the goal file called it closed

Not investigated further here (outside this row's scope) but worth naming: the s193 note closed this **in the goal file**, by measurement, two days before this row was handed out fresh by `next`. The queue and the goal file are two different stores with no automatic sync — closing something in one doesn't retract it from the other. This is the same class of hazard RULES.md already names elsewhere (a board/gate "scanning a tree that no longer exists"); here it's a queue scanning a bug that no longer exists. Flagging for HQ rather than proposing a queue-hygiene mechanism myself — not this row's mandate.

## Recommendation

Retire `mwseg-recfn-m4` from `QUEUE.tsv` (or mark it done) — this FINDING is its second independent green confirmation (s193 seat4 side-observation; this session's pristine build, current HEAD, all five programs, both modes). If HQ wants the attribution nailed down, that is a fresh, cheap, off-peak-scheduled row, not a re-open of this one.

## Scope check

Zero source changes to SCRIP or corpus. One `git checkout`/build/revert round-trip for the abandoned bisection attempt, left the tree exactly as found (`main`, pulled current, pristine-built). Nothing to commit there. This FINDING plus the `GOAL-SNOBOL4-100.md` cursor update are the entire deliverable.
