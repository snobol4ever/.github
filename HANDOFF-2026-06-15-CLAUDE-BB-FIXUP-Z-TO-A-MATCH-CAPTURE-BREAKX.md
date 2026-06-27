# HANDOFF — GOAL-BB-FIXUP-Z-to-A, 18th session (Claude Opus 4.8)
## bb_match_capture 6→0 + bb_match_breakx 3→0 — BOTH CLEAN, LANDED + PUSHED. Cursor ADVANCED bb_match_defer.cpp → bb_match_breakx.cpp.

**SCRIP HEAD pushed: `e4e0e5e`** (breakx), preceded by `ee4a731` (capture), rebased onto `e98ca10`.
**.github:** this handoff + GOAL watermark (18th-session entry) + cursor advance in BB-REVAMP-TRACKER.md (`# CURSOR:` line only). PLAN.md goals table NOT edited. Tracker not otherwise opened.

---

## WHAT LANDED (two commits)

Two more bb_match_* string-cset boxes made parameterless-clean, continuing the Z→A sweep from the 17th session's bb_match_defer.

### (1) bb_match_capture — `ee4a731` — 6→0 (3 local_vars + 3 returns_plus)
SNOBOL4 `IR_PAT_ASSIGN_COND`/`IR_PAT_ASSIGN_IMM` (the `. VAR` / `$ VAR` pattern capture), driven by `flat_drive_capture` (emit_bb.c:392). That driver emits a **SAVE box (ival=0)** at the start of the capture and a **COND box (ival=1)** or **IMM box (ival=2)** at the end — so every capture fires BOTH a SAVE and a COND-or-IMM box.

- Dropped the 3 flagged locals (`sk`/`va`/`fn`) plus the unflagged `vn`/`lbl`.
- Collapsed 5 returns → 2 (PLATFORM guard + one ternary).
- **NOTANY HAZARD APPLIES (preserved).** The original calls `strtab_label` UNCONDITIONALLY (line 20; `emit_intern_str` dead → `if(!lbl)` always taken) **before** the `sk` dispatch — so even a `sk==0` SAVE box (which never uses `lbl`) interns its varname, emitting a `.S` it never references. Folding `strtab_label` into the lea (sk!=0 only) would skip interning on SAVE boxes and renumber all later `.S`. Fixed with a comma-operator AFTER both bombs but BEFORE the dispatch:
  `: (strtab_label(b, sizeof b, _.op_sval?_.op_sval:""), (int)_.op_ival==0 ? SAVE : COND/IMM)`.

### (2) bb_match_breakx — `e4e0e5e` — 3→0 (3 local_vars; already returns-clean)
SNOBOL4 `IR_MATCH_BREAKX` (the `BREAKX(cset)` extended-break). **SINGLE-LINEAR box — no dispatch** (two sequential `lea ... lbl` / `call strchr` sites on one emission path, plus the β backtrack-extend section), so the notany hazard does NOT apply.

- Kept `strtab_label` as an UNCONDITIONAL BARE STATEMENT (the notany idiom).
- Inlined `ca` → `(uint64_t)(uintptr_t)(const void*)(_.op_sval?_.op_sval:"")`, `sf` → `(uint64_t)(uintptr_t)(void*)(const char*(*)(const char*,int))strchr`, and `z`/`zo` → `FR(_.x86_scratch_off)` / `FR(_.x86_scratch_off + 4)` — the **arb idiom** (`bb_match_arb.cpp`, already CLEAN, uses `FR(_.x86_scratch_off + 4)` directly, proving `FR` parenthesizes its arg, so `+ 4` binds correctly).

### emit_intern_str RE-CONFIRMED DEAD at this HEAD
`g_flat_intern_str` is `=NULL` (emit_bb.c:212); its sole setter `lower_flat_set_intern_str` exists only in `src/attic/emitter/emit_bb.c` (dead residue) with ZERO call sites → always NULL → `emit_intern_str` always returns NULL → the original `if(!lbl)` branch is always taken → bare-`strtab_label` inline is exactly equivalent.

---

## VERIFICATION — C2 by DIRECT A/B byte-identity (strongest standard)

Firing programs (SNOBOL4 space-form `SUBJ PAT . CAP`, the form that engages native pattern boxes — NOT the `?`/literal-subject form):
- **capture:** `cap_cond` (`. V` → SAVE+COND), `cap_imm` (`$ W` → SAVE+IMM), `cap_both` (both + a third `. Z`) → fires **3 SAVE + 2 COND + 1 IMM** boxes.
- **breakx:** `bx_simple` (`BREAKX(",") . V`), `bx_extend` (`BREAKX(",") "xyz"` forces backtrack-extend), `bx_both`.

Results (initial baseline = git-stash of each file; **re-certified at handoff** against the rebased tree, see below):
- **m2 (`--run`): identical** base==mine (empty for these programs — see note).
- **m3 (`--run`, native in-process): identical** base==mine (capture: world/123/foo; breakx: abc).
- **m4 (`--compile`): RAW BYTE-IDENTICAL** for all 6 programs — zero diffs, **no BB-label normalization needed** (pure inlining left emission order + object sizes unchanged, exactly as defer/notany). m4 binaries assemble (`as --64`) + link (`gcc -no-pie … libscrip_rt.so -lgc -lm -lstdc++`) + run, matching m3.

**NOTE — m2 is EMPTY for these pattern programs in BOTH base and mine.** Mode 2 is the IR-graph interpreter; it does NOT use BB templates at all, so an emitter-template change is inert to m2 by construction. Live coverage is m3 (native, correct output) + m4 (compile, byte-identical). This is expected, not a regression.

---

## ⚠️ HEAD DRIFT + MANDATORY RE-A/B (this is the session's one subtlety)

HEAD advanced **`476af37` → `e98ca10`** during the session (one rebase at handoff). The two concurrent commits:
- `b4ef415` "PL-GZ DYNITER rail: dynamic preds store-backed + enumerable"
- `e98ca10` "dead-code sweep: excise input/yyunput/unput from pascal/raku/rebus lexers"

**These TOUCHED `emit_bb.c` (155 lines — and `flat_drive_capture` lives in emit_bb.c!) + `emit_core.c` + `lower_snobol4.c`** — i.e. emission dependencies of my boxes. So a plain "rebases cleanly" was NOT sufficient; I did a **full re-A/B on the rebased combined tree**:
- Baseline = rebased tree with ONLY my 2 template files reverted to their `e98ca10` originals (`git checkout e98ca10 -- bb_match_capture.cpp bb_match_breakx.cpp`), built fresh.
- Result: all 6 firing programs m2/m3 identical + **m4 RAW BYTE-IDENTICAL** → the emit_bb.c change does NOT alter the bytes emitted by/around capture+breakx.

My 2 commits rebased cleanly → `ee4a731` / `e4e0e5e`; combined tree rebuilt + all gates re-run green before push.

**LESSON (re-affirming prior watermarks):** when the rebase diff touches emit_bb.c / emit_core.c / x86_asm.h / lower_*, re-A/B against a baseline built ON the rebased tree (revert only your files) — not just "git rebased without conflict."

---

## GATES (green on final rebased combined tree)
- audit `bb_match_capture` → 0 CLEAN; audit `bb_match_breakx` → 0 CLEAN.
- `sno_pat_reg --strict` → TIER 1 (Σ/Σlen bake) = 0, TIER 2 (r10) = 0, both HARD.
- pattern rung suite (`test_snobol4_pat_rung_suite.sh`) → rc=0 (identical base==mine modulo the TIME line).
- `no_bb_bin_t` → 0. `no_handencoded_bytes` → 0. `no_vstack` → 3 floor (src/attic/runtime/rt/rt.c + rt.h).

### ⚠️ PRE-EXISTING REDS — MUCH HEAVIER AT THIS HEAD, ALL proven base==mine (NOT mine)
Flagged for a future non-hygiene session — these regressed under the concurrent DT_C/DT_E EVAL-datatype emission + PL-GZ dynamic-rail + dead-code-sweep work that landed `3ed602b → e98ca10`:
- **SNOBOL4 crosscheck (m4):** PASS=166 FAIL=87 SKIP=8 — far worse than the 17th-session state at 3ed602b. Verified **base3==mine** per-program (identical), so not my conversions.
- **prolog xcheck:** PASS=0 FAIL=4 SKIP=136 (all-fail) — verified base==mine.
- **icon xcheck:** PASS=0 FAIL=4 (all-fail, modes 2+3 consistency HARD) — verified base==mine.
- (Also unchanged, long-standing: rebus hello ROW-DRIFT / all-langs monitor smoke on deleted `--monitor` infra + missing corpus; `bb_call_write_slot.cpp:71` fprintf purity; GZ gates gz2-gz7 stale banner.)

base==mine at EVERY gate confirms both conversions are behavior-neutral. Someone should look at the SNOBOL4/prolog/icon regression on a dedicated session — it is NOT part of this hygiene sweep and is on-hold per PLAN.

---

## NEXT (continue Z→A)
Cursor now `bb_match_breakx.cpp`. Resume: grep `# CURSOR:`, audit it (CLEAN expected), then `audit_bb_fixup_rank.sh` filtered `TOTAL=[1-9]`, take the dirty file sorting strictly before the cursor toward A:

1. **bb_match_break.cpp (3)** — NEXT. The plain `BREAK(cset)` box; almost certainly the same single-linear string-cset shape as breakx minus the extend section → bare-`strtab_label` idiom, NOT the capture dispatch hazard. **Still verify it has no dispatch before folding** (the notany rule: if strtab_label sits before a branch, keep it unconditional).
2. bb_match_atp (3) → bb_match_arbno (3) → bb_match_any (3) → bb_match_advance (3) → onward toward A (then bb_mapgrep, bb_logicvar, …).

Idioms to mirror: `bb_match_breakx.cpp` / `bb_match_notany.cpp` (single-linear string-cset, bare strtab_label), `bb_match_capture.cpp` (dispatch + comma-operator strtab_label), `bb_match_arb.cpp` (scratch-slot `FR(_.x86_scratch_off + N)` inlines).

## RESUME RECIPE (mechanical, from cold)
1. Clone SCRIP + corpus (token in session env), `git config` LCherryholmes/lcherryh@yahoo.com.
2. `bash scripts/install_system_packages.sh`; `rm -f scrip && make -j4 scrip`; `make libscrip_rt` (lands at `out/libscrip_rt.so`). NOTE: builds are slow — do `make -j4 scrip` and `make libscrip_rt` in SEPARATE steps (a combined double-build can time out).
3. `cursor=$(grep -m1 '^# CURSOR:' .github/BB-REVAMP-TRACKER.md | awk '{print $NF}')` → expect `bb_match_breakx.cpp`. Do NOT open the tracker otherwise.
4. `bash scripts/audit_bb_fixup_rank.sh` → dirty set via `grep 'TOTAL=[1-9]'`; per-file `bash scripts/audit_bb_fixup_file.sh <file>` (per-file total is authoritative; includes cv9/cv10).
5. A/B with a git-stash (or `git checkout <HEAD> -- <file>`) baseline: m2/m3 behavioral + m4 raw/normalized byte-identity + assemble/link/run vs m3 oracle. If you rebase and the diff touches emit_bb.c/emit_core.c/x86_asm.h/lower_*, RE-A/B on the rebased tree.
6. Gate battery; commit; `git pull --rebase && git push` (SCRIP first, .github last); watermark + cursor advance + this-style handoff doc.

**SCRIP @ `e4e0e5e` (pushed). Two conversions banked at a clean boundary.**
