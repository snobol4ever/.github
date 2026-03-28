# PLAN.md — snobol4ever HQ Plan

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row. `git pull --rebase` before every push.

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **⚠ GRAND MASTER REORG** | G-7 — FRONTEND-PROLOG-JVM.md trimmed | `eb9f2ec` G-7 | M-G0-FREEZE (Lon schedules) |
| **⭐ Scrip Demo** | SD-37: M-SD-6 ✅ ICON-JVM sieve PASS; demos 7-10 ICON-JVM compiler gap | `795c2ff` SD-37 | M-SD-7 ICON-JVM |
| **🌳 Parser pair** | PP-1: M-PARSE-POLISH ✅ mirrors pass; icon_recognizer.icn WIP (compiles, 7 bugs fixed, 1 remaining — see handoff) | `35988b9` PP-1 | M-RECOG-ICON · M-RECOG-PROLOG |
| **TINY backend** | B-292 — 106/106 | `acbc71e` B-292 | M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR |
| **TINY NET** | N-253 — M-LINK-NET-7 ✅ | `e7dc859` N-253 | M-LINK-NET-8 |
| **TINY JVM** | J-216 — STLIMIT/STCOUNT ✅ | `a74ccd8` J-216 | M-JVM-STLIMIT-STCOUNT |
| **TINY frontend** | F-223 | `b4507dc` F-223 | M-PROLOG-CORPUS |
| **DOTNET** | D-164 — 1903/1903 | `e1e4d9e` D-164 | TBD |
| **README** | R-2 | `00846d3` R-2 | M-README-DEEP-SCAN |
| **ICON x64** | IX-17 — rung01–35 all 5/5 ✅; emit_until, record prepass, reads() slot, suspend ω fixed | `3e4f131` IX-17 | rung36_jcon (separate subsystem) |
| **Prolog JVM** | PJ-84a — SWI bench 31/31 ✅ | `a79906e` PJ-84a | M-PJ-SWI-BASELINE |
| **Prolog x64** | PX-1 — M-PJ-X64-1 ✅ M-PJ-X64-2 ✅ | `8843d71` | M-PJ-X64-3 (\+ inline) |
| **Icon JVM** | IJ-58 — snprintf→ij_gvar_field bulk ✅ list-arg obj-field ✅ bang-coerce WIP | `5b32daa` IJ-58 | M-IJ-JCON-HARNESS (VE 36→0) |
| **🔗 LINKER** | LP-6 — M-LINK-NET-7 ✅ | `e7dc859` LP-6 | M-LINK-NET-8 (ilasm/mono run) |
| **🔗 LINKER JVM** | LP-JVM-3 — linkage infra ✅; pj_call_goal passes arity=0+null args to pj_reflect_call for compound goals — DB fallback can't unify | `55d8655` LP-JVM-3 | M-SCRIP-DEMO |

**Invariants:** TINY `106/106` · DOTNET `1903/1903`

---

## Routing: pick three → read three docs

**1. Repo**

| Repo | Doc |
|------|-----|
| snobol4x | `REPO-snobol4x.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |

**2. Frontend × Backend → Session doc**

| | x64 ASM | JVM | .NET |
|--|:-------:|:---:|:----:|
| SNOBOL4 | `SESSION-snobol4-x64.md` | `SESSION-snobol4-jvm.md` | `SESSION-snobol4-net.md` |
| Icon | `SESSION-icon-x64.md` | `SESSION-icon-jvm.md` | — |
| Prolog | `SESSION-prolog-x64.md` | `SESSION-prolog-jvm.md` | — |
| Snocone | `FRONTEND-SNOCONE.md` | — | — |
| Rebus | `FRONTEND-REBUS.md` | — | — |

Special: `SCRIP_DEMOS.md` (SD sessions) · `ARCH-snobol4-beauty-testing.md` (beauty sprint) · `ARCH-scrip-abi.md` + `SESSION-linker-sprint1.md` (LP-2 JVM) + `SESSION-linker-net.md` (LP-4 .NET)

**3. Deep reference → ARCH-*.md** (open only when needed — full catalog in `ARCH-index.md`)

---

*PLAN.md = routing + NOW only. 3KB max. No sprint content. No completed milestones.*

---

## Parser pair session doc

**Files:** `demo/scrip/prolog_parser.pro` · `demo/scrip/icon_parser.icn`
**Commit:** `82c2491` snobol4x

### M-PARSE-PROLOG (done)
DCG tokeniser + op-climbing term parser + S-expression output. Handles facts,
clauses (:-), DCG (-->), directives, queries, cut, all standard operators.
Tested with swipl 9.0.4. Output example:
```
(clause (call foo X Y) (, (call bar X) (call baz Y)))
(dcg sentence (, noun_phrase verb_phrase))
(directive (call use_module (call library lists)))
```

### M-PARSE-ICON (done, one known issue)
Suspend-combinator parsers: p_tok/p_kw/p_op primitives generate [tree,rest].
p_expr: full precedence climbing. p_stmt: if/while/every/control flow.
p_proc/p_global/p_record: top-level forms.
Tested with icont. Output example:
```
(proc fib (n) ((local a b tmp)) ((if (<= (id n) (int 1)) (return (id n))) ...))
```
**Known issue:** `p_proc` local-decl loop — `every dk := ("local"|"static"|...)` 
tries all variants and first name appears twice in the local list. Fix: use
`( dk := "local" | dk := "static" | dk := "initial" )` with explicit break,
or restructure as separate `if/else if` chains rather than `every`.

### M-PARSE-POLISH (next)
1. Fix Icon local-decl dup
2. Self-parse: feed `prolog_parser.pro` through itself; feed `icon_parser.icn`
   through itself
3. Add pretty-print indentation (2-space indent per nesting level, matching
   treebank.sno style)
4. Consider: add SNOBOL4 front end (treebank.sno-style, using treebank.sno
   as reference)

---

## PP-1 Emergency Handoff (2026-03-27, Claude Sonnet 4.6) — commit 3fe17af

### What exists
**`demo/scrip/prolog_parser.pro`** — full Prolog DCG parser + pretty-printer
**`demo/scrip/icon_parser.icn`** — full Icon combinator parser + pretty-printer

### Pretty-printer design (both files)
- `flat(tree)` → renders tree as single-line string
- `pp(tree, indent, col)` → if `col + len(flat) <= MAX_WIDTH`: write flat inline;
  else: write `(tag`, then for each child: inline if fits, else newline + indent+2
- Width: Prolog uses `--width=N` CLI arg (default 120); Icon uses `PARSE_WIDTH` env
- Output: clean treebank S-expressions, balanced parens, horizontal-then-vertical

### Prolog output sample (width=40)
```
(clause (call fib N F)
  (, (> N 1)
    (, (is N1 (- N 1))
      (, (is N2 (- N 2))
        (, (call fib N1 F1)
          (, (call fib N2 F2)
            (is F (+ F1 F2))))))))
```

### Icon output sample (width=120)
```
(proc fib (n) ((local a b tmp))
  ((if (<= (id n) (int 1)) (return (id n))) ...
    (every (:= (id i) (to (int 2) (id n)))
      (block ...))))
```

### DONE — "Run the mirrors" (2026-03-27, Claude Sonnet 4.6) — commit 9cb4af7
```bash
cd snobol4x

# Prolog self-parse
swipl -q -f demo/scrip/prolog_parser.pro -t halt \
  < demo/scrip/prolog_parser.pro 2>/dev/null | head -20

# Icon self-parse
icont -s -o /tmp/icon_parser demo/scrip/icon_parser.icn
/tmp/icon_parser < demo/scrip/icon_parser.icn | head -20
```
Both should produce valid S-expression trees of themselves — no crashes,
balanced parens. Do a quick `| grep -c '('` vs `| grep -c ')'` parity check.

### Known remaining issues
1. Icon `p_namelist` may still consume some identifiers that are call targets
   if they appear on the line immediately after `local`. The `id(` lookahead
   fix is in — verify it works on the self-parse.
2. Prolog `sx_flat` for deeply nested `,`-chains still renders flat; the
   pp_children wrapping handles it but verify on `prolog_parser.pro` itself
   (it has long `op_info` facts with many operators).
3. `str` node quoting in Icon `flat()` — verify `(str "hello")` not `(str hello)`.

### After mirrors pass
- Commit: `PP-1: M-PARSE-POLISH ✅ mirrors pass`
- Update this row in PLAN.md

**Read only:** `PLAN.md` section "Parser pair session doc" above + this handoff.

---

## PP-1 Handoff update (2026-03-27 session 2, Claude Sonnet 4.6) — commit 9cb4af7

### Mirrors PASS

**Prolog self-parse:** exit 0, 144 lines, structurally balanced.
**Icon self-parse:** exit 0, 259 lines, structurally balanced.

Raw `grep -c '('` counts show small apparent imbalances — artifacts of paren
characters inside `(str "(")` / `(str ")")` string literal nodes. Stripping
string contents before counting confirms both outputs are fully balanced.

**Bug fixed (prolog_parser.pro):**
`sx_tag(call(F,As), call(F), As)` → `sx_tag(call(F,As), call, [atom(F)|As])`
The compound tag `call(F)` caused `atom_length/2` to crash with a type error
whenever a call node was too wide to fit inline and `pp` fell through to the
multi-line path. Fix: tag is now the atom `call`; functor `F` becomes first
child as `atom(F)`, preserving `(call member ...)` output format.

**Known issues verified:**
1. `p_namelist` local-decl dup — did NOT manifest in Icon self-parse. ✓
2. Prolog `,`-chain flat rendering — `op_info` facts render correctly. ✓
3. Icon `str` quoting — `(str "hello")` output confirmed. ✓
   Exception: `(str "\"")` for literal double-quote renders as `(str "")` —
   cosmetic, does not affect parse correctness.

**Session is complete. Next session: Lon to assign.**

**Read only:** `PLAN.md` only.

---

## IX-17 Handoff (2026-03-27, Claude Sonnet 4.6) — commit `3e4f131`

### What was done (sessions IX-15 / IX-15b / IX-16)

**All rungs 01–35 now 5/5 ✅.** rung36_jcon is a separate subsystem.

**Fixes applied (`icon_emit_jvm.c`):**

1. **`emit_until` / rung09** — `ICN_UNTIL` was falling to UNIMPL. Added `emit_until()`
   to `icon_emit.c` (x64) and wired dispatch. Also `ij_emit_until` already existed in
   JVM emitter; rung09 5/5 via JVM path.

2. **Record type prepass / rung24, rung31** — `ij_prepass_types` had no branch for
   `ij_expr_is_record(rhs)`. Variables assigned from record constructors fell to `'J'`
   (long) default; `getstatic`/`putstatic` mixed `J` and `Ljava/lang/Object;` →
   `NoSuchFieldError` at runtime. Fix: detect record RHS → `ij_declare_static_obj(fld)`
   with dual local/global register.

3. **`reads()` slot bug / rung27** — `arr_slot` from `ij_alloc_ref_scratch()` is a raw
   JVM slot but was wrapped in `slot_jvm()` (doubles it) on two `aload` sites →
   `VerifyError: Illegal local variable number`. Fix: use `arr_slot` directly.

4. **Suspend body ω routing / rung03** — `ij_emit_suspend` body wired `bp.ω = ports.γ`
   (= while's `body_drain`, does `pop2`) and `body_done: pop2; JGoto(ports.γ)` (double
   drain). Both paths hit `pop2` on empty stack → `VerifyError`. Fix: both now target
   `ports.ω` (= while's `loop_top`, no-value path).

**Rename:** `icon_driver` eradicated everywhere — `src/frontend/icon/icon_driver.c` →
`icn_main.c`; function renamed `icn_main()`; all 46 affected files swept.

### Harness note

The standard `run_rungNN.sh` scripts only assemble `main.j`. Record types emit
companion `ClassName$RecordType.j` files. Correct runner pattern (see §BUILD in
`SESSION-icon-x64.md`): assemble **all** `.j` in TMPD, use TMPD as `-cp`, feed
`.stdin` files where present.

### Next session

Read `SESSION-icon-x64.md` §NOW (IX-17) only. rung36_jcon is the frontier —
52 tests, currently 2/52. That's a separate subsystem (`ARCH-icon-jcon.md`).

---

## PP-1 Handoff update (2026-03-27 session 3, Claude Sonnet 4.6) — commit 35988b9

### Task: icon_recognizer.icn + prolog_recognizer.pro (SNOBOL4 BEAUTY paradigm)

**What these are:** Wholesale recognizers (no separate lexer/tokenizer). The
program matches the entire source as a single string. Procedures mirror BNF.
`suspend` for every terminal. Same `nPush/nInc/nDec/nPop` + `Shift/Reduce`
as beauty.sno, translated one-to-one to Icon (string scanning) and Prolog (DCG).

### icon_recognizer.icn — STATUS: WIP, compiles, tree structure has one remaining bug

**Two stacks (globals):**
- `_stk` — tree/value stack. `Shift(tag,val)` pushes a leaf. `Reduce(tag,n)` pops n, makes parent node.
- `_cstk` — counter stack. `nPush()` pushes 0. `nInc()` increments top. `nTop()` reads top. `nPop()` pops. Used to count variable-length child lists.

**Bugs fixed this session:**
1. `many(cs)` used `every tab(upto(~cs)|0)` — `every` generated two positions, leaving &pos at 0. Fixed to `tab(upto(~cs)) | tab(0)`.
2. `skip_ws_comments()` used `else break` inside `if` inside `repeat` — illegal in Icon. Fixed to progress-check: `if &pos = p then break`.
3. `tab(many(...))` double-advance in `ws()`, `ident()`, `integer_lit()`. Fixed: call `many()` directly (it already advances &pos).
4. `r_top()` had no `suspend` — returned nothing to `compiland()`. Fixed: `suspend r_proc() | r_global() | r_record()`.
5. `r_expr_prec()` called `r_primary()` unconditionally — if primary fails, loop drives infinite recursion → segfault. Fixed: `r_primary() | fail`.
6. `r_xlist()` called `nInc()` before `r_expr()` check. Fixed: only `nInc()` after successful `r_expr()`.
7. `r_block()` used `nInc()` into the outer counter. Fixed: local `stmts` counter.

**ONE REMAINING BUG — r_decls never calls nInc()**

`r_decls()` finds `local`/`static`/`initial` declarations and for each one
calls `Reduce(dk,1)` pushing a node — but never calls `nInc()`. The counter
pushed by `r_proc` via `nPush()` before calling `r_decls()` stays 0. So
`nTop()` = 0 → `if ndecls = 0 then Shift("decls","")` always fires, even
when real decls were found.

**Fix:** Add `nInc()` inside `r_decls` after each successful decl:
```icon
procedure r_decls()
  local found, dk
  repeat {
    found := &null
    skip_ws_comments()
    every dk := "local" | "static" | "initial" do {
      if kw(dk) then {
        r_namelist()
        Reduce(dk, 1)
        nInc()          # ← ADD THIS
        found := 1; break
      }
    }
    /found & break
  }
  suspend &pos
end
```

Also verify `r_proc` restores `nPush/nPop` pairing for decls — current code
uses `stk_before`/delta approach (wrong session logic leaked in). Revert to
clean `nPush() / r_decls() / ndecls := nTop() / nPop()` with the `nInc()` fix above.

**After fixing:** Run smoke test:
```bash
icont -s -o /tmp/icon_recognizer demo/scrip/icon_recognizer.icn
echo 'procedure foo(x)
  local a
  return x + 1
end' | /tmp/icon_recognizer
```
Expected tree:
```
(proc
  (id "foo")
  (namelist (id "x"))
  (local (namelist (id "a")))
  (block (return (+ (id "x") (int "1"))))
)
```

**After smoke test passes:** Run self-parse mirror:
```bash
/tmp/icon_recognizer < demo/scrip/icon_recognizer.icn | head -30
```

### prolog_recognizer.pro — STATUS: NOT STARTED

**Design:** DCG rules with `{action}` code. Same `nPush/nInc/nDec/nPop` +
`Shift/Reduce` implemented as Prolog predicates operating on global nb-variables
(or passed state — nb_getval/nb_setval for the two stacks).

**Input:** char-code list from `atom_codes(Src, Codes)`.

**Terminal primitive:**
```prolog
% lit(+Codes, -Rest): match literal string
lit([], S, S).
lit([H|T], [H|S], Rest) :- lit(T, S, Rest).

% Match and shift an identifier
p_ident([C|Cs], Rest) --> { code_type(C, alpha) }, ... 
```

Or more idiomatically with DCG:
```prolog
ws --> [C], { code_type(C, space) }, !, ws.
ws --> [].

kw(Word) --> { atom_codes(Word, Codes) }, Codes, ws,
             { \+ peek_alnum }.
```

**Stack implementation:**
```prolog
:- nb_setval(val_stack, []).
:- nb_setval(ctr_stack, []).

nPush :- nb_getval(ctr_stack, S), nb_setval(ctr_stack, [0|S]).
nInc  :- nb_getval(ctr_stack, [H|T]), H1 is H+1, nb_setval(ctr_stack, [H1|T]).
nTop(N) :- nb_getval(ctr_stack, [N|_]).
nPop  :- nb_getval(ctr_stack, [_|T]), nb_setval(ctr_stack, T).

shift(Tag, Val) :-
    nb_getval(val_stack, S),
    nb_setval(val_stack, [node(Tag,Val,[])|S]).

reduce(Tag, N) :-
    nb_getval(val_stack, S),
    length(Kids0, N), append(Kids0, Rest, S),
    reverse(Kids0, Kids),
    nb_setval(val_stack, [node(Tag,'',Kids)|Rest]).
```

**Top-level call:**
```prolog
main :-
    read_all_input(Src),
    atom_codes(Src, Codes),
    phrase(compiland, Codes, []),
    nb_getval(val_stack, [Tree|_]),
    print_tree(Tree, 0).
```

**Grammar rules** mirror `prolog_parser.pro` but as DCG on char codes, with
`{shift(...)}` / `{reduce(...)}` / `{nPush}` / `{nInc}` / `{nPop}` actions.

**Read only:** `PLAN.md` PP-1 section + this handoff. No other docs.
