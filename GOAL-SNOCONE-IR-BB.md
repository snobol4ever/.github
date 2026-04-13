# GOAL-SNOCONE-IR-BB.md — Snocone IR Interpreter + BB Broker

**Repo:** one4all
**Done when:** All 14 Snocone beauty-sc subsystems PASS under `scrip --ir-run`,
including pattern match (`subject ? pattern`) wired through `bb_broker(BB_SCAN)`.

---

## Motivation

Snocone compiles to the shared IR (EXPR_t / STMT_t) via `snocone_compile()`.
The `--ir-run` path calls `execute_program(prog)` — the SNOBOL4 interpreter — which
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
  Verify `stmt_exec` interprets them correctly under `--ir-run`.
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh strings` PASS.

---

### Phase 3 — Remaining subsystems + full gate

- [ ] **SC-7** — Fix ReadWrite (I/O: INPUT / OUTPUT keyword handling in sc context).
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh ReadWrite` PASS.

- [ ] **SC-8** — Fix remaining subsystems (ShiftReduce, tree).
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh ShiftReduce tree` PASS.

- [ ] **SC-9** — Full gate: all 14 beauty-sc subsystems PASS.
  Gate: `bash test/beauty-sc/run_beauty_sc_subsystem.sh arith assign strings match roman stack trace counter fence global semantic ReadWrite ShiftReduce tree` → 14/14 PASS.
  Also: `make scrip` clean; SNOBOL4 regression PASS=156 non-regressing; Icon ir-run PASS=48/59 non-regressing.

---

## Invariants

- Every step leaves `make scrip` clean (zero errors, zero warnings).
- SNOBOL4 regression baseline PASS=156 must not drop.
- Icon ir-run baseline PASS=48/59 must not drop.
- Do not modify `execute_program` / `stmt_exec` for Snocone-specific cases —
  Snocone IR must work through the existing shared interpreter unchanged.
- Synthetic label names use prefix `_sc_` to avoid collision with user labels.

---

## Current state (session 2026-04-13, one4all HEAD 94c06c46)

Baseline: 3/14 beauty-sc PASS (assign, fence, global).
Root cause: snocone_lower skips all control-flow tokens; no subject?pattern lowering.
Next session starts at **SC-1** (procedure / DEFINE lowering).

---

## Updated state (session 2026-04-13, one4all HEAD dc221b2b)

SC-1 partial — struct lowering done, _builtin_DATA wired in scrip.c.
- do_struct() in snocone_cf.c: 'struct name { f1,f2 }' → DATA('name(f1,f2)') STMT_t
- _builtin_DATA in scrip.c calls DEFDAT_fn(spec); registered via register_fn

BLOCKER: field accessors (x(p)) fail — FNCEX_fn('x') returns 0 for post-DEFDAT names;
APPLY_fn path not reached. Fix: in interp_eval E_FNC, when no body label exists,
call APPLY_fn unconditionally (remove/bypass FNCEX_fn gate at line ~1766 scrip.c).

**Next session: fix FNCEX_fn gate.** Search for `FNCEX_fn(e->sval)` in scrip.c,
remove the guard so APPLY_fn is always called when no body label found.
Gate: `./scrip --ir-run /tmp/test_struct2.sc` → outputs 3 and 4.
Then: beauty-sc stack/trace/counter/arith improving from 3/14 baseline.
