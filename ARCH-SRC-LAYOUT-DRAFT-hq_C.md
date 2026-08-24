# ARCH — SOURCE LAYOUT PROPOSAL (hq_C draft, s269)

**Status: DRAFT. Nothing moves before Lon rules.** Folder structure only — the build system is hq_P's
half of the brief, and this draft is written so that it constrains the build as little as possible.

**Companion:** `FINDING-2026-08-23-hq_C-src-reorg-carve-list-adversarial-verification.md` — every
number below marked ✅ was measured there this session. Numbers marked ⟨carried⟩ come from the CEO
survey reports and were **not** re-verified.

**Binding constraints** (00-INDEX § CEO-9): TEMPLATE-ONLY EMISSION · BOTH-MEDIUM · no-lang-past-lower ·
PEERS · zero-blank-lines C style · **m3≡m4** · per-checkout objdir (HQ-27) · flag-keyed build cache ·
gates stay green through any move · 149 scripts reference `src/` · announcement timing.

---

## 0. The one ordering rule: ⭐ CARVE BEFORE MOVE

22 files and roughly 700 verified lines of dead code are on the table. A file that dies never needs its
script paths fixed, never needs an objdir entry, and never shows up in a move diff. And the reverse
ordering is actively dangerous: **after a move, a fossil path and a move mistake are indistinguishable**
— both present as "script names a file that isn't there". `test_gate_bb_one_box.sh` already fails that
way today (✅ measured, rc=1).

Proposed phase order, each phase landing green on its own:

1. **Carve** the verified-dead (§ A/B/C of the FINDING), no file moves at all.
2. **Fix the 52 fossil script paths** (✅ measured across 19 files) — with the tree still in its old
   shape, so every fix is provably about the script and not about the move.
3. **Move**, one directory per commit.
4. **Switch collapse** (§ G of the FINDING) — last, because it is the only phase that touches emitted
   bytes and it wants an unmoving tree underneath its byte-diffs.

---

## 1. Current shape (measured this session)

| dir | files | bytes | note |
|---|---|---|---|
| `src/templates` | 155 | 854 K | 131 `bb_*` + 17 `xa_*` + `x86_asm.h` |
| `src/runtime` (top) | 22 | 1.72 M ⁽incl. subdirs⁾ | `by_name_dispatch.c` dominates ⟨carried⟩ |
| `src/runtime/{core,rt,rtx,builtins}` | 11 / 23 / 24 / 7 | — | |
| `src/parser/*` (7 languages) | 70 | — | `raku` 10.6 K lines, `snobol4` 6.7 K, `pascal` 5.4 K |
| `src/lower` | 10 | 623 K | |
| `src/emitter` | 4 | 364 K | `emit.cpp` + `emit.h` are nearly all of it |
| `src/driver` | 18 | 257 K | |
| `src/contracts` | 17 | 191 K | |
| `src/optimizer` | 24 | 50 K | **734 lines total** — the smallest and cleanest tree in the repo |
| `src/machine` | 5 | 8 K | 156 lines; two of the five are forwarding shims |
| `src/tools` | 5 | 31 K | none of it in the `.so` |
| `src/include` | 4 | 5.4 K | `bb_box.h`, `dtp.h`, `emit_ir.h`, `XA.h` |
| `src/backends` | 40 | — | ✅ **zero C/C++/H files** — `.cs .java .il .wat .js .j .mjs` |

✅ **Zero duplicate object basenames** across the 262 built sources — so the objdir's `$(notdir)`
flattening (`Makefile:385`) is safe *today*, by luck rather than by design. Two duplicate **header**
basenames exist and both are deliberate 2-line forwarding shims: `src/machine/bb_box.h` →
`../include/bb_box.h`, and `src/runtime/core/descr.h` → `../../contracts/descr.h`.

---

## 2. Proposed structure

```
SCRIP/
  backends/                    ← OUT of src/ entirely (JVM/.NET/WASM/JS assets, no C)
  src/
    frontend/                  ← was parser/ ; language identity lives here and nowhere else
      snobol4/ snocone/ icon/ prolog/ raku/ rebus/ pascal/
    lower/                     ← the identity boundary: nothing past here knows a language name
    ir/                        ← the spine: IR.h, SM.h, BB_t, descr.h, stage2.h, bb_program.h,
                                 ab_abi.h, pin_va.h, zeta_*.h  (today: contracts/ + machine/ + include/)
    optimizer/                 ← unchanged
    emitter/                   ← emit.cpp split 3 ways, emit.h split 4 ways ⟨carried, 05⟩
    templates/
      bb/                      ← the 131 one-box bb_*.cpp
      xa/                      ← file-scaffolding boxes (≈3 live after the carve — ✅ measured)
      x86/                     ← x86_asm.h split 3 ways under one umbrella header ⟨carried, 07⟩
    runtime/
      core/ rt/ rtx/ builtins/ ← as today
    driver/
    tools/                     ← never in the .so; opt-in builds only
```

### Why each move, with its receipt

**`src/backends/` → `SCRIP/backends/`.** ✅ It contains **no C, C++, or header file at all** — 40 files
of `.cs .java .il .wat .js .j .mjs .jar .csproj .md` — and **nothing in it appears in `RT_PIC_SRCS`**.
The C build cannot notice this move. It is the single largest structural simplification available and
it is free. (⟨carried, 11⟩: zero live consumers, zero overlap with the sibling `snobol4jvm` /
`snobol4dotnet` repos. 70 dir-level script references will need updating — phase 2 work.)

**`parser/` → `frontend/`.** Not cosmetic. The standing law is *"language identity stops at lower"*, and
the directory that owns identity should be named for that role, not for one of the techniques used
inside it (three of the seven frontends are not just parsers — they carry lowering and runtime code
today, which is the next point).

**`contracts/` + `machine/` + `include/` → `ir/`.** Three directories hold one concept between them,
and the smallest of them is 156 lines with two forwarding shims in it. `src/include/` in particular is
4 files / 5.4 K and exists only to be a fourth place to look. Dissolving it also removes the
`bb_box.h` shadowing pair (`src/include/bb_box.h` vs the 2-line `src/machine/bb_box.h`, resolved today
purely by `-I` ordering in `CXXRT`). ⟨carried, 09: "dissolve src/include/"⟩.

**Code that must leave the frontend tree** ⟨carried, verified only where noted⟩:
- `scrip_cc.h` — a cross-language contract sitting in `parser/snobol4/`. ✅ **57 files include it**
  (report 01 said ≥25; the measured number is 57). It belongs in `ir/`.
- `re.c` (raku NFA engine) → `runtime/` · `icon_runtime.c`, `pl_cell*`/`pl_area` → out of `frontend/`
  · `tree_to_sno.c` + `binop_apply` out of `lower/` · `sil_macros.h` out of `emitter/`.

**`tools/` stays a directory but becomes a stated non-member of the `.so`.** ✅ All 5 files are already
outside `RT_PIC_SRCS`; the reorg should make that a rule rather than an accident.

---

## 3. Three constraints this draft asks Lon and hq_P to rule on

**3.1 ⭐ Objdir basename uniqueness is currently unguarded.** `RT_PIC_OBJS` flattens with `$(notdir)`
(`Makefile:385`) and `vpath` searches `$(sort $(dir …))`. ✅ There are zero collisions among the 262
sources today — but nothing enforces it, and the proposed `templates/{bb,xa,x86}` split plus an
`ir/` merge both create new chances to introduce one. A collision does not error; it **silently builds
one file twice and drops the other**, which is the HQ-27 class through a third door. **Ask: mirror the
source tree in the objdir** (hq_P's call on mechanism; hq_C's position is only that "no two objects may
share a basename" must become enforced rather than observed).

**3.2 ⛔ `src/` currently includes out of `scripts/`.** ✅ `src/runtime/core/core.c:26` reads
`#include "../../../scripts/monitor/monitor_wire.h"`. No layout can be clean while the build tree
depends on the test tree. Two exits: move `monitor_wire.h` into `src/ir/` (or `runtime/core/`) and leave
a shim in `scripts/monitor/`, or let the monitor wiring die in the switch collapse. **hq_C's
recommendation: decide this in the switch-collapse phase, not the move phase** — `MONITOR_BIN` is one
of the 351 env switches and a monitor verdict is already a verdict on a different program (RULES.md).

**3.3 ⛔ One absolute path into the retired root.** ✅ `src/driver/csnobol4_shim.c:11` reads
`#include "/home/claude/csnobol4/data.h"`. It breaks D-17 PORTABLE-HOME outright and cannot resolve
from a slim root. It is also not in the build. Whatever the layout, this line does not survive it.

---

## 4. What this draft deliberately does **not** propose

- **No renaming of `bb_*.cpp` files.** ✅ The templates are the cleanest thing in the tree — zero
  `MEDIUM_*`, zero raw-byte producers, zero language branches across all 131 (⟨carried, 04+08⟩, and the
  BOTH-MEDIUM gate reads 0 sites / ceiling 0 this session). Grouping them into `bb/` is enough; touching
  their names would churn 92 dir-level script references for no correctness gain.
- **No DRY consolidation in the move phase.** The cset-dispatch ×5, the duplicated ISO term-compare, the
  two Prolog parsers, the `by_name_dispatch.c` god-functions ⟨carried, 04/06/10⟩ are all real — and all
  of them change behaviour-bearing code. They are *after* the move, each with its own byte-diff, never
  bundled into a commit whose stated purpose is "moved files".
- **No build-system opinion.** hq_P's half.

---

## 5. The gate contract for every phase

hq_C's condition on all of it, and the only thing in this draft that is non-negotiable from the
correctness seat:

- **Every phase re-proves the blocking set**: `test_corpus_snobol4.sh`, `test_gate_emit_no_lang.sh`,
  `test_gate_template_medium_invisible.sh`, plus the owning goal file's named gate — after
  `make pristine` (HQ-27), with the baseline **measured, not quoted** (the long-cited m3 339/341 totals
  are stale; see CLAUDE.md).
- **Every phase that touches emitted bytes carries a byte-diff**, per the Class A / Class B split in
  § G.5 of the FINDING. Moves and carves of unreachable code are Class A and need none; the switch
  collapse is mostly Class B and needs one every time.
- ⭐ **A gate that cannot fail is worse than no gate.** Before the move phase begins,
  `test_gate_bb_one_box.sh` must be repaired or retired (✅ it is red today, and for reasons that have
  nothing to do with fossil paths), and the 52 fossil paths must be fixed — including the two in the
  **mandatory handoff regen scripts**.
