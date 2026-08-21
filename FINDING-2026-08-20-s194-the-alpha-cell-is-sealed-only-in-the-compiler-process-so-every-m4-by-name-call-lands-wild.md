# FINDING — s194 (seat5 `/home/claude5`, Claude Opus 5; queue row `semantic-driver-m4-segv`, rank 1)
# ⭐⭐⭐ THE `alpha$<FN>` CELL IS SEALED ONLY IN THE COMPILER PROCESS, SO **EVERY** BY-NAME CALL TO A DEFINE'd PROC IN MODE 4 ENTERS THROUGH A THUNK ITS OWN COMMENT NAMES AS THE WRONG PROTOCOL.

**LANDED: SCRIP `f722e70e` · corpus `d16055da`.** `make pristine` EXIT=0 before every verdict (three times: control, patched, re-proof), RT_OPT `-O0`. Gates green: `template_medium_invisible` **0** (ceiling 0) · `emit_no_lang`. Killswitch `SCRIP_M4_ALPHA_SEAL=0`.

## THE ROW'S ANSWER, IN ONE LINE
`semantic_driver` m4 is **byte-identical to its `.ref`**, and `beauty_suite` is **17/17 in BOTH modes** — DOD item 2 of `GOAL-SNOBOL4-100` closed. The board moved **m4 331/8 → 336/3**, m3 untouched at 338/2, **zero new reds**, fail-set a strict subset.

## ⛔ THE FIRST FACT IS A DIAGNOSTIC TRAP: "ZERO OUTPUT" WAS A LOST STDIO BUFFER
The brief (and every prior reading) recorded `semantic_driver` m4 as SIGSEGV with **no output**, which reads as "dies before it starts". It does not. Under `stdbuf -o0` the binary prints **PASS 1, 2, 3** and dies in test **4**. Redirected stdout is block-buffered and a SIGSEGV discards the buffer, so the crash *looked* three tests earlier than it is. ⭐ **Never localise a SIGSEGV from redirected stdout — re-run it unbuffered first.** Tests 1–3 take `DATATYPE(nPush())`; test 4 is the first that **matches** the pattern. That single observation moved the search from "startup/include" to "the deferred-capture transfer" and is what made the ablation cheap.

## THE MECHANISM — TWO LAYERS, AND ONLY THE SECOND IS THE BUG
**Layer 1 (why arity selects the road).** `nPush()` returns `epsilon . *PushCounter()` — SPITBOL's value-assignment `.` with a *deferred* right operand. The lowerer treats the two arities differently, visible in the emitted `.s` as the assignment-target STRING:
- **arity ≥ 1** → the call is lifted into a thunk; target string is `*EXPR$0`, a compiled chain with a registered entry. `.S0: .string "*EXPR$0"`.
- **arity 0** → **no thunk is built**; target string is the bare name `*Zero`. `.S0: .string "*Zero"`.

`rt_dcap_pump` (`pattern_match.c:712`) sees the leading `*` and hands the name to `rt_call_proc_descr(name, 0)` — the **by-name** road. Only the zero-argument form ever gets there.

**Layer 2 (the defect).** `rt_call_proc_descr`'s dyn arm asks `rt_dyn_alpha_fn`, which reads the `alpha$<FN>` cell:
- non-NULL ⇒ `rt_tiny_record_enter(afn, nargs)` — the **staged rcx-record contract** the emitted `<FN>_α` blob actually speaks (`[rcx+0]`=nargs, `[rcx+8]`=γ cont, `[rcx+16]`=ω cont).
- NULL ⇒ falls through to `rt_proc_enter(p->fn)`, and `p->fn` from `rt_define_site` is the generic label-chain entry. `rt_dyn_alpha_fn`'s OWN comment names this: *"the generic entry thunk (rt_goto_transfer into a label chain, **wrong protocol for emitted bodies — rip=5 crash class**)"*.

⛔ **And that cell can only ever be sealed in the compiler process.** `bb_ab_seal_entry_cells` resolves the address with `emit_label_lookup_offset` — the **live emitter label pool** — and its only callers are `src/driver/scrip.c` (3 sites) and `runtime_eval.c`. A **linked m4 binary has neither a driver nor a label pool**. Measured: `grep -c 'alpha\$' <any emitted .s>` = **0**. So in mode 4 the cell holds `rt_ab_undef_fn_stub` for **every** proc, the guard rejects it, and every by-name call takes the wrong-protocol fallback. gdb: `rt_call_proc_descr(name="Zero", nargs=0)` → **rip = 0x1**.

⭐ **m3 is not "more correct" — it is the SAME process.** `m3_seal_entry_cells` runs right after each `emit_chain`, pool live, so the cell holds the JIT `Zero_α` and the correct `rt_tiny_record_enter` arm is taken. **The two modes were never running the same code here.**

## THE PROOF CAME BEFORE THE PATCH
Under gdb, breaking at `rt_call_proc_descr` **entry** and hand-storing `Zero_α` into `bb_ab_fn_cell_ptr("alpha$Zero")` makes the unmodified m4 binary print the correct answer and exit 0. (Poking the same cell at line 908 — *after* the dyn arm had already been skipped — moves the crash from `rip=1` into `Zero_γ` instead of curing it, which is what proves the seal must be present **before** the arm is chosen, not merely present.)

## ⛔ THIS IS NOT A CORNER — IT IS THE MANUAL'S OWN WORKED EXAMPLE
**SPITBOL manual v3.7 p.136–137**, the published `NRETURN` + deferred-evaluation idiom:
```
'ABCDE' ? LEN(2) . *PUSH() 'D' LEN(1) . *PUSH()
```
*"the calls to PUSH() are deferred until assignment takes place"* — a **zero-argument** call as the target of `.`. Run verbatim: `sbl -bf` **`n=2 [1]=BC [2]=E`**, m3 identical, **m4 SIGSEGV**. It is also exactly the shape `counter.sno`/`semantic.sno` are built from, which is why this sits on beauty's road (`beauty.sno:225 Parse = nPush() ARBNO(*Command) (...) nPop()`).

## THE WITNESS SET (all share ONE preamble; only the pattern line differs — `corpus/probe/m4alpha/`)
| witness | pattern | m3 | `sbl -bf` | m4 before | m4 after |
|---|---|---|---|---|---|
| `x3` | `LEN(1) . *Zero()` | ok | ok | **rc=139** | ok |
| `x4` | `LEN(1) . *One(1)` | ok | ok | ok | ok |
| `x5` | `LEN(1) . *Two(1,2)` | ok | ok | ok | ok |
| `w6` | `epsilon . *n` (deferred **variable**) | ok | — | ok | ok |
| `w8` | `*Zero()` alone (**no** `.`) | ok | — | ok | ok |
| `w10` | `epsilon . *(n = n + 1)` (deferred **expr**) | ok | ok | ok | ok |
| `man` | the manual's p.136 `PUSH()` example | ok | ok | **rc=139** | ok |

⭐ **The oracle agrees with m3 on every row**, so m4 was the only wrong arm and "match m3" and "match sbl" are the same target here.

## THE CURE — ONE STORE, TWO ROUTES, AND THE PREDICATE WAS ALREADY WRITTEN
`bb_ab_seal_alpha(pname, alpha)` (`bb_define.cpp`, beside `bb_ab_seal_entry_cells`) is the **same** cell store reached with the address **already resolved** instead of via the label pool. The DEFINE bind site (`bb_define_bind`, role 6 — where `rt_define_site` already registers, per Lon's s114 *"it must happen at the DEFINE"*) emits a call to it with the assembler-resolved `<FN>_α`. Two guards, neither invented here:
1. **`!bb_ab_cell_addr(fname)` — ASK THE ALLOCATOR, NOT THE MEDIUM.** The file's own precedent at `:406`/`:474`. Non-NULL = the BINARY image, where the driver already seals; NULL = the TEXT image, the only one that needs this. **This is why m3 does not move a byte** and why the BOTH-MEDIUM ratchet stays at 0 — no `MEDIUM_*` token was added.
2. **`bb_tiny_shim_ok(fname, 0)` — the ONE AUTHORITY on whether `<FN>_α` exists.** Its own comment: *"a site may jmp `<fn>_alpha` iff this returns 1, so the shim and its consumers can never drift."* ⛔ Guessing here is not a wrong answer, it is an **undefined symbol at link** — the s112 treebank class verbatim (*"the bake predicate must equal the arming predicate"*). I hit exactly that failure once en route, from a UTF-8 double-encoding of the α in the emitted label (`Zero_Î±`); it failed **loudly at ld**, which is the right failure direction.

⛔ **NO NEW GLOBAL.** The store is the existing `bb_ab_fn_cell_ptr` cell under the existing name; the only new file-scope object is a function.

## MEASURED (pristine at every point, RT_OPT `-O0`, `test_corpus_snobol4.sh` — ⛔ **not** `scorecard_snobol4.sh`, which runs the `programs/lon/` suite RULES.md forbids)
**CONTROL BUILT, NOT QUOTED** — the corpus had grown 337→340 rows since the s193 watermark, so the recorded numbers were not a legal comparison. I stashed the patch, rebuilt pristine, and re-ran the whole board on the same tree.

| | m3 | m4 | `beauty_suite` vs `.ref` (m4) |
|---|---|---|---|
| control (pre-patch, same tree) | 338/2 | **331/8** SKIP 1 | 16/17 |
| patched | 338/2 | **336/3** SKIP 1 | **17/17** |

**m4 +5, m3 bit-for-bit unmoved, zero new reds.** Remaining m4 reds (`145_pat_left_assoc_via_arbno_fence`, `160_pat_alt_inner_gen_resume`, `demo_treebank`) are all in the control's set; the first two are m3 reds too.

**CURED, BY NAME (5):** `semantic_driver` · `expr_eval` · `140_pat_eval_double_fn_trick` · `141_pat_eval_double_fn_arbno` · **`demo_claws5`**.
⭐⭐ **`demo_claws5` is seat3's s190 row** — the brief told me to dedupe against *"a cell the COMPILER process sealed that the emitted binary never inherits"* rather than re-derive it. It was the same defect, and it fell to the same line. `140`/`141` are EVAL + deferred-call, i.e. beauty's grammar machinery.

**KILLSWITCH-CLEAN, MEASURED NOT ARGUED:** control vs patched-with-`SCRIP_M4_ALPHA_SEAL=0`, 145 programs' `--compile` md5 — **IDENTICAL, 0 movers**. Blast radius at the default: **50 of 145** `.s` move (exactly the DEFINE-bearing programs, each gaining the one seal call).

**RE-PROVED IN FULL AFTER THE REBASE MOVED SCRIP FIVE COMMITS** — including seat6's s193 `dcap-freturn-false-accept`, which edits `rt_dcap_pump`, this row's own function. Pristine EXIT=0 again; **`beauty_suite` 17/17 both modes**; `test_gate_em_beauty_subsystems_mode4` **PASS=17 FAIL=0** (it read PASS=16 FAIL=1 on `semantic_driver` for five sessions); gates `template_medium_invisible` 0 and `emit_no_lang` green. Merged-tree board: **m3 339/1 · m4 337/2 · SKIP 1**. ⛔ **THAT IS BETTER THAN MY OWN +5 AND THE SURPLUS IS NOT MINE** — `145_pat_left_assoc_via_arbno_fence` went green in both modes with the other seats' commits, not with this rung. My rung's own delta is the control-vs-patched pair above, measured on one tree: **m4 331/8 → 336/3**.

**WITNESS SET IS A LIVE INSTRUMENT** (`corpus/probe/m4alpha/`, 7 programs, `.ref` all minted LIVE from `sbl -bf` via `util_ref_mint.sh`): m3 **7/7** · m4 default **7/7** · m4 under `SCRIP_M4_ALPHA_SEAL=0` **5/7**. Exactly the two witnesses that must go red on the killswitch's off arm do; the five controls stay green in both. Checked deliberately because of s193's finding that `probe/leafsib/` had gone inert and *"fails GREEN, the direction nobody audits."*

**`.s` REGEN LADDER RUN IN RULES ORDER, ALL SIX EXIT 0** — benchmark 15 files · feature 20 · demo 6 · programs `changed=0` · prolog-bench `changed=0` · crosscheck 31. ⭐ **THE CROSSCHECK 31 WERE ATTRIBUTED FILE-BY-FILE, NOT ASSUMED**, by recompiling each under `SCRIP_M4_ALPHA_SEAL=0` and diffing against its pre-regen content: **27 mine · 1 standing drift (`rung10/1021_code_direct_goto.s`, seat7's s192 direct-goto row, never regenerated) · 3 compile-fail bomb stubs.** This is the exact hazard RULES names for this step; without the attribution the rung would have claimed a file it did not move.

## ⭐ GENERALISABLE — THE ALLOWLIST LAW, AGAIN, AND THIS TIME IT WAS A CELL
`scrip.c` already carries the warning in two comments: *"the startup replay is an ALLOWLIST, not a snapshot, so m3 passing proves nothing about m4."* Every `rt_proc_set_*` fact has a printed m4 twin **because someone was bitten**. `alpha$<FN>` had no twin, and it hid longer than the others for a structural reason worth naming: **it is not in the startup ladder's reach at all** — line 668 skips every `dyn_scope` proc, whose registration lives at the DEFINE site. **When auditing m3→m4 fact parity, the startup ladder is only half the surface; the DEFINE site is the other half.**
⭐ And the cheap general test: **a cell whose only writer resolves through the emitter's label pool cannot exist in a linked image.** `grep -c 'alpha\$' *.s` = 0 was the whole diagnosis in one command, available at any point in the five sessions this was open.

## NOT DONE HERE, DELIBERATELY
- **The arity asymmetry itself stands.** A zero-arg deferred call still takes the by-name road while an ≥1-arg one is lifted to an `EXPR$` thunk. That road is now *correct*, so this is no longer a correctness question — but two roads for one construct is a latent per-arity filter of the kind Lon's NO-PER-OP-FILTER ruling is about, and collapsing them is its own rung.
- **`rt_call_named_proc` (`rt.c:1993`)** carries the same sealed-alpha arm behind `SCRIP_BYNAME_ALPHA`; the seal makes that arm live in m4 too. Untested surface, named not measured.
- **`demo_treebank`** m4 remains red, pre-existing and unrelated (in the control set).
