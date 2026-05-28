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
| **Prolog BB** | `GOAL-PROLOG-BB.md` | **WAM-CP-1/2/3/4 ✅** (Opus 4.7, 2026-05-28). **WAM-CP-5 ✅ COMPLETE** (Sonnet 4.6, 2026-05-28, `414d5da3`/`60dea34f`/`b1e27f56`): BB_CHOICE+BB_PL_CALL migrate rsp-frame cursor to heap `pl_choice` via `pl_cp_push/pop`; compound args via `emit_build_compound_term`; `rt_pl_arith` extended with bitwise/shift/max/min/mod/power. full mode-4 (with .expected) 40/107 (+7). GATE-1 5/5, GATE-2 132/0, GATE-3 91/107, GATE-4 4/4, FACT 0. **NEXT: WAM-CP-6 (LCO)** or fix open bugs: `**` power prefix clash with `*` in `rt_pl_arith`; unary sign/truncate/integer (different BB path). |
| **Raku BB** | `GOAL-RAKU-BB.md` | RK-BB-1/2/3 ✅. SEGFAULT-CLUSTER 4 ✅. SM-FRAME-MODE4 ✅. RK-GIVEN-MODE4 ✅. **RK-HASH ✅** (Sonnet 4.6, 2026-05-28, `c2a0830d`): hash_set/get/exists/keys/values/pairs/delete builtins (SOH/STX encoding); polyglot TT_FNC-skip fix; SSE alignment fix (raku_itos); stale-frame writeback; rt_acomp string coercion. **GATE-RK4 19→22** (+rk_given18, +rk_hashes, +rk_hash17). GATE-RK 18→20. Smokes/broker/mode-4 HOLD. FACT RULE 0. Remaining 11 FAILs: regex/NFA (6, deferred), I/O (2), exceptions (1), junctions (1, blocked Q9-Q12), class (1). NEXT: I/O or exceptions. |
| **SNOBOL4 BB** | `GOAL-SNOBOL4-BB.md` | **M3-NATIVE-4 SBL-CAP-2 ✅** (Opus 4.7, 2026-05-28, `e9a9d7f3`): bb_capture.cpp BINARY arm fixed — proper gate, deque-int scratch (NOT GC_MALLOC; bb_pool is mmap'd, GC can't see baked imm64), push/pop r10 around child_fn, sites {40, 49(def), 77, 124}, internal jmp rel32=32. Native corpus **156→165/280** (+9: 039/040/042/043_pat_any/notany/break/len + 058/059 capture_dot/dollar + W07_capt_×3). Zero baseline regressions. Established the deque-int allocator as the GC-safe pattern for per-template BINARY scratch — reuse in SBL-SPAN-2, SBL-ARBNO-3, SBL-BREAKX-2. Earlier this day: LANG-IGNORANT SM TEMPLATES (`08e05f68`, split SM_BB_SWITCH into INVOKE/PL_INVOKE, Icon 0/5 expected per Lon directive); M3-NATIVE-2 (`sm_run_native` template-pure runner), 2b (JUMP/RETURN BINARY arms + two-pass rel32), 3 (BB call-out confirmed native). Gates: G1=13/13, G2=31, G3=175/280, G4=238/280, rungs M2=19/M4=15, FACT=0, audit GATE OK. **NEXT:** knock down remaining ~73 native-only failures by cluster — SPAN, ALT (combinator deferred), ARBNO, FENCE, then flip default off `SCRIP_M3_NATIVE` getenv. See GOAL file (pruned this session 363→287 lines). |
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
