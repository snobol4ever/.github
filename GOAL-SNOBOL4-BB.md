# GOAL-SNOBOL4-BB.md — SNOBOL4 Pattern BB Templates

## ▶ CURRENT PRIORITY — READ FIRST (2026-06-02): x86() TEMPLATE-REVAMP

Convert this language's BB templates to the **`x86()` self-encoding API** (one return per `PLATFORM_*`, pure
`x86(mnem,…)` concat, no `bb_bin_t`, pBB-free). The shared looping-box **keystone is LANDED at SCRIP
`origin/main`=`30e8422` — REBASE ONTO IT BEFORE CONVERTING ANY BOX** (internal-label + ζ-frame support lives in
the SHARED `x86_asm.h`; do not rebuild it or you collide).
- **START HERE:** `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` (rules R1–R13, divvy-up table, landed API `x86_begin()`/
  `L(n)`/`FR(off)`/`bb_slot_claim`, `x86_asm.h` vocabulary). **Reference:** `bb_pat_pos.cpp` (loop-free) +
  `bb_pat_span.cpp` (looping). **Recipe:** `HANDOFF-2026-06-02-OPUS48-SNOBOL4-BB-TEMPLATE-REVAMP-V3-KEYSTONE-POS-SPAN.md`.
- **STILL OPEN (shared):** the VARIABLE-LENGTH define/jmp-pair loop (combinators + FENCE pair path + Raku `bb_nfa`)
  — first to reach a combinator designs it once in the RULES-DRAFT.
- **YOUR BOXES:** `bb_pat_pos`✅ + `bb_pat_span`✅ + `bb_pat_abort`✅ + `bb_pat_tab`✅ + `bb_pat_atp`✅ +
  `bb_pat_arb`✅ + `bb_pat_defer`✅ + `bb_pat_fence`✅ + `bb_pat_break`✅ DONE (`x86_movimm32` / `mov32` encoder
  landed for TAB δ=r14d set; ARB uses `bb_slot_claim(8)` for its z/zo ζ-frame generator state; DEFER off
  `[r10]`→δ=r14d with the 16-byte-aligned `rt_defer_match` call preserved; FENCE single-shot save-δ-on-α/
  restore-on-β via `bb_slot_claim(4)`; BREAK+BREAKX looping, z/z_orig in `bb_slot_claim(8)` ζ-frame, internal
  labels plain L(0)/L(1) + BREAKX rescan L(2)/L(3), strchr with push/pop r10). Next loop-free leaf: NONE LEFT.
  Variable-length combinators (the STILL-OPEN define/jmp-pair design): `bb_pat_cat`, `bb_pat_alt`, `bb_match`,
  `bb_pat_fence` PAIR path (the with-children `FENCE(P)` form — the bare-FENCE primitive above is done).
- Edit only your boxes + their dispatch/decl lines; `x86_asm.h` edits are additive; `git pull --rebase` before push.
- (Full live status is in the **Watermark** near the end of this file.)

---

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

> **⛔⛔⛔ ACTIVE TOP PRIORITY — DE-NAME: NO `SNO`/`sno` IN EMITTER OR RUNTIME (Lon directive 2026-06-01). DO THIS
> NEXT, BEFORE more pattern dev.** Language-specific naming STOPS AT THE PARSER (frontend). The IR, the emitter
> boxes, the runtime helpers, and the lowerer are LANGUAGE-INDEPENDENT — **there is NO `BB_*`/`IR_*`/box/runtime
> identifier particular to a language.** Every `SNO`/`sno` prefix/infix/suffix in `src/emitter`, `src/runtime`,
> `src/lower`, `src/processor`, `src/driver` is STRIPPED (the symbol is removed; e.g. `bb_sno_match` → `bb_match`).
>
> **✅ STARTED (2026-06-01, Opus 4.8): `bb_sno_match` → `bb_match`** (the box created this session; the directive's
> named example). Renamed: file `bb_sno_match.cpp`→`bb_match.cpp` (git mv), `bb_sno_match`/`_str`→`bb_match`/`_str`,
> `flat_drive_sno_match`→`flat_drive_match`, `g_sno_match_*`→`g_match_*`, emit_core dispatch, Makefile, lower.c
> comment, de-SNO'd error strings. Gates GREEN + probe 2/2. The REST of the surface (below) is the next session.
>
> **THE LADDER (one box-cluster per slice, gate green each — mirror the BB→IR rename's slice discipline). Each
> strips the token; a file rename is `git mv` + Makefile (`RT_PIC_SRCS` line + per-`.o` rule) + every `#include`/
> call site + emit_core dispatch + comments/strings. Run the full gate suite (smoke SNOBOL4 m2 7/7 HARD + Icon m2
> 12/12 HARD + prove_lower2 65 + probes + sm_dead + concurrency + purity + g_vstack==0) after EACH slice.**
> - **DN-1 SUBJECT:** `bb_sno_subject`→`bb_subject` (file+sym+`_str`), `flat_drive_sno_subject`→`flat_drive_subject`,
>   `rt_sno_subject_load`→`rt_subject_load`, `g_sno_subject_slot`→`g_subject_slot` (read in `bb_match.cpp` — update
>   there too), `g_sno_subject_dbg_*`→`g_subject_dbg_*`, `Lsno_subj*`→`Lsubj*`. Touches bb_sno_subject.cpp, emit_bb.c,
>   emit_core.c, rt.c, bb_match.cpp, lower.c, prove_lower2.c.
> - **DN-2 SCAN:** `bb_sno_scan`→`bb_scan` (file+sym+`_str`), `flat_drive_sno_scan`→`flat_drive_scan`,
>   `rt_sno_exec_scan`→`rt_exec_scan`. (`bb_scan` is free — `gen_scan` is `bb_gen_scan`.) Touches bb_sno_scan.cpp,
>   emit_bb.c, emit_core.c, rt.c, bb_exec.c.
> - **DN-3 CHAIN:** `sno_flat_chain_build`/`_text`→`flat_chain_build`/`_text`, `codegen_sno_flat_chain_body`→
>   `codegen_flat_chain_body`, `sno_chain_*`→`chain_*` (arity/is_real/operand_refs/prebuild_children[_text]/resolve),
>   `sno_stmt_operand_refs`→`chain_stmt_operand_refs`, `sno_stmt_t`/`sno_prog_t`→`stmt_t`/`prog_t` (⚠ grep `stmt_t`
>   first for a collision), `g_sno_flat_chain`→`g_flat_chain` (emit_bb.c + emit_bb.h + bb_var.cpp), `sno_flat`
>   label-prefix→`flat`. Touches emit_bb.c, emit_bb.h, bb_var.cpp, scrip.c, driver. (These sit beside the Icon
>   `icn_flat_chain_*`/`icn_chain_*` twins — the generic names are free; the prefix-drop is the point.)
> - **DN-4 PROG / REF / MATCH-LIT:** `IR_SNO_PROG`→`IR_PROG` (IR.h enum + scrip_ir.c kind_names + emit_bb.c +
>   lower.c), `flat_drive_sno_program`→`flat_drive_program`, `flat_drive_sno_ref_invariant`→`flat_drive_ref_invariant`,
>   `rt_sno_match_lit`→`rt_match_lit` (rt.c), `g_sno_cur_func`→`g_cur_func` (bb_exec.c — grep collision first).
> - **DN-5 ASSIGN — ⚠⚠ COLLISION / MERGE DECISION (NOT a pure rename — needs Lon/judgment).** `bb_sno_assign`
>   stripped is `bb_assign`, which ALREADY EXISTS (the Icon assign box, `bb_assign.cpp`). This is exactly the
>   "no `BB_*` particular to a language" END STATE: IR_ASSIGN should be ONE box `bb_assign` that branches on
>   `operand kind` (lit-string / int-binop / var / concat — the SNOBOL arms) vs the Icon var-store arm, inside the
>   one template (the SHARED-LOWERER/EMITTER concurrency model already routes both via `case IR_ASSIGN`). So DN-5 is
>   a **box merge**, not a rename: fold `bb_sno_assign.cpp`'s arms into `bb_assign.cpp`, collapse the walk_bb_flat
>   `IR_ASSIGN` dispatch (currently SNO `α==IR_LIT_S|VAR|SEQ` → bb_sno_assign / `α==IR_BINOP` → bb_sno_assign_binop
>   vs Icon → bb_assign) into one box, rename `rt_sno_assign_*`→`rt_assign_*`, `flat_drive_sno_assign[_binop]`→
>   `flat_drive_assign[_binop]` (⚠ `flat_drive_assign` EXISTS — merge), `bb_sno_assign_var`/`_concat`/`_int`→ the
>   merged box's arms, `Lsno_dst/iname/name/src/str`→`L*`. bb_var.cpp's `bb_sno_assign_var`/`rt_sno_assign_var` refs
>   follow. **Do DN-5 LAST and with full context** — it is the architecture seam, not a sed.
> - **DN-6 RESIDUE:** strip leftover `sno` from `dump_sno`/`dump_sno_value` (prove_lower2.c → `dump_pat`/`dump_pat_value`,
>   grep collision), the dead-`sno_ring_to_tree` comment mentions, `has_non_sno` (scrip.c), and any `sno`/`SNO` token
>   in comments/strings of the touched files. Then a ZERO-CHECK: `grep -rnE '\b[A-Za-z_]*([Ss][Nn][Oo])[A-Za-z_]*'
>   src/emitter src/runtime src/lower src/processor src/driver` returns ONLY the EXCLUDED set below.
>
> **⛔ EXCLUDED — DO NOT TOUCH (these are NOT language-as-box-naming):**
> - **Snocone (a DIFFERENT language; `sno` is a substring of `snocone`, stripping it CORRUPTS the name):**
>   `snocone`, `_snoc_*`, `snoch`, `snotypes`, `lang_snocone`, `snocone_compile`, `snocone_driver`.
> - **The language-identity enum `IR_LANG_SNO`/`LANG_SNO`:** this is the tag the ONE shared lowerer branches on
>   (`switch (cx.lang)`), inherent to the unified-lowerer design (SHARED-LOWERER FACT RULE) — it is NOT a per-language
>   box/IR-kind. KEEP (it names the language, which the lowerer legitimately must know).
> - **Parser / frontend bridge (language-specific stops AT the parser, so these are fine):** `sno_parse_ast`,
>   `sno_parse_string_ast`, `sno_parse_define_proto`, `sno_add_include_dir`, `tree_to_sno`, `lower_sno`/`lower_sno.c`
>   (the AST→`.sno` SOURCE transpiler — a frontend/`--dump-sno` tool, not the IR lowerer), `LOWER_SNO_H`, `test_sno_*`.
> - **⚠ SEPARATE LARGER DECISION (flag for Lon — NOT in this ladder):** the SNOBOL RUNTIME-LIBRARY core in
>   `src/runtime/core` (`SNOBOL`, `SnoRt`, `SnoSaveEnt`, `SNO_INIT_fn`, `SNO_LIB`, `SNO_LINEBUF`, `SNO_LINE_SPLIT_AT`,
>   `SNO_LOOP_STACK_MAX`, `SNO_SAVE_MAX`, `g_sno_save`/`_top`) IS the SNOBOL execution model itself. Stripping `SNO`
>   there yields vague/colliding names (`INIT_fn`, …) and is a runtime-UNIFICATION question, not a rename. The IR/
>   emit/BB-facing surface (the ladder above) is unambiguous and goes FIRST; the core-runtime de-SNO awaits Lon's
>   call on whether/how the SNOBOL runtime library merges.

> **🚧 ACTIVE RUNG — STOP-AND-DEV (Lon directive 2026-05-31). READ THIS FIRST.**
> The next work is the **5-phase SNOBOL4 statement execution, 100% through BBs**: SUBJECT → PATTERN → MATCH →
> REPLACEMENT → REPLACE, built as the **SESSION RUNG #0 — SBL-PAT-BB** ladder (**PB-0 … PB-OPT**, in this file
> below). **DO THIS DEV FIRST.** ⛔ Do **NOT** start climbing test/rung ladders (prove_lower2 rungs, smoke-floor
> bumps, corpus-parity sweeps, per-language bring-up) until the 5-phase pattern execution is FULLY NATIVE through
> BBs. **PB-RB-1 (REF_INVARIANT) + PB-RB-2 (matcher-element four-port ABI, SPEC+VERIFY) are DONE (2026-06-01,
> Opus 4.8). First incomplete step = PB-RB-3 (BB_MATCH driver)** — see the REBUILT LADDER (PB-RB) below. ⚠
> PB-RB-3 has an OPEN SUBJECT-STORAGE fork flagged for Lon (ζ-slot-as-canonical vs register sweep) — see the
> "PB-RB-2 MATCHER-ELEMENT FOUR-PORT ABI" block in the ladder.
> **⛔⛔ ALSO PINNED — BROKERED-MODE-ERADICATION (Lon directive 2026-06-01): there is NO need for two ways to
> enter a box. `bb_build_brokered` + `EMIT_BINARY_BROKERED` + the `(ζ,int entry)` call convention in
> `bb_capture.cpp`/`bb_arbno.cpp` are the unfinished residue of the `cc23c9f` C-byrd-box deletion and MUST go
> (BROK-0…BROK-3 rung below, after PB-RB-OPT). "Still compiles" ≠ "needed" — it is the green-build preservation
> the top FACT RULE outlaws.** (PB-0 SUBJECT BB landed at SCRIP 179bf4d; OLD PB-1 landed at 6483bb5 but built a
> PATND_t and is superseded — see PB-1-REWORK.) (The SBL-M3-CHAIN mode-3 5/6 already landed runs non-pattern
> statements from LOWER's graph + static patterns via the IR_SCAN *interpreter bridge* — that is the substrate,
> NOT this native pattern ladder.) **Pattern construction — CORRECTED (Lon 2026-06-01):** a pattern is a graph
> of EMITTED BYRD-BOXES (`bb_box_fn`), built by REF_INVARIANT (sealed) + STITCH/BUILD (variant); NOT a baked
> `tree_t` (that is EVAL/CODE only) and NOT a PATND_t (being demolished). See **CORRECTED PATTERN
> ARCHITECTURE** below; the older `tree_t`-bake "DESIGN QUESTION (DECIDED)" is SUPERSEDED.

> **⭐⭐⭐ CORRECTED PATTERN ARCHITECTURE (Lon directive, 2026-06-01, Opus 4.8). THIS SUPERSEDES the `tree_t`-bake
> "DESIGN QUESTION (DECIDED)" below AND the PATND_t-based PB-1/PB-2 as previously landed. READ THIS FIRST; the
> older blocks are kept only for history and are marked SUPERSEDED.**
>
> The trigger: PB-1 (landed `6483bb5`) built a `PATND_t` via `rt_sno_pat_build_lit`, and a draft PB-2 read a
> `PATND_t*` head. But `PATND_t` is the redundant runtime pattern-IR that is **slated for demolition** (see
> "KILL PATND_t" + PND-1 below). Wiring the new native pattern path onto the type being deleted is backwards.
> The draft PB-2 was reverted (uncommitted); PB-1 needs rework (see PB-1-REWORK below). Five corrections:
>
> **(1) A SNOBOL4 pattern is a graph of EMITTED BYRD-BOXES — `bb_box_fn` machine code in the RX pool — NOT a
> `PATND_t` data structure, NOT a `tree_t`.** The pattern ELEMENTS *are* byrd-boxes (literal-matcher,
> span-matcher, alt-combinator, …); matching is *running* that graph through the **same `bb_broker.c`** that
> drives Icon generators and Prolog goals (four-port α/β/γ/ω resume). There is NO second runtime IR and NO
> interpreted pattern tree. This is why `PATND_t` must die: it was a parallel interpreted pattern-IR beside the
> real thing. The matcher boxes ALREADY EXIST — `bb_lit.cpp`, `bb_pat_span.cpp`, `bb_pat_any.cpp`,
> `bb_pat_alt.cpp`, `bb_pat_cat.cpp`, `bb_pat_len.cpp`, … (most already carry BINARY+TEXT arms). The native
> pattern engine is not invented; it is **driving the existing `IR_PAT_*` matcher boxes as a four-port graph
> from SUBJECT**, replacing the `IR_SCAN` super-node + `PATND_t` bridge.
>
> **(2) `tree_t` (AST) is for EVAL/CODE, NOT for PATTERN.** The older bake-the-AST decision justified itself by
> analogy ("EVAL/CODE use AST in the backend, so why not PATTERN"). The analogy breaks on WHEN the structure
> exists: `EVAL(s)`/`CODE(s)` get a *source string at runtime* and MUST parse → `tree_t` → build boxes (the
> structure does not exist until runtime — the legitimate runtime-codegen path). A PATTERN's structure is
> KNOWN AT COMPILE TIME (already parsed into the statement); baking its `tree_t` just to re-walk it at runtime
> is a pointless round-trip. So: no `tree_t` in the pattern path.
>
> **(3) `DT_P` (the pattern datatype, the `descr.h` `.p` slot being demolished with `PATND_t`) BECOMES a
> `bb_box_fn` graph head** — a function pointer into SEALED EXEC space with the housekeeping (subgraph
> descriptor: entry / single exit / fail boundary) in the right places. Then `COLOR = 'GOLD' | 'BLUE'` stores a
> box-graph in COLOR; `B ? COLOR` runs it; `BOTH = COLOR CRITTER` STITCHES two box-graphs. SPITBOL's "the bead
> diagram recorded in memory" — the recording is emitted byrd-boxes.
>
> **(4) SEAL AT THE ELEMENT GRANULARITY; WIRE AT THE INSTANCE LEVEL. This is the key simplification that makes
> a GRAPH (not a tree) build cleanly.** Each pattern ELEMENT's matcher code (`bb_lit`/`bb_pat_span`/…) is
> sealed (RO). The GRAPH — the wiring of elements by their four ports — is an INSTANCE-level structure:
> `STITCH_*` boxes wire instance records whose `code` field points at the sealed element matchers. STITCH
> therefore NEVER repoints sealed interior jumps; it only wires instance boundary ports. The runtime node is a
> four-port box-instance (`{code, α, β, γ, ω, bound-operand, match-state}`) — the SAME shape `lower2` fills on
> `IR_t`, one layer down; the broker follows the port pointers exactly as for Icon/Prolog. NO tree is held: the
> parse tree survives only as the postfix EMIT ORDER, flattened away (precisely how LOWER builds its graph).
> Back-edges (ω/β) are why it MUST be a graph: "fail of element 2 resumes element 1" and "both ALT arms share
> one success continuation" are edges a tree cannot express.
>
> **(5) THE BUILD SEQUENCE = the runtime twins of LOWER's `wire_seq` / `wire_alt`.** Compile-time `wire_seq`
> (n-ary sequence-with-backtrack) and `wire_alt` (n-ary fail-chain) wire `IR_t` nodes; runtime `STITCH_SEQ` /
> `STITCH_ALT` wire box-INSTANCES with the SAME port equations. ONE construction, TWO times: all-constant
> operands → wire at EMIT time (sealed); any runtime operand → wire at MATCH-BUILD time. Postfix order
> guarantees each STITCH consumes already-finished child heads; it emits a small descriptor `{entry, exit,
> fail}` (= lower2's α_out/β_out synthesized-up, γ_in/ω_in inherited-down) for its parent to wire next.
>
> **DECIDED forks (Lon delegated judgment 2026-06-01):**
>   - **Fork A — `BB_PAT_BUILD_*` is NARROW: it exists ONLY for STRUCTURAL variance** (`*E`, `$NAME`,
>     pattern-valued variable). OPERAND variance (`LEN(N)`, `SPAN(cvar)`) is NOT a builder — the
>     compile-time-emitted element matcher reads its operand late from a `ζ`-slot at match time (operand-binding,
>     no separate box), exactly as the existing variable-arg pattern family already resolves args late.
>   - **Fork B — "build" = SPLICE (wire ports), NOT JIT-emit.** A pattern-valued variable already holds a
>     `bb_box_fn` graph (corollary of (3)), so construction wires existing/sealed graphs. Real runtime codegen
>     happens ONLY for `*E`/EVAL/CODE — the `tree_t` path of (2). Ordinary pattern construction never emits
>     fresh machine code per match.
>   - **Fork C — REUSE the existing `IR_PAT_*` matcher boxes** as the sealed/instance element matchers; do not
>     invent parallel matcher templates.
>   - **Fork D — ε-merge (Thompson/NFA) boundaries for the VARIANT (instance-wired) path** so STITCH is always
>     O(1) "redirect prev.single-exit → next.entry" (single ε-entry / single ε-exit per subgraph; reuse the
>     in-tree `bb_nfa.cpp` / RK-NFA machinery). The all-INVARIANT path seals to direct jumps with NO ε.
>   - **Fork E — sealing depth: seal at ELEMENT granularity (per (4)).** Baseline mechanism = instance-level
>     wiring for the whole pattern (invariant leaves still use their sealed element `code` as an instance's
>     `code`). The ALL-INVARIANT single-sealed-BLOB freeze is the PB-OPT OPTIMIZATION on top (correctness first,
>     bake second) — NOT a special case the base mechanism must carry. So STITCH only ever touches instance
>     records, never a sealed multi-element interior.
>
> **The two NEW boxes this introduces** (the rest of the matcher boxes already exist, Fork C):
>   - **`REF_INVARIANT`** — loads a sealed element/subgraph `bb_box_fn` head into a `ζ`-slot (RO `[rip+disp]` /
>     movabs → `[ζ+off]`). For a FULLY-invariant pattern, this one box's output IS the `DT_P` value handed to
>     MATCH; nothing else runs (the PB-OPT fast path).
>   - **`STITCH_SEQ` / `STITCH_ALT`** — read two child heads from `ζ`-slots, wire their four ports (the runtime
>     twin of `wire_seq`/`wire_alt`), leave the combined head + `{entry,exit,fail}` descriptor in a `ζ`-slot.
>   - **`BB_MATCH`** (still phase 3) — receives the `DT_P` head + Σ/δ/Δ, drives it via the broker with the
>     ch.18 unanchored OUTER start-loop (within-pattern backtracking is already the boxes' β/ω ports).

> **⭐⭐⭐ SEAL-BOUNDARY HOOKS — `BB_LINK` + the per-glob HEAD BLOCK (Lon + Opus 4.8 design session, 2026-06-01).
> This is the mechanism for the ONE thing element-granularity sealing did NOT yet answer: how a SEALED graph's
> OUTERMOST edges (the head's OUTSIDE-γ success-out and OUTSIDE-ω fail-out) reach a target that DIFFERS PER CALL
> SITE. Two coupled ideas; both keep control threading by JUMPS (never a re-dispatcher — stays on the right side
> of BROKERED-ERADICATION) and create NO concurrency hazard.**
>
> **THE PROBLEM (precisely).** Interior jumps inside a seal (element→element, element→its own ε-exit) bake fine —
> both ends live inside the seal. The trouble is the two OUTERMOST edges. When `COLOR = 'GOLD' | 'BLUE'` is a
> sealed reusable head driven from `B ? COLOR` in one statement and `C ? COLOR` in another, the bytes are
> identical but the outward targets differ per call site, so they CANNOT be `jmp rel32 <fixed>` inside the seal.
> Unseal/reseal is OUT — it serializes a shared resource (the concurrency worry), dirties I-cache on a hot path,
> and defeats sharing one sealed copy. The current PB-RB-3 inline emit dodges this (the element is emitted INLINE
> per statement via `walk_bb_flat`, so OUTSIDE-γ/ω are hardwired and there is no seal boundary to cross). **That
> dodge expires the moment `DT_P` becomes a real SHARED sealed head.** This note is the answer for that moment.
>
> **NO REGISTERS for the continuations (decided — Lon).** The obvious "dedicate r8/r9 to OUTSIDE-γ/ω, head does
> `jmp r8`" is WRONG here: those continuations must SURVIVE a `call memcmp@PLT` inside the element matchers, and
> under SysV r8–r11/rax/rcx/rdx/rsi/rdi are caller-saved (the call clobbers them — the same reason `bb_lit` does
> `push r10; call; pop r10` and `bb_match` α re-establishes r10 after `rt_sno_subject_load`). The callee-saved
> set (rbx/rbp/r12–r15) WOULD survive but is fully allocated (ζ/Σ/δ/Δ/DESCR-base/hash-base) — no free register
> to burn. Registers are the wrong home; that points straight at the ζ-frame.
>
> **IDEA 1 — `BB_LINK`: the universal seal-boundary external edge (the ζ-slot indirect jump).** A sealed graph
> reaches OUTSIDE only through a `BB_LINK` box. `BB_LINK` is a SINGLE-ENTRY PURE-TAIL box — its only emitted code
> is `jmp qword [r12 + link_off]` (an indirect jump through a `ζ`-frame slot, ~5 bytes). It has NO β (nothing to
> resume — resumption lives in the boxes UPSTREAM of it, whose β/ω still thread among themselves inside the seal),
> NO γ/ω of its own, NO state, and NEVER returns to itself. That degeneracy is deliberate: it is what stops
> `BB_LINK` from quietly growing back into the broker we deleted. The DRIVER writes the real per-call-site targets
> into the `ζ` slots BEFORE jumping into the sealed head; the sealed bytes stay immutable and re-entrant (the
> instruction is always the same fixed `jmp [r12+off]`; only the DATA in the slot is per-call-site — the dual of a
> return-address slot, one for success and one for fail). **Concurrency-free BY CONSTRUCTION:** nothing in sealed
> code is mutated; every per-activation datum, the continuations included, lives in the R12 frame, and R12
> switches per sequence (callee-saved, survives calls). Two concurrent drives of the same sealed `COLOR` write
> their own targets into their own frames and never touch each other. (The ONLY design with a concurrency problem
> was unseal/reseal; this dissolves the question.) `BB_LINK` ALLOCATES its own `ζ` slot(s) via `bb_slot_alloc`
> like every other box, and the wiring/STITCH step FILLS them — exactly parallel to how `bb_match` α allocates the
> start-cursor + subject slots today. The "two fixed slots (γ, ω)" is the DEGENERATE one-head case; the general
> form is a small VECTOR of link slots, one per `BB_LINK` instance. This IS Fork D's ε-boundary made concrete: a
> single-entry/single-exit node whose exit is `jmp [r12+slot]`; STITCH wires `BB_LINK` instances (it cannot and
> does not rewire sealed interiors), so the ε-merge role and the external-hook role were the same problem in two
> hats. Matcher templates go back to SEAL-PURE — they only ever `jmp` to direct labels; if a label turns out to be
> a `BB_LINK`, the box neither knows nor cares.
>
> **IDEA 2 — every GLOB has a HEAD BLOCK; glob→glob transition is the SAME boundary (recovered prior design).**
> When BBs are GLOBbed into a graph, every glob has a HEAD. Going BB-BLOCK-1 → BB-BLOCK-2 is the SAME external-edge
> case as head→outside: the producing glob's exit and the consuming glob's entry are wired PER-INSTANCE, not baked.
> So the HEAD BLOCK is the universal transition node between ALL globs — the place a `BB_LINK` lives. (This is the
> "HEAD BLOCK to transition between all globs" design from before the repo was re-cut; the history is gone, so this
> is the durable re-statement.) **`BB_MATCH` is *kinda* a `BB_LINK` but NOT really:** `BB_MATCH` must JUMP OFF into
> the element AND be jumped back into (the ch.18 outer-loop driver that establishes the frame + the link slots),
> whereas `BB_LINK` is the pure indirect edge that never returns to itself. The chain is **`BB_MATCH` ↔ `BB_LINK`
> ↔ dynamic land**: `BB_MATCH` drives + sets the slots; `BB_LINK` is the edge; "dynamic land" is the per-call-site
> continuation. A sealed interior therefore NEVER contains an outward `rel32` — all external links go through a
> `BB_LINK` at a HEAD BLOCK.
>
> **REFINEMENT (Lon 2026-06-01) — a HEAD BLOCK is HALF a Byrd box, and that half IS `DT_P`.** A full BB has FOUR
> ports — α/β INBOUND (entered, resumed), γ/ω OUTBOUND (success-out, fail-out). A HEAD BLOCK has ONLY the TWO
> OUTBOUND hooks: OUTSIDE-γ and OUTSIDE-ω. It has NO α/β of its own to be entered-and-resumed at, because it is
> NOT a matcher — it is what the sealed matcher graph's last box flows INTO, and from there back OUT to the
> per-call-site continuation. This is precisely what a `DT_P` value already is: a sealed-body entry plus its two
> escape edges. So the identity is **`DT_P` ≡ HEAD BLOCK ≡ { entry-into-sealed-body, OUTSIDE-γ slot, OUTSIDE-ω
> slot }** — two hooks, not four. The half-BB framing is what makes it correct: `BB_LINK` is NOT a free-floating
> edge box, it IS the OUTBOUND HALF of the head, and the head is the thing `DT_P` denotes. This also collapses an
> apparent third concept: the `{entry, exit, fail}` descriptor STITCH synthesizes (the runtime twin of lower2's
> α_out/β_out synthesized-up, γ_in/ω_in inherited-down) is the SAME object — `exit` = OUTSIDE-γ, `fail` =
> OUTSIDE-ω, `entry` = the jump-in. STITCH's build-time descriptor and the run-time HEAD BLOCK are one object seen
> at two times; there was never a separate third thing.
>
> **TWO PINS for when this lands (open items, not yet code):**
>   - **ONE FRAME PER MATCH.** The slot is `[r12+off]` and r12 switches per sequence, so `BB_LINK` must read the
>     RIGHT frame. Rule: a stitched pattern runs in ONE frame for the whole match — the element graph gets
>     per-element SLOTS in the one statement frame (what PER-BOX-LOCAL-STORAGE already implies), NOT per-element
>     frames. Then `[r12+off]` is unambiguous and no copy-down is needed. The only place a FRESH frame appears is a
>     genuine subroutine-like construct (a pattern-valued variable invoked as a callee, or `*E`/EVAL) — and THAT
>     boundary is exactly the call/return seam where an explicit continuation hand-off is wanted anyway, so it is
>     not an exception to paper over.
>   - **`BB_LINK` IS PURE TAIL, NOT A PORTED BOX.** α loads-and-jumps; no β; no γ/ω. Keep it strictly "indirect
>     jump through a frame slot, no state, no return" so it can never become a re-dispatch point. The all-invariant
>     frozen pattern (PB-OPT) keeps HARDWIRING — that case is emitted into its OWN statement (not shared), so its
>     continuations are known at emit time and pay ZERO indirection. You buy `jmp [r12+off]` ONLY when you actually
>     seal-and-share — pay for sharing only when you use it.
>
> **NEXT TOUCHPOINT (where this drops in or reveals a wrinkle):** the `g_match_*` emit-globals + `bb_slot_alloc`
> path that today passes the boundary labels (`g_match_elem_p`, `g_match_advance_p`) into `bb_match` α — that is the
> concrete spot a `BB_LINK` instance would allocate its slot and the driver would fill it. It sits right next to the
> REG-1 work (both are about what lives in the frame vs. what is baked), but `BB_LINK` is a PB-RB-4+/PB-OPT-era
> concern (shared sealed heads), NOT a REG-ladder blocker — the REG ladder ships first.

> **⭐⭐ MODES 3 & 4: HOW THEY WERE MISSED — AND WHERE THE WORK ACTUALLY LIVES (Lon directive, 2026-05-31 Opus 4.8).**
> **The whole job is LOWER + EMITTER. Get those two right and modes 3 and 4 run like magic — automatically, from the
> SAME IR graph and the SAME per-box templates. Nothing else is needed.**
>
> **THE MISS (be honest about it so it never recurs):** prior sessions treated modes 3 and 4 as *driver* problems.
> The mode-3 work went into `scrip.c` — the `sno_ring_to_tree` adapter (un-flattening the AG-ring graph into a tree
> the emitter wants) + `mode_run` wiring. Mode 4 was left as a flat `[SMX]` abort and *reported* as "excised, not
> rebuilt" for days. Both framings were wrong:
>   1. **Mode 4 was NOT missing a backend.** The EMITTER side was fully intact the whole time — `codegen_flat_build`
>      (the GAS/TEXT flat emitter) + all 15 XA wrap templates (`xa_file_header`/`xa_file_footer`/`xa_flat_*`). ONLY the
>      one-line driver *call* into them had been severed. Verified empirically this session: re-stitching the driver +
>      adding the box's TEXT arm took mode 4 from 0/6 → 1/6 with the `output` shape running end-to-end (real
>      `scrip --compile` → `as` → `gcc -no-pie -lscrip_rt --allow-shlib-undefined` → prints `hello`).
>   2. **The real engine is two arms of ONE template per box.** A SNOBOL4 statement BB has ONE IR shape (LOWER) and ONE
>      template with TWO arms (EMITTER): the **BINARY arm = mode 3** (raw x86 into the mmap'd RX pool, `bb_build_flat`),
>      the **TEXT arm = mode 4** (GAS → `as`/`gcc`, `codegen_flat_build`). Mode 2 is the C oracle (`bb_exec.c`).
>      `bb_sno_assign` is the proof: its BINARY arm gave mode 3 (verified: 86 bytes, disassembled, stackless, `r12=ζ`),
>      and adding its TEXT arm this session gave mode 4 — SAME box, SAME graph, both native modes. **That is the "magic":
>      you write the box once in LOWER + EMITTER and all three modes light up. You do NOT write per-mode driver code.**
>   3. **`sno_ring_to_tree` (in `scrip.c`) is REMOVED (Lon directive 2026-05-31 — VIOLATION).** It was a STOPGAP, never
>      the design: it re-derived the four-port BB topology AT EMIT time from the mode-2 oracle's postfix AG-ring instead
>      of LOWER producing that topology. The correct fix is in **LOWER**: lower each SNOBOL4 statement DIRECTLY into the
>      `test_sno_1.c` four-port statement-BB topology (subject-BB → pattern-BBs → replacement-BB → substitution-BB), so
>      the emitter consumes it with no driver adapter. The adapter + its helpers are deleted.
>      **[CORRECTION 2026-06-02, Opus 4.8]** The original wording below — that BOTH call sites "ABORT by design" —
>      is inaccurate and is the verbiage Lon flagged for correction: (a) mode-3 `--run` does NOT abort — it was
>      re-wired via `sno_flat_chain_build` and runs the full SNOBOL pattern family; (b) mode-4 `--compile` is NOT a
>      design limit — it is the SAME boxes as mode-3 in the TEXT medium, pending only LOWER emitting the four-port
>      statement-BB graph for SNOBOL4 (the emission scaffolding is intact; Icon/Prolog mode-4 already emit). So this
>      is a narrow, temporary wiring gap, not an intentional abort. Original (stale) wording: "BOTH call sites (mode-3
>      `--run`, mode-4 `--compile`) now ABORT by design until LOWER emits the tree shape."
>      The driver then shrinks to
>      "find main graph → hand it to the emitter." This is LM-6 DISPATCH-UNIFY territory and is now the #1 SNOBOL4 step.
>
> **EMITTER fix landed earlier (the segfault that proves the point):** the shared flat TEXT prologue/epilogue
> (`xa_flat.cpp`) ignored `g_frame_active` — it always emitted the Σ/`[r10]`-deref Icon-pattern-return epilogue. `r10`
> is SysV caller-saved, so the `@PLT` store clobbered it → mode-4 segfault. The BINARY arm already honored
> `g_frame_active` (clean `pop r12; ret`); the TEXT arm now does too (`push r12;mov r12,rdi` prologue + no-deref
> `pop r12;ret` epilogue). Byte-neutral to Icon (Icon m2 6/6 HARD held; Icon m3 5/6 held).
>
> **SO, NEXT, AND FOR EVERY STATEMENT AFTER:** the recipe is fixed. (a) LOWER the statement into the four-port BB graph
> (Icon `lower_expr_threaded` is the model; `test_sno_1.c` is the SNOBOL4 statement topology). (b) EMITTER: give each new
> box a BINARY arm (mode 3) and a TEXT arm (mode 4) — SAME processing, only BINARY-bytes vs GAS-text differs — stackless
> (`[ζ=r12+off]` RW frame + RO `[rip+disp]`), NO ring, NO value stack, NO storage outside the boxes (PER-BOX LOCAL
> STORAGE FACT RULE). (c) Both native modes pass from the one graph + one template. There is NO ring→tree adapter to lean
> on anymore — LOWER must emit the four-port shape directly.

> **⚠️ SHARED-LOWERER LOCKSTEP NOTE (Sonnet, 2026-05-31, Prolog PLG-4 commit).** Two shared three-language
> helpers in `lower.c` changed SEMANTICS as STRICT GENERALIZATIONS during Prolog backtracking work:
> `wire_seq`'s fail-chain now walks back past bounded elements to the nearest resumable predecessor (was a
> single hop that dead-ended after one bounded element), and `wire_alt` now lowers arms right-to-left so each
> arm's exhaustion threads to the next arm's entry via its own deepest-fail edge (was patching only the
> wrapper node's ω, which missed multi-element arms). `wire_seq` backs SNOBOL CAT and `wire_alt` backs
> SNOBOL ALT, so both touch latent backtracking bugs for concatenations/alternations with 2+ bounded
> elements after a generator. Re-proven non-regressive for SNOBOL4 (m2 smoke 6/7 — byte-identical via
> stash/rebuild/compare; the mode-4 pattern suite is all-SKIP under the current SMX excision). No action
> needed unless you edit `wire_seq`/`wire_alt`; the FACT RULE policy below is unchanged.

## ⛔ SHARED-LOWERER ONE-FILE CONCURRENCY (FACT RULE — byte-identical in GOAL-SNOBOL4-BB.md, GOAL-ICON-BB.md, GOAL-PROLOG-BB.md)

The unified AST→IR lowerer is **ONE file** — `src/lower/lower.c` (formerly `lower2.c`, the new tree root after old `lower.c` was deleted 2026-05-31) — with **ONE entry** (`lower2`, role-seeded via `lower2_{value,pattern,goal}_entry`) and **ONE big switch over the shared `tree_e`** (every `TT_*`). SNOBOL4, Icon, and Prolog are developed CONCURRENTLY in SEPARATE sessions, all writing into this one file. Each language adds ARMS the others don't; the discipline below makes three concurrent sessions **conflict-free and mutually beneficial** (one session's added case label / shared helper is the next session's ready slot):

1. **ONE CASE PER KIND.** Each `TT_*` is at most ONE `case` label per role switch. If your language needs a kind with no case yet → ADD the case. If the case exists → ADD YOUR ARM to it. **NEVER duplicate the label.** (Win-win: SNOBOL4 adding `case TT_ASSIGN` hands Icon/Prolog a ready slot.)

2. **LANGUAGE VARIATION LIVES INSIDE THE CASE — NEVER A PER-LANGUAGE FORK.** When a kind behaves differently per language, branch on `cx.lang` (or role) WITHIN the one case (`switch (cx.lang) { case IR_LANG_SNO: …; case IR_LANG_PL: …; }`, or if/else). No per-language lowering functions, no per-language files. One kind → one case → language arms inside.

3. **EDIT ONLY YOUR OWN LANGUAGE'S ARM.** A session may ADD or MODIFY the `cx.lang` arm for its OWN language inside any case. It must **NEVER modify, reorder, or delete another language's arm.** This is what makes the three sessions' diffs non-overlapping → git auto-merges with **zero conflicts**.

4. **A MISSING LANGUAGE ARM FALLS LOUD, NEVER SILENT.** Inside a case, a language with no arm yet routes to `lower_unhandled` (loud stderr + NULL) — never a silent or wrong default. A half-built arm fails LOUDLY so it can never corrupt a peer's proven path.

5. **SHARED SCAFFOLDING IS ADDITIVE; SIGNATURE/SEMANTIC CHANGES ARE LOCKSTEP.** The cursor (`lcx_t`), the port primitives (`nalloc`/`set_succ_fail`/`ret`/`emit_leaf`), and the match-collect library (`tm`/`tm_g`) are SHARED. ADDING a helper or a case label is free (no conflict). CHANGING the signature/semantics of an existing shared helper or of `lcx_t` affects all three cats → it MUST update all three GOAL files' FACT RULE in the SAME commit and re-prove all three.

6. **THE TOPOLOGY PROOF GATE IS THE SHARED GREEN SIGNAL.** `scripts/prove_lower2.sh` must stay green before every commit. Each cat's proof cases are ADDITIVE (append your own; never delete a peer's). Green = your arm wired right AND you didn't disturb a peer.

**COMPLETION TEST:** (a) no duplicated `case TT_` label within any one switch in `lower.c`; (b) every case's language branches end in a real arm or `lower_unhandled` (no silent default); (c) the FACT RULE body is byte-identical across the three GOAL files (`awk '/SHARED-LOWERER ONE-FILE/{p=1} p{print} /prove_lower2.sh green/{if(p)exit}'` md5 matches — first-match, not greedy `sed`); (d) `scripts/prove_lower2.sh` green.

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

## 🔴🔴 #0 PRIORITY — BB-HYGIENE LADDER (SNOBOL4) — ORDERED, DO BEFORE REG LADDER (Lon 2026-06-01)

Per the BB-HYGIENE FACT RULE. **STRICT ORDER — lowest number first.** De-cram + de-fuse each file (de-cram first because cram hides the duplicated logic underneath it), then the de-dup/RT-fix sweep. After EACH step: SNOBOL4 m2 7/7 HARD byte-identical, smoke 3-mode unchanged, purity green, commit. Copy the worked example: `bb_binop_*.cpp` + 38-line `bb_binop.cpp` router (Icon-owned; done 2026-06-01). The de-cram steps are prep; **SNO-HY-7 (de-dup + RT-fix) is the core fix** — collapse any logic written twice.

- [ ] **SNO-HY-1 — `bb_pat_break.cpp` (349).** De-cram: one file per distinct four-port shape behind a `bb_pat_break` router. Group 95%-identical cursor-advance shapes (do NOT over-split). De-fuse any `pBB->…->ival/sval` operand reads.
- [ ] **SNO-HY-2 — `bb_pat_tab.cpp` (286) + `bb_pat_span.cpp` (271).** TAB/RTAB and SPAN: split inline-vs-RT-call shapes; group near-identical. Routers.
- [ ] **SNO-HY-3 — `bb_sno_assign.cpp` (226) + `bb_capture.cpp` (226).** Split literal-rhs vs slot-rhs vs name-store; the capture deque-save vs @-cursor-write. **De-fuse: a literal rhs is its own producer box — read its slot, do not seal its value here.**
- [ ] **SNO-HY-4 — `bb_pat_any.cpp` (218) + `bb_pat_notany.cpp` (215).** cset-blob vs single-char; group if 95%-identical between the two files' shapes. Routers.
- [ ] **SNO-HY-5 — `bb_pat_cat.cpp` (194) + `bb_pat_alt.cpp` (185) + `bb_pat_arb.cpp` (183).** Combinators. The variable-length define/jmp-pair loop is its own shape; fixed shape another. (The variable-length define/jmp-pair loop derives offsets from a running length — that is a separate design question; split the shapes now.) Routers.
- [ ] **SNO-HY-6 — audit the rest (`bb_pat_len` 161, `bb_pat_pos` 158).** Split only if >1 four-port shape; else mark NO-SPLIT-NEEDED. `bb_lit.cpp` (185) — its 5 platform arms (`if (PLATFORM_X86/JVM/JS/NET/WASM)`) are the sanctioned per-platform multiplex, NOT a violation; leave it.
- [ ] **SNO-HY-7 — de-dup + RT-fix, all SNOBOL4 boxes.** Any algorithm in both a TEXT and BINARY arm → DELETE both, replace with one `rt_*` call. No emit-time value work (term-build/compare/arith go to RT).
- [ ] **SNO-HY-FENCE — gate.** `scripts/test_gate_bb_one_box.sh` green for SNOBOL4-owned files; wired into Session Setup. m2 7/7 HARD held throughout.

## 🔴 CURRENT PRIORITY (Lon directive 2026-06-01) — DO THIS FIRST: REG LADDER (BB TEMPLATES → RATIFIED REGISTERS)

**The SNOBOL4 pattern BB templates are NOT yet on the ratified registers** — they still use the legacy subject
model (`[r10]` cursor; Σ/Δ via `movabs &Σ`/`&Σlen` = emitter-process global addresses). Migrating them to
Σ=R13 / δ=R14 / Δ=R15 / ζ=R12 is **the current top priority** (Lon): it brings convention compliance AND removes
the process-local-address bake that blocks SNOBOL **mode-4** (the m4 0/6 cause). This ladder runs BEFORE the rest
of the PB-RB feature ladder (PB-RB-4+) and the BROKERED-ERADICATION rung (both still below, lower priority until
the registers are correct). REG-0 is coupled to PB-RB-3 (now landed), so REG-1 (`bb_lit`) is the first code step.

### ⭐⭐ REG LADDER — SNOBOL4 PATTERN-FAMILY REGISTER-LAYOUT MIGRATION (Lon directive 2026-06-01, Opus 4.8)

Bring the SNOBOL4 pattern family from the **legacy subject model** (cursor in the `[r10]` per-BLOB data-block
field; Σ via `movabs &Σ;deref`/`lea [rip+Σ]`; Δ via `movabs &Σlen`/`[rip+Σlen]` — `TEMPLATE_ADDR_SIGMA`/
`TEMPLATE_ADDR_SIGLEN` = **emitter-process global addresses**) to the **ratified register convention** Σ=R13,
δ=R14, Δ=R15 (ζ=R12, r10 stays the per-BLOB DATA-block ptr). Two wins in one: (a) convention compliance; (b)
**removes the process-local-address bake → SNOBOL mode-4 relocatability** (the m4 0/6 blocker). NOT a convention
change (the table is untouched) → SNOBOL-session-local, no lockstep. Each step: prove topology
(`prove_lower2.sh`) unchanged, migrate BINARY+TEXT arms together (SAME processing, only bytes-vs-GAS differ),
disasm-verify the new register usage, gate. **Mode-2 oracle (`bb_exec.c`) is UNTOUCHED — these are modes-3/4
templates only; m2 7/7 HARD must stay invariant every step.**

- [ ] **REG-0 — register-establishment contract + r13 de-confliction (PREREQ; coupled to PB-RB-3).** Pin who sets
  R13/R14/R15 and that they survive the chain. Canonical: **BB_MATCH (PB-RB-3) α** loads `R13 ← Σ-slot`,
  `R15 ← Δ-slot` from SUBJECT's ζ-frame and `xor r14,r14` (δ=0, ch.18 step 1) before entering the element graph;
  the ch.18 OUTER start-loop re-sets R14 per start-iteration. R13/R14/R15 are **callee-saved (SysV)** so they
  survive `call memcmp@PLT` with NO per-box save (only the caller-saved r10 needs `push r10`/`pop r10`).
  **r13 de-confliction:** r13 doubles as the SM-state register ONLY in SM context; SNOBOL pattern chains emit
  ZERO SM opcodes (sibling of ICON SM = ZERO OPCODES), so R13=Σ is unambiguous on this path. NO element edits in
  REG-0 — it is the contract REG-1+ depend on. **DO REG-0 AS PART OF PB-RB-3's BB_MATCH α** (preferred), or — to
  unit-test elements before BB_MATCH — a thin subject-register prologue shim in `sno_flat_chain_build`/`_text`
  that loads R13/R15 from SUBJECT's ζ-slots + zeroes R14 after the SUBJECT box. Gate: build rc=0; all gates
  invariant (no element bytes changed yet).
- [ ] **REG-1 — migrate `bb_lit` (the proven reference element).** BINARY+TEXT: cursor read `mov eax,[r10]` →
  `mov eax, r14d`; cursor write `mov [r10], eax` → `mov r14d, eax`; Σ-base `movabs rax,&Σ; mov rax,[rax]` (BIN) /
  `lea rcx,[rip+Σ]; mov rax,[rcx]` (TEXT) → use `r13` directly; Δ-compare `movabs rcx,&Σlen; cmp eax,[rcx]` →
  `cmp eax, r15d`. β arm: `δ -= len` becomes `sub r14d, len` (no `[r10]`). Re-derive the byte sequence + patch
  offsets (the patch tuple shrinks — the two `movabs`+deref blocks vanish). Removes both `TEMPLATE_ADDR_SIG*`
  bakes from `bb_lit`. Prove: prove_lower2 topology unchanged; mode-3 `S 'b'` in `'abc'` → `[1,2]` under REG-0;
  disasm shows cursor=r14/Σ=r13/Δ=r15, no `&Σ`/`&Σlen` imm64. Gate: m2 7/7 HARD invariant; m3 ≥ floor; purity
  clean; g_vstack==0.
- [x] **REG-2 — cursor-advancing leaves. 6/6 COMPLETE (SCRIP `65686c2`, 2026-06-01 Opus 4.8).** `bb_pat_len`,
  `bb_pat_any`, `bb_pat_notany`, `bb_pat_span`, `bb_pat_break`, `bb_pat_rem` — same rewrite per box (verify each box's
  actual cursor-field offset + `&Σ`/`&Σlen` sites against disasm before editing; they are NOT all identical). Each step
  removes that box's `TEMPLATE_ADDR_SIG*` bakes. Gate per box (or small sub-group); m2 invariant.
  **First 5 (SCRIP `eb4bf7c`):** `bb_pat_len` (34B, sites {13,25,29,30}), `bb_pat_rem` (13B, {4,8,9}), `bb_pat_any`
  (74B, {8,52,61,65,70}), `bb_pat_notany` (74B, same; byte@50 `0F84`→`0F85`), `bb_pat_span` (195B,
  {118,143,147,167,191}; internal Δ jge +62 / je +18 / jmp loop −86; r11 base-copy + its push/pop dropped, Σ=r13 used
  directly). **`bb_pat_break` LANDED THIS SESSION (dual-arm, both converted in one pass for the REG-FENCE grep):**
  plain BREAK **153B, sites {125,129,149}** (internal Δ jge +63 / jnz +19 / jmp loop −88); BREAKX **290B, sites
  {125,130,134,265,286}** (α scan + β rescan; identical per-loop internal jumps jge +87 / jnz +19 / jmp loop −88;
  `z` in [zeta+8], `z_orig` in [zeta+12] — the 4B padding of the 16B `rt_cs_t`, recovered as δ−z before z++). Both
  arms assembled+objdump-verified via the `as`-transcribe route, then Python byte-recounted to confirm every site.
  BINARY+TEXT both; r11 + push/pop r11 dropped (Σ=r13 direct), only push/pop r10 around strchr remains. Token-clean:
  zero `TEMPLATE_ADDR_SIG*`/`[r10]` in code OR comment. β semantics preserved (BREAK δ−=z on β; BREAKX z_orig recover
  + z++ + rescan-to-next). Zero `b.size()` introduced (stash-verified: 123 with and without the diff).
- [ ] **REG-3 — cursor-verify / position leaves.** `bb_pat_pos` (RPOS folded), `bb_pat_tab` (RTAB folded),
  `bb_pat_atp` (`@var` writes the cursor → write R14). POS/RPOS read R14 (and Δ=R15 for RPOS) and compare; TAB/RTAB
  advance R14 to a computed target. Gate; m2 invariant.
- [ ] **REG-4 — combinators.** `bb_pat_alt`, `bb_pat_cat`, `bb_pat_fence` — they thread δ via the ports and
  save/restore δ on backtrack: the saved-δ slot moves from the `[r10]` data-block field to a **ζ-slot save of R14**
  (`mov [r12+off], r14d` / restore), NOT `[r10]`. FENCE seals δ on α, restores on β (commit) — now via R14+ζ-slot.
  Gate; m2 invariant.
- [ ] **REG-5 — generators + capture (coordinate with BROK-1/BROK-2).** `bb_pat_arb`, `bb_arbno`, `bb_capture`
  (the `std::deque<int>` saved-δ pattern stores R14 snapshots), `bb_pat_defer`. Per-activation δ state migrates
  from the `[r10]` block to R14 + ζ-slot/deque saves. Since BROK-1/BROK-2 convert CAPTURE/ARBNO to jump-to-α/β,
  do REG-5 **with or after** those rungs to avoid double-rework. Gate; m2 invariant.
- [ ] **REG-RO — READ-ONLY locals to IP-RELATIVE (the RW ladder's DUAL; this is what finishes r10 off).** Lon
  directive 2026-06-01. RULES.md **ICON READ-ONLY LOCALS ARE IP-RELATIVE FACT RULE**: a per-box compile-time
  constant — literal string bytes, cset pointer, a fixed bound, an op code, AND the resolved address of a runtime
  helper — is RO and MUST be reached by `[rip+disp]` into SEALED data placed adjacent to (within/next to) the box's
  own BLOB, NEVER by an absolute `movabs` immediate and NEVER from an `[r10]`-block field. Today the SNOBOL pattern
  **BINARY** arms bake their RO ADDRESSES as `movabs` imm64 — `bb_lit` `movabs rsi,&lit` + `movabs rax,&memcmp`;
  `bb_pat_any`/`notany`/`span`/`break` `movabs rdi,&cset` + `movabs rax,&strchr` (the matching **TEXT** arms ALREADY
  do this right: `lea reg,[rip+label]` / `call …@PLT`). Per box, move each baked ADDRESS into a sealed RO data
  trailer emitted immediately after the box code and load it with `lea`/`mov reg,[rip+disp]`, where `disp` is a
  LITERAL emit-time constant derived from the box's fixed layout (data and access live in the SAME box BLOB, so the
  disp is knowable by hand — FACT RULE TWO LITERAL FORMS preserved: the byte map stays hand-coded, only the
  addressing mode changes). NOTE — a small literal INTEGER operand (e.g. `bb_lit`'s `mov rdx,len`) is a normal
  immediate, NOT addressed storage, and is OUT OF SCOPE. **PAYOFF:** (1) conforms the SNOBOL pattern family to the
  RO FACT RULE; (2) makes the box POSITION-INDEPENDENT in the BINARY (mode-3 JIT) arm too — a SECOND contributor to
  lifting SNOBOL m4, alongside the `&Σ`/`&Σlen` removal; (3) with RW state now in ζ=R12 / Σ=R13 / δ=R14 / Δ=R15
  (the RW ladder above) and RO state in `[rip+disp]`, **r10 has NO remaining purpose** — the `[r10]` cursor-mirror
  writes and the `push r10`/`pop r10` guards around `memcmp`/`strchr` are DEAD and are removed here, eliminating
  r10 from the pattern family entirely (the RW ladder removes [r10]-as-cursor; REG-RO removes the last r10 traffic).
  Sequence: do REG-RO **after** the RW ladder (REG-2…REG-5) so each box is touched once; per box re-derive the byte
  map + patch offsets (the `movabs`+imm64 block, 10 bytes, becomes a `lea`/`mov [rip+disp]`, 7 bytes — offsets
  shift; verify with `as`+`objdump` exactly as REG-2 did). Gate per box; m2 7/7 HARD invariant. COMPLETION TEST
  (rung): no `movabs` loading an RO ADDRESS (lit / cset / helper-fn ptr) remains in the SNOBOL pattern BINARY arms —
  each is `[rip+disp]` into sealed RO data; **zero `r10` in ANY form** (`[r10]`, `push r10`, `pop r10`) in the
  pattern family; m3 ≥ floor; probes green.
- [ ] **REG-FENCE — the no-legacy-cursor / no-r10 gate (completion test).** Add `scripts/test_gate_sno_pat_reg.sh`:
  `grep -lE 'TEMPLATE_ADDR_SIGMA|TEMPLATE_ADDR_SIGLEN' src/emitter/BB_templates/bb_pat_*.cpp src/emitter/BB_templates/bb_lit.cpp src/emitter/BB_templates/bb_capture.cpp src/emitter/BB_templates/bb_arbno.cpp`
  == empty, AND no `[r10]`-as-cursor read/write remains in those files (cursor is r14, subject r13, length r15),
  AND (post-REG-RO) **zero `r10` in any form** (`[r10]`/`push r10`/`pop r10`) in the pattern family with every RO
  address reached `[rip+disp]` (no RO-address `movabs` left). Wire into the Session Setup gate list so it can never
  creep back. **Then RE-CHECK SNOBOL m4 smoke** — with the `&Σ`/`&Σlen` bakes gone AND the RO addresses now
  position-independent, the pattern boxes are relocatable, so the m4 0/6 floor should finally be liftable (track
  the new m4 count). COMPLETION TEST (rung): the new gate green + in Session Setup; m2 7/7 HARD held; m3 ≥ floor;
  SNOBOL m4 re-measured (expected > 0/6 once a pattern chain assembles+links+runs standalone).

**COMPLETION TEST (REG ladder):** `test_gate_sno_pat_reg.sh` green (zero `TEMPLATE_ADDR_SIG*`, zero `[r10]`-cursor,
and — post-REG-RO — zero `r10` in any form with all RO addresses `[rip+disp]`, in the SNOBOL pattern family); every
pattern box reads cursor=R14 / subject=R13 / length=R15 and reaches RO constants by IP-relative addressing; m2 7/7
HARD invariant throughout; SNOBOL mode-4 pattern smoke re-measured and improved (the process-local-address blocker
is gone). The convention TABLE is byte-identical-×3 and UNCHANGED (this rung conforms boxes to it, does not edit it).

---

## ⭐ SESSION 2026-05-31 (Opus 4.8) — GROUND-ZERO LOWER REWRITE (unified four-port AST→IR) — FOUNDATION LAID + PROVEN

**Post-PIVOT direction (Lon):** rip-and-replace the lowerer with ONE unified AST→IR pass on the Proebsting
four-port attribute-grammar model. SNOBOL4 pattern lowering (the legacy `build_node`) becomes the **PATTERN
role** of that unified pass. Ground zero — old build may break; old `lower.c` left untouched for now.

**Survey:** `src/lower/lower.c` is the ONLY real AST→IR lowerer (7 tangled `TT_` dispatchers). `prolog_lower.c`/
`rebus_lower.c` are AST→AST normalizers; `lower_sno.c` is a tree→`.sno` source emitter. 156 `TT_` in, 110 `IR_` out.

**Architecture — ROLE × kind.** One funnel `lower2(cx, e, γ_in, ω_in, &α_out, &β_out)` → branch on
`cx.role ∈ {VALUE, PATTERN, GOAL}` → ONE `switch(tree_e)` per role. ~2/3 of kinds role-monomorphic; only
QLIT/VAR/FNC + arith/rel (shared VALUE↔GOAL) split on role.

**Canonical signature = the attribute grammar** (jcon `ir_a_X(p,st,inuse,target,bounded,rval)`; Proebsting):
γ/ω (succeed/fail) INHERITED in as 2 pointers; α/β (start/resume) SYNTHESIZED out as 2 ptr-to-ptr. `IR_t`
ports are POINTERS → goto-chains COLLAPSE = the paper's Fig-2 optimization for free. Two template classes:
BOUNDED LEAF (`emit_leaf`, honors `cx.bounded` = jcon `/bounded`) + RESUMABLE GENERATOR. Discipline in 3
primitives: `nalloc`, `set_succ_fail` (default-only — never clobber a threaded port), `ret`.

**Landed (SCRIP `3c66694`, NEW standalone TUs — NOT in Makefile/driver, nothing regressed):**
- `src/lower/lower2.c` (358 ln, 0 errors). 5 FOUNDATION BOXES wired + PROVEN faithful to Proebsting Figs 1&2:
  literal §4.1, unop §4.2, binop §4.3 (plus+LessThan, relational flag `dval=1.0`), to/to_by §4.4 (ir_a_ToBy),
  if §4.5 (runtime-gated; E1 lowered `bounded=1`). PATTERN leaves (LIT/ARB/REM + SPAN/ANY/NOTANY/BREAK/BREAKX
  via centralized `pat_cset_arg` — the cset trichotomy that was copy-pasted 5× in legacy `build_node`). GOAL
  leaves (cut/true/fail). 118/156 kinds armed; rest = labelled stubs → LOUD `lower_unhandled`, each annotated
  with its `ir_a_*` source.
- `src/lower/prove_lower2.c` — topology proof harness (links lower2+scrip_ir ONLY; local `kind_is_resumable`
  + `cset_try_fold` stub so the old lowerer is NOT linked). Dumps each IR node idx + α/β/γ/ω.
- `src/lower/tmatch_proto.c` — `tm`/`tm_g` tree-pattern match+capture PROTOTYPE (compiles) + `#if 0` rewrite
  exhibit (foundation arms + nested `EVERY(ASSIGN(VAR,TO(lo,hi)))` + Prolog ladder in pattern form).

**PROOF (why this is a SOLID foundation, not a guess):** `5 > ((1 to 2)*(3 to 4))` → exactly **9 IR nodes**
(paper's "nine expanded templates"); **14/17 control edges == Figure 1**, the 3 = FAITHFUL Fig-2 collapses
(constant bounds). Proof CAUGHT a real `v_to` bug — wired both children's fail to outer ω; canonical
`ir_a_ToBy` requires **`to.fail → from.resume`**. FIXED, RE-PROVEN on `(1 to 2) to (3 to 4)` (paper §2
"initiated four times"): critical edge now `to2.fail → to1`. **Topology proven; NOT executed** — value-level
proof pending and depends on `bb_exec.c` honoring the relational flag (`dval=1.0`) + if-gate (`node.β` runtime
dispatch) as encoded — VERIFY against the executor, do not assume (RULES: consult canonical sources).

**Tree-pattern matching — WHAT IT IS (Lon's "two shots"; STEP 2, AFTER the foundation is complete).**
A lowering rule is really "*if the AST node looks like SHAPE, bind its parts and wire them*." Tree-pattern
matching makes that literal: a matcher tests a node's SHALLOW shape (its kind, optionally one child's kind /
an sval tag / arity) and **captures** the immediate sub-expressions into named pointers; the rule body then
recursively lowers the captured parts and wires the ports. This is the AST-side analog of SNOBOL `subj ? pat`:
the AST node is the subject, the shape is the pattern, captures bind sub-trees, ordered alternation gives the
"first matching rule wins" fall-through (the same effect as today's if-ladders).

THE FACILITY (prototyped + compiles in `src/lower/tmatch_proto.c`):
```c
/* match kind + arity, capture the first nargs children into (const tree_t **) out-params */
int tm  (const tree_t *e, tree_e kind,            int nargs, /* &cap0, &cap1, ... */ ...);
/* same, plus require e->v.sval == tag  (the FNC(",",a,b) / FNC("phrase",...) style dispatch) */
int tm_g(const tree_t *e, tree_e kind, const char *tag, int nargs, /* &cap0, ... */ ...);
```
`tm` returns 1 and binds the capture pointers iff `e->t==kind && e->n>=nargs`. Captures are the subtrees to
lower next (NOT yet lowered — capture defers, exactly like a DEFER pattern binds-then-matches).

THE "TWO SHOTS":
- **Shot 1** = `tm`/`tm_g` (match + capture).
- **Shot 2** = the per-role switch where each arm is `if (pattern matches) → produce wiring`.

WORKED EXAMPLE (hand-coded vs pattern form), the `binop` arm:
```c
/* hand-coded today (lower2.c v_binop): */
if (e->n < 2 || !e->c[0] || !e->c[1]) return NULL;
IR_t *E1 = e->c[0], *E2 = e->c[1];                 ... lower E1, lower E2, patch, wire ...
/* pattern form: the guard + the child-grab become ONE line that reads as the shape */
const tree_t *E1, *E2;
if (!tm(e, e->t, 2, &E1, &E2)) return NULL;        ... lower E1, lower E2, patch, wire ...
```
And the NESTED case (today a 3-deep manual guard at legacy lower.c:753) reads top-down as the AST shape:
```c
/* EVERY(ASSIGN(VAR, TO(lo,hi))) */
tm(e,TT_EVERY,1,&asn) && tm(asn,TT_ASSIGN,2,&var,&rhs) && var->t==TT_VAR && tm(rhs,TT_TO,2,&lo,&hi)
```
And the Prolog goal if-ladder collapses to a table: `if (tm_g(e,TT_FNC,",",2,&A,&B)) return lower_conj(...);`
one readable `shape ? builder` line per control construct.

WHY (measured on legacy lower.c): decisions are SHALLOW — 120 decision-peeks but only **12 sites peek two
levels**, **0 peek three**; wiring is uniform recursion (78 lower-calls, one per child subexpression). So
every rule = MATCH shallow shape + CAPTURE children + RECURSE + WIRE — exactly what `tm`/`tm_g` serve. LOC
shrink is ~30%; the real win is UNIFORMITY (every `e->n<k`/null guard vanishes into the match; nested peeks
read as the tree; dispatch ladders become tables). **Sequencing:** do this AFTER the hand-coded foundation
boxes are all in and proven — refactor proven code into pattern form, don't design two things at once.

ENDGAME: this pattern form is the bridge to an **Icon-bootstrap lowerer** — the lowerer IS an Icon program
over `tree_t` (each rule a SNOBOL pattern over `node.kind ++ node.sval` with children captured, Icon
alternation giving ordered match). Once Icon-BB executes enough, the pattern-form C transliterates almost
mechanically. (Parse symmetry: the parser is an LALR match tokens→tree; `tm`/`tm_g` is the symmetric match
tree→IR on the way down. DEFER symmetry: `IR_PAT_DEFER`/`rt_defer_match` is the runtime analog of a
compile-time capture.)

**Endgame threads:** (a) parse = LALR match tokens→tree; tmatch = SYMMETRIC match tree→IR. (b) `IR_PAT_DEFER`
(`rt_defer_match`) is the runtime analog of a compile-time capture — same deferral discipline, one level up.
(c) the pattern-form C transliterates to an Icon-bootstrap lowerer once Icon-BB executes.

**Next:** (1) add `Every`/`Alt`(first SIBLING-backtrack box)/conjunction, prove each via the harness;
(2) wire `lower2`→`bb_exec` on `1 to 5` for value-level proof + confirm/adjust the relational+if-gate encodings;
(3) rebuild program/proc walkers (`lower`/`lower_proc_body`/`lower_pl_predicate`/`IR_lower_pat`) → `stage2_t`;
(4) fill VALUE/PATTERN/GOAL arms box-by-box, grounded in `ir_a_*`, proven; (5) THEN tmatch refactor;
(6) later, Icon bootstrap. Refs: `Proebsting-...-Goal-Directed-Evaluation.pdf`, `jcon_irgen.icn` (`ir_a_*`).

**(The pattern-BB-template work below — BINARY/TEXT arms, mode-3/4 — is the PRIOR track and remains valid;
the lower rewrite is upstream of emission and does not change the BB/SM/XA template ladder.)**

---

## ⛔ MANDATORY READ BEFORE EVERY SESSION

> **⛔ READ FIRST for SBL-PAT-BB (modes-3/4 pattern work) — Lon "Eureka" 2026-05-31.** Before touching the
> SUBJECT/PATTERN/REPLACEMENT build path, read **ARCH-SNOBOL4.md → "Native pattern architecture — modes 3 & 4
> (pattern = built BB graph)"** AND **ARCH-x86.md → "Two block TYPES the emitter outputs (BB vs XA)"**. The
> active rung is **SESSION RUNG #0 SBL-PAT-BB** (below); first incomplete step = **PB-1 PATTERN-BUILDER BB** (PB-0 done, 179bf4d). Core idea:
> a SNOBOL4 pattern is a runtime byrd-box GRAPH — phase-2 lowers to BUILDER BBs that build BBs; phase-3 runs
> via a generic BB_MATCH box; later, INVARIANT patterns BAKE to a static BB. (PLAN.md rule 7 already routes
> MODE3/4-EMIT work to ARCH-x86.md + ARCH-SCRIP.md, both of which cross-ref the ARCH-SNOBOL4 section.)

**Pipeline:**
```
SNOBOL4 source → CMPILE parser → tree_t* → lower_pat_dcg.c (BB_lower_pat)
    → BB_graph_t (BB_PAT_* nodes, four-port-wired)
    → [mode 2] bb_exec.c: case BB_PAT_*  (correctness oracle)
    → [mode 4] walk_bb_flat → FILL → walk_bb_node → emit_core
               → BB_templates/bb_pat_*.cpp TEXT arm (inline GAS)
               → BB_templates/bb_pat_*.cpp BINARY arm (raw x86 via bb_bin_t)
```

- **Mode 2 (`--interp`):** `sm_interp_run` + `bb_exec.c` C oracle.
- **Mode 3 (`--run`):** `sm_run_native` → SM_templates BINARY arms → sealed RX → jump in. BB call-outs via flat-wired `bb_build_flat`. Opt-in via `SCRIP_M3_NATIVE=1`; default still `sm_interp_run`.
- **Mode 4 (`--compile`):** Emit phase uses TEXT arms → GAS → gcc link. Standalone runtime builds pattern blobs via `bb_build_brokered` → template BINARY arms.

> **⛔ TESTING DIRECTIVE (Lon 2026-05-31) — ALWAYS RUN ALL THREE MODES FOR THIS GOAL.** Whenever you test
> SCRIP, exercise **mode 2 (`--interp`)**, **mode 3 (`--run` / SB-LINEAR)**, AND **mode 4
> (`--compile --target=x86` → `as` → `gcc -no-pie … -lscrip_rt` → run the binary)** — every time, from now on.
> `scripts/test_smoke_snobol4.sh` now does this: mode 2 is the **HARD gate** (exit 0 requires mode-2 all-pass);
> modes 3 and 4 are **RUN + REPORTED on every invocation** (tracked with `MODE3_MIN`/`MODE4_MIN` PASS floors,
> default 0) so the full native picture is always visible. NEVER report a mode-2 number alone — always run and
> record 3 and 4 alongside it. (Mode 3/4 for SNOBOL4 are currently 0/6 — the `--run` native path and the
> SMX-4-excised `--compile` x86 emission are not yet rebuilt; the directive makes that gap visible each run.)
> Raise `MODE3_MIN`/`MODE4_MIN` as those modes come back so regressions in them also fail the gate.

**Absolute rules (RULES.md):** No C Byrd boxes. TEMPLATE-PURITY. ONE x86 PRODUCER. Stub LOUD via `bomb_bytes()`. X86 ONLY. MODE PURITY (no silent cross-mode fallback / no silent eps substitution).

---

## Architecture: what the x86 TEXT arm must emit

`walk_bb_flat` calls `FILL(nd, lbl_γ, lbl_ω, lbl_β)`. Template emits α-port code (fresh: match, advance Δ, jump γ or ω) followed by β-port code (retry: undo, advance differently, jump γ or ω; some kinds β = lbl_ω directly).

**Runtime state in TEXT arm:** `[r10]` = Δ (cursor, 32-bit int). `[rip + Σ]` = subject ptr. `[rip + Σlen]` = length. `nd->sval` = charset string baked into `.data`. `nd->counter` (int64) = runtime mutable state for generators.

**BINARY arm:** raw bytes via `bytes()` + `u32le(0)` rel32 placeholders + `bb_bin_t.sites` listing rel32 patch offsets. `movabs` for absolute addresses. Refs: `bb_lit.cpp`, `bb_pat_len.cpp`, `bb_pat_pos.cpp`, `bb_pat_any.cpp` (104B, sites {17,72,86,90,100}), `bb_pat_notany.cpp`, `bb_pat_break.cpp` (178B), `bb_capture.cpp` (128B).

**Per-node persistent BINARY storage (SHARED PATTERN):** brokered blobs have no ELF `.data`. Two patterns:
1. `g_emit.bb_cs_zeta` `rt_cs_t {const char *chars; int delta;}` — `delta @+8` for SPAN/ARBNO counters; baked via `movabs rcx, &zeta`.
2. Process-lifetime `std::deque<int>` allocator (e.g. `cap_alloc_saved_delta_slot()`) — pointer never invalidates, GC-safe via C++ heap. Use for SPAN-2 / CAP / BREAKX scratch.

**DO NOT** use `GC_MALLOC` for per-node scratch baked as imm64 — bb_pool is mmap'd, GC can't see the address.

**Semantic oracle:** `bb_exec.c case BB_PAT_*` — α (state==0) and β (state>0) logic.

---

## ⭐ THIS SESSION (Lon directive 2026-05-30): RENAME BB → IR (uppercase IR-graph constructs only)

**Why.** With the Stack Machine gone (SMX-4), the uppercase `BB_*` directed graph IS the
intermediate representation. Restore its historical name **IR** so the codebase visibly separates
**IR constructs** (the lowered graph — uppercase, → `IR_*`) from **emitted byrd-box constructs** (the
executable boxes — lowercase `bb_*`, UNCHANGED). The casing split (`BB` vs `bb`) already in place
makes this mechanically safe; `BB.h`'s include guard is already `SCRIP_IR_H` (residue of the prior IR name).

**Reliability facts (measured this session on clean `a0bb9be4`).**
- Target namespace is clean: the ONLY pre-existing `IR_*` tokens are `IR_IS_GEN_KIND_TO` and
  `IR_WALK_MAX` (macros in `emit_ir.h`) — no collision with `IR_t`/`IR_graph_t`/`IR_op_t` or any
  enum-member rename.
- The casing split is real and reliable: lowercase `bb_alloc` (pool allocator) ≠ uppercase `BB_alloc`
  (IR-graph allocator); lowercase `bb_node_t`/`bb_node_id` ≠ uppercase `BB_t`/`BB_node_alloc`. A
  `\bBB[_A-Z]` (rename) vs `\bbb_` (leave) regex cleanly separates IR from byrd-box.
- UTF-8 hazard: source carries `α/β/γ/ω` — every grep/sed MUST use `-a` / byte-level (the token `BB_t`
  never overlaps the Greek bytes, so a byte-level sed is safe and lossless).

### Scope tiers
- **TIER A — rename (Lon-named, definite):** `BB_t`→`IR_t` (1346 occ / 88 files); `BB_graph_t`→`IR_graph_t`
  (301 occ / 24 files).
- **TIER B — rename (CONFIRMED in scope; the IR node-kind taxonomy + IR API):** `BB_op_t`→`IR_e`
  (23) — enum-suffix convention `_e` (structs are `IR_t`/`IR_graph_t`, the node-kind enum is `IR_e`);
  the ~125 `BB_op_t` enum members `BB_LIT_I … BB_PAT_ATP` incl. `BB_GEN_*`/`BB_NFA_*`/`BB_CSET_*`
  + `BB_OP_COUNT` → `IR_*` (~1850 occ); `BB_LANG_*`→`IR_LANG_*` (27); IR API fns
  `BB_alloc`/`BB_free`/`BB_node_alloc`/`BB_lower_pat`→`IR_*` (~214). **Rationale:** leaving the node-kind
  enum as `BB_*` while the node type is `IR_t` (`switch(n->t){ case BB_VAR: … }`) reintroduces the exact
  IR/emit confusion this rename exists to remove — a half-renamed IR is worse than either pure state.
- **TIER C — STAYS `BB` (these ARE the emitted-construct layer, NOT the IR):** `BB_MEDIUM_*` (emission
  medium), `BB_MODE_*` (byrd-box execution mode), `BB_PLATFORM_*` (codegen target), `BB_templates`
  (template directory), the bb_*.h header guards (`BB_POOL_H`/`BB_EXEC_H`/`BB_BOX_H`/`BB_BROKER_H`/`BB_BUILD_BIN_H`),
  and ALL lowercase `bb_*` (324 identifiers — pool / broker / exec / templates / byrd-box). **Untouched.**

**Template boundary (Lon-clarified 2026-05-30) — templates are TRANSLATORS: they receive the IR
(`IR_t`) and emit BB asm (byrd-box x86).** So inside `src/emitter/BB_templates/*.cpp`, the IR-type/enum
tokens the templates CONSUME **do** get renamed (the 330 `BB_t`→`IR_t`, 134 `BB_PAT_*`→`IR_PAT_*`,
3 `BB_op_t`→`IR_e`) — that is the IR being handed to them. But the template MACHINERY stays `BB`/`bb`:
the file names (`bb_pat_span.cpp`), the `BB_templates/` directory, the `bb_*` function names, the
`g_emit.bb_*` fields, and `BB_MEDIUM_*`/`MEDIUM_TEXT`/`MEDIUM_BINARY`. Net effect on a template:
`bb_pat_span(BB_t * pBB)` → `bb_pat_span(IR_t * pBB)`, same file, same dir, still reading `g_emit`.
**NO `typedef IR_t BB_t;` alias** — zero `BB_t` remains after the rename (Reading X).

### ⛔ Gate suite — run before EVERY commit  (ALL THREE MODES per the TESTING DIRECTIVE above)
```bash
make scrip                                   # rc=0
make libscrip_rt                             # rc=0
bash scripts/test_smoke_snobol4.sh           # ALL 3 modes: m2 7/7 (HARD); m3 5/6 + m4 1/6 (tracked, reported) @ 18357d4
bash scripts/test_smoke_icon.sh              # m2 6/6 (HARD), m3 4/6 (tracked)
bash scripts/prove_lower2.sh                 # 37/37 topology
bash scripts/test_gate_sm_dead.sh            # <= 1
bash scripts/audit_concurrency_invariants.sh # OK
bash scripts/util_template_purity_audit.sh   # FACT 6 (byte-neutral baseline)
```
Behavioral gates MUST stay invariant under any byte-neutral change; any gate delta ⇒ a bug — revert that slice and diagnose.

### Slices (ATOMIC PER TOKEN — typedef/enum body + all uses change together so the build stays green)
- [x] **RN-IR-1** — `\bBB_graph_t\b` → `IR_graph_t` across `src/**` (24 files; smaller, first). Gate. Commit `RN-IR-1 BB_graph_t→IR_graph_t`.
- [x] **RN-IR-2** — `\bBB_t\b` → `IR_t` across `src/**` (88 files). Word-boundary exact (does NOT touch `BB_templates`/`BB_to_by`/lowercase). Gate. Commit. **[TIER A COMPLETE]**
- [x] **RN-IR-3** — `\bBB_op_t\b` → `IR_e` (enum type; `_e` = enum, distinct from the `_t` structs). Gate. Commit.
- [x] **RN-IR-4** — curated enum-member rename: the 125 `BB_op_t` values listed in `BB.h` (`BB_LIT_I`…`BB_PAT_ATP`) + `BB_OP_COUNT` + the `BB_GEN_*`/`BB_NFA_*`/`BB_CSET_*` members → `IR_*` (CONFIRMED: `BB_VAR`→`IR_VAR`, `BB_PAT_SPAN`→`IR_PAT_SPAN`, `BB_OP_COUNT`→`IR_OP_COUNT`, …). **NOT a blanket `BB_[A-Z]*`** — explicitly EXCLUDE every TIER-C token (`BB_MEDIUM_*`,`BB_MODE_*`,`BB_PLATFORM_*`,`BB_templates`,bb_*.h guards). Rewrite the enum body in `BB.h` AND every `case`/construction site in one pass. Gate. Commit.
- [x] **RN-IR-5** — `\bBB_LANG_(\w+)` → `IR_LANG_\1` (6 values: SNO/SCO/REB/ICN/PL/RKU). Gate. Commit.
- [x] **RN-IR-6** — IR API (CONFIRMED): `\bBB_alloc\b`→`IR_alloc`, `\bBB_free\b`→`IR_free`, `\bBB_node_alloc\b`→`IR_node_alloc`, `\bBB_lower_pat\b`→`IR_lower_pat` (watch: lowercase `bb_alloc`/`bb_node_id`/`bb_node_t` STAY); any remaining bare `BB` in comments/strings (the `(BB_t*)` casts were already converted by RN-IR-2). Gate. Commit. **[TIER B COMPLETE]**
- [x] **RN-IR-7a** (FILE rename — CONFIRMED, Lon 2026-05-30 "BB*.* files become IR*.* files") — `git mv src/include/BB.h src/include/IR.h`; update every `#include "BB.h"` across `src/**`, plus `Makefile` + `scripts/build_scrip.sh`. Guard is already `SCRIP_IR_H`. Gate. Commit.
- [x] **RN-IR-7b** (baseline artifacts — same rule) — the **1330 git-tracked `baselines/per_kind/**/BB_*.*`** files (x86/jvm/net/wasm × text/binary, named after IR kinds) → `IR_*.*` via basename prefix `BB_`→`IR_` (`for f in $(git ls-files 'baselines/per_kind/**/BB_*'); do git mv "$f" "$(dirname "$f")/$(basename "$f" | sed 's/^BB_/IR_/')"; done`). Pairs with RN-IR-4. NOTE: the per-kind diff gate is flagged STALE (SBL-G-2) so these are currently inert; rename keeps names consistent with the new IR kinds. No build gate (fixtures, not source) — verify `git ls-files 'baselines/per_kind/**/BB_*'` is empty. Commit.
  - ✅ **`src/emitter/BB_templates/` DIRECTORY STAYS `BB` (DECIDED, Lon 2026-05-30)** — templates are emit-side: they reach state only through `g_emit` globals, i.e. they live PAST the IR boundary, not in it. Not a `BB*.*` file, 140 path refs (src + Makefile + build_scrip.sh), TIER C. No directory rename.
- [x] **RN-IR-8** — zero-check + handoff. `grep -rhoaE '\bBB[_A-Z][A-Za-z0-9_]*' src` must return ONLY the TIER-C set (`BB_MEDIUM_*`,`BB_MODE_*`,`BB_PLATFORM_*`,`BB_templates`,bb_*.h guards); `git ls-files 'baselines/per_kind/**/BB_*'` empty. Full gate. `git pull --rebase && git push` (code repos first, `.github` last). Confirm `git log origin/main --oneline -1` shows the hash.

**Scope decision (Lon 2026-05-30) — FULLY SETTLED, no open items:** TIER A + TIER B are confirmed.
Enum members `BB_*`→`IR_*`, `BB_LANG_*`→`IR_LANG_*`, constructors `BB_alloc`/`BB_free`/`BB_node_alloc`/`BB_lower_pat`→`IR_*`,
and **all `BB*.*` files → `IR*.*`** (source header `BB.h`→`IR.h` + the 1330 `baselines/per_kind/**/BB_*.*`
artifacts) confirmed. **STAYS `BB`** (emit-side, reached only via `g_emit` globals — past the IR boundary):
the `BB_templates/` directory and TIER C tokens (`BB_MEDIUM_*`/`BB_MODE_*`/`BB_PLATFORM_*`/bb_*.h guards),
plus all lowercase `bb_*`. Ready to execute RN-IR-1 → RN-IR-8.

**✅ RENAME COMPLETE (2026-05-30, this session).** All 8 slices landed + RN-IR-8b cosmetic comment polish.
SCRIP commits `b2a13e2`(1)→`7cbd3c9`(2)→`2018dd6`(3)→`222755f`(4)→`8730787`(5)→`0466698`(6)→`15418a0`(7a)→`bc69550`(7b)→`9ff631f`(8)→`29aaac0`(8b),
on top of base `c334861`. **Zero whole-word IR identifiers remain as `BB_`** (verified: exact-111-member
grep = 0; `BB_t`/`BB_graph_t`/`BB_op_t`/`BB_LANG_*`/ctors = 0; baselines `BB_*` = 0). Every remaining
`BB[_A-Z]` token is emit/byrd-box machinery (Tier-C: PLATFORM/MEDIUM/MODE/WIRED/BROKERED/templates/LABEL/
PATCH/POOL/DCAP/BANNER/bb_*.h-guards/ENTER/ALPHA + the `BBCopyMap` Term-struct + box-descriptive `.cpp`
comments) OR the AST-layer `BB_DEFINE_NAMES` guard (ast.h — outside scope). Gates held INVARIANT every
slice: `make scrip` rc=0, `make libscrip_rt` rc=0, Icon m2 **6/6** (HARD), m3 2/6, sm_dead 1 (≤1),
FACT **6** (pre-existing baseline — predates `a0bb9be4`; my byte-neutral rename moved it 0). **NOT pushed
yet** (10 SCRIP commits local; `.github` goal-file local). Open follow-ups (Lon's call, NOT done): the
AST-layer `BB_DEFINE_NAMES`→`AST_DEFINE_NAMES`? and the vestigial `-DIR_DEFINE_NAMES` Makefile flag
(checked nowhere in src). NOTE the watermark's old "FACT 0" was stale.

---

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
SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh                                # 13/13
INTERP=$(pwd)/scrip SCRIP_M3_NATIVE=1 bash scripts/test_interp_broad_corpus_and_beauty.sh  # 195/280
```

For full failure list patch `head -40` to `head -300` in test_interp_broad_corpus_and_beauty.sh copy.

---

## Active rung: M3-NATIVE-4 — per-language bring-up + corpus parity (SNOBOL4)

### ⭐ MILESTONE (2026-05-29 Opus 4.8): NATIVE-ONLY GAP CLOSED

After SBL-1010 + SBL-1016, the broad-corpus partition has **ZERO native-only failures**:
every one of the 28 remaining native FAILs **also fails in `--interp` (mode-2)**. Native ==
mode-2 oracle == **252/280**. The "knock down remaining native-only failures" objective of this
rung is therefore effectively DONE — there are no more native-dispatch bugs in the broad corpus.
All further corpus climb now requires fixing the **mode-2 ORACLE** (which lifts BOTH modes
simultaneously, exactly as SBL-1016 demonstrated: fix once, both modes gain). Verified via
`comm -23 native_fails m2_fails` = empty. To re-confirm: run the broad corpus under
`SCRIP_M3_NATIVE=1` and under plain `--interp`, sort the two FAIL lists, diff them.

### Next phase: ORACLE-PARITY (lifts both modes)

**Completed (mode-2 oracle + native, terse — full narrative in git log / HANDOFFs):**
- [x] VARIABLE-ARGUMENT PATTERN FAMILY (SPAN/ANY/NOTANY/BREAK/BREAKX/LEN/POS/RPOS/TAB/RTAB accept `TT_VAR` args, resolved late in `bb_exec.c`) + SBL-SIZE-SHADOW. m2 248→253, native 255→256.
- [x] ANY/SPAN w/ CONSTANT charset EXPRESSION arg; charset-EXPR / ARBNO-combinator brokered wiring (XDump).
- [x] SBL-ARB-CAT-BACKTRACK (mode-3 native + mode-4 flat); ARB-as-pattern-VARIABLE backtracking (mode-2 oracle).
- [x] DEFERRED capture-commit; POS/RPOS-NON-FIRST-IN-CAT; 1010 SEGV (OPSYN-alias recursion); 1016 EVAL SEGV (deferred-expr dispatch).
- [x] 046/047 TAB/RTAB SIGSEGV native (site off-by-one + RTAB writeback); SPAN already complete (SBL-SPAN-2 was phantom); nested XDSAR `*var` in combinator under sm_run_native (walk_bb_flat DEFER case + tree-route + 16-byte align) — native 223→243.
- [x] Flip default to native (getenv gate removed; honest `[NO-SM-BB]`, no fallback).

**Open (mode-2 oracle gaps — fix oracle first, native parity follows):**
- [ ] 1011_func_redefine / 1013_func_nreturn / 1017_arg_local — fail in BOTH modes (DEFINE-redefinition, NRETURN-as-lvalue, ARG/local introspection). Audit-only bucket.
- [ ] Pre-existing m2 oracle gaps (audit-only): rungs 044/045/046/048/052/054/055/056/057 — `bb_exec.c` POS/RPOS/TAB/REM/star_deref/fail_builtin gaps.

- [~] **FENCE-commit / ALT-fall-through (124 + 114) — INLINE class FIXED; DEFER-capture-resume blocker remains.**
  SBL-ALT-CURSOR-RESTORE + SBL-FENCE-SEAL landed: Δ-advancing single-shot leaves set `β=self` (re-enter to undo Δ on ALT fall-through); FENCE saves Δ on α, restores on β (commit). Inline probes pass m2. **Blocker:** 124/114 reach the ALT through a pattern VARIABLE (`BB_PAT_DEFER`); on `bb_exec_resume` the alt entry is alt1's capture node, which can't distinguish "backtrack" from "commit/regrow" (same `inner.state>0` ambiguity as SBL-CAP-REGROW). Capture-transparency prototype (`resume_at` + `g_resume_backtrack` one-shot) made 124 green but regressed 3 sealed-FENCE-via-var tests (over-reach: re-enters a sealed FENCE). **NEXT FIX:** gate the capture's backtrack-delegation so it does NOT re-enter an inner that wraps a sealed/exhausted FENCE (delegate only when inner holds a live backtrackable generator). Clean floor = `77a39e82`; minimal repro of the pure DEFER-capture-resume gap = p8 (`token=('if'.K|SPAN.I)`).

### ⭐ TOP PRIORITY (Lon directive 2026-05-30): Complete all SNOBOL4 pattern BB BINARY and TEXT arms for mode-3 and mode-4

Every SNOBOL4 pattern BB template must have a working BINARY arm (mode-3 `--run`) and TEXT arm (mode-4 `--compile`). No pattern primitive may fall to the `default: jmp ω` stub once this rung is done. Honest `bomb_bytes()` stub is acceptable only as a temporary placeholder while the arm is being written; a permanent `jmp ω` for a real opcode is a RULES violation once the rung is declared complete.

**Missing BINARY arms (mode-3):** SPAN (SBL-SPAN-2 — deque pattern), ARBNO (SBL-ARBNO-3 — deque pattern), REM, ABORT, FENCE, ALT (combinator EP-walk present but needs corpus validation), CAT (same).
**Mode-4 TEXT arm gaps:** DEFER needs alignment fix (`push r10; push r10` convention per SBL-CAP-OUTPUT-R10); SBL-M4-FLATWIRE — `--compile` must flat-wire at emit time rather than brokering at runtime.
**Work order:** fill BINARY arms first (SPAN → ARBNO → REM → ABORT → FENCE), gate each via `--run` corpus delta, then audit TEXT arms for mode-4.

### ⭐⭐ SESSION RUNG #0 (Lon "Eureka" directive 2026-05-31): SBL-PAT-BB — pattern = built BB graph (modes 3 & 4 ONLY)

**SCOPE: modes 3 (`--run`, BINARY) and 4 (`--compile`, TEXT) ONLY. Mode 2 (interp) is NOT in scope and
must NOT regress.** Full architecture in **ARCH-SNOBOL4.md → "Native pattern architecture — modes 3 & 4"**
and ARCH-x86.md → "Two block TYPES (BB vs XA)". The five phases of `SUBJ ? PAT [= REPL]`, each emitted as
BB(s) (the ONLY vehicle that does work in modes 3/4 — XA blocks only wrap/stitch):

> **THE EUREKA.** Phase 1 build SUBJECT (easiest) → SUBJECT BB loads `Σ/δ/Δ`. Phase 2 build PATTERN →
> **builder BBs that build OTHER BBs dynamically** (a SNOBOL4 pattern is a runtime byrd-box graph: `'a'|'b'`
> CONSTRUCTS). Phase 3 RUN pattern → the generic **BB_MATCH box** runs the SPITBOL ch.18 scanner over the
> built graph against the subject (unanchored start-loop unless `&ANCHOR`, four-port backtrack, NO value
> stack). Phase 4 build REPLACEMENT (can fail). Phase 5 do REPLACE (fails if subject not an lvalue —
> `"hello"`, `99`). **Build (ph.2) and run (ph.3) are GENUINELY SEPARATE.** The current mode-2 `IR_SCAN`
> super-node + hidden `IR_alloc` sub-graph is the WRONG layer (`sno_ring_to_tree` anti-pattern in the
> lowerer) and is NOT this design.
>
> **THEN — OPTIMIZATION (after ph.1–5 work): INVARIANT-PATTERN BAKE.** Collapse any maximal run of builder
> BBs that builds an INVARIANT pattern (all components compile-time constant: literal str/int/cset, fixed
> LEN/POS/RPOS, constant ALT/CAT of such) into ONE **STATIC pattern BB BAKED into the generated code**
> (emitted once as sealed data/code, no runtime rebuild). Only VARIANT builders (`SPAN(VAR)`, `ANY(expr)`,
> deferred `*EXPR`, indirect `$NAME`) stay dynamic. const subtree ⇒ bake; references-runtime ⇒ keep builder.

Each step's discipline: prove the four-port TOPOLOGY first (`prove_lower2.sh`: node counts + α/β/γ/ω), then
the BINARY arm (verify mode-3 `--run`), then the TEXT arm (verify mode-4 `--compile` → `as` → `gcc` → run).
Smoke target ladder: `S 'b'` (plain match) → `S 'b' = 'X'` → `aXc` (match+replace).

- [x] **PB-0 — SUBJECT BB (phase 1).** Lower the subject value-expr → a SUBJECT box that loads `Σ` (base),
  `δ` (cursor=0), `Δ` (len) into the locked registers / `ζ` frame. BINARY + TEXT arms. Prove topology on
  `S 'b'`; verify mode-3 `--run` loads the subject (disasm / probe).
  **[DONE 2026-05-31, Opus 4.8]** New `IR_SUBJECT` kind + `lower2_subject_entry` (lower.c) + mode-2 arm
  (bb_exec.c) + `bb_sno_subject.cpp` template (BINARY 58-byte + TEXT @PLT arms) + emit_core dispatch +
  `flat_drive_sno_subject`/walk_bb_flat case (emit_bb.c) + `rt_sno_subject_load` (rt.c, returns {base,len}
  in rax:rdx). Box stores Σ→`[r12+off]`, Δ→`[r12+off+8]` in a 16-byte ζ-frame slot (ABI-safe, r12 preserved
  by the flat prologue; per SPITBOL ch.18 the cursor δ is zeroed when the match begins, so it is the
  matcher's state — SUBJECT loads only the fixed whole + bound). **v_scan deliberately NOT rewired** (the
  mode-2 IR_SCAN super-node stays intact → zero regression); IR_SUBJECT is exercised by the prove_lower2
  topology gate (2 new cases) + a standalone mode-3 execution probe (`SUBJECT('abc')→SUCCEED` JIT'd via
  `sno_flat_chain_build`, ran, confirmed Σ base="abc" / Δ len=3). v_scan re-stitch to the five-phase chain
  is deferred to PB-2/PB-5 (when BB_MATCH consumes Σ/δ/Δ in one sealed sequence). Gates: prove_lower2 59/0
  (was 57), smoke m2 7/7 (HARD) / m3 5/6 / m4 0/6 (UNCHANGED), concurrency invariants OK, sm_dead 1.
- [x] **PB-1 — PATTERN-BUILDER BB, literal first (phase 2).** Lower `TT_QLIT` pattern → a builder BB whose
  runtime effect CONSTRUCTS a LIT pattern-box; the built pattern-graph head lands in a `ζ` slot. BINARY +
  TEXT. (This is the "BBs that build BBs" core — model the construction protocol here, reuse for all kinds.)
  **[DONE 2026-06-01, Opus 4.8]** New `IR_PAT_BUILD_LIT` kind (IR.h, append-only) + `lower2_pat_build_entry`
  (lower.c): `TT_QLIT` → ONE builder box, bounded single-shot (β=ω; a builder is NOT a generator). DISTINCT
  from the matcher-leaf `IR_PAT_LIT` the mode-2 IR_SCAN super-node consumes (stays intact → ZERO regression).
  `rt_sno_pat_build_lit` (rt.c) is VALUE-STACK-FREE — it wraps the proven `pat_lit` constructor and returns
  the built `PATND_t*` head (NOT the deleted `rt_pat_lit` vstack-assembler wrapper). `bb_sno_pat_build_lit.cpp`
  template: BINARY (40-byte) + TEXT (@PLT) arms, mirroring `bb_sno_subject`; literal is RO (`[rip+disp]`/movabs),
  built head is RW into an 8-byte ζ-slot `[r12+off]` (PER-BOX LOCAL STORAGE FACT RULE). emit_core dispatch +
  `flat_drive_sno_pat_build_lit`/walk_bb_flat case (emit_bb.c) + dormant mode-2 arm (bb_exec.c, concurrency
  completeness). v_scan deliberately NOT rewired (re-stitch is PB-2). Gates: prove_lower2 **64/0** (+1 BLDLIT
  topology: own α, β=ω, 1 real node), smoke m2 **7/7 HARD** / m3 5/6 / m4 0/6 (UNCHANGED), concurrency
  invariants OK, purity +0 (fail-loud is MEDIUM_BINARY-exempt), no-vstack `g_vstack`==0. **Mode-3 execution
  probe PASS**: `BLDLIT('abc')`→SUCCEED JIT'd via `sno_flat_chain_build`, ran with `rt_frame`, built a
  `PATND_t{kind=XCHR, STRVAL="abc"}`; disasm confirms stackless ζ=r12 frame, no value stack.
- [~] **PB-1-REWORK — SUPERSEDED by the CORRECTED PATTERN ARCHITECTURE (2026-06-01).** PB-1 as landed
  (`6483bb5`) built a `PATND_t` (the type slated for demolition) via `rt_sno_pat_build_lit`. Per the
  corrected architecture above, a pattern element is an EMITTED BYRD-BOX (`bb_box_fn`), not a `PATND_t`, and a
  literal is INVARIANT → it is the EXISTING `IR_PAT_LIT` matcher box (`bb_lit.cpp`) referenced via
  **`REF_INVARIANT`** as a sealed element, with NO runtime builder (Fork A/E). So `IR_PAT_BUILD_LIT` +
  `rt_sno_pat_build_lit` + `bb_sno_pat_build_lit.cpp` are to be RETIRED, replaced by `REF_INVARIANT` +
  `IR_PAT_LIT`. The `rt_sno_match_lit` ch.18 scan kernel (PB-2 prep, `PATND_t`-free, raw subj/lit, unit-tested
  7/7) SURVIVES as the literal element matcher's inner scan. **Done in PB-RB-1 below** (the rebuilt ladder);
  this row marks the OLD PB-1 superseded so its watermark "done" is not mistaken for the corrected design.
- [ ] **PB-2 — BB_MATCH box (phase 3). [RE-CUT — see PB-RB ladder below; OLD text SUPERSEDED.]** The MATCH
  PHASE survives but as a `bb_box_fn`-graph DRIVER (broker, ch.18 outer start-loop), NOT a `PATND_t` reader.
  The draft PB-2 (`IR_PAT_MATCH` + `bb_sno_match.cpp` calling a `PATND_t`-inspecting `rt_sno_match`) was
  REVERTED (uncommitted) on 2026-06-01 when the corrected architecture landed. `rt_sno_match_lit` (the scan
  kernel) remains valid. See PB-RB-3 below.
- [ ] **PB-OPT — [RE-CUT — see PB-RB-OPT below; OLD `tree_t`-bake mechanism SUPERSEDED.]** The OLD PB-OPT
  baked the pattern AST as a static `tree_t` and had ONE BB tree-walk-construct the graph from it. Per the
  corrected architecture, there is NO `tree_t` in the pattern path; the invariant fast path is the
  all-invariant single-sealed-BLOB freeze (REF_INVARIANT hands MATCH the sealed head). See PB-RB-OPT.

---

### ⭐⭐ REBUILT LADDER — PB-RB (CORRECTED PATTERN ARCHITECTURE, 2026-06-01)

Supersedes the PB-1/PB-2/PB-3/PB-OPT mechanism above (kept for history, marked SUPERSEDED). The matcher
boxes are the EXISTING `IR_PAT_*` templates (Fork C); the only NEW boxes are `REF_INVARIANT`, `STITCH_SEQ`,
`STITCH_ALT`, and the phase-3 `BB_MATCH` driver. Same discipline every step: prove four-port TOPOLOGY first
(`prove_lower2.sh`), then BINARY arm (mode-3 `--run`), then TEXT arm (mode-4 `--compile`→`as`→`gcc`→run).
**Mode-2 (`IR_SCAN`) stays intact and MUST NOT regress** (m2 7/7 HARD) — the native chain is modes-3/4;
full `IR_SCAN` retirement is deferred to PB-RB-CONV when the native chain has breadth. Each box reads its
inputs RO `[rip+disp]` (sealed head address, literal bytes) or RW `[ζ+off]` (built head, match state) — NO
`PATND_t`, NO `tree_t`, NO value stack, NO ring (PER-BOX LOCAL STORAGE + NO-VALUE-STACK FACT RULES).
Smoke ladder unchanged: `S 'b'` (plain) → `S 'b' = 'X'` → `aXc`.

- [x] **PB-RB-1 — REF_INVARIANT + retire the PATND_t literal builder.** Delete `IR_PAT_BUILD_LIT` /
  `rt_sno_pat_build_lit` / `bb_sno_pat_build_lit.cpp` (the PATND_t literal builder). Add `IR_REF_INVARIANT`
  (IR.h, append-only) + `bb_ref_invariant.cpp`: loads a sealed element `bb_box_fn` head (RO `[rip+disp]` /
  movabs) into a `ζ`-slot. The sealed element for a literal is the EXISTING `IR_PAT_LIT` matcher box
  (`bb_lit.cpp`); `rt_sno_match_lit` survives as its inner scan. lower `TT_QLIT` pattern → REF_INVARIANT over
  a sealed `IR_PAT_LIT`. Prove topology; mode-3 probe: REF_INVARIANT('b') yields a `bb_box_fn` head in its
  ζ-slot whose code is the `'b'` literal matcher. (No runtime construction — Fork A/E.)
  **[DONE 2026-06-01, Opus 4.8 — EMIT ARM + PROBE]** RETIRE half landed earlier (`6343198`: IR_PAT_BUILD_LIT
  family removed, lower2_pat_build_entry repointed to IR_REF_INVARIANT over a sealed IR_PAT_LIT, prove 64/64).
  THIS turn = the EMIT ARM that was the remaining work: (1) `bb_ref_invariant.cpp` BINARY (25-byte) + TEXT arms
  — load the sealed element `bb_box_fn` HEAD (emit-time constant: `movabs rax,head` BINARY / `lea rax,[rip+lbl]`
  TEXT, RO never on a stack) into an 8-byte ζ-slot `[r12+off]` via `bb_slot_alloc`, then `jmp γ`; β = `jmp ω`
  (bounded single-shot, Fork A/E — NO runtime construction). Modeled on bb_sno_subject.cpp; patch tuple
  `{19,23,24}/{γ,β,ω}/{false,true,false}`. (2) `emit_bb.c` — new emitter-global `g_emit_cfg` (exposes the active
  IR_graph_t to the emit path so a node's operand_aux sidecar is resolvable, mirroring bb_exec.c's g_current_cfg;
  set/restored in sno_flat_chain_build / _text); `pre_build_children` + `pre_build_children_text` recognize
  IR_REF_INVARIANT and pre-build its sealed child resolved via `bb_operand_aux_get` (NOT bb_pat_kid, PEERS RULE);
  the two SNOBOL chain builders run a REF-specific child prebuild (`sno_chain_prebuild_children[_text]`) GUARDED
  by `has_ref` so they stay byte-neutral to every prior shape; `flat_drive_sno_ref_invariant` resolves the cached
  child head and hands it to the box via `g_emit.child_fn`/`bb_child_fn`/`bb_child_lbl`. (3) emit_core dispatch
  was already wired (emit_core.c IR_REF_INVARIANT → bb_ref_invariant). **MODE-3 PROBE PASS** (committed artifact:
  `test/snobol4/pat_bb/probe_pb_rb_1_ref_invariant.c` + `scripts/test_sno_pat_bb_probe.sh`): JIT'd
  SUBJECT('abc') → REF_INVARIANT('b') → SUCCEED via `sno_flat_chain_build`, ran with `rt_frame`, result.v=1.
  **DISASM-VERIFIED**: REF box = `movabs $head,%rax ; mov %rax,0x10(%r12) ; jmp γ` / β:`jmp ω` — the sealed head
  address (a real BB-pool box) lands in ζ-slot `[r12+0x10]`, stackless (ζ=r12, `push r12;mov r12,rdi` prologue),
  NO value stack; and the loaded head disassembles as the EXISTING bb_lit('b') four-port matcher (δ from [r10],
  bounds-check vs Σlen, memcmp 1 byte, advance δ → γ). The sealed element is REFERENCED, not run (running is
  PB-RB-3 BB_MATCH). v_scan NOT rewired (mode-2 IR_SCAN super-node intact → ZERO regression; retirement is
  PB-RB-CONV). Gates ALL match watermark: make scrip rc=0, libscrip_rt rc=0, SNOBOL4 m2 **7/7 HARD** / m3 5/6 /
  m4 0/6, Icon m2 **11/11 HARD** / m3 11/11 / m4 9/11, prove_lower2 **64/64**, sm_dead 0, concurrency OK, purity
  7 (MEDIUM_BINARY-exempt baseline), no-vstack `g_vstack`==0. **NEXT (#1): PB-RB-2** (matcher-box four-port ABI —
  how the head box-graph is driven over Σ/δ/Δ via α/β/γ/ω; ground in the canonical Icon/Prolog brokered-graph
  pattern per CONSULT CANONICAL SOURCES) then **PB-RB-3** (BB_MATCH driver reads REF_INVARIANT's ζ-slot head +
  SUBJECT's Σ/δ/Δ and drives the ch.18 unanchored outer start-loop). NOTE on rebuild: `scrip` and
  `out/libscrip_rt.so` MUST be rebuilt in LOCKSTEP — a stale `.so` against a fresh `scrip` shows phantom mode-3
  failures (2/6); always `bash scripts/build_scrip.sh && make libscrip_rt` together before gating.
- [x] **PB-RB-2 — the matcher-box four-port ABI (drive ONE element).** Pin down how the four-port driver runs a
  single matcher element box (`IR_PAT_LIT`) over Σ/δ/Δ via α/β/γ/ω: α tries match at δ, γ on success
  (advance δ, leave span), ω on fail, β to re-offer (generators only). Ground in the canonical
  Icon/Prolog brokered-graph pattern (CONSULT CANONICAL SOURCES rule). Verify the existing `IR_PAT_LIT`
  BINARY/TEXT arms honor it (or adapt minimally). This is the substrate PB-RB-3 drives.
  **[DONE 2026-06-01, Opus 4.8 — SPEC + VERIFY, no code adaptation needed.]** ⚠ STALE REF FIXED: the step said
  "ground in `bb_broker.c`", but `bb_broker.c` (the driver) was DELETED in `646a543` (C-byrd-box teardown). The
  surviving four-port driver is `bb_exec.c` (mode-2 oracle); its `rt_sno_exec_scan` is the ch.18 reference driver
  (anchored/unanchored start-loop). Grounded the ABI there + SPITBOL ch.18 ("Pattern Matching" algorithm steps
  1-6) + the ratified X86-64 REGISTER CONVENTION.
  **PINNED ABI — see "PB-RB-2 MATCHER-ELEMENT FOUR-PORT ABI" block below.** Key result: `IR_PAT_LIT`
  (`bb_lit.cpp`) HONORS the port contract in BOTH arms with ZERO adaptation — α bounds-checks `δ+len ≤ Δ`,
  memcmps Σ+δ, advances δ, `jmp γ`; mismatch/overflow `jmp ω` (δ unchanged); β is bounded single-shot (`δ -= len;
  jmp ω` — a literal has NO implicit alternative). Verified vs the PB-RB-1 mode-3 probe disasm + a byte/text
  re-read of both arms this session. The whole SNOBOL pattern family (`bb_pat_any/pos/span/…`) shares this exact
  `[r10]`-cursor / `[rip+Σ]`/`[rip+Σlen]` model (grepped, uniform). **OPEN FORK handed to PB-RB-3 + flagged for
  Lon — see the ABI block's "SUBJECT-STORAGE LOCATION" note: three coexisting homes for Σ/δ/Δ (ratified
  R13/R14/R15 · SUBJECT's ζ-slots · legacy `[r10]`/`[rip+Σ]`); BB_MATCH is the bridge; the family-wide register
  migration is a SEPARATE LOCKSTEP sweep, NOT folded into PB-RB-2/3.** Gates UNTOUCHED (spec-only, no compile this
  step): m2 7/7 HARD / m3 5/6 / m4 0/6, prove_lower2 64/64, sm_dead 0, concurrency OK, g_vstack==0 @ `77bbebc`.

> **⭐ PB-RB-2 MATCHER-ELEMENT FOUR-PORT ABI (pinned 2026-06-01, Opus 4.8). The substrate PB-RB-3's BB_MATCH
> drives. Grounded in SPITBOL ch.18 + `bb_exec.c rt_sno_exec_scan` (the ch.18 reference driver) + the ratified
> X86-64 REGISTER CONVENTION. This is a CONTRACT statement, not new code — `IR_PAT_LIT` already conforms.**
>
> **SUBJECT MODEL (names — the casing carries meaning AND the oracle-C vs native-register casing is INVERTED;
> wiring it backwards is the failure mode this note exists to prevent):**
>   - **Σ** (R13) = subject BASE ptr (the fixed whole).
>   - **δ** (R14, lowercase) = CURSOR (the moving scan position), zeroed when the match begins (ch.18 step 1).
>   - **Δ** (R15, uppercase) = subject LENGTH / END (the fixed bound).
>   - ⚠ **In the mode-2 oracle C (`bb_exec.c`/`rt.c`/`stmt_exec.c`) the CURSOR global is named `Δ` (UPPER) and the
>     LENGTH is `Σlen`/`Ω`** (verified: `rt.c:776` `Δ = 0` at match start = cursor; `stmt_exec.c:47` `Σlen` =
>     length; JS `_bb_Δ` "cursor position", `_bb_Ω` loop bound). The RETIREMENT rename sweep **`Δ(cursor)→δ`,
>     `Ω→Δ`, `Σlen→Δ`** reconciles oracle-C ↔ native-register: **oracle-C `Δ` ≡ native `δ` (cursor); oracle-C
>     `Σlen`/`Ω` ≡ native `Δ` (length).**
>
> **FOUR PORTS (per element box; map 1:1 to SPITBOL ch.18 algorithm steps 3-6):**
>   - **α (fresh entry)** = step 4 "apply current pattern at current cursor". Read δ; if `δ + matchlen > Δ` →
>     `jmp ω` (bound check). Compare/scan Σ at offset δ. On match: advance δ past the matched span (step 4
>     "advance the cursor past the characters matched"); the span is IMPLICIT in δ_before..δ_after (a bounded leaf
>     leaves no separate span slot); `jmp γ`. On mismatch: `jmp ω` with **δ UNCHANGED** (the element bound nothing).
>   - **γ (success port)** = step 5 "if subsequent, point to it". Emitter-patched to the successor element's α (or
>     BB_MATCH's success continuation for the last element). The box only `jmp lbl_γ`; it NEVER picks the target.
>   - **ω (fail port)** = step 6 "pop the stack / advance starting cursor". Emitter-patched to the predecessor's β
>     (inner backtrack) or, at the graph root, BB_MATCH's OUTER-loop retry (advance starting δ unless anchored).
>     The box only `jmp lbl_ω`.
>   - **β (resume entry)** = re-offer on backtrack. **BOUNDED single-shot leaf** (literal / LEN / POS / RPOS / TAB
>     / RTAB): β UNDOES its δ advance (`δ -= matchlen`) and `jmp ω` — no alternative to offer. **GENERATOR** (ARB /
>     ARBNO, span-shrink/grow): β yields the next alternative (a different δ) and `jmp γ`, or exhausts → `jmp ω`.
>     (ch.18: "ARB behaves as `(LEN(0)|LEN(1)|LEN(2)|…)`" — the implicit-alternative generator; the bounded leaf
>     has none. This is the ONLY α/β-port difference between leaf and generator.)
>
> **VERIFIED — `IR_PAT_LIT` (`bb_lit.cpp`) conforms, BOTH arms, NO adaptation:** α = `mov eax,[δ]; add eax,len;
> cmp vs Δ(Σlen); jg ω; load Σ+δ; memcmp lit; jne ω; δ += len; jmp γ` (BINARY 121-byte patch tuple
> `{22,89,105,109,121}/{ω,ω,γ,β,ω}` + TEXT `memcmp@PLT` — SAME processing, only bytes-vs-GAS differ). β = `δ -=
> len; jmp ω` (bounded single-shot). Confirmed by the PB-RB-1 probe disasm (the REF_INVARIANT-loaded head IS this
> matcher) + this session's byte/text re-read. The pattern family (`bb_pat_any/pos/span/…`) is uniform on this.
>
> **OPEN — SUBJECT-STORAGE LOCATION (the one unresolved fork; PB-RB-3's bridge, NOT a port-contract issue).**
> Three homes for Σ/δ/Δ coexist today: **(1)** ratified convention Σ=R13/δ=R14/Δ=R15 (registers); **(2)** SUBJECT
> box (PB-0, `bb_sno_subject.cpp`) Σ=`[ζ=r12+off]`, Δ=`[r12+off+8]` (ζ-frame slots), δ "owned by MATCH"; **(3)**
> legacy family (`bb_lit`+siblings) δ=`[r10]`, Σ=`[rip+Σ]`, Δ=`[rip+Σlen]` (sealed data labels). The
> `[rip+Σ]`/`[rip+Σlen]` form is **mode-3-in-process-only** (a baked address breaks mode-4 relocatability — the
> RW-frame rule). **✅ RESOLVED (Lon directive 2026-06-01): adopt the REGISTER model for the pattern family** —
> conform the SNOBOL pattern templates to the ALREADY-RATIFIED convention (Σ=R13, δ=R14, Δ=R15, ζ=R12). **This is
> NOT a change to the convention table** (the byte-identical-×3 table already says R13/R14/R15), so it is NOT a
> lockstep edit — it is the SNOBOL session conforming ITS OWN boxes (`bb_pat_*`) to the table, squarely in its
> lane (EDIT ONLY YOUR OWN LANGUAGE'S BOXES). Lockstep would bite only if the TABLE changed, which it does not.
> BB_MATCH (PB-RB-3) is the register-establishment point: its α loads R13←Σ-slot, R15←Δ-slot, R14←0 from
> SUBJECT's ζ-frame, then drives the element graph; the elements read R13/R14/R15 directly (the **REG ladder**
> below). **⭐ MAJOR PAYOFF: this is ALSO the SNOBOL mode-4 unblocker** — the `&Σ`/`&Σlen` imm64 bakes
> (`TEMPLATE_ADDR_SIGMA`/`TEMPLATE_ADDR_SIGLEN` = addresses of the emitter-process globals) are the reason m4 is
> 0/6 for patterns; removing them = relocatable boxes that a standalone `--compile` binary can run.

---

> **PB-RB-3 DESIGN — RESOLVED (Lon 2026-06-01): MODEL A (INLINE-JUMP).** BB_MATCH `jmp`s the element's α and is
> re-entered via its ω — the proven combinator mechanism (`walk_bb_flat`, as XCAT/XALT), NO `(ζ,int entry)` C call
> (honors the NO-C-BYRD-BOX FACT RULE; `bb_broker.c` is deleted). REF_INVARIANT's load-a-sealed-head-by-call model
> is therefore NOT the base-case drive — it is the primitive for PB-RB-OPT's all-invariant BLOB freeze and
> pattern-valued vars (Fork B) only; the base single-element case emits the element INLINE.

- [x] **PB-RB-3 — BB_MATCH driver (phase 3), BINARY arm + edge probes DONE (2026-06-01, Opus 4.8; HEAD `706d665`).**
  Inline-jump (Model A). `flat_drive_match` (emit_bb.c) resolves the element from `operand_aux[0]` (PEERS RULE) and
  inline-emits it via `walk_bb_flat(elem, lbl_γ, match_advance, elem_β)`. `bb_match.cpp` BINARY: α loads Σ/Σlen from
  SUBJECT's ζ-slot (`g_sno_subject_slot`) + re-establishes `r10=&Δ` + seeds start=0; `match_retry` sets `Δ=start, jmp
  elem_entry`; `match_advance` (element-ω target) is ch.18 step 6 (`start++; cmp start,Σlen; jg →ω; &kw_anchor jne
  →ω; jmp match_retry`); β=`jmp ω`. Box de-named per Lon (`bb_sno_match`→`bb_match`, `g_sno_match_*`→`g_match_*`).
  LEGACY SUBJECT MODEL deliberate (Σ/Σlen globals + cursor in Δ via `[r10]`, the cells `bb_lit` still reads) until
  the REG ladder migrates elements to R13/R14/R15. TEXT arm = `bomb_text` stub (PB-RB-8). v_scan NOT rewired (mode-2
  IR_SCAN intact → retire is PB-RB-CONV). Probes (`test/snobol4/pat_bb/`, in `test_sno_pat_bb_probe.sh`, 3/3):
  `probe_pb_rb_3_match` (happy path, `'b'` in `'abc'`, v=1) + `probe_pb_rb_3_match_fail` (whole-match-fail `'z'`→v=99;
  anchored-fail `&ANCHOR=1` suppresses the slide→v=99; unanchored control→v=1). Runtime contract (xa_flat_epilogue):
  v==1 SUCCEED / 99 FAIL. Gates: SNOBOL4 m2 7/7 HARD / m3 5/6 / m4 0/6, Icon m2 12/12 HARD / m3 12/12 / m4 12/12,
  prove_lower2 65, sm_dead 0, concurrency OK, purity 7, g_vstack 0.
- [ ] **PB-RB-4 — STITCH_SEQ / STITCH_ALT (the graph builders).** **TOPOLOGY PREREQ PROVEN (e39c329):**
  `prove_lower2.c` `MATCH('a' 'b')` (PATMAT + wire_seq(IR_PAT_CAT) + 2 PLIT = 4 nodes) and `MATCH('a'|'b')`
  (PATMAT + wire_alt(IR_PAT_ALT) + 2 PLIT = 4) — `lower2_match_entry` calls `lower2(cx,e,m,m,…)` under
  ROLE_PATTERN, which ALREADY handles TT_CAT/TT_ALT, so the lowering/topology layer EXISTS; the genuinely-new
  PB-RB-4 work is the emitter-side STITCH wiring + mode-3 drive, NOT the IR topology. Remaining: add
  `IR_STITCH_SEQ` / `IR_STITCH_ALT`
  (IR.h) + `bb_stitch_seq.cpp` / `bb_stitch_alt.cpp`: read two child heads from `ζ`-slots, wire their four
  ports (runtime twin of LOWER's `wire_seq`/`wire_alt` — SAME port equations), leave the combined head +
  `{entry,exit,fail}` descriptor in a `ζ`-slot. ε-merge boundaries (Fork D; reuse `bb_nfa.cpp`). Lower
  `TT_CAT`/`TT_ALT` pattern → REF_INVARIANT children + STITCH (all-invariant case still wires instances; the
  BLOB-freeze is PB-RB-OPT). Prove topology + mode-3 `S ('a' | 'b')` and `S 'a' 'b'`.
- [ ] **PB-RB-5 — operand-variant element matchers (Fork A).** `LEN(N)`/`SPAN(cvar)`/`ANY(expr)` etc.:
  the EXISTING `IR_PAT_LEN`/`IR_PAT_SPAN`/… matcher box reads its operand late from a `ζ`-slot (operand
  produced by a preceding value box, ref via `operand_aux`). NO builder box — operand-binding only. Prove +
  mode-3 `S LEN(2)`, `S SPAN('abc')`.
- [ ] **PB-RB-6 — BB_PAT_BUILD for STRUCTURAL variance (Fork A/B).** `*E` / `$NAME` / pattern-valued var:
  `IR_PAT_BUILD_*` boxes that SPLICE (wire ports) the runtime box-graph (a pattern-valued variable already
  holds a `bb_box_fn` graph — Fork B; `*E`/EVAL/CODE evaluate/compile first via the `tree_t` path) and stitch
  into the surrounding sealed pieces. Prove + mode-3 `P = 'x'; S P` and `S *E`.
- [ ] **PB-RB-7 — REPLACEMENT BB (ph.4) + SUBSTITUTION BB (ph.5).** Replacement value-expr → REPLACEMENT
  BB (can fail). SUBSTITUTION BB: lvalue-check (fail for literal/number subject), splice
  `Σ[0:m_start]+repl+Σ[m_end:]`, assign back. mode-3 `S 'b' = 'X'` → `aXc`.
- [ ] **PB-RB-CONV — IR_SCAN convergence (retire the dual shape).** Once the native chain
  (SUBJECT→REF/BUILD/STITCH→MATCH) covers the corpus breadth, retire `IR_SCAN`: lower `TT_SCAN` to the native
  chain for ALL modes (mode-2 arm drives the same box-graph), removing the super-node + the dual shape. Gate:
  m2 corpus parity held; broad corpus ≥ prior.
- [ ] **PB-RB-8 — mode-4 parity sweep.** Every PB-RB box's TEXT arm assembles+links+runs; `--compile` smoke
  ladder green. Driver re-stitch for `--compile` lands here (LOWER emits the graph; no `sno_ring_to_tree`).
- [ ] **PB-RB-OPT — ALL-INVARIANT BLOB FREEZE (the optimization).** When a pattern is FULLY invariant,
  collapse its REF_INVARIANT + STITCH sequence into ONE sealed `bb_box_fn` BLOB emitted at compile time (the
  wiring frozen to direct jumps, no ε, no runtime stitch); REF_INVARIANT hands MATCH that sealed head
  directly. Variant patterns keep instance-level wiring. Gate: a fully-invariant pattern emits ONE sealed
  BLOB (verify `--dump`/disasm); native behavior unchanged (smoke ladder green). This is the MAX OPTIMIZATION
  — correctness (instance-wiring) first, freeze second.

---

### ⛔⛔ SESSION RUNG — BROKERED-MODE-ERADICATION (Lon directive 2026-06-01, Opus 4.8). THERE IS NO NEED FOR TWO WAYS TO ENTER A BOX.

**THE DIRECTIVE (Lon, verbatim intent):** "Any funky `int entry` MUST be gone. There is no need for two." A box is entered EXACTLY ONE way — a **jump to its α or β label**. The `(void *ζ, int entry)` **call-with-selector** is the second way, and the *existence* of two ways is the confusion. It is FORBIDDEN per the "NO C BYRD-BOX FUNCTIONS — JUMP TO α/β LABELS" FACT RULE at the top of this file. "Still compiles today" is NOT "needed" — propping the brokered path up to keep the build green is the exact green-build preservation that FACT RULE outlaws. **`bb_build_brokered` is NOT needed; it goes.**

**HONEST STATE (verified by grep 2026-06-01 — what `cc23c9f` did NOT finish).** The *driver* (`bb_broker.c`) and the C *functions* with the `(ζ,int entry)` signature were deleted. But the **emit-side brokered CALLING CONVENTION survives** and is the residue to eradicate:
- **`bb_build_brokered(IR_t*)`** (`emit_bb.c:~2196`, decl `emit_bb.h:13`) — emits a box with a `push rbp;mov rbp,rsp` brokered prologue (`0x55 0x48 0x89 0xE5`) in `EMIT_BINARY_BROKERED` mode, producing a `bb_box_fn` *called* with `(ζ,entry)`.
- **`EMIT_BINARY_BROKERED` (=2) + `g_bb_brokered` flag** (`emit_core.h:18`, `emit_core.c:18,30`) and the **`BB_BROKERED`/`BB_WIRED` macros** (`emit_core.h:55-56`) — **VERIFIED: the macros are read NOWHERE (pure dead weight).**
- **`BB_MODE_BROKERED`/`BB_MODE_DRIVER`/`BB_MODE_LIVE` + `bb_build_pure_mode`** (`emit_bb.c:~2230`; `g_bb_mode` set at `rt.c:201`, `stmt_exec.c:63`; branched at `stmt_exec.c:274,278,308,338`).
- **The actual `(ζ,int entry)` call convention lives in exactly TWO templates** — **`bb_capture.cpp`** and **`bb_arbno.cpp`** (`movabs rax, child_fn; edi=ζ; esi=entry(0=α/1=β); call rax; cmp eax,99`). These two boxes are the ONLY real reason `bb_build_brokered` still has live callers. (`bb_pat_defer.cpp` only ALIGNS for the brokered-child case in a comment + dynamic `and rsp,-16`; it calls `rt_defer_match@PLT`, NOT a child box — once the brokered-child context is gone, its alignment dance can simplify but it is not itself a brokered box. **`bb_ref_invariant.cpp` (PB-RB-1) is CLEAN** — it loads `child_fn` as a VALUE via `movabs`/`lea` and NEVER calls it.)
- The `stmt_exec.c:274-338` callers sit inside `exec_stmt`/`exec_stmt_blob` PATND paths that **already `abort()`** ("PATND->IR bridge removed"; `exec_stmt_blob` aborts outright at `:359`) — so those callers are dead-but-compiled.
- `bb_node_t {fn,ζ,ζ_size}` + the `bb_box_fn = DESCR_t(*)(void*,int)` typedef were KEPT by `cc23c9f` (the typedef slips past the FACT-RULE completion-test grep via `grep -v typedef`). The `int` param in the typedef is the last vestige of the selector; it goes too once no caller passes an entry.

**ORDER (FACT-RULE-sanctioned: convert the holdouts to jump-to-α/β FIRST, then delete the builder; a deliberately-broken build between rungs is acceptable, a surviving brokered box is not).** The STITCH_SEQ/STITCH_ALT graph-wiring of PB-RB-4 is what gives CAPTURE/ARBNO a jump-wired form to convert *to*; if BROK-1/BROK-2 are done before PB-RB-4 they must hand-wire the child inline (emit the child body in the same flat sequence, reach it by `jmp child_α`, take its γ/ω back by label) rather than `call child_fn`.

- [ ] **BROK-0 — dead-caller excision (free; no behavior).** Replace the `bb_build_brokered`/`bb_build_pure_mode` calls in `stmt_exec.c` (`:274,296,320,338`) — all inside already-`abort()`ing PATND/`exec_stmt_blob` paths — with the abort that already guards them (delete the now-unreachable `bb_box_fn bfn = …` lines). Delete the `BB_MODE_*` branch ladder (`:278,308`) and the `g_bb_mode` global (`rt.c:201`, `stmt_exec.c:63`) + `bb_build_pure_mode` (`emit_bb.c:~2230`, decl `emit_bb.h:14`) if no live caller remains. Gate: build rc=0; SNOBOL m2 7/7 HARD / m3 5/6 / m4 0/6, Icon m2 11/11 HARD — byte-neutral (dead code only).
- [ ] **BROK-1 — convert CAPTURE (`bb_capture.cpp`) to jump-to-α/β.** The captured sub-pattern is reached by emitting its element inline and wiring `jmp child_α` (fresh) / `jmp child_β` (resume on backtrack), taking the child's γ (matched → run the capture-assign, then this box's γ) and ω (this box's ω) by LABEL — NO `movabs child_fn; call rax; cmp eax,99`. The saved-Δ slot + `rt_cap_assign_cursor`/`rt_cap_assign_*` assign stays (that is real capture work, not a box entry). Both ASSIGN_COND (`.`) and ASSIGN_IMM (`$`) arms. Stackless `[ζ=r12+off]`, no value stack. Gate: the capture corpus (cross / W07_capt_cur / 074) holds under `--run`; m2/m3 smoke invariant.
- [ ] **BROK-2 — convert ARBNO (`bb_arbno.cpp`) to jump-to-α/β.** ARBNO is a generator loop: α matches the null string (SPITBOL ch.18 — ARB/ARBNO start empty); each retry re-enters the child by `jmp child_α` and threads the child's γ back to ARBNO's γ, child's ω to ARBNO's ω/exhaustion — all by LABEL, no brokered call. Keep the `std::deque<int>` per-activation slot pattern (real per-iteration state, NOT a value stack). Gate: ARBNO corpus under `--run` holds; m2/m3 smoke invariant.
- [ ] **BROK-3 — delete the brokered machinery + add the gate.** Now that NO caller passes `(ζ,entry)`: delete `bb_build_brokered` (`emit_bb.c`, `emit_bb.h`), `EMIT_BINARY_BROKERED` (`emit_core.h:18`, the `emit_core.c:30` case + the `:2201/2206` mode toggles inside the deleted fn), `g_bb_brokered` (`emit_core.c:18`) and the dead `BB_BROKERED`/`BB_WIRED` macros (`emit_core.h:55-56`), and the brokered `push rbp;mov rbp,rsp` prologue. Drop the `int entry` param from the `bb_box_fn` typedef + `bb_node_t` if no surviving signature needs it (else note exactly what does and why). **ADD COMPLETION GATE** `scripts/test_gate_no_brokered.sh`: `grep -rn 'bb_build_brokered\|EMIT_BINARY_BROKERED\|g_bb_brokered\|BB_MODE_BROKERED\|BB_MODE_DRIVER' src/ == 0` AND `grep -rnE 'esi, *1.*call|movabs.*child_fn.*call' src/emitter/BB_templates/ == 0` (no box entered by call-with-selector) — wire it into the Session Setup gate list so it can never creep back. Gate: build rc=0; SNOBOL m2 7/7 HARD / m3 5/6 / m4 0/6, Icon m2 11/11 HARD / m3 11/11 / m4 9/11; prove_lower2 64/64; concurrency OK; the FACT-RULE completion test (a) still 0 AND the new no-brokered gate green.

**COMPLETION TEST (rung):** `bb_build_brokered`/`EMIT_BINARY_BROKERED`/`g_bb_brokered`/`BB_MODE_BROKERED`/`BB_MODE_DRIVER` all grep to 0 in `src/`; no `bb_*.cpp` template enters a child box by `call` with an entry selector (every box reached by `jmp α`/`jmp β`); `test_gate_no_brokered.sh` green and in the Session Setup list; SNOBOL/Icon HARD gates survive. ONE way to enter a box, not two.

### ⭐ DESIGN QUESTION (Lon 2026-05-31, raised mid-SBL-M3-CHAIN): how do the PATTERN-builder BBs represent the pattern? — ✅ **DECIDED (Lon 2026-05-31): BOTH** — ⚠️ **SUPERSEDED 2026-06-01 (see CORRECTED PATTERN ARCHITECTURE at top): the pattern is a `bb_box_fn` byrd-box graph, NOT a baked `tree_t`. `tree_t` is for EVAL/CODE only. The `beauty.sno` / `tree(t,v,n,c)` memorial below stands as the AST shape for EVAL/CODE, not for patterns. History kept below.**

**✅ DECISION (Lon 2026-05-31): WE HAVE BOTH. This is the MAX OPTIMIZATION.** The two mechanisms are not
rivals — they compose:
- **The baked path (for INVARIANT patterns — and MOST patterns are invariant).** The pattern's AST is
  **compiled in / hard-coded as a pure static `tree_t` constant** (the `tree(t,v,n,c)` node — see below).
  **ONE BB** takes that baked-in `tree_t` and **builds the entire invariant pattern's dynamic BB graph from
  it in a single shot** (one tree-walk-construct). One box, one baked constant, the whole matcher graph
  materialized. This is the maximum optimization: an invariant pattern costs ONE baked AST + ONE builder BB,
  not N threaded builders.
- **The threaded path (for VARIANT parts).** Variable args (`LEN(N)`), pattern-valued var refs, and deferred
  `*E` stay as threaded builder BBs (the general PB-2 mechanism). They splice into / compose with the baked
  invariant subgraphs.
- **Classification (PB-OPT)** at lower time decides, per subtree, baked-invariant vs threaded-variant.

**Why this stays HONEST (the AST-prohibition is preserved, not broken).** The baked `tree_t` is consumed by a
**CONSTRUCTION BB** that *builds a pattern graph* from it — it is **never interpreted as the matcher**. The
matcher (PB-3 `BB_MATCH`, SPITBOL ch.18) still runs the *pattern graph*, never `tree_t`. So "one BB from a
baked AST" is real box work (construct), not the dead-mode-1 cheat (interpret `tree_t` as a stand-in for
execution). The prohibition's true line — *modes must never interpret `tree_t` in place of doing their job* —
holds: here the AST is the INPUT to honest construction work, exactly as it is for `EVAL`/`CODE`.

**🏛 MEMORIALIZED FOREVER: `beauty.sno` and `tree(t,v,n,c)`.** The baked AST node is `tree(t, v, n, c)` —
**t** = tag/kind, **v** = value (sval/ival/dval union), **n** = arity (child count), **c** = children array —
byte-for-byte the C `struct tree_t { tree_e t; union {char* sval; long long ival; double dval;} v; int n;
tree_t **c; }` (`src/include/ast.h`). That four-field tree representation comes from Lon's own
`corpus/programs/snobol4/demo/beauty/beauty.sno` (the SNOBOL4 Beautifier, 2002–2005; `tree.inc` /
`ShiftReduce.inc` / `TDump.inc`). `tree(t,v,n,c)` is the canonical shape of the compiled-in constant the
one-BB-from-AST builder consumes. *This will SCREAM.*

---

**The question (as originally posed).** The pattern-builder BBs (PB-2: "builder BBs that build OTHER BBs dynamically") must end up with the pattern's structure. Two ways Lon posed:
1. **BAKE the parser AST** — the parser-built tree (the exact `tree_t`) is baked into generated code as an RO constant; the builder references it.
2. **THREAD builder BBs** — a sequence of BBs assembles that same tree at runtime, each BB constructing one node.

**Context (Lon).** AST was historically FORBIDDEN because modes 2 & 3 would *cheat* — run the `tree_t` interpreter instead of doing their real job (the C oracle / native BBs). The dead **mode-1** WAS that `tree_t` interpreter (it lost its usefulness → removed; we'd otherwise have 4 modes). BUT **AST will legitimately be used in the backend for `EVAL` and `CODE`** (both inherently runtime-compile a string of SNOBOL source), "so why not PATTERN" — patterns are runtime-dynamic too.

**Claude's recommendation (now SUPERSEDED by the DECISION above — kept for the record).** Option 2 (threaded) canonical + Option 1 (bake) as PB-OPT, building a pattern-specific graph, never `tree_t`. Lon's crystallization sharpened the baked side: the baked artifact is the pure-constant `tree_t` AST, and ONE BB reconstitutes the whole invariant pattern graph from it — which is cleaner than baking a pattern graph (a graph has runtime pointers/allocation; an AST is a pure constant). Reasoning that still holds:
- **(a) Dynamic patterns force threaded construction anyway.** `LEN(N)` / `SPAN(C)` with variable args, `P1 | P2` over pattern-VALUED variables, and deferred `*E` (recursive patterns `P = *P 'x' | ''`) can't be baked. Threaded is the *general* mechanism; the baked one-BB-from-AST is the *invariant-subtree* fast path.
- **(b) The baked AST is consumed by CONSTRUCTION, never interpreted as the matcher** — so the mode-1 cheat does not return.
- **(c) The matcher interprets a pattern graph, never `tree_t`** — domain-specific, legitimate (SPITBOL itself interprets a pattern node graph).

**AST-prohibition refinement (ADOPTED with the DECISION).** *AST is permitted in the BACKEND for inherently-dynamic constructs — `EVAL`, `CODE`, and PATTERN construction (the one-BB-from-baked-AST builder + the threaded variant builders) — because there building/compiling from a tree IS the actual job. The absolute invariant: modes 2/3/4 must never interpret `tree_t` as a stand-in for STATIC code that already has a defined oracle (mode 2) or native-BB (modes 3/4) path. The matcher interprets a pattern-specific graph, never `tree_t`.*

- **SBL-SPAN-2 / SBL-ARBNO-3 BINARY arms.** Use `std::deque<int>` slot pattern from bb_capture.cpp (NOT GC_MALLOC). SPAN: TWO persistent int slots (z, z_orig); β yields successively shorter spans using ABSOLUTE z_orig. ARBNO: uses `nd->counter`, deque pattern + brokered child call. Validate via `--run`.
- **SBL-BREAKX-2 ✅ DONE** (2026-05-29 Opus 4.8). Own BINARY arm. TEXT β rescans-to-next using z_orig + z. z lives in [zeta+8]; z_orig recovered arithmetically (Δ - z) so no second slot needed. 302-byte α-scan + β-rescan, assembled+verified via `as`. Native +2 (W05_breakx, word4); zero regression.
- **SBL-ATP** (`@var` cursor capture). ✅ FULLY DONE (mode-2 oracle `877f61fe` + native template `745c7536`, 2026-05-30). Native +3: cross/W07_capt_cur/074. Key: `rt_pat_capture(kind=2)` builds `pat_cat(EPS, pat_at_cursor(var))` so XEPS must join XATP in `patnd_is_simple_atom` for the enclosing XCAT to be tree_eligible. ✅ COMPLETE (lifts cross/W07_capt_cur/074 native): (4) `build_patnd` XATP("@")→`BB_PAT_ATP`; `bb_pat_atp.cpp` TEXT+BINARY arms (model on `bb_pat_pos.cpp`; BINARY writes Δ→var int — add `rt_at_cursor` near rt.c:873); `emit_core` dispatch + `walk_bb_flat case`. Byte-producing → own session. (Interim: `BB_PAT_ATP` hits `walk_bb_flat default:` = honest `jmp ω` fail, RULES-OK.)
- **SBL-SM-BINARY (HQ-track).** `sm_pat_nullary.cpp` BINARY arm embeds emitter-process `rt_pat_*` fn-ptr as imm64 — Invariant-8 violation. Fix: call `rt_pat_*@PLT` directly.
- **SBL-G-2.** Re-freeze GATE-PK in `test_per_kind_diff.sh`. Baseline references deleted `rt_bb_*` boxes — stale.
- **SBL-LOWER-CLEANUP.** Delete `lower_subj_pat_split` + `lower.c:1750` duplicate after Snocone confirmed unused.
- **SBL-VERIFY-1/2.** Corpus climb after all BINARY arms + SBL-ATP: target ≥260/280 broad corpus.
- **Pre-existing m2 oracle gaps** (audit-only). Rungs 044/045/046/048/052/054/055/056/057 fail m2 too: `bb_exec.c` doesn't implement what rung suite expects for POS/RPOS/TAB/REM/star_deref/fail_builtin. Separate session.

### M3-NATIVE-5 (final)

Gate sweep + corpus, all langs. Honest failure for unbuilt opcodes.

**Mode-4 sibling (separate goal):** SBL-M4-FLATWIRE — `--compile` standalone brokers at runtime instead of flat-wiring at emit time. Defer until after M3-NATIVE done.

---

## Completed (summary)

**Templates with x86 TEXT arms filled:** LIT, ARB, LEN, POS/RPOS, TAB/RTAB, REM, ALT, CAT, FENCE, ABORT, EPS, FAIL, ANY, NOTANY, BREAK (plain), SPAN, ARBNO, CAPTURE, DEFER.

**Templates with x86 BINARY arms filled and validated by `--run`:** LIT, LEN, POS, UPTO, ANY, NOTANY, BREAK (plain), CAPTURE. Combinator arms (ALT/CAT/FENCE/PL_SEQ/PL_ITE/SUCCEED) emit real bytes via inline EP-walk (per-template, FACT-clean).

**Runtime translators:** `patnd_to_bb_graph()` (γ-chain, mode-2) + `patnd_to_bb_tree()` (tree-shape, mode-3 flat-wire). `patnd_needs_xlate` covers XARBN trees + simple-atom roots + capture-wrapped. `patnd_is_combinator_root` + `patnd_tree_eligible` route XCAT/XOR/XFNCE/XNME/XFNME/XARBN through tree builder.

**Infra:** `cap_alloc_saved_delta_slot()` deque-int pattern. `bomb_text`/`bomb_bytes`/`rt_bomb`. `audit_m3_native_binary_arms.sh`. `emit_label_alloc()` session-stable label arena. `_assign_varname_str` populates STRVAL_fn at construction time (NAMEPTR reverse-lookup via `NV_name_from_ptr`).

**Recovery resource:** original hand-written boxes at `git show 660339cd~1:src/runtime/boxes/<box>/<file>.s`. Native-SM engine semantic spec at `git show 22a17fa3~1:src/processor/sm_jit_interp.c` (bytes through templates only).

---

## Session State

Live HEAD is in the **Watermark** below; per-session detail (HEAD-by-HEAD writeups, gate logs, design
deliberations) lives in the `.github/HANDOFF-*.md` files. Only durable carry-forward is kept here.

**Done (structural, no logic change):** LOWER-MERGE LM-1…LM-5 (`9326db2`) — the four lowering files folded into
one `src/lower/lower.c` + `lower.h`, section order driver → Icon (the model) → Prolog → SNOBOL4 pattern → context.
PND-1 (KILL PATND_t lower bridge) — SNOBOL4 patterns lower `TT_*`→`IR_t` directly (like Icon/Prolog); the
`PATND_t` *type* removal from `pattern.c`/`rt.c`/`descr.h`/`patnd.h` is the separate Track-B runtime demolition.

**Open (ONE AST → ONE IR → ONE LOWER, Icon `lower_expr_threaded` the canonical four-port model):**
- [ ] **LM-6 (DISPATCH-UNIFY)** — collapse lower.c's three dispatch entry points (`lower_expr_threaded` [Icon] /
  `lower_pl_goal` [Prolog] / `build_node` [SNOBOL4 pat]) into ONE `tree_e`-keyed dispatch. Do AFTER all lower2
  roles are armed + exec-proven.
- [ ] **BOX-ZERO** — cut byrd boxes against the register-allocation scheme (Icon STACKLESS ONE-REGISTER FRAME,
  `[reg+off]` per-sequence frame distinct from r10/r13; RO constants IP-relative; no value stack).
---

### ⚠ PRE-SMX-4 corpus state (historical — engine deleted, numbers not reachable today)

```
HEAD SCRIP       = 1f011f10  SBL-ARBNO-BROKERED: ARBNO combinator roots via patnd_to_bb_tree in BROKERED (--interp +2: Qize, XDump)
GATE-1 smoke       = 13/13 (mode-2 AND mode-3)
GATE-2 broker      = 61/5
DEFAULT/NATIVE     = 265/280
true --interp      = 263/280
Rung suite         = M2=19/19 SKIP=0  (M4=18/19, 053 pre-existing)
```

## Session log (last few, terse)

- **2026-06-01 (Opus 4.8) — PB-RB-4 TOPOLOGY PREREQ** (SCRIP `e39c329`, pushed). `prove_lower2.c` MATCH('a' 'b')
  + MATCH('a'|'b') proofs (4 real nodes each, composite element γ+ω → MATCH). Finding: `lower2_match_entry`'s
  `lower2(cx,e,m,m,…)` under ROLE_PATTERN already handles TT_CAT/TT_ALT, so PB-RB-4's lowering layer exists; the
  new work is emitter STITCH wiring + drive. Test-only, byte-neutral; prove_lower2 65→67; all gates invariant.
- **2026-06-01 (Opus 4.8) — PB-RB-3 EDGE PROBES** (SCRIP `706d665`, pushed). Hardened the landed BB_MATCH BINARY
  arm: `probe_pb_rb_3_match_fail.c` exercises the two ch.18 step-6 edges the happy-path probe missed —
  whole-match-fail (`'z'`∉`'abc'` → start-loop exhausts → v=99) and anchored-fail (`&ANCHOR=1` suppresses the
  start-cursor slide → v=99), with an unanchored control (v=1) proving the anchor flag is the sole cause. Found two
  apparent bugs that are correct: `kw_anchor` is genuinely 8 bytes in the live `.so` (the `int` line is
  STMT_EXEC_STANDALONE-only) so `cmp qword` is right; `result.v==99` is the canonical FAIL code (xa_flat_epilogue
  fail_half), not garbage. Test-only, byte-neutral. Probe suite 3/3; all gates invariant.
- **2026-05-31 (Opus 4.8) — SBL-M3-CHAIN: SNOBOL4 MODE-3 RUNS FROM LOWER'S FOUR-PORT GRAPH (the `sno_ring_to_tree` replacement) ✅ mode-3 0/6 → 5/6**
  (SCRIP `7c26eb7`, base `641e45d`; .github this commit). The banned `sno_ring_to_tree` adapter stays deleted; mode-3
  now consumes LOWER's four-port statement-BB graph DIRECTLY via a new SNOBOL4 flat-chain emitter. **5 cases pass
  natively via `--run`: output `'hello'`, concat `'ab' 'cd'`→`abcd`, arith `2+3`→`5`, pattern `S 'b'='X'`→`aXc`, goto_s
  `:S(HIT)`→`hit`** (all confirmed vs SPITBOL oracle `/home/claude/x64/bin/sbl -b`). mode-2 **7/7 HARD held**; only
  `define` (user functions, IR_CALL+frame) remains for mode-3. **New (emit_bb.c, all SNOBOL-specific, byte-neutral to
  Icon — confirmed Icon m2 6/6 + m3 6/6 + m4 6/6 via `git stash` rebuild):** `sno_flat_chain_build(IR_graph_t*)` (BINARY)
  + `_text` (mode-4 future) mirror `icn_flat_chain_build` but (1) RESOLVE the `IR_SUCCEED` LANDING nodes transitively
  (`sno_chain_resolve` — a port to a landing follows through to its target; terminal `IR_SUCCEED` γ==NULL → success
  epilogue, `IR_FAIL` → failure epilogue), so the per-statement landing threading is transparent; (2) do NOT set
  `g_icn_flat_chain` (so `walk_bb_flat` takes the SNOBOL arms), instead set new `g_sno_flat_chain` (makes a standalone
  `IR_VAR` a by-name PASS-THROUGH — its value is read by-name in `bb_sno_assign_var`, so it must NOT push the excised
  value stack / `rt_nv_get` → `[SMX]` abort). Operand-ref pass `sno_chain_operand_refs(IR_graph_t*)` runs PER STATEMENT
  (`sno_stmt_operand_refs` over each statement-head = landing-resolved γ-target of entry + every landing) so statements
  reachable only via a failure/ω edge or a goto still get their consumer's `α` set (the `goto_s`/skipped-statement
  bug). `sno_chain_arity`: SNOBOL concat `IR_SEQ`(dval==1.0) = arity-0 LEAF (operands in sub-graphs) → `ASSIGN.α`=SEQ;
  `IR_SCAN` = arity-1 (consumes its γ-predecessor: subject for plain form / replacement for repl form) → `SCAN.α` set;
  else delegates to `icn_chain_arity` (covers the postfix LIT_I/LIT_I/BINOP/ASSIGN arith chain). Driver `scrip.c`:
  the mode-3 SNOBOL4 ABORT replaced with `sno_flat_chain_build(sbbg)` run under `g_frame_active=1` via `fn(rt_frame(),0)`;
  unbuilt shapes → SOFT honest fall (loud `[SBB]` stderr, clean exit, NO abort), so working shapes run while `define`
  just yields empty output. `bb_var.cpp` gained a `g_sno_flat_chain` pass-through arm (10-byte `jmp γ; β: jmp ω`).
  **NOTE — patterns run via the EXISTING IR_SCAN interpreter bridge** (`rt_sno_exec_scan`→`bb_exec_once` over the
  `IR_SCAN.counter` pattern sub-graph, mode-2's 19-arm engine, process-valid pointer baked imm64): this is the pragmatic
  static-pattern path, **NOT** the native PB-2/PB-3 builder-BB/`BB_MATCH` ladder (still future; see DESIGN QUESTION above).
  **Gates:** make scrip rc=0, make libscrip_rt rc=0, SNOBOL4 smoke m2 **7/7 HARD** + m3 **5/6** (floor MODE3_MIN raised
  0→5), prove_lower2 **55 PASS**, sm_dead 1 (≤1), Icon m2 **6/6 HARD** (byte-neutral). **PRE-EXISTING (NOT this session,
  proven via `git stash` at clean `8a01bb3`):** `audit_concurrency_invariants.sh` flags template-purity 7 > baseline 6
  (bb_assign/bb_binop/bb_call/bb_every/bb_field/bb_list_bang/bb_swap) — none touched here; my 4 files add ZERO purity
  side-effects. **NEXT:** (define) SNOBOL4 user functions in mode-3 (IR_CALL + call frame); then the real PB-0..PB-3
  native pattern ladder per the DESIGN QUESTION decision; mode-4 SNOBOL4 still 0/6 (driver `--compile` re-stitch is PB-5).

- **2026-05-31 (Opus 4.8) — SBL-M4-STACKLESS-1: SNOBOL4 MODE 4 LANDS (literal-assign) + modes-3/4 MISS diagnosed ✅**
  (SCRIP `80e6c22`, base `aa307b7`, rebased over `17096f3` RK-LOWER; .github this commit). Mode 4 **0/6 → 1/6**: `OUTPUT='hello'` emits a complete
  `.intel_syntax` program via real `scrip --compile --target=x86`, assembles (`as`), links (`gcc -no-pie -lscrip_rt
  --allow-shlib-undefined`), runs → `hello`. SAME box + SAME IR graph as mode 3 — proof that **modes 3 and 4 are two
  template arms (BINARY=m3, TEXT=m4) of ONE box, driven from ONE LOWER graph.** **The miss (now a top-of-file banner):**
  prior sessions treated m3/m4 as *driver* problems (the `sno_ring_to_tree` adapter; the `[SMX]` "not rebuilt" abort).
  In fact the mode-4 EMITTER was fully intact (`codegen_flat_build` + 15 XA templates) — only the driver *call* was
  severed. **Landed:** (1) EMITTER `bb_sno_assign.cpp` TEXT/GAS arm (rodata + `lea[rip+.L]` + `call …@PLT`, four-port,
  no value stack); (2) EMITTER `xa_flat.cpp` shared TEXT prologue+epilogue now honor `g_frame_active` (push/pop r12,
  no Σ/[r10] deref) — ROOT CAUSE of the 1st segfault was the `@PLT` store clobbering caller-saved r10 then the
  vestigial Icon epilogue deref'ing [r10]; byte-neutral to Icon; (3) DRIVER `scrip.c` mode_compile_x86 re-stitched
  (header → call-glue → main-close → codegen_flat_build → `.note.GNU-stack` LAST — the note had stranded the body in a
  discarded section, 2nd bug); (4) smoke link line += `--allow-shlib-undefined` (4 unreachable SMX-residue undefs in
  the .so). **Gates GREEN+INVARIANT:** scrip rc=0, libscrip_rt rc=0, m2 **7/7** HARD, m3 1/6, m4 **0→1**, prove_lower2
  **49/49**, sm_dead 1(≤1), concurrency OK, purity FACT 6 (baseline; new TEXT-arm byte-producers sit in the
  MEDIUM_BINARY-exempt path), Icon m2 **6/6** HARD + m3 5/6 (byte-neutral). **MODE3_MIN/MODE4_MIN can both go to 1.**
  **NEXT = pure LOWER+EMITTER:** lower `S 'b'='X'` (the `pattern` smoke) into the `test_sno_1.c` four-port statement-BB
  chain (subject-BB → LIT-match-BB → splice-BB), BINARY+TEXT arms each; both native modes pass from the one graph;
  then retire `sno_ring_to_tree`.

- **2026-05-31 (Opus 4.8) — SBL-M3-STACKLESS-1: SNOBOL4 mode-3 LANDS (literal-assign), STACKLESS ✅** (SCRIP `79e62f7`,
  base `7d3a15b`; .github this commit). First SNOBOL4 native mode-3 since SMX-4. **NO value stack** (Lon directive:
  "do NOT create a value stack. Forbidden!!!"). `OUTPUT = 'hello'` now runs via `--run`: m3 **0→1**. The other
  five smoke shapes SOFT-fail honestly (loud `[SBB]` stderr, clean exit, NO abort — the old `[SMX] FATAL` is gone for
  SNOBOL4; Prolog `--run` keeps its by-design abort). **What landed:** (1) `bb_sno_assign.cpp` — stackless box for
  `IR_ASSIGN` of a literal-string rhs: name+str baked as RO immediates, passed in `rdi`/`rsi` to `rt_sno_assign_lit_s`;
  42-byte BINARY arm (`movabs rdi,name; movabs rsi,str; movabs rax,&fn; call; jmp γ; β:jmp ω`); TEXT arm bombs
  (mode-4 excised). Touches NO `g_vstack`/`rt_push_*`/`rt_pop_*`. (2) `rt.c` `rt_sno_assign_lit_s(name,str)` — stackless
  store via `NV_SET_fn` (OUTPUT→write-line, core.c:2397). (3) `emit_core.c` + `walk_bb_flat`: `IR_ASSIGN` branches
  SNO(`α==IR_LIT_S`)→`bb_sno_assign` vs Icon(`α==IR_VAR`)→`bb_assign` — Icon untouched/byte-neutral. (4) `scrip.c`
  `sno_ring_to_tree` (skip landing IR_SUCCEED, postfix-fold; recognizes ONLY `landing→LIT_S→ASSIGN→PSUCC` today,
  returns NULL else) + `mode_run` SNOBOL4 wiring → `bb_build_flat`, soft-fail on NULL. **Gates GREEN+INVARIANT:**
  scrip rc=0, libscrip_rt rc=0, m2 **7/7** HARD, m3 0→1, m4 0/6 (excised), Icon m2 **6/6** HARD (byte-neutral),
  prove_lower2 **38/38**, sm_dead 1(≤1), concurrency OK, purity **6** (baseline; the box's FATAL-guard `fprintf` sits
  inside the `MEDIUM_BINARY` exempt range so it is NOT counted). Local commits; NOT pushed (no handoff trigger).
  **MODE3_MIN can now be raised to 1.**

  **⭐ STATEMENT-BB MODEL (Lon directive 2026-05-31 — the shape for the pattern/goto/full-statement work; evidenced in
  the uploaded `test_sno_1.c`/`test_sno_2.c`/`test_sno_3.c`, which build the EXACT four-port goto-threaded form):**
  Treat **each SNOBOL4 statement like an Icon expression** — a four-port (α/β/γ/ω) BB. The order, per `test_sno_1.c`
  (`POS(0) ARBNO('Bird'|'Blue'|LEN(1)) $ OUTPUT RPOS(0)` over `Σ`/`Δ`/`Ω`):
  1. **Statement BB starts BEFORE the subject.** The outer BB's α enters first; the subject expression is evaluated
     inside it (`seq_α: seq = str(Σ+Δ,0)` then into the pattern chain). Σ=subject base (R13), Δ=cursor (R14),
     Ω=length (R15) — matches the X86-64 REGISTER FACT table exactly.
  2. **Subject gets ONE SHOT — no β-backtrack, but CAN fail.** The subject is evaluated once; if it fails, the
     statement fails to ω. It does NOT participate in pattern backtracking (no resume edge back into the subject).
  3. **BUILD PATTERN = a BB.** The pattern is constructed as its own four-port BB (each primitive POS0/BIRD/BLUE/
     LEN1/alt/ARBNO/RPOS0 is a BB with _α/_β/_γ/_ω; alternation threads `alt_i`; ARBNO carries `ζ`-frame `_1[64]`
     with per-instance slots — the `[r12+off]` one-register frame, NOT a stack). Built at runtime, OR
  4. **statically compiled** as an OPTIONAL optimization (the "2nd pass, optimization" block in `test_icon.c`/the
     test_sno programs — the pattern flattened to straight-line code when shapes are known at compile time).
  5. **Run the MATCH** from the built (or compiled) pattern BB against the subject; on γ, do the `$`/`.` captures +
     `= REPLACEMENT` splice; thread the statement's γ/ω to the SPITBOL `:S`/`:F`/`:(L)` goto exits (ch.4/ch.14).
  This is why `pattern` (`S 'b' = 'X'`, an `IR_SCAN`) and `goto_s` need: an `IR_SCAN` flat driver that emits the
  statement-BB (subject one-shot eval → build/emit the pattern BB → run match → splice) + `IR_GOTO`/landing
  threading — all stackless (`ζ`-frame `[r12+off]` + RO `[rip+disp]`), NEVER a value stack. The 19-arm pattern
  engine becomes per-primitive stackless BBs (model leaves on `test_sno_1.c`'s POS0/LEN1/alt/ARBNO bodies).

  **NEXT (next full-budget session, stackless byte-producing):** (1) widen `sno_ring_to_tree` / add an `IR_ASSIGN`
  arm for non-literal rhs (var, arith) — needs the operand sub-expr to deliver its value stacklessly (per-box
  `ζ`-slot, not vstack); (2) `IR_SCAN` statement-BB driver per the model above (the `pattern` smoke); (3) `IR_GOTO`
  + landing threading (the `goto_s` smoke); (4) SNOBOL4 user-proc call (the `define` smoke). Each: emit stackless,
  prove, gate (m2 7/7 HARD invariant; raise MODE3_MIN as they land). Recovery model = `test_sno_1.c` four-port bodies.

- **2026-05-31 (Opus 4.8) — MODE-3 SNOBOL4 ROUTING: SUBSTRATE DIAGNOSIS (superseded by SBL-M3-STACKLESS-1 above).**
  Lon: "Mode 3. Continue." Investigated routing SNOBOL4's `mode_run` onto `bb_build_flat` (the stated #1 next step,
  "Icon proves it works"). **Finding: the mode-3 native substrate is mid-GROUND-ZERO-3 migration and internally
  inconsistent — routing SNOBOL4 onto it now would route onto abort-stubs / a half-converted value-passing
  convention.** NOTHING committed (the real work is byte-producing → reserved for a dedicated session per the
  TEMPLATE-ONLY ONE-DISPATCH rule); recording the exact blocking facts so the next session doesn't re-spend a
  session rediscovering them.
  **Blocking facts (all grounded in source this session):**
  1. **Store/write/call runtime family is STUBBED.** `rt.c` `STACKLESS_ABORT` set: `rt_pop_nv_set`, `rt_pop_write_int_nl`,
     `rt_pop_write_any_nl`, `rt_pop_store_i64`/`_descr`, `rt_push_stored_i64`, `rt_call_proc`, `rt_call_builtin`,
     `rt_gen_concat`, all `rt_unop_*`, `rt_field_get`/`_set`, `rt_idx_get`/`_set`, `rt_list_bang`, `rt_limit_begin`,
     `rt_toby_real`, `rt_case_eq` — each aborts ("Icon value stack removed (GROUND ZERO 3); rebuild stackless").
  2. **Icon m3 5/6 passes ONLY via the `write(...)` call path** (write_str/int/string_op/every/arith) which uses the
     still-LIVE `vstack_push/pop` + `rt_nv_get` + `rt_nv_set` + `rt_arith` + `rt_push_int`/`rt_push_str`. None store
     to a variable, so none hit a stub. The lone m3 FAIL (`if_expr`) + the whole assign-store family are where the
     stubs bite. SNOBOL4 has no `write(...)` — it uses `OUTPUT = expr`, i.e. the stubbed/assign path.
  3. **Half-converted value-passing convention.** `bb_lit_scalar` IR_LIT_I (GZ-2) AND IR_LIT_S (R-HW-2) are now pure
     four-port PASS-THROUGHS (RO constants the *consumer* box seals `[rip+disp]`, NOT pushed) — yet `bb_binop`'s
     arith arm still POPS the vstack via `rt_arith`. So lits don't deliver a value the way `rt_arith`/`rt_nv_set`
     expect. The convention (value-stack vs stackless ζ-frame) is in flux and MUST be settled before any box lands.
  4. **SNOBOL4 IR node shapes ≠ Icon flat-template shapes.** `IR_ASSIGN` (SNO): `α=β=NULL`, value on the AG γ-ring
     (postfix), target name in `sval`; `OUTPUT`/`TERMINAL`/keyword writes route through `NV_SET_fn` (core.c:2384 —
     `OUTPUT`→`output_val` writes a line; the LIVE `rt_nv_set` calls `NV_SET_fn`, CONFIRMED reachable). But Icon's
     `flat_drive_assign` + `bb_assign.cpp` require `α=IR_VAR` and call the STUBBED `rt_pop_nv_set` → would abort.
     `IR_SCAN` + `IR_GOTO` have NO `walk_bb_flat` case (→ `default: jmp ω`). SNOBOL4 concat (`IR_SEQ`, `dval=1.0`)
     keeps operands in ISOLATED `IR_graph_t` sub-graphs (not the flat ring), and `flat_drive_seq` reads `pBB->α`
     (NULL for SNO) → emits empty-seq no-op. `icn_ring_to_tree` returns NULL on the SNO graph (entry is a landing
     IR_SUCCEED), so the Icon mirror falls back to `bbg->entry` (a landing) → walk emits jmp-γ → empty output.
  **The fork (Lon's architectural call — coupled to GROUND ZERO #1's shared register/ABI FACT RULE, x3 lockstep):**
  - **A — target the LIVE value stack now** (`rt_nv_set`/`rt_push_int`/`rt_arith`/`vstack_*`). Fast green on the simple
    expression-assign family, but builds ONTO the value stack GROUND ZERO 3 is removing → those boxes are knowingly
    throwaway (need stackless rebuild later). NOT lockstep (SNOBOL4-own box; no Icon re-prove).
  - **B — build SNOBOL4 boxes STACKLESS from the start** (per-box ζ-frame `[r12+off]`, no `g_vstack`; matches RULES
    ICON STACKLESS ONE-REGISTER FRAME + the goal's BOX-ZERO directive). Correct end-state, no rework — but means
    writing the stackless store primitive that `rt_pop_nv_set` is a stub FOR = a slice of the GROUND ZERO 3 rebuild,
    LOCKSTEP-shared with Icon (ABI change → all three GOAL files in one commit + re-prove all three).
  Lean = **B** (BOX-ZERO + the stackless rule are central; A's output is disposable). A is a legitimate stopgap only
  if a same-day mode-3 number is wanted (flag boxes for rebuild).
  **ORDERED PLAN (next session, byte-producing — pick A or B convention first):**
  (1) `sno_ring_to_tree` adapter (in scrip.c, NON-byte-producing, reused by BOTH A and B): skip leading landing
      IR_SUCCEED, collect the single statement's γ-chain to PSUCC/PFAIL/next-landing, postfix-fold by SNO arities
      (LIT*/VAR=0, BINOP=2, ASSIGN=1 with value→child + name kept in sval), return root or NULL (soft-fail) on
      multi-statement / IR_SCAN / IR_GOTO / isolated-subgraph-concat shapes.
  (2) SNOBOL4-OWN assign box `bb_sno_assign.cpp` (TEXT+BINARY) on the chosen convention — A: call LIVE `rt_nv_set`
      (32-byte movabs-name/movabs-fn/call/jmp-γ/β:jmp-ω, model bb_assign but `rt_nv_set` not `rt_pop_nv_set`);
      B: stackless ζ-frame store. + emit_core dispatch case + walk_bb_flat SNO-assign arm (lang-guarded) + Makefile
      RT_PIC_SRCS line.
  (3) Make IR_LIT_I/S deliver a value in the flat path under the chosen convention (A: restore the `rt_push_int`/
      `rt_push_str` push for the SNO path; B: seal RO + consumer reads `[rip+disp]`).
  (4) Wire scrip.c `mode_run` `!is_icon && !is_prolog` arm → `sno_ring_to_tree` + `bb_build_flat`, replacing the
      `[SMX] FATAL` abort, with a SOFT honest fallback (loud stderr "shape not yet flat-emittable", clean exit, NO
      abort) when the adapter returns NULL. Target: `output`/`arith` first (MODE3 0→2); `concat` needs isolated-
      subgraph flattening; `pattern`(IR_SCAN)/`goto_s`(IR_GOTO)/`define`(user-proc) are the LONG POLE (separate boxes).
  (5) Gate: m2 7/7 HARD (byte-neutral — SNO mode_run arm only), raise MODE3_MIN as cases land, prove_lower2 38/38,
      sm_dead ≤1, concurrency OK, purity (new template's byte-producers are MEDIUM_BINARY-exempt). Build: scrip rc=0,
      libscrip_rt rc=0. NO regression. Gates verified GREEN + INVARIANT at session start on `7d3a15b`.

- **2026-05-31 (Opus 4.8) — SBL-EXEC-4: SNOBOL4 KEYWORD-ASSIGN + COMPUTED/INDIRECT GOTO ✅** (SCRIP this handoff,
  base `81d721b`; .github this handoff). Two SNOBOL4 stmt-level features landed on the four-port IR; mode-2 stays 7/7.
  **(A) KEYWORD-ASSIGN `&NAME = expr`** (SPITBOL Manual ch.16 "Unprotected Keywords"). `v_assign` (lower.c) rejected
  any non-`TT_VAR` lhs → `&ANCHOR = 1` hit `lower_unhandled` (kind 47). Fix: accept a `TT_KEYWORD` lhs **only when
  `cx.lang==IR_LANG_SNO`** (FACT RULE: variation inside the one TT_ASSIGN case, Icon `:=` untouched). The lexer
  already strips the `&` (snobol4.l:154 `yytext+1`), so `as->sval` = bare keyword name; the runtime write path
  ALREADY EXISTED — `NV_SET_fn` (core.c:2403+) maps `ANCHOR/TRIM/FULLSCAN/MAXLNGTH/STLIMIT/CODE/ERRLIMIT/FTRACE/
  TRACE` → the `kw_*` globals and rejects protected `&CASE` (Error 10, SCRIP is case-sensitive). Same four-port
  topology as a var-assign (verified: anchored matching flips `"abc" ? 'b'` S→F; keywords round-trip; `&CASE`
  rejected). **(B) COMPUTED/INDIRECT GOTO `:($X)` / `:S($X)` / `:F($X)`** (SPITBOL ch.4). Used the free `IR_GOTO`
  enum slot (no exec arm, never constructed). **Parser fact:** `:($IDENT)` does NOT parse to an expr node — it
  folds to a `TT_QLIT` label STRING with a leading `$` (snobol4.y goto_label_expr:120); the rarer `:($(expr))`
  form (line 121) carries a real expr. So `goto_node_str` returns `"$L"`, NOT caught by `goto_node_expr`. New in
  lower_program.c: a run-time label registry (`g_bb_labels[]` + `bb_label_landing()`, populated after PASS-1 with
  every labeled stmt's landing), `make_computed_goto` (lowers the goto expr into an isolated value sub-graph on
  `IR_GOTO.counter`, like IR_SCAN/IR_CALL operands), and `make_indirect_goto` (the `$`-prefix string form →
  synthesize `TT_VAR(suffix)` → resolver). Wired into the U/S/F branch resolution. `IR_GOTO` exec arm (bb_exec.c):
  run the sub-graph, `VARVAL_fn` → label string, `bb_label_landing` → landing node, return it (unresolved/fail →
  `bb->ω` = the lowerer's fall-through). **CAUGHT A REAL BUG:** `bb_reset` (scrip_ir.c:201) zeroed `counter` for
  every kind except ARBNO/SCAN/SNO-SEQ/SNO-CALL → the resolver's sub-graph pointer was wiped on re-entry; added
  `IR_GOTO` to the preserve-list. All three branches verified (U/S/F → reached/hit/failure-routed). +1 prove case
  (`&ANCHOR = 1`, via new `dump_sno_value` since `IR_LANG_SNO=1`≠the shared lang-0 dump) + `kw()` builder.
  **Gates GREEN + INVARIANT:** scrip rc=0, libscrip_rt rc=0, prove_lower2 **38/38** (37+1), snobol4 m2 **7/7**
  (HARD), icon m2 **6/6** (HARD, byte-neutral — SNO-only guards), sm_dead 1(≤1), concurrency OK, purity FACT 6
  (no template touched). **MODE-3/4 ASSESSMENT (empirical, Lon-requested):** SNOBOL4 m2 7/7 (BB exec via
  `bb_exec_once`); **m3 = `[SMX] FATAL` abort** — mode-3 `--run` is gated `if (is_icon)` in scrip.c:478, Icon
  flows through `bb_build_flat`→`bb_box_fn` native (PROVEN: `hello from icon mode-3`, exit 0, icon m3 5/6), SNOBOL4/
  Prolog fall to the SMX abort (the native run-path EXISTS + works for Icon — SNOBOL4 just isn't routed onto it =
  the long pole); **m4 = blanket `[SMX]` abort** (scrip.c:396, returns before ANY emission for ALL langs incl.
  Icon — BB-native x86 emission excised by SMX-4, not rebuilt). **NEXT (high→low):** route SNOBOL4 onto the mode-3
  `bb_build_flat` path (highest value — Icon proves it works); rebuild mode-4 BB-native x86 emission; then
  `IR_PAT_DEFER` runtime (Track B), broader builtins (ARRAY/TABLE/APPLY), `&ANCHOR` already done.

- **2026-05-31 (Opus 4.8) — TESTING DIRECTIVE: ALL THREE MODES, ALWAYS ✅** (.github + SCRIP this handoff). Per Lon:
  every SCRIP test for this GOAL now runs modes 2/3/4. `scripts/test_smoke_snobol4.sh` rewritten — mode 2
  (`--interp`) is the HARD gate; mode 3 (`--run` / SB-LINEAR) + mode 4 (`--compile --target=x86` → `as` → `gcc
  -no-pie … -lscrip_rt` → run) are RUN + REPORTED on EVERY invocation (tracked, `MODE3_MIN`/`MODE4_MIN` PASS
  floors, default 0). Current: **m2 7/7, m3 5/6, m4 1/6** @ 18357d4 (the `--run` native path and the SMX-4-excised
  `--compile` x86 emission are not yet rebuilt — now VISIBLE every run). Gate exits 0 (mode-2 clean + floors
  met). The Mode-defs block gained a ⛔ TESTING DIRECTIVE and the gate-suite block was updated to match. Raise
  the floors as 3/4 come back so regressions in them fail the gate too.

- **2026-05-31 (Opus 4.8) — SBL-EXEC-3: SNOBOL4 PROGRAM-DEFINED FUNCTIONS + COMPARISON PREDICATES + RECURSION ✅**
  (SCRIP `cb5946a`, rebased onto `eccb4f6` PLG-3; .github this handoff). Mode-2 smoke **6/7 → 7/7** (`define` was the last fail).
  **(A) CALL LOWERING** — `lower.c` VALUE-role `TT_FNC`, `cx.lang==IR_LANG_SNO` arm → `IR_CALL` (sval=name,
  ival=nargs, `dval=2.0` SNO marker; each arg lowered into its OWN isolated `lower_value_subgraph`, the array
  riding on `counter`). The Icon arm (callee child c[0]) is untouched — the SHAPE split keys on `cx.lang`.
  `scrip_ir.c` `bb_reset` now also preserves `counter` for `IR_CALL(dval==2.0)`. **(B) FUNCTION REGISTRATION** —
  `lower_program.c`: scan `DEFINE('NAME(p..)l..')`, parse the prototype, and register a proc whose graph is a
  **VIEW** over the one landing-node graph `g` (`*fg=*g; fg->entry = land[label NAME]` — shared node set, own AG
  ring, distinct entry; no body extraction). `lower_sc` carries the saved-name list (params, then locals, then
  NAME); `nparams=#params`. Shared `RET`/`FRET` `IR_RETURN` nodes created up front; bare-subject and `:(L)`-goto
  `RETURN`/`FRETURN`/`NRETURN` wire to them (NRETURN→RET placeholder). **(C) CALL EXEC** — `bb_exec.c` `IR_CALL`
  `dval==2.0`: evaluate the arg sub-graphs (a failing arg fails the call); a proc-table user function runs through
  the **SNOBOL4 global save/restore frame** (save the globals named in `lower_sc`, bind dummy args to actuals,
  null locals+result var, push an EMPTY-scope `GenFrame` so the body's vars route through the global name table,
  snapshot/reset/`bb_exec_once(fg)`, capture `g_ir_return_val` on `FRAME.returning`, restore globals LIFO); any
  other name falls to `try_call_builtin_by_name`. **AG-ring save/restore around the nested call** (the ring is
  graph-level state `bb_snapshot/restore_state` don't cover, and recursion re-enters the SAME view graph) — this
  is what makes `N * FACT(N-1)` survive the recursive descent. `IR_RETURN` now branches on `dval`: `1.0`=value is
  the function-named global (RETURN), `2.0`=failure (FRETURN), else generic α-return (Icon/Prolog). **(D)
  PREDICATES** — `gen_runtime.c try_call_builtin_by_name`: numeric `EQ/NE/LT/LE/GT/GE` + lexical
  `LGT/LLT/LGE/LLE/LEQ/LNE` comparison FUNCTIONS (null string on success, FAIL otherwise) beside the existing
  relational OPERATORS; these were newly reachable (TT_FNC used to hit `lower_unhandled`) and are needed by the
  recursion base case. **Verified:** `DOUBLE(21)`→42, `FACT(5)`→120, `T(0)/T(5)`→1/99, top-level `EQ(0,0)`→equal.
  **Gates GREEN:** scrip rc=0, libscrip_rt rc=0, prove_lower2 37/37, sm_dead 1(≤1), purity FACT 6 (byte-neutral —
  no template touched), concurrency OK, Icon m2 6/6 (HARD), Prolog m2 3/5 (eccb4f6 PLG-3 lifted +1). All SNOBOL4-gated edits are
  byte-neutral for Icon/Prolog by construction (lang/dval guards). **NEXT:** `&ANCHOR`/keyword-assign, computed/
  indirect goto `:($X)`, true NRETURN (return-by-name) + DEFINE 2nd-arg entry-label, the `IR_BINOP` multi-node
  AG-ring fragility (`(10+20)+(3+4)`→11; same sub-graph fix as IR_SEQ), `IR_PAT_DEFER` runtime (Track B), broader
  SNOBOL4 builtin coverage (ARRAY/TABLE/APPLY/…).

- **2026-05-31 Opus 4.8 — SBL-EXEC-2: SNOBOL4 CONCAT + GOTO ✅** (SCRIP `687aa58`, base `f4f4d9a`; .github this
  handoff). Mode-2 smoke **4/7 → 6/7** (only `define` left). **(A) CONCAT** — Lon's steer: `TT_SEQ` → `IR_SEQ`,
  not a BINOP fold. `v_conj` branches `cx.lang==IR_LANG_SNO` → left-assoc binary `IR_SEQ` chain; each node lowers
  its 2 operands into ISOLATED `IR_graph_t` sub-graphs (`lower_value_subgraph`, γ=NULL terminal value-node) and
  the `bb_exec.c IR_SEQ` arm (marker `dval==1.0`) runs each via `bb_exec_once` + `binop_apply(BINOP_CONCAT)`.
  Robust for multi-node operands (`(2+3) ' ' (4+5)`→`5 9`; `(10+20) ' x ' (3+4)`→`30 x 7`; vars→foobar/foo-bar).
  `bb_reset` preserves `counter` for SNO-concat `IR_SEQ`. Value-role `TT_ALT`→`v_alt`→`IR_ALT` added too.
  **FINDING: `IR_BINOP` has the SAME AG-ring multi-node fragility** (`(10+20)+(3+4)`→11, not 37) — apply the
  sub-graph fix there later. **(C) GOTO** — `lower_program.c` SNOBOL4 walker rewritten: two-pass LANDING-NODE
  scheme (every stmt gets an `IR_SUCCEED` landing; label→landing map; `:S`/`:F`/`:(L)` resolve fwd+bwd with
  SPITBOL ch.4 precedence; subject-less bare-goto/END transfer via landing; entry=`land[0]`). Verified S/F/
  unconditional/backward-loop/combined. **Concurrency-audit false-positive FIXED** (`g_term`/`g_builtin` Prolog
  helpers between `lower_pattern`/`lower_goal` were misattributed to block#2 → bogus `TT_QLIT`/`TT_VAR` dup): the
  LOWER(a) awk now scopes counting to the 3 role dispatchers (`in_role`); still catches a real injected dup.
  **Gates GREEN:** scrip rc=0, libscrip_rt rc=0, prove_lower2 35/0, sm_dead OK, purity 6 (byte-neutral),
  concurrency OK, Icon m2 5/6 (HARD, byte-neutral via stash). **NEXT:** DEFINE/`TT_FNC` user functions (the last
  smoke fail — call frame + param binding + RETURN; `INVOKE_fn`/`IR_CALL` are refs), `&ANCHOR=N` keyword-assign,
  computed goto, `IR_PAT_DEFER` runtime (Track B).

- **2026-05-31 Opus 4.8 — REGISTER CONVENTION LOCKED IN CODE + SNOBOL4 PATTERN LEAVES ✅** (this handoff). Lon: cover
  the register base before the 3-session race, "SET the registers up front in the code before we JUMP into BB land."
  **Findings:** (1) the x86 BB-native emission backend is EXCISED by SMX-4 (`--compile` says "BB-native x86 emission not
  yet rebuilt"; `--run` silent; `bb_program` was an unwired empty stub) — so emitted bytes are assemble-verifiable only,
  not run-provable; rebuilding it IS the race. (2) THREE contradictory register conventions existed: GOAL FACT RULE
  (r12=ζ, r13/r14/r15=Σ/δ/Δ) vs REGISTER-LAYOUT.md (r12=SM value-stack TOS, r13-15 free) vs RULES.md ICON-STACKLESS
  ("r13=SM-state register") — all SMX-4 residue (SM engine gone → no value-stack, no SM-state). **Lon ratified the GOAL
  FACT RULE as winner.** **Done:** created `src/emitter/bb_regs.h` — THE single register source the 3 sessions reference
  (BBREG_* GAS names + BBREGN_* reg numbers); filled `bb_program.cpp` with the register-setup prologue (mov r12,rsp;
  lea r10,[rip+Δ_root_data]; jmp root α) — assemble-verified via `as` (`49 89 e4`/`4c 8d 15…`); synced REGISTER-LAYOUT.md
  to the live convention (supersession banner + table). **Lon register decisions captured:** rbx=DESCR base pointer
  (dual-width 8/16-byte DESCR; concurrent 32-bit session in flight), rbp=variable hash-table base (RESERVED — GET/SET
  stay C calls for now, inlining is a future optimization). ζ (r12) = ONE load per BB-BLOB sequence BEGIN, amortized
  across the sequence's boxes, survives C calls (callee-saved); R10 = caller-saved re-loadable constant data (flat) — the
  RO-const-vs-RW-dynamic axis is why ζ is callee-saved and r10 caller-saved. **SNOBOL4 PATTERN leaves added to lower.c
  `lower_pattern`:** LEN/POS/RPOS/TAB/RTAB/FENCE/ABORT/FAIL/SUCCEED/ARBNO + captures (COND/IMMED/CURSOR) + DEFER(*var) +
  bare VAR; `kind_is_resumable` extended with the pattern generators. Flag/payload encodings match the bb_exec.c oracle
  arms. **Gates green throughout:** make scrip rc=0, make libscrip_rt rc=0, prove_lower2.sh 17/17, purity FACT 6, sm_dead
  1, concurrency invariants OK. **OPEN:** (a) the pattern leaves are NOT YET PROVEN (no prove_lower2.c cases — next step);
  (b) R10 flat-data-ptr vs brokered-current-node fork is the one unresolved byte-affecting decision; (c) the 3 GOAL-file
  register FACT tables (byte-identical x3) now LAG bb_regs.h — a lockstep amendment is deferred until R10 settles + the
  dual-width session's rbx work lands (co-owned). Per Lon: do not tangle on the HASH inline optimization now.

- **2026-05-31 Opus 4.8 — CONCURRENCY GROUND RULES for 3-session LOWER+EMITTER fill ✅** (SCRIP `d1c082f`,
  .github `0b3e3bea`). Lon greenlit firing up 3 concurrent sessions (SNOBOL4/Icon/Prolog) to fill LOWER + EMITTER
  to 100% BBs on x86 by EOD, all platforms next; asked to verify the herding discipline first ("LOWER turning into
  a mess and code flying outside EMITTERS"). **Audit:** LOWER already herded (SHARED-LOWERER FACT RULE, verified
  byte-identical x3 — the earlier sed mismatch was a false alarm, the phrase recurs in this file's watermark). **Gap:
  EMITTER had NO concurrency rule** — `emit_core.c` is one giant shared `switch` (108 cases), 67 per-box template
  `.cpp`s, one shared Makefile `RT_PIC_SRCS`; RULES.md TEMPLATE-ONLY governed only WHERE bytes live. **Installed:**
  (1) `TEMPLATE-ONLY EMISSION — ONE-DISPATCH CONCURRENCY` FACT RULE, byte-identical x3 (md5 307534d6), mirroring the
  LOWER rule. (2) `scripts/audit_concurrency_invariants.sh` — the herding gate enforcing both rules' completion tests
  (no dup `case TT_` per role switch, no dup `case IR_` in emit_core.c, no byte-emitter regression vs baseline 6,
  FACT RULE blocks byte-identical x3 via awk). (3) `prove_lower2.c` `main()` sectioned per-language (BEGIN/END markers)
  so concurrent appends auto-merge. (4) Fixed the LOWER rule's self-check (c) sed→awk (over-matched in SNOBOL4-BB),
  re-synced byte-identical x3 (md5 5097ed94). Gates green: audit_concurrency_invariants OK, prove_lower2.sh 17/17,
  make scrip rc=0. No code logic changed (rules + gate + harness sectioning only); Icon m2 stays 5/6.

- **2026-05-31 Opus 4.8 — ICON EXECUTES AGAIN (m2 0/6 → 5/6) ✅** (SCRIP `212ed70`, base `593fbf3`; .github this
  handoff). Continuation of the shared-combinator session (Lon: "Finish."). Made Icon run on the four-port IR via
  `bb_exec_once(main)`. (1) Promoted `g_det_builtin1` → SHARED role-agnostic `wire_det_builtin1`, called from BOTH
  the Icon VALUE role (write/writes) AND the Prolog GOAL role (write/writeln/print) — another sharing seam. Set
  `dval=1.0` (is_deep) so the IR_CALL exec arm reads the threaded arg from the AG ring (verified `bb_exec_once`
  pushes each node value between steps). (2) Added the VALUE-role `TT_FNC` write arm; the per-language TT_FNC SHAPE
  is handled inside the one case (FACT RULE: variation lives in the case) — Icon carries the callee as child
  c[0]=TT_VAR with args c[1..], Prolog carries it in sval. (3) `lower_icon_body` (lower_program.c): builds each
  registered Icon proc's four-port graph from the TT_PROC_DECL body (c[2]), reverse-threads its statements
  VALUE-role, fills proc_table bb_idx. FAIL-LOUD — any unhandled statement sinks the whole body (-1) so the driver
  keeps its clean `[IBB] FATAL` rather than silently running a partial graph (verified: `write("one"); x:=[1,2,3]`
  aborts with NO partial output, satisfying the concern that made me revert this in the prior handoff). (4)
  **`tt_to_binop` fix** — `v_binop` stored the raw `tree_e` in `ival`, but the IR_BINOP exec arm casts ival to
  `BinopKind` (TT_ADD=13 ≠ BINOP_ADD=0) → binop_apply computed the wrong op. Latent since the lower2 rewrite (only
  topology was ever proven); Icon arith is the first executor. Added a tree_e→BinopKind mapper; this also fixes
  SNOBOL4 value binops (`OUTPUT = 2 + 3`→5, was wrong). **Icon m2 now 5/6** (write_str/write_int/arith/string_op/
  if_expr); the lone fail `every write(1 to 3)` (outputs `1`) needs generator-through-call resumption (L2-E
  suspend/resume frame) — IMMEDIATE NEXT in the Watermark. Gates: make scrip rc=0, make libscrip_rt rc=0,
  prove_lower2.sh 17/17, sm_dead 1, FACT 6. corpus UNTOUCHED. bb_exec.c UNTOUCHED. FACT RULE block byte-identical
  across the 3 goal files preserved.

(Older entries pruned; see git history of GOAL-SNOBOL4-BB.md.)

---

## Architecture references

- Semantic oracle: `bb_exec.c case BB_PAT_*`
- Flat driver: `emit_bb.c codegen_flat_body`, `walk_bb_flat`, `walk_bb_node`
- Template dispatch: `src/emitter/emit_core.c`
- Template directory: `src/emitter/BB_templates/bb_pat_*.cpp`
- Lowering: `src/lower/lower_pat_dcg.c::build_node`
- Mode-2 interp dispatch: `src/runtime/sm_interp.c SM_EXEC_STMT`
- Mode-3 native runner: `src/processor/sm_native.c sm_run_native`
- PATND legacy: `src/runtime/snobol4/stmt_exec.c exec_stmt` DT_P branch
- Translator gate: `src/runtime/snobol4/stmt_exec.c patnd_needs_xlate`
- Pattern-building runtime helpers: `src/runtime/rt/rt.c rt_pat_*` (called @PLT from templates)
- Bomb infra: `src/emitter/emit_str.{cpp,h}` bomb_text/bomb_bytes; `src/runtime/rt/rt.c rt_bomb`
- Audit gate: `scripts/audit_m3_native_binary_arms.sh`

---

## ⭐ SESSION 2026-05-31 (Opus 4.8) — LOWER2 BOX LADDER: proof gate restored + L2-A/L2-B-core proven

**Directive (Lon):** continue lower2.c; read Proebsting + irgen.icn (+ found: GOAL-LOWER-REDESIGN.md §318 wiring
table — the authoritative cross-check); implement all TT_* kinds; rungs in small proven groups; read the
tree-pattern notes. **Read this session:** Proebsting §4.1–4.6+Figs1&2, `jcon_irgen.icn` ir_a_Every/Alt/
conjunction/Limitation/While/Until/Repeat/Not, `lower.c` lower_new_*_ag (exec-compat reference),
GOAL-LOWER-REDESIGN.md (the four-port node §204, canonical wiring table §318, "lower wires the DCG directly"
§759, final pipeline §788). **NOT yet read** (next session): GOAL-SM-LOWER-REFACTOR.md, GOAL-ICON-LOWER-REDESIGN.md.

**INFRA RESTORED (was local-only in the prior session — never committed; confirmed via `git log -S`):**
- 3 public role-entry shims added to lower2.c: `lower2_value_entry`/`_pattern_entry`/`_goal_entry` (the only
  external surface — `lower2()` stays static; each seeds the cursor with a role and funnels in).
- `prove_lower2.c` rewritten: proves Fig-1 `5 > ((1 to 2)*(3 to 4))` (=9 real IR nodes) AND nested
  `(1 to 2) to (3 to 4)` (=7; `to-child.fail → from-child`), each with a PASS/FAIL node-count assertion + a
  full α/β/γ/ω port dump. Builders lit/bin/un/tri; kname covers all wired kinds.
- `scripts/prove_lower2.sh` — committed reproducible gate (compiles lower2.c+scrip_ir.c+prove_lower2.c
  standalone; the production lower.c is NOT linked, via local kind_is_resumable+cset_try_fold). **9/9 PASS.**

**Method.** Each box transcribes the canonical port equations (Proebsting §4 + `ir_a_*` + the §318 table) into
lower2's idiom (lcx_t cursor + `lower2()` recursion + nalloc/set_succ_fail/ret), in PURE four-port form (α/β
synthesized out, γ/ω inherited in) matching the foundation. lower.c's lower_new_*_ag are the exec-compat
reference. Value-plumbing (which node reads which operand `.value`) is DEFERRED to LOWER2-EXEC (IR_t lacks the
`c[]` child array the design §204 imagined; operands collapsed onto α/β — verify against the executor, do not
assume). The proof checks TOPOLOGY only.

**TREE-PATTERN NOTES (read, acknowledged):** `tmatch_proto.c` `tm`/`tm_g` is a STEP-5 *refactor* of already-proven
box code into uniform MATCH-shape + CAPTURE-children + RECURSE + WIRE. MEASURED shallow (120 peeks, 12 two-level,
0 three-level; 78 uniform recursion calls); ~30% LOC shrink; win = uniformity. "Refactor proven code into pattern
form — don't design two things at once." Correctly deferred until all role arms are implemented + proven. Endgame:
(a) parse=LALR tokens→tree is SYMMETRIC to tmatch tree→IR; (b) IR_PAT_DEFER = runtime analog of a compile-time
capture; (c) the pattern-form C transliterates to the Icon-bootstrap lowerer.

### Rung ladder (VALUE role unless noted) — proven box-by-box via scripts/prove_lower2.sh

- [x] **L2-A — combinators**: conjunction `TT_SEQ`/`TT_SEQ_EXPR` (= binop w/o compute; `ir_conjunction` —
  `c0.γ→c1.α`, `c0.ω→ω`, `c1.γ→conj`, `c1.ω→c0.β`, resume=c1.β), alternation `TT_ALTERNATE` (2nd runtime-gated
  box; `ir_a_Alt` — `arm.γ→alt`, fail-chain `arm[i].ω→arm[i+1].α`, last→ω, resume=alt, arm resumes in operand_aux).
- [x] **L2-B-core — loops**: `TT_EVERY` (`ir_a_Every`: E1.γ→body.α, body.γ=body.ω=E1.β, E1.ω→every.fail; no-body
  E1.γ→E1.β drain), `TT_WHILE` (`ir_a_While`: cond bounded, body.γ=body.ω=cond.α, E1.ω→while.fail), `TT_UNTIL`
  (`ir_a_Until`: E1.γ→until.fail, E1.ω→body/loop via UNTIL-node trampoline), `TT_REPEAT` (`ir_a_Repeat`:
  E.γ=E.ω→REPEAT-node trampoline→E.α), `TT_NOT` (`ir_a_Not`: E.γ→not.fail, E.ω→not⇒null,succeed). Bodies bounded.
  **Fixed** a latent NULL-ω in until/repeat (generator children stranded) by threading the loop node as the
  concrete restart trampoline (matches every/while). All ports concrete; 9/9 PASS.
- [ ] **L2-B2 — loop escapes + non-Icon loops**: `TT_LOOP_BREAK`/`TT_LOOP_NEXT` (`ir_a_Break`/`ir_a_Next` via a
  loop-context in lcx_t: break→loop.fail, next→loop nextlabel), `TT_DO_WHILE`, `TT_FOR`, `TT_FOR_RANGE`, `TT_UNLESS`.
- [ ] **L2-C — limitation / interrogation**: `TT_LIMIT` (`ir_a_Limitation` — counter box: lim.α=N.α, N.γ→E.α,
  E.γ→lim.γ, E.ω→N.β, resume decrements counter), `TT_INTERROGATE`, `TT_NONNULL` (verify v_unop route),
  `TT_IDENTICAL`/`TT_INDIRECT`.
- [ ] **L2-D — assignment**: `TT_ASSIGN`, `TT_SWAP`, `TT_AUGOP` (`ir_augmented_assignment`), `TT_REVASSIGN`, `TT_REVSWAP`.
- [ ] **L2-E — calls & access**: `TT_FNC` (`ir_a_Call` — suspend/resume frame), `TT_METHCALL`, `TT_FIELD`
  (`ir_a_Field`), `TT_IDX`, `TT_SECTION`/`_PLUS`/`_MINUS` (`ir_a_Sectionop`), `TT_INITIAL` (`ir_a_Initial`).
- [ ] **L2-F — scan / match**: `TT_SCAN` (`ir_a_Scan`), `TT_SMATCH` (`subj ? pat` → flips cx.role=ROLE_PATTERN).
- [ ] **L2-G — returns / decls / goto / case**: `TT_RETURN`/`TT_NRETURN` (`ir_a_Return`), `TT_SUSPEND`
  (`ir_a_Suspend`), `TT_PROC_FAIL` (`ir_a_Fail`), `TT_CASE` (`ir_a_Case`), `TT_GLOBAL`/`TT_LOCAL`/`TT_STATIC_DECL`/
  `TT_DECL`/`TT_OPSYN`, `TT_GOTO_U`/`TT_GOTO_S`/`TT_GOTO_F`, `TT_TRY`/`TT_DIE`.
- [ ] **L2-H — data / cset / IO**: `TT_MAKELIST`/`TT_VLIST`/`TT_RECORD`/`TT_NEW`/`TT_SORT`, `TT_MAP`/`TT_GREP`/
  `TT_GATHER`, `TT_HASH_*`/`TT_ARR_*`, `TT_CSET_UNION`/`_DIFF`/`_INTER`, `TT_PRINT`/`TT_PRINT_FH`/`TT_SAY`/`TT_SAY_FH`.
- [x] **L2-P — PATTERN role** (lowering COMPLETE 2026-05-31; exec arms deferred to LOWER2-EXEC): **`TT_LEN`/`POS`/`RPOS`/`TAB`/`RTAB` ✅**, **`TT_FENCE` ✅**, **`TT_ABORT`/`TT_FAIL`/`TT_SUCCEED` ✅**,
  **`TT_ARBNO` ✅**, **CAT chain (`TT_SEQ`/`TT_CAT`) ✅**, **ALT (`TT_ALT`) ✅**, **captures `TT_CAPT_COND_ASGN`/`_IMMED_ASGN`/`_CURSOR` ✅**,
  **`TT_DEFER`(*var) + bare `TT_VAR` ✅**, **`TT_BAL` ✅** (2026-05-31 — IR_PAT_BAL generator, proven). **`TT_FNC` pattern-primitive folds: N/A ✅** — INVESTIGATED 2026-05-31 (Sonnet 4.6): the SNOBOL4 parser NEVER delivers SPAN/ANY/LEN/etc. as a generic `TT_FNC`. In `snobol4.y` the `T_FUNCTION` production calls `pat_prim_kind(name)`, and `tal_fnc_close` builds `ast_node_new(k==TT_VAR ? TT_FNC : k)` — so a recognized primitive name (ANY/NOTANY/SPAN/BREAK/BREAKX/LEN/POS/RPOS/TAB/RTAB/ARB/ARBNO/REM/FAIL/SUCCEED/FENCE/ABORT/BAL) is constructed DIRECTLY as its dedicated `TT_*` kind (all already handled in `lower_pattern`); only a non-primitive name becomes `TT_FNC`. A `TT_FNC` reaching `lower_pattern` is therefore a user function returning a pattern value used in pattern position — runtime-resolved (DEFER territory), NOT a compile-time primitive fold — and correctly falls to `lower_unhandled` (loud). **L2-P lowering is COMPLETE; no fold arm needed.**
  (foundation leaves LIT/ARB/REM/SPAN/ANY/NOTANY/BREAK/BREAKX already in lower_pattern via pat_cset_arg.)
  CAT/ALT done 2026-05-31 via SHARED `wire_seq`/`wire_alt`. **Leaves added 2026-05-31 (this handoff):** LEN→IR_PAT_LEN,
  POS/RPOS→IR_PAT_POS (RPOS sval="r"/dval=1.0; bounded, β=ω_in), TAB/RTAB→IR_PAT_TAB (generator, self-β), FENCE→IR_PAT_FENCE
  (bounded; FENCE(inner) lowers inner then FENCE-successor), ABORT→IR_PAT_ABORT, FAIL→IR_FAIL, SUCCEED→IR_SUCCEED,
  ARBNO→IR_PAT_ARBNO (inner pattern in own IR_alloc sub-graph + bb_arbno_state_t), CAPT_COND/IMMED→IR_PAT_ASSIGN_COND/_IMM
  (inner.γ→capture, varname in sval), CAPT_CURSOR→IR_PAT_ATP, DEFER→IR_PAT_DEFER(ival=1), bare VAR→IR_PAT_DEFER(ival=0).
  `kind_is_resumable` extended with the pattern generators (β=self) so emit_leaf wires self-retry for generators and β=ω_in
  for POS/RPOS/FENCE/ABORT. Flag/payload encodings match the bb_exec.c oracle arms exactly. **NOT YET PROVEN — no prove_lower2.c
  cases for these arms yet (the 17/17 covers only the pre-existing arms). NEXT: add SNOBOL4 dump_pat cases (node counts + α/β/γ/ω).**
- [~] **L2-Goal — GOAL role**: **`TT_UNIFY` (+`=/2`) ✅**, **arith-compares (`< > =< >= =:= =\=`) ✅**, `TT_IF`, `TT_VAR`/`TT_FNC`
  call/builtin, **conj `,` ✅ / disj `;` ✅** /ITE (cut/true/fail leaves already in lower_goal).
  conj/disj done 2026-05-31 via SHARED `wire_seq`/`wire_alt` (IR_GCONJ/IR_DISJ); unify=`g_unify` (IR_UNIFY),
  compares=`g_compare` (IR_ARITH, ival=BinopKind). Remaining: ITE (`->`/`*->`), `is/2`, user-pred Call, `nl`,
  term-comparison (`==`/`@<`…), findall/catch. (Prolog EXEC stays resolve-runtime + sm_interp_run per RULES;
  these arms are topology-only, proven via prove_lower2.sh, feeding the eventual goal graph.)
- [~] **LOWER2-EXEC** — **SNOBOL4 pattern-match statements EXECUTE ✅ (2026-05-31 Opus 4.8, the long pole — first since SMX-4):**
  `v_scan` lowers `SUBJECT ? PATTERN` (+ `= REPLACEMENT`) to `IR_SCAN`; the `IR_SCAN` exec arm drives the pattern
  sub-graph through the 19-arm `IR_PAT_*` oracle with anchored start-iteration + deferred-capture flush + replacement
  splice; `bb_reset` preserves `IR_SCAN.counter`; walker does match-replace synthesis + default fall-through; bare
  ARB/REM/BAL/FAIL/SUCCEED/FENCE/ABORT recognized. 13/13 byte-identical to SPITBOL oracle. (See Watermark.) **STILL OPEN:**
  Icon value-level proof — wire `lower2_value_entry` → bb_exec on `1 to 5`; confirm/adjust the relational flag (`dval=1.0`)
  + if-gate (`node.β` runtime dispatch) + alt-gate (operand_aux) AGAINST the executor.
- [ ] **L2-TMATCH** — STEP 5: refactor the proven box code into `tm`/`tm_g` pattern form (match-capture-recurse-wire);
  retire `tmatch_proto.c`'s `#if 0` exhibit. Don't start until the arms above are proven.
- [ ] **LM-6 DISPATCH-UNIFY** — once all roles armed + exec-proven, retire lower.c's 3 dispatch entry points; lower2 IS the lowerer.

**Watermark.** SCRIP `c66bbc8` · .github this commit.
**This session (2026-06-02, Opus 4.8 cont.) — TEMPLATE-REVAMP: `bb_pat_fence` + `bb_pat_break` converted to x86() self-encoding (pBB-free); the LOOP-FREE pattern leaves are now ALL DONE:**
- **`bb_pat_fence`** — LOOP-FREE single-shot convert (the bare-FENCE primitive, no argument). Per the mode-2 oracle
  (bb_exec.c IR_PAT_FENCE) + SPITBOL Manual ch.18 ("matches the null string and succeeds when the scanner is moving
  left to right, but fails if the scanner has to back up through it"): α saves δ to a ζ-frame slot then `jmp γ` (null
  match, always succeeds forward); β restores δ from the slot then `jmp ω` (the fence effect — backtrack fails). One
  ζ-frame dword saved_δ @ `[r12+off]` via `bb_slot_claim(4)`, register-relative so BINARY==TEXT (no movabs, no
  rip-rel .data). Ratified cursor δ=R14d (REG-3). pBB-free end-to-end (fn/wrapper/prototype/dispatch all `void`).
  No internal labels needed (single-shot, like POS/TAB). Verified: a pattern hitting FENCE on the forward pass
  succeeds and matches null (`'a' FENCE 'b'` in `'abc'` → ok). NOTE: the two SPITBOL backtrack-blocking examples
  (`ANY('AB') FENCE '+'` in `'1AB+'` → fail; `FENCE 'B'` as first component → anchored-fail) fail in BOTH m2 AND m3
  (agreement) — a PRE-EXISTING mode-2 oracle gap in FENCE-through-ALT/ANY backtracking, NOT a regression from this
  conversion (the box agrees with the oracle exactly; the oracle itself doesn't propagate the fence into those
  ALT/capture-resume contexts — that is the same 124/114 DEFER-capture-resume blocker tracked elsewhere in this file).
- **`bb_pat_break`** — LOOPING convert (BREAK + BREAKX, both arms in one pass). BREAK(S) scans from δ to the first
  char in set S (NOT included), fails if the subject ends first; BREAKX(S) on backtrack "looks past" — steps past the
  break char and rescans to the NEXT char in S (SPITBOL Manual ch.3 word4.spt; INTEGERS ? BREAKX('E') . OUT 'ER' →
  INTEG). Grounded in the mode-2 oracle (bb_exec.c IR_PAT_BREAK: α scan-to-first; β plain = δ−=z+fail; β BREAKX =
  origin=δ−z, rescan from origin+z to next, fail if none/i<=z else δ=origin+z). The match-state scalars moved OFF the
  process-global `rt_cs_t` (`bb_cs_zeta` + `movabs &zeta`) INTO the ζ-frame: z @ `[r12+off]`, z_orig @ `[r12+off+4]`
  via `bb_slot_claim(8)`, register-relative so BINARY==TEXT (PER-BOX LOCAL STORAGE / NO-VALUE-STACK FACT RULES).
  Internal labels: plain BREAK loop=L(0)/done=L(1); BREAKX β-rescan adds loop2=L(2)/done2=L(3) — resolved by the
  bb_emit_x86 walker. strchr(cs,ch)≠NULL ⇒ char in set; r10 push/pop around the call (r13/r14/r15 callee-saved,
  survive). Ratified Σ=R13/δ=R14d/Δ=R15d (REG-2; was already register-migrated, this conversion drops the `bb_bin_t`
  hand-counted byte map + the process-global zeta scratch). pBB-free end-to-end. r10-as-cursor mirror was already
  gone (REG-2); the only r10 use left is the strchr push/pop guard. **Verified mode-3 == mode-2 == SPITBOL oracle**
  for plain BREAK (delimiter found, delimiter absent→fail, word-split), AND BREAKX look-past (INTEGERS→INTEG) — all
  4 cases byte-exact. The BREAKX β rescan loop + ζ z/z_orig + strchr-with-r10 all exercised together. TEXT arm
  structure hand-assembled via `as` (both plain + BREAKX β rescan) to confirm the internal-label + ζ-frame GAS is
  well-formed (SNOBOL4 mode-4 end-to-end still pends the LOWER four-port-statement-BB wiring, PB-RB-8 — not box-specific).
- **`b.size()` count: 121 → 118** (this conversion REMOVED bb_pat_break's 3 hand-counted-offset sites; the box now
  has ZERO `b.size()`, ZERO `bb_bin_t`, ZERO `TEMPLATE_ADDR`/`[r10]`-cursor/`movabs &zeta` in code — the 3 grep hits
  in the file are comment mentions of what was removed). Progress toward the FACT-RULE zero goal.
- **Gates ALL GREEN + INVARIANT:** make scrip rc=0, libscrip_rt rc=0, SNOBOL4 m2 **7/7 HARD** / m3 5/6 / m4 0/6,
  pat-rung-suite M2 **18/19** (same pre-existing `053_pat_alt_commit`), prove_lower2 **67/67**, concurrency invariants
  OK (FACT RULES byte-identical ×3 UNPERTURBED — `x86_asm.h` NOT touched this session, so it is byte-neutral to
  Icon/Prolog/Raku; Icon m2/m3/m4 all-PASS confirmed), `g_vstack` **0**, broad interp corpus held at 108/280 (the
  GATE-4 `inc/` corpus-snapshot gap noted in the prior watermark persists — orthogonal). Files touched: `bb_pat_fence.cpp`
  + `bb_pat_break.cpp` (boxes, both rewritten) + `bb_templates.h` (two prototypes → `void`) + `emit_core.c` (two
  dispatch calls → parameterless). No `x86_asm.h` edit — both boxes use the EXISTING encoders (the SPAN looping box
  already proved the internal-label + ζ-frame + strchr/r10 vocabulary; FENCE reuses the FR()/jmp/def forms).
- **NEXT (SNOBOL4):** the loop-free pattern leaves are now ALL converted. What remains is the VARIABLE-LENGTH
  combinators — `bb_pat_cat`, `bb_pat_alt`, `bb_match`, and the `FENCE(P)` with-children PAIR path — which share the
  STILL-OPEN define/jmp-pair design (variable-count define/jmp pairs from `g_emit.xa_bb_emit_pair_n`). Whoever reaches
  a combinator first designs that idiom once in `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`. (Or pivot to the REG-RO rung
  — RO addresses → `[rip+disp]` — to fully retire r10 and unblock SNOBOL m4, per the 🔴 CURRENT PRIORITY section.)

**Prior watermark.** SCRIP `fe94061` · .github this commit.
**This session (2026-06-02, Opus 4.8 cont.) — TEMPLATE-REVAMP: `bb_pat_arb` + `bb_pat_defer` converted to x86() self-encoding (pBB-free):**
- **`bb_pat_arb`** (`fe94061`) — generator convert. ζ-frame state z (matched len) @ `[r12+off]` + zo (origin δ) @
  `[r12+off+4]` via `bb_slot_claim(8)` (PER-BOX LOCAL STORAGE / NO-VALUE-STACK FACT RULES) — the old process-global
  `std::deque<int>` z/zo + `movabs &z`/`&zo`/`&Σlen` bakes are GONE. Ratified registers Σ=R13/δ=R14d/Δ=R15d.
  Two-entry generator, NO internal loop label (like POS): α sets z=0, zo=δ, → γ (offers the 0-char match first per
  SPITBOL ch.18 "shortest possible substring … behaves like a spring"); β does z++, eax=zo+z, `cmp eax,r15d`/`jg ω`,
  δ=zo+z, → γ (expands one char per retry). Driven correctly by the existing `add reg,[r12+off]` / `mov [r12+off],imm`
  encoders — no new x86_asm.h vocabulary needed.
- **`bb_pat_defer`** (`fe94061`) — runtime-resolved pattern-valued variable. Migrated off the legacy `[r10]` cursor to
  δ=R14d (REG-3); pBB-free (varname=`_.op_sval`, flag=`_.op_ival`). α: rdi=&varname (RO via `x86_load_ro` lea[rip]/
  movabs), esi=flag, edx=δ, call `rt_defer_match`; `test eax,eax`/`js ω` (return <0 = fail); δ=eax; → γ. β: → ω
  (single-attempt). The 16-byte-aligned call sequence is PRESERVED (sub-pattern path → exec_stmt → SSE stores need
  aligned rsp): `push r10; push rbx; mov rbx,rsp; and rsp,-16; call; mov rsp,rbx; pop rbx; pop r10` — the three raw
  qword-mov/and bytes (`48 89 e3` / `48 83 e4 f0` / `48 89 dc`) `as`+objdump-verified before writing. X86-only.
- **Verified:** m2 smoke **7/7 HARD** (unchanged), pat-rung-suite **M2 18/19** (same pre-existing 053_pat_alt_commit),
  **ARB+DEFER green in BOTH m2 AND m3-native** (`'O' ARB 'A'`→matched; `'O' ARB P` with P='NT'→matched both modes,
  exercising ARB spring-expansion + DEFER string-literal resolution + the aligned call). Concurrency invariants hold
  (FACT RULES byte-identical ×3 UNPERTURBED), `g_vstack` 0, purity baseline (my two files NOT in the side-effect list),
  net −54 lines. Files: `bb_pat_arb.cpp` + `bb_pat_defer.cpp` (boxes) + `bb_templates.h` + `emit_core.c` (parameterless
  decl/dispatch). Rebased clean over sibling Raku `RK-HY-1/2` (`bb_seq`/`bb_nfa` de-cram) — no conflict.
- **ENV NOTE for next session:** GATE-4 (`test_interp_broad_corpus_and_beauty.sh`) reports ~108/280 not the ~251
  Session-Setup figure, because the script's `INC=corpus/programs/snobol4/demo/inc` directory is ABSENT from the
  current corpus checkout (include-dependent tests fail in the harness though they pass run-directly — verified
  `097_keyword_alphabet` emits the exact ref). A corpus-snapshot/harness gap, NOT a regression and orthogonal to the
  conversion; restore that `inc/` dir (or repoint the script) to re-baseline GATE-4. Also: the clone token's last
  char before `5dK` is lowercase `h` (`…Sy0xh5dK`); an uppercase-`H` variant 401s — set the remote URL accordingly.
- **NEXT (SNOBOL4):** next loop-free leaf is `bb_pat_fence` (do the single-shot save-Δ-on-α / restore-on-β form
  first); then looping `bb_pat_break` (follow SPAN); then the STILL-OPEN variable-length define/jmp-pair combinators
  `bb_pat_cat`/`bb_pat_alt`/`bb_match` + FENCE's pair path (whoever reaches a combinator first designs that idiom once
  in `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`).

**This session (2026-06-02, Opus 4.8 cont.) — TEMPLATE-REVAMP: `bb_pat_abort` + `bb_pat_tab` + `bb_pat_atp` converted; `x86_movimm32` encoder added:**
- **`bb_pat_atp`** (`52daa2e`) — LOOP-FREE single-shot convert. @var cursor capture: α writes δ to var via
  `rt_at_cursor` then → γ; β fails → ω. Cursor δ read from R14d (REG-3; legacy `[r10]` cell GONE). Varname is RO
  via `x86_load_ro` (lea[rip] TEXT / movabs BINARY), call via `x86_call_ro`, double `push/pop r10` around the
  side-effecting call (NV_SET print-path clobbers caller-saved r10 + rsp 16-align). varname = `_.op_sval` (==
  driver `op_name1` for IR_PAT_ATP). X86-only (no other arm). pBB-free; prototype + dispatch parameterless.
  **mode-3 == mode-2** verified: `LEN(3)@P`→P=3, `@Q LEN(2)@R`→Q=0/R=2, `BREAK(' ')@W` in "hello world"→W=5.
- **Full session detail + NEXT STEPS:** `HANDOFF-2026-06-02-OPUS48-SNOBOL4-BB-TEMPLATE-REVAMP-V4-ABORT-TAB-ATP.md`
  (next loop-free-ish leaves `bb_pat_arb` [generator, re-pump like SPAN] + `bb_pat_defer`; then looping
  `bb_pat_break`; then the variable-length combinators `fence`/`cat`/`alt`/`match`). Parallel sessions landed
  `bb_cut` (Prolog `ed42331`) + `bb_binop_arith` (Icon `b8db625`) — rebased clean, no conflict, rebuilt+reverified.
- **`bb_pat_abort`** (`66eb967`) — TRIVIAL convert: x86 arm = `x86("jmp",PORT_OMEGA)+x86("def",PORT_BETA)+x86("jmp",PORT_OMEGA)`.
  pBB-free (reads `_` only); prototype + dispatch parameterless. Verified mode-3: a pattern hitting ABORT fails the
  match (SPITBOL Manual ch.18: ABORT causes pattern match failure).
- **`bb_pat_tab`** (`66eb967`) — LOOP-FREE convert on the ratified registers δ=R14d / Δ=R15d (legacy `[r10]`/`lea[rip+Σlen]`
  GONE). TAB(N): `cmp r14d,N / jg ω / mov32 r14d,N / jmp γ / def β / jmp ω`. RTAB(N): `mov ecx,r15d / sub ecx,N /
  cmp r14d,ecx / jg ω / mov r14d,ecx / jmp γ / def β / jmp ω`. RTAB distinguished by `sval[0]=='r'` (NOT `ival!=0`).
  Semantics matched to mode-2 oracle (`bb_exec.c` IR_PAT_TAB): target = N (TAB) | Σlen−N (RTAB), fail if δ>target,
  advance δ=target, β fails restoring δ. **mode-3 == mode-2** verified for TAB(2), TAB(0), RTAB(2), RTAB(0), and the
  cursor-past-target failure path (`LEN(3) TAB(1)` / `LEN(3) RTAB(4)` both correctly fail).
- **NEW ENCODER `x86_movimm32`** in `x86_asm.h` (+ `"mov32"` front-end mnemonic) — 32-bit `mov reg,imm32` (B8+rd,
  REX.B when reg≥8; 5/6 bytes; `mov r14d,N`=`41 BE imm32`). Byte-verified vs `as` BEFORE use. ADDITIVE — no existing
  encoder perturbed (the 64-bit `x86_movimm`/movabs path for operand-constant loads is untouched). The `mov` vs `mov32`
  mnemonic split is the R7-sanctioned way to pick the immediate width at the call site.
- Gates ALL GREEN: m2 **7/7 HARD**, m3 5/6 (`define` lone fail), PAT-BB rung 18/19 m2 (`053_pat_alt_commit` pre-existing),
  g_vstack **0**, prove_lower2 PASS, concurrency invariants OK (FACT RULES byte-identical ×3), Icon smoke 2/2 (shared
  `x86_asm.h` edit caused no Icon regression). Detail: this watermark (no separate HANDOFF file this turn).
- **NEXT loop-free leaves:** `bb_pat_atp` / `bb_pat_arb` / `bb_pat_defer` (read each for its exact shape; arb/atp touch
  variable storage). Then looping `bb_pat_break` (follow SPAN), then the variable-length combinators.

**Prior session (2026-06-02, Opus 4.8) — TEMPLATE-REVAMP: x86() internal-label keystone + `bb_pat_pos` + `bb_pat_span` converted; mode-4 verbiage corrected:**
- **x86() SELF-ENCODING REVAMP** (per GOAL-TEMPLATE-REVAMP-RULES-DRAFT): each BB becomes ONE return per PLATFORM_*,
  pure `x86(mnem,…)` concatenation, NO `bb_bin_t`, pBB-free (reads `_` only). In-band records replace the hand-counted
  offset table — `L`(literal bytes) / `J`(rel32 patch to a label) / `D`(define a label); the consumer `bb_emit_x86`
  DISCOVERS byte positions as it copies, so no offset can drift.
- **KEYSTONE `a1779e6`** (looping-box prerequisite for ALL FOUR sessions, purely additive → zero regression):
  (1) INTERNAL (box-local) LABELS — record ids ≥ `X86_INTERNAL_BASE`(4) map in the walker to a fresh box-local
  `bb_label_t`; forward+backward refs resolved by the EXISTING `bb_label_define`/`bb_emit_patch_rel32` patch list;
  TEXT names `.Lx<uid>_<n>`, uid set per-box by `x86_begin()`; front-end `x86("jmp"/jcc/"def", L(n))`. (2) ζ-FRAME
  `[r12+off]` MEM OPS (mov-imm/store/load/add-imm/add-to-reg) — register-relative so BINARY==TEXT bytes (PER-BOX
  LOCAL STORAGE / NO-VALUE-STACK FACT RULES; no `movabs` to a process addr, no rip-rel `.data`); front-end via
  `FR(off)`. (3) `cmp r32,imm` (imm8/imm32/eax). (4) `bb_slot_claim(bytes)` — node-free per-sequence frame claim so a
  pBB-free box takes private scratch without an `IR_t*` key. Every encoder byte-verified vs `as`.
- **`bb_pat_pos` `195bea4`** — POS/RPOS → x86() + ratified regs (REG-3); the LOOP-FREE register-migration reference.
  POS `cmp r14d,N`; RPOS `mov ecx,r15d / sub ecx,N / cmp r14d,ecx`; then `jne ω / jmp γ / def β / jmp ω`. Legacy
  `[r10]`/`&Σlen` GONE; cursor δ=R14d, length Δ=R15d read straight from the regs. RPOS distinguished by `sval[0]=='r'`
  (authoritative per lower_pat_dcg.c), NOT `ival!=0`. Verified mode-3: POS(0)'abc'=Xde, POS(2)'c'=abXde,
  'cde'RPOS(0)=abX, 'b'POS(0) correctly fails.
- **`bb_pat_span` `3769d21` (+ encoders `24b9c78`)** — FIRST LOOPING box on x86(); validates the keystone end-to-end
  and is the reference looping-box conversion for all sessions. Internal labels loop=`L(0)`/done=`L(1)`; the match-state
  scalars z (matched length) and zo (β-undo origin) moved from the process-global deque (`movabs` to a fixed addr) to
  ζ-frame z@`[r12+off]`/zo@`[r12+off+4]` via `bb_slot_claim(16)` → BINARY==TEXT, re-entrant; cset/strchr reuse the
  any-style RO load. New encoders (byte-verified vs `as`): `jle`(0F 8E), `add reg,reg`(01/r), `add reg,[r12+off]`(03/r).
  Verified mode-3: SPAN('a')/'aaabbb'=Xbbb, SPAN('ab')=X, SPAN('xyz')/'xyz123'=Q123, SPAN('a')/'bbb' fails, AND
  SPAN('a')'ab'/'aaab'=X (β GIVE-BACK — exercises the internal labels + ζ-scratch + β port together).
  ⚠ encoders for span were left unstaged in 3769d21 and added in 24b9c78 — the remote TIP 24b9c78 builds; 3769d21 alone does not.
- **MODE-4 VERBIAGE CORRECTED (Lon directive):** mode-4 is NOT "aborting by design" and is NOT inferior to mode-3 — the
  two are the SAME boxes in two media (BINARY run in-process vs TEXT relocatable), and for the ζ-frame/REG-ratified
  boxes the bytes are identical. SNOBOL4 mode-4 is pending ONE wiring step (LOWER emitting the four-port statement-BB
  graph directly; the emission scaffolding is intact, and Icon/Prolog mode-4 already emit). Corrected `scrip.c`'s
  comment + abort message, and the stale historical note that claimed BOTH modes abort by design (mode-3 never aborted
  after the `sno_flat_chain_build` re-wire). `eval_code.c`'s "by design" abort is a DIFFERENT, correct one (the removed
  global value stack) — left as-is.
- Files: `emit_globals.h` + `emit_bb.c` + `x86_asm.h` (keystone/encoders); `bb_pat_pos.cpp` + `bb_pat_span.cpp` +
  `bb_templates.h` + `emit_core.c` (boxes); `src/driver/scrip.c` (verbiage).
- Gates GREEN throughout: SNOBOL4 m2 **7/7 HARD** / m3 5/6 (floor 5) / m4 0/6 (floor 0 — a MEASURED state pending the
  LOWER wiring, **not** a design abort), PAT-BB probes 3/3, prove_lower2 PASS, `g_vstack`==0. **Reference examples are now
  ample:** POS (loop-free reg-migration) + SPAN (looping: internal labels + ζ-scratch + β give-back) + the five pBB-free
  exemplars (rem/len/any/notany/lit) cover every remaining box's shape.
- **NEXT (SNOBOL4 x86() conversion remainder), in order:** loop-free legacy→REG-ratified+x86(): `bb_pat_tab`
  (TAB `cmp r14d,N / jg ω / mov r14d,N` — needs a `mov r32,imm32` encoder, 41 BF imm32; RTAB via Δ=r15d
  `mov ecx,r15d/sub/cmp/jg/mov r14d,ecx`), `bb_pat_atp`, `bb_pat_arb`, `bb_pat_defer`, `bb_pat_abort` (TRIVIAL:
  `jmp ω / def β / jmp ω`). LOOPING: `bb_pat_break` (follow the SPAN pattern; plain BREAK ≈ SPAN, BREAKX two-loop needs
  L(0..3) and z/z_orig moved from `[zeta+8/+12]` to ζ-frame). VARIABLE-LENGTH (separate define/jmp-pair design, shared
  with Icon/Prolog `xa_bb_emit_pair_*`): `bb_pat_fence` (pair-array path), `bb_pat_cat`, `bb_pat_alt`, `bb_match`.
- **OTHER SESSIONS CLEARED TO START** (`.github` `97355e35`): updated the SHARED `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`
  so Icon/Prolog/Raku don't rebuild the keystone (it's in the shared `x86_asm.h` → would collide). Flipped its
  "OPEN DESIGN ITEM — INTERNAL LABELS" to **RESOLVED (LANDED `30e8422`)** with the live API (`x86_begin`/`L(n)`/
  `FR(off)`/`bb_slot_claim`), added a **START HERE** header (rebase onto `30e8422`; reference boxes `bb_pat_pos`
  loop-free + `bb_pat_span` looping; recipe in HANDOFF V3), and refreshed the `x86_asm.h` vocabulary list. The
  ONE remaining shared unknown is the VARIABLE-LENGTH define/jmp-pair loop (combinators + FENCE pair path + likely
  Raku `bb_nfa`) — flagged "STILL OPEN," to be designed once by whoever reaches a combinator first. Did NOT edit
  the other sessions' GOAL files (their own to touch). [SUPERSEDED by the next bullet — Lon directed top-of-file RUNG.]
- **RUNG NOW AT TOP OF EVERY GOAL FILE** (`.github` `09e07507`, Lon directive): a session reads its own
  `GOAL-{LANG}-BB.md` top-down, so the revamp priority was being missed (it lived only in the RULES-DRAFT + the
  bottom watermark — never "first"). Added a concise **"CURRENT PRIORITY — READ FIRST"** block right after the title
  in SNOBOL4/Icon/Prolog/Raku: the x86() goal, keystone **LANDED `30e8422` (REBASE FIRST)**, START HERE → RULES-DRAFT,
  reference boxes `bb_pat_pos`(loop-free)/`bb_pat_span`(looping), recipe HANDOFF V3, the STILL-OPEN combinator idiom,
  and each file's box list. Inserted ABOVE the byte-identical NO-C-BYRD-BOX FACT RULE (its md5 unchanged across all 5
  files, so that gate stays green); a top-of-file insertion is a different hunk from the bottom watermark, so live
  sessions (Icon on `bb_binop_arith` — a loop-free leaf that needs no keystone) rebase clean. Snocone omitted (not in
  the four-session divvy-up).

**Prior session (2026-06-01, Opus 4.8) — REG-2 COMPLETE (6/6): `bb_pat_break` (BREAK + BREAKX) migrated:**
- **REG-2 6/6** — finished by converting the last cursor-advancing leaf, `bb_pat_break`, off the legacy
  `[r10]`-cursor + `&Σ`/`&Σlen` movabs bakes to Σ=R13/δ=R14d/Δ=R15d. **Both arms in one pass** (all-or-nothing for
  the REG-FENCE grep): plain BREAK **153B, sites {125,129,149}** (internal Δ jge +63 / jnz +19 / jmp loop −88);
  BREAKX **290B, sites {125,130,134,265,286}** (α scan to first cset char + β rescan to next; identical per-loop
  internal jumps jge +87 / jnz +19 / jmp loop −88). `z` lives in `[zeta+8]`; BREAKX `z_orig` lives in `[zeta+12]`
  (the 4B padding of the 16B `rt_cs_t`), recovered as δ−z BEFORE the z++ at β entry. r11 + push/pop r11 dropped
  (Σ=r13 used directly in `movzx esi,[r13+rcx+0]` — the disp8 SIB form, 6B); only push/pop r10 around `strchr`
  remains. BINARY+TEXT both converted; both arms assembled via the `as`-transcribe route, objdump-verified, then
  Python byte-recounted to confirm every site and every internal-jump literal. Token-clean: zero
  `TEMPLATE_ADDR_SIG*`/`[r10]` in code OR comment. Zero `b.size()` introduced (stash-verified: 123 with AND without
  the diff — the +1 over the 122 watermark is the intervening Prolog tree, not this change).
- Single file touched: `src/emitter/BB_templates/bb_pat_break.cpp` (+155/−144).
- Gates all GREEN + invariant; m2 7/7 HARD held; no regression. **REG-2 is done → next is REG-RO** (then REG-3…5,
  REG-FENCE). REG-FENCE can now re-check SNOBOL m4 once a full pattern chain assembles+links (the `&Σ`/`&Σlen`
  bakes are gone from the cursor-advancing family; r10 traffic + RO `movabs` addresses are what REG-RO finishes).

**Prior session (2026-06-01, Opus 4.8) — REG-2 (5/6) cursor leaves + REG-RO step added:**
- **REG-2 5/6** (SCRIP `eb4bf7c`): migrated `bb_pat_len`/`rem`/`any`/`notany`/`span` off the `[r10]`-cursor +
  `&Σ`/`&Σlen` bakes to Σ=R13/δ=R14/Δ=R15. BINARY+TEXT both; span also dropped r11 + its push/pop (Σ=r13 used
  directly in the indexed byte load). Every BINARY byte map disasm-verified with `as`+`objdump` BEFORE writing
  (caught a real `movzx [r13+rcx]` SIB-encoding bug — r13 base needs the disp8 form, 6 bytes not 5); all 5
  token-clean. Per-box β semantics preserved. Per-box sizes/sites in the REG-2 rung above.
- **NEW STEP REG-RO** (REG ladder, inserted before REG-FENCE): READ-ONLY locals → IP-relative. The SNOBOL pattern
  BINARY arms bake RO ADDRESSES (lit / cset / `memcmp` / `strchr`) as `movabs` imm64, violating the RULES.md
  **ICON READ-ONLY LOCALS ARE IP-RELATIVE FACT RULE**; move each to `[rip+disp]` into a sealed RO trailer (the
  TEXT arms already do this). Makes the BINARY arm position-independent (a 2nd m4 lever) and — together with the
  RW register ladder — eliminates r10 entirely (the `[r10]` mirror writes + `push/pop r10` guards become dead).
  (Lon directive.)

**Prior session (2026-06-01, Opus 4.8) — FACT RULE + REG-0/1 + bb_match literal conversion:**
- **NEW FACT RULE "TWO LITERAL FORMS ONLY"** (above, after the NO-VALUE-STACK rule) — byte-identical ×5 GOAL-*-BB
  (block md5 `67020897`). The two literal forms (MEDIUM_BINARY = hand-coded byte map with HARDCODED literal offsets;
  MEDIUM_TEXT = literal asm) are CORRECT; the ONLY bad site is a FUNCTION that counts bytes (`b.size()`). `bytes()`,
  hardcoded `bin={{..}}`, literal rel32 deltas, `u32le/u64le`, `TEMPLATE_ADDR_*` are explicitly NOT bad.
- **NEW GUARD** `scripts/test_gate_no_handencoded_bytes.sh` — counts `b.size()` per `BB_templates/*.cpp` (comments
  stripped). Baseline **121 across 23 files** (informational; `--strict` = hard zero-check).
- **REG-0** (bb_match α establishes Σ=R13/Δ=R15/δ=R14 from SUBJECT ζ-slot; legacy `&Σ`/`&Σlen`/[r10] cells kept) +
  **REG-1** (bb_lit cursor→r14d / Σ→r13 / Δ→r15d; `&Σ`/`&Σlen` bakes removed; [r10] kept as mirror) — both LITERAL
  byte maps. **bb_match converted off `b.size()` → literal offset map** {87,91,121,141,150,151}, internal back-jump
  literal −78 (a genuine bad-site fix). PAT-BB probe **3/3** validates the offsets.
- (Mid-session a WRONG pivot abort-stubbed bb_lit/bb_match on a backward reading — REVERSED after Lon clarified.
  Net committed state is clean: literal byte maps, probe-green.)
**SNOBOL4 status:** mode-2 **7/7 HARD**, mode-3 5/6 (`define`/user-fn the lone fail — needs DEFINE registration +
a SNOBOL4 call frame + RETURN), mode-4 0/6 (pattern boxes bake `&Σ`/`&Σlen` imm64 → not relocatable; the REG
ladder removes that). prove_lower2 **67**, PAT-BB probes **3/3**, Icon m2 12/12 / m3 12/12 / m4 12/12, sm_dead 0,
concurrency OK (FACT RULES byte-identical-×3), purity 7 (MEDIUM_BINARY-exempt), g_vstack 0. FACT-RULE md5s the
audit pins: LOWER `5097ed94`, EMITTER `307534d6` (do not perturb the byte-identical-×3 blocks). ENV NOTE: the
build needs `libgc-dev` (`apt-get install -y libgc-dev`) — `core.h`/`raku_nfa_bb.c` include `<gc/gc.h>`.

**🔶 TEMPLATE-REVAMP v1 (PIVOT — Lon directive, 2026-06-01, SCRIP `2111555`).** Kill the two-divergent-arm +
hand-counted-`bb_bin_t` churn. New header-only `src/emitter/BB_templates/x86_asm.h`: self-encoding `x86_*`
helpers that switch BINARY/TEXT on `g_medium` (invisible in the template) + in-band patch records (L/J/D)
walked by `bb_emit_x86` (positions DISCOVERED, no offset table). Template API is ONE
`x86(mnem, ...)` keyed on the mnemonic (1st arg; trailing args' cardinality/type select the form via overloading;
the typed encoders are the internal impl) — Lon eureka 2026-06-01. `bb_lit` converted → ONE return, pure concat,
NO template locals, `MEDIUM_MACRO_DEF` dropped; BINARY arm byte-identical to `65686c2` (addr-masked). GO-FORWARD
(Lon): **TEXT-FIRST** — keep the GAS arm as source of truth, **throw away the hand-coded BINARY**, let `x86_*`
regenerate it position-independent (= REG-RO); **no safety net / no full regression** (four sessions fix typos),
move straight-forward, we are at GROUND ZERO. ⚠ This SUPERSEDES the TWO-LITERAL-FORMS / TEMPLATE-ONLY-EMISSION
FACT RULES — the rule text (5 GOAL files + RULES.md) + purity/concurrency gates need the coordinated rewrite to
land (grand-master-reorg). Detail + next steps: `HANDOFF-2026-06-01-OPUS48-SNOBOL4-BB-TEMPLATE-REVAMP-V1.md`.

**⭐ NEXT (SNOBOL4).** **(0) BB-LITERAL CLEANUP — drive the new GUARD's `b.size()` count to zero**
(`scripts/test_gate_no_handencoded_bytes.sh`, **121/23** baseline): rewrite each `b.size()` function-counter to a
hardcoded LITERAL offset map (the way bb_match was converted this session). ⚠ The in-scope handful is
`bb_pat_alt` + `bb_pat_cat`, but these are NOT a mechanical conversion: their `b.size()` sits inside a loop over
`g_emit.xa_bb_emit_pair_n` (a runtime-variable define/jmp pair count), so literal offsets need a DESIGN answer
(how a variable-length box gets literal patch offsets) — solve that before touching them. The other ~21 files are
Icon/Prolog/generic boxes (outside the SNOBOL goal). **(1) REG LADDER** (see the 🔴 CURRENT PRIORITY
section at the top): migrate the pattern BB templates off the legacy `[r10]`/`&Σ`/`&Σlen` model to the ratified
registers Σ=R13/δ=R14/Δ=R15/ζ=R12 — REG-0/REG-1 (bb_match α + bb_lit) landed, and **REG-2 is now COMPLETE 6/6**
(bb_pat_len/rem/any/notany/span SCRIP `eb4bf7c`; **bb_pat_break BREAK+BREAKX this session**). **Next is REG-RO**
(RO addresses → `[rip+disp]`, kills r10), then REG-3 (pos/tab) → REG-4 (combinators) → REG-5 (generators) →
REG-FENCE. **(2) THEN** PB-RB-4 (STITCH_SEQ/STITCH_ALT — topology already proven, only the emitter wiring + drive
remain; mode-3 `S ('a'|'b')` and `S 'a' 'b'`), PB-RB-5…OPT, and BROK-0…BROK-3. The pattern-engine breadth (PB-RB
ladder) is the LONG POLE for the SNOBOL4 corpus. Older per-session writeups live in the `HANDOFF-*.md` files.

**🔶 TEMPLATE-REVAMP v2 (continuation — 2026-06-01, Opus 4.8, SCRIP `d96e1b0`).** Four more boxes converted
to the `x86()` self-encoding form + `bb_lit` hardened: **`bb_pat_rem`, `bb_pat_len`, `bb_pat_any`,
`bb_pat_notany`, `bb_lit`** are now **`pBB`-free END-TO-END** (template fn / `extern "C" void bb_X(void)` /
`bb_templates.h` prototype / `emit_core.c` dispatch all parameterless) and **`_.node`-free** (grep proof: 0
of each in all five, code + comments). New op-promotion: `sm_emit_t.op_sval/op_ival` set at the single
dispatch point from `nd->sval/ival`; templates read `_.op_*`. `x86_asm.h` += 64-bit `test rax,rax`
(width-aware ALU), `x86_movzx_subj_byte` (indexed subject-byte load), and imm8 short-form for `x86_add`/`sub`
(BINARY now matches `as`). **NEW rules draft `.github/GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md`** (R1–R13 normal +
the "reads only `_`, no `pBB`, no neighbor" **FACT RULE** — compiler-enforced via parameter removal + a
one-line `_.node` grep gate; reasons: no confusion + BB-fusion impossible). NOT yet folded into the 5 GOAL
files (that + the internal-label record design + `test_gate_template_no_node.sh` are the next session's
grand-master-reorg). Gates: m2 7/7 HARD · m3 5/6 · m4 0/6 · probes 3/3 · prove_lower2 67 · Icon m2 12/12 ·
concurrency OK (sm_emit_t field add did NOT perturb the byte-identical-×3 blocks) · purity clean · g_vstack 0.
Detail: `HANDOFF-2026-06-01-OPUS48-SNOBOL4-BB-TEMPLATE-REVAMP-V2-NO-PBB.md`. **OPEN (gates looping boxes):**
internal-label record kind for SPAN/BREAK/combinators/generators (L/J/D only encode the 4 ports today).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
