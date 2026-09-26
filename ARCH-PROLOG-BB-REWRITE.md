# ARCH-PROLOG-BB-REWRITE — Prolog redesigned from scratch as Byrd boxes (hq_prolog, 2026-09-26)

**Lon, in-chat to hq_prolog, 2026-09-26, verbatim:** *"You are to re-design Prolog from scratch using Byrd Boxes."* · to the ceo 13:5x, verbatim: *"HQ-PROLOG is on a COMPLETE RE-WRITE using Byrd Boxes versus C functions."* · 12:1x: *"The bar is the compiler."* · 10:2x: *"The Prolog unification needs to mirror SNOBOL4's pattern matching, using R13, R14, and R15, and also R12 as a stack."* · 10:5x: *"The R12 push and pop should be inlined, and just a few instructions."*

**What this page is.** The design is drawn fresh from three sources: Byrd's four ports, Proebsting's rule that each port is a compile-time chunk that holds its operator's logic, and the SNOBOL4 matcher already emitted by this compiler. The design does not start from `lower_prolog.c`. **The implementation lands in place, one rung at a time.** Each rung replaces one mechanism, deletes the C it replaces in the same landing, and holds every Prolog suite at its floor. Big-bang replacement is refused because a rewrite that is red for a month is unmeasurable for a month.

**Where it sits.** This page supersedes the *mechanism* sections of `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` (§ A.1 frame offsets, § B.11 trail, § B.9 meta-call, § B.15 database) wherever they differ. It keeps that page's port correspondence (§ A), its per-construct wiring (§ B.1–B.8, B.10, B.14, B.17) and its literature (§ G). The census it answers is `findings/FINDING-2026-09-26-ceo-prolog-byrd-box-score-…md` (§ H there). Two numbered counts appear below; each names the instrument and tree it came from, and every other count is left to the instrument.

---

## 0. The one rule

**A box's logic is inside its chunk.** A `call` from emitted Prolog code into C or rtx is legal only for a **value service**: a function over finished values that neither binds, trails, derefs, opens or cuts a choice, carves a frame, nor decides a port. The value services are I/O (`write`, `format`, streams), atom and string text operations, `sort`/`msort`/`keysort`, bignum and float arithmetic, `copy_term`, and ISO error-ball construction. Everything else is emitted: unification, dereference, binding, the trail push and unwind, term construction, the frame, choice open and cut, clause selection, small-integer arithmetic and comparison, type tests, meta-call dispatch and the dynamic database.

The instrument is `scripts/bench_prolog_call_census.sh REGEX`. Each rung's DONE-WHEN is its regex reading zero over the 23 kernels. The speed criterion is `scripts/bench_prolog_bar.sh kernel K 1.0 gplc`.

---

## 1. The cell — the term representation, redesigned for inline code

A term is a 16-byte `DESCR_t`. The tag byte is the collector's only tag (THE COLLECTOR, CEO-812). Equality and type tests must be one or two instructions, so every atomic kind carries its whole identity in the tag byte plus the value qword.

| kind | tag `v` | `slen` (+4) | value (+8) | test |
|---|---|---|---|---|
| unbound variable | `DT_PLVAR` | 0 | its own address | `cmp byte [c],DT_PLVAR; jne nv; cmp [c+8],c; je unbound` |
| bound reference | `DT_PLVAR` | 0 | the target cell | the deref loop follows it |
| atom | **`DT_PLATOM` (new, `0xB0`)** | 0 | atom id | `cmp byte [c],DT_PLATOM; jne; cmp qword [c+8],imm32` |
| small integer | `DT_I` | 0 | int64 | `cmp byte [c],DT_I; jne; cmp qword [c+8],imm` |
| float | `DT_R` | 0 | double | value service beyond `=:=`/`<` |
| big integer | `DT_BIG` | — | pointer | value service |
| string | `DT_S` | length | `char *` | value service |
| compound | `DT_PLREF` | **functor id (32 bits)** | pointer to the argument block | `cmp byte [c],DT_PLREF; jne; cmp dword [c+4],imm32` |

**Atoms stop being `DT_S` strings and stop colliding with `DT_A`.** Today atom literals are lowered to `DT_S` char pointers (`lower_prolog.c` `term_e`), and atom equality is a `strcmp` (`by_name_dispatch.c` `plw_unify_cells`). The builder form `DT_A` also collides with the SNOBOL4/Icon array tag, and survives in the collector only by coincidence (`gc_heap.c` DT_A case). The new tag is free (`src/ir/descr.h` enum).

**The compiler interns.** Every atom and functor the compiler sees gets its id at compile time. The ids go into a read-only table in the code slab: id → name, arity, operator class and priority. `module_init` registers the table with the one runtime interner, so an atom made at run time (`atom_codes/2`, `read/1`) resolves to the same id. Nothing is interned by its characters on a hot path. That closes the crypt row (16% in `prolog_atom_intern`), and the table's operator columns close the deriv row: `write/1` reads a functor's operator class from the table in one load, not from the parser's tables per node.

**The functor id is 32 bits in `slen`, and the arity comes from the table.** The 16-bit caps on both fields go away.

**The argument block** is one collector block of `arity` DESCRs (`HB_DVEC`). A list cell is `'.'/2`, and `[]` is the atom `'[]'`.

**⭐ Every variable cell lives in the heap. A frame slot holds a VALUE and is never bound.** This is the decision the rest of the design stands on.
- A clause variable's first occurrence either takes the incoming argument's DESCR (head) or allocates a fresh self-referencing cell (body; one 16-byte bump in the emitted allocation sequence, § 7). Every later occurrence reads the frame slot's DESCR, which may be a reference to that heap cell.
- Consequences:
  - No pointer anywhere points into an activation frame. Last call and deterministic frame release are always safe without an unsafe-variable analysis.
  - The trail records heap cells only, and the collector already relocates it (`gc_heap.c` trail root range).
  - The trail entry shrinks to one word (§ 3).
- The cost is one bump allocation per body-only variable. It replaces today's two mechanisms that each do the same thing later and in C: `plw_bind`'s boxing of a frame cell, and `plw_mkc_kids`' globalising of an unbound kid.
- ⚠ This is a heap allocation of *structure* in the sense of the CLAUDE.md digest ("only string values belong on the heap"). It is also exactly the "compound cells" carve-out of `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § rule 2(e). It is asked as § 13 Q1.

---

## 2. The register plane

| register | during head unification and body construction (the match plane) | between them |
|---|---|---|
| `r12` | **TR, the trail top**: the CAS twin (§ 3) | TR (always) |
| `r13` | **Σ, the base of the cells being walked**: `&F.A[0]` at the head, an argument block inside a structure | free for box scratch |
| `r14` | **δ, the cursor**: a byte offset, advanced by 16 per cell | free for box scratch |
| `r15` | **Δ, the end**: `16 × arity` | free for box scratch |
| `rbx` | the heap frontier (`PIN_FRONTIER_REG`); the emitted allocation sequence bumps it | same |
| `rbp` | the pinned activation frame | same |
| `r10` / `r11` | statement number / BB node id (Lon 2026-09-02) — untouched | same |

This is exactly the SNOBOL4 plane (`x86_asm.h` `PIN_*` asserts), so r13/r14/r15 carry the same *kind* in every language. The collector's register shield needs no per-language reading, which the 2026-09-20 finding on r15 asked for.

**B, HB and the ball leave the registers.** They move into the trail arena's own header, which is reached from `r12` (`and rax, -(1<<PL_TR_ARENA_LG2)`), and the header already carries the ball at `+8` (`PL_TR_BALL_SLOT`). The layout becomes `+0` top word · `+8` ball · `+16` B · `+24` HB.
- They are the trail box's own state, not ζ-STANDING and not a global: the 2026-09-02 sixth ruling forbids engine state in ζ-STANDING, and the arena's only handle is `r12`.
- Reaching them costs one `mov`/`and` pair per use. The uses are choice open, cut and ω, plus the bind, which reads HB.
- § 13 Q2 asks whether Lon prefers a pinned VA (the `RT_DCAP_TOP` precedent, one instruction).

**ROOT** (today `r14`: the dynamic-database cells at `[r14-24-8k]`) becomes the root frame's address, reached the same way at `+32`.

---

## 3. The trail — the CAS twin, pushed and popped inline

**Entry.** A binding always overwrites an unbound heap cell, whose old value is reconstructible (a self reference). So a binding's entry is **one word: the cell's address**. A value-trail entry is three words, `{addr|1, old.lo, old.hi}`; it is used by `setarg/3`, `b_setval/2` and anything else that overwrites a bound value backtrackably, and bit 0 tells the two kinds apart.

**Bind** (the WAM condition, the choice's heap mark). Four instructions in the common case: compare with HB, push, store tag, store value.
```
    ; rdi = unbound heap cell, value in rax:rdx
    mov  rcx, r12 ; and rcx, -ARENA ; cmp rdi, [rcx+24]  ; HB
    jae  1f                          ; younger than the youngest choice: no entry
    mov  [r12], rdi ; add r12, 8     ; THE PUSH
1:  mov  [rdi], rax ; mov [rdi+8], rdx
```

**Unwind to a mark** (the pop), inline, a loop of seven instructions:
```
2:  cmp  r12, MARK ; jbe 3f
    sub  r12, 8 ; mov rdi, [r12]
    test dil, 1 ; jnz value_entry     ; cold arm: restore 16 bytes, pop 2 more words
    mov  byte [rdi], DT_PLVAR ; mov [rdi+8], rdi ; jmp 2b
3:
```

**HB under a moving collector.** A copying collection does not preserve address order. The collector therefore raises HB and every retained frame's saved `F.HB` to the post-collection frontier. Every surviving cell then reads as older than every choice (sound: it only over-trails), and every cell allocated after the collection reads as younger (correct). That is one typed visit per frame header (the frame map already names `F.HB`), and it belongs to the cfo's collector review.

**Overflow.** The arena refuses with a named limit (`rt_pl_tr_refuse`, exit 2), as today. Growing it is a later rung.

**Deleted by this rung:** `plw_bind`, `pl_tr_push`, `pl_tr_needs_log`, `rt_pl_tr_unwind`, `rt_pl_tr_unwind_to` and `rt_pl_tr_unwind_sync`, which is the rank-0 row's DONE-WHEN exactly. `rt_pl_tr_gc_sync` also goes: `r12` is spilled by the one collector entry the poll already reaches.

---

## 4. The predicate box

One predicate `p/n` is one box. Its α is the call port, its β the redo port, and γ/ω are the caller's landings passed in `rcx`/`rdx`, as today.

### 4.1 The call protocol, and the frame carved inline
- **Caller.** It builds the n argument DESCRs directly in a block on its spine (`sub rsp,16n`; one or two stores each), loads `rcx=γland` and `rdx=ωland`, then `jmp p.α`. No `g_call_args`, `rt_arg_stage`, `rt_proc_call_open_det` or `rt_icn_zframe_args_install`. A static call knows its callee's label at compile time.
- **Callee α.** It carves its frame immediately below the argument block (`sub rsp,kt`). The frame reads `F.A[i] = [rbp+kt+16i]`, so the arguments are never copied.
- **The header** is stored inline: γ, ω, caller rbp, `F.TRMARK=r12`, `F.B0=B`, `F.HB` and `F.CUR`. Only the locals that a γ→β window can observe are zeroed (a `rep stosq` or unrolled stores, sized at compile time). There is no `rt_jmp_frame_lexprep2`.

| header word | meaning |
|---|---|
| `F.TRMARK` | r12 at α; the clause step unwinds to it |
| `F.B0` | B at α; the cut barrier |
| `F.HB` | HB saved while this frame is the youngest choice |
| `F.CUR` | pointer into the clause chain (§ 4.2); 0 = no alternative left |
| `F.RES` | banked β of the youngest retained sub-goal; zeroed on read |
| γ · ω · caller rbp | the wire triple |

### 4.2 Clause selection: the SWITCH box (first-argument indexing)
- α derefs `F.A[0]` and branches on the tag byte: unbound → the full chain; atom or integer → a compare chain, or a hashed table above a compile-time threshold; compound → a functor compare.
- Each branch lands on a **clause chain**: a read-only array of clause-α addresses, terminated by 0.
- **One candidate:** the box opens no choice. It jumps straight to that clause, and the predicate is deterministic on that call.
- **More than one:** the choice open is a set of stores: `F.CUR := chain+8`, `B := H`, `HB := rbx`.
- **The clause step** (β with `F.RES`=0): unwind to `F.TRMARK`, load `rax=[F.CUR]`, test it, jump to ω at 0, otherwise advance `F.CUR`. If the next word is 0, drop the choice (`B:=F.B0`, HB reloaded from B) before `jmp rax`. This is Jcon's `Alt` with its temporary promoted into the frame (`…TRANSLATION.md` § B.3). The chain address replaces today's per-clause `altK` trampolines.
- Indexing is beyond Byrd and Proebsting. It is added because the bar is `gplc`, and in the papers' own terms it is only a conditional and indirect jump (Proebsting 1997: *"nothing more powerful than conditional, direct, and indirect jumps"*).

### 4.3 The exits
- **Deterministic γ** (B = `F.B0`; nothing younger survived): release the frame and the argument block (`lea rsp,[rbp+kt+16n]`), restore the caller's rbp, then `jmp γ` with `eax=0`.
- **Nondeterministic γ:** keep the frame and return `rax=rbp`, `rdx=&β` for the caller's `F.ACT[site]`. This is Icon's retained-generator frame, as now, but with no `rt_gen_spine_pass_γ`: the landing is two stores.
- **ω:** unwind to `F.TRMARK`, set `B := F.B0`, release, `jmp ω`.
- **Ball (exception):** every β that can re-enter a retained callee opens with the ball test (C9, `…TRANSLATION.md` § A.1), now `mov rcx,r12; and rcx,-ARENA; cmp qword [rcx+8],0`.

### 4.4 Last call
The last goal of a clause, reached while `B == F.B0`, copies its n new arguments over `F.A`. The copy is safe because frames hold only values (§ 1). It then resets `rsp` to the frame's base and jumps to the callee's α with the caller's own γ/ω. `rt_pl_tail_args_safe` is deleted, because the property it tested now holds by construction. Calls between different arities adjust the argument block by `16×(n'−n)`.

---

## 5. Head unification IS a SNOBOL4 match

The clause head `p(t1,…,tn)` is a **pattern**, and the argument block is the **subject**. At the clause's α: `r13 = &F.A[0]`, `r14 = 0`, `r15 = 16n`. Each head argument is one match node that consumes one cell at `[r13+r14]` and advances `r14` by 16, exactly as `bb_match_lit` consumes bytes at `[r13+rcx]`. The head is deterministic, so every node's β is a trampoline to the preceding node's β, and the first node's β is the clause step. Undo is wholesale, by the clause step's unwind to `F.TRMARK`, just as MATCH_BEGIN's ω resets `r12` from its frame.

| node | α (read mode) | if the subject cell is unbound (write mode) |
|---|---|---|
| **`U_CONST k`** (atom, int) | inline deref; `cmp` tag+value; equal → advance, γ; else ω | bind the cell to `k` (§ 3), advance, γ |
| **`U_FIRST Xj`** (first occurrence) | `F.X[j] := [r13+r14]` (16-byte copy, no deref); advance, γ | same |
| **`U_VAL Xj`** (later occurrence) | both sides atomic or unbound → inline compare or bind; otherwise the **general-unify leaf** (§ 5.2) | same |
| **`U_STRUCT f/k … U_POP`** | deref; `DT_PLREF` with functor `f/k` → **push `(r13,r14,r15)` on the spine** (MATCH_BEGIN's outer-Σ/δ/Δ save), `r13 := block`, `r14 := 0`, `r15 := 16k`; the k children run; `U_POP` restores the triple and advances | allocate a k-cell block (§ 7), bind the cell to `{DT_PLREF,f/k,block}`, then run the **write-mode twin** of the children, which fills the block instead of testing it (§ 5.1) |
| **`U_LIST`** | `U_STRUCT '.'/2` with a two-cell block and its tail as the last child; a list spine walks by rebinding r13 in place with no push (the tail-cell case of LCO) | as `U_STRUCT` |

**5.1 Read mode and write mode are two code copies, not a flag.** A pattern node never writes its subject; a unification node must. The WAM uses a mode register tested at every `unify_*` instruction. Here `U_STRUCT`'s α picks, once, between two compile-time copies of the subterm: the read copy (the nodes above) and the write copy, which is § 7's construction sequence aimed at the new block. Both copies rejoin at `U_POP`'s γ. This is Proebsting's run-time-selected gate taken at compile time; it costs code size proportional to head size and removes every per-cell mode test.

**5.2 The general-unify leaf.** `U_VAL` of two arbitrary runtime terms needs a walk whose depth is unknown at compile time. It is **one rtx leaf, `rtx_pl_unify`, written in asm on the same plane**. Its stack of `(r13,r14,r15)` triples lives on the spine, it binds through § 3's inline sequence, and it returns `eax` as 0 or 1. It is the SNOBOL4 matcher's ARBNO shape (a node that loops over its own stack), not a C function. `plw_unify_cells`, `plw_cell_deref_slow` and `rt_pl_deref_val` are deleted with the C walk. The leaf is a leaf, not a box graph, because Lon's "no C Byrd-box functions" law is about C; an asm leaf over the match plane is what `rtx_match.s` already is.

**5.3 Collector safety.** No safe point falls inside a head. Write mode's bump never collects (THE COLLECTOR: collection happens only at the return of an allocating runtime call). The raw `(r13,r14,r15)` triples on the spine therefore never meet a poll. The head's γ (the neck) is the clause's first poll, and by then the spine is back to DESCRs only.

---

## 6. Body goals — control, in the wiring the translation page already specifies

| construct | box | what changes from today |
|---|---|---|
| `A , B` | wiring only (`…TRANSLATION.md` § B.4) | none |
| `A ; B` | the disjunction box; the choice open is inline stores (`F.HI`/B/HB/r12 mark in the box's own frame words) | `rt_pl_disj_open` deleted |
| `C -> T ; E`, `\+`, `once`, `forall`, `ignore` | `IR_GATE` + `IR_BOUND` + `IR_UNMARK` (§ B.7); the fence commit is two stores | `rt_pl_fence_commit` deleted |
| `!` | `F.CUR := 0; F.RES := 0; B := F.B0; HB := [B].F.HB; rsp := pin` | `rt_pl_cut_barrier` deleted |
| `catch/3`, `throw/1` | as landed at rung 9 (§ B.10); the ball in the arena header | the ball-slot address changes |
| `findall/bagof/setof` | the drive loop is boxes; collect and group stay **value services** (a copy is a value service) | none |
| `between/3`, `repeat` | `IR_TO`, `bb_repalt` | the bounds guard inline for small ints |

---

## 7. Body construction — the emitted allocation sequence

`f(t1,…,tk)` in a body (or a head in write mode) is built by the rtx_alloc inline carve, emitted in the box:
```
    mov rax, rbx ; add rbx, 16+16k ; cmp rbx, [g_hp_fr.line] ; ja slow   ; one header + k cells
    <write the HB_DVEC block header>                                    ; as rtx_alloc.s does
    <k stores of 16 bytes: constants, F.X copies, fresh self-refs, nested blocks>
```
- Nested subterms are built innermost-first into the same bump, one carve for the whole term when its size is static.
- `slow` calls the allocator, which grows the window and sets `g_gc_pending` but never collects, then rejoins. The next poll collects.
- `rt_pl_dop_mkc`, `rt_pl_dop_mkc_c`, `plw_mkc_build` and `plw_mkc_kids` are deleted, along with the run-time functor intern.

---

## 8. Arithmetic, comparison, type tests — inline for the small-integer case

`X is A+B*C` compiles to deref, tag test `DT_I`, `imul`/`add` with `jo`, and store or bind. Any other tag or an overflow takes **one cold asm leaf** (floats, bignums, ISO type and evaluation errors), reached only off the hot path. `=:=`, `<` and the rest are a `cmp` and a conditional jump to ω. `var/1`, `atom/1`, `integer/1`, `compound/1` and `atomic/1` are deref plus one tag compare. `functor/3` and `arg/3` with a known argument number are loads from the block. The whole `rt_pl_dop_ax_*`, `rt_pl_dop_cmp_*`, `rt_pl_dop_anum_guard*`, `rt_pl_dop_is_v` and `dop_pl_var` family leaves the hot path.

---

## 9. Meta-call — a compiled goal is jumped to; everything else goes through CODE

`call(G, E1…Em)` derefs G and branches on its tag.
- **Atom or compound whose functor id names a compiled predicate** (a read-only **predicate table** in the code slab: functor id → α, n, kt, sorted and binary-searched, or perfect-hashed at compile time): copy the goal's k arguments plus E1…Em onto the spine as an argument block, then enter p.α exactly as § 4.1 does. The call site's β resumes through the banked β like any call. This is row `prolog-bb-a-meta-call-whose-goal-resolves-to-a-compiled-predicate-jumps-to-it-…`.
- **A control construct** (`,`, `;`, `->`, `\+`, `call/N` nesting, a cut inside) **goes through the runtime compiler**. That is THE RUNTIME-GOAL RULING (`ARCH-ENGINE.md`; Lon 2026-09-01: *"re-using EVAL and CODE"*). The goal is compiled once per goal *shape* (the term with variables abstracted to argument positions), and the compiled graph is cached in the standing code slab. Later calls of the same shape jump to it with the goal's variables as arguments.
- **Unknown:** ISO `existence_error`, or fail under `unknown=fail`.

`rt_pl_goal_spine_prep`, `rt_pl_goal_gen_h`, `rt_call_value_resume_h` and `rt_gen_spine_resume_enter` are deleted.

---

## 10. The dynamic database is code (Lon 2026-09-03: *"It is all code not data."*)

- **The store.** A dynamic predicate is a predicate box whose clause chain (§ 4.2) is mutable. It is one named root cell per predicate (as landed at 10b) holding a heap chain of `{clause α, generation born, generation erased}`.
- **`assertz(C)`** compiles C through the runtime compiler (CODE) into a clause box and links it. Its α is a head match (§ 5) plus a body, exactly like a static clause.
- **`retract(C)`** is an ordinary call of that predicate's `clause/2` view followed by marking the entry erased.
- **The logical update view** is a generation compare in the clause step. A call records the generation at its α in its frame and skips entries born later or erased earlier.
- **Cost of a fact assert.** A fact's compile is template instantiation: head-match nodes over constants, with no optimizer pass needed. It is measured against gplc's `assertz` before it is called done.
- **Deleted:** `rt_pl_dop_db_*` (decl, t_guard, at, gen, n, assertz) and the `$db_at` / `IR_TO` enumeration.

---

## 11. What is deleted, and the census regex that proves it

| mechanism | deleted | census regex at zero |
|---|---|---|
| trail push/test/unwind | `plw_bind` `pl_tr_push` `pl_tr_needs_log` `rt_pl_tr_unwind*` `rt_pl_tr_gc_sync` | `rt_pl_tr_.*` |
| frame | `rt_jmp_frame_lexprep2` `rt_icn_zframe_args_install` `rt_arg_stage` `rt_proc_call_open_det` `rt_proc_drop_frame_h` `rt_nret_fix_tiny` `rt_pl_tail_args_safe` (Prolog graphs only; Icon keeps what it uses) | `rt_(jmp_frame_lexprep2\|icn_zframe_args_install\|arg_stage\|proc_call_open_det\|proc_drop_frame_h\|nret_fix_tiny\|pl_tail_args_safe)` |
| choice/cut | `rt_pl_choice_open` `rt_pl_disj_open` `rt_pl_cut_barrier` `rt_pl_fence_commit` | `rt_pl_(choice_open\|disj_open\|cut_barrier\|fence_commit)` |
| unify/deref | `rt_pl_dop_unify*` `rt_pl_dop_clause_unify` `plw_unify_cells` `plw_cell_deref_slow` `rt_pl_deref_val` | `rt_pl_dop_(clause_)?unify.*` |
| construction | `rt_pl_dop_mkc` `plw_mkc_*` | `rt_pl_dop_mkc` |
| arithmetic | `rt_pl_dop_(ax_\|cmp_\|anum_guard\|is_v)` `dop_pl_var` | `rt_pl_dop_(ax_\|cmp_\|anum_guard\|is_v)\|dop_pl_(var\|integer\|atom)` |
| meta-call | `rt_pl_goal_spine_prep` `rt_pl_goal_gen_h` `rt_call_value_resume_h` `rt_gen_spine_resume_enter` | those four |
| database | `rt_pl_dop_db_.*` | `rt_pl_dop_db_.*` |

**The C that stays, as value services:** the writer, `format/2`, streams, atom and string text, `sort`/`msort`/`keysort`/`compare/3` beyond the atomic case, `copy_term`, bignum and float math, the ISO error balls, and findall's collect. **Baseline, measured this sitting:** `bench_prolog_call_census.sh` on SCRIP `bc6481017` (incremental `make`) reads the same per-entry counts as the ceo's grid on `a6d057a31`; nothing has moved since. The entries live in `src/runtime/by_name_dispatch.c`, `unification.c` and `rtx_plunify.s`, and after the rewrite those files keep the value services above and nothing else. ⚠ The census also prints `qword`, `with` and `moved` as though they were entries. Those are indirect `call qword ptr […]` sites and comment text parsed as symbols, so no regex above may match them.

---

## 12. The rungs — in place, each deleting what it replaces

Each rung: the census regex reads zero; the named kernels' `bench_prolog_bar.sh … gplc` multiple is recorded before and after (the bar 1.0 is the destination, not each rung's gate); the ladder `test_prolog_ladder.sh --to N` plus the master board and the five package suites hold their floors in **both modes**; the monitor bracket names any red. Each rung maps to rows already on the queue.

| rung | lands | depends on | row(s) it closes |
|---|---|---|---|
| **R0** | § 3 the trail: inline push, inline unwind, entries of one word, B/HB/ball in the arena header, HB raised by the collector | — | rank 0 `prolog-bb-lon-the-r12-push-and-pop-are-inlined-…`; `prolog-speed-the-trail-test-…` |
| **R1** | § 1 atoms and functors: `DT_PLATOM`, compile-time ids, the read-only table with operator columns, the runtime services moved to ids | — | `prolog-speed-an-atom-the-compiler-saw-…`; `prolog-speed-an-operator-term-…` (deriv, derive, divide10, times10, log10, ops8) |
| **R2** | § 1 heap-only variable cells: frame slots hold values; `plw_bind` boxing and `plw_mkc_kids` globalising deleted | R0 | (the soundness base for R3–R5) |
| **R3** | § 7 construction by the emitted carve | R1, R2 | `prolog-bb-a-body-term-is-built-…` |
| **R4** | § 5 head unification as match nodes on r13/r14/r15, read/write twins, the `rtx_pl_unify` leaf; the C walk deleted | R1–R3 | `prolog-speed-get-put-and-unify-…` (nrev, qsort, mu, zebra, queens_8) |
| **R5** | § 4.1/4.3/4.4 the frame carved inline, arguments in place, deterministic release, last call by copy | R2 | `prolog-bb-the-activation-frame-is-carved-…`; `prolog-speed-a-retained-choice-point-costs-…` (tak) |
| **R6** | § 4.2 SWITCH and clause chains; § 6 choice/cut/fence/disjunction as stores | R5 | `prolog-bb-choice-open-cut-fence-…`; `query`; rung-12 indexing |
| **R7** | § 8 arithmetic and type tests inline | R1 | `prolog-bb-is-2-comparison-and-type-tests-…`; fib, cal, sendmore |
| **R8** | § 9 meta-call through the predicate table plus CODE | R5 | `prolog-bb-a-meta-call-…`; meta_qsort |
| **R9** | § 10 the dynamic database as code | R4, R8 | `prolog-bb-the-dynamic-database-is-code-…` |

**R0 first**, because Lon ranked it 0 and because it is the only rung with no dependency. It does not wait for R2: under today's cells the entry stays `{cell, old}` (the frame-cell case needs the old value), and it shrinks to one word when R2 lands.

---

## 13. Questions for Lon (each has a recommended answer; work proceeds on the recommendation)

1. **Heap-only variable cells (§ 1).** Every unbound variable is a 16-byte heap cell, and frames hold only values. This buys last call, frame release and a one-word trail with no unsafe-variable analysis. **Recommended: yes.** It is the same heap use as a compound's argument block, which the carve-out already admits.
2. **Where B, HB and the ball live (§ 2).** **Recommended: the trail arena's own header, reached from `r12`** (two instructions, and not a global). The alternative is a pinned VA (one instruction), which is a global in effect and needs Lon's banner permission.
3. **The trail arena (§ 3) against CEO-313's withdrawal (2026-09-06: entries into per-frame logs).** Lon's 10:5x words ("R12 … like the CAS") read as the CAS's own shape, and the CAS is an island addressed by `r12` (`pin_va.h` `RT_DCAP_ISLAND_BYTES`), not the spine. **Recommended: keep the arena; retire row `prolog-trail-entries-live-in-the-activation-frame-…`.**
4. **First-argument indexing (§ 4.2).** It is beyond Byrd and Proebsting and is WAM-standard. **Recommended: yes**, as a SWITCH box made of conditional and indirect jumps. Without it app/3 and nrev open a choice at every call, and the gplc bar is out of reach.
5. **Control constructs under `call/1` (§ 9).** They are compiled through CODE per goal shape and cached; they are not interpreted by a Prolog-written meta-interpreter. **Recommended: CODE**, per THE RUNTIME-GOAL RULING.
