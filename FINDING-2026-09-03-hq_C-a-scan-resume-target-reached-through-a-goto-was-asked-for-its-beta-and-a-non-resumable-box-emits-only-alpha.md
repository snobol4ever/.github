# FINDING — a SCAN resume target reached through a GOTO was asked for its β, and a non-resumable box emits only α

**Seat:** hq_C (HQ-COMPLETE) · **Date:** 2026-09-03 · **Mode:** QUARTET
**Routed to hq_C by:** hq_B, mail `icon-three-defects-from-the-jcon-demo-row` + `…-CORRECTION-witnesses-were-eaten`, on
`FINDING-2026-09-03-hq_B-jcon-is-a-demo-now-two-of-its-seventeen-modules-were-never-in-the-corpus-and-jtran-does-not-link.md`.
**Tree:** SCRIP `7cc472145` + this change · corpus `91a055302` · oracle `/home/resources/icon-master/bin/icont` · `RT_OPT=-O0`.

## THE DESIGN QUESTION hq_B ASKED, AND THE RULING

> "the natural fix is a 'resume at α' marker on the scan's resume operand, but `IR_t` carries only TWO `IR_ref_t` (γ, ω) —
> α/β are x86 labels per the FROZEN LABEL MODEL (`GOAL-JCON-IN-SCRIP.md`)."

**RULING: no new `IR_ref_t`, no new IR field, and the FROZEN LABEL MODEL does not move.** The marker hq_B reached for is
not missing — it is *derivable at the site*, and the emitter already derives it twice within fifty lines of the defect.
The bug is not an absent fact. It is **a walk that changed the meaning of its own cursor without noticing.**

`operands[2]` of an `IR_SCAN` names a box: *resume THAT box* → its **β** is right. But when the walk cannot find that box
on the emit spine it hops `bb2 = bb2->γ.node` — and **a γ edge means "proceed to that box's ENTRY", i.e. its α.** After
one hop the cursor no longer denotes "the box to resume"; it denotes "the box to enter". The code kept asking for β.

## THE MEASURED MECHANISM

Two-line witness (hq_B's; reproduced exactly):

```icon
procedure g(); "" ? { while 1 do suspend 1 }; end
procedure main(); write(g()); end
```

`--dump-ir` for `proc g` (the whole graph, so the wiring is checkable):

```
0      1    11@  LIT_STRING    [12] ""
1      2    11@  SCAN_ENTER    [0]
2      3    8@   LIT_INTEGER   [] 1          <- the `while` CONDITION
3      4@   7@   LIT_INTEGER   [] 1
4@     5    7@   SUSPEND       [3,5]
5      6@   6@   SCAN          [1,.,7@]      <- operands[2] = 7@, the resume target
7@     2    2    GOTO          []            <- pure wiring; γ -> node 2
```

`SCRIP_SCAN3_DIAG=1` prints the walk's own confession: `[SCAN3] i=4 found_k=2 -> t0=n2_lit_integer_β`.
Node 2 is a `LIT_INTEGER`. Its template emits an α entry and no β, so `n2_lit_integer_β` is allocated (the `betas[i] = emit_label_alloc("n%d_%s_β", …)` line allocates a β for **every** node, eagerly) and never defined:
m3 `bb_emit_end: 1 unresolved forward reference(s)` → abort rc=134; m4 assembles and dies at `ld`.

**Why the eager allocation hides it:** the site already carried a fallback — `betas[k] ? betas[k] : lbls[k]` — which reads
as "β if there is one, else α". There is *always* one. **A fallback whose guard can never be false is not a fallback; it is
a comment.** It had the right shape and zero effect, which is why it survived review.

## THE CURE — the file's own idiom, applied at the one site that forgot it

`src/emitter/emit.cpp`. `flat_beta_used_scan` already owned the predicate "does this node keep a β label" as an inline
clause. It is now the named function `flat_beta_kind_keeps`, and **both** callers use it:

- `flat_beta_used_scan` — unchanged behaviour, now calls the helper.
- the `IR_SCAN` `operands[2]` resume walk — `(betas[k] && flat_beta_kind_keeps(nodes[k])) ? betas[k] : lbls[k]`.

Two sibling sites in the same function already discriminate this way and were the model:
the ω resolution's `omega_is_beta ? betas[k] : lbls[k]`, and the `IR_SUSPEND` do-body's
`g_suspend_dobody_beta = (ir_is_generator_kind(…) || … ) ? betas[k] : lbls[k]`. ⛔ Both are cited by their text, not by a line
number: this file's own edit moved every line below 2677, and a `emit.cpp:<line>` citation would already be wrong. **The cure adds no concept to the emitter; it removes an exception.**

## GRADING — the whole condition axis, both modes, against icont

| `while COND do suspend 1` inside `"" ? {…}` | oracle | m3 before | m3 after | m4 after |
|---|---|---|---|---|
| `1` | `1` rc=0 | abort rc=134 | **PASS** | **PASS** |
| `"x"` | `1` rc=0 | abort rc=134 | **PASS** | **PASS** |
| `1 to 2` | `1` rc=0 | abort rc=134 | **PASS** | **PASS** |
| `f()` (generator) | `1` rc=0 | PASS | **PASS** | **PASS** |
| `&fail` | (empty) rc=0 | PASS | **PASS** | **PASS** |
| `not 1` | (empty) rc=0 | PASS | **PASS** | **PASS** |

⭐ The three that already linked are unchanged **by construction**, not by luck: the predicate returns β for exactly the
kinds whose templates define one, so no case that passed before can take a different label now.

## WHAT IT DID TO jtran — the row's actual blocker

`test_demo_icon_jcon.sh`: jtran moves from **BUILD-ERR in both modes** to **built, linked, run, rc=0** in both modes.
It is still a KNOWN-DIFF, on a **different and already-owned class**: `jtran preproc inputs/hello.icn : stdout` prints
nothing where the oracle prints 4 lines, and stderr carries

```
[GENHOST] ⛔ host=proc_ir_a_ProcDecl RESERVES NOTHING: a generator callee … is not yet registered (forward reference) or is recursive/cyclic
[GENHOST] ⛔ host=pat_flat RESERVES NOTHING: …
```

— the recursive-generator-host / per-activation-storage class, row `icon-jcon-class-genhost-recursive-generator`
(seat14). `corpus/demos/icon/jcon/jtran.knowndiff` is re-classed to name that instead, so the marker no longer
advertises a cured defect. ⛔ **Re-classing was mandatory, not tidiness:** the gate XPASS-fails a KNOWN-DIFF that starts
matching, but it says nothing about one that keeps differing *for a new reason* — a stale class name on a still-red row
is invisible to the instrument that exists to catch stale markers.

## ALSO CURED THE SAME SESSION — hq_B's defect (3), exit status

`src/runtime/by_name_dispatch.c`. `stop()` wrote its arguments to stderr and then `exit(0)`; Icon's `stop` terminates with
error status. `exit()` was absent entirely (`** Error 5 — Undefined function or operation`). Both now match icont on the
**answer and the status**, in both modes:

| witness | oracle | SCRIP m3 | SCRIP m4 |
|---|---|---|---|
| `stop("bye")` | `bye` on stderr, rc=1 | PASS | PASS |
| `stop()` | empty, rc=1 | PASS | PASS |
| `stop("a","b")` | `ab`, rc=1 | PASS | PASS |
| `stop(1)` | `1`, rc=1 | PASS | PASS |
| `exit()` | empty, rc=0 | PASS | PASS |
| `exit(0)` | empty, rc=0 | PASS | PASS |
| `exit(3)` | empty, rc=3 | PASS | PASS |

This closes the `⚠ jlink: exit status diverges (oracle=1 m3=0 m4=0)` line the JCON demo gate prints — a divergence that
gate deliberately **reports rather than gates**, and which would otherwise have sat behind a byte-for-byte matching stdout.

⭐ **`builtin_ids.h` is generated by a ONE-WAY transform and cannot be regenerated.** `gen_builtin_ids.py` finds its work
by scanning `try_call_builtin_by_name` for `!strcmp(fn, "NAME")` sites — sites the same script already rewrote into
`(_bid == BID_NAME)`. Re-running it today exits `ERROR: no !strcmp(fn,"...") sites found`. So `BID_exit` was added by
hand — **and the hand-edit was checked against the generator before it was trusted:** re-emitting the committed header
from its own table with the generator's own hash and layout does **not** reproduce it. `__pas_round 177` and
`__pas_halt 178` sit out of sorted order at the end, so two Pascal builtins were already appended by hand before this
seat arrived. `BID_exit 179` follows that established practice (next free id, correct probe slot, slot verified empty at
probe 0) rather than a full renumber, which would have been a 322-line diff to change one thing.

## THE INSTRUMENT LESSONS

⛔ **`command -v`'s cousin: `$?` after a pipe.** Grading these witnesses with `… | head -5` and reading `$?` reported
`rc=0` for the oracle on `stop("bye")` — `head`'s status, not `iconx`'s. The real answer is rc=1, which is the entire
defect. CLAUDE.md names this trap; this seat walked into it inside the first five minutes and caught it only because
rc=0 disagreed with hq_B's report. **A pipeline silently answers a narrower question than the one asked, and never says so.**

⛔ **A background gate started before an edit grades a binary that changed underneath it.** The row's DONE-WHEN was
launched, then `make` relinked `scrip` mid-run; it exited 0 and that 0 certifies nothing (REBASE-BASELINE COROLLARY,
applied to a build rather than a rebase). It was re-run on the final tree; only the re-run is quoted.

⛔ **THE ICON MASTER BOARD IS ALREADY RED ON ORIGIN, BEFORE ANY CHANGE IN THIS SESSION.** Measured on a clean
`7cc472145` build, no local diff: `m3 PASS=378 FAIL=2` and `m4 PASS=378 FAIL=2` of 381 run-graded, against a pinned
watermark of **379** — `⛔ ICON MASTER BOARD RED`, rc=1, on both arms. ast-graded 153/153. This is **not** attributable to
this session's cures; it is the state of `origin/main`. It is reported here rather than fixed because naming the two
entries is itself blocked: `board_icon_master.sh` runs the harness with `--by-modes-column`, which prints only the two
`SUITE_BOARD` summary lines and **no per-entry FAIL rows**, and the harness has no verbose flag in that mode. ⭐ **A board
that can say "two of these regressed" but not "which two" cannot hand a cure to anybody.**

⛔ **BOTH HALVES OF THAT ARE ALREADY A ROW, AND IT IS UNCLAIMED:**
`icon-master-board-is-two-below-watermark-and-the-board-never-names-the-failures`, rank 1, **FREE** in `QUEUE.tsv`.
hq_B minted it — this seat reached the identical two conclusions independently, from a different lane, without knowing
the row existed. ⭐ That agreement is worth more than either report alone (it is hq_T's neighbour-checks argument from
the same day: neighbours are useful because they fail *differently*), but the operational fact is the one that matters:
**a rank-1 row that two HQs have now separately confirmed is sitting FREE, so nobody is on it.** Under QUARTET the Icon
lane is hq_B's; this seat leaves the row where it is rather than claiming across lanes, and says so out loud so it is
not mistaken for coverage.

⚠️ **AND MY NUMBER DISAGREES WITH THE BOARD'S OWN ROW, WHICH IS ITSELF THE THIRD DIFFERENT READING.** `SCORE.md`
carries **377/381** both modes (SCRIP `e751405f`, hq_B, 21:52) and notes the pinned floor moved 377→379 mid-session on
yet another tree. This seat measures **378/381** both modes on `7cc472145`, twice, on two byte-identical arms. Three
readings — 377, 378, 379 — across three trees. **None of them is wrong; they are simply three different objects**, and
that is exactly why the row's second half (name the failures) is the load-bearing one: a per-entry list reconciles
three denominators in one reading, and three more summary numbers never will.

## RECEIPT — re-proven on the PUSHED tree, because the first proof was voided by a rebase

The gate was first proven on `7cc472145`; the push rebased onto three commits that had landed meanwhile
(`9bd2e1950`, `ca96ba948`, `8412955e6` — bus and leaderboard work, **zero `src/` files**, but `Makefile` grew and
`make test` grew two arms with it). ⛔ **A gate proven before a rebase is not a gate** (RULES.md § re-prove your gate
after a rebase), so every number below is from a rebuild and re-run on the merged, pushed tree.

**SCRIP `f4d69ac83` · corpus `96a459b9f` · `RT_OPT=-O0` · incremental build (HQ-27 loosened, Lon 2026-09-03 15:58).**

| arm | result |
|---|---|
| `make test` blocking set + ladder + trace gate + smoke + strip_comments (the row's whole DONE-WHEN) | **rc=0** |
| SNOBOL4 master `test_corpus_snobol4.sh` | m3 **PASS=1689 FAIL=0** · m4 **PASS=1689 FAIL=0 SKIP=0 MISSING=0** ✅ |
| Icon smoke `test_smoke_icon.sh` | m3 **14/14** · m4 **14/14** |
| Icon master `board_icon_master.sh` | run-graded **378/381 · 378/381**, ast **153/153** — RED vs floor 379, **identical before and after this change** |
| JCON demo gate `test_demo_icon_jcon.sh` | **PASS(0)**; jtran built/linked/ran in both modes; **the `⚠ jlink: exit status diverges` line is GONE** |
| Prolog ladder `--to 8` · port-trace gate `--to 8` · quad gate | 50/50 · PASS · PASS |
| `strip_comments.py --check` | 0 files |

⭐ **The SNOBOL4 denominator moved under the routing message.** hq_B's control arm read `PASS=1679`; the same script on
the merged tree prints **1689**. Neither seat mistyped — the suite grew between the two runs. This is CLAUDE.md's
"never quote a number you did not produce" with the emphasis on *when*: a denominator has a timestamp as surely as a
numerator, and a control arm quoted from an hour ago is a different control arm. `SCORE.md`'s snobol4 and icon rows
are rewritten in place from these runs (FACT RULE, Lon 2026-09-03 ~16:05).

⛔ **A caught near-miss, recorded because it would have shipped a false green.** The first full DONE-WHEN run reported
`rc=0` and it was **not** green: the command was `( … ) > log 2>&1; echo "rc=$?"`, so the reported status was the
`echo`'s. The real chain had exited **1** at `strip_comments --check` — this seat's own new `/*---*/` separator was 202
characters where the sanctioned one is 200, and the checker normalises it. Caught only by reading the log instead of
the status. ⭐ Same family as the pipeline trap above and as `command -v`: **the instrument answered a narrower question
than the one asked, and said nothing.** The re-run puts the rc *inside* the log, where it cannot be intercepted.

⭐ **The SCORE.md write hit a real concurrent-edit conflict, and it was MERGED, not forced.** Between this seat's
`util_score_row.py write` and its push, another session rewrote both the snobol4 and icon rows. Resolution: **their**
snobol4 row was kept whole — it carries the identical `PASS=1689 FAIL=0` board plus a genuinely newer entries column
(`1736`, the +10 rungs-0-9 ladder), so this seat's confirming run adds no number and taking mine would have deleted
theirs — and **this seat's** icon row was kept, because 378 on `f4d69ac83` supersedes 377 on `ca96ba948`'s ancestor.
⛔ `--force` was never a candidate. On a leaderboard whose whole value is that every row names a real run, "my arm won
the race" is not a reason to drop someone else's measurement.


⛔ **AND THE SECTION ABOVE WAS ITSELF NEARLY LOST TO A ONE-WORD MISTAKE — recorded because it is the same shape as
everything else in this file.** The receipt was appended with `F=… && cat >> "$F"` from a shell whose cwd was
`SCRIP/`, not `.github/`. `cat >>` on a name that does not exist there does not complain: it **creates** the file.
So the append reported success, `wc -l` printed a plausible 32, the FINDING was committed and pushed **without its
own control arms**, and the only reason it surfaced is that `handoff_status.sh` flagged one untracked file in the
wrong repo. ⭐ A redirect that creates on miss is `command -v` again in a third costume: **it answered "can I write
here" when the question was "is this the file I mean", and nothing in its output distinguishes the two.**

## ⛔ CORRECTION — THE "NO PER-ENTRY FAIL ROWS" CLAIM ABOVE IS WRONG ABOUT THE CAUSE

Everything this file says about the Icon board's *symptom* holds: `board_icon_master.sh` prints two summary lines and
no failing entry names. **The stated cause is wrong.** This file says "the harness has no verbose flag in that mode."
hq_T corrected it with a measurement, and this seat then re-measured it independently on the Icon suite:

```
harness --by-modes-column, stdout only (2>/dev/null):   0 per-entry FAIL rows
harness --by-modes-column, stderr only (2>&1 1>/dev/null): 4 per-entry FAIL rows
```

**The harness has been printing the names all along, on stderr, and the board captures its run with `2>/dev/null`.**
The information was produced and discarded four inches from where it was wanted.

⭐ **THE NAMES, MEASURED HERE ON `f4d69ac83` / `96a459b9f` — the thing the row has been asking for all day:**

```
FAIL m3 procedure_every_elemgen_replace_4: output mismatch
FAIL m4 procedure_every_elemgen_replace_4: output mismatch
FAIL m3 procedure_every_scan_replace_5:    output mismatch
FAIL m4 procedure_every_scan_replace_5:    output mismatch
```

Two entries, both modes — which is exactly the `FAIL=2` in each summary line. **Not from this session's cures:** the
board read `PASS=378 FAIL=2 CRASH=0` identically on a clean `7cc472145` before any local change, and the scan-resume
defect this file cures aborted the compiler (a CRASH, and `CRASH=0` on both arms), so it cannot be either of these.

⭐ **WHY NEITHER SEAT COULD HAVE GOT THERE ALONE, which is the part worth keeping.** This seat inferred the *harness's*
capability from the *board's* output — a reasonable inference, and wrong: **a board is not a transparent window onto
its harness, it is a filter, and this one filtered on a STREAM rather than on content.** hq_T had run the same harness
directly on Raku an hour earlier and seen the FAIL lines, so they knew the capability existed before ever reading the
board. Two seats, two half-views, one correct answer that neither half contained. The general form, and it generalises
past this tool: **when something appears to lack a capability, check whether a wrapper is discarding it before
concluding it cannot do it — and `2>/dev/null` inside a capture is the likeliest place for that to be true.**

This is the same family as `command -v` answering "is it on PATH" when asked "does it exist", and as the `$?`-after-a-
pipe and `cat >>`-creates-on-miss traps recorded above: **an instrument answered a narrower question than the one
asked, and nothing in its output said so.** Four instances in one session, three of them caught only by a disagreement
with someone else's number.

## POSTSCRIPT — a fifth instance of the same family, found on the way out

Closing the rung-6 row's computed `done` refused, on an arm the ceo had already seen refuse and not chased:
`GATE FAIL(1) [test_gate_pl_port_trace]: 2 failed checks`. Chased here. The cause is unrelated to this file's cures
and is worth recording because it is the same shape one more time.

`ladder__rung03_disjunction` read `trace m3=FAIL(total 25 != ref 26)`, m4 identical, **with `answer=ok`**. hq_P's
rung-11 last-call optimisation had landed; they re-cut the port-trace ref for the rung-11 witness that motivated it
(`corpus 54d5b5cf4`) and not for the earlier rungs LCO also changes. ⭐ **An optimisation that removes a FRAME changes
the trace of every earlier witness with a last call, not only the witness that motivated it** — trace refs are a
cross-rung artifact and LCO is a cross-rung change.

The removed line, from the full diff:

```
-  (2) Exit: call_proc_staged p/0   -> main/0_ret0
   (…) Exit: call_proc_staged main/0 -> pat_flat_γ
```

The witness is `main :- p.` with `p` as main's only goal — textbook last call. Under LCO main's frame is released
before `p` is entered, so `p` never returns into main and `p`'s exit *is* the exit. **One frame, one Exit port: not a
lost port, a box that no longer exists.** Re-cut with `--only 3 --cut` (whose merge semantics keep every other block)
rather than hand-edited, and the ref moved 26→25 lines.

⛔ **"Re-cut the ref until the gate passes" is the false-green trap, so the re-cut carries its argument:** the answer
is unchanged and still matches live `swipl` (not a pinned string); the single removed port is exactly the elided
frame; all **78** blocks were diffed and only rung 3's two changed; fail-once and pass-once both observed (`--to 9`
red 2-of-56 before, `PASS(0)` 56/56 after, ladder 56/56).

⚠️ **One thing was NOT swept under the re-cut.** The two modes now disagree on that final Exit's box id — m3 reports
it from box `(2)`, m4 from box `(1)`; before the landing both were `(1)`. Totals and answers agree, so `MODES MAY
DIVERGE` sanctions it and it was cut as-is; but a re-cut *pins* whatever it records, so it went to hq_P as an explicit
question rather than into the ref silently. **A ref is not a place to park an uncertainty.**

⭐ **And the family closes at five.** `command -v` answering *is it on PATH* for *does it exist*; `$?` after a pipe
answering *how did the pager exit*; `cat >>` answering *can I write here* for *is this the file I mean*; `2>/dev/null`
in a board's capture answering *what did stdout say* for *what did the harness report*; and a green summary line
answering *did the answers match* for *did anything change*. **Every one produced a confident, plausible, wrong
answer, and not one of them said it had been asked something narrower.** Four of the five were caught only because a
number disagreed with somebody else's.
