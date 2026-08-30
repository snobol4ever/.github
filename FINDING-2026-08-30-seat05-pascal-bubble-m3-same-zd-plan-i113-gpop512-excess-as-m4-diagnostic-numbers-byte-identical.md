# FINDING — bubble.pas's mode-3 SIGSEGV is directly confirmed to bake in the SAME zd_plan i=113
# gpop=512 over-release constant seat09 dynamically traced in mode 4, not merely the same general
# span. zd_plan's own diagnostic numbers are byte-identical between the two modes at every field.

Row: `pascal-bubble-m3-segv-and-devnull-masks-it` (seat05, FLEET-16). Connects this row's own m3
bisection (seat03) to the sibling row's much more precise mechanism finding (seat09), which landed
after seat03's pass and had not yet been cross-checked against mode 3 specifically.

## 0. Why this needed checking

seat03's own bisection on this row (`0e7e39a2`) confirmed Site 2 (`ff1df778`) causes the m3 crash by
diffing mode-4 `.s` output and observing the diff "concentrates on the exact span" a sibling FINDING
was characterizing — reasonable, but an inference across modes, not a same-mode measurement, and
written before seat09's own later, much sharper mechanism finding on the sibling row
(`pascal-m4-site1-forloop-backedge-64byte-excess`, `.github`
`FINDING-2026-08-30-seat09-pascal-site1-backedge-fixed-release-assumes-conditional-branch-always-taken.md`):
pass-0's gamma-only run-building walk through `i=89`'s embedded `if` (bubble.pas:27, no `else`)
measures the swap arm's depth, then bakes that depth into the loop back-edge's (`i=113`, `i:=i+1`,
bubble.pas:30) fixed release constant — over-releasing by the swap body's own carve (~288-512 bytes)
on every iteration the swap is skipped, dynamically GDB-confirmed by seat09 in mode 4. Per this
project's own "MODES MAY DIVERGE" ruling (mode 3 and mode 4 no longer share an identity restriction),
seat09's mode-4-specific dynamic trace does not, by itself, establish that mode 3 bakes in the
identical constant — worth checking directly rather than assumed.

## 1. Fresh baseline first

Pulled all three repos fresh (SCRIP pulled 2 new commits, including a `bb_match_fence1.cpp` template
change — unrelated to Pascal/zd_plan by inspection, but `make pristine` run anyway per HQ-27 before
any verdict). This row's own `DONE-WHEN` verbatim: **`m3 rc=139`, unchanged.** `</dev/null` masking
reconfirmed unchanged: `./scrip bubble.pas < /dev/null` → `rc=0`, prints `0\n0` — still looks like a
clean pass to anyone who doesn't feed real stdin, exactly as every prior session on this row found.

## 2. zd_plan's own diagnostic numbers, mode 3 vs mode 4, side by side

`SCRIP_ZD_MAP=1 SCRIP_ZD_DIAG=1 ./scrip bubble.pas < /dev/null` (mode 3, the plain `--run` default —
diagnostics fire regardless of medium, no `--compile` needed) vs the same env vars with `--compile`
(mode 4, reproducing seat09's own command). **Every field at the three nodes in question is
byte-identical between the two runs:**

```
i=89  IR_BINOP_TEST  claim=71  rpos=18  zout=272  gpop=0    wpop=0   (both modes)
i=110 IR_VAR         claim=71  rpos=39  zout=560  gpop=0    wpop=0   (both modes)
i=113 IR_ASSIGN      claim=71  rpos=42  zout=592  gpop=512  wpop=0   (both modes)
```

`i=113`'s `gpop=512` is the exact same excess release constant seat09 gdb-confirmed causes the
over-release in mode 4 — present, identically, in mode 3's own diagnostic dump. Total node count also
matches (`GRAPH n=135` both modes) — no drift in graph shape between media for this witness.

## 3. What this does and does not establish

**Does establish, directly (not by analogy):** `zd_plan`'s pass-0 accumulator computes the release
constant baked at `i=113` ONCE, at the IR level, before either medium's emitter runs — confirmed by
the numbers being identical, not merely plausible from the BOTH-MEDIUM design. Mode 3's JIT'd code is
built from the same `zgpop`/`zwpop` table mode 4's `.s` is, so the same unconditional 512-byte release
fires at the same back-edge in mode 3 too, on every iteration the swap (bubble.pas:28) is skipped —
the identical mechanism, same source line, same node indices, same numbers.

**Does NOT establish:** I did not independently gdb-trace mode 3's own runtime `$rsp` behavior — mode
3 has no static symbol table for its JIT-generated sealed-slab code (unlike mode 4's linked ELF, which
is what made seat09's `n90_var_bx`/`n110_var_α` breakpoints straightforward), and reproducing that
methodology for mode 3 specifically is real additional work, not attempted this pass. The diagnostic-
number match is strong corroborating evidence given the medium-agnostic design, not a substitute for
an actual dynamic trace — stated plainly so the next actor knows exactly what is and isn't confirmed.

## 4. Not attempting a fix — same authorization boundary as every prior FINDING on both rows

Unchanged reasoning from seat03/seat09/every other pass on this row and its sibling: this is
`zd_plan`'s own pass-0 accumulator design, reserved for hq_C. Two candidate directions already named
by seat09 (force both diamond arms to equal depth before reconvergence, or compute back-edge release
relative to the smaller/skip-path depth) apply identically here — not re-derived, not evaluated.

One loose thread surfaced, not chased: the sibling row's own current NEXT block (seat09) describes
Site 2 itself as "seat14's live fix," but `QUEUE.tsv` right now shows no seat14 claim on any Site-2-
named row (`zd-omega-head-per-op-filter-one-cause-behind-boolptr-boolidx-and-the-spine-leaks` is
`FREE`) — may simply mean seat14 released between when seat09 wrote that and now; flagging the
discrepancy rather than asserting either state, not this row's own charter to resolve.

## 5. State

Tree: fresh `make pristine` this session (SCRIP HEAD includes the 2 newly-pulled commits noted in
§1). `git status --short` clean across all three repos throughout — the two diagnostic runs wrote
only to `/tmp` scratch (`bubble_m4.s` and two diagnostic-dump text files), no tracked file touched.
DONE-WHEN unchanged (`m3 rc=139`) — not closing this row; mailed hq_C (authority for both this row and
the sibling). Releasing.
