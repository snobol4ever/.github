# HANDOFF 2026-05-28 — Opus 4.7 — PROLOG-BB: EP→emit_pair rename (Step 1/3)

**Goal:** GOAL-PROLOG-BB.md infrastructure cleanup. Step 1 of 3 in a multi-step
plan to remove FACT-rule-violating `push_back` / `bin.sites` / `bin.labels` /
`bin.is_def` code from six combinator templates (bb_pat_fence/alt/cat, bb_pl_seq/ite,
bb_succeed) introduced by `0e077eb5`.

## Context — why this work

Lon flagged this code in `bb_pat_fence.cpp`:

```cpp
bin.sites.push_back((int)b.size());
bin.labels.push_back(g_emit.xa_bb_ep_define[i]);
bin.is_def.push_back(true);
```

Directive: **"Remove a thing called push_back, and sites and labels. All of
it. We do not do that. Look around how it is done."** And later: **"Templates
stay pure."**

The offending pattern is in six templates (`bb_pat_fence.cpp`, `bb_pat_alt.cpp`,
`bb_pat_cat.cpp`, `bb_pl_seq.cpp`, `bb_pl_ite.cpp`, `bb_succeed.cpp`), all
introduced together by `0e077eb5` to give those templates real MEDIUM_BINARY
byte production by walking `g_emit.xa_bb_ep_*[]`. The walk requires a
runtime-variable number of `(site, label, is_def)` records, and the implementer
reached for `push_back` to populate `bb_bin_t`'s vectors. That violates the
strengthened FACT rule's spirit (RULES.md): every other template populates
`bin` with a single brace-initialized assignment at the tail, e.g.

```cpp
bin = { {1, 5, 6}, {_.lbl_γ_p, _.lbl_β_p, _.lbl_ω_p}, {false, true, false} };
```

Side observation Lon made: **the "EP" name is wrong** — it stands for
"epilogue" but each entry is structurally a (define-label, jmp-target) **pair**
that wires a combinator's port labels to child-graph labels. Lon's
prescription: **"call it emit_pair and quit being cryptic."**

## What landed in this session

### one4all `68c2c5bc` — EP → emit_pair rename (behavior-neutral)

Pure mechanical rename pass. 115 references across 8 files. Zero behavior
change. All gates byte-identical.

* `src/emitter/emit_globals.h`:
  * `xa_bb_ep_define[]` → `xa_bb_emit_pair_define[]`
  * `xa_bb_ep_jmp[]` → `xa_bb_emit_pair_jmp[]`
  * `xa_bb_ep_n` → `xa_bb_emit_pair_n`
  * `XA_BB_EP_MAX` → `XA_BB_EMIT_PAIR_MAX`
  * Field comment rewritten: "IFT-7: emit-pair (label-define / jmp) sequence...
    Each pair: optional label-definition + optional jmp-target." — explicitly
    drops "epilogue" framing.

* `src/emitter/emit_bb.c`:
  * `EP_RESET()` → `EMIT_PAIR_RESET()`
  * `EP_DEF(lbl)` → `EMIT_PAIR_DEF(lbl)`
  * `EP_JMP(tgt)` → `EMIT_PAIR_JMP(tgt)`
  * `EP_DEF_JMP(l,t)` → `EMIT_PAIR_DEF_JMP(l,t)`
  * `EP_FILL(nd,s,f,b)` → `EMIT_PAIR_FILL(nd,s,f,b)`
  * IFT-7 block comment rewritten: "IFT-7: emit-pair collection helpers —
    driver loads xa_bb_emit_pair_define/jmp arrays, template emits them. Each
    pair is (optional label-definition, optional jmp-target)."
  * All ~50 use sites in `flat_drive_cat`, `flat_drive_fence`, `flat_drive_alt`,
    `flat_drive_pl_seq`, `flat_drive_pl_ite`, `flat_drive_succeed` etc.
    renamed.

* Six template files (`bb_pat_fence.cpp`, `bb_pat_alt.cpp`, `bb_pat_cat.cpp`,
  `bb_pl_seq.cpp`, `bb_pl_ite.cpp`, `bb_succeed.cpp`):
  * Field references inside the `push_back` code renamed (the violation code
    itself still present — that's Step 3).
  * Wildcard comment mentions `xa_bb_ep_*` → `xa_bb_emit_pair_*`.

### Verification

```
grep -rnE '\bxa_bb_ep_|\bXA_BB_EP_MAX|\bEP_(RESET|DEF|JMP|FILL)\b' src/
# 0 hits — zero residue
```

## Gates at HEAD `68c2c5bc`

| Gate                              | Baseline | After    | Δ |
|---|---|---|---|
| Build                             | green    | green    | = |
| GATE-1 Prolog smoke               | 5/5      | 5/5      | = |
| GATE-4 Prolog mode-4 minimal      | 4/4      | 4/4      | = |
| Sister smoke icon                 | 5/5      | 5/5      | = |
| Sister smoke raku                 | 5/5      | 5/5      | = |
| Sister smoke snobol4              | 13/13    | 13/13    | = |
| Sister smoke snocone              | 5/5      | 5/5      | = |
| Sister smoke rebus                | 4/4      | 4/4      | = |
| FACT grep (push_back violations)  | 6 files  | 6 files  | = (Step 3) |

GATE-2/GATE-3/GATE-4 full corpus / mode-4 corpus / per-rung were not re-run
this session — pure rename, no codegen changes, so no expected delta. Next
session should re-run them before/after Step 3 since that one DOES change
codegen for the six combinator templates.

## REMAINING WORK — Steps 2 and 3 (NOT done this session)

The full 3-step plan was scoped but only Step 1 landed. Steps 2 and 3 are
spelled out here so the next session can execute deterministically.

### Step 2 — Add driver-side metadata reconstruction helper

Goal: enable templates to emit BINARY bytes for the emit_pair walk without
touching `bin.sites/labels/is_def` at all.

The (site, label, is_def) triples that `bb_emit_asm_result` needs to drive
`bb_label_define` and `bb_emit_patch_rel32` are **fully derivable** from the
`xa_bb_emit_pair_*` arrays plus the fixed byte-layout convention:

  * `xa_bb_emit_pair_define[i]` non-NULL → 0 bytes consumed, record
    `(current_offset, define[i], is_def=true)`.
  * `xa_bb_emit_pair_jmp[i]` non-NULL → 5 bytes (`\xE9` + rel32) consumed,
    record `(current_offset + 1, jmp[i], is_def=false)`.

Add to `src/emitter/emit_str.h`:

```cpp
void bb_emit_asm_result_pairs(const std::string & out);
```

Add to `src/emitter/emit_str.cpp` (immediately after `bb_emit_asm_result`):

```cpp
/* Variant of bb_emit_asm_result for combinator templates whose BINARY arm
 * walks g_emit.xa_bb_emit_pair_*[] and emits zero-or-5 bytes per pair.
 * Metadata reconstructed here from the same arrays — templates stay pure
 * (no bin.sites/labels/is_def access). FACT rule: byte production stays
 * in the template; this helper only reconstructs the patch metadata. */
void bb_emit_asm_result_pairs(const std::string & out) {
    if (!MEDIUM_BINARY) {
        if (!out.empty()) emit_text_n(out.data(), out.size());
        return;
    }
    int pos = 0;
    int n = g_emit.xa_bb_emit_pair_n;
    for (int i = 0; i < n; i++) {
        if (g_emit.xa_bb_emit_pair_define[i]) {
            bb_label_define(g_emit.xa_bb_emit_pair_define[i]);
        }
        if (g_emit.xa_bb_emit_pair_jmp[i]) {
            /* Emit the \xE9 opcode byte from `out`, then patch rel32. */
            bb_emit_byte((uint8_t)(unsigned char)out[pos]); pos++;
            bb_emit_patch_rel32(g_emit.xa_bb_emit_pair_jmp[i]);
            pos += 4;
        }
    }
    /* Drain any trailing bytes (n==0 fallback shape, if any template uses one). */
    for (; pos < (int)out.size(); pos++) bb_emit_byte((uint8_t)(unsigned char)out[pos]);
}
```

Build, link, verify it doesn't break anything (no template uses it yet).

### Step 3 — Strip the six templates

For each of `bb_pat_fence.cpp`, `bb_pat_alt.cpp`, `bb_pat_cat.cpp`,
`bb_pl_seq.cpp`, `bb_pl_ite.cpp`, `bb_succeed.cpp`:

#### Template body changes

In the BINARY arm, remove ALL `bin.sites.push_back(...)`,
`bin.labels.push_back(...)`, `bin.is_def.push_back(...)` lines. Keep only
the byte production loop:

```cpp
+ IF(MEDIUM_BINARY, [&]() {
      std::string b;
      for (int i = 0; i < g_emit.xa_bb_emit_pair_n; i++) {
          /* define[i] contributes 0 bytes (label binding handled in driver helper) */
          if (g_emit.xa_bb_emit_pair_jmp[i]) {
              b += bytes(1, "\xE9");
              b += u32le(0);
          }
      }
      return b;
  }())
```

`bb_pat_fence.cpp` has an additional `xa_bb_emit_pair_n == 0` synthesized
shape (lbl_α: jmp γ ; lbl_β: jmp ω). Two ways to handle:

  * **Option A** — keep that special case, but require it to emit ONLY bytes:
    `b += bytes(1,"\xE9") + u32le(0) + bytes(1,"\xE9") + u32le(0)`. The
    bookkeeping for the 4 sites needs to come from somewhere — easiest is
    to have the driver fence path emit pseudo emit_pairs for the 0-children
    case via EMIT_PAIR_DEF / EMIT_PAIR_DEF_JMP, so the template path
    becomes uniform. Read `flat_drive_fence` to see whether the 0-children
    case already populates pairs (if so, the template's special case is
    dead code and can be deleted).
  * **Option B** — drop the special case entirely; ensure
    `flat_drive_fence` always populates pairs for the 0-children case.

Recommend Option B for symmetry.

#### Template wrapper change

At the bottom of each of the six files, change:

```cpp
extern "C" void bb_pat_fence(BB_t * pBB) {
    bb_bin_t bin;
    bb_emit_asm_result(bb_pat_fence_str(pBB, bin), bin);
}
```

to:

```cpp
extern "C" void bb_pat_fence(BB_t * pBB) {
    /* Combinator template: BINARY metadata reconstructed by the driver-side
     * helper from g_emit.xa_bb_emit_pair_*[] arrays; template emits bytes only. */
    std::string s = bb_pat_fence_str(pBB);
    if (MEDIUM_BINARY) bb_emit_asm_result_pairs(s);
    else if (!s.empty()) emit_text_n(s.data(), s.size());
}
```

And change `bb_pat_fence_str` signature from `(BB_t *pBB, bb_bin_t &bin)` to
`(BB_t *pBB)`, removing the `bin = {}` line at the top.

#### Verification after Step 3

```
grep -rnE 'push_back|bin\.sites|bin\.labels|bin\.is_def' src/emitter/BB_templates/
# Should be 0 hits (the one in bb_capture.cpp is a comment about std::deque,
# not bin — verify by hand)

grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/ \
  --include="*.c" --include="*.cpp" | grep -v "_templates/" | grep -v emit_core.c
# Should be 0 (FACT compliance)
```

Run full gate suite:
* GATE-1 smoke_prolog → 5/5
* GATE-2 crosscheck → 132/0
* GATE-3 mode-2 rung suite → 96/107
* GATE-4 mode-4 minimal → 4/4
* Full mode-4 corpus → 54/107 (these six templates not yet wired into
  mode-3 native sealed-RX build path — see PLAN.md SNOBOL4 BB row's NEXT
  pointer; their BINARY arms are NOT exercised by current corpus runs,
  which is WHY the push_back code was undetected during 0e077eb5's gates)
* Sister smokes → all green

### Why Step 3 should be **byte-identical** in the gates we currently run

PLAN.md SNOBOL4 BB row explicitly notes: *"NEXT: wire `bb_build_flat` for
combinator nodes through mode-3 sealed-RX so ALT/CAT/FENCE actually fire
their new arms under --run SCRIP_M3_NATIVE=1; bytes are ready, build path
needs the extension."* Translation: the six templates' BINARY arms are
written but **not reached** by any current build. So removing the bookkeeping
push_back lines and routing through `bb_emit_asm_result_pairs` instead of
`bb_emit_asm_result(..., bin)` produces a code path that currently no test
exercises. Step 3 is safe to land on green gates **provided** the build still
compiles and `bb_emit_asm_result_pairs` proves correct when those arms ARE
eventually wired in (which is what SBL-CAP-2's "NEXT" describes).

## Why I stopped after Step 1

Lon asked for a handoff after Step 1's commit. Steps 2 and 3 are scoped and
ready to execute in a fresh session with full context budget. The rename was
the natural commit point — pure mechanical, zero risk, leaves the tree clean
and the next session free to focus on the substantive refactor.

## Rebase note

Pulled `.github` before commit: rebased over `2c666ff5`, `e5a93452`,
`6be121c4` (Sonnet's Icon-BB analysis revert chain). No PLAN.md conflict
expected — different row.

## Commit identity used

```
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

## Verification

```
cd /home/claude/one4all && git log origin/main --oneline -1
# 68c2c5bc rename EP -> emit_pair in BB driver/template interface
#          (behavior-neutral)

cd /home/claude/.github && git log origin/main --oneline -1
# <this commit>  Prolog BB: EP→emit_pair rename (Step 1 of FACT cleanup)
```

## NEXT session candidates (in rough order)

1. **Steps 2 + 3 of this cleanup** (top priority — Lon explicitly directed
   it). Stripping the six templates is a one-session job once Step 2's
   helper is in place. Gate: `grep` shows zero push_back violations and all
   smokes/rungs hold.

2. **WAM-CP-13** (mode-4 catch/throw + longjmp-free unwind) — picks up from
   the prior session's `5427e12e`.

3. **WAM-CP-6** (LCO).
