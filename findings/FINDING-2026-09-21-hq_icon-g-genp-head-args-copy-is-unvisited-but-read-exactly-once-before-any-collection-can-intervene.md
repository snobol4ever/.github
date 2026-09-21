# FINDING 2026-09-21 hq_icon — `g_genp_head`'s unvisited `args[]` copy is real, reachable, and PROVEN INERT (the fifth CEO-1019 candidate closes)

**Seat** hq_icon · **Mode** TENET · **Row** `icon-gc-the-generator-context-list-g-genp-head-holds-an-unvisited-copy-of-the-call-args-in-off-heap-memory`
**Tree** SCRIP `f839e933b`, corpus (unchanged), RT_OPT `-O0` · **Oracle** `/home/resources/icon-master/bin/icont`+`iconx` 9.5.25a

## THE QUESTION THIS ROW LEFT OPEN

The baton (minted by this seat 2026-09-20) named `rt_genp_s.args[CALL_ARGS_MAX]` (`src/runtime/rt/rt.c:1070`) as the fifth
CEO-1019 candidate and could not close it: `g_call_args[]` is visited (`rt_gc_root_args`, `rt.c:1994-2003`, wired into
`gc_heap.c:1309`), but the **copy** into `g->args[]` (`rt.c:1168`) is not, and a plain `suspend tag || "-1"` generator
never populates `g_genp_head` at all — so every prior reading over it was a zero nobody could have failed. Stated job:
find what reaches `rt_genp_entry_c`, then decide reachable-and-dangerous vs. reachable-and-inert.

## PART 1 — REACHABILITY, CONFIRMED (empirically, non-invasively)

`rt_proc_call_gen_h` (`rt.c:1157`) is the only allocator of `rt_genp_s`. Its callers, by grep, are exactly the
**by-value / indirect** generator-call sites in `src/runtime/by_name_dispatch.c`: `rt_call_value_gen_h:1286` (Icon
`p(x)` where `p` is a procedure VALUE) and `rt_pl_goal_gen_h_c:1445` (Prolog goal dispatch). It is NOT reached by an
ordinary direct `suspend` in a statically-named call — matching the baton's own negative result.

A comment already in the tree names the exact shape (`src/templates/bb/bb_call_value.cpp:56`, cto/hq_R): *"Measured
on Icon `every i := 1 to n do x := p()` with p a procedure value naming a generator: 11.2 kB and one live pthread per
abandoned call..."* — confirming genp is the by-value path and it is exercised routinely, not a corner nobody hits.
The corpus already carries a landed witness that walks it: `scripts/gc_witnesses/hb_coexpr_genp_scan.icn` (a
generator passed as a bare procedure name and invoked as `goal()` inside a scan).

I built a minimal witness and confirmed with the existing, non-invasive `SCRIP_C2BB_TRACE` hook (`rt.c:27`, an
env-gated file logger already in the tree — no source edited, no rebuild needed beyond the ordinary incremental one):

```icon
procedure gen(x)
   suspend x;
   suspend x;
end
procedure main()
   local p, r, i;
   p := gen;
   every r := p(["orig"]) do {
      write(r[1]);
      every i := 1 to 8 do repl("a", 65536);
   }
end
```

```
SCRIP_HEAP_MB=1 SCRIP_C2BB_TRACE=/tmp/genp_trace.log ./scrip gc_genp_witness.icn </dev/null
$ cat /tmp/genp_trace.log
genp.spine.n2	gen
```

`g_genp_head` is populated on ordinary, unremarkable Icon code (any indirect call to a generator). **Reachability is
not the open question; it is closed, yes.**

## PART 2 — IS IT DANGEROUS? TRACED EVERY READER OF `g->args[]`, THERE IS EXACTLY ONE

```
grep -n 'g->args\[\|->args\[i\]' src/runtime/rt/rt.c
  rt.c:1168   g->args[i] = g_call_args[i];        <- the write (inside rt_proc_call_gen_h)
  rt.c:1128   rt_arg_stage(i, g->args[i]);         <- the ONLY read, inside rt_genp_entry_c
```

`rt_arg_stage` (`rt.c:763`) has exactly one call site in the whole tree (`rt.c:1128`). `rt_genp_entry_c` is the
coroutine's OWN entry point (`rt_genp_thread_entry` → `rt_genp_entry_c`, wired at allocation via
`scrip_co_ctx_init(&g->co, rt_genp_thread_entry, (void*)g)`, `rt.c:1171`), and it runs exactly once: at the FIRST
activation, called **synchronously** within the same `rt_proc_call_gen_h` invocation that just wrote `g->args[]`
(`scrip_coexpr_activate(&g->co, ...)`, `rt.c:1176`, unconditional, same call). **Resumption never re-enters this
code path** — `rt_proc_resume_frame_h` (`rt.c:1207`) calls `scrip_coexpr_activate` directly on the already-running
coroutine, which resumes at the parked `scrip_coret`/`scrip_cofail` site inside `gen`'s own body, not at
`rt_genp_entry_c`. So across the generator's entire suspended lifetime — the part the baton worried about — nothing
ever looks at `g->args[]` again.

For a collection to corrupt this copy in a way that matters, a GC would have to run **between** `rt.c:1168` (write)
and `rt.c:1128` (read), both inside one synchronous call chain with no intervening collected-heap allocation:
`ct_zalloc` (`src/ir/ct_arena.c:68`) is the compile-time arena, explicitly not the collected heap; `scrip_co_ctx_init`
or coroutine-stack setup (`rt_coexpr.c:331`) touch no GC-managed memory either. There is no collection-triggering
call in that window. **The copy is read-once, synchronously, before any collector could ever see a stale value in
it — by construction, not by luck.**

## WHAT ACTUALLY PROTECTS THE ARGUMENT DURING SUSPENSION (a separate, already-tracked question)

Once `rt_arg_stage` runs, the argument lives on in the generator's OWN activation frame (`x`, bound on the
coroutine's private mmap'd stack — CLAUDE.md's "no software value stack, one-register frame" ζ design applies here
too). Whether THAT frame survives a collection while parked is the co-expression-stack-walking question, and it is
**not this row** — it is the fourth CEO-1019 candidate ("`g_co_gc_head` IS walked, partially, and its completeness
is the cfo's question") plus the ten `NO-ANCHOR-REACHES-SITE` co-expression sites already named undecidable in
`FINDING-2026-09-20-hq_icon-...-g-fh...`. Concretely: `g->co` (the embedded `scrip_coctx_t`) IS linked onto
`g_co_gc_head` (`scrip_co_gc_link(&g->co)`, `rt.c:1173`; `rt_coexpr.c:357`) and its `scan_state` is walked by
`rt_coexpr_gc_scan_states` (`rt_coexpr.c:358-364`) — but that walk visits `c->scan_state` only, never reaches
`rt_genp_s.args[]`, which sits at a different offset in the OUTER struct the `scrip_coctx_t*` list doesn't know
about. So this row's specific unvisited memory (the `args[]` snapshot) and the frame-preservation question are two
different gaps that happen to sit in the same feature; I confirmed my witness's actual correctness (both arms
matched oracle, `orig`/`orig`, at `SCRIP_HEAP_MB=1` and shipped arena) is consistent with frame-preservation working
for this shape — `hb_coexpr_parked.icn` (landed, currently green) already tests that class directly for native
`create` co-expressions and passes.

## CONCLUSION — CLOSES, SAME SHAPE AS THE OTHER FOUR

`g->args[]` is a real, measured root-set gap by the collector's own discriminator (a collected-heap pointer parked
where no visitor reaches it) — but it is **provably causally inert**: nothing ever reads it again after the
synchronous window in which it was written, so no collection can ever expose a stale value through it. This closes
CEO-1019's fifth Icon candidate with the same shape as the other four: not a defect, and said so with the reason,
not rounded up to "cured" or left as an unowned red.

⛔ **This is a proof of inertness for THIS storage class, not a green light for the class generally.** A future
change that adds a SECOND reader of `g->args[]` (e.g. a "replay" or "retry" path) would reopen this instantly and
without warning, because nothing enforces read-once — the invariant lives only in this FINDING and in the fact that
`rt_arg_stage` currently has one call site. `test_gate_*` coverage for "no second reader of g->args[] appears" would
need `grep -c 'rt_arg_stage(' src/runtime/rt/rt.c` staying at 1; not added here since a gate for an invariant this
narrow, on a file under active officer landings this sitting, is itself a shared-node change and out of scope for
this row.

## ROUTING

No cure needed — nothing to hand to an officer. Recorded here per CEO-1019 and folded into the baton's LEDGER in the
same sitting (this file will be summarized/deleted per Lon's periodic-cleanup word; the baton is the durable copy).
