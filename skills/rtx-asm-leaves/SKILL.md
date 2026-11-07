---
name: rtx-asm-leaves
description: Hand-written x86-64 runtime leaves in SCRIP/src/runtime/rtx (*.s, rtx_abi.inc, rtcc.h, rt_entries.tsv): the rtcc ABI, the four registers the machine owns, clobber masks, declining leaves, CFI, leaf tests. REQUIRED by the skill gate before editing them.
---

# Writing rtx asm leaves

An rtx leaf is a hand-written asm routine that emitted code calls BARE (no veneer, no save and restore) for hot runtime operations: compare, arithmetic, strings, tables, allocation, unification, the Icon aggregates. It is not a C function: it keeps the four RTCC registers unless its derived row says otherwise, tells the unwinder the truth at every instruction, and never enters a box (CEO-1576; RULES.md LOGIC LIVES IN EMITTED BOXES). The design is the retired call-protocol ARCH page (CEO-2115; now skill runtime-calls) § 15 (the leaf contract) and the retired x86-encoder ARCH page (CEO-2115; now skill box-templates) § 1 (rtcc). Quoted code, file lists and receipts are in `reference.md` beside this file.

## 1. THE RULES

- **No veneer** (Lon 2026-09-30): emitted code calls a leaf through the GOT, bare; only a call into the C runtime carries the rtcc veneer (`x86_rtcc_call`, the register block in `rtcc.h`).
- **The four registers are the machine's:** a leaf returns r8, r10, r11 as received and r9 as the GVA base, unless its `clobbers` cell in `rt_entries.tsv` (derived from the assembled objects) records the write. To use r9, reload it with `RTX_GVA_R9`.
- **CFI true at every pc:** every stack move through `RTX_PUSH`, `RTX_POP`, `RTX_SUB_RSP`, `RTX_ADD_RSP` (or the `_DYN` forms), so the unwinder and the collector's chain walk through the leaf. A bare `push` is red.
- **Every entry registered:** `RTX_FUNC(name)` ... `RTX_ENDF(name)`, `RTX_ENTRY(name)` for a second entry; a row in `rt_entries.tsv` (`conv=asm`, `rc`, `allocates`, `clobbers`).
- **A declining leaf hands back by the twin table:** `RTX_DECLINE` returns `RTX_NOT_HANDLED` and `c_<name>` completes; declining leaves are exactly the twin table.
- **The kill switch is byte-identical in both arms** (`RTX_GATE_DEF`, `RTX_GATE`): a family can switch to its C body and output must not change.
- **Stores no wider than their global; the length carried, never measured (no `strlen` on a DESCR); addresses baked in; no new global without Lon's grant; no malloc family** (`rtx_alloc.s` is the allocator).
- **Every family owes a differential battery** (`rtx_<fam>_test.c`): leaf and `c_` twin over the same inputs, bit-identical.

## 2. THE FILES

- `SCRIP/src/runtime/rtx/`: the leaves `rtx_{alloc,arith,gc,icnagg,icncall,icngen,icnnum,icnrel,icnsub,icnvar,match,misc,plunify,str,table,zdp}.s`; the batteries `rtx_*_test.c`; `rtx_abi.inc` (the macros); `rtcc.h`, `rtcc_init.c`; `rtx_init.c` (the gates).
- Tables: `harness/scripts/rt_entries.tsv` → `src/runtime/rt_entry_table.inc` (`util_gen_rt_entry_table.py`; clobbers derived from the objects); `src/templates/x86/gc_allocating_table.inc` (`util_gen_gc_allocating_table.py`, until zeta-layout step 5c deletes it). Generated, never edited.
- C twins `c_<name>` in `src/runtime/{core,rt,builtins}/`; the DESCR layout in `descr.h` and `descr_tags.inc`.

## 3. WORKED EXAMPLES

The macro vocabulary, `rtx_abi.inc` (excerpt):

```asm
#define RTX_FUNC(name) .text; .globl name; .type name,@function; .align 16; name: ; .cfi_startproc; endbr64; RTX_NAME(name)
#define RTX_ENDF(name) .cfi_endproc; .size name, .-name
#define RTX_PUSH(x) push x; .cfi_adjust_cfa_offset 8
#define RTX_GVA_R9 mov r9, qword ptr [rip + g_rtccb@GOTPCREL]; mov r9, qword ptr [r9 + 48]
#define RTX_DECLINE mov eax, RTX_NOT_HANDLED; ret
```

A leaf with no frame and nothing of r8-r11 touched, `rt_cmp_d` in `rtx_arith.s` (integer fast path):

```asm
RTX_FUNC(rt_cmp_d)
    mov     eax, dword ptr [rdi]
    mov     ecx, dword ptr [rsi]
    cmp     al, DT_I
    jne     .Lcd_notint
    mov     rdx, qword ptr [rdi + 8]
    cmp     rdx, qword ptr [rsi + 8]
    setg    al
    setl    cl
    sub     al, cl
    movsx   eax, al
    ret
```

Its battery declares the leaf and the twin side by side, `rtx_arith_test.c`:

```c
DESCR_t rt_add(DESCR_t, DESCR_t);
DESCR_t c_rt_add(DESCR_t, DESCR_t);
```

## 4. THE PROVING INSTRUMENTS

In `harness/scripts/`: `test_rtx_unit.sh` (every battery); `test_gate_rtx_calls_carry_no_veneer.sh`, `test_gate_rtx_entries_keep_the_rtcc_four.sh`, `test_gate_rtx_the_leaf_clobber_table_is_derived_and_gated_against_the_objects.sh`, `test_gate_rtx_every_leaf_carries_cfi_true_at_every_pc.sh`, `test_gate_rtx_declining_leaves_are_exactly_the_twin_table.sh`, `test_gate_rtx_inventory_live.sh`, `test_gate_rtx_killswitch_sets.sh`, `test_gate_rtx_store_width.sh`, `test_gate_rt_entry_table_matches_the_binary.sh`. For a wrong answer: `monitor_run.sh <prog> --oracle`, then the battery with the failing input, then gdb on the leaf's label; `objdump -d` to read what assembled; `readelf --debug-dump=frames` for the CFI. Time by `util_instr_count.sh` with `< /dev/null`.

## 5. THE FORBIDDEN FORMS

A stack move without its `RTX_` macro; a veneer around a leaf call, or a courtesy save inside one; a write to r8-r11 the table does not carry; a hand-edited `.inc`; a call from a leaf into emitted code or a box; a name looked up at run time; `strlen` on a DESCR; a new `.data`/`.bss` symbol without Lon's grant; any malloc spelling; AT&T syntax; a declining leaf with no twin; a leaf without its `rt_entries.tsv` row and battery line; a comment in the `.s` beyond the separator; mode-dependent correctness.

## 6. THE REGISTER PLANE (who owns which register)

| register | owner and role |
|---|---|
| rsp | the spine and the C stack: ONE stack |
| rbp | the activation frame base in a graph that pins one; a free register otherwise |
| r12 | SNOBOL4: the conditional-assignment stack top (its base is a MATCH_BEGIN frame slot). Prolog: TR, the trail top (skill `prolog-engine`). The two r12 islands are the only stacks off RSP and RBP |
| r13, r14, r15 | inside a match or scan box: Σ the subject's first byte, δ the 0-based cursor, Δ the length (Lon 2026-09-19: "Yes R13 for SNOBOL4 and Icon points to the subject string, &subject."). Prolog: r13 is B, r15 the ball |
| rbx | free, preserved only (the allocation frontier is the memory word `g_hp_fr`, not rbx) |
| r8, r9, r10, r11 | the rtcc four, the emitted machine's: r8 the anchor (master copy in `rtccb`), r9 the GVA base, r10 the statement number, r11 the box id; a leaf returns them as received unless its `clobbers` cell says otherwise, and never writes r9 |
| rax, rcx, rdx, rsi, rdi, xmm0-15 | the leaf's working set; a DESCR comes back in rax:rdx (the tag in al) |

The six GP pins (rbx, rbp, r12-r15) are the SysV callee-saved set, so a leaf only C calls keeps the C convention for them. `cld` holds everywhere (a `std` user restores it); conditions are EFLAGS, never a memory flag byte. One syntax: GNU `as`, `.intel_syntax noprefix`.

Related skills: `runtime-calls` (the call protocol, the verdict road), `gc-collector` (the collection runs in `rtx_gc.s` and `rtx_alloc.s`), `prolog-engine` (`rtx_plunify.s`), `icon` (the Icon leaves and the scanning plan), `scrip-memory-model` (the entry table's columns, zeta-layout R4). Receipts: CEO-1224, CEO-1576, CEO-2019 in RULES.md, GOAL-CEO.md and GOAL-RTCC.md.

## 7. HOW A LANDING IS PROVED

1. The C twin first: `c_<name>` is the specification; write inputs that reach every branch into `rtx_<fam>_test.c`, and show the battery red on a wrong input once (CEO-1680).
2. The leaf under `RTX_FUNC`/`RTX_ENDF`, every stack move through the macros; its `rt_entries.tsv` row; `util_gen_rt_entry_table.py` regenerated before `make`.
3. `make -j8`; `test_rtx_unit.sh`; the rtx gates of § 4; `test_feature_reps.sh` for the feature served; the smokes of every language that calls it (all eight for a shared leaf); `util_reflow_200.py --check` on any C touched.
4. One commit: the leaf, its battery, its rows. Pull, rebuild, re-run the rtx gates, push.
