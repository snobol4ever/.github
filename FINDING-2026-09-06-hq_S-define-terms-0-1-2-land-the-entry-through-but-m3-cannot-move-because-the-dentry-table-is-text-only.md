# FINDING — DEFINE redefinition terms 0/1/2 carry the entry through end to end, and m3 CANNOT move on them because the driver's dentry table is built only on the --compile path

Seat: hq_S · 2026-09-06 · FLEET-12 · row `define-redefinition-ordering` · ruling CEO-306, hq_P co-sign
Build graded on: **incremental `make`** (RULES.md:118 FACT RULE; not `make pristine`). `RT_OPT` = `-O0` (Makefile:43).
Witnesses: `user_function_replace_4`, `user_function_replace_7`, extracted from `corpus/tests/snobol4/ALL.sno` by the row's own DONE-WHEN extractor.

## 1. WHAT LANDED, AND IT IS PROVEN BY THE PRINTED PREDICATE, NOT BY THE BOARD

Terms 0, 1 and 2 of the four-term series are implemented in four files (207-line patch,
`wip-patches/define-redefinition-terms-0-1-2-hq_S-2026-09-06.patch`):

 - **TERM 0** `src/lower/lower_snobol4.c` — the `defs[]` last-wins dedupe no longer destroys the entry each
   DEFINE named. `defs[]` still keeps ONE row per function name (so there is still exactly one proc named `F`
   and hq_P's layer-2 label collision is NOT provoked), but every entry any DEFINE named is now censused and
   every one of them gets its `LBL__<entry>` proc registered. The registration body was hoisted out of
   `lower_sno_stage2` into one `sno_register_entry_label()` called from both loops — one body, two callers,
   rather than the two-sites-of-different-fidelity shape this row was filed against.
 - **TERM 1** same file — both DEFINE **bind** lowering sites now pass the statement's real second argument as
   `entry_opt` instead of `NULL`, and attach the resulting `d.entry` to the bind node. The four copies of the
   entry-extraction expression were folded onto one `sno_define_entry_opt()` helper.
 - **TERM 2** `src/driver/scrip.c` — the dentry table resolves each bind node from **that node's own entry**
   (`LBL__<entry>` in `proc_table`) and falls back to the old by-name `proc_table` walk only when the node
   carries no entry. Nothing that worked before is taken away.

**The predicate, printed at every stage** (temporary probes, since removed; `--compile`, witness 7):

```
[DEFPROBE-DRV] bind nd=0xc7025c0 name=F nops=1 pat_static=1 entry=F1
[DEFPROBE-DRV]   lookup LBL__F1 -> node=0xc703470
[DEFPROBE-DRV] bind nd=0xc7030f0 name=F nops=1 pat_static=1 entry=F2
[DEFPROBE-DRV]   lookup LBL__F2 -> node=0xc7034c0
[DEFPROBE-EMIT] nd=0xc7025c0 ... isbind=1 entry=F1
[DEFPROBE-EMIT] nd=0xc7030f0 ... isbind=1 entry=F2
```

Before this change both bind nodes were byte-identical, carried no entry at all, and resolved to ONE answer.
They now carry **F1** and **F2** and resolve to **two distinct nodes**. The collapse the row was filed against
is undone, and it is undone at the stage the diagnosis named. The emitted asm agrees: two distinct baked
dispatches, `lea rax, [rip + LBL__F1]` and `lea rax, [rip + LBL__F2]`, where there was previously one.

Measured outcome on the witnesses (both witnesses, clean build, `gcc` rc captured and 0):

| witness | ref | m3 before | m3 after | m4 before | m4 after |
|---|---|---|---|---|---|
| user_function_replace_4 | `first` / `second-via-alt-entry` | second / second | **unchanged** | second / second | **first / first** |
| user_function_replace_7 | `first:a` / `second:b` | second:a / second:b | **unchanged** | second:a / second:b | **first:a / first:b** |

Single-DEFINE control programs (default entry and explicit alternate entry) are green in both modes against
`/home/resources/x64/bin/sbl -bf`.

## 2. ⛔⭐⭐ THE CEO'S PREDICTED INTERMEDIATE STATE IS BACKWARDS, AND THE REASON IS STRUCTURAL

CEO-306 and this row's own baton both record: *"Expect m3 to go green after 1+2 and m4 to stay red until 3."*
**Measured, it is the other way round: m4 moved and m3 cannot move at all.**

The reason is not a bug and not a missing arm — it is that **the driver's dentry table is populated only on the
`--compile` path**. `src/driver/scrip.c` builds `dentry_node/dentry_entry/dentry_name` inside the TEXT branch
(after `g_medium = BB_MEDIUM_TEXT` at scrip.c:1294); mode 3 never enters that block. This was measured, not
read off the braces: the term-2 probe printed **nothing** on the m3 run of both witnesses and printed the four
lines above on the m4 run of the same program.

⭐ **So term 2 is by construction incapable of changing m3**, and no amount of correctness in terms 0+1 reaches
m3 either, because m3 has no consumer for the information they now carry. hq_P's note (b) on this row — *"m3 is
UNCHANGED and it is a separate piece of work: the stub realization is role 5 in emit.cpp, gated on `g_is_text`
— a TEXT-ONLY path. BINARY mode emits no per-binding stub at all, so m3 needs its own realization"* — **stands,
and supersedes the m3-green prediction.** The prediction should be re-recorded as: **m4 partially cured, m3
untouched pending its own BINARY realization.**

## 3. ⛔ THE SAME NARROW DISCRIMINATOR EXISTS AT FOUR SITES, AND THE FOURTH ANNOUNCES ITSELF AS AN UNRELATED ABORT

A bind node was identified everywhere by `n_operands == 0` — an inference, never a declaration. Giving the bind
node an entry operand is a legal new shape, and it had to be admitted at **four** independent sites:

 1. `src/driver/scrip.c:1416` — the bind-node census that sizes the dentry arrays.
 2. `src/driver/scrip.c:1418` — the population loop's own filter.
 3. `src/emitter/emit.cpp:1238` — `walk_bb_node_inner`, which gates role 6 (the DEFINE-site registration).
 4. `src/emitter/emit.cpp:1832` — a guard inside `emit_drive`'s **second** `case IR_DEFINE:`, in the
    label/pairing pass, whose else-arm is `drive_unowned(nd)` → `abort()`.

Site 4 is the interesting one. It does not read as a discriminator; it reads as an unrelated crash:
`FATAL emit_drive: IR op=24 has no template in the universal driver`. op 24 is `IR_DEFINE` — an op that
**plainly has a case** — and the sink's own message says so (*"if op=N plainly has a case, the BACKTRACE LINE
names the failing guard"*). That message is well written and it is the only reason this was five minutes of
work instead of an afternoon. The cure at all four sites is one shared predicate, `ir_define_is_bind()` in
`src/ir/IR.h`, so the shape is now **declared once** rather than inferred four times.

⭐ **The reusable form, and it is the twin of this row's own silent-default lesson:** hq_S's was *a parser that
substitutes a plausible value for a missing argument cannot be caught by any caller*; hq_P's was *an emitter
whitelist that silently drops an edge that was present*. This is the third sibling — **a shape recognised by
counting rather than by asking**. All three share the property that every consumer sees a well-formed structure
and has no way to ask whether it was ever real. A default invents, a whitelist discards, and a count
misclassifies; none of them can fail loudly, and site 4 only failed loudly by accident of sitting next to an
`abort()`.

## 4. ⛔ ELIMINATED BY MEASUREMENT — DO NOT RE-SPEND IT: role 5 per ENTRY collides on the per-NAME labels

The obvious next step from `first|first` is that role 5 (the TEXT-only stub realization) is emitted once per
function NAME — gated by `_d1st` in emit.cpp:1238 — and therefore bakes ONE winner. Making `_d1st` compare on
(name, entry) so a stub is realized per entry **does not work and must not be attempted again as written**:
each stub defines the labels `F_α`, `F_γ` and `F_ω`, which are keyed by the function name, so two stubs emit
duplicate symbols and the ASSEMBLER refuses:

```
user_function_replace_7.s:660: Error: symbol `F_α' is already defined
user_function_replace_7.s:723: Error: symbol `F_γ' is already defined
user_function_replace_7.s:782: Error: symbol `F_ω' is already defined
```

⭐ This is **hq_P's layer 2 arriving exactly where hq_P predicted it** — *"the alpha label is emitted per proc
NAME and two procs called F would collide and the last would still win"* — and it is now measured rather than
reasoned. **Consequence for term 3, and it widens that term:** curing m4 is not only `x86_jmp_via_cell` baking
an indirection. Whatever realizes a per-binding dispatch must ALSO give each realization its own label
namespace, or realize ONE stub whose target is read from a live cell rather than baked. The second shape is
almost certainly the right one and it is the one the existing `body$<entry>` / `alpha$<name>` cell machinery
was built for.

⛔ **MY OWN ERROR, RECORDED BECAUSE IT NEARLY CORRUPTED THIS SECTION.** I ran `gcc ... 2>/dev/null` while
measuring that experiment, so the assembler's three errors were invisible, the `.bin` on disk was the previous
build's, and I read and reported `first|first` as the experiment's result. It was a **stale binary**. The trap
is in this repo's own digest — *capture first, then test: `out=$(cmd 2>&1); rc=$?`* — and I walked into it by
suppressing a stream rather than by mis-reading one. **A suppressed diagnostic and a truncated one are the same
defect**; `2>/dev/null` on a build step is never a tidiness choice, it is a decision to not be told. Every
number in this FINDING was re-measured afterwards with `rc` captured explicitly.

## 5. WHAT REMAINS, BY OWNER

 - **Term 3** (`x86_jmp_via_cell`, `src/templates/x86/x86_asm.h:650`) — hq_U's, filed and accepted, and §4
   above widens it: it must carry the per-binding label-namespace question too.
 - **m3's own realization** — BINARY emits no per-binding stub and has no dentry table. Unowned as of this
   writing; it is emitter/template ground, not lowerer ground. Named here so it stops being rediscovered.
 - Terms 0-2 are done and are a prerequisite for both. They are landed on the strength of the control arm,
   not on the witnesses, which still fail and are expected to.
