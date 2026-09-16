# FINDING 2026-09-16 hq_pascal — the 131 open PAT rejections, censused by class, and why the next rung is the required-function domain errors

**Source of the population:** the progress database, not a fresh board. Row `2026-09-16T16:32:51`,
SCRIP `fe37edc72`, corpus `9e75ac5ce`, measurer hq_pascal — the run that wrote the 296/427 SCORE
row. No board was re-run to produce this census; the per-program rows the runner already appended
are the record, which is the whole point of CEO-319/331.

⭐ **The m3 and m4 failing sets are BYTE-IDENTICAL, all 131 names.** That is the shape a rejection
suite should have, and it is new: before the m4 arm compiled, linked and ran (SCRIP `fe37edc72`,
CEO-783), m4 could only observe a compile-time refusal, so the two columns disagreed by 12 for an
instrument reason. They now agree by measurement.

## The census

A PRT entry declares its own violation in its header comment (`PRT test NNN: <claim>`). This table
classifies the 131 by that declared claim.

⛔ **It is a census by DECLARED INTENT, not by observed failure mode** — a keyword pass over the
header lines, useful for picking a rung and worthless as a verdict on any single entry. The names
are the ground truth; the class is a handle.

| n | class | entries (`iso7185prt` prefix dropped) |
|---:|---|---|
| 21 | file-variable state and file I/O (6.6.5.2, 6.9) | 1706a 1706b 1713 1718 1741 1754 1755 1756 1758a 1758b 1767 1839 1840 1841 1866 1875 1876 1877 1878 1879 1880 |
| 14 | parameter and procedure rules (6.6.3) | 0054 0055 1707a 1707b 1708 1723 1724 1737 1748 1829 1830 1831 1861 1918 |
| 14 | required-function domain and range errors (6.6.6) | 1727 1730 1733 1734 1735 1736 1738 1739 1744 1746b 1858 1859 1864 1865 |
| 13 | lexical and token-level rejection (6.1) | 0031 0040 0138 1300 1508 1749 1750 1761 1824 1847 1911 1913 1916 |
| 13 | subrange, index and range checking (6.4.2.4, 6.5.3.2) | 1701 1762 1763 1809 1811 1823 1828 1852 1855 1881 1882 1907a 1907b |
| 13 | variant / tagfield active-arm (6.4.3.3, 6.6.5.3) | 1702A 1702b 1702c 1702d 1719 1722 1843 1851 1856 1857 1871 1872 1873 |
| 12 | goto and label scope (6.8.3.10, 6.1.6) | 0024 1759 1825 1832 1833 1834 1835 1836 1837 1845 1902 1903 |
| 8 | pointer, new and dispose (6.6.5.3) | 1703 1704 1705 1720 1721 1800 1820 1874 |
| 5 | statement forms (6.8) | 1821 1904 1905 1906 1909 |
| 5 | unclassified by the keyword pass | 1732 1743 1846 1849 1917 |
| 4 | type identity and scope of declarations (6.3, 6.2.2) | 1850 1853 1854 1915 |
| 3 | set and case rules (6.7.1, 6.8.3.5) | 1751 1822 1901 |
| 2 | for-statement control variable (6.8.3.9) | 1752 1753 |
| 2 | string rules (6.4.3.2) | 1764 1765 |
| 1 | real where an ordinal is required (6.7.1) | 1908 |
| 1 | undefined value use (6.5.3.2) | 1838 |
| **131** | | |

## The next rung, and why it is not the largest class

The largest class is file I/O at 21. The rung I propose is **required-function domain and range
errors, 14 entries** — `ln(x)` for x ≤ 0, `sqrt(x)` for x < 0, `trunc`/`round` out of integer
range, `succ`/`pred` past the end of an ordinal type, `x/y` and `i mod j` with a zero divisor,
`pack`/`unpack` with out-of-range components. Three reasons, in order:

1. **One mechanism, fourteen witnesses.** Every one of them is "a required function must raise an
   error on a value outside its domain", so the cure is a guard per required function, not a
   design. The file-I/O class at 21 is at least four different mechanisms sharing a chapter.
2. **It is the class the instrument change just made reachable.** Every one of these fires at RUN
   time, not compile time. Until `fe37edc72` the m4 column literally could not see them; they are
   the population that motivated the arm, so they are the population that proves it earned its keep.
3. **It has a precedent in this lane for the shared-node hazard.** Two of the fourteen (`1744`
   `x/y` by zero, `1746b` `i mod j` by zero) reach `rt_div`/`rt_mod`, which SNOBOL4, Icon and
   Prolog also reach, and SPITBOL's REMDR wants today's C behaviour. ⛔ **Those two are an ASK with
   the measurement, never a landing** — the cure shape already established here is a Pascal-local
   node (`pas_rdiv` for real division, ISO `mod` against the shared `rt_mod`), not an edit to the
   shared one. The other twelve look Pascal-local; that is a claim to verify per entry, not to
   assume.

## What this does not say

It does not say any of the 131 is one edit from green, and it does not promise 14 entries from one
commit. A PRT entry passes only when scrip **exits non-zero with a diagnostic**; an entry that
starts crashing instead (rc 139/134) has moved from FAIL to a worse place, and the runner's own
header law counts a crash as CRASHED, never as a correct refusal. The rung is done when the
witnesses are green **and** `test_gate_pas_pat_m4_arm_links_and_runs.sh` still passes.
