# HANDOFF — 2026-06-13 · Sonnet 4.6 · PROLOG BB m4 typetest-lea + x86 bomb backstop

## Watermark
SCRIP `cda87e5` · .github `(this commit)` (both green).
**m2 114/115 · m3 91/115 · m4 75/115** (ratchet floor: m3≥91, m4≥75).

## Gates
GATE-1 5/5/5 ✓ · GATE-3 m2=114, m3=91, m4=**75** (was 70, +5 this session).
SNOBOL4 7/7/7 ✓ · Icon 12/10/10 ✓ · Raku 10/7 (baseline, invariant) ✓.

---

## What was done

### 1 · `bb_type_test.cpp` — silent-drop `lea rdi` in TEXT (m4) arm (ROOT CAUSE + FIX)

**Bug.** `bb_type_test_str`'s TEXT arm emitted:
```cpp
x86("lea", "rdi", emit_fmt("[rip + %s]", op_lbl))
```
The `x86_asm.h` classifier doesn't recognize `[rip + <label>]` as a sealed-RIP
operand. It falls through to `XK_MEMIND` (base extracted as the first 7 chars →
`"rip + ."`), which hits **no arm** in the `lea` dispatch and returns `std::string()`.
The `lea rdi` instruction **silently vanishes** from the emitted asm.

Result: `rt_type_test_term(fn, t0)` received a garbage `rdi` (stale register value),
`type_test_common` strcmp'd against junk, every compound-arg typetest returned `no`.

**Fix.** Added one-line file-local helper `tt_rip_lea` (identical idiom to `blbl_lea`
in `bb_resolve.cpp`) using the sealed `"[rip + __]"` form with (ptr, label) args,
which classifies as `XK_RIPSEAL` → dispatches correctly to `x86_load_ro`:
```cpp
static std::string tt_rip_lea(const char *dst, const char *raw, const char *lbl)
    { return x86("lea", dst, "[rip + __]", (uint64_t)(uintptr_t)(raw?raw:""), lbl); }
```
Three sites in the TEXT arm converted: lines 63, 76, 79 (compound-arg fn, scalar-arg
fn, scalar-arg atom-value). BINARY arm (hand-encoded `bytes()` path) was already
correct — untouched.

**Gain.** rung40 ×4 (compound/callable/ground/is_list) + rung09 ×1 (var/nonvar on
compound term) → m4 **+5**: 70 → 75.

Note: this is the *exact* silent-lea hazard the C-LABEL handoff flagged as "worth a
gate". The BINARY arm had its own `mov rdi, fn` hand-encoding that worked; only
TEXT was broken.

### 2 · `x86_asm.h` — bomb backstop on unsealed-RIP `lea` operands

**Scope check** (done before touching the spine): grep found **zero** remaining
unsealed `emit_fmt("[rip + ...]")` sites in any template — `bb_type_test.cpp` was
the lone outlier, now fixed. So no other template needs the recognizer.

**What was added.** One surgical arm in the `lea` dispatch, after all five working arms:
```cpp
if (b.txt && strstr(b.txt, "rip"))
    return x86_bomb("lea: unsealed [rip + label] operand — use [rip + __] sealed form …");
```
Tests `b.txt` (raw operand string, always populated on the struct) for "rip". Fires
only on the reintroduction of the unsealed-RIP idiom; every legitimate `lea` and every
other fall-through remain untouched. Required forward-declaring `x86_bomb` before
the `x86()` dispatch function (line 513).

**Proof.** With the bad idiom re-injected into `bb_type_test.cpp`, the emitted asm
shows `call rt_bomb@PLT` + `ud2` precisely where the `lea rdi` used to silently
vanish. With the good code, nothing trips across any language.

---

## What was NOT done (left for next session)

### C-FRAME (rung06 lists — `[a,b,c,d]|` → stops after first write)
GOAL-PROLOG-BB.md flags this as **"FIX (decision pending Lon)"** between
option A and option B. Deliberately not touched — Lon must choose the approach.

### rung11 findall m4 cluster (5 failures)
- 4 of 5: empty output — runtime "unhandled kind 64 (IR_GCONJ)" on the findall
  result-list construction path. The GOAL already flags this as known-hard.
- 1 of 5 (`findall_template`): `.S0` linker error — **different** from the silent-lea
  class. This is a missing strtab *definition* (the reference is present; the `.quad` /
  `.string` for `.S0` was never emitted for this program shape). Tentative: the
  `gzq0_g0_α` function emits a `[rip + .S0]` reference for a pair-template atom but
  the strtab emission for that shape is gated out in the TEXT medium path.

### m3 failures (24, all in named buckets — unchanged from session start)
B3 retract ×5 · B4 abolish ×5 · A6 nb/aggregate ×4 · B2 catch/throw ×5 · B5 DCG ×4 ·
rung22 write_canonical_ops ×1.

---

## Key architectural finding (reusable for future reviewers)

**The correct idiom for RIP-relative string loads in x86_asm.h:**
```cpp
// WRONG — classifies as XK_MEMIND, hits no lea arm, returns ""
x86("lea", "rdi", emit_fmt("[rip + %s]", label_str))

// CORRECT — classifies as XK_RIPSEAL, routes to x86_load_ro
x86("lea", "rdi", "[rip + __]", (uint64_t)(uintptr_t)raw_ptr, label_str)
```
Every template in the codebase already uses the correct form except `bb_type_test.cpp`
(now fixed). The new bomb backstop in `x86_asm.h` makes any reintroduction of the
wrong form abort loudly at runtime instead of silently producing wrong answers.

**Why the C-LABEL handoff's Raku-BB `lea rdi` fix *worked* while the
`bb_type_test.cpp` one *didn't*:** The Raku-BB fix changed the call in
`bb_call_fn.cpp` to use the byname directive form (which internally uses sealed
`[rip + __]`). The `bb_type_test.cpp` author presumably wrote the TEXT arm by
analogy with what the asm *should look like* (`[rip + .S0]`) rather than by analogy
with sibling templates (`[rip + __]` + args). The bomb backstop closes that gap.
