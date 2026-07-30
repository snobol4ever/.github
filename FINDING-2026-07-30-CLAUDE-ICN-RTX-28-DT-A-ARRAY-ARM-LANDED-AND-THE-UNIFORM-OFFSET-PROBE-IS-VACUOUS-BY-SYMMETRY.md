# FINDING s224-ICN — RTX-28-ICN: the `DT_A` array arm landed, and the uniform-offset falsification probe is VACUOUS BY SYMMETRY

**Session s224-ICN, 2026-07-30. Ladder `GOAL-ICON-RTX.md`. Contract `ARCH-ICON-RTX.md`.**
Symbol `rt_subscript_var`, gate `SCRIP_RTX_ICNSUB` (existing — **no new gate, not a gate ledger event**).

---

## 0. WHAT LANDED

`rt_subscript_var`'s **`DT_A` (array) arm** is now assembly — the **fourth** arm on this symbol, beside
RTX-24 (`DT_DATA` list), RTX-26 (`DT_T` table) and RTX-27 (`DT_S` substring trap).

| | before | after |
|---|---|---|
| 0(j) census, 2M-subscript window | 200,001 entries / 200,001 bailed / **0 commits** | 2,000,001 / **0** bailed / **2,000,001 commits** |
| Icon watermark | 252/11/30 | **252/11/30 unmoved** |
| SNOBOL4 m3 | 329/5 | **329/5 unmoved** |
| SNOBOL4 m4 | 324/2 | **324/2 unmoved** |

**Speed: 1.160× median / 1.152× min-min, OVERLAPPING. ⛔ NO DISJOINT SPEED CLAIM.**
`RT_OPT=-O0`, gate ON/OFF interleaved, 10 rounds, warmup discarded. Expectation was stated BEFORE
measuring (1.05–1.20×, widened to 1.05–1.35× after the dominance number below but still before the A/B)
and the result landed inside it. The overlap is one first-round ON outlier (98 ms against 79–84 for the
other nine); the conservative reading is reported deliberately rather than the flattering one.

---

## 1. ⭐⭐ THE ARM WAS DEAD FOR THE EXACT OPPOSITE REASON RTX-24's WAS

The queue listed `DT_A` as *"probably SNOBOL4-only for this symbol — MEASURE before opening."* Measuring
gave something sharper than a yes/no. The arm was taking **200,001 entries and bailing 100% of them**,
and instrumenting `c_rt_subscript_var` to print arriving descriptors showed why:

```
[ARRIVE] base.v=4 base.slen=0 base.p=0x7f9d04e05610 idx.v=6 idx.slen=0 idx.i=3
```

`base.v == 4` is **DT_A, bare** — never the `DT_N` (=9) varref shape. So the traffic died at the very
first pre-frame reject, `cmp edi, DT_N`, before the frame was even built.

⇒ **This is RTX-24's lesson INVERTED, on the same symbol.** RTX-24's first attempt was vacuous because
it *rejected* varrefs when the live traffic was 100% varref. This arm was vacuous because the entry gate
*required* varrefs when the live traffic is 100% non-varref. **Same function, same census tool, opposite
error.** The transferable form is neither "port the arm the guard rejects" nor its opposite — it is:
**the entry gate's shape is an EMPIRICAL question per arm, and the instrument is the arriving
descriptor, not the C source read top-to-bottom.**

A bare `DT_A` also needs **no `rt_deref` call at all**, so every reject in this arm costs a handful of
compares and a tail jump, and the frame exists only to bridge the `rt_agg_alloc` call.

---

## 2. ⭐⭐⭐ THE UNIFORM-OFFSET PROBE IS VACUOUS BY SYMMETRY — AND IT IS RTX-24's OWN RECORDED PROBE

This is the finding that generalizes furthest, and it nearly recorded a false pass.

**Two-sided falsification requires breaking a RESULT, not a route.** The obvious result-break for a
cell-naming port is to shift the computed element address by one — and that is **verbatim RTX-24's
recorded probe** (*"dropped the `dec` so cellp=&elems[i]": ON 22, OFF 11*). I planted the same probe:

```
    movsxd  rax, eax
    inc     rax                         /* FALSIFICATION PROBE: off+1 */
    shl     rax, 4
```

**The board did not move: gate ON printed 22, gate OFF printed 22.**

Per ARCH §8 (*"a silent probe is a QUESTION, not an ANSWER"*) this was escalated rather than recorded.
It was **not** a dead arm:
- `util_rtx_arm_census.sh` on that exact program: **3 entries / 0 bailed / 3 commits.**
- `objdump -d out/rt_pic/rtx_icnsub.o` showed `inc %rax` live at `+0x3c6`.

**THE CAUSE: `rt_subscript_var` serves BOTH the lvalue and the rvalue path, so a uniform shift moves the
WRITE and the READ by the same amount and they still agree.**

```
A<2> = 22    ->  asm names slot (1+1)=2, writes 22 there
OUTPUT = A<2> -> asm names slot (1+1)=2, reads 22 back    => output unchanged
```

**Why RTX-24's identical probe DID work:** its window built the list with a constructor
(`list()`/`put()`) that populates elements **without going through `rt_subscript_var`**. Its write was
therefore unshifted while its read was shifted — asymmetry by accident of the workload, not by design of
the probe.

**THE FIX — AN ASYMMETRIC BREAK.** Collapse every subscript to slot 0 so two *distinct* indices alias:

```
    xor     eax, eax                    /* all subscripts -> slot 0 */
```
```
A<2> = 22 -> slot0 = 22 ;  A<3> = 33 -> slot0 = 33 ;  OUTPUT = A<2> -> slot0 = 33
```
⇒ **gate ON prints 33, gate OFF prints 22.** Two-sided, on a RESULT, non-vacuous.

⛔⛔ **THE RULE, and it is owed to SN4-RTX and PL-RTX as well as this ladder: A UNIFORM-OFFSET PROBE IS
NOT A FALSIFICATION INSTRUMENT ON ANY SYMBOL THAT BOTH READS AND WRITES THE CELL IT NAMES.** The probe
must make two distinct inputs collide, or make an in-range access go out of range — something the
read/write pair cannot cancel. This applies to every `NAMETRAP`-minting symbol either ladder ports:
`rt_assign_var`, `rt_field_var`, `rt_list_bang_var_at`, and the rest of `rt_subscript_var`'s arms.
**Recorded on the message board, because RTX-24's write-up currently advertises the vacuous probe as the
one that worked.**

---

## 3. ⚠ THIS ARM'S INDEX RULE IS THE THIRD DISTINCT ONE IN ONE FUNCTION

The goal file already warned that the `DT_S` arm wraps on `i <= 0` while the `DT_DATA` arm wraps on
`i < 0` — *"two arms, two rules, one function. Do not 'tidy' that."* It is now **three**:

| arm | rule |
|---|---|
| `DT_DATA` list | `i < 0` ⇒ `i = n + i + 1` (wraps) |
| `DT_S` string | `i <= 0` ⇒ `i = slen + 1 + i` (wraps) |
| **`DT_A` array** | **NO WRAP AT ALL.** `off = i - a->lo`; fail if `off < 0 \|\| off >= hi-lo+1` |

A negative subscript on an array simply goes out of range and fails. Regression-tested explicitly
(`A<-1>` on a 5-element array must FAIL, not alias `A<5>`), because a "tidying" refactor that unified
the three would be silent, would pass every in-range test, and would corrupt exactly the edge.

⚠ **`ndim != 1` BAILS.** The C body does not consult `ndim`, so a 2-D array subscripted with ONE index
takes C's flat path. Bailing preserves that exactly — a bail re-enters the same C body — while keeping
the arm's arithmetic honest about what it has proven. Verified: `C = ARRAY("3,4"); C<2,3>` is ON==OFF.

---

## 4. ⭐⭐ RTX-25's PREMISE NOW HOLDS ON A FOURTH ARM — AND THE CEILING IS VISIBLE IN THE NUMBERS

`rt_agg_alloc` fires **2,000,001 times** in the array window: one thrown-away 72-byte `VCELL_t` per
rvalue subscript, on **list, table, string AND array**. Canonical Icon does not allocate to fetch an
element — `refs/icon-master/src/runtime/oref.r:639`, the `list:` arm of `operator{0,1} [] subsc`, returns
`struct_var(&bp->lelem.lslots[i], bp)`, a pointer into the existing block. (Its `table:` arm legitimately
allocates, via `alctvtbl` — which is why RTX-26's table arm is the one place the carve is canonical.)

**The four arms now form a clean measured series, and it is a statement about WINDOWS, not about asm:**

| arm | ratio | what dominated the window |
|---|---|---|
| RTX-26 `DT_T` | **1.569× disjoint** | hash + `strcmp` chain walk |
| RTX-24 `DT_DATA` | **1.376× disjoint** | two `strcmp` per subscript (the RTX-13 by-name disease) |
| **RTX-28 `DT_A`** | **1.160× overlapping** | **allocation — there is no hash and no strcmp to remove** |
| RTX-27 `DT_S` | 1.132× overlapping | allocation ×2 (substring trap derefs a 1-char string) |

⇒ **The array arm is the cheapest-dispatch arm of the four, so it has the least C work to delete and
sits nearest the allocation floor.** Its (d2) window dominance is genuinely high — 104 ms with the
subscript vs 23 ms with it deleted, **~78%** — so the modest ratio is NOT a window artifact and NOT a
refusal of the asm. It is the allocation, measured a fourth time. **RTX-25 remains the rung that
dominates this whole family by construction, and this is now the fourth independent measurement saying
so.**

---

## 5. LEDGER

- ⭐ **`rt_frame` FATAL CLOSED** — the gate's last remaining fatal, handed to ICON-RTX explicitly by
  s221-PL (*"Not my row"*). Re-derived, not inherited: no dynamic definition in `libscrip_rt.so`, and the
  only two textual references in the whole tree are COMMENTS recording its removal
  (`src/driver/scrip.c:1564`, `src/contracts/zeta_choices.h:61`). ⇒ **Eradicated at RUNG ZS-1 s57** when
  the main ζ frame moved from an arena memo to the driver's own stack. Row now
  `NOT-A-TARGET:ERADICATED-AT-ZS-1-s57` **with the cause named, not just the symptom.** Gate went
  **3 fatal → 2**.
- ⛔ **The remaining 2 fatals are SN4-RTX's and I did not touch them.** `rt_defer_open` /
  `rt_defer_close` are already assembly with non-`DONE` rows — check 3, STALE-PORTED, precisely the
  disease 0(e) exists to prevent. Hard rule 1 is *one symbol one owner, including "I'm only reading it."*
  Message-board entry filed asking them to set the rows or release them.
- ⚠ **Layout pinned, not assumed.** `DT_A == 4` verified present in `rtx_abi.inc:62` before use (s222
  proved an undefined tag compare assembles cleanly as a relocation and admits the wrong datatype
  silently). `ARBLK_t` size + `lo`/`hi`/`ndim`/`data` offsets pinned by new `_Static_assert`s in
  `rtx_init.c`, matching the file's existing discipline.

---

## 6. WHAT I DID NOT DO, AND WHY

- **RTX-25-ICN NOT opened**, despite Lon's *"all your choices"* grant this session. It is
  (a) explicitly a **DESIGN rung, not an asm port** — against the session's stated "just ASM" directive —
  and (b) **template territory**, which fires `.s` regen ×3 and collides head-on with the concurrent
  ICON-BB ζ ladder. The grant is discretion over MY ladder; it does not dissolve a live **coordination**
  hazard involving another session's files. **Still `⛔ SERIALIZE WITH LON`.**
- **Nothing pushed — no credential this session.** Per `RULES.md` this handoff is **INCOMPLETE**, stated
  plainly and not dressed up. Also: the clone was `--depth=1`, so the s202 ancestry check
  (`git rev-list --count origin/main..HEAD`) is **not satisfiable** until the repo is unshallowed.
  ⛔ Per `RULES.md` s47 rule (a) no push-status banner is written into any goal file — `handoff_status.sh`
  is the only ground truth.

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
