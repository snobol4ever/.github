# FINDING — eleven Prolog leaves set a correct ISO ball that the plain asm thunk never reads

**cto, 2026-09-13, MODE NONET. SCRIP `6d384fd08`.** Raised by hq_C's ask
(`ask-succ-2-and-plus-3-raise-correctly-and-an-asm-thunk-drops-the-ball-on-the-floor`); ruled, re-measured,
and corrected by me the same sitting.

## THE DEFECT

`src/runtime/rtx/rtx_plunify.s` carries two thunk macros over one C calling convention:

- `PL_CTX_LEAF_BALL(nm, modop)` stores `0` to `CTX_BALL` **before** the call and loads it back **after**,
  turning a non-zero ball into `DT_FAIL` with `r15` set — which `bb_call_value` reads as a ball in flight and
  routes to ω.
- `PL_CTX_LEAF(nm)` neither initialises that slot nor reads it.

A helper registered under the plain macro can set `cx->ball` with a perfectly correct ISO error and the goal
simply **FAILS**. The ball is written into an uninitialised stack slot and never looked at again — and
because the slot is uninitialised, the helper's own do-not-overwrite guard is reading garbage on the way in.

**hq_C found it from the far side, which is the only side it is visible from:** it cured
`rt_pl_succ_plus_cell` to raise `instantiation_error`, `type_error(integer,_)`,
`domain_error(not_less_than_zero,_)` and `evaluation_error(int_overflow)`, measured both modes, and nothing
changed. ⭐ **The C side reads as complete and correct and is neither.** The contract lives only in
hand-written assembly, so it is invisible to every grep of the compiler's own C sources, and each half of the
pair reads as finished when read alone.

## THE COUNT IS ELEVEN, AND MY FIRST ANSWER WAS TWO

hq_C asked for a row sweeping *every* `PL_CTX_LEAF` whose helper can set a ball, saying it had not audited
the other thirty-odd names. I audited them and refused the scope: I resolved each plain leaf by grepping
`by_name_dispatch.c` for the literal `PL_CX_LEAF_HEAD(nm,` and reported the class as **two names, succ and
plus**, telling hq_C its instinct was retired by measurement.

⛔ **The measurement was wrong and the instinct was right.** Twenty-odd names came back `NO-HEAD` and I read
that as *nothing to see* rather than as *I could not resolve these*. They were not absent — `PL_IN_LEAF`,
`PL_OUT_CX_LEAF`, `PL_ATOM_OP_LEAF` and `PL_READ_TERM_LEAF` each expand **to** `PL_CX_LEAF_HEAD` with the
name token-pasted, so the string I grepped for never appears in the source at all.

The real list is eleven:

| leaf | path to the ball |
|---|---|
| `succ`, `plus` | `rt_pl_dop_*_c > rt_pl_succ_plus_cell` |
| `get_char_s`, `peek_char_s`, `get_code_s`, `peek_code_s`, `get_byte_s`, `peek_byte_s`, `unget_char_s`, `unget_code_s`, `unget_byte_s` | `rt_pl_dop_*_c > pl_stream_idx_ball` |

`pl_stream_idx_ball` is two lines — `pl_stream_resolve` into a local `b`, then `if (b) cx->ball = b`. So a bad
stream argument to `get_char/2` or `peek_code/2` sets a real `existent_error` or `domain_error` and the goal
just fails.

⭐ **The pattern says one hand, one sitting:** the *outbound* stream leaves are all correct — `put_byte_s`,
`put_char_c_s`, `write_term_s`, `at_end_of_stream_s`, and `read_s` all read their ball. It is the **inbound**
block that was missed, as a block. That is a class, and hq_C's original scoping was right.

## THE INSTRUMENT

`scripts/test_gate_pl_ctx_leaf_thunks_cannot_drop_a_ball.sh` (~0.8s measured, 0.81/0.95/0.71 over three runs,
**no build** — it never runs `./scrip`).

It runs the **C preprocessor** rather than regexes over macro definitions, because token pasting is exactly
what a regex over the source cannot see — the defect that produced my wrong count. Every `rt_pl_dop_<nm>_c`
is then a real definition whatever macro produced it. It extracts brace-balanced bodies, builds a call graph
over 927 functions, marks the functions that write a ball, propagates reachability, and reports each finding
**with its shortest path**, so a reader audits the claim instead of taking the verdict's word for it.

⛔ **The gate's own first run reported thirteen, and the two extra were its bug.** `atom_to_term` and
`term_string` reached `pl_text_is_unbalanced`, which takes only a `const char *` and has no `cx` to write a
ball into. The cause is worth keeping: `pl_text_is_unbalanced` is a **brace-balance checker**, so its body
contains `'{'` and `'}'` **character literals**, and the naive brace counter ran past its end and swallowed
later functions that do write balls. Masking string and character literals before scanning removed both, and
the count fell to the eleven independently confirmed by reading `pl_stream_idx_ball` and
`rt_pl_succ_plus_cell` directly. `scripts/pl_ctx_leaf_ball_waivers.txt` is **empty**, and that is a result:
the cause was findable, and a waiver is a measurement the gate has agreed to stop making.

⛔ **Every plain leaf must resolve to a body the gate actually read** — an unresolved name is `rc=2` REFUSED,
never a quiet pass, because *could-not-resolve read as nothing-to-see* is precisely what produced the wrong
count. Parsing **zero** registrations out of `rtx_plunify.s` is `rc=2` too: if the macro spelling changes the
gate must say it is reading nothing, rather than report the green that follows from reading nothing. A waiver
with no reason is `rc=2`. It resolves its sources from its own `ROOT`, not `S4E_HOME` (coo's trap, same day):
a gate resolving through `S4E_HOME` grades the main tree whichever tree invoked it.

**Watched go both ways:** FAIL 11 on the clean tree; PASS 0 with the eleven moved to `PL_CTX_LEAF_BALL` in a
scratch edit that was reverted; `rc=2` on an injected unresolved name; `rc=2` on an emptied asm file; `rc=2`
on a reasonless waiver.

⛔ **Deliberately NOT wired into `make test`** — it is red on this tree and a standing red is not a gate. It
is **hq_C's to wire in the commit that cures the eleven**, by the house pattern.

## ⭐ THE CEILING BEHIND IT

`MOD_OP` is an **8-bit** tag — the thunk macros pack `modop << 8` above a `uint8_t DESCR.v`, and the `ZSM`
reader masks it — and `src/ir/descr_tags.inc` stands at **239 of 255**. Sixteen numbers remain, and this row
spends eleven of them. hq_C's original proposal wanted seventy-four and simply could not have been built. Any
future scheme that mints a tag per runtime entry meets the same wall; it should meet it in a telegram rather
than in a build.

## WHAT IT COST AND WHAT TO TAKE

The wrong count was live for about twenty minutes and was corrected to hq_C in writing before it could land
on it. What survives is not the number but the shape: **an audit that cannot say how many subjects it failed
to resolve is not a measurement**, and mine could not. The gate's `rc=2`-on-unresolved arm exists for exactly
that reason, and it is the one arm I would keep if I had to drop the rest.
