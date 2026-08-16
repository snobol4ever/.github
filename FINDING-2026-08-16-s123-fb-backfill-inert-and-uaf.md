# FINDING s123 — THE s62 FB-BACKFILL IS DOUBLY DEAD: IT WRITES TO FREED MEMORY, AND NOTHING EVER READS IT

**Measured 2026-08-16 s123 (Claude Opus 5).** SCRIP `f36bb76d`. NO CODE CHANGED — probes added, measured, removed; all OFF-arm `.s` md5s verified unchanged afterwards (fibonacci `a48740453935fb0999c070cac7c77cec`, the s122 pin).

Found while assessing the s122 `module_init` relocation design. It is not a `module_init` bug; `module_init` is how it surfaced.

---

## THE CLAIM

`scrip.c:1370`'s **STATEMENT-ORDER FB-BACKFILL (s62)** has never once had an effect, and it has been writing to freed heap the whole time.

Two independent defects in one loop:

1. **USE-AFTER-FREE.** `scrip.c:1333` frees `proc_fb_buf` and `proc_pidx_buf` (with three siblings). Line 1370 then indexes **both**. 37 lines, unconditional, same scope.
2. **NO READER.** `proc_fb_buf` is read at exactly three sites — `scrip.c:1235`, `:1288`, `:1290` — all inside the `main_init` block (`:989-1331`), all of which emit **before** 1370 runs. After 1370 there is not one read. The backfill writes a value nobody will ever look at.

So the row that the s62 author intended to correct is emitted with the **stale 0**, every time, in every program.

## THE INTENT, IN THE CODE'S OWN WORDS

`scrip.c:1369` states what the backfill is for:

> STATEMENT-ORDER FB-BACKFILL (s62): LBL__ rows share main's frame — ARG/LOCAL read frame_bytes at runtime to index formals/locals. At record time (line 926) we wrote 0 because the LBL__ standalone chain no longer emits and `g_last_flat_frame_bytes` was stale from the prior proc; now main has emitted, `g_last_flat_frame_bytes` holds its true value…

`frame_bytes` is **read at runtime by ARG/LOCAL to index formals and locals.** The intended value is main's frame; the shipped value is 0.

## HOW IT WAS MEASURED (not read — measured)

**(1) Does the loop fire?** Temporary `SCRIP_MI_PROBE` counter, 292 programs:

| fires | program | rows patched |
|---|---|---|
| ✅ | `beauty.sno` | **14** |
| ✅ | `porter.sno` | 30 |
| ✅ | `TDump_driver.sno` | 6 |
| ✅ | `Qize.sno` | 2 |
| — | all 72 benchmark + probe programs | **0** |

**(2) Is the memory freed first?** `proc_fb_buf`/`proc_pidx_buf` set to NULL immediately after the `free` under a probe flag. `beauty.sno` goes **rc=0 → rc=139**. gdb, one frame:

```
Program received signal SIGSEGV
#0  main (...) at /home/claude/SCRIP/src/driver/scrip.c:1370
```

**(3) Is there a reader after it?** `awk 'NR>1370 && /proc_fb_buf/'` → empty.

## ⛔ WHY THE BENCHMARK COLUMN IS THE IMPORTANT ONE

Every witness set this area would naturally be gated with — fibonacci, roman, func_call, cap_imm_nret, the 141-probe suite — reports **0**. A seat that "proved" a change here against the benchmarks would see byte-identical output and ship. The four programs that fire are all in `programs/snobol4/`, and one of them is **`beauty.sno`, Milestone 1's own program, with 14 affected rows.**

This is the s118 shape a third time: correct everywhere you look, wrong where you did not look.

## RELEVANCE TO MILESTONE 1 — STATED CAREFULLY

`beauty.sno` has 14 LBL__ rows whose `frame_bytes` is emitted 0 where the s62 author's stated intent was main's frame (measured `main_fb=1216` for beauty), and ARG/LOCAL index formals/locals with that field at runtime.

⛔ **THIS IS NOT YET A CLAIM THAT IT BREAKS BEAUTY.** Not measured: whether any of those 14 rows is ever entered through a path that reaches an ARG/LOCAL index. The s122 root cause (stored-pattern blob β dead end, `emit.cpp:2288`) is untouched by this and remains the named M1 blocker. This is a **candidate second cause** in the same class as the already-open `$'$X'`/`$'$C'` marker defect — worth measuring, not worth assuming.

## WHAT THE NEXT SEAT MUST DECIDE (in this order)

1. **Is post-backfill the correct value?** The s62 comment says yes. If so the backfill must move **above** the `main_init` emission so it can actually be read — which changes emitted bytes on exactly those four programs, and on nothing else.
2. **Then fix the UAF.** Moving the backfill above `:1333` fixes both defects at once and is the natural shape. Simply moving the `free` below 1370 silences the UAF while leaving the backfill inert — that is the wrong fix and would bury the real one.
3. **Only then** revisit the `module_init` relocation. ⛔ Note the trap: relocating `module_init` to the bottom as designed puts its three `proc_fb_buf` reads **after the free at :1333** — the s122 design as written would introduce a *second* use-after-free, this one on a read path.
4. **Gate against `beauty` + `porter` + `TDump_driver` + `Qize`.** A green benchmark sweep proves nothing here, by measurement.

## FALSIFIED / RETRACTED THIS SESSION

- s123's own first framing called `:1370` a pure "ordering barrier" (write-after-read) blocking relocation. Accurate as far as it went, but it **understated the defect**: the buffer is already freed at that point and the write has no reader at all. The barrier is real; it is also a corpse.
