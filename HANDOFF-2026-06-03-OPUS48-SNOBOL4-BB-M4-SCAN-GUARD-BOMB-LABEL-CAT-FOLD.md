# HANDOFF 2026-06-03 (Opus 4.8) — SNOBOL4 m4 scan: compound-pattern SILENT-WRONG fixed (single-lit guard); x86_bomb TEXT label repaired (all-language latent); constant-CAT fold lands m4-green

## Summary

Probing past the smoke (which exercises only single-literal scans) found that **mode-4 silently mishandled
compound patterns** — a direct violation of "a missing box falls LOUD, never silent." Three layered, gated
fixes landed (SCRIP `9e8e4b8`, 2 files, +37/−1): the misclassification guard, a repair of the (latent,
all-language) `x86_bomb` TEXT-label bug the guard surfaced, and a constant-literal-CAT fold that makes pure
literal concatenation patterns m4-green. **All HARD gates hold; m2/m3 byte-paths untouched; prove_lower2
topology untouched (67/67).**

## Bug 1 — compound patterns were SILENT-WRONG in m4 (fixed: single-lit guard)

`flat_drive_scan_stmt` (emit_bb.c) set `op_scan_pat_lit` whenever `pg->entry->t == IR_PAT_LIT`. But for
CAT/ALT the pattern graph's **entry IS the first child literal** (probe ground truth below), so a compound
pattern was mis-fed to the literal-only `rt_scan_lit` and matched ONLY its first element:

```
S = 'xabz' ; S 'a' 'b' = 'Q'      m4 gave xQbz   (matched only 'a'; correct xQz)
S = 'abc'  ; S ('q'|'b') = 'Q'    m4 gave abc    (2nd-alternative backtrack lost; correct aQc)
S = 'abc'  ; S ('a'|'b') = 'Q'    m4 gave Qbc    (accidentally right — 1st alt matched)
```

m2 and m3 were NEVER affected: m2 is the `IR_interp` IR_SCAN handler; the BINARY (m3) arm of
`bb_scan_stmt.cpp` always drives the FULL graph via `rt_scan` regardless of `op_scan_pat_lit`. The bug was
strictly the m4 TEXT fast-path classification.

**FIX:** `scan_pat_is_single_lit(pg)` — a pattern qualifies for `rt_scan_lit` iff its graph contains ONLY
the two sentinels (`IR_SUCCEED`, `IR_FAIL`) plus EXACTLY ONE `IR_PAT_LIT`. Anything else (CAT/ALT/captures/
operand matchers) leaves `op_scan_pat_lit` NULL → the TEXT arm bombs.

### Probe ground truth (recreate with a 5-line stderr dump in flat_drive_scan_stmt)

```
'b'           entry=LIT  n=3  [SUCCEED, FAIL, LIT(b)]
'x' (goto_s)  entry=LIT  n=3  [SUCCEED, FAIL, LIT(x)]            ← genuine single literal, stays fast-path
'a' 'b'       entry=LIT  n=5  [SUCCEED, FAIL, CAT, LIT(b), LIT(a)]
('q'|'b')     entry=LIT  n=5  [SUCCEED, FAIL, ALT, LIT(b), LIT(q)]
γ-chain from entry:  'a' 'b'      → LIT(a)→LIT(b)→CAT→SUCCEED     (left-to-right!)
                     'a' 'b' 'c'  → LIT(a)→LIT(b)→LIT(c)→CAT→SUCCEED
                     ('q'|'b')    → LIT(q)→ALT→SUCCEED            (not a clean literal chain)
```

Enum values for probes: `IR_LIT_S=1  IR_SCAN=28  IR_PAT_LIT=32  IR_PAT_CAT=38  IR_PAT_ALT=39  IR_FAIL=11
IR_SUCCEED=12`.

## Bug 2 (surfaced latent, ALL languages) — every m4-TEXT `x86_bomb` was unassemblable (fixed)

Routing CAT/ALT to the bomb exposed: the TEXT arm emitted `lea rdi, [rip + ??]` → `as` error
"invalid character '?'". Root cause: `emit_intern_str` **always returns NULL** — its backing callback
`g_flat_intern_str` (`lower_flat_set_intern_str`, emit_bb.c:209) is defined but **wired NOWHERE in the
repo**. The scan template's own RO strings only ever resolved via `scan_lbl`'s `strtab_label` FALLBACK;
`x86_bomb` had no fallback. So no box in any language could ever bomb correctly in the m4 TEXT medium —
it simply had never been reached there before.

**FIX (`x86_asm.h`, +2, TEXT-only):** when `emit_intern_str` yields nothing, fall back to
`strtab_label` (which `strtab_intern`s the message; `xa_emit_strtab_rodata` emits it at end-of-emit).
**Byte-neutral to BINARY/mode-3** — `x86_load_ro`'s BINARY arm uses the raw `ptr` and ignores `label`
entirely, and the fallback is gated `!MEDIUM_BINARY`. A bombed m4 binary now assembles, links, and at
runtime prints `libscrip_rt: BOMB — <msg>` then `ud2` (rc=134) — the intended LOUD abort.

## Constant-CAT fold — pure literal concatenation is now m4-green (PB-RB-OPT subset)

A CAT of all-constant literals is semantically one literal (SPITBOL manual Appendix-C item 11, constant
sub-expressions pre-evaluated; the same principle as the `047dded` concat fold and a strict subset of this
goal's PB-RB-OPT invariant-pattern bake). `scan_pat_cat_concat(pg)`:

- QUALIFIES only when `all[]` = sentinels + ≥2 `IR_PAT_LIT` + ≥1 `IR_PAT_CAT` and NOTHING else
  (ALT / captures / SPAN / any operand matcher → NULL → bomb path).
- Concatenates `sval`s along the **γ-chain from entry** (probe-verified left-to-right order, incl. nested
  3-literal CAT) into a `GC_MALLOC_ATOMIC` buffer (emit_bb.c now includes `<gc/gc.h>`; both binaries
  already link `-lgc`). The buffer is sized and filled by the SAME γ-walk — no overflow window.
- Pre-verified `rt_scan_lit` handles multi-char literals (`S 'ab' = 'Q'` was already m4-green) before
  relying on the fold.

**Deliberately in the EMIT DRIVER, not the lowerer:** a lowerer fold would shrink the IR node count and
break `prove_lower2`'s `MATCH('a' 'b')` 4-node topology assertion (the PB-RB-4 prereq case). The emit-driver
fold leaves IR topology untouched (prove_lower2 67/67) and touches only the m4 TEXT fast-path.

## Verification matrix (all on final pushed tree)

```
                       m2     m3     m4(before)        m4(after)
lit    S 'b'='X'       aXc    aXc    aXc               aXc
goto_s 'x' 'x'         hit    hit    hit               hit
single S 'ab'='Q'      xQz    xQz    xQz               xQz
CAT    S 'a' 'b'='Q'   xQz    xQz    xQbz  ❌silent     xQz   ✅
CAT3   'a' 'b' 'c'     wQz    wQz    wrong ❌silent     wQz   ✅
ALT    ('q'|'b')='Q'   aQc    aQc    abc   ❌silent     LOUD bomb naming PB-RB ✅
```

## Still open (next session)

1. **m4 ALT + variable/captured CAT = PB-RB-4** (`STITCH_ALT` for genuine alternation; `STITCH_SEQ` for
   non-constant CAT). The bomb message now names it. Graph pointers are emitter-process addresses — NOT
   relocatable into a standalone binary — so `rt_scan` cannot be the m4 arm; the native byrd-box graph is
   the only path (as the goal file already says).
2. **⚠ Compound SUBJECT/REPLACEMENT beside a literal pattern (`S 'b' = (A B)`) — UNVERIFIED.** The
   subj/replace classification is still entry-only (`sg/rg->entry->t == IR_LIT_S`). A compound replacement
   leaves `op_scan_replace_lit` NULL while `is_repl=1`, so `rt_scan_lit` receives `repl=NULL` — behavior
   not audited; likely needs the same genuine-single-literal guard (or a bomb) on the subject/replacement
   graphs. Flagged, not fixed (out of this session's verified scope).
3. String-arg `slen` (pre-existing, unchanged — see prior handoffs).

## Build / verify recipe

```bash
cd /home/claude/SCRIP
bash scripts/build_scrip.sh && make libscrip_rt        # emit path lives in BOTH
bash scripts/test_smoke_snobol4.sh                     # m2 7/7 HARD; m3 6/6; m4 6/6
bash scripts/test_smoke_icon.sh                        # m2 12/12 HARD
bash scripts/prove_lower2.sh                           # 67 PASS / 0 FAIL
bash scripts/test_gate_no_bb_bin_t.sh ; bash scripts/test_gate_no_lang_names.sh   # 0 ; 13 (Δ0)
bash scripts/audit_concurrency_invariants.sh ; bash scripts/test_gate_sno_pat_reg.sh
cat > /tmp/cat.sno <<'EOF'
        S = 'xabz'
        S 'a' 'b' = 'Q'
        OUTPUT = S
EOF
echo END >> /tmp/cat.sno   # m2/m3/m4 must all print xQz; swap pattern to ('q'|'b') → m4 must LOUD-bomb
```

## Gate state (verified on rebased+pushed tree `9e8e4b8`)

SNOBOL4 m2 **7/7 HARD** · m3 **6/6** · m4 **6/6** · Icon m2 **12/12 HARD** (m3/m4 5/12 unchanged) ·
prove_lower2 **67/0** · no_bb_bin_t 0 · LI-FENCE **13 (Δ0)** · concurrency OK · REG-FENCE TIER1=0
(TIER2 r10=20 info, unchanged) · no-handencoded `--strict` 0 · unified-broker **32**.
Rebased over mid-handoff upstream `1d92abc` (Pascal PB-9 doc) + `873792f` (Prolog float-unify; its
`x86_asm.h` edits additive, zero conflict) — rebuilt + re-gated green after each.

## Watermark

SCRIP tip = **`9e8e4b8`** (pushed). `.github` tip = this commit. Detail: this file.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
