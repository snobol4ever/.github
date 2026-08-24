# FINDING: sweep-free-rows-are-real — pass 7

**Context:** `sweep-free-rows-are-real` STEP 7 (row-factory continuation, same method as pass 6). Trees pulled fresh FIRST per pass 6's lesson (a stale checkout is indistinguishable from a false citation). No cure attempted anywhere except one in-place citation correction (see below) — zero edits to any `.c`/`.h`/`.S`/`.cpp` source in SCRIP.

Trees at session start (all fresh `git pull --rebase`, clean, `main == origin/main`): SCRIP `447faf10`, corpus `07564948`, `.github` `afce7f38`.

⚠️ Aside, not part of this row's own scope: the `corpus` pull renamed `corpus/lon/` → `corpus/snobol4/lon/` (a plain git rename, files untouched). Per CLAUDE.md this directory is off-limits — no read/cat/grep/run in any mode. Noted only so a future session isn't surprised the path moved; not entered, not inspected beyond the rename summary git printed.

## Method (unchanged from pass 5/6 — exact-diff against `SWEEP-CLASSIFIED.tsv`)

```
awk -F'\t' 'NF>=4 && $4=="FREE"{print $2}' QUEUE.tsv | sort > a
ls claims/ | sed 's/.claim$//' | sort > b
comm -23 a b            # true-free set
comm -23/-13 against SWEEP-CLASSIFIED.tsv's TOPIC column  # exact delta
```

True-free count: 145 (pass 6 end) → **141** (this pass). A *smaller* count than last pass — first time this sweep has gone down, and (as pass 5's own lesson warned) a stable-or-shrinking count says nothing about churn underneath it; this pass's net -4 is actually -5/+1, not "4 rows quietly vanished."

## Delta vs pass 6 baseline

**-5, all correctly excluded (claimed, not lost):**

| topic | QUEUE.tsv state | claim file contents |
|---|---|---|
| `arith-operand-type-check` | FREE | `seat04 / RUNNING` |
| `conform-defer-tab-span-crash` | FREE | `seat01 / RUNNING` |
| `defer-nv-read-by-pointer-not-name` | FREE | `seat06 / RUNNING / DONE` (orphaned-DONE, not yet swept) |
| `nul-in-counted-strings-class-defect` | FREE | `seat07 / RUNNING / DONE` (orphaned-DONE, not yet swept) |
| `recursion-stack-overflow-diagnostic` | FREE | `seat02 / RUNNING` |

All 5 checked directly (QUEUE.tsv row + claim file contents, not inferred). QUEUE.tsv's own `state` column still reads FREE for all 5 — confirms pass 2's operational redefinition still holds: the claim file, not the queue row's state/owner columns, is the actual lock. 3 are in-progress work (RUNNING only), 2 are finished-but-not-yet-swept (matches the "orphaned DONE-terminated claim" pattern passes 2/3 already characterized as healthy and not worth chasing — count grew 43→51 this pass, proportional to overall claim growth, see sanity checks below).

**+1, verified LIVE by direct repro (not by reading the brief):**

`callgrind-sbl-opaque-core` — minted by seat02 off `perf-string-runtime`'s STEP 1 cross-kernel sweep, receipts in `FINDING-2026-08-24-seat02-ifunc-phantom-generalizes-plus-gc-crash-and-sbl-opacity.md`. Brief claims SPITBOL's own oracle binary (`sbl`) is 99.1% unattributed under callgrind (`154,614,358` / `156,056,575` Ir as `???:0x...`), and that the mechanism is "no covering symbol at all" near the hot addresses, nearest being `sysbs`@`0x4032ba`, "a gap of many KB."

Independently checked against `/home/resources/spitbol-bench-oracle/sbl`:
- `file sbl` → "not stripped" ✓ matches.
- `nm sbl | grep ' [Tt] '` → 2,687 text symbols ✓ matches exactly.
- **The "gap of many KB, nothing named" sub-claim does not hold up.** A correct hex→decimal nearest-preceding-symbol check (I hit the same string-vs-numeric awk bug on my first attempt and had to redo it with explicit `$((16#hex))` conversion — plausibly what produced the brief's wrong answer too) finds 503 symbols between `sysbs` and the last cited hot address, with the true nearest-preceding symbols for the three cited addresses being `ocnc6`@`0x406941` (5 bytes before `0x406946`), `call_25`/`_l0042`@`0x4071fa` (29 bytes before `0x407217`), and `pnth4`@`0x40825c` (27 bytes before `0x408277`) — not `sysbs`, not "many KB" away.
- **This does not weaken the headline 99.1% number — it explains it better.** `readelf -sW sbl` shows only 156 symbols are properly-sized `FUNC`; 3,856 are `NOTYPE` with size 0 (`ocnc6`/`pnth4`/`sysbs` all included). Every nearby label exists but is unusable as a callgrind attribution boundary — exactly the same missing-`.type`/`.size` mechanism as `callgrind-opaque-bb-labels` (confirmed by reading that row's own task file: it's the identical `readelf -s | awk '$4=="NOTYPE"'` signature, just on SCRIP's own emitted labels instead of a third-party binary).

**Verdict: LIVE-p7.** Correction (not a cure — a citation fix) written into `callgrind-sbl-opaque-core.task.md`'s LEDGER: the row's own STEP 1 item 2 ("is this fixable at all") should treat this as the *same* mechanism as `callgrind-opaque-bb-labels`, unpatchable only because `sbl` is a third-party binary outside the two approved compatibility hunks — not a distinct "hand-assembled interpreter has no finer boundaries" phenomenon as currently framed. Likely converges on the same "permanent, document it" bottom line STEP 1 already guessed, but for a verified reason. STEP 1 itself remains open and unclaimed — not worked here.

## Sanity checks (same as passes 1-6)

- Duplicate topic rows in QUEUE.tsv: **0** (176 data rows, 176 unique topics).
- Orphaned DONE-terminated claim files: **51** (was 43 at pass 3, 68 total claim files vs 176 queue rows) — proportional growth, same healthy shape as prior passes, not chased.

## Baseline rewritten

`/home/resources/postoffice/SWEEP-CLASSIFIED.tsv` updated for pass 8: 141 topics (140 carried forward + `callgrind-sbl-opaque-core` newly LIVE-p7, 5 claimed rows dropped). Prior version backed up to this session's scratchpad only (not committed — the live file itself is the record, per the established pattern). SCRIP `447faf10` / corpus `07564948` / `.github` `afce7f38` cited in the file's own header, each repo's own hash as the FACT RULE requires.

## Cadence note (still not this row's call)

Pass 5: Δ0(net). Pass 6: Δ+3(net), Δ+9 gross. Pass 7: Δ-4(net), Δ+6 gross (5 out, 1 in) — the first net *decrease*, driven entirely by other seats picking up free rows, not by any slowdown in new mints. HQ's event-driven-vs-clock-driven cadence question (raised pass 4, still open) gets a new data point here: gross churn (6 rows changing status) stayed in the same 4-9 range passes 5-7 all showed, regardless of net direction — net alone would have been a misleading cadence signal this pass.
