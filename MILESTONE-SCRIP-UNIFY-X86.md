# MILESTONE-SCRIP-UNIFY-X86.md — Unify x86 Executable

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-07
**Status:** ⬜ not started
**Depends on:** SCRIP-UNIFIED.md (design), current PASS=178

---

## Goal

Replace the `scrip-interp` / `scrip-cc` split with a **single `scrip` binary** for
the x86 platform. One executable, three execution modes, zero disk round-trips for
native code.

This is the x86 instance of a per-platform pattern. The JVM and JS platforms will
produce `scrip-jvm` and `scrip-js` respectively — each a self-contained interpreter
for their target. The x86 `scrip` is the primary development focus and the
correctness/performance reference.

---

## Binary Inventory — Before and After

| Before | After | Disposition |
|--------|-------|-------------|
| `scrip-interp` (pre-built, 647KB) | removed | replaced by `scrip --interp` |
| `scrip-interp-dbg` (pre-built) | removed | replaced by `scrip --interp` + debug flags |
| `scrip-interp-s` (pre-built) | removed | replaced by `scrip --interp` stripped |
| `scrip-cc` (Makefile target) | removed | replaced by `scrip --gen` / `--hybrid` |
| *(none)* | **`scrip`** | new unified binary |
| *(future)* | `scrip-jvm` | JVM interpreter (separate milestone) |
| *(future)* | `scrip-js` | JS interpreter (separate milestone) |

---

## Execution Modes (from SCRIP-UNIFIED.md RT-128 addendum)

```
scrip --interp      Mode I:  C tree-walk over IR. Correctness reference.
scrip --hybrid      Mode GS2: SM dispatch (phases 1/2/4/5) + BB-DRIVER (phase 3). [default]
scrip --gen         alias for --hybrid
scrip --stackless   Mode GS1: 100% stackless x86 blob chain, no SM dispatch overhead.
```

---

## Milestone Steps

### U0 — Remove pre-built binaries and rename driver ✅ partial
- [x] Remove `sno4parse` pre-built binary (done 2026-04-07, commit `7186f29c`)
- [ ] Remove `scrip-interp`, `scrip-interp-dbg`, `scrip-interp-s` pre-built binaries
- [ ] Rename `src/driver/scrip.c` entry point to unify `--interp` / `--gen` flags
- [ ] Root `Makefile`: rename target `scrip-interp` → `scrip`; remove `scrip-cc` target
- [ ] `src/Makefile`: change `BIN = ../scrip-cc` → `BIN = ../scrip`
- **Gate:** `make` produces `scrip`; `scrip --interp corpus/001.sno` passes

### U1 — Harness switchover
- [ ] Update all test scripts in `test/` that reference `scrip-interp` or `scrip-cc` → `scrip`
- [ ] Update `snobol4-asm.sh`, `snobol4-jvm.sh`, `snobol4-net.sh` wrapper scripts
- [ ] Update `harness/` repo references
- **Gate:** `run_invariants.sh` and `run_emit_check.sh` pass at PASS=178 with `scrip`

### U2 — Scrip image / segment allocator
- [ ] Create `src/runtime/asm/scrip_image.c` + `.h` — mmap slab allocator for 5 segments
  - segment 0: runtime stubs (RX)
  - segment 1: SM dispatch table (RX)
  - segment 2: program body (RX, variable)
  - segment 3: Byrd box pool (RW/RX, per-statement)
  - segment 4: data / constants (RW)
- [ ] Wire into `scrip --gen` path (replaces disk .s emission)
- **Gate:** `scrip_image_test` allocates all segments, mprotects, writes+calls a stub

### U3 — SM-LOWER (IR → SM_Program)
- [ ] Create `src/runtime/sm/sm_lower.c` + `.h`
- [ ] IR STMT_t/EXPR_t nodes → flat SM_Program (array of SM instructions)
- [ ] SM_PAT_* instructions for pattern phases; SM_EXEC_STMT for BB-DRIVER handoff
- **Gate:** `sm_interp_test` runs all 178 passing corpus programs via SM_Program

### U4 — Pattern integration (--hybrid default)
- [ ] Wire SM_PAT_* → BB-GRAPH build; SM_EXEC_STMT → BB-DRIVER call
- [ ] `scrip --hybrid` executes SM_Program via SM dispatch + BB-DRIVER for phase 3
- **Gate:** PASS=178 via `scrip --hybrid`; diff of `--interp` vs `--hybrid` trace is empty

### U5 — Stackless path (--stackless)
- [ ] Inline blob chain: each SM instruction → self-contained x86 blob, direct jmp wiring
- [ ] r13 = stmt frame ptr; BB-DRIVER inline; C stack only at static helper boundaries
- **Gate:** PASS=178 via `scrip --stackless`; M-DYN-BENCH-X86 filled (all 3 mode columns)

---

## Test Command Reference

```sh
# Smoke — all three modes must agree
scrip --interp   corpus/001.sno
scrip --hybrid   corpus/001.sno
scrip --stackless corpus/001.sno

# Full corpus
./test/run_invariants.sh

# Mode diff (must be empty after U4)
SNO_TRACE=1 scrip --interp  /tmp/x.sno 2>/tmp/interp.trace
SNO_TRACE=1 scrip --hybrid  /tmp/x.sno 2>/tmp/hybrid.trace
diff /tmp/interp.trace /tmp/hybrid.trace

# vs oracle
SNO_TRACE=1 scrip --interp /tmp/x.sno 2>/tmp/interp.trace
SNO_TRACE=1 /home/claude/x64/bin/spitbol /tmp/x.sno 2>/tmp/spitbol.trace
diff /tmp/interp.trace /tmp/spitbol.trace | head -30
```

---

## What Does NOT Change

- Frontend (CMPILE.c, IR) — unchanged
- Runtime (stmt_exec.c, bb_*.c boxes) — unchanged
- Corpus — unchanged
- BB-GRAPH, BB-DRIVER, BB-GEN-X86-BIN docs — unchanged (blob ABI unchanged)
- M-DYN-B* milestone chain — continues as-is; blobs slot into segment 3

---

*Written: 2026-04-07, Lon Jones Cherryholmes + Claude Sonnet 4.6*
*Design basis: SCRIP-UNIFIED.md (RT-125 + RT-128 addendum)*
