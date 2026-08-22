# FINDING — s256 HQ: `free-r10` and `free-r11` had an INVERTED DONE-WHEN, and it made the two rows mechanically destroy each other

**Date:** 2026-08-22 · **Seat:** HQ (`/home/claude`, Claude Opus 5, s256) · **Topics:** `free-r10`, `free-r11`, `diag-regs-stmt-and-bb` · **Status:** RULING. Both rows are **DONE as they stand**. The blocker on `diag-regs-stmt-and-bb` is **dissolved**. Two genuinely open mechanisms split out as new rungs. **HQ's own error, diagnosed and corrected here.**

## 1. What Lon asked for

Verbatim in substance, 2026-08-22 in-chat: *"R10 and R11 are free, they used to be reserved for GAMMA and OMEGA which is now replaced by PUSH-PUSH at RBP."*

That sentence **lifts a reservation**. A free register is one that any code MAY use as ordinary caller-saved scratch. It is a statement about the register *contract*, not about how many times the string `r10` appears in the tree.

## 2. What HQ wrote instead

Both briefs' DONE-WHEN: *"r10 has ZERO uses in `src/templates` and `src/emitter`."*

Zero uses means **nobody may use it** — a *stricter* reservation than the one being lifted. The criterion measured the opposite of the goal, and it can never go green, because freeing a register is precisely what makes ordinary uses of it legal and expected. **This was HQ's error, not a seat's.**

## 3. Measured proof that the two rows were destroying each other

`git grep -cE "\br1[01][dwb]?\b" -- src/templates src/emitter`:

| commit | r10 | r11 |
|---|---|---|
| `0ff71be8` (before seat3's scratch move) | 136 | 91 |
| `ef553d3a` (after) | **65** | **152** |

r10 fell by 71. **r11 rose by 61.** seat3, chasing r10 toward zero, moved 71 scratch sites off r10 and onto **r11 — the sibling register the same directive frees** (correctly avoiding r8/r9, which carry live ANCHOR/GVA). A seat then running `free-r11` to the old DONE-WHEN would move those same sites back onto r10, re-opening `free-r10`. **A closed loop: neither row could ever close, and the dependent row's gate could never open.**

## 4. The census instrument enforced the design that was just superseded

seat6 ran STEP 1 with `scripts/test_gate_wreg_claim.sh --strict`. That gate's own header states its purpose:

> "LADDER WREG **reserves** rΓ=r10 and rΩ=r11 as PRODUCT-WIDE dynamic wire registers … **Who MENTIONS r10/r11 at all, outside the sites licensed to own the wires?**"

It is LADDER WREG's *enforcement arm* — the very design PUSH-PUSH-at-RBP superseded at s195. Its "248 unlicensed occurrences across 25 files, plus 225 in the RTX `.S` files" is **debt against a license that no longer exists**. It also sits at `WREG_CLAIM_LIVE=0` (informational tier, exits 0), so it was never blocking anything. seat6's numbers are accurate and its measurement discipline was better than HQ's; the instrument was pointed at the wrong invariant.

## 5. Two seats, one directive, opposite definitions of done — both shipped

- **seat3 (`free-r10`)** read it as near-textual-zero: eradicated the dead WREG fallback (`0ff71be8`, 34 sites — `bb_wire_stack_on()` deleted, dead arms out of `bb_glue_flat.cpp`, `emit.cpp`, `bb_match_defer.cpp`, `bb_define.cpp`, `rt.c`), then moved 71 scratch sites (`ef553d3a`). Claim marked DONE.
- **seat4 (`free-r11`)** read it as reservation-lifted: landed the contract amendment and the `rtx_zdp.S` comment correction (`ff84322c`), no code movement. Claim marked DONE.

**seat4's reading is the correct one.** seat3's eradication half was also correct and valuable — the *dead fallback* genuinely had to go. Only seat3's second pass (the 71-site scratch move) was work done under the wrong criterion. **It stays**: it is byte-behaviour-verified, harmless, and reverting it is pure churn.

## 6. THE RULING — the new DONE-WHEN is a contract predicate, never a grep count

A register is FREE when all three hold:
1. **No product-wide γ/ω wire on it.** ✅ Already true — `rtx_zdp.S:9` states the retirement in-tree; `ARCH-SNOBOL4-RTX.md` §2 records it with Lon's directive quoted.
2. **Every DEDICATED (non-scratch) use is named in `ARCH-SNOBOL4-RTX.md` §2.** ✅ Already true — four classes documented.
3. **Ordinary scratch use is LEGAL and requires no action.** This is what "free" *means*.

⇒ **`free-r10` and `free-r11` are both DONE.** ⇒ **`diag-regs-stmt-and-bb` (seat8) is UNBLOCKED** — its stated blocker ("a half-freed register is the s194 collision") was an artifact of the inverted criterion. seat8 read the criterion correctly and was right to refuse to start; the criterion was wrong.

⛔ **No seat may re-open either row on a grep count.**

## 7. Confirmed non-issues — do not chase these

- **`bb_call_fn.cpp`** (52 r10 / 34 r11): `lea r10,[rip+g_pl_trail]` then loads off `[r10+0/24/32]` — a base pointer to a global struct, r11 a load target. Ordinary scratch. **Legal.** seat6's guess ("inline-cache scratch, not a wire") was right.
- **The 19 `bb_scan_*.cpp` files** (4 r11 each): `push r11` … `pop r11`. Save-and-restore scratch. **Legal.**
- **`bb_define.cpp:138-145`** (monitor save): pushes all 8 non-rax caller-saved GPRs around an opaque splice. **Cannot reach zero as a matter of definition** — it protects whatever meaning *other* code gave the register, so it must keep naming every register that could hold one. seat3 was right; ruling confirms it.
- **`GOAL-PASSTHRU-RBP-ERAD.md`**, which seat6 flagged as a live resurrection risk for the rival LADDER WREG design: **the file does not exist.** Renamed to `GOAL-RBP-EARN.md` at `d114f372` (s25c). seat6 was reading a stale name. No action needed.

## 8. What is genuinely still open — two new rungs, both already flagged high-blast-radius in §2

- **`wire-suspend-cache-clobber`** — `src/emitter/emit.cpp:2744` (entry) / `:3052` (suspend), `_bfb <= 0` frameless arm only. A frameless blob reads its caller-pushed {γ,ω} pair out of `[rsp]` once at entry into r10/r11, purely so a later suspend point can build a resume record and `jmp r10` without re-touching the stack. **Nothing enforces that box-body code emitted between entry and suspend avoids clobbering r10/r11** — the identical shape `FINDING-2026-08-20-s194b`/`s194c` convicted. Both registers.
- **`define-shim-omega-half`** — `src/templates/bb_define.cpp:471` and `:525` (IR_DEFINE role 4, the s63/s64 activation shim). `lea rcx,[γ]; lea r11,[ω]; push r11; push rcx`. seat3 already moved r10's half to `rcx` (proving `rcx` dead across the shim's span in both arms, re-verified on a live `DEFINE('F1()')` witness in m3 and m4). **r11 still carries ω into every call of every user-written SNOBOL4 procedure** — not an edge case, and the reason both seats deliberately left it.

## 9. Also owed — retire the superseded instrument

`scripts/test_gate_wreg_claim.sh` and `test_gate_wreg_claim_binary.sh` police the retired LADDER WREG reservation and will keep producing burn-down numbers against a dead license, misdirecting any future seat exactly as they misdirected this ladder. Row: `wreg-gate-retire`. Small.

## 10. HQ's own lesson (LAW 18's shape, one level over)

s255 closed three laws that were *trivially satisfiable by inaction* or *required knowing the unknowable*. This is the dual defect and it belongs on the same sweep: **a criterion that can never say YES is as broken as one that can never say NO.** The old DONE-WHEN could not be satisfied by any amount of correct work — and three seats spent sessions discovering that, each correctly, none able to act on it because only HQ could rule. ⭐ **Generalise: before writing a DONE-WHEN, ask what the tree looks like when the goal is FULLY achieved, and check the criterion is TRUE of that tree.** Here, the fully-achieved tree has r10/r11 used *freely and often* — the criterion demanded the opposite, and said so in every brief for three sessions.

**Routed:** this FINDING · `ARCH-SNOBOL4-RTX.md` §2 (ruling banner) · `GOAL-SCRIP-HQ.md` cursor + queue mirror · `QUEUE.tsv` rows `free-r10`/`free-r11` DONE-WHEN replaced, `diag-regs-stmt-and-bb` unblocked, new rows `wire-suspend-cache-clobber` · `define-shim-omega-half` · `wreg-gate-retire` · replies to seat3 (`q-free-r10-zero-scope`, `q-free-r10-brief-numbers`), seat6 (`q-free-r11`), seat8 (`q-diag-regs-stmt-and-bb`).
