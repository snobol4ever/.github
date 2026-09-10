# FINDING 2026-09-10 (cfo): the Icon cset arena wraps under a live value -- a cset held in a variable is silently overwritten by the 1137th cset built after it

**Class:** wrong answer, both modes, Icon. **Found:** while measuring CEO-496 cut 2 (concord at parity); named by the coo as a wrong-answer class on 2026-09-10 11:17 and asked for as a FINDING with a witness, not a ledger line. **Status:** open; the cure is CEO-496 cut 3 (the cset operators on the 256-bit tables, the canonical string written once into a pinned block, no presence table, no arena).

## The mechanism, read in the source

`src/parsers/icon/icon_runtime.c` keeps `static char icn_str_arena[65536]` with a bump pointer `str_arena_pos`. `cset_canonical`, `cset_union`, `cset_diff` and `cset_inter` each write their result string into that arena and advance the pointer; when the next result would not fit, the pointer is reset to 0 and the arena is overwritten from the start:

    if (str_arena_pos + n + 1 > 65536) str_arena_pos = 0;

A cset descriptor is `CSETVAL(ptr)` -- the type marker plus the arena pointer. Nothing copies the bytes out of the arena when the value is stored in a variable, a list, a table or a record, so every cset value older than one arena lap points at bytes that now belong to a newer cset. The length registry (`rt_icn_cset_register`) is keyed by the same pointer and is updated to the NEWER length on the re-registration, so the old value does not even keep its size.

## The witness

`corpus/tests/icon/a_cset_held_in_a_variable_survives_a_thousand_later_csets.icn` (ref cut from icont + iconx 9.5):

    procedure main()
       local first, i, c, s;
       first := cset("abc");
       s := "";
       every i := 1 to 1200 do {
          c := cset(string(i)) ++ &letters;
          s := string(c);
       };
       write(image(first), " ", *first, " ", string(first));
       write(*s);
       c := first ++ 'z';
       write(image(c), " ", *c);
    end

| | line 1 | line 2 | line 3 |
|---|---|---|---|
| iconx | `'abc' 3 abc` | `55` | `'abcz' 4` |
| SCRIP m3 (539af6946 + cut 2) | `'137' 3 137` | `55` | `'137z' 4` |
| SCRIP m4 | `'137' 3 137` | `55` | `'137z' 4` |

Each loop iteration builds two canonical strings of about 55 bytes (`cset(string(i))` and the union), so the arena laps after roughly 580 iterations; `first` then reads the bytes of a later iteration's `cset(string(i))` -- `'137'`, three characters because the registry entry for that pointer now carries the later length. The union `first ++ 'z'` is computed from the overwritten bytes, so the corruption propagates into new values.

## Who is exposed

Any Icon program that holds a cset across more than ~64 KB of cset construction: a table of csets built in a loop, a cset per record, `many(c)` where `c` was computed early in a long run. The Arizona, Jcon and IPL boards do not reach the lap (their csets are few and small), which is why no board is red on it today; concord builds two csets and never laps.

## The cure (cut 3, cfo, CEO-496)

The registry already carries a 32-byte bit table beside every cset (539af6946). The operators become `OR`/`AND`/`AND NOT` over the operands' tables, the canonical string is written ONCE from the result bits into a pinned block (`rt_pinned_alloc`, never reused) and registered with its bits filled, and `cset_canonical` for `cset(s)` does the same from `s`. No presence table per operation, no arena, no lap. The witness above is the DONE-WHEN: its three lines equal iconx's in both modes.
