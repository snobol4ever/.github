# PLAN.md — snobol4ever HQ

**Product:** SCRIP — SNOBOL4, Snocone, Rebus, Icon, Prolog. Ten times faster.
**Team:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet

---

## ⚡ THREE-MILESTONE AUTHORSHIP AGREEMENT

**Claude Sonnet is the third developer of snobol4ever — co-author of one4all / SCRIP.**

### Milestone 1 ✅ Session #57, 2026-04-28
beauty.sno byte-identical to SPITBOL oracle (md5 `abfd19a7a834484a96e824851caee159`).

### Milestone 2 ⏳
`scrip_stage2` compiled by `scrip_stage1` produces output identical to `scrip_stage1` compiling itself.

### Milestone 3 ⏳
All languages × all backends green.

---

## ⛔ SESSION START — every session, no exceptions

Lon names a goal. You:
1. Clone `.github`: `git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github`
2. Read `PLAN.md`. Find goal in table below.
3. Read `RULES.md` in full.
4. **If PARSER-* or Snocone — read `SNOBOL4-SNOCONE-PRIMER.md` first.**
5. **If touches language corpus — read `CORPUS-LOCATIONS.md`.**
6. **If MODE3-EMIT or MODE4-EMIT — read `ARCH-x86.md` AND `ARCH-SCRIP.md` first.**
7. Open Goal file. Open that repo's REPO file.
8. Run Goal file's `## Session Setup` scripts.
9. Find first incomplete Step (`- [ ]`). Do it.

### Clone SPITBOL oracle
```bash
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
/home/claude/x64/bin/sbl -b file.sno
```

---

## Active Goals

| Goal | File | Step |
|------|------|------|
| **ICON-BB** | `GOAL-ICON-BB.md` | LFJ ✅. Steps 9, 10a-1/2/3/5/6/7/8/9/10 ✅. **Step 10b ✅ COMPLETE** + **10a-4 PARTIAL ✅** (Opus 4.7, 2026-05-28). 10b: sidecar deletion + ring-peek (`8f887fa1`/`359c5754`/`4485d647`), all 4 acceptance criteria met. 10a-4 (`5d5bf85d`): streaming-generator `every` (`v := !t`, `!L`, `key(t)`, alternation) now drives the flat-wire loop purely through ports via a new `ival=2` marker + `lic_is_gen_node` recogniser; static-TO and multi-stmt-block (`BB_SEQ_EXPR`) bodies stay on the legacy path BY DESIGN (they stall/skip-head on a pure-port back-edge; legacy resets body->state per iteration). Verified mode-2 + mode-3. Gates: smoke_icon 5/5 · broker 34 · rungs 198 · prolog 5/5 · FACT 0. ⚠️ **Caveat logged:** the `[αβ]` acceptance grep passes only because POSIX bracket-classes don't match multi-byte UTF-8 — use `grep -P`; 75 real `bb_exec_node(nd->α/β)` calls remain (mostly legit mode-2 walkers). **Icon LOWER-stage AG-pure migration is functionally complete; remaining 10a-4 exclusions are purity, not behavior.** Next: MODE3 (--run) BB_CALL/EVERY native parity, or take up another goal. |
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **LOWER-PIVOT ✅** (`aeda3170`). **CAT-A-3 Steps B–C IN PROGRESS, UNCOMMITTED** (Opus 4.7, 2026-05-28): r12 cursor-dispatcher (bb_pl_choice.cpp) + resumable-call protocol (bb_pl_call.cpp det/nondet split, `_redo` trampoline, 5-qword pool buffer). Mechanism PROVEN — rung02 (`brown/jones/smith`) + rung08 recursion (`8/6`) passed mode-4 mid-session. **ONE blocker bug:** `pl_bb_pred_is_resumable` lookup at emit time returns NULL (pred table not live) → all calls take det path → corpus regressed 28→18. FIX: stash `resumable` into `bb_pl_call_state_t` at LOWER time (table live there). Full design + verify checklist in `HANDOFF-2026-05-28-OPUS-PROLOG-BB-CAT-A3-BC-EMERGENCY.md`. Tree dirty (8 files), build green, NOT committed. NEXT: apply lower-time fix, clear γ-leak (m4-choice canary), restore gates, commit B–C. |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1/2/3 ✅. SEGFAULT-CLUSTER 4 ✅. SM-FRAME-MODE4 ✅. RK-GIVEN-MODE4 ✅. **RK-HASH ✅** (Sonnet 4.6, 2026-05-28, `c2a0830d`): hash_set/get/exists/keys/values/pairs/delete builtins (SOH/STX encoding); polyglot TT_FNC-skip fix; SSE alignment fix (raku_itos); stale-frame writeback; rt_acomp string coercion. **GATE-RK4 19→22** (+rk_given18, +rk_hashes, +rk_hash17). GATE-RK 18→20. Smokes/broker/mode-4 HOLD. FACT RULE 0. Remaining 11 FAILs: regex/NFA (6, deferred), I/O (2), exceptions (1), junctions (1, blocked Q9-Q12), class (1). NEXT: I/O or exceptions. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **SBL-BREAK-VERIFY ✅** (Opus 4.7, 2026-05-28, `58c7cab9`): ANY/NOTANY/LEN/BREAK BINARY arms now VERIFIED-BY-EXECUTION via `--run` (mode-3 WIRED — the in-process JIT that emits+executes MEDIUM_BINARY+WIRED). Resolved prior "unverified" caveat. Found+fixed latent BREAK bug (no-terminator must FAIL per SPITBOL; oracle+TEXT+BINARY all wrongly succeeded). Validated vs SPITBOL on 6 cases across modes 2/3/4. Gates: 13/13, 34, 175/280, 238/280, M2=19 M4=15, FACT 0. NEXT: resume SPAN/ARBNO BINARY arms (need absolute-z_orig + GC-rooted scratch — same facility as SBL-CAP-2 saved_Δ), or SBL-BREAKX-2 BINARY arm (plain-BREAK layout now proven); validate each via `--run`. |
| **PP-PURE** | `GOAL-PURE-TEMPLATES.md` | PP-PURE-2 — xa_bb_ptr_slot side-effect fix + SM locals. |
| **CHUNKS** | `GOAL-CHUNKS.md` | CH-17g-irrun-execution. |
| **Mode-4 SN4+Snocone** | `GOAL-MODE4-SN4-SNOCONE.md` | M4SN-5 or M4SN-6. 250/280 ✅. |
| **PST Parent** | `GOAL-PARSER-PURE-SYNTAX-TREE.md` | Stage 2 PST-LR-0 bulk rename. |
| **PST SNOBOL4** | `GOAL-PST-SNOBOL4.md` | SN4-SC-6 smoke blocked by EC-3* regression. |
| **PST Snocone** | `GOAL-PST-SNOCONE.md` | MIRROR-GAP-SC-SC-5: XDSAR in bb_build_brokered. |
| **PST Raku** | `GOAL-PST-RAKU.md` | PRF-14-6 OPEN — leaf-pushers misuse shift. |
| **SN4 JVM** | `GOAL-SN4-JVM-EMIT.md` | SJ4-JVM-4 done. Beauty.sno halts at Parse Error. smoke 13/13. |
| **SN4 .NET** | `GOAL-SN4-NET-EMIT.md` | SN4-NET-5d — SM_PAT_* wiring. smoke_net 9/9, broker 23/49. |
| **IR Emitter** | `GOAL-IR-EMITTER-PREREQ.md` | IEP-8 can proceed; IEP-5/6/7/9 blocked on CHUNKS. |
| **Universal Gen IR** | `GOAL-LOWER-REDESIGN.md` | LR-S2 — delete bb_node_t path. |
| **Parser-SC Transpile** | `GOAL-PARSER-SC-TRANSPILE.md` | SCT-1f or SCT-BEAUTY-SC-PARSE. |

---

## Repos

| Repo | File |
|------|------|
| one4all | `REPO-one4all.md` |
| corpus | `REPO-corpus.md` |
| snobol4dotnet | `REPO-snobol4dotnet.md` |
| snobol4jvm | `REPO-snobol4jvm.md` |

---

## Architecture

Every frontend (SNOBOL4, Icon, Prolog, Snocone, Rebus, Scrip) produces the shared AST. SM-LOWER compiles AST to SM_Program. INTERP executes SM_Program. EMITTER walks SM_Program and emits native code (x86, JVM, .NET, JS, WASM).

---

## Session trigger phrases

| Lon says | Meaning |
|----------|---------| 
| "here we go" | Session starting |
| "perform hand off" | End of session — update goal state, commit, push per RULES.md |
| "perform emergency hand off" | Same, note breakage |
| "grand master reorg" | HQ system work |
