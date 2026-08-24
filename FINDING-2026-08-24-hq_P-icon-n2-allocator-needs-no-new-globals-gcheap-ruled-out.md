# FINDING 2026-08-24 hq_P — icon-n2's remaining work (the off-stack activation allocator) needs NO NEW GLOBALS, because the off-stack non-moving per-generator store ALREADY EXISTS; and the GC heap is ruled OUT as its home, measured

LINKS: row `icon-n2-generator-activation-frames` (rank 0, GOAL-ICON-100 rung N-2). Predecessors, both hq_P s271: `FINDING-2026-08-24-hq_P-icon-generator-has-no-activation-frame.md` (three corruptions on the `rung03_suspend_gen` witness) and `FINDING-2026-08-24-hq_P-generator-frame-cannot-live-below-the-callers-rsp.md` (the two-moment gdb witness that disproved the storage half of the brief). Tree: SCRIP `ab9c087c`, corpus `fea43840f`, pristine `-O0`.

## THE HEADLINE, AND IT REMOVES A DEPENDENCY FROM THE CRITICAL PATH

The row's own baton predicted, in bold, that the next step would require a **NO-NEW-GLOBALS banner ask to Lon** — *"allocator handle / free-list is exactly the file-scope mutable state the law names"*. **It does not, and the reason is that the thing the corrected design needs is already in the tree**, has been for many sessions, and is currently scheduled for DELETION by this row's own slice (v).

`src/runtime/rt/rt.c:1354-1363` already carries an off-stack, growable, non-moving, per-generator-instance state store:

```c
typedef struct { void *gen_fb; void *cont; void *caller_fb; void *gwire; void *owire; } icn_gen_state_t;
static icn_gen_state_t  g_icn_gen_stk_buf[64];      /* plain static array — nothing moves it */
static icn_gen_state_t *g_icn_gen_stk = g_icn_gen_stk_buf;
static int              g_icn_gen_stk_top = 0;
static int              g_icn_gen_stk_cap = 64;
```

It is keyed by `gen_fb`, it has a find (`icn_gen_find`), a push and a pop (`rt_gen_save_wires`'s `gw`/`!gw` arms), and a growth path (`icn_gen_stk_grow` → `rt_ws_realloc`). That is precisely the shape an activation-record allocator needs. **The corrected design extends the element struct — `void *frame; uint64_t frame_sz;` — rather than introducing new file-scope state.** A field added to a file-scope struct that already exists is not a new global variable, a pinned VA slot, an exported cell, or a parallel array; it is an extension of state the law already permits to exist.

⛔ **THIS MAKES SLICE (v)'s DELETION LIST ACTIVELY DANGEROUS, not merely premature.** The baton already carried the warning (*"that machinery is the only existing off-stack path… delete AFTER the replacement allocator exists"*). This finding upgrades it: the machinery is not merely *an* off-stack path to keep around as a fallback — **it is the replacement allocator's own substrate.** Slice (v) as written would delete the storage the cure is built on. The list must be re-cut to delete only the *wire-shadowing* halves (`g_gen_pending_*`, the `rt_gen_get_fb` stub which is already `return (void*)0;`, the dead `icn_zframe_gen` consultation sites) while KEEPING and EXTENDING `icn_gen_state_t` + `g_icn_gen_stk*`.

## THE GC HEAP IS RULED OUT AS THE ALLOCATOR — MEASURED, AND THE REASON IS A DELIBERATE s262 DECISION

The obvious first idea is `rt_gcheap_alloc(HB_*, bytes)`: a typed heap block per activation. It cannot work, and the disqualifying fact is written in the collector's own source at `gc_heap.c:668`:

> `/* ⛔ THE PIN ARM IS GONE (Lon s262). It mapped a pinned block to itself (h->fwd = h) so the compactor left it in place; every live block now relocates. */`

**Every live block relocates.** The compactor fixes up only the pointer locations it can enumerate (`gc_heap.c:674`, walking registered roots and rewriting `*loc` through `h->fwd`). But under this row's protocol the activation-record address is banked in exactly the places the collector *cannot* enumerate: the per-call-site frame slot `FRQ(act+8)`, and word 3 of the on-stack resume record. A collection between suspend and resume would slide the record and leave both banked copies pointing at whatever now occupies that address — **the identical failure mode this row already measured once**, in `FINDING-…-generator-frame-cannot-live-below-the-callers-rsp.md`, where `0x7fffffffde30` held `{0,0}` at yield and `write()`'s own call frame by the time it was dereferenced. Same class of bug, different mechanism; a stack that reuses beneath rsp and a heap that compacts beneath a stale pointer fail the same way.

⭐ **So the storage requirement is now stated exactly, and it is a stability requirement, not a size one:** the activation record must live somewhere that **neither the C stack discipline nor the compactor may move or reuse while a suspension is outstanding**. `g_icn_gen_stk_buf` satisfies it by being a plain static array; the grown case satisfies it the same way the already-shipping `zeta_heap.c` does (`g_zh_tab` is `rt_ws_realloc`'d and its pointers are held stably across collections — an existing, working precedent in this tree, not a new bet).

## Co-EXPRESSIONS WERE CHECKED AND REJECTED, so nobody re-checks them

`src/runtime/rt/rt_coexpr.{c,h}` implements a full activation context — and it is **pthread-based** (`pthread_t thread; sem_t sema;` per context, `scrip_coswitch`, `scrip_coexpr_create(body_entry, regs, frame_bytes)`). Semantically an Icon generator suspension is co-expression-shaped, so this is the natural second idea. It is rejected on cost, not correctness: a thread and two semaphores per generator activation is not a mechanism this seat will put on the hot path of `rung03_suspend_gen`, and the row's parent goal is a speed goal. Recorded so the next session does not re-derive it.

## FRESH WATERMARK — AND THE ROW'S DONE-WHEN IS REACHABLE AGAIN

Per this row's own standing warning (*"recompute the watermark fresh before trusting any number here"*), which has now paid off three sessions running. `bash scripts/test_icon_all_rungs.sh`, pristine `-O0`, SCRIP `ab9c087c`, single checkout:

**PASS=246 · FAIL=16 · BADEXIT=1 · XFAIL=30 · TOTAL=293**

⭐ **This corrects the baton's headline blocker.** The LEDGER records `PASS=185` (s271, under the 47-program `IR_DISJUNCTION` regression) and seat13's `232/31/30`, and concluded in bold that **"DONE-WHEN is currently unreachable by this rung alone"** because the threshold is `PASS ≥ 256` and 232 + a best-case 12 = 244. Both inputs to that conclusion have since changed:

- the 47-program shared-node regression is **CURED** (`50997871`, keying the grant on the consuming ζ regime), and
- the suite now grades on **exit status**, which the board itself explains: *"BADEXIT = stdout matched .expected but the process exit status did not. Before hq_P s272 these counted as PASS… This is NOT a regression: it is the same tree, graded on exit status for the first time."*

At 246, this rung's own best-case yield (12) reaches **258 ≥ 256**. ⭐ **DONE-WHEN is reachable by this rung alone again** — it should stop being carried as an at-risk threshold. The margin is 2 programs, so it is reachable, not comfortable.

The 16 FAIL + 1 BADEXIT, which is exactly this rung's target witness set plus the D3-scan residue: `rung03_suspend_gen`, `rung03_suspend_gen_compose`, `rung03_suspend_gen_filter`, `rung03_suspend_return`, `rung36_jcon_{args,cxprimes,genqueen,level,mindfa,proto,recogn,scan,scan1,scan2,var}`, `rung37_proc_lookup`, `rung37_subscript_genproc`.

⚠️ **Instrument note for whoever reads that log:** it contains NUL bytes (a runaway-output test writes binary), so `grep` silently suppresses ALL matches as "binary file" and prints nothing — indistinguishable from "no failures found". Use `grep -a`. This cost this session two confused reads and is exactly the false-signal class that gets a clean board misreported.

## WHAT IS OWED NEXT

1. Extend `icn_gen_state_t` with the frame pointer + size; α allocates through the existing store, ω releases, ζ base register points at `e->frame` instead of at rsp. All behind `SCRIP_ICN_GENFRAME2`, still default OFF.
2. Re-cut slice (v)'s deletion list per the ⛔ above — delete the wire-shadow globals, KEEP and extend the state stack.
3. ⛔ Unchanged and still blocked: `test_gate_icn_rbp_census_ratchet`'s default-flip needs Lon's grant (the fifth census class). **Only the gate flip is blocked; killswitch-off work proceeds**, and that is where all of the above sits.
