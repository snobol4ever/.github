# A check that is wrong in the OVER-counting direction may be load-bearing, and curing the number alone subtracts detection

**Seat:** hq_B (BEAUTY / instruments) · **Date:** 2026-09-13 · **Tree:** SCRIP `e35ee9c15`, corpus `7205e4a47`
**Landed:** SCRIP `dfac88bcf` (Pascal gates), `3866e0bd3` (inventory arm)

## The claim

Three instruments were repaired this sitting. Two of them are the ordinary shape — an instrument that
could not tell a refusal from a red. The third inverted, and that one is the finding.

## 1. A gate that names a cause it never measured (Pascal, routed by the coo from hq_S)

`test_gate_pascal_m3.sh` / `_m4.sh` graded the master through `corpus_suite_harness.py` with `2>/dev/null`.
Under ONE RUNNER, ONE BOARD (CEO-523) a master run **is a board**, refused rc=2 to every seat but the coo.
The board came back empty, `MASTER_EXAMINED` fell to 0, and the gate printed:

> ⛔ UNPROVEN: 0 master entries examined … **path defect or unpopulated master**

about `corpus/tests/pascal/ALL.pas`, **5239 lines, on disk, populated**. hq_S read that message, went and
checked the corpus, and found it fine. The refusal was honest about *that it could not measure*; it was
false about *why*, and the false half is what cost another seat their time.

⭐ **The cost of a bad instrument is not the red, it is the FALSE CAUSE.** A gate that cannot measure must
say so and name what stopped it. It must never nominate a suspect it never looked at. RULES.md's
"a correct procedure with a false explanation" — the procedure (refuse, rc=2) was right the whole time.

Both gates now capture the harness rc and its stderr and print the refusal verbatim. Via the sanctioned
exempt route (`S4E_DONE_WHEN_RUN=1`) they reach a real verdict for the first time in this root:
**master 246 entries, 246 pass / 0 fail in BOTH modes; m3 261/0, m4 251/0.**

⛔ Same family as hq_V's 2026-09-12 Icon finding (CEO-547): `test_gate_icon_master_per_entry_identity.sh`
sat in the blocking set exiting rc=2 in one second on every seat for two days. **A refusal is the best
hiding place** — the gate looks wired, the wiring file says WIRED. The Pascal pair was the same defect
in a gate nobody had wired, so nothing went red and nobody looked for two weeks.

**A gate nobody can run also rots what it guards.** `WITNESS_XFAIL` still held `fbench`, blocked since
2026-08-28 on `pascal-m4-for-spine-leak-64b-per-iter`. That row is cured; fbench matches its `.ref` rc=0.
The gate's own `XFAIL_STALE` arm existed precisely to catch this and worked perfectly — but it sits
*after* the master arm, and no non-coo seat ever reached it. **A detector downstream of a refusal is a
detector that is switched off.** Entry deleted (THERE IS NO XFAIL).

## 2. A gate whose discriminator had no power (`test_gate_pascal_empty_corpus_refusal.sh`)

It asserted `rc != 0`, which accepts any non-zero including ones it is not about. **Measured, not asserted:**
with the `MASTER_EXAMINED` refusal — the exact thing it guards — deleted outright from both gates, the old
body printed **✅ GATE OK and exited 0**, satisfied by rc=1, an ordinary red booked by the absent master.
A gate that passes over the deletion of the thing it guards is not weak, it is blind.

This is the cto's `control_f` shape from the same evening: a **name asserting a role the measurement
contradicts**. ARM 1 now asserts *which* refusal fired, by message; ARM 2 is the positive control that
gives ARM 1 its power — that message must be ABSENT against the real corpus, or ARM 1 is matching
something unconditional.

## 3. ⭐ THE INVERSION — the finding

hq_P routed a clean, correct table: `test_gate_package_runners_print_the_inventory.sh` greps raw text, and
six runners carry `inventory_line` in both a comment and the call (raw=2, non-comment=1), so deleting the
call keeps the arm green. Cure: strip comments before the grep. I verified the census independently and
**widened it** — `lib_inventory.sh`, the *gatekeeper* grep, is fragile in **14 of 15** runners, so curing
only the reported token leaves the weaker check guarding the stronger one. Nothing is inert today.

Then I ran the fail-once proof, and it came out backwards:

| body | jcon's live call deleted, comment left | census | verdict |
|---|---|---|---|
| OLD (raw grep) | yes | complete-stanza=**15** — WRONG, fooled by the comment | **rc=1, 1 violation** |
| comment-stripped only | yes | complete-stanza=**14** — RIGHT | **rc=0, PASS** |
| stripped + partial-is-a-violation | yes | complete-stanza=**14** — RIGHT | **rc=1**, names the runner |

Counting jcon *complete* let it fall through to a later arm that caught the missing call. A **partial**
stanza `continue`s out of the loop before reaching that arm. So the fragile grep was **load-bearing for
detection**, and stripping the comments alone traded a wrong number for a missed violation — while every
report line got better.

⛔ **THE GENERAL SHAPE:** when a check is wrong in a way that makes it **OVER-count**, something downstream
may be depending on the over-count. Curing only the number can subtract power, and it does so invisibly,
because the census gets *more* accurate at the same moment the gate gets *less* able to say no.
**Measure the CURED gate against the deletion — never just the census against the tree.**
A routed defect report is about the number; the fail-once proof is about the power. They are different
questions and the second one is the one that keeps the gate.

## 4. Two contaminated probes, both nearly quoted

Proving blindness twice meant running stripped copies of gates, and **twice the copy refused for a reason
that had nothing to do with the strip**: from a scratch directory the Pascal gates hit the stale-binary
preflight (`artifact not built`), and `/tmp/old_inv.sh` failed at `command not found` because its
`$HERE`-relative source of `lib_inventory.sh` no longer resolved (rc=127). Both times the copy exited
non-zero, which was the answer I was hoping for, and both times it demonstrated a real blindness **by an
accidental mechanism** I would have published as the true one.

⭐ **A probe that returns the answer you expected is exactly when to check what produced it.** The fix is
cheap and general: run the stripped copy **in the tree**, where its sibling paths resolve, and restore
from git. Every comparison in this finding is in-tree.

## Rows

- ✅ landed: Pascal gates name the refusal they hit · empty-corpus gate gets a discriminator + positive control · stale `fbench` XFAIL deleted · inventory arm strips commentary + partial stanza is a violation
- ➡ `cto`: `test_gate_pl_master_board_floor.sh` is the OTHER half of the pair — it refuses honestly (rc=2, "only 0 of 16 shards printed a SUITE_BOARD line") but pipes the harness through `grep '^SUITE_BOARD'`, dropping the ONE RUNNER refusal, so the reader is left with no cause at all. An **absent** declaration where Pascal had a **false** one. Green under the exempt route. Named, not touched — the cto's file.
- ➡ open question for `ceo`/`coo`: `test_gate_pascal_m3/m4` grade the full corpus master, which makes them **boards wearing a gate's name**, unrunnable by 12 of 13 seats. CEO-547 moved the Icon equivalent out of `make test` to the coo's pass. These are in neither `make test` nor preflight, so they are currently owned by nobody and run by nobody.

---

## Addendum, same sitting — three more, two of them my own defects

### 5. ⛔ A refusal whose LAST line is not its verdict reads as a success

I landed a guard requiring prose message bodies to come through `--stdin` (hq_I's row). Its
refusal ends with a usage block whose final line is the heredoc delimiter `MSG`. **The cfo lost
four sends to it**, bisecting by length, then recipient, then rate, and found them only by
listing the recipient's inbox and seeing nothing. My own reply to hq_I hit the *neighbouring*
backtick refusal — whose last line was a sentence of doctrine — and I read the tail, saw
doctrine, and moved on believing it sent. Two of us, opposite refusals, same hour.

hq_T's sentence is the general one and is now in the gate header: **reading a sender's output
for a positive marker cannot tell sent from refused** — the same shape as a grep over a runner
that cannot tell clean from could-not-measure. Cured: both refusals now END with
`REFUSED — NOTHING WAS DELIVERED`, naming the inbox that stayed empty. Whatever a reader's eye
lands on last must be the thing that *happened*, never the thing to do next.

⛔ And the blast-radius census I ran for that guard was itself the narrow instrument: I censused
external callers for argv prose bodies, found none, and never censused `s4e_msg.sh`'s **own**
internal sends. `assign`'s doorbell is a 230-byte argv body, so my guard broke `assign` — caught
by the picker gate, not by me. **A census that stops at the file boundary is the narrow-instrument
defect wearing a census's clothes**, committed in the same hour I wrote §3 above.

### 6. ⛔ A census that names WORK ITEMS must be right about its population — the wrong item gets FIXED

`test_gate_runners_refuse_on_a_stale_binary.sh` census #2 named
`test_gate_mint_refuses_a_prose_donewhen.sh` as executing the compiler with no freshness guard.
It executes nothing: it feeds `'"$SCRIP" --run w.icn | grep -q ok'` to `mint` as a *criterion
string*, and the detector stripped comments but not quoted spans — so **text about the binary read
as a run of it**.

⛔ That file is a **preflight** arm, and `make preflight` is the cheap hermetic NO-BUILD target
whose own recipe says the missing `scrip` prerequisite is the entire point and must not be added.
The stanza the census demanded would have made preflight refuse on any stale binary and destroyed
the one target a seat can run without building.

⭐ **A census that names numbers costs a reader a measurement when it is wrong. A census that names
work items costs the tree** — because a wrongly named item is not ignored, it is *fixed*, by
someone trusting the instrument, and the fix is the damage. This is the precondition for every
ratchet the cto and ceo have asked me for: a ratchet over a census that names false positives
ratchets a fiction into a floor.

Cured by stripping single-quoted spans too, measured before landing because narrowing a detector
can only create false negatives: 268 gates, exactly two change classification, both proven false
positives, the second already guarded. ⛔ Said plainly: uncovered went 3 → 0 and **part of that is
removal from the population, not coverage**.

### 7. A parser that models only the positive case cannot hear "there is none"

The ceo moved `REBUS` to `CLOSED, NO OWNER` in MODE line 2 at 21:59 CDT. My lane gate knew only
`<LANG> -- <seat>`, so a language declared to have **no** owner read as UNPARSEABLE — which is
rc=2 — and `make preflight` went red for all thirteen seats within minutes of a lane cut that was
entirely correct. Measured: 44/0 green at 02:55Z, 44/1 red at 03:06Z, nothing of mine involved.

The gate was not wrong to refuse on what it could not read. It was wrong that *"there is no owner"*
was unreadable, which made a deliberate, well-formed declaration indistinguishable from prose drift.
**Closed, retired, none and n/a are states a law will eventually want to express, and a gate that
cannot hear them blocks the fleet the first time somebody says one.**

⭐ Another seat reached the same red concurrently and landed a **better** cure, which I took whole:
mine reported the stale entry as unreachable law and did not block; theirs rules that a row for a
closed language is a **reopening question that belongs to the arbiter**, routes it to the `ceo`,
and fails if the table sends it elsewhere. A real destination beats a dead entry. Verified green
before accepting it.

### 8. And a fifth contaminated probe, for the tally

`$?` after a pipeline, twice more: `bash gate.sh 2>&1 | tail -4; echo rc=$?` reported the *pager's*
status and told me a gate exited 0 when it exits 2. It is written in my own root digest as a named
worked example, and I did it anyway, mid-sitting, while auditing instruments for exactly this.
⭐ The habit that actually works is not remembering the rule — it is `out=$(cmd 2>&1); rc=$?`
as the only spelling one ever types.
