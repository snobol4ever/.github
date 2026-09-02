# FINDING 2026-09-02 seat16 — the row's own acceptance gate fed `bubble`/`quick` `< /dev/null` and reported a false 0/5; with the bug fixed, `bubble` is 5/5 clean (Site 1 is cured) and `quick`'s residual FAIL is confirmed cross-row, not this row's charter

**Row:** `zd-omega-head-per-op-filter-one-cause-behind-boolptr-boolidx-and-the-spine-leaks` (resumed unfinished claim, seat16).
**Tree:** SCRIP `9c2c962f2` (pristine `make`, `RT_OPT=-O0`), pulled clean before building.

## 1. Why this row was re-served at all

This row parked `BLOCKED-ON:calling-convention-depth-tracked` on 2026-08-30 (seat12). That blocker went `DONE`
(hq_P, SCRIP `f9a90958`, landed 2026-09-02 — `[ZD-FINAL]` widened from the single `zvd_ok` test node to every
armed node's cross-run exit edges plus in-run forward ω-to-α skips; see that row's own `## NEXT`, "BOTH SHAPES
CURED AND LANDED"). The park self-cleared, `next` resumed this row as an unfinished claim.

## 2. `make pristine` + this row's own gate, run fresh, said the fix had NOT landed — it had

First clean run at `9c2c962f2`:

```
✅ PASS structural-zd-omega-head
✅ PASS pascal-boolptr-m3 / m4          ✅ PASS pascal-boolidx-m3 / m4
✅ PASS a_plainvar-m3 / m4              ✅ PASS f_const_then_relop-m3 / m4
⛔ FAIL pascal-bubble-m4-5x -- 0/5 clean under setarch -R
⛔ FAIL pascal-quick-m4-5x  -- 0/5 clean under setarch -R
```

`bubble` failing 0/5 directly contradicts hq_P's own measured report on the landing commit ("sieve and bubble
cured in BOTH media, output byte-identical to ref"). Before trusting either prose over the gate (this row's own
standing rule), re-derived it by hand rather than assuming a regression between hq_P's measurement and mine.

## 3. Root cause: the gate's own run step used `< /dev/null` against a program that reads stdin

`bubble.pas` and `quick.pas` both open `readln(reps)` — confirmed by grep, and independently documented in
`test_bench_pascal_timed.sh`'s own header ("every kernel here opens with `readln(reps); for rep := 1 to reps
do <body>`"). Section 3 of `test_gate_zd_omega_head_acceptance.sh` (written by seat03, 2026-08-29, predating
the trap's documentation) ran the compiled benchmark with:

```bash
out=$(setarch "$(uname -m)" -R timeout 30s "$exe" < /dev/null 2>/dev/null); rc=$?
```

This is the exact trap CLAUDE.md/RULES.md name by number: *"`< /dev/null` ... NEVER on a run fed by a pipe or
file: the redirect overrides the pipe, the program reads EOF and prints a plausible answer"* — and
`FINDING-2026-09-01-seat05-site1-row-carries-a-retracted-reservation-in-its-goal-and-no-blocked-on-in-the-queue.md`
already hit and retracted the identical mistake on `sieve.pas` one day earlier (§ "the claim that sieve m3
prints 0 ... was MY MEASUREMENT ERROR"). This gate had the same bug, unnoticed, for four days across ~15
sessions, because every session before Site 1 landed correctly read "0/5" as the expected, already-known
outcome and had no reason to question the harness.

**Manually reproducing the gate's own compile→link sequence, byte-for-byte, with only the stdin swapped:**

| stdin | bubble m4 (5 reps, `setarch -R`) | quick m4 (5 reps, `setarch -R`) |
|---|---|---|
| `< /dev/null` | 0/5 (rc=0, wrong output every time) | 0/5 (rc=0, wrong output every time) |
| `echo 1 \|` | **5/5 PASS, byte-matches `bubble.ref`** | 0/5 — rc=0, prints `-50000 / 10414` every time, `.ref` says `15505` |

`echo 1` is the input `bubble.ref`/`quick.ref` were generated against, and matches every other script in this
tree that runs these two kernels: `calling-convention-depth-tracked`'s own DONE-WHEN, `pascal-quick-m4-wrong-
checksum-crash-masked`'s own DONE-WHEN, and `test_bench_pascal_timed.sh`.

**Fixed** (SCRIP, this session): section 3 now pipes `echo 1` instead of redirecting `< /dev/null`, with a
comment naming the trap so it doesn't recur.

## 4. With the bug fixed: `bubble` is genuinely, fully cured — this row's actual charter is met

`pascal-bubble-m4-5x`: **5/5 clean, byte-identical to `.ref`.** This is Site 1 (the spine leak this row's own
GOAL named as items 3+4) closing for real, on top of Site 2 (the `IR_BINOP_TEST` per-op-filter admission,
landed weeks earlier and unaffected by any of this). Combined with structural + boolptr(m3/m4) +
boolidx(m3/m4) + both regression detectors, **every witness this row was actually minted to fix now passes.**

## 5. `quick`'s residual FAIL is NOT this row's charter — confirmed, not assumed

`quick` m4 with correct stdin is deterministic 5/5 **wrong-output** (`10414` vs ref `15505`), never a crash.
This is not Site 1 surviving a partial cure — it is the exact signature already root-caused by seat09
(`FINDING-2026-08-30-seat09-pascal-quick-m4-wrong-output-root-caused-to-stray-comparison-operand-read-as-fail-
tag-at-a-procedure-exit.md`): a comparison node's ω-port wired directly onto `qsort`'s own success exit leaks
a raw, untagged operand into `rax`; when its low byte happens to equal `DT_FAIL` (0x68), the caller's own
post-call convention misreads a normal return as a failure and propagates a spurious ω up the live call chain.
That is a port-wiring/value-contract hazard in `x86_omega`/`x86_alpha`/`x86_gamma`/`x86_beta` — shared
cross-language infrastructure, unrelated to `zd_plan`/two-depth-joins (`SCRIP_ZD=0` was already shown to
reproduce the identical wrong output, ruling `zd_plan` out as a contributing factor). It has its own row,
`pascal-quick-m4-wrong-checksum-crash-masked`, fully root-caused, its DONE-WHEN already targeting `15505`,
explicitly marked **not attempting a fix pending an hq_C/hq_P scoping ruling** (three named candidate
directions) — sitting FREE, unclaimed, since 2026-08-30.

`FINDING-2026-09-01-seat05-...` independently reached the identical split one day earlier on the *sibling*
row (`pascal-m4-site1-forloop-backedge-64byte-excess`): *"`quick` no longer manifests Site 1 at all ... what
remains there is the separate wrong-answer defect."* Two independent measurements, two different rows, same
conclusion: **this row's original GOAL text bundling "the bubble/quick m4 spine leaks" as one cause was
correct for bubble and a mis-attribution for quick**, corrected by investigation over the following two days.

## 6. A second, unrelated red: the `prolog-crosscheck` floor moved

`PL-CROSSCHECK` fail-set: `rung15_abolish_abolish_one_of_two` LEFT the pinned set, `rung22_write_canonical_
write_canonical_list` ENTERED it. Neither is `zd_plan`/depth-tracking territory. `git log` on `src/parsers/
prolog` since the floor was last pinned (hq_P, `.github` re-pin 2026-09-01) shows a dense, unrelated wave —
seat14's `abolish`-existence-error landing today (`FINDING-2026-09-02-seat14-prolog-abolish-existence-error-
landed-ite-swallows-exceptions-found.md`, which explains the abolish stem leaving the set and separately
documents a *new*, different blocker — `->` swallowing exceptions — for the 3 abolish stems still red) plus
the ongoing "Term eradication" (T9) milestone series (struct-tree deletions, cell-native conversions) that
touches `write_canonical`'s neighborhood. This gate's own design intent (comment above the check) is exactly
"grades omega-head regressions, not Prolog's pre-existing correctness debt" — this movement reads as exactly
that debt shifting under unrelated, concurrent work, not as fallout from `f9a90958` or anything in this row.
**Not re-pinned here** — re-pinning is a deliberate act this row's own gate reserves to the floor's owner
(hq_P did the last one under an explicit ruling); flagged to hq_P rather than done unilaterally.

## 7. What this session changed

- `SCRIP/scripts/test_gate_zd_omega_head_acceptance.sh`: fixed the `< /dev/null` → `echo 1` stdin bug in
  section 3, with a comment naming the trap.
- **Did not** touch `emit.cpp`/`zd_plan`/`x86_asm.h` — nothing there needed changing; the fix already landed
  elsewhere (`f9a90958`).
- **Did not** re-pin the `prolog-crosscheck` floor or touch `pascal-quick-m4-wrong-checksum-crash-masked` —
  both flagged to hq_P rather than resolved unilaterally, consistent with this row's own standing practice.

## 8. Net effect on this row

Every witness this row actually owns now passes. The row's literal DONE-WHEN (the gate script exiting 0)
still cannot pass, because it also gates on `quick` (a different row's charter) and `prolog-crosscheck`
(unrelated churn). Parked `BLOCKED-ON:pascal-quick-m4-wrong-checksum-crash-masked` rather than closed —
same reasoning this row already used once for `calling-convention-depth-tracked`, and the same open question
seat05 already raised on the sibling row (drop the cross-row clause vs. keep it as a deliberate gate) is
raised here too, for hq_P to rule on either way.
