# HANDOFF — 2026-06-10 — Fable 5 — BB-FIXUP 43rd attended run

## What landed
**SCRIP dc72af7** — `FIXUP bb_atom_string.cpp` (the 42nd-run-deferred heavy ring stop), ONE commit, 4 files:
- `src/emitter/BB_templates/bb_atom_string.cpp` REGENERATED 425→157: ONE-MEDIUM unification (MEDIUM_TEXT ins2 duplicate tree deleted; 6 arm families once on medium-complete x86() forms) + CV8 fence + R4 one lazy-IF return + R6 zero locals (5 R2-KEEP statics: bas_fn/bas_cn/bas_cp/bas_s/bas_term).
- `src/emitter/emit_bb.c` — op_parts delivery MERGED INTO the existing `bb_prepare` IR_BUILTIN block (args 0-2 tag/ival/sval; sval only for ATOM|STRUCT|ARITH per CAT-D-1; node ptrs opaque at ival[8+j]; char_type inner at slot 3 / ival[11]).
- `bb_common.h` + `bb_resolve.cpp` — signature `(pBB, fn, hdr)` → `(hdr)`.
- Audit 139→15 ([S] residue: bas_term per-medium term-builders rb=1 mt=2 + R2-KEEP computers). GRAND 2373→**2249** (−124, sole mover). Gates at floors throughout; 2 concurrents absorbed mid-land with full re-certification.

## Proof shape (reusable for the remaining ins2 files: bb_list, bb_io, bb_is_cmp, bb_type_test, bb_retract_throw, bb_term_io…)
7 per-family m4-LIVE probes; A/B normalized .s diff (bbN/.LN/.SN) → zero unexplained residue; behavior m2/m3/m4-run identical (m3 = pre-existing GZ-fence abort both sides). **Explained-delta set:** TEXT `mov r,N`→`movabs r,N` spelling · β-row line-split · strtab intern-order artifact (helpers interning inside chained-+, GCC right-to-left; string SETS must verify identical) · chars-path-B BINARY sub-rsp 8→16 (unified on the LIVE-proven TEXT value; m3-silent arm).

## Two lessons (recorded in tracker + GOAL watermark)
1. **PREP-SHADOWING:** bb_prepare already had an IR_BUILTIN block (bb_ls intern for write, bb_op_lbl for is). A new early-return block above it starved bb_io's write arm — `write(yes)` emitted `xor edi,edi`. Gates stayed green; ONLY the A/B probe diff caught it. Grep bb_prepare for an existing per-kind block before adding one.
2. **COUNTER SEMANTICS:** med_inv counts the `IF(MEDIUM_BINARY` combinator form, not plain if-statements. bas_term restructured to statement form → 103 floor held (transient 104 caught pre-commit).

## Done this run besides the stop
- GOAL-BB-FIXUP.md CLEANED on Lon's word: 189KB→42KB; runs 5-38 watermarks compressed to a git-history pointer (39th/42nd/43rd kept full); FIX-7a/7b one-lined as CLOSED; FIX-8/8a/8b/9 compressed to operative rules; superseded BINARY-ARM PORTS block compressed; `prove_lower2.sh` → `prove_lower.sh` corrected throughout (the script was renamed; Session Setup and C3 referenced the dead name).
- Tracker: 43rd-run header added, bb_atom_string entry rewritten with the landing + [S] note, `# CURSOR: bb_call.cpp`.

## Next session
1. Session open protocol → THE LOOP at **bb_call.cpp** (TOTAL=312; FIX-3/FIX-7d territory). FIX-3-i (write-family de-walk) is the unblocked entry; the dval==2/3 mass needs the Lon pin (FIX-3-iii). If the whole file proves split-gated, [S]-note + advance per law 5.
2. The CV10 IR_BUILTIN op_parts prep now serves the WHOLE resolve family — bb_is_cmp (eb=34), bb_io, bb_term_inspect, bb_term_io can consume it at their stops with the bb_atom_string recipe.

## Outstanding Lon verdicts (unchanged)
x86_movimm uint32-trunc (bb_call_fn) · prove rc=0-on-FAIL · PL-GZ-8 arith-is 2≠5 · m2 disj-backtrack · IRD-2b ratify · ml false-positive · counter-scope trio (lv/rp/nw) · bb_arith+bb_atom dead-dispatch retirement · ceiling-ratify (now 2249) · c3b1dbb icon alternation regression (owner ICON-NL) · two-chunk template design · prove_lower harness-list pre-fix for remaining NL flips (lower_prolog/raku/snobol4 lines).

SCRIP @ dc72af7 · .github @ the commit carrying this file. Both local==origin at close.
