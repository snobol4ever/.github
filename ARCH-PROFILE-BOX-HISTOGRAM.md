# ARCH-PROFILE-BOX-HISTOGRAM.md — the standard per-box wall-cost histogram

**Tool:** `SCRIP/scripts/profile_box_histogram.sh prog.sno input [top_n]`
**Born:** s143 (2026-07-24), expression-eval case study. **Do not re-derive this from scratch — run the script.**

---

## What it produces

ONE unified, ranked histogram of where a mode-4 program's wall time goes, at
BOX granularity for emitted code and FUNCTION granularity for the runtime:

```
cyc-proxy split: emitted boxes 55.1%  |  runtime+libc 44.9%
     cyc-proxy  cyc%             Ir   Ir%     Bcm+Bim       D1m     DLm  box-family / rt:function
   667,730,073  34.3    519,595,708  37.2   8,610,701   419,758     342  xchain
    57,472,472   3.0     17,410,932   1.2   2,660,862       9,901      9  proc_PAT$2_γ
    56,005,838   2.9     43,207,753   3.1     351,105      73,624     20  rt:try_call_builtin_by_name
```

This is possible because **every emitted box label is a real symbol (`nm` t/T)
in an m4 binary** — 545 of them in expression-eval — so instruction-level
callgrind costs can be joined back to the exact box (and port) that spent them.

## How it works (all encoded in the script — listed here so nobody re-solves them)

1. Compile `.sno` → mode-4 `.s` → `gcc -no-pie` binary (labels become symbols).
2. `valgrind --tool=callgrind --dump-instr=yes --cache-sim=yes --branch-sim=yes
   --main-stacksize=2000000000` (the 2G main stack is the s142 rsp-ζ fix —
   without it valgrind's 64MB cap kills the run).
3. Join: for costs inside the program's `ob=`, binary-search the instruction
   address against the sorted `nm -n` t/T table → owning label; for the
   runtime `.so` / libc `ob=`s, aggregate by the current `fn=` name (`rt:` prefix).
4. **Callgrind format traps (each cost a debugging round on first contact):**
   - the cost line after a `calls=` line is the CALL-INCLUSIVE cost of that
     call site, not self cost — skip it, or `main`/`_start` absorb the program;
   - `positions:` may be `instr` or `instr line` — the event columns shift;
   - subpositions are compressed: absolute `0x…`, relative `+N`/`-N`, `*` = same;
   - `fn=` lines carry name-compression `(id) name` / bare `(id)` back-refs.
5. Family rollup: strip `_n<K>_<port>` and trailing digits so a box's per-node
   instances aggregate (`xchain190_n2_α` → `xchain`); `GRAN=label` disables.

## The cycle proxy — and the two laws

```
cyc-proxy = Ir + 10*(I1mr + D1mr + D1mw) + 100*(ILmr + DLmr + DLmw) + 15*(Bcm + Bim)
```

A RANKING metric, not absolute cycles. It exists because of:

**LAW 1 — Ir LIES on rep-string ops.** callgrind counts every `rep stosb`
iteration as an instruction; ERMS microcode fills ~560B in ~35 cycles. s143
measured proof: the PAT$ α blanket fill was 52% of blob **Ir** yet its removal
(CAP-NOFILL) bought 10% **wall**. The inverse was s142's whack lesson (−8.5% Ir
bought −30% wall — branch/store-buffer traffic under-counted). Rank by
cyc-proxy; treat bare-Ir rankings as advisory only.

**LAW 2 — absolute ms drift with host load.** The SAME bytes (cmp-proven .so)
measured 51ms and 71ms on treebank minutes apart. This tool RANKS candidates;
a win is only proven by same-moment interleaved A/B medians
(`scripts/bench_sno_match4.sh` — the s141/s108 bimodality protocol). Never
compare absolute ms across runs, sessions, or containers.

## Reading the table

- `<box>_α` — activation/prologue cost (frame carve, wire saves, zero fills).
  Post-CAP-NOFILL these should be near-pure Ir (straight-line stores, Bcm≈0).
- `<box>_β` — resume; `<box>_γ` / `<box>_ω` — success/fail edges. High Bcm on
  γ/ω = the backtrack record machinery (the s142 γ-record disease).
- `xchain` — SEQUENCE glue chains minted by the emit driver. High Bcm here =
  trampolining jmp chains (BC-CENSUS class) → the BC-EMIT-ACC fold rung.
- `proc_PAT$N_*` — frozen pattern blobs, numbered in freeze order; map N to a
  source pattern by grepping the `.s` around `proc_PAT$N_α` for its literals.
- `scanfail`/`scanhit` — unanchored-scan cursor-advance arms.
- `rt:*` — runtime/libc. Watch the LL-miss column: a modest-Ir `rt:` entry with
  huge DLm (s143: `rt:strtok_r` 1.5% Ir / 852K DLm / 6.0% cyc) is a cache
  disease, not an instruction-count disease.

## Workflow (the loop that leads home)

1. `profile_box_histogram.sh` the failing/slow program → ranked candidates.
2. Pick the top family; read its emitted `.s` body; design the cut (template
   change ⇒ BB-CODEGEN design-set gate applies; runtime-only ⇒ no gate).
3. Land behind a kill-switch env; poison/identity lanes where state is skipped.
4. Gates: smokes 7/7×2 · crosscheck ≥ watermark m3+m4 · DIVERGE=0 (plain AND
   poison when applicable).
5. Prove the win with same-moment interleaved A/B; re-run the histogram to
   confirm the family shrank and see what surfaced next.

**Targets (Lon, s143): 2–3× SPITBOL on pattern matching, 4–6× on functional
code.** The histogram is the map; every session picks the top bar and cuts it.

## Provenance / worked case study (s143, expression-eval)

Ir-only histogram named PAT$ α at 52% of blob → CAP-NOFILL landed → wall −10.1%
(834→750ms same-moment). Cyc-proxy histogram then named the truth: `xchain`
62.6% of blob cycles carrying 8.9M mispredicts per 3 passes → LIVE CURSOR =
BC-EMIT-ACC aimed at xchain. C-side snipe candidates surfaced by the unified
table: `rt:strtok_r` (6.0% cyc, LL-miss-bound), `rt:pat_pool_ctor`,
`rt:try_call_builtin_by_name` (by-name dispatch, SPD-4).
