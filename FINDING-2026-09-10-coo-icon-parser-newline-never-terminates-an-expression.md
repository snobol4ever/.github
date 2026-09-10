# FINDING 2026-09-10 coo — the Icon parser has NO newline statement termination; every graded Icon program happens to carry semicolons

Filed 2026-09-10 08:34 CDT by the coo while diagnosing ipl chkhtml (CEO-483). Not the chkhtml divergence; a separate, older class, named here for the ceo to route. NOT a fresh regression: every seat's built binary (twelve roots, heads from ded51d003 to edb1a8f69) rejects the same two-line program, and the lexer's own unit test PINS the behaviour ("no auto-semicolon on newline", icon_lex_test.c ~line 350).

## THE WITNESS (valid Icon; icont accepts it; SCRIP refuses it)

    procedure main()
      write("a")
      write("b")
    end

SCRIP, every seat, both modes: icon: parse error in v7.icn: line 3: expression statement: expected ; (got IDENT). Same for x := 1 / write(x) and for every newline-separated pair. Icon's rule (Griswold, The Icon Programming Language, section on syntax): a newline terminates an expression when the token before it can END an expression and the token after it can BEGIN one. SCRIP's icon_lex.c has no such rule (skip_ws eats the newline like a space; icn_lex_next is a bare lex_one call), and icon_parse.c's parse_stmt demands TK_SEMICOL unless the next token is }, end, else, then, return, suspend, EOF, or the previous token was }.

## WHY THE BOARD NEVER SAW IT

Every Icon program the board grades carries semicolons. Measured: 0 of the IPL progs/*.icn are semicolon-free (each has at least a local declaration line ending in ;), the Arizona and Jcon tests are Griswold's semicolon style throughout, and the master ALL.icn entries are written in the same style. The single IPL site with the bare shape found by a narrow scan (xtable.icn lines 46-51, a Usage block of write() lines) sits in a program that is not graded green today. So the gap is real and unmeasured, not absent.

## WHAT IT COSTS

Any hand-written Icon that relies on newline termination (the normal Icon style outside Griswold's test suites) refuses at parse. It is invisible to every runner and gate because the population was written to the parser, not the language. The lexer test that pins the wrong behaviour will red when the cure lands and must be re-decided, not kept.

## THE SHAPE OF A CURE (named, not taken — not this seat's row)

In icon_lex.c: track the previous token kind; when skip_ws crosses a newline and prev can end an expression (IDENT, literal, ), ], }, a keyword like fail/next/break, &keyword) and the next token can begin one (icn_begins_nexpr in icon_parse.c already lists these), emit TK_SEMICOL once. The continuation rule must stay: a line ending in an operator or comma continues. Then re-pin the lexer test. Every suite is a control arm: no graded program should move, because every graded program already carries its semicolons; the identity gate proves it per entry.

## RELATED

The two Icon smoke probes if_expr and proc_recursion (test_smoke_icon.sh lines 85 and 137) carry "; else", which icont refuses ("else": invalid expression, measured through /home/resources/icon-master/bin/icon this session). The smoke red the cto named on edb1a8f69 (13/15 both modes) is 38470889b (refuse the four semicolons icont refuses) meeting probe text that was never valid Icon — the same population-written-to-the-parser shape as above, from the other side.

## CLOSED BY DESIGN (ceo CEO-494/495, Lon 2026-09-10 09:3x, verbatim through the ceo)

*"So you ensure that you have properly added the semi-colons to the programs checked in to the corpus repo. SCRIP does not process new-line characters as special. They are white space."* — SCRIP Icon is SEMICOLON-REQUIRED (Lon's 09-04 ruling; icont-style insertion is forbidden by gate). The parser is RIGHT to refuse `write("a")` newline `write("b")`; the corpus is what must carry the semicolons, and hq_B's row is two-sided (SCRIP parses every shipped file AND icont accepts it). The cure shape above is withdrawn; the witness stands as the record of why the vendored population reads the way it does. Recorded by the coo 2026-09-10 09:4x CDT.
