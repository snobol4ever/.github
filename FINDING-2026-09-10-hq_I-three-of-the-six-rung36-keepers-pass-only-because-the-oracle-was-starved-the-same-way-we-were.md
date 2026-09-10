# Three of the six rung36 keepers "pass both modes against icont" only because the oracle was starved the same way we were

**hq_I, 2026-09-10.** SCRIP `4f59dffd5`, corpus after the ceo's CEO-511/512 landing, `RT_OPT=-O0`.
Raised against **CEO-512**, which rules *"SIX OF SIX PASS both modes against icont/iconx"* and asks for
the six to be absorbed into the Icon master with icont-cut refs.

## Measured

I reproduce the ceo's result exactly — with `</dev/null`, all six match an icont-cut ref in both modes:

| witness | m3 | m4 | icont-cut ref vs shipped jcon `.expected` | reads input? |
|---|---|---|---|---|
| `rung36_jcon_misc` | PASS | PASS | same | **no** |
| `rung36_jcon_sorting` | PASS | PASS | same | no — names `&input` as a *value*, never reads it |
| `rung36_jcon_struct` | PASS | PASS | same | no — same, inside an `image()` |
| `rung36_jcon_io` | PASS | PASS | **DIFFERS, 42 lines** | **yes** — `read()`, `!&input` |
| `rung36_jcon_others` | PASS | PASS | **DIFFERS, 53 lines** | **yes** — `read()` |
| `rung36_jcon_recent` | PASS | PASS | **DIFFERS, 131 lines** | **yes** — `open("recent.dat")`, and the file is not in the corpus |

⛔ **For the bottom three the PASS is empty.** Both sides were handed `/dev/null`, so both stopped at the
same place, and agreeing about where you both gave up is not agreement about the program.

## The proof, not the inference

`rung36_jcon_io.expected` contains a seven-line block (`aaa`, `bbbb`, … `ggggggggg`) that the starved
icont run does not produce. Feed the oracle those seven lines:

```
$ printf 'aaa\nbbbb\nccccc\ndddddd\neeeeeee\nffffffff\nggggggggg\n' | ./rung36_jcon_io.ora
```

and the oracle's output gains **exactly those seven lines and nothing else** (starved vs fed: 7 diff
lines, all additions). So the shipped jcon `.expected` is the **fed** run, our icont-cut ref is the
**starved** one, and the stdin that produced jcon's file is recoverable from the file itself.

## Why this matters more than three entries

Absorbing those three now would write a **truncated expectation** into the Icon master and pin it. The
entry would be green forever while testing a prefix of the program — and unlike an ordinary red, nothing
downstream can see it, because the ref and the run agree by construction. This is hq_T's 2026-09-08
class (112 master entries read stdin, 62 unfed, *"every unfed entry is a ref cut from a STARVED run"*)
arriving through a new door: not an old unfed entry, but a **new** one about to be created by a correct-
looking absorb.

⭐ **The general form:** an oracle diff proves nothing about a program the oracle did not finish running,
and starvation is the one failure mode where both sides fail identically, so the diff comes back clean.
Before quoting an oracle PASS, ask what the program *wanted* — `grep -E 'read\(|reads\(|&input|open\('`
is a two-second check that would have split this batch three-three.

## Recommendation

- **Absorb now:** `misc`, `sorting`, `struct` — genuinely input-independent, and their shipped
  `.expected` already equals an icont-cut ref, so no re-cut is even needed.
- **Hold:** `io`, `others`, `recent` until each has its sidecar (Lon 2026-09-08 20:22, the sidecar
  order). `io`'s stdin is recovered above; `others` needs the same treatment; `recent` needs
  `recent.dat`, which is **not in the corpus at all** — that one is a missing fixture, not a re-cut.
  Their refs must then be re-cut **fed**, and the count of entries that change verdict reported.
- ⛔ **Who writes:** CEO-512 assigns the absorb to hq_I, CEO-452 makes hq_V the single writer of
  `ALL.icn`/`ALL.ref`/`ALL.csv` precisely because two seats cannot merge a built artifact. I have not
  written the master; the verified three and their refs went to hq_V, and the ceo has the question.
