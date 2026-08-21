# FINDING — s193 (seat4, Claude Opus 5): the m4 image was never told where `<FN>_α` lives, so EVERY by-name route to a DEFINE'd function jumped through the generic entry thunk — and the seal was deleted by a ruling about something else

**Front** GOAL-SNOBOL4-100 · M1 beauty self-host · wall **B1** · **queue row `apply-snodef-m4` (rank 25)**
**Landed** SCRIP `99cd7ede` · corpus `07bd862e` · .github this commit
**Build discipline** every number below is from `make pristine` (HQ-27) at the stated commit, **RT_OPT `-O0`** (FACT RULE O0-DEV). Oracle `x64/bin/sbl` present and used under **`-bf`** (RULES.md ONE ORACLE AUTHORITY).

---

## 1. The brief's premise held, and the 3-line repro was exact

FINDING-s170 §2b handed this row a live repro: `APPLY('ADD1', 5)` to a **SNOBOL-defined** target
SEGVs in m4 while `APPLY('SIZE','abcd')` (built-in target, *same dispatch call*) is green. Both
reproduced verbatim at pristine SCRIP `c512089a`. Nothing in the brief was stale.

---

## 2. Root cause, established with three independent instruments

**`rt_call_proc_descr`** (reached from `by_name_dispatch.c:6958`, the `BID_APPLY` arm) enters a
`dyn_scope` callee through **`rt_dyn_alpha_fn`**, which reads the `alpha$<FN>` cell and — per
**D-18c** — correctly *declines* an unsealed one, returning the caller's fallback. The fallback is
`p->fn`, which `rt_define_site` registered as the **body-entry STATEMENT label** (`n3_statement_begin_α`),
i.e. the **generic entry thunk**. `rt_proc_enter`'s wire `jmp` cannot speak that protocol and lands wild.

In **m3** the driver seals the cell from the live emit label pool (`m3_seal_entry_cells`,
scrip.c:1682/1814). In **m4 nothing ever does.**

| instrument | measurement |
|---|---|
| **killswitch equivalence** | `SCRIP_DYN_ALPHA=0` in **m3** reproduces the m4 SEGV **exactly** on every APPLY witness, and leaves the direct-call sibling green — the differentiator is the sealed cell and nothing else |
| **gdb** | `rip = _rtld_global`, `#1 0x0` — the **verbatim** signature `rt.c:1993`'s s117 comment names for this wild jmp |
| **asm diff** (ASM-DIFF-FIRST) | the DEFINE half **and the whole `ADD1` blob** are byte-identical (number-normalized) between the green direct-call sibling and the crashing APPLY witness; the entire delta is the call statement's by-name route |

This is **FINDING-s117's named hazard arriving through the sibling it was never applied to** (s117
installed the `SCRIP_BYNAME_ALPHA` arm in `rt_call_named_proc` only), and it is **FINDING-s170 R1
layer 2 reached without an EVAL and without a fragment** — a plain main-image `APPLY` is enough.

### The ablation ladder (checked in, `corpus/probe/b1/`, every `.ref` from live `sbl -bf`)
| witness | ingredient | oracle | m3 | m3 `DYN_ALPHA=0` | m4 (before) |
|---|---|---|---|---|---|
| `b1_direct_snodef_call` | `ADD1(5)` direct | 6 | 6 | **6** | **6** ✅ control |
| `b1_apply_snodef_target` | `APPLY('ADD1', 5)` | 6 | 6 | **SEGV** | **SEGV** |
| `b1_apply_snodef_zeroarg` | `APPLY('ZERO')` | 7 | 7 | **SEGV** | **SEGV** |
| `b1_apply_snodef_varname` | `APPLY(FN, 5)` | 6 | 6 | **SEGV** | **SEGV** |
| `b1_apply_builtin_target` | built-in target | 4 | 4 | 4 | **4** ✅ control |

**Arity is not a factor. Literal-vs-variable name is not a factor. The APPLY machinery is exonerated.**

---

## 3. ⛔ THE SEAL WAS DELETED BY A RULING ABOUT SOMETHING ELSE, AND THE RULING IS STILL RIGHT

`scrip.c`'s m4 startup hoist **already** emits `lea rsi, [rip + <FN>_α]; call rt_proc_set_fn` — the
exact address the by-name route needs. Lon's **s114 STARTUP-HOIST-DELETE** skips it for every
`dyn_scope` proc, because *"you can not register these FUNCTIONS at the beginning of the program, it
must happen at the DEFINE"*. That ruling is about **REGISTRATION** and it is preserved verbatim here.

**A seal is not a registration.** This rung publishes a *static code address* at image load and
nothing else: `rt_call_proc_descr` and `rt_call_named_proc` both consult `rt_proc_find` **first** and
still fail until the DEFINE statement executes. Nothing becomes callable early. The two facts —
*"this function is now defined"* and *"its record-contract entry is at this address"* — were riding one
emission, and deleting the first correctly took the second with it.

---

## 4. ⭐ THE α FACE IS NOT ALWAYS EMITTED, AND THE LINKER IS THE ONLY HONEST ORACLE FOR THAT

`<FN>_α` exists **only where the TINY shim is admitted**. `1010_func_recursion` emits its DEFINEs
inline in the shared chain and has **no `fact_α` at all** — and it *passes* in m4 without one, because
where no α face exists the pre-fix fallback was already correct.

The driver **cannot ask the live label pool**: a proc blob's pool is retired long before
`module_init` emits at the bottom. So the **linker** answers instead — `.weak <FN>_α` plus a
**`@GOTPCREL`** load yields `rsi=0` for a face that was never emitted, and `rt_proc_seal_alpha`'s
`!fn` guard turns that into a no-op.

⛔ **The obvious spelling is the one a PIE refuses.** A plain `lea rsi, [rip + <FN>_α]` on a weak
undefined symbol is an `R_X86_64_PC32` against an undefined symbol — *"can not be used when making a
PIE object"*. **Measured, not predicted:** that first spelling turned `1010_func_recursion` from
**PASS into SKIP(compile/link)**, and it was caught only because the corpus runner's SKIP count moved
1 → 2 while PASS moved +4 against 5 cures. **A cure count that does not reconcile with the pass
count is hiding a regression** — the SKIP lane is where a link failure goes to be silent.

---

## 5. The fix (SCRIP `da4d1252`), killswitch `SCRIP_M4_ALPHA_SEAL`, DEFAULT ON

* `src/runtime/rt/rt.c` — new leaf `rt_proc_seal_alpha(name, fn)`: `*(void**)bb_ab_fn_cell_ptr("alpha$<name>") = fn`, guarded on `!name || !fn`. **No new global variable** — it writes an existing cell through the existing allocator.
* `src/driver/scrip.c` — at the `dyn_scope` skip inside `emit_module_init_body`, emit the seal *only* (`.weak` + `@GOTPCREL` + call). Guarded off `LBL__` rows and `$`-bearing thunk names.

**Three files, 10 insertions, 1 deletion.** m3 is untouched by construction (the emission is TEXT-only
driver preamble; the new runtime leaf has no m3 caller) **and by measurement** (§6).

---

## 6. Measured — A/B is the killswitch on ONE build, both arms at one commit

| board | OFF (pre-fix) | ON | Δ |
|---|---|---|---|
| corpus **m4** | 332 / 7 · SKIP 1 | **337 / 2 · SKIP 1** | **+5**, zero new reds |
| corpus **m3** | 339 / 1 | 339 / 1 | **unchanged** |
| crosscheck **m4** | 315 / 4 · SKIP 1 | **318 / 1 · SKIP 1** | **+3** |
| crosscheck **m3** | 319 / 1 | 319 / 1 | **unchanged** |
| crosscheck **DIVERGE** (m3≠m4) | **3** | **0** | a MODE34-IDENTICAL win |
| bench suite | `indirect_dispatch` XFAIL:CRASH | **ok=15 bad=0 xfail=0 xpass=0** | row's DONE-WHEN met |

⛔ **RE-PROVED AFTER THE REBASE, PRISTINE, AT THE MERGED HEAD.** Four other seats' commits landed
beneath this one during the session (`c7560c6b` goto-code-object-parse, `3f0dc46a` opsyn-3arg,
`eef7fec9` prototype-spelled-twice, `c52f3529` alt-arb-bal-witness — 16 files, ~1000 lines — and then `c43d8f51` FENCE1-DEPTH on a SECOND rebase), so the
board above is **not** the pre-rebase measurement quoted forward: it is a fresh `make pristine` at
`da4d1252` with **both arms at that one commit**. The absolute numbers rose with the merged baseline
(340 corpus rows, up from 337); **every delta is identical to the pre-rebase measurement.**

**Cured BY NAME:** `expr_eval` · `140_pat_eval_double_fn_trick` · `141_pat_eval_double_fn_arbno` ·
`semantic_driver` · `demo_claws5`. The DIVERGE set that went 3 → 0 is exactly the first three.
⭐ **`semantic_driver` and `demo_claws5` are beauty-family** — `semantic.inc` IS the OPSYN grammar
engine FINDING-s156 named as the B1 beauty blocker.

**KILLSWITCH BYTE-IDENTITY, at scale:** `SCRIP_M4_ALPHA_SEAL=0` regenerates the checked-in `.s`
**byte-identically on 213 / 213** comparable programs — **0 movers**. ON moves **36 of 215** (every
program carrying a `dyn_scope` DEFINE); that is the regen debt and it is paid in this session's
RULES step-4 sweep.

**Gates green:** `emit_no_lang` · `template_medium_invisible` · `icn_no_stack` · `icn_semicolon_required`.
Smokes: snobol4 / icon / rebus green. ⛔ **prolog and snocone smokes are RED in BOTH ARMS** with
identical verdict lines — **pre-existing, not this rung**, said out loud rather than left for the
next seat to attribute to the newest commit.

---

## 7. ⛔ NOT MINE, MEASURED AND SAID OUT LOUD

`mixed_workload` also XPASSes — **and it XPASSes with the killswitch OFF too.** All four
`corpus/probe/mwseg/` witnesses are green in **both** arms, so the s170 §2a three-ingredient m4 SEGV
class was closed by an **earlier rung**, not this one. Its `.xfail` is retired as **stale by
measurement**, with the attribution stated rather than absorbed into this rung's cure count.
`probe/mwseg/` stays checked in as that class's regression guard.

---

## 8. Owed / open

1. **`rt_call_proc_direct` is the third by-name path and is still unsealed-blind** — `rt.c:2006` carries an explicit *"s117 SUSPECTED TWIN, NOT LANDED"* comment saying it has the same generic-entry-thunk hazard, and this session minted no witness that reaches it. Left verbatim rather than changed blind, exactly as its comment asks. A queue row, not a drive-by.
2. **`$FN(X)` is a DIFFERENT class and it is still divergent.** Measured this session: oracle says `ERROR 022 -- undefined function called`; SCRIP says `** Error 5 ... Undefined function or operation` in **all three arms** (m3, m3-α0, m4). Both are errors, so no board shows it; the error-number/text divergence is a standing global class, untouched here. Worth noting because the *original* 2026-06-20 `indirect_dispatch` xfail premise was about this form.
3. **The 36 moved `.s` are this session's regen debt** (RULES step-4), paid at handoff.
