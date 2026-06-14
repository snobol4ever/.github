# HANDOFF 2026-06-14 — PASCAL-BB — Per-proc FRAME-ARENA overflow fixed (dynamic running-offset allocator)

Session 60. GOAL-PASCAL-BB (7th frontend). Continues the Session-59 pcom-M3 frontier ("pcom's first
`write` never reaches stdout in M3, rc=0 no abort"). That frontier is now ROOT-CAUSED and one of its
blockers is FIXED + gated. pcom is still NOT self-hosting — it is gated by SEVERAL independent bugs,
enumerated below with exact signatures and minimal reproducers so the next session can pick them off.

## WHAT LANDED (validated, regression-free, committed)

**The per-procedure FRAME-SLOT-ARENA overflow is fixed via a dynamic running-offset (stack) frame
allocator in the runtime, sized per-proc by the proc's actual slot peak, with a 4096-byte floor.**

### Root cause (confirmed with hard numbers)
Per-proc frame slots accumulate MONOTONICALLY across a whole proc body: `bb_slot_alloc16` (emit_bb.c
~l.74) only ever does `g_flat_slot_count += 16`, never decrements, and `codegen_gvar_flat_chain_body`
(emit_bb.c l.3652) never resets it between statements (temporaries of statement i are dead after its
γ, but their slots are never reused). So `g_flat_slot_count` at body-end = the PEAK frame-bytes the
emitted code addresses via `[reg+off]`. The RUNTIME, however, gave every nested-proc frame a FIXED
4096-byte slice: `rt.c` had `#define PROC_FRAME_NEST_QWORDS 512` and
`fb = &arena[depth * 512]` (512 qw × 8 = 4096 B). A proc whose peak exceeds 4096 wrote PAST its slice
into the next frame's region → corrupted the static link / return path → the proc returned FAILDESCR
(eax=99) → caller's `cmp eax,99; je ω` dropped the rest of the caller's statement chain. This is the
"silent drop, rc=0, no abort" the Session-59 handoff saw in pcom M3.

In pcom the first proc to overflow is `chartypes` (l.3908, a level-3 proc nested in `inittables`):
~64 char-indexed assignments `chartp['x']:=v` (each `array[char]` assign consumes 4 slots = 64 B) ⇒
64×64 = exactly 4096 ⇒ overflow. Its sibling `rators` has the SAME `for i:=ordminchar to ordmaxchar
do sop[chr(i)]:=noop` loop and WORKS — the only difference is statement COUNT (rators ~10 vs chartypes
~105). Measured worst-proc peaks (instrumented, then reverted): **pcom = 13008 B, pint ≥ 11152 B** —
3.2× the old slice. These are the corpus's two largest programs, so any blanket constant is a guess.

### The fix (5 edits across 4 files — all DRIVER/runtime, ZERO template/x86 emission changes)
1. **emit_bb.c** — new non-static `int g_last_flat_frame_bytes;` set `= g_flat_slot_count` at the end
   of BOTH `gvar_flat_chain_build` (binary/M3) and `gvar_flat_chain_build_text` (text/M4), right after
   `codegen_gvar_flat_chain_body` returns. Purely additive; changes no emitted code.
2. **rt.c** — added `int frame_bytes;` to `rt_proc_t` (init 0 in `rt_proc_register` AND `rt_proc_set_fn`).
   Added `void rt_proc_set_frame_bytes(const char *name, int bytes)` (stores max). Replaced the fixed
   `g_proc_frame_nest_arena[PROC_FRAME_NEST_MAX*512]` (1 MB, depth-strided) with a 1-D running-offset
   stack: `#define PROC_FRAME_ARENA_QWORDS (8*1024*1024)` (64 MB BSS, lazy, `aligned(16)`) +
   `static long g_proc_frame_cursor_qw`. Rewrote BOTH `rt_call_named_proc` and `rt_call_named_proc_sl`
   to: `fbytes = max(4096, p->frame_bytes)` (THE FLOOR — see below); `fqw = ((fbytes+15)&~15)/8`
   (always even ⇒ 16-aligned); overflow-guard `if (cursor+fqw > ARENA) return FAILDESCR;`;
   `fb=&arena[cursor]`; save cursor; `cursor += fqw`; call `p->fn(fb,0)`; restore cursor. Kept
   `g_proc_frame_nest_depth` for the recursion-COUNT limit (PROC_FRAME_NEST_MAX) and kept the `_sl`
   zero-fill of declared slots.
3. **rt.h** — declared `rt_proc_set_frame_bytes`.
4. **scrip.c M3 path** (the SHARED SNOBOL4/Pascal gvar branch, ~l.2925, after
   `gvar_flat_chain_build_at` returns pfn): `rt_proc_set_frame_bytes(pname, g_last_flat_frame_bytes);`.
5. **scrip.c M4 path** (~l.2627 build loop + ~l.2655 proc_startup emit): capture each proc's peak into
   a `static int peak_buf[64]` parallel to the existing `pidx_buf[64]` right after
   `gvar_flat_chain_build_text_at`; in `proc_startup` emit `lea rdi,[rip+.Lpn%d]; mov esi,<peak>;
   call rt_proc_set_frame_bytes@PLT` for each proc with peak>0. (M4 registers in the COMPILED binary's
   `proc_startup`, so `out/libscrip_rt.so` MUST be rebuilt — `make libscrip_rt`.)

### THE FLOOR — why this is regression-proof
`fbytes = max(4096, frame_bytes)` means EVERY frame is ≥ the old 4096-byte size. A proc that fit in
4096 at baseline still gets exactly 4096; a proc needing more now gets exactly its peak. The change is
therefore a STRICT SUPERSET of baseline behaviour — it can only GROW frames, never shrink them, so a
frame can never overflow where it didn't before. This neutralises the one real risk (that the emit-time
peak could UNDER-count a proc's true slot use — e.g. SNOBOL4 pattern child-cache prebuild slots — and
hand back a too-small frame). The running-offset allocator keeps total memory bounded by the summed
deepest call chain (not max×depth), so flooring small procs to 4096 costs nothing meaningful.

### Validation (all GREEN; this is the commit gate)
- Pascal **M2 122/0 XFAIL=1, M3 122/0 XFAIL=1, M4 122/0 XFAIL=1** (recursion.pas the lone XFAIL) —
  unchanged from the Session-59 watermark.
- Minimal reproducer (below) **charA N=64 now passes in M4** (`[S][A][B][E]`); was dropping (`[S][A]`).
- SNOBOL4 mode-4 crosscheck **166/87/SKIP=8 — BYTE-IDENTICAL before and after** the change (the 87 are
  pre-existing, unrelated to frames). Icon crosscheck 4/0. Prolog crosscheck 102/38 (Prolog uses the
  separate `pl_gz` path, untouched; 38 pre-existing). The floor guarantees these are baseline.

### Minimal reproducer (regenerate any time)
A level-3 proc (called from a level-2 proc) with N char-indexed `array[char]` assignments. Breaks at
EXACTLY N=64 (63 ok, 64 drops) pre-fix; int-indexed `array[1..n]` breaks between N=70 and N=100.
```pascal
program t(output);
type chtp=(letter,number,special,illegal,chspace);
var chartp:array[char] of chtp;
  procedure outer;
    procedure ctypes;
    begin chartp['a']:=letter; { ... repeat to N distinct/cycled chars ... } end;
  begin write('[A]'); ctypes; write('[B]'); end;
begin write('[S]'); outer; write('[E]'); writeln; end.
```
Pre-fix M3/M4 print `[S][A]` for N≥64 (ctypes drops outer's chain); post-fix M4 prints `[S][A][B][E]`.

## STILL OPEN — the remaining pcom/pint self-hosting blockers (INDEPENDENT bugs)

pcom is NOT self-hosting yet. After the frame fix, four distinct bugs remain. None is a frame issue.

1. **M3 (--run) does NOT apply the sized frame to the failing call — the in-process call never reaches
   the runtime dispatcher.** charA N=64 PASSES in M4 but STILL DROPS in M3 (`[S][A]`). Traced: in M3
   the `outer→ctypes` call IS emitted with `mig=1` (i.e. `rt_call_named_proc_sl`, confirmed via emit
   trace `[EMIT-CALL-BIN] fn=ctypes mig=1`), and `rt_proc_set_frame_bytes(ctypes,9232)` IS called at
   registration (confirmed via runtime trace `[SETFB] name=ctypes bytes=9232`) — BUT at RUNTIME only
   `outer` hits `rt_call_named_proc_sl` (`[CALLSL] name=outer`), and `ctypes` NEVER produces a CALLSL/
   CALL trace. So the in-process MEDIUM_BINARY emitted code for `outer→ctypes` is NOT actually calling
   the rt.c `rt_call_named_proc_sl` the trace instruments — it reaches ctypes by some other route (or
   ctypes' body runs on outer's frame region without a dispatcher hop). NEXT STEP: dump the in-process
   blob for `outer` (or compare the MEDIUM_BINARY `x86_call_ro(rsym, fptr)` path at bb_call.cpp l.408
   vs the MEDIUM_TEXT `call rt_call_named_proc_sl@PLT` path l.391) to find why the binary path bypasses
   the sized-frame dispatcher. This is THE reason M3 pcom still emits nothing.
2. **`op_a_slot==-1 (call result slot not promoted)` at extreme statement counts.** charA N=200 (and
   pint) BOMB with `libscrip_rt: BOMB — bb_gvar_assign call-result: op_a_slot==-1`. Fires in
   `bb_gvar_assign` when a gvar-assign's RHS call-result slot wasn't promoted; surfaces only at very
   high single-proc statement counts (N≥~150). Likely a slot-offset field overflow/sentinel once
   offsets get large. Pre-existing; orthogonal to the arena fix.
3. **M4 duplicate-label collision blocks pcom assembly.** `scrip --compile pcom.pas` emits asm that
   gcc/as rejects: `Error: symbol '.Lcallfn6716' is already defined` (multiple sites). The
   `.Lcallfn%d`/`.Lprocfn%d` label ids in bb_call.cpp (`marshal_single_call` uses `lblid`; the IR_CALL
   box uses `g_flat_node_id++`) COLLIDE across procs in a large program. NEXT STEP: make these label
   ids globally unique (e.g. always `g_flat_node_id++`, or a dedicated monotonic counter), then re-try
   pcom M4 assemble+link+run.
4. **pint emit SEGFAULT.** `scrip --run pint.pas` segfaults DURING emission (the frame-peak instrument
   printed pint peaks up to ≥11152 then the process segfaulted at emit time, before any runtime). A
   separate emit-time crash in pint; needs its own bisect.

Suggested order: (3) is mechanical and unblocks reading pcom's real M4 output; (1) unblocks M3; (2)
and (4) are deeper. Once (1)+(3) land, re-drive pcom on `/tmp/tiny.pas` (`program t(output); begin end.`)
and walk the checkpoint probes (below) forward.

## ARTIFACTS / HOW TO REPRODUCE (this session's scratch, in /tmp — NOT committed)
- `/tmp/tiny.pas` — `program t(output); begin end.` (pcom's smallest self-host input).
- `/tmp/pcom_probe.pas .._probe2 .._probe3` — pcom copies with checkpoint `write(output,'[..]')` probes
  in the main body, inside `inittables`, and inside `chartypes`. probe3 (M2) reaches `[DONE]`; probe3
  (M3, post-fix) still stops at `[T6-procmnemonics]` because of open bug #1.
- `/tmp/charA.pas` (N=64), `/tmp/charA200.pas` (N=200) — the minimal reproducer at both thresholds.
- `/tmp/run_m4.sh` — M4 one-shot: `scrip --compile $1 > m4.s; gcc -no-pie -o m4.bin m4.s -Lout
  -lscrip_rt; LD_LIBRARY_PATH=.../out m4.bin`. (lib is `out/libscrip_rt.so`, NOT `./`.)
- `/tmp/run_gate.sh`, `/tmp/run_gate_m3.sh`, `/tmp/run_gate_m4.sh` — the three Pascal gates (M2/M3/M4).
- Build: `cd SCRIP && rm -f scrip && make -j4 scrip && make libscrip_rt`. After rt/ or scrip.c edits,
  `make libscrip_rt` is MANDATORY (M4 links the external .so).

## GATE WATERMARK (frame fix is parity-preserving; main is regressed by a SEPARATE concurrent push)
Frame commit `9149cb1` on its own base: Pascal M2/M3/M4 122/0 XFAIL=1 (zero gate delta). **BUT current
`origin/main` is REGRESSED to M3 119/3 (FAILING: `arr2dtype.pas boolfn.pas case2.pas`) and M4 119+3SKIP
by commit `2fa5086` "IR_CALL split rung 5" — a non-Pascal push that exercised only descr/DEFINE probes
and did NOT run the Pascal gate.** Verified by gating `2fa5086` in isolation (same 119/3, same 3 tests).
That is the TOP-PRIORITY fix for the next session — bisect the `IR_CALL_GVAR_USERPROC` stamping in
`resolve_call_kinds_gvar`/`bb_call.cpp` against those 3 probes BEFORE resuming pcom work. SNOBOL4 mode-4
crosscheck 166/87 (pre-existing). Icon crosscheck 4/0. Prolog crosscheck 102/38 (pre-existing). pcom/pint
NOT gated.
