# FINDING — 2026-09-20 · hq_snobol4 · MODE TENET condition 1, CEO-1019, CEO-1024

**TREE OF EVERY NUMBER BELOW:** SCRIP `5418432bb` (plain `origin/main`, CFO-117 in, tree otherwise clean) · corpus `8486bb1e2` · `.github` this commit · `RT_OPT=-O0` · oracle `/home/resources/x64/bin/sbl -bf` reached by `sbl_correctness_bin()`, refs cut **live** in the same run. Box load 8–14 on 16 cores (ten seats): every number here is a **correctness** reading, not a timing.

## 1. ⭐⭐ THE SNOBOL4 SHARE OF THE UNMAPPED-SLOT POPULATION IS ALL OF IT — AND TWO OF THE OTHER ZEROS ARE NOT ZEROS

`util_gc_unmapped_store_census.py` over the 37-program shared witness set:

```
witnesses=37 graphs=202 shielded_stores=930 members=162 undecidable=294
BELOW-REGION=162  RAW-SLOT=0  GAP=0  ABOVE-REGION=0  OUTSIDE-LAYOUT=0  NO-MAP=0
LANG sno   witnesses=12 members=162 undecidable=42
LANG icn   witnesses=17 members=0   undecidable=10    <- ZERO OVER UNMEASURED SITES
LANG pl    witnesses=5  members=0   undecidable=242   <- ZERO OVER UNMEASURED SITES
LANG raku  witnesses=3  members=0   undecidable=0     <- the only clean zero
```

**SNOBOL4 owns 162 of 162 — one hundred percent of the DECIDED population.** ⛔ Stated that way deliberately: the census prints *ZERO MEMBERS HERE IS NOT A CLEAN READING* on icon's and prolog's lines itself, and prolog's **242** undecidable sites are a hole nobody can read in either direction. A census that names its own blindness is the only reason this sentence can be honest.

**THE 162 BY WITNESS — a census NAMES and never counts (CEO-997 batch 30 clause 2):**

| witness | members | | witness | members |
|---|---|---|---|---|
| `hb_dvec_sort_match.sno` | 46 | | `hb_nested_match_outer_subject.sno` | 12 |
| `hb_dvec_data_convert.sno` | 34 | | `hb_blob_span_defer.sno` | 12 |
| `hb_datblk.sno` | 24 | | `hb_eval_names.sno` | 10 |
| `hb_arr.sno` | 18 | | `hb_defer_subject.sno` | 8 |
| `hb_wsb_eval_define.sno` | 16 | | `hb_mkexpr_unmapped_spine_store.sno` | 6 |
| `hb_nv.sno` | 12 | | `hb_dtp.sno` | 6 |

The 42 undecidable split 22 `NO-ANCHOR-REACHES-SITE` + 20 `SPINE-DEPTH-UNKNOWN`. Every member is `BELOW-REGION`; **no snobol4 witness contributes a `RAW-SLOT`, a `GAP` or an `ABOVE-REGION` store**, which matters because `RAW-SLOT` is the only one of the five that is a *lie* to the collector rather than an omission.

**CLASS 2 (a graph with no frame map at all) IS ZERO FOR SNOBOL4, and the one entry that prints is not a collector hole.** `util_zls_frame_map_census.py --lang snobol4` on this tree: `entries=1982 graded=1981 no_layout=1 (declared=0 defect=1) graphs=4506 fields=174642 unkinded=0 holes=0`. The one is **`trim_alt_keyword_replace_branch_1`**, and it has no frame because **`lower_snobol4` refuses it** — *"lambda(expr), the CONDITIONAL pattern lambda, is not implemented yet"* — so it is a completeness gap wearing a GC census's clothes. It is already `XFAIL` at line 7 of `ALL.xfail`, inside the denominator. ⛔ **AND AN INSTRUMENT NUANCE THE NEXT READER NEEDS:** the census prints `NO-LAYOUT-SIDECAR lang=snobol4 -- no ALL.wantrc beside corpus/tests/snobol4`, so **the DECLARED split raku got at `621c08866` is unavailable to snobol4 by construction** and this entry is *counted a defect* although the master declares it. The number to quote is therefore **zero class-2 GC holes in snobol4, one declared-but-undeclarable lowering refusal**, never a bare `no_layout=1`.

## 2. THE BAND RE-WALKED ON THE `cfo`'s LANDED TREE — 340 ARMS, 6 RED, BYTE-IDENTICAL TO BASE

CFO-117 landed in **`pattern_match.c`**, which is a SNOBOL4 runtime file, so *"nothing I am landing moves your row"* was a sentence owed a measurement rather than a thank-you. Measured, twice, by two instruments:

| instrument | arms | red | red NAME SET |
|---|---|---|---|
| standalone walker, 17 points × 10 witnesses × 2 modes | 340 | **6** | `w` m3 {1,2,4,8} · `w` m4 {1,2}, all rc=0 |
| the new gate, `GC_BAND_FULL=1` | 340 | **6** | identical |
| the new gate, default band 0..8 + 16 + 25 | 200 | **6** | identical |

**Byte-identical to the base column published at `2facb6c60`.** All 334 base-green arms stay green; the eight siblings and the control `nodefer` are green at all 17 points in both modes. ⭐ The `cfo`'s no-move claim holds **on my instrument**, and their four-fingerprint reading of the master entry (`3b192bd3` the ref's own md5 at stress 0, `a84e1945` across 1..13 and 55, `ae252bdf` at their crash island, `ad07daca` after their cure) is independent evidence for this row's *"ragged per poll set"* title from a direction I did not have.

**DT_X IS STILL NOT IN `gc_cell_visit` on origin** — one occurrence in all of `gc_heap.c`, line 594, `gc_visit_one` only. The cure is CFO-138, taken by the `cfo` after CFO-117.

## 3. THE MASTER AT THE TINY ARENA — AND ⛔ WHY THAT READING IS **NOT** A CLEAN LANE

SnoM at `SCRIP_HEAP_MB=1` on `5418432bb`: **1963/1982 OUTSIDE=8 (graded 1974) both modes**, xfail 9, xpass 0. Red NAME SET **`dupl_size_replace_branch_1` `[fp=d41d8cd9 rc=1]`** + **`size_keyword_replace_branch_1` `[fp=effe1e03 rc=1]`**, both modes. Same names *and* fingerprints as the `coo`'s reading at `e20c8e1a2`, so nothing in CFO-117 moved the board. No SCORE row: declared through `S4E_SCORE_NO_WRITE` because the published cell is a default-arena board.

⭐ **`d41d8cd9` IS THE md5 OF THE EMPTY STRING** — `dupl_size_replace_branch_1` prints **nothing** and exits 1. It is an **error exit, not a wrong answer**, and therefore a different class from everything else on this board; the fingerprint belongs in its own row and is now there. (RULES.md clause 2 records this same fingerprint fooling two seats this week: it is byte-identical whichever cause produced it.)

⛔⛔ **AND THE WITHDRAWAL, BEFORE ANYONE BUILDS ON IT: THAT RUN CARRIED NO STRESS PLANT AT ALL.** `SCRIP_GC_STRESS` unset is stress **0** — no forced collection — which is the weakest arm there is, and it is *precisely* the hazard I had sent `hq_prolog` three hours earlier about their arena-default row. CEO-1024 (measured by `hq_raku`, who reversed their own green for it: raku master 853 → 817 m3 / 824 m4 at stress 16, **65 gradings lost over 36 distinct programs, every one exit 0 with a plausible wrong answer**) makes that explicit: *a band that ends where the known defects start measures the band and not the compiler.* **SnoM at `SCRIP_HEAP_MB=1 SCRIP_GC_STRESS=16` is the reading that decides this lane, and until it is in, snobol4 is NOT reported clean.**

## 4. ⛔⭐⭐ LON'S ROOTED-ALLOCATION SWEEP: ONE LIVE MEMBER IN SNOBOL4, AND THE SWEEP'S OWN CRITERION CANNOT SEE IT

Lon, in-chat to the `ceo` (CEO-1019): *"Go make sure that all language specific constructs at runtime have ROOTED GC allocations."*

**MEASURED, TWO LINES OF SNOBOL4, FIRST TRY.** Assign a literal to the `ERRTEXT` keyword, then OUTPUT it. Oracle `sbl -bf` prints `ABCDEFGH`. Ours at `SCRIP_HEAP_MB=1`, 15-point band, both modes:

```
stress   0  1  2  3  4  5  6  8 10 12 16 20 25 35 50
m3       .  X  .  .  .  X  .  .  .  .  .  .  .  .  .
m4       .  X  .  .  .  X  .  .  .  .  .  X  .  .   (25 is m4-only)
```
`X` = **six kilobytes of heap garbage**, rc=0, no diagnostic. Fingerprints stable across reps: m3 `31009eac` len 6384, m4 `6ab72e42` len 5392.

**MECHANISM, READ AT THE LINE:** `g_sno_errtext` (`keywords.c:34`) is a plain `const char *` global taken from **`rt_heap_strdup_c`** at four sites — `keywords.c:311` (`kwb_error`), `keywords.c:341` (the `&ERRTEXT` assignment), `runtime_eval.c:255` and `:489` (captured eval errors) — read at `keywords.c:289` through `STRVAL` when the keyword is read, and **named by no root walk and no visitor anywhere in the tree (zero hits)**. A SNOBOL4 keyword's value lives in the collected heap with no root.

⛔ **WHY THE SWEEP'S CANDIDATE LIST COULD NOT CONTAIN IT:** the criterion was *non-scalar **statics** under `src/runtime`*, and `g_sno_errtext` is **neither static nor non-scalar** — it fails the filter twice, in the **same file** as two candidates the list does name (`g_kwb`, `g_kwb_bound`, both clean). That is the `ceo`'s own *228 `static DESCR_t`* lesson in the mirror: last time the shape was too wide, this time too narrow, and **both print a plausible population.** Minted rank 0: `snobol4-errtext-keyword-value-is-an-unrooted-collected-heap-string-so-reading-it-after-a-collection-prints-heap-garbage`.

**THE NINE NAMED CANDIDATES, ONE LINE EACH, AS ASKED:**

| static | verdict |
|---|---|
| `g_dcap_nv_cell` `pattern_match.c:713` | **CLOSED BY CURE** — held one and lost it; CFO-117 generation-checks it against `g_nv_memo_gen` at **both** read sites |
| `g_lf_type` `pattern_match.c:24` | **OPEN, NARROW** — caches a `DATBLK_t *` and is **never dereferenced**, only compared, so a stale value costs one redundant `strcmp`; the **ABA is real** — if that block moves and another lands at the same address the equality holds and `rt_list_view` *skips the field-shape validation it exists to perform*. Not banded; labelled as reasoning |
| `g_dcap` `rt_runtime.c:24` | **CLOSED — DEAD.** One grep hit in the tree: its own declaration |
| `_vstack` `core/core.c:3573` | **CLOSED — DEAD.** One hit; the corpse of the removed Icon value stack (GROUND ZERO 3) |
| `g_nv_memo_val` `core/core.c:3070` | **CLOSED BY PROTOCOL** — `g_nv_memo_gen` + `rt_nv_memo_invalidate`, which `gc_heap.c` calls six lines after it slides the heap |
| `g_ctx_current` `core/name_save.c:15` | **CLOSED** — points at the static root ctx or at the address of a **C local** (`runtime_eval.c:559` is the only caller of `NAME_ctx_enter`), and `entries` is nulled on both enter and leave |
| `g_name_save` | **CLOSED — AND THE LIST HAS THE FILE WRONG:** it is `rt/rt.c:1226`, and it **is rooted** — `rt_gc_ws_roots` (`rt.c:1335`–`1343`) visits the array pointer, every name, every cell and every `old` descriptor |
| `g_kwb` `keywords.c:205` | **CLOSED** — a static initialised table, not a heap block |
| `g_kwb_bound` `keywords.c:240` | **CLOSED** — initialised to `g_kwb`, and `rt_kw_bind`, the only thing that could repoint it, **has no call sites** (declaration + definition only) |

⛔ **PLUS THE ONE THE LIST OMITS AND THE `cfo` NAMED AN HOUR EARLIER:** `g_sno_defer_cells[4096]` (`pattern_match.c:662`) holds the same class of heap address **as `uint64_t`**, invisible to any pointer-shaped criterion — including the sweep's, and including the `cfo`'s own `[GC-SPINE-LOST]`, which is *exact* on my witness and **blind to this by construction**. Named and unmeasured; its layout is `_Static_assert`ed against `rtx_match.s`, so it is not a one-liner.

⭐ **THE METHOD I TOOK FROM CEO-1021 BEFORE ANSWERING ANY OF THE NINE:** look for the **gate whose name asserts the invariant**, not only for a visitor in the source. That is how `g_name_save` came back rooted, and it is how `hq_pascal` refuted the `ceo`'s Pascal finding in one command. **The gate index is a better index of invariants than the source is.**

⛔ **AND A CORRECTION I OWE IN THE OPEN:** I told `hq_pascal` their heap table was the *third* member of this class. It is not — `pas_gc_roots` (`by_name_dispatch.c:776`) walks every cell and all 512 text-file buffers. **My class has two members, both in `pattern_match.c`.** I took another seat's *claim-notice topic string* as a reading because it agreed with a class I was already holding, which is worse than a bad grep: agreement feels like evidence. ⭐ Their distinction is better than my class and is recorded here in their words: **a stable root holding movable pointers is not a cache of bare addresses** — the Pascal table must not move because a Pascal pointer value is an integer handle *into* it, so rooting is right there and invalidation would destroy the handles; mine hold raw addresses with nothing stable in between, so invalidation is right for `g_dcap_nv_cell` and **a root walk, not an invalidation, is right for `g_sno_errtext`** (a value that must survive, not a cache). That distinction changed the cure I am going to write.

## 5. THE GATE — PROVEN RED, PROVEN REFUSING, AND DELIBERATELY NOT WIRED

`scripts/test_gate_gc_a_bare_deferred_expression_name_survives_every_collection_point.sh`, 200 arms in **2.9 s**: ten witnesses minted **inline**, refs cut **live from the oracle in the same run**, every arm an oracle diff, reds classified as **WITNESS / SIBLING / CONTROL** so a widening defect can never read as this one.

* **FAIL proven:** rc=1, 6 of 200, witness-only.
* **REFUSAL proven reachable, twice:** rc=2 on a missing `./scrip`, and rc=2 on an **empty oracle answer** (*"an empty expectation makes every arm pass"*), each exercised on a copy rather than asserted.
* **Declared `RULING` in `gate_wiring.tsv`, signed `hq_snobol4`**, with the one recipe line that wires it written in the gate header and the flip condition named: the sitting `DT_X` reaches origin. Wiring a knowingly-red arm into a 367-arm all-blocking serial set shared by ten seats (TENET condition 2) costs every one of them and buys nothing. `make preflight` **56 arms, 0 red** after the declaration.

⛔⭐ **WHY THE TEN WITNESSES ARE MINTED INLINE INSTEAD OF SHIPPED INTO `scripts/gc_witnesses/` — MEASURED BEFORE LANDING, NOT DISCOVERED AFTERWARDS BY THE SEAT IT WOULD HAVE CONVICTED.** `test_gate_gc_a_safe_point_stores_into_a_mapped_slot.sh` arm (e) is a ratchet pinned at `members=162 undecidable=42` whose **population is a directory glob** over `scripts/gc_witnesses`. I put the nine siblings there and censused them alone: **`members=30 undecidable=8`**. So the arm would have read `192/50` and printed ***"THE CLASS GREW … a new safe point stores outside its frame map"*** — when no safe point had moved and nine test files had arrived.

> **A RATCHET WHOSE POPULATION IS A DIRECTORY GLOB CANNOT DISTINGUISH A COMPILER REGRESSION FROM A COLLEAGUE'S TEST FILE, AND ITS FAILURE TEXT NAMES A CAUSE IT NEVER MEASURED.**

That is the gate's own header rule — *the floor is a NAME SET and never a count* — left unapplied one level down, at the **population** rather than at the floor. The cure offered to the `cto` (whose row owns it, so it is theirs to take): a **per-witness** census file, the shape `ORPHANED-WITNESSES.tsv` already has, where adding a witness adds a **line** and only a *change* to an existing line can red the arm. Their baseline is untouched and re-verified at `162/294` on this tree.

## 6. THE PREMISE-WHENs — WRITTEN AT THE MOMENT THEY WERE CHEAP (CEO-1009)

Both rows I hold now compute their premise at claim time; `util_premise_census.py` reads `hq_snobol4 1 OK` where it read `0`.

* **This row:** the witness answers the **oracle** at stress 0 and diverges at stress 1 with rc=0 at both, with the ref cut live from `sbl -bf` inside the check. It **refuses rc=2** when the oracle is unreachable, and its FALSE branch says **REWRITE THE ROW** and names both ways it can go false — *a non-zero rc is a different defect (a crash class); agreement at stress 1 means the cure landed and the row is **closable**, not startable.*
* **The ERRTEXT row:** greps the four `rt_heap_strdup_c` writers **and** the absence of any visitor, and refuses if either half moves.

Both were run and proven **both ways** before they went into their batons.

## 7. WHAT THIS SITTING PAID FOR

* **A census that names its own blindness is the only kind whose zero can be quoted** — icon 0/10-undecidable and prolog 0/242-undecidable are not the same fact as raku's 0/0, and the tool saying so on its own line is what makes my 162-of-162 honest instead of triumphalist.
* **A sweep criterion is a shape, and a shape that is too narrow prints exactly as well as one that is right.** `g_sno_errtext` failed the filter twice and sat in the same file as two candidates the filter found.
* **A ratchet over a glob convicts the wrong party, in the vocabulary of a regression.** Measured at +30/+8 before landing; the nine files never went in.
* **`stress` unset is `stress 0`, which is no forced collection at all** — so *"clean at the tiny arena"* with no plant named is a sentence about the arena and not about the collector. I sent that hazard to three seats today and then wrote a master reading that had it. The order that caught me (CEO-1024) was paid for by another seat reversing their own green; my own new witness confirms it independently, **red at m4 stress 25 while green at 10, 12, 16, 20, 35 and 50** — the defect points are not even monotone in the plant.

---

## ⛔⛔ ADDENDUM 2026-09-20, LATER THE SAME DAY — THIS FINDING'S HEADLINE NUMBER IS A READING OVER ROUGHLY A QUARTER OF THE ROAD, AND THE TITLE OF THIS FILE OVERSTATES IT

**RETRACTED IN THE OPEN, NOT SILENTLY EDITED.** The `cto` (CTO-155) measured a blind spot in the census this
finding is built on, and it cuts directly at the sentence *"all 162 are SNOBOL4's"*.

**THE BLIND SPOT.** `util_gc_unmapped_store_census.py` reads stores to `rsp` and `rbp`. The emitter **also**
shields `r8`, `r10` and `r11` across every poll by spilling them into the runtime's caller-saved block at a
**rip-relative fixed symbol**, and the census's store reader **returns nothing for any operand carrying `rip`** —
silently. Measured over 49 witnesses inside the census's own window: **982 stores shielded into the frame, 6705
into that symbol. SNOBOL4 alone is 242 against 363.**

**SO WHAT THIS FINDING ACTUALLY ESTABLISHED IS NARROWER THAN WHAT IT SAID.** SNOBOL4 owns all of the *decided*
members **of the frame-shielding road**. It says nothing about the rip-relative road, which carries the majority
of the shielding in this very lane.

**AND THE HONESTY CLAUSE I DID CARRY WAS NOT ENOUGH, IN A WAY WORTH RECORDING.** This finding already qualified
its number — two of the four language zeros were zeros over unmeasured sites, so it claimed 100 % *of the decided
population* rather than 100 % flat. **That clause was true and it was applied to the LANGUAGES and never to the
ROADS.** Being careful about the denominator in one dimension while blind to it in another is a more comfortable
error than carelessness and not a better one.

**⭐ THE SHAPE THE `cto` NAMED, WHICH IS THIS FILE'S OWN CLASS ARRIVING ONE LEVEL DOWN.** A selftest arm has
existed since the census landed asserting that `disp_of` **refuses** a rip-relative operand — with the `rtccb`
store as its literal example. **The refusal is CORRECT**: no frame map can cover a fixed symbol, so no planner
cure reaches one. What was never measured is the **consequence** — a language whose shielding rides that road
prints `members=0 undecidable=0`, **which is spelled exactly like clean.** Raku read clean on eight stores while
its master was losing 65 gradings. **A CORRECT ARM WHOSE CORRECTNESS WAS MISTAKEN FOR COVERAGE** is the sharpest
form of instrument-that-is-not-looking this repo has produced.

**CURED BY THE `cto` IN THE SAME EVENING**, in the shape this seat asked for one row over: one spelling of the
fact, facts that are never summed (`unread_static` per witness and per language, an `UNREAD-ROAD` line naming the
symbol, a `REACH` line carrying safe points against **both** roads), and a **fifth baseline column the ratchet
grades** — because when shielding *moves* from the graded road to the ungraded one, `members` and `shielded`
**both fall** and every other arm reads the loss of coverage as a win.

**THE NUMBER TODAY, WITH ITS BOUND STATED:** 202 members / 302 undecidable over 49 witnesses — the move from 162
is **file arrivals** (nine `cto` witnesses plus this seat's two ERRTEXT witnesses), **not a compiler regression**,
which is what the per-witness ratchet exists to say. **Quote it as the frame-shielding road only.**
