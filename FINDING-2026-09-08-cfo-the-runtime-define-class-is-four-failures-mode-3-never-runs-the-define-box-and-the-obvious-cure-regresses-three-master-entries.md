# FINDING — the runtime DEFINE class is FOUR failures across two modes, mode 3 never runs the DEFINE box at all, and the obvious cure regresses three master entries

**cfo · 2026-09-08 · routed by ceo from hq_P's `flip-gimpel-redefine-driver`**
**Trees:** SCRIP `397b3bd22` (clean — everything below reproduces on origin/main; my candidate cure is NOT landed, it is ablated here and backed out) · corpus `6c94504c0` · `RT_OPT=-O0`, incremental `make`.
**Builds on:** `FINDING-2026-09-09-hq_P-runtime-define-binds-early-and-crashes-when-it-redefines.md`. hq_P's two witnesses are confirmed verbatim; this adds a third symptom, the mechanism, and a measured ablation of the fix that looks right.

## 1. Both of hq_P's witnesses reproduce, and there is a THIRD symptom they did not name

Using hq_P's `wB` (top-level redefine, call before and after) and `wA` (redefine from inside a function):

| witness | mode | SPITBOL `sbl -bf` | SCRIP |
|---|---|---|---|
| wB | m3 | `orig(x)` / `new(x)` | `new(x)` / `new(x)` |
| wB | m4 | `orig(x)` / `new(x)` | `new(x)` / `new(x)` |
| wA | m3 | `orig(x)` / `new(x)` | `orig(x)` then **SIGSEGV** |
| wA | **m4** | `orig(x)` / `new(x)` | **`orig(x)` / `orig(x)`** ⛔ |

⛔ **wA in mode 4 is a third symptom and it is the quiet one squared:** the runtime redefinition performed
inside a function is **silently ignored** — no crash, no diagnostic, the old body just keeps running. A seat
grading only mode 3 sees a crash and fixes the crash; mode 4 will still be wrong and will still say nothing.
**Grade this class on four cells, not two.**

## 2. The crash is a jump to address 0, and the runtime asks for it explicitly

`gdb` on wA m3: `Program received signal SIGSEGV` at `0x0000000000000000`. `rt_sno_runtime_define()`
(`src/runtime/rt/rt.c:609`) is the whole story:

```c
p->fn = (bb_box_fn)0; ... p->redefined = 1; ...
{ ... snprintf(cn, sizeof cn, "alpha$%s", name); void **cell = ...; if (cell) *cell = (void *)0; }
```

It **nulls the function pointer and zeroes the `alpha$<name>` cell, and never installs the new entry** —
because its caller `_DEFINE_` (`src/runtime/core/core.c`) has the entry label in hand as `entry` and
**does not pass it**. The next call jumps through the cell it just zeroed.

## 3. The static half: the body cell is baked to the LAST definition, and the IR already knew better

Mode 4 assembly for wB:

```
body_cell$F:  .quad  LBL__F2          # static initialiser, before any DEFINE has run
```

and **both** DEFINE sites emit `lea rax, [rip + LBL__F2]` into that cell — the first statement seals the
second statement's body. `F_α` dispatches by `jmp` through that cell, so the design is right and the value
is wrong.

⭐ **The IR is already correct and nobody reads it.** `--dump-ir` on wB:

```
2   3@  29@  DEFINE  [30]        30  LIT_NAME  "F"
14  15@ 26@  DEFINE  [27]        27  LIT_NAME  "F2"
```

Each bind node carries its own entry, and there is even an accessor for it —
`ir_define_bind_entry()` at `src/ir/IR.h:197`. The dedup is in **`src/driver/scrip.c`**, in the `dentry`
construction: for each bind node it searches `s2->proc_table` **by FUNCTION NAME**, and that table holds
one row per name, so every DEFINE of `F` resolves to whatever the last one recorded.

## 4. The two mediums disagree, in one line

`src/templates/bb/bb_define.cpp:424`:

```cpp
+ (_.lbl_t0 ? x86("lea", "r9", "[rip + __]", (uint64_t)(uintptr_t)_fn, blbl.c_str()) : ...)
```

The **text** medium uses `blbl` — the statement's own label. The **binary** medium uses `_fn` —
`rt_define_query()`'s per-NAME answer, i.e. the last definition. Per the rule that every emitting function
must be correct for both mediums, this line is a defect on its own terms, independent of the cure chosen.

## 5. ⭐ THE FACT THAT DECIDES THE CURE: mode 3 never executes the DEFINE bind box

I added a candidate runtime binder and gated a diagnostic on `SCRIP_DEFINE_BIND_DIAG=1`, called from the
DEFINE site in `bb_define_bind()` (role 6, which `bb_define()` dispatches for **both** mediums). Mode 4:

```
[DBIND] name=F entry=F  lbl=LBL__F  found=1 fn=0x4018d3
[DBIND] name=F entry=F2 lbl=LBL__F2 found=1 fn=0x401b0d
orig(x)
new(x)
```

— two calls, correct per-statement entries, **and mode 4 wB is cured**. Mode 3, same binary, same program:
**the diagnostic never prints at all.** The emitted call exists (`grep -c rt_define_bind_entry wB.s` → 2)
but mode 3 never runs it.

⛔ **So mode 3 binds DEFINE entirely at slab-seal time and has no run-time DEFINE step to correct.** Any cure
written only in the template will move mode 4 and leave mode 3 byte-for-byte as it was. That is the trap this
section exists to prevent, and it is why hq_P's "template plus runtime pair" is if anything an understatement.

## 6. ⛔ THE OBVIOUS CURE IS WRONG — ablated, measured, and backed out

Making the `dentry` construction use the bind node's own entry (via `ir_define_bind_entry`) is the fix that
suggests itself. It works on the witness — wB m4 goes `orig(x)` / `new(x)` — and it produced a real
`XPASS(marker stale, promote it) m4 user_function_replace_7` on the SNOBOL4 master. **It also regresses three
master entries in m4:**

| | |
|---|---|
| regressed | `user_function_26`, `user_function_replace_10`, `user_function_replace_branch_1` |
| measured against | hq_U's snobol4-master run at `2026-09-09T01:32:26` on clean `e4ff7e9c7`, which had **zero** unmarked m4 non-PASS rows; mine had exactly these three |

`user_function_26` reduced: `DEFINE('myfunc(n)')` — **no second argument**. SPITBOL and m3 print
`PASS 1011_func_redefine (3/3)`; with the patch m4 prints `FAIL 1011/001: first definition myfunc(3)=6`,
i.e. the FIRST call is wrong. **Cause: a DEFINE with no explicit entry must bind to the `<fname>_α`
ACTIVATION, and resolving its own body label routes around the activation** (the old code's other arm sets
`dentry_name = "<fname>_α"` with a null entry precisely for this case).

⛔ And the two cases are **coupled**, which is the part that makes this hard: restricting the patch to
DEFINEs whose entry differs from the function name removes the regression (`uf26` passes again) **and removes
the cure** (wB's first DEFINE has an implicit entry, so it falls back to the per-name path and bakes
`LBL__F2` again). One arm cannot be fixed without the other.

## 7. One more trap for the next seat

`user_function_26` **passes on the baseline** while its assembly shows `body_cell$myfunc: .quad LBL__myfunc2`
baked and both DEFINE sites writing that same value — the identical shape that makes wB wrong. So **the
activation's dispatch through the body cell is conditional**; do not assume the cell is the only path, and do
not conclude from a correct-looking cell that a program is correct.

## 8. What the cure has to do

1. Give **mode 3** a run-time DEFINE step at all — otherwise nothing in the template reaches it (§5).
2. Make the **activation** carry the right per-statement body in **both** mediums, rather than routing around
   the activation (§6), and make `bb_define.cpp:424` agree with itself (§4).
3. Pass the entry label from `_DEFINE_` into `rt_sno_runtime_define` and **install** it instead of nulling
   `p->fn` and the `alpha$` cell (§2) — that is defect A in both modes.
4. Grade on **all four cells** of §1, and re-run the SNOBOL4 master, checking `user_function_26`,
   `user_function_replace_10`, `user_function_replace_branch_1` and `user_function_replace_7` by name.

⛔ NOT CURED. Tree left clean; the candidate was backed out rather than carried, so no seat measures a board
against a half-cure.
