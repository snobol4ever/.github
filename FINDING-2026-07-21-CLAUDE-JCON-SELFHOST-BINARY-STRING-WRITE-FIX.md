# FINDING: ICN-BINWRITE-FIX — SCRIP could not write binary bytes 0x00/0x01/0x03; every JCON .class was corrupt

**Date:** 2026-07-21
**Author:** Claude Opus 4.8
**Commit:** (ICN-BINWRITE-FIX in SCRIP — two edits in src/runtime/by_name_dispatch.c)
**Status:** CLOSED for the byte-write root cause (byte-exact + zero smoke regression). Unmasks the NEXT jtran blocker.

---

## Summary

The JCON self-host pipeline was reported at "bc_File ✓, next = jlink" — but that was a **false
positive**. `bc_File` returned rc=0 while the `.class` bytes were already garbage; nothing validated
them until the JVM tried to load the linked class. Building the full run path (jcon.zip runtime +
SCRIP-jlink + bundle + `java`) exposed the real state: the JVM rejected the class with
`UnsupportedClassVersionError: class file version 28261.28271`.

Root cause: **SCRIP's string-output path cannot faithfully emit the bytes 0x00, 0x01, 0x03** — the
exact bytes JVM `.class` files are saturated with. Two independent runtime bugs, both fixed.

---

## Diagnosis (monitor-first, minimal repro)

Hexdump of the jlink-produced `hello_t.class`: magic `ca fe ba be` correct, but the version field
(should be `00 03 00 2d` = minor 3 / major 45) was `6e 6f 6e 65` = ASCII **"none"**. The JVM read
that as version 28261.28271. The same corruption was present in `bc_File`'s own module classes.

Minimal repro — write single bytes to a file and read them back:

| char(v) | *char(v) | bytes written | verdict |
|---|---|---|---|
| 0x00 | 0 | (nothing) | NUL dropped |
| 0x01 | 1 | (nothing) | SOH dropped on write |
| 0x03 | 1 | `6e 6f 6e 65 28 29` = "none()" | ETX expands to a structure image |
| 0x02, 0x04-0xFF | 1 | faithful | OK |

So `00 03 00 2d` → `` + `none()` + `` + `-` = `none()-` — matching the corrupt class byte-for-byte.

### Mechanism

`out_write_str()` (by_name_dispatch.c:3738) uses control bytes as an **in-band encoding for
structured values** (SNOBOL4-style pattern/set display): `\x03` at s[0] marks a structured object
(s[1] picks flavor a/l/o → any/all/one, else "none"), `\x01` separates elements, `\x04` closes
nesting. `write`/`writes` routed ALL string arguments through this decoder (via `out_write_descr`),
so genuine data bytes 0x01/0x03/0x04 were reinterpreted as structure markers. Separately, `\x00`
was lost because the length came from `strlen`, and the dispatcher's `char()` built its result with
`STRVAL` (slen=0) instead of `BSTRVAL` (slen=1), so `char(0)` collapsed to the empty string.

Enabling fact: `DESCR_t` carries an explicit `uint32_t slen` (descr.h:30). `BSTRVAL(s,len)` sets it;
`STRVAL(s)` sets slen=0 (length via strlen). The bytes were always representable — only the output
and the `char()` constructor ignored `slen`.

---

## Fix (two edits, src/runtime/by_name_dispatch.c)

1. **write/writes to a real file writes verbatim by slen.** In the write loop (~4189): when the
   destination is a real file (not stdout/stderr) and the argument is a string, emit exactly
   `slen` bytes via `fwrite`, bypassing the `\x03`/`\x01` structure decoder. File I/O is data
   (byte-exact); stdout/stderr keeps the structure display for pattern images. This fixed 0x01/0x03/0x04.
   `_bn = av.slen ? av.slen : strlen` (slen==0 legitimately means "use strlen" for STRVAL strings).

2. **`char()` carries an explicit length.** The dispatcher's `char()` (~4286) used `STRVAL(buf)`
   (slen=0, drops embedded NUL); changed to `BSTRVAL(buf, 1)` so `char(0)` yields a real 1-byte NUL.
   (`BCHAR_fn` in string_builtins.c was already correct with BSTRVAL, but the dispatcher path fires first.)

---

## Verification

- Rebuilt `scrip` (-O0) + `libscrip_rt.so` (RT_OPT=-O0, feature build per RULES — -O2 is perf-only).
- `bintest.bin` now = `ca fe ba be 00 03 00 2d` EXACTLY. Byte map 0x00-0x14 all faithful.
- **Icon smoke: m3 14/14 PASS, m4 14/14 PASS — ZERO regression.**
- Self-host run: version corruption GONE (no more UnsupportedClassVersionError).

---

## What this unmasks (NEXT blocker)

With bytes handled correctly, `bc_File` now errors cleanly instead of writing garbage:
`Run-time error 500 / offending value: record(ir_Label)`. An unresolved `ir_Label` record reaches a
`j_writer_u1/u2/u4` integer writer (bytecode.icn ~1649-1664 range check `(0<=u<N) | runerr(500,u)`).
Almost certainly a **pre-existing jtran label-resolution bug** that the byte corruption masked (the
buggy path silently coerced the record to garbage bytes → 832B rc=0 "class"; now it errors honestly).
Pointer: bytecode.icn:1548-1550 resolves `j_label` offsets to ints via a `locations` table — a branch
target that never got converted `ir_Label` → `j_label` → int is leaking through. Diagnose with
gdb/monitor discipline in gen_bc.icn's branch emission + bytecode.icn's offset resolution.

---

## Toolchain built this session (fresh container, reproducible via scripts)

- `scripts/jcon_selfhost_build.sh` — bootstraps scrip (-O0), libscrip_rt (-O0 feature / -O2 perf via PERF=1),
  the 17-module SCRIP-jtran, 2-module SCRIP-jlink, and jcon.zip. do_ops.icn/interface.icn generated by
  running oplexgen/interfacegen THROUGH SCRIP then semicolonizing; iTrampoline.java likewise via SCRIP.
- `scripts/jcon_selfhost_run.sh <prog.icn>` — full end-to-end: SCRIP-jtran translate → jcon.ZipMerge →
  SCRIP-jlink → manifest + FindFiles + ZipMerge → `java -cp combined.zip:jcon.zip`. Uses canonical `l$<base>` naming.

Both jtran (505,146 asm lines, 0 bombs, 5MB) and jlink (82,290 lines, 0 bombs, 860KB) built clean.
jcon.zip = 333KB / 382 classes. JDK required (container ships JRE-only; script installs openjdk-21-jdk-headless).
