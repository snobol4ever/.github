# SESSION-linker-net.md — SCRIP Linker: .NET Track

**Track:** LINKER (LP) — .NET only. Jeff's snobol4dotnet is a separate track, does not block this.
**Session prefix:** `LP` · **Trigger:** "playing with linker net"
**Gate:** Read `ARCH-scrip-abi.md` before touching any code.

---

## §SUBSYSTEMS

| Subsystem | Doc | Go there when |
|-----------|-----|---------------|
| SCRIP ABI / calling convention | `ARCH-scrip-abi.md` | any cross-lang call site |
| .NET emitter | `BACKEND-NET.md` | CIL patterns, ilasm |
| JVM linker (parallel track) | `SESSION-linker-jvm.md` | reference only |

---

## §BUILD

```bash
TOKEN=ghp_xxx bash /home/claude/.github/SESSION_BOOTSTRAP.sh
```

Requires: `ilasm` (Mono). NET corpus at `test/linker/net/`.

---

## §NOW — LP-9

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **LINKER .NET** | LP-9 | `cce1c3a` one4all · `e03add2` .github | M-SCRIP-XLINK-1 |

### State at LP-8g (current baseline)

**Green:** M-LINK-NET-8 ✅ — all six cross-language edges (SNOBOL4↔Prolog↔Icon) pass.
**Corpus:** 109/110 NET (056_pat_star_deref @N off-by-one — pre-existing, not a blocker).

**Syntax:** `-EXPORT` / `-IMPORT` are proper control lines handled in `lex.c` scanner. Parser never sees them.

**Known emitter bug (non-blocking):** `OUTPUT = 'prefix' IMPORT_CALL(args)` in single expression → stack-depth verifier failure (`brfalse` on omega path leaves prefix stranded). Workaround: two-step assignment. Fix in `emit_byrd_net.c` import call block — push `""` on omega path.

### Next: M-SCRIP-XLINK-1 — Five languages in one linked program

Requires:
1. `icon_emit_net.c` — Icon → CIL emitter (model on `icon_emit_jvm.c`)
2. Snocone .NET emitter stub
3. Five-language acceptance test

**Known stubs blocking this:**
- `prolog_emit_net.c`: intermediate variable binding (Z in transitive rules) not implemented
- `icon_emit_net.c`: does not exist — hand-authored `fibonacci.il` used in LP-8g
- `demo_prolog.il` / `demo_icon.il`: hand-authored — no compiler generates them yet

**Regression test:**
```bash
bash test/linker/net/three_lang/run.sh
# expect: sno4->prolog: ann | sno4->icon: 13 | prolog->sno4: Hello World | prolog->icon: 5 | icon->sno4: Hello, Icon | icon->prolog: ann
```
