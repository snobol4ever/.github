# ARCH-LANGUAGES.md — the seven frontends, one file

**Consolidated 2026-08-27 by `hq_C`** from eight files, under the method in `arch-consolidate-engine`'s LINKS: truth-check every checkable claim in BOTH directions, move-not-rewrite true content, correct false content citing its FINDING, resolve RETIRED NAMES, sweep references.

⛔ **This file is FRONTEND/LANGUAGE truth only.** The shared engine, the register contract, the zeta taxonomy and the x86 substrate live in `ARCH-ENGINE.md` and `RULES.md`. Where a language section used to restate engine law, it now points instead — that restatement is exactly how the eight files drifted apart from each other.

⭐ **Why one file, stated once so it is not re-litigated.** The eight sources disagreed *with each other* about live code, not merely with the tree. Measured during this consolidation: `ARCH-PROLOG.md` said the `bb_node_state_t` snapshot/restore mechanism "is being removed", while the 2026-08-27 CEO audit of `ARCH-x86.md` listed `bb_snapshot_state`/`bb_restore_state` under "verified correct". Both readings were defensible in isolation and the code is unchanged: `emit.h:179,237-238` and `rt_runtime.c:465` are live today. A reader could obey either file and be misinformed by the other.

---

## RETIRED NAMES

Everything a reader might arrive with, and where it went. ⛔ Entries here are **resolutions, not deletions** — a name is listed because something still cites it.

| retired name / path | resolution | evidence |
|---|---|---|
| `ARCH-SNOBOL4.md` · `ARCH-SN4-CONSTANTS.md` · `ARCH-ICON.md` · `ARCH-PROLOG.md` · `ARCH-PROLOG-DESCR-ZETAS-hq_C.md` · `ARCH-SNOCONE.md` · `ARCH-REBUS.md` · `ARCH-C.md` | **this file** | consolidated 2026-08-27 |
| `src/runtime/interp/pl_runtime.{c,h}` | **gone from the tree.** `pl_choice` now lives in `src/lower/lower_prolog.c` — the choice-point mechanism moved into the lowerer | verified: no `pl_runtime.*` under `SCRIP/`; `grep -rl pl_choice src/` → `src/lower/lower_prolog.c` |
| `SCRIP/archive/frontend/prolog/prolog_emit.c` | **not in this root** — lives at `one4all/archive/frontend/prolog/prolog_emit.c` (ceo's root) | matches the 2026-08-27 CEO x86/Prolog audit |
| `SCRIP/doc/PROLOG-FEATURE-COMPARISON-2026-05-29-SONNET.md` | **`SCRIP/docs/`** — one-letter path error, the file is present | `ls SCRIP/docs/` |
| `GOAL-PROLOG-BB.md` | **`GOAL-PROLOG-100.md`** (one GOAL file per language) | `ls .github/GOAL-PROLOG*` |
| `x86_r12_modrm` | **`x86_frame_modrm`** | zero hits for the old name; new name live in `src/templates/x86/x86_asm.h` |
| `ZC_FRAME_R12` accessor arm | **genuinely deleted.** Its only two survivors are comments *documenting* the deletion (`rtx_match.S:863`, `rtx_abi.inc:17`) | ⭐ checked because a raw grep count reads as "still present" — it is not |
| flat `src/templates/*.cpp` | **re-gridded** into `bb/` (137) · `x86/` (2) · `xa/` (19); zero top-level `.cpp` | ⚠️ the 2026-08-27 CEO x86/Prolog audit's own context line says "no `xa/` subdir" — that line went stale within hours of being written; the ICON audit is the correct one |
| `src/machine/` | **does not exist** | ⛔ still named in per-root `CLAUDE.md` digests, which are untracked and cannot be updated by a commit here |
| `corpus/programs/snobol4/demo/beauty_c/` | **absent** — no `beauty_c` directory exists anywhere in `corpus/`. Live relatives: `corpus/demo/snobol4/beauty`, `corpus/tests/snobol4/beauty_suite`, `corpus/tests/snobol4/smoke/beauty_compiled.sno` | ⚠️ and `corpus/programs/` is ruled non-test material entirely (Lon 2026-08-27, `RULES.md:55`) |

---

## REBUS

Frontend: REBUS → shared IR (`EXPR_t`/`STMT_t`). See `ARCH-ENGINE.md`.

*(Absorbed whole from `ARCH-REBUS.md`, which was three lines and carried no checkable claim beyond the IR types and the cross-reference — both verified.)*

## C backend

Backend: C source output. **Status: inactive** — `scrip-cc` fails on `word*`/`pat_alt_commit`. Not maintained; no active goals.

*(Absorbed whole from `ARCH-C.md`. ⚠️ Status is carried forward as written and was NOT re-measured — the row's method requires truth-checks on live mechanisms, and an explicitly-inactive backend has none. Anyone reviving it re-derives the failure first.)*

---

## ICON

Frontend: Icon → shared IR. See `ARCH-ENGINE.md`.

### Execution model — MOVED UNCHANGED (verified)
Icon is goal-directed: every expression **Succeeds** (γ, may resume for more) or **Fails** (ω). That IS the Byrd-box four-port model — **α** proceed · **β** recede · **γ** succeed · **ω** concede. Icon uses `BB_PUMP` (generate until ω); SNOBOL4 uses `BB_SCAN` (try each cursor position).

**NO SOFTWARE VALUE STACK** (GROUND ZERO 3; renamed from "STACKLESS" — that name is VOID per Lon 2026-08-27, `RULES.md`: all three zetas ARE on the stack, and Icon walks the ladder RSP spine → RBP activation frame → root, with γ-SUSPEND-capable graphs keeping ζ in an RBP activation frame). Icon emits **zero** SM opcodes, no software value stack, no r12-TOS, no `rt_push`/`rt_pop`. Each box's value lives in a flat per-box DATA slot; consumers read operand boxes' slots directly (Proebsting: `plus.value ← E1.value + E2.value`). Inter-box transitions are direct `jmp`. Reference embodiment: `corpus/probe/bb/test_icon.c`.
✅ *Spot-checked (RULING-vs-CODE): `grep -c 'SM_' src/lower/lower_icon.c` → **0**. The zero-SM-opcodes ruling holds.*

⛔ **One clause CORRECTED, not moved:** the old text said unbounded backtrack state (ARBNO, recursion) is a *"per-box `.bss` arena by depth"*. That is **wrong twice**, per the 2026-08-27 CEO ICON audit: the state is the **stack-carved** `jcon_value_region` / `zls_g_region()`, folded into `flat_frame_bytes` (`emit.cpp:3308/3414`).

**Relational ops are NOT booleans** — a comparison is a `{0,1}` generator: γ yields a value, ω fails; constructs only choose where γ/ω go (verified against canonical `ocomp.r` and JCON `ir_opfn`).

### Variable model (Lon 2026-06-03) — two backends, switch-selected, BOTH kept
- **OLD** per-procedure frame slots (`g_bb_varslot`) — fast, per-graph namespace.
- **NEW** shared NV dictionary (`NV_GET_fn`/`NV_SET_fn`, the same hash dict as SNOBOL4/Snocone/Rebus) — one cross-language global namespace. Only the GLOBAL arm of `IR_VAR`/`IR_ASSIGN` reroutes; locals stay frame slots. Kept side by side for A/B perf and standalone-Icon compilation. Ladder: `GOAL-ICON-100.md` (GVA superseded NV for native globals; NV remains the reflective/cross-language binding).

### ⛔⛔ REGISTER CONTRACT — REMOVED FROM THIS FILE, NOT MOVED
`ARCH-ICON.md` carried what it called *"the LIVE REGISTER CONTRACT that every BB template (all languages) obeys"* — the file's own stated reason for existing. **It was wrong in five load-bearing specifics** and is not reproduced here. Authority: `FINDING-2026-08-27-ceo-arch-audit-icon-pair-major-drift-register-contract-names-a-frame-base-that-is-not-there.md` and `FINDING-2026-08-27-hq_P-arch-icon-register-contract-describes-a-selector-that-was-eradicated.md`.

**LIES GET CONSEQUENCES — what this one cost, and would have kept costing:** the section taught `emit_jmp_pin_rbp()` (no such symbol — the live pair is `emit_jmp_pin_legacy()`/`emit_rec_pin()`), a per-graph RBP/RSP duality via `x86_fb()` (unconditionally `"rsp"`), and `x86_fb_pinned()` as the selector (a compile-time **constant zero**). ⛔ **A template author obeying it literally emits against a frame base that is not there.** hq_P found it by *complying* with Lon's read-the-ARCH-docs order before starting rung N-2 — the order paid for itself on first use, and the doc it validated against was the thing that was wrong.
✅ **The register contract is ENGINE law, not Icon law.** It belongs in `ARCH-ENGINE.md` / `RULES.md` § BB FRAME-PLACEMENT CRITERION, and having it live in a *language* file is precisely how it drifted unnoticed: nobody auditing the engine looked in the Icon doc.

### String scanning — the ICN-SCAN BB family (verified section, moved untouched)
Canonical set closed: `fstranl.r` any/bal/find/many/match/upto · `fscan.r` move/pos/tab · control `?` live, `?:=`, `=s` sugar.
Two semantic families, **do not blur them**: *position-returners*, δ-untouched — `any`/`match`/`many` are `{0,1}`; `upto`/`find`/`bal` are `{*}` generators (suspend each position, β re-pumps via `bb_to`). *Cursor-movers*, reversed-on-resume — `tab`/`move` write δ and restore the saved δ on β then fail; `pos` is a stateless compare. Genuinely different from SNOBOL4 pattern leaves (which thread the cursor); the reuse is the Σ/δ/Δ walk plus the cset test loop.

### Box structure (from `corpus/probe/bb/test_icon.c`, verified present)
```
construct_α: init state; first value; goto γ or ω
construct_β: advance;    next value; goto γ or ω
construct_γ: value ready — wire to caller success
construct_ω: exhausted   — wire to caller fail
```
State lives in the per-α DATA block; CODE is shared.

### JCON reference
`refs/jcon-master/tran/irgen.icn` — 43 `ir_a_*` procedures; `ir_info(start,resume,failure,success)` is the four-port record. Ground truth for every construct's port topology. ⚠️ `SCRIP/refs/` is gitignored and not auto-created — `ls` it before trusting a grep.

### Co-expressions
**LANDED 2026-07-01**, both modes: `create` / `@` / `coret` / `cofail` via pthread + semaphore. C-function Byrd constructs remain banned.
✅ *Spot-checked: `src/runtime/rt/rt_coexpr.c` present, and all four of `bb_create` / `bb_activate` / `bb_coret` / `bb_cofail` present under `src/templates/bb/`.*

---

## PROLOG

Frontend: PROLOG → shared IR (`EXPR_t`/`STMT_t`). See `ARCH-ENGINE.md`.

### Four-port is the model — NOT a value stack (2026-05-30 correction, moved)
The older framing leaned on GNU Prolog's WAM CP-frame **stack** (`pl_choice`, ported from `wam_inst.h`) as the engine compass. **That was wrong.** The model is Proebsting's four-port translation: each operator is four labelled code chunks (**α/β/γ/ω**) threaded by `goto`, each box's value in a FLAT per-activation home — not a pushed/popped value stack, and not a save/restore of shared mutable node slots.

**What survives, and is therefore NOT the value stack:** the **trail** (binding undo log); the **resume cursor / CP ledger** (`_cs` int / parent-linked `pl_choice` record — the irreducible "which suspended alternative is live"); and **explicit indexed deferred-frame arrays** for genuinely repeating constructs (ARBNO-style `_1[64]`).

⛔ **CLAIM CORRECTED — the removal announced here never happened.** The old text said *"the `bb_node_state_t` snapshot/restore mechanism in the current engine IS a value stack and **is being removed**"*. Measured 2026-08-27, ~3 months later: it is **fully live** — `emit.h:179` (the typedef), `emit.h:237-238` (`bb_snapshot_state`/`bb_restore_state`), `rt_runtime.c:465` (inside `PlCallSt`). **LIES GET CONSEQUENCES:** the 2026-08-27 CEO audit of `ARCH-x86.md` independently listed those same two symbols under *"verified correct"*. So the fleet held two ARCH docs that described the same live code as, respectively, being-removed and verified-correct — and a reader could obey either and be misinformed by the other. That is the single clearest argument for this consolidation.

### Engine model (substrate facts — moved, with citations repaired)
A **boxed-cell, GC-managed** model (tagged `Term*`, GC-allocated). The choice-point ledger is a parent-linked record — not a contiguous WAM stack, and not a value stack.
- **Terms** — `src/frontend/prolog/term.h` *(was `src/parser/prolog/`; renamed 2026-08-24, `cf1f2961`)*: tagged `Term*` (ATOM/VAR/COMPOUND/INT/FLOAT/REF), GC-allocated. Bound vars become `TERM_REF` with a `ref` pointer; `term_deref` chases the chain (≡ SWI `deRef`).
- **Unify + trail** — `src/frontend/prolog/prolog_unify.c`: structural unify; `bind()` records the var on a GC-doubling trail; `trail_unwind(mark)` restores vars to `TERM_VAR` on backtrack.
- **Choice points** — ⛔ the old citation `src/runtime/interp/pl_runtime.{c,h}` **no longer exists**. `pl_choice` now lives in `src/lower/lower_prolog.c`: the CP mechanism moved into the lowerer. Mapping to gprolog's WAM CP frame is unchanged: `parent≡BB`, `trail_mark≡TRB`, `env≡EB`, `resume≡ALTB`, `saved_args≡AB`, `stamp` ≈ HB stand-in; HB/CPB/BCIB/CSB deferred.
- **Cut** — `g_pl_cut_barrier` + `pl_cp_truncate` ≡ gprolog `Assign_B(BB(B))`.
- Per-invariant reference: `SCRIP/docs/PROLOG-FEATURE-COMPARISON-2026-05-29-SONNET.md` *(the docs said `SCRIP/doc/` — one letter, and the file is present)*.

### Byrd-box refinements (moved; one verified)
- **Callee resumability is a CLOSURE VALUE, not a port.** Entering a predicate is a `call` yielding `(value, Resume)`; re-driving it is `closure.Resume()` dispatched from the caller's OWN β chunk. In SCRIP the closure IS the callee's `rt_enter` frame. There is no caller-side "callee-entry/resume port": the ports once emitted as `δ`/`ε` (`X86P_DELTA`/`X86P_EPSILON`, ports 4/5) are **ABOLISHED**.
  ✅ *Spot-checked (RULING-vs-CODE): zero occurrences of either symbol under `src/`. The abolition genuinely landed and stayed.*
- **Determinacy is first-class (`bounded`).** A box that cannot offer a second solution emits NO β chunk, allocates no choice point, retains no closure. β exists only for genuine generators (multi-clause predicates, `retract`, member-style recursion, `between`, findall's inner goal). Assigned at lower time.
- **The boxes ARE the engine.** No central choice-point-stack interpreter loop, no bytecode fetch-decode-execute, no C control engine / `rt_meta_solve` meta-rail. Backtracking is the ω/β wiring plus the one shared trail plus per-callee closures. `pl_choice` remains the CP-ledger RECORD but no longer an engine that DRIVES control.
- **catch/throw**: catcher tried on a scratch trail before commit (correct ISO discipline).

### Known parity gaps vs gprolog/SWI (moved)
1. **Conditional trailing.** Both references trail a binding only when the var is older than the youngest live CP (gprolog `Word_Needs_Trailing`, `wam_inst.h:472`; SWI `GTrail`, `pl-incl.h:2194`). SCRIP trails unconditionally → rung family **PL-TRAIL-COND**. This is also the de-facto **HB** port — the one deferred CP-frame field with a real consumer.
2. **Level-2 indexing.** WAM-CP-8 gives Level-1 first-arg indexing with an O(N) linear filter scan; gprolog Level 2 (`indexing.pl`) and SWI (`pl-index.c` Fibonacci hash) select in O(1) → rung family **PL-INDEX-L2**.

Ladder home: **`GOAL-PROLOG-100.md`** *(the docs said `GOAL-PROLOG-BB.md`, which does not exist — one GOAL file per language)*.

### Prolog on `DESCR` + the three zetas — Lon's s273 ruling (design, absorbed with corrections)
**Ruling (Lon s273, verbatim in substance):** *Prolog should not use `Term` at all, it should be using `DESCR`… Any allocations better live on (1) the SPINE, (2) the ACTIVATION FRAME, (3) the STANDING (ROOT) ACTIVATION FRAME — IN THAT ORDER… We use GC Heap! NO MALLOC!*

**The one sentence:** a Prolog term is a `DESCR_t`; a logic variable is a `DESCR_t` slot whose address is its identity; a compound is a `DESCR_t` pointing at a contiguous run of `DESCR_t`; all three live on a zeta chosen by lifetime, in Lon's order — and nothing but string bytes reaches the GC heap.

⛔⛔ **TWO CORRECTIONS TO THIS SECTION, BOTH AGAINST ITS OWN AUTHOR (hq_C, s273). Re-measured 2026-08-27:**

| the doc's number (s273) | measured now | |
|---|---|---|
| 448 `Term` references | **233** | ↓ 48% |
| 27 `malloc(` in the Prolog frontend | **11** | ↓ 59% |
| 23 `malloc`/`free` in `prolog_parse.c` | **4** | ↓ 83% |

Substantial cleanup landed between s273 and now, so the doc's *"the worst of any area"* framing should not be quoted as current. ⭐ Per `RULES.md:105`, the numbers were replaced rather than re-pinned: **re-measure before citing.**

⛔ **AND THE SECTION'S RHETORICAL CENTREPIECE IS FALSE.** It called `rt_jmp_frame_lexprep2` *"a **no-op** called from every 2+-clause predicate's prologue… frame machinery SNOBOL4 and Icon never needed"*, and argued *"fix the representation and the plumbing stops being necessary."* Measured at `src/runtime/rt/rt.c:1653`, the function:
1. `memset(fb, 0, region_bytes)` — zeroes the frame region; and
2. restores the pending **cursor / trail-mark** triple for a suspended activation.

Its own comment states the stakes: *"A freshly zeroed frame reads as 'never suspended', so a resumed call would silently re-run clause 1 instead of jumping to the retained cursor."* **It is load-bearing for resume correctness, not dead plumbing.** It is also not Prolog-bespoke: `rtx_icngen.S:84` documents Icon generators depending on state *"set by `rt_jmp_frame_lexprep2` at the generator's α prologue"*, and it appears in emitted **Pascal** prologues (observed 2026-08-27 in `nested.pas`).
✅ **The DESCR ruling itself is Lon's and stands untouched.** What is struck is one piece of *evidence* offered for it. ⭐ The lesson is the one this consolidation keeps finding: a doc that names a mechanism "a no-op" without a witness invites the next hand to delete it — and here that deletion would silently re-run clause 1 of every resumed predicate, which is a wrong answer, not a crash.

---

## SNOBOL4 — user-declared `&` constants (Lon's Eurekas 1–3, 2026-08-19)

**Status home:** rung STATE lives in `GOAL-SNOBOL4-100.md` § SN4-CONSTANTS; this section is the design of record it points at.

⭐ **This section verified unusually well.** Every load-bearing mechanism was spot-checked against live code and **all of it holds**, including both error codes with their exact wording. Recorded because the method's value is not only in catching drift — a section that survives a both-directions check should be usable without re-deriving it.

### The three-tier `&` namespace (resolution order)
1. **Protected keywords** — already constants (`&ALPHABET &ARB &BAL &FENCE &ABORT &FAIL &REM &SUCCEED &UCASE &LCASE &STCOUNT &STNO …`), untouched.
2. **The closed unprotected list** — true keyword VARIABLES (`&ANCHOR &TRIM &STLIMIT &MAXLNGTH &FULLSCAN &DUMP &ERRLIMIT &CODE &CASE &FTRACE &TRACE &ABEND &COMPARE &PROFILE &ERRTEXT &ERRTYPE`), assignable per manual ch.16.
3. **Every other `&name` = USER CONSTANT** — one-time assignment, sealed forever. Bare `name` is a different cell (CN-2 canonicalises the NV key to `"&Name"`).

### Semantics
Second textual definition = compile error (CN-0 target; today runtime-only). Any dynamic write to a sealed cell = **error 341** (with the name). Read before the definition EXECUTES = **error 342** (with the name). No bypass via `OPSYN`/aliasing — the seal lives on the CELL (`NV_t.is_const`, Lon's bit).
✅ **All four verified live:** `NV_t.is_const` at `core.c:2267`; the namespace filter `_nv_ordinary()` at `:2337`; **error 341** at `:2427` — *"re-assignment of a sealed &constant: %s"*; **error 342** at `keywords.c:392` — *"&constant read before its one-time assignment: %s"*. `NV_KW_GET_fn`/`NV_KW_SET_fn` live at `keywords.c:386/393/451`. Killswitch `SCRIP_KWSPACE_SPLIT=0` live at `core.c:2336`.

⛔ **THE `$('&X')` CLAUSE IS STRUCK AS FACTUALLY WRONG** (s173, measured on live `sbl`; `FINDING-2026-08-19-s173-eval-fails-not-aborts-and-the-dollar-indirect-premise-is-falsified.md`). In SPITBOL, `$('&X')` names an ORDINARY VARIABLE literally spelled `&X` — a namespace wholly DISJOINT from the keyword `&X` in BOTH directions: `$('&ANCHOR')` reads null while the keyword reads 1, an indirect write leaves the keyword untouched, and `$('&NEVERSET') = 99` is accepted silently. **There was never a bypass here to seal — the clause is VACUOUS.** ⭐ **LIES GET CONSEQUENCES:** the earlier HQ-58 ruling had *narrowed* the clause to writes on the strength of an s153 truth-table row (`$("&N") -> 42, same cell`) that is **false against the oracle**. A wrong table row survived one ruling that refined it rather than re-testing it — narrowing a claim is not the same as checking it. **RULED AND CLOSED — HQ-61 (s173).**
Witnesses, all three present: `corpus/probe/cn/cn_indirect_is_ordinary_var.{sno,ref}` · `cn_indirect_rewrite.{sno,ref}` · `cn_indirect_seal.{sno,ref}`.

### The guarantee (two layers)
(a) **The bit** — `is_const` on the NV cell (landed CN-2, SCRIP `a63c13d9`). (b) **The page** — constants land in the KW-STATIC emitted block's sibling RO segment, `mprotect(PROT_READ)` after init: re-assignment FAULTS (CN-4).

### CVA / GVA — the two-area model of record (Lon's names, 2026-08-19)
**GVA** (Global Variable Area — `rt_gva_island`/`gva_register`/R9-slot machinery) holds **WRITABLE globals only**; **CVA** (Constant Variable Area) is its sealed sibling holding every constant DESCR + payload.
✅ Disjointness is already mechanically true at the collector: `src/optimizer/gva_collect.c` refuses `&`-names (`if (name[0] == '&') return 0;`). ⚠️ *The doc cited this as line **10**; it is at line **47** — the claim is true, the line number had drifted. Line numbers are the first thing to rot; cite the symbol.*

**The two guarantees are different things and the design needs both.** The **BIT** refuses a second NAME→value binding and costs nothing on the hot path (`NV_SET_fn` segregates on `name[0] != '&'` before any seal logic). The **ARENA** makes the bound VALUE physically immutable: a GVA-like mmap'd region holding every constant DESCR + payload, with GVA proper reserved for writable globals — which also relieves scarce R9-tier slot pressure.
**The EVAL hole and the answer:** `EVAL("&new = …")` mints constants at runtime, so a one-shot `mprotect` over the whole arena breaks. Recommended shape: **page-granular progressive sealing** — a bump allocator whose FILLED pages seal RO as the frontier crosses them; only the frontier page is writable; reads never pay a protection flip.
**Two homes, one semantics:** compile-time-known constants emit into the KW-STATIC block's sibling `.rodata` (mode-4) or the sealed arena (mode-3); EVAL-minted constants always land in the arena. Payoffs: no GC scanning, no write barriers, co-located reads. Status: DESIGN CANDIDATE for CN-4; the bit stays regardless.

### Optimizer tiers
**T1** scalar constants → immediates/rodata, zero NV/GVA reads. **T2** constant PATTERNS → `pat_static` by DECLARATION (⛔ but NOT the match-time `. *Fn()` capture-call class — those side effects fire per match by design). **T3** constant strings/tables → rodata, no GC scan, no write barriers.

### Parser-action COMPILER primitives (CN-5)
Lon's ruling 2026-08-19: *"nPush/nPop FAMILY is a compiler primitive… CONSTANT forever."* Builtin WINS always — sealed compiler names; user `DEFINE` of them is an error. The family lowers at compile time to dedicated zero-width boxes (counter op + four-port backtrack undo); the runtime two-level deferred-call encoding is never emitted for them.

### Oracle amplification + the pristine-oracle law
Both oracles learn `&name` as plain variables (`sbl-x`, `csnobol4-x`) so converted programs keep LIVE oracle grading. ⛔ **Stock binaries are NEVER replaced**; every `-x` proves full-classic-corpus byte-identity against stock before anything trusts it.

### The flagship
⛔ **PATH ABSENT.** The doc names `corpus/programs/snobol4/demo/beauty_c/` as the generated flagship (fixed point: `beauty_c < beauty.sno ≡ beauty.sno`). **No `beauty_c` directory exists anywhere under `corpus/`.** Live relatives: `corpus/demo/snobol4/beauty`, `corpus/tests/snobol4/beauty_suite`, `corpus/tests/snobol4/smoke/beauty_compiled.sno`. ⚠️ And `corpus/programs/` is ruled non-test material entirely (Lon 2026-08-27, `RULES.md:55`), so the flagship needs a new home *and* a new status before it can be cited again.

---

## SNOBOL4 — frontend

Frontend: SNOBOL4 → shared IR (`EXPR_t`/`STMT_t`). See `ARCH-ENGINE.md`.

### ⛔⛔ PARSER — THE DOC DESCRIBED A PARSER THAT IS NOT THE FRONTEND AND IS NOT BUILT
`ARCH-SNOBOL4.md` opened with: *"`src/frontend/snobol4/CMPILE.c` — single-file SIL-faithful parser. Public API: `cmpile_init`, `cmpile_file`, `cmpile_string`, `cmpile_free`. Parse node type `CMPND_t`. Statement type `CMPILE_t`,"* followed by a **Streaming model** section describing `FORWRD`/`FORBLK`/`FORRUN`/`STREAM` and the `IBLKTB`/`FRWDTB` action tables.

**Measured 2026-08-27, all of it:**
- `src/frontend/snobol4/CMPILE.c` **does not exist**.
- **Zero** occurrences of `cmpile_init`, `cmpile_file`, `cmpile_string`, `cmpile_free`, `CMPND_t` or `CMPILE_t` anywhere under `src/`.
- `CMPILE` lives at **`SILly/cmpile.{c,h}`** — a separate top-level directory, and ⛔ **`SILly/` appears nowhere in the `Makefile`: it is not built into `scrip`.**
- **The live SNOBOL4 frontend is lex/yacc:** `src/frontend/snobol4/{snobol4.l, snobol4.y, snobol4.lex.c, snobol4.tab.c, snobol4.tab.h}`, and `Makefile:325-326` builds `snobol4.tab.c` + `snobol4.lex.c`.

⭐ **LIES GET CONSEQUENCES — what this one would cost.** These were the doc's **first two sections**: the first thing a new hand reads about how SNOBOL4 source becomes IR. Anyone sent to *"the single-file SIL-faithful parser"* to add a construct, fix a parse bug, or answer a grammar question looks for a file that is not there, and — if they find `SILly/cmpile.c` by name — edits a program that is **not linked into the compiler**, then cannot explain why their change has no effect. ⛔ **The SIL-faithful description is not merely mis-pathed; it describes a different parsing strategy from the one that ships.** Whether `SILly/` is a live sibling project, a reference implementation, or residue is **not resolved here** — it is outside this row's scope, and I am flagging rather than guessing. What is resolved: it is not the frontend, and this file will no longer say it is.

### Runtime · DATATYPE · monitor hooks
Moved from the source doc unchanged. ⚠️ **NOT re-verified** — the sections' anchors were not spot-checked this pass, and after the CMPILE finding above they carry the same doubt as any unchecked claim in the same file. **Re-derive before relying on them**, and do not read their presence here as endorsement.

### Native pattern architecture — modes 3 & 4
Pattern = a graph of emitted Byrd boxes (`bb_box_fn`). ✅ *Anchor spot-checked: `bb_box_fn` is live — `src/driver/scrip.c` (14 hits), `src/templates/bb/bb_main.cpp`, `src/runtime/rt_gram_trampoline.S`.* The five-phase statement model, the real build/run split, and the ALL-INVARIANT BLOB FREEZE optimization step move with it.

### ⭐⭐⭐ THE THREE COMBINATORS — WHAT EACH ACTUALLY REQUIRES (PROVED BY DELETION, 2026-08-05, Lon-directed)
Moved intact — this is the section the file existed for, and it is a *proof method* rather than a claim about a path, so it does not rot the way the parser section did.
1. **SEQUENCE — wiring.** A node is possible but worthless.
2. **ALTERNATE — the box is REQUIRED**, and the section states exactly why.
3. **ARBNO — ZERO local storage**, proved by deletion.
   - ⭐ **CORRECTED LAW: ARBNO REQUIRES A NON-ZERO PER-ITERATION FRONTIER ADVANCE.** (Carried forward as the source doc's own correction — a law amended in place after the original claim proved too strong.)
   - **3b. ARBNO and the WHACK — the TWO-TIER verdict**, answering Lon's 2026-08-05 question *"is ζ storage required for the ARBNO BB box?"*

### ARBNO iteration frames — ERADICATION GOAL (Lon ruling, 2026-07-24 s146) · Dynamic linkage — the WIRE CONTRACT and the GLUE set (2026-08-01) · ZETA-PER-BOX FRAME DISCIPLINE
Moved. The frame-discipline section names *"the greatest current challenge — frame-base/register coherence at β re-entry under NESTED frames"*, records what is **already SOLVED (do not re-litigate)**, and carries the four design verdicts and the four rulings from the 2026-08-04 C-reference-ladder session.
⚠️ **Register/frame-base specifics in this section are ENGINE law and were the exact class found wrong in `ARCH-ICON.md`.** Where it and `ARCH-ENGINE.md`/`RULES.md` § BB FRAME-PLACEMENT CRITERION disagree, **the engine authority wins** — that is the rule this file adopts rather than adjudicating each line, precisely because a language file restating engine law is how the drift happened twice.

---

## SNOCONE — frontend and language spec

⭐ **This section moved WHOLE and essentially unaltered, and that is the finding.** Of the eight consolidated files, `ARCH-SNOCONE.md` was the one in good repair: every path it cites is live (`src/frontend/snocone/{snocone_driver,snocone_lex,snocone_parse.tab}.{c,h}` + `snocone_parse.y`, all present), and its own 2026-08-24 correction — that the comparison-operator sugar table *"documented 14 operators that do not exist"* — is consistent with the code (no `SNOCONE_RELOP`/`relop_sugar` under the frontend) and corroborated by `FINDING-2026-08-27-seat07-snocone-relop-sugar-was-deliberately-removed-not-a-regression-corpus-migrated.md`.
⭐ **Why it aged better than its siblings:** it is overwhelmingly *language semantics* — operator precedence, concatenation, the zero-space rule, statement boundaries, comments, identifiers — which do not rot when a directory is renamed. The files that drifted worst were the ones restating **engine and path** facts, which is the pattern this consolidation exists to stop.

**Reference spec for expression semantics:** SPITBOL Manual v3.7 by
Mark B. Emmer and Edward K. Quillen (Catspaw, 2000) — 368 pages.
Snocone expression syntax and semantics are 100% identical to SPITBOL;
the only differences are control flow (C-style braces vs label-goto)
and newline-as-whitespace. Chapters 15 (Operators), 17 (Data Types),
18 (Patterns), and 19 (Functions) are authoritative for what Snocone
expressions mean. Frontends and runtimes never reinterpret these.

Frontend: SNOCONE. Produces shared IR (EXPR_t/STMT_t). See ARCH-ENGINE.md.

---

## In one sentence

> Snocone is **Andrew Koenig's `.sc` self-host operator set, minus
> `&&` / `||` / `%`, plus C-style structured control flow, plus
> SPITBOL space-as-concat.**

A SPITBOL program that does not itself use `&&`, `||`, or `%` as
binary operators, and that uses `;` statement terminators with
`name:` label syntax (not column-1 labels), runs unchanged under
Snocone. **This functional-superset guarantee is a hard invariant.**

---

## Operator tables

### Binary operators (highest priority first — SPITBOL Manual Ch.15)

| Op       | Assoc  | Pri | Definition                               |
|----------|--------|-----|------------------------------------------|
| `=`      | right  |  0  | Assignment                                |
| `?`      | left   |  1  | Pattern match                             |
| `\|`     | right  |  3  | Pattern alternation                       |
| *space*  | right  |  4  | **Concatenation or match** (synthetic `T_CONCAT` token from lexer) |
| `+`      | left   |  6  | Addition                                  |
| `-`      | left   |  6  | Subtraction                               |
| `/`      | left   |  8  | Division                                  |
| `*`      | left   |  9  | Multiplication                            |
| `^` `!` `**` | right | 11 | Exponentiation                          |
| `$`      | left   | 12  | Immediate assignment (in pattern context) |
| `.`      | left   | 12  | Conditional assignment (in pattern ctx)   |

### ⛔ Comparison-operator sugar — **REMOVED FROM THE LANGUAGE, 2026-08-24. THIS TABLE DOCUMENTED 14 OPERATORS THAT DO NOT EXIST.**

**Lon, s272, carried in the commit messages that removed them** (SCRIP `28d73dbf2`, `7408829f8`): *"ambiguous; removed until ruled"* and *"sugar rejection is a plain syntax error, as if the construct never existed"*.

**MEASURED AT HEAD (hq_C 2026-08-27):** `:==:` has **zero occurrences** in `src/frontend/snocone/snocone_lex.c`. `x = 1 :==: 1;` → `snocone parse error: syntax error`. The predicate-call form is unaffected and is the supported spelling:

| Snocone surface | status |
|---|---|
| `EQ()` `NE()` `LT()` `LE()` `GT()` `GE()` (numeric) · `LEQ()` `LNE()` `LLT()` `LLE()` `LGT()` `LGE()` (lexical) · `IDENT()` `DIFFER()` | ✅ **SUPPORTED — the spelling to use** |
| `==` `!=` `<` `<=` `>` `>=` · `:==:` `:!=:` `:<:` `:<=:` `:>:` `:>=:` · `::` `:!:` | ⛔ **REMOVED — a plain syntax error, by ruling** |

⛔⭐ **THE CONSEQUENCE THIS STALE TABLE ALREADY CAUSED, named because a lie without a cost gets re-introduced:** the removal's substance lived **only in two commit messages** — no FINDING, no GOAL entry, and this table still said "hard invariant". So when 17 crosscheck corpus files began failing, the failure was mis-minted as a **regression** (`snocone-relop-parse-regression`) and a seat spent a session on it before discovering, from `git log`, that the operators had been **deliberately removed hours before the row was minted**. ⭐ Their cure was right — migrate the corpus to the predicate-call form rather than revert a Lon ruling (seat07, 17/17 byte-identical both modes; the sweep moved 108p/52f → 125p/35f). **The row should never have existed, and this table is why.**

⚠️ **OPEN QUESTION, RECORDED AS A QUESTION AND NOT AS AN INVARIANT:** *"removed until ruled"* implies a replacement-syntax ruling was expected. **None has landed in the three days since.** Until Lon rules, the code's behaviour above **is** the specification — and this file must describe what the code does, never what a pending ruling might restore.

### Undefined binary operators (available for `OPSYN`)

| Op | Assoc | Pri |
|----|-------|-----|
| `&` | left  |  2  |
| `@` | right |  5  |
| `#` | left  |  7  |
| `%` | left  | 10  |
| `~` | right | 13  |

The lexer emits these as plain tokens; the grammar routes them
through the OPSYN catch-all production. **`%` was previously
Andrew's modulo (lowering to `REMDR()`); it is now reserved as a
user-OPSYN slot. Programs needing remainder write `REMDR(a, b)`
directly.**

### Unary operators (all equal priority, higher than any binary, right-to-left)

| Op | Name           | Definition                                     |
|----|----------------|------------------------------------------------|
| `@` | at sign       | Assigns cursor position to its operand          |
| `~` | tilde         | Negates failure or success of its operand       |
| `?` | question mark | Interrogation — returns null if operand succeeds|
| `&` | ampersand     | Keyword (with **zero-space**: `&IDENT` is one `KEYWORD_NAME` token) |
| `+` | plus          | Indicates positive numeric operand               |
| `-` | minus         | Negates numeric operand                          |
| `*` | asterisk      | Defers evaluation of expression                  |
| `$` | dollar sign   | Indirection                                      |
| `.` | period, dot   | Returns a name                                   |

Undefined unary operators (available for `OPSYN`):
`!` `%` `/` `#` `=` `|`

### Dual-role operator disambiguation rule

The dual-role unary/binary operators (`& | ? $ . + - * / ^ ! @ # % ~`)
are **binary only when {W}OP{W}** — both sides whitespace. Without
right-side whitespace they are unary.

This is the SPITBOL/SNOBOL4 rule. Concretely:

- `2 * 3` (whitespace both sides) → binary multiply
- `A *B` (whitespace left only) → concat A with unary defer of B
- `*W` (no whitespace, expression start) → unary defer
- `1*2` (no whitespace either side) → **syntax error**, matching SPITBOL Error 231

The implementation enforces this rule consistently for all dual-role
operators including `+` `-` `*` `/` `^` — see GOAL-SNOCONE-100.md
SB-6.E for the rung that landed this. `^` has no unary form (the
unary operator set is `+ - * & @ ~ ? . $`), so a tight or
unary-position `^` is a syntax error.

`!` is dual-role in a different way: defined-binary
(exponentiation, alternate spelling for `^` and `**`, priority 11)
AND undefined-unary (OPSYN-available, like `% / # = |`). The lexer's
binary cascade for `!` already follows the strict `{W}!{W}` rule;
the unary-position emit is tracked under SB-6.F (currently the
fallback collapses to `T_2CARET` instead of the correct `T_1BANG` —
narrow lexer-only fix, does not gate SB-6 self-host).

---

## Concatenation — whitespace IS the concat operator

Whitespace between two value-yielding tokens IS the concat operator.
The lexer emits a synthetic `T_CONCAT` token at the boundary; the
grammar treats it as a normal binary operator at SPITBOL priority 4,
right-associative.

```snocone
x = 'foo' 'bar';        // assigns 'foobar'
x = a /* comment */ b;  // concat across the comment — comments are whitespace
```

The lexer suppresses `T_CONCAT` injection before any token that
could be a binary operator (`.`, `$`, `+`, `-`, `*`, `?`, `&`, `~`,
`@`). Those tokens are left for the grammar to disambiguate via the
{W}OP{W} rule above.

---

## `f(x)` vs `f (x)` — the zero-space rule

`f(args)` with **zero whitespace** between the identifier and `(`
is a function call. `f (expr)` with one or more whitespace chars
between is `f` concat `(expr)`. Strict — same SPITBOL rule, enforced
by the lexer via the `IDENT_LPAREN_NOSP` token.

```snocone
result = f(x);          // call f with argument x
result = f (x);         // concat the value of f with the value of x
result = f /* */ (x);   // also concat — the comment is whitespace
```

---

## `&IDENT` — the keyword-name token

`&` followed by an identifier with **zero whitespace** is a keyword
reference (e.g. `&FULLSCAN`, `&UCASE`, `&ANCHOR`). Single `KEYWORD_NAME`
token carrying the full sequence.

If `& IDENT` (whitespace), the `&` becomes unary `AMPERSAND` followed
by `IDENT` — almost certainly a syntax error.

---

## Conditions are SPITBOL backtracking expressions

Not C-style booleans. The parenthesised condition of `if`, `while`,
`do/while`, `for`-test, and `case` tag is a single SPITBOL
backtracking expression. The success/failure exit drives the branch.

```snocone
if (subj ? pat = repl) {
    // match succeeded; subj has been mutated by the replacement
}

while (subj ? BREAK(',') . token ' ' = '') {
    // each iteration extracts the next comma-delimited token
}
```

A bare variable reference always succeeds (a bound name has a value).
`if (x)` therefore always takes the success branch — no truthy/falsy
semantics. The LS-4.w warning pass is a deferred TODO that would
flag this as "condition can never fail," but the construct is not an
error.

**Boolean AND is juxtaposition, not `&` or `&&`.** Inside `if (...)`,
`while (...)`, etc., write `if (IDENT(t(x), 'E_FNC') IDENT(v(x), ','))`
to mean "both predicates succeed" — they are concatenated in
backtracking-expression context. Using `&` is a syntax error
(documented session 2026-05-03 PARSER-PR-3 attempt). Boolean OR is
the alternation operator `|`.

---

## Statement boundary is `;` only — newlines are whitespace

Every Snocone statement ends with `;`. Newlines, tabs, and spaces
are all whitespace; the lexer treats them identically. There is no
implicit semicolon at end of line, no continuation token, no
off-side rule.

`x = 1\ny = 2;` is **one statement** (the expression `x = 1 y = 2`,
which evaluates `1 y = 2` as a chain and assigns to `x`, almost
certainly not what was meant). Programs that omit `;` produce
surprising parses, not error messages. This is by design.

(For one-statement-per-line readability, source files conventionally
write each statement on its own line with `;` at the end — but the
parser does not care.)

---

## Bare expression statements may fail silently

A statement that is just `expr;` with no surrounding control flow
lowers to a bare SPITBOL statement with no `:S(...)F(...)`
decoration. If it fails, control falls through to the next
statement.

```snocone
EQ(x, y);          // succeeds or fails; either way, next stmt runs
GT(x, 0)  x = -x;  // negate x if positive (succeed-and-side-effect idiom)
```

This is the SNOBOL4 default — failure-as-control-flow is reserved
for the parenthesised conditions listed above.

---

## Multi-line continuation — `+` / `.` at column 1

SNOBOL4-style continuation: when the next physical line's column 1
is `+` or `.`, the line is glued onto the previous one. The
continuation counts as whitespace for the CONCAT rule.

```snocone
   x = 'foo'
+         'bar'
```

emits `IDENT(x) ASSIGN STRING('foo') CONCAT STRING('bar')`. The
continuation is transparent.

---

## Comments

`// to end of line` and `/* ... */` block comments. Both count as
whitespace for the CONCAT rule. Block comments are non-nesting and
may span newlines.

```snocone
   x = 'foo' /* hello */ 'bar'
```

emits `IDENT(x) ASSIGN STRING('foo') CONCAT STRING('bar')` — the
comment is a whitespace gap, CONCAT fires across it.

---

## String literals — the SNOBOL4 rule, no escapes

A string starts with `'` or `"`. Body is everything up to the
matching delimiter. **Backslash is NOT an escape character.** To
embed a quote, use the other delimiter (`"can't"` or `'a"b'`), or
build via `CHAR(39)` etc. Newlines inside strings are not permitted.

---

## Identifiers

`[A-Za-z_][A-Za-z0-9_]*` — Andrew's `.sc` uses `_` for compound
names (`cl_type`, `or_binfo`). SNOBOL4 source-style names with `.`
(`cl.type`) are NOT identifiers in Snocone — they lex as `IDENT(cl)
PERIOD IDENT(type)`.

Snocone is **case-sensitive byte-for-byte** (per `RULES.md` "Case-
sensitive name space"). The lexer keeps the byte sequence the user
wrote — no folding at lex time.

---

## Control flow

C-style structured control. Block braces `{` `}` around every body.

```snocone
if (cond) { ... }
if (cond) { ... } else { ... }

while (cond) { ... }
do { ... } while (cond);            // do/while only — do/until removed

for (init; test; step) { ... }      // semicolons (Andrew used commas)

switch (e) {
    case v1: ... ;
    case v2: ... ;
    default: ... ;
}                                   // no fall-through; implicit break at end of each case

break;
break LABEL;                        // labeled break
continue;
continue LABEL;                     // labeled continue

goto LABEL;                         // single keyword (not Andrew's two-word `go to`)
LABEL: stmt                         // label clause; can stack: L1: L2: stmt
```

`goto` is the escape hatch for any control-flow shape the
structured forms don't cover — labeled-break out of nested loops,
state-machine dispatch, retry-from-error. Using it for ordinary
control flow is discouraged.

### Lowering map

| Snocone source            | SNOBOL4-IR equivalent                             |
|---------------------------|---------------------------------------------------|
| `expr;`  (bare statement) | emit `expr` as bare SPITBOL statement; failure is silent fall-through |
| `name : stmt`             | emit `name` at column 1 before lowered `stmt`     |
| `goto name;`              | append `:(name)` to current statement, or emit empty `:(name)` clause |
| `if (cond) S1`            | `cond  :F(after)` `S1` `after  ...`               |
| `if (cond) S1 else S2`    | `cond  :F(else)` `S1  :(after)` `else  S2` `after  ...` |
| `while (cond) S`          | `top  cond  :F(after)` `S  :(top)` `after  ...`   |
| `do S while (cond);`      | `top  S` `cond  :S(top)`                          |
| `for (init; cond; step) S`| `init` `top  cond  :F(after)` `S` `step  :(top)` `after  ...` |
| `switch(e){case v: S; ..}`| see "switch backends" below — chain or table |
| `break;` / `break LABEL;` | `:(after-of-innermost-or-labeled-loop-or-switch)` |
| `continue;` / `continue LABEL;` | `:(top-of-innermost-or-labeled-loop)`       |
| `(e1, e2, e3)` (alt-eval) | SPITBOL extension — emit as-is to SPITBOL backend; for non-SPITBOL backends, lower to a chain of `:S(after)` branches |

### Switch backends — chain vs label-table (compile-time selectable)

**Status:** open design idea (Lon, session 2026-05-02 #6). Not yet
implemented. See `GOAL-SNOCONE-100.md` for the working
goal and milestones.

**Motivation.** `switch` over a string discriminator is the natural
target for SNOBOL4-style polymorphic dispatch — `:S($('pp_' t))F(...)`
in `beauty.sno` is a 30+ way string switch. Today's lowering is a
single shape: an if/else-if chain (per the `IDENT(e, v) :S(caseN)`
row in the lowering map). That's the right answer for small case
counts and the wrong answer for a 30-way dispatch in a hot loop.

**Two backends, one source language.**

1. **`chain`** — current behavior. Lowers to a sequence of
   `IDENT(e, vK)  :S(caseK)` followed by a default fallthrough. O(n)
   compares per dispatch. Wins for ≤ ~4 cases, smallest code, best
   branch-predictor behavior when one case dominates, and for cases
   over heterogeneous types or non-literal values.

2. **`table`** — perfect-hash jump table on the case literals.
   Compiler builds the hash at compile time (gperf-style) keyed on
   the literal case strings. Dispatch is one hash + one compare +
   one indirect branch. O(1). Wins for dense or large case sets,
   especially the polymorphic-AST-dispatch idiom. Requires every
   case label to be a compile-time literal of the same scalar type
   (string or integer); falls back to `chain` when any case violates
   that.

**Compile-time selection — three layers, narrowest wins:**

| Layer | Form | Scope |
|-------|------|-------|
| Per-site | `switch [[table]] (e) { ... }` / `switch [[chain]] (e) { ... }` | one switch only |
| File-level | `#pragma snocone switch=table` near top of file | rest of file |
| Driver flag | `--switch-style=chain\|table\|auto` on `scrip` | whole compile |

`auto` is the recommended default: choose `table` when (a) ≥ N cases
(N=5 is a sensible starting threshold) and (b) every case is a
compile-time string-or-integer literal of the same type. Otherwise
`chain`. The threshold lives in one place in the lowering pass and
is tunable.

**IR considerations.** The shared IR (`ir.h`) doesn't need a new
EKind — both backends lower to existing primitives. `chain` emits
the same sequence it does today. `table` emits a new lowering shape
in `sm_lower.c` (and per-backend equivalents in JVM/.NET/JS/WASM):
a constant table holding `(hash_key, label)` pairs plus a small
preamble computing `hash(e)` and indexing the table. The hash table
itself is data, not IR. No frontend changes beyond the optional
`[[chain|table]]` attribute parse.

**Why this matters for SNOBOL4-style dispatch.** `beauty.sno::pp`
and `beauty.sno::ss` each dispatch on tree-node-type strings (30+
distinct values). Today's `if/else-if` Snocone port (which is what
the chain lowering produces) is both slow and a fertile source of
copy-paste bugs (see SB-6.E.7 audit findings — beauty.sc had three
identical broken `if` conditions in `pp()`). A `table`-lowered
`switch` is faster and removes the entire class of "I copy-pasted
case 7 from case 6 and forgot to change the constant" bugs. The
source becomes:

```snocone
switch [[table]] (t) {
    case 'snoBuiltinVar': ppLeaf(x, t); break;
    case 'snoFunction':   ppLeaf(x, t); break;
    ...
    case 'snoComment':    SetLevel(0); GenSetCont(); Gen(v(c[1]) nl); break;
    default: error();
}
```

That **is** the original `:S($('pp_' t))` idiom expressed in
structured Snocone. The compiler then chooses chain or table based
on the heuristic.

---

## Functions

```snocone
function name (param1, param2) local1, local2 {
    ...
    return E;         // value via E (lowers to `name = E :(RETURN)`)
    return;           // bare `:(RETURN)`
    nreturn;          // pattern/name return — `:(NRETURN)`
    freturn;          // failure — `:(FRETURN)`
}
```

Statement terminator `;` is mandatory. Locals can be declared with
commas after the parameter list (canonical) or folded into the
parameter list with a comma separator (scrip dialect — both forms
accepted).

The keyword is `function`, not Andrew's `procedure` (rename per
LS-4.h, Lon session #7 — these forms return a value, name matches
role).

Lowering of `function name(args)`: emits `DEFINE('name(args)')
:(name_end)` then label `name` on body's first stmt then `name_end`
pad.

---

## `struct` declarations

Andrew's `.sc` line 162 self-host extension, adopted verbatim:

```snocone
struct NAME { f1, f2, f3 }          // no trailing `;`
```

Lowers to single bare-expression statement `DATA('NAME(f1,f2,f3)')`.
SPITBOL's `DATA()` installs the constructor plus per-field
accessors (each accessor doubling as an L-value).

---

## Alternative-evaluation `(e1, e2, e3)`

SPITBOL extension (Manual Ch.15 footnote): a parenthesised list of
expressions separated by `,` is evaluated left to right; the value
of the first to succeed is the value of the whole. If all fail,
`(...)` fails.

```snocone
result = (LT(I, J) I, GT(I, J) J, "Same");
```

This is the canonical replacement for Andrew's `||` operator — same
semantics, different surface (and already a SPITBOL primitive, not
something we invented).

The IR node is `E_VLIST` (n-ary, eager left-to-right, short-circuit
on first non-failing arm). Distinct from `E_ALT` (pattern alternation,
lazy at match time, with backtracking).

---

## What is NOT in Snocone

- Binary `&&` (replaced by whitespace concat)
- Binary `||` (replaced by alt-eval `(e1, e2, e3)`)
- Built-in modulo `%` (use `REMDR(a, b)`; `%` reserved as OPSYN slot)
- `do/until` (removed per Lon directive 2026-04-30 #12; use
  `while (~cond)` or `goto`-with-label)
- `then` keyword (Andrew has none; not in KW_TABLE)
- Two-word `go to` (use single-keyword `goto`)
- `procedure` keyword (renamed to `function`)
- SPITBOL goto-field `:S(L) F(M)` syntax — Snocone has no goto-field.
  Control flow uses structured forms or `goto LABEL;`. The `:` is
  always a label-suffix in Snocone grammar.
- Newline tokens. The lexer does not emit a newline token; newlines
  are whitespace, full stop.

---

## DATATYPE convention

SCRIP returns **uppercase** for built-in types (`"NAME"`,
`"PATTERN"`, `"STRING"`, `"INTEGER"`). This is intentional per
SNOBOL4 spec. SPITBOL x64 returns lowercase (a known divergence;
see `RULES.md` "DATATYPE case" table).

Tests that compare DATATYPE results must be portable across case —
compare against a runtime-derived token, never hardcode `'PATTERN'`
or `'pattern'`. See `RULES.md` "DATATYPE case — authoritative,
intentional per runtime" for the binding rule.

---

## Implementation map

### File layout (SCRIP)

| Path | What |
|------|------|
| `src/frontend/snocone/snocone_parse.y` | Bison grammar |
| `src/frontend/snocone/snocone_parse.tab.{c,h}` | Generated parser tables |
| `src/frontend/snocone/snocone_lex.c` | Threaded-code FSM lexer |
| `src/frontend/snocone/snocone_lex.h` | Public FSM API |
| `src/frontend/snocone/snocone_driver.{c,h}` | scrip-side entry point |
| `archive/snocone_lower.{c,h}` | Legacy lowering (archived in LS-4.k) |
| `archive/snocone_control.{c,h}` | Legacy control-flow lowering (archived in LS-4.k) |

### Lexer

Single-pass threaded-code FSM in `snocone_lex.c` — one C function
`sc_lex_next(LexCtx *ctx)` whose body is a graph of labelled
`Label: action; goto NEXT;` blocks. No `switch` / `for` / `while` /
`do-while` in the FSM body. The FSM maintains a previous-token
state and emits a synthetic `T_CONCAT` token when a value-yielding
token is followed by another with whitespace between — that is the
space-as-concat implementation.

Comments fold into whitespace via `S_LCOMMENT` / `S_BCOMMENT`
sub-FSMs. Token names follow the `T_<arity><charname>` scheme
matching `snobol4.tab.h` — `T_2EQUAL` (`=`), `T_2DOT` (`.`),
`T_2DOLLAR` (`$`) for binary; `T_1*` for unary.

### Grammar

Bison parser in `snocone_parse.y`, generated to
`snocone_parse.tab.{c,h}`. Bison reports 0 shift/reduce and 0
reduce/reduce conflicts at every rung. Precedence declarations
match SPITBOL Manual Ch.15 priorities 0–13. The conditional in
`if`, `while`, `do/while`, `for`-test, and `case` tag is a single
`expr` non-terminal — the same backtracking expression that appears
as a SPITBOL statement subject/pattern/replacement chain. No special
"boolean expression" non-terminal.

Public entry: `CODE_t *snocone_parse_program(const char *src,
const char *filename)`.

### Build path

`.l` and `.y` source edits require regeneration:

```bash
bash scripts/regenerate_parser_and_lexer_from_sources.sh
```

This regenerates `snocone_parse.tab.{c,h}` (also any other front-
end's `.tab.{c,h}` and `.lex.c`). Per `RULES.md` "Editing `.y` or
`.l` files," the `.y`/`.l` source AND the updated generated files go
in the **same commit** — never edit the generated files directly
for grammar or lexer logic. Generated files are checked in so
normal builds do not require bison/flex on the build machine; flex
and bison are installed via `scripts/install_system_packages.sh`
when a regeneration is needed.

### Smoke gate (per-session, before every commit touching Snocone)

```bash
bash scripts/test_smoke_snocone.sh                 # PASS=5 FAIL=0
bash scripts/test_beauty_snocone_all_modes.sh      # PASS=42 FAIL=0 SKIP=3
bash scripts/test_smoke_unified_broker.sh          # PASS=49 FAIL=0
```

---

## Corpus migration

The `scripts/util_migrate_snocone_to_lang_space.py` script does the
mechanical sweep:

- `&&` → space (the new concat operator)
- `||` → `(a, b)` n-ary alt-eval (preserves short-circuit semantics)
- `go to NAME` → `goto NAME`

Strings and comments preserved verbatim. Single `|` (pattern
alternation) untouched. Idempotent.

Manual review handles edge cases (strings containing `&&` or `||`
literally, format specifiers using `%`, etc.).

A companion script `scripts/util_migrate_snocone_procedure_to_function.py`
handles the `procedure` → `function` rename.

---

## Authority and scope

This file is the single source of truth for Snocone language and
front-end architecture. The earlier sources have been consolidated
here:

- `GOAL-SNOCONE-LANG-SPACE.md` (deleted — work complete, content here)
- `RULES.md` "Snocone language facts" (now a one-line pointer to this file)
- `REPO-SCRIP.md` "Snocone front-end" (now a one-line pointer)
- `corpus/programs/snocone/LANGUAGE.md` (deleted — pointer in corpus README)
- `GOAL-SNOCONE-BEAUTY.md` "Snocone language facts" (deleted — pointer here; GOAL-SNOCONE-BEAUTY.md itself later absorbed into `GOAL-SNOCONE-100.md`, 2026-08-27)

Andrew Koenig's original Snocone (`SNOCONE.zip`: `snocone.sc`,
`snocone.sno`, `snocone.snobol4`) is historical context, not
authoritative for our Snocone. The authoritative implementation is
`snocone_lex.c` + `snocone_parse.y` in this tree; this document is
the spec they implement.

---

## Reference-sweep policy (applied 2026-08-27, recorded so it is not undone)

**22 live documents** were repointed from the eight retired names to this file: `GOAL-*`, `ARCH-*`, `PLAN.md`, `DESIGN-*`, `DISPATCH-*`, `CARVEOUT-*`, the primers, and `SCRIP/scripts`. Residual live citations after the sweep: **0**.

⛔ **`FINDING-*` files and `.github/archive/` were deliberately NOT repointed.** A FINDING is a dated, attributed record of what was true when it was written; rewriting its citations would make it claim to have cited a file that did not exist on its own date. ⭐ **The rule: sweep the documents that TELL you what to do; never sweep the documents that RECORD what happened.** Roughly 10 of `ARCH-ICON.md`'s 24 citers were FINDINGs, so this is a large deliberate exclusion, not an oversight.

⚠️ **And one thing the sweep got wrong, recorded because the next consolidation will hit it too:** the blanket `sed` was run over `.github` *including this file*, and it rewrote the eight old names inside the RETIRED NAMES table and in seven prose sites that quote the retired docs by name — turning *"`ARCH-ICON.md` carried the LIVE REGISTER CONTRACT"* into a statement about this file. All eight sites were repaired by hand. **A reference sweep must EXCLUDE the consolidation target**, because that is the one file where the retired names are the content rather than a pointer.
