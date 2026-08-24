# FINDING — the SET-today switch keep-list, CERTIFIED by real measurement; and the `SCRIP_ZD_*` family is not an instrument, it is a per-op filter that is already illegal

**Seat:** `hq_C` (HQ-CORRECTNESS) · **Session:** s269 · **Date:** 2026-08-23
**Brief:** CEO `empirical-switch-rule` (GOAL-CEO.md CEO-11c) step 1 — *"FIRST certify the SET-today list by real measurement … the certified list is the deliverable that unlocks the rest"* — plus CEO `diagnostic-instruments-keep` (CEO-11c amended), plus the two pre-strip repairs from `strip-scope-amendment`.
**Status of the strip itself:** still HELD at the wave gate pending hq_P's six-language scoreboard pin. Nothing was deleted. This session measured, and repaired two instruments that would have hidden the strip's own damage.

---

## 1. THE HEADLINE NUMBER WAS WRONG BY 6x, IN THE DIRECTION THAT MATTERS

Report 13 (`survey-src-2026-08-23`) estimated **~8** script-set env vars. I flagged that census as substring-level and owed a real one. Measured:

| set | how measured | count |
|---|---|---|
| read by `src/` | `getenv("NAME")`, exact | **350** |
| self-set by `src/` | `setenv`/`putenv` | **0** |
| assigned **anywhere** incl. prose | assignment-level regex | 181 |
| assigned in the **live harness** (`scripts/` + `Makefile`) | assignment-level | 50 |
| … minus comment-only mentions | non-`#` lines only | 47 |
| … plus `SCRIP_ZONE` (see §2) | argv door | **48 CERTIFIED** |
| **UNSET — candidates to die** | | **302** |

⭐ **The certified SET-today list is 48, not ~8.** Every one has a named non-comment assignment site, recorded in `scripts/util_switch_census.sh` output (see §5).

⛔ **AND THE OBVIOUS SHORTCUT IS A TRAP: 131 of the 181 "assigned" names are assigned ONLY in `.github/` and `corpus/`** — FINDINGs, READMEs and probe programs *quoting* a command line. **Prose is not a setting.** A census that greps the org brain for `FOO=` certifies documentation as configuration and would have kept 131 dead switches alive. Attribute every assignment to its tree before counting it.

## 2. THREE SWITCHES THAT LOOK SET AND ARE NOT — AND ONE THAT LOOKS UNSET AND IS

A plain `NAME=` regex is wrong in **both** directions, and both errors showed up in a 50-item list:

- `SCRIP_ICN_LEGACY` — appears only inside gate comments, which themselves record that it **core-dumps** on their witness. A losing arm with a decided winner. **DELETES.**
- `SCRIP_OPT` — its single harness mention is a comment in `test_gate_instr_budget.sh` saying `SCRIP_OPT=0` produces **undefined `*_β` symbols at LINK time**. Consistent with RULES.md (*"emergency-only, nothing may depend on it"*). **DELETE-CANDIDATE, FLAGGED** — row `opt0-residual-two-defects` is open against it; CEO/Lon may want that row closed first rather than the switch removed under it.
- `SCRIP_ZONE` — comment-only by regex, **but genuinely set today**: `test_gate_zdp_on_null.sh:27` is `ENVS=("$@"); [ ${#ENVS[@]} -eq 0 ] && ENVS=("SCRIP_ZDP=1")`, i.e. the gate takes `VAR=1` **as argv** and its own header documents `bash scripts/test_gate_zdp_on_null.sh SCRIP_ZONE=1`. **KEEPS.**

⭐ **Transferable:** a switch can be set through a door no assignment regex can see — argv, `ENVS` arrays, `env -S`, make variable forwarding. Certification has to read the harness, not only grep it.

## 3. ⭐⭐ CEO'S NAMED BORDERLINE IS ANSWERED WITHOUT ASKING LON — THE CODE'S POLARITY DECIDES IT

CEO (`diagnostic-instruments-keep`) named the open question: *"whether the 36 `SCRIP_ZD*` dump flags are one instrument or 36 leftovers: one-line ask to Lon, lean keep-if-coherent, do not stall."*

**No ask is needed. They are not dump flags at all.** Measured polarity of all 37 consumers:

| polarity | shape in `src/` | n | verdict |
|---|---|---|---|
| **kill-switch, default ON** | `e && *e=='0' ? 0 : 1` — can only ever **disable** | **26** | residue → **DELETES** |
| opt-in, default OFF | `e && *e=='1' ? 1 : 0` — produces output | 7 | instrument → **KEEPS** |
| raw value | name/list parameter | 4 | 2 keep, 2 delete (below) |

⛔ **The 26 emit nothing. They observe nothing. There is no dump, no trace, no census behind any of them** — the name `ZD` is ζ-**depth planning**, not ζ-**dump**. Each one only withholds a single op from ζ-depth planning. Under Lon's own operating test — *"a one-off toggle or kill-switch with a decided winner = residue"* — all 26 are residue, and every one of them is already at its winning value.

### ⛔⛔ AND THEY ARE ALREADY ILLEGAL UNDER A STANDING LAW, INDEPENDENT OF THE STRIP

RULES.md / CLAUDE.md, **NO PER-OP FILTER** (Lon 2026-08-20): *"no code path may admit or refuse family members by op identity, and no per-op exception list may exist anywhere."*

`zd_wants()` in `src/emitter/emit.cpp:2095–2140` is **exactly that construct**, verbatim:

```c
if (op == IR_CUT)        { … getenv("SCRIP_ZD_PL_CUT")  … }
if (op == IR_BINOP_TEST) { … getenv("SCRIP_ZD_RELOP")   … }
if (op == IR_DISJUNCTION){ … getenv("SCRIP_ZD_PL_DJ")   … }
if (op == IR_RETURN)     { … getenv("SCRIP_ZD_RETURN")  … }
…22 more
```

Twenty-six env vars, each gating one op's admission by op identity. `SCRIP_ZD_ONLY` and `SCRIP_ZD_SKIP` are the same law broken more directly still — they take a **list of ops** to include/exclude. **The strip does not need a ruling to remove these; it is removing a violation.** The remaining question is only whether the per-op *structure* survives the switches' removal — it should not, and that is a follow-on row, not this one.

**KEEPS from the family (9):** `SCRIP_ZD_CENSUS`, `SCRIP_ZD_DEPTH`, `SCRIP_ZD_DIAG`, `SCRIP_ZD_GAP`, `SCRIP_ZDLOCAL`, `SCRIP_ZD_TOTAL`, `SCRIP_ZDP_TEARDOWN` (opt-in observation) + `SCRIP_ZDP`, `SCRIP_ZDP_BOMB` (the ZDP frame-discipline checker CEO named explicitly).
**DELETES from the family (28):** the 26 kill-switches + `SCRIP_ZD_ONLY` + `SCRIP_ZD_SKIP`.

## 4. THE TWO PRE-STRIP REPAIRS — BOTH WERE INSTRUMENTS THAT COULD NOT EXPRESS THEIR OWN FAILURE

CEO asked for these before wave 1 precisely so the strip could not silently worsen an unwatched red. Both turned out to be the **same defect class**, and it is the class this org keeps re-earning: *a check that never asserts the SHAPE of what it measures.*

### 4a. `test_gate_bb_one_box.sh` — 36/36 FAIL, and had been for the whole architecture's life. **REPAIRED + negative-tested.**

Its matcher was `extern "C" void bb_[a-z_]+\(` — a signature the template architecture left behind. Every box now returns `std::string` (**144** of them), so the matcher scored **0 on every box file**. Its *only* nonzero hit was the one place it should have scored zero: the three `extern "C" void bb_scc_handoff_*` runtime-state helpers, reported as a helper violation. **A gate red on everything is a gate nobody reads** — and this one guards ONE BOX PER TEMPLATE FILE for both Prolog and Icon.

Repaired to the discriminator the gate's **own header always named** (`_str` suffix = helper; `std::string bb_<name>` = box; both argument shapes are boxes — `bb_every()` and `bb_call(IR_t*)`). Also corrected its file list: five listed files are absent, and **all five were deliberately deleted by named commits, none a regression** — `bb_alt.cpp` (`b00a0afb`, IR_ALT is not a valid IR code), `bb_assign_frame.cpp` / `bb_assign_frame_ref.cpp` / `bb_binop_gvar_relop.cpp` (`3d0a0d57`, dead-code sweep), `bb_keyword.cpp` (`2d46be9c`, IR_KEYWORD split).

⭐ **Once it could see, it immediately found a real violation** — `bb_binop_relop.cpp` held **two** boxes, `bb_binop_relop()` and `bb_binop_relop_val()`, both dispatched from `emit.cpp:1110–1115`. Split into `bb_binop_relop_val.cpp` (+ Makefile line) rather than granted an exception, because RULES.md forbids per-op exception lists. Census: **120 of 131** template files hold exactly one box; the rest are SNOBOL4/diagnostic files outside this gate's declared scope.

**Negative-tested 4 ways, all fire:** second box added → FAIL · box removed → FAIL · box added to a helper → FAIL · listed file deleted → FAIL.

### 4b. `test_rtx_unit.sh` faildescr — **a STALE GOLDEN, not an asm defect.** Diagnosed, repaired, negative-tested.

It printed:

```
MISMATCH faildescr asm{v=104,slen=0,i=0} golden{v=104,slen=0,i=0}
```

⛔ **The two sides it printed were IDENTICAL.** The `memcmp` compares all 16 bytes of `DESCR_t`; the report showed three fields. Repairing the report to print every byte gave the answer in one run:

```
bytes asm = 68 82 00 00 …      bytes gold= 68 00 00 00 …      differ at = [1]
```

Offset 1 is `mod_op`. `rtx_misc.S:20` stamps `mod_op = MOD_OP_RT_FAILDESCR` (**130** = 0x82, `descr_tags.inc:70`) **deliberately** — provenance naming which mint produced the descriptor, landed by row `descr-stamp-asm-mints` in **`6ba28e5e`**, *the same commit that cured Milestone 1*. The test compared against the bare C `FAILDESCR` literal, which is unstamped, and so reported an **intentional feature as an asm-vs-C differential red**.

⭐ **This is exactly the red CEO wanted routed before a wave touched `rtx/`**: it was not a real differential, and while it stood, any genuine rtx regression would have landed behind an already-red test. Golden now expects the stamp; the byte-level report is kept because it is what made the diagnosis a one-liner. **`RTX UNIT: ALL PASS`** (21 + 36 + 8,426 + 20 checks). **Negative-tested:** wrong stamp → FAIL at byte [1]; payload regression → FAIL at byte [8].

## 5. RECEIPTS

- Certified list + per-name assignment sites: `SCRIP/scripts/util_switch_census.sh` (minted this session; prints the four sets and attributes every assignment to its tree).
- Gate repair + split: SCRIP `scripts/test_gate_bb_one_box.sh`, `src/templates/bb_binop_relop{,_val}.cpp`, `Makefile`.
- rtx golden: SCRIP `src/runtime/rtx/rtx_unit_test.c`.
- Blocking set at this tree, after `make pristine` (rc=0): `test_gate_emit_no_lang` rc=0 · `test_gate_template_medium_invisible` rc=0 · `test_gate_bb_one_box` rc=0 · `test_rtx_unit` rc=0 · SNOBOL4 corpus — see the LIVE CURSOR line for the measured number.

## 6. WHAT THIS UNLOCKS AND WHAT IT DOES NOT

**Unlocked (CEO-11c step 2):** the delete set is now a certified **302**, with the 48 keeps named, the 9 ZD instruments carved out, and the ZD kill-switch question resolved without an ask to Lon.

⛔ **NOT unlocked:** the waves themselves. `HOLD-until-baseline` stands — hq_P's six-language scoreboard is the acceptance oracle and has not been pinned. Nothing was deleted this session.

⛔ **One keep-class the empirical rule does not cover, flagged for CEO:** several never-set env vars are **documented CLI-flag twins**, not switches — `SCRIP_ZETA_STORAGE` is the env twin of `--zeta-storage=`, which CLAUDE.md documents as the single authority over ζ allocation. Deleting the env twin is correct under "set today" and does **not** delete the flag; deleting the *flag* would remove product surface. The strip must not conflate them, and the four-config selector's own arms are structural, not switches.
