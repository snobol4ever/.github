# HANDOFF 2026-05-29 — Opus 4.8 — Raku BB M3-RK-NOINTERP-1d LANDED (rk_gather closed)

**Goal:** GOAL-RAKU-BB.md · **Step:** M3-RK-NOINTERP-1d · **Result:** rk_gather CRASH→PASS, GATE-RK3 25→26.
**Commits:** SCRIP `a894af4a` (rebased onto upstream `d9062238` Prolog WAM-CP-8, clean — orthogonal).

## What landed

`rk_gather.raku` (`for gather { take(10); take(20); take(30); } -> $v { say($v) }` → `10 20 30 done`)
was the last Cluster-1 mode-3-native CRASH. It aborted with:

```
bb_emit_end: 1 unresolved forward reference(s):
  site=20 label='.Lbbinv0_β'
```

The prior handoff guessed the fix was bb_upto/bb_suspend/bb_seq mechanical mirrors. The actual
gather-body BB graph (confirmed by probe) is:

```
BB_SEQ (n=4) → γ-chain: BB_SUSPEND, BB_SUSPEND, BB_SUSPEND, BB_FAIL
```

(three `take()` SUSPENDs + a terminal FAIL for Seq exhaustion). bb_upto is NOT involved.
bb_suspend and bb_fail already had MEDIUM_BINARY arms — but bb_suspend's was broken (r12),
and the real gap was bb_seq + a lowering ordering bug. THREE coordinated fixes:

### 1. bb_seq.cpp — new raw-x86 gather-driver `bb_seq_gather_binary`

The MEDIUM_BINARY arm (lines ~262) only walked `g_emit.xa_bb_emit_pair_*[]` (the flat-driver
passthrough). On the mode-3 SM_BB_INVOKE path, the wrapper (sm_bb_switch.cpp:128) dispatches the
SEQ via `walk_bb_node(gen, NULL)` — `flat_drive_seq` never ran, so `xa_bb_emit_pair_n == 0`, the
loop emitted nothing, and the wrapper's outer β label (`.Lbbinv%d_β`) — which the SEQ is supposed
to DEFINE as its resume entry — was left unresolved → abort.

New `static int bb_seq_gather_binary(BB_t *pBB)` (called from the extern-C `bb_seq` entry; returns
1 if it handled emission). It fires only for `PLATFORM_X86 && MEDIUM_BINARY && n>0 && has_suspend`.
Raw-bytes mirror of the MEDIUM_TEXT gather-driver:

- `jmp s0_α` (seq fresh entry — execution falls in here)
- define `_.lbl_β_p` (outer β, wrapper's stack label): `movabs rax,&resume_slot; mov rax,[rax]; jmp rax`
- per child k: `bb_label_define(&Lα[k])`; set g_emit ports (α=Lα[k], γ=Lγ[k], ω=Lα[k+1]|outer_ω,
  β=Lβ[k]); `walk_bb_node(child, NULL)` (child emits its own bytes); `bb_label_define(&Lγ[k])` fixup
  = `movabs rax,&resume_slot; lea rcx,[rip+nxt]; mov [rax],rcx; jmp outer_γ` (nxt = Lα[k+1] or done)
- done trampoline: `jmp outer_ω`

Key mechanics:
- **resume_slot** is a `malloc`'d `uint64_t` (the scratch page is sealed code, no `.data` — the
  TEXT driver's `.data: .quad 0` can't be used). Same one-time-leak idiom as the wrapper's
  `entry_flag` (calloc, freed on process exit).
- **Intermediate labels** (Lα/Lγ/Lω/Lβ arrays, Ldone) are `malloc`'d, NOT stack locals. Patches
  registered against them are resolved by `bb_emit_end`, which runs in the wrapper AFTER bb_seq
  returns — stack locals would dangle. The wrapper-owned outer γ/ω/β (`_.lbl_*_p`) are stack-stable
  across that bb_emit_end (same sm_bb_switch frame).
- **rip-relative lea** (`48 8D 0D <disp32>`) patched via the standard `bb_emit_patch_rel32`: site
  is recorded at current pos, site+4 = end of instruction = rip, so disp = label_offset − rip. Same
  patch mechanism as a `jmp rel32`. movabs (absolute) for resume_slot (heap addr, not a buffer label).

Resume trace: fresh → s0.α push 10, jmp Lγ[0]; fixup resume=Lα[1], jmp outer_γ → say(10). β →
[resume]=Lα[1] → push 20 → say(20). β → Lα[2] → push 30 → say(30). β → Lα[3]=FAIL.α → jmp outer_ω
→ wrapper resets entry_flag, set_last_ok(0) → loop exits → say('done').

### 2. bb_suspend.cpp — MEDIUM_BINARY pushes via rt_push_int, not raw [r12]

The old arm did `mov dword[r12],DT_I; …; mov [r12+8],r8; add r12,16`. But `sm_run_native` (mode-3
native, the only consumer of this arm) does NOT initialise r12 as a value-stack pointer — the SM
value stack is the `g_vstack` C global accessed via `rt_push_int`/`rt_pop`. r12 held arbitrary
callee-saved garbage → the stores segfaulted. This is the SAME bug bb_to_by.cpp fixed in 1a and
bb_to.cpp in IBB-3 (both documented in-file). Fix: `movabs rdi,val_i; movabs rax,&rt_push_int;
call rax; jmp lγ` then `jmp lω`. val_i is a compile-time literal (take(<int-literal>)). bin sites
reordered ascending `{succ_off+1, back_off, back_off+1}` per the 1b invariant (β-define at the
second jmp's opcode byte, ω-patch at its rel32). Added `void rt_push_int(int64_t)` to the extern "C"
block. Helper reached via absolute movabs+call (no PLT in mode-3).

### 3. lower.c lower_every — gather-iterate branch (the underflow fix)

`for gather{} -> $v` parses to `TT_EVERY(TT_ITERATE(v, TT_GATHER(...)))`; the gather-hoist pass
rewrites the TT_GATHER child into `TT_FNC(__gather_N)`. The two existing TT_ITERATE branches in
lower_every match TT_VAR / TT_FNC(non-gather) children, so the gather case fell to the generic
scaffold → `lower_iterate` (Raku) which emits `lower_expr(c[0])` (→ SM_BB_INVOKE) then
`emit_var_store(v)` (→ STORE_VAR v) — BEFORE the scaffold's JUMP_F. On the exhaustion (ω) pull the
generator pushes NO value but STORE_VAR v still runs → `SM value stack underflow`.

New branch (placed before the generic scaffold), mirroring the iterate-array branches exactly:
detect `TT_ITERATE(sval=v, c[0]=TT_FNC(__gather_*))`, look up the proc's `bb_idx`/`is_generator`,
then emit `SM_BB_INVOKE; JUMP_F→exit; STORE_VAR v; VOID_POP; body; JUMP→switch; exit: stamp a[2].i;
PUSH_NULL`. JUMP_F now gates the store — the γ-yield is consumed only on the success path.

## Gates (after rebase + rebuild)

```
GATE-RK3 mode-3 native:  PASS=26 FAIL=1 CRASH=6 TOTAL=33   (was 25/1/7 — rk_gather CRASH→PASS)
GATE-RK  mode-2:         PASS=23 FAIL=10                    HOLD
GATE-RK4 mode-4:         PASS=26 FAIL=7  SKIP=0             HOLD
Smoke raku/prolog/icon:  5/5 / 5/5 / 5/5                    HOLD
Smoke snobol4:           13/13                              HOLD
FACT RULE grep:          0
Build:                   clean
```

Mode-4 rk_gather also PASSes (was already in the 26). Mode-2 rk_gather still FAILs — pre-existing,
NOT a regression (verified by stash): `bb_exec.c` BB_SEQ doesn't drive the multi-yield loop in the
mode-2 interpreter. That is a separate path from the mode-3 native templates landed here.

## FACT / PEERS

FACT grep = 0. All byte production is inside `BB_templates/` (bb_seq.cpp uses `bb_emit_byte/u64/
patch_rel32`; bb_suspend.cpp uses `bytes()/u64le()` — both in templates). No `seg_byte(SEG_CODE`,
`SL_B`, `sl_emit_one`, `emit_standard_blob`. No fields added to BB_t (resume_slot + labels are
malloc'd locals, not BB_t members). Ports stay α/β/γ/ω.

## NEXT

Cluster-1 native is COMPLETE (26/33). Remaining 7 = regex cluster (6: rk_re32/33/34/35/37,
rk_regex23 — DEFERRED to GOAL-RAKU-PAT-BB) + rk_junctions (1 — BLOCKED on Lon Q9-Q12). Substantive
next: RK-BB-4 junctions (after Q9-Q12), or the mode-2 gather gap in bb_exec.c if mode-2 parity is
wanted.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
