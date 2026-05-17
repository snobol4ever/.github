# GOAL-CASE-SENSITIVE-ONLY.md — Remove all case folding from SCRIP

**Repo:** one4all
**Origin:** Lon command decision, session 2026-05-17. Recorded as ABSOLUTE RULE in `RULES.md`.
**Status:** Directive landed in RULES; code sweep PENDING.

---

## ⛔ Read first

Read the ABSOLUTE RULE block "SCRIP IS CASE-SENSITIVE. NO FOLDING. ANYWHERE." in `RULES.md`. That rule is binding. This goal file is the sweep that makes the code match the rule.

---

## Done when

1. `grep -rn "sno_fold_name\|sno_fold_on\|fold_strbuf\|strcasecmp\|strncasecmp\|sno_set_case_sensitive\|sno_get_case_sensitive\|--case-sensitive\|--fold-case" src/` returns ONLY:
   - References inside legacy oracle directories (SPITBOL, CSNOBOL4), which are exempt.
   - The removal commit's comment trail.
2. `&CASE` keyword assignment is either rejected or no-op-with-warning. `&CASE` is no longer wired to behavior.
3. All existing gates green at HEAD:
   - `test_smoke_rebus.sh`: 4/0
   - `test_smoke_scrip_all_modes.sh`: 2/0
   - `test_smoke_snobol4.sh`: baseline ≥ 6/1
   - `test_smoke_icon.sh`: 5/0
   - `test_smoke_snocone.sh`: 5/0
   - `test_crosscheck_snobol4.sh`: 4/2 baseline
   - `test_beauty_snocone_subsystems.sh` (20 subsystems): 19/20 (Qize SKIP per SL-3)
   - `unified_broker`: 19/30 baseline
4. Beauty self-host (Milestone 1) remains byte-identical — md5 `abfd19a7a834484a96e824851caee159`, 646 lines.
5. Corpus tests that depend on case-folding behavior are either:
   - Updated to use case-correct identifiers (preferred), OR
   - Moved to a `legacy/` subdir with a note that they require the future preprocessor tool.

---

## Sites to sweep, by file

| File | Sites | Action |
|---|---|---|
| `src/frontend/snobol4/snobol4.l` | `sno_fold_on` (line 22), `sno_set_case_sensitive` (line 30), `sno_get_case_sensitive` (line 32), `sno_fold_name` (lines 34-37), `fold_strbuf` (lines 39-42), every call site | Delete. Lex passes identifiers through verbatim. |
| `src/runtime/snobol4/snobol4.c` | `sno_fold_name` calls in `sno_DATA_register` (lines 1506, 1518, 1527), `_VALUE_` (line 1671), function table registration (lines 2793, 2805) | Delete every `sno_fold_name(x)` call; the variable it folded becomes the canonical name. |
| `src/runtime/snobol4/eval_code.c` | `sno_fold_name` calls at lines 118, 129, 239, 281 | Delete each. |
| `src/runtime/rt/rt.c` | `sno_fold_name` calls at lines 933, 940, 962, 976, 1109 | Delete each. |
| `src/driver/interp_data.c` | `strcasecmp` in `sc_dat_find_type` (line 48), `sc_dat_find_field` (line 55) | Change to `strcmp`. |
| `src/driver/interp_hooks.c` | `_usercall_hook` uppercase-fallback at lines 64-68 — the `for (size_t _i = 0; _i <= _fl; _i++) _uf[_i] = (char)toupper(...)` loop and the second `label_lookup(_uf)` | Delete the toupper loop and the redundant second label_lookup; first lookup against `name` is the only one. |
| `src/driver/scrip.c` | `--case-sensitive` arg parsing (line 115), `--fold-case` arg parsing (line 116), `sno_set_case_sensitive(opt_case_sensitive)` (line 119), the `opt_case_sensitive` variable (line 88), the help text mentioning these (line 176) | Delete. |
| `src/runtime/snobol4/snobol4.c` keyword `&CASE` handler | wherever `&CASE` is read/written | Make assignment a no-op (or stderr warning); reads return 1 (a fixed sentinel). |

After sweep, also search for incidental `toupper` / `tolower` loops on identifiers (NOT on character-class building like `&UCASE`/`&LCASE` keyword values, which are legitimate strings):

```bash
grep -rn 'toupper\|tolower' src/ | grep -v 'UCASE\|LCASE\|alphabet\|test_\|demo_'
```

Triage each; delete the ones operating on identifier-shaped strings.

---

## Steps

- [ ] **CSO-1** — Snapshot baseline. Run every gate listed in "Done when", record numbers. This is the floor. The sweep must hold them.
- [ ] **CSO-2** — Delete fold infrastructure in `snobol4.l`. Rebuild. Run gates. Expect everything still green because the default was already `sno_fold_on=0` (SN-31) — these calls were already no-ops.
- [ ] **CSO-3** — Delete `sno_fold_name` calls in `snobol4.c`, `eval_code.c`, `rt.c`. Rebuild. Run gates.
- [ ] **CSO-4** — Switch `strcasecmp` → `strcmp` in `interp_data.c`. Run gates. This is the first call site that previously had *non-no-op* fold behavior. If any corpus test depended on case-insensitive DATA field lookup, it fails here — that test needs updating per "Done when" rule 5.
- [ ] **CSO-5** — Delete `_usercall_hook` uppercase-fallback in `interp_hooks.c`. Run gates. Same triage as CSO-4 — anything that relied on a lowercase-name finding an uppercase label fails here.
- [ ] **CSO-6** — Delete `--case-sensitive` / `--fold-case` CLI handling in `scrip.c`. Delete `opt_case_sensitive`. Update help text. Run gates.
- [ ] **CSO-7** — `&CASE` keyword: assignment becomes no-op-with-warning, reads return 1. Document in CHANGES or release notes.
- [ ] **CSO-8** — Final acceptance: full gate sweep, byte-identity check on beauty.sno self-host (Milestone 1 protection), update PLAN.md to mark CSO done, push.

---

## Risks and mitigation

- **Corpus tests using mixed-case identifiers and relying on SNOBOL4 folding.** Most likely failure surface. Mitigation: per-test triage in CSO-4 / CSO-5; either fix the source to canonical case (preferred) or move to `legacy/` with a note.
- **EVAL'd strings containing mixed-case identifiers.** If a `.sc` file has `EVAL("foo() + Foo()")`, those are now two distinct names. Mitigation: search corpus for EVAL with embedded identifiers; verify case canonicalization at the source.
- **Beauty self-host byte-identity (Milestone 1).** This is the most important gate. The `beauty.sno` corpus has been running case-sensitively since SN-31, so this should hold — but it's the must-not-break invariant. Verify byte-identity at CSO-8.
- **Cross-language calls (SCRIP polyglot statements).** A Snocone function `foo()` called from inside a SNOBOL4 `.sno` block must use the exact case. Currently a `.sno` block might have written `FOO()` expecting fold. Mitigation: build-time grep + manual triage.

---

## State

```
watermark:  CSO directive recorded in RULES.md 2026-05-17 (.github a1558e7b);
            code sweep PENDING.
status:     Directive binding. Sweep not yet executed.
            Default behavior was already case-sensitive (SN-31), so fold calls
            in current codebase are mostly no-ops — sweep is primarily a
            structural cleanup to align code with the new absolute rule.
next:       CSO-1 (snapshot baseline) → CSO-2..CSO-8 sequentially.

Authors:
  directive  Lon, 2026-05-17
  sweep      pending
```
