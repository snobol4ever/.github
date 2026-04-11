# MILESTONE-SS-STUBS.md — Silly SNOBOL4 Stub Implementation

**Goal:** Implement every stubbed function in `one4all/src/silly/`. No stubs remain when done.  
**Method:** One stub at a time. Build clean after each. Commit per stub.  
**Gate:** All stubs replaced by real SIL-faithful implementations. Build clean.

---

## Watermark (update after each stub fixed)

**Current stub:** `XCALL_IO_FILE` / `XCALL_XINCLD` (#8/#9)
**Next stub:** `XCALL_IO_FILE` / `XCALL_XINCLD` (#8/#9)

1. ~~**OPSYN_fn** (#15)~~ ✅ implemented `1ed4862f`
2. ~~**CNVRT_fn** (#13) + **CODER_fn** (#14)~~ ✅ CNVRT_fn implemented `c84aa12e`; CODER_fn TODO M19
3. ~~**XCALL_RPLACE** (#17)~~ ✅ implemented `101b9f87`
4. ~~**getbal_fn** (#11)~~ ✅ implemented `101b9f87`
5. ~~**DTREP_fn2 / DTREP_fn3** (#12)~~ ✅ implemented `101b9f87`
6. **KEYT_fn** (#10) — keyword trace
7. **XCALL_IO_FILE** (#9) — file I/O attach
8. **XCALL_XINCLD** (#8) — include file
9. **XCALL_GETPMPROTO** (#7) — get prototype string
10. ~~**DATDEF_fn** (#3)~~ ✅ implemented `3e4a1ae5`
11. ~~**RSORT_fn / SORT_fn** (#4)~~ ✅ implemented `58545e92`
12. **LOAD_fn / LOAD2_fn** (#5/#6) — dynamic load
13. **DEFFNC_fn** (#16) — TODO M19 (compiler re-entry required)
14. **CONVE_fn** — TODO M19
15. **CODER_fn** — TODO M19

---

## Stub List (fix in dependency order)

| # | Function | File | SIL § | SIL lines | Status |
|---|----------|------|-------|-----------|--------|
| 1 | `DMK_fn` | func.c | §19 | 6747–6783 | ✅ implemented `2b07b9b4` |
| 2 | `DMP_fn` / `DUMP_fn` | func.c | §19 | 6699–6746 | ✅ implemented `2b07b9b4` |
| 3 | `DATDEF_fn` | arrays.c | §14 | 4748 | ✅ implemented `3e4a1ae5` |
| 4 | `RSORT_fn` / `SORT_fn` | arrays.c | §14 | 5004–5271 | ✅ implemented `58545e92` |
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
| 11 | `getbal_fn` | ✅ `101b9f87` — faithful bal.c translation |
| 12 | `DTREP_fn2` / `DTREP_fn3` | ✅ `101b9f87` — delegate to DTREP_fn |
| 13 | `CNVRT_fn` | ✅ `c84aa12e` — full dispatch (S/I/R/TABLE/ARRAY/NUMERIC); RECOMP TODO M19 |
| 14 | `CODER_fn` | ⬜ TODO M19 — requires compiler re-entry |
| 15 | `OPSYN_fn` | ✅ `1ed4862f` — full N=0/1/2 implementation |
| 16 | `DEFFNC_fn` | ⬜ TODO M19 |
| 17 | `XCALL_RPLACE` | ✅ `101b9f87` — 256-entry table, translate in place |
| pre | INSATL/OTSATL dup-def | ✅ `ff18a0a1` |
| pre | DMPSP definition | ✅ `ff18a0a1` |
| pre | QTSP/AMPSP/BLEQSP/BLSP/FRZNSP init | ✅ `2b07b9b4` |
| warn | 48 warnings → 0 | ✅ `98a5c215` — MILESTONE-SS-WARNINGS complete |
| sub | CONVR/CONIR/CONRI/CNVIV/CNVVI/CNVRTS helpers | ✅ `1ed4862f` |

