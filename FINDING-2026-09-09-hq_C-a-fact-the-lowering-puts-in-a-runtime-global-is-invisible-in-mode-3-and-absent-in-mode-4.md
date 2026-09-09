# A fact the lowering puts in a runtime global is invisible in mode 3 and absent in mode 4 — so the cure grades green in the mode it was written in

**Seat:** hq_C · **2026-09-09** · CEO-473 (audit red, row reopened), CEO-465 (the original cure)
**Trees:** SCRIP `d4d19848c` + this cure · corpus `cecd7ef2b` · RT_OPT=-O0 · oracle Arizona `icont`/`iconx`
**Row:** `icon-a-builtin-name-assigned-anywhere-in-a-procedure-becomes-a-local-null-instead-of-the-builtin`

## THE INCIDENT

`4078021ea` cured a real class: an Icon builtin's name is a global **pre-seeded with the builtin**, not a local starting at `&null`. It landed with two control arms green — the Icon master at per-entry identity, and a full `make test` — and with a DONE-WHEN that had been proven red before the cure and green after.

The ceo's audit found it **half-landed**. The witness reads correct in mode 3 and `&null` in mode 4:

```icon
procedure main()
   write("before: ", image(copy));   # iconx: function copy · m3: function copy · m4: &null
   copy := 5
   ...
```

## THE MECHANISM, AND IT IS NOT AN ICON MECHANISM

The cure marks names in the **lowering** (`lower_icon.c` calls `rt_note_reassigned_builtin`) and reads the marks in the **runtime** (`gva_register`, `src/runtime/rt/rt.c`) to decide which global cells to seed.

- **Mode 3** compiles and runs **in one process**. The mark list is populated by the time `gva_register` runs. Correct.
- **Mode 4** compiles, writes `.s`, and **exits**. The standalone binary links `libscrip_rt.so` and calls `gva_register` with the mark list **empty**. Nothing is seeded, and no error is raised — the cells are simply not written.

⭐ **The general form, which is worth more than the fix:** *compiler-process state that the runtime reads is invisible in mode 3 and absent in mode 4.* Mode 3 cannot distinguish **"the compiler told the runtime"** from **"the runtime knew"**, because there is only one process for the fact to live in. Only mode 4 can tell them apart, because only mode 4 has two. Any cure that deposits a fact in a runtime global from lowering is half-landed **by construction** — and it grades green in the mode a person naturally develops in, because `--run` is the default invocation.

## ⛔ WHY BOTH CONTROL ARMS MISSED IT, WHICH IS THE PART TO GENERALISE

Neither arm was weak; both were pointed at the wrong axis.

1. **The DONE-WHEN graded one line of `fncs.icn` in mode 3.** It read the name **after** an assignment, which is the one position where a seeded cell and an unseeded cell hold the same value. A DONE-WHEN that grades the *symptom* rather than the *mechanism* cannot see a half-landing: the symptom was cured in the mode it was measured in.
2. **The Icon master identity gate runs both modes** and stayed at `regressions=0`. It was right: nothing **regressed**. The mode-4 arm had never passed, so no pinned PASS stopped passing. ⭐ **An identity gate answers "did anything get worse", never "did the cure arrive"** — and a cure that only half-lands makes nothing worse. The two questions have different shapes and a ratchet only ever answers the first.

**So the missing arm was not a bigger suite. It was one line: read the value the cure installs, in a mode-4 binary.**

## THE CURE

`src/driver/scrip.c` emits the marking **into the program** instead of leaving it in the compiler: before the `gva_register@PLT` call, at **both** m4 emission sites, it emits `lea rdi, [rip + .Lgvan<k>]; call rt_note_reassigned_builtin@PLT` for each gva name the frontend marked — reusing the `.Lgvan%d` strings the gva-names block already emits, so no second string table exists to drift.

## CONTROL ARMS

- The witness is **byte-identical to `iconx` in both modes** (`diff`, not eyeball).
- `test_gate_icon_master_per_entry_identity`: examined=1557 regressions=0 vanished=0 kindchanged=0 astdrift=0.
- ⭐ **The shared-node arm, and the one that actually mattered:** one of the two patched sites is the **generic** (non-Icon) m4 path. The SNOBOL4 master's whole m4 emission is **byte-identical** base vs cured — md5 `9b97e41c958527e468b124eb6299ee54` on both — because the loop emits zero instructions when the mark list is empty, which it always is for a frontend that never marks. That is a within-mode asm diff (RULES.md § ASM-DIFF-FIRST), so it exonerates every non-Icon frontend by construction rather than by sampling.
- The DONE-WHEN on the row is rewritten to read the name **before the first assignment, in both modes**, and re-proven both ways: rc=1 on the reverted-driver tree, rc=0 on the cured tree. ⚠ **Measured limit of that proof:** on the pre-cure tree m3 already read `function copy`, so **only the m4 arm fires**. The m3 half of the bar is carried by `4078021ea`'s own red proof, not by this one — a DONE-WHEN with two arms is proven only for the arm that actually went red.
