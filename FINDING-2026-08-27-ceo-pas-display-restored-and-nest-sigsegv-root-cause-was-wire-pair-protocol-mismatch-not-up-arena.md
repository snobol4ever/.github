# FINDING: PAS-DISPLAY restored on THE THREE ZETAS; the nest* rc=139 class root cause was a wire-pair protocol mismatch, not the __up_* arena

**Session:** ceo (Fable), 2026-08-27, row `pas-display-revival` · **Tree:** SCRIP @ this commit

## What landed

1. **IR_VAR_FRAME / IR_ASSIGN_FRAME re-added** to the reduced IR (they were dropped whole in the GZ#5 IR reduction; PASCAL-RESTORE `32ccfdf3` then rebuilt uplevel access on `__up_*` GVA capture globals — the mechanism hq_C's diagnosis pass found as "the only mechanism running").
2. **Lowering**: `lower_pascal.c` resolves every name through one `pas_resolve2` (scope chain walk); an uplevel hit lowers to a frame node carrying the var name (`sval`), the absolute owner level (`nd->seal` — IR_LIT is one anonymous union, so `dval` clobbers `sval`; the first build crashed on exactly that, name pointer = double 1.0's bits), and the owner proc name as an unwired `IR_LIT_NAME` operand. The `__up_*`/`__upsv_*` capture arena (mangle, prepass scan, three entry/exit copy loops) is **deleted** — zero occurrences remain.
3. **Templates**: `bb_var_frame` rewritten, `bb_assign_frame` new — `mov rax, r13|r14|r15` per the FROZEN map (rbx=L0 via GVA · r13=L1 · r14=L2 · r15=L3), owner slot resolved at emit time via `stage2_owner_varslot()` → the owner graph's ZLS vslot table (safe: `drive_slots_all()` lays out every graph before any emission — driver's own comment, scrip.c:81). L≥4 bombs loudly (fallback rung open, deep5 is its witness).
4. **Display save/set/restore**: zframe prologue stores the caller's display[L] at `[kt-40]` (a measured-free header cell — kt = ZLS region + 48; no RSP shift, no alignment change, recursion-safe) and sets display[L]=frame; both plain epilogue arms restore it. Gated PURELY on the graph's `decl_level` (new `IR_graph_t` field, set only by `lower_pascal_stage2`; every other language is 0) — no language enum, `emit_no_lang` holds by construction, same as the 2026-06-27 landing.

## ⭐ The root cause hq_C's pass attributed to __up_* was actually a WIRE-PAIR PROTOCOL MISMATCH

hq_C's (excellent) diagnosis stopped at "whatever `__up_*` does, it corrupts state that only matters at exit." Measured further with a hardware watchpoint on the owner's `x` cell: **the uplevel write lands correctly** (5→15 in the owner's frame, via r13) — and the crash still fires. The true mechanism:

- `bb_call_proc_staged` callers **push the γ/ω wire pair on the stack** (`bcps_wire_push`, s110/s111 arms) and, per `bcps_wire_pair_consumed()` defaulting to 1, emit **no landing release** — the contract is "the callee consumes the pair" (SNOBOL DEFINE procs do, via the fnrbp2 RETURN floaters).
- The **pure-zframe epilogue never consumed it** — it exits through the `[kt-24]` rcx-wire (which only ever worked because the last caller-side `lea rcx, γ-landing` happens to leave the γ landing in rcx at entry). The pushed pair stays seated → **every frame-relative access in the CALLER is skewed by 16 for the rest of its body**.
- Every observed symptom is this one skew: `writeln(x)` reads `[rsp+160]` = frame+144 = the literal cell holding 5 (the "prints 5"); the epilogue r13 restore reads frame+168 = x's value cell (the "r13=15" hq_C saw as "r13=0"-class garbage); the γ wire load reads a data cell = 0 (the "jump to 0x0").
- Only the **zframe-caller → zframe-callee** pairing has this hole, and Pascal nested procs are the only shape that exercises it — hence exactly the nest*/deep* family red and everything else green. The `xa_flat` wire-stack arm's own comment recorded the hole: "pure zframe_graph (Prolog/Raku/Pascal), whose callee side this rung never touched."

**Cure:** PAS-NEST pair-consuming epilogues (γ: pop landing, discard ω, jmp; ω: discard γ, pop landing, jmp), gated on `decl_level >= 1` — a class that was 100% red, so no green path could regress; Prolog/Raku/Icon zframe graphs (decl_level 0) keep byte-identical epilogues.

## Measured results (this tree, -O0, mode-3 unless noted)

- **DONE-WHEN both green:** `uplevel2.pas` and `uplevel3.pas` byte-match their `.ref` at rc=0 — 240,000,000 uplevel read+writes inside the 8s timeout, through display registers, zero chain walks.
- **Blast radius 8 SIGSEGV → 0:** nested, nest2, nestcount, nested_vp_writeback, nestfunc, nestrec, nestshadow, deep5-class all cured; 11/14 nest*/deep* PASS. Remaining 3: nestvar2/nestvar3 (pre-existing tvsubs bomb, IDX-UNIFY rung, untouched by this work) and deep5 (the honest L≥4 display-fallback bomb — open rung).
- Gate battery (pristine): recorded in the row baton with this commit.

## Open follow-ups (routed to the baton)

- L≥4 display fallback (deep5 witness) — old design's chain-walk needs a static-link home that today's frames don't carry; needs its own rung.
- byref-of-uplevel argument passing (IR_VAR_FRAME_REF) — lowers by plain name today, known-red class.
- `SCRIP_PAS_ZFRAME` env switch in `lower_pascal_stage2` — a mode switch surviving the zeta eradication; candidate for the no-modes law.
- hq_P's do-not-score-Pascal ruling still stands (write-width oracle question) — nothing here builds a Pascal pass-rate; witnesses are cmp-graded.
