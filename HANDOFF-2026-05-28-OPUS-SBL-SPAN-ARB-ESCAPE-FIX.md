# HANDOFF — SBL-SPAN-ARB-ESCAPE-FIX ✅

**Date:** 2026-05-28
**Author:** Opus 4.7
**Repo:** SCRIP
**Parent commit:** `55d03444` (M3-RK-NOINTERP-1a: bb_to_by.cpp MEDIUM_BINARY r12->rt_push_int prep)
**Goal:** GOAL-SNOBOL4-BB.md

---

## Summary

Mechanical escape-sequence fix to `bb_pat_span.cpp` and `bb_pat_arb.cpp` MEDIUM_BINARY arms. Every `bytes(N, "...")` literal used double-backslash escapes where the working templates use single. Every native SPAN run was segfaulting; every native ARB matching path was emitting nonsense bytes. Fix: `\\x` → `\x` in the MEDIUM_BINARY lambdas of both files. **Native broad corpus 187 → 195 (+8). Default broad corpus 246 → 250 (+4). Mode-4 compile 175 → 178 (+3). Zero regressions.**

---

## Diagnosis

Working from the previous-session handoff's "NEXT options (c) SBL-SPAN-2 / SBL-ARBNO-3 BINARY arms," I noticed the SPAN arm had already been written (current file shows 220 bytes, sites `{143, 168, 172, 192, 216}`, comments matching the bb_capture.cpp `std::deque<int>` slot pattern). Audit script classifies it REAL. But:

```
$ SCRIP_M3_NATIVE=1 ./scrip --run /tmp/simple_span.sno
Segmentation fault
```

gdb on a bare `X SPAN('0123456789')` test:

```
0x7ffff7400000: movabs $0xd7bc08,%r10           ; xa_flat_prologue (10 bytes)
0x7ffff740000a: cmp    $0x0,%esi               ; xa_flat_prologue (3 bytes)
0x7ffff740000d: jne    0x7ffff74000bf          ; xa_flat_prologue jne β (6 bytes, rel32 patched)
0x7ffff7400013: pop    %rsp                    ; ← SHOULD BE SPAN's "movabs rcx, z_slot" (48 B9)
0x7ffff7400014: js     0x7ffff73fffa6
0x7ffff7400016: xor    %edx,%ebx
=> 0x7ffff7400018: add    %al,(%rax)            ; SIGSEGV here
```

Raw bytes from `x/40bx 0x7ffff7400013`:

```
0x5c 0x78 0x90 0x33 0xda 0x00 0x00 0x00 0x00 0x00 0x5c 0x78 0x43 0x37 0x5c 0x78
```

SPAN's first instruction was supposed to be `48 B9 <8 bytes of z_slot ptr>` (movabs rcx, imm64). Instead the slab contained `5C 78 90 33 DA 00 00 00 00 00`. The `5C 78` is the byte sequence for `\` (ascii 0x5C) and `x` (ascii 0x78) — i.e. literal backslash-x characters from the source string.

Source examination, `bb_pat_span.cpp:40`:

```cpp
b += bytes(2,"\\x48\\xB9") + u64le(za);    /* [0]  movabs rcx, z_slot */
```

In a C string literal:
- `"\x48\xB9"` — escape sequences — 2 bytes: `0x48 0xB9` ✓
- `"\\x48\\xB9"` — `\\` is one backslash, `x` is one char — 8 chars total: `\ x 4 8 \ x B 9`

So `bytes(2, "\\x48\\xB9")` returns the first 2 chars of the 8-char string: `\` (0x5C) and `x` (0x78). The remaining 6 chars `48\xB9` are silently dropped (bytes() truncates to N). Every line in the SPAN MEDIUM_BINARY arm followed this same pattern, producing 100% nonsense bytes interleaved with the correctly-emitted `u32le`/`u64le` helper calls (which weren't affected because they don't take string literals).

Comparison with `bb_pat_any.cpp:61` (works natively):

```cpp
+ bytes(2, "\x48\xB9") + u64le(TEMPLATE_ADDR_SIGLEN)
```

Single-backslash form. Same pattern in bb_pat_pos.cpp, bb_pat_break.cpp, bb_capture.cpp — all single-backslash, all work.

`bb_pat_arb.cpp:32-48` had the identical double-backslash bug (the file's structure mirrors SPAN's `std::deque<int>` slot scheme).

## Why the audit didn't catch it

`scripts/audit_m3_native_binary_arms.sh` classifies arms by examining `bin.sites.push_back` / `bin.labels.push_back` activity in the source — substantive site registration → REAL. The audit can't tell whether the byte literals in the source produce the right bytes; the source compiles, the function returns a non-empty string, the bin has sites. Only runtime execution reveals the corruption, and the corruption manifests as SIGSEGV (not a "no match" failure) so it shows up in test PASS/FAIL deltas, not in any structural check.

## Fix

Two `str_replace` calls — one per file. The byte-layout comments and site numbers `{143, 168, 172, 192, 216}` (SPAN) and `{32, 36, 77, 85}` (ARB) are correct for the *intended* layout, so no offset arithmetic changes. Pure escape correction.

`src/emitter/BB_templates/bb_pat_span.cpp`: 45 substitutions, every `bytes(N, "\\x…")` → `bytes(N, "\x…")` in the MEDIUM_BINARY lambda (lines 40-87).

`src/emitter/BB_templates/bb_pat_arb.cpp`: 16 substitutions, same pattern (lines 32-48).

The MEDIUM_TEXT and JVM/JS/NET/WASM arms in both files were already correct — they use GAS/JVM/CIL assembler text strings, not raw bytes, so backslashes weren't a concern there.

## Validation

**Bare SPAN under native:**
```
$ SCRIP_M3_NATIVE=1 ./scrip --run /tmp/simple_span.sno
matched
$ SCRIP_M3_NATIVE=1 ./scrip --run test/snobol4/patterns/041_pat_span.sno
12345
```

**Newly passing native broad corpus (from `comm -23` of fail lists):**
- `041_pat_span` — direct SPAN
- `W05_span` — direct SPAN
- `063_pat_fence_fn_optional`, `064_pat_fence_fn_capture`, `065_pat_fence_fn_decimal`, `066_pat_fence_fn_nested` — FENCE templates internally use SPAN for cursor scanning; same multiplier effect as the POS-PATCH-OFFSET → 8 FENCE wins from yesterday
- `test_string`, `wordcount` — SPAN-based driver programs

**Newly passing default-mode broad corpus (4 net):** mostly the same SPAN-based programs that route through `bb_build_brokered` → BINARY arm even under `--interp` (as predecessor noted).

**Gates after fix (all hold):**
- G1: 13/13 default + 13/13 native
- G2: 39 (sibling-influenced, unchanged)
- G3 (mode-4 compile): 178/280 ← up from 175 (+3)
- G4 (default broad): 250/280 ← up from 246 (+4)
- G4 native (`SCRIP_M3_NATIVE=1`): 195/280 ← up from 187 (+8)
- Rungs: M2=19/M4=15 (unchanged — 052/053/054/056 still fail M4-compile, separate ARBNO-in-CAT issue)
- Prolog smoke 5/5, Raku smoke 5/5, Icon smoke 5/5, FACT clean, audit GATE OK
- Zero regressions in the diff of native fail lists (`comm -13` empty)

---

## Sibling bug — NOT fixed in this commit

The same `\\x` typo exists in 6 other template files, but in BOMB-style placeholder stubs that fall through `jmp γ; jmp ω` (never reached at runtime when the surrounding architecture is correctly wired). These produce no known crash today but should be cleaned up prophylactically:

| File | Line | Pattern |
|---|---|---|
| `bb_arbno.cpp` | 23 | `bytes(1,"\\xE9")+u32le(0)+bytes(1,"\\xE9")+u32le(0)` |
| `bb_binop_gen.cpp` | 120 | 3-jmp variant |
| `bb_pat_arb.cpp` (the `bomb_bytes` companion if any — already fixed in this commit) | n/a | done |
| `bb_pl_alt.cpp` | 23 | 2-jmp |
| `bb_pl_call.cpp` | 41 | 2-jmp |
| `bb_pl_choice.cpp` | 42 | 2-jmp |
| `bb_to.cpp` | 65 | 3-jmp |

Each currently emits `5C 78 ?? ?? ?? ?? 5C 78 ?? ?? ?? ??` (literal backslash-x + 4 zero bytes + same again) instead of `E9 ?? ?? ?? ?? E9 ?? ?? ?? ??`. If any of these paths becomes reachable in the future, it will SIGSEGV the same way SPAN did. One-line cleanup per file. Worth a separate small commit.

---

## Test methodology notes

- `test_interp_broad_corpus_and_beauty.sh` truncates FAILURES output to `head -40`. To diff failure lists between commits use `sed 's|head -40|head -400|'` copy and explicit `INTERP=$(pwd)/scrip` (because `$HERE` resolves to `/tmp` after the copy).
- `gdb -batch -x cmd.txt ./scrip` captures the crash site without an interactive session.
- `x/40bx <addr>` on the slab start = absolute byte dump — the only reliable way to confirm what the emitter actually produced when patcher conventions are suspect.

---

## What to do next

The currently-unchecked next step in `GOAL-SNOBOL4-BB.md` is **enable combinator flat-wire in mode-3**. With today's SPAN+ARB fix and yesterday's POS-PATCH-OFFSET, the BB template layer is much healthier. The `patnd_to_bb_tree` routing in `stmt_exec.c:362-374` is already live and rungs `050_pat_alt_two` / `055_pat_concat_seq` pass natively — combinator flat-wire is *partially* working already. The remaining gap is **nested-combinator eligibility**: `patnd_tree_eligible` rejects subtrees containing kinds it doesn't recognize. Broadening it (cautiously — predecessor noted gate expansion regressed 237→229 mode-2 last time it was tried naively) should be the next session's focus. Validate on `100_pat_fence_two_alts_first`, `124_pat_regex_keyword_seal`, `126_pat_json_number`.

Alternative quick wins:
- (b) prophylactic `\\x` → `\x` in the 7 BOMB-stub sites (above table)
- (c) extend `patnd_tree_eligible` for XARBN inside CAT (rungs 052/054 still empty native — segfault root cause gone, but matching logic still has a gap)

---

## Files touched

- `src/emitter/BB_templates/bb_pat_span.cpp` (+45/-45)
- `src/emitter/BB_templates/bb_pat_arb.cpp` (+16/-16)
- `.github/GOAL-SNOBOL4-BB.md` (one new `[x]` step)
- `.github/PLAN.md` (SNOBOL4 BB row updated)
- `.github/HANDOFF-2026-05-28-OPUS-SBL-SPAN-ARB-ESCAPE-FIX.md` (this file)
