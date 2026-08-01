# FINDING 2026-08-01c (s23e) — two demo artifacts froze on a duplicate label, and the graceful-skip is why nobody noticed

**Session:** s23e, OBJ-NOTE ladder (ON-1 + ON-3 restore side). **Found incidentally**, while using the committed
`.s` artifacts as a *pre-session baseline* to prove an annotation-only change had not moved any code.

---

## THE MEASUREMENT THAT SURFACED IT

The annotation work needed proof that it changed comments and nothing else. The cheap, broad instrument: compile
every corpus program fresh, strip trailing `#` comments from both sides, and diff against the **committed `.s`
artifact** — which, per the handoff protocol, IS the honest previous compiler output.

**163 of 165 programs were code-identical** (21 benchmarks + 20 demos + 122 pattern crosschecks). Exactly two
differed: `programs/snobol4/demo/json.s` and `programs/snobol4/demo/claws5.s`.

The diff was not subtle and not annotation-shaped:

```
committed:   mov qword ptr [rsp + 2480], rax     <- whole-graph carve coordinates
fresh:       sub rsp, 16                          <- per-BB claim (THE MODEL)
             mov qword ptr [rsp + 0], rax
committed json.s = 29864 lines | fresh json = 55854 lines
```

That is the **pre-CARVE-ERAD world**. `git log` confirmed it: `json.s` last moved at **s22z** (`8b184f84`), while
`roman.s` beside it is current at s23d (`cae1e083`). The artifacts had been frozen across the entire
CARVE-DATA-ERAD transition and everything after.

## THE ROOT CAUSE — NOT THE SCRIPT'S FILE LIST, AND NOT A SIZE CEILING

Both were plausible and both are WRONG; I checked each before believing either:

- **Not the list.** `util_regen_demo_s_artifacts.sh`'s `DEMOS` names `json` and `claws5` explicitly.
- **Not the size ceiling.** The script's own header calls json "the standing ceiling ~18k" — but that comment
  documents an *intent*, not a gate; there is no line-count test in the loop at all.

The actual arm that fires is the **assembler-rejected graceful-skip**:

```
json.sno    --compile rc=0, 55854 lines   ->  gcc -c: Error: symbol `.Lbynamefnzd8'  is already defined (:34015)
claws5.sno  --compile rc=0, 14796 lines   ->  gcc -c: Error: symbol `.Lbynamefnzd83' is already defined (:10200)
```

`SKIP <f>.s — assembler-rejected (committed .s untouched)`. The compiler emits a **duplicate label** in the
byname-fn path, `as` refuses the file, and the script — **correctly, by its stated design** — leaves the old
committed bytes in place rather than committing a file that does not assemble.

This is the **BYNAMEFN-DUP-LABELS class**, already on the books:
`FINDING-2026-07-26-CLAUDE-SN4-BYNAMEFN-DUP-LABELS-BEAUTY-M4-NEVER-ASSEMBLABLE.md`. It is alive at HEAD and it
reaches further than beauty.

## ⭐ THE LESSON — A GRACEFUL-SKIP CONVERTS A LOUD FAILURE INTO A QUIET LIE

The skip behaviour is **right** and should not be changed: committing a non-assembling `.s` would be worse. But
the protocol's two halves have very different half-lives:

- *"an assembler-rejected `.s` is left untouched **and flagged**"* — the flag is one line of stdout in a
  ~20-line regen tail, in a session whose attention is elsewhere. It is printed and then it is gone.
- The **stale file persists forever**, and it does not look stale. It looks like an artifact. Anyone reading
  `json.s` to learn what the compiler emits — the exact use RULES.md sanctions artifacts for — reads the
  carve model that was deleted three sessions ago and believes it.

⛔ **This is the s26 F12/F13 lesson recurring through a different door.** That one was artifacts minted into the
WRONG TREE; this one is artifacts NOT minted in the right tree. Same consequence, and RULES.md already states the
remedy in one sentence: **"When you need to know what the compiler actually emits, sweep the COMPILER
(`scrip --compile`), never the artifacts."** s23e is the empirical case for why that sentence is load-bearing.

⭐ **The generalizable instrument:** a strip-comments diff of fresh compiler output against committed artifacts
is a cheap, whole-corpus staleness detector that costs one sweep and needs no oracle. It was reached for here to
prove an annotation change was inert; it incidentally found two lying artifacts and a live codegen defect. **Any
session making a provably-inert change gets this audit nearly free — take it.**

## STATUS / NEXT

- **Not fixed this session** — off-rung, and the fix is the dup-label defect, not the script.
- The two `.s` files remain stale at s22z **by design** until the emitter stops emitting a duplicate
  `.Lbynamefnzd*`. They must NOT be hand-refreshed; they cannot assemble.
- Candidate rung: run the BYNAMEFN-DUP-LABELS finding's analysis against `json`/`claws5` (uid suffix collision
  in the byname-fn label mint — `zd8` vs `zd83` suggests a prefix/suffix concatenation that is not injective).
- **Second, unrelated pre-existing defect logged the same session:** `demo/roman.sno` emits empty numerals at
  HEAD (oracle `1 -> I`, SCRIP `1 -> `). Proven to predate s23e by assembling and running the pre-change `.s`.
  Monitor-first applies; not chased.
