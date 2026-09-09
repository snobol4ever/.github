# FINDING (hq_V, 2026-09-09 18:0x CDT) — the eleven Icon-master reds are SEVEN roots, two of them two-for-one; every one of the eleven refs is ORACLE-FAITHFUL; and the board's drift warning is a FALSE ALARM that fires on every green run

**Tree:** SCRIP `d4d19848c` · corpus `cecd7ef2b` · binary built 17:53 CDT after the merge (HQV-15's standing rule: merge, rebuild, THEN measure). **Board this tree:** IcnM **740/751** both modes, m3 740 / m4 740, entries=904, watermarks re-pinned 740/740 (`.github` `819a56a6`). 739 → 740 came from the fleet's `f ! record` landing (`d4d19848c`), not from this seat.

## 1. EVERY REF IN THE RED SET IS ORACLE-FAITHFUL — the eleven reds are all genuinely OURS

All eleven red entries were re-probed against Arizona `icont` 9.5.25a on this tree, extracted from the master by banner and run standalone. **Nine matched their stored ref immediately. The two that did not were BOTH artifacts of my own probe, not defects of the master**, and both were retracted before they were reported:

- `procedure_write_265` — I captured `2>&1`; `&trace` output goes to **stderr**, and the master grades **stdout**. Captured stdout-only the oracle is `A:end`, byte-identical to the stored ref.
- `procedure_record_every_replace_12` — my banner-splitter did `.strip('\n')`, which ate a **leading blank line** that the stored ref genuinely carries (Icon's error report opens with one). Read unstripped from `ALL.ref`, the stored ref is byte-identical to the oracle's 533 lines.

⛔ **This is worth writing down because I nearly filed two false ref defects against the master on announcement eve**, and the master pair is the one artifact this seat is the sole writer of. A probe method that merges streams or normalises whitespace is not measuring the thing the grader measures. The rule from here: **probe the way the grader runs — stdout only, no normalisation — or the divergence you find is your own.**

**The certification that matters for the fleet:** there is **no false red** in the current Icon master red set. Every one of the eleven is a real divergence from the oracle, so no seat's cure time is about to be spent on a wrong ref.

## 2. ELEVEN REDS, SEVEN ROOTS — and two roots are worth two reds each

Every one of the eleven is red in **both** m3 and m4, with the identical divergence in each. That uniformity is itself the finding: **not one of these is a codegen defect**; all seven roots sit in the front end or in lowering.

| root | reds it accounts for | first divergence |
|---|---|---|
| **`copy()` of a RECORD mints no new serial** | `procedure_write_257`, `procedure_record_every_replace_14` | `copy(r(1))` reads `r_1`, oracle `r_2`; counter then permanently one behind |
| **element generation over a set concurrent with deletion loses every second element** | `procedure_write_258`, `procedure_every_scan_replace_13` | 40-element set generates 20 (`A:20 B:20`); the other entry names the lost ones: `not generated: 34 35 38 39 41` |
| nested reversible exchange | `procedure_every_alt_replace_12`, `procedure_record_every_replace_13` | `(x<->y):=:z` leaves no net inner swap; unparenthesised form kills the procedure (already diagnosed in the entry itself) |
| integer coercion (hq_U's named class) | `procedure_write_256` | `image(seq("a")\|"converted")` reads `0`, oracle `"converted"` |
| `&trace` SIGSEGV (hq_U's tracer class) | `procedure_write_265` | rc=139 under `&trace := -1` |
| `loadfunc` | `procedure_write_254` | rc=1, no output at all |
| `break` as a value | `procedure_write_266` | `image(every break)` and the following line print nothing |

**Two roots are worth two reds each, so four of the eleven reds are two cures.** The two-for-one roots are also the two cheapest to state, which is why they were probed first.

## 3. THE TWO PROBES, MINTED BEFORE ANY CURE (corpus `82f4d259a`)

Both refs **cut from `icont` 9.5.25a on this tree, never from our own output**; both RED ON ARRIVAL in **both** modes; each carries its control arm INSIDE the file, which is what makes it a probe rather than a witness.

- **`copy_of_a_record_mints_a_new_serial_number.icn`** — the oracle mints a serial at allocation and `copy()` allocates, so `copy(r(1))` is `r_2` and the next constructor is `r_3`. Ours returns the **source's** serial and mints nothing. ⭐ **The control arm decides the size of the cure:** D–I copy a **list, a set and a table** and **all six agree with the oracle**. So `copy()` is sound, the serial counter is sound, and the fault is in the **record path of `copy()` alone** — one box. A cure aimed at the shared serial mechanism is aimed at the wrong node, and D–I will catch it.
- **`deleting_during_element_generation_over_a_set_still_visits_every_element.icn`** — the oracle visits all ten and ends empty; we visit **exactly half** and half survive. The halving is the diagnosis: not a lost element here and there but a **stride of two**, the shape of a cursor advancing by one while the collection shifts by one underneath it. ⭐ **Control arm inside the file:** the same generation with **no** deletion reads 10/10 in both modes, so `!set` is sound and the fault is in **generation concurrent with mutation**.

Neither probe is absorbed into the master pair by that landing, so **no board and no denominator moved** — see §5.

## 4. ⛔ THE BOARD'S DRIFT WARNING IS A FALSE ALARM, AND IT FIRES ON EVERY GREEN RUN

`board_icon_master.sh` prints, on this and every recent run:

> ⚠️ NOTE: harness graded 904 entries but ALL.csv carries 905 rows — the suite file and its provenance index disagree.

**Nothing has drifted.** Measured: `ALL.icn` carries **905** banner markers, `ALL.ref` **905**, `ALL.csv` **905** rows, and the three name-sets are **identical** (zero-line `diff`, no duplicates). The modes column is exactly `752 m3,m4 + 153 ast = 905`.

The gap is **one entry, `procedure_every_alt_replace_4`**, removed from the graded denominator by the **CEO-390/391 outside-baseline ruling** (Arizona `icont` refuses to compile it — *"Line 76 # }: invalid case clause"*), recorded in `ALL.outside.tsv` with the oracle's own words, and **printed by name with its reason on every single run** as `OUTSIDE_BASELINE`. The harness is behaving exactly as ruled.

The defect is in the check: it compares `graded` against `CSV_ENTRIES` **without subtracting the outside-baseline count**, so a ruled, recorded, deliberately-removed entry is reported as a suite/index disagreement. The harness already prints `OUTSIDE_BASELINE_COUNT` for the board to read.

⛔ **Why this is not cosmetic:** it is a warning that is **permanently true and permanently meaningless**, sitting one line above the numbers Lon reads on the eve of the announcement, and it trains every reader to scroll past the one check whose entire job is to catch a real silent-orphan shrink. A check that cries wolf on every green run has been disabled by its own output. **Owner: hq_T (the instruments).** Not touched by this seat — reported with the measurement rather than fixed in another seat's lane.

## 5. THE ABSORPTION QUESTION, NAMED RATHER THAN TAKEN

CEO-452 makes this seat the **one writer** of the master pair, and the lane's own precedent absorbs red-on-arrival probes (`daf298638`, three of them). Absorbing these two would take the board **740/751 → 740/753**: two more true, curable reds inside the denominator, and a **percentage that reads lower on 09-10**. That is the exact shape this seat flagged at HQV-1 — a criterion change rendered to a reader as lost ground. The numbers would be true either way; only the reading changes. **Asked of the ceo, not decided here**, and the probes are already on origin and usable by their owning seats regardless of the answer.
