# FINDING 2026-07-27m — SIXTH PHANTOM CLASS: **THE ALREADY-PORTED SYMBOL.** `rt_deref` IS ALREADY ASSEMBLY, RTX-5 IS A THIRD SMALLER THAN ITS RUNG, AND STEP 0's OWN GREP CANNOT SEE `.S` FILES

**Session:** s200 · **Goal:** `GOAL-SNOBOL4-RTX.md` → RTX-5 (AGG) step 0 · **Read-only reconnaissance; no code changed.**

---

## 1. THE FINDING

RTX-5's rung says step 0 is done and must not be re-derived. Two of its three claims verify **byte-exactly**:

| claim | verified |
|---|---|
| `rt_subscript_var` at `pattern_match.c:1000` | ✅ exact |
| `rt_field_var` at `pattern_match.c:1042` | ✅ exact |
| `rt_deref` "exported, but NOT grep-locatable; `core/core.c` is non-UTF-8 (`file` says `data`), so ordinary greps miss it — **locate it before porting**" | ⛔ **the symptom was real, the diagnosis was wrong** |

`core/core.c` **is** non-UTF-8 (`file` confirms `data`) — that part is true and is a genuine hazard. But it is **not where `rt_deref` lives**, and encoding is not why the grep missed it.

⭐⭐ **`rt_deref` IS ALREADY HAND-WRITTEN x86-64 ASSEMBLY.** It is defined in **`src/runtime/rt/rt_asm_helpers.S:8`**, resolved by `nm`-ing all 240 objects to `out/rt_pic/rt_asm_helpers.o`. It is a proper fast-path/slow-path port in exactly RTX's own idiom: three hot deref shapes inlined (slen==1 pointer cell, slen==0 shared-NV name, slen==2 nametrap with direct `cellp`), every cold shape tail-jumping to `rt_deref_slow@PLT`. Its header comment documents the same DESCR_t register marshaling the RTX contract calls its "ABI cornerstone" — `RDI:RSI` in, `RAX:RDX` out — verified there against an emitted mode-4 caller.

**`to_int` in the same file is likewise already ported** (DT_I fast path, `to_int_slow` fallback).

---

## 2. ROOT CAUSE — STEP 0's GREP IS STRUCTURALLY BLIND TO ASSEMBLY

`ARCH-SNOBOL4-RTX.md` §7 specifies the step-0 existence check verbatim as:

`grep -rn '<sym>' src/ --include=*.c --include=*.h --include=*.cpp`

**There is no `--include=*.S`.** A symbol already implemented in assembly therefore returns **zero hits** and presents exactly as a phantom — the same signature RTX-2 (dead), RTX-3 (invented) and RTX-4 (misrecorded) all produced. s188's session hit this, correctly observed the symbol was absent from `src/runtime/` greps, and reached for the nearest available explanation — the genuinely-weird non-UTF-8 `core.c` sitting right there in the same subtree. **A plausible neighbouring anomaly absorbed the blame for a filter defect.**

⛔ **FIX (one word, and it retires the whole class): add `--include=*.S` to the step-0 grep in ARCH §7.** Better still, drop the `--include` filters entirely for the existence check — the cost of a few extra hits is nil next to the cost of a rung aimed at an already-ported symbol.

---

## 3. ⭐ SIXTH MEMBER OF THE PHANTOM FAMILY — AND THE FIRST WHOSE FAILURE MODE IS *DUPLICATED WORK*

| # | rung | class | what step 0 saw | what was true |
|---|---|---|---|---|
| 1 | RTX-2 (s163) | **DEAD** | name exists | zero live call sites, C unbuilt in `archive/` |
| 2 | RTX-3 (s164) | **INVENTED** | name in prose | declaration-only, no definition anywhere |
| 3 | RTX-4 (s165) | **MISRECORDED** | grep fails | live symbol, doc spelled it truncated |
| 4 | RTX-4 sl.3 (s188) | **COLD** | passes (a)(b)(c) | real + correct, never executed in the window |
| 5 | RTX-3b (s199) | **UNREPRESENTATIVE REPRO** | repro agrees | it exercised a different path than the port |
| 6 | **RTX-5 (s200)** | **ALREADY PORTED** | **grep fails ⇒ reads as phantom** | **real, live, hot — and already assembly** |

⭐ **THE FIVE EARLIER MEMBERS ALL WASTE A RUNG ON WORK THAT CANNOT PAY. THIS ONE WASTES A RUNG RE-DOING WORK THAT ALREADY PAID** — and it is the more dangerous shape, because a re-port would have *succeeded*: batteries green, board unmoved, and the null result misread as "AGG asm doesn't help" when the truth is "that part was already asm."

⛔ **STEP 0(e), PROPOSED: BEFORE PORTING, CONFIRM THE SYMBOL IS NOT ALREADY ASSEMBLY.** `nm` the defining object, or grep `.S` files. Ten seconds. The check that would have caught this is smaller than the one that missed it.

---

## 4. THE COMPLETE MAP OF ASM THE RTX LADDER DOES NOT KNOW IT HAS

`grep -rl rt_asm_helpers` across all of `.github` returns **one** file — an unrelated Icon finding. **No RTX doc mentions it. ARCH §4 declares RTX sources live in `src/runtime/rtx/`; these do not.**

| file | exported symbols | gated? |
|---|---|---|
| `src/runtime/rtx/{alloc,call,misc,str}.S` | the four RTX families | ✅ `SCRIP_RTX_<FAM>` |
| **`src/runtime/rt/rt_asm_helpers.S`** | **`rt_deref`** · `to_int` | ⛔ **none** |
| **`src/runtime/rt/rt_sg_scan.S`** | `rt_sg_scan_member` · `rt_sg_scan_nonmember` · `rt_sg_member` | ⛔ **none** |
| `src/runtime/rt_gram_trampoline.S` | `rk_gram_enter_box` (Raku) | ⛔ none |

⛔ **SIX RUNTIME SYMBOLS ARE IN HAND-WRITTEN ASSEMBLY WITH NO KILL-SWITCH, NO DIFFERENTIAL BATTERY, AND NO GATE.** The RTX contract's entire migration discipline — dual-build, per-family kill-switch, md5 byte-identity vs pristine, two-sided falsification — **does not cover them.** If `rt_deref` were subtly wrong, there is no `SCRIP_RTX_*=0` that bisects it, and s200's own board work (which leaned on "all four gates off ⇒ pristine C") would silently **not** have been pristine C at all.

⚠ **THIS QUALIFIES s200's OWN EARLIER RESULT AND I AM FLAGGING IT AGAINST MYSELF:** this session reported "all four RTX gates OFF ⇒ byte-identical failure set" as a whole-surface kill-switch proof. That remains true **as stated** — the four *RTX* families are byte-identical ON vs OFF. But it is **not** the stronger claim it could be mistaken for. "All RTX gates off" ≠ "no hand-written asm in the runtime." Six symbols stay asm in both arms.

---

## 5. WHAT THIS DOES TO RTX-5 — THE RUNG IS A THIRD SMALLER THAN IT READS

Step 0(d)'s dynamic measurement is **sound and independently corroborated here.** Its `table_access` counts were `rt_subscript_var` 5,001,000 · `rt_deref` 2,500,500 — "exactly 2:1." Static emitted call sites in `corpus/benchmarks/snobol4/table_access.s`: `rt_subscript_var` **2**, `rt_deref` **1**, `rt_field_var` **0**. **The same 2:1.** Static and dynamic agree.

| target | calls | status |
|---|---|---|
| `rt_subscript_var` | 5.0M | **C — the real RTX-5 target** |
| `rt_deref` | 2.5M | ⭐ **ALREADY ASM — no work available** |
| `rt_field_var` | 0 in `table_access` | cold here |

⇒ **RTX-5's addressable surface is `rt_subscript_var` + the table internals it calls — not the three-symbol list the rung names.** One third of the named targets, and one third of the measured call volume, is already done. **State the expected board accordingly, or the rung fails s188's own vacuity test before it starts.**

---

## 6. ⭐⭐ THIS RESOLVES LON'S OPEN FORK — WITH AN EXPERIMENT, NOT AN OPINION

RTX-5 carries a fork awaiting Lon's ruling: integer-keyed table access does `tbl_key_str` **stringify** → `_tbl_hash` **hash the digits** → `table_find_pair` **strcmp down the chain** → **`rt_agg_alloc` per subscript** (because `rt_subscript_var` returns a NAME). Options recorded: (i) port as-is, winning only `-O0` ceremony; (ii) promote the table-LAYOUT rung ahead of RTX-5; (iii) middle path — fuse itoa+hash in one pass, preserving layout exactly.

**The fork is really one empirical question: how much does asm-ceremony-alone buy on an AGG leaf?** If it is large, (i) is fine and layout can wait. If it is small, the algorithm is the whole story and (ii)/(iii) win.

⭐ **THAT EXPERIMENT HAS ALREADY BEEN RUN — WE JUST CANNOT READ IT, BECAUSE IT HAS NO GATE.** `rt_deref` is an AGG-family leaf, hot at 2.5M calls in the very benchmark the rung would be graded on, already ported to asm in the identical fast-path/slow-path idiom. **It is a perfect natural control for exactly this question**, and the only reason it yields no number is the missing kill-switch from §4.

⛔ **RECOMMENDED SEQUENCE — CHEAP, AND IT ANSWERS THE FORK WITH A MEASUREMENT:**
1. **RTX-5a (small, hours): bring `rt_asm_helpers.S` under the RTX contract.** Add a gate (`SCRIP_RTX_AGG`, or its own `SCRIP_RTX_LEAF`), rename the C fallbacks to the `c_*` convention, add a differential battery, run the two-sided falsification. **This is owed regardless of the fork** — §4 shows six ungated asm symbols, which is a standing hole in the migration discipline and a live hazard to every board claim that assumes gates-off means pristine C.
2. **Then measure `rt_deref` ON vs OFF on `table_access`** (adequate window: 1324ms, and `bench_sno_rtx.sh` already gates the ≥800ms floor). **That ratio is the price of asm ceremony on an AGG leaf, measured, not argued.**
3. **Then Lon rules with a number in hand.** If `rt_deref` moves like `var_access` did (1.37×), option (i) is vindicated. If it moves like the AGG null control (1.00–1.04), the ceremony is worth nothing here and the algorithm — option (ii) or (iii) — is the only real win.

⚠ **AND STATE THE EXPECTED BOARD FIRST, per s187/s188:** if step 2 returns ~1.00, that is not a failed measurement, it is **the answer**, and it falsifies option (i) outright.

⚠ **CONCURRENCY UNCHANGED AND NOW SHARPER:** `rt_subscript_var` and `rt_field_var` both live in `pattern_match.c` — the ζ session's active file **and** the home of all 47 current board failures. `rt_asm_helpers.S` does **not**, which makes RTX-5a additionally attractive: **it is the one piece of this rung that cannot collide with the parallel session.**
