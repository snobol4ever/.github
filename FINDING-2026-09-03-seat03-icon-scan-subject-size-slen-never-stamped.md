# FINDING — `*&subject` reads 0 inside ANY active scan (not specific to a second scan block, though
# that is where the assigned witness happens to exercise it): the register-fast-path DESCR build for
# `&subject` writes only the low 32 bits of its tag word (the DT_S type), leaving the upper 32 bits
# (`slen`, what `rt_size_d`'s DT_S arm actually reads for the `*` operator) at whatever a bare qword
# immediate move leaves them — zero. The subject's real length is sitting unused in r15 two
# instructions away. Two-instruction fix, both call sites (ZRES and frame-slot arms).

**seat03 · 2026-09-03 · row `icon-master-six-run-graded-reds-cured`**

## 1. Witness and symptom

Task-assigned witness `procedure_scan_write_1` (origin `probe_witness__witness_icn_carve_leak_subject`):
```icon
procedure main()
   local s
   s := "-n10"
   s ? { if ="-" then write("blk1 matched") }
   s ? { write("blk2 *subj=", *&subject, " subj=[", &subject, "]") }
end
```
Expected `blk2 *subj=4 subj=[-n10]`; SCRIP printed `blk2 *subj=0 subj=[-n10]` — **the bare value read of
`&subject` is completely correct** (`-n10`, matching the current scan's subject exactly), only its SIZE
is wrong. That split (value right, size wrong) is what pointed at a separate encoding path for the size
operator rather than a stale/uninitialized subject pointer.

## 2. ASM-DIFF-FIRST: reading the actual emitted `--compile` output settled it in one pass

`&subject`'s register-optimized read (`bb_keyword_icon.cpp`, the `g_scan_regs_live` arm — active any
time compilation is inside a `?` scan body) emits:
```
mov qword ptr [dst+0], 2      ; DT_S, and this ALSO zeroes [dst+4..7] as a side effect
mov qword ptr [dst+8], r13    ; subject pointer
```
Compare the literal-string case a few nodes earlier in the SAME emitted file (`"blk2 *subj="`, a `DT_S`
value built the ordinary way):
```
mov qword ptr [dst+0], 2      ; DT_S
mov dword ptr [dst+4], 11     ; <-- slen = 11, the string's real length, patched into the SAME qword
mov rax, ...                  ; address of the literal bytes
mov qword ptr [dst+8], rax
```
Every OTHER DT_S-tagged value construction in this emitter follows the tag qword-write with a SEPARATE
dword-write to `offset+4`, patching the true length into the tag word's upper half (`DESCR_t`'s own
layout, confirmed in `c_rt_size_d`: `v.v = lo & 0xFFFFFFFF; v.slen = lo >> 32;`). `&subject`'s
register-fast path is the one site that skips it. `rt_size_d`'s `DT_S` arm (`rt.c:1795-1798`) reads
`descr_slen(v)` — the stamped field, never a `strlen()` fallback for this type — so a subject read
through this path always sizes to 0, no matter how long the actual string is.

## 3. The fix

`bb_keyword_icon.cpp`, both call sites of the `g_scan_regs_live` (`&subject` in-scan) arm — the `ZRES`
form (used when the result lives in a Byrd-box register-carried slot) and the frame-slot form (`FRQ`)
— gained one instruction each, stamping the tag's slen half from **r15**, which the scan-enter
sequence (`rt_scan_enter`/`rt_scan_reenter`, both return `{ptr in rax, len in rdx}`, banked to
`r13`/`r15` respectively at every scan entry site) already carries as the register-cached subject
length for the entire duration of the active scan:
```cpp
+ x86("mov", ZRES(0), (long)DT_S)
+ x86("mov", ZRESD(4), "r15d")     // NEW
+ x86("mov",  ZRES(8), "r13")
```
and the frame-slot twin:
```cpp
+ x86("mov", FRQ(_.op_off),     (long)DT_S)
+ x86("mov", FR(_.op_off + 4),  "r15d")   // NEW
+ x86("mov", FRQ(_.op_off + 8), "r13")
```
`ZRESD`/`FR` are this file's own existing 32-bit-slot accessors (`x86_asm.h:981`, and the identical
`FRQ`/`FR` split already used e.g. in `bb_lit_scalar.cpp`'s `ls_rd`/`ls_rq` macros and
`bb_match_arbno.cpp`'s frame-slot writes) — no new addressing primitive needed, just the missing call.
r13/r14/r15 are the Σ/δ/Δ scan-reserved register trio (RULES.md's own register contract) and are
callee-saved by the standard SysV ABI, so r15 is guaranteed live and correct from scan-enter through
to this read regardless of what ordinary C-runtime calls (e.g. the `write` builtin) happen in between.

## 4. Verified: NOT specific to "second scan" — a general in-scan defect the witness merely surfaces once

The assigned witness only exercises `*&subject` in its SECOND `?` block (the first uses a bare pattern
match with no explicit size read), which is why the census framed it as a "second scan" symptom. Direct
test isolates it to the general case:
```icon
procedure main(); local s; s := "-n10"; s ? { write("first *subj=", *&subject) }; end
```
**Failed identically (`0`) before this fix, in the FIRST and only scan block** — confirming the defect
is "any in-scan `*&subject` read," not anything specific to entering a second, separate scan region.
Post-fix: `first *subj=4`, correct. Assigned witness now matches its `.ref` byte-for-byte, m3 AND m4
(`--compile` + link + run, output identical to `--run`).

## 5. Witness minted

`corpus/tests/icon/icon_scan_subject_size.icn` / `.ref` — exercises `*&subject` in a first scan block,
a plain-match-only second block, and a third block with `*&subject` again, guarding against a future
regression that only shows up on re-entry.

## 6. State

Companion to `FINDING-2026-09-03-seat03-icon-level-entry-side-landed.md` — both land in the same
commit (same task row, both touch the emitter, both need the same full-battery verification before
push).
