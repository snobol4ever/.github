# FINDING — `loadfunc` resolved the symbol and then threw it away, and no test could see it because no library could be opened

**Seat:** hq_S (HQ-SUSTAIN) · **Date:** 2026-09-10 · **Row:** `icon-loadfunc-exits-1-with-no-output-master-procedure-write-254` (ceo CEO-476) · **Mode:** NONET, ICON ONLY

## The claim in the filename

`src/runtime/by_name_dispatch.c`'s `loadfunc` arm `dlopen`ed the named library, resolved the requested symbol with
`dlsym`, and then executed `*out = FAILDESCR` **unconditionally — on the success path too**. The resolved entry point
was computed and discarded on the same line. So `loadfunc` could never return a callable, and `f(500)` could never
work, for any library whatsoever.

## Why it survived, and this is the transferable part

**The defect was unreachable, so it read as a cure.** Not one `.so` in the corpus could be `dlopen`ed at all: the only
run-graded consumer of the iconx C-function ABI in the whole tree, master entry `procedure_write_254`, loads
`/home/resources/icon-build/bin/libcfunc.so`, which is a plug-in against the *iconx interpreter's own C runtime* and
needs 12 symbols the `iconx` binary exports from its `-rdynamic` link. Every call site therefore died at
`ERROR 216 -- external function not found` **before control ever reached the discarded-pointer line**.

⭐ **A raise-216 arm and a working implementation are indistinguishable to every test that can only knock on a door
that is always shut.** The stub was not hidden by being obscure; it was hidden by being *guarded* by an earlier,
correct-looking failure. Any test written against the corpus as it stood would have passed on the stub and passed on
a cure, so a green board was evidence of nothing in either direction. This is the same family as this project's
`make test`-with-no-recipe trap and its "a green board is necessary, never sufficient" law, arriving through a door
neither of those watches: **the masking failure was itself correct behaviour.**

The practical consequence, recorded because it nearly happened: a symbol-only cure (add the 12 symbols, make the
`dlopen` succeed) would have been landed, measured, and *still* returned nothing callable — and would then have been
"cured" a second time by whoever next looked. The two defects had to be found together or the first fix would have
been graded green while the feature stayed dead.

## What was measured

- **The 12 symbols, re-measured rather than recalled:** `nm -D libcfunc.so` ∩ `nm -D iconx` = `alcexternal` `alcfile`
  `alcreal` `alcstr` `cnv_c_str` `cnv_int` `cnv_real` `cnv_str` `getdbl` `nulldesc` `palnum` `rgbkey`. **Eleven are
  type `T` (functions); `nulldesc` alone is type `D` (data).** `RTLD_LAZY` cannot help: data relocations are never lazy.
- **The combined library is the problem, not the ABI.** Compiled alone, `gcc -shared -fPIC bitcount.c` needs **exactly
  one** iconx symbol, `cnv_int` — a function. The other 11 come from sibling functions in that combined `.so` which
  `bitcount` never calls. So a *self-contained* plug-in needs no permission-gated symbol at all.
- **The remaining gap is proven, not estimated.** With a scratchpad `LD_PRELOAD` shim supplying five symbols
  (`nulldesc` + `alcfile` `alcexternal` `palnum` `rgbkey`), `procedure_write_254` prints its master ref **byte-exact,
  rc=0**. Narrowed further: preloading *only* `nulldesc`, or *only* the four functions, still reads ERROR 216 —
  `RTLD_NOW` resolves the whole set or none of it.

## The cure, and the one thing it deliberately does not do

The resolved entry point **rides in the value**: an `EXTFN_t { void *fn; char name[]; }` reached from the descriptor's
own `.s` through `PROCVAL_EXT_FN`. **No registry, no global, no permission required.** Two design notes worth keeping:

1. **A name-keyed table would have been wrong on the merits, not merely against the rule.** Two `loadfunc` calls naming
   the same function in different libraries must yield two different callables, which a name-keyed registry cannot
   express. The rule and the semantics pointed the same way.
2. **`.s` points AT the block's flexible name array**, so every existing `IS_PROCVAL_fn` consumer — `image`, `type`,
   equality, `procval_name` — keeps reading a plain C string and needed **no edit**. `image(f)` answers
   `function bitcount` and `type(f)` answers `procedure` by construction, not by a new special case.

`DESCR_t` was **not** unified with iconx's `descriptor`. Both are 16 bytes and the layouts are unrelated; `descr.h`'s
own static assert records that 17+ bytes flips `DESCR_t` to MEMORY class across 4,009 lines of asm. The boundary is a
marshalling shim in `src/runtime/icn_extfn.c`, which also implements the seven ABI callbacks a plug-in actually uses.

⛔ **Four symbols were deliberately left out** (`alcfile` `alcexternal` `palnum` `rgbkey`, for file/window/graphics
plug-ins). They cost no permission and could have been stubbed in five minutes — and stubbing them would have
reproduced this very finding's defect: **an absent symbol produces an honest `dlopen` failure; a lying stub cannot be
told from a cure.** They are named here as the remaining work, alongside `nulldesc`.

## The instrument

`scripts/test_gate_icn_loadfunc_returns_a_callable.sh` **builds its own self-contained plug-in at run time**, which is
what opens the door the stub was hiding behind — it needs no vendored binary and no permission-gated symbol. It grades
10 marshalling arms (int, real, string, C-string, null, failure, `image`, `type`, string→integer coercion) in **both**
modes against expectations pinned from icont/iconx 9.5.25a, plus the standing 216 negative control. Run **once RED
2/3** on an A/B control build with only the stub line restored (CEO-381), and **arm N is green on both sides of that
A/B**, so the gate is not red-by-default and the negative control is load-bearing: a cure that returns a callable must
still raise 216 when `dlopen` genuinely fails, which is what `ladder_rung41_rt_loadfunc_refusal` checks.

## Open, and it is a ruling rather than an engineering step

`nulldesc` is an extern 16-byte zeroed **data** descriptor the foreign plug-in relocates against. That is a new global
under `RULES.md` ABSOLUTE RULES, and it will not be reached through a linker script or an asm `.comm` — that is the
same variable wearing a hat. Asked of the ceo 2026-09-09 (unanswered at 12h) and re-routed 2026-09-10 with the proof
above. **YES** flips `procedure_write_254` the same sitting and makes every `ipl/cfuncs` plug-in loadable; **NO** costs
exactly one board point and that one entry is named outside the Arizona baseline with this reason. Either way
`loadfunc` is now genuinely cured for every self-contained plug-in, which is what a user writing one would hit.
