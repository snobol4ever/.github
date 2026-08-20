# FINDING s189 (HQ, Fable 5, max effort) — THE BUG FINDER CAME BACK ARMED AND BRACKETED FIVE BUGS IN ONE SITTING

**Date:** 2026-08-20 · **SCRIP:** `c62c18af` (pristine, RT_OPT `-O0`) · **corpus:** `d686c91f` · oracle live `x64/bin/sbl`.
**Lon's directive (in-chat, verbatim in substance):** *"the AUTOMATIC BUG FINDER is the absolute key … PIVOT! … One session find 2-3 bugs and being done in an hour"*, then: *"choose at random failing programs, analyze them with the AUTOMATIC BUG FINDER, then write up the RUNG/STEPS … you'll lay out the fix for them and do the hard work, and they will spend all the time developing, testing, and administrating. Always include ONE BEAUTY SELF HOST bug."*

## 1 · THREE INSTRUMENT CURES (SCRIP `c62c18af`, pushed) — what unblocked the finder

1. **Synthetic names never cross the trace/monitor surface.** `comm_call`/`comm_return`/`comm_var` now refuse compiler-minted names via `mon_name_is_internal` — the s112 MON-CAP ONE AUTHORITY (identifier-head + `$`, so the user variable named `$` survives). The oracle structurally cannot emit `EXPR$n`/`PAT$n` events, so each one was a guaranteed false divergence. **Beauty's autobug bracket had been pinned at step 1568 by exactly this** — `spl CALL PushCounter` vs `scr CALL EXPR$173`, where `EXPR$173` is merely the thunk for `*Command`, the ARBNO body defer (`Parse = nPush() ARBNO(*Command) …`; `nPush()` returns `epsilon . *PushCounter()`, and SPITBOL, matching ARBNO null-first, fires the conditional-target calls at success — so its first event is the user call while SCRIP's was the thunk). `SCRIP_MON_SYNTH=1` restores the old stream. With the filter, **the monitor sync-steps beauty on `m1_min.in` to END with zero divergence** — which also proves the plain-build SIGSEGV is invisible on the monitor arm (`MONITOR_BIN` grades a different program; RULES already names this), so the beauty bracket below was taken by the OTHER road.
2. **The ZSM ring got a `st=` column.** Mode-3 node ids are pointer hashes (`bb_node_id`: ptr%100000, unstable across runs), so a ring line could say WHAT box fired but not WHERE. `mon_emit_label_bin` now latches `kw_stcount` (a dead cell — nothing incremented or read it) and the ring stamps it per port. Statement-number ↔ source resolution: `scripts/monitor/build_stno_map.py <prog>` (numbering monitor-verified against live SPITBOL label events).
3. **The statement LABEL tap now also emits under `SCRIP_ZSM=1`** (was MONITOR_BIN-only), so plain crash-runs carry statements. Default byte-identical by construction (both gates off ⇒ tap off). Gates run: smoke 7/7 BOTH modes.

**The crash-window recipe (no monitor needed), now the standard first move on a SIGSEGV:**
```bash
SCRIP_ZSM=1 SCRIP_ZSM_ALL=1 SCRIP_ZSM_RING=1 SCRIP_NO_SEGV_HANDLER=1 \
  gdb -batch -ex 'run PROG.sno < IN' -ex 'bt 4' -ex 'call (void)zsm_dump()' /home/claude/SCRIP/scrip
```
The raw SEGV bypasses the atexit reporter; calling `zsm_dump()` from gdb at the fault prints the last 2048 four-port events **ending at the crash**, each with op name, rbp, rsp, depth, stno.

## 2 · ⭐⭐⭐ THE BEAUTY SELF-HOST BUG, BRACKETED (the ONE beauty rung, per Lon's standing order)

Witness: `beauty.sno < m1_min.in` (one empty line; oracle prints the identity, rc=0; SCRIP SIGSEGV rc=139, `rip=0x7ffff7ffd000` = `_rtld_global`, ld.so DATA — wild jump, backtrace destroyed, rsp shallow).

**The ring at the crash (recipe above):** during the `*Parse` match the retreat cascades β·/ω· through DEFER/ALTERNATE/ASSIGN_COND/ASSIGN_SAVE, then `MATCH_BEGIN` node takes **β then ω — the whole match CONCEDES** (the oracle's match SUCCEEDS — that wrong answer is its own open class, the composed-pattern family). Control takes the failure road; two ordinary statements run; then an **IR_DEFINE-family box** fires α· and executes the **RETURN glue**:
```
pop  %rcx          ; the success continuation …
add  $0x8,%rsp     ; … discard the failure one
jmp  *%rcx         ; RETURN/FRETURN pop-pair trick (ARCH-PASSTHRU law 0a)
```
**gdb at the 236th α·-IR_DEFINE event (the last before death — breakpoint recipe in §4):** the quad the `pop` will read is `0x00007ffff7ffd000` (`_rtld_global`) — **and one slot below it sits `0x41bd68`, a real scrip-binary continuation, with a live slab address (`0x7fffee4664f7`) a few quads further down. The {γ,ω} pair is not MISSING — it is SHIFTED: the stack is one-plus slots low at RETURN.** An unbalanced push/release upstream (the conceded match's unwind is the prime suspect: its ω must give back exactly what its α and body carved — law 0b/ω-balance) leaves rsp displaced, and the first pop-pair consumer thereafter flies wild. This is the stack-doping read Lon asked for: not "it went somewhere unknown" but "the pair is exactly N slots away from where the consumer looked."

**Fix lane for the seat (row `beauty-return-pair-shift`):** find the first port where the carve is not given back. The instrument already measures it — `rt_zdp_sm_event`'s ω arm compares `rsp@ω` vs `rsp@α` ("RSP LEAK … carved and never released", counted-not-fatal on the frameless arm). Run the ring census on beauty, grep the leak/imbalance warnings BEFORE the crash, take the FIRST leaking box, asm-diff its emitted form against a green sibling. Gates: `m1_min.in` stops SEGVing; `board_beauty_m1.sh --modes m3` first-red moves past 10; corpus fail-set no worse.

## 3 · FOUR WITNESS BRACKETS (one autobug run each, ~seconds apiece; commands + full artefacts in each queue row)

| witness | oracle | SCRIP | the bracket says |
|---|---|---|---|
| `ptw_min_arbno_tail_falseaccept_nodefer` (`E = ARBNO('a') LEN(1)`; `'aa+aa' POS(0) E RPOS(0)`) | **nomatch** | match | DIVERGE step 4: spl takes `:F`, scr takes `:S`. ARBNO exhaustion against an unsatisfiable tail reports SUCCESS. No defer, no ALT — pure ARBNO exhaustion. |
| `ptw_min_nullalt_retreat_falsereject` (`E = ANY('ab') (LEN(1) \| '')`; `'ab+ab' *E 'b'`) | **match** | nomatch | DIVERGE step 4, opposite direction: the forced retreat into the ALT's null arm never happens. |
| `ptw_min_fence_alttop` (`P = ('a' FENCE(epsilon) \| 'aa')`; `'aa' POS(0) *P RPOS(0)`) | **match** | nomatch | DIVERGE step 4: fence-cut inside arm 1 kills the WHOLE alternation; arm 2 (`'aa'`) is never offered. Manual ground: FENCE fails when backed THROUGH; trying the next arm at the same cursor backs through nothing (the alt-seam-tier row's own argument). |
| `ptw_min_opsyn_evalpat` (OPSYN'd op returns EVAL-built `epsilon . *RDX(t,n)`; `'aa' POS(0) *P2 RPOS(0)`) | calls `RDX` at match | **never calls RDX**, skips to the outcome label | DIVERGE step 13: `spl @9 CALL RDX` vs `scr LABEL stno=11`. The deferred call inside a build-returned pattern is never wired into the match — the s182-pinned wall, now bracketed on a 10-line witness. |

## 4 · ⭐⭐ THE HANG, CAUGHT COLD (`ptw_min_defer2_hang` — the defer-depth-floor row's surviving face)

`G1 = ARBNO('a' | 'ab')` · `P = *G1 RPOS(0)` · `'abcdef' POS(0) *P` → oracle nomatch; SCRIP never terminates. Live census (`SCRIP_ZSM_CENSUS=1`, 10s = **5.47M port events**) shows a **four-event cycle repeating forever**:
```
β·  IR_MATCH_ALTERNATE  node=17328  state=DEAD   ← [ZSM] β WITH NO LIVE α ("claimed impossible")
β·  IR_MATCH_LIT        node=17408  state=DEAD   ← [ZSM] β WITH NO LIVE α
ω·  IR_MATCH_LIT        node=17408
ω·  IR_MATCH_ALTERNATE  node=17328
```
Both boxes are DEAD (activations retired), yet the retreat wiring bounces between their β entries: A's ω wires to B's β, B concedes, B's ω wires to A's β, forever — **the retreat never unwinds OUT of the dead pair to the enclosing choice point**. rsp/rbp frozen (same values every iteration): a pure control-flow cycle, not a stack leak. Two instrument notes minted from this: (a) the β-no-live-α counter at volume IS a hang signature — worth an escalation knob; (b) the finder's monitor road cannot bracket a hang (no divergence event) — the census road is the hang tool.

## 5 · THE OPERATING MODEL, PROVEN TODAY (routed here because Lon declared it in-chat)

**One Fable at HQ runs the finder and does the analysis; 8 Opus seats develop, test, administer.** Every dispatch row now carries: the finder command verbatim, the bracket, the mechanism analysis, the laid-out fix lane, and gates. **The ZSM/autobug BAN in older rows is LIFTED** — the s184 rax-bank cure proved ZSM-ALL transparent (896-program sweep, silent wrong answers 65→0) and s189's three cures (this FINDING §1) are pushed at `c62c18af`; rows written before that carry a stale ⛔. The tool **LOCATES, never GRADES** (RULES ASM-DIFF-FIRST binds unchanged): every verdict is still the plain build against the live oracle.

## 6 · Corrections routed

- The GOAL-SCRIP-HQ queue's `m1-composed-wild-jump` row said *"the crash is inside the `*Parse` match"* — **refined**: the wrong ANSWER is inside the match (it concedes where the oracle matches); the CRASH is after it, on the failure road, at the first RETURN pop-pair consumer of a shifted stack (§2). One defect family became two rows with a clean seam.
- The monitor-vs-map statement numbering confusion cost this session ~20 minutes: `build_stno_map.py` IS the authority (monitor-verified against live SPITBOL to END); an earlier in-chat table quoted from a stale map. Trust the script, not transcripts.
