# FINDING 2026-07-18 — JCON compiler under SCRIP: parses 18/18, ONE bomb, link blocked by a single missing-label class

Session goal: get the JCON compiler (Icon source) working in SCRIP. This finding records the
exact state after landing the parser fixes (SCRIP `2e8c7788`) and checking the sources into corpus
(`c6cd5ee9`, `programs/icon/jcon-compiler/`). Re-derive all counts fresh; do not trust prose.

## Reproduce

```bash
# sources already converted + committed in corpus/programs/icon/jcon-compiler/*.icn
cd /home/claude/SCRIP
ORDER="dump preprocessor lexer ast parse ir keyword irgen gen_bc gen_symbolic gen_dot gen_ucode optimize bytecode jtran_main"
FILES=""; for m in $ORDER; do FILES="$FILES /home/claude/corpus/programs/icon/jcon-compiler/$m.icn"; done
./scrip --compile $FILES < /dev/null > /tmp/jtran.s 2>/tmp/merge.err   # rc=0, ~451,520 lines asm
gcc -no-pie /tmp/jtran.s -L out -lscrip_rt -Wl,-rpath,out -o /tmp/jtran.bin 2>/tmp/link.err  # rc=1
```

The Makefile link order matters (jtran_main last; it holds `procedure main()`). Only jtran_main +
interfacegen + oplexgen + linker define main(); the other 14 are library modules (compile only as
part of the whole program — alone they abort "main BB graph not found", which is expected).

## State (measured this session, SCRIP `2e8c7788`)

- **Parse: 18/18 clean.** (Enabled by the parser fixes: prefix-`.` deref TT_DEREF; position-free
  `case` default; canonical `break`-operand via icn_begins_nexpr = jcon nexpr_set.)
- **Codegen: near-complete.** The merged 15-module program emits ~451,520 lines of x86-64 asm, rc=0.
- **ONE bomb stub:** exactly 1 `bb_assign_local` bomb in the whole output (grep `bb_assign_local:`
  /tmp/jtran.s == 1). NOTE: `grep -c bomb` overcounts wildly — bomb *messages* appear as `.string`
  data throughout; count the specific template tag, not the substring "bomb".
- **Link: BLOCKED — 183 undefined references, ALL one class: `xchainN_nN_α`** (BB alpha-labels
  referenced by a jmp/je/successor but never emitted). Across 19 chains, concentrated:
  xchain32375=46, xchain16628=43, xchain21827=29 (118 of 183 in 3 chains).

## The link blocker is ONE bug, not 183

A whole CONTIGUOUS SPAN of nodes is referenced-but-not-emitted. Example: in xchain1259, nodes
n119–n128 emit ZERO ports (no α/β/γ/ω), while n114/n115 just above them ARE emitted. So the walker
reaches n114/n115 but never enqueues the subgraph hanging off one of their successor pointers.

Signature at the reference site (jtran.s ~line 13894):
```
    call rt_call_arr@PLT          # array/table subscript
    ... store result ...
    cmp eax, 99                   # type-code dispatch (99 = a descriptor type tag)
    je  xchain1259_n127_α         # <- undefined: the "matches type" arm
    jmp xchain1259_n119_α         # <- undefined: the fallthrough arm
  xchain1259_n114_β:              # _β present => generator/backtrack resume in play
    jmp xchain1259_n127_α
# IR_DEREF variable -> value       # (my new TT_DEREF node n115, emitted fine)
  xchain1259_n115_α: ...
```
So the missing span is the **branch arms of a type-dispatch / disjunction that sits on a generator
(backtracking) path** — arm-entry labels the emit walker isn't enqueuing when the arm is reached only
via a successor pointer (not via the linear α→γ chain). This is the SAME "label-indirection instead
of walked self-state" family the goal file's IR_MOVE_LABEL / IR_DISJUNCTION eradication targets.

**NOT reproduced by small cases** tried this session (all link + run clean, 0 undefined refs):
`x := t["a"]` subscript; `every x := (1 to 3 | 10 to 12)`; `case type(x) of {...}`. The trigger needs
the specific nesting/combination the merged program hits — likely a disjunction/case arm that is
ALSO a generator resume target (the `_β` in the signature). Next session: build the repro up from the
xchain1259 shape (subscript result → type-cmp branch → arm that is a generator β target), then fix the
walker's successor-enqueue so branch-arm α-labels on backtracking paths are always emitted.

## The one bomb (bb_assign_local)

`src/templates/bb_assign_local.cpp` bombs when `op_a_slot < 0 || op_off < 0` (rhs value or own frame
slot unslotted). Prepared in emit.cpp IR_ASSIGN arm (L1050–1065); `op_a_slot` set at L710. Single node
in the whole compiler hits it — some local-assignment rhs shape the slotter leaves unslotted. Small
shapes tried (`x := f()`, `x := (1 to 3)`, `x := if..`, `x := [..]`, `x := a||b`) all slot fine.
Lower priority than the link blocker (1 stub vs 183 refs); isolate the same way (find the node in a
--dump-ir of the offending module).

## Order of attack next session
1. **Missing-label walk bug** (blocks link entirely; one fix clears all 183). Repro from xchain1259.
2. **bb_assign_local** (1 stub; only matters once it links and runs far enough to reach that node).

## Corpus artifact
`corpus/programs/icon/jcon-compiler/` (committed `c6cd5ee9`): 18 semicolonized sources + JCON COPYRIGHT
+ README + NOTICE entry. Semicolons added at icont's Beginner/Ender points (SCRIP requires `;`; pure
Icon does not). preprocessor.icn's undefined `$ifdef _MACINTOSH` block dropped (as JCON's build does).
No .s/.j artifacts (RULES.md: none for programs/icon).
