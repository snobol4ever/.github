# FINDING — `--zeta-storage=cell-heap` WAS NOT A HEAP MECHANISM MISSING A HOME, IT WAS THE SPINE MECHANISM NEVER TOLD HEAP EXISTS

**Seat:** seat04 (worker, THE LOOP, task `zeta-cell-heap-segv`) · **2026-08-23** · **Class:** ROOT-CAUSED + CURED (MEASURE AND CURE, Lon s261)

## Verdict

`./scrip --zeta-storage=cell-heap` on `corpus/benchmarks/snobol4/roman.sno` now runs to completion and produces the
same deterministic `check: 1102` as the default `cell-stack` arm. Root cause: eight call sites across
`src/emitter/emit.cpp` and `src/templates/x86_asm.h` gate the ζ-SPINE cell-planning pass (`zd_plan`) and its
downstream consumers (`x86_fc_on`, `x86_fc_hit`, the ARBNO chain-size computation, `fc_seq_on`, `op_subj_cell`,
the zpop-fold optimization, and `zd_plan`'s own chain-distance accumulator) on `x86_port_mode() == ZC_PORT_FORTH`
**exclusively**. `--zeta-storage=cell-heap` compiles to `ZC_PORT_HEAP`, not `ZC_PORT_FORTH` — so every one of these
sites silently no-ops, and any IR node whose *only* viable home is a ζ-SPINE cell (the common case — see below) has
no home at all. Fix: widen all eight to `(ZC_PORT_FORTH || ZC_PORT_HEAP)`. Two lines of that work (not all eight)
were necessary and sufficient to move the failure from a hard abort to a live SIGBUS; all eight together are
necessary for a correct answer. `frame-rsp` (`ZC_PORT_CSTACK`, the sibling row `zeta-frame-rsp-capture-home`) was
deliberately **not** touched and is still red — see Scope below.

## The failure mode had already changed once, silently, before this session touched anything

The brief (converted from `FINDING-2026-08-22-hq_P-the-zeta-ab-axis-has-one-working-arm.md`) says cell-heap
**SIGSEGVs** on roman. At a fresh pristine build this session found it instead **aborts** with a diagnostic:

```
libscrip_rt: BOMB — IR_MATCH_CAPTURE_SAVE: no home -- neither a ζ-SPINE cell (op_zres) nor a ζ-STANDING slot
(frame_need_of: DEFER-hazard / ALT-arm classes); classifier and ZD plan disagree on this node -- the legacy C
rt_cap_push fallback is deliberately not rebuilt (s83)
```

`git log -S` on that string shows it landed at s93 (SCRIP `1aaf1a11`), unrelated to zeta-storage — it's a generic
guard against emitting a wild-pointer write when neither of `bb_match_capture.cpp`'s two known homes (`op_zres`
spine cell, or `op_cap_frame_off` STANDING slot) is available. It converted this row's SIGSEGV into a safe abort
as a side effect, not a fix. The underlying gap — cell-heap has no spine-cell home at all — was unchanged. This is
recorded so the next reader isn't confused when the brief's exact symptom doesn't reproduce: **the codebase
churns fast, and a symptom description is a snapshot, not a contract** (per CLAUDE.md's own warning).

## Why the "delta is bounded by construction" premise didn't hold, and what to trust instead

The brief's ASM-DIFF-FIRST framing ("cell-heap and cell-stack differ ONLY in where the zeta cell lives... the
delta is bounded by construction") predicted a small, localized `.s` diff. Measured: `--compile` on roman.sno
under the two arms diffs **3825 of ~3700 lines** — essentially the whole program, because `zd_plan` claims (or
doesn't) nearly every IR node, and that one decision cascades through dozens of templates. The premise was wrong
about *size*; it was right about *kind* — every difference traces to the same eight gates, confirmed by grepping
every `x86_port_mode() == ZC_PORT_FORTH` / `!= ZC_PORT_FORTH` in the two files (exactly 8, listed below) and by
the `SCRIP_CAP_DIAG=1` field dump showing `zres` flip 1→0 between arms on an otherwise-identical node
(`anchor`/`frame_off` unchanged) — never trust a brief's size estimate over a direct measurement.

## Root cause, precisely

`frame_need_of()` (`emit.cpp:746`, decides the ζ-STANDING/`op_cap_frame_off` fallback) is **storage-independent**
by construction — it dispatches purely on IR shape (`IR_MATCH_ARBNO`/`FENCE0`/`FENCE1`, or `earn_hazard_in` /
`cap_in_alt_arm` / `cap_in_repeat_body` for captures), never touching `x86_port_mode()`. It covers only the
DEFER-hazard/ALT-arm minority. The ζ-SPINE path (`op_zres`, the "ordinary, unchanged mechanism" — see
`bb_match_capture.cpp`'s own comment) is meant to cover the rest, and is driven entirely by `zd_plan()`
(`emit.cpp:2388`), whose very first line was:

```c
if (!_zd || x86_port_mode() != ZC_PORT_FORTH || n <= 0) return;
```

— an unconditional bail for any port other than FORTH, leaving `zd_on[]` all-zero and `op_zres` false for
*every* node. Under cell-heap this is the **only** source of the divergence: address formation for a claimed
spine cell (`ZRESD`/`ZOPD` → `x86_zref` → the literal `"[rsp# + N]"` template → `x86_rsp_modrm`, a hardcoded SIB
byte for register 4/RSP) never branches on `x86_zstorage()` at all, and `bb_glue_flat.cpp`'s own carve-out
(`sub/add rsp, op_fc_bytes`) already explicitly guards on `ZC_STORAGE_CELL_STACK || ZC_STORAGE_CELL_HEAP` — i.e.
that file's author already intended ordinary spine cells to live on the real machine stack under **both** arms.
`zd_plan`'s FORTH-only gate (and seven siblings that key off the same predicate to keep the resulting bookkeeping
consistent — chain distances, FC-hit windows, the ARBNO chained-cell flag, subject-cell eligibility) is simply
the one place nobody told that cell-heap counts too.

**The eight sites** (all `src/emitter/emit.cpp` unless noted):
`zd_plan`'s early return (2395) · the chain-distance accumulator inside `zd_plan` (3021) · `fc_seq_on` (1311) ·
`op_subj_cell` (1493) · the ARBNO-K16 framing decision and its chained-cell flag (1116, 1118) · the zpop-fold
optimization's entry gate (2959) · `x86_fc_on` and `x86_fc_hit` (`src/templates/x86_asm.h:466,468`).

## A stray, harmless artifact worth naming so nobody chases it later

`x86_asm.h:1992-2005` has a `ZC_PORT_HEAP`-specific hook (bump-allocate via `rbx`/`rt_zh_bump_slow` against
`RT_WS_TOP`/`RT_WS_LIMIT`) that fires whenever `op_fc_bytes > 0` under heap port — which, per `SCRIP_CAP_DIAG`,
is true for capture-SAVE nodes regardless of storage arm. It is the **only** `ZC_PORT_HEAP` reference in the
file; `rt_zh_alloc`/`rt_zh_deref`/`rt_zh_mark_dead` are called nowhere in `src/templates/`, only from the retired
C `rt_cap_push`-era code in `src/runtime/rt/rt.c` that the bomb message itself says is "deliberately not
rebuilt." No template reads the `rax` it hands back — every consumer overwrites `rax` before use (verified by
reading the emitted `.s`) — so it is a live but inert, unreleased 16-byte-per-hit leak into the ZH region under
cell-heap, pre-existing and **not** introduced by this fix. It's why this fix does not attempt to make cell-heap
cells physically live in the ZH heap: that plumbing was scaffolded once and abandoned (s83's "legacy C fallback"
retirement), and rewiring every `op_zres` consumer (49 files) to a handle-indirected heap addressing scheme is
far outside a "second dead arm" bug fix. Left as multi-KB-per-run waste; worth a follow-up row if cell-heap's
raison d'être ever becomes "actually live on the heap" rather than "a selectable, correct A/B arm."

## Verification

- **Minimal witness** (ASM-DIFF-FIRST mint): `DEFINE('ROMAN(N)T')` + one call, `OUTPUT = ROMAN(1201)`. cell-stack
  prints `MCCI` (correct — 1000+200+1). Before the fix, cell-heap aborted on the bomb; after `zd_plan` alone,
  it SIGBUS'd inside `n1_lit_integer_α`'s own emitted code (confirmed live in gdb: `mov r14d,[rsp+0x7f010]`,
  disassembly + `SCRIP_CAP_DIAG` + a `.s` diff of the exact node traced it to `x86_fc_on`/`x86_fc_hit` still
  gating the matching `sub/add rsp` carve-out to FORTH only, while `zd_plan` had started claiming cells that
  expected it); after all eight, cell-heap prints `MCCI` too.
- **roman.sno, full**: both arms exit 0, `check: 1102` byte-identical. `iters:`/`ns:`/`ms:` differ — see next
  section, this is expected and not a defect.
- **Blocking set** (`GOAL-SNOBOL4-100.md`'s SNOBOL4-FIRST policy), pristine build: `test_gate_emit_no_lang.sh` OK
  · `test_gate_template_medium_invisible.sh` OK (WIP baseline unchanged, I didn't touch `bb_*.cpp`) ·
  `test_corpus_snobol4.sh` 359/360 both modes, sole failure `demo_treebank` — matches the goal file's own
  documented pre-existing baseline exactly · `test_gate_instr_budget.sh`: roman OK, **beauty FAILs its Ir
  budget — confirmed pre-existing** by `git stash`-ing this fix, rebuilding pristine at unmodified HEAD, and
  reproducing the identical `Ir=2607784844` failure with zero code changes. Not this row's regression; flagged
  to hq_P/hq_C, not fixed here (out of scope, unrelated mechanism).
- **All six `.s` regen scripts** (required — this touched `emit.cpp`/`x86_asm.h`): benchmark, feature, demo,
  programs, prolog_bench all report `changed=0`. crosscheck reports one changed file
  (`crosscheck/patterns/132_pat_fence_eps_recur_shallow.s`) — traced via `git show` to the unrelated, already-landed
  upstream commit "mode-4 DEFINE-site: bodiless function entry references rt_ab_undef_fn_stub" (pulled at this
  session's start, before any of this row's edits) whose artifact simply hadn't been regenerated yet; not this
  fix's doing. **Net: this fix is behaviorally inert for the compiled-default (cell-stack) arm across the entire
  pinned corpus**, exactly as its "only add a case, never narrow FORTH's" construction predicts.
- **Sibling arm sanity check**: `--zeta-storage=frame-rsp` on roman.sno still hits the identical `IR_MATCH_
  CAPTURE_SAVE: no home` bomb, byte-identical to before this session — confirming the fix is scoped to
  `ZC_PORT_HEAP` only and does not touch `ZC_PORT_CSTACK` (row `zeta-frame-rsp-capture-home`, still open).

## The DONE-WHEN command as written can never pass — and why that's not this fix failing

```
"$R/SCRIP/scrip" --zeta-storage=cell-heap "$R/corpus/benchmarks/snobol4/roman.sno" >/tmp/zch.out 2>&1 &&
"$R/SCRIP/scrip" --zeta-storage=cell-stack "$R/corpus/benchmarks/snobol4/roman.sno" >/tmp/zcs.out 2>&1 &&
diff -q /tmp/zch.out /tmp/zcs.out
```

roman.sno is explicitly `* roman -- TIME-BASED: fixed ms budget, count iterations` (its own header comment) —
`iters:`/`ns:`/`ms:` are real wall-clock measurements and **will differ across any two separate process
invocations**, including two runs of the *same* arm. Measured directly: running `--zeta-storage=cell-stack`
against itself twice gives a non-empty `diff` on those three lines every time. The mechanically-decidable content
is the deterministic `check: 1102` line (fixed by `ZCHK=200`, phase-1 of `harness.inc`), which is byte-identical
between the two arms both before this command's `diff -q` and independently verified via `head -1`. **This
command cannot be satisfied as written, by any compiler behavior whatsoever — it isn't a decidable core, it's an
undecidable one that happens to have a decidable line buried in it.** Per this task's own instruction ("if it is
WRONG, fix it and say so"): the corrected, mechanically-decidable form is

```
diff -q <(grep -v '^\(iters\|ns\|ms\):' /tmp/zch.out) <(grep -v '^\(iters\|ns\|ms\):' /tmp/zcs.out)
```

which this fix satisfies (verified). Flagged to hq_P for the row's own DONE-WHEN text, not silently substituted.

## Scope note for whoever picks up `zeta-frame-rsp-capture-home`

The same eight-gate shape almost certainly reproduces there — `frame-rsp` maps to `ZC_PORT_CSTACK`
(`rt_zeta_storage_set`), a **ninth** value these same predicates don't admit, and the FINDING that named both
rows together (`FINDING-2026-08-22-hq_P-...-one-working-arm.md`) reports the identical bomb text on beauty
under frame-rsp. Confirmed but deliberately not touched or extended here — that row's DONE-WHEN target is
beauty.sno, a much larger surface, and its own session should re-verify a `CSTACK` widening the same way this one
verified `HEAP` (minimal witness first, full regression + all six regen scripts after) rather than inherit an
unverified guess.
