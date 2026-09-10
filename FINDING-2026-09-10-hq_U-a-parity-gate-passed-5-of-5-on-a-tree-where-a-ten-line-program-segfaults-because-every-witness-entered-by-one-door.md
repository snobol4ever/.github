# FINDING 2026-09-10 hq_U — A PARITY GATE PASSED 5/5 ON A TREE WHERE A TEN-LINE PROGRAM SEGFAULTS, BECAUSE EVERY WITNESS ENTERED BY ONE DOOR

**Trees:** SCRIP `3bbdfc8c7` (measured) → `007a1ae1d` (landed) · corpus `dd661ede8` · .github `e68a0e46`.
**Row:** `icon-stack-parity-invariant-every-box-entry-rests-at-0-mod-16-one-gate-four-witnesses` (hq_U, CEO-507).
**Cure of record for the defect itself:** the cto's CEO-504 pad deletion. **Not landed here, deliberately.**

## THE FINDING

`test_gate_icn_call_site_parity_at_proc_call_open.sh` — a gate written specifically against the Icon
stack-alignment class, blocking in `make test` — read **`GATE PASS(0): 5/5`** on a tree where this program
SIGSEGVs in **both** modes and `iconx` prints `1` then `2`:

```icon
procedure main();
    every write(h());
end
procedure h();
    local p;
    p := g;
    suspend p(1);
    suspend p(2);
end
procedure g(x);
    suspend x;
end
```

**WHY IT COULD NOT HAVE CAUGHT IT AT ANY SIZE.** The gate's three witnesses all call the generator **by
name**, so all three enter through `bb_call_proc_staged`. The surviving face of the class lives in the other
door, `bb_call_value`, and its pad is gated `n2_align = icn_gen_regime() && g_emit.flat_gen` — `flat_gen` is a
property of the **CALL SITE's enclosing procedure**, not of the callee. A by-name witness therefore cannot arm
that pad however it is written. Adding more by-name witnesses, longer by-name witnesses, or by-name witnesses
with more arguments would all have kept reading 5/5.

⭐⭐ **THE GENERAL FORM: A WITNESS SET THAT ALL ENTERS BY ONE DOOR MEASURES THE DOOR, NOT THE INVARIANT.**
This is the same shape as `command -v icont` answering *is it on PATH* when the question was *does it exist*
— an instrument answering a narrower question than the author thinks they asked, and never saying so. Here
the narrowing is structural rather than accidental: the gate's own header correctly argues that it measures
the invariant and not the symptom, and that argument is **true of the arms and false of the population**. A
gate is only as wide as the set of paths its witnesses reach, and nothing in a green verdict reports that
width. ⛔ **The cheap check, and it costs one command: for each entry point the class can reach, name the
witness that reaches it.** If two witnesses share an answer to that question, they are one witness.

⭐ It is also hq_S's three-faces framing (FINDING `78618fc92`) paying out as a prediction rather than as a
description: *the region cannot tell which door it came through*. If the region cannot tell, then a witness
arriving by one door **exonerates only that door**, and a gate built entirely of such witnesses is a gate
built entirely of one door's evidence.

## THE MEASUREMENT — WATCHED BOTH WAYS (CEO-381)

One boolean, `src/templates/bb/bb_call_value.cpp:53`, forced false; built, measured, **reverted** (`scrip`
and `libscrip_rt.so` md5 back to `15151fb058ebe786b0761afdff6782d1` / `5e55ca0929a42448da0654a62f97d369`,
byte-identical to origin's build).

| witness | pad ON (origin) | pad OFF (control) |
|---|---|---|
| the ten lines above, m3 + m4 | rc=139 SIGSEGV | prints `1`,`2` — matches `iconx` |
| `ipl/progs/diffu.icn`, m3 + m4 | rc=139 SIGSEGV | rc=0, **byte-identical to `diffu.std`** |
| `ipl/progs/diffn.icn`, m3 + m4 | rc=139 SIGSEGV | rc=0, **byte-identical to `diffn.std`** |
| `jcon_tests/geddump.icn` fed `geddump.dat`, m3 + m4 | rc=139 SIGSEGV | rc=0, **byte-identical to `geddump.std`** (313 lines) |
| `geddump.icn` on hq_S's one-line `0 INDI` | rc=139 SIGSEGV | Run-time error 103 line 229 — **the same error `iconx` raises on the same input** |
| the widened gate | FAIL=7 of 17 | **PASS 17/17** |

⭐ So the flip on that one line is **three package programs × two modes to a byte-identical `.std`**, not a
crash count. ⚠️ One residue NOT claimed as this class: on the `0 INDI` input we name the file `geddump.icn`
where `iconx` names `gedcom.icn` — a link-file identity difference.

## THE ARMS ADDED, AND ONE THAT LIED BEFORE IT WAS FIXED

Four new arms, 5 → 17, ~13s measured. `gen_via_value` (above); **arm C**, the four named witnesses of CEO-507
run in both modes grading **signal death only** — geddump's output is hq_S's row and diffu/diffn are hq_R's,
and their refs moved twice today, so a gate that grades someone else's moving denominator goes red for their
landings rather than for its own class; **arm D**, a census of sites that *declare themselves alignment
compensation* rather than a count of `sub rsp, 8` (several of those are ABI words with real readers and their
own notes say which), with the two PL port-trace reporters exempted by name and with a reason.

⛔ **ARM C REPORTED A CLEAN PASS ON A SEGFAULTING PROGRAM BEFORE IT WAS CORRECTED, AND THE MECHANISM IS WORTH
MORE THAN THE ARM.** Field 1 of a `NAME.argv` sidecar is the **program name**, not an argument. Hand-splitting
the file passed `diffu` as `argv[1]`; the program exited rc=1 on a file that does not exist, **never reached
the misaligned door**, and printed `PASS diffu.icn m3`. ⭐ **A hand-rolled reader of a shared format does not
fail loudly — it grades a different program and prints the reassuring answer.** `ipl_argv_read` in
`lib_icon_ipl_isolation.sh` is the one authority and refuses rc=2 on a malformed sidecar; the arm now sources
it. This is the second instrument-blindness in one gate in one sitting, both found only by A/B-ing a build
that was known-good.

## WHY THE CURE IS NOT IN THIS LANDING

CEO-507 names the cure of record as the cto's CEO-504 and says it lands first, and there is an engineering
reason to respect that beyond the routing: `bb_call_value` is reached by the PL meta-call arm (`cv_pl_proto`)
and by Raku as well as Icon, so deleting the pad owes control arms this row has not run. The gate is landed
**REPORTED, NOT BLOCKING**, with its promotion back to blocking named in the recipe comment and owed the
commit after the cto lands: all seven FAILs are that one defect with a named owner, and pushing it blocking
would red a `make test` arm for every seat over a defect none of them caused (CEO-463). It is not softened —
it still exits 1 and still prints every FAIL line.

## NOT CLAIMED

The IPL board is **not** re-run here (rule 5) and hq_R has landed 14 new refs against the tree my 09:50 board
measured, so that board no longer describes this tree. No SNOBOL4, Prolog or Raku arm was run: nothing shared
moved, the diff is one shell script and one Makefile comment.
