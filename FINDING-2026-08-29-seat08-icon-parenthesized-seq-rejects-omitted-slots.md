# FINDING 2026-08-29 seat08 — ICON PARENTHESIZED SEQUENCE EXPRESSIONS `(a,,b)`/`(,,,)` REJECT OMITTED SLOTS; LIST LITERALS ALREADY HANDLE THE IDENTICAL CASE

**Row:** `tests-consolidate-icon` (postoffice task), disposing `rung36_jcon_proto.icn` — KEEP.md (seat07, 2026-08-29) flagged its line-28 behavior as "a genuine m3-vs-m4 PARSE divergence... worth a FINDING if picked up." **That divergence is gone at current HEAD (`54161efd`)** — m3 and m4 now give byte-identical parse errors, 6/6 repeated. What's still there, confirmed against the real Icon oracle, is a parser bug independent of the mode question.

## SUMMARY

SCRIP's parser rejects an omitted (empty) expression slot inside a parenthesized comma- or semicolon-separated sequence — `(,,,)`, `(,)`, `(1,,2)` all fail with `expected expression (got ,)`. The real Icon compiler (`/home/resources/icon-master/bin/icont`, built and runnable locally) accepts all of these with **"No errors"**, and `(1,,2)` runs and evaluates to `2` (the sequence's last non-omitted value; empty slots contribute nothing and are not an error). List literals (`[1,,2]`) already support the identical omitted-slot shape in SCRIP today — this is a gap in one sibling construct, not a missing feature.

## MINIMAL REPRO

```icon
procedure main()
   write(image((1,,2)))
end
```
Real Icon (`icont`+`iconx`): compiles clean, runs, prints `2`.
SCRIP (either mode): `icon: parse error in v2.icn: line 2: expected expression (got ,)`.
Simplest form: `procedure main(); (,); end` — icont "No errors" / SCRIP same parse error, one line.

## ROOT CAUSE (precisely located, not guessed)

`src/frontend/icon/icon_parse.c`, the `(`-handling arm of `parse_primary` (lines 124-151). After the empty-parens special case (`()` → `TT_SEQ_EXPR`, line 126, which already works), the very next line unconditionally calls the general expression parser for the first slot:
```c
tree_t *first = parse_expr(p);                 // line 127 -- no comma/semicolon check first
```
and both loop bodies do the same for every subsequent slot:
```c
push_child(seq, parse_expr(p));                 // line 134 (semicolon form), line 145 (comma form)
```
None of the three call sites checks whether the *next* token is itself a separator (or `)`) before recursing into `parse_expr`, so a bare comma with nothing before it has no path except falling through to `parser_error(p, "expected expression")` at line 192.

**The identical case is already solved four lines later, for `[...]` list literals** (lines 153-165):
```c
if (!check(p, TK_RBRACK)) {
    if (check(p, TK_COMMA)) push_child(lst, ast_node_new(TT_NUL));   // line 157 -- the missing check
    else push_child(lst, parse_expr(p));
    while (check(p, TK_COMMA)) {
        advance(p);
        if (check(p, TK_RBRACK)) { push_child(lst, ast_node_new(TT_NUL)); break; }
        if (check(p, TK_COMMA)) { push_child(lst, ast_node_new(TT_NUL)); continue; }
        push_child(lst, parse_expr(p));
    }
}
```
Every slot is checked for "is the next token a separator/closer" before calling `parse_expr`, inserting a `TT_NUL` placeholder node when so. The parenthesized-sequence arm never got this same three-call-site treatment. Confirmed via `--dump-ast` that `[,]` already produces a `TT_NUL` child on SCRIP today — the placeholder AST shape being reused is not new capability, just not wired into the sibling construct.

## IMPACT

Corpus-wide: grepped `tests/icon/*.icn` for a bare `(...,...)`-with-adjacent-commas shape — `rung36_jcon_proto.icn` (this file) is the only witness this session found; did not survey `coverage/`, `frontend/`, `samples/`, or standalones. Likely narrow in the current test tree (V9GEN-style syntax-kitchen-sink files are rare), but the construct is legal, oracle-confirmed Icon and any real program using it would hit the same wall.

## DISPOSITION

Not fixed here — parser change, out of `tests-consolidate-icon`'s lane (characterize, route, leave loose, same disposition this task family gives every compiler-bug witness). `rung36_jcon_proto.icn` stays loose, not KEEP.md'd (bug, not permanent design choice). The original m3-vs-m4 divergence this file was flagged for no longer reproduces (6/6 identical across both modes, current HEAD) — record that as resolved separately from this parser gap. Mailed to hq_C as `icon-paren-seq-omitted-slot` (parser correctness, hq_C's lane per this task family's standing convention).
