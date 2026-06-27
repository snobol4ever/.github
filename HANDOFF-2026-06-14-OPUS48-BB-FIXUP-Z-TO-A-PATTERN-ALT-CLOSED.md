# HANDOFF 2026-06-14 — Opus 4.8, lap 1, 15th session
## GOAL-BB-FIXUP-Z-to-A — bb_pattern_alt 1→0 CLEAN; bb_pattern_* family closed; cursor bb_pattern_arb.cpp → bb_pattern_alt.cpp

### Summary
Cold start. Ran the RESUME PROCEDURE: the tracker `# CURSOR:` line read `bb_pattern_arb.cpp`; audited it → CLEAN (rc=0); per step 3, computed the next dirty file sorting strictly before it (Z→A) = **`bb_pattern_alt.cpp`** (1 violation, `lv=1`), matching the 14th-session NEXT. One conversion, byte-proven, all gates green, committed and pushed. The push was held for the explicit "perform hand off" trigger.

| # | file | violations | language / box | pushed commit |
|---|------|-----------|----------------|---------------|
| 1 | bb_pattern_alt.cpp | 1→0 | SNOBOL4 · IR_PATTERN_ALT | `ef1ce99` |

SCRIP origin HEAD after handoff: **`ef1ce99`**. Cursor (tracker): **`bb_pattern_alt.cpp`**.

**This closes the entire `bb_pattern_*` family** — all 11 files now CLEAN: nullary, unary_s, unary_i, stub, lit, cat, arb, alt (plus the earlier members).

### HEAD drift this session (clean throughout)
Started at `89e8dd0`. The remote advanced **`89e8dd0 → 2fd0755`** during the session — one concurrent commit, "IR_CALL split Rung 1: recognize IR_CALL_* at the 3 emit-path dispatch consumers (dormant)". `git show --stat 2fd0755` confirms it touched **no `bb_pattern_*` file**. My commit (`af1950c`) rebased cleanly on top → **`ef1ce99`**; I rebuilt the combined tree and re-certified (audit 0 + pattern rung 19/19 + sno_pat_reg HARD + prolog/icon xcheck) before pushing.

### The conversion
**bb_pattern_alt 1→0** (`lv1`) — the trivial `fn`-inline shape, identical to the already-landed `bb_pattern_cat`. The single violation was the `fn` local:
```c
uint64_t fn; { void (*fp)(DTP_FRAG_t*,const DTP_FRAG_t*,const DTP_FRAG_t*) = rt_pattern_stitch_alt; fn=(uint64_t)(uintptr_t)(void*)fp; }
```
Dropped it and inlined the full function-pointer cast directly into the call argument:
```c
+ x86("call",    "rt_pattern_stitch_alt", (uint64_t)(uintptr_t)(void*)(void(*)(DTP_FRAG_t*,const DTP_FRAG_t*,const DTP_FRAG_t*))rt_pattern_stitch_alt)
```
Two `str_replace` edits. No blobs, no dispatch, no helper. Longest line 159 chars (≤200); zero blank lines. The result is structurally identical to `bb_pattern_cat` (verified side-by-side).

### Proof — direct A/B byte-identity (strongest standard)
Firing program (`/tmp/alt_fire.sno`):
```
    P = "a" | "b" | "c"
    Q = "xx" | "yy"
END
```
This lowers via `lower_snobol4.c:545` (≥2 quoted-literal alternatives → `IR_PATTERN_LIT` leaves chained by `IR_PATTERN_ALT`) and **fires 3 `IR_PATTERN_ALT` boxes** in m4 (one per chain join: `a|b`, `(a|b)|c`, `xx|yy`).

Captured mine, `git stash`, rebuilt baseline `89e8dd0`, captured, diffed:
- m2 (`--run`): **byte-identical**
- m3 (`--run`, native in-process): **byte-identical**
- m4 (`--compile`): asm **raw byte-identical** — zero diffs, no BB-label normalization even needed

Pure inlining left emission order and object sizes unchanged, so C2 holds by construction *and* by direct byte-identity — exactly as the sibling cat/arb conversions.

### Gates (green on the combined rebased tree)
audit 0 CLEAN · `sno_pat_reg` TIER1+2 HARD 0/0 · SNOBOL4 pattern rung 038–057 **19/19 across all three modes** · prolog xcheck 4/0 (3-mode agree) · icon xcheck 4/0 HARD + m4 4/4 · `no_bb_bin_t` 0 · `no_handencoded_bytes` 0 BAD · `no_vstack` 3 floor (the rt.c/rt.h references, unchanged).

### Pre-existing reds (NOT mine, unchanged, on-hold per PLAN)
- rebus `hello` ROW-DRIFT (the all-langs monitor smoke also fails on deleted `--monitor` infra + missing `/home/claude/corpus`).
- `bb_call_write_slot.cpp:71` `fprintf` purity rc=1.
- GZ gates gz2–gz7 stale — expect the pre-GUT "INTERP-FALLBACK" banner the GUT replaced with PL-GZ FENCE rejection (retarget candidate).

### Cursor mechanics this session
Per the RESUME PROCEDURE, the cursor advances **one step** as the file (sorting strictly before the cursor) lands: `bb_pattern_arb.cpp` → `bb_pattern_alt.cpp`. The dirty `bb_match_*`/`bb_mapgrep`/`bb_unify` files all sort *before* the cursor toward A and are the ongoing sweep — Z→A never turns back toward Z.

### NEXT — ordinary Z→A sweep into the bb_match_* range
Computed mechanically from a fresh `audit_bb_fixup_rank.sh` with the new cursor (`bb_pattern_alt.cpp`): the next dirty file sorting strictly before it is **`bb_match_tab.cpp`** (1 violation = `lv1`). Then `bb_match_span_var` (4) → `bb_match_span` (3) → `bb_match_rtab` (1) → `bb_match_pos` (2) → onward toward A per the audit rank.

**Correction vs the 14th-session projection:** that handoff projected `bb_match_tab (3)`; the fresh audit shows `bb_match_tab = 1` (lv-only). The live audit is authoritative — re-run `audit_bb_fixup_rank.sh` at the start of each session rather than trusting prior counts.

Recipe for the `bb_match_*` range (mostly `lv`-only, mechanical):
1. `view` the file; `audit_bb_fixup_file.sh` to see the exact local(s).
2. If `fn`-style → inline the cast on the call line (verify the runtime fn's exact signature). If a scalar/offset local → fold it into the single `x86(...)` arg expression where used. If a proto-blob → use the established idiom (drop helper, extract `x86("raw",…)` programmatically, inline locals, splice verbatim).
3. Rebuild; `audit` → rc=0; check longest line ≤200 and zero blank lines.
4. A/B byte-identity across m2/m3/m4 vs a `git stash` baseline; normalize `bb<N>_`→`bb#_` only if needed (the pattern-family conversions have needed none).
5. Full gate battery (sno_pat_reg, pattern rung 038-057, prolog/icon xcheck, no_bb_bin_t, no_handencoded_bytes, no_vstack).
6. Commit SCRIP; advance the cursor in `.github/BB-REVAMP-TRACKER.md` (targeted `sed` on the `^# CURSOR:` line — do NOT read the whole tracker).

### State notes
- SCRIP source tree CLEAN, matches pushed `ef1ce99`; binaries regenerate at setup. ENV needs libgc-dev + libgmp-dev (both in `scripts/install_system_packages.sh`).
- `out/libscrip_rt.so` is the mode-4 link target (NOT `./libscrip_rt.so`); link `gcc -no-pie file.s -L out -lscrip_rt`, run with `LD_LIBRARY_PATH=out`.
- The `bb_pattern_*` family is fully retired. The trivial fn-inline idiom (`cat`/`alt`) and the proto-blob inline idiom (`nullary`/`lit`/`arb`/`unary_*`/`stub`) are both well-exercised; the `bb_match_*` range ahead is predominantly `lv`-only and should be straightforward.
- Process: the context gauge is unobservable to the agent; the user invited a self-estimate (~22% then ~25%) and said "Continue" then "Perform hand off". The conversion was committed locally as it landed and pushed only at the handoff trigger, after `pull --rebase` (the remote advanced once during the session) and a combined-tree re-certification.
