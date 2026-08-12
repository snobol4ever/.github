# FINDING — LOWER L-3b LANDED (partial): non-carving splice class fixed by SUBTRACTING
# terms from the read formula, not adding one; op_zdepth alone supplies the compensation.
# ARB/BREAK residual and the carving class remain open, narrower now.

**Session:** Claude Sonnet 5, 2026-08-12, LOWER seat.
**SCRIP HEAD:** `cfd5341c` (local, unpushed). **corpus HEAD:** `ed55662b` (local, unpushed).
**Prior state this session:** FINDING-2026-08-12j (same session) documents a disproved
intermediate attempt (`op_off + op_zfc`, additive) that this landing supersedes.

## What changed

`src/templates/bb_match_replace.cpp`'s read formula:
```cpp
int _dispc = _.op_zfc ? _.op_off : (_.op_off - _.op_zpat);
int _dispe = _.op_zfc ? (_.op_off + 24) : (_.op_off + 24 - _.op_zpat);
std::string _cur = FR(_dispc); std::string _end = FRQ(_dispe);
```
When `op_zfc != 0` (the non-carving class is armed — SPAN/ARB/BREAK/REM-family primitives that
carve their own un-popped backtrack cell before MATCH_END runs), the read passes `op_off` alone
— **no `op_fc_disp`, no `op_zpat`, no `op_zfc` term at all** — to `FR()`/`FRQ()`. When
`op_zfc==0` (carving class TAB/RTAB/POS/RPOS, or no replacement-adjacent carve), the legacy
`-op_zpat` expression is untouched, so that class and every existing control is byte-identical
by construction.

This is NOT the "ADDITIVE... op_off+op_fc_disp+32" formula the s37 STEP-6 comment described
(disproved this session, see FINDING-2026-08-12j), and NOT this session's own first attempt
(`op_off + op_zfc`, also disproved by direct counter-example against `.s` output). It is
simpler than both: it removes the write-side FC-window term from the read side entirely,
trusting `FR()`'s own `x86_frame_off` regime-4 arm (`off + op_zdepth`) — which tracks the
READER's OWN accumulated carve depth (the replacement expression's cells, e.g. K=16 for a
one-character literal), not anything about the writer's match-primitive history — to reach
the correct absolute address by itself.

## Why this works where the additive attempts didn't

The writer (`bb_match_end.cpp`) stores at `[rsp + op_off + op_fc_disp + 32]` relative to its
OWN pre-unwind RSP. Immediately after, `mov rsp, [r8+8]` unwinds to `cas_rsp_mark` — a value
saved ONCE at MATCH_BEGIN's own alpha, BEFORE any match-primitive fires. Because that mark is
fixed at match-begin time, independent of how many bytes the match's primitives subsequently
carve, the unwind lands at the SAME absolute address on every witness sharing the same
`op_off` header shape — REGARDLESS of `op_fc_disp`. In other words: **the writer's own
`op_fc_disp` term and the unwind's restoration to a carve-independent mark cancel each other
out by construction** — the writer's compile-time offset LOOKS like it depends on
`op_fc_disp`, but the runtime address it resolves to, post-unwind, does not. The reader must
therefore reach that SAME carve-independent address, which means `op_fc_disp`/`op_zpat`/`op_zfc`
must NOT appear in the read formula's arithmetic — exactly the fix. `op_zdepth`'s own separate,
correct accounting (the replacement expression's own K, uniform across all three probed
non-carving witnesses at 16 bytes for a one-char literal) supplies the only remaining term,
and it was ALREADY being applied via `FR()`'s regime-4 arm even before this fix — the bug was
purely the EXTRA, wrong, write-side term riding along on the read side.

## Board results

`corpus/probe/l3/` (m3), SCRIP `cfd5341c`, x64 oracle `x64/bin/sbl`:

| witness | before | after |
|---|---|---|
| `len_nonterm`/`len_pure`/`lit_len` (controls) | PASS | PASS (unchanged) |
| `span_nonterm` | FAIL | **PASS** |
| `rem_nonterm` | FAIL | **PASS** |
| `VACUOUS_terminal_trap` | FAIL | **PASS** |
| `span_concat` | FAIL | **PASS** |
| `span_span_double` (new witness, this session) | n/a | **PASS** |
| `arb_nonterm` | FAIL (flat garbage read) | FAIL (plausible-but-wrong `start`; `end` now CORRECT) |
| `break_nonterm` | FAIL (flat garbage read) | FAIL (same narrower shape as arb) |
| `pos`/`tab_nonterm`/`rtab_nonterm`/`tab_linear3` (carving class) | FAIL | FAIL (untouched, unaffected) |

**3 PASS / 10 FAIL → 8 PASS / 6 FAIL.**

## Broad-corpus regression check

Ran `scripts/test_broad_corpus_snobol4.sh` (336 SNOBOL4 programs, both modes) TWICE — once
with the fix `git stash`ed (baseline) and once restored — and diffed the FAIL/SKIP name sets
with `comm`, not just totals:

- mode-3: **260 → 261 PASS** (net +1; the l3-class flips are a small fraction of this broad
  corpus, most of which doesn't exercise the non-carving splice shape).
- mode-4: **255 → 255 PASS**, unchanged.
- `comm -23`/`comm -13` on the sorted-unique FAIL/SKIP name sets: **both empty** — the uniqued
  name SETS are identical (a few names appear twice in the raw log, once per mode, which is
  why the +1 count doesn't show as a set-difference at the granularity checked). No name
  present in one run's failures and absent in the other's.
- `test_string`/`test_stack`/`cross` (files touched by a stray pre-existing local commit this
  session inherited, see below) still FAIL identically in both configurations — unaffected by
  this fix, consistent with `test_string`'s L-5 status as a documented separate defect.

**Zero regressions, net positive.**

## Anomaly noted, not chased: an unexplained local commit and working-tree state

On resuming this session after a context check-in, `git status` in `/home/claude/SCRIP` showed
`bb_match_replace.cpp` already modified (with a DIFFERENT, working formula from the one this
session had derived and reverted earlier) and a local commit `a27a5b41` ("feature x86 .s
artifacts: regen") sitting ahead of the pushed `05e6b1ae` tip. Neither this session's own
transcript nor the repo's reflog (clone→reset→reset→commit only) accounts for how either
arrived. `git config --local user.name/email` was UNSET in SCRIP when first checked this
session (had to be set fresh to commit), ruling out a config leak from `.github`. This is
flagged here rather than silently absorbed into the narrative: **the state was not trusted on
provenance — it was built, boarded against a freshly-generated baseline, and diffed before any
of it was committed or relied upon**, exactly as anti-pattern §2 requires for any unexplained
number. If a next session can identify the source (a background regen job, a shared container
artifact, or similar), that explanation belongs here; absent one, treat this as a documented
gap rather than a mystery to re-derive an explanation for.

## NOT pushed

Per RULES 2026-08-09: push needs a credential, asked in-chat, not supplied this session.
Both commits (SCRIP `cfd5341c`, corpus `ed55662b`) are LOCAL ONLY. Handoff is NOT complete —
`handoff_status.sh` will report BLOCKED until push succeeds.

## NEXT SEAT, IN ORDER
1. MONITOR-FIRST on `l3_spl_arb_nonterm` (short, wrong-answer class, exactly what the 2-way
   sync-step monitor targets) — do not hand-trace further from `.s` reading alone.
2. Falsify or confirm: does ARB's post-fix `start` read its own extension-counter cell
   (`[rsp+16]`, a small loop-iteration integer, confirmed present in `.s` at `bb_match_arb`'s
   β-loop) instead of the cursor MATCH_END wrote?
3. Re-measure TAB/RTAB per L-3's still-outstanding instruction (orthogonal, not touched by
   this session's fix).
4. Only then L-1 (Defect A) — honour its ⛔ (fixing A alone raises the hang count).
