# FINDING 2026-08-19 s146 — KW-1 CENSUS: THE KEYWORD TRUTH TABLE, AND WHAT SCRIP ACTUALLY DOES

**Seat:** claude.ai web (Claude Opus 5), dispatched to `GOAL-SCRIP-HQ.md` **D-3 KW-STATIC, TOP #1**.
**Rung:** KW-1 (census every special-case + every `kw_*` static + every reader in runtime C; oracle-probe each bare name for the shadow class).
**Build:** SCRIP `abd79832` (clean `make -j8 scrip` + `make libscrip_rt`), corpus `0250ca0a`, oracle `x64/bin/sbl`.
**Witnesses minted:** `corpus/probe/kw/{kw_bare_shadow,kw_defaults,kw_datatypes,kw_protected_write}.{sno,ref}` — every `.ref` from live `sbl -b`.
**Method:** oracle-probe first, source second. Every claim below is a measured diff, not a reading.

---

## 0. HEADLINE — FOUR DEFECT CLASSES, ALL FOUR PROBES DIFF

| class | what | scale |
|---|---|---|
| **A — BARE-NAME SHADOW** | 14 unprefixed names hijacked as keywords before the variable table | 13 of 14 wrong |
| **B — WRONG INITIAL VALUES** | keyword defaults disagree with the oracle | 6 wrong, 5 missing entirely |
| **C — CSET LEAK** | `&UCASE`/`&LCASE` return a CSET; SNOBOL4 has no cset datatype | 2 wrong |
| **D — PROTECTION UNENFORCED** | protected keywords accept assignment silently; error 209 never raised | the whole Ch.16 distinction absent |

Class D is the structural one: **SCRIP does not implement the protected/unprotected split at all**, which is the organizing concept of manual Chapter 16.

---

## 1. THE LAW (SPITBOL manual Ch.16 "Keywords", pp.187-191)

> *"Special variables called keywords allow a program to communicate with SPITBOL. **Their names are set apart from other variables by the unary operator ampersand (&).** Protected keywords cannot be changed by a program, while unprotected keywords can."* — p.187

That one sentence decides Class A. A bare `ANCHOR` is **an ordinary variable** with no keyword meaning; only `&ANCHOR` is the keyword. Oracle agrees exactly (§2).

**PROTECTED** (read-only repositories; assignment ⇒ error 209): `&ABORT &ALPHABET &ARB &BAL &FAIL &FENCE &FILE &FNCLEVEL &LASTFILE &LASTLINE &LASTNO &LCASE &LINE &REM &RTNTYPE &STCOUNT &STNO &SUCCEED &UCASE`
**UNPROTECTED** (settable integers): `&ABEND &ANCHOR &CASE &CODE &COMPARE &DUMP &ERRLIMIT &ERRTEXT &ERRTYPE &FTRACE &FULLSCAN &INPUT &MAXLNGTH &OUTPUT &PROFILE &STLIMIT &TRACE &TRIM`

Error codes (manual p.277 list, oracle-confirmed): **208** *Keyword value assigned is not integer* · **209** *Keyword in assignment is protected* · **210** *Keyword value assigned is negative or too large* · **211** *Value assigned to keyword ERRTEXT not a string*.
⚠ **ORDER MATTERS, MEASURED:** `&ALPHABET = 'x'` raises **208, not 209** — the integer-value check fires BEFORE the protection check. A KW-2 implementation that checks protection first will be oracle-wrong on this witness.

---

## 2. CLASS A — THE BARE-NAME SHADOW (`kw_bare_shadow`)

`NV_GET_fn` (`src/runtime/core/core.c:2199-2213`) intercepts 14 bare names **before** the variable-table lookup. Oracle returns the null string for every one; SCRIP returns keyword integers.

| bare name | oracle | SCRIP m3 |
|---|---|---|
| `STCOUNT` `STNO` `ANCHOR` `TRIM` `FULLSCAN` `CASE` `FTRACE` `TRACE` `ERRLIMIT` `CODE` `FNCLEVEL` | `` (null) | `0` |
| `STLIMIT` | `` (null) | `-1` |
| `MAXLNGTH` | `` (null) | `524288` |
| `RTNTYPE` | `` (null) | `` ✓ (only correct one) |
| `DATATYPE(STCOUNT)` | `STRING` | `INTEGER` |

The write half is symmetric: `NV_SET_fn` (core.c:2254-2255) and `ASGNIC_fn` (core.c:2376+) capture the same bare names on assignment.

**s145 precedent:** the bare-`ALPHABET` member of this family was already gated OFF behind `SCRIP_SEED_NAMES` as the M1-R0 bridge, with an in-source note naming KW-STATIC as the structural fix. **This census supplies the other 14.** The `ALPHABET` special-case at core.c:2213 is a *second* hijack site for the same name.

⚠ Beauty is NOT hit by this class — all 14 names appear in `beauty.sno`/`XDump.inc` only inside string literals and an `IDENT(objType,'CODE')`, never as bare variable reads. Consistent with the FINDING-s145 §4 exclusion list; **this class is not the B1 wall.**

## 3. CLASS B — WRONG INITIAL VALUES (`kw_defaults`)

| keyword | oracle | SCRIP m3 | note |
|---|---|---|---|
| `&TRIM` | **1** | 0 | ⚠ manual p.191 says "initially zero" — **the oracle disagrees with its own manual; oracle wins** (RULES.md). Affects every line read from a file. |
| `&CASE` | **1** | 0 | SCRIP also errors on assignment ("case-sensitive only") |
| `&FULLSCAN` | **1** | 0 | manual: exhaustive scan IS the default; setting 0 is an error |
| `&MAXLNGTH` | **16777216** | 5000000 | manual says 4194304; **oracle is 16777216** — and `kw_maxlngth` is a THIRD value, 524288 |
| `&STLIMIT` | **2147483647** | -1 | |
| `&ERRTYPE` | **0** | *(missing)* | |
| `&ABEND &INPUT &OUTPUT &PROFILE &COMPARE` | 0,1,1,0,0 | *(all missing)* | not implemented at all |

Correct today: `&ANCHOR &CODE &DUMP &ERRLIMIT &FTRACE &TRACE &FNCLEVEL &RTNTYPE &ERRTEXT`.

**These are the values the KW-2 `.data` block must be born holding.** Do not copy today's C initializers — they are wrong in six places.

## 4. CLASS C — THE CSET LEAK (`kw_datatypes`)

`&UCASE`/`&LCASE` route to `kw_read()` → `make_kw_cset(...)` → `CSETVAL`. **SNOBOL4 has no cset datatype** — cset is Icon's. Oracle: `STRING`, size 26. SCRIP: `CSET`, size 26.

Root cause is structural: `kw_read()` (`src/runtime/keywords.c:92`) is a **shared Icon+SNOBOL4 table** — `&window`, `&lpress`, `&errornumber`, `&pi` sit beside `&anchor`, `&stcount`. `rt_keyword_read_snobol4` special-cases `alphabet`/`digits`/`ht`/`lf`/`cr`/… ahead of it (which is why `&ALPHABET` is correctly a STRING) but **does not** cover `ucase`/`lcase`, so those fall through to Icon's cset arms.
⛔ KW-2 must give SNOBOL4 its own block and must NOT "fix" `kw_read` in place — Icon legitimately wants csets there. Same discipline as the `IR_COERCE_NUMERIC` ruling in R-3(g)(d): touch the SNOBOL4 edge only.

## 5. CLASS D — PROTECTION IS NOT ENFORCED (`kw_protected_write`)

| statement | oracle | SCRIP m3 |
|---|---|---|
| `&STCOUNT = 5` | fails, errtype **209** | **succeeds silently** |
| `&ALPHABET = 'x'` | fails, errtype **208** | **succeeds silently** |
| `&FNCLEVEL = 3` | fails, errtype **209** | **succeeds silently** |
| `&ANCHOR = 1` | succeeds, reads back 1 | succeeds ✓ |

`rt_keyword_write_snobol4` (`keywords.c:279`) has **no protection check whatsoever**: it recognizes 7 unprotected names, silently ignores 4 more, and sends everything else — including every protected keyword — to `NV_SET_fn`, creating an ordinary variable. KW-2's block must carry a per-keyword protected bit and raise 208/209/210/211 in the oracle's order.

---

## 6. SPELLED-TWICE DISEASE — TWO PARALLEL KEYWORD STATE FAMILIES

The census's structural find. **Every integer keyword is spelled twice**, in two files, with two different owners and two different values:

| fact | family 1 (`keywords.c`) | family 2 (`core.c`) | agree? |
|---|---|---|---|
| `&ANCHOR` | `g_anchor` (static, alias `rt_anchor_g`) | `kw_anchor` | both 0 ✓ |
| `&MAXLNGTH` | `g_maxlngth` = 5000000 | `kw_maxlngth` = 524288 | ✗ **DISAGREE** |
| `&STLIMIT` | literal `-1` in `kw_read` | `kw_stlimit` = -1 | ✓ |
| `&TRIM` | `g_trim` | `kw_trim` | both 0 |
| `&STCOUNT`/`&STNO` | `g_stcount`/`g_stno` | `kw_stcount`/`kw_stno` | ✓ |
| `&TRACE`/`&FTRACE`/`&CODE`/`&ERRLIMIT`/`&FULLSCAN`/`&FNCLEVEL` | `g_trace` (+ literals) | `kw_ftrace` `kw_code` `kw_errlimit` `kw_fullscan` `kw_fnclevel` | mixed |

**Which family a read reaches depends on HOW you spell the read:**
- `&ANCHOR` → `rt_keyword_read_snobol4` → `kw_read` → **`g_anchor`**
- bare `ANCHOR` → `NV_GET_fn` → **`kw_anchor`**
- `&ANCHOR = 1` → `SNO$KWSET` → `rt_keyword_write_snobol4` → **`g_anchor`**
- bare `ANCHOR = 1` → `NV_SET_fn` → **`kw_anchor`**

`kw_*` is written by `ASGNIC_fn`, whose ONLY caller is `src/driver/driver_call.c:238`. So in a normal compiled program the `kw_*` family is **write-dead and read-live** — a shadow set of stale zeros feeding `NV_GET_fn`.

**One live template still reads the stale family:** `bb_match_advance.cpp:20` emits `[rip + kw_anchor]` — the *unanchored-retry* decision — while the real `&ANCHOR` lives in `g_anchor`. **NOT currently a bug, because `bb_match_advance()` is DEAD:** `IR_MATCH_ADVANCE` is never produced by any lowerer; it survives only as a range endpoint (`op <= IR_MATCH_ADVANCE`) in `emit.cpp:2197/3449` and `optimizer.c:28`, and nothing dispatches the template. The live retry bump is inlined in `bb_match_begin`'s β, which correctly reads `rt_anchor_g` (verified in emitted `.s`). **Route `bb_match_advance` deletion to R-7 dead-code**; it is the last template-layer reference to `kw_anchor` and must go before KW-4 can delete the family.

---

## 7. THE CURRENT COST — WHAT KW-STATIC REPLACES (measured from emitted `.s`)

**Read** (`bb_keyword_snobol4.cpp`): every `&KW` read emits a rip-relative pointer to the keyword's *name string* plus `call rt_keyword_read_snobol4@PLT`, which lowercases into a 64-byte stack buffer and walks a **strcmp cascade of ~60 arms** (9 SNOBOL4 special-cases, then `kw_read`'s shared table), then may fall through to `NV_GET_fn` and a hash lookup.

**Write**: `&KW = v` does not even get a template — it lowers to a **builtin call by name**: `.string "SNO$KWSET"` → `rt_call_arr@PLT` → `to_cstring(args[0])` → `rt_keyword_write_snobol4` → a second strcmp cascade. Verified in `anchor2.s` (this session).

Both collapse to a single `[rip+disp]` under KW-STATIC, per Lon's ruling.

---

## 8. THE KEYWORD BLOCK — PROPOSED SHAPE FOR KW-2 (design input, not yet landed)

One `.data` block per emitted program, bound once in the main prologue via `rt_kw_bind(&block)` (the `gva_register` precedent — **no new global**; the block is program-owned storage, and the runtime holds the bound pointer that Lon's in-chat KW-STATIC grant covers).

- **integer keywords** — one quad each, born holding the §3 oracle-true values.
- **`&ALPHABET`** — 256 bytes inline + a DESCR pointing at it (already correct as a STRING; the KW-2 block subsumes the `core.c:2213` hijack).
- **`&UCASE`/`&LCASE`/`&RTNTYPE`/`&ERRTEXT`** — string DESCRs (fixes Class C by construction).
- **protected-pattern cells** — `&ARB &BAL &REM &FAIL &FENCE &ABORT &SUCCEED` (oracle: all PATTERN in both engines; s145 HQ probe already confirmed the bare forms stay registered).
- **a protected bit per entry** — so the write path raises 208/209/210 in the oracle's order (§1) without a name compare.

`&STNO`/`&STCOUNT`/`&LASTNO`/`&FNCLEVEL` are runtime-maintained; the block holds them but `rt_stmt_enter`/call-return sites write them through the bound pointer.

---

## 9. NEXT SEAT — PICK UP EXACTLY HERE

1. **KW-2** — emit the block + bind + runtime indirection behind a killswitch (`SCRIP_KW_STATIC`, default OFF until gated). Bake §3's oracle-true defaults, §1's protected bits, §1's 208-before-209 order. BOTH-MEDIUM; TEMPLATE-ONLY.
2. **KW-3** — retarget `bb_keyword_snobol4` reads to `[rip+disp]`; give `&KW =` a real template instead of the `SNO$KWSET` by-name builtin call.
3. **KW-4** — delete the `NV_GET_fn`/`NV_SET_fn`/`ASGNIC_fn` bare-name family (§2), the `kw_*` statics (§6), and the `SCRIP_SEED_NAMES` ALPHABET bridge; gates + md5 blast radius.
4. **Route to R-7:** `bb_match_advance()` + `IR_MATCH_ADVANCE` are dead — delete (§6).
5. ⚠ **Class B is a behaviour change with real blast radius** — `&TRIM=1` and `&FULLSCAN=1` alter input handling and scanning for every program. Land it with the killswitch A/B and a BY-SET old-vs-new over crosscheck+patterns+probe, ZERO PASS→fail, exactly as s145 did.

**Gate for all four rungs:** `bash scripts/test_gate_kw_static.sh` (added this session) — runs `corpus/probe/kw/` in both modes against the oracle refs. Measured baseline this session: **0 PASS / 8** (4 witnesses × 2 modes). KW-4 is not done until it reads 8/8.
⭐ **m3 ≡ m4 on all four witnesses** — every failure is byte-identical across modes, so this whole defect set lives in the shared runtime/lowering path, NOT in either emitter medium. That is good news for KW-2: the fix has one home.

---

# ADDENDUM — KW-2 LANDED THE SAME SESSION (SCRIP `bf7e25bb`, corpus `afd0fda8`)

The census above is the measurement record; this is what was built on it.

## The design decision that mattered
The block homes each keyword **at the cell its consumer already reads**, not at a fresh copy. §6 measured the disease as *two* spellings of every integer keyword; a block with its own storage would have made *three*. Homing at the consumer's cell means the block does not add a spelling — it makes the one surviving spelling be the cell that the consuming code actually tests. `rt_kw_bind()` therefore already exists as the KW-3 seam: reads and writes go THROUGH a bound pointer today, so emitting the block into the program's `.data` is a pure relocation of storage.

## It immediately paid for itself: `&TRIM = 1` DID NOTHING
Not stale state — a **live defect**, invisible to any test that only reads the keyword back. The write landed in `g_trim`; the input path tested `kw_trim`. `&TRIM` reported 1 and never trimmed a line. Homing `&TRIM` at `kw_trim` is the whole fix. Witness `probe/kw/kw_trim_effect` (ships a `.dat` as stdin — the gate now feeds `<name>.dat` when present).

## Status by class
| class | armed result |
|---|---|
| **A** bare-name shadow | **closed**, read (`NV_GET_fn`) AND write (`NV_SET_fn`) halves gated together so they cannot disagree. Gated, not deleted — KW-4 deletes after measuring. |
| **B** wrong initial values | **closed** — oracle-true, not copied from the C initializers |
| **C** cset leak | **closed** — `&UCASE`/`&LCASE` STRING; `kw_read` untouched so Icon keeps its csets |
| **D** protection | **enforced** — 209 protected / 208 non-integer, in the oracle's order. Witness still red: see below. |

## Gates
- **killswitch byte-identity 529/529** mode-4 `.s` md5 unchanged (stash-rebuild A/B). Zero template/emitter/lower files touched — as §0's `m3 ≡ m4` finding predicted, the whole fix had one home.
- **by-set blast radius: 802 rows** (crosscheck + probe + benchmarks, m3), **712 → 715 PASS, ZERO PASS→fail**, 3 movers all the intended witnesses.
- **witness gate 0/10 legacy → 6/10 armed**, m3 ≡ m4 on every row.

## ⛔ THE REGRESSION THE WITNESS GATE MISSED AND THE BY-SET A/B CAUGHT
Seeding runs **lazily at the first keyword touch**, not at program start. Initializing PROTECTED entries therefore **rewound the live `&STNO`/`&STCOUNT` counters**, taking `crosscheck/keywords/082_keyword_stcount` PASS→FAIL. Fixed: protected repositories are never initialized — they own their value, the block only reads it.
**Standing lesson for KW-3/KW-4: a small witness gate does not substitute for the by-set A/B.** Both were run; only the second saw this.

## Still red — routed, not taken
- **`kw_protected_write`** needs the **`&ERRLIMIT` → statement-failure** mechanism. SCRIP does not have it at all: `kw_errlimit` is a dead static, nothing converts an error to statement failure, and the terminating error-report format differs from the oracle's block. **Its own rung (KW-5 / ERRLIMIT), independent of KW-STATIC.**
- **`kw_bare_shadow`'s last two lines** — `DATATYPE(<unset variable>)`. HQ's B1; handed over below, not taken.

## ⭐ HANDOFF TO HQ — B1 LOCALIZED, AND `DATATYPE` IS INNOCENT
Witness `probe/kw/kw_unset_datatype.{sno,ref}`, found while clearing class A. Four lines separate the defect from its neighbours: a **null literal**, an **assigned null**, and a **non-null string** are ALL correct in SCRIP today; **only an UNSET VARIABLE differs** (oracle STRING, SCRIP NULL). So s145's suspect is sharper than "DATATYPE(null) = NULL": **DATATYPE is innocent — the wrong datum is the descriptor an unset variable yields**, carrying a distinct NULL tag instead of being the null string manual p.24 gives every fresh variable. **Reads identically on both killswitch arms**, confirming it is not keyword-related. `ShiftReduce.inc` calling `DATATYPE` ×2 remains why this reaches beauty.

## Next
**KW-3** (emit block into `.data`, bind in main prologue, retarget `bb_keyword_snobol4` to `[rip+disp]`, give `&KW =` a real template instead of the `SNO$KWSET` by-name call) — **not opened this session**, deliberately: it is a codegen change in both media requiring regens ×3 and the full gate set, and END-OF-CONTEXT LAW forbids opening what cannot be closed. The seam is in place and the semantics are proven, so it starts from a clean base.
⚠ **Flipping the killswitch default to ON is its own gated step** — class B changes `&TRIM`/`&FULLSCAN` behaviour for every program; the 802-row A/B is the evidence required.

---

# ADDENDUM 2 — BEAUTY IS UNAFFECTED BY KW-STATIC (an EXCLUSION for HQ, measured)

Ran beauty's self-host (`beauty.sno < beauty.sno`) on BOTH killswitch arms, both modes, against the KW-2 build (SCRIP `5510ea8c`):

| mode | arm | rc | stdout | verdict |
|---|---|---|---|---|
| m3 | legacy | 139 (SIGSEGV) | 7 lines | — |
| m3 | `SCRIP_KW_STATIC=1` | 139 (SIGSEGV) | 7 lines | **byte-identical to legacy** |
| m4 | legacy | 0 | 10 lines: 7-line header byte-true, then beauty's own `Parse Error`, then `START` | — |
| m4 | `SCRIP_KW_STATIC=1` | 0 | same 10 lines | **byte-identical to legacy** |

**This reproduces the s145 wall description exactly** (m4: header byte-true then beauty's OWN `Parse Error`, rc=0 no crash; m3: same prefix then SIGSEGV) — an independent confirmation on a different build that s145's two walls are still where s145 left them, and that KW-2 did not move, mask, or worsen either.

**What this EXCLUDES, and it is worth having:** none of the four keyword defect classes is on beauty's B1 or B2 path. Not the bare-name shadow (already argued from source in §2 — the 14 names appear in beauty only inside string literals and an `IDENT(objType,'CODE')` — and now confirmed by execution), not the wrong initial values (including `&TRIM`/`&FULLSCAN`, which change input handling and scanning for every program and still change nothing here), not the cset leak, not the missing protection. **HQ can strike the whole keyword family off the B1/B2 suspect list.**

⚠ The exclusion is honest but bounded: beauty dies 7 lines into 622, so this measures only the prefix that executes. A keyword defect in the unreached remainder would not show up here. What is proven is that keywords are not what STOPS it.

**Where B1 does point, from this session:** `probe/kw/kw_unset_datatype` — an unset variable yields a NULL tag instead of the null string (oracle STRING, SCRIP NULL), with the null literal, the assigned null, and the non-null string all already correct. Identical on both arms, so it is not keyword-related. That is the live suspect; the keyword classes are not.
