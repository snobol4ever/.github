# HANDOFF — 2026-06-29 — Sonnet 4.6 — IR enum analysis + no-regression keep-set derivation

## SCRIP HEAD: d0046704 — no code changes this session
## .github HEAD: this doc — pending push

---

## Session arc

Orientation from scratch (PLAN.md, RULES.md, GOAL-IR-IMMUTABLE-EMIT.md, all six today's handoffs,
JCON ir.icn/irgen.icn/gen_bc.icn, full IR.h scan, emit_x86_drive.c switch).
Build verified: scrip + libscrip_rt built, PASS=86/86/86 all three modes, gate HARD=4.

Session was entirely analysis — produced two reference grids and the authoritative no-regression
keep-set for the next enum amputation. No commits to SCRIP.

---

## What was produced

### Grid 1 — JCON IR record → SCRIP IR_* + variance
Maps every JCON ir.icn record type to its SCRIP realization. Key findings:
- `ir_OpFunction` (ONE record) fans to **25 SCRIP opcodes** — the headline bloat; B2 fold target
- `ir_Call` (ONE record) fans to **9 SCRIP opcodes** — the F2/B4 target (4 remaining gate mutations)
- `ir_Var`/`ir_Assign` fan by storage class (×3 each) — eliminate with slot discipline
- `ir_ScanSwap` fans to **10 SCRIP opcodes** — D2 target
- `ir_Create`/`ir_CoRet`/`ir_CoFail`/`ir_Unreachable`/`ir_Invocable`/`ir_Link` — MISSING (C-track)
- `ir_Tmp` — realized as `IR_t.tmp` int field on producer, NOT a node (by design, confirmed correct)
- `ir_ResumeValue` — no node; β resume port (ω/β-wiring, B3 confirmed)
- `ir_Suspend` — maps to `ir_Succeed(resumeLabel)` in JCON (no Suspend record); SCRIP's IR_SUSPEND
  should collapse into IR_SUCCEED+β path

### Grid 2 — SCRIP IR_* with no JCON record, categorized
- **C (control — legitimate permanent divergence):** IR_IF, IR_EVERY, IR_WHILE, IR_UNTIL, IR_REPEAT,
  IR_TO, IR_TO_BY, IR_SUSPEND, IR_ALT, IR_REPALT, IR_LIMIT, IR_CASE, IR_CASE_ARM, IR_CONJ,
  IR_SEQ, IR_SEQ_EXPR, IR_BREAK, IR_NEXT, IR_INTERROGATE — JCON lowers these to Goto/Succeed
  chunk streams; SCRIP keeps as opcodes + γ/ω/β edge threading. KEEP + grow driver ownership.
- **F (fan — delete targets):** IR_BINOP_{ARITH,RELOP,CONCAT,GVAR_*}, IR_UNOP_GVAR_SLOT,
  IR_NEG/POS/SIZE/NONNULL/NULL_TEST, IR_CSET_*, IR_IDX, IR_SECTION, IR_LIST_BANG, IR_LCONCAT,
  IR_INTERROGATE, IR_FIELD_{GET,SET}, IR_KEY_GEN, IR_SCAN_*, IR_GEN_SCAN, IR_VAR_FRAME*,
  IR_ASSIGN_FRAME*, IR_CALL_{DEFINE,PROC_STAGED,USERPROC,BYNAME,BUILTIN,GVAR_USERPROC},
  IR_PROC_GEN, IR_CALLEE_FRAME — collapse toward JCON primitives.
- **D (dead accretion — delete):** IR_UPTO, IR_ITERATE, IR_GEN_ALT, IR_TO_NESTED, IR_FIND_GEN,
  IR_SEQ_GEN, IR_GATHER — never produced live.

### Authoritative no-regression keep-set (empirically derived)

Method: ran ALL 1317 corpus Icon programs under `--run` (mode-3), collected the 181 that pass,
ran `--dump-ir` over each, took the union. Separately identified emit-fan targets (ops written
into `nd->op` by `resolve_call_kinds_descr` at emit time) and structural chain-builder ops
(`IR_ALT` branched in `codegen_flat_chain_body`).

**25 keep opcodes + IR_OP_COUNT sentinel:**

Lower-produced by the 181 green programs (17):
  IR_LIT_I  IR_LIT_S  IR_LIT_F  IR_VAR  IR_KEYWORD  IR_ASSIGN  IR_BINOP  IR_NOT
  IR_CALL  IR_TO  IR_EVERY  IR_CONJ  IR_ALT  IR_IF  IR_SUCCEED  IR_FAIL  IR_RETURN

Emit-fanned into nd->op at emit time (3):
  IR_CALL_BUILTIN  IR_CALL_PROC_STAGED  IR_PROC_GEN

Call variants in the keep-27 driver switch, needed for user-proc + byname calls (3):
  IR_CALL_USERPROC  IR_CALL_BYNAME  IR_CALL_GVAR_USERPROC

Structural / compile-required (2):
  IR_GOTO  IR_SEQ

**69 delete opcodes (the complement of the above in the current 94-member enum):**
IR_LIT_NUL IR_UNOP IR_NEG IR_POS IR_SIZE IR_NONNULL IR_NULL_TEST IR_TO_BY IR_WHILE IR_UNTIL
IR_REPEAT IR_REPALT IR_LIMIT IR_SUSPEND IR_PROC IR_INTERROGATE IR_CALLEE_FRAME IR_UPTO
IR_ITERATE IR_GEN_ALT IR_TO_NESTED IR_BREAK IR_NEXT IR_CSET_COMPL IR_CSET_UNION IR_CSET_DIFF
IR_CSET_INTER IR_GEN_SCAN IR_IDX IR_SECTION IR_LIST_BANG IR_RECORD_DEF IR_FIELD_GET IR_FIELD_SET
IR_IDX_SET IR_KEY_GEN IR_SWAP IR_RASGN IR_SEQ_EXPR IR_INITIAL IR_LCONCAT IR_FIND_GEN IR_SEQ_GEN
IR_GATHER IR_BINOP_RELOP IR_BINOP_ARITH IR_BINOP_GVAR_ARITH IR_BINOP_GVAR_RELOP
IR_BINOP_GVAR_ARITH_SLOT IR_UNOP_GVAR_SLOT IR_BINOP_CONCAT IR_BINOP_GVAR_CONCAT IR_SCAN_ANY
IR_SCAN_MANY IR_SCAN_MATCH IR_SCAN_UPTO IR_SCAN_FIND IR_SCAN_BAL IR_SCAN_TAB IR_SCAN_MOVE
IR_SCAN_POS IR_VAR_FRAME IR_ASSIGN_FRAME IR_VAR_FRAME_REF IR_ASSIGN_FRAME_REF IR_CALL_DEFINE
IR_GOTO_DYN IR_ALT(NOTE: keep — was incorrectly in delete-set in mid-session analysis)

NOTE on IR_LIT_NUL: in the keep-27 driver switch but NOT in the 181-green produce-set; include
in keep if the driver owns it (zero cost to keep), delete if closing to strict-green-only.

---

## What was attempted and reverted

An IR.h strict-27 cut was made and reverted in the same session (before commit).
The revert was clean: `git checkout src/contracts/IR.h src/contracts/scrip_ir.c`.
SCRIP tree is at clean HEAD d0046704. No damage.

---

## Next session entry point

Execute the 69-delete amputation using the keep-set above:
1. Edit IR.h enum to the 25-keep + IR_OP_COUNT
2. Edit scrip_ir.c (designated-init tables) in lockstep
3. `make scrip` — capture the full compiler break list
4. Chase each break site: delete dead case-labels / dead lower arms /
   dead template switch arms in emit_bb.c, lower_icon.c, emit_core.c,
   ir_query.c, scrip.c
5. Build green, run suite, verify PASS >= 181
6. Commit + push

Key notes for the next session executor:
- IR_ALT: lower-produced (green set), structural branch in codegen_flat_chain_body → KEEP
- IR_IF: lower-produced (green set) → KEEP (not in driver switch, edge-threaded by design)
- IR_GOTO: structural (chain builder loop termination) → KEEP
- IR_SEQ: structural (chain builder seq-pair detection) → KEEP
- IR_LIT_NUL: in driver switch but not produced by green set — judgment call; recommend KEEP
  (zero cost, avoids a silent regression if any program uses &null literal path)
- The strict-27 driver-switch list: IR_LIT_S IR_LIT_I IR_LIT_F IR_LIT_NUL IR_KEYWORD IR_VAR
  IR_BINOP IR_UNOP IR_NEG IR_POS IR_NONNULL IR_NULL_TEST IR_SIZE IR_NOT IR_ASSIGN IR_CALL
  IR_CALL_BUILTIN IR_CALL_PROC_STAGED IR_CALL_USERPROC IR_CALL_BYNAME IR_CALL_GVAR_USERPROC
  IR_TO IR_EVERY IR_CONJ IR_SUCCEED IR_FAIL IR_RETURN

IMPORTANT: IR_UNOP/IR_NEG/IR_POS/IR_SIZE/IR_NONNULL/IR_NULL_TEST are in the driver switch
but NOT in the green produce-set. They ARE in the keep-set (driver owns them) but deleting
them would only regress programs that currently FAIL (drive_unowned aborts). Safe to delete
per the "let it go to zero and grow back" mandate, but confirm against the full corpus first.

Recommended: keep ALL driver-switch members (strict-27) PLUS the structural/emit-fan members
(IR_GOTO, IR_SEQ, IR_IF, IR_ALT, IR_PROC_GEN). That gives a 32-member keep-set which
is cleanly conservative, zero regression risk, and still cuts 62 of the 69 targets.

---

## Gate and suite at session end (unchanged from session start)

Mutation gate: HARD=4 (4 ->op writes in resolve_call_kinds_descr)
Suite: PASS=86/289 interp, PASS=86/289 run, PASS=86/289 compile (with libscrip_rt built)
Corpus green: 181 programs pass --run across the full 1317-program icon corpus
