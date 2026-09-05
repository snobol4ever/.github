# The "mode-4 compile failure" class does not exist: all 41 programs refuse identically in BOTH modes

**Seat:** hq_B · **Date:** 2026-09-05 · **Lane:** #4 under QUARTET
**Populations measured:** `snobol4-gimpel-class-rc1-compilefail` (20 named drivers) and snoflake's `SKIP(cc)` (21)
**Tree:** SCRIP `b1fb42fb1` + this session's two cures · oracle `/home/resources/x64/bin/sbl -bf` (18:19 build)

## The claim under test

`GOAL-SNOBOL4-100.md` § THE ORDER OF ATTACK, wave 3:

> **3 — mode-4 compile failures** (DECOUPLED from wave 1 on hq_C's reading: independent of the capture
> mechanism) | *programs that run in m3 and do not build in m4* | gimpel 27, snoflake 23 in m4

And the row's own GOAL, which is where the reading comes from:

> the board's per-mode counts are equal (m3_pass == m4_pass == 59), so a per-mode number says the modes agree,
> while the SIGNATURES say mode 4 cannot even emit these. Start with the m4 COMPILE_FAIL half […] and only then
> ask whether the m3 rc=1 has the same cause or is a second, independent defect in the same program.

The row asked the right question and left it open. **It is answered: it is the same cause, in every single case.**

## The measurement

Each program run twice — `./scrip <f>` and `./scrip --compile -o /tmp/x.s <f>` — and the first stderr line compared.

### gimpel, the 20 named drivers

| cause | n | members |
|---|---|---|
| `DEFINE with a non-literal prototype string` — **runtime DEFINE, the ceo's #1** | **11** | ARC DEXP DEXTERN FLOOR INFINIP_lib LOG L_TWO POL REDEFINE STACK TRIG |
| `ERROR 248 -- attempted redefinition of system function` | 3 | SQRT (SQRT) TUPLE (LOAD) VISIT (DATA) |
| `name operator over this form is outside the landed subset` | 2 | FLD LSORT |
| `SN4-REPL slice 1: replacement subject must be a plain variable` | 2 | PEEL PERMS |
| **compiles in m4 now, CRASHES in m3** | 2 | GPM (m3 rc=134) TR (m3 rc=139) |

**For all 18 that refuse, m3 rc=1 and m4 rc=1 with a byte-identical message.** The lowerer refuses before
either backend is reached; m3 reports it as an exit status and m4 as "no .s produced". One defect, two
reporting conventions. The 11 exactly matches the ceo's own count of the runtime-DEFINE members.

⭐ Note the last row runs the *other* way: GPM and TR now build in m4 and fail in m3. A class named
"runs in m3, will not build in m4" has two members doing precisely the opposite.

### snoflake, all 21 `SKIP(cc)`

| cause | n |
|---|---|
| `DEFINE with a non-literal prototype string` (runtime DEFINE) | 9 |
| parse error / `missing END` / `unexpected char` | 6 |
| `name operator over this form` | 2 |
| `assignment subject form not in the landed subset` | 2 |
| `pattern shape outside the SN4-PAT subset` | 2 |
| **gcc assembler failure** | **0** |
| **linker failure** | **0** |

Every one is a parser or lowerer refusal, identical in m3. Spot-checked four in both modes
(`indirect-integer-and-keyword`, `string-pad`, `stack-opsyn`, `eliza-modernized`): m3 rc=1 with the same
message m4 gives. **`SKIP(cc)` is a bucket in the snoflake runner's reporting, not a property of mode 4** —
`compile_m4()` calls anything that is not a `SCRIP: ERROR N` line a toolchain failure, and a lowerer FATAL
is not that shape. The m3 arm lumps the same programs into its FAIL count instead.

## What follows

⛔ **Wave 3 should be struck as a class.** There is no population of programs that run in m3 and fail to build
in m4. Its 41 members are: **20 runtime DEFINE** (the ceo's #1 row, wave 1 — not a decoupled wave-3 item at
all), **3 ERROR-248/ERRLIMIT** (blocked on the same #1), **4 named lowerer subset gaps**, **6 parse-stage
cases**, **2 pattern-subset cases**, and **2 m3 crashes**. The decoupling premise — "independent of the capture
mechanism" — is also wrong for PEEL/PERMS and the eliza pair, which land in exactly the SN4-REPL / SN4-PAT
neighbourhood wave 1 owns.

⭐ **This is why the row was unclosable by anyone.** Its DONE-WHEN requires all 20 gimpel drivers green.
Fourteen of the twenty are gated on rows belonging to other seats — 11 on the ceo's runtime DEFINE, 3 on
ERRLIMIT survival of a runtime 248. The holder could do everything right and never close it.

## Of the 6 parse-stage cases, only ONE was a SCRIP defect

Checked against the oracle rather than assumed:

| program | oracle | verdict |
|---|---|---|
| `eliza-duquet-original` | rc=0, prints `ENTER SCRIPT` | ⛔ **real SCRIP defect — CURED this session** |
| `gimpel-poker-game` | rc=1, refuses | agreement, not a defect |
| `gimpel-state-functions` | rc=1, refuses | agreement, not a defect |
| `multiline-backtick-load` | rc=231, refuses | agreement, not a defect |
| `lexical-comparison`, `string-pad` | `No END statement found` | lowercase `end` — the dialect class, out of scope on Lon's keyword ruling |

The one real defect: **text after the `END` statement was being parsed as source.** Cured — see
`FINDING-2026-09-05-hq_B-text-after-the-end-statement-was-parsed-as-source-so-a-clean-program-produced-nothing.md`.
`eliza-duquet-original` now parses and reaches its true blocker (SN4-REPL). Its `SKIP(cc)` bucket is unchanged,
because the bucket never meant what its name says — which is the finding, restated at the level of one program.

## ⭐ The reusable half

A per-mode **count** said the modes agreed (59 == 59) and a per-mode **signature** said they disagreed
(RC1 vs COMPILE_FAIL). The row correctly distrusted the count and read the signatures — and the signatures were
a reporting artifact too. Both instruments were describing one lowerer refusal through two different vocabularies,
and neither could say so. **Two disagreeing summaries of the same run are not two facts; running the thing twice
and diffing the stderr is one.** It cost nine minutes to settle a question that had shaped a whole wave of the
plan of attack.
