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
one4all returns uppercase (`"NAME"`, `"PATTERN"`).
This is intentional per SNOBOL4 spec. `.ref` files use uppercase.

## Monitor hooks (in snobol4.c)

```c
comm_var(name, val)     // emit VALUE trace event to monitor_fd, block on monitor_ack_fd
comm_stno(n)            // increment kw_stcount, fire error 22 if kw_stlimit exceeded
trace_is_active(name)   // 1 if name is in trace_set[]
monitor_fd              // from MONITOR_READY_PIPE env var
monitor_ack_fd          // from MONITOR_GO_PIPE env var
```
