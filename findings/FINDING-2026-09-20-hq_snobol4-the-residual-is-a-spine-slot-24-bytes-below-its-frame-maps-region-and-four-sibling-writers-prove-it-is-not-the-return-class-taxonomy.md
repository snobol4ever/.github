# THE RESIDUAL IS A SPINE SLOT 24 BYTES BELOW ITS FRAME MAP'S REGION — AND FOUR SIBLING WRITERS PROVE IT IS NOT THE RETURN-CLASS TAXONOMY

`hq_snobol4`, 2026-09-20, row `snobol4-the-pattern-replacement-class-prints-a-wrong-answer-under-collection-and-changes-its-fingerprint-per-poll-set` (CEO-979, GC-only order).
Answers the `cfo`'s question in CFO-124: *"whether any of the four flips when a DIFFERENT out-parameter writer is on the path, because that would tell us whether one entry or the whole class is implicated."*

**TREE OF EVERY NUMBER BELOW:** SCRIP `ac1970678` (plain `origin/main`, `merge --ff-only`, **DT_X cure `9c17f8c4a` is an ancestor**) · corpus `86574b2bf` · `.github` `da849247` · `RT_OPT=-O0` · RT_TAG `f65f143e2f` · `SCRIP_HEAP_MB=1 SCRIP_HEAP_MAX_MB=512`, mode 3.
⛔ **NOTHING IS LANDED IN SCRIP.** Every probe quoted here was reverted; `git status` is empty and `make preflight` reads **56 arms, 0 red** on the restored tree. The sites named are the collector and the emitter's frame maps — shared nodes, so this is an ASK with the measurement.
⭐ Supersedes nothing in [FINDING-…-a-dt-x-name-string-is-collected…] except its section 4(b) *reading*: the hole is real, but it is **not** where 4(b) guessed.

## 1. THE BAND REPRODUCES, AND THE RESIDUAL IS THE SAME WORD

Witness as published in the prior finding (9 lines, no includes). **The oracle's answer is `match`** (`/home/resources/x64/bin/sbl -bf`, rc=0) — cut from the oracle, not from our stress-0 run.

`.` = oracle's answer, `X` = wrong answer (`nomatch`):

```
stress   0  1  2  3  4  5  6  8 10 12 16 20 25 30 35 40 50
base.sno .  X  X  .  X  .  .  X  .  .  .  .  .  .  .  .  .
```
The `cfo`'s cure column at CFO-124 reproduces **exactly** — reds at 1, 2, 4, 8; the two points DT_X bought (3 and 6) stay bought.

⭐ **The four residual reds are the SAME lost word, not a second defect.** Ordered probe at mint and at use, on the **cured** binary:

| stress | minted `xd.s` | read at use | verdict |
|---|---|---|---|
| 0 | `…c7d0` | `"EXPR$0$lvl1"` | match |
| 1 | `…c7d0` | `20c8…0058000000` | **nomatch** |
| 2 | `…c7d0` | `20c8…0058000000` | **nomatch** |
| 3 | `…c7d0` | `"EXPR$0$lvl1"` | match |
| 4 | `…c7d0` | `20c8…0058000000` | **nomatch** |
| 6 | `…c7d0` | `"EXPR$0$lvl1"` | match |
| 8 | `…c7d0` | `20c8…0058000000` | **nomatch** |

Two facts fall out of that table and both matter:
- ⭐ **The address is IDENTICAL at mint and at use in all seven readings.** The block is **reclaimed and re-issued in place — never relocated.** So this is not "visited but its slot unregistered"; the descriptor is **never visited at all**.
- The trailing `58 00 00 00` of the re-issued block is `DT_X = 0x58` itself, the arena handing the block back as a `DESCR_t`.

⛔ **Collection COUNT does not decide the verdict.** stress 2 → 4 collections → FAIL. stress 3 → 4 collections → PASS. A same-count pair with opposite verdicts is a sharper statement than non-monotonicity: it is *which* collection lands *where*, exactly as the `cfo` read it.

## 2. THE FATAL COLLECTION, NAMED TO THE INSTRUCTION

The emitted window at the `SNO$MKEXPR` call (`--compile`, `.Lcall_α_76_240`):
```asm
        call      rt_call_arr_bl@PLT          # mints DT_X, returns it in rax:rdx
        add       rsp, 16
        cmp       al, 104;  jne .Lcall_α_76_240
.Lcall_α_76_240:
        mov       qword ptr [rsp + 0], rax    # <-- the result IS stored, to the spine slot
        mov       qword ptr [rsp + 8], rdx
        call      rt_gc_poll@PLT              # <-- THE FATAL SAFE POINT
        jmp       n23_assign_α                # <-- only HERE does it reach lvl2's home
```
⭐ **The poll obeys ARCH-GC section 3 to the letter — it is after the result is stored.** The defect is that the slot it was stored *to* is not a place the collector looks.

Interleaved probe, stress 1 (RED) against stress 3 (GREEN), same binary:

```
stress 1                                     stress 3
[MKEXPR] xd.s=0x…c7d0                        [MKEXPR] xd.s=0x…c7d0
[SP] rt_gc_poll floor=0x…19f7                [SP] point_arr_c arr=0x…a00 n=1 floor=0x…a10
[SP] point_arr_c arr=(nil) n=0  <-- NO SHIELD   [VISIT-DT_X] d=0x70001010  str="EXPR$0$lvl1"
[ZGC-MARK] regeneration #3 done <-- 0 DT_X      [VISIT-DT_X] d=0x…c7f8     str="EXPR$0$lvl1"
   VISITED, BLOCK SWEPT                         [VISIT-DT_X] d=0x…a00      str="EXPR$0$lvl1"
[VISIT-DT_X] … str=" ..."  <-- already dead  [ZGC-MARK] regeneration #3 done
[USE-DT_X] garbage -> nomatch                [USE-DT_X] "EXPR$0$lvl1" -> match
```
At stress 3 no collection lands inside the window, so by the time one runs the descriptor is in **three** homes (a standing cell, a heap cell, and the shield array) and is marked. At stress 1 a collection lands **inside** the window, finds the descriptor in **none** of them, and sweeps it. `rt_gc_poll` passes `arr = NULL, n = 0` — at the one safe point where a freshly minted descriptor is live in the spine and nowhere else, **the shield is empty.**

## 3. ⭐⛔ THE WORD IS 24 BYTES BELOW ITS FRAME MAP'S REGION — AND THE INSTRUMENT ALREADY PRINTS IT

`SCRIP_GC_MAPS=1`, the sanctioned reporter, on the **unpatched** tree at stress 1:
```
[GC-WALK-SPINE] pop=cstack graph=main off=-24 at=0x7fff6e1db8b8 word=0x74ee2fe0c7d0 blk=0x74ee2fe0c7c0 type=215
```
`word=0x…c7d0` **is the DT_X name string.** `off=-24` is **negative** — the spine slot holding it sits 24 bytes **below** `main`'s frame-map region base (`map_off` = 416 for this graph; `gc_frame_map.h`: *"map_off is the cell's offset from the frame's region base … the walker finds the region as cell − map_off"*). The map-driven walk visits `GC_LAY_DESCR` cells **inside** the region, so a cell below the region base is never visited. The block is unmarked, swept, and re-issued.

⛔ **The reporter sees the lost word and nothing acts on it.** `[GC-WALK-SPINE]` with a negative `off` is exactly the divergence line this class needs, and it is counted into `map_only` rather than raised.

Correlation across the band, unpatched tree:

| stress | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 |
|---|---|---|---|---|---|---|---|---|---|
| verdict | match | **nomatch** | **nomatch** | match | **nomatch** | match | match | **nomatch** | match |
| `GC-WALK-SPINE` lines | 0 | 2 | 2 | 1 | 1 | 0 | 1 | 1 | 0 |
| `off` | — | −24 | −24 | −24 | −24 | — | −24 | −24 | — |

Every red has an out-of-map word. So do the greens at 3 and 6. So do none of the greens at 0, 5 and 10.

⭐ **`off=-24` is NECESSARY AND NOT SUFFICIENT, and I am labelling it as exactly that** (the same discipline the DT_X case earned): the out-of-map word appears at **every** collection that lands while the spine slot is live, red or green. It is **fatal precisely when no mapped home holds the descriptor yet** — which is the stress-1-versus-stress-3 trace in section 2. Every red has it; two greens have it too.

## 4. ⭐⭐ THE `cfo`'s QUESTION, ANSWERED: ONE ENTRY'S WINDOW, NOT THE RETURN-CLASS TAXONOMY

Eight sibling witnesses over **four other out-parameter writers** from the `cfo`'s own 51-entry candidate set — `bn_dupl`, `bn_trim`, `bn_substr`, `bn_replace` — in **both** shapes: the deferred-expression road (`*DUPL('A',2)`) and the plain assignment road (`s = DUPL('AB',2)`). **Every expected answer is oracle-cut** (`sbl -bf`).

```
stress        0  1  2  3  4  5  6  8 10 12 16 20 25 30 35 40 50
a_dupl.sno    .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
a_trim.sno    .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
a_substr.sno  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
a_replace.sno .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
d_dupl.sno    .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
d_trim.sno    .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
d_substr.sno  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
d_replace.sno .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .
nodefer.sno   .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .   (control: no deferred expression)
```
**136 arms, zero red.** And the negative is worth something only because **the confounds are closed one at a time:**

| | `SNO$MKEXPR` | `bn_dupl` / `bn_trim` / `bn_substr` / `bn_replace` |
|---|---|---|
| writes its DESCR through an `out` pointer arg | yes | **yes** — all four are in the `cfo`'s 51 |
| the `out` local that receives it | `rt_call_arr_impl`'s, unrooted | **the same one**, unrooted |
| allocator | `rt_heap_strdup_c` → collected heap | `rt_heap_alloc_c` → **the same collected heap** |
| emitted window | `call` → `mov [rsp+0], rax` → `call rt_gc_poll` → `jmp assign` | **byte-identical shape** (`.Lcall_α_27_240`) |
| `GC-WALK-SPINE` out-of-map words, stress 1..8 | **8** | **0, 0, 0, 0, 0** |

⛔⭐ **SO THE ANSWER IS: ONE ENTRY'S WINDOW, NOT THE CLASS.** Four other members of the 51 share the unrooted `out`, the allocator, and a byte-identical emitted window, and none of them loses a value. The discriminator is not *who writes through a pointer argument* — it is **whether this graph's spine slot for the call result falls inside its frame map's region.** For `main` in the witness it does not (`off=-24`); for `main` in all four siblings it does.

⛔ **THE TAXONOMY GAP IS STILL REAL — IT IS JUST NOT WHAT IS KILLING THIS ENTRY.** CFO-123 should stand or fall on its own merits; this witness is **not** evidence for it, and I would rather say so than let my row be cited as its first proof. By the time the fatal collection runs, `out` is already dead: the value lives in the emitted spine slot and in `rax:rdx`, not in the callee's argument.

## 5. WHAT I AM ASKING FOR

Both remaining sites are shared nodes and neither is SNOBOL4's:
- **(a) the emitter's frame-map sizing** — `main`'s declared region for this graph does not cover the spine depth the call-result store reaches, so a live `GC_LAY_DESCR` cell sits at `off=-24`. `ARCH-GC-COMPILE-TIME-FRAME-MAPS.md` §7 is FROZEN and this is the `cto`'s/`ceo`'s region. **Who sizes it, and is a negative `off` a map defect or a missing region?**
- **(b) the reporter should refuse, not count.** `[GC-WALK-SPINE]` with `off < 0` is a live descriptor cell outside every map. Today it lands in `map_only` and reads as ordinary divergence. A negative `off` at a cell whose word is a heap block is the collector guessing nothing and *finding* something — it deserves a loud line at minimum.

⛔ **I did NOT wire the witness into the GC battery this sitting, on purpose.** It is red at four band points until (a) lands, and `make test` is already carrying the `coo`'s nineteen blocking arms; adding a knowingly-red arm ahead of its cure buys nothing and costs every seat. The witness and its eight oracle-graded siblings are held ready and go in **with** the cure, in one landing, as `test_gate_orphaned_witnesses_do_not_grow.sh` requires.

## 6. THE INSTRUMENT LESSON THIS SITTING PAID FOR

⭐ **A negative offset is a well-formed answer to the wrong question.** `off=-24` parsed, printed, aligned and totalled correctly in the `map_only` column for as long as this defect has existed. The reporter was not broken and was not silent — it was *counting* the lost word into a bucket that means "the map and the sniff disagree", which is exactly what a reader skims past. The lesson is the one already in the digest, wearing new clothes: **readable and wrong is the shape a parse check can never catch** — and a divergence counter is a parse check that has learned to add up.

## APPENDIX — THE NINE SIBLING WITNESSES, VERBATIM

Held for the landing that carries the cure. Each is graded against `sbl -bf` in the same run; the expected answer beside it is the **oracle's**, never ours.

```snobol4
* a_dupl.sno      oracle: ABAB          * a_trim.sno      oracle: AB
                  s    =  DUPL('AB',2)                    s    =  TRIM('AB  ')
                  OUTPUT =  s                             OUTPUT =  s
END                                     END

* a_replace.sno   oracle: ABAB          * a_substr.sno    oracle: AB
                  s    =  REPLACE('ABCD','CD','AB')       s    =  SUBSTR('ZABZ',2,2)
                  OUTPUT =  s                             OUTPUT =  s
END                                     END
```
The four deferred-road siblings share one shape; only the call inside `*(...)` changes. All four read `match` from the oracle:
```snobol4
                  subj   =  'AA'
                  subj   POS(0) *DUPL('A',2) RPOS(0)        :F(no)
                  OUTPUT =  'match'                         :(done)
no                OUTPUT =  'nomatch'
done
END
```
`d_trim` substitutes `*TRIM('AA  ')`, `d_substr` `*SUBSTR('ZAAZ',2,2)`, `d_replace` `*REPLACE('BB','B','A')`.

The control, `nodefer.sno` (oracle `match`) — the witness with the one load-bearing ingredient removed, `lvl2 = lvl1` in place of `lvl2 = *lvl1`:
```snobol4
                  lvl1   =  LEN(2)
                  lvl2   =  lvl1
                  subj   =  'AA'
                  subj   POS(0) lvl2 RPOS(0)                :F(no)
                  OUTPUT =  'match'                         :(done)
no                OUTPUT =  'nomatch'
done
END
```

The band walker, so the numbers above are re-runnable rather than quotable:
```bash
for N in 0 1 2 3 4 5 6 8 10 12 16 20 25 30 35 40 50; do
  SCRIP_HEAP_MB=1 SCRIP_HEAP_MAX_MB=512 SCRIP_GC_STRESS=$N timeout 20 ./scrip w.sno < /dev/null
done
```
