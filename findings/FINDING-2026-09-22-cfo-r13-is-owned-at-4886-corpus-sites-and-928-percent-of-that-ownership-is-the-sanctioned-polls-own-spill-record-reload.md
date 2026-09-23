# FINDING 2026-09-22 (cfo) — r13 IS OWNED ACROSS AN ALLOCATING RETURN AT 4886 CORPUS SITES, 98% OF THEM IN FILES THAT CONTAIN NO MATCH AT ALL, AND 92.8% OF THAT OWNERSHIP IS THE SANCTIONED POLL'S OWN SPILL-RECORD RELOAD

Asked for by the **cto** (mail `reply-yes-run-the-r13-owned-census-over-the-corpus-...`, 2026-09-22): *"r13 OWNED across an
allocating return with a defining class that is not RSP, IMM, D32 or RIP, over the 76-file corpus, and send me the name set
by file and graph."* The cto's stated decision rule: **if r13 is never owned outside a scan anywhere in the corpus, the
`rec_sigma` stays and the fact is written into the site as a static assertion; if it is owned anywhere, the
`bb_binop_relop_val` site gets a guard on the live Σ or a split path with a bare poll.**

Tree: SCRIP `9a2633f9b`, corpus `624adc393`, .github `786b91ef8`, clean. Build fresh (`make -j8`, 3.3 s incremental).
MODE DECTET. Arena knob irrelevant here — this is a **static** census of emitted mode-4 `.s`, nothing is executed.

## THE ANSWER: r13 IS OWNED, AND NOT MARGINALLY

**The second branch of the cto's rule is the live one.** The `rec_sigma` static assertion cannot be written, because the
fact it would assert is false in every language the corpus covers.

| population | sites |
|---|---|
| allocating call sites over the 77 compiled files | **11305** |
| r13 live across one | 11104 |
| — of those, `passed_through` (no def in this graph reaches the call; the ancestor's value) | 6130 |
| — of those, **`owned`** (this graph's own code put the value there) | **4974** |
| owned with a defining class **not spelled** RSP/IMM/D32/RIP — *the ask read literally* | **4954** |
| owned as the **census's own filing rule** counts it (one `CELL:` prefix peeled) | **4932** |
| owned with a class that **peels to a leaf that is not provably raw** — *the decision-relevant number* | **4886** |

⛔ **THE THREE COUNTS ARE RECONCILED, NOT ROUNDED.** 4954 → 4932 is **68 sites whose only non-four class is `CELL:RSP`**;
4932 → 4886 is **46 sites whose only such class is `CELL:CELL:RSP` or `CELL:CELL:CELL:RSP`**. All 114 are Pascal
(`perm.pas` 26, `fbench.pas` 17, `quick.pas`, `queens.pas`, `towers.pas`) and every one is **a copy of a stack address**,
which cannot be a heap pointer. I report 4886 and name the other two bands rather than ship one number three ways.
*(Instrument note for the cto, who owns the classifier: the census files `CELL:CELL:RSP` into the COPY list because it peels
exactly one prefix, while `bucket()` peels all of them — the same one-vs-all asymmetry behind the 289/287 drift. This is an
observation about the **r13 corpus population**, NOT about arm 5's residual, which is a different register set over a
different population; the two must not be netted.)*

## AND IT IS OWNED OUTSIDE A SCAN, MECHANICALLY AND NOT BY INFERENCE

The only route to a scan subject in r13 is `mov r13, rax` after `call rt_match_enter` (class SUBJECT;
`SUBJECT_SEED` is that literal at `util_gc_callee_saved_census.py:82`). So "outside a scan" is decidable by grep:

- **40 of the 44 files carrying r13-owned sites contain no `rt_match_enter` anywhere**, and they carry **4788 of the 4886
  sites**. No scan can exist in them.
- The 4 files that do call it are all SNOBOL4 (`mixed_workload`, `pattern_bt`, `string_pattern`, `roman`) and carry 98 sites.
- **SUBJECT-class readings in the entire corpus: 13.** Thirteen, against 4886.

**By language (sites / files):** icn 3576/14 · pas 643/10 · raku 458/9 · sno 119/5 · pl 90/6. Four of the five languages
have no SNOBOL4 match construct at all.

## THE RELOP SITE THE CURE IS FOR — 504 SITES, 26 FILES, THREE LANGUAGES, ZERO OF THEM IN A FILE WITH A MATCH

| | |
|---|---|
| r13-owned sites whose callee is a relop | **504** (26 files, 228 graphs) |
| of those, in a file with **no** `rt_match_enter` anywhere | **504 — all of them** |
| by language | icn 196 · pas 166 · raku 142 |
| by callee | `rt_jct_relop` 220 · `rt_relop_val_coerce` 167 · `rt_relop_overload` 117 |

The language-blindness of `bb_binop_relop_val` is confirmed in the emitted output, not just in the template: the same
owned-r13 shape appears in Icon, Pascal and Raku, in files where a subject pointer cannot exist.

## ⭐ THE MECHANISM, AND IT LANDS ON THE CEO-973 ROW FROM THE OTHER DIRECTION

Every reaching definition was walked back through the census's own reverse CFG and its defining form recorded:

| defining form | sites it owns |
|---|---|
| **`mov r13, qword ptr [rsp + N]`** | **4626** |
| `mov r13, qword ptr [rbp + N]` | 337 |
| `mov r13, rax` (includes the 13 SUBJECT) | 232 |
| `mov r13, rsp` | 82 |

And pairing each `[rsp + N]` reload with the call in front of it:

- **4596 sites — 92.8% of all r13 ownership in the corpus — are owned by a reload out of the sanctioned poll's OWN spill
  record**: `mov qword ptr [rsp + N], r13` before `call rt_gc_point_arr_c@PLT`, `mov r13, qword ptr [rsp + N]` after it,
  **same slot, matching store, no intervening write**.
- The only other pairings in the whole corpus: 4 at `scrip_coret`, 1 at `scrip_coexpr_activate`.

Worked example, read out of the emitted asm rather than off the classifier — `bubble.pas.s`, graph `n14_binop_test`,
allocating return at **line 513** (`call rt_jct_relop@PLT`), r13 live across it (read at 521 to be spilled). Its seven
reaching definitions are lines 535, 863, 1710, 1980, 2367, 2521, 2790 — **every one of them `mov r13, qword ptr [rsp + 8]`**,
each the reload half of a spill/reload pair around `rt_gc_point_arr_c@PLT`, reaching 513 through the box graph's back-edges:

```
521:  mov  qword ptr [rsp + 8], r13      <- the poll's own record: r13 stored
530:  call rt_gc_point_arr_c@PLT         <- the sanctioned poll
535:  mov  r13, qword ptr [rsp + 8]      <- reloaded from the SAME slot  (class CELL == "a copy", so OWNED)
```

⭐ **This is exactly the site class the ceo ruled at CEO-1164 is the cfo's CEO-973 named-raw table** ("a reload out of the
poll's OWN tagged spill record, verified mechanically — source cell inside the array handed to THAT poll, no intervening
write, record below the declared floor"). The cto's tag-truth question and the cfo's named-raw row meet at one instruction.
**The consequence for the split of work: the relop site's r13 is not a tag-truth problem for the great majority of the
population — it is the named-raw table's own site class, and the table retires the ownership rather than guarding it.**

⛔ **THE RESIDUAL IS MEASURED, NOT SUBTRACTED.** A site can have several reaching definitions, so "total minus poll-owned"
is not the residual — a site owned by BOTH the poll reload and something else still needs the something else. Counting the
sites that carry at least one owning def that is neither the poll reload nor a provably-raw form (`mov r13, rsp`):

| | corpus-wide | **at the relop sites** |
|---|---|---|
| r13-owned sites (leaf-peeled) | 4886 | **504** |
| every owning def IS the poll's spill-record reload | 4236 | **445** |
| **residual: at least one def needing a tag of its own** | **568** | **30** |
| — `mov r13, qword ptr [rbp + N]` | 337 | 26 |
| — `mov r13, rax` | 232 | 4 |
| residual by language | icn 398 · pl 90 · sno 80 · pas 0 · raku 0 | **icn 30 · pas 0 · raku 0** |

**So the relop cure's own residual is 30 sites in five Icon files** (`tgrlink` 18, `geddump` 4, `rsg` 4, `micsum` 3,
`concord` 1) — **not one of them Pascal or Raku**, the two languages where the cto's language-blind-relop worry was sharpest.
The 474 remaining relop sites are retired by the CEO-973 table. Corpus-wide the residual is 568 sites, and it too is
Icon/Prolog/SNOBOL4 only: **zero Pascal and zero Raku sites in the whole corpus own r13 by anything but the poll's own
record or a stack address.**

## PROVENANCE AND COST (economy, cfo)

- **Denominator:** 86 sources globbed from `corpus/benchmarks/*/*.{sno,sc,icn,pl,reb,raku,pas}`; **77 compile** to mode-4
  `.s`; 9 refuse (8 Raku — parse errors and mode-4 `[SMX]` non-coverage — plus `whet.pas`, a Pascal parse error). The cto's
  "76-file corpus" and this 77 differ by one; the 9 refusals are named in the raw log so the gap is auditable, and nothing
  in the finding depends on which of 76/77 is the divisor.
- **Method:** `util_gc_callee_saved_census.py` **imported, not reimplemented** — `allocating_entries`, `parse`, `build_cfg`,
  `build_ctx`, `liveness`, `build_pred`, `classify_def`, `graph_of` are the blocking gate's own, so this answer cannot drift
  from `test_gate_gc_a_callee_saved_register_at_an_allocating_return_is_named_not_assumed.sh`. Cross-check: the artifact has
  **11104 rows against the instrument's own `live_across=11104`**, and owned 4974 + passed_through 6130 = 11104.
- **BOARD COST (new row for the cfo cost table):** corpus compile 77 files **1.9 s**; one full r13 CFG+liveness pass over
  the 77 `.s` **62–102 s** at load ~5 on 16 cores (102 s when it also renders the full per-site report). A re-run of this
  census is therefore a **~1 minute** purchase, not a board.
- **Artifact:** `r13_sites.tsv`, one row per r13 live-across site with state, class set, every defining form and def line —
  scratch, volatile; regenerate in ~65 s by the recipe above.

## THE NAME SET, BY FILE AND GRAPH (the cto's ask)

4886 r13-OWNED sites over 44 files and 3771 graphs. Per file: site count, graph count, whether the file contains
`rt_match_enter` AT ALL, and the heaviest graphs. The Icon files are long tails — hundreds of graphs at 1–4 sites
each — so the graph column is the honest shape of it rather than a list that would run to 3771 lines.

```
THE NAME SET: 4886 r13-OWNED sites over 44 files and 3771 graphs

micro.icn.s  sites=633  graphs=453  match_enter_in_file=0
   top graphs: main=123  n1316_to=4  n1334_to=4  n3562_to=4  n3614_to=4  n3744_to=4  (+447 more graphs)

tgrlink.icn.s  sites=561  graphs=485  match_enter_in_file=0
   top graphs: main=12  n1657_to=4  n418_proc_gen=3  n808_binop_test=3  n813_binop_test=3  n829_binop_test=3  (+479 more graphs)

rsg.icn.s  sites=494  graphs=388  match_enter_in_file=0
   top graphs: main=26  n604_to=4  n2690_to=4  n2821_to=4  n2993_to=4  n11_scan_tab=3  (+382 more graphs)

ipxref.icn.s  sites=480  graphs=426  match_enter_in_file=0
   top graphs: main=13  n710_to=4  n2063_to=4  n2194_to=4  n2366_to=4  n391_binop_test=3  (+420 more graphs)

geddump.icn.s  sites=403  graphs=297  match_enter_in_file=0
   top graphs: main=16  n17_proc_gen=3  n267_binop_test=3  n341_binop_test=3  n346_proc_gen=3  n651_scan_tab=3  (+291 more graphs)

deal.icn.s  sites=297  graphs=244  match_enter_in_file=0
   top graphs: main=13  n39_to=4  n75_to=4  n1580_to=4  n1711_to=4  n1883_to=4  (+238 more graphs)

queens.icn.s  sites=281  graphs=220  match_enter_in_file=0
   top graphs: main=11  n46_to=4  n1551_to=4  n1682_to=4  n1854_to=4  n50_binop_test=3  (+214 more graphs)

concord.icn.s  sites=274  graphs=216  match_enter_in_file=0
   top graphs: main=12  n1558_to=4  n1689_to=4  n1861_to=4  n23_scan_tab=3  n31_scan_tab=3  (+210 more graphs)

fbench.pas.s  sites=185  graphs=157  match_enter_in_file=0
   top graphs: main=7  n432_call=3  n448_call=3  n785_call=3  n790_binop_test=3  n988_call=3  (+151 more graphs)

send-more-money-loops.raku.s  sites=166  graphs=88  match_enter_in_file=0
   top graphs: n12_binop_test=3  n15_binop_test=3  n25_binop_test=3  n28_binop_test=3  n38_binop_test=3  n41_binop_test=3  (+82 more graphs)

queens.pas.s  sites=125  graphs=87  match_enter_in_file=0
   top graphs: n44_binop_test=3  n54_binop_test=3  n68_binop_test=3  n84_binop_test=3  n94_binop_test=3  n99_call=3  (+81 more graphs)

intmm.pas.s  sites=100  graphs=90  match_enter_in_file=0
   top graphs: n18_binop_test=2  n25_binop_test=2  n30_binop_test=2  n72_binop_test=2  n77_binop_test=2  n119_binop_test=2  (+84 more graphs)

micsum.icn.s  sites=95  graphs=86  match_enter_in_file=0
   top graphs: n21_scan_tab=3  n27_scan_tab=3  n36_scan_tab=3  n164_binop_test=3  main=2  n10_deref=1  (+80 more graphs)

quick.pas.s  sites=75  graphs=57  match_enter_in_file=0
   top graphs: n59_binop_test=3  n62_binop_test=3  n65_call=3  n68_binop_test=3  n259_call=3  n16_binop_test=2  (+51 more graphs)

bubble.pas.s  sites=64  graphs=57  match_enter_in_file=0
   top graphs: n14_binop_test=2  n25_binop_test=2  n57_binop_test=2  n66_binop_test=2  n79_binop_test=2  n84_binop_test=2  (+51 more graphs)

merge-sort.raku.s  sites=54  graphs=35  match_enter_in_file=0
   top graphs: n6_call_builtin=4  n18_call_builtin=4  n191_call_builtin=4  n197_call_builtin=4  n36_binop_test=3  n184_call_builtin=3  (+29 more graphs)

point_class_add1.raku.s  sites=51  graphs=21  match_enter_in_file=0
   top graphs: n106_call_builtin=8  n109_call_builtin=8  n43_call_builtin=4  n45_call_builtin=4  n122_call_builtin=4  n126_call_builtin=4  (+15 more graphs)

mixed_workload.sno.s  sites=49  graphs=41  match_enter_in_file=1
   top graphs: n125_match_defer=4  n126_match_end=3  n151_assign_var=3  n123_assign=2  n97_call=1  n100_call=1  (+35 more graphs)

point_class_add.raku.s  sites=48  graphs=21  match_enter_in_file=0
   top graphs: n78_call_builtin=8  n81_call_builtin=8  n17_call_builtin=4  n94_call_builtin=4  n98_call_builtin=4  n10_call_builtin=3  (+15 more graphs)

sieve.pas.s  sites=41  graphs=34  match_enter_in_file=0
   top graphs: n12_binop_test=2  n19_binop_test=2  n24_binop_test=2  n40_binop_test=2  n45_binop_test=2  n56_binop_test=2  (+28 more graphs)

bench_icnsub_table_miss_semantics.icn.s  sites=40  graphs=31  match_enter_in_file=0
   top graphs: n86_to=4  n101_to=4  n125_to=4  n72_deref=1  n73_deref=1  n74_deref=1  (+25 more graphs)

point_class_add2.raku.s  sites=40  graphs=13  match_enter_in_file=0
   top graphs: n103_call_builtin=8  n106_call_builtin=8  n52_call_builtin=4  n115_call_builtin=4  n119_call_builtin=4  n46_call_builtin=3  (+7 more graphs)

rc-dragon-curve.raku.s  sites=34  graphs=28  match_enter_in_file=0
   top graphs: n77_call_builtin=4  n84_call_builtin=4  n58_unop=1  n59_call_builtin=1  n61_call_builtin=1  n63_call_builtin=1  (+22 more graphs)

insertion-sort.raku.s  sites=28  graphs=20  match_enter_in_file=0
   top graphs: n4_call_builtin=4  n18_binop_test=3  n24_binop_test=3  n5_to=2  n8_deref=1  n10_call_builtin=1  (+14 more graphs)

perm.pas.s  sites=24  graphs=17  match_enter_in_file=0
   top graphs: n238_call=3  main=3  n215_binop_test=2  n222_binop_test=2  n236_binop_test=2  n217_assign=1  (+11 more graphs)

indirect_dispatch.sno.s  sites=21  graphs=15  match_enter_in_file=0
   top graphs: n74_call=4  n117_call=3  n119_assign=2  n69_call=1  n75_binop=1  n76_assign=1  (+9 more graphs)

string-escape.raku.s  sites=20  graphs=11  match_enter_in_file=0
   top graphs: n27_call_builtin=7  n35_call_builtin=4  n29_call=1  n31_call=1  n36_call_builtin=1  n40_binop=1  (+5 more graphs)

pattern_bt.sno.s  sites=17  graphs=11  match_enter_in_file=1
   top graphs: n83_match_defer=4  n84_match_end=3  n81_assign=2  n77_call=1  n88_call=1  n92_coerce_numeric=1  (+5 more graphs)

pi-sequential-iteration.raku.s  sites=17  graphs=15  match_enter_in_file=0
   top graphs: n19_binop_test=3  n4_binop_test=1  n6_call_builtin=1  n8_call_builtin=1  n11_call_builtin=1  n22_binop=1  (+9 more graphs)

string_pattern.sno.s  sites=17  graphs=11  match_enter_in_file=1
   top graphs: n92_match_defer=4  n93_match_end=3  n90_assign=2  n86_call=1  n97_call=1  n101_coerce_numeric=1  (+5 more graphs)

epilogue_gplc.pl.s  sites=15  graphs=9  match_enter_in_file=0
   top graphs: n42_call_proc_staged=3  n152_call_value=3  n154_call_value=2  n251_call_value=2  n37_call=1  n38_call=1  (+3 more graphs)

prelude_gplc.pl.s  sites=15  graphs=9  match_enter_in_file=0
   top graphs: n90_call_proc_staged=3  n200_call_value=3  n202_call_value=2  n299_call_value=2  n85_call=1  n86_call=1  (+3 more graphs)

prelude_swipl.pl.s  sites=15  graphs=9  match_enter_in_file=0
   top graphs: n101_call_proc_staged=3  n211_call_value=3  n213_call_value=2  n310_call_value=2  n96_call=1  n97_call=1  (+3 more graphs)

prelude_trealla.pl.s  sites=15  graphs=9  match_enter_in_file=0
   top graphs: n106_call_proc_staged=3  n216_call_value=3  n218_call_value=2  n315_call_value=2  n101_call=1  n102_call=1  (+3 more graphs)

prelude_xsb.pl.s  sites=15  graphs=9  match_enter_in_file=0
   top graphs: n120_call_proc_staged=3  n230_call_value=3  n232_call_value=2  n329_call_value=2  n115_call=1  n116_call=1  (+3 more graphs)

prelude_yap.pl.s  sites=15  graphs=9  match_enter_in_file=0
   top graphs: n120_call_proc_staged=3  n230_call_value=3  n232_call_value=2  n329_call_value=2  n115_call=1  n116_call=1  (+3 more graphs)

roman.sno.s  sites=15  graphs=7  match_enter_in_file=1
   top graphs: n51_match_defer=4  n39_match_end=3  n55_match_end=3  n49_assign=2  n41_match_replace=1  n45_call=1  (+1 more graphs)

towers.pas.s  sites=11  graphs=7  match_enter_in_file=0
   top graphs: n81_call=3  n74_binop_test=2  main=2  n76_assign=1  n84_binop=1  n85_assign=1  (+1 more graphs)

bench_icnsub_list_dispatch.icn.s  sites=9  graphs=9  match_enter_in_file=0
   top graphs: n22_coerce_numeric=1  n23_binop=1  n25_coerce_numeric=1  n26_binop=1  n27_subscript=1  n28_deref=1  (+3 more graphs)

uplevel2.pas.s  sites=9  graphs=5  match_enter_in_file=0
   top graphs: n4_binop_test=3  n9_binop_test=3  n12_binop=1  n16_binop=1  n20_binop=1

uplevel3.pas.s  sites=9  graphs=5  match_enter_in_file=0
   top graphs: n4_binop_test=3  n9_binop_test=3  n12_binop=1  n16_binop=1  n20_binop=1

bench_icnsub_table_miss_dispatch.icn.s  sites=5  graphs=5  match_enter_in_file=0
   top graphs: n21_subscript=1  n22_deref=1  n27_deref=1  n29_call_icon=1  main=1

bench_icnint_loop.icn.s  sites=2  graphs=2  match_enter_in_file=0
   top graphs: n22_call_icon=1  main=1

bench_icnint_mod_isolate.icn.s  sites=2  graphs=2  match_enter_in_file=0
   top graphs: n18_call_icon=1  main=1
```
