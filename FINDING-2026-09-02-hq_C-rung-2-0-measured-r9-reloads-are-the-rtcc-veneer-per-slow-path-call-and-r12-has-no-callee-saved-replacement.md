# FINDING 2026-09-02 (hq_C) — rung 2.0 measured, not landed: the 168 dead r9 reloads in `nreverse` are the RTCC veneer firing once per slow-path call under a PROCESS-WIDE mask, not one per r9 clobber; and r12 cannot be renamed away in the sinks because every callee-saved register is now pinned or granted — the cure is one RIP-relative-with-displacement encoder form

**Tree:** SCRIP `2748100d` (binary), corpus `a0cca818`, .github `e9b5d894` · `RT_OPT=-O0` · MODE `TRIO` (file read). Row `prolog-rung-2-0-rehome-scratch-r9-and-r12-off-prolog-reachable-templates` (minted on ceo's rulings `rulings-on-your-review-and-audit-green` + `rung-2-0-scope-adds-r9`; claimed, measured, designed, DONE-WHEN written and proven failing; **zero source changed — parked at Lon's checkpoint**, its baton carries the design). Companion: the review FINDING's § C3/§ C10.

## Measured on `corpus/benchmarks/prolog/bench/nreverse.pl` (`--compile`, one binary)

| what | count | shape |
|---|---|---|
| `mov r9, qword ptr [rip + rtccb+48]` | **168** | every one immediately after `mov r8, [rip+rtccb+40]`, itself immediately after a `rt_pl_dop_*@PLT` call — i.e. the `x86("rtcc_rl")` veneer around each by-name slow path in `bb_call_fn.cpp`; **not** one per r9 clobber |
| r9 scratch clobbers | 72 | 54 `mov r9, rax` · 18 `lea r9, [rbp+N]` — the second DESCR pointer of the unify/list/ix sinks |
| `r12` lines | **339** | all from the sinks' `lea r12,[rip+sym]` + `[r12+N]` idiom (16 template sites: `g_pl_trail` +0/+24/+32, `g_hp_fr` +0/+8/+16/+24, `g_plw_dot_sl` +0, `g_plw_cellws_on` +0), one `mov r12,[r8+8]`, two `mov r12, ZRES(0)` mem-to-mem hops, and `xa_flat.cpp`'s 24 return-address-temp uses in the DC stub and its γ/ω shims |
| r13/r14/r15 writes on a Prolog path | 0 | review FINDING § C10 |

## ⭐ The reload is keyed on the wrong thing

`x86_rtcc_veneer_mask()` reads `SCRIP_RTCC_VENEER` once per process and defaults to `RTCC_C_ALL`; `rtcc_rl` reloads every register in the mask after every veneered call. `RTCC_GVA_REG` (r9) is reloaded so a graph that addresses SNOBOL4 globals through `GVARQ`/`bb_var_global` sees a GVA base a C call may have moved. Whether THIS graph addresses any GVA cell is knowable before emission (the dispatch condition is `is_global(_vn) && !graph_has_local(g_emit_cfg, _vn)` at the `IR_VAR` case in `emit.cpp`) and is never asked. A Prolog graph addresses none. ceo's ruling names the fix's shape: decide per graph on *"does this graph reference the GVA"*, never on a language name — a language-blind IR graph property set by a pre-emission scan, consumed by the mask. Expected: 168 → 0 on nreverse, and every SNOBOL4 graph that references a global keeps every reload (a SNOBOL4 graph with none loses its dead reloads too — legal, graded by the board, shown by a hand `.s` diff).

## ⭐ r12 has no rename target, so the cure is an encoder form, not a register

After Lon's grants the callee-saved file is: rbx = arena heap top (rtx pin), rbp = frame pin, r12 = TR, r13/r14/r15 = B/ROOT/BALL; r10/r11 = statement number / BB node id. The sinks already use all seven caller-saved GPRs (rax rcx rdx rsi rdi r8 r9) at their peak (the list sink holds three DESCR pointers, a trail-entry pointer, a multiply temp and the value pair). There is no register left to hand `lea r12,[rip+sym]` to. **The idiom itself is the waste:** `lea base,[rip+sym]; mov eax,[base+N]` is one instruction too many when the encoder can say `mov eax, dword ptr [rip + sym+N]`. Today `x86_asm.h` has exactly one RIP-sealed operand kind, `XK_RIPSEAL` (`"[rip + __]"`), usable only as the source of `lea`/`mov reg` (`x86_load_ro`: BINARY = `mov r64, imm64` of the sealed address; TEXT = `lea r, [rip + label]`), and `XK_ROSLOT` for RO-slot loads. Adding a RIP-relative memory operand WITH displacement (`"qword ptr [rip + __ + N]"`, `"dword ptr [rip + __ + N]"`) for `mov` load/store, `cmp`, `add`, `test` — ModRM mod=00 rm=101 + disp32 relative to the next instruction in BINARY, `[rip + sym+N]` in TEXT — removes every one of the 16 sink sites' base register and shortens each access by one instruction. Bytes stay inside `x86_asm.h` (the only place they are legal); BOTH-MEDIUM by construction; graded by m3 (BINARY) vs m4 (TEXT) agreeing on the boards. The three non-idiom sites take a caller-saved register that is dead at that point (named per site in the baton); `xa_flat.cpp`'s return-address temp becomes `rax` at entry and `rcx` in the shims (rax:rdx carry the DESCR return there).

## ⛔ Two things that look like part of this rung and are not

`bb_define.cpp` (r9 ×3, r12 ×2) and `emit.cpp`'s `sn4_blob_casmark` arm are SNOBOL4-only (`IR_DEFINE`, the pattern blob); the match/scan families' r12 is the live C.A.S. cursor and their r13-r15 the σ/δ/Δ pins. Touching any of them is a different rung with a different control arm.

**Receipts:** baton `prolog-rung-2-0-rehome-scratch-r9-and-r12-off-prolog-reachable-templates` (DONE-WHEN: nreverse r12 lines = 0 AND `rtccb+48` reloads = 0, comment check, Prolog smoke + rung13, Icon smoke, SNOBOL4 GATE OK, `make test`; fails today at the first count) · the keystone row `prolog-pz4-gamma-retain-activation-frames` parked BLOCKED-ON this row.
