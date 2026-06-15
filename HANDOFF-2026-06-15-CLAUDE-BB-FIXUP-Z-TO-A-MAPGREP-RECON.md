# HANDOFF — GOAL-BB-FIXUP-Z-to-A, 20th session addendum (Claude Opus 4.8)
## bb_mapgrep RECON ONLY — no SCRIP edit. Cursor HELD bb_match_advance.cpp (the last LANDED file). Next file = bb_mapgrep.cpp, mapped cold below.

**No SCRIP code changed this turn — working tree clean at `b6e13b9`.** This is a recon hand-off at the ~70% context brake (Law 7): `bb_mapgrep` is the first HEAVY file of the stretch and full conformance is entangled with the *pending* native map/grep emission, so per the SOP I did the required fire-probe + mapping and stopped cleanly rather than half-start a heavy dormant file at the brake. The two files this session (`bb_match_any`, `bb_match_advance`) are LANDED + PUSHED (see HANDOFF-2026-06-15-CLAUDE-BB-FIXUP-Z-TO-A-MATCH-ANY.md). The tracker cursor is `bb_match_advance.cpp`; on resume the RESUME PROCEDURE computes the next dirty file Z→A = **bb_mapgrep.cpp**.

---

## bb_mapgrep.cpp — audited 16 (medium_any=1, returns_plus=6, helper_count=9)
SNOBOL4/Raku box for `IR_MAP` / `IR_GREP` (the materialized map/grep result array). 62 lines. emit_core.c:450-451 dispatches both `IR_MAP` and `IR_GREP` → `bb_prepare(nd); bb_emit_x86(bb_mapgrep());`.

### ⛔ PRIMARY FINDING — the box is FULLY DORMANT and its prep is a deliberate abort
- `bb_mapgrep_prepare(IR_t*)` (lines 58-62) is a stub that prints `[NO-IR-INTERP] … native Raku map/grep emission pending` and **`abort()`s**. `bb_prepare` (emit_bb.c:1219-1220) calls it for the IR_MAP/IR_GREP kinds → **any program containing IR_MAP/IR_GREP aborts at prep time, before `bb_mapgrep()` is ever called.**
- **Nothing in `src/` writes the `s_mg_*` static state** (grep `s_mg_` outside this file = empty). The writer was the deleted IR-interpreter materialization path. So the template reads always-zero/empty state even if it were reached.
- ∴ The box never fires in native modes. A hygiene rewrite is **byte-identical-by-construction** (it can't be exercised by any real program); prove it the way the resolver-family deletion did (abort-as-detector: 0 aborts across a map/grep battery = unreachable) or via a throwaway lowering-retag vehicle if you want a positive emission A/B.

### The 16 violations and how they interlock
- **helper_count=9** = 11 statics − 2 allowed. The 11: 6 data members (`s_mg_vals[4096]`, `s_mg_n`, `s_mg_vals_ptr`, `s_mg_lbl[64]`, `s_mg_cursoff`, `s_mg_resoff`) + 5 trivial accessor fns (`mgN`/`mgValsP`/`mgLbl`/`mgCurs`/`mgRes`, each just `return s_mg_X;`).
- **returns_plus=6** = 8 returns − 2. The 8: the 5 accessor `return`s (lines 25-29), the `if(PLATFORM_X86) return` (33), the `.quad`-builder lambda `return q` (39, NOT excluded — it's the bare `[&]{…}` form without parens, so the audit's capturing-lambda exclusion `\[[&=]…\]\s*\(…\)\s*\{` does not match it), and `return std::string()` (55).
- **medium_any=1** = the `IF(MEDIUM_TEXT, …)` block (lines 35-42) emitting the `.section .rodata` / `mgLbl: .quad <csv>` / `.section .text` / `.intel_syntax noprefix` materialized-array directives.

**Inlining the 5 accessors kills 5 helpers AND 5 returns at once** (mgN()→s_mg_n etc., delete the fns). That drops helper_count 9→4 and returns_plus 6→1. Remaining after that: 4 helper (the 6 data members − 2) + 1 return (the lambda) + 1 medium.

### ⛔ THE STRUCTURAL BLOCKER — CV9/CV10 vs the abort stub
- **CV10** says zero IR-graph access + all state via `bb_prepare`-delivered `_.op_*` fields, and the 6 `s_mg_*` static data members are exactly the kind of per-box state CV10 wants moved into prep/`_` fields (the materialized values array, its count, the rodata label, the cursor/result frame offsets). **But `bb_mapgrep_prepare` is a deliberate `abort()` ("native map/grep emission pending").** Making the box truly CV9/CV10-conformant — prep computes the values/label/offsets and delivers them via `_.op_*` — IS implementing the pending native map/grep prep. That is a genuine TIER-S feature (Raku map/grep native emission), NOT hygiene, and is the "native … emission pending" work the stub is a placeholder for.
- **CV5/CV7** also bite: the `IF(MEDIUM_TEXT, x86("directive", "…"))` rodata block must collapse to the both-medium CV7 decomposition — the RO-seal pattern `x86("def", L(n)) + x86(".quad", LS(n), …) + x86("label", LS(n)) + x86(".quad", val)…` (see CV7 precedent / `x86_ro_seal_q`), with the per-element `.quad` list emitted one `x86(".quad", …)` per value. `x86("directive", …)` and `x86("comment", …)` strings that aren't a real mnemonic/directive-as-spelled are CV7 targets.

### TWO PATHS for the next session (Lon to weigh — STATE the call in the run record)
1. **HYGIENE-ONLY, leave dormant (smaller, behavior-neutral, but may not reach rc=0):** inline the 5 accessors (kills 5 helper + 5 returns), inline/rewrite the `.quad` lambda to drop its return, collapse the MEDIUM_TEXT block to the CV7 `.quad`-decomposition both-medium form. This clears medium_any→0, returns_plus→0, and helper_count 9→4 — but the **4 residual static data members still trip helper_count** (CV6/CV10 want them gone). If the audit can't reach 0 without moving them to `_` fields, this path does NOT satisfy the SOP's rc=0 bar by itself.
2. **FULL CV9/CV10 = implement the native prep (TIER-S, the real fix):** write a real `bb_prepare` IR_MAP/IR_GREP block that walks the map/grep IR, computes the materialized value array + label + cursor/result ζ-slots, and delivers them via new `sm_emit_t` `_.op_*` fields (replacing the 6 statics); make `bb_mapgrep()` parameterless reading only `_.*`; remove the abort stub. This is the "native Raku map/grep emission" feature — multi-session, with its own A/B (it would make the box LIVE, so real map/grep programs must be exercised m3/m4). Per the SOP this is in-scope and is the genuine job; per Law 5 it is OURS (no owner-goal hand-off). But it is NOT a brake-time half-edit.

**Recommended:** open the next session fresh on bb_mapgrep with full budget and do Path 2 (the SOP/Law-5 answer — the box is mis-designed exactly because its prep aborts; redesign it). Path 1 is the fallback only if Path 2 proves to need cross-subsystem Raku-runtime work genuinely outside this template (then state that finding and the minimal in-scope slice). Either way: fire-probe is DONE (dormant, confirmed above); start from the accessor-inline (mechanical, 5 helper + 5 returns) which is safe regardless of path.

### RESUME RECIPE (mechanical, from cold)
1. Clone SCRIP + corpus; `git config` LCherryholmes/lcherryh@yahoo.com.
2. `bash scripts/install_system_packages.sh`; `rm -f scrip && make -j4 scrip`; `make libscrip_rt` (separate steps; slow). `export LD_LIBRARY_PATH=/home/claude/SCRIP/out`.
3. `cursor=$(grep -m1 '^# CURSOR:' .github/BB-REVAMP-TRACKER.md | awk '{print $NF}')` → `bb_match_advance.cpp` (CLEAN) → RESUME step 3 → next dirty Z→A = **bb_mapgrep.cpp**. Audit it (`src/emitter/BB_templates/bb_mapgrep.cpp`) → 16, confirming this recon.
4. Decide Path 1/2; START with the accessor inline (always-safe). For the dormant-emission A/B use the abort-detector or a throwaway retag; rebuild + diff vs pre-edit captures.
5. Gate battery (sno_pat_reg --strict · pat rung PASS-M4=19/0/0 · bin_t 0 · handencoded 0 · vstack 3 · icon crosscheck = pre-existing FAIL=4). Commit, `git pull --rebase` (HEAD drifts ~1 commit per push this lap — re-A/B if the rebase touches emit_bb.c/emit_core.c/x86_asm.h/lower_*), push (SCRIP first, .github last), cursor-advance + watermark + handoff.

**SCRIP @ `b6e13b9` (clean). Cursor `bb_match_advance.cpp`. Next file bb_mapgrep.cpp mapped cold above — DORMANT, 16 violations, structural (entangled with pending native map/grep prep).**
