# FINDING: `geddump.icn`'s Error-3 `arr` corruption traced to a specific producer — a stack-slot collision, not random garbage

**Who/when:** seat07, 2026-08-29, `icon-n2-recursive-generator-per-activation-storage` row, extending
seat16's `FINDING-2026-08-29-seat16-geddump-error3-gdb-confirmed-garbage-descr-t-plus-a-missed-selfrec-branch.md`
(which gdb-localized the crash to `subscript_get` on a `DESCR_t` with invalid type tag 64 and unreadable
pointer `0x70`, but did not trace where that value came from). This finding traces it one level further:
**the exact producer of the corrupted value, and why it looks like a slot collision rather than
uninitialized memory.**

## Reproduction (unchanged from seat16, re-confirmed on a fresh pristine build post the apply-call-to-generator cure, `42a6260f`)

```
SCRIP_ICN_N2_SELFREC=1 ./scrip corpus/benchmarks/icon/geddump.icn < <(head -200 corpus/benchmarks/icon/geddump.dat)
** Error 3 in statement 0
   Erroneous array or table reference
```

The recent `bb_call_value.cpp` N-2 apply-call fix (this row's own former sibling blocker) does **not** change
this outcome — geddump.icn's flow hits Error-3 before it ever reaches the apply-call site that fix addressed.

## The source construct

```icon
procedure gedload(f); #: load GEDCOM data from file f
   local line, lnum, r, curr;
   local root, id, fam, ind;      # <- id, line 149
   ...
   id := table();                  # line 153
   ...
   while line := trim(read(f), WHITESPACE) do {
      ...
      id[\r.id] := r;              # line 175 -- id populated inside this loop
      ...
   };

   every r := gedwalk(root) do     # <- gedwalk is THIS ROW'S self-recursive generator
      r.ref := id[r.data];         # line 182-183 -- id READ inside the every-loop body
   ...
```

`id` is a local of `gedload`. It's built up in an ordinary `while` loop (lines 157-180), then **read inside
the body of `every r := gedwalk(root) do ...`** (lines 182-183) — a loop whose control flow is driven by
`gedwalk`, the exact self-recursive generator this row's `SCRIP_ICN_N2_SELFREC` mechanism exists to give
per-activation storage to. Every iteration of this `every` loop resumes across a `gedwalk` suspend point.

## gdb + asm trace: `arr`'s producer, not just its corrupted value

Breaking at `subscript_get` entry (`src/runtime/pattern_match.c:222`) on the 200-line reproducer:

```
(gdb) print arr
$1 = {v = 64 '@', mod_op = 224 '\340', src_node = 36671, slen = 32767,
      {..., p = 0x70, arr = 0x70, tbl = 0x70, ...}}
#0  subscript_get (arr=..., idx=...) at pattern_match.c:222
#1  c_rt_subscript_var (base=..., idx=...) at pattern_match.c:1473
#2  n227_subscript_bx () at <geddump>.s:2924
#3  0x0000000000000000 in ?? ()      <- return address also gone, not just arr
```

Beyond seat16's original observation (tag 64, pointer `0x70`): **`src_node = 36671` (`0x8F3F`) matches a
byte-fragment of the live stack pointer at the crash (`rsi = 0x7fff8f3fe040`** — bytes `8f 3f` appear at the
matching position). This is a strong sign `arr` was read from a stack slot holding an unrelated pointer-typed
value, not simply never-initialized zero/pattern memory.

Reading the emitted `.s` around the call site (`n227_subscript_bx`, matching RULES.md's ASM-DIFF-FIRST order
— read the assembly before reaching for more gdb):

```asm
n224_var_ref_α:  mov  r11, 154
                 mov  rax, 4294967336        ; a var-ref tag+encoding, NOT an array/table value
                 lea  rdx, [rsp + 2624]      ; address of a LOCAL slot (r.ref's storage, the ASSIGNMENT TARGET)
                 mov  qword ptr [rsp + 384], rax   ; <-- writes the SAME slot n227 later reads as `arr`
                 mov  qword ptr [rsp + 392], rdx
                 jmp  n225_var_α
n225_var_α:      ...  ; loads r.data's VALUE (unrelated offsets, rsp+2672/2680) into rsp+416/424
n226_field_get_α: ... ; dat_field_get("data", ...) -> rsp+400/408  (becomes `idx`)
n227_subscript_α: mov rdi, [rsp+384]   ; <-- `arr`: still holding n224's var-ref, nothing rewrote it
                  mov rsi, [rsp+392]
                  mov rdx, [rsp+400]   ; `idx`: r.data's value, correctly wired
                  mov rcx, [rsp+408]
                  call rt_subscript_var@PLT
```

**`n224_var_ref` computes `r.ref` as an assignment-target reference (an l-value: a tag plus a pointer into a
local slot) — that's the LHS of `r.ref := id[r.data]`.** Its result is stored at `[rsp+384]`/`[rsp+392]`.
**Nothing between `n224` and `n227` writes to that same slot again** — so when `n227_subscript` (which
computes the RHS's `id[r.data]`) loads its `arr` operand from `[rsp+384]`/`[rsp+392]`, it reads back
`r.ref`'s own leftover var-ref value, not `id`'s table value. `id` never appears to get loaded into this
call's `arr` argument at all in this compiled sequence.

## What this is NOT

- Not the same mechanism as `rung36_jcon_genqueen`'s two root causes (seat12's FINDING) — those are about
  the self-recursion depth counter and the sibling-generator reservation formula. This is upstream of both:
  `id`'s value is simply not present in the slot the subscript reads, independent of depth or reservation size.
- Not proven to be an N-2-specific bug — `subscript_get`'s garbage input could in principle come from any
  slot-allocation mismatch. But the SHAPE (a variable local to the generator-iterating procedure, read
  across an `every ... do` loop body driven by a self-recursive generator) is exactly the class of case
  `SCRIP_ICN_N2_SELFREC`'s per-activation carving exists to handle — `id` needs to survive across `gedwalk`'s
  suspend/resume boundary the same way any per-activation state does, and if the region N-2 carves for
  `gedwalk`'s own frames overlaps or aliases `gedload`'s pre-existing local-variable slots (rather than being
  additively reserved alongside them), that would produce exactly this symptom: a caller-local silently
  overwritten by callee per-activation bookkeeping.

## Not attempted here

No fix. This row's own GOAL is explicit that the storage-location design (where do per-activation records
live, and how do they compose with an enclosing procedure's own locals) is Lon/hq territory, not a unilateral
call — and this finding, if the collision hypothesis is right, is really a question about how N-2's region
carving composes with a HOST procedure's own frame layout, which is squarely that design question, not a
narrow independent bug like genqueen's root cause 1.

## Suggested next step, not decided here

Confirm the collision hypothesis directly: dump `icn_gen_host_slice`'s (or whichever function ultimately
decides `gedload`'s own frame layout when it hosts a self-recursive generator call) computed offsets for
`gedload`'s locals (`id` specifically) versus the region reserved for `gedwalk`'s per-activation storage, and
check whether they're additive (non-overlapping) or whether `gedwalk`'s carve can land inside/adjacent to a
host local in a way that a later host read observes stale generator state instead of its own variable. This
is a concrete, bounded check — narrower than the general per-activation storage design question, and might
usefully inform it either way.
