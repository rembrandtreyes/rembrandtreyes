#!/usr/bin/env bash
# Rewrite the block between <!-- RECENT:START --> and <!-- RECENT:END --> in README.md
# with the repos I was most recently active in (from the public event feed, which covers the last 90 days). Needs gh (authenticated) and jq.
set -euo pipefail
cd "$(dirname "$0")/.."

owner=${OWNER:-rembrandtreyes}
limit=${LIMIT:-5}

list=$(gh api "users/$owner/events/public?per_page=100" |
  jq -r --arg owner "$owner" --argjson limit "$limit" '
    def ago: ((now - (. | fromdateiso8601)) / 86400 | floor)
      | if . == 0 then "today" elif . == 1 then "yesterday" else "\(.) days ago" end;
    [ .[] | select(.repo.name != "\($owner)/\($owner)") ]
    | group_by(.repo.name)
    | map({
        repo: .[0].repo.name,
        last: (map(.created_at) | max),
        pushes: (map(select(.type == "PushEvent")) | length),
        release: (map(select(.type == "ReleaseEvent")) | sort_by(.created_at) | last | .payload.release.tag_name?),
        created: (any(.[]; .type == "CreateEvent" and .payload.ref_type == "repository")),
        prs: (map(select(.type == "PullRequestEvent" and .payload.action == "opened")) | length)
      })
    | sort_by(.last) | reverse | .[:$limit][]
    | (if (.repo | startswith("\($owner)/")) then (.repo | split("/")[1]) else .repo end) as $name
    | ([ (if .release then "released `\(.release)`" else empty end),
         (if .created then "created it" else empty end),
         (if .pushes > 0 then "\(.pushes) push\(if .pushes > 1 then "es" else "" end)" else empty end),
         (if .prs > 0 then "opened \(.prs) PR\(if .prs > 1 then "s" else "" end)" else empty end)
       ] | join(", ")) as $what
    | "- **[\($name)](https://github.com/\(.repo))**: \(if $what == "" then "active" else $what end) <sub>· \(.last | ago)</sub>"')

tmp=$(mktemp)
LIST="$list" awk '
  /<!-- RECENT:START -->/ { print; print ENVIRON["LIST"]; skip = 1; next }
  /<!-- RECENT:END -->/   { skip = 0 }
  !skip
' README.md > "$tmp"
mv "$tmp" README.md
