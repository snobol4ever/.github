# FINDING 2026-10-03 hq_icon -- a runtime-compiled EVAL chain copies an alternation operand out of a stack slot it never wrote

Answers CEO-1461 finding one (seed 1205, mode 4, general-protection fault in libc). Measured on SCRIP `6c82634b6`, incremental `make`, scratch only, no suite run, no row written.

## The witness: three lines, deterministic, mode 4 only

`...witness.txt` beside this file, fed to the driver `...inf_eval.sno` (the ceo's `inf_eval.sno`, byte-identical, md5 `4ce880cc7482...`):

```
"b" ? LEN(1)^ LEN(2)
FENCE
'(matched [things])' ?&STLIMIT | (']' ? *']')
```

```
scrip --compile -o x.s inf_eval.sno < /dev/null
gcc -m64 -no-pie x.s -Wl,-rpath,SCRIP/out -LSCRIP/out -lscrip_rt -lm -lpthread -o x.bin
./x.bin < witness.txt        # rc=139, the signature of CEO-1461: libc.so.6+0x19bc5c, fault address nil, rsp mod 16 = 8
scrip inf_eval.sno < witness.txt   # mode 3, rc=0: ERROR 233 / PATTERN / PATTERN
```

Line one raises error 233 (`^` on patterns, trapped by SETEXIT), line two evaluates `FENCE`, line three crashes. Line three alone runs clean in mode 4 (rc=0).

## How it was reduced

- The ceo's `mm/runs/t1205/crash_batch.txt` (8235 lines) fed to the driver on the CURRENT binary: mode 3 prints all 8235 lines clean; mode 4 dies rc=139 with the same signature. So the batch reproduces on its own, contrary to the note that it did not.
- Prefix bisection: the first crashing prefix ends at line 5652 (`'(matched [things])' ?&STLIMIT | (']' ? *']')`); that line alone is rc=0.
- Delta debugging with that line pinned (13 runs): the three lines above.

## What the fault is -- not a misaligned stack

`rsp mod 16 = 8` is the normal state inside a libc function and was a red herring. The fault is `__strlen_evex` reading through `0x45007ffff5448819`, a non-canonical address (bits 63..48 are `0x4500`, bit 47 is 0), which is what a general-protection fault with a nil fault address means.

Backtrace: `strlen` <- `rcp_of` (`src/runtime/pattern_match.c:78`, the `DT_S || DT_SNUL` arm: `d.slen ? d.slen : strlen(s)`) <- `pat_alt` (`:258`) <- `rt_sno_pbalt_d`. The operands as `pat_alt` received them:

- left = `{v = 0 (DT_SNUL), slen = 0, s = 0x45007ffff5448819}`
- right = `{v = 2 (DT_S), slen = 1, s = "]"}`

A null-string descriptor whose payload is garbage; `rcp_of` trusts the payload, while `pat_operand_is_null` a few lines below never reads it.

## Where the garbage comes from

The emitted chain builds the `rt_sno_pbalt_d` argument array with `mov 0xd0(%rsp),%rax; mov %rax,(%rsp); mov 0xd8(%rsp),%rax; mov %rax,0x8(%rsp)` (args[0] copied from a slot 0xd0 bytes up the frame), then the two words of args[1].

A watchpoint on that slot's payload word, armed after `eval_build_chain` returned for the third line, fired exactly once before the fault: `NV_SET_fn("EVAL$")` called from `eval_string_transient` (`runtime_eval.c:636` -> `core.c:3628`), writing `0x45007ffff5448819`. That is the runtime's own earlier C frame leaving stale bytes on the stack. The chain, once running, never writes the slot it copies from.

So: on the path taken, an alternation operand is read from stack that nothing initialised. When the stale bytes happen to be zero the operand reads as a null string and nothing shows; when they are a pointer-shaped value under a zero tag, `strlen` follows it. That is the whole of the state dependence, and it is why a prefix of thousands of lines is needed in one process and a single line passes.

## Not established

- Which operand of the alternation that slot is meant to hold, and why the emitter skips its store on this path (the lowering of `A ? B | C`, where `?` binds loosest, is the first place to look).
- Whether the ceo's finding two (seed 1214, error 102 with offending value `&null` raised at `drive(inf_bsize, inf_sbl)`, a rerun of the same seed clean) is the same class. A read of unwritten stack would vary run to run, so it fits; I did not witness it.

## Priors

- Not caused by `56de2bc13` (the EVAL chain reclaim): the ceo's `explore.bin` was built at 10:59 CDT, before it, and died the same way.
- A consumer-side guard in `rcp_of` (do not read `.s` of a `DT_SNUL`) would hide this one reading and nothing else: a stale tag word that is not zero is an arbitrary type. The cure is the store in the emitted chain.
- The cfo is rewriting this road (`eval_frame_open`, `eval_frame_land`, c2bb); the witness should be run against that build before anyone patches the old emitter.
