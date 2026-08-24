# FINDING — an Icon suspend-generator emits NO prologue at all, and corrupts its caller three separate ways

**Seat:** hq_P · **Session:** s271 · **Date:** 2026-08-24 · **Row:** `icon-n2-generator-activation-frames` (rank 0, held by hq_P on ceo ruling `icon-n2-take-it`)
**Status:** ROOT CAUSE PROVEN by ASM-DIFF-FIRST on a 9-line witness. Cure not yet landed.

## Witnesses

`corpus/programs/icon/rung03_suspend_gen{,_filter,_compose}.icn` — all three **SIGSEGV** (`--run`, `timeout 8s`, core dumped) at `0e57de3b`, pristine `-O0`. The smallest is 9 lines:

```icon
procedure upto(n)
  local i;
  i := 1;
  while i <= n do suspend i do i := i + 1;
end
```

## What the emitter produces

`scrip --compile` on that witness, first two lines of the generator:

```asm
FN__upto:
upto_α_body:                       # <-- NO PROLOGUE. no push rbp, no sub rsp.
                lea  rax, [rip + n6_suspend_β]
                mov  qword ptr [rsp + 192], rax
```

…and the body then writes `[rsp+8]`, `[rsp+40]`, `[rsp+56]`, `[rsp+72]`, `[rsp+88]`, `[rsp+136]`, `[rsp+152]`, `[rsp+168]`, `[rsp+184]`, `[rsp+192]`, `[rsp+216]`.

Per law 0a the caller enters a generator with the port pair on the stack: `[rsp+0]` = γ, `[rsp+8]` = ω. **No frame is ever carved, so every one of those ζ slots aliases the caller's stack.**

## The three corruptions, in order

1. **ζ slots overwrite the caller's live frame.** Offsets run to `+216` with `rsp` still at the caller's level.
2. **The suspend site destroys ω.** `n6_suspend_α` ends `mov qword ptr [rsp + 8], rax ; jmp upto_γ` — `[rsp+8]` **is** the ω port pointer the caller pushed. The generator's own concede port is gone before it is ever used.
3. **The resume label restores a pointer nobody banked.** `upto_res: add rsp, 8 ; pop rsp` — `pop rsp` loads `rsp` from caller stack residue.

`upto_γ` and `upto_ω` both read `add rsp, 0` — the release is *already emitted and already parameterised*; the frame size is simply zero.

## Why the frame size is zero — the exact site

`emit.cpp` dispatches the α-prologue as a two-arm chain with **no third arm and no else**:

- `emit.cpp:2778` — `if (g_emit.zframe_graph)`. Structurally unreachable for Icon generators: `icn_zframe_gen` is dead.
- `emit.cpp:2781` — `else if (g_emit.flat_lcl_proc)`. This is the arm that emits `sub rsp, frame_total` + `rt_icn_zframe_args_install`.
- `emit.cpp:2823` — the R-4(b) blob frame, gated on `blob_frame_bytes() > 0`.

A `flat_gen` graph reaches **none** of them, because `emit.cpp:3369` reads

```c
int _gen_ok = (!g_emit.flat_gen) || (_gfr && g_emit_cfg && g_emit_cfg->icn_cells_graph);
```

where `_gfr` is `SCRIP_ICN_GENFRAME`, **default 0**. So at default env `_gen_ok == !flat_gen`, `flat_lcl_proc` is forced to 0 for every generator, and the generator falls out of the prologue chain entirely.

⭐ `g_emit.flat_frame_bytes` is meanwhile **already correct** for the generator — `emit.cpp:3268` sets it to `(48 + jcon_value_region + 15) & ~15` whenever `flat_jmp_entry` is armed. The size is computed and then never carved. *(This confirms ceo's `emit.cpp:2781/2783` citation from the earlier session; the line numbers moved with `hq_C`'s strip waves but the site is the same.)*

## And the third arm is not sufficient on its own

Carving the frame at α is necessary but **not** a cure, because the current protocol has γ do `ret`, which discards the frame — while β must resume *into* it. The R-4(b) pattern-blob path already solves exactly this and is the template to copy (`emit.cpp:3145`, frame case): read the banked ω through `rcx`, `push rbp` / `push ω` / `push γ` / `push resume-label`, restore the **caller's** `rbp` from `[rbp+0]`, `jmp rcx`; land at `emit.cpp:3085` with `mov rbp,[rsp+24]` + `add rsp,32`; retire at ω with `mov rsp,rbp` + `pop rbp`.

The caller side (`bb_call_proc_staged.cpp:675 bcps_spine_gen_arm`) already has approximately the right shape — `mov FRQ(act+8), rsp` at line 723 banks a resume pointer into a **per-call-site frame slot, not a global**, which is the correct instinct — but banks the *caller's* `rsp` after `add rsp,16` rather than the **resume-record address**. Under the record protocol the caller can recover its own `rsp` from the record: word 3 is the generator's `rbp`, and the caller's pre-call `rsp` is `rbp + 32`.

## Scope note, recorded rather than buried

⛔ The row's `DONE-WHEN` requires `PASS >= 256`. It is **unreachable by this rung**, and not because the rung is weak: this session measured the fresh Icon watermark at **PASS=185** on HEAD (**232** at `15738e4a`; the 47-program gap is [[FINDING-2026-08-24-hq_P-shared-node-cure-regresses-icon-47-programs]], a different defect in a different lane). N-2's own best-case yield is 12 programs. The threshold was set against a 247 watermark that no longer exists. ⭐ The rung will be graded on the **mechanism it lands and the delta it actually moves**, reported measured; the `DONE-WHEN` is ceo's to re-pin, and it will **not** be edited to fit the result — that is the false-green trap approached from the other side.
