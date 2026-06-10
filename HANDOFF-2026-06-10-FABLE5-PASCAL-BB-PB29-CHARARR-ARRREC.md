# HANDOFF 2026-06-10 — Pascal BB: Session 35 (char arrays + array-of-record + variant parse; gate 98/0)

## State on origin (verified clean)
- **SCRIP `2654333`** · **corpus `50651e50`** · **.github** (this commit)

## Gate
**m2 98/0** over 99 probes (recursion.pas XFAIL). Up from 93/0 at session start.
Post-rebase rebuild + full re-gate done (landmine #5 observed — SCRIP rebased mid-push).

## Work done this session (all in `src/parser/pascal/pascal.y`)

### 1. Char arrays print as chars (BUG-1) — probes chararr1/chararr2
- New `g_pas_chararrs[256]` table + `pas_chararr_add/pas_is_chararr`.
- `pas_is_charexpr` extended: TT_IDX whose c[0] is TT_VAR in chararrs → char expr → write path
  wraps with `mk_chr_wrap` (prints via `__pas_chr`, width sentinel -2).
- Element-type-is-char detection: array rules save inner `g_pas_pend_ischar` into new
  `g_pas_pend_arr_ischar` (index-type ischar would otherwise clobber it).
- Named array types: `g_pas_arrtypes[]` grew an `ischar` field (+`pas_arrtype_ischar`);
  `var id: alpha` and value params `(w: alpha)` register chararr from the named type.
- `var_decl` now: arrays → `pas_chararr_add` (when element char); scalars → `pas_charvar_add`
  only when `$3 < 0` (was unconditionally charvar'ing array names).

### 2. `array[char]` index type (BUG-2) — probe chararr3
- `simple_type: IDENT` arm: name=="char" → `$$ = 255` (was falling to -1, array never registered).

### 3. Tagfield-only variant record (BUG-3)
- `record_case_opt` new arm: `CASESY IDENT OFSY record_case_list` (pint.pas `case datatype of`).
- **pint.pas now parses clean.**

### 4. Array-of-record (BUG-4) — probes arrrec1/arrrec2
- `var d: array[0..H] of rec` registers `pas_array_add2d(d, (H+1)*nf-1, nf)` + new
  `g_pas_arrrecs[128]` {aname, rname, nf}. (Was bogusly recvar+array(nf-1) registering.)
- `selector PERIOD IDENT`: base TT_IDX(TT_VAR in arrrecs, sub) → `pas_arrrec_flatten` →
  `TT_IDX(d, sub*nf + fi)`. Anonymous rectype fallback: scan rectypes for field name with
  matching nf.
- `with d[i]`: `pas_with_sel_rtype` new arm (TT_IDX, base in arrrecs → rname);
  `mk_ident` with-loop emits `pas_arrrec_flatten(clone(wsel), fi)` for arrrec selectors.
- `pas_rectype_to_pend` calls `pas_pend_reset()` which wiped `g_pas_pend_typename` →
  arrrec rname stored NULL → with rtype NULL. Fix: re-strdup typename after the call in
  `simple_type: IDENT`.

### 5. `pas_tree_clone` union strdup corruption (latent, critical)
- Clone did `if (e->v.sval) strdup(e->v.sval)` on EVERY node; `v` is a union, so TT_ILIT
  ival=2 aliases sval=0x2 → strdup(0x2) → SEGV. ival=0 masked the bug (d[0] worked, d[1+] crashed).
- Fix: strdup only when `t == TT_VAR || t == TT_QLIT`.

### Corpus
- **81 missing `.ref` files regenerated** from the pcom+pint oracle and committed; the gate now
  covers all 99 probes against checked-in refs (was 12 refs before).
- New probes: chararr1-3, arrrec1-2 (5 net new, all green, all oracle-verified).
- Note: pcom rejects passing `alpha` as a VALUE param to a user proc ("duplicated label" — pcom's
  own string-param limitation); chararr2 was rewritten to avoid that — pcom rejections are
  out-of-scope per the goal's dialect rule.

## pcom.pas / pint.pas ladder status (PB-30)
- pint.pas: parses. Not yet executed.
- pcom.pas: parses, `--interp` exits silently (no crash, 0 bytes out, empty prr created).
  `--dump-ast` still segfaults on it (huge-AST printer issue; NOT a lower/interp blocker).
- Verified-working in isolation this session: pcom's full type block (3-level nested variants,
  forward ptrs), `with display[0] do`, `chartp[chr(i)] :=` (chr is parse-time identity),
  set-of-enum constructors `[addop,intconst,...]`.
- **Next bisect plan:** instrument pcom main: `initscalars; initsets; inittables;` →
  `enterstdtypes; stdnames; entstdnames; enterundecl;` → `insymbol; programme(...)`.
  Top suspects: (a) `assign(prr,'prr'); rewrite(prr)` + file builtins missing → silent no-op
  somewhere fatal; (b) entstdnames-scale pointer-record chains (new/^.field:=); (c) table
  limits — PAS_FIELD_MAX=32 vs identifier's nested-variant field count via pas_pend_add,
  PAS_LOCAL_MAX=64 per scope.

## Residues (carried forward)
- recursion.pas XFAIL (16-bit maxint, P4 limitation).
- m3/m4 pre-existing failures.
- Case no-match silently continues (no probe).
- `__pbt`/`__pct` NV temps clobber under recursive re-entry (no probe).
- `--dump-ast` segv on very large ASTs (pcom.pas).

## Session setup (next session)
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && rm -f scrip && make -j4 scrip && make libscrip_rt
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
cd /home/claude/corpus/programs/pascal && apt-get update -qq && apt-get install -y fpc \
  && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas
```
Gate loop (refs now checked in): for each `*.pas` minus pcom/pint/ppp, `timeout 8s scrip --interp
p.pas < ${p}.in-or-/dev/null` vs `p.ref`; recursion = XFAIL.
