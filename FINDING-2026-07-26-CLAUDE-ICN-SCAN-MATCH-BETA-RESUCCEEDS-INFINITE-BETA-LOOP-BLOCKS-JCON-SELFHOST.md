# FINDING (2026-07-26) — `=s` β RE-SUCCEEDS INSTEAD OF FAILING: INFINITE β LOOP, SEGV, AND IT IS THE JCON SELF-HOST BLOCKER

**SCRIP `20aa255f` (no code changed this session) · RT_OPT=-O0 · oracle iconx 9.5.25a · modes 3 AND 4 identical**

## ⭐ THE SIX-LINE REPRO — SEGV, BOTH MODES

```icon
procedure main();
   local s;
   s := ".abc";
   s ? { if ="." & ="9" then write("Y") else write("N") };
   write("done");
end
```

| | result |
|---|---|
| iconx 9.5.25a | `N` `done` |
| SCRIP m3 (`--run`) | **SEGV rc=139** |
| SCRIP m4 (`--compile`+link) | **SEGV rc=139** (mode-identical) |

## THE DISCRIMINATING TABLE (each measured)

| construct | iconx | SCRIP | note |
|---|---|---|---|
| `if ="." then A else B` | `Y` | `Y` ✅ | single matcher, no conjunction |
| `if ="x" & ="9" then A else B` | `N` | `N` ✅ | **first conjunct FAILS** — never backtracks into it |
| `if ="." & ="9" then A else B` | `N` | **SEGV** | **first conjunct SUCCEEDS, second FAILS** |
| `write(if ="." & ="9" then "Y" else "N")` | `N` | **SEGV** | not `if`-statement-specific |
| `if (="." & ="9") then A else B` | `N` | **SEGV** | not parenthesization |

**TRIGGER, EXACTLY:** a cursor-moving matcher that **SUCCEEDS**, followed by a conjunct that **FAILS**, forcing
backtracking INTO the first matcher's β. If the first conjunct fails outright, there is no β re-entry and the
code is correct — which is why so much scan code works.

## ROOT CAUSE

`=s` is sugar for `tab(match(s))` (ARCH-ICON.md, ICN-SCAN family). Per canonical
`refs/icon-master/src/runtime/fstranl.r` + `fscan.r`, `match` is `function{0,1}` — **one result, then fail** —
and `tab` is a CURSOR-MOVER whose documented contract (ARCH-ICON.md, verbatim) is:

> **Cursor-movers, REVERSED on resume:** `tab`/`move` write δ and restore the saved δ on β then fail.

SCRIP's β does **not** restore-δ-and-fail. It re-enters as though from α, re-runs the match at the restored
position, and **succeeds again**. The second conjunct fails again, backtracks again, forever.

**MEASURED PROOF (gdb):** ~3,041,700 stack frames, one address repeating. Crash site:

```
rt_substr (sigma=0x42b770 ".abc", a=1, b=1) at src/runtime/builtins/gen_runtime.c:175
```

`a=1, b=1` — the SAME position every time. It is not a wild pointer; it is **stack exhaustion from an
infinite β loop**. Under `ZC_FRAME_RSP` (the s65 default) control-flow-lifetime ζ rides the machine stack, so
each spin pushes cells until the guard page is hit.

⚠ The SEGV is a SYMPTOM. A `{0,1}` generator that yields unboundedly is the defect; the crash is just where
the stack ran out.

## WHY THIS IS THE JCON SELF-HOST BLOCKER

`SCRIP-jtran preproc irgen.icn : yylex : parse : ast2ir : bc_File` dies with:

```
File irgen.icn: Line 29 # invalid character: "c"
```

Oracle-jtran translates the same file to **114 class files**. Bisected to `lexer.icn:135`, the
".123-as-a-real" special case:

```icon
if str <- ="." & str ||:= tab(many(&digits)) then { ... };
...
if op := do_ops() then { ... }          # line 148 — never reached
lex_error("invalid character: " || image(&subject[&pos]))   # line 170 — reached instead
```

On `p.coord`: `="."` succeeds, `tab(many(&digits))` fails on `c`. Canonical Icon backtracks, **restoring
`&pos` to the dot**, so `do_ops()` then returns `lex_DOT`. SCRIP leaves `&pos` PAST the dot, so `do_ops()`
is offered `c`, matches no operator, falls through string-lit and cset-lit, and reports
`invalid character: "c"` — the char AFTER the dot, which is the tell.

**Minimal SCRIP-level repro of the same shape (no jtran):**

```icon
s := ".abc";
s ? { if str <- ="." & str ||:= tab(many(&digits)) then write("REAL") else write("pos=", &pos) };
```
iconx → `pos=1` (restored). SCRIP → `pos=2` (**not restored**).

⚠ NOTE THE TWO FACES OF ONE FAMILY: with reversible assignment `<-` present, SCRIP does NOT crash but
silently skips the δ restore (`pos=2`); without it, SCRIP spins and SEGVs. Fix must close BOTH.

**LIKELY THE SAME DEFECT AS `GOAL-ICON-BB.md`'s OPEN FZ-E SCAN CLUSTER** (`scan1`/`scan2`/`recogn`,
"emitter wires the SCAN_MATCH fail-edge to arm-B beta not alpha"). This repro is 6 lines, needs no procedure,
no subject variable, no generator, and CRASHES HARD — strictly better to debug than any FZ-E program. Verify
the connection before claiming it; do not assume.

## ⛔ TWO STALE DIAGNOSES CORRECTED

**(a) `GOAL-JCON-IN-SCRIP.md` LIVE CURSOR: "the ONLY remaining bc_File divergence for `hw.icn` is JVM
constant-pool ordering ... char 647, sc=973 vs or=983 bytes." MEASURED FALSE at `20aa255f`.**
Both files are now **995 bytes**; `cmp` first-differs at **byte 826**, 57 bytes differ, all inside 826–950.
The constant pool lies entirely BEFORE 826 and is therefore **byte-identical**. The real divergence is
`0x3a` = `astore`: oracle writes slots **19,17,18**, SCRIP **18,19,17** — a permutation, emitted by
`gen_bc.icn:1495 bc_initialize_tmps`, which walks `key(bc_tmp_table)`.

**(b) TABLE KEY-ORDER IS A REAL DIVERGENCE — AND MY FIRST CALL ON IT WAS WRONG.**
15-line repro (8 one-char keys, `every k := key(t)`):
`iconx → @-*$!+%/` · `SCRIP → %$!-/+*@`. Both deterministic.
Canonical contract: `rmisc.r:175` hash = `Σ(char × 37^k)` over first ≤10 chars `+ length`;
`rstruct.r:263 hgnext` walks slots in index order, chains sorted ascending by `hashnum`.
Consequence: `oplexgen.icn`'s `dotree` (line 254) emits the lexer trie in `key()` order, so SCRIP's
regenerated `do_ops.icn` differs from the oracle's (611 lines both, 401 differing).
⚠ **I initially judged this "semantically inert" because JCON-on-JVM would permute it too. That reasoning is
UNSAFE and I retract it:** `optimize_tree` MERGES chains (`t.t[i||j] := s.t[j]`), so sibling keys CAN be
prefixes of one another, and `dotree` emits sequential `if =KEY` tests — first match wins. Order is therefore
**semantically load-bearing** wherever a merged key is a prefix of a sibling. It is NOT the cause of the
line-29 failure above (the `.` arms are byte-identical in content, only repositioned), but it is a live
latent hazard and must not be dismissed. `interface.icn` regenerates **byte-identical** (415 lines).

## ORACLE OPERATING NOTE (cost me a false blocker)

Oracle-jtran SIGSEGVs (`Run-time error 302`, `init.r:510`) on `irgen.icn` unless invoked with **`jcont`'s own
environment** — the critical one is **`COEXPSIZE`**, because `jtran_main.icn:55` runs each pipeline stage in a
co-expression. `jcont` (bin/jcont L92-98) exports `BLKSIZE=6000000 STRSIZE=1000000 COEXPSIZE=1000000` and
**unsets** `MSTKSIZE QLSIZE HEAPSIZE BLOCKSIZE ICONCORE TRACE IPATH NOERRBUF`. Setting `MSTKSIZE` (my first
attempt) does NOT help and is explicitly cleared by jcont. With the correct env, oracle irgen.icn → 114 classes.

## SESSION STATE (all rebuilt from scratch this session, single-CPU container)

| artifact | state |
|---|---|
| `icont`/`iconx` 9.5.25a | built, `/home/claude/icon-oracle-src/bin/` |
| oracle `jtran`+`jlink` | built, `/home/claude/jcon-oracle-src/tran/` |
| `scrip` + `libscrip_rt.so` (-O0) | built |
| **SCRIP-jtran, 17 modules** | **compiled 0 bombs, 516,712 asm lines, linked 5,123,216 B** |
| `hw.icn` end-to-end | ✅ `l$hw_semi.class` + `links` byte-identical; `p_l$..$main.class` 57/995 bytes permuted |
| `irgen.icn` (self-host gate) | ❌ blocked by the `=s` β defect above |

Java was NOT installed and the JVM was NOT run (s121 ABSOLUTE). `jcon_selfhost_build.sh` step [7/7]
(javac/jar) was SKIPPED for that reason; verification is byte-comparison of `.class` files as DATA.
⚠ `jcon_selfhost_run.sh` is Java-dependent from its ZipMerge step onward — only its FIRST command
(the `jtran ... bc_File` translate) is sanctioned.

## FIX / RE-TEST GATE

1. 6-line repro → `N` `done`, no SEGV, both modes.
2. `<-` variant → `pos=1` (δ restored).
3. `SCRIP-jtran preproc /tmp/t1.icn : ... : bc_File` (the 5-line `p.coord` file) → 3 classes, not a lex error.
4. `SCRIP-jtran ... irgen.icn` → **114 class files**, matching oracle's file set.
5. `bash scripts/test_icon_all_rungs.sh` → must not regress **249/12/32**.
6. Re-check FZ-E (`scan1`/`scan2`/`recogn`) — plausibly the same root; the count may drop by more than one.
