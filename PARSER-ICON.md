# PARSER-ICON.md — ICON Parser

**Status:** STUB — to be filled in.

## Role
Consumes token stream from LEXER-ICON and produces the shared IR (Program*).

## Output
`Program*` — linked list of `STMT_t` nodes with `EXPR_t` trees.
This is the input to SM-LOWER (see SCRIP-SM.md).

## Files
TBD — see src/frontend/icon/

## References
- `LEXER-ICON.md` — input token stream
- `IR.md` — output representation
- `SCRIP-SM.md` — SM-LOWER compiles IR to SM_Program
