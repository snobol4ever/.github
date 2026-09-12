# FINDING — a classification measured for one question was consulted for a second, and moved eleven error codes on evidence about one

**hq_U, 2026-09-12 · SCRIP `856852a45` · corpus `854e3597f` · MODE NONET**

The regression is mine. The coo bisected it by reading, off their daily SNOBOL4 master pass:
**1869/1894, FAIL=1** where the previous pass read FAIL=0, `keyword_replace_branch_9`.

## The measurement

`70a0bc6c0` (hq_U, 2026-09-11) cured a real defect: `:(NOSUCH)` under a nonzero `&ERRLIMIT` printed
nothing and exited 0 where `sbl -bf` prints the ERROR 038 postmortem and stops. The cure made the
`&ERRLIMIT` survival arm consult `core_err_is_terminal()`.

⛔ **That predicate already existed, already held eleven codes, and answers a different question:
*does this error exit nonzero*.** Reading it for *may this error be absorbed* moved eleven codes on
one commit's evidence about one of them.

Measured both sides, each witness under `&ERRLIMIT = 10` against the one oracle:

| code | witness | `sbl -bf` | us, before the cure |
|---|---|---|---|
| 022 undefined function called | `X = NOSUCHFN(1) :F(NX)` | **absorbs, prints nothing, continues rc=0** | ERROR 022, exit 1 |
| 038 goto undefined label | `:(NOSUCHLABEL)` | reports and stops | reports and stops ✓ |
| 242 return from level zero | `:(RETURN)` at depth zero | reports and stops | reports and stops ✓ |

⭐ **And the number that makes this a class rather than a typo: of the eleven members
(20 21 22 23 26 27 29 30 31 38 39), this tree raises exactly THREE — 22, 29 and 38.** Eight are raised
at zero sites (`grep -c 'core_runtime_error( *NN' src/`). So the first consultation of that list
silently changed behaviour for codes **for which no witness can be minted at all**, and the one live
member it was wrong about was wrong the same day.

## The cure, and why it is not a one-line revert

Taking 022 out by hand would have left the polarity intact: membership in an unvalidated list would
still decide a question the list was never measured for, and the next code added to it — by anyone,
for the exit-status question — would silently acquire an `&ERRLIMIT` meaning too.

`core_err_survives_errlimit()` now answers the `&ERRLIMIT` question alone. **Its default is SURVIVAL,
and every non-survivable case is an explicitly measured exception.** A code nobody has put to the
oracle therefore keeps the behaviour we already matched byte for byte, instead of quietly acquiring a
new one. `core_err_is_terminal` keeps deciding exit status. 029 is recorded as **NOT VALIDATED** rather
than assumed: it is raised only from by-name operator dispatch and every direct spelling is a parse
error in both engines.

Gate `test_gate_errlimit_survival_is_measured_per_code.sh`, wired (CEO-381). Negative-tested by
restoring `case 22:`: **2 of 6 arms red, both the 038 and 242 control arms green** — so it reds on this
regression specifically and would not go green on a blanket "absorb everything" revert of either
earlier cure.

## ⛔⭐ The consequence nobody could have seen, and the reason this is filed as a class

hq_S's `99d4be3aa` added **242** to `core_err_is_terminal` — correctly, for the exit-status question
they were answering. At that moment that predicate *also* decided `&ERRLIMIT` absorption, because of my
70a0bc6c0. **Splitting the two questions would have silently made 242 survivable under `&ERRLIMIT`,
undoing their cure, in a commit whose message was about 022.** I measured 242 before deciding and
carried it across with its measurement attached; it is a control arm in the gate.

⭐ **The general form:** A CURE THAT LANDS AS A ROW IN A SHARED CLASSIFICATION INHERITS EVERY QUESTION
THAT CLASSIFICATION IS CURRENTLY BEING ASKED — including questions added after the cure, by other
seats, without notice. Two seats each made a correct one-line change to the same list within a day,
for two different questions, and the second one's correctness depended on the first one's coupling
continuing to exist.

The cheap discipline that would have caught it at the source: **before adding a case to a shared
predicate, grep its call sites and count how many questions it is answering today.** `core_err_is_terminal`
had two call sites; one of them was three weeks older than the question it was being asked.

⚠ **Not validated and named as such:** `core_err_is_fatal` (19 24 25 35) is consulted by the same arm
and was never put to the oracle either. It predates 70a0bc6c0 so it is not this regression, but it is
the same shape one step over, and nobody owns it as of this write.
