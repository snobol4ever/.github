# FINDING 2026-08-12d — BOARD B-0 (concurrent seat): the r9 seed ALREADY EXISTS as `rtcc_load_all` on the `flat_α` twin, and the placement prescribed in 12c clobbers the ζ-frame exit wires

**Seat:** BOARD (`GOAL-SN4-HOME-BOARD.md`), rung B-0. **Compiler bytes written: ZERO** (charter). Corrective addendum to `FINDING-2026-08-12c-…-THE-M4-HARNESS-IS-EXONERATED-…`, reached independently and concurrently; the repair is corrected, not claimed.

⛔ **SEAT COLLISION, REPORTED NOT RESOLVED:** two live BOARD sessions ran B-0 simultaneously in ONE shared clone (`/home/claude/SCRIP`, `/home/claude/.github`). That is the s38b race the HOME EXECUTION MODEL forbids by its ONE INVARIANT ("one live session per seat file") and it also breaks "one clone per seat". Timeline in this container: my checkout 13:38–13:40; `52545cbf` landed 13:42; `8729da2f` + `43b74a95` (12c, B-0 CLOSED) landed 14:11 — into the working tree I was mid-build in. Lon's call, not a seat's.

---

## 1. WHAT 12c GOT RIGHT (independently reproduced here)

Every load-bearing claim of 12c reproduces at a **verified-clean build** (`rm -rf out/rt_pic`; 264-line log; 0 errors):

- The harness is exonerated. `run_suite.sh MODE=compile` is honest; `SCRIP`, `RTOUT="$(dirname "$SCRIP")/out"` and `out/libscrip_rt.so` (Makefile:343) all resolve. The absolute-path class is not involved.
- Stage split by hand on `A01`: compile rc=0 (39,887-byte `.s`) · gcc link rc=0 · **run rc=139**.
- `mov qword ptr [r9 + 0], rax  # S` executes with r9 never established.
- Minimal pair, same program ± one leading statement: `S = "abcd"` → rc=139, **zero** `mov r9,…` in the emitted `.s`; `OUTPUT = "" ; S = "abcd" ; OUTPUT = S` → rc=0 `abcd`, **two** `mov r9, qword ptr [r11 + 48]`.

**Refinement of the masking mechanism.** 12c attributes the mask to "zero user globals" in `hello`. That is one arm; the sharper statement is per-*statement*, and the manual pins it (Ch.3, p.15 region): `OUTPUT` is an **ordinary assignment to a variable whose name is special** — "values assigned to it are displayed". So "first statement is an assignment" is not the discriminator. An ordinary variable compiles to a direct `[r9+…]` slot write; `OUTPUT` routes through `NV_SET_fn`, and it is that call's **RTCC veneer restore** which incidentally establishes r9. Hence `OUTPUT = ""` — a global-free, output-free statement — is a **complete cure** for every later access in the same program. Any veneered C crossing before the first global read/write masks the defect, not merely the absence of globals.

## 2. CORRECTION 1 — THE SEED IS NOT MISSING FROM THE PRODUCT, ONLY FROM ONE OF TWO TWINS

12c §3 names the emit site as `scrip.c:1473` (SNOBOL4) / `:1265` (Icon) and §4 prescribes **three new instructions** (`mov edi,1` / `call rt_gva_island@PLT` / `mov r9, rax`).

The sanctioned mechanism already exists and is already correct:

```c
/* src/driver/scrip.c:1490 — the flat_α preamble */
{ extern unsigned char g_rtcc_on; if (g_rtcc_on) emit_textf("  call rtcc_load_all@PLT\n"); }
/* RC-5-GVA: main is the first C→generated crossing; load all claimed GPRs (incl. R9=RT_GVA_VA) from the block before any generated code runs. */
```

`rtcc_load_all` (`src/runtime/rtx/rtcc_init.c:38`) loads all nine claimed GPRs from `g_rtcc_block`; slot 48 (R9) is seeded **once** with the constant `RT_GVA_VA` by the runtime constructor (`rtcc_init.c:24`, RC-5-GVA, BLOCK-CANONICAL EXCEPTION for constant globals).

There are exactly **two** m4 preamble emitters. Both seed r12 from `[0x70000000]`; only one seeds r9:

| emitter | r12 seed | `rtcc_load_all` | entry |
|---|---|---|---|
| `flat_α` path | `scrip.c:1488` | **`:1490` — present** | `jmp flat_α` |
| `main_α` path | `scrip.c:1278` | **absent** | `jmp main_α` (`:1290`) |

The comment at `:1277` describes itself as *"Mirror of the flat_α path already at line 1438"* — a mirror minted before RC-5-GVA landed the seed on the flat side, and never re-synced (its own line reference is stale by 50 lines). **This is the ONE-AUTHORITY/two-copies class, not a missing feature.**

**Therefore the repair is ONE line restoring the twin, not three hand-rolled instructions**, and the difference is load-bearing:
- The twin is **gated on `g_rtcc_on`**, so `SCRIP_RTCC=0` stays byte-identical (killswitch law, RULES). An ungated 3-line seed breaks that guarantee — and at OFF the templates address globals absolutely (`ABSQ(RT_GVA_VA + …)`, `bb_func_activate.cpp:149`), so the seed is not merely redundant there, it is off-contract.
- `rtcc_load_all` establishes the whole claimed set at the C→generated edge, which is what the RTCC convention requires of `main`; seeding r9 alone leaves the other eight to the same "restore of a value never established" hazard 12c correctly names.

## 3. CORRECTION 2 — "IMMEDIATELY BEFORE `jmp main_α`" IS UNSAFE (ζ-FRAME EXIT WIRES)

12c §4/§6 prescribe inserting the seed *"immediately before `jmp main_α`"*. Any seed there is a **C call**, and SysV makes rcx/rdx/rsi/rdi/rax/r8–r11 caller-saved; `rtcc_load_all` additionally *loads* rcx (slot 8), rdx (16) and rsi (24) from the block. The ζ-frame arm (`scrip.c:1282–1288`, ICN-FR-2) puts the exit wires in exactly those registers at exactly that point. Emitted Icon `main` at this HEAD, verbatim:

```
xor   esi, esi
xor   r14d, r14d
lea   rcx, [rip + .Lmain_zf_γ]
lea   rdx, [rip + .Lmain_zf_ω]
jmp   main_α
```

Inserting at the prescribed point destroys `rcx`/`rdx` — the γ/ω exit-wire pointers — for every ζ-frame `main`, and `rsi` (match start pos = 0) for all mains. The failure mode is ICN-FR-5's: a wild jump, not a wrong answer.

**Correct insertion point: after `:1279` and before `:1281`** — i.e. after the `is_prolog` W1 twins (`rt_gcheap_warmup` / `rt_plw_floor_bypass_on`, which would clobber a freshly loaded r9/r10/r11) and before `xor esi, esi` and the ζ-frame `lea rcx/rdx`. r12 is unaffected either way (callee-saved).

**The instrument is right; only the prose is wrong.** `util_board_m4_gva_seed_probe.sh` inserts *before* `xor esi, esi` and is therefore correctly placed — its 153/159 number stands. A seat implementing from §4/§6 prose rather than from the script would ship the ζ-frame regression.

## 4. STATUS / OWNER

Unchanged from 12c §6: BOARD does not claim the edit. It is one gated line in `src/driver/scrip.c` at the `main_α` preamble, plus the same audit for the Icon arm, and belongs to whichever of **RBX**/**WIRES** claims it first (first push wins, RULES 2026-08-10). This finding only ensures the line that lands is the twin, gated, and placed where it cannot clobber the wires.

**Acceptance remains 12c's:** the seed must dominate every consumer including the `[r11+48]` restores; 153/159 is the *proof*, not the acceptance. The residual 8 is B-1 work once the seed lands, and no m4 number taken between 2026-08-10 and 12c may be quoted.
