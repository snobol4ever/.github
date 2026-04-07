#!/usr/bin/env bash
# snobol4ever_clone.sh — clone selected snobol4ever repos
#
# Usage:
#   mkdir ~/snobol4ever && cd ~/snobol4ever
#   git clone https://github.com/snobol4ever/.github
#   bash .github/snobol4ever_clone.sh PROFILE_OR_REPOS...
#
# Repos are cloned as subdirectories of wherever you run this script.
# Credentials come from your git config / GitHub Desktop — no token needed.
#
# Profiles:
#   interp     — .github one4all harness corpus
#   jvm        — .github snobol4jvm harness corpus
#   dotnet     — .github snobol4dotnet harness corpus
#   spitbol    — .github one4all harness corpus x64
#   all        — every repo in the org
#
# Or list repos explicitly:
#   bash .github/snobol4ever_clone.sh one4all corpus harness
#
# Options:
#   --token TOKEN   GitHub PAT (only needed if not using GitHub Desktop / git credential store)
#   --ssh           Clone via SSH instead of HTTPS
#
# Safe to re-run — already-cloned repos are skipped.

set -euo pipefail

# ── All known repos ───────────────────────────────────────────────────────────
ALL_REPOS=(
    .github
    corpus
    harness
    one4all
    snobol4artifact
    snobol4csharp
    snobol4dotnet
    snobol4jvm
    snobol4python
    x32
    x64
)

# ── Profiles ──────────────────────────────────────────────────────────────────
profile_interp()  { echo ".github one4all harness corpus"; }
profile_jvm()     { echo ".github snobol4jvm harness corpus"; }
profile_dotnet()  { echo ".github snobol4dotnet harness corpus"; }
profile_spitbol() { echo ".github one4all harness corpus x64"; }
profile_all()     { echo "${ALL_REPOS[*]}"; }

# ── Argument parsing ──────────────────────────────────────────────────────────
TOKEN="${GH_TOKEN:-}"
USE_SSH=0
TARGETS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --token) TOKEN="$2"; shift 2 ;;
        --ssh)   USE_SSH=1;  shift ;;
        interp|jvm|dotnet|spitbol|all)
            profile="$1"; shift
            read -ra expanded <<< "$(profile_${profile})"
            TARGETS+=("${expanded[@]}")
            ;;
        --help|-h)
            sed -n '2,/^set /p' "$0" | grep '^#' | sed 's/^# \?//'
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"; exit 1 ;;
        *)
            TARGETS+=("$1"); shift ;;
    esac
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
    echo "Usage: bash snobol4ever_clone.sh [--token TOKEN] PROFILE_OR_REPOS..."
    echo "Profiles: interp  jvm  dotnet  spitbol  all"
    echo "Repos:    ${ALL_REPOS[*]}"
    exit 1
fi

# ── Deduplicate while preserving order ────────────────────────────────────────
declare -A seen
REPOS=()
for r in "${TARGETS[@]}"; do
    if [[ -z "${seen[$r]+x}" ]]; then
        seen[$r]=1
        REPOS+=("$r")
    fi
done

# ── Clone ─────────────────────────────────────────────────────────────────────
for repo in "${REPOS[@]}"; do
    if [[ -d "$repo/.git" ]]; then
        echo "SKIP    $repo  (already cloned — use GitHub Desktop to update)"
        continue
    fi
    if [[ $USE_SSH -eq 1 ]]; then
        url="git@github.com:snobol4ever/${repo}.git"
    elif [[ -n "$TOKEN" ]]; then
        url="https://${TOKEN}@github.com/snobol4ever/${repo}"
    else
        url="https://github.com/snobol4ever/${repo}"
    fi
    echo "CLONE   $repo"
    git clone --quiet "$url" "$repo"
done

echo ""
echo "Done. Add these folders to GitHub Desktop for day-to-day workflow."
