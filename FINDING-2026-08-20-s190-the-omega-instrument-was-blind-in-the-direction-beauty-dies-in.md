# FINDING s190 (seat3, `/home/claude3`, Claude Opus 5) — queue row `beauty-return-pair-shift`

## ⛔ THE HEADLINE: THE PAIR IS NOT SHIFTED AND THE OMEGA UNWIND DOES NOT LEAK. `IR_STATEMENT_END` RELEASES 96 BYTES WHILE STANDING AT DEPTH **ZERO**, AND THE INSTRUMENT THE BRIEF SENDS YOU TO CANNOT SEE THAT DIRECTION BY CONSTRUCTION.

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

## THE MECHANISM, WITH THE NUMBERS

The DEFINE call protocol, read out of the emitted TEXT (`--compile`, not inferred) — `InitCounter_α`, and every one of the 255 DEFINEs is the same shape:

```
InitCounter_α:  sub rsp, 48                     ; activation frame
                ... save-set into frame ...
                lea r10, [rip + InitCounter_γ]
                lea r11, [rip + InitCounter_ω]
                push r11                        ; ω  -> [rsp+8]
                push r10                        ; γ  -> [rsp+0]
                jmp rax                         ; enter body
```

and the ONE shared floater the whole program returns through:

```
RETURN:   pop rcx
          add rsp, 8;   jmp rcx        ; takes γ at [rsp+0], drops ω
FRETURN:  add rsp, 8
          pop rcx;      jmp rcx        ; drops γ, takes ω at [rsp+8]
```

**The pair IS pushed and the protocol is coherent. `RETURN`'s pop is DEPTH-EXACT** — it assumes rsp is standing precisely where those two pushes left it. 152+ sites in beauty reach it as `statement_end_{α,β}: add rsp, K; jmp RETURN` with K ∈ {32,48,64,80,96,112,128,144,160,192,224}, and **α and β overwhelmingly carry the SAME K**.

The ZSM ring at the crash (`SCRIP_ZSM=1 SCRIP_ZSM_ALL=1`, datum `g_zsm_rsp0 = 0x7fffffff8800` stamped by the last ORIGIN):

```
α· op=15  IR_CMP_TEST       rsp=0x7fffffff8800  depth=0     st=969
γ· op=15  IR_CMP_TEST       rsp=0x7fffffff8800  depth=0     st=969
α· op=114 IR_STATEMENT_END  rsp=0x7fffffff8800  depth=0     st=969   <-- enters AT the datum
γ· op=114 IR_STATEMENT_END  rsp=0x7fffffff8860  depth=-96   st=969   <-- releases 96 bytes
α· op=25  IR_DEFINE         rsp=0x7fffffff8860  depth=-96   st=969   <-- the RETURN floater
```

**`IR_STATEMENT_END` (node 13504) enters with depth 0 — nothing of its own carved — and emits `add rsp, 96` anyway, climbing 96 bytes ABOVE the datum.** The chain immediately preceding it had already walked its own cells off, 16 bytes per γ (`0x8850 → 0x8840 → 0x8830 → 0x8820 → 0x8810 → 0x8800`, ops 125/7/125/17/17/15 = IR_VAR, IR_CALL, IR_VAR, IR_COERCE_NUMERIC ×2, IR_CMP_TEST). So the 96 bytes STATEMENT_END is billed for **were already released by the consumers themselves — this is a DOUBLE release, not an over-estimate.** Control then enters `RETURN`, whose depth-exact `pop rcx` now reads 96 bytes above the pair.

Death site, single-stepped (13 instructions after the ZSM tap returns, at the **236th** `α·op=25` event — the brief's count is right):

```
pop rax                       ; result
pop rcx                       ; rcx = 0x7ffff7ffd000
add $0x8, %rsp
jmp *%rcx                     ; -> SIGSEGV
```

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

The leaking box is named (`IR_STATEMENT_END`, releasing at depth 0 into a depth-exact floater) but **the cure belongs to the ζ-depth planner, not to `bb_statement.cpp`**, and it is a CLASS decision: either the consumers stop popping their own cells, or STATEMENT_END stops being billed for cells a consumer already took. Clamping `K` at the template would be the op-filter shape RULES bans (`NO PER-OP FILTER`) and would paper over a model/emission disagreement that main-shaped graphs are currently absorbing silently everywhere else. That is Lon's call, not a seat's.

## SUGGESTED ROWS (asked, not worked)

1. **`zd-statement-end-double-release`** — who owns the release of a consumed operand cell, the consumer's γ or STATEMENT_END's `K`? Both do today. One measurement: instrument `zeta_depth.c`'s staging against the ring's measured per-γ pops on the 6-node chain above.
2. **`zsm-overpop-triage`** — 1094 over-releases are now visible and most are legitimate whack-owners. A predicate that separates "whack-owner retiring an enclosing construct frame" from "double release" turns the new knob from a candidate list into a verdict.
3. **`m1-ladder-is-one-wall`** — all 8 `m1_lad_*` rungs are the same rc=139; the ladder currently bills one defect eight times and its first-red number cannot move until this seam does.
