# SESSION-snobol4-x64.md — SNOBOL4 × x64 ASM (snobol4x)

**Repo:** snobol4x · **Frontend:** SNOBOL4/SPITBOL · **Backend:** x64 ASM (NASM)
**Session prefix:** `B` (TINY backend) · **Trigger:** "playing with beauty" / TINY ASM

## Subsystems

| Subsystem | ARCH doc | Go there when |
|-----------|----------|---------------|
| x64 emitter deep ref | BACKEND-X64.md | register model, label conventions |
| beauty.sno plan | BEAUTY.md | beauty subsystem testing |
| sno2c implementation | ARCH-sno2c.md | compiler internals |

---
**Deep reference:** all ARCH docs cataloged in `ARCH-index.md`
---

## Status by Repo

| Repo | Implementation | Active sprint | Milestone |
|------|---------------|---------------|-----------||
| TINY | sno2c (C compiler) | `beauty-crosscheck` | M-BEAUTY-CORE |
| JVM | Clojure interpreter + JVM codegen | `jvm-inline-eval` | M-JVM-EVAL |
| DOTNET | C# interpreter + MSIL JIT | `net-delegates` | M-NET-DELEGATES |

---

## The Proof Program — beauty.sno

`beauty.sno` is the canonical correctness test for the SNOBOL4 frontend.
It is a self-contained SNOBOL4 parser and pretty-printer written in SNOBOL4.
If a backend can run `beauty.sno` self-beautification correctly, the SNOBOL4
frontend is correct on that backend.

**Self-beautification oracle test:**
```bash
INC=/home/claude/snobol4corpus/programs/inc
BEAUTY=/home/claude/snobol4corpus/programs/beauty/beauty.sno
snobol4 -f -P256k -I$INC $BEAUTY < $BEAUTY > oracle.sno
<backend-binary> < $BEAUTY > compiled.sno
diff oracle.sno compiled.sno   # empty = frontend correct on this backend
```

---

## How beauty.sno Works — The Two-Stack Engine

