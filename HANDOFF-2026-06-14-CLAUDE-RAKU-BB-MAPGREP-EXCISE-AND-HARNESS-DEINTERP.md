# HANDOFF 2026-06-14 — Raku: map/grep abort→EXCISE regression fix + de-interp the smoke harnesses

## Session: GOAL-RAKU-BB. Restore the m3/m4 done-bar (no aborts) and make the smoke gates green after the interpreter deletion; then read the Rakudo sources to ground the gather/map/grep semantics.

**SCRIP HEAD at open: `6e87566` (local). origin/main advanced to `023fb43` during the session (3 peer
commits: PL-GZ rung28 rethrow + Icon m3/m4 +1/+3). Rebased cleanly; pushed. SCRIP origin/main now `b63cc45`.**

**Gates at close — ALL THREE smoke gates rc=0:** Raku m3/m4 31 PASS / 0 FAIL / 7 EXCISED; Icon m3/m4 12/12;
SNOBOL4 m4 7/7. Invariants: g_vstack=0, bb_bin_t=0, IR_NFA=0. (Mode 2 / `--interp` no longer exists.)

---

## WHY (the regression, root-caused)

`a2440f4` ("DELETE the IR-graph interpreter") bomb-stubbed `bb_mapgrep_prepare` — its body used to MATERIALIZE
the map/grep list by running the now-deleted interpreter (`IR_interp_once` over the source + body sub-graphs).
But that commit LEFT `graph_native_emittable_mode` (`src/driver/scrip.c`) ADMITTING `IR_MAP`/`IR_GREP`
(`rhs_kind_ok` returned 1 for `IR_GATHER||IR_MAP||IR_GREP`). So a map/grep program passed the gate, reached the
`[NO-IR-INTERP]` bomb in `bb_mapgrep_prepare`, and **aborted** — violating the done-bar "PASS or EXCISED, never
abort." (The already-dead `kind_native_stub` had carried the correct `IR_MAP||IR_GREP` excise intent before the
dead-code sweep removed it; it had been unreachable, so removing it was behavior-neutral — it was NOT the cause.)

Separately, `a2440f4` + the CLI trim `94c94f4` deleted `--interp`, but the three per-language smoke harnesses
still INVOKED it. `test_smoke_raku.sh` and `test_smoke_icon.sh` GATED on `[ $F2 -eq 0 ]` → with m2 structurally
all-FAIL they returned **rc=1** despite clean m3/m4. `test_smoke_snobol4.sh` already gated on m4-only (rc=0) so
its m2 invocation was cosmetic noise.

---

## WHAT LANDED — 3 commits (`1c64469` / `2860563` / `b63cc45`)

### 1. `1c64469` — map/grep EXCISE not abort (`src/driver/scrip.c`, +2 lines net)
- Node-loop guard in `graph_native_emittable_mode`: `if (nd->op == IR_MAP || nd->op == IR_GREP) return 0;`
  (placed right after the `IR_CASE`/`IR_INITIAL` structural excises).
- `rhs_kind_ok`: `IR_GATHER || IR_MAP || IR_GREP` → just `IR_GATHER` (gather has a real self-contained
  `bb_gather.cpp`; map/grep do not). This also closes the nested-only-RHS hypothetical.
- RESULT: map_range/grep_range/map_over_gather/grep_over_gather go **abort → clean `[SMX]` EXCISE**;
  `gather_take` still PASSes natively. Raku m3/m4 31 PASS / 0 FAIL / 7 EXCISED (was 31 / **4 FAIL** / 3 EXCISED).

### 2. `2860563` — Raku smoke → 2-mode gate (`scripts/test_smoke_raku.sh`)
Removed the `--interp` invocation + all m2 bookkeeping (P2/F2, the `[%s]` field); gate on zero silent m3/m4
FAIL + the MODE3/4_MIN floors. Also fixed a doubly-stale comment ("lowers to NFA-as-BB; m2 oracle" → regex
rides the C matcher, m3/m4 EXCISE). Gate now rc=0.

### 3. `b63cc45` — Icon + SNOBOL4 smoke de-interp (`scripts/test_smoke_icon.sh`, `scripts/test_smoke_snobol4.sh`)
Same residue: removed every `--interp` invocation + m2 bookkeeping.
- Icon: gate was `[ $F2 -eq 0 ] && floors` → **rc=1**. Now `m3 AND m4 zero-FAIL + floors` → rc=0. ⚠️ This
  STRENGTHENS the Icon gate (floors-only → zero-FAIL); m3 replaced m2's build-sanity role. One-line revert if
  the Icon owner wants it looser. Behavior-neutral for the Icon compiler (no Icon source touched; m3/m4 12/12).
- SNOBOL4: dropped the `run_m2` fn + its `run_all` call + P2/F2 + the m2 summary line (gate already m4-only).

All three harnesses are now free of any live `--interp`; remaining `interp` mentions are explanatory comments.

---

## RAKUDO SOURCE CORRECTION (read `6_rakudo-main` this session — do-not-re-derive)

I had earlier characterized gather as "a real generator, materialized" vs map/grep "lazy" — **wrong** per the
canonical sources. In real Raku ALL THREE are lazy:
- **gather/take** (`src/core.c/Seq.rakumod` `sub GATHER` → `src/core.c/Rakudo/Iterator.rakumod` `class Gather
  does Rakudo::SlippyIterator`) is a first-class **continuation coroutine**: the block runs under
  `nqp::handle(&block(),'TAKE',…)`; each `take` decrements `$!wanted` and at 0 captures the continuation
  (`nqp::continuationcontrol(0,PROMPT,…)`) and SUSPENDS mid-block; `pull-one` sets `$!wanted=1` and
  `nqp::continuationreset`s to resume to the next `take`. One value per pull, producer paused between yields.
- **map/grep** (`src/core.c/Any-iterable-methods.rakumod`) return `Seq.new(<pull-one iterator over
  SELF.iterator>)` — lazy, applying the closure/test per pulled element.

SCRIP's `bb_gather.cpp` only emits the **degenerate literal-int-take** case: `bb_gather_prepare` constant-folds
each `take(N)` at compile time into a baked `.quad` array and the emitted loop cursors over it (one value per
β-resume). It passes the smoke (`10/20/30/done`) but `take($computed)` or a `take` in a loop ABORTS — far from
real gather.

**IMPLICATION for RK-EMIT-MAP/GREP + RK-GRAM-3:** the generator-PUMP the goal calls for ("closure emitted as
native, invoked per element, SUSPEND/EVERY driver") IS exactly Rakudo's continuation model, and the four-port
box resumption (γ advance / ω redo / β resume) is its native analog. The same suspend/resume-across-a-boundary
substrate serves BOTH the real map/grep pump AND the recursive-descent grammar seam.

---

## ⚠ PROCESS NOTES (read before next push)

- **The bare `git push origin main` fails** ("could not read Username"). Use the token URL:
  `git push https://<TOKEN>@github.com/snobol4ever/SCRIP.git HEAD:main` (do NOT `git remote set-url` — keeps the
  token out of `.git/config`). Push SCRIP first, `.github` LAST. Confirm `git log origin/main --oneline -1`.
- **origin moves under you.** This session origin advanced +3 mid-work (Prolog + Icon peers). `git fetch` +
  `git rebase origin/main` BEFORE pushing. The peer's 266-line `scrip.c` change did NOT touch the map/grep
  gate region (my two edit-sites were byte-identical merge-base↔origin), so the rebase was conflict-free — but
  ALWAYS rebuild BOTH (`rm -f scrip && make -j4 scrip && make libscrip_rt`) and re-gate after a rebase.
- **`scrip` statically links the runtime; the `.so` is mode-4 only.** After any runtime `.c` edit rebuild both.
  (This session only `scrip.c` (driver, in the `scrip` binary) + `.sh` changed, so the map/grep fix did not need
  the `.so` — but the rebase picked up peer runtime/lower changes, so both were rebuilt anyway.)

---

## Session Setup (next session)
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
rm -f scrip && make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_raku.sh      # rc=0 : m3/m4 31 PASS / 0 FAIL / 7 EXCISED
bash scripts/test_smoke_icon.sh      # rc=0 : m3/m4 12/12
bash scripts/test_smoke_snobol4.sh   # rc=0 : m4 7/7
# (--interp is GONE; the harnesses are 2-mode. test_gate_raku_nfa_oracle.sh is also gone — NFA-BB was deleted.)
```

## ORDER OF WORK for next session
1. **RK-GRAM-3 (THE SEAM)** — the recursive-descent grammar engine. Replace `gram_expand`'s flatten-to-NFA with
   subrule `<name>` recursion + backtracking on the four-port box-resumption substrate; build a real Match tree;
   then `$<name>`/`$0` capture access. **NEEDS FULL BUDGET + read `ARCH-x86.md` AND `ARCH-SCRIP.md` first.** The
   continuation/PUMP insight above is the design key.
2. (Independent) **RK-EMIT-MAP/GREP** — the real non-materialized map/grep PUMP (shares RK-GRAM-3's machinery).
   This promotes the 4 currently-EXCISED map/grep tests to PASS. NOTE: a real gather (beyond literal-int takes)
   is the same PUMP work.

## Commits this session (pushed + verified on origin/main)
| Commit | Repo | What |
|---|---|---|
| `1c64469` | SCRIP | Raku m3/m4: map/grep EXCISE not abort — restore gate clause lost when interp deleted (a2440f4) |
| `2860563` | SCRIP | Raku smoke: de-interp the harness to a 2-mode gate; drop deleted --interp; fix stale NFA-BB comment |
| `b63cc45` | SCRIP | Icon+SNOBOL4 smoke: de-interp the harnesses (drop deleted --interp) |
| (this doc + GOAL-RAKU-BB watermark) | .github | handoff |
