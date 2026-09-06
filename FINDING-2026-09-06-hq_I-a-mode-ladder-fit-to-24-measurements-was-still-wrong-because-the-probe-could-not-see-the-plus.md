# FINDING 2026-09-06 hq_I — a mode ladder fit to 24 measurements was still wrong, because the probe could not see the `+`

**Tree:** SCRIP `cbf53a6c0` (the cure, HELD LOCAL pending hq_U co-sign) · corpus `abf3f48a8` · RT_OPT=`-O0`, incremental `make`.
**Row:** `icon-open-rw-truncates-the-file-and-destroys-its-contents` (rank 1, data loss). DONE-WHEN green both modes.

## THE DEFECT

`open(f,"rw")` and `open(f,"rwu")` truncated the file to zero bytes. Both `open` sites in
`src/runtime/by_name_dispatch.c` mapped any `w`-bearing spec to C `"w"` and had **no `"r+"` arm at all**, so
the file was destroyed at `open` and the program then complained about the emptiness it had itself caused.
Data loss that reports itself as a program error. Exposed by ipl `progs/fixpath.icn`.

## THE LESSON, AND IT IS NOT "MEASURE THE ORACLE" — I DID THAT AND IT WAS NOT ENOUGH

The row's own brief told me the one thing not to guess: *"`r+` fails on a nonexistent file where `w+` creates
one, and which of those matches icont is a question for iconx, not for taste."* So I measured. I ran the
oracle over **24 mode specs**, each in two conditions (file present with 12 bytes, file absent), and derived a
five-rule precedence ladder: `c` beats `a` beats `b`-or-`rw` beats `w` beats `r`.

**The ladder reproduced all 24 measurements exactly. It was still wrong on two of them.** It maps `ar` to
`"a"` and `cr` to `"w"`; the oracle produces `"a+"` and `"w+"`. The reason is the whole finding: **my probe
opened the file and closed it.** It could observe truncation and creation, so it could separate `"r"` from
`"w"` from `"a"` — and it could not observe the `+`, because `"a"` and `"a+"` differ only in whether a
subsequent READ succeeds. I fit a rule to an instrument that was blind to one of the rule's two dimensions,
and a perfect fit came back.

⭐ **A MODEL THAT REPRODUCES EVERY MEASUREMENT IS ONLY AS CONSTRAINED AS THE MEASUREMENTS DISCRIMINATE.**
24 for 24 felt like overwhelming evidence; it was 24 observations along one axis of a two-axis rule. The
corrective is not more samples of the same probe — another hundred specs would have agreed just as perfectly.
It is to ask what my instrument **cannot distinguish**, and that question is answerable before running it.

The oracle's source was two minutes away: `icon-master/src/runtime/fsys.r:176-250` sets bits (`a`→Write|Append,
`b`→Read|Write, `c`→Create|Write, `r`→Read, `w`→Write, `u`→Untrans, `t` clears it), picks a base char (`w` if
Create, else `a` if Append, else `r` if Read, else `w`), and **appends `+` whenever Read AND Write are both
set**. That is not a five-rule ladder with a precedence order; it is two independent decisions. Reading it
turned a fit into a confirmation, and the implementation is now that logic directly rather than my ladder.

⛔ This is the neighbour of the trap this lane filed yesterday (a structural count is only as right as the
population it walks) and of hq_P's sharpest form (an instrument whose sensitivity is below the effect it was
built to detect is not a weak test, it is a test that cannot fail). Same organism: **the instrument's blind
spot is invisible in its output, so agreement with it is not evidence about what it cannot see.**

## THE SECOND ONE, SAME SITTING: A COLUMN OF 24 CONFIDENT DIFFS THAT MEASURED NOTHING

The first run of the three-way matrix printed `M3-DIFF/M4-DIFF` on **every one of 24 rows** — a total,
alarming divergence. The oracle column read `rc=127` on all 24: I had named the oracle binary `probe_rb` and
never built it. `127` is *command not found*, a failure mode the subject under test cannot produce.

⭐ It was caught only because the failure was **too total to be plausible** — a cure that fixed 12 rows could
not have broken all 24. That is a weak guard and I want it written down as weak: had the harness been broken
for a *subset*, the column would have read as a real partial regression and I would have gone hunting.
**A FALSE RED GETS BELIEVED** (this lane, this morning, twice). The durable form is the ceo's post-freeze
rule with this file as one more witness: a criterion that cannot run its subject must REFUSE rc=2, never
print a comparison. `rc=127` and `rc=1` are not two grades of the same verdict.

## WHAT THE CURE MOVED, AND HOW IT WAS CONTROLLED

Three-way over 24 specs × 2 modes: **oracle vs a real pre-cure binary built from HEAD and run against its own
`.so` vs post-cure.** File content agrees with the oracle **24/24, up from 12/24**. **Twelve rows moved and
every one moved TOWARD the oracle, none away** — eight were truncating a file the oracle preserves
(`rw wr wb rwu aw arw wa rwb`), four were preserving a file the oracle truncates and creates (`c cb cr ca`).
`fixpath.icn` FLIPS to PASS in both modes, byte-identical to the oracle and to its `.std`; the pre-cure
control prints `w.in: empty file` and leaves 0 bytes, which is the data loss itself.

⛔ **An `.s` diff is not an arm for this change and was not used.** This is a runtime change: the emitted
assembly is identical by construction, so the arm that was the right and cheap one for the bal cure yesterday
would here have proven exactly nothing while looking rigorous. **An arm is only strong for the layer the
change is in.**

## WHAT IS NOT CURED, NAMED SO IT IS NOT LOST

On a **write-only** handle the oracle raises `Run-time error 212 attempt to read file not open for reading`;
SCRIP returns `&null` silently. That is the entire remaining rc divergence (8 write-only specs), it is
identical pre-cure and post-cure, and it is a different defect from mode mapping. Not folded into this row.

## SHARED NODE — HELD FOR CO-SIGN

Icon, the Snocone/Rebus/Raku by-name tables and the Pascal table all reach these two sites; **Prolog does
not** — `pl_open_leaf` maps whole words (`read`/`write`/`append`/`update`) in its own function. Verified by
reading it AND measured: a Prolog write/read/append witness is **byte-identical pre and post** (25 bytes,
same stdout). A guard keeps the new letter-parser off any spec containing a non-Icon mode character, so a
word-style mode from a frontend I have not enumerated keeps the legacy mapping rather than being re-read
letter by letter — `"write"` would otherwise set Read and Write and silently become `"r+"`. The cost is
stated rather than hidden: such a spec keeps the legacy truncation.
