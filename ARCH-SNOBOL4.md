# ARCH-SNOBOL4.md — SNOBOL4 Frontend

Frontend: SNOBOL4. Produces shared IR (EXPR_t/STMT_t). See ARCH-IR.md.

## Parser

`src/frontend/snobol4/CMPILE.c` — single-file SIL-faithful parser.
Public API: `cmpile_init`, `cmpile_file`, `cmpile_string`, `cmpile_free`.
Parse node type: `CMPND_t`. Statement type: `CMPILE_t`.

Key SIL procedures (implemented in CMPILE.c):
- `CMPILE` — top-level statement parser
- `ELEMNT` / `EXPR` / `EXPR_PREC` — expression parsing
- `FORWRD` / `FORBLK` / `FORRUN` — continuation handling (true streaming, no linebuf)
- `STREAM` — 6-arg: `STREAM out, in, table, error_branch, eos_branch, stop_branch`
- `IBLKTB` / `FRWDTB` — action tables

## Streaming model

True streaming — no linebuf pre-join. TEXTSP = one physical line.
FORWRD/FORBLK call FORRUN on ST_EOS to fetch the next card.
STREAM returns: ST_ERROR→arg4, ST_EOS→arg5, ST_STOP→arg6.

## Operator table names (SIL → CMPILE)

| SIL | CMPILE | Meaning |
|-----|--------|---------|
| ADDFN | ADDFN | + |
| SUBFN | SUBFN | - |
| MPYFN | MPYFN | * |
| DIVFN | DIVFN | / |
| EXPFN | EXPFN | ** |
| ORFN | ORFN | alternation `\|` |
| CATFN | CATFN | concatenation |
| BIQSFN | BIQSFN | binary `?` |
| EQTYP | EQTYP | = (assignment) |

## Runtime

Key files:
- `src/runtime/snobol4/snobol4.c` — builtins, keywords, TRACE, monitor hooks
- `src/runtime/snobol4/stmt_exec.c` — 5-phase statement executor
- `src/runtime/snobol4/invoke.c` — INVOKE_fn / APPLY_fn dispatch
- `src/runtime/snobol4/argval.c` — VARVAL_fn, INTVAL_fn, PATVAL_fn
- `src/runtime/snobol4/snobol4_nmd.c` — NAM_push/save/commit/discard

## DATATYPE convention

SPITBOL returns lowercase (`"name"`, `"pattern"`).
SCRIP returns uppercase (`"NAME"`, `"PATTERN"`).
This is intentional per SNOBOL4 spec. `.ref` files use uppercase.

## Monitor hooks (in snobol4.c)

```c
comm_var(name, val)     // emit VALUE trace event to monitor_fd, block on monitor_ack_fd
comm_stno(n)            // increment kw_stcount, fire error 22 if kw_stlimit exceeded
trace_is_active(name)   // 1 if name is in trace_set[]
monitor_fd              // from MONITOR_READY_PIPE env var
monitor_ack_fd          // from MONITOR_GO_PIPE env var
```

## Native pattern architecture — modes 3 & 4 (pattern = graph of emitted byrd-boxes, `bb_box_fn`)

Added 2026-05-31 (Lon "Eureka"); CORRECTED 2026-06-01 (Lon): the built pattern is a graph of EMITTED
BYRD-BOXES (`bb_box_fn`) driven by `bb_broker.c`, NOT a `PATND_t` and NOT a `tree_t`. See
GOAL-SNOBOL4-BB.md "CORRECTED PATTERN ARCHITECTURE" for the full statement + decided forks.
Modes 1 (AST interp) and 2 (IR interp) are DELETED (long gone — see PLAN.md Architecture + GOAL-MODE34-IDENTICAL.md); this section governs the only two modes that exist: mode 3 (`--run`, BINARY arm → RX pool) and
mode 4 (`--compile`, TEXT arm → `as`/`gcc`). Both are pure LOWER + EMITTER, no interpreter. RULES recap: the ONLY emitted thing that does work is
a **BB code block** (a byrd box) reached via `emit_core.c` dispatch; **XA blocks** only wrap/stitch
(file header/footer, flat prologue/epilogue, data/rodata, entry dispatch, pattern-blob framing). So in
modes 3/4 the ONLY vehicle to build a subject, build a pattern, or build a replacement is a **BB**.

### Five-phase statement model
A SNOBOL4 match statement `SUBJ ? PAT [= REPL]` processes in five phases, EACH emitted as BB(s):
1. **Build subject** — lower the subject value-expr → a **SUBJECT BB** that evaluates it and loads the
   locked registers `Σ` (base ptr), `δ` (cursor = 0), `Δ` (length/end). Easiest of the three builds;
   closest to existing value-box work.
2. **Build pattern** — THE KEY TURN. A SNOBOL4 pattern is a *runtime object* = a graph of EMITTED
   BYRD-BOXES (`bb_box_fn` machine code in the RX pool), driven by `bb_broker.c` four-port (`α/β/γ/ω`) —
   the SAME broker that drives Icon generators and Prolog goals. It is NOT a `PATND_t` data structure
   (that redundant runtime pattern-IR is being demolished) and NOT a `tree_t` (AST is for EVAL/CODE only —
   they compile a runtime *source string*; a pattern's structure is known at COMPILE time). The pattern
   ELEMENTS *are* byrd-boxes — the EXISTING `IR_PAT_*` matcher templates (`bb_lit`, `bb_pat_span`,
   `bb_pat_alt`, `bb_pat_cat`, `bb_pat_len`, …). Construction has two cases, decided by COMPILE-TIME
   invariance of each subtree:
   - **Invariant subtree** (literal, fixed `LEN`/`POS`, ALT/CAT of invariants) → emitted + port-wired at
     COMPILE time; referenced at runtime by a **`REF_INVARIANT`** box that loads the sealed `bb_box_fn` head
     (RO `[rip+disp]`/movabs) into a `ζ`-slot. A FULLY-invariant pattern (most patterns) costs only this one
     box — NO runtime construction.
   - **Variant subtree** (operand-variant `LEN(N)`/`SPAN(cvar)`, or structural-variant `*E`/`$NAME`/
     pattern-valued var) → for OPERAND variance the sealed element matcher reads its operand late from a
     `ζ`-slot (operand-binding, no builder box); for STRUCTURAL variance a **`BB_PAT_BUILD`** box SPLICES
     (wires ports of) the runtime box-graph and **STITCH_SEQ/STITCH_ALT** boxes wire it to the sealed pieces.
   `STITCH_SEQ`/`STITCH_ALT` are the runtime twins of LOWER's `wire_seq`/`wire_alt` (same port equations,
   one layer down): they wire box-INSTANCE records whose `code` field points at the sealed element matchers,
   so STITCH never repoints sealed interior jumps. The built/sealed graph head (a `bb_box_fn`) lives in a
   `ζ`-frame slot and IS the pattern's **`DT_P`** value (the `descr.h` `.p` slot, reborn as a box-graph head).
   **SEAL at element granularity, WIRE at instance level.**
3. **Run pattern** — control enters the generic **BB_MATCH box**, which takes the built pattern graph +
   the subject (`Σ`/`δ`/`Δ`) and runs the SPITBOL ch.18 scanner over it: the unanchored starting-cursor
   loop (advance start unless `&ANCHOR`; ch.18 step 6) wrapping the pattern's four-port (`α/β/γ/ω`)
   backtracking. ALL backtracking is carried by the four-port topology — NO value stack (FACT RULE).
4. **Build replacement** (only if `= REPL`) — lower the replacement value-expr → a **REPLACEMENT BB**.
   CAN fail (e.g. a failing conditional in the replacement expr).
5. **Do replace** — a **SUBSTITUTION BB**: requires the subject be an LVALUE — FAILS for a literal/number
   subject (`"hello"`, `99`). Splice `Σ[0:m_start] + repl + Σ[m_end:]` and assign back to the subject.

### Build/run split is real
Phase 2 (build) and phase 3 (run) are GENUINELY SEPARATE steps, matching SNOBOL4 first-class patterns:
the pattern object is constructed (REF_INVARIANT / BB_PAT_BUILD / STITCH boxes — or, for a fully-invariant
pattern, just sealed at compile time and referenced), then matched (BB_MATCH drives the box-graph via the
broker). (Historical note: the old mode-2 `IR_SCAN` super-node + hidden `IR_alloc` sub-graph re-derived
topology at exec — the `sno_ring_to_tree` anti-pattern relocated into the lowerer — and was the WRONG layer.
Mode 2 is DELETED, so that path is gone; the native build/run chain above is the only design.)

### OPTIMIZATION — ALL-INVARIANT BLOB FREEZE (second step, after correctness)
Invariance is a COMPILE-TIME property of the pattern subtree: a pattern all of whose components are
compile-time constant (literal strings/ints/csets, fixed `LEN`/`POS`/`RPOS`, constant `ALT`/`CAT` of
such) is INVARIANT. The BASELINE mechanism wires even invariant patterns at the instance level (an
invariant leaf's sealed element `code` becomes an instance's `code`); correctness first. The OPTIMIZATION:
when a pattern is FULLY invariant, collapse its REF_INVARIANT + STITCH sequence into ONE sealed `bb_box_fn`
BLOB emitted ONCE at compile time (the wiring frozen to direct jumps, no ε-nodes, no runtime stitch);
`REF_INVARIANT` hands MATCH that sealed head directly. Only variant components (`*E`, `$NAME`,
pattern-valued var) keep runtime build+stitch. Rule: const subtree ⇒ freeze to a sealed BLOB;
references-runtime ⇒ keep instance-wired/built. This mirrors SPITBOL: constant patterns build once;
variable patterns rebuild/defer per match. See GOAL-SNOBOL4-BB.md rung PB-RB for the step ladder.

## Storage & call convention (pointer, 2026-07-11)
ζ storage design of record: `ARCH-ZETA-LOCAL-STORAGE.md` §7 (two MM flavors, regions, register end-state). Call convention: the ONE-ENTRY / NO-C→BB rule — mode 3 has exactly one C→BB transfer (driver MAIN); C runtime helpers are strict leaves; mode 4 entry is `main` (= the emitted graph). Live rung ladder + violation ledger: `GOAL-SNOBOL4-BB.md` Phase 1 (NCB).
