# FINDING 2026-09-04 seat01 — `table_size_replace_1` SIGSEGV traced to a specific formula
(`emit.cpp:2622`'s `gback` branch computing `gpop=0` for IR_IDENT's gamma edge); NOT fixed, because
the two closest precedents in `.github` both show guessing at this exact mechanism breaks SNOBOL4
elsewhere. Continuing row `snocone-table-size-replace-1-splitwords-segv-on-procedure-return`
(owner hq_P, seat01 off-lane per FLEET-16's dependency-inversion picker).

Tree at start: SCRIP `2f38e54f`. seat02's LEDGER entry on this task already has an excellent
14-witness ablation chain and an ASM-diff pinpointing that the IDENT/DIFFER comparison box's
`sub rsp,16` carve is released on one exit edge and not the other. This FINDING narrows that
down to one formula and one specific value, and explains why I did not then patch it.

## 1. Reproduced fresh, confirmed the exact leak arithmetic

Extracted via the task's own DONE-WHEN (`corpus_suite_harness.py extract ... table_size_replace_1`):
`SplitWords` on `'the cat sat on the mat the cat'` (7 space characters, 8 words) SIGSEGVs in m3.
Compiled with `--compile -o` and read the `.s` directly (ASM-DIFF-FIRST per RULES.md — no gdb
needed, seat02's gdb trace already named the crash site).

The IDENT box for `IDENT(c, ' ')` (`n30_ident_α`, inside the `while` loop):
```
n30_ident_α:  sub  rsp, 16
              ...
              call descr_identical@PLT
              test eax, eax;  jne .Lident_α_118_240
              add  rsp, 16;   jmp n29_lit_string_β      # <- edge A: releases its own 16, cascades correctly
.Lident_α_118_240:            jmp n31_var_α              # <- edge B: releases NOTHING
```
Edge A (recede/omega) cascades correctly through the box's own predecessors —
`n29_lit_string_β` releases its own 16 and jumps to `n28_var_β`, which releases its own 16 **plus**
an extra 144, landing back at the loop head. `16+16+144 = 176`.

Edge B (success/gamma — taken every time the scanned character actually IS a space) jumps straight
to `n31_var_α` and releases **zero**. Every space character in the input leaks 16 bytes of RSP that
are never recovered. The witness has exactly 7 spaces: **7 × 16 = 112**, which is exactly the
`add rsp, 112` the original GOAL line's gdb trace found at `SplitWords_γ`'s corrupted
`[rsp+920]` continuation read — the leak from the loop and the corruption at procedure-return are
the same 112 bytes, not merely the same order of magnitude.

## 2. Traced the missing release to one formula, with real instrumented values

`SCRIP_ZD_DIAG=1 SCRIP_ZD_MAP=1 ./scrip --compile -o /tmp/tsr1_diag.s /tmp/tsr1.sc` (both env vars
are existing diagnostics already in the tree, not new instrumentation):
```
[ZD-MAP] i=30  IR_IDENT   nops=2 ops=[28,29] g=31 o=45 ...
[ZD]       h=17 r=13 i=30 IR_IDENT K=16 zout=192 gpop=0 wpop=176
[ZD-FINAL]      i=30 IR_IDENT K=16 zout=192 gpop=0 wpop=176 gback=31 oback=-1
```
`wpop=176` matches §1's cascade exactly (confirms the omega/recede side's accounting is right).
`gpop=0` is the bug — it is the value edge B fails to release.

`emit.cpp:2622`:
```c
if (!gin) zgpop[i] = (gback >= 0) ? (_wzdepth - _gbpre) : (... _wzdepth ...);
```
`gback=31` means: node 31 (the gamma target — the very next node, `n31_var`, reading `w`) was
already flagged `zon` (armed/processed) by the time node 30 is reached, so the formula takes the
`gback>=0` branch: `zgpop[i] = _wzdepth - _gbpre` where `_gbpre = zout[31] - zd_k(nodes[31])`. This
branch exists to handle a genuine loop back-edge (target already has an established baseline depth
from a prior iteration, so only the *delta* since that baseline should be released, not the full
depth). The printed values make `_wzdepth == _gbpre`, i.e. the formula concludes there is no delta
to release at all.

**What I could not verify in the time I gave this**: whether `gback=31` here is a *genuine* loop
back-edge (node 31 legitimately re-armed from a prior iteration, making the zero-delta conclusion
correct) or a *misclassification* of node 31's role as the plain next-in-sequence successor within
the SAME straight-line run (which is what it structurally looks like from the source — `n31_var_α`
immediately follows `n30_ident_α` in program order, as the `if`'s then-branch). Telling these apart
needs grepping the FULL `SCRIP_ZD_DIAG` log (not just the IDENT/DIFFER-filtered slice I pulled) for
every `i=31` line across every `h=` value, to see which run first set `zon[31]` and what `zout[31]`
was at that time — I did not do this before running out of budget for this row.

**One structural asymmetry worth the next actor's first look**: the omega side already has an
in-run check that the gamma side (line 2622) does not — line 2644, `else if (_zni && oback >= 0 &&
claim[oback] == claim[i] && rpos[oback] > rpos[i] && ...)`, explicitly distinguishes "target is in
the SAME claimed run, later position" from a true cross-run backedge. Line 2622's `gback` branch has
no equivalent `claim[gback]==claim[i]` guard. That asymmetry — present on one port, absent on its
sibling — is exactly the shape of bug `FINDING-2026-08-22-seat07-ir-ident-differ-inline.md` (cited
below) catalogued twice for these same two opcodes: a list/condition that correctly handles the
sibling case but was never extended to this one.

## 3. One hypothesis tested and refuted, cleanly reverted

First guess, before finding the above: `IR_IDENT`/`IR_DIFFER` might be missing from `zd_wl_kind`'s
(`emit.cpp:2133`) per-opcode admission table — it has an explicit arm for the closest sibling,
`IR_CMP_TEST` (line 2148), but none for `IR_IDENT`/`IR_DIFFER`. Added one, gated behind a new
`SCRIP_ZD_STRCMP` killswitch (matching this file's own established convention — eight-plus existing
admissions in the same function follow this exact pattern). Rebuilt, reran the witness: **no
change, still crashes.** Root cause: `zd_wl_kind` line 2141, `if (!(g_emit_cfg &&
g_emit_cfg->icn_cells_graph)) return 1;`, already returns admitted for ANY non-Icon/non-Prolog-cells
graph before reaching any per-opcode arm — Snocone hits this unconditional early return, so my new
arm was unreachable dead code for this witness. Reverted; `git status --short` and `git diff --stat`
both empty, confirmed before writing this up.

## 4. Why this is not shipped as a fix, despite being narrowed to one formula

Two existing findings on this exact subsystem raised the bar for what "verified" needs to mean here:

- **`FINDING-2026-08-22-seat07-ir-ident-differ-inline.md`** — the same two opcodes, `IR_IDENT`/
  `IR_DIFFER`, were newly minted that session and required independent registration in *multiple*
  separate "spelled twice" classification lists across the emitter (`zw_carve_k`'s `_spine` list,
  `zd_nops`, `ir_node_produces_value`, `flat_unwind_beta`'s trivial-beta list, the RPO_PUSH ω-walk
  macro, `ir_value_is_null_string`) because each already listed sibling `IR_CMP_TEST` but had never
  been taught the two new opcodes. §2's asymmetry (line 2644 has an in-run guard, line 2622 doesn't)
  smells like exactly this class of gap, in a list this FINDING did not manage to fully identify.
- **`FINDING-2026-08-29-seat12-pascal-op-zres-gated-omega-pop-fixes-pb34-breaks-snobol4.md`** — a
  single-line, seemingly well-targeted change to this *exact* ω/γ-pop gating mechanism (one line
  away from what §2 examines) fixed one Pascal defect (`pb34`) and **broke 52 SNOBOL4 programs**
  (all pattern-matching-heavy `*_driver`/`demo_*` names) in the same session, because the
  discriminating condition used (`op_zres`) was true for both "safe to skip" and "must not skip"
  cases. That FINDING's own recommendation, and one it says five other named sessions
  (seat05/08/09/10/15/hq_B) independently converged on: **do not guess at this mechanism without a
  specific instrumented answer, and grade any candidate change against the full SNOBOL4 corpus, not
  only the target witness.**

I have the specific instrumented answer for *this* witness (§2) but not yet the general condition
that would fix it without touching the SNOBOL4 pattern-matching cases the sibling `oback`/omega side
already has to guard against at line 2644. Shipping a guess here, even a narrow one, risks repeating
exactly the outcome seat12 already measured and reverted once. Time-boxed my own investigation at
this point rather than iterating guesses without a full-corpus regression gate in the loop for each
attempt.

## 5. Concrete next step

1. `SCRIP_ZD_DIAG=1` on this witness, full log (not filtered to IDENT/DIFFER) — find every `i=31`
   line across every `h=`/`hi` value, to see which run first sets `zon[31]` and confirm whether it's
   a genuine prior-iteration visit or the same straight-line run seen from a different starting head.
2. If it's the latter (misclassification): try mirroring line 2644's `claim[oback]==claim[i]`
   in-run guard onto line 2622's `gback` branch — i.e., only trust `gback` as a true backedge when
   `claim[gback] != claim[i]`, otherwise fall through to the plain `_wzdepth` release.
3. Whatever the candidate: rebuild, confirm this witness's DONE-WHEN goes green in both modes
   (below, unchanged from the task file), **then** run the full SNOBOL4 corpus gate
   (`test_corpus_snobol4.sh`) before considering it shippable — per §4, that is the step that caught
   the last guess at this mechanism before it shipped.

DONE-WHEN (unchanged, still RED both modes, reconfirmed this session on `2f38e54f`):
```
cd "$S4E_HOME/SCRIP" || exit 2; P="$S4E_HOME/corpus/tests/snocone"
python3 scripts/corpus_suite_harness.py extract "$P/ALL.sc" "$P/ALL.ref" table_size_replace_1 /tmp/tsr1.sc --out-ref /tmp/tsr1.ref
o3=$(timeout 10 ./scrip /tmp/tsr1.sc </dev/null 2>/dev/null); [ "$o3" = "$(cat /tmp/tsr1.ref)" ] || { echo "m3 red"; exit 1; }
timeout 30 ./scrip --compile -o /tmp/tsr1.s /tmp/tsr1.sc </dev/null >/dev/null 2>&1 && gcc -no-pie /tmp/tsr1.s -o /tmp/tsr1.bin -Lout -lscrip_rt -lm -Wl,-rpath,$PWD/out
o4=$(timeout 10 /tmp/tsr1.bin </dev/null 2>/dev/null); [ "$o4" = "$(cat /tmp/tsr1.ref)" ] || { echo "m4 red"; exit 1; }
```

## Disposition

No code shipped. `git status`/`git diff --stat` clean on SCRIP, confirmed before this write-up
(§3). Task file's `## NEXT` rewritten with this diagnosis (demoting seat02's to
`## SUPERSEDED-NEXT`); LEDGER appended, not overwritten. Claim released — this needs either
hq_P (owner) or specific instrumented follow-through per §5, not another off-lane bounce.
