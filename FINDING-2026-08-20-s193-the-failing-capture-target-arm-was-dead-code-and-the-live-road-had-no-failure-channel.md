# FINDING s193 (2026-08-20, seat6 `/home/claude6`, Claude Opus 5) — **THE FAILING-CAPTURE-TARGET ω ARM WAS WIRED TO SUCCESS *AND* WAS DEAD CODE. THE LIVE ROAD IS THE IMMEDIATE ONE, AND IT HAD NO FAILURE CHANNEL AT ALL.**

**Brief executed:** queue row `dcap-freturn-false-accept` (rank 0) — beauty's token-classification wall. **Verdict: CURED AND LANDED**, default ON, `SCRIP_CAP_FAIL_RETREAT=0` reverts VERBATIM (proven against a real unpatched control build).

## ⛔ THE ONE SENTENCE

The row's own FINDING located the defect at `rt_dcap_pump`/`MATCH_END` — *"drained after the match already succeeded, so a failure has nothing to retract"* — but at this HEAD **the witness never records a dcap entry at all** (`SCRIP_DCAP_TRACE` prints `end_ok n=0`): `$ *chk()` is the **IMMEDIATE** road, `c_rt_cap_open` resolves the target itself and returns `0` = *"fully handled"* whether it **assigned or failed**, and that shared `return 0` is the bug.

## 1 · WHAT THE WITNESS ACTUALLY DOES (measured, before any code)

`corpus/probe/dcap/dcap_freturn_target` — oracle `nomatch`, SCRIP `matched`, **m3 ≡ m4** (DIFF/DIFF); the `:S(NRETURN)` control is PASS/PASS in both. Then three measurements that redirected the whole row:

* **`SCRIP_DCAP_TRACE=1` → `[DCAP] end_ok n=0`.** The pump's walk range is EMPTY. `IS_FAIL_fn` is never evaluated, `rc` is 0 by construction, and no `[DCAP] WARN` is printed. **The MATCH_END drain story does not apply to this witness.**
* **`chk` IS called — exactly once, in both engines** (probe with `OUTPUT` inside `chk`). So the target fires; only its *verdict* is lost.
* **`SCRIP_CAP_NAME_STRICT` is DEFAULT ON since s178** — the row's killswitch sweep tested `=0` only. Neither value moves the witness, because that switch's failure edge is wired into `IR_MATCH_END` for the **COND/dcap** road and this element is **IMM**.

## 2 · ROOT CAUSE, READ OFF THE EMITTED `.s` (ASM-DIFF-FIRST, no gdb)

The IMM capture box emits a four-port transfer whose ω landing is wired to success:

```
call rt_cap_open ; test rax,rax ; je .Lx95_1     <-- 0 = "fully handled" -> SUCCESS continuation
lea rcx,[.Lx95_2] ; lea rdx,[.Lx95_3] ; jmp rax  <-- transfer: γ and ω landings
.Lx95_2:  epilogue_γ ; rt_cap_finish ; jmp .Lx95_1
.Lx95_3:  epilogue_ω ; rt_cap_finish            <-- NO JUMP: FALLS THROUGH into .Lx95_1
.Lx95_1:  jmp n37_..._α                          <-- the success continuation
n36_match_assign_imm_β: jmp n35_match_span_β     <-- the fail port ω never reached
```

**Four ports, three wires** — and `rt_cap_finish` returns `void`, so the C side has no channel either. **But fixing only that arm changes nothing on this witness, because the arm is DEAD here:** the asm `rt_cap_open` (`rtx_match.S`) delegates every `'*'` target to `c_rt_cap_open`, which calls the proc itself, skips the assignment on failure, and returns `0` — so the box takes `je .Lx95_1` and the transfer never happens. **Two defects on one road; only the second is reachable from the witness.**

## 3 · ⛔ THE HAZARD, HIT FROM THE OTHER SIDE

The brief named it at `MATCH_END`: the return register is overloaded — `test rax,rax` treats every non-zero value as a **transfer address** to `jmp rax`, so a naive `return 1` jumps to address 1. **The identical overload exists at `rt_cap_open`**, where `0` = handled and any positive value = `fbytes`, a frame size. The cure therefore uses a **sentinel `-1`** tested *before* the transfer test — a value that cannot collide with a frame size, read on a path that runs before `rax` is ever treated as an address.

## 4 · ⭐ THE ORACLE RULED THE CURE'S SHAPE — RETREAT, NOT ABORT

The obvious cure (reuse s170's `IR_MATCH_END` ω, which aborts the statement) would have been **wrong**, and live `sbl -bf` says so:

| probe | oracle | meaning |
|---|---|---|
| `(SPAN('ABC') $ *chk('NO') \| 'ABC')` | `CHK` then **`matched`** | a failing target **RETREATS**; the next alternative runs |
| `&FULLSCAN=1`, `SPAN $ *chk('NO')` | `CHK` then `nomatch` | the retreat propagates; SPAN offers no shorter alternative |
| call count | **exactly 1** | no rescan, no re-entry |

So a **failing** target concedes on the box's own ω wire (where `x86_beta_trampoline` already routes β), while a **not-a-name** target aborts through `IR_MATCH_END` (s170 SN4-CAP-NAME-STRICT). **Two different verdicts on one road; merging them would have been a plausible wrong answer.** SCRIP now matches the oracle on all three probes.

## 5 · THE CURE

Both halves read one env name (`SCRIP_CAP_FAIL_RETREAT`, the s121 both-halves-land-together law), default ON:

* **runtime** (`pattern_match.c`) — `c_rt_cap_open`'s `*` arm: a FAIL descriptor returns **`-1`** instead of falling into the shared `return 0`.
* **emitter** (`bb_match_capture.cpp`, **both** IMM arms — no per-op filter) — `cmp rax,-1 ; je L(4)` **before** the transfer test, and an `L(4)` landing that does `x86_anchor_leave()` (the alignment pair must balance exactly once, and this path never reaches `L(1)`'s leave) then `x86_omega()`.
* the previously-dead transfer ω arm is wired too, so the family is correct whether or not the transfer is taken.

## 6 · RECEIPTS (pristine `c52f3529` + this cure, RT_OPT `-O0`, live `sbl -bf` verified alive)

| | armed (default) | `=0` |
|---|---|---|
| `dcap_freturn_target` (oracle `nomatch`) | **PASS/PASS** | DIFF/DIFF |
| `dcap_freturn_target_ok_ctl` (oracle `matched`) | **PASS/PASS** | PASS/PASS |
| corpus | m3 **335/2** · m4 **328/8** SKIP 1 | identical, **fail-set identical BY NAME** |

* **Killswitch reverts VERBATIM — proven, not asserted.** The patch was set aside, HEAD rebuilt as a real control, and swept: `=0` vs unpatched control = **0 movers on 1648 `.sno`**, the only row being `unary_not.sno`, which emits uninitialised memory into `.rodata` and differs on every compile in every arm (reported separately at s191).
* **Blast radius: 128 programs / 1648, noise floor 1** — every one a `$`-capture carrier. RULES step-4 regens moved exactly **one** artifact tree-wide: `test/snobol4/capture/059_capture_dollar_deferred.s`, +3/−1. The radius lands precisely on the construct.
* **4 gates green:** `emit_no_lang` · `template_medium_invisible` (ceiling 0, and the template carries zero `MEDIUM_` tokens) · `icn_no_stack` · `icn_one_reg_frame`.

## 7 · ⭐⭐ BEAUTY: THE CLASSIFICATION WALL IS DOWN — AND THE CRASH IS **NOT** DOWNSTREAM OF IT

With the FINDING's own `xTrace = 5` ablation on the one-line input `L       X = 1`:

| token | oracle | `=0` (pre-cure) | **armed** |
|---|---|---|---|
| `X` | `Push(Id)` | `Push(BuiltinVar)` | **`Push(Id)`** |
| `1` | `Push(Integer)` | `Push(BuiltinVar)` | **`Push(Integer)`** |

**Oracle-identical.** Beauty advances past the first guarded alternative and reaches `Shift(Integer, 1)`.

⛔ **BUT THE ROW'S PREMISE IS HALF FALSIFIED, AND SAYING SO IS THE POINT.** The row states *"Every downstream symptom incl. the wild jump is a consequence of the mis-parse."* Measured: beauty **SIGSEGVs at rc=139 after exactly 18 trace lines in BOTH arms** — same depth, same count, arm-independent. And `board_beauty_m1.sh --modes m3` is **identical across arms: 5/10, first red at rung 40**, per-rung diff empty. So the mis-parse and the crash are **two independent walls**; curing the first does not move the ladder. A seat taking the next beauty row should expect the SEGV to still be there and should not spend the session looking for it downstream of token classification.

## 8 · NEXT

The SEGV wall at prefix-rung 40 is now the sole beauty blocker on this ladder and is **arm-independent of every capture switch** — it wants its own row, minted from the 18-line trace ceiling rather than from the classification symptom.
