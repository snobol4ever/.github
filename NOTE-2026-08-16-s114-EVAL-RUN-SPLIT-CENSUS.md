# NOTE 2026-08-16 s114 — THE EVAL RESIDUAL IS A ZD **RUN SPLIT**, NOT A ONE-CELL OFFSET

**Status: NO BUG FIXED. THE BOARD DID NOT MOVE.** `beauty_self` 0/1, beauty m3 still SIG11.
What this note contains is a root-cause narrowing, a mechanical witness pair, and four
falsifications. It is routing, not a landing.

⚠ **PROVENANCE CAVEAT, READ FIRST.** This seat found SCRIP `57972743`, corpus `b69f86ee`
and `.github` `50f4d630` present in its container as **local-only commits** (`origin/main`
was still `657a8dc1`; `git branch -r --contains` empty; the Makefile invokes no git and none
of the four committing scripts were run). This seat has **no record of authoring them** and
does not claim them. Everything below marked MEASURED was measured first-hand by this seat
against the rebuilt tree. Treat the authorship of `57972743` as unresolved.

---

## 1. THE RESIDUAL, RE-CHARACTERISED

`corpus/probe/eval/ev_fn_literal.sno` — `F = EVAL('1 + 2')` inside a DEFINE'd function —
prints **2**; oracle prints **3**. It is filed as a "ONE-CELL OFFSET". **That framing is wrong**
and will cost the next seat a session if inherited.

MEASURED, m3 vs m4, same source:

| | m3 (`--run`) | m4 (`--compile`) | oracle |
|---|---|---|---|
| output | **2** | **3** | **3** |

**m4 PASSES.** So this is ALSO a `GOAL-MODE34-IDENTICAL` violation, and m4 stands as a
**working reference emission for byte-identical IR** — the cheapest discriminator this class
has ever had. Do not hunt m3 in isolation; diff it against m4.

## 2. THE TWO EMISSIONS ARE NOT THE SAME CODE

Both media JIT the chain at RUN time through `eval_build_chain` (m4's static `.s` does NOT
contain the chain), so a divergence here is an **emitter-state** divergence, not a codegen-path
divergence. Disassembled at `rt_chain_enter_v` in both and diffed:

- **m4** — fused inline arithmetic: `cvtsi2sd` / `addsd`, DT tag checks, FORTH spine (`sub $0x10,%rsp`, cells at `(%rsp)`/`0x8(%rsp)`).
- **m3** — flat frame reads at `0x20/0x28/0x30/0x38` plus runtime call-outs through the RTCC block.

## 3. ROOT CAUSE: THE RUN SPLITS AND RELEASES THE BINOP'S OPERAND

`SCRIP_ZD_DIAG=1` names it mechanically. The chain graph is `n=6 region=64 jmp=1 pat=0 gen=0`
in BOTH arms — every emitter flag identical.

**PASSING arm** — one run, everything armed:
```
[ZD] h=0 r=0 i=0 IR_STATEMENT_BEGIN K=0  zout=0  gpop=0  wpop=0
[ZD] h=0 r=1 i=1 IR_LIT_INTEGER   K=16 zout=16 gpop=0  wpop=0
[ZD] h=0 r=2 i=2 IR_LIT_INTEGER   K=16 zout=32 gpop=0  wpop=16
[ZD] h=0 r=3 i=3 IR_BINOP         K=16 zout=48 gpop=0  wpop=32
[ZD] h=0 r=4 i=4 IR_ASSIGN        K=0  zout=48 gpop=0  wpop=0
[ZD] h=0 r=5 i=5 IR_STATEMENT_END K=0  zout=48 gpop=48 wpop=48
```

**FAILING arm** — the run SPLITS after `i=1`, and that node is RELEASED (`gpop=16`):
```
[ZD] h=0 r=0 i=0 IR_STATEMENT_BEGIN K=0  zout=0  gpop=0  wpop=0
[ZD] h=0 r=1 i=1 IR_LIT_INTEGER   K=16 zout=16 gpop=16 wpop=0
[ZD] run h=2 len=4 REFUSED at i=3 (opnd op=3)
```

`op=3` = **`IR_BINOP`** (the `+`). Refuse reason `why="opnd"`. The second run cannot arm the
BINOP because the split already freed the spine cell holding its first operand.

⭐ **THE DEFECT IS THE RUN BOUNDARY AT `h=2`. Everything else is consequence** — the four
refused nodes, the fall to flat-FRQ addressing, and the wrong value. Do not chase the BINOP,
do not chase the flat offsets, and do not "fix" the refused path: the armed path is already
correct and m4 proves it.

## 4. THE TRIGGER IS THE PRIOR GRAPH'S IR POPULATION — WITNESS PAIR MINTED

`corpus/probe/eval/ev_pad_alias_0.sno` (FAIL) and `ev_pad_alias_1.sno` (PASS), both with live
`sbl` refs. They differ by **one semantically inert line**. The EVAL chain is byte-identical.

| padding placed ahead of the call | armed | output |
|---|---|---|
| none | 2/6 | **2** ✗ |
| `x = x` — adds IR, adds NO new global | 6/6 | **3** ✓ |
| `PADV0 = 0` — adds a new global | 6/6 | **3** ✓ |
| 1 or 2 `*` comment lines — shift line numbers, emit ZERO IR | 2/6 | **2** ✗ |

Reading: the trigger is neither **source-line attribution** (comments shift every line number
and change nothing) nor the **global registry** (`x = x` flips it without adding a global). It
is the **IR node population of the previously-lowered graph**. That is consistent with the
address-aliasing class `fc_tables_reset`'s own header documents — `eval_build_chain` ends in
`IR_free_dyn`, so a later chain's fresh `IR_t` land on a freed graph's addresses — but the
carrier is NOT YET NAMED. **Dependence is proven; the carrier is not.** State it that way.

## 5. ⛔ FALSIFIED THIS SEAT — DO NOT REDO

- **`fc_tables_reset` widening.** It clears `fct_n` and nothing else, while **fourteen** more
  pointer-keyed tables (`fca fcab fcc fch fcm fcs fcv fpe fvb fvcl fvl fvr fvs fvw`) survive
  every runtime compile; the function header's claim that "two remain" is **stale by thirteen**.
  Widened it behind `SCRIP_FC_RESET_ALL` and A/B'd on the same binary: **INERT** — arming stayed
  2/6, output stayed 2. REVERTED rather than land an unmeasured change in shared codegen. The
  stale header is still worth correcting, but it is NOT this defect.
- **`g_chain_entry_key[65536]`** (`emit.cpp:368`) — also never reset and also pointer-keyed, but
  it gates group-anchor pull-in, not arming; `n=6` in both arms. Ruled out.
- **Source-line attribution / `stmt_src_slice` collision** — comment-line test above kills it.
- **Global registry / `is_global`** — `x = x` test above kills it.

## 6. ALSO STANDING

- **DEAD KILLSWITCH:** `emit.cpp:2759` computes `_gsym` from `SCRIP_GLUE_SYM` and then discards
  it with `(void)_gsym`. The GLUE-SYM enter therefore **never fires regardless of the env var**.
  R-7 (dead killswitch/arm deletion) has a customer.
- **CLASS-C placement fact** (earned with gdb, worth not re-deriving): a chain frame carve must
  land AFTER the chain's two-jmp entry dispatch. Placed at the zframe/`flat_lcl_proc` prologue
  dispatch it sits at **offset 0**, ahead of `jmp α_body` / `jmp ω`, so any caller entering at
  `fn+5` for ω lands mid-instruction — regressed `ev_fn_var` PASS→SIG11.

## 7. NEXT SEAT STARTS HERE

Instrument is already minted and costs one command:
```bash
SCRIP_ZD_DIAG=1 scrip --run corpus/probe/eval/ev_pad_alias_0.sno   # run splits at h=2, REFUSED (opnd op=3)
SCRIP_ZD_DIAG=1 scrip --run corpus/probe/eval/ev_pad_alias_1.sno   # one run h=0 len=6, all armed
```
Find why `zd_plan` cuts a run boundary at `h=2` in arm 0 and not arm 1. The refuse print is
`emit.cpp:2457`; `why="opnd"` is the branch to instrument, and the run-FORMATION loop above it
(which sets `hi` and fills `run[]`) is the unread region — this seat ran out of context before
reading it and deliberately did not open that hunt. `SCRIP_ZD_GAP=1` exists beside the refuse
print and may already report the boundary.

## 8. UNCOMMITTED WHEN THIS NOTE WAS WRITTEN

`corpus/probe/eval/ev_pad_alias_{0,1}.sno` + `.ref` (minted, verified against a clean rebuild).
No push attempted; no credential requested — see the provenance caveat at the top.
