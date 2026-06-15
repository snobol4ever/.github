# HANDOFF — GOAL-BB-FIXUP-Z-to-A, 19th session (Claude Opus 4.8)
## bb_match_break 2→0 + bb_match_atp 3→0 + bb_match_arbno 3→0 — ALL CLEAN, LANDED + PUSHED. Cursor ADVANCED bb_match_breakx.cpp → bb_match_arbno.cpp.

**SCRIP HEAD pushed: `f84a7f4`** (arbno), preceded by `0f306a5` (atp) and `9194695` (break), rebased onto `1f2e340`.
**.github:** this handoff + GOAL watermark (19th-session entry) + cursor advance in BB-REVAMP-TRACKER.md (`# CURSOR:` line only, via in-place sed — tracker not otherwise opened). PLAN.md goals table NOT edited.

---

## WHAT LANDED (three commits, Z→A from the 18th session's bb_match_breakx)

Cold start: ran the RESUME PROCEDURE — cursor (tracker `# CURSOR:`) = `bb_match_breakx.cpp`; audited it → CLEAN (rc=0) → step 3 swept the three dirty bb_match_* files strictly before it, Z→A, one per step: bb_match_break → bb_match_atp → bb_match_arbno.

### (1) bb_match_break — `9194695` — 2→0 (local_vars=2)
SNOBOL4 `IR_MATCH_BREAK` (plain `BREAK(cset)`). **SINGLE-LINEAR box — one `strtab_label`/`lbl` site, `lbl` used once in the `lea`, no dispatch** → the notany hazard does NOT apply (exactly as the 18th handoff predicted). Used the bare-`strtab_label` **breakx idiom**: dropped `cc`/`lbl`/`ca`/`sf`, kept `static char b[24]`, inlined the cset address `(uint64_t)(uintptr_t)(const void *)(_.op_sval ? _.op_sval : "")` into the `lea` and the `strchr` fn-pointer cast into the `call`. Result is structurally identical to clean `bb_match_breakx` minus the extend section.

- The audit's `const char *` branch only matches double-pointers/trailing-space forms, so it counted only `uint64_t ca` / `uint64_t sf` (not `cc`/`lbl`) — but I converted all four to satisfy the SPEC and match the proven-clean sibling exactly.
- `emit_intern_str` RE-CONFIRMED DEAD: body is `return (g_flat_intern_str && g_is_text) ? g_flat_intern_str(s) : NULL;` and `g_flat_intern_str`=NULL → returns NULL with **zero side effect** (the call is never reached) → dropping it cannot perturb `.S` numbering.

### (2) bb_match_atp — `0f306a5` — 3→0 (local_vars=2 + returns_plus=1)
SNOBOL4 `IR_PAT_ATP` (the `@VAR` cursor-assignment, calls `rt_at_cursor`). **IR_PAT_ATP is DORMANT** — `TT_CAPT_CURSOR` (`@VAR`) produces no IR_PAT_ATP (it lowers to capture/defer ops), and nothing else lowers to it either. So the box is unreachable via normal compilation (like the 16th-session `bb_match_span_var`); my change is trivially inert to every real program.
- Collapsed 3 returns → 2 (PLATFORM guard + one ternary) and dropped `vn`/`lbl`/`va`/`fn`.
- **Used the capture comma-operator idiom** for `strtab_label` so the intern side-effect stays conditional on non-empty varname: `return !(_.op_sval ? _.op_sval : "")[0] ? std::string() : (strtab_label(b, sizeof b, _.op_sval ? _.op_sval : ""), x86("comment","IR_MATCH_ATP") + …);`. **PRESERVED atp's distinct behavior** — empty varname → silent `std::string()`, **NOT** a bomb (capture bombs; atp does not).

### (3) bb_match_arbno — `f84a7f4` — 3→0 (local_vars=1 + returns_plus=1 + over_col=1)
SNOBOL4 `IR_PAT_ARBNO` (the shy ARBNO generator). The meatiest of the three: genuine `std::string` label arithmetic — `base = g_emit.bb_child_lbl` minus its 3-byte `_α` suffix (UTF-8 `α`=2 bytes, so `_α`=3), used in 3 label concatenations (`base + "_α"`, `+ "_wγ"`, `+ "_wω"`).
- **over_col (line-17 comment >200 chars)** fixed by **CV1 terse comment** → `"IR_MATCH_ARBNO"` (matching the sibling `IR_MATCH_*` convention). This is the **only** m4 .s delta (C2-sanctioned).
- **base** delivered via a **single capturing lambda** taking `base` as a parameter — `: [&](std::string base) { return x86(…) + … + x86("jmp", base + "_α") + …; }(<strip-expr>)`. Rationale (audit mechanics): `returns_plus`/`local_vars` are **whole-file** counts, but `returns_plus` **subtracts capturing-lambda returns** (regex `\[[&=][^]]*\]\s*\([^)]*\)\s*\{` on the return's line). So a static helper-function would add a counted return; the SPEC-intended idiom (CV6 "lambda parameters are not locals") is a capturing lambda. Param `base` ≠ local; lambda return excluded → returns net to 2 (PLATFORM + ternary).
- The strip-expr argument is local-free (triple-construct `std::string(g_emit.bb_child_lbl).size() > 3 ? …substr(0, …size()-3) : …`); kept the helper-form everywhere (NOT the `base+"_α" == bb_child_lbl` simplification, which fails the size≤3 edge case) for exact byte-identity.

---

## VERIFICATION — C2 by DIRECT A/B byte-identity (strongest standard)

- **break:** fired `042_pat_break` (`X BREAK(' ') . V`, 1 box, →hello) + a custom 3-BREAK program (`,`/`;:`/` ` csets, →abc/foo/xxx). m2 IDENTICAL, m3 IDENTICAL, **m4 RAW BYTE-IDENTICAL** (sha256 exact, no label renumber). m4 binaries assemble+link+run matching m3.
- **atp:** dormant ∴ proven via a **throwaway lowering-retag vehicle** (the 16th-session span_var method) — temporarily retagged the main `TT_DEFER` `*VAR` alloc (lower_snobol4.c:403) `IR_PAT_DEFER → IR_PAT_ATP`, fired `S *PVAR`, **m4 RAW BYTE-IDENTICAL** (sha256 `75fa9a1…`), then fully reverted (lower_snobol4.c confirmed byte-identical to HEAD; `*PVAR` fires 0 IR_MATCH_ATP afterward).
- **arbno:** fired `052_pat_arbno` + `054_pat_arbno_alt` (both 1 ARBNO box). m2/m3 IDENTICAL base==mine; **m4 diff = ONLY the comment line** (`# BOX ARBNO()…` → `# IR_MATCH_ARBNO`), every instruction/label byte-identical — the C2-sanctioned R1 delta.

**NOTE — ARBNO m2/m3 are EMPTY/abort for these programs in BOTH base and mine.** m2 is the IR-graph interpreter (no BB templates); m3 (`--run`, native in-process) aborts for ARBNO at this HEAD (pre-existing ARBNO red zone). The live coverage is m4 (`--compile`), which is in the rung suite's PASS-M4=19 — the compiled arbno binary runs correctly. A/B proved m2/m3 identical base==mine, so this is expected, not a regression.

---

## ⚠️ HEAD DRIFT + RE-A/B
HEAD advanced **`42d4c95` → `1f2e340`** during the session (one rebase at handoff): `1f2e340` "FIX-3-iii bb_call: IR_CALL_BUILTIN producer (FN/non-write builtins, both flat paths)" — **touched `emit_bb.c` (8 lines)**, so per the standing lesson I re-A/B'd on the rebased combined tree. The change is purely IR_CALL retagging (`IR_CALL → IR_CALL_PROC_STAGED/GVAR_USERPROC/BUILTIN` by dval + registration) — it touches **only IR_CALL nodes, never IR_PAT_*/IR_MATCH_*** — so my pattern boxes are unaffected by construction. Confirmed: re-audit all 3 CLEAN; break + arbno m4 emission **IDENTICAL to pre-rebase** captures; rung PASS-M4=19; sno_pat_reg strict OK. atp (dormant, IR_CALL-unrelated) unaffected by construction — retag A/B not re-run. My 3 commits rebased cleanly → `9194695`/`0f306a5`/`f84a7f4`.

---

## GATES (green on final rebased combined tree)
- audit `bb_match_break` / `bb_match_atp` / `bb_match_arbno` → all 0 CLEAN.
- `sno_pat_reg --strict` → TIER 1 = 0, TIER 2 = 0, both HARD.
- pattern rung suite → rc=0, **PASS-M4=19 FAIL-M4=0 SKIP-M4=0**.
- `no_bb_bin_t` → 0. `no_handencoded_bytes` → 0 BAD. `no_vstack` → 3 floor (src/attic/runtime/rt/rt.c + rt.h).

### ⚠️ PRE-EXISTING REDS (unchanged, NOT mine, on-hold per PLAN)
The heavy SNOBOL4/prolog/icon xcheck reds flagged at this HEAD in the 18th handoff persist — all three of my changes are byte-identical-m4 single-file edits and cannot affect them. ARBNO m2/m3 fails (above) are part of this pre-existing red zone. Also long-standing: rebus hello ROW-DRIFT / monitor smoke on deleted `--monitor` infra; `bb_call_write_slot.cpp:71` fprintf purity; GZ gates gz2-gz7 stale banner. Flagged for a future non-hygiene session.

---

## NEXT (continue Z→A)
Cursor now `bb_match_arbno.cpp`. Resume: grep `# CURSOR:`, audit it (CLEAN expected), then `audit_bb_fixup_rank.sh` filtered `TOTAL=[1-9]`, take the dirty file sorting strictly before the cursor toward A. **Per-file paths:** `audit_bb_fixup_file.sh` needs the path relative to repo root (`src/emitter/BB_templates/bb_*.cpp`), NOT the bare basename the rank tool prints.

1. **bb_match_any.cpp (lv=3)** — NEXT. The `ANY(cset)` box; almost certainly the single-linear string-cset shape (like notany/span/break) → bare-`strtab_label` idiom. **Verify it has no dispatch before folding** (the notany rule: if `strtab_label` sits before a branch, keep it unconditional).
2. bb_match_advance (lv=1, rp=1) → then bb_mapgrep (heavy, 16), bb_logicvar (1), bb_lit*/bb_keyword, … onward toward A.

Idioms by shape (all proven this lap):
- single-linear string-cset, bare `strtab_label`: `bb_match_break` / `bb_match_breakx` / `bb_match_notany`.
- dispatch + comma-operator `strtab_label` (intern side-effect before a branch): `bb_match_capture`; empty-guard-as-ternary variant (silent empty, not bomb): `bb_match_atp`.
- `std::string` label arithmetic with no locals → **single capturing lambda** `[&](std::string base){ return …; }(<local-free expr>)`: `bb_match_arbno`.
- scratch-slot `FR(_.x86_scratch_off + N)` inlines: `bb_match_arb`.

## RESUME RECIPE (mechanical, from cold)
1. Clone SCRIP + corpus (token in session env), `git config` LCherryholmes/lcherryh@yahoo.com.
2. `bash scripts/install_system_packages.sh`; `rm -f scrip && make -j4 scrip`; `make libscrip_rt` (lands at `out/libscrip_rt.so`). Builds are slow — keep `make -j4 scrip` and `make libscrip_rt` in SEPARATE steps.
3. `cursor=$(grep -m1 '^# CURSOR:' .github/BB-REVAMP-TRACKER.md | awk '{print $NF}')` → expect `bb_match_arbno.cpp`. Do NOT open the tracker otherwise (sed it in place for the advance).
4. `bash scripts/audit_bb_fixup_rank.sh` → dirty set via `grep 'TOTAL=[1-9]'`; per-file `bash scripts/audit_bb_fixup_file.sh src/emitter/BB_templates/<file>` (authoritative; includes cv9/cv10).
5. **Efficient A/B:** the freshly-built current binary IS the baseline for the next file — capture its m2/m3/m4 BEFORE editing (saves one slow rebuild). For DORMANT boxes use a throwaway lowering-retag vehicle and REVERT it. If you rebase and the diff touches emit_bb.c/emit_core.c/x86_asm.h/lower_*, RE-A/B on the rebased tree (re-emit + diff vs pre-rebase captures).
6. Gate battery; commit each file; `git pull --rebase && git push` (SCRIP first, .github last); watermark + cursor advance + this-style handoff doc.

**SCRIP @ `f84a7f4` (pushed). Three conversions banked at a clean boundary (stopped before bb_match_any).**
