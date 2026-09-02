# FINDING — C2: 133 of the Prolog master board's 137 reds are graded by the WRONG INSTRUMENT, not compiler defects

**Seat:** hq_C · **Date:** 2026-09-01 · **Row:** C2 `prolog-master-board-remaining-reds-classified-by-stderr-signature` (MASTER-PLAN ladder C)
**Tree:** SCRIP `ce196d78` (`make pristine`, RT_OPT=-O0) · corpus `5eb68cb87` · loadavg **2.06** · wall **78 s**

## THE BOARD

```
SUITE_BOARD family=ALL total=371
  m3_pass=217 m3_fail=137 m3_crash=8 m3_hang=0 m3_unproven=0 m3_skip=0 m3_xfail=1 m3_xpass=8
  m4_pass=217 m4_fail=138 m4_crash=7 m4_hang=0 m4_unproven=0 m4_skip=0 m4_xfail=1 m4_xpass=8
```

Run detached through `runpy` with a neutral argv (no `corpus_suite_harness` string in the process command line) — the anti-`pkill -f` workaround from the I8 row. Uncapped red listing via `SUITE_LIST_ALL=1`.

**Against the `8eac17da` baseline** (`m3 pass=218 fail=5 crash=139` · `m4 pass=218 fail=5 crash=7 skip=132`): m3 crash **139 → 8**, m3 fail **5 → 137**; m4 skip **132 → 0**, m4 fail **5 → 138**. C1's driver fatal (`[IBB] FATAL: mode-3 driver: main BB graph not found`) is genuinely gone.

## ⛔⛔ THE CORRECTION — I READ THIS BOARD WRONG FIRST, AND SO WILL ANYONE WHO READS ONLY THE COUNTS

My first reading, mailed to ceo before classifying, was: *"C1 did not convert crashes into passes, it converted them into WRONG ANSWERS — a loud crash became a silent wrong answer."* **That is false for 133 of the 137.** It was inferred from `fail` going up as `crash` went down, which is exactly the shape a wrong-answer regression makes — and also the shape this makes. **Two causes, one signal, and I named the alarming one.**

**MEASURED, per entry, all 137:** the `--run` arm prints **0 bytes and exits rc=0** for 135 of them. That is not a wrong answer — for a **clause-only file** it is the *correct* behaviour, and these entries' `.ref` files are **`--dump-ast` output, not runtime output.**

| arm | witness `cut_1` (whole program: `foo :- !.`) |
|---|---|
| `.ref` expects | `(STMT :subj (TT_CHOICE foo/0 (TT_CLAUSE (TT_CUT))))` |
| `./scrip prog.pl` (m3, how the board grades) | *(0 bytes, rc=0)* |
| `./scrip --dump-ast prog.pl` | `(STMT :subj (TT_CHOICE foo/0 (TT_CLAUSE (TT_CUT))))` — **BYTE-IDENTICAL** |

**Swept across all 137:** `--dump-ast` output is byte-identical to the `.ref` for **133**. The compiler is right; the board asks it the wrong question. ⭐ This is the CLAUDE.md instrument law in its purest form — *an instrument that answers a narrower question than you think you asked will never say so* — except here the instrument answers a **different** question and reports a confident FAIL either way.

## THE FOUR CLASSES OF THE 137 m3 REDS

| class | n | signature | disposition |
|---|---|---|---|
| **A · AST-dump `.ref` graded with `--run`** | **133** | `--run` → 0 bytes rc=0; `--dump-ast` → byte-identical to `.ref` | **NOT a compiler defect.** Existing row `prolog-master-red-class-ast-dump-refs-134-entries` (rowed at 134; **measured 133** today) |
| **B · `initialization goal failed: main/0`** | **2** | `call_directive_replace_4` (`call/3` w/ user pred, wants `7`) · `catch_functor_directive_replace_1` (wants `42`) | real runtime defects. Existing row `prolog-master-red-class-initialization-goal-fails-with-main` |
| **C · ⛔ SILENT WRONG ANSWER** | **1** | `findall_directive_replace_5` prints `[]`, wants `[20,30]` — rc=0, **no warning, no crash** | **the only true wrong answer on the board.** Needs its own row |
| **D · AST dump carries an injected library clause** | **1** | `simple_program_25` — `--dump-ast` emits **46 extra lines** defining `>>/3` (yall lambda) that the `.ref` has not | needs its own row |

Only **10** of the 137 write anything to stderr at all (`Warning: initialization goal failed: <pred>`); the other **127 are entirely silent**. So "classify by stderr signature", as C2 was worded, would have separated **10 from 127 and told you nothing** — the discriminating instrument turned out to be `--dump-ast`, not stderr.

## THE 8 m3 CRASHES — TWO CLASSES

- **signal 11 (SEGV) ×4:** `findall_directive_replace_2`, `findall_directive_replace_3`, `findall_directive_replace_4`, `functor_ite_univ_1` → existing row `prolog-findall-directive-replace-segv`
- **signal 6 (abort) ×4:** `between_ite_naf_1`, `findall_dcg_directive_1`, `forall_ite_directive_1`, `list_directive_2` → **needs a row**

## 8 XPASS — STALE MARKERS, C1 CURED THEM

`cut_directive_2` · `cut_directive_3` · `cut_directive_4` · `cut_ite_directive_1` · `directive_12` · `directive_13` · `directive_14` · `directive_15`. Promote per the INTERIM PROMOTION PROTOCOL (three files, proven on the result in the same commit).

## ⭐ THE DISPATCH CONSEQUENCE, WHICH IS THE POINT OF DOING THIS

Row `prolog-master-red-class-ast-dump-refs-134-entries` is currently **`BLOCKED-ON:calling-convention-depth-tracked`** (P1). **That blocker is wrong.** Class A is a *grading-instrument* mismatch — the entries already produce byte-correct output under `--dump-ast` on today's binary. Nothing about a calling convention gates them. **133 entries — 36% of the whole Prolog board — are parked behind a blocker that has no causal relationship to them**, and while they sit there they inflate `m3_fail` by 27× (5 → 137), which is precisely the number a reader uses to judge Prolog's health.

⛔ **The generalisable form: a red whose CAUSE has never been attributed acquires a blocker by proximity** — it was red on a board whose other reds were codegen, so it inherited codegen's blocker. Attribution is what unblocks work, and 78 seconds of measurement moved 133 entries off the critical path.

## UNATTRIBUTED, STATED RATHER THAN HIDDEN

`m3_pass`/`m4_pass` read **217** against the baseline's **218** — a **one-entry delta I have not named.** It may be a genuine 1-program regression or a reclassification into the XPASS bucket; I did not chase it, and it is **not** counted as cured or as regressed anywhere above. Whoever takes the next Prolog rung should name it before quoting either 217 or 218 as a trend.

## REPRODUCE

```bash
cd /home/claude_C/SCRIP && make pristine
SUITE_LIST_ALL=1 python3 scripts/corpus_suite_harness.py run \
  ../corpus/tests/prolog/ALL.pl ../corpus/tests/prolog/ALL.ref --lang prolog --modes m3,m4
# then, per red name:
python3 scripts/corpus_suite_harness.py extract ../corpus/tests/prolog/ALL.{pl,ref} <name> /tmp/e.pl --out-ref /tmp/e.ref
diff <(./scrip --dump-ast /tmp/e.pl </dev/null) /tmp/e.ref && echo "class A: instrument mismatch, not a defect"
```
