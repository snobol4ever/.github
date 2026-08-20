# FINDING s170 (2026-08-19, seat8 `/home/claude8`, Claude Opus 5, CN front) — THE "ALT-ARM NESTED-SUBSTITUTION m4 CRASH" IS NOT ABOUT NESTING, NOT ABOUT SUBSTITUTION, AND NOT ABOUT CONSTANTS: IT IS THE s130/s131 LEAF-SUSPENSION CLASS, AND ITS CURE IS ALREADY BUILT AND DISARMED

**Brief executed:** queue row `cn-alt-depth` → `GOAL-SNOBOL4-100.md` s166 **SEAT-CN-3 item 1 ONLY** — *"ALT-arm nested-substitution root-cause → delete the TOP-LEVEL-ONLY depth limit (witness `probe/cn/cn_nest_alt_defer`; asm-diff u3-vs-u4 per the s161 FINDING)."* DONE-WHEN: root-cause FINDING; fix only if killswitch-clean.
**Trees:** landed at SCRIP **`924cf16a`** (over baseline `c6245f60`) · corpus **`6d7da37f`** · .github this commit. Root-caused at SCRIP `f44be5f1`; **every claim below was RE-PROVEN after the rebase** onto three other seats' commits (B1c parity default-ON, medium-retire, GC-W1), from a **`make pristine`** build (HQ-27), RT_OPT `-O0` (FACT RULE O0-DEV). Re-proof block at the bottom.

## ⛔ THE s161 FRAMING IS FALSIFIED — BOTH HALVES OF IT

`FINDING-2026-08-19-s161-CN12-constants-total-and-the-alt-arm-nested-inline-crash.md` records the defect as *"the emission mechanics of substituting mid-ALT-collection"*, and exonerates the final graph on the ground that *"its literal twin `(SPAN|SPAN)` compiles and passes m4"*. Both statements are false at this HEAD, measured:

1. **The literal twin CRASHES.** `&P = SPAN("ab") | SPAN("09")` with `*&P` — no nesting anywhere — is **m4 rc=139**. Pinned as `corpus/probe/cn/cn_alt_leaf_lit_red.sno`.
2. **A program with no `&constant` at all crashes the same way.** Twenty ordinary assignments followed by `"ab" POS(0) (SPAN("ab") | SPAN("09")) RPOS(0)` is **m4 rc=139**. No declaration, no substitution, no inline, no chase stack. Pinned as `corpus/probe/cn/cn_alt_leaf_flat_red.sno`.

The constant machinery is **fully exonerated**. It was never a participant — it was only the thing that happened to make the graph bigger. (Killswitch receipt on the s161 witness shape: `SCRIP_CONST_INLINE=0` and `SCRIP_CONST=0` each "cure" the crash, `SCRIP_PAT_INLINE=0` does not — which is exactly what a size-mediated defect looks like when you flip the switch that removes the extra statement's slots.)

## THE ABLATION LADDER (each row a minted witness, default arm, m4)

| witness | shape | m4 |
|---|---|---|
| `v1` | `"ab" POS(0) (SPAN\|SPAN) RPOS(0)` — bare, 0 padding | **PASS** |
| `pad5 / pad10 / pad15` | same + 5/10/15 padding assignments | **PASS** |
| `pad20 / pad25 / pad30` | same + 20/25/30 padding assignments | **rc=139** |
| `c1` | 25 pads, `SPAN` **without** an ALT | **PASS** |
| `c2` | 25 pads, ALT with **literal** arms (no scratch leaf) | **PASS** |
| `c3` | 25 pads, ALT with SPAN in **one** arm only | **rc=139** |
| `c4` | 25 pads, **two SPANs, no ALT** | **PASS** |
| `u4` | the s161 literal twin (constant, no nesting) | **rc=139** |

**Required ingredients, exactly three:** an `IR_MATCH_ALTERNATE`, a **scratch-cell leaf** (SPAN/BREAK/BREAKX/TAB/RTAB/REM) inside one of its arms, and a **ζ coordinate large enough to escape the live frame**. Nesting is not one of them. Substitution is not one of them.

## THE ASM DIFF — FOUR INSTRUCTIONS, ONE NUMBER

Diffing the emitted `.s` of the passing `v1` against the crashing `u4`, match region, whitespace-normalised: **the two regions are identical except for four instructions**, the two arms' ζ save/restore.

```
 v1 (PASS)                                    u4 (CRASH)
  mov dword ptr [rsp + 164], r14d      →       mov dword ptr [rsp + 532], r14d
  mov r14d, dword ptr [rsp + 164]      →       mov r14d, dword ptr [rsp + 532]
  mov dword ptr [rsp + 148], r14d      →       mov dword ptr [rsp + 516], r14d
  mov r14d, dword ptr [rsp + 148]      →       mov r14d, dword ptr [rsp + 516]
```

`--dump-zeta` names the number outright: those displacements **are the flat ZLS coordinate, verbatim**. v1 allocates `span.cnt/cur` at ZLS `+144`/`+160` (emitted `[rsp+164]`/`[rsp+148]`, i.e. coordinate + `x86_scratch_off+4`); u4's declaration statement adds twenty more slots ahead of the match, so the same two cells land at `+512`/`+528` and are emitted as `[rsp+532]`/`[rsp+516]`.

## THE MECHANISM, AND WHY IT DETONATES IN `getenv`

A scratch-cell leaf **carves nothing at its own α**, so `x86_frame_off`'s single `op_zdepth` term has no own-carve to compensate and the raw flat coordinate reaches whatever `rsp` happens to be. On the ordinary spine that address has a granted owner. **Inside an ALT arm it has no owner in either medium** — `zd_plan` grants per RUN and the arm interior is the s66/s71 ungranted-arm denial class. This is not a new discovery: it is written verbatim in `src/templates/x86_asm.h:1216` (the `LFC()` accessor comment) and in `leaf_frame_candidate()` (`src/emitter/emit.cpp:2319`). What was missing was that **anyone could reach it without an ALT-arm-specific program** — the flat coordinate is a *whole-graph* offset, so any statement earlier in the graph pushes it further past the live frame until it clears the top.

At crash time the write lands in the process's **argv/envp pointer array**, zeroing the high dword of a live environment pointer. The program then dies the next time libc walks `environ`:

```
#0  __GI_getenv (name=0x... "SCRIP_DCAP_TRACE") at ./stdlib/getenv.c:31
#1  c_rt_dcap_end_ok_open  (pattern_match.c:721)
#2  rt_match_end_all       (pattern_match.c:743)
#3  n106_match_end_α ()
si_addr = 0xffffe7bc          ← the low half of a 0x7fffffff…  stack pointer, high half zeroed
rsp = 0x7fffffffdf70 → write target rsp+564 = 0x7fffffffe1a4;  environ array base = 0x7fffffffe218  (Δ = 116 bytes)
```

This is bit-for-bit the signature the s161 FINDING recorded (`getenv` ← `c_rt_dcap_end_ok_open` ← `rt_match_end_all`) — it was reading the right crash and naming the wrong cause. `SCRIP_DCAP_TRACE` is a red herring: any libc `environ` walk after the stray write would do.

**CAUSAL PROOF AT THE NAMED INSTRUCTION (no gdb required).** Take the crashing `pad25.s`, change **only** the four displacements `564`/`548` → `24` (a free quad inside the ALT's own `sub rsp,32`), reassemble, relink: **`rc=0`, output `match`.** Same line count, same everything else. The displacement is the whole defect.

## ⛔ m3 IS NOT EXONERATED — ITS PASS IS A STACK-NEIGHBOURHOOD ACCIDENT

The s161 FINDING's "crashes m4 and passes m3" reads as a medium divergence. It is not one: **m3 emits the same wild displacement** (one `LFC()` accessor, medium-complete `x86()` — m3 ≡ m4 holds here) and simply runs deep inside `scrip`'s own process stack, so a coordinate that clears a standalone binary's frame still lands on dead frames in-process. Push the coordinate far enough and **m3 dies too**, measured:

| padding statements | ζ coordinate | m3 |
|---|---|---|
| 50 / 100 / 200 / 400 / 1000 | +960 … +16160 | PASS |
| **3000** | **+48160** | **rc=139 (SIGSEGV)** |

Any future witness of this class that is graded green on m3 alone is graded on luck.

## THE CURE ALREADY EXISTS, IS MEASURED, AND IS DISARMED BY DESIGN

`SCRIP_SPAN_FRAME=1` (`sn4_span_frame()`, `emit.cpp:2312`) re-homes the admitted six (SPAN/BREAK/BREAKX/TAB/RTAB/REM) onto the rbp-relative activation-frame slot, which is depth-immune. Measured this session, both media:

- **Every witness above turns green** — `u4`, `pad20`, `pad25`, `c3`, `cn_alt_leaf_flat_red`, `cn_alt_leaf_lit_red`, and `pd3000` (the m3 crasher) — **m3 PASS and m4 PASS in every cell**.
- `test_gate_clobarm.sh`: **1/5 → 2/5**; the cured row is `clob_altarm_arm2direct_red`, the only rc=139 row. The other three reds are `parse fail`, a different defect, unmoved.
- Default (`=0`) is byte-identical to pre-s130 **by construction** — a declined candidate never enters the registry scan.

Its own comment states why it is off: *"=1 opt-in pending the corpus ON-arm sweep and Lon's flip grant, per the R-7/s124 protocol."* **That flip grant is the disposition this defect is waiting on, and it is Lon's, not a seat's.**

## WHAT I LANDED — CN-15, THE SUBSTITUTION-DEPTH SELECTOR, DEFAULT OFF AND MEASURED CLEAN

The brief says *delete the TOP-LEVEL-ONLY depth limit*. The limit (`!sno_kw_chase((const char *)0, 3)`, two sites in `sno_pat_node`) is **not deletable while `SCRIP_SPAN_FRAME` is off**: lifting it converts an ALT arm's `IR_MATCH_DEFER` into a scratch-cell leaf, which is precisely the ingredient that arms the class above. So it is landed as a selector, `sno_kw_nest_ok()`, whose OFF branch is the identical expression:

| `SCRIP_CONST_NEST` | `SCRIP_SPAN_FRAME` | `cn_nest_alt_defer` defer labels | m3 | m4 |
|---|---|---|---|---|
| 0 (default) | 0 (default) | 8 | match | match |
| 1 | 0 | **0** | match | **rc=139** |
| **1** | **1** | **0** | **match** | **match** |
| 0 | 1 | 8 | match | match |

**The witness's own stated success criterion is met** — its header says *"when that emission defect is root-caused, the depth limit deletes and this witness's defer count drops while its output stays byte-identical"*: defer labels **8 → 0**, output `match` in all four cells.

**Killswitch receipts (measured, not construed):**
- **Default-arm `.s` sweep vs a baseline worktree built at `f44be5f1` with no edit: 0 movers of 318** crosscheck programs.
- **Non-vacuity:** `SCRIP_CONST_NEST=1` moves **exactly 1 of 18** probe/cn programs — `cn_nest_alt_defer`, the pinned witness — and **0 of 318** crosscheck programs (no shipped program declares a constant with nested pattern members; the switch's blast radius today is the witness set, stated rather than implied).
- `test_gate_udc.sh` **27/0**, unchanged.

## WITNESSES PINNED (`corpus/probe/cn/`)

- `cn_alt_leaf_flat_red.{sno,ref}` — **constant-free**, 20 pads + ALT(SPAN,SPAN). Default: m3 PASS / m4 rc=139. `SPAN_FRAME=1`: PASS both. *The falsifier.*
- `cn_alt_leaf_flat_grn.{sno,ref}` — identical statement, 5 pads (coordinate +224). Green on the default arm both media. *The pair proves the defect is the coordinate's magnitude, never the shape.*
- `cn_alt_leaf_lit_red.{sno,ref}` — the s161 literal twin. Default: m3 PASS / m4 rc=139. `SPAN_FRAME=1`: PASS both.

These sit in `probe/cn/` deliberately: they are graded by no gate, so pinning them moves **no tally** on another front's board. The class they belong to is `probe/clobarm/` + `probe/leafsib/` and `test_gate_clobarm.sh` is its gate.

## ⭐⭐⭐ THE ON-ARM SWEEP LON'S FLIP NEEDS — RUN THIS SESSION, AND IT CURES A NAMED BOARD BLOCKER

The flip's stated precondition is *"the corpus ON-arm sweep"*. Measured here on the 318-program crosscheck corpus plus the 337-program broad runner, same pristine tree:

- **`.s` blast radius: 15 movers of 318.** Every mover is a `*_pat_*` program — `063–066_pat_fence_fn_*`, `120/121_pat_calc_*`, `123_pat_regex_alt_class`, `127/152_pat_json_keyvalue*`, `130_pat_two_star_fence_concat_outer`, `131_pat_boolean_expr_grammar`, `178/179/181/182_pat_*`. **The prediction stated above holds exactly:** only programs holding an alternation with a scratch-cell-leaf arm move, and **all 15 PASS against their `.ref` under BOTH arms** — every mover is a `.s` change with unchanged output.
- **Broad runner:** measured twice. At the root-cause tree `f44be5f1`: default **m3 325/337 · m4 322/337** (the recorded watermark, unchanged by CN-15) → `SPAN_FRAME=1` **m3 326/337 · m4 322/337**. At the landed tree `924cf16a` (other seats' work included): default **m3 326/337 · m4 322/337** → `SPAN_FRAME=1` **m3 327/337 · m4 322/337**. **Both times: zero regressions in either medium, exactly one program gained.**
- ⭐ **THE GAINED PROGRAM IS `demo_claws5` — the blocker the s166 dispatch board names** (*"claws5 (66KB) BLOCKED by the m3 SIG11 (D-2's rung)"*, also the PT front's second workhorse). Measured three runs per arm, deterministic: **m3 `SCRIP_SPAN_FRAME=0` → rc=139 SIGSEGV; `SCRIP_SPAN_FRAME=1` → rc=0 PASS.** claws5's m3 SIG11 is this class.
- **Stated, not hidden: claws5 m4 still crashes under BOTH arms** (rc=139). That is a *second, different* defect, untouched by this switch and still owed to D-2.

So the ON-arm evidence is: 15 `.s` movers, all correct in both arms; no behavioural regression anywhere measured; one long-standing named SIGSEGV cured. What is still outstanding before the flip is the wider `.s` sweep (the 527-program demo/feature/benchmark artifact set) that this seat did not run.

## OWED, IN ORDER

1. **⛔ LON'S RULING: flip `SCRIP_SPAN_FRAME` to default ON** — the ON-arm sweep above is now on the record and it is clean plus one cure; what remains is the 527-program artifact sweep. It is the cure for a live wrong-answer/crash class that is reachable from ordinary SNOBOL4 — an alternation with a SPAN arm in a program with enough statements ahead of it — with **no constant, no nesting, and no unusual construct required**. The 318-program sweep is measured above (15 movers, all correct both arms, zero regressions, `demo_claws5` m3 cured); the 527-program artifact sweep is what is left.
2. **Then delete the limit for real** — `SCRIP_CONST_NEST` becomes the default and `sno_kw_nest_ok()` collapses to `!sno_kw_chase(nm, 0)`; op 0 (the genuine cycle test, dead today because op 3 subsumes it) becomes the live guard, which is what `sno_kw_chase`'s own comment always described.
3. **ARB and BAL are still declined** inside `leaf_frame_candidate()` for two separate measured reasons (the 8-byte usable-window law). An ALT arm holding ARB or BAL is the same wild write with no cure available on either arm today — untested here, and the next witness worth minting.

## ⛔ RE-PROOF AFTER THE REBASE (RULES: "re-prove your goal's gate/watermark after a rebase")

The push rebased CN-15 onto three other seats' commits landed the same hour — `c6245f60` B1c parity **flipped default ON**, `bcd3984e` medium-retire rung 1, `b7e10d3c` GC-W1 worklist mark. Every number in this FINDING was re-measured on that tree from `make pristine`, with a fresh baseline worktree built at `c6245f60` carrying no edit:

| claim | re-proved |
|---|---|
| default-arm `.s` byte-identity vs baseline | **0 movers of 318** |
| `cn_nest_alt_defer` matrix | NEST=0/SPAN=0 → 8 defers, green · NEST=0/SPAN=1 → 8, green · **NEST=1/SPAN=0 → 0 defers, m4 rc=139** · **NEST=1/SPAN=1 → 0 defers, green BOTH media** |
| the three pinned witnesses | `flat_red` m4 rc=139 → PASS armed · `flat_grn` PASS both arms · `lit_red` m4 rc=139 → PASS armed; m3 PASS in all six cells |
| `test_gate_udc.sh` | **27/0** |
| `test_gate_clobarm.sh` | **1/5** default → **2/5** armed |
| `demo_claws5` m3 | **rc=139** default → **PASS** armed |
| broad runner | default **m3 326 · m4 322** → armed **m3 327 · m4 322** |

Nothing moved. The rebase changed the watermark's absolute numbers (other seats gained a program) and changed nothing about this defect, this cure, or this switch.
