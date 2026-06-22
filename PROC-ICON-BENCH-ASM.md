# PROC-ICON-BENCH-ASM.md — maintaining side-by-side x86 `.s` artifacts for Icon benchmarks

**What:** every Icon benchmark `.icn` in the corpus that compiles cleanly carries a
sibling `.s` — the **current SCRIP emitter's** x86 output (`--compile --target=x86`,
GAS `.intel_syntax`). These are committed next to the source so a diff of the corpus shows,
over time, exactly how the emitted code for each benchmark changes as the Icon backend
evolves. They are an emitter-regression snapshot, NOT hand-written.

**Tool:** `SCRIP/scripts/update_icon_bench_asm.sh` (single source of truth; do not hand-edit
the `.s` files).

```bash
cd /home/claude/SCRIP && bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/update_icon_bench_asm.sh            # regenerate/refresh; writes only on real change
CHECK=1 bash scripts/update_icon_bench_asm.sh    # dry-run; exit 1 if any artifact is stale
bash scripts/update_icon_bench_asm.sh 'queens.icn'   # restrict to a glob (default rung36_jcon_*.icn)
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

## Baseline (2026-06-22, SCRIP `a18778b`, glob `rung36_jcon_*.icn`, 75 programs)
maintained=6 (`center map misc right toby[ASMWARN] trim`) · nondet=2 (`left nargs`) ·
compile-err=2 (`iobig level`) · excised=65. The legacy `.s` siblings predating this procedure
were NASM-syntax dumps from a retired `icon_emit.c`; they are superseded by the current GAS
output as each program becomes maintainable.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
