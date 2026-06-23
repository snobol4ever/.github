# PROC-ICON-BENCH-ASM.md — maintaining side-by-side x86 `.s` artifacts for Icon benchmarks

**What:** every Icon benchmark `.icn` in `corpus/benchmarks/icon/` that compiles cleanly carries a
sibling `.s` — the **current SCRIP emitter's** x86 output (`--compile --target=x86`,
GAS `.intel_syntax`). These are committed next to the source so a diff of the corpus shows,
over time, exactly how the emitted code for each benchmark changes as the Icon backend
evolves. They are an emitter-regression snapshot, NOT hand-written.

(NB: `corpus/programs/icon/` is the rung **test** suite, NOT the benchmark corpus; its legacy
NASM `.s` siblings predate this procedure and are out of scope here. The benchmark sources —
queens, concord, deal, ipxref, rsg, micro, micsum, version, … — live in `benchmarks/icon/`.)

**Tool:** `SCRIP/scripts/update_icon_bench_asm.sh` (single source of truth; do not hand-edit
the `.s` files).

```bash
cd /home/claude/SCRIP && bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/update_icon_bench_asm.sh            # regenerate/refresh; writes only on real change
CHECK=1 bash scripts/update_icon_bench_asm.sh    # dry-run; exit 1 if any artifact is stale
bash scripts/update_icon_bench_asm.sh 'queens.icn'   # restrict to a glob (default *.icn)
ICON_CORPUS=/path/to/icon bash scripts/update_icon_bench_asm.sh   # override corpus dir
```

## The procedure (run on every Icon-emitter handoff)

1. Build `scrip` + `libscrip_rt`.
2. Run `scripts/update_icon_bench_asm.sh`. It rewrites a `.s` **only when its content
   actually changed** — so the resulting git diff is exactly the set of benchmarks whose
   emitted code your session altered. An empty diff means your change was output-neutral for
   the benchmark set.
3. `git add -A && git commit` the corpus alongside your SCRIP commit, so the artifacts never
   lag the emitter. Mention the artifact delta in the commit body.

This is wired into the handoff sequence in `RULES.md` ("Icon-emitter handoff").

## Why the `.s` is canonicalized (and why it's safe)

The emitter names internal labels from heap **addresses** (`bb52384_α`, `.Lcall31952_pname`,
…), which vary run-to-run under ASLR. The script renumbers every address-derived label
digit-run to a stable `00001`-style sequence by order of first appearance, so re-running on
an unchanged source+emitter yields a byte-identical `.s` (no churn). The renumbering is a
consistent global substitution over defs **and** references, so the canonical `.s` assembles
to equivalent machine code (verified with `as`).

## What is and isn't maintained

A benchmark's `.s` is written/updated only if it:
- compiles to non-empty output (no `[SMX]` EXCISE, no compile abort), **and**
- is **deterministic** — three independent compiles produce identical canonical output.

Reported-and-skipped (existing artifact, if any, left untouched):
- **EXCISED** — native arm pending (the bulk today; picked up automatically once the feature
  lands and the program compiles). The BENCH-ladder headliners (`queens`, `concord`,
  `genqueen`) are here until F2 `<-`/F1 subscript-assign land.
- **CERR** — `--compile` aborts (e.g. `iobig`, `level`): a real emitter bomb, tracked
  separately.
- **NONDET** — emission order varies run-to-run (e.g. `left`, `nargs`): a known emitter
  non-determinism (address-keyed iteration order). These cannot be stably maintained until
  the emitter's node-iteration order is made address-independent. **Follow-up:** make the
  emitter iterate nodes in a deterministic (id-keyed, not pointer-keyed) order, then these
  benchmarks become maintainable and the `CHECK=1` gate stops flagging them.
- **ASMWARN** — compiles + deterministic but the standalone `.s` doesn't assemble (dup labels
  — the known "m3 tolerates dup labels, m4 `as` rejects" limitation, e.g. `toby`). The
  artifact is still written (faithful emitter snapshot) and annotated.

## Baseline (2026-06-22, SCRIP `dd0d0a2`, corpus `benchmarks/icon/`, glob `*.icn`, 13 programs)
maintained=3 (`micro micsum version`) · compile-err=8 (`concord deal ipxref options post queens
rsg tgrlink` — native arms pending: F2 `<-`, F1 subscript-assign, link resolution) · excised=2
(`geddump shuffle`). The headliners `queens`/`concord` auto-acquire a `.s` the first time they
compile. (Superseded location note: the prior baseline pointed `update_icon_bench_asm.sh` at
`programs/icon/` with glob `rung36_jcon_*.icn`; that was the rung test suite, not the benchmark
corpus — corrected here to `benchmarks/icon/`, glob `*.icn`.)

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
