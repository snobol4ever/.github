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
| **🌳 Parser pair** | PP-1: M-PARSE-PROLOG ✅ M-PARSE-ICON ✅ pretty-printers WIP (fit-or-wrap, 2-space indent, width=120 default); pending: mirror self-parse smoke test | `3fe17af` PP-1 | M-PARSE-POLISH |
| **TINY backend** | B-292 — 106/106 | `acbc71e` B-292 | M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR |
| **TINY NET** | N-253 — M-LINK-NET-7 ✅ | `e7dc859` N-253 | M-LINK-NET-8 |
| **TINY JVM** | J-216 — STLIMIT/STCOUNT ✅ | `a74ccd8` J-216 | M-JVM-STLIMIT-STCOUNT |
| **TINY frontend** | F-223 | `b4507dc` F-223 | M-PROLOG-CORPUS |
| **DOTNET** | D-164 — 1903/1903 | `e1e4d9e` D-164 | TBD |
| **README** | R-2 | `00846d3` R-2 | M-README-DEEP-SCAN |
| **ICON x64** | IX-14 — M-IX-CSET ✅ M-IX-STRBUILTINS ✅; rung09 0/5 until unimpl | `ee76037` IX-14 | M-IX-LOOPS (emit_until; rung09 5/5) |
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

### PENDING — trigger phrase: "Run the mirrors"
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
