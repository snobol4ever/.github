# TEMPLATE REVAMP — CONSTRUCTION RULES (DRAFT for review, 2026-06-01)

Synthesized from Lon's session notes. **DRAFT** — not yet folded into the five GOAL-*-BB files /
RULES.md / the purity+concurrency gates. That fold-in is the grand-master-reorg (byte-identical-×5
block, like the other FACT RULES). Review first.

**WHY (the problem being killed).** Each BB box carried TWO divergent arms — `MEDIUM_BINARY` (hand-coded
byte map) + `MEDIUM_TEXT` (GAS) — PLUS a hand-counted `bb_bin_t` patch-offset table. The two arms drift
(e.g. BINARY baked `movabs` absolute addresses while TEXT used position-independent `lea [rip+...]`); the
literal `{13,65,80,84,95}` offsets break on every edit. This is the SPIN and CHURN every GOAL-*-BB session
keeps paying. The revamp makes a box ONE description, medium switched invisibly, patch positions discovered.

---

## STATUS — START HERE (updated 2026-06-02)

**The shared looping-box keystone is LANDED at SCRIP `origin/main` = `30e8422`.** All four sessions
(SNOBOL4 / Icon / Prolog / Raku) should **rebase onto `30e8422` before converting any box**, especially any
box with an internal loop or RW scratch — the internal-label + ζ-frame support already exists; do NOT rebuild it
(it lives in the SHARED file `x86_asm.h`, so a parallel implementation would collide). See the two sections
below: "RESOLVED — INTERNAL LABELS + ζ-FRAME SCRATCH" (the API + reference boxes) and the updated
"`x86_asm.h` VOCABULARY". Reference conversions to copy: `bb_pat_pos.cpp` (loop-free) and `bb_pat_span.cpp`
(looping). Per-box recipe + the byte-verify-vs-`as` discipline:
`HANDOFF-2026-06-02-OPUS48-SNOBOL4-BB-TEMPLATE-REVAMP-V3-KEYSTONE-POS-SPAN.md`.

Each session converts its OWN boxes (table under "DIVVY-UP MATERIAL" below) and edits only its own files; the
dispatch/decl inserts land on different lines and `x86_asm.h` additions are additive. The ONE remaining shared
item — the VARIABLE-LENGTH define/jmp-pair loop for the combinators (`bb_pat_alt/cat/match`, FENCE pair path) — is
now **DESIGNED** (see "STILL OPEN → DESIGNED" below: two pointer-carrying records `'P'`/`'Q'` in `x86_asm.h`); it
awaits a clean dedicated landing of the shared `x86_asm.h` edit (all four sessions aware), then each session
converts its own combinators with the identical FOR-over-pair-array body.

---

## THE RULES

**R1 — DROP `MEDIUM_MACRO_DEF`.** No macro-def arm. Delete any `IF(MEDIUM_MACRO_DEF, …)`.

**R2 — ONE MEDIUM, INVISIBLE.** BINARY and TEXT are produced by the SAME body. The template NEVER branches
on the medium. The `x86_*` encoders switch on the medium global internally (`MEDIUM_BINARY` → in-band record
stream; else → GAS text). A reader of the template cannot tell which medium is active.

**R3 — ONE RETURN PER `PLATFORM_*`.** Each `if (PLATFORM_X86)` / `PLATFORM_JVM` / … has exactly ONE `return`
of a single concatenation expression. (X86 ONLY for now; JVM/JS/NET/WASM arms stay stubbed/unchanged.)

**R4 — STRING CONCATENATION ONLY.** The x86 arm is one `+`-chain of `x86(...)` calls (wrapped by IF/FOR).
No statements, no imperative control flow, no temporaries.

**R5 — NO LOCAL VARIABLES (x86 arm); OPERANDS FROM `_` ONLY.** The x86 arm declares no local and references
no `pBB`. Operand data comes from:
  - (a) **promoted node scalars on `_`** — `_.op_sval`, `_.op_ival`, … (set at the single dispatch point from
    `nd->FIELD`; see the FACT RULE below);
  - (b) **`_` (g_emit) globals** — labels (`_.lbl_α/β/γ/ω`), ports, medium, driver handoffs (child cache,
    pair arrays, subject slot, match labels);
  - (c) **literals**.
  **NEVER the `pBB` parameter and NEVER `_.node`** (see FACT RULE). Pure parameterless accessor functions
  reading `_` are the sanctioned way to keep the arm local-free and English-readable, e.g.
  `static inline long lenN(){ return (long)(int)_.op_ival; }` → `x86("add","eax",lenN())`.
  (The function-top `int nid/sid` that feed the NON-x86 platform arms are out of scope of this rule.)

**R6 — ALL VARIANCE INLINE, IN THE ONE CONCAT.** Conditionals and repetition fold INTO the single
concatenation via combinators — never per-variant `if`-blocks or early returns:
  `X + IF(cond, A) + Y + FOR(i, lo, hi, BODY(i)) + IF(SPECIAL_MODE, Z) + …`

**R7 — `x86(...)` FRONT-END, KEYED ON THE MNEMONIC (1st arg).** The template-facing API is ONE overloaded
`x86(mnem, …)`. The first arg (mnemonic string) PLUS the trailing args' cardinality/type select the encoding
via C++ overloading. The typed `x86_*` encoders are the internal implementation. Forms in use:
```
x86("mov",  "eax", "r14d")              reg/mem 2-op  (mov/cmp/test/movsxd/movzx/lea-subj)
x86("add",  "eax", N)                   reg, imm      (add/sub imm8-or-imm32; mov-imm)
x86("jmp",  PORT_GAMMA)   x86("def", PORT_BETA)        jmp / jcc / label-define (ports)
x86("jg",   PORT_OMEGA)                 conditional jump to a port
x86("call", "memcmp", ptr)              RO runtime-helper call
x86("lea",  "rdi", "[rip + __]", addr, label)          RO pointer load
x86("push", "r10")   x86("pop", "r10")  push / pop
```
Add a NEW shape by adding an encoder + a dispatch case in `x86_asm.h` — NEVER by hand-writing bytes in a
template.

**R8 — SIDE-EFFECT-FREE CONCAT; SIDE EFFECTS ONLY IN `bb_emit_x86`.** Every function in the concatenation is
PURE (returns a string, mutates nothing). The only side effects — emit bytes, register a rel32 patch, define
a label — happen in `bb_emit_x86(...)`, called from the `extern "C"` wrapper AFTER the pure string is built:
```
extern "C" void bb_pat_len(IR_t *pBB) { bb_emit_x86(bb_pat_len_str(pBB)); }
```

**R9 — IN-BAND PATCH RECORDS REPLACE `bb_bin_t`.** Patch/label sites are TAGGED RECORDS inside the returned
string; `bb_emit_x86` walks them and DISCOVERS each byte position as it copies — no hand-counted offsets to
drift. Records (BINARY only; TEXT passes through as GAS):
  - `L <len> <bytes>` — literal code bytes
  - `J <port>`        — rel32 patch to a port label (the preceding `L` carries the opcode)
  - `D <port>`        — define a port label here (0 bytes)
  Ports: `0=α 1=β 2=γ 3=ω`. ONE primitive (`bb_emit_patch_rel32`, `disp = target − (site+4)`) serves jmp
  rel32, `lea [rip+disp]`, and `call qword [rip+disp]`. This IS the "BEGIN/END patch-marker" idea made
  concrete: the `J`/`D` tag is the marker; the displacement is computed by the primitive, not the template.

**R10 — BINARY MUST AGREE WITH TEXT (`as`).** For every plain instruction, the BINARY bytes equal what `as`
produces from the TEXT arm — same short-form choice (imm8 vs imm32), same REX.W width, same SIB. The ONLY
intentional medium-specific encodings: the RO load (BINARY `movabs imm64` vs TEXT `lea [rip+label]` /
`call sym@PLT`) and jumps (BINARY discovered rel32 vs TEXT named label). Making the RO load
position-independent in BINARY too (`lea [rip+disp]` into a sealed RO trailer) is REG-RO — a one-function
change in the encoder, no template edit.

**R11 — TEXT-FIRST CONVERSION.** To convert a box: take the **TEXT arm as source of truth**, THROW AWAY the
hand-coded BINARY arm + its `bb_bin_t`, and re-express the TEXT in `x86(...)` calls; the encoders regenerate
BINARY. Hand conversion (deterministic auto-conversion is too hard).

**R12 — NO SAFETY NET / GROUND ZERO / GO FAST.** Everything is effectively broken (we are at
`write("hello world")`); byte-identity against the broken baseline is NOT the goal. Do NOT run full
regression suites — optional only: a couple of before/after `as` `.o` comparisons. Four parallel sessions
fix any few typos. The over-testing in the v1 session is exactly what we are avoiding. Move STRAIGHT-FORWARD.

**R13 — FORMAT/COMMENTS DEFERRED.** Do not polish formatting or comments until the GOAL-*-BB sprints finish.

---

## ⛔ FACT RULE — A TEMPLATE READS ONLY g_emit; pBB AND NODE-NEIGHBORS ARE FORBIDDEN (Lon directive 2026-06-01)

**A BB template emits exactly ONE node's machine code. Its x86 arm references NO `pBB` and NEVER dereferences
a node neighbor.** All operand data a template needs is GATHERED BEFORE the template is called and handed in
through the `_` (g_emit) region. Specifically:

1. **Only fields DIRECTLY ON THE NODE may be promoted.** At the single dispatch point (`emit_core.c`, where
   `g_emit.node/nid/sid` are already set) the emitter copies the handful — **four or five** — of
   directly-accessible node fields into dedicated g_emit slots: today `g_emit.op_sval = nd->sval` and
   `g_emit.op_ival = nd->ival` (more added the same way as boxes need them). These are the ONLY promotions;
   a promotion is `nd->FIELD`, never `nd->α->…` / `nd->c[i]->…` / a sibling.

2. **The template reads ONLY `_`** — promoted operands (`_.op_sval`, `_.op_ival`, …), labels/ports
   (`_.lbl_α/β/γ/ω`, `PORT_*`), driver-supplied handoffs (`_.child_fn`, child cache, the pair arrays,
   subject-slot, match labels), and literals. It does **NOT** reference a `pBB` parameter (there is none —
   see below) and does **NOT** dereference `_.node` (dereferencing `_.node` is a back-door to neighbors via
   `_.node->α` — equally forbidden). **The `pBB` parameter is REMOVED** from a converted box end-to-end: the
   `bb_X_str()` template fn, the `extern "C" void bb_X(void)` wrapper, the `bb_templates.h` prototype, and the
   `emit_core.c` dispatch call are all parameterless; EVERY arm (x86 + the not-yet-revamped JVM/JS/NET/WASM)
   reads `_` (`_.op_sval`/`_.op_ival`/`_.nid`/`_.sid`). With no `pBB` in scope, the temptation cannot exist.

3. **NEVER reach a neighbor to gather information.** A template cannot read `pBB->α`, `pBB->c[]`,
   `pBB->next`, or any child/sibling/parent — it has no node handle at all (no `pBB`, no `_.node` deref). If a
   box needs such a fact, the **driver** (`emit_bb.c` flat-drive / `emit_core` promotion) resolves it FIRST and
   deposits a SCALAR (or a child-cache entry / a g_emit field) — exactly the existing `bb_match` (subject
   slot + element labels) and combinator (child heads + pair arrays) pattern. There is no emit-time case that
   genuinely requires a neighbor read.

**WHY (two reasons):** (a) **no confusion** — there is exactly one place operands come from (`_`), so a
template can never silently depend on graph shape; (b) **it makes BB-FUSION impossible** — a template
physically cannot reach into the next box and weld two boxes into one "double-indemnity" box, because it has
no handle on any node but the promoted scalars of its own. One node → one template → its own code only.

**ENFORCEMENT (answering "could we actually enforce that?"):** mostly **the COMPILER, structurally** — once
`pBB` is removed from the signature, a template that writes `pBB->anything` or `pBB->α` simply does not
compile. That is far stronger than a grep gate and needs no maintenance. The ONE residual that a compiler
can't catch is `_.node` (because `_` is still in scope and `.node` is a real field): a one-line gate
`scripts/test_gate_template_no_node.sh` greps `BB_templates/*.cpp` for `_.node`/`g_emit.node` and must read
zero. So the rule is enforceable, and the enforcement is: parameter-removal (compiler) + a trivial `_.node`
grep. **COMPLETION TEST:** (a) no `pBB` parameter on any converted box (fn / wrapper / prototype / dispatch
all `void`) — compiler-guaranteed; (b) `test_gate_template_no_node.sh` == 0; (c) the promoted g_emit fields
are set at the single dispatch point from `nd->FIELD` only (never a neighbor); (d) this FACT RULE body is
byte-identical across the five GOAL-*-BB files once folded in.

---

## WORKED EXEMPLARS (copy these)

- **Conformant boxes (this session), all `pBB`-free end-to-end (fn/wrapper/prototype/dispatch all `void`):**
  `bb_pat_rem`, `bb_pat_len`, `bb_pat_any`, `bb_pat_notany`, and `bb_lit` (migrated off `_.node`). Every arm
  reads `_` only (`_.op_sval`/`_.op_ival`/`_.nid`/`_.sid`); zero `pBB`, zero `_.node` in code AND comments.

## RULE CLASS — NORMAL RULES vs FACT RULES, AND WHAT IS ACTUALLY ENFORCEABLE

A **FACT RULE** in this repo earns the name by having a mechanical **COMPLETION TEST** (a grep/gate that
verifies it) and being kept byte-identical across the GOAL-*-BB files. A **normal rule** is a convention
recorded in prose; it is followed by discipline, not checked by a script.

- **R1–R13 are NORMAL RULES.** "One return per platform," "all variance inline," "string concatenation only,"
  "TEXT-first," "go fast / no safety net" are style/process conventions. They are NOT cleanly gateable (a grep
  can't tell good `IF(...)` folding from bad), so making them FACT RULES would buy a maintenance burden
  (byte-identical-×5 + a flaky gate) with no real teeth. Keep them as prose rules in the goal file.
- **The "reads only `_`; no `pBB`; no neighbor" rule IS a good FACT RULE** — precisely because it is
  enforceable, and mostly **structurally** (the compiler), which is the strongest kind. Removing the
  parameter is the trick: with no `pBB` in scope the prohibited code does not compile, so the rule enforces
  itself with zero gate maintenance. Only the `_.node` back-door needs a one-line grep gate.

So the honest answer to "could we properly enforce that? seems hard": the *style* rules are hard to enforce
and should stay normal rules; the *no-neighbor* rule is easy to enforce and is worth promoting to a FACT
RULE — and it's already 90%-enforced by the compiler the moment `pBB` is gone (done, this session).

## RESOLVED (LANDED 2026-06-02, SCRIP `30e8422`) — INTERNAL LABELS + ζ-FRAME SCRATCH

**INTERNAL LABELS — DONE, use it; do NOT reinvent it.** R9's records now also encode box-local labels:
`D <id>` / `J <id>` with `id ≥ X86_INTERNAL_BASE (4)` are box-local (ports stay `0..3`). The `bb_emit_x86`
walker maps each `id ≥ 4` to a fresh per-box `bb_label_t` and resolves forward+backward refs via the EXISTING
`bb_label_define` / `bb_emit_patch_rel32` patch list — no new patch machinery. Front-end:
  - `x86("def", L(n))` defines internal label n; `x86("jmp", L(n))` / `x86("jcc-mnem", L(n))` jump to it.
  - A LOOPING box's extern calls `x86_begin()` BEFORE building the string (sets the per-box uid used for the
    TEXT label name `.Lx<uid>_<n>`; no-op in BINARY).
**ζ-FRAME SCRATCH — DONE.** Box-local RW state lives in the ζ-frame `[r12+off]`, register-relative so
BINARY==TEXT (PER-BOX LOCAL STORAGE / NO-VALUE-STACK; never `movabs` a process addr, never rip-rel `.data`):
  - claim with `int off = bb_slot_claim(N);` in the extern (declare `int bb_slot_claim(int);` locally), stash in
    `_.x86_scratch_off`; access with `FR(off)`: `x86("mov", FR(off), imm)`, `x86("mov", FR(off), reg)` (store),
    `x86("mov", reg, FR(off))` (load), `x86("add", FR(off), imm)`, `x86("add", reg, FR(off))`.
**REFERENCE CONVERSION = `bb_pat_span.cpp`** (the first looping box; loop=`L(0)`, done=`L(1)`, z/zo in the
ζ-frame, β give-back). Loop-free reference = `bb_pat_pos.cpp`. Full recipe + byte-verify-vs-`as` discipline in
`HANDOFF-2026-06-02-OPUS48-SNOBOL4-BB-TEMPLATE-REVAMP-V3-KEYSTONE-POS-SPAN.md`. **Rebase onto `30e8422` first.**

## RESOLVED (LANDED 2026-06-02, Prolog PL-RV-3) — VARIABLE-LENGTH define/jmp-pair loop

`bb_pat_alt`/`bb_pat_cat`/`bb_match` (and FENCE's pair path) — and the Prolog combinators `bb_conj`/`bb_ite` —
carry a VARIABLE-LENGTH define/jmp-pair loop over `g_emit.xa_bb_emit_pair_{n,define,jmp}`: a runtime-count loop
where each pair OPTIONALLY defines an externally-owned `bb_label_t` glue label and OPTIONALLY emits `jmp` to
one (def-only / jmp-only / def+jmp all occur). All five boxes hand-rolled the byte-identical loop. The idiom is
NOT a `FOR(…) over x86("def"/"jmp", id)` — those bake a FIXED port/internal id into the record, but these
labels are DRIVER-MINTED pointers, not ports. The resolution is a single combinator primitive in `x86_asm.h`:

```cpp
inline std::string x86_pair_loop();   // emits the whole g_emit.xa_bb_emit_pair_* loop
```

It mirrors `x86_jmp`/`x86_deflabel` but, instead of a fixed id, its records carry the PAIR INDEX and the walker
fetches the `bb_label_t*` out of `g_emit` by that index — so no raw pointer rides in the 1-byte-id stream. Two
new `bb_emit_x86` records: **`'E' <idx>`** = define `xa_bb_emit_pair_define[idx]` here (0 bytes); **`'F' <idx>`**
= rel32-patch to `xa_bb_emit_pair_jmp[idx]` (the preceding `'L'` carries the `E9`, exactly like `'J'`). TEXT
emits the same GAS the boxes hand-rolled (`LABEL:\n` ; `" jmp LABEL\n"`), so the primitive is byte-identical to
the loops it replaces in BOTH media. A converted combinator is then just `return x86_pair_loop();` (plus any
leading comment). **Prolog `bb_conj`/`bb_ite` converted (PL-RV-3); SNOBOL4 `bb_pat_cat`/`bb_pat_alt` adopt the
same call when they convert** — they read the same `g_emit` fields, so it serves them directly, no further design.

## `x86_asm.h` VOCABULARY (current — updated `30e8422`)

`x86_mov/cmp/test` (REX.W width-aware) · `x86_add_rr` (`add reg,reg`, 01/r) · `x86_add/x86_sub` (imm8 short-form
when it fits, else imm32) · `x86_cmp_imm` (`cmp reg,imm`: imm8 / eax 0x3D / imm32) · `x86_movsxd` ·
`x86_lea_subj_cursor` (`lea dst,[r13+rcx]`) · `x86_movzx_subj_byte` (`movzx dst,[r13+rcx]`) ·
`x86_store_cursor_mirror` (legacy `[r10]`, dies at REG-RO) · `x86_push/x86_pop` · `x86_movimm` (movabs) ·
`x86_load_ro` · `x86_call_ro` · `x86_jcc/x86_jmp/x86_deflabel` (PORTS) ·
**INTERNAL LABELS:** `x86_begin()` · `L(n)` + `x86("def"/"jmp"/jcc, L(n))` (`x86_jmp_id/x86_jcc_id/x86_deflabel_id`) ·
**ζ-FRAME `[r12+off]`:** `FR(off)` + `x86_frame_mov_imm/_store/_load/_add_imm/_add_to_reg` (`x86_r12_modrm` SIB) ·
**PAIR LOOP:** `x86_pair_loop()` (variable-length `xa_bb_emit_pair_*` define/jmp combinator; records `'E'`/`'F'`) ·
`bb_slot_claim(bytes)` (node-free frame claim). jcc mnemonics: je/jne/jl/jle/jge/jg. Consumer: `bb_emit_x86`.

---

## DIVVY-UP MATERIAL (b.size() ledger — the function-byte-counter sites = the revamp debt)

| Owner | Files (b.size count) |
|-------|----------------------|
| **SNOBOL4** | `bb_pat_cat`(2), `bb_pat_alt`(2), `bb_match`(1) + FENCE-pair path — pair-loop design RESOLVED (`x86_pair_loop()`, Prolog PL-RV-3); convert each to `return …prologue… + x86_pair_loop();` (reads the same `g_emit.xa_bb_emit_pair_*`, no further design). **Loop-free remainder ALL DONE** (`bb_pat_span`/`break`/`pos`/`tab`/`atp`/`arb`/`fence`/`defer`/`abort`/`rem`/`len`/`any`/`notany`/`lit`). |
| **Prolog** | `bb_builtin`(28), `bb_goal`(13), `bb_choice`(6), `bb_disj`(2), `bb_unify`(1), `bb_catch`(1) remaining. DONE: `bb_cut`(PL-RV-1), `bb_arith`(PL-RV-2), `bb_ite`+`bb_conj`(PL-RV-3, via `x86_pair_loop()`). |
| **Icon** | `bb_iterate`(17), `bb_binop_gen`(11), `bb_upto`(6), `bb_to_by`(5), `bb_to`(5), `bb_alt`(5), `bb_seq`(4), `bb_every`(2), `bb_suspend`(2), `bb_succeed`(2), `bb_binop_arith`(1), `bb_unop`(2). |
| **Raku** | `bb_rk_gather` + `bb_nfa` (verify counts). |

Each session converts its own boxes TEXT-first per R1–R13 and helps a neighbor with the loop-free leaves.
The internal-label design (OPEN ITEM) is the shared prerequisite for every looping box across all four.
