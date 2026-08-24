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

## OPEN QUESTIONS FOR LON (answers land here as ruled)

1. Announcement headline: org debut / SCRIP-centric / milestone-centric? (Story suggests: ORG debut told AS the story.)
2. Language labels: SNOBOL4 "complete, self-hosting" · Icon "in active development" · Prolog "experimental" — confirm.
3. Numbers in public: current ruled-axis set, or none until a demo clears 2x? And is "20x faster" (dotnet) measured on a stated axis?
4. SCRIP README archaeology → docs/ file or drop (git keeps it)?
5. Chronology check: Byrd-box rediscovery (2025) vs Jeff's call (March 2026) vs the two-day/one-day finishes — exact order for print.
6. Does the announcement name Claude/Anthropic ("that is when I really met you for real") — public credit is Lon's call.
7. Jeffrey Cooper: preferred name/credit form, and does he review the dotnet text before it posts?
