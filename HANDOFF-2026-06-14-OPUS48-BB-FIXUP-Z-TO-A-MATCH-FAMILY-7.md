# HANDOFF 2026-06-14 — Opus 4.8, lap 1, 16th session
## GOAL-BB-FIXUP-Z-to-A — seven bb_match_* conversions; cursor bb_pattern_alt.cpp → bb_match_len.cpp

### Summary
Cold start. Ran the RESUME PROCEDURE: tracker `# CURSOR:` read `bb_pattern_alt.cpp`; audited it → CLEAN (rc=0); per step 3 swept the dirty `bb_match_*` range strictly before it, Z→A, one file per step. **Seven conversions landed, all byte-proven, all gates green, all pushed at the handoff trigger.** The pushes were held for the explicit "perform hand off" (PLAN.md:102).

| # | file | violations | language / box | pushed commit |
|---|------|-----------|----------------|---------------|
| 1 | bb_match_tab.cpp | 1→0 | SNOBOL4 · IR_PAT_TAB | `2495b84` |
| 2 | bb_match_span_var.cpp | 4→0 | SNOBOL4 · IR_PAT_SPAN_VAR (dormant) | `a9a2c80` |
| 3 | bb_match_span.cpp | 3→0 | SNOBOL4 · IR_PAT_SPAN | `fd43adb` |
| 4 | bb_match_rtab.cpp | 1→0 | SNOBOL4 · IR_PAT_RTAB | `9ea06c7` |
| 5 | bb_match_pos.cpp | 2→0 | SNOBOL4 · IR_PAT_POS / IR_PAT_RPOS | `0c49867` |
| 6 | bb_match_notany.cpp | 3→0 | SNOBOL4 · IR_PAT_NOTANY | `4c3de60` |
| 7 | bb_match_len.cpp | 1→0 | SNOBOL4 · IR_PAT_LEN | `81b63f1` |

SCRIP origin HEAD after handoff: **`81b63f1`**. Cursor (tracker): **`bb_match_len.cpp`**.
Tree dirty among my files: **all CLEAN**. Whole-tree dirty count moved 83 → 76 by my work (then 76 → 78 after rebasing in concurrent work that re-dirtied `bb_pattern_unary_s.cpp` — not mine; it sorts behind the cursor toward Z).

### HEAD drift this session (clean throughout — THREE rebases)
Started at `448f529` (already past the 15th-session `ef1ce99`; concurrent SNOBOL4 PB-RB-5 single-var cset work had landed). During handoff the remote advanced twice more:
- `448f529 → bf1dc97` ("IR_CALL split rung 4 — 5th kind GVAR_USERPROC, dormant"); touched `bb_pattern_unary_s.cpp` only — no `bb_match_*`.
- `bf1dc97 → cf2e1d5` ("Prolog GZ catch/throw step 4: catch box → m3/m4 100→104"); no `bb_match_*`.

My 7 commits rebased cleanly each time (`git diff` confirmed no collision with any swept file); the combined tree was rebuilt + re-certified green before the final push to `81b63f1`.

### The conversions — idioms used
All seven were **`local_vars`-only** violations (declarations inside the `*_str()` body). Two idiom shapes, both already established by the 13th–15th-session pattern-family work:

1. **Trivial scalar inline** (`tab`, `rtab`, `len`): the sole `long n = (long)(int)_.op_ival;` folded directly into each `x86()` arg where used (`len` uses it twice). The `(int)` truncation cast preserved verbatim.

2. **String-cset + fn-ptr inline** (`span`, `span_var`, `notany`): the `cs`/`lbl`/`ca`/`sf` cluster. Inlined:
   - `cs`  → `(_.op_sval ? _.op_sval : "")`
   - `ca`  → `(uint64_t)(uintptr_t)(const void *)(_.op_sval ? _.op_sval : "")`
   - `sf`  → `(uint64_t)(uintptr_t)(void *)(const char *(*)(const char *, int))strchr`
   - `lbl` → the **comma-operator idiom** `(strtab_label(b, sizeof b, …), b)`, dropping the dead `emit_intern_str` call. The allowed `static char b[24]` stays.

   `bb_match_pos` adds an `is_rpos` dispatch local → inlined `(_.op_sval && _.op_sval[0] == 'r')` at both the comment ternary and the POS/RPOS dispatch ternary; it handles **both** opcodes (one template).

### emit_intern_str RE-CONFIRMED DEAD at this HEAD
`lower_flat_set_intern_str` (emit_bb.c:241, the only setter of `g_flat_intern_str`) has **zero call sites** (only def + decl emit_bb.h:21 + macro-alias emit_bb.h:49). So `g_flat_intern_str` stays NULL → `emit_intern_str` always returns NULL → the original `if(!lbl)` fallback branch is always taken → the comma-operator inline is exactly equivalent. This is the same finding the 13th/14th sessions documented; verified again here by grep before relying on it.

### ⚠️ KEY CORRECTNESS FINDING — bb_match_notany unconditional strtab_label (A/B caught it)
The naive `notany` inline — moving `strtab_label` into the multi-char branch of the single/multi dispatch — **diverged in m4** and was caught by the firing A/B (NOT by construction). Root cause: the original calls `strtab_label(b, sizeof b, cs)` **unconditionally** (its `if(!lbl)` branch) *before* the dispatch, so even the single-char fast path (`NOTANY("X")`) interns the cset string into the string table — emitting a `.S<n>` entry it never references. Dropping that side effect on the single-char path made the interned string vanish and **renumbered every later `.S` label**. Fix: keep `strtab_label(b, sizeof b, _.op_sval ? _.op_sval : "");` as an **unconditional bare statement** (not a local-var decl → audit-clean), then use `b` directly in the multi-char lea. **Lesson for the remaining string-cset boxes (`bb_match_break`, `bb_match_breakx`, `bb_match_any`, `bb_match_capture`, `bb_match_defer`): check whether their `strtab_label` / interning call is unconditional before folding it into a conditional branch — preserve the side-effect position.**

### Proof — direct A/B byte-identity (strongest standard)
Each file proved against its own baseline (the pre-edit version from `git show HEAD:…` or a `git stash`), across all three modes, with a firing program that emits the actual box:

- **Live boxes** (`tab`, `span`, `rtab`, `pos`, `notany`, `len`): direct firing, no vehicle. e.g. `S SPAN("0123456789").X` (2 boxes), `S POS(3) LEN(2).X / S RPOS(2) LEN(2).Y` (both arms), `NOTANY("X")` + `NOTANY("xyz")` (both dispatch arms). m2 (`--interp`), m3 (`--run`, native in-proc), m4 (`--compile`) **all raw byte-identical**, m4 identical sha256 (no BB-label normalization needed — pure inlining left emission order + sizes unchanged; the one exception, notany's first attempt, is the bug above, fixed and re-proven identical).
- **Dormant box** (`span_var`): `IR_PAT_SPAN_VAR` has **no frontend creation site** (variable-cset SPAN lowers to `IR_PAT_SPAN`+`ival=1` and runs through `bb_match_span` with rt_scan deferral; the SPAN_VAR retag is builder-pending — same shape as the 14th-session `bb_pattern_stub`). Proven via a **throwaway lowering retag vehicle**: temporarily set `nd->op = IR_PAT_SPAN_VAR` in the TT_SPAN var-branch (uncommitted), forced the box to fire, A/B'd my template vs baseline through that retag (m2/m3/m4 byte-identical, m4 identical sha256), then reverted the retag and confirmed the working tree held only the template change.

After each A/B the committed working file was rebuilt and re-emitted to confirm it reproduces the exact proven asm (sha256 match).

### Gates (green on the final combined rebased tree)
audit 0 CLEAN (all 7 files) · `sno_pat_reg` TIER1+2 HARD 0/0 · SNOBOL4 pattern rung 038–057 **19/19 across all three modes** · prolog xcheck 4/0 (3-mode agree) · icon xcheck 4/0 HARD + m4 4/4 · `no_bb_bin_t` 0 · `no_handencoded_bytes` 0 BAD · `no_vstack` 3 floor (rt.c/rt.h, unchanged).

### Pre-existing reds (NOT mine, unchanged, on-hold per PLAN)
- rebus `hello` ROW-DRIFT (the all-langs monitor smoke also fails on deleted `--monitor` infra + missing `/home/claude/corpus`).
- `bb_call_write_slot.cpp:71` `fprintf` purity rc=1.
- GZ gates gz2–gz7 stale — expect the pre-GUT "INTERP-FALLBACK" banner the GUT replaced with PL-GZ FENCE rejection (retarget candidate).

### Cursor mechanics this session
Per the RESUME PROCEDURE, the cursor advances **one step** as each file (sorting strictly before the cursor) lands: `bb_pattern_alt → bb_match_tab → bb_match_span_var → bb_match_span → bb_match_rtab → bb_match_pos → bb_match_notany → bb_match_len`. The dirty `bb_match_capture`/`bb_match_defer`/`bb_match_breakx`/… files all sort *before* the cursor toward A and are the ongoing sweep — Z→A never turns back toward Z.

### NEXT — ordinary Z→A sweep, continuing the bb_match_* range
Computed mechanically from a fresh `audit_bb_fixup_rank.sh` with the new cursor (`bb_match_len.cpp`): the next dirty file sorting strictly before it is **`bb_match_defer.cpp`** (2 violations). Then `bb_match_capture` (6) → `bb_match_breakx` (3) → onward toward A.

**Re-run `audit_bb_fixup_rank.sh` at the start of each session — do not trust prior counts** (the rebased-in concurrent work shifts the dirty list; e.g. `bb_pattern_unary_s` got re-dirtied this session and now sits behind the cursor).

Recipe for the remaining `bb_match_*` files:
1. `view` the file; `audit_bb_fixup_file.sh <path>` (full path under `src/emitter/BB_templates/`) for the exact local(s).
2. Scalar/offset local → fold into the `x86(...)` arg. fn-ptr → inline the cast on the call line. String-cset cluster → the `cs`/`ca`/`sf` inlines + `(strtab_label(b,sizeof b,…), b)` comma-operator, keeping `static char b[24]`. **If there is an unconditional `strtab_label`/intern call before a branch, KEEP it unconditional (bare statement) — see the notany finding.**
3. Rebuild; `audit` → rc=0; longest line ≤200, zero blank lines.
4. A/B byte-identity across m2/m3/m4 vs a `git stash` (or `git show HEAD:…`) baseline; normalize `bb<N>_`→`bb#_` only if needed (these needed none). After restoring your edited file, rebuild and confirm it re-emits the proven asm (sha256).
5. Full gate battery (sno_pat_reg, pattern rung 038-057, prolog/icon xcheck, no_bb_bin_t, no_handencoded_bytes, no_vstack).
6. Commit SCRIP; advance the cursor in `.github/BB-REVAMP-TRACKER.md` via a targeted `sed` on the `^# CURSOR:` line — do NOT read the whole tracker.

### State notes
- SCRIP source tree CLEAN, matches pushed `81b63f1`; binaries regenerate at setup. ENV needs libgc-dev + libgmp-dev (both in `scripts/install_system_packages.sh`).
- `out/libscrip_rt.so` is the mode-4 link target (NOT `./libscrip_rt.so`); link `gcc -no-pie file.s -L out -lscrip_rt`, run with `LD_LIBRARY_PATH=out`.
- A handy A/B vehicle for any **dormant** pattern box: the throwaway lowering-retag trick (force `nd->op` to the dormant opcode in the relevant lower_snobol4.c branch, A/B, revert). The per-kind audit tool (`emit_per_kind_audit.c`, `--audit-per-kind`) constructs every opcode but is **unlinked** in the production `scrip` binary, so it's not directly usable without a custom link target.
- Process: context gauge unobservable to the agent; the user invited a self-estimate before each turn (~13/25/40/52/60/68/74%) and said "Continue" ×6 then "Perform hand off". Each conversion was committed locally as it landed and everything pushed only at the handoff trigger, after three `pull --rebase` cycles and a combined-tree re-certification. Stopped at a clean 7-conversion boundary with margin rather than starting the heavier `bb_match_defer`/`capture` files mid-budget.
