# FINDING 2026-09-01 (seat16) — `scan_saved` was a leaking stack with a silent cap; the "tab-with-generator-argument" family was a misattribution

Row: `icon-scan-env-value-residue`, item (5a). Tree: SCRIP `f85e1fdc` + this cure. RT_OPT `-O0`. Oracle: `icont_bin`/`iconx_bin` via `lib_oracle_flags.sh`.

## What the baton said, and why it was wrong

The baton attributed **all 25** remaining `rung36_jcon_scan` diff lines to one family — *"tab-with-generator-argument resumption"* — and named a first measurement: the deliberate exclusion at `lower_icon.c:175/:193` (`is_cursor_mover && icn_arg_is_scan_fn(arg)`), asking whether it was the cause or a correct guard for a different shape.

**It is a correct guard for a different shape, and it is not the cause.** Two independent proofs:

1. **Static.** `icn_arg_is_scan_fn` (`lower_icon.c:145`) matches only a `TT_FNC` named tab/move/pos/any/match/many/upto/find/bal. The headline witness `tab(1 to 10)` has a **`TT_TO`** argument, so the exclusion never fires for it. `is_resumable(TT_TO)` is 1 and `la_res` computes 1 — the arg chain is built, exactly as intended.
2. **Empirical.** Every witness in the baton's own list passes **byte-exact against iconx in isolation**, on a pristine build, before any change:
   - `every write("abcdef" ? tab(1 to 10))` → ` /a/ab/abc/abcd/abcde/abcdef` ✅
   - `every write(s ? tab(find(" ")))` → `this/this is/this is a` ✅
   - `every write("abcdef" ? move(1 to 3))` → `a/ab/abc` ✅

   Wrapping them in the rung's own `write(label, image(...) | "none")` shell, and moving them into a called procedure, also passes. **The construct was never broken.**

## What was actually wrong

Bisecting the rung mechanically: `p3()` alone passes; `p1(); p3()` fails; `p2(); p3()` passes. Within `p1`, **no single statement and no pair** triggers it — only the triple. Repeating ONE statement showed the real shape:

| repeated statement | copies to break `p3` |
|---|---|
| `every write((1 to 10) ? move(1))` (line 9) | **2** |
| `every write((("aeiou"\|"foobaz") ? upto('dracula')) ? =(1 to 10))` (line 8) | **4** |
| `every write(("badc"\|"edgf"\|"x") ? write(upto(!&lcase)))` (line 7) | never (≥4 fine) |

A **count**, not a semantic interaction — different statements contribute different amounts of the same resource, and the failure fires when the total crosses a threshold.

The resource is `scan_saved[SCAN_STACK_MAX]` in `src/runtime/builtins/gen_runtime.c`. `rt_scan_leave` **pushed** a departing env's `(subj,pos)` so a later `rt_scan_reenter` could **pop** it. But only a **resumed** env ever pops: an env that is left and then **abandoned** — the ordinary `every`-exhausts-a-scan shape — leaks its slot forever. `scan_saved_depth` grew monotonically across independent statements, and at 16 the old guard

```c
if (scan_saved_depth < SCAN_STACK_MAX) { ...push...; scan_saved_depth++; }
```

**dropped the push with no diagnostic**, so the next `rt_scan_reenter` popped a stale entry belonging to a long-dead scan. That is why the failure looked like a tab bug: `tab(1 to 10)` resumed into someone else's subject and yielded `9` instead of progressive prefixes.

⛔ **This class was already known three times over and cured only site-by-site.** `lower_icon.c:610`, `lower_icon.c:766` and `bb_gen_scan.cpp:42` each carry an `sb=3` no-push arm whose comment says, in substance, *"an ordinary push here leaks one scan_saved entry per exhaustion"*. Slices 3 and 4 each patched the site in front of them. **The general path — a plain leave of an env nobody resumes — was never covered**, and it is the one the corpus actually walks.

## The cure

`scan_saved` is now **indexed by nesting level** instead of used as a free-growing stack: `rt_scan_leave` banks at `scan_saved[scan_depth]` (post-decrement), `rt_scan_reenter` reads the level it is re-entering, and `rt_scan_enter` retires the bank at and above the level it replaces. Level *d*'s slot is overwritten by the next env at level *d*, so nothing accumulates. `SCAN_STACK_MAX` now bounds **nesting depth** — something a fixed 16 can honestly bound — instead of a statement count it never could. `scan_saved_depth` keeps its old meaning (count of valid banked levels from 0) for `rt_scan_state_capture`/`apply`, whose only live callers are co-expressions (`rt_coexpr.c:57/60/79`). **No new global** (ABSOLUTE RULES); the two existing ones carry it.

## Measured

| | before | after |
|---|---|---|
| `rung36_jcon_scan` diff (m3) | 25 | **2** |
| `rung36_jcon_scan` diff (m4) | 25 | **2** |
| `rung36_jcon_scan2` diff | 0 | **0** (unmoved) |

Confirmed both directions: raising `SCAN_STACK_MAX` to 100000 as a pure diagnostic reproduced the identical 25→2, so the stated cause bears the weight of its own repair; the shipped cure is the bounded form, not the bigger cap. Blocking set on pristine: `make test` rc=0 — SNOBOL4 master m3 PASS=1677 FAIL=0 · m4 PASS=1677 FAIL=0 SKIP=0 MISSING=0, plus `capture_stdin_and_red_exit`, `emit_no_lang`, `template_medium_invisible`, `corpus_coverage_classified`, `optbypass_watermark` all green. Smokes icon/prolog/snocone/rebus all rc=0. Blast radius is Icon-only: `rt_scan_enter/leave/reenter` are referenced from `bb_gen_scan.cpp` and `lower_icon.c` and nowhere else.

✅ **RE-PROVEN ON THE MERGED TREE.** The push-time `git pull --rebase` moved the base from `f85e1fdc` to `fbff0649`, which carries emitter commit `32cce542` (BB label names over 80 bytes collided into one symbol) — a tree no proven checkout had existed on. Full re-prove on that merged tree, pristine: `make test` rc=0 (m3 PASS=1677 FAIL=0 · m4 PASS=1677 FAIL=0 SKIP=0 · MISSING=0, all five other gates green), `rung36_jcon_scan` diff **2**, `rung36_jcon_scan2` diff **0**, icon smoke 14/14 both modes. Landed as SCRIP `e9cb8afa`.

⚠️ **An instrument observation, raised not cured.** The first `make test` of this sitting returned rc=2 with `⛔ GATE REFUSES: harness produced no SUITE_BOARD line for the master suite`; the identical tree returned rc=0 on re-run, and the machine was at **load 21.73 on 16 cores**. `test_corpus_snobol4.sh:205` invokes the harness as `... 2>/dev/null | grep '^SUITE_BOARD '`, so whatever the harness said about its own trouble was discarded before anyone could read it, and the gate reported the absence of a line rather than the reason for it. A refusal that a busy machine can induce, and that swallows its own stderr on the way, will read to the next seat as a real gate failure on their change. Out of this row's lane; raised to HQ as `q-corpus-gate-refusal-under-load`.

## What remains (attributed, not abandoned)

The last 2 diff lines are a **different defect**, with a clean ablated pair:

- ✅ `every write(("aeiou" | "foobaz") ? upto('dracula'))` → `1 5 5` — **passes**
- ⛔ `every write((("aeiou" | "foobaz") ? upto('dracula')) ? =(1 to 10))` → we give `1 5`, iconx gives `1 5 5` — **fails**

One ingredient apart: the inner scan-over-alternation generator is correct standalone and loses its **third** value when it becomes an **outer scan's subject**. Not a `tab`/mover shape and not the leak — mint it as its own slice.

Item **(5b)** (concede-path reversal residue, `foo(){suspend move(1); write("B")}` then `write(&pos)` → we print 2, iconx 1) is untouched by this cure and still belongs to the N-2 concede path.

## The generalisable half

⭐ **A resource whose overflow guard silently declines to record is indistinguishable from one that is working, right up until a reader pops someone else's entry.** The old guard was written to prevent an overrun and succeeded at that; what it never did was say that it had stopped recording. Three sessions cured three *sites* of the resulting corruption without the shared resource ever being questioned, because each site's local fix genuinely worked. ⛔ **And the misattribution is the more expensive half: a family named for the construct that FAILS, rather than for the resource that is exhausted, sends the next reader into the lowerer for a bug that lives in the runtime.** The cheap discriminator was available the whole time and takes one minute — *run the failing construct on its own*. It passed.
