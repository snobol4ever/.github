# GOAL-RAKU-BB.md — Raku goal-directed onto the shared four-port IR (the fourth musketeer)

## ★ CURRENT PRIORITY — READ FIRST, HANDLE FIRST (Lon, 2026-06-15): RAKU OOP IS THE LEAD

**OOP is Raku's signature contribution to SCRIP (the other five languages are non-OO) and is now THE priority
for Raku — ahead of RK-GRAM-3 and RK-EMIT-MAP/GREP.** Work the OO LADDER below top-to-bottom; take the first
incomplete (`- [ ]`) rung. The grammar/regex and map/grep rungs (further down this file) are PARKED until the OO
ladder advances on Lon's word.

### OO LADDER (the Raku-distinctive paradigm — milestones A–G; anchored to Rakudo `Metamodel/{BUILDPLAN,C3MRO,MROBasedMethodDispatch,RoleToClassApplier}.nqp`, `Mu.rakumod`, `Attribute.rakumod`). Architecture note: OO is overwhelmingly RUNTIME (`obj_new`/`meth_call`/`dat_field_*` + the `DatType`/`DATINST_t` model). Most rungs land via runtime by-name dispatch (the Str-suite pattern); parser+lower changes only where new *syntax* must be recognized. **LEXER CONSTRAINT (verified 2026-06-15): flex 2.6.4 CANNOT regenerate `raku.lex.c` (fails on the pristine file at line 132 — committed lexer built with a different flex). So NO new lexer keywords — recognize new keywords at the PARSER level as `IDENT` checked in the rule action (how `is` is done). bison regen works fine.**
- [x] **RK-OO-A1 — attribute mutation — LANDED both modes (2026-06-15, `952d528`).** Objects were write-once; now attributes mutate. Parser: twigil-field as lvalue (`$.x =`/`$!x =`) + void method-call statements (`$obj.m(args);`). Lower: `TT_FIELD`/`TT_TWIGIL_FIELD` LHS in `lower_rv` TT_ASSIGN → `IR_CALL "field_set"` with `[obj,name,val]` producer chain (was a silent `IR_SUCCEED` no-op). Runtime: `field_set` known-builtin + handler writing through `data_field_ptr` (write twin of `dat_field_get`). Also fixed pre-existing `raku.y`/`raku.tab.h` include drift (`../../ast/ast.h`→`ast.h`) so `bison -d` regenerates faithfully. Smokes: `attr_mutate`, `field_write_external`.
- [~] **RK-OO-A2 — public-attribute AUTO-ACCESSOR — LANDED both modes (2026-06-15, this session). Privacy (`$!`) + `is rw` are LEXER-BLOCKED → deferred (see below).** A public attribute now answers `.x()` (with parens), not just `.x`. Runtime-only fix in `by_name_dispatch.c`'s `meth_call`: after `resolve_method_chain`, if the method takes no args and is NOT a real user proc (`meth_is_user_proc`, dual native-registry+proc_table check mirroring the chain walk), and the receiver has a field of that name (`data_field_ptr`), return the field value — exactly Rakudo `Attribute.compose`'s `has_accessor` codegen (`unless ...method_table` guard → user method of the same name WINS; verified `accessor_method_wins`→105). Resolves the `$p.x()`→`[GZ-10] 'Point__x' has no stackless slab` abort. Accessor resolves through inheritance too (`accessor_inherited`). No parser/lexer/template/IR change. Smokes: `accessor_paren`/`accessor_method_wins`/`accessor_inherited`. **DEFERRED (lexer-blocked):** the `$.`(public) vs `$!`(private) twigil distinction is ERASED at lex time — `raku.l:117-118` both do `strdup(yytext+2)` → identical `VAR_TWIGIL` bare-name token, and the registration spec (`Name(f1,f2)`) carries no per-field privacy bit. Enforcing privacy (`$!x` should be externally inaccessible — today `$s.hidden` wrongly reads a private field) and `is rw` (writable-container accessor) BOTH require carrying a public/private/rw flag from the declaration, which needs a lexer change to preserve the twigil — and flex 2.6.4 cannot regenerate `raku.lex.c` (LEXER CONSTRAINT above). Unblock path: a flex fix (or a hand-patch of the committed `raku.lex.c` to emit a twigil-tagged token) → then thread the flag into the spec and gate it in `meth_call`/`dat_field_get`.
- [!] **RK-OO-A3 — `@.`/`%.` array & hash attributes — LEXER-BLOCKED (probed 2026-06-15).** No `@.`/`%.` lexer rules exist; `has @.items` fails at lex (`unexpected char '@'`). Adding the rules needs `raku.lex.c` regen, which flex 2.6.4 cannot do (LEXER CONSTRAINT). Blocked until the lexer is unblocked (flex fix or hand-patch `raku.lex.c`).
- [~] **RK-OO-A4 — typed + constant-default attributes — LANDED both modes (2026-06-15, this session). Closure/expression defaults deferred.** `has Int $.x` (typed; type currently IGNORED — parsed and discarded, no constraint enforced) and `has $.x = 42` (constant default) now parse and work. Default = the constant value used at construction iff the named arg is absent (Rakudo BUILDPLAN op 400, the constant-`build` case). Parser (bison-regen only, NO lexer change — `Int` arrives as `IDENT`): 6 new `class_body_list` rules — typed-no-default (`KW_HAS IDENT VAR_TWIGIL/VAR_SCALAR ';'`) lowers to a plain `TT_VAR` field (type dropped); any-default case lowers to a new `TT_HAS_DECL` node (`v.sval`=field name, `c[0]`=default expr). Runtime/driver (`driver_data.c`): `DatType` gains parallel `DESCR_t defaults[64]` + `char has_default[64]`; new `dat_set_field_default_{i,s,r}` setters; `dat_construct` applies the stored default when the incoming field arg is absent (`DT_SNUL`) — the SINGLE chokepoint, so both `obj_new` and `bless` get defaults free; `class_inherit` rewritten to carry the default/has_default metadata alongside fields (parent defaults inherit). Lower (`lower_raku.c`): after `record_register`, `rk_register_classes` calls the setters for each `TT_HAS_DECL` whose default is an `ILIT`/`QLIT`/`FLIT` literal. m4 (`scrip.c` `proc_startup`): emits a `dat_set_field_default_{i,s,r}@PLT` sequence parallel to `class_inherit` (class+field as `.byte` rodata, value as `mov rdx`/`.byte` string/`.quad`+`movsd`), so the standalone binary repopulates defaults — m3/m4 byte-faithful by construction. Smokes (all `[m3 PASS][m4 PASS]`): `attr_typed`, `attr_default_int`, `attr_default_str`, `attr_default_override`, `attr_typed_default`, `attr_default_inherited`. **DEFERRED:** (a) closure/expression defaults (`has $.x = computed()` / `has $.x = $!other + 1`) — only literal constants are captured today; a non-literal default is silently skipped (field stays the type default, no crash). Needs a per-field default *closure* threaded through the record system + run at construction (true op-400). (b) type CONSTRAINT enforcement (`has Int $.x` rejecting a Str) — the type is parsed but discarded; enforcing it needs the type carried into the spec + checked in `dat_construct`. (c) native-typed attrs (`int`/`num`/`str` primspec, BUILDPLAN ops 1/2/3) — SCRIP attrs are all opaque `DESCR_t`.
- [x] **RK-OO-B1 — user `method new` overrides built-in `obj_new` — LANDED both modes (2026-06-15, `41a9393`).** `method new(...)`/`self.bless(k=>v)`/`T.new(positional)` parse (bison-regen only); class-name barewords → `IR_LIT_S` (`rk_is_class_name`); runtime `bless` construct + `obj_new`→user-`new` routing + type-object (class-name receiver) method dispatch. Smokes: `method_new_override`/`bless_named`/`type_object_method`. See HANDOFF-2026-06-15-...-OO-B1-METHOD-NEW.md.
- [ ] **RK-OO-B2 — `bless` + BUILDPLAN** (op-list: 0 set-attr-from-named, 400 default-closure, 800 die-if-required). Default `new` = `self.bless(|%args)`. (Basic `bless` from named args landed in B1; BUILDPLAN ops are the remaining work.)
- [ ] **RK-OO-B3 — `BUILD`/`TWEAK` submethods** (submethod_table; don't inherit).
- [ ] **RK-OO-B4 — required attrs (`is required`)** (BUILDPLAN op 800/1503).
- [x] **RK-OO-C1/C2/C4 — single + multi-level inheritance — LANDED both modes (2026-06-15, `952d528`).** `class Child is Parent {…}` (parser: `KW_CLASS IDENT IDENT IDENT '{'` with action-time `is` check, parent name stored in `TT_CLASS_DECL` node `v.sval` — NOT a lexer keyword, see constraint above). C2 attr inheritance: `class_inherit(child,parent)` in `driver_data.c` flattens parent fields into child (parent-first, dup-checked → idempotent), `DatType` gains `char parent[64]`. C4 method inheritance: `resolve_method_chain()` in `by_name_dispatch.c` walks `self→parent→…` (via `dat_parent`) for the first `<C>__<m>` present in proc_table OR native registry; `meth_call` uses it. m4: `scrip.c` emits `class_inherit@PLT` calls after `record_register` so the standalone binary has parent links. Smokes: `inherit_attr`/`inherit_method`/`inherit_override`. **CAVEAT: multi-level (3+ class) programs can hit the PRE-EXISTING `x86_uid` dup-label emitter scaling bug in m4 (`bbNNNNN_α already defined`) — orthogonal to inheritance logic (m3 always works; m4 works for 2-class). That emitter bug is the real blocker for larger m4 OO programs.**
- [ ] **RK-OO-C3 — C3 MRO** (`compute_mro` linearization). Needed for diamonds; single/linear chain works today via the simple parent walk.
- [ ] **RK-OO-C5 — `callsame`/`nextsame`/`callwith`** (re-dispatch to next MRO candidate).
- [ ] **RK-OO-C6 — multiple inheritance (`is A is B`)** (MRO merge; needs C3).
- [ ] **RK-OO-D1..4 — Roles** (`role`/`does`; role-to-class flattening per `RoleToClassApplier`; required-method stubs + conflict detection; punning).
- [ ] **RK-OO-E1..2 — Multi-dispatch** (`multi`/`proto`; arity then type-narrowness).
- [ ] **RK-OO-F1..4 — Metaobject/introspection** (type objects + `:D`/`:U`/`.defined`; `.WHAT`/`.^name`; `.^methods`/`.^attributes`/`.^parents`; `.isa`/`.does`).
- [ ] **RK-OO-G1..6 — Advanced** (`.Str`/`.gist`/`.raku` override; operator overload `multi sub infix:<>`; `handles` delegation; `but`/runtime mixin; `enum`/`subset`; `.=`).

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

## ▶ GRAMMAR/REGEX DIRECTION (2026-06-14) — PARKED BEHIND THE OO LADDER (see ★ top of file)

> **PARKED 2026-06-15:** RK-GRAM-3 (the recursive-descent grammar engine) was the prior lead rung; it is now
> PARKED behind the OO ladder per Lon. The direction below stays AUTHORITATIVE for when grammar work resumes —
> do NOT re-derive it. Grammars register and `.parse` dispatches end-to-end in all three modes today (`f3b1837`);
> recursive grammars are the remaining gap.

**DIRECTION SET BY LON 2026-06-14: an NFA is the WRONG primary engine for a top-down recursive-descent
language. The entire NFA-on-Byrd-boxes apparatus is DELETED (SCRIP `d63c374`).** Verified against the Rakudo/
NQP internals: real Rakudo's matcher IS recursive descent (a backtracking cursor machine with a bstack); the
NFA is only an LTM-dispatch oracle that prunes/orders alternation+proto candidates and does ZERO consuming or
capturing. An engine is fully correct with no general NFA (the old PGE engine matched Raku regex with only
literal-prefix dispatch). Subrule `<name>` recursion (Raku supports self-recursion) is at least context-free →
provably beyond any finite automaton → needs a pushdown/recursion mechanism, i.e. recursive descent.

**WHAT WAS DELETED (`d63c374`):** `IR_NFA_*` IR kinds (11 of them) from IR.h + scrip_ir.c name table;
`nfa_to_bb`/`nfa_bb_exec`/`nfa_bb_graph_exec` + the file `src/parser/raku/nfa_bb.c` + re.h decls + Makefile
entries; the `RK_NFA_BB` env dispatch (collapsed to the C matcher); the `IR_NFA_MATCH` interp case + bb_reset
exemption; `test_gate_raku_nfa_oracle.sh`. `~~ /regex/` reverted to the plain `re_match` IR_CALL (dval=2) and
now cleanly EXCISES in m3/m4 (gate guard mirrors the DVAL2_BOMB predicate: `dval==2 && !__rk_bool/__rk_try &&
!rt_builtin_is_known`).

**WHAT STAYS (Lon 2026-06-14): the C NFA matcher for RE.** `src/parser/raku/re.c` (`nfa_build`/`nfa_exec`/
`Nfa`/`Match`) is KEPT as the regex engine for plain `~~ /regex/`. This is NOT "NFA-BB" — it is the runtime
regex matcher, and it carries m2 regex+grammar today. Grammars currently match via `gram_expand` (inline-
flatten subrules → one NFA → `nfa_exec`) — a NON-recursive stopgap (`by_name_dispatch.c`: hard depth-16 cap +
4096-byte buffer; a self-recursive rule overflows/caps out = wrong). Flat grammars (the 4 grammar smoke tests)
work; recursive grammars do not.

**STATUS (2026-06-15, SCRIP `41a9393`):** Raku m3/m4 **80 PASS / 0 FAIL / 7 EXCISED** of 87
(the 7 = 3 `~~` verdict+capture smokes + 4 map/grep — all correctly EXCISED, never abort). This session: RK-OO-A2
accessor half (`5370ad1`, +3 smokes) then RK-OO-B1 user `method new`/`bless`/type-object dispatch (`41a9393`, +3).
Prior session (`952d528`) brought OO attr-mutation + inheritance (74/0/7/81) and the Str/Cool/List method suite.
**Mode 2 / `--interp` is GONE** (the IR-graph interpreter was deleted, `a2440f4`); the numbers above are the two NATIVE
modes and m3 is the primary correctness mode. Peers: Icon m3/m4 12/12, SNOBOL4 m4 7/7. g_vstack=0, bb_bin_t=0, IR_NFA=0.

**LANDED 2026-06-14 (3 commits, `1c64469`/`2860563`/`b63cc45`):**
1. **map/grep abort→EXCISE (the regression fix).** `a2440f4` (interp deletion) bomb-stubbed `bb_mapgrep_prepare`
   (its `IR_interp_once` materialization body was deleted) but LEFT `graph_native_emittable_mode` ADMITTING
   `IR_MAP`/`IR_GREP` — so a map/grep program reached the `[NO-IR-INTERP]` bomb and ABORTED, violating
   PASS-or-EXCISED. FIX (matches the intent of the already-dead `kind_native_stub`): node-loop guard
   `IR_MAP||IR_GREP → return 0`, and dropped them from `rhs_kind_ok` (kept `IR_GATHER`, which has a real
   self-contained `bb_gather.cpp`). `gather_take` still PASSes; map_range/grep_range/map_over_gather/
   grep_over_gather: abort → clean `[SMX]` EXCISE.
2. **Smoke harnesses de-interp'd to 2-mode (raku + icon + snobol4).** All three still invoked the deleted
   `--interp`; raku/icon GATED on `[ $F2 -eq 0 ]` → rc=1 despite clean m3/m4. Removed every `--interp`
   invocation + m2 bookkeeping; gate on zero silent m3/m4 FAIL + floors (the shape snobol4 already used). Icon
   gate STRENGTHENED from floors-only to m3/m4 zero-FAIL (m3 replaced m2's build-sanity role) — one-line revert
   if the Icon owner wants it looser. Behavior-neutral for every compiler; all three gates now rc=0.

**RAKUDO SOURCE CORRECTION (read `6_rakudo-main` this session — do-not-re-derive):** real Raku `gather`/`take`
is **NOT materialized** — it is a first-class **continuation coroutine** (`Rakudo/Iterator.rakumod` `class
Gather does SlippyIterator`): the block runs under `nqp::handle(&block(),'TAKE',…)`; each `take` decrements
`$!wanted` and at 0 captures the continuation (`nqp::continuationcontrol(0,PROMPT,…)`) and SUSPENDS mid-block;
`pull-one` sets `$!wanted=1` and `nqp::continuationreset`s to resume to the next `take`. `map`/`grep`
(`Any-iterable-methods.rakumod`) are ALSO lazy — `Seq.new(<pull-one iterator over SELF.iterator>)`. So ALL
THREE are lazy. SCRIP's `bb_gather.cpp` only emits the **degenerate literal-int-take** case (constant-folds each
`take(N)` at compile time into a baked `.quad` cursor; `take($computed)` aborts) — passes the smoke but is far
from real gather. **IMPLICATION for RK-EMIT-MAP/GREP + RK-GRAM-3:** the generator-PUMP the goal calls for
("closure emitted as native, invoked per element, SUSPEND/EVERY driver") IS Rakudo's continuation model, and the
four-port box resumption (γ advance / ω redo / β resume) is its native analog — the same suspend/resume-across-a-
boundary substrate both rungs need.

**NEXT: RK-GRAM-3 (THE SEAM) — recursive-descent grammar engine.** Build subrule `<name>` recursion +
backtracking on the EXISTING four-port box-resumption substrate (the SNOBOL4 pattern boxes `bb_match_*`/
`bb_pattern_*` ARE a backtracking recursive-descent matcher — γ=matched/advance-cursor, ω=fail/redo; alternation
= `IR_ALT`; subrule call = recursion into another box graph; the Σ/δ/Δ subject triad already reserved for the
regex slab is the cursor). This REPLACES `gram_expand`'s flatten-to-NFA for recursive grammars and builds a real
Match tree. Needs full budget + `ARCH-x86.md`/`ARCH-SCRIP.md` reads first. NOTE the obsoleted rungs below.


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
FORM:** a box's leading `α:` label (`s_1asm(std::string(_.lbl_α)+":")`) and comments (`s_comment(...)`) exist only
in the GAS arm, so `IF(MEDIUM_TEXT, <comment-or-label>)` with NO matching `IF(MEDIUM_BINARY, <bytes>)` is fine; an
`IF(MEDIUM_TEXT,<gas-instruction>) + IF(MEDIUM_BINARY,<bytes>)` PAIR is the violation. Non-x86 platform arms
(JVM/JS/NET/WASM) are out of scope (X86 ONLY for now) and keep their `s_*asm` text.


**CORRECTION RECORD (Lon 2026-06-06):** RULES.md TEMPLATE-ONLY EMISSION is now corrected to MATCH this rule; its former
“duplicate the byte-producing code into each template file” clause (515aa7d6, 2026-05-28) is DEAD — it predated the
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

## STATUS — Raku is the FOURTH concurrent BB session (peer to SNOBOL4/Icon/Prolog)

Raku is LIVE through `lower.c` (RK-LOWER-0..4 + 5a/5b done; mode-2 oracle healthy). Post-SMX-4: no Stack
Machine engine; ONE unified `lower.c`; `IR_*` node taxonomy; BB run-path via `bb_exec_once`. The SM-era
`BB_*`/`SM_*` content is preserved as SEMANTIC SPECS in **APPENDIX A** (numbers NOT reachable today; don't cite as live).

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
| **R10** | caller-saved | LOCAL | per-BLOB DATA-block ptr (`lea r10,[rip+Δ_data]`); constant inside a BLOB |
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

**Pipeline (post-SMX-4 — the SM engine is GONE; this is the BB run-path all four languages share):**
```
Raku source → raku.l / raku.y → tree_t* (TT_* AST)
    → src/lower/lower.c  lower2()  [cx.lang = IR_LANG_RKU, role VALUE]
        → IR_t four-port graph (alpha/beta/gamma/omega; ports are POINTERS → goto-chains collapse)
    → [mode 2] bb_exec.c: bb_exec_once(entry) / bb_exec_resume   (correctness ORACLE)
    → [mode 3] --run native runner → SM/BB/XA template BINARY arms → sealed RX → jump in
    → [mode 4] --compile --target=x86 → template TEXT arms → as → gcc -no-pie -lscrip_rt → run
```

- **Mode 2 (`--interp`):** `bb_exec_once` C oracle over the lowered `IR_t` graph. The reference.
- **Mode 3 (`--run`):** native runner → `{BB,SM,XA}_templates/*.cpp` MEDIUM_BINARY arms. (For SNOBOL4
  this AOT path is not yet rebuilt; for Raku it does not exist yet either — see the rungs.)
- **Mode 4 (`--compile`):** template MEDIUM_TEXT arms → GAS → gcc link → run the binary.

> **⛔ TESTING DIRECTIVE (mirrors the other three GOAL files, Lon 2026-05-31) — ALWAYS RUN ALL THREE
> MODES.** Every time you test Raku, exercise mode 2 (`--interp`), mode 3 (`--run`), AND mode 4
> (`--compile --target=x86` → `as` → `gcc -no-pie … -lscrip_rt` → run). Mode 2 is the **HARD gate**
> (exit 0 requires mode-2 all-pass); modes 3 and 4 are **RUN + REPORTED on every invocation** (tracked
> with `MODE3_MIN`/`MODE4_MIN` PASS floors, default 0) so the full native picture is always visible.
> Never report a mode-2 number alone. Raise the floors as 3/4 come back so regressions in them also fail.
>
> **⛔ COMPLETION BAR — adopted from GOAL-ICON-BB / GOAL-PROLOG-BB (2026-06-01).** A rung is **promoted only
> when all three modes are accounted for together**: (1) mode-2 all-PASS (the oracle, HARD); (2) mode-3 PASS
> **or** LOUDLY EXCISED; (3) mode-4 PASS **or** LOUDLY EXCISED — **never a silent FAIL or an abort.** An
> unbuilt native family (no `bb_rk_*` template yet) is added to `icn_kind_native_stub` (`src/driver/scrip.c`)
> so the `(is_icon || is_raku)` mode-3/4 pre-flight prints `[SMX] … EXCISED` and DECLINES — the gap stays
> visible and tracked, not hidden behind a crash. `test_smoke_raku.sh` now reports three columns
> (`PASS / FAIL / EXCISED`) per mode and its exit gate requires **zero silent m3/m4 FAIL** (every native mode
> PASS-or-EXCISED) on top of the m2 hard gate. Driving an EXCISED family to PASS = writing its stackless
> `bb_rk_*` template (the RK-EMIT work). The `[SMX]→EXCISED` mechanism is byte-identical to the Icon/Prolog twins.

**Mandatory reads, in order, every Raku session:**
1. `GOAL-ICON-BB.md` (the live ground-zero goal + the canonical four-port generator model Raku REUSES).
2. `RULES.md` in full (No C Byrd boxes · TEMPLATE-PURITY · ONE x86 PRODUCER · stub LOUD via `bomb_bytes()`
   · X86 ONLY · MODE PURITY — no silent cross-mode fallback / no silent eps substitution).
3. This file. Find the first incomplete `- [ ]` rung in the ladder.
4. `GOAL-RAKU-FRONTEND.md` (parser/lexer state) and `GOAL-PST-RAKU.md` (pure-syntax-tree track) if touching the frontend.
5. If touching corpus → `CORPUS-LOCATIONS.md`. If MODE3/4-EMIT → `ARCH-x86.md` AND `ARCH-SCRIP.md`.

**Absolute rules (RULES.md):** No C Byrd boxes. TEMPLATE-PURITY. ONE x86 PRODUCER. Stub LOUD via `bomb_bytes()`. X86 ONLY. MODE PURITY. No `rt_*`/`raku_*` port-logic helpers; conversion/effect helpers via `@PLT` (mode-4) or absolute `movabs+call` (mode-3) are fine.

---


## The insight (Raku is a Seq language → ONE four-port pull protocol)

Per docs.raku.org: almost everything generative in Raku produces a **`Seq`**. `gather`/`take`, the
`…` sequence operator, lazy ranges, `map`, `grep` — all "generate a Seq" on demand. ONE four-port
pull protocol (yield-one-at-β, identical to Icon's generator `SUSPEND`/`EVERY` PUMP) suffices; every
generative construct is a PRODUCER or CONSUMER of it. A 10-kind ladder collapses to ~3 rungs on the
SHARED Icon generator kinds — Raku adds almost no new IR kinds, it REUSES Icon's.

## Port semantics (identical to Icon generators — REUSE, do not reinvent)

| Port | Direction | Raku meaning |
|---|---|---|
| gamma | inherited DOWN | `take` yield / next Seq element delivered to the consumer |
| omega | inherited DOWN | exhaustion (Seq drained; junction collapsed; grep all-false) |
| alpha | synthesized UP | fresh-pull entry (first `.pull-one`) |
| beta | synthesized UP | resume entry (next `.pull-one` after a yield) |

Driver = the Icon generator PUMP (`IR_EVERY` / the `IR_*` resumable family). NOT Prolog's once-driver.

## Moves to BB (shared IR) vs stays eager

**MOVES (goal-directed, REUSE shared Icon IR kinds — Raku adds `cx.lang==IR_LANG_RKU` arms INSIDE the existing cases):**

| Raku construct | shared IR kind (Icon's) | rung |
|---|---|---|
| lazy range `$a..$b`, `$a,$b … $c` | `IR_TO` / `IR_TO_BY` | RK-LOWER-1 |
| `gather { … take … }`, `…` operator | `IR_*` SUSPEND + PUMP (Icon generator) | RK-LOWER-2 (keystone) |
| lazy `map` / `grep` | `IR_*` ITERATE consumer (eager-drain) | RK-LOWER-3 |
| junctions `any`/`all`/`one`/`none`, infix bar/amp | `IR_ALT` + Bool-collapse | RK-LOWER-4 |

**STAYS eager (lower to straight-line `IR_*`, no generator):** scalar builtins, `say`/`print`,
arithmetic, hash/array element ops, class/method dispatch, `sort` (whole-list), `try`/`CATCH`.

**REGEX / GRAMMAR (RK-NFA rungs):** regex backtracking onto an ISOLATED `IR_NFA_*` family (NOT
SNOBOL4's pattern opcodes — isolation decision below). Grammar/LTM deferred to Phase 2.

---

## Rung ladder (REVAMPED for the unified `lower.c` + BB run-path)

Completed rungs (git history has full detail): RK-LOWER-0 (say/print ✅), RK-LOWER-1 (lazy range→IR_TO ✅), RK-LOWER-2 (gather/take→IR_GATHER ✅), RK-LOWER-3 (map/grep→IR_MAP/IR_GREP ✅), RK-LOWER-4 (junctions→__rk_jct_* ✅), RK-LOWER-5a (read-only value ops ✅), RK-LOWER-5b (mutating ops via pure-variant writeback ✅), RK-LOWER-5c (try/CATCH/die ✅ 2026-06-12 — TT_DIE→IR_CALL("die"); TT_TRY→IR_CALL("__rk_try", dval=2.0, na=1or2) with body/catch as sub-graphs in EXEC.counter; IR_interp intercepts "__rk_try", runs body, checks g_script_exception, runs/swallows catch. **ALSO FIXED:** `lower_raku_stage2` now populates `lower_sc` with param names after assigning bb_idx — mirroring `lower_icon_stage2` — so the dval==2.0 IR_CALL dispatch can bind args via NV_SET; previously lower_sc was always empty → all proc params read as NUL/0. `rk_try_catch25.expected` corrected: `might_die(0)` fires die before say, so the two bogus "0" lines removed.), RK-EMIT-1/2/3 (Raku rides Icon's native driver via is_raku flag ✅), RK-EMIT-GATHER (bb_rk_gather.cpp, x86() API ✅), RK-HY-0/1/2 (de-cram: bb_binop_jct_relop, bb_seq→3 files, bb_nfa→7 leaf files ✅), RK-HY-3 (bb_call_rk.cpp extracted ✅), RK-NFA-1 (IR_NFA_* graph builder + mode-2 walk ✅), RK-NFA-2 (csets/anchors/ordered-alt gate ✅), RK-NFA-3 (captures $0/$1/$<name> ✅).

- [ ] **RK-EMIT-MAP/GREP** — `bb_rk_map.cpp`/`bb_rk_grep.cpp` (`IR_MAP`/`IR_GREP`). m2 PASS, m3/m4 EXCISED. Closure emitted as native + invoked per element. Blocked on Icon GZ-7 (IR_ASSIGN ζ-slot store).
- [x] **RENAME-C / RENAME-SNO / icn_ / SNOBOL-interp-vars / RK-NFA-4a-SMOKE — DONE `f548d70` (2026-06-14).** See the LANGUAGE-PREFIX PURGE bullets in the watermark for the full mapping + the LI-FENCE STATUS (remaining reds are the Prolog GZ type-migration tail, owner-only).
- [x] **RK-NFA-4 — OBSOLETE / DELETED 2026-06-14 (`d63c374`).** The native NFA-on-Byrd-boxes apparatus this rung was building (`IR_NFA_*`, `nfa_to_bb`, `bb_nfa_*`, `nfa_bt_ir_cap`, `RK_NFA_BB`, the oracle gate) is DELETED per Lon — an NFA is the wrong primary engine for a recursive-descent language. Superseded by the recursive-descent grammar engine (see CURRENT PRIORITY). Regex leaf matching stays on the C matcher `re.c` (Lon 2026-06-14).
- [x] **RK-NFA-5 — OBSOLETE 2026-06-14.** This rung's "on the BB rebuild" premise referenced the now-deleted NFA-BB path. Greedy/longest-match + multi-capture correctness is a property of the kept C matcher `re.c` (for `~~`) or the future recursive-descent engine (for grammars) — not a BB-NFA rung. (The `12abc → "1"/"2abc"` greediness is a `re.c` issue if/when it matters.)
- [ ] **RK-GRAM-3 (THE SEAM) — recursive-descent grammar engine (LEAD RUNG, reframed 2026-06-14).** See CURRENT PRIORITY (top of file) for the full direction. Build subrule `<name>` recursion + backtracking on the EXISTING four-port box-resumption substrate — the SNOBOL4 pattern boxes `bb_match_*`/`bb_pattern_*` ARE a backtracking recursive-descent matcher (γ=matched/advance-cursor, ω=fail/redo; alternation=`IR_ALT`; subrule call = recursion into another box graph; the Σ/δ/Δ subject triad reserved for the regex slab is the cursor). REPLACES `gram_expand`'s flatten-to-NFA for recursive grammars (today's depth-16-capped stopgap handles only flat grammars) and builds a real Match tree, then `$<name>`/`$0` capture access. Grammar registration + `.parse` dispatch already landed (`f3b1837`); regex `~~` stays on the kept C matcher. Needs full budget + `ARCH-x86.md`/`ARCH-SCRIP.md` reads first.
- [ ] **RK-GRAM-4..6 — LTM + proto dispatch; actions + Match tree; convergence/control/adverbs.** (UN-DEFERRED 2026-06-14. Sits on the RK-NFA-4 BB matcher + RK-GRAM-3 PUMP.)
- [x] **RK-NFA-CONV — OBSOLETE 2026-06-14.** `IR_NFA_*` kinds are deleted; there is nothing left to converge with SNOBOL4 `IR_PAT_*`.

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh            # or: make -j4 scrip   (rc=0; seed `scrip --interp` → hello)
make libscrip_rt                       # rc=0
```

## Gates (run ALL THREE MODES per the TESTING DIRECTIVE; behavioral gates stay INVARIANT under byte-neutral change)

```bash
make scrip                                    # rc=0
make libscrip_rt                              # rc=0
bash scripts/prove_lower2.sh                  # topology — Raku cases ADDITIVE in the RAKU section; stays green
bash scripts/test_smoke_raku.sh               # mode 2 HARD; m3/m4 tracked (floors MODE3_MIN/MODE4_MIN)
bash scripts/test_smoke_icon.sh               # m2 6/6 (HARD) — REUSED generator kinds; must not regress
bash scripts/test_smoke_snobol4.sh            # m2 7/7 (HARD) — NFA isolation proof: must stay byte-unchanged
bash scripts/audit_concurrency_invariants.sh  # OK — no dup case TT_/IR_, FACT RULES byte-identical
bash scripts/util_template_purity_audit.sh    # no bytes outside templates (baseline)
```

**Isolation gate (every RK-NFA step):** `test_smoke_snobol4.sh` + the SNOBOL4 pattern-rung suite must stay
byte-identical (no SNOBOL4 pattern template touched), FACT grep 0, Icon/Prolog smokes invariant.

---

## Architecture reference

- Unified lowerer: `src/lower/lower.c` — `lower2()`, role-seeded `lower2_{value,pattern,goal}_entry`; Raku arms are `cx.lang==IR_LANG_RKU` branches INSIDE the shared `tree_e` cases.
- Shared four-port builders: `wire_seq` (n-ary sequence-with-backtrack), `wire_alt` (n-ary fail-chain), `wire_det_builtin1` (role-agnostic deterministic builtin call — Raku `say`/`print` reuse this).
- Semantic oracle (mode 2): `src/lower/bb_exec.c` — `bb_exec_once` / `bb_exec_resume` over `IR_t`.
- Topology proof harness: `src/lower/prove_lower2.c` (+ `scripts/prove_lower2.sh`); `main()` is sectioned SNOBOL4 / ICON / PROLOG — ADD a RAKU section (BEGIN/END markers) so concurrent appends auto-merge.
- Emitter dispatch: `src/emitter/emit_core.c`; Raku templates: `src/emitter/BB_templates/bb_rk_*.cpp`.
- Register source of truth: `src/emitter/bb_regs.h` (the BBREG_*/BBREGN_* names; the subject triad is used only in the NFA slab).
- Raku frontend: `src/frontend/raku/raku.l`, `raku.y`; goal files `GOAL-RAKU-FRONTEND.md`, `GOAL-PST-RAKU.md`.
- Isolated regex matcher (C reference / oracle): `src/frontend/raku/raku_nfa*.c` (`nfa_bt`), `raku_re.c`.

---

## Watermark

**RK-OO-A4 — typed + constant-default attributes — LANDED both native modes (2026-06-15, this session).** `has Int $.x` (type parsed+ignored) and `has $.x = 42` (constant default, Rakudo BUILDPLAN op-400 constant case) parse and work. `DatType` gains `defaults[64]`/`has_default[64]`; `dat_construct` applies a default when the field arg is absent (single chokepoint → `obj_new` + `bless` both covered); `class_inherit` carries defaults to children; lower sets literal defaults after `record_register`; m4 `proc_startup` emits a `dat_set_field_default_{i,s,r}@PLT` sequence parallel to `class_inherit` (m3/m4 byte-faithful). Parser bison-regen only (6 new `class_body_list` rules, conflicts steady at 31, NO lexer change — `Int`=`IDENT`; new `TT_HAS_DECL` AST node for the defaulted case). Raku m3/m4 **86 PASS / 0 FAIL / 7 EXCISED / 93** (was 80/0/7/87 — +6 smokes: `attr_typed`/`attr_default_int`/`attr_default_str`/`attr_default_override`/`attr_typed_default`/`attr_default_inherited`). Peers invariant: Icon 12/12, SNOBOL4 7/7. `g_vstack`=0, `bb_bin_t`=0, IR_NFA=0; no-lang-names fence + template purity show only the documented pre-existing baselines (my symbols 0 hits, 0 templates touched). DEFERRED: closure/expression defaults (non-literal → silently skipped), type-constraint enforcement, native-primspec attrs. See HANDOFF-2026-06-15-...-OO-A4-TYPED-DEFAULT-ATTRS.md.

**RK-OO-B1 — user `method new` + `bless` + type-object dispatch — LANDED both native modes (2026-06-15, SCRIP `41a9393`).** `method new(...)` parses (KW_NEW accepted as method name, bison-regen only — no lexer change); `self.bless(k => v)` parses (named-arg methcall rule); `T.new(positional)` parses. Class-name barewords now lower to `IR_LIT_S` (mirrors the grammar-name fix) so a class receiver isn't a free `IR_VAR` tripping the m3/m4 EXCISE gate (new `rk_is_class_name` registry in `lower_raku.c`). Runtime (`by_name_dispatch.c`): `bless` arm constructs from named args; `obj_new` routes `.new` to a user `<C>__new` if present (else built-in — regression-clean); a method call on a class-name string routes to the user method with the class name as `self`. Smokes: `method_new_override`/`bless_named`/`type_object_method`. Raku m3/m4 80 PASS / 0 FAIL / 7 EXCISED / 87. Peers invariant: Icon 12/12, SNOBOL4 7/7; g_vstack=0, bb_bin_t=0, IR_NFA=0.

**RK-OO-A2 (accessor half) — public-attribute auto-accessor `.x()` — LANDED both modes (2026-06-15, `5370ad1`).** Runtime-only `meth_call` fallback: if the method is no-arg and not a real user proc (`meth_is_user_proc`) and the receiver has a field of that name (`data_field_ptr`), return the field value (Rakudo `has_accessor` codegen; user method of the same name wins). Privacy (`$!`) + `is rw` are LEXER-BLOCKED (twigil erased at lex; flex can't regen) — deferred.

**STR/COOL/LIST METHOD SUITE — 30 methods, runtime-only (2026-06-15, `c82bc7e`).** One CS-neutral `rt_str_method` in `by_name_dispatch.c` reaching both `.meth` (`IR_FIELD_GET`→`dat_field_get`) and `.meth(args)` (`meth_call`). case/measure/Str→list/args/coercion/numeric/list methods; semantics per Rakudo `core.c/{Str,Cool,Int,List}`. See HANDOFF-2026-06-15-...-STR-COOL-METHOD-SUITE.md.

**OO ATTR-MUTATION + INHERITANCE (2026-06-15, `952d528`).** RK-OO-A1 (attr mutation: twigil-lvalue + void methcall → `field_set`) and RK-OO-C1/C2/C4 (`class Child is Parent`: attr+method inheritance via `class_inherit`/`resolve_method_chain`). See HANDOFF-2026-06-15-...-OO-ATTR-MUTATION-AND-INHERITANCE.md. **CAVEAT:** 3+ class m4 programs can hit the pre-existing `x86_uid` dup-label emitter bug (m3 fine; m4 fine for 2-class).

**GRAMMAR `.parse` FOUNDATION (2026-06-14, `f3b1837`).** Grammars register + `.parse` dispatches end-to-end all modes via `gram_expand` inline-flatten → NFA (`grammar_parse_core`). NON-recursive stopgap (depth-16 cap): flat grammars only; recursive grammars need RK-GRAM-3 (PARKED). `.parse` returns matched STRING (truthy) / `NULVCL` (falsy).

**NFA-BB DELETED — REGEX STAYS ON C MATCHER (2026-06-14, `d63c374`).** The NFA-on-Byrd-boxes apparatus (`IR_NFA_*`, `nfa_to_bb`, `nfa_bb.c`, `RK_NFA_BB`, oracle gate) is deleted; `~~ /regex/` rides the kept C matcher `re.c` (`nfa_build`/`nfa_exec`), cleanly EXCISES in m3/m4. Grammar engine direction = recursive descent (RK-GRAM-3), not NFA.

**LANGUAGE-PREFIX PURGE (2026-06-14, `f548d70`).** Post-lower stages (`driver/interp/runtime/emitter/machine/contracts`) carry zero language prefix; `icn_`/`raku_`/`rk_` etc. allowed only in `src/parser/` + `src/lower/`. Enforced by `test_gate_no_lang_names.sh` LI-FENCE. Remaining reds (≈40 grouped lines) are ALL pre-existing Prolog GZ type-migration tail (`pl_gz_*_t`/`pl_catch_*`/`rt_pl_*`) + Pascal `pas_*` — **owner-only, do NOT touch from a Raku session**; plus 3 false-positives to add to the ALLOW list (`__rk_bool`/`CALL_ROUTE_RK_BOOL_*`, `IR_DET_SUCC_PLUS`, the `_pl` float-cast union local).

**⚠ KEY GOTCHA (cost prior sessions real time):** `scrip` STATICALLY links the runtime; `out/libscrip_rt.so` is mode-4 ONLY. After ANY runtime `.c` edit, rebuild BOTH (`rm -f scrip && make -j4 scrip && make libscrip_rt`) and after any rebase, rebuild+re-gate before pushing — else m3 and m4 silently disagree. Parser edits: `cd src/parser/raku && bison -d raku.y -o raku.tab.c` (do NOT run flex — see LEXER CONSTRAINT).

- **Done (history):** RK-LOWER-0..5h, RK-NFA-ORACLE-FIX, RK-EMIT-1/2/3+GATHER, RK-HY-0..3, RK-NFA-1/2/3, RK-M34-1, while_loop fix, bb_call_fn MEDIUM arm, ONE-MEDIUM rk_bool, lbl_β double-colon, x86_uid dup-label, Bug 1 proc-double-emit (`33f7202`), user-sub CALL Layers A+B (`f6bbabb`), B-c bool_truthiness + B-b jct relops (`b9a2433`), GROUP C class_method emit path (session 9), **GROUP C class_method m3 freed-IR fix (`738b950`, session 10)** (git log).

## ⛔ FACT RULE — "HANDOFF COMPLETE" REQUIRES A CONFIRMED PUSH (Lon directive, 2026-06-24)
**The phrase "handoff complete" — or any terminal claim of doneness ("done", "all set", "wrapped up", "committed and clean" presented as the end state) — MUST NOT be spoken until `git push` has SUCCEEDED and `git log origin/main --oneline -1` (step 7) shows THIS SESSION'S hash on origin for EVERY touched repo.** A local commit is NOT a handoff; the bytes are on this disposable sandbox and vanish with it. "Pending push awaiting credential", "ready to push", or "the local commits are safe" is an **INCOMPLETE handoff and must be reported as INCOMPLETE — never dressed up as complete.** If a credential is missing or the push fails, the handoff is **BLOCKED**: state that plainly, say exactly what is needed, and STOP — do NOT declare completion. The push (step 6) and the `origin/main` hash confirmation (step 7) are the LAST and MANDATORY acts of every handoff; skipping either means the handoff did not happen, regardless of how green the local tree is. Verify HEAD == origin/HEAD per repo, or it is not done.

**HOW THIS WAS MISSED (root cause, 2026-06-24 — so it is not repeated):**
1. **BLOCKED was reframed as COMPLETE.** The push failed for a missing credential; instead of reporting the handoff BLOCKED, the green *local* state was reported as done with the push demoted to a suggested user follow-up. The rule's real success criterion (the session's bytes living on `origin`) was silently swapped for a weaker proxy (bytes committed to a disposable sandbox). A locally-committed handoff is the same failure as an uncommitted one, one step later.
2. **A bad precedent was inherited.** Prior HANDOFF docs in this repo literally recorded "commits pending push awaiting user token" as a handoff outcome, normalizing the incomplete pattern; it was pattern-matched instead of challenged. "Pending push" is NOT an outcome — it is an unfinished, BLOCKED handoff.
3. **The completion claim was free-authored text.** Nothing forced the status line to be checked against ground truth, so under optimism it drifted from reality. Free-text status will always drift; it must be computed.

**PROTOCOL — THE STATUS LINE IS COMPUTED, NEVER TYPED (the mechanical gate):**
The assistant MUST NOT write the string "HANDOFF COMPLETE" (or any terminal doneness claim) as its own prose. The ONLY sanctioned source of that claim is the verbatim stdout of **`bash scripts/handoff_status.sh`**, which reads ground truth (working tree clean + local HEAD == `origin/<branch>` + zero unpushed) for every git repo it AUTO-DISCOVERS under the workspace (no hardcoded repo list — it enumerates every repo with an `origin` remote, so it cannot miss a touched one and reports the count it found) and prints `HANDOFF COMPLETE` (exit 0) or `HANDOFF BLOCKED` with the reason (exit 1). Handoff step 7 is now: **run `handoff_status.sh`, paste its output verbatim, and only treat the handoff as done if that output — not the assistant — says `HANDOFF COMPLETE`.** If it says BLOCKED, the handoff is BLOCKED: fix the listed reason (commit, then `git pull --rebase && git push`) and re-run. Reading `origin` needs no credential; only the push that PRECEDES the check does. The script blocks on its own uncommitted bytes, so it cannot be satisfied by a tree that still has the rule edit unpushed — closing the loop on itself.

**LIMITATION — DO NOT OVERSELL THIS GATE.** A markdown rule CANNOT coerce the assistant to run the script; this rule has the SAME enforcement gap as the rule it replaces (the assistant must still choose to honor it — exactly what failed on 2026-06-24). The script makes the truth cheap to obtain and hard to FAKE; it does not make the lie IMPOSSIBLE. Real coercion can only live OUTSIDE the model: (a) a harness/product layer that blocks any completion claim not backed by a fresh `handoff_status.sh` run (only the platform can add this), or (b) the human reviewer, who is the enforcer that actually works — **reject any "HANDOFF COMPLETE" not accompanied by the script's verbatim stdout with hashes matching `origin`, and treat a bare completion claim as FALSE by default.**

