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
| **Prolog x64** | `PX-1` | `a051367` | M-PJ-X64-3 (3-ucall re-entry) |

**M-PJ-X64-1 ✅ M-PJ-X64-2 ✅** at `8843d71`.  
**Parts A/B/C (`\+`/`\=`)** ✅ at `e3f92cc`.  
**2-ucall backtrack** ✅ at `a051367` — naf/alldiff/minimal2/retry2 all PASS.  
**3-ucall re-entry** 🔲 — loops; root cause identified, fix designed.

## CRITICAL NEXT ACTION — 3-ucall re-entry loop (M-PJ-X64-3 final blocker)

### What is fixed (all in `emit_byrd_asm.c`, committed at `a051367`)

| Bug | Fix |
|-----|-----|
| Inter-ucall trail mark in dead code | Moved to success path before `jmp γN` |
| βN unwind to wrong mark (post-ucall N-1) | Now unwinds to `UCALL_MARK_OFFSET(N-1)` |
| `UCALL_MARK_OFFSET(0)` before head unif | Moved to body label, fresh `trail_mark_fn` |
| Body always started fresh (ignored start) | Stride-based re-entry decode added |
| `inner = start-base` negative (head-fail jump) | Changed `jz` → `jle` for fresh check |
| `sub_cs_acc` corrupted on retry | γN now recomputes from slots 0..N |
| `pop ecx` invalid in 64-bit | Fixed to `pop rcx` |

### Remaining bug — 3-ucall γN slot-zeroing conflict

**Symptom:** `find(N,Qs) :- numlist(1,N,Ns), permutation(Ns,Qs), safe(Qs)` loops for N≥2.

**Root cause:** γ0 (reached after ucall 0 = numlist succeeds) zeros `UCALL_SLOT_OFFSET(1)` so that ucall 1 (permutation) starts fresh when numlist finds a new answer. But on re-entry, the re-entry decode pre-loads `slot_1 = K` (the permutation sub_cs to resume). Then α0 (numlist retry) succeeds — possibly at the same answer — and γ0 fires, zeroing `slot_1`. α1 then calls `permutation_r(start=0)` (fresh) instead of `permutation_r(start=K)` (resume). Permutation always gives its first solution → same safe-check → same fail → infinite loop.

**The fix: separate fresh vs resume entry points for α0.**

Add a `resume_α0` label that jumps directly past γ0's slot-zeroing into α1 with slot_1 intact. The re-entry decode, instead of jumping to `α0`, should jump to `resume_αK` where K is the deepest ucall to resume.

Concretely: for a 3-ucall clause on re-entry with `inner > 0`:
- Decode `slot_0`, `slot_1`, `slot_2` from packed inner-1
- Pre-load all three slots
- Determine which ucall to resume: it's the deepest one with slot > 0
  - if `slot_2 > 0`: jump to `α2` (bypass α0, γ0, α1, γ1 — but vars not bound)
  - if `slot_1 > 0`: jump to `α1` (bypass α0 and γ0's slot-zeroing)
  - else: jump to `α0`

But jumping to α1 skips head unif and α0's work — vars from prior ucalls are still live from the original call (trail unwind at the caller's β only undid the last ucall's work). So jumping to α1 directly with pre-loaded slots is correct.

**Simpler equivalent fix:** In the re-entry decode, after pre-loading all slots, jump to `αK` where K = highest slot index with non-zero value. This bypasses all γ slot-zeroings:

```c
/* After pre-loading all slots in re-entry decode: */
/* Find deepest non-zero slot and jump to its αK */
int resume_ucall = 0;
for each ucall K from max_ucalls-1 down to 0:
    if slot_K != 0: resume_ucall = K; break
A("    jmp pl_%s_c%d_α%d\n", pred_safe, idx, resume_ucall);
```

But at emit time we can't know which slot will be non-zero (it's runtime data). So the emitted code must do this at runtime:

```asm
; after pre-loading slot_0, slot_1, slot_2:
cmp dword [rbp - UCALL_SLOT_OFFSET(2)], 0
jne pl_PRED_c_α2
cmp dword [rbp - UCALL_SLOT_OFFSET(1)], 0
jne pl_PRED_c_α1
jmp pl_PRED_c_α0
```

Jumping to `α2` directly skips fresh var allocation (already done at c_α entry above the body), head unification (already done), and α0/γ0/α1/γ1. The vars `_V0.._VN` are freshly allocated at clause entry and bound by head unification. The trail unwind at the caller's β undid the *last* ucall's bindings — so jumping to α2 with slot_2 is correct: vars are bound (from head unif), ucall 0 and 1's bindings are live (from previous successful calls before the unwind), only ucall 2's bindings were undone.

**Wait** — the trail unwind at the caller's β2 unwound to `UCALL_MARK_OFFSET(1)` (mark after ucall 0 succeeded, before ucall 1). This undoes both ucall 1 *and* ucall 2's bindings. So ucall 1's bindings are also gone. We cannot jump directly to α2 — we must re-run α1 (permutation) to get its bindings back. So the correct resume point is α1 (not α2) when β2 fires and we're re-entering permutation.

The key insight: **the caller's β always fires for the last ucall** (β2 = ucall 2 failed), and it retries the previous ucall (α1 = ucall 1). So the re-entry always resumes at `α_{last-1}`. For a 3-ucall clause retried by the caller, we always resume at α1. For a 2-ucall clause retried by the caller, always at α0. We never need to jump to α2 on re-entry from an external caller's β.

**Therefore the correct fix is simple:** on re-entry decode, always jump to `α_{max_ucalls - 1}` (the second-to-last ucall) with `slot_{max_ucalls-1}` pre-loaded, and set all other slots correctly. γ_{max_ucalls-2} (the one that would zero slot_{max_ucalls-1}) is bypassed. γ_{max_ucalls-1} still runs after α_{max_ucalls} (last ucall), but it doesn't zero any prior slots.

Actually more precisely: the caller retried this predicate because its β_{last} fired. That β retried α_{last-1}. So from the callee's perspective, we're entering this predicate fresh at the clause entry (c_α) with start=sub_cs. Inside this predicate, the re-entry decode must set up to resume at α_{ucall_to_retry} which is determined by which level the sub_cs encodes.

**Simplest correct implementation for the common case:**

```c
/* Re-entry: jump past γ0..γ_{K-1} slot-zeroings by jumping to αK directly */
/* For 3-ucall clause: if slot_1 > 0, jump to α1; else jump to α0 */
/* Emitted at compile time as runtime check: */
for (int _ji = max_ucalls - 1; _ji >= 1; _ji--) {
    A("    cmp     dword [rbp - %d], 0\n", UCALL_SLOT_OFFSET(_ji));
    A("    jne     pl_%s_c%d_α%d\n", pred_safe, idx, _ji);
}
A("    jmp     pl_%s_c%d_α0\n", pred_safe, idx);
```

This replaces the current unconditional `jmp α0` at the end of the re-entry decode.

### Key emitter locations (`emit_byrd_asm.c`)

| What | Approx line |
|------|-------------|
| Clause-entry mark, slot zeroing | ~5753 |
| Body label + `UCALL_MARK_OFFSET(0)` mark | ~5800 |
| Re-entry decode → `jmp α0` to fix | ~5840 |
| γN recompute + slot zeroing | ~6837 |
| βN unwind + retry | ~6820 |
| γ return | ~6850 |

### Gate tests (recreate each session — /tmp doesn't persist)

```bash
cd snobol4x && make -C src -s
build_run() {
  ./sno2c -pl -asm "$1" -o /tmp/t.asm &&
  nasm -f elf64 /tmp/t.asm -o /tmp/t.o &&
  gcc -no-pie /tmp/t.o src/frontend/prolog/prolog_{atom,unify,builtin}.o -lm -o /tmp/t &&
  timeout 8 /tmp/t
}
# Passing: naf.pro alldiff.pro minimal2.pro retry2.pro
# Target: queens_4.pro (find(4,Q) with self-contained numlist/permutation/safe)
# Expected: [2,4,1,3]
```

---

## Milestone Table

| ID | Description | Gate | Status |
|----|-------------|------|--------|
| M-PJ-X64-1 | Multi-clause dispatch | tak/nreverse/qsort PASS | ✅ `8843d71` |
| M-PJ-X64-2 | Arithmetic (is/2, comparisons) | times10/log10/ops8 PASS | ✅ `8843d71` |
| M-PJ-X64-3 | \+ / \= / multi-ucall backtrack | naf/alldiff/crypt/sendmore/queens PASS | 🔲 WIP `a051367` |
| M-PJ-X64-4 | List builtins (member/append) | nreverse/qsort/flatten PASS | 🔲 |
| M-PJ-X64-5 | Timing grid ≥15/31 vs SWI native | BENCH-prolog-x64.md committed | 🔲 |
