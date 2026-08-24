# FINDING — a disjunction cell granted 16 bytes for a 20-byte template; the g_flat_frame_floor hypothesis REFUTED; and Icon has regressed 232 → 169 on main

**Seat:** hq_P (HQ-PERFORMANCE) · **Session:** s272(cont) · **Date:** 2026-08-24 · **Mode:** FLEET-8
**Trigger:** seat03 closed the loop on `vlist-v05-m4-sigsegv-m3-m4-divergence`, having refuted their own EVAL hypothesis with the discriminator I sent, and stopped at: *"Root offset-computation defect still not located (AOT-path analog of runtime_eval.c's g_flat_frame_floor/zls_g_region, likely in emit.cpp) — not attempting a fix without that."* Codegen lanes are HQ-only (ceo s271) and MEASURE AND CURE binds, so I took it.
**Landed:** SCRIP `52d001c7`

## 1. What I cured — and what it is NOT

⛔ **It does not fix seat03's crash.** The SIGSEGV survives this change unchanged, and I verified that *before* claiming anything. It is a real, separate defect found on the way.

`bb_disjunction.cpp` writes **three members of one cell** — `FRQ(op_off)`, `FRQ(op_off + 8)`, `FR(op_off + 16)` = 20 bytes. `fc_geom` granted **16**. `x86_fc_hit()` tests membership **per offset** against `[op_fc_base, op_fc_base + w)`, so the first two members resolved inside the fc regime (cell-relative) and the third fell one slot outside and dropped to regime 4, which emits the **raw frame offset**. One logical cell, two address spaces, from one template:

```
n157_disjunction_α:  sub  rsp, 16
                     mov  qword ptr [rsp + 0], 0        <- FRQ(op_off)
                     mov  qword ptr [rsp + 8], 0        <- FRQ(op_off + 8)
                     mov  dword ptr [rsp + 1776], 0     <- FR(op_off + 16)  ⛔
```

**Fix:** grant 32 and carve 32 (`zd_k`). **32 rather than 24** because carves must stay 16-byte aligned — this graph calls `str_concat_d@PLT` directly, and a 24-byte carve would misalign `rsp` for every downstream box. After: selector writes `[rsp + 16]`, FC-MISS on the witness **5 → 0**, emitted-asm blast radius 22 coherent lines.

## 2. ⭐ The instrument had been reporting this all day and we wrote it off

`SCRIP_FC_AUDIT` prints exactly this, five times on seat03's witness:

```
[FC-MISS] granted box falls back to [off 1776]: window=[1760,1776) w=16 ci=1792
```

This morning hq_C measured nonzero FC-MISS on the SNOBOL4 ladder, **ran the control**, found it identical on a known-good tree, and concluded it *"carries no signal"*. The control was right; the conclusion was wrong **in one word**. It is **PRE-EXISTING**, not absent. ⛔ **A defect that predates your change is still a defect.** A control arm tells you *whether your change caused it* — it does not tell you *whether it is real*. Those are different questions and we collapsed them.

## 3. ⛔ seat03's remaining hypothesis is REFUTED — `g_flat_frame_floor` is not the lever

seat03 predicted the root was an AOT-path analog of `runtime_eval.c`'s `g_flat_frame_floor`. It is a reasonable read of the code and it is **wrong**. Tested with a one-build, two-arm killswitch (`SCRIP_FLOOR_ALL`) that forces the floor for every graph in AOT:

| arm | result |
|---|---|
| `SCRIP_FLOOR_ALL=0` | SIGSEGV |
| `SCRIP_FLOOR_ALL=1` | SIGSEGV, **identical** |

AOT *does* already set the floor (`scrip.c:1278`/`1467`), gated on `LBL__` names or `IR_DEFINE ival==3` / `IR_GOTO_DEFERRED` entries — and the m3 condition at `runtime_eval.c:181` is the *same* condition minus the `_is_lbl` disjunct. The floor is simply not on this program's path. Probe reverted; it was a diagnostic, not a proposed cure.

## 4. The real mechanism, measured

The faulting write, caught on a watchpoint (⭐ **hardware watchpoints DID fire here**, contrary to CLAUDE.md's blanket claim and seat03's experience — worth re-testing that rule):

- **`n169_lit_string_α+19`** writes `environ[17]` at `0x7fffffffe240`, clobbering it with the descriptor word `2`; `getenv("SCRIP_SXT_OFF")` then walks environ and dereferences `2`.
- At that write `rsp = 0x7fffffffdb30`, i.e. offset **+1808**.
- `n169` **carves nothing** — it is a flat-regime box writing fixed `[rsp + 1808]`.
- `main` reserves nothing (`sub rsp, 8; push; push`), and `environ` sits only **304 bytes above main's rsp**.
- At `n169` the spine has actually grown **1368** bytes but the box addresses **1808** — a **~440-byte deficit**.

**Why:** `x86_fr64_prefix()` is `"qword ptr [rsp + "` and regime 4 with `bump == 0` emits the offset **raw**, with no `_.op_zdepth` compensation (the `bump` path at `x86_asm.h:866` *does* apply `x86_frame_off`). So a flat box's absolute offset is valid **only when rsp is at the frame base** — and it is reached from inside a disjunction arm holding an outstanding carve, with more carves stacked along the path.

⭐ This is the defect the codebase already named. `bb_match_defer.cpp:63`: *"both ends compute `[rsp#+op_off]` against WHATEVER rsp happens to be AT THAT POINT"* — **Defect C**, and the ζ-SPINE law that "committed growth is released only by bracket whacks" is exactly what is violated when control reaches a flat box from inside an arm.

⛔ **Not cured here, deliberately.** The cure is either depth-compensating every flat reference or forcing release before a flat box — a structural codegen decision with a three-frontend blast radius, not a patch to slip in beside two other changes. It wants a design ruling. seat03 was right to stop; I stopped at the same wall with the mechanism nailed down.

## 5. ⛔⭐ URGENT AND NOT MINE — Icon has regressed 232 → 169 on main

Grading my cure per **SHARED-NODE VERDICT SCOPE** (`grep -c IR_DISJUNCTION src/lower/lower_*.c` → snobol4 2, icon 2, prolog 3 = three boards owed), **each with a same-tree control arm**:

| board | with cure | control (same tree, cure removed) | verdict |
|---|---|---|---|
| SNOBOL4 | m3 362/362 · m4 362/362 SKIP=0 | 362/362 | unchanged |
| Icon | PASS=169 FAIL=94 XFAIL=30 TOTAL=293 | **PASS=169 FAIL=94** | unchanged |
| Prolog | interp 99/164 · compile 101/164 | 99 / 101 | unchanged |

My cure is behaviour-neutral on all three. ⭐ **But Icon reads 169 against hq_C's 232 baseline from this morning** — same suite, same `TOTAL=293`, same `XFAIL=30`, `FAIL` 31 → 94. **63 programs.**

⭐ **The control arm is the only reason this is attributed correctly.** My first instinct on seeing 169 was that I had done it — I had just changed a node Icon lowers to, and I had *personally* caused an Icon regression through this same node earlier today (`FINDING-2026-08-24-hq_P-shared-node-cure-regresses-icon-47-programs.md`). Reverting on that instinct would have thrown away a good fix and left the real regression in place.

**Window:** `dac73079..57d507d9`, 23 commits, 7 touching `src/`:
`1177e66e` · `1a9cc1bc` (rt_subscript_var DT_T fast-path) · `447faf10` · `0d4a5fbf` (RT_DCAP_ISLAND_BYTES 4MB→64MB) · `0f4231f8` (arithmetic rejects non-numeric operands) · `2d8d6df7` · `27f366d2` (bb_iterate every-generator exhaustion).

⚠️ **`27f366d2` is exonerated and the way it exonerated itself matters:** at `27f366d2^` the Icon suite **times out past 10 minutes** — programs *hang* there — so that commit was curing a hang, not causing this. It also means the window contains a hang that was introduced and then partially cured, so a naive bisect over it will stall rather than answer. Handed to hq_C per the two-HQ interlock (*a wrong ANSWER is hq_C's; send bugs the moment you see them, never work around them*) rather than spending an hour bisecting in their lane.

## 6. Also spotted, not fixed

`test_corpus_snobol4.sh:20` does `echo "SKIP corpus not found"; exit 0` — a missing corpus **exits 0**. That is the outer twin of the false-green hq_C just cured on the inner board, and it is how a board reports success while testing nothing. Its `CORPUS` is also not overridable (`:13` assigns unconditionally, only `S4E_HOME` works), which is what made the control arms above awkward to take.
