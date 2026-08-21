# FINDING s192 — THE FENCED ARM'S CARRIER SCAN PUBLISHED ELEMENT 0, AND A BLOB IS ENTERED FROM THE RIGHT

**2026-08-20 · seat2 `/home/claude2` · Claude Opus 5 · queue row `rty-fence-arbno-stored` (rank 1) · SCRIP `56842aab` (rebased onto `84966023`) · corpus `2d4e0ed6`**

## THE ONE-LINE DEFECT, AND ITS ONE-LINE ASM DIFF

`s182 FENCE-RESUME` narrowed `s121`'s wholesale fence refusal to a rule: *publish the blob's resume carrier only when **the first real body node** is a tier-1 generator*. The rule looked at the wrong node. `sno_seq_nary` allocates its elements **LEFT TO RIGHT** — S sentinel, element 0, element 1, … — so "the first real body node" **is element 0**. A `PAT$` blob is entered at β **from the RIGHT**; its resume surface is its **rightmost** element's carrier. `sno_seq_nary` already computes exactly that and its own doc already forbids the mistake: *"a righter construct's exhaust must resume the run's rightmost generator, **not element 0**"* (`out_rtail`).

The row's witness, `probe/retry/rty_fence_arbno_stored`:

```
expr = LEN(1) ARBNO(FENCE('+') LEN(1))          '1+2+3' POS(0) expr RPOS(0)      oracle: match, SCRIP: nomatch
```

`SCRIP_RESUME_WHY=1` named it on the first run, no gdb, no board:

```
[RESUME-NIL] pat=PAT$0 pfenced=1 rn=0 brt=0 fb=IR_MATCH_LEN fbtier=2 chain=IR_GOTO|IR_MATCH_LEN|IR_MATCH_ARBNO|IR_MATCH_LEN
```

`fb` is the **leading** `LEN(1)`, tier 2 — refused — while the ARBNO one slot to its right is tier 1 and is the surface. Emitted: `PAT$0_β: jmp PAT$0_ω` (concede wholesale) where the fence-free twin emits `jmp n1_match_arbno_β` (extend). **The cure's entire asm diff, on the crashing witness and on every mover, is that one `jmp`.**

## THE CURE — BYTE-IDENTICAL BY CONSTRUCTION, NOT BY MEASUREMENT

Two edits in `src/lower/lower_snobol4.c`, killswitch `SCRIP_FENCE_RTAIL=0`:

1. `sno_pat_carrier_build` captures `out_rtail` for a fenced top **when no TOP-LEVEL element is a fence** (`topf`). That test is verbatim the TT_SEQ arm's own `first_fence == ne` — the exact condition under which `sno_pat_node` routes to `sno_seq_nary` **anyway**, with the same flatten and the same args. Taking the call one level up to capture the pointer therefore moves **zero bytes**; a top-level fence keeps the FENCE-PASS-THROUGH splitter untouched.
2. `sno_pat_publish_body_root`'s fenced arm prefers that carrier and falls back to the s182 first-allocated scan only when there is none. **The tier gate is unchanged** — tier 1 or 3 only, `FENCE1` is tier 0 and still refused — so the s182 narrowing and the cut semantics are untouched.

⭐ **THE GENERALISABLE MOVE: a diversion that already exists is cheaper than a new road.** The fenced arm was not missing a mechanism; it was declining to *keep the return value* of the mechanism it already ran. Framing the guard as "would the other road do this anyway?" is what makes the change provably inert instead of measurably inert.

## MEASURED (RT_OPT `-O0`; arm A = `SCRIP_FENCE_RTAIL=0`, arm B = default; every number re-proved after the rebase)

**Compile-time md5 blast radius, 1378 SNOBOL4 programs** (⛔ `programs/lon` excluded **by construction** in the sweep, per RULES): **11 movers**, every one behaviour-verified in **both** modes.

| movers | verdict |
|---|---|
| `probe/retry/rty_fence_arbno_{stored,stored_1iter,defer}` | **RED → GREEN both modes** (the row's named reds) |
| `probe/fuzz/fz_diff_22` · `probe/fuzz/fzr_22_nested_arbno_not_first` | **RED → GREEN both modes** (unasked-for, found by the sweep) |
| `probe/fuzz/fz_hang_06` · `probe/fuzz/fz_min_arbno_fence_seal` · `demo/calculator-1` | bytes moved, output **identical**, still PASS |
| `145_pat_left_assoc_via_arbno_fence` · `fz_hang_16` · `parser/unary_not` | bytes moved, output **identical**, still red exactly as before |

**Boards** — broad corpus **m3 334/3 · m4 327/9 · SKIP 1 (337)**, fail-set **identical between arms**; `crosscheck/patterns` 2-mode board **byte-identical between arms** (116 AGREE / 122 — the s121 7-mover fence class 114/119/129/130/148/149/150 intact); `probe/passthru` **identical between arms** (m3 170/182 · m4 156/182). **Gates green:** `emit_no_lang` · `template_medium_invisible` · `icn_no_stack` · `icn_one_reg_frame`. RULES step-4 regen run ×6.

## ⛔ ONE SHAPE TRADES A WRONG ANSWER FOR A CRASH. IT IS NOT IN THE CORPUS. IT IS REPORTED, NOT HIDDEN.

```
num = SPAN('0123456789')   expr = num . FIRST ARBNO(FENCE('+') num . LAST)   '1+2+3' POS(0) expr RPOS(0)
       with the cure:  m3 rc=139 (SIGSEGV) · m4 'fail'   ⛔ ALSO A MODE DIVERGENCE
       without it:     'fail' both modes
```

Checked in RED under law 0d as `probe/retry/rty_fence_capdefer_both_segv` **with both of its green one-sided controls beside it**. **THE ABLATION IS THE FINDING** — capture+defer on ONE side is fine; it takes capture+defer on **BOTH** element 0 and the ARBNO body:

| element 0 | ARBNO body right of FENCE | result |
|---|---|---|
| `num . FIRST` (cap+defer) | `num` (defer) | **green** (`rty_fence_capdefer_left_ctl`) |
| `num . FIRST` (cap+defer) | `LEN(1) . LAST` (cap) | green |
| `LEN(1) . FIRST` (cap) | `num . LAST` (cap+defer) | **green, and itself a cure** (`rty_fence_capdefer_right_ctl`) |
| `num` (defer) | `num . LAST` (cap+defer) | green |
| `LEN(1)` (plain) | `num . LAST` (cap+defer) | red 'fail', **no crash** (`rty_fence_capdefer_plainleft`) |
| `num . FIRST` (cap+defer) | `num . LAST` (cap+defer) | **SIGSEGV** (`rty_fence_capdefer_both_segv`) |

**The mechanism is PRE-EXISTING and the lowerer already documents it as violated.** A `FENCE1` inside an ARBNO body stores and restores rsp through a **static-depth** slot — `n7_match_fence1_α: mov [rsp+224], rsp` / `n7_match_fence1_β: mov rsp, [rsp+224]` — and `lower_snobol4.c`'s own TT_SEQ fence arm says why that is unsound there: *"the pass-through seam repoint rests on a static-depth rsp premise that ARBNO violates (rsp moves per iteration, Tier D)"*, which is exactly why `FENCE1`-inside-ARBNO sets `right_sealed = 1`. Publishing the ARBNO carrier makes that slot **reachable** at a foreign depth. ⛔ **Per FACT RULE NO-PER-OP-FILTER the class is left VISIBLY RED rather than hidden behind an invented conjunct**: the distinguishing ingredient is a *depth* accident (cap+defer on both sides), not a box family, and a filter shaped to it would be a lie about what the engine can do.

## ⛔ 145 IS NOT CURED, AND THE ROW'S OWN DONE-WHEN ASKED FOR IT — THE HONEST ACCOUNTING

`145_pat_left_assoc_via_arbno_fence` **moved bytes and did not move its answer.** The residual was measured **before** the cure was written, with the diagnostic that exists for exactly this question: under `SCRIP_FENCE_IGNORE=1` (unsound by construction, a MEASUREMENT never a fix) the three `rty_fence_arbno_*` reds all go green **and 145 still prints `fail`** — so the fence refusal never owned all of 145.

Its minimal spelling is checked in as `probe/retry/rty_fence_capdefer_plainleft`, and the important part is what it is **not**: the carrier **IS** published there — `body_root_op=57 tier=1 f1r=0`, character-for-character the reading of the **green** `rty_fence_capdefer_right_ctl` beside it — and it still answers `fail`. **Whatever still fails 145 is downstream of carrier selection**, in what the blob's β does after it lands a correctly published ARBNO β. That is the next row and it now has a two-line witness instead of a 7-line corpus program.

## ⭐ TWO THINGS THE TREE SAID THAT MEASUREMENT CORRECTED

1. **"Allocation runs RIGHT-TO-LEFT, so the first real body node is the RIGHTMOST element"** — the s183 diagnostic's own comment, written from beauty's blobs where `fb` read `IR_MATCH_ALTERNATE`. Measured here it runs **LEFT to RIGHT**: `chain=IR_GOTO|IR_MATCH_LEN|IR_MATCH_ARBNO|…` on `LEN(1) ARBNO(…)`, sentinel then element 0 then element 1. Both observations are real; the comment generalised a direction from one witness, and the generalisation is what made "first-allocated" look equivalent to "rightmost". **A scan whose correctness depends on allocation order should name the order it needs, not the order it saw once.**
2. **RULES step 4 does not name `util_regen_crosscheck_s_artifacts.sh`.** Running it regenerated **15** `.s`, of which exactly **1** (145) is this session's — attributed file-by-file by recompiling each under the killswitch arm. **The other 14 are pre-existing drift**, i.e. `crosscheck/` is carrying the same class s169's regen-catchup found in the `programs`/`prolog_bench` trees, for the same reason: the step that mandates the regen does not list the script. The step is amended in RULES.md by this rung.

## ⛔ CO-TENANCY, PER HQ'S s189 WARNING

A `ps` check before the first board found **seat1 running a 6-job scorecard on this box**. Nothing here is timing-graded — the two boards are output-comparison with 10s/15s per-program budgets and both arms ran under the same conditions — but it is recorded because HQ's warning says a silent co-tenant is how a headline number rots.

## NEXT

1. **`rty_fence_capdefer_plainleft` — the residual, and 145's real blocker.** Carrier published, answer still wrong: the hunt is in the blob β → ARBNO β extend path, not in selection.
2. **`rty_fence_capdefer_both_segv` — the static-depth `FENCE1`-in-ARBNO rsp slot.** A latent the lowerer documents and the tree now reaches. It is also a **mode divergence** (m3 139 / m4 'fail'), so it is a `GOAL-MODE34-IDENTICAL` row as much as a fence row.
3. `fz_hang_16` remains rc=124 both arms, untouched by this rung.
