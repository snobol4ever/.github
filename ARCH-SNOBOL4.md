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

## Native pattern architecture — modes 3 & 4 (pattern = built BB graph)

Added 2026-05-31 (Lon "Eureka" directive). Modes 2 (interp) is OUT OF SCOPE here; this section
governs ONLY mode 3 (`--run`, BINARY arm → RX pool) and mode 4 (`--compile`, TEXT arm → `as`/`gcc`).
Both are pure LOWER + EMITTER, no interpreter. RULES recap: the ONLY emitted thing that does work is
a **BB code block** (a byrd box) reached via `emit_core.c` dispatch; **XA blocks** only wrap/stitch
(file header/footer, flat prologue/epilogue, data/rodata, entry dispatch, pattern-blob framing). So in
modes 3/4 the ONLY vehicle to build a subject, build a pattern, or build a replacement is a **BB**.

### Five-phase statement model
A SNOBOL4 match statement `SUBJ ? PAT [= REPL]` processes in five phases, EACH emitted as BB(s):
1. **Build subject** — lower the subject value-expr → a **SUBJECT BB** that evaluates it and loads the
   locked registers `Σ` (base ptr), `δ` (cursor = 0), `Δ` (length/end). Easiest of the three builds;
   closest to existing value-box work.
2. **Build pattern** — THE KEY TURN. A SNOBOL4 pattern is a *runtime object* = a byrd-box graph (the
   "pattern data type": `P = 'a' | 'b'` *constructs*). So pattern lowering emits **builder BBs — BBs
   that build other BBs dynamically**: each pattern construct lowers to emitted code whose RUN-TIME
   EFFECT is to allocate + wire the pattern's own byrd-boxes (a LIT box, an ALT box, a CAT box, a SPAN
   box, …) into a pattern graph in memory. The built graph head lives in a `ζ`-frame slot.
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
the pattern object is constructed (builder BBs), then matched (BB_MATCH). The current mode-2 `IR_SCAN`
super-node + hidden `IR_alloc` sub-graph is the WRONG layer (re-derives topology at exec — the
`sno_ring_to_tree` anti-pattern relocated into the lowerer) and is NOT the modes-3/4 design.

### OPTIMIZATION — INVARIANT-PATTERN BAKE (second step, after correctness)
Invariance is a COMPILE-TIME property of the pattern subtree: a pattern all of whose components are
compile-time constant (literal strings/ints/csets, fixed `LEN`/`POS`/`RPOS`, constant `ALT`/`CAT` of
such) is INVARIANT. After phases 1–5 work end-to-end, collapse any MAXIMAL sequence of builder BBs that
builds an invariant pattern into a SINGLE **STATIC pattern BB graph BAKED into the generated code**
(emitted ONCE as sealed data/code), eliminating the per-execution runtime rebuild. Only builder BBs for
VARIANT components (patterns referencing runtime values — `SPAN(VAR)`, `ANY(expr)`, deferred `*EXPR`,
indirect `$NAME`) remain dynamic after the bake. Rule: const subtree ⇒ bake static; references-runtime
⇒ keep dynamic builder. This mirrors SPITBOL: constant patterns build once; variable patterns
rebuild/defer per match. See GOAL-SNOBOL4-BB.md rung SBL-PAT-BB for the step ladder.
