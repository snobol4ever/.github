# FINDING — CURE LANDED: Icon's `!x` (element generator) never coerced a numeric `x` to its string
# form before generating characters, so `every write(!<number>)` silently produced ZERO results
# instead of the number's digits one at a time. Root-caused to one C function, fixed with a four-line,
# purely-additive change, verified broadly (Icon board all 3 modes + SNOBOL4 1517-entry control arm,
# both clean). Landed.

**seat01 · 2026-08-30 · row `icon-rung-ladder-absorption`** (Class C, per hq_P's steer — the
output-content-mismatch reds; this is the first one fully closed this session rather than merely
characterized).

## 1. The bug, empirically confirmed before touching anything

Witness: `rung36_jcon_every.icn` lines 21-22, `every write("p. ", !-514); every write("q. ", !12.5);`.
Real Icon (`/home/resources/icon-master/bin/icon`) on the minimal repro:
```
p. -
p. 5
p. 1
p. 4
q. 1
q. 2
q. .
q. 5
```
— i.e. `!<number>` coerces the number to its string form, then generates each character. SCRIP (both
m3 and m4, pre-fix): zero output, `rc=0`. Full-file diff against `.expected`: exactly the trailing 8
lines missing, nothing else — a clean, isolated symptom, not a cascade.

## 2. Root cause

`!` (`TT_ITERATE`) lowers to `IR_ITERATE`, emitted by `bb_iterate.cpp`, which calls
`rt_list_bang_at`/`_var_at`/`_key_at` (`rtx_icnagg.s`, hand-written asm) — a thin wrapper whose real
logic is the C function `list_bang_at()` in `rt_runtime.c:467`. That function dispatches on `obj.v`:
`DT_DATA` (list/struct), `DT_FH` (file, line-read), `DT_T` (table, pair-walk), then a final fallback
block that **only** extracted characters when `obj.v == DT_S` (already a string) — any other type
(including plain integers/reals) left `s = NULL` and returned 0 (fail) immediately. Confirmed by
direct read, not inferred from the symptom alone.

## 3. The fix

`src/runtime/rt_runtime.c`, the fallback block in `list_bang_at()`:
```c
DESCR_t     sobj = (obj.v == DT_S) ? obj : descr_to_str_fracdigit(obj);
const char *s    = (sobj.v == DT_S) ? sobj.s : NULL;
int64_t     slen = !s ? 0 : (IS_CSET_fn(sobj) ? (int64_t)strlen(s) : (int64_t)(sobj.slen > 0 ? sobj.slen : strlen(s)));
```
(previously read `obj` directly everywhere `sobj` now appears). `descr_to_str_fracdigit` — not the
plain `descr_to_str` — because `lower_icon.c:369` shows Icon's own `||` concatenation always upgrades
to the FRACDIGIT real-number formatter (`icon_real_str`, Icon's own convention), so this coercion
matches how Icon already stringifies numbers everywhere else, not a new convention invented for this
fix. Both `coerce.h` and `descr_to_str` were already in use in this exact file — zero new includes.
**Purely additive**: every existing branch (DT_DATA/DT_FH/DT_T, and the pre-existing DT_S passthrough)
is untouched; the only new behavior is that a previously-always-failing type now has a chance to
succeed via coercion, and only if that coercion itself succeeds (an uncoercable type still correctly
falls through to `return 0`, unchanged).

Scope: `list_bang_at`/`_key_at`/`_var_at` are reachable only from `IR_ITERATE`, which
`lower_icon.c` is the sole producer of (`TT_ITERATE` is an Icon-only parse-tree node) — this is
Icon-only by construction, not by an added guard.

## 4. Verification (full control battery, not a spot check)

- `make pristine`: exit 0.
- `test_smoke_icon.sh`: 14/14 both modes, unchanged.
- `test_icon_rung_suite.sh` (all 3 modes — interp/run/compile): `rung36_jcon_every` now **XPASS**
  ("marked XFAIL but now genuinely passes") in all three; `PASS=259 FAIL=8 BADEXIT=1 XFAIL=28 XPASS=1
  TOTAL=297` in every mode — nothing else moved.
- `test_corpus_snobol4.sh` (control arm, unrelated language): `m3 PASS=1517 FAIL=0 · m4 PASS=1517
  FAIL=0 SKIP=0 · MISSING=0` — **GATE OK**, zero regressions.
- Re-checked the other 12 uncharacterized Class-C candidates (`arith`/`case`/`checkfpx`/`ck`/
  `errkwds`/`large`/`nargs`/`sets`/`sorting`/`gener`/`radix`/`fncs`) against the fixed binary: **all
  12 unchanged**, confirming the fix is precisely scoped to this one root cause, not a lucky
  side-effect on a shared code path.

## 5. Stale marker note

`rung36_jcon_every.xfail`'s own text read `"crashes: SIGSEGV (rc=139). Not further diagnosed"` —
**not the bug this FINDING fixes.** Some earlier, untraced commit already cured that crash (same
"fix predates the marker's removal" pattern as `diffwrds`/`fncs1` in this same directory's `KEEP.md`);
this session's fix cured the DIFFERENT defect (missing output, not a crash) that was left over
afterward. Marker deleted (corpus) rather than rewritten, per this project's established promotion
convention for a genuine XPASS.

## 6. State

SCRIP tree was `ee2a24df`-DIRTY at measurement (this fix, uncommitted at verification time); committing
alongside this FINDING. corpus: xfail marker removed. `tests/icon/KEEP.md`'s rung36 list updated to
remove `every` from the "28 still genuinely red" bucket.
