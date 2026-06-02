# HANDOFF — SNOBOL4 BB x86() revamp: α-operand promotion + `bb_lit_scalar` + `bb_sno_assign`

**Author:** Opus 4.8 (third developer). **Date:** 2026-06-02. **Repo tips after this session:**
SCRIP `origin/main` = this commit; `.github` = the commit carrying this file.

Continues the x86()-self-encoding revamp (V1, V2-NO-PBB, V3-KEYSTONE-POS-SPAN, V4-ABORT-TAB-ATP, bb_bin_t-ABOLISHED).
This session restores the **first SNOBOL4 statement to mode-3** since the prison commit (`9afac84`) dropped m3 to 0,
and adds the reusable α-operand promotion that the rest of the SNOBOL4 lane needs.

---

## ⭐ HEADLINE: `OUTPUT = "hello"` RUNS IN MODE-3 (prints `hello`)

Verified by direct `./scrip --run`. The chain `bb_lit_scalar` (pass-through producer) → `bb_sno_assign` (lit_s
consumer, `rt_sno_assign_lit_s` → NV_SET → print) now executes correctly end-to-end.

## 1. What landed (all on SCRIP `main`)

### NEW SHARED INFRA — α-operand promotion (`emit_globals.h` + `emit_core.c`)
`sm_emit_t` gains two fields:
```c
const char * op_a_sval;       // nd->α->sval  (the α-operand's string)
int          op_a_node_kind;  // (int)nd->α->t (the α-operand's IR kind)
```
`walk_bb_node` sets them in the dispatch prologue (right after `op_sval`/`op_ival`/`op_node_kind`):
```c
g_emit.op_a_sval      = nd->α ? nd->α->sval : (const char *)0;
g_emit.op_a_node_kind = nd->α ? (int)nd->α->t : -1;
```
**Why:** this is the no-neighbor FACT RULE made practical for a BINARY consumer (a box with an operand, e.g.
ASSIGN). Before, `bb_sno_assign` read `pBB->α->sval` / `pBB->α->t` directly — a neighbor read the rule forbids.
Now the dispatcher (which legitimately sees the graph) marshals the α-operand onto `_`, and the consumer box reads
ONLY `_`. This is the SAME promotion mechanism the revamp already used for `op_sval`/`op_ival`/`op_node_kind`,
extended to the first child. **Additive** — Icon m2 stayed 12/12 (no box but `bb_sno_assign` reads the new fields).
The natural follow-on is `_.op_a_slot` (promote `bb_slot_get(nd->α)` at dispatch) for the int-binop consumer arm.

### `bb_lit_scalar` → x86() self-encoding (was bb_bin_t offset-table)
- Pass-through arms (IR_LIT_S / IR_LIT_NUL / IR_LIT_F, and **non-flat-chain** IR_LIT_I): pBB-free
  `IF(MEDIUM_TEXT, α:+comment) + x86("jmp",PORT_GAMMA) + x86("def",PORT_BETA) + x86("jmp",PORT_OMEGA)` —
  byte-identical to the original IR_LIT_S arm (E9→γ ; β-def ; E9→ω). A scalar literal is RO; the CONSUMER reads it
  [rip+disp], so the leaf only threads ports. (The old IR_LIT_F arm pushed the now-ABOLISHED value stack via
  `rt_push_real_bits` — pass-through is its correct heir.) Reads `_.op_node_kind` to detect IR_LIT_I; never `pBB`.
- **IR_LIT_I FLAT-CHAIN arm (`g_icn_flat_chain`) is a documented LOUD bomb.** Its GZ-7 16-byte-DESCR→ζ-slot store
  needs a RELOCATABLE rip-relative load of the sealed DESCR **VALUE** from an in-blob RO trailer. The keystone RO
  encoders (`x86_load_ro`) load **ADDRESSES**, not sealed values; the value-from-trailer encoder is the **REG-RO**
  rung (anticipated in `x86_asm.h`, not yet built). A `movabs` of the value would violate the ICON READ-ONLY
  LOCALS ARE IP-RELATIVE FACT RULE — NOT bent. (Note: for the SNOBOL4 `--run` path `g_icn_flat_chain` is FALSE,
  so SNOBOL4 mode-3 never reaches this bomb; it gates Icon-flat-chain integer literals.)
- Signature kept `bb_lit_scalar(IR_t*)` with `(void)pBB` (the x86 arm is pBB-free; no shared prototype / dispatch
  edit needed — minimizes churn on the shared `bb_templates.h` / `emit_core.c` that Icon also owns).

### `bb_sno_assign` → x86() self-encoding (pBB-free)
- **`lit_s`** (`_.op_a_node_kind == IR_LIT_S`): `lea rdi,[dst] ; lea rsi,[str] ; call rt_sno_assign_lit_s ; jmp γ ;
  def β ; jmp ω`. dst = `_.op_sval`; str = `_.op_a_sval`. RO ptrs via `x86("lea",reg,"[rip + __]",addr,label)`
  (`emit_intern_str` label + raw pointer); call via `x86("call",sym,ptr)`.
- **`var`** (`_.op_a_node_kind == IR_VAR`): identical shape, `rt_sno_assign_var(dst,src)`, src = `_.op_a_sval`.
  Structurally byte-shape-identical to the proven `lit_s` arm; not yet exercised end-to-end (see §2).
- **`int-binop`** (`IR_BINOP`) → LOUD bomb: needs the binop's ζ-slot OFFSET on `_` (`_.op_a_slot` via
  `bb_slot_get(nd->α)` at dispatch) — a fusion the no-neighbor rule forbids reading inline.
- **`concat`/other** (`IR_SEQ`/`IR_SEQ_EXPR`/…) → LOUD bomb: the old arm baked process-local sub-graph pointers
  (mode-3-only, NOT relocatable; its TEXT arm already bombed). The relocatable form is the STITCH_SEQ pattern-graph
  build (PB-RB-4), not a box rewrite.
- β = jmp ω (single-shot statement). No r10 guard / no rsp-align dance — rsp is 16-aligned at α entry so one direct
  `call` is SysV-correct (matches the original lit_s arm, which also had neither).

## 2. Gate state (GREEN throughout; build `make scrip` then `make libscrip_rt`)
- SNOBOL4 m2 **7/7 HARD** · Icon m2 **12/12 HARD** (the shared emit_core.c/emit_globals.h touch did NOT regress Icon).
- `test_gate_no_bb_bin_t` **0** · `test_gate_template_medium_invisible` unchanged (only Icon `bb_unop`(1)) ·
  `audit_concurrency_invariants` rc=0 · `prove_lower2` PASS · `g_vstack` 0.
- m3 by the smoke harness is still 0/6 (so the harness exits 1 — the accepted "broke nice" baseline; `MODE3_MIN=5`
  is a restoration TARGET, not a regression I introduced). `OUTPUT="hello"` is verified by direct `./scrip --run`.
  The `var` assign + arith + concat are gated on `bb_var` (shared lane) + `_.op_a_slot` (see NEXT).

**Method note:** mode-3 `--run` runs the EMITTER (the `bb_*` templates) inside the `scrip` DRIVER binary — so after
editing a template you MUST `make scrip` (not only `make libscrip_rt`, which is the runtime the emitted code CALLS).
A converted-box change that "doesn't take" is usually a stale `scrip`.

## 3. NEXT STEPS (SNOBOL4), priority order
1. **`bb_var`** (shared/Icon lane). For the SNOBOL4 assign path it is a port pass-through (the assign reads the src
   NAME via `_.op_a_sval` and does NV_GET at runtime). **Check Icon's value-producing use of `bb_var` first** — Icon
   likely materializes the var's value into a slot/register, so the conversion must preserve that. Unblocks the
   `var` assign + `OUTPUT = S`.
2. **`_.op_a_slot` promotion** (`emit_core.c`: `g_emit.op_a_slot = nd->α ? bb_slot_get(nd->α) : -1;`) + convert
   `bb_sno_assign` int-binop arm to read `FR(_.op_a_slot)` instead of `bb_slot_get(pBB->α)`. With `bb_var` this
   gets arith/concat statements moving.
3. **`bb_sno_subject` + `bb_match` together** — MATCH's α reads SUBJECT's ζ-slot (`g_sno_subject_slot`); convert as
   a pair. Then `bb_capture` / `bb_arbno` for the pattern-match statements. (Originals in `git show HEAD~N:<path>`;
   `bb_match` is the ch.18 unanchored OUTER loop, inline-jump model — a looping box, follow `bb_pat_span` + the
   internal-label keystone.)
4. **REG-RO** sealed-trailer rip-relative encoder in `x86_asm.h` — unblocks `bb_lit_scalar` IR_LIT_I + makes the RO
   loads across the pattern boxes position-independent (the 2nd mode-4 lever). The keystone comments anticipate it
   ("REG-RO target: … lea dst,[rip+disp] into a sealed RO trailer + a rip-rel patch record — a one-function change").

## 4. Divvy-up (conflict-free; this session = SNOBOL4)
- **SNOBOL4:** lit_s✅/var✅ arms of `bb_sno_assign`; `bb_lit_scalar` pass-through✅ (IR_LIT_I bombed on REG-RO).
  Remaining: `bb_sno_assign` int-binop/concat, `bb_sno_subject`, `bb_match`, `bb_capture`, `bb_arbno`,
  `bb_ref_invariant`, `bb_eps`; plus the variable-length combinators `bb_pat_cat`/`alt`/`match`/FENCE-pair via
  `x86_pair_loop()`.
- **Icon:** bb_var (shared — coordinate), bb_iterate, bb_binop_gen, bb_upto, bb_to/to_by, bb_alt, bb_seq, bb_every,
  bb_suspend, bb_unop (last medium-branch), + the binop arm-files.
- **Prolog:** bb_builtin, bb_goal, bb_choice, bb_disj, bb_unify, bb_catch (cut/arith/ite/conj done).
- **Raku:** bb_nfa leaves (rk_gather done).

`x86_asm.h` is shared but additive; the dispatch/decl inserts land on different lines; `git pull --rebase` before push.

## 5. Handoff sequence (RULES.md) — done this session
Marked the GOAL watermark (single source of truth) with the dated session block; committed SCRIP (4 files) then
`.github`; `git pull --rebase && git push` code-repo-first. ENV: `apt-get install -y libgc-dev`
(core.h / raku_nfa_bb.c include `<gc/gc.h>`).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
