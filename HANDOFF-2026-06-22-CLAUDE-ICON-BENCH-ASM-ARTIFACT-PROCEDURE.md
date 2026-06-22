# HANDOFF — Icon benchmark `.s` artifact maintenance procedure (Claude)
## HQ procedure + tool established; 6 benchmark artifacts regenerated from the current emitter. Pushed to all three repos.

**Heads:** SCRIP `f06b4ee` · corpus `8a096a0d` · .github (this commit). No emitter/lowerer behavior change in this segment — corpus artifacts + HQ infra only. (Earlier in the same session: BENCH-F1.5 landed at SCRIP `a18778b`; suite 140/283 — see `HANDOFF-2026-06-22-CLAUDE-ICON-BB-BENCH-F1.5-UNOP-ASSIGN-VALUE-FLOW.md`.)

---

## WHAT WAS ASKED
Produce + maintain side-by-side `*.s` artifacts for the Icon benchmark programs in the corpus, next to each `.icn`; keep each `.s` updated whenever its content actually changes; put the procedure in HQ (mirroring the existing SNOBOL4 artifact pattern).

## WHAT LANDED
1. **`SCRIP/scripts/update_icon_bench_asm.sh`** (new) — the single source of truth. For each `corpus/programs/icon/<glob>.icn` (default glob `rung36_jcon_*.icn`, the JCON benchmark family): compile with the current emitter (`--compile --target=x86`), and write the sibling `.s` **only when its content actually changed**. Modes: bare = refresh; `CHECK=1` = dry-run (exit 1 on drift, for CI); positional arg = glob; `ICON_CORPUS=` = corpus override.
2. **`.github/PROC-ICON-BENCH-ASM.md`** (new) — documents the procedure, the canonicalization rationale, and the maintained/skip taxonomy.
3. **`.github/RULES.md`** handoff step 4 extended — Icon-emitter handoffs now also run `update_icon_bench_asm.sh` (alongside the existing SNOBOL4 `util_regen_*` artifact step).
4. **`corpus/programs/icon/*.s`** — 6 regenerated from the current emitter (`5816d3ff`).

## THE TWO NON-OBVIOUS DESIGN POINTS (why this took care)
The SNOBOL4 `--compile` output is deterministic, so its artifact script just compiles + diffs. **The Icon emitter is NOT:**
- **Address-derived labels.** Internal labels are named from heap addresses (`bb52384_α`, `.Lcall31952_pname`), which vary run-to-run under ASLR. The script renumbers every address-derived label digit-run (`(?<=[A-Za-z])(\d{3,})_`) to a stable `00001` sequence by first appearance — a consistent global substitution over defs **and** references, so the canonical `.s` still assembles (verified with `as`). Without this, every run would rewrite every file (pure churn) and the "update only on real change" requirement fails.
- **Intermittent emission-order non-determinism.** For the *larger* programs (`left` 1181 lines, `nargs` 3902 lines) the **order** in which nodes are emitted varies run-to-run (address-keyed iteration), which label-renaming alone can't canonicalize (the blocks themselves reorder). The script runs a **3-sample determinism gate** (compile 3×, all canonical outputs must match) and **skips** (NONDET) anything that fails, so the maintained set never churns. This is intermittent (ASLR-layout dependent) — a 2-sample gate let `nargs` through ~half the time; 3 samples is far more reliable but still env-dependent for these two.

## BASELINE (SCRIP `a18778b`, glob `rung36_jcon_*.icn`, 75 programs)
- **maintained = 6**: `center map misc right toby[ASMWARN] trim` (committed as current GAS, superseding their legacy NASM `icon_emit.c` dumps).
- **nondet = 2**: `left nargs` (skipped; left as legacy NASM).
- **compile-err = 2**: `iobig level` (`--compile` aborts — a real emitter bomb, tracked).
- **excised = 65**: native arm pending — incl. the BENCH headliners `queens`/`concord`/`genqueen`. These auto-acquire a `.s` the first time they compile (i.e. once F2 `<-` + F1 subscript-assign land).
- **ASMWARN**: `toby` compiles + is deterministic but its standalone `.s` doesn't assemble (dup labels — the known "m3 tolerates, m4 `as` rejects"). Written anyway as a faithful snapshot, annotated.

## FOLLOW-UPS (surfaced, not done)
1. **Make Icon emission order deterministic** (iterate nodes by id, not pointer address) — then `left`/`nargs` become maintainable and the `CHECK=1` gate stops intermittently flagging them. This is the root cause behind both the NONDET skips and any `CHECK=1` flakiness.
2. **`iobig`/`level` `--compile` aborts** — real emitter bombs, independent of this work.
3. As Icon features land (esp. **BENCH-F2 `<-`**, the queens keystone — fully specced in `HANDOFF-2026-06-22-CLAUDE-ICON-BB-BENCH-F1.5-UNOP-ASSIGN-VALUE-FLOW.md`), re-running the script auto-populates the headliner benchmark `.s` files.

## HOW TO RUN
```bash
cd /home/claude/SCRIP && bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/update_icon_bench_asm.sh          # refresh (writes only on change)
CHECK=1 bash scripts/update_icon_bench_asm.sh   # dry-run / CI gate
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
