# A bare GLOBAL operand is snapshotted, not re-dereferenced, when a generator resumes

hq_S, 2026-09-09, measured on SCRIP a16688252 / corpus a059b477d. Found reducing IPL `progs/gediff` (CEO-452
lane, IPL G-M). NOT CURED -- the cure is in the operand model the whole emitter shares, so it is named here
rather than patched from one program's lane.

## THE CLAIM

Icon keeps a **bare variable operand as a variable** and dereferences it at each execution of the operation.
So when a generator inside the same expression resumes, the operation re-reads the variable. SCRIP does this
for a **local** and not for a **global**: a global operand is copied into a frame slot once, and the resume
path never re-enters the read, so every later iteration sees the value from before the loop.

The asymmetry is one line, `src/emitter/emit.cpp:910` -- the operand-slot resolver:

    if (o->op == IR_VAR && ... && (!is_global(...) || graph_has_local(g_emit_cfg, ...))) {
        int voff = bb_varslot_peek(...); if (voff >= 0) return voff; }   /* LOCAL: the LIVE varslot */
    int s = bb_slot_get(o); if (s >= 0) return s;                        /* GLOBAL: a one-time SNAPSHOT */

A local operand resolves to its varslot, which the assignment writes back to, so re-executing the operation
re-derefs for free. A global resolves to the node's value slot, while the assignment writes to the GVA
(`[r9 + k]`) -- so the write and the read no longer address the same storage. Confirmed in the emitted `.s`:
`n13_assign` (local) stores to `[rbp + 1168]`, the very slot its `n7_var` read from; `n26_assign` (global)
stores to `[r9 + 16]` while `n20_var` had copied `[r9 + 16]` into `[rbp + 704]` before the loop began.

## THE WITNESS — one file, four lines, and the two that pass are what make it precise

    global GN
    procedure main()
       local L, LN
       L := [1, 2, 3]
       LN := 0; every LN +:= !L;         write("1 aug   local  ", LN)
       GN := 0; every GN +:= !L;         write("2 aug   global ", GN)
       LN := 0; every LN := LN + !L;     write("3 expl  local  ", LN)
       GN := 0; every GN := GN + !L;     write("4 expl  global ", GN)
    end

| case | iconx | SCRIP |
|---|---|---|
| 1 augmented, **local**  | 6 | 6 |
| 2 augmented, **global** | 6 | **3** |
| 3 explicit,  **local**  | 6 | 6 |
| 4 explicit,  **global** | 6 | **3** |

Both global cases return the LAST element instead of the sum, and both local cases are correct. It is not the
augmented operator: cases 3 and 4 use the explicit rewrite and split the same way. `+:=` is lowered to
`X := X + rhs` (`lower_icon.c` TT_AUGOP, the TT_VAR fast path) so cases 1/2 and 3/4 are the same IR; only the
storage class differs.

⭐ **The control that stops the wrong generalisation**: `every S := S || " " || !L` with S global prints `" c"`
under **iconx as well** -- and SCRIP agrees. That is correct, not a second bug: `(S || " ") || !L` makes the
left operand a COMPOUND expression, whose value is computed once, whereas a BARE variable stays a variable and
is re-dereferenced. Any cure must keep that distinction, so "re-evaluate the left operand on resume" is the
wrong shape -- the rule is "a bare variable operand derefs at use".

## IMPACT

Any `every`-driven accumulation into a global. IPL `progs/gediff` is one: it builds its command line with
`every ArgStr ||:= " " || !arg` where `ArgStr` is a global, gets one argument instead of all of them, and dies
as `diff: missing operand after 'fixture_b.txt'` -- an error naming `diff`, not SCRIP, and not the variable.

## WHY NOT CURED HERE

The frame-slot operand protocol cannot express "read `[r9 + k]` live" -- the resolver returns a frame offset and
every consuming box emits `FRQ(off)`. Giving globals the same liveness means either teaching the operand model a
GVA-relative location (every box that reads an operand) or putting the global's read node on the generator's
resume path (generator wiring). Both are the shared engine, well outside a one-program flip, and a frame mirror
of the global is NOT a safe shortcut -- a called procedure can assign the global, and a mirror would then be
stale in the other direction.
