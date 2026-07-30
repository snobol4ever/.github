# FINDING 2026-07-30 (s21x-o) — ZTOS-1: the depth displacement was two authorities, not a hard problem; and the arming frontier is a property of a box's READERS

**Session:** s21x-o · SNOBOL4-BB · Lon directive "Finish the RSP/RBP once and for all. We've been struggling for unknown reasons for the last few sessions."
**Commits:** SCRIP `b5754902` (ZTOS-1), `785e3a41` (GLUE-3), `5c0576cb` (feature .s) · corpus `aafe071e` (benchmark .s), `066cc232` (demo .s)
**Watermark:** m3 211/105 → **250/66** · m4 208/72/36 → **248/32/36** · DIVERGE=3 unchanged throughout. Reproduced at session start before any edit.

---

## 1. The "unknown reasons" were two instructions

`028_arith_unary_minus` is four lines of SNOBOL4 (`OUTPUT = -5`) and printed `5`. Byte-diffing its `--compile` output against the `SCRIP_BB_ALLOC=0` control gave the ENTIRE difference:

```
> sub rsp, 16
> add rsp, 16
```

Nothing else. The emitted body explains itself once seen:

```
n1_unop_α:
        sub  rsp, 16                        <- the box's own carve
        mov  rdi, qword ptr [rsp + 0]       <- its operand, hardcoded, now 16 bytes too low
        mov  rsi, qword ptr [rsp + 8]
        call rt_num_neg@PLT
        mov  qword ptr [rsp + 0], rax       <- result into the dead cell
        add  rsp, 16                        <- ...which is then popped
```

The literal producer pushes a 16-byte DESCR at TOS. The consumer carves its own cell and then reads its operand at a **template-private, hardcoded** `[rsp+0]/[rsp+8]` — which after the carve is its own fresh uninitialised cell. It negates garbage, stores the answer where nobody will look, pops it, and `assign` reads the original un-negated `5`.

**The defect class, stated plainly: the allocation and the operand address were computed by two authorities that did not know about each other.** The carve fires in `x86_port_hook`; the address was spelled by a `static inline const char * rspq(int off)` helper that each template had grown privately (five of them across the tree, each citing the previous one as precedent). Neither could see the other. This is the same shape as every other defect this subsystem keeps re-learning — `x86_fc_hit`'s silent fallback, the FRQ/FRQB bump disagreement, the five-boolean cascade ZOP-1 collapsed — and it is why the failures looked mysterious: **nothing in the code names the relationship that is being violated.**

## 2. ZTOS-1 — the fix is one field and one accessor

`op_zdepth` (emit.h, appended at struct end per the s141 ABI law) is set at the ONE choke, `walk_bb_node_inner`, from the SAME `op_fc_bytes` that the allocator spends. Allocator and accessor therefore cannot hold two opinions — the `zw_node_k` ONE-K-AUTHORITY discipline extended from the size side to the address side.

`ZTOS(off)` / `ZTOSD(off)` resolve a TOS reference to `off + op_zdepth`: **the producer's offset plus whatever the reader allocated beneath it.**

Three properties make this the right shape rather than merely a working one:

- **It is LOCAL.** A box compensates for exactly what IT carved and knows nothing about its neighbours. Lon's "no pre-allocation calculation is necessary" falls out — the graph traversal that computes the zeta offsets is the traversal the emitter is *already doing*, and the answer is available at the choke without a prefix pass. Contrast `op_flat_disp`, LOWER's static prefix sum, which was the correct answer only while boxes did not allocate for themselves.
- **Arming one BB can no longer displace another.** That property is what the whole s21x-j..m ladder was missing.
- **`op_zdepth == 0` reproduces the old raw spelling byte-for-byte**, so an unarmed box is unchanged and the conversion can crawl family by family with byte-identity as the gate at each step.

Ordering was verified rather than assumed: `DRIVE_FILL` sets per-kind geometry and *then* calls `walk_bb_node`, so the choke sees the final `op_fc_bytes` from both the `fc_geom` path and the ZW-1 universal carve.

Converted this rung: `bb_unop`, `bb_assign_global`, `bb_binop_arith`, `bb_binop_concat_slot`, private helpers deleted. `bb_unop` alone moved m3 211→213 and m4 208→211.

## 3. GLUE-3 — the two glue codes wired, byte-identical

The four `x86_sub/x86_add("rsp", K)` lines inside `x86_port_hook` now route to `bb_glue_flat_enter/leave`, promoted at s21x-n and left with **zero callers** ever since. Allocation now reaches rsp only through `x86_alpha`/`x86_beta`, exactly as directed.

The substantive gain is that **`ZC_STORAGE` becomes load-bearing at the allocation site for the first time.** The hook allocated identically under all four modes: FRAME_R12/FRAME_RSP would have carved a per-BB cell *on top of* the whole-graph frame they had already carved (the roman anti-pattern approached from the other side), and CELL_HEAP would have silently taken the rsp arm instead of its rbx frontier. The glue answers each mode explicitly and BOMBS on the unimplemented one rather than emitting plausible-but-wrong code.

Proven byte-identical across 100 crosscheck programs plus an unchanged watermark.

⚠ **`x86_begin()` had to come out of both glue fragments.** It mints a fresh `x86_uid` from `g_flat_node_id` in TEXT medium, and that uid names the box's RO constant labels (`.Lx<uid>_0`). Calling it once per port advanced the counter and renumbered every downstream label: instructions identical, `.Lx5_0` → `.Lx8_0`. **A pure label rename executes perfectly and is invisible to any run-only test** — only the byte-identity A/B caught it, and had it landed it would have churned every committed `.s` artifact with a diff nobody could later explain. The glue is a *fragment* emitted inside another box's port and must inherit that box's uid, not mint one.

## 4. ⛔ NEGATIVE RESULT — the arming frontier is a property of a box's READERS, not of the box

Lon directed arming every BB, and the `_spine` exclusion list in `walk_bb_node_inner` looked like exactly the shyness being called out: its own s21x-m note blamed "a zw carve-only cell inserted mid-spine displaces every TOS read by K", and ZTOS retires precisely that displacement.

Set to 0 and **MEASURED: m3 214 → 108, m4 211 → 107.**

The spine kinds themselves are fine. `OUTPUT = 1 + 2` still prints `3`, and the A/B shows ZTOS compensating the binop's reads correctly (+16 on every operand — its own carve). What broke is **111 programs that are almost entirely MATCH statements** (`033_goto_success`: the match runs, fails, takes the `:F` branch).

**Root cause is the same root cause one level out.** The match family does not address through ZTOS. It speaks `FRQ()` — x86_zop arms 3/4 — whose depth compensation is `op_flat_disp`, LOWER's **static** prefix sum, blind to per-BB carves. Arming a producer that *feeds* a match deepens rsp underneath a consumer whose compensation cannot see it.

**THE LAW:** a BB may be armed once ALL of its consumers speak the live-depth authority (`op_zdepth`); arming it while a consumer still speaks the static authority (`op_flat_disp`) displaces that consumer by exactly the new carve.

This is why widening the arming set BY KIND kept producing the "unknown reasons" of s21x-j..m: **the property that decides whether a box can be armed does not live on that box.** The exclusion is restored with this reason recorded in `emit.cpp`, replacing the wrong one.

## 4b. ZTOS-2 — the same law on the frame arm, one line, +37 both arms (SCRIP `e064482e`)

The blocker section 4 identified was discharged in the same session, and the fix was one line in `x86_frame_off` — *the* one offset function:

```c
return (x86_isle() || x86_fb_data()) ? off : off + (int)_.op_flat_disp + _.op_zdepth;
```

The rsp whole-graph arm carried only `op_flat_disp`, LOWER's **static** distance from rsp to the flat frame base. The box's own alpha carve moves rsp down by K *after* that distance was computed, so every such reference read K bytes too low — **the identical ZTOS-1 defect, on the frame arm instead of the spine.** Arms 1 and 3 (island r12, pinned rbp) are depth-immune bases and are deliberately excluded; compensating a base that does not move is the FRQ/FRQB double-add class.

**m3 214 → 251, m4 211 → 248, DIVERGE=3 flat.**

This discharges the s21x-n cursor's NEXT(1) — "`op_flat_disp` must become the live authority as carves deepen the stack" — and generalises the law:

> **A box compensates for exactly what IT carved, whichever base its references name.**

Both halves of this session are the same one-sentence law applied at two sites. That is the useful takeaway: the subsystem did not need a new mechanism, it needed the two existing authorities (what a box allocates, and where a box reads) to be forced to agree.

## 4c. ⛔ The spine arming has a SECOND blocker — measured, not identified

With arm 4 live, `_spine = 0` was retried: **m3 251 → 192, m4 248 → 191.** Far better than the pre-ZTOS-2 collapse to 108, so ZTOS-2 removed one of two causes — but a second remains and this session did **not** identify it. Reverted; the exclusion stands.

⚠ This experiment has now been run twice with two different results. The next session's job is to **name** the residual class — bisect with `SCRIP_BB_ONLY`/`SCRIP_BB_SKIP` (nid csv), which is precisely what that instrument exists for — not to re-observe that it regresses.

## 5. Next, in dependency order

1. ⭐ **Bisect the residual spine blocker** (§4c) with `SCRIP_BB_ONLY`, one kind at a time, against the 251/248 baseline. The fail set is now roughly a third of what it was at session start.
2. The remaining 11 templates spelling `"rsp"` directly. `bb_match_capture`'s deliberate raw `rsp#` marker is load-bearing inside the SAVE/COND protocol and wants the splice ruling first.
3. `bb_binop_arith`'s own mid-body `add rsp,16` (pops its second operand cell) — traced, composes correctly with `op_zdepth`, but still a raw rsp reference in a template.
4. **Wire `bb_glue_framed_*`** — the RBP half. Customers closed by the s21x-c four constructs. ⛔ LAYOUT CONTRACT, not a spelling switch (s21x-m measured SEGV): whoever wires it wires the prologue's rbp save/seed in the same breath.
5. ARBNO onto the framed glue = the VARIABLE-EXTENT ANCHOR that retires the SUSPENDED-CELL law.

## 6. Method note

Every claim above is a measurement taken this session, not a citation. The watermark was reproduced *before* any edit (m3 211/105, m4 208/72/36, DIVERGE=3 — matching the s21x-n record exactly), which is what makes the deltas meaningful. The one time this session reasoned from a comment instead of a measurement — reading the `_spine` note as shyness — the measurement immediately contradicted it, and that contradiction turned out to be the most useful result of the session.
