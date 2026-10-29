# ARCH-BUILTIN-TABLE.md — ONE BUILTIN TABLE: A CALL IS DECIDED ONCE, IN LOWER; THE RUNTIME RE-DECIDES NOTHING BY NAME (the cto, 2026-10-29 16:51 CDT; a DESIGN PROPOSED to Lon on his word *"what should we design next? Scan the SCRIP and give me an idea on how to improve it?"*; no row is minted until Lon rules)

## 0. The measurement (SCRIP fe4714842, mode 4, RT_OPT -O0, callgrind, SCRIP_DIAG=0; three loop witnesses of 200,000 builtin calls each, in the cto's scratch)

| witness | total Ir | Ir per call | where it goes |
|---|---|---|---|
| Raku `$n = $n + "abcdef".chars` | 2,294,168,271 | 11,470 | `__strcmp_avx2` 51.8%, `script_try_call_builtin_by_name_rq` 19.3%, `try_call_builtin_by_name_bl_s_rq` 10.3%: 81.4% is resolving the NAME |
| Icon `n +:= *map("abcdef")` | 339,634,209 | 1,698 | `try_call_builtin_by_name_bl_s_rq` 35.7%, `rt_call_arr_bl_strict` 6.5%, `rt_call_arr_impl` 6.4% |
| SNOBOL4 `N = SIZE("abcdef") + N` | 65,599,681 | 328 | `rt_call_bid_sn4` 13.4% (44 Ir per call), `bn_size` 25.9%: SNOBOL4 resolves `SIZE` to `BID_SIZE` AT COMPILE TIME (`c_rt_call_bid_sn4`, the `[BID_SIZE] = { bn_size, ... }` table at by_name_dispatch.c:21607) |

The shape behind the numbers: `src/runtime/by_name_dispatch.c` is 26,371 lines, 335 distinct `strcmp(fn, "name")` arms, 1,398 string compares, 49 first-character cases, and 12 of the runtime's 25 `rt_c2bb_bomb` sites (TWEAK, BUILD, grammar actions, `__rk_eval`, callsame, `rk_proc_descr_rq`: every one a road where C reached user code BY NAME). Its entry tests the `__rk_` prefix of the name before anything else: language identity decided in the runtime by a name's spelling, which CEO-1838 forbids past lower. What the emitter produces today: Icon's committed benchmark asm carries 322 `call_byname` boxes against 17 `call_direct`; a four-line Raku program 234 `call_method` and 31 `call_byname` boxes, each carrying its name as a `.string`; Pascal `call_pas_bi` (an id road through `rt_call_pas_bi`); Prolog `call_pl_leaf` (direct). The leaf share of SCORE.md (2026-10-17, mode 4) reads Raku 88.86% and Prolog 84.08% of instructions in the C runtime, Icon 16.38%, SNOBOL4 4.15%, Pascal 3.86%.

## 1. The malfunction, in the shape Lon already ruled on

Two deciders. The LOWERER knows the name, the arity and the language of every builtin call, because the call is in the source; the RUNTIME decides it AGAIN at every call by walking a string-compare chain, and decides language by the name's spelling on the way. This is the memory model's two-decider malfunction (CEO-1895: the layout granted and the emitter re-decided) over CALLS instead of cells. Placement is now decided once in the planner (the countdown reads 0 at fe4714842); a call is decided once in LOWER.

## 2. The design

- **(1) THE TABLE.** One generated table, `src/runtime/builtins/builtin_table.inc` from `harness/scripts/builtins.tsv` by `util_gen_builtin_table.py` with a currency gate -- the shape of `box_cell_shapes.tsv`/`.inc`. One row per builtin: name, the frontend vocabularies that spell it, min and max arity, the entry symbol, the kind (value leaf, generator, mutating with the variable, retaining), and whether it OPENS user code (the request channel of `rt_call_next_t`). Every `strcmp(fn, "x")` arm of the dispatcher becomes a row and its body a named leaf `bn_x(args, nargs, out)`, which SNOBOL4's `bn_size` already is.
- **(2) THE LOWERER RESOLVES.** A call whose callee is a literal name the frontend's vocabulary knows lowers to `IR_CALL` carrying the BID (the row index) on the node AS DATA (CEO-1836: a runtime entry named on the node), never the string; the template serves ONE form, `call_bid` (SNOBOL4's road generalized: the id in a register, `call rt_call_bid`), and a value leaf of fixed arity a direct `call bn_x`. Overloads by arity and by the frontend's own meaning (Icon `pos` against Snocone `pos`, ARCH-ICON-RTX 11.8 (b)) are the lowerer's, because language identity stops at lower.
- **(3) THE DYNAMIC ROAD.** A name computed at run time (SNOBOL4 `APPLY` and `$`, Icon string invocation `"upto"(...)`, Prolog `call/N` through `planner_rt_plan`, a Raku method on a value whose type the lowerer cannot know) resolves through ONE hash from name to BID built from the same table at `core_lib_init` (FNV and open addressing, `rt_proc_hash_lookup`'s shape), then takes the same `call_bid` road. A lookup is not a dispatch loop: nothing walks.
- **(4) RAKU'S METHODS.** The lowerer resolves a method call to a BID when the invocant's type is static (a literal, a declared type, the result of a known builtin); otherwise the dynamic road keyed by (type id, name). `rt_str_method`, `rk_is_rakudo_method` and `rk_qh_hook` become rows. The Raku rewrite design (`design-raku-rewrite-ceo-1998`) takes the table as its given.
- **(5) THE BOMBS.** The 12 `rt_c2bb_bomb` sites are rows marked `opens`; for those the lowerer emits the box-side open (`rt_call_open_by_name_p`'s shape, the request `rq` on the call edge), so C never discovers mid-call that it must reach a box. CEO-1576's gate `test_gate_no_c_to_bb.sh` stays at 0 throughout.
- **(6) WHAT IT DELETES.** `script_try_call_builtin_by_name_rq`'s chain, `try_call_builtin_by_name_bl_s_rq`, the `__rk_` prefix test, the 49 first-character cases, the per-call `strcmp`. `by_name_dispatch.c` keeps only leaves, each reachable by one id.

## 3. The order (LARGE CHUNKS, CEO-1478..1484)

(a) The table and its generator, every row carrying its arm's name, arity and entry, the gate current, NOTHING resolved yet: byte-identical asm (the coo's identity proof). (b) ICON FIRST, one language and one regime (322 by-name boxes in its benchmarks, 16% C share, four suites one short): rolled out small on the nine scanning builtins hq_icon already holds, smoked, then everywhere in Icon in a few landings. (c) Raku's methods. (d) The remaining `call_byname` boxes of SNOBOL4, Snocone and Rebus (12 in the benchmarks) and the dynamic road's hash. (e) The chain deleted. Then ultracode.

FINISH LINE (the DONE-WHEN a row would carry): `grep -c 'strcmp(fn' src/runtime/by_name_dispatch.c` at 0 as a ratchet that only falls; the three loop witnesses at or under SNOBOL4's per-call cost (Raku 11,470 and Icon 1,698 to the order of 300); every suite row not below its last reading; `test_gate_no_c_to_bb.sh` at 0 with the dispatcher's 12 bombs resolved to `opens` rows.

## 4. What it is not

Not an interpreter (one hash lookup for a run-time name; no loop over terms). Not a per-language emitter branch (one `call_bid` template form; the vocabularies live in the lowerers). Not an accessor layer (a row is read as a struct, as the planner's columns are). Not a frame or stack change (the call's cells are the planner's as today).

## 5. Rank, and who

In the order of work this reads as speed (rank 3), but its substance is CORRECTNESS: a runtime that decides language by a name's spelling is identity past lower (CEO-1838), and the by-name road is where 12 of the 25 C-to-box bombs live (CEO-1576). The cto proposes it as the NEXT DESIGN after the seven of CEO-1998, for Lon's word; on it the cto writes the STEPS.tsv and the test sources, hq_runtime executes (a) and (e), hq_icon (b), hq_raku (c), hq_snobol4 (d), the cfo when an HQ fails (CEO-1996).
