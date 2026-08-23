# FINDING 2026-08-23 (seat06) — row `opt0-define-beta-link`: one real defect fixed in `emit.cpp`, two more of the same class found and left open; SCRIP_OPT=0 is NOT a working escape hatch yet

## HEADLINE

seat13's repro (`SCRIP_OPT=0` → undefined `*_define_beta`/`*_goto_deferred_beta` at LINK) traces to a genuine ordering bug in `src/emitter/emit.cpp`'s γ/ω target-resolution loop, not to anything DEFINE-specific. Fixed that ordering bug (2-line diff, verified zero regression on the default/optimizer-on path). That resolves the LINK failure on `roman.sno` and gets `beauty` self-host further, but each witness then hits a SEPARATE, independent defect of the same general shape: `roman.sno` now links and runs but SIGSEGVs 100 lines into 345 (a stack double-teardown, diagnosed below); `beauty` self-host still fails to link, on a DIFFERENT symbol class (`bb_goto_deferred`, not `bb_define`) that my fix does not cover. **Neither named witness passes end-to-end under `SCRIP_OPT=0` even after this session's fix.** RULES.md's "SCRIP_OPT=0 is emergency-only; nothing may depend on it" remains true in substance — updated in place to stop implying it's merely unexercised rather than actively broken, and to point here.

## EVIDENCE 1 — the original repro, confirmed exactly as seat13 logged it

`SCRIP_OPT=0`, mode-4, `roman.sno` (`corpus/programs/snobol4/demo/roman.sno`), emit→assemble→link (the same three steps `test_broad_corpus_snobol4.sh:compile_mode4` runs):

```
SCRIP_OPT=0 SNO_LIB=.../demo/inc ./scrip --compile roman.sno > p.s
gcc -c p.s -o p.o
gcc -no-pie p.o -L./out -lscrip_rt -lm -Wl,-rpath,./out -o p.bin
```
```
/usr/bin/ld: p.o: in function `n7_match_begin_af':      undefined reference to `n120_define_β'
/usr/bin/ld: p.o: in function `n23_match_begin_af':     undefined reference to `n121_define_β'
/usr/bin/ld: p.o: in function `n122_goto_α':             undefined reference to `n120_define_β'
/usr/bin/ld: p.o: in function `n123_goto_α':             undefined reference to `n121_define_β'
```
Mode-3 (`--run`, no link step) hits the identical pair of unresolved labels via its own runtime binder and `abort()`s cleanly with a diagnostic instead of segfaulting: `site=2149 label='n121_define_β'` / `site=702 label='n120_define_β'`. Same root cause, two different failure textures — proves this is not a mode-4-only/link-specific problem.

## EVIDENCE 2 — root cause: `bb_define`'s β port is never emitted by ANY of its 6 role branches, and `emit.cpp`'s resolver prefers a dead per-node label over the one place that IS correct

Read `src/templates/bb_define.cpp` in full. `bb_define()` (:632) dispatches to `bb_define_bind()` (role 6), `bb_define_activate()` (role 7), or `bb_define_sr()` (default — roles -1/0/1/2/3/4). Grepped every one for `x86_beta`/`X86P_BETA`/`op_beta_dead`: **zero hits in `bb_define_sr()`, in any of its 6 role branches** (confirmed by reading all ~240 lines). `bb_define_activate()` defines α/γ/ω generically (`x86_deflabel(X86P_GAMMA)`/`x86_deflabel(X86P_OMEGA)` at :258-259) but likewise never β. So the generic per-node label `n<uid>_define_β` (allocated unconditionally for every node in `emit.cpp`'s `betas[i] = emit_label_alloc("n%d_%s_β", ...)`, :2803) is architecturally **never defined** by any DEFINE role — full stop, independent of `SCRIP_OPT`.

What keeps this latent 100% of the time under the default optimizer is `src/emitter/emit.cpp`'s target-resolution loop (:2858-2889), which computes where a node's γ/ω edge lands after chasing through any `IR_GOTO` chain (:2867-2868), then resolves the landing node to a label in two steps: (1) a loop over `nodes[]` for a literal object-identity match, preferring `betas[k]`/`lbls[k]`/`na_f[k]` (:2870-2880, 2887); (2) a floater check — `RETURN`/`FRETURN` are **floaters**, `IR_DEFINE` nodes with `op_ival` 1/2 whose code is emitted exactly ONCE at a shared label (`emit_floater_label`, `emit_floater_kind`, `emit.cpp:59-61`) rather than inline per node (skipped in the main loop at :2851 via `_flt_hoisted`). Pre-fix, that floater check only fired **if step (1) left `node_γ`/`node_ω` at its untouched sentinel** (`node_γ == &lbl_γ` at :2882; `!omega_resolved` at :2888) — i.e. step (1) unconditionally wins whenever it finds *any* literal match, even when the matched node is itself a floater whose `betas[k]`/`lbls[k]` is exactly the never-emitted label from the paragraph above. Under the default optimizer, `dead_pure`/`copy_prop`/`dead_goto`/`branch_chain` reliably remove or retarget these specific edges before this code runs (confirmed: neither `n120_define_β`/`n121_define_β` nor any `_define_` label with that shape appears anywhere in the optimizer-on `.s` for the same source — `grep -n "_define_" roman_opt1.s` shows only the two real per-statement DEFINE sites, `n1`/`n38`, both with real α **and** β bodies). Under `SCRIP_OPT=0` nothing removes them, step (1) wins, and the label it picks was never going to be defined by construction.

## EVIDENCE 3 — the fix, and proof of zero regression on the default path

`src/emitter/emit.cpp`, two lines, dropping the sentinel guard so the floater check always wins when the target genuinely is a floater (which is the ONLY floater-kind target for `IR_DEFINE(ival∈{1,2})`, so there is no legitimate case where the per-instance label was ever the intended one):
```diff
-        { int _flk = emit_floater_kind(gtgt); if (_flk && node_γ == &lbl_γ) node_γ = emit_floater_label(_flk); }
+        { int _flk = emit_floater_kind(gtgt); if (_flk) node_γ = emit_floater_label(_flk); }
@@
-        if (!omega_resolved) { int _flk = emit_floater_kind(otgt); if (_flk) { node_ω = emit_floater_label(_flk); omega_resolved = 1; } }
+        { int _flk = emit_floater_kind(otgt); if (_flk) { node_ω = emit_floater_label(_flk); omega_resolved = 1; } }
```
Result on `roman.sno` under `SCRIP_OPT=0`: mode-4 now links and runs (previously: link failure); mode-3 now runs past the previous abort point (previously: 0 lines before `abort()`; now: 100 correct lines before a different, independent crash — EVIDENCE 4).

Zero-regression checks, all on the DEFAULT (optimizer-on) build, same tree, `make pristine`, `RT_OPT` default `-O0`:
- `roman.sno` m3 and m4, default settings: both byte-identical to `roman.ref` (unchanged from pre-fix).
- `bash scripts/test_gate_m1_self_host_fixed_point.sh` (Milestone 1, beauty self-host): **PASS**, m3 and m4 both `40971 bytes md5 6f1671c0757729992ae01a6bdf16f081` — byte-identical to the pinned fixed point, both media.
- `bash scripts/test_broad_corpus_snobol4.sh`: `mode-3 PASS=344 FAIL=1`, `mode-4 PASS=344 FAIL=1` — the one failure both before and after is `demo_treebank`, a pre-existing named issue (referenced in `ARCH-SNOBOL4-RTX.md`, `DESIGN-SN4-ZD-VLIST-ARM-REENTRY.md`, `FINDING-2026-08-20-s182-beauty-m1-one-empty-line.md` already), unrelated to `IR_DEFINE`/floater resolution and unchanged in count by this fix.

The fix only ever changes behavior when `emit_floater_kind(target) != 0` **and** a literal node match also existed — a combination the default optimizer already prevents from surviving to this code, which is exactly why none of the above moved.

## EVIDENCE 4 — residual defect #2 (not fixed): an already-unwound landing pad redirected into a floater that unwinds AGAIN

Post-fix, `roman.sno` mode-3 under `SCRIP_OPT=0`: correct output for `TEST(1,100)`, then SIGSEGV exactly at the `TEST(149,151)` transition (`gdb`, `CSN_NO_SEGV_HANDLER=1`):
```
Program received signal SIGSEGV, Segmentation fault.
0x0000000000000003 in ?? ()
```
`rip == 0x3`, and the register dump shows `rcx == 0x3` at the fault — a `jmp rcx` landed on a small-integer value popped from the wrong stack slot, not a valid code address.

Traced to `n7_match_begin_af` (`MATCH_BEGIN`'s total-pattern-failure exit, deep inside `ROMAN`'s own body — line 2/3/4 of `roman.sno` all end statements in a pattern match). Its own emitted code, BEFORE jumping to what my fix now correctly resolves as the shared `FRETURN` floater, already does:
```
mov rsp, rbp
pop rbp
add rsp, 16          ; <- unconditionally skips BOTH the {γ,ω} save slots, no pop rcx
jmp <floater>
```
This is the same `mov rsp,rbp; pop rbp` teardown the RBP-WRITER floater itself performs (`bb_define.cpp:562-567`, role 1/2) — i.e. the af-exit path already tore the frame down once, on its own, before jumping. Landing in the shared floater (which does `mov rsp,rbp; pop rbp; add rsp,8; pop rcx; add rsp,8; jmp rcx` — a SECOND, independent teardown) pops `rcx` from 24-32 bytes further up an already-collapsed stack than the floater's contract assumes, picking up unrelated data (observed: small integers matching loop-counter-shaped values, e.g. `0x64`=100, matching how far execution had gotten). This is a genuine double-unwind, not something the 2-line fix above touches or could safely touch — `af`'s pre-existing teardown and the floater's own teardown are two independently-correct-in-isolation pieces of code that are wrong when composed, and my fix is what newly makes them compose (pre-fix, this path hit the harder abort/link failure of EVIDENCE 1 before ever reaching this). The pre-existing `add rsp, 16` (discard both slots without reading either) strongly suggests `af`'s ORIGINAL, correct-under-optimization target was never the generic floater at all, but the owning procedure's own shim exit label (`ROMAN_ω`, defined via `x86_def_ext(lbl_o)` inside the role-4 shim, `bb_define.cpp:490`/`:546`) reached directly, with no second pop needed — i.e. the true fix is teaching this resolution path which procedure a node belongs to and redirecting to ITS shim-exit label, not to the shared RETURN/FRETURN floater. That is meaningfully more machinery than this row's scope (needs per-node procedure-membership tracking that doesn't currently exist at this point in `emit.cpp`) and is NOT attempted here.

## EVIDENCE 5 — residual defect #3 (not fixed, different box, not covered by the fix at all): `bb_goto_deferred` has the identical never-emits-β property, and `emit_floater_kind` doesn't know about it

`beauty` self-host (`.github/probes/m1-bisect/beauty_classic_fixedpoint.sno`, run from `corpus/programs/snobol4/demo/beauty` per the M1 probe's own CWD requirement), mode-4, `SCRIP_OPT=0`, WITH this session's fix applied — compiles clean now (204,498 lines of `.s`, vs. 16 parse errors when run from the wrong CWD the first time), but still fails at LINK:
```
/usr/bin/ld: ... in function `n8997_match_begin_af': undefined reference to `n9008_goto_deferred_β'
/usr/bin/ld: ... in function `n15925_goto_α':          undefined reference to `n9008_goto_deferred_β'
(and 4 more matched pairs: n9101/n9193/n9272/n9603)
```
Read `src/templates/bb_goto_deferred.cpp` in full at the start of this investigation: all three of its arms (DEFINE-FOLD, TAIL-TRANSFER, and the plain fallback) emit only α and γ — **none call `x86_beta`/`x86_beta_trampoline` either**. Same defect class as EVIDENCE 2, different box. But `emit_floater_kind()` (`emit.cpp:59`) only recognizes `IR_DEFINE` with `ival` 1/2 and the `SNO$NRET`-tagged `IR_CALL`/`IR_LIT_STRING` pattern — an `IR_GOTO_DEFERRED` target is neither, so this session's fix does not reach it, and the literal-match loop's pick (`betas[k]` of a `goto_deferred` node) is undefined exactly as before. `beauty` self-host is a much larger, more GOTO-heavy program than `roman.sno` (16 DEFINE'd sections + heavy computed-`:( )` use throughout `ShiftReduce.inc`/`Gen.inc`), which is presumably why it surfaces this box and `roman.sno` doesn't.

## WHAT WOULD ACTUALLY CLOSE THIS ROW'S REPAIR ARM

Two more, independent pieces of work, neither attempted here:
1. Give the γ/ω resolver (or an earlier optimizer pass) enough procedure-membership awareness to redirect an already-self-unwound `af`/failure landing pad to the owning procedure's shim-exit label directly, instead of the generic RETURN/FRETURN floater — EVIDENCE 4.
2. Determine what an edge into `IR_GOTO_DEFERRED`'s β port is actually supposed to mean (it has no "recede" semantics either — `:(EXPRESSION)` always transfers or the whole call fails hard) and either give it the same floater-style consolidation or prove such edges should never be lowered in the first place — EVIDENCE 5.
Both need real design judgment, not a mechanical patch; scoping either properly is a new row, not a NEXT-block bullet on this one.

## CURRENT STATE / WHAT I DID

- Landed: `src/emitter/emit.cpp` 2-line fix (EVIDENCE 3), a real, independently-justified, zero-regression correctness fix — worth keeping regardless of this row's own disposition.
- NOT landed: full correctness of either named witness (`roman.sno`, `beauty` self-host) under `SCRIP_OPT=0`. Both still fail, on defects distinct from the one this session fixed and from each other.
- RULES.md's "OPTIMIZER STAYS ON... `SCRIP_OPT=0` is emergency-only; nothing may depend on it" — corrected in place (this session) to say so explicitly and point here, rather than reading as an untested-but-presumably-fine escape hatch. The underlying claim ("nothing may depend on it") was already true and stays true; what changes is that it's now backed by a receipt instead of asserted cold.

## RECEIPTS

SCRIP `2a81f82c` pristine (`make pristine`, `RT_OPT` default `-O0`) + this session's 2-line `emit.cpp` patch on top (committed separately, see LEDGER). corpus `dedb2fb2`, `.github` `0a1ea6b3`, both pulled/rebased clean at session start. Full compile→assemble→link→run pipeline reproduced by hand (not just via the test script) for both witnesses, pre-fix and post-fix, output captured at each stage. `git stash`/`stash pop` used to confirm pre-fix mode-3 behavior (abort, `site=... label='n120_define_β'`) on the identical tree, ruling out an unrelated tree-state difference. `gdb -batch -ex run -ex bt -ex "info registers"` under `CSN_NO_SEGV_HANDLER=1 SCRIP_NO_SEGV_HANDLER=1` for the EVIDENCE 4 crash. Zero-regression suite: `test_gate_m1_self_host_fixed_point.sh` (PASS, byte-identical md5 both media) + `test_broad_corpus_snobol4.sh` (344/345 both modes, unchanged fail set, pre-existing `demo_treebank` only).
