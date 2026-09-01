# FINDING 2026-09-01 (seat07) — the full startup-executed list, and the order file is scoped to ~1/7 of its own lever

**Row:** `rtx-startup-touch-rewrites` `## NEXT` item 1 (linker ordering). **Derivation only** — the ordering
itself is deliberately NOT landed; this is the half the item calls "the rung".
**Artifact:** `corpus/benchmarks/snobol4/startup-touch-coverage-20260901T230821Z-seat07-executed-page-symbol-coverage.tsv` (full 77-function list + all counts).

## 1. The list, and the original sizing is CONFIRMED not overturned

The seat03 FINDING named **15** functions and estimated **65**. Re-derived whole on SCRIP `14f384ed`:

| workload | executed `.so` fns | of which `src/runtime` | RT pages spanned | RT cluster floor |
|---|---|---|---|---|
| `OUTPUT = 1` (do-nothing witness) | 480 | **77** | **32** | **7** |
| `treebank-match` | 842 | 155 | 116 | 72 |
| union | 847 | 158 | 116 | 73 |

⭐ **32 → 7 independently reproduces hq_P's "29 executed pages → ~6"** with a different toolchain and three
days of tree drift. The item's premise stands on its own feet; nobody needs to re-litigate it.

## 2. ⭐⭐ WHAT THE NEXT PASS SHOULD ACT ON: the order file is scoped to a third of its lever

seat03's own scope correction says `libscrip_rt.so` is **the whole compiler**, not just the runtime — and the
measurement makes that concrete. On a program that does nothing, **480 `.so` functions execute, spanning 237
pages against a perfect-cluster floor of 144.** The 77 RT functions are **32 of those 237 pages**.

⛔ So an order file clustering "the 65 startup-executed RT functions" — the item as written — reaches **32 of
237 pages**, while the same mechanism, zero extra code, applied to the executed set reaches all of it. The
ceiling is **~93 pages** rather than ~25. The RT framing is inherited from the *rewrite* lever (item 2/4,
where "is it RT?" decides whether you may hand-port it) and was carried into the *ordering* lever, where it
does not apply: the linker does not care which subtree a function came from.

## 3. ⛔ Pages are not faults, and this row has already been bitten once by exactly that

Pages-spanned is a **structural upper bound**: Linux fault-around maps up to 16 pages per fault, and a
function executing does not mean all of its bytes were. **Faults/RSS remains the graded metric** — this is
seat01's own lesson from the blob rung one entry earlier in this ledger, where relocations moved −14.26% and
faults moved −0.78%. **Do not quote a page delta as a fault delta**, including the 93 above.

Measured m3 do-nothing floor, this tree, 5 runs: **minflt 743.6** (743/744/744/744/743), maxrss 8976–9104 kB
— matching seat01's post-blob 742.2.

⚠️ **A near-miss worth recording:** the executed set spans **237 pages** and this row's `## QA` quotes a
do-nothing floor of **~237 faults**. They look like the same number and are not — the QA figure is the **m4**
arm; every number here is **m3**. I had a tidy causal story (each executed text page costs one fault, so
ordering buys ~93) and it is wrong. One `/usr/bin/time -v` run killed it. **A coincidence that confirms your
hypothesis is the most expensive kind, and mode is a unit** — the eighth/ninth-batch unit-mismatch clause
wearing another costume.

## 4. ⛔ Two callgrind parsing traps that each yield a PLAUSIBLE WRONG LIST

`perf` is non-functional in this container (exists, `linux-tools` reports Installed, ships no binary for
6.17.0-1032-oem, `perf record` exits 2) — same substitution to callgrind seat03 made, same reason.

1. **Name-compression namespace is per ENTITY KIND, not per keyword.** The spec prose says *"a separate ID
   mapping for each position specification"*, which reads as per-keyword — but the spec's **own example**
   defines ID 2 with `cfn=(2) func1` and then resolves it with `fn=(2)`. Call-side specs (`cfn`/`cfi`/`cob`)
   **define into the same table** the cost-side specs read. Keying by keyword silently drops every definition
   a call-side spec made: measured **741 of 753 rows came back `???` for object before the fix, 0 after**,
   and the executed-function count went 753 → 1343. A reader that "works" and is wrong by 44%.
2. **callgrind demangles C++; `nm` does not** (`nm -C`), and callgrind appends a recursion-context suffix
   (`fn'2`) naming the *same* function. Unfixed, both inflate "unresolved" and undercount the list.

⭐ Both were caught the same way — the output had a bucket (`???`) that was too big to be plausible. **A
parser's error bucket is an instrument reading in its own right**; a large one means the parser is wrong far
more often than the data is.
