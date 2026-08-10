# FINDING 2026-08-10c — SN4 / RTX-FUNC

**The name-alias bug was an ENTRY NULL in α, not a RESULT READ in β. Fixed and gated.
The SCRIP_AB default-on flip is blocked by a SECOND, independent defect: expression-position
DEFINE never gets an activation block. Root-caused, witnessed, NOT fixed — it is entangled
with runtime-DEFINE binding and needs Lon to route.**

Seat: Claude Opus. SCRIP `3a9ccee`. corpus `19a5bf9`. Both LOCAL until the push is confirmed.

---

## 1. The inherited conviction was wrong in both halves

The prior cursor recorded the defect as: *"the AB result read takes the WRONG GVA SLOT and the
error SCALES WITH nformals (2 formals → returns formal 1's actual; 3 formals → null)."* That
located it in **β**, the return path, and described a **slot-shift**. Both are false.

**What it actually is:** the entry null loop in `bb_func_activate.cpp` nulls save-set slot 0 (the
result cell) unconditionally. When the function name is also a formal, slot 0 and that formal are
ONE name sharing ONE GVA cell, so the null **destroys the actual the call site just installed**.
The site is **α**, entry, and the read is fine.

**Why the wrong reading was reachable, and it is instructive:** the standing witness
`ab_name_alias.sno` uses `mx = LT(mx,x) x` — a guard that *reads the formals*. With `mx` nulled,
`LT(mx,x)` becomes `LT(0,2)`, which **SUCCEEDS** where `LT(9,2)` fails. The assignment therefore
fires and returns `x` — formal 1's actual — perfectly impersonating a slot shift. At 3 formals the
guard `LT(1,0)` does not read the formals, so nothing fires and the result is null. Two different
wrong answers from one cause, and the pair looks exactly like an index scaling with arity.

**The discriminator that killed it** (cheapest experiment, run before reading any code): an arity
sweep whose guard does NOT read the formals, `f = LT(1,0) 0`. Under AB=1 that returns **null at
every arity** — 1, 2, 3, 4 formals, with and without locals, and when the fname is aliased to a
NON-zero formal slot. No scaling. One signature.

**The conviction** was then taken directly, by observing the formal **at entry**, before any return
logic can run:

```
        DEFINE('t2(t2,x)')
t2      OUTPUT = 'inside t2: t2=[' t2 '] x=[' x ']'   :(RETURN)

  oracle : inside t2: t2=[21] x=[22]
  AB=1   : inside t2: t2=[]   x=[22]      <- slot 0 destroyed, slot 1 intact
```

`x` installs correctly; only the aliased slot is gone; the non-aliased control is perfect. That is
an entry defect, and no examination of β could have produced it.

> **Method note for the next seat.** The wrong conviction did not come from sloppiness — it came
> from reading a root cause off ONE probe whose guard happened to interact with the bug. When a
> defect's symptom *varies with a parameter*, suspect the probe before believing the scaling.
> A second probe shape costs a minute and it is what separated these.

## 2. Manual authority (Ch.8 + Ch.19 DEFINE)

The result is *"a variable with the same name as the function"*. When that name is also a formal
they are the same variable: the actual assigned at call time IS its value at entry, and IS the
result when no assignment fires. Oracle confirms — `a1(11)` returns `11`. This is not a corner
case: it is SPITBOL's own accumulator idiom, `DEFINE('max(max,x)')`, `DEFINE('abs(abs)')`,
`DEFINE('gcd(gcd,b)r')`, used throughout `corpus/lib/math.sno`.

## 3. The fix

`bb_func_activate.cpp`, entry null loop. Detect the collision **by GVA index** — names are resolved
to cells at this point, so identity is an integer compare, not a string one — and skip the null for
slot 0 only. Formals were already skipped; locals still get nulled; **restore is untouched**, since
the spill loop above still saves the caller's OUTER value out of that same cell.

**GATE — m3 and m4, AB=1 and AB=0, every line oracle-exact:**

| witness | result |
|---|---|
| `probe/ab_name_alias.sno` (standing witness) | IDENTICAL, both media, both arms |
| `crosscheck/library/test_math.sno` | IDENTICAL to `.ref`, both arms |
| arity sweep 1–4 formals, aliased / non / with locals / aliased-to-formal-1 | IDENTICAL to oracle |
| outer-value restore, aliased and non-aliased | IDENTICAL to oracle |
| recursive accumulator `ac(0,4)` → 10 | IDENTICAL to oracle |

## 4. ⛔ The flip is BLOCKED — expression-position DEFINE gets no activation block

`DIFFER(DEFINE('f(n)','entry'))` is hoist-registered by `sno_prescan_expr`
(`lower_snobol4.c` ~:2311) so the LEGACY path finds it, but the AB activation block + bind are
minted ONLY on the statement path (~:2048–2070, gated on `sno_stmt_define` finding a DEFINE in
**subject** position). `fn_cell$<FN>` is never wired for such a definition.

* **NEW name** → `fn_cell` holds `rt_ab_undef_fn_stub` → *"Undefined function called"*
* **REDEFINED name** → `fn_cell` holds the **PREVIOUS** body → old body entered under the new
  prototype's frame/save-set shape → **SIGSEGV**. This is 1011's crash.

Witness minted: `corpus/probe/ab_expr_define.sno` + `.ref`, two-sided (AB=0 oracle-exact, AB=1
diverges). N=5 both arms: `1011_func_redefine` AB=0 **PPPPP**, AB=1 **F(139)×5** — a hard,
deterministic regression. **On this program AB=1 is strictly WORSE than AB=0, so the flip would
be a regression and must not happen until this closes.**

**Do not "fix" this by minting a block at the prescan site.** The call-site guard at
`bb_call_proc_staged.cpp:242` is `ab_n > 0` — *the program has ANY block* — not *this function has
a valid one*. And in 1011 `myfunc` **does** have a block; it is just built from the FIRST
prototype while the live binding is the SECOND. Per-fname presence is therefore not sufficient
either; the block must match the LIVE definition.

**And that runs straight into a deeper divergence, found this seat and present in BOTH arms:**

```
        DEFINE('fe(n)')   / fe = n * 2
        OUTPUT = fe(3)                      oracle 6    SCRIP 103   <-- BOTH arms
        DEFINE('fe(n)','fe2') / fe2  fe = n + 100
        OUTPUT = fe(3)                      oracle 103  SCRIP 103
```

SCRIP binds redefinitions at **compile time** (last-define-wins, the standing deviation noted at
`lower_snobol4.c:2312`); SPITBOL executes DEFINE at **runtime**. This is pre-existing, equally
present at the current default, and NOT caused by anything this seat did — but it means the
correct fix for §4 is entangled with runtime DEFINE, already flagged pending at
`lower_snobol4.c:740`. **Routing decision for Lon, not a session-end patch to the file every call
site depends on.**

## 5. ⚠ Two measurement traps, both live

**(a) This container cannot reproduce the recorded absolute watermark.**
`corpus/snobol4corpus` is a **dangling symlink** → `/home/claude/snobol4corpus`, which is not in
any of the three repos. Measured here: AB=0 m3 253/64, m4 248/68/1 — far below the file's
282/35 · 276/40/1. **Absolute counts from this seat are not comparable to the file's watermark**
and none are recorded as such. Everything above is an AB=1-vs-AB=0 **delta within one
environment**, which is the correct control regardless. Next seat: resolve the symlink before
quoting any absolute number.

**(b) A sweep delta at N=1 is not evidence on DEFINE-bearing programs.**
The sweep showed `097_define_capture_return_d2probe` failing at AB=0 and passing at AB=1 in both
modes — an apparent AB=1 win. At N=5 it is **AB=0 F×5, AB=1 F F P F F**. The pass was a lucky
draw. Note the non-determinism here is in the **AB=1** arm; RTX-FUNC-6 recorded it in the LEGACY
arm. Both arms are affected. RTX-FUNC-7's N≥4 rule is not optional and it applied to this seat's
own headline delta.

`132_pat_fence_eps_recur_shallow` likewise: SEGVs in BOTH arms on direct run; its m4 "fix" was a
SKIP/timeout reclassification (m4 SKIP 1→2). Not a win.

**Net honest delta of this seat's change: no program regressed; `test_math` moved to green under
AB=1; no genuine AB=1 win over legacy; `1011_func_redefine` remains a hard AB=1-only regression.**

## 6. Left for the next seat

1. **§4 — the flip blocker.** Route the runtime-DEFINE question first; the block-minting fix is
   downstream of it. Witness is already the gate.
2. **The `ab_n > 0` guard** at `bb_call_proc_staged.cpp:242` is too coarse independently of §4 —
   it flips call sites for functions that have no valid block.
3. **Compile-time vs runtime DEFINE binding** (§4 code block) — pre-existing, both arms, no rung
   owns it.
4. **The dangling `snobol4corpus` symlink** — blocks absolute watermark comparison for everyone.
5. **SCRIP accepts a duplicate label** where SPITBOL raises `ERROR 217 — syntax error: duplicate
   label`. Noticed incidentally when a malformed probe was rejected by the oracle and accepted by
   SCRIP. Front-end, unowned, not investigated.
6. RTX-FUNC-5 (measure) still unrun; RTX-FUNC-1/2's gate re-scope still owed.
