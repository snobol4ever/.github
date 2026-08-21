# FINDING s190 (seat3, `/home/claude3`, Claude Opus 5) — queue row `claws5-m4-sig11` (GOAL-SCRIP-HQ D-2)

## ⭐⭐⭐ THE HEADLINE: THE DEFERRED-CAPTURE ROAD RESOLVES ITS CALLEE THROUGH A CELL THAT **ONLY THE COMPILER PROCESS EVER FILLS**. THE INGREDIENT IS THE CAPTURE-TARGET **POSITION**, NOT THE CALL — AND THE ROW'S "×3" IS NOW ×1.

`. *token()` — a deferred function call in **capture-target position** — routes through `rt_dcap_pump` (`pattern_match.c:705`), which reaches its callee **by name at runtime** via `rt_call_proc_descr` (`rt/rt.c:908`). That line is the dyn road, `rt_proc_enter(rt_dyn_alpha_fn(name, p->fn))`, and it resolves through the **`alpha$<FN>` cell**. Those cells are filled by **`m3_seal_entry_cells`, which lives in `src/driver/scrip.c`** (call sites :1682, :1721, :1814) — *the compiler process*. **A mode-4 image contains ZERO `alpha$` cells** (`grep -c 'alpha\$'` on the emitted `.s` = 0), so the transfer lands on a null-derived address.

Confirmed by backtrace, not inferred:

```
#4  rt_call_proc_descr (name=0x4020b3 "tok", nargs=0)  rt/rt.c:908
#5  rt_dcap_pump ()                                    pattern_match.c:705
rip = rcx = 0x8
```

This is the s186 seat8 formulation exactly — *"a cell the compiler process sealed and the emitted binary never inherited"* — instantiated on the dcap road. m3 is green **because the compiler process still holds the sealed cell**; that pass is not evidence the road is sound.

## ⭐ THE ROW SAYS "SIG11 ×3". AT THIS HEAD IT IS ×1.

Measured with the data file on stdin (`< claws5.dat` — the programs read it there; running them `< /dev/null` makes every engine print `check: 0`, which is a measurement artifact and not a defect):

| program | m3 | m4 |
|---|---|---|
| `claws5-match` | GREEN `check: 66757` | **GREEN** |
| `claws5-match-fence` | GREEN `check: 66757` | **GREEN** |
| **`claws5`** | GREEN `check: 6469` | **SIG11 rc=139** |

Both `-match` siblings now pass in *both* modes — consistent with the `span-frame-flip` landing that the row's own brief says answered the m3 half. **Only `claws5.sno` remains, so the row's scope is one program, not three.**

## THE THIRD RUNG — WHAT THE EXISTING PAIR COULD NOT SEPARATE (corpus `61e8dfd2`)

The checked-in D-2 pair differs by the *whole call*: the green **deletes** `. *token()` and fires `n=0`. That cannot tell "the deferred call" from "the capture-target POSITION". I added a rung that keeps the call and moves it **one character**:

| witness | shape | `n` | m3 | m4 |
|---|---|---|---|---|
| `claws5_dcap_call_red` | `. *token()` — capture target | 9 | GREEN | **SIG11** |
| `claws5_dcap_call_green` | call deleted | 0 | GREEN | GREEN |
| **`claws5_dcap_call_noncap_green`** (new) | `*token()` — not a capture target | **9** | GREEN | **GREEN** |

**The new rung fires the deferred call the same 9 times as the red one and is green in both modes.** So the deferred call is exonerated; the ingredient is the **position**. A non-capture `*token()` lowers to the ordinary defer road; the capture-target form does not.

## THE ASM DIFF (ASM-DIFF-FIRST, per the brief) — TWO DIFFERENT ROADS, NOT TWO VERSIONS OF ONE

| | RED (`. *token()`) | GREEN (non-capture) |
|---|---|---|
| `rt_defer_run_all` | **absent** | 2 |
| `rt_defer_get_pat_dtp` | **absent** | 2 |
| `rt_call_arr` | 2 | **absent** |

The capture-target form does not emit the defer machinery at all — it emits `rt_call_arr` and defers resolution to `rt_dcap_pump`'s by-name road at runtime. ⛔ **Registration is NOT the difference:** both arms emit exactly one `rt_proc_register_rec` and one `.Lstartup_prec` record. I first suspected a missing registration and that is **wrong** — the record is present in both; what is missing in m4 is the `alpha$` cell the *dyn* road reads.

## INDEPENDENT MINIMAL WITNESSES (10 lines, outside the claws5 grammar)

The class is not specific to ARBNO/ALT. Minimal repro, oracle `n=1` in all three:

- `SPAN('0123456789') . w . *tok()` + `:(NRETURN)` → m3 GREEN, **m4 rc=139**
- same with `:(RETURN)` → m3 GREEN, **m4 rc=139** ⇒ **NRETURN is exonerated**
- `SPAN('0123456789') . w *tok()` → m3 GREEN, **m4 GREEN**

`FENCE`, `IDENT`, `TABLE` are all exonerated too: `claws5-match-fence` carries FENCE and is green in m4, and a 5-line 3-level `IDENT(...)/TABLE()` build is green in both modes.

## ⛔ NOT MY CHANGE — CHECKED TWO WAYS

This session also landed `SCRIP_GOTO_TAIL` (computed-goto tail transfer). It is **not** implicated here: `claws5.sno` m4 is rc=139 under **both** `SCRIP_GOTO_TAIL=1` and `=0`, and the program contains **zero** computed gotos.

## ⛔ CORRECTIONS I MADE TO MYSELF WHILE WORKING THIS ROW (recorded, not buried)

1. I first ran the claws5 programs `< /dev/null` and reported a "silent wrong answer" (`check: 0` vs the ref's `66757`). **Wrong** — the programs read `claws5.dat` on stdin, as their own header comment says. With the data they match their refs exactly.
2. On the same bad measurement I called the `.ref` **stale**. **Wrong** — it is correct.
3. I claimed the red arm "never registers the proc". **Wrong** — both arms register identically; the missing thing is the `alpha$` cell, not the record.

## RECEIPTS

SCRIP `f4c3fbb75` + this session's `b12cb82e`; RT_OPT `-O0`; oracle `sbl -b`. m4 built as `--compile` → `gcc -no-pie … -lscrip_rt`. Corpus board unaffected by this row (investigation only; **no fix landed — the row says fix optional**).

## SUGGESTED ROWS (asked, not worked)

1. **`dcap-alpha-cell-m4`** — the fix: either emit `alpha$<FN>` cells into the mode-4 image (the `body$<ENTRY>` precedent already crosses this seam), or give `rt_dcap_pump` a resolution road that does not depend on a driver-sealed cell. `bb_define.cpp`'s `bb_ab_seal_entry_cells` is the hoisted twin and the natural landing site.
2. **`dcap-capture-target-lowering`** — why does capture-target position bypass the defer road entirely (`rt_call_arr`, no `rt_defer_*`)? If the two positions lowered the same way, the mode-4 gap would not be reachable from this direction at all.
