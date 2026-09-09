# FINDING — three dead-pinned entries in the SNOBOL4 master, and the NUL byte was NOT why

⛔⭐ **CORRECTED 2026-09-08 ~21:5x CDT by hq_B, on hq_T's measurement, and the correction is half of this
file's value.** The filename and title used to read *"one NUL byte hid three dead-pinned entries"*. **The
three dead-pinned entries are real and the count of 25 stands** — re-measured on corpus `HEAD` after this
correction, still 3 in the master and 25 corpus-wide over 932 pins. ⛔ **But the stated CAUSE was wrong,
and with it the DIVERGENCE NOTICE this finding put into the census — that notice has been re-pointed.**
`grep` on this box is a **ugrep shell FUNCTION** interactively; it is **not exported** (no `BASH_FUNC_grep`),
so it never reaches a script. Inside a script — the only place `sbl_died` ever runs — grep is
`/usr/bin/grep` GNU 3.11, whose binary detection suppresses **output** but never **exit status**, and `-q`
prints nothing regardless. Re-measured by hq_B in a script on the real master: **no `-a` => DEAD, with `-a`
=> DEAD**. So `sbl_died` has always answered DEAD everywhere it actually runs, **nothing was concealed, and
no board number was ever hidden** — all three entries already carry `xfail=1`, and `sbl_died` is never
handed `ALL.ref` anyway (its only call sites are per-program captures, `scorecard_snobol4.sh:296,:593`).
hq_T landed `-a` on the authority (SCRIP `60d58c05b`) as **insurance, not a repair**.

⭐ **THE KEEPER, and it is a better lesson than the one this finding was filed for: a predicate must be
measured with the INTERPRETER THAT WILL RUN IT.** `command -v grep` printed a bare `grep` and could not say
so; **`type -t` is the instrument that answers *which* grep**. hq_P hit the identical trap the same night.
⛔ Read every "Why grep said zero" claim below as SUPERSEDED narrative, kept for the record — the
measurement table and the three entry names are what survive.

**Seat:** hq_B · **When:** 2026-09-09 ~02:2xZ (2026-09-08 21:2x CDT) · **Mode:** NONET
**Trees:** SCRIP (incremental `make`, RT_OPT=-O0) · corpus `66ea99dd2`
**Instrument:** `SCRIP/scripts/util_census_dead_pinned_refs.sh` (new, this finding)
**Routed by:** ceo → hq_B, *"hold-the-csnobol4-recut-hq_r-may-make-those-22-winnable"* — *"your census
instrument, the one that applies sbl_died to the PIN … have it ready to re-run and report the
before-and-after."* This is the BEFORE.

## The claim in one line

The dead-pin class is **not confined to `csnobol4_suite`**. The **SNOBOL4 master**
(`corpus/tests/snobol4/ALL.ref`) carries **three** entries pinned to SPITBOL's fatal termination report,
allocator counters included, all three behind the `xfail` column. The corpus-wide BEFORE number is **25**,
not 22. ⛔ **The original second half of this line — that a single NUL byte made them invisible to `grep` —
is RETRACTED; see the correction at the top.** They went unseen because nobody had applied `sbl_died` to
the PIN rather than to the run, which is what this instrument does.

## The measurement

| tree | pins examined | dead-pinned | names |
|---|---|---|---|
| `packages/snobol4/csnobol4_suite` | 97 | **22** | digits file float2 function json1 labelcode label loaderr maxint openi openo2 openo ord popen2 popen rewind1 setexit4 setexit7 tab t update vdiffer |
| `corpus/tests/snobol4/ALL.ref` (master) | 1 file / many entries | **3** | `ord_unimplemented` · `input_eof_hang` · `user_function_arbno_rpos_1` |
| every other package and test tree | 832 | **0** | — |
| **total** | **930** | **25** | |

The three master entries pin, verbatim, SPITBOL's eight-line report:

```
ord_unimplemented.sno(7) : ERROR 022 -- undefined function called
in file              ord_unimplemented.sno
in line              7
in statement         1
stmts executed       1
execution time msec  0
REGENERATIONS        0
memory used (bytes)  11248
memory left (bytes)  1037320
```

⛔ **All three are hidden behind the `xfail` column of `ALL.csv`** (field 6 = `1`; `user_function_arbno_rpos_1`
additionally appears in `ALL.xfail`). Under Lon 2026-09-03 — *"there is no such thing now as XFAIL … if an
XFAIL is a faulty test then let's fix all those tests"* — an xfail is a faulty test or a defect, never a
resting place. These are the first kind: **a pin no correct implementation can match** is a faulty test,
and the xfail is what has kept that invisible.

## ⛔ SUPERSEDED — "why `grep` said zero", retracted (kept for the record)

`corpus/tests/snobol4/ALL.ref` is 330 570 bytes of which **one** is NUL. `file` calls it `data`; GNU grep
therefore treats it as binary and prints nothing while **exiting 0**. Measured, on the real file, with the
authority's own predicate lifted verbatim beside a binary-safe twin:

```
y/foo.ref            authority(no -a)=DEAD   binary-safe(-a)=DEAD
y/bar.ref            authority(no -a)=clean  binary-safe(-a)=DEAD   <- synthetic: identical text + one NUL
snobol4/ALL.ref      authority(no -a)=clean  binary-safe(-a)=DEAD   <- the real master
```

⚠️ `sbl_died` in `scripts/scorecard_snobol4.sh` — the shared authority, sourced by the gimpel, dotnet and
csnobol4 runners — is spelled without `-a`:

```sh
sbl_died() { grep -qE ' : ERROR [0-9][0-9][0-9] -- ' "$1" && grep -qE '^in statement +[0-9]+$' "$1"; }
```

⛔ **RETRACTED: the authority lacking `-a` was never a defect that hid a number** — it answers DEAD either
way in a script (see the correction at the top). hq_T landed `-a` anyway as insurance. What follows was the
original reasoning. **Not patched from here.** It belongs to hq_T's minted row (*a pin whose own content trips `sbl_died` must
count as NO pin in `run_one`, plus a refusal at mint time*) — one word, `-a`, in the same edit. The census's **divergence notice has been re-pointed to say what is
true**: it is a spelling-DRIFT guard only, and explicitly disclaims the "a number is being hidden" reading
that the original wording would have handed every reader.

⭐ **The reusable form, which is the third instance of one law in one night.** `command -v` answers *is it
on PATH*, not *does it exist*. `find corpus/crosscheck` prints nothing and exits 0 for a tree that is
**gone**. ⛔ The third example as originally written — `grep` on a binary file —
**was itself an instance of the law it was illustrating, and I was the one it caught**: `command -v grep`
answered *is there a grep* when the question was *which grep runs inside a script*. The law holds; my third
example was wrong, and the real third example is `command -v` vs `type -t`. The cost was not a hidden board
number (there was none) — it was a divergence notice that would have told every reader one was being hidden.

## What it does NOT mean

⛔ **Do not read 25 as 25 curable bugs, and do not delete a pin on this finding.** The ceo's HOLD stands:
hq_R is building SCRIP's own termination report, and **six of the eight lines we can produce honestly**
(`g_file` `g_line` `g_stno` `g_stcount` + a clock). If that lands, these become programs differing in **two**
implementation-defined lines — a CEO-409 line mask, not an outside-the-baseline exclusion. Removing 22 (now
25) programs from a denominator is the hardest edit on the board to undo. This finding **raises the number
riding on hq_R's landing from 32 to 35** and changes nothing else.

## The instrument

`scripts/util_census_dead_pinned_refs.sh` — reports, changes nothing; rc=0 censused, rc=2 refused.
Proven **red as well as green**: it detects a plain dead pin, detects one hidden behind a NUL byte, does
**not** trip on a half-signature (` : ERROR NNN -- ` with no `in statement` line — `gimpel/ALL.ref` has 37
of those and is correctly clean), refuses rc=2 on an unreachable corpus, and refuses rc=2 on a corpus with
zero pins. Two instrument laws are built in and both were learned by this census **failing them first**:

1. **Zero-found and zero-examined print identically.** The first sweep suppressed directories with no pins,
   so `snoflake 0 / dotnet 0 / testpgms 0` read as CLEAN when it meant NOT LOOKED AT — those three suites
   have no per-program pins at all, they grade live against the oracle. Every directory now prints its
   population, and an empty population is spelled `NO-PINS`, never `0`.
2. **A census that double-counts is the same defect as one that undercounts.** The first run totalled **26**
   for 25 real entries: `ALL.ref` was counted once as a file and again by occurrence. `ALL.ref` is now
   excluded from the per-file loop and counted only in the concatenated-master pass.

Both were caught here before publishing, by the seat that had documented the class four hours earlier —
which is the point: knowing the trap does not exempt you from it, only re-running does.
