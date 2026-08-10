# FINDING 2026-08-10 — RTX-FUNC: step 0(c)'s instrument cannot answer step 0(c)'s question, `rt_k_level` has two OPPOSED consumers, and a concurrent actor committed over this seat's working tree

**Seat:** GOAL-SNOBOL4-RTX (RTX-FUNC). **Base at session open:** SCRIP `ea16aedf`, `.github` `5a3a8800`, corpus `0f02731d`.
**Outcome:** RTX-FUNC-1 + RTX-FUNC-2 present at SCRIP `799f2e76` (unpushed, ahead 1) and INDEPENDENTLY VERIFIED by this seat. RTX-FUNC-3 DISCHARGED with its prescription corrected. **RTX-FUNC-5 acceptance NOT met: `fibonacci` 0.66× vs the ≥0.80× bar.**

---

## 1. ⭐⭐ STEP 0(c) ROUTES YOU TO AN INSTRUMENT THAT CANNOT ANSWER ITS OWN QUESTION

ARCH §7 step 0(c) says — correctly, and for a hard-won reason — run `nm` on the **object file, never the `.so`**. It then instructs: *"Exported (`nm` capital `B`/`D`) means PREEMPTIBLE and needs `[rip+sym@GOTPCREL]`; visibility-hidden … stays `[rip+sym]` direct."*

**That inference is INVALID on an object file.** In a `.o`, `nm`'s capital/lowercase letter encodes **linkability** (global vs `static`), NOT **visibility**. A `__attribute__((visibility("hidden")))` global prints capital `D` exactly like a default-visibility one. The `.so` is where hidden collapses to lowercase — and step 0(c) explicitly forbids reading the `.so`.

Measured this session on `out/rt_pic/*.o`:

| symbol | `nm` letter | TRUE visibility (`readelf -sW`) | in `.so` `.dynsym`? |
|---|---|---|---|
| `rt_k_level` | **D** | **HIDDEN** | **ABSENT** |
| `rt_g_want_name` | B | DEFAULT | present |
| `rt_g_ret_by_name` | B | DEFAULT | present |
| `Σ` / `Σlen` (stmt_exec.o) | B | DEFAULT | present |
| `kw_fnclevel` (core.o) | B | DEFAULT | present |
| `g_pl_trail` (resolution.o) | B | DEFAULT | present |

This seat's first pass read all seven as exported and was **wrong about `rt_k_level`**. The letter is identical; only `readelf -sW`'s BIND+VIS columns separate them.

⇒ **AMENDMENT OWED TO ARCH §7 step 0(c): the check is `readelf -sW <obj>` (BIND + VIS), not `nm`. `nm` on the `.o` answers "can `.S`/emitted code NAME this symbol"; it CANNOT answer "must this be reached via GOT."** Two questions, one letter. Same "two things identical through the instrument you happened to pick" class this checklist already names twice — one level further down, and this time the defect is IN the checklist.

## 2. ⭐⭐ THE RTX-FUNC-1/-3 PRESCRIPTION IS BACKWARDS, AND THE NAIVE FIX IN THE OTHER DIRECTION BREAKS THE `.so`

The rung reads: *"promote to `visibility("hidden")` and inline as `inc dword ptr [rip + sym]`"*, and asserts *"`rt_k_level` and `kw_fnclevel` are already hidden (`rt.c:396`)."*

Three corrections:
- **(a) Only `rt_k_level` is hidden.** `kw_fnclevel` is DEFAULT and lives in `core.o`, not `rt.c` — the parenthetical covered one symbol and was silently extended to two.
- **(b) For a symbol EMITTED CODE must reach, hidden is the DISQUALIFIER, not the enabler.** Hidden ⇒ absent from `libscrip_rt.so`'s `.dynsym` ⇒ an m4 executable cannot link it at all. That is precisely the `g_cap_gen` class already recorded at `pattern_match.c:737` (173/316 m4 LINK failures, m3 structurally blind). Following the rung as written on a symbol α must write would have reproduced that incident.
- **(c) ⛔ BUT `rt_k_level` CANNOT SIMPLY BE PROMOTED EITHER — MEASURED, NOT REASONED.** Promotion to DEFAULT fails the `.so` link outright:
  ```
  ld: out/rt_pic/rtx_call.o: relocation R_X86_64_PC32 against symbol `rt_k_level'
      can not be used when making a shared object; recompile with -fPIC
  ```
  The hand-written `rtx_call.S` / `rtx_plcall.S` reach it with **direct PC32, legal ONLY while it is non-preemptible**. Its hidden visibility is **load-bearing for the runtime's own asm**.

⇒ **THE TWO CONSUMERS ARE OPPOSED: in-`.so` asm REQUIRES hidden; emitted m4 code REQUIRES dynsym-exported.** Neither direction of the one-line fix works. Resolution of record: the cell stays hidden and a new **exported `int * const rt_k_level_p`** carries it across the boundary (one extra load: GOT → pointer → cell; identical shape in both media). ⚠ **A future seat reading the rung will try promotion first, as this one did — the rung text must carry this or the wall gets hit again.**

## 3. ⚠ BOTH-MEDIUM: `x86_reg_disp32_load32` PRINTS ITS DESTINATION VERBATIM

Its TEXT arm emits `" mov " + dst + ", dword ptr [...]"`. Pass a 64-bit `dst` and TEXT spells `mov rcx, dword ptr [rax+0]` — a gas size mismatch — while **BINARY silently encodes a correct 32-bit load** (no REX.W). The m3/m4 divergence class, and m3 alone can never see it. Correct form: `"ecx"` (accepted as `XK_REG`, same `x86_rnum`) + `x86("movsxd","rcx","ecx")` for the C's exact sign-extension. ⛔ `movsxd` has **no memory-source arm** (it aborts loudly — good); adding one means `x86_asm.h`, which is NOT-CONCURRENCY-SAFE. `x86_asm.h` UNTOUCHED this session.

## 4. VERIFICATION OF `799f2e76` BY AN INDEPENDENT SEAT (see §5 — this seat did not author the commit)

Rebuilt first: the on-disk binary was from a **pristine** build while the source carried FUNC-1+2 — the stale-build trap, and every number below post-dates the rebuild.

**m3, min-of-5, RT_OPT=-O0, this machine.** Ratio = SPITBOL ÷ SCRIP (>1 beats the oracle).

| bench | pre-port AB=1 (this seat) | post AB=0 | post AB=1 | SPITBOL | ratio | commit claimed |
|---|---|---|---|---|---|---|
| `func_call` | 1510 | 2047 | **1281** | 1514 | **1.18×** | 1299 / 1.17× |
| `func_call_overhead` | 1494 | 2050 | **1303** | 1472 | **1.13×** | 1274 / 1.16× |
| `fibonacci` | 407 | 559 | **357** | 234 | **0.66×** | 360 / 0.65× |

All three oracle-exact in BOTH arms. **The claimed numbers REPRODUCE within noise — the commit's measurements are real.** Semantics micros three-way vs SPITBOL: `recur2` 6 ✅, `r_keepn` `z1` ✅ (the live-nested recursion class stays fixed), FRETURN (manual Ch.8 p.103 non-pattern form) `ok4` ✅. Two pre-existing failures **proven pre-existing by a pristine-HEAD control, not assumed**: NRETURN-into-capture and `LEN(*N)` runtime-built patterns both fail IDENTICALLY at pristine HEAD in both arms (GZ#5 lowering subset).

⛔ **ACCEPTANCE NOT MET.** The directive's bar is ≥0.80×; `fibonacci` is **0.66×** and needs ≤293 ms (currently 357). Two of three past parity is real progress and is NOT the acceptance.

## 5. ⛔⛔ CONCURRENCY INCIDENT — A SECOND ACTOR COMMITTED OVER THIS SEAT'S WORKING TREE

This seat authored the RTX-FUNC-1 α inline, the `rt_k_level_p` alias, and the `resolution.c` assert extension, then ran `git stash` to take a pristine control. Reflog of record:

```
799f2e76 pull --rebase -q origin main (finish)
5416ed56 commit: RTX-FUNC-1 + RTX-FUNC-2 ...
ea16aedf reset: moving to HEAD          <- this seat's `git stash`
ea16aedf clone
```

**This seat did not run that `commit` or that `pull --rebase`.** `git stash pop` then failed with *"No stash entries found"*; `refs/stash` does not exist. The resulting commit is authored `LCherryholmes`, contains this seat's edits **plus an RTX-FUNC-2 β fast path this seat never wrote**, and was rebased onto an upstream that had advanced to `7b4d310d`. Foreign artifacts (`/tmp/pkw_m4.s`, `/tmp/pfib_m4.s`, `/tmp/pristine.s`) confirm a second actor in this container.

⇒ **`GOAL-SNOBOL4-RTX` already marks RTX-FUNC NOT-CONCURRENCY-SAFE on `bb_func_activate.cpp` — "Lon routes the seat." That routing was not in force, and the first casualty was a stash.** The work survived only because the other actor incorporated it. ⚠ **This seat stopped editing rather than start RTX-FUNC-4 into a file another actor is committing.** The verification in §4 is offered precisely because a commit whose provenance is unclear must be treated as an untrusted claim and falsified by measurement — which it survived.

## 6. OWED (unchanged or newly owed)

- **RTX-FUNC-4 / -5:** `fibonacci` 0.66× → ≥0.80×. Legacy call surface (`rt_arg_stage`, `rt_proc_call_open_slim`, `rt_proc_open_fn`, `rt_proc_call_epilogue_slim_`) still on the m4 path.
- **`.s` regen ×3 — NOW DEMONSTRABLY STALE:** `corpus/benchmarks/snobol4/fibonacci.s` is timestamped at clone (14:08) and predates every edit today. ⚠ **Its call census describes the OLD emission; do not quote it as current output.** Debt carried since `8172e54`.
- **m4 AB=1 SEGV** — the commit reports it PRE-EXISTING by pristine control and states this **falsifies the prior cursor's claim that the `"leave"` fix unblocked m4 AB=1**. Not re-verified by this seat.
- Kill-switch CALL gate N≥4 both modes; full crosscheck at watermark; watermark re-prove. **None run this session.**
- ARCH §7 step 0(c) amendment per §1.

## 7. LIMITATION

Every number here is m3, `RT_OPT=-O0`, min-of-5, one machine, and this machine is NOT the one the prior cursor measured (its 1104/1136/294 do not transfer). `bench_rtx_3arm.sh`'s three-arm rail was NOT used — these are ON/OFF two-arm numbers and ARCH §7 step 4 warns no two-arm number below ~1.10× is trustworthy. The `func_call` 1.18× and `fibonacci` 0.66× are far enough from 1.0 to survive that caveat; **`func_call_overhead` 1.13× is close enough to it to deserve a rail re-run before being quoted anywhere load-bearing.**
