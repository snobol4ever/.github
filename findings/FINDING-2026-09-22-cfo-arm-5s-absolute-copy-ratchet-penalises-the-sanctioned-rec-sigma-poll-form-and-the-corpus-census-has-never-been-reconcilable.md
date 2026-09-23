# FINDING 2026-09-22 (cfo, 22:3x–23:0x CDT, `date`-read) — ARM 5's ABSOLUTE COPY RATCHET PENALISES THE SANCTIONED POLL FORM, AND THE CORPUS CENSUS HAS NEVER BEEN RECONCILABLE

MODE DECTET. Trees: SCRIP `4a1cecc84` (measured) → `7a55e21d1` (the arm-4 landing of this sitting). Instrument: `scripts/util_gc_callee_saved_census.py`, selftest 14/14 green at both ends.

⛔ **Lon deletes FINDING files periodically. Every measured claim below is also in `GOAL-CFO.md` CFO-148 and in the `gc-rt-c-...-except-the-original-invocation` baton's `## NEXT`, which are the durable copies.**

## 1. A BLOCKING ARM IS RED ON origin/main AND NOBODY HAD ROWED IT

`test_gate_gc_a_callee_saved_register_at_an_allocating_return_is_named_not_assumed.sh` **arm 5: copy residual 293 against `COPY_CEILING` 289**, rc=1. Blocking: `Makefile:409` is a tab-`b` recipe and the gate is in `run_blocking_set.sh --list`. HEAD == origin/main == `4a1cecc84`, tree clean. So every one of the ten seats reading `make test` was getting rc=1 on it.

The gate's sibling, `test_gate_gc_the_spill_record_carries_a_callee_saved_heap_pointer_across_an_allocating_return.sh`, is **green** — arm 3 there is coverage over the census's *heap* class, which did not move.

## 2. THE COUNT HID TWO OPPOSITE MOVES; ONLY A NAME SET SHOWED THEM

Per-file copy residual, the census's own `COPY <file> total=N: <graph>=n …` attribution, ceiling tree against today:

| witness | at the 289 ceiling | today | Δ |
|---|---|---|---|
| `w.pas.s` | 13 | **24** | **+11** |
| `w.icn.s` | 36 | **29** | **−7** |
| `w.defer.sno.s` | 166 | 166 | 0 |
| `w.sno.s` | 43 | 43 | 0 |
| `w.pl.s` | 22 | 22 | 0 |
| `w.raku.s` | 5 | 5 | 0 |
| `w.reb.s` | 2 | 2 | 0 |
| `w.sc.s` | 2 | 2 | 0 |

⛔ **The net `+4` is an eleven-reading regression partly masked by a seven-reading improvement.** That is MODE line 2's own rule — *a count cannot tell two readings apart and a name set can* — landing on a live blocking arm rather than in a memo.

⭐ **THE ALLOCATING SET IS NOT THE CAUSE, AND THE 2×2 SAYS SO RATHER THAN AN ARGUMENT.** Three cells, the census's allocating set derived from each tree's own `libscrip_rt.so`:

- OLD `.s` × OLD allocating set → `sites=612 raw=372 copies=289 heap=6` — **reproduces the recorded ceiling exactly**
- OLD `.s` × TODAY's allocating set → **byte-identical** to the above
- TODAY's `.s` × TODAY's allocating set → `sites=618 raw=366 copies=293 heap=6`

So the whole move is in **today's emitted code**, not in the derivation.

## 3. ISOLATED, THEN ATTRIBUTED, THEN READ OFF THE EMITTED CODE

`w.pas` alone, both trees: **`sites=18 raw=13 heap=0 unclassified=0 graphs=12` identical**. The entire `+11` is one register:

```
r13  CEILING: live_across=16/18 owned=0  passed_through=16   owned_def_classes: -
r13  TODAY:   live_across=16/18 owned=11 passed_through=5    owned_def_classes: CELL=11
```

r13 is the one callee-saved register ARCH-GC § 6.5 names as able to hold a collected-heap pointer (the subject base).

**Bisect: `2344d2dc7` first bad** — 8 steps, **3m26 wall / 20m44 user** at load ~8, with the **instrument pinned to today's census script** and only the tree moving. That commit is **CTO-126**: ten of the ceo's twelve rejected sites taking `rec_sigma`, including `bb_binop_relop` ×2 and `bb_binop_relop_val` ×4 — and the Pascal witness is all binops.

⭐ **THE MECHANISM, READ OFF `w.pas.s` RATHER THAN INFERRED FROM THE BISECT.** The eleven readings *are* the spill record doing exactly what the design says:

```
sub   rsp, 32
mov   dword ptr [rsp + 0], 2          ; the DESCR tag
mov   dword ptr [rsp + 4], r15d       ; the length half
mov   qword ptr [rsp + 8], r13        ; THE SUBJECT POINTER, spilled as a tagged cell
mov   qword ptr [rsp + 16], rax       ; the relop int result, below the floor
lea   rdi, [rsp + 0]                  ; shield array
mov   esi, 1                          ; one cell
mov   edx, 0                          ; r0 = NULL
lea   rcx, [rsp + 32]                 ; THE FLOOR the record opened at
call  rt_gc_point_arr_c@PLT
...
mov   r13, qword ptr [rsp + 8]        ; <-- the census reads THIS as CELL
add   rsp, 32
```

⛔⛔ **SO ARM 5 RATCHETS AGAINST THE SANCTIONED POLL FORM.** `rt_gc_point_arr_c` visits that array with `rt_gc_visit_descr` and rewrites `[rsp+8]` if the block moved, so the reload yields a **repaired** pointer — yet the census classifies it `CELL` = *a copy of something else*, its hazard bucket. **CTO-126 is correct and must not be reverted; the ratchet's shape is the defect.** With safe points at **196 of 253** and 57 to go, every further `rec_sigma` conversion raises the number arm 5 holds, and each recurrence invites the one thing the ceiling's own header forbids — *raising it to fit*.

The Icon `−7` is not lost work: `w.icn` sites stay **29** while `raw` falls 35 → 26 and copies 36 → 29, i.e. sixteen readings moved from `owned` to `passed_through` — a real ownership improvement that happened to mask Pascal.

## 4. A SECOND, SEPARATE DEFECT IN THE SAME FILE: THE CORPUS CENSUS REFUSES, AND ALWAYS HAS

`util_gc_callee_saved_census.py --corpus` over 76 files (103 s) prints its own **INSTRUMENT REFUSAL and exits rc=2**:

```
SUMMARY sites=11232 raw=10327 copies=11995 heap=13 unclassified=1732 bucket_unclassified=2021 …
```

The gap is **exactly the `CELL:…:UNCLASSIFIED` readings**: r13 `32+81+97` + r14 `36+43` = **289**. `census()` files them in the COPY list because the leading form is a `CELL`, while `bucket()` peels every `CELL:` prefix and matches the `UNCLASSIFIED` tail — so they are in **neither blocking arm**, which is the residual-behind-a-green-gate shape the refusal text itself names.

⛔ **THE 289 HERE AND THE 289 CEILING ARE TWO UNRELATED QUANTITIES.** Stated before anyone conflates them.

⛔ **It has never been reconcilable.** Both wired gates run only the 8-witness population, where `unclassified=0` and the two routes therefore agree trivially. The corpus has never been graded, so the 09-19 `bucket()` cure could not have exposed this.

## 5. STEP 4'S DENOMINATOR, WHICH THE BATON REQUIRED BEFORE THE WORK STARTS

CEO-973's named-raw table is **site-class → word → reason**, census-read, undeclared site RED, `rbx` excluded by name (CEO-959). Sized:

- **hermetic gate population: 293 copy readings over 68 graphs**, attributed by file above; `defer.sno` 166 is the single largest block
- **corpus population: 11995 copy readings** over 11232 allocating call sites in 7572 graphs, 76 files
- **rows, which is the real cost:** the table is keyed on *class*, not reading. Today's copy classes across the corpus are `CELL`, `POP`, `REG`, `ARITH` and their `CELL:`-composed forms plus `CELL:CALLERS` — so the first table is **single digits of rows, not 293 and not 11995**. CEO-973's "166 copy sites" is not a corpus figure: it is the `w.defer.sno` share of the 289, from this gate's own header at line 113.

⭐ **AND THE RED WROTE THE TABLE'S FIRST ROW.** site-class = *a reload out of the poll's own tagged spill record*; word = r13/r15; reason = *the poll visited that cell as a DESCR through its shield array and rewrote it if the block moved, so the reload yields a repaired pointer, not a stale one*. It must be verified **mechanically** — the source cell inside the array handed to *that* poll, no intervening write, the record below the declared floor — and never by trusting the class name, which is the census's own standing rule.

## 6. BOARD COST (cfo, `date`-read, load stated with every figure)

| measurement | cost |
|---|---|
| cold worktree build, `-j8`, load 6–8 | **33 s wall / 3m50 user** — far cheaper than the 7 min the seat digest quotes for a `core.h` touch |
| incremental `make` after a merge of 39 files | 2.9 s |
| `--corpus` census, 76 files | 103 s |
| 8-witness census | < 2 s |
| bisect, 8 steps, load ~8 | 3m26 wall / 20m44 user |
| `a_board_can_say` gate | 1.8 s |
| `make preflight` | 59 arms, 1 red, **18 s** |

## 7. TWO PROCESS NOTES, SELF-REPORTED

1. I read `rc=$?` **after a pipeline ending in `tail`** and recorded the corpus census as rc=0 when it was rc=2 — my own memory, violated inside the hour. The refusal was visible in the text and the rc was not; the text is what caught it.
2. I piped a **bus verb** (`s4e_msg.sh board`) through `grep | cut | head`. `head` closed the pipe, the verb wedged at 0.0% CPU, and **it held the `cfo` identity lock for 741 s** — my next `send` was refused with `ANOTHER LIVE PROCESS ALREADY HOLDS THE IDENTITY cfo`. This is stronger than the pipe rule I already carry: a bus verb holds the lock for its whole run, so piping one into a short read can lock the seat out of its own inbox.
