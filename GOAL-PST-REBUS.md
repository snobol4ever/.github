# GOAL-PST-REBUS.md — Pure Syntax Tree: Rebus

**Repo:** one4all + corpus + .github
**Parent:** `GOAL-PARSER-PURE-SYNTAX-TREE.md`
**Status:** ✅ COMPLETE — Phase 1 C + Phase 2 PST-RB-SC (2026-05-19).

---

## Phase 2 — `corpus/SCRIP/parser_rebus.sc`

**Rung:** `PST-RB-SC` — verify-and-stamp. Estimated 10 min.

Per `PST-SCRIP-AUDIT.md § parser_rebus.sc`: the file is **already
shift/reduce-pure**. Every `Push(`/`Pop(`/`Tree(` grep hit is a
substring match on `nPush(`/`nPop(` or the post-Compiland driver-tail
`Pop()` (permitted — root retrieval, not a grammar action).

### Permitted primitives (binding)

`shift(p, kind)` · `reduce(kind, n)` · `nPush()` · `nInc()` · `nPop()` ·
`nTop()` · `assign(.var, val)`. Pure string preprocessors with no tree
ops also permitted.

### Steps

- [x] **RB-SC-1** — Read `corpus/SCRIP/parser_rebus.sc` and confirm no
  helper functions, no forbidden primitives. Grep:
  ```
  grep -nE 'shift_value|foldop|reduce_call|reduce_prim|reduce_opsyn' parser_rebus.sc
  grep -nE '^function ' parser_rebus.sc
  grep -nE '\b(Push|Pop|Tree|tree|Append|IncCounter|TopCounter)\(' parser_rebus.sc
  ```
  Expected: zero non-substring hits (only `nPush(`/`nPop(` and the
  driver-tail `Pop()`).

- [x] **RB-SC-2** — Add stamp comment at top:
  ```
  /* PST-RB-SC ✅ 2026-05-19 — already shift/reduce-pure; verified zero violations. */
  ```

- [x] **RB-SC-3** — Run the smoke test:
  ```
  bash /home/claude/one4all/scripts/test_parser_rebus.sh
  ```
  If it passes, commit. If it fails, file `⚠ MIRROR-GAP-RB-SC-3` and
  commit anyway — debugging belongs to a separate later session per the
  audit's strict rule.

### Done

`parser_rebus.sc` carries the stamp; per-language goal closed; Phase 2
moves on.

---

## Closed rungs (Phase 1 C — history)

All six §⛔ violations closed 2026-05-19. RB-C-1 (stmt_list_ne) ✅,
RB-C-2 (unless) ✅, RB-C-3 (case TT_IF) ✅, RB-C-4 (augop) ✅,
RB-C-5 (postfix-call) ✅, DECL-1/2/3 (RDecl/RProgram/RCase) ✅.

---

## State

```
watermark:   Phase 2 PST-RB-SC ✅ COMPLETE 2026-05-19.
next:        PST-ICN-SC (next recommended rung).
audit:       PST-SCRIP-AUDIT.md § parser_rebus.sc — "ALREADY CLEAN".
heads:       one4all @ 2a9aa511 · corpus @ d1c08ff
```
