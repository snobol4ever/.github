# FINDING — under the armed N-2 protocol, a value received FROM a suspended generator silently reads as empty when used as a TABLE SUBSCRIPT, even though the same value works fine as a plain argument

**Seat:** `seat15` · 2026-08-29 · row `icon-bench-correct-suspend-residue` (formerly `icon-bench-correct-zero-of-eight`, renamed by ceo this session — the **acceptance** side of N-2, `icon-n2-generator-activation-frames`)
**Trees:** SCRIP `c8a5fcd5` (pristine build; includes ceo's `77e8e423` loop/after cure) · corpus unchanged this session · .github this commit
**Oracle:** Arizona `icont`/`iconx` via `lib_oracle_flags.sh` accessors, verified executable and executed for every witness below.
**Gate:** `SCRIP_ICN_GENFRAME2=1` (armed). Unarmed is the pre-existing baseline crash (`suspend` in a user procedure segfaults on first call) — there is no working unarmed run to cross-check against, so every comparison below is armed-vs-oracle.

## 0. Context: a stale-build false alarm, corrected same-session

First pass at this row's own acceptance work (`concord`, one of the three real-`suspend` programs in `bench_correct`) measured on SCRIP `143559b7` and found `concord` HANGING under the armed gate — 3 good lines then no progress for 120s+. Built a minimal witness, reported it to `ceo` as new. It was not: `77e8e423` (ceo's own loop/after cure, landed on origin/main between the pull that produced `143559b7` and the report) fixes it — re-pulled to `c8a5fcd5`, rebuilt, re-ran the identical witness, passes clean. Sent a correction immediately. Recorded here only as a process note: **on a rung moving this fast, pull immediately before measuring, not after** — a build that was current ten minutes ago is not current.

## 1. `concord`'s real current state: DIVERGE, not crash or hang

`honest_icon_correctness.sh` computes its oracle live via real `iconx` every run, never a checked-in `.std`. The row's own baton quoted `concord` as "30 of the oracle's 38 lines" — that figure is stale, read off the checked-in `concord.std` rather than a live run. The true oracle window is **1345 lines** (`concord.dat` is a genuine 894-line input, an `ICONT(1)` man page).

At `c8a5fcd5`, armed:
- Input-echo section (oracle lines 1–894) matches the oracle **exactly**.
- The sorted-concordance tail (oracle lines 895–1345 — the actual point of the program) does not: SCRIP collapses roughly 450 distinct word entries into **one entry with an empty key**, holding every citation number concatenated together in sequence.

`geddump`/`tgrlink` are unchanged — both still hit the documented forward-reference refusal (`[GENHOST] host=proc_event` / `host=proc_dumpcode`), routed to `icon-n2-forward-ref-gen-prepass`. Not this finding's subject.

## 2. Isolated to three minimal witnesses, each removing one variable at a time

**(a) A generator-resumed value used as a plain argument — WORKS:**
```icon
procedure item()
   local word; local line;
   line := "ICONT UNIX Manual";
   line ? { while tab(upto(&letters)) do { word := tab(many(&letters)); if *word >= 3 then suspend word } }
end
procedure tabulate(name)
   write("got: ", name);
end
procedure main()
   every tabulate(item());
   write("DONE");
end
```
Oracle: `got: ICONT / got: UNIX / got: Manual / DONE`, rc=0. SCRIP armed: **identical**, rc=0.

**(b) A non-generator (static) value used as a table subscript — WORKS:**
```icon
procedure main()
   local t, ulist, name;
   t := table("");
   t["zebra"] := "1, 2"; t["apple"] := "3, 4, 5"; t["mango"] := "6";
   ulist := sort(t, 3);
   while name := get(ulist) do write(name, " -> ", get(ulist));
end
```
Oracle: `apple -> 3, 4, 5 / mango -> 6 / zebra -> 1, 2`. SCRIP m3 and m4: **identical**, both modes, rc=0.

**(c) A generator-resumed value used as a table subscript — BROKEN.** First via a direct subscript on the call:
```icon
procedure gen()
   local i; every i := 1 to 400 do suspend "word" || (i % 5);
end
procedure main()
   local t, n; t := table(""); n := 0;
   every t[gen()] ||:= (n +:= 1) || ", ";
   ulist := sort(t, 3);
   while name := get(ulist) do write(name, " -> ", get(ulist));
end
```
then reproduced again through a formal parameter — concord's own actual shape (the suspended value received as an ordinary procedure argument, THEN used to subscript a table inside that procedure body, exactly as `tabulate(name, lineno)` does with `uses[name]`):
```icon
procedure gen()
   local i; every i := 1 to 400 do suspend "word" || (i % 5);
end
procedure tabulate(name, n)
   static t; initial t := table("");
   t[name] ||:= n || ", ";
   return t;
end
procedure main()
   local t, n; n := 0;
   every t := tabulate(gen(), n +:= 1);
   ulist := sort(t, 3);
   while name := get(ulist) do write(name, " -> ", get(ulist));
end
```
Oracle (both forms): 5 distinct keys, correctly bucketed —
```
word0 -> 5, 10, 15, 20, ..., 400,
word1 -> 1, 6, 11, 16, ..., 396,
word2 -> 2, 7, 12, 17, ..., 397,
word3 -> 3, 8, 13, 18, ..., 398,
word4 -> 4, 9, 14, 19, ..., 399,
```
SCRIP armed (both forms, identical failure shape): **one entry, empty key, everything dumped into it** —
```
 -> 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ..., 400,
```

## 3. What this isolates, and what it does not

The three witnesses hold everything constant except one axis each: (a) proves a resumed value is readable when consumed as an argument; (b) proves table-subscript-then-sort-then-get is correct when the subscript is not generator-derived; (c) proves the SAME resumed value, consumed as a subscript instead of an argument — whether directly on the call or forwarded through an ordinary parameter first — reads as empty. The formal-parameter variant of (c) matters specifically because it rules out "maybe subscripting a bare generator call is special-cased wrong" as the whole story — concord never subscripts a generator call directly, only a parameter that received one.

**Not established:** which stage of the armed protocol drops the value on the subscript path specifically — whether the yielded descriptor is read through a different accessor for subscript evaluation than for argument binding, a timing/ordering issue in when the descriptor becomes readable relative to subscript evaluation, or something else. Not chased into the emitter or templates — this is `icon-n2-generator-activation-frames`'s mechanism (the value-transfer half of N-2, per that row's own `.github/FINDING-2026-08-27-hq_P-armed-n2-mode4-segfaults-intermittently-and-a-single-shot-witness-cannot-see-it.md` § 6.1, "the value path... the result descriptor is not [carried]" — plausibly the same root cause resurfacing now that the crash it used to hide behind is fixed, but that connection is speculation, not measured here, and is flagged as such rather than asserted).

## 4. Row status

⛔ **No cure written — not this row's claim to make.** `icon-bench-correct-suspend-residue`'s own GOAL text: *"DO NOT WRITE A CURE UNDER THIS ROW. THE CURE IS RUNG `icon-n2-generator-activation-frames`."* Sent both the stale-build correction and this finding to `ceo` (claim holder on `icon-n2-generator-activation-frames` at time of writing) with full witness text; added a QA note to that row's task file so the finding survives independent of mail being read promptly. Released this row's claim — `concord`'s remaining gap is squarely N-2's mechanism, not the acceptance row's to chase further solo.

What advanced: `concord`'s failure mode is now precisely characterized (crash → hang [transient, already cured] → diverge-on-tail, isolated to one specific, previously-uncatalogued value-propagation path) rather than left as an unexplained line-count shortfall.
