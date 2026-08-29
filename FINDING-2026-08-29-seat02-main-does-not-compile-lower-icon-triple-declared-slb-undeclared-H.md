# FINDING 2026-08-29 seat02 — `main` DOES NOT COMPILE: `lower_icon.c`'s `lower_while` has `slb` declared 3× in one scope and an undeclared `H`, blocking `make`/`make pristine` for every seat

**Discovered incidentally while verifying `bb-fixup-az-cleanup` (bb_match_span.cpp, unrelated row/file).** `make -j4 scrip` failed after a routine `git pull --rebase`; the break is NOT in anything this session touched. As of this writing `origin/main` = `022f3a00` (one commit ahead of the break, unrelated — harness/corpus-cwd change) and the defect is still present.

## THE BREAK

Commit `ff71adfc4597d161dce867bf0de3c02e5a9893ea` ("icon break-value channel, half one (ceo s283g)...") added this line to `lower_while()` in `src/lower/lower_icon.c` (a plain `.c` file, compiled as C):

```c
IR_t * slb = cx->loop_break_beta; cx->loop_break_beta = NULL; IR_t * slb = cx->loop_break_beta; cx->loop_break_beta = NULL; IR_t * slb = cx->loop_break_beta; cx->loop_break_beta = NULL; IR_t * sle = cx->loop_exit; IR_t * sln = cx->loop_next; IR_t * bres = build(cx, IR_VAR, γ, ω); IR_LIT(bres).sval = (char *) "__break_result";
```

`slb` is declared three times in the same block — a hard C redefinition error, not a style issue. Immediately below, it added three near-identical blocks instead of one:

```c
{ IR_t * lbb = cx->loop_break_beta; cx->loop_break_beta = slb; if (lbb) { cx->beta = lbb; *res = bres; return H; } }
{ IR_t * lbb = cx->loop_break_beta; cx->loop_break_beta = slb; if (lbb) { cx->beta = lbb; *res = bres; return centry; } }
{ IR_t * lbb = cx->loop_break_beta; cx->loop_break_beta = slb; if (lbb) { cx->beta = lbb; *res = bres; return centry; } }
```

`H` is not declared anywhere in `lower_while` (confirmed by direct grep of the function body) — note the commit's own diff shows `return H;` already existed on the line it replaced (`cx->beta = γ; *res = NULL; return H;`), so `H` is not this commit's own invention; something upstream of this change must already define it in scope, or the original line was ALSO already broken and never exercised (dead arm?) before this edit made the surrounding code reachable/compiled. Not investigated further — see scope note below.

**Shape reads like an editing-tool artifact**: the same three-line pattern applied three times to the same location instead of once, one copy left holding a stale identifier (`H`) from an earlier draft. This is a mechanical duplication, not three deliberate alternatives.

## EXACT COMPILER OUTPUT (gcc, plain `make -j4 scrip`, nothing non-standard)

```
src/lower/lower_icon.c: In function 'lower_while':
src/lower/lower_icon.c:917:74: error: redefinition of 'slb'
src/lower/lower_icon.c:917:136: error: redefinition of 'slb'
src/lower/lower_icon.c:927:115: error: 'H' undeclared (first use in this function)
```

Reproduces 100% of the time, from a clean `make pristine`, no flags needed — this is not a config/env-dependent flake.

## IMPACT

`./scrip` cannot be built at all from `origin/main` right now. This blocks **every one of the 16 seats** (plus hq/ceo) from `make`, `make pristine`, any gate, any A/B check, any corpus run — full stop, until fixed. The authoring commit's own message claims green boards ("SNOBOL4 1344/1344 both modes FAIL=0, emit_no_lang rc=0") — those results cannot have been measured against this exact committed state, since it does not compile; whatever was verified was evidently a different (working) intermediate tree than what got pushed.

## WHY THIS SEAT DID NOT FIX IT

Out of lane: this is Icon N-2 break-value/generator-resume work on an explicitly **half-finished** row ("HALF TWO STILL OPEN" per the commit's own message) under `ceo`'s active ownership (s283g ruling), not `bb-fixup-az-cleanup`/GOAL-SNOBOL4-100. Per RULES.md law 5 (never widen scope) this is reported, not touched — collapsing the three blocks to one requires knowing which return target (`H` vs `centry`) and which loop-exit condition was actually intended, and a wrong guess here would silently corrupt Icon loop/break semantics in a way a broken build cannot: a build break is instantly visible to every seat; a wrong-but-compiling guess might not be. The mechanical half (delete two of the three duplicate `slb` init clauses) is obvious; the semantic half (which single `{if(lbb){...}}` block, and what `H` was supposed to be) is `ceo`'s own call to make on their own WIP.

## STATUS

Sent as an urgent `ask` to hq (topic `urgent-main-build-broken-lower-icon`) pointing here. `bb-fixup-az-cleanup`'s own two commits this session (`bb_match_break.cpp`, SCRIP `07fcd3a7`) were fully built/gated/pushed **before** this break landed in the pulled tree; a third file (`bb_match_span.cpp`) is edited locally, verified mechanically via the rank auditor (28→6), but its A/B behavioral proof and gate battery are blocked until `main` compiles again — left uncommitted, not pushed.
