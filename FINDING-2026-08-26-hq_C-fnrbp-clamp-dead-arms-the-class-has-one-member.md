# FINDING — `fnrbp()` clamp-shadowed arms deleted; the CLASS was swept and has exactly one member

**Seat:** hq_C · **Date:** 2026-08-26 · **Row:** `rung-fnrbp-clamp-dead-arms` (owning rung: `GOAL-SNOBOL4-100.md` R-7)
**Tree:** SCRIP `8d27b148` + this commit · corpus `14c5cf745`

## The row was the CLASS, not the sites

Brief, verbatim: *"YOUR ROW IS THE CLASS — clamps that silently shadow branches — not the four sites."* So the deliverable is a swept class, and the sites are incidental. Both halves are below.

## 1. The domination proof

```c
src/templates/bb_define.cpp:363
static int fnrbp(void) { static int v = -1; if (v < 0) { const char * e = getenv("SCRIP_FN_RBP");
                         v = e ? atoi(e) : 2; if (v == 1) v = 2; if (v < 0 || v > 2) v = 2; } return v; }
```

`fnrbp()` returns **0 or 2, never 1**, on every call forever:

1. `fnrbp` is `static` — file-local, and declared in **no** header (`grep -rn fnrbp src/ --include=*.h` → 0).
2. `SCRIP_FN_RBP` is read at **exactly one** site, this line.
3. `v` is a function-local `static int`; its address is never taken and nothing else writes it.
4. The initializer body is guarded by `v < 0`, so it runs on the **first** call, before any `return`. Its last two statements are the clamp: `if (v == 1) v = 2` removes 1; `if (v < 0 || v > 2) v = 2` removes everything outside `[0,2]`. The surviving set is `{0, 2}`.
5. Later calls skip the body and return the already-clamped `v`.

∴ the clamp **dominates every path to every test**, and `fnrbp() == 1` is false on all of them. ∎

**Three dead arms** (brief said two in role-4; the true count is three, and the two the brief attributed to `bb_save_restore.cpp:161/213` are among them — that file was folded into `bb_define.cpp` at `abcfc02e` s116, so the line numbers moved and the class did not):

| site | shape |
|---|---|
| `bb_define.cpp:470` | `IF(fnrbp() == 1, …)` s63 RBP-FUNCTION WRITER (role-4) |
| `bb_define.cpp:524` | `IF(fnrbp() == 1, …)` s63 RBP-FUNCTION WRITER |
| `bb_define.cpp:555` | `if (fnrbp() == 1) return …` s63 RETURN/FRETURN/NRETURN floater |

## 2. The class sweep — 42 selectors, one offender

Mechanically enumerated every `static int NAME(void) { static int v = -1; … return v; }` selector in `src/`, simulated each clamp chain to a possible-value set, and tested every `NAME() == N` / `!= N` / bare-boolean use against it.

**42 selector functions. Exactly one has an unreachable arm: `fnrbp()`.** The other 41 are honest — 8 are `v = e ? (atoi(e) != 0) : N` booleans with possible set `{0,1}` and no out-of-range comparison anywhere.

⛔ **The sweep tool had this same bug first, and that is worth recording.** Its first version reported `fnrbp() -> possible [-3,-2,-1,0,2,3,…]` — too wide. Cause: it `eval`'d the C condition `v < 0 || v > 2` as Python, where `||` is a syntax error, and a bare `except: pass` swallowed the throw so the range clamp was **never applied**. It reached the right verdict on `==1` for the wrong reason. Fixed by translating `||`/`&&` and, more importantly, by making an unmodelled initializer **report itself as UNMODELLED rather than silently widening** — 8 did, and were then closed by hand.

⭐ **That is the row's own class biting the instrument built to hunt it**, and it is the third instance this session of one shape: *an arm that cannot fire, in a place where nothing downstream contradicts it.* A swallowed exception, a clamped comparison, and a `grep` pattern that matches one phrasing are the same defect at three altitudes. **The common signature: the code reads as if it decides something, and no observation can tell you it doesn't.**

## 3. What was deliberately NOT deleted

⛔ **The `if (v == 1) v = 2;` clamp STAYS, and it is now load-bearing for a different reason than it was written for.** With the `==1` arms gone it looks like pure residue, but it maps a legacy `SCRIP_FN_RBP=1` invocation onto the live s64 RSP-ONLY arm. Delete it and `v` becomes 1, no arm matches, and the site falls through to the **s58 BOMB** — i.e. removing an apparently-dead line would silently convert a legacy env value into emitted bomb code.

⛔ **`SCRIP_FN_RBP=0` is REACHABLE and selects the BOMB arm deliberately.** R-7 lists the whole `SCRIP_FN_RBP` knob as "unreachable"; that is true of the **value 1 only**, not of the knob. Retiring the knob is a behaviour change and belongs to R-7's killswitch fold, not to this row. **Scope held: this row deleted three provably-dead arms and nothing else.**

## 4. Verification

- **TEXT medium:** 350 corpus programs emitted `--compile` before and after; **319 compile, and all 319 `.s` are byte-identical** (`diff -rq` clean; content-manifest `969fb94f5a9a29e9d50442dea2d1f164` on both sides). The 31 non-compilers are pre-existing and identical in both arms.
- **BINARY medium:** `test_corpus_snobol4.sh` → **m3 PASS=365 FAIL=0 · m4 PASS=365 FAIL=0 SKIP=0 · MISSING=0**.
- **`make pristine` rc=0** (162s), and the baton DONE-WHEN re-run post-pristine: `test_gate_emit_no_lang` rc=0 · `test_gate_template_medium_invisible` rc=0 · `test_corpus_snobol4` rc=0.

⛔ **A first content-manifest comparison printed a false mismatch** — `md5sum` output embeds the **path**, so hashing its output compared `emit_before/x.s` against `emit_after/x.s` as text and always differed. `diff -rq` was right; the manifest was answering a different question. Recomputed path-independently. *(Same family as §2; noted because it would have read as a real regression.)*

## 5. Byproduct: the 30s corpus timeout is inside the run-to-run spread

Board measured **28s, then 33s, on the same tree** in this session (hq_P measured 32s in their root). The long-standing `timeout 30s` advice therefore does not fail — it fails **intermittently, on a fully green board**, and prints as a hang. ⭐ A timeout tuned to a job's measured duration is not a tight bound, it is a flaky one; a whole-board timeout exists to catch a hang and belongs an order of magnitude above the measurement. Corrected to `timeout 600` in this root's digest.
