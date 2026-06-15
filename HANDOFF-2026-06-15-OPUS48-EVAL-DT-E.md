# HANDOFF — EVAL(STRING) as DT_E expression datatype (2026-06-15, Opus 4.8)

## Status: DONE + pushed (SCRIP `cf50707`), gates green. ONE follow-up flagged by Lon.

EVAL now works like the DT_P pattern datatype, but emits a **DT_E expression**
datatype: STRING → parser → AST → IR → `bb_box_fn`. **No interpreter** anywhere
on the path (`eval_node` stays bombed; nothing walks `tree_t` at runtime).

### Probes — m3 ≡ m4 ≡ sbl oracle
- `OUTPUT = EVAL('2 + 3')` → 5
- `X=2; Y=3; OUTPUT = EVAL('X + Y')` → 5
- `OUTPUT = EVAL('SIZE("ab")')` → 2
- `EVAL('5  :S(FOO)')` → **rejected** (parse error → FAIL). Expression-only ⇒ EVAL ≠ CODE.

### Gates (floors, all HARD, met)
- smoke **M4 7/7** (m3 7/7)
- pat-rung **M4 19/19 0-SKIP**, M3 15/19 (floor; the 4 M3 fails are pre-existing
  arbno/alt_commit/arbno_alt/star_deref pattern gaps — unrelated to EVAL)
- fence **TIER1=0 TIER2=0**

## Architecture (the EVAL rail, as built)

`_builtin_EVAL` → `EVAL_fn(arg)` (src/runtime/pattern_match.c).
For a STRING arg, after int/real fast-paths:
- **mode-3**: `g_eval_str_hook` = `_eval_str_impl_fn` (src/driver/driver_hooks.c) →
  now routes through `CONVE_fn`+`EXPVAL_fn` (was the `eval_ast_pat` bomb).
- **mode-4** standalone: hook is NULL → `EVAL_fn` falls through to `CONVE_fn`+`EXPVAL_fn`.
Both modes therefore share ONE path.

`CONVE_fn(str)` — BUILD (src/runtime/runtime_eval.c):
1. Parse the string as an EXPRESSION → `tree_t *e`.
   **CURRENTLY a paren-wrap workaround**: `parse_expr_pat_from_str("(<src>)")`.
   The parens route the inner text through `expr17 : T_LPAREN expr0 T_RPAREN`, so
   the returned subject subtree IS the full `expr0` (incl. binary arith). It also
   rejects statement syntax (gotos/labels aren't valid inside `(...)`).
2. Build a one-statement assignment program AST **in C** (NOT by parsing a
   statement): `ZZEVALZZ = <e>` via `ast_stmt_new(TT_PROGRAM/TT_STMT/TT_VAR)`,
   `ast_attr_int(":line"/":stno")`, `ast_attr_expr(":subj"/":repl")`,
   `ast_attr_leaf(":eq","")`, `ast_push`.
3. `lower_snobol4(prog)` → IR_graph_t; `gvar_flat_chain_build(g)` → `bb_box_fn`.
4. Stash in DT_E: `{ v=DT_E, slen=3, ptr=fn }`. `slen=3` = "emitted bb_box_fn"
   (the twin of DT_P carrying emitted pattern code; legacy slen 0/1/2 untouched).
   `eval_build_chain()` first calls `bb_pool_init()` (idempotent — `if(pool_base)return`)
   so mode-4 binaries, which never otherwise emit at runtime, can build.

`EXPVAL_fn(DT_E)` — INVOKE (src/runtime/runtime_eval.c), new `slen==3` arm:
- allocate a DEDICATED frame `int64_t eval_frame[512]` (zeroed),
- save `ZZEVALZZ` (NV_GET), run `rt_eval_run(fn, eval_frame)`, read `ZZEVALZZ`
  (NV_GET) as the result, restore the saved value, return result.

`rt_eval_run` — asm trampoline (src/runtime/runtime_eval.c). The value-return
analog of `rt_dtp_run`: pushes rbx/r12–r15, `call *fn` with `rdi=zeta, esi=0`,
pops them, ret. This is REQUIRED because EVAL runs INSIDE the outer program's
already-executing flat chain; the emitted chain is a top-level chain that does
not preserve callee-saved subject/frame regs, so calling it directly from C
corrupts the suspended outer chain (that was the segfault). Patterns return a
cursor (rt_dtp_run); expressions return their value via the `ZZEVALZZ` gvar temp.

## Latent bug fixed (separate from EVAL): `sno_parse_string_ast`

It always returned NULL: it initialised `PP.ast_prog = NULL`, but the program
rule (`sno4_stmt_commit_go`) only `ast_push`es statements when `ast_prog != NULL`,
and nothing lazily allocated it. `parse_expr_pat_from_str` only works because it
has a `prog->head` fallback; `sno_parse_string_ast` had none. **CODE() was
silently broken by this too.** Fix (mirrors `parse_program_tokens_ast`):
pre-allocate `ast = calloc(1,sizeof(tree_t)); ast->t = TT_PROGRAM;`, pass
`PP p = {prog, NULL, ast}`, return `(ast && ast->n>0) ? ast : NULL`.
Applied to BOTH src/parser/snobol4/snobol4.y AND .../snobol4.tab.c (build uses
the checked-in .tab.c directly; no bison regen in build_scrip.sh).

## FOLLOW-UP (Lon directive, do next): proper Bison expression ENTRY POINT

Lon's instruction: the paren-wrap in step 1 is a WORKAROUND. Replace it with a
real Bison separate-entry-point in the SAME grammar. **Do NOT write a second
SNOBOL4 parser.** Current state of snobol4.y: single implicit start
(`program : program stmt | stmt`, no `%start`); NO sentinel start-token; the
lexer start-conditions (INITIAL/BODY/BODY_START/…) are scanner states, not
parser entry points.

Recommended implementation (idiomatic Bison multi-entry via a start-token):
- Add a pseudo-token, e.g. `%token T_START_PROGRAM T_START_EXPR`.
- Make a new `%start unit` with:
  `unit : T_START_PROGRAM program | T_START_EXPR expr0 { /* set pp->ast_prog or pp->result to $2 */ } ;`
- Give the lexer a one-shot "emit this sentinel first" flag (set in a new
  `lex_open_*` variant or via a field on `Lex`/`g_lx`), so the first token
  returned selects the entry. CODE keeps the program entry; EVAL uses expr.
- Add `parse_sno_expr_from_str(const char *s)` that selects the expr entry and
  returns the `expr0` tree directly (no parens, no statement). Point `CONVE_fn`
  at it instead of `parse_expr_pat_from_str("(...)")`.
- Mirror edits into snobol4.tab.c, OR verify/run the parser-regen script
  (check for scripts/regenerate_parser_and_lexer_from_sources.sh) and confirm
  the build still uses the regenerated .tab.c.
- Re-run the three EVAL probes (m3≡m4≡sbl) + all gate floors after.

Cosmetic (optional): invalid EVAL prints `parse error: syntax error` via
`sno_error` to stderr before returning FAIL. A quiet-error mode on the expr
entry could suppress it; not required.

## Files touched this session (all in SCRIP repo, committed cf50707)
- src/runtime/runtime_eval.c — eval_build_chain, rt_eval_run, EXPVAL slen==3, CONVE_fn, bb_pool_init
- src/runtime/pattern_match.c — dropped stray DBG fprintf in EVAL_fn
- src/driver/driver_hooks.c — _eval_str_impl_fn → CONVE_fn/EXPVAL_fn
- src/parser/snobol4/snobol4.y, snobol4.tab.c — sno_parse_string_ast pre-allocates ast_prog

## Reusable facts (do not re-derive)
- `bb_box_fn` = `DESCR_t (*)(void *zeta, int entry)` (src/include/bb_box.h). Invoke a
  gvar flat chain as `fn(rt_frame(), 0)` (driver scrip.c ~2747); for nested EVAL use
  `rt_eval_run(fn, dedicated_frame)` instead to protect the outer chain.
- `gvar_flat_chain_build(IR_graph_t*)` (emit_bb.c:3646) is the exact mode-3 statement
  emitter, runtime-callable, in libscrip_rt. `lower_snobol4(const tree_t*)`
  (lower_snobol4.c:912) is the public program-AST → IR entry. Both exported (`nm -D`).
- `rt_frame()` returns a SINGLE shared static buffer — nested chains MUST use their
  own frame or they collide on slot temporaries.
- DT_E=11; DT_P=3; DT_C=8 (descr.h). DESCR_t struct is 16 bytes → returned in rax:rdx.
- Statement AST shape (stmt_ast.c): TT_STMT with TT_ATTR children keyed `:line :stno
  :subj :pat :eq :repl` + goto nodes; lower_snobol4 reads via stmt_attr_find/expr.
