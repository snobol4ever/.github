# ARCH-X86-ASM-ENCODER — design rationale recovered from `x86_asm.h`

**What this is.** `src/templates/x86/x86_asm.h` is the sole `x86(...)` encoder (RULES.md § Emission
discipline): every x86 instruction in the project, TEXT and BINARY alike, is produced inside it. On
**2026-08-20** commit `e25a5daf` stripped 6,919 comments tree-wide to enforce the C style rule, and this file
lost **186 comment blocks** — a mean of **416 characters each**, with only **2** shorter than 60 characters.
That length profile is the whole reason this document exists: the file's comments were not decoration, they
were the only record of *why* the encoder emits the bytes it emits.

Recovered and relocated by **hq_P, 2026-09-11**, row `rationale-x86-asm-h`, per `RATIONALE-INDEX.md`.
⛔ **The comments are NOT going back into the source** — RULES.md's one-comment-form rule stands. Grep the
symbol in `RATIONALE-INDEX.md` and it points here.

⭐ **Everything below was re-verified against the LIVE tree (SCRIP `909c1b574`, file now at
`src/templates/x86/x86_asm.h`, 2171 lines) before being written down** — the recovered text says what the
author believed in August; the ✅/⛔ notes say what is true today. Where the two disagree, today wins, and the
disagreement is itself recorded rather than quietly resolved.

---

## §1 THE RTCC REGISTER-BLOCK CALL CONVENTION (tags `RC-4`, `RC-5`)

The densest cluster in the file — **17 of the 186 recovered blocks** carry an `RC-4`/`RC-5` tag, which is the
criterion by which it was picked for relocation first (next densest: `ZB-FC-0` and `HZ-1` at 4 each).

### The problem it solves

Templates keep VM state in registers. A C runtime call may clobber any of them. RTCC ("runtime calling
convention") spills a claimed register set to a fixed static block around every C call, so a template's
register wires survive the crossing.

### The block and its slot offsets

`rtccb` is a static 9-slot array, 8 bytes each. The slot map is fixed and is duplicated by *arithmetic* in
both mediums, so it is written down once here:

| reg | RAX | RCX | RDX | RSI | RDI | R8 | R9 | R10 | R11 |
|---|---|---|---|---|---|---|---|---|---|
| offset | 0 | 8 | 16 | 24 | 32 | 40 | 48 | 56 | 64 |

✅ Verified live: `RTCC_SLOT_R8 5` / `RTCC_SLOT_R9 6` in `src/runtime/rtx/rtcc.h:18-19` (slot *index*; the
byte offsets above are what the emitted instructions carry — `rtccb+40`, `rtccb+48`, …).

### Writeback / reload order, and why R11 is restored last

- **WRITEBACK** — `push r11` (saves it to stack), `movabs r11, block`, store the other eight through `r11`,
  then `pop [r11+64]` to drop old R11 into its own slot. Net: 1 push + 1 movabs + 8 stores.
- **RELOAD** — `movabs r11, block`, restore the other eight through `r11`, restore **R11 last** (slot 64).
  ⭐ **R11 is the block base during its own reload**, so restoring it early would destroy the pointer the
  remaining restores depend on. That ordering constraint is load-bearing in the BINARY path.
- ⭐ **The TEXT path does not have that constraint and says so**: each slot is addressed off `rip`
  (`qword ptr [rip + rtccb+56]`), R11 is never the base, so the "R11 last" rule simply does not apply there.
  Two mediums, one convention, **different invariants** — which is exactly the kind of asymmetry that reads as
  a bug to anyone who only learned the BINARY rule.
- **Call stubs** — BINARY: `movabs r10, ptr; call r10` (R10 is already written back, so it is free scratch).
  TEXT: `call sym@PLT`, gas handles indirection. ⛔ Because *we* clobber R10 in the BINARY stub regardless of
  what the callee does, R10 is forced into the mask in mode 3 unconditionally.

### ⛔ THE RETURN-BEFORE-RELOAD LAW (`RC-4`, design of record)

For `DESCR_t`-returning calls the caller captures **RAX:RDX into the destination frame slot BEFORE the
reload**. Otherwise the reload overwrites RAX:RDX with block values — which are *stale VM globals*, not the
return value. `x86_rtcc_call_descr` exists solely to handle this; `x86_rtcc_call` is the void/int/ptr form
where RAX need not survive.

⭐ **The failure this law prevents is silent and type-correct**: the callee returns fine, the reload succeeds,
and the caller reads a well-formed `DESCR_t` that is simply the wrong one.

### `RC-4` PARTIAL RELOAD — the tier split

Only the **SCRATCH TIER** `{R8, R9, R10, R11}` is restored. The **ARG TIER** `{RAX, RCX, RDX, RSI, RDI}`
reload was **deferred to RC-5** for a reason worth keeping: until a VM global is actually assigned to those
slots, the block values are **zero (BSS)**, and restoring zero would destroy the call's return value in
RAX/RDX. Consequence, stated as a guarantee: templates reading RAX/RDX after a call still see the return
value.

⭐ **A reload that is "obviously symmetric" with the writeback would have been wrong here.** The asymmetry is
the correctness argument, not an unfinished edge.

### CLASS N — the per-callee decline

`x86_rtcc_clob(sym)` returns the mask a given callee can actually disturb; **mask 0 means the whole dance is
dead weight** and the veneer falls through to a plain `x86_call_ro`. ✅ Live at `:322-324`, now composed with
`x86_rtcc_live_mask()`, which additionally drops R9 from the mask when `RTCC_GLOBAL_R9_GVA` is on and
`gva_count() == 0` — i.e. when no global is in the GVA plane, the R9 machinery is skipped entirely.

⛔ **This is a per-CALLEE decline, not a per-op filter** — it keys on what a named C function can clobber, so
it does not collide with the no-per-op-filter rule (RULES.md); every member of a BB family is treated alike.

### ⛔⭐ H2 — THE R9/GVA SLOT IS NOT WRITTEN BACK (s8, 2026-08-10) — **LIVE TODAY**

The sharpest item in the file, and the one whose live code is unreadable without it.

`rtcc_init.c` seeds slot 6 (R9) with `RT_GVA_VA` **once**, and documents it as a **BLOCK-CANONICAL
EXCEPTION** requiring *"no companion writes anywhere"*. The writeback **was** a companion write: it stored R9
on **every** crossing. So the documented exception held only for as long as nothing ever clobbered R9.
Something eventually did — `bb_define`'s `movzx r9, cl` — and the clobbered value entered the canonical slot,
after which the reload **spread it**: `RT_GVA_VA` dead process-wide, every `[r9 + k*16]` near-null.
**PROVEN: `AB=1 RTCC=1` fibonacci SIGSEGV.**

**The cure is to skip the store**, which makes the documented exception *true*: R9 becomes a read-only cache
of a constant, the reload always restores the pristine seed, and a template clobber of R9 becomes
**SELF-HEALING at the next crossing** instead of fatal.

✅ **Verified live in both mediums** — the guard is `(m & RTCC_C_R9) && !RTCC_GLOBAL_R9_GVA` at
`x86_asm.h:357` (BINARY) and `:376` (TEXT), and the seed is
`rtcc_init.c:9` — `if (RTCC_GLOBAL_R9_GVA) rtccb[RTCC_SLOT_R9] = (uint64_t)(uintptr_t)(void *)RT_GVA_VA;`.

⭐ **THE TRANSFERABLE SHAPE — A DOCUMENTED EXCEPTION IS NOT AN ENFORCED ONE.** The comment in `rtcc_init.c`
correctly stated the invariant ("no companion writes anywhere") and the code three files away violated it from
the day it was written. Nothing connected the two, so the invariant was true only by luck, and the luck ran
out at a `movzx` in an unrelated template. ⛔ **An invariant that names a global condition must be enforced
where the condition can be broken, not asserted where it is convenient to state.**

### `RC-5-GVA` — `GVARQ`, the GVA-base displacement form

When `RTCC_GLOBAL_R9_GVA=1` and `g_rtcc_on=1`, R9 holds `RT_GVA_VA`, so a global at GVA slot `k` word `w` is
`qword ptr [r9 + (k*16 + w)]`. For `k ≤ 7` the offset is ≤ 120 < 128, so it encodes as **disp8: 4 bytes,
against 7 for the `ABSQ` absolute form**. Gate off → the caller uses `ABSQ(RT_GVA_VA + k*16 + w)`, which is
byte-identical to pre-RTCC.

✅ Live, and still genuinely two-armed: `(g_rtcc_on && RTCC_GLOBAL_R9_GVA) ? GVARQ(...) : ABSQ(...)` appears
across `bb_assign_global.cpp`, `bb_var_global.cpp`, `bb_match_defer.cpp`, `bb_rev_assign_global.cpp`,
`bb_binop_gvar_arith.cpp`, `bb_call_proc_staged.cpp`.

### `RC-5-ANCHOR` — `test r8, r8`

Replaces a 3-instruction `[rip + rt_anchor_g@GOTPCREL]` load + deref + cmp with a single **3-byte**
`test r8, r8` (`4D 85 C0`). ZF semantics are identical — ZF=1 iff anchor==0 (unanchored) — so the following
`jne` is unchanged. Killswitch `RTCC_GLOBAL_R8_ANCHOR=0` re-emits the original sequence byte-identically.
✅ Live at `x86_asm.h:1544` (`rtcc_anchor_cmp`).

### ⛔⭐ THE `s11` DEFECT — TWO GRADED RUNGS WERE VOIDED BY A DUPLICATED MACRO

`RTCC_SLOT_R8/R9`, `RTCC_GLOBAL_R8_ANCHOR`, `RTCC_GLOBAL_R9_GVA` and `RTCC_GVA_REG` were **defined in both**
`x86_asm.h` **and** `rtx/rtcc.h`, **both unguarded**, so no `-D` could override either — and gcc's
`"redefined"` warning was **eaten by the tree-wide `-w`**.

The cost was not a crash. It was measurement:

> **`RC-5-GVA` was RETAINED on a 1.036x "rail" and `RC-5-ANCHOR` was REVERTED on a 1.000x "rail", when in
> both cases the two arms were THE SAME BINARY.**

⭐ **THIS IS THE KILLSWITCH-CONTROL-ARM RULE'S ORIGIN STORY, AND IT IS WHY THE RULE IS WRITTEN THE WAY IT IS.**
Every instrument behaved: the build succeeded, the killswitch flipped, both arms ran, both produced numbers,
and the numbers *differed* — by exactly the noise you would expect from two runs of one binary. ⛔ **A
killswitch that does not reach the emitter produces a perfect A/B with no B**, and nothing in the output says
so. A perf claim's control arm must be proven to *change the emitted bytes*, not merely to flip a flag.

✅ **The cure held.** Verified today: `RTCC_GLOBAL_R8_ANCHOR` / `RTCC_GLOBAL_R9_GVA` are `#ifndef`-guarded in
`rtx/rtcc.h:22-26` **only**; `x86_asm.h` merely *reads* them. One source of truth, and a `-D` now reaches the
emitter — which is what makes those two rungs re-gradeable at all. Values were verified identical across both
copies before the duplicates were deleted.

### ONE MODE (`s180`, Lon 2026-08-20)

The `g_rtcc_on` off-arm was deleted from the veneer: protection around C calls is **unconditional**, and
CLASS N is the only exemption. ✅ Verified: `g_rtcc_on` survives in `x86_asm.h` as a bare `extern` declaration
at `:12` and gates nothing there. ⚠️ **But it is still a live gate in the GVA-addressing templates** (the
`GVARQ`/`ABSQ` choice above) — so "ONE MODE" is true of the **veneer**, and *not* of GVA addressing. The
veneer's own arming now runs through `SCRIP_RTCC_VENEER` / `x86_rtcc_veneer_mask()` (`:316-320`).

### ⛔ Symbols in the recovered text that NO LONGER EXIST

`x86_rtcc_writeback` and `x86_rtcc_reload` — the "FULL 9-GPR block I/O helpers" the recovered header names —
have **zero occurrences** in the live tree. The surviving forms are the medium-split
`x86_rtcc_wb_bin` / `x86_rtcc_rl_bin` (BINARY) and `x86_rtcc_wb_text` / `x86_rtcc_rl_text` (TEXT).
**The convention above is still accurate; only those two names are dead.** Recorded rather than silently
corrected, because a reader meeting the old names in an older FINDING needs to know where they went.

---

## §2 THE TAB RECORD — `x86_tabs_on` (Lon 2026-08-13 s62b)

Lon, verbatim: *"would it not be best to have all x86_\*() and x\*() use TAB character delineated four columns
with NO padding, and do formatting later on output like your second pass is doing — strings would take LESS
MEMORY"*.

Every `x86_*()` encoder emits its line as **TAB-DELIMITED FIELDS** — `label \t opcode \t operands` — carrying
**zero padding**; the sink splits on TAB and applies the columns **once**, on output.

⭐ **The win is not the memory, it is that field occupancy becomes EXPLICIT** — which deletes the entire
whitespace-sniffing layer: no first-token scan, no `':'` label detection, and no `rep`/`lock` prefix special
case, because a prefixed mnemonic is simply *what the opcode field contains*.

⛔ **THE ONE TRAP THE DESIGN NAMED FOR ITSELF:** a label-only line and the `#@` note marker become records
with **empty fields** rather than special cases — so `x86_rec_kind` keys off **OCCUPANCY** (is the opcode
field empty?) and **never off text**. ✅ Live at `:1407`:
`if (r.marg) return r.al ? 4 : 0; if (!r.ol) return 1; return (r.op[0] == 'j') ? 3 : 2;`

**LEGACY LINES SURVIVE BY CONSTRUCTION:** a record with **no TAB** — the raw producers in `emit.cpp` and the
`xa_*.cpp` templates that do not speak `x86()` — falls through to the whitespace parse. ⭐ **This is ADDITIVE,
not a cutover**, which is why it could land without touching every producer in the tree.

**Tabs cannot collide with content:** `x86_asm_str_escape` and `emit_str.cpp` both render a literal tab as the
two characters `\` `t`, so no raw tab ever reaches a `.string` operand.

**KILLSWITCH `SCRIP_ASM_TABS=0`** restores the space-delimited producer form, and the rendered `.s` is
**byte-identical either way** — proven across the demo corpus by `scripts/test_gate_asm_tabs_identity.sh`.
✅ Both verified live: the getenv at `:22`, the gate script present in `scripts/`.

⭐ **Note the contrast with `s11` one section above** — this killswitch ships with a gate that proves the two
arms agree on output. That is the difference between a killswitch and a decoration, and the two live in the
same file.

---

## §3 What was NOT relocated

This document covers the `RC-4`/`RC-5` cluster and the TAB RECORD: **~20 of 186 recovered blocks**, chosen by
design-tag density. The remainder is real and still unrelocated — the next densest tags are `ZB-FC-0` (4),
`HZ-1` (4), `PL-DC` (3), `REG-7` (3), then a long tail including `ZOP-1`, `FLATDISP-8`, `OBJ-NOTE ON-1/2/3`,
`ALIGN-INV-0`, `GLUE-3/4`, `CALL-SYNC` and `ICN-SCAN`.

⭐ Some of that tail is unusually good — the `OBJ-NOTE` accessors (`ZRESN`, `ZOPAN`, `ZOPN`, `HKN`) carry a
Lon ruling *and* a stated naming law (*name the object AT THAT INSTRUCTION*) *and* the reason each is an
accessor rather than 39 inlined literals. Per the row-factory rule it is a separate row, not a bigger sitting.

⚠️ **The recovery method is reproducible**: `git show e25a5daf^:src/templates/x86_asm.h` vs
`git show e25a5daf:` — note the **old** path, before the `src/templates/{bb,x86,xa}` split. The extraction
script was scratch and is not checked in (same as the parent row); it is ~40 lines of Python that walks the
BEFORE file collecting `/* … */` runs with the next code line as anchor.
