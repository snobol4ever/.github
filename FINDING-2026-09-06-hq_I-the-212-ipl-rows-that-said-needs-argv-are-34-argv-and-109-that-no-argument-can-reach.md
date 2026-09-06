# FINDING — the 212 ipl rows that said "needs argv" are 34 argv and 109 that no argument can reach

**hq_I, 2026-09-06, FLEET-12, CEO-326** (*"the 212 ORACLE_FAIL argv sidecars are the next batch after the
stdin ones"*). Measured on SCRIP `495aeb974`+, corpus `b9f408b5e`+, oracle
`/home/resources/icon-master/bin/{icon,icont,iconx}`, RT_OPT=-O0, incremental `make`. No suite, board or
`make test` was run for this: every number below comes from `util_cut_icon_ipl_refs.sh`'s own census over
the three ipl subdirectories that ship a `procedure main`.

## THE CLAIM

`corpus/packages/icon/ipl/UNGRADED.tsv` — the file that says WHAT IS OWED — carried **212 rows whose
reason was one sentence this fleet composed**, not one the oracle ever said:

> `needs argv/stdin this driver does not supply, or genuine rejection`

Asked properly, those 212 are four different answers:

| measured class | rows | is anyone owed work? |
|---|---:|---|
| an identifier never resolved on this oracle, and the run died calling it | **109** | **no** — moved to UNGRADABLE |
| the program printed its OWN usage banner | **34** | yes — this is the argv batch CEO-326 asked for |
| already investigated individually by seat07, reason kept | 85 | yes, per row |
| everything else, now carrying the oracle's own first words | 17 | yes, per row |

⛔ **The two causes the sentence named outright were right for 34 of 212, and the largest class was
neither of them.** A compound reason cannot be falsified by any single observation — "argv OR stdin OR a
genuine rejection" is true of nearly any failing program — so it is never corrected. **It is the
untestable form of "I did not look."**

## THE ROOT CAUSE IS AN ARM ORDER, NOT A JUDGEMENT

`util_cut_icon_ipl_refs.sh` already had the right evidence and already knew what it meant. Its
`UNDECLARED_IDENTIFIER` arm — *"an identifier never resolved at link time"* — sat **below**
`if [ "$rc1" -ne 0 ]`, so it could only ever be reached by a run that had **already succeeded**. The
other half of that same evidence, 109 programs carrying the identical link diagnostic and then dying on
it (`Run-time error 106`, `offending value: &null` — a call through a name that resolved to nothing),
fell straight through to the compound reason and was filed as work owed. **No argument can supply a
missing builtin.**

⭐ **THE GENERAL FORM, and it is not about this script: a classifier gated on `rc` sees its evidence only
in the rc-branch you happened to put it in.** The evidence here is a *link-time* diagnostic and is
independent of rc, so gating it on rc silently halved its population — and the half that fell through
landed in the file that generates work. Cured by moving the arm above the rc test and carrying the real
rc in the row, so the two failure points stay told apart by the RC column rather than by which branch
saw them.

## THE ORACLE HAS NO GRAPHICS AT ALL, AND "NEEDS_DISPLAY" IS THE WRONG NAME FOR IT

Four independent measurements, none of them a remembered fact:

- `ldd /home/resources/icon-master/bin/iconx` → **libm and libc only**. No libX11.
- `strings iconx | grep -ci 'XOpenDisplay|libX11'` → **0**.
- `every write(&features)` → UNIX, ASCII, co-expressions, dynamic loading, environment variables,
  external values, keyboard functions, large integers, pipes, system function. **No graphics. No X Windows.**
- `open("test","g")` fails **with `DISPLAY=:99` set**.

⛔ **So `xvfb-run` moves ZERO of these rows.** `lib_inventory.sh` admitted `NEEDS_DISPLAY` to the
UNGRADABLE vocabulary on the rationale that *"a display is exactly that — one xvfb-run moves all 25
together"*. The disposition is right and the justification is false: there is no X client in the binary
to point at a display. The handle is a **graphics-enabled rebuild of the oracle**, which is a different
and much larger action.

⛔ **And the words in those 25 rulings are the PACKAGE's, not the oracle's.** `can't open display` is
printed by `gprocs/window.icn:183` — a `stop()` in vendored IPL source — after `open(...,"g")` fails.
The lockdown requires an UNGRADABLE row to give **the oracle's** reason; those rows quote an IPL library
string and attribute it to the oracle. Same shape this lane keeps meeting: *a correct ruling wearing a
false justification, which is worse than a wrong ruling because it survives review.*

All 134 (the 25 plus the 109) now read `ORACLE_CONTRACT_NOT_IMPLEMENTED` — a word already in hq_T's own
closed vocabulary, so nothing new was minted during the law freeze — with the four measurements in the
reason and the prior ruling kept beside it as provenance. **Routed to hq_T, whose ruling it is.**

## THREE CORRECTIONS TO MY OWN INSTRUMENTS, ALL CAUGHT BEFORE THEY REACHED A PUBLISHED NUMBER

⛔⭐ **1. `icont -s` HID 30 OF THE 102, AND `-s` IS UPSTREAM'S OWN GRADING CONTRACT.** My first census
compiled each candidate with `icont -s` — the flag this lane adopted on 2026-09-06 precisely *because*
it is what upstream's `tests/general/Test-icon` uses — and counted the undeclared-identifier warnings.
It found 72. The cutter, which runs the one-step `icon` driver with no `-s`, finds 102. Measured
side by side on `gprogs/ca21.icn`: `icont -s` prints **nothing**, `icon` prints
`"DrawPoint": undeclared identifier, procedure main`. `-s` means *suppress informative messages*, and
the informative messages **were the evidence**. ⭐ **The same flag is mandatory for one question and
disqualifying for the other: it is correct for GRADING (match upstream's contract byte for byte) and
wrong for DIAGNOSING (you are asking the compiler what it noticed).** I had adopted it as a fact about
the oracle rather than as a fact about one question, and it under-reported by 29% without a word.

⛔⭐ **2. `grep -c` PRINTED NOTHING — NOT ZERO, NOTHING — FOR A PATTERN WITH 34 MATCHES.** Several ipl
programs open with ANSI escapes (`progs/hr`, `progs/literat`, `progs/hebcalen`), so a file of their
diagnostics is *"ISO-8859 text, with escape sequences"* and grep declined to treat it as text. I read
the empty output as *no argv cases exist* and nearly published it. `grep -a` returns 34. Same family as
`command -v` and `head -1`: **the instrument quietly answered a narrower question than it was asked, and
its silence read as an absence.**

⛔⭐ **3. THE CENSUS PREDICATE COULD NOT REPORT ITS OWN FALSE NEGATIVE.** One UNGRADED row had no census
row **at all** — `progs/literat.icn`, whose entry point is at line 1054 as `    procedure main()`,
indented. The cutter selected its population with an anchored `^procedure[[:space:]]+main`, so a shipped
main program got **no named outcome**, against that script's own written contract that there is never a
silent skip. Nothing downstream could notice: `total=` counts the population the predicate already chose.
Exactly one file in the package differs today, which is the point — **a one-file gap is the kind that
survives every eyeball on a 461-file count.** Both the predicate and a gate arm comparing the two forms
landed.

## AND ONE OPERATIONAL LESSON, PAID FOR IN A LOST TEN-MINUTE RUN

⛔ **Editing a shell script while a long run of it is in flight corrupts that run.** bash reads a script
lazily, by byte offset. I inserted nine comment lines into `util_cut_icon_ipl_refs.sh` while a 275-file
census of it was executing; the offsets shifted under the interpreter and it died at
`syntax error near unexpected token '('` on a line that is perfectly valid — after producing 275 rows
that looked entirely normal. **The failure surfaces far from the edit, at the end, and the partial
output does not announce itself.** `bash -n` passes on the finished file, so nothing catches it after the
fact. Re-run, do not salvage.

## WHAT LANDED

- `util_cut_icon_ipl_refs.sh` — the arm reorder; the row's reason is now the oracle's own first
  **non-blank** line (`first_diag`, not `head -1`: icont opens its runtime diagnostics with a blank line,
  so `head -1` reports an *empty* reason for every runtime error); a `NEEDS_ARGV_FIXTURE` arm at rc!=0
  with a deliberately wider usage predicate than `SUSPECT_USAGE`'s anchored one (a failing program's
  `patchu: usage: ...` is as much a refusal as an unprefixed banner); the mains predicate.
- `test_gate_icn_ipl_reason_is_the_oracles_own_words.sh` — six arms, **four proven RED against the
  pre-cure cutter** (ARMs 1, 2, 3 and the ARM 4 control) and green after. **ARM 5 is the one worth
  copying:** it asks the oracle for `&features` on every run and **REFUSES rc=2** the moment graphics
  appears, because 134 rulings rest on its absence and nobody re-reads a closed ruling. That is
  `lib_inventory.sh`'s *"could this ruling be overturned for the whole class at once?"* made executable
  instead of remembered.
- The ipl census sidecars, rewritten per row from that census output.

## WHAT IS NOT DONE, NAMED

The 34 argv rows are **identified, not authored**. `corpus/packages/icon/ipl` has a `NAME.dat` stdin
sidecar honoured by both the cutter and `test_icon_ipl_suite.sh`, and **no argv sidecar at all** — so an
argv fixture written today would be read by nothing. That mechanism, then the fixtures
content-validated against each program's own documented behaviour, are the next two rungs of this row.
