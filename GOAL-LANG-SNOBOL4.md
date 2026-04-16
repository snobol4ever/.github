# GOAL-LANG-SNOBOL4.md — SNOBOL4 Frontend Ladder

**Repo:** one4all
**Done when:** beauty.sno self-hosts cleanly under all three modes (--ir-run,
--sm-run, --jit-run). Full corpus PASS count matches SPITBOL oracle.

**Cross-pollination:** Every bug fix in interp.c, sm_lower.c, or bb_boxes.c
immediately benefits Icon, Prolog, Raku, Snocone, Rebus sessions.
Share fixes via main — no branches.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
bash /home/claude/one4all/scripts/build_csnobol4_oracle.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_snobol4.sh          # PASS=7
bash /home/claude/one4all/scripts/test_smoke_unified_broker.sh   # PASS=47
```

---

## Architecture reminder

```
.sno → sno_parse() → Program* [LANG_SNO]
    --ir-run  → execute_program() → interp_eval()   tree-walk
    --sm-run  → sm_lower() → SM_Program → sm_interp_run()
    --jit-run → sm_lower() → SM_Program → sm_codegen() → sm_jit_run()
```

Pattern matching uses BB_SCAN. Every pattern primitive is a bb_box_fn in bb_boxes.c.
Oracle: SPITBOL x64 at /home/claude/x64/bin/sbl.

---

## scrip-monitor Protocol

⛔ Step 1 (`scrip-monitor --monitor`) runs EVERY iteration, unconditionally.
⛔ Steps 2 and 3 only if Step 1 shows DIVERGE or IR vs CSN.

```bash
# Build once per session:
bash /home/claude/one4all/scripts/build_csnobol4_archive.sh
make -C /home/claude/one4all scrip-monitor CSN_A=/home/claude/csnobol4/libcsnobol4.a

# Step 1 — ALWAYS:
BEAUTY=/home/claude/corpus/programs/snobol4/beauty
SNO_LIB=$BEAUTY /home/claude/one4all/scrip-monitor --monitor \
    $BEAUTY/beauty_${DRIVER}_driver.sno < /dev/null 2>&1 | grep -A 10 "DIVERGE\|IR vs CSN"

# Step 2 — only if Step 1 shows problem: SPITBOL diff
SNO_LIB=$BEAUTY /home/claude/x64/bin/sbl -b $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/spitbol.out 2>/dev/null
SNO_LIB=$BEAUTY timeout 30 /home/claude/one4all/scrip --ir-run $BEAUTY/beauty_${DRIVER}_driver.sno > /tmp/scrip.out 2>/dev/null
diff /tmp/spitbol.out /tmp/scrip.out | head -40

# Step 3 — only if Step 1 shows problem: OUTPUT probe → fix → rebuild → repeat
# Rebuild: make scrip && make scrip-monitor CSN_A=...
# Broker gate: bash scripts/test_smoke_unified_broker.sh
```

---

## Rung ladder

### Phase 1 — IR-run  ✅ DONE (SN-1..SN-5)
### Phase 2 — SM-run  (SN-7..SN-9, gated on SN-6)
### Phase 3 — JIT-run (SN-10..SN-12, gated on SN-9)

- [x] **SN-1** — beauty omega driver all three modes. DONE.
- [x] **SN-2** — beauty gen driver all three modes. DONE.
- [x] **SN-3** — beauty tdump driver all three modes. DONE.
- [x] **SN-4** — beauty alpha/beta/gamma drivers all three modes. DONE.
- [x] **SN-5** — beauty.sno self-hosts; all 18 driver×mode combos PASS. DONE.
- [ ] **SN-6** — Full corpus: run test_interp_broad_corpus_and_beauty.sh. IN PROGRESS: PASS=215/228.

```bash
bash /home/claude/one4all/scripts/test_interp_broad_corpus_and_beauty.sh
```

- [x] **SN-14** — Pattern primitives as typed EKind nodes. DONE.
- [x] **SN-15** — Verify all three modes still pass after SN-14. DONE.

---

## Key files

| File | Role |
|------|------|
| `src/frontend/snobol4/snobol4.y` | Bison grammar |
| `src/frontend/snobol4/snobol4.l` | Flex lexer |
| `src/driver/interp.c` | --ir-run tree-walk |
| `src/runtime/x86/sm_lower.c` | IR → SM |
| `src/runtime/x86/sm_interp.c` | SM interpreter |
| `src/runtime/x86/sm_codegen.c` | x86 JIT |
| `src/runtime/x86/bb_boxes.c` | SNOBOL4 pattern boxes |
| `src/runtime/x86/snobol4_pattern.c` | subscript, OPSYN, array helpers |
| `src/runtime/x86/snobol4.c` | ARRAY/TABLE/CONVERT builtins, array_get/set |
| `corpus/programs/snobol4/beauty/` | Beauty test suite |

---

## Invariants

- SPITBOL is the sole oracle. Fix the runtime, never the corpus source.
- Gate = Smoke PASS=7, Broker PASS=47 after every commit.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

---

## Current state (2026-04-16h, one4all HEAD 09261c1d)

SN-1..SN-5 DONE. BEAUTY SELF-HOSTS (all 18 driver×mode combos).
SN-6 IN PROGRESS: PASS=219/228 (broad corpus); crosscheck PASS=206 FAIL=1.
Smoke PASS=7. Broker PASS=49.

**Prior fixes summary (compressed):** Dynamic stacks; h_store_var JIT stack balance;
bb_capture return type DESCR_t; E_POW integer path (interp.c — was always DT_R per Icon
comment; fixed to int**int→int for non-negative exponents, matching SPITBOL);
DEFINE return null string; E_KEYWORD uppercase for &lcase/&ucase (IR+SM);
DATA field accessor/mutator SM+JIT; ARBNO SM_PAT_ARBNO opcode; ITEM/_SET in _usercall_hook;
N-dim IDX/IDX_SET; ARRAY 'lo:hi,N' parsing; CONVERT array→table (1113);
$.var<idx> SM/JIT lowering (212);
callcap union clobber (stmt_exec.c — flush_pending_callcaps and bb_callcap immediate branch
both set args[0].s=buf then args[0].ptr=NULL, zeroing the string pointer because .s/.ptr
share the same union in DESCR_t; removed both .ptr=NULL assignments).

**Next session:**
1. Fix XCALLCAP+RPOS(0) cursor threading so expr_eval passes.
   Root cause: `pat RPOS(0)` fails when pat contains `. *Push()`; pat alone works.
   bb_seq is not threading cursor from XCALLCAP output into next box. Investigate
   bb_seq / bb_callcap spec_t return value in bb_boxes.c when followed by RPOS/POS.
2. Investigate demo_claws5 (*** no match — real pattern failure).
3. Add missing wordcount.sno and roman.sno to corpus/programs/snobol4/demo/.
4. Investigate beauty_XDump driver.
5. Full broad corpus recount (fileinfo/triplet/word1/wordcount pass individually —
   likely test-script artefact; expect 221+ after expr_eval fix).

**Remaining SN-6 failures (7 real):**
- expr_eval: XCALLCAP+RPOS(0) cursor threading (see next session #1)
- Beauty: XDump driver
- demo_wordcount, demo_roman: .sno source MISSING from corpus/programs/snobol4/demo/
- demo_claws5: *** no match — real pattern failure
- fileinfo, triplet, word1, wordcount: pass individually; test-script artefact
