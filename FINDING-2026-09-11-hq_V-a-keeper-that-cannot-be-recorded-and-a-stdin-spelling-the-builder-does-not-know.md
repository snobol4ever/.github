# FINDING 2026-09-11 (hq_V) — A KEEPER THAT CANNOT BE RECORDED, AND A STDIN SPELLING THE BUILDER DOES NOT KNOW

**Tree:** SCRIP `1493214e4` · corpus `2e98e16ad` (both origin/main at measurement) · MODE NONET, order of work ICON.
**Instruments:** `scripts/util_build_master_suite.py`, `scripts/util_unabsorbed_census.py`, `scripts/corpus_suite_harness.py`.
**Owner of the cure:** the master builder is hq_T's row this sitting (`ack-both-items-cured…`, `ruling-third-source…`); these three defects are MEASURED here and ROUTED, not landed, so two seats are not editing one file.

## ⛔ 1. A PAIRLESS KEEPER CAN NEVER BE ACCOUNTED, SO THE ICON CENSUS CANNOT REACH ZERO NO MATTER HOW CORRECT EVERY DECLARATION IS

`util_unabsorbed_census.py` accounts a source exactly two ways: it is absorbed into the master, or it is named
in `tests/<lang>/ALL.excluded.txt` with a reason. `ALL.excluded.txt` is written only by the builder, and since
CEO-545 it REFUSES any other writer. In `discover_pairs()` the file with no `.ref` and no `.expected` is dropped
by `continue  # pairless loose witnesses are not board members` — **one branch BEFORE the `_declared_in_keep()`
check that would have written its KEEPER line**. A declaration whose own stated form is *"deliberately shipped
with NO `.ref`, because a pairless witness is not a board member"* therefore produces no ledger line, ever.

**Two arms, one tree, one file changed between them (scratch copies, never the real tree):**

| arm | tree | ledger line for `rung16_seqexpr_gen_basic` | entries |
|---|---|---|---|
| A | `tests/icon` as shipped (KEEP.md declares it; no `.ref`) | **NONE** | 959 |
| B | same tree **+ one `rung16_seqexpr_gen_basic.ref`** | `KEEPER, declared in KEEP.md -- never absorbed` | 959 |

Same entry set in both arms — arm B absorbs nothing new, it only becomes RECORDABLE. **The accounting channel is
gated on the exact property the declaration says the file deliberately lacks.** This is not one file: icon reads
`OWED 54` today (benchmarks 37, demos 9, tests 8) and **46 of the 54 are pairless**, among them the two
deliberately-invalid ladder witnesses seat01 declared on 2026-09-03 and the two fixture-directory sources THIS
SEAT declared on 2026-09-10 — including, that is, my own correct declarations, invisible to the machine that
counts them the day after they were written.

⭐ **The cure belongs in the builder and is small:** run the keeper/deferral check BEFORE the pairless `continue`,
so a declared-but-pairless source is excluded WITH ITS REASON instead of being dropped silently. It composes with
hq_T's row (a live computed reason must not be destroyed by a KEEP.md echo) rather than competing with it.

## ⛔ 2. THE ALREADY-IN-THE-MASTER GUARD IS KEYED ON AN ORIGIN SPELLING — SECOND SIGHTING, AND THIS ONE WOULD HAVE SHIPPED A RED

Measured on a scratch rebuild of today's tree: `util_build_master_suite.py --lang icon --write` produces **959**
entries, one of them **`959 procedure_suspend_scan_replace_2`, origin `rung36_jcon_recogn`, xfail=1** — a second
copy of the already-green **`900 procedure_suspend_scan_replace_1`, origin `rung36_jcon_recogn__rung36_jcon_recogn`**,
whose body and ref are BYTE-IDENTICAL to the loose pair's. Two spellings of one origin walk past the guard,
exactly the shape recorded in `GOAL-HQ-VALIDATE.md` HQV-31 for `generators.icn` five days of work earlier. **The
difference is that this duplicate arrives stamped `xfail=1`, and THERE IS NO XFAIL — it counts as a FAIL on every
board.** A routine rebuild by any seat would have added a red duplicate of a green entry.

## ⛔ 3. AND THE REASON IT WOULD BE RED: THE BUILDER'S STDIN GUARD DOES NOT KNOW THE `.stdin` SPELLING THIS TREE USES

The builder's stdin guard checks four paths — `<stem>.input`, `<stem>.in`, `config/<base>.input`,
`config/<base>.in`. The harness's own finder `corpus_suite_harness.loose_stdin_companion()` checks **six**: all
three spellings in both locations, `.stdin` included, and hq_U widened it to `config/` on 2026-09-08 precisely
because `rung36_jcon_recogn` had been absorbed unfed once already. **All 8 icon stdin companions in this tree are
`config/*.stdin`** — the one spelling the builder omits. So a program whose fed ref is correct is graded against
`/dev/null`, prints nothing where its ref has 8 lines, and the auto-XFAIL-by-source-verdict path files the
resulting red as documented. **Two lists of the same thing, one of them shorter, and the short one decides whether
a witness is fed.** The cure is to call the harness's finder rather than re-spell its list; every guarantee it
carries (one-candidate-or-refuse, UTF-8-or-refuse) then applies unchanged.

⚠ **Seven more are waiting on the same trip-wire.** `btrees geddump io others prefix profsum recent` all have
`config/*.stdin` and are held loose today only by a KEEP.md or PENDING.md declaration. `recogn` fell through the
moment its deferral row (`icn-recogn-genqueen-suspend-shape`) reached DONE and the deferral EXPIRED. **Every one of
those seven becomes absorbable-unfed the day its own declaration is retired** — the defect is armed, not latent.

## ⭐ WHAT LANDED HERE INSTEAD, AND WHY IT IS NOT A WORKAROUND

`rung36_jcon_recogn.icn` is DECLARED in `tests/icon/KEEP.md` with its `.icn` suffix (HQV-30's lesson: a bare
basename matches nothing in the delimited-substring deferral contract) **with a stated exit condition**, and the
declaration is proved to bite: the same scratch rebuild that produced 959 produces **958 and no duplicate row**
with the declaration in place. Deleting the duplicate — the ordinary cure, used for 18 of them on 2026-09-10 —
would have been WRONG here: `test_gate_icn_rundir_contract.sh` discovers its witnesses by scanning `tests/icon/*.icn`
and refuses only on an EMPTY set, so the file's removal takes it 8 → 7 witnesses silently, and
`test_icon_ir_rung_36.sh`'s `run()` prints `SKIP (no .expected)` and returns success. **Two instruments that would
have gone quietly smaller, neither of them red.**

`rung36_jcon_genqueen` was ABSORBED in the same sitting (master **957 → 958**, entry `procedure_every_suspend_replace_8`)
because its own deferral expired the same way and it is genuinely input-independent: m3 PASS, m4 PASS through the
harness's `run_suite_entry`, and its `.expected` equals a fresh `icont -s` cut of BOTH the upstream
`packages/icon/jcon_tests/genqueen.icn` and the corpus copy, byte for byte. Its smoke line is now `moved`, which
ASSERTS the master carries the origin and REFUSES rc=2 otherwise, instead of the silent skip that made the deletion
of an absorbed pair invisible.

## THE LESSON, because it is not about these two files

**An accounting channel that a correct declaration cannot reach will print debt forever and blame the declarer.**
The icon census has read `owed 46+` through three sittings of honest declaration work, and every one of those
declarations was written, reviewed and correct. A number that cannot move is not a backlog; it is a broken meter,
and the first question about any stubborn count is which writes can physically reach it.
