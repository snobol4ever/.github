# FINDING: `icon-n2-recursive-generator-per-activation-storage`'s two most recent FINDINGs (seat08, `8a6dd4a3` and `e63df29c`) patched and reasoned about a call site that NEVER EXECUTES for the witness they used — gdb-confirmed, resolving the "routing doubt" seat08's own last pass raised but couldn't settle

## WHAT THIS ANSWERS
seat08's last pass (`e63df29c`) flagged an unresolved doubt: is `bb_call_proc_staged.cpp`'s self-recursion depth-push/region-LEA code (the `+16` constant everyone has been patching and reasoning about) even the branch that executes for the minimal repro (`vsr3.icn`), or does a different branch run? Their own suggested resolution — assemble a real linked mode-4 binary, `objdump -d` it, break by address in gdb — is exactly what this FINDING does. **The answer is more consequential than either "yes" or "no": the CODE PATH exists and runs, but not at the call site seat08 (and everyone building on their numbers) was reading.**

## SETUP (per seat08's own suggested recipe)
```
SCRIP_ICN_N2_SELFREC=1 ./scrip --compile -o vsr3.s vsr3.icn
gcc -no-pie -g vsr3.s -L"$SCRIP/out" -lscrip_rt -Wl,-rpath,"$SCRIP/out" -lm -lpthread -o vsr3.bin
objdump -d vsr3.bin   # real addresses + preserved local labels (n51_proc_gen_bx etc. survive as symbols)
```
`vsr3.icn` is the exact 15-line repro from `FINDING-2026-08-29-seat08-geddump-error3-not-host-region-overlap-real-defect-in-call-site-plus16-constant.md` Part 2 (a `walk`/`node` self-recursive tree-walker, no corpus dependency). Reproduces byte-identically: unarmed rc=134 GENHOST bomb, armed rc=1 Error 3.

## THE PROGRAM HAS THREE `walk`-CALL SITES, NOT ONE — seat08's numbers belong to the one that never runs
`SEAT01_N2_STEP3_DBG=1` at compile time dumps all three registered nodes:
```
node=0x36276150 callee=walk host_flat_lcl_proc=0 off=0     base=48    <- walk's OWN recursive call (walk(!r.sub))
node=0x36286cb0 callee=walk host_flat_lcl_proc=1 off=21504 base=1552  <- main's FIRST call  (every r:=walk(root) do r.ref:=id[r.data])
node=0x36286810 callee=walk host_flat_lcl_proc=1 off=0     base=1552  <- main's SECOND call (every r:=walk(root) do write(...))
```
**seat08's two FINDINGs both cite `off=0 base=1552`** — that is the THIRD line, main's SECOND call site, in the source statement that only runs (if it ever did) after the first `every` loop completes.

## GDB, BREAKING BY ADDRESS, NOT BY COMMENT OR ASSUMPTION
Compiled-label addresses (survive as real ELF symbols — `objdump -t` confirms):
- `off=0/base=1552`'s region-LEA (`lea rcx,[rsp+1568]`, i.e. `1552+0+16`): **`0x402a65`**, inside `n64_proc_gen_bx`.
- `off=21504/base=1552`'s region-LEA (`lea rcx,[rsp+23072]`, i.e. `1552+21504+16`): **`0x402448`**, inside `n51_proc_gen_bx`.
- the recursive call's region-LEA (flat_gen arm, `lea rcx,[rbp+48]`, no `+16`): **`0x401627`**.

Breaking on all three and running once:
```
break *0x402448   <- HIT (n51, main's FIRST call)
break *0x401627   <- never hit
break *0x402a65   <- never hit (seat08's own call site)
```
**`n64`'s breakpoint (seat08's `off=0/base=1552`) is never reached at all — the program crashes and exits before main's second statement is ever compiled-into-reached.** This single fact invalidates the byte-for-byte-identical-corruption test in `e63df29c`: patching `bb_call_proc_staged.cpp`'s `+16` constant and re-testing showed "no change" not because the fix was insufficient, but because the patched instance of the constant (there is one instance of the *source line*, but it is specialized per call site at compile time into as many copies as there are call sites — three, here) was never on the executed path in the first place. Nor is the recursive call ever reached: **the crash happens entirely within main's FIRST call to `walk(root)` and what follows it — no actual recursion (`walk(!r.sub)`) is ever attempted.** This matches every prior session's "fires on the very first activation" observation, now pinned to a specific, confirmed call site rather than assumed.

## TRACED FORWARD FROM THE REAL CALL SITE TO THE CRASH
Continuing from the `0x402448` breakpoint (no further breakpoints needed — the program runs to the crash on its own from here): the recursive-call and second-main-call breakpoints are never hit before `subscript_get` is entered and raises Error 3. Breaking on `subscript_get` (`pattern_match.c:222`) and inspecting its arguments directly:
```
arr = {v = 64, mod_op = 224, src_node = 36671, slen = 32767, s = 0x0, ...}   <- garbage: v=64 is not a valid DT_* tag
idx = {v = 2 (DT_S), s = "root"}                                             <- correct: this is id["root"]
```
`idx` is exactly right (`r.data` for the root node is the string `"root"`). `arr` — which should be `id`, the table built two statements earlier — is corrupted, **with the identical signature** (`src_node=36671`/`0x8F3F`, invalid type tag) that `FINDING-2026-08-29-seat07-geddump-error3-arr-corruption-traced-to-stack-slot-collision-not-random-garbage.md` and `FINDING-2026-08-29-seat16-geddump-error3-gdb-confirmed-garbage-descr-t-plus-a-missed-selfrec-branch.md` found on `geddump.icn` itself. This is strong (not yet fully proven identical) evidence that `geddump.icn`'s Error-3 and this minimal repro's Error-3 are the SAME underlying mechanism, corroborating seat08's own repro design intent.

Stepping to `FN__walk`'s own prologue (`0x4012a6`) and past its `mov rax,[rsp+16]` region-pointer load: `rax` is a real stack address (`0x7ffffffe8c28`), and `rax - rsp` (at that point) is **23096** — close to but not exactly the pushed `1552+21504+16=23072` (a 24-byte gap, consistent with additional words pushed between the region-LEA and the `jmp` into the callee, e.g. `bcps_wire_cross_gen`'s own continuation pushes — not fully accounted for by hand here; see NEXT ACTOR). Not claiming this proves or disproves an off-by-N defect at the real call site — flagging the concrete number for whoever continues, per this row's own standing lesson that hand arithmetic on this exact code has repeatedly misled prior passes.

## WHAT THIS DOES AND DOES NOT SETTLE
**Settles:** seat08's "routing doubt" — yes, `bcps_spine_gen_arm`'s self-rec depth-push/region-LEA code genuinely executes (comment/note text proving nothing either way, since `x86("comment",...)` is unconditionally stripped to `""` in `x86_asm.h:1624` for every branch, and `x86("note",...)` never fired anywhere in this build either — checked, zero `#@` lines in the whole 96KB `.s`, so absence of either proves nothing about branch selection; only the presence/absence of the branches' own distinguishing instructions, like `sub rsp,8`, does). **Also settles:** the specific instance of that code seat08 patched and hand-reasoned about (`off=0/base=1552`) is not it — a sibling instance at the SAME source line, specialized to a different call site (`off=21504/base=1552`), is what actually runs. **Does NOT settle:** the actual corruption mechanism at the real call site — that is now open again, cleanly, from a confirmed starting point (`n51_proc_gen_bx`, region base 1552+21504, `arr`'s corruption confirmed at `subscript_get`), not a continuation of anyone's prior `off=0` arithmetic.

## NOT ATTEMPTED
No fix landed, no source touched. Root cause 2 (sibling-generator reservation formula) and mutual recursion (c) remain untouched and are still explicitly Lon/hq design territory per this row's GOAL — this FINDING is entirely about which code runs for the ALREADY-in-scope narrow defect class, not the general design question.

## NEXT ACTOR
1. **Redo seat08's `+16`→`+8` empirical test against the RIGHT call site** (`n51_proc_gen_bx`, `off=21504/base=1552`, address `0x402448` in a fresh rebuild) — it was never actually tested; everything cited as "confirmed insufficient" was measured against dead code for this witness.
2. **Reconcile the 24-byte gap** between the pushed region pointer (`rsp_push+23072`) and what `FN__walk` actually receives (`rax-rsp_walk=23096`) — this needs the intervening pushes (`bcps_wire_cross_gen(3,4)` and anything else between the region-LEA and `jmp rax`) counted precisely, not estimated, before trusting either number as the true expected/actual delta.
3. **Confirm or refute `id`'s slot address for this specific call site** the same way seat08 did for the (wrong) other one — locate `id := table()`'s write address in `main`'s frame and check whether it's reachable from `n51`'s actual region arithmetic or the generator-call landing/epilogue path (L(3)/L(8)/L(9) in `bcps_spine_gen_arm`), not just the initial call-site push.
4. Root cause 2 and mutual recursion (c): unchanged, still Lon/hq design territory.
