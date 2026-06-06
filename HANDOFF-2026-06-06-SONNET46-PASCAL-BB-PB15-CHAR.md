# HANDOFF — 2026-06-06 — Sonnet 4.6 — PASCAL-BB session 25

One deliverable, landed + pushed. Gate at close: **m2 60/1** over 61 probes (sole fail =
recursion.pas, 16-bit maxint pin); SNOBOL and Prolog smoke clean. m3/m4: 32/28 (25 pre-existing
+ 3 new char probes, all marshal_call_arg pre-existing root cause).

---

## PB-15 — char type (SCRIP `3cb0be3`, corpus `e515505`)

Sources read first: `grammar/pascalp.l` (STRINGCONST rule); `grammar/pascalp.y` (factor,
scalar_constant, constant productions); `pcom.pas` (charptr init, string-length-1 → `ldc 6`,
charptr type-check in write/read, ord/chr procedure bodies at lines 2551/2559); `int.p`
(`ldc` type-6 = `store[sp].vc := chr(q)`; op 59/60 = null; `wrc` sp-10 = `write(output,
store[sp-2].vc: store[sp-1].vi)` default width 1). Oracle probes verified before any SCRIP change.

**Representation choice:** chars stored as integer ordinals everywhere (not as 1-char strings).
This is required for for-over-char, char arithmetic (`ord(c)+1`), and char comparisons to work
with the existing integer IR machinery. The write boundary is the only point where an ordinal
must be rendered as a character.

**Changes — `pascal.y`:**
- `scalar_constant: STRINGCONST` len=1 → `(long long)(unsigned char)s[0]` (previously returned 0).
  Covers: `const x = 'A'`, case labels `'A':`, for-loop bounds `for c := 'A' to 'E'`.
- `constant:` — removed the old `STRINGCONST { $$ = 0; }` arm (was ambiguous with the new
  `scalar_constant: STRINGCONST`; removal resolves all 6 r/r conflicts).
- `factor: STRINGCONST` len=1 → `ilit(ord)` (was `leaf_s(TT_QLIT, s)`). Multi-char stays TT_QLIT.
- `mk_call("chr", args)` → identity (returns `args->items[0]`), parallel to `ord`. chr(n)=n
  since chars are ints; no type conversion needed.
- `g_pas_charvars[256]` + `pas_charvar_add` + `pas_is_charvar` — new table, reset per parse.
  `g_pas_pend_ischar` flag set in `simple_type: IDENT` when `!strcmp($1, "char")`.
- `var_decl:` action: calls `pas_charvar_add` when `g_pas_pend_ischar`.
- `parameter_decl: id_list COLON IDENT`: registers char params when IDENT="char".
- `mk_chr_wrap` + `pas_is_charexpr` — forward-declared before `mk_call`. `pas_is_charexpr(e)`:
  true if `e->t == TT_VAR && pas_is_charvar(e->v.sval)` OR `e->t == TT_FNC` with `__pas_chr` head.
- `mk_call` write/writeln path: for each `(val, wid)` pair, if `pas_is_charexpr(val)`:
  wrap val with `mk_chr_wrap`, change default width -1 → -2 (char sentinel).

**Changes — `by_name_dispatch.c`:**
- `__pas_chr` added to `builtins[]` array (for `proc_as_value` lookup).
- `__pas_chr` handler (1 arg, integer ordinal → 1-char GC_malloc(2) string, `DT_S` tag).
- Write string branch: width `-2` → `fputc(ch, stdout)` (char, pint wrc default width 1);
  width `≥0` → `fprintf(stdout, "%*s", w, s)` right-justified (pint wrc `:w` behavior).

**Probes (each oracle-verified before SCRIP):**
- `char1.pas`: var c:char; c:='A'; writeln(c); writeln(c:3); c:=chr(66); writeln(c); i:=ord(c); writeln(i) → `A\n  A\nB\n        66`
- `char2.pas`: char comparisons (< > =), for c:='A' to 'E' do writeln(c) → `less\nequal\ngreater\nA\nB\nC\nD\nE`
- `char3.pas`: char params/returns, chr/ord, case-over-char → `M\nN\nmid`

**Gotchas:**
1. `mk_chr_wrap` and `pas_is_charexpr` must be forward-declared before `mk_call` (which uses both).
2. Removing `constant: STRINGCONST { $$ = 0; }` was required — leaving it alongside the new
   `scalar_constant: STRINGCONST` creates 6 r/r conflicts on the follow set {`;`, `end`, `,`, `:`, `]`, `..`}.
3. Write path loop: `for (int i = 0; i + 1 < args->count; i += 2)` — the off-by-one guard
   `i + 1 <` prevents reading past the last width item if count is odd.
4. `DT_SSTR` does not exist — correct tag is `DT_S` (from `descr.h`).
5. m3/m4 char write fails: `__pas_chr(c)` is a computed write arg → hits pre-existing
   marshal_call_arg ICN-HY-7g regression. Same root as m4wexpr/rec*/goto*. stash-proof: char2
   m3 outputs `less\nequal\ngreater` (comparisons correct) + 5 blank lines (for-loop writeln(c)
   fails) — for-loop itself runs correctly (5 iterations), only write is broken.

**Residues (added to goal):**
- Char literal in write position (`writeln('A')`) prints 65 not `A` — the `ilit(65)` from a
  char literal is indistinguishable from integer 65 at the write call site. Fixing requires
  either grammar-level write specialization or a per-node char tag. No probe exercises this case.
- Charvar table global/unscoped — same param name used with `char` type in one proc registers
  globally; a different proc reusing that name would see it as charvar. No probe affected.

## Next (Lon picks)

(a) **File I/O** — `program(input,output,prd,prr)`, reset/rewrite, `f^` buffer variable, get/put,
eof/eoln. The largest missing subsystem; pint.pas is built on it.
(b) **packed-array / alfa** — `packed array [1..8] of char`; pcom's alpha type; string literals
as packed char arrays.
(c) **16-bit maxint** — closes recursion.pas (XFAIL). Gate goes to 61/0 uniform in m2.

## Landmines (all six live)
1. `rm -f scrip` before `make scrip`
2. Pascal regen via `bison -d -o pascal.tab.c pascal.y` only
3. `touch` templates before `make` after template edits
4. `apt-get update` before `apt-get install fpc`
5. Every `git pull --rebase` → `rm -f scrip && make` → FULL gate re-run
6. TEXT internal labels keyed by `bb_node_id` not per-box uid
