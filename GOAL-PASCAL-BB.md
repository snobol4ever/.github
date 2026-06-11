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

**Session 39 (2026-06-11): PB-30 — IR_WHILE infinite-loop fix landed. Gate 101/0.**
Gate: **m2 101/0** (101 probes, +1 new pb30.pas). SCRIP `da7b809`, corpus `7a963f57`.

**Fixed this session:**
- **IR_WHILE infinite loop on set-membership while-conditions** (`src/interp/IR_interp.c`).
  The `IR_WHILE` handler called `IR_interp_node(cnd)` once and checked `IS_FAIL_fn(IR_EXEC(cnd).value)`.
  For conditions like `while sy in statbegsys` the parser wraps via `pas_cond()` as
  `TT_NE(TT_FNC(__pas_in,...), ILIT(0))`. The entry node is the `__pas_in` CALL which always returns
  INTVAL(0/1), never FAILDESCR. The downstream BINOP_NE that converts 0→FAIL was never reached.
  Result: `while sy in set` inside any outer loop (for, repeat) ran forever.
  Fix: replaced single-shot call with a mini chain-walk loop mirroring `IR_interp_once` semantics —
  walks from `cnd` through γ edges calling `ag_ring_push` at each step, stops when `cur==bb` (WHILE
  node reached via ω = condition false) or FAIL. Covers all non-relop while conditions including
  set-membership, boolean-func, and any compound non-relop expression.
  Bisect confirmed: `for i:=1 to 3 do begin sy:=5; while sy in s do ... end` — for 1..2 passed,
  1..3 hung. Zero-iteration while (sy not in set) also hung on 3rd for-iteration proving spurious
  condition fire, not body loop.
- **New probe:** `corpus/programs/pascal/pb30.pas` — 20 cycles of `while sy in funcprocsy` +
  `repeat statement until not (sy in statbegsys)`. Was timeout; now correct (20/120/20).

**pcom.pas status after fix:**
- `scrip --interp pcom.pas < hello.pas` STILL exits after line 1 (`     1        9 program hello;`).
  The IR_WHILE fix removes one blocker but another survives. The while-sy-in-[procsy,funcsy] in
  block() is now correct; the early exit is in a different path inside body()/compoundstatement()/
  statement() call chain for the actual writeln('Hello World!') statement.
- `program x; begin end.` HANGS (timeout). Truncated input (no begin/end) causes pcom's insymbol
  to print `*** eof encountered` in a tight loop (expected pcom behavior for truncated input, not
  a SCRIP bug). The hang with complete input is a separate blocker from the while-set fix.
- Isolated constructs all pass: block/body repeat-until-set, statement dispatch with setuni,
  setofsys-param procs, nested call chains. The remaining blocker only manifests at pcom scale.

**NEXT — PB-30 continues:**
Write a probe that exactly mirrors pcom's `programme()→block()→body()→compoundstatement()→
statement()` chain at full call depth with the correct set-membership conditions at every level:
- `programme`: `repeat block until (sy=period) or eof`  
- `block`: `repeat [while sy in [procsy,funcsy]] until (sy in statbegsys) or eof` + `repeat body until (sy=fsy) or (sy in blockbegsys) or eof`
- `body`: `repeat repeat statement until not (sy in statbegsys); test:=sy<>semicolon until test`
- `statement`: `if sy in statbegsys+[ident] then case sy of ident: call(...)`
Run this at the same token sequence as `program hello; begin writeln(...) end.` to isolate which
of these constructs produces the early exit. Candidates: (a) body()'s outer `repeat body until
(sy=fsy) or (sy in blockbegsys)` — the `sy in blockbegsys` part is a set-membership condition
inside a repeat, which goes through lower_repeat's NE-wrap path; (b) statement()'s
`if sy in statbegsys+[ident]` — a set-union then set-membership in an if-condition.

**Fixed this session (Session 37 fix summary retained for reference):**

**Fixed this session:**
1. **Char-by-char `alpha` never matched a bulk `alpha` under `=`/`<>`** (`lower_program.c` `binop_apply`).
   Concurrent commit `1c687d2` had already added the both-operands-string arm (slen-aware `memcmp` lexical
   compare, CSET excluded) that fixed the old "two strings → `(long)lv.r` union garbage → everything EQUAL"
   bug. But that `memcmp` compares RAW bytes, and the two `alpha` build methods diverge: a char-by-char
   `alpha` (`id[k]:=ch`) is a SOH(0x01)-delimited string of integer ORDINALS with a leading "0" element-0
   filler, while a bulk `alpha` (`id:='do      '`) is a plain packed string — so raw `memcmp` never matched
   them (the "chararr elementwise stores" blocker 1c687d2 left noted/unfixed). FIX: added static helper
   `pas_norm_charseq(DESCR_t)` that decodes the SOH-ordinal form to the logical char string (per segment:
   all-digits→`chr(value&0xFF)` skipping value==0 filler, else literal bytes; no SOH→string as-is), and
   applied it inside 1c687d2's string-relop block **only when a 0x01 is present** in an operand — so normal
   (non-array) strings, incl. SNOBOL4/Icon, are byte-for-byte unchanged. pcom's reserved-word lookup
   `rw[i]=id` (bulk `rw[]` table vs char-by-char `id`) now classifies correctly (blocker i gone).
2. **For-loop with a complex `to` bound severed all continuation after the loop completed**
   (`lower_pascal_nl.c` `lower_for`). EXPOSED once `=` worked (the old always-true compare fired the inner
   `goto` on iteration 1 every time, so loop-completion paths never ran). The limit `BINOP` reads its
   operands from the bounded `ag_ring` (no explicit aux), and `lower_for` RE-WALKED the `to` subgraph every
   iteration. A complex `to` (e.g. `frw[k+1]-1` = an `arr_get` CALL + lit + SUB) pushed ~3 values/iter onto
   the ring; the churn eventually corrupted the ring state the procedure RETURN relied on → after a
   completed array-bound loop, ALL subsequent statements were silently dropped (no hang, exit 0). Bisected:
   `D1` (param proc, LITERAL bound) works; `D2` (no-param proc, `frw[]` ARRAY bound) severs; source-level
   cache (`hi:=frw[3]-1; for i:=… to hi`) works → confirms re-eval is the cause, NOT the parameter. FIX:
   evaluate `to` ONCE on the init path; give `lim_cmp` explicit `bb_operand_aux_set` (aux[0]=`lim_var`,
   aux[1]=`to_res`=`all[to_mark]`, the once-computed limit node) so the limit is read from the cached node
   value rather than re-walked; loop-back goes increment→`lim_var`→`lim_cmp` (skips `to_entry`). Also
   ISO-Pascal-correct (limit evaluated once at entry). Touches ALL for-loops → full gate re-run 100/0.
   Regression probe: `alphacmp.pas` (exact pcom reserved-word mechanism: bulk `rw[]` table vs char-by-char
   `id`, with empty-bucket + no-match calls). NOTE probes must use `(* *)`, NOT `{ }` (P4 rejects braces).

**REPRESENTATION fact (used by fix 1):** `var id: alpha` (=`packed array[1..8] of char`) init prologue
builds a 9-slot SOH array (indices 0..8, all `"0"`). `id[k]:='d'` pokes `__pas_chrlit(100)` → the array
stores the decimal ORDINAL "100" at raw slot k (slot 0 unused = "0" filler; element reads in write
position get `__pas_chr`-decoded, so chararr1/2 still pass). Bulk `id:='do      '` OVERWRITES the prologue
with a plain 8-char string. So the two build methods diverge; `pas_norm_charseq` reconciles them. (Whole-
array `writeln(id)` of a char-by-char array still prints raw ordinals — separate write-path bug, no probe.)

**Active lowering path reminder:** `nl_on(1)` defaults TRUE → Pascal uses the **NL lowering**
(`src/lower/nl/lower_pascal_nl.c`: `lower_if`/`lower_while`/`lower_for`/`lower_repeat`/`lower_seq`). Edit
the NL functions, not `lower.c`'s `v_if`/`v_repeat` (the `SCRIP_NL=0` path).

**pcom.pas status — blocker (i) resolved; still incomplete downstream:**
- blocker (i) GONE: classification correct, line-1 listing emits `     1        9 program hello;` with NO
  spurious `**** ,` error. The array-bound-loop sever (the largest part of old blocker (ii)) is fixed.
- STILL FAILS — two distinct input-dependent downstream symptoms past the header:
  - `hello.pas` → emits line 1 correctly, then exits 0 EARLY (continuation lost after the program header,
    before lines 2-4).
  - minimal `program x; begin end.` → HANGS (timeout 30s, ~1 byte out).
  Both are downstream of the two fixes, in paths beyond simple for-loops — likely the `programme()`→
  `block()` transition, output flush, and/or ANOTHER construct (while/case/nested call) that re-evaluates a
  complex expression and churns the `ag_ring` the same way the for-loop did. pcom's `output` buffers
  independently of `stdbuf` so line-by-line visibility needs instrumentation.

NEXT — Lon picks:
**(a) PB-30** — next probe: write a program that exactly reproduces block()'s structure (setofsys param +
`while sy in [procsy,funcsy] do` + `repeat body_stub(fsys+[casesy])` with nested call inside body_stub
mirroring statement()'s call-dispatch path), fed with beginsy input, to see if `sy in statbegsys` with
a setofsys-as-global causes ag_ring churn at scale. Also audit `lower_while` in lower_pascal_nl.c for
the same re-walked-complex-cond pattern the for-loop fix addressed.
**(b)** Any open bug (case no-match; __pbt/__pct clobber; --dump-ast segv on huge AST).

**Gate harness note:** Use `/tmp/run_gate.sh` (checked against `.ref` files + `.in` for stdin probes):
```bash
cat > /tmp/run_gate.sh << 'EOF'
#!/bin/bash
cd /home/claude/corpus/programs/pascal
PASS=0; FAIL=0; XFAIL=0; FAILS=""
for f in *.pas; do
    case "$f" in pcom.pas|pint.pas|ppp.pas) continue ;; esac
    base="${f%.pas}"
    [[ "$f" == "recursion.pas" ]] && { XFAIL=$((XFAIL+1)); continue; }
    [[ ! -f "${base}.ref" ]] && { echo "SKIP (no ref): $f"; continue; }
    inp=/dev/null; [[ -f "${base}.in" ]] && inp="${base}.in"
    expected=$(cat "${base}.ref")
    got=$(timeout 6s /home/claude/SCRIP/scrip --interp "$f" < "$inp" 2>/dev/null)
    if [[ "$expected" == "$got" ]]; then PASS=$((PASS+1))
    else FAIL=$((FAIL+1)); FAILS="$FAILS $f"; fi
done
echo "PASS=$PASS FAIL=$FAIL XFAIL=$XFAIL"
[[ -n "$FAILS" ]] && echo "FAILING:$FAILS"
EOF
chmod +x /tmp/run_gate.sh && bash /tmp/run_gate.sh
```


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
