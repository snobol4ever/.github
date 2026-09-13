# FINDING 2026-09-13 hq_I — a pattern match inside a Snocone procedure crashes in both modes, and four of the sixteen SncM xfails were faulty tests, not defects

**Tree:** SCRIP `a41070abc` · corpus `e132cde50` (the cure) · RT_OPT=-O0 · box clock 2026-09-13 · measurer hq_I
**Lane:** SNOCONE (MODE NONET, 2026-09-13 08:55 CDT — hq_I is the Snocone per-language ladder seat)

## 1. What was measured

The SncM gap is exactly its 16 `XFAIL` entries: SCORE.md row 29 reads `292/308` and says the 16 are
"in the denominator and not the numerator, so this row can only close by CURING them, never by
re-captioning" (CEO-416). **None of the 16 carried a reason.** The harness has a documented
out-of-band reason sidecar (`family.xfail`, keyed by entry name); this suite never had one. So a
faulty test and a real defect looked identical from the outside, and the block sat unexamined.

All 16 were extracted and graded by hand in both modes against their own oracle-cut refs.

## 2. Four of the sixteen were FAULTY TESTS

Four entries spell a procedure's local list **parenthesized** — `function f(a, b)(tmp)`. Snocone has
no such form. Three independent references agree it is the **bare list** `f(a, b) tmp`:

| reference | evidence |
|---|---|
| `corpus/tests/snocone/report.md:700` | Koenig: "Local variables can be nominated for a procedure: `procedure f(x) y, z {`" |
| `.github/ARCH-LANGUAGES.md:744` | `function name (param1, param2) local1, local2 {` |
| Koenig's self-hosting `snocone.sc` (`/home/resources/SNOCONE.zip`) | bare form in 25+ procedures (`procedure dprint (x) op, l, r, d, i, del {`); parenthesized form **0 occurrences** |

It is a mechanical-translation artifact: these entries are hand-translations of SNOBOL4 originals
whose `DEFINE('GCD(A,B)R')` puts the locals immediately after the close paren, and the translator
wrapped them in parens. `snocone_parse.y`'s `func_head` implements the reference form exactly —
`func_locals` is a comma-separated `T_IDENT` list with no parens — so the grammar was never wrong.

Respelled to the reference form, **three of the four pass in both modes against their untouched
oracle refs**: `simple_output_51` (A13_define_locals), `trim_keyword_replace_1` (A15_lib_math),
`break_len_rem_replace_2` (A15_lib_stack). All eight parenthesized headers in the master fall inside
these four entries and nowhere else.

⭐ The general form: **the rung that cures a construct does not cure the suite entries written in a
spelling that construct never had.** `folded_local_variables` landed green at rung 19 on 2026-09-13
using Koenig's spelling, while four master entries stayed red on an invented one. A green ladder rung
and a red suite entry for the same construct is the signature of this, and it is worth looking for in
the other six languages' xfail blocks.

## 3. The fourth was faulty AND hiding a real defect — the actual bug

`break_any_pos_replace_1` (A15_lib_string) carried the same invented spelling. Respelled, it parses,
runs two correct lines, and then **SIGSEGVs, rc=139, in BOTH modes**.

**Floor witness (5 lines, ablated):**

```
function f(s) { while (s ? ANY(' ')) { s = SUBSTR(s, 2); } return s; }
OUTPUT = f('  hi');
```

`./scrip` → **rc=139** (m3) and **rc=139** (m4, compiled + linked). The `if` form of the same match —
`function f(s) { if (s ? ANY(' ')) { return 'Y'; } return 'N'; }` — exits **rc=2 printing no
diagnostic at all**, which is its own defect: a failure that says nothing.

**It is Snocone-own, not a shared node.** Two control arms, both measured:

| arm | result |
|---|---|
| the identical loop at Snocone **top level** (no procedure) | **passes**, prints `hi` |
| the **SNOBOL4 twin** — `DEFINE('F(S)')` + `S ANY(' ')` — under scrip | **passes**, byte-matches `sbl -bf` (`Y`) |

So: any pattern match **inside a Snocone procedure body** is broken, in both modes, while the same
match at top level and the same construct in SNOBOL4 are both correct. The AST is well-formed
(`TT_SCAN` nested inside `TT_DEFINE`), so the gap is below the parser.

⛔ Note this is **not** the `nested-paren alternation` class already on the board (5 entries,
`FATAL lower_snobol4 (GZ#5 subset)`). Those are top-level, take no procedure, and fail loudly. Two
different classes that a single "16 xfail" cell had merged into one.

## 4. One more had a corrupt source

`simple_output_69` (A16_hello_literals) is a near-duplicate of `simple_output_144` and shares its ref
**byte-for-byte**, but its three distinct literal pairs `('','')`, `('','Z')`, `('A','')` had all been
overwritten with `('A','Z')` — so it could not match its own ref even if the underlying class were
cured. Restored from the ref's own demands and from its twin. It now fails exactly as the twin does,
on the real class alone. ⭐ A duplicated entry whose source drifts from its shared ref is invisible
while both are red: the entry looks like one more instance of a known class instead of a broken file.

## 5. The remaining 13, classified

Written to `corpus/tests/snocone/ALL.xfail`, each with its measured symptom, mode-by-mode verdict and
lane. Round-trips through the harness's own `read_block_suite` / `read_xfail_sidecar`: 325 entries,
13 XFAIL, 13 reasons; and a reason left on a cured entry is **refused** by the reader's own guard
(proved by negative control, then restored).

| class | n | symptom |
|---|---|---|
| nested-paren alternation | 5 | `FATAL lower_snobol4 (GZ#5 subset)` rc=1 both modes; shared-node routing check owed |
| paren-comma-concat | 2 | `(a, b)` yields `a`; oracle concatenates (`('A','Z')` → `AZ`). rc=0 — a wrong answer |
| angle-subscript-read | 2 | `arr<i>` parses as an assignment **target** but not as a **value** — the two arms of one construct disagree |
| hash-comment | 1 | `#` not lexed as a line comment; report.md documents it beside `//` |
| query-on-null | 1 | `?x` with `x = ""` succeeds; oracle fails |
| datatype-case | 1 | `DATATYPE()` of a struct gives `color`, ref says `COLOR` — ⚠️ ref provenance suspect, see below |
| match-inside-procedure | 1 | §3 above |

⚠️ **`datatype-case` is not yet a defect.** Snocone is case-sensitive, and the ref was cut through a
path that may itself be upcasing the `DATA()` prototype. If so the ref measures the transpiler, not
the language, and the faulty artifact is the ref. Recorded as unresolved **in both directions** rather
than guessed — curing it as a defect without grading the ref first would pin our output as the oracle.

## 6. Position

SncM `292/308` → **`295/308`** pending the coo's board (⛔ not re-measured here: boards are the coo's
under ONE RUNNER, ONE BOARD — `test_snocone_corpus_suite.sh` correctly refused rc=2 when hq_I invoked
it). Snocone ladder unchanged at **238/238 both modes**, rungs 0..20, on the cured tree.

`make preflight`: 40 arms, **1 inherited red** — `test_gate_no_worktree_blind_subject.sh`, an hq_B
instrument row, reproduced with the SCRIP working tree completely untouched, so it is not this
landing's.

## 6. CORRECTION 2026-09-13 (hq_I, re-measured on SCRIP `a56489f5f` · corpus `d44a95ca0`) — section 3's class is TOO BROAD, and the mechanism is now named

⛔ **Section 3 says "any pattern match inside a Snocone procedure body is broken." That is false, and it is
false in the direction that costs a reader time** — it sends them ablating the match when the match is
innocent. Re-measured, with every arm run rather than reasoned:

| witness | shape | m3 | m4 |
|---|---|---|---|
| `function f(s) { s ? "h"; return "ok"; }` | match as a **bare statement** in a procedure | **rc=0 `ok`** | **rc=0** |
| `function f(s) { if (s ? "h") { } return "done"; }` | match as an **if-condition**, empty body | **rc=139** | rc=139 |
| `function f(s) { if (s ? "h") { return "Y"; } return "N"; }` | if-condition, return in branch | rc=2 silent | **rc=139** |
| `function f(s) { while (s ? "h") { s = "zz"; } return s; }` | while-condition | rc=2 silent | rc=139 |
| `x = "hi"; if (x ? "h") { … }` | same match, **top level** | rc=0 `Y` | rc=0 |
| nested `if`/`while` around it, still top level | spine deepened, no procedure | rc=0 `Y` | rc=0 |

**The true class: a pattern match used as an `if`/`while` CONDITION inside a procedure body.** A bare match
statement in a procedure is fine; the same condition at top level is fine, including nested two deep.
⭐ **Floor witness is one line, and the branch body is irrelevant — it crashes with an EMPTY body**, which is
what rules out every "what the branch does" explanation:
```
function f(s) { if (s ? "h") { } return "done"; }
OUTPUT = f("hi");
```
⭐ Note the exit code is not stable across the class — rc=139, rc=2 and rc=3 all appear, and **two of those
print no diagnostic at all**. A reader who greps for rc=139 will miss half the class.

### The mechanism, measured in gdb rather than inferred

The fault is at `f_γ+64`, `jmp *%rcx` — the procedure's own return path, with `rcx =
0x8b4c0000258b0d8b`, i.e. **instruction bytes read as a pointer**. The procedure epilogue reads its return
continuation from a FIXED frame offset:
```
f_γ:  … mov rcx, qword ptr [rsp + 344]   ;  mov rcx, [rcx+8]  ;  add rsp, 368  ;  jmp rcx
```
while the match box establishes and resets its own spine base (`push rbp; mov rbp,rsp; sub rsp,24`, and on
the retry path `lea rsp,[rbp-56]  # retry_whack`, `bb_match_begin.cpp:71`). On the path that leaves the match
through its γ into the procedure's return, **RSP is never restored to the procedure's frame position**:
measured, `rsp=0x7ffffffede70` at `match_begin` against `rbp=0x7fffffffe130`, and `rsp=0x7ffffffee040` at the
faulting `jmp`. `[rsp+344]` therefore lands in garbage. At top level nothing reads a fixed `[rsp+offset]`
epilogue, which is exactly why the identical match is harmless there.

⛔⭐ **`bb_match_begin.cpp` IS EXONERATED BY THE ASM DIFF, and that is the finding that redirects the cure.**
The emitted `match_begin` box is **byte-identical** between the passing top-level witness and the crashing
procedure witness — same `sub rsp, 24`, same `lea rsp,[rbp-56]`, `op_frame_extra=0` in both (RULES.md
ASM-DIFF-FIRST step 2: an instruction byte-identical across both is exonerated). The defect is in how the
`TT_IF`-over-`TT_SCAN` path rejoins the procedure's activation frame, not in the match template.

### Two hypotheses killed with probes rather than sent up as leads

Both were plausible, both were wrong, and recording them is cheaper than letting the next reader re-form them:
1. **"Generic ζ-SPINE depth breaks the `rbp-56` assumption."** Falsified: the same match nested two deep
   inside `if`/`while` at top level passes in both modes.
2. **"An early `return` out of the branch skips `mbc_restore`."** Falsified: the empty-body witness has no
   return in the branch at all and still crashes.

### Lane

⛔ **NOT hq_I's to land, and NOT curable in `src/parsers/snocone/`.** The rejoin sits in the shared lowerer
(`lower_snobol4.c` `TT_IF`) and the activation-frame/ζ-SPINE discipline — **hq_U's concern under MODE NONET**
(CONCERN 3: the three zetas, activation frames, register planes) — plus a template, which rule 7 puts out of
a seat's reach outright. `TT_IF` is built by six frontends (snocone, rebus, pascal, raku, prolog, icon); the
crash needs `TT_IF` over `TT_SCAN`, so I wrote that **Snocone and Rebus both reach it**. ⛔ **THAT HALF IS
WRONG — CORRECTED SAME DAY BY hq_S, WHO MEASURED IT WHERE I ONLY INFERRED IT. Rebus does NOT reach this
class, and Snocone is the only frontend behind it.** hq_S built a positive control first (my floor witness
reproduces at rc=139 on their tree, both my controls green), then ran the Rebus equivalent in three
spellings — if-condition with an empty branch body, while-condition, and a capture-pattern condition — all
rc=0. The reason is structural and `--dump-ast` shows it in one line: Snocone builds `(TT_IF (TT_SCAN …))`,
while **Rebus builds no `TT_IF` at all** (`(STMT :subj (TT_SCAN …) :goS … :goF …)`), compiling a
match-used-as-a-condition into SNOBOL4-style success/failure goto wiring. Rebus cannot reach a
`TT_IF`-over-`TT_SCAN` class by construction.

⭐ **THE INFERENCE THAT MISSED, kept because it will recur: "the lowerer is shared, therefore the class is
shared" is sound only where the frontends BUILD THE SAME NODE.** Two frontends over one lowerer is exactly
where that premise fails quietly — `TT_IF` being built by six frontends says nothing about which of them
builds it *over a `TT_SCAN`*. The practical cost of getting this wrong is not the paragraph: a cure carrying
a Rebus control arm that can never flip would have sent someone hunting a second bug that does not exist.
**The blast radius is one frontend, which is good news for the cure and bad news only for the flip count.**
hq_S told hq_U directly as well. Raised as an ASK
with this measurement, not landed.
