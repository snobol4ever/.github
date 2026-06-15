# HANDOFF — Raku-BB OO RK-OO-A4: typed + constant-default attributes

**Date:** 2026-06-15 · **Author:** Claude (Opus 4.8) · **Repos:** SCRIP + .github

## TL;DR
`has Int $.x;` (typed — type parsed and **ignored**) and `has $.x = 42;` (constant default) now parse and
work in BOTH native modes. A default is the constant value applied at construction iff the named arg is
absent — Rakudo BUILDPLAN **op 400** (the constant-`build` case). The mechanism is a single chokepoint:
`DatType` stores per-field defaults, and `dat_construct` applies them, so `obj_new` AND `self.bless(...)`
both get defaults for free.

```raku
class Box { has $.v = 42; }
my $b = Box.new();        # → 42   (default applied)
my $c = Box.new(v => 7);  # → 7    (named arg wins)

class Cfg { has Int $.limit = 100; }   # typed + default; type ignored
Cfg.new().limit;          # → 100

class Animal { has $.legs = 4; }
class Dog is Animal { method describe() { return $!legs } }
Dog.new().describe();     # → 4    (parent default inherited)
```

## Gates (all green this session)
- **Raku m3/m4 86 PASS / 0 FAIL / 7 EXCISED / 93** (was 80/0/7/87 — +6 smokes, no FAILs).
- **Icon 12/12, SNOBOL4 7/7** unchanged. `g_vstack`=0, `bb_bin_t`=0, IR_NFA=0.
- `test_gate_no_lang_names.sh`: **my symbols 0 hits** (reds are the pre-existing Prolog `pl_gz_*`/`_pl` + SNOBOL4
  tail, owner-only). `util_template_purity_audit.sh`: the single `bb_call_write_slot.cpp` baseline site, UNCHANGED
  (0 templates touched). `audit_concurrency_invariants.sh`: the 5 pre-existing LOWER/EMITTER md5 + stale-`lower.c`
  VIOLATIONs (in `GOAL-ICON-BB.md`/`GOAL-PROLOG-BB.md`, not Raku), UNCHANGED. **0** dup `case TT_HAS_DECL`.
- 6 new smokes, all `[m3 PASS] [m4 PASS]`: `attr_typed`, `attr_default_int`, `attr_default_str`,
  `attr_default_override`, `attr_typed_default`, `attr_default_inherited`.

## What landed

### Parser (`raku.y`, bison-regen only — NO lexer change; honors the LEXER CONSTRAINT)
`Int` is recognized as an ordinary `IDENT` in the rule action (same trick as `is`). 6 new `class_body_list` rules:
- `KW_HAS IDENT VAR_TWIGIL ';'` / `KW_HAS IDENT VAR_SCALAR ';'` — **typed, no default** → a plain `TT_VAR` field
  (the type `IDENT` is `free()`d and dropped; downstream identical to `has $.x;`).
- `KW_HAS VAR_TWIGIL '=' expr ';'` / `KW_HAS VAR_SCALAR '=' expr ';'` — **default** → new `TT_HAS_DECL` node
  (`v.sval` = field name, `c[0]` = default expr).
- `KW_HAS IDENT VAR_TWIGIL '=' expr ';'` / `KW_HAS IDENT VAR_SCALAR '=' expr ';'` — **typed + default** → same
  `TT_HAS_DECL` (type dropped).

Conflicts steady at **31** (B1 baseline) — the new rules are lookahead-separable (`IDENT` vs `VAR_*` after
`KW_HAS`; `;` vs `=` after the var), zero new conflicts. New AST node `TT_HAS_DECL` added to `ast.h` (enum +
name table). `TT_HAS_DECL` appears ONLY when there is a default — typed-no-default stays `TT_VAR`, so the
existing field-spec loops (which skip only `TT_SUB_DECL` and read `ch->v.sval`) include it with NO change.

### Driver / runtime (`driver_data.c`, `driver_private.h`)
- `DatType` gains parallel arrays `DESCR_t defaults[64]` + `char has_default[64]` (zeroed by the existing
  `memset` in `dat_register`).
- New setters `dat_set_field_default_{i,s,r}(cls, field, v)` — find the field by name, store a typed `DESCR_t`
  (`INTVAL`/`STRVAL(GC_strdup)`/`REALVAL`) + flag.
- **`dat_construct` is the single chokepoint:** after copying args, `if (has_default[i] && field[i].v == DT_SNUL)
  field[i] = defaults[i];`. Absent field ⇒ default; explicitly-passed arg (non-`DT_SNUL`) ⇒ caller wins. Both
  `obj_new` and the `bless` arm call `dat_construct`, so neither needed a per-site change.
- `class_inherit` rewritten to carry `defaults`/`has_default` alongside fields in the merge (parent-first), so a
  parent's default inherits into the child idempotently.
- m4 accessors `dat_type_field_has_default(i,j)` / `dat_type_field_default(i,j)` expose the stored default to the
  emitter.

### Lower (`lower_raku.c`)
After `record_register(spec)` for each class, `rk_register_classes` iterates the class children and for each
`TT_HAS_DECL` whose default `c[0]` is a literal (`TT_ILIT`/`TT_QLIT`/`TT_FLIT`) calls the matching setter. This
runs for BOTH modes (lowering precedes emission), so the in-process `dat_types[]` carries defaults for m3 and is
the source the m4 emitter reads.

### m4 emitter (`scrip.c` `proc_startup`)
A new block parallel to the `class_inherit` emission: for each class field with a default, emit class name + field
name as `.byte` rodata, then the value (`mov rdx, <int>` / `.byte` string + `lea rdx` / `.quad` bits + `movsd
xmm0`) and `call dat_set_field_default_{i,s,r}@PLT`. The standalone binary thus repopulates defaults at startup —
m3/m4 byte-faithful by construction (verified: identical output on all 6 smokes + the real-default probe).

## Why this layer (architecture note honored)
OO is overwhelmingly runtime. Defaults are value-work on `DESCR_t` fields in the record system — no ports, no
template bytes, no IR/AST walk on the run path. The only emitter touch is the driver's hand-written `proc_startup`
preamble (exempt from TEMPLATE-ONLY — that rule governs `BB_templates/`/`XA_templates/`, mirrored exactly on the
existing `record_register`/`class_inherit` preamble emission). FACT-RULE clean.

## ⚠️ DEFERRED (none block the ladder)
1. **Closure / expression defaults** (`has $.x = computed()`, `has $.x = $!other + 1`). Only literal constants
   (`ILIT`/`QLIT`/`FLIT`) are captured; a non-literal default is **silently skipped** (field stays the type
   default — no crash, no wrong value, just no default). True op-400 needs a per-field default *closure* threaded
   through the record system and run at construction time (with `self` bound for cross-attr refs). This is the
   bulk of remaining B2 BUILDPLAN work.
2. **Type-constraint enforcement** (`has Int $.x` rejecting a `Str`). The type is parsed but **discarded**;
   enforcing it needs the type name carried into the spec and a check in `dat_construct`/`field_set`.
3. **Native-primspec attributes** (`int`/`num`/`str`, BUILDPLAN ops 1/2/3/1500-series). SCRIP attrs are all
   opaque `DESCR_t`; no unboxed native slots.

## ⚠️ GOTCHA honored
`scrip` STATICALLY links the runtime; `out/libscrip_rt.so` is mode-4 ONLY. After every runtime/driver `.c` edit:
`rm -f scrip && make -j4 scrip && make libscrip_rt` — both were rebuilt and both modes re-gated here. Parser regen
was `cd src/parser/raku && bison -d raku.y -o raku.tab.c` (NO flex — LEXER CONSTRAINT).

## Files touched
**SCRIP:** `src/contracts/ast.h` (TT_HAS_DECL enum + name), `src/driver/driver_private.h` (DatType defaults +
setter decls), `src/driver/driver_data.c` (3 setters, 2 accessors, default-carrying `class_inherit`,
default-applying `dat_construct`), `src/parser/raku/raku.y` (+ regenerated `raku.tab.c`/`raku.tab.h` via `bison
-d`), `src/lower/lower_raku.c` (literal-default setting after `record_register`), `src/driver/scrip.c` (m4
default-setter emission), `scripts/test_smoke_raku.sh` (+6 smokes).
**.github:** `GOAL-RAKU-BB.md` (RK-OO-A4 marked `[~]` done/deferrals; watermark) + this handoff.

## Build / test
```
cd SCRIP && rm -f scrip && make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_raku.sh    # 86/0/7 both modes
bash scripts/test_smoke_icon.sh    # 12/12 ; bash scripts/test_smoke_snobol4.sh # 7/7
# parser regen only if editing raku.y:  cd src/parser/raku && bison -d raku.y -o raku.tab.c   (NOT flex)
```

## Next on the OO ladder (priority order — OO is the lead)
1. **RK-OO-B2 closure defaults / BUILDPLAN op-list** — the remaining default work (expression/closure defaults
   run at construction) + required attrs (op 800, `is required`). Builds directly on the `defaults[]` slot landed
   here; the literal path is the constant-fold subset of the full closure path.
2. **The lexer unblock** (flex fix or hand-patch `raku.lex.c`) — unblocks RK-OO-A2 privacy/`is rw`, RK-OO-A3
   `@.`/`%.`, and would also let `has Int $.x` enforce the constraint cleanly. Single biggest cross-cutting unblocker.
3. **RK-OO-B3/B4** (BUILD/TWEAK submethods; required attrs), **RK-OO-F** (introspection `.^name`/`.^methods`).
4. **m4 `x86_uid` dup-label fix** — unblocks 3+ class m4 programs (emitter; benefits all languages).

## Commits
| Commit | Repo | What |
|---|---|---|
| (this session) | SCRIP | RK-OO-A4: typed + constant-default attributes (both native modes) |
| (this doc + GOAL mark/watermark) | .github | handoff |
