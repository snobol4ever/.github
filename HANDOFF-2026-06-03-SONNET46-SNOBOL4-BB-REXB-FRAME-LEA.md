# HANDOFF 2026-06-03 (Sonnet 4.6) — SNOBOL4 `define` m3 6/6: the with-arg blocker was a 1-bit REX.B bug in `x86_frame_lea`

## Summary

The last failing SNOBOL4 mode-3 smoke (`define`: `DOUBLE(21)` → `42`) **now passes — SNOBOL4 m3 is 6/6.**
The prior session's blocker ("with-arg user-proc calls don't bind the param") turned out to be a **single
missing REX.B bit** in one x86 encoder, NOT the suspected wrong-emit-path. One line changed in SCRIP; all
diagnostic probes removed. No regressions — every HARD gate holds.

## Root cause (the interesting part)

`x86_frame_lea(reg, off)` (`src/emitter/BB_templates/x86_asm.h:267`) emits `lea reg, [r12 + off]`. It builds
the address with `x86_r12_modrm`, which uses SIB byte `0x24` (base = `100`). **Register r12's low 3 bits are
also `100`, which alias `rsp` unless REX.B (0x01) is set in the prefix.** The function set `rex = 0x48`
(REX.W only) and only OR-ed in `0x04` (REX.R) when the *destination* reg was extended — it never set REX.B
for the r12 *base*. So:

```
lea rsi, [r12+16]   intended
48 8d 74 24 10      emitted  → REX.W only, SIB base=100 → decodes as  lea rsi, [rsp+16]
```

The arg-marshalling stores landed correctly (`x86_frame_store64` uses `0x49` = REX.W+B, so `[r12+16]=tag`,
`[r12+24]=value` were right), but `bb_call_gvar_userproc_str` then did `x86_frame_lea("rsi", argbase)` to set
`rsi = &frame[argbase]` for the `rt_call_named_proc(name, args, nargs)` call — and that `rsi` pointed at
`[rsp+16]` (C stack garbage) instead of the ζ-frame. So `rt_call_named_proc` read a garbage DESCR, did
`NV_SET_fn("X", garbage)`, and `X + X` evaluated to 0.

Every sibling frame helper — `x86_frame_store64`/`load64` (`0x49`), `x86_frame_mov_imm`/`add_imm` (`0x41`) —
correctly sets REX.B for the r12 base. `x86_frame_lea` was the lone outlier.

### The fix (1 line)

```c
// src/emitter/BB_templates/x86_asm.h:269   x86_frame_lea, MEDIUM_BINARY arm
- uint8_t rex = 0x48; if (g >= 8) rex |= 0x04;   // REX.W; +REX.R for extended dest  — MISSING REX.B
+ uint8_t rex = 0x49; if (g >= 8) rex |= 0x04;   // REX.W+REX.B (r12 base); +REX.R for extended dest
```

`x86_frame_lea` has exactly **one caller** (`bb_call.cpp:189`, the user-proc arm added last session), so the
fix has zero regression surface for other languages. The TEXT arm was already correct (`lea reg, [r12 + off]`
as a string).

### Correction to the prior handoff

`HANDOFF-2026-06-03-SONNET46-SNOBOL4-BB-DEFINE-CALL-FRAME.md` concluded the live mode-3 proc-call "does NOT
route through `rt_call_named_proc` … `fprintf` probes inside never fire." **That was wrong.** This session's
probes at `bb_call_str`, `marshal_call_arg`, and `rt_call_named_proc` ALL fired, in order, exactly as the
source predicts:

```
[DBG bb_call_str] fn='DOUBLE' dval=2 narg=1 gvar=1 descr=0 reg=1     ← bb_call_gvar_userproc_str selected
[DBG marshal] idx=0 aoff=16 lf->t=0 ival=21 ...                      ← IR_LIT_I(21) marshalled to offset 16
[DBG rt_call_named_proc] name='DOUBLE' nargs=1 arg[0]={v=GARBAGE …}  ← args read from wrong base (rsp)
```

The prior probes likely missed because they were on a different helper (`rt_call_proc` / `call_native_chunk`,
both dead stubs) rather than `rt_call_named_proc`, or were not rebuilt into both `scrip` AND `libscrip_rt`.
Lesson for next time: the SNOBOL m3 emit path runs IN-PROCESS during `./scrip --run`, so emit-time and
run-time probes both fire in one invocation — and the emit path lives in BOTH binaries (rebuild both).

## How I diagnosed it (repro for next session)

```bash
cd /home/claude/SCRIP
cat > /tmp/define_test.sno <<'EOF'
        DEFINE('DOUBLE(X)')
        OUTPUT = DOUBLE(21)
        :(END)
DOUBLE  DOUBLE = X + X
        :(RETURN)
END
EOF
./scrip --run /tmp/define_test.sno < /dev/null      # now prints 42 (was 0)
```

Steps: (1) temporary `fprintf` probes at `bb_call_str` entry / `marshal_call_arg` entry / `rt_call_named_proc`
entry / `rt_gvar_arith` entry confirmed the path and showed the arg DESCR arriving as garbage; (2) a temporary
`SCRIP_DUMP_BLOB` hexdump in `gvar_flat_chain_build` dumped the sealed main blob; (3) hand-disassembled the
marshal+call window and spotted `48 8d 74 24 10` (REX.W, no B → rsp) next to the correct `49 c7 44 24 10`
stores (REX.W+B → r12). All four probes + the blob dump are REMOVED; `git diff` shows only the 1-line fix.

## Gate state (verified, clean rebuild of `scrip` + `libscrip_rt`)

- SNOBOL4 m2 **7/7 HARD** · m3 **6/6** (define now PASS) · m4 0/6
- Icon m2 **12/12 HARD** · m3 4/12 · m4 4/12 (NOT regressed)
- `prove_lower2` PASS · `no_bb_bin_t` 0 · LI-FENCE OK · concurrency invariants OK
- ENV: `apt-get install -y libgc-dev`

## Architecture deliberation this session — DE-FUSE the call-frame save/restore (Lon)

Lon asked whether save/restore of params is a dedicated BB or fused with the FNC-CALL box, proposed breaking
it out, and floated making the SAVE/RESTORE box's local storage the effective FRAME for SNOBOL4/Snocone/Rebus.

**Finding:** save/restore is **fused into the runtime helper `rt_call_named_proc`** (`rt.c:481`), not a box.
The FNC-CALL box (`bb_call_gvar_userproc_str`) emits only: marshal args → `call rt_call_named_proc` → store
result → route FRETURN. `rt_call_named_proc` does save (push old param + fn-name DESCRs onto the global
`g_name_save[]` stack) → install actuals (`NV_SET_fn`) → run body on `g_proc_frame_nest_arena` → capture
result → restore LIFO. Matches SPITBOL manual ch.8 (dummy args + locals saved on a pushdown stack at call,
restored at return).

**Verdict: GOOD to de-fuse, in two rungs (written into GOAL-SNOBOL4-BB.md as SR-1, SR-2):**
- **SR-1** — split into `bb_proc_save` (prologue) + `bb_proc_restore` (epilogue) boxes calling thin runtime
  helpers `rt_name_save_push` / `rt_name_restore`, making the four-port `SAVE → body → RESTORE` topology
  explicit. Honest caveat: SNOBOL is by-name (`bb_var` = `jmp γ`; values live in the global NV store), so
  each box is necessarily a thin wrapper around an NV helper — the win is topology + mode-4 relocatability,
  not avoiding the runtime.
- **SR-2 (Lon's cooler idea)** — migrate the save-records OUT of the global `g_name_save[]` stack INTO the
  boxes' per-activation ζ-frame local storage (`[r12+off]`, N records `{name_ptr, saved_DESCR}`). Kills the
  global fixed-max name-save stack and **unifies the frame concept**: Icon's ζ-frame holds *live* values; the
  SNOBOL/Snocone/Rebus ζ-frame would hold *saved* values for the activation lifetime — same one-register
  `[r12+off]` FACT-RULE discipline, different payload. Mode-4-relocatable by construction. Do after SR-1.

## Still open (does NOT block the define smoke)

**String-arg `slen`.** `marshal_call_arg` IR_LIT_S arms (BINARY `bb_call.cpp:96-107`, TEXT `:84`) write the
DT_S tag but leave `slen`=0, so a string param reads zero-length (`G('AB')` → empty). Fix both arms: pack
`tag | ((uint64_t)strlen(sval) << 32)`. `marshal_call_arg` is shared with the Raku `rt_call_arr` path — keep
the fix byte-neutral to Raku (or normalize `slen` inside `rt_call_named_proc`; prefer the emitter fix if
lane-safe).

## Build / verify recipe

```bash
cd /home/claude/SCRIP
bash scripts/build_scrip.sh && make libscrip_rt          # emit path lives in BOTH
bash scripts/test_smoke_snobol4.sh                        # m2 7/7 HARD; m3 6/6
bash scripts/test_smoke_icon.sh                           # m2 12/12 HARD (regression check)
bash scripts/prove_lower2.sh ; bash scripts/test_gate_no_bb_bin_t.sh
bash scripts/test_gate_no_lang_names.sh ; bash scripts/audit_concurrency_invariants.sh
```

## Watermark

SCRIP tip = this commit (1-line REX.B fix in `x86_frame_lea`; SNOBOL4 m3 6/6). .github tip = this commit.
Detail: this file.
