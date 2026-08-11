
## 8. ⭐ INTERIOR-FREE AUDIT — FIRST PASS (s20 close, PARTIAL, static census only)

s19 CORRECTION 4 asks whether any interior box carves without releasing on its fail path (residue accumulating per retry with nothing reclaiming it) — named a live suspect for part of the residual. First-pass static census over `src/templates/bb_*.cpp`, carve (`sub rsp`) vs release (`add rsp` / `mov rsp` / `leave`):

- `bb_match_arbno.cpp` **9 carve / 9 add-release** — count-balanced.
- Asymmetric (carve>0, `add rsp`==0): `bb_func_activate.cpp` · `bb_glue_framed.cpp` · `bb_match_begin.cpp`. ⭐ **All three are LICENSED KEEPERS** (FUNCTION activation frame · FRAMED glue, the only RBP writer · MATCH_BEGIN statement head) and they release by a different spelling — `bb_match_begin` shows 5 `mov rsp`/`leave` hits the crude `add rsp` grep cannot see.

**⇒ No unlicensed interior carve-without-release was found.** ⛔ **THIS DOES NOT CLEAR THE HYPOTHESIS.** Count-balance is not path-balance: a box can carve and release in equal static counts while a *fail* path skips its release, which is exactly what CORRECTION 4 asks and exactly what a count cannot answer. And this is a census of TEMPLATE SOURCE, blind to releases emitted through shared helpers or the `x86()` dispatch, and blind to emitted code.

**What it buys:** the suspicion moves off "a box that never releases" and onto "a box whose FAIL path skips a release it does perform on the success path." The next seat should walk the ARBNO fail edge specifically (9/9 balanced, in-blob top-level ARBNO is already this file's named surviving clobberer) rather than re-running a census. Suggested instrument: emit-time assertion that entry rsp == exit rsp on the ω edge, or a bounded-iteration probe on `114` watching rsp drift per retry — a drift of one carve width per iteration would convict it outright.
