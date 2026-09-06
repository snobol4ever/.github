# FINDING 2026-09-06 cto — rung 38 co-expressions: the frame snapshot rode rbp while the body read rsp, and `^` refresh was a parser no-op

Row: `icon-co-expressions-on-pthread-stacks-rung-38-create-activate-refresh-and-the-generator-abi` (CEO-326, the CTO's first problem).
Measured on incremental `make`, `RT_OPT=-O0`, at SCRIP `68ef5b5f0` / corpus `b9f408b5e` before the rebase; re-measured on the
rebased tree (see **Measured**). Every witness cut from iconx v9.5.25a (`/home/resources/icon-master/bin/icont`).

## The claim

`test_icon_ladder.sh --only 38` went from 8/14 to **14/14, both modes**. Three ladder witnesses cured, and the two coexpr crash rows in
hq_B's lane closed by the same landing. hq_B's three prior cures (a coexpr VALUE is a descriptor; the body sees GLOBALS; a finished
coexpr returns to a live activator, walk bounded) are the floor this stands on and are not re-derived here.

## What was wrong — four defects, one headline

**1. `&current`, `&main`, `&source` were three identical hardcoded strings** (`keywords.c`, three consecutive lines, all
`"co-expression_1(0)"`). Every identity test among them was trivially true, so `&source === &main` passed by accident and
`&current === &main` inside a body was wrongly true. The blocker hq_B named ("there is no coexpr VALUE to return") was already gone.

**2. THE HEADLINE: a captured local read EMPTY inside the body.** ASM-DIFF-FIRST on `refresh_caret` (`create |(i *:= 2)`):
the create-time snapshot IS taken — `edx=656` (frame_bytes), `regs[5]=rsp`, `scrip_coexpr_create` memcpys the frame into a heap
buffer `cp` — and the trampoline pointed the body at it with `rbp = cp`. But the compiled body reads the captured local at
`[rsp+608]`, the SAME slot main uses. **Two addressing planes for one datum**: delivered rbp-relative, read rsp-relative, so the
body saw its fresh pthread-stack slot, which is zero. iconx `2 4 2 4`; SCRIP `0 0 0 0`.
The four already-green rung-38 witnesses never hit this: `coroutine_switch` calls a PROCEDURE (`note()` sets its own `i`),
and `parallel_evaluation` / `activate_at` / `create` reference no enclosing local. refresh_caret is the first witness to read a
captured enclosing local.

**3. `^` refresh was a parser no-op.** `icon_parse.c` prefix `TK_CARET`: `advance(p); return parse_unary(p);` — it dropped the
caret and returned the bare operand, so `^seq1` compiled to `seq1`. The asm carried ONE `scrip_coexpr_create` for two
coexpr-producing expressions. Masked by defect 2 (everything read zero); once 2 was cured the output became `2 4 8 16` — seq3
continuing seq1's mutated state instead of restarting.

**4. `serial()` had no implementation** — a recognized name (the `proc()` arity table) with no dispatch body; every call died
ERROR 022.

## The cure

**1.** `keywords.c` returns distinct `DT_CO` descriptors `{v=DT_CO, .p=ctx}` from `scrip_co_current` (root when NULL, i.e. in
main), `scrip_co_gc_root()`, and `cur->activator` (root fallback); `values.c descr_identical` gains an explicit `DT_CO → a.p == b.p`
case beside DT_T/DT_DATA, so `===` on co-expressions is object identity, not a whole-struct memcmp. No new state.

**2.** `rt_coexpr.c`: `scrip_coexpr_entry_pkg_t` gained `frame_bytes` (offset 64, static_assert'd — a struct field, not a global).
When `frame_bytes > 0` the trampoline now does `sub rsp,fb; sub rsp,256; and rsp,-16; rdi=rbp=rsp; cld; rep movsb (cp → [rsp,rsp+fb]);
jmp body` — the body frame is CARVED ON THE CO-EXPRESSION'S OWN PTHREAD STACK, below the C trampoline's frame (which is why the
old design had parked cp on the heap: `[rsp, rsp+fb]` overlapped the trampoline's own frames), and loaded from the pristine
snapshot, so `[body_rsp+k] == cp[k] == [create_rsp+k]`. `cp` stays a pristine heap SNAPSHOT (a coexpr outlives its creating frame —
a genuine escaper), never the frame itself. The `frame_bytes == 0` fallback changed from `rbp = cp` to `rbp = rsp` so **rbp never
points at a foreign block on any path**.
⭐ **refresh=copy and resume=evolve fall out of ONE mechanism, not a flag**: the memcpy lives in `scrip_coexpr_trampoline_entry`,
the pthread start routine, entered exactly once per birth. Resume goes through `scrip_coswitch` (stack swap) and never re-enters
the trampoline, so a coexpr's evolving state persists on its own pthread stack (`i` 1→2→4 across `@seq1,@seq1`, graded against
iconx). Refresh spawns a NEW pthread → new trampoline entry → fresh copy from the pristine cp → restart.

**3.** `icon_parse.c` prefix `^x` now synthesizes `copy(x)`, mirroring the existing `=x → tab(match(x))` precedent; the `copy`
handler in `by_name_dispatch.c` gained a `DT_CO` case calling new `scrip_coexpr_refresh(ctx)`, which rebuilds the 7-register
package from the original's pkg (`csav5` = the pristine cp) and calls `scrip_coexpr_create` with `orig->frame_copy_sz` — so
create's own memcpy clones the pristine snapshot. Icon defines `copy(C)` of a co-expression as exactly this refresh, so `^` and
`copy` now share it.

**4.** `scrip_coctx_t` gained `long serial`; `scrip_coexpr_create` assigns `++g_coexpr_serial` (root/`&main` = 1, creates = 2,3,…,
matching iconx numbering; generator threads via `scrip_co_ctx_init` get 0, they are not user-visible); the upstream `BID_serial`
handler (e3bc95da6, list/table/set/record) gained the `DT_CO` case. `serial(non-serialable)` fails, so `serial(5) | "x"` takes
the alternative. **`g_coexpr_serial` is the ONE new global, on Lon's in-chat banner grant (2026-09-06)** — there was no
monotonic source to reuse: `g_scrip_coexpr_live` is decremented at destroy, and the three `g_agg_*_ser` counters are per-type
and must not be advanced by coexpr creates.

## Measured

Pre-rebase, SCRIP `68ef5b5f0`: ladder `--only 38` 8→10→12→**14/14**; Icon master (`board_icon_master.sh`) run-graded
m3 660→661→**662**/671, m4 660→661→**662**/671, CRASH=0, watermark moved up from the 607 floor at each cure (re-pin in this commit);
every rung-38 red gone from the master; residual master reds are pre-existing and not mine (rung41 `rt_*` file builtins,
`procedure_every_alt_replace_4`). Crash rows: `test_icon_rung_suite.sh --rung rung36_jcon_cxprimes` FAIL=0 in all three arms
(closed by cures 1+2); undefined-curly-call no longer SIGSEGVs — rc=1, a clean error.
Rebased onto origin/main `3377cf43e`: one witness re-reddened (`serial_on_coexpr`) because upstream `e3bc95da6` had landed a
`BID_serial` for list/table/set/record with no coexpr case and the bidjmp `goto` reaches it ahead of any by-name handler —
reconciled by merging the `DT_CO` case INTO that handler and deleting the duplicate. Re-measured after, on the final binary
(rebased + reconciled, commit `6e7bb4507`): ladder `--only 38` **14/14 both modes**; Icon master run-graded **m3 665/671,
m4 665/671, CRASH=0**, watermarks held (665 against the 607 floor — re-pinned by this landing), zero rung-38 reds, and the six
residual reds are all pre-existing and not mine (rung41 `rt_chdir_getenv`, `rt_delay`, `rt_getch_getche_kbhit_on_eof`,
`rt_loadfunc_refusal`, `rt_system_exit_stop`; `procedure_every_alt_replace_4`). The rebase itself regressed nothing: on the
rebased tree BEFORE the serial reconciliation the only rung-38 red was `serial_on_coexpr`, exactly the upstream collision.
SNOBOL4 master on this tree (`test_corpus_snobol4.sh`, same final binary): **m3 PASS=1842 FAIL=0 · m4 PASS=1842 FAIL=0
SKIP=0 · master-ast 28/28 · GATE OK**, zero user_function_* reds and zero demo_* reds — the change is Icon-only (the three
keywords are Icon's, and `DT_CO`/`serial` never occur in SNOBOL4), and the inherited demo_* set (hq_R 285f8fb12, CEO-335) was
already cured on origin by the time of the rebase, so this landing inherits nothing. Machine load during the run: 29–37 on 16
cores (other seats boarding concurrently); no rc=124 fired.

## Co-sign

hq_U co-signed the frame model **in full**: carving on the machine stack is the sanctioned destination (RULES.md § BB
FRAME-PLACEMENT CRITERION; ARCH-ENGINE.md exonerates the coexpr pthread stack — the ban is on an mmap FRAME STORE, not the
execution stack); `rbp = cp` was itself the defect (a heap block as the activation frame); rbp after restore need not equal
the create-time rbp, only resolve to the same CONTENTS; `frame_bytes` in the pkg needs no permission (a struct field is not a
global). hq_U's withheld concern — that a per-entry memcpy gives copy semantics on every activation — is resolved structurally
by WHERE the copy lives (once per birth), not by a mode flag.

## Scope rulings (Lon, in-chat, 2026-09-06)

- **Banner grant**: one new global, `g_coexpr_serial`, for the co-expression serial source. Nothing else.
- **undefined-curly-call DONE-WHEN arm scoped to NO-CRASH / clean-error, not iconx byte-match.** The row's defect was a SIGSEGV
  and it is fixed. Byte-matching would need Icon error/traceback-format parity: `Run-time error 106` (SCRIP raises 022 through the
  SNOBOL4-format printer, `core.c:2243`; its Icon printer `core_icn_error`, `core.c:2283`, has no File/Line, no offending-value
  line, and no Traceback at all) plus a co-expression IMAGE `co-expression_N(M)` in the traceback. That is a separate,
  cross-cutting row, not rung 38.

## Follow-up owed (hq_U, not a rung-38 blocker)

`^` refresh spawns a new pthread each time, so refresh-in-a-loop (`^e` inside a `repeat` is idiomatic) is O(pthreads):
(1) VA/thread exhaustion — 8 MB reserved stack per refresh, and `pthread_create` EAGAIN deep inside a refresh has no loud
refusal today; (2) GC root-set growth — every live refreshed coexpr adds a scanned stack range per collection; (3) no reaping of
a refreshed-away coexpr. The honest fix when it bites is a loud rc-refusal at exhaustion, never a silent cap (the standard RULES.md
already sets for worst-case reservation). Mint a row.

## Disposition

Landed at SCRIP **`09a1ce869`** on origin/main (rebased twice onto a moving origin — `3377cf43e`, then `3b8964cf9`; the ten
intervening commits touched no file of mine and no coexpr path, verified by `git diff --name-only`); hq_U re-grades on that hash. The row closes by its computed DONE-WHEN
(`s4e_msg.sh done`), which runs the whole criterion: ladder `--only 38` both modes, the no-crash arm, and cxprimes rung36.
