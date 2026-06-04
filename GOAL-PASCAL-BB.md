# GOAL-PASCAL-BB.md — Pascal, 100% Byrd Boxes, from zero

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

**No language-specific logic in any BB or XA C++ template.** All delineated operations are enveloped in
unique BBs; each BB does NOT have varying runtime behavior depending on language. Templates dispatch on IR
shape and representation flags only. FORBIDDEN inside `src/emitter/BB_templates/` and
`src/emitter/XA_templates/`: language enums/guards (`IR_LANG_*`, `LANG_*`, `is_<lang>`), language-named
template functions/files/dispatch arms, and hardcoded language-builtin names. Behavior that differs by
language belongs in the runtime (by-name dispatch) or in LOWER (a different IR shape → its own unique BB) —
never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (XA scanned clean 2026-06-03); fix
ladder: LB-* in `GOAL-PASCAL-BB.md`. COMPLETION TEST: the audit's Tier-1 grep over `BB_templates/` +
`XA_templates/` returns 0 sites.

**Repo:** SCRIP (frontend + lower) · corpus (reference compiler at `programs/pascal/`)
**The 7th frontend.** SNOBOL4 · Snocone · Rebus · Icon · Prolog · Scrip · **Pascal**.

---

## ▶ CURRENT STATE — READ FIRST

**Watermark — PB-9d LANDED (flat procs/params, mode-3+4, LANGUAGE-BLIND). 2026-06-03, session 13 (same
session as PB-9c). SCRIP HEAD = 66e9e19, corpus untouched. POST-REBASE: rebased onto concurrent
`c3d5547` (SNOBOL4 PB-RB-CONV, touches `emit_bb.c` flat_drive_alt); merged tree re-verified — recursion
m3+m4 fact(7) identical, sieve m3 identical, flatnoarg 10, SNOBOL4 19/0, Icon 130/117/36, Prolog 136/0/0.** GATES MET: `recursion.pas` byte-identical to
`pint` through fact(7) in BOTH mode-3 and mode-4 (pint traps at fact(8), the documented 16-bit XFAIL — SCRIP
computes the full table, fib(10)=55 correct); `flatnoarg.pas` byte-identical BOTH modes. KEY DISCOVERY: the
driver ALREADY compiles + registers every non-main proc body in both modes (mode-3: `rt_proc_register` +
`gvar_flat_chain_build` + `rt_proc_set_fn` per proc, scrip.c~1297; mode-4: per-proc
`gvar_flat_chain_build_text` emitting `<name>_α` + the `sno_proc_startup` shim) — and `rt_call_named_proc`
(rt.c:515) is a complete NV-seating invoker whose result convention (`NV_GET_fn(name)` after the body) IS
Pascal's funcname-as-return-variable model. So PB-9d was call-site-only, four pieces: (A) **dispatch** — the
registered-proc gvar arm now accepts dval==3.0 alongside 2.0 (`bb_call.cpp:310`) → `bb_call_gvar_userproc_str`
→ `rt_call_named_proc`. (B) **marshal nested CALL args** (`writeln(k, fact(k), fib(k))` — arg subgraph entry
IS the IR_CALL) — the nested-call arm in `marshal_call_arg` now accepts dval 2.0|3.0 and picks the runtime
entry by `rt_proc_is_registered`: registered → `rt_call_named_proc`, else → `rt_call_arr`; ALSO FIXED the
arm's previously-broken MEDIUM_BINARY idiom (was `x86("mov","rdi",u64)` — which the PB-9b gotcha says
resolves to x86_call_ro! — plus a `frame_load64` of an address; now the proven byname idiom: `x86_load_ro`
rdi + `x86_frame_lea` rsi). (C) **NEW TEMPLATE `bb_binop_gvar_arith_slot.cpp`** (+`IR_BINOP_GVAR_ARITH_SLOT`
kind, emit_core case, Makefile×2) — general gvar arith with per-operand LIT-imm / VAR-via-`rt_gvar_get_int`
/ slot-resident shapes (same `bb_lk/bb_li/bb_rk/bb_ri`+`op_name1/2`+`op_sa/sb` contract as PB-9c's relop;
+8 disp for IR_CALL DESCR operands, +0 for raw qwords; result = raw qword at `op_off` matching the
`bb_gvar_assign` int-binop read convention; op_off doubles as the rax stash around a right-VAR call) —
serves `n * fact(n-1)` (VAR×CALL), `fib(n-1)+fib(n-2)` (CALL×CALL), `five+five`; dispatch arm sits after the
four exact-shape arith arms, before the relop arm. (D) **`IR_RETURN` gvar junction — THE 0s BUG.** Symptom:
all fact/fib returned 0, even the base case. Root cause read off the emitted TEXT: `gvar_stmt_operand_refs`
gives IR_RETURN arity 1, CLOBBERING the lower-set α (or NULL) with the chain's stack top = the
else-branch ASSIGN; `flat_drive_return` then RE-WALKS that α, so BOTH branch tails re-emit the else-assign
inline — on the then-path it reads an unwritten slot and OVERWRITES the correct `fact := 1` with 0. Under
the gvar model the return value rides NV entirely (`rt_call_named_proc` reads `NV_GET_fn(name)`), so the
gvar IR_RETURN is a pure junction: skip the α-walk, define β, jmp the dval-chosen exit — PRESERVING the
SNOBOL4 FRETURN contract (`dval==2.0 → flat_fail_p`, exactly flat_drive_return's exit choice; SNOBOL4
FRET also has α=NULL at lower so no walk is lost). Gates pinned: recursion m3+m4 byte-identical through
fact(7) (THE GATE); flatnoarg m3+m4; sieve + 4 probes m3+m4 (PB-9c preserved); Pascal `--interp` **35/0/1**;
SNOBOL4 smoke **19/0** incl. m4 6/0 (the FRETURN-contract pin); Icon **130/117/36**; Prolog honest
**136/0/0**; all-langs m4 hello **5/1** (rebus pre-existing); new template lang-names CLEAN. NEXT: **PB-9e**
— nested procs = the representation FORK (frame-as-BB, static link on the parent-port thread, Invariants
2 & 4 — Lon's call). Note for PB-9e probing: `rt_call_named_proc` seats params into NV flat — nested probes
(`nestrec` etc.) will need the static-link model, not more NV flattening; the LB ladder also remains.

**Watermark — PB-9c LANDED (control flow, mode-3+4, LANGUAGE-BLIND). 2026-06-03, session 13. SCRIP HEAD =
3d9f434, corpus untouched. POST-REBASE: the push rebased onto concurrent `18940fb` (ICN-SCAN-4, touches
`emit_bb.c` IR_CALL flat-chain arm + `bb_scan_any.cpp` + `scrip.c`) atop `2cfd1bb` (Prolog meta resolver);
the MERGED tree re-verified green in full — sieve m3+m4 byte-identical, 4 probes m3+m4 PASS, Pascal
`--interp` 35/0/1, SNOBOL4 19/0 incl. m4 6/0, Icon 130/117/36, Prolog honest 136/0/0, all-langs m4 hello
5/1.** GATE MET: `sieve.pas` byte-identical to `pint` in BOTH mode-3 and mode-4
(nested WHILE + IF + two lowered FORs + array rail). Five walls, all shape-dispatched, zero language names:
(1) **`gvar_chain_operand_refs` missed ω-only-reachable chains** — nodes reachable ONLY via ω edges (the
post-FOR `i := 2` LIT_I head n48, the WHILE junctions) never became operand-chain heads, so downstream
`IR_ASSIGN.α` stayed NULL → `flat_drive_assign: missing α`. Fix = a third head-scan loop over every node's
resolved ω target (`emit_bb.c`). SAFETY PROOF: a mid-chain re-walk can only NO-write (stack-underflow arm
`else if (ar >= 1) sp = 0` writes nothing), never wrong-write — consumers' top-of-stack operands are
invariant to chain entry point; SNOBOL4 (ω-rich graphs) pinned identical. (2) **`IR_WHILE`/`IR_UNTIL` gvar
junction jumped ω** — in the chain topology the WHILE node is reached ONLY when its condition fails (cond
chain's ω → WHILE), so its emission must `jmp γ` (after-loop), was `jmp ω` (graph failure). The
`g_gvar_flat_chain` arm goes FIRST (before `while_cond_emittable`) because under the chain the body/cond are
separate chain nodes — `flat_drive_while` must never fire. Non-gvar fallback preserved byte-for-byte.
(3) **`IR_IF` gvar junction had no template** — `EMIT_PAIR_FILL` dispatched into a nonexistent IR_IF
template. Under the chain IR_IF is structural (the cond chain's γ/ω do the branching); fix = `jmp γ`
junction arm, descr-chain EMIT_PAIR path untouched. `IR_CONJ` (the loop-back junction) was already correct.
(4) **dval==2.0 by-name calls had NO gvar arm** — `arr_set_pure` (the PB-5 array rail, `v_raku_det_call`
sets dval=2.0, args ride `counter` as `IR_graph_t**` — IDENTICAL layout to dval=3.0) fell through every
dispatch arm → `bb_call: unsupported call shape`. Fix = one `bb_call.cpp` arm: `g_gvar_flat_chain &&
dval==2.0 && !rt_proc_is_registered(fn) && !rt_builtin_is_known(fn)` → `bb_call_byname_str`. The
`!rt_builtin_is_known` guard is LOAD-BEARING: SNOBOL4 `TT_FNC` calls are ALSO dval==2.0 (`lower.c:912`) and
must keep their existing `bb_call_builtin_str` route — pinned by SNOBOL4 smoke. Runtime resolution chain
verified: `rt_call_arr` → `try_call_builtin_by_name` → `script_try_call_builtin_by_name` (holds
`arr_get`/`arr_set_pure`). (5) **gvar relops had NO template** (`sqr(i) <= n`, `arr_get(a,i) <> 0`, `i <=
100`) — `bb_binop_relop` is descr-chain-only (predicate requires `g_descr_flat_chain` + slot operands) →
shape-mismatch bomb. NEW TEMPLATE `bb_binop_gvar_relop.cpp` (+ `IR_BINOP_GVAR_RELOP` kind, emit_core case,
Makefile×2): numeric relops `BINOP_LT..NE`, per-operand shapes LIT-imm / VAR-via-`rt_gvar_get_int` /
slot-resident, communicated via `bb_lk/bb_li/bb_rk/bb_ri` + `op_name1/2` + `op_sa/sb`; slot displacement
dispatches on producer kind (`IR_CALL` result = 16-byte DESCR, value at +8; gvar-arith result = raw qword at
+0); the template's own 8-byte slot doubles as the rax stash around a right-VAR call; fail-jcc table
duplicated into the file per the byte-duplication doctrine. Dispatch arm in `walk_bb_flat` classifies both
operands or falls through to `flat_drive_binop_tree`; γ-chain BFS guarantees operand slots are allocated
before their consuming relop walks. Gates pinned: **sieve m3+m4 byte-identical** (THE GATE); 4 probes
(`m4asg`,`m4arith`,`m4wexpr`,`hello`) m3+m4 PASS; Pascal `--interp` **35/0/1** (XFAIL=recursion fact(8));
SNOBOL4 smoke **19/0** incl. m4 6/0; Icon `--interp` **130/117/36**; Prolog honest **136/0/0**; all-langs m4
hello **5/1** (the 1 = rebus, pre-existing); lang-names gate = only pre-existing `rt_icn_*`/`g_pl_meta`
sites, new template CLEAN. STASH PROOF of causation AND non-regression: clean HEAD aborts sieve+ptr5 at
`flat_drive_assign`, rec2 at the `arr_set_pure` wall — rec2/ptr5 now segv DEEPER (record-field/heap
`__pas_*` arms — never passed m3, walls moved, not regressions; same pattern as flatnoarg in PB-9b). PB-9d
ENTRY MAPPED: `recursion.pas` m3 — the FOR loop now iterates and prints column 1 (k=1..10) but
`fact(k)`/`fib(k)` produce nothing = the documented missing REGISTERED-proc dval==3.0 gvar arm;
`flatnoarg.pas` m3 segv unchanged at that same arm (m4 emits 192 lines rc=0, emitter clean). PB-9d =
that one `bb_call.cpp` arm + CALL-operand BINOPs (the relop template's slot shapes already handle
CALL×LIT — arith may need the same slot extension).

**Watermark — PB-9b LANDED (arith/assign/writeln(expr), mode-3+4, LANGUAGE-BLIND). 2026-06-03, session 12.
SCRIP HEAD = see commit, corpus HEAD = see commit (3 new probes).** Four walls, all shape-dispatched on IR kind
(zero new Tier-1 sites; lang-names gate run, only pre-existing `rt_icn_*` hits, none in touched files):
(1) **`IR_ASSIGN` α=`IR_LIT_I`** (`x := 5`) crashed `flat_drive_assign got kind=0` — `IR_LIT_I` added to BOTH
duplicate dispatch guards (`emit_bb.c` IR_ASSIGN arm AND `emit_core.c:416` — the guard list exists twice!) +
new `IR_LIT_I` arm in `bb_gvar_assign.cpp` (`x86_movabs_r64` imm64 → `rt_gvar_assign_int`; the value rides
`_.op_a_ival_sg`). (2) **Mixed `VAR×LIT`/`LIT×VAR` gvar BINOP** (`y := x * 7`) bombed shape-mismatch — two new
dispatch arms in `emit_bb.c` (MUST clear the unused `op_name1/2` — sticky globals) + mixed arms in
`bb_binop_gvar_arith.cpp` via new helper `rt_gvar_get_int`. (3) **`writeln(2+3)` silently printed `2`** —
`marshal_call_arg` marshaled the subgraph ENTRY node, not the chain result; fix = the gvar dval==3.0 IR_CALL
dispatch arm now runs `gvar_stmt_operand_refs` on every arg subgraph (forward-decl added), and
`marshal_call_arg` resolves the chain-final node and inline-emits arith (frame-slot scratch, DT_I tag 6) per
the template byte-duplication doctrine. (4) **`writeln(x)` read an uninitialized FRAME slot** — gvar-chain
vars live in NV; new gvar `IR_VAR` marshal arm calls `rt_gvar_get_descr` (DESCR in rax:rdx). New rt helpers
(`rt.c`/`rt.h`, exported in libscrip_rt): `rt_gvar_get_int(name)`, `rt_gvar_get_descr(name)`. BUILD GOTCHAS
(cost a cycle each): the `x86(mnem,reg,uint64_t)` overload resolves to `x86_call_ro` — imm64 loads must call
`x86_movabs_r64` directly; template externs to C symbols must sit in the file's `extern "C"` block (inline
fn-body externs mangle); `libscrip_rt.so` must be REBUILT alongside scrip (a stale .so carries mangled
undefined refs that only surface at exe link). Gates pinned: 4 probes (`m4asg`,`m4arith`,`m4wexpr`,`hello`)
byte-identical to `pint` in m3 AND m4; Pascal `--interp` **36/0/1** (33+3 new probes; XFAIL=recursion);
Icon `--interp` **130/117/36** identical; Prolog honest **135/0/0** — **stash-proven the CLEAN baseline is
also 135** (+2 vs session-11's 133 comes from concurrent `715daa5`/`d46b943`, not this change); SNOBOL4 smoke
**19/0** incl. m4 6/0; all-langs m4 hello **5/1** (the 1 = rebus pre-existing). Stash proof of causation:
clean HEAD gives m4asg ABORT, m4arith ABORT, m4wexpr silent-wrong `2`. NEXT WALLS precisely mapped:
**PB-9c** (`sieve.pas`) now aborts `flat_drive_assign: missing α` — assigns whose operand chain crosses
control-flow nodes (arity −1 resets the operand stack); the real work is the missing `IR_IF/WHILE/FOR/REPEAT`
templates. **PB-9d** (`flatnoarg.pas`) — a REGISTERED proc called with dval==3.0 has NO gvar arm in
`bb_call.cpp` dispatch (line ~262 requires dval==2.0, line ~264 excludes registered) → mode-3 segv in
EMITTED code (the emitter itself is clean: mode-4 emits 192 lines, rc=0); plus CALL-operand BINOPs need
slot-fed operands. flatnoarg's failure MOVED DEEPER vs clean HEAD (was the assign abort) — not a regression,
the function body's `five := 5` now emits and the program reaches the unimplemented call arm. POST-REBASE:
the push rebased onto concurrent `c4da0b1` (PB-RB probe renames, test-only) atop `f406239` (SNOBOL4 m4 scan
loud-bomb); the MERGED tree re-verified green — 4 probes m3+m4 PASS, SNOBOL4 smoke 19/0, Icon 130/117/36,
Prolog honest **136/0/0** (denominator drifted again with concurrent work; the 0-fail/0-abort invariant is
the gate, both honest). SCRIP commit = `40ec5bc`, corpus = `f0adcc5`.

**Watermark — PB-9a LANDED (mode-3/4 seed, LANGUAGE-NEUTRAL) + LANG-BLIND FACT RULE + LB ladder. 2026-06-03,
session 11. SCRIP HEAD = 6cc95c3 (PB-9a = 80ee2e3 after rebase), corpus HEAD = 58a7174 (untouched).**
PB-9a is green BOTH modes: `scrip --run hello.pas` and `scrip --compile hello.pas` → `gcc -no-pie
-lscrip_rt` → run print `Hello World!` byte-identical to `pint`. Implementation DEVIATES from
`PB-9-DESIGN.md` Step 2 on Lon's same-day directive (the new LANGUAGE-BLIND FACT RULE above): instead of a
`__pas_`-prefix arm (which would itself have been a new Tier-1 violator), `bb_call.cpp` gained
shape-dispatched **`bb_call_byname_str`** — guard `g_gvar_flat_chain && dval==3.0 && fn[0] &&
!rt_proc_is_registered(fn)` → `marshal_call_arg` per arg → `rt_call_arr` → `cmp eax,99; je ω; jmp γ` (the
four-port FAIL contract landed at the seed, not deferred to PB-9b). Name knowledge (`__pas_*`) stays in
`src/runtime/by_name_dispatch.c`. Precision proof: `v_det_call` (`lower.c:596`) is the ONLY dval=3.0 setter,
reached only by `IR_LANG_ICN`/`IR_LANG_PAS` (`lower.c:955-6`), and Icon never rides the gvar chain. Design
Step 1 was a NO-OP: `x86_frame_lea` pre-existed (added + REX.B-fixed in `3b655dc`) — no byte-encoder was
touched, defusing the held-for-JIT-byte-risk concern. The push rebased onto concurrent `9e8e4b8` (SNOBOL4 m4
scan, touches `x86_asm.h`+`emit_bb.c`); the MERGED build was re-verified green post-rebase. Gates pinned on
the merged tree: hello m3+m4 byte-identical; Pascal `--interp` 33 PASS (the `33/0/1` bucket decoded: the 1
XFAIL = `recursion.pas`, the documented fact(8)>maxint pint trap rc=217, identical through fact(7); pcom.pas
excluded); Icon `--interp` **130/117/36** identical; Prolog honest **133/0/0**; SNOBOL4 smoke **19/0** incl.
m4 6/0; all-langs m4 hello 5/1 — the 1 = **rebus FAIL-compile, PROVEN PRE-EXISTING on clean HEAD by
stash→rebuild→test→pop** (NOT this change; flag for the Rebus owner). Next PB-9b wall probed: `--run
flatnoarg.pas`/`sieve.pas` abort `flat_drive_assign: lhs (α) must be IR_VAR with sval (got kind=0)` —
Pascal `IR_ASSIGN` under the flat chain is the PB-9b entry point. ALSO this session:
`SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (Tier-1 = 8 named-code sites, Tier-2 = 14 tagged emitted strings, Tier-3
= 3 language-naming C comments; ZERO `IR_LANG_*`/`is_<lang>` guards exist in any template; XA_templates
appendix: scanned CLEAN), the LANGUAGE-BLIND FACT RULE placed atop all 6 `GOAL-*-BB.md`, and the **LB
ladder** (one step per violator) appended at the bottom of this file.

**Watermark — PB-9 DESIGNED (entry mapped end-to-end), build held. 2026-06-03, session 10. SCRIP HEAD = 1d92abc,
corpus HEAD = 58a7174.** No functional code change this session — the deliverable is `SCRIP/PB-9-DESIGN.md`, a
verified turn-key plan grounded by tracing the mode-3/4 path on `hello.pas`. Key reframings vs the goal doc's
"rebase onto `x86_asm.h` and start": (1) **the wiring already exists** — Pascal rides the SNOBOL4 flat chain, so
`--run`/`--compile` already reach `bb_call` with NO `is_pascal` flag, and `rt_call_arr` (`by_name_dispatch.c:1828`)
already reaches `try_call_builtin_by_name`; (2) **the seed's apparent one-liner is a trap** — `rt_builtin_is_known`
omits `__pas_*`, but its target arm `rt_call_builtin` is a dead `STACKLESS_ABORT` stub (`rt/rt.c:529`); the live
path is `rt_call_arr` with a marshalled args array; (3) **the one missing primitive** is a frame-ADDRESS helper
(`lea rsi,[r12+off]`) — only value load/store exist in `x86_asm.h`. **PB-9a (the `hello.pas` mode-3/4 seed) is
FORKLESS and turn-key** (recipe in the design doc: add `x86_frame_lea`, add a `__pas_*`-guarded `bb_call` arm
reusing `marshal_call_arg` → `rt_call_arr`). Held because it touches the JIT byte-encoding path (a wrong byte
segfaults silently, not a compile error) and deserves a fresh-budget build+2-mode-test+full-regression+commit pass.
**Ladder above the seed:** PB-9b (arith/assign/`writeln(expr)`) → PB-9c (the stretch: `IR_IF/WHILE/FOR/REPEAT` have
NO emitter templates, must be authored per FACT RULES; `sieve` gate) → PB-9d (flat procs/params) → **PB-9e = the
representation FORK (frame-as-BB / static-link-as-parent-port-thread, Invariants 2 & 4) — Lon's call, exactly the
PB-7 model.** Baselines RE-VERIFIED green this session (direct rebuild + suites): Pascal **33/0/1**, Icon `--interp`
**130/117/36**, Prolog honest mode-2 **133/0/0** (0 fail / 0 abort — the invariant; the script's PASS denominator
differs from the 132 in prior watermarks, both honest). SNOBOL4 smoke 2/0.

**Watermark — PB-8 COMPLETE: pointers/`new` landed. 2026-06-03, session 9. SCRIP HEAD = f79fae0, corpus HEAD = 58a7174.**
**PB-0..PB-7 + PB-6b green; PB-8 DONE in full — `record` + `set` + pointers/`new`.** Next rung is PB-9 (mode-3/4
compiled BBs). Pointers ride the **NV heap rail** with **one** small `IR_LANG_PAS`-gated `lower.c` arm and **zero**
interpreter structural changes: all pointers are **integer cell numbers** sharing one file-scope counter
(`g_pas_heap_ctr`), `nil`=`ilit(0)` (integer 0, distinct from every allocation — a STRING key was tried first and
REJECTED because it coerces to 0 and collides with nil under `<>`), heap cell key = `__heap_<n>`. Record cells
store the **SOH-packed record on the array rail** so `arr_get` handles field reads for free. Parser: `nil`→
`ilit(0)`; `new(p)`→`p := __pas_alloc()` (scalar) or `p := __pas_alloc_rec(nf)` (record, `nf` from the pointed-to
rectype) with the write-back routed through `mk_assign` so `new(head^.next)` (allocate into a **field**) works;
`^` deref→`__pas_deref(p)`; scalar `p^ := v`→ the `lower.c` arm → `__pas_deref_set(p,v)`; record `p^.field`→
`TT_IDX(__pas_deref(p), ilit(idx))` (read = `arr_get` for free; write = parser `mk_assign`→`__pas_field_set(p,idx,v)`
read-modify-write of the SOH cell). **Chained** `head^.next^.val` resolves via per-field pointer-target tracking
(`fldptrto[]` in the rectype table) + mutually-recursive `pas_selector_rectype`/`pas_ptrexpr_target`. Pointer-to-
record **parameters** register in both value and `var` parameter arms (else `p^.field` inside a proc body falls to
`TT_FIELD` — the bug `ptr8` caught). A second bug `ptr4` caught: a record's pointer **field** (`next:link`) leaked
`g_pas_pend_ptrtarget` up to the enclosing `type:` rule, mis-registering the record itself as a pointer type —
fixed by clearing the leaked target in the record/array/set/file `type` arms and propagating the `-3` pointer
sentinel through `type: simple_type`. Five name-gated builtins (`__pas_alloc`, `__pas_alloc_rec`, `__pas_field_set`,
`__pas_deref`, `__pas_deref_set`). Probes `ptr1..ptr8` byte-identical to `pint`: scalar; two-cell arithmetic; `nil`
compare; linked list with chained deref; build-in-loop+`while` traversal (`p := p^.next`); aliasing/identity;
pointer-as-param + `new`-on-field. **Pointer limits (deferred, no probe forces):** variant-record `new(p,tag)`,
`dispose`, nested records, `with`; the flat `g_pas_ptrvars`/`g_pas_ptrtypes` tables are global (same scoping
limitation as arrays/recvars). Zero cross-language regression (direct rebuild + full-suite, AND a stash/rebuild
byte-identical proof for the spot-check): Icon `--interp` **130/117/36** (exact baseline, every bucket pinned),
Prolog **0 fail / 0 abort** (111 `.expected`-covered programs), Pascal suite **25/0/1** + 8 pointer probes = 33/0/1.
All edits on the `LANG_PASCAL`/`IR_LANG_PAS` path. (Note: this push rebased cleanly onto concurrent SNOBOL4/Icon/
Prolog commits that also touched `lower.c`; the merged build was re-verified green before push.)

**PB-8 SETS (session 9) — still green.** Sets ride the
**integer-bitmask rail** with **zero lower/interpreter structural changes** — a `set of 0..47` is a 48-bit mask
stored as `INTVAL`. Parser maps `[a,b,c]`→`__pas_set(a,b,c)` and `e in s`→`__pas_in(e,s)`; a set-var table
(type sentinel `-2` in `var_decl`) lets `pas_is_setexpr` redirect `+`/`*`/`-`/`<=`/`>=` to
`__pas_setuni`/`__pas_setint`/`__pas_setdif`/`__pas_subset`/`__pas_super` **only when an operand is a set-expr**,
leaving integer arithmetic untouched; `=`/`<>` work for free via bitmask integer compare. Seven name-gated
builtins in `script_try_call_builtin_by_name` (`by_name_dispatch.c`). Probes `set1,set2,set3,set5,set6,set7,set8`
byte-identical to `pint` (incl. **overlapping union** `{1,2}+{2,3}`→3, the case integer-`+` got wrong). **Set
ranges `[a..b]` confirmed OUT OF SCOPE** — the corpus `pcom.pas` itself rejects them (error 6); also note the
corpus oracle is `sethigh=47,setsize=1` (the uploaded `comp.p` is a *different* copy at 63). Zero cross-language
regression: Icon `--interp` **130/117/36**, Prolog honest mode-2 **132/0/0**, SNOBOL4 smoke **2/0**, Pascal suite
**24/24**, `recursion` through `fact(7)` byte-identical. All edits on the `LANG_PASCAL`/`IR_LANG_PAS` path.

**Two cross-language borrows logged this session (NOT yet cleaned — Lon reviewed, deferred):** (1) Pascal's
`TT_IDX` lower arms call **Raku-named** helpers `v_raku_det_call`/`v_raku_mutate_writeback` (the documented PB-5
"Raku array rail"; smell is the naming entanglement, not the IR_CALL-to-runtime-helper approach). (2) Pascal
procs are wrapped in the SNOBOL4-style `TT_STMT`+`:subj` envelope — **rebus** is the cleaner precedent (bare
`TT_PROGRAM`, no envelope). Recommended cleanup when prioritized: rename the helpers to neutral names AND drop
the `:subj` envelope for Pascal. (Confirmed NOT contamination: `IR_IF`/`IR_WHILE` are shared imperative-control
IR used by 5–6 frontends with a lang-agnostic interpreter — not language tags; the goal doc's boolean model
relies on `IR_IF`.)

**PB-8 RECORDS (session 8) — still green.**
PB-0..PB-7 + PB-6b green. Records reuse the **existing array rail** with **zero lower/interpreter changes** — the parser resolves
field names to indices at parse time and emits `TT_IDX(record_var, ilit(field_index))` instead of `TT_FIELD`,
so `arr_get`/`arr_set_pure` (PB-5) handle reads/writes and the array-fill prologue sizes the record. Probes
`rec1/rec2/rec3.pas` byte-identical to `pint`. All PB-0..PB-7 probes + cross-language baselines unchanged.

**Records — the design (parser-only, on the array rail):**
- `pascal.y` gains a record-type table `g_pas_rectypes[name]→ordered fields`, a record-var table
  `g_pas_recvars[name]→ordered fields`, and a `g_pas_pend_fields` accumulator that bridges them.
- `record_field` appends each `id_list` name to pending (flat scalar fields; nested-record fields deferred).
- `type_decl` registers the pending fields under the type name (`pas_rectype_add`); a type-alias to a record
  type inherits its fields for free. `simple_type → IDENT` loads a named record type's fields into pending
  (`pas_rectype_to_pend`) so `var p : point` works.
- `var_decl`, if pending is nonempty, registers the var (`pas_recvar_add`) and sizes it via the existing
  `pas_array_add(name, nf-1)` so the program-level array-fill prologue inits it to `nf` "0" segments.
  Pending is reset at the end of every `var_decl`/`type_decl` to prevent staleness across declarations.
- `selector PERIOD IDENT`: if `selector` is a `TT_VAR` naming a record var and the field resolves, emit
  `TT_IDX(var, ilit(index))`; else fall back to `TT_FIELD`. Read context → `arr_get`; `p.f := v` →
  `TT_ASSIGN(TT_IDX,…)` → existing Pascal `v_assign` TT_IDX arm → `arr_set_pure`. Both already worked.
- Reset `g_pas_nrectype`/`g_pas_nrecvar`/`g_pas_pend_nf` in `pascal_parse_string`.

**Record limits (deferred, no probe needs yet):** nested records (record-typed field) — `simple_type`'s
pending load would clobber accumulation mid-record, so a record-typed field is not resolved (falls to
`TT_FIELD`); `with`-statement field shorthand; record-valued `var` params (whole-record by-reference);
per-activation record locals in nested/recursive procs (array-fill prologue is global-name-based, same
limitation as arrays). Whole-record copy `p := q` happens to work (string-value copy via `TT_VAR` assign).

**Zero cross-language regression (direct rebuild + suite run):** Icon `--interp` **130/117/36** identical to
baseline; Prolog honest mode-2 **132/132, 0 ABORT** identical.

**Earlier this session — PB-6b (parameterless function call in expression) — COMPLETE, HEAD 521726d.** A bare
identifier in `factor` that names a declared function now correctly generates a zero-arg call, not a variable read. Gate
`flatnoarg.pas` prints **`10`** (was `0`), byte-identical to `pint`. All PB-0..PB-7 probes + cross-language
baselines unchanged.

**The PB-6b fix (two parts):**
- **Parser (`pascal.y`)**: Added `g_pas_funcs[256]` table + `pas_func_add`/`pas_is_func`. All `FUNCTIONSY`
  declarations (forward + full) call `pas_func_add(name)` at parse time. `mk_ident` now checks the table:
  if the name is a known function, return `mk_call(name, NULL)` (zero-arg `TT_FNC`) instead of `TT_VAR`.
  Reset `g_pas_nfunc = 0` in `pascal_parse_string`.
- **Lowerer (`lower.c`, `v_assign`)**: Added Pascal-guarded case for `TT_FNC` LHS (the result-variable
  assignment pattern `fn_name := expr` that now parses as `TT_ASSIGN(TT_FNC, expr)`): extract callee name
  from `lhs_t->c[0]->v.sval` and emit `IR_ASSIGN` with that name — same behavior as the former `TT_VAR` path.
  Comes before the `lhs_is_var` check; no other paths affected.

**Why PB-6b is correct:** Inside function `five`'s body, `five := 5` has LHS `selector → IDENT("five")` →
`mk_ident("five")` → now `mk_call("five", NULL)` (TT_FNC). The lowerer's new TT_FNC-LHS arm extracts "five"
→ `IR_ASSIGN("five", 5)`. "five" is not in the frame scope → NV write → correct result-var assignment.
Outside (in expression context), `five` in `g := five + five` → `TT_FNC` → `v_det_call` → `IR_CALL("five",
0)` → interpreter invokes `five`'s body → returns NV("five") = 5. Two calls sum to 10. ✓

**Zero cross-language regression (stash→rebuild→diff prescribed method not used; direct rebuild + suite run):**
Icon `--interp` full ladder **130 PASS / 117 FAIL / 36 XFAIL** identical to PB-7 baseline; Prolog honest
mode-2 **132/132, 0 ABORT** identical. All PB-0..PB-7 probes byte-identical, `flatnoarg.pas` now PASS.

**All prior context (PB-7 design model, static-link-as-static-chain, etc.) unchanged — see below.**

**The model (grounded in `pint`'s `base(ld)` + `lod/str (level−vlev)`):** a frame slot is value / reference
(PB-6) / *or now* reachable from a descendant via the static chain. `ProcEntry.decl_level` = lexical level the
routine is **declared** at (main scope = 1; top-level procs = 1, bodies run at 2; their nested = 2, bodies at 3…).
`GenFrame` gains `GenFrame *static_link` + `int level`. At call setup `static_link = pas_base(caller,
caller_level − callee_decl_level)` (the `mst (level−pflev)` rule), `frame.level = decl_level+1`. Uplevel access
reuses PB-6's `Loc` chase: `IR_VAR`/`IR_ASSIGN`, if the name isn't in the current frame's scope, walk
`static_link` (Pascal-guarded) and read/write the found `(frame,slot)` **before** the NV fallthrough. The chain
**bottoms out at NV**: a top-level proc's `static_link` is NULL, a walk reaching NULL resolves against NV — keeps
`sieve` globals + the accidental-pass `nested.pas` correct. Recursion is correct because each call captures the
**caller's** activation as the link before `frame_depth++`, so a nested helper always mutates its *own* parent
activation's local (the `nestrec` proof).

**Files (SCRIP, this commit):** `stage2.h` (`ProcEntry.decl_level`); `pascal.{y,tab.c,tab.h}` (lexical-level
counter via mid-rule `pas_proc_enter`/`pas_proc_exit` on `procedure_decl`'s block; previously-discarded
**non-array local var names** now captured per-proc and appended as a trailing `TT_VLIST` child whose container
`v.ival` carries `decl_level`; regen via the direct `bison -d -o pascal.tab.c pascal.y` workaround,
`pascal.lex.c`/`pascal.l` unchanged; the 1 s/r conflict is the pre-existing dangling-else, **no new conflict**);
`lower_program.c` (`is_function` made **type-aware** — return-var is `TT_VAR`, locals child is `TT_VLIST`, so a
procedure's trailing locals VLIST is never mistaken for a return-var; `lower_sc` = params **then** locals;
`decl_level` read off the locals VLIST); `IR_interp.c` (`pas_base`/`pas_uplevel_find`; `pas_loc_of_name` extended
to chase uplevel so a `var` actual that is an enclosing-frame local resolves too; static-link+level set at the
dval==3.0 call setup, Pascal-guarded; uplevel walk in `IR_VAR`/`IR_ASSIGN` before NV; param loop extended to seat
locals init `NULVCL`); `GenFrame` from `gen_runtime.h`.

**Probes (corpus/programs/pascal/, committed):** `nestrec.pas` byte-identical (`11,21,31`) — the gate;
`nestcount.pas` (sibling nested procs share an outer counter → `3`); `nest2.pas` (three-level nesting, innermost
does a **Δ2 grandparent** uplevel read+write and a Δ1 → `15,101`); `nestfunc.pas` (a nested **function** with its
own param reading uplevel `base`+`n` and returning → `213`). All PB-6 probes + `sieve`/`nested` stay
byte-identical; `recursion` matches through `fact(7)`.

**Proven zero cross-language regression (stash→rebuild→diff, the prescribed method):** Icon `--interp` full
ladder **130 PASS / 117 FAIL / 36 XFAIL identical baseline-vs-post**; Prolog honest mode-2 **132/132, 0 ABORT
identical**. Baseline `nestrec` confirmed `11,11,11`, post `11,21,31`. All edits stay isolated to the
`LANG_PASCAL`/`IR_LANG_PAS`-guarded path.

**SEPARATE GAP FOUND — parameterless function call in an expression (its own rung, NOT PB-7).** A bare identifier
in `factor` parses as `selector → mk_ident → TT_VAR` (a variable read); only `IDENT(...)` with parens becomes a
call. So a zero-arg function used in an expression (`x := f + f`) reads an unset variable → `0`. This hits **flat
functions too** (discriminating probe `flatnoarg.pas`, committed, XFAIL: oracle `10`, scrip `0`), so it is
orthogonal to nesting — no prior probe exposed it because `fact`/`fib`/`inner(k)` are all parameterized. The fix
needs its own design: the parser/lower must know which identifiers are **function names** and turn a non-local
bare-IDENT-that-is-a-function into a call (careful not to turn genuine variable reads into calls). Recommend as
the next small rung **PB-6b** before PB-8.

**16-bit overflow (still deferred).** `fact(8)`=40320 > `maxint`=32767: `pint` traps, SCRIP computes 40320. Its
own integer-model rung.

**PB-6 value+`var` params (sessions 5–6) — still green.** Value params + functions + procedures +
procedure-as-statement; `var` (pass-by-reference) via the unified slot-reference model (a frame slot is a value or
a reference to a location `(frame,slot)`/`(NULL,NV-name)`; setup resolves the actual's location in the caller,
chasing → transitivity + `f(a,a)` aliasing; `var` actuals that aren't simple variables still fall back to
by-value). `varparam`/`swap`/`alias`/`vartrans`/`varframe`/`varmix` byte-identical.

**Two residual issues (NOT introduced by Pascal work — flagged for attention):**
- `scripts/regenerate_parser_and_lexer_from_sources.sh` is `set -e` and ABORTS at the snobol4 flex step
  (clobbers `snobol4.lex.c`, never reaches the Pascal stanza at the end). Workaround: regen Pascal directly —
  `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y && flex --noline -o pascal.lex.c pascal.l` —
  then `git checkout` the snobol4 generated files. Script wants a fix.
- `test/raku/rk_array_literal.raku` FAILS on the CLEAN baseline (pre-existing, proven by stash+rebuild).

**Lower-priority Icon adjacency (driver plumbing, not LOWER semantics):** `src/driver/polyglot.c:43,90,128`
— `LANG_PASCAL` is gated alongside `LANG_ICN`/`LANG_RAKU` in the init guard, proc-table collection, and
`nparams` shape. Break into its own clauses when convenient for zero adjacency.

---

## The Pascal rail (architecture facts that bind ongoing work)

Pascal has its own rail end-to-end: parser tag **`LANG_PASCAL`=6** (`src/parser/snobol4/scrip_cc.h`), IR tag
**`IR_LANG_PAS`=7** (`src/contracts/IR.h`), own body walker **`lower_pascal_body`** (`src/lower/lower_program.c`),
own program dispatch (`lower_program.c`). Parser emits **real AST** (no desugaring): `TT_FOR`/`TT_REPEAT`/
bare-`TT_IF`, and `TT_PROC_DECL` with `c[3]`=return-var present iff it's a function. LOWER dispatch shape is
**outer `switch(tree->t)` → inner `switch(cx.lang)`** — share an arm where behavior is identical, dedicated
arm where it diverges. `v_pascal_for` + `v_pascal_repeat` (`src/lower/lower.c`) lower **directly to IR**
(compose IR nodes, wire the four ports by hand; no synthetic AST). Driver mode-2 for Pascal is the
`!is_icon && !is_prolog` branch in `scrip.c` → finds `main`, runs `IR_interp_once`.

**Key design facts (PB-4/5/6):**
- **Output:** `__pas_writeln`/`__pas_write` take interleaved `(value,width)` arg pairs. Integer right-justified
  in `max(w,digits)`, default width 10 (real 20); string as-is; `:w` is a **minimum**; `__pas_writeln`
  appends `\n`. `__pas_sqr(x)`=x*x.
- **Arrays:** keep `TT_IDX` faithful in the parser; translate at LOWER on the Raku array rail — `TT_IDX` →
  `arr_get`; `a[i]:=v` → `a := arr_set_pure(a,i,v)`. `arr_set_pure` does NOT auto-grow, so the parser prepends
  an init prologue sizing the array to `high+1` SOH-packed "0" segments (raw index; slots `0..low-1` wasted).
- **Booleans:** `IR_IF` branches on `IS_FAIL_fn`. Stored booleans must survive the array round-trip, so encode
  true=`INTVAL(1)`/false=`INTVAL(0)`; a bare-boolean condition is wrapped `expr ≠ 0` (`pas_cond`). `and`/`or`
  are `TT_MUL`/`TT_ADD` in this grammar so they wrap too.
- **Functions:** body ends with `IR_RETURN`(dval 0.0) whose `α` is `IR_VAR(funcname)`; `fact := …` writes the
  NV global (funcname not in frame scope), `IR_RETURN` reads it back. Correct under recursion because each
  call clears `FRAME.returning` before the enclosing NV write.
- **Parse-time tables** (reset per parse): `const` folding, array name→high, `true`/`false`→`ilit(1/0)`,
  `sqr`→`__pas_sqr`.

---

## Target dialect — the P4 subset, NOT full ISO 7185

The target is the **P4 Pascal subset** — the language `pcom` actually compiles. Authoritative spec is
`pcom.pas`'s `const` block plus `grammar/pascalp.y`. Practical bounds:
- **Files:** only predefined `text` files (`input`, `output`); no user file variables.
- **`goto`:** intra-procedure only.
- **Sets:** small base type (`set of 0..58`).
- **Types:** integer (**16-bit `maxint = 32767`**), real, char, boolean, enumerated, subrange, `array`,
  `record`, `set`, pointer (`new`); value + `var` params; nested routines.
- **Absent:** first-class strings, `dispose`, later ISO niceties. If `pcom` rejects a probe, it is **out of
  scope, not a bug.** Climb only as far up this subset as the probes demand.

---

## ⚖ Provenance guardrail — the SCRIP frontend stays commercial-clean

The SCRIP Pascal frontend is **original C**, written fresh. `pcom.pas`/`pint.pas` are a **private behavioral
oracle**, used only to check SCRIP's output during development — **never transliterated into the lowering,
never linked into `scrip`, never shipped.** Syntactic reference = the MIT-licensed grammar; semantic
reference = `pint`'s observable behavior + the P4 subset above. Read the reference to learn what a construct
*means*, then write the C yourself.

---

## The crux: nested-function frames ARE Byrd Boxes (PB-7 design intent)

Pascal contributes **one** genuinely new construct: **nested procedures/functions** — a routine declared
inside another, able to read/write the enclosing routine's locals (uplevel / non-local addressing).
Everything else is wiring an existing AST shape to an existing lowering (arithmetic, assignment,
`if`/`while`/`for`/`repeat`, compound statements, value/`var` params, return values — all already lowered).

A Byrd-Box graph **is already an activation-record stack**. In the P-machine, `mst` reserves a frame, `cup`
enters it, and frames chain through a **static link** (the classic display). In SCRIP that chain is **the
parent-port thread of the BB graph** — no separate display array, no C frame struct.

Design intent (refine at PB-7, not before):
- Each routine activation is a BB; its **α/β/γ/ω** ports carry the four-port contract; the **static link to
  the lexical parent** travels as the parent-port reference the BB already holds.
- **Uplevel access** = walk `level(use) − level(decl)` parent links and read the slot (port-chasing).
- **100% Byrd Boxes, zero C Byrd-box functions, stackless.** No closures — the P4 subset has no
  first-class/returnable functions, so a frame never outlives its parent; uplevel access is always to a live
  ancestor frame.

This stresses the frame/scope dimension of the BB model the way Prolog stresses backtracking and Icon
stresses generators.

---

## Invariants (inherited from Command Central)

1. **No AST walking in modes 2/3/4.** Lower to IR, then interpret/emit.
2. **Zero C Byrd-box functions.** A Pascal frame is a BB, not a C function.
4. **Four ports hard-wired.** `BB_node_alloc` bakes α=nd, β=nd, γ=NULL, ω=NULL; static link rides the
   parent-port thread.
6. **Builder/consumer case rule.** UPPERCASE builds IR; lowercase consumes.
16. **THE RULE.** From PB-9 on (mode-3/4): no byte emitted unless it carries a BB/SM/XA opcode; every box is
    one `x86(...)` concat emitted by `bb_emit_x86`; `bb_bin_t` is abolished. Early rungs are mode-2
    (`--interp`) only.

---

## Where things live

| Thing | Path | Role |
|-------|------|------|
| **Reference compiler** | `corpus/programs/pascal/pcom.pas` | Grammar + semantics oracle. |
| **Reference P-machine** | `corpus/programs/pascal/pint.pas` | Execution oracle. Diff SCRIP's output against it. |
| **Token + grammar blueprint** | `corpus/programs/pascal/grammar/pascalp.{l,y}` | lex tokens → `TT_*`; yacc grammar scopes the parser. (MIT.) |
| **Probes** | `corpus/programs/pascal/` (`recursion.pas`, `sieve.pas`, `README.md`) | Our own Pascal probes + bootstrap writeup. |
| Pascal frontend | `src/parser/pascal/pascal.{l,y}` | Source → `TT_*` → shared AST. |
| Lowering | `src/lower/lower.c` + `lower_program.c` | Pascal AST → shared IR; nested-frame lowering at PB-7. |
| Mode-2 interpreter | `src/interp/IR_interp.c` | Executes the IR. The early-rung target. |
| BB templates | `src/emitter/BB_templates/` | Only from PB-9 (mode-3/4). |

**Start every Pascal session by reading the reference grammar** (`pascalp.l` tokens, `pascalp.y` productions).

---

## Session Setup

```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip > /tmp/build_full.log 2>&1
[ -x /home/claude/SCRIP/scrip ] || { grep -E "error:|fatal error" /tmp/build_full.log | head -5; exit 1; }
for r in /home/claude/SCRIP /home/claude/corpus /home/claude/.github; do
    ( cd "$r" && git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com" )
done
# Reference toolchain (the oracle) — build once with Free Pascal:
( cd /home/claude/corpus/programs/pascal && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas )
```

Check a probe against the oracle:
```bash
cd /home/claude/corpus/programs/pascal
./pcom < probe.pas && cp prr prd && ./pint < /dev/null   # reference output (the oracle)
/home/claude/SCRIP/scrip --interp probe.pas              # SCRIP output — must match
```

---

## The Rung Ladder

- [x] **PB-0 — Orient.** Reference `pcom`+`pint` built; grammar/opcodes read.
- [x] **PB-1 — Lexer → `TT_*`.** Pascal flex lexer, case-sensitive lowercase-only P4 keywords, `(* *)`+`{ }`
  comments, `'...'` strings with `''` escape.
- [x] **PB-2 — Parser → AST.** Bison grammar from MIT `pascalp.y`; full P4 statement/expression grammar;
  declarations parsed (const/array tables built, rest discarded for now).
- [x] **PB-3 — SEED.** `scrip --interp hello.pas` prints `Hello World!`, byte-identical to `pint`.
- [x] **PB-4 — Integers, `var`, assignment, `writeln(int)`.** `__pas_writeln`/`__pas_write` width formatting,
  byte-identical to `pint`. (16-bit overflow deferred to PB-6.)
- [x] **PB-5 — Control flow + `sieve.pas` gate.** All control flow byte-identical to `pint` via Pascal LOWER
  arms on real `TT_FOR`/`TT_REPEAT`/`TT_IF` (IR-direct, not desugaring). Arrays + const + `sqr` + booleans;
  `sieve.pas` gate MET (25 primes, 2..97).

- [x] **PB-6 — Top-level (flat) procedures & functions.** Value params + functions + procedures +
  procedure-as-statement (session 5): `recursion.pas` byte-identical to `pint` through `fact(7)`. **`var`
  (pass-by-reference) params DONE** (session 6) via the unified slot-reference model — a frame slot is a value
  or a reference to a location `(frame,slot)`/`(NULL,NV-name)`; setup resolves the actual's location in the
  caller (chasing → transitivity + `f(a,a)` aliasing) and installs it as the callee slot's reference; the
  primitive PB-7 uplevel reuses. `varparam`/`swap`/`alias`/`vartrans`/`varframe` byte-identical to `pint`; zero
  cross-language regression proven (Icon 130/117/36, Prolog 132/0/0 identical baseline-vs-post). Open-but-not-a-
  blocker: `var` actuals that aren't simple variables (array element/field) fall back to by-value. **DEFERRED:
  16-bit overflow** (`fact(8)` aborts in `pint` with an unmatchable fpc crash dump) — its own integer-model rung.
- [x] **PB-7 — NESTED procedures & functions (THE NEW RUNG).** A routine declared inside another,
  reading/writing the enclosing locals. **DONE** via static-link-as-static-chain: `ProcEntry.decl_level`,
  `GenFrame.static_link`+`level`, parser lexical-level counter + non-array-local capture, `lower_sc`
  params-then-locals, `pas_base(caller, caller_level−decl_level)` at call setup, uplevel walk in
  `IR_VAR`/`IR_ASSIGN` before NV. Gate `nestrec.pas` `11,21,31`; probes `nestcount`/`nest2`/`nestfunc`
  byte-identical; Icon 130/117/36 + Prolog 132/0/0 identical baseline-vs-post.
- [x] **PB-6b — Parameterless function call in an expression (SEPARATE GAP, recommend before PB-8).** A bare
  identifier in `factor` parses as a variable read, not a call; only `IDENT(...)` becomes a call. So a zero-arg
  function in an expression (`x := f`) reads an unset variable → `0`. Hits flat functions too (probe
  `flatnoarg.pas`, XFAIL: oracle `10`, scrip `0`) — orthogonal to nesting. Fix: parser/lower must know function
  names and promote a non-local bare-IDENT-that-is-a-function to a call (without turning genuine variable reads
  into calls). `pcom.pas` uses these heavily. **DONE**: `g_pas_funcs` table in parser; `mk_ident` promotes;
  `v_assign` TT_FNC-LHS arm handles `fn := expr` result-var assignment. `flatnoarg.pas` PASS (oracle 10). ✓
- [x] **PB-8 — Aggregates as needed.** `record`, `array`, `set`, pointers/`new`. **ALL DONE** — `record`
  (session 8), `set` (session 9), pointers/`new` (session 9). Records via field→index on the PB-5 array rail;
  sets via the integer-bitmask rail (`[..]`, `in`, `+`/`*`/`-`/`<=`/`>=`/`=`/`<>`); pointers on the NV heap rail
  (integer cell numbers, `nil`=`ilit(0)`, one `lower.c` arm). All zero lower/interp structural change.
  `rec1/rec2/rec3`, `set1,set2,set3,set5,set6,set7,set8`, `ptr1..ptr8` byte-identical to `pint`. Set ranges
  `[a..b]` out of scope (oracle rejects). Deferred (no probe forces): variant-record `new(p,tag)`, `dispose`,
  nested records, `with`, record-valued `var` params, per-activation record locals. `array` was PB-5.
- [ ] **PB-9 — Cross onto compiled BBs (mode-3/4).** Convert Pascal's boxes to the `x86()` self-encoding API
  per the FACT RULES (one `x86(...)` concat per box, `bb_emit_x86`, no `bb_bin_t`). **DESIGNED** (session 10) —
  see `SCRIP/PB-9-DESIGN.md`. Wiring already exists (flat-chain ride); seed (`hello.pas`) blocker is the dead
  `rt_call_builtin` stub + the missing `x86_frame_lea` helper, not a "rebase from scratch". Sub-rungs:
  **PB-9a** seed (FORKLESS, turn-key recipe in the doc) · **PB-9b** arith/assign/`writeln(expr)` · **PB-9c** the
  template-authoring stretch (`IR_IF/WHILE/FOR/REPEAT` have NO templates; `sieve` gate) · **PB-9d** flat
  procs/params · **PB-9e** nested procs = the frame-as-BB representation FORK (Invariants 2 & 4, Lon's call, the
  PB-7 model). Build held: PB-9a touches the JIT byte path (wrong byte = silent segfault) → fresh-budget pass.
  - [x] **PB-9a — seed.** `hello.pas` mode-3 + mode-4 byte-identical to `pint` (session 11, SCRIP 80ee2e3).
    Landed LANGUAGE-NEUTRALLY per the FACT RULE — shape-dispatched `bb_call_byname_str` → `rt_call_arr`,
    FAIL→ω contract included; NO `__pas_` string in the template (supersedes PB-9-DESIGN.md Step 2).
  - [x] **PB-9b — arith/assign/`writeln(expr)`.** DONE (session 12) — four shape-dispatched walls knocked
    down, all language-blind; probes `m4asg`/`m4arith`/`m4wexpr` + `hello` byte-identical to `pint` in BOTH
    mode-3 and mode-4. See watermark for the wall list, the two new `rt_gvar_get_*` helpers, and the
    precisely-mapped PB-9c/PB-9d entry points.
  - [x] **PB-9c — control flow.** DONE (session 13) — `sieve.pas` byte-identical to `pint` in BOTH mode-3
    and mode-4. Five walls knocked down, all shape-dispatched/language-blind; new template
    `bb_binop_gvar_relop.cpp`. See watermark for the wall list and the PB-9d entry map.
  - [x] **PB-9d — flat procs/params.** DONE (session 13, same session as PB-9c) — `recursion.pas`
    byte-identical to `pint` through fact(7) in BOTH modes; `flatnoarg.pas` byte-identical both modes.
    Three pieces: registered dval==3.0 call arm, marshal nested-CALL generalization, gvar arith-slot
    template, plus the IR_RETURN gvar junction (the α-clobber fix). See watermark.
  - [ ] **PB-9e — nested procs = the representation FORK (Lon's call).** Frame-as-BB, static link on the
    parent-port thread (Invariants 2 & 4, the PB-7 model).

---

## The LB Ladder — LANGUAGE-BLIND BB/XA templates (Lon directive 2026-06-03, session 11)

Fix every violator inventoried in `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (audit at SCRIP `80ee2e3`; line
numbers drift with edits — re-grep per step). Lon's mechanism for Tier-1 code arms: **replace the snippet
with an ABORT** (`x86_bomb` body keeps the dispatch shape; any surviving traffic fails LOUD and names
itself). Where a violation is naming-only the step says rename — confirm with Lon before downgrading a
prescribed ABORT to a rename. EVERY step: run the named gate, pin before/after counts in this file, prove
zero drift elsewhere (stash→rebuild→diff where feasible). XA_templates scanned CLEAN — no XA steps.

LB BATCH LANDING NOTE (session 13): SCRIP `37eefa1`, rebased onto concurrent `d2405a6` which did PARALLEL
overlapping cleanup the same hour — ONE conflict (bb_catch.cpp LB-7 wording, both sides neutralized
WAM-CP-13; resolved to d2405a6's "non-admitted shape" text). Merged tree re-verified: SNOBOL4 19/0, Icon
130/117/36, Prolog 136/0/0, sieve + recursion m3 green.

- [x] **LB-1 — Raku-named arm → ABORT.** DONE (session 13). Arm at (drifted) `bb_call.cpp:311` now
  `x86_bomb("IR_CALL dval=2 descr-chain arm aborted per LANGUAGE-BLIND rule")`. MEASURED DELTA: raku smoke
  m4 PASS 2→1 / FAIL 0→1 — the moved test is `str_reverse` (m3 was already FAIL); m2 HARD 25/0 unchanged;
  raku m4 rung 0/47 unchanged (all-FAIL baseline). Cross-language pin: SNOBOL4 19/0, Icon --interp
  130/117/36, Prolog 136/0/0, all-langs m4 5/1 — zero drift.
- [x] **LB-2 — `bb_call_rk.cpp` deleted.** DONE (session 13). File + extern + 2 Makefile entries gone;
  `.Lrkarg` → `.Lcallarg`. Build clean, gates as LB-1.
- [ ] **LB-3 — `DEFINE` name-gate → ABORT. DEFERRED (session 13) — the only LB step left before FENCE.**
  Investigation note for next session: the abort would drop SNOBOL4 smoke m3/m4 from 6/6 to ~5/5 (floors
  3/4 — survivable but ugly); the CLEAN re-route is LOWER tagging DEFINE with its own IR shape (a dval or
  a dedicated kind) so dispatch needs no name. Prefer re-route + abort in one step so the gate never moves.
- [x] **LB-4 — Icon fork RESOLVED AT THE UNIFICATION TARGET (not abort).** DONE (session 13). Rationale:
  the fork carried LIVE GN-4/5 traffic AND two concurrent ICN-SCAN sessions were mid-flight this hour —
  an abort would have invalidated their in-flight pins; the step's own stated target ("ONE shape-dispatched
  bb_gvar_assign") was achievable with ZERO drift, so unification chosen over abort. The fork body moved
  verbatim into `bb_gvar_assign_str` as a `g_descr_flat_chain` first arm (x86_begin + sealed-RO idiom
  preserved; slotless rhs → in-arm bomb preserving the fork's failure mode); `emit_core.c:419` re-pointed.
  PROOF: Icon NV-global probe m4 `.s` before/after MODULO-ID BYTE-IDENTICAL (the only diff = bb<addr>
  box-ID labels, proven run-noise by same-binary double emission); Icon --interp 130/117/36; crosscheck
  3/1 with the 1 (`if_expr`) stash-proven pre-existing on clean HEAD. If Lon wants the prescribed ABORT
  regardless, it is now a one-line change to the unified arm.
- [x] **LB-5 — decl removed with LB-4.** DONE (session 13).
- [x] **LB-6 — `bb_pl_op_floaty` → `bb_op_floaty`.** DONE (session 13), all 3 sites. Gate: Prolog honest
  136/0/0 (count moved 133→136 by concurrent PT-1b/PT-2b before this step; unchanged by the rename).
- [x] **LB-7 — Tier-2 sweep, AUDIT SCOPE.** DONE (session 13) for every audit-enumerated site (the
  `bb_call_rk.cpp:37` site vanished with LB-2): BOX SNO → BOX (bb_call ×2, bb_binop_gvar_arith,
  bb_gvar_assign ×4, bb_scan_stmt); WAM-CP tags out of bb_catch/bb_choice/bb_goal; ICN-HY-4 tag out of
  bb_to; bb_var tags → mode words (gvar/descr flat-chain) + neutral bombs (bb_var, bb_gvar_assign concat).
  NEW INVENTORY (post-audit, NOT swept — concurrent ICN-SCAN sessions actively own these): `# BOX ICN`
  tags in bb_gen_scan.cpp:19,36, bb_keyword.cpp:23,32,43,54,64,73, bb_scan_any.cpp:19, bb_scan_match.cpp:20
  (+ siblings bb_scan_pos/tab/upto) — sweep when ICN-SCAN settles, or fold into their next rung.
- [x] **LB-8 — Tier-3 C comments deleted.** DONE (session 13): bb_choice header + the 5-line inline
  cluster (separators preserved — first attempt over-deleted 2, caught and redone precisely), bb_goal
  header, bb_builtin_term_inspect 2-line comment. Gate: Prolog 136/0/0.
- [ ] **LB-FENCE.** COMPLETION TEST green: the audit's Tier-1 grep over `BB_templates/` + `XA_templates/`
  == 0; full matrix pinned (Pascal · Icon · Prolog · SNOBOL4 · all-langs m4 hello) with every delta from
  LB-1..LB-8 accounted for in this file.
