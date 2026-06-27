# GOAL-ICN-GVA-M3.md — Icon globals in mode-3 (in-process RX slab) via runtime heap arena

## One-line
Extend the GST/GVA `[rbx+k*16]` slot-array facility to mode-3 (`--run`, in-process RX slab),
eliminating the last NV hash round-trips for Icon global reads/writes in the native in-process path.

## Status: OPEN (2026-06-24)

**Prerequisite DONE:** ICN-GVA (GST-1/2 + GVA-1/2) landed 2026-06-24 — mode-4 globals are
`[rbx+k*16]`, gate `test_gate_icn_local_no_nv.sh` PASS (3 locks). Mode-3 globals still use
NV hash (`g_gva_active` never set on m3 path). SNOBOL4 is identical — m3 also on NV, for
the same reason. This rung is Icon-scoped; SNOBOL4-m3 is a separate concern.

## Why m3 still uses NV (root cause, verified 2026-06-24)

1. **`g_gva_active` is only set on the mode-4 text-emit path** (`src/driver/scrip.c:2640`).
   The mode-3 in-process builder (`bb_pool_init` → RX-slab) never activates GVA.
2. **The RX slab has no writable region.** `bb_pool.c:42` seals the code blob
   `PROT_READ|PROT_EXEC` — writing a DESCR into it would SEGFAULT. Mode-4 uses `.bss __gva`
   (writable BSS in the linked binary); m3 has no equivalent emit mechanism.
3. **`gva_register(names, cells, n)` (rt.c:222) already accepts a caller-supplied
   `DESCR_t *cells` array** — it does NOT require the array to be in `.bss`. So a
   heap-allocated arena (`calloc(n, sizeof(DESCR_t))`) is a drop-in substitute for the
   `.bss __gva` pointer. The runtime side needs no change.

## Design

### M3-ARENA-1 — heap-allocate the GVA cell array in the mode-3 driver
In `src/driver/scrip.c`, the mode-3 Icon path (near `bb_pool_init`, before the proc-body
emit loop) must mirror what mode-4 emits at runtime, but call the runtime *directly* (we are
already in the same process):

```c
// after gva_collect_icon_globals() / gva_count() — same collection already done for m4
int n_gva_icn = gva_count();
DESCR_t *m3_gva_arena = NULL;
if (n_gva_icn > 0) {
    m3_gva_arena = (DESCR_t *)calloc((size_t)n_gva_icn, sizeof(DESCR_t));
    if (!m3_gva_arena) { fprintf(stderr, "FATAL: m3 GVA arena alloc\n"); abort(); }
    const char **names = /* build name array from gva_name(k) */;
    gva_register(names, m3_gva_arena, n_gva_icn);   // binds each name to its cell
    g_gva_rbx_base = (uintptr_t)m3_gva_arena;        // new global — rbx initialiser
    g_gva_active = 1;
}
```

`m3_gva_arena` lives for the lifetime of the process (never freed). `gva_register` handles
the `NV_bind_gva` side so reflective paths (image/EVAL) still work.

### M3-ARENA-2 — initialise rbx before jumping into the BB slab
The mode-3 jump-in preamble (the generated code that calls `main_α`) must load `rbx` with the
GVA base before entering any box, exactly as mode-4's `call gva_register; mov rbx,rax` does.
Two sub-options, choose the simpler:

**Option A (recommended) — emit a tiny C preamble stub that sets rbx then jumps into the slab:**
```c
// In the m3 driver, instead of a raw function pointer call into the slab:
typedef void (*icn_entry_t)(void *zeta);
// ... generate a tiny thunk: mov rbx, <arena_addr>; jmp slab_entry
// Or: just set rbx in C before the jmp, using __attribute__((naked)) or inline asm.
```
The simplest correct form: emit a small `mmap`'d or stack-allocated trampoline that does
`mov rbx, imm64; jmp slab_entry_α`. rbx is callee-saved; once set in the trampoline it is
preserved across all box transitions.

**Option B — add a `g_gva_rbx_base` global read at the start of the m3 slab preamble:**
The RX slab's existing preamble (`mov r12,rdi; jmp .Lroot_α` shape, `XA_templates/xa_flat.cpp`)
could be extended to load `rbx` from a known global:
```asm
mov rbx, qword ptr [rip + g_gva_rbx_base]
```
This touches `xa_flat.cpp`; keep it behind `g_gva_active` so non-GVA paths are unaffected.

**Option B is simpler** (no mmap trampoline, no inline asm) and is recommended because
`xa_flat.cpp` already exists and is the sanctioned m3 preamble location.

### M3-ARENA-3 — gate the emitter arms on `g_gva_active` (already done)
`bb_var_global.cpp` and `bb_gvar_assign_descr.cpp` already gate on `g_gva_active` before
emitting `[rbx+k*16]`. No template change required — those arms are already correct for m3
once rbx holds the arena base.

### M3-ARENA-4 — verify + gate
After the above:
- `rung25_global_global_basic` m3: `counter` accesses → 0 NV calls, result still 3.
- Extend `test_gate_icn_local_no_nv.sh` LOCK 3 to also check m3 (currently only m4).
  Or add a new `test_gate_icn_global_no_nv_m3.sh` gate that runs a globals-only program
  with `--run` and greps the binary strace / runtime log for NV_GET/NV_SET.
- Smoke 12/12 m3+m4 must stay green; suite 151/283 must not decrease.

## Steps

- [ ] **M3-ARENA-1** — In `scrip.c` mode-3 Icon build path: call `gva_collect_icon_globals()`,
  `calloc` the cell array, call `gva_register`, set `g_gva_active = 1` and store the arena
  base for the preamble (new `g_gva_rbx_base` or pass directly to the xa_flat preamble emit).
  Scope: `src/driver/scrip.c` only (Icon m3 block). Add `g_gva_rbx_base` extern to a shared
  header if used across files.

- [ ] **M3-ARENA-2** — In `xa_flat.cpp` (or the m3 preamble emitter), after the existing
  `mov r12,rdi` preamble, add (gated on `g_gva_active`):
  `x86("mov", "rbx", G_GVA_RBX_BASE)` or the `[rip+g_gva_rbx_base]` load form.
  Verify via `objdump`/strace that rbx holds the arena address at first box entry.

- [ ] **M3-ARENA-3** — Confirm `bb_var_global` and `bb_gvar_assign_descr` reach the
  `[rbx+k*16]` arm in m3 (they are already gated; just verify the gate fires). Run
  `rung25_global_global_basic --run` and confirm result=3 with zero NV calls.

- [ ] **M3-ARENA-4** — Extend or add a gate that locks m3 globals off NV. Run full suite;
  confirm 151/283 baseline holds (or improves). Run all four existing gates. Commit.

## Completion test
(a) `rung25_global_global_basic --run` → 3, zero NV_GET/NV_SET on the global-access path;
(b) `test_gate_icn_local_no_nv.sh` (or successor) green for m3 globals;
(c) suite ≥ 151/283 both modes; smoke 12/12 both modes; all discipline gates green;
(d) SNOBOL4 smoke unaffected (shared runtime, no SNOBOL4 m3 path changed).

## Cross-language note
SNOBOL4 m3 has the identical gap (globals on NV). Once this rung proves the m3-arena
pattern for Icon, SNOBOL4-m3 follows the same template in its own m3 driver block —
a separate rung, separate commit, no cross-contamination.

## Authors
Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
