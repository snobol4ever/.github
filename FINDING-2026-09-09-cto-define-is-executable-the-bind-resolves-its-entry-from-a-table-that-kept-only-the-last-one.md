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

## Addendum, same sitting: why mode 3 cannot be cured by re-pointing anything

The next step the ceo asked for is done, and it changes the shape of the remaining work.

I built the `dentry` table in the mode-3 path as well, gave each bind its own label name, added a mode-3 arm to the bind template, and a runtime helper that writes **both** candidate cells for the function — the wired cell `bb_ab_cell_addr(fname)` and `body_cell$<fname>` — from the sealed `body$<entry>` of that DEFINE's own entry. Instrumented, all of it runs and all of it is correct:

```
[bind]   fname=F lbl_t0=LBL__F cell=0x...4d28      (first DEFINE, at its own site)
[rtbind] F <- LBL__F cell=body$F src=... *src=0x...1125
second                                              (the call, ignoring both writes)
[bind]   fname=F lbl_t0=LBL__G cell=0x...4d28
[rtbind] F <- LBL__G cell=body$G src=... *src=0x...124f
second
```

**The mode-3 call does not read any cell.** It is wired straight to the body chosen when the slab was sealed, which is what "the wiring is the execution" means. Writing `alpha$F`, `body_cell$F`, or the runtime cell at run time therefore cannot change which body a statically wired call reaches, and no amount of re-pointing will.

**So the mode-3 half is not a cell fix, it is a dispatch decision:** a function whose name carries MORE THAN ONE DEFINE in the program text must be dispatched **indirectly**, the way a run-time-defined function already is (`rt_sno_runtime_define` clears `p->fn` precisely to force the by-name path). The lowerer already detects the collision — it is the `defs[]` overwrite this finding starts from — so the condition is known at compile time and costs nothing for the overwhelming majority of programs, which define each name once.

That is a change to how a call is wired, not to how a bind writes, so it wants the ceo's word before it lands. The mode-4 cure remains held for the same reason it was held: a semantic difference between the modes is not licensed.
