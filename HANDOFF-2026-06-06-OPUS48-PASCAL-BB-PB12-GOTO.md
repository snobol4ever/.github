# HANDOFF — 2026-06-06 — Opus 4.8 — PASCAL-BB session 23

One deliverable, landed + pushed. Gate at close: **m2 52/1, m3 52/1, m4 52/1 — UNIFORM** over 53
probes (sole fail = recursion.pas, 16-bit maxint pin); SNOBOL smoke 19/0; Icon m3/m4 10/2
**stash-proven pre-existing** (rebuilt unmodified base, identical failures); Prolog smoke clean.

## PB-12 — `goto`/label (SCRIP `d8a5c1d`, corpus `2c7c68b`)

Sources read first per goal-file rule: `grammar/pascalp.y` (goto_statement, label_decl_block,
INTCONST COLON statement); `pcom.pas` gotostatement (ujp; intra-procedure only — cross-proc = error
399), labeldeclaration (per-block flabel chain), statement-entry label definition (putlabel + defined
flag, error 165/167); `int.p` ujp = `pc := q`. Oracle-first probes: all three pcom-compiled and
pint-run BEFORE any SCRIP change.

Mechanism — pure IR wiring, ZERO templates, ZERO new IR kinds, m3/m4 free:
- `ast.h`: ONE new tree kind `TT_LABEL_DEF` (+names entry). `TT_GOTO_U` reused for the goto itself
  (exact semantic match; removed from lower.c's no-op grab-bag where it previously sat — that was
  the duplicate-case build error of the session).
- `pascal.y`: `goto N` → `TT_GOTO_U` leaf, sval = strdup'd digits (leaf_s-doesn't-copy landmine
  honored); `N: stmt` → `TT_LABEL_DEF` wrapper. Direct bison regen, expected 1 s/r.
- `lower_program.c`: `pas_register_labels` — recursive pass-1 walk of the body (stops at nested
  TT_PROC_DECL/TT_SUB_DECL) allocating one IR_SUCCEED landing per label into the proc's graph and
  registering via the existing SNOBOL `bb_label_registry_*`; registry RESET per body = per-proc
  scoping (Pascal labels are block-scoped). Pre-registration makes BOTH goto directions resolve
  under the existing back-to-front statement lowering.
- `lower.c`: `TT_LABEL_DEF` arm (IR_LANG_PAS-guarded) lowers the inner stmt, wires landing→γ to its
  α, exposes the LANDING as the statement's α (so fall-in and every goto route through one node);
  `TT_GOTO_U` arm lowers to an IR_SUCCEED hop with γ PINNED to the landing — γ_in deliberately
  ignored, ω = ω_in. Unresolved label → NULL (loud lower failure, pcom-error-167 spirit).

Probes (each oracle-verified first): `goto1.pas` backward loop + forward dead-code skip (5/15);
`goto2.pas` the pcom-insymbol restart pattern — backward goto from if-inside-while + forward goto
out of the loop (3/16/1603); `goto3.pas` SAME label number in two routines (proc + function) pins
the per-body registry reset (11/15).

## Gotchas (carry forward)

1. `TT_GOTO_U` lived in lower.c's ignore-list arm (~line 1177) — any future kind promotion out of
   that grab-bag will hit the same duplicate-case error; delete from the list when claiming.
2. Stash-prove discipline paid: Icon m3/m4 10/2 looked alarming, was pre-existing frontier.
3. Residue added to goal: labels NESTED inside compounds register + lower by construction, but no
   probe pins that position yet (pcom will need it — its `2:` sits mid-insymbol).
4. All six standing landmines re-confirmed live.

## Next (Lon picks)

(a) 16-bit maxint rung (recursion.pas). (b) the pcom/pint ladder proper — char type, enum
ordinals, file I/O (prd/prr/`f^` buffer), packed-array alfa string ops, `with` binding (currently
DROPS the selector — silent wrong code on any real `with`), variant records. pint.pas (1062 lines)
is the realistic first self-host target; pcom.pas adds pack/unpack + heavier with/enum on top.
(c) documented residues if a probe forces them.
