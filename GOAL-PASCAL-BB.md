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

**Session 30 (2026-06-08): PB-26 LANDED — named-type array var init fix.**
Gate: **m2 77/0** over 78 probes (recursion.pas XFAIL).
Commits: SCRIP `6b4ff36`, corpus `39d39d11`.

**CRITICAL: Upstream force-push collision.** FIX-7a commit (`7c7fe07`) force-updated SCRIP main, erasing session 29 SCRIP commit `2daa9d0`. PB-24 (2D arrays) and PB-25 (matmul/markrel/forward1 probes) pascal.y code are **permanently lost**. Probes arr2d/arr2d2/arr2d3/arr2denum/matmul/markrel/forward1 removed from corpus. Must re-implement PB-24 2D arrays next.

**PB-26 bug (named-type array vars):** `type vec = array[0..4]; var v: vec` — `v` never registered in `g_pas_arrays[]` because `type → simple_type → IDENT "vec"` always returned -1 (array high was thrown away). Fix: added `g_pas_arrtypes[64]` table in `pascal.y`; `type_decl` registers named array types; `type → simple_type` now propagates high for named array types; `simple_type IDENT` looks up `g_pas_arrtypes`. Also: `lower_program.c` nparams redundancy clarified. New probes: `arrparam.pas`, `intparam.pas`, `realparam.pas`.

NEXT — Lon picks:
**(a) PB-24 RE-IMPLEMENT** — 2D comma-syntax arrays (lost; see handoff for full recipe).
**(b) PB-27** — record value params (same root cause; `recparam.pas` fails).
**(c) More named-type value params.**


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
