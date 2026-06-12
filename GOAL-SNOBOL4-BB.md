**SESSION WATERMARK — 2026-06-12 · Sonnet 4.6 · SCRIP=70b9977. _wγ/_wω partial fix landed: `flat_drive_capture` stop-terminated BREAK→LIT→ARBNO→ASSIGN_COND chain now drives arms correctly via `flat_drive_cat_arms(NULL, stop_arms, stop_n, ...)` guarded by `stop_has_arbno`; `flat_drive_cat_arms` null-pBB guard fixed (nc==0 only); `pre_build_children_text` ASSIGN_COND branch walks full γ-chain so ARBNO gets pre-built. Qize proc body: `Qize_c0_wγ`/`_wω` DEFINED ✅ gates green. REMAINING GAP: `sno_flat_c0_wγ`/`_wω` still undefined — spurious `sno_flat_c0_α` child emitted by `gvar_chain_prebuild_children_text` finding Qize proc's SCAN in `g->all[]` of the whole-program flat graph, but `codegen_gvar_flat_chain_body` starting from sno_flat entry never reaches the ARBNO box → `_wγ`/`_wω` never defined. Fix: in `gvar_chain_prebuild_children_text`, after emitting the child body for an ARBNO, check whether a walk from `g->entry` would actually reach that ARBNO; if not, skip the child build. OR: after emitting each child body, immediately emit the ARBNO box inline. Probe: `DEFINE('Qize(S)part') :(e) Qize S ? ((BREAK('.') '.' ARBNO(NOTANY('.'))) . part) RPOS(0) :F(FRETURN) Qize=part :(RETURN) e OUTPUT=Qize('a.b.c')` — should link and print `b.c`. GATES: smoke 7/7/7 HARD · pat-rung 19/19/19 no-SKIP · fence HARD.**

---

## 🔴🔴🔴 TOP PRIORITY (Lon 2026-06-08) — GROUND-ZERO PATTERN BUILDING THROUGH RT FUNCTIONS · NO BB_INVARIANT

**THE priority.** Every pattern BUILT at runtime via `rt_pattern_build` / `rt_pattern_stitch_cat` / `rt_pattern_stitch_alt` (`src/runtime/pattern_match.c:748/756/762`). All 8 `bb_pattern_*.cpp` builders converted — `ins*` = 0 ✅. All D7 rungs DONE (D7-RB-1 ✅ D7-RB-2 ✅ D7-RB-2b ✅ D7-RB-3 ✅); full ladder + design in `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`. BB_INVARIANT/REF_INVARIANT excluded — ground zero only. GATE: smoke 7/7/7 · pat-rung m2==m3==m4 no-SKIP · corpus non-decreasing all modes · fence HARD.

---

## ⛔ SESSION DIRECTIVE — modes 2/3/4 CO-EQUAL HARD GATES (Lon 2026-06-08: "modes 3 and 4 are IDENTICAL"). See `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md` D7.

## ⭐ PIVOT (Lon 2026-06-07) — BUILDERS REPLACE SM · DT_P SEAL-ON-MATCH

Directives: (1) BB_INVARIANT/REF_INVARIANT — quit using. (2) No constant-folding. (3) BBs replace ALL SM. (4) ✅ DONE `da96b66`: bb_pat_* → bb_match_*. BUILDER TAXONOMY: `bb_pattern_nullary` · `_unary_i` · `_unary_s` · `_unary_p` · `_stitch` · `_capture` · `_defer`. DT_P MEMORY MODEL: build-unsealed, seal-on-match. `--dump-bb` V2/V2b live (`8795a2c`).

## 🔴🔴 #0 PRIORITY — OWNED 5-STAGE BUILD

Master ladder + design decisions: `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`. Architecture of record: `.github/ARCH-SNOBOL4.md`. RoE: BBs/XAs only through templates; ONE template MAY serve multiple IRs; NO runtime calls without ledger stamp; probe-first vs sbl; one rung = one commit; m2/m3/m4 co-equal hard gates; corpus non-decreasing HARD.

## MODE 4 BUG LADDER (specimen record for the S-rungs)

Inventory: smoke m4 **7/7** · pat-rung m4 **19/19 no-SKIP** · broad m4 corpus **155/280** · beauty m4 **1/17**.

- [ ] **M4-CRASH** — `scrip --compile` must never abort/segfault: 29 corpus SKIPs + 4 beauty emit-crashes. First specimen: literal-subject + non-literal-pattern → `rt_scan` BOMB. Enumerate every SKIP by FATAL bucket, fix each.
- [ ] **M4-FENCE** — ~10 corpus fails (061/062/064/066/100/101/103/108/110/112). FENCE + FENCE(pattern) + fence-via-pattern-var. Manual p.204: FENCE matches null L→R, fails if retreated through.
- [ ] **M4-ONESHOT** — probe: `'aab' ? SPAN('ab') . A 'b' . B` → sbl `:`, m4 `aa:b`. Fix: β→ω on both span twins, audit ANY/NOTANY/BREAK/LEN/TAB/RTAB/POS/RPOS β arms.
- [ ] **M4-CAPTURE-COND** — probe: `V='unset'; S='ab'; S 'a' . V 'x' :F(NO)` → m4 `nomatch a`, sbl `nomatch unset`. `rt_cap_assign_cursor` discards `is_imm` and NV_SET_fns immediately; deferred machinery exists only on shim path.
- [ ] **M4-STARVAR** — 070/071/073/075/061 + 053 class. PB-RB-6: BB_PAT_BUILD for `*E`/`$NAME`/pattern-valued var.
- [ ] **M4-ARBNO-REENTRY** — matched ARBNO instance's remaining alternatives not re-enterable on backtrack: `ARBNO('ab'|'a') 'b'` on `'ab'`.
- [ ] **M4-DATA** — 091/092/093/094/095/096.
- [ ] **M4-DEFINE** — 084/088/089.
- [ ] **M4-BUILTIN** — 076/077/081/082/097/006/030/020/014/015.
- [ ] **M4-BEAUTY** — beauty subsystems 16 fails: link=5, diff=7, emit=4.
- [ ] **M4-REPL-NATIVE** — replacement form natively (PB-RB-7). Probe: `S 'b' = 'X'` → `aXc`.

## ⛔ FACT RULE — LANGUAGE-BLIND BB/XA TEMPLATES (Lon, 2026-06-03)

**No language-specific logic in any BB or XA C++ template.** All delineated operations are enveloped in unique BBs; each BB does NOT have varying runtime behavior depending on language. Templates dispatch on IR shape and representation flags only. FORBIDDEN inside `src/emitter/BB_templates/` and `src/emitter/XA_templates/`: language enums/guards (`IR_LANG_*`, `LANG_*`, `is_<lang>`), language-named template functions/files/dispatch arms, and hardcoded language-builtin names. Behavior that differs by language belongs in the runtime (by-name dispatch) or in LOWER (a different IR shape → its own unique BB) — never in a template arm. Inventory: `SCRIP/BB-TEMPLATES-LANG-AUDIT.md` (XA scanned clean 2026-06-03); fix ladder: LB-* in `GOAL-PASCAL-BB.md`. COMPLETION TEST: the audit's Tier-1 grep over `BB_templates/` + `XA_templates/` returns 0 sites.


## ⛔ TEMPLATE SPEC v2 (Lon 2026-06-04) — REGENERATE, DON'T PATCH

No local variables · ONE return per PLATFORM returning ONE concatenated string · IF()/FOR() string functions for all conditionals/loops · ONE source line == ONE asm line · REAL Greek α β γ ω (no PORT_ALPHA/BETA/GAMMA/OMEGA spellings) · no MEDIUM_TEXT/MEDIUM_BINARY at template top level (hide in helper functions) · zero emit_fmt() · zero C comments [separator status vs RULES.md: confirm with Lon] · zero blank lines · **ONE-IR-ONE-LOGIC (Lon 2026-06-04):** a template may serve SEVERAL IR kinds (near-identical shapes parameterized — the `bb_lit_scalar` grouping), and most are one-to-one; but ONE IR kind carrying MULTIPLE distinct four-port BB logics inside one template is FORBIDDEN — a bb_*.cpp that obviously needs it is broken out by splitting the IR kind in LOWER into separate IR codes, each reaching its OWN template via its own `emit_core.c` dispatch case. N IR → 1 BB allowed; 1 IR → 1 BB the norm; 1 IR → N BB never. **EMIT-BLIND / NO NEIGHBOR INQUIRY (Lon 2026-06-04):** a template reads ONLY its own emit context `_` (own labels, own ζ-slots, the `_.op_*` metadata the driver prepared) — it NEVER dereferences a neighboring IR node: no `pBB->α/β/γ/ω->t` kind tests, no neighbor `->ival/sval/dval` value reads, no neighbor kids/operand_aux walks, whether to ADMIT a shape or to CHOOSE an emission. A template inquiring about its neighbors is doing IR LOWERING inside the emitter — a design flaw in the lowering stage, not a template feature. The fix is always upstream: LOWER produces a DISTINCT IR shape per case (ONE-IR-ONE-LOGIC) and delivers operand values via `_.op_*`/ζ-slot offsets; the driver (`emit_bb.c`/`emit_core.c`) is where graph inspection lives. Scope: forbidden inside `src/emitter/BB_templates/` + `XA_templates/`. Separation of concerns: LOWER decides, templates emit. Each template is REGENERATED whole to this spec, not patched. Full directive + session state: `HANDOFF-2026-06-04-OPUS48-SNOBOL4-BB-HYGIENE-SWEEP-SPEC-V2.md`.

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
FORM:** a box's leading `α:` label (`s_1asm(std::string(_.lbl_α)+":")`  ) and comments (`s_comment(...)`) exist only
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

> **⭐⭐⭐ CORRECTED PATTERN ARCHITECTURE (Lon 2026-06-01).** A SNOBOL4 pattern is a graph of EMITTED BYRD-BOXES — `bb_box_fn` machine code — NOT a `PATND_t` or `tree_t`. `DT_P` = HEAD BLOCK = `{entry, OUTSIDE-γ slot, OUTSIDE-ω slot}`. Build = SPLICE (wire ports); no JIT-emit except for `*E`/EVAL/CODE. Seal at element granularity; wire at instance level. Runtime `STITCH_SEQ`/`STITCH_ALT` are the runtime twins of `wire_seq`/`wire_alt`. `BB_LINK` = pure-tail indirect-jump `jmp [r12+slot]` through ζ-frame; sets the universal seal-boundary external edge. Only needed when DT_P is a SHARED sealed head (not the current inline case).

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The AST→IR lowerer's SHARED SPINE is **ONE file** — `src/lower/lower.c` — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** for the co-located languages. **AMENDED (Lon 2026-06-04): the shared IR graph is the LANGUAGE-INDEPENDENT contract — LOWER splits per language.** Prolog's goal-role family now lives in `src/lower/lower_prolog.c` (`d6d93c6`; shared helpers de-static'd into `lower_internal.h`); remaining languages stay co-located in `lower.c` until Lon splits them out. The discipline below keeps concurrent sessions **conflict-free and mutually beneficial**:

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). One kind → one case → language arms inside. A language graduates to its OWN `lower_<lang>.c` ONLY by Lon's directive (Prolog: 2026-06-04), taking its whole role-family with it — never an ad-hoc fork.

3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language's arm.** A language owning its own `lower_<lang>.c` edits ONLY that file (plus lockstep scaffolding per rule 5) and never a peer's. This is what makes concurrent sessions' diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer's proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED (declared in `lower_internal.h`, defined in `lower.c`). ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit (it compiles `lower.c` + `lower_prolog.c` + the harness). Each cat's proof cases are ADDITIVE (append your own; never delete a peer's). Green = your arm wired right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c` (nor within any per-language lowerer file); (b) every case's language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

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


## ⭐⭐ REBUILT LADDER — PB-RB (CORRECTED PATTERN ARCHITECTURE)

`wire_seq`/`wire_alt` are shared LOCKSTEP helpers. All PB-RB gates mode 4 HARD. Open:

- [ ] **PB-RB-5** — Operand-variant element matchers (Fork A). `LEN(N)`/`SPAN(cvar)` etc.: existing `IR_PAT_LEN`/`IR_PAT_SPAN` box reads operand late from ζ-slot. NO builder box. Prove + mode-3 `S LEN(2)`, `S SPAN('abc')`.
- [ ] **PB-RB-6** — BB_PAT_BUILD for STRUCTURAL variance (Fork A/B). `*E`/`$NAME`/pattern-valued var.
- [ ] **PB-RB-7** — REPLACEMENT BB (ph.4) + SUBSTITUTION BB (ph.5). mode-3 `S 'b' = 'X'` → `aXc`.
- [ ] **PB-RB-CONV** — IR_SCAN convergence: retire dual shape once native chain covers corpus breadth.
- [ ] **PB-RB-OPT** — All-invariant BLOB freeze: collapse REF_INVARIANT+STITCH into ONE sealed blob. After correctness rungs done.
## BROK residue (eradication ✅ — git; fence 0 HARD in Setup)

- [ ] ARBNO child-β re-entry gap: a matched instance's remaining alternatives are not re-enterable on backtrack (`ARBNO('ab'|'a') 'b'` on `'ab'`); own rung.
- `bb_box_fn` typedef KEEPS `(void*,int entry)` — survivors rt.c:480/529/595 (C α-entry into DEFINE blobs); convert those to jmp-threading BEFORE touching the typedef.

## Architecture references

- Mode-2 oracle: `src/interp/IR_interp.c`
- Flat driver: `src/emitter/emit_bb.c` (`codegen_gvar_flat_chain_body`, `walk_bb_flat`)
- Template dispatch: `src/emitter/emit_core.c`
- Template dir: `src/emitter/BB_templates/bb_pat_*.cpp`
- Lowering: `src/lower/lower.c` + `lower_prolog.c` + `lower_program.c`
- Bomb infra: `src/emitter/emit_str.{cpp,h}`
- Audit gate: `scripts/audit_m3_native_binary_arms.sh`
- M4 statement anatomy: per-statement `IR_SUCCEED` landing nodes (`lower_program.c:514-611`); labels registered land[i]; γ_tgt/ω_tgt = U|S/F-goto landing or fall-through — HARD graph edges at lower time → direct `jmp` in flat emission; computed/undefined gotos via `IR_GOTO`. NO setjmp/longjmp in the SNOBOL4 path.
- M4 scan routing (`emit_bb.c flat_drive_scan_stmt`): literal pattern → `bb_scan_stmt` literal arm → `rt_scan_lit`; non-literal + named-var subject + NO repl → `flat_drive_scan_native` (native bb_pat_* chain); everything else → `bb_scan_stmt` general arm → `rt_scan` shim.

## ⏸ PARKED — OUT OF MODE-4 SCOPE

- **M2-ARBNO-SHY** — m2 ARBNO greedy vs sbl shy; m4 already matches sbl — mode-2-only bug.
- **SR-2** save/restore→ζ-frame migration — parked.
- **LOWER2 BOX LADDER** — parked.
- **RECOVERY / REC-*** rungs (m3 BINARY arms, Icon/Raku boxes) — removed.

## Session log

**Watermark (D7 B-ladder B0–B6 ✅ B7a–B7b ✅ D7-RB-1–RB-2b ✅; SCRIP=4c65b17; 2026-06-12 prior session Sonnet 4.6).** All D7 rungs done. pat-rung 19/19/19 no-SKIP. _wγ/_wω root cause diagnosed; fix partially landed in 70b9977 (Qize proc fixed; sno_flat_c0_wγ/wω remaining gap documented in watermark above).

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64   # SPITBOL oracle: /home/claude/x64/bin/sbl -b file.sno
```

Gates — modes 2/3/4 CO-EQUAL HARD:
```bash
bash scripts/test_smoke_snobol4.sh                                    # m2/m3/m4 7/7/7 HARD
bash scripts/test_snobol4_pat_rung_suite.sh                           # M4: 19/19 no-SKIP target; M2/M3 informational
SCRIP=$PWD/scrip bash scripts/test_mode4_only_corpus_snobol4.sh       # 155/280 floor; prints FAIL+SKIP names
bash scripts/test_gate_em_beauty_subsystems_mode4.sh                  # 1/17 floor
bash scripts/test_gate_sno_pat_reg.sh                                 # static source fence (mode-agnostic): HARD
```

## X86-ONE + S-ASM ABOLITION (SCRIP 47883c4 + 68ba77c)

**ONE x86() function** (`x86_asm.h`): `x86(mnem, xop a={}, b={}, c={}, d={})`. Operands are strings that read like Intel asm; `xop` implicit ctors absorb const char*/int/long/uint64_t/std::string (via 16-slot keep ring). Parser classifies REG/IMM/PORT/ILBL/FR32/FR64/RSP64/MEMIND/MEMIDX8/R13RCX/R10MIR/RIPSEAL/SYM (space-normalized), ONE switch dives per opcode → proven byte encoders. PORT_*/FR/FRQ/L/RSP/F64 are string producers. TEXT-only forms: "label", "comment", "directive", "raw", "ins1/ins2/ins3/Lins1/Lins2" (passthrough), SYM-target jmp/jcc/call, "movsd"+f64.

---

**Architecture law:** all instruction emission flows through the ONE `x86()` in `src/emitter/BB_templates/x86_asm.h`. New shapes = new parse kinds + opcode-switch routes there, never new functions.

**Open refinement (X86-ONE):** ins2 passthrough sites still carry joined operand strings (`"rax, [rip+...]"`) — converting them to true parsed form (`x86("mov","rax","[rip+lbl]")`) per-file unlocks BINARY for those TEXT-only arms. Mechanical per-file; verify with asm diff (`git stash` baseline method).

**Facts that cost time to learn (do not re-derive):**
- one4all == 713c581: old API + forbidden vstack; NOT a source for current-architecture files.
- All bb_scan_*/bb_var_frame*/bb_cell_*/bb_gvar_assign etc. were born post-713c581 on x86() API — git has no cleaner version.
- Brace-stripping platform arms REQUIRES string-literal-aware scanning (first attempt broke bb_lit on `{`/`}` inside strings).
- Old s_L1asm semantics: label arg ALREADY contains ':', single line — Lins1/Lins2 match this exactly.
- emit_fmt has ONE static buffer — never two emit_fmt in one x86() call; FR/FRQ/L/RSP/F64/x86_strkeep use rotating rings for this reason.
- `operand_aux` is PER-GRAPH (`bbg->operand_aux[]`): any code walking a SUB-graph (ARBNO inner, pattern graphs) must switch `g_emit_cfg` to that graph first (save/restore idiom, cf. emit_bb.c:1477) or every aux lookup silently misses.
- Flat emission of driver-owned kinds (`bb_kind_is_driver_owned`: PAT_CAT/PAT_ALT/PAT_FENCE/GCONJ) starts at the JOIN node; `wire_alt`/`wire_seq` return α_out = FIRST ARM — always `ir_skip_alt_arms` before a single-node walk.
- BROK-0 probe method: fprintf markers + smokes + broker + full 280-corpus grep proves call-site deadness cheaply; runners swallow stderr, so validate probe plumbing with one direct `--run` first.
- Broad-corpus gate counts are container-sensitive — always stash-baseline before treating a count as a regression.
- ALWAYS grep-count after any perl/python batch edit and re-anchor with str_replace on miss (a trailing \n inside a line-match silently deleted a lower.c line once).
- SPITBOL stream primitives are ONE-SHOT on rematch (SPAN/BREAK/ANY/NOTANY/LEN/TAB/RTAB/POS/RPOS); only BREAKX/ARB/ARBNO/BAL generate rematch alternatives (manual BREAKX entry + Ch18; SNO-SPAN-BETA probe). Quickscan heuristics do NOT exist in SPITBOL (&FULLSCAN forced non-zero, p.123).
- Stream-fn by-var kind-split recipe = 13 sites + optional rt helper: IR.h end-of-SNO-block, scrip_ir names, lower kind-select (KEEP ival/dval flags verbatim), lower leaf-predicate, m2 case-label SHARE (byte-identical interp), is_pat_chain_elem, walk_bb_flat FILL case, emit_core dispatch, bb_templates.h, new template (faithful twin), Makefile ×2, prove_lower2 (+name +case), emit_per_kind_audit.
- `flat_drive_cat_arms(pBB=NULL, arms, nc, ...)`: pBB=NULL is now supported (nc==0 guard removed; tail trampolines emitted explicitly via emit_label_define_bb+emit_jmp_label when pBB==NULL). Use when stop-terminated γ-chain has ARBNO and no sentinel PAT_CAT node.
- `pre_build_children_text` ASSIGN_COND/IMM branch: uses operands[0] fallback + walks full γ-chain so ARBNO in capture child chains gets pre-built. Still misses ARBNO reachable via SCAN in `g->all[]` but not reachable from sno_flat entry — see watermark.
