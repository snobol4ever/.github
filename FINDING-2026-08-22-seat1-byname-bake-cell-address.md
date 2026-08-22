# FINDING — the 43.8% by-name defect was a linear scan hiding behind a hash-shaped table; hashing it recovers 97% of the defect's own cost and 42.8% of every instruction beauty.sno executes

**Session:** 2026-08-22 seat1 (`/home/claude1`, Claude Sonnet 5), THE LOOP queue row `byname-bake-cell-address`, rank 0. RT_OPT=`-O0`, callgrind whole-process Ir, `make pristine` before every verdict (HQ-27). Watermark: SCRIP `c72482d6` → this session's two commits, corpus `51e640cd` (untouched — all six `.s` regen scripts report `changed=0`), `.github` at this commit.

## (1) STEP 1 — WHICH CONSTRUCT REACHES THE BY-NAME ROAD (witnessed, not guessed)

The brief's own hypothesis (SPITBOL's `NRETURN` idiom, `. *F()` via `rt_dcap_pump`) is real but is **not** the dominant contributor. A direct witness — a temporary trace inside `rt_call_proc_descr` logging `(name, nargs)` for every call, run over `scrip beauty.sno < beauty.sno`, then reverted before any fix landed — shows:

- **281,240 traced calls, `nargs=0` on every single one** (confirms s194's "only zero-arg deferred calls reach that road").
- Dominant name: **`EXPR$31`, 158,620 calls alone (56.4% of the trace)** — a *compiler-synthesized* zero-arg thunk. Per seat5's s194 cursor, an arity≥1 deferred-call target gets "lifted" to an auto-generated `EXPR$<N>` wrapper so it can still travel the zero-arg alpha-cell road; beauty.sno's expression grammar routes one extremely hot backtracking site through a single such thunk.
- Long tail: dozens more `EXPR$<N>` thunks (~2,000–3,000 calls each) plus beauty's own `IncCounter`/`PushCounter`/`PopCounter` helpers (~3,700–4,200 each).
- `rt_dcap_pump` (the brief's named suspect) accounts for only ~21,519 of the traced calls (~7.5%) — real, but a minority contributor.

Compiled call-site attribution (via callgrind's caller-tree, `cfn=` edges into `rt_call_proc_descr`/`'2`) confirms the *mechanism*: **`rt_defer_get_pat_dtp` (`src/runtime/pattern_match.c:1048`), reached from exactly one template — `src/templates/bb_match_defer.cpp:144`, the compiled form of `IR_MATCH_DEFER`** — accounts for 233,064 of ~285,046 attributed calls (~82%). This is SNOBOL4's `*<name>` deferred-evaluation operator (`if (varname[0]=='*') { rt_call_proc_descr(varname+1, 0); ... }`), used both for beauty's hand-written recursive grammar rules (`Gray = *White | epsilon`, dozens of siblings — none of which are `DEFINE`'d procedures in the source; beauty.sno has exactly 6 `DEFINE`s, all pretty-printer helpers unrelated to the grammar) and for the compiler's own synthesized `EXPR$<N>` thunks. Exact call count into `bb_ab_fn_cell_ptr` for the full pristine run: **551,979** — matching the brief's 550,995 almost exactly (my own early caller-tree summation undercounted at ~285K by missing some edges; the direct per-function count is authoritative and reconciles cleanly).

## (2) STEP 2 — INDEPENDENT CONFIRMATION OF THE 43.8%

Own callgrind run, `scrip beauty.sno < beauty.sno` (m3), before touching any code:

| | Ir | % of total |
|---|---|---|
| PROGRAM TOTAL | 27,760,640,730 | 100.0% |
| `__strncmp_avx2` (called from `bb_ab_slot_for`) | 7,374,668,425 | 26.57% |
| `emit.cpp:bb_ab_slot_for` (own cost) | 4,861,075,974 | 17.51% |
| **combined defect** | **12,235,744,399** | **44.08%** |

Matches the brief's 43.8% within measurement noise (different commit/session). m3 self-host fixed point (`scrip beauty.sno < beauty.sno` byte-identical to the input, md5 `6f1671c0757729992ae01a6bdf16f081`) reproduced before any change.

## (3) ⭐ WHY A HASH, NOT (YET) THE BAKE — AND WHAT WAS FOUND ABOUT THE BAKE

The brief is explicit: *"THIS IS A BAKE, NOT A HASH… A hash recovers most of it; baking the address recovers essentially all of it."* Investigated both; shipped the hash this round, for a concrete reason found while designing the bake — recorded here so the next seat does not have to re-derive it.

`bb_call_proc_staged.cpp`'s existing bake (`x86_jmp_via_cell` / `XK_RIPCELL`, `x86_asm.h:665`) works because it is a **tail-jump into a known procedure entry**: BINARY dereferences the compiler-process-local `g_ab_fn_cells[idx]` cell directly (safe — m3 compile and run share one process, so a compile-time pointer stays valid at that same process's runtime); **TEXT mode does not use the cell at all** — it emits a direct `lea rax,[rip+<name>_α]; jmp rax`, because within one `.s` compilation unit the label is always resolvable by the assembler. TEXT-mode calls therefore never needed the cell to begin with.

`bb_match_defer.cpp`'s `*<name>` deferred-pattern-reference site needs **more than a tail-jump**: `rt_defer_get_pat_dtp`'s star-branch wraps the call result (`rt_dtx_drain`, a `DT_P`-payload check, and a park-into-`g_spk` fallback on miss) before it can be used. A bake mirroring `bb_call_proc_staged.cpp` verbatim cannot provide that wrapping — it would need a **new runtime entry point**, and BINARY and TEXT need genuinely **different** bake strategies (BINARY: bake the `g_ab_fn_cells[idx]` cell address, same as today, just computed once at compile time instead of re-derived per call; TEXT: `g_ab_fn_cells` has no linkable symbol across the process boundary a separately-linked `m4` binary crosses, so TEXT would instead have to bake the `<name>_α` label address directly, the same trick `x86_jmp_via_cell`'s TEXT arm already uses, and skip the cell layer entirely) — real design and encoder work on a subsystem with an extensive history of subtle pattern-matching correctness bugs (this goal file's own `LIVE CURSOR` history is mostly about exactly this file's neighbors). Concrete next-step sketch, so this is a scoped rung and not a vague TODO:

1. Extract `rt_defer_finish_star(varname, DESCR_t r)` from `rt_defer_get_pat_dtp`'s existing star-branch body — pure, mechanical, behavior-preserving.
2. Add `rt_call_proc_descr_baked(void **cell, const char *name, int nargs)`: try `*cell` first (mirrors `rt_dyn_alpha_fn`'s existing validity check — non-null, not the undef stub), fall back to today's `rt_call_proc_descr(name, nargs)` unchanged when the cell isn't sealed yet.
3. In `bb_match_defer.cpp`'s non-GVA branch (today's lines ~140–150), for BINARY, bake `bb_ab_fn_cell_ptr(("alpha$"+bare_name).c_str())`'s address into a register the same way the file's *own* existing `g_sno_defer_cells` cache already loads a known address (`x86("lea", reg, "[rip + __]", addr, label)`, lines 60–68) — no new encoder needed. For TEXT, either bake `&<name>_α` directly (skip the cell) or leave TEXT on the (now hashed, already fast) name-string path as a partial bake.
4. Killswitch, six-script `.s`-regen byte-identity proof, full corpus regression — same discipline as this session, below.

Given the hash fix already recovers **97% of the defect's own cost** and the residual is now dominated by cheap, bounded work (hash + occasional collision probe), the bake's *marginal* win is real but small next to what a first-pass implementation risk buys on this file. Filed as the named follow-on rather than attempted blind this session.

## (4) THE FIX SHIPPED

`src/emitter/emit.cpp`, `bb_ab_slot_for` (`AB_FNCELL_MAX=1024`, `g_ab_fn_cells`/`g_ab_fn_names` — both **pre-existing**, unchanged in shape/size): replaced the `for (i=0..n) strncmp(...)` linear scan with **open-addressing linear-probe hashing over the same two arrays** (FNV-1a via new pure helper `ab_fn_hash`; empty-slot sentinel is the pre-existing zero-initialized `g_ab_fn_names[i][0]=='\0'`). **No new global variables** — `g_ab_fn_cells`/`g_ab_fn_names`/`g_ab_fn_cell_n` are the exact same three file-scope statics that existed before; only the *access algorithm* changed (same class of move RULES.md's own medium-guard history calls out: "move to where the state already lives," here "change how the existing state is addressed," not "add new state"). Contract unchanged and verified unchanged: same name → same stable slot address for the remainder of a process's life, deterministic within one run, `AB_FNCELL_MAX`-full still aborts with the original (slightly shortened to fit the 200-char margin) message. Killswitch `SCRIP_AB_HASH` (default on; `=0` reproduces the original algorithm's insertion order and probe sequence exactly — same code path, not merely equivalent behavior).

Bonus, explicitly named in the brief as a separate one-line fix, not the 43.8%: `src/runtime/rt/rt.c:rt_call_named_proc` called `getenv("SCRIP_BYNAME_ALPHA")` uncached on every invocation, unlike every other rt.c site's cached-`static int` idiom (e.g. `rt_dyn_alpha_fn`, `rt.c:851`). Extracted `rt_byname_alpha_on()` matching that exact idiom. (Touching this line also exposed that it was **already** over the 200-char margin before this session — 433 chars in the pre-patch tree; reflowed to fit while landing the cache, since the edit was already there.)

## (5) MEASURED — CALLGRIND A/B, BEAUTY SELF-HOST, m3

| | Ir | % of total |
|---|---|---|
| **BEFORE** (this session's own control build) | 27,760,640,730 | 100.0% |
| **AFTER** (hash on, default) | **15,870,550,520** | 100.0% |
| **reduction** | **11,890,090,210** | **42.83% of every instruction beauty.sno's self-host executes** |

Speedup: **1.75×** fewer instructions. Residual cost of the whole by-name mechanism in the AFTER run (`bb_ab_slot_for` self + new `ab_fn_hash` + residual `strncmp` on collision/confirm): 96,569,932 + 96,657,207 + 146,905,960 = **340,133,099 Ir (2.14% of the new total)** — down from 12,235,744,399 (44.08% of the old total): **the defect's own cost fell ~36×**. `bb_ab_fn_cell_ptr` call count unchanged at 551,979 (expected — the fix changes *how* each lookup is done, not how many happen).

Native wall-clock (this container; sandboxed, treat as directional per this campaign's own established caveat — Ir is the number of record):

| | before | after | speedup |
|---|---|---|---|
| m3 (`--run`), median of 3 | 2.41s | 1.49s | 1.6× |
| m4 (`--compile`, assembled+linked+run), median of 3 | 0.48s | 0.27s | 1.8× |

m4 was independently built (`--compile` → `gcc -no-pie … -lscrip_rt`) and run to confirm the fix helps the linked-binary path too, not just in-process m3 — it does, and by a slightly larger margin (less non-defect overhead to dilute the win in a leaner binary). Both m3 and m4 outputs stayed byte-identical to the fixed point (md5 `6f1671c0757729992ae01a6bdf16f081`) with the fix on, with the killswitch off, and against a from-scratch pre-patch control build.

## (6) KILLSWITCH — PROVEN BYTE-IDENTICAL TO TODAY, FOUR INDEPENDENT WAYS

`SCRIP_AB_HASH=0` (and the pre-patch control build, built via `git stash`):
- m3 self-host output: identical md5 across {pre-patch control, patched+hash-on, patched+hash-off}.
- m4 `--compile` TEXT output for beauty.sno: `diff` exit 0 across the same three.
- Full SNOBOL4 corpus (`test_corpus_snobol4.sh`, 357 rows): **identical pass/fail/skip sets by name** — m3 PASS=355 FAIL=2 (`160_pat_alt_inner_gen_resume`, `demo_treebank`, both pre-existing and independent of this change), m4 PASS=353 FAIL=2 SKIP=2 (`132_pat_fence_eps_recur_shallow`, `demo_porter`, same). Note for the record: the brief's DONE-WHEN cites `339/341` / `338/341+1SKIP` — those are stale; the corpus grew to 357 rows in yesterday's `demo-corpus-coverage-audit` session (this seat's own prior work). "Unchanged" is verified against the actual current baseline, confirmed identical between hash-on and hash-off on this exact tree.
- All six mandatory `.s` regen scripts (touched codegen ⇒ required per RULES.md handoff sequence): `util_regen_benchmark_s_artifacts.sh` (15/15 unchanged), `_feature_` (0 changed; 1 pre-existing unrelated EMIT-FAIL, `coverage_sno_nodes.s`, confirmed pre-existing via the same "outside the SN4-PAT subset" error on a from-scratch check), `_demo_` (12/12 unchanged), `_programs_` (623/623 unchanged; 15 EMIT-FAIL + 42 AS-FAIL, all pre-existing Prolog/Rebus gaps, unrelated to this change), `_prolog_bench_` (22/22 unchanged; 3 pre-existing AS-rejects), `_crosscheck_` (488/488 unchanged; 15 pre-existing EMIT-FAIL, all Snocone + the same coverage file). **Zero bytes moved anywhere in either corpus, twice** (once per patch — the `emit.cpp` hash and the `rt.c` getenv-cache — run separately and then combined).

## (7) INCIDENTAL, PRE-EXISTING, OUT OF SCOPE — RECORDED NOT BURIED

`scripts/test_gate_sn7_beauty_self_host.sh`'s `--compile` arm captures `scrip --compile prog.sno`'s **stdout** (which is the emitted assembly text itself) and diffs it against a `.ref` file containing expected **program output** — these can never match as the script is written; it fails PASS=17 FAIL=17 identically on a from-scratch pre-patch control build, so it is unrelated to this session's change and out of scope for this rung. `test_gate_em_beauty_subsystems_mode4.sh`, which correctly compiles→links→runs→diffs, passes 17/17 clean both before and after. Not fixed here; flagging for whoever owns that gate next.

## (8) DONE-WHEN, CHECKED AGAINST THE BRIEF

- ✅ Construct established with a witness (§1), not assumed.
- ✅ 43.8% independently confirmed (§2, 44.08% measured).
- ✅ Procedure calls resolve without a per-call **string scan** (O(1) amortized hash+probe replaces the O(n) strncmp scan). Full compile-time bake **not** taken this round — reason and concrete follow-on scope recorded (§3), per the brief's own explicit allowance.
- ✅ Killswitch arm proven byte-identical to today, four independent ways (§6).
- ✅ Callgrind A/B states before/after Ir (§5).
- ✅ Corpus unchanged (against the real current baseline, not the brief's stale citation — §6).
- ✅ This FINDING carries the numbers.

Follow-on queued in `GOAL-SNOBOL4-100.md`'s `LIVE CURSOR`: the compile-time bake per §3's sketch (est. next-biggest single-mechanism win after this one), and separately, `rt_defer_get_pat_dtp`/`rt_call_proc_descr`'s remaining `rt_proc_find` call resolves `varname+1` — a substring pointer into the `*name` literal, not the separately-interned name used at the name's own registration site — so it always misses `rt_proc_find`'s own pointer-identity fast cache (`g_proc_idx_key`) and falls to the hash lookup; small next to the fix landed here, not measured, named for whoever chases the residual 2.14%.
