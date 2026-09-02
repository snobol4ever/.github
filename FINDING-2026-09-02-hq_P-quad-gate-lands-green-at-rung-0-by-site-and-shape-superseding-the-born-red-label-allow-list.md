# FINDING — THE QUAD GATE LANDS GREEN AT RUNG 0 BY SITE AND SHAPE, SUPERSEDING THE BORN-RED LABEL ALLOW-LIST (hq_P, 2026-09-02, s284, MODE `TRIO` read from the file)

**Row:** `prolog-quad-gate-no-r12-r15-write-outside-tr-b-root-ball` (rank 0, instrument lane of `ARCH-PROLOG-BYRD-BOX-TRANSLATION.md` § E; law `RULES.md` § THE PROLOG REBUILD GATE clause 5 — the instrument lane never touches `src/`). **Tree:** SCRIP `9623ff55` (rebased onto `76ebd5f2`; measured on `db299d41`, rung 0) · corpus `9c6489879` · `-O0`, pristine binary built at `db299d41`. **`src/` untouched** (`git diff --stat 76ebd5f2..9623ff55 -- src` is empty).

## 1. What landed

`scripts/test_gate_pl_quad_regs.sh` + `scripts/pl_quad_regs_scan.py`, enrolled LAST in `make test`. The contract it pins is Lon's grant (ARCH top table): in a Prolog graph **r12 = TR, r13 = B, r14 = ROOT, r15 = the ball or 0**, live for the whole run, so any other write to them is a silent corruption of engine state — the rung-2.0 scratch class (`bb_call_fn.cpp lea r12,[rip+…]`, 4,606 sites on the pre-cut tree) that the cut deleted and this instrument keeps deleted.

- **ARM 1 (emitted mode-4 TEXT):** every instruction whose destination is r12–r15 under any width alias is a WRITE, attributed to its SITE — the driver block (`main:` to the root graph's α), the root graph's seed (that α to `<root>_α_body:`), or the enclosing box `nN_<kind>` + port segment / function — and matched against `ENROLLED`, an explicit **(site, register, shape)** table. Unenrolled = VIOLATION, printed with file:line, site and instruction. Fail-closed: an unknown mnemonic with a quad first operand is reported as `?<insn>`, which no row matches.
- **ARM 2 (rtx asm):** the `RTX_FUNC` routines the program names by `call`/`jmp`, closed transitively over `src/runtime/rtx/`; a write in a reachable routine is a violation unless the routine is a TR helper **by name** (`TR_HELPER`, env `QUAD_HELPER_RX`) or the write is bracketed by the routine's own push/pop of that register (printed as preserved, never silent).
- **Fail-once, every run, before the real run is trusted:** (c1) the first compiled witness with `mov r13, rax` injected inside its first box must scan RED; (c2) a synthetic rtx routine writing r14, reached by an injected `call`, must scan RED; (c3) no input must REFUSE rc=2. A canary that is not red makes the gate UNPROVEN(2).

## 2. Measured (the receipt)

```
population: ladder=12 probe_plz=9 corpus=145 -> compiled=1 refused(not-on-the-ladder-yet)=163 other-compile-fail=2
canaries: c1 injected-scratch-write RED ok · c2 reachable-rtx-write RED ok · c3 empty-input REFUSE(2) ok
ok  ladder__rung00_hello.pl.s:100  r12(TR)    driver main       mov r12, qword ptr [0x70000000]   [ROOT/driver-seed]
ok  ladder__rung00_hello.pl.s:104  r14(ROOT)  driver main       xor r14d, r14d                    [ROOT/driver-seed]
ok  ladder__rung00_hello.pl.s:119  r13(B)     rootseed main_α   xor r13d, r13d                    [ROOT/seed B=0 (ARCH § A.1)]
ok  ladder__rung00_hello.pl.s:120  r15(BALL)  rootseed main_α   xor r15d, r15d                    [ROOT/seed ball=0 (ARCH § A.1)]
ok  ladder__rung00_hello.pl.s:121  r14(ROOT)  rootseed main_α   lea r14, [rsp + 64]               [ROOT/seed r14=H (ARCH § A.1)]
rtx reachable from the population: rt_gen_spine_pass_γ, rt_gen_spine_pass_ω, rt_gen_spine_resume_enter
quad-scan: files=1 writes=5 enrolled=5 violations=0 rtx-defined=47 rtx-reachable=3 rtx-writes=0 rtx-violations=0
GATE PASS(0) [test_gate_pl_quad_regs]: 0 unenrolled r12-r15 writes (mode-4 TEXT + reachable rtx; compiled witnesses=1)
```
- The post-cut compiler compiles exactly ONE Prolog program — the rung-0 hello witness; the other 163 refuse loudly with *"not on the ladder yet — rung N lands it"* (21 `include`, 15 `l__/1` multi-clause, 14 `d/3`, …). The two `other` failures are a parse error at line 43 of the two `det.pl` copies (`src/swi-bench`, `src/swi-vanroy`) — the ladder runner's business, printed, not graded.
- The five writes are the five ROOT seeds § A.1 rules (driver: the C.A.S. top into r12 and `r14=0`; root α: `r13=0`, `r15=0`, `r14=H`). `0x70000000` is `RT_DCAP_TOP`/`RT_PIN_BASE` (`pin_va.h:6`, `scrip.c:1355`), the SNOBOL4 C.A.S. base that Lon's second grant re-purposes as TR.
- Tree-wide informational sweep (`--rtx-scan-all`, census not verdict): of all 47 rtx routines the ONLY r12–r15 writers are three push/pop-bracketed scratch uses of r12 in `rt_match_replace` (`rtx_match.s:336/368/412`, SNOBOL4), preserved for the caller. `rtx_abi.inc` defines no `.macro`.
- `make test` (the blocking set, detached per ceo's `board-takes-748s-under-load-run-it-detached`): rc=0 in 713 s (m3 PASS=1679 FAIL=0 · m4 PASS=1679 FAIL=0 SKIP=0 · MISSING=0; the quad gate last, PASS).
- **Re-proved after the rebase** (three commits landed under the push, one in `src/lower/lower_icon.c`): incremental `make`, then the gate on SCRIP `9623ff55` clean stamp — identical numbers (compiled=1, writes=5/5 enrolled, rtx 3 reachable / 0 writes), `GATE PASS(0)`, 45 s.
- Cost: ~45 s (166 compiles, `sys`-dominated by process spawn), last in the recipe so every cheaper gate reports first.

## 3. This SUPERSEDES the version this seat minted at `4253dd88` — and why that is a correction, not a rewrite

The earlier gate (same path, hq_P s283, "born red on `f4532dea`: 5,303 writes / 5,303 violations") graded writes by whether their enclosing column-0 LABEL matched `QUAD_HELPER_RX` (default: nothing). Measured on today's HEAD it is **RED with 5 violations — the five ROOT seeds** — and its only path to green is naming `main` and `main_α` in the allow-list, **which admits ANY write under those labels**: exactly the widening the gate exists to forbid. Three further defects, all measured: its ASCII-only awk did not follow the Greek-lettered rtx routines in the reachability arm (reached 1 of the 3 the program calls — `rt_gen_spine_pass_γ/ω` were invisible); its proof was an opt-in `--self-test` (lib_gate.sh's own lesson: *a flag no caller passes is a disabled gate*); and it was never in `make test`. What survives, deliberately: `QUAD_HELPER_RX` is still honoured — as the **rtx ROUTINE-name** allow-list, which is the right unit for asm (a whole routine whose job is the trail IS the helper, and the rung-1 brief's sentence *"QUAD_HELPER_RX gains EXACTLY the TR helper names"* still reads true); the balanced push/pop rule; the fresh-compile-never-artifacts rule; the probe_plz population.

⛔ The three prose records of the old design (`GOAL-PROLOG-100.md` and `GOAL-HQ-PERFORM.md` s283 cursors, `GOAL-CEO.md` CEO-149) are HISTORY of a minted instrument, kept; this FINDING plus the E.2 row are the current description. hq_C's live rung-1 baton names `QUAD_HELPER_RX` — telegram `quad-gate-superseded-enrol-shapes-not-labels` sent so the mechanism is re-pointed before rung 1 lands.

## 4. The lesson (transferable)

**An allow-list keyed on a LABEL is a per-site exception wearing a regex.** The RULES "no per-op filter" law has a twin for instruments: a gate that admits code by WHERE it sits re-admits by the back door everything that later lands there. Admit by WHAT the instruction is (register, source shape) at WHERE it may legally be (site) — the table is then the contract, one row per legitimate shape, and a new writer turns the gate red until someone names the exact shape. That red is the instrument working.

## 5. Open (named, not hidden)

- rtx reachability follows direct `call`/`jmp` symbols; `jmp rax` / `call rax` (the resume-through-frame shape) is not followed. A future helper reached only indirectly would be missed until named. Recorded on the baton's NEXT.
- mode-4 TEXT only (MODES MAY DIVERGE): the verdict names its mode and does not bind mode 3.
