# HANDOFF — 2026-05-25 (Sonnet 4.6, Session C)

## Repos @ handoff

| Repo | HEAD |
|------|------|
| one4all | `f85525cc` |
| .github | `dc294e8b` |

## Gates

```
GATE-PK: PASS=513 FAIL=0 STUB=602
Icon --interp: PASS=195 FAIL=36 XFAIL=35
Prolog smoke: PASS=5 FAIL=0
```

## What happened this session

**Goal:** GOAL-BB-TEMPLATE-LADDER — fill MEDIUM_BINARY arms with real machine code.

### Rules added
- **Invariant 0** (GOAL file): THE GOAL IS TO EMIT BYTES. A template returning empty string or only placeholder `\xE9` stub jumps is NOT done. A rung is complete only when both MEDIUM_TEXT (real GAS) and MEDIUM_BINARY (real x86 bytes) are implemented. Stubs do not count.

### Completed this session
- **bb_upto.cpp** `BB_UPTO`: MEDIUM_BINARY now emits real x86 — counter state in `pBB->counter`, movabs for hay/cset pointers, call strchr via function pointer, pushes `DT_S` DESCR_t onto r12.
- **bb_iterate.cpp** `BB_ITERATE`: MEDIUM_BINARY now emits real x86 — counter state in `pBB->counter`, loads hay[counter], pushes `DT_S` DESCR_t onto r12.

### Still stubs (MEDIUM_TEXT empty, MEDIUM_BINARY placeholder)
`bb_proc_gen.cpp`, `bb_gen_alt.cpp`, `bb_limit.cpp`, `bb_gen_scan.cpp`, `bb_keyword.cpp`,
`bb_call.cpp`, `bb_choice.cpp`, `bb_alt.cpp`, `bb_cut.cpp`

## Key facts for next session

### DESCR_t layout (from src/include/descr.h)
```
struct DESCR_t { DTYPE_t v(4); uint32_t slen(4); union { char *s; int64_t i; double r; ... }(8) }
Total: 16 bytes. DT_SNUL=0, DT_S=1, DT_I=6, DT_R=7, DT_FAIL=99.
```

### SM stack push via r12 (REGISTER-LAYOUT.md)
```asm
mov dword [r12],   v_and_type   ; DTYPE_t (4 bytes)
mov dword [r12+4], slen         ; uint32_t
mov       [r12+8], data_ptr     ; 8-byte union
add r12, 16
```

### MEDIUM_BINARY pattern (from bb_upto.cpp / bb_iterate.cpp)
- State in `pBB->counter` — address is `(uint64_t)(uintptr_t)&pBB->counter`
- `movabs rcx, addr` = `\x48\xB9` + u64le(addr)
- `mov qword[rcx], 0` = `\x48\xC7\x01` + u32le(0)
- `inc qword[rcx]` = `\x48\xFF\x01`
- `mov rcx,[rcx]` = `\x48\x8B\x09`
- `cmp rcx,rdi` = `\x48\x39\xF9`
- `jge rel32` = `\x0F\x8D` + u32le(0)  → RELOC site at offset+2
- `lea rax,[rax+rcx]` = `\x48\x8D\x04\x08`
- `mov dword[r12],imm` = `\x41\xC7\x04\x24` + u32le(imm)
- `mov dword[r12+4],imm` = `\x41\xC7\x44\x24\x04` + u32le(imm) (NOTE: 9 bytes total)
- `mov [r12+8],rax` = `\x49\x89\x44\x24\x08`  (REX.WR prefix for r12)
- `add r12,16` = `\x49\x83\xC4\x10`
- `jmp rel32` = `\xE9` + u32le(0) → RELOC site at offset+1
- For int push: `mov [r12+8],rcx` = `\x49\x89\x4C\x24\x08`

### bb_bin_t reloc syntax
```cpp
bin = { {offset_of_rel32_field, ...}, {label_ptr, ...}, {is_def, ...} };
// is_def=true means this is the label definition site (lbl_back_p)
// is_def=false means this is a jump-to-label site
```

### Remaining open rungs (must emit real bytes, not stubs)
| Rung | Kind | ir_exec.c | Key state |
|------|------|-----------|-----------|
| ICN-T-4 | BB_PROC_GEN | L1679 | GeneratorState* opaque — complex broker, may skip for now |
| ICN-T-6 | BB_GEN_ALT | L1609 | icn_alt_dcg_t* opaque — old path, may skip |
| ICN-T-7 | BB_LIMIT | L548 | c[0]=gen, c[1]=limit; counter in pBB->counter |
| ICN-T-9 | BB_GEN_SCAN | L873 | Single-shot: save/set/restore scan_subj,scan_pos |
| ICN-T-10 | BB_KEYWORD | L904 | sval=name; static lookup via icn_kw_read |
| PL-T-4 | BB_CALL | L1841 | Prolog predicate call |

### For ICN-T-10 (BB_KEYWORD) — simplest next target
TEXT: emit `call icn_kw_read@PLT` with sval pointer, check result, push onto r12.
BINARY: movabs rdi,sval; movabs rax,icn_kw_read; call rax; test for FAILDESCR; push result.
icn_kw_read is in icn_runtime.c — already linked.

## Session setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip
bash scripts/test_per_kind_diff.sh   # expect PASS=513 FAIL=0 STUB=602
bash scripts/test_icon_all_rungs.sh  # expect PASS=195 FAIL=36
bash scripts/test_smoke_prolog.sh    # expect PASS=5 FAIL=0
```
