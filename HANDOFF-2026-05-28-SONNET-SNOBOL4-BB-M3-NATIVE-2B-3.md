# HANDOFF — 2026-05-28 · Sonnet 4.6 · SNOBOL4-BB · M3-NATIVE-2b + M3-NATIVE-3

## Repos / HEADs

| Repo | HEAD |
|------|------|
| SCRIP | `910d55c3` |
| .github | `eab88062` |

Tree: **CLEAN**. Both repos pushed to origin/main.

---

## Gates (watermark)

| Gate | Result |
|------|--------|
| G1 SNOBOL4 smoke | 13/13 |
| G2 unified broker | 36 |
| G3 broad corpus mode-4 | 175/280 |
| G4 broad corpus mode-2 | 238/280 |
| Rung suite | M2=19 M4=15 SKIP=0 |
| FACT RULE | 0 |
| audit_m3_native_binary_arms.sh | GATE OK |

---

## What was done this session

### M3-NATIVE-2b ✅ (`d16c6780` → rebased as part of `910d55c3`)

**JUMP/JUMP_S/JUMP_F BINARY arms** (`sm_jumps.cpp`):
- JUMP: `E9 00 00 00 00` (5 bytes; rel32 at byte 1)
- JUMP_S: `movabs rax,&rt_last_ok; call rax; test eax,eax; jz +5; jmp rel32` (21 bytes; rel32 at byte 17)
- JUMP_F: same but `jnz +5` at byte 14

**RETURN/FRETURN/NRETURN BINARY arms** (`sm_returns.cpp`):
- RETURN: `mov edi,0; mov esi,cond; movabs rax,&rt_do_return; call rax; ret`
- FRETURN: same with `edi=1`
- NRETURN: `movabs rdi,fname; mov esi,cond; movabs rax,&rt_do_nreturn; call rax; ret`

**Two-pass rel32 relocation** (`sm_native.c`):
- Pass 1: `instr_off[i] = ftell(mem)` before each `codegen_sm_dispatch` call
- Pass 2: for each JUMP/S/F: `rel32 = instr_off[target] - (r32_off + 4)`; patched into buf before `memcpy` into `sm_image`

**Critical bug found + fixed: `SM_PAT_LIT` BINARY arm missing `rdi`** (`sm_pat_anchors.cpp`):
- Was: `movabs rax,&rt_pat_lit; call rax` — rdi = garbage from prior call
- Fix: `movabs rdi,&str; movabs rax,&rt_pat_lit; call rax`
- Root cause of apparent JUMP_F inversion: garbage pattern matched everything → last_ok=1 always → JUMP_F never triggered
- Verified JUMP/JUMP_S/JUMP_F all correct against mode-2 oracle (both taken and not-taken paths)

`sm_jumps` and `sm_returns` now classified **REAL** by audit (were BOMB from M3-NATIVE-0).

---

### M3-NATIVE-3 ✅ (`910d55c3`)

**BB call-out from native SM confirmed working.**

Test: `S = 'hello'; S ANY('aeiou') :S(YES)F(NO)` under `SCRIP_M3_NATIVE=1`
- Native output: `vowel-found` ✓ (matches mode-2 oracle)
- Path: `sm_run_native` → `rt_match_variant` → `exec_stmt` (g_bb_mode=BB_MODE_LIVE, already set for --run) → `bb_build_flat` → BINARY template arm → flat-wired execution
- No additional wiring needed — `BB_MODE_LIVE` was already active

**12/13 smoke tests pass natively** (opt-in via `SCRIP_M3_NATIVE=1`). Only `define` fails.

**Also fixed: `SM_CALL_FN` BINARY arm missing `rdi`** (same class as SM_PAT_LIT):
- Was: `mov esi,nargs; movabs rax,&rt_call; call rax` — rdi=garbage
- Fix: `movabs rdi,&name; mov esi,nargs; movabs rax,&rt_call; call rax`

Removed two leftover `[M3-DBG]` fprintf lines from sm_native.c.

---

## Next step: M3-NATIVE-4 — user-defined function dispatch in native blob

**The blocker for making `--run` use native by default:** the `define` smoke test:

```snobol4
        DEFINE('DOUBLE(X)')
        OUTPUT = DOUBLE(21)
        :(END)
DOUBLE  DOUBLE = X + X
        RETURN
END
```

SM sequence contains `SM_CALL_FN "DOUBLE" nargs=1` which calls `rt_call("DOUBLE", 1)`.
`rt_call` uses `chunk_reg_lookup("DOUBLE")` — but SNOBOL4 user functions from `DEFINE()`
are NOT registered as native chunks; they're in the SNOBOL4 function table via `INVOKE_fn`.

`rt_call` falls through to `INVOKE_fn("DOUBLE", args, 1)` which would work **if** the
interpreter is running (mode-2), but in native mode the blob is a flat function — there's
no call frame to jump back to.

**Design for M3-NATIVE-4:**

The runner needs to register each `SM_LABEL define_entry=1` as a callable native chunk
before entering the blob. Two sub-steps:

1. **Pre-scan pass (before emission):** walk `prog->instrs[0..n-1]`, record each
   `SM_LABEL` with `define_entry != 0` as `(name, pc_index)` pairs.

2. **Post-copy registration:** after `memcpy` into sealed `sm_image`, for each recorded
   `(name, pc_index)`, register `code + instr_off[pc_index]` as a native chunk via
   `chunk_reg(name, fn_ptr)`. Wrap it: the chunk wrapper must handle the frame (save
   locals, push args, call into blob at that offset, handle RETURN).

   Actually simpler: each define-entry in the blob IS a valid function entry point
   (starts with `SM_DEFINE_ENTRY` which emits frame setup). Register
   `(void*)(code + instr_off[define_entry_pc])` directly as the chunk function pointer.
   Then `rt_call("DOUBLE",1)` → `chunk_reg_lookup("DOUBLE")` finds it →
   `call_native_chunk("DOUBLE", fn, args, nargs)` calls it.

3. **SM_RETURN in inner function:** currently emits `rt_do_return(0,0); ret`. For a
   function body (not the top-level blob), `ret` returns to `call_native_chunk`'s
   caller correctly — this should already work once the fn ptr is registered.

**Implementation location:** `sm_native.c::sm_run_native()` — add pre-scan + post-copy
registration before the entry trampoline.

**Gate to clear:** `SCRIP_M3_NATIVE=1 ./scrip --run /tmp/define_test.sno` outputs `42`.
Then flip default (remove `getenv("SCRIP_M3_NATIVE")` guard in `scrip.c`).

---

## Bugs of the same class (pattern: BINARY arm calls rt_fn without loading rdi)

These were found this session. The pattern — BINARY arm emits `movabs rax, &rt_fn; call rax`
without first loading the string/pointer argument into `rdi` — may exist in other templates.
Known fixes this session: `SM_PAT_LIT`, `SM_CALL_FN`. When filling other BINARY arms,
always verify `rdi`/`rsi` are loaded before the `call rax`.

---

## Session setup for next session

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_snobol4.sh          # G1: 13/13
bash scripts/test_smoke_unified_broker.sh   # G2: 36
bash scripts/test_mode4_broad_corpus_snobol4.sh   # G3: 175/280
bash scripts/test_interp_broad_corpus_and_beauty.sh  # G4: 238/280
bash scripts/test_snobol4_pat_rung_suite.sh  # M2=19 M4=15
bash scripts/audit_m3_native_binary_arms.sh  # GATE OK
```

Native smoke verification (opt-in):
```bash
SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh   # expect 12/13 (define fails)
```

---

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet 4.6
