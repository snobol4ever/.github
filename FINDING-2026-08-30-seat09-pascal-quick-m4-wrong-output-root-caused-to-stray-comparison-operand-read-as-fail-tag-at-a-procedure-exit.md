# FINDING: quick.pas's m4 wrong-output (10414 vs 15505) is root-caused — a guarded recursive
# call's ω-port, wired directly onto the enclosing procedure's own γ exit, forwards a raw leftover
# comparison operand as if it were the call's DESCR_t return value; when that raw integer's low
# byte happens to equal 0x68 (DT_FAIL=104 decimal), the caller misreads a successful, ordinary
# return as a failure and cascades a spurious ω all the way up the live call chain, abandoning
# every not-yet-made recursive call above that point.

Row: `pascal-quick-m4-wrong-checksum-crash-masked` (seat09, FLEET-16, claimed cold via `s4e_msg.sh
claim` after `next` served the sibling row `pascal-m4-site1-forloop-backedge-64byte-excess` and its
own current NEXT block turned out to be carrying this exact investigation informally, without
realizing this row already existed, unclaimed, since its 2026-08-29 mint). Recorded here so the
next actor on either row has the full mechanism rather than a re-characterization.

## 0. Baseline, fresh

Pulled all 3 repos, `make pristine` at SCRIP `ae078681` (later confirmed the very next pulled
commit, `09186866`, touches only Icon/Raku/cset code — `git log -p` read directly, not assumed —
irrelevant to this witness). `RT_OPT=-O0` confirmed. `SCRIP_ZD=0` (kills the zd_plan optimizer
entirely) recompiled and re-run: **byte-identical wrong output** — this is not zd_plan/Site-1's
own mechanism (that row's `tests-consolidate-icon`-style sibling reasoning does not transfer here;
confirmed by direct measurement, not inference).

```
m3 (--run):      -50000 / 15505   <- matches quick.ref
m4 (--compile):  -50000 / 10414   <- wrong, rc=0, no crash
```

## 1. It's a permutation, not corruption — narrows the search enormously

Instrumented a scratch copy of `quick.pas` (not committed; lives only in this session's scratchpad)
to print the full 500-element sorted array in both modes. `sort -n` on both outputs is
**byte-identical** — mode 4 has the exact same 500 values as mode 3, just not fully sorted. This
rules out value corruption, garbage reads, and register-clobbering-style stack bugs as the
mechanism, and points at **quicksort's recursion simply stopping partway through** rather than
computing a wrong value anywhere.

## 2. Minimal repro: N=120 diverges with 16 diff lines (vs 648 for N=500)

Swept `srtelements` (10/20/30/50/80/100/120/150/200/300) with the RNG otherwise unchanged. Result
is **non-monotonic** — 120 and 200 diverge, the sizes on either side of each don't — consistent
with a **data-dependent coincidence**, not a size or depth threshold (confirmed below: the same
qsort call that succeeds at max recursion depth 13 earlier in the very same run is not where this
manifests; the failure shows up at depth 9, well short of the run's own maximum). At N=120 elements
**106–120 are scrambled (same 15 values, wrong order), 1–105 are byte-identical to `.ref`.**

## 3. Ground truth without needing to trace mode 3's symbol-less JIT slab

Wrote a direct Python transliteration of the exact algorithm (RNG, Hoare partition, recursive
boundaries) and logged every `(l, r)` call in traversal order. Its final sorted output is
byte-identical to mode 3's (confirmed the values column, not the whitespace-padded columns, which
differ cosmetically between `writeln`'s formatting and Python's — a first diff attempt on this
false-flagged every line before the padding was stripped). This sim is now the reference oracle
for the call sequence — mode 3 itself was never traced (no static symbols in its sealed-slab JIT
output; not attempted).

## 4. GDB trace of every qsort entry's own (l, r), mode 4 only

Broke at `n0_var_bx` (qsort's entry point after `rt_icn_zframe_args_install`, confirmed via `nm` —
the label carries a literal Greek α and GDB's charset warning on it is cosmetic, not a resolution
failure: `nm` shows `n0_var_bx`/`n0_var_α`/`qsort_α_body` all resolve to the identical address).
Auto-continuing breakpoint logging `*(long*)($rsp+24)` (l) and `*(long*)($rsp+40)` (r) at every hit:
**93 total invocations in mode 4 vs 105 in the ground truth — exactly 12 short, and the 12 missing
calls are exactly the ones covering [106,120]** (`106 107`, `108 120`, `108 115`, `108 110`,
`108 109`, `111 115`, `111 112`, `114 115`, `116 120`, `116 119`, `117 119`, `117 118` — all present
in the sim, none in the m4 trace). The first 93 calls in each trace are line-for-line identical.

## 5. Localizing the exact transition, GDB-confirmed

The 105th ground-truth call is `qsort(1,120)`'s deep-left descendant chain
`(102,107)→(102,105)→(103,105)→(103,104)`, and the very next ground-truth call is `(102,107)`'s
**own second recursive call**, `qsort(106,107)` (guarded by `if ii<r`). Set a one-shot breakpoint
at qsort's entry conditioned on `l==102 && r==107`, captured `$rsp` into a GDB convenience variable
at that exact frame, then a second breakpoint at `n66_var_bx` (the code immediately following
`(102,107)`'s own first recursive call, i.e. exactly where it would read `ii`/`r` back out to check
its second guard) conditioned on `$rsp` matching that saved value.

**Entry to `(102,107)`'s frame fires once, as expected. The return-to-checkpoint breakpoint never
fires at all** — confirmed over the whole run, not a timing artifact.

## 6. What happens instead: an ω cascade, one full stack frame at a time

Traced the two `jmp *rcx` epilogue instructions shared by every recursive call site
(`qsort_γ`@`0x4031dd` and `qsort_ω`@`0x4031f3` in this specific binary) from the moment `(102,107)`
is entered. Sequence observed (armed only after entry, first 8 hits):

```
[1] GAMMA  -> 0x402cf2   rsp=...9940   (an n65_call-site continuation: (103,104)'s own leaf return)
[2] OMEGA  -> 0x4030c4   rsp=...9fb0   (n71_call-site's own ω continuation)
[3] OMEGA  -> 0x402d2a   rsp=...a620   (n65_call-site's own ω continuation)
[4] OMEGA  -> 0x4030c4   rsp=...ac90
[5] OMEGA  -> 0x4030c4   rsp=...b300
[6] OMEGA  -> 0x4030c4   rsp=...b970
[7] OMEGA  -> 0x4030c4   rsp=...bfe0
[8] OMEGA  -> 0x4030c4   rsp=...c650
```

Each successive `rsp` is exactly **+0x670 (1648 = 1632-byte frame + 16 bytes of pushed
continuations)** above the last — this is the ω propagating **upward through one full qsort stack
frame per hit**, i.e. every ancestor frame from the point of origin up to (at least; logging was
capped at 8) 7 levels above is independently taking its own "my callee failed" branch and
re-failing itself in turn, rather than continuing normally. `(102,107)` itself is exactly the
second frame in this chain (`[2]`, immediately after `(103,104)`'s own leaf return at `[1]`) — this
is why it never reaches its own second-guard check: the very first thing that happens after its
first recursive call returns is that its own frame ALSO takes the ω branch.

## 7. Root cause, read from the emitting template and the runtime source, not guessed

`0x402ecc` — the `ii<r` fast-integer-path comparison instruction — disassembles to `cmp
%rcx,%rax; jge 4031c3 <qsort_γ>` (this exact site's earlier log entry, `l=103 r=104 ii=104
r_cmp=104`, is `(103,104)`'s **own** guard check: `ii(104) >= r(104)` is true, so it takes this
`jge` **directly to `qsort_γ`, with `rax` still holding the raw integer 104** — a leftover
comparison operand, not a DESCR_t).

- `src/templates/bb/bb_binop_relop.cpp:34-37` (the `IR_BINOP_TEST` fast-integer-path template):
  ```
  mov rax, FRQ(op_sa+8)          ; ii's raw value
  mov rcx, FRQ(op_sb+8)          ; r's raw value
  cmp rax, rcx
  x86_omega(...)                  ; jcc straight to this test node's wired ω port
  ```
  `x86_omega(mnem)` (`x86_asm.h:532`) is a pure control-flow primitive — `x86_jcc(mnem,
  X86P_OMEGA)` — it has no notion of "return value" and is not supposed to. **The template never
  sets up a value in `rax`/`rdx` before this jump because normally there IS no value to set up: an
  `if`-guard's failure is usually just a goto to more statements.** The hazard is specific to what
  the wiring puts on the other end of that ω port.
- Because `if ii < r then qsort(ii, r)` is qsort's **last statement**, this test node's ω port is
  wired directly onto `qsort`'s own success exit, `qsort_γ`. And `qsort_γ`'s own body
  (`rt_proc_call_epilogue_γ`, `src/runtime/rt/rt.c:1327-1331`) is `{ rt_k_level--; return frame0; }`
  — it unconditionally **trusts** that whatever is in `rax`/`rdx` (via the `mov rdi,rax; mov
  rsi,rdx` immediately before the jump into it — see any `n*_call_bx`'s `.Lcall_α_*_3` block) is
  already a valid DESCR_t. It is not, here — it is the raw comparison operand.
- The caller (whichever frame's `n65_call`/`n71_call` site made this specific recursive call) reads
  that forwarded value back via the shared post-call convention (`.Lcall_α_*_29: cmp al,104; je
  qsort_ω`), and **`DT_FAIL = 0x68` (`src/ir/descr.h:27`) is 104 decimal** — an exact byte match on
  a value (`ii`/`r` here) that is a completely unremarkable, ordinary loop-bound integer for this
  witness. The caller has no way to distinguish "a genuine DT_FAIL descriptor" from "a raw int64
  that happens to be 104" — both are just a low byte of 0x68 in `al`.
- Every ancestor above that repeats the identical mistake: each one also reaches its own procedure
  or call-continuation boundary having received (from `mov rdi,rax` at the ω/γ label it landed on)
  the SAME poisoned low byte, so each one also takes the `cmp al,104; je qsort_ω` branch — this is
  the observed one-frame-per-hit cascade in §6, and it is not a separate bug: it is the SAME defect
  re-triggering, correctly by the letter of a convention whose precondition was violated once, at
  the origin.

## 8. Why this is data-dependent, not size- or depth-dependent

The collision requires only that **some leaf (or any test whose ω/γ port lands undecorated on a
procedure exit) hold a raw comparison operand whose low byte is exactly 0x68 (104)** at the instant
it takes that jump. `ii`/`jj`/`l`/`r` here are ordinary sort-index integers in `[1,500]`, so roughly
1-in-256 of the *specific* leaf calls that happen to reach a procedure exit this way will trigger
it — consistent with the observed non-monotonic pattern across array sizes (§2: 120 and 200 hit it,
the sizes bracketing each do not) and with `bubble.pas` (a different algorithm, different leaf
shapes) not needing this mechanism to independently crash via Site-1's own, unrelated defect.

## 9. What this does NOT establish, stated plainly

- **Not independently confirmed on mode 3.** The emitting template (`bb_binop_relop.cpp`) carries
  no `MEDIUM_*`/mode-conditional arm that this session found, so the SAME instructions almost
  certainly execute in mode 3 too — but mode 3's JIT slab has no static symbol table (confirmed
  attempting exactly this in a sibling investigation this session), and this session did not
  attempt an alternative mode-3 tracing method. The leading hypothesis is that mode 3 has the
  identical latent hazard but mode 3's own register/slab layout simply does not happen to leave a
  0x68-tailed value in `rax` at any of its own procedure-exit-wired test nodes for this specific
  program — i.e. **this is plausibly a mode-agnostic hazard that mode 4 happens to expose here**,
  not a mode-4-specific defect. Not verified; flagging the distinction because it changes where a
  fix would need to be scoped.
- **Scope beyond this witness is not audited.** `x86_omega`/`x86_alpha`/`x86_gamma`/`x86_beta` are
  generic port-wiring primitives used by every language this compiler targets; ANY test/comparison
  node whose port is wired directly onto a procedure-level γ/ω exit (rather than onto another
  statement) is structurally exposed to the same hazard, in principle, in any frontend. This
  session characterized exactly one witness and did not attempt a broader census.
- **Not attempting a fix.** This project's own recent history on the immediately adjacent
  mechanism (`bb_call_proc_staged.cpp`/`zd_plan`, this row's own sibling
  `pascal-m4-site1-forloop-backedge-64byte-excess`) already produced one fix that "CURES PASCAL AND
  REGRESSES SNOBOL4" and had to be reverted (hq_P, 2026-08-29, same task file) precisely because the
  blast radius of a shared port-wiring/calling-convention change was under-measured against the
  graded population rather than a convenient sample. A candidate direction (make procedure-exit γ/ω
  landing sites defensively normalize `rax`/`rdx` to a valid void-success DESCR_t rather than
  trusting the incoming value, OR require every port-wiring pass to never land a bare
  comparison-node port directly on a procedure exit without an intervening normalization node) is
  named here for whoever picks this up, not evaluated or implemented.

## 10. DONE-WHEN, made runnable (the row's own header said this was still owed)

```
cd "$S4E_HOME/SCRIP" && make pristine && \
Q="$S4E_HOME/corpus/benchmarks/pascal/quick.pas" && W=$(mktemp -d) && \
./scrip --compile --target=x86 "$Q" < /dev/null > "$W/q.s" && \
as "$W/q.s" -o "$W/q.o" && gcc -no-pie "$W/q.o" -Lout -lscrip_rt -Wl,-rpath,out -lm -o "$W/q_bin" && \
echo 1 | "$W/q_bin" | tail -1 | tr -d ' ' | grep -qx 15505 && echo PASS || echo FAIL
```
Currently prints `FAIL` (mode 4 prints `10414`). `quick.pas` under mode 3 and the real oracle both
already pass; this command is mode-4-only by design, matching this row's own GOAL text.

## THIS ROW

Not claiming further this pass — the mechanism is now precisely, dynamically confirmed at the
instruction level and the fix direction is named but genuinely undesigned (same "reserved,
shared-node risk" shape as this row's sibling). ⚠️ **This is a DIFFERENT mechanism from
`calling-convention-depth-tracked`'s own charter** (that row is about `zd_plan`'s pop-accounting
depth model; this is about the γ/ω port-wiring value contract — both live in the same
flat/frame-call neighborhood but are independent defects, not verified to share a fix). Not
presuming an owning row exists yet for this specific class — mailed hq_C to triage/route (mint a
new row, or fold into an existing one if hq_C knows of a better fit) rather than guessing, and
rather than proposing a unilateral fix on a mechanism this codebase has already been burned by once
this session's own history (§9). Releasing (`unclaim`).
