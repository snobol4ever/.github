# PARSER-SNOBOL4.md — SNOBOL4 Parser

**Status:** STUB — to be filled in.

## Role
Consumes token stream from LEXER-SNOBOL4 and produces the shared IR (Program*).

## Output
`Program*` — linked list of `STMT_t` nodes with `EXPR_t` trees.
This is the input to SM-LOWER (see SCRIP-SM.md).

## Files
TBD — see src/frontend/snobol4/

## References
- `LEXER-SNOBOL4.md` — input token stream
- `IR.md` — output representation
- `SCRIP-SM.md` — SM-LOWER compiles IR to SM_Program
