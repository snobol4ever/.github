# FINDING-2026-09-23-hq_icon-ipl-miu-set-string-corruption-under-gc-pressure-not-yet-rooted

hq_icon, routed on Lon's CEO-1200 word (IPC sync-step monitor push, every hold lifted). `test_gate_icn_ipl_scan_resume_and_limit_flips.sh` names `miu` RED in both m3 and m4 (IPL package suite: 193/194). This is a real defect, isolated but **not cured** — recorded so the diagnostic work is not lost and the next seat does not re-walk it.

## Symptom

`corpus/packages/icon/ipl/progs/miu.icn` (MIU string-system generator, GEB) diverges from its `.std` only at generation #7 (the last, largest generation: 1544 strings). A handful of entries (7 on one heap size, 11 on another) print with **16 stray bytes prepended** before otherwise-correct content, e.g.:

```
"\x00\x00\x00\x00\x00\x00\x00\x000\x00\x00\x00\x02\x00\x01\x00MIIIIUIIIIU"
```
expected:
```
"MIIIIUIIIIU"
```
The count of strings in the set is also short by the same number (1533/1541 vs 1544), consistent with the corrupted entries hashing/comparing differently than they should.

Reproduces deterministically with `SCRIP_HEAP_KB=64` (the isolation harness's *default* heap; smaller values are refused by the floor). Does **not** reproduce with a large arena (`SCRIP_HEAP_MB=64`) — output matches `.std` exactly — so this is GC-pressure-triggered, not a pure logic bug. Under the IPL isolation harness's exact env (cwd change, `ICONPATH`/`PATH` rewrite -- see `lib_icon_ipl_isolation.sh`), the same defect sometimes manifests as a **SIGSEGV** instead of silent corruption (ASLR/layout-dependent: whether the stale read lands on a still-quarantined `PROT_NONE` page or on already-reused memory).

## What the 16 garbage bytes are

Decoded as an `rt_hblk_t` (`src/runtime/rt/gc_heap.c:29`): `{fwd=0, size=48, type=2(DT_S), flags=1(HBF_TTL)}` -- i.e. a syntactically valid, currently-live 48-byte string block's **own header**, immediately followed by the correct string bytes. So *some* `DESCR_t.s` ends up pointing at `h` (a block's header) instead of `h+1` (its payload) -- 16 bytes early -- while `.slen` is inflated by the same 16, so the read walks straight through the header into real data and stops in the right place.

## What was ruled out (with evidence, not just reasoning)

- **GC repair loop** (`gc_heap.c:1437-1438`, the slot-fixup pass after computing forwarding addresses): the formula preserves whatever offset a pointer already had relative to its block; it cannot *introduce* a negative offset, only propagate one that already existed. Confirmed by instrumenting `gc_visit_one`'s `DT_S` case to fire on any `d->s < (char*)(h+1)` at **mark time** (before repair runs) across the whole miu run (114 collections, `SCRIP_HEAP_KB=64`): **zero real `DT_S` hits**. (An initial version of the probe fired 350 times, but every one was `DT_SNUL`, whose `.s` field is a don't-care value never dereferenced -- a false trail, noted so nobody re-chases it.)
- **`rt_sxt_extend`/`rt_sxt_note`/`rt_sxt_match`** (the top-of-heap string-extend-in-place fast path, `gc_heap.c:91-135`): self-validates by exact pointer equality against `g_sxt_owner`, which is only ever set from a fresh allocation's own payload pointer. Cannot produce a header-offset pointer.
- **`table_set_descr_d` / `_tbl_grow` / `_tbl_rehash`** (`aggregates.c:265-347`, the set/table insert and hash-table growth path): `c_rt_gcheap_alloc` (`gc_heap.c:276`) **never collects synchronously** -- it only ever sets `g_gc_pending`; the actual collection runs later, at an emitted safepoint, after these C helpers have already returned and their writes are durably in the table's own (correctly GC-visited) storage. So a collection firing mid-insert cannot see a stale C-local copy of the value being stored.
- **`sort()`'s set path** (`by_name_dispatch.c:8062-8065`): copies `ent[_k]->key_descr` (the real, table-visited descriptor) into the output list -- does not touch the `e->key` display-cache field (`tbl_pair_key`/`aggregates.c:276-279`), which was the other candidate and is a dead end for this symptom.
- **Concatenation itself** (`string_ops.c:18-58`, `c_str_concat_d`): every return path constructs `.s` from a value that is, by construction, exactly a fresh allocation's or `rt_sxt_extend`'s own payload pointer -- never `h` -- so it cannot originate a header-pointer by itself.

## Leading remaining hypothesis, untested

The corrupted strings are specifically the outputs of `apply`'s third `suspend` clause (`tab(find("III")) || (move(3) & "U") || tab(0)`), reached via `every insert(new, apply(!gen))` -- a generator (`apply`, itself scanning with `s ? {...}`) driven by an outer generator (`!gen`), each `suspend`ed result immediately fed into an allocating call (`insert`). This is the textbook hard case for a precise (non-conservative) collector: a value live *across a suspend/resume boundary*, inside a scanning environment, whose root registration may not survive the specific combination of generator resumption + the immediately-following allocating call. Given CLAUDE.md's collector section (CEO-812/818: "the collector guesses nothing... no conservative scan, no pinning") and the cto's existing GC-lane queue (icon-ilib-tgcd-mode4-hang / unitgenr hex2bits, both already named as "a runtime-built structure holding a heap address raw"), this looks like the same defect *class*, on a third witness. Not yet confirmed with a breakpoint on the actual `suspend`/resume path -- that is the next step, not done here.

## Why this wasn't cured in this landing

Root-causing a moving-GC + hand-rolled-coroutine interaction properly (rather than papering over the symptom) needs a focused session with the actual suspend/resume codegen open, not more static reasoning. Landing a guess here risks exactly the kind of "reverted on sight" conservative-visit/pinning patch CEO-818 forbids. Recorded per RULES.md so the diagnostic cost is not paid twice; routed to the cto's GC queue (already holds two siblings of this class) rather than held as a silent local TODO.

## Reproduction (cheap, no isolation harness needed)

```bash
cd SCRIP && make
SNO_LIB=../corpus/include SCRIP_HEAP_KB=64 ./scrip --run ../corpus/packages/icon/ipl/progs/miu.icn </dev/null \
  | diff - ../corpus/packages/icon/ipl/progs/miu.std
```
