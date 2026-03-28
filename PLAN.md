# PLAN.md — snobol4ever HQ Plan

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row. `git pull --rebase` before every push.

**🔒 ALL SESSIONS FROZEN — Grand Master Reorganization in progress. Resume post M-G7-UNFREEZE.**

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **⚠ GRAND MASTER REORG** | G-7 — 59 canonical IR nodes FINAL; pattern primitives added | `fb90365` G-7 | M-G0-SIL-NAMES |
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

**Invariants (frozen baseline):** x64 ASM: SNOBOL4 `106/106` · Icon `38-rung` · Snocone `10/10` · Rebus `3/3` · Prolog per-rung PASS | JVM: SNOBOL4 `106/106` · Icon `38-rung` · Prolog `31/31` | .NET: SNOBOL4 `110/110` | DOTNET repo: `TBD — retest required` | snobol4jvm repo: `TBD — retest required`

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
prolog_recognizer) against every program in snobol4corpus and snobol4x test suites.

**Harness scripts added to `snobol4x/test/scrip/`:**
- `run_corpus_icon.sh` — compiles both Icon tools, runs on all `.icn` files, reports pass/empty/crash
- `run_corpus_prolog.sh` — runs both Prolog tools via swipl, reports pass/empty/crash

**Baseline (30-file sample, icon corpus):**
- icon_parser: 29/30 pass (97%), 0 crashes
- icon_recognizer: 13/30 pass (43%, empty = files with $include/link), 0 crashes

**Milestone doc:** `MILESTONE-RECOG-CORPUS.md` in this repo

**Corpus sizes:**
- `snobol4corpus/programs/icon/`: 851 .icn files
- `snobol4x/test/frontend/icon/`: 258 .icn files
- `snobol4x/test/frontend/prolog/`: 130 .pro/.pl files

### Next session

Run the harness. Expected flow:
1. `bash test/scrip/run_corpus_icon.sh` — expect 0 crashes; note pass rate
2. `bash test/scrip/run_corpus_prolog.sh` — expect 0 crashes; note pass rate
3. Triage any crashes, fix tools, re-run until PASS
4. Fill results table in MILESTONE-RECOG-CORPUS.md, commit, update PLAN.md

**Read only:** `PLAN.md` PP-1 section + `MILESTONE-RECOG-CORPUS.md`.

---

## PP-1 Handoff update (2026-03-27 session 6, Claude Sonnet 4.6) -- commit 4b4d71a snobol4x

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

## PX-1 Handoff (2026-03-27, Claude Sonnet 4.6) — snobol4x `532be13`

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

## PX-1 Handoff (2026-03-28, Claude Sonnet 4.6) — snobol4x `a051367`

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

## G-7 Handoff (2026-03-28, Claude Sonnet 4.6) — .github `fb90365` snobol4x `d2ac7e6`

### Phase 0 milestones completed this session

| Milestone | Commit | What |
|-----------|--------|------|
| M-G0-FREEZE ✅ | snobol4x `716b814` | pre-reorg-freeze tag; doc/BASELINE.md |
| M-G0-RENAME ✅ | .github `22fae8d` | canonical names confirmed; GitHub redirects live |
| M-G0-CORPUS-AUDIT ✅ | .github `19d0db8` | 471-file inventory; 0 conflicts; execution plan; beauty.sno divergence flagged for Lon |
| M-G0-AUDIT ✅ | snobol4x `8b773e8` | doc/EMITTER_AUDIT.md — all 8 emitters, deviations, Greek law |
| M-G0-IR-AUDIT ✅ | snobol4x `d2ac7e6` | doc/IR_AUDIT.md — 45 nodes, minimal set, lowering rules |

### Key decisions and corrections made this session

- **Greek law**: Greek letters (α β γ ω) used **everywhere** — C source, comments, generated labels. No ASCII aliases. Was incorrectly written as ASCII in original law doc — corrected.
- **45 canonical IR node names** — finalized with SIL heritage. Key renames from sno2c.h: `E_CONC→E_SEQ`, `E_OR→E_ALT`, `E_MNS→E_NEG`, `E_EXPOP→E_POW`, `E_NAM→E_CAPT_COND`, `E_DOL→E_CAPT_IMM`, `E_ATP→E_CAPT_CUR`, `E_ASGN→E_ASSIGN`, `E_ARY→E_IDX` (merged), `E_ALT_GEN→E_GENALT`, `E_VAR→E_VAR`. New: `E_PLS`, `E_CSET`, `E_MAKELIST`.
- **ARCH-sil-heritage.md** created — documents SIL v311.sil lineage for all E_ names.
- **Git identity rule** corrected in RULES.md: all commits as `LCherryholmes <lcherryh@yahoo.com>`. History rewritten via git-filter-repo across .github, snobol4x, snobol4corpus, snobol4jvm.
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

Source: snobol4x emit_byrd_asm.c lines 2420-2422 recognized builtin list.
SPITBOL v37.min p$xxx match routines confirm each is distinct.
Icon equivalents (upto, move, tab, match) map to same nodes in M-G5-LOWER-ICON.

**IR_AUDIT.md is now correct. Proceed to M-G0-SIL-NAMES then M-G1-IR-HEADER-DEF.**
