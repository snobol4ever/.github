# FINDING 2026-08-24 (seat03) — row `vlist-v05-m4-sigsegv-m3-m4-divergence`: the m3≢m4 crash is NOT the disjunction's spine cell — it's a genuine memory-safety bug in EVAL's runtime indirect-call path, valgrind-localized

## HEADLINE

The task brief's own hypothesis ("suspect the m4 medium's spine depth around the new disjunction flat-cell")
is **exonerated by direct measurement**: `v01_select_min.sno`, which uses the exact same `IR_DISJUNCTION`
construct as `v05`, runs **100% valgrind-clean** under mode 4. `v05`'s crash is a real memory-safety defect —
valgrind catches an **invalid read of an unmapped address (`0x1F00000000`) inside libc's `getenv()`**, reached
via an `atexit` handler, meaning something earlier in execution performed a wild write that corrupted process
state (most likely `environ` or an adjacent glibc global). Every "uninitialised value" warning valgrind flags
along the way — including inside `rt_define_tiny_ok` (`rt.c:1785`) — is **not disjunction/zeta-storage code at
all**; all of it sits inside **EVAL's runtime code-generation path for an indirect procedure call**
(`*push_list(...)`, `*pop_final(...)` — the classic SPITBOL `epsilon . *Foo(...)` trampoline idiom, here built
from a dynamically-constructed `EVAL()` string, not a literal source pattern) or the deferred pattern-capture
pump. ⛔ The `rt_define_tiny_ok` lead was tested this session with a one-line kill-switch (`SCRIP_NO_TINY=1`)
and **did not fix the crash** — read the "RECOMMENDED NEXT STEP" section below before chasing it further; the
exoneration of the disjunction construct is solid, but which specific EVAL/capture site is the true root cause
is still open.

## WHAT'S CONFIRMED, MEASURED THIS SESSION

- **m3/m4 split reconfirmed** on current tree (SCRIP `1a9cc1bc`, post `0e57de3b` + `9df28b03`): `v05` mode 3
  prints `MATCH size=1` correctly, rc=0. Mode 4 (`--compile` + `gcc -no-pie` + `libscrip_rt.so`): **no stdout at
  all**, rc=139 (SIGSEGV, core dumped).
- **`v01` is valgrind-clean under mode 4** (`valgrind -q ./v01_bin`, zero output, rc=0) — same
  `IR_DISJUNCTION`/`disj_sigma_copy`/`fc_geom` flat-cell path the task brief suspected, minimal witness,
  completely exercised, zero corruption signal. This rules out the disjunction's own codegen as the culprit for
  `v05`'s crash; whatever's wrong is specific to something `v05` does that `v01`–`v04` don't.
- **`v05` under `valgrind -q` (no `--main-stacksize` override, default 60s timeout)**: several "Conditional
  jump or move depends on uninitialised value(s)" warnings preceding the fatal one, most specifically —
  ```
  ==PID== Conditional jump or move depends on uninitialised value(s)
  ==PID==    at 0x4B95240: rt_define_tiny_ok (rt.c:1785)
  ==PID==    by 0x4DDFF40: bb_tiny_shim_ok (bb_call_proc_staged.cpp:204)
  ==PID==    by 0x4DE5BB6: bcps_det_arm()::{lambda()#1}::operator()() const (bb_call_proc_staged.cpp:266)
  ==PID==    by 0x4DF9B59: bcps_det_arm() (bb_call_proc_staged.cpp:263)
  ==PID==    by 0x4E0F0F0: bb_call_proc_staged_str[abi:cxx11](IR_t*) (bb_call_proc_staged.cpp:859)
  ==PID==    by 0x4DDAA6A: bb_call[abi:cxx11](IR_t*) (bb_call.cpp:510)
  ==PID==    by 0x4BE1531: walk_bb_node_inner (emit.cpp:1254)
  ==PID==    by 0x4BDA8A3: walk_bb_node (emit.cpp:975)
  ==PID==    by 0x4BE807A: emit_drive (emit.cpp:1520)
  ==PID==    by 0x4C12DCE: codegen_flat_chain_body (emit.cpp:3086)
  ==PID==    by 0x4C1BB17: emit_chain (emit.cpp:3421)
  ==PID==    by 0x4BB6102: eval_thunks_emit_from (runtime_eval.c:188)
  ```
  **This is the emitter running AT RUNTIME, inside the compiled `v05_bin` process itself** — `eval_thunks_emit_from`
  is EVAL's mechanism for JIT-compiling a dynamically-built string (`EVAL("epsilon . *push_list(" vs ")")`,
  line 65 of the witness) into a fresh Byrd-box chain and executing it, by calling back into the SAME
  `emit_chain`/`codegen_flat_chain_body`/`walk_bb_node` machinery that `scrip --compile` itself uses at
  ahead-of-time compile time. `bb_call_proc_staged_str` → `bcps_det_arm` → `bb_tiny_shim_ok` is a call-site
  optimization deciding whether an indirect call (`*push_list(...)`) can use a cheaper "tiny shim" ABI —
  `rt_define_tiny_ok` (rt.c:1782-1786) makes that decision by reading `p->dyn_scope`, `p->is_generator`,
  `p->is_variadic`, `p->redefined` off the `rt_proc_t` registry entry for `"push_list"`, and valgrind says one
  of those fields is uninitialized memory at the time of the read.
- Several more "uninitialised value" warnings follow, all inside EVAL/pattern-capture machinery
  (`eval_cache_insert_raw`/`eval_cache_get` in `runtime_eval.c`, `table_set_descr_d` in `aggregates.c` via
  `rt_assign_var`/`rt_dcap_pump`/`rt_match_end_all` — the deferred-capture-and-assign pump for the unanchored
  scan `'ab' ? p :F(NO)` at the witness's line 91) — **not reproduced or investigated in depth this session**,
  listed here so the next pass doesn't have to re-discover them.
- **The fatal error**: `Invalid read of size 1 at getenv (getenv.c:31), by zop_audit_report (zeta_storage.c:904),
  by __run_exit_handlers, by exit, by main_γ. Address 0x1F00000000 is not stack'd, malloc'd or (recently)
  free'd.` `zop_audit_report` is an `atexit`-registered diagnostic hook (registered from
  `zop_audit_graph_close`, `zeta_storage.c:894-896`) that calls `getenv("SCRIP_ZOP_AUDIT")` as its first act.
  glibc's `getenv` crashes walking `environ` — meaning `environ` (or a pointer glibc's `getenv` depends on) has
  already been corrupted to an absurd, clearly-non-pointer-shaped value (`0x1F00000000` — plausibly a
  SNOBOL4-domain integer like `31` landing in a pointer-sized slot via a tagged-value/DESCR mixup, though this
  is speculation, not verified). **Because this crash happens inside an atexit handler, it also swallows the
  program's own buffered stdout** — `v05`'s actual computed result may well be correct (mode 3 says so) and the
  crash purely destroys visibility into that fact, which is why `--run` mode's own terminal output never
  appears even though `main_γ` had already reached `exit()`.
- **EVAL itself is not broadly broken under mode 4**: `corpus/crosscheck/rung10/{1016_eval,1019_eval_string,1022_eval_fail}.sno`,
  `crosscheck/control/expr_eval.sno`, and `crosscheck/patterns/{140,141}_pat_eval_*.sno` are all part of the
  clean, fully-passing crosscheck suite (mode 4 included). The `epsilon . *Foo(...)` indirect-call idiom is
  also independently exercised (and passing) in `beauty.sno`, `json.sno`, `porter.sno`,
  `calculator-2.sno`, `include/semantic.inc` — **as a literal source pattern**, not as the return value of a
  dynamically-constructed `EVAL()` string. The narrower, untested combination appears to be: **EVAL of a
  dynamically-built string, where that string itself contains an indirect-call trampoline, invoked from inside
  real (non-tail, multi-frame) SNOBOL4 procedure recursion (`ListInsert`/`ListAppend`), running inside a
  `--compile`-built (mode 4, gcc-linked) process.**

## WHAT THIS FINDING DOES NOT ESTABLISH

- **Not proven**: that `rt_define_tiny_ok`'s uninitialized read is the actual ROOT cause of the wild write that
  later corrupts `environ`-adjacent memory, as opposed to a downstream symptom of something else already wrong,
  or a red herring that happens not to matter (an uninitialized boolean read can take a wrong branch without
  itself writing bad memory). It is the **first** point in the crash's causal chain where valgrind can name a
  concrete, file:line-precise defect, which makes it the natural next place to look — not a confirmed fix target.
- **Not investigated**: whether `rt_proc_register`'s "already exists" branch (`rt.c:448`, which deliberately
  does NOT touch `is_generator`/`dyn_scope`/`is_variadic`/`jmp_entry` — correct behavior for genuine
  redefinition, since it sets `redefined=1` and `rt_define_tiny_ok` checks `!p->redefined`) is actually what's
  firing here, versus a THIRD registration path. `rt_proc_register_rec` (`rt.c:1948-1959`) only calls
  `rt_proc_register()` (the fully-zero-initializing path) when `r->flags & 1` is set; if unset, the subsequent
  `rt_proc_set_fn`/`rt_proc_set_nparams`/`rt_proc_set_nformals` calls all silently no-op via `rt_proc_find`
  returning NULL (verified: `rt_proc_set_nparams`/`rt_proc_set_nformals`, `rt.c:561-571`, both guard on
  `if (p)`) — so THAT path looks safe on inspection, but was not traced against v05's actual DEFINE/registration
  sequence to confirm which path `"push_list"` actually goes through, nor whether some OTHER writer touches
  `g_rt_gen_procs` entries outside `rt_proc_register`'s two branches.
- **Not attempted**: any fix. Per this row's own repeated, hard-won lesson (this same investigation area has
  already produced multiple "confident but wrong" attempts across prior sessions — see the superseded
  `vlist-expr-alternation` FINDING's own corrections), a genuine memory-safety bug reached through a chain this
  long deserves targeted instrumentation (e.g., a temporary assert/fprintf on every write to a `push_list`
  `rt_proc_t` entry's `is_generator`/`is_variadic`/`dyn_scope` fields, or a valgrind `--track-origins=yes` run
  to get the uninitialized value's allocation site directly) before any code change, not a guess.

## RECOMMENDED NEXT STEP

1. ⛔ **TESTED THIS SESSION, NEGATIVE RESULT — do not re-propose this as the fix:** `SCRIP_NO_TINY=1
   v05_bin` (which makes `bb_tiny_shim_ok` return 0 unconditionally at its very first line, before reaching
   `rt_define_tiny_ok` at all) **still crashes rc=139, same as without it.** This means `rt_define_tiny_ok`'s
   uninitialized read, while real (valgrind still flags it independently of whether its result is later used
   for a tiny-shim decision), is **not sufficient on its own to explain the fatal crash** — either it's a
   genuinely inert red herring (an uninitialized boolean read that happens not to matter because both branches
   are otherwise safe), or the real wild write happens somewhere else in the chain regardless of which ABI path
   `bb_call_proc_staged_str` takes. **Correcting my own hypothesis in real time rather than leaving it
   standing unconfirmed.**
2. The other valgrind-flagged "uninitialised value" sites — `eval_cache_insert_raw`/`eval_cache_get`
   (`runtime_eval.c:54/47`) and `table_set_descr_d` (`aggregates.c:428`) via `rt_assign_var`/`rt_dcap_pump`/
   `rt_match_end_all` (the deferred-capture-and-assign pump servicing the witness's own `'ab' ? p :F(NO)`
   unanchored scan-with-capture at line 91) — are now the **more promising** leads, specifically because they
   involve mutable shared state (a cache, a table assignment) rather than a read-only ABI-choice flag. Neither
   was tested against a `SCRIP_NO_TINY`-style cheap kill-switch this session (none may exist) — worth checking
   for one before instrumenting by hand.
3. Re-run `valgrind --track-origins=yes` on `v05_bin` (this session used plain `-q`) targeting the
   `eval_cache_*`/`table_set_descr_d` sites specifically now that the tiny-shim lead is ruled insufficient — it
   names exactly where the uninitialized bytes were allocated/left unset, which is the fastest path to a real
   root cause from here.
4. Do not chase the `zeta_storage.c:904` `getenv()` crash site itself — it is confirmed to be a **victim**, not
   a cause (an ordinary `getenv()` call against corrupted global state), and "fixing" it (e.g., by removing the
   `atexit` audit hook) would only hide the real defect and additionally stop losing the diagnostic evidence
   this FINDING relies on.
5. Whatever the mechanism turns out to be, this session's strongest confirmed result stands regardless: it is
   **not** `zd_plan`/`emit.cpp`'s disjunction dispatch/`bb_disjunction.cpp` (v01 exonerates that construct
   directly), so the fix almost certainly belongs in the EVAL runtime path (`runtime_eval.c`) or the
   pattern-capture pump (`pattern_match.c`/`aggregates.c`), not in this row's own VLIST/disjunction code.

## ⭐ ADDENDUM (same session, after `valgrind --track-origins=yes`) — a strong structural match to hq_P's PROVEN Icon generator-frame defect, same session

Ran `valgrind --track-origins=yes` on `v05_bin` per the recommendation above. **All five "uninitialised value"
origins trace to the exact same place**: `rt_slab_get`/`rt_slab_region` (`rt_slab.c:29/51`) → `malloc`, called
from either `_parse_define_spec` (at process-startup `DEFINE` registration) or `c_rt_str_alloc`/`c_str_concat_d`
(GC-heap string allocation). This is the signature of a slab/GC allocator that does **not** zero fresh pages —
normal, expected behavior for this class of allocator — so these five warnings are very likely **benign
false-positive noise**, not the defect. **Correcting my own prior framing**: the `rt_define_tiny_ok` /
`eval_cache_*` / `table_set_descr_d` leads named above are probably not where the real bug is; they were just
the first "uninitialised value" reads valgrind happened to reach before the fatal one, not causally connected
to it. Do not spend further time instrumenting those specific functions.

**More useful from this run: valgrind reports ZERO "Invalid write" warnings anywhere before the fatal crash.**
Memcheck normally catches an out-of-bounds or use-after-free WRITE directly, at the write site — it did not
here. Combined with `grep -rn 'setenv\|putenv\|environ' src/runtime/` returning **zero hits** (this runtime
never touches `environ` directly, ruling out "a real call computed the wrong value"), the corruption is not a
bounds violation valgrind's shadow memory can see, and not a deliberate-but-wrong environ write. It has to be a
write that is **in-bounds of some legitimately-mapped region valgrind considers valid, but at the wrong logical
offset** — exactly the shape of the mechanism hq_P proved this same session for a related-but-distinct code
path.

⭐ **The connection**: `.github/FINDING-2026-08-24-hq_P-generator-frame-cannot-live-below-the-callers-rsp.md`
(hq_P, s271, same day) proves — with a two-moment gdb memory read, not a guess — that an Icon `SUSPEND`
generator's activation frame, when carved **below the caller's `rsp`** at the moment of yield, gets silently
overwritten by the very next `call` the caller makes: *"Everything below a C stack pointer is scratch: the
next call owns it."* No bounds violation, no crash at the overwriting write (it's a completely ordinary,
in-bounds stack write from the overwriting call's own point of view) — the corruption only becomes visible
much later, when something still holds a pointer into the now-reused region. **That is exactly v05's evidence
shape**: no invalid write, a real value computed correctly (m3 prints the right answer), and a crash much later
in unrelated code holding a stale pointer. `v05`'s crash chain runs through `eval_thunks_emit_from` — EVAL's
runtime JIT-compilation of `epsilon . *push_list(...)`, an **indirect procedure call construction**, which per
`src/runtime/rt/rt_coexpr.c:74/93/97/164/170` (`rt_gc_root_range_add`/`_del`, `stk_win`, `stk_guard`,
`frame_copy`) plausibly shares the SAME low-level coroutine/activation-frame machinery hq_P's finding is about,
carving some scratch/frame region relative to the CURRENT `rsp` at the moment EVAL's JIT'd chain runs — if that
region is placed below `rsp` the same way the generator frame was, it would be silently reclaimed by
`ListInsert`'s own subsequent recursive calls, corrupting something a much-later GC/string operation still
points at, eventually reaching whatever `environ`-adjacent memory `getenv()` trips over at exit.

**This is a hypothesis pointing at a proven mechanism, not itself proven for v05** — I have not repeated
hq_P's two-moment gdb memory read against v05's own activation/EVAL path this session. Flagged directly to
hq_P (`send hq_P vlist-v05-may-share-your-generator-frame-mechanism`) since they are the ones with the
demonstrated method and the freshest context on this exact failure shape, rather than attempting to
independently re-derive their technique against a much larger, harder-to-isolate witness.

## RECEIPTS

SCRIP `1a9cc1bc` (post `0e57de3b` vlist cure + `9df28b03` tdump-regression fix), `make pristine` fresh build,
`RT_OPT` default `-O0`. `valgrind` (available in-container, `/usr/bin/valgrind`) with default options
(`-q`, no `--track-origins`) against both `v01_select_min.sno` and `v05_treebank_pushlist_235.sno` compiled
`--compile` + `gcc -no-pie -Wl,-rpath,out out/libscrip_rt.so`. `gdb -batch -ex run -ex bt -ex "info registers"`
under `SCRIP_NO_SEGV_HANDLER=1` gave the initial (less informative — points at the `getenv` victim site, not
the cause) backtrace; valgrind is what actually localized this. `test_gate_template_medium_invisible.sh`
checked first (0 BOTH-MEDIUM sites in `bb_*.cpp`, ruling out a literal `MEDIUM_TEXT`/`MEDIUM_BINARY` branch as
the mechanism, before reaching for valgrind).

## ⭐⭐⭐⭐ ADDENDUM 2 (new session) — EVAL IS NOT THE MECHANISM (refuted by direct test); root cause CONFIRMED via gdb software watchpoint: a disjunction box writes outside its own frame when reached through a deferred-pattern-call-at-match-end path, not through hq_P's generator-frame mechanism

Checked inbox per the prior NEXT block: hq_P replied (`the-connection-is-plausible-heres-the-discriminator...`, resent clean after a
backtick-eaten first copy) with PLAUSIBLE-BUT-UNPROVEN status and a discriminator question: *"does anything v05 writes need to
SURVIVE a return the emitted thunk makes? If nothing must survive, the mechanism is different even if the code is shared."*
Also reiterated RULES.md's mandated order: ASM-DIFF-FIRST, ablate toward a minimal witness before gdb. Both directly informed
what follows.

### The EVAL hypothesis is REFUTED, not just unconfirmed

Ablated `v05_treebank_pushlist_235.sno` (94 lines) down incrementally, re-testing the m3-pass/m4-SIGSEGV signature after every
cut (dead code first: `Push_item`/`Pop_list`/`ListName` are never called by the driver; then the unread `tags` TABLE; then
flattened `push_list`'s body to one call; then dropped `Init_list`). Each cut preserved the crash. **One cut mid-way pulled the
call out of pattern-construction context entirely (a bare top-level `Push_list("'BANK'")` statement) — this did NOT crash in
either mode, but also gave the WRONG value (`size=0` in both m3 and m4, not just m4) — a self-inflicted semantic bug from
restructuring the witness, not a finding about the defect. Recorded here so it is not re-attempted: pattern-construction
context for the call is load-bearing for CORRECTNESS, separately from whatever is load-bearing for the CRASH.** Reverted that
one step and continued ablating conservatively.

The decisive test: swapped `Push_list`'s body from `EVAL("epsilon . *push_list(" vs ")")` to the literal, non-EVAL form
`epsilon . *push_list(vs)` — the exact idiom this same file already used, untested until now, for the never-called `Pop_list`
wrapper — with the matching caller-argument change (`Push_list("'BANK'")` → `Push_list('BANK')`, since the literal form takes
the value directly rather than a string to re-parse). **The crash survives unchanged.** EVAL, `eval_thunks_emit_from`,
`runtime_eval.c`'s runtime-JIT machinery are NOT in the picture at all for this defect — the headline and Addendum 1 above
were chasing the wrong subsystem. Also tested and ruled out as necessary: `EVAL` string-building, the `Init_list` wrapper, a
second `list()` call nested in argument position (flattened to a temp var — still crashes), and two levels of DEFINE'd-proc
call nesting (`push_list → ListAppend → ListInsert` collapsed to `push_list → ListInsert` directly — still crashes).

**Minimal witness: 94 → 49 lines**, committed as `corpus/probe/vlist_select/v06_defer_call_disjunction.sno` (+ `.ref`,
`MATCH size=1`) — m3 PASS, m4 SIGSEGV rc=139, reproduced from the committed file itself, not just the scratch copy.

### The clean flip, and what it isolates

One more single-variable change flips the witness to a clean PASS in **both** modes with the **same correct value**
(`MATCH size=1`, matching m3 and the oracle-implied answer, not a different wrong number): change `Push_list`'s body from the
deferred-expression pattern call `epsilon . *push_list(vs)` to an ordinary direct call `push_list(vs)` (no `epsilon .`, no
`*`). Nothing else differs. This is now the cleanest possible ASM-diff pair (`ab9.s` vs `ab10.s` in scratch, same shape,
differing only in how the one call is invoked) and it answers hq_P's discriminator precisely: **the deferred `*E` pattern
form is necessary for the crash; the ordinary direct-call form is not just "also broken" or "differently broken" — it is
fully correct.**

### hq_P's specific mechanism does NOT appear to apply here — corrected in place

hq_P's PROVEN defect is: a SUSPEND generator's frame is carved on the C stack, control returns out to a caller that runs
FURTHER arbitrary code (e.g. `write()`), and the caller's own next `call` silently reclaims the frame — no suspend, no bug.
Tracing `*push_list(vs)`'s actual execution (gdb, see below) shows **no coroutine, no `rt_coexpr.c`, no pthread switch, and no
suspend/resume anywhere in this path** — `push_list` runs to completion in one straight-line nested-call sequence, exactly
like an ordinary procedure call, then returns normally. hq_P's own finding text describes pattern-blob (`*P DEFER`) execution
as the SAFE contrast case precisely because "the blob's caller ... does not run arbitrary code below the retained frame" —
and that description fits what's actually happening here (no external arbitrary code runs while anything is suspended,
because nothing is ever suspended). **Correcting the connection flagged to hq_P last session: plausible on the evidence
available then, but the actual mechanism (below) is structurally different — not a shared root cause with the Icon generator
defect.** Message sent to hq_P and hq_C with this correction and the new mechanism (see LEDGER).

### The confirmed mechanism — gdb software watchpoint (hardware watchpoints do not work in this container, per hq_P's warning and CLAUDE.md)

`environ` is corrupted, deterministically, at a fixed address under `gdb` (ASLR is disabled by gdb's own `run` by default in
this container — addresses were byte-identical across separate `gdb -batch` invocations on the unchanged binary, confirmed
before trusting a hardcoded address). One `environ[]` slot's low 32 bits are zeroed while its high 32 bits stay intact
(`0x00007fffffffe79f` next to it vs the corrupted `0x00007fff00000000`) — the signature of a 32-bit store landing on the low
half of an 8-byte pointer slot, not a wild 64-bit-pointer write.

Set `set can-use-hw-watchpoints 0` (forces a software watchpoint — slow, but this witness is small enough to finish well
inside a timeout) on the exact corrupted qword's address, from `break main` (before any SNOBOL4 code runs) — NOT from a
Greek-lettered Byrd-box label (`break main_γ` silently produced a "charset conversion failure" warning and the breakpoint
never actually fired; ASCII-only symbols are safe, unicode port labels are not, for `break` in this gdb build). The watchpoint
fires exactly once:

```
Old value = 140737488349128   (0x00007fffffffe79f — valid stack address)
New value = 140733193388032   (0x00007fff00000000 — corrupted)
0x0000000000404879 in n157_disjunction_α ()
```

`objdump -d` at that PC (crashing binary, address confirmed via `nm`):

```
40486e:  c7 84 24 f0 06 00 00 00 00 00 00   mov DWORD PTR [rsp+0x6f0], 0x0
```

**A disjunction box (`n157_disjunction_α` — the `LT(place,0) n(x)+place` idiom used throughout `ListValue`/`ListInsert`,
compiled to `IR_DISJUNCTION`) writes a 32-bit zero to a fixed, large, statically-computed offset (`0x6f0` = 1776 bytes) from
its OWN current `rsp`, intending to land inside some ancestor frame's reserved "flat frame" scratch region. When this exact
box is reached through the deferred-call-at-match-end path (see next section), the actual runtime `rsp` at that point is not
what the static offset assumed, and the write overshoots all the way to the process's `environ` array near the top of the
initial stack.** This is a genuine, confirmed, reproducible defect — not a guess, not an inference from a victim site.

### Why v01 was "exonerated" and v05/v06 are not — reconciled, not contradictory

Addendum 1 (this same file) reported `v01_select_min.sno` — same `IR_DISJUNCTION` construct — 100% valgrind-clean, and used
that to rule out "the disjunction's own codegen" as the culprit. That measurement was correct and remains correct for HOW
`v01` calls it: directly, at pattern-construction time, shallow call depth. **It does not generalize to "the disjunction
construct has no bug"** — it only shows v01's specific (shallow, non-deferred) invocation never reaches the buggy path. The
task brief's ORIGINAL hypothesis ("suspect the disjunction's spine depth") was closer to right than Addendum 1 gave it credit
for; what was missing was the trigger condition: **the SAME disjunction code, reached via a `*E` deferred-pattern call whose
real invocation is pumped at match-end (`rt_dcap_pump`, `pattern_match.c:685`, calling an internal `*EXPR$0` thunk — confirmed
via breakpoint, `e->varname = "*EXPR$0"`) rather than during the ordinary match traversal, sits at a different (deeper, and/or
differently-computed) `rsp` than the fixed compile-time offset assumed.** The clean flip (deferred call → crash, direct call →
correct) isolates exactly this trigger; it does not by itself prove which side of the arithmetic is wrong (the disjunction
box's offset, or something in the `EXPR$0` thunk / `rt_call_proc_descr` / `rt_proc_enter` tail-jump chain that under- or
over-adjusts `rsp` relative to what the disjunction box's offset was compiled against).

### NOT established — the actual next step

- **Which specific fixed-offset computation is wrong is not yet located, but the AOT-path analog IS found — narrower than
  it was an hour ago.** `runtime_eval.c:180-184`'s `g_flat_frame_floor`/`zls_g_region` logic (EVAL-at-runtime registration —
  does not apply, this witness has no EVAL) turns out to have an **identical AOT `--compile`-path counterpart, duplicated
  FOUR times** in `src/driver/scrip.c` (lines 1278, 1467, 1663, 1793 — byte-for-byte the same block each time): it sets
  `g_flat_frame_floor` from **`main`'s own `zls_g_region`** whenever the proc being registered is either an `LBL__`-prefixed
  label proc, or its entry IR node is `IR_GOTO_DEFERRED` (or `IR_DEFINE` with `ival==3`). `zls_g_region`/`g_flat_frame_floor`
  are then consulted repeatedly in `emit.cpp` (at least lines 2345-2346, 2803-2806, 3154, 3280-3313, 3396-3411) to decide a
  chain's "flat frame" layout/floor. **Not yet confirmed**: whether `EXPR$0`'s own IR entry is actually classified
  `IR_GOTO_DEFERRED` (plausible by name/shape, not verified by instrumenting the lowerer or by reading `lower_snobol4.c`'s
  four `IR_GOTO_DEFERRED`-emitting sites, 797/807/819/1929, against what an `*E` pattern lowers to) — if it is, the
  hypothesis writes itself: the floor is pinned to `main`'s region on the assumption that a `GOTO_DEFERRED`-shaped chain
  always executes "in place" relative to `main`'s own frame (true for an ordinary jump-wired label/goto), but `EXPR$0`
  reached via `rt_dcap_pump`'s C-level `rt_call_proc_descr` call is several REAL, C-ABI, register-passing call frames
  removed from `main` by the time it runs (`rt_match_end_all` → `c_rt_dcap_end_ok_open` → `rt_dcap_pump` →
  `rt_call_proc_descr` → `rt_proc_enter`), so `main`'s region is not actually where its runtime `rsp` sits. Two cheap
  instrumentation attempts this session came up empty and are recorded so they are not retried as-is: `SCRIP_STF_DEBUG=1`
  at compile time produced zero `[STF]` lines for this witness (the gated fprintf at `emit.cpp:3411` never fires — its own
  `_stf`/`_stfj` condition is false here, for a reason not chased further), and `SCRIP_RTPAT_DIAG=1` at run time produced
  zero `[RTPAT-DIAG]` lines (`bb_pat_build.cpp:104`'s gate isn't reached on this witness's call path either). Whoever
  picks this up next should instrument `g_flat_frame_floor`'s four `scrip.c` write sites and its `emit.cpp` read sites
  directly (a one-line `fprintf(stderr, ...)` on write, gated by proc name, is probably faster than chasing an existing
  diagnostic flag that turns out not to cover this path) rather than repeat these two dead ends.
- **No fix attempted.** Per this row's own repeated lesson (RULES.md, and this file's own LEDGER), do not ship a fix ahead of
  locating the actual offset-computation defect — the mechanism is now precisely characterized (down to the exact instruction
  and address) but the ROOT arithmetic error (which side is wrong, and why) is not yet found.
- `v06_defer_call_disjunction.sno`/`.ref` committed to `corpus/probe/vlist_select/` as a fast (49-line), confirmed-reproducing
  regression witness for whoever takes the fix — much cheaper to re-run/re-diff/re-gdb than the 94-line original.

### RECEIPTS (this addendum)

Reconfirmed after rebuilding against `0f4231f8` (Lon's direct commit, same day, landed mid-session: `RT_DCAP_ISLAND_BYTES`
4MB→64MB, a DIFFERENT defect in the same `pattern_match.c`/`rt_dcap_pump` neighborhood — an `r12` bump-allocator
overflow, not the `rsp`-relative static-offset desync this addendum documents). Both `v05_treebank_pushlist_235.sno`
and `v06_defer_call_disjunction.sno` still SIGSEGV rc=139 in m4 at `0f4231f8`, unchanged — Lon's fix does not touch
this defect, as expected given the different register/mechanism.

SCRIP `1a9cc1bc` (unchanged from Addendum 1's receipts — investigation only this session too, zero source changes).
`gdb -batch` under `SCRIP_NO_SEGV_HANDLER=1`, `set can-use-hw-watchpoints 0` (hardware watchpoints do not fire in this
container — confirmed by way of hq_P's own warning, not independently re-discovered the hard way). `objdump -d -M intel`
against the minimized witness's `--compile` output for the exact instruction. `nm`/nothing beyond stock binutils + gdb 
needed. Ladder sanity-checked unaffected (m3 PASS, unchanged source) before commit: `c01`, `c02`, `v01`-`v04`.
