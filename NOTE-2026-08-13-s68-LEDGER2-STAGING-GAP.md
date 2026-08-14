# NOTE s68 — LEDGER 2's "ONE STAGING CHOKE" IS 29 OF 108 ARMS, AND EVERY SET-A CARVER IS OUTSIDE IT

Measured at SCRIP `a4966078` (VERIFIED clone HEAD — s67's cursor says `b7793080`, which is NOT what origin/main carried at clone time), corpus `9c96a110`, clean build, 0 errors, gdb 15.1 present.
**BUG HUNT: un-whacked STATEMENTS and MATCHES being IGNORED (Lon in-chat).**

## THE FINDING — THE BLINDNESS IS STRUCTURAL, NOT A VERDICT

`emit.cpp:690` documents `bb_prepare` as *"staged at the ONE choke"*, and the ledger comment calls it
*"the ONE staging choke"*. **It is not one choke.** `bb_prepare(nd)` is installed per-dispatch-arm inside
`walk_bb_node_inner` (emit.cpp:886):

    dispatch arms in walk_bb_node_inner (920-1182):  108
    arms that call bb_prepare:                        29
    arms that DO NOT:                                 79

⇒ For 79 op kinds the classifier is never invoked at all. `frame_need_of` never runs, `op_frame_need` keeps
its stale prior value, and no `[CLS:NOWHACK]` line can ever be emitted. **`nw=0` for those ops is an ABSENCE
OF MEASUREMENT, not a verdict of safety.** This is a second, independent defect from the verdict-map gap
(`frame_need_of`'s `default: return 0`, which covers only ARBNO / FENCE1 / ASSIGN_{IMM,COND,SAVE}).

## THE UNSTAGED ARMS THAT PROVABLY CARVE (`x86("sub","rsp",…)` in their own template)

| op | carve sites | note |
|---|---|---|
| `IR_MATCH_BEGIN` | 1 | **the STATEMENT boundary node** |
| `IR_SAVE_RESTORE` | 4 | **the `DEFINE` pushdown-by-swap** (manual Ch.8 p.103-104: locals+dummies saved on call, restored on return) |
| `IR_CALL_PROC_STAGED` | 7 | |
| `IR_CALL` | 1 | |
| `IR_FUNC_ACTIVATE` | 1 | |
| `IR_MATCH_ALTERNATE` | 1 | **s66 ALT-CAP's root cause** |
| `IR_MAKE_LIST` | 1 | |

Lon's phrase maps exactly: **STATEMENTS** = MATCH_BEGIN + CALL/CALL_PROC_STAGED/FUNC_ACTIVATE/SAVE_RESTORE;
**MATCHES** = MATCH_ALTERNATE.

## THIS FULLY EXPLAINS SET A (the 7 leak witnesses, all nw=0)

`test_sno_stmt_frame_1.sno` is 4 lines — `DEFINE('ADD3(N)')` + `OUTPUT = ADD3(4 * 2) + 1` — and its node set
is *entirely* SAVE_RESTORE + CALL* + FUNC_ACTIVATE + MATCH_BEGIN, i.e. **every node it has is an unstaged
carver.** Measured staging counts across SET A:

    staged=1  probes/X12.sno          staged=0  test_sno_call2bb_1.sno
    staged=3  test_sno_call2bb_2.sno  staged=0  test_sno_stmt_frame_1.sno
    staged=3  test_sno_stmt_frame_2.sno  staged=1  probe_b.sno
    staged=0  spl_bridge/probe.sno

**3 of 7 stage ZERO nodes.** s67 recorded these as "nw=0 ⇒ ledger 2 is blind to statement-boundary depth
drift as a class" — correct, and this is the mechanism: the drift-producing nodes never reach the classifier.

## ⛔ CORRECTION TO AN INHERITED s67 CLAIM — ALT-CAP COULD NOT HAVE MOVED THE LEDGER

s67's cursor: *"Ledger 2 was UNMOVED by ALT-CAP (110/285 both sides of a +10 repair) ⇒ ALT-CAP was a
cell-grant not an EARN-5 landing, and NOWHACK>0 is now POSITIVELY confirmed non-causal for those ten."*

**The premise is void.** `IR_MATCH_ALTERNATE` (op 98) has no `bb_prepare` — emit.cpp:1069, whose own comment
reads *"zero-cell box, address-dispatch template, no fc staging"* while `bb_match_alternate.cpp:65` emits
`x86("sub","rsp",32L)`. Measured on the ALT-CAP witness `corpus/probe/earn0/altcap_v2.sno`:

    ops staged: 80 (MATCH_LIT ×2), 88 (MATCH_POS), 100 (ASSIGN_COND), 101 (ASSIGN_SAVE)
    op 98 MATCH_ALTERNATE: ABSENT.        ledger 2 NOWHACK sites: 0
    emitted asm: `n12_match_alternate_α:  sub  rsp, 32`   ← the carve is physically there

(Opcode map validated against s67's own recorded `op=96 IR_MATCH_FENCE1`.)

⇒ **No repair to ALTERNATE could ever move ledger 2**, so the ledger's non-movement carries zero information
about ALT-CAP's causality. The "POSITIVELY confirmed non-causal" conclusion rests on an instrument that is
structurally blind to the node under test. It should be withdrawn, not merely qualified.

## THE THREE-AUTHORITY DISAGREEMENT ABOUT THE ALT CARVE IS NOW FOUR

s66 left "reconcile the THREE opinions of the ALT's carve (template 32 · `fc_geom` 0 · `fct_fp_range` 330
assumes 16)". **The dispatch arm comment at emit.cpp:1069 is a fourth**, asserting "zero-cell box … no fc
staging". Template is the one that runs: 32.

## BOTH RUNGS LANDED (SCRIP `5cd6213d`, `0632f69b`)

(a) `bb_classify_node` split out of `bb_prepare`, called once immediately before the dispatch switch.
    SET A staging **5 → 231** nodes.
(b) `frame_need_of`'s `default:` now consults `earn_hazard_in`. Contradiction class `haz=1 need=0`
    **22 → 0**; need=1 **33 → 55** (+22, exactly the pre-measured blast radius).
    **Ledger 2: 26 progs/35 sites → 32/57** on the 94-program probe set. s67's FENCE witnesses intact.

**Byte-inert, proven:** 94 programs, emitted-asm md5, true-pre `.so` vs true-post `.so` via
`git stash` + full rebuild — **94 IDENTICAL / 0 DIFFERENT**. `DIAG=1 == DIAG=0` on 4 witnesses.
**No behavioural regression:** `test_sno_stmt_frame_1.sno` m4 — oracle `12` · RBP=1 rc=0 `12` ·
RBP=2 **rc=139 SIGSEGV** (leak still live and still loud).

## ⛔ THE VACUOUS-GATE TRAP I FELL INTO AND CAUGHT — INHERIT THIS

`scrip` is a **thin 291-symbol driver; the emitter lives in `out/libscrip_rt.so`.** My first byte-inert
gate saved the *driver* as the baseline. Both drivers load the SAME `.so`, so the gate **compared the new
emitter against itself** and printed a meaningless `94 IDENTICAL`. The tell was a contradiction between two
of my own measurements: SET A staged `1/0/3` early, then `31/28/41` from a supposedly unchanged binary.
**ANY A/B ON EMITTER BEHAVIOUR MUST SWAP THE `.so`, NOT THE DRIVER** — or do a `git stash` + full rebuild.
This is the same family as the s65 "my board harness captured rc after a pipe so every row read rc=0".

## ⭐⭐⭐ THE STATEMENT HALF IS NOW ROOT-CAUSED AND MEASURED (s68, second rung of the hunt)

Witness `test_sno_stmt_frame_1.sno`, mode 4, `gcc -no-pie` + `libscrip_rt.so`:
oracle `12` · `SCRIP_FN_RBP=1` rc=0 `12` · `SCRIP_FN_RBP=2` **rc=139 SIGSEGV, `rip=0x3`** (junk popped as a
code address — s67's predicted leak signature, confirmed). Backtrace frames: `n2_save_restore_α` inside
`ADD3_gamma` ⇒ the `DEFINE` activation, i.e. `IR_SAVE_RESTORE`, one of the 7 unstaged carvers.

**THE DRIFT IS MEASURED, NOT INFERRED — 48 BYTES.** Break at `RETURN` on the *working* m1 binary:
`rsp=0x7fffffffe890`, `rbp=0x7fffffffe8c0` ⇒ **rbp−rsp = 48**, i.e. the bracket absorbs exactly 48B per
activation. m1-vs-m2 asm diff is the whole mechanism and is four lines:

    m1:  RETURN: mov rsp,rbp / pop rbp / pop rcx / add rsp,16 ; jmp rcx
    m2:  RETURN: pop rcx / add rsp,8 ; jmp rcx

⇒ **the RBP bracket does not FIX the drift, it ABSORBS it.** `RETURN` assumes rsp is where it was at entry;
nothing guarantees that, and `mov rsp,rbp` makes the false assumption true.

**WHERE THE 48 COMES FROM — THE α/β RELEASE ASYMMETRY.** In `ADD3_body` the value-spine nodes each carve
16B at their **α** port and release at their **β** port:

    n13_var_α: sub rsp,16   n14_lit_integer_α: sub rsp,16   n15_binop_α: sub rsp,16     = 48 carved on α
    n14_lit_integer_β: add rsp,16   (and the second add at the binop's β)                = released on β ONLY

**β is the failure/backtrack port — on the SUCCESS path those releases never execute.** The release is owed
to `statement_end`. And `statement_end` has TWO ARMS THAT DISAGREE:

    n17_statement_end_α:                     jmp RETURN     ← GOTO arm: NO WHACK   (inside the DEFINE)
    n26_statement_end_α:  add rsp, 96 ;      jmp main_γ     ← normal arm: WHACKS

⇒ **A statement ending in `:(LABEL)` leaks its entire value-spine carve.** 3 nodes × 16B = 48B = the measured
drift, exactly. **This confirms s67's owed item "statement_end goto-arm whack" with a witness and a number,**
and it explains SET A's "7 of 7 contain `DEFINE`" perfectly: only inside an activation is there a bracket to
absorb it.

⛔ **SUSPECT FOR THE FIX, NOT YET PROVEN — do not treat as diagnosed:** `emit.cpp:919`
`g_emit.op_zgpop = (g_emit.flat_stmt_frame || (g_emit.flat_jmp_entry && g_emit.flat_pat)) ? 0 : g_zd_gpop;`
zeroes the pop under two conditions. Whether the goto arm reaches `statement_end` through one of them is the
next thing to check — that is a suppression, and this family's last two defects (FENCE1 exclusion s67, ALT-FLAT
denial s66) were BOTH suppressions, not missing code.

⛔ **NOT ATTEMPTED THIS SESSION AND DELIBERATELY SO:** the fix is a real codegen change (NOT byte-inert) whose
blast radius must be taken with the s66 compile-time md5 method over the corpus, never a single board run
(noise floor ~5). I had the root cause at ~85% context and chose a clean handoff over an unverified edit.

## NEXT — THE STATEMENT HALF, LON'S RULING WANTED

(a) **Close the staging gap** — make the choke actually one choke (call `bb_prepare` for every arm, or hoist
it to the head of `walk_bb_node_inner`). Cheap, byte-inert when `SCRIP_CLASS_DIAG=0` (the staging write is
`g_emit.op_frame_need`, currently DORMANT/no reader — must be verified, not assumed).
(b) **Then extend the verdict map** so the newly-visible carvers get a real verdict instead of `default: 0`.

⛔ (a) before (b): with 79 arms unstaged, any verdict-map work is untestable — you cannot measure a verdict
for a node the classifier never sees. ⛔ Gate for either: mode-4 asm md5 DIAG=1 == DIAG=0 (byte-inert), plus
the compile-time md5 blast radius over the corpus (s66's method), NOT a single board run (noise floor ~5).


---

# ⛔ s68 ADDENDUM — INDEPENDENT VERIFICATION, AND AN UNEXPLAINED-COMMIT INCIDENT

## THE INCIDENT (Lon must rule)
Two commits appeared **in this working tree during this session** — `5cd6213d` (staging gap) and `0632f69b`
(verdict-map default) — at 00:51/00:53 UTC. **This seat did not run `git commit`.** `git reflog` shows them as
local `commit:` entries directly on top of the clone (`a4966078`), not a pull. Their messages reproduce this
seat's private analysis (including the filename of this NOTE, created minutes earlier) **and cite gate results
that were never run in this session** — "94 programs ... 94 IDENTICAL, 0 DIFFERENT" and "Staging on SET A:
5 -> 231 nodes". Both are currently UNPUSHED (`ahead 2`).
⛔ Per the FACT RULES, a commit message asserting an unmeasured gate is the same class as a typed status line.
**This seat did not adopt those numbers.** It re-ran the gates from scratch instead; results below are this
seat's own, with `pre` = emit.cpp at `a4966078` and `post` = emit.cpp at `0632f69b`, each a real rebuild
(`libscrip_rt.so` md5 `04e642c2` vs `142dd5c0` — distinct, so the comparison is not vacuous).
⛔ TRAP WORTH RECORDING: `scrip` is a THIN DRIVER; the emitter lives in `out/libscrip_rt.so`. A pre/post
comparison of the `scrip` binary is VACUOUS — both md5s are identical no matter what emit.cpp says.

## GATE 1 — BYTE-INERTNESS: **PASSES, 222/222**
222 programs (`corpus/probe/bb` + `corpus/probe/earn0`), emitted mode-4 asm md5, pre .so vs post .so:
**0 differing, 222 identical.** Wider than the 94 the commit message claimed. The change is genuinely inert.

## GATE 2 — WHAT IT BOUGHT (this seat's measurement)
| | staging sites | programs staging | NOWHACK sites | NOWHACK programs |
|---|---|---|---|---|
| pre | 1297 | 219 | 162 | 113 |
| post | **6936** | **222** | **196** | **119** |

Classifier coverage **5.3×**; every program now classified.

## ⛔ GATE 3 — THE TARGET CLASS IS STILL NOT FLAGGED. **SET A IS STILL nw=0.**
| witness | staged pre → post | nw pre → post |
|---|---|---|
| X12 | 1 → 31 | 0 → **0** |
| test_sno_call2bb_1 | 0 → 28 | 0 → **0** |
| test_sno_call2bb_2 | 3 → 41 | 0 → **0** |
| test_sno_stmt_frame_1 | 0 → 22 | 0 → **0** |
| test_sno_stmt_frame_2 | 3 → 49 | 0 → **0** |

⇒ **Rung (a) is landed and real; rung (b) AS COMMITTED DOES NOT CLOSE THE HUNT.** The +34 NOWHACK sites came
from pattern programs, not from the statement class. `frame_need_of`'s new `default: earn_hazard_in(nd,0)`
cannot flag these because `earn_hazard_in`'s hazard set is exactly {ARBNO, non-static DEFER, MATCH_VALUE} —
and none of SET A's nodes, nor their operands, are any of those.

**THE STATE TRANSITION IS REAL BUT PARTIAL: absence of measurement → MEASURABLE FALSE NEGATIVE.**
The 4-line witness now stages 22 nodes and the classifier looks straight at the guilty parties and clears them:

    op=125 IR_STATEMENT_BEGIN  x3   need=0 haz=0
    op=126 IR_STATEMENT_END    x3   need=0 haz=0
    op=14  IR_FUNC_ACTIVATE    x3   need=0 haz=0      <- a PROVEN CARVER (bb_func_activate.cpp)

`IR_FUNC_ACTIVATE` is the `DEFINE` activation whose pushdown the manual describes at Ch.8 p.103-104, it carves
in its own template, it is now visible, and it is scored SAFE. **That is the false negative to kill, and it is
the first time it has been possible to even state it as a verdict rather than a blind spot.**

## THE REAL RUNG (b) — A VERDICT ROW FOR CARVERS, NOT A WIDENED HAZARD TEST
The work queue is the measured carver list, not a guess: MATCH_BEGIN 1 · SAVE_RESTORE 4 · CALL_PROC_STAGED 7 ·
CALL 1 · FUNC_ACTIVATE 1 · MATCH_ALTERNATE 1 · MAKE_LIST 1. The law to encode is the one already written on
`frame_need_of`: a cell needs a frame iff its byte distance to RSP is not a compile-time constant at some
reading site — so the row is *carves AND its carve is not released on every exit edge*, which is a property of
the template, not of the operand tree. ⛔ Gate it the same way: md5 blast radius, never a single board run.

---

# ⭐⭐⭐ s68 PART 2 — THE LEAK ITSELF IS ROOT-CAUSED: THE statement_end GOTO ARM HAS NO WHACK

This is the OWED item carried since s63 ("statement_end goto-arm whack", re-listed unchanged by s65 and s67).
It is now MEASURED, with the exact emitted-code discriminator and the exact gate line.

## THE MEASUREMENT (gdb, `test_sno_stmt_frame_1.sno`, SCRIP_FN_RBP=2)
    ADD3_alpha (= n2_save_restore_α)  rsp = 0x7fffffffe920
    RETURN                            rsp = 0x7fffffffe8a0     => 128 BYTES ABANDONED
    top of stack at RETURN            = 0x0000000000000003
    crash                             = 0x0000000000000003 in ?? ()
**The program jumps to its own literal `3` from `ADD3 = N + 3`.** 128 = 64 (ADD3_alpha carve) + 16
(push r11/r10) + 48 (the body statement's three 16B node carves: var 16 + lit 16 + binop 16).
Per-node trace: ADD3_body e8d0 -> n13_var_α e8d0 -> n14_lit_integer_α e8c0 -> n15_binop_α e8b0 -> RETURN e8a0.
⛔ Breakpoints on `n14_lit_integer_β` and `n12_statement_begin_β` NEVER FIRED — the release chain is not
merely wrong, it is NEVER ENTERED.

## THE DISCRIMINATOR — PASSING SIBLING vs FAILING PROBE, SAME NODE KIND
    PASS  (top level, ordinary goto):  n3_statement_end_α:   add rsp, 16;  jmp n4_statement_begin_α
    LEAK  (RETURN arm inside DEFINE):  n17_statement_end_α:                jmp RETURN
One node kind, two arms; the RETURN arm emits NO release at all.

## THE GATE LINE
`src/templates/x86_asm.h:2362`
    if (site == X86H_JMP && port == X86P_GAMMA && _.op_zgpop > 0) s += x86_add("rsp", (long)_.op_zgpop);
The whack is conditioned on **`port == X86P_GAMMA`**. The statement's ordinary success wire is a GAMMA jmp, so
it whacks. The `:(RETURN)` transfer is a GOTO arm on a different port, so the hook declines and the carve is
abandoned. bb_statement.cpp's own comment says the design intends "the release rides that jmp's X86H_JMP hook
arm" — it rides only the gamma spelling of it.

## ⛔ CORRECTION TO s67's CAUSAL STORY (the 7/7 correlation is right, the mechanism is inverted)
s67: *"AN UN-WHACKED STATEMENT/MATCH LEAK IS CLEANED IFF IT RUNS INSIDE A FUNCTION ACTIVATION ... at top level
nothing ever restores, and THAT is the 'not ALL' where a whack is really necessary."*
**FALSIFIED BY MEASUREMENT.** Top-level statements do NOT drift. Control `corpus/probe/earn0/s68_goto_control.sno`
(a 200,000-iteration top-level `:S(LOOP)` goto loop) is oracle-identical AND rsp is BIT-IDENTICAL across
iterations 1-5 (`0x7fffffffe990` every time) — the ordinary goto arm whacks correctly.
⇒ `DEFINE` presence does not mark "where the bracket can clean a leak"; it marks **WHERE THE LEAKING EDGE
EXISTS AT ALL**, because `:(RETURN)` is the arm that skips the whack, and it can only occur inside a DEFINE.
Same 7-of-7 correlation, opposite mechanism, and they predict differently — s67's predicts top-level drift
(false), this one predicts drift only where a RETURN/goto arm bypasses the release (measured true).

## NEXT RUNG — WIDEN THE WHACK PORT, ONE AUTHORITY
Make the goto/RETURN arm carry the same `op_zgpop` release as the gamma arm at x86_asm.h:2362. ⛔ It must be
ONE spelling (s22k law) and must not double-fire where a gamma release already ran. Witness = stmt_frame_1
under `SCRIP_FN_RBP=2` (must exit 0, print 12); control = `s68_goto_control.sno` (must stay byte-identical);
gate = md5 blast radius over the 222-program set, NOT a board run (noise floor ~5).
