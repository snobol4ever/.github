# FINDING — `&ascii` and `&cset` are built off-by-one: `chr(0)` is missing from position 1 and wraps to the last position instead

**Seat:** seat09 · **Date:** 2026-08-29 · **Row:** `tests-consolidate-icon` (found while characterizing `rung36_jcon_scan1.icn`'s residual divergence, per that row's own KEEP.md flag: *"a constant offset smells mechanical, not semantic"*)
**Not fixed.** Root-caused to the exact two lines; no code changed.

## THE SYMPTOM

`rung36_jcon_scan1.icn` is otherwise fully green against `.expected`. The only divergence is two lines that scan *within* `&ascii`:

```
- ascii?skips 1 16 31 46 61 76 91 106 121
+ ascii?skips 15 30 45 60 75 90 105 120 128
```

Not a uniform shift, at first glance — but every value is explained exactly by one bug (see below), not a family of unrelated ones.

## ROOT CAUSE — exact, both keywords, same pattern

`src/runtime/keywords.c:75-76`:

```c
{ static char a[128]; for (int c=1;c<128;c++) a[c-1]=(char)c; a[127]='\0'; kw_cset_reg(a, "&ascii", 128); }
{ static char a[256]; for (int c=1;c<256;c++) a[c-1]=(char)c; a[255]='\0'; kw_cset_reg(a, "&cset", 256); }
```

The loop starts `c` at **1**, not 0, so `a[0]` gets `chr(1)`, `a[1]` gets `chr(2)`, … `a[126]` gets `chr(127)` — `chr(0)` is never written by the loop. The following line, `a[127]='\0'`, looks like ordinary C null-termination hygiene but is actually **data**, not a terminator, here (`kw_cset_reg` takes an explicit length): it plants `chr(0)` at the *last* slot instead of the first. Net effect, confirmed by direct probe:

```
&ascii[1]   = "\x01"   (should be "\x00")
&ascii[120] = "x"      (should be "\x77" — chr(0x77)='w'; SCRIP's [120] holds chr(120)=0x78='x')
&ascii[127] = "\x7f"   (should be "\x7e", '~')
&ascii[128] = "\x00"   (should be "\x7f", DEL — off the end of a correctly-built 128-char &ascii)
```

i.e. `&ascii[N] == chr(N)` today; it must be `chr(N-1)`. `&cset` (256-char) has the byte-identical pattern (`&cset[1]="\x01"`, confirmed). Both are the SAME bug at adjacent lines, not two bugs. Range-limited keywords built differently (`&lcase[1]="a"`, `&digits[1]="0"`) are unaffected — they don't start from `chr(0)`, so this specific loop shape doesn't apply to them.

## WHY scan1's DIFF LOOKS LIKE A "+14" SHIFT AT A GLANCE, AND ISN'T

`upto(skips)` on `&ascii`, sorted by ascending scan position, in a **correctly-built** `&ascii` (position = byte+1): the 9 sub-128 members of `skips` (`\x00,\x0f,\x1e,-,<,K,Z,i,x` = bytes `0,15,30,45,60,75,90,105,120`) land at positions `1,16,31,46,61,76,91,106,121` — exactly `.expected`.

In SCRIP's off-by-one `&ascii` (position N holds `chr(N)`, and `chr(0)` lives at position 128 instead of being absent-until-wrapped), the same 9 byte values are found at position = byte value itself, **except** byte 0 which is at position 128 (the wrap): `15,30,45,60,75,90,105,120,128`. Sorted ascending, that is exactly SCRIP's reported line. Every one of the 9 values is accounted for — this is one off-by-one construction bug, not a family of small semantic bugs, and not a real "+14": the two lists happen to start 14 apart only because `.expected`'s first entry (position 1, the wrapped `\x00`) has no correctly-shaped counterpart near the front of SCRIP's list.

## RULED OUT: NOT `FINDING-2026-08-24-seat16-icon-cset-string-literal-embedded-nul-truncates-to-empty.md`

That prior finding (also surfaced while investigating this same file) is a **different, unrelated** bug: a cset/string *literal* with an embedded `\x00` (e.g. `'\x00ab'`) truncates to empty at parse time — a source-literal-parsing defect, not a built-in-keyword-construction one. Checked directly before writing this up, since `skips := '\x00\x0f\x1e-<KZix...'` also opens with `\x00` and could plausibly have collided with that bug: `*skips` measures **18**, its full and correct member count — `skips` is not truncated. The `&ascii`/`&cset` off-by-one fully and exactly explains 100% of `scan1`'s divergence on its own; the two findings are independent.

## BLAST RADIUS (uncharacterized further, flagging not chasing)

Anything that inspects `&ascii`/`&cset` positionally or by content — not just this one corpus file. `chr(0)` is silently absent from where every Icon program expects to find it in these two keywords and present 127/255 positions later than expected instead. Did not sweep the corpus for other consumers of `&ascii`/`&cset` beyond this file.

## DISPOSITION

Not attempting the fix — out of this row's lane (`tests-consolidate-icon` is suite *conversion*, not runtime bug-fixing) and it's a two-line, well-isolated change (`for (int c=1;c<128;c++)` → `for (int c=0;c<128;c++) a[c]=(char)c;`, dropping the now-unneeded `a[127]='\0'`/`a[255]='\0'` lines, for both `&ascii` and `&cset`) that someone with room can verify and land quickly. `rung36_jcon_scan1.icn` stays loose (bug, not a permanent design choice, same precedent this task uses everywhere else). Mailed hq_C. `tests/icon/KEEP.md`'s `scan1` entry updated to point here instead of carrying the open "worth a real look" note.
