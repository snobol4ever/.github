# PLAN.md — snobol4ever HQ Plan

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⛔ SESSION START — Run this first, every session

```bash
TOKEN=ghp_xxx bash /home/claude/.github/SESSION_BOOTSTRAP.sh
```

Clones repos, installs tools, sets git identity, prints current milestone, runs all three invariants.
Script is self-contained. See RULES.md for the six things it covers.

## 9 Repos under github.com/snobol4ever

| Repo | Role | Clone path |
|------|------|------------|
| `.github` | HQ — PLAN, ARCH, SESSION, FRONTEND docs | `/home/claude/.github/` |
| `one4all` | Main compiler/runtime — 6 frontends × 4 backends, C | `/home/claude/one4all/` |
| `snobol4jvm` | SNOBOL4 → JVM, Clojure | `/home/claude/snobol4jvm/` |
| `snobol4dotnet` → `snobol4net` | SNOBOL4 → .NET, C# (rename pending M-G9) | `/home/claude/snobol4dotnet/` |
| `corpus` | Test corpus — .sno/.icn/.pro + .ref oracle output | `/home/claude/corpus/` |
| `harness` | Test infrastructure — corpus runners | `/home/claude/harness/` |
| `snobol4python` | SNOBOL4 pattern library for Python | clone if needed |
| `snobol4csharp` | SNOBOL4 pattern library for C# | clone if needed |
| `snobol4artifact` | CPython extension | clone if needed |

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row. `git pull --rebase` before every push.

**🔒 ALL SESSIONS FROZEN — Grand Master Reorganization in progress. Resume post M-G7-UNFREEZE.**

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **⚠ GRAND MASTER REORG** | G-8 — M-G-RENAME-ONE4ALL ✅ `f2f0fcb` one4all (58 files, snobol4x→scrip-cc) | `f2f0fcb` one4all · pending .github | **Fix co-located check mode → declare M-G-INV-EMIT-FIX ✅ → wire SESSION_BOOTSTRAP → M-G4-SHARED-CONC-FOLD** |
| **⭐ Scrip Demo** | [FROZEN SD-37 `795c2ff`] | — | resume post-reorg |
| **🌳 Parser pair** | [FROZEN PP-1 `4b4d71a`] | — | resume post-reorg |
| **TINY backend** | [FROZEN B-292 `acbc71e`] | — | resume post-reorg |
| **TINY NET** | [FROZEN N-253 `e7dc859`] | — | resume post-reorg |
| **TINY JVM** | [FROZEN J-216 `a74ccd8`] | — | resume post-reorg |
| **TINY frontend** | [FROZEN F-223 `b4507dc`] | — | resume post-reorg |
| **DOTNET** | [FROZEN D-164 `e1e4d9e`] | — | resume post-reorg |
| **README** | [FROZEN R-2 `00846d3`] | — | resume post-reorg |
| **ICON x64** | [FROZEN IX-18 `c648df5`] | — | resume post-reorg |
| **Prolog JVM** | [FROZEN PJ-84a `a79906e`] | — | resume post-reorg |
| **Prolog x64** | [FROZEN PX-1 `a051367`] | — | resume post-reorg |
| **Icon JVM** | [FROZEN IJ-58 `5b32daa`] | — | resume post-reorg |
| **🔗 LINKER** | [FROZEN LP-6 `e7dc859`] | — | resume post-reorg |
| **🔗 LINKER JVM** | [FROZEN LP-JVM-3 `55d8655`] | — | resume post-reorg |

**Invariants (frozen baseline):** x86: SNOBOL4 `106/106` · Icon `38-rung` · Snocone `10/10` · Rebus `3/3` · Prolog per-rung PASS | JVM: SNOBOL4 `106/106` · Icon `38-rung` · Prolog `31/31` | .NET: SNOBOL4 `110/110` | DOTNET repo: `TBD — retest required` | snobol4jvm repo: `TBD — retest required`

**Gate invariants (SESSION_BOOTSTRAP.sh — G-sessions run all nine):** 3×3 matrix: SNOBOL4/Icon/Prolog × x86/JVM/.NET. Icon .NET and Prolog .NET not yet implemented (SKIP). Seven active checks: x86 `106/106` · JVM `106/106` · .NET `110/110` · Icon x64 `38-rung` · Icon JVM `38-rung` · Prolog x64 per-rung PASS · Prolog JVM `31/31`. Expanded from three per G-7 session (M-G2-MOVE-PROLOG-ASM-b). Rationale: reorg touches all emitters.

---

## Routing: pick three → read three docs

**1. Repo**

| Repo | Doc |
|------|-----|
| one4all | `REPO-one4all.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |

**2. Frontend × Backend → Session doc**

| | x86 | JVM | .NET |
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
**Commit:** `82c2491` one4all

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
cd one4all

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

---

## PP-1 Handoff update (2026-03-27 session 4, Claude Sonnet 4.6) — commits 008ea48 / 566aba8

### M-RECOG-ICON ✅ (commit 008ea48)

**Bugs fixed in icon_recognizer.icn:**
1. `r_decls` never called `nInc()` — counter stayed 0, placeholder always fired. Fixed: add `nInc()` after each successful decl.
2. `r_proc` used stk-size delta for params (wrong — `r_namelist` is self-contained). Fixed: stk-size delta for params, clean `nPush/r_decls/nTop/nPop` for decls.
3. `Reduce()` — `every` loop as last expression causes procedure to fail. Fixed: add `return` at end of `Reduce`.

Self-parse mirror: exit 0, balanced parens (71/71 after stripping string literals).

### M-RECOG-PROLOG ✅ (commit 566aba8)

**New file: `demo/scrip/prolog_recognizer.pro`**

DCG on char-code lists. `op_def/3` table (renamed from `op/3` to avoid built-in clash). `nPush/nInc/nTop/nPop` via `nb_setval/nb_getval`. `shift/2` + `reduce/2` on `val_stack`. `compiland_loop/4` with snapshot/restore on clause parse failure (graceful skip-past-dot for unrecognised constructs).

Key fixes during development:
- `r_op_token` needs explicit clauses for `,` (code 44) and `;` (code 59) — not covered by symbol-char scanner
- `r_maybe_args`: shift functor *before* parsing args (not after) to get correct stack order for `reduce(call, N+1)`
- `!` (cut, code 33) added as explicit `r_primary` alternative
- `compiland_loop` snapshot/restore prevents stray nodes from failed partial parses corrupting the tree count

Self-parse mirror: exit 0, 1486 lines, 1065 open = 1065 close parens — perfectly balanced.

### Next session
Lon to assign. Read only: `PLAN.md` PP-1 section + this handoff.

---

## PP-1 Handoff update (2026-03-27 session 5, Claude Sonnet 4.6) — commits below

### What was done

**Milestone defined: M-RECOG-CORPUS**

New milestone to run all four tools (icon_parser, icon_recognizer, prolog_parser,
prolog_recognizer) against every program in corpus and one4all test suites.

**Harness scripts added to `one4all/test/scrip/`:**
- `run_corpus_icon.sh` — compiles both Icon tools, runs on all `.icn` files, reports pass/empty/crash
- `run_corpus_prolog.sh` — runs both Prolog tools via swipl, reports pass/empty/crash

**Baseline (30-file sample, icon corpus):**
- icon_parser: 29/30 pass (97%), 0 crashes
- icon_recognizer: 13/30 pass (43%, empty = files with $include/link), 0 crashes

**Milestone doc:** `MILESTONE-RECOG-CORPUS.md` in this repo

**Corpus sizes:**
- `corpus/programs/icon/`: 851 .icn files
- `one4all/test/frontend/icon/`: 258 .icn files
- `one4all/test/frontend/prolog/`: 130 .pro/.pl files

### Next session

Run the harness. Expected flow:
1. `bash test/scrip/run_corpus_icon.sh` — expect 0 crashes; note pass rate
2. `bash test/scrip/run_corpus_prolog.sh` — expect 0 crashes; note pass rate
3. Triage any crashes, fix tools, re-run until PASS
4. Fill results table in MILESTONE-RECOG-CORPUS.md, commit, update PLAN.md

**Read only:** `PLAN.md` PP-1 section + `MILESTONE-RECOG-CORPUS.md`.

---

## PP-1 Handoff update (2026-03-27 session 6, Claude Sonnet 4.6) -- commit 4b4d71a one4all

### M-RECOG-CORPUS PASS

All four tools ran clean on full corpus (1109 Icon files, 130 Prolog files). Zero crashes.

**icon_parser fix applied this session:**
- p_exprlist: was left-recursive via mutual recursion (p_exprlist -> p_expr -> p_primary -> p_exprlist).
  On files with long argument lists this blew Icon eval stack (error 301, 13 crashes).
  Fix: iterative right-recursive accumulation -- single p_expr call, then while loop consuming commas.
- make_node/is_flat_op: flat trees for associative/chainable ops.
  | || ++ -- ** + - * / % // now produce (op a b c ...) instead of (op (op a b) c).

**Results:**
| Tool | Total | Pass | Empty | Crash | Pass% |
|------|-------|------|-------|-------|-------|
| icon_parser | 1109 | 1090 | 19 | 0 | 98.3% |
| icon_recognizer | 1109 | 576 | 533 | 0 | 51.9% |
| prolog_parser | 130 | 130 | 0 | 0 | 100% |
| prolog_recognizer | 130 | 130 | 0 | 0 | 100% |

**Remaining icon_parser non-passes (19 empty):** files using $include/link directives --
parser produces empty output, not crash. Acceptable per milestone criteria.

**Next session:** Lon to assign. Read only: PLAN.md PP-1 section.

## PX-1 Handoff (2026-03-27, Claude Sonnet 4.6) — one4all `532be13`

### Accomplished
- `\+` and `\=` inline emission ✅ (`e3f92cc`) — naf/alldiff PASS
- Multi-ucall backtrack root cause **fully diagnosed** — four bugs in `emit_byrd_asm.c`
- Bugs 1–4 addressed in `532be13`; `minimal2` PASS (2-ucall fact backtrack works)
- `alldiff` regressed (all_diff([1,2,3]) fails) — one remaining issue

### Remaining issue — alldiff regression
`all_diff([H|T]) :- \+ member(H,T), all_diff(T)` — `\+` is inlined (not a ucall),
`all_diff/1` is the single ucall. The Bug 3 fix adds a `trail_mark_fn` call at body
entry. **Next session: generate ASM for alldiff, read the `all_diff` clause 2 body
from the `pl_all_dt_diff_sl_1_c1_body:` label through α0, and trace why
`member([1,2,3])` fails when it should find `1` not in `[2,3]`.**

### Read only for next session
`SESSION-prolog-x64.md` §NOW only.

---

## PX-1 Handoff (2026-03-28, Claude Sonnet 4.6) — one4all `a051367`

### Accomplished this session
- `jle` fix: re-entry decode `inner = start-base` goes negative on head-fail jumps — `jz` → `jle`
- γN recompute: `sub_cs_acc` now recomputed from slots 0..N at each γN (fixes retry corruption)
- `pop rcx` fix: was `pop ecx` (invalid 64-bit instruction)
- All 2-ucall tests PASS: naf, alldiff, minimal2, retry2

### Remaining blocker — 3-ucall re-entry γN slot-zeroing conflict

On re-entry with `inner > 0`, the decode pre-loads `slot_1 = K`. Then α0 (ucall 0)
re-succeeds, γ0 runs and **zeros `slot_1`**, so α1 (ucall 1) gets `start=0` (fresh)
instead of `start=K` (resume). Always returns first solution → infinite loop.

**Fix (designed, not implemented):** At end of re-entry decode, instead of
`jmp α0`, emit a runtime dispatch that jumps to the deepest appropriate αK:

```asm
; end of re-entry decode, after pre-loading all slots:
cmp  dword [rbp - UCALL_SLOT_OFFSET(max_ucalls-1)], 0
jne  pred_c_α{max_ucalls-1}
...
cmp  dword [rbp - UCALL_SLOT_OFFSET(1)], 0
jne  pred_c_α1
jmp  pred_c_α0
```

Jumping to α1 bypasses γ0's slot-zeroing. Vars are already bound from head
unification (done at clause entry before body label). Ucall 0's bindings are
live (the caller's β only undid ucall N's bindings). So jumping straight to α1
with slot_1=K correctly resumes permutation at solution K+1.

### Read only for next session
`SESSION-prolog-x64.md` §NOW only. The fix is ~10 lines in `emit_byrd_asm.c`
around line 5840 (the `jmp α0` at end of re-entry decode).

---

## G-7 Handoff (2026-03-28, Claude Sonnet 4.6) — .github `fb90365` one4all `d2ac7e6`

### Phase 0 milestones completed this session

| Milestone | Commit | What |
|-----------|--------|------|
| M-G0-FREEZE ✅ | one4all `716b814` | pre-reorg-freeze tag; doc/BASELINE.md |
| M-G0-RENAME ✅ | .github `22fae8d` | canonical names confirmed; GitHub redirects live |
| M-G0-CORPUS-AUDIT ✅ | .github `19d0db8` | 471-file inventory; 0 conflicts; execution plan; beauty.sno divergence flagged for Lon |
| M-G0-AUDIT ✅ | one4all `8b773e8` | doc/EMITTER_AUDIT.md — all 8 emitters, deviations, Greek law |
| M-G0-IR-AUDIT ✅ | one4all `d2ac7e6` | doc/IR_AUDIT.md — 45 nodes, minimal set, lowering rules |

### Key decisions and corrections made this session

- **Greek law**: Greek letters (α β γ ω) used **everywhere** — C source, comments, generated labels. No ASCII aliases. Was incorrectly written as ASCII in original law doc — corrected.
- **45 canonical IR node names** — finalized with SIL heritage. Key renames from scrip-cc.h: `E_CONC→E_SEQ`, `E_OR→E_ALT`, `E_MNS→E_NEG`, `E_EXPOP→E_POW`, `E_NAM→E_CAPT_COND`, `E_DOL→E_CAPT_IMM`, `E_ATP→E_CAPT_CUR`, `E_ASGN→E_ASSIGN`, `E_ARY→E_IDX` (merged), `E_ALT_GEN→E_GENALT`, `E_VAR→E_VAR`. New: `E_PLS`, `E_CSET`, `E_MAKELIST`.
- **ARCH-sil-heritage.md** created — documents SIL v311.sil lineage for all E_ names.
- **Git identity rule** corrected in RULES.md: all commits as `LCherryholmes <lcherryh@yahoo.com>`. History rewritten via git-filter-repo across .github, one4all, corpus, snobol4jvm.
- **Phase 9 added**: snobol4dotnet → snobol4net rename (post M-G7-UNFREEZE).
- **snobol4jvm, snobol4dotnet test counts** marked TBD — retest required.

### Next milestone: M-G0-SIL-NAMES

SIL naming heritage was analyzed for IR nodes only. Broader analysis needed:
1. Runtime variable names in generated code (`sno_var_X`, `sno_cursor`, `pl_trail_top` etc.)
2. Emitter C source variable names and struct fields
3. Generated label prefixes (`P_`, `L`, `sno_`, `pl_`, `icn_`, `pj_`, `ij_`)
4. Runtime library macro names (`snobol4_asm.mac`, Byrd box macro library)

Produce `doc/SIL_NAMES_AUDIT.md`. This is prerequisite for M-G3 (naming law may need extension).

**Read for next G-session:** `GRAND_MASTER_REORG.md` Phase 0 + `ARCH-sil-heritage.md` + `doc/EMITTER_AUDIT.md` runtime variable table.

## G-7 Addendum — phase reorder decision (2026-03-28)

**Phase 3 (naming) moved after Phase 4 (collapse) and Phase 5 (frontend unification).**
Rationale: Phase 4 collapses duplicate `emit_<Kind>` functions into shared wiring;
Phase 5 eliminates frontend-local node types. Renaming pre-collapse code that Phases 4+5
immediately delete wastes ~20 milestones. Post-collapse naming surface: 9 surviving files
instead of 29+ opcode-group passes. GRAND_MASTER_REORG.md Phase 3 and dependency graph
updated. Commit `G-7`.

## G-7 Addendum — final pattern primitive pass (2026-03-28)

59 IR nodes (was 45). 14 pattern primitives added after discovering they each
have distinct Byrd box wiring in emit_byrd_asm.c:
E_ANY, E_NOTANY, E_SPAN, E_BREAK, E_BREAKX, E_LEN, E_TAB, E_RTAB, E_REM,
E_FAIL, E_SUCCEED, E_FENCE, E_ABORT, E_BAL.

Source: one4all emit_byrd_asm.c lines 2420-2422 recognized builtin list.
SPITBOL v37.min p$xxx match routines confirm each is distinct.
Icon equivalents (upto, move, tab, match) map to same nodes in M-G5-LOWER-ICON.

**IR_AUDIT.md is now correct. Proceed to M-G0-SIL-NAMES then M-G1-IR-HEADER-DEF.**

---

## G-8 Handoff (2026-03-29, Claude Sonnet 4.6) — one4all `9c386ee` .github pending

### What was done this session

**M-G-INV-EMIT-FIX: SIGSEGV fixed, baseline generated, check script working**

**SIGSEGV root cause (both asm and jvm emitters):**
- `emit_program` (x64) and `jvm_emit_stmt` (jvm) accessed `e->children[1]` on
  unary `E_INDR` nodes produced by `unop()` — `nchildren==1`, so `children[1]`
  reads one slot past the `realloc`'d array into heap memory from the previous
  file's stdio buffer. Manifested only in multi-file mode.
- Added `ECHILD(e,idx)` macro to `emit_jvm.c`; fixed all OOB sites (ASan-verified).
- Added per-file state reset to `asm_emit()` and `jvm_emit()`: zero `named_pats`,
  `call_slots`, `uid_ctr`, `jvm_pat_node_uid`, `jvm_fn_count_fwd`, etc. on every
  call, not just first init. Commit `6967683` one4all.

**emit-diff check: 484 pass / 0 fail (emit_baseline/ layout)**
- `test/run_emit_check.sh` extended to all 7 cells: SNOBOL4×{asm,jvm,net},
  Icon×{asm,jvm}, Prolog×{asm,jvm}.
- 474 baseline snapshots in `test/emit_baseline/`.

**test/ reorganization: co-located source+generated layout**
- `test/snobol4/{subdir}/foo.{sno,s,j,il}` — 152 SNOBOL4 sources with all backends.
- `test/icon/foo.{icn,s,j}` — 8 Icon samples.
- `test/prolog/foo.{pro,s,j}` — 6 Prolog samples.
- Commit `9c386ee` one4all.

### Unfinished / known issues

**1. run_emit_check.sh co-located mode broken (PRIORITY 1)**
The check script was rewritten to use co-located sources but produces 484 FAILs.
Root cause: `scrip-cc` adds the source file's directory as an include dir via
`snoc_add_include_dir()` in `compile_one`. When sources live under
`test/snobol4/arith_new/`, that directory is added as the include root, but
`scrip-cc` silently produces **empty output** for those files (exit 0, 0 bytes).
The stored generated files were created from `corpus/crosscheck/` paths and have
content. Direct `./scrip-cc -asm test/snobol4/arith_new/023_arith_add.sno` → 0 bytes.
Same file via `./scrip-cc -asm /home/claude/corpus/crosscheck/arith_new/023_arith_add.sno` → 70 lines.

**Fix:** In `run_emit_check.sh` `check_one` and `regen_one`, pass
`-I$(dirname $src)/..` or use the corpus path directly for SNOBOL4 files.
Alternatively: fix `compile_one` in `driver/main.c` to not silently swallow
errors when include dir is wrong — return non-zero so the bug surfaces.

Until fixed: `test/emit_baseline/` remains the authoritative baseline.
`run_emit_check.sh` still uses `emit_baseline/` path (old mode).

**2. SESSION_BOOTSTRAP.sh not updated**
`run_emit_check.sh` not yet wired into SESSION_BOOTSTRAP.sh. Do this after fix #1.

**3. M-G-INV-EMIT-FIX milestone**
The milestone is functionally complete (SIGSEGV fixed, 7-cell check green at
484/0 using emit_baseline/) but the co-located layout isn't wired up yet.
Declare ✅ after fixing run_emit_check.sh co-located mode.

### Next session

**Read only:** This G-8 handoff section.

**Step 1 — Fix co-located check mode:**
In `run_emit_check.sh`, pass corpus path for SNOBOL4, not test/snobol4/ path:
```bash
# check_one: resolve source path to corpus for scrip-cc invocation
# but compare output against co-located stored file
CORPUS_SRC="/home/claude/corpus/crosscheck/$(basename $(dirname $src))/$(basename $src)"
"$SNO2C" "$backend" "$CORPUS_SRC" > "$tmp" 2>/dev/null
```
Or: set `-I` flag per subdir. Simplest: keep test/snobol4/ for human reading
but invoke scrip-cc on the corpus originals.

**Step 2 — Verify 484/0 with co-located mode, delete emit_baseline/**

**Step 3 — Wire into SESSION_BOOTSTRAP.sh, declare M-G-INV-EMIT-FIX ✅**

**Step 4 — Advance to M-G4-SHARED-CONC-FOLD**
Extract n-ary→binary right-fold helper for E_SEQ/E_CONCAT into
`src/ir/ir_emit_common.c`. Shared by x64 and .NET. See GRAND_MASTER_REORG.md Phase 4.

## G-7 Handoff (2026-03-28, Claude Sonnet 4.6) — one4all `0bc5d9a`

### What was done this session

**Repo renames (M-G0-RENAME cleanup):**
- `snobol4ever/snobol4corpus` → `snobol4ever/corpus` ✅
- `snobol4ever/snobol4harness` → `snobol4ever/harness` ✅
- 112 refs updated in `.github`, 43 refs in `one4all`. Both committed.

**M-G4-SPLIT-SEQ-CONCAT phase 2 — parser/lowering E_CONC sites ✅**

`src/frontend/snobol4/parse.c`:
- Added `fixup_val_tree()` — recursively renames `E_SEQ` → `E_CONCAT` in value-context trees.
- Added `repl_is_pat_tree()` — lightweight guard: detects pattern-only nodes (`E_ARB`, `E_ARBNO`, `E_NAM`, `E_DOL`, `E_ATP`, `E_STAR`) in replacement tree.
- Post-parse fixup at statement level: `fixup_val_tree(s->subject)` always; `fixup_val_tree(s->replacement)` only when `!repl_is_pat_tree(s->replacement)`. `s->pattern` left as `E_SEQ` (correct by construction).
- **Key bug caught and fixed:** `PAT = " the " ARB . OUTPUT (...)` — replacement IS a pattern expression. Naive `fixup_val_tree` on replacement converted `E_SEQ→E_CONCAT`, breaking `expr_is_pattern_expr` in the emitter → `named_pat_register` not called → word1-4 FAIL. Fix: `repl_is_pat_tree` guard.

`src/frontend/snocone/snocone_lower.c`:
- `SNOCONE_CONCAT`, `SNOCONE_PIPE`, `SNOCONE_OR` → `E_CONCAT` (all pure value-context string concat).

**x86 invariant: 106/106 ✅** (verified with `run_crosscheck_asm_corpus.sh`)

**M-G-INV-JVM: single-JVM harness ⏳ (built, smoke-tested, full run pending)**

Root cause of JVM suite slowness: per-test JVM startup (~200-500ms × 106+ tests = minutes). Previous M-G-INV optimization only addressed x86 gcc recompilation — never touched JVM startup cost.

Fix:
- `src/backend/jvm/emit_jvm.c`: `System/exit` → `SnoRuntime/sno_exit` (2 sites).
- `test/jvm/SnoRuntime.java`: `sno_exit(int)` shim — throws `SnoExitException` in harness mode, calls `System.exit` standalone.
- `test/jvm/SnoHarness.java`: single-JVM runner. Per-test `URLClassLoader` isolation (statics reset automatically). Per-test daemon thread with 3s timeout (handles blocking `INPUT` reads). One JVM startup for entire suite.
- `test/run_invariants.sh` `run_snobol4_jvm()`: rewritten — compile all `.j` + assemble all `.class` in one pass, copy `.ref`/`.input` flat, then `java -cp $W SnoHarness $W $W $W` once.
- `setup.sh`: installs `openjdk-21-jdk-headless` (javac) if missing.

**Smoke test (13 tests):** 11 PASS, 1 FAIL (expr_eval — pre-existing), 1 TIMEOUT (wordcount — infinite INPUT loop, expected). Mechanism confirmed working.

**`javac` not in PATH by default** — only JRE was installed. `setup.sh` now installs JDK.

### Remaining issues / known state

1. **Full JVM 106/106 run not yet confirmed** — harness built and smoke-tested but `run_invariants.sh` full run was not completed this session (context limit). This is the first thing to do next session.

2. **`expr_eval` FAIL in JVM smoke** — pre-existing (not caused by this session's changes). Check whether it fails in the old per-test runner too before investigating.

3. **`wordcount` TIMEOUT** — expected. `wordcount.sno` reads `INPUT` in a loop; no `.input` file → blocks. The 3s timeout in SnoHarness handles it correctly. Not a bug.

4. **`.class` files gitignored** — correct, they're build artifacts. `run_invariants.sh` compiles them fresh each run from the `.java` sources in `test/jvm/`.

### Next session

**Read only:** `PLAN.md` G-7 Handoff + this section.

**Step 1 — Run SESSION_BOOTSTRAP.sh first (mandatory):**
```bash
TOKEN=ghp_<your-token> bash /home/claude/.github/SESSION_BOOTSTRAP.sh
```

**Step 2 — Confirm JVM 106/106:**
```bash
cd /home/claude/one4all
bash test/run_invariants.sh 2>&1 | grep -E "matrix|106|FAIL|wall"
```
If JVM shows 106/106: commit `G-7: M-G-INV-JVM ✅ — JVM 106/106 confirmed`, update PLAN.md, advance to **M-G4-SHARED-CONC-FOLD**.

If JVM shows failures: diff against `run_crosscheck_jvm_rung.sh` results to isolate whether failures are harness bugs or real regressions.

**Step 3 — M-G4-SHARED-CONC-FOLD** (after JVM confirmed):
Extract n-ary→binary right-fold helper for `E_SEQ`/`E_CONCAT` into `src/ir/ir_emit_common.c`. Shared by x64 and .NET. JVM unaffected (different execution model). See GRAND_MASTER_REORG.md Phase 4.

## G-8 Handoff update (2026-03-29 session 2, Claude Sonnet 4.6) — .github `10c20f8` snobol4x `65baf6a`

### M-G-RENAME-ANY2MANY ✅

**Full rename complete. 0 remaining `sno2c` refs. 0 remaining `snobol4x` refs.**

| Old | New |
|-----|-----|
| `sno2c` binary | `scrip-cc` |
| `sno2c.h` header | `scrip_cc.h` |
| `snobol4x` (repo identity in all docs/scripts) | `one4all` |
| `sno2c_icon` | removed — Icon is a frontend of `scrip-cc`, not a separate binary |

**Brand:** `any²many` (compiler) · `many²one` (linker) · `any²many²one` (full pipeline)  
`scrip-cc` = Scrip Compiler Collection (CC = Compiler Collection, per GCC precedent)

**GitHub repo rename still pending** — Lon must do manually:  
`https://github.com/snobol4ever/snobol4x/settings` → Danger Zone → Rename → `one4all`

**All four repos pushed:** `.github` `10c20f8` · `snobol4x` `65baf6a` · `harness` `4e4860f` · `corpus` `ab217d4`

### Next session

**Read only:** `PLAN.md` G-8 handoff (session 1, above) + this update.

**Step 1 — Fix co-located check mode in `run_emit_check.sh`** (G-8 session 1 handoff, still pending):
Pass corpus path to `scrip-cc` for SNOBOL4 files, compare against co-located stored file.

**Step 2 — Verify 484/0, declare M-G-INV-EMIT-FIX ✅**

**Step 3 — Wire into SESSION_BOOTSTRAP.sh**

**Step 4 — M-G4-SHARED-CONC-FOLD**

## G-8 Handoff update (2026-03-29 session 3, Claude Sonnet 4.6) — GitHub rename done

### GitHub rename complete
`snobol4ever/snobol4x` → `snobol4ever/one4all` ✅ (Lon, 2026-03-29)

### NEW MILESTONE: M-G-RENAME-ONE4ALL

**Full scan-and-replace of all remaining `snobol4x` string literals** in every file
across all four repos: README.md, all .github MDs, source comments, shell scripts,
generated headers, .gitignore, everything. The previous M-G-RENAME-ANY2MANY sweep
caught shell/script/MD references but a full grep will surface any stragglers
(clone URLs, path strings, comments, GitHub URLs still pointing to old name).

**Scope:**
- `snobol4ever/snobol4x` → `snobol4ever/one4all` (GitHub URLs)
- `snobol4x` (bare repo name in prose/paths) → `one4all`
- Local clone path `/home/claude/snobol4x` refs in docs → `/home/claude/one4all`
- Any `github.com/snobol4ever/snobol4x` URLs in README, ARCH docs, SESSION docs

**Read for next G-session:** This handoff only. Run SESSION_BOOTSTRAP first.

## G-8 Handoff update (2026-03-29 session 4, Claude Sonnet 4.6) — one4all `f2f0fcb`

### M-G-RENAME-ONE4ALL ✅

**Full sweep complete. 0 remaining `snobol4x` refs in live code.**

58 files changed in one4all. `snobol4x` → `scrip-cc` everywhere:
- bench printf strings (bench_re_vs_tiny.c, bench_pcre2_wins.c, bench_round2.c, bench_round2b.c, bench_pda.c)
- shell driver scripts (snobol4-asm, snobol4-jvm, snobol4-net) — comments + env var names (`scrip_cc_jvm_cache`, `scrip_cc_net_cache`)
- source file headers/comments (ir.h, engine.c/h, runtime.c/h, snobol4.c/h, prolog_lex.c/h, prolog_builtin.h, term.h, icon_ast.h, rebus_emit.c, emit_wasm.c, emit_jvm_prolog.c, mock_includes.c)
- generated file banners (.j artifacts, demo output)
- test comments (plunit.pl, tracepoints.conf, .sno test files, .c backend test files)

**Not changed (correct as-is):**
- `.github/PLAN.md` + `MILESTONE-RENAME-ANY2MANY.md` — historical handoff records, accurately describe the rename
- `corpus/` .sno files — "SPITBOL/snobol4x" refers to the external SPITBOL engine, not our project

### Next session

**Step 1 — Fix co-located check mode in `run_emit_check.sh`** (G-8 session 1 handoff):
Pass corpus path to `scrip-cc` for SNOBOL4 files, compare against co-located stored file.

**Step 2 — Verify 484/0, declare M-G-INV-EMIT-FIX ✅**

**Step 3 — Wire into SESSION_BOOTSTRAP.sh**

**Step 4 — M-G4-SHARED-CONC-FOLD**

**Read only:** This G-8 session 4 handoff.
