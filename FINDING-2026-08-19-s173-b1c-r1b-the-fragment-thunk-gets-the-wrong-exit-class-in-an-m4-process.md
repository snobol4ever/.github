# FINDING s173 (seat1 `/home/claude1`, Claude Opus 5, queue row `m4-fragment-landing` = M1-R2 successor / B1c-**R1b**) — **THE LANDING PROTOCOL IS NOT THE CROSSING: THE m4 FRAGMENT THUNK IS EMITTED WITH THE WRONG EXIT CLASS. m3 GIVES IT A WIRE EXIT (`jmp r10`/`jmp r11`), m4 GIVES IT A C-ABI `ret` — AND THE `ret` POPS A PATTERN-MATCH FRAME SLOT THAT WAS NEVER A RETURN ADDRESS. ⭐ SEAT6'S SEAL IS NOT WRONG, IT IS INCOMPLETE: SEAL + EXIT-CLASS TOGETHER LAND THE CROSSING AND RESTORE m3 ≡ m4 ON FOUR OF THE FIVE WITNESSES.**

**Front:** GOAL-SNOBOL4-100 · M1 beauty self-host · wall B1c, residue **R1b** (queue row 5 `m4-fragment-landing`). Successor to `FINDING-2026-08-19-s170-b1c-r1-the-m4-image-never-rebuilds-the-emitters-gva-registry.md` (seat6), whose §7 set up exactly this asm diff.

**Build:** `make pristine` RC=0 at SCRIP `aaf9d96b`, corpus `1cfd4fd3`, .github `7acd8463`. **RT_OPT `-O0`** (FACT RULE O0-DEV). Oracle `x64/bin/sbl` present and proven alive before any verdict was taken (`ALIVE`, rc=0) — the CLAUDE.md false-all-FAIL class checked, not assumed.

**Method: ASM-DIFF-FIRST as RULES.md mandates, and it answered without needing the seal arm to be built in code.** No source was changed to reach this diagnosis; every measurement below is gdb on the shipped pristine build.

---

## THE ANSWER IN ONE LINE

`emit.cpp:3308` picks a graph's shared γ/ω glue with `_wire_stub = (g_emit.flat_jmp_entry && g_flat_frame_floor > 0) || …`; the runtime fragment compiler computes `g_flat_frame_floor` by **searching `g_stage2` for `main`** and taking `zls_g_region` of it — and **that source fails in BOTH modes**: an m4 image's `g_stage2` contains only the fragment's own procs (no `main` row at all), and in m3 `zls_g_region(main)` returns **−1 from the second EVAL onward**. Either way the floor is ≤ 0, `_wire_stub` is 0, and the EVAL-built `EXPR$` thunk is emitted with `bb_glue_outer_γ/ω` (`mov eax,DT_S; ret`) instead of `bb_glue_wire_γ/ω` (`jmp r10` / `jmp r11`).

⭐ **The m3 half of that was NOT known when this rung opened** — it was found by landing the fix, and it is why the cure moves the m3 board too (§11).

---

## 1. Baseline at HEAD (pristine, default arm), all nine `probe/b1/` witnesses

| witness | m3 | m4 |
|---|---|---|
| `b1c_e_plain` | PASS | **Error 22** |
| `b1c_m_plain` (main-built control) | PASS | PASS |
| `b1c_cross_medium_concat_seam` | PASS | **Error 22** |
| `b1c_eval_fn_pattern_retreat` | DIFF (=R2) | **Error 22** |
| `b1c_patvalued_formal_retreat` | DIFF (=R2) | **Error 22** |
| `b1_eval_pattern_defer_call` | DIFF (=R2) | **Error 22** |
| `b1_opsyn_binary_snodef` (green control) | PASS | PASS |
| `b1_apply_snodef_target` | PASS | **SEGV 139** |
| `b1_apply_builtin_target` | PASS | PASS |

Reproduces seat6's post-layer-1 matrix exactly.

## 2. The asm diff that names it (RULES step 2), and the pair that makes it sharp

`*PC()` compiles to an `EXPR$` **thunk** in both witnesses. In `b1c_m_plain` the thunk is *statically assembled* (m4 PASSES); in `b1c_e_plain` the identical thunk is built by the **runtime fragment compiler** (m4 fails). Same callee `PC`, same pattern — only the thunk's emission context differs.

**The m4 static thunk's TINY site (works)** — `b1c_m_plain.s:9`:
```
n1_call_α:  sub rsp,16 ; lea rcx,[rip+.Lsig6z] ; lea rax,[rip+PC_α] ; jmp rax
```
**The m4 runtime thunk (crashes)** reaches the same callee through `x86_jmp_via_cell`'s BINARY arm — `movabs rax,<cell>; mov rax,[rax]; jmp rax` — and the cell is `rt_ab_undef_fn_stub` (= seat6 §5, Error 22).

⭐ **Forcing the crossing (gdb: redirect `rip` to `PC_α` with the fragment's own register state, i.e. seat6's seal arm with zero code) reproduces their SEGV on demand** — and shows the crossing itself is **healthy**: `rcx` = a real sig record (`nargs=0`, γ=ω=`0x7fffade01053`), `r9` = a valid GVA base, `PC_γ` is reached with **rsp exactly `entry_rsp-48` as designed** and `[rsp+32]` still holding the sig record. `PC` runs, `PC_γ` restores, and control returns to the fragment's landing correctly.

**The death is 29 instructions LATER, in the thunk's own epilogue.** Instruction-for-instruction, the m3 and m4 thunks are identical for 41 steps and then diverge at the **same offset (+0x11c)**:

| | **m3 (works)** | **m4 (crashes)** |
|---|---|---|
| γ exit | `jmp *%r10` | `add $0x70,%rsp` |
| ω exit | `jmp *%r11` | `add $0x0,%rsp` · `mov $0x2,%eax` · `ret` |

The rsp arithmetic is **exactly balanced** (`add $0x10` undoes the call site's carve, `add $0x70` restores the thunk's entry rsp) — so this is not a depth bug. The thunk is *entered by a wire `jmp`* from the defer site, so **there is no return address at `[rsp]`**; the `ret` pops `0x7fffffffdff0` — a pattern-match frame slot — and executes stack bytes (SIGILL at `0x7fffffffdff2`).

`mov eax,2; ret` is `bb_glue_outer_γ`'s `x86("mov32","eax",DT_S) + x86("ret")` (`bb_glue_flat.cpp:98`). `jmp r10`/`jmp r11` is `bb_glue_wire_γ/ω` (`bb_glue_flat.cpp:121`). **Two different glue families for one thunk.**

## 3. The discriminator, and the one bit that differs (RULES step 3, one breakpoint)

`emit.cpp:3308`:
```c
int _wire_stub = ((g_emit.flat_jmp_entry && g_flat_frame_floor > 0) || (g_emit.flat_lcl_proc && !icn_cells_graph)) ? 1 : 0;
```
Breakpoint on `bb_ab_seal_entry_cells`, same program `b1c_e_plain`, both modes, **every** seal:

| seal | m3 | m4 |
|---|---|---|
| `EXPR$0F1` `flat_jmp_entry` | 1 | 1 |
| `EXPR$0F1` **`g_flat_frame_floor`** | **64** | **0** |
| `EXPR$0F1` **`_wire_stub`** | **1** | **0** |
| `PAT$0` `_wire_stub` | 0 | 0 (same both modes — *not* this class) |
| `g_stage2.proc_count` | **5** (`main`, `LBL__PC`, `PC`, `EXPR$0F1`, `PAT$0`) | **2** (`EXPR$0F1`, `PAT$0`) |

**One bit differs, and its cause is named:** `runtime_eval.c:239-242` computes the floor as `zls_g_region(<the g_stage2 row named "main">)`. In m3 the driver and the fragment compiler share one process, so `main` is still in `g_stage2`. **An m4 image's `g_stage2` was never populated with `main`** — main was compiled in the *driver* process — so the search finds nothing and the floor stays 0.

**This is precisely seat6's R1 class, second member.** They named it for the GVA registry; the emitter's *stub verdict* is the same kind of driver-side fact, and it is the one that makes the crossing crash. `emit.cpp:3308`'s own comment says so: *"THE DISCRIMINATOR IS THE DRIVER'S OWN STUB VERDICT: `g_flat_frame_floor > 0` is set by all four scrip.c proc-emission loops."*

## ⭐ 4. WHY s164 / s164b RULED OUT THE RIGHT INGREDIENTS AND STILL MISSED IT

The predicate is a **conjunction**. s164 tested `jmp_entry`-alone; s164b tested `g_flat_frame_floor`-alone. In an m4 fragment `flat_jmp_entry` is *already* 1, so setting it alone changes nothing; and the floor alone (without the seal) leaves the call jumping into `rt_ab_undef_fn_stub`, so it also changes nothing visible. **Both falsifications are correct and both were single-ingredient tests of a two-ingredient cure.** Measured here: floor-alone in m4 ⇒ still `Error 22`.

## ⭐ 5. SEAT6'S §5b IS NOT OVERTURNED — IT IS COMPLETED. THE SEAL IS ONLY FATAL *ALONE*

Their measurement stands verbatim: sealing `alpha$<FN>` alone takes the witnesses **Error 22 → SEGV**, and *"Error 22 was the SAFE failure"* is exactly right — with the wrong epilogue the guard was the only thing catching a thunk that was going to `ret` into a stack slot. Their conclusion — *"a fragment-emitted TINY site cannot speak the record/landing protocol to a statically assembled callee"* — is the part this rung overturns: **the site speaks it correctly; the thunk's exit class was wrong.**

**Both together, measured (gdb, no source change: force `g_flat_frame_floor=64` in the fragment loop + seal every statically-assembled `<FN>_α`):**

| witness | m3 default | m4 default | **m4 + floor + seal** | verdict |
|---|---|---|---|---|
| `b1c_e_plain` | `PC ran/match` | Error 22 | **`PC ran/match`** | ✅ **oracle-identical**, m3 ≡ m4 |
| `b1_eval_pattern_defer_call` | `dt: PATTERN/F called: t cap=A/match` | Error 22 | **identical to m3** | ✅ m3 ≡ m4 restored |
| `b1c_eval_fn_pattern_retreat` | `dt: PATTERN/CB: ty cap=AB/match` | Error 22 | **identical to m3** | ✅ m3 ≡ m4 restored |
| `b1c_patvalued_formal_retreat` | `dt: PATTERN/CB: ty cap=B/match` | Error 22 | **identical to m3** | ✅ m3 ≡ m4 restored |
| `b1c_cross_medium_concat_seam` | `PC ran/PC ran/match` | Error 22 | `PC ran/match` | ⚠ **residue: one `PC ran` short** |
| `b1c_m_plain` / `b1_opsyn_binary_snodef` | PASS | PASS | PASS | controls unmoved |
| `b1_apply_snodef_target` | `6` | SEGV 139 | SEGV 139 | untouched — distinct wall (seat6 agreed) |

**Four of the five named B1c witnesses go `Error 22` → their exact m3 answer.** Three of those land on R2's known wrong answer (`match` where the oracle retreats `nomatch`) — that is queue row 5's lane, it is *identical in m3*, and it is therefore the correct outcome for **this** rung: **the m3 ≡ m4 breach §6b of seat6's FINDING carried as a shipping ratchet is closed on them.**

## 6. The floor's VALUE is inert here — what is wanted is the CLASS-P verdict, not main's geometry

Forcing the floor to **8 / 64 / 256 / 4096** all cure `b1c_e_plain` identically. That matters for the fix's design: `runtime_eval.c:245` already says *"fragment graphs are self-owned, never main-shared, so the s176 shared-graph rationale does not apply"* — i.e. flooring a fragment thunk's region at **main's** layout is inapplicable by the file's own reasoning, and the floor is being consumed here purely as a proxy for *"this blob is wire-entered."* ⛔ **Value-inert on this witness is not value-inert in general** (a thunk whose own region is below main's would carve differently), so a landing must either publish main's real region into the m4 image or make the CLASS-P verdict explicit in **both** modes — a choice that touches m3 and is priced below.

## 7. `semantic_driver` is NOT this class — it becomes its own row, per s171's own rule

HQ routed `beauty_suite/semantic_driver.sno` here as the preferred iteration vehicle, with s171's condition *"becomes its own row ONLY if R2's fix misses it."* **It misses it, measured:** m3 **PASS 8/8**; m4 prints `PASS: 1/2/3` then SEGV, and the fault is **byte-identical cured and uncured** — `rip=0x0`, reached from `rt_call_proc_descr(name="PushCounter")` (`rt.c:908`) through a `β` frame in the `.so`. That is a **null proc fn**, not an exit-class mismatch. ⇒ **mint the row.** (Note for whoever takes it: its output is block-buffered, so the three PASS lines are *lost* on the crash unless you run it under `stdbuf -o0`; a seat reading raw stdout will report "no output" and mis-scope the wall.)

## 8. What a landing costs, and what it must not break

Two pieces, and **neither is optional**:
- **(a) the exit class** — the m4 fragment loop must reach `_wire_stub=1`. The honest fix publishes main's zls region into the m4 image (it is available at the emission site: `zls_g_region(sbbg)`, `scrip.c:1568`) rather than flooring at an invented number, so m3 and m4 compute the *same* floor and the thunk stays byte-identical.
- **(b) the seal** — seat6's reverted `rt_b1c_seal_alpha` + m4-preamble emission, **excluding `$`-bearing names** (`EXPR$<n>`/`PAT$<n>` are runtime-built and referencing their α is a hard link error — their §5b(1), which stands).

⛔ **Blast-radius warning for the landing seat:** (b) changes the **m4 preamble**, so at a default-ON arm every one of the 527 comparable `.s` artifacts moves. It must ship **killswitch default OFF** (blast radius 0 by construction, the same discipline seat6 used for layer 1), with the flip priced separately on a full both-mode corpus A/B.

## 9. No new globals; no source changed for this diagnosis

Every fact above was measured on the shipped pristine build with gdb. `g_flat_frame_floor`, `g_stage2`, `zls_g_region`, `bb_ab_fn_cell_ptr` all pre-exist. **This FINDING adds no global and no code** (FACT RULE NO-NEW-GLOBALS).

## 10. Next rung, named

**B1c-R1c — land (a)+(b) behind one killswitch, default OFF**, then price the flip. Acceptance: the four witnesses hold their m3 answers with `.s` byte-identity **0 movers at the default arm**, and `b1c_cross_medium_concat_seam`'s missing second `PC ran` (§5 residue) is either cured or minted as its own witness. Two rows fall out of this one: **`semantic-driver-pushcounter`** (§7, null proc fn — its own wall) and the residue above.

---

# ⭐ LANDED THIS RUNG — HALF THE CURE, KILLSWITCH `SCRIP_B1C_LAND=1`, **DEFAULT OFF** (SCRIP `bd183811`)

## 11. The `main` lookup is unreliable in m3 too — measured, and it re-frames the fix

Landing (a) exposed a second, previously unnamed defect. On `crosscheck/patterns/140_pat_eval_double_fn_trick.sno` (two EVALs), in **m3**, breakpointed at the fragment seal:

| fragment | `zls_g_region(main)` | floor | `_wire_stub` |
|---|---|---|---|
| `EXPR$0F1` (1st EVAL) | 160 | 160 | **1** ✅ |
| `EXPR$1F2` (2nd EVAL) | **−1** | −1 | **0** ❌ |

**`zls_g_region(main)` goes stale to −1 from the second EVAL onward** (`ir_drive_slot_assign` runs on each fragment graph in between), so **m3 has carried the identical wrong-exit-class defect all along** — it was simply invisible except on multi-EVAL programs, where m4 hits it on the *first* one. `PAT$0`/`PAT$1` read `_wire_stub=0` in every arm and mode: not this class.

**So the fix is not "make m4 imitate m3" — it is "stop asking `main` a question it cannot answer".** The floor now falls back to the fragment's **own** region, which `runtime_eval.c`'s own `emit_chain` comment already licenses (*"fragment graphs are self-owned, never main-shared"*), and which is measurably the **right number, not merely a positive one**: `zls_g_region(_pg)` computes **160** — exactly what `main` gave the first fragment.

## 12. Landing receipts (pristine `make pristine` RC=0, RT_OPT `-O0`, oracle proven alive)

**Blast radius 0, proven twice, not asserted:**
- `.s` md5 default-vs-armed over the **full crosscheck tree: 318/318 comparable, ZERO movers** (0 no-emit).
- The changed function `eval_thunks_emit_from` takes **0 hits under `--compile`** (gdb) — unreachable on the compile path.
- ⭐ **AND THE RULES STEP-4 REGENS WERE RUN, NOT MERELY ARGUED** — all five, in the prescribed order: `benchmark` **no changes** · `feature` **0 changed** · `demo` **no changes** · `programs` **emitted=623 changed=0 unchanged=623** · `prolog_bench` **emitted=22 changed=0**. Both trees clean afterwards, nothing to commit. (The `EMIT-FAIL`/`REJECTED-BY-AS` rows the scripts print are pre-existing rebus/prolog/icon shapes, left untouched by design and untouchable by a SNOBOL4 EVAL-path change.) s170 discharged the same step by structural argument; this rung discharges it by measurement.

**Default arm inert, MEASURED (both reproduce the recorded watermark):** crosscheck `--run` 308 / `--compile` 306 / **DIVERGE 1**; corpus m3 326.

| | crosscheck m3 | crosscheck m4 | corpus m3 | corpus m4 | DIVERGE |
|---|---|---|---|---|---|
| default (shipping) | 308 | 306 | 326 | 323 | 1 |
| **`SCRIP_B1C_LAND=1`** | **309** | 306 | **327** | 323 | **2** |

**+1 in both m3 runners, m4 unchanged in both, ZERO regressions in either mode** — the gain is `140_pat_eval_double_fn_trick`, an EVAL-built-pattern program (the B1c family), i.e. the cure working.

⛔ **The armed arm widens DIVERGE 1 → 2, and that is EXACTLY why it ships OFF.** `140` joins `141_pat_eval_double_fn_arbno`: m3 gains the program, m4 *cannot* until `alpha$<FN>` is sealed. Flipping this default alone would ship a second standing m3 ≡ m4 breach. **Flip it WITH its partner (b), never before.**

**Gates:** `test_gate_template_medium_invisible` GREEN (ratchet **3**, ceiling 3 — not grown) · `test_gate_emit_no_lang` GREEN (LANG-BLIND). **Smokes:** Icon **14/14** both modes · Prolog 3/5 both modes (recorded watermark).

**No new globals** (FACT RULE): `b1cland` is a function-local, `g_flat_frame_floor` / `zls_g_region` / `bb_ab_fn_cell_ptr` all pre-exist. Net new file-scope state: **zero**.

## 13. What is left — B1c-R1c is now exactly ONE piece

With (a) landed, **the seal alone completes the cure**, re-verified at this HEAD under `SCRIP_B1C_LAND=1` with the seal applied in gdb: `b1c_e_plain` → `PC ran`/`match` **oracle-identical**; the three retreat witnesses → **byte-identical to their m3 answers**. The remaining work is seat6's reverted `rt_b1c_seal_alpha` + m4-preamble emission with `$`-bearing names excluded (their §5b(1) stands). ⛔ That piece edits the **m4 preamble**, so unlike this one it moves all 527 comparable `.s` when armed — ship it OFF, then flip **both** killswitches together and price the DIVERGE ledger once.

