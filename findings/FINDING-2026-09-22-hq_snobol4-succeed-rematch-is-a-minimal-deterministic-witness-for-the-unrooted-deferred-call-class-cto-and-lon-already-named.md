# FINDING-2026-09-22-hq_snobol4 — `succeed-rematch` is a minimal, deterministic witness for the unrooted-deferred-call class cto/Lon already named; root cause narrowed to `pattern_match.c`'s `g_dfx` stack, one call chain still unread in a shared file

**Row:** `snobol4-the-pattern-replacement-class-…-per-poll-set` (this witness) and the row Lon named directly by cto's `f84bf131b`: `hb_nested_match_outer_subject.sno`'s "unrooted deferred-call subject … the blocked bb_match_defer site." **Same class, not yet proven identical mechanism.**

**TREE:** SCRIP `7a1361373` · corpus `aeb624c6e` · `.github` this commit · `RT_OPT=-O0`.

## The witness

`corpus/packages/snobol4/snoflake_suite/succeed-rematch.sno` (already vendored, unmodified — one of the 7 entries standing between Flake's 117/124 and 124/124):

```
        DEFINE('BUMP()')                        :(MAIN)
BUMP    N = N + 1
        BUMP = N                                :(RETURN)
MAIN    N = 0
        'ABC' SUCCEED *EQ(BUMP(), 3)            :F(NO)
        OUTPUT = 'MATCHED AFTER ' N ' TRIES'    :(END)
NO      OUTPUT = 'FAILED'
END
```

Oracle (`sbl -bf`) and SCRIP both agree the answer is `MATCHED AFTER 3 TRIES`. On tree `7a1361373`, SCRIP prints `MATCHED AFTER 1 TRIES` — **at the shipped default arena, in both mode 3 and mode 4, with zero forced relocation, zero `-INCLUDE`s, and zero stress knobs.** `SCRIP_HEAP_MB=512` alone (nothing else changed) makes it read correctly:

```
$ scrip --run succeed-rematch.sno < /dev/null
MATCHED AFTER 1 TRIES
$ SCRIP_HEAP_MB=512 scrip --run succeed-rematch.sno < /dev/null
MATCHED AFTER 3 TRIES
```

This is **strictly better as a witness** than `hb_nested_match_outer_subject.sno`: no `SCRIP_GC_RELOC=1`, no stress list, no ASLR pinning, and it reproduces identically compiled (mode 4) as interpreted (mode 3) — ruling out an interpreter-only bug.

**Isolation:** a control (`*EQ(BUMP(), 1)`, needing only one try) is correct at every arena size. The defect requires SUCCEED to actually retry at least once; a single pass never corrupts.

## GC telemetry: a real, named divergence

`SCRIP_GC_MAPS=9` on the failing run:

```
[GC-WALK-DUMP] off=-208 at=... word=0x7b8916c0e230 cls=heap-RAW type=221
[GC-WALK-DUMP] off=-56  at=... word=0x7b8916c0e230 cls=heap-cell type=221
[GC-WALK] ... s_words=36 s_cell_heap=3 s_raw_heap=1 ... divergence=2
```

Type 221 = `HB_DTP` (`gc_heap.h`), the block kind backing a deferred-call/pattern descriptor (`DTP_t`). **The same pointer value exists in two stack locations**: one properly tagged (`heap-cell`, part of a declared DESCR pair the collector updates on relocation) and one bare (`heap-RAW`, invisible to the typed walk, guaranteed stale the moment this block moves). This is exactly cto's class ("the outer subject … is one raw heap word the typed walk cannot see").

## Narrowing the mechanism — what's proven, not guessed

`gdb` breakpoints on the emitted symbols show something that overturned my first assumption: **`n52_match_defer_α` (the box's own entry) fires exactly once, and its β (backtrack) port never fires at all — in both the broken run and the correct 3-try run.** SUCCEED's retry does *not* re-enter the compiled `MATCH_DEFER` box. All three tries happen inside one call to `n52_match_defer_α`, via an internal loop (`.Lmatch_defer_α_125_2`) that chains through `rt_defer_land_γ`/`rt_defer_land_ω` repeatedly. Confirmed by breakpoint counts:

- Correct run (`SCRIP_HEAP_MB=512`): `rt_defer_land_ω` ×2, `rt_defer_land_γ` ×1, `rt_defer_close` ×3 (2/3 fail then succeed — three tries, matches the oracle).
- Broken run (default arena): `rt_defer_land_ω` ×1, `rt_defer_close` ×1, then the box exits claiming overall success off that single (failing) close — the retry loop terminates after try 1 instead of continuing.

So the defect is not "a stale pointer causes a wrong comparison" in the naive sense — it's that **the chain that's supposed to continue retrying stops early**, and whatever state that decision reads is the thing going stale.

## Strongest candidate, confined to a file I can land in

`src/runtime/pattern_match.c`'s `g_dfx` array is the GC root for this whole mechanism — `rt_cas_gc_roots()` (`pattern_match.c:1008`) scans `g_dfx[0..g_dfx_top)`, called from `gc_root_cas()` (`gc_heap.c:1223`, confirmed wired into the collector). Two places shrink `g_dfx_top` — i.e. remove an entry from the scanned range — *before* all uses of that entry's value are provably finished:

- `rt_defer_resolve`, the `DT_P` branch (`pattern_match.c:1070`): `g_dfx_top--` fires, then the (now-unrooted) pointer is handed back to the caller to be invoked.
- `c_rt_defer_close` (`pattern_match.c:1038`): pops `g_dfx[--g_dfx_top]` into a **local C stack variable**, then (`:1042`) can call `rt_defer_expr_value` → `EXPVAL_fn`, an allocating call, with the popped value now living only in an unrooted local — the exact shape the `heap-RAW` telemetry names.

I have **not** proven which of these (or something in between) is the one that fires for this witness — `rt_defer_resolve`'s `DT_X` branch (not the `DT_P` one) is what the assembly shows actually running for `EXPR$0`, and I did not get to single-step far enough to confirm whether `c_rt_defer_close`'s early pop is live on this path or whether the true retry-continuation gets minted somewhere inside `rt_call_land_ω` instead.

**And that is exactly where the trail crosses into a shared file:** `rt_defer_land_γ`/`rt_defer_land_ω` (`pattern_match.c:1095`/`1102`, SNOBOL4-exclusive, safe) call `rt_call_land_γ`/`rt_call_land_ω` — defined in **`src/runtime/rt/rt.c:1076`/`1085`**, the generic call-epilogue machinery the officers' C-to-BB conversion has been actively rewriting this same week (CEO-1134's own "third cause" ask names this exact file). I read `rt_call_land_γ/ω` far enough to see they return a plain `DESCR_t` from the generic procedure epilogue (`rt_proc_call_epilogue_named_γ`/`_ω` etc.) — nothing SUCCEED-specific — so the retry-continuation logic is almost certainly still on the SNOBOL4 side (`rt_defer_resolve`'s loop reprocessing whatever `DESCR_t` comes back), but I stopped short of being certain, and `rt.c` is a shared node per CLAUDE.md — **not something to land a change in on a hunch.**

## What this is not

- Not the IC/site-cache: `SCRIP_DEFER_IC=0` and `SCRIP_DEFER_MERGE=0` both leave the defect unchanged.
- Not the `rtx_gate_match`-gated hand-ASM fast path in `rt_defer_close` (`nm`/`objdump` on `libscrip_rt.so` show TWO distinct symbols, `rt_defer_close` at a separate address from `c_rt_defer_close`, the former a `SCRIP_RTX_MATCH`-gated inline reimplementation that falls through to the latter when off): `SCRIP_RTX_MATCH=0` leaves the defect unchanged, so the slow/C path (`c_rt_defer_close`) carries the same bug the fast path does — this is in logic both paths share, or in a caller common to both, not in the fast-path optimization itself.
- Not a mode-3-only interpreter artifact: mode 4 (`--compile`), disassembled and traced independently, shows byte-identical symptoms and the identical `n52_match_defer_α`-fires-once shape.
- Not `dupl_size_replace_branch_1`/`size_keyword_replace_branch_1` (the two long-standing SnoM reds) — unrelated file set, unmoved by any of this session's landings.

## BREAKTHROUGH — the sync-step monitor names the exact divergence, and it is not GC rooting at all

⛔ **CORRECTION TO THIS FINDING'S OWN EARLIER FRAMING.** Everything above this section is real (the arena-dependence, the `HB_DTP` raw-pointer telemetry, the `n52_match_defer_α`-fires-once shape) but the GC-rooting angle was the wrong layer. **First, monitor-safety was checked before trusting it** (CLAUDE.md: *"a monitor verdict is a verdict on a different program … legitimate only on a witness independently proven monitor-safe"*): `scrip --monitor --run succeed-rematch.sno` reproduces BOTH arms byte-identically to non-monitor SCRIP (default-arena md5 unchanged, `SCRIP_HEAP_MB=512` still reads 3 TRIES under `--monitor` too) — this witness is monitor-safe. Then `PARTICIPANTS="spl scr" bash scripts/test_monitor_3way_sync_step_auto.sh succeed-rematch.sno` (SPITBOL vs SCRIP, statement-level sync-step) gives an exact divergence, not a guess:

| step | stno | spl (oracle) | scr (SCRIP) |
| --- | --- | --- | --- |
| 8 | 3 | LABEL stno=INT=3 | LABEL stno=INT=3 |
| 9 | 3 | @3 VALUE BUMP = INT=1 | @3 VALUE BUMP = INT=1 |
| 10 | 3 | @3 RETURN BUMP (RETURN) | @3 RETURN BUMP (RETURN) |
| **11** | 3 | **@3 CALL BUMP** (invokes BUMP a second time, continuing to evaluate the deferred expression) | **LABEL stno=6** (jumps straight to the `OUTPUT = 'MATCHED …'` statement) |

Every step through BUMP's first call and return is byte-identical between the oracle and SCRIP. **The instant BUMP's first return lands, SPITBOL continues inside the deferred-expression closure (calls BUMP again, en route to evaluating `EQ(1,3)`); SCRIP instead resumes at the OUTER program's next statement — the success branch — never calling `EQ` at all.** This is a **continuation/return-address defect**, not a stale-heap-pointer read: the code that should resume "back inside the `EXPR$0` closure, about to call `EQ`" instead resumes "back in `MAIN`, past the whole match statement." The GC-rooting evidence upstream may still be a real, separate defect (the telemetry is real) — but it is not what this witness's wrong answer is caused by, and the arena-size sensitivity is a symptom of the continuation address itself being computed from something GC-relocation perturbs, not of a value going stale after a correct continuation.

⛔ **AND THIS NOW POINTS AT A SHARED FILE, NOT A SNOBOL4-EXCLUSIVE ONE.** A wrong-continuation-after-a-named-procedure-return is exactly the shape of `ceo`'s own open "third cause" ask (CEO-1134/1137, topic `snobol4-c2bb-regression-58-code-eval-indirect-entries-broken-since-your-14-commit-landing`): the C-to-BB call-landing machinery in `rt.c` (`rt_call_land_γ`/`rt_call_land_ω`, `rt_call_open_by_name`, `rt_c2bb_word`) is under active rewrite by the officers this same week, and it is a SHARED node (all seven languages' named-procedure calls route through it). I have not proven the defect is IN `rt.c` rather than in SNOBOL4's own consumption of its return value, but the shape (right through the call, wrong immediately after the return) matches that family exactly, and `code_eval_1` — ceo's own witness for the still-open regression — is architecturally the same class (`CODE()` value + a goto/call landing back in the wrong place). **Routing this to `ceo` rather than continuing to trace it unilaterally, since a wrong guess in `rt.c` is reverted on sight and it may already be the same defect ceo is bisecting.**

## Classification per RULES.md THE INSTRUMENT LAWS, thirty-third batch, clause 1 (CEO-1158)

Zero-collection arm, knob is STRESS/arena per the mandated recipe, run's own report read directly (`SCRIP_GC_EXERCISE=1`, never assumed):

```
env -u SCRIP_HEAP_KB SCRIP_HEAP_MB=512 SCRIP_GC_EXERCISE=1 scrip --run succeed-rematch.sno < /dev/null
  MATCHED AFTER 3 TRIES   [GC-EXERCISE] ... collections=0 ...
env -u SCRIP_HEAP_MB SCRIP_GC_EXERCISE=1 scrip --run succeed-rematch.sno < /dev/null
  MATCHED AFTER 1 TRIES   [GC-EXERCISE] ... collections=1 ...
```

Right at collections=0: correct. Wrong the instant one collection runs. Per clause 1: **this is the COLLECTOR (a continuation held in a block that moved), not emission.** Confirms the sync-step reading independently.

`atn` (Budne's other standing red, mode-4-only) carries the identical signature: `collections=0` at 512 MB and content-correct (module trailing-newline harness noise only); wrong (missing `------ Code ------` blocks) at the shipped default arena. Strong circumstantial evidence it is the same class, not yet proven the same mechanism.

## Structural candidate, named but NOT landed — do not act on this without independent verification

`bb_glue_enter_c2bb` (`src/templates/bb/bb_glue_flat.cpp:97`, used by `bb_match_defer.cpp`, `bb_match_capture.cpp` ×2, `bb_match_end.cpp` — all SNOBOL4 pattern-match boxes) saves `r13`/`r15d` as a tagged `DT_S` pair and `r14`/`rdx` as tagged `DT_I` pairs across the deferred call — both correctly covered by the general spine-cell walk (§ 3d Rule 1a, no explicit poll needed for a properly tagged 16-byte cell). **But it saves `rbx` (rsp+48) and `r12` (rsp+56) as bare 8-byte words with no preceding tag at all.** If either register holds a live heap pointer at a call site using this glue, that pointer is invisible to the typed walk by construction — exactly the `heap-RAW` shape the telemetry names. The identical untagged-`rbx`/`r12`-across-a-call shape is *also* duplicated inline inside `bb_match_defer.cpp`'s own DT_E/DT_X dispatch branches (e.g. around the `sub rsp,64` blocks at its `.125_0`/`.125_2` labels) — so there are at least two candidate sites, not one, and I have not proven which (if either, or both) actually holds the stale pointer in this witness — only that the shape matches.

**Why this is not landed:** confirming which register and which site requires catching the value live during the actual mid-program collection (not the exit-time `SCRIP_GC_MAPS` diagnostic dump, which is a post-mortem snapshot taken after the program has already finished and already printed its wrong answer — a watchpoint set from that dump's own breakpoint fires too late, confirmed by trying it). Changing this shared buffer's layout (adding tag words changes its size, which cascades through `land_γ`/`land_ω`'s offset arithmetic in the same function) is not a one-line change, and RULES.md's own standing warning applies directly: a wrong guess in a shared node is reverted on sight, and the thirty-third batch's clause 4 says re-draw a one-side-only name before accepting or rejecting on it. I have one side (static structural suspicion), not two (a caught live write/read).

## A tested-and-disproven hypothesis, tried and reverted, not landed

`dtp_fn_of` (`pattern_match.c:108`) held a raw `DTP_t*` across two allocating calls (`dtp_rcp_tree`, then `bb_compile_pat_tree_sz`) with no rooting — a real, separate theoretical unsafety, structurally matching the class. I rooted it through a `g_dfx` slot (the same mechanism `rt_defer_resolve` already uses), rebuilt, and tested directly against the witness. **It did not change the outcome — still `MATCHED AFTER 1 TRIES` at the default arena.** Caught with `gdb` (`break dtp_fn_of`): the branch does execute (`fn=(nil)` on entry), and it completes *without* triggering a collection — `gc_collect_ex` is called later, from a completely different site. Reverted (`git checkout -- src/runtime/pattern_match.c`) rather than leave an unverified change claiming a fix it doesn't deliver.

**Where the collection actually happens, caught live with `break gc_collect_ex` + backtrace:** immediately after `rt_defer_open_entry`'s call returns, at the `rt_gc_point_arr_c` poll that follows it (`bb_match_defer.cpp`'s emission around its `x86_rt_gc_poll_rec_sigma_pair(1, 51)` call, matching `.s` lines ~1349-1360 in the compiled witness). Disassembled the actual call site (`x/24i`): the poll's save/restore of the sigma pair (`r13`/`r15d`) and the `rax`/`rdx` pair is structurally correct and matches the audited pattern used ~111 times elsewhere (`r9`'s apparent non-save is the already-adjudicated `RT_GVA_VA` constant pin, not a bug — CEO/coo settled that earlier). Nothing in this specific poll looks wrong on inspection, which is exactly why I didn't guess further: sync-step proves the wrong behavior manifests much later (after BUMP's return, deep inside the invoked closure), so either this poll's protection is subtly incomplete in a way static reading doesn't show, or the corruption is unrelated to this poll and something later reads a value that was never live-registered anywhere.

## Next steps, named rather than guessed at

1. Single-step (not disassembly-reconstruct) through one failing collection with `gdb` watchpoints on `g_dfx_top` and on the specific stack slot GC_MAPS names, across the second `rt_defer_land_ω` call that *should* happen but doesn't, to catch the exact instruction that decides "stop retrying."
2. If the decision point is confirmed inside `pattern_match.c` (the `DT_X`/`DT_P` resolve loop or `c_rt_defer_close`), it is SNOBOL4-exclusive (`IR_MATCH_DEFER` — `grep -c IR_MATCH_DEFER src/lower/lower_*.c` = 10, all in `lower_snobol4.c`, zero elsewhere) and safe to land without an ASK.
3. If it lands in `rt_call_land_γ`/`rt_call_land_ω` (`rt.c`) or anything else the C-to-BB conversion touched, this is CEO-1134's "third cause" by another name and goes to `ceo`/`cto`, not landed here.

## Suites this blocks, named per Lon's 2026-09-22 directive (all-suites-to-100%)

- Flake (`snoflake_suite`): `succeed-rematch` is 1 of the 7 entries between 117/124 and 124/124 — the only one of the 7 that's a regression-recovery case rather than a pre-existing gap.
- Plausibly related by shared feature (deferred/indirect `*`/`$` constructs), **not yet confirmed the same mechanism**: `fullscan-palindrome`, `pattern-assignment-targets`, `indirect-integer-and-keyword` (also standing Flake reds).
- `atn` (Budne, mode-4-only divergence, `------ Code ------` blocks silently dropped) — not yet checked against this mechanism; worth a pass once this lands.
