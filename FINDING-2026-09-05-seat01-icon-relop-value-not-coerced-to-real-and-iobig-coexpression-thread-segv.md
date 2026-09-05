# FINDING seat01 2026-09-05 (session 7, icon-arizona-suite-49-reds-censused-by-class-and-cured)

## 1. CURED: numeric relop-as-value did not coerce the returned operand to the comparison's common type

**Symptom**: `arith.icn`'s `numtest(6.2, 4)` line — real Icon prints `4.0` three times (the `a~=b`,
`a>=b`, `a>b` columns, each of which succeeds and returns `b`); SCRIP printed plain `4`.

**Root cause**: Icon's numeric relational operators (`<`,`<=`,`>`,`>=`,`=`,`~=`) return their second
operand **coerced to the wider numeric type used for the comparison** on success — not the operand
verbatim (`SCRIP/docs`-canonical semantics, confirmed against real `icont`: `6.2 >= 4` yields `4.0`,
not integer `4`). Three independent call sites all skipped this coercion and copied the raw, un-coerced
rhs descriptor into the result on success:
- `src/templates/bb/bb_binop_relop_val.cpp`, the `_.op_zres && IR_BINOP_TEST` "zd" branch's slow/generic
  path (reached whenever either operand isn't confirmed-integer at runtime) — this is the branch Icon's
  `lower_icon.c` actually uses for `a >= b` consumed as a value (Icon's lowering only ever emits
  `IR_BINOP_TEST`; it never builds `IR_BINOP_RELOP_VAL` — that opcode is Raku/Pascal-only, see below).
- `src/templates/bb/bb_binop_relop.cpp`'s equivalent slow/generic path (the boolean/`if`-context sibling
  of the same node; its result slot is still materialized even when only used for branching, so a chained
  comparison `x < y < z` — real Icon idiom, the middle value feeds the second `<` — would have inherited
  the same bug had one arisen there).
- `src/runtime/by_name_dispatch.c`'s indirect/by-name relop dispatch (`x := ">="; x(a,b)` style calls) —
  same bug, same missing coercion; string relops (`SLT..SNE`) already called `rt_str_coerce(b)` here, only
  the **numeric** relops were left raw.

**Fix**: added `void rt_relop_val_coerce(DESCR_t a, DESCR_t b, DESCR_t *out)` (`src/runtime/arithmetic.c`,
beside `rt_relop_overload`/`rt_binop_overload`, same out-pointer calling convention — deliberately NOT a
struct-return-by-value call, to avoid any SysV 16-byte-struct classification assumption): `*out =
(IS_REAL(a) && !IS_REAL(b)) ? REALVAL(to_real(b)) : b`. Tag-only check (`IS_REAL`, not a numeric-string
parse) — **deliberately conservative**: it changes behavior ONLY when the raw DT_R tag is already present
on the left operand, so it cannot touch any currently-passing cset/numeric-string comparison (e.g.
`numtest('40','7')`, CSETs, sort BEFORE this fix as pure character sets — verified unaffected, see below).
Wired into all three sites above; the FAST integer-only sub-path in both templates (both operands
runtime-confirmed `DT_I` before reaching the copy) is untouched — it was already correct and needed no
coercion. SCRIP `<pending commit>`.

**Verification**: minimal isolated repro (`numtest(a,b)`-shaped parameter passing, matching the actual bug
site) confirmed `6.2 >= 4` now yields `4.0` in both m3 and m4, byte-identical to real `icont`. `arith.icn`'s
own diff against `.std` shrank from 6 differing lines to 3 (the `6.2`/`4` pair on both flanking lines
gone); the file does **not** reach a full PASS — its two remaining diffs are unrelated: a pure
width/padding difference on `numtest(" 5 "," 5 ")` (not investigated this session, both operands plain
integers, no coercion involved) and the `ishift()` large-magnitude columns, which are the already-scoped,
explicitly do-not-touch `icon-arizona-class-bignum-not-implemented` gap (real Icon promotes to bignum past
64-bit, SCRIP does not). **Zero pass-count movement on the Arizona board** (m3/m4 stayed 45/89 before and
after, full-suite rerun) — every file that exercises this path apparently has at least one other
independent defect too, consistent with this row's pattern on every prior session. Full Arizona suite
rerun clean otherwise (FAIL list identical, 44 names, both modes, REJECT=0 both).

⚠️ **Misattribution caught and corrected before landing**: the STRICT rung suite's `rung36_jcon_collate`
newly reads XPASS this session (in addition to the already-known `rung36_jcon_btrees` stale marker) —
initially looked like this fix's doing (collate is comparison-heavy). Control-armed (`git stash`, rebuild,
3 direct reruns, no diff either way): **collate passes identically with or without this fix** — it must
have landed from one of the 10 origin commits this session's own `git pull --rebase` picked up before this
fix was written (today's heavy 16-seat load), not from this row's work. Not claimed here. Whoever owns
`rung36_jcon_collate.xfail` should promote it (`rm corpus/tests/icon/rung36_jcon_collate.xfail`) — leaving
it named here since it surfaced during this session's own gate run, per the same "found, not this row's
cause, reported rather than hidden" convention every prior session on this row has followed. Current honest
STRICT-rung-suite reading, all three modes: `PASS=46 FAIL=8 BADEXIT=1 XFAIL=22 XPASS=2 MISSING=2 TOTAL=79`
— this row's own DONE-WHEN literal (`XFAIL=23 XPASS=1`) is stale on exactly this point, re-cut below.

⚠️ **Scope note, not chased further**: `IR_BINOP_RELOP_VAL` (a same-named-looking but semantically
different opcode — its value-producing branches write a plain `{DT_I,0|1}` boolean, never the coerced
operand) is built only by `lower_raku.c` and `lower_pascal.c`, both explicitly "in progress" frontends per
CLAUDE.md and outside every current hard gate. This fix does not touch those branches at all. Flagging only
so nobody reads the shared file and assumes the boolean-producing branches were an oversight — they are a
different node kind serving a different (still undetermined, not investigated) language semantic.

## 2. NOT CURED, real and reproducible: `iobig.icn` SIGSEGVs inside a coexpression's first libc allocation

**Symptom**: `iobig.icn` (tests text/binary I/O with huge `repl()`-generated strings via coexpression
generators) dumps core partway through, right after printing `writing file(tmp3)`, before `reading
file(tmp3)`.

**Isolated** (gdb backtrace + a from-scratch minimal repro, `local ce := create gen(); write(@ce);` where
`gen()`'s only statement is `suspend !&digits;`): crashes **iff** this is the first-ever program reference
to any of the six built-in keyword csets (`&digits`/`&lcase`/`&ucase`/`&letters`/`&ascii`/`&cset`) AND that
first reference happens from inside a coexpression's own pthread, not the main thread (same repro on the
main thread: no crash, prints normally). Backtrace: `rt_icn_cset_register` → `kw_cset_prime` (a
`static int primed` lazy one-shot global init, `src/runtime/keywords.c`) → `kw_cset_reg` → `kw_cset_grow`
→ `realloc(NULL, …)` → glibc's `tcache_init`/`arena_get2`/`_int_new_arena`/`new_heap`/`alloc_new_heap` →
SIGSEGV, `si_addr=0x0` (caught by gdb before SCRIP's own `rt_stack_overflow.c` handler runs, per gdb's
usual ptrace-first ordering — confirmed this is NOT what that handler classifies as a stack-overflow: the
fault address is nowhere near the coexpression's own `pthread_getattr_np`-reported stack range).

**Ruled out** (two control-arm programs, run standalone, no SCRIP involved): (a) a bare `pthread_create`
(8 MB stack, matching `g_coexp_stksize` in `src/runtime/rt/rt_coexpr.c`) whose child thread does one
`malloc(384)` — clean, no crash; (b) the same, but `dlopen`-ing `libscrip_rt.so` first so every one of its
`__attribute__((constructor))` inits (GC heap, stack-overflow SIGSEGV handler + altstack, alloc-history)
run before the thread spawns — still clean. So this is **not** a generic environment/glibc/sandbox issue
and **not** merely "the library's constructors poison later threads" — it depends on something SCRIP's
runtime does during actual PROGRAM EXECUTION on the main thread before the first coexpression switches in
(not yet identified precisely). Also checked and ruled out as simpler explanations: no `mallopt`/custom
`sbrk`/`MAP_FIXED` anywhere in `src/runtime/`; no malloc hooks; `ulimit -v` unlimited in this environment.

**Deliberately NOT pursued further this session**: `scrip_coswitch` (`src/runtime/rt/rt_coexpr.c`) hand-
spills callee-saved registers via inline asm (`gc_spill`) around every coexpression switch — the most
likely remaining place to look — which is coexpression-context-switch/register-plumbing territory, the
same subsystem an earlier session's FINDING (`icon-arizona-population-law-cwd-fidelity-and-fresh-census`,
§4.5) already flagged: *"do-not-attempt without first reading whatever the recent co-expression/pthread-
stack work established"*. Minting `icon-arizona-class-coexpression-thread-first-malloc-segv` (this FINDING
+ the two repro files described above are the witnesses) rather than guessing at a register-spill fix
under time pressure. Affects at minimum `iobig` (confirmed) and plausibly `gc2`/`others`/`tracer` (the
`icon-arizona-class-silent-segv-no-diagnostic` grouping from the 2026-09-04 census names these four
together on symptom alone, unconfirmed shared cause — this session confirms `iobig`'s mechanism precisely
but did NOT check whether `gc2`/`others`/`tracer` share it; their own diffs (256/151/89 lines respectively)
are far larger than a single first-malloc SIGSEGV would produce alone, so at most one of several defects
each carries could be this one).

## LEDGER (see task baton for the full cross-session history)
- Board unchanged this session: m3/m4 45/124 (89 graded) — the cure above is real and verified but did not
  flip any file's byte-exact PASS on its own, consistent with every prior sitting on this row.
- Gates before push: STRICT rung suite `PASS=46 FAIL=8 BADEXIT=1 XFAIL=22 XPASS=2 MISSING=2 TOTAL=79` (re-
  cut, see above); `strip_comments.py --check` rc=0 (383 files, 0 flagged); SNOBOL4 `make test` — see this
  session's ledger entry for the receipt.
