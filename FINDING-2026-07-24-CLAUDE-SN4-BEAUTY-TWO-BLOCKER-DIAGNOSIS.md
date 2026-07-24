# FINDING — beauty.sno self-host is blocked by TWO independent bugs, not the DEFINE O(n²)

**Session:** s140 (2026-07-24, Claude) · **SCRIP HEAD:** `303839b8` (== origin/main; the gated DEFINE entry-stub) · **RT_OPT=-O0 throughout**

This finding **corrects the diagnosis** carried by `FINDING-2026-07-24-...-ENTRY-STUB-VALIDATED.md` and the pre-s140 LIVE CURSOR. Everything below was proven **empirically** in this container with two experiments; the tree was reverted to pristine after each (nothing here was committed as code).

---

## TL;DR

The wall blocking `beauty.sno` from self-hosting is **NOT** the DEFINE-loop O(n²) that the 1-node DEFINE entry-stub was built to kill. It is **two independent blockers**, and the entry-stub addresses **neither** of beauty's real walls:

1. **LBL__ CODE-label O(n²) → compile-time entry-table overflow** (the first diverge).
2. **Runtime pattern-blob registration gap** (`PAT$30+` not registered) → beauty runs, then `Parse Error`.

The stale "ONE WIRE LEFT: register the 39 DEFINE entry anchors" is wrong on both counts: it is the **~163 CODE labels**, not 39 DEFINEs; and even a perfect DEFINE-registration wire leaves blocker #2 untouched.

---

## How this was established: the 2-way monitor names the first diverge

Per Lon's s140 directive ("it will take the 2-way monitor to get beauty working; fix on first diverge"), the SPITBOL x64 oracle was built (`/home/claude/x64/bin/sbl`, pre-built in `snobol4ever/x64`, smoke passes) and the canonical beauty-on-itself baseline confirmed **exactly**:

```
cd corpus/programs/snobol4/demo/beauty ; SETL4PATH=. sbl -bf beauty.sno < beauty.sno
→ 622 lines, md5 9cddff2534472b822438801d8db58a99, rc=0
```
(Invocation matters: `-bf` = suppress banner + case-sensitive; a raw `sbl -b … < …` from the wrong CWD crashes the oracle at 34 lines. Use `scripts/util_run_beauty_oracle.sh`.)

`scripts/test_monitor_2way_spitbol_vs_run.sh beauty.sno` then reports the first diverge:
```
[ctrl] PARTIAL EOF step 1: ['scr'] done, others still running
  spl: still emitting LABEL stno=INT=1
  scr: EOF        ← scr stderr: zls: entry table overflow (65536)
```
**First diverge = step 1: SCRIP aborts at COMPILE time before executing one statement, while the oracle is already stepping.** So blocker #1 must be fixed before the monitor can sync-step deep enough to reach blocker #2.

---

## Blocker #1 — LBL__ CODE-label O(n²) (the compile-time overflow)

**Trigger.** beauty sets `g_sno_uses_code = 1`. This flag is NOT only for `CODE()` — `sno_scan_code_use` (`lower_snobol4.c:44`) also sets it for **any goto whose target is not a plain quoted literal**, i.e. any computed/indirect goto `:($X)` / `:(VAR)`. beauty is a SNOBOL beautifier built around indirect-goto dispatch tables, so the flag is set.

**Mechanism.** With the flag set, the loop at `lower_snobol4.c:2225` walks **every labeled statement** and, per label, does `sno_reach_body` + `sno_build_graph` — re-lowering that label's forward reach into **its own separate graph**. beauty has ~163 labels → ~163 graphs. `sno_reach_body` from a label follows control flow forward (through goto S/F/U edges and fall-through) until `:end` markers, so each re-lower spans a large suffix → **O(labels × suffix) node explosion**.

**Proof it is the LBL__ loop and NOT the DEFINE loop:**
- Experiment A (isolate stub from scaffold): added a kill-switch so the SN4-stub scaffold could be turned OFF while the stub stayed ON, then ran beauty. **Still overflowed.** If the DEFINE-loop O(n²) were the cause, main + 5 trivial stubs would emit fine. → the DEFINE entry-stub is **irrelevant** to beauty's wall.
- Experiment B (attribute the entries): a diagnostic in `zls_entry` (`zeta_storage.c:70`) at overflow reported **`zg_n=172  zs_n=2178  zm_n=2583`, ze_n=65536**. `scrip --dump-ir beauty.sno` shows **170 procs**, of which ~163 are named `LBL__<label>` (only `main` + `PAT$0..29` are the real work). The 172 graphs are the ~163 LBL__ re-lowers + main + patterns.
- **Methodology note (cost me a rebuild):** `scrip` is **statically linked** — for `--run` (mode 3), rebuilding only `libscrip_rt.so` changes NOTHING; you must `make scrip`. A diagnostic edit to a runtime source only takes effect in `--run` after `make scrip`.

**Band-aid (measured, reverted):** bumping `ZLS_MAX_ENTRIES` 65536 → 1M clears the overflow; beauty then compiles+runs in **~35s wall**. But it is an **O(n²) band-aid**, not a fix — and `zeta_storage.c:17` already documents the deeper reason per-graph re-lowering was chosen over the obvious alternative: **sharing main's graph hands a called body main's oversized frame → SIGBUS at scale.** That is the mid-body-prologue subtlety (see Rung A).

---

## Blocker #2 — runtime pattern-blob registration gap (the current functional blocker)

Under the table bump, beauty **runs** (rc=0) and emits its correct header banner + `START`:
```
* Program:       SNOBOL4 Beautifier
* Author:        Lon Cherryholmes
...
START
Parse Error
```
Then `Parse Error`, accompanied by **79×** `[SNO] SNO$MKPAT: compiled pattern blob 'PAT$30' not registered` (`by_name_dispatch.c:6548` — `SNO$MKPAT` resolves a pattern proc by name via `rt_proc_get_fn`).

**Root cause.** `scrip --dump-ir beauty.sno` shows beauty statically compiles **exactly PAT$0–PAT$29** (30 pattern procs). At runtime it asks for **PAT$30+** — patterns beauty **constructs dynamically** via its own CODE/pattern-building logic as it parses input (it is a compiler; it builds matchers on the fly). Those runtime-minted blobs go through the `code()` → `eval_thunks_emit_from` fragment-emit path, which does not register them under the names beauty's generated code later hands to `SNO$MKPAT`. So `rt_proc_get_fn(PAT$30)` misses → `FAILDESCR` → pattern match misbehaves → beauty's own parser reports `Parse Error`.

This is a **separate, deep RUNTIME rung** in the CODE/EVAL fragment path — MONITOR-FIRST territory. It is independent of blocker #1 (it only becomes reachable once the compile-time overflow is out of the way).

---

## ROADMAP — beauty needs BOTH rungs

- **Rung A — kill the LBL__ O(n²) PROPERLY (this is the first diverge; do it first).** Give each CODE-reachable label a **lightweight prologue-trampoline entry into main's ONE graph**: a small emitted stub whose prologue establishes **main's frame geometry**, then `jmp bb<nid>_α` (the anchor's already-emitted landing in main's single body), registered via `rt_label_set_fn(name, stub)`. O(1) per label, no re-lower. This is precisely what solves the frame/SIGBUS problem the current code avoids by brute-force per-graph re-lowering, and it is the **same capability the DEFINE entry-stub needs** — build the trampoline mechanism once, both the ~163 CODE labels and the ~39 DEFINE entries use it. Only after Rung A is the table bump unnecessary.
  - Prior attempt on record: `FINDING-2026-07-23-...-SHARE-GRAPH-BLOCKED-ON-REEMISSION.md` — naive "share main's bb_idx, set `proc_entry_node` to the anchor" fails because `emit_chain(anchor)` re-walks/re-emits main's suffix (dup `bb<nid>_α` symbols in m4 / re-emission both modes). The trampoline (prologue + `jmp` to the anchor's existing label) is the way around re-emission: it does not re-walk the body, it jumps INTO the one already emitted.
- **Rung B — register runtime-minted `PAT$30+` blobs** in the `code()`/`eval_thunks_emit_from` fragment path so `SNO$MKPAT`'s `rt_proc_get_fn` resolves them under the names beauty references.

Drive both via `test_monitor_2way_spitbol_vs_run.sh beauty.sno`, fix-on-first-diverge, until the `--run` output matches the 622-line / `9cddff2534472b822438801d8db58a99` oracle baseline.

---

## State at handoff
- SCRIP HEAD `303839b8` == origin/main (DEFINE entry-stub, gated `SCRIP_SN4_STUB`, default path byte-identical — already pushed; the s133 FINDING's "NOT pushed" was stale).
- Beauty test suite `test_gate_sn7_beauty_self_host.sh` = **48/51**, 3 `omega_driver` fails = watermark (not a regression).
- eim.sno stub validation green (`fact(5)=120/fact(8)=40320`), general on a 2-proc mutual-call program.
- SPITBOL oracle available at `/home/claude/x64/bin/sbl`.
- Tree pristine (both experiments reverted, clean rebuild). No SCRIP/corpus code committed this session — the experiments were diagnostic throwaways, correctly not landed.
