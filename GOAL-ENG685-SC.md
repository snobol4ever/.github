# GOAL-ENG685-SC.md — ENG685 Snocone (.sc) Conversions

**Repo:** one4all (test/demo/) + corpus (programs/snobol4/demo/)
**Done when:** claws5.sc and treebank.sc pass under scrip --ir-run, --sm-run, --jit-run, output matches .sno SPITBOL output.

---

## Context

Source files (one4all/test/demo/):
- `claws5.sno`   — PASS under SPITBOL -b. Clean, Python names.
- `treebank.sno` — PASS under SPITBOL -b. Clean, Python names.
- `claws5.sc`    — Written. pp_mem loop termination broken (sk[si,1] exhaustion check).
- `treebank.sc`  — Written. Untested (scrip binary path issue at session end).

Both use the one-big-pattern technique with NRETURN side-effect functions.
Function names match Python assignment3.py exactly.

Key pattern technique (see RULES.md):
- Single NRETURN function, two call forms:
  `(word . tag) . *push_list(tag)`   — deferred call with captured arg
  `(epsilon . *push_list('BANK'))`   — zero-width hook with literal

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh          # also: apt-get install -y libgc-dev
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

Test data locations:
- claws5:    /home/claude/corpus/programs/snobol4/demo/CLAWS5inTASA.dat
- treebank:  /home/claude/one4all/test/demo/VBGinTASA.dat  (copy of treebank.input)

Run .sno files from data directory:
```bash
cd /home/claude/corpus/programs/snobol4/demo && /home/claude/x64/bin/sbl -b /home/claude/one4all/test/demo/claws5.sno
cd /home/claude/one4all/test/demo            && /home/claude/x64/bin/sbl -b treebank.sno
```

Run .sc files (stdin):
```bash
SCRIP=/home/claude/one4all/scrip
head -3 /home/claude/corpus/programs/snobol4/demo/CLAWS5inTASA.dat | timeout 30 $SCRIP --ir-run /home/claude/one4all/test/demo/claws5.sc
cat /home/claude/one4all/test/demo/VBGinTASA.dat | timeout 30 $SCRIP --ir-run /home/claude/one4all/test/demo/treebank.sc
```

---

## Steps

- [x] **SC-1** — claws5.sno working under SPITBOL -b. Python names: init(), new_sent(), add_tok().
- [x] **SC-2** — treebank.sno working under SPITBOL -b. Python names: init_list(v), push_list(v), push_item(v), pop_list(), pop_final(v).
- [ ] **SC-3** — Fix claws5.sc pp_mem loop: SORT returns 2-col array; loop terminates when sk[si,1] is empty. Use explicit variable `sk1 = sk[si,1]; if (~DIFFER(sk1)) goto done` — already in code but check the DIFFER logic ordering vs GT(si,1) guard. Also confirm scrip binary at /home/claude/one4all/scrip.
- [ ] **SC-4** — Test treebank.sc --ir-run. DATA('list(head,tail)') syntax, push_list/push_item nreturn pattern, DATATYPE check uses REPLACE(&LCASE,&UCASE) for portability.
- [ ] **SC-5** — Test both under --sm-run and --jit-run. Gate: output matches SPITBOL ref.
- [ ] **SC-6** — (stretch) beauty.sno under SPITBOL -b from beauty/ directory with all -INCLUDE files.

---

## Known issues

**claws5.sc pp_mem:** SORT produces an N×2 array. The termination check `if (~DIFFER(sk1))` should work when si exceeds array bounds (returns empty). But the loop has a GT(si,1) OUTPUT guard that may fire before the DIFFER check. Fix: move DIFFER check to top of loop before the GT guard. Pattern in .sno:
```
pp_s   si = si + 1
       sk[si,1]          :F(pp_s_done)   ← termination: :F when out of bounds
       si GT(si,1) OUTPUT = '   },'      ← only if si > 1
```
In .sc: `if (~DIFFER(sk1)) { goto pp_s_done; }` then `if (GT(si, 1)) { OUTPUT = ...; }`.

**treebank.sc DATA():** Confirm `DATA('list(head,tail)');` works in scrip. If not, use struct: `struct list { head, tail }`.

**scrip binary:** Always at `/home/claude/one4all/scrip` after `build_scrip.sh`. Requires `libgc-dev` installed.

---

## State (2026-04-16 session end)

claws5.sno:   PASS SPITBOL -b. one4all/test/demo/. HEAD: (see commit)
treebank.sno: PASS SPITBOL -b. one4all/test/demo/. HEAD: (see commit)
claws5.sc:    Written, pp_mem broken. SC-3 next.
treebank.sc:  Written, untested.  SC-4 next.
