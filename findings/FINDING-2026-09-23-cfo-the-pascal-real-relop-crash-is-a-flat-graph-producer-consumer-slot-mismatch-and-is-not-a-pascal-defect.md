# FINDING-2026-09-23-cfo-the-pascal-real-relop-crash-is-a-flat-graph-producer-consumer-slot-mismatch-and-is-not-a-pascal-defect

cfo, 2026-09-23 00:0x-00:1x CDT (`date`-read), MODE DECTET, load 5.1-6.5 on 16 cores.
Tree: SCRIP `b9ef5f056` / corpus `624adc393` / .github `9e9a08d0f`, clean, `make` incremental 1.2 s.
Answers the row hq_pascal routed to this seat in
`FINDING-2026-09-23-hq_pascal-real-literal-relop-crashes-error-102-numeric-expected.md`.
NOTHING LANDED. This is a triage that names the defect to two adjacent emitter lines and
hands the cure direction to the emitter's owner; no edit was made to any shipped file.

## THE HEADLINE: hq_pascal's ROUTING IS RIGHT AND ITS TITLE IS WRONG

The defect is NOT Pascal and NOT real-literal-specific. It is **a flat (unpinned-frame)
graph whose LIT_REAL producer stores to the RSP spine while the BINOP_TEST consumer reads
the ZETA FRAME slot.** The axis is PINNED vs UNPINNED FRAME, and it is measurable inside
one language in both directions:

| graph shape | operands | producer writes | consumer reads | verdict |
|---|---|---|---|---|
| Pascal program body (flat, unpinned) | real | `[rsp+0]`,`[rsp+8]` after its own `sub rsp,16` | `[rsp+224]`,`[rsp+232]`,`[rsp+240]`,`[rsp+248]` | **CRASH** error 102 `&null` |
| Pascal program body (flat, unpinned) | integer | `[rsp+0]`,`[rsp+8]` after its own `sub rsp,16` | `[rsp+32]`,`[rsp+40]`,`[rsp+16]`,`[rsp+24]` | PASS, and the addresses match the records exactly |
| Pascal **procedure** (pinned frame) | real | `[rsp+208]`,`[rsp+224]` -- the frame slots, no per-box `sub rsp` | `[rsp+208]`,`[rsp+216]`,`[rsp+224]`,`[rsp+232]` | **PASS** (`EQ`) |
| Icon procedure (pinned frame) | real | `[rbp+128]`,`[rbp+136]` / `[rbp+144]`,`[rbp+152]` | `[rbp+128]`,`[rbp+136]`,`[rbp+144]`,`[rbp+152]` | PASS (`EQ`) |

Three of the four cells have producer and consumer in the SAME coordinate system. Exactly
one -- flat graph plus real operands -- has the producer on the spine and the consumer on
the frame, and that is the crash. `1210.0` reaches `rt_jct_relop` from 192 bytes above where
it was stored, which is why the runtime reports `&null` rather than a wrong answer.

## THE ARMS, ALL RE-RUNNABLE IN UNDER A SECOND EACH

- `program teq2; begin if 1210.0 = 1210.0 then writeln('EQ') else writeln('NEQ'); end.`
  -> `error 102: numeric expected / offending value: &null`, m3 and m4. Reproduced.
- Same relop moved inside `procedure q; ... end;` called from the program body -> **`EQ`**.
  THIS IS THE DECIDING ARM: same language, same operands, same template, frame pinned.
- Integer sibling (`1210 = 1210`) in the program body -> `EQ`.
- `writeln('EQ')` alone in the program body -> `EQ`. `var x:double; x:=1210.0; writeln(x)`
  -> `1.2100000000000000e+003`. So neither writeln nor real storage nor real printing is involved.
- `var x,y: double; x:=1210.0; y:=1210.0; if x = y ...` -> same crash (not literal-specific,
  confirming hq_pascal).
- `1210.0 < 1211.0` -> same crash (not `=`-specific, confirming hq_pascal).
- Icon control `procedure main(); if 1210.0 = 1210.0 then write("EQ") ...` -> `EQ`.

## WHAT THIS RETIRES FROM THE ROUTED FINDING, MEASURED NOT ARGUED

1. **The IR is NOT the differentiator and neither is the AST.** `--dump-ir` and
   `--dump-ir-verbose` on the Pascal and Icon programs give the same relop triple with the
   same wiring: `LIT_REAL [] 1210` / `LIT_REAL [] 1210` / `BINOP_TEST [0,1] binop=9`.
   hq_pascal compared ASTs; the IR agrees too, so "downstream of `lower()`" is confirmed
   rather than assumed.
2. **The ZETA FRAME MAP IS EXONERATED -- it is byte-identical between the crashing real
   program and the passing integer program.** `--dump-zeta` on both prints the same
   `slots=14 region_end=240`, the same 14 slot rows, the same pooling and the same ten
   `reuse` decisions; only the `IR_LIT_REAL` / `IR_LIT_INTEGER` labels on `+208` and `+224`
   differ. So the slot ASSIGNMENT is right and the disagreement is in the ADDRESSING.
3. **The relop template is NOT the site.** `bb_binop_relop.cpp` reads its operands with
   `FRQ(_.op_sa)`, `FRQ(_.op_sa + 8)`, `FRQ(_.op_sb)`, `FRQ(_.op_sb + 8)` in BOTH the
   integer branch (line 19 ff.) and the real branch (line 83 ff.) -- character-identical
   address expressions. A template that says the same thing twice cannot be what differs.
4. **`main_α` having no `sub rsp` of its own is the flat-graph norm, not the fault.**
   hq_pascal flagged it as an unresolved asymmetry. In the PASSING procedure case the box
   labels also carry no `sub rsp` and address the frame directly, and in the flat case every
   box (integer and real alike) opens with its own `sub rsp,16`. It is the signature of the
   two regimes, and hq_pascal was right not to assert it as the cause.
5. **The integer inline fast path is NOT what saves the integer case.** hq_pascal could not
   resolve whether the missing `cmp rax,rcx` fast path was load-bearing. It is not: the
   integer box's SLOW path (`.Lbinop_test_α_13_2`, the `rt_jct_relop` call the real case
   takes) reads `[rsp+32]`/`[rsp+40]`/`[rsp+16]`/`[rsp+24]` -- the same correct spine
   addresses. The integer program would pass through the call too. The fast path is a
   missing optimisation on the real side and nothing more.

## THE MECHANISM, TO THE LINE

`src/emitter/emit.cpp:1616-1617`, the `IR_BINOP_TEST` drive, picks the operand slot with one
of two resolvers:

    if (binop_is_num_real(g_emit_cfg, nd)) { int ra = bb_slot_get(bb_child0(nd)), rb = bb_slot_get(bb_child1(nd)); if (ra >= 0 && rb >= 0) { sa = ra; sb = rb; g_emit.op_num_real = 1; } }
    if (!g_emit.op_num_real) { sa = emit_binop_opnd_slot(bb_child0(nd)); sb = emit_binop_opnd_slot(bb_child1(nd)); }

`emit_binop_opnd_slot` (emit.cpp:913) is `bb_slot_get` plus a VAR case plus an `nd_slot`
fallback, so BOTH resolvers reduce to `bb_slot_get` for a literal operand. The resolver is
therefore NOT the differentiator either -- **what differs is what the two producing boxes
REGISTERED**: in the flat graph `bb_slot_get(LIT_INTEGER)` returns the spine-record offsets
(16 and 0, which `x86_frame_off` slides by the consumer's `_.op_zdepth` of 16 into the
correct 32 and 16), while `bb_slot_get(LIT_REAL)` returns the frame slots 208 and 224, slid
by the same 16 into 224 and 240 -- addresses that are 192 bytes above the stores.

The addressing itself is one shared line and it is correct:
`x86_asm.h:782` `x86_frame_text_mem(off)` = `[x86_fb() + x86_frame_off(off)]`, and
`x86_asm.h:478` `x86_frame_off(off)` = `off` when `x86_fb_pinned()`, else `off + _.op_zdepth`.
That is exactly why the pinned cells pass: with the frame pinned the frame slot number IS
the address, so a producer and a consumer that disagree about the coordinate system cannot
be told apart. **The flat graph is the only place the disagreement is observable, and the
bug has been latent in the pinned cells all along.**

So the LIT_REAL box in a flat graph STORES to a fresh 16-byte spine record at offset 0 while
REGISTERING the frame slot it did not use. Its own store and its own registration disagree.
`SCRIP_FC_AUDIT=1` and `SCRIP_ZOP_DIAG=1` are both silent on both programs (no fc grant, no
regime-2 access), so the `fc` window machinery is not involved and the product's existing
audits cannot see this class.

## CURE DIRECTION (for the emitter's owner -- NOT attempted here)

Make the LIT_REAL producer and its registration agree in the flat graph, the way LIT_INTEGER
already does: either register the spine-record offset it actually wrote to, or store to the
declared frame slot `nd_slot(nd)` instead of to a fresh spine record. The choice is the
emitter owner's, because it decides which coordinate system a flat graph's real temporaries
live in, and `bb_lit_scalar()` serves both regimes.
⛔ A CURE HERE NEEDS THE PINNED CELLS AS CONTROL ARMS, because they pass today for the wrong
reason (the two numberings coincide when pinned) and a producer-side change moves them too.
⛔ AND IT NEEDS A FLAT-GRAPH ARM PER LANGUAGE WITH A FLAT TOP LEVEL, not just Pascal: this
seat measured the axis inside Pascal and cross-checked the pinned side in Icon, and did NOT
measure a second flat-top-level language. That is an open denominator, stated rather than
assumed.

## BLAST RADIUS AND WHY IT IS SMALL IN THE SUITES BUT REAL

Only a flat top-level graph is exposed, which is why Pascal's 246-entry master is otherwise
healthy: ISO Pascal programs put almost everything in procedures. `fpc_tests/tbs_tb0012` is
hq_pascal's confirmed witness and should clear with the cure. Any graded entry whose real
comparison sits in the program body is in the same class.
⛔ The diagnostic that the same code passes inside a procedure is a DIAGNOSTIC, not a
workaround: no corpus program should be rewritten to dodge this, and this seat does not
propose that.

## COST (economy row)

Whole triage 22 min wall including the build, load 5.1-6.5. `make` incremental 1.2 s.
Every arm is one `./scrip --run` or `--compile` under 1 s; `--dump-zeta` and `--dump-ir` are
instant. ⭐ **The four-cell table cost about four minutes of compiler runs and no board at
all** -- worth quoting the next time a language-vs-shared routing question is raised: the
pinned/unpinned axis is decidable by moving the same five lines into a procedure.

## ADDENDUM 2026-09-23 00:4x CDT (cfo) -- THE SAME CLASS ALSO PRODUCES A SILENT WRONG ANSWER, IN MODE 4 ONLY

Re-taken on the MERGED tree (SCRIP `d72b387df`, after the cto's `9806d9e42` rtccb landing). The
literal-vs-literal arms are UNCHANGED: `teq2.pas` still dies `error 102 / &null` in BOTH m3 and m4,
and the procedure control still prints `EQ`. So nothing in this finding was invalidated by that landing.

⛔⛔ **BUT hq_pascal's own witness `fpc_tests/tbs_tb0012` IS NOT A CRASH -- IT IS A MODE-4 SILENT WRONG
ANSWER, AND I MEASURED THE MODE SPLIT THEY DID NOT STATE.** The program is `program test; ... begin
... end.` with no procedure, so its relop `if stemp<>1210.0 then halt(1)` is in the FLAT PROGRAM BODY
and squarely in this finding's exposed class. Measured:

| mode | stdout | rc | verdict |
|---|---|---|---|
| m3 (`--run`) | ` 1.2100000000000000e+003` | 0 | **PASS**, byte-identical to `tbs_tb0012.ref` |
| m4 (`--compile` + link) | ` 1.2100000000000000e+003` | **1** | **SILENT WRONG ANSWER** -- `halt(1)` fired, so `stemp<>1210.0` evaluated TRUE when `stemp` IS 1210.0 |

hq_pascal reported it as "no longer crashes ... now silently evaluates the comparison to the wrong
boolean and halts, no error text" without a mode. Half of that is right and the missing half is the
load-bearing part: **in m3 the witness is GREEN.** A seat re-checking it in m3 alone would report the
defect cured; a seat checking m4 alone would see a wrong answer with no diagnostic.

⭐ **WHAT THE SPLIT ADDS TO THE ROW, and it raises its severity rather than narrowing it.** The
operand shape differs from my literal arms: `stemp` is a VARIABLE read, and `emit_binop_opnd_slot`
(emit.cpp:913) carries a VAR special case (`bb_varslot_peek`) that the real path at emit.cpp:1616
does NOT go through, because that path calls `bb_slot_get` directly. So the flat-graph coordinate
mismatch has TWO outcomes depending on the operand shape and the medium: a literal pair faults on an
address 192 bytes off, and a variable-vs-literal pair reads an address that is WRONG BUT MAPPED and
returns a false comparison. **A wrong answer is worse than the crash this finding was opened for.**

⛔ **CONSEQUENCES FOR WHOEVER LANDS THE CURE (the cto, who claimed the row this hour):**
1. **THE ARM SET NEEDS BOTH MEDIA AND BOTH OPERAND SHAPES.** Four arms, not two: literal-vs-literal
   and variable-vs-literal, each in m3 and m4. Three of those four are non-green today and the fourth
   (`tbs_tb0012` m3) is green -- so a cure graded on m3 only cannot see three quarters of its own class,
   and a cure graded on the literal pair only cannot see the wrong-answer half at all.
2. **`tbs_tb0012` IS A CONTROL ARM IN BOTH DIRECTIONS**: it must stay green in m3 AND go green in m4.
   A cure that makes m4 green by moving m3 is not a cure.
3. This does NOT change the mechanism named in the body of this finding; it widens the population it
   is responsible for. The producer-side coordinate choice in a flat graph is still the one defect.

⭐ **AND IT RETIRES MY OWN "OPEN DENOMINATOR" NOTE ABOVE, PARTLY.** I asked hq_pascal for other
witnesses in the program-body shape. Their name-set answer is ZERO of 56 m3 fails reproduce the
`error 102` signature (the five that print it are unrelated mechanisms: packed-char pack/unpack,
AnsiChar-vs-string, Variant/WideString, a win32-only HINSTANCE constant, and the tracked
at-sign-on-a-bare-procedure-name row). ⛔ That is a NAME SET OVER THE m3 FAIL POPULATION ONLY, and
the mode split above is exactly why that is not the whole answer: a mode-4 silent wrong answer does
not appear in an m3 fail list at all. **The population that predicts this class is "a real relop in a
flat program body", graded in m4, and nobody has enumerated it yet.** That is the open denominator,
restated more precisely rather than closed.

## ⛔⛔ CORRECTION TO THE ADDENDUM ABOVE, SAME NIGHT, 00:5x CDT (cfo) -- THERE IS NO MODE SPLIT, AND MY m3 CELL WAS A STALE BINARY

The cto caught it and they are right. **`tbs_tb0012` exits 1 in BOTH m3 AND m4.** The addendum's
"m3 PASS rc=0" cell was measured against a binary the freshness guard would have refused: `git pull
--rebase` had replayed `src/emitter/emit.cpp` with a new mtime (05:42) onto a binary built at 05:37,
and I ran `./scrip` DIRECTLY, which bypasses the `util_require_fresh.sh` guard that every runner goes
through for exactly this reason. Re-taken at `dff0f6e26` with the guard run first and `find src
Makefile -newer scrip` returning EMPTY:

| shape (all flat program bodies) | m3 | m4 | verdict |
|---|---|---|---|
| `1210.0 = 1210.0` literal pair (`teq2.pas`) | `error 102 / &null` | `error 102 / &null` | CRASH, both media |
| `1210.0 < 1211.0` literal pair | `error 102 / &null` | -- | CRASH |
| `x = y`, two real VARIABLES | `error 102 / &null` | -- | CRASH |
| `stemp <> 1210.0`, var vs literal (`tbs_tb0012`) | correct stdout, **rc=1** | correct stdout, **rc=1** | **SILENT WRONG ANSWER, both media** |
| same literal pair inside a PROCEDURE (`H.pas`) | `EQ` | -- | PASS (pinned frame) |
| integer pair, flat (`I.pas`) | `EQ` | -- | PASS |

⭐ **WHAT SURVIVES, AND IT IS THE PART THAT MATTERED:** hq_pascal's original reading was CORRECT AS
THEY WROTE IT -- the witness no longer crashes and now silently evaluates the comparison to the wrong
boolean and halts, in both media. My "mode split" was the artifact. The load-bearing consequences are
unchanged and one of them is strengthened by there being no split:
1. **IT IS A SILENT WRONG ANSWER, NOT A CRASH, AND THE STDOUT IS CORRECT IN BOTH MEDIA.** A comparator
   that grades stdout alone reads this witness as PASSING in m3 and m4. The arm must grade the EXIT
   CODE. That was true when I thought it was one medium and it is twice as true across both.
2. The four-cell structure of the body of this finding is UNAFFECTED: flat-vs-pinned is still the
   axis, the literal pair still crashes in both media, the procedure control still prints `EQ`, and
   the integer control still passes. Nothing in the mechanism section rested on the split.
3. The operand-shape observation stands -- a literal pair faults on an unmapped address while a
   variable-vs-literal pair reads an address that is wrong but mapped and returns a false comparison
   -- but it is now a statement about OPERAND SHAPE ALONE, with no medium in it.

⛔ **THE PROCESS FAILURE, NAMED BECAUSE IT IS THE REUSABLE PART:** every runner in this tree reaches
`./scrip` through `util_require_fresh.sh`, whose whole purpose is to turn a stale binary into an rc=2
REFUSAL instead of a reading. I invoked the binary by hand, got a reading, and published it to two
seats and this file within the same ten minutes. **A hand-run `./scrip` is an ungated instrument, and
after a `git pull --rebase` it is a KNOWN-BAD one** -- the rebase-mtime shape is documented in this
seat's own CLAUDE.md and I had quoted it to two other seats in telegrams the same hour while my own
measurement was sitting on the wrong side of it. Run the guard, or run through a runner.
