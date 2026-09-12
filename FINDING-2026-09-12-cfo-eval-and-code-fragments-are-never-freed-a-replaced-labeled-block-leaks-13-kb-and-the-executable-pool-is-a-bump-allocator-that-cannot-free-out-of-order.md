# FINDING 2026-09-12 cfo — EVAL and CODE fragments are never freed: a replaced labeled block leaks 13 KB, a retained EVAL 5.5 KB, and the executable pool is a bump allocator that cannot free out of order

**Seat** cfo · **Mode** EXECUTIVE · **On Lon's word** (2026-09-12 17:5x CDT, verbatim: *"Go and check that EVAL and CODE items get freed at the appropriate times. I want to make sure that executable slab code is getting freed. I suspect it is by labeled block replacements."*) · **Tree** SCRIP `3fde23f04` + the day's emitter work.

## Measured

| loop, mode 3 | 5,000 | 20,000 | per item | reclaimed |
|---|---|---|---|---|
| `C = CODE('BLK OUTPUT = ' I ' ;')` -- the same label replaced each time | 80 MB peak RSS, 1 s | 277 MB, 4 s | **13.1 KB per replaced block** | never |
| `X = EVAL(I ' + 2.0')` -- a distinct expression each time | 44 MB | 127 MB | **5.5 KB per retained fragment** | never |

Both loops print `all N ok` under `sbl -bf`; both pass under SCRIP today only because the executable pool was raised this afternoon from 64 MB to a 2 GB `MAP_NORESERVE` reservation. On the 64 MB pool the distinct-EVAL loop **failed silently at 15,359** (`&ERRTYPE` 0, `&ERRTEXT` empty): `bb_alloc` returns NULL and the caller reports nothing. That is why the last 15 of `math_sum`'s 15,376 checks read "runtime error" with an empty observation: the suite's 15,376 distinct expressions filled the pool.

## Where, in the code

- **The pool** (`src/ir/bb_pool.c`): one `mmap` region, a bump pointer (`bb_alloc` = page-rounded advance), sealed RX per allocation, and release only from the top: `bb_free` aborts on a non-LIFO free, `bb_pool_release(mark)` rewinds to a mark. Nothing in the middle of the pool can ever be returned.
- **EVAL** (`runtime_eval.c: eval_string_transient`): compiles the string into the pool, runs it, and keeps it in `g_eval_cache` **if the pool mark is below `eval_retain_budget()`**, whose default is unlimited (`SCRIP_EVAL_RETAIN` unset → `~0`). Past the budget it releases the mark -- correct and LIFO-safe, because an EVAL fragment finishes before the release. So the mechanism exists and the default disables it; and a cached fragment is never evicted.
- **CODE** (`runtime_eval.c: rt_label_set_fn`): a labeled block compiled by CODE is emitted into the pool (`emit_chain(..., "code_flat")`, a 4 MB reservation trimmed to size) and the label table entry is **overwritten** with the new pointer. The displaced fragment is not released, and cannot be: it sits below everything allocated since.

Lon's suspicion is exactly right: labeled block replacement is the leak, and EVAL retention is the second one.

## Why it is not a one-line fix, and the design that fits

Freeing a replaced block is not only an allocator question, it is a **liveness** question: after `CODE` replaces label `BLK` from inside `BLK`, execution continues in the OLD block until control leaves it by a transfer, and a function body compiled by CODE may be on a return path. A free at replacement time would pull the floor from under running code.

The design that fits the machine, all of it in the runtime's own arena code and none of it on the compiled call path:
1. **A fragment arena separate from the main slab**: each EVAL/CODE fragment is emitted into the pool as today, then copied whole into its own page-rounded RX mapping and the pool mark released. A fragment copied whole stays valid: its own labels are RIP-relative and move together, runtime calls are absolute pointers, program labels are reached by name (`rt_goto_transfer`), variables through the GVA's absolute addresses.
2. **A quarantine, not a free, at replacement**: `rt_label_set_fn` puts the displaced mapping on a quarantine list. A fragment leaves the quarantine (munmap) when its activation count is zero: entered via `rt_proc_enter_frag`/`rt_goto_transfer` into it (+1), left by a transfer out of it or a return (-1). The transfer hook is the one place both entry and exit already pass.
3. **EVAL**: a default retain budget (64 MB is the number the old pool taught) with eviction of the least-recently-used cached fragment, guarded by the same activation count so a fragment running (recursive EVAL of one string) is never evicted.

Until that lands, the 2 GB reservation buys ~150,000 replaced blocks or ~350,000 distinct EVALs before the same silent failure, and the silent failure itself should not stay silent: `bb_alloc` returning NULL must raise a numbered error, not an empty `&ERRTEXT`.
