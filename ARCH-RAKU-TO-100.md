# ARCH-RAKU-TO-100 — RAKU RE-DESIGNED FROM THE BYRD-BOX MACHINE UP, AS ONE COMPLEXITY-ORDERED RUNG LADDER BUILT INCREMENTALLY (the cto, Fable 5.1 xhigh, 2026-10-30 12:2x-13:1x CDT; CEO-2044, CEO-2045, CEO-2046; Lon in-chat to the ceo, verbatim: *"Give the Raku design to CTO. Line up features by complexity and have rungs built incrementally."* · *"Regarding the Raku design: Use BB's, Byrd Boxes, NOT C code."* · *"Well, No code where possible. BB's are maximally preferred."* · *"You should re-phrase the Raku design as a COMPLETE RE-DESIGN really. Correct? 89% C code is a failure."*)
DESIGN-PLAN: raku-to-100

THE VERDICT, in Lon's frame: Raku on this machine is 89 percent C. The leaf census (SCORE.md, sha e71e5253b, mode 4 over 80 RakBench kernels) reads emitted 1.45, asm_leaf 2.54, c_runtime 88.86, libc 6.75; the five worst C functions are the BY-NAME CALL ROAD ITSELF (`rt_call_arr_bl_s`, `rt_call_arr_impl`, `try_call_builtin_by_name_bl_s_rq`, `rt_call_arr_bl`, `script_try_call_builtin_by_name_rq`: 24 to 25 G inclusive instructions each over 62 programs, 3.3 G and 4.8 G of SELF cost in the two string-compare dispatchers), because `lower_raku.c` lowers a method call, a multi, a junction, a smartmatch, a regex, a sequence, `.new`, `Grammar.parse` and every list method it does not special-case as `IR_CALL <name>` into C, and the parser pre-digests `gather`, `take`, `...`, `~~` and the `.elems` of an array operand into those calls before the lowerer sees them. That is not a Byrd-box language with some leaves; it is a C interpreter driven by boxes. THIS PAGE REPLACES IT: Raku is re-designed as the fourth syntax over the ONE machine (ARCH-ENGINE: every construct a four-port box wired at compile time, the planner placing every operand, the one emitter), with the core classes WRITTEN IN RAKU and compiled by SCRIP itself over a small kernel of boxes and ASM leaves, and the whole of it built as one complexity-ordered ladder of 930 rungs that the fleet walks incrementally while RakRungs (1,182 entries) and RakBench (84 kernels), both at 100 today, stay green at every landing. It SUPERSEDES ARCH-RAKU-REWRITE.md's twelve steps and the present roads of `lower_raku.c`; what it keeps of either it keeps by name with the reason (§ 7). The finish is 100 percent of Roast's denominator, not half of it.

## 0. The measurement (results.tsv latest mode-3 readings at 11:5x, the ceo's snapshot beside the baton; the cto's reads of 12:0x)

- ROAST: 1,464 files, 63 EXCLUDED (NO_ORACLE_ANSWER: rakudo 2026.05 `-c` refuses the unfudged file; `EXCLUDED.tsv`), 160 PASS, 1,225 NOT PASS: 870 FAIL, 232 REJECT, 54 CRASH, 51 HANG, 18 UNPROVEN. THE FAILURE CLASSES by the last line each program left (the cto's aggregation of the 1,225 notes): 229 REJECT by the emitter's refusal `[SMX] native emitter does not yet cover this program: variable 'X' is read but never assigned` (147 distinct X: `=pod` 19, bare identifiers the parser read as variables, sigilled names of a list declaration, `$?BITS`/`$?PACKAGE`/`$?MODULE`, `self`, a ternary's rhs shape, an excised node), 148 `You planned N tests, but ran M` (the program died mid-file), 100 `expected: <value>` (a wrong answer), 57 `code did not die` (an exception not raised), 50 segfaults, 49 `undefined function called`, 45 HANG under the timeout twice, 54 `You failed N tests of M`, the rest singles (type checks, `No such method`, heap at the cap, stack overflow, Perl-5 code refused).
- BY CHAPTER (pass/total): S32-str 24/69, S03-operators 8/71, S02-types 3/66, S17-supply 7/58, S32-list 2/50, S15-normalization 8/49, S32-io 2/47, S06-signature 2/35, S32-num 5/32, S02-literals 4/28, S26-documentation 1/27, S12-methods 1/27, S14-roles 1/24, S12-class 1/24, S16-io 1/23, S03-smartmatch 6/22, S32-array 2/20, S32-hash 0/17, S04-phasers 2/17, S24-testing 3/17, and 93 smaller chapters.
- HOW RAKU LOWERS TODAY (ARCH-RAKU-BOXES § 3's census, re-read at 12:0x): `lower_raku.c` (7,718 lines) has 34 `IR_CALL` sites by name and 11 `rk_*` C entries of its own (the write family and the loop-condition helpers); `for` over a range is `bb_to`, `.map/.grep/.first/.reduce/.sort` with a block are `IR_TO` loops where the shape is special-cased and `IR_CALL meth_call` otherwise; `gather`/`take` are rewritten in the PARSER (`rk_desugar_gather`, `rk_take_rewrite`) into an eager array and `push`; `...` is `__rk_seq` from the parser into `rk_sequence` in C, eager and capped; junctions are `IR_CALL __rk_jct_*` values collapsed in C from the relop boxes; `m//` is `IR_CALL re_match` into `rx.c`; `Grammar.parse` is `grammar_parse_core`; methods and multis are `IR_CALL meth_call` and `__multi_call` resolved by `strcmp` in C (`rt_str_method`'s 101 compares, `rk_list_more_methods`, `rk_io_path_method`); `~~` is `__rk_smartmatch` from the parser; `.new` is `obj_new`; the Test functions are C arms. The parser (`rk_syntax.c` 5,312, `rk_tree.c` 3,487, `rk_regex.c` 482 lines) is a pruned parse tree with desugars in it, which CEO-1715 forbids. The Raku-specific boxes that exist: `bb_match_rkrun`, `bb_match_rkcap`, `bb_match_rkland` (the regex run and capture), `bb_stmt_mark`; everything else Raku uses is the shared family (131 templates).
- WHAT IS GREEN AND STAYS GREEN: RakRungs 1,182 entries (720 smoke, 361 ladder, the rest named tests) at 100 in both modes; RakBench 84 kernels at 100; `LADDER.tsv` rungs 00 to 20 BUILT (say/print, scalars, arithmetic, strings, arrays, hashes, control, subs, for, string methods, given/when, junctions, exceptions, classes, roles, blocks, relops, compare ops, two-argument blocks, block method calls, parenthesised groups). THE TWO READINGS the ladder is measured against: the Roast row (both modes, the coo's loop) and the LEAF_SHARE line (`util_runtime_leaf_census.sh --mode m4`, hq_runtime's), which this design takes from 88.86 to under 10 (CEO-1682's row, re-pointed here).
- THE DATA THE ORDER IS CUT FROM: `corpus/packages/raku/roast/TESTS.tsv` (48,009 TAP tests over 941 files, cut 09-27 from Rakudo with TestLine preloaded: per test the CONSTRUCTS it exercises) and `RUNGS.tsv` (784 constructs ranked by frequency: a queue, not a bottleneck, as `util_raku_roast_ablation_ranker.sh`'s header proved on 09-16, which is why the ladder below orders by DEPENDENCY first and by frequency only within a family); 804 of the 1,225 red programs have test rows, 421 do not (S17-supply 51, S15 58, S26 26, S32-io 22, the 6.c and 6.d variants, S24 14, S02-types 14) and are placed by chapter.

## 1. THE RE-DESIGN: the Raku machine in five layers, and the value model under it

**1.1 THE VALUE MODEL.** Every Raku value is ONE DESCR (the machine's 16-byte descriptor: a type tag and a payload) as every SNOBOL4, Icon and Prolog value is; the tag names the SETTING's class (a type id the lowerer assigns per class at load, the MOP's `.WHAT`), an immediate payload for Int (small), Num, Bool, Nil and the type objects, a heap block of a typed collector class for everything else (Str as the machine's string, a Rat as two bigint words, an object as a block whose field layout its class declares and `bb_create`/`bb_field_get` address, a List/Array/Hash as the aggregate blocks `bb_rk_aggr` addresses, a Scalar CONTAINER as a one-cell heap block of class HB_RKSCAL whose tag says container). R3 stands: a lexical's slot holds its value (the LIFETIME RULE); `:=` between lexicals of one scope is a compile-time alias; a run-time binding and an itemized element hold a REF to a heap Scalar, dereferenced by a tag test in the box that reads it, never in C. A native (`int`, `num`, `str`) is a planner cell kind (the typed cell forms of `box_cell_shapes.tsv`), unboxed on the spine. Numeric, string and boolean CONTEXT of a value is a box arm selected by a NODE FACT the lowerer sets (`bb_rk_coerce`: one tag compare in the box; hq_raku's 10-30 case, an Array in a scalar numifying to its elems, is its first rung and the parser's `.elems` wrapping is deleted with it).

**1.2 THE FIVE LAYERS.** (a) THE PARSER STAYS the pruned parse tree it is (`rk_syntax.c`, `rk_tree.c`, `rk_regex.c`: the one Raku frontend, the bootstrap `parser_raku.sc` tree-for-tree against it) and LOSES EVERY DESUGAR: `rk_desugar_gather`, `rk_take_rewrite`, `__rk_seq`, `__rk_smartmatch`, the `.elems` wrapping (`nctx`), the `__rk_jct_*` and `__multi_call` call forms, the Test call forms; the tree carries the construct (CEO-1532/1715) and the lowerer lowers it. (b) THE LOWERER IS REWRITTEN as the box-graph builder of ARCH-ENGINE: every construct becomes the box kinds of § 2 with its node facts (the dialect facts, the context facts, the type facts the lowerer can prove), its operands pushed for the planner, NO `IR_CALL` by name: the 34 sites go, and a call reaches C only as a declared LEAF of the runtime entry table (R4 of ARCH-ZETA-LAYOUT) or an ASM leaf. (c) THE SETTING IN RAKU: the core classes (Mu, Any, Cool, Str, Int, Rat, Num, Complex, Bool, Nil, List, Array, Hash, Map, Pair, Range, Seq, Slip, Iterator, Junction, Failure, Exception and the X:: tree, Match, Regex, Grammar, Set/Bag/Mix, IO::Path, IO::Handle, IO::Spec, Date/DateTime/Instant/Duration, Version, Signature, Parameter, Capture, Code, Block, Routine, the Metamodel HOWs, Test) are RAKU SOURCE under `src/parsers/raku/setting/*.raku`, compiled by SCRIP's own Raku frontend at build into the prelude image and AUTOLOADED per name exactly as the Prolog prelude is (ARCH-PROLOG-DATABASE § 2: a user definition wins when it arrives; a setting method never shadows a user class); a setting method is boxes by construction, so "no code where possible" is met by writing the method in Raku, and the C body it replaces is deleted in the same landing. Rakudo does the same (its CORE setting is Raku), and Rakudo's `lib/Test.rakumod` (Artistic 2.0) is the setting's first file (R10). (d) THE PRIMITIVES are a CLOSED vocabulary the setting may name and nothing else may: the kernel BOXES of § 2 (each a `bb_rk_*` template on the `x86()` encoder, line-oriented, its four ports wired at compile time, its cell declared in `box_cell_shapes.tsv`) and the ASM LEAVES of § 8 (`rtx_rk_*`), each a row of the builtin table (ARCH-BUILTIN-TABLE, vocabulary `RK`) and of the runtime entry table (conv, rc, allocates, clobbers, transfers), so the planner and the emitter read them as data; a setting method calls a primitive by a `prim` form the lowerer maps to the box or the leaf at compile time, never through a by-name road. (e) THE PLANNER AND THE THREE ZETAS: Raku is already on the RSP regime (CEO-1923: subs DONE); a block activation is a cell on the spine, a closure that escapes (R5's escape boundary, CEO-1619) moves to the heap at the escape point as the first-class handle, a generator (`gather`, `...`, a lazy Seq) is the generator road `bb_suspend` pumps (its frame on the consumer's spine while it lives inside the consumer, the heap handle when it escapes), a `die` unwinds by ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise RETURNS with the ball armed and the box's ω road unwinds through the planned discards, running LEAVE/UNDO on the way: R7's frame walk is superseded by the one protocol, § 7).

## 2. THE KERNEL: the boxes and the leaves a construct may be made of (every rung's line in § 4 names one of these or says NOT-A-BOX: why)

| box | ports and cell | what it carries |
|---|---|---|
| `bb_rk_coerce` (new) | α reads the operand cell, γ the value in the asked context, ω never | numeric, string, boolean context by the operand's tag under the node fact: an aggregate's count, a Str's number, a type object's failure |
| `bb_rk_scalar` (new) | α binds or assigns, γ the container | the Scalar container: `=` stores through, `:=` rebinds, itemization, `is default`, `is rw`, a REF deref by tag |
| `bb_rk_aggr` (new) | α the aggregate and the key or index, γ the element cell or value, ω a failed EXISTS | Array and Hash primitives: index, slice, autovivification, elems, push and pop, the typed and shaped forms |
| `bb_rk_iter` (new) | α a source, β pulls the next, γ an element, ω the end | THE ONE ITERATOR: pull-one over List, Range, Seq, a gather's `bb_suspend`, a lazy source; map, grep, first, sort, reduce, for and the hyper forms are consumers of this box, their bodies setting Raku or the block |
| `bb_rk_block` (new) | α binds the topic and the placeholders, γ the value, ω a failed guard | a block invocation: `$_`, `$^a`, `-> $x`, WhateverCode, LEAVE/KEEP/UNDO arms (with `bb_rk_phaser`), `return` as a control exception |
| `bb_rk_sig` (new) | α the capture, γ bound, ω no match | signature binding: positional, named, slurpy, optional, defaults, `where`, type checks, sub-signatures, coercion types, `is copy`/`is rw` |
| `bb_rk_dispatch` (new) | α the receiver and name or the multi's capture, γ the chosen code address, ω no candidate | method dispatch through the per-type table the setting builds at load (C3 MRO, FALLBACK, `.?`, `.*`, `.+`, `.^`), multi candidates sorted at lowering by narrowness and bound at the call (R8); never a `strcmp` chain |
| `bb_rk_type` (new) | α a value and a type, γ accepts, ω rejects | type checks, `~~` against a type, coercion `Int()`, role composition (R4: a role is a template, composed per class at lowering), mixins `does`/`but`, `.WHAT`/`.WHO`/`.HOW` reads |
| `bb_rk_control` (new) | α raises, no γ; the ω road unwinds | next, last, redo, succeed, proceed, return, take, die, fail, warn as the ONE protocol's balls; CATCH and CONTROL as `bb_rk_block` arms; try; Failure values |
| `bb_rk_smartmatch` (new) | α lhs and rhs, γ true, ω false | `~~` by the right operand's kind where the lowerer knows it (type, regex, code, range, junction, literal, list) and through a kind switch otherwise; `given`/`when` the same (R9) |
| `bb_rk_junction` (new) | α the eigenstates, β the next state, γ a state, ω none left | autothreading: a junction at a relop or an argument is the box's own alternation over its eigenstates, collapsed at boolean context; `junction_collapse` retires |
| `bb_rk_hyper` (new) | α the operands, β the next pair, γ an element result, ω done | hyper (`»+«`), meta (`[+]`, `R`, `X`, `Z`, `!`, `=`), the set operators over `bb_rk_sets`, feeds |
| `bb_rk_num` (new) | α two numerics, γ the result | the numeric tower: Int small and big, Rat, FatRat, Num, Complex selected by tags, the leaves `rtx_rk_bigint_*` and `rtx_rk_rat_*` for the arithmetic (bignum.c and rk_rat.c retire into ASM) |
| `bb_rk_sets` (new) | α a QuantHash and a key, γ the weight | Set, Bag, Mix and their Hash forms over `bb_rk_aggr` |
| `bb_rk_phaser` (new) | α on the block's α, γ on its γ, ω on its ω | ENTER, LEAVE, KEEP, UNDO, FIRST, NEXT, LAST, PRE, POST on the ports of the block that declares them; BEGIN, CHECK, INIT, END run at lowering or at the program's own ports |
| `bb_rk_native` (planner) | the cell kind | `int`, `num`, `str` cells and native arrays as typed cell forms, no box of their own |
| existing | | `bb_lit_scalar`, `bb_var`, `bb_var_frame`, `bb_assign_var`, `bb_binop_arith`, `bb_binop_relop`, `bb_gate`, `bb_to`, `bb_call_fn`, `bb_call_value`, `bb_proc_value`, `bb_create`, `bb_field_get`, `bb_iterate`, `bb_suspend`, `bb_match_rkrun`, `bb_match_rkcap`, `bb_match_rkland` and the `bb_match_*` pattern family, `bb_call_proc_staged` (an EVAL result) |

THE ASM LEAVES (§ 8 lists each with the C it retires): `rtx_rk_str_*` (the NFG grapheme and codepoint primitives, case mapping over `rk_case_table.h`, normalization over `rk_unicode_norm_tables.inc`, collation, the sprintf engine), `rtx_rk_bigint_*` and `rtx_rk_rat_*`, `rtx_rk_io_*` (open, read, write, close, stat, dir, mkdir, unlink, rename, chdir, pipe, fork-exec, wait: one leaf per syscall family, each a NOT-A-BOX by nature, a kernel entry), `rtx_rk_dynfind` (the `$*X` walk up the dynamic chain by ARCH-GC § 13's link words), `rtx_rk_hash` (the Hash key hash). FORBIDDEN in the kernel: a leaf that calls back into a box (CEO-1576), a leaf that loops over user code, a leaf that holds a stack (CEO-1542), a by-name entry.

## 3. THE ORDER AND THE RULE (the generator `harness/scripts/util_raku_ladder_design.py` is the rule's executable form; `--dry-run` prints without writing)

- THE FAMILIES, IN DEPENDENCY ORDER (what a feature needs built beneath it first): F01 literals and values · F02 variables, containers and declarators · F03 operators · F04 control flow · F05 subs, signatures and dispatch · F06 blocks, closures and topics · F07 lists, arrays, hashes and sequences · F08 strings and normalization · F09 numerics · F10 classes, roles, methods and the MOP · F11 exceptions, failures and the Test assertions · F12 smartmatch, junctions and boolean context · F13 regex, match objects and grammars · F14 types, coercions, natives, enums and subsets · F15 phasers and statement prefixes · F16 IO, processes and the environment · F17 packages, modules, pragmas, EVAL and pod · F18 dynamics, introspection and the call frame · F19 sets, bags and mixes · F20 concurrency, HELD. Within a family the rungs are ordered by how many red programs exercise the construct (the unblock count), so the family's foot is its most-used feature.
- WHAT IS A FEATURE: a construct of TESTS.tsv whose family is `kw`, `op`, `lit`, `quote`, `regex`, `twigil`, `var`, `meta` or `test`, or a `meth`, `call`, `type` or `word` whose name Raku's `CORE::` (704 keys, `CORE-NAMES.tsv`) or Rakudo's method list names and the classing tables place; a test-local name (`call:foo`, `type:A`, `word:a`) places nothing; `type:X::A::B` collapses to `type:X::A` (an exception namespace is the feature, its subclasses its forms). The 20 BUILT rungs' constructs are excluded. Five SYNTHETIC constructs name the refusal classes the data has no token for: `decl:list` (a sigilled name of a list declaration read as unassigned), `decl:sigilless` (`my \a`, `constant`, an enum value, a bare identifier the parser read as a variable), `term:typeobject` (a type name used as a value), `op:ternary_rhs`, `stmt:excised`.
- THE PLACEMENT of a program: its FIRST-BLOCKING rung is the lowest rung among the features its tests exercise, its UNBLOCK rung the highest; an emitter refusal that names a construct overrides the first block; a program with no test row is placed at its chapter's family's first rung (basis `chapter:`); every row of the map carries its basis. THE COUNTS at 12:5x: 930 rungs (rung021 to rung950: F01 12, F02 10, F03 56, F04 9, F05 44, F06 3, F07 121, F08 70, F09 121, F10 51, F11 107, F12 8, F13 31, F14 65, F15 14, F16 118, F17 17, F18 14, F19 34, F20 25); 1,225 programs placed (652 by their tests, 216 by a refusal, 357 by chapter); first blocks per family F01 342, F02 224, F03 61, F04 21, F05 31, F06 2, F07 55, F08 94, F09 17, F10 35, F11 38, F12 19, F13 13, F14 78, F15 7, F16 33, F17 71, F18 2, F20 82; 42 of 930 rungs are NOT-A-BOX (the 17 compile-time directives, EVAL and pod of F17, and the 25 held rungs of F20); the biggest first blocks are rung021 `quote:<>` 220, rung035 `decl:sigilless` 102, rung276 `type:Cool` 82, rung926 `kw:start` 82 (held), rung033 `var:&` 60, rung667 `term:typeobject` 52, rung861 `kw:EVAL` 42.
- HOW THE MAP MOVES: a rung is GREEN when every declared form's witness is green in both modes (the ladder recipe); the moment a rung is green every program first-blocked on it is re-placed by the instrument (§ 9) at its next red rung, so a rung whose construct already works (many of F01's will) closes on its first landing and its programs move up at once; a program still red with every one of its rungs green GAINS A FORM on its unblock rung, cut from its failing test (at most 20 lines, the ref from rakudo 2026.05, proven red against a corrupted ref), which is how the 20-line rule and the Roast forms meet. The first-block column is where a program's journey starts; the unblock column is where it ends; both are read, neither is guessed.

## 4. THE LADDER: 930 rungs, each one construct, its family, the red programs that exercise it, the programs it first blocks and unblocks, and the box that carries it (generated; `LADDER.tsv` declares every one, STATUS DECLARED, F20's HELD)

| rung | construct | family | red programs | first block | unblock | the box, or NOT-A-BOX: why |
|---|---|---|---|---|---|---|
| **F01 literals and values** | | | | | | bb_lit_scalar / bb_rk_coerce (new: numeric, string and boolean context of a value, one tag test in the box) |
| rung021 | `quote:<>` | F01 | 292 | 220 | 5 | bb_lit_scalar; bb_rk_coerce for a value in context |
| rung022 | `quote:q` | F01 | 95 | 35 | 0 | bb_lit_scalar; bb_rk_coerce for a value in context |
| rung023 | `kw:Nil` | F01 | 87 | 34 | 0 | bb_lit_scalar; bb_rk_coerce for a value in context |
| rung024 | `kw:Inf` | F01 | 86 | 32 | 0 | bb_lit_scalar; bb_rk_coerce for a value in context |
| rung025 | `kw:NaN` | F01 | 44 | 0 | 0 | bb_lit_scalar; bb_rk_coerce for a value in context |
| rung026 | `lit:radix` | F01 | 34 | 14 | 0 | bb_lit_scalar; bb_rk_coerce for a value in context |
| rung027 | `quote:Q` | F01 | 15 | 3 | 0 | bb_lit_scalar; bb_rk_coerce for a value in context |
| rung028 | `quote:qq` | F01 | 8 | 1 | 0 | bb_lit_scalar; bb_rk_coerce for a value in context |
| rung029 | `quote:qw` | F01 | 8 | 1 | 0 | bb_lit_scalar; bb_rk_coerce for a value in context |
| rung030 | `type:WhateverCode` | F01 | 4 | 2 | 0 | bb_lit_scalar; bb_rk_coerce for a value in context |
| rung031 | `type:Whatever` | F01 | 3 | 0 | 0 | bb_lit_scalar; bb_rk_coerce for a value in context |
| rung032 | `quote:qqw` | F01 | 1 | 0 | 0 | bb_lit_scalar; bb_rk_coerce for a value in context |
| **F02 variables, containers and declarators** | | | | | | bb_rk_scalar (new: the Scalar container, = against :=, itemization, defaults) over bb_var and bb_assign_var |
| rung033 | `var:&` | F02 | 154 | 60 | 6 | bb_rk_scalar over bb_var / bb_assign_var |
| rung034 | `op::=` | F02 | 134 | 21 | 2 | bb_rk_scalar over bb_var / bb_assign_var |
| rung035 | `decl:sigilless` | F02 | 102 | 102 | 24 | bb_rk_scalar over bb_var / bb_assign_var |
| rung036 | `kw:our` | F02 | 56 | 7 | 0 | bb_rk_scalar over bb_var / bb_assign_var |
| rung037 | `op:=:=` | F02 | 35 | 5 | 0 | bb_rk_scalar over bb_var / bb_assign_var |
| rung038 | `kw:constant` | F02 | 31 | 1 | 0 | bb_rk_scalar over bb_var / bb_assign_var |
| rung039 | `decl:list` | F02 | 23 | 23 | 3 | bb_rk_scalar over bb_var / bb_assign_var |
| rung040 | `kw:state` | F02 | 18 | 2 | 2 | bb_rk_scalar over bb_var / bb_assign_var |
| rung041 | `kw:temp` | F02 | 15 | 3 | 0 | bb_rk_scalar over bb_var / bb_assign_var |
| rung042 | `kw:let` | F02 | 3 | 0 | 0 | bb_rk_scalar over bb_var / bb_assign_var |
| **F03 operators** | | | | | | bb_binop_arith / bb_binop_relop (existing) by operator class; bb_rk_hyper (new) for meta, hyper, reduce, X and Z; bb_rk_junction for the junction infixes |
| rung043 | `op:===` | F03 | 87 | 24 | 14 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung044 | `meta:reduce` | F03 | 81 | 8 | 1 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung045 | `op:.=` | F03 | 45 | 9 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung046 | `op:>>` | F03 | 34 | 3 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung047 | `op:..^` | F03 | 29 | 1 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung048 | `op:»` | F03 | 29 | 2 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung049 | `op:>>.` | F03 | 28 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung050 | `op:«` | F03 | 26 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung051 | `op:%%` | F03 | 25 | 2 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung052 | `kw:but` | F03 | 23 | 2 | 1 | bb_rk_dispatch with bb_rk_type over bb_create / bb_field_get; the MOP is SETTING Raku |
| rung053 | `op:+>` | F03 | 23 | 1 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung054 | `op:div` | F03 | 22 | 1 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung055 | `op:».` | F03 | 22 | 1 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung056 | `op:<<` | F03 | 19 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung057 | `op:!==` | F03 | 17 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung058 | `op:^..^` | F03 | 16 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung059 | `op:^..` | F03 | 15 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung060 | `op:+<` | F03 | 14 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung061 | `op:max` | F03 | 11 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung062 | `op:before` | F03 | 10 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung063 | `op:+&` | F03 | 9 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung064 | `kw:orelse` | F03 | 8 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung065 | `op:^^` | F03 | 8 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung066 | `op:after` | F03 | 8 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung067 | `op:~&` | F03 | 8 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung068 | `op:min` | F03 | 7 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung069 | `op:…` | F03 | 7 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung070 | `op:!=:=` | F03 | 6 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung071 | `op:!eqv` | F03 | 6 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung072 | `kw:andthen` | F03 | 5 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung073 | `op:+^` | F03 | 5 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung074 | `op:+|` | F03 | 5 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung075 | `op:/=` | F03 | 5 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung076 | `op:ternary_rhs` | F03 | 5 | 5 | 3 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung077 | `kw:xor` | F03 | 4 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung078 | `op:<==` | F03 | 4 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung079 | `op:?&` | F03 | 4 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung080 | `op:?|` | F03 | 4 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung081 | `op:gcd` | F03 | 4 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung082 | `op:||=` | F03 | 4 | 1 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung083 | `op:~^` | F03 | 4 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung084 | `op:~|` | F03 | 4 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung085 | `op:**=` | F03 | 3 | 1 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung086 | `op:mod` | F03 | 3 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung087 | `op:≤` | F03 | 3 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung088 | `kw:notandthen` | F03 | 2 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung089 | `op:%=` | F03 | 2 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung090 | `op:&&=` | F03 | 2 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung091 | `op:==>` | F03 | 2 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung092 | `op:?^` | F03 | 2 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung093 | `op:lcm` | F03 | 2 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung094 | `op:minmax` | F03 | 2 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung095 | `op:≠` | F03 | 2 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung096 | `op:≥` | F03 | 2 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung097 | `op:=~=` | F03 | 1 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| rung098 | `op:∘` | F03 | 1 | 0 | 0 | bb_binop_arith / bb_binop_relop; bb_rk_hyper for a meta or hyper form |
| **F04 control flow** | | | | | | bb_gate (if, unless, with), bb_to (loops) and bb_rk_control (new: next, last, redo, succeed, proceed and return as control exceptions on the one protocol) |
| rung099 | `kw:with` | F04 | 60 | 12 | 3 | bb_gate / bb_to; bb_rk_control for a transfer |
| rung100 | `kw:do` | F04 | 44 | 8 | 1 | bb_gate / bb_to; bb_rk_control for a transfer |
| rung101 | `kw:as` | F04 | 19 | 1 | 0 | bb_gate / bb_to; bb_rk_control for a transfer |
| rung102 | `kw:repeat` | F04 | 9 | 0 | 0 | bb_gate / bb_to; bb_rk_control for a transfer |
| rung103 | `kw:without` | F04 | 7 | 0 | 0 | bb_gate / bb_to; bb_rk_control for a transfer |
| rung104 | `kw:redo` | F04 | 5 | 0 | 0 | bb_rk_control on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns and the box unwinds) |
| rung105 | `kw:once` | F04 | 2 | 0 | 0 | bb_gate / bb_to; bb_rk_control for a transfer |
| rung106 | `kw:bless` | F04 | 1 | 0 | 0 | bb_rk_dispatch with bb_rk_type over bb_create / bb_field_get; the MOP is SETTING Raku |
| rung107 | `kw:orwith` | F04 | 1 | 0 | 0 | bb_gate / bb_to; bb_rk_control for a transfer |
| **F05 subs, signatures and dispatch** | | | | | | bb_call_fn / bb_call_value (existing) with bb_rk_sig (new: positional, named, slurpy, optional, defaults, type and where checks, captures) and bb_rk_dispatch (new: multi candidates and methods by a per-type table, never by name) |
| rung108 | `kw:multi` | F05 | 103 | 19 | 9 | bb_rk_dispatch: candidates sorted at lowering, bound at the call (R8) |
| rung109 | `kw:of` | F05 | 57 | 3 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung110 | `word:rw` | F05 | 45 | 5 | 3 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung111 | `word:infix` | F05 | 41 | 0 | 2 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung112 | `kw:where` | F05 | 38 | 1 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung113 | `word:copy` | F05 | 35 | 1 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung114 | `kw:proto` | F05 | 21 | 0 | 0 | bb_rk_dispatch: candidates sorted at lowering, bound at the call (R8) |
| rung115 | `word:postfix` | F05 | 11 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung116 | `kw:callsame` | F05 | 10 | 0 | 1 | bb_rk_dispatch: candidates sorted at lowering, bound at the call (R8) |
| rung117 | `call:gist` | F05 | 8 | 0 | 1 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung118 | `word:prefix` | F05 | 8 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung119 | `kw:nextsame` | F05 | 7 | 0 | 0 | bb_rk_dispatch: candidates sorted at lowering, bound at the call (R8) |
| rung120 | `word:raw` | F05 | 7 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung121 | `kw:callwith` | F05 | 6 | 0 | 0 | bb_rk_dispatch: candidates sorted at lowering, bound at the call (R8) |
| rung122 | `word:trait_mod` | F05 | 6 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung123 | `meth:type` | F05 | 5 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung124 | `word:term` | F05 | 5 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung125 | `call:leave` | F05 | 4 | 0 | 0 | bb_rk_control on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns and the box unwinds) |
| rung126 | `call:return-rw` | F05 | 4 | 0 | 1 | bb_rk_control on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns and the box unwinds) |
| rung127 | `call:undefine` | F05 | 4 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung128 | `kw:nextwith` | F05 | 4 | 0 | 0 | bb_rk_dispatch: candidates sorted at lowering, bound at the call (R8) |
| rung129 | `kw:only` | F05 | 4 | 1 | 0 | bb_rk_dispatch: candidates sorted at lowering, bound at the call (R8) |
| rung130 | `meth:params` | F05 | 4 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung131 | `word:readonly` | F05 | 4 | 0 | 1 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung132 | `call:pair` | F05 | 3 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung133 | `kw:samewith` | F05 | 3 | 0 | 0 | bb_rk_dispatch: candidates sorted at lowering, bound at the call (R8) |
| rung134 | `word:postcircumfix` | F05 | 3 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung135 | `word:required` | F05 | 2 | 1 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung136 | `call:callframe` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung137 | `call:lastcall` | F05 | 1 | 0 | 1 | bb_rk_dispatch: candidates sorted at lowering, bound at the call (R8) |
| rung138 | `call:proceed` | F05 | 1 | 0 | 0 | bb_rk_control on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns and the box unwinds) |
| rung139 | `call:subbuf-rw` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung140 | `call:substr-rw` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung141 | `call:succeed` | F05 | 1 | 0 | 0 | bb_rk_control on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns and the box unwinds) |
| rung142 | `call:take-rw` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung143 | `meth:constraints` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung144 | `meth:named` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung145 | `meth:optional` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung146 | `meth:positional` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung147 | `meth:slurpy` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung148 | `meth:yada` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung149 | `word:circumfix` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung150 | `word:dynamic` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| rung151 | `word:returns` | F05 | 1 | 0 | 0 | bb_call_fn with bb_rk_sig; bb_rk_dispatch for a multi |
| **F06 blocks, closures and topics** | | | | | | bb_rk_block (new: a block invocation with its topic, placeholders, LEAVE/KEEP/UNDO) over bb_proc_value |
| rung152 | `op:<->` | F06 | 4 | 0 | 0 | bb_rk_block over bb_proc_value |
| rung153 | `twigil::` | F06 | 3 | 0 | 0 | bb_rk_block over bb_proc_value |
| rung154 | `stmt:excised` | F06 | 2 | 2 | 1 | bb_rk_block over bb_proc_value |
| **F07 lists, arrays, hashes and sequences** | | | | | | bb_rk_iter (new: the one iterator box, pull-one over List, Range, Seq, gather, lazy) and bb_rk_aggr (new: index, slice, autoviv, elems, push and pop primitives) over bb_iterate and bb_suspend; the methods are SETTING Raku over them |
| rung155 | `op:...` | F07 | 71 | 27 | 18 | bb_suspend / bb_rk_iter: the generator road (R5), take is a gamma-SUSPEND, the consumer beta resumes it |
| rung156 | `meth:list` | F07 | 52 | 4 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung157 | `call:flat` | F07 | 41 | 1 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung158 | `kw:gather` | F07 | 41 | 2 | 1 | bb_suspend / bb_rk_iter: the generator road (R5), take is a gamma-SUSPEND, the consumer beta resumes it |
| rung159 | `word:exists` | F07 | 40 | 2 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung160 | `meth:Seq` | F07 | 38 | 1 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung161 | `meth:List` | F07 | 34 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung162 | `kw:take` | F07 | 31 | 0 | 1 | bb_suspend / bb_rk_iter: the generator road (R5), take is a gamma-SUSPEND, the consumer beta resumes it |
| rung163 | `type:Pair` | F07 | 28 | 1 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung164 | `word:delete` | F07 | 26 | 0 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung165 | `meth:flat` | F07 | 25 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung166 | `meth:pick` | F07 | 25 | 1 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung167 | `meth:roll` | F07 | 20 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung168 | `type:Positional` | F07 | 20 | 3 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung169 | `type:Seq` | F07 | 17 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung170 | `word:kv` | F07 | 17 | 0 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung171 | `meth:item` | F07 | 16 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung172 | `meth:append` | F07 | 14 | 1 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung173 | `meth:is-lazy` | F07 | 14 | 0 | 0 | bb_suspend / bb_rk_iter: the generator road (R5), take is a gamma-SUSPEND, the consumer beta resumes it |
| rung174 | `call:hash` | F07 | 13 | 2 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung175 | `kw:lazy` | F07 | 13 | 0 | 2 | bb_suspend / bb_rk_iter: the generator road (R5), take is a gamma-SUSPEND, the consumer beta resumes it |
| rung176 | `meth:antipairs` | F07 | 13 | 0 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung177 | `meth:head` | F07 | 13 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung178 | `call:list` | F07 | 12 | 1 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung179 | `meth:Slip` | F07 | 12 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung180 | `meth:default` | F07 | 12 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung181 | `meth:reverse` | F07 | 12 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung182 | `type:Slip` | F07 | 12 | 2 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung183 | `call:item` | F07 | 11 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung184 | `meth:all` | F07 | 11 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung185 | `kw:eager` | F07 | 10 | 1 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung186 | `meth:cache` | F07 | 10 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung187 | `meth:splice` | F07 | 10 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung188 | `meth:unique` | F07 | 10 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung189 | `meth:eager` | F07 | 9 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung190 | `meth:end` | F07 | 8 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung191 | `type:Iterable` | F07 | 8 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung192 | `type:Map` | F07 | 8 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung193 | `type:Range` | F07 | 8 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung194 | `word:ignorecase` | F07 | 8 | 1 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung195 | `word:ignoremark` | F07 | 8 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung196 | `call:append` | F07 | 7 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung197 | `call:kv` | F07 | 7 | 0 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung198 | `call:reverse` | F07 | 7 | 1 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung199 | `call:values` | F07 | 7 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung200 | `meth:Array` | F07 | 7 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung201 | `meth:any` | F07 | 7 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung202 | `meth:iterator` | F07 | 7 | 0 | 0 | bb_suspend / bb_rk_iter: the generator road (R5), take is a gamma-SUSPEND, the consumer beta resumes it |
| rung203 | `meth:prepend` | F07 | 7 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung204 | `meth:shape` | F07 | 7 | 1 | 2 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung205 | `meth:AT-POS` | F07 | 6 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung206 | `meth:Supply` | F07 | 6 | 2 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung207 | `call:array` | F07 | 5 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung208 | `call:keys` | F07 | 5 | 0 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung209 | `meth:ASSIGN-POS` | F07 | 5 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung210 | `meth:BIND-POS` | F07 | 5 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung211 | `meth:combinations` | F07 | 5 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung212 | `type:IterationEnd` | F07 | 5 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung213 | `call:prepend` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung214 | `call:rotate` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung215 | `meth:DELETE-POS` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung216 | `meth:EXISTS-POS` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung217 | `meth:Hash` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung218 | `meth:none` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung219 | `meth:one` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung220 | `meth:permutations` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung221 | `meth:pull-one` | F07 | 4 | 0 | 0 | bb_suspend / bb_rk_iter: the generator road (R5), take is a gamma-SUSPEND, the consumer beta resumes it |
| rung222 | `meth:repeated` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung223 | `meth:rotate` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung224 | `meth:rotor` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung225 | `meth:squish` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung226 | `type:Associative` | F07 | 4 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung227 | `call:pairs` | F07 | 3 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung228 | `call:pick` | F07 | 3 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung229 | `call:slip` | F07 | 3 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung230 | `call:splice` | F07 | 3 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung231 | `call:zip` | F07 | 3 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung232 | `meth:STORE` | F07 | 3 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung233 | `meth:hyper` | F07 | 3 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung234 | `type:Iterator` | F07 | 3 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung235 | `word:nth` | F07 | 3 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung236 | `word:sigspace` | F07 | 3 | 1 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung237 | `call:head` | F07 | 2 | 0 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung238 | `call:roll` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung239 | `meth:ASSIGN-KEY` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung240 | `meth:BIND-KEY` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung241 | `meth:Capture` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung242 | `meth:EXISTS-KEY` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung243 | `meth:Map` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung244 | `meth:antipair` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung245 | `meth:categorize` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung246 | `meth:classify` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung247 | `meth:lazy` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung248 | `meth:pairup` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung249 | `meth:produce` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung250 | `meth:tail` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung251 | `meth:tree` | F07 | 2 | 0 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung252 | `type:Capture` | F07 | 2 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung253 | `call:cache` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung254 | `call:categorize` | F07 | 1 | 0 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung255 | `call:classify` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung256 | `call:combinations` | F07 | 1 | 0 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung257 | `call:cross` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung258 | `call:permutations` | F07 | 1 | 0 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung259 | `call:produce` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung260 | `call:repeated` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung261 | `call:roundrobin` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung262 | `call:squish` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung263 | `call:tail` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung264 | `call:unique` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung265 | `kw:hyper` | F07 | 1 | 0 | 1 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung266 | `meth:AT-KEY` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung267 | `meth:DELETE-KEY` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung268 | `meth:batch` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung269 | `meth:deepmap` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung270 | `meth:duckmap` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung271 | `meth:flatmap` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung272 | `meth:nodemap` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung273 | `meth:push-all` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung274 | `meth:race` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| rung275 | `meth:skip` | F07 | 1 | 0 | 0 | bb_rk_iter / bb_rk_aggr; the method body is SETTING Raku |
| **F08 strings and normalization** | | | | | | bb_rk_dispatch to rtx_rk_str_* (ASM leaves over the NFG and case tables); the methods are SETTING Raku over the leaves |
| rung276 | `type:Cool` | F08 | 32 | 82 | 81 | bb_rk_dispatch to rtx_rk_str_* (ASM leaf); the method body is SETTING Raku |
| rung277 | `meth:contains` | F08 | 22 | 1 | 0 | bb_rk_dispatch to rtx_rk_str_contains (ASM leaf); the method body is SETTING Raku |
| rung278 | `meth:decode` | F08 | 17 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_decode (ASM leaf); the method body is SETTING Raku |
| rung279 | `type:Buf` | F08 | 17 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_* (ASM leaf); the method body is SETTING Raku |
| rung280 | `meth:encode` | F08 | 16 | 0 | 1 | bb_rk_dispatch to rtx_rk_str_encode (ASM leaf); the method body is SETTING Raku |
| rung281 | `meth:fmt` | F08 | 14 | 1 | 2 | bb_rk_dispatch to rtx_rk_str_fmt (ASM leaf); the method body is SETTING Raku |
| rung282 | `meth:chr` | F08 | 13 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_chr (ASM leaf); the method body is SETTING Raku |
| rung283 | `call:chr` | F08 | 10 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_chr (ASM leaf); the method body is SETTING Raku |
| rung284 | `meth:ord` | F08 | 10 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_ord (ASM leaf); the method body is SETTING Raku |
| rung285 | `call:sprintf` | F08 | 9 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_sprintf (ASM leaf); the method body is SETTING Raku |
| rung286 | `call:substr` | F08 | 9 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_substr (ASM leaf); the method body is SETTING Raku |
| rung287 | `call:uc` | F08 | 9 | 2 | 0 | bb_rk_dispatch to rtx_rk_str_uc (ASM leaf); the method body is SETTING Raku |
| rung288 | `call:val` | F08 | 9 | 1 | 0 | bb_rk_dispatch to rtx_rk_str_val (ASM leaf); the method body is SETTING Raku |
| rung289 | `type:Blob` | F08 | 9 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_* (ASM leaf); the method body is SETTING Raku |
| rung290 | `call:lc` | F08 | 8 | 2 | 1 | bb_rk_dispatch to rtx_rk_str_lc (ASM leaf); the method body is SETTING Raku |
| rung291 | `meth:ords` | F08 | 8 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_ords (ASM leaf); the method body is SETTING Raku |
| rung292 | `meth:starts-with` | F08 | 8 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_starts_with (ASM leaf); the method body is SETTING Raku |
| rung293 | `meth:invert` | F08 | 7 | 0 | 1 | bb_rk_dispatch to rtx_rk_str_invert (ASM leaf); the method body is SETTING Raku |
| rung294 | `meth:trans` | F08 | 7 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_trans (ASM leaf); the method body is SETTING Raku |
| rung295 | `call:ord` | F08 | 6 | 0 | 1 | bb_rk_dispatch to rtx_rk_str_ord (ASM leaf); the method body is SETTING Raku |
| rung296 | `type:Stringy` | F08 | 6 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_* (ASM leaf); the method body is SETTING Raku |
| rung297 | `meth:chomp` | F08 | 5 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_chomp (ASM leaf); the method body is SETTING Raku |
| rung298 | `meth:tc` | F08 | 5 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_tc (ASM leaf); the method body is SETTING Raku |
| rung299 | `call:chars` | F08 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_chars (ASM leaf); the method body is SETTING Raku |
| rung300 | `meth:ends-with` | F08 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_ends_with (ASM leaf); the method body is SETTING Raku |
| rung301 | `type:IntStr` | F08 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_* (ASM leaf); the method body is SETTING Raku |
| rung302 | `type:NumStr` | F08 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_* (ASM leaf); the method body is SETTING Raku |
| rung303 | `type:RatStr` | F08 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_* (ASM leaf); the method body is SETTING Raku |
| rung304 | `call:flip` | F08 | 3 | 0 | 2 | bb_rk_dispatch to rtx_rk_str_flip (ASM leaf); the method body is SETTING Raku |
| rung305 | `call:index` | F08 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_index (ASM leaf); the method body is SETTING Raku |
| rung306 | `meth:chop` | F08 | 3 | 1 | 0 | bb_rk_dispatch to rtx_rk_str_chop (ASM leaf); the method body is SETTING Raku |
| rung307 | `meth:chrs` | F08 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_chrs (ASM leaf); the method body is SETTING Raku |
| rung308 | `meth:printf` | F08 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_printf (ASM leaf); the method body is SETTING Raku |
| rung309 | `meth:sprintf` | F08 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_sprintf (ASM leaf); the method body is SETTING Raku |
| rung310 | `meth:substr-rw` | F08 | 3 | 0 | 1 | bb_rk_dispatch to rtx_rk_str_substr_rw (ASM leaf); the method body is SETTING Raku |
| rung311 | `type:ComplexStr` | F08 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_* (ASM leaf); the method body is SETTING Raku |
| rung312 | `call:ords` | F08 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_ords (ASM leaf); the method body is SETTING Raku |
| rung313 | `call:words` | F08 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_words (ASM leaf); the method body is SETTING Raku |
| rung314 | `meth:NFD` | F08 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_nfd (ASM leaf); the method body is SETTING Raku |
| rung315 | `meth:Stringy` | F08 | 2 | 1 | 0 | bb_rk_dispatch to rtx_rk_str_stringy (ASM leaf); the method body is SETTING Raku |
| rung316 | `meth:codes` | F08 | 2 | 1 | 1 | bb_rk_dispatch to rtx_rk_str_codes (ASM leaf); the method body is SETTING Raku |
| rung317 | `meth:rindex` | F08 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_rindex (ASM leaf); the method body is SETTING Raku |
| rung318 | `meth:trim-trailing` | F08 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_trim_trailing (ASM leaf); the method body is SETTING Raku |
| rung319 | `meth:unival` | F08 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_unival (ASM leaf); the method body is SETTING Raku |
| rung320 | `meth:val` | F08 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_val (ASM leaf); the method body is SETTING Raku |
| rung321 | `meth:wordcase` | F08 | 2 | 1 | 0 | bb_rk_dispatch to rtx_rk_str_wordcase (ASM leaf); the method body is SETTING Raku |
| rung322 | `type:NFD` | F08 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_* (ASM leaf); the method body is SETTING Raku |
| rung323 | `call:chop` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_chop (ASM leaf); the method body is SETTING Raku |
| rung324 | `call:chrs` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_chrs (ASM leaf); the method body is SETTING Raku |
| rung325 | `call:comb` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_comb (ASM leaf); the method body is SETTING Raku |
| rung326 | `call:indices` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_indices (ASM leaf); the method body is SETTING Raku |
| rung327 | `call:printf` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_printf (ASM leaf); the method body is SETTING Raku |
| rung328 | `call:rindex` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_rindex (ASM leaf); the method body is SETTING Raku |
| rung329 | `call:samecase` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_samecase (ASM leaf); the method body is SETTING Raku |
| rung330 | `call:samemark` | F08 | 1 | 1 | 0 | bb_rk_dispatch to rtx_rk_str_samemark (ASM leaf); the method body is SETTING Raku |
| rung331 | `call:tc` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_tc (ASM leaf); the method body is SETTING Raku |
| rung332 | `call:trim` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_trim (ASM leaf); the method body is SETTING Raku |
| rung333 | `call:trim-leading` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_trim_leading (ASM leaf); the method body is SETTING Raku |
| rung334 | `call:trim-trailing` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_trim_trailing (ASM leaf); the method body is SETTING Raku |
| rung335 | `call:unival` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_unival (ASM leaf); the method body is SETTING Raku |
| rung336 | `call:wordcase` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_wordcase (ASM leaf); the method body is SETTING Raku |
| rung337 | `meth:indent` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_indent (ASM leaf); the method body is SETTING Raku |
| rung338 | `meth:indices` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_indices (ASM leaf); the method body is SETTING Raku |
| rung339 | `meth:parse-base` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_parse_base (ASM leaf); the method body is SETTING Raku |
| rung340 | `meth:polymod` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_polymod (ASM leaf); the method body is SETTING Raku |
| rung341 | `meth:samecase` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_samecase (ASM leaf); the method body is SETTING Raku |
| rung342 | `meth:samemark` | F08 | 1 | 0 | 1 | bb_rk_dispatch to rtx_rk_str_samemark (ASM leaf); the method body is SETTING Raku |
| rung343 | `meth:trim-leading` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_trim_leading (ASM leaf); the method body is SETTING Raku |
| rung344 | `meth:uniprop` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_uniprop (ASM leaf); the method body is SETTING Raku |
| rung345 | `type:StrDistance` | F08 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_str_* (ASM leaf); the method body is SETTING Raku |
| **F09 numerics** | | | | | | bb_binop_arith with bb_rk_num (new: the Int, Rat, Num, Complex tower selected by tags) over rtx_rk_bigint and rtx_rk_rat (ASM leaves; bignum.c and rk_rat.c retire) |
| rung346 | `type:Rat` | F09 | 37 | 7 | 4 | bb_binop_arith with bb_rk_num; rtx_rk_bigint / rtx_rk_rat (ASM leaves) |
| rung347 | `type:Numeric` | F09 | 36 | 0 | 1 | bb_binop_arith with bb_rk_num; rtx_rk_bigint / rtx_rk_rat (ASM leaves) |
| rung348 | `type:Complex` | F09 | 35 | 1 | 0 | bb_binop_arith with bb_rk_num; rtx_rk_bigint / rtx_rk_rat (ASM leaves) |
| rung349 | `type:Real` | F09 | 29 | 0 | 0 | bb_binop_arith with bb_rk_num; rtx_rk_bigint / rtx_rk_rat (ASM leaves) |
| rung350 | `call:sqrt` | F09 | 27 | 0 | 0 | bb_rk_num to rtx_rk_num_sqrt (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung351 | `meth:Rat` | F09 | 23 | 0 | 1 | bb_rk_num to rtx_rk_num_rat (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung352 | `call:exp` | F09 | 21 | 0 | 0 | bb_rk_num to rtx_rk_num_exp (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung353 | `meth:FatRat` | F09 | 18 | 0 | 0 | bb_rk_num to rtx_rk_num_fatrat (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung354 | `call:abs` | F09 | 15 | 0 | 0 | bb_rk_num to rtx_rk_num_abs (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung355 | `meth:Complex` | F09 | 15 | 0 | 0 | bb_rk_num to rtx_rk_num_complex (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung356 | `meth:abs` | F09 | 13 | 0 | 1 | bb_rk_num to rtx_rk_num_abs (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung357 | `meth:rand` | F09 | 11 | 2 | 0 | bb_rk_num to rtx_rk_num_rand (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung358 | `meth:succ` | F09 | 10 | 4 | 0 | bb_rk_num to rtx_rk_num_succ (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung359 | `type:More` | F09 | 10 | 0 | 0 | bb_binop_arith with bb_rk_num; rtx_rk_bigint / rtx_rk_rat (ASM leaves) |
| rung360 | `call:sin` | F09 | 9 | 0 | 0 | bb_rk_num to rtx_rk_num_sin (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung361 | `meth:floor` | F09 | 9 | 0 | 0 | bb_rk_num to rtx_rk_num_floor (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung362 | `meth:max` | F09 | 9 | 0 | 0 | bb_rk_num to rtx_rk_num_max (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung363 | `meth:min` | F09 | 9 | 0 | 1 | bb_rk_num to rtx_rk_num_min (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung364 | `meth:pred` | F09 | 9 | 0 | 0 | bb_rk_num to rtx_rk_num_pred (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung365 | `meth:sqrt` | F09 | 9 | 1 | 0 | bb_rk_num to rtx_rk_num_sqrt (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung366 | `type:Less` | F09 | 9 | 0 | 0 | bb_binop_arith with bb_rk_num; rtx_rk_bigint / rtx_rk_rat (ASM leaves) |
| rung367 | `type:Same` | F09 | 9 | 0 | 0 | bb_binop_arith with bb_rk_num; rtx_rk_bigint / rtx_rk_rat (ASM leaves) |
| rung368 | `type:FatRat` | F09 | 8 | 0 | 1 | bb_binop_arith with bb_rk_num; rtx_rk_bigint / rtx_rk_rat (ASM leaves) |
| rung369 | `call:cos` | F09 | 7 | 0 | 0 | bb_rk_num to rtx_rk_num_cos (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung370 | `call:log` | F09 | 7 | 0 | 0 | bb_rk_num to rtx_rk_num_log (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung371 | `call:rand` | F09 | 7 | 1 | 0 | bb_rk_num to rtx_rk_num_rand (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung372 | `meth:Numeric` | F09 | 7 | 0 | 0 | bb_rk_num to rtx_rk_num_numeric (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung373 | `meth:ceiling` | F09 | 6 | 0 | 0 | bb_rk_num to rtx_rk_num_ceiling (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung374 | `meth:sign` | F09 | 6 | 0 | 0 | bb_rk_num to rtx_rk_num_sign (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung375 | `type:UInt` | F09 | 6 | 0 | 0 | bb_binop_arith with bb_rk_num; rtx_rk_bigint / rtx_rk_rat (ASM leaves) |
| rung376 | `call:ceiling` | F09 | 5 | 0 | 0 | bb_rk_num to rtx_rk_num_ceiling (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung377 | `call:cosh` | F09 | 5 | 0 | 0 | bb_rk_num to rtx_rk_num_cosh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung378 | `call:sinh` | F09 | 5 | 0 | 0 | bb_rk_num to rtx_rk_num_sinh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung379 | `call:truncate` | F09 | 5 | 0 | 0 | bb_rk_num to rtx_rk_num_truncate (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung380 | `meth:is-prime` | F09 | 5 | 0 | 1 | bb_rk_num to rtx_rk_num_is_prime (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung381 | `meth:round` | F09 | 5 | 0 | 0 | bb_rk_num to rtx_rk_num_round (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung382 | `meth:sum` | F09 | 5 | 0 | 0 | bb_rk_num to rtx_rk_num_sum (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung383 | `call:floor` | F09 | 4 | 0 | 1 | bb_rk_num to rtx_rk_num_floor (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung384 | `meth:base` | F09 | 4 | 0 | 1 | bb_rk_num to rtx_rk_num_base (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung385 | `meth:im` | F09 | 4 | 0 | 0 | bb_rk_num to rtx_rk_num_im (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung386 | `meth:narrow` | F09 | 4 | 0 | 0 | bb_rk_num to rtx_rk_num_narrow (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung387 | `meth:re` | F09 | 4 | 0 | 0 | bb_rk_num to rtx_rk_num_re (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung388 | `meth:roots` | F09 | 4 | 0 | 0 | bb_rk_num to rtx_rk_num_roots (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung389 | `meth:truncate` | F09 | 4 | 0 | 0 | bb_rk_num to rtx_rk_num_truncate (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung390 | `meth:unpolar` | F09 | 4 | 0 | 0 | bb_rk_num to rtx_rk_num_unpolar (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung391 | `call:cis` | F09 | 3 | 0 | 0 | bb_rk_num to rtx_rk_num_cis (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung392 | `call:expmod` | F09 | 3 | 1 | 0 | bb_rk_num to rtx_rk_num_expmod (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung393 | `call:sign` | F09 | 3 | 0 | 0 | bb_rk_num to rtx_rk_num_sign (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung394 | `call:sum` | F09 | 3 | 0 | 0 | bb_rk_num to rtx_rk_num_sum (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung395 | `meth:cis` | F09 | 3 | 0 | 0 | bb_rk_num to rtx_rk_num_cis (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung396 | `meth:denominator` | F09 | 3 | 0 | 0 | bb_rk_num to rtx_rk_num_denominator (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung397 | `meth:exp` | F09 | 3 | 0 | 0 | bb_rk_num to rtx_rk_num_exp (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung398 | `meth:log` | F09 | 3 | 0 | 0 | bb_rk_num to rtx_rk_num_log (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung399 | `meth:log10` | F09 | 3 | 0 | 0 | bb_rk_num to rtx_rk_num_log10 (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung400 | `meth:minmax` | F09 | 3 | 0 | 0 | bb_rk_num to rtx_rk_num_minmax (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung401 | `meth:nude` | F09 | 3 | 0 | 0 | bb_rk_num to rtx_rk_num_nude (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung402 | `meth:numerator` | F09 | 3 | 0 | 0 | bb_rk_num to rtx_rk_num_numerator (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung403 | `meth:sin` | F09 | 3 | 0 | 0 | bb_rk_num to rtx_rk_num_sin (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung404 | `type:Order` | F09 | 3 | 0 | 0 | bb_binop_arith with bb_rk_num; rtx_rk_bigint / rtx_rk_rat (ASM leaves) |
| rung405 | `call:acos` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_acos (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung406 | `call:acosh` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_acosh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung407 | `call:acotan` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_acotan (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung408 | `call:asec` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_asec (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung409 | `call:asin` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_asin (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung410 | `call:asinh` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_asinh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung411 | `call:atan` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_atan (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung412 | `call:atan2` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_atan2 (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung413 | `call:atanh` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_atanh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung414 | `call:cotan` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_cotan (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung415 | `call:round` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_round (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung416 | `call:sec` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_sec (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung417 | `call:srand` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_srand (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung418 | `call:tan` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_tan (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung419 | `call:tanh` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_tanh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung420 | `meth:Real` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_real (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung421 | `meth:atanh` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_atanh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung422 | `meth:conj` | F09 | 2 | 0 | 0 | bb_rk_num to rtx_rk_num_conj (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung423 | `type:Rational` | F09 | 2 | 0 | 0 | bb_binop_arith with bb_rk_num; rtx_rk_bigint / rtx_rk_rat (ASM leaves) |
| rung424 | `call:acosec` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_acosec (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung425 | `call:acosech` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_acosech (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung426 | `call:acotanh` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_acotanh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung427 | `call:asech` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_asech (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung428 | `call:cosec` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_cosec (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung429 | `call:cosech` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_cosech (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung430 | `call:cotanh` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_cotanh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung431 | `call:is-prime` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_is_prime (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung432 | `call:log10` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_log10 (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung433 | `call:log2` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_log2 (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung434 | `call:lsb` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_lsb (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung435 | `call:msb` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_msb (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung436 | `call:roots` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_roots (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung437 | `call:sech` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_sech (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung438 | `call:unpolar` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_unpolar (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung439 | `meth:Bridge` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_bridge (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung440 | `meth:acos` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_acos (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung441 | `meth:acosec` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_acosec (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung442 | `meth:acosech` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_acosech (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung443 | `meth:acosh` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_acosh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung444 | `meth:acotan` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_acotan (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung445 | `meth:acotanh` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_acotanh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung446 | `meth:asec` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_asec (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung447 | `meth:asech` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_asech (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung448 | `meth:asin` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_asin (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung449 | `meth:asinh` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_asinh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung450 | `meth:atan` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_atan (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung451 | `meth:cos` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_cos (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung452 | `meth:cosec` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_cosec (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung453 | `meth:cosech` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_cosech (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung454 | `meth:cosh` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_cosh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung455 | `meth:cotan` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_cotan (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung456 | `meth:cotanh` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_cotanh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung457 | `meth:expmod` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_expmod (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung458 | `meth:log2` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_log2 (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung459 | `meth:lsb` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_lsb (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung460 | `meth:msb` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_msb (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung461 | `meth:polar` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_polar (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung462 | `meth:sec` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_sec (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung463 | `meth:sech` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_sech (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung464 | `meth:sinh` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_sinh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung465 | `meth:tan` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_tan (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| rung466 | `meth:tanh` | F09 | 1 | 0 | 0 | bb_rk_num to rtx_rk_num_tanh (ASM leaf over libm or the bigint/rat leaves); the method body is SETTING Raku |
| **F10 classes, roles, methods and the MOP** | | | | | | bb_rk_dispatch (new) with bb_create and bb_field_get (existing) and bb_rk_type (new: type checks, coercion, role composition, mixins); the MOP is SETTING Raku |
| rung467 | `meth:WHAT` | F10 | 84 | 27 | 28 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung468 | `op:.^` | F10 | 74 | 1 | 1 | bb_rk_dispatch with bb_rk_type over bb_create / bb_field_get; the MOP is SETTING Raku |
| rung469 | `meth:value` | F10 | 55 | 0 | 1 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung470 | `meth:key` | F10 | 49 | 0 | 4 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung471 | `meth:name` | F10 | 35 | 0 | 1 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung472 | `meth:bless` | F10 | 21 | 0 | 1 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung473 | `meth:of` | F10 | 21 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung474 | `op:.*` | F10 | 17 | 0 | 0 | bb_rk_dispatch with bb_rk_type over bb_create / bb_field_get; the MOP is SETTING Raku |
| rung475 | `kw:submethod` | F10 | 16 | 2 | 0 | bb_rk_dispatch with bb_rk_type over bb_create / bb_field_get; the MOP is SETTING Raku |
| rung476 | `meth:WHICH` | F10 | 15 | 0 | 1 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung477 | `meth:clone` | F10 | 15 | 1 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung478 | `meth:signature` | F10 | 15 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung479 | `op:.+` | F10 | 15 | 0 | 1 | bb_rk_dispatch with bb_rk_type over bb_create / bb_field_get; the MOP is SETTING Raku |
| rung480 | `type:Code` | F10 | 15 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung481 | `meth:HOW` | F10 | 14 | 1 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung482 | `op:.&` | F10 | 14 | 0 | 0 | bb_rk_dispatch with bb_rk_type over bb_create / bb_field_get; the MOP is SETTING Raku |
| rung483 | `meth:ACCEPTS` | F10 | 13 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung484 | `meth:isa` | F10 | 13 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung485 | `type:Callable` | F10 | 13 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung486 | `type:Sub` | F10 | 13 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung487 | `type:Block` | F10 | 11 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung488 | `meth:can` | F10 | 8 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung489 | `meth:does` | F10 | 8 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung490 | `type:Method` | F10 | 8 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung491 | `type:Routine` | F10 | 8 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung492 | `meth:candidates` | F10 | 7 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung493 | `meth:WHO` | F10 | 5 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung494 | `meth:count` | F10 | 5 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung495 | `meth:wrap` | F10 | 5 | 0 | 2 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung496 | `type:Proxy` | F10 | 5 | 0 | 2 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung497 | `meth:arity` | F10 | 4 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung498 | `kw:self` | F10 | 3 | 3 | 0 | bb_rk_dispatch with bb_rk_type over bb_create / bb_field_get; the MOP is SETTING Raku |
| rung499 | `type:Attribute` | F10 | 3 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung500 | `type:Scalar` | F10 | 3 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung501 | `meth:CREATE` | F10 | 2 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung502 | `meth:cando` | F10 | 2 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung503 | `meth:package` | F10 | 2 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung504 | `meth:pair` | F10 | 2 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung505 | `meth:returns` | F10 | 2 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung506 | `meth:unwrap` | F10 | 2 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung507 | `op:.?` | F10 | 2 | 0 | 0 | bb_rk_dispatch with bb_rk_type over bb_create / bb_field_get; the MOP is SETTING Raku |
| rung508 | `type:Metamodel::ClassHOW` | F10 | 2 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung509 | `type:ObjAt` | F10 | 2 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung510 | `type:Parameter` | F10 | 2 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung511 | `meth:BUILDALL` | F10 | 1 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung512 | `meth:callwith` | F10 | 1 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung513 | `meth:dispatcher` | F10 | 1 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung514 | `meth:is_dispatcher` | F10 | 1 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung515 | `meth:perl` | F10 | 1 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung516 | `type:Label` | F10 | 1 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| rung517 | `type:Signature` | F10 | 1 | 0 | 0 | bb_rk_dispatch with bb_rk_type; bb_create / bb_field_get; the MOP is SETTING Raku |
| **F11 exceptions, failures and the Test assertions** | | | | | | bb_rk_control (new) on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns, the box unwinds); CATCH and CONTROL are bb_rk_block arms; Test is SETTING Raku (R10) |
| rung518 | `type:Exception` | F11 | 119 | 22 | 20 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung519 | `test:eval-lives-ok` | F11 | 67 | 3 | 4 | SETTING Raku (Test.rakumod, R10) over bb_rk_control and bb_call_fn |
| rung520 | `type:X::Syntax` | F11 | 61 | 1 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung521 | `type:X::TypeCheck` | F11 | 44 | 0 | 2 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung522 | `type:Failure` | F11 | 30 | 1 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung523 | `type:X::Undeclared` | F11 | 30 | 2 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung524 | `test:fails-like` | F11 | 23 | 2 | 0 | SETTING Raku (Test.rakumod, R10) over bb_rk_control and bb_call_fn |
| rung525 | `type:X::Assignment` | F11 | 22 | 1 | 3 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung526 | `type:X::Comp` | F11 | 22 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung527 | `type:X::Cannot` | F11 | 20 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung528 | `type:X::Str` | F11 | 20 | 0 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung529 | `type:X::Method` | F11 | 19 | 1 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung530 | `type:X::Obsolete` | F11 | 19 | 1 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung531 | `type:X::OutOfRange` | F11 | 19 | 0 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung532 | `kw:CATCH` | F11 | 18 | 1 | 2 | bb_rk_control on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns and the box unwinds) |
| rung533 | `type:X::Multi` | F11 | 17 | 0 | 2 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung534 | `type:X::Numeric` | F11 | 14 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung535 | `type:X::Parameter` | F11 | 14 | 0 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung536 | `type:X::Redeclaration` | F11 | 14 | 1 | 2 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung537 | `kw:fail` | F11 | 11 | 0 | 1 | bb_rk_control on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns and the box unwinds) |
| rung538 | `test:does-ok` | F11 | 11 | 0 | 0 | SETTING Raku (Test.rakumod, R10) over bb_rk_control and bb_call_fn |
| rung539 | `test:like` | F11 | 10 | 0 | 0 | SETTING Raku (Test.rakumod, R10) over bb_rk_control and bb_call_fn |
| rung540 | `type:X::AdHoc` | F11 | 10 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung541 | `meth:resume` | F11 | 8 | 0 | 0 | bb_rk_control on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns and the box unwinds) |
| rung542 | `type:X::Attribute` | F11 | 8 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung543 | `type:X::Inheritance` | F11 | 8 | 1 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung544 | `meth:message` | F11 | 7 | 0 | 0 | bb_rk_control on the one exceptions protocol; CATCH is a bb_rk_block arm; Test is SETTING Raku |
| rung545 | `type:X::IO` | F11 | 7 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung546 | `kw:CONTROL` | F11 | 6 | 0 | 0 | bb_rk_control on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns and the box unwinds) |
| rung547 | `test:eval-dies-ok` | F11 | 5 | 0 | 1 | SETTING Raku (Test.rakumod, R10) over bb_rk_control and bb_call_fn |
| rung548 | `type:CX::Warn` | F11 | 5 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung549 | `type:X::ControlFlow` | F11 | 5 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung550 | `type:X::Immutable` | F11 | 5 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung551 | `meth:payload` | F11 | 4 | 0 | 0 | bb_rk_control on the one exceptions protocol; CATCH is a bb_rk_block arm; Test is SETTING Raku |
| rung552 | `meth:handled` | F11 | 3 | 0 | 1 | bb_rk_control on the one exceptions protocol; CATCH is a bb_rk_block arm; Test is SETTING Raku |
| rung553 | `meth:sink` | F11 | 3 | 0 | 0 | bb_rk_control on the one exceptions protocol; CATCH is a bb_rk_block arm; Test is SETTING Raku |
| rung554 | `meth:throw` | F11 | 3 | 0 | 0 | bb_rk_control on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns and the box unwinds) |
| rung555 | `type:X::Adverb` | F11 | 3 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung556 | `type:X::Bind` | F11 | 3 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung557 | `type:X::Coerce` | F11 | 3 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung558 | `type:X::Constructor` | F11 | 3 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung559 | `type:X::Dynamic` | F11 | 3 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung560 | `type:X::IllegalOnFixedDimensionArray` | F11 | 3 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung561 | `type:X::InvalidType` | F11 | 3 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung562 | `type:X::NoDispatcher` | F11 | 3 | 0 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung563 | `type:X::NotEnoughDimensions` | F11 | 3 | 0 | 2 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung564 | `type:X::Seq` | F11 | 3 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung565 | `type:X::UnitScope` | F11 | 3 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung566 | `kw:warn` | F11 | 2 | 0 | 0 | bb_rk_control on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns and the box unwinds) |
| rung567 | `meth:exception` | F11 | 2 | 0 | 0 | bb_rk_control on the one exceptions protocol; CATCH is a bb_rk_block arm; Test is SETTING Raku |
| rung568 | `meth:rethrow` | F11 | 2 | 0 | 0 | bb_rk_control on ARCH-EXCEPTIONS-ONE-PROTOCOL (a raise returns and the box unwinds) |
| rung569 | `type:CX::Last` | F11 | 2 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung570 | `type:X::Backslash` | F11 | 2 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung571 | `type:X::Declaration` | F11 | 2 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung572 | `type:X::HyperOp` | F11 | 2 | 0 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung573 | `type:X::InvalidTypeSmiley` | F11 | 2 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung574 | `type:X::NoSuchSymbol` | F11 | 2 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung575 | `type:X::Package` | F11 | 2 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung576 | `type:X::Phaser` | F11 | 2 | 1 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung577 | `type:X::Pragma` | F11 | 2 | 0 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung578 | `type:X::Role` | F11 | 2 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung579 | `type:X::Signature` | F11 | 2 | 0 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung580 | `type:X::Temporal` | F11 | 2 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung581 | `type:X::Trait` | F11 | 2 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung582 | `meth:backtrace` | F11 | 1 | 0 | 0 | bb_rk_control on the one exceptions protocol; CATCH is a bb_rk_block arm; Test is SETTING Raku |
| rung583 | `meth:fail` | F11 | 1 | 0 | 0 | bb_rk_control on the one exceptions protocol; CATCH is a bb_rk_block arm; Test is SETTING Raku |
| rung584 | `test:unlike` | F11 | 1 | 0 | 0 | SETTING Raku (Test.rakumod, R10) over bb_rk_control and bb_call_fn |
| rung585 | `type:Backtrace` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung586 | `type:CX::Done` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung587 | `type:CX::Emit` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung588 | `type:CX::Next` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung589 | `type:CX::Proceed` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung590 | `type:CX::Redo` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung591 | `type:CX::Succeed` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung592 | `type:CX::Take` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung593 | `type:CX::Whatever` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung594 | `type:X::Anon` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung595 | `type:X::B` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung596 | `type:X::Buf` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung597 | `type:X::Caller` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung598 | `type:X::CompUnit` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung599 | `type:X::Composition` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung600 | `type:X::Control` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung601 | `type:X::EXPORTHOW` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung602 | `type:X::Enum` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung603 | `type:X::HTTP` | F11 | 1 | 0 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung604 | `type:X::Hash` | F11 | 1 | 0 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung605 | `type:X::IllegalDimensionInShape` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung606 | `type:X::Import` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung607 | `type:X::Item` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung608 | `type:X::Meow` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung609 | `type:X::Meows` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung610 | `type:X::NYI` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung611 | `type:X::NotParametric` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung612 | `type:X::PhaserExceptions` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung613 | `type:X::Placeholder` | F11 | 1 | 0 | 1 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung614 | `type:X::PoisonedAlias` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung615 | `type:X::Proc` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung616 | `type:X::PseudoPackage` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung617 | `type:X::Range` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung618 | `type:X::SecurityPolicy` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung619 | `type:X::Sequence` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung620 | `type:X::Subscript` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung621 | `type:X::TooLateForREPR` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung622 | `type:X::Value` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung623 | `type:X::Worry` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| rung624 | `type:X::Y` | F11 | 1 | 0 | 0 | SETTING Raku (the exception class) raised through bb_rk_control; bb_rk_type for the type check |
| **F12 smartmatch, junctions and boolean context** | | | | | | bb_rk_smartmatch (new: by the right operand kind, a kind switch box otherwise) and bb_rk_junction (new: autothreading as the box own alternation, collapse at boolean context) |
| rung625 | `op:~~` | F12 | 288 | 18 | 14 | bb_rk_smartmatch by the right operand kind |
| rung626 | `op:!~~` | F12 | 56 | 0 | 1 | bb_rk_smartmatch by the right operand kind |
| rung627 | `call:any` | F12 | 29 | 1 | 2 | bb_rk_smartmatch / bb_rk_junction |
| rung628 | `call:all` | F12 | 21 | 0 | 0 | bb_rk_smartmatch / bb_rk_junction |
| rung629 | `kw:so` | F12 | 18 | 0 | 0 | bb_rk_smartmatch / bb_rk_junction |
| rung630 | `call:one` | F12 | 13 | 0 | 0 | bb_rk_smartmatch / bb_rk_junction |
| rung631 | `call:none` | F12 | 12 | 0 | 1 | bb_rk_smartmatch / bb_rk_junction |
| rung632 | `type:Junction` | F12 | 8 | 0 | 0 | bb_rk_smartmatch / bb_rk_junction |
| **F13 regex, match objects and grammars** | | | | | | bb_match_rkrun / bb_match_rkcap / bb_match_rkland (existing) with the bb_match_* pattern family; rules are bb_call into pattern graphs; rx.c retires for Raku (R6) |
| rung633 | `regex:/` | F13 | 239 | 13 | 46 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung634 | `regex:m` | F13 | 51 | 0 | 2 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung635 | `kw:grammar` | F13 | 34 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung636 | `kw:token` | F13 | 31 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung637 | `kw:regex` | F13 | 30 | 0 | 1 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung638 | `regex:rx` | F13 | 27 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung639 | `meth:subst` | F13 | 25 | 0 | 1 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung640 | `kw:rule` | F13 | 24 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung641 | `meth:parse` | F13 | 24 | 0 | 3 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung642 | `meth:match` | F13 | 23 | 0 | 4 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung643 | `twigil:<` | F13 | 23 | 0 | 2 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung644 | `type:Match` | F13 | 20 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung645 | `regex:s` | F13 | 10 | 0 | 2 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung646 | `call:make` | F13 | 9 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung647 | `meth:from` | F13 | 9 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung648 | `meth:to` | F13 | 7 | 0 | 2 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung649 | `type:Regex` | F13 | 7 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung650 | `meth:ast` | F13 | 6 | 0 | 1 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung651 | `meth:subparse` | F13 | 6 | 0 | 1 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung652 | `meth:orig` | F13 | 4 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung653 | `type:Grammar` | F13 | 3 | 0 | 1 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung654 | `meth:make` | F13 | 2 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung655 | `meth:parsefile` | F13 | 2 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| rung656 | `meth:pos` | F13 | 2 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung657 | `meth:postmatch` | F13 | 2 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung658 | `meth:prematch` | F13 | 2 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung659 | `type:Cursor` | F13 | 2 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung660 | `meth:caps` | F13 | 1 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung661 | `meth:chunks` | F13 | 1 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung662 | `meth:made` | F13 | 1 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* family |
| rung663 | `regex:tr` | F13 | 1 | 0 | 0 | bb_match_rkrun / bb_match_rkcap / bb_match_rkland and the bb_match_* pattern family (R6); a rule is bb_call into a pattern graph |
| **F14 types, coercions, natives, enums and subsets** | | | | | | bb_rk_type (new) and bb_rk_coerce; native cells are planner cell kinds (bb_rk_native: the typed cell forms of box_cell_shapes.tsv) |
| rung664 | `type:Test::Util` | F14 | 136 | 23 | 15 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung665 | `kw:Any` | F14 | 86 | 0 | 19 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung666 | `kw:Mu` | F14 | 76 | 0 | 15 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung667 | `term:typeobject` | F14 | 52 | 52 | 23 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung668 | `type:X` | F14 | 28 | 0 | 9 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung669 | `kw:enum` | F14 | 20 | 0 | 4 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung670 | `kw:subset` | F14 | 13 | 0 | 1 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung671 | `word:int` | F14 | 11 | 0 | 2 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung672 | `word:uint8` | F14 | 11 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung673 | `type:Empty` | F14 | 10 | 0 | 5 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung674 | `meth:day` | F14 | 8 | 0 | 1 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung675 | `word:num` | F14 | 8 | 0 | 3 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung676 | `meth:now` | F14 | 6 | 1 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung677 | `meth:day-of-week` | F14 | 5 | 1 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung678 | `meth:month` | F14 | 5 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung679 | `meth:year` | F14 | 5 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung680 | `word:int64` | F14 | 5 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung681 | `meth:Instant` | F14 | 4 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung682 | `meth:days-in-month` | F14 | 4 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung683 | `meth:later` | F14 | 4 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung684 | `meth:truncated-to` | F14 | 4 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung685 | `word:int16` | F14 | 4 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung686 | `word:int32` | F14 | 4 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung687 | `word:int8` | F14 | 4 | 0 | 1 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung688 | `word:str` | F14 | 4 | 0 | 1 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung689 | `meth:Date` | F14 | 3 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung690 | `meth:DateTime` | F14 | 3 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung691 | `meth:earlier` | F14 | 3 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung692 | `meth:hour` | F14 | 3 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung693 | `meth:minute` | F14 | 3 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung694 | `type:Kept` | F14 | 3 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung695 | `word:uint` | F14 | 3 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung696 | `word:uint16` | F14 | 3 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung697 | `word:uint32` | F14 | 3 | 0 | 1 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung698 | `meth:is-leap-year` | F14 | 2 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung699 | `meth:offset` | F14 | 2 | 1 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung700 | `meth:second` | F14 | 2 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung701 | `meth:timezone` | F14 | 2 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung702 | `type:Broken` | F14 | 2 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung703 | `type:PROCESS` | F14 | 2 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung704 | `type:PredictiveIterator` | F14 | 2 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung705 | `type:SeekFromBeginning` | F14 | 2 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung706 | `word:byte` | F14 | 2 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung707 | `word:num32` | F14 | 2 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung708 | `word:num64` | F14 | 2 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung709 | `word:uint64` | F14 | 2 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung710 | `meth:day-of-year` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung711 | `meth:formatter` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung712 | `meth:hh-mm-ss` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung713 | `meth:posix` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung714 | `meth:week` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung715 | `meth:week-number` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung716 | `meth:week-year` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung717 | `meth:weekday-of-month` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung718 | `meth:whole-second` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung719 | `meth:yyyy-mm-dd` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung720 | `type:BigEndian` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung721 | `type:CompUnit` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung722 | `type:Deprecation` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung723 | `type:EXPORTHOW` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung724 | `type:Hyper` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung725 | `type:Planned` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung726 | `type:ProtocolFamily` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung727 | `type:SeekFromEnd` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| rung728 | `type:WalkList` | F14 | 1 | 0 | 0 | bb_rk_type / bb_rk_coerce; bb_rk_native cells |
| **F15 phasers and statement prefixes** | | | | | | bb_rk_phaser (new: ENTER, LEAVE, KEEP, UNDO, FIRST, NEXT, LAST on the block ports; BEGIN, CHECK, INIT, END at lowering and at the program ports) |
| rung729 | `kw:BEGIN` | F15 | 21 | 4 | 4 | bb_rk_phaser on the block ports |
| rung730 | `kw:END` | F15 | 18 | 1 | 0 | bb_rk_phaser on the block ports |
| rung731 | `kw:LEAVE` | F15 | 14 | 0 | 0 | bb_rk_phaser on the block ports |
| rung732 | `kw:quietly` | F15 | 13 | 1 | 1 | bb_rk_phaser on the block ports |
| rung733 | `kw:sink` | F15 | 9 | 0 | 3 | bb_rk_phaser on the block ports |
| rung734 | `kw:INIT` | F15 | 6 | 0 | 1 | bb_rk_phaser on the block ports |
| rung735 | `kw:ENTER` | F15 | 5 | 1 | 0 | bb_rk_phaser on the block ports |
| rung736 | `kw:LAST` | F15 | 5 | 0 | 0 | bb_rk_phaser on the block ports |
| rung737 | `kw:NEXT` | F15 | 5 | 0 | 1 | bb_rk_phaser on the block ports |
| rung738 | `kw:UNDO` | F15 | 4 | 0 | 0 | bb_rk_phaser on the block ports |
| rung739 | `kw:FIRST` | F15 | 3 | 0 | 1 | bb_rk_phaser on the block ports |
| rung740 | `kw:KEEP` | F15 | 3 | 0 | 0 | bb_rk_phaser on the block ports |
| rung741 | `kw:POST` | F15 | 2 | 0 | 0 | bb_rk_phaser on the block ports |
| rung742 | `kw:PRE` | F15 | 2 | 0 | 1 | bb_rk_phaser on the block ports |
| **F16 IO, processes and the environment** | | | | | | bb_rk_dispatch to rtx_rk_io_* (ASM leaves over the syscalls); NOT-A-BOX: a syscall is a leaf; the IO::Path and IO::Handle methods are SETTING Raku over the leaves |
| rung743 | `meth:parent` | F16 | 166 | 30 | 27 | bb_rk_dispatch to rtx_rk_io_parent (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung744 | `meth:add` | F16 | 163 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_add (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung745 | `meth:IO` | F16 | 40 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_io (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung746 | `meth:close` | F16 | 30 | 1 | 0 | bb_rk_dispatch to rtx_rk_io_close (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung747 | `meth:lines` | F16 | 27 | 0 | 3 | bb_rk_dispatch to rtx_rk_io_lines (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung748 | `meth:x` | F16 | 27 | 0 | 6 | bb_rk_dispatch to rtx_rk_io_x (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung749 | `call:open` | F16 | 26 | 1 | 0 | bb_rk_dispatch to rtx_rk_io_open (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung750 | `call:unlink` | F16 | 21 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_unlink (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung751 | `meth:absolute` | F16 | 21 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_absolute (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung752 | `meth:slurp` | F16 | 19 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_slurp (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung753 | `meth:open` | F16 | 17 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_open (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung754 | `call:run` | F16 | 16 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_run (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung755 | `meth:e` | F16 | 14 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_e (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung756 | `meth:spurt` | F16 | 13 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_spurt (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung757 | `type:IO::Path` | F16 | 13 | 1 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung758 | `meth:get` | F16 | 12 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_get (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung759 | `call:copy` | F16 | 11 | 0 | 3 | bb_rk_dispatch to rtx_rk_io_copy (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung760 | `meth:basename` | F16 | 10 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_basename (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung761 | `meth:d` | F16 | 10 | 0 | 1 | bb_rk_dispatch to rtx_rk_io_d (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung762 | `meth:out` | F16 | 10 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_out (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung763 | `meth:exitcode` | F16 | 9 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_exitcode (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung764 | `meth:path` | F16 | 9 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_path (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung765 | `meth:s` | F16 | 9 | 0 | 2 | bb_rk_dispatch to rtx_rk_io_s (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung766 | `meth:write` | F16 | 9 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_write (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung767 | `call:get` | F16 | 8 | 0 | 2 | bb_rk_dispatch to rtx_rk_io_get (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung768 | `call:sleep` | F16 | 8 | 0 | 1 | bb_rk_dispatch to rtx_rk_io_sleep (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung769 | `meth:is-absolute` | F16 | 8 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_is_absolute (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung770 | `type:IO::Handle` | F16 | 8 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung771 | `call:slurp` | F16 | 7 | 0 | 1 | bb_rk_dispatch to rtx_rk_io_slurp (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung772 | `meth:in` | F16 | 7 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_in (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung773 | `meth:sibling` | F16 | 7 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_sibling (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung774 | `meth:z` | F16 | 7 | 0 | 1 | bb_rk_dispatch to rtx_rk_io_z (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung775 | `call:close` | F16 | 6 | 0 | 2 | bb_rk_dispatch to rtx_rk_io_close (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung776 | `call:lines` | F16 | 6 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_lines (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung777 | `call:shell` | F16 | 6 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_shell (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung778 | `call:spurt` | F16 | 6 | 0 | 1 | bb_rk_dispatch to rtx_rk_io_spurt (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung779 | `meth:canonpath` | F16 | 6 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_canonpath (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung780 | `meth:child` | F16 | 6 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_child (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung781 | `meth:dirname` | F16 | 6 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_dirname (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung782 | `meth:err` | F16 | 6 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_err (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung783 | `meth:relative` | F16 | 6 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_relative (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung784 | `meth:resolve` | F16 | 6 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_resolve (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung785 | `meth:cleanup` | F16 | 5 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_cleanup (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung786 | `meth:f` | F16 | 5 | 0 | 1 | bb_rk_dispatch to rtx_rk_io_f (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung787 | `meth:mkdir` | F16 | 5 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_mkdir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung788 | `meth:read` | F16 | 5 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_read (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung789 | `meth:w` | F16 | 5 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_w (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung790 | `call:note` | F16 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_note (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung791 | `meth:encoding` | F16 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_encoding (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung792 | `meth:getc` | F16 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_getc (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung793 | `meth:is-relative` | F16 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_is_relative (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung794 | `meth:tmpdir` | F16 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_tmpdir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung795 | `meth:volume` | F16 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_volume (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung796 | `meth:words` | F16 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_words (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung797 | `type:IO::Spec::Win32` | F16 | 4 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung798 | `call:chdir` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_chdir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung799 | `meth:abs2rel` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_abs2rel (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung800 | `meth:catdir` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_catdir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung801 | `meth:catfile` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_catfile (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung802 | `meth:catpath` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_catpath (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung803 | `meth:curdir` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_curdir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung804 | `meth:devnull` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_devnull (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung805 | `meth:flush` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_flush (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung806 | `meth:nl-in` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_nl_in (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung807 | `meth:put` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_put (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung808 | `meth:rel2abs` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_rel2abs (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung809 | `meth:rootdir` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_rootdir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung810 | `meth:splitdir` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_splitdir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung811 | `meth:splitpath` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_splitpath (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung812 | `meth:unlink` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_unlink (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung813 | `meth:updir` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_updir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung814 | `type:IO::Path::Win32` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung815 | `type:IO::Socket::Async` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung816 | `type:IO::Spec::Cygwin` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung817 | `type:IO::Spec::Unix` | F16 | 3 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung818 | `call:dir` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_dir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung819 | `call:indir` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_indir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung820 | `call:mkdir` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_mkdir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung821 | `call:put` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_put (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung822 | `call:rmdir` | F16 | 2 | 0 | 1 | bb_rk_dispatch to rtx_rk_io_rmdir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung823 | `meth:accessed` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_accessed (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung824 | `meth:changed` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_changed (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung825 | `meth:chmod` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_chmod (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung826 | `meth:copy` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_copy (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung827 | `meth:dir` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_dir (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung828 | `meth:eof` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_eof (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung829 | `meth:l` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_l (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung830 | `meth:modified` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_modified (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung831 | `meth:nl-out` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_nl_out (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung832 | `meth:note` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_note (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung833 | `meth:r` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_r (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung834 | `meth:seek` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_seek (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung835 | `meth:signal` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_signal (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung836 | `type:IO::Path::Cygwin` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung837 | `type:IO::Path::Unix` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung838 | `type:IO::Socket::INET` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung839 | `type:Proc` | F16 | 2 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung840 | `call:chmod` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_chmod (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung841 | `call:getc` | F16 | 1 | 0 | 1 | bb_rk_dispatch to rtx_rk_io_getc (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung842 | `call:move` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_move (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung843 | `call:prompt` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_prompt (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung844 | `call:signal` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_signal (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung845 | `call:sleep-timer` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_sleep_timer (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung846 | `call:sleep-until` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_sleep_until (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung847 | `meth:extension` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_extension (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung848 | `meth:move` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_move (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung849 | `meth:pid` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_pid (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung850 | `meth:shell` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_shell (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung851 | `meth:spawn` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_spawn (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung852 | `meth:stdout` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_stdout (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung853 | `meth:tell` | F16 | 1 | 0 | 1 | bb_rk_dispatch to rtx_rk_io_tell (ASM leaf over the syscall; the syscall is NOT-A-BOX: a kernel entry) |
| rung854 | `type:IO::ArgFiles` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung855 | `type:IO::CatHandle` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung856 | `type:IO::Path::QNX` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung857 | `type:IO::Pipe` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung858 | `type:IO::Spec` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung859 | `type:IO::Spec::QNX` | F16 | 1 | 0 | 0 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| rung860 | `type:IO::Special` | F16 | 1 | 0 | 1 | bb_rk_dispatch to rtx_rk_io_* (ASM leaf over a syscall; the syscall itself is NOT-A-BOX: a kernel entry) |
| **F17 packages, modules, pragmas, EVAL and pod** | | | | | | NOT-A-BOX: a use, no, need, require, unit, module or package directive is lowered at compile time and runs nothing; EVAL is the compile-at-run-time road (runtime_eval and planner_rt_plan, R11); pod is data (R2); bb_call_proc_staged for an EVAL result |
| rung861 | `kw:EVAL` | F17 | 188 | 42 | 112 | NOT-A-BOX: the compile-at-run-time road (runtime_eval, planner_rt_plan), one road for every language (R11) |
| rung862 | `call:lib` | F17 | 159 | 0 | 0 | NOT-A-BOX: a loader or scope directive, lowered at compile time; nothing runs at the site |
| rung863 | `word:pod` | F17 | 136 | 20 | 72 | NOT-A-BOX: pod is data built by the lowerer as $=pod (R2); no box runs |
| rung864 | `op:::` | F17 | 77 | 0 | 34 | NOT-A-BOX: a loader or scope directive, lowered at compile time; nothing runs at the site |
| rung865 | `kw:module` | F17 | 38 | 0 | 2 | NOT-A-BOX: a loader or scope directive, lowered at compile time; nothing runs at the site |
| rung866 | `meth:EVAL` | F17 | 33 | 0 | 11 | NOT-A-BOX: the compile-at-run-time road (runtime_eval, planner_rt_plan), one road for every language (R11) |
| rung867 | `twigil:?` | F17 | 26 | 9 | 12 | NOT-A-BOX: a compile-time constant the lowerer substitutes ($?FILE, $?LINE, $?PACKAGE, $?BITS) |
| rung868 | `kw:package` | F17 | 21 | 0 | 8 | NOT-A-BOX: a loader or scope directive, lowered at compile time; nothing runs at the site |
| rung869 | `kw:need` | F17 | 6 | 0 | 3 | NOT-A-BOX: a loader or scope directive, lowered at compile time; nothing runs at the site |
| rung870 | `kw:import` | F17 | 4 | 0 | 2 | NOT-A-BOX: a loader or scope directive, lowered at compile time; nothing runs at the site |
| rung871 | `kw:unit` | F17 | 4 | 0 | 2 | NOT-A-BOX: a loader or scope directive, lowered at compile time; nothing runs at the site |
| rung872 | `word:comment` | F17 | 4 | 0 | 4 | NOT-A-BOX: lowered at compile time (a directive) or the compile-at-run-time road (EVAL) or data (pod) |
| rung873 | `kw:require` | F17 | 2 | 0 | 0 | NOT-A-BOX: a loader or scope directive, lowered at compile time; nothing runs at the site |
| rung874 | `twigil:=` | F17 | 2 | 0 | 0 | NOT-A-BOX: pod is data built by the lowerer as $=pod (R2); no box runs |
| rung875 | `twigil:~` | F17 | 2 | 0 | 1 | NOT-A-BOX: lowered at compile time (a directive) or the compile-at-run-time road (EVAL) or data (pod) |
| rung876 | `word:code` | F17 | 1 | 0 | 0 | NOT-A-BOX: lowered at compile time (a directive) or the compile-at-run-time road (EVAL) or data (pod) |
| rung877 | `word:config` | F17 | 1 | 0 | 0 | NOT-A-BOX: lowered at compile time (a directive) or the compile-at-run-time road (EVAL) or data (pod) |
| **F18 dynamics, introspection and the call frame** | | | | | | bb_var_frame with rtx_rk_dynfind (ASM leaf walking the dynamic chain for $*X); .WHAT, .WHO, .HOW, .VAR, .DEFINITE are bb_rk_type reads; callframe and Backtrace read ARCH-GC section 13 chain |
| rung878 | `twigil:*` | F18 | 213 | 2 | 171 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung879 | `type:Perl` | F18 | 33 | 0 | 29 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung880 | `meth:VAR` | F18 | 20 | 0 | 12 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung881 | `type:DateTime` | F18 | 11 | 0 | 1 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung882 | `type:Date` | F18 | 10 | 0 | 5 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung883 | `type:Duration` | F18 | 9 | 0 | 1 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung884 | `type:Instant` | F18 | 6 | 0 | 6 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung885 | `type:Stash` | F18 | 6 | 0 | 6 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung886 | `type:Raku` | F18 | 5 | 0 | 5 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung887 | `meth:DEFINITE` | F18 | 4 | 0 | 3 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung888 | `type:CallFrame` | F18 | 1 | 0 | 1 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung889 | `type:Dateish` | F18 | 1 | 0 | 1 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung890 | `type:Rakudo` | F18 | 1 | 0 | 1 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| rung891 | `type:Version` | F18 | 1 | 0 | 1 | bb_var_frame with rtx_rk_dynfind (ASM leaf); bb_rk_type for the reads |
| **F19 sets, bags and mixes** | | | | | | bb_rk_sets (new: the QuantHash family) over bb_rk_aggr; the set operators through bb_rk_hyper |
| rung892 | `call:set` | F19 | 18 | 0 | 6 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung893 | `op:(|)` | F19 | 17 | 0 | 11 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung894 | `meth:Bag` | F19 | 10 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung895 | `meth:Set` | F19 | 10 | 0 | 1 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung896 | `op:(.)` | F19 | 10 | 0 | 8 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung897 | `meth:BagHash` | F19 | 9 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung898 | `meth:Mix` | F19 | 9 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung899 | `meth:MixHash` | F19 | 9 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung900 | `meth:SetHash` | F19 | 9 | 0 | 1 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung901 | `type:BagHash` | F19 | 9 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung902 | `type:Set` | F19 | 8 | 0 | 3 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung903 | `type:SetHash` | F19 | 8 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung904 | `call:bag` | F19 | 7 | 0 | 1 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung905 | `type:Bag` | F19 | 7 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung906 | `meth:total` | F19 | 6 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung907 | `type:MixHash` | F19 | 6 | 0 | 1 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung908 | `op:∪` | F19 | 5 | 0 | 1 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung909 | `type:Mix` | F19 | 5 | 0 | 2 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung910 | `call:mix` | F19 | 3 | 0 | 2 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung911 | `op:(&)` | F19 | 3 | 0 | 1 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung912 | `op:(+)` | F19 | 3 | 0 | 1 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung913 | `op:(-)` | F19 | 3 | 0 | 1 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung914 | `op:⊆` | F19 | 3 | 0 | 1 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung915 | `op:(^)` | F19 | 2 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung916 | `op:(cont)` | F19 | 2 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung917 | `op:(elem)` | F19 | 2 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung918 | `op:∈` | F19 | 2 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung919 | `op:∉` | F19 | 2 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung920 | `op:∋` | F19 | 2 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung921 | `op:∩` | F19 | 2 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung922 | `op:⊂` | F19 | 2 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung923 | `op:⊃` | F19 | 2 | 0 | 0 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung924 | `op:⊇` | F19 | 2 | 0 | 1 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| rung925 | `meth:Setty` | F19 | 1 | 0 | 1 | bb_rk_sets over bb_rk_aggr; bb_rk_hyper for the operators |
| **F20 concurrency (S17), HELD on Lon word** | | | | | | NOT-A-BOX: held; Promise, Supply, Channel, start, await, react, whenever, Lock, Proc::Async ride the thread runtime when Lon opens S17 (R11) |
| rung926 | `kw:start` | F20 | 12 | 82 | 86 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung927 | `kw:await` | F20 | 8 | 0 | 2 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung928 | `meth:tap` | F20 | 5 | 0 | 0 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung929 | `type:Promise` | F20 | 5 | 0 | 1 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung930 | `meth:keep` | F20 | 4 | 0 | 0 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung931 | `meth:result` | F20 | 4 | 0 | 2 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung932 | `meth:emit` | F20 | 3 | 0 | 0 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung933 | `meth:act` | F20 | 2 | 0 | 0 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung934 | `meth:break` | F20 | 2 | 0 | 0 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung935 | `meth:send` | F20 | 2 | 0 | 0 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung936 | `meth:then` | F20 | 2 | 0 | 1 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung937 | `type:Channel` | F20 | 2 | 0 | 0 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung938 | `type:Supplier` | F20 | 2 | 0 | 2 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung939 | `call:done` | F20 | 1 | 0 | 0 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung940 | `call:emit` | F20 | 1 | 0 | 1 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung941 | `kw:react` | F20 | 1 | 0 | 0 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung942 | `kw:supply` | F20 | 1 | 0 | 1 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung943 | `kw:whenever` | F20 | 1 | 0 | 0 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung944 | `meth:receive` | F20 | 1 | 0 | 1 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung945 | `type:CurrentThreadScheduler` | F20 | 1 | 0 | 0 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung946 | `type:HyperSeq` | F20 | 1 | 0 | 1 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung947 | `type:Lock` | F20 | 1 | 0 | 1 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung948 | `type:Proc::Async` | F20 | 1 | 0 | 1 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung949 | `type:Tap` | F20 | 1 | 0 | 1 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |
| rung950 | `type:ThreadPoolScheduler` | F20 | 1 | 0 | 1 | NOT-A-BOX: HELD on Lon word (S17 rides the thread runtime when opened) |

## 5. THE MAP (`corpus/tests/raku/config/ROAST-RUNG-MAP.tsv`: program, first rung, unblock rung, outcome, basis, construct; 1,225 rows)

Every program of the snapshot is on a declared rung (the baton's DONE-WHEN reads it). THE EXCLUSION CLASSES, said here as the baton asks: (1) the 63 NO_ORACLE_ANSWER files are already out of the denominator (`EXCLUDED.tsv`) and are not in the map; (2) the 82 programs whose first block is an F20 rung (S17-supply 51, S17-promise, S17-channel, S17-procasync, S17-scheduler, S07-hyperrace, and the `start`/`await` users elsewhere) are HELD on Lon's word (R11: concurrency rides the thread runtime when Lon opens it, or is his exclusion); they stay in the map at their F20 rung and in the denominator until Lon rules, so the ladder's 100 is 1,401 minus whatever Lon excludes, never minus what is merely hard; (3) a program whose chapter is `6.c`, `6.d` or `APPENDICES` is a version variant placed by the same rule as its base chapter; the one Perl-5 file (`S01-perl-5-integration`) is placed at F17 and will be an EXCLUDED line if rakudo's own answer is a refusal. RakDemo (Rakudo's grammar demonstration) reads 100 at its last reading; when it reds, hq_raku runs the generator over its red set with `--snapshot` and the programs land where their constructs fall (F13 for the grammar), no second rule.

## 6. THE BUILD: incremental, by family lanes in the dependency order, one rung one landing, the kernel box born with its family's first rung

- ONE RUNG IS ONE LANDING: the rung's forms (its ladder entries in the RakRungs master, `ladder__rungNNN_<slug>_<form>`, each at most 20 lines, the ref cut from rakudo 2026.05, proven red before the cure against a corrupted ref, CEO-1680) plus THE HANDFUL: at most eight of the Roast programs the rung first-blocks, both modes, then a TEST REQUEST for the rest of them and for the RakRungs core; the Raku smoke before every push (CEO-1928); a shared-template change smokes all eight languages. Rung N+1 of a family opens when rung N is green in both modes; FAMILIES run as parallel lanes once their dependencies are green (F01 and F02 first and alone; F03 to F06 after F02; F07 after F06; F08, F09 after F07's `bb_rk_iter`; F10 to F12 after F05; F13 after F12; F14, F15 after F10; F16 to F19 after F11; F20 held), so three or four seats walk the ladder at once without stepping on one template.
- THE KERNEL BOX IS BORN SMALL ONCE (CEO-1478): the family's first rung lands the family's box with the one arm that rung needs, the smoke and the identity (the coo's), then the rungs behind it grow the arms; a box is never landed whole ahead of a rung that proves it. The C road a rung replaces is DELETED IN THE SAME LANDING (CEO-2045: a deletion carries its re-expression), and the leaf census line beside the landing says what the deletion bought.
- WHO BUILDS: hq_raku walks the rungs of every family (one program at a time, CEO-1926); the KERNEL BOXES that need the machine's officers are built by the cao at the family's first rung and handed to hq_raku (`bb_rk_sig` and `bb_rk_dispatch` at F05, `bb_rk_iter` and `bb_rk_aggr` at F07, `bb_rk_control` on the one protocol at F11, `bb_rk_type` at F10), the cfo places the cells (`bb_rk_scalar`'s container cells and REFs at F02, the native cell kinds at F14, the escape boundary's heap handle at F07), hq_runtime builds the ASM leaves under its CEO-1682 row re-pointed to this page (F08 strings, F09 numerics, F16 IO) and runs the leaf census after each family, the coo grades; when hq_raku flounders on a rung (the fleet plan rates the risk HIGH) the row escalates to the cao, never to the cto (CEO-2029), and the cto answers a design gap on this page. THE SETTING LOADER (§ 1.2 (c)) is step 0, the cao's, with `Test.rakumod` as its first file and the C Test arms deleted the same day.
- RakRungs AND RakBench STAY GREEN AT EVERY LANDING: the Raku smoke is the landing's gate, the RakRungs core partition the lander's request, and RakBench's kernels are the leaf census's population, so a landing that moves an instruction count up is seen by the census it is measured with; a red in either is cured or reverted within the tick (CEO-1928).

## 7. THE TWELVE REWRITE STEPS AND THE PRESENT ROADS, PLACED BY NAME (ARCH-RAKU-REWRITE.md is SUPERSEDED by this page; nothing of it is followed except as kept here)

| of the rewrite | fate | reason |
|---|---|---|
| R1 every name declared by the lowerer | FOLDED into F02 and F17 (rung035 `decl:sigilless`, rung039 `decl:list`, rung667 `term:typeobject`, rung867 `twigil:?`) | the refusal classes are rungs with programs on them, not a blanket rule |
| R2 pod is data | KEPT (F17 rung863 `word:pod`, NOT-A-BOX: data) | `$=pod` is built by the lowerer from the tree; no box runs |
| R3 a container exists where the program asks | KEPT as § 1.1 (F02, `bb_rk_scalar`) | the lifetime rule's own shape |
| R4 a role is a template | KEPT (F10, `bb_rk_type`'s composition at lowering) | measured divergence (1,2,1 against 1,2,3) |
| R5 the Seq machine is the generator road | KEPT (F07, `bb_rk_iter` over `bb_suspend`; the escape boundary CEO-1619) | lazy by construction; the eager array desugar is deleted |
| R6 a regex is a pattern graph, rx.c retires | KEPT (F13, the `bb_match_*` family; backtracking boxes, not an NFA, CEO-1602) | the boxes exist; the rungs wire the rest |
| R7 an exception unwinds by the frame walk | SUPERSEDED by ARCH-EXCEPTIONS-ONE-PROTOCOL (F11, `bb_rk_control`) | a raise RETURNS and the box unwinds through the planned discards: one protocol for every language, R8 of ARCH-ZETA-LAYOUT |
| R8 dispatch is resolved or tabled | KEPT (F05 and F10, `bb_rk_dispatch`; the table from the setting's classes) | never a by-name search |
| R9 smartmatch, junctions, metaoperators are boxes | KEPT (F12 and F03, `bb_rk_smartmatch`, `bb_rk_junction`, `bb_rk_hyper`) | |
| R10 Test is a Raku module SCRIP compiles | KEPT AND GENERALIZED: THE SETTING IN RAKU (§ 1.2 (c)), Test.rakumod its first file | the same mechanism carries every core class |
| R11 EVAL stays; concurrency rides the thread runtime or is Lon's exclusion | KEPT (F17 rung861 NOT-A-BOX: the compile-at-run-time road; F20 HELD) | |
| R12 the finish is half of Roast | SUPERSEDED | the finish is the denominator |
| `lower_raku.c`'s `IR_CALL` by name (34 sites), `rk_lower_iter_meth`'s special cases, the merge sort written as a Raku sub | DELETED, family by family, each site with the rung that re-expresses it | the C interpreter road |
| the parser's desugars (`rk_desugar_gather`, `rk_take_rewrite`, `__rk_seq`, `__rk_smartmatch`, `nctx`'s `.elems`, the `__rk_jct_*` and `__multi_call` forms) | DELETED with their rungs (F07, F12, F01, F03, F05) | CEO-1715: the tree does not desugar |
| `bb_match_rkrun`, `bb_match_rkcap`, `bb_match_rkland`, the `IR_GLIT`/`IR_GCC`/`IR_GALT` grammar boxes | KEPT (F13) | the Raku boxes that exist |
| `rk_case_table.h`, `rk_unicode_norm_tables.inc`, `rk_core_names.h`, `rk_rakudo_method_names.inc` | KEPT as DATA the leaves and the lowerer read | tables are not logic |

## 8. THE C ROADS AND THEIR FATES (named from the recorded census, SCORE.md sha e71e5253b, and the lowering census; the fresh ranking is hq_runtime's first act under this page: `util_runtime_leaf_census.sh --mode m4 --top 60` over the RakBench kernels, its LEAF_C lines appended to § 8.1 with a fate each by the rule below)

THE RULE OF FATES: a function that DECIDES (dispatches, loops over user code, selects by kind, collapses, binds) becomes a BOX; a function that COMPUTES a value with no control flow of the program's (a string primitive, a numeric primitive, a hash) becomes an ASM LEAF declared in the entry table; a function that ENTERS THE KERNEL (a syscall) or COMPILES AT RUN TIME stays a leaf and is NOT-A-BOX with that reason; a C function that is a TABLE is data. THE DESTINATION: `LEAF_SHARE lang=raku mode=m4 c_runtime` under 10 (CEO-1682's row, re-pointed to this page as its DONE-WHEN), read after every family.

| C road (today) | fate | by |
|---|---|---|
| `try_call_builtin_by_name_bl_s_rq`, `script_try_call_builtin_by_name_rq`, `rt_call_arr_bl_s`, `rt_call_arr_impl`, `rt_call_arr_bl` (the by-name call road: ranks 1 to 5, 24 to 25 G inclusive, the two dispatchers 8.1 G of self cost) | DELETED for Raku: every call resolves at lowering to a box, a setting method through `bb_rk_dispatch`, or a declared leaf | F05, F10 |
| `rt_str_method` (101 `strcmp` compares), `rk_list_more_methods`, `rk_io_path_method`, `meth_call`, `obj_new` | BOX `bb_rk_dispatch` over the setting's per-type table; the method bodies SETTING Raku over `rtx_rk_str_*`, `bb_rk_iter`, `rtx_rk_io_*` | F05, F07, F08, F16 |
| `__multi_call` | BOX `bb_rk_dispatch` (R8) | F05 |
| `__rk_jct_*`, `junction_collapse` | BOX `bb_rk_junction` | F12 |
| `__rk_smartmatch` | BOX `bb_rk_smartmatch` | F12 |
| `rk_sequence` (eager, capped) | BOX `bb_rk_iter` over `bb_suspend` (R5) | F07 |
| `re_match`, `re_matchx`, `rx.c` (22 RX_ALLOC sites, eight shapes), `grammar_parse_core` | BOXES: the `bb_match_*` family and `bb_match_rk*`; rx.c retires for Raku (R6) | F13 |
| the Test C arms (`plan`, `ok`, `is`, `throws-like`, `dies-ok`, `subtest`, `is-deeply`, `done-testing`) | SETTING Raku: `Test.rakumod` (R10) | step 0 |
| `rk_write`, `rk_writes`, `rk_write_list`, `rk_write_arr` | ASM LEAF `rtx_rk_io_write` under `bb_rk_dispatch`; the formatting (gist, Str) SETTING Raku | F16 |
| `rk_while_cond`, `rk_until_cond`, `rk_repeat_cond`, `rk_repeat_body`, `rk_loop_body`, `rk_cloop_incr`, `rk_cloop_cond` | DELETED: the loops are `bb_to` and `bb_gate` wirings with `bb_rk_coerce` on the condition | F04 |
| `rk_rat.c`, `bignum.c` (for Raku's Rat and big Int) | ASM LEAVES `rtx_rk_rat_*`, `rtx_rk_bigint_*` under `bb_rk_num` | F09 |
| `rt_gc_poll_asm`, `rt_gc_poll_slow`, `gc_point_arr_*`, `gc_collect_ex` (ranks 6 to 10: the collector, 6.1 G on 14 programs) | NOT-A-BOX: the collector; its share falls as the by-name road's allocations go, and it is the collector's own rows | hq_collector |
| the string primitives behind `uc`, `lc`, `substr`, `index`, `split`, `comb`, `trim`, `sprintf`, `ord`, `chr`, NFG and normalization | ASM LEAVES `rtx_rk_str_*` over the two tables | F08, hq_runtime |
| the IO primitives behind `open`, `slurp`, `spurt`, `lines`, `dir`, `mkdir`, `unlink`, `run`, `shell`, `Proc` | ASM LEAVES `rtx_rk_io_*`; NOT-A-BOX: a syscall | F16, hq_runtime |
| `runtime_eval.c` for `EVAL` | NOT-A-BOX: the compile-at-run-time road, one for every language (R11) | F17 |
| the `[SMX]` refusal in `scrip.c` | DELETED with F02's rungs: the lowerer declares every name, the emitter refuses nothing a Roast file reads | F02 |

**8.1 The fresh ranking (appended by hq_runtime from the census; each line a fate by the rule).** PENDING: the cto runs nothing heavy; the request is telegrammed with this page.

## 9. THE ROWS (minted by the cto 13:0x CDT; executors by § 6; every DONE-WHEN reads results.tsv through the ladder instrument, which is the first row)

THE INSTRUMENT `harness/scripts/util_raku_ladder_status.py` (hq_raku's first landing, a read): reads `LADDER.tsv`, `ROAST-RUNG-MAP.tsv` and `results.tsv`; `--family F01,F02` prints per rung GREEN (every form PASS in both modes at the latest reading) or RED with its first red form, the programs first-blocked there and where they stand now; `--replace` rewrites the map's first-block column for programs whose rung is green (the next red rung among their features, by the generator's data; the unblock column never moves); `--green` exits 0 when every declared rung of the named families is GREEN; `--count` prints Roast PASS of the denominator from results.tsv. A rung's forms are the master's `ladder__rungNNN_*` entries; a rung with no form yet is RED by definition (the work list).

| row | executor | DONE-WHEN reads |
|---|---|---|
| `raku-ladder-step-0-the-ladder-instrument-util-raku-ladder-status-reads-the-rungs-and-replaces-the-map-ceo-2044` | hq_raku | `util_raku_ladder_status.py --family F01 --count` runs and prints the 930 rungs' states and the Roast count |
| `raku-ladder-step-1-the-setting-in-raku-the-loader-and-test-rakumod-as-its-first-file-ceo-2044` | cao | `test_gate_raku_test_module_is_setting_raku.sh`: a witness using plan, ok, is, throws-like, dies-ok, subtest runs with Test from the setting in both modes, the C Test arms are gone from by_name_dispatch.c (grep), the Raku smoke green |
| `raku-ladder-f01-f02-the-value-model-literals-containers-and-declarators-rungs-021-to-042-ceo-2044` | hq_raku (the cfo for the container cells) | `util_raku_ladder_status.py --family F01,F02 --green` |
| `raku-ladder-f03-f04-operators-and-control-flow-rungs-043-to-107-ceo-2044` | hq_raku | `--family F03,F04 --green` |
| `raku-ladder-f05-f06-subs-signatures-dispatch-and-blocks-rungs-108-to-154-ceo-2044` | cao (`bb_rk_sig`, `bb_rk_dispatch`, `bb_rk_block`), hq_raku the rungs | `--family F05,F06 --green` |
| `raku-ladder-f07-lists-arrays-hashes-and-the-iterator-rungs-155-to-275-ceo-2044` | cao (`bb_rk_iter`, `bb_rk_aggr`), hq_raku the rungs, the cfo the escape boundary | `--family F07 --green` |
| `raku-ladder-f08-f09-strings-and-numerics-rungs-276-to-466-ceo-2044` | hq_runtime (the ASM leaves), hq_raku (the setting methods) | `--family F08,F09 --green` |
| `raku-ladder-f10-f12-classes-exceptions-and-smartmatch-rungs-467-to-632-ceo-2044` | cao (`bb_rk_type`, `bb_rk_control`), hq_raku the rungs | `--family F10,F11,F12 --green` |
| `raku-ladder-f13-regex-match-objects-and-grammars-rungs-633-to-663-ceo-2044` | hq_raku | `--family F13 --green` |
| `raku-ladder-f14-f15-types-natives-enums-subsets-and-phasers-rungs-664-to-742-ceo-2044` | hq_raku (the cfo for the native cells) | `--family F14,F15 --green` |
| `raku-ladder-f16-f19-io-packages-dynamics-and-sets-rungs-743-to-925-ceo-2044` | hq_runtime (the IO leaves), hq_raku | `--family F16,F17,F18,F19 --green` |
| `raku-ladder-the-c-share-the-leaf-census-after-every-family-and-the-road-deletions-ledger-ceo-2044` | hq_runtime (CEO-1682's row re-pointed) | `LEAF_SHARE lang=raku mode=m4` c_runtime under 10 on SCORE.md; § 8.1 filled |
| F20 | none: HELD | the ceo's EXCLUDED line or Lon's word opens it |

THE ORDER: step 0 and step 1 first (the instrument and the setting loader), then F01-F02 alone, then the lanes as § 6's dependencies allow; the census row runs beside them from the first family. A row's rank is Raku's (rank 9 for building, CEO-1931) under Lon's order of this day; a step that founders escalates to the cao.

## 10. What a builder must not do

- Lower a construct to a C function by name; add an `IR_CALL <name>` to `lower_raku.c`; add a `strcmp` chain or a by-name table lookup on any Raku path; add a desugar to `rk_tree.c` or `rk_syntax.c`.
- Write a core method in C that the setting can write in Raku; write a leaf in C that ASM can carry; let a leaf call a box or loop over user code (CEO-1576); keep a C road a rung has re-expressed (the deletion lands with the box).
- Build a kernel box whole ahead of a rung that proves it; land a rung without its forms' refs cut from rakudo 2026.05 and proven red against a corrupted ref; cure a Roast file by its name instead of by its rung; test a feature on top of one that is not yet green (Lon's direction of 10-29).
- Move RakRungs or RakBench below 100 at any landing; publish a Raku number from anything but results.tsv and the LEAF_SHARE line; count by wall clock.
- Touch S17 before Lon opens it; place a program off the map by hand (the generator and the instrument place; a hand edit to the map is a second rule).
- Add a global, a side table, a frame marker, a second stack, a stack held by the runtime, a fixed limit a program can reach (the ABSOLUTE rules stand under Raku as under every language).
