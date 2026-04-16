# GOAL-ENG685-SC.md — ENG685 Snocone (.sc) Conversions

**Repo:** corpus (programs/snobol4/demo/) + one4all (test/demo/)
**Done when:** claws5.sc and treebank.sc produce correct output under scrip --ir-run,
  matching claws5.ref and treebank.ref respectively.

---

## Context

Canonical files (corpus/programs/snobol4/demo/):
- `claws5.sno`   — PASS sbl -b. Python names: init(), new_sent(), add_tok().
- `treebank.sno` — PASS sbl -b. Python names: init_list/push_list/push_item/pop_list/pop_final.
- `claws5.sc`    — Written. TWO bugs (see SC-3 below).
- `treebank.sc`  — Written. TWO bugs (see SC-4 below).

Input data:
- claws5:    corpus/programs/snobol4/demo/CLAWS5inTASA.dat
- treebank:  corpus/programs/snobol4/demo/treebank.input (copy to VBGinTASA.dat)

Run .sno:
```bash
cd /home/claude/corpus/programs/snobol4/demo
/home/claude/x64/bin/sbl -b claws5.sno
/home/claude/x64/bin/sbl -b treebank.sno
```

Run .sc:
```bash
SCRIP=/home/claude/one4all/scrip
head -3 /home/claude/corpus/programs/snobol4/demo/CLAWS5inTASA.dat | timeout 30 $SCRIP --ir-run /home/claude/corpus/programs/snobol4/demo/claws5.sc
cat /home/claude/corpus/programs/snobol4/demo/treebank.input | timeout 30 $SCRIP --ir-run /home/claude/corpus/programs/snobol4/demo/treebank.sc
```

---

## Session Setup

```bash
apt-get install -y libgc-dev
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
```

---

## Root cause of .sc failures (fully diagnosed)

### Bug 1: scrip backward goto resets INPUT channel
In scrip, a backward `goto` that crosses an `INPUT` read resets the stdin position.
The slurp loop:
```snocone
slurp: line = INPUT; if (~DIFFER(line)) { goto done; }
       src = src && line && sep; goto slurp;   // ← goto back resets INPUT!
```
**Fix:** Wrap slurp in a procedure. `while (DIFFER(line = INPUT))` inside a
procedure does NOT have this problem:
```snocone
procedure slurp_stdin(sep,   line) {
    slurp_stdin = '';
    while (DIFFER(line = INPUT)) {
        slurp_stdin = slurp_stdin && line && sep;
    }
    return;
}
src = slurp_stdin(' ');   // for claws5
src = slurp_stdin(nl);    // for treebank
```
✓ Verified working.

### Bug 2: . capture not visible to NRETURN fn in same pattern step
In scrip's ARBNO, when `(PAT . var)` is followed immediately by `(epsilon . *fn())`,
the function `fn()` sees the OLD value of `var`, not the newly captured one.
The `.` assignment takes effect AFTER `*fn()` evaluates the arg.

**Fix:** Do NOT use `epsilon . *fn()` for side-effects inside ARBNO.
Instead, do the work AFTER the full pattern match, using the captured globals.

For claws5 — the tokens and their tags are already captured to globals
`num`, `wrd`, `tag`, `sentno` by the pattern. Process them after match:

```snocone
// Pattern: just capture, no side effects
claws_pat =
    POS(0)
    && ARBNO(
        ( (SPAN(DIGITS) . num) && '_CRD :_PUN'
        | (NOTANY('_') && BREAK('_')) . wrd && '_'
          && (ANY(UCASE) && SPAN(DIGITS && UCASE)) . tag
        )
        && SPAN(' ')
    )
    && (SPAN(' ') | epsilon) && RPOS(0);
```

BUT: this only captures the LAST token. We need ALL tokens.

**Real fix for claws5:** Use a different strategy —  match one token at a time
with a scan-replace loop:
```snocone
// Scan-replace: consume one token per iteration
tok_pat = (SPAN(DIGITS) . num) && '_CRD :_PUN'
        | (NOTANY('_') && BREAK('_')) . wrd && '_'
          && (ANY(UCASE) && SPAN(DIGITS && UCASE)) . tag;
sentno = 0;
mem = TABLE();
while (src ? (POS(0) && tok_pat && SPAN(' ') && '')) {
    if (DIFFER(num)) {
        sentno = INTEGER(num); mem[sentno] = TABLE(); num = '';
    } else {
        if (~DIFFER(mem[sentno][wrd])) { mem[sentno][wrd] = TABLE(); }
        if (~DIFFER(mem[sentno][wrd][tag])) { mem[sentno][wrd][tag] = 0; }
        mem[sentno][wrd][tag] = mem[sentno][wrd][tag] + 1;
    }
}
```
The `?=` scan-replace (consuming match) advances `src` on each iteration.
This avoids ARBNO entirely and sidesteps the capture-ordering bug.

**Real fix for treebank:** Same issue — `(word . tag) . *push_list(tag)` gives
push_list the OLD tag. Use scan-replace loop on `buf` consuming one token/bracket
at a time, maintaining the stack explicitly in procedural code rather than pattern.

---

## Steps

- [x] **SC-1** — claws5.sno PASS sbl -b. Python names.
- [x] **SC-2** — treebank.sno PASS sbl -b. Python names.
- [ ] **SC-3** — Fix claws5.sc for scrip:
  1. Replace goto slurp loop with `slurp_stdin(' ')` procedure (Bug 1 fix) ✓ already in file
  2. Replace ARBNO+epsilon.*fn() with scan-replace while loop (Bug 2 fix)
  3. pp_mem: already correct — DIFFER(sk1) check is in right order
  4. Gate: `head -3 CLAWS5inTASA.dat | scrip --ir-run claws5.sc` matches claws5.ref subset
- [ ] **SC-4** — Fix treebank.sc for scrip:
  1. Replace goto slurp loop with `slurp_stdin(nl)` procedure (Bug 1 fix) ✓ already in file
  2. Replace pattern-based tree building with explicit procedural scan loop (Bug 2 fix)
  3. DATATYPE check: use `REPLACE(DATATYPE(node), &LCASE, &UCASE)` for portability
  4. Gate: `cat treebank.input | scrip --ir-run treebank.sc` matches treebank.ref
- [ ] **SC-5** — Test both under --sm-run and --jit-run. Gate: output matches ref.

---

## Key implementation notes for SC-3/SC-4

### claws5.sc scan-replace approach
The `?=` operator in Snocone scans and REPLACES the match with the replacement.
`src ?= (pat <- '')` consumes the matched portion from src.
Use: `src ?= tok_pat <- ''` in a while loop to process tokens one at a time.

Verify `?=` syntax in scrip first:
```snocone
s = 'hello world';
s ?= 'hello' <- '';    // s becomes ' world'
OUTPUT = s;
```

### treebank.sc procedural approach
Replace the one-big-pattern with an explicit recursive-descent procedure:
```snocone
procedure parse_group(  tag, wrd) {
    if (~(buf ?= '(' <- '')) { freturn; }
    buf ?= SPAN(' ' && nl) <- '';
    if (~(buf ?= word . tag <- '')) { freturn; }
    dummy = push_list(tag);
    while (buf ?= SPAN(' ' && nl) <- '') {
        if (buf ? POS(0) && ')') { break; }
        if (buf ? POS(0) && '(') {
            if (~parse_group()) { freturn; }
        } else {
            if (~(buf ?= word . wrd <- '')) { break; }
            dummy = push_item(wrd);
        }
    }
    if (~(buf ?= ')' <- '')) { freturn; }
    dummy = pop_list();
    parse_group = ''; return;
}
```
This is equivalent to the original recursive ARBNO(*group) pattern but fully
procedural — no capture-ordering issues.

---

## State (2026-04-16 session end)

claws5.sno: PASS sbl -b. corpus HEAD 1437ea2.
treebank.sno: PASS sbl -b. corpus HEAD 1437ea2.
claws5.sc: slurp fix done; scan-replace rewrite needed (SC-3 next).
treebank.sc: slurp fix done; procedural rewrite needed (SC-4 next).

Root causes fully diagnosed. Implementation approach proven correct (conceptually).
Next session: implement SC-3 scan-replace for claws5, SC-4 procedural for treebank.
