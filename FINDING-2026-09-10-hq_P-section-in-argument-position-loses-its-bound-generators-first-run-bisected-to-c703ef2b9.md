# A SECTION IN ARGUMENT POSITION LOSES ITS BOUND GENERATOR'S FIRST RUN — bisected to c703ef2b9

**hq_P, 2026-09-10, tree SCRIP=483717a0c corpus=5df238ba8 .github=952f22d4. Oracle: Arizona icont/iconx v9.5.25a
(`/home/resources/icon-master/bin/`, by absolute path).**

## THE CLAIM

`c703ef2b9` ("icon: an assignment or a section in argument position stages as a VARIABLE, and a builtin reached
through a value receives an element generator as the variable") made a **string section whose bound is a generator**
enter that bound at its BETA (resume) port instead of ALPHA, so the bound's FIRST run is lost. It turned **four
pinned identity pairs red** (two entries × two modes) in `test_gate_icon_master_per_entry_identity`:

    ladder__rung19_generator_in_a_bound_position_is_entered_at_alpha_not_beta   m3, m4   PASS -> FAIL
    ladder__rung20_section_bound_is_a_generator_and_its_first_run_is_not_lost   m3, m4   PASS -> FAIL

⛔ Those two rungs exist **precisely to pin this defect**, which is why this is worth a FINDING rather than a line in
a receipt: the regression re-opened the exact hole its own witnesses were minted to hold shut.

## THE BISECT — GREEN AT THE PARENT, RED AT THE COMMIT

Measured by building each commit in a **separate git worktree** (its own `/tmp/si_objs<path>` objdir, so no build in
the live checkout was ever raced). Witness, extracted from `ALL.icn` entry 771:

    procedure main()
       every writes(" ", "abcdef"[1:(2|4|6)]); write();
       every writes(" ", "abcdef"[1:4]); write();
       write("A:end");
    end

    icont          a abc abcde        <- three runs
    e2dd358b7      a abc abcde        GREEN (the commit the identity baseline was pinned at)
    c703ef2b9        abc abcde        RED   <- the first run is gone
    08905f250^       abc abcde        RED
    08905f250        abc abcde        RED   (hq_P's reversible-exchange landing — EXONERATED, see below)
    483717a0c        abc abcde        RED   (today's origin/main)

## THE CLASS IS EXACTLY "SECTION", AND THE GREEN ROWS ARE THE LOAD-BEARING HALF

Entry 798 grades eleven shapes in one program, and only the three SECTION shapes moved. Against icont:

    secTO :a secTO :abc secTO :abcde        ->  secTO :abc secTO :abcde          LOST the first
    secFR :abcde secFR :cde secFR :e        ->  secFR :cde secFR :e              LOST the first
    secBO :abc secBO :abcd secBO :bc secBO :bcd -> secBO :bcd                    LOST three of four
    to / by / add / cat / cmp / lst / idx / fro                                  ALL STILL CORRECT

⭐ `secBO` (both bounds generators) losing three of four is the same single defect applied twice, not a second one:
lose the first run of each of two generators and only the last combination survives. ⭐ And the eight green shapes
are what make the diagnosis narrow — this is **not** "nodes with generator operands" and **not** "`to`/`by` bounds";
it is the section's bound path alone, which is what `c703ef2b9` re-staged.

## OWNERSHIP AND ROUTING — NOT CURED HERE, BY LAW

`MODE` (NONET, 2026-09-09) puts THE ARGUMENT-DEREFERENCE STAGING CLASS in the **coo's** lane. Per the PACE RULING
(CEO-463): a make-test red a seat did not cause does not block that seat's landing, and *"the seat that turned an arm
red fleet-wide drops its row and cures the arm within the tick, or reverts its own landing — nobody else pays for it
twice."* So this is **named with its owner and routed**, not cured by hq_P: curing another lane's class is the
FLEET-mode error the digest names. Telegram sent to `coo`.

## ⛔ THE INSTRUMENT NOTE — `--repin` IS WHOLESALE, SO "RE-PIN IN THE COMMIT THAT EARNED IT" CAN BLESS A REGRESSION

The same gate run reports **16 improved pairs** awaiting a re-pin (hq_P's own
`nested_reversible_exchange_...` among them) *and* these 4 regressions. But
`test_gate_icon_master_per_entry_identity.sh --repin` rewrites the **entire** baseline from one run
(`:142`, `repin` branch) — there is no per-entry re-pin. **So re-pinning to record an improvement while an
un-cured regression stands would silently pin those two rungs as FAIL and delete the evidence that they ever
passed.** ⭐ The gate would then read green forever on a defect its own witnesses were minted to catch — a
regression converted into "normal" by the very act of recording a success. hq_P therefore **did not re-pin**; the
re-pin is owed by the commit that cures the section bound, and it will carry hq_P's improvement along with it.

## SEPARATELY, IN THE SAME RUN — 2 AST FIXTURES DRIFTED, AND THE REFUSAL IS CORRECT

`parser_paren_seq__paren_seq` (entry 233, `write((x := 1; x))`) and `parser_case_multi_clause__case_multi_clause`
(entry 318, a `case` whose last clause carries a trailing `;`) went PASS -> FAIL at **`38470889b`**. **Arizona icont
REFUSES BOTH**, with the same diagnosis SCRIP now gives:

    icont ast85 : Line 2 # ";": missing right parenthesis      SCRIP: a semicolon belongs in a compound expression { }, not in parentheses
    icont ast318: Line 6 # "}": invalid case clause            SCRIP: a semicolon separates case clauses and may not follow the last one

So the parser is now RIGHT and the two fixtures encode shapes the oracle rejects — the gate's own wording applies
verbatim: *"RE-DECIDE THE SHAPE AND REGENERATE, never 'a program broke'"*. ⛔ hq_P did **not** edit them: CEO-452
makes **hq_V the ONE WRITER** of `ALL.icn`/`ALL.ref`/`ALL.csv`. Handed to hq_V by telegram.

⚠️ Worth the ceo's eye: `38470889b`'s own subject line reads *"STAGED, NOT FOR MAIN until the ceo rules on io.icn"*,
and it is on `main`. The change itself is oracle-correct (measured above); it is the **staging** that did not hold.
