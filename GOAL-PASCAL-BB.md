# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes

## ⛔ FACT RULES POINTER (Lon 2026-06-06)
ONE MEDIUM, INVISIBLE + TEMPLATE-ONLY EMISSION (corrected): canonical text in GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md / GOAL-PROLOG-BB.md / GOAL-RAKU-BB.md and RULES.md. ZERO BINARY emission anywhere in a `bb_*.cpp` (top level or helpers); `x86()` internals are the ONLY emitter of BINARY and TEXT.

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

No language-specific logic in any BB or XA C++ template; templates dispatch on IR shape and
representation flags only. FORBIDDEN in `src/emitter/BB_templates/` + `XA_templates/`: language
enums/guards (`IR_LANG_*`, `LANG_*`, `is_<lang>`), language-named functions/files/dispatch arms,
hardcoded language-builtin names. Language-divergent behavior goes in the runtime (by-name dispatch)
or in LOWER (different IR shape → its own BB) — never a template arm. COMPLETION TEST: the Tier-1 grep
(`SCRIP/BB-TEMPLATES-LANG-AUDIT.md`) over both template dirs == 0.

**Repo:** SCRIP (frontend + lower) · corpus (reference at `programs/pascal/`)
**The 7th frontend.** SNOBOL4 · Snocone · Rebus · Icon · Prolog · Scrip · **Pascal**.

---

## ▶ CURRENT STATE

**Session 29 (2026-06-07): PB-24 (2D comma-syntax array, flat-index encoding) + PB-25 (mark/release no-ops + stdlib/misc probes) LANDED.**
Gate: **m2 81/0** over 82 probes (sole fail = recursion.pas XFAIL).
Commits: SCRIP `2daa9d0`, corpus `f45e1e74`.

BUG DIAGNOSED (PB-26, NOT YET FIXED): Array value params — `nparams` never set for Pascal TT_PROC_DECL.
Fix: one line in `lower_program.c` before the `int np = ...` line (~line 641):
`g_stage2.proc_table[pi].nparams = plist2 ? plist2->n : 0;` where `plist2 = proc->c[1]`.
See HANDOFF-2026-06-07-SONNET46-PASCAL-BB-PB24-PB25.md for full recipe + test probe.
New probes: enumarr.pas, subarr.pas, enumsubarr.pas, varrec.pas.
m3/m4 pre-existing failures unchanged (marshal_call_arg root cause, not touched).

Mechanism (PB-22): `g_pas_enumtypes[]`/`g_pas_subtypes[]` tables; `type_decl` action registers
enum max ordinal + subrange low/high by name; `simple_type` IDENT arm looks up both tables before
falling through to record/pointer; `simple_type` DOTDOT arm captures low/high into pending state;
`simple_type` LPARENT arm sets `g_pas_pend_enum_max` and returns `_eo-1` (not -1).

Mechanism (PB-23): `record_case_opt`/`record_case_list`/`record_case_arm` productions added to
`record_body`; tag field + all variant arm fields flattened into `g_pas_pend_fields[]` accumulator;
overlap semantics correct for non-aliasing probes (each variant field gets a distinct named slot).

PB-24 (2D comma-syntax arrays) — ATTEMPTED, REVERTED. Segfault on assignment; root cause:
TT_FNC node layout in mk_assign desugar needs to match lower.c:566 TT_FNC dispatch.
Recipe in HANDOFF-2026-06-07-SONNET46-PASCAL-BB-PB22-23.md.

RESIDUES (carry-forward): recursion.pas XFAIL (16-bit maxint); case no-match silently continues;
NV __pbt/__pct temps can clobber under recursive re-entry; right-relop diamond hoists over
side-effecting left operand; variant record cross-arm aliasing not supported (non-tested).

NEXT — Lon picks from open areas: (a) PB-26 — array value params (one-liner fix in lower_program.c, recipe in handoff); (b) 3D arrays; (c) named-type value params (int/real/record) — all gated on PB-26 fix.

**Session 26 (2026-06-06): PB-16 (read/readln/eof/eoln) + PB-17 (abs/trunc/odd/pred/succ) LANDED.**
Gate: **m2 65/1** over 66 probes; sole fail = recursion.pas (16-bit maxint pin, XFAIL).
Commits: SCRIP `4e4cbf8`, corpus `80e95e7` (read1-4 + .in files, stdlib1).
m3/m4 pre-existing failures unchanged (marshal_call_arg root cause, not touched this session).

Mechanism (PB-16): `read(v)` → parser emits `mk_assign(v, mk_fnc0("__pas_read_i"))` for int vars,
`mk_assign(v, mk_fnc0("__pas_read_c"))` for charvars; `readln` with no args → `mk_fnc0("__pas_readln")`;
`readln(v,...)` → seq of reads + readln; bare `eof`/`eoln` identifiers → `mk_ident` intercepts and
emits `mk_fnc0("__pas_eof")`/`mk_fnc0("__pas_eoln")` (critical: `eof` appears as bare selector in
expression, not as `call_with_args`, so intercept is in `mk_ident` not `mk_call`).
Runtime: `__pas_read_i` = `scanf(" %lld", &v)`; `__pas_read_c` = `getchar()` (no ws-skip);
`__pas_readln` = drain to `\n`; `__pas_eof` = peek getchar/ungetc; `__pas_eoln` = peek for `\n`.
Probes with stdin use `.in` companion files; gate uses `inp=${base}.in` when present, else `/dev/null`.

Mechanism (PB-17): all pure parser transforms in `mk_call`:
`pred(i)` → `TT_SUB(i, 1)`; `succ(i)` → `TT_ADD(i, 1)`;
`trunc(r)` → `mk_fnc1("__pas_trunc", r)` (runtime: `(long long)d`);
`abs(x)` → `mk_fnc1("__pas_abs", x)` (runtime: int or real absolute value);
`odd(i)` → `bin(TT_NE, bin(TT_MOD, i, ilit(2)), ilit(0))` (raw relop — NOT pre-wrapped in pas_bool;
pre-wrapping caused a double-diamond IR_BINOP(NE, IR_IF(...), 0) with null α/β that the interpreter
short-circuits to FAILDESCR).

RESIDUES (carry-forward): char literal in write position prints as int; charvar table global/unscoped;
recursion.pas XFAIL (per-arg eager writeln vs all-args-first evaluation order).

NEXT — Lon picks: (a) more stdlib (sqrt/sin/cos/ln/arctan — pint csp 14-19); (b) packed-array/alfa;
(c) 16-bit maxint close (recursion.pas); (d) write(real:w:d) two-width specifier (wrr).

NOTE: 16-bit maxint (recursion.pas) stays XFAIL. The mismatch is that pint writes k=8 before
computing fact(8) (sequential P-machine ops), while SCRIP's __pas_writeln evaluates all args
before writing any. Reproducing the partial row requires per-arg eager writeln output; the
TT_SEQ_EXPR desugaring approach breaks m3/m4 (computed-expr args in SEQ_EXPR via IR_CONJ
don't emit correctly in native mode — pre-existing limitation). Not worth fixing in isolation.

PRE-EXISTING m3/m4 REGRESSION (not from PB-15): computed-expression args to __pas_writeln
fail in m3/m4 (e.g. writeln(2+3), writeln(p.x+p.y), writeln(c) where c is charvar). Root
cause: ICN-HY-7g (bc95d97) deleted marshal_call_arg operand-kind arms that Pascal computed
args rely on. m2 gate is clean (60/1); m3/m4 have 28 pre-existing failures including rec1/2/3,
bool*, goto1/2/3, ptr1/2/4/5/6/8, set2/5/6/7, m4wexpr, nestfunc, nestrec, with1/2/3,
char1/2/3. ICN-SCAN session owners should stash-prove these against bc95d97 and fix marshal_call_arg.

RESIDUES (documented, no probe): (1) right-relop diamond hoisted over a side-effecting left operand
reorders evaluation vs pcom's strict l-to-r; (2) NV `__pbt`/`__pct` temps can clobber under recursive
re-entry of the same expression (frame-slot temps would cure); (3) case no-match: pcom emits ujc →
pint halts "value out of range"; our if-chain silently continues (error trap = runtime work, out of
parser scope); (4) labels nested inside compounds register + lower but no probe pins that position
(probes pin top-level labels + nested gotos); (5) char literal directly in write position (`writeln('A')`)
prints integer 65 not `A` — write call site has no type info for plain ilit; (6) charvar table
global/unscoped — param name shadows across nested procs with different types (doesn't affect probes).

Open ladder item: **LB-7-NEW** — `# BOX ICN` tag inventory in bb_gen_scan/bb_keyword/bb_scan_*
(ICN-SCAN sessions own these files; sweep when ICN-SCAN settles).

---

## Mechanism inventory (how it works NOW)

- **Rail:** parser tag `LANG_PASCAL`=6, IR tag `IR_LANG_PAS`=7, body walker `lower_pascal_body`
  (`lower_program.c`). Parser emits real AST (TT_FOR/TT_REPEAT/bare-TT_IF; TT_PROC_DECL c[3]=ret-var
  iff function). LOWER dispatch: outer `switch(tree->t)` → inner `switch(cx.lang)`. Driver mode-2 =
  the `!is_icon && !is_prolog` branch in `scrip.c` → finds `main` → `IR_interp_once`.
- **Frame-as-BB:** nested frames + static links ride the parent-port thread; `[fb+0]`=SL,
  `[fb+16+k*16]`=DESCR slot k; hop chains are emit-time constants. Var params = cell addresses
  ({tag 0, ptr} DESCRs, verbatim 16-byte copy); REF kinds `IR_VAR_FRAME_REF`/`IR_ASSIGN_FRAME_REF` =
  one extra indirection. Migration trigger: `decl_level>1 || byref_mask`; main + flat programs stay NV
  (`rt_gvar_cell` gives NV globals stable cells).
- **Calls:** registered dval 2|3 → `bb_call_gvar_userproc_str` → `rt_call_named_proc(_sl)`;
  unregistered → `bb_call_byname_str` → `rt_call_arr`; DEFINE rides dval=5. `marshal_call_arg`
  γ-chases each arg subgraph to its final node; inlines CALL + nested-BINOP operands across BOTH binop
  layouts (direct α/β pointers AND the PEERS `operand_aux` sidecar — sidecar is keyed to the ARG
  SUBGRAPH's own graph, so `sg` is threaded through the marshal chain). Relop-diamond args: CMP +
  conditional INTVAL(0/1) store; TEXT internal labels keyed by `bb_node_id(relnd)`.
- **Booleans:** stored true=INTVAL(1)/false=INTVAL(0). Conditions wrap via `pas_cond` (`expr ≠ 0`);
  `and`/`or` = TT_MUL/TT_ADD (correct on 0/1 inputs); `not` = `pas_flip_rel(pas_cond)`. Relop
  assigned to a VAR or bare-funcname selector → parser statement-IF rewrite (`x:=1`/`x:=0` arms);
  other destinations (`a[i]`, `p^.f`) → `pas_bool` diamond in call-arg position, covered by the
  marshal arm. Relop as arith operand → `pas_bool_diamond` (lower.c): the diamond is HOISTED as a
  chain prefix with a bare `IR_VAR(__pbtN)` left in operand position — forced by
  `gvar_stmt_operand_refs`' stack simulation (a consumer's operands must be the most recent γ-spine
  pushes; IR_IF arity −1 = stack reset breaks any in-place diamond).
- **goto/label (PB-12):** parser → `TT_GOTO_U`(sval=label digits, strdup'd) + `TT_LABEL_DEF`(sval,
  c[0]=stmt). `lower_pascal_body` pass-1 recursively pre-registers one IR_SUCCEED landing per label
  (`bb_label_registry_*`, reset per body = per-proc scoping; both goto directions resolve). The
  `TT_LABEL_DEF` arm wires landing→γ to the inner α and exposes the LANDING as the statement's α;
  `TT_GOTO_U` lowers to an IR_SUCCEED hop with γ pinned to the landing (γ_in ignored). Zero new IR
  kinds, zero template work — m3/m4 came free. Intra-procedure only, matching pcom error 399.
- **I/O:** `__pas_writeln`/`__pas_write` take interleaved (value,width) pairs; int right-justified in
  max(w,digits), default width 10 (real 20); `:w` is a minimum. `__pas_sqr(x)`=x*x.
- **Char (PB-15):** chars stored as integer ordinals. `scalar_constant: STRINGCONST` len=1 →
  `(long long)s[0]` (for const/case/for-bounds). `factor: STRINGCONST` len=1 → `ilit(ord)`.
  `ord`/`chr` both → identity. `var c:char`/value-param `x:char` → `pas_charvar_add`. Write path:
  charvar args wrapped with `mk_chr_wrap` (→ `TT_FNC(__pas_chr, val)`) + width sentinel `-2`
  (default char width = 1). `__pas_chr` runtime: ordinal → 1-char GC string. Width `-2` →
  `fputc`; width ≥0 → `fprintf("%*s", w, s)`. Char lit in write position prints as int (no type
  info available at write call site for plain ilit). Charvar table global/unscoped (probes unaffected).
- **Arrays/records/pointers:** TT_IDX faithful in parser; LOWER → `arr_get`, `a[i]:=v` →
  `a := arr_set_pure(a,i,v)` (no auto-grow; parser prepends an init prologue sizing to high+1).
  Records = field-index arrays; `p^` = `__pas_deref`, `p^.f := v` = `__pas_field_set`,
  `new(p)` = `__pas_alloc(_rec)`. Sets = `__pas_set{,uni,int,dif}`/`__pas_in`.
- **case (PB-11):** parse-time desugar, no new IR. `case e of …` → TT_SEQ_EXPR(`__pctN := e`,
  if-chain): each arm = TT_IF(pas_cond(or-chain of `__pctN = const`), stmt) folded right-to-left into
  else slots; multi-label = TT_ADD of EQ diamonds (boolchain-proven). Temp stack depth 8 (nested
  cases), names strdup'd per leaf, counter reset per parse; labels = folded integer constants only.
- **Functions:** body ends with IR_RETURN(dval 0) whose α reads `IR_VAR(funcname)`; `f := …` writes
  the NV global (recursion-safe). Parse-time tables (reset per parse): const folding, array
  name→high, true/false→ilit(1/0), sqr→__pas_sqr.

## Target dialect — the P4 subset, NOT full ISO 7185

The language `pcom` actually compiles; spec = `pcom.pas` const block + `grammar/pascalp.y`. integer
is **16-bit maxint=32767**; real, char, boolean, enum, subrange, array, record, set (small base,
`0..58`), pointer (`new`); value + var params; nested routines; files = predefined text only; goto
intra-procedure only. Absent: first-class strings, `dispose`, later ISO. If pcom rejects a probe it
is out of scope, not a bug.

## ⚖ Provenance guardrail

The SCRIP Pascal frontend is original C. `pcom.pas`/`pint.pas` are a private behavioral oracle —
never transliterated into the lowering, never linked, never shipped. Syntax reference = the MIT
grammar; semantics = pint's observable behavior. Read what a construct means, then write the C
yourself.

## Invariants

No AST walking in modes 2/3/4. Zero C Byrd-box functions — a Pascal frame is a BB. Four ports
hard-wired (α β γ ω; static link on the parent-port thread). UPPERCASE builds IR, lowercase consumes.
THE RULE: modes 3/4 emit no byte outside a BB/SM/XA opcode via `bb_emit_x86`; `bb_bin_t` abolished.

## Where things live

| Thing | Path |
|-------|------|
| Reference compiler / P-machine (oracle) | `corpus/programs/pascal/pcom.pas` / `pint.pas` |
| Token + grammar blueprint (MIT) | `corpus/programs/pascal/grammar/pascalp.{l,y}` |
| Probes | `corpus/programs/pascal/*.pas` |
| Frontend | `src/parser/pascal/pascal.{l,y}` |
| Lowering | `src/lower/lower.c` + `lower_program.c` |
| Mode-2 interp | `src/interp/IR_interp.c` |
| BB templates (m3/m4) | `src/emitter/BB_templates/` |

Start every Pascal session by reading the reference grammar (`pascalp.l` tokens, `pascalp.y`
productions) for the constructs in play.

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/SCRIP/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }
make libscrip_rt
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
( cd /home/claude/corpus/programs/pascal && apt-get update -qq && apt-get install -y fpc \
  && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas )
```

Gate (no checked-in script): oracle `./pcom < p.pas && cp prr prd && ./pint < /dev/null`; m2
`--interp`; m3 `--run`; m4 `--compile > p.s` then `gcc -no-pie p.s out/libscrip_rt.so
-Wl,-rpath,SCRIP/out`. Suite = all `*.pas` minus pcom/pint/ppp; `timeout 8s` + `< /dev/null` per
RULES; recursion.pas = XFAIL.

## ⚠ Landmines (each has cost real time)

1. `rm -f scrip` before `make scrip` — the target has no prerequisites; edits silently don't take.
2. Pascal regen ONLY via `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y` (1 s/r =
   dangling-else, expected). NEVER the full regen script (it deletes snobol4.lex.c).
3. `touch` templates before `make scrip` after any template edit.
4. fpc on this image: `apt-get update` first, then plain `apt-get install -y fpc`.
5. Concurrent pushes land mid-session: every `git pull --rebase` → `rm -f scrip && make` → FULL gate
   re-run. Byte-identity baselines go stale at every rebase — stash-prove against the rebased base,
   never against pre-rebase captures.
6. Never assume per-box uid for TEXT internal labels on the Pascal gvar flat chain — the whole chain
   shares one `_.x86_uid`; key labels by `bb_node_id`.
