# FINDING — the want-name request rides the activation frame, and the two confirmed snoflake reds flip

**hq_V, 2026-09-09 09:0x–09:2x CDT.** Authored under **CEO-441** (*"YOU AUTHOR the NRETURN want-name class — rt_g_want_name has no nesting; the nesting rides the activation frame or the existing call machinery, NEVER a new global"*). Supersedes the CURE section of `FINDING-2026-09-08-hq_V-want-name-is-a-global-live-across-the-callee-body-so-nreturn-derefs-wrongly-under-a-deferred-target.md`; that file's DIAGNOSIS stands unchanged and is the evidence this cure was built against.

## What was wrong, in one sentence

`rt_g_want_name` is a single global carrying "the caller wants a NAME", and the **role-4/5 per-DEFINE shim** in `src/templates/bb/bb_define.cpp` — the arm that actually compiles a `DEFINE`d SNOBOL4 function, in **both** modes — neither parked it at entry nor put it back at exit, so an inner request raised inside the callee's own body, and cleared by whichever consumer took it, **destroyed the outer request still pending at the call site**; the caller's post-call consult (`bcps_nret_consult` → `rt_nret_fix_tiny`, which reads the live global at RETURN time) then saw `wn=0` and dereferenced a correct `DT_N`.

## Measured at the seam, on the nine-line repro

```
        DEFINE('FLD(ST,I)')             :(FLD_END)
FLD     FLD = .APPLY(FIELD(DATATYPE(ST), I), ST)
+                                       :S(NRETURN)F(FRETURN)
FLD_END
        DATA('PAIR(LEFT,RIGHT)')
        P = PAIR('left','right')
        OUTPUT = DATATYPE(.FLD(P,2))
END
```

Instrumented trace on the **pre-cure** tree (probes reverted before the landing):

```
[WN] WANTNM fired                                  <- outer .FLD(P,2)
[WN] WANTNM fired                                  <- inner .APPLY(...), inside FLD's body
[WN] fieldvar-fastpath-2 consumes+clears RIGHT     <- by_name_dispatch.c ~6672 zeroes the global
[WN] nret_fix_tiny wn=0                            <- the caller's own request is gone
[WN] nret_fix wn=0 rbn=1 rv=40                     <- DT_N dereferenced
```

⛔ **AND THE PART THAT CORRECTS THE 09-08 TASK TEXT.** The baton and the earlier FINDING both name `rt_proc_call_prologue` / `rt_call_proc_descr` / `rt_ab_enter_env` as the site. **They are not on this path at all.** Probes on all four C entry points (`rt_call_proc_descr`, `rt_proc_call_prologue`, `rt_proc_call_open_slim`, `rt_ab_enter_env`) fired **zero times** on this repro in mode 3. The emitted asm names the real path: `FLD_α` is the role-4 SIG shim, its prologue reads `sub rsp, 80` and touches `rt_g_want_name` **nowhere**, and the call site jumps into it directly (`lea rax, [rip + FLD_α]; jmp rax`). `rt_ab_enter_env`'s `AB_OFF_WN` slot — the machinery the earlier note said "already exists and is simply never reached" — belongs to the **sibling** `bb_define_activate()` convention (role 7), which a tiny-shim-eligible DEFINE never enters. So the cure is the same PROTOCOL in the shim that is actually reached, not a re-route onto the C path.

## The cure

`src/templates/bb/bb_define.cpp`, `bb_define_sr()` role 4/5, **both arms** (`fnsig()` on — the default — and the `SCRIP_FN_SIG=0` fallback): a `WNSAVE()`/`WNRESTORE()` pair over an otherwise-unused 8 bytes of the shim's **own activation frame** at `rsp + 16*xt4 + 24` (inside `T4`, disjoint from the saved-GVA area at `16*k`, from the signature pointer at `16*xt4+16`, and from the extra-formals area at `T4+`).

- **Entry** (right after the frame is carved): park `rt_g_want_name` in the slot and zero the global, so the body starts with no inherited intent. `rax`/`rdx` are scratch there; `rcx` (the signature block) and `r8`/`r9` are untouched.
- **Both exits** (γ value-returning and ω failing), after the restore-by-map and before the frame is released: put the parked value back. The failing exit is included deliberately — an unbalanced exit leaks this activation's intent into the caller exactly the way the global did, and that is the same class as the `&FNCLEVEL` omega omission recorded a few lines above it in this file.

**No new global. No new frame bytes** — the slot was already allocated and unused. `rt_g_want_name`, `rt_nret_fix`, `rt_nret_fix_tiny`, `pattern_match.c` and `by_name_dispatch.c` are **unchanged**.

## Fail-once, pass-once, and the board

| | pre-cure tree `01eb996ca` | this landing |
|---|---|---|
| repro, mode 3 | `STRING` | `NAME` |
| repro, mode 4 | `STRING` | `NAME` |
| repro, `SCRIP_FN_SIG=0` (fallback arm) | `STRING` | `NAME` |
| oracle `sbl -bf` | `NAME` | `NAME` |

`test_snoflake_suite.sh` cited before the run per rule 5 — SCORE.md § THE SUITE TABLE, Flake row **113/124 (09-08, `c4b5a1617`)**. Measured on the change alone (SCRIP `01eb996ca` + this diff): **115/124**; re-measured after rebasing onto `b2824175a`, which carried other seats' cures: **117/124**, `both_modes_pass=115/124`, mode-3 PASS=151 FAIL=22, mode-4 PASS=151 FAIL=15 SKIP(cc)=8. The two programs that left FAIL-M3 and FAIL-M4 are exactly **`gimpel-stack-field-functions`** and **`gimpel-l-one-compiler`** — the two CONFIRMED members of the class, verified individually against `sbl -bf` in both modes with the suite's own include staging.

**The two other members are reported as they measure, not rounded up:** `kalah-opening-search` (the CANDIDATE) is **still red** — so this cure is not its cause, and the `CODE()`-subset hypothesis in the 09-08 note is now the live one. `gimpel-linked-list-functions` is **still red**, consistent with its attribution to the twice-`DEFINE`d-name defect under CEO-429, which stays with the cto.

## The control-arm bar (ceo-359)

`bb_define.cpp` role 4/5 is reached by SNOBOL4 lowering only — `lower_prolog.c:1372` merely *reads* `IR_DEFINE` role 3, and no other frontend builds an `IR_DEFINE`. The bar was run anyway, same corpus, comparison tree the clean stamp `01eb996ca`:

- **snobol4** `test_corpus_snobol4.sh` — the same frontend and therefore the real risk arm: **1870/1894**, m3 PASS=1893 **FAIL=0**, m4 PASS=1893 **FAIL=0** SKIP=0, ast 28/28, **xpass=0 in both modes**. Identical to the SUITES.tsv reading. ⭐ The zero XPASS matters as much as the zero FAIL: a cure that quietly turned an xfail green would show here, and none did.
- **icon** `board_icon_master.sh`: **707/707** both modes, watermarks held.
- **pascal** `test_gate_pascal_m3.sh` / `_m4.sh`: m3 **248/251**, m4 **248/251** — the opening baseline, unmoved.
- **prolog** `test_gate_pl_master_board_floor.sh`: GATE PASS, m3 **518**, m4 **439**, floor 230.

Every arm reads the same as the clean tree. The bar is met.

## What this does NOT claim

The request is parked per activation of a **shim-eligible** DEFINE. A call reaching a procedure through `rt_call_proc_descr`'s dyn-scope path still carries the flag across the body the way it always did; nothing on the graded boards exercises that combination today, and it is named here rather than left for the next seat to rediscover.
