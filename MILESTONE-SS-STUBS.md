# MILESTONE-SS-STUBS.md — Silly SNOBOL4 Stub Implementation

**Goal:** Implement every stubbed function in `one4all/src/silly/`. No stubs remain when done.  
**Method:** One stub at a time. Build clean after each. Commit per stub.  
**Gate:** All stubs replaced by real SIL-faithful implementations. Build clean.

---

## Watermark (update after each stub fixed)

**Current stub:** `DATDEF_fn` (#4)  
**Next stub:** `RSORT_fn` / `SORT_fn` (#5)

---

## Stub List (fix in dependency order)

| # | Function | File | SIL § | SIL lines | Status |
|---|----------|------|-------|-----------|--------|
| 1 | `DMK_fn` | func.c | §19 | 6747–6783 | ✅ implemented `2b07b9b4` |
| 2 | `DMP_fn` / `DUMP_fn` | func.c | §19 | 6699–6746 | ✅ implemented `2b07b9b4` |
| 3 | `DATDEF_fn` | arrays.c | §14 | ~4947 | ⬜ stub returns FAIL |
| 4 | `RSORT_fn` / `SORT_fn` | arrays.c | §14 | ~5220–5267 | ⬜ stub returns FAIL |
| 5 | `LOAD_fn` | extern.c | §13 | 4471–4520 | ⬜ stub returns FAIL |
| 6 | `LOAD2_fn` | platform.c | §13 | (platform) | ⬜ stub returns FAIL |
| 7 | `XCALL_GETPMPROTO` | platform.c | §13 | (platform) | ⬜ stub returns FAIL |
| 8 | `XCALL_XINCLD` | platform.c | §15 | (platform) | ⬜ stub returns FAIL |
| 9 | `XCALL_IO_FILE` | platform.c | §15 | (platform) | ⬜ stub returns FAIL |
| 10 | `KEYT_fn` | platform.c | §16 | ~5600 | ⬜ stub returns FAIL |
| 11 | `getbal_fn` | platform.c | — | (platform) | ⬜ stub returns subject unchanged |
| 12 | `DTREP_fn2` / `DTREP_fn3` | platform.c | §4 | ~1175 | ⬜ stub returns empty |
| 13 | `CNVRT_fn` | func.c | §19 | 6606–6674 | ⬜ stub returns FAIL |
| 14 | `CODER_fn` | func.c | §19 | ~6600 | ⬜ stub returns FAIL |
| 15 | `OPSYN_fn` | func.c | §19 | 6805–6927 | ⬜ stub returns FAIL |
| 16 | `DEFFNC_fn` call frame | define.c | §12 | ~4390 | ⬜ TODO M19 — INTERP re-entry |
| 17 | `XCALL_RPLACE` | platform.c | §19 | (platform) | ⬜ stub no-op |

---

## Method (one stub per commit)

1. Read the SIL block in v311.sil.
2. Read the generated C in snobol4.c.
3. Implement in our silly — three-way sync.
4. Build clean:
   ```bash
   cd /home/claude/one4all
   gcc -Wall -Wextra -std=c99 -g -O0 src/silly/sil_*.c src/silly/*.c -lm -o /tmp/silly-snobol4 -I src/silly 2>&1 | grep -v "^$"
   ```
5. Commit:
   ```bash
   git -c user.name="Lon Jones Cherryholmes" -c user.email="lon@snobol4ever.com" \
       commit -m "M-SS-STUBS FUNCNAME: implement <description>"
   ```
6. Update this file — mark ✅, advance watermark.

---

## Completed

| # | Function | Status |
|---|----------|--------|
| 1 | `DMK_fn` | ✅ `2b07b9b4` — full keyword dump loop |
| 2 | `DMP_fn` / `DUMP_fn` | ✅ `2b07b9b4` — full OBLIST walk with type dispatch |
| pre | INSATL/OTSATL dup-def | ✅ `ff18a0a1` — removed from platform.c |
| pre | DMPSP definition | ✅ `ff18a0a1` — added to platform.c |
| pre | QTSP/AMPSP/BLEQSP/BLSP/FRZNSP init | ✅ `2b07b9b4` — data_init() |

