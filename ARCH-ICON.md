# ARCH-ICON.md — Icon Frontend and BB Execution

Frontend: Icon. Produces shared IR (tree_t* via icon_parse). See ARCH-IR.md.

---

## Execution model

Icon is a goal-directed language. Every expression either:
- **Succeeds** (gamma port) — produces a value, may produce more on resume
- **Fails** (omega port) — produces no value, terminates generator

This is exactly the Byrd Box four-port model: alpha (start), beta (resume),
gamma (succeed), omega (fail). Icon IS a Byrd Box graph. Every construct is
a box. The broker pumps it (BB_PUMP mode).

**Key distinction from SNOBOL4:** SNOBOL4 uses BB_SCAN (try each cursor
position). Icon uses BB_PUMP (generate all values until omega).

**STACKLESS (foundational, GROUND ZERO 3, 2026-05-30).** An Icon program emits
ZERO SM opcodes and uses NO value stack — no SM value stack, no `r12` TOS, no
`rt_push_*`/`rt_pop_*`. Every box's value lives in a **flat per-box DATA slot**
(`&pBB->value` / `&pBB->counter` / `&pBB->state`); a consumer reads its operand
boxes' slots directly (operands known at emit time via α/β), exactly as Proebsting
specifies (`plus.value ← E1.value + E2.value`). Unbounded-depth backtrack state
(ARBNO, recursion) lives in a **per-box .bss arena** indexed by depth — never a
global stack. Inter-box transitions are direct `jmp`. The reference embodiment is
`SCRIP/refs/bb/test_icon.c` (and the archived stackless emitter
`SCRIP/archive/backend/emit_emitters/emit_x64.c`, which benchmarked faster than
SPITBOL because there is no stack). The prior mode-3 build that introduced an SM
value stack is SUPERSEDED — see `GOAL-ICON-BB.md` → "GROUND ZERO 3".

**Relational ops are NOT booleans (foundational).** A comparison is a
zero-or-one-result generator: it succeeds (yields a value → γ) or fails
(→ ω). Verified across both references: canonical Icon
`operator{0,1} <= cmplte(x,y)` → `return y` / `fail` (`ocomp.r`); JCON
`ir_opfn(<=, args, failLabel)` routes failure to `failLabel`. The
construct (`if`/`while`/`until`/`case`) only chooses where the γ/ω edges
go; the comparison needs no per-construct boolean test. SCRIP historically
reified a `LAST_OK` flag + a `BB_IF` router instead — see
`STUDY-JCON-ICON-CONTROL-FLOW-2026-05-29-OPUS48.md` for the full three-way
comparison and the IBB-9-2 / IBB-9-RELOP-PORTS plan derived from it.

---

## Variable model — frame slots (OLD) and shared NV dictionary (NEW), side by side (Lon directive, 2026-06-03)

Icon variable *references* resolve through one of two backends. **Both are kept side by side, selected by a command-line switch** — the OLD path already exists and is proven, and the NEW path is being added at the SAME call sites (`IR_VAR` read, `IR_ASSIGN` write), so a switch is a cheap refactor rather than a rewrite. See `GOAL-ICN-GLOBAL-NV.md` for the rung ladder (GN-1…GN-FENCE) and the switch's exact name/default.

- **OLD — per-procedure frame slots (`g_bb_varslot` / `bb_varslot_peek`).** A global gets an integer frame slot, addressed `[r12+off]` in the one-register frame. This is the model inherited from `icont`'s integer-index symbol resolution. It is local-optimal (a register-relative load, no hashing) but the namespace is per-graph: a global written by an Icon box is NOT visible to a SNOBOL4/Snocone/Rebus box, because those resolve names through the NV dictionary, not Icon frame slots.

- **NEW — shared NV dictionary (`NV_GET_fn` / `NV_SET_fn`), EXACTLY like SNOBOL4.** An Icon global becomes a name-keyed lookup in the SAME hash dictionary (`_var_buckets[_var_hash(name)]`, core.c) that SNOBOL4/Snocone/Rebus already use for every variable. **This makes Icon globals share the one variable namespace with all those languages** — a global set by an Icon BB is read by a SNOBOL4 BB through the same `bb_var_global` / `NV_GET_fn` path, with zero dispatch and zero extra machinery (the four ports + DESCR_t are the universal protocol). Locals (procedure params + `local`/`static`) stay frame slots in BOTH modes — only the GLOBAL arm of `IR_VAR`/`IR_ASSIGN` is rerouted.

**Why keep both (the directive's intent):** (1) **Performance measurement** — we want the head-to-head cost of frame-slot globals (OLD) vs NV-dictionary globals (NEW): a `[r12+off]` load/store vs a hash lookup + chain walk. The switch lets the SAME corpus run both ways for a clean A/B. (2) **Independent-Icon compilation** — when Icon is compiled standalone (not in a polyglot mix that needs cross-language sharing), the OLD frame-slot model may stay available as a faster, self-contained option; the NEW shared-dictionary model is for the cross-language case. The end state is therefore BOTH backends retained, switch-selected, not OLD-deleted-for-NEW.

(Mode-2 interpreter note deleted 2026-07-01 — mode 2 no longer exists.)

---

## String scanning — the ICN-SCAN BB family (Lon directive, 2026-06-03)

**Every string-scanning operation Icon offers is its own stackless BB.** The canonical set is closed —
`refs/icon-master/src/runtime/fstranl.r`: `any` `bal` `find` `many` `match` `upto`; `fscan.r`: `move` `pos`
`tab`; plus the control forms `?` (scan env, LIVE — `bb_gen_scan.cpp` + `bb_keyword.cpp`, SCRIP `d46b943`),
`?:=` (scan-assign) and `=s` (sugar, `tab(match(s))`, a lowerer rewrite — no box). Rung ladder with ONE STEP
PER BOX: **GOAL-ICON-BB.md → "ICN-SCAN LADDER"** (ICN-SCAN-0 … ICN-SCAN-FENCE).

**Register contract (CORRECTED 2026-07-18, verified vs live `x86_asm.h` + `zeta_choices.h` — the prior
2026-06-30 table said R12=ζ and RBX=GVA base; BOTH are superseded):** ζ frame selection is the `ZC_FRAME`
BUILD CONSTANT (`src/contracts/zeta_choices.h`), **default `ZC_FRAME_RSP` since s65 R12-ERAD**. Under it:
`x86_zr()` = **RSP** (control-flow-lifetime ζ rides the machine stack — FORTH port cells + carve
discipline, shared with the C call stack) and `x86_fb()` = **RBP** (the ζ value-slot frame base, seeded at
every activation boundary; all `FR`/`FRQ` spellings resolve `[rbp+off]`, no depth compensation — REG-7 U3,
sealed U5 s87). **R12 is FREE** (residuals: the six-register coexpr save in `bb_create.cpp` covers it
regardless; the `ZC_FRAME_R12` accessor arm survives as compile-time-selectable history only). Subject
registers unchanged: **R13=Σ subject base · R14=δ cursor (0-based; `&pos = δ+1`) · R15=Δ subject length**
(live in `bb_gen_scan.cpp`'s scan-env swap). RO constants sealed `[rip+disp]`; the membership test is the
`bb_pat_any.cpp` idiom. Result DESCRs go to the box's own 16-byte frame slot; consumers read the
producer's slot.

⛔ **RBX (CORRECTED 2026-07-18, supersedes the 2026-06-30 note):** the GVA-base role is RETIRED — globals
now address ABSOLUTE, `bb_assign_global`'s `ABSQ(RT_GVA_VA + gva_k*16)`, no register base. **RBX is
reserved as the WS/GC bump-frontier TOP**: the `ZC_PORT_HEAP` α-carve emits `mov rax,rbx; add rbx,K;
cmp rbx,[RT_WS_LIMIT]; ja <refill>` (x86_asm.h ~1620, HZ-1). The build default is `ZC_PORT_FORTH`
(grants spend as `sub rsp,K`), so the rbx allocator is the HEAP arm's ratified contract, dormant under
FORTH — plus three named inert rbx-dance holdouts (`bb_gvar_assign_concat`, `bb_pattern_break/len`,
`bb_ref_invariant`). RBP is the ζ frame base under the RSP default (see the corrected contract above);
`NV_GET_fn`/`NV_SET_fn` remain plain C calls.

**Two semantic families (fstranl.r function signatures — do not blur):**
- **Position-returners, δ untouched:** `any`/`match`/`many` are `function{0,1}` (one result or fail);
  `upto`/`find`/`bal` are `function{*}` GENERATORS (suspend each position; β re-pumps via the generator-β
  chain edge, the `bb_to` mechanism). None of these moves `&pos`.
- **Cursor-movers, REVERSED on resume:** `tab`/`move` (`function{0,1+}`, fscan.r) write δ and restore the
  saved δ on β then fail. `pos` is a stateless `{0,1}` compare. Only tab/move ever write δ — `tab(upto(c))`
  is the composition idiom and reads upto's slot like any consumer.

This is genuinely DIFFERENT from SNOBOL4 pattern matching (checked against canonical sources 2026-06-03 — see
GOAL-ICON-BB Watermark): SNOBOL pattern leaves thread the cursor; Icon scan functions return position VALUES.
Reuse = the Σ/δ/Δ register walk + the cset test loop; the value contract and the `{*}` re-pump are Icon's own.

---

## Box structure for Icon constructs (from .github/test_icon.c)

  construct_alpha:  initialize state; compute first value; goto gamma or omega
  construct_beta:   advance state; compute next value; goto gamma or omega
  construct_gamma:  value ready — wire to caller's success label
  construct_omega:  exhausted — wire to caller's fail label

Three-column form: LABEL / ACTION / GOTO. Exactly as in test_icon.c.
State (cur, lo, hi, index, etc.) lives in the DATA block (zeta struct),
allocated fresh per alpha-entry. CODE is shared.

---

## JCON reference

`refs/jcon-master/tran/irgen.icn` — 43 `ir_a_*` procedures, one per Icon AST construct. `ir_info(start, resume, failure, success)` = the four-port record. Ground truth for every construct's port topology.

---

## Co-expressions and TT_SUSPEND

**LANDED 2026-07-01 (GOAL-IR-IMMUTABLE-EMIT RUNGs 1-5):** `create`/`@`/coret/cofail via the pthread+semaphore model in `src/runtime/rt/rt_coexpr.c` + `bb_create/bb_activate/bb_coret/bb_cofail` templates, end-to-end both modes. (The former ucontext `coro_runtime.c` framing is superseded.) Still banned: implementing Byrd constructs as `DESCR_t foo(void *zeta, int entry)` C functions.

---

