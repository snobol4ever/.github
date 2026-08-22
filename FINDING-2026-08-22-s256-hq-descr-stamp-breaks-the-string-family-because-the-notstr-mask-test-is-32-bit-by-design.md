# FINDING — s256 HQ: DESCR stamping is NOT complete — turning it on breaks the string family, because `DT_NOTSTR_MASK` tests are 32-bit **by documented design** and the stamp writes into exactly those bits

**Date:** 2026-08-22 · **Seat:** HQ (`/home/claude`, Claude Opus 5, s256) · **Topic:** `descr-stamp-fields` · **Status:** ROOT-CAUSED AND REPRODUCED at HEAD `261cafcb`, pristine build EXIT=0, RT_OPT=`-O0`. **NOT CURED** — HQ designs, seats cure. Also **retracts** seat4's reported regression as non-reproducing.

## 1. Where DESCR stamping actually stands

Landed: the *structure*, not the feature.

| commit | what |
|---|---|
| `62017f8a` | split `DESCR_t` tag into `v`/`mod_op`/`src_node`/`slen`, pin `sizeof==16` |
| `9e6d3de2` | missing `kind_names[IR_GALT]` entry |
| `0f17fbf4` | convert **171** asm+template `DT_x` tag compares to 8-bit |
| `49df58fb` | stamp scalar-literal mints, killswitch `SCRIP_DESCR_STAMP` — **default OFF** |

⇒ **The stamp is inert in every default build.** The row is *not* complete: what shipped is the field split plus a switch that, when thrown, is wrong.

## 2. seat4's reported regression does NOT reproduce — retracted

seat4 reported (inbox, `regression-descr-stamp-fields-eq-coercion`) that `corpus/crosscheck/functions/060_pred_operand_edge.sno` — `EQ('2.0', 2)`, output line `d` — began failing at the `62017f8a`+`9e6d3de2` pair, PASS at `0ff71be8`, in both modes.

**Measured at HEAD `261cafcb` after `make pristine` (EXIT=0):**

```
m3 (--run)      -> M3 MATCH   (rc=0, byte-identical to .ref)
m4 (--compile)  -> M4 MATCH   (assembled + linked against out/libscrip_rt.so)
```

Line `d` is present in both. seat4's bisection was sound in method but its endpoint no longer holds — most likely fixed by the later `0f17fbf4` 8-bit compare conversion, which is precisely the class its failure belonged to. **No seat should inherit this as an open regression.** (seat4 found it while re-verifying gates on an unrelated row and correctly flagged rather than chased it; the flag was right.)

## 3. The real defect, reproduced and mechanised

Same witness, same build, killswitch thrown:

```
SCRIP_DESCR_STAMP=1 ./scrip 060_pred_operand_edge.sno
  -> rc=0, but TWO LINES MISSING vs .ref:
       'f'  from  OUTPUT = LGT('b', 'a') 'f'
       'l'  from  OUTPUT = LEQ(X, '2') 'l'
```

Both are **string-family lexical predicates**. Default arm loses nothing; stamped arm loses exactly these.

**Mechanism — a direct contradiction between two live designs:**

`src/templates/bb_lit_scalar.cpp:17` packs the stamp into the tag word:
```c
return base_tag | (mod_op << 8) | (src_node << 16);
```
so `mod_op` occupies bits 8-15 and `src_node` bits 16-31 — the upper 24 bits of the word whose low byte is `v`.

But the string-family test is **32-bit on purpose**, and three sites say so:
- `src/runtime/rtx/rtx_match.S:946` — `test edi, DT_NOTSTR_MASK` · *"string family (DT_SNUL|DT_S) in ONE 32-bit mask test"*
- `src/runtime/rtx/rtx_arith.S:78` — `test r10d, DT_NOTSTR_MASK`
- `src/runtime/rtx/rtx_abi.inc:63` — *"⛔ STRING tests are 32-BIT ONLY (test eax, DT_NOTSTR_MASK) — see descr.h."*

`DT_NOTSTR_MASK` is `0xFFFFFFFD`, and `descr.h:41` asserts the invariant the trick rests on:
```c
DESCR_SASSERT(((DT_SNUL | DT_S) & DT_NOTSTR_MASK) == 0, "SNUL|S must vanish under the string mask");
```
**A string vanishes under that mask only while the upper 24 bits are zero. The stamp writes into exactly those bits.** A stamped string therefore tests as NOT-a-string, the lexical compare takes the wrong path, and `LGT`/`LEQ` fail where they must succeed.

⭐ **So `0f17fbf4`'s "convert all 171 tag compares to 8-bit" was not incomplete by oversight — the `DT_NOTSTR_MASK` sites were left 32-bit deliberately, under a rule written down in `rtx_abi.inc`.** The stamp design and the string-test design were each internally consistent and mutually incompatible. That is why the sweep looked finished and the feature still breaks.

## 4. The cure, and the guard that should have caught it

1. **Narrow the three string tests to 8 bits** — `test <r8b>, (DT_NOTSTR_MASK & 0xFF)` i.e. `0xFD`, or `movzx` the tag byte first. All three sites, plus `rtx_abi.inc:63`'s rule text, in one commit (NO-PER-OP-FILTER: one class, one cure).
2. ⛔ **Tighten the static assert so the contradiction cannot return.** `descr.h:41` currently proves the invariant against a 32-bit mask and passes happily while the stamp violates it at runtime — it constrains the *constants*, never the *stamped word*. Re-express it over the 8-bit tag (`DT_NOTSTR_MASK & 0xFF`), so a future widening of the stamp fails the build instead of the corpus.
3. **Then re-run with `SCRIP_DESCR_STAMP=1` as a second corpus arm** — the stamp being default-OFF is exactly why this sat green. A killswitch nothing exercises is an untested branch.

⛔ **Not established, and the curing seat owns it:** whether the same 32-bit read reaches `DT_NUMERIC_BIT`/`DT_REAL_BIT` paths (those masks are 1-byte values, so probably safe) and whether any `.S` site loads the tag with a 32-bit `mov` that must also narrow. `LNE(X,'q')` still answered correctly with the stamp on — so the misroute does not corrupt every L\* member equally, and the per-predicate behaviour needs enumerating rather than assuming.

## 5. Scope note

Only **scalar literal mints** are stamped today (`bb_lit_scalar.cpp`). Lon's directive is broader — *"stamp DESCR with the node id that created it, and the node id that last modified it"* — so every future stamp site inherits this hazard until fix (2) lands. Fix the mask contract **before** widening the stamp.

**Routed:** this FINDING · queue row `descr-stamp-notstr-mask-8bit` (new) · `descr-stamp-fields` reopened as NOT-complete with the killswitch state named · `ARCH-SNOBOL4-RTX.md` §9 (stamp design) gets the mask-contract caveat · retraction of seat4's `regression-descr-stamp-fields-eq-coercion` recorded here and replied to seat4.
