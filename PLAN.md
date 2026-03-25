# snobol4ever — HQ

SNOBOL4/SPITBOL compilers targeting JVM, .NET, and native C.
Shared frontends. Multiple backends.
**Team:** Lon Jones Cherryholmes (arch, MSIL), Jeffrey Cooper M.D. (DOTNET), Claude Sonnet 4.6 (TINY co-author, third developer).

---

## ⚡ NOW

Each concurrent session owns exactly one row. Update only your row on every push. `git pull --rebase` before every push — see RULES.md §CONCURRENT SESSIONS and §NOW TABLE ROW FORMAT.

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **⚠ GRAND MASTER REORG** | G-1 — ALL SESSIONS FROZEN — see GRAND_MASTER_REORG.md | `pre-reorg-freeze` | M-G0-FREEZE ❌ NEXT |
| **TINY backend** | [FROZEN] `main` B-292 — 106/106 | `acbc71e` B-292 | resume post-reorg |
| **TINY NET** | [FROZEN] `net-t2` N-248 — M-T2-NET ✅ 110/110 | `425921a` N-248 | resume post-reorg |
| **TINY JVM** | [FROZEN] `main` J-216 — STLIMIT ✅; 2D E_ARY WIP | `a74ccd8` J-216 | resume post-reorg |
| **TINY frontend** | [FROZEN] `main` F-223 — rung05 reverted clean | `b4507dc` F-223 | resume post-reorg |
| **DOTNET** | [FROZEN] `main` D-164 — 1903/1903 | `e1e4d9e` D-164 | resume post-reorg |
| **README** | [FROZEN] `main` — M-README-CSHARP-DRAFT ✅ | `00846d3` | resume post-reorg |
| **ICON frontend** | [FROZEN] `main` I-11 — rung03 5/5 PASS | `bab5664` I-11 | resume post-reorg |
| **Prolog JVM** | `main` PJ-43 — **20/20** confirmed; M-PJ-DISPLAY-BT root cause diagnosed — display/6 gamma cs re-enters gn retry on external fail-loop; minimal reproducer isolated | `38e4c39` PJ-43 | M-PJ-DISPLAY-BT: fix gamma cs pack — see PJ-44 bootstrap in FRONTEND-PROLOG-JVM.md |
| **Icon JVM** | [FROZEN] `main` IJ-29 — M-IJ-CORPUS-R20 ✅ 104/104 PASS | `7f8e3a2` IJ-29 | resume post-reorg |
| **README v2 sprint** | [FROZEN] `main` R-2 | TBD R-2 | resume post-reorg |

**Invariants (check before any work):**
- TINY: `106/106` ASM corpus (`run_crosscheck_asm_corpus.sh`) · ALL PASS ✅
- DOTNET: `dotnet test` → 1903/1903 (Linux); 0 failures

**Read the active L2 docs: [TINY.md](TINY.md) · [JVM.md](JVM.md) · [DOTNET.md](DOTNET.md)**

---

## Goals

*(Clean slate — new goals TBD.)*

---

## 4D Matrix

```
Products:   TINY (native x64) · JVM (Clojure→bytecode) · DOTNET (C#→MSIL)
Frontends:  SNOBOL4 · Snocone · Rebus · Icon · Prolog · C#/Clojure
Backends:   x64 ASM (native) · JVM bytecode · .NET MSIL
            [C backend: ☠️ DEAD — 99/106, sno2c failures on word*/pat_alt_commit; not maintained]
Matrix:     Feature matrix (correctness) · Benchmark matrix (performance)
```

| Frontend | TINY-x64 | TINY-NET | TINY-JVM | JVM | DOTNET |
|----------|:--------:|:--------:|:--------:|:---:|:------:|
| SNOBOL4/SPITBOL | ⏳ | ⏳ | — | ⏳ | ⏳ |
| Snocone | — | — | — | ⏳ | ⏳ |
| Rebus | — | — | — | — | — |
| Icon | — | — | — | — | — |
| Prolog | ⏳ | — | — | ⏳ | — |
| C#/Clojure | — | — | — | — | — |

✅ done · ⏳ active · — planned · ☠️ dead

---

## Milestone Dashboard

### ⚠ Grand Master Reorganization — ALL OTHER MILESTONES FROZEN

See [GRAND_MASTER_REORG.md](GRAND_MASTER_REORG.md) for full plan, naming law, folder structure, and success criteria.

| ID | Phase | Status |
|----|-------|--------|
| **M-G0-FREEZE** | 0 — Baseline: tag pre-reorg-freeze, record invariants | ❌ **NEXT** |
| **M-G0-AUDIT** | 0 — Baseline: `doc/EMITTER_AUDIT.md` covering all 5 emitters | ❌ |
| **M-G0-IR-AUDIT** | 0 — Baseline: `doc/IR_AUDIT.md` mapping all frontend nodes to unified enum | ❌ |
| **M-G1-IR-HEADER** | 1 — Unified IR: `src/ir/ir.h` with full EKind enum | ❌ |
| **M-G1-IR-PRINT** | 1 — Unified IR: `ir_print_node()` debugger | ❌ |
| **M-G1-IR-VERIFY** | 1 — Unified IR: `ir_verify()` structural checker | ❌ |
| **M-G2-DIRS** | 2 — Folders: `src/backend/{x64,jvm,net}/` skeleton confirmed | ❌ |
| **M-G2-MOVE-ASM** | 2 — Folders: `emit_byrd_asm.c` → `emit_x64.c` | ❌ |
| **M-G2-MOVE-JVM** | 2 — Folders: `emit_byrd_jvm.c` → `emit_jvm.c` | ❌ |
| **M-G2-MOVE-NET** | 2 — Folders: `emit_byrd_net.c` → `emit_net.c` | ❌ |
| **M-G2-MOVE-ICON-JVM** | 2 — Folders: `icon_emit_jvm.c` → `backend/jvm/emit_jvm_icon.c` | ❌ |
| **M-G2-MOVE-PROLOG-JVM** | 2 — Folders: `prolog_emit_jvm.c` → `backend/jvm/emit_jvm_prolog.c` | ❌ |
| **M-G2-MOVE-ICON-ASM** | 2 — Folders: `icon_emit.c` → `backend/x64/emit_x64_icon.c` | ❌ |
| **M-G2-MOVE-PROLOG-ASM** | 2 — Folders: Prolog ASM emitter → `backend/x64/emit_x64_prolog.c` | ❌ |
| **M-G3-NAME-X64** | 3 — Names: `emit_x64.c` naming law applied | ❌ |
| **M-G3-NAME-JVM** | 3 — Names: `emit_jvm.c` naming law applied | ❌ |
| **M-G3-NAME-NET** | 3 — Names: `emit_net.c` naming law applied | ❌ |
| **M-G3-NAME-JVM-ICON** | 3 — Names: `emit_jvm_icon.c` naming law applied | ❌ |
| **M-G3-NAME-JVM-PROLOG** | 3 — Names: `emit_jvm_prolog.c` naming law applied | ❌ |
| **M-G3-NAME-X64-ICON** | 3 — Names: `emit_x64_icon.c` naming law applied | ❌ |
| **M-G4-SHARED-CONC** | 4 — Shared wiring: `E_CONC` in `ir_emit_common.c` | ❌ |
| **M-G4-SHARED-OR** | 4 — Shared wiring: `E_OR` | ❌ |
| **M-G4-SHARED-ARBNO** | 4 — Shared wiring: `E_ARBNO` | ❌ |
| **M-G4-SHARED-CAPTURE** | 4 — Shared wiring: `E_DOT`, `E_DOLLAR` | ❌ |
| **M-G4-SHARED-ARITH** | 4 — Shared wiring: `E_ADD/SUB/MPY/DIV/MOD` | ❌ |
| **M-G4-SHARED-ASSIGN** | 4 — Shared wiring: `E_ASSIGN` | ❌ |
| **M-G4-SHARED-IDX** | 4 — Shared wiring: `E_IDX` | ❌ |
| **M-G4-SHARED-ICON** | 4 — Shared wiring: Icon generator nodes | ❌ |
| **M-G4-SHARED-PROLOG** | 4 — Shared wiring: Prolog unification/clause nodes | ❌ |
| **M-G5-LOWER-SNOBOL4** | 5 — Frontends: snobol4 lower → unified IR confirmed | ❌ |
| **M-G5-LOWER-SNOCONE** | 5 — Frontends: snocone lower → unified IR | ❌ |
| **M-G5-LOWER-ICON** | 5 — Frontends: icon lower → unified IR | ❌ |
| **M-G5-LOWER-PROLOG** | 5 — Frontends: prolog lower → unified IR confirmed | ❌ |
| **M-G5-LOWER-REBUS** | 5 — Frontends: rebus lower → unified IR | ❌ |
| **M-G6-ICON-NET** | 6 — Matrix: Icon → .NET rung01 PASS | ❌ |
| **M-G6-PROLOG-NET** | 6 — Matrix: Prolog → .NET rung01 PASS | ❌ |
| **M-G6-SNOCONE-JVM** | 6 — Matrix: Snocone → JVM corpus PASS | ❌ |
| **M-G6-SNOCONE-NET** | 6 — Matrix: Snocone → .NET corpus PASS | ❌ |
| **M-G6-REBUS-JVM** | 6 — Matrix: Rebus → JVM PASS | ❌ |
| **M-G6-REBUS-NET** | 6 — Matrix: Rebus → .NET PASS | ❌ |
| **M-G6-SCRIPTEN-ALL** | 6 — Matrix: Scripten → all 3 backends rung01 PASS | ❌ |
| **M-G7-STYLE-DOC** | 7 — Style: `doc/STYLE.md` written | ❌ |
| **M-G7-STYLE-BACKENDS** | 7 — Style: all backend files conform | ❌ |
| **M-G7-STYLE-FRONTENDS** | 7 — Style: all frontend files conform | ❌ |
| **M-G7-UNFREEZE** | 7 — Style: post-reorg-baseline tagged; all sessions resume | ❌ |

Full plan → [GRAND_MASTER_REORG.md](GRAND_MASTER_REORG.md)

> Completed milestones → [MILESTONE_ARCHIVE.md](MILESTONE_ARCHIVE.md)
> One row per **active or future** milestone. ✅ rows move to archive on session end.

### TINY backend — Active + Upcoming

| ID | Trigger | Status |
|----|---------|--------|
| **M-BUG-IS-DIALECT** | `is` driver fix — arg staging -32 fix (B-286) | ✅ |
| **M-BUG-TDUMP-TLUMP** | `TDump` driver fix — same root fix (B-286) | ✅ |
| **M-BUG-GEN-BUFFER** | `Gen` driver fix — same root fix (B-286) | ✅ |
| **M-BUG-SEMANTIC-NTYPE** | `semantic` driver fix — same root fix (B-286) | ✅ |
| **M-BUG-BOOTSTRAP-PARSE** | beauty bootstrap: *Parse scan-retry fails — shared static DATA template; ARBNO depth stale across scan attempts. E_VART+DATA slot zeroing fixed (B-288). Remaining: M-T2-INVOKE or scan-reset fix. | ❌ |
| **M-BEAUTIFY-BOOTSTRAP-ASM-MONITOR** | Run monitor on beauty.sno (Sprint M5): get ASM trace stream flowing, find first divergence, fix r12 DATA-block clobber. Prerequisites: BSS fix ✅ (B-291), TRACE_SET_CAP 256 ✅ (B-291). Remaining: TERMINAL= trace capture to file; diff CSN(92601 events) vs ASM; first diverging line names the r12 clobber site. | ❌ **NEXT** |
| **M-SNO2C-FOLD** | sno2c lexer folds identifiers to uppercase; `-F`/`-f` switches | ❌ |
| **M-MON-BUG-SPL-EMPTY** | SPITBOL trace empty for treebank/claws5 — diagnose + fix | ❌ |
| **M-MON-BUG-ASM-DATATYPE-CASE** | ASM DATA type name lowercase; fix to uppercase | ❌ |
| **M-MON-BUG-JVM-WPAT** | JVM pattern datatype emits empty string; fix | ❌ |
| **M-MONITOR-4DEMO** | roman + wordcount + treebank pass all 5 participants | ❌ |
| **M-BEAUTIFY-BOOTSTRAP** | beauty.sno reads + writes itself; fixed point | ❌ |
| **M-MONITOR-GUI** | 🌙 HTML/React monitor GUI — diverging cells highlighted | 💭 |

### Prolog Frontend — Puzzle Corpus

Each milestone: write solution in puzzle_NN.pro, verify correct answer via swipl.

| ID | Puzzle | Status |
|----|--------|--------|
| **M-PZ-01** | Bank positions — Brown/Jones/Smith, cashier/manager/teller | ✅ |
| **M-PZ-02** | Clark/Daw/Fuller — carpenter/painter/plumber, earnings + heard-of clues | ✅ |
| **M-PZ-03** | Triple engagement party — 6 people, age constraints, equal couple sums | ✅ swipl PASS; JVM over-generates (M-PJ-DISPLAY-BT open) |
| **M-PZ-04** | Milford occupations — income doubling chain + $3776 gap | ✅ |
| **M-PZ-05** | First National Bank — Brown/Clark/Jones/Smith, chess + proximity clues | ✅ |
| **M-PZ-06** | Clark/Jones/Morgan/Smith — butcher/druggist/grocer/policeman | ✅ |
| **M-PZ-07** | Brown/Clark/Jones/Smith — age/golf/income/conservatism ordering | ✅ |
| **M-PZ-08** | Dept store Ames/Brown/Conroy/Davis/Evans — roommate/bachelor/marriage clues | ✅ |
| **M-PZ-09** | Empire dept store Allen/Bennett/Clark/Davis/Ewing — lunch hours + cribbage | ✅ |
| **M-PZ-10** | Five J-names — Father/Son banquet + naming convention + friendship | ✅ |
| **M-PZ-11** | Smith family — grocer/lawyer/postmaster/preacher/teacher + blood relations | ✅ swipl PASS; JVM 2L (over-generates) |
| **M-PZ-12** | Stillwater High — 6 teachers × 6 subjects + father/roommate clues | ✅ |
| **M-PZ-13** | Murder case — Clayton/Forbes/Graham/Holgate/McFee/Warren × 6 roles | ✅ |
| **M-PZ-14** | Golf scores — Bill/Ed/Tom wives, two couples same total, Ed's wife beats Bill's | ✅ |
| **M-PZ-15** | Vernon/Wilson/Yates — architect/doctor/lawyer + 3 secretaries, floor ordering | ✅ |
| **M-PZ-16** | Train crew Art/John/Pete/Tom — brakeman/conductor/engineer/fireman + family | ✅ |
| **M-PZ-17** | Country Club dance — Ed/Frank/George/Harry wives, dance exchange snapshot | ✅ |
| **M-PZ-18** | Luncyville shopping — Abbott/Briggs/Culver/Denny, day constraints per store | ✅ |
| **M-PZ-19** | Office floors — Allen/Brady/McCoy/Smith, floor arithmetic constraints | ✅ |
| **M-PZ-20** | Pullman car — Adams/Brown/Clark/Davis, 4 fields, book exchange constraints | ✅ |

### Prolog JVM — Active

| ID | Trigger | Status |
|----|---------|--------|
| **M-PJ-CORPUS-R10** | Rung 10: Lon's puzzle corpus PASS | ✅ |
| **M-PJ-R10-SEARCH** | Rewrite hardcoded puzzles as proper Prolog search | ❌ |
| **M-PJ-PZ08** | puzzle_08 real search — swipl PASS | ✅ |
| **M-PJ-PZ09** | puzzle_09 real search — swipl PASS | ✅ |
| **M-PJ-PZ10** | puzzle_10 real search — swipl PASS | ✅ |
| **M-PJ-PZ11** | puzzle_11 real search — swipl PASS | ✅ |
| **M-PJ-NEQ** | `\=/2` missing from `pj_emit_goal` — add emit with trail-save/unwind | ✅ |
| **M-PJ-STACK-LIMIT** | Fix `.limit stack` over-estimate in `prolog_emit_jvm.c` — eliminate VerifyError on 5+ clause predicates | ✅ |
| **M-PJ-NAF-TRAIL** | Fix `\+` trail corruption — save/unwind on both inner paths | ✅ |
| **M-PJ-BODYFAIL-TRAIL** | Fix body-fail trail: `bodyfail_N` trampoline unwinds clause trail on body goal failure | ✅ |
| **M-PJ-BETWEEN** | `between/3` missing from `pj_emit_goal` — fixes puzzle_19 NoSuchMethodError | ✅ |
| **M-PJ-DISJ-ARITH** | Plain `;` retry loop in `pj_emit_body` — tableswitch dispatch; fixes puzzle_12 silent 0L | ✅ |
| **M-PJ-DISPLAY-BT** | puzzle_03 display/6 over-generation — not_dorothy 2-clause retry; ITE cut leak | ❌ |
| **M-PJ-NAF-INNER-LOCALS** | NAF helper method — fix frame aliasing; puzzle_18 PASS; 20/20 | ✅ |
| **M-PJ-CUT-UCALL** | `!` + ucall body sentinel propagation | ✅ |
| **M-PJ-DISPLAY-BT** | puzzle_03 over-generation — not_dorothy 2-clause retry | ❌ **NEXT** |
| **M-PJ-PZ-ALL-JVM** | All 20 puzzle solutions pass JVM | ✅ |

Full sprint detail → [BACKEND-JVM-PROLOG.md](BACKEND-JVM-PROLOG.md) · [FRONTEND-PROLOG-JVM.md](FRONTEND-PROLOG-JVM.md)

### ICON Frontend — Active

| ID | Trigger | Status |
|----|---------|--------|
| **M-ICON-CORPUS-R3** | Rung 3: user procedures + generators | ✅ |
| **M-ICON-STRING** | `ICN_STR`, `\|\|` concat | ❌ **NEXT** |
| **M-ICON-SCAN** | `E ? E` string scanning | ❌ |
| **M-ICON-CSET** | Cset literals → BREAK/SPAN/ANY | ❌ |
| **M-ICON-CORPUS-R4** | Rung 4: string operations and scanning | ❌ |

Full sprint detail → [FRONTEND-ICON.md](FRONTEND-ICON.md)



### Icon JVM Frontend — Active

| ID | Trigger | Status |
|----|---------|--------|
| **M-IJ-SCAFFOLD** | `icon_emit_jvm.c` exists; `-jvm null.icn → null.j` assembles + exits 0 | ✅ |
| **M-IJ-HELLO** | `every write(1 to 5);` → JVM `1\n2\n3\n4\n5` | ✅ |
| **M-IJ-CORPUS-R1** | All 6 rung01 tests PASS vs ASM oracle | ✅ |
| **M-IJ-PROC** | rung02_proc: user procedures + locals | ✅ |
| **M-IJ-CORPUS-R2** | rung02 arith_gen 5/5 + proc 3/3 PASS | ✅ |
| **M-IJ-SUSPEND** | `suspend E` generators via tableswitch resume | ✅ |
| **M-IJ-CORPUS-R3** | rung03_suspend PASS | ✅ |
| **M-IJ-STRING** | `ICN_STR`, `\|\|` concat | ✅ |
| **M-IJ-SCAN** | `E ? E` string scanning | ✅ |
| **M-IJ-CSET** | Cset literals → BREAK/SPAN/ANY | ✅ |
| **M-IJ-CORPUS-R4** | Rung 4: string ops + scanning PASS | ✅ |
| **M-IJ-CORPUS-R5** | Rung 5: not/neg/to-by/str-relops all PASS | ✅ |
| **M-IJ-CORPUS-R8** | Rung 8: find/match/tab/move builtins PASS | ✅ |
| **M-IJ-CORPUS-R9** | Rung 9: until/repeat loop emitters PASS | ✅ |
| **M-IJ-CORPUS-R10** | Rung 10: augop (+=/*=/-=//=/%=), break, next emitters; 5/5 rung10 PASS | ✅ |
| **M-IJ-CORPUS-R11** | Rung 11: `||:=` string augop + `!E` bang generator | ✅ |
| **M-IJ-CORPUS-R12** | Rung 12: string relops + ICN_SIZE (*s) + ij_expr_is_string(ICN_IF) fix; 64/64 PASS | ✅ |
| **M-IJ-CORPUS-R13** | Rung 13: ICN_ALT β-resume gate (indirect-goto per JCON §4.5); enables `every s ||:=("a"\|"b"\|"c")` | ✅ |
| **M-IJ-CORPUS-R14** | Rung 14: ICN_LIMIT (`E \ N`) limitation operator | ✅ |
| **M-IJ-CORPUS-R15** | Rung 15: ICN_REAL, ICN_SWAP (:=:), ICN_LCONCAT (|||) | ✅ |
| **M-IJ-CORPUS-R16** | Rung 16: ICN_SUBSCRIPT s[i] + if-cond String drain fix | ✅ |
| **M-IJ-CORPUS-R17** | Rung 17: real arith (dadd/dmul), integer()/real()/string() builtins | ✅ |
| **M-IJ-CORPUS-R18** | Rung 18: real relops (dcmpl/dcmpg), mixed int/real, ICN_ALT realness | ✅ |
| **M-IJ-CORPUS-R19** | Rung 19: ICN_POW (^) + real to-by generator; parse_pow + dneg fix | ✅ |
| **M-IJ-CORPUS-R20** | Rung 20: ICN_SECTION s[i:j] + ICN_SEQ_EXPR (E;F); 104/104 PASS | ✅ |
| **M-IJ-CORPUS-R21** | Rung 21: next corpus rung | ❌ **NEXT** |

| **M-IJ-CORPUS-R10** | Rung 10: next rung corpus PASS | ❌ **NEXT** |

Full sprint detail → [FRONTEND-ICON-JVM.md](FRONTEND-ICON-JVM.md)

### Grid + README v2 — Active

| ID | Repo | Status |
|----|------|--------|
| **M-FEAT-JVM** | snobol4jvm | ❌ **NEXT** |
| **M-FEAT-DOTNET** | snobol4dotnet | ❌ |
| **M-GRID-BENCH** | .github | ❌ |
| **M-GRID-CORPUS** | .github | ❌ |
| **M-GRID-COMPAT** | .github | ❌ |
| **M-GRID-REFERENCE** | .github | ❌ |
| **M-GRID-STARTUP** | .github | ❌ |
| **M-GRID-OPERATOR** | .github | ❌ |
| **M-GRID-SWITCH-FULL** | .github | ❌ |
| **M-README-V2-X** | snobol4x | ❌ |
| **M-README-V2-JVM** | snobol4jvm | ❌ |
| **M-README-V2-DOTNET** | snobol4dotnet | ❌ |
| **M-PROFILE-V2** | .github | ❌ |

Full trigger specs → [GRIDS.md](GRIDS.md)

---

## L2/L3 Index

| File | Level | What |
|------|-------|------|
| [TINY.md](TINY.md) | L2 | snobol4x — HEAD, build, active sprint, pivot log |
| [JVM.md](JVM.md) | L2 | snobol4jvm — HEAD, lein commands, active sprint |
| [DOTNET.md](DOTNET.md) | L2 | snobol4dotnet — HEAD, dotnet commands, active sprint |
| [RULES.md](RULES.md) | L3 | Mandatory rules ← **read every session** |
| [BEAUTY.md](BEAUTY.md) | L3 | beauty.sno subsystem test plan: 19 drivers |
| [MONITOR.md](MONITOR.md) | L3 | 5-way monitor design and runner |
| [ARCH.md](ARCH.md) | L3 | Byrd Box model, shared architecture |
| [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md) | L3 | Full session history — append-only |
| [MILESTONE_ARCHIVE.md](MILESTONE_ARCHIVE.md) | L3 | All ✅ completed milestone rows |
| [FRONTEND-PROLOG.md](FRONTEND-PROLOG.md) | L3 | Prolog frontend sprint detail |
| [FRONTEND-ICON.md](FRONTEND-ICON.md) | L3 | Icon frontend sprint detail |
| [FRONTEND-PROLOG-JVM.md](FRONTEND-PROLOG-JVM.md) | L3 | Prolog→JVM frontend sprint detail |
| [FRONTEND-ICON-JVM.md](FRONTEND-ICON-JVM.md) | L3 | Icon→JVM frontend sprint detail |
| [TESTING.md](TESTING.md) | L3 | Corpus ladder, oracle index |
| [PATCHES.md](PATCHES.md) | L3 | Runtime patch audit trail |

---

*PLAN.md = L1 index only. ~3KB max. No sprint content. No step content. No completed milestone rows. Ever.*
*Milestone fires → move its row to MILESTONE_ARCHIVE.md, update NOW table, update L2 doc.*
