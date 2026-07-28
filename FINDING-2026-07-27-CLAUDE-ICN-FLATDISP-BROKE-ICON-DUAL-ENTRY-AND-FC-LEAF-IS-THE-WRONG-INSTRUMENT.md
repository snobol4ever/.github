# FINDING — FLATDISP-1 broke Icon (51 tests); the defect is DUAL-ENTRY, and `fc_leaf_walk` cannot fix it

**Session:** s196 (2026-07-27) · **SCRIP:** `62aaf9ff` → `8d9b8d50`
**Headline:** Icon suite `199/62/32` → `236/25/32`. SNOBOL4 crosscheck UNCHANGED (`221/219`, FAIL 94, DIVERGE=1).
**⚠ READ THIS IF YOU ARE WORKING THE FLATDISP LADDER.** s188 is not SNOBOL4-local.

---

## 1. The regression is real and was invisible

Icon's watermark claimed `250/11/32` at `e63a8b6a`. At HEAD it measured `199/62/32`.
A five-line recursive factorial **segfaulted**. Verified by building both commits clean:

| tree | Icon suite | `fact(5)` |
|---|---|---|
| `e63a8b6a` (Icon watermark) | 250 / 11 / 32 ✓ | `120` |
| `62aaf9ff` (HEAD) | 199 / 62 / 32 | **rc=139** |

Nothing in any doc said Icon had moved. The Icon watermark was accurate *when written* and
silently falsified by a parallel session eight commits later.

⚠ **RULES.md's concurrency note — "safe for CODE (different files)" — is FALSIFIED by this.**
s188 touched `x86_asm.h`, the shared spine. Different *goal files* is not different *code*.

## 2. Bisect: clean builds only

First bisect blamed `9843ee7e`, a commit that adds ONE benchmark script and touches zero
files under `src/`. That was **incremental-`.o` staleness** (checking out backwards leaves
objects newer than sources) — the s126 poisoned-tree lesson, one layer down.

Re-run with `rm -rf out /tmp/si_objs` per step:

| commit | rung | `fact(5)` |
|---|---|---|
| `734b5372` | RTX-4 (s187) | `120` |
| `2410f938` | **FLATDISP-1 (s188)** — *"rsp becomes the frame base by default"* | **SEGV** |

**RULE EARNED: never bisect this tree with incremental builds.** A build-flag or header
change makes `make` skip work and the bisect lands on an innocent commit with total confidence.

## 3. Root cause: ONE body, TWO entries, ONE static displacement

`x86_fb()` returns `"rsp"` unconditionally since s189. Every `FR`/`FRQ` spells
`[rsp + off + op_flat_disp]`, and `op_flat_disp` comes from LOWER's `fc_leaf` registrar
(`emit.cpp:1027`).

```
fc_leaf references per lowerer:   snobol4 9 · icon 0 · prolog 0 · raku 0 · pascal 0
```

Icon compiles **one shared body with two entries**:

```
proc_X_α     sub rsp,kt                 mov rbp,rsp                -> rbp == rsp     (needs D=0)
proc_X_dcα   sub rsp,kt+16  ...         mov rbp,rsp  add rbp,16    -> rbp == rsp+16  (needs D=16)
             jmp proc_X_α_body   <-- SAME BODY
```

⭐ **`fc_leaf_register` is keyed per IR NODE. The body's nodes are shared by both entries.
There is no correct static value. The walk is the WRONG INSTRUMENT** — landing it in
`lower_icon.c` would have burned a session and fixed nothing. Recorded so nobody retries it.

Symptom shape (all measured, HEAD, clean tree):

| program | rc | out | expected |
|---|---|---|---|
| `every i := 1 to 3` (no proc call) | 0 | `1 2 3` | ✓ |
| `f()` no args | 139 | `7` | right value, SEGV on teardown |
| `f(4) -> n+1` | 139 | **`1`** | `5` — param read as null |
| `f(2,3) -> a+b` | 139 | **`0`** | `5` |
| recursive `f(5)` | 139 | — | `120` |

`rt_pl_dc_prep` reads arg pointers from `fb+16`; the stub's `FRQ(16+8i)` emitted
`[rsp+16+8i]` = `[rbp+8i]` — 16 low. That is exactly why parameters arrived null.

## 4. Why the +16 existed, and the fix

`rt.c:1221` — `*(long *)((char *)fb - 16) = rt_value_trail_mark();`
The PL-DC value-trail mark lived 16 bytes **below** fb, which is the entire reason the DC
stub carved `kt+16` and set `rbp = rsp+16`.

**Fix (3 sites), `8d9b8d50`:**
1. `xa_flat.cpp` — DC stub keeps its `kt+16` carve but seeds `rbp = rsp`; the extra 16 moves
   **above** the frame at `[rbp+kt]`. Both entries now agree, so the shared body is correct.
2. `rt.c` — vtmark writes to `fb + region_bytes + 32` (== `fb+kt`).
3. `xa_flat.cpp` shims (DC-only) — reclaim the 16 (`add rsp,16`) before the retaddr push so
   the call stays balanced, **and restore the caller's `rbp`**.

⭐ (3) is its own bug and was masked: a depth-static graph never saves rbp on the wire path
(`emit_jmp_pin_rbp()` gate, s194), so the shared epilogue never restores it — but the DC
entry clobbers it. That was the `rc=134` *"stack smashing detected"*: the emitted code rides
the C stack under `ZC_PORT_FORTH`, so a destroyed caller rbp takes out a canary.

**FALSIFIED EN ROUTE — do not retry:** growing the wire header 32→48 to reserve the vtmark
slot. It works (Icon 236) but costs SNOBOL4 exactly 2 tests in each mode (221/219 → 219/217),
because it shifts *every* frame in *every* language. Measured, not assumed — baseline was
re-measured at unmodified HEAD, not taken from the s195 commit message. The DC-only
above-frame placement gets the same Icon number at zero SNOBOL4 cost. **Gating on
`g_flat_dc_np` does NOT work either:** `emit_jmp_entry_for_proc` (scrip.c:883) runs *before*
the driver arms it (:884) and clears it internally.

## 5. Residual: 14 tests, ONE class

`suspend_gen`, `suspend_gen_compose`, `suspend_gen_filter`, `suspend_return`, `jcon_genqueen`,
`subscript_genproc`, `jcon_coerce/htprep/level/meander/mffsol/recogn/wordcnt`, `scan_alt`.

All **suspended generators**. Those graphs pin rbp by design (`flat_gen` is a load-bearing
conjunct of `emit_jmp_pin_rbp()` precisely because the suspend protocol reads pinned rbp), so
on resume `rsp != frame base` and the offset is **dynamic**. No static `op_flat_disp` can work
— the same wall the FLATDISP ladder hit at s192.

**Next rung:** gate the frame base on `flat_gen` — `x86_fb()`/`FR`/`FRQ`/`x86_r12_modrm` return
rbp for generator graphs (BOTH MEDIA per R10). ⛔ That is `x86_asm.h`, which the SNOBOL4
session owns and which RULES already flags as not concurrency-safe. **Lon's call, not a
session's.**

## 6. Prolog / Raku / Pascal

Prolog has 0 `fc_leaf` sites too, but its failure (`rc=134` on a recursion probe) is
**pre-existing** — identical at `734b5372` and HEAD, so NOT a FLATDISP regression. Raku and
Pascal unmeasured. The general statement: *any* graph whose frame base is not rsp needs a
displacement nothing supplies. Icon is the measured instance.

## 7. Stale docs corrected by this session

- `ARCH-ICON.md` register contract still says `x86_fb()` = **RBP**. It has been **RSP** since
  s189 (`x86_asm.h:360`, "s189 deleted the alternative").
- `GOAL-ICON-BB.md` watermark `250/11/32` was true at `e63a8b6a` and false at HEAD for eight
  commits. A watermark naming a commit is only a claim about *that* commit.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
