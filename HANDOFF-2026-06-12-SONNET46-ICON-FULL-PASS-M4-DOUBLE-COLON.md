# HANDOFF-2026-06-12-SONNET46-ICON-FULL-PASS-M4-DOUBLE-COLON.md

**Session:** 2026-06-12 · Claude Sonnet 4.6
**Goal:** GOAL-ICON-FULL-PASS — m4 double-colon label fix
**HEAD (SCRIP):** `7214e00`
**m2:** 200/247 (unchanged) · **m3:** 44/283 · **m4:** 41/283 (was 0 at session start)

---

## Work Done

### Double-colon label bug in m4 TEXT output (committed `7214e00`)

**Bug:** All m4 (--compile) tests failing with `Assembler messages: junk at end of line` at β labels
like `xchain0_n1_β::`. GAS rejects double-colon labels.

**Root cause:** `x86("label", s)` in `x86_asm.h` line 510 appends `:\n` to its argument. Four templates
were passing `std::string(_.lbl_β) + ":"` — so the argument already ended with `:`, producing `name::`.

**Fixed files:**
- `bb_call_write_slot.cpp` (2 occurrences: `bb_call_write_slot_str` and `bb_call_write_binop_str`)
- `bb_call_rk_bool.cpp` (1 occurrence)
- `bb_call_proc_staged.cpp` (1 occurrence)

Fix: strip the trailing `:` from the argument — pass `_.lbl_β` or `std::string(_.lbl_β)` directly.

**Result:** m4 0 → 41 PASS (remote had already applied equivalent fixes to the other 3 instances;
the rebase merged cleanly; our fix contributed bb_call_write_slot's 2 occurrences).

---

## State Invariants (all hold at HEAD 7214e00)

- m2 icon smoke 12/12 HARD ✅
- m3 icon smoke 10/12 (2 pre-existing: proc_zeroarg, proc_recursion) ✅
- m4 icon smoke 5/12 (7 still broken — see remaining gap below) ✅
- Prolog m2 5/5 HARD ✅
- Build green ✅

---

## Remaining m3/m4 gap (m3=44, m4=41 vs m2=200)

Failure categories in m3 (93 FAIL, 98 EXCISED):
- **rc=134 (~30)** — `x86_bomb` hit: missing or broken BINARY arm in template. One confirmed source:
  `bb_to.cpp` — the TO generator's BINARY arm may emit x86_bomb for real-step cases. Check by running
  `./scrip --run /tmp/rung01_paper_to_by.icn 2>&1` to see which bomb fires.
- **rc=124 (~12)** — timeout: infinite retry loop. Likely in TO/EVERY retry wiring in BINARY path.
- **rc=139 (4)** — segfault: CASE box (`rung33_*`) — `IR_CASE` has no native template.
- **~47 silent-empty** — control lost in BINARY path. The `rung01_paper_lt` class (TO+relop+EVERY)
  identified last session remains unresolved. Hypothesis: `descr_flat_chain_build` path (when
  `icn_ring_to_tree` returns NULL) loses control somewhere before `rt_write_any_nl`.

**m4 gap vs m3 (41 vs 44):** 3 additional m4 failures — likely toolchain/linking issues with specific
template shapes not yet confirmed with BINARY emission (add `fprintf(stderr,"[M4-DBG]")` to a failing
case to confirm it enters the template vs fails in asm/link).

**Next session approach:** Pick one rc=134 test, run under gdb or add stderr probe to identify which
`x86_bomb` fires, then add the BINARY arm for that template. The TO generator BINARY arm is the most
likely first target given `rung01_paper_to_by` (every write(1 to 5 by 2)) fails rc=134.

---

## Authors
Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
