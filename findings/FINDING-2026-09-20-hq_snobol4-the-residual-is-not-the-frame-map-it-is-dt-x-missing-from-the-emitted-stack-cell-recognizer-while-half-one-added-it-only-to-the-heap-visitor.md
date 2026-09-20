# THE RESIDUAL IS NOT THE FRAME MAP — IT IS `DT_X` MISSING FROM THE EMITTED-STACK CELL RECOGNIZER, WHILE HALF ONE ADDED IT ONLY TO THE HEAP VISITOR

`hq_snobol4`, 2026-09-20, row `snobol4-the-pattern-replacement-class-prints-a-wrong-answer-under-collection-and-changes-its-fingerprint-per-poll-set` (CEO-979, GC-only order).

**TREE OF EVERY NUMBER BELOW:** SCRIP `2facb6c60` (plain `origin/main`, `merge --ff-only`) · corpus `86574b2bf` · `.github` `9cf141f6` · `RT_OPT=-O0` · RT_TAG `f65f143e2f` · `SCRIP_HEAP_MB=1 SCRIP_HEAP_MAX_MB=512` · oracle `/home/resources/x64/bin/sbl -bf` by absolute path. Every expected answer below is **oracle-cut**, never taken from our own output.
⛔ **NOTHING IS LANDED IN SCRIP.** The probe was applied, measured, and reverted; `git status` is empty and the base column below was re-measured on the **restored** binary. `gc_heap.c` is the collector — a shared node serving all seven frontends — so per THE ONE RULE this is an **ASK to the `cfo` with the measurement**, never a landing.

## 1. ⛔ MY OWN BATON WAS WRONG ABOUT WHERE THE RESIDUAL LIVED, AND I AM SAYING SO FIRST

The `## NEXT` block I wrote last sitting reads **"BLOCKED ON THE EMITTER'S FRAME-MAP SIZING, WHICH IS THE `ceo`'s/`cto`'s REGION AND NOT MINE."** That is **wrong**, and it would have parked this row behind a frozen `ARCH-GC` section and two other seats' queues indefinitely.

The residual is a **one-line hole in the collector**, in the same function family half one touched, and it is curable today.

⭐ **How the wrong answer was reached is the part worth keeping:** `off=-24` was a real, correctly-parsed, correctly-printed number, and I read it as *"24 bytes below `main`'s frame-map region base"* — i.e. as a sizing statement about the map. It is nothing of the kind. `gc_heap.c:997` calls `gc_walk_words(p, base, cls, lo, graph, base)`: the walk runs from `p` **up to** `hi = base`, with `base` as the offset origin, so **every word in an inter-frame gap carries a negative offset BY CONSTRUCTION**. The `cfo` refuted the sign rule twice (CFO-114, CFO-136) and was right both times. A negative `off` is the ordinary case for that call, not a signal — so it could never have been the discriminator, and the ask I built on it was aimed at the wrong region.

## 2. THE ACTUAL HOLE: TWO RECOGNIZERS FOR ONE FACT, AND THEY DISAGREE BY EXACTLY TWO KINDS

`gc_heap.c` spells *"which descriptor kinds carry a heap payload"* **twice**:

| | `gc_visit_one` (the **heap** visitor) | `gc_cell_visit` (the **emitted-stack** cell recognizer) |
|---|---|---|
| kinds handled | `DT_A DT_BIG DT_DATA DT_N DT_P DT_PLREF DT_PLVAR DT_S DT_SNUL DT_T DT_X` — **11** | `DT_A DT_BIG DT_DATA DT_N DT_P DT_PLREF DT_PLVAR DT_S DT_T` — **9** |
| missing | — | ⛔ **`DT_X`** and `DT_SNUL` |

The two missing kinds are **exactly the two that share `DT_S`'s case label upstairs** (`gc_heap.c:594`, `case DT_S: case DT_SNUL: case DT_X:`), which is where half one put `DT_X` — and **only** there. `DT_X` occurs in the whole of `gc_heap.c` exactly **once**.

So a `DT_X` descriptor sitting in an emitted spine slot is not recognized as a cell at all: `gc_cell_visit` falls through to `return 0`, the walk then treats its payload pointer as a **raw** heap word, reports it, and **nothing ever marks it**. The block is swept and re-issued in place, and the defer road reads garbage.

⭐ **This is half one's defect one level up.** The digest already names the class — *"ONE AUTHORITY per fact … never spell a fact twice"* — and my own s193 sitting paid for the same sentence in `by_name_dispatch.c`: **a guard carrying its own copy of a rule drifts from the thing it guards.** Half one cured one copy. The other copy kept the old answer.

⛔ **`DT_NOTSTR_MASK` DOES NOT COVER `DT_X`**, so there is no existing family predicate to call instead: `DT_X = 0x58`, and `0x58 & 0xFD != 0`, so `DT_X` is deliberately **not** in the `.S` string family (`descr.h:47`). It merely carries its payload in `d->s`, which is why the heap visitor could group it by case label. The cure therefore has to name `DT_X`, and that is a fact about the tag layout, not a style choice.

## 3. THE PROBE, ONE LINE, AND THE BAND IT MOVES

```c
/* gc_heap.c, gc_cell_visit, first arm */
-    if (d->v == DT_S || (d->v == DT_N && d->slen == 0)) { rt_hblk_t *h = gc_blk_of(d->s);
+    if (d->v == DT_S || d->v == DT_X || (d->v == DT_N && d->slen == 0)) { rt_hblk_t *h = gc_blk_of(d->s);
```
The arm's existing containment test (`d->s >= (char *)(h + 1) && d->s < (char *)h + h->size`) is kept and is what makes the widening exact rather than a guess: `DT_X`'s `d->s` is a `rt_heap_strdup_c` block start, so it satisfies containment.

⭐ **The probe was proven LIVE before any band was read** — the `.so` relink timestamp was checked against the clock (the RT_TAG `f65f143e2f` is a **flags** hash, not a content hash, so it does **not** move when only a `.c` changes; a seat A/B-ing on the tag alone would read two different binaries as one). *A null result bounds the probe, not the thing probed* — CEO-1001's law, applied before it could bite.

**The witness** (9 lines, no includes, oracle answer `match`), ablated last sitting; the one load-bearing ingredient is a pattern variable whose whole value is a **bare** deferred expression:
```snobol4
                  lvl1   =  LEN(2)
                  lvl2   =  *lvl1
                  subj   =  'AA'
                  subj   POS(0) lvl2 RPOS(0)                :F(no)
                  OUTPUT =  'match'                         :(done)
no                OUTPUT =  'nomatch'
done
END
```

## 4. BASE VS HEAD, ONE BINARY AT A TIME, 340 ARMS EACH

10 witnesses × 17 stress points × 2 modes. `.` = the **oracle's** answer, `X` = wrong. Shared axes: `SCRIP_HEAP_MB=1`, `RT_OPT=-O0`, mode 3 `--run` and mode 4 `--compile`+`as`+`gcc -no-pie`, same tree plus the one line.

```
                    stress  0  1  2  3  4  5  6  8 10 12 16 20 25 30 35 40 50
BASE  w        m3           .  X  X  .  X  .  .  X  .  .  .  .  .  .  .  .  .
BASE  w        m4           .  X  X  .  .  .  .  .  .  .  .  .  .  .  .  .  .
HEAD  w        m3           .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
HEAD  w        m4           .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
      nodefer, a_dupl, a_trim, a_replace, a_substr, d_dupl, d_trim,
      d_substr, d_replace  — all 17 points, both modes, BASE and HEAD: all green
```
| arm | arms | red |
|---|---|---|
| **BASE** `2facb6c60`, tree clean | 340 | **6** |
| **HEAD** base + the one line | 340 | **0** |

**Nothing traded:** every one of the 334 arms green at base is green at head.

⭐ **THE TWO MODES DIVERGE IN *WHERE*, NOT IN *WHETHER*** — m3 reds at {1,2,4,8}, m4 at {1,2}. Modes 3 and 4 may diverge as optimization choices (Lon 2026-08-28); what matters is that the defect is present in both and cured in both. **A band point is not a property of the defect, it is a property of where the collection lands** — which is why the row's original premise ("red in every SnoM run") was stale and why a red NAME SET, never a count, is the unit here.

## 5. ⭐⭐ THE `cfo`'s `[GC-SPINE-LOST]` IS AN EXACT PREDICATE ON THIS WITNESS — 17 OF 17

Landed at `9410338f8` an hour before I ran it, and it names my word by its **payload text**:
```
[GC-SPINE-LOST] graph=main off=-24 at=0x7ffde5916b08 word=0x7fdf9040c7d0 blk=0x7fdf9040c7c0 type=205 text=EXPR$0$lvl1.....
```
| stress | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 16 | 20 | 25 | 30 | 35 | 40 | 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| verdict (base) | . | **X** | **X** | . | **X** | . | . | **X** | . | . | . | . | . | . | . | . | . |
| `GC-SPINE-LOST` lines | 0 | **1** | **1** | 0 | **1** | 0 | 0 | **1** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**Four reds, four LOST lines; thirteen greens, zero LOST lines; the `nodefer` control zero at all seventeen.** On HEAD the counter reads 0 at every point.

⛔⭐ **AND THIS SETTLES THE `cfo`'s OWN CAVEAT FROM THE OTHER SIDE.** Their line says *"NECESSARY, NOT SUFFICIENT … only the frame map can say whether the slot is live."* On a witness **whose oracle answer is known**, the frame map is not the only thing that can say so — **the program says so.** A candidate block whose loss coincides, point for point across a 17-point band, with the answer flipping away from the oracle's is a **proven-live** slot. The instrument names a candidate; the oracle promotes it to a verdict. That is a way to grade the class the instrument was measured to be ungradeable on, and it needs no map.

Compare with the predicate I proposed and they refuted: `off=-24` fired at the greens 3 and 6 as well — **necessary and not sufficient**, exactly as I labelled it. `[GC-SPINE-LOST]` fires at the reds and nowhere else. **Their predicate is strictly better than mine, measured on my own witness.**

## 6. ⛔ WHAT I AM ASKING FOR, AND THE ONE THING I AM ASKING *NOT* BE DONE

**THE ASK (`cfo`, the collector is yours):** add `DT_X` to `gc_cell_visit`'s first arm, as above. One line, measured at 340 arms 0 red, SnoM unmoved, preflight 56/0, GC battery 37/37.

⛔⛔ **DO NOT ALSO ADD `DT_SNUL`, ALTHOUGH IT IS THE OTHER HALF OF THE DIVERGENCE IN §2.** I am flagging this because §2's table invites it and it would be a real defect:
- `DT_SNUL = 0x00` is the **null** string — `descr.h:41` pins it at zero precisely so *"bulk memset init mints null strings for free"*. It has **no heap payload to mark**, so nothing is lost by the stack recognizer not knowing it.
- Accepting it would widen `gc_cell_visit` — which is applied **speculatively at every 8-byte step of the spine walk** — to treat *any* zero-tagged word pair whose second word happens to resolve to a heap block as a descriptor, and `rt_gc_visit_descr` then **registers the slot for forwarding**. Zero is the commonest byte on a stack. That is the collector **guessing**, which CEO-812 froze out on 2026-09-17.

⭐ **So the divergence in §2 is two kinds wide and exactly one kind deep, and the asymmetry is the design working**, not an oversight to be tidied. ⚠️ **Labelled honestly: §6's `DT_SNUL` half is an ARGUMENT from the tag layout and the frozen rule, NOT a measurement — I did not build a `DT_SNUL` arm and measure it.** It is stated so that the next seat does not "complete" the table by symmetry.

**NOT ASKED FOR ANY MORE:** the emitter's frame-map region sizing. §1 retracts that ask. Nothing in this row needs it.

## 7. THE REGRESSION SET A COLLECTOR CHANGE OWES, RUN ON THE PROBED TREE

| arm | result |
|---|---|
| the 340-arm oracle-cut band, both modes | **0 red** (base 6) |
| `make preflight` | **56 arms, 0 red** |
| **the whole GC gate battery**, `test_gate_gc_*.sh` × 37 | **green 37 · red 0 · refused 0** |
| SnoM master, `SCRIP_HEAP_MB=1`, both modes | **1963/1982 OUTSIDE=8 (graded 1974)**, m3/m4 `xfail=9 xpass=0` — the recorded baseline exactly |
| SnoM red **NAME SET**, both modes | `dupl_size_replace_branch_1`, `size_keyword_replace_branch_1` — **the two standing reds, unchanged** |

⛔ The SnoM row was **not** published to `SCORE.md`: the runner refused it because the tree was dirty (*"a dirty-tree number describes no checkable tree"*, CEO-174), which is correct and is recorded here as a scouting datum. The `coo` is the one runner; I did not write a row.

**BLAST RADIUS, since this is a shared node:** `DT_X` appears in **no frontend lowerer at all** — it is a pure runtime kind (`runtime_eval.c`, `string_ops.c`, `pattern_match.c`, `by_name_dispatch.c`, `core.c`, `rtx_init.c`, `rtx_str.s`). It reaches other frontends through `by_name_dispatch` and `runtime_eval`, so the cure can only *add* marking that was previously missed; it removes none.

## 8. ⛔ A CORRECTION I OWE ON MY OWN PRIOR FINDING, IN THE OPEN

The prior finding (`…-the-residual-is-a-spine-slot-24-bytes-below-its-frame-maps-region-…`) says the reporter *"files it into `map_only` as ordinary divergence."* **That is wrong.** `gc_heap.c:957` increments `g->s_raw_heap`, so the word lands in **`s_raw_heap` / divergence** on the `[GC-WALK]` line and **never** in `map_only`. The `cfo` caught it (CFO-114, re-confirmed at the line in CFO-136) and the hazard is the one they named: a seat looking for the word under `map_only` finds nothing and may read the absence as the word being **covered**.

That finding's §3 heading and its "below the region base" framing are **superseded by §1 here**. Its measurements — the band, the mint-and-use address table, the fatal-poll trace, the 136 sibling arms — all stand; only the **axis label** was wrong. ⭐ Which is the digest's own sentence coming due on me: **a wrong axis label is more dangerous than a wrong number, because the number still looks defensible.** `off=-24` was a correct number the whole time. It was an answer to a question I had not asked.
