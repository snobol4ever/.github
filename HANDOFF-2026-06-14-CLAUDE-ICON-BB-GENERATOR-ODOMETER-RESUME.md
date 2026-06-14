# HANDOFF 2026-06-14 — Icon m3/m4: generator-odometer resume in the flat emitter (Claude)

**Goal:** GOAL-ICON-FULL-PASS — Icon modes 3 (`--run`) and 4 (`--compile`) up to m2 parity.
**Result:** m3/m4 **104 → 111 (+7)**. m2 held at **202** (HARD gate) throughout. FAIL 43 → 36.
**HEAD (SCRIP) = `3738eac`** (2 commits). HEAD (.github) = this file.

Both fixes are the SAME safe class: the lowering graph was already correct (m2 prints the
right sequence from the identical graph), so ONLY the native flat-chain label binding changed
and the m2 HARD gate provably cannot move. Each increment passed the full gate battery before
commit.

---

## The diagnosis correction that drove this

The prior watermark framed the rc=124 cluster as "bb_every rebuild / infinite retry." Running
the EVERY rungs through BOTH engines showed it is really **native generator-resume label-binding
bugs**, not a timeout/bb_every problem (and several "rc=124" cases actually terminate with WRONG
or EMPTY output, not a hang):

- `every write(2 < (1 to 4))`        m2 `3,4`        m3 `3,4`       — already PASS (1 generator)
- `every write((1 to 3)*(1 to 2))`   m2 `1,2,2,4,3,6` m3 `1,2,1,2…` — WRONG (cross-product carry)
- `every write(3 < ((1 to 3)*(1 to 2)))` m2 `4,6`     m3 (empty)    — WRONG (filter exits early)

Method (reused from prior sessions): `./scrip --dump-bb foo.icn` to read the actual port edges,
then fix the native resolver to match the graph — never touch lowering (would risk m2).

---

## What landed (2 commits, both in src/emitter/emit_bb.c, `descr_flat_chain_build`)

**`c4fe0ef` — ω-edge into an earlier generator resumes via β (the odometer carry). +6.**
The flat-chain **γ** resolver already routed a back-edge into an EARLIER generator to that
generator's **β** (resume): `(i > k && ir_is_generator_kind(nodes[k]->op)) ? betas[k] : lbls[k]`.
The **ω** (failure) resolver did NOT — it bound any in-chain target to `lbls[k]` (the node's
fresh **α**). So when a chained generator operand exhausted, its failure edge re-entered the
preceding generator at α (restart at 1) instead of β (advance) — severing the cross-product
odometer. `--dump-bb` on rung01_paper_mult: right `TO` [8] has `ω=5β` (left `TO`) — the graph is
right; only the native binding picked α. FIX (one line, symmetric with the γ resolver):
```c
node_ω = (i > k && ir_is_generator_kind(nodes[k]->op)) ? betas[k] : lbls[k];
```
Matches `irgen.icn` `ir_binary` (`right.failure -> left.resume`). `ir_is_generator_kind` holds
Icon generator kinds only (IR_TO/TO_BY/UPTO/ALT/BINOP_GEN/ITERATE/LIMIT/PROC_GEN/LIST_BANG/
KEY_GEN/FIND_GEN/SEQ_GEN/GATHER/MAP/GREP) → structural no-op for Prolog (verified: prolog rung
suite 114/91/91, exact baseline). Disjoint from the existing EVERY-ω-block (IR_EVERY is not a
generator kind).

**`3738eac` — relop/filter over a cross-product resumes the INNERMOST generator. +1.**
When a non-generator node (e.g. a relop filter) fails and its `ω.node` is the IR_EVERY, the
EVERY-ω-block redirects the failure into a generator's β so the loop re-pumps. It picked the
**first** generator in chain order (`break` on first match) = the OUTER generator. With a
cross-product feeding the filter, filter-reject must resume the **innermost** generator (the same
one `CALL.γ` resumes), so the odometer advances by one rather than skipping the inner dimension.
FIX (one line): drop the early `break` so the loop keeps the LAST generator in chain order =
innermost. Single-generator filters (one generator = first = last) are unaffected. Fixes
rung01_paper_compound (`3<(...)`→4,6) and rung01_paper_paper_expr (`5>(...)`; ...→3,4,done).

---

## Verification (full battery, run before EACH commit)

| Check | Baseline | After |
|---|---|---|
| Icon m2 (HARD) | 202 | **202** (unchanged) |
| Icon m3 `--run` | 104 | **111** |
| Icon m4 `--compile` | 104 | **111** |
| Icon FAIL / EXCISED | 43 / 100 | 36 / 100 (pure FAIL→PASS) |
| Icon smoke | 12/12/12 | 12/12/12 |
| Prolog rung suite | 114/91/91 | 114/91/91 (exact) |
| Prolog smoke | 5/5/5 | 5/5/5 |
| SNOBOL4 / Raku | 7/7 · 35/35/35 | 7/7 · 35/35/35 |
| Snocone | 2/3 (pre-existing) | 2/3 (pre-existing) |
| no-stack / one-reg / FACT | 0 / 0 / 0 | 0 / 0 / 0 |

Snocone 2/3 was confirmed pre-existing by reverting (stash) + rebuild before the change
(`procedure`/`if_eq`/`while` already FAIL on pristine bd5f614).

---

## NEXT (clearly scoped, in priority order)

1. **`nested_to` — generators as TO bounds.** `(1 to 2) to (2 to 3)` wants 1,2,1,2,3,2,2,3; native
   gives 1,2. The inner generators (FROM/TO operands of the outer TO) must resume and re-drive the
   outer TO's `...` computation. Same shape as this session — `--dump-bb` it, find which ω/γ edge
   the native resolver mis-binds for a generator operand of an outer generator (vs. a binop), fix
   the resolver, keep m2 untouched. Likely the highest-yield next single-fix.
2. **`bb_every` four-port rebuild (architectural).** `bb_every.cpp` is logic-empty (`def β; jmp ω`);
   the loop drive lives in `flat_drive_every` (TEMPLATE-ONLY EMISSION violation). Build a real
   four-port box mirroring canonical `ir_a_Every` (start→gen; expr.success→body;
   body.success/fail→expr.resume = the loop; expr.failure→ir.failure), move topology out of the
   driver, kill the duplicate β stub. Own session; gate m2 HARD unmoved + loop rungs byte-checked.
3. **`cross_arg` ring protocol.** `write(1|2,3|4)`→ wrong (13,34,23,34). The `is_deep` CALL
   ag_ring is not maintained across literal-separated args on carry. Materially larger; fresh
   session.
4. **Real-arith native path (rc=134).** `descr_binop_opnd_slot` returns -1 for IR_LIT_F → real/
   mixed operands never slotted; arith template is int-only. Slot LIT_F + real-arith arm (SSE
   addsd/mulsd or rt_* DESCR arith). Unblocks rung17/18 + `2^3+1`.

## Key intel (reused this session, keep handy)
- m2 and m3/m4 share ONE lowering graph. If m2 is correct and native is wrong, the bug is in the
  native emitter (`descr_flat_chain_build` / walk_bb_flat), NOT lowering — a SAFE class (cannot
  move the m2 HARD gate). Confirm with `--dump-bb` (shows γ/ω node edges; chain indices in the
  asm `xchainN_nK_*` are CHAIN POSITIONS, not graph node ids).
- The flat resolver's γ and ω back-edges into earlier generators must both use β (resume), not α.
- `ir_is_generator_kind` (emit_bb.c:2065) is the generator-kind predicate; IR_EVERY is NOT in it.

## Files touched (SCRIP)
`src/emitter/emit_bb.c` only (two one-line changes in `descr_flat_chain_build`).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
