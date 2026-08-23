# FINDING 2026-08-23 (seat03) — row `zeta-frame-rsp-second-wild-write`: minimal, fully synthetic witness found by bisection; root mechanism not yet gdb'd

## HEADLINE

No minimal witness existed for this row — its own brief named that as the actual starting point. Bisected
`corpus/programs/snobol4/demo/beauty/beauty.sno` (630 lines, the SNOBOL4 self-host pretty-printer) down to a
15-statement, fully synthetic, `beauty.sno`-independent repro:
`corpus/probe/frame/frame_rsp_indexed_call_concat.sno`. Isolated ingredient: **N statements of the shape
`TABLE[fn(a) fn(b)] = 'v'` — a table-indexed assignment whose subscript is the concatenation of two function
calls.** Crashes reliably (rc=139, both `--run` and `--compile`) under `--zeta-storage=frame-rsp` at N=96,
runs clean (rc=0) at N=95 and under default (cell-stack) storage at any N tried. The exact faulting
mechanism (which frame-rsp slot, why N=96 specifically) was NOT root-caused this session — gdb work
(brief's own step 3) is the next step, now against a witness that takes milliseconds to run instead of a
630-line self-host.

## BISECTION LOG (every step re-run to confirm reliability, not a single lucky run)

1. **Confirmed the crash reproduces at current HEAD** (this seat's `scrip` binary was stale from earlier in
   the session — a first attempt against the stale binary hit a DIFFERENT, already-CLOSED bug,
   `IR_MATCH_CAPTURE_SAVE: no home`, rc=134/SIGABRT — a reminder this cost real time: always `make pristine`
   before trusting any repro on a row you didn't just build for). Fresh pristine rebuild, then:
   `scrip --zeta-storage=frame-rsp --run beauty.sno </dev/null` → rc=139, genuine SIGSEGV, 0 bytes of output
   or stderr — matches the row's own description exactly.
2. **`main00` (`beauty.sno:612`, `Line = INPUT :F(END)`) fails immediately on empty stdin** and jumps
   straight to `END` — so with `</dev/null`, none of `beauty.sno`'s `pp_*`/`ss_*` parser/pretty-printer
   functions are ever CALLED (a compiler compiles every `DEFINE`d body regardless, but compiling ≠
   executing, and the crash backtrace lands in `rt_outer_call` — i.e., it's the COMPILED program executing,
   not `scrip` itself compiling). This means the crash must be in top-level code that runs unconditionally
   before `main00`'s loop, not deep parser logic — a much smaller search space than "630 lines of self-host."
3. **`head -247 beauty.sno` + `END` still crashes** — confirmed by testing: this drops the ENTIRE `main`
   driver and every `pp_*`/`ss_*` function body, keeping only the top-level pattern/global-variable setup
   before the first `DEFINE`.
4. Cut further to `head -100` (crash), `head -65` (crash — the FIRST `$ tx $` capture-bearing top-level
   statement), then to **`-INCLUDE 'global.inc'` + that one later statement alone** (crash), then to
   **`-INCLUDE 'global.inc'` ALONE** (crash) — the later statement isn't needed at all.
5. Bisected inside `global.inc` (163 lines: `&ALPHABET`-derived single-char captures, `digits`/`TRUE`/`FALSE`
   constants, a large `UTF` unicode-name `TABLE()` populated via ~90
   `UTF[CHAR(a) CHAR(b)] = 'NAME'` inserts, then an unrelated `SORT`+indirect-assignment loop at the tail).
   `head -46` (just the ALPHABET captures + `digits`/`TRUE`/`FALSE` + first few UTF inserts): **no crash**.
   `head -157` (full UTF table, table-sort loop NOT included): **still crashes** — the tail loop is
   irrelevant. Binary-searched the exact line: **line 96 of `global.inc`: no crash; line 97: crash,
   reliable across 3 repeated runs each way.**
6. **Replaced the UTF-specific content with a fully synthetic repeated statement** to separate "this specific
   table/content" from "this statement SHAPE, repeated N times": `UTF = TABLE()` + N ×
   `UTF[CHAR(a) CHAR(b)] = 'Xi'` (varying `a`,`b`,content per iteration) reproduces at N=96, N=0 (no
   statements) trivially clean — **fully `beauty.sno`-independent, no `-INCLUDE` needed at all.**
7. **Ruled out three alternative mechanisms, each independently tested:**
   - **Not a generic frame-depth/statement-count threshold**: 500 repetitions of a plain `X = 1` (no
     subscript, no call) does not crash at any N tried.
   - **Not table growth/rehash**: repeating the exact SAME key 96+ times (table size stays 1 the whole
     time, only the value is overwritten) crashes identically to varying keys.
   - **Not "any function call in a subscript" or "any multi-part subscript"**: `T[a b]` (two plain
     variables, no call) at N=96 does not crash; `T[CHAR(1)]` (one call, single-arg subscript) at N=96 does
     not crash either. **Specifically requires the subscript to be the CONCATENATION OF TWO SEPARATE
     FUNCTION CALLS.**
8. Binary-searched the exact threshold on the clean synthetic witness: **N=95 → rc=0; N=96 → rc=139**,
   reproducible 3/3 each side. Final witness pinned at N=96 (the smallest confirmed-crashing count),
   committed as `corpus/probe/frame/frame_rsp_indexed_call_concat.sno` with an empty `.ref` (the program
   never calls `OUTPUT`; the interesting signal is the exit code, confirmed clean at rc=0 under default
   storage and crashing at rc=139 under `frame-rsp`, in BOTH mode 3 `--run` and mode 4 `--compile`+gcc+run).

## WHAT THIS DOES AND DOES NOT TELL US

**Does tell us:** the defect needs (a) a `TABLE()`-indexed assignment (b) whose subscript expression is a
concatenation of at least two function-call results, repeated (c) roughly 96 times in sequence, under (d)
`--zeta-storage=frame-rsp` specifically. The "roughly 96" threshold and its total independence from table
size/growth strongly suggests a **compile-time accumulation in the frame-rsp emitter's allocation
bookkeeping** (matching the row brief's own hint #4 — suspect the lifetime/allocation model, not the
arithmetic) that overflows, wraps, or aliases once enough of these particular multi-temporary statements
have been laid out — consistent with "a slot outliving or under-living its owning box" becoming a wild
pointer once enough slots have accumulated. This is a hypothesis from the bisection shape, NOT confirmed by
instruction-level evidence.

**Does not tell us (next session's job, brief's step 3):** the actual faulting instruction/address, which
zeta-storage bookkeeping structure is involved, or why "two concatenated calls" specifically is the trigger
ingredient rather than e.g. "two temporaries live simultaneously" more generally (not yet tested: does
`T[fn(a) fn(b) fn(c)]` — three calls — lower the threshold? Does a non-table target, e.g. plain
`X = fn(a) fn(b)` repeated N times, reproduce at all? These are cheap follow-up bisections against the
existing witness generator, not yet run this session due to time.). ASM-DIFF-FIRST (RULES.md) is the
prescribed next step: `--compile` this witness at N=95 (clean) and N=96 (crash) and diff the two `.s`
outputs — the delta is now bounded to essentially one extra repetition of one statement shape, which should
make the frame-rsp-specific emission difference small enough to read directly, before reaching for gdb.

## RECEIPTS

SCRIP (fresh `make pristine` rebuild this session, HEAD at time of bisection `b40a25a8`), corpus adds the
new witness + empty `.ref` under `probe/frame/`. Oracle not applicable (this row is a SCRIP-internal
zeta-storage arm defect, not a cross-engine correctness question). Every bisection step re-run at least
once to rule out flakiness (unlike the `vlist-expr-alternation` row's EVIDENCE 2b, where an earlier session
found a superficially similar zeta-storage defect was actually environment-dependent — checked for that
here too: the N=95/N=96 threshold held across repeated runs with no env-var changes, and separately across
mode 3 and mode 4, which use different code paths to reach the same crash, making a pure environment-layout
coincidence much less likely, though not strictly disproven without varying the environment deliberately the
way that earlier finding did).
