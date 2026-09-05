# FINDING 2026-09-05 hq_P — 44 batons carry a placeholder DONE-WHEN; two of them are live seat claims that cannot be closed

**Measured:** hq_P, 2026-09-05, `/home/resources/postoffice/tasks/` + `QUEUE.tsv` (664 live rows).
Found while working `snobol4-every-xfail-fixed-as-a-faulty-test-or-cured-as-a-defect`, after two rows in
this lane turned out to be unclosable in the same sitting.

## 1. The population

`mint` writes a skeleton baton whose DONE-WHEN line is prose:

    DONE-WHEN: ⛔ MUST BE MADE RUNNABLE BEFORE done CAN EVER PASS — minted with no executable
    acceptance test; replace this line with a real command … before anyone can close this row.

**44 batons still carry that line as their DONE-WHEN**, spread across every lane:

| state | n | | owner | n |
|---|---|---|---|---|
| FREE | 23 | | hq_P | **16** |
| PARKED-LON-HOLD | 14 | | hq_B | 10 |
| CLAIMED | **3** | | hq_T | 9 |
| DONE | 2 | | hq_C | 7 |
| SUPERSEDED | 1 | | unassigned | 1 |

## 2. ⛔ The urgent part: three rows are CLAIMED right now and cannot be closed

Two are rank 1 in the hq_P lane and both seats are working today:

- `snobol4-error-5-is-a-catch-all-for-three-spitbol-outcomes` — **CLAIMED:seat07**
- `snobol4-output-third-argument-is-a-format-not-a-file-name` — **CLAIMED:seat09**

A seat can do the whole job correctly and `done` will still refuse, because `done` executes the
DONE-WHEN line whole and prose is not a command. The seat has no way to tell "my cure is wrong" from
"my criterion was never written" — both arrive as a refusal.

## 3. Why a placeholder is not a paperwork gap

`assign` runs a dispatch probe and, on a placeholder, prints:

    ⚠ DISPATCH PROBE COULD NOT MEASURE <row> -- assigning anyway, unverified:
      the DONE-WHEN is still the mint placeholder, not a command

…and **assigns anyway**. So the row reaches a seat looking exactly like a real one, and the warning is
addressed to the assigner, who is not the person who will later be unable to close it. ⭐ The signal is
emitted at the moment it cannot be acted on and is absent at the moment it matters.

23 of the 44 are FREE, so this is not a backlog of old paperwork — it is 23 traps armed for the next
seat that runs `next`.

## 4. ⭐ The census instrument itself over-reported by 2.5×, and that is the transferable part

The obvious census — `grep -l "MUST BE MADE RUNNABLE" tasks/*.task.md` — returns **112**. The true
figure is **44**. The difference is prose *mentioning* the placeholder: ledger lines, handoff notes,
and (by the time I ran it) **two ledger lines I had written myself an hour earlier in this same
sitting**, recording that I had replaced a placeholder. The instrument counted the cure as if it were
the disease.

⛔ The correct census keys on the DONE-WHEN **line**, not the file:

    for f in tasks/*.task.md; do case "$(grep -m1 '^DONE-WHEN' "$f")" in
      *"MUST BE MADE RUNNABLE"*) echo "${f%.task.md}";; esac; done

⭐ This is the same shape as `command -v` for an oracle and the `crosscheck/*.sno` glob that matched
zero files: **an instrument that answers a slightly different question than the one you meant, and
answers it in a well-formed way that carries no sign of the substitution.** Here it failed in the
inflating direction, which is the more persuasive one — a scary number invites action, not scrutiny.
I had already written the wrong command into a handoff block before checking it; it is corrected there.

## 5. Not this FINDING's cure

The mechanism is already a row — `done-when-line-is-executed-whole-so-prose-makes-a-row-unclosable`
(rank 2, unassigned, marked **DONE**) — which is itself one of the 44, i.e. that row was closed while
still carrying the placeholder it names. The remaining work is a `mint`-side refusal or a sweep that
fills the 44 in; both are ceo/hq_T harness calls, not this row's.

**Immediately actionable regardless of that:** the three CLAIMED rows need a real criterion written
before their seats finish, and their seats need to know the refusal they may hit is not their cure.
hq_P has done this for the two rows it owns today; the four HQs own the rest of their lanes.
