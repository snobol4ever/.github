# FINDING s191 (seat1, `/home/claude1`, Claude Opus 5) — queue row `scorecard-provenance` (rank 1)
# THE BOARD WAS BLIND TO CONTENTION — AND THE WITNESS THAT CONVICTED IT WAS NEVER A CONTENTION ARTEFACT

**SCRIP `7d5ebaaf`** (two commits, both labelled s190 in their subject lines — this FINDING is filed s191 with the wave).
corpus untouched. **No compiler source touched**, so no watermark is claimed and RULES step-4 regen is N/A.
Gates green at the landed tree: `emit_no_lang` · `template_medium_invisible` (0, ceiling 0) · `icn_no_stack` · `icn_one_reg_frame`.

---

## 1. THE CURE, AS BRIEFED — PROVENANCE TRAVELS WITH THE NUMBER

`scorecard_snobol4.sh` is timing-graded (`grade()` turns rc 124 into `TIMEOUT`, nine of twelve suites on a 20s budget) and until
now its output could not distinguish a board measured on an idle box from one measured under a co-tenant. Every META and every
fail-set-by-name in `GOAL-SNOBOL4-100.md` rests on that number. This is the **HQ-27 class** — a stale build is indistinguishable
from a current one by inspecting its output — and it takes the same cure.

| artefact | what it carries |
|---|---|
| `<out>/provenance.tsv` | host · root · pid · jobs · nproc · both git HEADs · **`scrip` binary md5+mtime** · **`libscrip_rt.so` md5+mtime** · start/end wall time · duration · load at start/end · peak/mean load · runnable peak · peers seen · `forced` |
| `<out>/load.tsv` | every `S4E_SAMPLE` (5s): 1-min average, **instantaneous runnable count** (`/proc/loadavg` field-4 numerator), peer count, peer pids |
| `report` header | prints all of it and **computes** CLEAN / NOISY / CONTENDED from the recorded facts |
| registry | box-scoped advisory lock; a second board **refuses**, names the holder (pid, root, jobs, since, out dir), and requires `--force` |
| `one <suite> <program> [N]` | new verb: re-run ONE program N times exactly the way the board runs it, each line stamped with the load |

⛔ **A BOARD WITH NO PROVENANCE IS ANNOUNCED AS SUCH.** Every results dir measured before this commit prints
*"jobs, wall time, load and concurrent-board state are UNKNOWN, so a TIMEOUT row here CANNOT be distinguished from a load
artefact"*. Silence about provenance is the defect; the absence must be as loud as the presence.

## 2. ⛔ THE LOCK THE BRIEF ASKED FOR WOULD HAVE BEEN VACUOUS — IT IS BOX-SCOPED, NOT TREE-SCOPED

The brief said *"an advisory lock file in test-results/"*. **`$SC/test-results/` is per-checkout.** The colliding seats hold
separate clones (`/home/claude1/SCRIP`, `/home/claude2/SCRIP`, …) and therefore separate `test-results/` dirs, so a lock sited
there is **never seen by the seat it exists to announce** — vacuous for the only failure it was asked to catch, and vacuous in
exactly the way this project keeps convicting (the `MEDIUM_*` gate grepping a directory that no longer existed).

MEASURED before choosing the site: all eight seats are **one uid** sharing `/tmp`, `/home` and `/proc`, and see each other's
processes — so a `/tmp/s4e-boards.d` registry is both shared and **liveness-checkable** (`[ -d /proc/$pid ]` is a real test here,
not a guess; stale entries are reaped, not reported). `S4E_BOARDS` overrides.

⭐ **TWO DETECTORS, DELIBERATELY, BECAUSE THEY CATCH DIFFERENT THINGS.** The **registry** names a *cooperating* board exactly and
can refuse to start. The **load sampler** catches every contender that will never register — another runner, a `make -j`, a
browser — and is the only half that works against a non-participant. Neither subsumes the other.

⛔ **REGISTER-THEN-LOOK, NOT LOOK-THEN-REGISTER.** The other order is a TOCTOU in which two boards starting together each see an
empty registry and both run. Two boards racing here therefore both refuse: **fail-closed by choice**, because a loud double
refusal is recoverable in one command and a quiet double run corrupts the headline instrument and says nothing.

## 3. ⭐ CALIBRATION IS THE PART THAT MATTERS — AND BOTH THRESHOLDS WERE FOUND BY MEASUREMENT, NOT BY REASONING

**(a) Excess load is PRINTED; oversubscription is what ALARMS.** This box holds ~4–5 runnable at idle from the desktop alone, so
"peak exceeds my jobs" fires on *every* board ever run here — **a banner that always fires is one every seat learns to skip,
strictly worse than no banner.** CONTENDED is raised on: a registered peer, a `--force` start, or **peak > nproc** (the jobs did
not each hold a core). Foreign load below that line prints as `NOISY` **with its number**, never as "not comparable".

**(b) The alarm rides the SMOOTHED average, not a single sample.** A 6-job board on an idle box sampled `runnable PEAK 13`
against a 1-minute average of **3.69** — each `run_one` slot briefly holds two processes (`timeout` plus its child), and gcc
bursts on top. Alarming on the instantaneous count would have fired OVERSUBSCRIBED on every honest `--jobs 12` board. The
runnable peak is kept and printed (it is the responsive half and shows the burst shape); the **verdict** uses the peak of the
1-minute average, which no single sample can spike. Both target failures still trip it: two `--jobs 12` boards for an hour drive
the *average* past 16 cores, and a foreign burst inside a long board is caught because `load_peak` is the max **across** samples.

## 4. PROVEN WITH TWO REAL CONCURRENT BOARDS, NOT A STUBBED PEER

| test | result |
|---|---|
| B starts while A runs, no `--force` | **REFUSED rc=3**, naming `pid=2386189 root=/home/claude1 jobs=4 since=20:02:41 out=…/A` |
| B starts with `--force` | runs, and its report is **born marked** CONTENDED |
| **A — which started first and clean** | **retroactively reports CONTENDED**, having seen B arrive mid-run |
| quiet 124-program board | ⭐ CLEAN |
| 6-job board beside an idle desktop | · NOISY (comparable) — the calibration case |

⭐ The third row is the load-bearing one: **the first board does not get to think it was clean.** "Self-identifying afterwards"
is only true if the board that was *already running* also says so.

## 5. ⛔⭐⭐ AND THE ROW'S OWN CONVICTION WITNESS DOES NOT SURVIVE THE RE-RUN IT ASKED FOR

The brief convicts the instrument with `csnobol4-suite/nqueens.sno`: five runs of the same script on the same binary giving
`TIMEOUT/TIMEOUT`, `SIG11/TIMEOUT` ×3, `SIG11/SIG11`. **That flapping is real and I reproduced it — but it is not caused by load.**

**BOTH ARMS FLAP IDENTICALLY.** Contended arm (beside a real foreign 12-job board): `SIG11/TIMEOUT`, `SIG11/TIMEOUT`,
`TIMEOUT/SIG11`, `SIG11/SIG11`, `SIG11/TIMEOUT`. **Quiet arm (idle box, load 4.3, runnable 1–3): `SIG11/SIG11`, `TIMEOUT/TIMEOUT`,
`SIG11/TIMEOUT`, `SIG11/TIMEOUT`, `SIG11/SIG11`.** Same spread. No arm effect.

**THE VARIABLE IS ADDRESS LAYOUT.** Under `setarch -R` (ASLR off) the program is deterministic — **0 of 34 runs** diverge, every
one a SIGSEGV at **1.11s**. With ASLR on, **7 of 34** instead run past the budget and are graded TIMEOUT (~21%). Interleaved
on/off reps rule out warm-cache ordering. If the divergence rate were layout-independent, observing 0/34 has probability
≈ 0.79³⁴ ≈ 3·10⁻⁴.

**THE PAIR-FLAPPING IS FULLY EXPLAINED BY TWO INDEPENDENT DRAWS.** m3 and m4 each get their own layout, so the four observed
pairs fall out at ≈ 0.62 / 0.17 / 0.17 / 0.04 — which is what both the brief's five runs and my ten runs show.

**THE DECISIVE COMPARISON.** Across three 124-program boards — one CLEAN, two CONTENDED — **exactly ONE row moved and it was this
one; the other 123 were identical by name.** And boards A and Bf ran **at the same instant under identical load** and *still*
disagreed on nqueens (`TIMEOUT/SIG11` vs `SIG11/SIG11`). **Two boards under the same load cannot disagree because of load.**

⭐ **INDEPENDENTLY CORROBORATED FROM OUTSIDE THIS ROW:** seat2's s191 `gimpel-suite-harness` locked a non-timing-graded prediction
first and the board **returned it to the digit at loadavg 11.30**. Contention at realistic fleet levels is not moving rows.

⛔ **WHAT THIS DOES AND DOES NOT OVERTURN.** It does **not** touch seat5's measured fact that two boards ran simultaneously and
neither knew — that happened, and the instrument's blindness is real and now cured; the timing-grading argument stands on its
own. It overturns only the **use of nqueens as the evidence** for load-induced flapping. The provenance header is what lets these
two be told apart, which is precisely why it was worth building — **but nqueens must not be cited as a contention artefact again.**

## 6. ROUTED, NOT OPENED (asked as follow-on rows)

1. **`nqueens-aslr-divergence`** — the real defect behind the flapping. The fault is in **emitted mode-3 slab code**: SIGSEGV at
   `rip=0x7fffee00176b`, an RX-slab address, not the runtime `.so` and not the driver; `rsp`/`rbp` in the normal stack range.
   Deterministic at 1.11s under `setarch -R`, which makes it **cheap to bisect** — the reproducer is `setarch -R ./scrip --run
   nqueens.sno`, and `scorecard_snobol4.sh one csnobol4_suite nqueens N` is the ready-made N-run harness. m4 flaps the same way,
   consistent with m3 ≡ m4 sharing one codegen.
2. **`scorecard-icon-provenance`** — `scripts/scorecard_icon.sh` is the sibling instrument with the identical disease and is
   **not** covered by this commit. The honest fix is not a second copy of these helpers (spelled-twice disease) but extracting
   `sc_load`/`sc_peers`/`sc_board_*`/`sc_sampler` + the report header into one sourced file both boards use — **ONE AUTHORITY over
   "what was this measured under"**. Creating that shared file is a design call, so it is asked rather than taken.
3. **Any long runner that competes for the box** (`test_broad_corpus_snobol4.sh` and friends) should register with the same
   `/tmp/s4e-boards.d` registry once (2) lands — a contender that never registers is only visible to the load half.

## 7. THE GENERALISABLE MOVE

⭐ **When an instrument can be corrupted by something outside itself, the cure is not to prevent the corruption — it is to make
every number the instrument emits carry the conditions it was measured under, and to make the ABSENCE of those conditions as
loud as their presence.** A lock only stops participants; provenance survives non-participants, survives being ignored, and is
still readable months later on a directory nobody remembers running.

⭐ **And calibrate the alarm against the idle baseline you actually measured, not against zero.** Two of the three thresholds in
this commit were wrong on first writing and were caught only by running the verdict against four real boards. A detector tuned
by reasoning fires on the developer's imagination; one tuned by measurement fires on the failure.
