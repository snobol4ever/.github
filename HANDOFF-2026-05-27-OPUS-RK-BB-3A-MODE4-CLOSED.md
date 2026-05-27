# HANDOFF — 2026-05-27, Opus 4.7 — RK-BB-3a-mode4-debug ✅ CLOSED

**Watermark:** one4all `cc6c1a06` · .github HEAD · corpus unchanged

## Goal

GOAL-RAKU-BB.md, ladder step RK-BB-3a-mode4-debug. Close the mode-4
half of RK-BB-3a (the prior `706e2828` partial got mode-2 and mode-3
green but mode-4 emitted a template whose loop bailed on slen=0).

## What landed

One file, `src/emitter/BB_templates/bb_iterate.cpp` (+58/-4), commit
`cc6c1a06`. Two surgical edits in the Raku-arm of `bb_iterate_str()`:

### Edit 1 — slen-fallback after `NV_GET_fn@PLT`

After `mov rsi, rax; shr rsi, 32; mov r10, rdx` (extracting slen and
base ptr from the SysV ≤16-byte struct return), insert:

```
test esi, esi              ; slen == 0?
jnz  .Liter<id>_have_slen
test r10, r10              ; base ptr NULL?
jz   .Liter<id>_have_slen  ; keep slen=0; bounds will hit ω cleanly
push r10                   ; save base ptr (caller-saved)
sub  rsp, 8                ; re-align rsp to 16 for the call
mov  rdi, r10
call strlen@PLT
mov  rsi, rax              ; rsi = real slen
add  rsp, 8
pop  r10                   ; restore base ptr
.Liter<id>_have_slen:
```

Why: STRVAL() in `src/runtime/snobol4/snobol4.h:20` hard-codes
`.slen = 0` for every DT_S DESCR. Codebase convention is that
consumers recover length via `strlen(s)` at use-time. The mutating
push handler (`raku_builtins_byname.c:220`) produces a slen=0 DESCR
with a valid NUL-terminated string. Template now honors that
convention.

### Edit 2 — NUL-terminated segment copy in `send` block

Replace the bare `mov rdi, r11; mov rsi, r8; call rt_push_str@PLT`
with:

```
; State: r8 = seg_len, r11 = seg_start_ptr (into source), r10 = base.
; Allocate seg_len+1 bytes via GC_malloc — 16-aligned via 2 pushes.
push r8
push r11
mov  rdi, r8
add  rdi, 1
call GC_malloc@PLT        ; rax = fresh ptr
pop  r11
pop  r8

; memcpy(rax, r11, r8) via rep movsb (no PLT call — no align issue)
mov  rdi, rax             ; dst
mov  rsi, r11             ; src
mov  rcx, r8              ; count
push rax                  ; save dst (rep clobbers rdi)
rep  movsb
pop  rax

; NUL-terminate: new_buf[seg_len] = 0
mov  byte ptr [rax + r8], 0

; rt_push_str(new_buf, seg_len)
mov  rdi, rax
mov  rsi, r8
call rt_push_str@PLT
jmp  .Licngen<n>_γ
```

Why: `rt_push_str(ptr, len)` stores `.s = ptr, .slen = len`. But
downstream `write`/`say` use `fputs(s, dest)` which prints from `ptr`
to the nearest NUL byte — `slen` is ignored. The yield's
`seg_start_ptr` points INTO the source array string (one big NUL-
terminated buffer), so without a fresh copy each yield leaks the
whole remaining tail.

This was the actual observed symptom of the prior session: with the
slen-fallback alone, output was `10\x0120\x0130 / 20\x0130 / 30` —
exactly what NUL-bounded reads would print at offsets 0, 3, 6.

## Diagnostic path

1. Reproduced via `scripts/run_raku_via_x86_backend.sh test/raku/rk_for_array_simple.raku`.
   Empty stdout — iterator bails immediately.

2. Discovered the slen=0 symptom via LD_PRELOAD shim wrapping `NV_GET_fn`
   (`/tmp/probe_inline.c`). EVERY `NV_GET_fn("x")` call returned
   `slen=0, s=<valid_ptr>`, including the working `say(@x)` and
   `elems(@x)` calls. That ruled out "x" name mismatch, scope/timing,
   and section-switch fall-through hypotheses from the prior handoff.

3. Confirmed via `descr.h` + a 10-line sizeof program that DESCR_t is
   exactly 16 bytes, returned in rax:rdx per SysV ABI. Template asm
   logic was correct.

4. Read STRVAL() macro — `.slen = 0` is hard-coded. Read 5+ downstream
   consumers (write, elems, arr_get, raku_substr, snobol4 invoke) —
   all recover via strlen(s). Convention confirmed.

5. After slen-fallback applied, iter ran but output was wrong (whole-
   tail per yield). Second LD_PRELOAD shim on `rt_push_str`
   (`/tmp/probe2.c`) showed slen=2 was being passed correctly per
   segment ("10", "20", "30"). The bug was downstream: fputs ignores
   slen. Read raku_builtins_byname.c's push handler to confirm the
   GC_malloc + memcpy + NUL pattern, mirrored it inline.

## Verification

```
GATE-RK mode-2:  12/31  HOLD
Mode-3 (--run):  12/31  HOLD
GATE-RK4 mode-4: 13/31  (+2: rk_for_array_simple, rk_for_array)
Smoke raku:      5/0    HOLD
Smoke icon:      5/5    HOLD
Smoke prolog:    5/5    HOLD
Broker Icon:     198    HOLD
FACT RULE grep:  0
Build:           clean
```

Byte-exact outputs:
- `rk_for_array_simple` mode-4: `10\n20\n30\n`
- `rk_for_array` mode-4: `10\n20\n30\n60\nalpha\nbeta\ngamma\n`

## Doctrinal notes

**100% template emission preserved.** No new `rt_*` or `raku_*`
helpers. The PLT calls added (`strlen`, `GC_malloc`) are both
memory/conversion helpers already used throughout the runtime
(`raku_builtins_byname.c:213` does `GC_malloc + memcpy + NUL`
for the same array-segment job, just in C). They are not
port-logic helpers — α/β/γ/ω routing stays entirely inline x86.

**FACT RULE grep:** 0 occurrences of `seg_byte`, `SL_B`,
`sl_emit_one`, `emit_standard_blob` in the template (only the
header comment names them as forbidden).

**PEERS RULE preserved:** Discriminator stays `pBB->sval`
presence; no new BB_t fields. `cfg->lang` carried but not
accessed from templates.

**Stack discipline:** All PLT calls reach the callee at a
16-aligned rsp. Two patterns used:
- `push reg + sub rsp, 8 + call + add rsp, 8 + pop reg` (one save)
- `push a + push b + call + pop b + pop a` (two saves, natural 16)
- `push reg + rep movsb + pop reg` (no intervening call, so the
  8-misalign during rep is harmless)

## Next session

**RK-BB-3b/c** — lazy `map`/`grep` as Seq consumers. The polymorphic
BB_ITERATE substrate is now complete in mode-2/-3/-4. Per Open Q3
(Lon's recommendation: eager-drain first cut, lazy as future rung),
`my @x = map { ... } @y` materializes into a fresh `\x01`-string by
walking BB_ITERATE on `@y`, running the lambda body at each γ yield,
accumulating results via the same push-builtin path established by
RK-BB-3.0b. `grep` is the same with a γ-side predicate gate. Target
test: `rk_map_grep_sort24.raku` under `--compile`.

**Deferred / open:**
- Segfault cluster: rk_subs, rk_interp, rk_try_catch25 (verified at
  baseline pre-RK-BB-3.0a). Separate concern; cluster as
  RK-BB-SEGFAULT-CLUSTER if Lon prioritizes.
- Open Q5 union-clobber proper fix for TT_SUB_DECL nparams. RK-BB-2
  step 6's defensive `v.ival=0` (commit `d08237e0`) is still load-
  bearing for gather/take.
- Latent in raku_builtins.c L144/318/353/399: `c[1]->t == TERM_VAR`
  checks against the wrong tag (TERM_VAR=1 vs TT_VAR=5). NAME-write-
  back branches unreachable. Separate cleanup goal.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
