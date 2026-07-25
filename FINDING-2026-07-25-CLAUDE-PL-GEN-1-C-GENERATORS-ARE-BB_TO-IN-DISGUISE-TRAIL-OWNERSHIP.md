# FINDING 2026-07-25 (s144) — THE C GENERATORS ARE `bb_to` IN DISGUISE; THE GENERATOR OWNS THE TRAIL, NOT THE RAIL

**Directive (Lon, s142/s144):** "Rewrite Prolog runtime into BBs for performance. Things that were FOR loops in the C code
would become BBs with bouncing back and forth via gamma and omega."

**Status:** DESIGN + BLOCKING-QUESTION ANSWERED. No code landed this session. Implementation is mechanical from §4.

---

## 1. THE ISOMORPHISM — `rt_pl_between_gen` IS `bb_to` WRITTEN IN C

`by_name_dispatch.c:4358` (`rt_pl_between_gen`) and `templates/bb_to.cpp:53-77` (integer arm) are the SAME MACHINE.
The C version pays for a worse ABI on every solution:

| | `bb_to` (emitted box) | `rt_pl_between_gen` (C) |
|---|---|---|
| loop state | box frame slots `FRQ(op_off+16)` | `plc_between_t{cur,hi,mark}` via **`rt_ws_alloc` — a heap alloc per activation** |
| resume | β port — a landed `jmp` | `int64_t *resume` cookie, tri-state `0`/`-1`/pointer, **decoded every re-entry** |
| yield | `x86_gamma()` — a jump | `return r` + caller `test eax,eax` + route |
| exhausted | `x86_omega("jg")` — a jump | `return FAILDESCR` + caller test |
| per-solution cost | `inc` · `cmp` · `jmp` | call + cookie decode + unify + return + test + route |

`bb_call.cpp:347` states the current arrangement outright: *"alpha zeroes resume cell, beta re-pumps invoke with
persisted cell."* **The box already HAS α/β/γ/ω — it is a pump handle bolted onto a C loop, talking through a cookie.**
Moving the loop into the box deletes the per-activation `rt_ws_alloc`, the cookie decode, and the call/return per solution.

---

## 2. ⚠ THE BLOCKING DISCOVERY — THE GENERATOR OWNS ITS OWN TRAIL DISCIPLINE

**The GEN rail's β is a BARE `jmp` (`bb_call.cpp:381-382`: `x86_beta(); jmp L(60)`). There is NO trail unwind anywhere
in the emitted wire.** All inter-solution trail discipline is done BY HAND inside the C generator —
`rt_pl_between_gen:4375` calls `pl_trail_unwind(&g_pl_trail, it->mark)` + `plw_zh_kill_to(it->mark)` at the top of
EVERY iteration, and again at exhaustion (`:4379`).

**CONSEQUENCE FOR EVERY RUNG OF THIS LADDER:** a box that takes over a generator loop MUST carry the
`mark` in its own frame slot and MUST unwind to it per iteration AND at ω. Assuming the GZ choice-point machinery
does it for you is a **silent binding leak across solutions** — the second solution would see the first's bindings
still live and mis-unify. This was the question that blocked design; it is now answered and must not be re-litigated.

---

## 3. LOOP TAXONOMY — NOT EVERY C `for` WANTS PORTS

Mis-applying the generator shape is the bug class this section exists to prevent.

1. **Emit-time bounded** — `plw_mkc_kids:1337` `for(i<ar)`, `ar` an emit-time constant (2 for `'.'/2`).
   → R6 `FOR(i,lo,hi,BODY)` combinator, UNROLLED into the one concat. No runtime loop, no ports. **This is PL-SINK-3.**
2. **Deterministic chase** — deref's `while(bound) follow`. One answer, nothing to resume.
   → internal label + `jmp` back inside one box. `sink_deref` (bb_call_fn.cpp:26) already. **Ports here would be pure overhead.**
3. **Resumable / nondeterministic** — `between`, `sub_atom`, `clause`, `current_op`, …
   → the true α/β/γ/ω box, `bb_to`'s shape. **Untouched; the largest remaining win.**
4. **Tree recursion** — `plw_unify_cells:133` `for(i<ar) if(!plw_unify_cells(&aa[i],&bb[i]))`.
   → a single induction variable cannot carry this. Needs the per-box `.bss` arena indexed by depth that
   ARCH-ICON.md:26 sanctions ("never a global stack"). **Do NOT attempt with a bare γ/ω loop.**

---

## 4. RUNG PL-GEN-1 — `$between` AS A REAL BOX (implementation-ready)

**Why first:** `between(Lo,Hi,X)` IS Icon's `i to j` plus a unify. `bb_to.cpp:53-77` is a near-verbatim template.

Frame slots (box's own zeta frame, `bb_to` layout): result DESCR at `FRQ(resoff)`/`FRQ(resoff+8)`;
`cur` at `+16`, `hi` at `+24`, `mark` at `+32`.

```
α:   marshal Lo,Hi,X -> argbase
     deref+int-check Lo -> cur ; non-int -> SLOW (C leaf owns the ISO throw)
     deref+int-check Hi -> hi
     deref X
       BOUND   -> int-check + range test -> γ once, then ω        (the semidet arm, C :4366)
       UNBOUND -> mark = pl_trail_mark()                          (§2 — the box owns this)
L:   cmp cur, hi        ; jg -> ω_unwind
     trail_unwind(mark)                                           (undo prior solution, C :4375)
     bind X <- {DT_I,0,cur}   = sink_trailpush + 16-byte store    (SINK-1 machinery, reuse verbatim)
     inc cur
     result = {DT_I,0,1}
     -> γ
β:   jmp L
ω_unwind: trail_unwind(mark) ; -> ω                               (C :4379)
```

**Reuse verbatim from SINK-1 (`bb_call_fn.cpp`):** `sink_deref` (contract §2 — the DT_N arms are MANDATORY, a sink that
bails on tag 9 never fires), `sink_trailpush`, `sink_cp16`. **Label decade: allocate 100–119** (SINK-1=40–58,
SINK-2=60–77, SINK-3=80–99 reserved).

**Encoder traps (contract §5, plus s143's own):** `x86("cmp",reg,imm)` is 32-BIT ALWAYS — qword needs `"cmp64"`.
**`x86("cmp", reg, "dword ptr [mem]")` IS NOT AN ENCODER FORM AND SILENTLY EMITS NOTHING** (s143 lost a session to
this) — load to a register, then `cmp reg,reg`. ALWAYS eyeball the emitted `.s` when a fast path half-fires.

**Gates:** the failure-driven smoke `main :- between(1,3,X), write(X), nl, fail.` (verified working on the C rail this
session, m3, prints 1/2/3/done); byte-identity vs the C rail; **a nested-generator test where the outer generator's
bindings must survive the inner's unwind** (this is what §2 puts at risk); then `test_prolog_rung_suite.sh` 164/164 ×3.

**GEN-rail inventory (the full class-3 target list, `lower_prolog.c:401-409`):** `$between` `$sub_atom` `$for`
`$bag_group` `$clause` `$current_predicate` `$predicate_property` `$current_op` `$current_prolog_flag`, plus `$call`.
`rt_pl_sub_atom_gen:4385` (`plc_subatom_t{s,len,b,l,mark}`) is the same pattern with a NESTED loop — two induction
variables in frame slots, the double-`for` as one box.

---

## 5. STALE-PATH CORRECTIONS (STALE-ORIENTATION rule, RULES.md:97)

- **`emit_core.c` DOES NOT EXIST.** `GOAL-PROLOG-BB.md`'s admission recipe step 5 and RULES.md's TEMPLATE-ONLY
  grep both name it. The emitter is **`src/emitter/emit.cpp`**; GEN-rail dispatch is entirely inside
  **`src/templates/bb_call.cpp`**. Fix the recipe before following it.
- **`SCRIP/refs/`** (cited by ARCH-ICON.md:28 for `refs/bb/test_icon.c` and by the SINK-2 note for the gprolog
  source) is **absent from the repo**. gprolog/swipl sources were supplied as session uploads instead.
- Templates live FLAT in `src/templates/`, not `src/emitter/{BB,XA}_templates/` as several rules still spell it.

## 6. ENVIRONMENT (verified this session)

Build is green from a clean clone: `make -j4 scrip` → `scrip` + `out/libscrip_rt.so`, **`-O0` by Makefile default,
no `RT_OPT` override** (O0-DEV / O2-DIRECTED-ONLY compliant). gcc 13.3.0, `as` present, **`nasm` absent**.
`./scrip --run` needs `:- initialization(main, main).` — a bare `:- p.` directive file aborts with
`[IBB] FATAL: mode-3 driver: main BB graph not found`.
