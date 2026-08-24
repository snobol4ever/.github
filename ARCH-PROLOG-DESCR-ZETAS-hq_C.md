# ARCH — PROLOG ON `DESCR` + BYRD BOXES + THE THREE ZETAS

**Author:** hq_C (HQ-CORRECTNESS) · **Date:** 2026-08-24 s273 · **Status:** DESIGN, commissioned by Lon in-chat (*"You must design an entire new system. Get to work and let me know if you need help."*)
**Ruling this implements (Lon s273, verbatim in substance):** *Prolog should not use `Term` at all, it should be using `DESCR`. It is out of whack design-wise. Things do not really need to live on the heap for our GDE stuff — look at Icon and SNOBOL4. The values for strings, yes. But we are using Byrd Boxes. **Any allocations better live on (1) the SPINE, (2) the ACTIVATION FRAME, (3) the STANDING (ROOT) ACTIVATION FRAME — IN THAT ORDER.** We use BB with RESULT and BB LOCALS. You can have as many RESULTS and LOCALS as needed at ALL THREE ZETAS.* — plus: ***"We use GC Heap! NO MALLOC!"***

---

## 0. THE ONE SENTENCE

**A Prolog term is a `DESCR_t`. A logic variable is a `DESCR_t` slot whose address is its identity. A compound is a `DESCR_t` pointing at a contiguous run of `DESCR_t`. All three live on a zeta, chosen by lifetime, in Lon's order — and nothing but string bytes ever reaches the GC heap.**

Everything below is consequence.

---

## 1. WHAT IS ACTUALLY THERE TODAY (measured s273, not recalled)

| | measured |
|---|---|
| `Term` references (frontend + `unification.c` + `sync_monitor.c`) | **448** |
| Prolog-reachable files touching `DESCR_t` | **2** (`pl_cell.h`, `unification.c`) |
| raw `malloc(` sites in `src/parser/prolog/` | **27** ⛔ (the worst of any area; SNOBOL4 8, Icon 6) |
| `malloc`/`free` sites in `prolog_parse.c` alone | **23** |

`src/parser/prolog/term.h` is a **complete second value representation**, parallel to `DESCR_t` and structurally unlike it:

```c
typedef enum { TERM_ATOM, TERM_VAR, TERM_COMPOUND, TERM_INT, TERM_FLOAT, TERM_REF } TermTag;
struct Term { TermTag tag; int saved_slot;
              union { int atom_id; int var_slot;
                      struct { int functor; int arity; Term **args; } compound;
                      long ival; double fval; Term *ref; }; };
```

⛔ **Two independent defects, and they compound.** (a) **Wrong type** — a second value universe the rest of the compiler cannot see. (b) **Wrong allocator** — `Term **args = malloc(...)`: raw `malloc`, so those nodes are invisible to the GC, untraced, unmoved, and unfreed on backtracking.

⭐ **This is the root of the bespoke-plumbing smell.** `rt_jmp_frame_lexprep2` — a **no-op** called from every 2+-clause predicate's prologue (`xa_flat.cpp:282-287`) — is frame machinery SNOBOL4 and Icon never needed. They never needed it because they carry values in **BB RESULT and BB LOCALS on the zetas**, and Prolog carries a heap node graph that the frame has to be taught about. **Fix the representation and the plumbing stops being necessary, rather than being fixed.**

---

## 2. THE TARGET MACHINE (what we are building onto — not invented here)

`DESCR_t` is **exactly 16 bytes** and its size is load-bearing:

```c
typedef struct DESCR_t { uint8_t v; uint8_t mod_op; uint16_t src_node; uint32_t slen;
                         union { char *s; int64_t i; double r; void *p;
                                 struct _ARBLK_t *arr; struct _TBBLK_t *tbl;
                                 struct _DATINST_t *u; ... }; } DESCR_t;
DESCR_SASSERT(sizeof(DESCR_t) == 16, "SysV register-pair (rax:rdx) INTEGER-class return;
                                      17+ bytes flips it to MEMORY class across 4,009 lines of asm");
```

⭐ **A `DESCR_t` is returned in `rax:rdx`.** That is precisely what a Byrd box's **RESULT** wants to be: a value handed γ-ward in registers, with no memory traffic and no allocation. `Term *` cannot do this — it is a pointer to something that had to be allocated first.

Already-ruled register contract (`GOAL-PROLOG-100.md:19`), which this design **uses unchanged**:

| reg | role |
|---|---|
| **R15** | **CP** — the choice-point register, in Prolog graphs (Lon ruling, s-2026-08-21). `fail` is uniformly `jmp [r15]`; cut is `r15 = [r15+16]` |
| **R12** | undo-arena top — **the trail** ("Prolog trail marks ride records") |
| R10/R11 | γ/ω wires, WIRE-ORDER γ@+0 / ω@+8 |
| RBX | heap frontier · R13/R14 Σ/δ scan-reserved (free in Prolog graphs, no string scanning) · R9 RTCC/GVA base |

The three zetas (CLAUDE.md): **ζ-SPINE on RSP**; **ζ-ACTIVATION-FRAME** and **ζ-STANDING** on RBP.

---

## 3. THE REPRESENTATION — six `TermTag`s become `DESCR_t`

| `Term` | becomes | carrier |
|---|---|---|
| `TERM_INT` (`long ival`) | `DESCR` integer | `.i` — **immediate, no allocation** |
| `TERM_FLOAT` (`double fval`) | `DESCR` real | `.r` — **immediate, no allocation** |
| `TERM_ATOM` (`int atom_id`) | `DESCR` atom | interned; ⚠️ see §7 open question 1 (`DT_A` vs `DT_S`) |
| `TERM_VAR` (`int var_slot`) | **a `DESCR` slot; identity = its address** | a BB LOCAL on a zeta (§4) |
| `TERM_REF` (`Term *ref`) | a bound var slot holding a **ref-to-slot** `DESCR` | `.p` → the target slot |
| `TERM_COMPOUND` (`{functor, arity, Term **args}`) | `DESCR` whose `.p` → a **contiguous run of `arity` `DESCR_t`** ("the ARG RUN"), functor+arity in the header word | the run sits on a zeta (§4) |

⭐ **`saved_slot` disappears.** It exists only to let a heap node remember where it was parked. A slot that *is* its own identity has nothing to save.

⭐ **Two of six kinds stop allocating entirely.** Integers and floats become immediate `DESCR` payloads — today each is a `malloc`'d node.

---

## 4. WHERE IT LIVES — the lifetime ladder IS Lon's order

⛔ **Lon's order is not a preference list; it is a lifetime ladder.** You go down it only when the tier above genuinely cannot carry the value's lifetime.

| # | tier | carries | lifetime |
|---|---|---|---|
| **1** | **ζ-SPINE** (RSP) | box-local temporaries, the arg run of a compound consumed within the box, unification scratch | dies with the box |
| **2** | **ζ-ACTIVATION FRAME** (RBP) | a predicate activation's logic variables; arg runs surviving the box but not the activation; the **retry/resume state** | dies with the predicate activation |
| **3** | **ζ-STANDING / ROOT** (RBP) | program-lifetime terms: the clause database, interned atoms, asserted clauses | program lifetime |
| — | **GC heap**, `rt_gcheap_alloc` only | ⛔ **string BYTES and nothing else** | traced |

⛔ **`malloc` is banned outright.** Where the heap is genuinely right (string bytes), the allocator is **`rt_gcheap_alloc(uint16_t type, uint64_t payload_bytes)`** — asm at `src/runtime/rtx/rtx_alloc.S`, C twin `c_rt_gcheap_alloc` (`gc_heap.c:172`), typed by an `HB_*` tag. All **27** Prolog `malloc` sites are defects on both axes. ⭐ Their real cost is not bytes: **`malloc`'d nodes are invisible to the GC and are not undone by backtracking**, so every failed branch leaks. That is a correctness bug wearing a performance bug's clothes.

**Placement is decided at LOWER time, not run time.** The lowerer knows a term's escape: consumed in-box → tier 1; escapes the box but not the activation → tier 2; asserted/interned → tier 3. ⭐ **This is what `zdp_tier` already does for SNOBOL4 and Icon** — Prolog stops being special and starts calling the same planner. PZ-4 already says this in words: *"Multi-clause/resumable predicates take the ζ-ACTIVATION tier via `zdp_tier`/heap-fb ADOPT — never a hand predicate."* **This design is what makes that sentence implementable.**

---

## 5. THE HARD PART — logic variables, binding, and undo

This is the one place Prolog genuinely differs from SNOBOL4 and Icon, and it is where a design either works or quietly reintroduces the heap.

A logic variable needs three things: **identity**, **destructive binding**, and **undo on backtracking**.

**Identity.** A variable *is* a `DESCR_t` slot at a known offset in a zeta. Its identity is its **address**. Two occurrences of `X` in a clause lower to the same offset in the same activation frame. ⭐ No node, no id, no allocation — a variable costs 16 bytes of frame that the frame was going to reserve anyway.

**Binding.** Unification writes the `DESCR` **in place**. Binding `X` to an integer writes an integer `DESCR` into `X`'s slot. Binding `X` to another variable writes a **ref-to-slot** `DESCR` (`.p` → target). **Deref** walks the ref chain until it reaches a non-ref or an unbound slot — the classic union-find walk, over slots instead of nodes.

**Undo — and the machine already has it.** R12 is the **undo-arena top**, and the contract already says *"Prolog trail marks ride records."* On binding a previously-unbound slot, push `(slot address, old DESCR)` to the undo arena. On `β` (recede), pop back to the choice point's mark and restore. ⭐ **This is the same undo arena SNOBOL4 uses for pattern-match backtracking** — Prolog's trail stops being a bespoke data structure and becomes a *use* of the shared one.

⭐⭐ **THE STRUCTURAL PAYOFF, and it is the argument for the whole design:** with variables as frame slots and the trail as the shared undo arena, **`β` restores bindings by unwinding an arena that already unwinds** — which is exactly why SNOBOL4 and Icon never needed `rt_jmp_frame_lexprep2`. ⛔ **Do not fix that no-op by writing a heap-aware frame seed.** The frame's retry/resume state is **BB LOCALS at the activation-frame zeta**; make it that, and the function has nothing left to do.

⚠️ **The one real hazard, named so nobody rediscovers it:** a slot must never hold a ref to a slot **shorter-lived than itself** (a frame slot pointing into a dead spine cell — a dangling ref that outlives its target). **Rule: a ref may only point from a shorter-lived tier to an equal-or-longer-lived tier — never downward.** When unification would bind long→short, the short side is **promoted** to the longer tier first. ⭐ This is the same discipline as the existing heap-fb **ADOPT** mechanism PZ-4 already names, and it is the constraint that makes the ladder safe rather than merely tidy.

---

## 6. WHAT A PREDICATE COMPILES TO — four ports, unchanged

A predicate call is a Byrd box; clauses are its alternatives. No new machinery:

- **α (proceed)** — enter: reserve the activation frame (variable slots = BB LOCALS), unify head args against caller args, first clause.
- **γ (succeed)** — hand the result γ-ward. The result is a `DESCR` **in `rax:rdx`** (§2), which is why 16 bytes matters.
- **β (recede)** — retry: unwind the trail to this box's mark (R12), try the next clause. `fail` = `jmp [r15]`.
- **ω (concede)** — no clauses left: release the activation frame, restore caller base, concede.
- **Cut** — `r15 = [r15+16]`, already ruled.

⭐ **Multi-clause is not a special case any more.** It is a box with more than one alternative — the same shape as a SNOBOL4 pattern alternation and an Icon generator with multiple results. **That is the "three syntaxes over one machine" claim actually being true**, rather than asserted while Prolog runs a private machine underneath.

---

## 7. OPEN QUESTIONS — honestly flagged, not hidden

1. **Atom representation: `DT_A` or `DT_S`?** The retired-goal-file carried lesson is explicit: *"an atom is `DT_A` OR `DT_S` depending on entry — check both tags."* Interned atom ids are compact and fast to compare; `DT_S` unifies with SNOBOL4's string world. ⭐ **My recommendation: intern to a stable id, carry `DT_A`, and make `DT_S` a conversion at the boundary** — but this needs measurement, and it is the one choice that touches the string/GC boundary.
2. **Arg-run header.** Functor+arity must live somewhere. Options: (a) `slen` carries arity and `.p` points at the run with functor in a preceding word; (b) a two-`DESCR` header. (a) is cheaper and fits the existing 16-byte shape; **(a) is the recommendation**, pending a check that `slen`'s 32 bits and `mod_op`/`src_node` stamping are not already claimed on this path.
3. **`assertz`/`retract` and tier 3.** Asserted clauses are program-lifetime, so tier 3 — but `retract` makes that tier *mutable*, which the standing zeta has not had to be before. ⚠️ This is the row `prolog-assertz-retract-abolish-unmasked` was minted over; the 3 `abolish` `existence_error`-vs-fail disagreements against `swipl` are a **separate** `.expected`-provenance question and must not be folded in.
4. **Conversion sequencing.** 448 references cannot move in one commit. §8.

---

## 8. EXECUTION LADDER — how it lands without a flag day

⛔ **One directory/one concern per commit, blocking gates green through every step** — the same contract as the srcreorg ladder, and for the same reason.

| rung | work | gate |
|---|---|---|
| **P-0** | **Kill `malloc` in Prolog.** Convert all 27 sites to `rt_gcheap_alloc` **with `Term` unchanged.** Pure allocator swap, no representation change. | no `malloc(` in `src/parser/prolog/`; Prolog rungs no worse |
| **P-1** | **`DESCR` for the two free kinds** — `TERM_INT`, `TERM_FLOAT` become immediate `DESCR` payloads. Smallest real conversion; proves the seam. | rungs unmoved; allocation count drops measurably |
| **P-2** | **Logic variable → frame slot + shared undo arena** (§5). The keystone. Retires `rt_jmp_frame_lexprep2` by making it unnecessary. | `rung13/14/15` honest board improves; `queens.pl` runs both modes |
| **P-3** | **Compound → arg run on the tier ladder** (§4), placement via `zdp_tier`. | multi-clause + structure tests; no tier-3→tier-1 refs (§5 hazard) |
| **P-4** | **Atoms** per open question 1; **delete `term.h`.** | zero `Term` references in `src/` |

⛔ **BINDING ON EVERY RUNG: `xa_flat.cpp` is shared with Icon.** Grade all three frontends on a same-tree control arm — **SNOBOL4 holds 365/365 both modes SKIP=0**, **Icon rung suite unmoved**. That gates *landing*, never *starting* (the seed gate is retired, Lon s273).

⭐ **P-0 and P-1 are independently valuable and carry no representation risk** — if the ladder stalls, the tree is still strictly better: GC-visible allocations and two kinds off the heap.

---

## 9. WHAT I NEED FROM LON

Answers are welcome but **not blocking** — the seed gate is retired and P-0/P-1 can start today.

1. **Open question 1 (atom `DT_A` vs `DT_S`)** — the only choice that touches the string/GC boundary, where a wrong pick is expensive to unwind.
2. **Tier-3 mutability for `assertz`/`retract`** (open question 3) — a mutable standing zeta may be a genuinely new capability rather than a use of an existing one.
3. **Sequencing against the srcreorg ladder** — P-0/P-1 touch only `src/parser/prolog/`, so they do **not** collide with the three moves in flight. **P-2 onward touches `xa_flat.cpp`/templates and should follow the moves**, or it will fight move 3 for the same files.
