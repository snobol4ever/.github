# FINDING 2026-08-23 (seat01) — row `zeta-frame-rsp-second-wild-write`: BOTH fix-plan sites implemented, beauty.sno's own DONE-WHEN now passes in BOTH modes, full crosscheck regression-checked with zero new failures. ROW CLOSED.

## HEADLINE

Implemented the two-site fix scoped by `FINDING-2026-08-23-seat03-frame-rsp-wild-write-root-cause-and-fix-plan.md`
(mode 4 in `scrip.c`, mode 3 in `rt.c`) — **plus a second, previously-unknown mode-4 prologue site the plan's
author never saw**, found only because the row's own mode-4 check (which the task file flags as required even
though the mechanical DONE-WHEN only exercises mode 3) still crashed after patching the site the plan named. With
both mode-4 sites patched: `beauty.sno` under `--zeta-storage=frame-rsp` now exits 0 and matches the default
cell-stack arm **byte-for-byte in BOTH modes** (the row's ORIGINAL CRITERION, not just the mechanical mode-3-only
DONE-WHEN). Full `test_crosscheck_snobol4.sh` regression sweep under frame-rsp: mode-4 FAIL 126→34 (34 is a
**strict subset** of the prior 126 — zero new failures), mode-3 unchanged byte-for-byte (33/33 identical items),
DIVERGE 93→1. Default (cell-stack) arm: unaffected in every measurement taken (proven, not assumed).

## CONTEXT / CONTINUITY

Row history: seat02 minted this row splitting it off `zeta-frame-rsp-capture-home` once that row's named defect
closed (`FINDING-2026-08-23-seat02-zeta-frame-rsp-capture-home.md`) but beauty.sno kept SIGSEGVing further in.
seat03 bisected a minimal synthetic witness (`corpus/probe/frame/frame_rsp_indexed_call_concat.sno`, N=96 threshold,
`FINDING-2026-08-23-seat03-frame-rsp-wild-write-minimal-witness.md`), then in a later session root-caused the
mechanism via ASM-DIFF-FIRST + `--dump-zeta` (no gdb needed) and wrote a scoped, evidenced, NOT-YET-IMPLEMENTED fix
plan before being reassigned mid-session to `vlist-expr-alternation` by hq_C
(`FINDING-2026-08-23-seat03-frame-rsp-wild-write-root-cause-and-fix-plan.md`). This session picked up the released
claim, implemented the plan, found it incomplete (see below), completed it, and verified regression-free.

**Root mechanism, unchanged from the prior FINDING:** `--zeta-storage=frame-rsp`'s outer/top-level scope computes a
correct, ever-growing ζ-local-storage (ZLS) slot layout (`zls_build`/`ir_drive_slot_assign`) but the entry prologue
only ever reserves a fixed `sub rsp, 8` — once accumulated slot usage exceeds real (unreserved) stack headroom, the
generated code walks past the top of the OS-mapped stack region and wild-writes. Cure: reserve the actual computed
region (`zls_g_region()`) instead of the fixed 8 bytes.

## THE FIX — THREE EDIT SITES (the plan named two; this session found the plan's mode-4 site was a dead branch for
## any program with `DEFINE`d procedures, and the real site was elsewhere)

**Mode 3 (`--run`, JIT trampoline), `src/runtime/rt/rt.c`, `rt_outer_call`** — exactly as planned: bracket the
existing `sub $8, %rsp` / `add $8, %rsp` with a symmetric `sub $4194304, %rsp` / `add $4194304, %rsp` pair (4 MiB,
build-once-run-many, can't see a per-program size). Alignment re-verified independently before implementing (plan's
own instruction): entry rsp ≡ 8 (mod 16) → `push %r12` → ≡0 → `sub $8` → ≡8 → **4,194,304 = 2^22, a multiple of 16,
so the bracket is a no-op on the residue** → `call *%rax` still lands at the same ≡8 (mod 16) it always did. Two
lines added, symmetric, unconditional (all 4 storage arms pay two extra harmless instructions once per process).

**Mode 4 site A (`--compile`, TEXT), `src/driver/scrip.c:1481`, the `sbbg`-keyed prologue** — the site the plan
named. Immediately after the existing `SCRIP_M4_HEADROOM` block:
```c
if (rt_zeta_storage_get() == (int)ZC_STORAGE_FRAME_RSP) {
    extern int zls_g_region(const IR_graph_t *);
    long need = sbbg ? (long)zls_g_region(sbbg) : 0L;
    if (need > 0) { need = (need + 15) & ~15L; emit_textf("  sub rsp, %ld\n", need); }
}
```
Gated on `ZC_STORAGE_FRAME_RSP` specifically — the other three arms emit byte-identical output (unreachable branch
for them, not merely untested — provable by inspection, and empirically confirmed, see Verification).

**Mode 4 site B (`--compile`, TEXT), `src/driver/scrip.c:1302`, the `bbg`-keyed prologue — NOT IN THE ORIGINAL
PLAN, found this session.** `scrip.c` contains **two** near-duplicate `main:`-prologue emitters for mode 4, each
with its own copy of the exact same `SCRIP_M4_HEADROOM` block (confirmed: `grep -n SCRIP_M4_HEADROOM scrip.c` finds
exactly these two hits and no others). The plan's author patched only the `sbbg` one (line ~1480, reached when
`n_procs == 0` — the small synthetic witness has no `DEFINE`d procedures, so that's the branch it exercises, and is
why the plan's experimental confirmation via `SCRIP_M4_HEADROOM=65536` worked). **`beauty.sno` — and any program
with `DEFINE`d procedures, classes, or grammar rules — instead compiles through the earlier `bbg`-keyed emitter**
(the one that ends `call module_init` / `call main_init` depending on `sn4_module_init_bottom()`), which the plan
never touched. Discovered because this row's task file explicitly requires checking mode-4 beauty.sno even though
the mechanical DONE-WHEN only names mode-3 (line 91: "mode-4 ... should also be checked before this is truly
closed") — a mode-3-only verification would have missed this and closed the row on a still-broken mode-4. Same
patch shape, keyed on `bbg` instead of `sbbg`:
```c
if (rt_zeta_storage_get() == (int)ZC_STORAGE_FRAME_RSP) {
    extern int zls_g_region(const IR_graph_t *);
    long need = bbg ? (long)zls_g_region(bbg) : 0L;
    if (need > 0) { need = (need + 15) & ~15L; emit_textf("  sub rsp, %ld\n", need); }
}
```
Confirmed via direct `.s` inspection: before this second edit, `beauty.sno --compile --zeta-storage=frame-rsp`'s
`main:` showed the identical unpatched 3-instruction prologue and still SIGSEGV'd (rc=139) even with site A live;
after, `main:` shows `sub rsp, 168112` (exactly `zls_g_region()`'s reported value for beauty's real top-level
graph, confirming the correct value flows through) and the compiled binary exits 0.

## VERIFICATION

**The row's own DONE-WHEN + ORIGINAL CRITERION (`corpus/programs/snobol4/demo/beauty/beauty.sno`), both modes:**
- mode 3 (`--run`): frame-rsp rc 139→**0**; `diff` against cell-stack mode-3 output: **identical** (both empty —
  beauty.sno's `main00` hits EOF on `</dev/null` immediately and jumps to `END`, so the byte-identity bar here is
  "both produce zero bytes," confirmed, not assumed).
- mode 4 (`--compile` → `gcc -c` → `gcc` link → run, exact recipe lifted from `test_crosscheck_snobol4.sh`'s
  `compile_mode4()`): frame-rsp rc 139→**0**; `diff` against cell-stack mode-4 output: **identical**.
- cell-stack (default arm) `beauty.sno` output, mode 3: **byte-identical before vs after** both fix commits (proves
  the mode-3 `rt.c` bracket is genuinely inert on the arm everyone else uses, not just "should be" from the
  alignment math).

**Full `test_crosscheck_snobol4.sh` (the row-prescribed regression command), fresh `make pristine` at SCRIP
HEAD `3f81eda2`, both before edits (baseline re-captured fresh at this HEAD — the earlier baseline from a
background task had drifted one revision stale, see Receipts) and after both edits landed:**

| Arm | Mode | Before | After | Regression? |
|---|---|---|---|---|
| default (cell-stack) | `--run` | PASS=325 FAIL=0 | PASS=325 FAIL=0 | none — identical |
| default (cell-stack) | `--compile` | PASS=325 FAIL=0 | PASS=325 FAIL=0 | none — identical |
| default (cell-stack) | DIVERGE | 0 | 0 | none |
| frame-rsp | `--run` | PASS=292 FAIL=33 | PASS=292 FAIL=33 | **none — the 33-item FAIL list is byte-identical, same items, same order** |
| frame-rsp | `--compile` | PASS=199 FAIL=126 | PASS=291 FAIL=34 | **the 34 after-items are a verified strict subset of the 126 before-items — zero new failures, 92 cured** |
| frame-rsp | DIVERGE | 93 | 1 | 92 fewer; the survivor (`086_define_locals`) was already diverging before this fix and is untouched by it |

Subset check for the frame-rsp `--compile` row was done by literal set inspection (all 34 post-fix names checked
against the 126 pre-fix names), not by count arithmetic alone.

**Supplementary (not row-required, run for extra confidence): `test_corpus_snobol4.sh`, broader corpus (361
items vs crosscheck's 325):** default arm unaffected (PASS=360/FAIL=1 both before and after, same single
pre-existing failure `demo_treebank` both times — unrelated to this row). Frame-rsp arm improved at the count level
(`--run` FAIL 57→43, `--compile` FAIL 158→44) — **notable that mode-3 improved here** (unlike the smaller crosscheck
corpus, where mode-3 was untouched): this broader corpus includes bigger programs that apparently do cross the
mode-3 headroom threshold, so the `rt.c` bracket has real, not just theoretical, value beyond beauty.sno. Item-level
subset was NOT rigorously re-verified for this supplementary script (its FAIL-line output format turned out
ambiguous to parse mechanically vs. the row-required script's clean space-delimited lists) — the row-required
`test_crosscheck_snobol4.sh` result above is the load-bearing regression proof; this table is corroborating count
evidence only, flagged honestly rather than silently claimed at the same rigor.

**Gates:** `test_gate_emit_no_lang.sh` (LANG-BLIND, rc=0) and `test_gate_template_medium_invisible.sh` (ratchet
ceiling 0, rc=0) both pass — expected, since neither edit touches `src/templates/`.

**NOT run this session:** the full `.s`-artifact regen chain (`util_regen_*_s_artifacts.sh`). Reasoned + partially
empirically justified rather than silently skipped: mode-4 site A/B are both gated on an exact-equality check
against `ZC_STORAGE_FRAME_RSP`, which is unreachable under every other arm by construction (provable by inspection,
not merely untested); the mode-3 bracket is a content-free stack-pointer shuffle proven byte-identical on
cell-stack via beauty.sno AND the full default-storage crosscheck (0 change both before/after). Since every
committed `.s` artifact in the repo is generated under default storage, a full regen would necessarily show
`changed=0` — skipped running the multi-stage chain to save the wall-clock, noted here rather than left unstated.

## OUT OF SCOPE, UNCHANGED FROM THE PRIOR FINDING

- `DEFINE`d-function activations' OWN per-call headroom (as opposed to the outer/top-level scope this row's
  DONE-WHEN covers) are still not fixed — flagged by the root-cause FINDING as needing correct `add rsp` on every
  RETURN/FRETURN/NRETURN exit port, non-trivial surface area not attempted here, matching the fix plan's own
  explicitly out-of-scope section.
- frame-rsp is not a 100%-passing arm: 34 `--compile` / 33 `--run` crosscheck items still fail under it, and one
  item (`086_define_locals`) still diverges m3-vs-m4. These are pre-existing, independent, unrelated-mechanism
  gaps (this row's DONE-WHEN was never "100% crosscheck," it was beauty.sno specifically) — same "dead-arm-still-
  has-other-issues" shape `zeta-frame-rsp-capture-home` closed on, just with fewer remaining issues now.
- The architecturally "correct" fix (real per-box α-push/ω-pop bounding memory to live depth, per
  `ARCH-ZETA-LOCAL-STORAGE.md`'s own STACK-flavor law) is not what either mode-4 site implements — both are a
  reserve-the-whole-computed-total stopgap, safe for any program whose total node count fits in a few MB (every
  known corpus/demo program) but not the documented design's scaling model.

## RECEIPTS

SCRIP HEAD at investigation/fix time: `3f81eda2` (pre-fix baseline re-captured fresh at this exact HEAD after
`git pull --rebase`, `make pristine`, per HQ-27 PRISTINE-BUILD-BEFORE-VERDICT — the background baseline task
kicked off earlier in this session's history had run one revision stale against an older local HEAD and was
discarded in favor of this fresh capture once the drift was noticed). Diff: `src/driver/scrip.c` (+10 lines, two
sites) and `src/runtime/rt/rt.c` (+2 lines) — 12 lines total, no other files touched, no new globals.

**Mid-session infrastructure note, for the record:** the machine's root filesystem (backing both `/tmp` and
`/home`) hit 100% full partway through this session's verification runs, from an unrelated seat's Icon scorecard
run writing several 8–12 GB scratch directories into `/tmp`. Work paused immediately on an emergency relayed via
HQ-PERFORM/ceo (no builds/commits/writes) until confirmed clear (root back to comfortable headroom, the runaway
scratch dirs and their producing processes gone); this row's own two background crosscheck processes had already
self-terminated from ENOSPC and were confirmed dead, nothing of this row's was lost or corrupted, and both
before-fix baselines affected by the pause were simply re-run clean afterward (see the crosscheck table above,
which reflects the post-recovery fresh captures). `/home` (all git repos) was never actually at risk per ceo's
correction — the exposure was `/tmp`-only.

**Local-only, not a repo change:** this seat's `/home/claude01/CLAUDE.md` had the retired `O0-DEV-O2-BENCH`
`-O2`-for-benchmarks paragraph (superseded by the NO-`O2`-EVER FACT RULE, Lon s262/s267) — corrected per hq_P's
fleet-wide memo this session. Not part of this commit (CLAUDE.md is untracked).
