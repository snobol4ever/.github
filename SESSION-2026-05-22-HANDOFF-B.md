# SESSION HANDOFF — 2026-05-22-B (ICN-T-2 partial + goal renames)

## Repos at handoff

| Repo | HEAD |
|------|------|
| SCRIP | `cf9284f5` |
| corpus | `3e223db` |
| .github | `3505eaa7` (pre-handoff-doc) |

## Gate

**PASS=409 FAIL=0 STUB=645** — unchanged from session start. Zero regressions.

## What was done this session

### Goal file renames (.github)

- `GOAL-ICON-BB-COMPLETE.md` → `GOAL-ICON-BB.md` (remove confusing -COMPLETE and -JCON suffixes; this is the active Icon BB goal)
- `GOAL-PROLOG-BB-JCON.md` — **untouched** (Prolog session owns this)
- Title lines inside both files updated to match.

### ICN-T-2 partial (GOAL-BB-TEMPLATE-LADDER)

| Item | Status |
|------|--------|
| `corpus/programs/icon/rung01_paper_to_by.icn` + `.expected` | ✅ committed `3e223db` — step-up (1 to 10 by 3), step-down (10 to 1 by -3), single-value (2 to 2 by 1). All pass under `--run`. |
| `src/emitter/BB_templates/bb_icn_to_by.c` | ✅ committed `cf9284f5` — stub with IS_X86/JVM/JS/NET/WASM arms per RULES.md |
| `src/emitter/BB_templates/bb_templates.h` | ✅ committed — `void bb_icn_to_by(BB_t * pBB)` declared |
| `emit_core.c` — pull `BB_ICN_TO_BY` out of stub fallthrough | ⏳ **PENDING** |
| `Makefile` — add bb_icn_to_by.c to SRCS + build rule | ⏳ **PENDING** |
| Freeze per-kind baseline | ⏳ after emit_core + Makefile wired |

## NEXT: complete ICN-T-2

```bash
# 1. emit_core.c: separate BB_ICN_TO_BY from stub fallthrough
#    Change:
#      case BB_ICN_TO_BY:   (falls through to bb_icn_stub)
#    To:
#      case BB_ICN_TO_BY:   bb_icn_to_by(nd); return 0;

# 2. Makefile: add after bb_icn_to lines:
#    SRCS: $(SRC)/emitter/BB_templates/bb_icn_to_by.c \
#    build rule: $(CC) $(CRT) -c $(SRC)/emitter/BB_templates/bb_icn_to_by.c -o $(OBJ)/bb_icn_to_by.o

# 3. make -j4 scrip

# 4. bash scripts/test_per_kind_diff.sh   # expect PASS=409 FAIL=0 STUB=645 or better

# 5. bash scripts/test_icon_all_rungs.sh --rung rung01  # rung01_paper_to_by must PASS

# 6. bash scripts/freeze_per_kind_baseline.sh  (if STUB count changes)

# 7. Mark ICN-T-2 [x] in GOAL-BB-TEMPLATE-LADDER.md, update watermark
# 8. Update PLAN.md BB Template Ladder row: NEXT ICN-T-3
# 9. Commit SCRIP, .github; push .github last
```

## Session start protocol for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus /home/claude/corpus
# Read PLAN.md, RULES.md, GOAL-BB-TEMPLATE-LADDER.md
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip
bash scripts/test_per_kind_diff.sh
# Expect: PASS=409 FAIL=0 STUB=645 at SCRIP cf9284f5
```

## Note on session health

Context window was ~75%+ by end of session. Several navigation errors occurred (wrong goal renamed twice). Start fresh next session.
