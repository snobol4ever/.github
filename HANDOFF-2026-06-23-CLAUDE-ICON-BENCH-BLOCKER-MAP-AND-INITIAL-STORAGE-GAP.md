# HANDOFF — 2026-06-23 — Claude — Icon benchmark blocker map (corrected) + IR_INITIAL needs a persistent-writable-static facility (NOT a gate lift)

## One-line: Probed all 13 `corpus/benchmarks/icon/*.icn` at `fa33cd6`; built the exact per-benchmark blocker map (corrects the goal file); diagnosed `IR_INITIAL` as a foundational storage gap, not the "quick gate lift" the goal file's NEXT-LEVERS list implies. **NO code change — tree pristine, suite 145/283 unchanged, all gates green. Nothing to push.**

**Repos:** all clean at their current heads (SCRIP `fa33cd6`). This handoff is the only artifact.

---

## 1. GROUND-TRUTH BENCHMARK STATE (`corpus/benchmarks/icon/`, 13 programs, at `fa33cd6`)

Probed each with `--compile` (→ `.s`, then `as`) and `--run`. **The goal file's "9/13 compile to assembling `.s`, all blocked on `tab`" is INACCURATE.** Reality:

| Bucket | Programs | Note |
|--------|----------|------|
| **Compiles to REAL `.s`** | `version` only | 1258 B, assembles clean, SMX-free. Its `.s` is committed & current. |
| **Excised at the gate** (0-byte `.s`, exit 0) | concord deal geddump ipxref micsum options post queens rsg shuffle tgrlink | `graph_native_emittable` returns 0 → emits nothing. NOT "assembling `.s` with SMX stubs" — they emit **nothing**. |
| **Parse-FAIL** | micro | real grammar gap (`create`) |

- **Committed `micro.s` / `micsum.s` are STALE** (fresh `--compile` → 0 bytes / parse-fail). Corpus hygiene: they should be removed (the honest current state is "no `.s`", since they excise/parse-fail). `version.s` is the only honest committed artifact.
- 2 of the excised set (`ipxref`, `tgrlink`) hit `[NO-AST] eval_ast stub` on `--run` (a routing-into-deleted-AST-interp path) — a *different* bug class from the SMX gate; worth a separate look.

### Exact per-benchmark blockers (rejectable IR kinds present, via `--dump-ir`)

The gate `graph_native_emittable_mode` (`src/driver/scrip.c:288`) returns 0 on the FIRST unsupported node. Kinds each benchmark trips on:

| Benchmark | Blocking IR kinds |
|-----------|-------------------|
| shuffle  | `IR_SWAP`(non-var operands: `!x :=: ?x`), `IR_LIST_BANG`, `IR_EVERY` |
| post     | `IR_INITIAL`, `IR_EVERY`, `IR_TO` (+ lists `[]`/`put`/subscript/`*x`/builtin-reassign underneath) |
| deal     | `IR_INITIAL`, `IR_ALT`, `IR_EVERY`, `IR_LIST_BANG`, `IR_SECTION`, `IR_TO` |
| queens   | `IR_INITIAL`, `IR_ALT`, `IR_EVERY`, `IR_IDX_SET`(F1 in-progress), `IR_RASGN`(F2 in-progress) |
| micsum   | `IR_GEN_SCAN`, `IR_ALT`, `IR_EVERY`, `IR_LIST_BANG` |
| concord  | `IR_GEN_SCAN`, `IR_ALT`, `IR_EVERY`, `IR_SECTION` (+ tables `T[word]`, sort) |
| ipxref   | `IR_INITIAL`, `IR_ALT`, `IR_EVERY`, `IR_FIELD_GET`, `IR_LIST_BANG`, `IR_SECTION` (heaviest) |
| tgrlink  | `IR_INITIAL`, `IR_ALT`, `IR_EVERY`, `IR_FIELD_GET`, `IR_GEN_SCAN`, `IR_IDX_SET`, `IR_LIST_BANG`, `IR_SECTION`, `IR_SUSPEND`, `IR_TO` (heaviest) |
| geddump/options/rsg/micro | PARSE-blocked (grammar gaps: `return`-in-expr, `create`, if-else-as-RHS, paren comma-subscript) |

**KEY TAKEAWAY:** no single benchmark is one-fix-from-clean. They collectively *are* the remaining GOAL-ICON-FULL-PASS. The most-shared real levers, by benchmark count: **`every`/`to` value-flow** (≈8), **lists** (`[]`/`put`/`!x`/subscript/`*x`, ≈6), `IR_INITIAL` (5), `IR_SECTION` (4), `IR_ALT` value-position. Tables+sort gate `concord`; `IR_SUSPEND` gates `tgrlink`.

### 1a. PRECISE LAYERED TRIGGERS (gate-instrumented — supersedes the "kinds present" table for PRIORITIZATION)

The kinds-present table OVER-counts: `graph_native_emittable` only rejects specific *shapes*. I instrumented the gate to print the EXACT first `(line, kind)` that triggers each excise, then peeled layers by loosening the top one. Result — the blockers are **LAYERED and CONCENTRATED**, not scattered:

- **LAYER 1 — the narrow alt gate (`scrip.c:330` `alt_safe_kind`) — first trigger for 6 of 8** (deal, queens, micsum, concord, ipxref, tgrlink). The check is whole-graph: if a graph contains ANY `IR_ALT`, EVERY node must be `alt_safe_kind`, whose whitelist is only `{IR_ALT, IR_CALL, IR_EVERY, IR_FAIL, IR_SUCCEED, IR_LIT_I/S/F/NUL}`. So an `IR_TO`/`IR_VAR`/`IR_IF`/`IR_WHILE`/`IR_LIST_BANG` *anywhere* in an alt-containing graph excises it — even when unrelated to the alt. (This whole-graph scoping looks over-broad — arm-scoped would be more correct — but loosening it alone un-excises nothing; see LAYER 2. Also `alt_arms_all_simple_lit` (`:332`) restricts actual alt arms to literals.)
- **LAYER 2 — `IR_ASSIGN` with an unsupported RHS shape (`scrip.c:325`) — the NEXT trigger for 5 of those 6** once Layer 1 is lifted. **CORRECTION (empirically verified — do NOT trust the gate source alone):** `rhs_kind_ok` is actually permissive, and MOST RHS shapes already COMPILE — verified working: `x := []`, `x := [1,2,3]` (list literals; `MAKELIST` is a known builtin with a runtime impl), `x := y[1]` (subscript RHS), `x := "a" || "b"` (concat), `x := f()` (call RHS), and even `every put(a,9)`. The shapes that STILL excise are NARROW and specific:
    - **chained/nested assignment** `a := b := c` (RHS is itself an `IR_ASSIGN`) — e.g. post's `write := writes := 1`;
    - **builtin/procedure used as a value** `x := write` (assigning the builtin reference) — e.g. post's `Save__ := write`;
    - **the `list(n, init)` builtin** specifically (the `[]` literal works; `list(5,0)` excises).
  So the LAYER-2 lever is NOT "list/call RHS" (that works) — it is **chained-assign + builtin-as-value + the `list()` builtin**. The exact failing assign per benchmark still needs the gate-debug method (§ METHOD NOTE) to pin individually; only post's was traced to `write := …`. (post is also special: it reassigns the output builtins `write`/`writes` to suppress output — an unusual pattern; it may not be the best first benchmark.)
- **shuffle** — first trigger is `IR_SWAP` (`:313`) with non-var operands (`!x :=: ?x`): exchange of two generator-produced **lvalues** (list-element refs). Genuinely advanced (reference-valued `:=:`).
- **queens** — after Layer 1, first trigger is `IR_ALT` with non-literal arms (`:332`).
- **post** — first trigger is `IR_ASSIGN` (Layer 2) directly (no alt).

**REFRAME:** the 6 alt-benchmarks do NOT each need 5 unrelated features. They share an ORDERED two-layer blocker: **(1) assign-RHS shapes — list-literal `[]` and call RHS** (5 benchmarks, the dominant next wall), then **(2) richer alternation** (non-literal arms + arm-scoped `alt_safe_kind` instead of whole-graph). Build them in that order and 5–6 benchmarks advance together. This is the single highest-leverage Icon-native target on the board — far more concentrated than the kinds-present table suggests.

**METHOD NOTE for next session:** the gate-instrumentation trick is cheap and decisive — add a `grej(nd,line)` helper that prints under `SCRIP_GATE_DEBUG`, sed the bare `return 0;` sites in `graph_native_emittable_mode` to `return grej(nd,__LINE__);`, build, run each program, read the first `[GATE-REJECT]`. Loosen the top trigger, rebuild, repeat to peel layers. (Mind the line-shift when inserting the helper.) Revert when done — it's diagnostic only.

---

## 2. `IR_INITIAL` IS NOT A GATE LIFT — IT NEEDS A PERSISTENT-WRITABLE-STATIC FACILITY THAT DOES NOT EXIST

The goal file lists "NEXT LEVER (5): IR_INITIAL (explicit `return 0` in gate, blocks queens/deal/post/tgrlink/ipxref)", implying a scan-body-style gate lift (emitter ahead of gate). **I verified this is FALSE.** The scaffolding exists but is **unfinished and unwireable without new infrastructure**:

### What exists (and was never wired)
- `src/emitter/BB_templates/bb_initial.cpp` — a template, but **not declared in `bb_templates.h`, not in any `walk_bb_node`/`walk_bb_flat` dispatch case, not in the Makefile** (neither the `scrip` recipe nor `RT_PIC_SRCS`). Dead file.
- `src/emitter/emit_bb.c` `flat_drive_initial` (~line 1823) — sets up 4 EMIT_PAIRs then `EMIT_PAIR_FILL(pBB,…)` → `walk_bb_node(IR_INITIAL)`, expecting a template to consume the pairs. But `walk_bb_node` has **no `case IR_INITIAL`**, so today it hits the unhandled default → `; [walk_bb_node: kind=134 unhandled]` (kind 134 = `IR_INITIAL`).

### Why wiring it up is NOT enough (I tried; reverted)
Wiring the dispatch case + declaration + build makes `flat_drive_initial`'s template run, but it produces **broken code**, because:
1. **Pair-protocol mismatch.** `x86_pair_jmp(idx)` emits only the *jmp* of pair `idx`; the pair *defines* (pair 2 = `mark_done`, pair 3 = `lbl_β`) must be emitted via the define mechanism. The template instead emits `def L(2)` (an internal label) and `def "β"`, so `mark_done`/`xinit1_mark` is **never defined** (m3: "unresolved forward reference") and `lbl_β` is **double-defined** (template + the body-walk both use `lbl_β`) (m4: "symbol already defined").
2. **The done-flag has nowhere legal to live.** `initial expr` runs the body **once across ALL activations** of the procedure, so the flag must be (a) **persistent across calls** and (b) **writable**:
   - NOT a frame slot — `[r12+off]` is per-activation, resets every call.
   - NOT `.rodata` / the code slab — **`src/machine/bb_pool.c:42` seals the mode-3 RX slab `PROT_READ|PROT_EXEC` (no W)**; the template's `mov ROQ(0), 1` (writing sealed RO storage in the code stream) would **SEGFAULT in mode-3**, and `x86_ro_seal_q` emits a duplicate `.quad` anyway (m4 "symbol already defined" for `.Lx*_0`).
3. **No writable-static mechanism exists.** Grep found **no `.bss`/`.data`/writable-static-seal** emitter primitive. And Icon `static` declarations currently lower to **`IR_SUCCEED` (a no-op)** (`src/lower/lower_icon.c:186` `case TT_STATIC_DECL: build(cx, IR_SUCCEED,…)`) — so `static` vars get **no persistent storage** either. `initial` and `static` share this missing facility.

### The real prerequisite (recommended rung, before any INITIAL/STATIC lever)
Build a **persistent writable static-data facility**: a writable region (`.data`/`.bss` in m4; a separate `PROT_READ|PROT_WRITE` arena — NOT the RX code slab — in m3) addressed `[rip+disp]`, with an emitter primitive to allocate one slot per `initial` site / `static` var. Then:
- `static` (`TT_STATIC_DECL`) stops being a no-op and binds its var to a persistent slot.
- `IR_INITIAL` becomes: `load flag-slot; jnz skip; <body→mark>; mark: store 1; skip: →γ; β:→ω` with the flag in a persistent writable slot, and the EMIT_PAIR defines (`mark_done`, `lbl_β`) emitted correctly (NOT `def L(n)`).
- Only THEN does the gate's `if (nd->op == IR_INITIAL) return 0;` (`scrip.c:308`) come out — for the proven shape.

Until that facility lands, **the gate's defensive excise of `IR_INITIAL` is correct and must stay** (writing to the RX slab would crash; a silent miscompile is worse than a clean excise).

---

## 3. SMALL CORRECTNESS NOTE (independent, untouched)
`walk_bb_node`'s unhandled-kind diagnostic uses `;` (`fprintf(out, "; [walk_bb_node: kind=%d unhandled]\n", …)`, ~4 sites in `emit_core.c`). GAS treats `;` as a **statement separator**, not a comment, so any `.s` containing this line **fails to assemble** (`junk … '['`). Should be `#`. Low priority (only appears on already-gated kinds) but trivially correct.

---

## 4. NO-REGRESSION PROOF
Tree returned to pristine `fa33cd6` (`git checkout` of the 4 files I had touched; `git status` clean in all 3 repos). Rebuilt clean: `build_scrip.sh` rc=0, `libscrip_rt` rc=0, icon smoke **12/12 m3+m4**, rung suite **145/283 m3==m4 unchanged** (FAIL 14 / XFAIL 36 / EXCISED 88), no-stack/one-reg/semicolon-prison gates green. This session was **diagnosis only — zero code delta**.

## 5. RECOMMENDED NEXT MOVES (in order — revised by §1a, CORRECTED by empirical RHS testing)
1. **Richer alternation (LAYER 1) — the highest-concentration lever.** First trigger for 6 of 8. Two parts: (a) change `alt_safe_kind` from **whole-graph** to **arm-scoped** (only nodes inside an alt's arms need be alt-safe — today ANY `IR_ALT` taints the whole graph, excising unrelated `IR_TO`/`IR_VAR`/`IR_IF`/`IR_WHILE`/`IR_LIST_BANG`); (b) relax `alt_arms_all_simple_lit` to allow non-literal arms. VERIFY emitter readiness per-arm before lifting (the bb_alt path may genuinely only handle literal arms — test with the gate-debug method). This alone un-excises nothing (LAYER 2 follows) but is the gate to everything else.
2. **LAYER-2 assign shapes — NARROW (corrected):** NOT list/call/subscript RHS (those already compile). The real gaps are **chained assignment** `a := b := c`, **builtin/proc-as-value** `x := write`, and **the `list(n,init)` builtin**. Pin each benchmark's specific failing assign with the gate-debug method first.
3. **Persistent-writable-static facility** (the §2 prerequisite) — unblocks `static` (currently a no-op) AND `IR_INITIAL`; 5 benchmarks reference it. Bigger lift (m3 RX-slab writability problem).
4. **`every`/`to` value-flow** + remaining **list ops** (`!x` LIST_BANG value-flow in accumulation context) — broad once (1)/(2) land. (Basic `every put(a,x)` and subscript already work.)
5. **Tables + sort** → `concord`. **`IR_SUSPEND`** → `tgrlink`. **`IR_SWAP` reference-valued `:=:`** → `shuffle`.
6. The 4 parse gaps (`return`-in-expr, `create`, if-else-as-RHS, paren comma-subscript) → geddump/micro/options/rsg.
7. Corpus hygiene: remove stale `micro.s`/`micsum.s` (no longer reflect compiler output).
8. The `[NO-AST] eval_ast stub` on `--run` for ipxref/tgrlink — separate routing bug, not the SMX gate.

**META-LESSON (for the next session): test, don't trust the gate source.** Twice this session, reading `graph_native_emittable` suggested a blocker that empirical compilation disproved (IR_INITIAL "just a gate lift" → needs storage infra; "assign list/call RHS missing" → already works). Always confirm a blocker by compiling a minimal case and reading the actual `[GATE-REJECT]`, then by checking whether the emitter ABORTS (real gap) or SUCCEEDS (gate timidity) when the gate is loosened.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
