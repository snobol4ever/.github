# FINDING 2026-08-09i — SN4 RTX-FUNC step 0: the AB-3b arm is DEAD at HEAD; the ZD scope in bcps_det_arm captures every user-proc call, BOTH modes

**Seat:** Fable, RTX (Lon: "your choice, continue" → RTX-FUNC per the 2026-08-09 directive).
**HEAD:** SCRIP `d2328f81` (= `69ab50bf` "AB-3b: call-site flip + body-jmp fix + nformals pipeline" + README). Fresh clone, fresh full build (watched to "Built:"), zero stale-build exposure.

## 1. THE HEADLINE — measured, not read

`util_rtx_count_syms.sh` (interposer, control-validated: `str_concat_d`=8 on the micro while targets read 0):

| workload (m3 `--run`) | rt_ab_enter_env | rt_ab_leave_env | rt_proc_call_open_slim | rt_proc_open_fn | rt_arg_stage |
|---|---|---|---|---|---|
| `func_call.sno` | **0** | **0** | **10,000,000** | — | — |
| 5-call DEFINE micro | 0 | 0 | 5 | 5 | 5 |

⇒ At HEAD, every user-proc call runs the FULL classic slim protocol per call. The AB activation path never executes. **The cursor's landed claim "AB-3b fires in m3, func_call −11%" (measured at pre-rebase `07b56155`) is NOT reproducible at HEAD.** Provenance of the −11% is an OPEN question (rebase-dropped hunk vs measurement at a different arm state) — flagged, not asserted.

## 2. THE MECHANISM — printf-split forensics (all diagnostics reverted; tree clean)

- `bb_call_proc_staged_str` entry fires (×2/site); non-generator path unconditionally calls `bcps_det_arm()`.
- Inside `bcps_det_arm` (:187), the **ZD scope early-returns at :229**, BEFORE the :360 probe and the :404 `scc && !c2` leg where AB-3b lives. A VERDICT printf at :362 never fired while the entry printf did.
- The ZD scope runs **its own probe** (`scc_z = bb_scc_probe(...)` at :223 — the source of the two `[SCC]` diagnostic lines; all six outer legs =1) and with `scc_z=1` emits: `rt_arg_stage`×args → `rt_proc_call_open_slim` → `rt_proc_open_fn` → slim epilogues. Exactly the dynamic counts.
- `SCRIP_ZD_PROC=0` does NOT release the capture (counts unchanged) — that env gates the emit.cpp:1928 ZD *planner admission* for IR_CALL, not this template scope's own selection. The two gates are independent; the killswitch a next seat will reach for first does not reach this arm.
- Cursor NEXT(1) already named the fix location ("extend AB-3b to the ZD-armed scc path in bcps_det_arm(), lines 231–252, `_z` suffix") but framed it as an *extension*; at HEAD it is the ONLY live path. m4 behaves identically (artifact `func_call.s`:680 `call rt_proc_call_open_slim@PLT`, activation block present at :96/:372 ⇒ `ab_n>0` at emit, so the guard that fails is not `ab_n`).

**Consequence for the RTX-FUNC ladder:** RTX-FUNC-1/2's premise ("two C crossings remain: enter/leave") is FALSIFIED at HEAD — the live path pays arg_stage×n + open_slim + open_fn + epilogue per call. Writing the RTX-FUNC-1 inline as specced would land in an unreachable arm — the s216 vacuous-port class, caught pre-port by §7 step 0(d)/(f). **Real rung order: (RTX-FUNC-0) port the AB-3b call-site flip into the ZD scope's `scc_z` leg — THEN RTX-FUNC-1/2 inline enter/leave in `bb_func_activate`.**

## 3. STEP-0 CENSUS FOR RTX-FUNC-1/2/3 (done; next seat should NOT redo)

- **Bodies read in full** (rt.c:511/:529): `enter` is STRAIGHT-LINE (0(f-pre) discharged: entries==commits by construction) and ALSO reads+zeroes `rt_g_want_name` (absent from the rung text). `leave` arms: `is_fail` + tidy + `rt_nret_fix` guard.
- **vtmark is a READ, not an increment** — the rung's "`inc dword ptr [rip+g_value_trail_top]`" is wrong in both name and op: `rt_value_trail_mark()` = `return g_pl_trail.top` (resolution.c:31, field at offset 32, guarded by an existing `_Static_assert` because **rtx_plcall.S already bakes PL_TRAIL_TOP** — direct precedent for the inline, spelling and offset both).
- **β fast path provable from source:** tidy is a no-op when `g_pl_trail.top == vtmark`; nret_fix fast path when `rt_g_ret_by_name==0` is `rt_g_want_name=wn; return r`. Discriminants: two loads + two compares; slow path = existing `call rt_ab_leave_env` unchanged.
- **Linkage census (nm on .o per ARCH 0(c), then `nm -D` on the .so = the m4 link truth):** EXPORTED and inline-safe both media: `Σ` `Σlen` (stmt_exec.o B) · `g_pl_trail` · `rt_g_want_name` · `rt_g_ret_by_name` · `kw_fnclevel`. **ABSENT from the dynamic table:** `rt_k_level` (hidden, rt.c:396) and `rt_nret_fix` (hidden — fine, fast path never calls it).
- **RTX-FUNC-3 as written is the WRONG DIRECTION for its own purpose:** what the inline needs is `rt_k_level` REACHABLE FROM EMITTED m4 CODE ⇒ exported, the opposite of "promote to hidden". ⚠ HAZARD: `rtx_call.S:89/:144` `dec dword ptr [rip + rt_k_level]` rely on hidden ("hidden => rip-direct" comment at :17/:227); exporting without converting those two sites to GOT-indirect (`mov r11,[rip+rt_k_level@GOTPCREL]; dec dword ptr [r11]` — r11 free at both sites, C signatures) breaks the .so link. No `-Bsymbolic` in the Makefile; scrip's -fPIC .so + m4 GOTPCREL-only exe refs keep ONE coherent copy (no copy-reloc, no direct exe data refs). Both-medium addressing primitive already exists: **`x86_load_got(dst,label,ptr)`** (x86_asm.h:265 — BINARY movabs baked addr, TEXT GOTPCREL).

## 4. FALSE TRAILS CLOSED (so they are not re-walked)

- Instrument suspicion: control symbol proved the interposer live before believing any zero.
- "ab_n==0 at emit": falsified by the artifact (activation block present).
- "the six outer probe legs": all =1 (frame_rsp/dyn/nogen/gva/pok/reg) — none is the discriminator.
- "SCRIP_ZD_PROC=0 will expose AB": falsified by count; wrong gate.

## 5. REPRO (all < 2 min on a built tree)

```bash
bash scripts/util_rtx_count_syms.sh corpus/benchmarks/snobol4/func_call.sno rt_ab_enter_env rt_proc_call_open_slim
# entry/arm split: printf at bb_call_proc_staged_str entry vs after :362 `int c2=...`; run any DEFINE micro with SCRIP_SCC_DBG=1
```
