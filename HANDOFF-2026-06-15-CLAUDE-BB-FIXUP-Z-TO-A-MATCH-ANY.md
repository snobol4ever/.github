# HANDOFF — GOAL-BB-FIXUP-Z-to-A, 20th session (Claude Opus 4.8)
## bb_match_any 3→0 + bb_match_advance 2→0 — BOTH CLEAN, LANDED + PUSHED. Cursor ADVANCED bb_match_arbno.cpp → bb_match_advance.cpp. GOAL.md reduced 109K→18K.

**SCRIP HEAD pushed: `b6e13b9`** (bb_match_advance), preceded by `da13bbb` (bb_match_any), rebased across ~4 concurrent commits (Icon real-arith, Raku OO, Pascal realloc-cap, SNOBOL4-BB indirect-assign).
**.github:** this handoff + GOAL watermark (20th-session entry) + cursor advance in BB-REVAMP-TRACKER.md (`# CURSOR:` line only, via in-place sed — tracker not otherwise opened). PLAN.md goals table NOT edited.

---

## WHAT LANDED (one commit, Z→A from the 19th session's bb_match_arbno)

Cold start: ran the RESUME PROCEDURE — cursor (tracker `# CURSOR:`) = `bb_match_arbno.cpp`; audited it → CLEAN (rc=0) → step 3: computed the next dirty file sorting strictly before it (Z→A) = **bb_match_any.cpp** (`any` < `arbno`: position-2 `n`<`r`), matching the 19th-session NEXT.

### bb_match_any — `da13bbb` — 3→0 (local_vars=3: `ca`, `sf`, `test`)
SNOBOL4 `IR_MATCH_ANY` (the `ANY(cset)` box). **SINGLE-LINEAR box** with an internal `strlen==1` single-char-vs-multi-char dispatch (single-char → `cmp sil, imm`/`jne`; multi-char → `lea`/`strchr`/`test`/`je`). The 3 flagged locals were `uint64_t ca` (cset addr), `uint64_t sf` (strchr fn-ptr), `std::string test` (the dispatch fragment).

Conversion (matches the proven-clean sibling `bb_match_break`/`bb_match_breakx`/`bb_match_notany` bare-`strtab_label` idiom):
- Dropped `cs`, `lbl`, the `if(!lbl){…}` block, `ca`, `sf`, `test`.
- **Kept `static char b[24]` + `strtab_label(b, sizeof b, _.op_sval ? _.op_sval : "")` as an UNCONDITIONAL BARE STATEMENT** — this is the **notany hazard** (16th-session finding): the original calls intern/strtab UNCONDITIONALLY before the dispatch, so even a single-char `ANY("X")` (which never uses `lbl`) interns its cset into the string table and emits a `.S<n>` it never references. Folding strtab into the multi-char-only branch would skip interning on the single-char path → renumber all later `.S` labels. The bare statement preserves the exact side-effect position.
- Inlined `ca` → `(uint64_t)(uintptr_t)(const void *)(_.op_sval ? _.op_sval : "")` into the multi-char `lea`.
- Inlined `sf` → `(uint64_t)(uintptr_t)(void *)(const char *(*)(const char *, int))strchr` into the `call`.
- Folded the `test` dispatch into the return chain as a ternary on `strlen(_.op_sval ? _.op_sval : "") == 1` (the single-char arm reads `(_.op_sval ? _.op_sval : "")[0]`).
- Net: 2 returns (PLATFORM guard + the one assembled return); longest line 120 ≤200; zero blank lines; comment `IR_MATCH_ANY` untouched (already terse, matches sibling house style).

### bb_match_advance — `b6e13b9` — 2→0 (local_vars=1 `ka` + returns_plus=1)
SNOBOL4 `IR_MATCH_ADVANCE` (the cursor-advance + kw_anchor abort-check box, fired by every pattern match). Two violations: the `uint64_t ka = …&kw_anchor` local, and 3 returns (PLATFORM guard + the `op_sa/op_off` `x86_bomb` guard + the main return).
- Inlined `ka` → `(uint64_t)(uintptr_t)(const void *)&kw_anchor` into the `mov "rcx", "[rip + __]"` site.
- **Folded the bomb guard into the return as a ternary** — `return (_.op_sa < 0 || _.op_off < 0) ? x86_bomb(…) : x86("comment", "IR_MATCH_ADVANCE") + …;` — dropping the standalone guard return (3→2 returns). `x86_bomb` returns `std::string` (x86_asm.h:540) so the ternary type-unifies. This is the same returns-collapse shape as bb_match_atp/arbno; the bomb branch is never taken on well-formed programs so it's behavior-neutral.

**`emit_intern_str` RE-CONFIRMED DEAD at this HEAD:** `g_flat_intern_str` is `= NULL` (emit_bb.c:229); its only setter `lower_flat_set_intern_str` has a declaration + macro-alias in emit_bb.h but **ZERO call sites** outside `src/attic` → `g_flat_intern_str` stays NULL → `emit_intern_str()` always returns NULL with zero side effect → the original `if(!lbl)` branch was *always* taken → dropping the dead call and making `strtab_label` unconditional is exactly equivalent (the established lap-1 finding, re-verified).

---

## VERIFICATION — C2 by DIRECT A/B byte-identity (strongest standard)

Baseline = the freshly-built binary at `f84a7f4` BEFORE editing (captured per the RESUME RECIPE's "current binary IS the baseline" efficiency note).

Firing programs:
- `test/snobol4/patterns/039_pat_any.sno` — `X ANY('aeiou') . V` on `'hello'` → fires 1 ANY box (multi-char branch), output `e`.
- `/tmp/any_both.sno` (custom) — `ANY('e')` (single-char branch) + `ANY('aeiou')` (multi-char branch) + trailing `'tail'` literal to check `.S` numbering. Output `\ne\ntail` (m3).

Results (both branches covered):
- **m3 (`--run`, native in-process):** `039` IDENTICAL (`e`); `any_both` IDENTICAL (`\ne\ntail`).
- **m4 (`--compile`):** `039` .s **RAW BYTE-IDENTICAL** (sha256 `e0c0b47…`); `any_both` .s **RAW BYTE-IDENTICAL** (sha256 `dae9200…`). No BB-label renumber needed — pure inlining left emission order + sizes unchanged, exactly as the sibling break/breakx/notany conversions.
- Baseline m4 binaries assemble + link (`gcc -no-pie … -lscrip_rt`) + run: `039`→`e`, `any_both`→`\ne\ntail`, matching m3.

**NOTE — m2 not available at this HEAD:** there is no `--run` flag in the current driver (modes are `--run`=mode-3 default and `--compile`=mode-4; `--target=ARCH` implies compile). m2 (IR-graph interpreter) is not exposed via a flag here, and per the 18th/19th handoffs mode-2 doesn't use BB templates anyway — the live coverage for SNOBOL4 pattern boxes is m3 + m4, both proven byte-identical.

---

## ⚠️ HEAD DRIFT + RE-A/B
HEAD advanced **`f84a7f4` → `c26f89f`** during the session (one rebase at handoff): `c26f89f` "Icon BB: native real-arithmetic binops + relops (m3/m4 127→132, +5 each)" — **touched `emit_bb.c` (62 lines)** + `emit_globals.h` + scrip.c + bb_binop_arith.cpp + bb_binop_relop.cpp + arithmetic.c + by_name_dispatch.c. Per the standing lesson (rebase touches shared emitter infra → re-A/B), I rebuilt on the rebased combined tree (`da13bbb`) and re-emitted: `039` + `any_both` m4 .s **byte-identical to my pre-rebase captures** — the Icon change touches only IR_BINOP_ARITH/RELOP paths, never IR_MATCH_ANY, so my SNOBOL4 pattern box is unaffected by construction. m3 unchanged. My commit rebased cleanly → `da13bbb`.

---

## GATES (green on final rebased combined tree)
- audit `bb_match_any` → 0 CLEAN (re-confirmed post-rebase).
- `sno_pat_reg --strict` → TIER 1 = 0, TIER 2 = 0, both HARD.
- pattern rung suite → **PASS-M4=19 FAIL-M4=0 SKIP-M4=0** (the lap-1 floor).
- `no_bb_bin_t` → 0. `no_handencoded_bytes` → 0 BAD. `no_vstack` → 3 floor (src/attic/runtime/rt/rt.c + rt.h).

### ⚠️ PRE-EXISTING REDS (unchanged, NOT mine, on-hold per PLAN)
- **icon crosscheck `PASS=0 FAIL=4`** (modes 2+3 consistency, HARD). **PROVEN PRE-EXISTING this session by stash-A/B**: stashed my edit, rebuilt baseline `f84a7f4`, re-ran the icon crosscheck → identical `PASS=0 FAIL=4`. This is the heavy DT_C/DT_E / PL-GZ red zone flagged in the 18th/19th handoffs; my SNOBOL4-pattern single-file byte-identical edit cannot affect Icon emission.
- Long-standing (per prior handoffs): rebus hello ROW-DRIFT / monitor smoke on deleted `--monitor` infra + missing `/home/claude/corpus`; `bb_call_write_slot.cpp:71` fprintf purity; GZ gates gz2-gz7 stale (pre-GUT INTERP-FALLBACK banner — retarget candidate); the SNOBOL4/prolog xcheck reds at this HEAD. Flagged for a future non-hygiene session.

---

## NEXT (continue Z→A)
Cursor now `bb_match_any.cpp`. Resume: grep `# CURSOR:`, audit it (CLEAN expected), then `audit_bb_fixup_rank.sh` filtered `TOTAL=[1-9]`, take the dirty file sorting strictly before the cursor toward A. **Per-file paths:** `audit_bb_fixup_file.sh` needs the path relative to repo root (`src/emitter/BB_templates/bb_*.cpp`), NOT the bare basename the rank tool prints.

1. **bb_match_advance.cpp (2 = lv1, rp1)** — NEXT (audited dirty=2 this session, confirms the 19th-session projection). Inspect its shape: likely a small scalar/linear box. Check for the notany hazard (unconditional intern before a branch) only if it has a string-cset + dispatch — if single-linear, the bare-`strtab_label` idiom applies; the `rp1` suggests a returns-collapse (PLATFORM-guard + ternary) like bb_match_atp/arbno.
2. Then **bb_mapgrep (heavy, ~16)** → bb_logicvar (1) → bb_lit_scalar → bb_lit → bb_keyword → … onward toward A.

Idioms by shape (all proven this lap):
- single-linear string-cset, bare `strtab_label`: `bb_match_break` / `bb_match_breakx` / `bb_match_notany` / **`bb_match_any`** (this session).
- dispatch + comma-operator `strtab_label` (intern side-effect before a branch): `bb_match_capture`; empty-guard-as-ternary variant (silent empty, not bomb): `bb_match_atp`.
- `std::string` label arithmetic with no locals → single capturing lambda `[&](std::string base){ return …; }(<local-free expr>)`: `bb_match_arbno`.
- scratch-slot `FR(_.x86_scratch_off + N)` inlines: `bb_match_arb`.

## RESUME RECIPE (mechanical, from cold)
1. Clone SCRIP + corpus (token in session env), `git config` LCherryholmes/lcherryh@yahoo.com.
2. `bash scripts/install_system_packages.sh`; `rm -f scrip && make -j4 scrip`; `make libscrip_rt` (lands at `out/libscrip_rt.so`). Builds are slow — keep `make -j4 scrip` and `make libscrip_rt` in SEPARATE steps. **Set `LD_LIBRARY_PATH=/home/claude/SCRIP/out` for `--run` / linked m4 binaries.**
3. `cursor=$(grep -m1 '^# CURSOR:' .github/BB-REVAMP-TRACKER.md | awk '{print $NF}')` → expect `bb_match_any.cpp`. Do NOT open the tracker otherwise (sed it in place for the advance).
4. `bash scripts/audit_bb_fixup_rank.sh` → dirty set via `grep 'TOTAL=[1-9]'`; per-file `bash scripts/audit_bb_fixup_file.sh src/emitter/BB_templates/<file>` (authoritative; includes cv9/cv10).
5. **Efficient A/B:** the freshly-built current binary IS the baseline for the next file — capture its m3/m4 BEFORE editing (saves one slow rebuild). m2 (`--run`) is NOT available at this HEAD — use m3 (`--run`) + m4 (`--compile`). For DORMANT boxes use a throwaway lowering-retag vehicle and REVERT it. If you rebase and the diff touches emit_bb.c/emit_core.c/x86_asm.h/lower_*, RE-A/B on the rebased tree (re-emit + diff vs pre-rebase captures).
6. Gate battery; commit each file; `git pull --rebase && git push` (SCRIP first, .github last); watermark + cursor advance + this-style handoff doc.

**Gate scripts (verified names this session):** `scripts/test_gate_sno_pat_reg.sh --strict` · `scripts/test_snobol4_pat_rung_suite.sh` (grep `PASS-M4`) · `scripts/test_gate_no_bb_bin_t.sh` · `scripts/test_gate_no_handencoded_bytes.sh` · `scripts/test_gate_no_vstack.sh` · `scripts/test_crosscheck_icon.sh` (HARD modes 2+3; currently pre-existing FAIL=4).

**SCRIP @ `da13bbb` (pushed). One conversion banked at a clean boundary (stopped before bb_match_advance).**
