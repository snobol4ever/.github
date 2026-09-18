# FINDING 2026-09-18 ceo — `CODE()` rebinding a label leaks ~20.5 KB per call, and rebinding is 15x worse than adding

- **Seat:** ceo · **Filed:** 2026-09-18 CDT · MODE EXECUTIVE
- **Trees:** SCRIP `d83a55c55` · `.github` (this commit)
- **Occasion:** Lon, in-chat to ceo: *"Compiler data is collected when a new labeled block of SNOBOL4 statements is compiled over an existing one. The old one will be collected."* He stated the semantics. This measured whether we implement them. **We do not.**

## §1 THE MEASUREMENT

Two witnesses, identical but for the label. `/usr/bin/time -f RSS=%M`, SCRIP mode 3, `RT_OPT=-O0`.

| `CODE()` calls | **same label rebound** | distinct labels |
|---|---|---|
| 200 | 19,916 KB | 13,128 KB |
| 2,000 | 57,548 KB | 14,196 KB |
| 20,000 | **423,920 KB** | 27,440 KB |

**~20.5 KB per rebind, linear, no plateau.** Baseline for a trivial program is ~12,900 KB, so at 20,000 rebinds the program holds **424 MB** of memory it can never reach again.

⛔ **AND THE CASE LON NAMED IS THE WORST ONE, WHICH IS THE OPPOSITE OF WHAT THE SEMANTICS PREDICT.** Rebinding one label 20,000 times costs **15x** what compiling 20,000 *distinct* labels costs. If the old block were collected, rebinding would be the CHEAP case — the table never grows and the storage is recycled. It is the expensive case, which is the signature of a leak rather than of a cost.

## §2 THE DIAGNOSIS, ONE LINE OF CODE

`src/runtime/runtime_eval.c:362`:

```c
for (int i = 0; i < g_lbl_n; i++) if (!strcmp(g_lbl_tab[i].key, name)) { g_lbl_tab[i].fn = (eval_chain_fn)fn; return; }
```

On a rebind the entry's `fn` is **overwritten and the function returns.** The previous `fn` is the old compiled BB blob, and nothing releases it:

- the **blob** lives in `bb_pool` — a bump allocator, page-granular (`bb_alloc` does `page_ceil(pool_top)` and rounds the size up to whole pages), so every abandoned blob wastes at least one full page. `bb_free` exists and is never called from this path.
- the **compile's own data** — AST, IR, `lp_strdup`'d interned strings, frame metadata — is in `ct_arena`, which is `A_PROG is immortal`: never collected, never freed.

~20.5 KB per rebind is consistent with one or two abandoned pages of blob plus the arena allocations of one compile.

## §3 WHY THE RULE PERMITTED IT, AND THE CAUSE IS THE ceo's WORDING

CEO-842 destination (2): *"anything ONLY THE COMPILER touches, **dead before the emitted program runs**, goes in the COMPILE-TIME ARENA … never collected, never freed, released by process exit."*

**`CODE()` and `EVAL()` run the compiler DURING the emitted program.** The clause's premise is false for every program that generates code, which is a first-class SNOBOL4 idiom. This is the THIRD edge the same clause has failed at today:

- **CEO-864** — the clause *condemned correct code*: `lp_strdup` interning into the arena with its address baked as an `imm64`.
- **CEO-887** — the predicate had to be restated as *does the collector need to find or move it*, not *is it compiler-only*.
- **This** — *dead before the emitted program runs* is simply false whenever `CODE`/`EVAL` runs.

⭐ **THE COMMON CAUSE, AND IT IS ONE SENTENCE: THE RULE WAS WRITTEN IN TERMS OF *WHEN* MEMORY IS USED INSTEAD OF *WHO OWNS IT AND WHAT RECLAIMS IT*.** All three edges fall out of that and no fourth wording will fix it — the rule has to name an owner and a reclaimer.

## §4 WHAT LON'S SEMANTICS IMPLY FOR THE DESTINATION

His sentence is also the reclamation rule, and it is decidable: **a compiled block is reachable exactly through its label-table entry, and a rebind makes the previous block unreachable.** So compiled code is ordinary collectable data with `g_lbl_tab` as its root — **destination (1), the collected heap with a root, not destination (2).**

That is the opposite of where it lives now, and it is why the arena could not answer the question: a bump arena cannot be told that one of its blocks just became unreachable.

## §5 SPITBOL DOES RECLAIM THIS

SPITBOL's storage regeneration reclaims dead code blocks; a SNOBOL4 program that rebinds a label in a loop is bounded there. We are measurably not bounded, on the rival's own idiom, in the language the 10x goal is set against.
