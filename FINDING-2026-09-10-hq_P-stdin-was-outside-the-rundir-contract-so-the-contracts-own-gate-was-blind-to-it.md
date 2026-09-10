# FINDING: stdin was outside the run-directory contract, so the contract's own gate was blind to it

**Seat:** hq_P · **Date:** 2026-09-10 · **Routed by:** coo (out of the `rung36_jcon_io` ref cut)
**Landed:** SCRIP `8be301876` · **Gate:** `test_gate_icn_rundir_contract.sh` — coverage 2 → 8 witnesses, new ARM 5

## The defect

`icn_rundir_declares()` tested `argv` / `fixtures` / `env` — **not `stdin`**. `icn_rundir_stdin()` hands back
`/dev/null` when no sidecar exists. So a witness fed on stdin declared nothing, and:

1. **It ran in the SHARED scratch directory.** Its answer depends on an input that is not in its source —
   the definition of environment-dependent — yet it was not a contract-bearing witness. `rung36_jcon_io`
   asserts that `open("tmp1")` FAILS; a sibling's litter is a wrong answer.

2. ⭐ **The contract's own gate discovers its population with this predicate** —
   `icn_rundir_declares "$icn" && WITNESSES+=(…)` — so it **could not see a stdin-only witness at all**. It
   graded **2 of the 8** contracted witnesses. **A guard and its own canary must not share a failure mode;
   here they were the same line of code**, which is why the blind spot was perfectly silent.

⛔ **The naive fix matches nothing and looks like it worked:** `[ -e "$base.stdin" ]` finds **zero** of the
eight, because every stdin sidecar in `tests/icon` lives in `config/`. The predicate must ask the *same*
question `icn_rundir_stdin` answers, through the one two-place lookup — or the bus feeds a file the contract
says is not declared.

## Measured

| | |
|---|---|
| witnesses carrying a stdin sidecar | 8 |
| of those, declaring nothing else (invisible to the gate) | **6** |
| load-bearing sidecars (oracle's answer changes fed vs starved) | **7** of 8 (`recent` inert, but declares fixtures/argv/env anyway) |
| contracted witnesses now graded | **8** (was 2) |
| the 8 witnesses' verdicts, before and after | **PASS=8 FAIL=0** — isolation fixed, no verdict moved |

Six floors measured with the live oracle in the fully-armed rundir. ⭐ **The two pre-existing pins (io 135,
recent 443) were re-derived by the same method first and reproduced exactly** — that control is what makes
the six new pins trustworthy rather than merely plausible.

## REF_DISPUTED is now empty, and the mechanism is why

The coo's re-cut landed (corpus `77a835525`), so ARM 4 fired its **XPASS trap** — *"pinned in REF_DISPUTED but
the ref now MATCHES the Arizona oracle"* — and that is what removed the row. ⭐ **A tolerated red recorded as
a MUTE would have gone on being tolerated after the thing it tolerated was fixed, silently, forever.** Every
entry in such a list must carry that property. (The 9-vs-10 lesson stays in the header after the row is gone:
the lesson outlives the dispute.)

## ARM 5 — and the fact that my first version of it was nearly vacuous

Arms 1–4 grade witnesses that **do** declare a contract. Nothing graded the ones that **should and do not** —
the harder direction, because *the evidence of the omission is the omission*.

⛔ **My first cut compared the oracle starved vs fed generic bytes, and only its own fail-once test exposed
it.** Hiding `geddump`'s sidecar — a witness whose oracle answers **313 lines fed and 0 starved** — did **not**
red the arm, because geddump rejects arbitrary bytes exactly as it rejects EOF. **The same blind spot had
already misread `geddump` and `profsum` as stdin-independent in the census that motivated the arm.** I
reported that wrong pair to myself before catching it. **An instrument whose failures and successes look
alike is worth less than no instrument, because it also reports a number.**

✅ **The discriminator is now "does it READ stdin", not "does its answer change":** stdin is a **FIFO held
open by a writer that sends nothing**, so a reader **blocks** and a non-reader runs to completion. It needs no
knowledge of any witness's input format — exactly what the byte-feeding version required and could not have.
**With a control arm**, because "it blocked" has a second explanation: the program is also run against
`/dev/null`, and one that fails to finish *there too* is slow or looping, not stdin-hungry, and is **excluded
rather than convicted**. Graded on `icont`, so a SCRIP bug can neither raise nor suppress a finding. It
refuses if it sweeps nothing.

**Fail-once proved three ways** (hide `geddump`'s, `profsum`'s or `btrees`'s sidecar → ARM 5 names it). Live:
20 swept, 0 starved, 1.5 s.

⛔ **A green ARM 5 is not proof that no starved witness exists** — only that no *obvious* one does.

## One more misreport, caught in my own new code

The summary line first read **`PASS ARM5 … 1 starved silently`** — a summary announcing PASS beside its own
failure count. **A summary is the line a reader trusts *instead of* reading the body**, so the verdict word
must follow the count next to it. Same shape as this gate's ARM-4 doubled-count scar; that is three instances
of one class in one sitting.

## Not done here

The board (`test_icon_all_rungs.sh`) is the coo's under ONE RUNNER, ONE BOARD. My verdict is the row's
DONE-WHEN (the 8 witnesses, graded by the runner's own mechanics: fresh rundir, sidecar argv/env, two-place
stdin, rc part of the answer), the gate I touched, and `make preflight` (33 arms, 0 red).
