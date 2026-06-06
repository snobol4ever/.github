# HANDOFF — 2026-06-06 — Sonnet 4.6 — PASCAL-BB session 26

Two rungs this session. Gate at close: **m2 65/1** over 66 probes (sole fail = recursion.pas, XFAIL);
SNOBOL smoke 19/0; Prolog smoke m2 5/0, m3/m4 clean. m3/m4 pre-existing failures unchanged.
Commits: SCRIP `4e4cbf8`, corpus `80e95e7`.

---

## Sources read (per goal-file rule)

`pcom.pas` lines 2247–2302 (read procedure — csp rdi/rdr/rdc dispatch, lkey 5=read/11=readln);
`pcom.pas` lines 2575–2592 (eof/eoln procedures — lkey 9=eof/10=eoln, gen0(8) for eof, csp 14=eln);
`pcom.pas` lines 3628–3630 (stdnames table — na[9]=read, na[15]=readln, na[25]=eof, na[26]=eoln);
`pint.pas` lines 491–515 (readi/readr/readc — scanf semantics: two-item stack, address of var);
`pint.pas` lines 545–650 (callsp: csp 0=get,1=put,3=rln,7=eln,11=rdi,12=rdr,13=rdc);
`pint.pas` line 899 (opcode 27=eof — checks `store[sp].va == inputadr`);
`grammar/pascalp.l` (no special tokens for read/eof — all plain IDENT);
`grammar/pascalp.y` (argument production — `:w` only for write; read args are bare variables).

---

## PB-16 — read/readln/eof/eoln

**Parser changes (`pascal.y`):**

Added `mk_fnc0(fn)` and `mk_fnc1(fn, a)` helpers (before `mk_call`).

Added forward declarations of `pas_is_charvar`, `pas_is_rel`, `pas_bool` before `mk_call`
(needed because `mk_call` now calls these before their definitions in the file).

In `mk_call`:
- `read(v, ...)` → seq of `mk_assign(v, mk_fnc0("__pas_read_i"))` per int var,
  `mk_assign(v, mk_fnc0("__pas_read_c"))` per charvar. Multiple vars: `seq_of(stmts)`.
- `readln()` (no args) → `mk_fnc0("__pas_readln")`.
- `readln(v, ...)` (with args) → seq of reads + `mk_fnc0("__pas_readln")`.
- `eof()`/`eoln()` when called with explicit parens — `mk_fnc0("__pas_eof"/"__pas_eoln")`.

In `mk_ident` (critical fix):
- `eof` → `mk_fnc0("__pas_eof")`.
- `eoln` → `mk_fnc0("__pas_eoln")`.
This is the essential fix. In P4 Pascal, bare `eof` (no parens) is the common form — it appears
as `selector → IDENT` in the grammar (expression position), routed through `mk_ident`, NOT through
`mk_call`. Without this intercept, `eof` falls through to `leaf_s(TT_VAR, "eof")` = an unbound
variable, and `while not eof do` silently does nothing (no failure, just drops to ω immediately).

**Runtime changes (`by_name_dispatch.c`):**

Added to `try_call_builtin_by_name` (in the `__pas_chr` neighbourhood, before `__pas_writeln`):
- `__pas_read_i` (0 args): `scanf(" %lld", &v)` — leading space skips whitespace including `\n`.
- `__pas_read_c` (0 args): `getchar()` — no ws-skip, reads the literal next character.
- `__pas_readln` (0 args): `while ((c=getchar()) != '\n' && c != EOF)` — drains to end of line.
- `__pas_eof` (0 args): peek via `getchar()`/`ungetc` — returns INTVAL(1) if EOF, else INTVAL(0).
- `__pas_eoln` (0 args): peek via `getchar()`/`ungetc` — returns INTVAL(1) if `'\n'` or EOF.

Added all eight new names to the `builtins[]` table for `proc_as_value` lookup.

**Gate mechanics — `.in` companion files:**
The standard gate rule (`timeout 8s < /dev/null`) fails for read probes because both oracle (pint)
and SCRIP get empty stdin, producing identical but trivial output (reading 0 always). For probes
needing real stdin, `.in` companion files (`read1.in`…`read4.in`) supply the data. Gate snippet:
`inp=/dev/null; [ -f "${base}.in" ] && inp="${base}.in"`.

**Probes (each oracle-verified first):**
- `read1.pas` + `read1.in` ("3 7"): `read(i); read(j); writeln(i+j)` → `        10`.
- `read2.pas` + `read2.in` ("42\nX"): `readln(i); read(c); writeln(i); writeln(c)` → `        42\nX\n`.
- `read3.pas` + `read3.in` ("1 2 3 4 5"): `while not eof do begin read(i); sum := sum + i end; writeln(sum)` → `        15`.
- `read4.pas` + `read4.in` ("abc\nde"): eoln/readln char-count loop → `         7`.

---

## PB-17 — abs/trunc/odd/pred/succ

All pure parser transforms in `mk_call` (no new IR, no new templates):
- `pred(i)` → `bin(TT_SUB, args->items[0], ilit(1))`.
- `succ(i)` → `bin(TT_ADD, args->items[0], ilit(1))`.
- `trunc(r)` → `mk_fnc1("__pas_trunc", r)`. Runtime: `(long long)d`.
- `abs(x)` → `mk_fnc1("__pas_abs", x)`. Runtime: `v < 0 ? -v : v` for int; `d < 0 ? -d : d` for real.
- `odd(i)` → `bin(TT_NE, bin(TT_MOD, args->items[0], ilit(2)), ilit(0))`.

**Gotcha — `odd` must NOT be pre-wrapped in `pas_bool`:**
First attempt was `pas_bool(bin(TT_NE, ...))` which produces `TT_IF(TT_NE(...), 1, 0)`. When this
appears in `if_statement`, `pas_cond(TT_IF(...))` sees a non-relop and wraps it again:
`TT_NE(TT_IF(...), 0)`. This outer `TT_NE` lowers to `IR_BINOP(NE)` with null α/β (no explicit
operand pointers — the IR chain model). The interpreter's null-α/β `IR_BINOP` path checks PEERS
(`bb_operand_aux_get`) first; if none, falls back to `ag_ring_peek`. For Pascal flat chains,
neither yields correct values → immediately returns FAILDESCR → program silently routes to ω.
Fix: return the raw `TT_NE` relop from `mk_call("odd")`. The `argument_list` wrapper and
`assignment` wrapper each apply `pas_bool` at the use site when needed — no pre-wrapping in `mk_call`.

**Probe:** `stdlib1.pas` (no stdin): abs(-7)=7, abs(5)=5, trunc(3.9)=3, trunc(-2.1)=-2,
odd(4)→no, odd(7)→yes, pred(10)=9, succ(10)=11. All 8×m2 first run.

---

## Gotchas for next session

1. **`eof`/`eoln` intercept is in `mk_ident`, not `mk_call`** — bare identifiers in expression
   position route through `selector → IDENT → mk_ident`, not through the call path. Any new
   zero-arg standard function (e.g. `eoln(prd)` if prd support is added) would need both.
2. **`odd` pre-wrapping with `pas_bool` breaks the IR chain model** — returning raw relops from
   `mk_call` is safe; the use-site wrappers (`argument`, `assignment`) apply `pas_bool` correctly.
3. **`.in` companion file gate pattern** — any future probe needing stdin needs a `.in` file.
   The gate is the caller's responsibility (no checked-in script); the pattern is documented here.
4. All six standing landmines remain live (rm -f scrip, bison-only regen, touch templates,
   apt-get update before fpc, pull-rebase → rebuild → full gate, TEXT labels by bb_node_id).

## Next (Lon picks)

(a) More stdlib: `sqrt`/`sin`/`cos`/`ln`/`arctan` (pint csp 14-19; all have direct C equivalents).
(b) `write(real:w:d)` two-width specifier (pint wrr: `write(f, store[sp-2].vr: store[sp-1].vi)`).
(c) packed-array/alfa — `packed array [1..8] of char`; pcom alpha type; string literals.
(d) 16-bit maxint close (recursion.pas XFAIL → 66/0 gate; requires per-arg eager writeln).
