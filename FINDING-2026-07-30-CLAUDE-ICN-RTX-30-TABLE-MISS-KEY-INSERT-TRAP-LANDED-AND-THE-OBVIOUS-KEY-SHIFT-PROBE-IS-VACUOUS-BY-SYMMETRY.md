# FINDING-2026-07-30-CLAUDE-ICN-RTX-30-TABLE-MISS-KEY-INSERT-TRAP-LANDED-AND-THE-OBVIOUS-KEY-SHIFT-PROBE-IS-VACUOUS-BY-SYMMETRY.md

**Session:** s225-ICN  
**Rung:** RTX-30-ICN — `rt_subscript_var` table MISS / key-insert trap  
**Gate:** `SCRIP_RTX_ICNSUB` (sixth arm on existing gate, no new gate)  
**SCRIP commit:** `b85f0303`  
**corpus commit:** `b5c3c0f0`

---

## 1. What landed

The chain-exhausted edge of the `DT_T` table walk in `rtx_icnsub.S` no longer
bails to `c_rt_subscript_var`. It mints C's key-INSERT trap in assembly:

```
vc->cellp = 0;  vc->tbl = tb;  vc->key = rt_ws_strdup_c(ks);
vc->key_d = idx; vc->sv = FAILDESCR; vc->pos = 0; vc->len = 0;
return NAMETRAP(vc);
```

One arm `.Lsub_tbl_miss` serves **both** key shapes — DT_S and RTX-29's DT_I
— because both arrive at `.Lsub_hash_init` as a NUL-terminated string in `rdi`.
`t[i] := v` on a fresh integer key was covered at no extra cost.

---

## 2. Measurements

**Window:** `bench_icnsub_table_miss_dispatch.icn` — 2,000,000 RVALUE misses
on a constant key in a constant-size table. The rvalue miss mints the trap,
`rt_deref` resolves via `table_get_found` (returns the table default), and the
table never grows. Per-access cost is constant throughout the run.

**0(j) arm census:**

| | entries | bailed | commits |
|---|---|---|---|
| **before RTX-30** | 200,001 | 200,001 | **0** |
| **after RTX-30** | 2,000,001 | 0 | **2,000,001** |

**A/B — 10 interleaved rounds, round 0 (hugepage warmup) discarded, RT_OPT=-O0:**

| round | ON (ms) | OFF (ms) |
|---|---|---|
| 1 | 140 | 162 |
| 2 | 145 | 179 |
| 3 | 143 | 164 |
| 4 | 140 | 169 |
| 5 | 148 | 160 |
| 6 | 139 | 212 |
| 7 | 194 | 164 |
| 8 | 136 | 162 |
| 9 | 140 | 157 |
| 10 | 140 | 158 |

**ON median 140 ms · OFF median 163 ms → 1.164× median / 1.154× min-min,
OVERLAPPING — ⛔ NO DISJOINT SPEED CLAIM.**

Expectation was stated in the arm's header *before* measuring (1.05–1.20×,
overlapping expected) and the result fell inside it.

**(d2) window dominance ~94%:** subscript present 140 ms, identical loop with
subscript deleted 8 ms. The ratio is the allocation floor, not a window
artifact. This arm calls **both** `rt_agg_alloc` and `rt_ws_strdup_c` — twice
the allocation of any previously landed arm — which is why the ceiling is lower
than RTX-29's 1.296×.

---

## 3. Watermarks

**Icon: 252/11/30 — unmoved.** Re-derived from a pristine stash *before* the
edit and again after.

**SNOBOL4: NOT FULLY CONFIRMED THIS SESSION.** Mode-4 ran to 332/2 against a
documented 324/2; mode-3 did not complete within context budget. No pristine
SNOBOL4 baseline was taken before the edit. **The SNOBOL4 watermark pair must
be re-derived from a pristine build at the start of the next session before
this rung can be declared watermark-clean on SN4.**

**Prolog:** harness fails identically ON and OFF (pre-existing environmental,
third consecutive session). Differential is an identity; not this rung's.

---

## 4. Falsification

**Two-sided, asymmetric result break.**

The obvious probe — corrupting the strdup'd key pointer by one byte — was
**reasoned vacuous by symmetry before use**: the insert stores under the
corrupted key, and the readback's miss re-corrupts identically, so
`table_get_found` finds it again and the board does not move. This is the s224
symmetry trap (ARCH-ICON-RTX.md §8 amendment 1) applied one arm over; the
lesson generalises to every lookup where the write and read both pass through
the same key-formatting path.

Instead: zeroed `vc->tbl` in the arm (`mov qword ptr [rax + VCELL_TBL], 0`).

| | output line 1 | line 2 | line 3 |
|---|---|---|---|
| **Probe, gate ON** | `0` | `0` | *(absent)* |
| **Probe, gate OFF** | `111 22 77 33 99 0 0` | `12502500` | `12502577` |

Gate ON collapses all insert results to `0`; gate OFF is byte-identical to
correct. The asm provably executes and the switch switches.

---

## 5. ⭐⭐ Finding: the obvious key-shift probe is vacuous by symmetry here

Recorded so it is not re-built. A probe that shifts the computed key address
by one byte looks like a clean result break but is **self-concealing under
the semantics of deferred insert**:

1. At subscript time, the miss arm strdup's the (corrupted) key and stores it
   in `vc->key`.
2. At write time, `rt_assign_var` calls `table_set_descr_keyown(vc->tbl,
   vc->key, vc->key_d, val)`, which hashes and inserts under the corrupted key.
3. At the next readback `t["absent"]`, the miss arm re-corrupts the same probe
   key by the same offset, re-hashes identically, and `table_find_pair` finds
   the entry — returning the value that was stored.

Board: unmoved. Census: 2,000,001 commits. Output: correct. The probe looks
like a pass. **It is not a pass; it is a vacuous probe.** The failure degrades
to silence because the same corruption touches both the write-path key and the
read-path key.

**Generalisation (complement to s224 §8 amendment 1):** any port whose commit
path is gated on a key that is consumed symmetrically by both the WRITE and the
READ side cannot be falsified by corrupting that key. Use a result-field break
that is asymmetric with respect to the read-write pair.

---

## 6. Canonical Icon confirms the design

`refs/icon-master/src/runtime/oref.r`, operator `[]` subsc, table case:

> *"Return a table element trapped variable representing the result; defer
> actual lookup until later."*

The chain link happens in `oasgn.r:tvtbl_asgn` at **write time**, which
re-runs `memb()` to handle concurrent inserts. An eager bucket insert at
subscript time would not be an optimisation — it would be wrong semantics in
both models. `t[k]` alone must not grow the table.

---

## 7. GC safety ordering — non-incidental

The field store order in `.Lsub_tbl_miss` is C's exact order and is
load-bearing for GC correctness:

1. Carve the VCELL (`rt_agg_alloc`). The allocator may collect, so `vc` must
   be on the C stack before the next allocation.
2. Store `cellp=0` and `tbl=tb` into the VCELL **before** calling
   `rt_ws_strdup_c`. The GC's `HB_AGGV` walk dereferences `vc->tbl` on every
   live VCELL it visits; a collection landing between the strdup call and the
   `tbl` store would see `tbl=0` (skipped — safe) or `tbl=tb` (followed —
   safe), never a dangling pointer.
3. Spill `vc` to `[rsp+40]` so the conservative C-stack scan finds it across
   the strdup. Without the spill, the only reference to a live HB_AGGV cell is
   in a caller-saved register that `rt_ws_strdup_c` may reuse.
4. Store `key` **after** the strdup returns. The carve is fully zeroed
   (HB_AGGV takes the full memset arm), so `key=0` between steps 1 and 4 is
   coherent for the GC walk.

---

## 8. Open items going into next session

1. **SNOBOL4 watermarks must be re-derived from pristine.** m3 329/5 and m4
   324/2 are the documented targets. Do not trust the 332/2 reading from this
   session — no pristine SN4 baseline was taken.
2. **RTX-23-ICN** (str concat DT_S‖DT_I arm) remains BLOCKED ON LON: needs
   §7 re-assignment of `str_concat_d`/`rtx_str.S` from SN4-RTX.
3. **RTX-25-ICN** (eliminate the VCELL allocation on rvalue subscript) is the
   highest-leverage open rung but is PHASE 2 / template territory: fires `.s`
   regen ×3 and collides with the ζ ladder — serialize with Lon.
4. **RTX-21-ICN** (extend run-phase workload set: list/set/scan/IO) is the
   next unblocked survey rung.
