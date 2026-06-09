# lower-rebuild — WIP from-scratch per-language LOWER (pre-integration)

Five segregated lower_*.c, mirrored structure, generated from scratch off the parser + IR.h
(JCON tran/irgen.icn as the Icon guide). NOT yet wired into the SCRIP build — staged here so the
SCRIP tree stays green. Promote into SCRIP/src/lower/ at integration (collides with existing
lower_* symbols — that collision IS the integration step).

## Compile-check all five against the contracts (from a SCRIP checkout):
    INC="-I src -I src/contracts -I src/include -I src/interp -I src/machine -I src/emitter -I src/runtime"
    for f in icon pascal prolog raku snobol4; do
      gcc -c -std=gnu11 -fextended-identifiers $INC lower_$f.c -o /tmp/lower_$f.o
    done

## Icon graph-level pipeline proof (real parser -> lower_icon -> bb_print):
    INC="$INC -I src/parser/icon -I src/driver"
    gcc -c -std=gnu11 -fextended-identifiers $INC src/parser/icon/icon_lex.c   -o /tmp/icon_lex.o
    gcc -c -std=gnu11 -fextended-identifiers $INC src/parser/icon/icon_parse.c -o /tmp/icon_parse.o
    gcc -c -std=gnu11 -fextended-identifiers $INC src/contracts/scrip_ir.c     -o /tmp/scrip_ir.o
    gcc -c -std=gnu11 -fextended-identifiers $INC src/driver/stmt_ast.c        -o /tmp/stmt_ast.o
    gcc -std=gnu11 -fextended-identifiers $INC pipe_icon.c /tmp/lower_icon.o /tmp/scrip_ir.o \
        /tmp/icon_parse.o /tmp/icon_lex.o /tmp/stmt_ast.o -o /tmp/pipe_icon
    /tmp/pipe_icon
# expected: PROG -> PROC(main) -> CALL -> [VAR "write", LIT_S "hello"]
# pipe_icon.c provides `int g_jcon = 0;` to avoid pulling in the runtime.
