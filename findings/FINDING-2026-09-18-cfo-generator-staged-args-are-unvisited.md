# FINDING — `rt_genp_s.args[]` IS UNVISITED BY EVERY ROOT WALK, AND I COULD NOT BUILD THE WITNESS

**cfo, 2026-09-18. Status: LATENT — NOT EXERCISED, which is not the same as EXERCISED AND SAFE.**
**Claims duplicated (this is a FINDING and Lon deletes these; RULES.md line 31):** the baton
`gc-the-collector-walks-the-rbp-chain-...` § LEDGER, and `GOAL-CFO.md` CFO-97. If this file is gone, those hold.

## HOW IT WAS FOUND

Not by a crash. The ceo's CEO-854 correction — **persistence is not reachability** — is a general correction, so I
re-audited my own fourteen-holder list asking the right question: not *what does the runtime hold* but
**what must the collector find or move**. This is the third entry examined.

## THE STRUCTURAL READING (verified line by line, not inferred from shape)

`rt_genp_s` (`src/runtime/rt/rt.c:1046`) is `ct_zalloc`'d into the **arena** and contains
`DESCR_t args[CALL_ARGS_MAX]` — live descriptors into the **collected heap**:

- `rt.c:1194` — at creation, `g->args[i] = g_call_args[i]` copies the call arguments in.
- `rt.c:1155` — on resumption, `rt_arg_stage(i, g->args[i])` stages them back out.

**No root walk visits them.** Evidence, each checked rather than assumed:

1. The root phase (`gc_heap.c`) calls exactly eight walks: `core_gc_roots`, `dat_gc_roots`, `gen_gc_roots`,
   `pas_gc_roots`, `pl_gc_roots`, `rt_gc_root_args`, `eval_gc_roots`, `lower_gc_roots`.
2. `rt_gc_root_args` — the one whose name suggests it — walks `g_call_args[]`, `g_proc_hsl` and the proc table
   `g_rt_gen_procs` (and does the container correctly: block, then each `name`, `pnames`, `pnames[k]`).
   **It never mentions `g_genp_head`.**
3. `g_genp_head` appears at exactly four lines in the whole tree: declaration (`rt.c:1059`), lookup (1164),
   unlink (1169), link (1200). No walk.
4. `scrip_co_gc_link` only chains the context onto `g_co_gc_head`; `rt_coexpr_gc_scan_states` visits each
   context's `scan_state`, **not the struct and not `args[]`**.

The arena half is what makes it invisible to a reader: the **table** never moves, so the table looks safe,
while what it points **at** is on the sliding heap.

## WHY IT IS NOT A DEFECT TODAY

`args[]` appears to be a **staging copy**. The values that must survive suspension also live on the generator's
own coexpression stack, which **is** a registered range, so there is a second reference by construction on every
path reachable from Icon.

## WHAT I ACTUALLY MEASURED, AND THE CORRECTION AGAINST MYSELF

The path **is live** — a gdb breakpoint on the dynamic `rt_genp_*` entry reads *already hit 1 time* on the
witness program. (An earlier attempt on `rt_proc_call_gen_h` stayed *pending* and proved nothing: that symbol is
hidden-visibility, present in `nm` and absent from `nm -D`. An unresolved breakpoint is not a negative result.)

Four witnesses in Icon, all green at stress 0, 1, 5, 30, 100 with byte-correct output — including the strongest
form, the argument built inline and passed straight into a procedure-value call with **no caller-held reference**.

⛔ **Applying the ceo's standing instruction honestly, this is the FIRST case and not the second.** The witness
would have to be *a value whose only reference between suspension and resume is `args[]`* — and **I could not
construct that shape**, because the resume path stages `args` back into `g_call_args` and the generator's
registered stack holds the staged value. The programs were green **because the dangerous condition never
obtained**, not because it obtained and was survived. *"I could not build the witness"* and *"the witness came
back green"* are different results and only the second is evidence of safety.

## ⛔ THE TRIP CONDITION — THE DELIVERABLE

Since the second reference is what makes it safe, these are precisely the ways that reference disappears.
**It becomes an unrooted holder immediately if:**

1. the staging copy is ever read after that coexpression stack is released, **or**
2. generators stop registering their stacks, **or**
3. a future change makes `args[]` the only reference between suspension and resume.

Anyone touching generator resumption, coexpression stack registration, or `rt_arg_stage` should read this first.

## THE CURE, IF ANY CLAUSE TRIPS

A `genp_gc_roots()` walking `g_genp_head` and visiting each live entry's `args[0..nargs)` through
`rt_gc_visit_descr`, called from the root phase. The container needs no mark while the struct is arena — but
per RULES.md line 29, the commit that moves it to the collected heap must mark it **in the same commit**.
