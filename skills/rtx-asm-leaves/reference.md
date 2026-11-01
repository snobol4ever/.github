# Writing rtx asm leaves: the reference (the detail behind SKILL.md; read the section you need)


An rtx leaf is a hand-written assembly routine of the runtime that emitted code calls BARE (no veneer, no save and restore of the emitted machine's registers) for the hot runtime operations: comparison, arithmetic, string and table primitives, allocation, the collector's roots, unification, the Icon aggregates. It is NOT a C function: it keeps the four RTCC registers as it received them unless its derived clobber row says otherwise, it declares its frame to the unwinder truthfully at every instruction, and it never enters a box (NO C FUNCTION ENTERS A BOX, CEO-1576, and no leaf either: LOGIC LIVES IN EMITTED BOXES, RULES.md). The law is this skill (the leaf contract), skill `runtime-calls` (the return protocols, the verdict road), skill `box-templates` (the rtcc register-block convention) and skill `scrip-memory-model` (the runtime entry table, zeta-layout R4), with receipts in `GOAL-RTCC.md`; the inventory of leaves is read from the objects, never from a page. Lines quoted below are from SCRIP 8e366c454.

## 1. THE RULES (each with its receipt)

- **NO VENEER: A LEAF IS NOT A C FUNCTION** (Lon 2026-09-30, verbatim: *"Ensure the veneer to save and restore registers has been removed from ALL x86 asm runtime calls since they are not C functions and do not require the extra."*; `test_gate_rtx_calls_carry_no_veneer.sh`): emitted code calls a leaf bare through the GOT (`call qword ptr [rip + sym@GOTPCREL]`); a call into the C runtime still carries the rtcc veneer (`x86_rtcc_call`, the register block of `RTCC_BLOCK_BYTES` = 9 GPR slots + 8 XMM, rtcc.h 9-20).
- **THE FOUR REGISTERS ARE THE MACHINE'S** (`test_gate_rtx_entries_keep_the_rtcc_four.sh`): every entry returns r8, r10 and r11 as it received them and r9 as the GVA base, UNLESS its `clobbers` cell in `rt_entries.tsv` records the write; the cell is DERIVED from the assembled objects (`util_rtx_abi_walk.py`, through `util_gen_rt_entry_table.py`) and gated against them (`test_gate_rtx_the_leaf_clobber_table_is_derived_and_gated_against_the_objects.sh`); a leaf that must use one of the four reloads r9 with `RTX_GVA_R9` and lets the table carry the rest. The template that calls a leaf reads that row; nothing is guessed on either side.
- **CFI TRUE AT EVERY PC** (`test_gate_rtx_every_leaf_carries_cfi_true_at_every_pc.sh`, hq_runtime 2026-10-08): every stack move goes through the macros that carry its `.cfi_adjust_cfa_offset` (`RTX_PUSH`, `RTX_POP`, `RTX_SUB_RSP`, `RTX_ADD_RSP`, the `_DYN` forms for a dynamic frame), so the system unwinder and the collector's chain (ARCH-GC § 13) walk through a leaf to the first emitted frame; a bare `push` in a leaf is a red.
- **EVERY ENTRY IS REGISTERED** (`RTX_NAME` into the `rtx_entry_names` section; `test_gate_rtx_inventory_live.sh`): `RTX_FUNC(name)` opens a leaf (`.globl`, `.type`, `.align 16`, `.cfi_startproc`, `endbr64`, the name record) and `RTX_ENDF(name)` closes it; `RTX_ENTRY(name)` is a second entry into a leaf's body. The symbol is a row of `harness/scripts/rt_entries.tsv` (`conv=asm`, its `rc`, `allocates`, `clobbers`) and the gate `test_gate_rt_entry_table_matches_the_binary.sh` holds the table and `libscrip_rt.so` equal.
- **A DECLINING LEAF HANDS BACK TO C BY THE TWIN TABLE** (`RTX_DECLINE`, `RTX_DECLINE_INT`, `RTX_DECLINE_PTR`; `test_gate_rtx_declining_leaves_are_exactly_the_twin_table.sh`): a leaf that covers the fast case and declines the rest returns `RTX_NOT_HANDLED` and its C twin `c_<name>` completes; the set of declining leaves is exactly the twin table, no leaf declines without a twin and no twin exists without its leaf.
- **THE KILL SWITCH IS BYTE-IDENTICAL IN BOTH ARMS** (`RTX_GATE_DEF(fam)`, `RTX_GATE(fam, stub)`, `rtx_gates_init()`; `test_gate_rtx_killswitch_sets.sh`, `test_gate_rtx_ctor_armed.sh`): a family can be switched to its C body at start-up; the program's output set is identical under either arm, N ≥ 4 programs per arm, both modes; the constructor that arms the gates is observable.
- **A STORE IS NO WIDER THAN THE GLOBAL IT WRITES** (`test_gate_rtx_store_width.sh`); **THE LENGTH IS CARRIED, NEVER MEASURED** (no `strlen` on a DESCR's `.s`, RULES.md: a NUL is a valid string element); **ALL ADDRESSES ARE BAKED IN** (Lon 2026-09-29: no name string looked up at run time); **NO NEW GLOBAL** (an `RTX_GATE_DEF` byte is a granted exception of its family; anything else needs Lon's in-chat grant that session); **NO `malloc` FAMILY** (the collector is the allocator: `rtx_alloc.s`).
- **EVERY FAMILY OWES ITS DIFFERENTIAL BATTERY** (`test_rtx_unit.sh`: *"asm family vs its c_* body. Every RTX family owes one of these: same inputs, both implementations, bit-identical results."*): `rtx_<fam>_test.c` declares the leaf and its `c_` twin and drives both over the same inputs.

## 2. THE FILES

- `SCRIP/src/runtime/rtx/`: the leaves `rtx_alloc.s rtx_arith.s rtx_gc.s rtx_icnagg.s rtx_icncall.s rtx_icngen.s rtx_icnnum.s rtx_icnrel.s rtx_icnsub.s rtx_icnvar.s rtx_match.s rtx_misc.s rtx_plunify.s rtx_str.s rtx_table.s rtx_zdp.s`; the batteries `rtx_alloc_test.c rtx_arith_test.c rtx_direct_test.c rtx_misc_test.c rtx_relop_test.c rtx_sname_test.c rtx_str_test.c rtx_sval_test.c rtx_tins_test.c rtx_unit_test.c rtx_varval_test.c`; `rtx_str_bench.c`, `rtx_str_shim.c`; `rtx_abi.inc` (the macros, `.intel_syntax noprefix`, `descr_tags.inc`, `../core/g_runtime_abi.inc`), `rtcc.h` and `rtcc_init.c` (the register block), `rtx_init.c` (the gates `rtx_gate_table rtx_gate_misc rtx_gate_alloc ...` and `rtx_gates_init`).
- The ABI include, `rtx_abi.inc` 6-30, is the whole vocabulary:

```asm
#define RTX_NAME(name) .pushsection rtx_entry_names,"a",@progbits; .asciz #name; .popsection
#define RTX_FUNC(name) .text; .globl name; .type name,@function; .align 16; name: ; .cfi_startproc; endbr64; RTX_NAME(name)
#define RTX_ENTRY(name) .globl name; .type name,@function; name: ; endbr64; RTX_NAME(name)
#define RTX_ENDF(name) .cfi_endproc; .size name, .-name
#define RTX_PUSH(x) push x; .cfi_adjust_cfa_offset 8
#define RTX_POP(x) pop x; .cfi_adjust_cfa_offset -8
#define RTX_SUB_RSP(n) sub rsp, n; .cfi_adjust_cfa_offset n
#define RTX_GVA_R9 mov r9, qword ptr [rip + g_rtccb@GOTPCREL]; mov r9, qword ptr [r9 + 48]
#define RTX_DECLINE mov eax, RTX_NOT_HANDLED; ret
#define RTX_CALL(fn) call qword ptr [rip + fn@GOTPCREL]
#define RTX_GATE_DEF(fam) .data; .align 1; .globl rtx_gate_##fam; .hidden rtx_gate_##fam; .type rtx_gate_##fam,@object; .size rtx_gate_##fam,1; rtx_gate_##fam: .byte 0; .text
#define RTX_GATE(fam, stub) cmp byte ptr [rip + rtx_gate_##fam], 0; je stub
#define RTX_CALL_ALIGN(k) RTX_PUSH(rsp); RTX_PUSH(qword ptr [rsp]); and rsp, -16; RTX_CFA_DYN(8, k)
```

- The tables beside it: `harness/scripts/rt_entries.tsv` → `src/runtime/rt_entry_table.inc` (`util_gen_rt_entry_table.py`); `src/templates/x86/gc_allocating_table.inc` (which entries can collect; a leaf that calls the allocator is a row). The callers: `x86_*.{h,cpp}` `"call_bare"` (1897) and `x86_rtcc_call` (570).
- The C twins live beside the C runtime (`src/runtime/core/`, `src/runtime/rt/`, `src/runtime/builtins/`) under the `c_` prefix; the DESCR layout is `descr.h` and `descr_tags.inc` (`DT_I`, `DT_S`, `DT_NOTSTR_MASK`, the 16-byte cell: tag word, value word).

## 3. WORKED EXAMPLES (quoted)

A comparison leaf, `rtx_arith.s` (`rt_cmp_d`): two DESCR pointers in rdi and rsi, the integer fast path first, then the string road; no push, no frame, nothing of r8-r11 touched, so its clobber row is `none` and the unwinder sees a leaf with the CFA at the return address.

```asm
RTX_FUNC(rt_cmp_d)
    mov     eax, dword ptr [rdi]
    mov     ecx, dword ptr [rsi]
    cmp     al, DT_I
    jne     .Lcd_notint
    cmp     cl, DT_I
    jne     .Lcd_notint
    mov     rdx, qword ptr [rdi + 8]
    cmp     rdx, qword ptr [rsi + 8]
    setg    al
    setl    cl
    sub     al, cl
    movsx   eax, al
    ret
.Lcd_notint:
    test    al, (DT_NOTSTR_MASK & 0xFF)
    jnz     .Lcd_real
```

Its battery, `rtx_arith_test.c` 7-14: the leaf and its C twin declared side by side, driven over the same inputs, bit-identical or the battery is red.

```c
#include "descr.h"
DESCR_t rt_add(DESCR_t, DESCR_t);
DESCR_t rt_sub(DESCR_t, DESCR_t);
DESCR_t rt_mul(DESCR_t, DESCR_t);
DESCR_t c_rt_add(DESCR_t, DESCR_t);
```

The register block a C entry receives, `rtcc.h` 9-20: nine GPR slots and eight XMM slots, the slot order the veneer stores and reloads, so a template's `x86("call", sym, ptr)` and a leaf's `RTX_CALL` into C agree on what a C body may clobber.

```c
#define RTCC_GPR_COUNT 9
#define RTCC_XMM_COUNT 8
#define RTCC_BLOCK_BYTES (RTCC_GPR_BYTES + RTCC_XMM_BYTES)
#define RTCC_SLOT_RAX 0
#define RTCC_SLOT_R8 5
#define RTCC_SLOT_R9 6
```

The entry row the leaf owes, `rt_entries.tsv`: `sym conv rc allocates clobbers transfers src` with `conv=asm` for a leaf, `rc` what rides rax:rdx (`DESCR | OTHER | VOID`), `allocates` 1 when the leaf reaches the allocator (so the emitter's poll follows the call), `clobbers` the derived mask (`none` is explicit, `-` means no row yet). The gate compares every row to `nm` over the built objects.

## 4. THE PROVING INSTRUMENTS (harness/scripts)

- `test_rtx_unit.sh` (the differential batteries, every family), `test_gate_rtx_calls_carry_no_veneer.sh`, `test_gate_rtx_entries_keep_the_rtcc_four.sh`, `test_gate_rtx_the_leaf_clobber_table_is_derived_and_gated_against_the_objects.sh`, `test_gate_rtx_every_leaf_carries_cfi_true_at_every_pc.sh`, `test_gate_rtx_declining_leaves_are_exactly_the_twin_table.sh`, `test_gate_rtx_inventory_live.sh`, `test_gate_rtx_killswitch_sets.sh`, `test_gate_rtx_ctor_armed.sh`, `test_gate_rtx_store_width.sh`, `test_gate_rt_entry_table_matches_the_binary.sh`, `test_gate_no_hidden_global_in_emitted.sh`, `test_gate_globals_census_counts_writable_sections_only.sh` and `audit_runtime_globals_census.py` (a new `.data`/`.bss` byte is a global).
- The generators: `util_gen_rt_entry_table.py`, `util_gen_gc_allocating_table.py` (the allocating table follows the runtime binary and falls behind every runtime landing: regenerate it).
- The bracket for a wrong answer: `monitor_run.sh <prog> --oracle` first (the leaf's effect shows as the first diverging event), then the battery with the failing inputs added, then `gdb` with a breakpoint on the leaf's label and a hit count; `objdump -d --no-show-raw-insn out/libscrip_rt.so | sed -n '/<rt_cmp_d>:/,/ret/p'` to read what assembled; `readelf --debug-dump=frames` for the CFI the gate checks. A ZGC-STALE after a C call from a leaf is a clobbered register, not a root.
- The timing instrument is `util_instr_count.sh` (instruction count, CEO-2035; it drains a non-tty stdin to its end, so a caller whose stdin is a pipe or a socket HANGS: give it `< /dev/null` unless the program reads stdin; and the perf on PATH fails on kernel 6.17, the tool finds `/usr/lib/linux-tools-6.8.0-138/perf` itself, hq_jvm 2026-10-31); a clock only inside `util_quiet_slice.sh`; `rtx_str_bench.c` for the string family.

## 5. THE FORBIDDEN FORMS

A `push`/`pop`/`sub rsp` without its `RTX_` macro (CFI lies); a save and restore of r8-r11 around a leaf call in emitted code, or inside a leaf as a courtesy (the veneer); a write to r8, r10 or r11, or to r9 other than the GVA base, that the derived table does not carry (and a hand-edited clobber or entry `.inc`); a `call` into emitted code or into a box from a leaf (a leaf returns to its caller, the box decides the port); a name looked up at run time; `strlen` on a DESCR; a new `.data`/`.bss` symbol without Lon's grant; `malloc`/`calloc`/`realloc`/`free` under any spelling; an AT&T-syntax line (`.intel_syntax noprefix` is the file's); a leaf that declines with no `c_` twin, or a twin with no leaf; a leaf added without its row in `rt_entries.tsv` and its line in the battery; a C comment in the `.s` (a `#` line is a comment the assembler drops: still zero, the separator only); a leaf whose correctness depends on the mode that called it.

## 6. WHERE THE REST LIVES

The call protocol and the verdict road: skill `runtime-calls`. The rtcc register-block convention and the encoder: skill `box-templates`. The runtime entry table's columns (zeta-layout R4, the `allocates` column of step 5c): skill `scrip-memory-model`. The collector's chain through a leaf, the sites and the polls: skill `gc-collector`. The register plane: SKILL.md § 6. The inventory of leaves by family is read from the objects (`util_rtx_abi_walk.py`), never from a page. The ARCH pages these pointed at are retired (`.github/RETIRED-ARCH-PAGES.tsv`).

## 7. HOW A LANDING IS PROVED

1. The C twin first, or beside: `c_<name>` is the specification the battery grades the leaf against; write the inputs that reach every branch into `rtx_<fam>_test.c`.
2. The leaf under `RTX_FUNC`/`RTX_ENDF`, every stack move through the macros, the four registers untouched or the write deliberate; its row in `rt_entries.tsv`; `util_gen_rt_entry_table.py` regenerated BEFORE `make` (the freshness guard reads the table against the objects).
3. `make -j8`; `test_rtx_unit.sh`; the rtx gates named in § 4 (grep the gates for the leaf's name: a gate anchored on a leaf dies the day it changes); `test_feature_reps.sh` for the feature the leaf serves; the smokes of every language that calls it (all eight for a shared leaf: the collector's, the string family's); `util_reflow_200.py --check` on any `.c`/`.h`/`.inc` touched.
4. One commit, the leaf with its battery and its rows; pull, rebuild, re-run the rtx gates, push. A new leaf's first battery run is RED on a deliberately wrong input before it is trusted (CEO-1680: a proper test, never a plant in the code).
