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

---

## ADDENDUM 3 [seat03, 2026-08-24, fresh session] — root arithmetic LOCATED and quantitatively confirmed; one fix
attempted and DISPROVEN by direct test; **major scope correction: v02 and v03 are ALSO m4-red, always were, via a
DIFFERENT mechanism — the task's own recorded QA baseline undercounted this row's true scope by 2 programs.**

### PART A — the root arithmetic (the thing every prior session on this row named as the missing piece)

⭐ **`EXPR$0`'s graph entry classifies as `IR_DEFINE` with `ival==3` ("kind 3") — NOT `IR_GOTO_DEFERRED`.** Addendum 2
left this "not yet confirmed." Fresh, permanent, env-gated instrumentation added this session (`SCRIP_FLOOR_DIAG=1`,
one `fprintf` per floor-forcing call site — `src/driver/scrip.c` all four sites, `src/emitter/emit.cpp`'s
`emit_jmp_entry_for_proc`, `src/templates/xa_flat.cpp`'s `xa_flat_class_c`; all four kept in the tree, zero cost when
unset, same idiom as the codebase's existing `SCRIP_STF_DEBUG`/`SCRIP_RTPAT_DIAG`/etc.) proves it directly:
```
[FLOOR-DIAG] pname=EXPR$0 is_lbl=0 entry_op=25 hit=1        # 25 = IR_DEFINE (IR.h enum index)
[ARM-REGION] pname=EXPR$0 r=1 floor=4288 frame_bytes=208 seed_off=0 layout_unknown=1 jcon_value_region=160
```
`ival==3` on an `IR_DEFINE` entry is stamped **exclusively** by `sno_expr_thunks_build` (`lower_snobol4.c:2315`), the
lowering routine for the SNOBOL4 `*` unevaluated-expression operator (`sno_expr_collect`, `lower_snobol4.c:85-95` —
confirmed by its own fatal-error text, `"unevaluated-expression operator (*) with no operand"`). Genuine runtime
`EVAL()` **never reaches this code at all**: at lower time it is just an ordinary builtin-name string
(`lower_snobol4.c:1031`, alongside `CODE`/`CONVERT`) dispatched at runtime via `by_name_dispatch.c:310`'s builtin
table into `runtime_eval.c`'s **own, separate** copy of the floor-pinning logic (lines 180-184) — a different
mechanism, a different file, a different time (actual program execution inside the JIT, not AOT `scrip --compile`).
**scrip.c's four floor-forcing sites are therefore exercised exclusively by the `*E` operator family, never by
EVAL**, which matters for Part B below.

⭐ **Confirmed live with gdb, not inferred:** broke on `FN__EXPR$0`'s entry and on `n157_disjunction_α` (Greek labels
silently fail to `break` by name in this container's gdb — as the task file already warns — so `break *0x404852`, the
raw address from `nm`, was used instead):
```
ENTRY rsp = 0x7fffffffdda0                 (FN__EXPR$0 has ZERO prologue: first instruction IS the first box)
N157  rsp = 0x7fffffffdc10                 (only 400 bytes of cumulative per-box "sub rsp,16" descent by box #157)
target addr rsp+1776 = 0x7fffffffe300      (post box's own local sub-16, the write target)
target EXCEEDS entry (target - entry_rsp = +1376)
```
The disjunction box (`bb_disjunction()`, `src/templates/bb_disjunction.cpp:34-36`) writes its `disj.alt_i`/pad cell at
a **fixed, large, positive offset from ITS OWN current `rsp`** (`_.op_off=1760`, i.e. `mov dword ptr [rsp+1776],0` for
the `+16` sub-field) — a scheme that is only safe if a big frame was carved ONCE, early, sized to cover that offset.
**No such carve ever happens for `EXPR$0`.** `nm`/the `.s` confirm `FN__EXPR$0:` has no prologue whatsoever — box #0
runs at the function's literal entry address. The write at box #157 lands **~1376 bytes above `FN__EXPR$0`'s own
entry `rsp`** — not merely "unreserved scratch," but up and into whatever real C stack frames belong to its actual
caller chain (`rt_match_end_all` → `rt_dcap_pump` → `rt_call_proc_descr` → `FN__EXPR$0`, all real x86 `call`s, zero
coroutine/splice — Addendum 2 already traced this chain and ruled out EVAL/generator mechanisms). Given enough
programs/environment layout, that overshoot reaches `environ[]`, silent until `atexit`'s `getenv()` finally reads
through the corruption — matching every prior session's symptom exactly.

⭐ **Why the carve is missing — `xa_flat_class_c()` (`src/templates/xa_flat.cpp:321-326`) bails outright whenever
`g_flat_frame_floor > 0`:**
```c
{ extern int g_flat_frame_floor; if (g_flat_frame_floor > 0) return 0; }   // no carve, full stop
```
Fresh instrumentation on this exact line, run against `v06`, shows **CLASS-C's carve fires ZERO of 8 times in this
program's entire compilation** — 3 bail on `floor`, 3 bail on `no_jmp_entry` (ordinary, non-flat procs — expected,
harmless), 2 bail on `flat_pat` (the `PAT$N` pattern-literal helpers — also expected, harmless). Of the 3 floor
bails, `EXPR$0` is one.

⭐ **Second, independent bug layer, found while checking whether "just let it carve" would even be sufficient — it
would NOT:** `flat_frame_bytes` (the actual carve size `xa_flat_class_c`'s caller would use, `emit.cpp:3297`) is
computed as `(48 + jcon_value_region + 15) & ~15` — **from the CURRENT graph's own native region only, completely
ignoring `g_flat_frame_floor`.** For `EXPR$0`, native `jcon_value_region=160` → `frame_bytes=208`. The disjunction
box's offset (1760) requires ≥ ~1780 bytes. **Even a hypothetical "always carve" patch that did nothing else would
carve 208 bytes and still corrupt memory** — just with a smaller, possibly-still-crashing overshoot. Any real fix
needs `flat_frame_bytes` to account for the floor too, not just the bail in `xa_flat_class_c`.

⭐ **The likely original design intent, now legible:** `main` itself is never floor-forced (it never appears in
either diagnostic's output at all — it must carve its own frame through a separate, dedicated code path, sized to
its own `zls_g_region`, which happens to equal 4288 here). `LBL__`-prefixed graphs (`_is_lbl`, true label-goto-target
duplicates, reached by an ordinary `:(label)` GOTO from code that is *already running inside `main`'s own,
already-carved frame* — SNOBOL4 GOTO never touches `rsp`) correctly skip their own carve and borrow `main`'s region
size, because they are, in fact, still executing with `main`'s own live `rsp`. **`EXPR$0` was swept into the same
treatment by analogy** (its entry also isn't an ordinary named-proc `IR_DEFINE`, so it superficially resembles the
label-alias case) **but it is invoked via a real, several-frames-deep C call chain through `rt_dcap_pump`, not an
in-place GOTO — `main`'s frame is not where its `rsp` actually is, so borrowing `main`'s region without a local
carve is simply wrong for this case.**

### PART B — one fix attempted, and DISPROVEN by direct test (recorded so it is not retried as-is)

Given Part A's tight causal chain, tried the narrowest fix it suggests: remove the `(_pg->entry->op == IR_DEFINE &&
IR_LIT(_pg->entry).ival == 3)` disjunct from all four `scrip.c` floor-forcing sites, leaving `_is_lbl` and
`IR_GOTO_DEFERRED` untouched (kind-3 is lowering-confirmed *E*-exclusive per Part A, so this looked like a clean,
narrow, structurally-justified removal, not a per-op filter — RULES.md's NO-PER-OP-FILTER law was weighed explicitly
before attempting this).

**Result: WORSE, not better.** Mode 4 (`v06`) still SIGSEGV rc=139 (unchanged — did not fix the target). Mode 3, which
was PASSING before this change on every prior session including this one's own reconfirmation, **also started
SIGSEGVing (rc=139)** after the edit. Reverted immediately (`git diff` confirmed byte-identical condition logic
restored, mode 3 re-confirmed `MATCH size=1` after rebuild). **Conclusion: the kind-3/`*E` floor-forcing disjunct is
load-bearing for something beyond just this crash site** — most likely the zls offset-granting pass for *other*
nodes in the same flat island shifts when the floor stops applying to kind-3 graphs, and at least one of those other
nodes' new offset is wrong in a way that mode 3's interpreter loop is *not* tolerant of (whatever slack let mode 3
survive the original, unfixed offset scheme evidently depends on kind-3 also being floor-pinned). **Do not re-attempt
this exact removal without first explaining why mode 3 broke** — that's the concrete unblocking question for
whoever picks this up next, not "does mode 4 pass now."

### PART C — ⭐⛔ MAJOR SCOPE CORRECTION: `v02` and `v03` are ALSO m4-red, confirmed at the task's OWN cited baseline

While re-running the full ladder to sanity-check the (reverted) build, `v02_select_concat_and_assign` and
`v03_array_proto_via_select` **both SIGSEGV rc=139 in mode 4** — contradicting this task file's own `## QA` line
("ladder v01-v05 PASS ... in m3 and m4; m4 v01 PASS, m4 v05 SIGSEGV"). **This is not a new regression**: built SCRIP
`0e57de3b` (the exact commit this row's QA baseline names) in an isolated `git worktree` and reproduced both crashes
there too, byte-for-byte the same signature. **The QA line was wrong from the start, not stale** — v02/v03 were
never actually green in m4; nobody had checked them individually before this session (the row's own probes only ever
singled out v05 for deep investigation). Per THE LOOP protocol (`CLAUDE.md`: "a number that disagrees with the brief
... is a FINDING, not a blocker"), correcting it here rather than treating it as a blocker.

⭐ **Confirmed NOT the same mechanism as Parts A/B**, so do not conflate them: `SCRIP_FLOOR_DIAG=1` against both
`v02` and `v03` produces **zero** `[FLOOR-DIAG]`/`[ARM-REGION]` lines — the floor-forcing code path never fires at
all for either program (neither uses `*E`/the unevaluated-expression operator — grepped, zero hits — and neither
has an `LBL__`-prefixed or `IR_GOTO_DEFERRED`-classified proc). **Their crash is a genuinely separate, unlocated
defect** that merely happens to share the identical *symptom signature* with v05/v06 — `gdb bt` on `v02`'s crash:
```
__GI_getenv (name="SCRIP_ZETA_TELEM") at ./stdlib/getenv.c:31
#1 rt_gcheap_report () at src/runtime/rt/gc_heap.c:111
#2 __run_exit_handlers ... #3 __GI_exit ... #4 main_γ ()
```
— corruption silent until an unrelated `getenv()` call inside an atexit hook trips over it, exactly like v05/v06.
This looks like this runtime's generic "something wrote out of bounds somewhere, discovered lazily at exit" fingerprint
rather than evidence of one shared root cause — **treat v02/v03 as a NEW, third open defect on this row, not as
already covered by Parts A/B's fix.** Not investigated further this session (out of scope for the time remaining);
whoever takes Part A/B's fix should re-test v02/v03 afterward on the chance they're accidentally caught by the same
cure, but should not assume it without checking, and should budget for them being genuinely separate.

### REVISED DONE-WHEN SCOPE

The row's true remaining scope is **THREE** m4-red programs, not one: `v02`, `v03` (mechanism unknown, floor-forcing
provably not involved), and `v05`/`v06` (mechanism now fully characterized per Part A, fix direction outlined but
unproven — Part B's naive attempt is disproven). `v01`, `v04`, `c01`, `c02` remain green both modes, unaffected, and
were re-confirmed clean this session (no source changes carried) — see LEDGER for the full ladder table.

### RECEIPTS (this addendum)

SCRIP `28d73dbf` (pulled forward from `0f4231f8` this session — 4 new commits, all independently confirmed unrelated:
`0d4a5fbf`/DCAP island, `2d8d6df7`/by-name dispatch, `27f366d2`/`bb_iterate`, `57d507d9`/SIGSEGV handler
classification, plus a `snocone_lex.c` regen — none touch `emit.cpp`/`xa_flat.cpp`/`scrip.c`'s floor logic or
`zeta_storage.c`). Full `c01,c02,v01-v06` ladder re-run both modes on the final (reverted-to-baseline-behavior,
diagnostics-only) build — table in LEDGER. Baseline cross-check for Part C used `git worktree add
/tmp/scrip_baseline_check 0e57de3b` (removed after use, `git worktree list` confirmed clean). `SCRIP_FLOOR_DIAG=1`
is now a permanent, zero-cost-when-unset diagnostic (same idiom as this file's existing `SCRIP_*_DEBUG`/`_DIAG`
flags) — four `fprintf` sites in `scrip.c`, one in `emit.cpp`'s `emit_jmp_entry_for_proc` (prints
`floor`/`frame_bytes`/`seed_off`/`layout_unknown`/`jcon_value_region` together as `[ARM-REGION]`), one in
`xa_flat.cpp`'s `xa_flat_class_c` (prints the exact bail reason as `[CLASS-C]`). All gated behind
`getenv("SCRIP_FLOOR_DIAG")`; `git diff` of the behavioral condition logic itself (pre- vs post-session) is
byte-identical — confirmed before commit.

## ADDENDUM 4 [seat03, 2026-08-24, fresh session] — Parts A/B's causal claim REFUTED by hq_P; the TRUE mechanism is
Defect C (hq_P, hardware-watchpoint-measured, independently verified here by reading the source); v02/v03 are now
believed to be the SAME defect, not a separate third one — three sightings of one general class, not three bugs.

### Parts A/B RETRACTED as causal — read hq_P's finding first

`.github/FINDING-2026-08-24-hq_P-disjunction-cell-was-16-for-a-20-byte-template-and-icon-has-regressed-232-to-169.md`
(landed SCRIP `52d001c7`/`be376a2f`) **refutes this file's own Addendum 3 Part A** with a controlled experiment, not
just a disagreeing read: a one-build two-arm killswitch (`SCRIP_FLOOR_ALL`) forcing `g_flat_frame_floor` for *every*
AOT graph gave **byte-identical SIGSEGV outcome** whether the floor applied or not. The floor/carve-bailing chain
Part A traced (kind-3 `IR_DEFINE` → `g_flat_frame_floor` → `xa_flat_class_c()` bails → `EXPR$0` never carves) is
real — the instrumentation numbers were not wrong — but it is **not what causes the crash**. It was a true fact about
a box that doesn't matter, chased to a false causal conclusion. Filed here so nobody re-derives it: **do not re-open
Parts A/B's fix direction (depth-forcing/un-forcing the kind-3 floor disjunct) — it is a dead end, proven twice now**
(this file's own Part B disproved the fix by direct test; hq_P's Part-3-of-their-finding disproved the *mechanism*
by controlled test, which is the stronger refutation).

### The actual mechanism — Defect C, and I verified it by reading the code, not just trusting the finding

hq_P caught the real write on a watchpoint: a **flat-regime box with no carve of its own** (their witness:
`n169_lit_string_α`) emits a fixed offset **raw**, and that offset is only correct when `rsp` is sitting at the
frame base — which it is not when the box is reached from inside a disjunction arm (or anything else) holding an
outstanding carve. Confirmed by reading `src/templates/x86_asm.h:860-869` myself rather than taking it on faith:

```c
inline int x86_zop_regime(int off) { if (x86_zstorage() == ZC_STORAGE_FRAME_R12) return 1; if (x86_fc_hit(off)) return 2; return x86_fb_data() ? 3 : 4; }
inline const char * x86_zop(int off, int q, int bump) {
    ...
    if (r == 2) { ... snprintf(..., off - _.op_fc_base + bump); }                                    // fc regime: compensated
    else if (bump && !x86_fb_data() && !_.op_stmt_dyn) snprintf(..., x86_frame_off(off) + bump);      // "bump path": compensated
    else { snprintf(..., off + ((x86_fb_data() || _.op_stmt_dyn) ? 0 : bump)); }                      // regime 3/4 fallback: RAW, no x86_frame_off()
}
```
Regime 3/4's fallback branch fires whenever `bump==0` — the common case for a box whose template never learned it
might be invoked from inside someone else's outstanding carve, so it never passes a nonzero `bump` to begin with.
No `_.op_zdepth`/`x86_frame_off` compensation reaches this branch at all. **Worth flagging to whoever takes the
cure:** `x86_ztos`/`ZTOS`/`ZTOSD` (the very next function in the same file, `x86_asm.h:871-878`) unconditionally
computes `off + _.op_zdepth` — i.e. a *correctly zdepth-compensated* sibling primitive already exists a few lines
away from the buggy path. Not established whether it's a drop-in substitute for the affected templates' use of
`x86_zop`/`ZOP` (didn't trace every call site — that's real codegen-lane work), but it's a concrete starting point:
either the affected templates should be calling `ZTOS` instead of `ZOP` for these offsets, or `ZOP`'s regime-3/4
fallback should be doing what `x86_ztos` already does.

⭐ **This defect class was already found and cured ONCE before, precedent worth reusing:** `bb_match_defer.cpp:63`'s
own comment names this exact failure mode "Defect C" — *"both ends compute `[rsp#+op_off]` against WHATEVER rsp
happens to be AT THAT POINT, sound only if the deferred target's own body never carves stack without self-releasing
before jumping back... which the non-popping ζ-SPINE law... guarantees it does NOT."* The cure that comment
describes, for `*P DEFER`'s own case: **establish an RBP activation frame at alpha instead of an RSP-relative
watermark** — `rbp` doesn't move across a jmp-entry wire transfer (callee carves are rsp-relative, never touch
`rbp`), so addressing through `rbp` is immune by construction to however much intervening carve state exists. That
is a **working, already-shipped pattern** for solving exactly this problem for one box family; it may or may not
generalize to the flat/regime-4 boxes hq_P found (`lit_string`, and see below, also `coerce_numeric`) — that
generalization judgment is the design ruling hq_P is asking for, not something to guess at here.

### ⭐⛔ v02/v03 are now believed to be the SAME defect, not a separate third one — correcting Addendum 3 Part C

Addendum 3 Part C called v02/v03 "a genuinely separate, unlocated defect" because `SCRIP_FLOOR_DIAG` shows zero
output for either (true, still true, floor-forcing really doesn't fire for them). **But Part A/B's floor-forcing
chain is now known non-causal for v05/v06 too (see above) — so "doesn't share the floor mechanism" no longer
implies "doesn't share the crash mechanism."** Defect C's actual precondition is just "a flat/regime-4 box reached
from inside an outstanding carve" — floor-forcing was never a necessary ingredient, only an artifact of how v05/v06
happen to reach their particular flat box. Re-examined v02/v03 this session against that corrected, broader
precondition:

- **Both source programs use the same `(cond A, B)` selection idiom that lowers through `IR_DISJUNCTION`** — grepped
  the emitted `.s`: v02 has 4 `_disjunction_α` sites (`n5`,`n21`,`n31`,`n48`), v03 has 2 (`n24`,`n55`). All carve
  `sub rsp, 32` (hq_P's fix already landed and applied — confirmed the 16-vs-20-byte MISS class is cured here, it
  just isn't the thing that's crashing).
- **hq_P's landed fix does NOT cure either program** — rebuilt current HEAD (`SCRIP` past `be376a2f`) and re-ran
  both in mode 4: still SIGSEGV rc=139, unchanged. Expected, since that fix targets a different bug in the same
  file.
- **valgrind signature matches v05/v06's exactly in kind, though the discovery site differs:** v02 crashes at
  `atexit → getenv("SCRIP_ZETA_TELEM") → rt_gcheap_report`, byte-for-byte the same call chain as v05/v06's crash.
  v03 crashes *earlier*, mid-execution: `c_str_concat_d → rt_sxt_match → getenv`, reading through the same class of
  corrupted pointer before `atexit` ever runs. Both valgrind reports: `Invalid read... Address 0x2/0x3 is not
  stack'd, malloc'd or (recently) free'd` — a **tiny integer sitting where a valid pointer belongs**, the same
  "descriptor word written through a stale/wrong offset" shape hq_P found (their case: value `2` clobbering
  `environ[17]`).
- **Direct gdb memory inspection on v02, not just signature-matching:** `environ[]` at the moment of SIGSEGV shows
  **many** slots holding small integers (`1,2,3,7,9`) instead of valid string pointers, scattered through the array
  rather than one isolated slot — consistent with v02's 4 separate disjunction sites each contributing an
  independent stray write at a slightly different offset/depth, not one single-shot corruption.
- **Caught one of the writes red-handed with a hardware watchpoint** (tried hardware first per hq_P's correction —
  **it fired cleanly**, no software fallback needed; my first attempt watching a different, uncorrupted slot
  correctly produced no trap, which is not evidence hardware watchpoints don't work here, just evidence I watched
  the wrong address): the write to `environ[1]`'s slot (`0x7fffffffe1c0`, old value a valid pointer, new value `3`)
  happens in **`n38_coerce_numeric_α`** — a *different* box family from hq_P's `lit_string_α` witness. This is
  useful, not concerning: it says Defect C is not narrowly a disjunction-template or lit-string-template bug, it's
  a property of the **regime-3/4 raw-offset path itself** (`x86_zop`'s fallback branch above), so it surfaces
  through whichever flat box happens to be reached from inside an outstanding carve on a given program — disjunction
  and lit_string for hq_P's witness, coerce_numeric (and probably others, not exhaustively catalogued) for v02.

**Net correction to Addendum 3's REVISED DONE-WHEN SCOPE: the row most likely has ONE mechanism (Defect C), not
three.** Not gdb-proven for v03 specifically (only valgrind-signature-matched; v02 got the direct watchpoint catch),
and not proven that literally every affected box across v02/v03/v05/v06 is Defect C rather than some of them being
a coincidentally-identical-looking second bug — but the evidence converges hard enough (same corruption shape, same
discovery family, same `IR_DISJUNCTION`-carrying construct in source, same "landed disjunction-cell fix doesn't
touch it" result) that whoever executes HQ's design-ruled cure should **re-test v02/v03/v05/v06 together as one
batch**, not assume v02/v03 need separate, further root-causing first.

### Lane note, and where this row stands

`GOAL-CEO.md` (CEO-19, s271): **"Codegen lanes (wave 4, icon-n2) stay HQ-only per the collision evidence."** This
row's remaining `DONE-WHEN` cannot be met without a change to `emit.cpp`/`x86_asm.h`'s regime-3/4 addressing (or an
equivalent structural fix) — squarely a codegen lane. hq_P, an HQ seat, already reached the same wall this session
("the cure... wants a design ruling... I stopped at the same wall you did") — this is not a case of a worker-seat
row waiting on worker-seat effort; it is waiting on an HQ design decision that hasn't been made yet by anyone.
Sent `send hq_P vlist-v02-v03-same-defect-c-plus-match-defer-precedent` and cc'd hq_C (queue custodian, two-HQ
interlock) this session with this addendum's contents. Not calling `s4e_msg.sh done` — `DONE-WHEN` is unmet and
will stay unmet until the codegen cure lands — but there is no further seat03-lane measurement action identified
for this row right now; the honest state is "fully characterized pending an HQ ruling," not "in progress." Next
session (mine or anyone's): check inbox / HQ board for a landed cure or a design ruling before spending more time
re-deriving what's already nailed down here and in hq_P's finding.

### RECEIPTS (this addendum)

SCRIP `be376a2f` (pulled forward from `28d73dbf`; `git log -p` read directly to confirm the fc_geom/zd_k diff
before relying on it). `.github` pulled to `fa2aff43` (hq_P's finding + CEO-19/CEO-18 context). No SCRIP/corpus
source changes this session — measurement only, consistent with the lane note above. Ladder re-run in mode 4 on
current HEAD: `v02`,`v03`,`v05`,`v06` all SIGSEGV rc=139 (unchanged by hq_P's landed fix, as hq_P's own finding
already said for v05/v06 and is now confirmed here for v02/v03 too). gdb transcripts (environ address discovery,
multi-slot corruption dump, `n38_coerce_numeric_α` watchpoint catch) run against `v02_select_concat_and_assign`
built fresh from current HEAD at `/tmp/claude-1000/.../scratchpad/v02_select_concat_and_assign_bin` (scratch,
not committed — rebuild from the corpus source + current SCRIP HEAD to reproduce). Hardware watchpoints tested and
confirmed working in this container this session, corroborating hq_P's correction over this file's own Addendum
2 claim and CLAUDE.md's blanket "hardware watchpoints do NOT work in this container" — that line is now known
overbroad; software fallback is still fine when a hardware one doesn't fire, but try hardware first.

## ADDENDUM 5 [seat03, 2026-08-24, fresh session #3] — the design ruling Addendum 4's "Lane note" was waiting on HAS LANDED: CEO ruled Defect C GO, owned by hq_P, gated on the icon-232-to-169 verdict

Checked inbox (0 messages) and `.github`/SCRIP for a landed cure or ruling, per Addendum 4's own instruction and this
row's task-file NEXT. Neither shows a landed fix as of this addendum: `.github` was still at `d1347490` (this row's
own Addendum 4 commit, nothing since); SCRIP moved `be376a2f`→`ef18421e`, two new commits, both read in full and
confirmed unrelated — an Icon RTCC `r8/r9/r10/r11` bank restore-ordering fix (`bb_call.cpp`, `bb_call_fn.cpp`,
`bb_binop_arith.cpp`, `bb_binop_gvar_arith_slot.cpp`) and an `update_icon_bench_asm.sh` guard-narrowing fix — neither
touches `x86_zop`/`x86_asm.h`/`scrip.c`'s floor logic, the actual Defect C site.

But the design ruling itself HAS landed, off this row's own git-tracked trail: `ceo-defect-c-ruled-go.msg`, found in
**hq_P's** postoffice inbox (not `.github`, not a message addressed to this row — found while checking cross-seat
state to confirm nothing had landed). CEO ruled Defect C **GO**: "take it as ITS OWN ROW with its own three-frontend
board, exactly as you [hq_P] scoped: a design ruling implemented as one attributed change, never slipped beside
others. Rank 1 codegen lane, HQ-only, AFTER the icon-169 verdict lands." Not yet in `QUEUE.tsv` as a row (checked,
no `defect-c*` entry) — hq_P has the ruling but has not started; the gate is hq_C's own `icon-regression-232-to-169`
measurement, which per hq_C's reply (also read in hq_P's inbox) is close to resolved: a corpus-versioning mismatch
from seat02's semicolonize landing (`daf8918d`), not a SCRIP regression — "the moving part is CORPUS, not SCRIP."

Relayed to hq_C directly (`send hq_C vlist-defect-c-ruling-landed-gated-on-icon169`) since hq_C owns this row but the
ruling reached only hq_P's inbox — hq_C measuring their own gating row is not the same as hq_C knowing it now also
gates a ruled-GO codegen fix that this row (plus v02/v03, folded into the same mechanism per Addendum 4) is waiting on.

Net for this row: technically unchanged — still no fix landed, still nothing for a worker seat to do in the codegen
lane — but Addendum 4's open question ("waiting on an HQ design decision that hasn't been made yet by anyone") is
resolved: it HAS been made, it has a named owner (hq_P) and a named gate (the icon-169 verdict). Also consolidated
this row's task-file `## NEXT` (six superseded session blocks, ~230 lines) down to one current-state block, per the
task file's own "rewrite ## NEXT before you stop" instruction — nothing load-bearing dropped, full mechanism detail
stays in Addenda 1-4 above, ladder status and disproven-fixes carried forward verbatim.

### RECEIPTS (this addendum)

SCRIP pulled `be376a2f`→`ef18421e` (2 commits, both `git show`'d in full, confirmed unrelated to this row). corpus
pulled `d2d15c96`→`89eda383` (Icon bench `.s` artifact regen, unrelated). `.github` unchanged at `d1347490` before
this addendum. No SCRIP/corpus source changes this session. `s4e_msg.sh check` run at session start and re-checked
before wrap (0 messages both times). Cross-seat inbox files read directly (hq_P's, hq_C's) to establish the ruling
had landed and that hq_C had not yet been told — same shared-filesystem coordination surface this row's own prior
sessions have relied on throughout (BOARD.md, QUEUE.tsv, claim files), no seat-private mechanism bypassed.

## ADDENDUM 6 [seat03, 2026-08-24, fresh session #4] — v01/v03/v05/v06's m4 PASS was never stable: all four are environment-size-sensitive manifestations of Defect C, not a smaller-scope subset

Per this task row's own "Action for every future session" step 2: `git log` for touches to `x86_zop`/`x86_zop_regime`/
`x86_asm.h`, and `git log --all --grep="Defect C" -i`, at current HEAD — no landed fix (the grep hits are all
pre-existing s137-era commits, an unrelated historical reuse of the name). hq_P's `vlist-v02-v03-same-defect-c-...`
message arrived in seat03's own inbox this session (read, cleared) — its content was already known from Addendum 5/
the task file's NEXT (icon-169 exonerated, ruling GO, nothing further needed from seat03 while HQ-lane); no new
information, no reply needed.

Per step 3 ("re-confirm the ladder is unchanged... note it in LEDGER, stop cleanly"): re-ran the full ladder on a
fresh pristine-equivalent build at `4a5f88e9` and got a result that does **not** match the recorded baseline —
**v01 SIGSEGV rc=139 in m4**, where this row's own "Current ladder status" line and every prior session have it
PASS. Isolated the cause per RULES.md's measure-before-assume order before recording it as a regression:

1. **Ruled out the 6 newly-pulled commits**: built SCRIP at `ef18421e` (this row's own last-confirmed baseline) in
   an isolated `git worktree`, same corpus source, same link recipe. v01 SIGSEGV'd identically, deterministically
   (4/4 runs). Not a regression from `ef18421e..4a5f88e9` (all six commits also read in full — `strip-mechanical-
   carve`, `handoff_status.sh` third state, two exit-status-wiring fixes, banner attribution, `s4e_msg.sh unclaim`
   — none touch the floor/ZOP codegen path).
2. **Found the actual variable: process environment size.** Same binary, same everything else. Under this
   session's ambient shell environment (65 vars, 2448 bytes), v01 SIGSEGVs 8/8 runs. Under a minimal environment
   (`env -i` plus only `LD_LIBRARY_PATH`), the identical binary PASSES 2/2 runs, output byte-identical to `.ref`.
3. **Extended the env-size test to the rest of the ladder** (each binary built once at current HEAD, run under
   both environments, every PASS verified byte-for-byte against `.ref`, not just by exit code):

   | witness | m4, full env (65 vars/2448B) | m4, minimal env (`env -i`) |
   |---|---|---|
   | c01 | PASS | PASS |
   | c02 | PASS | PASS |
   | v01 | SIGSEGV rc=139 | PASS |
   | v02 | SIGSEGV rc=139 | SIGSEGV rc=139 |
   | v03 | SIGSEGV rc=139 | PASS |
   | v04 | PASS | PASS |
   | v05 | SIGSEGV rc=139 | PASS |
   | v06 | SIGSEGV rc=139 | PASS |

This reframes the split this row has carried since session #1 ("v01/v04 clean, v02/v03/v05/v06 broken"): v01 was
never actually clean — it is the same Defect C write as v02/v03/v05/v06 (§ Addendum 3/4, hq_P's finding), just
with a narrower trigger window. The raw, non-depth-compensated fixed-offset overshoot lands inside `environ`/stack
territory whose exact contents depend on `envp`'s size at process start: a small environment leaves the target
offset in harmless padding (silent, unobservable), an ordinary shell's environment does not. v02 is the one
witness whose overshoot is large/consistent enough to crash regardless of environment size — evidence of a bigger
displacement or a different flat-box instance in the same family, not a different mechanism (Addendum 4 already
placed v02 in the same class via a hardware-watchpoint catch in a different box, `n38_coerce_numeric_α`).

**Why this matters for the HQ-owned cure (flagged onward, not actioned further by seat03 — codegen lane stays
HQ-only per CEO-19):** for this defect class, a clean run is a weak signal — the crash is a false-negative
detector, not a false-positive one, since silent corruption of unused padding produces the SAME exit code as a
correct program. Recommend whoever validates the eventual fix runs the ladder under at least two environment
sizes (e.g. `env -i` minimal AND the harness's own ambient environment) before treating any witness as cured,
since stopping-the-crash-under-one-environment and stopping-the-out-of-bounds-write are not the same fact.

No SCRIP/corpus/emitter source changes this session — measurement only.

### RECEIPTS (this addendum)

SCRIP pulled `ef18421e`→`4a5f88e9` (6 commits, each read via `git show`: `4a5f88e9` strip-mechanical-carve,
`24760433` handoff_status.sh third state, `f5dd74af`/`420eaad3` corpus+icon-runner exit-status wiring,
`3723631c` banner row-attribution fix, `086e02f4` s4e_msg.sh unclaim — none touch `x86_zop`/`x86_zop_regime`/
`x86_asm.h`/`scrip.c` floor logic). corpus and `.github` pulled to latest (strip-mechanical-carve .s deletions;
Icon-232-vs-169 FINDINGs + string-manip work — both read enough to confirm unrelated). Pristine-equivalent
`make scrip`+`libscrip_rt` at `4a5f88e9`. Isolated worktree at `ef18421e` (`/tmp/scrip-wt-ef18421e`) built,
tested (v01 m4, 4 runs), and removed via `git worktree remove --force` after use. Full ladder + env-size matrix
run via an ad hoc scratch script (`/tmp/claude-1000/.../scratchpad/run_ladder.sh`, one-off, not a project script,
not committed) plus direct manual reruns (`env -i LD_LIBRARY_PATH=<out-dir> <binary>`) for the isolation step.
Inbox checked at session start (0 msgs) and after the repo pulls (1 msg, hq_P's, read and cleared, no reply
needed — see above). `git status` clean in SCRIP/corpus at time of writing; this addendum is the only change.

## ADDENDUM 7 [seat03, 2026-08-27, fresh session] — Lon's new BB FRAME-PLACEMENT CRITERION describes Defect C's own trigger and may supersede hq_C's "depth-compensate" ruling on the cure row with an RBP-activation-frame answer instead; flagged to hq_P/hq_C, not landed as of this addendum

### The law, verbatim, and why it lands on this row specifically

Lon, in-chat to CEO, 2026-08-27 (landed `.github d3fd64e1`, now `RULES.md:72`): *"the determining factor for
whether to place a BB RESULT and/or BB LOCALS [in an activation frame] is the UNBOUNDED — i.e. unknown at
compile-time — stack growth between the time a BB box leaves at GAMMA and is resumed at BETA. Or any time
UNBOUNDED growth prevents an OPERAND from being loaded by its OPERATOR with a fixed offset."* Operationalized in
RULES.md: RESULT/LOCALS stay on the ζ-SPINE (RSP) **iff every consumer reaches them at a fixed, compile-time-known
offset on every path**; the moment unbounded growth can intervene, they move to a ζ-ACTIVATION-FRAME (RBP).

That is a formal, general restatement of exactly Defect C's own precondition, already established in this file's
own Addenda 3-6: a flat-regime box (RSP-addressed via `x86_zop`'s regime-3/4 raw fallback) reached from inside a
disjunction arm holding an outstanding, unbounded carve — i.e. an OPERAND (the flat box's RESULT/LOCALS) that
cannot be loaded by its OPERATOR at a fixed offset, because the intervening growth is unbounded. The cure row
(`defect-c-zop-flat-regime-depth-compensate`, hq_P, ASSIGNED, still not landed — LEDGER unchanged since s272)
records a *different* ruled approach from hq_C: **depth-compensate every flat reference** (correct the RSP-relative
offset arithmetic dynamically), explicitly **not** force-release, but also not framed as "move to RBP." Lon's law,
read plainly, points at the RBP-activation-frame answer instead ("they move up the ladder to a ζ-ACTIVATION-FRAME
(RBP)") — a third option distinct from both of the cure row's previously-considered approaches (force-release,
disproven; depth-compensate, ruled). Per THE LOOP (CLAUDE.md § 6), Lon's word overrides a standing HQ ruling, and
the override must be routed back explicitly rather than assumed to have already propagated.

### A live worked example landed in the same session, in the same function

`SCRIP e637707d` (hq_P, same day, "N-2 item 1" — re-homing Icon **generator** ζ from the RSP spine to an RBP
activation frame) is a concrete, already-built instance of exactly this RBP re-home pattern, applied to a sibling
ζ family (`x86_zop`/`x86_zref`, the identical function Defect C lives in) via a new gate, `icn_gen_zeta_ft()`.
Verified by direct read this session that it does **not** touch Defect C's own raw-offset formula (the regime-3/4
`else` arm's `eff` computation is byte-identical to every prior session's quoted signature) and does **not** fire
for any SNOBOL4 graph (`icn_genframe2()` is `SCRIP_ICN_GENFRAME2=1`-gated via `getenv`, default OFF) — confirmed
both by code read and empirically (full ladder + corpus gate unaffected, see task-file LEDGER for this session).
This is not offered as proof the pattern transfers to Defect C's regime-3/4 case — the triggering condition differs
(disjunction/outstanding-carve vs. armed Icon generator) — only as an existing scaffold worth knowing about before
hq_P designs the cure from scratch.

### Action taken — coordination only, not a fix attempt (HQ-only, CEO-19)

Sent `send hq_P defect-c-frame-placement-law-may-change-ruled-approach` (full detail: law text, the e637707d
connection, request to confirm the ruled approach before building further) and a shorter awareness copy to hq_C
(`send hq_C defect-c-frame-placement-law-may-change-ruled-approach`, since hq_C made the ruling that may now be
superseded and owns this witness row). Re-checked the cure row directly before sending: still `ASSIGNED:hq_P`,
LEDGER unchanged since the s272 mint — the ruling has not yet been revisited in light of the new law as of this
addendum. Did not attempt to redesign or re-derive the cure myself.

### What this addendum does NOT establish

Whether RBP-activation-framing is actually the right cure for Defect C's specific regime-3/4 case, whether it is
cheaper or more invasive than depth-compensation, or how it interacts with the row's own second bug layer
(`flat_frame_bytes` sizing ignoring the floor). All of that is HQ design work, not established here — this
addendum only establishes that the *design question itself* may have reopened, and that the right people now know.

### RECEIPTS (this addendum)

SCRIP pulled `f7af8606`→`e637707d` (1 commit, read in full via `git show`, confirmed unrelated to Defect C by both
code read and empirical ladder/corpus re-run). corpus pulled `9068fdd4`→`8e85e50d` (1 commit, benchmark TSVs,
unrelated). `.github`: first `git pull --rebase` falsely reported "Already up to date" (stale — raced an origin
push in progress); caught via `git cat-file -t d3fd64e1` failing locally despite a message citing it; `git fetch`
confirmed 6 commits behind, re-pulled to `5fe6cb43`. Full ladder (c01,c02,v01-v06) re-run both modes × both
environment sizes on the `e637707d` tree, pristine rebuild, `RT_OPT=-O0` confirmed: byte-for-byte identical to
every prior session's matrix, zero drift. Corpus gate `PASS=365 FAIL=0` both modes, `MISSING=0`. `git status` clean
in all three repos — zero source edits this session (measurement, two coordination messages, this addendum, and
the task-file LEDGER entry only).
