# GOAL-ENG685-SC.md — ENG685 Snocone (.sc) Conversions

**Repo:** corpus  
**Done when:** claws5.sc and treebank.sc pass under scrip --ir-run, --sm-run, --jit-run.

---

## Context

SNOBOL4 versions (corpus/programs/snobol4/demo/):
- `claws5.sno` — PASS under SPITBOL x64. HEAD fd21aa6 on corpus.
- `treebank.sno` — PASS under SPITBOL x64. HEAD fd21aa6 on corpus.

Both use the one-big-pattern technique: `(PAT . tx)  (epsilon . *func())`
as in beauty.sno ShiftReduce. See assignment3.py for the Python originals.

SNOCONE package: uploaded as SNOCONE.zip. Key dialect facts:
- Comments: `//`
- String concat: `&&`
- Procedures: `procedure name(args, locals) { body }`
- File I/O: `input__(.var, unit, '', filename)` (NOT `INPUT(.var, unit, file)`)
- goto: `goto LABEL;` (one word, unlike Snocone spec's `go to`)
- nreturn: `nreturn;` keyword (for pattern side-effect hooks)
- DATATYPE: scrip returns uppercase ('STRING', 'INTEGER', etc.)
- Pattern operators: identical to SNOBOL4

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Test data (create in working dir):
```bash
# For claws5:
echo "1_CRD :_PUN the_AT1 cat_NN1 sat_VVD 2_CRD :_PUN running_VVG is_VBZ fun_JJ " \
  > /tmp/claws_test/CLAWS5inTASA.dat

# For treebank:
cat > /tmp/tb_test/VBGinTASA.dat << 'DAT'
(S (NP (DT The) (NN cat)) (VP (VBZ is) (VP (VBG running) (NP (DT the) (NN race)))))
DAT
```

Run tests:
```bash
cd /tmp/claws_test && timeout 10 /home/claude/one4all/scrip --ir-run /path/to/claws5.sc
cd /tmp/tb_test   && timeout 10 /home/claude/one4all/scrip --ir-run /path/to/treebank.sc
```

---

## Steps

- [ ] **SC-1** — Fix claws5.sc:
  1. Replace `+num` with `INTEGER(num)` in `ci_new_sent()`
  2. Fix `goto ci_done` label in `ci_add_tok()` — may need `ci_done:` on its own line
     outside the if-else chain in scrip's clause parser
  3. Fix `pp_mem()` — Error 5 (undefined function) at statement 16; likely
     the nested while loop with `DIFFER(sk[si,1])` needs explicit variable assignment
     rather than inline array index test. Use: `sk_key = sk[si,1]; if (~DIFFER(sk_key))`
  4. Verify: pattern fires ci_init, ci_new_sent, ci_add_tok correctly on stub data
  5. Gate: output matches claws5.sno SPITBOL output on same stub input

- [ ] **SC-2** — Write treebank.sc:
  - DATA('list(head,tail)') — same as .sno version
  - All stack procedures: stk_push_frame, stk_push_item, stk_pop_into_parent, stk_pop_final
  - All λ hooks: tb_init, tb_push_bank, tb_push_root, tb_push_list, tb_push_item,
    tb_pop_list, tb_pop_final
  - group pattern with *group recursive reference (identical to .sno)
  - treebank_pat one big pattern (identical to .sno)
  - pp_node: REPLACE(DATATYPE(node), &LCASE, &UCASE) vs 'STRING' for portability
    (scrip returns uppercase so IDENT(DATATYPE(node), 'STRING') also works directly)
  - File I/O: input__(.rdch, 8, '', 'VBGinTASA.dat')
  - Gate: output matches treebank.sno SPITBOL output on same stub input

- [ ] **SC-3** — Test all 3 modes: --ir-run, --sm-run, --jit-run for both files

---

## Known issues from previous session (2026-04-16)

claws5.sc debugging findings:
- `input__(.rdch, 8, '', filename)` is the correct file-open form
- `+num` (unary +) does NOT work in scrip for string→integer; use `INTEGER(num)`
- Pattern side-effects (`epsilon . *fn()`) work correctly in scrip Snocone
- `goto ci_done` inside `ci_add_tok` — clause parser may misparse label inside
  if/else; test with label on its own statement line
- `pp_mem()` Error 5 at stmt 16 — SORT works; issue is in nested while loops
  using array index expressions as DIFFER argument

The pattern itself (`claws_pat`) was verified MATCHED on inline string test data.
The file-slurp path (`input__` → while loop → `src = src && line && ' '`) was
not yet verified to produce the correct `src` string.

## State (2026-04-16 session end)

claws5.sno: PASS SPITBOL. corpus HEAD fd21aa6.  
treebank.sno: PASS SPITBOL. corpus HEAD fd21aa6.  
claws5.sc: pattern logic verified on inline data. File I/O + pp_mem still broken.  
treebank.sc: not yet written.  
