# FINDING s170 (seat6, Opus 5) — B1c residue R1 ROOT-CAUSED: an m4 process never rebuilds the EMITTER's GVA registry, so the runtime fragment compiler asks `bb_scc_probe` a question the image cannot answer and TINY declines; behind that wall sits a second one — `alpha$<FN>` is unsealed for main-image procs in m4

**Front:** GOAL-SNOBOL4-100 · M1 beauty self-host · wall B1c, residue **R1** (queue row 4 `b1c-m4-seam`). Continues FINDING-2026-08-19-s168 (HQ) which cured B1c in m3 and named R1; and s164/s164b which ruled out `jmp_entry`-alone and `g_flat_frame_floor`-alone.

**Build:** `make pristine` (RC=0) at SCRIP `f44be5f1` + this fix, **RT_OPT `-O0`** (FACT RULE O0-DEV). corpus `a3604cc9`, .github `f0523ebe`. Oracle `x64/bin/sbl` — ⛔ it was **ABSENT from this seat root on arrival** and was cloned before any verdict was taken (the CLAUDE.md false-all-FAIL class); every `.ref` in `probe/b1/` was then re-confirmed oracle-identical.

## 1. The armed-arm A/B, at HEAD, before this fix
All five `corpus/probe/b1/` witnesses, both modes, both arms. `.ref` == oracle for all five (re-verified).

| witness | m3 OFF | m3 `=1` | m4 OFF | m4 `=1` |
|---|---|---|---|---|
| `b1c_cross_medium_concat_seam` | SEGV 139 | **PASS** | SEGV 139 | **SEGV 139** |
| `b1c_eval_fn_pattern_retreat` | SEGV 139 | runs clean, `match` vs oracle `nomatch` (=R2) | SEGV 139 | **SEGV 139** |
| `b1c_patvalued_formal_retreat` | SEGV 139 | runs clean, `match` vs `nomatch` (=R2) | SEGV 139 | **SEGV 139** |
| `b1_eval_pattern_defer_call` | SEGV 139 | runs clean, `match` vs `nomatch` (=R2) | SEGV 139 | **SEGV 139** |
| `b1_opsyn_binary_snodef` (green control) | PASS | PASS | PASS | PASS |

s168's m3 receipts reproduce exactly. R2 (the three `*_retreat` wrong answers) is queue row 5, another seat's lane — untouched here.

## 2. The measurement that names R1 (one gdb breakpoint, no code)
Breakpoint on `bb_tiny_shim_ok`, printing the emit-side facts `bb_scc_probe` consults, on the **same program** (`e_plain` = `P = EVAL("'x' *PC()")`, the s164 minimal isolator) under `SCRIP_B1C_PARITY=1`:

```
m3  [SHIM] fname=PC nargs=0 frag=0 gva=1 dyn=1 reg=1 sccok=1 zc=2     <- main emission
m3  [SHIM] fname=PC nargs=0 frag=1 gva=1 dyn=1 reg=1 sccok=1 zc=2     <- FRAGMENT emission -> ADMITS -> green
m4  [SHIM] fname=PC nargs=0 frag=1 gva=0 dyn=1 reg=1 sccok=1 zc=2     <- FRAGMENT emission -> DECLINES -> SEGV
```

**One bit differs: `g_gva_active`.** Everything HQ's R1 hypothesis suspected is in fact HEALTHY at m4 runtime — `rt_proc_dyn_scope`=1, `rt_proc_is_registered`=1, `scc_program_ok()`=1, `x86_zc_frame()`=ZC_FRAME_RSP. The proc table is populated in the m4 image. **`g_stage2` was not the gap.**

Second probe, at `eval_thunks_emit_from` entry in the m4 process:
```
[PRE] g_gva_active=0  gva_count()=0
```
The emitter's GVA **name registry is entirely empty**, not merely the flag.

## 3. Root cause R1 (layer 1) — the emitter's compile-time side tables do not exist in an m4 process
`bb_scc_probe` (src/templates/bb_call_proc_staged.cpp:199) gates TINY admission on two pieces of **emit-side** knowledge: `g_gva_active`, and `gva_index_of(name)` over `gva_collect.c`'s static name table. Both are built by the **driver at compile time** and neither survives into the emitted program:
- `src/driver/scrip.c:1566` sets `g_gva_active` for the m4 emit, then **`:1573` clears it to 0** before the driver exits. The flag is a compile-process artifact.
- `gva_collect.c`'s `g_gva_names[]`/`g_gva_n` are filled by `gva_collect_graph()` during compilation. Nothing repopulates them at runtime.
- In **m3** the compile and the run are ONE process (`scrip.c:1616` — `gva_register(...); g_gva_active = 1;`), so when the runtime fragment compiler re-enters the emitter for an EVAL body, the tables are still standing. **That is the entire m3/m4 asymmetry.**

Consequence: in m4, `bb_scc_probe` returns 0 → `bb_tiny_shim_ok` returns 0 → the fragment falls to the **slim/legacy call path** — precisely the pushed-landing protocol s168 convicted as the B1c SEGV. **s168's TINY gate is therefore structurally unreachable in m4: `SCRIP_B1C_PARITY=1` is INERT there, and m4-`=1` ≡ m4-OFF.** The cure was never declined by m4; it was never offered.

This is HQ's R1 hypothesis — *"TINY admission consults emit-side knowledge absent in an m4 process"* — **confirmed, with the specific knowledge named**: it is the GVA registry, not `g_stage2`.

## 4. The layer-1 fix (LANDED, killswitch `SCRIP_B1C_PARITY`, default OFF)
`src/runtime/rt/rt.c` `gva_register()` — the one funnel the m4 preamble already calls at startup (`.s` line 15: `lea rdi,[rip+__gva_names]; call gva_register@PLT`) — rebuilds the emit-side registry from `__gva_names`, the very table it is handed, and sets the flag.

**Why the indices are exact, not approximate:** the driver emits `.Lgvan<k>` in `gva_name(k)` order (scrip.c:1552–1554) and `gva_collect_var` assigns indices sequentially, so re-collecting `names[0..n-1]` in order reproduces index `k` for `names[k]` — the identical mapping the compile-time emitter used, and the same one `rt_gva_island`/`NV_bind_gva` bound the cells to. Verified: `gva_count=3 idx(PC)=0` against `.Lgvan0="PC"`.

**Why the guard `gva_count()==0` is exact:** it is the m4-runtime signature. The m3 driver only reaches `gva_register` with the table already populated (`n_gva_m3 = gva_count() > 0` is the precondition at scrip.c:1611), so the block is unreachable on the m3 path — no double-collect, no reordering, no perturbation of the arm s168 already proved.

**Receipt:** all four crashing witnesses move **SEGV(139) → Error 22** in m4 under `=1`; the green control stays green; m3 is unchanged in both arms; mode-4 `.s` is **byte-identical OFF vs ON** (md5 `bd7a504040c9535960290fcb25ae401e` both arms on `e_plain`) — blast radius 0, as the arm is runtime-`.so` only.

## 5. Root cause R1 (layer 2) — `alpha$<FN>` is never sealed for main-image procs in an m4 process
Removing wall 1 exposes wall 2, and it is a different mechanism. The TINY site reaches its callee through `x86_jmp_via_cell` on the cell `alpha$<FN>` (`bb_call_proc_staged.cpp:341`). That cell is filled by `bb_ab_seal_entry_cells` (bb_define.cpp:82), which resolves the target with **`emit_label_lookup_offset("<FN>_α")` — a lookup in the LIVE EMIT LABEL POOL.**

In m4 the callee `PC` is *statically assembled*: `PC_α` is a real label in the image (`e_plain.on.s:62`) but it is an **assembler** symbol, never an emit-pool entry, and `m3_seal_entry_cells` is called only on the m3 driver path (scrip.c:1682/1814). So `alpha$PC` still holds `rt_ab_undef_fn_stub` when the fragment's TINY site jumps through it — **`** Error 22 ... Undefined function called`**, the D-18a signature arriving from the opposite side: D-18a sealed the *fragment's own* thunks; nothing seals the *main image's* procs for a fragment consumer.

## ⛔ 5b. THE OBVIOUS FIX FOR WALL 2 WAS BUILT AND IS FALSIFIED BY TEST — do not spend a session re-deriving it
The natural move is "have the m4 preamble publish `&<FN>_α` into the cell". **I implemented it and it is WRONG.** Built: a runtime helper `rt_b1c_seal_alpha(name, addr)` filling `bb_ab_fn_cell_ptr("alpha$"+name)` (same process, same table the fragment compiler will ask — cell identity exact), plus a killswitch-gated emission in the SNOBOL4 mode-4 preamble (`scrip.c` beside its `gva_register` line, using the `prolog_op_user` rodata/text-switch idiom). Two measured results killed it:

1. **`EXPR$<n>` / `PAT$<n>` have NO statically assembled α.** They are the *runtime-built* fragment thunks, so referencing their label is a hard link error — measured verbatim: `undefined reference to \`EXPR$0_α'` / `PAT$0_α`. Any such loop MUST exclude `$`-bearing proc names. (Two of the five witnesses went `BUILDFAIL` on exactly this.)
2. **With those excluded so all five link, sealing the real α makes it WORSE:** all four crashing witnesses go **Error 22 → SEGV(139)** in m4. The seal works — the jump now genuinely reaches the statically-assembled `<FN>_α` — and *the crossing itself crashes*. **Error 22 was the SAFE failure**, the cell's undefined-stub guard doing its job.

**What that proves:** wall 2 is not "the cell is empty". It is that **a fragment-emitted TINY site cannot speak the record/landing protocol to a statically assembled callee** — the sig-record pointer rides `rcx` from the RX slab into a callee whose entry was assembled under the main image's regime, and the landing does not hold. Filling the cell only removes the guard that was catching it.

**Reverted; the tree at this FINDING's HEAD carries layer 1 only** (`git status` clean against `dbb6b98d`). This is the same discipline as s164/s164b, which banked `jmp_entry` and `g_flat_frame_floor` as ruled-out — three hypotheses on this wall are now eliminated by test rather than by argument.

## 6. Corpus A/B and blast radius (pristine build, `-O0`, `test_corpus_snobol4.sh`, 337 programs)

| arm | mode-3 | mode-4 | fail-set delta vs OFF |
|---|---|---|---|
| **OFF (default)** | PASS=325 FAIL=12 | PASS=322 FAIL=13 SKIP=2 | — (⚑ **exactly the HQ board watermark** m3 325/337 · m4 322/337 ⇒ this patch is inert at default, measured, not asserted) |
| **`SCRIP_B1C_PARITY=1`** | **PASS=326** FAIL=11 | PASS=322 FAIL=13 SKIP=2 | **one line, in the good direction**: `141_pat_eval_double_fn_arbno` FAIL→PASS in m3. **Zero regressions, either mode.** |

`141_pat_eval_double_fn_arbno` is an EVAL-built-pattern program — the B1c family — so the armed arm converting it is the cure working, not noise.

**RULES step-4 (`.s` regen) is a structural no-op for this session, proven not assumed.** The change lives inside `gva_register`, a *runtime* function. Under gdb with a breakpoint on it, `./scrip --compile` on the seam witness records **0 hits** and exits normally — the function is unreachable on the compile path, so no emitted byte can depend on it. Corroborated directly: `e_plain` mode-4 `.s` md5 is identical OFF vs ON.

**SNOBOL4 crosscheck A/B (`test_crosscheck_snobol4.sh`, the primary harness feed):**

| arm | `--run` | `--compile` | DIVERGE (m3≠m4 vs ref) |
|---|---|---|---|
| **OFF (default)** | PASS=307 FAIL=10 | PASS=306 FAIL=10 SKIP=1 | **0** (⚑ exactly the s167 recorded watermark ⇒ default inert) |
| **`=1`** | **PASS=308** FAIL=9 | PASS=306 FAIL=10 SKIP=1 | **1** — `141_pat_eval_double_fn_arbno` |

## ⛔ 6b. THE FLIP SEAT MUST READ THIS: the armed arm BREAKS m3 ≡ m4 until layer 2 lands
`SCRIP_B1C_PARITY=1` takes SNOBOL4 crosscheck DIVERGE from **0 → 1**. The cause is R1 itself, not a new defect and not this patch: the s168 cure lands in m3 and **cannot** land in m4, so `141_pat_eval_double_fn_arbno` passes m3 and fails m4 — a one-program breach of the **m3 ≡ m4 design invariant**. (This divergence is a property of the s168 arm, not of the layer-1 fix: with or without it the program fails m4 under `=1`; the fix only changes *how* it fails, SEGV → Error 22. The DIVERGE count is 1 either way.)

**Bearing on queue row 3 (`b1c-flip`):** the arm is a clear net win on the numbers (m3 corpus +1, m3 crosscheck +1, zero regressions anywhere, both media) but flipping the DEFAULT on today ships a standing m3/m4 divergence. Recommendation, HQ's call: either flip and record `141_pat_eval_double_fn_arbno` as a known DIVERGE ratchet until B1c-R1b, or hold the default OFF until layer 2 closes the seam and the invariant is restored. **Not this seat's decision — routed, with the number.**

**Gates green at HEAD+fix:** `test_gate_template_medium_invisible.sh` (BOTH-MEDIUM guard sites **29**, at the ratchet ceiling — not grown) · `test_gate_emit_no_lang.sh` (LANG-BLIND OK).

**No new globals.** `g_gva_active`, `gva_collect_var`, `gva_count` all pre-exist; this rung adds none (FACT RULE NO-NEW-GLOBALS).

## 7. Next rung, named — **B1c-R1b: make the fragment→main-image TINY crossing land**, NOT "seal the cell"
§5b closes the cheap road. The rung is the *protocol*, and the ASM-DIFF-FIRST move is already set up for whoever takes it: build the seal arm from §5b (it is ~15 lines and reproduces the SEGV on demand), then diff the emitted `<FN>_α` entry in the m4 `.s` against the m3 in-memory `<FN>_α` the same call reaches when it works, and find which entry-regime assumption the RX-slab caller violates. Two outcomes are acceptable and both close the seam:
- **(a) fix the landing** so a fragment TINY site may call a statically assembled proc; or
- **(b) admit TINY only for same-medium callees** — let a fragment site decline TINY for main-image procs *by callee medium* rather than by the blanket `g_rt_fragment_emit` D-18b flag, and fix the slim/legacy pushed-landing path that it then falls to (the mismatch s168 convicted). (b) may be the smaller correct rung: it restores m3 ≡ m4 by making both media use a path that works, instead of extending a path that does not.

**Also owed, cheap, and independent:** the `SCRIP_B1C_PARITY=1` **DIVERGE 0 → 1** in §6b is a live m3/m4 invariant breach that the `b1c-flip` seat must weigh before flipping the default.

**Acceptance witness for the rung** (HQ, s170 census): `printf 'START\n' | <beauty m4 binary>` beautifies oracle-identically. At this HEAD it prints `Parse Error` in both arms — unchanged by layer 1, as expected: layer 1 removes the *crash*, and beauty's m4 wall is the F-path of the same unlanded crossing.

---

## ⛔ ADDENDUM (same session, after the `b1c-flip` seat landed `c6245f60`) — the arm went DEFAULT ON under this rung, and §6b's warning is now shipping

Sequence, for the record: this rung landed layer 1 at SCRIP `dbb6b98d` **default OFF**; the `b1c-flip` seat then landed `c6245f60` *"FLIP SCRIP_B1C_PARITY DEFAULT ON — 9 movers / 1024 programs, every one crash→better, ZERO regressions"*, flipping the **three s168 sites** — but not the **fourth site this rung had just added**. Unset therefore meant **"m3 armed, m4 half-armed"**: m3's fragment admitted TINY while m4's still answered `gva=0` and declined — i.e. the R1 root cause shipping at the default.

**Resolved at SCRIP `3a4ca273`:** this rung's site flipped to match, so `SCRIP_B1C_PARITY` is ONE coherent switch again (`=0` disarms all four). Re-measured pristine at `c0efe346`+flip, armed vs disarmed:

| | corpus m3 | corpus m4 | crosscheck m3 | crosscheck m4 | DIVERGE |
|---|---|---|---|---|---|
| disarmed (`=0`) | 326 | 322 | 308 | 306 | 1 |
| **armed (new default)** | **326** | **322** | **308** | **306** | **1** |

**Zero count movement.** Icon smoke 14/14 both modes; Prolog smoke 3/5 (its recorded watermark). The gain is qualitative and is exactly `c6245f60`'s own bar: the four m4 B1c witnesses go **SEGV(139) → a clean Error 22**.

**⛔ §6b IS NOW LIVE, NOT HYPOTHETICAL:** SNOBOL4 crosscheck **DIVERGE=1** (`141_pat_eval_double_fn_arbno`, passes m3 / fails m4) is now the SHIPPING default — a standing breach of the **m3 ≡ m4** invariant. It is caused by R1's unfixed wall 2, not by either flip. **It closes when B1c-R1b lands, and until then it should be carried as a named DIVERGE ratchet rather than silently absorbed.**

## Answers owed to HQ on the two witnesses it routed
- **`beauty_suite/semantic_driver.sno` — NOT cured by R1, in either arm.** Measured: m3 **PASS 8/8**; m4 prints `PASS: 1/2/3` then **SEGV(139)** at test 4, byte-identical armed and disarmed. By HQ's own stated criterion this is a **distinct wall** and wants its own row.
- **`probe/b1/b1_apply_snodef_target.sno`** (minted by another seat during this rung) — same verdict: m3 PASS, **m4 SEGV(139) both arms**, untouched by R1.
- **beauty tiny-input** — `printf 'START\n' | beauty-m4` still prints `Parse Error` + raw echo (oracle: `START`), unchanged, as expected: layer 1 removes the *crash*, and beauty's m4 wall is the F-path of the still-unlanded crossing (wall 2).
- **Witness-set note:** `probe/b1/` held exactly the **five** witnesses HQ enumerated when this rung was locked; other seats have since grown it to **nine** (`e_plain`/`m_plain` checked in as real witnesses, plus the two `apply` witnesses). All nine are graded in the tables above.

---

## ⛔ ADDENDUM 2 (HQ answer RE `b1c-m4-seam`, same session) — ROUTING OF THE RESIDUE, and the COLD-START for queue row 5 `m4-fragment-landing`

HQ's ruling on this rung, on the record: **(1)** the uniform-polarity flip `3a4ca273` is **AFFIRMED** (HQ-59 cursor) — `c6245f60` had left *unset* meaning **m3-armed / m4-half-armed**, i.e. the R1 root cause shipping at the default; the flip meets that commit's own bar (zero count movement, four witnesses SEGV→Error 22). **Do not revert it.** **(2)** Both not-cured walls are routed to their own rows (below). **(3)** The rung completes as **investigation + layer-1**; layer 2 is a different rung and a different seat.

### Residue list — every unclosed thing this rung produced, with its owning row

| # | residue | verdict at this HEAD | owning queue row |
|---|---|---|---|
| R1b | **the fragment→main-image TINY landing protocol** (wall 2, §5 + §5b) | four witnesses reach a clean **Error 22**; sealing the cell makes it **SEGV** | **NEW row 5 `m4-fragment-landing`** — cut from this FINDING's §7(a)/(b) framing; cold-start below |
| — | `beauty_suite/semantic_driver.sno` **test 4** | m3 **PASS 8/8**; m4 prints `PASS: 1/2/3` then **SEGV(139)**, byte-identical armed and disarmed | same row 5 (it is the acceptance witness that is *not* in `probe/b1/`) |
| — | `probe/b1/b1_apply_snodef_target.sno` | m3 PASS, **m4 SEGV(139) both arms**, untouched by R1 | **row 25 `apply-snodef-m4`** — the s156 class, now with seat4's 3-line repro (BM-2). ⛔ **Not** row 5: APPLY/by-name dispatch to a SNOBOL-defined target is a *dispatch* wall, not the fragment seam |
| — | **`DIVERGE=1` at the shipping default** — `141_pat_eval_double_fn_arbno`, m3 PASS / m4 FAIL | a standing breach of the **m3 ≡ m4** design invariant, caused by wall 2, **carried as a NAMED breach**, not silently absorbed | **row 13 `pat-eval-double-fn-arbno`**. ⛔ **seat1 independently hit the same program from the other side**: it is also an **INTERMITTENT, load-dependent m3 `rc=139`**, the false-mover that burned seat1's `util_out_sweep` (it survives both of that script's existing cures, and manufactures a false mover in *either* direction). Two faces, one program — **row 13 must root-cause both, or prove them one class** |
| — | R2, the three `*_retreat` wrong answers | out of scope here | closed by seat7 at `97ad2912` (`SCRIP_CAP_NAME_STRICT`, DEFAULT OFF) — and seat7's minimal witness has **no EVAL and no fragment** yet still SEGVs in m4, so the fragment hypothesis is not the whole story for row 5 |

### COLD-START for row 5 `m4-fragment-landing` — first step, verified at HEAD `3a4ca273`

ASM-DIFF-FIRST per RULES.md. The set-up this rung banked is the **repro arm**, not a fix; rebuild it, then diff.

1. **Witness.** `corpus/probe/b1/b1c_e_plain.sno` (`P = EVAL("'x' *PC()")`, the s164 minimal isolator). Full set: the nine `probe/b1/` witnesses + `corpus/programs/snobol4/beauty_suite/semantic_driver.sno` (test 4).
2. **Rebuild the falsified seal arm — it reproduces the SEGV on demand** (~15 lines; §5b). Runtime helper `rt_b1c_seal_alpha(name, addr)` filling `bb_ab_fn_cell_ptr("alpha$" + name)`; emit it into the SNOBOL4 mode-4 preamble in `src/driver/scrip.c` beside its `gva_register@PLT` line (**:1487**, the SNOBOL4 arm; **:1305** is the Icon twin — do not touch it), using the `prolog_op_user` rodata/text-switch idiom. ⛔ **The loop MUST exclude `$`-bearing proc names** — `EXPR$<n>`/`PAT$<n>` are the *runtime-built* fragment thunks and have no statically assembled α; referencing the label is a hard link error (measured: ``undefined reference to `EXPR$0_α'``).
3. **The diff.** Compare the **m4 statically assembled `<FN>_α` entry** (`./scrip --compile -o e.s corpus/probe/b1/b1c_e_plain.sno < /dev/null`, then read `PC_α` — it was `e_plain.on.s:62`) against the **m3 in-memory `<FN>_α`** the same call reaches *when it works* (`./scrip --dump-bb`, and the live bytes at the `alpha$PC` cell target). The question is narrow: **which entry-regime assumption does the RX-slab caller violate?** The sig-record pointer rides **`rcx`** from the slab into a callee assembled under the main image's regime. An instruction byte-identical across both is exonerated (RULES.md).
4. **Only then gdb** — the caller is `bb_call_proc_staged.cpp` **:341 / :621** (`x86("jmp","[rip@cell + __]", bb_ab_fn_cell_ptr("alpha$"+name))`); the m3 authority that fills the cell is `bb_define.cpp:82 bb_ab_seal_entry_cells`, called only from `scrip.c:1682/1721/1814` (m3 path) and `runtime_eval.c:249` (fragment path) — **never for main-image procs in m4**, which is the whole asymmetry. Use `CSN_NO_SEGV_HANDLER=1`; hardware watchpoints do not work in this container.

**Two acceptable outcomes, both close the seam** (unchanged from §7): **(a)** fix the landing so a fragment TINY site may call a statically assembled proc; or **(b)** admit TINY only for **same-medium callees** — decline by *callee medium* rather than by the blanket `g_rt_fragment_emit` D-18b flag — and fix the slim/legacy pushed-landing path it then falls to. **(b) is likely the smaller correct rung: it restores m3 ≡ m4 by making both media use a path that works, instead of extending one that does not** — and it is the move that retires the `DIVERGE=1` breach in row 13's first face.

**Already eliminated by test — do not re-derive** (five hypotheses now dead on this wall): `jmp_entry`-alone (s164) · `g_flat_frame_floor`-alone (s164b) · `g_stage2` (§2, this rung) · "the emitter's GVA registry" (**cured**, §4 — layer 1, landed) · **"just seal the `alpha$<FN>` cell"** (§5b — built, measured, WORSE).
