# The goto-field call inversion is CURED — and what is left is a SECOND mechanism, not the tail of this one

**hq_P · 2026-09-06 · row `snobol4-goto-field-function-call-is-invoked-by-name-and-scrip-is-exactly-inverted` (rank 0)**
**Tree: SCRIP `f3f8e252b` + this landing · corpus `0c3a2e388` + this landing · `.github` `ba78882c` · RT_OPT=`-O0` · incremental `make`**

## 1. The inversion, reproduced on this tree before a line was touched

Graded against `/home/resources/x64/bin/sbl -bf` (the CORRECTNESS oracle, never the bench one):

| probe | SPITBOL | SCRIP (before) |
|---|---|---|
| `GOF = .L3 :(NRETURN)` then `:(GOF())` | `go` / `landed` rc=0 | **ERROR 239** "indirection operand is not name" rc=1 |
| `GOV = 'L3' :(RETURN)` then `:(GOV())` | **ERROR 021** "function called by name returned a value" | `go` / `landed` rc=0 |

Exactly inverted: we accepted the form the oracle refuses and refused the form it accepts.

## 2. The mechanism — and the measurement that named it, rather than a reading of the symptom

`sno_goto_computed_target` (`src/lower/lower_snobol4.c:846`) builds the deferred goto's target as **`"$IGT$n"`** — the
`$` string-indirection prefix. Correct for a STRING label name, wrong for a NAME.

⭐ **But the `$` wrap is not what raises 239, and this is the part that would have sent a cure to the wrong place.**
The goto field was not a WANT-NAME context, so `rt_nret_fix` (`src/runtime/rt/rt.c:778`) took its
`if (!wn && r.v == DT_N) r = rt_deref(r)` arm and **dereferenced the returned NAME away** — to the unset value of
`L3`, the null string — *before* the `$` wrap ever saw it. `rt_sno_indirect_name` (`src/runtime/core/core.c:2118`)
then refused an EMPTY operand, not a non-name one.

Proven by running the existing killswitch rather than by reading the code: `SCRIP_IND_NAME=0` takes the refusal out
and the program says **`transfer to undefined label: $IGT$0 (indirect name is null)`** — *null*, not *not-a-name*.

⭐ **THE NAMED BOUNDARY (the baton's lesson (b) applied to a RED witness — a red must fail for the reason you think).**
The same call in a VALUE context — `X = GOF()` then `DATATYPE(X)` — is **byte-identical to the oracle** (`dt=STRING`,
`[]`, `done`, `landed`). So the by-name RETURN machinery was never broken; only the goto field's want-name context was
missing. That one probe is what makes this a bounded defect instead of a vibe, and it is what told me the cure did not
belong anywhere near `rt_nret_fix`.

## 3. The cure — two sites, and NEITHER is the shared staged-call box

* **`src/lower/lower_snobol4.c`** — a goto operand that is `TT_FNC` is a BY-NAME call: prefix `'@'` instead of `'$'`,
  and prepend the **already-existing** `SNO$WANTNM` IR call (the same shape the EXPR machinery uses at `:2484`) so the
  callee's NRETURN name survives `rt_nret_fix`.
* **`src/runtime/runtime_eval.c`** — the `'@'` arm: a `DT_N` resolves through the NAME's own identity
  (`VARVAL_fn` → `NV_name_from_ptr`); anything else raises **ERROR 021** via `kwb_error`, so `&ERRLIMIT` still governs.

⛔ **ONLY `TT_FNC` TAKES THE NEW ARM, AND THE GRAMMAR IS WHY THAT IS SAFE.** `sno_goto_computed_target` is reached by
exactly two shapes: `$(expr)` and the call form. `goto_expr` has **no call production** (`snobol4.y:222`), so `$(expr)`
can never be `TT_FNC` — ordinary computed gotos keep `$` by construction, not by a name test.

⭐ **THE 021 ARM READS THE DESCRIPTOR TYPE, NEVER `rt_g_ret_by_name`** — directly honouring hq_U's hazard note on this
row: that flag is a process-global with no per-frontend reset, and `polyglot.c` compiles SNOBOL4 and Icon into ONE
image, so a caller acting on the bare global could act on a flag another language set. A descriptor cannot be stale in
that way. The arm cannot fire on a flag it did not itself set because it reads no flag at all.

**Killswitch:** `SCRIP_GOTO_CALL_BYNAME=0` restores the pre-cure inversion exactly — all four gate arms go red.

## 4. Control arms

* **SNOBOL4 master, both modes:** `total=1852 · m3 pass=1815 FAIL=1 · m4 FAIL=1`. The single FAIL is
  `code_eval_len_table_replace_1` — hq_T's charset class, rowed to hq_U, red before this landing and expected to stay
  red until they land it. **No regression.**
* **The row's own entry `user_function_indirect_replace_1` went XFAIL → XPASS** ("marker stale, promote it"), and is
  promoted in this landing: `ALL.csv` xfail→0, its `ALL.xfail` block removed, the `ALL.sno` separator de-XFAILed.
  Verified in both modes against its real, non-empty, multi-line `.ref` — lesson (a) satisfied, it is a legitimate
  witness for itself.
* **Blast radius — `scrip.c` routes `.sc` and `.reb` through `lower_snobol4.c`, so SHARED-NODE VERDICT SCOPE owes
  Snocone and Rebus.** Both boards are **byte-identical with the cure ON and OFF** (snocone 67/302 pass, 218 fail;
  rebus 64/139 pass, 71 fail). Those reds are pre-existing and untouched. ⭐ The killswitch is what made that
  provable in one extra run instead of a stash-and-rebuild.
* **Gates:** `test_gate_sno_goto_field_call_is_by_name.sh` added, green, and **proven non-vacuous** — with
  `SCRIP_GOTO_CALL_BYNAME=0` all four arms (2 arms × 2 modes) go red.

## 5. ⛔ WHAT IS NOT CURED, AND WHY IT IS A SECOND MECHANISM RATHER THAN THIS ONE UNFINISHED

The payload that got this row ranked 0 — gimpel `STATEF_driver.sno` and `POKEV_driver.sno` — is **not green**, and
saying so plainly is the point of this section.

Both use the published idiom `RET = .RETURN :(NRETURN)` / `PR = .RETURN :(NRETURN)`: the name returned is **`RETURN`**,
the special transfer, not a user label. After this cure `STATEF_driver` resolves that name correctly and then dies
`ERROR 038 — transfer to undefined label: RETURN`.

⭐ **That is a different mechanism, not a loose end of this one.** `RETURN` / `FRETURN` / `NRETURN` are registered as
**per-graph COMPILE-TIME landings** (`lower_snobol4.c:2086–2092`, wired to the graph's own return/fail nodes), while a
by-name goto target is chosen at **RUN time**. Nothing in the current machinery lets a runtime-resolved target select
one of three compile-time landings. Curing it is a structural change to the function-return wiring — hq_U's co-sign
surface — not another line in the resolver.

⚠️ **AND ONE HONEST LOOSE END I COULD NOT EXPLAIN, STATED AS UNEXPLAINED.** `STATEF_driver` reaches ERROR 038 (the name
`RETURN` resolved), but `POKEV_driver` reaches **ERROR 021** (the callee's result was not a NAME at all) from what is
textually the identical idiom. I ablated the three shapes that differ — a nested call with intervening calls, a
success-branch goto, and two goto-calls in one statement (`:S(PR(8))F(PR(4))`) — and **all three match the oracle
exactly**, so none of them is the cause. I am recording this as open rather than guessing: POKEV pulls in seven further
`-INCLUDE` files (ORDER, ROTATER, REVERSE, COMB, BASE10, CARDPAK, DECOMB) and the 021 may well be a pre-existing defect
in one of them surfacing now that the goto no longer dies first. **Both drivers were red before this landing and both
are still red; what changed is that they now fail LATER and for a named reason.**

## 5b. ⛔⭐ PROMOTING ONE XFAIL TOUCHES **FOUR** FILES, AND I GOT IT WRONG TWICE BEFORE A GATE CAUGHT ME

Worth its own section because "there is no XFAIL" makes this a move every seat will now make repeatedly, and the
failure is silent in the place you look first.

`ALL.csv` (the `xfail` cell) · `ALL.xfail` (the reason block) · `ALL.sno` (the banner) · ⭐ **`ALL.ref` — which
carries its OWN paired banner that must match `ALL.sno`'s BYTE FOR BYTE.**

* **Miss 1 — the width.** The banner is fixed-width 80 (`make_banner`: `dash_count = BANNER_WIDTH - 2 - len(suffix)`).
  Deleting the ` XFAIL` token leaves an INVALID 74-char banner; the dashes must grow by exactly six.
* **Miss 2 — the file I never looked in.** I grepped `ALL.sno ALL.ref ALL.xfail` for the entry at the start and read
  the result as "`ALL.ref` does not carry it." It does. I acted on that reading and shipped a mismatch.

⭐ **THE DIAGNOSTIC LESSON, AND IT IS THE SAME SHAPE AS THE 239 ONE ABOVE:** the symptom named a file and a family
that had nothing to do with my edit — `GATE FAIL [snobol4]: extract-family 'test_snobol4_parser_binary_opsyn' failed`,
a family ~forty entries away from 1853. Two ablation rounds (revert-all, then one-file-at-a-time) pointed at `ALL.sno`
and I nearly concluded the banner format itself was the problem. **Running the failing command directly and reading
its exception was worth more than both ablations combined:** `family.ref banner mismatch at seq 1852: sno=... ref=...
XFAIL` names the true cause in one line. ⛔ A gate's summary line is a symptom too; when ablation gets confusing, run
the thing the gate ran.

⚠️ **AND THE ABLATION ITSELF WAS CONFOUNDED, which is why it misled me:** testing "`ALL.sno` only" left `ALL.xfail`
and `ALL.csv` at origin, so that arm measured an INCONSISTENT tree, not my change. **A one-file-at-a-time ablation is
invalid when the files must agree with each other** — the atomic unit here is all four, and any subset is a state
nobody would ever commit.

⭐ **AND A THIRD MISS THE REBASE FOUND, WHICH IS THE ONE THAT GENERALIZES: THE SEQ NUMBER IS NOT STABLE.** I wrote
the promotion against seq **1853**. While I was measuring, another lane landed an entry earlier in the master and the
same program became **1854**, so all four of my edits conflicted at once and my worktree suddenly matched the entry
NOWHERE — which reads exactly like "the entry was deleted" and is not. ⛔ **A master entry's identity is its NAME
(and its `origin` provenance key), never its ordinal**; the ordinal is a rendering of current sort order and any
promotion, absorption or `--resort` renumbers it. ✅ The re-applied version keys on the name, reads the seq back OUT
of `ALL.csv`, and rebuilds both banners from `make_banner`'s own width formula — so it is correct at whatever number
the entry currently holds. **A hand-typed seq is a hard-coded fact with a short shelf life.**

## 6. The transferable part

⭐ **A killswitch is not just a safety catch, it is the cheapest control arm you will ever have.** The same
`SCRIP_GOTO_CALL_BYNAME=0` proved the gate non-vacuous, proved the Snocone and Rebus reds pre-existing, and reproduced
the exact pre-cure inversion for the record — three separate obligations discharged by one flag, none of them needing a
rebuild or a stash.

⭐ **And the diagnostic half: `SCRIP_IND_NAME=0` answered "empty or not-a-name?" in one command with no build at all.**
An error message that names the REFUSAL (`is not name`) can be describing a value that never got that far. When a
refusal is the only evidence you have, take the refusal out and look at what is actually underneath it.
