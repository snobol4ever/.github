# FINDING 2026-08-30 hq_B — SEAT-CLAUDE.md carried two retired laws; 18 of 19 seat digests have a dead map

**Tree:** SCRIP `544e8fd6`+ · measured 2026-08-30, seat `hq_B`. Opened by seat15's non-blocking
doc-freshness flag on the lon-folder ban; the sync pass they suggested found the rest.

## Two retired laws in a named shared authority

`/home/resources/postoffice/SEAT-CLAUDE.md` is one of the CONFLICT RULE's named shared authorities — the
file a seat reads cold. Both of these were **law statements**, and they were wrong in *opposite directions*:

**1. Too restrictive — the `corpus/programs/lon/` ban (seat15's flag).** It said: never run, never compile,
never read into a transcript, possible live PATs. Lon retracted **all** of it in-chat to CEO on 2026-08-24
s269 (*"Remove all references to the lon folder being special. I retract all of it."*), then refined it on
2026-08-27. The directory does not even exist under that name any more — it is
`corpus/programs/lon_cherryholmes/`. RULES.md § ABSOLUTE RULES has carried the current text for six days and
says outright that *"a stale digest claiming the old off-limits law … loses to this line."*

**2. ⛔ Too permissive — the `-O2` recipe, and this one is worse.** The line read *"`-O2` is used ONLY for
benchmark/demo runs, passed explicitly"* **and printed the command**. RULES.md § FACT RULE — NO `-O2`
BUILDS. EVER. (Lon 2026-08-23 s262) supersedes exactly that half of O0-DEV-O2-BENCH, **quotes that exact
sentence to mark it dead**, and states the recipe is *"deliberately not reprinted."* SEAT-CLAUDE.md was
reprinting it.

⭐ **The asymmetry is the finding.** A too-restrictive stale rule costs a seat some work it was allowed to
do — annoying, self-limiting, and it surfaces the moment somebody wants the work. A too-permissive one is
followed successfully: a seat builds at `-O2`, waits ~9m30 per rebuild instead of ~1m40, produces a number
that RULES.md says may not be quoted, and nothing anywhere objects. **Only the second kind recruits you.**

## 18 of 19 seat digests carry a dead workspace map

`src/frontend/` does not exist. The directory was renamed **twice**: `src/parser/` → `src/frontend/`
(2026-08-24, `cf1f2961`) → **`src/parsers/`** (2026-08-29, `96665b70`, Lon in-chat). Counted across every
readable per-root digest:

```
claude, claude03..claude16, claude_B, claude_C, claude_P   -> 18 of 19 still say src/frontend/
```

⭐ **And there is a reason this rename in particular went unnoticed everywhere:** the *word* "frontend"
survived the rename on purpose — it still names the pipeline **stage** (7 frontends, per-frontend grading).
`96665b70`'s own message says so. So a grep for "frontend" keeps returning live, correct hits, and the dead
**path** hides among them. A rename that leaves its noun in service is much harder to sweep than one that
retires the word.

⛔ This is the second measured instance of the same decay: `FINDING-2026-08-23-hq_P-the-per-root-claude-md-
digest-is-not-git-tracked-and-15-of-19-were-stale.md` found **15 of 19** carrying retired law. My own
digest's banner cites that finding, in bold, *and my digest was one of the 18.* Being the file that warns
about the decay confers no immunity from it.

## What was changed

- **SEAT-CLAUDE.md**: both law paragraphs replaced. ⭐ Not with fresher copies — **with pointers**. The lon
  entry now says "do not restate the current rule here — read RULES.md § ABSOLUTE RULES", gives the
  one-line answer so a seat is not left guessing, and names why it is a pointer: *law that exists in one
  versioned file cannot go stale in nineteen unversioned ones*. A copy would simply decay again on the next
  amendment. Also `src/parser/` → `src/parsers/` (2 sites).
- **This root's `CLAUDE.md`**: repointed to `src/parsers/`, with the two-step rename chain recorded so the
  next reader can tell a dead path from the live concept. Every `src/` path it now asserts exists; the five
  that do not are in sentences explicitly saying they do not.

⛔ **Not changed: the other 18 digests.** They are other seats' roots. The fix in one root does not reach
them — which is the finding, not an oversight. This wants a broadcast, or better, whatever makes the
workspace map computed rather than transcribed (`ls -d src/*/` is one line and cannot go stale).
