# FINDING — `demo02/wordcount.scrip` crashes because a proc's zframe resume-offset registers too late when a second polyglot section is present; the RSP==0x0/PIE connection is REFUTED

**seat07 · 2026-08-29 · SCRIP tree `54161efd` (no code changed) · row `polyglot-demo-empty-output-rc0`**

## Retracting the standing lead

The task's `## NEXT` (seat09, 2026-08-29) named this row's `RSP==0x0` / `jmp *(%rsp)` crash as
"named kin" to the closed row `m4-pie-vs-no-pie-changes-behaviour-not-just-signal`
(`ARCH-ENGINE.md` § "Mode-4 Link Mode"), on the reasoning that mode-3 always runs inside SCRIP's
own `-no-pie` driver process, so the same undiagnosed PIE-dependency might explain both.

**Directly tested and refuted.** Compiled `demo02/wordcount.scrip` under `--compile` (links PIE
by default, no `-no-pie`, per that row's own ruling) and ran the resulting binary:

```
$ ./scrip --compile demo02/wordcount.scrip > wc.s && gcc -c wc.s -o wc.o \
    && gcc wc.o -L out -lscrip_rt -lm -Wl,-rpath,out -o wc
$ ./wc
Segmentation fault (core dumped)   # rc=139, IDENTICAL to mode-3
```

It crashes **identically under both link modes**. The `fz_red_m2a_fence_cap_gen`/`fz_segv_10`
mechanism is specifically that a `*`-indirect continuation reads a *valid* address under PIE and
an *invalid* one under `-no-pie`, at the same program point, on the same object file — link-mode
IS the independent variable there. Here it is not: this is a different, self-contained defect
that happens to share a surface symptom (RSP holds an address a `jmp *(%rsp)`-shaped instruction
then dereferences). **Do not route this row's cure through that closed row's follow-up thread.**

## Localizing the actual trigger (bisection, not guessing)

The Prolog section run standalone (extracted verbatim from the `.scrip` file) is genuinely green:

```
$ scrip --run wordcount-prolog-section-alone.pl
9
```

This matches the task's original note #2 ("the SNOBOL4 section is correct in isolation") from the
other side — **the Prolog section is also correct in isolation.** The crash needs the polyglot
combination. Bisected which combination, by construction rather than by reading:

| content | 2nd section present | result |
|---|---|---|
| full Prolog (DCG + `phrase/3` + `string_chars`) | none | **PASS** (`9`) |
| full Prolog | trivial SNOBOL4 (`END` only) | **CRASH rc=139** |
| full Prolog | trivial Icon (1-line `main`) | **CRASH rc=139** |
| `main :- write(hello), nl.` (no DCG at all) | trivial SNOBOL4 | PASS |
| DCG + `phrase(words(Ws), [a,b,c], [])` (literal list, no `string_chars`) | trivial SNOBOL4 | PASS |
| `string_chars("ab c", Chars), write(Chars)` (no `phrase`) | trivial SNOBOL4 | PASS |
| `string_chars("ab c", Chars), phrase(words(Ws), Chars, [])` | trivial SNOBOL4 | **CRASH rc=139** |

**The trigger is exactly this 3-way interaction: DCG backtracking over a `string_chars`-derived
list, combined with the mere PRESENCE of a second top-level polyglot section — content and size of
that second section don't matter, an `END`-only SNOBOL4 block is sufficient.** Neither ingredient
alone crashes with either or both of the others' absence.

## ASM-DIFF-FIRST: the collapse

Emitted `.s` for the minimal PASS witness (Prolog-only) and the minimal FAIL witness (same Prolog
+ trivial SNOBOL4) via `scrip --compile -o`. The two are otherwise structurally identical (same
proc bodies, same call shapes) except at the choice-point retry site for `whites/2` (the DCG rule
`whites --> [C], { char_type(C, space) }, whites.`):

**PASS** emits the full retry sequence: `rt_pl_cp_pop3` → test → `rt_pl_zf_resume_set` →
`rt_arg_stage` ×N → `rt_proc_call_open_det` → push 3 continuation labels → `jmp rax`.

**FAIL** emits, at the identical logical site:
```asm
mov   rsp, qword ptr [rsp + 1240]
jmp   qword ptr [rsp]
```

This is not a new pattern — `bb_call_proc_staged.cpp:885` carries a comment on the *sibling* Icon
generator-resume arm (`icn_genframe2()`) naming this exact shape as already-cured-there: *"The old
form (mov rsp,[record]; jmp [rsp]) read a stack record the caller's own calls had already
scribbled over."* The Prolog choice-point-retry arm (`pl_zf_resume`, lines 834-883) has its own
correct, non-collapsing form (the `rt_pl_cp_pop3` sequence above) — but the FAIL witness isn't
reaching that arm at all for this call site; it's falling through to the generic fallback arm
(line 890-891) that still uses the old, already-known-broken form, because `icn_genframe2()` is
false for a Prolog program.

## Root cause, pinned via a temporary reverted probe

`pl_zf_resume` (`bb_call_proc_staged.cpp:715`):
```c
bool pl_zf_resume = g_emit.zframe_graph && !zf_resume && (zf_cont_off >= 0)
                     && !zls_g_icn_zframe_gen_by_name(_.op_sval);
```
`zf_cont_off` (`:713`) is `-1` unless `zls_g_resume_by_name(_.op_sval)` (`zeta_storage.c:750`, a
linear scan of a global `zg[]` table by proc name) finds a registered non-negative `resume_off`
for that proc.

Added a temporary `SCRIP_DEBUG_PLZF`-gated `fprintf` right after the `pl_zf_resume` computation,
printing `_.op_sval`, `zf_cont_off`, and `pl_zf_resume` for every call site, on both witnesses.
**Fully reverted before this FINDING was written — `git diff --stat` is empty; nothing committed.**

```
PASS (Prolog only):
  proc=word/3   zf_cont_off=1568  pl_zf_resume=1
  proc=whites/2 zf_cont_off=1024  pl_zf_resume=1      <- whites/2 already registered
  proc=whites/2 zf_cont_off=1024  pl_zf_resume=1
  ...

FAIL (Prolog + trivial SNOBOL4):
  proc=word/3   zf_cont_off=1568  pl_zf_resume=1
  proc=whites/2 zf_cont_off=-1    pl_zf_resume=0      <- NOT YET registered
  proc=whites/2 zf_cont_off=-1    pl_zf_resume=0      <- NOT YET registered
  proc=word/3   zf_cont_off=1568  pl_zf_resume=1
  proc=words/3  zf_cont_off=1648  pl_zf_resume=1
  proc=whites/2 zf_cont_off=1024  pl_zf_resume=1      <- NOW registered, same proc, same compile
  proc=words/3  zf_cont_off=1648  pl_zf_resume=1
```

**`whites/2`'s own `resume_off` is registered too late, only in the two-section case, for its
first two call-site emissions — and by its third call site in the SAME compilation run, it is
already correctly registered.** This is not a permanently-missing registration; it is an
ORDERING race between (a) whatever populates `zg[].resume_off` for a given proc (via
`zls_g_resume(g)`/`zls_g_find`, `zeta_storage.c:748`) and (b) codegen for that proc's own
call-sites — and the presence of a second polyglot section shifts that ordering for at least this
one proc (self-recursive, called from two sibling clauses of `words/3`), while leaving `word/3`
(also self-recursive, but with its clauses in the opposite order — recursive clause first, base
case second) apparently unaffected in this exact witness.

## Why not fixed here

`zeta_storage.c`'s `zg[]` registration is the zframe-offset bookkeeping every language sharing the
zframe/ζ-ACTIVATION-FRAME mechanism goes through (SHARED-NODE VERDICT SCOPE binds it). The obvious
patch shapes are the same kind of half-fix this task's own history already warned about for the
original trail bug (hq_C, 2026-08-28: *"the obvious shapes are all half-fixes that would pass
their own gate... it deserves its own sitting, starting from this data"*) — e.g. forcing eager
registration of every proc before any codegen begins could paper over this ordering race without
explaining why `whites/2` and not `word/3` is affected, and could interact with however Icon's own
generator registration (which this same table backs) is ordered. This needs someone to read
`zeta_storage.c`'s registration call sites (where `zls_g_resume(g)` actually gets invoked per
graph, and in what pass/order relative to per-language section processing) before proposing a
cure, not a patch to `pl_zf_resume`'s own boolean.

## Standing instruction for whoever picks this up

1. Start from `zeta_storage.c:748` (`zls_g_resume`) and its caller(s) in `scrip_ir.c:276-284` —
   find what triggers registration for a given graph and in what order relative to other graphs
   in the same compilation unit, single-section vs multi-section.
2. Confirm whether the trigger is genuinely "more than one top-level graph exists" (any second
   section, even a trivial one, changed the result here) or something more specific about how a
   `.scrip` polyglot file's multiple sections get lowered into one combined graph list — the two
   trivial-second-section witnesses (SNOBOL4 `END` alone, one-line Icon `main`) both reproduced,
   which argues for the former, but neither was traced past reproducing.
3. Grade any cure against `word/3` too, not just `whites/2` — confirm the fix doesn't merely move
   which proc's registration races, the same class of trap `plc_dead_cstack`'s forced-floor A/B
   caught for the original trail bug (corruption traded for a wrong answer, not actually cured).
4. This FINDING's two witness files were scratch-only, never committed; reconstruct from the table
   above rather than searching for them on disk.
