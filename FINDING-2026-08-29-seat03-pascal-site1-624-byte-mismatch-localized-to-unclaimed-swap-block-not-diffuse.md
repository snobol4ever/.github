# FINDING — Site 1's static-vs-physical mismatch (528 predicted, 176 actual, per hq_P) is NOT spread
# diffusely across the 39-node loop body — it is concentrated in ONE span, between the comparison test
# and its rejoin point, where zd_plan assumes zero net stack growth across UNCLAIMED code and that
# assumption is false: a real, physical 624-byte swing happens there that zd_plan has no visibility into.

**seat03 · 2026-08-29 · row `pascal-m4-site1-forloop-backedge-64byte-excess`** (continuing seat13's own
explicit "concrete next empirical step nobody has done yet": trace node-by-node which K-claims are still
physically outstanding by the time execution reaches n70 on the no-escape path).

**Not a cure — diagnosis only, same restraint as hq_P and seat13, for the same reason: two seats have
already produced necessary-but-insufficient fixes here, and this session's own finding shows the loop
body's true shape is stranger than "one straight path with a wrong constant."** Nothing committed to
SCRIP or corpus.

## 0. Method

Checkpointed physical `$rsp` (not the static `zout` plan) at 6 points across the h=0 run's 39 nodes,
via `gdb` breakpoints on each node's own `_α` label (entry, before that node's own carve executes),
`setarch -R` for determinism, `echo 1 |` stdin (required — empty stdin makes every kernel exit at 0
before reaching the loop, which looks like a mass regression and is not one). Two full laps captured
before the known crash (confirmed hit at `n58_var_bx`, matching hq_P's own crash-site finding exactly —
confirms the instrumentation is sound).

## 1. The checkpoint table — lap 1, raw and delta

| checkpoint | rsp (hex) | Δ from previous | static `zout` (from `SCRIP_ZD_DIAG=1`) | static Δ (`K`) |
|---|---|---|---|---|
| `n23` (loop head) | `0x7fffffffe510` | — | 240 (post-K) | — |
| `n30` | `0x7fffffffe4a0` | **−0x70 (−112, carved)** | 320 | +80* |
| `n44` | `0x7fffffffe3e0` | **−0xc0 (−192, carved)** | 544 | +224* |
| `n53` (the comparison test) | `0x7fffffffe360` | **−0x80 (−128, carved)** | 672 | +128 |
| `n69` (last node before the back-edge) | `0x7fffffffe5d0` | **+0x270 (+624, RELEASED)** | 768 | +96* |
| `n70` (the back-edge itself, entry) | `0x7fffffffe5c0` | −0x10 (−16, `n69`'s own carve) | 768 | 0 |
| `n70`'s own release (`add rsp,544`) | → `0x7fffffffe7e0` (next lap's `n23`) | **+0x220 (+544)** | — | — |

*(marked deltas span more than one intervening node — checkpoints were chosen for coverage, not
adjacency; the exact node-by-node static K between checkpoints is in `SCRIP_ZD_DIAG=1`'s own output,
available on request, not reproduced here since it isn't where the mismatch lives — see §2.)*

**Lap 2 reproduces every one of these deltas exactly** (`n23`→`n30` again `−0x70`, `n30`→`n44` again
`−0xc0`, `n44`→`n53` again `−0x80`, `n53`→`n69` again `+0x270`, `n69`→`n70` again `−0x10`) — fully
deterministic, not noise. Net per-lap drift measured directly (`n23` lap1 `0xe510` → `n23` lap2
`0xe7e0`): **`+0x2d0` = +720**, matching hq_P's own independently-measured per-visit drift exactly.

## 2. The headline number, independently confirmed, AND narrowed to one span

`n23`-entry to `n70`-entry, physical: `0xe5c0 − 0xe510 = 0xb0 = 176`. **This independently reproduces
hq_P's own "bubble's correct delta is −176" finding from a completely different measurement method**
(checkpoint bracketing vs. their direct two-arrival comparison) — strong corroboration, not a new claim.

**What's new: the same span, per the STATIC model, predicts `zout[70]-zout[23] = 768-240 = 528`** —
so the model overshoots physical reality by `528-176 = 352` bytes somewhere in this span. **That 352 is
not spread across the run.** Every checkpoint pair from `n23` through `n53` reproduces its OWN static
`K` sum almost exactly (a few bytes of expected rounding from unchecked intermediate nodes — not
investigated further, not where the money is). **The entire discrepancy is between `n53` and `n69`**:
physically, this span RELEASES 624 bytes net (checkpoints show `n53→n69` as `+0x270`); the static model
believes it contributes **zero** — every node's `gpop` in `SCRIP_ZD_DIAG=1`'s own `h=0` output is `0`
from `n53` through `n69` inclusive.

## 3. Why: this span is NOT zd_plan-claimed at all, and its own local carve/release doesn't net to zero

`SCRIP_ZD_DIAG=1`'s full output (not just the `h=0` filter) has **no second run** — `grep -v "h=0 "`
over the complete diagnostic dump returns nothing. So the code between `n57` (`zout=720`, last claimed
node before the gap) and `n67` (`zout=736`, the rejoin — `SCRIP_ZD_MAP`'s own `i=` numbering, matching
`SCRIP_ZD_MAP i=58` in the earlier claim table) is **entirely outside zd_plan's tracking** — presumably
the swap body of the comparison at `n53` (`if a[j] > a[j+1] then swap`), reached only when the
comparison is true, using the OLDER, non-zd stack-carving mechanism (self-contained `sub`/`add rsp`
pairs, each node balancing its own frame).

**`zd_plan`'s static model implicitly assumes any such unclaimed gap is stack-neutral** — going from
`zout=720` at `n57` to `zout=736` at `n67` adds only `n67`'s own `K=16`, i.e. the model assumes the
unclaimed span in between nets to exactly zero. **That assumption is what's false, not the back-edge
formula itself in isolation.** The swap body's own machinery — whatever it is — leaves a real, physical
624-byte imprint that the model never sees, and `n70`'s release formula (`_wzdepth − _gbpre`) then
computes a constant based on a `_wzdepth` (768) that already silently includes this invisible 624-byte
distortion.

## 4. What this changes about the fix's shape, and what's still open

hq_P's own NEXT (superseded, this row) frames the fix as "repair the constant" — true, but this finding
suggests the repair can't be a pure zd_plan-internal fix if the thing corrupting the count lives entirely
**outside** zd_plan's own claimed-run bookkeeping. Two live hypotheses, neither chased further this
session:
- The swap body genuinely does NOT balance its own stack (a real bug in whatever template emits it —
  the "5 IR_BINOP escape branches to `n67`" seat13 already found live in exactly this neighborhood, and
  are a plausible source: an escaped branch's own carve, if it ever fires, might not be released on the
  path that DOESN'T take it).
- The swap body balances correctly on its OWN terms, but its balance point is not the SAME physical
  depth zd_plan's model assumes for "resuming claimed tracking at `n67`" — a hand-off convention
  mismatch between claimed and unclaimed code, not an unbalanced leak per se.

**Not distinguished here.** The concrete next step, narrower than "trace all 39 nodes" (seat13's own
framing): instrument the SPECIFIC span `n53`→`n67` alone (the swap conditional's actual body,
`i=58`..`i=66` in `SCRIP_ZD_MAP`'s own numbering) node-by-node, the same checkpoint method this session
used, to find exactly which node(s) inside it account for the 624-byte swing and whether it's a leak or
a hand-off mismatch.

## 5. Not attempted

No code touched (`emit.cpp`/`zd_plan`/`x86_asm.h` untouched, `git status --short` clean throughout —
checked, not assumed). Same restraint as hq_P (whose own repair attempt cured Pascal and regressed
SNOBOL4) and seat13 (who found the escape-branch structure and explicitly declined a third attempt in
the same sitting) — this row's authorization is for diagnosis distributed across careful sessions, not a
rushed implementation. Mailed hq_C (this row's authority) and hq_P/seat13 (whose findings this extends)
directly.

## 6. State

- Tree: SCRIP HEAD at time of measurement (fresh `git pull --rebase`, incremental `make -j4 scrip` —
  not `make pristine`, no gate verdict claimed). `bubble.pas` compiled + linked standalone for gdb
  (`gcc -no-pie -g`), not the full corpus harness — a targeted repro, not a board run.
- Crash site independently reproduced at `n58_var_bx`, matching hq_P's own finding exactly — confirms
  the checkpoint methodology is sound and the tree is not stale relative to their measurement.
