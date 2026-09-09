# FINDING 2026-09-09 (cto, MODE NONET) — DEFINE is executable: the bind node carries the right entry and the driver throws it away

Class handed over fully diagnosed by hq_P (`FINDING-2026-09-09-hq_P-...`, row `flip-gimpel-readl-driver`'s sibling; four Gimpel reds behind it: REDEFINE_driver, COPYL, PERM, PERMS). **This finding adds the root cause and a proven mode-4 cure. It is NOT landed, and the reason is stated at the end.**

## Reproduced, and wider than the witness

hq_P's witness prints `first` then `second` under `sbl -bf` and `second` twice here. Three more witnesses already exist in the corpus with correct refs and are graded by nothing — `define_redef_alt_entry`, `define_redef_three_way`, `define_redef_two_functions` — and on origin the first two are **silent**, printing nothing at all where the oracle prints two and three lines. `define_redef_two_functions` passes, which is the useful control: two DIFFERENT names never collide, so the defect is per-name, not per-DEFINE.

## Root cause, measured rather than reasoned

hq_P located the lowerer keeping `defs[]` keyed by function name with one slot and three overwriting sites. That is true and it is not where the binding is decided. The rest of the chain:

1. Each DEFINE statement lowers to its own **bind node**, and the lowerer attaches that statement's own entry to it. `--dump-ir` on the witness shows exactly that: two DEFINE bind nodes, one carrying `LIT_NAME "F"` and the other `LIT_NAME "G"`. **The information is present and correct in the IR.**
2. The emitted code for a bind node writes a body cell: `lea rax, [rip + LBL__G]` then `mov [body_cell$F], rax`. The template's own comment says why — *"body_cell$<FN> <- &LBL__<this DEFINE's entry>, so a call reads the binding in force when it runs"*. **The mechanism for executable DEFINE was already built.**
3. **The defect:** the driver, not the lowerer, decides which label each bind writes. For every bind node it looks the function up **in the proc table by name** and follows that proc's graph to its deferred goto to recover an entry (`src/driver/scrip.c`, the `dentry` table build). The proc table holds one proc per name, built from the surviving definition — so both bind nodes resolve to the last DEFINE's entry, and both emit `lea LBL__G`. The per-statement entry the IR carries is never consulted.

## The cure, proven in mode 4

Before building that table from the proc table, use the bind node's own attached entry: scan its operands for the `IR_LIT_NAME`, find the `LBL__<entry>` proc, and use that node. 28 lines in the driver, no new state, no template change, no runtime change.

Measured on hq_P's witness: mode 4 prints `first` / `second`, byte-equal to `sbl -bf`, where origin prints `second` twice.

## Why it is not landed

**Mode 3 is unchanged by it, and a semantic difference between the modes is forbidden** (RULES.md: modes may diverge as an optimization, never as a semantic one). The reason is located, not guessed: the `dentry` table is built only inside the mode-4 branch, and copying that block into the mode-3 path does not help, because the mode-3 bind takes a different arm of the template. That arm is gated on `bb_ab_cell_addr(fname)` being absent, which is exactly the mode-3 case where the runtime cell already exists, so the body seal is skipped and the call reads a cell the driver sealed once from the surviving proc.

**What the next attempt needs, in one sentence:** the mode-3 bind must write the wired cell for the function with the address of *this* DEFINE's entry body at the moment the statement executes — the runtime already knows that address as `body$<entry>`, sealed per label proc, and the open question is only which cell the wired call actually reads (`bb_ab_cell_addr(fname)` versus `body_cell$<fname>`), which one `--dump-bb` of the call site will answer in a single read.

The mode-4 patch is saved at `postoffice/handoff/cto-define-executable-m4-cure-2026-09-09.patch` and the working tree is clean.

## Two hypotheses killed, so nobody re-runs them

- **Building a proc per distinct entry** (a per-entry activation stub named `F$G`) makes the FIRST call correct and leaves every later call silent: the alternate stub gets no `_α` label, because α labels come from the DEFINE statement's activation block and not from the proc, so it is not callable by name. The seal says so out loud under `SCRIP_SEAL_DIAG=1`: `[SEAL] MISS lbl=F$G_α`. Renaming the key to label-safe characters does not help; the label does not exist at all.
- **Re-pointing the name at the raw label body** (`LBL__G`) makes *both* calls produce nothing: a label body is not an activation, so the call arrives with no frame.
