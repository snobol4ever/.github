# FINDING — Prolog rung-zero: head-unify binds a THROWAWAY frame cell, not the caller's variable

Date: 2026-07-15 (session sXX, Claude). SCRIP HEAD 6a165d14 (clean).
Baseline MEASURED (NOT the cursor's "138/138 ×3"): rung suite = 88/138 ×3
(m3≡m4 parity holds; interp/run/compile identical). 50 rungs FAIL.

## The bug (bracketed to the land mine via gdb, MONITOR-FIRST-style)

Deterministic reproducer (no crash, wrong value):
    q(hello).
    main :- q(X), write(X), nl.
    :- initialization(main).
  SCRIP prints EMPTY; gprolog prints `hello`.
  Variant `q(X) -> write(got(X))` prints `got(_G0)` — call SUCCEEDS, X returns UNBOUND.
  Ground query `q(1) ; p(1)` works (`yes`) — only the VARIABLE-ARG case is broken.

Segfault variant (same root): `q(X), ..., fail` and `findall/3` over it → jump to 0x0
(RIP=0, stack region reads all-zero — an unpatched jump target / re-entry into the
throwaway frame region after it's gone). Same underlying cause as the wrong-bind.

## Exact trace (gdb)

Caller stages X correctly:
  - rt_proc_call_gen_h name=q/1 nargs=1, g_call_args[0] = NAMETRAP (DT_N slen=2) .p=0x1aede70
  - that VCELL.cellp = 0x7ffffffe9f00  = X's real cell, v=0 (DT_SNUL, unbound). CORRECT.
  - frame slot[1] (fb+16) receives the SAME NAMETRAP .p=0x1aede70. CORRECT.

Head-unify binds the WRONG cell:
  - $unify handler (by_name_dispatch.c:1391) sees args[0] = NAMETRAP .p=0x1aedeD0  (DIFFERENT VCELL, +0x60)
  - args[1] = DT_S "hello". CORRECT value.
  - plw_bind writes "hello" -> cell 0x7ffffffd9cb0  ← NOT X's cell (0x7ffffffe9f00).
    0x7ffffffd9cb0 is ~64KB BELOW, in the callee frame/scratch region (same zeroed
    region the segfault RIP unwinds into).

## Diagnosis

Between receiving the head arg (frame slot[1], a NAMETRAP → caller's X cell) and reaching
the body `$unify`, the head-argument variable is RE-WRAPPED to point at a FRESH callee-frame
cell instead of being dereferenced through to the caller's shared cell. `plw_unify_cells`
binds correctly (plw_bind fires) — but on the throwaway cell. When q returns, that cell is
gone; caller's X stays unbound.

This is the "Term↔cell cross-structure var-sharing gap" flagged in GOAL-PROLOG-BB PL-ISO-6
(`pl_term_to_cell_word_m` "first occurrence returns a value-copy"). The head-arg var must be
threaded as a REFERENCE to the caller's cell, not a value-copy into a new frame cell.

## Fix direction (NOT yet applied)

The clause head-match for a variable head-arg must unify the CALLER'S cell (deref the incoming
NAMETRAP to ->cellp) rather than allocating/wrapping a new frame-local cell. Locate where the
head arg → `$unify` arg[0] is materialized for a compiled clause (lower_prolog.c clause-head
lowering + how the frame slot NAMETRAP becomes the $unify operand) and make first-occurrence
of a head var carry the shared cellp through, so plw_bind lands on 0x...e9f00.

Key code:
  - src/runtime/by_name_dispatch.c: plw_unify_cells/plw_cell_deref/plw_entry (60-119),
    $unify arm (1390). These are CORRECT — deref follows NAMETRAP slen==2 → cellp.
    The bug is UPSTREAM: args[0] already points at the wrong VCELL.
  - src/lower/lower_prolog.c + src/parser/prolog/prolog_lower.c: clause head-arg lowering.
  - The two VCELLs (0x1aede70 caller vs 0x1aeded0 at $unify) diverge — find where the second
    is minted.

## Env for repro (this sandbox)
  - Repos cloned to /home/claude/work/{SCRIP,corpus,dotgithub}; symlinked to canonical
    /home/claude/{SCRIP,corpus,.github}; refs symlinked to uploaded gprolog/swipl zips.
  - apt: nasm libgc-dev libgmp-dev m4 gprolog(1.4.5). Built: make scrip + make libscrip_rt.
  - Baseline: bash scripts/test_prolog_rung_suite.sh  → 88/138 ×3.
  - Repro: ./scrip --run /tmp/q.pl  (q.pl above).

## ============ CORRECTION (deeper root cause found) ============

The "head-unify binds a throwaway cell" above is a SYMPTOM. TRUE ROOT CAUSE:

**FRAME-CONVENTION MISMATCH: the RSP-framed emitted proc box ignores the heap `fb`
pointer that rt_proc_call_gen_h binds args into.**

Evidence (gdb + emitted .s):
- rt_frame_bind_args CORRECTLY binds g_call_args[0] (NAMETRAP→X, p=0x1aede70) into
  the heap frame at fb+16 = 0x7ffff7ed0030. Args ARE staged correctly.
- BUT the emitted `proc_q$1_α` prologue is:
      sub rsp, 65544          ; frame allocated ON THE STACK
      mov rdi, rsp ; rep stosb ; ← ZEROES the whole stack frame
      ...all locals addressed [rsp+off]...
  It NEVER reads rdi (the fb arg from fn(fb,entry)). It builds a fresh rsp frame and
  zeroes it, wiping the passed args. So frame slot[1] read by the box (lea rdi,[rsp+16]
  = 0x7ffffffd9cb0) is a ZEROED STACK cell, not the heap fb+16 where X's NAMETRAP lives.
- Result: IR_VAR_REF wraps the wrong (zeroed, callee-stack) cell → head-unify binds it →
  caller's X (0x…e9f00) never touched → X unbound → wrong/empty output; under backtrack the
  stale stack region → jump-to-0 segfault.

## This is an s65 R12-ERAD / ZC_FRAME_RSP straggler

git log f7de3863: "R12-ERAD s65: ZC_FRAME_RSP complete ... RSP is now the default
(zeta_choices.h flipped)". The emitted proc box was regenerated to be a self-contained
RSP-framed function (sub rsp,N; [rsp+off] locals). But the PROLOG proc-call RUNTIME path
rt_proc_call_gen_h (rt/rt.c ~571-608) still uses the OLD heap-fb convention:
  base = rt_zls_alloc(total); fb = base+16; rt_frame_bind_args(fb,p,nargs);
  (void)p->fn((void*)fb, 0); result = *(DESCR_t*)(fb+0);
Under RSP the box neither reads args from fb nor writes its result to fb+0 — it uses its
own rsp frame. The two conventions were reconciled for whatever paths s65 covered, but NOT
for the Prolog generator-call path (rt_proc_call_gen_h / rt_call_proc_descr / the resume
variants rt_proc_resume_frame*). Every Prolog user-predicate CALL is therefore broken for
non-ground args → the 50 rung failures.

## Corrected fix direction (needs Lon's read — this is convention-level)

Two coherent options:
 (A) Make rt_proc_call_gen_h pass args the way the RSP box expects. Determine the RSP box's
     arg-input contract (does it read g_call_args[] directly? expect args pre-placed at a
     known [rsp+off]? via registers?) from a WORKING language's proc path (SNOBOL4/Icon, which
     s65 converted) and match it. Likely the box should read g_call_args[] itself and the C
     caller should NOT alloc/bind a heap fb at all — just call the α label.
 (B) If the intended end-state keeps a heap frame, the box prologue must set its frame base
     FROM rdi (mov rsp-frame-base ← rdi) instead of sub rsp — i.e. the box was mis-generated
     for the proc case. Then bind/result via fb stays valid.

MUST check how the CONVERTED SNOBOL4/Icon proc call works before choosing — do NOT guess.
Grep: the SNOBOL4/Icon emitted proc prologue + their runtime call entry; compare arg handoff.
Relevant: src/templates/bb_call_proc_staged.cpp, bb_enter_init.cpp, the proc α template in
the emitter, zeta_choices.h (ZC_FRAME_RSP), and rt/rt.c rt_proc_call_gen_h/rt_call_proc_descr.

## Board impact
If (A/B) reconciles the convention, expect the bulk of the 50 failing rungs (all the
backtrack/fact/findall/assert families) to recover at once, since they all route through
user-predicate calls with variable args.

## ============ FINAL PRECISION — the two conventions ============

Confirmed by comparing a WORKING SNOBOL4 proc call to the broken Prolog one:

SNOBOL4 (WORKS) uses the DYN-SCOPE / NAME convention:
  - rt_name_save_push (rt/rt.c ~694): args written into NAMED variable cells
    (*cell = arg / NV_SET_fn(nm,arg)). The box reads its param by reading the
    global NV cell for that name — NOT from a caller-passed frame slot.
  - So the box zeroing its own `sub rsp` frame is harmless: params live in NV cells.
  - DUB reads X from [rsp+240] which was loaded FROM the NV cell, not from fb.

Prolog (BROKEN) uses the LEXICAL / FRAME-BOUND convention (rt_pcall_t.lex=1,
rt/rt.c ~756): args must be threaded THROUGH THE FRAME. rt_proc_call_gen_h binds
them into a HEAP fb (rt_zls_alloc) and calls p->fn(fb,0). But the RSP box builds
its OWN frame via `sub rsp,N` and addresses locals [rsp+off] — a DIFFERENT region
than the heap fb. So frame-bound args never reach the box. THIS is the mismatch.

The NCB-1 comment (rt/rt.c ~740) states the intended shape:
    prologue leaf → frame (RSP BUMP) → call p->fn(fb,0) → release → epilogue leaf
Note "RSP BUMP" for the frame — but rt_proc_call_gen_h uses a HEAP fb, not an rsp
bump, so fb ≠ the box's rsp frame. Under a real rsp-bump they'd be the SAME memory
and args would line up. The reconciliation was done for the dyn-scope path (SNOBOL4)
but the lexical (Prolog) path still hands a heap fb to an rsp-framed box.

## DECISION NEEDED (Lon) — this is ABI/convention, not a local bug

The fix touches the whole Prolog proc-call spine (call + resume-β + generator +
det variants: rt_proc_call_gen_h, rt_call_proc_descr, rt_proc_resume_frame,
rt_proc_resume_frame_h) and their emitted-box contract. Options:

 (A) LEXICAL-VIA-RSP: make the emitted Prolog proc box take fb in rdi and use IT as
     the frame base (NOT sub rsp / not zero it), OR make rt_proc_call_gen_h do a real
     rsp bump so fb IS the box's frame. Requires the box prologue to differ for the
     frame-bound (Prolog) case vs the NV-name case (SNOBOL4). The emitter currently
     emits ONE prologue shape (sub rsp; rep stosb) for both — that is the actual defect.

 (B) LEXICAL-VIA-NV: give Prolog params stable cells the box reads by name/handle,
     like SNOBOL4 — but Prolog vars are frame-local and recursive, so NV-global cells
     are wrong for Prolog (recursion would clobber). (A) is almost certainly correct.

The single line that most localizes the defect: the emitted proc α prologue
(`sub rsp,N; mov rdi,rsp; rep stosb`) is generated identically regardless of whether
the proc uses dyn-scope (SNOBOL4, args in NV cells) or lexical frame-bound (Prolog,
args in fb). For Prolog it MUST consume rdi (the passed fb) as its frame, not
allocate+zero a fresh rsp one. Find that prologue in the emitter/proc template and
the ZC_FRAME_RSP switch in zeta_choices.h; that is where s65 left the Prolog case behind.

## STATE AT STOP
- No code changed. Tree CLEAN at 6a165d14. No commit, no push. Credential never used.
- Diagnosis complete and durable in this file. Reproducer /tmp/q.pl (also in finding).
- Baseline: 88/138 ×3 (NOT cursor's 138/138). Root cause fully bracketed to the
  frame-convention mismatch above. Fix is convention-level → needs Lon's direction on (A).
