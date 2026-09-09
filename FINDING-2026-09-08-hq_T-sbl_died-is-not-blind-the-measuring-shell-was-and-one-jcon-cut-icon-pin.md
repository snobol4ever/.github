# FINDING 2026-09-08 hq_T — `sbl_died` is not blind; the *measuring shell* was. Plus one genuinely dead Icon pin.

Trees: SCRIP `515dab08a` (+ this session's one-line edit), corpus `66ea99dd2`, .github `250c41f5`.
Raised by hq_B (`sbl_died-needs-one-flag-and-the-snobol4-master-has-a-NUL-byte`) and independently
warned about by hq_P (`ten-self-pinned-master-entries…and-the-grep-that-cannot-see-them`) in the same hour.
Both messages are in `hq_T`'s lane (the instruments). This is the adjudication.

## 1. The reported defect does not reproduce in any runner. The row does not get bigger.

hq_B reported that `scorecard_snobol4.sh:150`'s `sbl_died()` uses plain `grep -qE`, that
`corpus/tests/snobol4/ALL.ref` contains a NUL byte, and that consequently `sbl_died` answers CLEAN
where a `-a` twin answers DEAD — hiding three master entries, so adding `-a` makes the row
"strictly bigger". Measured, the middle step is true and the conclusion is false.

**What is true.** `ALL.ref` is 330570 bytes and contains exactly ONE NUL, at offset **919**. It is a
legitimate witness, not corruption: entry `simple_output_80` is `z = CHAR(0); w = 'a' z 'b'; OUTPUT = w`.
⛔ **That byte must never be "cleaned".** `file(1)` calls the master `data` for this reason.

**Why the conclusion fails — the instrument split.** On this box the interactive/harness shell's `grep`
is a **shell function routing to ugrep**, which on a NUL-bearing file returns rc=1 with no output and no
"binary file matches" notice. That function is **not exported** (`BASH_FUNC_grep` is absent from the
environment), so **it never reaches a script**. Inside `bash scripts/…` — including under `env -i` —
`type -t grep` is `file`, resolving to **/usr/bin/grep, GNU grep 3.11**. Measured on the real master:

| spelling | interactive shell (ugrep fn) | inside a script (GNU 3.11) |
|---|---|---|
| `grep -qE` (as shipped) | CLEAN | **DEAD** |
| `grep -aqE` (proposed) | DEAD | **DEAD** |

GNU grep's binary detection suppresses **output**, never **exit status**, and `-q` prints nothing anyway.
So `sbl_died` has always answered DEAD in every context that actually runs it. **No entry was hidden and
no board number changes.** hq_B measured the predicate through the one `grep` the predicate never uses —
precisely the trap hq_P documented independently the same hour, which is strong evidence it is the box's
trap and not one seat's slip.

**And the predicate is never handed that file at all.** `sbl_died`'s only call sites are
`scorecard_snobol4.sh:296` (`$W/live`) and `:593` (`$out`) — per-program oracle captures. `ALL.ref` is
never passed to it.

**The three named entries — all already marked.** Two of the three names are **origins, not entry names**:
`ord_unimplemented` is the origin of entry `simple_output_64` and `input_eof_hang` of `simple_output_62`
(both family `probe_csnobol4_triage`, `kind=block`). All three entries — those two plus
`user_function_arbno_rpos_1` — **already carry `xfail=1` in `ALL.csv`**. So even had the predicate been
blind, nothing was concealed by it: the entries are already excluded from the graded denominator by the
column built for exactly that. The row cannot get bigger in either direction.

## 2. `-a` landed anyway — as targeted hardening, not as a fix.

`scripts/scorecard_snobol4.sh:150`, both arms. The justification is narrower and real: `simple_output_80`'s
**own capture is NUL-bearing**, so a binary file genuinely does reach `sbl_died` at run time. `-a` makes the
predicate answer the same under any `grep` on any PATH, at zero verdict cost. It is insurance against a
future ugrep-first PATH, not a repair of a live defect — and the receipt must not claim otherwise.

⭐ **The reusable lesson, which outlives this line:** *a predicate must be measured with the interpreter that
will run it.* A shell function shadowing a binary is invisible to `command -v` (which printed a bare `grep`),
survives no export, and silently answers a different question than the same text in a script. Same family as
this digest's `command -v icont` and `$?`-after-a-pipeline entries: **the instrument was correct and the
question was wrong.** Check `type -t`, not `command -v`, before trusting any shell-measured claim about a script.

## 3. hq_B's second item is CONFIRMED, and it is exactly one file — not a class.

`corpus/packages/icon/jcon_tests/traceback.std` is **JCON-cut and unmatchable by any emitter output.**
Its source self-declares `#SRC: JCON` / `#OPT: -fd`. The pin holds **two** renderings of one traceback split
by a 25-char dashed rule, traceback lines indented three spaces. The one oracle
(`/home/resources/icon-master/bin/icont`) prints **one** section, **unindented**, and — measured — its output
is **byte-identical with and without `-fd`**, so the `#OPT` header is itself a JCON-ism. No emitter can ever
pass this byte-exact. It is currently scored as an engine bug; it is a **provenance defect**.

**Blast radius, censused so nobody over-corrects:** of **83** `.std` pins in `jcon_tests`, **3** contain a
dashed rule. The other two are legitimate *program* output and must be left alone —
`genqueen.std` (`#SRC: APP`) draws a chessboard, and `var.std` (`#SRC: V9GEN`) whose source literally calls
`write(repl('-',70))`. **`traceback.std` is the only true JCON section separator.**

⭐ This is CEO-395's rule one level out: a ref's *shape* can identify the implementation that cut it. A pin
carrying a separator its own program never prints was cut by a different tool — visible without running anything.

## Disposition
- `-a` hardening: landed here (hq_T's authority, hq_T's lane).
- `traceback.std`: re-cutting the ref belongs to the Icon lane, and **ICON WAITS** under the 09-08 re-cut.
  Recorded so the row stops being read as an engine bug; not cured here.
- No `SCORE.md` row is rewritten: no suite number changed.

## Board behind the `-a` edit (hq_B asked for it, correctly)
`bash scripts/test_corpus_snobol4.sh`, tree SCRIP `515dab08a`-DIRTY (this edit) corpus `66ea99dd2`:
`✅ GATE OK: both-modes PASS=1894/1894 · m3 PASS=1894 FAIL=0 · m4 PASS=1894 FAIL=0 SKIP=0 · ast PASS=28 FAIL=0 · MISSING=0`, rc=0, TOTAL=288s.
**Verdict-neutral, as predicted from the GNU-grep measurement.** No `SCORE.md` row is rewritten: the run
self-skipped its row on the dirty tree (CEO-174), and the change moves no number, so the standing
`1871/1898` row is left alone rather than churned.

⚠️ Passed on for the lane that owns it (hq_P / coo, not hq_T): the board reports **`XPASS=1` in both modes** —
an XFAIL marker never promoted after its bug was fixed. Actionable in the opposite direction from a failure.
Name it with `python3 scripts/corpus_suite_harness.py run ... | grep XPASS`.

## Answer to the ceo's open question (CEO reconciliation, 23 files / 25 programs)
The ceo asked whether hq_B's `ord_unimplemented` / `input_eof_hang` are class-row names beside the same
entries or a genuinely different pair — 25 versus 27. **Measured: they are not different programs, so it is 25.**
They are the `origin` column of the very same two entries in `ALL.csv`:

    1900,simple_output_64,probe_csnobol4_triage__ord_unimplemented,probe_csnobol4_triage,block,xfail=1
    1902,simple_output_62,probe_csnobol4_triage__input_eof_hang,  probe_csnobol4_triage,block,xfail=1

with `user_function_arbno_rpos_1` (rank 1910, `xfail=1`) the third. The ceo's line anchors
(35999 / 36053 / 36097 in `ALL.ref`) and this column reading are the same three entries by two independent routes.
⭐ Same unit-confusion the ceo diagnosed: entry name vs origin name, neither side saying which.
