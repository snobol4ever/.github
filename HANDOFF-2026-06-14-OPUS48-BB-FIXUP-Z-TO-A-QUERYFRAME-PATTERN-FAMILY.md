# HANDOFF 2026-06-14 — Opus 4.8, lap 1, 13th session
## GOAL-BB-FIXUP-Z-to-A — FOUR conversions landed; cursor bb_query_frame.cpp → bb_pattern_stub.cpp

### Summary
Opened at cursor `bb_query_frame.cpp` (12th-session advance). The cursor file was non-CLEAN, so I worked it, then swept three more files strictly earlier in Z→A order. **Four conversions, all byte-proven, all gates green, all committed.** Pushes were held for the explicit "perform hand off" trigger and pushed at handoff.

| # | file | violations | language / box | commit |
|---|------|-----------|----------------|--------|
| 1 | bb_query_frame.cpp     | 2→0 | Prolog · IR_QUERY_FRAME            | `d493448` |
| 2 | bb_pattern_unary_s.cpp | 8→0 | SNOBOL4 · ANY/NOTANY/SPAN/BREAK/BREAKX | `681951a` |
| 3 | bb_pattern_unary_i.cpp | 6→0 | SNOBOL4 · LEN/POS/RPOS/TAB/RTAB    | `3ae3d0e` |
| 4 | bb_pattern_stub.cpp    | 3→0 | SNOBOL4 · BAL/ARBNO/FENCE_P/CAPTURE/DEFER (unreachable placeholders) | `7a911f2` |

SCRIP HEAD this session: `7a911f2`. Cursor (tracker): `bb_pattern_stub.cpp`.

### The conversions

**(1) bb_query_frame 2→0** — both violations were `returns_plus` (the file had 4 C `return`s; the `x86("ret")` calls are *instructions*, not C returns). Collapsed the 3-branch `if/return` dispatch (op_sa==0 / op_sb==2 / else) into the canonical **guard early-return + single ternary chain = 2 returns**. A/B over the whole Prolog corpus × modes 2/3/4: only `hello.pl` (the sole IR_QUERY_FRAME firer) differed, and only in three pointer-derived BB-label IDs shifted by an identical constant (+39808, defs+refs in lockstep) — the documented renumber from a differently-sized recompiled object. Normalized `bb<N>_`→`bb#_` → m4 md5-identical. m2/m3 byte-identical (m3 = native in-process execution). Compiled+linked m4 binaries: identical `Hello, World!` rc=0.

**(2) bb_pattern_unary_s 8→0** — 7 `local_vars` + 1 `returns_plus` (the `usl()` helper's return was the over-budget one). Dropped `usl()` (inlined as `(std::string(".Lus")+std::to_string(g_us_seq)+"_s"/"_desc")`), inlined all 7 locals, expressed the five-way kind-dispatch (proto_addr/proto_len/desc_addr) as multi-line ternaries, and `proto_data` as a 5-way ternary appended to the return. The ~250 hand-tuned proto-blob bytes were transformed **programmatically** (a python script extracted all 36 `x86("raw", ...)` payloads verbatim and re-injected them; payloads verified byte-identical pre/post). Kept `static int g_us_seq` + the indented `static char lbuf[24]`. Result: 2 returns, max line 173, 0 blank lines.
  - **KEY FINDING — `emit_intern_str` is dead.** It delegates to `g_flat_intern_str` only in TEXT mode, and `g_flat_intern_str` is **never registered anywhere** (only `=NULL`, the decl, and a macro alias — zero call sites to the setter). So `emit_intern_str()` always returns NULL and the template's label was *always* the `strtab_label` fallback. This removed any double-call/idempotency hazard from inlining the label as `(strtab_label(lbuf, sizeof lbuf, cset), lbuf)`.
  - A/B: firing program covering all 5 kinds + `039_pat_any` + `041_pat_span`, modes 2/3/4 → **zero diffs** (not even label renumbering this time). Normalized m4 md5-identical (`8438ce6…`). Firing m4 = 276 lines, 5 boxes, 31 `.byte` lines.

**(3) bb_pattern_unary_i 6→0** — the integer sibling (LEN/POS/RPOS/TAB/RTAB, ILIT args). 5 `local_vars` + 1 `returns_plus` (the `pul()` helper). Same idiom as (2): dropped `pul()`, inlined the 5 locals. Simpler than the string sibling — no cset/label handling; `n = (long)_.op_ival` goes to `r8d`, `r9d = 0L`, no `r9` cset lea. Same programmatic verbatim-blob transform. A/B: 5 integer kinds + `044_pat_pos` + `045_pat_rpos`, modes 2/3/4 → zero diffs, normalized md5-identical (`61237fe…`). Firing m4 = 261 lines, 5 boxes, 21 `.byte`.

**(4) bb_pattern_stub 3→0** — a *different* idiom. Violations: cv9=2 (the `bb_pattern_stub_str` name, twice) + medium_any=1 (`IF(MEDIUM_TEXT, …)`). **The CV9 here is purely the `_str` NAME** — `cv9_param=0` because the parameter is `const char* which`, not `IR_t*` (only IR_t* params are flagged). So the fix did NOT need to be parameterless. Inlined the `_str` string-builder into the `extern "C" void bb_pattern_stub(const char* which)` wrapper (eliminating the `_str` name, keeping `which`, no emit_core.c change) and collapsed `IF(MEDIUM_TEXT, x86("label", _.lbl_α))` → bare `x86("label", _.lbl_α)`. One `x86("…")` per line (avoids `multi_x86`; note `x86_bomb(` does not contain the substring `x86(` so it doesn't trip it).
  - **The collapse is byte-identical by construction.** From the macros: `IF(c,X) = c ? X : std::string()`, and `x86("label",X)` already returns `std::string()` when `MEDIUM_BINARY || MEDIUM_MACRO_DEF`. So `IF(MEDIUM_TEXT, x86("label",X))` and bare `x86("label",X)` produce identical output in all three mediums (TEXT → label text; BINARY/MACRO_DEF → empty). This is exactly why the byte-identical unary boxes use the bare form; the stub's `IF` wrapper was redundant.
  - **KEY FINDING — the 5 routing opcodes are unreachable.** IR_PATTERN_BAL/ARBNO/FENCE_P/CAPTURE/DEFER have **zero creation sites** anywhere in `src/` (the SNOBOL4 lowering never produces them — they're "builder pending"). So bb_pattern_stub never fires for any current program. Cleaned (not deleted): the emit_core dispatch stays wired for when those builders land.
  - A/B: all 20 SNOBOL4 pattern programs mode-4 compile md5-identical base↔mine (confirms inertness), plus the by-construction proof.

### New idiom (first-of-family) — note for Lon (non-blocking)
`bb_pattern_unary_s` was the **first** `bb_pattern_*` proto-blob file converted; no clean sibling existed to mirror, so it sets the idiom the remaining seven will follow. The idiom is correct and audit-clean but **verbose**: with no locals allowed, the `(_.op_kind ? _.op_kind : "ANY")` kind expression repeats across each of the four ternary chains (proto_addr / proto_len / desc_addr / proto_data), each continuation line kept under 200 chars. A future **`x86_asm.h` vocabulary form** that absorbs the `kind → (proto_addr, proto_len, desc_addr, proto_data)` dispatch internally would slim the whole family (8 files) considerably — worth deciding before converting the remaining siblings (nullary/lit/cat/arb/alt) by hand, since whatever shape you pick propagates.

### Gates (green vs baseline, applied to all four landings)
audit 0 CLEAN · `sno_pat_reg` TIER1+2 HARD 0/0 · SNOBOL4 pattern rung suite 19/19 across all three modes · prolog xcheck 4/0 (3-mode agree) · icon xcheck 4/0 HARD + m4 4/4 · `no_vstack` 3 floor · `no_bb_bin_t` 0 · `no_handencoded_bytes` 0 · `pl_no_value_stack` · `pl_no_new_global` 17/17 floor · `pl_coupling`.

### Pre-existing reds (NOT mine, unchanged, on-hold per PLAN)
- rebus `hello` ROW-DRIFT (the all-langs monitor smoke also fails on the deleted `--monitor` trampoline infra + missing `/home/claude/corpus` clone — both unrelated).
- `bb_call_write_slot.cpp:71` `fprintf` purity rc=1.
- GZ gates gz2–gz7 stale — they expect the pre-GUT "INTERP-FALLBACK" banner that the GUT replaced with PL-GZ FENCE rejection (retarget candidate, per the 12th-session follow-up).

### Cursor mechanics this session
Per the RESUME PROCEDURE, the cursor advances **in step with each file's fix** when that file sorts strictly before the cursor. So: working bb_query_frame (the cursor itself) did NOT advance the cursor; then each of unary_s → unary_i → stub advanced it one step. The dirty `bb_r…`/`bb_s…`/`bb_u…` files (bb_rk_mapgrep, bb_subject, bb_scan_*, bb_unify, bb_unop) sort *after* the cursor and are correctly NOT candidates — Z→A never turns back toward Z.

### NEXT — ordinary Z→A sweep
Next dirty file strictly before `bb_pattern_stub.cpp`: **`bb_pattern_nullary.cpp`** (5 violations = lv4 rp1). It's the same proto-blob idiom as the unary boxes (rt_pattern_build + a proto blob), so the mechanical recipe applies:
1. `view` the file; back it up to /tmp.
2. Extract the `x86("raw", ...)` payload(s) programmatically (verbatim) — do NOT hand-retype blob bytes.
3. Drop any `*ul()`-style helper (its return is the rp violation); inline the locals; if there's a kind-dispatch, use multi-line ternaries (lines <200, one `x86("…")` per line to avoid multi_x86).
4. `audit_bb_fixup_file.sh` → rc=0; rebuild.
5. A/B byte-identity: construct a firing program (pattern primitive assigned to a variable → `IR_DTP_ASSIGN + IR_PATTERN_*`, per lower_snobol4.c:582–594), capture modes 2/3/4 mine, `git stash`, rebuild baseline, capture, diff; normalize `bb<N>_`→`bb#_` (and any local-label prefix) and confirm md5-identical; restore + rebuild.
6. Full gate battery (sno_pat_reg, pattern rung suite, structural, prolog/icon xcheck).
7. Commit SCRIP; advance cursor in `.github/BB-REVAMP-TRACKER.md` (targeted sed on the `^# CURSOR:` line — do NOT read the whole tracker).

Then continue: bb_pattern_lit → bb_pattern_cat → bb_pattern_arb → bb_pattern_alt → onward toward A.

### State notes
- SCRIP source tree CLEAN, matches pushed `7a911f2`; binaries regenerate at setup. ENV needs libgc-dev + libgmp-dev (both in `scripts/install_system_packages.sh`).
- `out/libscrip_rt.so` is the mode-4 link target (NOT `./libscrip_rt.so`); link with `gcc -no-pie file.s -L out -lscrip_rt` and run with `LD_LIBRARY_PATH=out`.
- Process: the context gauge is unobservable to the agent; the user invited a self-estimate each turn (~15/40/52/65/70%) and said "Continue" ×4 then "Perform hand off". All four conversions were committed locally as they landed and pushed only at the handoff trigger.
