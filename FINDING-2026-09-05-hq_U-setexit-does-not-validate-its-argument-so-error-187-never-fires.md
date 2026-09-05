# FINDING 2026-09-05 hq_U — `SETEXIT` never validates its argument, so `ERROR 187` never fires; and a plain `:(UNDEFINED)` goto under `&ERRLIMIT` still exits 0 with no diagnostic

**Seat:** hq_U · **Mode:** QUINTET · **Tree:** SCRIP `4d0aba663` + the `rt-goto-transfer-is-failure-blind` cure ·
corpus `e2f9c2f2c` · .github `69ae60ba` · oracle `/home/resources/x64/bin/sbl -bf`, measured by execution
**Companion to:** `FINDING-2026-09-05-hq_U-rt-goto-transfer-could-not-express-failure-so-three-call-sites-read-its-only-return-as-success.md`

Two faces found while establishing the oracle contract for that row. Both are **open**, both have runnable witnesses,
and both were deliberately left uncured — the reasons are in §3 and are about entanglement, not about difficulty.

## 1. Face A — `SETEXIT` accepts a name that is not a label, silently

SPITBOL validates the argument **at the `SETEXIT` call**:

```
	SETEXIT(.NOSUCH)
	OUTPUT = "MAIN"	:(FIN)
FIN	OUTPUT = "FIN"
END
```

| | output |
|---|---|
| SPITBOL | `ERROR 187 -- setexit argument is not label name or null`, postmortem, program stops |
| SCRIP (both modes) | `MAIN` `FIN` — accepted silently |

Under a **nonzero `&ERRLIMIT`** SPITBOL absorbs the 187 and continues (`MAIN` `FIN`), and there SCRIP now agrees —
by a different route: SCRIP arms the handler and fails the transfer, where SPITBOL never armed it. The observable
answers coincide, so this face is invisible to any witness that sets `&ERRLIMIT` first. It is only visible when
`&ERRLIMIT` is at its default, which is why it survived the row that ran right past it.

⭐ **The ordering is the whole witness.** One line moved changes which oracle behaviour you are grading:

| witness | SPITBOL | SCRIP after the transfer cure |
|---|---|---|
| `SETEXIT(.NOSUCH)` **after** `&ERRLIMIT = 10`, then an error | `BEFORE` `AFTER` | `BEFORE` `AFTER` ✅ |
| `SETEXIT(.NOSUCH)` **before** `&ERRLIMIT = 10`, then an error | `ERROR 187`, stops | `BEFORE` `AFTER` ⛔ |

⚠️ Stated plainly because it would be easy to overclaim: for the second row the transfer cure moved SCRIP from one
wrong answer (`BEFORE`, silent `exit(0)`) to a **different** wrong answer (`BEFORE` `AFTER`, survives where the oracle
stops). It is not a regression — nothing that passed now fails — but it is not a cure of this face either, and only
the 187 validation closes it.

## 2. Face B — a plain `:(UNDEFINED)` goto under a nonzero `&ERRLIMIT` produces no diagnostic at all

```
	&ERRLIMIT = 10
	OUTPUT = "BEFORE"
	D = 0	:(NOSUCH)
	OUTPUT = "AFTER"
END
```

| | output | rc |
|---|---|---|
| SPITBOL | `BEFORE` + `ERROR 038 -- goto undefined label` postmortem, stops | 0 |
| SCRIP (m3) | `BEFORE` | **0** ⛔ |

With `&ERRLIMIT` at its default SCRIP *does* report (`ERROR 038 -- transfer to undefined label: NOSUCH`, rc=1) — so
the diagnostic exists and `&ERRLIMIT` swallows it. The mechanism: this face consumes `rt_goto_resolve` through
`src/templates/bb/bb_goto_deferred.cpp` (the TAIL-TRANSFER arm's `test rax,rax; jz`), **not** `rt_goto_transfer`;
`rt_goto_resolve` raises 38, the `&ERRLIMIT` survival arm absorbs it and returns, the resolve returns NULL, and the
box falls through to a silent end of program.

⛔ **Same root — a resolve failure nobody can observe — but a different consumer and a different oracle contract**
(SPITBOL *stops* here; it *continues* in the SETEXIT case). That is why it is not folded into the transfer row:
one cure cannot serve two contracts, and pretending it does would put a false green on whichever is graded second.

Its `&ERRLIMIT=0` arm also carries a separate, already-known defect: SCRIP's postmortem reads `(0) : ... in statement 0`
where the oracle names file, line and statement number. That belongs to the file/line-reporting class
(`FINDING-2026-09-05-seat04-system-fn-protection-errors-carry-no-file-line-rt-stmt-enter-never-fires.md`), not here.

## 3. Why neither was cured on this row — entanglement, not difficulty

⛔ **Face A is entangled with hq_P's in-flight row** `setexit-not-invoked-under-errlimit-survival`. Validating a
`SETEXIT` argument means asking, at the call, whether the name resolves to a label. In **mode 4** a DEFINE'd handler
name is precisely the case whose registration hq_P is landing right now
(`FINDING-2026-09-05-hq_P-m4-drops-both-the-lbl-alias-and-its-registration-so-a-define-named-handler-exits-0-silently.md`).
A validation added today would raise a **spurious 187 on hq_P's own cure's witness**, and the two changes would land
within the hour of each other on a shared box. The ceo's opening telegram names that row as explicitly not hq_U's
mid-landing. **Routed to hq_P with this witness; hq_U takes it the moment their row closes if they would rather not.**

Face B wants its own row and its own board: it changes what happens on *every* unresolvable plain goto, in a
frontend-shared box, and the oracle contract for it is "stop", which is a louder behavioural change than anything in
the transfer row. Filing it with a measured contract is the honest handoff; it is not a substitute for curing it.

## 4. DONE-WHEN for whoever takes these

Both faces already have oracle-cut wants, so the criterion writes itself: extend
`SCRIP/scripts/test_gate_rt_goto_transfer_failure_is_expressible.sh` with the four witnesses above (each `want` cut
from `sbl -bf` at run time, both modes, graded count bumped), and the arm must be **red once** before the cure — Face A
is red today at the `SETEXIT`-before-`&ERRLIMIT` ordering and at the default-`&ERRLIMIT` END-trap shape; Face B is red
today at the nonzero-`&ERRLIMIT` shape. No new witnesses need minting.
