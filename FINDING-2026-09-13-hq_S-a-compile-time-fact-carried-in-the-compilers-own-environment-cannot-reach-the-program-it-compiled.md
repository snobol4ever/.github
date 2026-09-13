# FINDING 2026-09-13 hq_S — A compile-time fact carried in the COMPILER'S OWN ENVIRONMENT cannot reach the program it compiled, so mode 4 stopped counting statements the moment they came from CODE()

**Row:** `snobol4-stcount-diverges-in-m4-from-m3-and-the-oracle-inside-code-eval-compiled-statements` (hq_S, rank 0, minted by me on 09-13 as the split-out half of the `&STLIMIT` row).
**Tree:** SCRIP `6d384fd08`, corpus `485766db2`, incremental `make`, `RT_OPT=-O0`.
**Cure:** `src/runtime/keywords.c` — `rt_stmt_enter` seeds `SCRIP_SNO_STMTKW` on the first counted statement.
**Gate:** `scripts/test_gate_sno_stcount_counts_statements_inside_code_fragments.sh`, 10 witness-modes, proven RED on the pre-cure build.

## The defect

`CODE(str)` parses and lowers its argument **at run time** (`code_at`, `src/runtime/runtime_eval.c`). The
SNOBOL4 lowerer offers two shapes for a statement boundary and picks between them on `g_sno_uses_stmtkw`
(`src/lower/lower_snobol4.c:2544`): the **counted** `SNO$STMT` hook, which calls `rt_stmt_enter` and so bumps
`&STCOUNT` and enforces `&STLIMIT`, or a cheap inline statement mark. The flag is computed by a scan of the
whole program (`sno_scan_stmtkw`) and — this is the defect — **published to the fragment path through
`setenv("SCRIP_SNO_STMTKW", "1", 1)`**, i.e. through the environment of the process doing the lowering.

In **mode 3** the main program is lowered in the same process that later runs it, so the seed is already in
place when `code_at` lowers a fragment. In **mode 4** the scan happened in the COMPILER's process and the
`setenv` died with it; the generated binary starts with the flag at its initialiser, every `CODE()` fragment
is lowered down the uncounted arm, and **every statement executed inside dynamically compiled code is never
counted**. `&STCOUNT` drifts low, without a diagnostic, in the one mode where the drift is hardest to see.

Measured, 4-line witness, two calls into a `CODE()`-compiled function that loops N times:

| N | oracle (`sbl -bf`) | m3 | m4 before | m4 after |
|---|---|---|---|---|
| 1  | 4 / 9 / 14  | same | 4 / 6 / 8 | same as oracle |
| 5  | 4 / 13 / 22 | same | 4 / 6 / 8 | same as oracle |
| 12 | 4 / 20 / 36 | same | 4 / 6 / 8 | same as oracle |

⭐ **Read the "before" column down, not across.** It is the SAME THREE NUMBERS whatever the fragment does,
because the only statements m4 counted were the ones outside `CODE()`. That constant is the signature of the
whole class, and it is what makes a diff-shaped acceptance dangerous here: a build that had stopped counting
altogether would produce a CONSTANT in both modes and the m3-vs-m4 diff would read zero.

## Why it surfaced as a wrong answer and not as a counter reading

AIS `ATN.SPT` was the reporting witness, and it does not print `&STCOUNT` anywhere. Its own `GENNAME`
(`ATN.IN:110-114`) mints every generated parse-node name as `'*' X '_' &STCOUNT '*'` — the program **encodes
the statement counter into its answer**. So a counter that drifts by 9 shows up as `PARSE_NOUN_GROUP_2434`
where the oracle and m3 say `_2443`: a wrong parse-tree label, 106 lines of it, with nothing in the output
naming a counter. Masking the trailing `_NNNN` dropped that diff to exactly zero, which is what said
*the machine is right and only the counter is wrong* before any code was read.

## The cure, and why it is where it is

`rt_stmt_enter` is reached **only** from the counted arm — the uncounted arm never calls it (its single
`SNO$STMT` call passes `-1`, which `rt_stmt_enter`'s dispatcher skips). So *being called at all* is an exact
runtime witness that this program was lowered with statement hooks, available in both modes and requiring no
new state to observe. `g_stcount == 1` fires it once, on the first counted statement, for the price of one
compare per statement:

```c
static void rt_stmt_seed_code_fragment_statement_hooks(void) { setenv("SCRIP_SNO_STMTKW", "1", 1); }
...
    if (g_stcount == 1) rt_stmt_seed_code_fragment_statement_hooks();
```

⛔ **No new global.** The project bans one without Lon's in-chat permission, and the obvious shape here — a
`g_rt_stmt_hook_live` flag — was not needed once `rt_stmt_enter`'s own reachability was recognised as the fact.
⛔ **Nothing outside `src/runtime/`.** `SCRIP_SNO_STMTKW` is the channel the lowerer already publishes and
already reads for exactly this purpose; the cure feeds the existing interface rather than adding one, so the
lowerer (another concern's files under the NONET cut) is untouched.
⚠️ **Named side effect, not hidden:** the variable is now set in the environment of a running mode-4 program
and is therefore inherited by anything it spawns. The only effect on a child `scrip` is that it lowers with
counted hooks — which is what SPITBOL does unconditionally — so the leak is toward the oracle, not away.

## Why the gate pins values and sweeps, instead of diffing the two modes

The row's SYMPTOM was an m3-vs-m4 diff, and the cheapest wrong cure for it is to stop counting in both modes.
So the gate never compares SCRIP to SCRIP. Arm 1 pins `&STCOUNT`'s **value** at three points against the
oracle's own reading, in both modes. Arm 2 is the **boundary** arm: it sweeps the work inside the fragment
(N = 1, 3, 7, 12) and requires our count to TRACK the oracle's across the range. On the pre-cure build arm 2
reds four times over, and its output is the table above — the oracle's counts climbing while ours sit at a
constant. That is the shape CEO-678 named for limit, size and depth rows, applied to a counter: *a verdict arm
asks "did it count?"; a boundary arm asks "did it count the right number, everywhere?"*.

The gate also runs the **oracle twice and diffs it against itself** before using it as a ref, and REFUSES rc=2
rather than grading if the two runs differ — the prophylactic from
`FINDING-2026-09-13-hq_S-a-done-when-that-byte-compares-a-program-printing-a-clock-reading-is-unsatisfiable-and-the-oracle-differs-from-itself.md`,
now wired into an instrument instead of remembered.

## Arms

- Row DONE-WHEN: ATN m3-vs-m4 **0 diff lines** over 427 lines (was 106), and additionally **oracle-vs-m3 = 0** and **oracle-vs-m4 = 0** on the same normalization — a stronger reading than the row asked for, because two modes agreeing prove nothing on their own.
- New gate: **10 witness-modes PASS=10 FAIL=0**, and **PASS=5 FAIL=5** with the cure `git stash`ed and the tree rebuilt, every red on an m4 arm.
- `make preflight`: **39 arms, 0 red**.
- Smokes, all languages, compared name-for-name against the same tree rebuilt without the change: the red set is **identical** (`sn26_scr_subscript_bridge`, `snobol4_jvm`, `snobol4_net`, `snobol4_net_bb_gate`, `sno_command_match`, `snocone_parse_a..j`, `unified_broker`) and the refusals are identical (`self_beautify` — no CSNOBOL4 oracle installed; `snobol4_js` — the driver removed `--target`). Icon 15/15, Pascal 9/9, Prolog 5/5, Snocone 5/5, polyglot 2/2, hello-all-langs 6 rows no drift.

## The gap this leaves, named so it is not mistaken for closed

`&STLIMIT` is enforced only on the counted arm. A program that mentions **no** statement keyword still lowers
down the inline-mark arm, where `g_stcount` is incremented by the emitted `inc` but never compared against
`kw_stlimit` — so a runaway loop in such a program never raises `ERROR 244`. That is a separate class from
this row, it predates it, and this cure neither closes nor worsens it. Not rowed here; reported to the ceo.
