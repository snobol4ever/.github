# FINDING 2026-07-14 (Claude Opus 4.8) — RK-GRAM-3b `.parse` trampoline: the design is fully specified, ready for mechanical execution

**Context:** RK-GRAM-3b's two leaf boxes now BOTH lower + emit, both media, inert behind `RK_GRAM_NATIVE`:
`bb_rk_glit` (literal, SCRIP `1ed0a3d1`) and `bb_rk_gcc` (char-class, SCRIP `788e6247` — this session, LOCAL commit,
**not yet pushed**; `handoff_status.sh` is the push-truth). What remains before the RK-GRAM-3b GATE is fully met
("zero `nfa_build` on the `.parse` path for the literal/char-class shapes") is the **scan-entry trampoline** — the
seam that makes those boxes actually EXECUTE. This finding specifies it end to end so the next full-budget session
executes rather than re-discovers. All line numbers are against the tree at `788e6247`.

---

## THE ONE FACT THAT DRIVES THE WHOLE DESIGN

The native grammar proc `gram__<G>__TOP` is registered as an ordinary proc with a `bb_box_fn`
(`DESCR_t (*)(void* zeta, int entry)`). But its emitted body **reads Σ=r13 / δ=r14 / Δ=r15 and NOBODY SETS THEM.**
The α-preamble only does `push r12; mov r12, rdi` (ζ frame) + rbx=GVA base + rsp save + `rt_zls_mark`. It never
loads the subject registers. Verified by dumping the emitted proc (`RK_GRAM_NATIVE=1 scrip --compile` on
`grammar G { rule TOP { <digit> } }`):

```
proc_gram__G__TOP_α:                 ; push r12; mov r12,rdi; rbx=GVA; save rsp; rt_zls_mark
proc_gram__G__TOP_α_body:            ; the box:
    mov eax,r14d; cmp eax,r15d; jge ...ω     ; δ<Δ bound      <-- reads r14/r15, UNSET
    movsxd rcx,r14d; movzx esi,[r13+rcx]     ; char at Σ+δ    <-- reads r13,   UNSET
    ... strchr ...; je ...ω
    add r14,1; jmp ...γ                       ; advance δ, γ
proc_gram__G__TOP_γ:  mov eax,1;  xor edx,edx; mov rsp,[r12+40]; pop r12; ret   ; spec_t{1,0}
proc_gram__G__TOP_ω:  mov [r12+0],FAILDESCR;   mov eax,99;xor edx,edx; ...; ret ; spec_t{99,0} (99=DT_FAILED)
```

So: **entering this proc via the normal `rt_call_proc_descr` path scans a GARBAGE pointer.** `rt_call_proc_descr`
(rt.c:522) builds a ζ frame and calls `fn(fb,0)` — it does not touch r13/r14/r15. That is the whole gap. The
trampoline's job is exactly: **set Σ/δ/Δ, enter α, read the γ/ω outcome back.**

GOOD NEWS from the same dump: the proc already exposes **four global port labels** —
`proc_gram__G__TOP_α/β/γ/ω` are all `.global`. And the γ/ω terminals already `ret` a `spec_t` (rax=1 success /
rax=99 fail, rdx=0). δ is live in **r14** at the γ terminal. That is everything the trampoline needs to read back.

---

## THE INTERCEPTION POINT — one branch, one file

`grammar_parse_core(gname, subj, out)` — by_name_dispatch.c:381 — is called from exactly one hot site:
by_name_dispatch.c:2129 (`$obj.parse(subj)` when `rt_grammar_has_top(gname)`). Current body (381–395) builds the
NFA and returns `*out = STRVAL(subj)` on full match / `NULVCL` on fail. The trampoline is a **prepended branch**:

```c
static int grammar_parse_core(const char *gname, const char *subj, DESCR_t *out) {
    if (!gname) gname = ""; if (!subj) subj = "";
    /* NATIVE-BOX FAST PATH (RK-GRAM-3b): if gram__<G>__TOP has an emitted box fn, run it via the
     * scan-entry trampoline instead of nfa_build. Fallback (below) stays for every un-migrated shape. */
    { char gpn[320]; snprintf(gpn, sizeof gpn, "gram__%s__TOP", gname);
      extern void *rt_proc_get_fn(const char *);
      bb_box_fn bf = (bb_box_fn) rt_proc_get_fn(gpn);
      if (bf) { return rk_gram_run_native(bf, subj, out); } }
    /* ---- existing nfa_build fallback unchanged (KEEP for regex ~~ and un-migrated grammar shapes) ---- */
    char qn[256]; snprintf(qn, sizeof qn, "%s::TOP", gname);
    ... (381-395 body verbatim) ...
}
```

Note `rt_proc_get_fn` returns non-NULL **only when the box was actually emitted** — i.e. only under
`RK_GRAM_NATIVE` today (the lowerer gates registration on `g_opt_dump_bb || nat`, lower_raku.c:630). So this branch
is automatically inert in default builds until the flag flips to default. That preserves the
fallback-keeps-the-suite-green discipline for free: un-migrated grammars (alternation, subrule, quantifier, or any
non-literal/non-charclass TOP) never register a native fn → `bf==NULL` → NFA fallback, no regression.

---

## THE TRAMPOLINE ITSELF — `rk_gram_run_native` — TWO viable shapes, pick ONE

The box expects Σ/δ/Δ in callee-saved r13/r14/r15 and communicates via the γ/ω `ret`. C cannot set callee-saved
regs across a plain call, so a **tiny asm shim** is unavoidable. Per RULES.md TEMPLATE-ONLY EMISSION, hand-written
asm is forbidden *in templates*; but this shim is RUNTIME glue (a `.c`/`.S` runtime helper), not a code-emitting
template — the analogous precedent is the existing runtime asm in `rt/` (e.g. the zls mark/restore leaves). It does
NOT emit x86 for programs; it IS fixed runtime plumbing. Confirm this reading with Lon before landing (the rule's
spirit is "no per-instruction program codegen outside encoders," which this does not do).

### SHAPE A (recommended) — a naked asm trampoline, `rk_gram_trampoline.S`

```asm
    .text
    .globl rk_gram_enter_box
# DESCR_t rk_gram_enter_box(bb_box_fn fn /*rdi*/, const char* Sigma /*rsi*/, long Delta /*rdx*/,
#                           void* zeta_frame /*rcx*/, long* out_delta /*r8*/)
# Loads Sigma/delta/Delta into r13/r14/r15, enters the box at its alpha (fn), reads back delta.
rk_gram_enter_box:
    push r13; push r14; push r15; push rbx     # preserve OUR callee-saved (SysV)
    mov  r13, rsi                              # Sigma = subject base
    xor  r14d, r14d                            # delta = 0
    mov  r15, rdx                              # Delta = subject length
    mov  rax, rdi                              # box fn
    mov  rdi, rcx                              # arg0 = zeta frame  (box does mov r12,rdi)
    xor  esi, esi                              # arg1 = entry 0 (alpha)
    call rax                                   # -> box; returns spec_t{rax,rdx}; r14 holds final delta
    mov  [r8], r14                             # export final delta to caller
    pop  rbx; pop  r15; pop  r14; pop  r13     # restore OUR callee-saved
    ret                                        # spec_t (rax=1 match / rax=99 fail) flows straight back
```

Caller-side C:

```c
static int rk_gram_run_native(bb_box_fn bf, const char *subj, DESCR_t *out) {
    long Delta = (long) strlen(subj);
    long final_delta = 0;
    /* zeta frame for the box: it does `mov r12,rdi` then reads [r12+32]/[r12+40] (zls mark + rsp save) and,
     * on omega, writes FAILDESCR to [r12+0]. It needs a real frame. Size: reuse the proc's own frame_bytes if
     * discoverable via rt_proc_* ; else a conservative fixed scratch (>= 64B, 16-aligned) is enough for a leaf
     * (the leaf touches only +0,+32,+40). Allocate via the SAME zls2/alloca path rt_call_proc_descr uses so the
     * zls mark/restore balance holds. */
    void *fb = /* rt_zls2_push(FBYTES) or alloca — MIRROR rt_call_proc_descr's frame choice (rt_zeta_cstack()) */;
    extern DESCR_t rk_gram_enter_box(bb_box_fn, const char*, long, void*, long*);
    DESCR_t r = rk_gram_enter_box(bf, subj, Delta, fb, &final_delta);
    /* r.v == DT_FAILED (99) => box took omega. Else box took gamma with delta advanced. */
    int matched = (r.v != DT_FAILED);
    int full    = matched && (final_delta == Delta);     /* .parse requires full; .subparse: any gamma */
    *out = full ? STRVAL(rt_ws_strdup(subj)) : NULVCL;   /* SAME shape as the NFA path returns today */
    /* release fb symmetrically if rt_zls2_push was used */
    return 1;
}
```

**Frame caveat (the one real risk):** the emitted α-preamble references `[r12+32]` (zls mark) and `[r12+40]`
(saved rsp), and writes `[r12+0]` on ω. The trampoline MUST hand the box a frame that makes the preamble's
`rt_zls_mark` + `mov rsp,[r12+40]` balance. Two options, in order of safety:
  (1) **Reuse `rt_call_proc_descr`'s own frame construction** — factor its frame-alloc (rt.c:537-543:
      `rt_proc_call_open` → `rt_frame_prep` → release) so `rk_gram_run_native` builds the frame identically, then
      call `rk_gram_enter_box` with that `fb`. This guarantees the zls balance because it IS the same code.
  (2) A fixed 64B 16-aligned scratch with `[r12+40]=rsp`-at-entry pre-stored and a no-op-compatible zls mark. More
      fragile; only if (1) proves awkward.
  Recommendation: **(1).** The trampoline is then "rt_call_proc_descr, but load r13/r14/r15 first and read r14
  back" — which is the honest one-sentence description of the whole feature.

### SHAPE B (fallback if the asm shim is rejected) — keep NFA, defer

If Lon rules the asm shim out of bounds, leave `grammar_parse_core` on `nfa_build` and treat the leaf boxes as
dump/probe-only until 3c–3e make a box graph rich enough to justify a bigger emitter-side entry-thunk (emitted as
a real XA wrapper template that does the r13/r14/r15 load in-band). That is more machinery and defers all runtime
payoff, but it stays inside TEMPLATE-ONLY EMISSION with zero new runtime asm. Shape A is strongly preferred; this
is recorded only so the decision is explicit.

---

## GATE (unchanged from the rung) + THE TESTS TO WRITE

RK-GRAM-3b GATE part 2: `rule TOP { <digit> }` PASS both modes via the native box, **zero `nfa_build` on the
`.parse` path** for the literal + char-class shapes. Concretely, with the trampoline landed and `RK_GRAM_NATIVE`
default-ON for these shapes:
- `grammar G { rule TOP { "abc" } }; G.parse("abc")` ⇒ truthy Match; `G.parse("abcd")` ⇒ Nil (full-match required).
- `grammar G { rule TOP { <digit> } }; G.parse("5")` ⇒ truthy; `G.parse("x")` ⇒ Nil; `G.parse("55")` ⇒ Nil
  (single char leaf, δ=1≠Δ=2).
- Prove the NFA is gone for these: `nfa_build` not reached (breakpoint or a counter) on the `.parse` of a native
  shape; still reached for `~~ /regex/` and un-migrated grammar shapes.
- **BOTH MODES** (m3 `--run` AND m4 `--compile`), per this file's TESTING DIRECTIVE. Add smokes to
  `scripts/test_smoke_raku.sh`: `gram_native_lit_full`, `gram_native_lit_partial_fail`, `gram_native_cc_digit`,
  `gram_native_cc_nonmember_fail`, `gram_native_cc_twochar_fail`.
- NEUTRALITY still required: Icon 12/12, SNOBOL4 7/7, and the Raku OO/multi-dispatch failure set unchanged (the
  pre-existing 20 ALIGN-INV fails — do not conflate with grammar work).

Once green, flip `RK_GRAM_NATIVE` to default-ON for the literal + char-class shapes (retire the env seam for those
shapes only; un-migrated shapes still fall to NFA), delivering RK-GRAM-3b's "zero nfa_build on the .parse path"
clause. Then 3c (sequence + the δ-save ζ slot) builds directly on the trampoline: a sequence proc is the same
entry, a box graph with ≥2 leaves chained γ→α, the δ-save slot claimed in the ζ frame at each choice point.

---

## SEMANTIC ANCHORS (Rakudo, read this session — Cursor.rakumod / Grammar.rakumod, core.c)

- `constant Cursor = Match` (Cursor.rakumod is one line). Match truthiness = `pos >= from`; a zero-width match at
  `pos==from` SUCCEEDS (matters for `*`/`?` in 3f — a leaf that matches zero chars is still a truthy Match).
- `.parse` (Grammar.rakumod) calls the rule ONCE, then loops `$cursor := $cursor.'!cursor_next'()` **while**
  `pos != chars`. So full `.parse` is NOT a single α-pump for multi-alternative grammars — it is β-resumption of
  TOP until `pos==chars` or the cursor fails. For the single-leaf shapes here, one α-entry that lands γ with δ==Δ
  is sufficient; but the trampoline's γ/ω contract (read δ, compare to Δ) is exactly what generalizes to the
  cursor_next loop in 3d/3e. `.subparse` accepts any γ (no `pos==chars` requirement) — the `full` flag in
  `rk_gram_run_native` is the single switch between them.
- `IR_ALT` does NOT exist in live IR.h (only parked files). 3d alternation needs its own `IR_GALT` or inline
  wiring — do NOT reach for the SNOBOL4 `IR_MATCH_ALTERNATE`/`IR_PATTERN_ALT` (scan-semantics-specific).

## FILES THE NEXT SESSION TOUCHES (Shape A)

- NEW `src/runtime/rt_gram_trampoline.S` (the naked `rk_gram_enter_box`) + Makefile entry (both scrip static-link
  and `libscrip_rt.so` — grammar `.parse` runs in BOTH modes, so the shim must be in both; mirror how a `.c`
  runtime file is added to `RT_PIC_SRCS` and the static list).
- `src/runtime/by_name_dispatch.c` — the prepended native branch in `grammar_parse_core` + `rk_gram_run_native`
  (factoring rt_call_proc_descr's frame construction, or calling a small exported `rt_gram_frame_open/close`).
- `scripts/test_smoke_raku.sh` — the 5 smokes above.
- Possibly `src/runtime/rt/rt.c` — export the frame-open/close leaves if `rk_gram_run_native` reuses them (option
  (1) above), rather than duplicating the zls2/alloca choice.

## STANDING REMINDERS honored

Language-blind templates (the boxes dispatch on IR shape, never `is_raku`) — UNCHANGED, the trampoline is runtime,
not a template. No value stack. ζ-frame storage. `x86()`-only encoders (the trampoline adds NO new encoder — it is
fixed runtime asm, the distinction Lon must ratify). Fresh-full-budget-session rule: this finding IS the
prerequisite reading done, so the next session can open, read this, and execute.
