# HANDOFF 2026-06-14 — Icon m3/m4: builtins + subscript + globals (Sonnet)

**Goal:** GOAL-ICON-FULL-PASS — get Icon modes 3 (`--run`) and 4 (`--compile`) working.
**Result:** m3/m4 **87 → 104 (+17)**. m2 held at **202** (HARD gate) throughout. FAIL 59 → 43.
**HEAD (SCRIP) = `1fcd8c5`** (3 commits, pushed; rebased clean over concurrent BB-FIXUP / Raku landings).
Verified post-rebase: icon smoke 12/12/12 · prolog 5/5/5 · no-stack 0 · one-reg-frame 0 · FACT 0.

Every increment passed an explicit FAIL-list diff (zero EXCISE/PASS→FAIL) plus the mandatory gates before commit.

---

## What landed (3 commits)

**`ca60145` — deterministic builtins via by-name dispatch (+5).**
read/reads/iand/ior/ixor/ishift/icom/detab/entab were already implemented in
`try_call_builtin_by_name` (by_name_dispatch.c) but absent from `rt_builtin_is_known`'s
allow-list, so `bb_call` hit its FATAL instead of routing to `bb_call_byname_str` →
`rt_call_arr` → `try_call_builtin_by_name`. All are non-generators (verified vs
`builtin_is_generator`). `read` EOF returns FAILDESCR (.v=99), which the byname path's
`cmp eax,99` → ω correctly detects. Fixes rung27 read/read_eof_fail, rung37
math_hello/strfmt_hello/string_format. One-line edit to the `known[]` array.

**`f2b19cb` — native subscript `s[i]` + constant unary-minus fold (+5).**
- Added `[]` to the allow-list → byname → `subscript_get` (pattern_match.c), which already
  implements full Icon string-index semantics (negative index `s[-1]`=last, out-of-range →
  FAILDESCR). Fixes rung16 sub_basic/literal/fail. `sub_every` (`s[1 to 3]`, generator index)
  works through the existing flat generator chain.
- Root-caused `s[-1]`→'h': `-1` is lowered as `IR_UNOP(neg=TT_MNS, LIT_I(1))` and was never
  folded, so the subscript-arg marshaller read the inner positive literal; `write(-1)` alone
  was fully excised (no native int-unary-minus arm). `icn_const_step` (lower_icon.c) already
  evaluates TT_MNS/TT_PLS — extended the `lower()` unop branch to fold a constant result to
  `LIT_I(-n)`/`LIT_F(-x)` (mirrors the proven pow/real-arith folds). Non-constant `-x` returns
  0 from icn_const_step → unaffected. Fixes sub_neg + every negative-literal program.

**`8b15874` — global-VAR reads wired to the NV dictionary (+7).**
ROOT CAUSE: the emitter detected "global read" via `IR_EXEC(nd).state==1`, but **nothing sets
that at emit time** — only the mode-2 interp writes `.state` (as a per-node runtime flag) — so
the global-read NV arm (`bb_var_global`) was dead code and every cross-procedure global read
fell to `bb_var()` and bombed "unhandled arm". Meanwhile the ASSIGN side already routed globals
via `is_global(sval)` → `flat_drive_icn_global_assign` → `bb_gvar_assign_descr` → `NV_SET_fn`.
So writes went to the NV dictionary but reads were never wired — the exact asymmetry.

FIX: detect global reads the same way as the assign side — `is_global(sval)` — at three
coordinated sites: emit_core.c IR_VAR dispatch (→ `bb_var_global`), emit_bb.c IR_VAR slot setup
(which also now sets `op_sval` — it was omitted, so the arm could never have worked even if
reached), and the scrip.c native-emittable gate. No `.state` overload, so mode-2 is untouched
(HARD gate stays 202). `bb_var_global` reads `NV_GET_fn` into the node's own slot — same
dictionary the assign writes.

Also declined `IR_INITIAL` (static-once `initial n:=0`, kind 132, no native arm) in the gate so
those programs cleanly `[SMX]` EXCISE instead of aborting.

Outcome: 2 cross-proc-global programs FAIL→PASS (rung21/25 global_basic), 5 previously-EXCISED
global-read programs now PASS (the old gate declined them because it didn't recognize their
globals), 4 `initial`/static programs FAIL→clean-EXCISE. No PASS→EXCISE possible: locals
(`is_global` false) keep their existing `bb_var` routing untouched; only globals changed, and
they never passed before (the arm was dead).

---

## Lon's question answered: the `--icn-globals=` switch (SLOTS vs NV) — BOTH or NOT?

**Kept; both values parse; only NV is functional in native modes.**
- Switch: `--icn-globals=nv|slot`, default `nv` (`g_icn_globals_nv=1`, lower_icon.c:7;
  parsed scrip.c ~2048).
- **Mode-2 (interp)** ignores the switch — globals are ALWAYS NV (`scope_patch` marks declared
  globals slotless `ival=-1` → `scope_get` miss → `NV_GET`/`NV_SET`). The switch is a
  mode-3/4-only distinction.
- **Mode-3/4 `nv` (default):** now fully works (reads wired this session, writes already did).
- **Mode-3/4 `slot` (=0):** NOT implemented as working codegen — the gate `return 0`
  (clean EXCISE) for global reads in slot mode; there is no native frame-slot GLOBAL emitter.
  (Pre-session, slot-mode globals were admitted-then-bombed because the state==1 marker was
  never set, so that path never worked either.)
- Locals stay frame-slot in BOTH modes.

So we preserved the switch + both enum values per the GOAL-ICN-GLOBAL-NV design intent, but only
the NV arm produces working native globals; the `slot` arm for globals is a clean-decline stub.
To make `slot`-mode globals work natively, add a frame-slot global read/write emitter (a global
needs a stable per-PROGRAM frame slot, distinct from the per-proc local slots).

---

## Remaining m3/m4 FAIL clusters (43) — next-session intel

- **List mutation get/put/push (4) — ROOT-CAUSED, ready to fix.** Construction and non-mutating
  access work in m3 (`*L`→size, `L[1]`→subscript via this session's fix). `get(L)` segfaults
  ("Undefined function"): it takes `bb_call_fn_str` (not byname; `[]` has `op_dval==2.0`, get
  does not), and that path sets `_.op_arg_slot[0]` to a FRESH slot (e.g. r12+112) for the bare
  VAR arg `L`, but no producer box fills it — `L`'s list value is in its varslot (r12+64, where
  `IR_ASSIGN` stored the MAKELIST result). So `get` reads an uninitialized slot → arg arrives
  non-DT_DATA → `try_call_builtin` returns 0 → APPLY_fn → error → segfault. The working byname
  path doesn't set `op_arg_slot`, so its `marshal_call_arg` falls through to `bb_varslot(L)` and
  loads the correct slot. FIX: make a bare-VAR arg's `op_arg_slot` point at its varslot (or
  don't set op_arg_slot for VAR args; or route mutation builtins through byname). In SHARED
  call-marshalling infra → gate SNOBOL4/Prolog/Raku/Snocone full suites. (rung22 get/pull are
  the rc=139 segfaults; push/put are rc=134 — push/put are NOT yet in the allow-list but are
  implemented in try_call_builtin_by_name; once the slot bug is fixed they likely route too,
  but the list value must reach them as DT_DATA.)

- **Real relops (2): rung18 real_gt/mixed.** `1.5 > 2.5` bombs "shape mismatch" — LIT_F relop
  operands aren't slotted (`descr_binop_opnd_slot` returns -1 for IR_LIT_F), so it never reaches
  `bb_binop_relop`'s arms; and arm 1 does an INTEGER `cmp` on the DESCR high-word (wrong for
  reals), while `rt_jct_relop` falls to LEXICAL string compare (`"10.0"<"9.0"` → wrong). FIX:
  slot LIT_F relop operands + a numeric-aware compare (SSE `comisd`, or a DESCR-in `rt_*`
  numeric-relop helper). SHARED dispatch (SNOBOL4/Prolog) → gate carefully. This is the same
  "real-arith native path" the prior watermark flagged; the relop half is isolated here.

- **rc=124 timeouts (14): bb_every rebuild.** rung01/02/03/14/19 — generator-resume loops never
  terminate. `bb_every.cpp` is logic-empty (only `def β; jmp ω`); the EVERY drive lives in
  `flat_drive_every`. Build a real four-port `bb_every` mirroring canonical `ir_a_Every`
  (start→gen; expr.success→body; body→expr.resume = the loop; expr.failure→ir.failure). See the
  prior HANDOFF-2026-06-13-OPUS48-ICON-BB-EVERY-BOX-MISSING.md. Architectural.

- **diff / silent-wrong (14):** includes the deep `cross_arg` multi-generator ring bug
  (`write(1|2,3|4)` → 13,34,23,34) — a `is_deep` CALL ring-protocol fix, materially larger.
  Section `s[i:j]` (rung20, 3), iterate (rung15), augconcat-bang (rung11), type_mixed (rung29).
  Triage individually.

- **Globals remainder (4): rung21/25/36 `initial`/static.** Now clean-EXCISE. Need an
  `IR_INITIAL` native template (run-once guard) + static-local frame slots.

- **generators find/seq (3):** need β re-pump in the native call path (find/seq are
  `function{*}` generators; the byname single-shot path can't suspend/resume them).

- **misc:** rung02_proc_fact (`every` over recursive user-proc → depth-4096), rung32_strret
  (`every write(tag("a"|"b"|"c"))` hits removed `rt_call_proc`), rung37_proc_lookup (empty fn
  name) — all FULL-18 territory (user-proc call with generator/every interaction).

---

## Files touched (SCRIP)
`src/runtime/by_name_dispatch.c` (allow-list: builtins + `[]`),
`src/lower/lower_icon.c` (constant unary-minus fold),
`src/emitter/emit_core.c` (IR_VAR dispatch → is_global),
`src/emitter/emit_bb.c` (IR_VAR slot setup → is_global + op_sval),
`src/driver/scrip.c` (gate: is_global + IR_INITIAL decline).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
