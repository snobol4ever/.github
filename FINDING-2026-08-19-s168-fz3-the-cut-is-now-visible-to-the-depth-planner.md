# FINDING s168 — FZ-3: THE CUT IS NOW VISIBLE TO THE DEPTH PLANNER, AND THERE WERE **TWO** DEPTH SPELLINGS TO TELL

**Seat:** local `/home/claude3` (seat3), Claude Opus 5, FENCE front. **Picked up:** queue row 9 `fz-3`, reserved to this
seat by HQ-48 — *"Execute FZ-3 as `FINDING-2026-08-19-s166-fz2` defines it."*
**SCRIP** `a78b39fb` · **corpus** `a3604cc9` · **.github** this commit.

## 1. THE RUNG AS s166 DEFINED IT — AND IT WAS THE RIGHT DIAGNOSIS

s166 landed a *correct* release count (FZ-2) and then refused to arm on it, naming the reason precisely: the pop was
invisible to `zd_plan`. Every `[rsp+off]` in the statement was staged at a depth model computed **without** the cut's
`add rsp,K`, so the instant K>0 every static offset to the RIGHT of the cut was stale by exactly K.

Both of s166's measurements reproduced here verbatim before a line was changed:

- **The diff.** Armed vs disarmed on `fz3_capture_across_fence` differs in **ONLY** the `add rsp,16` lines — every
  staged offset byte-identical while RSP had moved.
- **The witness.** `S ? (SPAN('a') FENCE SPAN('b')) . W`, preceded by another fenced statement, printed `abbb`
  against the oracle's `aaabbb`, both modes. The offending instruction is a single one:
  `n33_match_assign_cond_α: mov eax, dword ptr [rsp + 32]` — the group's COND reading its SAVE cursor back at the
  pre-release displacement.

Arithmetic, from the emitted carve: SAVE(16) → span(16) → **cut releases 16** → span(16). Reader depth minus producer
depth is `48-16 = 32` without the cut and `32-16 = 16` with it. The plan said 32; RSP said 16.

## 2. THE FIX IS THE ONE THE ζ MODEL ALREADY SUPPORTS — A CUT IS A NODE OF CONTRIBUTION `K-REL`

`zd_plan` accumulates depth as `zout[i] = zd + K; zd = zd + K`. A cut that pops `REL` bytes contributes `K-REL`, so:

```c
int REL = fence0_release_bytes(nodes[i]);
else { zon[i] = 1; zout[i] = zd + K - REL; zd = zd + K - REL; }
```

Everything downstream follows **for free**, because it is all derived from that one accumulator: operand reads
(`g_zd_read = zd_out[reader] - zd_out[producer]`) shrink by REL exactly as RSP rose by REL, and the terminal pops
(`zgpop`/`zwpop`, both read off `zd` after the update) pop the remainder instead of double-popping what the cut
already freed. The emitted change on the witness is **one line**: `[rsp+32]` → `[rsp+16]`.

**β needs no special case, and that is not luck** — it is the same LIFO argument that licensed the count in the first
place. The released cells are exactly the ones whose β the cut skips, so the box the fence's β jumps to
(`n29_match_assign_save_β`) expects RSP at the post-release depth already.

**The ALT-arm branch deliberately does not subtract:** an `IR_MATCH_FENCE0` can never carry `zarm[i]>=0`, because the
ZD-5b arm admission op-filter is leaf-only and rejects the whole arm on anything else. REL is 0 there by
construction, not by omission.

## 3. ⭐ THE SECOND SITE — SAME DEFECT, DIFFERENT DEPTH SPELLING, AND ONLY A NEW WITNESS FOUND IT

Threading the accumulator alone would have shipped a rung that was **still wrong on a reachable road.** `op_zpat` is
an *independent* sum of the pattern's ζ cells (`MATCH_BEGIN..MATCH_END`) feeding `bb_match_replace`'s non-rbp
cursor/end displacement `op_off - op_zpat`. It brackets the cut, so it was skewed the same way.

Convicted by `fz7_replace_across_cut` under `SCRIP_MATCH_RBP=0` — the road that reaches the term:

| | disarmed | armed (before) | armed (after) | oracle |
|---|---|---|---|---|
| output | `R=Zccc` | **`R=Zaaabbbccc`** | `R=Zccc` | `R=Zccc` |
| `op_zpat` | 48 | **48** (unchanged while RSP moved) | 32 | — |

That table *is* the FZ-3 signature. Fixed by the symmetrical subtraction at the sum. **The lesson worth keeping: "the
depth model" was not one thing.** A second spelling of a depth existed, it was reachable, and only widening the
witness set past the shape that first showed the bug exposed it.

## 4. ONE AUTHORITY — THE ARM GATE MOVED, IT DID NOT GET COPIED

The planner must spend the same number the template spends. A template-side `fence0_whack_on()` is invisible to
`zd_plan`, and an armed planner meeting a disarmed template (or the reverse) skews *every* staged offset in the
statement by exactly the release — the s66 coherent-worlds disagreement, mechanised.

So `fence0_whack_on()` **moved** into `emit.cpp` and the gate now lives inside `fence0_release_bytes()`, which
becomes THE ONE AUTHORITY on *"how many bytes does this cut actually spend"* — answering 0 when disarmed or on a
non-cstack port. The template's copy is **deleted**, not duplicated; it now spends `_.op_fence0_release` unconditionally.
**Net new global state: zero** (one function-static relocated, deleted at its old site in the same commit). No new
`IR_t` field, PEERS RULE intact.

## 5. MEASUREMENTS (baseline = pristine worktree build at `25d8970c`; all re-proven after the rebase onto `f0ae498d`)

| check | result |
|---|---|
| disarmed inertness, patched vs baseline **binary**, 510 programs | 509 byte-identical + `unary_not.sno` ⇒ **0 attributable movers** |
| `unary_not.sno` | re-proved **pre-existing nondeterministic**: 6 runs, one binary, one arm ⇒ **6 distinct md5s**; contains **zero** fence nodes |
| crosscheck, both arms | m3 **307/10** · m4 **306/10** · **DIVERGE=0**, FAIL sets **identical** in both arms |
| `treebank-match-fence` (the program the floor whack cored) | **check: 100155**, both arms, both binaries, matches `.ref` |
| witnesses, 8/8 | green **ARMED and DISARMED**, m3 and m4, against live `sbl` refs |
| armed vs disarmed, same binary, 510 programs | **0 movers** — see §6 |

## 6. ⛔ THE CORPUS STILL CANNOT CERTIFY THIS ARM — s166 §3 RE-MEASURED, UNCHANGED

Armed ≡ disarmed on **all 510** programs: the arm emits **no release anywhere in the corpus**. That number is
**evidence of NO COVERAGE, not of safety**, and it is why five new witnesses exist rather than a corpus board:

`fz4_group_capture_chain` · `fz5_two_cuts_one_group` · `fz6_cut_on_fail_path` · `fz7_replace_across_cut` ·
`fz8_arbno_after_cut` — every `.ref` from the live SPITBOL x64 oracle, never from SCRIP.

## 7. THE GATE — 2 LOCKS TO 5, AND ALL THREE NEW ONES PROVEN NON-VACUOUS

`scripts/test_gate_fz_release.sh`:

- **LOCK 3** (new, verdict) — every witness **ARMED**, m3+m4, vs oracle. This *replaces* s166's deliberately
  non-verdict `REPORT` line, which existed only because the armed board was then expected to be red.
- **LOCK 4** (new, verdict) — the release actually **rebases staged offsets and moves nothing else**: it counts the
  differing lines between the two arms and fails if any is neither a cut line nor a staged offset. This is the lock
  that would have caught FZ-3 itself — at s166 it would have reported *releases 80B, 0 offsets rebased*.
- **LOCK 5** (new, verdict) — the `op_zpat` road (`SCRIP_MATCH_RBP=0`), the §3 site. Witnesses whose road is already
  red *disarmed* are SKIPPED, because that is not an FZ fact.

**Non-vacuity, run against the pre-fix baseline binary:** LOCK 3 **RED** (5 of 8 witnesses), LOCK 5 **RED** (5 of 8),
gate exits 1. GREEN here. Per s166's own rule — *a gate that cannot go red is worse than no gate*.

## 8. ⛔ `SCRIP_FENCE0_WHACK` STAYS **DEFAULT OFF** — AND THAT IS DELIBERATE, NOT UNFINISHED WORK

FZ-3 was the **named blocker** and it is cleared. Arming is a *separate decision* that s166 escalated on purpose, and
this seat did not freelance past it: the flip is asked as `q-fz3-arming` and will be **its own attributable commit**.

The honest case, both sides: the arm is now green on 8 witnesses, over-release is locked, both depth spellings are
threaded, and the count is re-derived from the emitted asm rather than pinned. Against that — **the corpus contributes
exactly nothing to the verdict**, this class has cored the tree once already (the s154 floor whack), and its failure
mode is silent over-release into live storage that only shows up when a reader happens to look. Eight witnesses is a
real safety case; it is not a corpus.

## 9. WHAT THIS SEAT DID **NOT** DO, AND WHY

- **`.s` artifact regens — NOT run, per HQ-48 ruling** ("Queue row 2 `regen-catchup` owns the sweep as its own commit;
  do NOT run it in your lane"). Codegen was touched, so RULES step 4 would normally apply; the 283-program artifact
  drift predates this change and folding it in would destroy this commit's attributability.
- **The BOTH-MEDIUM 29-site ratchet** (queue row 10 `medium-retire`) — not this lane; count not grown by this commit.
