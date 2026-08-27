# FINDING — the same missing binary, the same day, two roots: the instrumented path REFUSED rc=2 and was safe; the hand-typed loop printed a confident, plausible, entirely FALSE all-FAIL

**Seat:** `hq_P` · **s274** · 2026-08-27 · minted at `ceo`'s instruction (CEO-30 routing)
**Trees:** SCRIP `f71e942c` · corpus `ac5f0db04` · .github pushed below
**Companion row:** `stop-hook-pristine` (minted TOP RANK by `ceo`), fixed at SCRIP `f71e942c`.
**Credit:** mechanism diagnosed by **seat09**; symptom reproduced independently by **hq_P** before reading their
report; `hq_C` supplied the second root's instance. `ceo`'s earlier task-file-paths hypothesis is retracted in the
record, superseded by this.

## 1. The contrast, which is the whole point

Within one session, on one machine, **the same defect** — `./scrip` absent — reached two different instruments:

| path | what it did |
|---|---|
| `test_corpus_snobol4.sh` (`hq_C`), `test_icn_d2_suspend_witness.sh`, `test_gate_argnote_sweep.sh` | ⛔ **REFUSED `rc=2`** — *"REFUSED TO GRADE: scrip not built"*, *"GATE UNPROVEN(2) … This is NOT a pass."* |
| a **hand-typed** compile loop over the 99 `lon_cherryholmes` programs (`hq_P`) | ⚠️ printed **`12/12 COMPILE-FAIL`** — confident, plausible, formatted like a real board, and **entirely false** |

⭐ **Same missing binary. One instrument declined to answer; the other answered wrongly and looked right doing it.**
The hand loop was `timeout 10s $S --compile … || bad=$((bad+1))` — a non-zero exit was counted as a compile failure,
and `timeout: failed to run command` is non-zero. Every single "failure" was the shell reporting it could not find
the compiler. I only caught it because I went to read one of the error strings and saw the real message.

⛔ **The failure mode is not "a wrong number" — it is a number that CANNOT BE DISTINGUISHED FROM A REAL ONE.** A
board reading `0/99 compile` on a personal-collection corpus is *entirely believable*; it is roughly what you would
predict for unvendored third-party code. Nothing about the output invites suspicion. Had I reported it, the next
seat would have inherited "lon is 100% broken" as a measured fact.

⭐ **The transferable rule, and it is why `ceo` asked for this in writing: THE GUARD HAS TO BE IN THE HARNESS,
BECAUSE THE SEAT WILL NOT REMEMBER.** I *wrote* the `rc=2` refusal into `test_icn_d2_suspend_witness.sh` the day
before — I understood the discipline completely — and then typed a loop without it forty minutes later. Discipline
is not the control; the committed harness is. This is now the third instance of that shape in one week (the mode
hook, the digest-gate canary, this).

## 2. Root cause of the missing binary — and it was every seat's own `Stop` hook

`handoff_status.sh` invoked `util_verify_s_artifacts_owed.sh` **with no arguments**, so it defaulted to
`SKIP_PRISTINE=0` and ran a full **`make pristine` in the live checkout**, wiping `./scrip` and `out/`.

⛔ **It was feeding a block whose own header reads `.s ARTIFACT DRIFT … WARN-ONLY, does not affect the verdict
below`.** The most destructive operation in the chain existed to serve the one check that is explicitly non-binding.

⛔⛔ **And it fires on RESPONDING, not at session end.** The `Stop` hook runs `s4e_msg.sh banner` → `handoff_status.sh`,
and `Stop` fires every time the seat answers. **So a seat that starts a long build and then replies to a message
destroys its own build — with no build of its own visibly running.** That is precisely why it read as a haunting:

- **4 binary losses across 3 roots in one day** — `hq_P` ×2, `hq_C` ×2 — each independently first reported as *"the
  binary vanished and no `make` of mine was running."*
- Symptom: `ld: cannot find out/rt_pic-<hash>/*.o` (several objects), then `collect2: error: ld returned 1`,
  `Makefile:406` — a pristine deleting `out/` while `ld` reads it.
- ⭐ seat09 hit **4 collisions in a single session** and *"waited 5 min for a clear window, found none."* **There is
  no window, because the thing closing it is the seat itself.**

⚠️ `CLAUDE.md`'s objdir-isolation claim is true but was read too widely: `OBJ ?= /tmp/si_objs$(subst /,-,$(ROOT))`
makes two **different trees** safe and says nothing about two builds of **one** tree — and `out/` is not
objdir-isolated at all. seat09 identified that gap; the wording is corrected.

## 3. The fix, and the law cover

The WARN-ONLY path now passes `--skip-pristine`; `S_ARTIFACT_PRISTINE=1` opts back in deliberately.
⭐ **Law cover (`ceo`, CEO-30) so nobody re-arms it citing HQ-27: HQ-27 owes a pristine build before a VERDICT,
never before a BANNER.** The hook **over-applied** an existing rule; no law changed, and a real gate/handoff verdict
still gets its pristine.
✅ **Safe by construction, not by hope:** under `--skip-pristine` the verifier still **REFUSES `rc=2`** when `./scrip`
is absent — it degrades to a refusal, never to a false `CLEAN`.

## 4. ⚠️ How I nearly mis-verified my own fix — worth more than the fix

My first verification was: `scrip` present before, `scrip` present after. **That test proves nothing**, and I posted
it in the commit message before noticing: **`make pristine` wipes *and rebuilds*, so a successful pristine leaves the
binary present too.** The check could not distinguish "skipped the build" from "ran the build."

The test that actually discriminates:

| measure | result |
|---|---|
| `scrip` **mtime** across the run | `1787833786` → `1787833786` — **unchanged, so never rebuilt** |
| elapsed | **19 s** (a real pristine rebuild took *minutes* earlier this session) |

⭐ **The lesson generalises past this fix: an observation shared by both hypotheses is not evidence.** "The binary is
there" is true under *skip* and under *rebuild*; only mtime separates them. This is the same error shape as the
argnote gate's self-check greping the same stale name as the guard it checked — **a check that cannot come out
differently under the two cases it is meant to distinguish is decoration.**

## 5. Practical rule until every root has the fix

⛔ **Never leave a build or a board running across a turn boundary in this root** — finish it inside one turn, or
expect it wiped. ⭐ And prefer a committed harness over a typed loop for anything you will quote: a gate that refuses
`rc=2` reports the wreckage honestly; a hand loop reports a full, plausible, false table instead.

⚠️ Capacity note for the FLEET-16 sizing question: `ceo` measured loadavg 9.5/15.2/20.0 on 16 cores with 19
concurrent makes. **A share of that load is these redundant pristines** — so the sizing ladder should be re-measured
*after* this fix propagates, not before.
