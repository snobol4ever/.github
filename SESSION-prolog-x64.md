# SESSION-prolog-x64.md — Prolog × x64 ASM (snobol4x)

**Repo:** snobol4x · **Frontend:** Prolog · **Backend:** x64 ASM (NASM)
**Session prefix:** `PX` · **Trigger:** "playing with Prolog x64" or "Prolog x86"
**Driver:** `sno2c -pl -asm foo.pl > foo.s` → `nasm -f elf64 foo.s -o foo.o` → `gcc -no-pie foo.o ...srcs... -lm -o foo`
**Deep reference:** `ARCH-prolog-x64.md` · `FRONTEND-PROLOG.md`

## Subsystems

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| Prolog language, IR nodes | `FRONTEND-PROLOG.md` | parser/AST questions |
| Historical session notes | `ARCH-prolog-x64.md` | F-212..F-214 design decisions |
| JVM emitter (mature reference) | `prolog_emit_jvm.c` | algorithm reference |

---

## §BUILD

```bash
cd snobol4x && make -C src
./sno2c -pl -asm foo.pl > foo.s
nasm -f elf64 foo.s -o foo.o
gcc -no-pie foo.o \
  src/frontend/prolog/prolog_atom.c \
  src/frontend/prolog/prolog_unify.c \
  src/frontend/prolog/prolog_builtin.c \
  -lm -o foo
```

**Key facts:**
- Link `.c` source files directly (no separate `prolog_runtime.c` exists)
- `-no-pie` required (NASM 32-bit PC-relative calls incompatible with GCC PIE default)
- `-lm` required (pow, sqrt, log, etc.)
- `nasm` must be installed: `apt-get install -y nasm`

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **Prolog x64** | `PX-1` | `532be13` | M-PJ-X64-3 (multi-ucall backtrack) |

**M-PJ-X64-1 ✅ M-PJ-X64-2 ✅** at `8843d71` — tak/nrev/qsort PASS, times10/ops8/log10 PASS.  
**Parts A/B/C (`\+`/`\=`)** ✅ at `e3f92cc` — naf PASS, alldiff PASS.  
**Multi-ucall backtrack** 🔲 WIP at `532be13` — root cause diagnosed, fix partial.

## CRITICAL NEXT ACTION — multi-ucall backtrack (M-PJ-X64-3 final blocker)

### Background: what was diagnosed this session

All changes are in `src/backend/x64/emit_byrd_asm.c`. Four bugs found and addressed:

**Bug 1 ✅** (`e3f92cc`): inter-ucall trail mark was dead code (between β exit-jmp and γ label).  
**Bug 2 ✅** (`532be13`): βN unwind target = `UCALL_MARK_OFFSET(N)` (mark *after* ucall N-1) → ucall N-1 bindings survived → retry always got already-bound args. Fixed to `UCALL_MARK_OFFSET(N-1)`.  
**Bug 3 ✅** (`532be13`): `UCALL_MARK_OFFSET(0)` was taken at clause entry before head unification → β0 undid head bindings. Fixed: moved to body label with a fresh `trail_mark_fn` call after all head args unified.  
**Bug 4 ✅** (`532be13`): body always started fresh (`xor edx,edx`); added stride-based re-entry decode — `inner = start-base`, pre-loads ucall slots from `inner-1` packed as `slot_K = (inner-1 >> 12*K) & 0xFFF`, then jumps to α0.

### Current test status

```
naf:     PASS
minimal2 PASS  ([2,1] — 2-ucall fact backtrack)
alldiff: FAIL  — all_diff([1,2,3]) → fail1  (was ok1 before Bug 3 fix)
retry2:  FAIL  — permutation retry → none instead of [2,1,3]
```

### Most likely remaining bug

The body-entry `trail_mark_fn` call (Bug 3) uses `rdi` = `[rel pl_trail]`.
`trail_mark_fn` returns the mark in `eax`. Immediately after, the re-entry decode
reads `[rbp-32]` (start) into `eax`, overwriting the mark value — but the mark was
already stored into `[rbp - UCALL_MARK_OFFSET(0)]`, so that's fine.

**Actual suspect**: `trail_mark_fn` is called with `rdi = &pl_trail`. But the emitter
passes `Trail*` as `rdi` at the function call sites. Check whether `trail_mark_fn`
signature matches — it should take `Trail*` as first arg. If it takes *no* args and
reads the global directly, the `lea rdi` is harmless noise but the call is still OK.

**More likely culprit**: in clauses with zero ucalls (facts / builtin-only), the new
`UCALL_MARK_OFFSET(0)` block is guarded by `if (max_ucalls > 0)` — but `all_diff/1`
clause 2 (`all_diff([H|T]) :- \+ member(H,T), all_diff(T)`) has `\+` (now a builtin,
not a ucall) and `all_diff/1` recursion (1 ucall). So `max_ucalls=1`. The body-entry
mark call happens. **The mark call clobbers `eax` — but right before `xor edx,edx`
and the fresh-entry path. The `sub_cs_acc` at `[rbp-16]` is zeroed at clause entry
(before the mark call). The mark call returns the mark in `eax`. Then `xor edx,edx`
zeros edx. The `\+` handler calls `trail_mark_fn` again internally via push/pop.
All seems OK.**

**Most likely: check `all_diff` clause 2 generated ASM carefully.** The `\+`
inline emission uses `push rax / pop rax` around the inner call — verify these
don't clobber `[rbp-24]` (args array ptr). Since push/pop only affect rsp and the
memory at [rsp], and `[rbp-24]` is a frame slot not a stack-relative slot, this
should be safe. Generate the ASM and read it.

### How to rebuild and test

```bash
cd snobol4x && make -C src -s
# Gate test files (recreate each session — /tmp doesn't persist):
cat > /tmp/naf.pro << 'EOF'
:- initialization(main, main).
main :-
    ( \+ fail -> write(naf_ok) ; write(naf_fail) ), nl,
    ( \+ (1 = 2) -> write(neq_ok) ; write(neq_fail) ), nl.
EOF
cat > /tmp/alldiff.pro << 'EOF'
:- initialization(main, main).
all_diff([]). all_diff([H|T]) :- \+ member(H, T), all_diff(T).
member(X, [X|_]). member(X, [_|T]) :- member(X, T).
main :-
    ( all_diff([1,2,3]) -> write(ok1) ; write(fail1) ), nl,
    ( \+ all_diff([1,2,1]) -> write(ok2) ; write(fail2) ), nl.
EOF
cat > /tmp/minimal2.pro << 'EOF'
:- initialization(main, main).
mylist([1,2]). mylist([2,1]).
headis2([2|_]).
search(L) :- mylist(L), headis2(L).
main :- ( search(L) -> write(L) ; write(none) ), nl.
EOF
# Build helper:
build_run() {
  f=$1
  ./sno2c -pl -asm "$f" -o /tmp/t.asm &&
  nasm -f elf64 /tmp/t.asm -o /tmp/t.o &&
  gcc -no-pie /tmp/t.o src/frontend/prolog/prolog_atom.o \
    src/frontend/prolog/prolog_unify.o src/frontend/prolog/prolog_builtin.o \
    -lm -o /tmp/t && timeout 5 /tmp/t
}
```

### Key emitter locations (`emit_byrd_asm.c`)

| What | Approx line |
|------|-------------|
| Clause-entry mark `[rbp-8]`, slot zeroing | ~5753 |
| Head unification loop | ~5768 |
| Body label + `UCALL_MARK_OFFSET(0)` mark | ~5800 |
| Re-entry decode block | ~5810 |
| Fresh-entry `xor edx,edx` | ~5845 |
| `\+` inline handler | ~5880 |
| sub_cs_acc stride accumulation (ucall success path) | ~6755 |
| βN unwind + retry | ~6816 |
| γ return encoding | ~6844 |

---

## Milestone Table

| ID | Description | Gate | Status |
|----|-------------|------|--------|
| M-PJ-X64-1 | Multi-clause dispatch | tak/nreverse/qsort PASS | ✅ `8843d71` |
| M-PJ-X64-2 | Arithmetic (is/2, comparisons) | times10/log10/ops8 PASS | ✅ `8843d71` |
| M-PJ-X64-3 | \+ / \= / multi-ucall backtrack | naf/alldiff/crypt/sendmore/queens PASS | 🔲 WIP `532be13` |
| M-PJ-X64-4 | List builtins (member/append) | nreverse/qsort/flatten PASS | 🔲 |
| M-PJ-X64-5 | Timing grid ≥15/31 vs SWI native | BENCH-prolog-x64.md committed | 🔲 |
