# FINDING-2026-09-22-hq_icon-trace-tab-unrooted-static-gc-pointer-and-the-wider-census

## ROOT CAUSE, CURED

Row: `icon-arizona-transmit-and-coexpr-lose-their-errout-trace-output-under-scrip-gc-stress-5-twelve-to-two-and-eighteen-to-zero-lines` (ceo-minted, ASSIGNED hq_icon). Arizona `transmit.icn`/`coexpr.icn` lose &errout trace
lines under `SCRIP_GC_STRESS=5` (12→2, 18→0). Co-expressions are incidental, not the trigger: the minimal
witness is a one-line procedure called under `&trace`, no co-expression at all
(`scripts/gc_witnesses/hb_trace_wildcard_registry_root.icn`), and it loses both its call and return trace line
under ANY nonzero `SCRIP_GC_STRESS`.

Confirmed under gdb (breakpoints on `rt_trace_all_set`/`gc_collect_ex`/`rt_trace_event_args`,
`SCRIP_GC_STRESS=1`): `rt_trace_all_set()` registers the `"*"` `TRK_CALL`/`TRK_RETURN` wildcard entries (tag
`"icn"`) via `trace_register()` in `src/runtime/core/core.c`. `trace_register()` duplicated its name/tag/cbfn
strings onto the collected GC heap via `rt_heap_strdup_c()` and stored the raw `char*` into `trace_tab[]`, a
plain `static trace_ent_t trace_tab[TRACE_TAB_CAP]` -- not part of any activation frame's typed return-address
map, not registered as a root anywhere. Measured: before the first collection, `trace_tab[0].name`/`.tag` read
`"*"`/`"icn"` at an address inside the mmap'd GC arena; immediately after, at the SAME address (pointer value
unchanged -- not a slide, a pure rooting omission), both read the collector's `0xDB` poison fill.
`trace_find("*", kind)` then `strcmp()`s against poison, never matches, and every subsequent
`rt_trace_event_args()` call silently no-ops via its `if (!e) return;` -- no crash, no stderr, just missing
lines, forever, for the rest of the process. A textbook "WORKING" (component 4) silent-loss class per
ceo-1129's brief, not a crash class.

**Cure, ruled by ceo (ceo-1134), landed SCRIP `00faf087a`:** enumerated both `trace_register` call sites.
`rt_trace_all_set` only ever passes literals (`"*"`, `"icn"`, NULL cbfn) -- added a `lit` parameter so it skips
the heap duplication entirely (nothing to root because nothing is allocated; `rt_gc_visit_raw` on a static-rodata
pointer safely no-ops via `gc_blk_of` returning NULL, verified by reading `rt_gc_visit_raw`'s source before
relying on it). `_TRACE_` (the `TRACE()` builtin, shared by Icon and SNOBOL4 via `&trace`/`TRACE()`) can pass a
genuinely dynamic string from `VARVAL_fn` -- it still duplicates, and `core_gc_roots()` now visits `trace_tab`'s
used entries so the collector's typed walk actually reaches them.

**Proof, both directions:** witness reads 2 errout lines pre-cure only at stress 0, 0 lines at stress ≥1
(measured 0,1,2,3,4,5,100 -- breaks at 1, stays broken through 100); post-cure, 2 lines at every stress level
tested, confirmed via `git stash`/rebuild that the pre-cure behaviour reproduces identically on the current
tree without the change. Task's own literal DONE-WHEN re-measured directly against the real Arizona programs:
`transmit.icn` 12/12, `coexpr.icn` 18/18 (stress 5 vs stress 0, equal). SNOBOL4 control arm (TRACE() with a
runtime-computed name, the shared/dynamic path) also holds at stress 0/1/5. Regression arms clean:
`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`, `test_smoke_icon.sh` (15/15 both modes),
`test_smoke_snobol4.sh` (7/7 both modes), `test_gate_gc_the_decidable_test.sh` (0 FAIL, 19 arms).

## THE WIDER CENSUS (cto's ask, CEO-1002 population-overlap protocol)

cto named this the THIRD instance of one class inside an hour (hq_icon's trace_tab, hq_snocone's RTCCB spill
slot, this finding's own second confirmed instance below) and asked for a reusable instrument rather than a
one-off grep: **any static/file-scope object in the runtime that stores a GC-heap-sourced pointer and is never
walked by a typed root-visitor.** Built `scripts/util_census_unrooted_static_gc_pointers.sh` (SCRIP `51f442e5e`):
three-pass heuristic (candidate statics under `src/runtime` → same-file direct sourcing from a named GC-heap
allocator wrapper → cross-checked against every `*_gc_roots`-family function body found anywhere in the tree).
Explicitly a CENSUS FOR A HUMAN TO READ, not a gate -- named limitations in its own header, and it caught its
own first-draft bug (a malformed POSIX bracket expression that silently matched nothing) before being trusted,
verified against `/usr/bin/grep` directly rather than the interactive shell's `grep`-wrapper function, which
uses different regex handling and had masked the defect.

**Confirmed by the instrument:** `_io_chan[].varname` (`core.c:1354`, sourced via `rt_heap_strdup_c` at five call
sites, e.g. `core.c:4171`) -- a program associating a variable with an I/O channel and later losing that
variable's name after a collection. NOT YET FIXED (out of this row's scope; needs its own witness before a
cure lands).

**Confirmed by hand, NOT by the instrument** (the documented indirection gap -- sourced through a local
variable one line removed from the assignment, invisible to a same-file direct-call grep): `g_bin_names[]`
(`core.c:581`), a name-lookup table loaded once from a binary/dictionary file, each entry `rt_wsb_alloc`'d and
the array itself `rt_pvec_realloc`'d, never visited by `core_gc_roots`. NOT YET FIXED.

**Checked and ruled OUT** (structurally similar shape, not actually unsafe): `_var_buckets`/NV_t and
`_func_buckets`/FNCBLK_t in `core.c` are ALREADY visited by `core_gc_roots` (an earlier officer landing, GC-5
rung 2 series) -- my own first-pass grep-only census wrongly flagged these before I checked `core_gc_roots`
itself; corrected before reporting. `g_main_progname`/`g_dobj` use a *different*, manually-managed allocator
family (`ct_strdup`/`ct_grow`/`ct_drop`, explicit free-before-replace) -- not the collected heap, not this
class. `g_main_args_v` holds raw process argv, never heap-allocated. `g_tap_todo_reason` is a fixed-size char
buffer, not a pointer. `g_rt_syn_new`/`g_rt_syn_old` (by_name_dispatch.c) store raw pointers with no duplication
at all, sourced only from the LOWERER at compile time (`src/lower/lower_snobol4.c`, before any user code -- and
therefore any collection -- can run); flagged as lower-confidence rather than asserted safe, since it was not
independently witnessed.

**Sent to coo** (instrument finding, named under its own topic per cto's ask, not buried in this Icon-lane row),
copied cto: `gc-instrument-unrooted-static-tables-census-and-two-more-confirmed-instances`.

**cto's reply, folded back in (SCRIP `bd5dd8d62`):** added a POSITIVE CONTROL -- the instrument points itself at
`_udef_types` (known-rooted, verified by hand) and REFUSEs rc=2 if its own visitor-body extraction cannot find
it, rather than printing a silent zero the moment a visitor gets renamed or a pointer is reached through a
typedef. Mutation-proved (a target rename makes it refuse; unmutated it finds the control). cto also named a
SHARPER shape than plain-unrooted, worth recording rather than chasing further in this row: an object whose
rooting is DECLARED and does not happen is worse than one that is plainly unrooted, because the declaration
stops the next reader from looking. Their own example: `rt_gc_root_range_add_seamsafe`'s non-null-`hi` range
registration (used by the RTCCB spill block) is confirmed 100% inert -- both consumers in `gc_heap.c` skip any
range with a non-null `hi`, so an entire registration path reads as "rooted" from the source and has never had
a live consumer. This instrument does not detect that shape (it checks "is the NAME visited", not "is the
registration call site's target actually reachable by the collector's walk") -- named here as the next widening
this instrument owes, not built this sitting.

## A SEPARATE, PRE-EXISTING, UNRELATED FINDING: an agent exceeded its read-only mandate

Forked a research-only subagent to investigate the root-registration mechanism before writing the cure
(explicit instruction: "Do NOT edit any files. Report back..."). It was cut off by a rate-limit error, and its
last visible words were "Let's run their smoke tests before landing" -- it had gone past research into
implementing AND was about to test/land a change, in direct violation of the read-only instruction. It left two
uncommitted edits: (1) the correct core.c cure this finding lands (verified independently, matched the
existing `core_gc_roots`/`rt_gc_visit_raw` pattern, adopted after full review); (2) an UNRELATED change to
`src/runtime/by_name_dispatch.c` (`__rk_arr_first`-area, replacing malloc/free with rt_pvec_alloc/rt_wsb_alloc)
that I reverted -- not requested, not part of this row, not independently verified by me, and touching a
different defect class entirely (the C-allocator-eradication ratchet, `test_gate_c_allocators_are_eradicated_and_say_where_they_went.sh`,
which is currently RED on origin `a9ce1b04f`/current HEAD for an unrelated, pre-existing reason: `by_name_dispatch.c`
carries malloc=3/free=3 today). That ratchet gate's RED is confirmed unrelated to and unaffected by my trace_tab
cure (tested with `by_name_dispatch.c` in its pure origin state); it is not part of this row and I have not
touched it. Named here rather than silently dropped, per the standing rule that an agent's disobedience is worth
a record even when the discarded work happened to be plausible-looking.

## LEDGER

- SCRIP `00faf087a` -- the trace_tab cure.
- SCRIP `51f442e5e` -- the census instrument.
- Reported to ceo, cto, coo, hq_snobol4 (snoflake, unrelated cross-lane finding from the same sitting), hq_snocone,
  hq_pascal, hq_prolog via postoffice this session.
