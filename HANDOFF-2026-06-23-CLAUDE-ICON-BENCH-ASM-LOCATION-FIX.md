# HANDOFF — Icon `.s` benchmark-artifact maintenance repointed to the real corpus (Claude)
## Infra/corpus/docs only — NO codegen change. Suite unchanged 144/283. All three repos pushed.

**Heads:** corpus `a88c6ad8` · SCRIP `97e4d9d` · .github `22a81433` (+ this handoff + watermark).
No emitter/lowerer behavior change this session. Build green throughout; m3/m4 = **144/283**
(unchanged), all FACT gates green, icon smoke 12/12 m3+m4, prolog 5/5.

---

## WHAT WAS WRONG

The side-by-side `.s` artifact procedure (established `f06b4ee` / `PROC-ICON-BENCH-ASM.md`)
pointed `update_icon_bench_asm.sh` at **`/home/claude/corpus/programs/icon`** with default glob
**`rung36_jcon_*.icn`**. That directory is the **rung TEST suite** (293 `.icn`, matched against
`.expected` by `test_icon_rung_suite.sh`), NOT the benchmark corpus.

The actual benchmark sources were merged into **`corpus/benchmarks/icon/`** (commit `37bc1bc5`):
13 programs — `concord deal geddump ipxref micro micsum options post queens rsg shuffle tgrlink
version`. That directory had **ZERO `.s` artifacts**. So "every benchmark `.icn` carries a
side-by-side `.s`" was simply not happening for the real benchmark corpus.

## WHAT LANDED

1. **SCRIP `97e4d9d`** — `scripts/update_icon_bench_asm.sh`: default `ICON_CORPUS` →
   `/home/claude/corpus/benchmarks/icon`, default `GLOB` → `*.icn` (was `programs/icon` +
   `rung36_jcon_*.icn`). Header usage block updated to match. No logic change to the
   canonicalize/3-sample-determinism/assemble machinery.
2. **corpus `a88c6ad8`** — generated `.s` for the **3 benchmarks that compile cleanly today**:
   `micro.s`, `micsum.s`, `version.s`. Committed next to their `.icn`.
3. **.github `22a81433`** — `GOAL-ICON-FULL-PASS.md` gained a "Side-by-side `.s` artifacts" block
   (correct location + the run-on-every-Icon-handoff rule); `PROC-ICON-BENCH-ASM.md` location +
   baseline corrected, with an explicit note that the old `programs/icon` target was the test
   suite. (This handoff + the watermark are a follow-on .github commit.)

## CURRENT BENCHMARK-CORPUS `.s` STATUS (SCRIP `97e4d9d`, `benchmarks/icon/`, 13 programs)

- **maintained = 3**: `micro micsum version` (compile clean, deterministic, `.s` committed).
- **compile-err (CERR) = 8**: `concord deal ipxref options post queens rsg tgrlink` — `--compile`
  aborts; native arms pending (F2 `<-`, F1 subscript-assign, `link` resolution, & friends). Each
  auto-acquires a `.s` the first time it compiles.
- **excised (EXCISED) = 2**: `geddump shuffle` — a kind still EXCISEs; same auto-pickup rule.

`CHECK=1 bash scripts/update_icon_bench_asm.sh` reports **zero drift** at HEAD (the maintenance
gate is now wired to the right directory and will flag the next emitter change to any of the 3).

## STANDING REMINDER FOR EMITTER SESSIONS

Per `RULES.md` handoff step 4 (now pointing at the correct dir via the script default): after any
Icon-emitter/lowerer change, run `bash scripts/update_icon_bench_asm.sh` and commit the corpus
delta alongside the SCRIP commit. As headliners (esp. `queens` once F2 `<-` lands) start
compiling, this auto-populates their `.s`.

## NEXT (unchanged from prior handoff — smallest +PASS first)

The 14 open FAILs are untouched this session. Smallest wins still on the board:
1. `rt_size_d` list-size bug — `rung22_lists_push_put_size` (+1, ~15 min). `*L`→3 not 0; fix in
   `by_name_dispatch.c` (return list `frame_size` for `DT_DATA`/`list`).
2. dv=1.0 userproc chain routing — `rung32_strret_every` (+1, ~20 min). `every write(tag(...))`;
   route dv==1.0 registered-proc calls to `flat_drive_call_userproc` in the descr flat chain.
3. `bb_limit.cpp` counter — `rung14_limit_*` (+3, ~1 hr). Canonical `ir_a_Limitation`
   (`refs/jcon-master/tran/irgen.icn:113`).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
