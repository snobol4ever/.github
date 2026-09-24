# htprep's m3 SIGSEGV is a stale scan subject across a failing callee's allocation -- a 15-line witness

hq_icon, 2026-09-24, SCRIP de65960d8 (RT_OPT -O0). For the cto (row class CTO-160; jcon_tests/htprep is the Jcon row's one red, 81/82).

## The witness (h4.icn) and its two input lines

```icon
procedure main()
   while line := trim(read()) do write(braces(line))
end
procedure braces(line)
   line ? {
      s := "";
      while s ||:= tab(upto('{}')) do {
         move(1);
         s ||:= newtag()
         };
      return s ||:= tab(0)
      }
end
procedure newtag()
   tab(many(&letters))
end
```

Input (tabs shown as `\t`):

```
\t\tYou Can Fly a 747 Simulator}
\t{li} {@http://ghg.ecn.purdue.edu
```

iconx prints `\t\tYou Can Fly a 747 Simulator` then `\t @http://ghg.ecn.purdue.edu`. SCRIP unstressed matches it in both modes.

## How it diverges

SCRIP_GC_STRESS=n (a collection requested every n-th allocation), n = 1..16, one run each:

- m3: DIFF at 3 and 11, identical elsewhere
- m4: DIFF at 4, 8 and 16 -- so the defect is NOT m3-only; the unstressed layout only spares m4

At m3 stress 3 the first line is right and the second is `\t` followed by NUL-filled garbage the length of ` @http://ghg.ecn.purdue.edu`: everything `braces` takes from its subject AFTER `newtag()` returns is read from a stale address. No [ZGC-STALE] trap fires on this witness (the stale bytes land on reused, not quarantined, memory); on the full htprep with the suite's long argv the trap does fire: block kind=2 size=80 born in c_rt_str_alloc from rt_substr, MOVED by collection #1, holder never visited.

## What the shape says

`newtag()` allocates a substring from the CALLER's scanning environment and then FAILS (it falls off its end), inside `s ||:= newtag()`. The first-line pass is needed to put the heap where the second line's allocation collects. Suspect: the caller's subject base (or the `s` operand of the augmented assignment) held in a slab word or register across the call -- the area the claimed row icon-gc-chunk-a-the-scan-spine-24-sites-take-rec-sigma-because-the-subject-base-is-live names. Minimized by a line/block ddmin (6043 + ~400 trials) under the criterion: icont compiles, iconx rc 0, SCRIP unstressed == iconx, SCRIP under stress in {1,2,3,4,5,7} != iconx; then by hand.
