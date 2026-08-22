# FINDING 2026-08-22 s254 (seat5) — unary-not-uninit-rodata: root-caused and fixed

Queue row `unary-not-uninit-rodata` (rank 0, seat6 s191 + seat7 s192 independent discovery). Brief: `corpus/programs/snobol4/parser/unary_not.sno` (one line, `x = ~BREAK(nl)`) emits a different `.s` on every `--compile` of the same binary — the compiler was baking uninitialised memory into `.rodata`.

## Repro (pre-fix)

```
for i in 1 2 3 4; do ./scrip --compile -o /tmp/u$i.s corpus/programs/snobol4/parser/unary_not.sno </dev/null; md5sum /tmp/u$i.s; done
```
Four distinct md5s. `diff` between any two isolates the whole delta to one `.rodata` symbol:
```
.S0:  .string  ":3\003"       (run 1)
.S0:  .string  "#^\003"       (run 2)
.S0:  .string  "\273\301"     (run 3)
.S0:  .string  "M\374\003"    (run 4)
```
`.S0` feeds a `lea rdi,[rip+.S0]` / `call rt_bomb@PLT` / `ud2` sequence — the shared `x86_bomb()` helper (`src/templates/x86_asm.h:2075`), reached from `bb_assign_global.cpp:22`'s "unhandled (needs descr flat-chain + rhs slot + own slot)" fallback arm. `x = ~BREAK(nl)` hits that arm because unary NOT of a pattern-returning call, assigned to a global, isn't yet a handled codegen shape — the BOMB itself is correct/intentional; only the message backing it was corrupted.

## Root cause

`bb_assign_global.cpp:22`:
```cpp
x86_bomb((std::string("bb_assign_global: unhandled (needs descr flat-chain + rhs slot + own slot) var=") + (_.op_sval ? _.op_sval : "?")).c_str());
```
`.c_str()` on a temporary `std::string` — the pointer is only valid until the end of the full expression. `x86_bomb` → `strtab_label` → `strtab_intern` (`src/emitter/emit.cpp:389`, pre-fix) stored that raw pointer by reference:
```cpp
g_strtab[g_strtab_n].s = s;   // borrowed pointer, not a copy
```
for a **deferred** read at `xa_emit_strtab_rodata()` — which runs at end-of-compile/end-of-flush, well after the temporary is destroyed and its memory reused. The `.rodata` emission then dereferences a dangling pointer: whatever now occupies that address becomes the "message." Every symptom follows: different garbage per process run (allocator/stack content varies), and *short* garbage (`gas_escape_str` reads a C-string until the first stray NUL it finds in reused memory, which comes early).

**Second-instance check (RULES: name it either way):** grepped every `x86_bomb(`/`bomb_text(`/`bomb_bytes(` call site in `src/` for a non-literal argument. `bb_call.cpp`, `bb_create.cpp`, `xa_coexpr_entry.cpp` use adjacent string-literal concatenation (static storage, safe). `bb_idx_get.cpp:16` ternary is two literals (safe). `bb_assign_global.cpp:22` was the **only** call site building the message from a temporary. Fixed at the shared root instead of the call site, so the class is closed regardless of which template calls it next.

## Fix

`src/emitter/emit.cpp` (SCRIP `483d8849`): `strtab_intern` now `strdup()`s the string at registration time (owns a stable copy, independent of the caller's storage duration); `strtab_reset()` frees the owned copies before zeroing the count (this table interns/flushes/resets many times per compile, so an unfreed strdup would leak per cycle, not just once).

## Verification

- 14 consecutive `--compile` runs of `unary_not.sno` post-fix: one md5 (`7b8393b1ac32732d59494a0e472bbda4`) throughout, both before and after two intervening rebases. `.S0` now reads the real message: `"bb_assign_global: unhandled (needs descr flat-chain + rhs slot + own slot) var=x"`.
- `make pristine` clean (HQ-27), three times (initial fix, +1 rebase, +1 rebase after `8c1f2d41` byname-bake-cell-address landed and touched the same file — diff confirmed non-overlapping, re-verified byte-identical after merge).
- `bash scripts/test_corpus_snobol4.sh`: mode-3 339/341, mode-4 338/341 SKIP 1 — the only two fails (`160_pat_alt_inner_gen_resume`, `demo_treebank`) are pre-existing/known (demo_treebank is seat8 s194's Alternative-Evaluation gap, blocked on `vlist-alt-zeta-depth`), fail-set no worse.
- No `.s` pinned into any gate.

DONE-WHEN met: source named (which buffer/write/why it escapes), byte-identical repro, second-instance class check performed and negative at the call-site level (root fix covers the mechanism), corpus fail-set unchanged, no `.s` pinned.

SCRIP `483d8849`. This finding pushed via `.github` at HEAD `f3267d29` (stale, see board/inbox note same session on the `.github` remote divergence) — commit hash for this file to be confirmed once that's resolved.
