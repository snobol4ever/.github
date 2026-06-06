# HANDOFF — 2026-06-06 — Sonnet 4.6 — PASCAL-BB session 23 (final)

Two rungs this session. Gate at close: **m2 54/1, m3 54/1, m4 54/1 — UNIFORM** over 55 probes
(sole fail = recursion.pas, 16-bit maxint pin); SNOBOL smoke 19/0; Icon m3/m4 10/2 stash-proven
pre-existing.

---

## PB-12 — `goto`/label (SCRIP `0a614f2` → rebased `ab599a4`-1, corpus `2c7c68b`)

*(Details in `HANDOFF-2026-06-06-OPUS48-PASCAL-BB-PB12-GOTO.md` — written mid-session.)*

Mechanism recap: new `TT_LABEL_DEF` kind in ast.h; `TT_GOTO_U` leaf for goto; `lower_pascal_body`
recursive pass-1 pre-registers one IR_SUCCEED landing per label (bb_label_registry, reset per body
= per-proc scoping); `TT_LABEL_DEF` arm wires landing→γ to inner α; `TT_GOTO_U` arm is an
IR_SUCCEED hop with γ pinned to the landing. Zero templates, zero new IR kinds, m3/m4 free.
Probes: goto1 (backward loop + forward skip), goto2 (restart from inside while/if), goto3
(identical label numbers in two procs — pins per-body registry reset). All 3×3 uniform first run.

Landmine encountered: `TT_GOTO_U` was in lower.c's no-op grab-bag → duplicate-case build error;
removed from grab-bag, dedicated arm owns it. Per-RULES stash-prove for Icon m3/m4.
Concurrent push (PL-GZ-7b ITE box): rebuilt + re-gated on rebased base per landmine 5 — held.

---

## PB-13 — enum ordinals (SCRIP `ab599a4`, corpus `2c581f4`)

**Two parser lines, zero everything else.**

Sources read: `pcom.pas` const block (datatype, symbol enumerations — pcom/pint both load-bearing);
`int.p` `ord`/`chr` ops 59/60 ("only used to change the tagfield" = ord is identity on integers);
pascalp.y `simple_type` production.

Gap before fix: `simple_type: LPARENT id_list RPARENT { $$ = -1; }` — enum members never entered
into `g_pas_consts`. `mk_ident("green")` fell through to `TT_VAR("green")`, unbound at runtime.

Fix:
1. `simple_type: (id_list)` action iterates the list assigning ordinals 0,1,2,… via `pas_const_add`.
   Consequence: `mk_ident` → `pas_const_get` → `ilit(N)` for every enum name. Case-over-enum,
   for-over-enum, enum params, enum arithmetic all work without further changes.
2. `mk_call("ord", args)` early-returns `args->items[0]` (integer-valued enums → identity).
   ord() for char deferred to the char rung.

Probes: enum1 (two enum types, ord/case/for), enum2 (enum across procs/params, encode fn, for-to-fjp).
Probe discipline note: pcom compiled with `-Cr`; for-over-full-enum-range triggers pint range error
that writes to stdout (pint's `errori` → `writeln` to output, not stderr) — redesigned enum2 to stop
at fjp (7), leaving one increment to stp (8) still in range [0..8]. Probes must not trigger pint range
errors or the reference output is contaminated.

---

## Context note

Session hit ~82–85% context by handoff time. No rung was truncated; both rungs are complete and
byte-clean. The `with` rung was the natural next pick and was NOT started — clean slate for next
session.

---

## Next (Lon picks)

**(a) `with` binding** — the highest-priority latent wrong-code item. Currently `with_statement:
WITHSY selector_list DOSY statement { $$ = $4; }` silently drops the selector. pcom.pas uses `with`
extensively (withstatement pushes the record's fstfld chain onto `display` so bare field names
resolve — SCRIP needs parse-time field-name injection into a local alias table, similar to the
existing `g_pas_recvars` machinery). A contained parser + possibly small-runtime rung.

**(b) char type** — char literals `'a'` (STRINGCONST length-1 today), `chr(n)` (complement to ord),
char I/O (read/write of char vars), case-over-char, char comparisons. Foundational for pcom/pint
alfa and file-buffer reads. Larger rung.

**(c) 16-bit maxint** — closes recursion.pas (XFAIL). Gate goes to 55/0 uniform.

**(d) file I/O** — `program(input,output,prd,prr)`, reset/rewrite, `f^` buffer variable, get/put,
eof/eoln. The largest missing subsystem; pint is built on it.

## Landmines reminder (all six still live)
1. `rm -f scrip` before `make scrip`
2. Pascal regen via `bison -d -o pascal.tab.c pascal.y` only (never the full regen script)
3. `touch` templates before `make` after template edits
4. `apt-get update` before `apt-get install fpc`
5. Every `git pull --rebase` → `rm -f scrip && make` → FULL gate re-run
6. TEXT internal labels keyed by `bb_node_id` not per-box uid
