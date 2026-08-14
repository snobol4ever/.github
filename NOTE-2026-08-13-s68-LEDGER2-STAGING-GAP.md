# NOTE s68 — LEDGER 2's "ONE STAGING CHOKE" IS 29 OF 108 ARMS, AND EVERY SET-A CARVER IS OUTSIDE IT

Measured at SCRIP `b7793080` (HEAD as cloned), corpus `9c96a110`, clean build, 0 errors, gdb 15.1 present.
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

## NEXT — THE STATEMENT HALF, LON'S RULING WANTED

(a) **Close the staging gap** — make the choke actually one choke (call `bb_prepare` for every arm, or hoist
it to the head of `walk_bb_node_inner`). Cheap, byte-inert when `SCRIP_CLASS_DIAG=0` (the staging write is
`g_emit.op_frame_need`, currently DORMANT/no reader — must be verified, not assumed).
(b) **Then extend the verdict map** so the newly-visible carvers get a real verdict instead of `default: 0`.

⛔ (a) before (b): with 79 arms unstaged, any verdict-map work is untestable — you cannot measure a verdict
for a node the classifier never sees. ⛔ Gate for either: mode-4 asm md5 DIAG=1 == DIAG=0 (byte-inert), plus
the compile-time md5 blast radius over the corpus (s66's method), NOT a single board run (noise floor ~5).
