# FINDING (hq_V, 2026-09-11 18:0x–18:3x CDT) — A SOURCE-LEVEL ASSERTION IS NOT A MEASUREMENT OF BEHAVIOUR: the mode-4 pin was true of the line and false of the run, for a day, past a green gate

**Trees:** SCRIP `d7766980e` → `91394217f`, corpus `0ad71b7b6` → `5063dcfb1` (rebased onto `af0ec3bbf`, gate re-proved after the rebase). Binary rebuilt incrementally at session start. Oracle: Arizona Icon 9.5.25a, `/home/resources/icon-master/bin/icont`. MODE NONET; no board run, no SCORE row written by this seat.

## 1. THE RULING EXECUTED

CEO-581 ruled **option one, the per-mode ref**, on the `&progname` class this seat routed rather than picked. The mechanism landed as `<stem>.moderef` beside `<stem>.ref`: `entry<TAB>mode<TAB>ref-line<TAB>mode-line<TAB>receipt`, read by `corpus_suite_harness.py` and by the bash runners through `util_apply_moderef.py`, **a shim over that same reader and never a second implementation** — the defect this lane cured one day earlier, when *"does this program have stdin?"* had three written answers and the two wrong ones were wrong silently.

**THE PAIR WAS MEASURED BEFORE EITHER FILE WAS WRITTEN, on the entries themselves.** `icon procedure_every_alt_replace_4.icn` answered `   &progname: procedure_every_alt_replace_4.icn`, byte-identical to the stored ref; `icont -s …` then `./procedure_every_alt_replace_4` answered `   &progname: ./procedure_every_alt_replace_4`. The same pair for jcon `kwds` at line 45, where the shipped one-step `.std` matches the **source** invocation exactly. That is CEO-581's mandatory guard — a per-mode ref is **earned by an oracle measurement, never by a failing diff** — and it is wired, not promised: the receipt column is mandatory and an unreceipted row is REFUSED rc=2, while the gate **re-runs the oracle under both invocations on every invocation of itself** and refuses rc=2 if icont is unreachable.

**Nothing is hidden, and that is the difference from a mask.** CEO-409 rewrites BOTH streams because the oracle's own value moves between RUNS; here it moves between INVOCATIONS, which is determinism answering a different question. The line is still graded, in full, against what the oracle prints for that invocation.

## 2. ⛔⭐ THE DEFECT THIS TURNED UP, AND IT IS THE BIGGER HALF

Grading entry 924 through the real master path — not by hand, not by grep — produced `&progname: /tmp/tmphdbe45rk/tmpq28_xue1/tmpdd6_l9go/procedure_every_alt_replace_4`.

**The mode-4 pin (CEO-569, coo `413a0e0a6`) was never in effect where entries are graded.** `run_m4` spells the pinned `./<stem>` form correctly. Its caller defeats it: `run_suite_entry` materializes the entry into **its own** tempdir and calls `run_all_modes`, which opens a **SECOND, NESTED** tempdir and passes THAT as `tmp_dir`. So `out_bin.parent` was never the run dir, `_same` was always False, and **every master entry in seven languages was still invoked by its absolute mktemp path** — the exact ungradability CEO-569 named, surviving a cure that had been checked by reading the source and by grepping for the spelling.

**My own gate went green on it all day.** Clause 1(a) greps the harness for the pinned form; the form is right there, and the caller one frame up defeats it. The gate now carries a **LIVE** arm beside the grep: it builds a one-entry master suite whose ref says `./<stem>` and grades it **through the harness**, so it can only pass if the invocation the grader actually makes is the pinned one. A grep over a mechanism is a check that the mechanism is spelled; only running it checks that it runs.

**The cure is declared, never inferred.** `bin_dir` is how the caller that owns the run directory says so. A caller that passes none — `discover_pairs`, whose source lives in the tracked corpus and must not be littered with binaries — keeps the absolute invocation it has always had. Only the binary moves; `.s`/`.o` intermediates stay in `tmp_dir`, the same discipline `test_icon_jcon_suite.sh` keeps for its rundir and for the same measured reason (jcon `io.icn` grades what is in its directory). **Censused across all seven masters before landing: no entry lists or globs its run directory.**

## 3. THE CONTROL ARM (shared instrument, so it is owed)

Seven masters, 25-entry slices, pre-change vs post-change, same binary, same corpus, the pre arm run **from inside `scripts/`** so `__file__` resolves the same repo root (the HQV-34 trap: an instrument run from a copied directory succeeds about a different tree):

| icon | snobol4 | pascal | prolog | raku | rebus | snocone |
|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 |

— differing per-entry verdict lines, and identical `SUITE_BOARD` lines in all seven.

**The three argv[0]-sensitive entries fleet-wide were graded explicitly in both arms**, because a 25-entry slice does not contain them and a control arm that cannot see its subject says nothing: icon 414 `ladder_rung42_kw_host_version_progname` (prints only the TYPE and length of `&progname`) and snobol4 104 `datatype_2` (`HOST(0)`, ref `host0=` empty) **PASS identically in both arms**. Icon entry 924 is the intended flip: m4 FAIL → PASS.

## 4. THE FAIL-ONCE ARMS, AND A ROW GIVEN BACK

- **jcon `kwds`, one-program scratch corpus, both arms:** with `kwds.moderef` **m3 PASS and m4 PASS**; without it **m3 PASS and m4 FAIL**. The declaration is load-bearing and a deletion does not satisfy the criterion.
- **Every refusal proven red on purpose** before the mechanism was trusted: 4 fields, a wildcard entry, an unknown mode, a no-op substitution, an absent ref-line, an ambiguous ref-line, a majority substitution, an unreceipted row, and an explicitly-named sidecar that does not exist. Nine refusals, all rc=2.
- **`MODES.tsv`'s kwds m3-only row is retired on that measurement and not on a preference.** CEO-561's reason — *"no better ref and no pinned name can fix m4 against a one-step ref"* — was TRUE OF THE REF MODEL AS IT STOOD. The pin made the answer stated; CEO-581 changed the model. The cell is graded in BOTH arms again, which is a cell given **back** to the denominator — the opposite of the direction a declaration file usually moves.

## 5. NAMED, NOT INHERITED AND NOT CHASED

- **`test_gate_harness_transitive_companions.sh` is RED on the clean tree**, byte-identically: `BEFORE FAIL SKIP · AFTER HANG HANG`, expecting CRASH. Measured both ways by swapping my harness for `HEAD`'s and re-running. Pre-existing, not this landing's, and not this seat's row.
- **A second latent defect closed in passing, in the file already being changed:** `test_icon_jcon_suite.sh --corpus <scratch>` reached the SCORE.md write and published a JCON cell measured over the fixture's population — one program in, a complete and plausible `JCON 1/1` out, with a clean stamp. The board line is still printed (it is a real measurement of what was asked for); it is no longer called the package's published row. **Same shape as the builder trap measured one day earlier: an instrument pointed at the wrong tree does not fail, it succeeds about something else.**
