# HANDOFF — Raku-BB OO RK-OO-B1: user `method new` + `bless` + type-object dispatch

**Date:** 2026-06-15 · **Author:** Claude (Opus 4.8) · **Repos:** SCRIP (`41a9393`) + .github

## TL;DR
A user-defined `method new` now overrides the built-in `obj_new`, the `self.bless(k => v)` construction idiom
works, and class-name (type-object) method calls dispatch — all in both native modes. Also trimmed
`GOAL-RAKU-BB.md` (654→566 lines) and marked RK-OO-A3 lexer-blocked.

```raku
class Temperature { has $.celsius; method new($c) { return self.bless(celsius => $c); } }
my $t = Temperature.new(37);   # → 37  ✓ (m3 + m4)
```

## Gates (green this session, post-rebase)
- **Raku m3/m4 80 PASS / 0 FAIL / 7 EXCISED / 87** (was 77/0/7/84 — +3 smokes).
- **Icon 12/12, SNOBOL4 7/7** unchanged. `g_vstack`=0, `bb_bin_t`=0, IR_NFA=0.
- `test_gate_no_lang_names.sh` at baseline (40 grouped, all Prolog/Pascal-owned; my code 0). The 5
  `audit_concurrency_invariants.sh` VIOLATIONs + 1 purity site are pre-existing/unchanged. FACT-RULE blocks
  in GOAL-RAKU-BB stayed byte-identical through the trim (audit confirms none name the Raku file).
- New smokes (both modes PASS): `method_new_override`, `bless_named`, `type_object_method`.

## What landed (SCRIP `41a9393`)
**Parser (`raku.y`, bison-regen only — NO lexer change):**
- `method new(...)` + no-arg form: `KW_METHOD KW_NEW '(' param_list ')' block` → `TT_SUB_DECL` named `"new"`
  (`new` is the `KW_NEW` token, so it can't arrive as `IDENT`; accept it positionally instead).
- `self.bless(k => v)`: `atom '.' IDENT '(' named_arg_list ')'` → `TT_METHCALL` with receiver + key/val pairs
  (same layout `obj_new` consumes).
- `T.new(positional)`: `IDENT '.' KW_NEW '(' arg_list ')'`.
- Conflicts 30→31: one benign `arg_list`/`named_arg_list` 1-token-lookahead shift/reduce, resolves correctly.

**Lower (`lower_raku.c`):** class-name barewords now lower to `IR_LIT_S` (mirroring the existing grammar-name
special-case at the two `TT_VAR` sites) so a class receiver like `T` in `T.mk()` is not a free `IR_VAR` that
trips the m3/m4 free-var EXCISE gate. New `g_rk_class_names` registry + `rk_is_class_name`, populated in
`rk_register_classes` (runs before per-proc lowering).

**Runtime (`by_name_dispatch.c`):**
- `bless` arm in `meth_call`: receiver string = class name, rest are key/val pairs → `dat_construct` (clone of
  the `obj_new` named-arg construction).
- `obj_new` routes `.new` to a user `<C>__new` (via `resolve_method_chain` + `meth_is_user_proc`) if one exists,
  else built-in construction. Regression-clean: classes without a user `new` still construct normally (3/7).
- Type-object dispatch: when a `meth_call` receiver is a class-name string (not a `DT_DATA` instance) naming a
  registered class with a user `<C>__<m>`, route to that method with the class name as `self` (before the old
  DT_DATA guard that would have returned FAILDESCR). This is what makes `T.mk()` / `Temperature.new(37)` reach
  the user method body.

## GOAL file trim (this session's housekeeping ask)
`GOAL-RAKU-BB.md` 654→566 lines: deleted APPENDIX A (historical, "numbers not reachable"); collapsed the verbose
Watermark history (RENAME-PURGE detail, STAGE-4a/NFA superseded blocks, old session-9/10 + grammar STATE blocks)
into terse one-paragraph-per-milestone entries; kept the durable KEY GOTCHA and the done-history line.
**FACT-RULE bodies untouched** (byte-identical — required by `audit_concurrency_invariants.sh`; verified the
Raku file is named in zero violations before and after).

## Deferred / blocked (none introduced)
- **RK-OO-A3 (`@.`/`%.` attrs) — LEXER-BLOCKED.** Probed: no `@.`/`%.` lexer rules; `has @.items` fails at lex.
  Needs `raku.lex.c` regen (flex 2.6.4 can't). Marked `[!]` in the ladder.
- **RK-OO-A2 privacy (`$!`) + `is rw` — LEXER-BLOCKED** (twigil erased at lex). The accessor half landed (`5370ad1`).
- **BUILDPLAN** (RK-OO-B2): basic `bless` from named args landed here; the op-list (defaults op 400, required op
  800) is the remaining B2 work.

## Next on the OO ladder (priority order — OO is the lead)
1. **RK-OO-B2 BUILDPLAN** — default attr closures (`has $.x = 42`) + required attrs (`is required`), building on
   the `bless` arm landed here. Mostly runtime.
2. **The lexer unblock** (flex fix or hand-patch `raku.lex.c`) — unblocks RK-OO-A2 privacy/rw, RK-OO-A3 `@./%.`,
   RK-OO-A4 typed/default attrs. Cross-cutting; the single biggest unblocker for the OO ladder.
3. **RK-OO-B3/B4** (BUILD/TWEAK submethods; required attrs), **RK-OO-F** (introspection `.^name`/`.^methods`).
4. **m4 `x86_uid` dup-label fix** — unblocks 3+ class m4 programs (emitter, benefits all languages).

## Build / test
```
cd SCRIP && rm -f scrip && make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_raku.sh    # 80/0/7 both modes
bash scripts/test_smoke_icon.sh    # 12/12 ; bash scripts/test_smoke_snobol4.sh # 7/7
# parser regen only if editing raku.y:  cd src/parser/raku && bison -d raku.y -o raku.tab.c   (NOT flex)
```

## Commits
| Commit | Repo | What |
|---|---|---|
| `5370ad1` | SCRIP | RK-OO-A2 accessor half (earlier this session) |
| `41a9393` | SCRIP | RK-OO-B1: user `method new` + `bless` + type-object dispatch |
| (this doc + GOAL trim/marks/watermark) | .github | handoff |
