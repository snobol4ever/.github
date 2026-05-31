# GOAL-SNOCONE-SWITCH-BACKENDS — chain vs label-table switch lowering

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

**Repo:** SCRIP
**Done when:** the Snocone front-end + IR lowering supports two
`switch` lowerings — `chain` (current) and `table` (perfect-hash
jump table on case literals) — selectable per-site, per-file, and
per-compile via the three-layer mechanism described in
`ARCH-SNOCONE.md ## Switch backends`. `--switch-style=auto` picks
`table` when there are ≥ 5 cases and every case is a same-type
literal (string or integer); otherwise `chain`. Gate: a benchmark
fixture with a 30-way string `switch` in a hot loop runs measurably
faster under `--switch-style=table` than `--switch-style=chain`,
with byte-identical output.

---

## Origin

Lon, session 2026-05-02 #6, while reviewing the SB-6 audit findings
that surfaced the `beauty.sc::pp()` / `ss_leaf()` broken-dispatch
bugs. Insight: the SNOBOL4 `:S($('pp_' t))` polymorphic-dispatch
idiom is a `switch` over a string discriminator. Snocone already
has `switch`. The Snocone-port form of `pp()` should be one big
`switch (t) { case 'snoBuiltinVar': ...; ... }` — but to be both
correct and fast for the 30+ case scale, the lowering needs a
table option, not just a chain option.

---

## Spec

See `ARCH-SNOCONE.md ## Switch backends` for the full design. Recap:

- **chain backend** — `IDENT(e, vK) :S(caseK)` cascade, current
  behavior. O(n) compares.
- **table backend** — gperf-style perfect-hash table built at
  compile time keyed on the literal case strings/integers. O(1)
  dispatch.
- **selection** — narrowest layer wins:
  1. Per-switch attribute: `switch [[table]] (e) { ... }` /
     `switch [[chain]] (e) { ... }`
  2. File-level pragma: `#pragma snocone switch=table`
  3. Driver flag: `--switch-style=chain|table|auto`
- **`auto` heuristic** — `table` if (a) ≥ N cases (start with N=5,
  tunable) and (b) every case is a same-type compile-time literal
  (string or integer). Otherwise `chain`.

---

## Open rungs

- [ ] **SW-1** — Frontend parse: accept the `[[chain]]` / `[[table]]`
      attribute on `switch` (snocone_parse.y/snocone_lex.l).
      Smoke test: round-trip print preserves the attribute.

- [ ] **SW-2** — Frontend parse: accept `#pragma snocone switch=...`
      file-level pragma. Smoke test: pragma propagates to every
      `switch` in the file unless overridden per-site.

- [ ] **SW-3** — Driver flag: `scrip --switch-style=chain|table|auto`.
      Default `auto`. Smoke test: flag propagates through to lowering.

- [ ] **SW-4** — Lowering: implement `table` lowering shape in
      `sm_lower.c`. Constant table emission. Hash function selection
      (string: FNV-1a or similar; integer: direct or shifted). Verify
      gperf-style perfect-hash construction is feasible at compile
      time with the case-literal set, or pick a non-perfect hash with
      one extra compare per dispatch.

- [ ] **SW-5** — `auto` heuristic: count cases, type-check literals,
      pick chain or table. Threshold N=5. Tunable single point.

- [ ] **SW-6** — Per-backend ports: JVM (tableswitch / lookupswitch),
      .NET (Switch IL), JS (object dispatch), WASM (br_table). Each
      target already has a native dense-jump primitive — use it.

- [ ] **SW-7** — Benchmark fixture: 30-way string switch over a tree
      of synthetic AST nodes, 10⁶ dispatches. Measure chain vs table.
      Acceptance gate: ≥ 3× speedup on the table backend in interp
      mode, measurable improvement on every native backend.

- [ ] **SW-8** — Apply to beauty.sc: rewrite `beauty.sc::pp()` and
      `beauty.sc::ss_leaf()` as `switch [[table]] (t) { ... }` over
      the canonical 30+ type tags. This unbreaks the audit findings
      from SB-6.E.7 *and* makes the dispatch fast. Coordinate with
      SB-6.E.7 — the audit fixes the broken if/else-if chains *now*;
      this rung *replaces* them with a switch later.

---

## Invariants

- Both backends produce byte-identical output for any `switch`
  whose cases are well-formed.
- The `auto` heuristic must never silently pick `table` when a case
  literal violates the type-uniformity rule — fall back to `chain`
  with no warning required at default verbosity.
- A `[[table]]` attribute on a switch with non-uniform case types is
  a compile-time **error**, not a silent fallback. The user asked
  explicitly; tell them no.

---

## Why this is its own goal, not part of SB-6

SB-6 is "beauty self-hosts byte-identical." The audit step
(SB-6.E.7) fixes the broken-dispatch bugs in beauty.sc. The fixes
land as if/else-if chains today because that's what the lowering
produces. This goal turns those chains into switch+table later,
without changing observable behavior — separate concern, separate
gate.

---

## Repos

- `SCRIP` — frontend, lowering, drivers, tests
- `corpus` — benchmark fixture (under `programs/snocone/bench/switch/`)
- `.github` — this file, ARCH-SNOCONE.md spec
