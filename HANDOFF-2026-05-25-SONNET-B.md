# HANDOFF — 2026-05-25 (Sonnet 4.6, Session B)

## Repos @ handoff

| Repo | HEAD |
|------|------|
| one4all | `a2cbd6d8` |
| .github | `d5a91091` |
| corpus | `3e223db` |

## Gates

```
GATE-PK: PASS=513 FAIL=0 STUB=602
Icon --interp: PASS=195 FAIL=36 XFAIL=35
Prolog smoke: PASS=5 FAIL=0
```

## What happened this session

**Goal:** GOAL-BB-TEMPLATE-LADDER — climb the Icon+Prolog BB template ladder.

### Rules added
- **RULES.md**: No template code in `emit_core.c` — all emission goes in `BB_templates/`, `SM_templates/`, `XA_templates/`.
- **GOAL-BB-TEMPLATE-LADDER.md Invariant 8**: NO RT calls from BB templates. All generator logic (state, advance, exhaustion, value delivery) must be inline x86 assembly in the template's MEDIUM_TEXT arm. No `call rt_foo@PLT` with port dispatch logic.

### Completed rungs
- **BB_ICN_* rename** (prior session, carried): all 22 `BB_ICN_*` kinds renamed to `BB_*`; 5 collisions resolved (`BB_GEN_ALT`, `BB_GEN_BINOP`, `BB_GEN_SCAN`; dead `BB_ICN_TO_BY`/`BB_ICN_LIMIT` merged into existing).
- **ICN-T-2** ✅ `bb_to_by.cpp` — `BB_TO_BY` int+real TEXT arm (calls `icn_to_by_rt` — predates Invariant 8).
- **ICN-T-3** ✅ `bb_binop_gen.cpp` — `BB_BINOP_GEN` TEXT arm (calls `rt_binop_gen` — predates Invariant 8).
- **ICN-T-5** ✅ `bb_upto.cpp` — `BB_UPTO` fully inline x86. `.data` counter slot, `strchr@PLT` (libc ok), yields 1-based integer pos onto r12 SM stack.
- **ICN-T-8** ✅ `bb_iterate.cpp` — `BB_ITERATE` fully inline x86. `.data` counter + static per-char 2-byte slot table. Yields `DT_S` 1-char DESCR_t onto r12 SM stack per REGISTER-LAYOUT.md.

### Stubs filed (dispatch wired, template body empty)
`bb_proc_gen.cpp`, `bb_gen_alt.cpp`, `bb_limit.cpp`, `bb_gen_scan.cpp`, `bb_keyword.cpp`,
`bb_call.cpp` (PL), `bb_choice.cpp` (PL), `bb_alt.cpp` (PL), `bb_cut.cpp` (PL).

## Next steps

### Invariant 8 compliance model
All new BB templates must be self-contained inline x86:
- `.section .data` → state slot(s) with unique label `.Lkind%d_*`
- α path: initialize state, compute first value, push DESCR_t onto r12, `jmp lbl_succ` or `jmp lbl_fail`
- β path (`lbl_back:`): advance state, check exhaustion, push value or `jmp lbl_fail`
- DESCR_t push: `mov dword [r12], DT_X` + `mov dword [r12+4], slen` + `mov [r12+8], data` + `add r12, 16`
- DT_I=6, DT_S=1, DT_SNUL=0, DT_FAIL=99
- libc calls (`strchr@PLT`, `memcmp@PLT`, `strlen@PLT`) are fine — they are not RT
- No `call rt_*@PLT`, no `call icn_*@PLT` with entry-dispatch logic

### Next open rungs (priority order)
| Rung | File | BB Kind | ir_exec.c line | Notes |
|------|------|---------|---------------|-------|
| ICN-T-6 | `bb_gen_alt.cpp` | `BB_GEN_ALT` | L1609 | Uses `icn_alt_dcg_t` opaque — old broker path; may need redesign |
| ICN-T-7 | `bb_limit.cpp` | `BB_LIMIT` | L548 | c[0]=gen, c[1]=limit-expr; counter in .data; calls bb_exec_node on child — tricky inline |
| ICN-T-9 | `bb_gen_scan.cpp` | `BB_GEN_SCAN` | L873 | Scan stack save/restore; single-shot (no state machine needed) |
| ICN-T-10 | `bb_keyword.cpp` | `BB_KEYWORD` | L904 | sval=name; mostly constant lookup — straightforward inline |
| PL-T-4 | `bb_call.cpp` | `BB_CALL` | L1841 in ir_exec | Prolog predicate call |

### Key reference files
- `src/emitter/BB_templates/bb_upto.cpp` — model for inline counter generator
- `src/emitter/BB_templates/bb_iterate.cpp` — model for inline string iterator with static .data slot table  
- `src/emitter/BB_templates/bb_pat_arb.cpp` — model for `.data` state slot pattern (older style)
- `.github/REGISTER-LAYOUT.md` — r12 SM stack push/pop ABI
- `src/include/descr.h` — DESCR_t layout (v+slen = 8 bytes, union = 8 bytes = 16 total)
- `src/lower/ir_exec.c` — canonical C reference for every BB kind semantics

## Session setup for next session

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
cd /home/claude/one4all && make -j4 scrip
bash scripts/test_per_kind_diff.sh   # expect PASS=513 FAIL=0 STUB=602
bash scripts/test_icon_all_rungs.sh  # expect PASS=195 FAIL=36 XFAIL=35
bash scripts/test_smoke_prolog.sh    # expect PASS=5 FAIL=0
```
