# DESIGN-ICON-SUSPEND.md — Icon user-defined generators (`suspend`) in the BB model

**Status:** DONE — implemented and verified. All three rung03 `suspend` programs pass in m3 (`--run`): `rung03_suspend_gen`→`1 2 3 4`, `rung03_suspend_gen_filter`→`4 3 2 1`, `rung03_suspend_gen_compose`→`1 2 3 1 2`. Icon m3 corpus floor held at 169; discipline gates green. (FACT-RULE proc-slab selector ruling granted by Lon 2026-06-24.)
**Author:** Claude · **Date:** 2026-06-24 (completed 2026-06-25) · **Goal:** GOAL-ICON-BB rung03 (`suspend` ×3, the named top lever)

The three root causes actually fixed (the earlier draft below predates the resume-spine landing and is retained for history): (1) the `IR_PROC_GEN` call path drove args from `nd->operands` (empty for `dval==3.0`) instead of the argblks in `IR_EXEC.counter`, so the generator's argument was never materialised — routed it through `flat_drive_userproc` like a normal staged call; (2) a generator proc's body-terminal success was seeded `PSUCC`, so loop exhaustion *succeeded* (re-yielding a stale value) instead of failing — seeded it `PFAIL` when the body contains `suspend` (fall-off-end ⇒ exhausted ⇒ fail, per JCON `expr.failure → proc.failure`); (3) the flat-chain emitter's per-node γ resolution had no `IR_FAIL` case, so a node whose success-continuation was the proc fail port defaulted to the proc *success* label — added the `γ.node->op == IR_FAIL ⇒ lbl_ω` binding (consistent with the parallel emitter already doing so).

---

## 0. The three failing rungs (all the same shape)

```icon
procedure upto(n)
  local i; i := 1;
  while i <= n do suspend i do i := i + 1;
end
procedure main()
  every write(upto(4));
end
```

- `rung03_suspend_gen`     — count up → **empty output** (yields nothing)
- `rung03_suspend_gen_compose` — two sequential drives → **empty output**
- `rung03_suspend_gen_filter`  — count down → **hang (rc=124)**

A user-defined generator: `suspend EXPR do BODY` inside a loop, driven by `every write(...)`.

---

## 1. Root cause (verified by reading every layer)

The **lowering exists but the native emitter has no driver** for it.

- `lower_icon.c:190` (`TT_SUSPEND`) builds `IR_SUSPEND` stashing the EXPR subgraph in
  `IR_EXEC(sn).counter` and the `do`-BODY subgraph in `IR_LIT(sn).ival`, `dval=1.0`. **But α/β/γ/ω
  are the plain sequence successor/fail — no resume-spine wiring.** (Dump shows `IR_SUSPEND ival=<ptr>`,
  γ→the while re-test, with no Succeed/resume edges.)
- `IR_SUSPEND` is **absent** from `ir_is_generator_kind` and `gen_bb_is_gen_arg` (`emit_bb.c:2218/2227`).
- There is **no `bb_suspend.cpp`** and **no `flat_drive_suspend`**.

So the node falls through with no codegen: the generator yields nothing (empty) or loops forever (hang).
It is green-field codegen, not a broken edge.

## 2. Canonical target (JCON `ir_a_Suspend`, `refs/jcon-master/tran/irgen.icn:937`)

```
t   := ir_label(p, "suspend")        # resume label
susp:= ir_tmp(...)                    # the yielded-value temp
ir(p.expr → susp); ir(p.body)
chunk(start,        [Goto(expr.start)])
chunk(expr.success, [Succeed(susp, t)])   # <-- THE PRIMITIVE: yield susp to caller, resume at t
chunk(t,            [Goto(body.start)])    # on resume: run the `do` body…
chunk(body.success, [Goto(expr.resume)])   # …then resume expr for the next value
chunk(body.failure, [Goto(expr.resume)])
chunk(expr.failure, [Goto(failure)])       # expr exhausted → proc fails (generator done)
```

`Succeed(value, resumelabel)` = the activation **returns a value to its caller while preserving
itself**, so the caller can **resume** it and control re-enters at `resumelabel`. This is the whole
generator protocol; `_compose` (two independent activations) only works because each suspended
activation persists independently.

## 3. Caller side today (the consumer that must drive the resume)

- `flat_drive_every` (`emit_bb.c:2729`) wires `body.success → body_β` (resume for next value),
  `body.failure → every.success`. Correct, matches JCON `ir_a_Every`. So `every write(upto(4))`
  resumes the body at `body_β`, which must reach `upto`'s **generator-resume**.
- But `upto` routes as **`CALL_ROUTE_PROC_STAGED`** (`emit_bb.c:2881`; `dv∈{1.0,3.0}`,
  `rt_proc_is_registered`). `bb_call_proc_staged.cpp` stages args (`rt_arg_stage`) and
  `call rt_call_proc_descr(name,nargs)` — a **one-shot** dispatch. Its `def β` just re-jumps to the
  next chain element; it never re-invokes the proc at a resume point. The activation has already
  returned; `body_β` has nowhere to land. **This is the break.**

## ✅ RULING (Lon, 2026-06-24) — the `(void*,int entry)` selector is ALLOWED

**Verbatim intent:** the `(void*, int entry)` prototype is fine **as long as the code it dispatches
into is emitted x86, not C.** What is forbidden is a *C* Byrd Box — a C function carrying the α/β box
logic / entry points. The proc slab is native x86, so using `entry` (rsi) to pick fresh-start vs
resume — dispatched in the **emitted** prologue — is on the right side of the rule. `bb_suspend` is an
emitted-x86 template, never a C box. **§4 below is the pre-ruling analysis, retained for context;
§4A is the approved build.**

## §4A — APPROVED LEAN BUILD (everything gated on generator-proc / IR_SUSPEND so the 151 floor is safe until it works)

**BUILD STATUS (2026-06-24):** Pieces **1, 3, 4 + chain wiring LANDED** (SCRIP `aa16969` runtime, `ecef926`
template+lowering+wiring) — building clean, floor-safe (gate still rejects → suspend EXCISES, smoke 12/12).
**REMAINS: piece 2 (prologue entry-dispatch), piece 5 (caller gen-call box), then flip the gate + debug.**
The committed state is floor-green; resume directly at piece 2.
- [x] **1. Runtime** `rt_proc_call_gen` / `rt_proc_resume_gen` (persistent `g_gen_arena` activation stack).
- [ ] **2. Prologue entry-dispatch** — `xa_flat.cpp` frame-active TEXT (+BINARY) arm, for generator procs
      only (gate on a new `g_gen_proc_active`, set in scrip.c's proc-emit loop from
      `proc_table[pi].is_generator`): append `cmp esi,0` / `jne <flat_lbl_β>` after `mov r12,rdi`
      (esi≠0 ⇒ resume ⇒ jump chain β, which `ecef926` already routes to the suspend's resume β).
- [x] **3. `bb_suspend`** template (`bb_suspend.cpp`, emit_core dispatch, header, Makefile).
- [x] **4. Lowering** resume-spine (`TT_SUSPEND`: γ=psucc, operand[0]=expr value, operand[1]=do-body).
- [x] **chain wiring** (BFS collects do-body; `g_suspend_dobody_beta`; `lbl_β`→suspend-resume routing).
- [ ] **5. Caller gen-call box** — add `int rt_proc_is_generator(const char*)` (reads proc_table); in the
      call-route resolver, when `rt_proc_is_registered && rt_proc_is_generator(fn)` pick a new route whose
      box does α=`rt_proc_call_gen` (stage args, value→slot, `cmp type,99: je ω; jmp γ`),
      β=`rt_proc_resume_gen` (value→slot, `cmp type,99: je ω; jmp γ`). Model on `bb_call_proc_staged`.
- [ ] **flip gate** — delete `if (nd->op == IR_SUSPEND) return 0;` in scrip.c; build; rung03_suspend_gen
      → expect `1\n2\n3\n4\n`; debug slot/label/ABI; verify floor 151 + smoke 12/12 + rung03 ×3 PASS.

Reuses the existing `every` machinery: make the generator-proc **call box** itself the generator —
α = start, β = resume — exactly like `bb_to` (α init / β advance). `flat_drive_every` already wires
`body.success → body_β` and `body.failure → every.success`, so NO deep caller surgery.

**Five pieces, each gated so non-generator procs are byte-unchanged (floor-safe):**

1. **Runtime (`rt.c`) — persistent-frame generator dispatch.** `g_proc_arena` is depth-freed on
   return; generators need the frame to survive across suspend. Add a small activation stack:
   `rt_proc_call_gen(name,nargs)` — alloc a persistent frame (own arena, NOT depth-freed), stage args,
   `p->fn(frame,0)`, push the activation, return `frame[0]`; `rt_proc_resume_gen()` — top activation,
   `p->fn(frame,1)`, if `frame[0]` is FAILDESCR (type 99) pop+free and return fail, else return
   `frame[0]`. Single-activation stack suffices for rung03 (incl. `_compose` — sequential, never two
   live at once); a small stack also covers nesting.

2. **Prologue entry-dispatch (`xa_flat.cpp`), gated on a `g_gen_proc_active` flag.** The frame-active
   prologue (`push r12; mov r12,rdi`) gains, for generator procs only,
   `cmp esi,0; je α_body; jmp β` (the idiom already used on the non-frame path at lines 80-82). esi≠0
   ⇒ resume ⇒ jump to the chain β, which propagates to the active `bb_suspend` box's β. Non-generator
   procs keep the exact current prologue → floor untouched.

3. **`bb_suspend` template (emitted x86, new `BB_templates/bb_suspend.cpp`).** α (reached from
   while-cond-true): copy the EXPR value slot → `frame[0]` (the proc result), then `ret` (the
   frame-active epilogue's succeed path: `mov eax,1; pop r12; ret` — value already in frame[0]).
   β (resume, reached via prologue jump on re-entry): jump to the DO-body entry, which runs `i:=i+1`
   then `jmp γ` (loops back to the while test). r12 push/pop stays balanced: each entry (fresh or
   resume) pushes r12 in the prologue; each suspend-`ret` pops it.

4. **Lowering (`lower_icon.c` `TT_SUSPEND`).** Replace the stash-as-subgraphs form with INLINE
   producer boxes so the chain-β propagation reaches them: lower EXPR (`i`) as a producer box (its
   slot feeds bb_suspend), the DO-body (`i:=i+1`) as a box whose γ → the suspend's sequence-successor
   (the while loop-back). Wire `bb_suspend`: α copies EXPR slot → result, γ = (returns via epilogue);
   β → DO-body entry; DO-body.γ → loop-back. Register `IR_SUSPEND` in `ir_is_generator_kind` +
   `gen_bb_is_gen_arg`.

5. **Caller generator-call box (`bb_call` variant / route).** When the callee `rt_proc_is_registered`
   AND is_generator: α = stage args + `rt_proc_call_gen` → value to slot; `cmp type,99: je ω; jmp γ`.
   β = `rt_proc_resume_gen` → value to slot; `cmp type,99: je ω; jmp γ`. The existing `every` drive
   does the rest.

**Then:** remove the `IR_SUSPEND` gate rejection (admit it), re-test floor 151 + smoke 12/12 + the
3 rung03 rungs → PASS. **Order of landing (each step floor-safe because the gate still rejects until
the last step):** 1→2→3→4→5, build+`.s`-dump+run after each, flip gate last.

## 4. (pre-ruling analysis — retained for context) THE FACT-RULE COLLISION

`rt_call_proc_descr` (`src/runtime/rt/rt.c:268`) is the dispatch:

```c
char *fb = (char*)&g_proc_arena[g_proc_depth * PROC_FRAME_QWORDS];  // depth-indexed frame
g_proc_depth++;
... stage args into fb ...
(void)p->fn((void*)fb, 0);          // invoke proc native slab, entry=0 (α)
DESCR_t result = *(DESCR_t*)(fb+0); // result from frame[0]
g_proc_depth--;                     // <-- FRAME FREED on return
return result;
```

and the proc-fn type (`src/include/bb_box.h:33`):

```c
typedef DESCR_t (*bb_box_fn)(void * zeta, int entry);   // (void*, int entry)
```

Two collisions with load-bearing rules:

**(a) The resume entry is the forbidden signature.** Re-entering a suspended activation at its
suspend point needs `p->fn(frame, resume_id)` with `entry != 0`. But `(void *ζ, int entry)` as an
α/β selector is **exactly** what the **"NO C BYRD-BOX FUNCTIONS"** FACT RULE forbids
(GOAL-ICON-BB.md): *"A box… NEVER takes an integer `entry` argument to select α vs β… The C
signature `DESCR_t NAME(void *ζ, int entry)` … is FORBIDDEN… deleted three times… keeping the build
green is not a license to preserve a forbidden box."* The proc-dispatch **already** uses this
forbidden-shaped pointer at proc level (always `entry=0`); the `entry != 0` half is latent. A
generator is precisely what lights it up.
  - **Question for Lon:** Is the proc-activation entry `(frame, entry)` *grandfathered* (it is the
    procedure-call boundary, entered by a real `call`, not a box entered by `jmp` — arguably outside
    the box rule's scope)? If grandfathered, generator-resume via `entry=1` is the natural, minimal
    mechanism. **If NOT** grandfathered, we need a resume mechanism that carries no `entry` int —
    e.g. a saved resume **address** in the frame that the proc's prologue indirect-jumps to (the
    proc is always entered at one label; it reads `frame.resume_ip` and `jmp`s there; fresh
    activations have `resume_ip = α`). That keeps a single entry point and obeys the rule, at the
    cost of a frame slot + an indirect jump. **I lean toward this address-in-frame form** because it
    honors the rule's spirit (no `int entry` selector) and matches JCON's `Succeed(value, t)` where
    `t` is an address.

**(b) Frame lifetime breaks the depth-stack.** `g_proc_arena` is freed by `g_proc_depth--` on
return. A suspended generator's frame **must survive** until the generator is exhausted (the caller
stops resuming or the proc fails). So generator activations cannot use the depth-stack discipline
unchanged.
  - **Proposed:** a generator activation gets a frame that is **not** freed on suspend-return; it is
    freed only when the proc reaches its terminal FAIL (`expr.failure → proc fail`) or the caller
    abandons it. Simplest correct form: the caller (the `every`/proc-gen driver) owns the activation
    handle and frees on exhaustion. For the non-recursive single-drive cases (rung03), a per-call
    persistent frame slot suffices; `_compose` needs two, which the caller-owned model gives for free
    since each `call` site has its own activation.

## 5. Proposed implementation (pending §4 ruling) — smallest correct path

Assuming the **address-in-frame** resume form (rule-safe) and **caller-owned activation**:

1. **Lowering (`lower_icon.c`):** wire `IR_SUSPEND`'s ports per JCON §2 — `expr.success → Succeed`,
   `Succeed.resume → body.start`, `body.success/failure → expr.resume`, `expr.failure → proc-fail`.
   Register `IR_SUSPEND` in `ir_is_generator_kind` + `gen_bb_is_gen_arg`. (Low risk, no ABI change —
   can land first behind the gate so it EXCISES loudly until the driver exists.)
2. **`bb_suspend` box:** evaluate EXPR into the proc result slot (`frame[0]`), store the resume
   address (`&t`) into a reserved frame slot, and **suspend-return** (write result, set a
   "suspended/resumable" status distinct from succeed-and-done and from fail, `ret`). On resume the
   proc prologue jumps to `frame.resume_ip`; `t` runs the `do` BODY then `jmp` back to the EXPR loop.
3. **Proc prologue/`bb_callee_frame`:** add a single entry that reads `frame.resume_ip` (init = α for
   fresh activations) and indirect-jumps. No second C entry point; one label, dispatched by the saved
   address. This is the only delicate ABI touch and the part most needing the §4 ruling.
4. **Caller (`bb_call_proc_staged` + `flat_drive_*`):** distinguish 3 dispatch outcomes — value+resumable
   (γ, and `β` re-invokes the *same* activation/frame), value+done (γ, `β`→ω), fail (→ω). `rt_call_proc_descr`
   grows a sibling `rt_resume_proc_descr(handle)` that re-enters without re-staging args and **without**
   freeing the frame until exhaustion.
5. **Gates:** must stay green — `test_gate_icn_no_stack` (the activation frame is the existing
   `g_proc_arena`, not a value stack), `test_gate_icn_one_reg_frame`, smoke 12/12, and the floor 151
   must not drop. New rung coverage: rung03 ×3 → PASS.

## 6. Risk

High — it is the proc-call boundary in a stackless ABI, the part the goal file calls "the trickiest,"
and it sits directly on the most-guarded FACT RULE. The §4(a) ruling determines whether this is a
small `entry=1` change or a from-scratch address-dispatch resume mechanism. **No code until that
ruling** — implementing the wrong form is a rejection-worthy FACT-RULE violation, not a mergeable bug.
