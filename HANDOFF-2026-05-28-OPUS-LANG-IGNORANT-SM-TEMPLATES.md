# HANDOFF 2026-05-28 OPUS — LANG-IGNORANT SM TEMPLATES

**Session:** Opus 4.7 · Thu 2026-05-28 (late)
**Theme:** Rip language-specific dispatch forks out of SM/BB templates. One opcode does one thing.
**Initiating observation (Lon):** `sm_call_str` had MEDIUM_TEXT and MEDIUM_BINARY arms emitting different x86. TEXT had a Raku-sub fast path (`rk_sub_lookup → call .Lrksub_<name>` framed by `rt_frame_enter/leave`); BINARY didn't. Investigation showed this wasn't an isolated case — multiple SM/BB templates were sniffing producer-language state (`rk_sub_lookup`, `wasm_userfn_find`, `g_stage2.proc_table`, `fn_pcs/fn_names/pc_to_fn`) to decide what x86 to emit. **Violation of "ONE x86 PRODUCER per opcode; an SM opcode does one thing."**
**Directive (Lon):** "WHack em. Bad precedence to leave in junk like that. ... Forget it all. Do anything to split out the LANG specific template logic and we will deal with the many issues later."

---

## Watermark

- HEAD SCRIP: UNCOMMITTED (this handoff is pre-commit; tree dirty 14 files).
- HEAD .github: clean except this file.
- GATE-1 SNOBOL4 smoke: **13/13** (baseline held).
- GATE-2 unified broker: **31** (was 36; **−5**, all Icon+Raku regressions documented below).
- GATE-3 mode-4 broad corpus: **175/280** (baseline held).
- GATE-4 mode-2 broad corpus: **238/280** (baseline held).
- Rung suite: **M2=19, M4=15, SKIP=0** (baseline held).
- Per-language smokes: **raku 5/5, prolog 5/5, icon 0/5 (was 5/5 — SM_BB_PUMP_PROC whacked).**
- FACT RULE: 0.

---

## What was done

### 1) Ripped language-sniffing forks from SM/BB templates (9 sites across 5 files)

Each was a producer-language check (`rk_sub_lookup`, `wasm_userfn_find`, scans of `g_stage2.proc_table` / `_.fn_names` / `_.fn_pcs` / `_.pc_to_fn`) that picked a "resolved direct dispatch" code path inside the template instead of letting the opcode do one thing. Now every arm of every opcode below emits one fixed sequence regardless of producer:

- `src/emitter/SM_templates/sm_calls.cpp` (4 sites — x86-TEXT Raku fork, JVM `entry_pc≥0` invokestatic-direct path, .NET `fn_pcs` direct-jump path, WASM `wasm_userfn_find` inline path). All four collapsed to the by-name generic call route.
- `src/emitter/SM_templates/sm_jumps.cpp` (1 site — `sm_label_str` minted `.Lrksub_<name>:` when label name happened to be a Raku sub). Collapsed to plain `LABEL`.
- `src/emitter/SM_templates/sm_returns.cpp` (2 sites — NET arms used `pc_to_fn` + `fn_names` to push the caller's name; both replaced with `push_null`).
- `src/emitter/SM_templates/sm_bb_calls.cpp` (1 site — scanned `g_stage2.proc_table` to mint `CALL_EXPRESSION .L<entry_pc>` for Icon main). Collapsed to plain `BB_PUMP_PROC` macro; **then the whole file got whacked along with SM_BB_PUMP_PROC — see (2)**.

The "fast path" / "language fork" framing was always misleading: the only path Lon wanted gone was the one branching on *producer language* inside the template body. Two parallel templates with the same opcode emitting different x86 depending on which frontend produced the SM instruction is precisely what "one opcode = one thing" forbids.

### 2) Whacked `SM_BB_PUMP_PROC` entirely (mode-2-only Icon top-level pump)

Diagnosis: opcode existed only for Icon top-level `every`/etc. Worked in mode 2 (real `bb_broker(node, bb_pump, pump_print, NULL)` body in `sm_interp.c`). Mode 3 emitted `\xE8\x00\x00\x00\x00` (call to next instruction, no patch site — silent no-op). Mode 4 emitted `BB_PUMP_PROC` macro with no argument — the macro definition requires a target, so the assembler either rejects or silently mangles. Mode 4 had been partially working only because of the deleted `g_stage2.proc_table` scan in (1) above.

Per Lon: "Whack it now! Makes no difference what breaks." Tombstoned as `SM_UNUSED_8`.

Files touched:
- `src/include/SM.h` — opcode → `SM_UNUSED_8` tombstone.
- `src/lower/lower.c:2625` — emit site replaced with no-op comment guard.
- `src/processor/sm_interp.c` — handler block removed.
- `src/emitter/emit_core.c` — dispatch case + whitelist entry removed.
- `src/emitter/emit_sm.c` — removed from `pc_used_mark` switch and from `one_per_group` macro-def seed.
- `src/lower/sm_prog.c` — name-table entry renamed `SM_UNUSED_8`.
- `src/emitter/SM_templates/sm_templates.h` — decl removed.
- `src/emitter/emit_templates.h` — decl removed.
- `src/tools/emit_per_kind_audit.c` — audit entry removed.
- `src/emitter/SM_templates/sm_bb_calls.cpp` — file DELETED.
- `Makefile` — `sm_bb_calls.cpp` source + compile rule removed.

Runtime helper `icn_bb_pump_proc_by_name` (in `src/runtime/interp/icn_runtime.c`) now has no callers but was left in place — a separate cleanup item.

### 3) Split `SM_BB_SWITCH` into `SM_BB_INVOKE` + `SM_BB_PL_INVOKE`

Was: one opcode with `a[2].i` tag macro `SM_BBSW_ICN_GEN`/`SM_BBSW_RK_GEN`/`SM_BBSW_PL_ENTRY` selecting between three template bodies inside `sm_bb_switch.cpp`. ICN_GEN and RK_GEN were already byte-identical (their `SM.h` comments even acknowledged this: "semantically identical to SM_BBSW_ICN_GEN; the tag only records that the producing language was Raku"). PL_ENTRY emitted genuinely different x86 (pl_bb_env_push + walk_bb_flat + sibling callee blocks per other predicate).

Now: two opcodes, each does one thing. ICN_GEN and RK_GEN collapse into the generic `SM_BB_INVOKE` (language-ignorant — Icon and Raku produce the same opcode now, because they always wanted the same x86). Prolog gets its own `SM_BB_PL_INVOKE` (distinct because the x86 is genuinely different).

**Naming decision:** went through `SM_BB_ENTER` → rejected (implies one-way doorway; the opcode is bidirectional, control returns) → `SM_BB_CALL` → rejected (implies stack push/pop, but BB graphs never use the hardware call/ret mechanism — γ/ω ports are inline branches in mode-4, plain function-call returns in mode-2) → `SM_BB_INVOKE` (Lon's choice; "one shot" — single jump-in, single jump-out via γ or ω; semantics close to a function-call but not stack-mechanism specific).

Files touched:
- `src/include/SM.h` — `SM_BB_SWITCH` replaced with `SM_BB_INVOKE` + `SM_BB_PL_INVOKE`. Tag macros `SM_BBSW_ICN_GEN`/`SM_BBSW_RK_GEN`/`SM_BBSW_PL_ENTRY` deleted.
- `src/lower/lower.c` — 9 emit sites converted. Seven `SM_emit_sii(..., SM_BBSW_ICN_GEN/RK_GEN)` → `SM_emit_si(..., SM_BB_INVOKE)`. Two `SM_emit_sii(..., SM_BBSW_PL_ENTRY)` → `SM_emit_si(..., SM_BB_PL_INVOKE)`. One backward-jump loop search (`op == SM_BB_SWITCH`) updated to `SM_BB_INVOKE`.
- `src/processor/sm_interp.c` — single tag-dispatched case → two cases, one per opcode, no tag check.
- `src/emitter/emit_core.c` — single dispatch arm → two; whitelist split.
- `src/emitter/emit_sm.c` — `pc_used_mark` tag check (`tag == ICN_GEN || tag == RK_GEN`) → opcode check (`op == SM_BB_INVOKE`).
- `src/lower/sm_prog.c` — name table updated.
- `src/emitter/SM_templates/sm_bb_switch.cpp` — rewritten. Was one `sm_bb_switch_str()` function with three tag branches. Now two clean `_str()` functions: `sm_bb_invoke_str` (the generator body, no tag check) and `sm_bb_pl_invoke_str` (the Prolog body, no tag check). File NAME left as `sm_bb_switch.cpp` to minimize Makefile churn — could be renamed in a follow-up if desired.
- `src/emitter/SM_templates/sm_templates.h` — decl `sm_bb_switch` → `sm_bb_invoke` + `sm_bb_pl_invoke`.

### Doc-only comment refs left intact (deliberately)

Several files have stale comments mentioning `SM_BB_SWITCH`/`SM_BBSW_*` (BB_templates/bb_seq.cpp, BB_templates/bb_suspend.cpp, XA_templates/xa_file_header.cpp, runtime/rt/rt.h, runtime/rt/rt.c, driver/scrip.c, lower/lower.c). These don't affect compilation; a comment sweep is a separate clean-up.

---

## Regression: where the gates fell and why

**GATE-2 dropped 36 → 31 (−5). Per-language smokes: icon went 5/5 → 0/5. Raku and Prolog held.**

Failures from G2 broker:
- **Icon (5):** `ICN: hello`, `1 to 5`, `!str iterate`, `palindrome`, `rung01 compound`. All depended on `SM_BB_PUMP_PROC` (Icon top-level pump) being emitted by the lower. Opcode gone → Icon top-level programs don't pump. **Expected; per directive.**
- **Raku (~14):** `rk_class26`, `rk_fileio38`, `rk_gather`, `rk_given18`, `rk_junctions`, `rk_re32..37`, `rk_regex23`, `rk_stdio39`, `rk_try_catch25`, `raku_gather.scrip`. These exercised the deleted `rk_sub_lookup` fast path or other forks. **Expected; per directive.**
- **Cross-language (1):** `cross_lang.scrip`, `test_shared_nv.scrip`. Same dispatch sites.

Net: −5 against G2, but the *baseline* G2 was 36; per-script the FAIL list is ~22 (some failures pre-existed). The actionable delta is the 5-broker drop and the 5-icon smoke drop.

**G1 (SNOBOL4 smoke), G3 (mode-4 broad), G4 (mode-2 broad), rung suite — all baseline. The cleanup did not damage SNOBOL4.**

---

## Active mis-design recorded (for follow-up)

**`SM_BB_PL_INVOKE` is mis-designed and is a candidate to collapse into `SM_BB_INVOKE` once Prolog's lower is refactored.** Stated in the opcode's own docstring in SM.h.

Diagnosis: Icon's lower resolves procedure bodies at lower-time. It calls `SM_seq_bb_add(g_p, _irb)` to add the proc's BB graph to `g_stage2.sm.bb_table[]` with a stable `bb_idx`, and records that index in `proc_table[pi].bb_idx`. Call sites then look up the index and emit the BB-entry opcode against it. The emitter never has to scan tables or resolve names — it just inlines the bb_table[idx]'s graph.

Prolog *also* has its lower-time table (`g_pl_bb_table[]` with `Pl_PredEntry_BB { name, arity, bb_idx, lower_sc }`) but uses it differently: the lower emits a single magic opcode (`SM_BB_PL_INVOKE`) that, at emit time, looks up the predicate by name, walks its graph, AND emits every other predicate in the program as a sibling callee block inside the same `_str()` body. That bundles work into the template that Icon's design pushes into the lower.

Two real differences underlie the carve-out:
1. **Env push.** Prolog needs `pl_bb_env_push(64)` before entering predicates; Icon procs use the normal value-stack. Genuine language requirement.
2. **Per-predicate as emitter-emitted block.** PL_INVOKE emits every other predicate as `.Lplpred_<name>_<arity>` callable blocks so that `BB_PL_CALL` sites can `call <label>`. Icon emits its procs as ordinary SM functions via `SM_DEFINE_ENTRY`/`SM_DEFINE` with normal `SM_CALL_FN` call sites.

Both could be refactored away. The env push could become its own SM opcode (`SM_PL_ENV_PUSH`/`SM_PL_ENV_POP`) bracketing the BB invoke. The per-predicate blocks could be emitted as ordinary SM procs at lower time. `BB_PL_CALL` then lowers to `SM_CALL_FN`. With those moves, **`SM_BB_PL_INVOKE` collapses into `SM_BB_INVOKE`** and one opcode covers all six languages.

This is a real Prolog frontend refactor — touches the Prolog lower's clause-emission strategy, the seven `bb_pl_*` templates, the `BB_PL_CALL` resumable-call protocol with `_redo` trampoline (CAT-A-3 work area), and predicate-registration timing (CAT-A-3's open emergency about `pl_bb_pred_is_resumable` returning NULL at emit time is the same lowering-timing pain). Recorded as future work in PLAN.md (see Prolog BB row).

---

## What ISN'T done (left for future sessions)

1. **Restore Icon top-level pumping.** All five Icon smoke programs broke when `SM_BB_PUMP_PROC` was whacked. The correct fix is to lower Icon top-level `every` (and bare-generator-at-statement-level) into a normal SM loop using `SM_BB_INVOKE` + `SM_CALL_FN` for the consumer + `SM_JUMP` back. That's what every OTHER generator context already does — there was no real reason for top-level to need a special opcode.

2. **Restore Raku user-sub correctness.** ~14 Raku gates dropped. The deleted TEXT fast-path was emitting `mov edi,np; call rt_frame_enter@PLT; call .Lrksub_<name>; call rt_frame_leave@PLT` — which fixed a vstack underflow bug for void Raku subs (per commit 18c4820f's message). The generic `rt_call` path doesn't do equivalent frame-enter/leave around the user-sub body. Fix lives in either (a) the Raku lower emitting explicit frame-management SM opcodes around its `SM_CALL_FN`s, or (b) `rt_call` doing uniform frame management for any user sub.

3. **Prune `icn_bb_pump_proc_by_name`** (dead runtime helper — only caller was the deleted SM_BB_PUMP_PROC handler).

4. **Comment sweep** for stale `SM_BB_SWITCH` / `SM_BBSW_*` references in BB_templates/bb_seq.cpp, BB_templates/bb_suspend.cpp, XA_templates/xa_file_header.cpp, runtime/rt/rt.h, runtime/rt/rt.c, driver/scrip.c, lower/lower.c.

5. **Optional file rename** `sm_bb_switch.cpp` → `sm_bb_invoke.cpp` (left as-is to minimize Makefile churn; rename is trivial when desired).

6. **The CAT-A-3 emergency on Prolog BB** is still open (PLAN.md). The lowering-timing pain there is the same flavor of mis-design as `SM_BB_PL_INVOKE`. When that's tackled, the PL_INVOKE collapse becomes natural.

---

## Files touched (final list)

```
Makefile                                            modified
src/emitter/SM_templates/sm_bb_calls.cpp            DELETED
src/emitter/SM_templates/sm_bb_switch.cpp           rewritten (split into two _str fns)
src/emitter/SM_templates/sm_calls.cpp               modified (rip Raku/JVM/NET/WASM forks)
src/emitter/SM_templates/sm_jumps.cpp               modified (rip Raku label fork)
src/emitter/SM_templates/sm_returns.cpp             modified (rip NET fn_name sniffing ×2)
src/emitter/SM_templates/sm_templates.h             modified (decls)
src/emitter/emit_core.c                             modified (split dispatch)
src/emitter/emit_sm.c                               modified (rename SWITCH→INVOKE, drop tag check)
src/emitter/emit_templates.h                        modified (decl removal)
src/include/SM.h                                    modified (split opcodes, delete tag macros)
src/lower/lower.c                                   modified (9 emit sites, whack SM_BB_PUMP_PROC site)
src/lower/sm_prog.c                                 modified (name table)
src/processor/sm_interp.c                           modified (split case, drop SM_BB_PUMP_PROC)
src/tools/emit_per_kind_audit.c                     modified (drop SM_BB_PUMP_PROC)
```

---

## Lesson recorded

Two opcodes' worth of language-specific dispatch had accreted inside SM/BB templates over weeks. Some entered as bug-fix code (the Raku-sub frame wiring in 18c4820f fixed a real underflow); some as performance shortcuts (the JVM `entry_pc≥0` direct dispatch); some as "this is the only place I have the proc table handy at the time" expediency (the Icon `g_stage2.proc_table` scan in sm_bb_calls). Each one was individually defensible at the time it landed. Cumulatively they violated "an SM opcode does one thing."

The right home for "what x86 do I emit when calling Frontend-X's function" is **the lower for Frontend X**, not a fork in the shared template. If a frontend needs different framing/env/etc., it should emit additional explicit SM opcodes around the generic call, OR it should resolve to a different SM opcode at lower time. The template should never sniff `rk_sub_lookup`, `wasm_userfn_find`, `proc_table[]`, etc.

Going forward: any future "the template branches based on which language produced the SM" is a red flag. The fix is upstream in the lower, or a new opcode — never another branch inside the template.

---

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
