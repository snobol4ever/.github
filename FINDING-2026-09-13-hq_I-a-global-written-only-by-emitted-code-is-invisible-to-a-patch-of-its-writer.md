# A global WRITTEN only by emitted code is invisible to a patch of its writer

**hq_I · 2026-09-13 · measured on SCRIP `a672836a3` → cured at `e39d0c761`, corpus `52b80e32c`**

## The defect, in one line

`&CODE` never set the process exit value. `&CODE = 3` exited **rc=0** under scrip on the `.sc`
and the `.sno` path alike, where `sbl -bf` exits **3** — a program the oracle marks as failing
produced a plausible success under scrip. That is the dangerous direction.

## Why it survived: `kw_code` was write-only

`grep -rn kw_code src/` returns **three** hits and not one of them is a read:

| site | what it is |
|---|---|
| `core.h:306` | `extern int64_t kw_code;` |
| `core.c:983` | `int64_t kw_code = 0;` — the definition |
| `core.c:3246` | one store, inside `ASGNIC_fn` |

A value recorded and never consulted. Nothing in the compiler reads it, so nothing fails when
it is wrong, and the keyword "works" in the only sense anyone tests: you can assign it.

## ⛔⭐ The part worth keeping: the obvious cure does not work, and says nothing

The obvious cure is to arm the exit behaviour at the setter, `ASGNIC_fn`. **It changed nothing.**
A debug `fprintf` placed inside that setter **never printed** — for `.sc` or `.sno`.

`&CODE = 3` never calls a C setter at all. The emitted code stores `kw_code` **directly by
symbol**: `keywords.c`'s `KWB_ENT_t` carries the symbol name in its own `sym` column
(`{ "CODE", KWB_INT, 0, &kw_code, 0, 0, "kw_code" }`), and the store is emitted against that
name. There is no writer in the compiler's sources to patch.

**This is the digest's `g_zeta_mode` lesson with the observer moved.** That warning reads: a
global *read* only by emitted code is invisible to every grep of the compiler's own sources, so
deleting it compiles perfectly and dies inside someone else's program. This is its mirror:

> ⭐ **A global WRITTEN only by emitted code is invisible to a patch of its writer.** Instrumenting
> the C setter proves nothing, because the C setter is not on the path. The `fprintf` that does not
> print is the only honest signal, and it looks exactly like "this code is not reached yet".

The filed lesson was stored as a fact about *one symbol* and about *reads*. Both halves were too
narrow. The durable form is about the **boundary**, not the direction and not the symbol: anything
dispatched by string name across the compiler/emitted-code line is unfindable from whichever side
you are standing on.

## The cure is blind to the writer by construction

Consult the value **at exit**, from keyword init, however it got there — never at the write:

```c
static void code_at_exit(int status, void * arg) { (void) arg; if (status == 0 && kw_code != 0) { fflush((FILE *) 0); _exit((int) kw_code); } }
void rt_code_atexit_arm(void) { static int armed = 0; if (!armed) { armed = 1; on_exit(code_at_exit, (void *) 0); } }
```
armed from `rt_kw_seed_defaults()`, the keyword init both modes reach.

- **`on_exit`, not `atexit`** — `on_exit` is handed the status, so the handler fires only on a
  status of 0 and a program that already failed keeps its own rc. Verified: a `&STLIMIT` error with
  `&CODE=5` set still exits 1; a parse error still exits 1.
- **⛔ A second defect, in this cure, caught by grading m4 rather than by reasoning:** `_exit` skips
  stdio, so the first version printed the right exit code and **silently lost the program's output**
  in m4 (rc=3, stdout empty). `fflush` first. **m3 hid it completely.** A cure for a
  dangerous-direction bug that introduces a second dangerous-direction bug is the ordinary case, not
  an unlucky one — and only the both-modes grade caught it.

## Oracle agreement (scrip rc == `sbl -bf` rc on every arm)

| program | rc |
|---|---|
| `&CODE = 3` | 3 |
| `&CODE = 0` | 0 |
| `&CODE = 7` then `&CODE = 0` | 0 — last assignment wins, so the value is read **at exit**, not latched at assignment |
| no `&CODE` | 0 |
| `&CODE = 250` | 250 |

## The instrument refused, and the refusal was right

`util_add_ladder_witness.py` REFUSED rc=2 on a nonzero oracle rc, naming its own gap: it could not
write `ALL.wantrc`, the only place `lib_ladder.sh`'s `wantrc()` reads a declared rc. Minting the CSV
and master rows alone would have graded the witness against the default rc=0 **forever**. It now
writes that sidecar under the same tmp+replace discipline as its other writes; the refusal is
**narrowed, not deleted** — a mixed (non-block) master still refuses, that reader arm having no
sidecar path.

⭐ **A refusal that names the missing capability is worth more than a tool that guesses.** This one
cost ten minutes and saved a permanently mis-graded witness.

## The witness, and why its grading power is entirely the exit code

`ladder__rung23_keyword_and_system_variables_code_exit_value` sets `&CODE` **twice** (9, then 4)
around two `OUTPUT`s, so an implementation that latched the *first* assignment prints byte-identical
stdout and exits 9.

**Proven discriminating rather than asserted:** run against a **pre-cure binary** the witness FAILS
with **stdout already byte-correct** and rc=0 against want 4. Its entire grading power is the exit
code — which is exactly what makes the `ALL.wantrc` declaration load-bearing instead of decorative.

**Honesty proof:** corrupting the declared rc `4 → 5` reds exactly that witness in BOTH modes
(8/10) and leaves its four siblings green; restored and re-graded 10/10.

## Scope, and what is NOT claimed

The cure is in the runtime keyword init, so it is a **shared node**: it flips SNOBOL4 too. Graded
here: Snocone ladder rungs 0..23 **260/260 over 130 witnesses**, FAIL=0 both modes, on SCRIP
`e39d0c761` corpus `52b80e32c`. ⛔ The master and package control arms are **owed from the one
runner** (ONE RUNNER, ONE BOARD, CEO-723) and were **not** run by this seat — no board number here
is mine, and none is claimed.

⛔ Independently confirmed by an instrument this seat did not write: hq_T's
`util_ladder_form_census.py` reads snocone **117 declared / 117 built / 0 unbuilt**, and its global
form-gap count moved **17 → 15** — exactly the two forms closed here. Two derivations of one number,
by two readers that do not share a source.

## Related (tonight, same class, three other seats)

- cfo `9aaf3e912` — the emit site enumerating the wrong population; four instances, one co-signed.
- hq_U `152461d75` — the spine-close cure whose release is attached to **one edge**, so fall-through
  is cured and the edges that bypass the close are not. Its residual is named in `hq_I`'s re-grade.
- hq_S — truncation at a string-dispatch boundary, and `git checkout --` restoring from the **index**
  rather than HEAD.

⭐ **The sentence the four of us converged on tonight, and the one this FINDING is filed under:**
a number with only one reader is a belief with a decimal point on it; the instrument that crosses a
boundary honestly is a **disagreement between two readers that do not share a source**. And its
corollary, which cost this seat its own earlier class sentence: **a class sentence carries the tree
AND THE DATE it was measured on, or it is a claim** — because a cure that fixes half a class silently
rewrites every prose description of the other half.
