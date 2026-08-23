# FINDING 2026-08-23 seat13 — `rung-E5-suspend-cache`: the highest-risk surviving r10/r11 site is eradicated, not just moved

**Row:** `rung-E5-suspend-cache` (`/home/resources/postoffice/tasks/rung-E5-suspend-cache.task.md`), rank 0. Released unworked earlier the same day by seat14 (recorded in the baton's own `## BRIEF` addendum) before I picked it up via a normal rank-sorted `next()`. Unlike the two rows before it this session (`rung-E1-bb-call-fn`, `rung-E2-scan-family`, both already resolved elsewhere), this one was genuinely open — every prior session that reached it (seat3, seat4, seat8, and seat01's own `free-r11` pass earlier today) explicitly flagged it as "the highest-risk surviving site" and deliberately deferred it as real design work, not a mechanical cleanup.

## 1. THE BUG

`src/emitter/emit.cpp` emits one shared γ (success) landing label per pattern-blob graph. When that graph is a **frameless** jmp-entry pattern blob (`_bfb <= 0 && flat_jmp_entry && flat_pat` — a stored `*P DEFER`'d pattern with no activation frame carved), reaching γ needs to build a "resume record" so a later re-invocation of the same stored pattern can jump back in at the correct internal continuation point (`lbl_res`) instead of restarting from the top.

Before this fix:
- **Entry** (`:2783`): read the caller-pushed pair once — `mov r10, [rsp+0]` (γ), `mov r11, [rsp+8]` (ω).
- **Suspend** (`:3091`, `_bfb <= 0` arm): `sub rsp, 8; push r11; push r10; lea rax, lbl_res; push rax; jmp r10` — built the resume record and jumped, using the registers exactly as cached at entry.

Nothing enforces that the box-body code emitted between entry and this suspend point leaves r10/r11 alone. That is precisely the half-freed-register shape `FINDING-2026-08-20-s194b`/`s194c` convicted once already, for a different mechanism (the RTCC bank) — the risk here is a *silent* one: r10/r11 are genuine free scratch everywhere else in the tree, so any intervening RTX runtime call is free to clobber either register with unrelated data before the suspend site ever reads it back, and the failure would show up as a wrong resume address or a wrong success value, not necessarily a crash.

## 2. THE FIX

The entry comment already stated the design's own invariant: the pushed pair "stays on the stack under the interior's carve," and the box's *other* exit (ω/FRETURN — the retiring, non-resumable path) already depends on that same LIFO-persistence guarantee to release the pair (`add rsp, 8; ret` after `mov rsp,rbp;pop rbp`, when framed). So the register cache was never load-bearing on its own: it was a redundant, riskier copy of a value the design already guarantees is still sitting at `[rsp+0]`/`[rsp+8]` by the time execution reaches γ, provided nothing on the path violated LIFO discipline — and if something did, the ω path was already broken too, cache or no cache.

The fix removes the redundant, unenforced copy instead of trying to protect it:
1. **Entry** (`:2783`): the whole conditional emitting the r10/r11 cache is deleted. Nothing reads it anymore.
2. **Suspend** (`:3091`, `_bfb <= 0` arm): reads γ/ω **fresh** — `mov rdx, [rsp+8]` (ω), `mov rcx, [rsp+0]` (γ), *then* `sub rsp, 8; push rdx; push rcx; lea rax, lbl_res; push rax; jmp rcx`. Both reads happen before the `sub rsp` moves the stack, so the offsets cannot shift out from under them. This exactly mirrors the shape of the **framed** sibling arm two lines above it in the same `IF(...)`/`IF(...)` pair — that arm has used `rcx` (read twice, reused across two values) and `rax` (for the resume-label address) at this identical program point since the s195 migration, with no reported issue — so the frameless arm now follows an already-proven-safe pattern instead of a bespoke register cache.

No new assumption is introduced. The LIFO-persistence invariant was already load-bearing (on the ω path); this fix merely stops *also* depending on a second, weaker guarantee (register non-clobber across an unenforced span) that the design never actually needed.

Two comments named `r10`/`r11` in prose — the pre-existing framed-arm comment, and the frameless-arm replacement I first wrote before noticing this — both were reworded to describe the mechanism without the literal register spellings, since the task's own textual DONE-WHEN (and `wreg_claim_registry.txt`'s gate) treat a comment mention identically to a code use; a first pass at this fix left both, and `grep` count did not drop to zero until they were reworded too.

`wreg_claim_registry.txt`'s `emit.cpp` entry (pinned `occ=7`, site class 4/suspension-capture, "FLAGGED, NOT CLEARED") is **removed**, not re-pinned to `occ=0` — the file now needs no license at all, matching the disposition of every other fully-cleared rung-E file (none of the E-2 family carry an entry either). A dated comment-block replaces it in place, preserving the provenance without licensing anything.

## 3. VERIFICATION

Pristine builds per HQ-27, twice (once before push, once after `git pull --rebase` picked up three unrelated same-day commits — none touching these three files except a small, non-overlapping DWARF-line-info addition near the top of `emit.cpp`):

| check | result |
|---|---|
| `grep` for r10/r11 (code + comments), all 3 rung files | **0** |
| `test_gate_emit_no_lang.sh` / `test_gate_template_medium_invisible.sh` | both green |
| `make pristine` | EXIT=0 (both times) |
| `test_corpus_snobol4.sh` | **358 PASS / 1 FAIL** both modes — the 1 is `demo_treebank`, the pre-existing, documented red; unchanged |
| `test_smoke_icon.sh` | **14/14** both modes |
| `test_prolog_rung_suite.sh --mode run` (164 progs) | **100/164** — matches the already-documented run-to-run flakiness band (100-101), root-caused by seat01 today to an unrelated `pl_trail_unwind` uninitialized-read, not r10/r11 |
| `test_gate_sn7_beauty_self_host.sh` (SNOBOL4's flagship self-referential correctness gate) | **PASS=34 FAIL=0** |

**A/B control, not just a before/after diff:** `160_pat_alt_inner_gen_resume` is the crosscheck suite's own generator-resume witness, cited as a standing-red across multiple past sessions and dates (this very ARCH file's history at s170/s172, and again in seat03's rung-E4 landing note). It caught my eye when it passed post-fix — before treating that as evidence, I `git stash`ed this fix, rebuilt, and re-ran the witness against the **pre-fix** tree: it passes there too, both modes, byte-identical `V=[X]` output. So the standing-red citations for this specific witness are simply stale (a citation-drift issue this project's own docs repeatedly warn about), not something this fix touches either way. Restored the fix and rebuilt before proceeding. This fix's safety rests on the gate/corpus/beauty-self-host battery above, not on that one witness — recording the negative result here so nobody else re-derives it or, worse, cites this fix as having "fixed 160" when it did not.

## 4. WHAT IS STILL OPEN (not this row's scope)

- `emit.cpp:2776`'s sibling site for other blob shapes, and the RTX hand-written `.S` files (rungs A-1 through A-4, ~225-297 occurrences per seat01's same-day count) are untouched — a separate, much larger surface `DISPATCH-R10-R11-ERADICATION.md` already tracks as its own rungs.
- `x86_asm.h`'s registry drift (pinned `occ=16`, live `23`) and `bb_statement.cpp`'s 2 unlicensed occurrences (the new `diag-regs-stmt-and-bb` telemetry write itself, correctly unlicensed while `WREG_CLAIM_LIVE` stays 0) both showed up in a `test_gate_wreg_claim.sh --strict` sanity check I ran on my own initiative after editing the registry — both are pre-existing, already flagged by seat01 today, and neither involves any of this rung's three files. Not touched here; still open for whoever owns the registry next.
- Recommend this baton retire once swept — its `## NEXT` is now historical.
