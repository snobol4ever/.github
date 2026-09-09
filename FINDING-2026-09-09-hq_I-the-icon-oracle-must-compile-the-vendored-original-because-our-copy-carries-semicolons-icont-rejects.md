# The Icon oracle must compile the VENDORED ORIGINAL, because our copy carries semicolons icont rejects

**hq_I, 2026-09-09, under CEO-445 (Lon 09:0x: *"Switch to Icon completely... Get 100% using oracle probes"*).**
Measured on SCRIP `46ef31d1d`, corpus at origin, oracle `/home/resources/icon-master/bin/icont` + `iconx`
(Arizona Icon v9.5.25a), upstream `/home/resources/jcon-master/test`.

## The finding

Grading the 20 `rung36_jcon_*` xfail markers by compiling **our** `corpus/tests/icon/rung36_jcon_<stem>.icn`
with `icont` reports **5 of 20 as ORACLE-COMPILE-FAIL**:

```
rung36_jcon_case      Line 28  # "}": invalid case clause
rung36_jcon_checkfpx  Line 107 # ";": missing then
rung36_jcon_ck        Line 170 # ";": missing then
rung36_jcon_image     Line 67  # "else": invalid expression
rung36_jcon_sorting   Line 108 # "}": invalid case clause
```

**All five UPSTREAM twins compile clean, rc=0, no diagnostics.** The difference is ours: SCRIP's Icon frontend
is semicolon-required and does zero newline processing (`RULES.md` Semantics; icont-style Beginner/Ender
insertion is forbidden in `src/parsers/icon/`), so the vendored programs were adapted with explicit semicolons.
A `;` after a case-clause expression, or between a condition and its `then`, is a **syntax error for icont**.

⛔ **So our adaptation changed what the oracle can read.** The oracle must compile the vendored original while
SCRIP compiles our copy; the two are comparable exactly to the extent the adaptation is semantics-preserving,
which is a property to state rather than assume. Grading our copy with icont does not produce a wrong number —
it produces **no number at all**, five entries that look ungradable and are not.

⭐ **The general form, and it is not about semicolons.** Whenever a suite is *adapted* to the implementation
under test, the adaptation silently becomes part of the oracle's input, and an oracle that then refuses reads
as a property of the program. This is the sibling of `command -v icont` answering a narrower question than the
one asked: the instrument was correct and the question was wrong. **The vendored original is the oracle's
source; our copy is only ever the subject.**

## The feeding rule is the vendor's own, and it covers argv as well as stdin

`jcon-master/test/addtest` is the authority and says it in four lines:

```sh
if [ -r $BASE.dat ]; then
    ./$BASE $BASE.dat <$BASE.dat >$BASE.std     # the .dat is argv[1] AND stdin
else
    ./$BASE </dev/null >$BASE.std
fi
```

So `errors`, `fncs`, `sorting` and `struct` — which read stdin and have no companion in `config/` — are **not
unfed by accident**: `/dev/null` is their correct input, upstream says so, and an earlier pass of mine flagged
them UNFED on the (over-cautious, and wrong) inference that a stdin-reading program must want stdin. And the
three of the twenty that DO have a `.dat` (`io`, `others`, `recent`) need it in **both** positions. Our eight
`config/rung36_jcon_*.stdin` files were checked byte-for-byte against the upstream `.dat` and **all eight
match**, so the stdin half was already right; the **argv half was missing entirely**, and supplying it moved
`rung36_jcon_io` from FAIL to PASS in m3. That is Lon's 2026-09-08 sidecar order (*"command-line args and an
input file for each test"*) arriving on a second suite, and the cheapest way to satisfy it here is to read the
vendor's runner rather than to infer per-program intent.

## The measured grid — 11 of 20 markers are stale, not 8

Both modes, oracle cut per `addtest` from the upstream source, SCRIP running our copy:

| verdict | entries |
|---|---|
| **PASS both modes, stored ref already matches the fresh oracle** | arith, case, checkfpx, ck, errkwds, image, iobig, large, others, radix (**10**) |
| **PASS both modes, stored ref DIVERGES from the fresh oracle** | nargs (**1**) — ref must be re-cut *before* the marker drops |
| **still red** | errors, evalx, fncs, gener, io (m4 only), misc, recent, sorting, struct (**9**) |

⛔ **This supersedes my own 2026-09-08 count of eight**, and the correction is upward for a reason worth
keeping: that sweep graded against the **stored `.expected` sidecars** and against our own copies, which is
the self-pin-is-not-an-oracle class hq_T named in refusing the marker drop (CEO-395). Re-cutting from the
vendored source with the vendor's feeding rule is a different and stronger instrument, and it disagrees.
hq_T's refusal was correct and its stated order — **re-cut first, drop second, in one commit** — is what the
drop follows.

`rung36_jcon_errors` additionally aborts the m4 compiler (`IR op=16 has no template`), which is already a
rank-0 row in hq_U's queue per CEO-441 item 6 and is not counted as a marker question here.
