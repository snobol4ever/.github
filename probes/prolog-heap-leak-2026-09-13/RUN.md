# Prolog heap-leak witnesses — hq_P, 2026-09-13

Five self-contained programs isolating the leak behind the van Roy gate "flakiness".
Measured on SCRIP `a41070abc`, mode-3, `/usr/bin/time -f %M`. Each is ≤ 12 lines.

⛔ GRADE EVERY ARM BY ITS STDOUT LINE COUNT, NEVER BY EXIT CODE. A program that does
nothing exits 0 and has a beautifully flat memory profile. That mistake is documented in
the parent FINDING's addendum because I made it while investigating this.

    for f in A_copy_nowrite B_copy_write C_nrev_nowrite D_nrev_write E_recursive_counted; do
      kb=$(/usr/bin/time -f '%M' /home/claude_P/SCRIP/scrip $f.pl </dev/null 2>&1 >/dev/null | tail -1)
      ln=$(/home/claude_P/SCRIP/scrip $f.pl </dev/null 2>/dev/null | wc -l)
      printf '%-22s maxrss_kB=%-8s stdout_lines=%s\n' "$f" "$kb" "$ln"
    done

Each file is pinned at N=1024. To see the slope, edit the count in `main/0` (64 → 1024).

EXPECTED on an uncured tree:

    A_copy_nowrite         maxrss_kB=18800    stdout_lines=1        FLAT  (18,792 at n=64)
    B_copy_write           maxrss_kB=18800    stdout_lines=1025     FLAT  (18,836 at n=64)
    C_nrev_nowrite         maxrss_kB=108908   stdout_lines=1        LEAKS (22,968 at n=64)
    D_nrev_write           maxrss_kB=109272   stdout_lines=1025     LEAKS (23,140 at n=64)
    E_recursive_counted    rc=1 ERROR 246     stdout_lines=0        WORSE (56,064 at n=64)

READING: A and B flat across 16x in N exonerate the loop driver, the literal structure
copy, and write/1. C leaks without writing at all. E shows the same unbounded growth in a
RECURSIVE loop, so this is not "backtracking fails to reset H" — nothing reclaims the
Prolog heap at all. Slope 89.5 kB/iteration, dead linear.

CURED LOOKS LIKE: C and D flat in N (within a few MB of A/B), and E completing with
stdout_lines=1 instead of ERROR 246.
