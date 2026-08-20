# FINDING s178 (2026-08-20, HQ/sole-implementer, Fable 5) — THE BEAUTY WALL IS THREE STACKED LAYERS, AND THE BOTTOM ONE IS EIGHT LINES LONG

**Resumes:** GOAL-SNOBOL4-100 s177-HANDOFF cursor ("deferred capture call inside a build-time-fn-returned stored pattern never fires"). **Witnesses minted:** `corpus/probe/bfn/` (7 programs, all oracle-refed vs live sbl). **SCRIP unchanged this slice** — investigation + witnesses only, per STOP-AT-REPRODUCER (Lon s177, re-ordered in-chat s178).

## Receipt 1 — the beauty-context hypothesis is FALSIFIED
`bfn_transplant_parse.sno` (27 lines, self-contained: real counter.inc/semantic.inc machinery + `Parse = nPush() BREAK(nl) nl nPop()` + the real double-defer match line `Src POS(0) *Parse *Space RPOS(0)`, fz-poisoned) reproduces the wall with ZERO beauty context: oracle fires `PushCounter()`+`PopCounter()` and matches; SCRIP fires NOTHING and nomatches, **m3 ≡ m4**. Build-sequence position (~100 prior assignments) and PAT$/EXPR$ census are dead ablation branches — do not re-run them.

## Receipt 2 — the ablation matrix (default env, m3; SCRIP `a008b4b9`, RT_OPT -O0)
| witness | shape delta | oracle | scrip m3 | scrip m4 |
|---|---|---|---|---|
| bw2 | fn-ret capture + literal tail `'ab'`, seam | PC·match | PC·match | **SEGV** |
| bfn_inline_ctl (bw6b) | capture built INLINE (no fn), `BREAK(nl) nl`, seam | PC·match | PC·match | **SEGV** |
| bfn_break_lit_ctl (bw6d) | fn-ret, `BREAK('x') 'x'` LITERALS, seam | PC·match | PC·match | **SEGV** |
| bw6g / bw6h | fn-ret, var in ONE position only | PC·match | PC·match | (not run) |
| **bfn_break_var_nl (bw6)** | fn-ret, `BREAK(nl) nl`, `nl=CHAR(10)`, concat subject, seam | PC·match | **0 fires, nomatch** | **0 fires, nomatch** |
| **bfn_break_var_q (bw6k)** | bw6 with the variable RENAMED nl→q, nothing else | PC·match | **SEGV (core dump)** | 0 fires, nomatch |
| bw6i (var b='x', literal subject) | | PC·match | **6× over-fire + match** | 0 fires, nomatch |
| bw6c (no seam, direct match) | | PC·match | **6× over-fire + match** | 0 fires, nomatch |
⛔ **bw6 vs bw6k differ ONLY in a variable's NAME and the outcome differs (silent nomatch vs SEGV): the mechanism is a WILD/layout-dependent write, not clean logic.** The 6 of the over-fire = subject length = one fire per unanchored ANCHOR ATTEMPT, including FAILED attempts — conditional-assignment (`.`) discipline broken for the fn-returned defer (manual p.134: deferred until assignment, once, on success).

## Receipt 3 — the ladder bottoms out BELOW beauty: two primitives are broken at HEAD
- **`cap_min_name.sno`** (8 lines): `'ab' LEN(1) . *V` → oracle `match V=a`; SCRIP at default `match V=` (capture silently dropped), **BOTH modes**. `SCRIP_CAP_NAME_STRICT=1` cures it in **BOTH modes** (m4 verified: env at compile, correct output).
- **`cap_min_call.sno`**: `'ab' LEN(1) . *PC()` inline → m3 CORRECT at default and strict; **m4 SEGVs at default AND at strict** — the simplest deferred capture CALL, no stored pattern, no seam, no fn-build. The m4 crash is therefore its OWN layer, orthogonal to the strict switch.
- **`SCRIP_CAP_NAME_STRICT` (s170 seat7 cure, `97ad2912`, still DEFAULT OFF) is three synchronized halves** — `lower_snobol4.c:1240` + `bb_match_end.cpp:29` + `pattern_match.c:666`, one env name. The flip never happened: queue row 3 `b1c-retreat` was ⏳seat7 when the fleet was retired (HQ-67). **probe/b1 at HEAD default: 5 FAIL** (`b1c_capname_call_return`, `b1c_capname_var_target`, `b1c_eval_fn_pattern_retreat`, `b1c_patvalued_formal_retreat`, `b1_eval_pattern_defer_call`) — all the strict class.

## Receipt 4 — strict does NOT close the family (m3, SCRIP_CAP_NAME_STRICT=1)
bw2/bw6b/bw6d → correct. bw6/bw6i/bw6j → **6× over-fire + match**. bw6k → nomatch (STILL differs from bw6 on the name swap ⇒ wildness survives strict). bw6c → empty output rc=0. transplant → nomatch. So strict is NECESSARY (layer 1) and NOT SUFFICIENT.

## Receipt 5 — beauty itself under strict (m3)
`beauty.sno < beauty.sno` with strict: the 7 leading comment lines emit BYTE-CORRECT, then `Parse Error` at `START` — identical to minimal input. The entire self-host now reduces to layers 2+3.

## THE THREE LAYERS (= the M1 ladder from here)
1. **L1 — capname strict flip:** cure built s170, disarmed. Owed before flip: corpus-wide A/B + `.s` blast radius (flip precedent HQ-58/59: Lon's desk). Closes dc-class + 5 red b1 rows.
2. **L2 — fn-returned-pattern defer discipline (NEW class, THE beauty wall):** a pattern RETURNED by a compiled DEFINE body carrying `epsilon . *FN()` + `BREAK(var) var` tail: fires per-attempt instead of once-at-success, wrong-fails at anchor 0, and the whole thing is layout-wild (name-swap flips outcome). Note `runtime_eval.c`'s s172 RETAIN covers only the EVAL road — the compiled-fn-RETURN road never passes through it. ASM-DIFF pair pre-built: `bfn_break_lit_ctl` (pass) vs `bw6i` (over-fire), one ingredient apart (literal→variable), both media.
3. **L3 — m4 deferred-capture-call SEGV:** `cap_min_call` m4 core-dumps at the simplest possible shape; m3-passing siblings bw2/bw6b/bw6d also SEGV m4. Likely the rows-2/5 fragment-landing class (`b1c-m4-seam`/`m4-fragment-landing`), which now has a witness 20× smaller than the previous smallest.

## Corrections to standing text
- s177-HANDOFF's "the standalone twin PASSES both engines" was measured on m3 only; the same twin shape **SEGVs m4** (bw2). m3≡m4 is breached across this whole family.
