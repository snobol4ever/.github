# FINDING — SETEXIT's `:(CONTINUE)` resumes at the interrupted statement's OWN FAILURE EXIT, and the END trap that made setexit2 green is a CSNOBOL4 EXTENSION that SPITBOL does not have

**hq_P, 2026-09-04, QUARTET rank-1 row `setexit-not-invoked-under-errlimit-survival` (ceo assignment: challenge #3, the SETEXIT/ERRLIMIT mechanism).**
**Landed:** SCRIP `1840c6846` · corpus `7f6e847ff` · this file.
**Graded on:** incremental `make` (RULES.md:118 FACT RULE — pristine is void as a per-landing requirement), RT_OPT `-O0`.

## 1. THE MEASUREMENT THAT DECIDED EVERY OTHER LINE — TWO ORACLES, NINE FACES

Everything below was measured against **both** oracles before a line of `src/` changed: SPITBOL
`/home/resources/x64/bin/sbl -bf` (the SNOBOL4 grading oracle) and CSNOBOL4 `/home/claude/csnobol4/snobol4`.
⭐ **They AGREE on the whole mechanism and disagree on exactly two things** — the error NUMBERING, and one
extension. Separating those two axes is what made this row tractable; conflating them is what made it look
like a contradiction for three sessions.

| face | SPITBOL | CSNOBOL4 | SCRIP before | SCRIP after |
|---|---|---|---|---|
| `:(CONTINUE)`, statement has `:F(L)` | takes `L` | takes `L` | **exits** | takes `L` ✅ |
| `:(CONTINUE)`, no `:F` | next statement | next statement | **exits** | next statement ✅ |
| trap is one-shot | 2nd error takes ordinary failure exit | same | **exits** | same ✅ |
| handler re-arms itself | catches the 2nd too | same | **exits** | same ✅ |
| handler falls off its end | continues in source order | same | ✅ | ✅ |
| `:(ABORT)` | error processing resumes, terminates | same | **exits 0 silently** | terminates ✅ |
| `:(CONTINUE)` with no preceding error | ERROR **37** | ERROR **35** | **exits 0 silently** | ERROR 35 ✅ |
| error numbering (`1/0`, `CHAR(1000)`, undefined fn) | 14 · 282 · 22 | 2 · 10 · 5 | 2 · 5 · 5 | unchanged — **not this row** |
| SETEXIT trap fires on **normal termination** | **NEVER** | **fires** (`&ERRLIMIT`≠0) | fires, *even at `&ERRLIMIT`=0* | SPITBOL default ⛔ see §3 |

⛔ **The numbering column is NOT a defect I left unfixed — it is a dialect axis SCRIP has already chosen.**
`core_err_msgs[]` in `core.c` **is** the Griswold/CSNOBOL4 table, verbatim, and slot 35 already read
*"Not in a SETEXIT handler"* — the exact error this row needed to raise, sitting unused, waiting. I used the
number SCRIP's own table carries rather than importing SPITBOL's 37. A seat cross-checking `&ERRTYPE` against
the SPITBOL manual will find a mismatch on **every** error in the runtime and must not read it as this row's.

## 2. THE CURE — THE RESUME POINT IS A FRAME, AND THE ORACLE'S OWN SOURCE SAYS SO

`x64/sbl.min:29399-29416` (the SIL, quoted in the s249 cursor) saves **`stxof`** — the *failure offset* — and
`stxoc`, the interrupt offset, **before** branching to the trap. So SPITBOL's CONTINUE is not "goto the next
line": it is *resume the interrupted statement's own failure continuation*, which is why a `:F(L)` is honoured.

⭐ **SCRIP already had that continuation and was already correct about it.** The no-trap `&ERRLIMIT` arm of
`core_runtime_error` **returns**, and the statement then takes its failure exit — verified before I changed
anything (`n1.sno`: `BEFORE/FAILEXIT/AFTER`, byte-identical to both oracles). The trap arm's only defect was
that it called `rt_goto_transfer(lbl)` and then `exit(0)`, so **the correct resume path existed three lines
away and was unreachable.** The cure makes `:(CONTINUE)` reach it:

- `core_runtime_error` pushes a resume frame, enters the handler, and interprets the `longjmp` value —
  `1` = CONTINUE ⇒ **`return`**, i.e. the statement takes its failure exit (the already-correct road);
  `2` = ABORT ⇒ fall through to the terminal report, as if no intercept were set.
- `rt_goto_resolve` routes `CONTINUE`/`SCONTINUE`/`ABORT` to `sno_setexit_resume` instead of `exit(0)`.
- Outside a handler, `sno_setexit_resume` raises **35**, which is itself SETEXIT-trappable — and that is
  precisely what `csnobol4_suite/setexit7.sno` tests in its first three statements.

⛔ **NO NEW GLOBAL, and this is the one design point worth reviewing.** The resume buffer is the EXISTING
`g_core_errjmp_stk[64]`/`g_core_errjmp_n` pair, used exactly as `arithmetic.c:227-231` already uses it (push a
frame, longjmp back, pop). The one piece of genuinely new file-scope state is a single `int _setexit_resume`
holding the frame INDEX. ⭐ **It holds the index rather than "am I in a handler" on purpose:** longjmping to
`g_core_errjmp_n - 1` would be correct *today* and would silently land in an arithmetic guard the first time
one is live across a handler's goto. Nesting is handled by save/restore through a local, so an error inside a
handler that arms its own trap restores the outer frame on the way out.

## 3. ⛔⛔ THE PART THAT REVERSES A LANDED BEHAVIOUR — AND THE MEASUREMENT THAT FORCED IT

seat10's cure (row `snobol4-setexit-trap-never-invoked`, landed earlier the same day) made the SETEXIT trap
fire on **normal program termination**, which is what turned `csnobol4_suite/setexit2.sno` green. **That
firing is a CSNOBOL4 extension. SPITBOL does not have it** — measured four ways (`:(END)` transfer,
fallthrough, `&ERRLIMIT` set, `&ERRLIMIT` unset): SPITBOL fires in **none** of them.

⭐ **It is not an abstract dialect quarrel — it was the whole remaining blocker on my own rank-1 witness.**
`keyword_replace_branch_11`'s handler re-arms itself, so at program end the re-armed trap fired again and
printed a fifth line, `HANDLER S8`. **SCRIP matched CSNOBOL4 byte-for-byte, including that fifth line — and
the master's `.ref` has four.** I then cut both master refs against SPITBOL directly: **byte-identical, both
witnesses.** The SNOBOL4 master is SPITBOL-minted, it is the landing gate, and CLAUDE.md states SCRIP follows
SPITBOL for SNOBOL4. So the END trap now honours SPITBOL by default.

⛔ **THE COST, STATED PLAINLY BECAUSE IT IS A REGRESSION AND SOMEONE ELSE'S LANDING:** `csnobol4_suite/setexit2.sno`
goes from PASS to FAIL. That is **the entire cost** — censused, not assumed: of the four SETEXIT members of that
suite, `setexit3` never uses the END trap (it tests SETEXIT's return value), and `setexit4`/`setexit7` were
already red. ⭐ **seat10's work is preserved, not deleted:** the firing lives behind `SCRIP_SETEXIT_END=1`, and
under that arm `setexit2` passes and `keyword_replace_branch_11` reds — so the switch proves the divergence is
exactly one thing and nothing else moved with it.

⚠️ **THIS IS A RULING I AM ASKING FOR, NOT ONE I AM CLAIMING.** Routed to ceo. Two defensible answers exist and
the evidence for each is above: SPITBOL for the master (taken here, because the master is the sovereign gate),
or CSNOBOL4 for the vendored suite. What is NOT defensible is the state before this row, where SCRIP fired the
trap **even with `&ERRLIMIT = 0`** — which **both** oracles refuse, and which no board on the box could see.

## 4. ⛔ seat10's DONE-WHEN ENCODES A FALSE EXPECTATION — AND IT PASSED

The trap row's acceptance test asserts `TRAP-A-FIRED` from a program that sets **no `&ERRLIMIT` at all**.
`&ERRLIMIT` defaults to 0, and *both* oracles require it non-zero. So that arm demanded behaviour neither
oracle has, and its passing was the bug. It now correctly refuses. ⭐ **The shape is the lesson, not the slip:**
the DONE-WHEN was written from SCRIP's observed behaviour and CSNOBOL4's, and never re-cut against SPITBOL —
the same "measured the wrong oracle" class this file's §1 table exists to prevent. Its trigger B (the
error-survival arm) was always right and still passes. Corrected in the baton with attribution.

## 5. FOUND, NOT CHASED — THREE, ALL ROUTED, NONE CURED HERE

1. ✅ **`test_corpus_snobol4.sh` COULD NOT RUN AT ALL when I hit it — AND IT WAS ALREADY CURED BY hq_B BEFORE I
   FINISHED WRITING THIS FILE.** It called the harness with `--modes m3,m4` and no `--by-modes-column`, so the 28
   `modes=ast` entries made the harness refuse rc=2 with no board line, and the control arm every SNOBOL4 landing
   is graded on was returning a refusal instead of a verdict. **hq_B cured it in SCRIP `c9aff8472`** — which
   arrived in the `pull --rebase` I took before pushing, so my own final board ran on the sanctioned runner.
   ⛔ **I nearly published this as an open defect and it would have been false.** I graded via the harness
   directly, correctly, at the time — and the honest record is that the workaround was needed for about an hour
   and is not needed now. ⭐ **The transferable half is hq_B's, not mine, and it is sharper than the bug:** their
   cure also had to READ the second board, because grading only `SUITE_BOARD` would have printed a full plausible
   green over 1797 of 1825 entries with the other 28 graded by nobody — *the silently-narrowed population reached
   by fixing the loud one.*
2. ⛔ **`fence_bal_rtab_branch_1` crashes NON-DETERMINISTICALLY in the master** — SIGABRT, both modes, nothing to
   do with SETEXIT. **Attributed by measurement, not by argument:** I stashed my three source files, rebuilt, and
   it crashed **6 of 8** runs on the **pre-change** binary. ⭐ **Across four board runs of mine it read crash=0,
   crash=1, crash=0, crash=1 with no relevant change between them** — a flaky entry hands the next seat a red
   they cannot explain and invites them to attribute it to their own diff. ⭐ **hq_B found it independently the
   same evening and got further than I did:** 8 consecutive runs `0 0 134 134 134 134 0 0`, the abort being ZHP
   heap exhausted after storage regeneration, m3 signal 6 vs m4 signal 11 on one run (corrupted state, not one
   wrong branch), and — the useful part — **`setarch -R` makes it 10/10 deterministic**, which is the reproducer
   a cure needs for a before-control. Already routed to hq_T (ranked #5, the fuzz class). **Recorded here only as
   independent confirmation from a second seat and a second method**, not as a new find.
3. ⚠️ **The RAISE gap named at s249 is still live and now has a sharper witness.** `S + 1` with `S='abc'` raises
   nothing in SCRIP where CSNOBOL4 raises 1 and SPITBOL raises 1 — the statement just fails. So a SETEXIT
   handler cannot trap what is never raised, and `spitbol_testpgms/test1.spt`'s 29 intentional errors need
   *this*, not more resume machinery. **The resume half is now done; the raise half is the next rung** and is
   the real remaining distance to that program's 140 lines.

## 6. WATERMARKS (measured, both modes, this tree)

- **SNOBOL4 master, sanctioned runner, merged tree** (`test_corpus_snobol4.sh`, SCRIP `1840c6846` corpus `7f6e847ff`): `total=1830 · m3 xfail=54 xpass=0 · m4 xfail=54 xpass=0` · **mode-3 PASS=1799 FAIL=0** · mode-4 PASS=1798 **FAIL=0** with **CRASH=1**, that crash being `fence_bal_rtab_branch_1` alone — item 2 above, pre-existing and nondeterministic. A direct harness run minutes earlier on the same tree read `m3_fail=0 m3_crash=0 m4_fail=0 m4_crash=0`, 1776 pass each mode. **Both readings are true and the entry is why they differ.**
  Both witnesses promoted out of `ALL.xfail` in all **three** places.
- **Icon watermark:** 599/601 both modes; the 2 fails (`procedure_write_image_1`,
  `procedure_record_every_replace_2`) **proven pre-existing by stash-and-rebuild**, not asserted. Required
  because `rt_goto_resolve` and `core_runtime_error` are **shared nodes** (RULES.md § SHARED-NODE VERDICT SCOPE).
- **Promotion protocol clause 3:** both promoted entries PASS on `default`, `SCRIP_OPT=0` and `SCRIP_ZD=0` —
  the optbypass watermark does **not** move.
- **Control arms, non-vacuous:** `SCRIP_SETEXIT=0` reds all 4 resume faces; `SCRIP_SETEXIT_END=1` reds
  `keyword_replace_branch_11` alone. The new gate **refuses rc=2** if the killswitch ever stops discriminating.

⭐ **A promotion tore the master and the protocol's own 0.046 s check caught it in one command.** `ALL.ref`
carries the XFAIL banner too, and I had patched only `ALL.sno` and `ALL.xfail`; `read_suite` raised
`family.ref banner mismatch at seq 1785` immediately. Without that check I would have pushed a master that is
**unreadable for every seat on the box** — the exact failure the INTERIM PROMOTION PROTOCOL was written for,
reproduced accidentally and caught by its own cheap arm.
