# FINDING — m4 IS DARK FOR EVERY PROGRAM THAT NAMES A VARIABLE, AND THE ROOT CAUSE IS THAT NOTHING EVER SEEDS r9 INTO THE REGISTER — ONLY A VENEER RELOAD DOES, AND THE FIRST THREE CROSSINGS ARE BARE

**Seat:** WIRES (`GOAL-SN4-HOME-WIRES.md`) — found while building a W-6 nested-crossing witness. **Owner of the repair: BOARD B-0** (m4 harness), routed here with root cause, reproducer and negative controls.
**Session:** 2026-08-12, Opus 5. **Trees:** SCRIP `52545cbf` (+ `19d9ba37`, `54ed41bc`) · corpus `c91d1adf` · x64 `5035571`. **ZERO compiler bytes.**

---

## 1. THE MEASUREMENT — m4 IS NOT "FLAKY", IT IS DARK ON A ONE-LINE PROGRAM

Built exactly per the sanctioned recipe (`audit_jcon_wholesale.sh`): `scrip --compile` → `gcc -no-pie prog.s -L out -lscrip_rt -Wl,-rpath,out`. Runtime `.so` and `scrip` binary built in the same `make` at the same minute; `.so` is untracked, so this is the tree's state, not a stale artifact.

| program | m3 | m4 |
|---|---|---|
| `OUTPUT = "hi"` | `hi` | **PASS** |
| `S = "hi"` (assign only, never read) | `done` | ⛔ **SIGSEGV rc=139** |
| `S = "hi"; OUTPUT = S` | `hi` | ⛔ **SIGSEGV rc=139** |
| `OUTPUT = "[" S "]"` — **merely naming an unset variable** | `[]` | ⛔ **SIGSEGV rc=139** |
| `"ab" ? "a"` — pattern match, no variable | `m` | **PASS** |
| `2 + 3` · `"a" "b"` · bare `:(L)` goto | ok | **PASS** |

⭐ **It is not patterns, not DEFINE, not deferred evaluation. It is the mere presence of a user variable.** Since essentially every real program names a variable, **m4 is dark for the corpus**, and every m4 number quoted at this HEAD is void. The plan's `⛔ m4 arm DARK → B-0 first` is confirmed and now has a two-line reproducer.

## 2. ROOT CAUSE — r9 IS INSTALLED ONLY BY A VENEER RELOAD, AND THE PROLOGUE'S CROSSINGS ARE BARE

Fault site, `OUTPUT = "[" S "]"`: `0x4011e2 <n2_var_α+4>: mov (%r9),%rax` with **`r9 = 0x0`**.

`r9` is the GVA base (`RTCC_GVA_REG`, RC-5-GVA; `rtcc.h:62` calls it a SEALED ABI, not a knob). Every global read is `GVARQ` = `[r9+k*16]`.

**The seed is present and correct.** `rtcc_init` (`rtcc.h`/`rtcc_init.c:24`, an ELF `constructor`) sets `g_rtcc_block[RTCC_SLOT_R9]` once, because `RT_GVA_VA` is constant for process lifetime — the documented *"BLOCK-CANONICAL EXCEPTION for constant globals; no companion writes needed anywhere."* Verified live in the faulting process:

```
p g_rtcc_on          -> 1
p/x g_rtcc_block[6]  -> 0x70001000      (RTCC_SLOT_R9 = 6, ×8 = byte offset 48)
```

**Consistent with that exception, the veneer WRITEBACK deliberately skips offset 48** — it stores rax/rcx/rdx/rsi/rdi/r8 (0..40) then r10/r11 (56/64), never r9. The **RELOAD** does read it: `mov r9, qword ptr [r11 + 48]`.

⛔ **THEREFORE THE ONLY INSTRUCTION IN THE ENTIRE PROGRAM THAT EVER PUTS THE GVA BASE INTO r9 IS A VENEER RELOAD.** Grep of the emitted program confirms it — the complete set of writes to r9 is three identical reloads:

```
80: mov r9, qword ptr [r11 + 48]
123: mov r9, qword ptr [r11 + 48]
144: mov r9, qword ptr [r11 + 48]
```

And the program's first three C crossings are **BARE** (no writeback, no reload): `core_lib_init@PLT`, `rt_gva_island@PLT`, `gva_register@PLT`. So between process entry and the first *veneered* crossing, **r9 holds its process-entry value, 0.** A variable access in that window dereferences null.

**The prologue never performs the initial load.** The block is seeded; nothing hands it to the register.

⭐ **Falsifiable prediction for whoever takes the repair:** a program whose first GVA access falls *after* a veneered crossing should PASS in m4. That is consistent with the table above — `literal only`, `arith`, `concat`, `goto` and the variable-free match all avoid GVA entirely. **Test it before fixing; it discriminates "prologue never seeds" from "reload path is wrong."**

## 3. NEGATIVE CONTROLS RUN (both hypotheses FALSIFIED — do not re-spend them)

- **`-Wl,-z,now`** (W-6's named belt-and-suspenders for the r11 lazy-binding clobber): **does NOT cure it.** L2/L3/L4 SIGSEGV identically with and without. The lazy-binding resolver is exonerated for this class.
- **`SCRIP_RTCC=1` / `SCRIP_RTCC=0` in the run process:** **does NOT cure it.** `g_rtcc_on` already reads 1 by default and the slot is already seeded. The compile-process/run-process split is real in mode 4 but is NOT this defect.
- **Stale runtime `.so`:** ruled out — `scrip` and `out/libscrip_rt.so` share a build minute and the `.so` is untracked.

## 4. WHY THIS SITS NEXT TO THE WIRES SEAT (and why the veneer is EXONERATED)

The veneer round-trips r10/r11 **faithfully** — proven separately this session (172 veneered crossings, writeback/reload balanced, r11 restored last). It preserves whatever it is given. Here it is given nothing, and faithfully preserves nothing.

⛔ **The structural lesson is the one W-6 already carries:** a whole-program invariant (r9 = GVA base) is installed **only as a side effect of crossing into C**. A register the entire program depends on is established by a mechanism whose job is *preservation*, not *establishment* — so its correctness depends on control flow nobody stated. That is the same shape as `g_blob_ctx` / `g_zctx` / `g_star_peek`: a value with one home and no owner.

**This does NOT change the WIRES ladder.** r10/r11 are writeback-and-reload (round-tripped); r9 is reload-only (established). W-0/W-1/W-2 are unaffected. What it DOES change is gating: **⛔ no WIRES rung can be gated "BOTH modes" until B-0 lands, because m4 cannot run a program with a variable.** Until then every WIRES gate is m3-only and must SAY so — exactly as this seat's cursor already requires.

## 5. ⛔ THREE INSTRUMENT DEFECTS OF MY OWN, ALL THE SAME FAMILY

Recorded because this project convicts this class repeatedly (s14 `grep -c` units; s15b padded-mnemonic patterns) and it cost me three false readings in one session:
1. **awk array keys are STRINGS** — `for (n in calls)` then `i < n` compared `"92" < "104"` lexicographically; a lookback loop never ran and reported ten false BARE crossings. Fix: `n = k+0`.
2. **A name-shaped symbol filter** counted `bb_match_defer[abi:cxx11]()` — a compile-time template function returning `std::string` — as a match-time hazard. `nm -C` settles it in one command.
3. **`r=$?` after a pipeline** captured `head`'s status, not the binary's, and printed `m4rc=0` for runs that were visibly segfaulting on stderr. **This one nearly buried the entire finding above** — the first bisect table read "rc=0, empty output," which looks like a silent wrong answer rather than a crash.

⭐ **The rule these earn, offered for RULES.md:** *an instrument reports a class only after ONE member of that class has been confirmed by hand.* All three survived a plausible-looking table and died on first manual inspection.

---

## NEXT SEAT (BOARD B-0), IN ORDER

1. **Reproduce in 30 seconds:** `printf '\tOUTPUT = "[" S "]"\nEND\n' > /tmp/b.sno`, compile, link per the recipe, run → rc=139. m3 prints `[]`.
2. **Run the §2 prediction** (first GVA access after a veneered crossing) before writing any fix — it discriminates between the two candidate repairs.
3. **Candidate repair shape:** emit the initial `mov r9, [g_rtcc_block+48]` in the m4 program prologue (after `rtcc_init`'s constructor has run, i.e. after `core_lib_init`), so r9 is ESTABLISHED by the prologue and merely PRESERVED by veneers. ⛔ Do not "fix" it by adding r9 to the veneer writeback — that would overwrite the constant seed with whatever garbage r9 held and re-break it on the first crossing, and it contradicts the BLOCK-CANONICAL EXCEPTION.
4. **Then re-cut every floor.** All P0 m4 numbers taken before this lands are void by construction.
