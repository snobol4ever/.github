# FINDING s190 (seat3, `/home/claude3`, Claude Opus 5) — queue row `beauty-return-pair-shift`

## ⛔ THE HEADLINE: THE PAIR IS NOT SHIFTED AND THE OMEGA UNWIND DOES NOT LEAK. **rsp IS CORRECT AT THE POP; THE 16 BYTES IT POPS WERE NEVER A PAIR** — AND THE INSTRUMENT THE BRIEF SENDS YOU TO IS BLIND IN THE DIRECTION THAT MATTERS ANYWAY.

The brief's step 2 says *"grep the census/ring for the FIRST omega imbalance before the crash (`RSP LEAK`, `rsp still`, `IMBALANCE`, `skew`) — the omega arm of `rt_zdp_sm_event` already measures rsp@omega vs rsp@alpha"*. It does — **in one direction only.** The ω arm's release test is literally `if (rsp < e->rsp_a)`, i.e. *"carved and never released"*. **Over-release — rsp climbed ABOVE where α stood — was invisible BY CONSTRUCTION, and over-release is how beauty dies.** A seat following step 2 to the letter finds a clean census and concludes there is no imbalance. There isn't one *of the kind the instrument tests for*. Armed with the other direction (`SCRIP_ZSM_OVERPOP=1`, landed SCRIP `2cf31532`), the same run reports **1094 over-releases** it previously could not see.

## THE MINIMAL WITNESS — ONE EMPTY LINE, AND A COMMENT LINE IS GREEN

`m1_min.in` is not near-minimal, it *is* minimal, and bisecting the **input** (not the program) says exactly which road is broken:

| stdin to `scrip --run beauty.sno` | rc | output |
|---|---|---|
| empty file (0 bytes) | **0** | (none — correct) |
| `* comment\n` | **0** | `* comment` — **correct identity** |
| `head -5 beauty.sno` | **0** | 235 bytes, correct |
| **`\n` (one empty line)** | **139** | **zero bytes** |
| `' '\n` (one space) | 139 | zero bytes |
| `\tX = 1\n` | 139 | zero bytes |
| `END\n` | 139 | zero bytes |
| `head -10 beauty.sno` | 139 | zero bytes |

Oracle (`sbl -bf`) answers the identity, rc=0, on every one. **beauty's COMMENT road is green and its NON-COMMENT road SEGVs before emitting a single byte** — so the wall is not "an empty line", it is *any line that reaches the statement parse*. All eight `m1_lad_*.in` ladder rungs are the same rc=139, i.e. the ladder is not bracketing eight defects, it is showing one wall eight times.

## ⛔⛔ CORRECTED IN PLACE (same session, before any seat could inherit it): MY FIRST WRITE-UP OF THIS SECTION SAID "IR_STATEMENT_END DOUBLE-RELEASES 96 BYTES". **THAT IS FALSE AND I FALSIFIED IT MYSELF — STATEMENT_END'S RELEASE IS EXACT.**

I read the ring's `depth` column as "nothing carved" at STATEMENT_END's α. **`depth` is noise here and the file says so:** `g_zsm_rsp0` is ONE cell, re-based by every nested graph, and the last `ORIGIN` before the crash belongs to a *different* graph (`op=59 IR_MATCH_ASSIGN_IMM`, st=961). The raw rsp values are the only trustworthy column, and they say the opposite of what I first wrote. **Kept visible rather than silently rewritten, per STALE-ORIENTATION: a seat who saw the first version must be able to see it retracted.**

## THE MECHANISM, WITH THE NUMBERS (re-derived from raw rsp only)

The DEFINE call protocol, read out of the emitted TEXT (`--compile`, not inferred) — and all 255 DEFINEs are this shape:

```
InitCounter_α:  sub rsp, 48                     ; activation frame
                lea r10, [rip + InitCounter_γ]
                lea r11, [rip + InitCounter_ω]
                push r11                        ; ω  -> [rsp+8]
                push r10                        ; γ  -> [rsp+0]
                jmp rax                         ; enter body -- rsp now POINTS AT the pair
RETURN:   pop rcx ; add rsp, 8 ; jmp rcx        ; γ at [rsp+0], drop ω   <-- DEPTH-EXACT
FRETURN:  add rsp, 8 ; pop rcx ; jmp rcx        ; drop γ, ω at [rsp+8]
```

**So the pair sits AT the body's statement frontier and the body carves strictly below it.** The ring at the crash (minimal witness, raw rsp; `#n` = port index in the last-60 window):

```
#12  α· op=36  IR_GOTO_DEFERRED    rsp=0x…8b30  rbp=0x…8e20  st=956   <-- the transfer in
#13  α· op=113 IR_STATEMENT_BEGIN  rsp=0x…8860  rbp=0x…89d0  st=956   <-- frontier, 720B below
#15  α· op=125 IR_VAR              rsp=0x…8850  st=961                <-- subject cell
#17  α  op=63  IR_MATCH_BEGIN      rsp=0x…8850  st=961
#21  α· op=67  IR_MATCH_DEFER      rsp=0x…8800
#22  ORIGIN    op=59 IR_MATCH_ASSIGN_IMM rsp=0x…8800                  <-- datum re-based HERE
#31  α· op=80  IR_MATCH_SPAN       rsp=0x…8760
#32  ω· op=80  IR_MATCH_SPAN       rsp=0x…8790                        <-- THE MATCH FAILS
#33  ω· op=67  IR_MATCH_DEFER      rsp=0x…8810
#34  β  op=63  IR_MATCH_BEGIN      rsp=0x…8810
#35  ω  op=63  IR_MATCH_BEGIN      rsp=0x…8860                        <-- back to frontier, exact
#58  α· op=114 IR_STATEMENT_END    rsp=0x…8800  st=969
#59  γ· op=114 IR_STATEMENT_END    rsp=0x…8860                        <-- 96 = 6 cells x 16, EXACT
#60  α· op=25  IR_DEFINE           rsp=0x…8860  st=969                <-- RETURN floater
```

**Every release on this road is arithmetically exact.** The frontier is `0x…8860` and it is stable across st=956/961/963/969. MATCH_BEGIN's ω returns to it. STATEMENT_END's 96 is exactly the six cells its statement carved (`IR_VAR, IR_CALL, IR_VAR, IR_COERCE_NUMERIC ×2, IR_CMP_TEST` — 6 × 16 = 96, `0x8800` → `0x8860`). **rsp is CORRECT at the `pop rcx`.**

**The defect is therefore not WHERE the floater pops — it is that the 16 bytes AT the frontier are not a pair.** `[0x…8860] = 0x7ffff7ffd000` (ld.so rw data), `[0x…8868] = 0x41bd68` (scrip `.fini_array` base). Not code, not `_γ`/`_ω`, not in any executable mapping.

## ⭐ THE LEADING HYPOTHESIS, STATED AS A HYPOTHESIS: THE PAIR WAS NEVER PUSHED ON THIS ENTRY PATH

**The transfer into this body at `#12` is `IR_GOTO_DEFERRED`, not a call — and NO `IR_DEFINE` α event fires between it and the RETURN floater at `#60`** (grep-verified: the only `op=25` in the whole 60-port window is `#60` itself; 24 `op=25` events in the entire 2048-port ring). The pair is pushed by `IR_DEFINE`'s α and by nothing else. If no DEFINE α ran on this path, **nothing ever wrote those 16 bytes and `RETURN` is popping stack that was simply never initialised** — which is exactly what a slot holding two unrelated loader/image addresses looks like.

⛔ **NOT YET PROVEN, and the honest gap:** `rbp` does move (`0x…8e20` → `0x…89d0`) and rsp drops 720 bytes between `#12` and `#13`, so *something* established a frame there — more than a bare goto explains, and no instrumented port accounts for it. The competing hypothesis (pair pushed, then clobbered) is not excluded. **The one measurement that decides it:** break at the last `IR_DEFINE` α preceding the crash and check whether it writes `0x…8860`, or set a software watchpoint on that address once the frontier is established. I did not get to it.

## ⛔ WHAT THE BRIEF GOT WRONG — BOTH CLAIMS, MEASURED

**(1) "The `{gamma,omega}` pair is not missing, it is SHIFTED … a REAL scrip continuation ONE SLOT BELOW (`0x41bd68`)."** `0x41bd68` is **exactly the base of scrip's `.fini_array`** (`readelf -S scrip`: `[21] .fini_array FINI_ARRAY 000000000041bd68`) — static DATA in the compiler's own image, and `__do_global_dtors_aux_fini_array_entry` on the nose. The other quad, `0x7ffff7ffd000`, is ld.so's rw data page (`_rtld_global`). **Neither is a `_γ`/`_ω` label, neither is in any executable mapping.** The popped 16 bytes are not a shifted pair; they are not a pair. (They are also not startup garbage — I checked that too, and it is false: at `main` entry those slots read `0x0`, so the program genuinely wrote them.) The stack immediately below is a clean run of 16-byte DESCRs — `{3,0} {3,0x400} {3,0} {3,0x400} {3,0} {2,ptr}` — which is the same tag-3/tag-2 statement-cell signature `bb_match_replace.cpp:37` already records for this exact failure ("the floater's pop rcx loaded a statement cell descr tagword 0x300000002 and jumped into it").

**(2) "Prime suspect: the conceded match's omega unwind leaks slots; law 0b omega-balance."** A full `SCRIP_ZSM_ALL` census — **26,063 port events, 36 distinct IR kinds** — reports **ZERO** `RSP LEAK`, **ZERO** ω `IMBALANCE`, zero β `FRAME LOST`. The only violations are **8** γ· rbp skews, every one the known-benign whack-owner shape the γ arm already documents. There is no omega leak to find. See the headline: the arm cannot test the failing direction.

**Also exonerated:** `bcps_wire_pair_consumed` / `SCRIP_WIRE_PAIR_FRAME` (`bb_call_proc_staged.cpp:39`) looked like the perfect suspect — its own comment describes a caller/callee disagreement that "shifts every later rsp-relative reference in the caller". **A/B measured: `SCRIP_WIRE_PAIR_FRAME=0` and `=1` are both rc=139, same `_rtld_global`.** Not this.

## THE CLASS — AND IT IS ALREADY WRITTEN DOWN, WITH THE OPPOSITE SIGN

`bb_match_replace.cpp:37` (R-3(c), "the DEFINE RETURN-linkage root cause") records the mirror image: a subtree's `op_zdepth` bytes "released by NOBODY", so `RETURN` was reached **16 bytes low**. Here the same seam is reached **96 bytes high**, released by *two* parties. Its closing sentence is the law this whole row lives under: **"Main-shaped graphs tolerated the leak silently (the s97 INCLUDE-leak flavor); the RETURN floater's depth-exact pop could not."** Any disagreement between the ζ-depth planner's model of a DEFINE body and the body's actual carve — in *either* direction — lands on `RETURN`, and only inside a DEFINE, which is why beauty is where it shows.

## RECEIPTS (this tree, RT_OPT `-O0`, SCRIP `2cf31532`, pushed)

- corpus board `test_corpus_snobol4.sh`: **m3 PASS=332 FAIL=5 · m4 PASS=325 FAIL=11 SKIP=1 (337)** — the brief's baseline exactly, fail-set identical by name.
- `board_beauty_m1.sh --modes m3`: **3/10 green, first red at 10** — unchanged; this session did not move it and does not claim to.
- `beauty.sno --compile` **byte-identical before/after the patch** (172,891 lines). The knob is unreachable unless `SCRIP_ZSM=1` and silent unless `SCRIP_ZSM_OVERPOP=1`.
- gdb 15.1 live via `install_system_packages.sh`; `SCRIP_NO_SEGV_HANDLER=1` for clean backtraces; no hardware watchpoints used.

## ⛔ NAMED, NOT FIXED — AND WHY I DID NOT PATCH IT

There is **no leaking box** — that was the first write-up's error, retracted above. Every release on the failure road is exact. What is named instead is the SHAPE: **a `RETURN` whose depth-exact pop is served by an entry path (`IR_GOTO_DEFERRED`) on which no `IR_DEFINE` α is recorded.** Until the never-pushed-vs-clobbered question is decided by the measurement named above, any patch would be aimed at a guess. ⛔ In particular do NOT clamp STATEMENT_END's `K`: its release is arithmetically exact, and clamping it would be the op-filter shape RULES bans while breaking a correct box.

## SUGGESTED ROWS (asked, not worked)

1. **`define-pair-never-pushed`** (supersedes the double-release row I first proposed, which rested on the retracted reading) — decide never-pushed vs clobbered for the 16 bytes at the frontier, then follow `IR_GOTO_DEFERRED` as an entry path into a DEFINE body: does it establish an activation, and if so who pushes the {γ,ω} pair on that road?
2. **`zsm-overpop-triage`** — 1094 over-releases are now visible and most are legitimate whack-owners. A predicate that separates "whack-owner retiring an enclosing construct frame" from "double release" turns the new knob from a candidate list into a verdict.
3. **`m1-ladder-is-one-wall`** — all 8 `m1_lad_*` rungs are the same rc=139; the ladder currently bills one defect eight times and its first-red number cannot move until this seam does.
