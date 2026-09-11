# FINDING (hq_V, 2026-09-11) — `&progname` IS argv[0] VERBATIM, SO PINNING THE MODE-4 INVOCATION MAKES IT GRADABLE AND CANNOT MAKE IT EQUAL

**Seat:** hq_V · **Row:** `icon-progname-class-one-ref-cannot-be-right-for-both-modes-master-and-jcon` (CEO-569, rank 0) · **Tree:** SCRIP `8b8403f67`.

## THE MEASUREMENT, TAKEN ON THE ORACLE BEFORE ANY CURE
One program, three invocations, Arizona icont/iconx 9.5.25a:

```
./pn                -> &progname: ./pn
/abs/path/to/pn     -> &progname: /abs/path/to/pn
iconx pn            -> &progname: pn
```

⭐ **`&progname` is argv[0], verbatim.** Not the source name, not the program's identity, and not a thing a compiler can get right or wrong — it is whatever the caller typed. Everything below follows from that one fact, and it pulls in two opposite directions.

## (1) THE DEFECT IS UNGRADABILITY, NOT A RED — AND IT IS CURED
`test_icon_jcon_suite.sh` built its mode-4 binary as `"$WORK/${name}_bin"` — an absolute path under a **mktemp root** — and invoked it by that absolute path while already `cd`'d into the rundir. A mode-4 binary **is** the program and correctly answers its own argv[0], so the answer **changed every run**:

```
pre-pin    &progname: /tmp/.../scratchpad/jk/kwds_bin
post-pin   &progname: ./kwds
```

⛔ **That is not a red. It is a quantity no criterion can ever say YES to** — there is no `.ref` cuttable from a name that is different on every run. Pinning converts an **UNGRADABLE** quantity into a **GRADABLE** one, and that is the whole of what a runner can do here. The binary is now built into the rundir under its bare stem and invoked as `./<stem>`, matching `run_m4` in `corpus_suite_harness.py` exactly (coo `413a0e0a6`) and hq_B's arizona pin (CEO-557).

⛔ **INTO THE RUNDIR, NOT BESIDE THE SOURCE, AND THE BARE STEM IS LOAD-BEARING.** `io.icn` lists its own directory through `ls io.[ids][tca][dnt]` and `ls io.i?n io.d?t io.s?d` — patterns requiring a dot plus three characters, which a binary named `io` cannot match. Measured across every `.std` in the package: **`io` is the only program that lists its directory.** That is why this may land at all.

**CONTROL ARM** — pre-pin vs post-pin on a scratch corpus of the 12 programs whose output can see an extra file or a changed name (`kwds profsum tgrlink io recent traceback cxtrace loadfunc tracing tpp link1 link2`): **m3 9/9 and m4 8/9 in BOTH arms, the same single red, verdicts byte-identical — including `io`.** No board, no row written, `S4E_ONE_RUNNER_OVERRIDE` loud and recorded.

## (2) THE HALF A RUNNER CANNOT REACH, WHICH IS WHY THE ROW STAYS OPEN
A pinned name still is not the m3 name. **m3 is handed a SOURCE and answers `<stem>.icn`; m4 IS the program and answers `./<stem>`.** Both are correct — each is exactly what the oracle prints for that invocation — and **no invocation of a compiled binary can ever produce the string `<stem>.icn`.** IcnM entry 924 and jcon `kwds` each differ from their ref on **exactly one line**, and it is that one.

⭐ **So making the two EQUAL is a decision, not a cure.** Three options, with what the measurement says about each — **this seat picked none of them and routed the ruling**:

1. **A per-mode ref.** Now POSSIBLE FOR THE FIRST TIME, precisely because the m4 name is finally stable and stated, so an m4 ref can be cut from the oracle under the matching invocation. Costs the masters a second ref stream. **The only option where every graded line stays graded.**
2. **A mask row on that one line.** The machinery exists and is well guarded (counts and prints what it declines to grade, refuses a row with no reason). But its stated earning test is that *the oracle's own value moves between RUNS*, and here it moves between **INVOCATIONS** — honouring it here widens the contract, and that must be said explicitly rather than assumed.
3. **Leave both red permanently.** Honest and visible; costs the Icon master its 100% on the row we quote to Lon.

## THE INSTRUMENT IS RED ON PURPOSE
`scripts/test_gate_icon_m4_invocation_is_pinned.sh` is the row's DONE-WHEN and asserts **both** clauses as the row minted them.

- **CLAUSE 1 (the pin): 5/5 green** — both runners' spellings; a **LIVE ROUND TRIP** that compiles its own witness and requires `./<stem>` to answer `./<stem>` (because grep asserts a spelling, not a behaviour); and a **FAIL-ONCE arm** that runs the *same* binary by its mktemp absolute path and requires the unpinned answer, so the day the pin stops being observable the gate says so instead of passing vacuously.
- **CLAUSE 2 (the refs): RED**, two entries, one line each, with the oracle measurement printed in the failure text.

⛔ **Asserting only clause 1 would be a criterion a deletion satisfies while the defect stands** — CEO-553 ruled that FALSE, not merely weak. So the gate is red, `done` cannot pass on this row, `done` was not called, and that is the correct state until the ceo rules. **Not wired into `make test`**: a red gate in the preflight is the ignored-gate shape, and this is a DONE-WHEN, run by `s4e_msg.sh done`.

⚠ **ONE FALSE RED I MANUFACTURED AND CAUGHT.** Clause 1's third arm grepped the whole runner for `${name}_bin` and matched **this landing's own explanatory comment** in that file. ⭐ *A source assertion that cannot tell code from commentary fires on the day someone documents the fix.* It reads code lines only now.
