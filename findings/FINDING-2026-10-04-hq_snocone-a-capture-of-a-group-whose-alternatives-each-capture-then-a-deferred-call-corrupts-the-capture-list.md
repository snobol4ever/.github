# A conditional capture of a group whose alternatives each hold a capture, followed by `. *F(...)`, hits `rt_dcap_pump: CORRUPT CAPTURE ENTRY` (SCRIP modes 3 and 4; SPITBOL is clean)

Found 2026-10-04 by hq_snocone while landing the Pascal `Preprocess` pattern in `bootstrap/parser_pascal.sc`. Measured on SCRIP c9268cd17 (RT_OPT -O0).

## Witness (8 lines of SNOBOL4, no chain, no function body of substance)

```
        DEFINE('F(b,t)')                :(FEND)
F       F = .DUMMY
        OUTPUT = 'F [' b '] [' t ']'
                                        :(NRETURN)
FEND
        D = ( ( '{$' BREAK('}') . B '}' | '(*$' BREAKX('*') . B '*)' ) . T . *F(B, T) )
        P = POS(0) ARBNO(FENCE(D | ANY('ab'))) RPOS(0)
        '{$def}' ? P
        '{$def}a(*$xyz*)' ? P
END
```

- `sbl -bf`: `F [def] [{$def}]` twice, then `F [xyz] [(*$xyz*)]`.
- `scrip --run` and `scrip --trace --run`: `rt_dcap_pump: CORRUPT CAPTURE ENTRY refused -- len=0 saved_delta=<garbage> ... (target '*EXPR$0', frame depth 1)`, one line per match that starts with a directive (two of the two matches under `--run`; three lines under `--trace --run`).
- mode 4 (`--compile -o`, gcc against out/libscrip_rt.so): the same refusal once, and the program printed two `F` lines where `sbl` prints three.
- The garbage `saved_delta` differs run to run (it reads like an uninitialised word), so the loss is intermittent: `bootstrap/parser_pascal.sc` as first written (the group `( '{$' BREAK('}') . pp_b '}' | '(*$' BREAKX('*') . pp_b '*)' ) . pp_t . *PPDir(pp_b, pp_t)`) lost the whole Preprocess match, printing `Parse Error`, in 3 of 3 runs through `run_scrip_parser.sh` on one source, and in 2 of 8 and 3 of 10 runs of the same source through a scratch copy of the chain (the other runs printed the right tree). The monitor refuses the witness for the same reason (traced and untraced output differ).

## What does NOT trigger it (each measured)

- one alternative only: `( '{$' BREAK('}') . B '}' ) . T . *F(B, T)`
- the alternation with no outer `. T` : `( A . B '}' | C . B '*)' ) . *F(B, B)`
- no inner capture: `( '{$' BREAK('}') '}' | '(*$' BREAKX('*') '*)' ) . T . *F(T)` -- the shape landed in parser_pascal.sc.

So the trigger is the conjunction: an alternation whose arms each carry a conditional capture, itself captured, then a deferred-expression call target.

## Where to look

`src/runtime/pattern_match.c` `rt_dcap_pump` (the entry's `len`/`saved_delta` are read from the capture list after the first star-target call returned); the capture list is `mark..top` in the CAS area, and the entries after the first alternative's capture look overwritten or never written for the second capture of the group.

## Cure bar

The witness above prints, under `scrip --run`, `scrip --trace --run` and a `--compile -o` binary, exactly what `sbl -bf` prints, with no `CORRUPT` line, over 20 runs.
