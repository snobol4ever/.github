# FINDING — an unset root variable makes every `[ ! -e "$VAR/path" ]` test PASS, so a DONE-WHEN can certify a job nobody did

**hq_P · 2026-08-29 · row `corpus-crosscheck-probe-total-conversion`**

## The measurement

That row's DONE-WHEN — its sole definition of complete — read:

```bash
[ ! -e "$S4E_HOME/corpus/crosscheck" ] || { echo "FAIL: corpus/crosscheck still exists"; exit 1; }
[ ! -e "$S4E_HOME/corpus/archive"    ] || { echo "FAIL: corpus/archive still exists";    exit 1; }
n=$(find "$S4E_HOME/corpus/probe" -name "*.sno" 2>/dev/null | wc -l); [ "$n" = 0 ] || { ... exit 1; }
echo "LON-20260828 total conversion complete: crosscheck GONE, archive GONE, probe loose-.sno=0"
```

`S4E_HOME` is **unset in a plain seat shell** — every seat script derives the root itself
(`${S4E_HOME:-$(cd "$(dirname ...)/../.." && pwd)}`) precisely because it cannot be relied on. Unset, the three
clauses test `/corpus/crosscheck`, `/corpus/archive`, `/corpus/probe`. None exists. All three pass.

**Measured against the real, wholly unconverted tree** — `corpus/crosscheck` holding **401 files** and
`corpus/probe` holding **242 loose `.sno`**:

```
$ env -u S4E_HOME bash -c '<the DONE-WHEN>'
LON-20260828 total conversion complete: crosscheck GONE, archive GONE, probe loose-.sno=0
rc=0
```

⛔ **The criterion certified the row complete, with its own celebratory wording, having verified nothing.** Any seat
could have closed a rank-1 row — one carrying a direct Lon ruling — without doing a minute of the work, and the
`done` gate would have agreed.

## Why this shape is worse than an ordinary broken test

A negative existence test **inverts the usual failure direction**. Most broken instruments go red and get fixed;
this one goes *green*, and it goes green **precisely when it is pointed at nothing**. The three symptoms of a
correctly-finished job and of a completely misaddressed check are byte-identical.

⭐ It is also invisible to review: the command is *correct as written*, for the environment its author had. It
fails only in the environment where nobody set the variable — which is the default one.

## The cure

```bash
S4E="${S4E_HOME:-$PWD}"
[ -d "$S4E/corpus" ] || { echo "REFUSE (rc=2): cannot resolve a corpus under S4E=$S4E -- cannot measure, not a pass"; exit 2; }
```

**Assert the root resolves BEFORE testing anything under it, and REFUSE rather than pass when it does not.**

Negative-tested three ways:

| arm | before | after |
|---|---|---|
| `S4E_HOME` unset, cwd `/` | rc=0 **"complete"** | **rc=2 REFUSE** |
| cwd = seat root, tree unconverted | rc=0 **"complete"** | rc=1 `FAIL: corpus/crosscheck still exists` |
| `S4E_HOME` set, tree unconverted | rc=1 FAIL | rc=1 FAIL |

## The general law

⭐ **A test that locates its subject through a variable must prove the subject exists before reporting on it.**
`[ ! -e "$X/y" ]` answers "is there no `y` under `X`", which is *not* "was `y` removed" — and when `X` is empty the
two answers diverge completely while printing the same thing.

This is the same defect as the empty-glob false-green
(`FINDING-2026-08-29-hq_P-converting-a-family-silently-disarms-its-per-family-glob-script.md`) reached from a third
direction: **zero-subjects and zero-failures are indistinguishable unless something asserts a nonzero denominator.**
There, the denominator was files matched by a glob; here it is the existence of the root itself.

⛔ **Sweep worth doing:** any DONE-WHEN or gate of the form `"$SOME_VAR/..."` where `SOME_VAR` is not asserted first.
`grep -l 'S4E_HOME' /home/resources/postoffice/tasks/*.task.md` is where to start for the batons.
