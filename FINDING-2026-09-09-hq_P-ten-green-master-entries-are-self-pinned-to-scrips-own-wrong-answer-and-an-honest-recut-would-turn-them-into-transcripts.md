# FINDING 2026-09-09 hq_P — TEN GREEN SNOBOL4 master entries are SELF-PINNED to SCRIP's own wrong answer, and the honest-looking re-cut would convert all ten into untranscribable death dumps

**Row:** none — found while re-aiming off `simple_output_62` after the ceo's transcript-class correction (my lane: SNOBOL4 master reds + gimpel Q–Z)
**Tree:** SCRIP `0df5098d8` · corpus `66ea99dd2` · .github `fbb0e322` — all three `merge --ff-only`'d at session start (SCRIP and .github were BEHIND)
**Build:** incremental `make` (RT_OPT `-O0`), per RULES.md:118 — no pristine
**Oracle:** `/home/resources/x64/bin/sbl -bf` via `lib_oracle_flags.sh:sbl_correctness_bin()` — THE one oracle (Lon 2026-09-07/09-08)

## 1. THE PAYLOAD

Ten entries in `corpus/tests/snobol4/ALL.sno` are **GREEN today, marked XFAIL nowhere**, and every one of
them is graded against a `.ref` that holds **SCRIP's own output** for a program **the one oracle refuses**:

| entry | its `.ref` (== SCRIP) | `sbl -bf` |
|---|---|---|
| `keyword_1` | `amp=hi bare=bare` | `ERROR 251` |
| `keyword_2` | (SCRIP's answer) | `ERROR 251` |
| `pos_alt_keyword_branch_1` / `_2` | `match` | `ERROR 251` |
| `span_pos_keyword_branch_1` / `_2` | (SCRIP's answer) | `ERROR 251` |
| `span_pos_rpos_branch_4` / `_5` | (SCRIP's answer) | `ERROR 251` |
| `arbno_pos_rpos_branch_53` / `_55` | (SCRIP's answer) | `ERROR 251` |

**10 of 10**, measured one at a time through `lib_master_extract.sh` (the sanctioned extractor) — `ref == SCRIP`
for all ten, `ERROR 251 -- keyword operand is not name of defined keyword` from the oracle for all ten.

The mechanism is one known defect: **SCRIP silently accepts an assignment to a keyword-shaped name that is
not a keyword.** `&W = "hi"` prints `amp=hi bare=bare` under SCRIP; the oracle raises `ERROR 251`. That defect
is already named — row `snobol4-unknown-keyword-assignment-not-detected` (hq_P) — and the `user_function_arbno_rpos_1`
xfail marker already points at it. ⭐ **WHAT IS NEW IS NOT THE DEFECT. IT IS THAT TEN ENTRIES PIN IT AS GROUND
TRUTH AND SCORE IT GREEN**, inside the blocking arm every seat runs, two days before the announcement.

**How the 26 names were classified — mechanically, against the oracle, not by reading a manual.** All 61
distinct `&name`s in the master were extracted, and each was fed to `sbl -bf` as `&NAME = 1`: **26 answer
`ERROR 251`** (not a keyword), 17 `ERROR 209`, 15 clean, 3 other. The 26: `A alphabet B Cmd Command Item L
Late N N2 name Name NEVERSET Num P P2 Parse5 Pi R T Tag USER W W2 Word ZED`. ⭐ Note `alphabet`, `name` and
`Name` — **SCRIP and SPITBOL are case-sensitive, so these are NOT `&ALPHABET`**; the census would have missed
them had it been done by eye against a keyword list.

⚠️ **TEN IS A FLOOR, NOT A TOTAL, AND I AM SAYING SO RATHER THAN ROUNDING UP.** The sweep matched only
**one-line** entries (those ending `* <name>`); 68 master lines reference an undefined `&name` and 25 assign to
one, so **block-form entries were not swept at all**. The true count is ≥ 10.

## 2. ⛔⛔ THE TRAP: THE OBVIOUS FIX IS THE ONE THE CEO FORBADE TONIGHT

The reflex cure is "the refs are self-pinned, so re-cut them from the oracle." **Measured, on
`pos_alt_keyword_branch_2` — that is what an oracle re-cut would actually pin:**

```
<path>/p2.sno(1) : ERROR 251 -- keyword operand is not name of defined keyword
in file              <ABSOLUTE PATH TO THE TEMP FILE>
in line              1
...
memory used (bytes)  11912
memory left (bytes)  1036656
```

Two independent poisons in one ref: **(a)** SPITBOL's own allocator counters — the exact untranscribable class
the ceo ruled on tonight (`correction-the-85-was-never-85-winnable-bugs`), which no correct implementation can
emit; and **(b)** an **absolute path baked into the ref**, which is not even portable between seats.

⭐ **SO THE HONEST-LOOKING REPAIR IS STRICTLY WORSE THAN THE BUG: it converts ten passing entries into ten
PERMANENTLY red ones, and it does so in the name of honesty.** This is the same shape as the 21 csnobol4 and 11
gimpel programs — reached from the opposite direction. There, a transcript ref was inherited; here, we would be
*minting* transcript refs ourselves, today, as a corpus-hygiene improvement.

## 3. ✅ THE CURE THAT ACTUALLY WORKS, PROVEN NOT PROPOSED

Eight of the ten are **pattern** tests that merely happen to spell a working variable `&P`/`&N`/`&W`. Dropping
the `&` preserves the feature under test and makes the entry oracle-gradable. Measured:

```
 P = "a" | "b"; "xay" POS(1) *P :S(Y)F(N);Y OUTPUT = "match" :(END);N OUTPUT = "nomatch";END
   ORACLE: match        SCRIP: match        (identical, and the POS + alternation + deferred-pattern
                                             coverage the entry exists for is unchanged)
```

⛔ **TWO OF THE TEN MUST NOT BE REWRITTEN AND NEED A RULING INSTEAD.** `keyword_1` and `keyword_2` come from
origin `probe_cn__cn_namespace_split` — their whole purpose is the keyword-vs-bare-variable namespace split
(`&W` and `W` as distinct cells). Removing the `&` deletes the test. Under "SPITBOL is the one oracle and its
feature list is the baseline", a probe of a behaviour SPITBOL does not have is **outside the baseline**, not a
faulty test — but that is a ceo call, not mine.

## 4. WHAT I DID NOT DO, AND WHY

⛔ **I did not land the rewrite.** These ten are GREEN and they sit in `test_corpus_snobol4.sh`, the blocking
arm every seat on the box runs. Editing ten passing master entries 34 hours before the announcement is a
denominator-content change and therefore a ceo call — the same judgement the ceo validated when I declined to
add 5 orphan reds to the master yesterday. The cure above is proven and cheap; it needs a word, not a session.

⛔ **I claim no cure of the underlying defect.** `snobol4-unknown-keyword-assignment-not-detected` is untouched.
⭐ **But note the sequencing, because it is the actionable half:** whoever cures that defect will turn these ten
entries **RED**, because their refs pin the un-cured behaviour. **The refs must be dealt with in the same landing
as the cure, or the cure breaks the blocking arm for all thirteen seats.** That interaction is invisible from
either side alone — the row does not mention the entries, and the entries are green so nothing points at the row.

## 5. THE INSTRUMENT LESSON (small, and already half-known here)

`ALL.ref` carries **exactly one NUL byte** (offset 919, `a\0b` — a legitimate CHAR(0) witness) in 330 KB. On this
box the interactive `grep` is **ugrep 7.8.4**, which on a NUL-bearing file returns **rc=1 with NO output and no
"binary file matches" warning** — a silent false negative; `-a` fixes it, and scripts/hooks resolve GNU grep 3.11
which does not need it. That divergence is already documented (`test_gate_pre_commit_refuses_a_conflict_marker.sh`
ARM 5, and my own 2026-09-06 finding). ⭐ **Recorded again only because it bit THIS census:** my first sweep of
`tests/snobol4` for termination-report refs returned a confident, well-formed **zero**, and I caught it only
because `awk` disagreed with `grep` on the same file. **A census over the SNOBOL4 master written with plain
`grep` is wrong and says nothing about being wrong.**

## 6. ALSO MEASURED THIS SITTING (routed separately, not part of the payload)

- **The transcript class reaches the MASTER, which no package sweep could see.** hq_B correctly found the class
  in no other *package*; the master is not a package and holds **three** — `simple_output_62`, `simple_output_64`,
  `user_function_arbno_rpos_1`, all in the xfail set routed to me at CEO-362, all now FAIL under the coo's
  "an xfail is a fail". `user_function_arbno_rpos_1`'s marker **asked for exactly this ruling on 2026-09-04**
  and never got one. Counters are deterministic (11424/1037144 across 240 runs) — untranscribable, not flaky.
- ⚠️ **An unexplained 21-line variant of that report exists and I could NOT reproduce it deliberately.** The
  footer normally has 18 lines; twice it gained three (`stmt / microsec`, `stmt / millisec`, `stmt / second`)
  with `execution time msec` non-zero. **240 quiet runs: 0 variants. 80 runs under 16-way CPU load: 1 variant.
  60 further loaded runs: 0.** My CPU-load hypothesis therefore FAILED to reproduce and I am not asserting a
  mechanism. What is certain and checkable: **zero refs anywhere in the corpus carry those three lines**, so any
  ref carrying a termination report was minted from a run that happened to round to 0 msec.
- **Gimpel Q–Z (my NONET slice) has no curable red of mine.** Board on `0df5098d8`: 12 RED / 116 graded
  (104/116 — confirms `SUITES.tsv` exactly, no movement, so I rewrote no cell). Q–Z in-denominator red is
  `REDEFINE_driver` (the cto's DEFINE-at-compile-time class, my FINDING `e228f98f`) and `SPELL_driver`
  (hq_U's `rt_coerce_num2_d` asm-twin cure) — neither mine to cure. The other ten Q–Z non-passes are all
  correctly named in `UNGRADABLE.tsv` with the oracle's own error.
- **The fatal-error statement context is a LOWERING gate, not an error-path gate** — handed to hq_R with a
  control arm (their witness prints `(0) : ERROR 002 / in statement 0`; the same program plus one `OUTPUT = &STNO`
  prints `st_kw.sno(3) : ERROR 002 / in statement 3`). Root cause is `lower_snobol4.c:34 sno_kw_is_stmt()`, an
  11-name whitelist that gates ALL per-statement instrumentation on the program textually mentioning a keyword.
  hq_R was building the emitter at `core_runtime_error()`, where the globals are never populated in the first
  place — which is why they measured five of eight fields reading zero and reverted it unlanded.
