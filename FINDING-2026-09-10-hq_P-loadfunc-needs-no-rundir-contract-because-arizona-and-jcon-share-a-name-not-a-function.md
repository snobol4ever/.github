# `loadfunc` needs no run-directory contract: Arizona and jcon share the NAME, not the function

**hq_P, 2026-09-10.** MODE `NONET`, lane *"hq_P the fed refs and the rundir contract for io/recent/loadfunc with the coo"* (CEO-532).
This closes the third name in that lane. SCRIP `7c57e09b2`, corpus `40d2f633f`. Oracle `/home/resources/icon-master/bin/icont` v9.5.25a.

## The answer, first

**`loadfunc` is already green and must NOT be given a run-directory contract.** Measured, not inferred:

| arm | result |
|---|---|
| SCRIP vs live Arizona, **stdout** | byte-identical (both 0 bytes) |
| SCRIP vs live Arizona, **stderr** | byte-identical (304 bytes) |
| `corpus/packages/icon/jcon_tests/loadfunc.std` vs live Arizona (combined, as the suite grades it) | **identical** |
| SCRIP starved (no `load1.icn`/`load2.icn`) vs fed | **byte-identical, 304 bytes** |

The last row is the one that decides the lane question. A contract declared here would be **inert**, and
`test_gate_icn_rundir_contract.sh` ARM 3 — the killswitch that requires the starved answer to *differ* — would fail it on sight.
⭐ **That is the gate working as designed: it refuses to count a declaration as coverage merely because someone wrote one.**

## Why feeding it cannot help — and why the jcon `.std` was never reachable

jcon's `loadfunc()` loads **Java classes out of a `.zip`**, built by its own `loadfunc.sh` with `javac` and `jar`. Arizona's
`loadfunc()` loads a **C function out of a shared object**. ⛔ **They are two different functions wearing one name**, so
`loadfunc("load1.zip", "proc1a")` cannot succeed under Arizona no matter what is staged beside it: `load1.icn` is Icon source, and
Arizona has no path from Icon source to a dynamically loadable procedure at all. The program therefore dies at line 22 in every
environment Arizona can reach, which is exactly what the re-cut `.std` records — ten lines of diagnostic and traceback.

`/home/resources/jcon-master/test/loadfunc.std` is the **76-line JVM answer**, and its reals give the oracle away without any
knowledge of the loader: `1/3 = 0.3333333333333333` is Java's `Double.toString`, where Icon prints `0.333333`. ⭐ **A ref can carry
its own provenance in a detail nobody chose deliberately** — the float formatting is a stronger tell than the loader semantics,
because nobody would have thought to fake it. The corpus copy has already been re-cut against Arizona (the sixteen-`.std` re-cut,
`5951c0703`), which is why it is 10 lines and not 76.

## The two cures that got it here, both already landed

`b7a73a87a` (loadfunc names the library that would not load, on stderr, before it raises 216) and `d99bce69b` (the traceback frame
images the C strings it converted its arguments to). The ceo's 17:27 census on `4a4c8aa6a` lists `jcon … loadfunc 4` and assigns
hq_S *"we print no `cannot open shared object file` diagnostic when the library is missing"* — **that row is cured; the census
predates the cure.** The residual `\x00`-bearing traceback the coo flagged (*"a jcon-cut .std with NUL-terminated strings"*) is not
a defect either: **Arizona prints those NULs too**, `loadfunc("load1.zip\x00","proc1a\x00")`, because it images the C strings it
converted its arguments into, and SCRIP now matches it byte for byte.

## The lane clause this belongs to

Same family as the io ref, from the far end: **the wrong oracle**. There the two arms were both correct about different questions
and disagreed on 9 lines. Here they would disagree on all 76, and the tell is a float format. ⭐ **The generalisation worth keeping
is about the CURE, not the symptom: "feed the witness its environment" is the right move only where the environment is reachable.
For io and recent it was, and feeding them turned 133→135 and 313→443 lines with a real defect hiding in the difference. For
loadfunc there is no environment to feed, and a contract written anyway would have looked like coverage while proving nothing** —
which is the starvation defect wearing the cure's clothes, the exact thing `lib_icn_rundir.sh`'s header warns about.

⛔ **So the correct state for `loadfunc` is: no `.argv`, no `.fixtures/`, no `.env`, no line in `contract_floor()`, and no row in
this lane.** Recorded here so the next reader does not re-open it as an unfinished third name.
