# GOAL-SNOCONE-IR-BB.md — Snocone IR Interpreter + BB Broker

## ⛔ FACT RULES POINTER (Lon 2026-06-06)
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION (corrected): canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / GOAL-PROLOG-BB.md / GOAL-RAKU-BB.md and RULES.md. ZERO BINARY emission anywhere in a `bb_*.cpp` (top level or helpers); `x86()` internals are the ONLY emitter of BINARY and TEXT.

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

**No language-specific logic in any BB or XA C++ template.** All delineated operations are enveloped in
unique BBs; each BB does NOT have varying runtime behavior depending on language. Templates dispatch on IR
shape and representation flags only. FORBIDDEN inside `src/emitter/BB_templates/` and
`src/emitter/XA_templates/`: language enums/guards (`IR_LANG_*`, `LANG_*`, `is_<lang>`), language-named
template functions/files/dispatch arms, and hardcoded language-builtin names. Behavior that differs by
language belongs in the runtime (by-name dispatch) or in LOWER (a different IR shape → its own unique BB) —
never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (XA scanned clean 2026-06-03); fix
ladder: LB-* in `GOAL-PASCAL-BB.md`. COMPLETION TEST: the audit's Tier-1 grep over `BB_templates/` +
`XA_templates/` returns 0 sites.

## ⛔ NO C BYRD-BOX FUNCTIONS — A BOX IS ENTERED BY JUMPING TO ITS α/β LABELS, NEVER A `(ζ, int entry)` C CALL (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**There is NO such thing as a C byrd-box function. The "brokered BB" concept is ABOLISHED.** A byrd box is
EMITTED machine code. It has exactly TWO entry points, and they are **LABELS** — α (fresh entry) and β
(resume). Control reaches a box by **JUMPING to one of those labels**. A box is NEVER a C function, is NEVER
reached by a C call, and NEVER takes an integer `entry` argument to select α vs β. The C signature
`DESCR_t NAME(void *ζ, int entry)` — a ζ-state pointer plus an `int entry` α/β selector — is **FORBIDDEN**.
It was the discredited brokered-BB calling convention (an "entry kludge"); it is gone. The ONLY driver is the
**mode-2 BB-graph interpreter** (`bb_exec.c`), which walks the IR graph directly and IS the broker/driver;
**modes 3 and 4 are native code in which boxes thread control by jumping between α/β labels** (RULES X86-64
register / subject-model convention) — never through a function pointer plus an `entry` integer. There is no
`bb_broker` driver and no `(ζ, int entry)` box anywhere.

**HISTORY — READ THIS, because it is why the rule now exists in this strongest form.** This prohibition has
stood for **AT LEAST TWO MONTHS**. Lon ordered these C `(ζ, int entry)` byrd boxes DELETED at least **THREE
separate times**, and each time a session either declined, re-introduced them, or held/reverted the deletion
"to keep the build green." A prior plain rule (RULES.md "NO C BYRD-BOX FUNCTIONS") did **not** hold. They
were finally deleted **2026-06-01** — the `pl_*_fn` family (all of `pl_broker.c`), `gen_bb_dcg`,
`gen_bb_oneshot`, `resolve_bb_dcg`, `bb_deferred_var`/`_exported`, `fail_box`, the dead `bb_cap`/`bb_atp`
declarations, **and the `bb_broker` driver itself** (`bb_broker.c`). **KEEPING THE BUILD GREEN IS NOT A
LICENSE TO PRESERVE A FORBIDDEN BOX.** When this signature and a green build conflict, the **signature
loses**: delete the box and tear out its callers (the brokered execution path — Prolog `--run`, brokered
pattern scan, brokered generators — is removed, not preserved). A broken build pending the caller teardown is
acceptable; a surviving `(ζ, int entry)` box is not.

**COMPLETION TEST:** (a) `grep -rnE 'DESCR_t[[:space:]]+[A-Za-z_]+[[:space:]]*\([[:space:]]*void[[:space:]]*\*[[:space:]]*[a-z]*[[:space:]]*,[[:space:]]*int[[:space:]]+entry' src/ --include=*.c --include=*.cpp --include=*.h | grep -v typedef` == 0 (no C byrd-box definition or declaration with the `(ζ, int entry)` signature); (b) no `bb_broker` driver function exists; (c) every emitted box is entered by a jump to an α or β label, never a C call with an `entry` int; (d) this FACT RULE body is byte-identical across the five GOAL-*-BB files.

## ⛔ NO VALUE STACK — EVER (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**SCRIP HAS NO VALUE STACK. NO SESSION, IN ANY LANGUAGE, MAY CREATE ONE.** (Lon directive, 2026-05-31.)
There is nothing like a value stack in SCRIP — every value a BB graph computes or holds at run time lives
INSIDE a box: a READ-ONLY operand constant reached `[rip+disp]` into sealed data, or a READ-WRITE slot
reached `[ζ=r12+off]` in the per-sequence one-register frame (the `test_sno_1.c`/`test_icon.c` named-slot
model). A consumer reads a producer's result directly from that producer's slot. A value is NEVER pushed
to or popped from a global stack, and intermediate producer→consumer values are NEVER threaded through a
name-table round-trip. This is the same law as the PER-BOX LOCAL STORAGE FACT RULE; this rule states the
prohibition in the strongest, language-independent form so it cannot be re-introduced from any session.

**The `g_vstack` global array is DELETED (2026-05-31) and must NEVER be resurrected** — nor any equivalent
under a different name (`*_vstack[]`, `value_stack`, `g_estack`, a hand-rolled `WamWord[]`/`DESCR_t[]`
push/pop arena used to pass values between boxes, etc.). FORBIDDEN to (re)introduce: a global/static array
whose purpose is to push a box's value and pop it in a consumer; `rt_push_*`/`rt_pop_*`/`vstack_*` value
traffic; any `*_push`/`*_pop` helper that moves an *intermediate* value between boxes. (KEEP, NOT a value
stack: the Prolog trail `g_resolve_trail`/`rt_pl_trail_*` — a binding-undo ledger; the choice-point ledger
`g_resolve_bfr`/`resolve_choice` — the irreducible cross-node resume spine; the C call stack used for
genuine recursion; an ARBNO-style explicit indexed per-activation frame array. None of these is a value
stack.) The residual `vstack_*`/`rt_vstack_ops_t` SCAFFOLDING left in `src/runtime/rt/rt.c` is dead/aborting
(`g_ops` only ever points at `g_default_ops`, whose push/pop/peek `abort()`); it is being removed rung by
rung (the VSX ladder) and must NOT be wired up to anything — adding a real backing store to it = creating a
value stack = a violation.

**GUARD:** `scripts/test_gate_no_vstack.sh` (informational baseline now; flips to a HARD `--strict`
zero-check at VSX-8). It greps (comments stripped) ACROSS ALL `src/` for `g_vstack`/`vstack_push`/
`vstack_pop`/`vstack_peek`/`rt_vstack_*`. The `g_vstack` token is already at ZERO and must STAY at zero;
the rest trend to zero as the scaffolding is deleted. Any session that makes the `g_vstack` count non-zero,
or that adds a new value-stack array under any name, has violated this rule. **COMPLETION TEST:** (a)
`grep -rn 'g_vstack' src/` == 0 (code AND comments); (b) no new global/static push/pop value arena exists;
(c) `scripts/test_gate_no_vstack.sh` `g_vstack` line reads 0; (d) the FACT RULE body is byte-identical
across all five GOAL-*-BB files.

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repo:** SCRIP
**Done when:** All 14 Snocone beauty-sc subsystems PASS under `scrip --interp`,
including pattern match (`subject ? pattern`) wired through `bb_broker(BB_SCAN)`.

---

## Motivation

Snocone compiles to the shared IR (EXPR_t / STMT_t) via `snocone_compile()`.
The `--interp` path calls `execute_program(prog)` — the SNOBOL4 interpreter — which
handles the IR nodes Snocone's lower emits (E_ADD, E_CAT, E_FNC, E_VAR, etc.).
That works for scalar / arithmetic / string programs. Two gaps remain:

1. **Control flow** — `if/else/while/for/return/procedure` are parsed by snocone_parse
   but snocone_lower skips control-flow tokens (returns 0 without emitting IR).
   The lower must emit STMT_t with proper goto labels and branch targets.

2. **Pattern match** — `subject ? pattern` maps to the SNOBOL4 statement's
   `subject/pattern` fields + `bb_broker(BB_SCAN)` (wired in U-9).
   snocone_lower currently has no `SNOCONE_QUESTION` → STMT_t pattern case;
   it only maps binary `?` to `DIFFER(a,b)`, which is wrong for subject?pattern.

**Baseline (session 2026-04-13):** 3/14 beauty-sc subsystems PASS (assign, fence, global).
These three pass because they use only scalar assignment + keywords — no control flow,
no pattern match.

**Failing subsystems and root causes:**

| Subsystem | Root cause |
|-----------|-----------|
| arith | control flow (if/while/procedure) not lowered |
| strings | control flow (procedure/if) not lowered |
| match | control flow + `subject ? pattern` not lowered |
| roman | control flow (procedure/if/while) not lowered |
| stack | control flow (procedure) not lowered |
| trace | control flow (procedure) not lowered |
| counter | control flow (procedure/if) not lowered |
| semantic | control flow (procedure/if) not lowered |
| ReadWrite | control flow + I/O not lowered |
| ShiftReduce | control flow (procedure/if/while) not lowered |
| tree | control flow (procedure/if) not lowered |

---

## Architecture — how Snocone IR maps to SNOBOL4 stmt_exec

Snocone control flow maps directly onto the SNOBOL4 statement model:

```
Snocone source              STMT_t equivalent
─────────────────────────── ────────────────────────────────────────────────
if (cond) { S } else { T }  cond-stmt  :S(L_then) F(L_else)
                            L_then: S  :GO(L_end)
                            L_else: T
                            L_end:
while (cond) { S }          L_top: cond-stmt :S(L_body) F(L_end)
                            L_body: S  :GO(L_top)
                            L_end:
for (init; cond; step) { S} init; L_top: cond :S(L_body) F(L_end)
                            L_body: S; step; :GO(L_top)
                            L_end:
return expr                 st->replacement = expr; :GO(FRETURN)
freturn                     :GO(FRETURN)
nreturn                     :GO(NRETURN)
procedure name(a,b) { ... } DEFINE + label
subject ? pattern           st->subject=subj; st->pattern=pat; bb_broker BB_SCAN
```

The IR interpreter (`execute_program` / `stmt_exec`) already handles all of these —
we just need snocone_lower to emit the right STMT_t nodes.

---

## Key files

| File | Role |
|------|------|
| `src/frontend/snocone/snocone_lower.c` | RPN → STMT_t IR — add control-flow + pattern lowering |
| `src/frontend/snocone/snocone_lower.h` | API header |
| `src/frontend/snocone/snocone_parse.c` | Postfix token stream — control-flow tokens already present |
| `src/driver/scrip.c` | `lang_snocone` dispatch — may need `sc_execute_program` wrapper |
| `test/beauty-sc/` | 14 subsystem drivers + .ref files — the gate |

---

## Steps

### Phase 1 — Control flow lowering

- [ ] **SC-1** — Emit `procedure` / `DEFINE` STMT_t from `SNOCONE_KW_PROCEDURE`.
  Lower `procedure name(a, b, ...) { body }` into:
  a DEFINE call + a labelled block of STMT_t ending with FRETURN/NRETURN.
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh stack trace` PASS.

- [ ] **SC-2** — Emit `if/else` control flow STMT_t.
  Lower `if (cond) { T } else { F }` into cond-stmt with S/F gotos + synthetic labels.
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh counter` PASS.

- [ ] **SC-3** — Emit `while` / `for` loop STMT_t.
  Lower `while (cond) { body }` and `for (init; cond; step) { body }` into
  labelled goto loops matching the SNOBOL4 statement model.
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh arith roman` PASS.

- [ ] **SC-4** — Emit `return` / `freturn` / `nreturn` STMT_t.
  Lower each to a STMT_t with goto RETURN/FRETURN/NRETURN labels per SNOBOL4 convention.
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh semantic` PASS.

---

### Phase 2 — Pattern match via bb_broker BB_SCAN

- [ ] **SC-5** — Lower `subject ? pattern` to STMT_t subject/pattern fields.
  In snocone_lower: detect `SNOCONE_QUESTION` in statement (binary, top-level) →
  pop pattern expr, pop subject expr → `st->subject = subj; st->pattern = pat;`.
  The existing `stmt_exec` Phase 3 + `bb_broker(BB_SCAN)` (U-9) handles the rest.
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh match` PASS.

- [ ] **SC-6** — Lower conditional capture `.` and immediate capture `$` in pattern context.
  `E_CAPT_COND_ASGN` and `E_CAPT_IMMED_ASGN` already exist in the IR.
  Verify `stmt_exec` interprets them correctly under `--interp`.
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh strings` PASS.

---

### Phase 3 — Remaining subsystems + full gate

- [ ] **SC-7** — Fix ReadWrite (I/O: INPUT / OUTPUT keyword handling in sc context).
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh ReadWrite` PASS.

- [ ] **SC-8** — Fix remaining subsystems (ShiftReduce, tree).
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh ShiftReduce tree` PASS.

- [ ] **SC-9** — Full gate: all 14 beauty-sc subsystems PASS.
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh arith assign strings match roman stack trace counter fence global semantic ReadWrite ShiftReduce tree` → 14/14 PASS.
  Also: `make scrip` clean; SNOBOL4 regression PASS=156 non-regressing; Icon --interp PASS=48/59 non-regressing.

---

## Invariants

- Every step leaves `make scrip` clean (zero errors, zero warnings).
- SNOBOL4 regression baseline PASS=156 must not drop.
- Icon --interp baseline PASS=48/59 must not drop.
- Do not modify `execute_program` / `stmt_exec` for Snocone-specific cases —
  Snocone IR must work through the existing shared interpreter unchanged.
- Synthetic label names use prefix `_sc_` to avoid collision with user labels.

---

## Current state (session 2026-04-13, SCRIP HEAD 94c06c46)

Baseline: 3/14 beauty-sc PASS (assign, fence, global).
Root cause: snocone_lower skips all control-flow tokens; no subject?pattern lowering.
Next session starts at **SC-1** (procedure / DEFINE lowering).

---

## Updated state (session 2026-04-13, SCRIP HEAD dc221b2b)

SC-1 partial — struct lowering done, _builtin_DATA wired in scrip.c.
- do_struct() in snocone_cf.c: 'struct name { f1,f2 }' → DATA('name(f1,f2)') STMT_t
- _builtin_DATA in scrip.c calls DEFDAT_fn(spec); registered via register_fn

BLOCKER: field accessors (x(p)) fail — FNCEX_fn('x') returns 0 for post-DEFDAT names;
APPLY_fn path not reached. Fix: in interp_eval E_FNC, when no body label exists,
call APPLY_fn unconditionally (remove/bypass FNCEX_fn gate at line ~1766 scrip.c).

**Next session: fix FNCEX_fn gate.** Search for `FNCEX_fn(e->sval)` in scrip.c,
remove the guard so APPLY_fn is always called when no body label found.
Gate: `./scrip --interp /tmp/test_struct2.sc` → outputs 3 and 4.
Then: beauty-sc stack/trace/counter/arith improving from 3/14 baseline.

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_scrip.sh
```

---

## Session state (2026-04-14, SCRIP HEAD 04082b69)

Changes landed:
- scrip.c: snocone dispatch → snocone_cf_compile (control-flow lowering active)
- snocone_cf.h: fix scrip_cc.h include path
- scrip.c: ScDatType registry (sc_dat_register/find_type/find_field/construct/field_get)
- scrip.c: _builtin_DATA calls sc_dat_register after DEFDAT_fn
- scrip.c: _builtin_print (output_val per arg), registered as 'print'
- scrip.c: DATA constructor/field-accessor intercept in E_FNC before APPLY_fn

BLOCKER for SC-1: do_struct emits DATA call as bare STMT_t subject.
The stmt has no goto — if _builtin_DATA returns FAILDESCR the interp silently
skips forward on the fail branch, so sc_dat_register is never called.
Verified: DATA('...') called as expression works fine; print() works;
Point(3,4) succeeds when struct registers correctly (confirmed by placing
DATA call inline in .sc source).

Next session fix (SC-1):
  In do_struct (snocone_cf.c), after prog_append(st, s) for the DATA stmt,
  ensure it cannot silently fail. Two options:
  (a) Wire the DATA STMT_t go->onfailure = "FRETURN" so failure is loud, OR
  (b) In _builtin_DATA, always return NULVCL (never FAILDESCR).
  Option (b) is simplest and correct — DATA() in SNOBOL4 never fails on valid spec.
  Then confirm sc_dat_register is called, run beauty-sc stack/trace gate.

---

## Session state (2026-04-14, SCRIP HEAD f6c3a97b)

Score: 6/14 PASS (assign fence roman semantic stack counter). Was 3/14 at session start
(the test script path bug masked true baseline — test_beauty_snocone_subsystems.sh SCRIPT_DIR
was pointing at scripts/ instead of test/beauty-sc/).

Fixes landed this session:
1. snocone_lower.c PERIOD: unary . → E_NAME(E_VAR) — eliminates all stack underflows on .var
2. snocone_lower.c TILDE: ~ → E_NOT() node — fixes Error 5 on ~DIFFER() inside procedures
3. scrip.c sc_dat_construct: union clobber fix — r.s=NULL was overwriting r.u=inst
4. scrip.c _usercall_hook: sc_dat constructor/field lookup added before label search
5. scripts/test_beauty_snocone_subsystems.sh: SCRIPT_DIR path fixed

Remaining failures — root causes identified:

| Subsystem | Root cause |
|-----------|-----------|
| tree | MakeNode: array field (kids) round-trip — c(nd)[1] subscript on DATA array field |
| ShiftReduce | Reduce 2/3 children: same array-field subscript issue |
| arith | IsPrime(17)/Sieve(20): while loop with integer iteration — investigate |
| strings | TrimLeft/TrimRight/Trim: SPAN/BREAK pattern functions not wired in sc context |
| match | ANY/notmatch: pattern wiring (SC-5 not yet done) |
| trace | T8Pos / t8MaxLast: table field access or TABLE() not wired |
| global | Error 3 erroneous array/table ref on statements 30-31 |
| ReadWrite | Empty output — I/O builtins (Read/Write) not wired in sc context |

## Session state (2026-04-14, SCRIP HEAD 16457e83)

Score: 8/14 PASS (assign fence roman stack counter semantic tree ShiftReduce). Was 6/14.

Two bugs fixed:

Bug 1 — snocone_lower.c SNOCONE_ARRAY_REF:
E_IDX node was built with only index children; base expression discarded (stored as sval
only, never as a child). interp_eval E_IDX evaluated the index as the base and found no
children[1], returning FAILDESCR silently. Fix: preserve full base expr as children[0];
indices as children[1+]. Both rvalue reads and lvalue writes now work.

Bug 2 — snocone_parse.c SNOCONE_LBRACKET:
Bare '[' not after IDENT was pushed as FRAME_GROUP instead of FRAME_ARRAY, so expr[i]
forms (c(nd)[1], f(x)[2]) were never emitted as SNOCONE_ARRAY_REF. Fix: always push
FRAME_ARRAY for '['.

Remaining failures and root causes:

| Subsystem | Root cause |
|-----------|------------|
| arith     | IsPrime/Sieve: while loop with integer iteration — investigate |
| strings   | TrimLeft/TrimRight/Trim: SPAN/BREAK pattern functions not wired in sc context |
| match     | ANY/notmatch: pattern wiring (SC-5 not yet done) |
| trace     | T8Pos / t8MaxLast: table field access or TABLE() not wired |
| global    | Error 3 erroneous array/table ref on statements 30-31 |
| ReadWrite | Empty output — I/O builtins (Read/Write) not wired in sc context |

Next session starts at SC-1 continued:
  Fix arith: IsPrime(17) and Sieve(20) fail — while loop with integer index.
  Investigate: does while(i <= n) work when i is DT_I? Check LE operator in sc context.
  Gate: beauty-sc arith PASS.
