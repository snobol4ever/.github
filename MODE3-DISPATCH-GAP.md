# MODE3-DISPATCH-GAP.md — mode-3 still runs `sm_interp_run` for 4/5 languages

**Surfaced:** 2026-05-28 (Sonnet, GOAL-RAKU-BB session)
**Status:** OPEN — directive collision plus empirical hard data, needs Lon's call

---

## Lon's directive (2026-05-28, stated 3+ times this session)

> "Ensure mode 3 is running flat-wired x86 SM's and BB's and not the interpreter
> versions which are reserved for SCRIP mode 2!"

Strict reading: mode-3 = **flat-wired x86 for SM AND BB**. `sm_interp_run` is
mode-2 only. Treated as binding.

## Empirical reality (verified 2026-05-28 with stderr probe)

Inserted one-line probe at `scrip.c:518` (the `sm_run_with_recovery(&s2->sm,
sm_interp_run)` fall-through in the `mode_run` branch). Ran `M3_TRACE_DISPATCH=1
./scrip --run test/raku/rk_class26.raku` — probe fired. Plain `--run` IS the C
interpreter for Raku today. Probe reverted before commit.

## Honest Raku corpus measurement (this session)

| Engine | Mechanism | rk_class26 | Total |
|---|---|---|---|
| `--interp` (true mode-2) | `sm_interp_run` | PASS | 23/33 |
| `--run` (called "mode-3" today) | `sm_interp_run` ← interpreter | PASS | 23/33 |
| `--run SCRIP_M3_NATIVE=1` (real mode-3) | `sm_run_native` flat-wired x86 | CRASH (segv after 2nd say) | **11/33, 20 crashes** |
| `--compile` (mode-4) | x86 binary, libscrip_rt | PASS | 26/33 |

The "Crosscheck 37/37" line in the GOAL-RAKU-BB watermark was meaningless: it
was comparing `sm_interp_run` output to `sm_interp_run` output and reporting
"modes 2 and 3 agree." Same engine, two flags.

## Per-test mode-3 (SCRIP_M3_NATIVE=1) results

```
PASS:  rk_arith rk_arrays rk_control rk_forloop rk_hash17 rk_hashes
       rk_str22 rk_strings rk_typed_vars rk_unless_until rk_vars  (11)
FAIL:  rk_junctions rk_stdio39                                    (2)
CRASH: rk_class26 rk_combinator rk_fileio38 rk_for_array
       rk_for_array_simple rk_for_array_underscore rk_gather rk_given
       rk_given18 rk_interp rk_map_grep_sort24 rk_range_for
       rk_re32 rk_re33 rk_re34 rk_re35 rk_re37 rk_regex23
       rk_subs rk_try_catch25                                     (20)
```

## What the conflicting prior directive says (2026-05-27)

`scrip.c:467-476` (CAT-D-12-S1, Opus 4.7, GOAL-PROLOG-BB):

> Per Lon directive (2026-05-27): mode-3 = "SM in-memory walk via sm_interp_run
> + BB flat-wired (bb_build_flat into bb_pool slab, sealed RX, jumped into from
> SM_BB_SWITCH)" — identical to how SNOBOL4 has worked all along.

That directive is the codebase's current operating principle. Lon's 2026-05-28
statement overrides it.

## What this session DID land

| Goal | Mode-2 | Mode-3 native | Mode-4 |
|---|---|---|---|
| rk_class26 (RECORD_REGISTER SM call + handler) | PASS ✅ | CRASH (sm_run_native engine issue) | PASS ✅ |

The fix is correct at the SM emission level (idempotent runtime call to
icn_record_register). Mode-3's crash is in `sm_run_native` itself — a different
engine, separate failure surface. The fix does not regress any path.

## What this session is NOT landing

- **No silent enforcement of strict mode-3.** Adding `abort()` at scrip.c:518
  breaks ~40 test scripts that invoke `scrip` without explicit mode flags
  (default = `--run`). Out of scope for one continue.
- **No `sm_run_native` repair.** 20 crashes across the corpus indicate the
  flat-wired SM engine has fundamental gaps for Raku (likely around method
  dispatch, gather/take, frame slots — overlapping with the open RK-BB-4 work).
  This is its own goal, not a side patch.

## Recommended path forward

Spin a goal — `GOAL-MODE3-NO-INTERP.md` (or fold into existing GOAL-RAKU-BB
as a new rung) — with structure mirroring IBB ground-zero:

1. Surface the C-interpreter fall-through with an `abort()` gated by env
   `SCRIP_M3_REQUIRE_NATIVE=1` (opt-in for tests/dev that want strict mode).
2. Switch the dispatch policy from "env opts you INTO native, else interpreter"
   to "env opts you INTO interpreter (legacy), else native (strict)." That
   inverts the bias.
3. Fix `sm_run_native` crashes one test at a time (20 to triage).
4. Update all 40+ test scripts that depend on the silent fall-through to
   either pass explicit `SCRIP_M3_LEGACY=1` or to expect the new native
   behavior.

Estimated scope: several sessions, one engine fix per failure cluster.

— Sonnet, 2026-05-28

---

## ADDENDUM — 20-crash triage (Sonnet, 2026-05-28, follow-up continue)

Crashes classified by failure mode + root-cause locus. No source edits made
during triage; gates exactly where prior continue left them.

### Cluster 1 — SM_BB_INVOKE MEDIUM_BINARY no-op stub (7 tests)

**Tests** (all SIGABRT 134, message `libscrip_rt: SM value stack underflow.`):
```
rk_fileio38 rk_for_array rk_for_array_simple rk_for_array_underscore
rk_gather rk_map_grep_sort24 rk_range_for
```

**Locus:** `src/emitter/SM_templates/sm_bb_switch.cpp:35-36`. The
`MEDIUM_BINARY` arm of `sm_bb_invoke_str` emits only
`bytes(5, "\xE8\x00\x00\x00\x00")` — a 5-byte `call rel32=0`, a no-op stub.

**Why it's a no-op:** The `MEDIUM_TEXT` arm at lines 37-87 builds an inline
four-port box: `.Lent` data byte, α/β/γ/ω labels via
`emit_label_initf`, `walk_bb_node_str_c(gen)` rendering the BB graph body as
asm, then post-amble that wires γ/ω to `rt_set_last_ok`. Every BB-internal
jump uses symbolic labels resolved by the assembler. The `MEDIUM_BINARY` arm
has no equivalent — no BB walk into the binary sink, no label arena, no
rel32 patching for BB-internal jumps. `sm_run_native`'s pass-2 patcher only
fixes `SM_JUMP/JUMP_S/JUMP_F` rel32 fields; it doesn't know about
BB-internal labels.

**Observed failure:** `SM_BB_INVOKE` is elided to 5 dead bytes, the iterator
never runs, no descriptor is pushed, and the immediately-following
`SM_JUMP_F` pops a flag that was never pushed → vstack underflow.

**Verification:** All 7 tests carry ≥1 `SM_BB_INVOKE` in their SM dump
(counts: fileio38=1, for_array=3, for_array_simple=1,
for_array_underscore=2, gather=1, map_grep_sort24=6, range_for=1).

**Fix scope:** Architectural. A MEDIUM_BINARY equivalent of the inline
four-port box, plus rel32 patching for BB-internal labels — analogous to
the existing 42 `BB_templates/*.cpp` files that already have MEDIUM_BINARY
arms (bb_alt, bb_arbno, bb_every, etc.). Single rung, likely 1-2 sessions.

### Cluster 2 — SEGV-other, root cause not yet bisected (7 tests)

**Tests** (all SIGSEGV 139):
```
rk_class26 rk_combinator rk_given rk_given18 rk_interp rk_subs rk_try_catch25
```

**Differential opcode set** (in failing tests but not in `rk_arith` which
passes native): `SM_ACOMP`, `SM_JUMP_F`, `SM_PUSH_NULL`, `SM_UNUSED_8`,
`SM_NEG`, `SM_LOAD_FRAME`, `SM_PUSH_LIT_S`, `SM_CONCAT`. Likely culprit
families: frame-slot access in unentered frames, string concat through
`SM_CONCAT` template, or arith-result coercion. Cannot bisect without gdb
(unavailable in this environment) or per-opcode TEXT/BINARY diff probe.

**Notable latent bug** (does not trigger any current crash but is real):
`src/emitter/SM_templates/sm_named_call.cpp:35` — the `MEDIUM_BINARY` arm of
`SM_NAMED_CALL` emits `movabs rax, 0; call rax` with the comment
`/* patched by linker */`, but `sm_run_native` has no linker pass for
SM_NAMED_CALL targets (only patches SM_JUMP* rel32). Any program that
emits SM_NAMED_CALL in native mode will SEGV. No test in the Raku corpus
currently exercises this opcode (verified: 0/33 dumps contain it), but
future named-sub work will trip on it.

`rk_given18` carries 1 `SM_BB_INVOKE` AND additional crash surface — fixing
Cluster 1 alone won't close it; it will reveal Cluster 2's gap behind it.

### Cluster 3 — REGEX (6 tests, DEFERRED)

```
rk_re32 rk_re33 rk_re34 rk_re35 rk_re37 rk_regex23
```

All fail with Error 5 "Undefined function" then SEGV. Per
`GOAL-RAKU-BB.md`: deferred to `GOAL-RAKU-PAT-BB`. Out of scope here.

### Summary by closability

| Cluster | Count | Closable by | Session est. |
|---|---|---|---|
| 1 SM_BB_INVOKE BINARY arm | 7 | adding MEDIUM_BINARY BB walk + BB-label rel32 patching | 1-2 |
| 2 SEGV-other | 7 (incl. given18 overlap) | per-test bisection, needs gdb or probe instrumentation | 3-5 |
| 3 REGEX | 6 | GOAL-RAKU-PAT-BB | separate goal |
| **Total** | 20 | | |

### Recommended ladder for GOAL-MODE3-NO-INTERP (Raku slice)

1. **M3-RK-NOINTERP-1** — close Cluster 1. Add `MEDIUM_BINARY` arm to
   `sm_bb_invoke_str` that drives `walk_bb_node` through an in-memory sink
   and records BB-internal label offsets, plus a parallel patch pass in
   `sm_run_native` for those offsets. Target: 11/33 → 18/33 native.
2. **M3-RK-NOINTERP-2** — Cluster 2 bisection. Probe each candidate opcode
   in isolation with a minimal `.raku` reducer per opcode.
3. **M3-RK-NOINTERP-3** — close `SM_NAMED_CALL` latent gap (linker pass for
   named-call absolute addresses).
4. **M3-RK-NOINTERP-4** — flip default per gap-doc step 2.

— Sonnet, 2026-05-28 (continue)

