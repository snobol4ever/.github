# HANDOFF — Raku-BB OO RK-OO-A2: public-attribute auto-accessor (accessor half)

**Date:** 2026-06-15 · **Author:** Claude (Opus 4.8) · **Repos:** SCRIP + .github

## Session intent
Lon: "Put Raku OOP RUNGS and STEPS at the TOP of the GOAL file so it will be seen and handled FIRST. This is
the priority for Raku. Continue." Two deliverables: (1) relocate the OO ladder to the top of `GOAL-RAKU-BB.md`
and make OO the explicit lead; (2) advance the next open OO rung.

## TL;DR
- **GOAL file reorg:** the OO LADDER is now the `★ CURRENT PRIORITY` block at the very top of `GOAL-RAKU-BB.md`.
  The former NFA/grammar "CURRENT PRIORITY — READ FIRST" banner is demoted to "GRAMMAR/REGEX DIRECTION — PARKED
  BEHIND THE OO LADDER" (its content kept verbatim, just re-headed + a PARKED note). FACT-RULE bodies untouched
  (byte-identical preserved). OO ladder appears exactly once.
- **RK-OO-A2 accessor half — LANDED both native modes** (SCRIP `5370ad1`). A public attribute now answers
  `.x()` (with parens), not just `.x`. Privacy (`$!`) + `is rw` are **lexer-blocked** and deferred (reason below).

## Gates (all verified green this session, post-rebase)
- **Raku: m3 77 PASS / 0 FAIL / 7 EXCISED / 84 ; m4 77 / 0 / 7 / 84** (was 74/0/7/81 — +3 smokes, no FAILs).
- **Icon: m3/m4 12/12** (unchanged). **SNOBOL4: m4 7/7** (unchanged).
- 3 new smokes, all `[m3 PASS] [m4 PASS]`: `accessor_paren`, `accessor_method_wins`, `accessor_inherited`.
- The 7 EXCISED are unchanged (3 `~~` regex on the C matcher + 4 map/grep PUMP).

## The bug (probed live at session start)
```raku
class Point { has $.x; }
my $p = Point.new(x => 3);
say($p.x);     # 3      — worked (TT_FIELD → IR_FIELD_GET → dat_field_get)
say($p.x());   # ABORT  — [GZ-10] rt_call_proc_descr: procedure 'Point__x' has no stackless slab
```
`.x` (no parens) is a field-get; `.x()` (with parens) is a method call → `meth_call` resolved `Point__x`, found
no such proc, and fell straight to `rt_call_proc_descr("Point__x")` which aborts. Raku auto-generates a public
accessor method for every `$.`-twigil attribute, so `.x()` must return the attribute value.

## The fix (runtime-only, `src/runtime/by_name_dispatch.c`, +13 lines)
Anchored to Rakudo `src/core.c/Attribute.rakumod` → `method compose` → `if self.has_accessor { … unless
nqp::existskey($package.^method_table, $meth_name) … }`: a public attribute gets an accessor **unless a user
method of that name already exists** (user method wins).

Two edits:
1. **`meth_is_user_proc(procname)`** — new static helper after `resolve_method_chain`. Returns 1 iff the
   fully-resolved `Class__method` name is a real user proc, checking BOTH the native registry
   (`rt_proc_has_native_fn`, m4) AND `g_stage2.proc_table` (m2/m3) — the same dual lookup `resolve_method_chain`
   already does, factored out.
2. **Accessor fallback in `meth_call`** — immediately after `resolve_method_chain`:
   ```c
   if (nargs == 2 && !meth_is_user_proc(procname)) {        /* nargs==2 ⇒ receiver + method name, no extra args */
       DESCR_t *acc = data_field_ptr(mname, args[0]);        /* receiver has a field of this name? */
       if (acc) { *out = *acc; return 1; }                   /* yes ⇒ that's the auto-accessor */
   }
   ```
   `data_field_ptr` (driver_data.c) walks the instance's flattened field list (so inherited fields resolve too).
   Precedence is exactly Rakudo's: user method first (`meth_is_user_proc` short-circuits), else the field value.

No parser, lexer, template, or IR change. m2 path is irrelevant (interp deleted). Works in m3 (`--run`) and m4
(`--compile`) identically because both reach `meth_call` in the shared runtime.

### Why this is the right layer
OO is overwhelmingly runtime (the goal's architecture note). The accessor is value-work on a `DESCR_t` field —
no ports, no bytes, no graph walk. FACT-RULE clean: 0 new `test_gate_no_lang_names.sh` hits, template purity
untouched, `g_vstack`=0, `bb_bin_t`=0.

## Smokes added (`scripts/test_smoke_raku.sh`, after the inheritance block)
- `accessor_paren` — `Point.new(x=>3,y=>4); say($p.x())` → `3`.
- `accessor_method_wins` — `class Box { has $.v; method v(){ return $!v+100 } }; say($b.v())` → `105`
  (user method overrides the auto-accessor — the Rakudo `unless method_table` guard).
- `accessor_inherited` — `class Dog is Animal { … }; say($d.name())` → `Rex` (accessor resolves the inherited
  field through the chain).

## ⚠️ DEFERRED — privacy (`$!`) + `is rw` are LEXER-BLOCKED
The `$.`(public) vs `$!`(private) twigil distinction is **erased at lex time**: `raku.l:117-118` both do
`strdup(yytext+2)` → an identical `VAR_TWIGIL` bare-name token, and the class registration spec is just
`Name(f1,f2)` with no per-field privacy/rw bit. So today `$s.hidden` wrongly reads a private `$!hidden` field,
and there is no surviving signal to enforce privacy or to make an accessor writable (`is rw`).

Both halves need a public/private/rw flag carried from the declaration into the spec — which needs the **lexer**
to preserve the twigil. Per the standing LEXER CONSTRAINT, **flex 2.6.4 cannot regenerate `raku.lex.c`** (it
fails on the pristine `raku.l` at line 132). Unblock path (either):
- fix flex / use the flex version that built the committed lexer, then make `$.`/`$!` emit a twigil-tagged token; OR
- hand-patch the committed `raku.lex.c` directly to emit two distinct tokens (or one token carrying the twigil
  char), bypassing regeneration.
Then thread the flag into the `record_register` spec (a per-field marker) and gate it in `meth_call` (reject a
private accessor from outside the class) and `dat_field_get`. Until the lexer is unblocked, this is the wall.

## ⚠️ GOTCHA honored (cost prior sessions real time)
`scrip` STATICALLY links the runtime; `out/libscrip_rt.so` is mode-4 ONLY. After every runtime `.c` edit:
`rm -f scrip && make -j4 scrip && make libscrip_rt`. Also rebuilt + re-gated after the rebase onto the peer's
`f7f37db` (Prolog-only; no overlap with this Raku runtime change).

## Files touched
**SCRIP** (`5370ad1`): `src/runtime/by_name_dispatch.c` (+`meth_is_user_proc`, accessor fallback in `meth_call`),
`scripts/test_smoke_raku.sh` (+3 accessor smokes).
**.github**: `GOAL-RAKU-BB.md` (OO ladder → top as `★ CURRENT PRIORITY`; NFA/grammar banner → PARKED; RK-OO-A2
line marked `[~]` accessor-done/privacy-deferred; STATUS watermark → 77/0/7/84 @ base `952d528`) + this handoff.

## Next on the OO ladder (priority order — OO is the lead)
1. **RK-OO-A3** — `@.`/`%.` array & hash attributes (init to empty List/Hash; `.push`/`.keys`). Runtime-shaped,
   does NOT need the blocked twigil distinction → a good next move without touching the lexer.
2. **RK-OO-B1/B2** — user `method new` overrides built-in `obj_new`; `bless` + BUILDPLAN (defaults/required).
   Makes construction real; mostly runtime + the existing `meth_call`-first routing.
3. **The lexer unblock** (flex fix or hand-patch `raku.lex.c`) — unblocks RK-OO-A2's privacy + `is rw` halves
   AND RK-OO-A4 typed/default attrs AND future syntax. Cross-cutting; benefits all Raku grammar work.
4. **The m4 `x86_uid` dup-label fix** — unblocks 3+ class programs in m4 (emitter, benefits all languages).

## Build / test
```
cd SCRIP && rm -f scrip && make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_raku.sh    # 77/0/7 both modes
bash scripts/test_smoke_icon.sh    # 12/12
bash scripts/test_smoke_snobol4.sh # 7/7
```

## Commits
| Commit | Repo | What |
|---|---|---|
| `5370ad1` | SCRIP | RK-OO-A2 accessor half: public-attribute auto-accessor (both native modes) |
| (this doc + GOAL reorg/watermark) | .github | OO ladder → top; RK-OO-A2 marked; handoff |
