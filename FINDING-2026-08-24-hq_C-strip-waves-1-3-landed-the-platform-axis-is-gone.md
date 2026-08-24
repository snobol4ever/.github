# FINDING 2026-08-24 hq_C — strip waves 1–3 landed: the platform axis is GONE, and wave 1's own "zero-risk" list was not

**Seat:** `hq_C` (HQ-CORRECTNESS) · **session:** s269 · **mode:** FLEET-4
**Tree:** SCRIP `69449f94` (pushed) · baseline tree `15738e4a` · **RT_OPT `-O0`, pristine, build-then-board**
**Authority:** CEO-11 `strip-execution-go` · `survey-src-2026-08-23/13-switches.md` §6 · CEO-11c empirical switch rule

## THE HOLD CAME OFF AND FOUR WAVES LANDED

hq_P pinned the six-language baseline (`ab1c6b16`) and released this seat's hold at the start of the
session. CEO ruled the two flags. Waves 1, 2, 3a, 3b are landed, each its own commit with its own proof.

| wave | commit | what | proof |
|---|---|---|---|
| 1 | `84b07d2d` | grep-provable dead code, 6 sites, −131 lines | board unchanged |
| 2 | `5354dc0c` | 2 rt.c `ZC_FRAME` tautology guards | ⭐ **rt.o BYTE-IDENTICAL** |
| 3a | `f2347178` | 95 never-taken `!PLATFORM_X86` guards, 74 files | 25/25 `.s` identical |
| 3b | `69449f94` | remaining 102 sites + the axis itself deleted | ⭐ **325/325 `.s` identical** |

**`PLATFORM_X86` in `src/`: 197 → 0.** `bb_platform_t`, `g_platform` and all five `PLATFORM_*` macros are
deleted — the axis is gone, not merely unused.

**The board did not move once, across all four waves:** corpus **m3 363/364 · m4 363/364 · SKIP=0**,
`demo_treebank` the only red and deliberate — equal to hq_P's independent pin. Gates rc=0 throughout:
`emit_no_lang`, `template_medium_invisible`, `bb_one_box`, `rtx_unit`, `no_handencoded_bytes`,
`audit_m3_native_binary_arms`.

## ⛔⛔ THE FINDING THAT MATTERS MOST: WAVE 1's "ZERO-RISK, GREP-PROVABLE" LIST WAS NOT ZERO-RISK

The survey's wave 1 lists **"#error-blocked ZC arms (PROMOTE_ON, FRAME_DEAD5, STORAGE_FRAME_R12)"** as
zero-risk deletes. **Three of them are not deletes at all, and one was never dead.**

- ⭐ **They are TRIPWIRES, and deleting a tripwire before deleting the axis it guards is strictly
  negative.** `ZC_FRAME_DEAD5`'s `#error` guards a **measured 9-net-new-crash** configuration and its own
  text says *"This guard is NOT the fix — it converts a silent 9-crash trap into a loud one."* There are
  **45 live `ZC_FRAME` references** still in the tree. Deleting the label while the arms stand is
  **exactly `ZR-RSPFB5-1`, the mistake that caused the trap in the first place** — it buys 3 lines and
  restores a silent failure. These collapse *with* their axes in waves 4–5, not before.
- ⛔ **`ZC_STORAGE_FRAME_R12` was never dead**: live reference at `x86_asm.h:860` (`x86_zop_regime`).
  It was on a delete list while being read by running code.

⭐ **Transferable rule: a switch that is unreachable and a switch that is a GUARD against an unreachable
config look identical to grep and are opposite facts.** One is residue; the other is the only thing
standing between a future session and a documented 9-crash regression.

## ⭐ THE SECOND CLASS: A DELETE-CANDIDATE THAT A LIVE GATE PRESCRIBES AS ITS REMEDY

`bomb_bytes` was ruled dead by CEO-11b(3) and *is* uncalled — but `audit_m3_native_binary_arms.sh`
**named it as the required cure** for a fake-jmp placeholder arm and grepped for it as an accept
condition. Deleting the function alone would have left a gate demanding something that cannot exist.
Both scripts retargeted to the remedy that does exist (implement the arm; add an `x86_asm.h` encoder;
never hand-encode). Pass/fail logic untouched — the BOMB branch was already unreachable — both re-run
rc=0. ⭐ **"Nothing calls it" is not the same as "nothing depends on it."**

## ⛔⛔ THE INSTRUMENT FAILED, HONESTLY, AND THAT IS THE THIRD LESSON

The brace-matching sweep used for the 38 always-true `if` unwraps **crashed** on `xa_prologue.cpp` /
`xa_epilogue.cpp`: their JS and WASM bodies contain `{` and `}` **inside string literals**, so brace
counting walks off the end. It threw rather than silently mis-editing — but the same counter had
already run over 38 sites, where a wrong edit **can compile and still be wrong**.

⭐ **A clean build is not evidence that a mechanical source transform preserved meaning.** The verdict
was therefore taken on OUTPUT: all 326 crosscheck programs re-emitted with `--compile` and diffed
against their checked-in `.s` — **325/325 byte-identical**. The two crash sites were rewritten by hand.
This is the fourth instance of the standing class *an instrument must be able to express its own
failure*; here it did, and the recovery was to change instruments, not to trust the build.

**The 1 non-identical is pre-existing, not strip damage:** `crosscheck/coverage/coverage_sno_nodes.sno`
does not compile at HEAD at all (`FATAL lower_snobol4` GZ#5 pattern-subset), so no file was produced to
compare. This wave touched **zero** lowerer files; the artifact was last regenerated at corpus
`b10628f4c`, in the `scrip-cc` era. ⭐ **A checked-in `.s` for a program that can no longer be compiled
is a golden nobody can reproduce** — worth its own row.

## FLAGGED, NOT TAKEN

1. ⛔ **Scope boundary, for CEO:** wave 3b's constant-false deletions consumed the **JVM/JS/NET/WASM
   prologue/epilogue template bodies**. That is backend content and CEO-11 puts `backends/` removal in
   Phase 2 — but they are the same constant-false class wave 3 is *defined* by, and they live in
   `src/templates/`, not `src/backends/`. Phase 2 will find them already gone. Raised rather than done
   silently.
2. `wasm_emit_data_segments_str` (`emit.cpp:304`) is now unreferenced. **Left in place** — removing it
   opens the `g_wasm_strtab` thread, which is Phase 2's axis.
3. ⛔ **Pre-existing CLI lie, not introduced here:** `--target=jvm/js/wasm` never assigned `g_platform`,
   so those flags already emitted x86 rather than stubbing out. Now there is no platform variable behind
   them at all. Recorded so it is not later mistaken for strip damage.
4. **Provenance:** history pointers written before a push go stale by construction — the push rebased
   waves 1–2 (`b881142b`→`84b07d2d`, `d60993d0`→`5354dc0c`), so wave 2's message cites a hash that no
   longer exists. Later waves cite post-push hashes. Not rewritten (history rewrite is forbidden).

## NEXT

**Wave 4 — the ζ selector complex — is the one real hazard in the ladder** and is not mechanical: these
are **runtime-constant branches, not dead `#if`s**, so the proof is m3≡m4 byte-diff of regenerated `.s`,
not gates. Per CEO's ruling the `--zeta-storage` / `--zeta-port` / `--zeta` CLI trio dies **with** the
collapse, leaving hard-error stubs per the `frame-r12` precedent. Then wave 5 (batched ZC), waves 6–7,
and the `00-INDEX` dead-code carve.

Related: `[[FINDING-2026-08-23-hq_C-switch-keep-list-certified-and-the-zd-family-is-a-per-op-filter]]`.
