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


> **🔄 RESET 2026-06-02.** Live purpose: SNOBOL4 Byrd Boxes from ground zero. DE-NAME and REORG split to their own goal files.

## ⛔ TEMPLATE SPEC v2 (Lon 2026-06-04) — REGENERATE, DON'T PATCH

No local variables · ONE return per PLATFORM returning ONE concatenated string · IF()/FOR() string functions for all conditionals/loops · ONE source line == ONE asm line · REAL Greek α β γ ω (no PORT_ALPHA/BETA/GAMMA/OMEGA spellings) · no MEDIUM_TEXT/MEDIUM_BINARY at template top level (hide in helper functions) · zero emit_fmt() · zero C comments [separator status vs RULES.md: confirm with Lon] · zero blank lines. Each template is REGENERATED whole to this spec, not patched. Full directive + session state: `HANDOFF-2026-06-04-OPUS48-SNOBOL4-BB-HYGIENE-SWEEP-SPEC-V2.md`. Tracker: `SCRIP/BB-REVAMP-TRACKER.md` (reset to v2 semantics; v1 sweep — prose comments stripped + all >200-char lines wrapped — landed at SCRIP `2af3880`+`cd577ed`, gates sno 19/19 / icn m2 12/12 HARD).

## 🟢 CURRENT FRONTIER — CAPTURE ✅ + m4 SCAN-NATIVE ✅ + CHAIN-LABEL DRIFT ✅ — M2 18 / M4 16; probes 8/8

**NEXT: (1) BROK-2 ARBNO** (052/054 still SKIP — ARBNO still uses brokered `child_cache_get` path). **(2) REG-RO** (r10=22).

## SR-1 / SR-2 — call-frame save/restore

- [x] **SR-1a** — `rt_name_save_push` / `rt_name_restore` thin helpers extracted from `rt_call_named_proc`. Gated, byte-identical.
- [~] **SR-1b** — ❌ REJECTED (Lon 2026-06-03). SAVE/RESTORE stays FUSED in `rt_call_named_proc`. See handoff doc `HANDOFF-2026-06-03-OPUS48-SNOBOL4-BB-SR-1B-BOX-APPROACH-REJECTED.md`.
- [ ] **SR-2** — Save-records migrate INTO per-activation ζ-frame `[r12+off]` (kills global `g_name_save[]`). Do after SR-1 shape proven. Gate: define m3 6/6 + oracle; m2 7/7 HARD; no-stack/one-reg gates.

**Gate state (GREEN, verified 2026-06-04):** SNOBOL4 m2 **7/7 HARD** / m3 **6/6** / m4 **6/6** · Icon m2 **12/12 HARD** · `prove_lower2` PASS · `no_bb_bin_t` 0 · LI-FENCE 13 · concurrency OK · REG-FENCE TIER1=0 · probes 8/8 · rung M2 18 / M4 15. ENV: `apt-get install -y libgc-dev`.

## ✅ DONE (mode-3 byte-matched to SPITBOL oracle)

IR_SEQ value-concat (`'ab' 'cd'`→`abcd`); IR_SCAN `pattern`/`goto_s` (m3+m4); arith `2+3`→`5`; `OUTPUT="hello"`; `DOUBLE(21)`→`42` (define+params); `bb_binop` ROUTER DELETED; LI rung COMPLETE (de-name + comment purge, LI-FENCE gates); x86() TEMPLATE-REVAMP all loop-free+single-loop SNOBOL4 pattern leaves done: `bb_pat_{abort,tab,atp,pos,span,len,rem,any,notany,arb,defer,break,fence,alt,cat}` + `bb_lit` + `bb_lit_scalar` + `bb_var` + `bb_gvar_assign`; `x86_pair_loop` for variable-length combinators; STUB CLEANUP (-54 do-nothing stubs); `bb_nv_assign`/`bb_gvar_assign` renames; m4 UNBLOCKED 0→6 via flat TEXT emitter; concat fold; IR_SCAN TEXT arm; m4 scan-native routing; flat_drive_capture inline (BROK-1 precursor).

## 🔴🔴 #0 PRIORITY — BB-HYGIENE LADDER (SNOBOL4)

Per the BB-HYGIENE FACT RULE. After EACH step: SNOBOL4 m2 7/7 HARD byte-identical, purity green, commit.

- [ ] **SNO-HY-1** — `bb_pat_break.cpp`. De-cram: one file per distinct four-port shape behind a router. De-fuse `pBB->…->ival/sval` operand reads.
- [ ] **SNO-HY-2** — `bb_pat_tab.cpp` + `bb_pat_span.cpp`. TAB/RTAB and SPAN: split inline-vs-RT-call shapes; routers.
- [ ] **SNO-HY-3** — `bb_sno_assign.cpp` + `bb_capture.cpp`. Split literal-rhs vs slot-rhs vs name-store; capture deque-save vs @-cursor-write. De-fuse literal rhs.
- [ ] **SNO-HY-4** — `bb_pat_any.cpp` + `bb_pat_notany.cpp`. cset-blob vs single-char; routers.
- [ ] **SNO-HY-5** — `bb_pat_cat.cpp` + `bb_pat_alt.cpp` + `bb_pat_arb.cpp`. Combinators; variable-length define/jmp-pair shape separate.
- [ ] **SNO-HY-6** — audit rest (`bb_pat_len`, `bb_pat_pos`). Split only if >1 four-port shape.
- [ ] **SNO-HY-7** — de-dup + RT-fix, all SNOBOL4 boxes. Algorithm in TEXT+BINARY arm → DELETE both, replace with one `rt_*` call.
- [ ] **SNO-HY-FENCE** — `scripts/test_gate_bb_one_box.sh` green for SNOBOL4 files; in Session Setup. m2 7/7 HARD held.

## 🔴 REG LADDER — SNOBOL4 PATTERN-FAMILY REGISTER-LAYOUT MIGRATION

✅ **REG-0..REG-5 DONE** (register-establishment contract, bb_lit, cursor-advancing/verify/position/combinator/generator leaves all on Σ=R13/δ=R14/Δ=R15/ζ=R12; audit-confirmed 2026-06-03).

- [ ] **REG-RO** — READ-ONLY locals to IP-RELATIVE. RO addresses (lit, cset, helper-fn ptr) in SNOBOL pattern BINARY arms are `movabs` imm64; move each into sealed RO data trailer → `[rip+disp]`. Payoff: (1) conforms to RO FACT RULE; (2) position-independent → mode-4 relocatable; (3) removes last `r10` traffic (push/pop guards around memcmp/strchr + `bb_lit`'s `[r10]` cursor-mirror). Coupled to `xa_flat.cpp:140` `[r10]` cursor read — migrate that to r14 first or in lockstep. Per box: re-derive byte map + patch offsets; `as`+`objdump` verify. Gate per box; m2 7/7 HARD invariant.
- [~] **REG-FENCE** — `scripts/test_gate_sno_pat_reg.sh` AUTHORED. TIER1 `TEMPLATE_ADDR_SIG*`==0 HARD (passes `--strict`); TIER2 r10=22 informational (flip to `r10==0` HARD when REG-RO done). In Session Setup.

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

## ⛔ TWO LITERAL FORMS ONLY — MEDIUM_BINARY IS A HAND-CODED LITERAL BYTE MAP; NO FUNCTION MAY COUNT BYTES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md, GOAL-RAKU-BB.md, GOAL-SNOCONE-IR-BB.md)

**Every BB template emits its x86 in exactly TWO LITERAL forms, both counted BY HAND.** (1) `MEDIUM_BINARY`
is a hand-coded LITERAL byte map — `bytes("\x..")` opcode literals plus a LITERAL patch-offset map
(`bin = {{13,65,80,84,95}, {…}, {…}}` with HARDCODED constant offsets). (2) `MEDIUM_TEXT` is literal GAS asm.
Both forms are LITERALS. This is DELIBERATE, not a stopgap: a single shared/computed template proved
unmaintainable — it kept getting split apart — so each box is its own small template carrying its own
hand-coded byte map, and that literal form is the one that stays correct. (Lon directive, 2026-06-01 —
re-issued after a session INVERTED it: literal bytes + literal asm are RIGHT; the function-counter is WRONG.)

**FORBIDDEN — the ONLY thing that makes a site BAD: using a FUNCTION to count or compute the bytes.**
Specifically `b.size()` in any form (`bin.sites.push_back((int)b.size())`, `int off = (int)b.size()`,
`int mr_off = (int)b.size()`), or any helper that DERIVES a patch offset from the running buffer length
instead of a hardcoded literal constant. Every offset in `bin` must be a LITERAL integer, never a function
of the buffer. (CARVE-OUT: `bb_emit_asm_result` in `emit_str.cpp` may walk the FINISHED byte string with
`.size()` when it emits/patches — that is the consumer reading a complete literal, NOT a template counting
its own bytes; the prohibition is on a TEMPLATE deriving its patch offsets from a function.)

**NOT bad — explicitly allowed, do NOT flag or "fix" these:** hand-written `bytes("\x..")` opcode literals;
hardcoded `bin = {{…},{…},{…}}` literal offset tuples; literal internal rel32 deltas (`+65`, `-98`) written
as constants; `u8()/u32le()/u64le()` building literal immediates; `TEMPLATE_ADDR_*` address bakes. These ARE
the hand-coded byte map — the CORRECT, supported form. A box that hand-encodes bytes with literal offsets is GREEN.

**GUARD:** `scripts/test_gate_no_handencoded_bytes.sh` (informational baseline now; flips to a HARD `--strict`
zero-check). It counts, per `BB_templates/*.cpp` (comments stripped), every `b.size()` — the function
byte-counter — which is the ONLY bad pattern. The count only ever decreases as `b.size()` sites are rewritten
to literal offset maps; any session that raises it has violated this rule. **COMPLETION TEST:** (a)
`scripts/test_gate_no_handencoded_bytes.sh --strict` green — zero `b.size()` in any `BB_templates/*.cpp`;
(b) every `MEDIUM_BINARY` arm uses a hand-coded LITERAL byte map with hardcoded offsets, never a function to
count bytes; (c) the FACT RULE body is byte-identical across all five GOAL-*-BB files.

> **⛔ SNO/sno DE-NAME — ✅ SUPERSEDED + DONE.** This directive (strip `SNO`/`sno` from emitter/runtime,
> naming by CS concept) is COMPLETE and subsumed by the LANGUAGE-INDEPENDENT cleanup rung above +
> `GOAL-RUNTIME-RENAME.md`; LI-FENCE enforces it. Carve-outs preserved: `IR_LANG_SNO`/`LANG_SNO` (the shared
> lowerer's `switch(cx.lang)`); snocone (a DIFFERENT language — `sno` ⊂ `snocone`, never blanket-sed);
> `src/runtime/core/` SNOBOL runtime LIBRARY (LI-CORE, pending Lon); parser/frontend bridge (`sno_parse_*`,
> `lower_sno`, `tree_to_sno`, `test_sno_*`).

> **⭐⭐⭐ CORRECTED PATTERN ARCHITECTURE (Lon directive, 2026-06-01, Opus 4.8). THIS SUPERSEDES the `tree_t`-bake
> "DESIGN QUESTION (DECIDED)" below AND the PATND_t-based PB-1/PB-2 as previously landed. READ THIS FIRST; the

> **⛔ SNO/sno DE-NAME — ✅ DONE.** Subsumed by LI-FENCE. Carve-outs: `IR_LANG_SNO`/`LANG_SNO`; snocone; `src/runtime/core/`; parser bridge.

> **⭐⭐⭐ CORRECTED PATTERN ARCHITECTURE (Lon 2026-06-01).** A SNOBOL4 pattern is a graph of EMITTED BYRD-BOXES — `bb_box_fn` machine code — NOT a `PATND_t` or `tree_t`. `DT_P` = HEAD BLOCK = `{entry, OUTSIDE-γ slot, OUTSIDE-ω slot}`. Build = SPLICE (wire ports); no JIT-emit except for `*E`/EVAL/CODE. Seal at element granularity; wire at instance level. Runtime `STITCH_SEQ`/`STITCH_ALT` are the runtime twins of `wire_seq`/`wire_alt`. `BB_LINK` = pure-tail indirect-jump `jmp [r12+slot]` through ζ-frame; sets the universal seal-boundary external edge. Only needed when DT_P is a SHARED sealed head (not the current inline case).

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The AST→IR lowerer’s SHARED SPINE is **ONE file** — `src/lower/lower.c` — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** for the co-located languages. **AMENDED (Lon 2026-06-04): the shared IR graph is the LANGUAGE-INDEPENDENT contract — LOWER splits per language.** Prolog’s goal-role family now lives in `src/lower/lower_prolog.c` (`d6d93c6`; shared helpers de-static’d into `lower_internal.h`); remaining languages stay co-located in `lower.c` until Lon splits them out. The discipline below keeps concurrent sessions **conflict-free and mutually beneficial**:

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). One kind → one case → language arms inside. A language graduates to its OWN `lower_<lang>.c` ONLY by Lon’s directive (Prolog: 2026-06-04), taking its whole role-family with it — never an ad-hoc fork.

3. **EDIT ONLY YOUR OWN LANGUAGE’S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language’s arm.** A language owning its own `lower_<lang>.c` edits ONLY that file (plus lockstep scaffolding per rule 5) and never a peer’s. This is what makes concurrent sessions’ diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer’s proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED (declared in `lower_internal.h`, defined in `lower.c`). ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files’ FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit (it compiles `lower.c` + `lower_prolog.c` + the harness). Each cat’s proof cases are ADDITIVE (append your own; never delete a peer’s). Green = your arm wired right AND you didn’t disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c` (nor within any per-language lowerer file); (b) every case’s language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

## ⛔ TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified IR→x86 emitter is **ONE dispatch** — `src/emitter/emit_core.c`'s `switch (nd->t)` over the shared `IR_e` — fanning out to **per-box template functions** under `src/emitter/{BB,SM,XA}_templates/`. Every byte of emitted machine code lives INSIDE a template fn reached ONLY via this dispatch (RULES.md TEMPLATE-ONLY). SNOBOL4, Icon, and Prolog fill emitter boxes CONCURRENTLY in SEPARATE sessions, all writing into this one dispatch + this one template tree. The discipline below makes the three sessions **conflict-free and mutually beneficial** (one session's dispatch case + template file is the next session's ready slot), exactly mirroring the SHARED-LOWERER rule:

1. **ONE DISPATCH CASE PER IR KIND.** Each `IR_*` is at most ONE `case` label in `emit_core.c`. If your language's kind has no case → ADD it (one line: `case IR_FOO: bb_foo(nd); return 0;`). If it exists → it already calls the right template; do not duplicate. **NEVER duplicate the label.** Append new cases at the END of the language's contiguous block (SNOBOL `IR_PAT_*` block, Prolog `IR_GOAL/ARITH/BUILTIN/LOGICVAR/ATOM/STRUCT/UNIFY/CUT/DISJ/GCONJ` block, Icon `IR_EVERY/ALT/LIMIT/SCAN/TO/…` block) so the three sessions' inserts land in different hunks → git auto-merges.

2. **ONE TEMPLATE FILE PER BOX — NEVER A SHARED MEGA-FILE.** Each box's bytes live in its OWN `.cpp` (e.g. `bb_pat_len.cpp`, `bb_unify.cpp`, `bb_every.cpp`). A session creating a new box CREATES a new file; it never appends a second box's body into a peer's file. Per-box files = per-session non-overlapping edits. Duplicating a byte pattern INTO each template is REQUIRED (duplication is the point — RULES.md); never factor shared bytes into a common emitter helper that two languages edit.

3. **EDIT ONLY YOUR OWN LANGUAGE'S BOXES.** A session may ADD or MODIFY template files for ITS OWN language's kinds and the ONE dispatch line that reaches each. It must **NEVER modify another language's template body or dispatch line.** (SNOBOL touches `bb_pat_*`; Prolog touches `bb_goal/arith/unify/cut/disj/conj/atom/struct/logicvar`; Icon touches `bb_every/alt/limit/scan/to/iterate/…`.)

4. **BYTES LIVE ONLY IN TEMPLATES — A MISSING BOX FALLS LOUD.** FORBIDDEN outside a template fn: `seg_byte(SEG_CODE`, `SL_B(`, `sl_emit_one`, `emit_standard_blob`, and the raw byte-producers `bytes()/u8()/u32le()/u64le()` (allowed only in `bomb_bytes`/`bb_emit_asm_result` of `emit_str.cpp`). A kind with no template yet must hit the dispatch's loud default (assert/abort), never silently emit nothing or fall through. `scripts/util_template_purity_audit.sh` is the standing guard.

5. **THE SHARED SOURCE LIST IS ADDITIVE; BUILD/ABI CHANGES ARE LOCKSTEP.** The Makefile `RT_PIC_SRCS` template list is APPEND-ONLY — add your new `.cpp` on its own line at the end of the language's group (one line = one hunk, no conflict). ADDING a template + its source line + its dispatch case is free. CHANGING a shared emitter primitive (`emit_core` dispatch signature, `BB_t`/`IR_t` layout, the `operand_aux` sidecar API, register-frame ABI) affects all three → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE EMITTER GATES ARE THE SHARED GREEN SIGNAL.** Before every commit: `scripts/util_template_purity_audit.sh` (no bytes outside templates), `scripts/test_gate_em_template_byte_identity.sh` + `scripts/test_gate_em_template_matrix.sh` (templates emit the sanctioned bytes), and the per-language no-stack/one-reg gates (`test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`) must stay green. Green = your box emits right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case IR_` label in `emit_core.c` (`grep -oE 'case IR_[A-Z_]+' src/emitter/emit_core.c | sort | uniq -d` empty); (b) every `IR_*` kind a language emits has exactly one dispatch case reaching one template fn, unmatched kinds hit the loud default; (c) zero forbidden byte-emitters outside templates (`util_template_purity_audit.sh` clean); (d) the FACT RULE body is byte-identical across the three GOAL files (`awk '/TEMPLATE-ONLY EMISSION — ONE-DISPATCH/{p=1} p{print} /util_template_purity_audit.sh clean/{if(p)exit}'` md5 matches); (e) the emitter gates above are green.

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

**Repo:** SCRIP + corpus + .github
**Sister:** GOAL-COMMAND-CENTRAL.md · GOAL-TEMPLATES-X86.md · GOAL-PROLOG-BB.md · GOAL-ICON-BB.md
**Carved:** 2026-05-27

## ⛔ PER-BOX LOCAL STORAGE — ALL STATE LIVES INSIDE THE BOXES (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

**ONLY local BB allocation variables are used; NOTHING is stored outside the boxes.** Every value a
SNOBOL4 (or Icon / Prolog) BB graph computes or holds at run time lives in storage that belongs to a
box — never in any external/global side channel. There is NO AG ring at run time (the ring is the
MODE-2 ORACLE's idiom ONLY — `bb_exec_once`), NO value stack (`g_vstack`/`rt_push_*`/`rt_pop_*`), and
intermediate values are NOT threaded through the global name table (`NV_GET`/`NV_SET`) — name-table
stores are reserved for genuine SNOBOL4 *variables* on assignment, not for passing a value from a
producer box to its consumer.

**Each box owns exactly two kinds of local allocation, both INSIDE the box (not outside):**
- **READ-ONLY data (RO)** — compile-time constants for that box (literal int/real/string/cset values,
  the box's name string, fixed bounds, op codes). Placed in the SEALED segment adjacent to the box's
  BLOB and reached by IP-relative addressing (`lea/mov reg,[rip+disp]`, `disp` an emit-time constant in
  the BINARY arm; a `.L`-label in the TEXT arm). RO data is NEVER threaded on a stack and NEVER reached
  by an absolute `movabs … &slot` immediate.
- **READ-WRITE data (RW)** — the box's mutable runtime storage (its result value/DESCR slot, counters,
  cursors, per-box backtrack arenas, generator state). Lives in the per-sequence ONE-REGISTER FRAME and
  is reached register-relative `[ζ=r12 + emit_time_offset]`. A consumer reads a producer box's result by
  that producer's frame offset (`bb_slot_get`/`bb_slot_alloc`); a SNOBOL4/Icon *variable* is ONE
  name-keyed frame slot (`bb_varslot`) shared by its IR_ASSIGN(name) writer and IR_VAR(name) readers.

So every box value reference is exactly one of: **(RO)** `[rip+disp]` into sealed data, or **(RW)**
`[ζ+off]` into the per-sequence frame. Never a ring, never a value stack, never a name-table round-trip
for an intermediate. This is the `test_sno_1.c` / `test_icon.c` named-slot law the GZ-7 Icon and PLG-8
Prolog siblings already follow (`febef10`: `x:=42;write(x)` → m2==m3==m4, all slot-based, no ring).

**COMPLETION TEST (per box family):** (a) no `bb_exec_once`/AG-ring read or write on the mode-3/4 run
path; (b) no `g_vstack`/`rt_push_*`/`rt_pop_*`; (c) no `NV_GET`/`NV_SET` used to carry an *intermediate*
producer→consumer value (only true variable assignment); (d) every box-local read is `[rip+disp]` (RO)
or `[ζ+off]` (RW) — no `movabs … &pBB->slot` absolute slot address; (e) mode-3 BINARY arm and mode-4
TEXT arm of the SAME box do the SAME processing (the only diff is BINARY-bytes vs GAS-text).

---


## ✅ GROUND-ZERO LOWER REWRITE — FOUNDATION PROVEN (2026-05-31)

`lower.c` ONE unified AST→IR pass on Proebsting four-port model; `prove_lower2.sh` 67 cases green. Prolog now in `lower_prolog.c` (2026-06-04). `wire_seq`/`wire_alt` are shared LOCKSTEP helpers.

## ⭐⭐ REBUILT LADDER — PB-RB (CORRECTED PATTERN ARCHITECTURE)

- [x] **PB-RB-1** — REF_INVARIANT + retire PATND_t literal builder. `bb_ref_invariant.cpp` BINARY(25B)+TEXT arms; sealed head loaded into ζ-slot; probe PASS.
- [x] **PB-RB-2** — Matcher-box four-port ABI pinned. `IR_PAT_LIT` conforms BOTH arms. α bounds-check + memcmp + δ-advance → γ; β = δ-=len + jmp ω.
- [x] **PB-RB-3** — BB_MATCH driver restored (SCRIP `8cd05c1`). ONE `bb_match.cpp`, 3 emissions on `op_ival`; HEAD loads R13←Σ/R15←Δ/start=0; RETRY δ←start fall-through; ADVANCE ch.18 step-6. `bb_subject.cpp` loads Σ/Δ into ζ-slot. Probes 3/3.
- [x] **PB-RB-4** — STITCH_SEQ/STITCH_ALT: invariant half PROVEN via existing `flat_drive_cat`/`flat_drive_alt`; `probe_pb_rb_4_cat` + `probe_pb_rb_4_alt` PASS. CONV-ALT seam fixed (`flat_drive_alt` aux-fallback for operand_aux arms). Lowered-CAT γ-chain gather via `gather_lowered_cat_arms`. STITCH boxes proper only needed for runtime-variant wiring (Fork B).
- [ ] **PB-RB-5** — Operand-variant element matchers (Fork A). `LEN(N)`/`SPAN(cvar)` etc.: existing `IR_PAT_LEN`/`IR_PAT_SPAN` box reads operand late from ζ-slot. NO builder box. Prove + mode-3 `S LEN(2)`, `S SPAN('abc')`.
- [ ] **PB-RB-6** — BB_PAT_BUILD for STRUCTURAL variance (Fork A/B). `*E`/`$NAME`/pattern-valued var.
- [ ] **PB-RB-7** — REPLACEMENT BB (ph.4) + SUBSTITUTION BB (ph.5). mode-3 `S 'b' = 'X'` → `aXc`.
- [ ] **PB-RB-CONV** — IR_SCAN convergence: retire dual shape once native chain covers corpus breadth.
- [x] **PB-RB-8** — Mode-4 parity: m4 0/6 → 6/6 (flat TEXT emitter wired; output/arith/define/pattern/goto_s/concat all pass; non-const concat via `gvar_seq_flatten`→`rt_gvar_assign_concat_parts`).
- [ ] **PB-RB-OPT** — All-invariant BLOB freeze: collapse REF_INVARIANT+STITCH into ONE sealed blob. After correctness rungs done.

## ⛔⛔ BROKERED-MODE-ERADICATION

**THE DIRECTIVE (Lon):** `bb_build_brokered` is NOT needed; it goes. The emit-side brokered calling convention (`push rbp;mov rbp,rsp` prologue + `(ζ,entry)` call convention) survives in `bb_build_brokered` + `EMIT_BINARY_BROKERED` + two templates (`bb_capture.cpp`/`bb_arbno.cpp`). ORDER: convert holdouts to jump-to-α/β FIRST, then delete the builder.

- [ ] **BROK-0** — Dead-caller excision: `stmt_exec.c` calls in already-`abort()`-ing PATND paths → delete unreachable `bb_build_brokered` lines + `BB_MODE_*` branch + `g_bb_mode` global + `bb_build_pure_mode`. Gate: build rc=0; m2/m3/m4 byte-neutral.
- [ ] **BROK-2** — Convert ARBNO to jump-to-α/β. ARBNO is a generator loop: α matches null; retry re-enters child by `jmp child_α`; child γ→ARBNO γ, child ω→ARBNO ω/exhaustion — all by LABEL. Keep `std::deque<int>` per-activation slot. Gate: ARBNO corpus under `--run` holds; m2/m3 invariant. (BROK-1 = flat_drive_capture, already done.)
- [ ] **BROK-3** — Delete `bb_build_brokered`, `EMIT_BINARY_BROKERED`, `g_bb_brokered`, `BB_BROKERED`/`BB_WIRED` macros, brokered prologue. Drop `int entry` from `bb_box_fn` typedef if no survivor. ADD gate `scripts/test_gate_no_brokered.sh`. Gate: build rc=0; m2/m3/m4 smoke; no-brokered gate green.

## Architecture references

- Mode-2 oracle: `src/interp/IR_interp.c`
- Flat driver: `src/emitter/emit_bb.c` (`codegen_gvar_flat_chain_body`, `walk_bb_flat`)
- Template dispatch: `src/emitter/emit_core.c`
- Template dir: `src/emitter/BB_templates/bb_pat_*.cpp`
- Lowering: `src/lower/lower.c` + `lower_prolog.c` + `lower_program.c`
- Bomb infra: `src/emitter/emit_str.{cpp,h}`
- Audit gate: `scripts/audit_m3_native_binary_arms.sh`

## LOWER2 BOX LADDER — proven via prove_lower2.sh (67 cases)

Foundation (literal/unop/binop/to/if), combinators, loops, full PATTERN role, GOAL-role. Open arms: L2-B2/C/D/E/F/G/H (loop-escapes, limitation, assignment, calls, scan/match, returns, data/cset/IO) value-role; remaining GOAL ITE/findall/catch. LOWER2-EXEC: Icon value-level proof. L2-TMATCH: refactor into `tm`/`tm_g` form.

## Session log

**Watermark (CHAIN-LABEL DRIFT fix; SCRIP PUSHED origin/main=`f36dc13`; 2026-06-04 Sonnet 4.6).** 055 FLIPPED m4 (PASS-M4 15→16). Root cause: `IR_SEQ(dval=1.0)` concat sub-expression nodes entered the BFS `nodes[]` in `codegen_gvar_flat_chain_body` via `gvar_chain_is_real(IR_SEQ)=TRUE`; v_scan's no-repl path wires `land[k_yes].γ = IR_SEQ` (the α_out of v_assign, which is the concat RHS first entry), so the scan's S-goto resolved to the IR_SEQ node (at nodes[5], which emits NOTHING via `flat_drive_gvar_seq_passthrough`) instead of IR_ASSIGN_yes (at nodes[7]), causing execution to fall through to OUTPUT='fail'. Fix: `gvar_chain_resolve_stmt` (like `gvar_chain_resolve` but also follows through `IR_SEQ/IR_SEQ_EXPR` with `dval==1.0`); used ONLY in `codegen_gvar_flat_chain_body` BFS enqueue + emit-loop γ/ω lookup. `gvar_chain_operand_refs` keeps the old resolver so `gvar_stmt_operand_refs(IR_SEQ)` still walks IR_SEQ→IR_ASSIGN_yes and correctly sets α. Diff: +14/-5 lines, `emit_bb.c` only. Gates: smoke **7/7 HARD / 6/6 / 6/6** · rung **M2 18 / M4 16** · probes **8/8** · prove_lower2 PASS · no_bb_bin_t 0 · REG-FENCE TIER1 strict 0 · broker 32. **NEXT: (1) BROK-2 ARBNO** (052/054); (2) REG-RO (r10=22).

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
```

Gates:
```bash
bash scripts/test_smoke_snobol4.sh                   # GATE-1: 13/13
bash scripts/test_smoke_unified_broker.sh            # GATE-2: ~30-36 (sibling-influenced)
bash scripts/test_mode4_broad_corpus_snobol4.sh      # GATE-3: 178/280
bash scripts/test_interp_broad_corpus_and_beauty.sh  # GATE-4: 251/280
bash scripts/test_snobol4_pat_rung_suite.sh          # M2=19 M4=15 SKIP=0
bash scripts/audit_m3_native_binary_arms.sh          # GATE OK
bash scripts/test_gate_sno_pat_reg.sh                # REG-FENCE: TIER1 SIG=0 (HARD); TIER2 r10=20 (info, pending REG-RO)
SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh                                # 13/13
INTERP=$(pwd)/scrip SCRIP_M3_NATIVE=1 bash scripts/test_interp_broad_corpus_and_beauty.sh  # 195/280
```

For full failure list patch `head -40` to `head -300` in test_interp_broad_corpus_and_beauty.sh copy.

---

---

## 🔴 RECOVERY LADDER — STUB-CLEANUP CASUALTY RECONSTRUCTION

**What happened:** Commit `9afac84` (TEMPLATE-REVAMP) converted all non-working boxes to `x86_bomb` stubs. Commit `cd10224` (STUB CLEANUP) then deleted all 54 bomb stubs with the intent that future sessions would recreate them as real `x86()` implementations. Most boxes were correctly recreated; a handful were missed, breaking SNOBOL4 pattern work. Recovered originals live at `git show 713c581:src/emitter/BB_templates/<name>.cpp`.

**Recovered on 2026-06-04 (Sonnet 4.6):**
- `bb_pat_arbno.cpp` — BROK-2, adapted from 713c581 TEXT arm (r14d cursor, `call child_lbl` with `rdi=r12`, BINARY=bomb). Pre-build via `pre_build_children_text` scanning IR_SCAN subgraphs. Status: **TEXT ARM EXISTS, needs verification**.
- All other 713c581 originals dumped to disk as `bb_binop_gen.cpp`, `bb_seq.cpp`, `bb_to_by.cpp`, `bb_limit.cpp`, `bb_upto.cpp`, `bb_suspend.cpp`, `bb_case.cpp`, `bb_list_bang.cpp`, `bb_initial.cpp`, `bb_field.cpp`, `bb_if.cpp`, `bb_swap.cpp`, `bb_idx.cpp`, `bb_assign.cpp`, `bb_eps.cpp`, `bb_cset.cpp`, `bb_program.cpp`, `bb_proc.cpp`, `bb_clause.cpp`, `bb_proc_gen.cpp`, `bb_gen_alt.cpp` — NOT in Makefile, NOT compiled; they use old API (`BB_t*`/`bb_bin_t`/`bb_emit_asm_result`/`bb_node_id`) and serve as REFERENCE for reconstruction.

**Already correctly recreated (not lost):**
- `bb_pat_alt.cpp` → `x86_pair_loop()` ✓  
- `bb_pat_cat.cpp` → `x86_pair_loop()` ✓  
- `bb_pat_capture.cpp` → `flat_drive_capture` inline ✓  
- `bb_match.cpp`, `bb_subject.cpp`, `bb_scan_stmt.cpp` — all real ✓

### Recovery steps (ordered by language need)

**SNOBOL4 patterns:**
- [~] **REC-1 — `bb_pat_arbno.cpp` (BROK-2) TEXT arm working.** `pre_build_children_text` correctly finds child via `az->inner->entry`; child built as `sno_flat_c0_α`; `bb_pat_arbno_str()` calls it with `rdi=r12`. Gate: 052/054 m4 PASS. NOTE: child epilogue writes `[r12+0]=99` on fail — may corrupt SUBJECT slot. Verify with 054 (ARBNO+ALT).
- [ ] **REC-2 — `bb_pat_arbno.cpp` BINARY arm.** Convert the 713c581 BINARY arm (in `bb_arbno.cpp` reference copy) to x86() API: `x86_bomb` placeholder currently. Requires: `bb_slot_claim` for saved/depth/stack, child pre-built via `pre_build_children` (`bb_build_flat`), x86() body for α/β/done/pop/restore. Gate: 052/054 m3 PASS (currently works via rt_scan fallback; BINARY arm needed for true native pattern).

**Icon/Raku:**
- [ ] **REC-3 — `bb_to_by.cpp` (207 lines).** IR_TO_BY (Icon `lo to hi by step`). Reference in `src/emitter/BB_templates/bb_to_by.cpp`. Convert `BB_t*`→`IR_t*`, `bb_bin_t`→`x86()`, add to Makefile + dispatch. Gate: Icon to-by test.
- [ ] **REC-4 — `bb_seq.cpp` (358 lines).** IR_SEQ compound-statement sequence (Icon/Raku). Reference in `src/emitter/BB_templates/bb_seq.cpp`. Convert API. Gate: Icon proc-body test.
- [ ] **REC-5 — `bb_suspend.cpp` (111 lines).** IR_SUSPEND (Raku `take`). Reference in `src/emitter/BB_templates/bb_suspend.cpp`.
- [ ] **REC-6 — `bb_to_by.cpp`, `bb_limit.cpp`, `bb_upto.cpp`, `bb_list_bang.cpp`, `bb_binop_gen.cpp`** — remaining meaningful originals. Convert per RULES.md.

**Conversion recipe** (same for every REC-* box):
1. `BB_t * pBB` → `IR_t * pBB`; remove `bb_bin_t & bin` param
2. Remove `#include "bb_box.h"`, `#include "emit_bb.h"`; add current includes
3. `bb_emit_asm_result(str, bin)` → `bb_emit_x86(str)`
4. `bb_node_id(pBB)` → `_.nid`
5. `bytes(...)` / `u32le(...)` / `bb_bin_t` blocks → `x86_bomb(...)` for now (BINARY arm last)
6. `[r10]` cursor → `r14d`; `movabs &Σ` → `r13`; `movabs &Σlen` → `r15d`
7. Add to Makefile `RT_PIC_SRCS` and compile rule; add dispatch to `emit_core.c`; add decl to `bb_templates.h`

**Testing protocol for ALL recovery rungs:** No testing until ALL three modes are wired. Run:
```bash
bash scripts/test_smoke_snobol4.sh          # shows m2 / m3 / m4 counts
SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh
bash scripts/test_snobol4_pat_rung_suite.sh  # shows M2=N M4=N per rung
```

---

## 🔴 TEMPLATE-REVAMP-2 — Mass Hygiene Conversion Ladder

**Hygiene rules (from RULES.md):**
- Every byte of x86 lives in a template function — no helpers outside `BB_templates/` that return opcode bytes
- No `BB_t*` / `bb_bin_t` / `bb_emit_asm_result` / `bb_node_id()` anywhere
- No `pBB->value|counter|state` absolute slot emission — use `[reg+off]` ζ-frame
- `pBB->ival/sval/dval` → `_.op_ival/op_sval/op_dval` (emit-time IR metadata reads)
- `bb_node_id(pBB)` → `_.nid`; `bb_node_id(other)` → `other->id` field
- No x86_pair_loop() shim — write pair-table loop inline
- Four ports: α β γ ω only — no English synonyms
- No inline comments, no `//` — only 120-char `/*---*/` separator blocks
- No vstack (`rt_push_*`/`rt_pop_*`) for Icon stackless rule
- All per-box RW state → `[r12+off]` ζ-frame via `bb_slot_claim`
- All per-box RO constants → `[rip+disp]` via strtab/rodata labels

**Source of TEXT arm assembly for all conversions:** `git show 713c581:src/emitter/BB_templates/<f>.cpp` or `/home/claude/one4all/src/emitter/BB_templates/<f>.cpp`

---

### WAVE 1 — Trivial API fixes (no logic change)

- [x] **W1-1 `bb_call.cpp`** — `bb_node_id(lf)` → `lf->id`; `bb_node_id(owner)` → `owner->id`. Fix the 2 OLD_API refs. Gate: build clean.
- [x] **W1-2 `bb_gather.cpp`** — `bb_node_id(pBB)` → `_.nid`. Gate: build clean.
- [x] **W1-3 ALL `bb_builtin*.cpp`** (9 files) — `pBB->ival` → `_.op_ival`, `pBB->sval` → `_.op_sval`, `pBB->dval` → `_.op_dval`. Mass sed. Gate: build clean + Prolog smoke unchanged.

---

### WAVE 2 — SNOBOL4 critical bombs (pattern system)

- [ ] **W2-1 `bb_match.cpp`** — bomb: "subject/start slot not promoted". Fix: driver `flat_drive_match` must claim and promote the subject/start slot before dispatch. Cherry-pick TEXT arm from one4all. Gate: rung M2 unchanged, M4 scan tests advance.
- [ ] **W2-2 `bb_subject.cpp`** — bomb: "subject slot not promoted". Fix: `flat_drive_subject` slot promotion. Cherry-pick TEXT arm. Gate: same.
- [ ] **W2-3 `bb_pat_capture.cpp`** — bomb: "start slot not promoted". Fix: `flat_drive_capture`. Cherry-pick TEXT arm. Gate: same.
- [ ] **W2-4 `bb_scan_stmt.cpp`** — 3 bombs: TEXT non-literal pattern. Cherry-pick TEXT arm from one4all (SNOBOL4 scan statement driver). Gate: rung 038–057 M4 advance.
- [ ] **W2-5 `bb_gvar_assign.cpp`** — 5 bombs: descr arm + other shapes. Cherry-pick TEXT arm from one4all. Gate: SNOBOL4 smoke M4 unchanged or better.
- [ ] **W2-6 `bb_keyword.cpp`** — 2 bombs: no-slot arm. Cherry-pick TEXT arm from one4all (`NV_GET_fn` → `rt_nv_get`, register updates). Gate: keyword tests.
- [ ] **W2-7 `bb_pat_arbno.cpp`** — 2 bombs: no-child-label + BINARY arm. BINARY: cherry-pick from one4all and convert bytes() to x86() in-band records. Gate: 052/054 M3+M4 PASS.

---

### WAVE 3 — SNOBOL4 scan primitives (9 files, all identical bomb pattern)

Each: cherry-pick TEXT arm from one4all, update runtime fn names (`NV_GET_fn→rt_nv_get` etc.), update registers (`r10→r14d`), x86() BINARY arm or bomb.

- [ ] **W3-1 `bb_scan_any.cpp`** — needs literal cset arg + descr flat-chain
- [ ] **W3-2 `bb_scan_bal.cpp`** — needs nonempty bracket-free literal
- [ ] **W3-3 `bb_scan_find.cpp`** — needs nonempty literal needle ≤32 chars
- [ ] **W3-4 `bb_scan_many.cpp`** — needs literal cset arg + descr flat-chain
- [ ] **W3-5 `bb_scan_match.cpp`** — needs literal string arg + descr flat-chain
- [ ] **W3-6 `bb_scan_move.cpp`** — needs literal integer arg + descr flat-chain
- [ ] **W3-7 `bb_scan_pos.cpp`** — needs literal positive n + descr flat-chain
- [ ] **W3-8 `bb_scan_tab.cpp`** — needs literal positive n or sibling
- [ ] **W3-9 `bb_scan_upto.cpp`** — needs literal cset arg + descr flat-chain

---

### WAVE 4 — Icon variable/value bombs

- [ ] **W4-1 `bb_var.cpp`** — unhandled arm. Cherry-pick TEXT arm from one4all (`call rt_nv_get@PLT → jmp γ / jmp ω`). Gate: Icon var tests.
- [ ] **W4-2 `bb_var_frame.cpp`** — needs gvar flat-chain + own slot. Also fix `pBB->ival/dval` → `_.op_*`. Gate: Icon nested proc tests.
- [ ] **W4-3 `bb_var_frame_ref.cpp`** — same as W4-2. Gate: same.
- [ ] **W4-4 `bb_var_global.cpp`** — needs descr flat-chain + own slot. Cherry-pick TEXT arm. Gate: Icon global var tests.
- [ ] **W4-5 `bb_return.cpp`** — needs descr flat-chain. Cherry-pick TEXT arm from one4all. Gate: Icon return tests.
- [ ] **W4-6 `bb_assign_local.cpp`** — needs descr flat-chain + rhs slot + varslot. Gate: Icon assign tests.
- [ ] **W4-7 `bb_assign_frame.cpp`** — gvar flat-chain only + `pBB->ival` cleanup. Gate: Pascal frame tests.
- [ ] **W4-8 `bb_assign_frame_ref.cpp`** — same as W4-7. Gate: same.
- [ ] **W4-9 `bb_to.cpp`** — needs static int operands. Cherry-pick TEXT arm from one4all (static lo/hi arm; dynamic arm stays bombed). Gate: Icon to-pump tests.
- [ ] **W4-10 `bb_iterate.cpp`** — IR_LIST_BANG slot missing. Cherry-pick TEXT arm from one4all (string-split iterator). Gate: Icon iterate tests.

---

### WAVE 5 — Icon binop bombs (all shape-mismatch defensive guards)

Each: the bomb fires when the dispatcher sends an unrecognized shape. Cherry-pick TEXT arm, handle the shape or bomb loudly with shape description.

- [ ] **W5-1 `bb_binop_arith.cpp`**
- [ ] **W5-2 `bb_binop_relop.cpp`**
- [ ] **W5-3 `bb_binop_concat_slot.cpp`**
- [ ] **W5-4 `bb_binop_gvar_arith.cpp`**
- [ ] **W5-5 `bb_binop_gvar_arith_slot.cpp`**
- [ ] **W5-6 `bb_binop_gvar_relop.cpp`**

---

### WAVE 6 — Prolog bombs

- [ ] **W6-1 `bb_cell_unify.cpp`** — unadmitted operand shape. Extend admit conditions or bomb loudly.
- [ ] **W6-2 `bb_cell_choice.cpp`** — unadmitted choice shape. Same.
- [ ] **W6-3 `bb_cell_call.cpp`** — unadmitted call shape. Same.
- [ ] **W6-4 `bb_callee_frame.cpp`** — unadmitted callee shape. Same.

---

### WAVE 7 — Remaining misc bombs

- [ ] **W7-1 `bb_alt.cpp`** — needs ≤5 literal arms (descr flat-chain). Extend arm count or bomb louder.
- [ ] **W7-2 `bb_call_write_slot.cpp`** — write(non-slot arg). Extend or bomb.
- [ ] **W7-3 `bb_gen_scan.cpp`** — leave glue without regs. Cherry-pick TEXT arm.

---

### Conversion recipe (every file)

```
1. Open one4all or git show 713c581 for TEXT arm
2. Strip: BB_t*→IR_t*, bb_bin_t, bb_emit_asm_result, bb_node_id→_.nid
3. BINARY: convert bytes()/u32le() → x86() in-band records, OR bomb
4. Registers: [r10]→r14d (cursor δ), movabs&Σ→r13, movabs&Σlen→r15d
5. Runtime fns: NV_GET_fn→rt_nv_get, rt_push_str naming updates
6. pBB->ival→_.op_ival, pBB->sval→_.op_sval, pBB->dval→_.op_dval
7. RO data: .section .data labels OR strtab_label() for strings
8. RW state: bb_slot_claim(N) → [r12+off] ζ-frame
9. Build: bash scripts/build_scrip.sh
10. Gate: run the relevant test before commit
```

**Order of execution:** W1 first (trivial, validates build stays clean), then W2 (SNOBOL4 unblocking), then W3-W7 in order. Each wave is independently committable.

---

### REVAMP-2 STATUS UPDATE (post-W1 audit)

**Key finding:** All 40 bombs are ADMISSION GUARDS — every file has real x86() code above the bomb; the bomb fires when a shape reaches the template that doesn't satisfy current admission criteria. No file has "zero implementation." This changes the nature of the remaining work from "write from scratch" to "extend admission criteria or fix drivers."

**W1: DONE.** `bb_node_id→_.nid` (bb_call, bb_gather); `pBB->ival/sval/dval→_.op_ival/op_sval/op_dval` (13 files). Zero old-API refs remaining in compiled templates.

**W2 status:**
- W2-1/2/3 (match/subject/capture): templates complete with real code. Bombs = driver-side slot-promotion guard. Driver (emit_bb.c flat_drive_*) correctly promotes slots; bombs only fire on abnormal paths.
- W2-4 (scan_stmt): TEXT non-literal arm genuinely pending (needs native PB-RB scan graph — full pattern architecture). BINARY arm complete.
- W2-5 (gvar_assign): 5 bombs = admission guards for unhandled rhs shapes. 6 arms complete (lit_s, lit_i, var, int-binop, concat, call-result).
- W2-6 (keyword): 2 bombs = admission guards (no-slot and unsupported keyword). 4 keywords complete (subject, pos, null, fail).
- W2-7 (pat_arbno): TEXT arm done. BINARY arm = bomb.

**W3:** All 9 scan_* NOT in one4all. Need Icon canonical `refs/jcon-master/` + `refs/icon-master/src/runtime/fstranl.r`. Each file has 1 bomb guard; real x86() code pending for each shape.

**W4:** one4all TEXT arms use `rt_nv_get`/`rt_push_null` (vstack — FORBIDDEN per RULES). Current files are AHEAD of one4all. Bombs are admission guards; files not in one4all (var_frame, var_frame_ref, var_global, assign_local) were created post-713c581 with x86() API directly.

**W5/W6/W7:** All admission guards. Real x86() code exists (10–33 calls per file). Each bomb catches an unrecognized shape dispatched by the driver.

**Revised action plan — ordered by impact:**
- [ ] **ACT-1** `bb_pat_arbno` BINARY arm: convert one4all BINARY arm (bytes()/u32le() → x86() in-band 'E'/'F' records). Gate: 052/054 M3 PASS.
- [ ] **ACT-2** Extend Icon canonical `refs/` for W3 scan_* implementations. Restore: `git clone https://TOKEN@github.com/proebsting/jcon refs/jcon-master && git clone https://TOKEN@github.com/gtownsend/icon refs/icon-master`. Then implement each scan box against `fstranl.r`.
- [ ] **ACT-3** `bb_keyword` — add `&anchor`, `&maxno`, `&rtracing` and other SNOBOL4 keyword arms.
- [ ] **ACT-4** `bb_scan_stmt` TEXT non-literal arm — requires full native PB-RB pattern graph, blocked on scan architecture.
- [ ] **ACT-5** Shape-by-shape extension of W5/W6 admission criteria as new test programs expose them.

---

### X86-ONE + S-ASM ABOLITION (SCRIP 47883c4 + 68ba77c)

**ONE x86() function** (`x86_asm.h`): `x86(mnem, xop a={}, b={}, c={}, d={})`. Operands are strings that read like Intel asm; `xop` implicit ctors absorb const char*/int/long/uint64_t/std::string (via 16-slot keep ring). Parser classifies REG/IMM/PORT/ILBL/FR32/FR64/RSP64/MEMIND/MEMIDX8/R13RCX/R10MIR/RIPSEAL/SYM (space-normalized), ONE switch dives per opcode → proven byte encoders. PORT_*/FR/FRQ/L/RSP/F64 are string producers. TEXT-only forms: "label", "comment", "directive", "raw", "ins1/ins2/ins3/Lins1/Lins2" (passthrough), SYM-target jmp/jcc/call, "movsd"+f64.

**s_*asm DELETED** from the entire tree: dead JVM/JS/NET/WASM arms purged (12 files, 949 calls); BB + XA templates fully migrated; definitions and _c wrappers removed from emit_str.h/.cpp. 105 files, −2429 lines.

**Next refinement (optional):** ins2 passthrough sites still carry joined operand strings ("rax, [rip+...]") — converting them to true parsed form (`x86("mov","rax","[rip+lbl]")`) per-file unlocks BINARY for those TEXT-only arms.

**Gates at 68ba77c:** smoke m2 7/7 HARD, m3 6/6, m4 6/6; rung M2 18 / M4 17 (053 pre-existing FAIL-M2, 054 FAIL-M4 frame-corruption open).

---

## HANDOFF (session end — X86-ONE + S-ASM abolition complete)

**Repos at handoff:** SCRIP `68ba77c`, .github `c07a03e0`, both pushed. Working tree clean.

**Rebuild + verify from cold:**
```
cd /home/claude/SCRIP
bash scripts/build_scrip.sh                          # → OK scrip built
rm -f out/libscrip_rt.so obj/*.o && make libscrip_rt # → Built: out/libscrip_rt.so
bash scripts/test_smoke_snobol4.sh                   # expect m2 7/7 HARD, m3 6/6, m4 6/6
bash scripts/test_snobol4_pat_rung_suite.sh          # expect PASS-M2=18 FAIL-M2=1, PASS-M4=17 FAIL-M4=1 SKIP-M4=1
```
(053 FAIL-M2 + SKIP-M4 pre-existing; 054 FAIL-M4 = ARBNO child-epilogue frame-corruption, open.)

**What this session delivered (read these commits first):**
1. `ad430d3` PURGE — 22 dead old-API files deleted (content lives at 713c581/one4all).
2. `b3327fe`+ bb_pat_arbno TEXT arm restored; rung 052 PASS-M4.
3. `10903d6` pair-table recovery: bb_pat_cat/alt/conj/ite with inline pair iteration (no shims).
4. `6c0653e`+`703042c` REVAMP-2: zero old-API/vstack/pBB-field violations in all 47 compiled templates. 40 bombs remain = ADMISSION GUARDS ONLY (every file has real x86() code above its bomb).
5. `47883c4` X86-ONE: ONE x86(mnem, xop a,b,c,d) — operand strings parsed like Intel asm, one switch per opcode, routed to proven encoders. PORT_*/FR/FRQ/L/RSP/F64 are string producers.
6. `68ba77c` S-ASM ABOLISHED: zero s_*asm in the tree. Dead JVM/JS/NET/WASM arms purged. BB+XA migrated.

**Architecture law going forward:** all instruction emission flows through the ONE `x86()` in `src/emitter/BB_templates/x86_asm.h`. New shapes = new parse kinds + opcode-switch routes there, never new functions.

**Next-session menu (in priority order):**
- [ ] **NEXT-1** ins2→parsed: convert `x86("ins2","mov","rax, [rip+...]")` passthrough sites to true split operands per-file (unlocks BINARY for those TEXT-only arms). Mechanical per-file; verify with asm diff (`git stash` baseline method).
- [ ] **NEXT-2** 054_pat_arbno_alt FAIL-M4: child β-epilogue writes `[r12+0]=99` clobbering SUBJECT slot on fail path — trace with the 052-vs-054 asm diff.
- [ ] **NEXT-3** ACT-2: W3 nine Icon scan_* shapes against `refs/icon-master/src/runtime/fstranl.r` (refs cloned, in .gitignore).
- [ ] **NEXT-4** ACT-3: bb_keyword &anchor etc.
- [ ] **NEXT-5** ACT-1: bb_pat_arbno BINARY arm (needs ζ-frame rewrite, not deque port).

**Facts that cost time to learn (do not re-derive):**
- one4all == 713c581: old API + forbidden vstack; NOT a source for current-architecture files.
- All bb_scan_*/bb_var_frame*/bb_cell_*/bb_gvar_assign etc. were born post-713c581 on x86() API — git has no cleaner version.
- Brace-stripping platform arms REQUIRES string-literal-aware scanning (first attempt broke bb_lit on `{`/`}` inside strings).
- Old s_L1asm semantics: label arg ALREADY contains ':', single line — Lins1/Lins2 match this exactly.
- emit_fmt has ONE static buffer — never two emit_fmt in one x86() call; FR/FRQ/L/RSP/F64/x86_strkeep use rotating rings for this reason.
