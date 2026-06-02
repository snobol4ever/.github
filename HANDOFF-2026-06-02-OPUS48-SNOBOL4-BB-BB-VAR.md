# HANDOFF — SNOBOL4 BB x86() revamp: `bb_var` → x86() (SNO pass-through + ICN slot-copy)

**Author:** Opus 4.8 (third developer). **Date:** 2026-06-02. **Repo tips after this session:**
SCRIP `origin/main` = this commit; `.github` = the commit carrying this file.

Continues the x86()-self-encoding revamp (V1 → V2-NO-PBB → V3-KEYSTONE → V4-ABORT-TAB-ATP → bb_bin_t-ABOLISHED
→ α-OPERAND-PROMOTE). This session converts **`bb_var`** (the shared Icon/SNOBOL4 variable-read box) off its
`x86_bomb` stub and restores the **`OUTPUT = S` var-read path** — the prior session's NEXT(1).

---

## ⭐ HEADLINE: `S = 'hi'; OUTPUT = S` RUNS IN MODE-3 (prints `hi`)

Verified by direct `./scrip --run`. Also verified the var→var chain `A='foo'; B=A; OUTPUT=B` → `foo`. The
chain `bb_sno_assign`(lit_s, `S='hi'`) → `bb_var`(SNO pass-through, the `S` read) → `bb_sno_assign`(var,
`OUTPUT=S` → `rt_sno_assign_var` → NV_GET(S)→NV_SET(OUTPUT)→print) now executes end-to-end.

## 1. What landed (all on SCRIP `main`)

### `bb_var` → x86() self-encoding (`src/emitter/BB_templates/bb_var.cpp`)
Two live arms + one fallback bomb. pBB-free — reads ONLY `_` (g_emit) and the `g_sno_flat_chain` /
`g_icn_flat_chain` mode flags (declared in `emit_bb.h`, included via `bb_template_common.h`).

- **SNO flat-chain arm** (`g_sno_flat_chain`): pure four-port PASS-THROUGH —
  `IF(MEDIUM_TEXT, α:+comment) + x86("jmp",PORT_GAMMA) + x86("def",PORT_BETA) + x86("jmp",PORT_OMEGA)`.
  **Why pass-through:** SPITBOL semantics (manual p.23, "Using variables") — *using a variable's value is
  nondestructive; the data packet it points to remains unchanged.* A bare variable reference on an
  assignment's rhs (the `S` in `OUTPUT = S`) is resolved by the runtime **name-value table** at call time,
  INSIDE the downstream consumer (`bb_sno_assign` var arm bakes the source name and calls `rt_sno_assign_var`
  → `NV_SET(dst, NV_GET(src))`). The IR_VAR box itself produces no value and must NOT push the (ABOLISHED)
  value stack. Byte-shape identical to the `bb_lit_scalar` IR_LIT_S pass-through. NO value stack, NO ring.

- **ICN flat-chain arm** (`g_icn_flat_chain`, `_.op_off >= 0 && _.op_sa >= 0`): GZ-7 16-byte DESCR copy.
  Icon variables are typed DESCRs (two 8-byte qwords: lo = type tag, hi = payload), so a variable read copies
  the named variable's ζ-frame slot `[r12 + op_sa]` into this box's OWN slot `[r12 + op_off]` so a consumer
  reads it by `bb_slot_get(this)`:
  ```
  x86_frame_load64("rax", op_sa)       ; mov rax, [r12+op_sa]      (var slot lo qword)
  x86_frame_store64(op_off, "rax")     ; mov [r12+op_off], rax     (own slot lo)
  x86_frame_load64("rax", op_sa + 8)   ; mov rax, [r12+op_sa+8]    (var slot hi qword)
  x86_frame_store64(op_off + 8, "rax") ; mov [r12+op_off+8], rax   (own slot hi)
  jmp γ ; def β ; jmp ω
  ```
  All register-relative `[r12+off]` (the ζ-frame FACT RULE) — IDENTICAL bytes in BINARY and TEXT (no movabs to
  a process address, no value stack). The `x86_frame_load64`/`x86_frame_store64` REX.W ζ-frame encoders already
  existed in `x86_asm.h` (added for Icon value boxes) — NO new encoder needed.

- **Fallback:** `x86_bomb("bb_var: unhandled arm ...")` — a non-flat-chain or missing-slot IR_VAR (should not
  occur on the live paths; a LOUD abort if it does).

Single-shot in both live arms (a variable read does not re-offer): β = jmp ω.

### NEW dispatch-time slot promotion (`src/emitter/emit_bb.c`, `walk_bb_flat` IR_VAR case)
The old `bb_var` called `bb_varslot_peek(name)` + `bb_slot_alloc16(pBB)` INSIDE the template — a
side-effecting neighbor read the no-neighbor FACT RULE forbids (`bb_slot_alloc16` MUTATES the per-sequence
slot counter; the box must not do that). Moved to the dispatcher:
```c
case IR_VAR: if (g_icn_flat_chain && nd && nd->sval) {
                 int voff = bb_varslot_peek(nd->sval);
                 g_emit.op_sa  = voff;
                 g_emit.op_off = (voff >= 0) ? bb_slot_alloc16(nd) : -1;
             } else { g_emit.op_sa = -1; g_emit.op_off = -1; }
             FILL(nd, lbl_γ, lbl_ω, lbl_β); break;
```
The driver (which legitimately sees the graph AND owns the `g_bb_varslot` / `g_bb_slotmap` maps) marshals the
var slot offset (`op_sa`) and this box's own result slot (`op_off`) onto `_`; the box reads ONLY `_`. This is
the SAME promotion mechanism the revamp uses for `op_sval`/`op_a_sval`/`op_sa`/`op_off` elsewhere (e.g. the
Icon `bb_unop` arm at the same site). Under `g_sno_flat_chain`, op_sa/op_off are `-1` (the SNO arm ignores them).

## 2. Gate state (GREEN throughout; build `make scrip` then `make libscrip_rt`)
- SNOBOL4 m2 **7/7 HARD** · Icon m2 **12/12 HARD** — the shared `emit_bb.c` IR_VAR touch did NOT regress Icon.
  **Baseline-stashed proof:** `git stash` → rebuild → Icon m3 = **0/12** at HEAD *before* my change; restore →
  Icon m3 = 0/12 *with* my change. Icon m3 being 0 is the PRE-EXISTING prison-commit state (bomb stubs for
  bb_var/bb_assign/etc.), NOT a regression I introduced. The Icon m3 floor (MODE3_MIN=1) is below baseline at
  HEAD — a known "broke nice" state the Four Musketeers climb out of box-by-box.
- `test_gate_no_bb_bin_t` **0** · `prove_lower2` **PASS** · `test_gate_sm_dead` **0** ·
  `audit_concurrency_invariants` **rc=0** (FACT RULES byte-identical ×N unperturbed — I touched no FACT-RULE
  block) · `util_template_purity_audit` **1** (pre-existing Icon `bb_every`) · `test_gate_template_medium_invisible`
  **1** (pre-existing Icon `bb_unop`) · `g_vstack` token **0** (FACT RULE; the 3 residual `rt_vstack_*` refs in
  rt.c/rt.h are the VSX scaffolding, pre-existing informational baseline).
- `bb_var.cpp` self-check (all **0**): `b.size()`, `bb_bin_t`, `bb_emit_asm_result`, raw-byte producers
  (`x86_Lrec`/`x86_b[123]`/`bytes(`/`u32le`/`u64le`), `IF(MEDIUM_BINARY`, `pBB->` neighbor, `_.node`.
- SNOBOL4 m3 smoke PASS=1 (`output`). The `pattern`/`concat`/`arith`/`goto_s`/`define` smoke cases need the
  still-bombed boxes (subject/match, concat-seq, int-binop, goto, define+call-frame). `bb_var` unblocks the
  var-read LEAF — verified directly (`S='hi';OUTPUT=S` and `A='foo';B=A;OUTPUT=B` both correct under `./scrip --run`).

**Method note:** mode-3 `--run` runs the EMITTER (`bb_*` templates) inside the `scrip` DRIVER binary — after
editing a template you MUST `make scrip` (not only `make libscrip_rt`). I touched `emit_bb.c` (compiled into
BOTH scrip and libscrip_rt) so both were rebuilt.

## 3. NEXT STEPS (SNOBOL4), priority order
1. **`_.op_a_slot` promotion** (`emit_core.c`: `g_emit.op_a_slot = nd->α ? bb_slot_get(nd->α) : -1;` in the
   walk_bb_node dispatch prologue, parallel to op_a_sval) + convert the `bb_sno_assign` **int-binop arm** to read
   `FR(_.op_a_slot)` instead of the forbidden inline `bb_slot_get(pBB->α)`. With the binop box this gets
   `OUTPUT = 2 + 3` (the `arith` smoke) moving.
2. **`bb_sno_subject` + `bb_match` together** — MATCH's α reads SUBJECT's ζ-slot (`g_sno_subject_slot`); convert
   as a pair. `bb_match` is the ch.18 unanchored OUTER loop (inline-jump, looping box — follow `bb_pat_span` +
   the internal-label keystone). Then `bb_capture` / `bb_arbno` for the pattern-match statements → the `pattern`
   smoke (`S 'b' = 'X'`).
3. **REG-RO** sealed-trailer rip-relative encoder in `x86_asm.h` — unblocks `bb_lit_scalar` IR_LIT_I (the
   documented bomb from the prior session) + makes the RO loads position-independent (the 2nd mode-4 lever).

## 4. Divvy-up (conflict-free; this session = SNOBOL4)
- **SNOBOL4 (done so far):** `bb_lit_scalar` pass-through✅, `bb_sno_assign` lit_s✅/var✅, **`bb_var`✅ (this
  session — SNO + ICN arms)**. Remaining: `bb_sno_assign` int-binop/concat, `bb_sno_subject`, `bb_match`,
  `bb_capture`, `bb_arbno`, `bb_ref_invariant`, `bb_eps`; + the variable-length combinators
  `bb_pat_cat`/`alt`/`match`/FENCE-pair via `x86_pair_loop()`.
- **Icon:** bb_iterate, bb_binop_gen, bb_upto, bb_to/to_by, bb_alt, bb_seq, bb_every, bb_suspend, bb_unop (last
  medium-branch), bb_assign (the Icon var-store arm — the IR_ASSIGN box `bb_var` now feeds in the ICN chain),
  + the binop arm-files.
- **Prolog:** bb_builtin, bb_goal, bb_choice, bb_disj, bb_unify, bb_catch.
- **Raku:** bb_nfa leaves.

⚠ **Coordination note:** `bb_var` is SHARED (Icon + SNOBOL4). I converted BOTH arms (SNO pass-through + ICN
slot-copy) so the Icon lane does NOT need to touch `bb_var` — when Icon converts `bb_assign` (the var-STORE
box), the var-READ box (`bb_var`) is already done. The `emit_bb.c` IR_VAR dispatch promotion is the seam; it
sets op_sa/op_off ONLY under `g_icn_flat_chain` (Icon) and `-1` otherwise (SNOBOL4 ignores them).

`x86_asm.h` was NOT edited this session (the ζ-frame load64/store64 encoders already existed). The dispatch
insert (`emit_bb.c` IR_VAR) is a single line; `git pull --rebase` before push.

## 5. Handoff sequence (RULES.md) — done this session
Marked the GOAL watermark (single source of truth) with the dated session block + the `bb_var`✅ box-list
update; committed SCRIP (2 files: `bb_var.cpp` + `emit_bb.c`) then `.github`; `git pull --rebase && git push`
code-repo-first. ENV: `apt-get install -y libgc-dev` (core.h / raku_nfa_bb.c include `<gc/gc.h>`).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
