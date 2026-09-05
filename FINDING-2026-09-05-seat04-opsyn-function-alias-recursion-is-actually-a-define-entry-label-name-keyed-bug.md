# FINDING 2026-09-05 seat04 — the OPSYN function-synonym "snapshot" bug is really a `DEFINE` entry-label resolution bug, name-keyed instead of per-occurrence

**Seat:** seat04 · **Mode:** FLEET-16 (hq_C lane, "gimpel + shared-engine classes") · **Tree:** SCRIP `8e7c92217`

## 1. The row and its own diagnosis

Row `snobol4-opsyn-function-synonym-is-a-snapshot-not-a-name-alias` (minted by ceo 2026-09-05T03:52:01Z,
owner hq_C) states: *"SCRIP m3 new[] m4 ERROR 246 stack overflow (register_fn_alias copies the FNCBLK
but rt_proc_find_alias follows FUNC_ENTRY by NAME)."* — i.e. it names `register_fn_alias`/
`rt_proc_find_alias` (`src/runtime/core/core.c`, `src/runtime/rt/rt.c`) as the defect.

## 2. That diagnosis does not survive contact with the witness — tried the indicated fix, it made mode 3 worse

Wrote `rt_proc_snapshot_alias(newname, oldname)` in `rt.c`, called from `opsyn()`
(`pattern_match.c:469`) right after `register_fn_alias`: on OPSYN, copy the CURRENT `rt_proc_t` callable
fields (`fn`, `jmp_entry`, `dyn_scope`, frame layout, etc.) from `oldname`'s live entry into a fresh,
independent `g_rt_gen_procs` slot for `newname`, so a later `rt_define_site` mutation of `oldname`'s
entry (redefinition is destructive — it mutates the SAME struct in place, see `rt.c:1770-1778`) can't
reach the alias.

Built and tested against the row's own witness (below): **m4 unchanged (still ERROR 246); m3 REGRESSED**
from `new[]` (wrong, but at least didn't crash) to the same ERROR 246 stack overflow as m4. Reverted —
tree is clean, `git diff` empty, confirmed rebuilt back to the pre-fix `new[]`/`ERROR 246` baseline.

**Why it regressed m3, in hindsight:** the fix gave `_usercall_hook`'s first attempt
(`rt_call_named_proc` via `rt_proc_find("MYF.")`) a *directly-registered*, non-alias entry to succeed
against — pre-empting the fallback (`call_user_function`, AST/label-table based) that used to at least
partially save m3. But the `fn` it copied was **already wrong at the source** (see §3), so the new direct
path now recurses immediately instead of falling through to the (partially-working) fallback.

## 3. Real root cause: `DEFINE(name, label)`'s entry point is resolved by NAME, not by occurrence

Compiled the row's own witness with `--compile` and diffed the `.s`. **Both** `DEFINE` statements —
the first, implicit-entry `DEFINE('MYF(S)')` *and* the later, explicit-entry `DEFINE('MYF(S)','MYF2')`
— emit the identical target symbol for the registration call:

```
lea   r9, [rip + n11_statement_begin_α]      # <- BOTH DEFINE call sites emit exactly this
```

`n11_statement_begin_α` is confirmed (by its own source-line comment in the `.s`) to be `MYF2`'s body,
not `MYF`'s own (`MYF`'s body is `n3_statement_begin_α`). So **the very first `DEFINE('MYF(S)')` —
before any redefinition appears anywhere in the source — already registers MYF's entry as MYF2's code.**

Traced one layer: `bb_define_bind()` (`src/templates/bb/bb_define.cpp:256-296`, the "role 6" IR_DEFINE
emitter) computes the emitted symbol as:
```cpp
std::string blbl = _.lbl_t0 ? (...) : std::string("rt_ab_undef_fn_stub");
...
+ (_.lbl_t0 ? x86("lea", "r9", "[rip + __]", (uint64_t)(uintptr_t)_fn, blbl.c_str()) : ...)
```
`_fn` itself comes from `rt_define_query(fname, ...)` (`rt.c:1792-1799`), which is nothing but
`rt_proc_find(fname)->fn` — **keyed purely on the function's NAME**, with no notion of "which of the
name's several `DEFINE` occurrences is this." Since `blbl` in the actual witness resolved to
`n11_statement_begin_α` (not the direct-name-alpha form `fname + "_α"`), the true bug is one layer up
in whatever populates `g_emit.lbl_t0` for a `DEFINE` node — **not traced to that exact assignment site**
(ran out of session budget doing the .s/gdb work above; flagging the gap rather than guessing further).
Whatever it is, it evidently resolves "MYF's entry label" the same NAME-keyed, last-write-wins way
`rt_define_query` does, rather than reading the entry-label literally off *this* `DEFINE` node's own
operand (its own name, or its own explicit 2nd argument) — so every `DEFINE(SAME-NAME, ...)` sharing a
compilation unit bakes in whichever occurrence's entry label was seen **last**, corrupting every earlier
one, including the very first (non-redefining) `DEFINE`.

This is a **shared, core codegen defect** (any SNOBOL4 program with more than one `DEFINE` for the same
function name in one compile unit is exposed to it, OPSYN or no OPSYN) — squarely "shared-engine class"
territory per `RULES.md` — hence handed to hq_C rather than patched here per MASTER-PLAN's "a seat that
finds itself editing `src/` for more than one small, witnessed change hands the class to its HQ."

## 4. The row's original diagnosis may still be a real, separate, latent bug

`register_fn_alias`/`rt_proc_find_alias`'s by-name (not snapshot) resolution (§2's fix target) is a
plausible **independent** defect for the fully-dynamic case — e.g. OPSYN/DEFINE invoked through runtime
by-name dispatch inside a called procedure (not a literal top-level statement), where no compile-time
`defs[]`-style prescan can see it at all. `corpus/packages/snobol4/gimpel/REDEFINE_driver.sno` (which
drives OPSYN/DEFINE through exactly such an indirection, via its `REDEFINE(OP,DEF,LBL)` macro) currently
fails differently — `ERROR 022 -- Undefined function called`, mode 3, immediately after the macro call —
which I have **not** traced to either the §3 mechanism or the §2 one; it may be a third thing. Flagging,
not chasing further this sitting.

## 4b. Cross-reference found on push: this is the already-named `define-redefinition-ordering` class

`FINDING-2026-09-05-seat07-define-entry-point-redirect-not-honored-for-a-statically-wired-recursive-self-call.md`
(pulled into this tree after the investigation above was written) independently reaches the same
neighborhood from a completely OPSYN-free witness: `DEFINE('FOO(L)','FOO_1')` followed by a recursive
`FOO(L)` call from inside FOO's own body never reaches `FOO_1` — "in-setup-FOO" recurses forever. Their
hypothesis is call-site-side (a same-translation-unit call gets statically wired to the ORIGINAL label,
bypassing the dynamic `FUNC_ENTRY_fn` redirect entirely) rather than registration-side (this FINDING's
`rt_define_query`/`g_emit.lbl_t0` angle) — the two may be the same defect seen from opposite ends
(registration writes the wrong target XOR call sites read the right target the wrong way), or two
distinct bugs in the same area. Seat07 also names the pre-existing catalogued class this belongs to:
`corpus/tests/snobol4/ALL.csv`/`ALL.xfail` rows **`user_function_replace_4`** / **`user_function_replace_7`**
(class `define-redefinition-ordering`). Whoever picks this row up should read both FINDINGs together
before choosing a fix shape — a fix aimed only at this row's OPSYN witness risks re-deriving a narrower
patch than the class actually needs.

## 5. Repro

```
        DEFINE('MYF(S)')                                     :(E)
MYF     MYF  =  'orig(' S ')'                                :(RETURN)
MYF2    MYF  =  'new[' MYF.(S) ']'                           :(RETURN)
E       OPSYN('MYF.','MYF','')
        DEFINE('MYF(S)','MYF2')
        OPSYN('MYF','MYF','')
        OUTPUT  =  MYF('x')
END
```
- oracle (`/home/resources/x64/bin/sbl -bf`): `new[orig(x)]`
- SCRIP m3 (`--run`): `new[]`
- SCRIP m4 (`--compile`, linked, run): `scrip: runtime error: ERROR 246 -- stack overflow`

## 6. Evidence

- `.s` diff: `grep -n MYF witness.s` shows `.Ldefine_α_47_0_s "MYF"` (1st DEFINE) and
  `.Ldefine_α_84_0_s "MYF"` (2nd DEFINE) both followed by `lea r9, [rip + n11_statement_begin_α]`
  (verified via `grep -n 'lea.*n11_statement_begin_α\|DEFINE' witness.s`), where `n11_statement_begin_α`
  carries the source comment `# MYF2    MYF  =  'new[' MYF.(S) ']'`.
- `rt_define_query` at `src/runtime/rt/rt.c:1792-1799`: `rt_proc_find(name)->fn`, name-keyed, no
  per-occurrence identity.
- Attempted-and-reverted fix: see §2; tree is clean (`git diff` empty) at commit `8e7c92217`.
