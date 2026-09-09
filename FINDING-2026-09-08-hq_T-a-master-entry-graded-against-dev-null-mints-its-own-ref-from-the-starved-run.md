# FINDING — a master entry graded against `/dev/null` mints its ref from the starved run, and then passes forever

**hq_T · 2026-09-08 · Lon's sidecar order + ceo CEO-410**
**Trees:** SCRIP `0567aba18` → `f03584ebc` · corpus `6c94504c0` → `687132c48` · `RT_OPT=-O0`, incremental `make`.

## The one-sentence claim

An entry that reads stdin but is graded with no stdin does not error — it takes EOF, prints what a starved
run prints, and **its `.ref` is minted from that**; from then on it passes in both modes forever while
executing none of the behaviour it was written to test. **Nine such entries were found and cured today**
(one Icon, eight SNOBOL4), and the instrument that finds the rest is now in the tree.

## Why this is not the same finding as hq_U's

hq_U's `config/`-finder finding is about **one search path** being too narrow. This is about the **class**:
the finder was only one of the ways an entry ends up unfed, and the census that followed the cure found the
rest. The two are related the way a bug and its family are.

## The measured specimen, and what made it invisible

`rung36_jcon_recogn` (Icon master entry 831) was absorbed with its companion in `tests/icon/config/`, where
`loose_stdin_companion()` did not look. Its ref was minted as **one empty block** against the standalone
witness's 8 lines. The board read `704/704 ✅`.

⭐ **Nothing was capable of objecting.** The entry ran, exited 0, produced empty output, and matched an empty
ref. Every arm was green and every arm was right about what it measured.

⛔ **And it hid a real engine defect for three sittings.** `test_gate_icn_port_trace.sh` refused since 09-05
saying *"source contains `suspend` but SCRIP_PL_TRACE=1 produced ZERO proc_gen lines"* — and that refusal was
re-attributed three times to a gate gap in another lane. **The gate was the only instrument in the tree that
noticed.** It was refusing because the program never reached a `suspend`: it read EOF and exited. It had
*no run*, not *no ports*. ⭐⭐ **A correct REFUSAL with a false explanation outlives a wrong verdict**, because
nobody re-reads a refusal they have already explained.

Fed and re-cut from `iconx`, the entry exposed an oracle-confirmed defect (a generator called by name inside a
scanning context does not inherit the subject; hq_U's cure, SCRIP `d4799c97a`). The board went
`704/704 (false)` → `703/704 (honest)` → `704/704 (honest)`.

⛔⭐ **THE NUMBER RETURNED TO WHERE IT STARTED AND IS NOW TRUE.** An unchanged number whose meaning changed is
invisible to every freshness and staleness check we own — they all compare values. This is why the SCORE row
says it in words.

## The census, and the honest size of the class

`scripts/util_master_sidecar_census.py` over **5086 entries in 7 masters**: **61** read stdin with no `ALL.in`
block; **34** take program arguments with no `ALL.argv` — and **no master has ever had an `ALL.argv`**, though
the harness has carried full argv-sidecar support since 2026-09-06. *The capability was built and never wired
to the data.*

⛔ **But 61 is not 61 false greens, and saying so would be the same error one level up.** Detection is by
source construct, which is a heuristic. Classified by hand, the 26 SNOBOL4 candidates were:

| class | n | verdict |
|---|---|---|
| **genuinely starved** — reads stdin in a loop, ref empty or visibly truncated | **8** | cured below |
| `INPUT()` **file association** — writes a `/tmp` fixture and reads it back | 9 | correctly graded, owes nothing |
| the `&INPUT` **keyword** — never a read at all | 3 | correctly graded |
| **deliberate EOF tests** — the correct input IS empty (`n02_input_eof`'s own ref reads `input-eof-fails-as-expected`) | 2 | correctly graded |
| needs a **data companion**, not stdin (`claws5`, `treebank`) | 2 | separate row |
| self-contained probes | 2 | correctly graded |

Icon's 5 were 1 starvation candidate and 4 of the same false-positive shape. ⭐ **The census is a work list,
not a verdict** — it is documented as one in its own header, and this table is why.

## The eight, and where their input came from

⛔ **ceo CEO-410: "no sidecar is invented from our own output. A companion is the program's real input, or the
entry has none."** So none was invented. Each of the eight (`word1`–`word4`, `cross`, `triplet`, `fileinfo`,
`expr_eval`) was absorbed from a loose `crosscheck/` program that was deleted with its `.input` companion —
**and both are recoverable from this repo's own history at `c9d235401`.**

Every historical source was diffed against the master's copy before its input was used: five identical, three
differing **only in prose** (a later pass lowercased `INPUT` inside comments, and in `expr_eval` inside one
output literal). Refs cut from `sbl -bf` fed that input, run against **the master's own copy** of the entry —
refusing unless the oracle exits 0 with no error report, since a captured diagnostic is a pinned error.

**Result: 8 fed, 8 refs changed, ZERO changed verdict.** Seven refs went from empty to 198/151/151/98/260/13/9
bytes; the eighth from `" characters,  lines read"` to a real count.

⭐⭐ **THAT ZERO IS THE RESULT, NOT A NULL ONE.** SCRIP was already correct on all eight; the board was right
**by accident**. Before, a regression in any of them was undetectable — the entry could only ever produce empty
output and match an empty ref. **The board is not one higher; it is eight entries less hollow.**

## What is now in the tree

- `write_stdin_sidecar` no longer refuses a line entry (Lon named ONE-LINERS explicitly; the restriction was
  writer-side only — proven both directions on a scratch suite before deletion — and put all **818** SNOBOL4
  one-liners permanently out of reach of an input file).
- `util_master_sidecar_census.py` — the work list. Writes nothing, ever.
- `test_gate_master_sidecars_cover_stdin_and_argv.sh` — a **ratchet**, not a FAIL=0 bar, because each remaining
  item needs an authored input and an oracle re-cut and a zero bar would be red for every seat until that ends.
  The debt may not **grow**. Green on arrival, so blocking from the start. Floors lowered, never raised —
  already `61 → 53`.

## The reusable sentence

⭐⭐ **A green cell tells you the instrument agreed with itself; only the provenance of the input and the ref
tells you it agreed with anything else.** The self-pin/oracle-diff split the port-trace standard draws for
*traces* applies identically to `.ref` files — and, one level further down, to the **input** the ref was cut
from. A ref cut from a starved run is a self-pin of a program that never ran.

## Owed

1. `procedure_write_238` (Icon) — a stdin read-loop printing `0`. Plausibly starved; **no real input survives
   anywhere**, so it is named rather than fabricated. Needs a ruling or an authored input with an oracle re-cut.
2. The 7 unabsorbed `rung36_jcon_*` witnesses under `tests/icon/config/` (hq_U's item 2) — the finder cure means
   a fresh absorb feeds them, but it re-mints nothing already in.
3. The 34 argv declarations. Icon's 9 are in scope; Raku's 25 are PARKED-LON-HOLD.
4. The 2 needing a data companion (`claws5`, `treebank`), whose refs currently pin `Could not read *.dat`.
