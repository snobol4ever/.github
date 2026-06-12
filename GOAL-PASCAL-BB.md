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

**Session 41 (2026-06-12): Three runtime bugs fixed; pb40 LANDED; gate 103/0. pcom blocker #3 root-caused.**
Gate: **m2 103/0** (+pb40). Commit hashes: see git log (SCRIP + corpus pushed this session).

**pcom blocker #3 — ROOT-CAUSED, FIX PENDING (start here next session):**
- Symptom: `program t; begin writeln(42) end.` → pcom generates 3 position-0 errors at line 2 (any program without `(...)` file list errors). `program t(output); begin writeln(42) end.` compiles clean.
- Errors are at chcnt=0: generated right after `endofline` resets chcnt but before first nextch on the new line. Points to pcom state set by the extra `insymbol` calls that process the file list being absent when there is no file list.
- `kk` (initialized to 8 in `initscalars`), `id`, `eol`, or chcnt sequencing is the likely culprit. Next session: bisect pcom insymbol + block entry to isolate which state differs.
- Smoke: `echo "program x; begin end." | scrip --interp pcom.pas` → listing only, no errors (passes).

**Fixed this session:**
- **arr_get FAILed on element reads of bulk-assigned char arrays** (session-40, reference) (`src/runtime/by_name_dispatch.c` arr_get, ~line 1126).
  Bulk assign `src := 'x.        '` stores a PLAIN string (no SOH); arr_get only walked
  SOH-delimited segments, so `ch := src[i]` returned FAILDESCR for any i>=1, silently severing
  continuation (straight-line: silent early exit; inside repeat/while ω-cycles: spin until the
  IR_interp_once safety counter bails — i.e. an apparent hang). READ-path twin of the session-37
  pas_norm_charseq relop fix. Fix: one guarded arm before the SOH walk — if no SOH present and
  1 <= idx <= strlen, return INTVAL(ordinal of cur[idx-1]) (1-based packed read, matches
  elem_to_descr's INT convention). idx==0 and OOB behavior unchanged; SOH arrays unchanged.
- **New probe:** `corpus/programs/pascal/pb39.pas` (+.ref) — bulk-assign then element reads,
  straight-line and in a repeat. Was silent-exit; now correct.

**pcom blocker #2 — ROOT-CAUSED, FIX PENDING (start here):**
- Minimal reproducer: **`corpus/programs/pascal/pb40.pas`** (intentionally NO .ref → gate skips).
  Structure: a case arm containing `if c then s else <repeat or while>;` followed by a for-loop.
  Oracle prints `0`; SCRIP silently exits (small graph) / appears to hang (pcom-size graph).
- Mechanism (verified by IR dump of the reproducer, `scrip --dump-bb`): the for-loop's exit edge
  (limit-compare BINOP's ω) is wired to the PRECEDING if-statement's IR_IF marker node instead of
  the next statement. The IR_IF handler (IR_interp.c ~2843), when reached, evaluates its condition
  and returns bb->γ — which points at the for-INIT → cycle: for-init → limit-compare fails →
  IR_IF → γ → for-init, forever. Runtime path irrelevant (then-branch taken also fails);
  empty/non-empty for range irrelevant (any for-exit enters the cycle). This is the insymbol
  rw-lookup spin: `for i := frw[k] to frw[k+1]-1` re-reads both bounds endlessly after the
  letter-token case-arm's `if k >= kk then ... else repeat id[kk]:=' '...` — explains BOTH
  original symptoms (hello.pas early exit + `program x; begin end.` hang).
- Reproducer ladder kept in this note for re-derivation if needed: case+if/else-loop+for FAILS
  (pb40); remove the case → passes; remove the else-loop → passes; replace for with plain stmt →
  passes; while-in-else also fails; goto/label NOT required; chararr NOT required.
- **NEXT:** fix the wiring in `src/lower/nl/lower_pascal_nl.c` (lower_if continuation/ω handling
  when an else-branch contains a loop and a for-statement follows inside a case arm) — or make
  IR_IF reached-via-ω fail through to its own ω instead of returning γ. Verify with pb40 (then
  add pb40.ref = `0`), then `echo "program x; begin end." | scrip --interp pcom.pas` (expect the
  ';' to echo and parsing to proceed), then hello.pas end-to-end, then full gate.
- After blocker #2: pcom may surface further blockers; the per-char echo listing makes the
  bisection loop fast (`stdbuf -o0`, watch where the echo stops; strace shows pure-CPU spin vs IO).

**Refactor request (Lon, session 40): dynamic arrays everywhere.**
Replace fixed-cap arrays/stacks/queues (FRAME_SLOT_MAX=64 Scope.e, FRAME_STACK_MAX=256
frame_stack, SNO_SAVE_MAX=4096, NAME_SAVE_MAX, rt_frames, etc.) with malloc/calloc/realloc/free
dynamic growth — Lon explicitly wants realloc-style one-line insert/delete idioms. Notes from
session 40: (1) wrap as xrealloc — realloc(p,0) is implementation-defined (C17) / UB (C23);
map size 0 → free+NULL to keep the idiom portable. (2) GC HAZARD: arrays holding DESCR_t roots
(frame_stack, g_sno_save, Scope) are statics that Boehm GC scans automatically; plain-malloc'd
replacements are INVISIBLE to the collector → use GC_malloc/GC_realloc (GC_malloc_uncollectable)
or GC_add_roots for descriptor-bearing arrays; plain realloc is fine for non-DESCR metadata.
(3) Known silent-truncation sites to kill: lower_program.c scope build (~560, ~700, ~720),
IR_interp.c dval==3.0 IR_CALL scope copy (~2426, no guard — truncates >64 silently),
invocation.c nslots clamp, rt.c rt_frames.

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
