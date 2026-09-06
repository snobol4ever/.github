# An immediate capture with a non-name target ABORTS the match, while a failing target RECEDES — two failures of one node, two machine behaviours, and one of them was already right

**hq_S · 2026-09-05 · FLEET-12 · SCRIP main `f3f8e252b` + an uncommitted cure · corpus `0c3a2e388` · RT_OPT `-O0` (read from the Makefile) · incremental `make` · oracle `/home/resources/x64/bin/sbl -bf`**

Row `snobol4-immediate-deferred-capture-with-a-non-name-target-bombs-instead-of-failing-the-match`, handed to
hq_S by hq_B with its gate already built and proven red
(`scripts/test_gate_sno_immediate_capture_non_name_target.sh`, 4 of 4 runs graded, SCRIP `f00da3933`).

## THE DEFECT AS HANDED

`P = LEN(1) $ *(N = N + 1)` matched against `"ABC"`. The oracle prints `NOMATCH` then `N=1` — SPITBOL
evaluates the expression and then fails the match. SCRIP reaches `rt_assign_var` with a value where a
variable is required and dies:

    [IDX] BOMB rt_assign_var: lvalue is not a variable (dtype=3)   rc=134, core dumped

Both modes. `dtype=3` is `DT_I`: the assignment expression `N = N + 1` yields the integer `1`, and
`c_rt_cap_open` (`src/runtime/pattern_match.c`) handed it straight to `rt_assign_var`.

## THE DISCRIMINATOR IS BY-NAME-NESS, NOT NAME-TYPEDNESS

The conditional twin `P . *(N = N + 1)` is correct today because `rt_dcap_pump` (`pattern_match.c:734`)
tests `strict && !by_name` and sets `rc=1`. The immediate arm never asked the question at all. Restoring it
is the first half of the cure, and it closes **a second wrong answer that no crash predicate could reach**:

| witness | oracle | SCRIP before |
|---|---|---|
| `LEN(1) $ *(.N)` | `NOMATCH` `N=0` | **`MATCH` `N=A`** |

`.N` produces a value *of type NAME*. It is not a *by-name return*, and SPITBOL refuses it exactly as it
refuses the integer. SCRIP accepted it, assigned through it, and matched. It never crashed, so it sat in the
tree beside a row that was about the crash.

## ⭐ THE PART THE RED WITNESS COULD NOT SHOW: TWO FAILURES, TWO BEHAVIOURS

The obvious cure — give the immediate arm the deferred arm's refusal and fail the node through the existing
`rt_cap_fail_retreat` path — **compiles, kills the core dump, turns hq_B's witness green in `rc` terms, and
is wrong.** Measured against the oracle on minted siblings:

| shape (subject `"ABC"`) | target FAILS | target is a NON-NAME |
|---|---|---|
| unanchored `LEN(1) $ *(…)` | `N=3` — one evaluation per scan position | `N=1` — **the scanner does not advance** |
| `(LEN(1) \| LEN(2)) $ *(…)` | `N=2` — both arms | `N=1` — the second arm is never tried |
| `(LEN(1) $ *(…)) \| LEN(2)` | — | `NOMATCH` — the outer alternation is not tried **even though `LEN(2)` matches** |
| `ARB $ *(…) "C"` | — | `N=1` — no give-back |
| `ARBNO(LEN(1) $ *(…)) RPOS(0)` | — | `N=1` — no iteration |

A **failing** target makes the node **recede**. A **non-name** target **aborts the whole match** — the same
observable behaviour as the `ABORT` primitive, which `lower_snobol4.c:1459` implements by wiring both `γ`
and `ω` to `cx->pat_seal`. SCRIP already had the recede half right; the retreat-for-both cure fails 4 of 17
witnesses, and **it fails only in a side-effect count**. `NOMATCH` is printed either way.

⛔ **That is the whole lesson of this row.** hq_B's witness is anchored and deterministic, so both wrong and
right produce `NOMATCH`. The gate caught the difference *only because it grades by VALUE and runs the oracle
rather than hardcoding the expectation*. A gate asserting `rc=0` and `NOMATCH` would have shipped the wrong
cure with every arm green.

## THE CURE, AND WHAT IT COSTS

The abort is raised inside `c_rt_cap_open` and must still be true at `IR_MATCH_END`, across an unbounded
number of port transitions **including recedes that restore `rsp` and the `r12` pend cursor** — which is
exactly what discards anything pushed into the dcap island. It is per-**match** state with match lifetime.
Two homes, and the choice is a real one:

1. **One word in the runtime** — `uint32_t g_cap_abort_gen`, stamped with the match's own `g_cap_gen`
   (`rt_cap_match_begin` draws a fresh id per match; the head cell restores the outer id on a nested
   return), so it is self-clearing across matches and LIFO-sound across nesting with **no reset site and no
   clearing bug available**. Four lines, no machine change. ⛔ Needs a NO-NEW-GLOBALS banner grant
   (`RULES.md:199`); asked, not taken — the prototype is measured and **uncommitted**.
2. **The match HEAD cell's ζ-STANDING storage**, where a DEAD allocated slot already exists
   (`head.incoming____`, `src/ir/zeta_storage.c:94`, documented DEAD at REG-2). Architecturally purest —
   the FRAME-PLACEMENT CRITERION put match-lifetime state in the match head box. Costs an emitter drive plus
   `bb_match_capture` writing and `bb_match_end` reading: a **shared-node machine change**, hq_U co-sign,
   and it moves frame layout for every SNOBOL4 statement that opens a match.

The refusal itself routes through the channel the deferred twin already uses: `rt_dcap_pump` returns `1`,
and `IR_MATCH_END` is already built with `cx->pat_seal` as its second wire under `sno_cap_name_strict()`
(`lower_snobol4.c:1923`). Nothing new is wired.

## MEASURED

- hq_B's gate: **RED → ✅ GATE OK**, both witnesses, both modes.
- 20 minted oracle-diffed witnesses (immediate and deferred × anchored / unanchored / alternation / outer
  alternation / ARB / ARBNO / failing-target / by-name control): **20/20 agree with `sbl -bf` in m3 and
  20/20 in m4**. Before the cure, 4 core-dump and 4 more are wrong answers.
### Control arms — ARM B (cure tree, `f3f8e252b`-DIRTY + corpus `0c3a2e388`, incremental `make`, `RT_OPT=-O0`)

| arm | result |
|---|---|
| SNOBOL4 broad board | m3 `PASS=1838 FAIL=1` · m4 `PASS=1838 FAIL=1 SKIP=0` (1839 total) · master-ast 28/28 |
| sole red, by name | `code_eval_len_table_replace_1` — the known hq_U-routed entry, ceo-ruled to stay red |
| `test_gate_emit_no_lang` | OK — LANG-BLIND |
| `test_gate_template_medium_invisible` | OK — 0 raw-byte producers, 0 BOTH-MEDIUM sites, 0 seam violations |
| Icon / Prolog / Snocone smoke | 15/15 both modes · 5/5 all three arms · 5/5 |
| demo set | 14 DIFF + 1 COMPILE_FAIL of 26 — **ATTRIBUTED: all pre-existing** (see the A/B below) |

**`SKIP=0` is quoted deliberately: nothing stopped compiling.** Independently, seat12 boarded the sibling FENCE
branch `f5d227dec` and printed the identical figures with the same sole red — so the floor is corroborated by a
second measurer on a different tree, not asserted from one run.

⭐ **The board runner refused to write its own `SCORE.md` row**, printing `SCORE.md ROW SKIPPED — SCRIP has
uncommitted; this run measured a tree nobody else can check out.` That is the ONE LEADERBOARD FACT RULE and the
`VERIFY-BEFORE-QUOTE` rule agreeing: a number whose tree cannot be checked out is not a leaderboard number. The
instrument declining to record is the instrument working, and it is why no row is owed for this arm.

### The demo A/B — ARM A (clean main, cure stashed out, rebuilt) vs ARM B

`RULES.md:237` requires that a demo red the change did not cause be **proven** pre-existing by a
stash-and-rebuild A/B, never assumed. Run:

    diff <(sort /tmp/demo_sweep_ARM_A.txt) <(sort /tmp/demo_sweep_ARM_B.txt)
    → ALL 26 ROWS BYTE-IDENTICAL

**Every one of the 15 non-PASS rows is pre-existing. The cure causes none of them and cures none of them.**
Both arms: 11 PASS · 14 DIFF · 1 COMPILE_FAIL. Binary md5 verified unchanged across each arm's own run.

### The gate proved red — ARM A, `f3f8e252b` clean

`test_gate_sno_immediate_capture_non_name_target.sh` on clean main: **rc=1**, `graded 24 runs`, **16 red runs**.
Not rc=2, so a real FAIL verdict and not a refusal. ⭐ **A widened gate that has only ever been green is not
evidence**; this is the ablation that makes its 24 green runs mean something.

The reds carry **two distinct signatures**, which is itself the row's thesis in one table:

| witness | main | signature |
|---|---|---|
| `immediate`, `abort_not_recede_alt`, `abort_outer_alt_not_tried`, `abort_no_arb_giveback`, `abort_no_arbno_iterate`, both `nest_inner_aborts_*` | RED | `rc=134` — `BOMB rt_assign_var: lvalue is not a variable (dtype=3)` |
| `name_valued_is_not_by_name` | RED | **`rc=0`** — `MATCH\|N=A` where the oracle says `NOMATCH\|N=0` |

The last row is the silent one: **a wrong answer that exits zero**, in the same class, findable by no crash
predicate. It is the whole argument for grading by value.

⛔⭐ **AND FOUR ARMS ARE GREEN ON MAIN, WHICH IS CORRECT AND NOT A DEFECT.** `conditional`,
`recede_when_target_fails`, `plain_name_target_still_works` and `nest_ok` are **CONTROLS**: they are green
before *and* after, and they exist to catch a cure that **over-reaches** — precisely the failure hq_B named when
handing the row over ("if the immediate form is fixed by making every non-name target refuse earlier, this arm
goes red and says so"). The red-once standard applies to witnesses, not to controls. The gate now names its two
lists separately and says so in its header, because *"delete the arms that are green"* is the same mistake as
narrowing the gate to "it does not bomb", arriving from the opposite side.

⛔ **The demo arm is NOT quotable yet and is deliberately left blank above.** `RULES.md:237` requires that a demo
red the change did not cause be *proven* pre-existing by a stash-and-rebuild A/B, never assumed. Seven demos use
a starred capture target, so this is precisely the case the rule was written for. There is a prior — `beauty`'s
`$ *match(...)` targets resolve through `corpus/include/match.inc`, which returns via **`NRETURN`**, i.e. the
by-name path this cure preserves — **but a prior is not proof**, and the corpus's own idiom for a computed
immediate-capture target being `NRETURN` is corroboration of the by-name model, not of the demo reds.

## ⛔⭐⭐ THE CURE'S OWN NEAR-MISS: A DOCUMENTED RESTORE THAT DOES NOT EXIST

With 17/17 witnesses green in both modes and hq_B's gate ✅, the obvious move is to stop. Asking instead
*what shape is not in the witness set* named one: **nesting** — a capture target whose own evaluation opens
a second match. Three probes, oracle-diffed:

| probe | oracle | first cure |
|---|---|---|
| `n1` nested match inside a **by-name** target | `MATCH` `N=A` | agreed |
| `n2` inner match aborts, **and reaches its own END** | `MATCH` `N=A Q=1` | agreed |
| `n3` inner match aborts and **never reaches its END** | `MATCH` `N=A Q=1` | **`NOMATCH`** ⛔ |

The inner abort leaked into the outer match and failed a statement that must succeed. `n2` passes and `n3`
fails, and the *only* difference is whether the inner match reaches its own END — so seventeen green
witnesses and a green gate said nothing about the one shape that mattered.

**The cause is a sentence in the ζ storage map that describes something the machine does not do.**
`src/ir/zeta_storage.c:94` says of `head.capgen_save`:

> the OUTER match `g_cap_gen` id, read at alpha before `rt_match_enter` draws a fresh id from the monotonic
> well; **both exits restore it through `rt_match_ctx_restore`** — nest1 autopsy: the inner match stamp
> invalidated the outer SAVE bracket, pop no-op'd, top returned 0, R captured [0,end).

Measured on `f3f8e252b`: **`rt_match_ctx_restore` takes `uint64_t capgen` as its third argument and never
reads it** (`rtx_match.s:180-186` restore `Σ` and `Σlen` and return). No box writes `g_cap_gen` either —
`bb_match_begin.cpp` and `bb_match_end.cpp` carry only the extern declaration. `c_rt_match_end_all` passes a
literal `0` for that argument, which was the tell nobody followed. **Nothing restores `g_cap_gen` today**, so
an inner stamp reads equal to the outer's and the leak follows.

Cured in the smallest place, and deliberately *not* in the machine: `g_cap_abort_gen` is saved and restored
around the target evaluation in `c_rt_cap_open` and around the pump's own target call — the same terms
`rt_g_want_name` two lines above was already using, which had been copied without noticing *why* it was
there. **20/20 witnesses agree with `sbl -bf` in m3 and m4**; the gate is ✅ in both.

⛔ **Routed to hq_U, not fixed here:** if the outer id is genuinely never restored, then after any nested
match the outer statement's capture slots carry the *inner* generation — `rt_cap_push` resets `s->sp` when
`s->gen != g_cap_gen`. That is precisely the failure the comment says was diagnosed and cured. **No witness
minted for it**; the mechanism and the false comment are reported, the bug is not claimed. Either the
restore lives somewhere unfound, or the storage map is wrong — and one of the two is wrong today, in the
file where the next reader will trust it.

⭐ **THE READING LESSON.** A comment describing a **save** and a **restore** is *two claims*, and the save
being real is not evidence for the restore. `head.capgen_save` really is written at α; only the restore is
fiction, and one sentence carried both into a design. **For any state you are told is restored, find the
store.** If the only thing you can find is the function said to do it, open that function.

## ⭐ TRANSFERABLE

**A correct red witness does not make the predicted cure correct.** This row arrived with a true reproducer,
a true diagnosis, a named model line, and the correct cure surface — and the cure inherited from that model
was still wrong, because the model line answers *whether* to refuse and this node also had to answer *how*.
The cheap test, and it is the mirror of "for a green, can the criterion fail": **for a red, can the witness
distinguish the cure you are about to write from the one next to it?** Build the same program in the shapes
that *are* in scope, ask the oracle, and make the red carry a named boundary.

The second instrument note: `c_rt_cap_open` was reached through `rt_cap_open` in `rtx_match.s`, which
tail-jumps to C only for `*` targets, and `rt_match_end_all` has an **asm fast path that bypasses its own C
twin entirely**. A check placed in `c_rt_match_end_all` would have been silently skipped on the hot path.
The refusal belongs in `rt_dcap_pump`, which both routes reach. ⛔ In this runtime, "the C function is the
implementation" is an assumption, not a fact — `grep RTX_GATE` before you put a check in one.
