# FINDING — frame-rsp's "no home" capture abort was `havehome()` omitting the ordinary flat slot, not a zd_plan bug; beauty.sno now clears that abort but hits a second, unrelated, pre-existing defect (genuine SIGSEGV, not a bomb trap)

**Session:** 2026-08-23 seat02 (`/home/claude02`, Claude Sonnet 5), THE LOOP task `zeta-frame-rsp-capture-home` (postoffice task file, converted from QUEUE.tsv by hq_C 2026-08-22, owner hq_P). Resumed from an unfinished claim with no prior WIP (both SCRIP and corpus were clean/pushed at session start). Final watermark: SCRIP (this session's commit, below), corpus unchanged, `.github` this commit.

⛔ **ROW CLOSED (hq_C ruling, 2026-08-23, in-chat), but frame-rsp is STILL A DEAD ARM — do not read this closure as "frame-rsp works".** This row's binding prose was scoped to the one named defect below, and that defect is genuinely cured. It is not scoped to "beauty.sno runs end-to-end under frame-rsp" — that remains false. The continuation (a second, different-root-cause SIGSEGV) is split off as its own task: `zeta-frame-rsp-second-wild-write.task.md`.

## THE NAMED DEFECT — located, not guessed

`--zeta-storage=frame-rsp` aborted on ANY SNOBOL4 pattern capture (`. VAR` / `$ VAR`) with `IR_MATCH_CAPTURE_SAVE/COND/IMM: no home ... classifier and ZD plan disagree` (`src/templates/bb_match_capture.cpp`). Smallest repro (3 lines, `X = "HELLO WORLD"` / `X LEN(5) . Y` / `OUTPUT = Y`) reproduces it standalone — this was never an edge case, it was **every** capture under frame-rsp.

**Root cause, traced via ASM-DIFF-FIRST:**
- `zd_plan()` (`src/emitter/emit.cpp:2394-2395`) — the mechanism that grants a capture node `op_zres` (a register-resident "ζ-SPINE cell") — unconditionally no-ops (`if (!_zd || x86_port_mode() != ZC_PORT_FORTH || n <= 0) return;`) whenever the port mode isn't `ZC_PORT_FORTH`. `--zeta-storage=frame-rsp` sets port mode to `ZC_PORT_CSTACK` (`rt_zeta_alloc.c:160`). **This gating is deliberate and correct** — zd_plan's register-carve discipline is cell-stack-specific by design (ARCH-ICON.md's "FORTH-style port cells" description) — and is NOT what I changed.
- `frame_need_of()` (`emit.cpp:746`) — the structural hazard classifier (DEFER-crossing / ALT-arm / repeat-body) — is completely port-mode-agnostic, and correctly so: it answers "does this specific node's capture cross a lifetime hazard," a question independent of storage backend. When it says "no" (the common case), the ORIGINAL design intent (visible in `writehome()`/`readhome()`'s existing `_.op_zres ? ZRESD(0) : FR(_.op_off)` fallback) was that *some* home would still exist. But `havehome()` (`bb_match_capture.cpp:15`) only checked `_.op_zres || _.op_cap_anchor` — and `cap_anchor_of()` is a permanent stub returning 0 (`emit.cpp:973`, dead/future machinery). So under any port mode where zd_plan is inert, a non-hazardous capture had **zero** paths to a home, despite the function's own first guard (`_.op_off < 0 → bomb`) already having proven a valid ordinary flat slot exists for every node that reaches this far.

**Cure (`src/templates/bb_match_capture.cpp`, 1 line):**
```c
static inline int havehome(void) { return _.op_zres || _.op_cap_anchor || _.op_off >= 0; }
```
Since the function's first ternary arm already refuses `op_off < 0` before any of these branches run, `_.op_off >= 0` is unconditionally true by the time `havehome()` is evaluated — so this makes the "no home" bomb arms provably unreachable, using exactly the fallback location (`FR(_.op_off)`) the code already trusted for the (currently dead) `op_cap_anchor` case. No zd_plan change, no frame_need_of change, no new global (per the FACT RULE — this reuses an existing field).

## VERIFICATION

- Minimal repro: aborted before, `HELLO` printed correctly after, under `--zeta-storage=frame-rsp`, mode 3.
- **Cell-stack byte-identity (the DONE-WHEN's second clause), proven via `git stash` before/after, not inferred:**
  - `beauty.sno --compile` (mode 4 `.s`): **byte-identical**.
  - `beauty.sno --run` (mode 3 stdout): **byte-identical**.
  - `160_pat_alt_inner_gen_resume.sno`, `demo_treebank.sno` (mode 3 stdout): **byte-identical**. (Note: `160_pat_alt_inner_gen_resume` is no longer a standing red as of this session — closed by seat01 earlier the same day per `FINDING-2026-08-23-seat02-pat-fence-eps-recur-shallow-link.md` line 38 — but its *output* is unaffected by this patch either way, which is the actual requirement.)
  - `test_gate_emit_no_lang.sh`, `test_gate_template_medium_invisible.sh`: **byte-identical** stdout, both rc=0.
  - Full `test_corpus_snobol4.sh` (360 rows, cell-stack, both m3+m4): **359/360 pass, identical to the standing baseline** — the only red is `demo_treebank` (a pre-existing, unrelated red; not this row's mechanism).
  - `beauty.sno` mode-4 binary (compile→`gcc -c`→link→run) under cell-stack: output byte-identical to mode-3.
- Frame-rsp, mode 3 AND mode 4: `grep -c "no home"` on both emitted `.s` files for `beauty.sno` = **0**. The named abort is completely gone, in both modes.

## OUT OF SCOPE, FOUND NOT CHASED — beauty.sno still does not reach exit 0 under frame-rsp

With the named defect cured, `beauty.sno` under `--zeta-storage=frame-rsp` runs much further but then **segfaults** (SIGSEGV, both mode 3 in-process and the mode-4 compiled binary — confirmed via gdb backtrace landing in unsymbolized JIT'd code called through `rt_outer_call`). This is a **different failure mode**, not a re-hit of the same class:

- A minimal isolated ARBNO+capture witness (`X ARBNO("A") "AAA" . Y`) under frame-rsp hits a *different*, pre-existing bomb: `IR_MATCH_ARBNO: body contains a DEFER unsafe for the plain-frameless arm ... ARBNO-FRAME slot unavailable` (`bb_match_arbno.cpp:223`). That bomb text is already tracked elsewhere (`GOAL-SNOBOL4-100.md` line 840, in an unrelated DEFER-hang investigation `ptw_min_defer2_hang`) — it is a real, independently-known rough edge in ARBNO's frame-slot classification, not something this session introduced, and not gated on port mode the way the capture defect was (`emit_match_rbp()` defaults ON regardless of `ZC_STORAGE`).
- However, that ARBNO bomb aborts via `rt_bomb`+`ud2` → SIGABRT/SIGILL, not SIGSEGV — so it is very unlikely to be the literal cause of beauty.sno's crash. Beauty's crash is a genuine wild-memory-access, evidenced by `Segmentation fault` (not `Aborted`) on both mode 3 and the linked mode-4 binary. **This is an uncharacterized, separate defect** — beauty.sno is a ~1000+ line self-host program with far more ARBNO/DEFER/COLLECTION combinations than a hand-minted witness can quickly triangulate, and finding it would need its own ASM-DIFF-FIRST pass (most likely a bisection of beauty.sno's statement list, or per-statement `.s` diffing against cell-stack, or a build with `ZC_POISON_FILL`'s red-zone poisoning turned up) — a materially different, open-ended investigation from "locate one classifier/ZD-plan disagreement."

**My assumption, carried forward:** the DONE-WHEN's mechanical command (`grep -qi "no home"`) is satisfied and will read as PASS — it only checks for that one string, and it is genuinely gone. The row's own binding prose ("exits 0") is **not yet fully met** — I'm treating that as a known, honestly-reported gap rather than silently declaring victory on the mechanical proxy alone, per the task file's own instruction not to weaken or over-trust the command.

## OUTCOME

One file, one line: `src/templates/bb_match_capture.cpp`. The named "classifier and ZD plan disagree" defect is fully cured and verified regression-free (minimal repro + full 360-row corpus + both required gates + explicit beauty.sno byte-identity in both modes, all via git-stash-backed before/after, not inference alone). `--zeta-storage=frame-rsp` now supports pattern captures generically — the second, larger obstacle to a full beauty.sno self-host under frame-rsp (the SIGSEGV) is a distinct, uncharacterized defect, flagged here for the next session/row rather than chased past this row's evident scope.
