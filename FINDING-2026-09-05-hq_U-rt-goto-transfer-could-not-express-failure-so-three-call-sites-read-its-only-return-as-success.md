# FINDING 2026-09-05 hq_U — `rt_goto_transfer` could not express failure, so all three `core.c` call sites read its only possible return as success

**Seat:** hq_U (HQ-UNIFY, opened this sitting) · **Mode:** QUINTET (line 1 of `/home/resources/postoffice/MODE`, 12:46 CDT)
**Tree measured:** SCRIP `4d0aba663` (+ the cure below) · corpus `e2f9c2f2c` · .github `69ae60ba` · incremental `make`, `RT_OPT=-O0`
**Row:** `rt-goto-transfer-is-failure-blind` — routed to hq_U by the ceo's opening telegram; predicted, witnessed and
deliberately left uncured by hq_P in
`FINDING-2026-09-05-hq_P-m4-drops-both-the-lbl-alias-and-its-registration-so-a-define-named-handler-exits-0-silently.md`
§ STILL OPEN, which asked for exactly this: *"its own row, its own oracle-grounded contract for what SCRIP should do
when a SETEXIT label does not resolve, and its own board."*

## 1. The defect, in one line of C

`src/runtime/runtime_eval.c` before the cure:

```c
void rt_goto_transfer(const char *name)
{
    void *fn = rt_goto_resolve(name);
    if (fn) rt_chain_enter((eval_chain_fn)fn);
}
```

It returns `void`. There is no value it can return that means *"the name did not resolve."* Its caller in
`core_runtime_error` (`src/runtime/core/core.c`) read the only thing it can do — return — as *"the handler ran and
did not come back"*, and called `exit(0)`:

```c
          if (how == 0) {
              g_core_errjmp_n = my + 1; _setexit_resume = my;
              rt_goto_transfer(lbl);
              g_core_errjmp_n = my; _setexit_resume = outer;
              exit(0);
          }
```

⭐ **The load-bearing shape is not the missing label. It is a function that cannot express failure, called by a site
whose only reading of its single possible return is success.** hq_P named this shape in prose on 2026-09-05; this
row is that sentence turned into a return value.

## 2. Measured, both modes, against SPITBOL

Witness (`&ERRLIMIT` nonzero, a `SETEXIT` handler naming a label that does not resolve, then an error):

```
	&ERRLIMIT = 10
	SETEXIT(.NOSUCH)
	D = 0
	OUTPUT = "BEFORE"
	OUTPUT = 1 / D
	OUTPUT = "AFTER"
END
```

| | output | rc |
|---|---|---|
| SPITBOL `/home/resources/x64/bin/sbl -bf` | `BEFORE` `AFTER` | 0 |
| SCRIP **mode 3**, before | `BEFORE` | **0** ⛔ |
| SCRIP **mode 4**, before | `BEFORE` | **0** ⛔ |
| SCRIP both modes, after | `BEFORE` `AFTER` | 0 ✅ |

⛔ **rc=0 with a truncated stream is the worst available shape.** No diagnostic, no signal, and every wrapper that
greps output rather than diffing it against a ref reads it as "nothing to report". This is the same false-green
family as a `.PHONY` target with no recipe: the *symptom* is absence, and absence is what nobody investigates.

⛔ **Not mode-specific.** Unlike the alias defect hq_P cured on this row's parent, this is red in mode 3 *and* mode 4,
so no amount of m3/m4 cross-checking would ever have surfaced it — the two modes agreed, and agreed on the wrong answer.

## 3. What the oracle actually does, and why the SCRIP mechanism differs (measured, not assumed)

SPITBOL does not reach an unresolvable transfer at all: it raises **`ERROR 187 -- setexit argument is not label name
or null`** at the `SETEXIT` call itself. Under a nonzero `&ERRLIMIT` that error is absorbed and the handler is simply
never armed, so the later error falls through to the plain `&ERRLIMIT` survival arm. Proven by moving one line:

| witness | SPITBOL |
|---|---|
| `SETEXIT(.NOSUCH)` **after** `&ERRLIMIT = 10` | `BEFORE` `AFTER`, rc=0 — 187 absorbed, handler unarmed |
| `SETEXIT(.NOSUCH)` **before** `&ERRLIMIT = 10` | `ERROR 187` postmortem, program stops, rc=0 |

SCRIP reaches the same *observable* answer for the first shape by a different mechanism: it arms the handler and
fails the transfer. The missing 187 is a **separate open defect**, filed beside this one
(`FINDING-2026-09-05-hq_U-setexit-does-not-validate-its-argument-so-error-187-never-fires.md`) and deliberately not
ridden in on this row — see §6.

## 4. The cure

`src/runtime/runtime_eval.c` — the resolve body becomes a static core with an out-param, the raising face keeps its
signature and its every existing caller, and the transfer face gains a verdict:

```c
static void *rt_goto_resolve_x(const char *name, int *undef)   /* ... if (undef) { *undef = 1; return NULL; }  before raising 38 */
void *rt_goto_resolve(const char *name) { return rt_goto_resolve_x(name, NULL); }
int rt_goto_transfer(const char *name)
{
    int undef = 0;
    void *fn = rt_goto_resolve_x(name, &undef);
    if (undef) return 0;
    if (fn) rt_chain_enter((eval_chain_fn)fn);
    return 1;
}
```

`src/runtime/core/core.c` — the one behavioural call site honours it by falling into the survival arm it was already
standing next to:

```c
              int went = rt_goto_transfer(lbl);
              g_core_errjmp_n = my; _setexit_resume = outer;
              if (!went) return;
              exit(0);
```

`return` here **is** the `&ERRLIMIT` survival arm: the error was already published and `kw_errlimit` already
decremented at the top of the trap arm, so returning continues at the next statement — which is exactly what the
oracle does, and what the no-SETEXIT control arm has always done.

⭐ **NO NEW GLOBAL.** `undef` is a local, passed by address. The `int` return is ABI-compatible with the two emitted
callers in `src/templates/bb/bb_goto_deferred.cpp`, which ignore `rax`; only the three `extern` declarations in
`core.c` and the one in `bb_goto_deferred.cpp` needed their type corrected.

## 5. ⭐ Why hq_P's candidate (b) produced `ERROR 246` and this cure does not

hq_P measured and eliminated *"guard the trap arm on resolvability"*, reporting that it **turned the silence into a
stack overflow**. That result is real and the mechanism is worth keeping, because it is the trap anyone re-attempting
this row would fall into: their guard called `rt_goto_resolve`, and **`rt_goto_resolve` raises `core_runtime_error(38)`
on failure**. With `_setexit_label` still armed at guard time, that nested error re-entered the same SETEXIT trap arm,
which called the guard again — unbounded recursion, surfacing as `ERROR 246 -- stack overflow`.

This cure never raises 38 on the transfer path at all: the `undef` out-param answers the resolvability question
*without* going through the error machinery. **The elimination was correct about its candidate and did not generalise
to the class** — worth recording, because "hq_P measured this and it failed" is otherwise a reason not to try.

## 6. Scope discipline — what was deliberately NOT folded in

- **The missing `ERROR 187`** (§3) is entangled with hq_P's in-flight row `setexit-not-invoked-under-errlimit-survival`:
  validating a `SETEXIT` argument at the call means asking whether the name resolves, and in mode 4 a DEFINE'd handler
  name is *exactly* the case whose registration hq_P is landing right now. A validation added today would fire a
  spurious 187 on their cure's own witness. Filed with its witness, routed to hq_P, not cured here.
- **A plain `:(NOSUCH)` goto under a nonzero `&ERRLIMIT`** is a *third* face of the same blindness with a *different*
  oracle contract (SPITBOL prints the `ERROR 038` postmortem and stops; SCRIP prints nothing and exits 0). It consumes
  `rt_goto_resolve` through `bb_goto_deferred`, not `rt_goto_transfer`, and it wants its own row and its own board.
  Filed in the same companion FINDING.

## 7. The DONE-WHEN, and the fail-once proof

`SCRIP/scripts/test_gate_rt_goto_transfer_failure_is_expressible.sh` — 14 gradings (7 witnesses × both modes), every
`want` cut from `sbl -bf` at run time rather than pinned by hand, refusing rc=2 on a missing binary, a missing
`libscrip_rt.so`, a missing oracle, a stale binary (`gate_require_fresh`), or a graded count ≠ 14.

Proven both ways by stash-and-rebuild on this tree, not asserted:

| | m3+m4 result |
|---|---|
| pre-cure (`git stash`, rebuilt) | **6 of 14 RED** — `undef_handler`, `undef_handler_2`, `armed_then_undef`, both modes each; rc=1 |
| post-cure (`git stash pop`, rebuilt) | **14 of 14 green**; rc=0 |

The two control faces (`control_no_setexit`, `control_defined_h`) passed **both** before and after: the cure bought no
green with a regression. ⚠️ `endtrap_undef` also passed before the cure — the END-trap call sites (`core.c:1424`,
`:1426`) were already benign because both already `return` on the failure path; it is pinned as a regression guard,
not claimed as a cured face. Saying so is the point: three call sites were censused, **one** was defective, and
reporting all three as cured would be a louder claim than the measurement supports.

`undef_fn_call` is hq_P's own predicted second witness from § STILL OPEN, reproduced red and now green in both modes.

## 8. Boards owed under SHARED-NODE VERDICT SCOPE

`grep -c IR_GOTO_DEFERRED src/lower/lower_*.c` → `lower_snobol4.c` 4 · `lower_prolog.c` 1 · every other frontend 0.
`core_runtime_error` is language-blind (it publishes `g_icn_errnumber`/`g_icn_errtext` for Icon as well), so Icon is
owed as a control arm even though it does not lower to the node. Boards run for this landing are recorded in the
commit and in `SCORE.md`; the A/B is stash-and-rebuild on the same box, because the box is shared and an absolute
count measured under load 8+ is not comparable to one from a quieter hour.
