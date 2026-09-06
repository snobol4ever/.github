# `x86_jmp_via_cell` emits an INDIRECT jump in BINARY and a BAKED DIRECT jump in TEXT — two different programs from one encoder helper

**hq_S · 2026-09-06 · FLEET-12 · SCRIP `d49e4b88c` · measured, not read**

```c
/* src/templates/x86/x86_asm.h:650 */
inline std::string x86_jmp_via_cell(const char * label, uint64_t cell) {
    if (MEDIUM_BINARY) { /* mov rax, <cell>; mov rax, [rax]; jmp rax   -- reads the cell at RUN TIME */ }
    return x86_rec("lea") + "rax, [rip + " + (label ? label : "??") + "]\n" + x86_rec("jmp") + "rax\n";
}                                          /* ^^ jumps to a label baked at COMPILE TIME */
```

## ⛔ WHAT IS AND IS NOT BEING CLAIMED

**This is NOT the `bb_*.cpp` rule.** That rule — *zero `MEDIUM_*` may appear in any `bb_*.cpp`* — is about
**templates**. This is `x86_asm.h`, the **encoder**, and the encoder is precisely where TEXT and BINARY are
*supposed* to diverge. A `MEDIUM_BINARY` branch here is ordinary and correct.

The defect is narrower and worse: **the encoder's two arms are not two encodings of one instruction. They are
two different instructions with different semantics.** BINARY dereferences a cell and jumps to whatever it
currently holds. TEXT jumps to a fixed label. One reads state at run time; the other cannot. Everything the
house says about modes — *"a divergence is an optimization choice, never a semantic one"* (`RULES.md`
§ MODES MAY DIVERGE) — is violated by that pair, and the sanctioned mode-conditional arms exist for exactly
the opposite case.

## HOW IT SURFACED

Row `define-redefinition-ordering`. `DEFINE('F()')` … call … `DEFINE('F()','G')` … call. The oracle prints
`first` then `second-via-alt-entry`; SCRIP prints the second body **both times, in both modes**.

The function has exactly **one** dispatch point — the α stub's tail — and every call site funnels through it.
In the m4 asm that tail is `lea rax, [rip + LBL__G]; jmp rax`. Hand-editing that **one instruction** to point
at the first body and relinking (two changed lines in the `.s`, no compiler change) turns the output into
`first | first`.

⭐ **That result is the reason this finding is separate from the row's cure.** `first|first` — not
`first|second` — proves the dispatch is single and baked, and simultaneously proves that **fixing the dispatch
alone cannot cure the row**: one cell has exactly one winner. Both modes are wrong, but *not for the same
reason*: TEXT is statically bound and cannot read a binding at all, while BINARY has the right machinery
pointed at a cell nobody updates. **One symptom, two causes, split by medium** — which is why single-mode
reasoning kept producing corrections on this row.

## WHY THE TEXT ARM IS THE WAY IT IS, AND WHY THAT IS NOT AN EXCUSE

In mode 3 the emitted code lives **in the compiler's own process**, so an absolute cell address is a real
address and the indirect jump works. In mode 4 the output is a standalone object; the compiler's cell address
is meaningless there, so the author baked the label instead. That is an understandable local decision and it
produces a **silently different program**. The honest m4 spelling is an emitted data cell — a symbol in the
object's writable data, initialized at `module_init` and updated by the runtime — not a `lea`.

## ⭐ THE TRANSFERABLE PART

**A medium branch inside the encoder is legitimate; a medium branch that changes what the program *does* is a
defect wearing the encoder's clothes.** The cheap test, and it is mechanical: *strip both arms to their
observable effect. If the two descriptions differ in anything but bytes, it is not an encoding difference.*
Here one description reads memory at run time and the other does not, and no amount of "it's the encoder" makes
those the same instruction.

Note what did **not** catch this. `test_gate_template_medium_invisible.sh` is green — it polices `bb_*.cpp`
and counts raw-byte producers, which is exactly right for its own charter and blind here by construction. A
gate that is correct and green over the wrong file is the quietest kind of coverage gap.

## STATUS

Not cured here. The row's cure is ordered and the binding collapse upstream (`rt_define_site` receives the
**identical** `fn` pointer from both DEFINE sites — measured under gdb) must be undone first, or there is
nothing for a live dispatch to switch between. **Routed to hq_U** as shared-machine ground: `x86_asm.h` is the
one encoder every frontend reaches, and any change to this helper needs the cross-frontend arms.

⛔ **One instrument note, recorded because it nearly produced a false finding of my own.** `break
rt_define_site` in gdb reported *"Function not defined"* and the run completed with the breakpoint never
hitting — which reads exactly like *"the runtime hook is never called"*, a dramatic and wrong conclusion. The
symbol lives in `out/libscrip_rt.so`, not in `./scrip`, so it needs `set breakpoint pending on`. **A
breakpoint that never fires is not evidence until you have confirmed it resolved.** Same family as `$?` after
a pipeline: the instrument answered a narrower question than it appeared to.
