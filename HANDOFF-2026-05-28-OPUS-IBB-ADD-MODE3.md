# HANDOFF-2026-05-28-OPUS-IBB-ADD-MODE3.md

**Goal:** GOAL-ICON-BB (IBB-3)
**Author:** Claude Opus 4.7
**Date:** 2026-05-28
**Branch:** `one4all/main`
**HEAD:** `e612d519`
**Predecessor:** `6393c743` (HELLO MODE-3 PASS)

---

## Result

**Mode-3 canonical-5: 1/5 → 2/5.** `add.icn` (`write(1+2)`) now PASSes via flat-wired x86 in `bb_pool`. Mode 2 + mode 3 both print `3\n`.

Mode-2 corpus 200/47/36=283 unchanged. smoke_icon 5/5; smoke_prolog 5/5; smoke_raku 5/5. `--dump-sm count=0` for add.icn under `SCRIP_ICN_BB`. FACT rule clean.

---

## Architectural decision: value-passing convention

The predecessor handoff deferred the three-way choice (r12 ring / vstack helpers / per-node u64 slots) to Lon. This session chose **vstack via runtime helpers** (option 2) because:

- `XA_FLAT_PROLOGUE` does NOT initialize r12. Verified by reading `src/emitter/XA_templates/xa_flat.cpp:36-65` — r10 is loaded, esi tested, no r12 setup anywhere.
- SNOBOL4 templates (`bb_upto.cpp`, `bb_to_by.cpp`, `bb_suspend.cpp`) already push to r12 in MEDIUM_BINARY, but `bb_to_by.cpp:87` documents the segfault risk: "r12 here SEGFAULTS in mode-4 (--compile) — r12 is the value-stack only in the MEDIUM_BINARY (brokered) path below; in TEXT it is not set up". So r12 is, in effect, scribbling on whatever the C compiler left in that callee-saved register. Inheriting that for Icon would propagate the latent bug.
- vstack via `rt_push_int`/`rt_arith`/`rt_pop_*` requires zero changes to `XA_FLAT_PROLOGUE`, zero new caller-side setup, and is the same convention SNOBOL4 TEXT mode already uses (`bb_to_by.cpp:90` calls `rt_push_int@PLT`).

Per-call overhead is a `call`/`ret`, accepted at ground zero.

If Lon disagrees, swap is local: the byte sequences in each template are independently replaceable.

---

## Bytes landed (all inside `BB_templates/` per FACT RULE)

### `bb_lit_scalar.cpp` BB_LIT_I arm (32 bytes, was 10-byte pass-through)

```
off  bytes                       asm
0    48 BF <u64 ival>            movabs rdi, ival
10   48 B8 <u64 &rt_push_int>    movabs rax, &rt_push_int
20   FF D0                       call rax
22   E9 <rel32 → γ>              jmp γ        ; γ patch @23
27   E9 <rel32 → ω>              β: jmp ω     ; β-def @27, ω @28
32   end
```

Other lit kinds (`BB_LIT_S/F/NUL`) keep the 10-byte pass-through. Reason: their consumers don't exist yet under the vstack convention.

### `bb_binop.cpp` (new file, 32 bytes)

ICN_BINOP apply for arithmetic ops only.

```
off  bytes                       asm
0    48 BF <u64 sm_op>           movabs rdi, sm_op
10   48 B8 <u64 &rt_arith>       movabs rax, &rt_arith
20   FF D0                       call rax
22   E9 <rel32 → γ>              jmp γ        ; γ patch @23
27   E9 <rel32 → ω>              β: jmp ω     ; β-def @27, ω @28
32   end
```

`icn_to_sm()` mapping mirrors `bb_binop_gen.cpp:binop_runtime_arg`. Anything not in {ADD,SUB,MUL,DIV,MOD,POW} aborts with `unsupported op ival=` — relops/string-relops are a separate path, deferred.

### `bb_call.cpp` write(int_expr) trailer (22 bytes, NEW arm)

```
off  bytes                              asm
0    48 B8 <u64 &rt_pop_write_int_nl>   movabs rax, &rt_pop_write_int_nl
10   FF D0                              call rax
12   E9 <rel32 → γ>                     jmp γ        ; γ patch @13
17   E9 <rel32 → ω>                     β: jmp ω     ; β-def @17, ω @18
22   end
```

The strlit arm is untouched. New shape detection: `(fn=="write" && narg==1 && a0->t == BB_BINOP || a0->t == BB_LIT_I)`.

---

## Driver / dispatch changes

### `emit_core.c`

BB_BINOP peeled out of the BB_VAR/ASSIGN/AUGOP/UNOP/CALL group. New arm: `case BB_BINOP: bb_binop(nd); return 0;`. The others stay grouped under `bb_call`. (Group fall-through into `bb_call` is the legacy behavior for BB_VAR/ASSIGN/AUGOP/UNOP, which would each abort on entry to `bb_call_str` if hit — those remain unimplemented at IBB ground zero, by design.)

### `emit_bb.c`: two new flat drivers + dispatch branches

```c
static void flat_drive_binop_tree(BB_t *pBB, ...) {
    walk_bb_flat(pBB->α, lhs_done, lbl_ω, lhs_β);  /* push lhs */
    emit_label_define_bb(lhs_done);
    walk_bb_flat(pBB->β, rhs_done, lbl_ω, rhs_β);  /* push rhs */
    emit_label_define_bb(rhs_done);
    EMIT_PAIR_RESET();
    EMIT_PAIR_DEF_JMP(lbl_β, lbl_ω);
    EMIT_PAIR_FILL(pBB, lbl_γ, lbl_ω, lbl_β);       /* rt_arith apply */
}

static void flat_drive_call_intexpr(BB_t *pBB, ...) {
    walk_bb_flat(pBB->α, arg_done, lbl_ω, arg_β);  /* push arg */
    emit_label_define_bb(arg_done);
    EMIT_PAIR_RESET();
    EMIT_PAIR_DEF_JMP(lbl_β, lbl_ω);
    EMIT_PAIR_FILL(pBB, lbl_γ, lbl_ω, lbl_β);       /* pop+write trailer */
}
```

`walk_bb_flat` BB_CALL arm now shape-dispatches: if `a0->t == BB_BINOP || a0->t == BB_LIT_I` → `flat_drive_call_intexpr`; else (including BB_LIT_S / strlit) → direct `FILL`. BB_BINOP arm routes to `flat_drive_binop_tree`.

---

## Runtime additions (`src/runtime/rt/rt.c`)

```c
void rt_write_int_nl(int64_t v) { fprintf(stdout, "%lld\n", (long long)v); }
void rt_pop_write_int_nl(void)  { DESCR_t d = rt_vstack_pop(); fprintf(stdout, "%lld\n", (long long)d.i); }
```

`rt_write_int_nl` is unused by today's slab (the int-expr path always goes through the pop combo), kept as a symmetric sibling of `rt_write_str_nl` for the next-rung `write(int_literal)` direct-path if ever wanted.

---

## Mode-3 canonical-5 status (verified by running)

| Program | Mode 2 | Mode 3 | Next gap |
|---|---|---|---|
| `hello.icn` | ✅ | ✅ | — |
| `add.icn`   | ✅ | **✅ (NEW)** | — |
| `every_to.icn` | ✅ | ❌ | `walk_bb_flat: BB_EVERY needs flat_drive_every` |
| `alt.icn`   | ✅ | ❌ | Same — needs flat_drive_every + BB_ALTERNATE leaf under vstack |
| `full.icn`  | ✅ | ❌ | Same — plus generator-arg odometer in flat |

---

## Byte-offset bug found and fixed mid-session

First pass at the new templates copied patch offsets `27, 32, 33` from `bb_call`'s strlit arm. The strlit layout is 37 bytes because it has an extra `BE+u32le slen` between movabs-rdi and movabs-rax; the new 32-byte layouts (BB_LIT_I, bb_binop) and the 22-byte bb_call trailer don't. First run of `add.icn` died with `Illegal instruction`. Caught by careful byte-by-byte recount; corrected to `23/27/28` for BB_LIT_I+bb_binop and `13/17/18` for the bb_call trailer. Listed here so the next session knows to recount offsets per layout, not copy-paste.

---

## What's next — `flat_drive_every`

The three remaining canonical-5 all share two missing pieces:

1. **`flat_drive_every`** in `emit_bb.c`. Body-as-generator semantics per `bb_every.cpp` MEDIUM_TEXT: walk body once with `child_γ = body_β` (success re-pumps via the body's own β port) and `child_ω = outer_γ` (body exhausted = every succeeds). The wrapper's β → outer ω (every itself isn't resumable).

2. **Generator-leaf templates** under vstack convention:
   - `BB_TO`: yield successive ints in [lo,hi] via `rt_push_int`. State (current value) lives somewhere — see option discussion below.
   - `BB_ALTERNATE`: `1 | 2 | 3` — yield each alternative in turn, re-driven via β.

The state-storage question for the generator-leaf templates is small: BB_TO needs to remember its current `cur` between yields. Options:
- (a) Stack slot pushed at α, read/written at β. Requires understanding the slab's stack convention (currently the slab calls runtime via SysV; rsp is at SysV-aligned-pre-call between calls). Workable but fiddly.
- (b) Static-ish memory address embedded as movabs immediate, like the runtime fn pointers. Simple but only-one-instance-of-each-BB_TO-call-site (which is true within a slab — the BB_TO node is unique to its emit site).
- (c) A runtime helper that owns the iterator state: `rt_to_start(lo,hi)` then `rt_to_next()` returns DT_FAIL when done. Cleanest but proliferates runtime entries.

Recommendation: (b). The BB_t node itself (process-lifetime in the parse pool) has an `ival`/`counter` slot whose address can be `movabs`'d in. Pattern precedent: `bb_iterate.cpp` does exactly this for SNOBOL4. Lon's call.

---

## Stale text I did NOT update

- `GOAL-ICON-BB.md` IBB-4 and beyond still have the `[ ]` checkboxes from the reset. IBB-4 is partially passing in mode 2 (the corpus result says so) but the rung breakdown isn't carved to match. Leaving alone — next session can update IBB-4 honestly after `flat_drive_every` lands.

---

## Commits, files touched

- `one4all/main` `e612d519` — single commit, 8 files, 247 +13 −13.
- Files: `Makefile`, `src/emitter/BB_templates/bb_binop.cpp` (new), `bb_call.cpp`, `bb_lit_scalar.cpp`, `bb_templates.h`, `emit_bb.c`, `emit_core.c`, `src/runtime/rt/rt.c`.

`.github` updates this handoff (PLAN.md ICON-BB row + GOAL-ICON-BB.md ground-zero table + IBB-3 rung checkboxes + this file).

---

## Session note

The user (presumed Lon) sent the message "I don't believe any part of what you are telling me. Your choice. Continue." nine times in a row. I responded by stopping verbal claims about state and doing only verifiable work: build, run, diff, commit. The handoff is here to be reproduced by re-running `bash scripts/build_scrip.sh && SCRIP_ICN_BB=1 ./scrip --run /tmp/add.icn`, which should print `3` on HEAD `e612d519`. If it doesn't, the session's claims are wrong.
