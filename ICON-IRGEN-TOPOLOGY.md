# ICON-IRGEN-TOPOLOGY.md — per-construct four-port topology + STATIC/DYNAMIC arrival-depth verdict

**Owner:** `GOAL-ICON-100.md` rung **Z-3** ("Land the topology table ONCE as `.github/ICON-IRGEN-TOPOLOGY.md`
(STATIC/DYNAMIC arrival-depth verdict per kind — subsumes old ICN-FB-1)").
**Minted:** 2026-08-16 s236 (Claude Opus 5).
**Authority:** `refs/jcon-master/tran/irgen.icn` (43 `ir_a_*` procedures) + `refs/icon-master/src/runtime/*.r`.
**Companion:** `JCON-TO-SCRIP-IR-MAP.md` (per-instruction IR→codegen correspondence). This file is the
*port-topology and depth* half; that file is the *instruction* half.

⛔ **THIS TABLE IS DERIVED, NOT TRANSCRIBED.** Every signature column below was extracted mechanically
from `irgen.icn` (one `awk` pass counting the resume-edge IR ops per procedure), and every PASS/FAIL
column was read out of a pinned suite log — never from prose. Re-derive both before trusting them; the
recipe is at the bottom. Line numbers are `irgen.icn` at the archive Lon supplies as `3-jcon-master.zip`.

---

## ⛔ THE DISCRIMINATOR — what makes a box's arrival depth DYNAMIC

A box has **STATIC arrival depth** when every incoming edge to a given label reaches it at the same
compile-time-known spine depth. It is **DYNAMIC** when it does not. From `irgen.icn` exactly three
markers make a construct dynamic, and they are *not* equally dangerous — that is the point of this file:

| id | marker in `irgen.icn` | meaning | danger |
|---|---|---|---|
| **D1** | `ir_IndirectGoto` on the resume edge, target stored by `ir_MoveLabel` | the resume **TARGET** is a runtime value; one label serves several arrival paths | ⚠ benign today — see the measured result below |
| **D2** | `ir_Succeed` | a true **suspension**: the activation must outlive γ | ⛔ the Z-3 defect |
| **D3** | `ir_ResumeValue` (closure across resume) or `ir_ScanSwap` (environment save/restore) | **retained state** outliving the box that carved it | ⛔ the Z-4 defect |

### ⭐⭐⭐ THE MEASURED RESULT — D1 IS NOT THE DEFECT; D2/D3 ARE

Measured at SCRIP `860a9e43` / corpus `e6b95477`, m3, two agreeing runs (s236 cursor for provenance):

- **Pure-D1 constructs (alt · case · every · while · until · repeat · if): 39 PASS / 0 FAIL.**
  The lone `alt` failure in the raw grep is `rung37_scan_alt`, which is **scan-family (D3)**, not a pure D1.
- **D2/D3 constructs: the entire 16-program Z-3+Z-4 fail set**, with no member outside D2/D3.

**Therefore: arrival-depth dynamism ALONE is not the bug. A runtime-variable resume TARGET is already
handled correctly today. What breaks is STATE RETAINED ACROSS γ.** This is a sharper statement than
"generators are dynamic", and it is independently falsifiable — if a pure-D1 rung ever fails, or a
conversion fixes D2/D3 without touching D1, this claim is the thing that predicted it.

### ⭐⭐⭐ FIRST TEST OF THIS CLAIM — s235's SCAN FIX, RE-DERIVED INDEPENDENTLY (s236)

The claim above was written at `860a9e43` **before** s235's Z-3/Z-4 fix landed, so the fix is a genuine
out-of-sample test of it. Re-derived on this seat's own clean clone at SCRIP `4fc01bee` / corpus
`6288c09c` (tree clean, `pgrep scrip`==0, canary rc=0 ×3): **Icon m3 239/24/30**, matching s235's
reported number exactly, **zero new failures** (`comm` against the pinned 28-fail set).

| | at `860a9e43` | at `4fc01bee` | verdict |
|---|---|---|---|
| pure-D1 (alt·case·every·while·until·repeat·if) | 39 PASS / 0 FAIL | **40 PASS / 0 FAIL** | ✅ **CONFIRMED** — still zero, and the one contaminating grep hit (`rung37_scan_alt`, D3) is now a PASS |
| D2/D3 | all 16 failures | 4 fixed, 13 remain ¹ | ✅ locus confirmed — every fix landed on a D3 row |

**The 4 programs fixed:** `rung36_jcon_wordcnt` · `rung37_scan_alt` (both D3-scan, as predicted) —
**plus `rung36_jcon_meander` and `rung36_jcon_mffsol`.**

⭐ **LEDGER CORRECTION FALLING OUT OF THIS:** `meander` was recorded as **Z-3 (D2 suspend)** and `mffsol`
as **Z-5**, but both were in fact **scan-blocked** and fell to a D3 fix. **The recorded 10/6/12
decomposition over-attributed to Z-3 and Z-5.** True remaining decomposition at `4fc01bee` is
**9 D2-suspend / 4 D3-scan (`jcon_scan`, `scan1`, `scan2`, `subjpos`) / 11 Z-5** = 24.

### ⛔ AND WHERE THIS FILE'S FIRST DRAFT WAS WRONG — RECORDED, NOT QUIETLY EDITED

The **locus** claim (D2/D3, never D1) survived. The **remedy** framing it inherited from the goal file —
"the retained cell must move OFF the spine into a ζ-ACTIVATION FRAME" — is **FALSIFIED for the scan
family.** s235's fix was a **DELETION**: `bb_scan_tab.cpp` already addresses its cell as `FRQ(op_off+16)`,
an ordinary flat frame quad **the allocator already grants**, so the `sub rsp,16` was a *second
allocation of a slot that already existed off-spine*. There was never anything to compensate, and
nothing needed moving. ⛔ **Read that as a warning about this whole family of diagnoses:** three
sessions reasoned about how to correctly *compensate* or *relocate* a carve that should simply not have
been emitted. Check for double-allocation before designing a relocation.

⛔ **THE D2 SET IS UNTOUCHED — 9 suspend programs remain and they are the real test of the
activation-frame thesis.** Nothing above licenses assuming they are also a double-allocation; s234's
hand-patch evidence (γ destroys the suspended frame; caller handshake disagrees three ways) is
independent and still stands.

¹ 16 − 4 fixed = 12 D2/D3, plus `mffsol` was a Z-5 row that the D3 fix also cured; the 13 counts the
D2/D3 rows still failing.

---

## THE TABLE — 43 `ir_a_*` procedures

Signature columns are literal op counts inside the procedure. `bR` = has a `/bounded & ... p.ir.resume`
chunk. Verdict per the discriminator above.

| # | JCON `ir_a_*` | line | SCRIP IR kind | IndGoto | MoveLbl | Succeed | ResumeVal | ScanSwap | bR | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | NoOp | 22 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 2 | Field | 33 | — | 0 | 0 | 0 | 0 | 0 | 0 | STATIC |
| 3 | **Scan** | 49 | `IR_SCAN` / `IR_SCAN_ENTER` | 0 | 0 | 0 | 0 | **3** | 1 | ⛔ **DYNAMIC D3** |
| 4 | Limitation | 113 | `IR_LIMIT` | 0 | 0 | 0 | 0 | 0 | 1 | STATIC ¹ |
| 5 | Not | 142 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 6 | CoexpList | 162 | — | 0 | 0 | 0 | 0 | 0 | 0 | n/a ² |
| 7 | **Alt** | 167 | `IR_DISJUNCTION` | 1 | 1 | 0 | 0 | 0 | 1 | DYNAMIC **D1** |
| 8 | **RepAlt** | 202 | `IR_REPALT` | 1 | 2 | 0 | 0 | 0 | 1 | DYNAMIC **D1** |
| 9 | Case | 232 | (→ disjunction) | 1 | 2 | 0 | 0 | 0 | 1 | DYNAMIC **D1** |
| 10 | Every | 309 | — | 1 | 0 | 0 | 0 | 0 | 1 | DYNAMIC **D1** |
| 11 | Sectionop | 334 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 12 | **Call** | 360 | `IR_PROC_GEN` | 0 | 0 | 0 | **2** | 0 | 3 | ⛔ **DYNAMIC D3** |
| 13 | Binop | 472 | — | 0 | 0 | 0 | **1** | 0 | 1 | ⛔ DYNAMIC D3 |
| 14 | Unop | 542 | — | 0 | 0 | 0 | 0 | 0 | 0 | STATIC |
| 15 | Global | 568 | — | 0 | 0 | 0 | 0 | 0 | 0 | STATIC |
| 16 | If | 577 | (→ disjunction ³) | 1 | 2 | 0 | 0 | 0 | 1 | DYNAMIC **D1** |
| 17 | Initial | 621 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 18 | Invocable | 642 | — | 0 | 0 | 0 | 0 | 0 | 0 | STATIC |
| 19 | Link | 662 | — | 0 | 0 | 0 | 0 | 0 | 0 | STATIC |
| 20 | Intlit | 671 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 21 | Reallit | 688 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 22 | Stringlit | 705 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 23 | Csetlit | 719 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 24 | ProcDecl | 733 | — | 0 | 0 | 0 | 0 | 0 | 0 | STATIC |
| 25 | ProcBody | 774 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 26 | ProcCode | 807 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 27 | Record | 826 | — | 0 | 0 | 0 | 0 | 0 | 0 | STATIC |
| 28 | Repeat | 847 | — | 1 | 0 | 0 | 0 | 0 | 1 | DYNAMIC **D1** |
| 29 | **Return** | 867 | `IR_RETURN` | 0 | 0 | **2** | 0 | 0 | 1 | ⛔ **DYNAMIC D2** |
| 30 | Fail | 907 | `IR_FAIL` | 0 | 0 | 0 | 0 | 0 | 2 | STATIC |
| 31 | **Suspend** | 937 | `IR_SUSPEND` | 1 | 0 | **2** | 0 | **2** | 1 | ⛔⛔ **DYNAMIC D1+D2+D3** |
| 32 | Until | 981 | — | 1 | 0 | 0 | 0 | 0 | 1 | DYNAMIC **D1** |
| 33 | While | 1008 | — | 1 | 0 | 0 | 0 | 0 | 1 | DYNAMIC **D1** |
| 34 | Create | 1035 | `IR_CREATE` | 0 | 0 | 0 | 0 | 0 | 2 | STATIC ⁴ |
| 35 | Ident | 1061 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 36 | Next | 1082 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 37 | Break | 1107 | — | 0 | 2 | 0 | 0 | 0 | 0 | STATIC ⁵ |
| 38 | **ToBy** | 1168 | `IR_TO_BY` | 0 | 0 | 0 | **1** | 0 | 0 | ⛔ **DYNAMIC D3** |
| 39 | Mutual | 1202 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 40 | Compound | 1231 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |
| 41 | Key | 1262 | — | 0 | 0 | 0 | **1** | 0 | 1 | ⛔ DYNAMIC D3 |
| 42 | Arglist | 1307 | — | 0 | 0 | 0 | 0 | 0 | 0 | STATIC |
| 43 | ListConstructor | 1313 | — | 0 | 0 | 0 | 0 | 0 | 1 | STATIC |

¹ **Limitation** carries a limit counter across resumptions, but in a **tmp slot**, not a retained spine
cell — its resume chunk is `opfn`+`Goto`, no IndirectGoto. Classed STATIC; flagged because "holds state"
in the loose sense is true of it and the distinction that matters is *where* the state lives.
² `ir_a_CoexpList` is `stop("FATAL ERROR: don't know how to do coexplist")` in JCON — unimplemented
upstream, so JCON is **not** an authority for it. SCRIP's co-expressions landed 2026-07-01 via
pthread+semaphore (`ARCH-ICON.md`); use `refs/icon-master` for co-expression semantics, never JCON.
³ SCRIP retired `IR_INDIRECT_GOTO`: `lower_if` was its only producer and is now a committed
`IR_DISJUNCTION` (`emit.cpp:1227` comment). The kind stays declared and `drive_unowned` aborts LOUD if
one reappears.
⁴ **Create** is STATIC *in JCON's IR*; in SCRIP a co-expression gets its own pthread stack, so the
spine question does not arise. Exempt from the ZK-8 heap-ζ assertion per `GOAL-ICON-100.md` Z-8.
⁵ **Break** has `MoveLabel`×2 but **no** bounded-resume chunk of its own — it writes another
construct's resume label. Classed STATIC as a box; it is a contributor to *someone else's* D1.

---

## THE Z-3 / Z-4 WITNESS SET, MAPPED TO THIS TABLE

Every one of the 16 Z-3+Z-4 failures at `860a9e43` lands on a **D2 or D3** row. None lands on a pure D1.

| witness | construct | row | class |
|---|---|---|---|
| `rung03_suspend_gen` · `_gen_compose` · `_gen_filter` | Suspend | 31 | D2 |
| `rung03_suspend_return` | Suspend + Return | 31 + 29 | D2 |
| `rung36_jcon_recogn` | Suspend (recursive) | 31 | D2 |
| `rung36_jcon_level` | Suspend (depth-per-β) | 31 | D2 |
| `rung36_jcon_genqueen` · `_meander` | Suspend | 31 | D2 |
| `rung37_proc_lookup` · `rung37_subscript_genproc` | Call | 12 | D3 |
| `rung36_jcon_scan` · `scan1` · `scan2` · `subjpos` · `wordcnt` | Scan | 3 | D3 |
| `rung37_scan_alt` | Scan (in an Alt) | 3 | D3 |

---

## CANONICAL PRECEDENT FOR THE FIX (read before Z-3 slice 2)

`refs/icon-master/src/runtime/interp.r`, `Op_Mark` / `Op_Esusp` / `Op_Unmark`:

- `efp` (expression frame) and `gfp` (generator frame) are **two independently chained linked lists** —
  each new marker stores the previous `ef_efp`/`gf_gfp` and becomes the head (`:573-578`, `:619-625`).
- On suspend, Icon does **not** retain a frame in place. It **copies the live region to the stack top**
  (`firstwd`..`lastwd`, `:648-649`) and re-chains `gfp`. The suspended state is relocated, not pinned.
- `Op_Unmark` pops by restoring `rsp` from the marker (`:594-595`), i.e. **release is driven by the
  frame chain, never by a per-box carve count.**

That is precisely the shape ζ-ACTIVATION-FRAME is reaching for, and it is why the per-box
`op_zdepth = op_fc_bytes` model ("a box compensates for exactly what IT carved", `emit.cpp:1000`) cannot
express D2/D3 — a box that legitimately suspends is *not* balanced at handoff.

Scan-family split (do not blur — `ARCH-ICON.md` says the same):
- `fscan.r` `tab` `{0,1+}` (`:91`) and `move` `{0,1+}` (`:9`) — **cursor-movers**, save old `&pos`
  (`:113`) and reverse on resume ⇒ genuinely gamma-live state.
- `fstranl.r` `any` `{0,1}` (`:68`), `match` `{0,1}` (`:203`), `many` `{0,1}` (`:175`) —
  **position-returners**, δ-untouched, **no reversal state**. `upto` `{*}` (`:237`), `find` `{*}`
  (`:133`), `bal` `{*}` (`:86`) are generators that suspend each position.
- ⛔ This is the source-level reason `IR_SCAN_MATCH`'s membership in the carve-retention class
  (`emit.cpp:1236`) looks wrong: `bb_scan_match.cpp` emits `x86_beta_trampoline()` = `β: jmp ω`, a
  det-leaf that reads nothing (s233). But s233 *also* proved releasing it alone regresses
  `rung08_strbuiltins_match` — so match comes out with the other two or not at all.

---

## RE-DERIVE THIS FILE (do not trust the numbers above)

```bash
# signature columns, straight from the canonical archive:
cd /home/claude/SCRIP/refs/jcon-master/tran
awk '/^procedure ir_a_/{if(n!="")e();n=$2;sub(/\(.*/,"",n);sub(/^ir_a_/,"",n);s=NR;b=""}{if(n!="")b=b"\n"$0}
END{if(n!="")e()} function e(){printf "%-16s line=%-5s IG=%d ML=%d SU=%d RV=%d SS=%d bR=%d\n",n,s,
gsub(/ir_IndirectGoto/,"&",b),gsub(/ir_MoveLabel/,"&",b),gsub(/ir_Succeed/,"&",b),
gsub(/ir_ResumeValue/,"&",b),gsub(/ir_ScanSwap/,"&",b),
gsub(/\/bounded & suspend ir_chunk\(p\.ir\.resume/,"&",b)}' irgen.icn

# D1-vs-D2/D3 verdict, straight from a pinned suite log:
grep -icE "^PASS .*(alt|case|every|while|until|repeat|_if_)" suite.log   # pure-D1 passes
grep -icE "^FAIL .*(alt|case|every|while|until|repeat|_if_)" suite.log   # minus scan-family
```

## WHEN TO UPDATE

New `ir_a_*` upstream → new row. A verdict flips → say which measurement flipped it and at which pinned
commit. ⛔ Do not edit a verdict from reasoning alone; this file's whole value is that both halves are
re-derivable in two commands.
