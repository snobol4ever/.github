# HANDOFF 2026-06-15 — Raku: Str/Cool/List method suite (runtime-only, both native modes)

## Session: GOAL-RAKU-BB. Lon: "get some new Raku features working." Delivered a 30-method Str/Cool/List suite via one new runtime dispatch helper — no parser/template/lowering/gate change.

**SCRIP HEAD at open: `c602da9`. Local commits this session (7, pushed — see push notes):**
- `44079f5` — Str methods uc/lc/tc/tclc/fc/chars/flip/trim + Str/Int coercion.
- `9492211` — arg-taking Str methods contains/index/substr.
- `ccc2412` — numeric methods abs/floor/ceiling/round.
- `eeb703a` — .Bool/.so/.not truthiness + numeric .succ/.pred.
- `7650025` — list-returning Str methods words/comb/split.
- `b711c0b` — Str methods wordcase/chomp/lines.
- `c82bc7e` — list methods .join/.elems on SOH-list values.

**`.github` local commits (pushed LAST):** this doc + GOAL-RAKU-BB watermark entry.

**Gates at close — Raku m3 69 PASS / 0 FAIL / 7 EXCISED; m4 same / 76 tests.** Smoke grew 38→76
(+38 method tests, all PASS both native modes). Peers invariant: Icon m3/m4 12/12, SNOBOL4 m4 7/7.
`g_vstack`=0, `bb_bin_t`=0, IR_NFA residual=0. The 7 EXCISED are unchanged (4 map/grep PUMP + 3 `~~`
regex on the C matcher). The 5 pre-existing `audit_concurrency_invariants.sh` VIOLATIONs + 1
`util_template_purity_audit.sh` site (`bb_call_write_slot.cpp`) are UNCHANGED (not introduced here).

---

## What landed — the 30 methods

| Category | Methods | Result type |
|---|---|---|
| Str case/shape (nullary) | `.uc` `.lc` `.fc` `.tc` `.tclc` `.flip` `.trim` `.wordcase` `.chomp` | Str |
| Str measure (nullary) | `.chars` | Int |
| Str→list (nullary) | `.words` `.comb` `.lines` | List (SOH) |
| Str args | `.contains(n)` `.index(n)` `.substr(from[,len])` `.split(sep)` | Bool(0/1) / Int|Nil / Str / List |
| Coercion | `.Str` `.Int` `.Bool` `.so` `.not` | Str / Int / 0/1 |
| Numeric | `.abs` `.floor` `.ceiling` `.round` `.succ` `.pred` | Int (abs/succ/pred preserve type) |
| List | `.join([sep])` `.elems` | Str / Int |

Semantics anchored to Rakudo `src/core.c/{Str,Cool,Int,List}.rakumod` (read this session):
- `.tc` upcases only the FIRST char (rest unchanged); `.tclc` = tc-first + lc-rest; `.wordcase` = tc per word.
- `.trim` strips leading AND trailing whitespace (the pre-existing `TRIM_fn` only did trailing spaces — NOT reused).
- `.chars` = codepoint count (`utf8_strlen`). `.comb` splits codepoints (utf8_seqlen-aware).
- `Str.Bool` = non-emptiness (so `"0"` is True; only `""` is False). Int/Real `.Bool` = nonzero.
- `.contains` → 0/1 (SCRIP's bool convention, per `bool_compare_store`); `.index` → 0-based position or `NULVCL`(Nil).
- `.substr` is 0-based (Raku) — converted to the 1-based `SUBSTR_fn(from+1,len)`; optional length = to end.
- `.split(sep)` keeps empty fields (Raku default); empty sep = codepoint split. `.words` drops empty runs.
- `.succ`/`.pred` numeric only (±1); STRING magic-increment ("az".succ→"ba") DEFERRED.

---

## The mechanism (how 30 methods cost ~3 small runtime edits)

ONE new function `rt_str_method(const char *meth, DESCR_t recv, const DESCR_t *margs, int nmargs, DESCR_t *out)`
in `src/runtime/by_name_dispatch.c` (after `grammar_parse_core`, before `meth_call` so it is in scope).
Returns 1 if `meth` is recognized, 0 otherwise. Coerces `recv` via the existing static `to_cstring`; numeric
methods use `to_real`/`recv.i`. List results are SOH-separated strings (the `(1,2,3)` representation) so they
round-trip through `say` (`out_write_str` renders any `\x01`-bearing string space-joined) and through the
`elems()` builtin / the new `.elems` method.

Reached from BOTH Raku method-call shapes, which already EMIT natively in m3/m4 (no gate change needed):
1. **`.meth` (no parens)** → parser `TT_FIELD` → `IR_FIELD_GET` → template `bb_field_get.cpp` calls
   `dat_field_get(fname, obj)` (`src/driver/driver_data.c`). Edit: when `data_field_ptr` returns NULL and the
   receiver is not `DT_DATA`, call `rt_str_method(fname, obj, NULL, 0, &r)` before returning FAILDESCR.
2. **`.meth(args)` (parens)** → parser `TT_METHCALL` → `meth_call` (IR_CALL dval=2, "meth_call" is
   `rt_builtin_is_known` → CALL_ROUTE_BYNAME → native). Edit: after the grammar-`parse` check and BEFORE the
   `args[0].v != DT_DATA` class gate, `if (nargs>=2 && args[0].v!=DT_DATA && rt_str_method(mname0, args[0],
   &args[2], nargs-2, out)) return 1;`.

Field lookup precedence is preserved: a real class field named e.g. "chars" wins (`data_field_ptr` runs first);
method-name routing only fires for non-`DT_DATA` receivers or NULL field lookups → class_method smoke unchanged.

**Files touched (3):** `src/runtime/by_name_dispatch.c` (+`rt_str_method`, +utf8.h include, meth_call branch),
`src/driver/driver_data.c` (dat_field_get fallthrough). No header needed — call sites use inline `extern`
(consistent with the file's existing style).

---

## ⚠ GOTCHA honored (cost prior sessions real time): rebuild BOTH after any runtime edit
`scrip` STATICALLY links the runtime; `out/libscrip_rt.so` is mode-4 ONLY. After every runtime `.c` edit:
`rm -f scrip && make -j4 scrip && make libscrip_rt`. The smoke harness exercises both; do not trust a
one-sided rebuild.

---

## Compliance (all clean)
No templates touched, no value stack (`g_vstack`=0), no language guards (`rt_str_method` is CS-neutral —
0 hits in `test_gate_no_lang_names.sh`; method names like "uc"/"chars"/"join" are not language names), no
IR/AST walk on the run path (operates on `char*`/`DESCR_t` only). FACT-RULE clean. Pre-existing baselines
(NOT introduced, verified): 5 `audit_concurrency_invariants.sh` VIOLATIONs (LOWER/EMITTER md5 drift +
stale `src/lower/lower.c` path), 1 template-purity site (`bb_call_write_slot.cpp`).

---

## Honest deferrals / pre-existing gaps surfaced (none introduced)
- **`.sqrt` held back.** Computes correctly (REALVAL(sqrt)), but SCRIP prints integer-valued reals as `3.0`
  while Raku prints `3` — a pre-existing real-stringification divergence (`say(3.0)`→"3.0"), not method-
  specific. Re-add `.sqrt` once reals stringify Raku-faithfully (would also tidy Real output broadly).
- **Unary minus** (`my $n = -5`) EXCISES in m3/m4 (TT_MNS has no native arm) — a pre-existing lowering/emit
  gap. Tested `.abs` negative branch via `3 - 8` (binop subtraction, which DOES emit) to avoid it.
- **Chained method calls** (`.trim.lc`, `.split(",").elems`) are a PARSER limit — `.method` does not chain.
  Worked around in smokes via `my @a = ...; elems(@a)` / `@a.join(...)`. Lifting chaining is a raku.y rung.
- **Hyphenated method names** (`.starts-with`/`.ends-with`) are a LEXER limit (hyphen → subtraction). Skipped;
  needs a flex change.

---

## ORDER OF WORK for next session (unchanged priorities + cheap new options)
1. **RK-GRAM-3 (THE SEAM)** — recursive-descent grammar engine on the SNOBOL4 `bb_match_*`/`bb_pattern_*`
   boxes (LEAD RUNG; full budget + `ARCH-x86.md`/`ARCH-SCRIP.md` reads). See CURRENT PRIORITY at top of goal.
2. **RK-EMIT-MAP/GREP** — the generator-PUMP for the 4 EXCISED map/grep tests (`bb_rk_map.cpp`/`bb_rk_grep.cpp`).
3. **Cheap method follow-ups** (same `rt_str_method` chokepoint, runtime-only): real-faithful stringification
   to unlock `.sqrt`; string `.succ`/`.pred` magic-increment; `.subst`/`.trans`; more List methods
   (`.reverse`/`.sort`/`.sum`/`.min`/`.max` as methods — `.sort`/`.reverse`/`.sum` builtins already exist).
4. (Parser/lexer rungs, separate from runtime): method-call chaining; hyphenated identifiers; `**`/`unless`/
   `elsif`/ternary `?? !!`.

---

## ⚠ PUSH NOTES (use the token URL — bare `git push origin main` has failed for prior sessions)
```bash
cd /home/claude/SCRIP
git fetch origin && git pull --rebase origin main      # peers may be ahead; resolve, then rebuild + re-gate
rm -f scrip && make -j4 scrip && make libscrip_rt       # MUST rebuild BOTH after any rebase
bash scripts/test_smoke_raku.sh                         # m3/m4 69 PASS / 7 EXCISED
bash scripts/test_smoke_icon.sh ; bash scripts/test_smoke_snobol4.sh
git push https://<TOKEN>@github.com/snobol4ever/SCRIP main
# THEN .github LAST:
cd /home/claude/.github && git pull --rebase origin main
git push https://<TOKEN>@github.com/snobol4ever/.github main
# Confirm in each: git log origin/main --oneline -1   shows your hash.
```

## Session Setup (next session)
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
rm -f scrip && make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_raku.sh      # m3/m4 69 PASS / 0 FAIL / 7 EXCISED  / 76
bash scripts/test_smoke_icon.sh      # 12/12/12 HARD
bash scripts/test_smoke_snobol4.sh   # m4 7/7 HARD
```

## Commits this session
| Commit | Repo | What |
|---|---|---|
| `44079f5` | SCRIP | Str uc/lc/tc/tclc/fc/chars/flip/trim + Str/Int coercion |
| `9492211` | SCRIP | arg Str contains/index/substr |
| `ccc2412` | SCRIP | numeric abs/floor/ceiling/round |
| `eeb703a` | SCRIP | Bool/so/not + numeric succ/pred |
| `7650025` | SCRIP | list-returning words/comb/split |
| `b711c0b` | SCRIP | wordcase/chomp/lines |
| `c82bc7e` | SCRIP | list .join/.elems |
| (this doc + watermark) | .github | handoff |
