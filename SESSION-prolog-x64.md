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
| **Prolog x64** | `PX-1` | `8843d71` | M-PJ-X64-3 (\+ inline emission) |

**M-PJ-X64-1 ✅ M-PJ-X64-2 ✅** committed at `8843d71`.
- tak/nrev/qsort PASS, times10/ops8/log10 PASS.

**Blocker for M-PJ-X64-3:** `\+` (negation-as-failure) emitted as undefined user-call
`pl__bs__pl__sl_1_r`. Two-part fix in `src/backend/x64/emit_byrd_asm.c`.

## CRITICAL NEXT ACTION — M-PJ-X64-3

### Part A — Add `\+` (and `\=`) to the four builtin filter lists

Lines **5736, 6657, 6733, 6761** each end with:
```c
strcmp(gn,"compound")==0) continue;
```
Change each to:
```c
strcmp(gn,"compound")==0||strcmp(gn,"\\+")==0||strcmp(gn,"\\=")==0) continue;
```
This prevents `\+` and `\=` being counted as user-calls (ucall_seq stays correct).

### Part B — Inline `\+` emission in body goal dispatcher

After the `fail/0` handler (~line 5878), add a `\+` block. Pattern (use a frame temp slot
for the NAF trail mark — `UCALL_MARK_OFFSET(ucall_seq)` or a dedicated scratch slot):

```c
if (strcmp(fn, "\\+") == 0 && garity == 1) {
    EXPR_t *inner = goal->children[0];
    const char *ifn = (inner && inner->sval) ? inner->sval : NULL;
    int ia = inner ? (int)inner->nchildren : 0;
    int nuid = pl_next_uid();
    /* save trail mark to a temp stack slot */
    A("    call    trail_mark_fn\n");
    A("    mov     [rbp - %d], eax\n", NAF_MARK_SLOT);
    /* call inner goal → result in rax (-1=fail, >=0=succeed) */
    if (ifn && strcmp(ifn,"fail")==0) {
        A("    mov     eax, -1\n");               /* \+ fail → succeed */
    } else if (ifn && strcmp(ifn,"true")==0) {
        A("    mov     eax, 0\n");                /* \+ true → fail */
    } else {
        /* emit user-call for inner goal */
        char isf[256]; snprintf(isf,sizeof isf,"pl_%s",pl_safe_arity(ifn,ia));
        /* build args, call isf_r with start=0 */
        ...
        A("    call    %s_r\n", isf);
    }
    /* unwind trail regardless */
    A("    push    rax\n");
    A("    lea     rdi, [rel pl_trail]\n");
    A("    mov     esi, [rbp - %d]\n", NAF_MARK_SLOT);
    A("    call    trail_unwind\n");
    A("    pop     rax\n");
    /* invert: inner succeeded (>=0) → \+ fails */
    A("    cmp     eax, -1\n");
    A("    jne     %s\n", next_clause);   /* \+ fails → try next clause */
    /* inner failed → \+ succeeds → fall through to γ */
    continue;
}
```

### Part C — Inline `\=` (not-unifiable)

After the `=` (unify) handler, add:
```c
if (strcmp(fn, "\\=") == 0 && garity == 2) {
    /* save mark, call unify, unwind, invert */
    /* if unify succeeded → \= fails (jump next_clause) */
    /* if unify failed   → \= succeeds (fall through) */
}
```

### Gate tests

```bash
# naf.pl: \+ fail → naf_ok, \+ (X=Y) with X≠Y → neq_ok
# alldiff.pl: all_diff([1,2,3]) → ok1, all_diff([1,2,1]) → ok2
# Then: crypt / sendmore / queens_8 from SWI bench suite
```

### Known secondary bug

queens_8 outputs `[]` not a valid solution. Suspected: multi-ucall var aliasing — when
a clause with 3+ user-calls backtracks, var bindings from earlier ucalls may be incorrectly
preserved or lost during trail unwind. Investigate after \+ lands.

---

## Milestone Table

| ID | Description | Gate | Status |
|----|-------------|------|--------|
| M-PJ-X64-1 | Multi-clause dispatch | tak/nreverse/qsort PASS | ✅ `8843d71` |
| M-PJ-X64-2 | Arithmetic (is/2, comparisons) | times10/log10/ops8 PASS | ✅ `8843d71` |
| M-PJ-X64-3 | \+ / \= / multi-ucall backtrack | crypt/sendmore/queens_8 PASS | 🔲 |
| M-PJ-X64-4 | List builtins (member/append) | nreverse/qsort/flatten PASS | 🔲 |
| M-PJ-X64-5 | Timing grid ≥15/31 vs SWI native | BENCH-prolog-x64.md committed | 🔲 |
