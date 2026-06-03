# HANDOFF 2026-06-03 (Opus 4.8) — Prolog-BB: findall mode-4 in-process-pointer trap (root-caused), rung26 stale-note correction, register-allocation writeup

## TL;DR
Investigation session. **No SCRIP / corpus code shipped.** SCRIP HEAD unchanged at `c66723e`
(a peer ICN-GLOBAL-NV commit; the last Prolog-relevant commit is still `bfabff3`). All gates
re-verified green. Three findings, recorded here; two surgical GOAL-PROLOG-BB.md corrections made
(stale rung26 note struck; findall substrate item annotated with the root cause). `.github` only.

**GATE-3: m2 112/112 · m3 112/112 byte-identical · m4 87 / 0 FAIL / 25 EXCISED.** Unchanged baseline.

## Gate state (re-verified, nothing touched)
- GATE-1 smoke: m2 5/5, m3 4/5 (known `unify` smoke-harness artifact, covered by rung suite), m4 5/5.
- GATE-3 rung suite: m2 112/112 · m3 112/112 byte-identical · m4 87/0/25.
- PL-HY-FENCE (`test_gate_bb_one_box.sh`): PASS.
- FACT greps: `seg_byte(SEG_CODE`/`SL_B(` outside templates 0; `g_vstack` 0.

## Finding 1 — rung26_copy_term is ALREADY PASSING in all three modes (stale GOAL note)
The GOAL "Other open work" entry claimed `copy_term(f(X,X),f(A,B))` → `A==B` "should hold but doesn't
in mode-4 (var-identity)." **This is false today.** Verified directly:
`corpus/programs/prolog/rung26_copy_concat_copy_term.pl` (`copy_term(f(X,X),f(A,B)), (A==B -> write(same);write(diff)), nl, copy_term(hello,C), write(C), nl`)
prints `same\nhello` in **m2, m3, AND m4**, and `test_prolog_rung_suite.sh --rung rung26 --mode compile`
reports `PASS rung26_copy_concat_copy_term`. It was fixed by a later landing (most likely PLG-9i
`copy_term-compound` or the `374c2ff` compound-unify work) and the note was never struck. **Struck this
session.**

## Finding 2 — findall in mode-4: the in-process absolute-pointer trap (the real PLG-10/WAM-CP-13 blocker)
**The findall machinery already exists and the mode-3 arm works; only the cross-process boundary defeats
mode-4.** Specifically:
- `bb_builtin_findall.cpp` already carries a **complete mode-3 BINARY arm**: it marshals
  `fs_ptr = (void*)pBB->ival` into `rdi` (`48 BF <imm64>`), `call`s `rt_findall`, tests the boolean,
  and wires `je → ω` / else `→ γ`. The **mode-4 TEXT arm was a stub** (`g_sm_native_unsupported = 1; jmp ω`).
- `rt_findall(void *fs_ptr)` (in `interp/IR_interp.c`) is a complete, self-contained engine: save/clear
  the resolve registers, allocate a **findall accumulator** (`Term **acc = calloc(4096,…)` — NOT a value
  stack; the sanctioned "explicit indexed deferred-frame array"), drive the lowered sub-graph
  `fs->gcfg` to exhaustion via `IR_interp_once`/`IR_interp_resume` copying `tmpl` each solution, build
  the result list, `unify` it with `fs->result`, return 1/0. One pointer in, one int out — a perfect
  `rt_*` call (zero emit-time value-work; NO-DUP-clean).

**What I did (then reverted):** wrote the mode-4 TEXT arm as the sanctioned per-medium twin of the
BINARY arm —
```
hdr + sub rsp,16 ; mov rdi,<fs_ptr imm64> ; call rt_findall@PLT ; add rsp,16
    ; test eax,eax ; je ω ; jmp γ ; <β:> jmp ω
```
— and admitted findall to the mode-4 gate (`pl_rich_node_emittable`, BUILTIN block: `if (!strcmp(fn,"findall")) return nd->ival != 0;`).
**Emission is clean** (verified the `.s`: the box emits exactly the call sequence above and links).
**But the linked binary SEGFAULTS before `rt_findall` even runs its body**, and the root cause is
fundamental, not a wiring bug:

> `fs_ptr` (== `pBB->ival`) is an **absolute pointer to the compile-time `bb_findall_state_t`** — which
> holds the lowered sub-graph `gcfg`, the `tmpl` node, the `result` node, all `IR_t*`/`IR_graph_t*`
> living **in the scrip process's heap at emit time.** Mode-3 `--run` *"builds flat-wired x86 BB blobs
> in a sealed slab and jumps in"* — **in-process** — so that pointer is live and the BINARY arm works.
> Mode-4 `--compile --target=x86` emits a standalone `.s` assembled+linked into a **separate process**,
> where the baked `mov rdi,<imm64>` is a dangling address. `rt_findall`'s first `fs->gcfg` deref faults.

This is precisely why the GOAL scopes findall/catch/aggregate to "needs a real runtime substrate"
(PLG-9g / WAM-CP-13). The mode-3 BINARY arm is **not** a template for mode-4: it only works *because*
mode-3 shares scrip's address space. **Admitting findall to the gate as-is would convert its 5 EXCISED
rungs into segfaults (regression of the tracked m4 count) — so I reverted everything.** A clean EXCISE
beats a crashing false-PASS.

**The same trap blocks catch and aggregates** — `rt_catch(void *zc_ptr)` takes a compile-time
`bb_catch_state_t*` (holding `goal_g`, `catcher`) exactly the same way, and the aggregate/nb_setval
boxes follow the pattern. This is **one substrate problem**, which is why all 25 m4-EXCISED rungs
cluster into {findall ×5, retract ×5, abolish ×5, aggregate ×4, catch/throw ×5, dcg_generate ×1}.

**The real fix (the substrate, future session, needs design sign-off):** the sub-graph and its operand
terms must be **reconstructed at runtime in the target process**, not passed as a baked pointer.
Options sketched: (a) a runtime sub-graph rebuilder fed an emit-time serialization of `gcfg` (mirrors
`emit_build_compound_term`'s relocatable serialization — literal immediates + `[rip+strlabel]`, zero
runtime pointers); (b) emit the sub-graph itself as callable native code and have a runtime
`findall`-driver loop call it (the eventual end-state, no interpreter re-entry); (c) a hybrid that
emits a descriptor table the runtime walks. Cracking this once unlocks ~20 of the 25 EXCISED rungs.
Note (b) is the only option that also satisfies the long-standing "NO SM/BB WALKING AT RUNTIME IN
MODES 3/4" rule without leaning on the Prolog `--run` carve-out — (a)/(c) re-enter `IR_interp_*` and
would need the carve-out widened, which is a Lon call.

## Finding 3 — register allocation: R13/R14/R15 are SNOBOL4's subject model; Prolog uses none of them
Grounding for *why* Prolog's state is global/pointer-passed (Finding 2's root cause) rather than
register-resident. From the code:
- The locked callee-saved layout (RULES "X86-64 REGISTER / SUBJECT-MODEL CONVENTION") is **shared** by
  the three concurrent BB languages, and its canonical origin is the **SNOBOL4 subject scan**:
  **R13 = Σ** (subject BASE ptr, the fixed whole string), **R14 = δ** (CURSOR, the moving scan
  position), **R15 = Δ** (subject LENGTH/END, the fixed bound). Casing carries meaning (UPPER = fixed
  whole/bound, lower = moving position). The SNOBOL4 pattern templates (`bb_pat_*.cpp`) reference them
  **36×** (r13×11, r14×15, r15×10) — every scanner reads Σ and advances δ against Δ.
- **The Prolog mode-4 templates reference r13/r14/r15 ZERO times** (grepped `bb_goal/choice/conj/unify/cut/disj/ite/arith/atom/logicvar`).
  Prolog has no subject string to scan, so the subject triple is meaningless to resolution; Prolog
  leaves R13/R14/R15 untouched and, being callee-saved, preserves them for free → honors the shared ABI
  without using it.
- Prolog keeps only **two** things in registers, set once at box-graph entry (the `xa_flat.cpp` flat
  prologue `push r12 ; mov r12, rdi ; lea r10, [rip + Δ]`): **R12 = ζ** the per-sequence RW frame base
  (for Prolog, the **environment** = logic-var slot array; `rt_frame`/`rt_env_alloc` returns it in rax,
  driver passes in rdi, box parks in r12; every box-local is `[r12+off]`), and **R10** the per-BLOB
  sealed `[rip]`-relative DATA block. Both shared with SNOBOL4/Icon.
- Prolog's genuinely-dynamic WAM state — **trail, choice-point ledger, cut barrier, environment** —
  lives in **global memory** (`g_resolve_trail`, `g_resolve_bfr`, `g_resolve_env`, `g_resolve_cut_*`)
  reached via `call rt_*@PLT`, NOT in dedicated registers. Hence the Prolog box idiom is
  "marshal args → `call rt_*@PLT` → wire α/β/γ/ω" — value/state work in the runtime, ports in the box.

**Design logic:** the register table is a superset reserved for the most register-hungry consumer
(string scanning). SNOBOL4/Icon, scan-driven, bind the subject triple and keep the hot cursor in a
register. Prolog, resolution-driven (WAM), has a different hot path (unify/trail/backtrack), keeps that
state in globals behind `rt_*` calls, and spends only R12+R10. This is exactly why findall/catch can't
cross the mode-4 process boundary by passing a register/immediate: Prolog's state is global +
runtime-reconstructed, not carried in emitted-code-controlled registers.

**Forward note (not actioned):** the R13/R14/R15 reservation means a future Prolog **string-scanning
builtin** (`sub_atom/5`, backtracking `atom_concat/3`, DCG over a code list) *could* legitimately adopt
the Σ/δ/Δ subject model — scanning an atom's char buffer is exactly what that triple is for. That would
be the one place Prolog and SNOBOL4 converge on the same registers for the same reason.

## Files changed this session
- **`.github/GOAL-PROLOG-BB.md`** — (1) struck the stale rung26_copy_term "Other open work" entry
  (now PASSING in all 3 modes); (2) annotated the findall/PLG-9g/WAM-CP-13 scope with the in-process
  absolute-pointer root cause + the substrate-fix options. No watermark numbers changed (no code moved).
- **`.github/` (this handoff).**
- **No SCRIP, no corpus.** (Discarded incidental `.s` regen churn in `corpus/programs/prolog/*.s` —
  those are test-runner byproducts and additionally carry pre-existing peer emitter drift; not this
  session's to commit.)

## Recommended next steps
1. **findall/catch substrate (PLG-10 / WAM-CP-13)** — the real unlock for ~20 EXCISED rungs. Needs Lon's
   design sign-off on which option (a/b/c above); (b) — emit the sub-graph as callable native code — is
   the cleanest w.r.t. the no-runtime-walking rule. Degenerate first rung: `findall(X, fail, Xs)` → `[]`.
2. **WAM-CP-9 ITE-commit semantics** — still open, still needs sign-off (m2-oracle-WRONG case
   `( a(X),X>=2 -> true ; X=0 )`; risks 112/112 byte-identity). Untouched this session.
3. Strike the rung26 note is done; a broader stale-note sweep of "Other open work" may find more (the
   note set predates the m4 75→87 climb).

## Canonical sources consulted (uploaded zips)
- gprolog `4-gprolog-master.zip` → `src/EnginePl/unify.c` (deref/bind/TAG_STC_MASK), `src/Pl2Wam/syn_sugar.pl`
  (`normalize_cuts1`).
- swipl `5-swipl-devel-master.zip` → `src/pl-comp.c` `compileBody` ~2300–2420 (ITE local-cut).
- (Both re-read for grounding; neither drove a code change this session.)
