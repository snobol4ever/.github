# FINDING s184 — s126 COUNTED CHOICE NODES, AND SWEPT **SIBLING** ALTERNATIONS IN WITH **NESTED** ONES

**Seat:** seat4 (Opus 5), 2026-08-20, queue row `arbno-alt-fence-L1`. **Tree:** SCRIP `cecb7d11`, corpus `5d72325f`, **pristine at RT_OPT=-O0** before every verdict.
**Brief:** `ARBNO((LEN(1)|LEN(2)) FENCE(LEN(1)|''))` → oracle match, SCRIP nomatch. Ablate the body to find which of {ALT-before-FENCE, FENCE, ALT-inside-FENCE} is load-bearing.

## ⭐ THE HEADLINE — THE FENCE IS NOT LOAD-BEARING; **TWO SIBLING ALTERNATIONS** ARE
Ablating the body answered the brief's question immediately and in the negative: **dropping the FENCE does not cure it** (`ARBNO((LEN(1)|LEN(2)) (LEN(1)|''))` is red too), and neither the empty arm nor the FENCE nor the arm count matters. What matters is that **both** body elements are alternations:

| body | verdict |
|---|---|
| `ARBNO((LEN(1)\|LEN(2)) (LEN(1)\|LEN(2)))` | **RED** |
| `ARBNO((LEN(1)\|LEN(2)) LEN(1))` | GREEN |
| `ARBNO(LEN(1) (LEN(1)\|LEN(2)))` | GREEN |
| `(LEN(1)\|LEN(2)) (LEN(1)\|LEN(2))` — **the same body with no ARBNO** | GREEN |

The bare sequence backtracks correctly; **wrapping it in ARBNO is what loses the retry.**

## ⭐⭐ THE SYMPTOM IN ONE PROGRAM — EVEN LENGTHS ONLY
`ptw_min_arbno_altsib_ladder` matches the same ARBNO against every prefix of `'abcdefgh'`:
```
n:      1        2      3        4      5        6      7        8
oracle: NOMATCH  match  match    match  match    match  match    match
SCRIP:  NOMATCH  match  NOMATCH  match  NOMATCH  match  NOMATCH  match
```
Per-iteration widths are {2,3,3,4}; **every even total is reachable with all-first-arms iterations (1+1) and every odd total needs exactly one iteration to take a non-first arm.** So the generator was exploring **only the all-first-arms path** — not "a backtracking bug" in general, but *no arm variation at all inside the ARBNO*.

## THE ASM DIFF NAMED IT (ASM-DIFF-FIRST; gdb never needed)
`n0_match_arbno_af` — the ARBNO's exhaustion port — one line apart between the green and red arms:
```
GREEN  ARBNO(ALT LEN(1)):  cmp r14d, eax;   jne  n2_match_len_β        ← retreat into the body
GREEN  ARBNO(LEN(1) ALT):  cmp r14d, eax;   jne  n2_match_alternate_β
RED    ARBNO(ALT ALT):     cmp r14d, eax;   jmp  PAT$0_ω               ← EDGE ABSENT
```
In the red arm the `cmp` sets flags **nothing reads** and the box concedes wholesale. `SCRIP_RESUME_WHY=1` reports the *same* `body_root_op=57 tier=1 in_nodes=1` for all three, so the carrier publication was never the problem — the **retreat edge emission** was.

## THE SITE, AND WHY IT WAS WRITTEN THAT WAY
`bb_match_arbno.cpp:149` emits the edge under `IF(!sn4_defer_resume() || !_.op_arbno_body_actframe, …)`, and `emit.cpp:1192` computes:
```c
op_arbno_body_actframe = (((_alt==1 && _dfr==0 && _arb==0) || …) && !_ref && !_fseal) ? 0 : 1;
```
**`_alt` is a COUNT, and the edge is admitted for EXACTLY ONE choice node.** s126's own in-code comment says why, and its conviction is real:
> *"Witness pair nf3/nf4: `ARBNO(FENCE('a'|'ab')|'c')` … the FENCE BLOCKS THE FLATTEN leaving two **NESTED** ALTERNATEs, and the admitted edge then LIVELOCKS (af→outer-ALT-beta→…→af, rc=124)."*
That is **a nested pair**. Sibling alternations were swept up with them, and the IR says the two shapes are not the same thing at all — `MATCH_ALTERNATE`'s operands are its arm delimiters:
```
SIBLING  ARBNO [3,3,6] · ALTERNATE 3 arms [7,7,8,8] · ALTERNATE 4 arms [5,5,6,6]   ← disjoint
NESTED   ARBNO [32,32,36] · ALTERNATE 32 arms [33,33,36,36]                        ← 33 IS an ALTERNATE
```
Two disjoint 32-byte records laid contiguously on one spine is **exactly the composition s125 relied on**.

## THE CURE — ARBNO-ALTSIB (`SCRIP_ARBNO_ALTSIB=0` restores the s126 count)
Admit `_alt >= 1` **when no span choice node appears inside another choice node's arm operands.** The nesting test is **structural** — containment of one choice node in another's arms — never an op-name blacklist and never a per-op filter; it asks directly the question the count was standing in for. **Zero new globals** (a function-local `static` killswitch, the `sn4_arbno_tailbeta` construction).
⛔ **The unguarded relaxation was tried first and MEASURED WRONG:** `_alt>=1` alone cures the ladder *and* reproduces s126's nf3 livelock at **rc=124** verbatim. The nesting guard is not a precaution, it is the difference between the two shapes.

## RECEIPTS (pristine, RT_OPT=-O0; every A/B is the killswitch)
- **CURED oracle-identical BOTH modes:** `ptw_min_arbno_altsib_3` · `_5` · `_ladder` · `_nonempty`. Controls `_fst_ctl` / `_snd_ctl` green in **both** arms.
- ⭐ **s126's CONVICTION PRESERVED:** nf1/nf2/nf3/nf4 all PASS; nf3 is rc=0 `nomatch`, not rc=124.
- **CORPUS m3 332/5 · m4 325/11 — FAIL-SET BYTE-IDENTICAL** across the A/B.
- **BLAST RADIUS ZERO:** 1282 mode-4 `.s` md5s swept in both arms; the only differing row is the known self-differing `unary_not.sno`. **No existing corpus program carries the shape** — which is why it survived this long. All five RULES step-4 regens report `No changes`.
- **PASSTHRU BOARD m3 136 → 140, m4 123 → 127**, red-set diff **removals only**, zero new reds.

## ⛔ NOT CURED — THE ROW'S OWN WITNESS, AND EXACTLY WHY
`ptw_min_arbno_alt_fence_L1` keeps its FENCE and is **still red in both modes and both arms**. A FENCE'd alternation is `seal`ed, which sets `_ref=1` and **vetoes the edge outright** — even though its UNSEALED sibling `(LEN(1)|LEN(2))` is a perfectly good carrier that the manual requires be retried (FENCE makes the alternatives *inside P* invisible on backup, p.125/p.204; it says nothing about a sibling to its left). Compounding it, `sn4_arbno_tailbeta()` aims the edge at the span **TAIL**'s β — which here *is* the fenced ALT.
**The next rung, stated precisely:** a sealed choice node must not be re-entered *itself*, but it must not veto the edge when an unsealed sibling exists; the edge should then aim at the rightmost **unsealed** choice node rather than the tail. That is a retarget, not a relaxation, and it was deliberately not attempted here.

## NEXT
1. The sealed-sibling retarget above — it is the row's own witness and it is one rung.
2. `ARBNO(LEN(1) FENCE(LEN(1)))` **hangs at rc=124** where the oracle answers `nomatch` (found while ablating; not this class, not filed as a witness yet).
3. Nested alternations remain refused, as s126 ruled — `ptw_min_arbno_altsib_*` guards the sibling half so a future nested rung cannot silently take it back.
