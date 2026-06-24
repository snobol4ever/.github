# HANDOFF 2026-06-24 (Claude Opus 4.8) — PASCAL-BB: real floor is 115/12, single root = arith over a call-producing operand

## TL;DR
- **Frontier #1 (pcom `const`-hang) is CLOSED** by `e706a9a` ("PASCAL-BB: fix local char-array backing (digit/strng in insymbol uninitialized)"), which landed *after* GOAL-PASCAL-BB.md's Session-64 CURRENT STATE was written. That section of the goal file is **stale** and should be rewritten. Verified: `const n=3; begin end.` compiles cleanly through pcom in M3 **and** M4, 5/5 deterministic.
- **The documented "127/0" does not reproduce.** Real reproducible floor at HEAD (`9f828cb`) is **M3 115 pass / 12 fail** (XFAIL/no-ref = 23, of which 22 are pre-existing `pcom_*` scratch probes + `recursion`). "127" = the count of ref-bearing probes (153 `.pas` − 3 skipped − 23 without `.ref`). **M4 gate not yet run this session.**
- **One root cause explains 10 of the 12 fails:** a BINOP whose operand is a *call-producing* expression — array subscript (`arr_get`), record field (`field_get`), or a user function call — never has that operand's producing call emitted. The add then reads a stale slot and **collapses to the left operand**. Scalar / literal / frame-var operands are fine (hence scalar arithmetic works and the gate isn't worse).

## Repro (minimal, M3 `--run`, all deterministic)
```
a[1]:=3; a[2]:=4; writeln(a[1] + a[2])   -> 3   (exp 7)   # two arr_get operands
writeln(a[1] + 100)                        -> 3   (exp 103) # arr_get + literal
writeln(100 + a[2])                        -> 100 (exp 104) # literal + arr_get
p.x:=3; p.y:=4; writeln(p.x + p.y)         -> 3   (exp 7)   # two field reads (storage is FINE; p.x and p.y print 3/4 individually)
f+g  (f returns 3, g returns 4)            -> 3   (exp 7)   # two user-fn-call operands  <-- proves it is "call operand", not "aggregate"
x+y  (scalars)                             -> 7   (exp 7)   # CONTROL passes
```
`matmul` (`c[i,j] := c[i,j] + a[i,k]*b[k,j]`) → all zeros; `arr2dtype`/`arrparam` (`s := s + a[i,j]`) → crash/wrong. Same root; spans **both** call-arg BINOPs (`writeln(...)`) and assignment-RHS BINOPs (`s := s + ...`).

## Decisive evidence (M4 `.s` for `writeln(a[1]+a[2])`)
In the `__pas_writeln` BOX the generated code emits **one** `arr_get` (for `a[1]`) into `[r12+272]`, then hands `[r12+272]` straight to `writeln`. **No second `arr_get`, no `add`.** The right-operand subgraph is never walked. → rules out register-clobber; it is missing emission of the operand's producing call.

## Where it lives (localized, NOT yet patched)
1. `src/emitter/emit_bb.c:2081-2126` — per-arg pre-compute. For an arith-BINOP arg it **correctly defers** to the inline-arith path (L2113-2114 leaves `slots[i] = -1` to preserve the DT_I tag). So this file is doing the right thing; do not "fix" it by pre-computing here.
2. `src/emitter/BB_templates/bb_call.cpp:125-170` — the arith operand (`a`/`b`) handlers for the inline call-arg arith path. They handle `IR_VAR`, `IR_VAR_FRAME`, `IR_VAR_FRAME_REF`, `IR_LIT_I`, `IR_CALL` with `dv==2.0/3.0`, and `IR_CALL_DEFINE` — **but not a plain `IR_CALL` (`arr_get`/`field_get`) nor a user-function call**. That missing case is the bug for call-arg arith.
3. The assignment-RHS / `IR_BINOP_GVAR_ARITH` + `IR_BINOP_GVAR_ARITH_SLOT` path (`emit_bb.c:246-250` sets `op_parts_lbl`; templates `bb_assign_frame*.cpp` / the gvar-arith templates consume it) has the **same** operand gap and must be fixed in lockstep, else `s := s + a[i,j]` stays broken even after the call-arg fix.

## Fix shape (for the next focused block)
For an arith BINOP operand whose op is a call-kind (`arr_get`/`field_get`/user-fn/`ir_is_call_kind`):
- emit the operand's **producing call into a fresh temp slot** (same machinery `marshal_single_call` / the `IR_CALL_DEFINE` operand arm already use), then reference that temp slot as the arith operand — instead of falling through to a slot that was never produced.
- Preserve the DT_I/real tag handling that L2113-2114 was protecting.
- Apply to **both** operand positions (`a` and `b`) and to **both** the call-arg arith path (bb_call.cpp) and the assignment-RHS arith path.
- Watch the isolated arg-block `g_emit_cfg` save/restore (emit_bb.c:2116-2118) — operand `bb_slot_get`/aux lookups must use the arg-subgraph cfg.

## Verification plan (required before commit)
- Probes above must all flip to correct values.
- Re-run the Pascal M3 **and** M4 gate; expect the records cluster (`rec1-3`, `recparam3`, `with1-3`), the 2D-array cluster (`arr2dtype`, `arr2dtype2`, `matmul`), and `arrparam` to go green (≈10 of 12).
- **This is shared emitter code → run all four language gates (Pascal / Prolog / Icon / SNOBOL) and the template-byte-identity gate before landing.** The recent PB-*-DYN Prolog commits only verified the Prolog floor (115/115); do not repeat that — verify Pascal too.

## Gate-integrity notes (independent of the codegen bug)
- `corpus/programs/pascal/realparam.ref` is **whitespace-only (1 byte `\n`)**. `realparam` aborts (rc=134 — the documented frontier-#2 `flat_drive_assign missing α` family, triggered by a real-valued fn param) and produces no output, so it **false-passes under exact-string comparison** and only shows as a fail under `diff`. The headline pass-count is therefore comparison-method-dependent. Fix the ref (correct value `       3.0`) and treat `realparam` as the genuine frontier-#2 crash it is.
- `corpus/programs/pascal/` carries ~22 `pcom_*` scratch/diagnostic `.pas` with no `.ref` (correctly skipped). Consider moving them out of the probe dir so the testable count is unambiguous.

## pcom self-compilation status (deeper frontier, after the floor is real)
pcom no longer hangs on `const`, but it is not correct: on valid `var x: integer;` it raises a **spurious `error(103)`** ("identifier found, wrong class") from `searchid` — its pointer-BST symbol table corrupts at scale (minimal pointer/record probes round-trip fine). The `errlist[]` (`array[1..10] of packed record`) also fails to round-trip *inside pcom* (`endofline` reads `pos=0`/`nmr=blank` though `error()` wrote `15`/`103`), while the identical shape round-trips standalone. And a program declaring a **procedure segfaults (rc=139 in both M3 and M4)**. These are the endgame; the arith-over-call-operand fix + a trustworthy floor come first.

## Provenance / cleanliness
- SCRIP + corpus trees left clean; HEAD `9f828cb`. (Bisected SCRIP-only across `6e40d63`/`a48c831`/`e706a9a` to confirm the records/2D-array fails predate the recent churn — they reproduce at `a48c831`, so this is older than the PB-*-DYN band, i.e. either a long-standing gap or a regression older than those commits.)
- Instrumentation used a throwaway `/tmp/pcom_dbg.pas` (never committed, oracle untouched).
- This handoff is written but **not pushed** (no push credential this session).
