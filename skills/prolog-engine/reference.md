# The Prolog engine: the reference

Verified 2026-11-01 against SCRIP 9cb24d2ca. Consolidated from ARCH-PROLOG-BB-REWRITE, ARCH-PROLOG-BYRD-BOX-TRANSLATION, ARCH-PROLOG-THREE-ZETAS, ARCH-PROLOG-ACTIVATION-LIFETIME, ARCH-PROLOG-C-OUT-OF-THE-BOX, ARCH-PROLOG-SPINE-SEGMENTS, ARCH-PROLOG-RTX, ARCH-PROLOG-CONTINUATIONS and ARCH-PROLOG-THREADS, all retired (`.github/RETIRED-ARCH-PAGES.tsv`).

## 1. The term cell (one 16-byte DESCR; the tag byte is the collector's only tag)

| kind | tag | `slen` | value word |
|---|---|---|---|
| unbound variable | `DT_PLVAR` | 0 | its own address |
| bound reference | `DT_PLVAR` | 0 | the target cell (the deref loop follows it) |
| atom | `DT_PLATOM` | 0 | the atom id (compile-time interned; equality is one compare) |
| small integer | `DT_I` | 0 | int64 |
| float | `DT_R` | 0 | double |
| big integer | `DT_BIG` | | a pointer (a value service) |
| string | `DT_S` | length | `char *` |
| compound | `DT_PLREF` | the functor id (32 bits) | a pointer to the argument block (one collector block of `arity` DESCRs) |

A clause variable lives in its activation and reaches the heap only when a reference to it escapes (Lon 2026-09-28, the lifetime rule: the all-variables-on-the-heap design was ruled NO). Prolog integers are unbounded (SWI and the default). The compiler interns every atom and functor it sees; atoms made at run time go through the one runtime interner (`src/runtime/rt/prolog_atom.c`).

## 2. Every construct as a box

| construct | the box |
|---|---|
| a call `p(A,B)` | α enters the current clause and unifies the head; γ succeeds with the frame retained when a choice remains; β redoes the youngest sub-goal or steps the clause; ω unwinds the trail to the mark and releases |
| clause alternatives | the call box's β path; no choice-point stack beside the trail island |
| conjunction `A, B` | α to γ forward, γ to β backward |
| cut `!` | the enclosing call box's barrier (B, r13) dropping every younger alternative |
| if-then-else, `\+`, `once`, `ignore`, `forall`, soft cut `*->` | box graphs from lower (the soft cut is an if-type construct: its gate selects the continuation at run time, CEO-694) |
| `call/N` and any goal unknown at compile time | compiled at run time through EVAL/CODE, then an ordinary call box |
| `catch/3`, `throw/1` | a GATE whose ball entry claims the ball; `throw/1` arms r15 and propagates ω by ω |
| findall, bagof, setof | the forced-fail β loop from lower; collecting and grouping are value services |
| dynamic predicates | the database (skill `prolog` § the database), code not data |
| builtins | bound at compile time to their leaves, never a string at run time (the builtin table, skill `runtime-calls`) |

## 3. Instruments and hazards specific to Prolog

- `bench_prolog_call_census.sh REGEX` counts calls from emitted Prolog into a family over the kernels; `SCRIP_PL_TRACE=1` is the port tracer (boxes `n<i>` per graph).
- The dispatch chains of the old `dop` arithmetic were dead code: the cost was the call, never the dispatch; do not "fix" the chain again.
- An inline integer compare must replicate the C path exactly: the C path compares through `double`, so it diverges above 2^53 unless range-guarded.
- A Prolog tree pre-pass leaks into `clause/2`: transform the goal list at lowering instead.
- A ball never re-enters a retained frame.

## 4. Threads as designed (excluded by Lon, CEO-1766; nothing built)

Real pthreads with ONE BATON: exactly one thread runs SCRIP code at a time and gives the baton up only where its stack is mapped, so the collector keeps one mutator. The handoff is the co-expression handoff (`rt_gc_park_site`, `rtcc_coexpr_save`); preemption rides the existing poll (a timer stores a yield value into `g_gc_pending`); blocking (`thread_get_message`, `thread_join`, a mutex, `sleep/1`) is a handoff with a reason. The C core is a few atomic leaves; every policy (`thread_property/2`, `with_mutex/2`, `concurrent/3`) is prelude Prolog. Asked of Lon before any build: the new runtime state.

## 5. History a reader of old receipts meets

- The 2026-09-02 redesign put the trail inside each activation as its own binding log and deleted the choice-point stack; the later rulings (CEO-1542/1543) keep the trail and the choice records as the r12 island instead. `rt_pl_cp_push3`, `rt_pl_cp_pop3` and `g_pl_trail` are gone.
- The five rows of the C-out-of-the-box page (the activation frame, the choice words, body terms, meta-call, the dynamic database, the general unifier, mode-4 startup registration, the generator road, the call box, the head's write mode, first-argument indexing) took their C helpers out; the helpers named in SKILL.md § 1 no longer exist.
- The spine-segments page's count (cells rsp-addressable against the few rbp sites) is now the planner's plan columns (skill `scrip-memory-model`).
