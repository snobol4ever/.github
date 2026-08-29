# FINDING — 2026-08-29 seat09 (`/home/claude09`) — queue row `fuzz-nondeterminism-rootcause`

# CLUSTER A IS s188's "M4 — BLOB-ROAD FENCE/DEFER ADJACENCY", PREVIOUSLY CHARACTERISED BUT NEVER
# ROOT-CAUSED — AND THE CRASH IS A WILD INDIRECT JUMP, NOT AN UNINITIALISED-VALUE COMPARISON LIKE
# CLUSTER B. TRACED TO INSTRUCTION LEVEL: `PAT$N_res`'s BACKTRACK-REENTRY FRAME RECONSTRUCTION USES
# A HARDCODED STACK OFFSET THAT DOES NOT MATCH THE ACTUAL PUSH SEQUENCE ON AT LEAST ONE PATH.

**WATERMARK:** SCRIP HEAD `4407a299`, pulled clean via `git pull --rebase` at session start, `make`
clean (not `make pristine` — this session did not land a source change, so the HQ-27 pristine-before-
verdict bar does not apply; anyone landing a fix from this FINDING must still `make pristine` first).
Working tree clean throughout — **no source files touched this session, no candidate fix attempted.**

## 0. WHY THIS ROW, WHY CLUSTER A

`fuzz-nondeterminism-rootcause` has had 6 prior sessions (hq_B, seat02×2 policy-only, seat13×3, seat11,
seat16) — all on **Cluster B** (`fz_red_m1b_arbno_defer_blob`, `fz_segv_24`). Root cause there is deep
and precisely pinned (`resume_carrier_ok`'s tier-1 reuses `zd_k(m)!=0` — "does this node need a frame
slot" — as a proxy for "is this node a backtrack-reentry hazard", which is the wrong question for at
least two op kinds); five candidate fixes were tried and rejected, each curing Cluster B while
regressing `crosscheck/patterns.sno`'s `143_pat_regex_quantified_class`/`145_pat_left_assoc_via_arbno_fence`.
The row's own LANE NOTE routes the remaining design work to hq_C. **Cluster A** (`fz_segv_09`,
`fz_red_m4a_blob_alt_fence_defer`, `fz_red_m4b_blob_defer_fence`) had **zero investigation** across
all 6 sessions — everyone converged on Cluster B. This session investigated Cluster A instead, on the
row's own explicit "cheapest question, largest branching factor" advice (settle one-defect-or-two) and
because repeating a 7th empirical guess on Cluster B's already-exhausted candidate space, on shared
concurrently-built compiler internals, is not a responsible use of one more sitting.

## 1. CLUSTER A IS s188's M4, NOT A FRESH MYSTERY — THE CONNECTION WAS NEVER MADE EXPLICIT

`FINDING-2026-08-20-s188-the-eleven-fuzz-segvs-are-four-mechanisms-and-the-road-is-an-ingredient.md`
(seat4, row `fuzz-segv-batch`) classified the *original* 11 `fz_segv_*` witnesses into 4 mechanisms by
ablation. **Cluster A's own witness names carry the classification**: `fz_red_m4a_blob_alt_fence_defer`
and `fz_red_m4b_blob_defer_fence` are literally s188's own `fz_red_m4a`/`fz_red_m4b` reduced witnesses
for **"M4 — BLOB-ROAD FENCE/DEFER ADJACENCY"** (`fz_segv_09`, `fz_segv_15`, `fz_segv_19`, `fz_segv_02`).
s188's own words: *"the pattern must be reached through a stored pattern `*P` — a FENCE (or nested ALT)
adjacent to a defer inside it. The identical text written inline in the match statement is GREEN in all
four."* This is a real, previously-characterised mechanism that s188 explicitly **closed as
investigation-only** (*"the row closes investigation-only... lands no codegen change"*) — nobody has
root-caused the actual wild transfer since, across 9 days and (per this row's own history) at least 6
more sessions that never connected the dots. **Corollary for "one defect or two": Cluster A (M4) and
Cluster B (M1, `ARBNO(*G0)` blob-road) are s188's own two DIFFERENT, independently-ablated mechanisms.**
They are not proven unrelated at the *disease* level (see §5) but they are not the same specific bug.

## 2. REPRODUCTION AT HEAD, RAW (ASLR on) — STILL FLAKY, ALL THREE WITNESSES

Built via the exact `corpus_suite_harness.py compile_m4()` steps (`scrip --compile` → `gcc -c` →
`gcc ... -lscrip_rt -lm -lpthread`, PIE, matching the documented `-no-pie`-is-permanently-rejected
constraint). 5 raw runs each, current HEAD:

| witness | this session's 5-run sample |
|---|---|
| `fz_segv_09` | 5× SIGSEGV (rc=139) — within KEEP.md's documented flip set, this sample landed one-sided |
| `fz_red_m4a_blob_alt_fence_defer` | 3× SIGILL (rc=132) / 2× SIGSEGV (rc=139) — flip reproduced live |
| `fz_red_m4b_blob_defer_fence` | 3× SIGSEGV (rc=139) / 2× rc=0 clean exit — flip reproduced live |

Confirms KEEP.md's classification is still current at `4407a299`; nothing cured or worsened it since.

## 3. ⭐⭐⭐ THE MECHANISM, TRACED TO THE FAULTING INSTRUCTION — A WILD `jmp` THROUGH A REGISTER, NOT
## AN UNINITIALISED COMPARISON

**`gdb` reproduces `fz_segv_09` and `fz_red_m4a_blob_alt_fence_defer` 100% deterministically** (6/6 and
1/1 attempts respectively) — gdb disables ASLR for the debuggee by default, and both witnesses crash at
the *identical* address every time under it, which Cluster B's own prior sessions never got (Cluster
B's uninitialised-*value* signature needed valgrind's V-bits; Cluster A's crash is deterministic the
moment the address space stops moving, which is itself informative: **the garbage being jumped to is
ASLR-shaped stack content, not a genuinely-random uninitialised byte pattern**).

**valgrind's own diagnosis is the sharpest fact in this FINDING**, and it is a *different class* from
Cluster B's:
```
==...== Jump to the invalid address stated on the next line
==...==    at 0x1FFEFEFF68: ???
==...==  Address 0x1ffefeff68 is on thread 1's stack
==...==
vex amd64->IR: unhandled instruction bytes: 0x60 0xB0 0xF8 0x8 0x0 0x0 0x0 0x0 0x80 0x28
```
This is `memcheck`'s **control-flow** check, not its value-taint check — the program executed an
indirect jump/call whose *target address itself* is stack-resident garbage, and control landed inside
the stack trying to execute whatever bytes happen to be sitting there (hence the "unhandled instruction
bytes" — it isn't code, it's stale stack content). **Cluster B never showed this signature in any prior
session's valgrind output** — Cluster B's is `Conditional jump or move depends on uninitialised
value(s)`, a *comparison* reading taint, with the PC staying inside real code the whole time. These are
mechanically different valgrind checks catching mechanically different bugs.

**Traced under `gdb` (ASLR off, so addresses are stable and this is exactly reproducible) on
`fz_segv_09`, witness source:**
```
G0 = POS(0)
P  = FENCE((FENCE(POS(2)) *G0 | LEN(3)))
'a+a+a' POS(0) *P    :S(OK)F(NO)
```
`*P` compiles to `n28_match_defer_bx`, whose α port resolves the deferred pattern's compiled entry
point via `dtp_fn_of()`/`rt_defer_xpat_dtp()` into `rax`, pushes two continuation addresses (this box's
own success/failure resume labels), then transfers control:
```asm
n28_match_defer_α:  ... (resolve rax = deferred pattern's entry) ...
    mov    $0x0,%r8d
    lea    0x14(%rip),%rcx        # -> .Lmatch_defer_α_61_5  (failure continuation)
    push   %rcx
    lea    0x3(%rip),%rcx         # -> .Lmatch_defer_α_61_4  (success continuation)
    push   %rcx
    jmp    *%rax                  # <-- transfers into the deferred pattern's compiled body
```
**Breaking exactly here (`n28_match_defer_bx+0xcd`) and inspecting the live state (not inferred):**
`rax = 0x555555555278`, which `gdb`'s own `info symbol` resolves to **`PAT$1_α_body`** (aka
`FN__PAT$1`, the compiled body of `(FENCE(POS(2)) *G0 | LEN(3))`, `P`'s own alternation) — **this first
jump is correct**, not the bug. `continue`-ing from there, the program crashes with SIGILL at
`0x7ffffffedf7a` — an address in the `0x7ffffffed...` range, **the same range as `rsp`/`rbp` at that
moment**, i.e. on the stack, matching valgrind exactly. At the instant of the crash, `rax` holds
`0x555555555549` — `info symbol` resolves this to **`PAT$1_res`**, a *different* label than the one
that was jumped to a moment before. **So sometime after entering `PAT$1_α_body`, something loaded
`PAT$1_res`'s address into `rax` intending a `jmp *rax` there, and the actual control transfer that
executed went to the stack instead.**

**Reading `PAT$1`'s emitted assembly (`objdump -d`, no gdb needed for this part — ASM-DIFF-FIRST step
2) names the specific asymmetry:**
```asm
                                  ; PAT$1's OWN prologue (entered via jmp, not call):
FN__PAT$1:
    push   %rbp                  ; saves CALLER's rbp (n28_match_defer's rbp)
    mov    %rsp,%rbp
    sub    $0x48,%rsp
    mov    0x8(%rbp),%rcx        ; = the caller's pushed "success continuation" (.Lmatch_defer_α_61_4)
    mov    %rcx,-0x8(%rbp)       ;   saved to local slot -8
    mov    0x10(%rbp),%rcx       ; = the caller's pushed "failure continuation" (.Lmatch_defer_α_61_5)
    mov    %rcx,-0x10(%rbp)      ;   saved to local slot -0x10
    ...
                                  ; PAT$1's SUCCESS exit (its own internal alternation matched):
PAT$1_γ:
    mov    %rcx,[rbp-0x10]       ; rcx = saved failure_cont
    push   %rbp                  ; push PAT$1's OWN rbp            <-- (1)
    push   %rcx                  ; push failure_cont                <-- (2)
    mov    %rcx,[rbp-8]          ; rcx = saved success_cont
    push   %rcx                  ; push success_cont                <-- (3)
    lea    %rax, [PAT$1_res]
    push   %rax                  ; push PAT$1_res's own address     <-- (4)
    mov    %rbp,[rbp+0]          ; restore CALLER's (n28's) rbp
    jmp    *%rcx                 ; jump to success_cont (n28's .Lmatch_defer_α_61_4) -- rcx still (3)
                                  ;   the 4 pushes (1)-(4) are LEFT ON THE STACK, uncollapsed by
                                  ;   n28's own success handler (.Lmatch_defer_α_61_4 does
                                  ;   `mov rsp,rbp; pop rbp; jmp n29_match_end_α` -- it resets rsp
                                  ;   to N28's OWN rbp, which is BELOW all 4 of PAT$1_γ's pushes,
                                  ;   silently abandoning them without popping)
                                  ;
                                  ; PAT$1's own RETRY/backtrack re-entry (invoked later IF a
                                  ; downstream element fails and asks P to try its next alternative):
PAT$1_res:
    mov    %rbp,0x18(%rsp)       ; reconstruct PAT$1's rbp from a HARDCODED offset [rsp+0x18]
    add    $0x20,%rsp
PAT$1_β:
    jmp    PAT$1_ω
```
`PAT$1_res`'s `[rsp+0x18]` is a **compile-time-fixed** offset, generated once per graph by
`codegen_flat_chain_body` (`emit.cpp:2668`, the shared driver for every pattern/procedure's α/γ/ω/β/res
label family — `lbl_res` at `emit.cpp:2682`, used at `emit.cpp:3245`/`3343`) — it encodes an assumption
about **how many words are on the stack, at what depth, at the moment something jumps to `PAT$1_res`.**
`PAT$1_γ`'s own exit sequence pushes exactly 4 words and then leaves via a DIFFERENT, sibling path
(`jmp *rcx` to the caller's success continuation) that does not consume them — meaning **whatever later
mechanism jumps to `PAT$1_res` to retry `P` is relying on a stack shape that the success path never
actually produces on its own; some intervening frame (n28's own retry logic, or a sibling box further
down the chain) is expected to have laid down exactly 3 words (0x18 = 3×8) *of the right kind* below
whatever `PAT$1_res` reads at `[rsp+0x18]` before jumping there.** This is precisely the "spelled twice"
/ "the road is an ingredient" family already named twice in this codebase's own history (§5) — a
retry-address computation and the actual runtime stack shape at the moment of retry are two different
facts, generated in two different places, and nothing enforces they agree for a two-deep-nested
BLOB-ROAD composition (`*P` whose own body contains an alternation that itself was entered via a
defer). **Not yet pinned to the exact SECOND site that lays down the mismatched stack shape** — that is
the next rung, not this session's (§6).

## 4. WHY THIS IS NOT A LANDABLE FIX TODAY, AND WHY NO CANDIDATE WAS ATTEMPTED

`codegen_flat_chain_body` (`emit.cpp:2668`) is the **single shared driver for every graph's α/γ/ω/β/res
label family and prologue/epilogue shape** — every pattern, every procedure, every language that lowers
through this box machinery. A stack-depth assumption bug here is not local to `fz_segv_09`'s shape; it
is a property of how `_res`-style retry re-entry is wired for *any* two-deep nested defer/alternate
composition, and Cluster B's own five rejected candidates are the standing proof that a plausible-
looking local patch to this neighbourhood regularly regresses `crosscheck/patterns.sno` or other
currently-green programs. Finding the SECOND site (what actually jumps to `PAT$1_res`, and whether its
own push sequence is wrong or `PAT$1_res`'s offset is wrong) needs the same disciplined,
witness-verified design work Cluster B's row already asks hq_C for — not a guess landed mid-session on
shared, concurrently-built compiler internals. **No source file was edited this session.**

## 5. THE DISEASE FAMILY, NAMED A THIRD TIME

This is now the **third** independent instance, in this codebase's own history, of "a continuation/
resume address is computed in one place and the actual runtime shape it will be read against is a
different, unenforced fact":
1. `FINDING-2026-08-20-s189-...-predicate-asks-about-the-body-when-the-hazard-is-to-the-right.md` —
   `arbno_frame_candidate`'s hazard scan looks at the ARBNO's own body when the hazard is to its right.
2. This row's own Cluster B — `resume_carrier_ok`'s tier-1 reuses `zd_k`'s "needs a frame slot" answer
   as a proxy for "is a reentry hazard", which is a different question the same answer cannot settle.
3. This FINDING — `PAT$N_res`'s hardcoded stack-offset retry re-entry assumes a push shape that
   `PAT$N_γ`'s own success exit does not, in fact, leave behind.
All three are RBP/RSP-relative retry-addressing bugs in different corners of the same "backtrack into a
previously-exited pattern activation" mechanism, none sharing an exact fix, all sharing the same
diagnosis shape. **A future design pass on either Cluster B or Cluster A should read the other's
FINDING first** — not because the fixes transfer, but because the FAILURE MODE (a retry contract
assumed, never verified against the actual generator) is now measured three times, and whoever designs
the eventual fix for either should make the retry contract explicit and checked (e.g. an assertion or a
generation-time consistency check that the pushed-word-count at every `_res`-reachable site matches what
`_res` reads) rather than fix the two known instances and leave a fourth waiting.

## 6. WHAT THE NEXT SESSION INHERITS

1. **Cluster A's crash is now root-caused to instruction level for `fz_segv_09`** (and, by the shared
   M4 ingredient list per s188, very likely the same mechanism for `fz_red_m4a`/`fz_red_m4b` — not
   individually re-traced this session, `fz_red_m4b_blob_defer_fence` specifically did NOT reproduce
   under gdb/no-ASLR in one attempt, consistent with KEEP.md's own PASS↔CRASH flip and worth re-checking
   under raw ASLR + valgrind rather than gdb for that witness specifically).
2. **The open question, stated precisely:** which site emits the `jmp`/`call` that expects
   `PAT$1_res`'s `[rsp+0x18]` contract, and does it push the wrong shape, or is `PAT$1_res`'s offset
   itself wrong for the two-deep composition (`*P` whose body's own ALT was itself reached via `P`'s
   own defer entry, i.e. no longer the one-deep case the offset was presumably generated for)? Read
   `codegen_flat_chain_body` (`emit.cpp:2668`) for how `lbl_res`'s reader offset is computed, find every
   OTHER site that `jmp`s to a `*_res` label (grep `_res` as a jump target across `emit.cpp` and the
   `bb_*.cpp` templates — not done this session, this is the concrete next step), and diff the pushed-
   word-count at each against what `_res` expects.
3. **Do the ASM-diff on the cheapest pair first, per RULES' own ASM-DIFF-FIRST**: this FINDING's
   `.sno` witnesses already isolate the shape; a same-token-different-adjacency GREEN sibling (per
   s188's own §2 method) would confirm the exact ingredient before touching `emit.cpp`.
4. **`fz_red_m4b_blob_defer_fence` needs its own gdb/valgrind pass under conditions that reproduce
   it** (this session's one gdb attempt landed on the clean-pass side of its flip) — do not assume it
   shares `fz_segv_09`'s exact site without checking; s188 only proved they share the M4 *ingredient*
   list (stored-pattern road + FENCE/defer adjacency), not necessarily one instruction.
5. This row's DONE-WHEN is **still 0/5** — this FINDING roots Cluster A's mechanism, it does not close
   any of the 5 witnesses (path (a) requires a landed, 3×-verified fix; none exists for any witness yet).

**Routed to hq_C**: `send hq_C fuzz-cluster-a-wild-jump-pat-res-stack-offset --stdin`, this FINDING's
summary, continuing the row's own established convention (Cluster B's three prior routes) rather than
opening a second unmanaged thread to the same owning lane.
