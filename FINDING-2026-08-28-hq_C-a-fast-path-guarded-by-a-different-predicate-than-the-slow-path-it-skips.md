# FINDING — a fast path guarded by a DIFFERENT predicate than the slow path it skips

**Seat:** hq_C · **Date:** 2026-08-28 · **Row:** `perf-pattern-defer-capture-layer-cure`
**Cures:** SCRIP `aecbe2dc` (funnel + slice-length authority), SCRIP `88675ceb` (GVA quoted-name spelling)

## THE CLAIM

**Three separate wrong answers this session had one shape: a fast path admitted inputs its slow path
would have handled differently, because the guard was a *different function that looked equivalent*
rather than the slow path's own condition.** Two of the three were live on origin; the third was
latent and would have shipped as part of the next briefed slice.

## 1 — THE PUMP CACHE (live, both modes)

`rt_dcap_pump`'s landed caller-side cure keyed its cell cache on `NV_PTR_fn`, read as *"the cell
`NV_SET_fn` would have written."* **It is not that predicate.** `NV_PTR_fn`:

| | `NV_SET_fn` fast path | `NV_PTR_fn` |
|---|---|---|
| `g_call_fastpath_off` | refuses when set | **ignores it** |
| `name[0] == '&'` | refuses | **ignores it** |
| name absent | falls to slow path (io_chan / OUTPUT / TERMINAL / `&subject` / `&pos` / kw / insert) | **CREATES it and returns a cell** |
| `TERMINAL` | routed to its own arm | **not in its refusal list** |

So the store landed in the cell and **the side effect never ran.** Measured against
`/home/resources/x64/bin/sbl -bf`, both modes:

```
OUTPUT(.CAP, 2, 'capout.txt') ; &ANCHOR = 0 ; "hello world" ARB . CAP " "
   sbl  -> capout.txt contains "hello"        SCRIP -> file EMPTY
"hello world" ARB . TERMINAL " "
   sbl  -> "hello" on stderr                  SCRIP -> nothing
```

`g_call_fastpath_off` is the exact mechanism: it flips `0 -> 1` permanently the moment any
`INPUT()`/`OUTPUT()` associates a variable, and `NV_SET_fn` consults it before every cell write.
It must be **re-read per call, never latched** — a cell can be cached long before the flip.

**Cured as a funnel, not a patch.** `NV_CELL_IF_FASTSET_fn` is `NV_SET_fn`'s own admission test
factored out, **and `NV_SET_fn` now calls it**, so the short-circuit and the function it
short-circuits cannot drift apart again.

## 2 — THE SLICE HAD NO TERMINATOR (latent, exposed by curing 1)

Once stores reached `NV_SET_fn` again, the value was *still* wrong: `hello world` where the oracle
writes `hello`. The landed slice-capture hands out a `DESCR_t` pointing **into the subject** with no
terminator of its own; three `NV_SET_fn` slow-path arms (`io_chan`, `TERMINAL`, `&subject`)
stringified it with `%s` / `rt_ws_strdup_c` on `.s`, ignoring `.slen`. All three now go through
`rt_cstr_d`, the length authority the slice work established.

⭐ **`SCRIP_CAP_POISON=1` could not have found this** — poison writes its byte at `copy[len]` in the
**allocated** arm; a slice has no `copy` to poison. An instrument built for a hazard class can be
blind to the arm that removed the allocation.

## 3 — THE SAME CLASS AT COMPILE TIME (live; two tests red for a day)

`gva_io_refuse_scan_graph` refused only `IR_LIT_NAME`. The manual gives **both** spellings as equals
(v3.7 p.2436-2437) and they lower differently — `.FOUT` → `LIT_NAME`, `'FOUT'` → `LIT_STRING`. The
quoted form was admitted to the GVA island, where stores are direct cell writes that never call
`NV_SET_fn`, so **every write to a quoted-association variable was silently dropped — the file was
never written at all**, which is why the read-back could not match.

This is why `corpus/tests/snobol4/feat/{f10_io_basic,f11_io_file}.sno` were held **loose and red**
since 2026-08-27, documented as *"a real, pre-existing correctness bug, invisible to any mandatory
gate"*. Both now PASS in m3 **and** m4; both `.ref`s re-verified against the oracle rather than
trusted. Their stated conversion blocker is gone.

## ⭐ THE TRANSFERABLE PART

1. **A fast path is admissible only for inputs the slow path would have handled identically, so its
   guard must be the slow path's OWN condition** — not a different function that merely looks
   equivalent. `NV_PTR_fn` answers *"where does this name live"*; it was read as *"may I write it
   here."* Both are one-line lookups returning `DESCR_t *`, which is exactly why the substitution
   was invisible.
2. **An exclusion list keyed on ONE SYNTACTIC FORM silently admits every other form of the same
   thing, and looks complete because the form it checks is the one everybody writes.**
3. **Curing a bypass can make a second, older defect visible for the first time.** Defect 2 was
   unreachable while defect 1 existed. A cure that suddenly exposes a wrong *value* where there was
   previously no output at all is not a regression — but it will read as one.

## ⛔ THE BRIEFED SLICE WOULD HAVE PROPAGATED DEFECT 1

The row's remaining brief was *"delete the `NV_SET_fn` call from `rt_cap_open` ARM A"* (~17% of
`porter`). **The immediate-`$` path passes today only because that call is still there** — it is the
control arm that proved defects 1 and 2 were pump-specific. Cutting it against the shipped pump
precedent would have doubled the blast radius. The precondition is now named in code
(`NV_CELL_IF_FASTSET_fn`) and the ASM can be cut against it. Split unchanged: hq_P owns the ASM,
hq_C owns semantics and grading.

## GRADING (pristine `-O0`, SHARED-NODE VERDICT SCOPE — `NV_SET_fn` and GVA are reached by every frontend)

| arm | result |
|---|---|
| SNOBOL4 board m3 / m4 | **1299/1299 · 1299/1299 · FAIL=0 SKIP=0 MISSING=0 rc=0** |
| `test_gate_emit_no_lang` / `test_gate_template_medium_invisible` | rc=0 / rc=0 |
| snocone · rebus | 5/5 · 4/4 |
| Icon control arm (`test_icon_rung_suite.sh`) | 250/250/248 PASS · FAIL 16/16/18 — measured **with and without** the change, byte-identical |
| prolog `clause` | FAIL=1 both modes — **PRE-EXISTING**, verified on the baseline tree |
| perf (no regression) | `pattern_bt` **1.30x** vs `sbl`, `string_pattern` 0.98x, both `check=ok` |

## ⛔ A METHOD FAILURE OF MY OWN, RECORDED BECAUSE IT NEARLY VOIDED A VERDICT

I "verified a baseline" with `git stash push <files>` on files I had **already committed**. The stash
was a no-op, `stash pop` said *"No stash entries found"*, both arms ran the **same** tree — and the
two identical numbers read as a clean confirmation. Caught only because the *expected* difference
failed to appear. **A control arm that cannot fail is not a control arm.** Re-run properly
(`git checkout <commit>^ -- <files>`), the witness did diverge: `done|` where the oracle prints
`hello|done|`. Check `git stash list` shows an entry, and that `git status` was dirty first.
