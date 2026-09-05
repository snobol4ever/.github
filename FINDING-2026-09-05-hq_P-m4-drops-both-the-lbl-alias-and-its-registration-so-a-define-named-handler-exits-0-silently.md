# FINDING — m4 drops BOTH the `LBL__<name>` alias AND its registration, so a DEFINE-named SETEXIT handler exits 0 silently

**Seat:** hq_P · **Date:** 2026-09-05 · **Row:** `setexit-not-invoked-under-errlimit-survival` (reopened by ceo, CEO-286)
**Tree:** SCRIP `2aff59c4c` + this cure · corpus `48d053e21` · .github `530f4eb3` · `RT_OPT=-O0`, mode 3 and mode 4

## The defect

When `&ERRLIMIT` is nonzero and a `SETEXIT`-armed handler should catch a runtime error, **mode 4 printed ZERO bytes
and exited rc=0** — no output, no error, no diagnostic — while mode 3 printed the whole expected transcript. The
ceo's audit witness `.github/probes/errtype/errtype_official_numbers.sno` is the reported case; mode 3 prints
`CAUGHT 5 / next / CAUGHT 38 / done 2`, mode 4 printed nothing at all.

## The minimal pair — ONE ingredient apart

Both programs arm the same handler, take the same error, and resume with `:(CONTINUE)`. They differ **only** in
whether the handler's label is also a `DEFINE`'d function name.

| witness | handler label | m3 | m4 (before) | `LBL__H` in the `.s` |
|---|---|---|---|---|
| `lblhandler_bare` | bare statement label `H` | `caught/after/fin` | `caught/after/fin` | 4× |
| `lblhandler_define` | `DEFINE('H()')` + label `H` | `caught/after/fin` | **(nothing), rc=0** | **0×** |

⭐ **Both oracles AGREE on `caught/after/fin` for BOTH shapes** — measured on `/home/resources/x64/bin/sbl -bf` and
on CSNOBOL4. This is not a dialect-divergent face; there is no ambiguity to rule on.

## Root cause — the chain, and the load-bearing step

1. `scrip.c` **suppresses the `LBL__<name>` asm label alias** when the landing node is already a DEFINE dentry target.
2. `scrip.c` **also drops the `module_init` registration** for `LBL__<name>` when a DEFINE proc defers to that label.
   The emitted `.s` therefore registers only `LBL__START` and `LBL__DONE` — `LBL__ERRH` is registered nowhere.
3. `rt_goto_resolve("ERRH")` (`src/runtime/runtime_eval.c`) misses both its lookups — `rt_label_get_fn` (m3's table,
   empty in m4) and `rt_proc_get_fn("LBL__ERRH")` — and falls through to `core_runtime_error(38, ...)`.
4. That nested error is absorbed by the plain `&ERRLIMIT` survival arm, which **returns**. `rt_goto_resolve` returns
   NULL.
5. `rt_goto_transfer` is `void` — `if (fn) rt_chain_enter(fn);` — so it **cannot express failure** and silently returns.
6. `core_runtime_error` reads that return as *"the handler ran"* and calls **`exit(0)`**.

⭐ **The load-bearing defect is step 5/6: a function that cannot express failure, called by a site that interprets its
only possible return as success.** The alias/registration suppression is merely the trigger — ANY unresolvable
handler label reaches the same `exit(0)`.

## ⛔ The dead end, written down so nobody pays for it twice

The obvious cure — **un-suppress the alias so the symbol is emitted** — was measured on 2026-09-04 and **fails**:
`LBL__H` goes 0× → 3-4× in the `.s` and **the program is still silent**. The reason is that `rt_proc_get_fn` reads
the **runtime registration record** (`rt_proc_register_rec`), not the assembler symbol table. An emitted symbol is
cosmetic to this lookup. ⭐ **Anyone who fixes only the emission will believe they have the cure until they run it.**

A second candidate — guard the trap arm on resolvability and refuse to `exit(0)` — turns the silence into
`ERROR 246 -- stack overflow`, because falling through to the plain survival arm makes the failed statement re-raise
without bound. The survival arm cannot absorb this composition, so "skip the trap when the handler is unreachable"
is not the cure either.

## The cure

Both suppressions are the *same decision expressed in two places*, so both had to go. Guarded by the killswitch
`SCRIP_DEFINE_LBL_ALIAS` (default on; `=0` restores the old behaviour), following the existing
`sn4_module_init_bottom` / `sn4_m4_alpha_seal` idiom in the same file.

⛔ **NO NEW GLOBAL:** the switch is a function-local `static int` caching one `getenv`, byte-for-byte the shape of
its two siblings three lines above it. No file-scope mutable state, no exported cell, no parallel array.

With the cure, `exit(0)` becomes **unreachable** for this shape rather than merely guarded — the trap arm is taken,
so candidate (b)'s unbounded re-raise never arises.

## Evidence

- `errtype_official_numbers.sno`: m4 now byte-identical to m3, all four lines.
- Minimal pair: both shapes `caught/after/fin` in both modes, matching both oracles.
- **Killswitch `SCRIP_DEFINE_LBL_ALIAS=0` restores the silent `exit(0)` exactly** — the arm is non-vacuous.
- Row DONE-WHEN: `SETEXIT_ERRLIMIT_MECHANISM rc=0` (was rc=1, failing on precisely the composition arm).

## Gate

The m4 composition face is wired into `test_gate_sno_setexit_resume_matches_oracle.sh` (already in `make test`), as
**the minimal pair, not the single witness**, so a red names the composition rather than "m4 is broken". It REFUSES
`rc=2` if the m4 build fails, and REFUSES `rc=2` unless the killswitch moves it.

⛔ **Everything that gate tested before today ran mode 3 ONLY** — which is exactly why the 2026-09-04 closure of this
row was green and blind to a mode-4 defect that printed zero bytes. ⭐ **A gate that exercises one mode is evidence
about one mode, and it will not say so.**

## Instrument lessons banked this session

1. ⛔ **`corpus/tests/snobol4/ALL.ref` contains NUL bytes, so plain `grep` silently reports NOTHING rather than
   counting.** `grep -c XFAIL ALL.ref` prints nothing and returns 1; `grep -ac` prints 53. This is the `command -v`
   class again — an instrument answering a narrower question than the one asked, with a well-formed empty answer.
   **Use `grep -a` on any `ALL.ref`.**
2. ⛔ **A torn master takes the WHOLE board down, not one entry.** `75012904f` promoted an entry by removing
   ` XFAIL` from the `ALL.sno` banner and its `ALL.xfail` reason but left the suffix on the matching `ALL.ref`
   banner; `corpus_suite_harness.py` pairs the two banner lists positionally and REFUSES on mismatch, so
   `test_corpus_snobol4.sh` graded **zero** entries and exited rc=2 — on a day when every seat is SNOBOL4-only.
   Measured 1041 banners each side, exactly one differing. (Cured upstream at `48d053e21` by another seat while this
   was being measured; recorded because the *shape* recurs and the blast radius is the surprising part.)
3. ⛔ **A DONE-WHEN that reads a bare `$S4E_HOME` under `set -u` dies `unbound variable` rc=1 — a REFUSAL wearing a
   FAIL's clothing.** Hit on `snobol4-host-argv-not-staged-for-zero-param-entry`; every sibling criterion uses
   `${S4E_HOME:-...}`. A criterion that cannot distinguish *"I could not measure"* from *"it is broken"* is the
   vacuous-test class living inside the closing gate itself.

## ⛔ STILL OPEN — the same `exit(0)` is reachable by a second trigger, in BOTH modes (measured, not predicted)

The cure above removes the *trigger* (an unregistered `LBL__<name>`), not the *blindness*. Censusing the call sites
of the failure-blind function found `rt_goto_transfer` called from **three** places in `core.c` (`:1389`, `:1391`,
`:2157`), none of which can observe a resolve failure — while `rt.c:893`, consuming the sibling `rt_entry_resolve`,
**does** check for NULL and raises `ERROR 286 -- function call to undefined entry label`. The same resolve family is
handled correctly in one place and blindly in another.

That predicted a second live witness, and it reproduces:

```
	&ERRLIMIT = 1000
	SETEXIT(.NOSUCHHANDLER)
	X = NOSUCHFN(1)
	OUTPUT = 'after'
END
```

| | output | rc |
|---|---|---|
| SPITBOL `-bf` | `after` | 0 |
| SCRIP **mode 3** | *(nothing)* | 0 |
| SCRIP **mode 4** | *(nothing)* | 0 |

⛔ **This is NOT mode-specific** — unlike the defect cured above, it is red in mode 3 as well, so no amount of m3/m4
cross-checking would ever have surfaced it. The handler label is simply undefined; SPITBOL survives the error under
`&ERRLIMIT` and carries on, SCRIP silently `exit(0)`s from `core.c:2157`.

⭐ **Deliberately NOT cured under this row, and the reason is the control arm:** this row's landing is being graded by
a full SNOBOL4 master A/B on a loaded box. Folding in a second behavioural change — one that alters what happens on
*every* unresolvable transfer, not just this composition — would confound that A/B and make neither change's
watermark trustworthy. It wants its own row, its own oracle-grounded contract for what SCRIP should do when a
`SETEXIT` label does not resolve, and its own board. **Routed to ceo as its own row rather than ridden in on this one.**
