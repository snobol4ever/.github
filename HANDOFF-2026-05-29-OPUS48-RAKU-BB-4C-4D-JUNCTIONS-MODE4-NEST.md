# HANDOFF 2026-05-29 — Opus 4.8 — RAKU-BB RK-BB-4c + RK-BB-4d (mode-4 junctions, precedence, nesting)

**Goal:** GOAL-RAKU-BB.md. **Repos:** SCRIP `1652aeb9`, corpus unchanged, .github (this).
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude

## Summary

Three pieces, all green, all committed. Started at RK-BB-4c (mode-4 junctions), closed it and
both reachable parts of RK-BB-4d. GATE-RK mode-2 26→28/35, GATE-RK4 mode-4 26→29/35. Zero
regression. FACT 0. No template byte changes (all runtime-helper + grammar work).

## RK-BB-4c — mode-4 junctions ✅ (SCRIP `216f22cd`)

Route (i) from the goal doc (the fast, FACT-clean path). The `SM_ACOMP`/`SM_LCOMP` x86 templates
already emit `mov edi,<op>; call rt_acomp` / `call rt_lcomp` — the comparison work lives in those
runtime helpers, NOT in emitted bytes. So the junction collapse goes INTO `rt_acomp`/`rt_lcomp`
(`src/runtime/rt/rt.c`), mirroring the mode-2 `SM_ACOMP`/`SM_LCOMP` interpreter cases verbatim:
when either popped operand is `rk_junction_is()` true, call
`rk_junction_collapse(scalar, jct, op, numeric)` (numeric=1 acomp / 0 lcomp); push scalar+`LAST_OK=1`
on hit, FAIL+`LAST_OK=0` on miss. Added two `extern` decls (`rk_junction_is`,
`rk_junction_collapse` — already exported from libscrip_rt.so). `rk_junctions` mode-4 → green.

Because `rt_acomp`/`rt_lcomp` are the SAME helpers mode-3 native calls, mode-3 junctions are ALSO
correct — but mode-3 native Raku currently emits no output for any program (pre-existing
MODE3-DISPATCH-GAP: `--run` Raku entry not flat-wired). Verified empty at baseline too; not ours.

## RK-BB-4d — precedence ✅ (SCRIP `0a5352e3`)

`$x == 1|2|5` was misparsing as `($x==1) | 2 | 5`. Real Raku binds junction infix `|`/`&` TIGHTER
than comparison. Fix in `src/frontend/raku/raku.y`: new `jct_expr` tier between comparison and
`range_expr`. Comparison productions now take `jct_expr` operands; the four junction-infix +
logical productions were restructured (`|`/`&` → `jct_expr`; `OP_AND`/`OP_OR` stay at cmp_expr).
Moved `%left '|' '&'` above the comparison precedence line. Declared `%type <node> jct_expr`.
Regenerated parser+lexer via `scripts/regenerate_parser_and_lexer_from_sources.sh`. NET-ZERO new
conflicts (baseline raku.y already had 30 s/r; still 30 — verified by regenerating both). Added
`test/raku/rk_junction_prec.{raku,expected}` (precedence + var round-trip + string-relop collapse +
same-flavor-inner nesting). Green both modes.

## RK-BB-4d part 1 — nested mixed-flavor ✅ (SCRIP `1652aeb9`)

The SOH-leak the goal doc predicted, pinned exactly: in `rk_junction_collapse`
(`src/runtime/interp/raku_builtins_byname.c`) the member scan `while (*p && *p != SOH)` stopped at
the FIRST SOH — but a nested junction member `\x03<flav>\x01m1\x01m2…` CONTAINS SOH separators, so
the scan truncated it to `\x03<flav>` (zero members) and the inner members leaked out as bogus
outer members. Manifested ONLY as a flavor wrapping a DIFFERENT-flavor multi-member inner
(`50 & (50|60)` wrongly missed; `10 | (50&60)` wrongly hit). Same-flavor nesting was unaffected
(parse-time flatten in `mk_junction`).

**Fix — self-delimiting EOT (`\x04`) terminator:**
- Builder (`raku_try_call_builtin_by_name`): append `\x04` after the last member of every junction
  (`GC_malloc(total+2)`; `buf[p++]='\x04'; buf[p]='\0'`). Nested members already carry their own
  trailing `\x04` since they're built as values first.
- Collapse scanner: scalar members now stop at SOH **or** `\x04`. A member starting with `\x03` is a
  nested junction → consume to its MATCHING `\x04` via depth counting (`\x03`++, `\x04`--), recurse
  on that opaque span. Depth-correct to arbitrary nesting.

Added `test/raku/rk_junction_nest.{raku,expected}` (all/any/none mixed-flavor nesting, both member
orders). Green both modes. Existing `rk_junctions` + `rk_junction_prec` re-verified unaffected.

## Gates (SCRIP `1652aeb9`)

```
GATE-RK   mode-2:        28/35   (was 26/33; +rk_junctions already, +rk_junction_prec, +rk_junction_nest)
GATE-RK4  mode-4:        29/35   (was 26/33; +rk_junctions, +rk_junction_prec, +rk_junction_nest)
GATE-RK3  mode-3 native: not re-run — junctions correct but dormant (MODE3-DISPATCH-GAP)
Smoke raku/icon/prolog/snobol4/snocone: 5/5/5/13/5  HOLD
Crosschecks (stash/rebuild verified baseline-identical):
  SNOBOL4 5/1 (beauty_omega pre-existing) · Icon 3/1 · Prolog 0/132 (NO-MODE-FALLBACK) · Raku 36/1
FACT RULE grep: 0
Build: clean (scrip + libscrip_rt)
```

Mode-4 FAILs remaining (6): rk_re32/33/34/35/37, rk_regex23 — the deferred regex cluster
(GOAL-RAKU-PAT-BB). Mode-2 FAILs (7): same 6 regex + rk_stdio39 (documented test-fidelity issue).

## NEXT

RK-BB-4 junctions are effectively COMPLETE for the current corpus (mode-2 + mode-4, incl. nesting).
Remaining junction slivers are peripheral and unblocked-by-nothing:
- **`^` (one) infix operator** is not lexed (`raku.l` has no single-char `^`); only the `one(...)`
  constructor works. Add to lexer + a `mk_junction("one",...)` production if a corpus case needs it.
- **Unparenthesized chains mixing flavors** across constructors are untested at the precedence edge.

Substantive next work is elsewhere:
- **RK-BB-4c mode-3** will light up for free once MODE3-DISPATCH-GAP closes (Raku `--run` flat-wire;
  tracked in MODE3-DISPATCH-GAP.md / M3-RK-NOINTERP). The collapse logic is already in
  `rt_acomp`/`rt_lcomp` which mode-3 native calls.
- **RK-BB-5** — `reverse`/`tail`/`from-loop` as Seq consumers; `zip`/`cross` multi-Seq drivers.
- Deferred **regex cluster** under GOAL-RAKU-PAT-BB.

## Q11 substrate note (for Lon)

RK-BB-4c used route (i) (helper-call collapse), per Lon's recommendation ("recommend (i) to flip
mode-4 green, then refactor to (ii) if Lon wants the BB_ALT substrate exercised"). Route (ii) —
lowering `any`/`|` through the proven `BB_ALT` binary slab — remains available and unexercised.
Both mode-4 and mode-2 now share the tagged-string + `rk_junction_collapse` rep (now EOT-terminated).
