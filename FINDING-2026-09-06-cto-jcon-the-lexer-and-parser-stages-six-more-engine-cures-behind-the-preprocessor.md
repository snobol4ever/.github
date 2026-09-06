# FINDING 2026-09-06 cto — Jcon, the lexer and parser stages: six more engine cures behind the preprocessor, and the parse stage now matches the oracle's AST

Row: `flip-jcon-compiler-jtran` (CEO-359/360/368). Sequel to `FINDING-2026-09-06-cto-jcon-an-omitted-argument-read-the-callers-own-argument-and-two-more-cures-behind-the-preprocessor.md`.
Cures 4–6 are on origin/main: SCRIP `609cb5e5f`, `9817e21a2`, `b7d16043e` (measured as `883b3be3e` before the rebase). Cures 7–9 are on origin/main too: SCRIP `9cfdc2b8a` (thread exit), `d7e98db21` (carve-wide snapshot), `c5a6f7d50` (snapshot-sized
stacks), boarded as `cd95e88c1` before the rebase and push.
Measured on incremental `make`, `RT_OPT=-O0`, scrip and `libscrip_rt.so` rebuilt after every pull, every witness cut from iconx v9.5.25a.

## The claim

Jcon's **lexer stage** matches the oracle's twelve tokens exactly, driven directly or as a co-expression body, and its **parse stage**,
driven directly, matches the icont-built oracle's AST dump line for line (65 of 65). The preprocessor stage stays byte-equal through the
real driver. The row's own criterion passes the preprocessor arm and is red on the symbolic stage, where the remaining divergence is the
generator-host reservation at compiler scale (hq_B's one bug per CEO-368): `main` and `ir_value` each carve 66 MB, and under `ir_value`
the slice arithmetic addresses a region 166 MB above the co-expression's stack. None of the six cures is Jcon-specific.

## The technique held: drive the stage, trace under both, cut the witness, read the asm

Each stage of the pipeline is a generator or a co-expression body over the previous one, so each was driven directly by a two-line
`main` that builds the upstream co-expressions and prints the stage's yields (tokens; `dump_verbose` of AST records). Where the output
differed, the identical instrumented Icon source ran under iconx and SCRIP and the traces were diffed; the first differing line named the
defect every time. Where the program crashed, valgrind and gdb named the instruction, and the emitted `.s` named the arithmetic.

## 4. A subject assigned inside a suspended generator reverted on resume (`609cb5e5f`)

`lex_yylex0` installs each source line with `&subject := lex_nextline(getline)` and is resumed through `yylex`'s `"" ? { every … }`.
The sync-step trace read `pos=10 len=16` under iconx and `pos=10 len=0` under SCRIP after the first resumption. Mechanism (slices 3/4,
`158993400`/`508eeed56`): a suspend inside a scan banks only the position register in the re-entry node's frame slot and re-enters from
the `?` expression's *original* subject operand — robust to abandoned generators, wrong for a subject assigned inside. The yield edge now
also banks the live subject pointer in the slot's free second word and re-enters from it (`rt_scan_reenter_live`); no planner change.
Witness `v6_twolevel.icn` (iconx `ab cd ef`, SCRIP `ab`), controls unchanged.

## 5. A global declared in one file was invisible to every other file (`9817e21a2`)

`lex_IDENT`, declared `global` in `do_ops.icn` and assigned by `initialize()`, read `&null` in `lexer.icn`; `ptok.str := str` then raised
error 041. Each Icon file was lowered as its own *segment* with its own global list, so an undeclared identifier in a file without its own
`global` line became an implicit local. icont links the files as one program; the driver already merged consecutive Prolog segments, and
the same merge now applies to consecutive Icon segments. Two-file witness: iconx 5, SCRIP `&null` in both file orders and both modes,
now 5. This alone blocked every multi-file Icon program.

## 6. The last suspend of a scan body re-yielded forever on resume (`b7d16043e`)

After the token loop, `yylex` does `suspend ptok` (EOFX) inside its scan; SCRIP yielded EOFX on every resumption (3.2 million tokens until
the workspace was exhausted). The re-entry node's continuation is the scan's success trampoline and saving leave, reachable only through
an operand and never an edge, so the chain builder never emitted them, the emitter's target walk found nothing (`[SCAN3] found_k=-1`), no
resumption arm was emitted, and the node's β fell into its ω edge, which the lowering had wired to the *yield* target. The ω edge now
names the continuation; the trampoline and leave become reachable and the resumption ends at the failure exit as the scan-free shape does.
Witness `v11_eof.icn` (iconx `a b EOF`, SCRIP `a b EOF EOF …`).

## 7. A destroyed co-expression exited its thread through libgcc's forced unwind (`9cfdc2b8a`)

A finished co-expression, destroyed later, woke in `scrip_coswitch` and called `pthread_exit` from inside the compiled call chain; the
forced unwind cannot walk compiled Icon frames and segfaulted in `unwind_stop`, discarding buffered stdout with it (the shape of "exit 139,
0 bytes"). The thread's start routine now `setjmp`s before entering the body and the wake path `longjmp`s to it.

## 8. THE HEADLINE — the co-expression snapshot omitted the creator's generator-host reservation (`d7e98db21`)

The lexer as a co-expression body (`c2 := create yylex(c); while t := @c2`) aborted with `malloc(): unaligned tcache chunk` before its first
token, while the same lexer under `every` in the main thread was exact. valgrind: an invalid 8-byte write at `FN__lex_yylex0+5` to an address
neither stack nor heap; gdb at that entry: the region pointer is `rbp + 48` *on the co-expression's stack*. The create site packaged
`frame_bytes = frame_region` — the creator's locals frame, 1,168 bytes — while the creator's prologue had carved 65,544 (frame plus its
generator-host reservation). The body ran in a 1 KB copy and its generator calls addressed host-region slices laid out for the 64 KB
carve; the first store (the caller's `rbp` into the callee's region header, 8 KB up) landed above the co-expression stack in the thread's
TLS, where malloc keeps its cache. This was my rung-38 frame model, one number short. The prologue now records its carve total
(`flat_carve_total`) and the create packages it when it exceeds the locals frame; the co-expression body owns a frame the same shape as
its creator's. A probe of the thread-side region size in hq_B's pass (rt.c:1119 sizes it by the generator's own frame while
`icn_gen_host_slice` adds callee slices) grew `yylex`'s region from 2,112 to 10,224 bytes and changed nothing; the mismatch is a true
latent fact in that pass, reported to hq_B, not the operative defect, and the probe is reverted.

## 9. Co-expression stacks sized to the snapshot (`c5a6f7d50`)

With the snapshot spanning the whole carve, jtran's `main` (66 MB carve) copied more than the fixed 8 MB pthread stack held and the
preprocessor stage, green before, fell to 0 bytes. The create records the snapshot size and the first activation gives the thread a stack of
at least that plus 2 MB when the configured size is smaller; address space is reserved lazily, so only the copied bytes cost memory, and the
size shrinks with the carve. The preprocessor arm is byte-equal again through the real driver.

## Measured

| arm | before | after (tree `883b3be3e` for 4–6; `cd95e88c1` for 7–9, binary 18:35:39) |
|---|---|---|
| Jcon lexer stage, driven directly | 1 token then a hang | **12/12 tokens exact** (with or without a leading `#line`) |
| Jcon lexer as a co-expression body | abort before the first token | **13/13 exact, both modes** |
| Jcon parse stage, driven directly | error 041 / abort | **65/65 dump lines exact** |
| Jcon preproc stage through the real driver | 58 = 58 | **58 = 58** (held through cure 9) |
| row DONE-WHEN | red on the symbolic stage | red on the symbolic stage (hq_B's carve) |
| Icon master | 697/702 | **board OK, CRASH=0 both modes** on `cd95e88c1` (697/702 on `883b3be3e`) |
| Icon ladder | 626/634 | 626/634 (rung 41 inherited); rungs 36 and 38 alone 12/12, 14/14 |
| Prolog ladder | 533/568 | 533/568 |
| SNOBOL4 corpus | m3 1854 · m4 1854 / 1855 | m3 1854 · m4 1854, the standing red (CEO-365) |
| scan gates | argtype 11/11; probes 28/0; rung36 e41/e42 hang | unchanged (the hangs are the FREE row's, recorded since 09-05) |

## What remains, and whose

The symbolic stage: `ast2ir` driven directly under a 1 GB stack still segfaults under `ir_value`'s 66 MB carve, the reservation's
recursion-depth multiplier at compiler scale (three hosts in the whole compiler exceed 64 KB). hq_B holds it at rank 0 with the frame law and a
bounded carve with a loud refusal allowed as a floor (CEO-368). When it lands, the row's criterion runs unchanged.

## Disposition

Cures 4–9 landed on origin/main. The row stays claimed by the cto and its DONE-WHEN is unchanged. Not taken:
the newline-termination question (Lon's absolute rule, CEO-363) and the thread-side region size in hq_B's pass.
