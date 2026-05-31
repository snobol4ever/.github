# GOAL-IR-DEFINE-KIND.md — promote DEFINE to its own IR kind

╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║  ⛔ ABSOLUTE RULE — ZERO C BYRD BOX FUNCTIONS — NO EXCEPTIONS — READ THIS BEFORE WRITING CODE  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                  ║
║  A C Byrd box (C BB) is ANY C function with this signature:                                     ║
║                                                                                                  ║
║      DESCR_t foo(void *zeta, int entry)                                                         ║
║                                                                                                  ║
║  implementing four-port logic (α / β / γ / ω).                                                  ║
║                                                                                                  ║
║  THERE MUST BE ZERO OF THESE IN THE CODEBASE. NOT ONE. NONE. EVER.                              ║
║                                                                                                  ║
║  ALL Byrd boxes are x86 ASSEMBLY emitted at runtime by the emitter.                             ║
║  If you want a BB, you EMIT it. You do not write a C function for it.                           ║
║                                                                                                  ║
║  The only permitted C functions with (void *zeta, int entry) signature are:                     ║
║    • icn_lazy_box  — infrastructure shim, not a generator                                       ║
║    • icn_bb_dcg    — infrastructure DCG driver, not a generator                                 ║
║                                                                                                  ║
║  If you just wrote DESCR_t foo(void *zeta, int entry) { ... } — DELETE IT.                     ║
║  Implement it as an IR_block_t DCG (ir_exec.c + lower_icn.c) driven by icn_bb_dcg.             ║
║  See IR_ICN_UPTO in ir_exec.c and lower_icn_upto() in lower_icn.c as the template.             ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

**Repos:** SCRIP + corpus
**Branch:** TBD (likely `main` for SCRIP — frontend + ir_print are
shipping code paths, not parser-experimental)
**Tracker:** Lon's call (session #63+)

**Done when:** `scrip --dump-parse` emits `(E_DEFINE (E_QLIT "F(X)"))`
(or the agreed shape) instead of `(E_FNC DEFINE (E_QLIT "F(X)"))` for
every `DEFINE(...)` call site, and:
- the SCRIP runtime DEFINE path still works (registers procs, runs
  beauty.sno self-host byte-identical to SPITBOL).
- every cross-language test corpus that exercises DEFINE has been
  re-baselined against the new oracle output.
- PARSER-SN emits the matching shape (cheap follow-up, ~4 lines in
  `parser_snobol4.sc` Expr17).

---

## Motivation

Today the existing SNOBOL4 frontend emits `DEFINE('F(X)')` as
`(E_FNC DEFINE (E_QLIT "F(X)"))` — i.e. DEFINE is just a generic
runtime call that happens to be specially recognized by
`prescan_defines()` at runtime. Structurally it is *not* a runtime
call — it's a compile-time directive that registers a procedure.

`pat_prim_kind(sval)` in `snobol4.y:199` already gives the five pattern
primitives (LEN, BREAK, SPAN, ANY, NOTANY) their own IR kinds, with
`sval` dropped when the kind tag is itself the identity. DEFINE fits
the same pattern.

By symmetry, this raises the question of CSNOBOL4 / SPITBOL keyword
calls (`OPSYN`, `APPLY`, `DATA`, `LOAD`) — those *are* runtime calls
in CSNOBOL4 semantics, but only `OPSYN` and `DATA` are arguably
compile-time directives in the same family as DEFINE. Lon decides the
final list.

---

## Spec — IR shape

**Tag:** `E_DEFINE`
**Children:** 1 — the spec string as `E_QLIT`
**`sval`:** empty string (the kind tag is the identity)

The spec string stays opaque to `--dump-parse`. Parsing the spec into
its component parts (function name, formal args, locals, entry label)
is `prescan_defines()`'s job at runtime; nothing structural there is
visible at parse time. This matches what the parser *does* today; only
the wrapping kind tag changes.

```
DEFINE('F(X)L1')
  before: (E_FNC DEFINE (E_QLIT "F(X)L1"))
  after:  (E_DEFINE (E_QLIT "F(X)L1"))
```

---

## Implementation steps

- [ ] **Step 1 — frontend.** Add `E_DEFINE` to the IR kind enum (in
      `scrip_cc.h` — search for `E_FNC` to find the canonical declaration
      site). Update `pat_prim_kind()` in `snobol4.y` (and the regenerated
      `snobol4.tab.c`) to map `"DEFINE"` → `E_DEFINE`. The existing
      `_k==E_VAR?E_FNC:_k` ternary already handles dropping `sval` for
      non-E_VAR kinds, so no further frontend change is needed.
- [ ] **Step 2 — `--dump-parse`.** Add the new kind to `ir_print.c`
      (or wherever `print_node` lives — search for the `E_LEN` /
      `E_BREAK` cases). Render as `(E_DEFINE <spec child>)` — same shape
      as the other unary IR kinds.
- [ ] **Step 3 — sm_lower / runtime.** Walk every `case E_FNC:` /
      `kind == E_FNC` site (11 in `sm_lower.c` alone). Each is one of:
      (a) "treat E_DEFINE the same as E_FNC" — fall through, OR
      (b) "this is the runtime call dispatch" — keep E_FNC-only.
      `prescan_defines()` is the canonical handler for E_DEFINE; it
      already filters by `sval == "DEFINE"` and doesn't care about
      the kind tag, so it should keep working unchanged. Verify.
- [ ] **Step 4 — corpus oracle re-baseline.** Every program in
      `corpus/programs/snobol4/` that uses DEFINE needs its `.ref`
      re-captured. Scriptable: `for f in $(grep -l DEFINE …); do
      scrip --dump-parse $f > $f.ref; done`. Audit the diff before
      committing — should be a pure tag swap, no structural changes.
- [ ] **Step 5 — beauty.sno self-host.** Re-run Milestone 1 gate
      (`beauty.sno → SPITBOL byte-identical`). Output must stay
      `md5 abfd19a7a834484a96e824851caee159, 646 lines` at SCRIP
      `c801421a` parity. If diff: investigate — likely a missed
      E_FNC-vs-E_DEFINE case in lowering.
- [ ] **Step 6 — PARSER-SN-6 update.** Add a `_define_call(ep0, arg)`
      helper in `parser_snobol4.sc::Expr17`, ahead of the generic-call
      path:

      ```snocone
      // DEFINE — special: produces E_DEFINE not E_FNC.  Spec stays opaque.
      if (_src ? (POS(_ep) 'DEFINE(' @_ep)) {
          _src ? (POS(_ep) (SPAN(' ' tab) | epsilon) @_ep);
          arg = Expr(_src);
          if (~DIFFER(arg)) { _ep = ep0; freturn; }
          if (~(_src ? (POS(_ep) (SPAN(' ' tab) | epsilon) ')' @_ep))) {
              _ep = ep0; freturn;
          }
          Expr17 = Tree('E_DEFINE', '', 1, arg);
          return;
      }
      ```

      Re-run PARSER-SN gate; PASS=58 must hold (one of the 4
      `fn_define_*.sno` fixtures is the new oracle's witness). Update
      the GOAL-PARSER-SNOBOL4.md tree-shapes table and the SN-6 row.

---

## Open design question — siblings

Should OPSYN / APPLY / DATA / LOAD also get their own IR kinds in the
same change? Arguments:

- **For (symmetry):** all four are CSNOBOL4 directive-shaped — they
  have privileged runtime handling (OPSYN registers operator aliases,
  DATA registers types, LOAD pulls in `.so` files, APPLY dispatches
  through the alias table). Treating them as plain E_FNC obscures
  intent.
- **Against (scope creep):** OPSYN and DATA already have INFRA-11b /
  §14.2 open issues against them; adding new IR kinds without first
  fixing those issues paints over real bugs. APPLY and LOAD are
  unambiguously runtime calls — promoting them is more cosmetic than
  structural.

**Recommendation:** land DEFINE alone first. Re-evaluate the others
once the DEFINE migration ships clean.

---

## Risks

- **Cross-language emitter drift.** If the JVM / .NET / WASM back-ends
  switch on `EXPR_e` and don't have an E_DEFINE case, codegen breaks
  silently or noisily. `grep -rn "case E_FNC" src/backend/` should
  surface every emit-site.
- **Snocone PARSER-SC etc.** The five sibling parsers don't currently
  emit DEFINE-shaped trees, but if any sibling LANG ladder grows a
  parallel "compile-time directive" notion, they'll want their own
  E_DEFINE-equivalent — design with that in mind.
- **`tdump.sc`.** The PARSER-IC-0 internal-sval branch currently
  renders `(E_FNC DEFINE child)` as `(E_FNC DEFINE child)`. After
  migration, the parser emits `(E_DEFINE child)` directly via the
  generic-leaf `(KIND val)` form (since v=''). Both already work with
  current tdump; no change required there.

---

## Watermark

Goal stub written 2026-05-03 in response to a session-#63 question
("upgrade DEFINE to its own E_*"). Decision deferred to next planning
session — risk profile (frontend + runtime + corpus re-baseline +
Milestone 1 verification) is too wide for an opportunistic mid-rung
landing.
