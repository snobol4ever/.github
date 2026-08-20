# FINDING — s188 (seat4 `/home/claude4`, Claude Opus 5; queue row `gimpel-drivers-D`, rank 4)

## ⭐ HEADLINE — INCLUDING THE SAME FILE TWICE HANGS SCRIP, IN BOTH MODES, WITH NO OUTPUT AND NO DIAGNOSTIC

`-INCLUDE "X.sno"` twice in one compilation unit produces an image that **never terminates**: rc=124,
zero bytes on stdout, zero bytes on stderr, m3 and m4 alike. The oracle is **include-once** and answers
normally. One include of the same file is correct — the control is committed beside the witness, so the
ingredient is the second include and nothing else.

* Witness: `corpus/probe/gimpel/gim_double_include_hang.sno` (+ `_A.sno` the included module)
* Control: `corpus/probe/gimpel/gim_double_include_once_control.sno` — GREEN both modes
* Oracle for both: `3`

**Why this is not an exotic shape.** It is the ordinary "declare every module you use" habit, and the
gimpel library is built on it. `MINP.sno` includes `SPACING.sno` **and** `COUNT.sno`, while `SPACING.sno`
itself includes `COUNT.sno` — so MINP hangs. `LINE.sno` reaches `REVERSE` three ways, `COUNT` three ways
and `SPACING` twice. `FRSORT` doubles `COUNT` and `SEQ`. `HYPHENAT` doubles `BALREV`. Any corpus program
that names both a module and that module's own dependency is exposed.

⛔ **A measurement note that cost this seat a wrong answer first.** Piping the run through `head -1` closes
the pipe, the child takes SIGPIPE, and the hang reads back as **"silent, rc=0"**. Five probes were graded
that way before the pattern was caught. **A harness that truncates a program's output cannot distinguish
a hang from a silent success** — grade the exit status of an untruncated run.

---

## ⭐⭐ THE SECOND CLASS — A DEFERRED CAPTURE TARGET THAT IS NOT A SIMPLE VARIABLE IS SILENTLY INERT, AND THE `*` IS WHAT BYPASSES THE REFUSAL

`CRACK(S,B)` returns an array of **exactly the right size with every element null**. Its whole mechanism is
one line — `PAT = BREAK(B) . *CRACK<I> LEN(1)` — the ordinary "aim this capture at the I-th slot,
re-evaluated per match" idiom. The ablation is four programs and it is exact:

| capture target | SCRIP |
|---|---|
| `LEN(1) . V` — simple | **correct** |
| `LEN(1) . *V` — deferred simple | **correct** |
| `LEN(1) . A<I>` — array element | **LOUD REFUSAL**: `FATAL lower_snobol4 (GZ#5 subset): capture target in a runtime-built pattern is not a simple variable` |
| `LEN(1) . *A<I>` — deferred array element | **SILENT, rc=0, no diagnostic, both modes** |
| `LEN(1) . *$N` — deferred indirect | **SILENT, rc=0, no diagnostic, both modes** |

The feature is honestly declared unlanded on one spelling and goes quietly inert on the spelling one
character away. This is batch A's `EVAL`/`CONVERT` lesson again, on a different mechanism: **a feature
declared unlanded must fail on EVERY path that reaches it.** A fix aimed at "deferred capture targets"
aims at the wrong half — `. *V` is already right; it is the NON-SIMPLE target that needs the refusal to
follow it through the defer.

Witnesses: `gim_defer_cassign_array_elt`, `gim_defer_cassign_indirect`,
`gim_defer_cassign_simple_control` (green), `gim_cassign_array_elt_loud` (the loud sibling, no `.ref` —
SCRIP is expected to refuse it).

---

## ⭐ THE THIRD CLASS — THE DIRECT GOTO `:<expr>` (TRANSFER TO A CODE OBJECT) IS NOT SUPPORTED, AND FAILS TWO DIFFERENT DISHONEST WAYS

`LPROG.sno` is five lines and its entire body is `LPROG :<CODE(' LPROG = &STNO :(RETURN)')>`. `SEQ.sno`
does the same with `:<ARG_S>` where `ARG_S` holds a `CODE()` result. Measured:

* `:<G()>` — an expression operand — is a **PARSE ERROR**, no code generated.
* `:<L>` — a bare variable — is read as the **LITERAL LABEL NAME `L`**: `[SNO] transfer to undefined label: L`.
  Both oracles instead raise `ERROR 024 -- goto operand in direct goto is not code`, because the operand
  must be a code object. SCRIP is not refusing the construct; it is **misreading** it.

Neither path produces the honest *"EVAL and CODE are outside the landed subset"* refusal that `FLOOR`,
`LOG`, `L_TWO` and `INFINIP_lib` all get from `lower_snobol4`. Same "must fail on every path" class as
above. This is what takes out `FPROFILE` (via `LPROG`) and `CATA` (via `SEQ`), and it is the neighbourhood
of the already-red corpus test `216_indirect_goto_computed`.

---

## ⭐ THE 1:1 LAW — ONE STANDING BREACH (`LPERM`), ONE CURED MID-SESSION (`FORTPUT`), ONE LINK FAILURE (`GPM`)

**`FORTPUT` — WAS an m4-only SIGSEGV; ⭐ CURED MID-SESSION BY THE SPAN-FRAME FLIP, AND THE KILLSWITCH NAMES
IT IN ONE COMMAND.** `gim_fortput_m4_only_segv.sno` is an include plus one call.

* At SCRIP `cecb7d11` (this seat's first pristine build): **m3 rc=0 byte-correct 8/8 · m4 SIGSEGV 16/16**,
  ASLR on and ASLR off alike. The emitted `.s` was **BYTE-IDENTICAL across repeated compiles**, so the two
  modes were never handed different code — the same deterministic program was correct in the in-process
  image and fatal in the linked binary.
* At SCRIP `6d4cab2d` (re-measured after `git pull --rebase` brought in five commits): **m4 rc=0, 6/6.**
* ⭐ **Attribution, one command, no bisect:** `SCRIP_SPAN_FRAME=0` reproduces **rc=139 verbatim**;
  `SCRIP_ARBNO_ALTSIB=0` is **rc=0 correct**. So **SPAN-FRAME (s188 seat7, SCRIP `d3251f23`) is the cure.**

⭐ **This is an independent witness FOR that flip, from a seat that did not know it was landing.** The
program has no `ARBNO`, no alternation the eye is drawn to, and nothing to do with the row the flip was
landed for; it reaches the ALT-arm leaf through `(LEN(72) | REM) . T` inside a self-recursive `DEFINE`d
function. Seat7's flip note says the ALT-arm leaf's ζ cell stops being a raw flat rsp coordinate — this
witness says that mattered to a mode-4 program nobody wrote to exercise it. The witness is **kept, green,
as a regression guard** with the killswitch A/B in its header.

⛔ **AND THIS IS WHY THE RE-MEASUREMENT WAS NOT CEREMONY.** The first full batch-D board was taken at
`cecb7d11` and was internally consistent, plausible, and **wrong in one row**. It was caught only because
`git pull --rebase` moved SCRIP under the seat and the gate was re-proven rather than assumed —
s186 seat5's lesson (*a stale build is indistinguishable from a current one by inspection of its output*)
applies just as hard to a build that goes stale **during** the session as to one that was stale on arrival.

⛔ **One honest non-closure from when it was red.** An early burst of three runs of that same binary
returned **rc=124 (hang)** instead of 139. It did not reproduce in the 16 runs after, on a machine carrying
eight seats. Recorded as an unexplained transient; **not** claimed as nondeterminism, and not the
`ORBREAK` class batch B reported.

**`LPERM` — m3-only, and it is batch B's family on new code.** `m3 SIG11 / m4 PASS`. LPERM's one pattern is
`S LEN(1) $ T LEN(1) $ P *LGT(T,P)` — `$` immediate assignment plus **a deferred predicate call WITH
ARGUMENTS over the just-assigned variables**, which is precisely `gim_defer_pred_in_pattern_segv` from
batch B, and precisely beauty's `nInc() *Expr5 FENCE(…)`. Batch B saw that family split m3/m4 inside
`MDY.sno`; **LPERM is a second module, from a different chapter, splitting the same way** — so the split is
a property of the family, not of `MDY`. No new witness minted: batch B owns it.

**`GPM` — m3 SIG11 / m4 LINK FAILURE.** mode-4 emits references to symbols it never defines:

```
undefined reference to `PROC_α'      (three call sites: n4_call_α, n19_call_α, n34_call_α)
undefined reference to `FN__BAL'     (n236_define_α)
```

`PROC` is reached only through `. *PROC('NAME')` — a conditional assignment whose target is a **deferred
function call**, the same "non-simple target behind a `*`" shape as the CRACK class above. ⛔ **Not
minimized** — the obvious three-line shapes (`*F()`, `*F(ARG)`, called-normally-as-well) are all GREEN in
m4. Recorded unminimized rather than guessed at.

---

## THE BOARD — 25 MODULES, 25 DRIVERS, 5 GREEN

**WATERMARK (SCRIP `6d4cab2d`, `make pristine` before every verdict, RT_OPT `-O0`, corpus `9ba9ed5a`) — every figure below RE-MEASURED at that revision after a mid-session rebase moved SCRIP five commits:**
corpus board **m3 332/5 · m4 325/11 · SKIP 1 (337)** — **the row's quoted baseline to the digit, fail-set
identical by name.** A no-op by construction: the board enumerates `crosscheck` + `beauty_suite` + demos
and never reaches `programs/gimpel` or `probe/`, which is what makes an unchanged board the correct
result and the proof of no regression.

| module | m3 | m4 | cause |
|---|---|---|---|
| CH | PASS | PASS | |
| COUNT | PASS | PASS | |
| DECOMB | PASS | PASS | |
| FORTREAD | PASS | PASS | |
| HEX | PASS | PASS | |
| FORTPUT | PASS | PASS | ⭐ was m4 SIGSEGV at `cecb7d11`; **cured by SPAN-FRAME** (`d3251f23`), killswitch-attributed (above) |
| **LPERM** | **SIG11** | **PASS** | ⭐ 1:1 breach, m3 direction (above) |
| **CRACK** | DIFF | DIFF | ⭐ deferred non-simple capture target, silent |
| **INSULATE** | DIFF | DIFF | ⭐ silent wrong answer: `TRACE(NAME,'CALL',,'INS_CALL')` never fires, so `&ANCHOR` is **not** zeroed inside an insulated function — SCRIP prints `anchor-inside=1 no-match-B` where both oracles print `anchor-inside=0 matched-B` |
| **MINP** | TIMEOUT | TIMEOUT | ⭐ double include (above) |
| **FPROFILE** | COMPILE_FAIL | COMPILE_FAIL | ⭐ `:<CODE(…)>` in `LPROG.sno` — parse error |
| **CATA** | SIG11 | SIG11 | ⭐ `:<ARG_S>` in `SEQ.sno` — same class, crashing rather than refusing |
| **GPM** | SIG11 | ASM_FAIL | ⭐ m4 undefined references (above) |
| CARDPAK | COMPILE_FAIL | COMPILE_FAIL | trailing-dot real literal — `RANDOM.sno:6` is `REMDR(RAN_VAR * 4676., 414971.)`. Batch A's class (`gim_real_literal_parse`); recorded because it takes out a whole module chain (CARDPAK→RPERMUTE→RANDOM) |
| HYPHENAT | SIG6 | COMPILE_FAIL | deferred argument to a pattern primitive (`TAB(*K)`) has no template — batch A's `gim_tab_defer_no_template` |
| LINE | SIG6 | COMPILE_FAIL | same, via HYPHENAT |
| HSORT | SIG11 | SIG11 | `~` negation — batch A's `gim_not_op_no_template`. ⛔ Note it SIGSEGVs here rather than raising batch A's FATAL |
| FLOOR | RC1 | COMPILE_FAIL | `DEXP` builds a prototype at runtime — **honest, loud refusal**, both modes |
| LOG | RC1 | COMPILE_FAIL | same, via `DEXP` |
| L_TWO | RC1 | COMPILE_FAIL | same, via `POL.sno` |
| INFINIP_lib | RC1 | COMPILE_FAIL | same, via `REDEFINE.sno` |
| IMAGE | SIG11 | SIG11 | ⛔ **unclassified** — owed a witness |
| INORM | TIMEOUT | TIMEOUT | ⛔ **unclassified hang** — *not* a double include (its four includes are disjoint); owed a witness |
| L_ONE | TIMEOUT | TIMEOUT | ⛔ **unclassified hang** — *not* a double include (PUSH + TEMP are disjoint); owed a witness |
| FRSORT | COMPILE_FAIL | COMPILE_FAIL | include cannot be resolved — `lon-include-root`, not a SCRIP defect (below) |

**6 GREEN both modes · 1 green in exactly one mode (`LPERM`) · 18 RED both modes**, all checked in red per law 0d.

---

## ⛔ FOR HQ — THREE THINGS THE ROW'S BRIEF DID NOT ANTICIPATE

**1. BATCH D SHIPS NO MODULE WITHOUT A `.ref`, AND FIVE OF THEM ONLY BECAUSE CSNOBOL4 EXISTS.** SPITBOL
refuses five of the 25 outright, under `-b` **and** `-bf`:

| module | SPITBOL |
|---|---|
| GPM | `BAL.sno(11) : ERROR 042` — `BAL` collides with the protected built-in pattern |
| FPROFILE | `FPROFILE.sno(5) : ERROR 199` — no `KEYWORD` trace type |
| INSULATE | `INSULATE.sno(7) : ERROR 248` — `OPSYN('DEFINE','INSULATE')` over protected `DEFINE` |
| INFINIP_lib | `REDEFINE.sno(17) : ERROR 156` — opsyn first arg is not an operator name |
| L_TWO | `TUPLE.sno(31) : ERROR 248` — `DEFINE('LOAD(LOC)')` over the built-in `LOAD` |

**CSNOBOL4 runs all five**, so each gets a real live-oracle `.ref` by the `ASM_driver`/`TUPLE_driver`
routing, and every driver carries an ORACLE NOTE saying which engine produced its ref and why. Batch A
shipped three modules with no ref at all on exactly these grounds (BAL, FTRACE, INFINIP) — **two of those
three are the same two collisions (BAL, and the protected-`DEFINE` OPSYN), so they are recoverable the same
way.** Worth a row.

**2. `FRSORT` IS NOT AN INCLUDE-ROOT PROBLEM, IT IS A FILENAME PROBLEM.** `FRSORT.sno:9` asks for
`-INCLUDE "stringout.sno"`; the file present in that same directory, on the search path, is
**`STRINGOU.sno`** — an eight-character truncation of the name. Both engines fail:
`ERROR 285 -- include file cannot be opened` (sbl) and `cannot open include 'stringout.sno'` (SCRIP —
which names the file, and is the better message). The `lon-include-root` row as written adds include
ROOTS and will not fix this; it needs a name alias or a truncation-tolerant resolver. Censused: FRSORT is
the only batch-D module with this shape.

**3. `FPROFILE`'S REF PINS LESS THAN IT LOOKS.** CSNOBOL4 accepts the `TRACE(.STCOUNT,'KEYWORD',…)` call
but never fires it, so `FP_ARY` comes back entirely null and the pinned profile is empty
(`total statements counted = 0`). What the ref genuinely tests is `LPROG()`, whose value sizes the array.
Neither sanctioned oracle actually performs a `&STCOUNT` keyword trace, and hand-authoring a stronger ref
is forbidden. Said in the driver's own header so no later seat reads the empty profile as a SCRIP defect.

---

## ⛔ A RETRACTION, KEPT VISIBLE

This seat spent a round convinced that **an apostrophe inside a `*` comment line broke SCRIP's parser**,
and had begun sizing the blast radius (544 corpus `.sno` files carry the shape) before checking the probe
itself. The probe harness used `printf '%s\n'` on a `$"…"` string, so `\n` stayed a literal backslash-n:
every "failing" case was actually **one comment line and no program at all**, and the FATAL was the
empty-program message. There is no comment-apostrophe defect. Two lessons, both already paid for:
a probe that has not been shown to do the thing it claims to do is not evidence — the same failure took
out this seat's first `-INCLUDE` bisect, where a leading tab made `-INCLUDE` inert and six modules read
back "(clean)" while including nothing at all.

## Provenance
* corpus `1a8d6a9e` — 25 drivers + 25 refs in `programs/gimpel/`, 6 witnesses + 5 refs in `probe/gimpel/`
* SCRIP `6d4cab2d`, `make pristine` (twice: once at `cecb7d11`, again after the rebase), RT_OPT `-O0`.
  **No compiler file touched** — the `.s` regens are a provable no-op and were not run.
* Every ref generated from a live oracle: `x64/bin/sbl -b` for 20, `snobol4 -b` (CSNOBOL4) for 5. None
  hand-authored, none md5-pinned.
