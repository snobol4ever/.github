# FINDING — hq_P: one runaway Icon program filled the root filesystem and stopped nineteen sessions — and it had already been logged, separately, as a timeout and as a scoring bug, on two other desks

**Date:** 2026-08-23 s267 · **Seat:** hq_P · **Severity:** took the whole box down; Lon ordered an emergency fleet-wide stop.
**Cured:** ~31GB reclaimed under Lon's authority (CEO executed); root 100% → 82%, 22G free. Producers killed. Verified from this seat rather than taken on report.

## 1. What happened

`/` (125G) hit **100% full, 163M free**. Lon ordered all work halted: no builds, commits, pushes, or file writes. Cause, measured:

| dir | size | mtime |
|---|---|---|
| `/tmp/icn_corr_gPVhaD` | 12G | 15:32 |
| `/tmp/icn_corr_vXa5Kj` | 9.2G | 16:29 — **still growing during the stop** |
| `/tmp/icn_corr_NhUjtC` | 7.6G | 15:59 |

**28.8G in three Icon-board scratch dirs.** Behind them, a SCRIP correctness defect seat12 had reported minutes earlier: **`deal.icn` emits 6.79 GB where the Arizona oracle emits 285 KB — 24,000x.** The scratch was never cleaned because the harness's own `timeout 900` killed the script before its cleanup could run.

⛔ Build objdirs (`/tmp/si_objs*`) were **16M total** — the obvious suspect, and not a factor. Worth recording, because that is where a disk-full investigation instinctively starts.

## 2. ⭐⭐ THE FINDING THAT OUTLIVES THE OUTAGE: one root cause, three faces, three desks

The same defect had *already* been logged three times, as three unrelated problems, by three different parties, none of whom could see it was one thing:

| face | who logged it | as what |
|---|---|---|
| the Icon scorecard's `bench_correct` suite scores **0/1 at weight 15**, dragging Icon META to **69.0** against an honest **82.0** | hq_C → hq_P | an *instrument-honesty* bug |
| that suite hits its **900s timeout** | hq_C, and hq_P's own row text | assumed to be *23 collectively slow benchmarks* |
| the root filesystem filled | Lon | an *infrastructure emergency* |

⛔ **I minted the scoring fix (`icon-board-timeout-scored-as-zero`) BEFORE knowing the cause, and it would have made things worse alone.** Teaching the board to abstain on a timeout, and nothing else, would have turned a loud 0/1 into a quiet abstention — **hiding the program that was filling the disk**, while producing a more honest-looking META. The instrument would have improved and the defect would have gone dark.

That is the general hazard and it deserves a name: **fixing a symptom's REPORTING can conceal the symptom's CAUSE.** An abstain must therefore *say what it abstained on* — "this program was capped/timed out" is a finding, not an error to swallow. That requirement is now written into `icon-sweep-scratch-hardening` step 4.

## 3. The second correction: the git-corruption premise was wrong

The stop order's rationale was that a full root corrupts git objects on write. **Measured:** `/` is `nvme0n1p6`; **`/home` is a separate partition, `nvme0n1p7`, at 31% with 332G free.** `df` on `/home/claude_P/SCRIP/.git` and on `/home/resources/postoffice` both report `/home`. **The repos and the postoffice were never on the full filesystem and were never at corruption risk.** Commits and pushes were safe throughout; CEO accepted the correction.

⭐ The real asymmetry, and it is invisible in the scripts: **`/tmp` is on the 125G root; `/home` has 503G.** A harness writing "to /tmp" reads as harmless and is not.

## 4. Cures

- **`icon-sweep-scratch-hardening`** (rank 0, hq_P lane, CEO's four parts): scratch under `/home` via one resolved authority, never a bare `/tmp` literal · `trap cleanup EXIT INT TERM` on every scratch creation — *cleanup that only runs on the success path is not cleanup, because the failure path is when the scratch is biggest* · cap per-program output and report the cap · the abstain must name what it abstained on. ⭐ Plus one addition of mine: **sweep the class** — grep every board/bench script for bare `/tmp` scratch and untrapped `mktemp -d`. Icon is where it detonated, not where it is unique.
- **`icon-deal-runaway-output`** (rank 0, routed to hq_C — a wrong answer by content is their lane). Its literal first instruction is *cap the output before you reproduce it*, because reproducing it uncapped is what caused the outage. Hypothesis to check first: 24,000x output looks like a generator that never terminates or a suspend that re-yields — possibly the same family as the D2-suspend cluster `icon-n2-generator-activation-frames` targets.

## 5. Process notes worth keeping

- **A false alarm I raised and then retracted:** during the stop, `pgrep` still showed three `scorecard_icon.sh` PIDs and I reported the disk was still filling. It was — the newest dir's mtime was four minutes old — but by the time CEO acted the processes were already dead. I checked rather than letting the alarm stand. Raising it was right; leaving it unretracted would not have been.
- **I did not kill another session's processes.** They were actively consuming the last 163M, and the temptation was real. Killing another seat's job is not hq_P's to do unilaterally; I reported with a recommendation and CEO executed under Lon's authority. That is the interlock working, and it cost about ninety seconds.
- ⛔ **A message I sent about this was silently mangled** — shell backticks in the body were executed as command substitutions and ate the row name, the file paths and a sibling-row reference. I caught it only by reading back what actually landed in the recipient's inbox. **Read back what you sent when the body contains backticks**; the send reports success either way.
