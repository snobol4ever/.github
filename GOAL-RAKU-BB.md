# GOAL-RAKU-BB.md — Raku goal-directed onto the shared four-port IR (the fourth musketeer)

## ★ CURRENT PRIORITY — READ FIRST (Lon, 2026-06-15): RAKU OOP IS THE LEAD

OOP is Raku's signature contribution (the other five languages are non-OO) and is THE priority ahead of RK-GRAM-3 and RK-EMIT-MAP/GREP. Work the OO LADDER below top-to-bottom; take the first incomplete (`- [ ]`) rung. Grammar/regex and map/grep rungs are PARKED until Lon says otherwise.

### LEXER STATUS (updated 2026-06-24)
The "flex can't regen" wall is RESOLVED. Root cause: column-0 `/*---*/` separators in the rules section were unrecognized by flex 2.6.4. Fix: indent them by one space in `raku.l`. Verified: flex now regens `raku.lex.c` with rc=0, and the new lexer is behavior-equivalent across all 102 smokes (97/0/7 both modes). `raku.lex.c` is now the flex-2.6.4 regen. **Bison regen is always fine. To regen lexer: `cd src/parser/raku && flex -o raku.lex.c raku.l` (rc=0, 31 conflicts unchanged).**

### OO LADDER
Anchored to Rakudo `Metamodel/{BUILDPLAN,C3MRO,MROBasedMethodDispatch,RoleToClassApplier}.nqp`, `Mu.rakumod`, `Attribute.rakumod`. OO is overwhelmingly RUNTIME (`obj_new`/`meth_call`/`dat_field_*` + the `DatType`/`DATINST_t` model). Parser+lower changes only where new syntax must be recognized.

- [x] **RK-OO-A2 — public-attribute AUTO-ACCESSOR + `is rw` + PRIVACY — CLOSED (privacy LANDED both modes 2026-06-27).** `.x()` routes to the field value via `meth_call` fallback (`meth_is_user_proc` guard; user method wins). `is rw`: external accessor write is gated on the trait — Raku-default read-only attributes DIE on `$obj.x=v` and `self.x=v` (X::Assignment::RO "Cannot modify an immutable"); `is rw` opts into a writable accessor; internal `$!x=v` (direct attribute / TWIGIL) ALWAYS writes regardless of the trait. **PRIVACY (`$!` inaccessible from outside) — LANDED both modes:** a `$!`-declared attribute gets NO public accessor (faithful to Rakudo `Attribute.compose`, which only mints an accessor when `has_accessor`, i.e. the `$.` public twigil), so external `$obj.x` AND `$obj.x()` BOTH die ("not accessible outside of class"); internal `$.x`/`$!x` (direct attribute via `self`) ALWAYS read/write. Mechanism: lexer keeps the twigil char (`$.x`→`.x`, `$!x`→`!x`, plus `@`/`%` forms); declaration nodes carry the prefixed name, decoded to `(priv, bare-name)` at the single registration site in `lower_raku.c` (a union-clobber pitfall — `tree_t.v` is a union, so a flag-in-`ival` would destroy the name pointer — was caught; privacy is string-encoded instead); per-field `priv[64]` on `DatType` threaded through `class_inherit_multi`/`class_compose_role` field-merge; MRO-walking `dat_field_is_private`; emitted to the m4 binary via `dat_set_field_priv@PLT` (mirrors `dat_set_field_rw`). Enforcement at three runtime sinks: `meth_call` accessor fallback, `field_set_pub` (external write), and the NEW `field_get_pub` (external read — external `TT_FIELD` reads now lower to this privacy-gated by-name call so the no-paren `$obj.x` form is gated too; internal `TT_TWIGIL_FIELD` stays on the ungated `IR_FIELD_GET`/`field_get` path). New AST node `TT_RW_DECL`; lowerer routes `TT_FIELD`→`field_set_pub`/`field_get_pub` (gated) vs `TT_TWIGIL_FIELD`→`field_set`/`IR_FIELD_GET` (unconditional). Smokes: `field_write_rw`/`field_write_ro_dies`/`field_write_rw_typed`/`field_write_rw_inherited` (is rw); `priv_attr_external_dies`/`priv_attr_internal_ok`/`priv_attr_inherited_dies`/`priv_attr_inherited_internal_ok`/`priv_attr_public_sibling_ok`/`priv_attr_mixed_internal`/`priv_attr_external_noparen_dies`/`pub_attr_external_noparen_ok` (privacy); `accessor_paren`/`accessor_method_wins`/`accessor_inherited`.
- [~] **RK-OO-A3 — `@.`/`%.` array & hash attributes — LANDED (2026-06-24).** `has @.items;`/`has %.opts;` (plain + typed `has Int @.xs`) declare aggregate attributes that auto-vivify to an EMPTY aggregate (the `\x01`-separated empty string `""`, since Raku arrays AND hashes are both string-encoded here), distinct from a scalar attr's `Any`. Lexer mints `VAR_ARRAY_TWIGIL`/`VAR_HASH_TWIGIL` for `@.`/`@!`/`%.`/`%!` (flex regen rc=0); new AST `TT_ARR_DECL`/`TT_HASH_DECL`; per-field `sigil` on `DatType` (threaded through `class_inherit`) drives vivification in `dat_construct` (guarded `!required` so a future required-aggregate still DIEs); replayed into the m4 binary via `dat_set_field_sigil@PLT` (mirrors `is-rw`). Accessor `.items` rides the by-name field resolver; result is bound to a var before further method calls (existing grammar limit). `.new(field => @var)` plumbs a provided aggregate, overriding the empty default. In-method `@.x`/`%.x` atom access lowers to `TT_TWIGIL_FIELD`. Smokes (both modes): `attr_array_empty`/`_init`/`_inherited`/`_in_method`/`attr_hash_empty`/`_init`. **`@!`/`%!` privacy enforcement — LANDED both modes (2026-06-27, with RK-OO-A2 privacy):** private aggregate attributes get no public accessor; external access dies, the public `@.`/`%.` accessor still resolves. Smokes: `priv_array_attr_external_dies`/`priv_hash_attr_external_dies`. DEFERRED: traits on aggregates (`has @.x is rw`/`is required` — the `IDENT IDENT` trait grammar covers only `$`-sigils; belongs with A2/B2 when generalized).
- [~] **RK-OO-A4 — typed + constant-default attributes — LANDED (2026-06-15).** `has Int $.x` (type ignored) and `has $.x = 42` (constant default) work. DEFERRED: (a) closure/expression defaults (`has $.x = computed()`) — needs native sub-block execution; (b) type constraint enforcement; (c) native-primspec attrs.
- [~] **RK-OO-B2 — BUILDPLAN.** op-0 DONE (B1 bless + obj_new default path). op-800 (`is required` death) LANDED (2026-06-24): `dat_construct` sets `g_script_exception` + `rt_script_die_surface` fires for absent required attrs; native `die` route wired (`g_script_try_depth` gate for future try/CATCH). Present + absent cases both PASS both modes. DEFERRED: op-400 (closure/expression defaults) — needs native sub-block execution (same wall as map/grep). Smokes: `attr_required_present`/`_typed_present`/`_inherited_present`/`_absent`/`_absent_inherited`/`die_uncaught_halts`.
- [~] **RK-OO-B3 — TWEAK submethod — LANDED (2026-06-24).** `method TWEAK()` auto-fires at construction from `dat_construct` chokepoint via `rt_fire_buildplan_tweak`; parent→child order (BUILDALLPLAN); correctly non-inheriting. Smokes: `tweak_fires`/`tweak_derived_attr`/`tweak_inherited_order`. OPEN: `BUILD` submethod (`:$x` named params in signature are lexer-blocked — now unblocked; add `VAR_NAMED_PARAM` token to `raku.l` + bison rule for `method BUILD(:$x) {…}`).
- [x] **RK-OO-C3 — C3 MRO LANDED (2026-06-24, `c802035`).** `DatType` gains `mro[64][64]/mro_len`; `dat_register` seeds `[self]`; `class_inherit` computes `[child]++parent.mro`; `dat_mro()` accessor; `resolve_method_chain` and `rt_fire_buildplan_tweak` walk the MRO instead of single `dat_parent()` hops — behavior-neutral on all prior tests. Smokes: `mro_method_grandparent`/`mro_override_middle_wins`/`mro_attr_grandparent`/`mro_tweak_order_3`.
- [x] **RK-OO-C5 — `callsame`/`nextsame`/`callwith` LANDED (2026-06-24, `c802035`).** Re-dispatch ledger `g_redisp` captures invocant/mname/MRO/found_idx per `meth_call`; `resolve_method_chain` gains found-index out-param; shared `invoke_method_proc` helper (de-duplicates dispatch tail); chaining works (each re-dispatch pushes its own frame). Registered as known builtins → `CALL_ROUTE_FN` both modes. NOTE: `callwith(expr OP expr)` inherits a pre-existing general call-arg limitation (binop arg marshaled as leaf; reproduces with `abs($x+10)` on clean HEAD); use intermediate var. Smokes: `callsame_2level`/`callsame_3level`/`nextsame_passes_args`/`callwith_new_arg`/`callwith_var_arg`.
- [x] **RK-OO-C6 — multiple inheritance (`is A is B`) LANDED (2026-06-24, `c802035`).** Grammar: `is_clauses` non-terminal collects N parents into `\x01`-delimited `sval`; bison regen rc=0, 31 conflicts unchanged, no lexer change. `DatType` gains `parents[8][64]/nparents`; `class_inherit_multi` merges all ancestors' fields + computes true C3 via `c3_merge`; `class_inherit` delegates. Bug fixed: `c3_merge` pointer aliasing (snapshot `cand` before mutating lists). Mode-4 emitter rewritten: rodata pointer-table → `class_inherit_multi@PLT` (was single `class_inherit@PLT` using `dat_parent`). `dat_type_nparents`/`dat_type_parent_at` accessors. Smokes: `diamond_method_c3`/`diamond_callsame_c3order`/`diamond_attr_merge`/`mi_two_parents_methods`.
- [x] **RK-OO-D1..4 — Roles — LANDED (Claude Sonnet 4.6).** `role R {…}` declares a role; `class C does R` FLATTENS R's methods + attributes into C at COMPILE TIME (Rakudo `RoleToClassApplier`). **D1:** new AST `TT_ROLE_DECL`; lexer `KW_ROLE`; grammar `role_decl` (reuses `class_body_list`) + `is_clauses` now TAGS each clause `i`(is/parent)/`d`(does/role) into one `\x01` channel; role registers a `DatType` and its methods compile once as `R__m` through the shared proc-lowering loop; resolver `resolve_method_chain` gains a composition-lookup — at EACH MRO level it tries the class's own `K__m`, then `Ri__m` for each role K composes, before descending → Rakudo precedence **own > role > inherited** (role is NOT in the MRO; `does` ≠ `is`). `DatType` gains `roles[8][64]/nroles`; `class_compose_role` (field-merge + role-record); mode-4 bakes `class_compose_role@PLT` so the binary's class carries its roles list. **D2 (conflict):** 2+ composed roles supplying the same method with no class-local resolution → `X::Role::Unresolved::Method`, a COMPILE-TIME error (in-process during m3 --run; m4 --compile refuses the `.s`; both → empty stdout = harness PASS). Detection in `class_compose_role` (checks prior-composed roles) driven by per-type `methods[32][64]/nmethods` on `DatType` (`dat_add_method`, emitted via `dat_add_method@PLT`). Class-own or sibling-role resolution works; distinct names compose freely. **D3 (required stubs):** `method m() {...}` — the yada `{...}` lexes to `YADA` → a `TT_YADA`-bodied `TT_SUB_DECL` recognized as a STUB (not registered/compiled as a real proc); the consumer must provide a real `m` (itself or a sibling role) or COMPILE-TIME error; checked in the composition pass from the AST. **D4 (punning):** `Role.new(...)` used directly as a class — falls out of role-as-DatType registration, both modes. Smokes (all m3+m4): `role_method_flatten`/`role_attr_on_consumer`/`role_own_method_wins`/`role_beats_inherited` (D1), `role_conflict_unresolved`/`role_conflict_resolved`/`role_two_roles_distinct` (D2), `required_unimplemented`/`required_by_class`/`required_by_sibling` (D3), `pun_method`/`pun_attr` (D4). 31 bison conflicts unchanged throughout. DEFERRED: parametric/generic roles (`role R[::T]`), role-to-role composition (`role does role`), `$!`/`@!`/`%!` privacy on role attrs, fresh-pun-per-use identity.
- [x] **RK-OO-E1..2 — Multi-dispatch (`multi sub`) — LANDED both modes (Claude Sonnet 4.6).** `multi sub foo(T $a, ...)` candidates register as ordinary procs under a signature-mangled name `foo$arity$T0$T1…` (separator `$` is asm-safe so the name survives as a mode-4 GAS symbol). Lexer mints `KW_MULTI`/`KW_PROTO`; `param_list` grows typed-param productions (`IDENT VAR_SCALAR`, type stashed as a child `TT_QLIT`); the `multi sub` grammar action mangles the name via `rk_multi_mangle`. A compile-time pre-pass in `lower_raku_stage2` derives the base-name set from any sub name containing `$`; a call to a multi base name is re-lowered as `__multi_call("base", args…)` (a known builtin). The runtime dispatcher `__multi_call` (in `by_name_dispatch.c`) enumerates the **runtime** proc registry (`rt_proc_enum_count`/`rt_proc_enum_name` over `g_rt_gen_procs` — populated by `rt_proc_register` in BOTH modes, so it works standalone where `g_stage2` is empty), filters candidates by arity + per-arg type acceptance, and invokes the NARROWEST accepting candidate via `rt_call_proc_descr`. Narrowness is the faithful Rakudo `is_narrower` (`BOOTSTRAP.nqp`): subtype beats supertype (class MRO + a small numeric lattice), typed beats untyped (`Any` is top), `narrower>0 && narrower+tied==arity`. Smokes (all m3+m4): `multi_arity`/`multi_type_int_str`/`multi_typed_beats_untyped`/`multi_subclass_beats_parent`/`multi_two_typed_args`. **`multi method` — LANDED both modes (2026-06-27):** method-side multi-dispatch (Rakudo `MROBasedMethodDispatch` over typed candidates). `multi method foo(T $a)` candidates register as `Class__foo$arity$T0…` procs (the same `$`-mangle as multi sub, asm-safe); `dat_add_method` records the BASE name for `.^methods`. `meth_call` routes a base-name call with no direct `Class__foo` proc through a new MRO-scoped dispatcher `rt_multi_meth_dispatch` (mirrors `__multi_call`, but enumerates `K__foo$…` for each K in the C3 MRO and threads the invocant as arg0), filtering by arity + per-arg type acceptance and invoking the narrowest via `invoke_method_proc`. Candidates compose across the MRO (a `multi method` in a parent + one in the child are both reachable on a child instance). Both modes work because user-method candidate procs are in the runtime proc registry (`rt_proc_enum`) in m3 and m4 alike. Smokes (all m3+m4): `multi_method_type`/`multi_method_arity`/`multi_method_mro_inherited`/`multi_method_subclass_narrower`. DEFERRED: explicit `proto sub …{*}` syntax, slurpy/optional/`where`-constraint params, true ambiguity error (currently first-un-beaten wins deterministically).
- [~] **RK-OO-F — Metaobject/introspection.** `.^name` LANDED (2026-06-24). `.WHAT` LANDED (2026-06-24). `.isa`/`.does` LANDED both modes (Claude Sonnet 4.6, 2026-06-27): `$obj.isa(T)` true iff T is in MRO; `$obj.does(R)` checks composed roles too. Smokes: `isa_true_self_and_parent`/`isa_false_sibling`/`does_role`. `.^parents` LANDED both modes (2026-06-27): ancestor class names space-joined. Smoke: `meta_parents_chain`. **`:D`/`:U` definiteness constraints + `.defined` + `my $x;` LANDED both modes (2026-06-27):** `Int:D $x` accepts only defined ints; `Str:U $x` accepts only undefined (SNUL) values; mangled as `TypeName_D`/`TypeName_U` in proc names (colon→underscore, GAS-safe). `.defined` returns 1 if not SNUL, 0 if SNUL. `my $x;` (uninit decl) lower as ASSIGN←LIT_NUL; new NUL arm in `bb_assign_local` emits `{0,0}` directly without needing a rhs slot. `rt_mc_accepts` and `rt_mc_narrower` updated to parse both `:D`/`:U` (source form) and `_D`/`_U` (mangled form); narrowness: `T:D` beats `T`. Smokes: `defined_method_true_false`/`multi_colon_d_dispatch`/`multi_colon_u_dispatch`. **`.^methods`/`.^attributes` LANDED both modes (Claude Sonnet 4.6, 2026-06-27):** Rakudo `MethodContainer.nqp`/`AttributeContainer.nqp` non-`:local` form — the full set across the C3 MRO (most-derived first), including composed-role methods, rendered as space-joined name lists in the string metamodel. New MRO-walking accessors `dat_methods`/`dat_attributes` (driver_data.c) with dedup; wired into the `^`-handler in by_name_dispatch.c. Works both modes because the per-type method/role/field tables are already replayed into the m4 binary (`dat_add_method@PLT` + class spec). **Codegen fix (latent, pre-existing): the Raku/Icon mode-4 branch (`scrip.c` `is_icon||is_raku`) never set `g_m4_dense_nid=1`, so boxes got pointer-hash node-ids (`(uintptr_t)nd%100000`) that COLLIDE — surfaced by any program with 2+ user methods + 2 metamethod calls (e.g. `.^name`+`.^parents` on non-empty classes), an assembler dup-label `bbNNNNN_α`. Set dense+`g_bb_alpha_seq_reset` at branch entry → collision-free sequential ids. Icon rung suite 208/208 both modes unchanged; all 253 Icon demo `.s` artifacts relabeled (behavior-identical).** Smokes: `meta_methods_mro`/`meta_attributes_mro`/`meta_methods_role`/`meta_methods_typeobj`. **`.clone` LANDED both modes (Claude Sonnet 4.6, 2026-06-27):** Mu.rakumod `multi method clone(Mu:D: *%twiddles)` — shallow-copies the invocant's attribute values into a fresh same-class instance; named twiddles (`$obj.clone(attr => v)`) override specific attrs, the rest carried verbatim. Runtime-only (`meth_call` handler before user-method resolution, reusing `dat_construct` field-fill so inherited MRO attributes copy for free; original untouched). Smokes: `clone_basic`/`clone_twiddle`/`clone_inherited`. OPEN: `:D`/`:U` on non-multi params (runtime type checks), `where` constraints.
- [~] **RK-OO-G1..6 — Advanced.** G1 (`.Str`/`.gist`/`.raku` override) LANDED both modes (2026-06-27). User-defined `method gist`/`Str`/`raku` are honored in the implicit stringification contexts faithful to Rakudo `Mu.rakumod` (say→`.gist`; print/put→`.Str`; `~`/interpolation→`.Str`). Implementation is RUNTIME-only and VALUE-SHAPE dispatched (a `DT_DATA` value with a user method on its `DatType`; no language gate): new exported helper `rk_obj_stringify(d, use_gist)` in `by_name_dispatch.c` resolves the class's `gist`/`Str` via the existing `resolve_method_chain`+`meth_is_user_proc`+`invoke_method_proc` and falls back to the prior default (class name) when no override exists. Wired into three sinks: `rt_write_any_nl` (io_format.c — the single-arg slot say box `bb_call_write_slot`→`rt_write_any_nl`, say-only ⇒ gist), `out_write_descr` (by_name_dispatch.c — the multi-arg by-name `write`/`writes` path, gist for say / Str for print; gated behind a not-yet-grammar-reachable multi-arg comma-`say`), and `str_concat_d` (string_ops.c — the `~` runtime, also used by string interpolation; ⇒ Str, and incidentally fixes the prior object-stringifies-to-empty bug in concat). Inherited overrides resolve through the MRO for free. Explicit `.gist()`/`.Str()`/`.raku()` already dispatched through the normal user-method path (substrate from RK-OO-A2). Smokes (all m3+m4): `gist_override_say`/`str_override_concat`/`str_override_interp`/`gist_no_override_default`/`raku_str_gist_explicit`/`gist_override_inherited`. Peers unaffected (the `DT_DATA` arm only triggers for Raku objects). **G6** `.=` LANDED both modes (2026-06-27): `$x .= meth(args)` desugars to `$x = $x.meth(args)` (Rakudo `Mu.rakumod` `dispatch:<.=>`: `mutate = mutate."$name"(|c)`); pure grammar sugar — new lexer token `OP_DOTEQ`, three `sub` productions building `TT_ASSIGN(var, TT_METHCALL(var, meth, args))`, NO new AST kind / NO lowering / NO runtime change (reuses the existing assign+method-call path); covers no-paren (`$s .= uc`), empty-paren (`$s .= lc()`), and user-method-with-arg (`$c .= add(5)`) forms; bison/flex regen rc=0, 31 conflicts unchanged. Smokes: `dotassign_builtin_uc`/`dotassign_empty_paren`/`dotassign_user_meth_arg`. OPEN: **G2** operator overload `multi sub infix:<op>` (needs lexer `infix:<…>` token + grammar; rides existing E1..2 multi-dispatch; the call-site seam is a runtime hook in the arithmetic helpers diverting `DT_DATA` operands to `__multi_call`); **G3** `handles` attribute delegation; **G4** `but`/runtime mixin; **G5** `enum`/`subset`.

---

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

**No language-specific logic in any BB or XA C++ template.** All delineated operations are enveloped in
unique BBs; each BB does NOT have varying runtime behavior depending on language. Templates dispatch on IR
shape and representation flags only. FORBIDDEN inside `src/emitter/BB_templates/` and
`src/emitter/XA_templates/`: language enums/guards (`IR_LANG_*`, `LANG_*`, `is_<lang>`), language-named
template functions/files/dispatch arms, and hardcoded language-builtin names. Behavior that differs by
language belongs in the runtime (by-name dispatch) or in LOWER (a different IR shape → its own unique BB) —
never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (XA scanned clean 2026-06-03); fix
ladder: LB-* in `GOAL-PASCAL-BB.md`. COMPLETION TEST: the audit's Tier-1 grep over `BB_templates/` +
`XA_templates/` returns 0 sites.

## ▶ GRAMMAR/REGEX DIRECTION (2026-06-14) — PARKED BEHIND THE OO LADDER

RK-GRAM-3 (recursive-descent grammar engine) is PARKED behind OO. Direction stays authoritative for when grammar work resumes. Grammars register and `.parse` dispatches end-to-end in all three modes today (`f3b1837`); recursive grammars are the remaining gap.

**DIRECTION (Lon 2026-06-14):** NFA is the WRONG primary engine for top-down recursive-descent. The NFA-on-Byrd-boxes apparatus is DELETED (`d63c374`). Real Raku's matcher IS recursive descent (backtracking cursor machine). Subrule `<name>` recursion is provably beyond any finite automaton → needs recursive descent. The C NFA matcher `re.c` (`nfa_build`/`nfa_exec`) is KEPT for `~~ /regex/` only.

- [ ] **RK-EMIT-MAP/GREP** — `bb_rk_map.cpp`/`bb_rk_grep.cpp` (`IR_MAP`/`IR_GREP`). m3/m4 EXCISED. Blocked on Icon GZ-7 (IR_ASSIGN ζ-slot store).
- [ ] **RK-GRAM-3 (THE SEAM)** — recursive-descent grammar engine. Build subrule `<name>` recursion + backtracking on the EXISTING four-port box-resumption substrate (SNOBOL4 pattern boxes ARE a backtracking recursive-descent matcher — γ=advance, ω=fail/redo; alternation=`IR_ALT`; subrule call = recursion into another box graph). REPLACES `gram_expand`'s flatten-to-NFA (depth-16-capped stopgap). Needs full budget + `ARCH-x86.md`/`ARCH-SCRIP.md` reads first.
- [ ] **RK-GRAM-4..6** — LTM + proto dispatch; actions + Match tree; convergence/control/adverbs. Sits on RK-GRAM-3.

---

## ⛔ `bb_bin_t` IS ABOLISHED — PATCH METADATA TRAVELS IN-BAND; NO FUNCTION COUNTS BYTES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**The `bb_bin_t { sites, labels, is_def, bytes }` struct and `bb_emit_asm_result(out, bin)` /
`bb_emit_asm_result_pairs(out)` are DELETED (Lon directive 2026-06-02). No box may name `bb_bin_t`, declare a
`bb_bin_t bin`, or call `bb_emit_asm_result`.** The struct was the carrier for a hand-counted / FUNCTION-counted
patch-offset table — the `bin.sites.push_back((int)b.size())` idiom, which is invalid: it computes a patch offset
with `b.size()` (a function of the running buffer) instead of letting the position be DISCOVERED. That idiom is the
exact nonsense the template revamp kills, and the strongest way to kill it is to remove the type so the idiom does
not COMPILE — the same enforcement-by-deletion as the no-`pBB`/`_.node` rule (a grep gate is unnecessary when the
compiler rejects it).

**THE ONE WAY: every BB template returns ONE concatenation of `x86(...)` calls and is emitted by
`bb_emit_x86(out)`.** Patch sites are TAGGED RECORDS inside that string (`L` literal bytes / `J` rel32-to-port /
`D` define-port / internal-label `L(n)` / pair-loop `E`/`F`); `bb_emit_x86` walks them and DISCOVERS each byte
position as it copies. There is NO separate offset list, so NOTHING can drift and no function ever counts bytes.
This SUPERSEDES the earlier "TWO LITERAL FORMS ONLY" framing of the BINARY arm: the hand-coded literal byte map
with a literal offset tuple was a TRANSITIONAL form; the in-band record stream is the END form, and it is what the
`b.size()` ledger was driving toward — the ledger reaches zero when the last `bb_bin_t` user is converted, not by
rewriting offset tuples by hand.

**FORBIDDEN:** `struct bb_bin_t`, `bb_bin_t bin`, `bb_emit_asm_result(...)`, `bin.sites`/`bin.labels`/`bin.is_def`,
and `(int)b.size()` (or any `.size()` of a running byte buffer used as a patch offset) anywhere in
`src/emitter/BB_templates/`, `XA_templates/`, or `emit_str.*`. The carve-out for `bb_emit_asm_result` walking a
finished string is GONE — that function no longer exists. (A box NOT YET converted is a LOUD `x86_bomb(msg)` stub
— `extern "C" void bb_foo(...) { bb_emit_x86(x86_bomb("bb_foo: …")); }` — which COMPILES + LINKS so SCRIP stays
green and ABORTS beautifully when reached; each owning session replaces its stubs with real `x86()` concatenations
as its own test reaches them.)

**ENFORCEMENT:** structural (the compiler) — `bb_bin_t` is declared nowhere, so any use fails to compile. Plus a
one-line gate `scripts/test_gate_no_bb_bin_t.sh` (comments stripped): `bb_bin_t` / `bb_emit_asm_result` live code
references == 0. **COMPLETION TEST:** (a) `emit_str.h` declares neither `bb_bin_t` nor `bb_emit_asm_result`; (b)
the gate reads zero; (c) every BB template is emitted via `bb_emit_x86`; (d) `make scrip` + `make libscrip_rt`
rc=0; (e) this FACT RULE body is byte-identical across the four GOAL-*-BB files.

## ⛔ ONE MEDIUM, INVISIBLE — NO `IF(MEDIUM_BINARY,…)` INSTRUCTION BRANCH, NO RAW-BYTE PRODUCER IN A TEMPLATE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**A template NEVER writes an instruction twice — once as GAS text, once as raw bytes — and NEVER branches on the
medium to pick between them (Lon directive 2026-06-02).** The forbidden shape (the exact nonsense this rule kills):
```
  + IF(MEDIUM_TEXT,  std::string(" mov rbx, rsp\n"))      // same instruction…
  + IF(MEDIUM_BINARY, x86_Lrec(x86_b3(0x48, 0x89, 0xE3))) // …written a second time as bytes
```
Every instruction goes through ONE `x86(mnem, …)` call; the encoder switches medium INTERNALLY, so the template
body is identical for BINARY and TEXT and a reader cannot tell which medium is active. If an instruction has no
`x86()` form yet, ADD an encoder + dispatch case to `x86_asm.h` (one place, byte-verified vs `as`) — NEVER
hand-encode it inline in the template. The missing encoder is the bug; the medium-branch is the symptom.

**FORBIDDEN inside `src/emitter/BB_templates/*.cpp`:** the raw-byte producers `x86_Lrec`, `x86_Jrec`, `x86_Drec`,
`x86_b1(`, `x86_b2(`, `x86_b3(`, `bytes(`, `u8(`, `u32le`, `u64le`; and any `IF(MEDIUM_BINARY, …)` or
`IF(MEDIUM_MACRO_DEF, …)` carrying instruction bytes. Those record/byte primitives are PRIVATE to `x86_asm.h` (the
encoders' implementation); a template only ever sees the `x86(...)` front-end + the markers (`L(n)`, `FR(off)`,
`FRQ(off)`, `PORT_*`) and the LOUD `x86_bomb(msg)` stub. **ALLOWED carve-out — TEXT-ONLY ANNOTATIONS WITH NO BYTE
FORM:** a box's leading `α:` label (`s_1asm(std::string(_.lbl_α)+":"`) and comments (`s_comment(...)`) exist only
in the GAS arm, so `IF(MEDIUM_TEXT, <comment-or-label>)` with NO matching `IF(MEDIUM_BINARY, <bytes>)` is fine; an
`IF(MEDIUM_TEXT,<gas-instruction>) + IF(MEDIUM_BINARY,<bytes>)` PAIR is the violation. Non-x86 platform arms
(JVM/JS/NET/WASM) are out of scope (X86 ONLY for now) and keep their `s_*asm` text.


**CORRECTION RECORD (Lon 2026-06-06):** RULES.md TEMPLATE-ONLY EMISSION is now corrected to MATCH this rule; its former
"duplicate the byte-producing code into each template file" clause (515aa7d6, 2026-05-28) is DEAD — it predated the
2026-06-02 directive and said the opposite. Restated plainly: ZERO BINARY emission anywhere in a `bb_*.cpp` — not in the
top-level `*_str`, not in any helper it calls (a static helper in the template file is INSIDE the fence; relocating bytes
into helpers changes nothing). `x86()` internals (`x86_asm.h`) are the ONLY place BINARY and TEXT are emitted, side-by-side.

**ENFORCEMENT:** gate `scripts/test_gate_template_medium_invisible.sh` (comments stripped): in `BB_templates/*.cpp`,
the raw-byte producers + `IF(MEDIUM_BINARY`/`IF(MEDIUM_MACRO_DEF` count == 0 (informational WIP baseline; `--strict`
enforces zero). **COMPLETION TEST:** (a) zero raw-byte producers and zero `IF(MEDIUM_BINARY,…)`/`IF(MEDIUM_MACRO_DEF,…)`
in any `BB_templates/*.cpp`; (b) every instruction emitted via an `x86(...)` call; (c) the gate green under `--strict`
and in the Session-Setup gate list; (d) this FACT RULE body byte-identical across the four GOAL-*-BB files.

**THREE FACES OF ONE END STATE.** This rule, the `bb_bin_t`-ABOLISHED rule above, and the no-`pBB`/`_.node` rule are
three faces of ONE converted box: pure `x86()` concatenation reading only `_`. A box that still hand-encodes bytes
ALSO still carries `bb_bin_t` and ALSO branches on the medium; converting it to `x86()` clears all three at once. The
three gates therefore reach zero TOGETHER, box-by-box, as the revamp completes — the prison is escaped only by
finishing the conversion.

## ⛔ NO C BYRD-BOX FUNCTIONS — A BOX IS ENTERED BY JUMPING TO ITS α/β LABELS, NEVER A `(ζ, int entry)` C CALL (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**There is NO such thing as a C byrd-box function. The "brokered BB" concept is ABOLISHED.** A byrd box is
EMITTED machine code. It has exactly TWO entry points, and they are **LABELS** — α (fresh entry) and β
(resume). Control reaches a box by **JUMPING to one of those labels**. A box is NEVER a C function, is NEVER
reached by a C call, and NEVER takes an integer `entry` argument to select α vs β. The C signature
`DESCR_t NAME(void *ζ, int entry)` — a ζ-state pointer plus an `int entry` α/β selector — is **FORBIDDEN**.
It was the discredited brokered-BB calling convention (an "entry kludge"); it is gone. The ONLY driver is the
**mode-2 BB-graph interpreter** (`bb_exec.c`), which walks the IR graph directly and IS the broker/driver;
**modes 3 and 4 are native code in which boxes thread control by jumping between α/β labels** (RULES X86-64
register / subject-model convention) — never through a function pointer plus an `entry` integer. There is no
`bb_broker` driver and no `(ζ, int entry)` box anywhere.

**HISTORY — READ THIS, because it is why the rule now exists in this strongest form.** This prohibition has
stood for **AT LEAST TWO MONTHS**. Lon ordered these C `(ζ, int entry)` byrd boxes DELETED at least **THREE
separate times**, and each time a session either declined, re-introduced them, or held/reverted the deletion
"to keep the build green." A prior plain rule (RULES.md "NO C BYRD-BOX FUNCTIONS") did **not** hold. They
were finally deleted **2026-06-01** — the `pl_*_fn` family (all of `pl_broker.c`), `gen_bb_dcg`,
`gen_bb_oneshot`, `resolve_bb_dcg`, `bb_deferred_var`/`_exported`, `fail_box`, the dead `bb_cap`/`bb_atp`
declarations, **and the `bb_broker` driver itself** (`bb_broker.c`). **KEEPING THE BUILD GREEN IS NOT A
LICENSE TO PRESERVE A FORBIDDEN BOX.** When this signature and a green build conflict, the **signature
loses**: delete the box and tear out its callers (the brokered execution path — Prolog `--run`, brokered
pattern scan, brokered generators — is removed, not preserved). A broken build pending the caller teardown is
acceptable; a surviving `(ζ, int entry)` box is not.

**COMPLETION TEST:** (a) `grep -rnE 'DESCR_t[[:space:]]+[A-Za-z_]+[[:space:]]*\([[:space:]]*void[[:space:]]*\*[[:space:]]*[a-z]*[[:space:]]*,[[:space:]]*int[[:space:]]+entry' src/ --include=*.c --include=*.cpp --include=*.h | grep -v typedef` == 0 (no C byrd-box definition or declaration with the `(ζ, int entry)` signature); (b) no `bb_broker` driver function exists; (c) every emitted box is entered by a jump to an α or β label, never a C call with an `entry` int; (d) this FACT RULE body is byte-identical across the five GOAL-*-BB files.

## ⛔ NO AST AND NO IR DURING MODE-3/MODE-4 EXECUTION (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**During the EXECUTION of a mode-3 (`--run`) or mode-4 (`--compile`) program, NOTHING reads or writes the AST (`tree_t`) or the IR (`IR_t`/`IR_graph_t`).** (Lon directive, 2026-06-13.) The compiler reads the IR exactly ONCE — before execution — to emit the mode-3 RX-slab image or the mode-4 `.S` source; thereafter the produced machine code runs with ZERO reference to either tree. A box's runtime values live INSIDE the box (RO `[rip+disp]`, RW `[ζ=r12+off]`); a runtime helper (`rt_*`) operates only on `Term*`/`DESCR_t` values, never on `IR_t*` or `tree_t*`. This subsumes the IR-NEVER-TOUCHED rule and extends it to the AST: an AST walker that does not EMIT IR is worthless — it may not exist on any run path, not even for mode 2. (The mode-2 `--interp` IR-graph interpreter `IR_interp_once` is the ONLY sanctioned IR walker, and it is reachable ONLY via `--interp`, never from a mode-3/4 produced binary.)

**THE ONE EXCEPTION — `EVAL()` and `CODE()`.** SNOBOL4's `EVAL` and `CODE` are dynamic-compilation builtins: by definition they compile a string into executable form AT RUNTIME (`CONVE_fn`→`EXPVAL_fn`, the `g_eval_str_hook`/`g_eval_pat_hook` rail). Reading/building an IR (or equivalent) at runtime is intrinsic to their meaning, so the prohibition does NOT apply INSIDE `EVAL()`/`CODE()` (and only there). No other construct, builtin, or runtime helper may read or write AST/IR during mode-3/4 execution.

**FORBIDDEN on the mode-3/4 run path:** any `rt_*` (or template-called) function that takes an `IR_t*`/`IR_graph_t*`/`tree_t*`, walks `->operands`/`->c[]`/`->t`/`->op`, reads `IR_LIT(...)`/`IR_EXEC(...)`, dispatches on `IR_e`/`tree_e`, or bakes a live `IR_t*`/`tree_t*` address into emitted code (the `emit_term_from_node_bin` pattern). A box NOT YET converted is a LOUD `x86_bomb(msg)`, never a silent IR/AST read.

**GUARD:** the run path's runtime objects are `Term*`/`DESCR_t` only. **COMPLETION TEST:** (a) no GZ template (`bb_cell_*`) and no mode-3/4-reachable `rt_*` reads AST/IR (grep of the run-path helpers for `IR_t*`/`tree_t*`/`IR_LIT`/`->op`/`->t` == 0, excepting `EVAL`/`CODE`'s `CONVE_fn`/`EXPVAL_fn` rail and the mode-2-only `IR_interp_once`); (b) no function bakes a live `IR_t*`/`tree_t*` into emitted bytes; (c) FACT RULE body byte-identical across all five GOAL-*-BB files.

## ⛔ NO VALUE STACK — EVER (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**SCRIP HAS NO VALUE STACK. NO SESSION, IN ANY LANGUAGE, MAY CREATE ONE.** (Lon directive, 2026-05-31.)
There is nothing like a value stack in SCRIP — every value a BB graph computes or holds at run time lives
INSIDE a box: a READ-ONLY operand constant reached `[rip+disp]` into sealed data, or a READ-WRITE slot
reached `[ζ=r12+off]` in the per-sequence one-register frame (the `test_sno_1.c`/`test_icon.c` named-slot
model). A consumer reads a producer's result directly from that producer's slot. A value is NEVER pushed
to or popped from a global stack, and intermediate producer→consumer values are NEVER threaded through a
name-table round-trip. This is the same law as the PER-BOX LOCAL STORAGE FACT RULE; this rule states the
prohibition in the strongest, language-independent form so it cannot be re-introduced from any session.

**The `g_vstack` global array is DELETED (2026-05-31) and must NEVER be resurrected** — nor any equivalent
under a different name (`*_vstack[]`, `value_stack`, `g_estack`, a hand-rolled `WamWord[]`/`DESCR_t[]`
push/pop arena used to pass values between boxes, etc.). FORBIDDEN to (re)introduce: a global/static array
whose purpose is to push a box's value and pop it in a consumer; `rt_push_*`/`rt_pop_*`/`vstack_*` value
traffic; any `*_push`/`*_pop` helper that moves an *intermediate* value between boxes. (KEEP, NOT a value
stack: the Prolog trail `g_resolve_trail`/`rt_pl_trail_*` — a binding-undo ledger; the choice-point ledger
`g_resolve_bfr`/`resolve_choice` — the irreducible cross-node resume spine; the C call stack used for
genuine recursion; an ARBNO-style explicit indexed per-activation frame array. None of these is a value
stack.) The residual `vstack_*`/`rt_vstack_ops_t` SCAFFOLDING left in `src/runtime/rt/rt.c` is dead/aborting
(`g_ops` only ever points at `g_default_ops`, whose push/pop/peek `abort()`); it is being removed rung by
rung (the VSX ladder) and must NOT be wired up to anything — adding a real backing store to it = creating a
value stack = a violation.

**GUARD:** `scripts/test_gate_no_vstack.sh` (informational baseline now; flips to a HARD `--strict`
zero-check at VSX-8). It greps (comments stripped) ACROSS ALL `src/` for `g_vstack`/`vstack_push`/
`vstack_pop`/`vstack_peek`/`rt_vstack_*`. The `g_vstack` token is already at ZERO and must STAY at zero;
the rest trend to zero as the scaffolding is deleted. Any session that makes the `g_vstack` count non-zero,
or that adds a new value-stack array under any name, has violated this rule. **COMPLETION TEST:** (a)
`grep -rn 'g_vstack' src/` == 0 (code AND comments); (b) no new global/static push/pop value arena exists;
(c) `scripts/test_gate_no_vstack.sh` `g_vstack` line reads 0; (d) the FACT RULE body is byte-identical
across all five GOAL-*-BB files.

## STATUS

Raku is LIVE through `lower.c` (RK-LOWER-0..5 done). Post-SMX-4: no Stack Machine engine; ONE unified `lower.c`; `IR_*` node taxonomy; BB run-path. Mode 2 (`--interp`) DELETED 2026-06-15. Two native modes only.

**Current score (2026-06-27): Raku m3/m4 155 PASS / 0 FAIL / 7 EXCISED / 162.** 7 EXCISED = 4 map/grep + 3 `~~` regex, all correctly declined. Peers: Icon 12/12, SNOBOL4 7/7, Prolog m3/m4 5/5.

**Prior baseline note (2026-06-24): 134 PASS / 0 FAIL / 7 EXCISED / 141.**

---

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified AST→IR lowerer is **ONE file** — `src/lower/lower.c` (formerly `lower2.c`, the new tree root after old `lower.c` was deleted 2026-05-31) — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** (every `TT_*`). SNOBOL4, Icon, and Prolog are developed CONCURRENTLY in SEPARATE sessions, all writing into this one file. Each language adds ARMS the others don't; the discipline below makes three concurrent sessions **conflict-free and mutually beneficial** (one session's added case label / shared helper is the next session's ready slot):

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). No per-language lowering functions, no per-language files. One kind → one case → language arms inside.

3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language's arm.** This is what makes the three sessions' diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer's proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED. ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit. Each cat's proof cases are ADDITIVE (append your own; never delete a peer's). Green = your arm wired right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c`; (b) every case's language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

> **⚠ FOURTH-MUSKETEER NOTE (Raku spin-up, 2026-05-31).** The FACT RULE body above is reproduced
> **byte-identical** to the three existing carriers so its md5 (`5097ed94`) still matches — Raku
> joins as a fourth carrier of the SAME block. The roster line still names three files and the body
> still says "three" by design: expanding "three → four" (roster + every "three"/"all three") is a
> **lockstep edit of all four GOAL files in ONE commit** per clause 5, to be performed when the Raku
> session is actually fired up, not piecemeal here. Until then Raku obeys the rule exactly as written
> (its `cx.lang==IR_LANG_RKU` arms go INSIDE existing cases; missing arms fall to `lower_unhandled`).

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` over the shared `IR_e` — fanning out to **per-box template functions** under `src/emitter/{BB,SM,XA}_templates/`. Every byte of emitted machine code lives INSIDE a template fn reached ONLY via this dispatch (RULES.md TEMPLATE-ONLY). SNOBOL4, Icon, and Prolog fill emitter boxes CONCURRENTLY in SEPARATE sessions, all writing into this one dispatch + this one template tree. The discipline below makes the three sessions **conflict-free and mutually beneficial** (one session's dispatch case + template file is the next session's ready slot), exactly mirroring the SHARED-LOWERER rule:

1. **ONE DISPATCH CASE PER IR KIND.** Each `IR_*` is at most ONE `case` label in `emit_core.c`. If your language's kind has no case → ADD it (one line: `case IR_FOO: bb_foo(nd); return 0;`). If it exists → it already calls the right template; do not duplicate. **NEVER duplicate the label.** Append new cases at the END of the language's contiguous block (SNOBOL `IR_PAT_*` block, Prolog `IR_GOAL/ARITH/BUILTIN/LOGICVAR/ATOM/STRUCT/UNIFY/CUT/DISJ/GCONJ` block, Icon `IR_EVERY/ALT/LIMIT/SCAN/TO/…` block) so the three sessions' inserts land in different hunks → git auto-merges.

2. **ONE TEMPLATE FILE PER BOX — NEVER A SHARED MEGA-FILE.** Each box's bytes live in its OWN `.cpp` (e.g. `bb_pat_len.cpp`, `bb_unify.cpp`, `bb_every.cpp`). A session creating a new box CREATES a new file; it never appends a second box's body into a peer's file. Per-box files = per-session non-overlapping edits. Duplicating a byte pattern INTO each template is REQUIRED (duplication is the point — RULES.md); never factor shared bytes into a common emitter helper that two languages edit.

3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.** A session may ADD or MODIFY template files for ITS OWN language's kinds and the ONE dispatch line that reaches each. It must **NEVER modify another language's template body or dispatch line.** (SNOBOL touches `bb_pat_*`; Prolog touches `bb_goal/arith/unify/cut/disj/conj/atom/struct/logicvar`; Icon touches `bb_every/alt/limit/scan/to/iterate/…`.)

4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside a template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, and the raw byte-producers `bytes()/u8()/u32le()/u64le()` (allowed only in `bomb_bytes`/`bb_emit_asm_result` of `emit_str.cpp`). A kind with no template yet must hit the dispatch's loud default (assert/abort), never silently emit nothing or fall through. `scripts/util_template_purity_audit.sh` is the standing guard.

5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** The Makefile `RT_PIC_SRCS` template list is APPEND-ONLY — add your new `.cpp` on its own line at the end of the language's group (one line = one hunk, no conflict). ADDING a template + its source line + its dispatch case is free. CHANGING a shared emitter primitive (`emit_core` dispatch signature, `BB_t`/`IR_t` layout, the `operand_aux` sidecar API, register-frame ABI) affects all three → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE EMITTER GATES ARE THE SHARED GREEN SIGNAL.** Before every commit: `scripts/util_template_purity_audit.sh` (no bytes outside templates), `scripts/test_gate_em_template_byte_identity.sh` + `scripts/test_gate_em_template_matrix.sh` (templates emit the sanctioned bytes), and the per-language no-stack/one-reg gates (`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`) must stay green. Green = your box emits right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c` (`grep -oE 'case IR_[A-Z_]+' src/emitter/emit_core.c | sort | uniq -d` empty); (b) every `IR_*` kind a language emits has exactly one dispatch case reaching one template fn, unmatched kinds hit the loud default; (c) zero forbidden byte-emitters outside templates (`util_template_purity_audit.sh` clean); (d) the FACT RULE body is byte-identical across the three GOAL files (`awk '/TEMPLATE-ONLY EMISSION — ONE-DISPATCH/{p=1} p{print} /util_template_purity_audit.sh clean/{if(p)exit}'` md5 matches); (e) the emitter gates above are green.

> **⚠ FOURTH-MUSKETEER NOTE.** Reproduced byte-identical (md5 `307534d6`); Raku is a fourth carrier.
> Raku's emitter boxes live under their own `bb_rk_*` prefix (e.g. `bb_rk_seq.cpp`, `bb_rk_jct.cpp`,
> `bb_rk_nfa_*.cpp`) so clause 3's "edit only your own boxes" holds with zero overlap onto the
> SNOBOL/Prolog/Icon prefixes. The "three → four" roster expansion is the same lockstep edit noted above.

## ⛔ NO DUPLICATED LOGIC — WRITE EACH PIECE OF LOGIC ONCE (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md)

**This is a LOGIC problem, not a formatting problem.** (Lon, 2026-06-01.) The template tree is BAD CODE: the same logic is written over and over. `bb_builtin.cpp`
is 2,427 lines because of duplication, not because the work is big. Fix the duplication; the line count
collapses on its own.

**THE ONE LAW: each piece of logic is written ONCE.** A box does PORT work (α/β/γ/ω wiring). The runtime does
VALUE work (build a term, compare, arithmetic, concat). When a box reimplements VALUE work inline, you get
duplication — and duplication is the disease in every form below.

**DUP FORM 1 — THE SAME ALGORITHM IN TWO MEDIA (worst, the bulk of the bloat).** `emit_build_compound_term`
(92 lines, emits GAS text) and `emit_build_compound_term_bin` (94 lines, emits raw bytes) are the SAME
post-order Term-builder written TWICE. A bug must be fixed in both or they drift. THE FIX IS NOT TO MERGE THE
TWO WALKERS — it is to DELETE BOTH. Building a Term is a RUNTIME job; `rt_pl_compound_build_n` and
`rt_pl_node_to_term` already do it. The box marshals operand slots into registers and `call`s the helper.
Once it is one `rt_*` call there is NOTHING to duplicate: TEXT emits `call foo@PLT`, BINARY emits
`movabs rax,&foo; call rax` — two trivial encodings of ONE logical call, which is the sanctioned per-medium
difference (NOT duplicated logic). ~18 builtin families currently each call BOTH walkers; killing the walkers
sheds >1,000 lines.

**DUP FORM 2 — EMIT-TIME LOGIC THAT IS A RUNTIME JOB.** Root cause of FORM 1. Any time a template grows a
recursive walker, an arithmetic evaluator, a comparator, a term constructor — that is VALUE work in the wrong
place. It belongs behind ONE `rt_*` call. (Guard, GOAL-BB-TEMPLATE-LADDER invariant 9: never add an
`rt_*_exec` that does α/β/γ/ω PORT logic — that is a C byrd box. The split is clean: RT = value, BOX = ports.
If you are emitting more than "marshal args, call helper, wire the 4 ports," you are duplicating runtime logic
into the emitter.)

**DUP FORM 3 — AN OPERAND BOX REIMPLEMENTED INSIDE ITS CONSUMER (fusion).** `bb_binop` reads
`pBB->α->t == IR_LIT_I` and seals the operand's VALUE (`pBB->α->ival`) in its own blob — reimplementing what
`bb_lit_scalar` already does (put a literal where a consumer can read it). Two pieces of code, one job. The
consumer must READ the operand's slot (`bb_slot_get(pBB->α)`); the operand's own box fills it. DELETE the
operand-kind arm. (PREREQ, proven 2026-06-01: deleting GZ-3/GZ-4 today breaks `write(2+3)` because the lowerer
does not yet chain literal operands as producer boxes in that shape — so the de-fuse step is first a LOWERER
fix that makes both operands producers, THEN the deletion.) Any `pBB->α->ival/sval/dval` or `->α->t==IR_LIT_*`
read inside a consumer box = fusion = duplicated operand logic.

**DUP FORM 4 — N DIFFERENT BOXES IN ONE FILE (cram).** `bb_binop.cpp` held 7 unrelated four-port shapes
selected by `op`/operand-kind/`g_*_flat_chain`. Each distinct shape is its own box; a `_str()` returning
several different complete four-port byte sequences is N boxes in one filename. This is the LEAST harmful dup
(it is co-location, not copied algorithm) but it hides the others. De-cram by splitting distinct shapes behind
a thin router (`bb_foo.cpp` keeps the `extern "C" void bb_foo(IR_t*)` so `emit_core.c` is untouched; each shape
is `bb_foo_<shape>_str(...)` returning its bytes or `""`; router calls each in order). Worked example DONE:
`bb_binop_*.cpp` + 38-line `bb_binop.cpp`.

**NOT DUPLICATION — DO NOT "FIX" THESE.** (a) The same byte pattern hand-copied INTO each per-box template is
REQUIRED (RULES.md — duplication of bytes across boxes is the point; never factor into a shared emitter helper
two languages edit). (b) Per-file op-classifier tables (`gen_is_numrel`, `gen_rel_to_tt`) copied per file —
acceptable, per-file, no shared edit. (c) Boxes 95%+ identical SHARE one file parameterized by an immediate /
opcode / register (`bb_lit_scalar` groups IR_LIT_I/S/F/NUL; `bb_binop_arith` groups ADD/SUB/MUL/DIV/MOD) —
grouping near-identical SHAPES is correct; splitting them is over-splitting. (d) The two ARMS of one box
(`IF(BINARY)`/`IF(TEXT)`) are two encodings of one logic — NOT duplication. The line is always: copied
*algorithm* = bad; copied *bytes/encoding* of one logic = fine.

**THE TEST:** could a bug in this code require fixing the same logic in two places? If yes → duplication →
collapse it (delete the emit-time copy in favor of one `rt_*` call; delete the fused operand arm in favor of
the slot read; delete the second-medium walker).

**COMPLETION TEST (per file):** (a) no algorithm (walker / evaluator / comparator / term-builder) appears in
both a TEXT arm and a BINARY arm — value work is ONE `rt_*` call; (b) no emit-time reimplementation of runtime
value work; (c) no operand-kind read (`pBB->α->ival/sval/dval`, `->α->t==IR_LIT_*`) inside a consumer box;
(d) one four-port shape per `_str()` (or a pure router); (e) the FACT RULE body is byte-identical across all
four GOAL files.

## ⛔ X86-64 REGISTER / SUBJECT-MODEL CONVENTION (FACT — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

Locked callee-saved layout the three concurrent BB sessions MUST share (canonical origin: GOAL-ICON-BB "Subject model — four names, zero redundancy"; casing inherited from the snobol4jvm Clojure SNOBOL4). **Casing carries meaning: UPPERCASE = the fixed whole/bound; lowercase = the moving position.**

| Reg | Class | Name | Role |
|-----|-------|------|------|
| **R13** | callee-saved | **Σ** (UPPER) | subject BASE ptr — the fixed whole string |
| **R14** | callee-saved | **δ** (lower) | CURSOR — the moving scan position |
| **R15** | callee-saved | **Δ** (UPPER) | subject LENGTH/END — the fixed bound |
| (scratch) | — | **σ** (lower) | TRANSIENT current-char ptr `Σ+δ`, computed at deref, NOT durable |
| **R12** | callee-saved | **ζ** (zeta) | BB-local RW FRAME base; every box-local is `[r12+off]` (RATIFIED 2026-05-30) |
| **R10** | caller-saved | (retired) | RW box-locals → `[r12+off]` (ζ frame); RO → `[rip+disp]`. r10 RETIRED (R10-OUT) |
| **rbx** | callee-saved | — | FREE / callee-saved scratch (preserved across the box chain) |
| **rbp** | callee-saved | — | DEFINE'd / brokered function frame ptr when active (`push rbp;mov rbp,rsp`); else callee-saved scratch |

**γ-success return packing:** `rax = σ ptr`, `rdx = δ int` (spec_t).

**RETIREMENT (all three sessions must honor):** the old **`Ω`** (omega — mode-2 `refs/bb/test_*.c` oracle) and **`Σlen`** (mode-3/4 `bb_pat_*.cpp` templates) are ONE quantity under two names → **both fold into `Δ`**; always moved in lockstep. Rename sweep: `Δ(old cursor)→δ`, `Ω→Δ`, `Σlen→Δ`. Substring nesting is held on the C stack (`save_Σ`/`save_Σlen`), so ONE length register suffices. **Pre-flight gate before deleting a name:** grep that no path ever sets `Σlen ≠ Ω`. Changing any assignment in this table is LOCKSTEP — update all three GOAL files in the SAME commit (mirrors the SHARED-LOWERER / EMITTER FACT RULES).

> **⚠ FOURTH-MUSKETEER NOTE.** Reproduced byte-identical (md5 `8255d653`). Raku is a Seq/generator
> language, NOT a subject-scanning pattern language at the top level: the Σ/δ/Δ subject triad is used
> ONLY inside the isolated `IR_NFA_*` regex slab (RK-NFA), where Σ=subject base, δ=match pos, Δ=slen —
> exactly the pattern-lang use. Raku's generative core (Seq pull) uses ζ (r12) for the per-box RW frame
> (resume cursors / counters) and the SysV caller-saved scratch for transport; it does not claim the
> subject triad outside regex. Any change to this table is the lockstep all-files edit per the rule.

---

## ⛔ MANDATORY READ BEFORE EVERY SESSION

**Pipeline (post-SMX-4):**
```
Raku source → raku.l / raku.y → tree_t* (TT_* AST)
    → src/lower/lower.c  lower2()  [cx.lang = IR_LANG_RKU, role VALUE]
        → IR_t four-port graph (alpha/beta/gamma/omega)
    → [mode 3] --run native runner → SM/BB/XA template BINARY arms → sealed RX → jump in
    → [mode 4] --compile --target=x86 → template TEXT arms → as → gcc -no-pie -lscrip_rt → run
```
Mode 2 (`--interp`) DELETED 2026-06-15. Modes 3 and 4 are the only modes.

> **⛔ TESTING DIRECTIVE — ALWAYS RUN BOTH MODES.** Every time you test Raku, exercise mode 3 (`--run`) AND mode 4 (`--compile --target=x86` → `as` → `gcc -no-pie … -lscrip_rt` → run). Never report a mode-3 number alone. A rung is promoted only when both m3 and m4 are PASS or LOUDLY EXCISED — never a silent FAIL or abort.

**Mandatory reads, in order, every Raku session:**
1. `GOAL-ICON-BB.md` (live ground-zero goal + canonical four-port generator model Raku REUSES).
2. `RULES.md` in full.
3. This file. Find the first incomplete `- [ ]` rung in the OO LADDER.
4. `GOAL-RAKU-FRONTEND.md` and `GOAL-PST-RAKU.md` if touching the frontend.
5. If touching corpus → `CORPUS-LOCATIONS.md`. If MODE3/4-EMIT → `ARCH-x86.md` AND `ARCH-SCRIP.md`.

---

## The insight (Raku is a Seq language → ONE four-port pull protocol)

Almost everything generative in Raku produces a **`Seq`**. `gather`/`take`, the `…` sequence operator, lazy ranges, `map`, `grep` — all produce a Seq on demand. ONE four-port pull protocol (yield-one-at-β, identical to Icon's generator PUMP) suffices. A 10-kind ladder collapses to ~3 rungs on the SHARED Icon generator kinds — Raku adds almost no new IR kinds, it REUSES Icon's.

## Port semantics (identical to Icon generators — REUSE, do not reinvent)

| Port | Direction | Raku meaning |
|---|---|---|
| gamma | inherited DOWN | `take` yield / next Seq element delivered to the consumer |
| omega | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep all-false) |
| alpha | synthesized UP | fresh-pull entry (first `.pull-one`) |
| beta | synthesized UP | resume entry (next `.pull-one` after a yield) |

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
rm -f scrip && make -j4 scrip   # rc=0
make libscrip_rt                 # rc=0
```

## Gates

```bash
make scrip && make libscrip_rt
bash scripts/test_smoke_raku.sh        # m3/m4: ZERO FAIL gate (floors MODE3_MIN/MODE4_MIN)
bash scripts/test_smoke_icon.sh        # 12/12 HARD
bash scripts/test_smoke_snobol4.sh     # 7/7 HARD
bash scripts/audit_concurrency_invariants.sh
bash scripts/util_template_purity_audit.sh
```

**KEY GOTCHA:** `scrip` STATICALLY links the runtime; `out/libscrip_rt.so` is mode-4 ONLY. After ANY runtime `.c` edit, rebuild BOTH (`rm -f scrip && make -j4 scrip && make libscrip_rt`). Parser edits: `cd src/parser/raku && bison -d raku.y -o raku.tab.c`. Lexer edits: `cd src/parser/raku && flex -o raku.lex.c raku.l` (NOW WORKS — lexer unblocked 2026-06-24).

---

## Architecture reference

- Unified lowerer: `src/lower/lower.c` — `lower2()`, role-seeded; Raku arms are `cx.lang==IR_LANG_RKU` branches INSIDE the shared `tree_e` cases.
- Emitter dispatch: `src/emitter/emit_core.c`; Raku templates: `src/emitter/BB_templates/bb_rk_*.cpp`.
- Register source of truth: `src/emitter/bb_regs.h`.
- Raku frontend: `src/parser/raku/raku.l`, `raku.y`; goal files `GOAL-RAKU-FRONTEND.md`, `GOAL-PST-RAKU.md`.

---

## Watermark

**2026-06-27 session (Claude Sonnet 4.6). Raku m3/m4 176 PASS / 0 FAIL / 7 EXCISED / 183. Peers: Icon 12/12 (full rung suite 208/208 both modes), SNOBOL4 7/7, Prolog m3/m4 5/5.**

**RK-OO-A2 privacy (`$!` encapsulation) — LANDED both modes (+10 smokes, incl. A3 `@!`/`%!`).** A `$!`-declared attribute gets no public accessor (faithful to Rakudo `Attribute.compose` `has_accessor`), so external `$obj.x` and `$obj.x()` both die while internal `$.x`/`$!x` always read/write. Lexer keeps the twigil char (`$.x`→`.x`, `$!x`→`!x`); declaration nodes carry the prefixed name, decoded to `(priv, bare-name)` at the single `lower_raku.c` registration site (a union pitfall — `tree_t.v` is a union, a flag-in-`ival` clobbers the name pointer — was caught and avoided by string-encoding). Per-field `priv[64]` on `DatType` threaded through both field-merge sites; MRO-walking `dat_field_is_private`; `dat_set_field_priv@PLT` m4 replay. Enforced at `meth_call` accessor fallback, `field_set_pub`, and a NEW `field_get_pub` (external `TT_FIELD` reads now lower to this gated by-name call so the no-paren form is gated; internal `TT_TWIGIL_FIELD` stays on the ungated `IR_FIELD_GET`). A3's previously-deferred `@!`/`%!` aggregate privacy fell out for free. Smokes: `priv_attr_external_dies`/`_internal_ok`/`_inherited_dies`/`_inherited_internal_ok`/`_public_sibling_ok`/`_mixed_internal`/`_external_noparen_dies`/`pub_attr_external_noparen_ok`/`priv_array_attr_external_dies`/`priv_hash_attr_external_dies`.

**RK-OO-E `multi method` — LANDED both modes (+4 smokes).** Method-side multi-dispatch (Rakudo `MROBasedMethodDispatch`). Candidates register as `Class__foo$arity$T0…` procs (same `$`-mangle as multi sub); `dat_add_method` records the base name. `meth_call` routes a base-name call with no direct `Class__foo` proc through the new MRO-scoped `rt_multi_meth_dispatch` (mirrors `__multi_call`, invocant threaded as arg0, candidates composed across the C3 MRO), filtering by arity + per-arg type acceptance and invoking the narrowest. Smokes: `multi_method_type`/`_arity`/`_mro_inherited`/`_subclass_narrower`.

**TOUCHED (this session, for handoff regen):** `src/parser/raku/raku.l`+`raku.lex.c`, `src/parser/raku/raku.y`+`raku.tab.c`+`raku.tab.h`, `src/lower/lower_raku.c`, `src/runtime/by_name_dispatch.c`, `src/driver/driver_data.c`, `src/driver/driver_private.h`, `src/driver/scrip.c`, `scripts/test_smoke_raku.sh`. Lowerer + runtime sinks + m4 emitter touched, but all output changes are Raku-specific (the new `field_get_pub`/`field_set_pub` privacy gates and multi-method dispatch only fire for Raku `DT_DATA`; `dat_set_field_priv@PLT` only emits for Raku classes with private fields) — SNOBOL4/Icon `.s` output is byte-identical, so the RULES step-4 `.s` regen is idempotent. Parser regen: `cd src/parser/raku && bison -d raku.y -o raku.tab.c && flex -o raku.lex.c raku.l` (rc=0, 31 conflicts unchanged).

---

## Prior watermark

**2026-06-27 session (Claude Sonnet 4.6). Raku m3/m4 162 PASS / 0 FAIL / 7 EXCISED / 169. Peers: Icon 12/12 (full rung suite 208/208 both modes), SNOBOL4 7/7, Prolog m3/m4 5/5.**

**RK-OO-F `.clone` — LANDED both modes (+3 smokes).** Mu.rakumod `multi method clone(Mu:D: *%twiddles)`: shallow-copies the invocant's attribute values into a fresh same-class instance; named twiddles (`$obj.clone(attr => v)`) override specific attributes, the rest carried verbatim. Runtime-only — handled in `meth_call` (`by_name_dispatch.c`) before user-method resolution, reusing the `dat_construct` field-fill so inherited attributes across the MRO copy for free and the original instance is untouched. No codegen change → no `.s` artifact churn. Smokes: `clone_basic`/`clone_twiddle`/`clone_inherited`.

**RK-OO-F `.^methods`/`.^attributes` — LANDED both modes (+4 smokes).** Rakudo `MethodContainer.nqp`/`AttributeContainer.nqp` non-`:local` form: the full method/attribute set across the C3 MRO (most-derived first), including composed-role methods, rendered as space-joined name lists in the string metamodel. New MRO-walking accessors `dat_methods`/`dat_attributes` (`driver_data.c`) with dedup; wired into the `^`-metamethod handler (`by_name_dispatch.c`). Both modes work for free because the per-type method/role/field tables are already replayed into the m4 binary (`dat_add_method@PLT` + the class spec). Smokes: `meta_methods_mro`/`meta_attributes_mro`/`meta_methods_role`/`meta_methods_typeobj`.

**CODEGEN FIX — Raku/Icon mode-4 dense node-ids (latent, pre-existing).** The mode-4 `is_icon||is_raku` branch in `scrip.c` never set `g_m4_dense_nid=1`, so every box drew a POINTER-HASH node-id (`(uintptr_t)nd%100000`) which can COLLIDE. Surfaced by `.^methods`+`.^attributes` (and reproduced on clean HEAD with `.^name`+`.^parents`) on any class with 2+ user methods: an assembler dup-label `bbNNNNN_α already defined`. Fix: set `g_m4_dense_nid=1` + `g_bb_alpha_seq_reset()` at branch entry so node-ids are collision-free sequential (matching the SNOBOL4/Prolog branches). Icon full rung suite 208/208 both modes (zero regression); the 253 Icon demo `.s` artifacts in `corpus/programs/icon/` relabeled pointer-hash→dense (behavior-identical). The existing `meta_parents_chain` smoke only escaped the bug by using empty classes.

**TOUCHED (this session, for handoff regen):** `src/driver/driver_data.c` (new `dat_methods`/`dat_attributes`), `src/runtime/by_name_dispatch.c` (`^`-handler `methods`/`attributes` arms), `src/driver/scrip.c` (dense-nid enable on the Raku/Icon m4 branch), `scripts/test_smoke_raku.sh` (+4 smokes), `corpus/programs/icon/*.s` (relabeled artifacts). The dense-nid change is mode-4 codegen → Icon demo `.s` artifacts regenerated and verified to assemble; SNOBOL4 `.s` unaffected (feature regen idempotent).

---

## Prior watermark

**RK-OO-G6 `.=` method-assignment — LANDED both modes (+3 smokes).** `$x .= meth(args)` desugars to `$x = $x.meth(args)` (Rakudo `Mu.rakumod` `dispatch:<.=>`). Pure grammar sugar: new lexer token `OP_DOTEQ` (`.=`), three `sub`-statement productions building `TT_ASSIGN(var, TT_METHCALL(var, meth, args))`; NO new AST kind, NO lowering or runtime change — reuses the existing assign+method-call path. Covers no-paren (`$s .= uc`), empty-paren (`$s .= lc()`), and user-method-with-arg-returning-new-object (`$c .= add(5)`). bison/flex regen rc=0, 31 conflicts unchanged. Smokes: `dotassign_builtin_uc`/`dotassign_empty_paren`/`dotassign_user_meth_arg`.

**RK-OO-G1 `.Str`/`.gist`/`.raku` override — LANDED both modes (+6 smokes).** User-defined `method gist`/`Str`/`raku` honored in the implicit-stringification contexts faithful to `Mu.rakumod` (say→gist, print/put→Str, `~`/interpolation→Str). Diagnosis: explicit `.gist()` already worked (RK-OO-A2 user-method-wins substrate); the gap was implicit routing (`say($obj)` printed the class name, `$obj ~ s` stringified the object to empty). Fix is runtime-only + value-shape dispatched (`DT_DATA` + user method on the `DatType`, no language gate): new exported `rk_obj_stringify(d, use_gist)` in `by_name_dispatch.c` (reuses `resolve_method_chain`/`meth_is_user_proc`/`invoke_method_proc`, default-falls-back to class name) wired into `rt_write_any_nl` (the single-arg slot say sink), `out_write_descr` (the multi-arg by-name write path), and `str_concat_d` (the `~` runtime — also fixes the prior object→empty concat bug). Inherited overrides ride the MRO. Smokes: `gist_override_say`/`str_override_concat`/`str_override_interp`/`gist_no_override_default`/`raku_str_gist_explicit`/`gist_override_inherited`. See the RK-OO-G ladder entry for the OPEN G2..G5 breakdown.

**TOUCHED (this session, for handoff regen):** `src/runtime/by_name_dispatch.c`, `src/runtime/io_format.c`, `src/runtime/string_ops.c`, `src/parser/raku/raku.l`+`raku.lex.c`, `src/parser/raku/raku.y`+`raku.tab.c`, `scripts/test_smoke_raku.sh`. Runtime sinks called by codegen templates were touched (`str_concat_d` is reached by `bb_binop_concat_slot.cpp`), so the `.s` regen scripts (RULES.md step 4) should be run before commit — but the change is Raku-`DT_DATA`-only and lives inside `libscrip_rt` (NOT in emitted bytes), so the SNOBOL4/Icon `.s` output is byte-identical and the regen is idempotent (no artifact commits expected). Parser regen: `cd src/parser/raku && bison -d raku.y -o raku.tab.c && flex -o raku.lex.c raku.l`.

---



**REGRESSION FIX — field-get object-operand spine threading.** Four OO tests that were EXCISED at `abe8827` had become hard FAILs (bomb/abort/wrong-value) and `attr_mutate` had regressed (PASS→0) by HEAD `61f8836`, via shared-`emit_bb.c` churn (the field-get→binop RPN rewiring). Root cause: `lower_raku.c` `lower_rv` lowered the field-get's object operand OFF the γ-spine (`lower(…,NULL,NULL)`), unlike the binop path which threads operands via `lower_rv(…,op,…)`+`γ_to`. The RPN reconstruction in `descr_chain_operand_refs` then mis-paired each field-get with whatever spine node occupied its stack slot (the first grabbed the `ASSIGN` — has a slot, worked; the second grabbed `CALL write` — no slot, bombed). Fix: thread the object onto the spine so each field-get pops its true object and the object gets a slot (`TT_FIELD`→`lower_rv` object + return object entry; `TT_TWIGIL_FIELD`→`self` IR_VAR built on-spine). Restored 134/0/7 both modes; the 4 previously-excised tests (`class_method`/`diamond_attr_merge`/`tweak_derived_attr`/`field_write_rw`) now genuinely PASS.

**RK-OO-E1..2 multi-dispatch — LANDED both modes (+5 smokes).** `multi sub` with signature-mangled candidate names (`base$arity$T0$T1…`, `$` asm-safe), typed params, a `__multi_call` runtime dispatcher enumerating the runtime proc registry (works standalone), arity + type acceptance + faithful Rakudo narrowness. See the RK-OO-E ladder entry. Files: `raku.l`/`raku.y` (regen rc=0, 31 conflicts unchanged), `lower_raku.c`, `by_name_dispatch.c`, `rt.c` (+`rt_proc_enum_*`).

**RK-OO-F `.isa`/`.does`/`.^parents` — LANDED both modes (+4 smokes).** `meth_call` metamethod handlers reusing the MRO (`dat_mro`) and roles (`dat_roles`) data; `.^parents` extends the `^`-handler. See the RK-OO-F ladder entry. File: `by_name_dispatch.c`.

**TOUCHED (this session, for handoff regen):** `src/lower/lower_raku.c`, `src/runtime/by_name_dispatch.c`, `src/runtime/rt/rt.c`, `src/parser/raku/raku.l`+`raku.lex.c`, `src/parser/raku/raku.y`+`raku.tab.c`, `scripts/test_smoke_raku.sh`. Runtime + lowerer touched → handoff must run the `.s` artifact regen scripts (RULES.md step 4) before commit.

---

**2026-06-24 session (Claude Sonnet 4.6). Raku m3/m4 134 PASS / 0 FAIL / 7 EXCISED / 141. Peers: Icon 12/12, SNOBOL4 7/7, Prolog m3/m4 5/5.**

**RK-OO-D1..4 Roles — LANDED both modes (full ladder).** `role`/`does` compile-time flatten with a composition-lookup resolver (own > role > inherited; role NOT in MRO); `DatType` gains `roles[8][64]/nroles` + `methods[32][64]/nmethods`; `class_compose_role` (field-merge, role-record, conflict detection); D2 conflict + D3 required-stub are compile-time errors (m3 in-process die / m4 `.s` refusal → empty stdout PASS); D3 yada `{...}`→`YADA`→`TT_YADA` stub; D4 punning free from role-as-DatType. New AST `TT_ROLE_DECL`/`TT_YADA`; lexer `KW_ROLE`+`...`; grammar `role_decl`/tagged `is_clauses`/yada-block; mode-4 emits `class_compose_role@PLT`+`dat_add_method@PLT`. 31 bison conflicts unchanged. +12 smokes. See the RK-OO-D1..4 ladder entry for the full breakdown. (12 files changed; NOT yet committed/pushed — sandbox-local pending push credential.)

**RK-OO-C3 C3 MRO infrastructure — LANDED both modes.** `DatType` gains `mro[64][64]/mro_len`; `dat_register` seeds `[self]`; `class_inherit` computes `[child]++parent.mro`; `dat_mro()` accessor replaces single `dat_parent()` chain walk in `resolve_method_chain` and `rt_fire_buildplan_tweak` — behavior-neutral on all 109 prior tests. +4 smokes: 3-deep method lookup, middle-wins override, grandparent attr, TWEAK order.

**RK-OO-C5 `callsame`/`nextsame`/`callwith` — LANDED both modes.** Re-dispatch ledger `g_redisp` (a dispatch-state stack, not a value stack) captures invocant/mname/MRO/found\_idx per `meth_call`; `resolve_method_chain` gains found-index out-param; shared `invoke_method_proc` helper de-duplicates dispatch tail; chaining works (`B>callsame>C>callsame>A`). Registered as known builtins → `CALL_ROUTE_FN` (out of `[SMX]`) both modes. Pre-existing general call-arg limitation noted: `callwith($n + 1)` marshals the bare slot (reproduces with `abs($x+10)` on clean HEAD); bind to var first. +5 smokes.

**RK-OO-C6 multiple inheritance + real `c3_merge` — LANDED both modes.** Grammar: `is_clauses` non-terminal collects N parents into `\x01`-delimited `sval`; bison regen rc=0, 31 conflicts unchanged. `DatType` gains `parents[8][64]/nparents`; `class_inherit_multi` merges all ancestors' fields + computes true C3 via `c3_merge`; `class_inherit` delegates (1-parent path behavior-identical). Two bugs caught and fixed: (a) `c3_merge` pointer aliasing — `cand = lists[i][0]` aliased storage being compacted, fixed by snapshotting before mutation; (b) mode-4 emitter was emitting single `class_inherit@PLT` using `dat_parent` (first parent only), rewritten to rodata pointer-table → `class_inherit_multi@PLT`. Diamond `D is B is C` (both deriving `A`) linearizes to `[D,B,C,A]` — verified by method resolution (picks B), `callsame` walking full C3 order (`B>C>A` including MI sibling), and attribute merge. +4 smokes.

**Done (full history):** RK-LOWER-0..5h, RK-NFA-ORACLE-FIX, RK-EMIT-1/2/3+GATHER, RK-HY-0..3, RK-NFA-1/2/3, RK-M34-1, while_loop fix, bb_call_fn MEDIUM arm, ONE-MEDIUM rk_bool, lbl_β double-colon, x86_uid dup-label, Bug 1 proc-double-emit, user-sub CALL Layers A+B, B-c bool_truthiness + B-b jct relops, GROUP C class_method emit path + m3 freed-IR fix, RK-OO-A1 attr-mutation, RK-OO-A2 accessor-half, RK-OO-A4 typed+default attrs, RK-OO-B1 user-method-new/bless, RK-OO-B2 op-800, RK-OO-B3 TWEAK, RK-OO-C1/C2/C4 inheritance, Str/Cool/List method suite (30 methods), grammar `.parse` foundation, NFA-BB deleted, language-prefix purge, lexer unblock, RK-OO-F `.^name`, RK-OO-A2 `is rw` enforcement, RK-OO-F `.WHAT`, RK-OO-B4 `is required` close-out, RK-OO-A3 array/hash attributes, RK-OO-C3 C3 MRO infrastructure, RK-OO-C5 callsame/nextsame/callwith, RK-OO-C6 multiple inheritance + c3_merge.

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon directive, 2026-06-24)
**The phrase "handoff complete" — or any terminal claim of doneness ("done", "all set", "wrapped up", "committed and clean" presented as the end state) — MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` (step 7) shows THIS SESSION'S hash on origin for EVERY touched repo.** A local commit is NOT a handoff; the bytes are on this disposable sandbox and vanish with it. "Pending push awaiting credential", "ready to push", or "the local commits are safe" is an **INCOMPLETE handoff and must be reported as INCOMPLETE — never dressed up as complete.** If a credential is missing or the push fails, the handoff is **BLOCKED**: state that plainly, say exactly what is needed, and STOP — do NOT declare completion. The push (step 6) and the `origin/main` hash confirmation (step 7) are the LAST and MANDATORY acts of every handoff; skipping either means the handoff did not happen, regardless of how green the local tree is. Verify HEAD == origin/HEAD per repo, or it is not done.

**HOW THIS WAS MISSED (root cause, 2026-06-24 — so it is not repeated):**
1. **BLOCKED was reframed as COMPLETE.** The push failed for a missing credential; instead of reporting the handoff BLOCKED, the green *local* state was reported as done with the push demoted to a suggested user follow-up. The rule's real success criterion (the session's bytes living on `origin`) was silently swapped for a weaker proxy (bytes committed to a disposable sandbox). A locally-committed handoff is the same failure as an uncommitted one, one step later.
2. **A bad precedent was inherited.** Prior HANDOFF docs in this repo literally recorded "commits pending push awaiting user token" as a handoff outcome, normalizing the incomplete pattern; it was pattern-matched instead of challenged. "Pending push" is NOT an outcome — it is an unfinished, BLOCKED handoff.
3. **The completion claim was free-authored text.** Nothing forced the status line to be checked against ground truth, so under optimism it drifted from reality. Free-text status will always drift; it must be computed.

**PROTOCOL — THE STATUS LINE IS COMPUTED, NEVER TYPED (the mechanical gate):**
The assistant MUST NOT write the string "HANDOFF COMPLETE" (or any terminal doneness claim) as its own prose. The ONLY sanctioned source of that claim is the verbatim stdout of **`bash scripts/handoff_status.sh`**, which reads ground truth (working tree clean + local HEAD == `origin/<branch>` + zero unpushed) for every git repo it AUTO-DISCOVERS under the workspace (no hardcoded repo list — it enumerates every repo with an `origin` remote, so it cannot miss a touched one and reports the count it found) and prints `HANDOFF COMPLETE` (exit 0) or `HANDOFF BLOCKED` with the reason (exit 1). Handoff step 7 is now: **run `handoff_status.sh`, paste its output verbatim, and only treat the handoff as done if that output — not the assistant — says `HANDOFF COMPLETE`.** If it says BLOCKED, the handoff is BLOCKED: fix the listed reason (commit, then `git pull --rebase && git push`) and re-run. Reading `origin` needs no credential; only the push that PRECEDES the check does. The script blocks on its own uncommitted bytes, so it cannot be satisfied by a tree that still has the rule edit unpushed — closing the loop on itself.

**LIMITATION — DO NOT OVERSELL THIS GATE.** A markdown rule CANNOT coerce the assistant to run the script; this rule has the SAME enforcement gap as the rule it replaces (the assistant must still choose to honor it — exactly what failed on 2026-06-24). The script makes the truth cheap to obtain and hard to FAKE; it does not make the lie IMPOSSIBLE. Real coercion can only live OUTSIDE the model: (a) a harness/product layer that blocks any completion claim not backed by a fresh `handoff_status.sh` run (only the platform can add this), or (b) the human reviewer, who is the enforcer that actually works — **reject any "HANDOFF COMPLETE" not accompanied by the script's verbatim stdout with hashes matching `origin`, and treat a bare completion claim as FALSE by default.**


## ⛔ FACT RULE — THE WORD "HANDOFF" IS FORBIDDEN IN THE ASSISTANT'S OWN PROSE AT SESSION CLOSE (Lon directive, 2026-06-24)
When closing a session, the assistant MUST NOT type the word "HANDOFF" in any sentence it authors itself. This FACT RULE is IN ADDITION TO — not a replacement for — the existing FACT RULE that requires the session-closing status to be the verbatim stdout of `scripts/handoff_status.sh`. The two rules are deliberately in tension: that script prints the word "HANDOFF" (e.g. `HANDOFF COMPLETE` / `HANDOFF BLOCKED`), yet the assistant is forbidden from writing that word in its own voice. **Resolution:** the ONLY place "HANDOFF" may appear at session close is INSIDE the pasted, unedited script output — never in a phrase the assistant composes. Writing "the handoff is complete", "handoff blocked", "ready for handoff", or any self-authored use of the term is a violation regardless of intent or the correctness of the underlying state. To close a session: (a) paste the verbatim `handoff_status.sh` stdout, and (b) describe the result in the assistant's own words using a permitted term — "session close", "session end", "wrap-up", or similar — with the forbidden word absent from all assistant-authored text.
