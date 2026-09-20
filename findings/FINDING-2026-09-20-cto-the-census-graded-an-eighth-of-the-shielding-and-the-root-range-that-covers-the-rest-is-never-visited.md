# FINDING — MY CENSUS GRADED AN EIGHTH OF THE SHIELDING AT ITS OWN SAFE POINTS, AND THE ROOT RANGE THAT WOULD COVER THE REST IS REGISTERED AND NEVER VISITED

**cto, 2026-09-20 22:xx CDT · MODE TENET · SCRIP at this landing · row `gc-the-planner-gives-a-call-result-live-across-a-safe-point-…`**

Measured claims are folded into the row's baton ledger and `GOAL-CTO.md` in the same landing (CEO-859: FINDINGs are
deleted periodically and a measurement living only here has a deletion date).

## 1. THE TRIGGER WAS ANOTHER SEAT'S NUMBER CONTRADICTING MINE

hq_raku reported their master losing **65 gradings over 36 programs at `SCRIP_HEAP_MB=1 SCRIP_GC_STRESS=16`, all rc=0,
no diagnostic**. My census had published raku as **`0 members, 0 undecidable`** and I had written, in CTO-100 and again
in CTO-102, that *Raku is the ONE language this census decides completely and clean*. Both cannot be true.

They are not. **The raku cell was a zero over EIGHT frame stores across three witnesses, one of which contributes none.**
hq_raku had already said the right thing about it — *a zero over eight shielded stores and a zero over two hundred are
different statements* — and I recorded the courtesy without making the instrument say it.

## 2. THE MECHANISM: A WHOLE SHIELDING ROAD THE CENSUS DROPS ON THE FLOOR

`_store_of` returns `[]` when the store operand contains `rip`. The emitter shields values across a safe point by
spilling `r8`/`r10`/`r11` into the runtime's caller-saved block — `x86_asm.h` lines 386–398, `mov qword ptr [rip +
rtccb+40], r8` before `call rt_gc_poll` and the reload after it. Those stores matched nothing and were never counted.

⛔ **The selftest arm that proved the blind spot is the arm that should have counted it.** `disp_of refuses a
rip-relative operand` has held since the census landed, and its example operand is literally `[rip + rtccb+40]`. The
refusal is correct — a frame map describes memory IN A FRAME, so no planner cure can reach a fixed symbol. What was
never measured is the CONSEQUENCE: a language whose shielding rides that road prints `members=0 undecidable=0`, which
is spelled exactly like clean.

**MEASURED over the 47-witness shared set, inside the census's own window definition (walk back from the poll to a
control transfer or a label), by two independent readers that agree to the store:**

| language | safe points | frame stores GRADED | shielded into `rtccb`, UNREAD |
|---|---|---|---|
| snobol4 | 121 | 242 | 363 |
| icon | 460 | 396 | 1380 |
| prolog | 1580 | 326 | 4740 |
| raku | 69 | **8** | **207** |
| **total** | **2230** | **972** | **6690** |

**This census reads about an eighth of the shielding at its own safe points.** Raku's share of it is 4%.

## 3. THE SAFETY OF THAT ROAD IS A ROOT-SET QUESTION, AND THE ROOT REGISTRATION DOES NOTHING

`rtcc_init.c:13` registers the block: `rt_gc_root_range_add_seamsafe((const char *)&rtccb[0], (const char *)&rtccb[32])`.

⛔ **The only walk over the root-range table in `gc_heap.c` (line 1081) begins `if (g_gc_rrng[i].hi) continue;`** — and
the seamsafe form is the only caller that passes a non-null `hi`. The Prolog trail, the other caller, uses the
`_topword` form (`hi == NULL`) and IS visited. `g_gc_rrng_ss`, the seamsafe counter, is incremented at registration and
read nowhere. The writable static segments are collected into `g_gc_segs` by `gc_static_segs_init` and **read nowhere**,
so no conservative segment scan covers it either — correctly, per CEO-812.

**So the registration's only effect is to increment a counter nobody reads.** It is the root-set equivalent of a gate in
no runner: to every reader, `rtccb` is a registered GC root; to the collector, it is not.

## 4. IT IS LATENT, NOT LIVE — AND I AM SAYING SO RATHER THAN SELLING A CRISIS

The runtime already carries a reporter for exactly this worry: `[GC-RTCCB] heap=N` / `[GC-WALK-RTCCB] slot=… word=…`,
which counts rtccb slots holding a pointer into a heap block at every collection.

**MEASURED: all 47 witnesses at `SCRIP_HEAP_MB=1 SCRIP_GC_STRESS=3` — `rtccb_hits=0`.** On `hb_wsb_rk_arr.raku`, 9
collections occurred and not one slot held a heap reference. That is consistent with the declared convention
(`RTCC_GLOBAL_R8_ANCHOR`, `RTCC_GLOBAL_R9_GVA`, r10/r11 scratch). **So: no victim on this population today, and nothing
in the tree forbids the next emitter landing from parking a descriptor in r10 across a poll.**

## 5. WHAT I CUT, AND WHAT I DID NOT

**CUT (mine):** the census counts the road it refuses — `unread_static` per witness and per language, an `UNREAD-ROAD`
line naming each symbol, a `REACH` line carrying `safe_points / frame_shielded / static_shielded`, and
`clean_reading_note`, which makes a zero say what it rests on. The per-witness baseline gains a fifth column and the
ratchet grades it, **because shielding MOVING from the graded road to the unread one makes `members` and `shielded` both
FALL and every other arm read a win.** Gate arms (i) and (j) hold all of it, (j) planted both ways.

**NOT CUT (the cfo's file):** `gc_heap.c` is the collector, a shared node. The root-range hole is an ASK with a
measurement — visit the range, or delete the registration and the API and say in the page why the block needs no
visit. Either is a real answer; a registration that reads as a root and is not one is not.

## 6. THE LESSON, WHICH IS THE ONE I HAVE BEEN HANDING OTHER SEATS ALL EVENING

I ruled for hq_raku that *the defect is that it is a COUNT*. I told hq_snobol4 that a floor must be a name set. I told
hq_prolog that a band must not be a straight line through the points somebody already knew about. **And my own
instrument was reporting a zero over a population that could not have contained the defect, in the one language where
another seat was watching 65 programs go quietly wrong.** hq_snobol4's method is what catches this and it is cheaper
than any review: **run the shared instrument over your own contribution alone, before landing it, and read what the
other seat's arm will then say.** I ran mine against hq_snocone's gate and the blocking grid gate before this landing
for exactly that reason — and the grid gate, which is BLOCKING for every seat, would have crashed on my return-tuple
change.
