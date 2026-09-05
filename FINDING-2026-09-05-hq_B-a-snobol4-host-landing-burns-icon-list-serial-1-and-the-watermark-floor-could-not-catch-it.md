# A SNOBOL4 HOST() landing burns Icon list serial 1, and the watermark floor could not catch it

**Seat:** hq_B · **Date:** 2026-09-05 · **Trigger:** ceo audit — SCORE's icon cell said `601/601`, the board read `599`
**Bisected to:** SCRIP `1d31e2963` *"HOST(2,i) and HOST(3): implement the argv contract both oracles actually have"*

## The measurement

`board_icon_master.sh` on origin reads run-graded **m3 599 / m4 599 of 601**, ast 153/153. Two entries are red in
both modes. `git bisect` over the 67 commits since `6f3d0e72c` — the commit the stale cell cited — with a 3-line
probe. **The claimed-good baseline was re-proved good before bisecting, not assumed.**

Witness: `procedure main() write(image([1,2,3])) end`

| | output |
|---|---|
| `icont`/`iconx` (the oracle) | `list_1(3)` |
| SCRIP after `1d31e2963` | `list_2(3)` |

## The mechanism

`1d31e2963` removed the four `nparams >= 1` gates on `rt_main_args_stage` in `src/driver/scrip.c` (two m4 emit
sites, two m3 sites). Staging calls `rt_args_list_from` → `rt_make_list`, and `rt_make_list` draws a serial from
`rt_agg_serial_list()` (`g_agg_list_ser++`). So **every Icon program now allocates a list at startup**, burning
serial 1, and the first list the program itself creates images as `list_2`.

## ⭐ Why it looked safe: the gate was right for Icon and wrong for SNOBOL4 at the same time

Measured on the oracle rather than reasoned:

| entry | `write(image([1,2,3]))` | with args passed |
|---|---|---|
| `procedure main(a)` | `list_2(3)` | `list_2(3)` |
| `procedure main()` | `list_1(3)` | `list_1(3)` |

**Icon materializes the args list iff the entry has a formal parameter**, independently of whether args are
actually supplied. That is exactly what `nparams >= 1` encoded — so for Icon the gate was not incidental, it *was*
the contract.

And the commit's reasoning about SNOBOL4 is equally correct on its own terms, quoted from its message:

> Those gates ARE wrong -- whether the entry graph has formal parameters has nothing to do with whether HOST()
> sees argv

True for SNOBOL4: `genc.sno` has a zero-param entry and must still see argv, which is the defect that commit
cured. **One gate, two contracts, and the languages disagree about it.** Neither half of the reasoning is wrong;
what was missing is that the gate was answering two different questions.

⛔ A cure has to keep HOST(3)'s staged count exact — it is `total_cmdline_entries - rt_main_args_count()`, and
`rt_main_args_count()` reads the staged list's own `frame_size` — while not letting a bookkeeping list that no
program can observe consume a program-visible serial. That is a contract decision inside the HOST row's own
code, so it is named here and not taken: Lon's SNOBOL4-ONLY order stands and this is Icon.

## ⛔ The reusable half: a floor cannot catch a fall that stops above it

The Icon watermarks are pinned at **m3 596 / m4 596**. The board fell from 601 to 599 and stayed above the floor,
so `board_icon_master.sh` printed **`✅ ICON MASTER BOARD OK ... (watermarks held)`** on every run through the
whole regression, and the run even printed `⭐ WATERMARK MOVED UP (m3 599 vs 596)` — inviting a re-pin of a
number that was itself two below the truth.

Nothing was lying. The floor did its job, which is to catch collapses, and a 2-entry regression is not a collapse.
But the SCORE cell asserted `601/601 FAIL=0` from a real earlier measurement, and no gate compares a *cell* to a
*board* — `test_gate_score_tables_agree.sh` compares the two TABLES to each other, and both tables carried the
same stale 601. **Two mirrors agreeing is not corroboration when both were written from one source.** It took a
human reading the board beside the cell (the ceo's audit) to see it.

⭐ Generalisation worth keeping: a watermark answers *"did we collapse"*, not *"is this number true"*. Any cell
that states `FAIL=0` is a claim a floor cannot check, because a floor is satisfied by any value above it.

## The second red is unrelated

`procedure_record_every_replace_2` is **not** a regression from this commit — it is an independent `map()` defect.
One-line witness, oracle-confirmed:

```
map("hello", &cset || "e", &cset || "-")            SCRIP: hello      iconx: h-llo
map("hello", repl("z",256) || "e", repl("z",256) || "-")   both: h-llo
map("abc", "aa", "xy")                                     both: ybc
```

So it is **not** a 256-length cap and **not** the last-duplicate-wins rule — both of those are correct in SCRIP.
It is specific to a `&cset`-derived source string.

⚠ **My first reading of this one was wrong and is recorded so nobody repeats it.** I diagnosed a missing companion
file, because a hand-run in an empty directory could not `open("fncs1.dat")`, and I had just found that corpus
`9e5ccb5ee` moved companions into `config/`. The harness already searches `config/` — with a comment block
explaining that it must. The file was fine, my test directory was not. I had built a plausible causal story out of
a real commit and a real symptom that had nothing to do with each other, and it survived until I ran the program
with its companion actually present.
