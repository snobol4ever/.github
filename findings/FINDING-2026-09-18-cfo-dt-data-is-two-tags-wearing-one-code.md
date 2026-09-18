# FINDING — `DT_DATA` IS TWO TAGS WEARING ONE CODE, AND NOTHING IN THE DESCRIPTOR TELLS THEM APART

**cfo, 2026-09-18. Status: CONFIRMED, with a crash witness and a bisection. Blocks F6 step 5's descriptor-array typing.**
**Claims duplicated (Lon deletes FINDINGs; RULES.md line 31):** baton
`gc-the-collector-walks-the-rbp-chain-...` § LEDGER, and `GOAL-CFO.md` CFO-98/99. If this file is gone, those hold.

## THE CLAIM

The frozen design says everything is a DESCR and **its type field is the only tag**
(`ARCH-GC-COMPILE-TIME-FRAME-MAPS.md`, RULES.md THE COLLECTOR GUESSES NOTHING). On the heap, today,
**that is false for `DT_DATA`**, which carries two unrelated things:

1. a `DATINST_t *` — a real data-type instance, and
2. a raw `DESCR_t *` element array — an Icon list's `frame_elems`.

`gc_visit_one`'s `DT_DATA` case takes `d->u` as a `DATINST_t *` and reads `u->type` and `u->fields`.
Handed form (2) it reads those offsets out of a descriptor array.

## THE EVIDENCE

An Icon list is a four-field data type — `DEFDAT_fn("list(frame_elems,frame_size,gen_type,frame_cap)")`
(`string_ops.c:27`, `pattern_match.c:408`).

**Writers of form (2):** `pattern_match.c:414` `rptr.v=DT_DATA; rptr.slen=0; rptr.ptr=(void*)rbuf;` ·
`by_name_dispatch.c:5293` `eptr.v=DT_DATA; eptr.slen=0; eptr.ptr=(void*)elems;` · `by_name_dispatch.c:7111`.

**Readers of form (2):** `rt_runtime.c:235`, `pattern_match.c:32`, `by_name_dispatch.c:1167` and `:5956`,
all spelling the same test: `(ea.v == DT_DATA) ? (DESCR_t *)ea.ptr : NULL`.

**Writers of form (1):** `core.c:1782` `r.v = DT_DATA; r.slen = 0; r.u = inst;` · `core.c:2026` · `core.c:3007` ·
`by_name_dispatch.c:7126` `d.v = DT_DATA; d.slen = 0; d.u = nu;`.

⛔ **`slen` cannot discriminate them** — checked because it was the obvious escape. Both forms set `slen = 0`.
The two are **indistinguishable from the descriptor alone**. Only the owner's knowledge separates them, and
`gc_visit_datinst` already carries that knowledge as a `strcmp(u->type->fields[0], "frame_elems")` special case.

## HOW IT WAS MEASURED

Converting all 49 descriptor-array sites to a typed `HB_DVEC` kind segfaults an Icon list-and-table witness at
every stress level from 1. Attributed: origin clean at every level. **Bisected to one variable** — the same 49
call-site edits with the kind stamped `HB_WS` are green, so the edits are correct and the fault is in walking
the blocks *by type*.

Instrument rather than bisection: `SCRIP_GC_DVEC_AUDIT=1` makes the descriptor-array visitor **report** a cell it
would have dereferenced wrongly instead of dereferencing it. Under it the witness completes rc=0, and **every
dangerous cell is in an 80-byte block of exactly four descriptors with tags `0x02` and `0x70`** — `0x70` is
`DT_DATA`, and four is the list type's field count.

## WHY THE OLD CODE SURVIVED IT

The conservative sniff **validated** each pointer against the heap (`gc_block_exact`) before visiting, and a
`frame_elems` carrier's target does not match. A typed walk has no such step **by design** — that is the point
of it. So this defect could only appear when the heap started being walked by type.

## ⛔ THE CONSEQUENCE

Two statements cannot both hold: *the tag is the only discriminator* and *the tag is ambiguous*. Step 5's
descriptor-array typing cannot be completed while form (2) exists, because **any** blind typed walk over a
list's field array repeats the crash.

## THE CURE (the ceo's call, not mine)

Give the carrier **its own pointer-bearing tag** and update the readers — they all spell the test identically, so
they are greppable. ⛔ **Not `DT_RAW`**: `descr.h:58` states `DT_RAW` and `DT_MAP` are the *value-never-a-pointer*
codes, and this one **is** a pointer the collector must trace. Equivalently, from the block side: make
`frame_elems` a first-class `HB_DVEC` block referenced by an honest tag.
