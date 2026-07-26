# FINDING 2026-07-26b — Raku named arguments, and the mode-4 parameter-NAME replay gap

**Session:** s2026-07-26b · Claude Opus 5 · GOAL-RAKU-BB (RAKU-100 arc)
**Commit:** SCRIP `7e6848d`
**Watermark:** Raku m3 665→676, m4 665→676 (+11 smokes, zero FAIL both modes).
Peers re-verified after every change: Icon 14/14, SNOBOL4 7/7, Prolog 5/5/5, Rebus 4/4. Lang-blind gate green.

---

## PART 1 — THE RUNG: named arguments at sub call sites

### The gap was NOT where the cursor said it was

The prior cursor listed "named params `:$n` … still parse errors". Measurement first (before any edit)
refined this materially:

| shape | before this session |
|---|---|
| `sub f(:$n) { }` — the SIGNATURE | **already parsed** — `:$n` lexes to a plain `VAR_SCALAR $n` |
| `f(n => 7)` — the CALL SITE | parse error ← **the actual gap** |
| `C.new(a => 1)` | already worked (`named_arg_list` → `obj_new`) |
| `my %h = (a => 1)` | already worked (`pair_list`) |

So `named_arg_list` machinery already existed and was proven; it simply was never wired to plain sub calls.
**Lesson (repeat of the s2026-07-25b/s2026-07-23c pattern): measure the exact failing shape before
believing a one-line gap description in a cursor.** Three of the four shapes in the "named params" bucket
were already green.

### Canonical grounding (read before designing)

- `refs/rakudo-main/src/core.c/Parameter.rakumod:152` — `$flags +|= SIG_ELEM_IS_OPTIONAL unless $mandatory`
  ⟹ **named parameters are OPTIONAL by default** (unlike positionals). Name is `$name.substr(1)` (sigil stripped).
- `refs/rakudo-main/src/Perl6/bootstrap.c/BOOTSTRAP.nqp` `handle_optional` — an absent optional with no
  declared default binds **by SIGIL**: `$` → the type default (`Any`), `@` → empty Array, `%` → empty Hash.
  ⟹ absent named must yield an UNDEFINED value, never a Failure and never a bind error.

Both are honored: `sub f(:$x) { say $x.defined }; f()` → `0`.

### Implementation (no new IR opcode, no BB template, no x86 encoder)

Uniform call envelope, chosen so positional/named MIXING falls out for free:

```
__rk_named_call( QLIT procname, ILIT npos, pos1..posN, key1, val1, key2, val2, … )
```

- **Grammar** (`raku.y`): helper `rk_named_call` + two `call_expr` productions —
  `IDENT '(' named_arg_list ')'` and `IDENT '(' arg_list ',' named_arg_list ')'`.
  **ZERO conflict delta (93 s/r · 9 r/r).** The LALR discrimination is safe for the same reason the
  pre-existing `IDENT '.' KW_NEW '(' named_arg_list ')'` vs `… '(' arg_list ')'` pair is safe: one token of
  lookahead (`=>`) separates them.
- **Runtime** (`by_name_dispatch.c`): `__rk_named_call` fold resolves each key against **`rt_proc_pname()`**
  — the runtime parameter-name registry — and dispatches through the proven `invoke_method_proc` path.
  Unmatched slots stay `NULVCL` ⟹ `Any`, which is exactly `handle_optional`'s `$`-sigil arm.
  Registered in `rt_builtin_is_known` for mode-4 `@PLT`.

---

## PART 2 — ⚠ THE REAL DISCOVERY: mode-4 never replayed parameter NAMES

**This is the reusable part of the session and the reason this doc exists.**

The rung passed m3 immediately and FAILED m4 with a silent wrong answer — `say "Hello " ~ $name` printed
`Hello ` with an empty value. Not a crash, not an `[SMX]`, not a link error: **a silent miscompile-class
divergence between the two modes.**

### Root cause

`src/driver/scrip.c`'s startup emitter for the `is_icon || is_raku || is_sno_bb || is_prolog` branch replays
a proc's metadata into the standalone binary via a family of setters — `rt_proc_set_fn`,
`rt_proc_set_nparams`, `rt_proc_set_frame_bytes`, `rt_proc_set_jmpentry`, `rt_proc_set_dyn_scope`,
`rt_proc_set_result_name`, … — but **there was no setter for the parameter NAME LIST**, except along the
`dyn_scope` sub-path (which builds a rodata `.Lstartup_pnames%d` table and calls `rt_proc_register`).

⟹ For a non-`dyn_scope` proc in a standalone m4 binary, `p->pnames` is **NULL**, so `rt_proc_pname(name,k)`
returns NULL for every k. Any feature that resolves an argument BY NAME at runtime therefore binds nothing
in m4 while working perfectly in m3.

### Why it stayed invisible until now

Nothing before this rung *read* `rt_proc_pname` on the m4 path. The multi-dispatch work
(`__multi_call` / `rt_multi_meth_dispatch`) enumerates the proc registry by NAME and filters by
**arity + type**, never by parameter name; BUILD-key matching has its own dedicated
`dat_set_build_key@PLT` replay. So the hole was real but unreachable. **The generalizable warning: the m4
startup replay is a per-fact allowlist, not a snapshot of the proc record. Any NEW runtime consumer of a
`rt_proc_*` accessor must be checked against that emitter before it is trusted in mode 4 — m3 passing tells
you nothing about whether the fact was replayed.**

### Fix

New `rt_proc_set_pname(name, k, pname)` + per-param emission in the startup block.
**Scoped to `is_raku`** so peer `.s` output stays byte-identical (verified: `rt_proc_set_pname` emission
count is **0** for SNOBOL4, **>0** for Raku) ⟹ **no `.s` artifact regen owed for this session.** Scoping in
the DRIVER is legitimate under the language-sentinel FACT RULE: the driver is first dispatch, and this exact
site already branches on `is_icon` (`g_postfix_resume`).

---

## PART 3 — TWO HAZARDS HIT WHILE LANDING PART 2 (both reproduced, both fixed)

**(a) Label collision → peer BUILD BREAK, caught by the gate.** The first cut emitted
`.Lstartup_pp%d_%d`. The pre-existing `dyn_scope` path **already emits that exact label**, so a SNOBOL4 proc
with dyn scope produced a duplicate symbol: `d.s:139: Error: symbol '.Lstartup_pp0_0' is already defined`
⟹ `test_smoke_snobol4.sh` m4 went **7/0 → 6/1** (`define`, `<mode4-build-failed>`).
Fix: distinct `.Lstartup_qp` prefix **and** emit only when `!dyn_scope` (the dyn_scope path already carries
its own names). ⚠ **Before adding any label to a shared startup emitter, grep the emitter for that label
shape** — the namespace is flat and shared across four languages.

**(b) rodata write → latent crash, avoided.** The `dyn_scope` path points `p->pnames` at an **asm rodata
table**. The naive setter (`if (!p->pnames) alloc; p->pnames[k] = …`) would therefore have written into
READ-ONLY memory for any dyn_scope proc. Fix: `pnames_owned` flag on `rt_proc_t` — the setter allocates and
marks ownership, and **refuses to write an array it did not allocate**. ⚠ **Generalizes to every
`rt_proc_set_*`: some proc-record pointers are baked rodata in m4. Never write through one without an
ownership check.**

---

## PART 4 — PRE-EXISTING DEFECT FIXED AS A BONUS: `x`/`xx` could never be a key

`f(y => 9, x => 4)` was a parse error while `f(x => 4, y => 9)` and `f(q => 1, p => 2)` both worked —
an ordering-dependent failure, which is the tell for a LEXER cause, not a grammar one.

**Root cause:** `raku.l:117` `[ \t]+"x"/[^A-Za-z0-9_-] { return OP_REP_X; }` — the `x` string-repetition
infix operator OWNS any whitespace-preceded bare `x`. So `x` (and `xx`) could never be a named-argument key
or a pair key **anywhere in the language**.

**FALSIFIED AS PRE-EXISTING, cheaply and decisively** — no stash rebuild needed. The same failure reproduces
on the UNTOUCHED, pre-existing paths that share the lexer:
`my %h = (y => 9, x => 4)` and `C.new(y => 9, x => 4)` were BOTH parse errors on the same build.
⟹ not introduced by the new productions. **Technique worth reusing: to falsify an attribution, find a
pre-existing code path that shares the suspect component and test THAT, instead of paying for a full
stash-and-rebuild.**

**Fix:** one higher-priority lexer rule yielding `IDENT` when a fat arrow follows:
`[ \t]+("xx"|"x")/[ \t]*"=>"`. Trailing context does not count toward match length, so flex's
earliest-rule-wins settles it. Repetition operator unregressed — both pinned smokes (`xrep_concat_both_sides`
`1xxx2`, `xxrep_array_str` `x x x`) still green, plus 2 new regression locks. Same class as the documented
`[*]` metaop vs `@a[*]` slice collision: **an operator lexeme silently eating an identifier position.**

---

## PART 5 — DEFERRED, WITH THE COST NAMED (not faked)

**Named args to USER METHODS.** `$c.m(v => 7)` still marshals key/value as flat positional args, so
`method m(:$v)` binds `$v` to the STRING `"v"`, not `7`. The production
`atom '.' meth_name '(' named_arg_list ')'` is correct for `.new` (whose `obj_new` sink interprets pairs)
and wrong for a user method.

Why it is not a one-liner: **the call site does not know the invocant's class**, so the key→slot mapping
cannot be resolved at parse time the way the sub-call rung resolves it. The fix belongs inside `meth_call`,
AFTER `resolve_method_chain` has produced the concrete `Class__m` proc name — at which point
`rt_proc_pname` works exactly as it does for subs (and, post-Part-2, works in m4 too). Needs a marker
distinguishing named pairs from positional strings, since the current AST shape is lossy.
A smoke for this was written, observed to fail, and **REMOVED rather than left silently passing.**
`.new()` named args are unaffected.

---

## PART 6 — RECON FOR THE NEXT RUNG: slurpy `*@r` (design done, not landed)

Measured: `sub f(*@r)` is a parse error today. Two pieces already exist and should NOT be rebuilt:

1. **A variadic binding arm already exists** — `rt_frame_bind_args` (`src/runtime/rt/rt.c:585`):
   ```
   if (p->is_variadic && npc > 0) { bind fixed params; rest → rt_make_list(&g_call_args[fixed], rest); }
   ```
   fully wired end-to-end for **Icon** (`procedure p(a, b[])`): parser → `is_variadic` → stage2 →
   `rt_proc_set_variadic` in BOTH modes.
2. **`__rk_arr` already flattens** — its fold splits every argument on `SOH` while concatenating, which
   **IS canonical `from-slurpy-flat`** (`BOOTSTRAP.nqp:933`, `$slurpy_type.from-slurpy-flat($temp)`).

**The one real decision:** representation. The existing arm builds a `DT_DATA` list (`rt_make_list`);
Raku's `@a` is a **SOH-joined string** aggregate, so `.elems`/subscripts/`[+]` would not work on a
`rt_make_list` value. So the rung needs a SECOND variadic flavor. Per the shared-helper FACT RULE it must be
named by **WHAT differs, never by language** — e.g. `variadic_rest_kind`: `REST_LIST` (the existing
`rt_make_list`) vs `REST_FLAT_AGG` (SOH join, `__rk_arr` semantics) — NOT `is_raku_variadic`.

Canonical semantics to honor (`BOOTSTRAP.nqp:888-935`): collects ALL remaining positionals; when none
remain the while-loop simply does not run ⟹ **empty array, not `Any`** (and `handle_optional`'s `@`-sigil
arm agrees). Grammar needs `*@name` / `*%name` / `**@name` recognized in `param_list`; `**@` (`SLURPY_LOL`,
non-flattening) and `*%` (`SLURPY_NAMED`) can be deferred with the cost named.

---

## FILES TOUCHED (SCRIP `7e6848d`)

`src/parser/raku/raku.y` (+`rk_named_call`, +2 productions) · `src/parser/raku/raku.l` (+1 rule) ·
regen `raku.tab.c`/`.tab.h`/`.lex.c` · `src/runtime/by_name_dispatch.c` (+`__rk_named_call` fold,
+`RK_NAMED_MAX`, +known-builtin entry) · `src/runtime/rt/rt.c` (+`rt_proc_set_pname`, +`pnames_owned`) ·
`src/driver/scrip.c` (+`is_raku`-scoped pname replay) · `scripts/test_smoke_raku.sh` (+11 smokes).

**Zero emitter/template files in the diff** — which is also what proves the purity/concurrency audit
baselines are untouched by this session (`git diff --stat` is the evidence, per the standing practice).
All builds `-O0` per the O0-DEV FACT RULE.
