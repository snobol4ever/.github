# FINDING 2026-09-09 hq_R — twelve Icon builtins are callable inline but invisible to `proc()`, so they cannot be passed as values

**OPEN, NOT CURED.** Measured against `/home/resources/icon-master/bin/icont`. hq_R's lane (builtins).
Found while diagnosing the IPL A–F red `progs/chkhtml`; **not yet proven to be chkhtml's cause** — see the
honesty note at the end, which matters more than the gap itself.

## The witness

```icon
procedure main();
   local n, names;
   names := ["find","key","many","match","move","pos","tab","upto","any","bal","exit","runerr",
             "map","trim","reverse","sort","close","copy","delete","get","image","insert","member",
             "open","push","put","read","set","stop","string","table","type","write"];
   every n := !names do
      if not proc(n) then write("MISSING: ", n);
   write("-- scan done --");
end
```

`icont` prints only `-- scan done --`. **SCRIP reports twelve MISSING:**

`find` · `key` · `many` · `match` · `move` · `pos` · `tab` · `upto` · `any` · `bal` · `exit` · `runerr`

⭐ **The shape of the set is the clue:** ten of the twelve are the string-scanning builtins
(`tab move upto many any match find bal pos`) plus `key`, `exit` and `runerr`. These are exactly the
names SCRIP lowers to dedicated IR boxes (`IR_SCAN_TAB`, `IR_SCAN_UPTO`, …) rather than routing through
the ordinary builtin call path — so they work perfectly when written inline and do not exist as
first-class procedure values at all. Every one of the twenty-one names that lowers to an ordinary call
is present. **A builtin that is compiled away is a builtin that `proc()` cannot find**, and Icon
programs legitimately pass these as values: `proc("tab", 1)`, `every f := proc(!names) do …`, and the
IPL habit of defaulting a comparison or scanner argument to a builtin.

## Why this is filed as OPEN rather than as chkhtml's cure

⛔ **I have NOT shown this is what `chkhtml` trips on, and I am not implying it.** What is measured about
chkhtml: it prints its first two lines, then dies with `ERROR 022 — Undefined function called`; the raise
site is `rt_ab_undef_fn_stub`, reached from a `bb_call_proc_staged` fallback arm (`.Lcall_proc_staged_α_87_1`
in its emitted `.s`), i.e. **a call through a value that is not a procedure at run time** — which is the
right family. But the twenty-odd builtins chkhtml uses inline all resolve, and `set()`, `table()`, `list()`
with zero arguments were all checked directly against the oracle and are correct. The specific callee is
not yet named. `SCRIP_DEBUG_APPLY=1` does NOT print for it, which is itself informative: the failure is
NOT going through `core_apply_by_name` (core.c:3363) but through the compile-time-emitted stub, so the
name was already unresolved when the code was emitted.

⭐ Recording the gap and the non-proof separately, because folding them together would put an unproven
"this is chkhtml's cause" into the record, and a plausible cause written down as a fact is how the miu
brief sent the cto to the wrong file earlier today.

## Next

Name chkhtml's callee first (the `.Lcall_proc_staged_α_87` site and its operand chain, or a `--dump-bb`
of the enclosing procedure). Then cure the `proc()` gap on its own merits: the twelve need entries in
whatever table `proc()` consults, with bodies that route to the same runtime the boxes use, so that a
value-called `tab` behaves as an inline `tab` does.
