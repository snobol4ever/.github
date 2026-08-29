# FINDING — polyglot DEFINE entry-address bug: seat13's "shared g_emit field" theory falsified; divergence happens before `bb_call_proc_staged.cpp` is even reached

**seat07 · 2026-08-29 · row `polyglot-define-entry-address-wrong-in-merged-program` · SCRIP HEAD unchanged (tree confirmed clean, `git status --short`/`git diff --stat` both empty at handoff)**

**No fix landed. Builds on `FINDING-2026-08-29-seat13-polyglot-define-entry-address-attempt-3-crash-is-polyglot-specific-not-general.md` (read first) — this session ran seat13's own recommended next step (instrument `g_emit.lbl_t0`/neighboring fields at both compile points, single-language vs polyglot) and got a clean, decisive answer, but it is not the answer seat13's hypothesis predicted.**

## 1. The controlled experiment, done properly

Rather than recreating seat13's `recur.sno`/`recur_poly.scrip` witnesses from their description (their exact source wasn't actually embedded in their FINDING text despite a note saying it was), used `roman.scrip`'s own SNOBOL4 section verbatim, extracted as a standalone `.sno` file (`sed -n '2,17p' roman.scrip`, dropping only the fenced-block markers — byte-identical SNOBOL4 source otherwise). With attempt 3 applied (confirmed correct by seat13, re-confirmed this session):

- **Standalone**: `--run` and `--compile` (linked, executed) both print the correct output, **rc=0, both modes.**
- **`roman.scrip` (the same code, polyglot-wrapped)**: `--compile` SIGSEGVs, rc=139. (Matches seat06/seat07/seat13's prior measurements exactly.)
- **`roman_α`'s compiled body is byte-identical between the two builds**, modulo cosmetic node-numbering (`.Ldefine_α_78_*` vs `.Ldefine_α_920_*`, `n11_statement_begin_α` vs `n853_statement_begin_α` — both are "the statement-begin marker for label `roman`", just numbered differently because the standalone file is much smaller). Full `diff` in this session's transcript. **This alone rules out "the DEFINE side compiles differently under polyglot"** — it doesn't; the callee is provably identical.

## 2. Seat13's hypothesis, tested directly, falsified

Instrumented `bb_label_registry_add`/`landing` (temporary, removed) and `bb_define_sr()`'s role-4 `en4`/`_.lbl_t0` read (temporary, removed): `g_emit.lbl_t0` resolves to `roman_α` correctly and identically at the `rt_define_site` call point in **both** builds — no divergence there, and this is expected since §1 already proved the DEFINE side is byte-identical.

**The real question was always about the *call site*, not the DEFINE site — and that's where this session went instead, using the codebase's own existing (not newly written) diagnostic, `SCRIP_TINY_DIAG=1`** (`src/templates/bb/bb_call_proc_staged.cpp:512`, prints `fn`/`nargs`/`ok`/`scc`/`c2`) — no rebuild needed, it's already compiled in behind an env var:

```
polyglot:          [TINY] fn=roman nargs=1 ok=1 scc=1 c2=0     (fires 4x, once per real call site)
single-language:   (nothing — [TINY] never fires for roman at all)
```

**This is the actual divergence, and it is the OPPOSITE shape from seat13's hypothesis.** It is not that polyglot corrupts a shared field the call site reads — it's that **the single-language build's call sites never even reach the branch that contains the (buggy) signature-struct-setup logic in the first place.** Confirmed the entry condition (`(scc || bb_tiny_shim_ok(...)) && !c2`, line 509) — `bb_tiny_shim_ok("roman", 1)` returns `1` (true) identically in both builds (verified with a temporary trace, removed), so the difference is `scc`/`c2` (`_.op_c2`, another `g_emit`-adjacent per-node field) — but this observation only says WHERE the two builds' call-site *code path selection* differs, not why: **whatever mechanism selects which call-emission arm handles `roman`'s call sites is choosing differently between the two builds, and that selection happens earlier than anything inside `bb_call_proc_staged.cpp`'s own body — most likely at IR construction/op-selection time (which `IR_CALL_*` variant `roman(...)` lowers to), not at emission time.** Not traced further this session (would need a fresh, differently-aimed instrumentation pass, not this row's remaining time budget).

## 3. A concrete, unconfirmed observation worth checking first (fast to rule in/out)

`SCRIP_TINY_DIAG`'s earlier, unconditional print (`[TINYX]`, line 476, fires regardless of the `c2` gate) shows something suggestive in the polyglot build:

```
[TINYX] fn=roman/2 nargs=2 scc=0 c2=0      (x13, BEFORE any "fn=roman nargs=1" line)
[TINYX] fn=roman nargs=1 scc=1 c2=0        (x4, interleaved with [TINY])
```

`roman/2` is **Prolog's own predicate** from `roman.scrip`'s Prolog section (`roman(N, R) :- N >= 1000, ...` — properly arity-qualified, `roman/2`, distinct from SNOBOL4's 1-arg `roman`). Thirteen probes of the unrelated Prolog predicate happen immediately before SNOBOL4's four `roman` probes, in the same shared function, sharing the same `scc`/`bb_scc_probe` machinery. **This is circumstantial, not causal** — checked the one specific mechanism that looked most likely to cross-contaminate by name (`gva_index_of`, `src/optimizer/gva_collect.c:66`) and it is an exact `strcmp`, not case-folded, so a naive "SNOBOL4's `n` collides with Prolog's `N`" theory is already ruled out. But `bb_scc_probe`'s other preconditions (`x86_zc_frame()==ZC_FRAME_RSP`, `g_gva_active`, `scc_program_ok()`, `rt_proc_is_registered`) are all **global, not per-name**, state that could plausibly be perturbed by processing 13 unrelated Prolog probes first. Not verified this session — the natural next step, cheap to check (instrument `scc_program_ok()`/`g_gva_active` at each `[TINYX]` line, single-language has no such interleaving to compare against so the comparison itself needs the polyglot build's own before/after ordering, not a cross-build diff).

## 4. What's actually needed, for whoever picks this up

1. **Seat13's specific hypothesis (`g_emit.lbl_t0` or a sibling field carrying a stale/cross-language value) is falsified — do not re-instrument it.** The DEFINE side is proven byte-identical between builds (§1); the divergence is entirely on the call-site's *arm selection*, upstream of `bb_call_proc_staged.cpp`'s own body.
2. **Find where `roman`'s call sites get routed to different code (IR_CALL_PROC_STAGED vs whatever single-language actually uses, or a different arm within the same op).** Single-language's `roman(...)` calls work correctly without ever touching the `SCRIP_TINY_DIAG`-visible branches at all — find out what mechanism they DO go through, and why polyglot's identical-arity, identical-shape calls get routed differently. This is an IR-construction/op-selection question, not an emission-template question — the templates themselves (`bb_call_proc_staged.cpp`) were read in full by seat13 and again partially this session and are internally consistent; the bug is in what decides to invoke them.
3. **The `roman/2` (Prolog) timing correlation (§3) is a real lead, not yet confirmed causal.** Cheap to check first, before a deeper IR-lowering investigation: does removing Prolog's `roman/2` predicate (renaming it, or using a `recur_poly.scrip`-style witness where the OTHER languages' sections don't happen to share SNOBOL4's function name) change anything? If the crash persists with no name collision at all, §3 is a red herring and can be dropped entirely without further study.
4. **Attempt 3's own architecture is still correct and still needed eventually** (unchanged from seat13's own conclusion) — this FINDING doesn't touch that part of the picture, only the newer, second bug attempt 3 exposed.
5. Regression scope unchanged from every prior session's own notes: full `test_gate_polyglot_demos.sh` + SNOBOL4 blocking set + single-language explicit-DEFINE programs before any fix is landable.
