# HANDOFF — 2026-06-06 — Sonnet 4.6 — PASCAL-BB session 27

Four rungs this session. Gate at close: **m2 70/0** over 70 probes (sole fail = recursion.pas, XFAIL);
SNOBOL smoke not run (Pascal-only session). m3/m4 pre-existing failures unchanged.
Commits: SCRIP `a390e46`, corpus `032e833`, .github `c94e43fe`.

---

## Sources read (per goal-file rule)

`pcom.pas` lines 3636-3637, 3750-3762 (na[27..32]=sin..arctan; pfname=i-12; externl=true → gen1(csp,pfname));
`pcom.pas` lines 2338-2394 (write argument dispatch: wri/wrr/wrc/wrs default widths; default real=20);
`pcom.pas` lines 864-932 (constant() procedure: string, int, real constant handling; lsp=charptr for len=1);
`pint.pas` lines 137-147 (sptable[14..19]=sin/cos/exp/log/sqt/atn);
`pint.pas` lines 613-620 (wrr: write(output, store[sp-2].vr: store[sp-1].vi));
`pint.pas` lines 651-656 (callsp 14-19: sin/cos/exp/ln/sqrt/arctan);
`grammar/pascalp.y` (argument production: expression COLON expression for width specifier).

---

## PB-18 — sin/cos/exp/sqrt/ln/arctan

**Parser changes (`pascal.y`):**

Added six lines to `mk_call` after `abs`:
- `sin/cos/exp/sqrt/ln/arctan` → `mk_fnc1("__pas_sin"/etc, args->items[0])`
- arg may be int (coerced to double in runtime)

**Runtime changes (`by_name_dispatch.c`):**

Added `#include <math.h>`.

Added `static void pas_real_str(double r, char *buf, int bufsz, int prec)`:
- formats `%.*E` with given precision
- normalises exponent to 3 digits (zero-pads if C gives 2)
- prec clamped to [1, 16]
- matches pint's Pascal `write(r:w)` output exactly

Added one combined dispatch arm for all six math builtins:
- 1 arg (int-or-real coerced to double), returns `DT_R` DESCR_t
- dispatches on fn name to `sin`/`cos`/`exp`/`sqrt`/`log`/`atan`

Fixed `__pas_writeln` real branch: was calling `real_str()` (SNOBOL4 `%g` style, wrong format).
Now calls `pas_real_str(av.r, _rb, sizeof _rb, 12)` for default; prec computed from width when
explicit `:w` given.

Added all six names to `builtins[]` table.

**Probe:** `stdlib2.pas` — sin(1.0), cos(0.0), sqrt(2.0), arctan(1.0), exp(1.0), ln(r).

**Gotcha — pint real table overflow:**
pint has a small real constant table (~5 entries). A program with 6 distinct real literals
overflows. Probe uses `r := ln(r)` (reusing computed value) to avoid a 6th literal.

---

## PB-19 — `write(real:w)` width specifier

**Formula** (derived from pint `wrr` + oracle measurement across w=7..25):
- `prec = max(1, w - 8)`, clamped at 16 (double precision ceiling)
- output width = `max(w, prec + 8)` — minimum output is 9 chars (` d.dE+NNN`)
- default (no `:w`, sentinel w=-1) = prec 12, width 20 — unchanged

**Runtime:** `__pas_writeln` real branch computes `_prec` from `w` before calling `pas_real_str`.

**Probe:** `realwidth.pas` — sqrt(2.0) and arctan(1.0) at widths 20, 15, 12, 10.

---

## PB-20 — char literal in write position

**Root cause:** `factor: STRINGCONST len=1` emitted `ilit(ord)`, losing char type info.
`pas_is_charexpr` only recognised charvars and `__pas_chr(...)` nodes.
Bare char literals in write args were not wrapped → printed as integers.

**Fix — `__pas_chrlit` sentinel:**

1. `factor: STRINGCONST len=1` now emits `TT_FNC("__pas_chrlit", ilit(ord))`.
2. Runtime `__pas_chrlit(n)` = identity: returns `INTVAL(n)` unchanged. Transparent in
   arithmetic, comparison, array indexing, for-loop bounds.
3. `pas_is_charexpr` extended: also recognises `__pas_chrlit` → write-arg path replaces
   with `__pas_chr(ilit(ord))` → `"A"` string, width sentinel set to -2 → `fputc`.
4. `ord('A')` in `mk_call`: if arg is `__pas_chrlit(ilit(n))`, unwraps to bare `ilit(n)`.
   Prevents double-char-tagging through `ord()`.
5. `__pas_chrlit` added to `builtins[]` table.

**Probe:** `charlit.pas` — writeln('A'), writeln('Z'), writeln('a':3), writeln('0':5),
if c='M' then writeln('Y'), writeln(ord('A')), writeln(ord('Z')-ord('A')).

---

## PB-21 — real and string named constants

**Root cause:** `g_pas_consts[]` stored only `long long`. Real constants (`pi = 3.14159`)
were truncated on `pas_const_add` via `scalar_constant: REALCONST → (long long)$1`.
String constants (`msg = 'hello'`) silently stored as 0 (multi-char → 0, via the
`scalar_constant: STRINGCONST` arm).

**Fix:**

Added two parallel tables to `pascal.y`:
- `g_pas_rconsts[64]` (double) with `pas_rconst_add` / `pas_rconst_get`
- `g_pas_sconsts[64]` (char\*) with `pas_sconst_add` / `pas_sconst_get`

`const_decl` extended with four new alternatives (before the integer `constant` arm):
- `IDENT EQOP REALCONST SEMICOLON` → `pas_rconst_add`
- `IDENT EQOP PLUS REALCONST SEMICOLON` → `pas_rconst_add` (positive sign)
- `IDENT EQOP MINUS REALCONST SEMICOLON` → `pas_rconst_add` (negated)
- `IDENT EQOP STRINGCONST SEMICOLON` → single char → `pas_const_add(ord)`;
  multi-char → `pas_sconst_add`

`mk_ident` resolution order: int→`ilit`, real→`flit`, string→`TT_QLIT`.

**Probe:** `constreal.pas` — `pi=3.14159265`, `msg='ok'`, `limit=100`; assigns pi to real var,
writes it; writes string const; writes int const; writes `-pi`.

---

## Gotchas for next session

1. **pint real table overflow** — programs with more than ~5 distinct real literal constants
   overflow pint's internal table. Design probes to reuse computed real values via variables.
2. **__pas_chrlit sentinel and ord()** — `ord('A')` in mk_call strips the sentinel. Any new
   standard function receiving a char literal must similarly unwrap if it expects integer semantics.
3. **const_decl alternatives** — the REALCONST alternatives must precede the `constant` arm;
   bison picks the first matching alternative. The `constant` arm still handles plain INTCONST
   and IDENT-named constants correctly.
4. All six standing landmines remain live (rm -f scrip before make, bison-only regen,
   touch templates, apt-get update before fpc, pull-rebase → rebuild → full gate,
   TEXT labels by bb_node_id).

## Next (Lon picks)

(a) 16-bit integer clamp (recursion.pas XFAIL → 71/0; requires clamping int arithmetic to [-32768, 32767]).
(b) Subrange type bounds.
(c) Additional write/read coverage (write(i:w) integer width, write(s:w) string width — both already work; verify with dedicated probes).
(d) case no-match: emit a runtime trap matching pint's "value out of range" halt.
