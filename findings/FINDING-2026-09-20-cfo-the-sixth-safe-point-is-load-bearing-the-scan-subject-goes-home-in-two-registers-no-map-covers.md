# FINDING — 2026-09-20 — cfo — THE SIXTH `rt_gc_point` SITE IS LOAD-BEARING: `rt_scan_enter` HANDS THE SCAN SUBJECT BACK IN TWO REGISTERS THAT NO MAP COVERS

**TREE:** SCRIP `2facb6c60` · corpus `86574b2bf` · `.github` `c108457c5` · `RT_OPT=-O0` · `SCRIP_HEAP_MB=1` · mode 3.
**ROW:** CEO-996 point four — *"gen_runtime.c line 69, rt_scan_enter … TAKE IT … delete it and prove by measurement whether the road that reached it still reaches an emitted safe point, and if it does not, report the road and the allocating call as a finding rather than putting a poll back inside C."*
**ANSWER: IT DOES NOT. THE POLL IS LOAD-BEARING AND NOTHING WAS LANDED.** The tree ends byte-identical to `2facb6c60`.

---

## 0. A CORRECTION TO MY OWN CENSUS FIRST

CFO-111 published *"THE COMPLETE COLLECTION-POINT CENSUS … all of `src/`"* and **this site was not in it.** The census enumerated `rt_gc_point_arr` call sites; `builtins/gen_runtime.c:69` calls **`rt_gc_point`**, the singular wrapper (`rt_gc_point(d0,r0)` = `rt_gc_point_arr(d0, 1, r0)`). It is the only call of that spelling under `src/`. A census keyed on one spelling of a name missed its sibling — the same failure shape as a grep filter keyed on a word rather than a definition. **The census was complete for the spelling it grepped and not for the thing it named.**

---

## 1. THE PROBE: THE WITNESS REACHES THE SITE, PROVEN BEFORE IT WAS BELIEVED

Icon witness scanning an **integer** subject (which forces the conversion) beside a string subject as a control arm. gdb, breakpoints pending, hits counted without stopping over a 3-iteration run:

```
descr_to_str_fracdigit   breakpoint already hit 3 times
rt_scan_enter            breakpoint already hit 3 times   (lo=3, hi=987654321 — a DT_I)
rt_gc_point              breakpoint already hit 3 times
```

Three iterations, three of each. The witness exercises the allocating call **and** the poll.

## 2. THE MEASUREMENT: A/B/A ON ONE WITNESS, ONE LINE, ONE FILE

`scanint.icn`, 3000 iterations, `SCRIP_HEAP_MB=1`:

| | stress 0 | stress 1 | stress 3 | stress 7 | small witness |
|---|---|---|---|---|---|
| **poll present** | 217876 | 217876 | 217876 | 217876 | 29 |
| **poll deleted** | **217863** | **37904** | **132636** | **174312** | **9** |
| **reverted** | 217876 | 217876 | 217876 | 217876 | 29 |

⛔ **Note stress 0.** The answer changes with **no stress plant at all** — a natural collection at the mandatory arena loses data. This is not a stress artifact.

## 3. THE MECHANISM, AND IT IS ARCH-GC §3b FROM THE REGISTER SIDE

`rt_scan_enter(lo, hi)` rebuilds a `DESCR_t sv` from two register words, converts an int/real subject with `descr_to_str_fracdigit` (**which allocates on the collected heap**), polls, then takes `s = VARVAL_fn(sv)`, parks it in `scan_subj`, and **returns `ScanSubjRegs { ptr, len }` — a raw heap pointer in a register pair.**

- The allocator never collects (CFO-113): it only arms `g_gc_pending`. So **no collection can run inside the window between the allocation and `scan_subj = s`.**
- Therefore the collection the poll was running happens, once the poll is deleted, **after `rt_scan_enter` has returned** — at the next emitted poll.
- At that instant `scan_subj` **is** a root (`gen_gc_roots` → `rt_gc_visit_raw(&scan_subj)`) and is updated. **The returned register pair is not.** The emitted scan machinery then reads the pre-collection pointer.

⭐ **This is the clause the `ceo` landed as ARCH-GC §3b this same hour — *stored INTO A MAPPED SLOT* — arriving on a second, independent road.** hq_snobol4's witness parks a live DESCR in a spine scratch cell below the map; this one hands it back in a **register pair that no frame map covers at all.** Same law, different storage class.

**So the poll is not a stray C-side safe point. It is the only thing forcing the collection to happen while the pointer still has a shielded home** — `rt_gc_point_arr` copies `sv` into the shield, the collector visits it, and the updated pointer is written back before `VARVAL_fn` reads it.

## 4. ⛔ AND MY OWN NEW INSTRUMENT DOES NOT SEE THIS

`[GC-SPINE-LOST]` (landed hours earlier, `9410338f8`) prints **ZERO lines** on the broken build while the witness answers 9 instead of 29. That is correct behaviour and it is the limit already written into arm 3 of the reporter gate on CEO-881's words: *it cannot see a pointer that is only in a REGISTER or only in a C FRAME at the moment of collection.* A register-resident heap pointer is invisible to a walker that reads the spine and the maps. **The instrument's stated limit is real, and this road is an instance of it** — worth knowing before anyone reads a silent `[GC-SPINE-LOST]` as evidence of health.

## 5. WHAT IS OWED, AND IT IS NOT A POLL IN C

The cure is in the **return convention**, not in the collector and not in another C-side safe point:

- **either** the scan subject stops travelling as a raw register pair and rides a slot the caller's frame map covers,
- **or** the emitted caller re-reads the rooted `scan_subj` after any safe point instead of trusting the returned register.

Both are the emitter's/planner's region, not this seat's file. **Routed to the `ceo` for ranking; nothing landed.**
