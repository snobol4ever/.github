# FINDING s199 — DEFER-STAR: the narrowing s197 looked for and concluded did not exist

**SCRIP `9b19bb5a`** (source) + `85bb6d19` (feature .s) · corpus `814934ea` (benchmark .s) + `5afe1179` (demo .s).
**Baseline HEAD-stamped `84ea9f85`.** Census **113 → 48**. Watermark **held exactly**: m3 221/94 · m4 219/94 SKIP=2 · DIVERGE=1 (W06_tab). FAIL sets **byte-identical both modes, zero churn** (diffed, not eyeballed).

## 1. The headline

`emit_graph_has_deep_arrival()` counted **every** `IR_MATCH_DEFER`. That op is built by **two lowering arms the node cannot tell apart**:

| site | source form | semantics |
|---|---|---|
| `lower_snobol4.c` ~1212 / ~1214 | `TT_DEFER` — the `*` operator | value fetched at MATCH time; **can recurse** |
| `lower_snobol4.c` ~1218 | `TT_VAR` — bare pattern-valued variable | built EAGERLY at construction; **cannot recurse** |

The lowerer's own comment on the TT_VAR arm calls it the "twin of the TT_VAR arm above" — the two produce identical nodes (same sval, same `sno_fz_mark_defer`, same seal computation). The distinction was lost at lower time, so the emitter had no way to be anything but conservative.

## 2. Why the split is sound — the manual, not an argument

SPITBOL manual, **"Recursive Patterns" p.122**: a recursive pattern is possible because *"the unevaluated expression operator makes the definition possible"*, and `*LIST` *"allows a forward reference to a pattern not yet defined."* The whole reason `*` exists is that construction is otherwise eager — the manual introduces it (p.85) precisely because `NPAT = ':' LEN(N) . ITEM` "captures the value of variable N at the time of pattern construction."

**Therefore recursion REQUIRES `*`.** A stored pattern reused by name cannot name itself, so it cannot plunge. Only the `*` arm needs conservative deep arrival.

Also confirmed from the manual (p.69–71), supporting s196's alternation-free classification: **BREAK and SPAN are single-result** — SPAN "will match the longest subject string possible", BREAK stops at the delimiter; `BREAKX` is the extending variant and `ARB` is the one that "pokes along one character at a time".

## 3. Measured root — nobody had checked which arm was arming the gate

All four heavy benchmarks armed deep arrival via **exactly ONE `MATCH_DEFER` in `main`**, and **none contains a `*` in source.** Every one was the TT_VAR arm.

roman 29→1 · mixed_workload 34→15 · string_pattern 23→14 · pattern_bt 23→14.

The `PAT$` blob's own pin correctly survives (14 = the scan-retry class). That is irreducible and s196 was right about it: SPITBOL Ch.18 step 6's unanchored retry restarts at cursor+1 from **arbitrary carve depth**, so `mov rsp, rbp` is the only way back. `&ANCHOR` is a runtime keyword, so no static classifier retires it.

## 4. This is NOT the s197 change

s197 dropped `IR_MATCH_DEFER` from the list **wholesale** — also 113→48 — and **correctly reverted it**, because recursive defer is genuinely unbounded and *every* recursive witness already sat inside the 94-FAIL set, making the green false.

This split keeps `*` deep, and that is **verified rather than argued**: the manual's own `ITEM`/`LIST` example still classifies deep (**49 rbp refs, 4 seeds**) while a bare-variable control drops to **14**. s197's "no Use-A narrowing exists" conclusion was right about the split it tried (deferred *scalar* vs deferred *pattern* — dead, since `LEN(*N)` emits no `match_defer`) and missed this one, which is a different axis: **eager vs unevaluated**, the axis the manual itself draws.

## 5. Corrections to prior prose

- **s196's `flat_pat_susp` estimate is too optimistic.** Measured: the γ/ω epilogue's removable part under an alternation-free blob is `push rbp` = **1 line per blob (3 total)**, not "~6/blob, ≤12". γ's other two refs (`mov rax,[rbp+136]`, `mov rbp,[rbp+152]`) are reached from arbitrary depth and are not statically convertible.
- **The ~90 ceiling in s196/s197 is superseded.** Both assumed the ~65 DEFER refs were irreducible. Most were TT_VAR. New floor is **48**, and the residue is now dominated by the genuinely irreducible `PAT$` scan-retry class.

## 6. Known pre-existing, explicitly NOT introduced here

A stored-pattern reference (`PAT = BREAK(',') . W ','` used as `S PAT`) **SIGSEGVs in m3 on clean `84ea9f85` too** — verified by stash + rebuild + rerun, not assumed. That is the **s198 stored-pattern segv, rung (a)**. Benchmark runtime signatures are byte-identical pre/post (4 SIGSEGV + 1 timeout, all pre-existing).

## 7. Next

(a) **s198 rung (a) stored-pattern segv** — unchanged as #1; my control above is a second independent reproducer alongside `NPAT = ':' / ? NPAT`.
(b) **DEFERRED-ARG BUG** (`LEN(*N)` empty capture) — s197/s198 rung.
(c) **ARBNO-ELEM dig** — s195.
(d) `flat_pat_susp` epilogue split — now known to be worth only ~3; deprioritize accordingly.
