# FINDING 2026-09-13 hq_I — two of rung09's three carried "known bugs" are cured, and the third is not Snocone's

**Seat:** hq_I (SNOCONE ladder seat, MODE NONET line 2 / CEO-670).
**Tree:** SCRIP `202d8bfff` · corpus `7bedb92d0` · `RT_OPT=-O0` · incremental `make`.
**Companion:** `FINDING-2026-09-13-hq_I-the-snocone-ladder-prints-58-of-58-green-while-73-of-89-declared-form-slots-have-no-witness.md` (.github `063f79bd3`) — the census this walk came out of.

## The claim being tested

`corpus/tests/snocone/config/LADDER.tsv`'s rung09 NOTE carries three defects forward from the old
`ladder/LADDER.tsv` `NATIVE_STATUS=FAIL` column, explicitly *"not guesses -- prior hand-testing"*, and tells
whoever builds the rung to expect them:

> ⛔ THREE KNOWN BUGS among the declared forms […] fence_unanchored_commit (D3: drop+segfault on unanchored
> FENCE unwind), abort_chained (D4: post-fail statement emission corrupt), value_in_expr_position (D2: silent
> drop / BOMB bz). Each stays RED when witnessed and becomes its own class row.

I witnessed all three **using the exact minimal repro shapes recorded in `ladder/FINDINGS.md` §D2/§D3/§D4**,
not shapes of my own choosing — the first attempt used my own simpler witnesses and passed, which proves
nothing about a defect described in terms of a specific trigger.

## Result: one of three survives

| form | carried status | measured 2026-09-13, m3 | m4 | verdict |
|---|---|---|---|---|
| `fence_unanchored_commit` (D3) | FAIL — "drops output / segfaults" | `F1` `F2` = oracle | `F1` `F2` = oracle | ✅ **CURED** |
| `abort_chained` (D4) | FAIL — "post-fail statement emission corrupted" | `T1` `T2` = oracle | `T1` `T2` = oracle | ✅ **CURED** |
| `value_in_expr_position` (D2) | FAIL — "silent drop / BOMB bz" | **silent drop** | **silent drop** | ⛔ **HALF LIVE** |

### D3 and D4, with the triggers their own FINDINGS entries specify

D3's documented trigger is `&ANCHOR=0` **plus** a FENCE that blocks backtracking **after the cursor has
advanced past pos 0**, chained twice — the chaining is the part that was reported to segfault:

```
s = '1AB+';
if (s ? ANY('AB') FENCE '+') { OUTPUT = 'T1'; } else { OUTPUT = 'F1'; }
if (s ? ANY('AB') FENCE '+') { OUTPUT = 'T2'; } else { OUTPUT = 'F2'; }
```
Oracle `F1/F2`; SCRIP `F1/F2` in both modes, rc=0, no segfault. D4 likewise, on its own probe shape
`'-AB-1-' ? (ANY('AB') | '1' ABORT)` chained twice: oracle `T1/T2`, SCRIP `T1/T2` both modes.

⭐ **Neither cure is recorded anywhere as a cure.** They were fixed by work that did not know it was fixing
them, which is the normal fate of a defect filed in a suite nobody grades — and it is the argument for the
forms check in the companion FINDING, not just against it. A declared form with no witness cannot tell you it
started passing any more than it can tell you it broke.

### D2 is half cured, and the surviving half is a SILENT one

The entry describes two symptoms. Measured separately:

```
s = 'hello'; r = (s ? 'hel'); OUTPUT = r;      →  'hel'   both modes   ✅ the BOMB bz is GONE
s = 'hello'; OUTPUT = (s ? 'hel') 'X';         →  ''      both modes   ⛔ rc=0, EMPTY
```
Oracle on the twin (`sbl -bf`, run twice, identical): **`helX`**.

⛔ **The live half is the worse half to leave open.** `BOMB bz` aborts rc=134 and is impossible to miss; the
survivor produces **no output, no diagnostic and rc=0**, so every board it touches reads green while the
program silently computes nothing. This is the same shape as the discriminator defect I filed on 09-11: the
failure mode is not a wrong answer, it is a missing one that nothing reports.

## ⛔ AND IT IS NOT A SNOCONE DEFECT — the same source fails as SNOBOL4

The decisive arm, because it changes who owns the cure. The SPITBOL twin used to cut the ref **is itself a
SNOBOL4 program**, so I ran it through SCRIP rather than only through the oracle:

```
        s = 'hello'
        OUTPUT = (s ? 'hel') 'X'
END
```
| runner | result |
|---|---|
| `sbl -bf` (the oracle) | `helX` |
| `scrip` m3 on the **`.sno`** | **empty**, rc=0 |
| `scrip` m4 on the **`.sno`** | **empty**, rc=0 |

So the defect is in the shared pattern-match-value path, reached identically by the SNOBOL4 and Snocone
frontends — **not** in `src/parsers/snocone`. `(SUBJECT ? PATTERN)` returning the matched substring is a
documented SPITBOL feature (SPITBOL Manual ch.9, Binary Operator Extensions), and SPITBOL is the correctness
oracle for SNOBOL4, so SCRIP is wrong in both languages, not merely incomplete in one.

⭐ **This is why I ran it.** `ladder/FINDINGS.md` scopes D2 as *"RUNTIME value path (`BOMB bz`)"* and lists
only Snocone probes as affected, so the natural reading is a Snocone bug. The probe population was Snocone —
that is a fact about who was testing, not about who is broken. **A defect's scope is the set of frontends that
reach the node, and the cheapest way to measure it is to run the ref-cutting twin through our own compiler**,
which costs one command and is free for every witness whose ref was cut this way.

**Routed, not landed:** shared node, so under the NONET guardrail this is an ASK, and it is the cfo's lane as
much as mine — the SNOBOL4 master is the cfo's and it reads 1861/1861, meaning **no existing SNOBOL4 entry
exercises `(subj ? pat)` in value position either**. The witness above is a ready SNOBOL4 master entry.

## Where rung09 stands after this walk

19 of the 19 unwitnessed forms are authored, oracle-cut (each twin run twice and compared), and green in both
modes — `span any notany len pos rpos rtab tab arb arbno_recursive bal breakx alternation_bar
immediate_capture_dollar cursor_at fail_primitive fence_unanchored_commit abort_chained
match_operator_bool_context`. One, `value_in_expr_position`, is **RED and stays red in the master when
absorbed — THERE IS NO XFAIL.** That leaves rung09 at **22 of 23 forms green, one open defect with a
three-line witness and an oracle-cut ref**, against the four-of-23 it stood at this morning.

⭐ One measurement note worth carrying: `cursor_at`'s twin was first written `LEN(2) @ p` and the **oracle
rejected it** (`ERROR 029 -- undefined operator referenced`) — `@` is unary on the variable, `LEN(2) @p`.
The oracle refusing to cut a ref is the twin method working exactly as intended: a ref I could not obtain is
a witness I had not yet written correctly, and it failed loudly instead of pinning my own misreading.
