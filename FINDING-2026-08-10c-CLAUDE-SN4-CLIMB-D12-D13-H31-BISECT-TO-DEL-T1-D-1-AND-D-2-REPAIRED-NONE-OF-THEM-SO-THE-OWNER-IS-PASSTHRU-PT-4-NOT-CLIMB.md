# FINDING 2026-08-10c (CLIMB s37, Claude Opus 5) — D12/D13/H31 bisect to `1af93e3a` (DEL-T1 D-1); D-2 `1f96143c` repaired NONE of them; the owner is `GOAL-PASSTHRU-RBP-ERAD` PT-4, NOT CLIMB

**Goal:** `GOAL-SN4-ZETA-CLIMB` · **Container:** fresh · **No code changed this session.** SCRIP and corpus trees untouched and clean at `a5533659` / `f728c278`; only this file + the CLIMB cursor.

## ⛔⭐ CORRECTION APPLIED AT THE END-OF-SESSION REBASE — READ THIS FIRST, IT DEMOTES MOST OF WHAT FOLLOWS

`git pull --rebase` at close pulled `f2b6ea0e` (**MECH s36d**), which landed to origin *while this session ran*. It voids or supersedes four of this finding's claims. Recording them rather than quietly editing them out, per the concurrency protocol ("resolved BY THE REBASING SESSION and NOTED — never silently dominated"), and because a finding that overstates its own novelty is worse than no finding:

1. **⛔ THE BISECT WAS UNNECESSARY WORK.** MECH s36 states verbatim: *"DO NOT RUN s35's BISECT — IT IS VOID … The DEL-T1 trio (`1af93e3a` D-1 · `1f96143c` D-2 · `ef8a3052` D-3) was already convicted by two parallel seats on 08-10b."* Two seats had convicted these commits before I started. **~50 minutes of 1-CPU builds bought a re-derivation of a known result.** The information was partly reachable before I began: I opened FINDING-2026-08-10b *after* launching the bisect, and its hash-correction table names the trio outright. **Lesson for the next seat: grep the FINDING set for the suspect range BEFORE spending builds — orientation is not just the goal file.**
2. **⛔ "A FOURTH, PREVIOUSLY UNCOUNTED CASUALTY SET" IS FALSE — RETRACTED.** MECH s36's re-proved watermark is m3 **133/15/0/3** · m4 **132/16/0/3** with *"REGRESSION set D12·D13·H31 both modes"* — that watermark **is** the `corpus/probe/bb` suite. These three were already counted, by MECH, in this very suite, and MECH additionally measured **m4**, which this session did not.
3. **⛔ THE MECHANISM CLAIM IS SUPERSEDED.** This finding leaned on PASSTHRU PT-3's *"recursive/sealed-DEFER stays DEFER"* carve-out. Lon's s36c/s36d ruling states **"nothing special about `*name` DEFER"**, and MECH named the root cause **from source at HEAD**: the process-global mirror `g_blob_ctx[5]` (`pattern_match.c:624`) — every reader re-bases off the GLOBAL instead of its own already-correct per-activation cell. That is a real root cause; "it kept its blob" is only a symptom description.
4. **⛔ THE OWNER IS MECH M-1b, NOT PASSTHRU PT-4.** MECH holds it as GLOBAL-EXECUTE: `g_blob_ctx` **deleted, not bracketed**; blob header layer deleted, not rethreaded; per-box wires in per-box cells, pop-scan drain, record-carried β, statement-frame scan state. The cross-request below should be read as addressed to **MECH M-1b**.

**⭐ MECH ALSO FALSIFIES A CLAIM I WOULD HAVE MADE NEXT:** *"every blob-bearing program fails"* is false — D10 (18 `proc_PAT` defs, 6 `g_blob_ctx` refs) and D11 **pass in both modes**. The discriminator is **re-entry**, not blob count or capture (witness `W3_selfrec`: one stored pattern, same 6-ref footprint as passing D10, hangs because it re-enters). This fits D12/D13 exactly — recursive `*LIST` is re-entrant by construction — and is the better frame for them than anything below.

### What actually survives from this session

- The **parent-vs-convicted A/B on all three probes** (`930539c0` all rc=0 and oracle-matching → `1af93e3a` all rc=139 empty). Independent, same-container, and it pins all three to **one** commit — MECH convicted the trio of commits, but this is the clean single-commit A/B for these three specific witnesses, and it shows they are one cause rather than three defects.
- The **blind D-2 datum**: `1f96143c` was tested without knowing what it was and measured FAIL. Corroborative of "0 REPAIRED", now unsurprising.
- The **method note** at the end (setsid reaping, `pgrep` self-match) — container-level, unaffected by any of the above, and it cost real time to learn.

Everything between here and "METHOD NOTE" should be read through these four corrections.

## THE CLAIM THIS FALSIFIES

The s36 CLIMB cursor recorded:

> **⚠️ INHERITED REGRESSIONS — NEED AN OWNER:** D12 · D13 · H31 … Introduced between `6ffa57fe` and `c7e085fd` by a parallel seat. Not diagnosed here — left for the seat that introduced them or MECH to own.

and its GUIDANCE ruled them **"the highest-priority blocker before C-9 can be closed."**

Both halves are now falsified as framed. They are not an unowned mystery, and they are not a CLIMB blocker: they are the **documented, owner-directed, deliberate** breakage of `GOAL-PASSTHRU-RBP-ERAD` LADDER PT, whose fix-forward (PT-4) is open and is structural — the exact class the CLIMB charter forbids this ladder from landing.

## WHAT WAS MEASURED (all same-container, every arm built here, 1 CPU)

Endpoints verified **before** trusting the inherited cursor — the bisect driver tested both ends and would have aborted on a bad endpoint:

| rev | D12 | verdict |
|---|---|---|
| `6ffa57fe` (s34 watermark, claimed good) | rc=0 `=S` | **good — cursor confirmed** |
| `c7e085fd` (claimed bad) | rc=139 empty | **bad — cursor confirmed** |

`git bisect run` over the 33-commit range, one probe (D12), incremental builds:

```
[cff2a6b4] D12 PASS rc=0   -> good
[7b4d310d] D12 PASS rc=0   -> good
[1f96143c] D12 FAIL rc=139 -> bad
[930539c0] D12 PASS rc=0   -> good
[1af93e3a] D12 FAIL rc=139 -> bad
1af93e3af4655af48183cf28e7dd8a6f8e93a7fc is the first bad commit
```

**All three probes then confirmed against the convicted commit and its parent** (not just the bisect probe):

| rev | D12 | D13 | H31 |
|---|---|---|---|
| `930539c0` (parent) | rc=0 `=S` ✅ | rc=0 `=F` ✅ | rc=0 `k=age s= n=42 b=` ✅ |
| `1af93e3a` (D-1) | **rc=139 empty** | **rc=139 empty** | **rc=139 empty** |

One commit, one cause, all three — they are not three defects.

## THE CONVICTED COMMIT NAMES ITS OWN BREAKAGE

`1af93e3a` — *"DEL-T1 D-1: DELETE the BLOB-GRANT frame establishment for PAT$ blobs (Lon directive s9, 2026-08-10)"* — 1 file, 1 insertion / 23 deletions, `src/emitter/emit.cpp`. Its own message:

> **THIS COMMIT IS DELIBERATELY BREAKING** (delete-first by owner direction; DEL-T1 ladder, GOAL-PASSTHRU-RBP-ERAD). Dangling consumers = the D-2 worklist: scanhit/scanfail rbp# reads + retry whack · β res-stub pop rbp · CLASS D γ {res,rbp} record + wire reads · CLASS D ω absolute unwind · all interior `[rbp+N]` value-region readers (rbp now = invoker's frame, adopted). **Every pattern program routing through a surviving PAT$ blob is expected broken until D-2.**

D12/D13/H31 are exactly that: programs routing through a **surviving** PAT$ blob. `GOAL-PASSTHRU-RBP-ERAD` PT-3 states the carve-out verbatim — *"recursive/sealed-DEFER stays DEFER → MECH M-2(a) FRAMED variant"* — so a recursive `*name` reference is by design NOT inlined and keeps its blob. D12 and D13 are recursive patterns via `*LIST`; H31 chains pattern variables under FENCE. Their blobs survived PT-1/PT-2/PT-3 and then lost their frame at D-1.

## ⭐ THE LOAD-BEARING NEW DATUM: D-2 IS IN MY BISECT LOG, AND IT IS STILL RED

Per FINDING-2026-08-10b's hash-correction table, `1f96143c` is **"DEL-T1 D-2: PASS-THRU glue for PAT$ blobs — rbp-free activation via `g_blob_ctx`"** — the very commit advertised by D-1 as the repair.

My bisect tested `1f96143c` independently, without knowing what it was, and measured **D12 FAIL rc=139**.

That is a mechanical, blind corroboration of FINDING-2026-08-10b's headline — **"BY SET … 29 BROKEN / 0 REPAIRED"** — on a probe family that FINDING never measured. 2026-08-10b measured `crosscheck/patterns` and the `pt_/ab_/z4_` witnesses; it names neither D12, D13, nor H31. The CLIMB `corpus/probe/bb` suite is a **fourth, previously uncounted** casualty set of the same delete.

**Corollary for the PASSTHRU seat:** the "0 REPAIRED" result is not an artifact of the crosscheck corpus. D-2's `g_blob_ctx` pass-thru activation leaves the recursive-DEFER blob class dead in exactly the same way as the delete did — same rc, same empty stdout, no partial output.

## WHY CLIMB MUST NOT FIX THIS

The CLIMB charter, verbatim: *"MECH owns structural edits; this ladder NEVER lands a new frame/glue/claim protocol — it files the cross-request and blocks the rung on MECH's cursor."* The repair is `GOAL-PASSTHRU-RBP-ERAD` **PT-4 · SURVIVING-BLOB PASS-THRU PROTOCOL** (open, `[ ]`), which is precisely a new frame/glue/linkage protocol — box-own linkage CELL on the spine, CLASS D record `{res,rbp}`→`{res,pad}`, scanfail losing `mov rsp,rbp`, ω absolute unwind deleted — and it carries its own **PREREQ: coordinate with MECH, single authority; Lon routes.**

**⛔ DO NOT REVERT `1af93e3a`.** The delete was owner-directed, is a named ladder rung, and reserves its own revert path to its owner. A CLIMB revert would silently dominate a deliberate structural landing — the `zd_zdh`/`_xh_zdh` lesson.

## CONSEQUENCE FOR THE CLIMB LADDER

C-9's residuals (061 variable-arg POS, `test_string`, `test_case` rc=134, TAB-binds-subject per manual p.143 #10) are **independent** of these three and were never gated on them. s36's ruling that the 3R are "the highest-priority blocker before C-9 can be closed" should be retired: CLIMB cannot clear them, and waiting on them idles the ladder behind another seat's open rung.

**⛔ OPEN QUESTION FOR LON (not actionable by this seat):** RULES.md forbids adding to XFAIL *"except a Lon-ruled park."* D12/D13/H31 — and the other 26+ of the by-set — are known-broken-by-direction until PT-4. Absent a ruling they sit as permanent red in every concurrent seat's watermark, which corrodes the watermark's value as shared state: a seat that lands a real regression cannot see it against a red background. Request: rule whether the DEL-T1 casualty set is a **park** (XFAIL with a `DEL-T1/PT-4` reason tag, removed in the same commit as PT-4) or stays red as visible debt.

## METHOD NOTE (what actually cost the time, for the next seat)

Container has **1 CPU**; a full SCRIP build is ~9 min, incremental ~3–4 min. Two things mattered:

1. **Background jobs are reaped between tool calls** unless started under `setsid`. A plain `nohup … &` build died silently at 102/256 objects and left no error in the log — it looks exactly like a stalled compile. Use `setsid nohup … < /dev/null &`.
2. **`pgrep -f 'make|cc1'` self-matches the invoking shell**, so it reports the build alive after it is dead. Poll on artifacts (object count, binary mtime) or `pgrep -c cc1plus`, never on a pattern that appears in your own command line.

The whole bisect was run as one detached driver script with endpoint pre-verification, polled from outside — 8 builds unattended. That is the shape to reuse.

## STATUS

No code changed. Trees clean: SCRIP `a5533659`, corpus `f728c278`, both rebuilt and left at HEAD. Cross-request filed in the CLIMB cursor against `GOAL-PASSTHRU-RBP-ERAD` PT-4.
