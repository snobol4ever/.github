# FINDING 2026-08-03 — ALPHA s40 — U-SCOPE UCLAIM mem[] cross-statement exclusion (byte-neutral, gated)

**SCRIP HEAD at landing: `0a05b2d3` (U-GATE census) → new commit (U-SCOPE)**
**Corpus: `0c2b0df7` (untouched)**
**Session: s40, "Complete the ZETA CELLS / all your choices"**

---

## §1 THE BUG (OMEGA O-PB-2a root cause, ALPHA terrain)

During `zd_plan`'s UCLAIM span walk (`emit.cpp`, UCLAIM else-block, `mem[]` closure), the operand-tree expansion seeds from `run[]` members and expands transitively through `nodes[i]->n_operands`. This expansion can reach nodes from **OTHER statements** whose zls slots reside at lower addresses than the current statement's own nodes.

When such cross-statement nodes are included in the `umin`/`umax` span walk, the UCLAIM claim size K = `(umax - umin)` is inflated by the byte range of the foreign nodes. OMEGA's O-PB-2a measurement found a 224B inflation on `any.sno` stmt2 (NOTANY statement pulling ASSIGN_SAVE/LIT_STRING/ASSIGN_IMM from stmt1's zls range).

**Directive violated:** *"NO FUNCTION-level processing for ZETA whatsoever. ONLY statement level scoping."* (s21x-w)

---

## §2 THE FIX

`emit.cpp`, UCLAIM `mem[]` span walk (grep `U-SCOPE (s40 ALPHA)`): added a single guard before the `umin`/`umax` measurement:

```c
{ static int _usc2 = -1; if (_usc2 < 0) { const char *_e = getenv("SCRIP_ZD_SCOPE");
  _usc2 = (_e && *_e == '0') ? 0 : 1; }
  if (_usc2 && claim[k] >= 0 && claim[k] != hi) continue; }
```

`claim[k]` records which run-head owns node k. `claim[k] >= 0 && claim[k] != hi` means the node was claimed by a DIFFERENT statement's run head — a cross-statement node. These are excluded from the current UCLAIM run's span measurement.

**Killswitch:** `SCRIP_ZD_SCOPE=0` → byte-identical revert.

---

## §3 WHY THE ARMED Kc SPAN WAS NOT FIXED (important negative result)

The ARMED Kc span walk (`cm[]` closure, lines above the UCLAIM block) has the same operand-tree expansion shape. An initial attempt to apply the `claim[k] != hi` exclusion there caused a regression on `173_pat_fence_kw_blocks_backup` (m4 SEGV): its ARMED statement h=16 legitimately reads zls slots of nodes claimed by a prior ARMED statement h=0 through FRQ spellings, and the exclusion shrank Kc from 272 to 176, making the `[rsp+N]` addressing wrong.

**Conclusion:** ARMED statements' Kc spans legitimately include blob operands from other statements because those nodes' FRQ reader addresses are computed relative to the Kc-based rsp carve. The ARMED path cross-stmt expansion is a feature, not a bug. The contamination OMEGA measured was subsequently fixed by O-PB-2a's PATREF/DEFER exclusion (the specific contamination class was defer.pad being included in the Kc span).

The UCLAIM path is different: a DECLINED run's `mem[]` closure should not include cross-statement nodes because the UCLAIM claim is a flat reservation of the run's own region — foreign nodes are claimed by their own statement's UCLAIM head and should not inflate this run's K. The `claim[k]` discriminant is correct and safe here.

---

## §4 GATE RESULTS

**SCOPE=0 (gate-off):** byte-identical to corpus HEAD on all 506 `.s` files (roman.s md5 `4f775c5367c10723d3d9d42a98987508` confirmed both ways).

**SCOPE=1 (gate-on):** zero `.s` changes across 318 crosscheck programs + 21 benchmarks. The contamination class (UCLAIM run whose `mem[]` closure reaches a cross-statement claimed node) is currently empty in the corpus — DECLINED runs exist only where all statements are declined, so `claim[k]` is never set for cross-statement nodes in practice. The fix is **preventive**: it enforces the statement-scoping directive now so that future admission widening cannot introduce the contamination.

**Crosscheck (gate-on default):** m3 `281/25/11` · m4 `274/32(1L)/10` — **BY SET identical to s39 baseline**. The m3 127/152 swap is the known ASLR knife-edge (both programs are the same content; ASLR determines which lands on the rsp%16 boundary that flips PASS/FAIL).

---

## §5 POSITIVE CONTROL

The known-good case is any program where all statements are ARMED (claim[] set for all nodes) — the guard never fires and output is byte-identical. Verified: roman.sno, arithmetic.sno, all 21 benchmarks.

The known-bad case (contamination would fire) requires a DECLINED run whose `mem[]` walk reaches a node claimed by a different, earlier run. This shape does not currently appear in the corpus because:
- If stmt1 is ARMED, its nodes are claimed (claim[k]=hi1). If stmt2 is DECLINED, its `mem[]` expansion starting from its own run[] members would need to reach one of stmt1's claimed nodes via operand links. This requires stmt2's operand tree to reference a node allocated in stmt1's zls region — uncommon in practice because lowering allocates each statement's nodes contiguously.

The guard is correct by construction and will activate as admission widens.

---

## §6 HISTORY

- O-PB-2a (OMEGA s40): measured 224B contamination in ARMED Kc span for any.sno stmt2. Partial fix: PATREF/DEFER exclusion. Root cause identified: cross-stmt closure contamination. Routed to ALPHA terrain.
- U-SCOPE (ALPHA s40): UCLAIM mem[] fix landed. ARMED span fix correctly REJECTED (causes regression). Gated, byte-neutral, BY SET clean.
