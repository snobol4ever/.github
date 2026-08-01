
---

## 10. ⛔ LON RULING (s165, after the re-land): **DELETE THE PROLOGUE AND EPILOGUE. THEY ARE OLD. THEY DO NOT APPLY. WE ARE SCOPING AT A DIFFERENT LEVEL NOW.**

The §7 re-land is **REVERTED** — `xa_flat.cpp` back to 237 lines, enum members / declarations / both dispatch cases gone, `emit_graph_reads_pinned_frame()` deleted, zero live references tree-wide (only historical comments remain). Clean build, `-O0`, zero `-O1`/`-O2`.

⭐ **AND THE RULING IS RIGHT ABOUT MY FIX IN A WAY THE GATES COULD NOT SHOW.** The re-land keyed on `flat_jmp_entry || flat_pat || flat_gen` — **exactly the graphs that most need converting to per-BB storage.** Its own "self-retiring" comment claimed it would widen automatically as kinds arm; in practice it *guaranteed* the legacy whole-graph protocol stayed live on precisely the population the new scope has to take over. A gate that preserves the old model for the conversion frontier is not a bridge, it is an anchor. **Recording this because the gates were green and only the architecture said no.**

**HONEST COST, MEASURED AND NOT SOFTENED:** Prolog smoke returns to m2 **3/5** (HARD GATE red) · m3 3/5 · m4 2/5; bench **broken=22/22**. Prolog and Icon stay red until the readers convert. The §8 teardown defect is unaffected and remains independently open.

## 11. ⭐⭐ THE CONVERSION LIST — WHAT THE NEW SCOPE MUST TAKE OVER, CENSUSED BY KIND

The readers do **not** disappear because their producer did: the compiler still emits every one of them, now against a frame nobody establishes. They are the work. Censused over emitted `nrev` + `queens` + `qsort` at the deleted state, grouped by the emitted label's own IR kind — **4,510 whole-graph-frame references**:

| refs | share | IR kind | s164 run-gating rank |
|---|---|---|---|
| **2255** | 50.0% | `call_builtin_prolog` | **185/185 = 100%** |
| 781 | 17.3% | PROC-ENTRY / graph-level | — |
| **732** | 16.2% | `var_ref` | 130/185 |
| 258 | 5.7% | `lit_string` | — |
| 180 | 4.0% | `lit_integer` | — |
| 125 | 2.8% | `suspend` | — |
| 102 | 2.3% | `call_proc_staged` | 91/185 |
| 68 | 1.5% | `var` | 93/185 |
| 5 | 0.1% | `move_label` | 157/185 |
| 4 | 0.1% | `disjunction` | — |

⭐⭐ **THE RULE THIS EARNS — RUN-GATING RANK AND STORAGE-WEIGHT RANK ARE TWO DIFFERENT ORDERINGS, AND A LADDER NEEDS BOTH.** s164 ranked kinds by how many runs they block (all-or-nothing per run, so nothing executes until the whole blocking set is armed). This censuses how much frame storage each kind actually *reads*. They disagree sharply: `move_label` gates **157/185 runs but owns 5 references** — nearly free to arm, and arming it moves almost no storage; `lit_string`/`lit_integer` own 438 references between them and appear in no unlock set at all. **Ranking by either axis alone picks the wrong rung** — s164's own "vacuous by construction" trap, from the other side.

**ORDER IMPLIED (both axes agree only at the top):**
1. ⭐⭐ `call_builtin_prolog` — **50% of readers AND gates 100% of runs.** Dominates both axes; nothing else is arguable as first.
2. `var_ref` — 16.2% and 130/185.
3. The cheap completers `move_label` / `var` / `call_proc_staged` — small reader counts, but needed to finish the unlock set so runs actually execute.
4. `lit_string` / `lit_integer` (438 refs) — pure storage weight, no gating; free to take whenever convenient.
5. ⚠ **PROC-ENTRY / graph-level, 781 refs (17.3%), has NO BB to own it.** This is the residue of the entry protocol itself (wire header, saved rcx/rdx/rbp). Per-BB self-allocation has no natural home for it, so it needs an explicit design answer rather than a conversion — **it is the one item on this list that is not simply "arm another kind."**
