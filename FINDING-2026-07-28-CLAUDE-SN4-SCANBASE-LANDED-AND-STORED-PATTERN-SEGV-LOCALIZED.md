# FINDING-2026-07-28-CLAUDE-SN4-SCANBASE-LANDED-AND-STORED-PATTERN-SEGV-LOCALIZED.md

## Summary

Two findings from s198 (2026-07-28).

**(1) SCANBASE — independently reproduced and landed** (census 119→113, watermark held exactly).
s196's SCANBASE commit `a0e83fe2` was never on origin — origin HEAD at session start was `62aaf9ff` (s195).
SCANBASE was reconstructed from first principles against the manual and byte-verified, then committed as `6c16762a`.

**(2) STORED-PATTERN SEGV — localized to `bb_match_release.cpp`**, narrower than and independent of
s197's deferred-argument bug. Minimal two-line reproducer. Fix direction mapped; one attempt measured and
reverted (wrong compensation class). Root cause documented below.

---

## (1) SCANBASE — Reconstruction

### Origin state at session start

`a0e83fe2` (s196 SCANBASE) is not a valid git object in origin.
Origin HEAD = `62aaf9ff` (s195), census ratchet baseline = 119.
This was confirmed via `git cat-file -t a0e83fe2` → `fatal: Not a valid object name`.
The s196 and s197 cursors both describe a tree that was never pushed.

### What SCANBASE does

`bb_match_head.cpp` (`scan_live` arm, `emit.cpp` line 1822) emits two SPD-2 scan-slot prologue stores
immediately after the jmp-entry `mov rbp,rsp` seed:

```
[kt-32]  scan flag  (caller r8)
[kt-40]  attempt start (r14d)
```

These were emitted `[rbp + kt-32]` / `[rbp + kt-40]` in both TEXT and BINARY.
SCANBASE rebases them to `[rsp + kt-32]` / `[rsp + kt-40]`.

### Premise re-proven (and s196's stated reason corrected)

s196 claimed the stores are "one instruction after" the seed — they are **seven** instructions after it
(only `[rsp+N]` zero-fills intervene). The relevant invariant still holds, but for a different reason:
none of those seven intervening instructions modify rsp.

Verified mechanically for all three blob-bearing benchmarks (`string_pattern`, `pattern_bt`, `mixed_workload`)
by walking the emitted assembly and asserting that no rsp-modifying instruction (`sub/add/lea rsp`, `push`,
`pop`) appears between the seed and the first `[rbp+kt-N]` store.

### R10 defect fixed in passing

The old BINARY arm emitted ModRM `0x85` / `0xB5` (disp32) unconditionally.
`as` picks disp8 for `kt-40 = 120` in every measured blob (`44 89 75 78`), so BINARY diverged from
its own TEXT arm at those offsets.

New BINARY: selects disp8/disp32 based on signed-byte range, using `SIB 0x24` (mandatory for
`[rsp+N]` addressing). All four encodings verified byte-for-byte against `as`:

```
mov qword ptr [rsp+128], r8    → 4c 89 84 24 80 00 00 00
mov dword ptr [rsp+120], r14d  → 44 89 74 24 78
mov qword ptr [rsp+144], r8    → 4c 89 84 24 90 00 00 00
mov dword ptr [rsp+136], r14d  → 44 89 b4 24 88 00 00 00
```

### Results

- Census: NET 119 → 113 (−6: 2 stores × 3 blob-bearing benchmarks)
- Ratchet baseline lowered 119 → 113 in the same commit per the gate's own TIGHTEN rule
- Watermark held exactly: m3 221/94 · m4 219/94 SKIP=2 · DIVERGE=1 (W06_tab)
- FAIL-set membership: byte-identical, zero churn
- Commit: `6c16762a` (SCRIP)

### Prose-rot in mandatory docs (named, not fixed — s196 named these too)

- `ARCH-ICON.md`: says FR/FRQ resolve `[rbp+off]` "no depth compensation, sealed U5 s87" —
  FALSE; `x86_fr32_prefix()` is hardcoded `dword ptr [rsp + ` (line 362).
- `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`: says ζ-scratch is `[r12+off]` — dead since R12-ERAD s65.
- `x86_asm.h:841` FR()'s comment: "rbp is depth-immune" three lines under the rsp-only prefix it calls.

---

## (2) STORED-PATTERN SEGV — Localization

### The bug s197 did not describe

s197 identified the deferred-argument family as broken (`LEN(*N)`, `TAB(*I)`, `SPAN(*C)`).
That is confirmed but it is **not the most fundamental defect**.

A **stored pattern variable** segfaults regardless of whether its argument is deferred:

```snobol
        NPAT = ':'
        'xx:ab' ? NPAT
        OUTPUT = 'DONE'
END
```

Oracle: `DONE`. Scrip m3: SIGSEGV rc=139. Scrip m4: SIGSEGV rc=139.
Two lines, no capture, no pattern function, no deferred argument. The inline form `? ':'` passes.

This is **DIVERGE-blind** — both modes fail identically, so the crosscheck cannot see it; only the
oracle catches it. It is almost certainly the cause of a large share of the 94-FAIL set.

### Backtrace (mode-4, symbolized)

```
#0  n5_match_release_α+20  (push %r14)
rip = 0x555555555460
rsp = 0x2
```

`n5_match_release_α+15` executes `mov rsp, qword ptr [rsp+64]`, loading `2` into rsp.
The subsequent `push r14` faults.

### Measured: rsp at save vs. restore

gdb breakpoints at `n4_match_defer_α` and `n5_match_release_α`:

| stop | box | rsp |  `[rsp+64]` |
|------|-----|-----|-------------|
| 1 | `match_defer` | `0x7fffffffe8e0` | `0x7fffffffe8e0` ✓ |
| 2 | `match_defer` | `0x7fffffffe8e0` | `0x7fffffffe8e0` ✓ |
| 3 | `match_defer` | `0x7fffffffe8e0` | `0x7fffffffe8e0` ✓ |
| 4 | `match_release` | `0x7fffffffe8d0` | `0x2` ✗ → FAULT |

**`match_release` arrives 16 bytes deeper than `match_defer`.** It reads `[rsp+64]` at that
deeper rsp and lands 16 bytes past the saved slot, which happens to hold `2`.

### Root cause

`bb_match_release.cpp` tail arm (the `op_tail` branch, lines 82–88):

```cpp
+ x86("mov", "rax", RSP((int)_.op_fc_disp + 0))   // patstk_sp restore
+ x86("mov", "rsp", RSP((int)_.op_fc_disp + 8))   // rsp restore
```

`RSP()` is defined in `x86_asm.h:1048` as a **raw, uncompensated** reference:

```cpp
inline const char * RSP(int off) { ... snprintf(b[i], 40, "qword ptr [rsp + %d]", off); return b[i]; }
```

It bypasses `x86_frame_off()`, which is declared "THE ONE OFFSET FUNCTION … nothing else may add
a frame displacement." The offsets (`op_fc_disp + 0/8` = 56/64) match `match_head`'s *write* offsets —
but `match_head` wrote at a different depth.

### Fix attempt tried and reverted

Applied `+ (int)_.op_flat_disp` compensation to both RSP() calls (the static prefix-sum correction
used by FRQ/FR). Rebuilt and tested — no change. Emitted offsets were still `[rsp+56]`/`[rsp+64]`.

`op_flat_disp` is **0** for this box. The missing 16 is **dynamic**, not static: it is the
deep-window handoff offset from `x86_frame_sink` ("park old-rsp below the carved frame, hand the
callee a frame base of rsp+16"). No static prefix sum can capture it.

This is the same wall s196 hit on the scan-retry unwind: *"recovering base from a REGISTER is the
only way back when rsp is at unknown depth."*

Reverted cleanly. Working tree 0 modified files. Watermark re-confirmed after revert.

### Candidate fix direction

The deep window (`x86_frame_sink`, `x86_anchor_enter/leave`) already parks the old rsp below the
carved frame and releases with `mov rsp,[rsp]`. If `match_release` is **always** entered through
a deep window, the restore should use the parked anchor rather than the cross-box slot:

```cpp
+ x86("mov", "rsp", "[rsp]")   // deep-window anchor release
```

**Mandatory before any fix:**

1. Confirm `match_release` is always entered through a deep window (not sometimes balanced).
   If it has both entry paths, unconditional anchor-deref breaks the balanced path.
2. Confirm the delta is always 16 or verify it varies (varies → anchor-deref is the only option;
   invariant → the handoff is uniform, simplifying the fix).
3. Monitor-first per RULES.md: run `scripts/test_monitor_2way_sync_step_bin.sh` on `m_var.sno`
   with `PARTICIPANTS="spl scr"` to bracket the first divergence before touching any code.

### NEXT RUNGS IN ORDER (updated)

(a) **STORED-PATTERN SEGV** — monitor-first on `NPAT = ':' / ? NPAT` (cheapest reproducer),
    anchor-deref fix in `bb_match_release.cpp` tail arm. Map both entry paths first.
(b) **DEFERRED-ARG BUG** — monitor-first on `LEN(*N)` (wrong value, not crash). Some of the
    94 FAILs named `056_pat_star_deref`, `070–075_pat_star_*` may be this root — check after (a)
    resolves the stored-pattern segv, which likely dominates.
(c) **ARBNO-ELEM dig** — per s195 cursor. Value-spine window map first.
(d) **fc_cond FIRST-WINS audit** — per s195 cursor.
(e) **SYM-VIS-M3** — perf JIT map for m3 (SCRIP_PERF_MAP=1).

---

## Miscellaneous

- gdb was NOT installed in the container at session start. Required `apt-get install -y gdb`.
  RULES.md's entire bug-finding methodology assumes gdb. Worth baking in.
- The absolute address `[0x70001000]` in mode-4 text (`n4_match_defer_α`) is NOT a bug —
  `pin_va.h` defines `RT_PIN_BASE 0x70000000` as a deliberately pinned VA below the
  absolute-disp32 ceiling. Absolute addressing there is by design in both modes.
- Bisection table (all forms tested against the oracle):

| pattern shape | inline | stored-in-var |
|---|---|---|
| `':'` literal | OK | **SEGV** |
| `LEN(3)` literal arg | OK | **SEGV** |
| `LEN(*N)` deferred arg | empty capture | **SEGV** |
| no-capture literal | OK | **SEGV** |
