# ANNOUNCE-DRAFT — 2026-08-24 announcement to SNOBOL4 groups.io + SNOBOL4/Icon Discourse

**Working file, CEO + Lon directly (s267). The story below is Lon's, verbatim in substance, captured 2026-08-23 evening. This file feeds the org README, the three repo READMEs, and the announcement text.**

## THE STRATEGY (Lon's words, the ordering principle)

- **Do NOT steal the limelight from Jeffrey Cooper's lifelong work on snobol4dotnet.** The announcement honors snobol4dotnet as JEFF'S project first. Lon's contribution: made it run 20x faster with Claude Sonnet 4.6 (⛔ number needs ruled-axis verification before print).
- **Make the Clojure implementation SHINE** — snobol4jvm: the entire SNOBOL4 in ~1,000 lines of Clojure.
- **x86 (SCRIP) closes the gap** — "runs almost everywhere."
- **JavaScript is very important next** — web presence is the reason.

## THE STORY (the narrative spine)

1. **Jeff's life's work:** SNOBOL4 in C# — snobol4dotnet. A lifelong project.
2. **Lon's Clojure S4** — abandoned at ~600 lines of "amazing code" until **Jeff called in early March 2026** and brought Lon back. Finished form: the ENTIRE SNOBOL4 in ~1,000 lines of Clojure.
3. **The Byrd-box rediscovery** (2025): Lon rediscovered Todd Proebsting's paper on Byrd boxes (Byrd 1980 for Prolog; Proebsting 1996 for goal-directed codegen). With that model: **snobol4dotnet finished in TWO DAYS, snobol4jvm in ONE DAY.** "A light bulb went off — that is when I really met Claude for real."
4. **The cascade:** why not write SNOBOL4 *in* SNOBOL4 (→ beauty, the self-host) → Snocone, because raw S4 syntax "is so ugly" → the realization that **Icon and Prolog are GDE and BB** — the same machine → cross-language calling → language code-switching. Not all implemented yet: the SCRIP cross-language compile + cross-language runtime is the vision.
5. **The dream, stated:** "Jeff and my life's dream of writing a SNOBOL4 compiler. And a platform for all my favorite languages."

**STORY MATERIAL (Lon s268, in-chat, verbatim in substance — the runtime-compilation thread):** *"We will allow ALL languages to have their own version of CODE and EVAL"* — Icon and Snocone for sure, Prolog's assertz already is it — which is why compiled programs link ONE library carrying the whole compiler; and the future shrink is self-hosted Snocone parsers + templates dynamically loaded via `*(EXPRESSION)`: *"How funny that a string value in the language will hold asm code that can run direct on the CPU. Kind of cool."* (Candidate closing beat for THE STORY: SNOBOL4's 1962 run-time code generation, EVAL/CODE, carried to native x86 across every language in one compiland.)

## ⭐⭐ THE SCOPE, RULED (Lon s267, in-chat, verbatim in substance — THE product definition)
*"SCRIP is SEVEN LANGUAGES on FIVE PLATFORMS such that they can call each other and even co-exist in the same TRANSLATION UNIT, compiland."* Languages: SNOBOL4 · Snocone · Icon · Prolog · Rebus · Raku · Pascal. Platforms: x86-64 · JVM · .NET · JavaScript · WebAssembly. The polyglot `.scrip` demos (fenced per-language sections, one document) and the `family_net` cross-language linkage demo (SNOBOL4 parses → Prolog infers → Icon formats, real EXPORT/IMPORT) are the scope made visible.

## THE ARC FOR THE READMEs (ruled by Lon s267, correcting CEO's first frame)

- **Then:** ALL backends + many frontends ALMOST COMPLETELY running — 120,000+ lines of duplicated, unmaintainable code. Capability proven; cost fatal.
- **Now:** one engine — one IR, Byrd boxes, template discipline (every instruction through one encoder). x86-64 native, complete, self-hosting. The consolidation WAS the work.
- **Next, NEAR-TERM (weeks):** .NET MSIL · JVM bytecode · JavaScript · WebAssembly return as TEMPLATE ENCODERS modeled on the existing x86 BB set, old emitters as architecture reference (`src/backends/` dormant in-tree + git history), developed SIMULTANEOUSLY under the CEO/HQ/FLEET method.

## PER-DOCUMENT CENTER OF GRAVITY

| document | leads with |
|---|---|
| org README | THE STORY — the people (Griswold→Emmer→Shields→Wills→Budne→Cooper), then the discovery, then the three implementations |
| snobol4dotnet README | JEFF — his lifelong project; Lon's speedup contribution second |
| snobol4jvm README | the ~1,000-line Clojure elegance |
| SCRIP README | the platform: one engine, five frontends, x86-64 today, four backends near-term, the cross-language vision |

## OPEN QUESTIONS FOR LON — ✅ ALL SEVEN RULED 2026-08-29 (in-chat via ceo structured asks; answers inline below)

1. ✅ RULED (Lon 2026-08-29): **ORG DEBUT, TOLD AS THE STORY** — the narrative carries it; SCRIP and milestones appear as chapters.
2. ✅ RULED (Lon 2026-08-29, verbatim in substance): **SNOBOL4 is NOT "self-hosting" — no bootstrap claim.** The true public claims: it BEAUTIFIES ITS OWN SOURCE, and the language parsers are written in Snocone (parser_*.sc). Label: "complete" with those two facts. Icon "in active development" and Prolog "experimental" stand unobjected. ⛔ STYLE LAW for the whole piece: NO internal vocabulary in external-facing text — no "rungs", boards, seats, batons; public words only.
3. ✅ RULED (Lon 2026-08-29, verbatim in substance): **the snobol4ever (org) README ships WITHOUT speed details; SCRIP's README carries the benchmark results.** Numbers live in the technical README under the ruled multiple-axis law (named reference, x-multiples); the unstated-axis "20x" dotnet claim does not enter the org piece.
4. ✅ RULED (Lon 2026-08-29): **DROP IT** — the stale build-section history is deleted from the README; git history keeps it.
5. ✅ RULED (Lon 2026-08-29): **order confirmed for print** — Byrd-box rediscovery (2025) → Jeff's call (March 2026) → the rapid language finishes (2026).
6. ✅ RULED (Lon 2026-08-29, verbatim in substance): **name CLAUDE but NOT Anthropic — credit by model names: Claude Sonnet, Claude Opus, and Claude Fable.**
7. ✅ RULED (Lon 2026-08-29): **"Jeff Cooper"** in print, **and he reviews the dotnet passage before it posts.**
