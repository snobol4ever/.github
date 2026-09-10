# FINDING 2026-09-10 hq_R — `\none_found` succeeds on a &null local, and what flips it is a `/e.SEEN := set()` INSIDE the loop that expression guards

**Tree:** SCRIP `507bc8048` corpus `40d2f633f` · RT_OPT=-O0 · incremental `make` · measured hq_R 2026-09-10 ~18:0x CDT
**Program:** `corpus/packages/icon/ipl/procs/ichartp` (IPL, the last named red on the ipl row) · **Status: OPEN, not cured, named here so the next sitting does not re-derive the narrowing**

## The claim, in one line

In `parse_sentence`, `until \none_found do {...}` never executes its body: `image(none_found)` prints `&null` at that
exact point and `if \none_found then` takes the TRUE branch anyway. Delete `/e.SEEN := set()` from the loop's own body
and the same `\none_found`, on the same value, correctly fails.

## The measurement

Instrumented copy of `ichartp.icn` (procedures unchanged, three `write`s added), run under `setarch -R` so that the
reading is deterministic:

```
TRACE E1 none_found=&null
TRACE E2 BACKSLASH SUCCEEDED
TRACE E3 about to enter until
total=0
```

Trim the until-loop body to `none_found := 1` alone and the same three traces read `backslash fails (correct)` and the
loop runs. Adding the body back one construct at a time isolates it exactly:

| loop body | `\none_found` on a &null local |
|---|---|
| `none_found := 1` | fails (correct) |
| `+ every e := !ch.active do { active_modified := &null }` | fails (correct) |
| `+ if \active_modified then break next` | fails (correct) |
| `+ /e.SEEN := set()` | **SUCCEEDS (wrong)** |

## Two things that make this expensive to find, and both are the general lesson

**It is layout-sensitive, so the first probe you write will disagree with the program.** Calling `parse_sentence` from a
`main` with `local res, n` returns the correct 1 parse; adding one unused local, or one `write` before the call, returns
0. Same source, same input, same binary. Under ASLR the same build alternates between the two readings run to run —
`setarch -R` makes it deterministic and is the only way to bisect it at all. **A defect that moves with the caller's
frame will read as flaky and be filed as "nondeterminism" unless ASLR is pinned first.**

**It did not reduce.** Four hand-built witnesses reproduce the SHAPE and none reproduce the DEFECT: a 14-local generator
with the same local list; the same `until \x do` around an `every` with `/e.SEEN := set()` on a record field; the same
plus `**`/`--` set algebra, `++:=`, `break next`, and a `suspend` inside the loop. All agree with iconx. So the trigger
is not any one construct in the table above — that row is where it BECOMES visible, not where it lives — and the next
sitting should bisect DOWN from `ichartp.icn` (delete toward the witness) rather than UP from a clean file.

## What is already cured, so nobody re-finds it

`ichartp` used to die before any of this, printing its own `error 4 (unmatched left angle bracket)` while reading
`bnfs.byte`: the scan-subject length cache was dropped across both scan-leave paths, so `&subject` came back one byte
short whenever the subject carried a trailing NUL — which `string_2_list` appends deliberately. Cured at SCRIP
`507bc8048`, witness `corpus/tests/icon/a_nul_bearing_subject_keeps_its_length_across_a_nested_scan_and_a_suspend`,
red before and green in both modes after. The grammar now loads identically to the oracle's (59 edges, byte-identical
dump). The defect above is what is left between there and a green `ichartp`.

Also cured on the way: `scripts/util_ipl_grade_programs.sh` looked only in `progs/` and answered `REFUSES(2): no such
program` for `ichartp`, a `procs/` entry the suite has been grading and failing for days. A grader that cannot address
an entry its own suite grades is measuring a different population than the board it exists to agree with; it now
discovers the entry's directory the way the suite does (from the `.std`).
