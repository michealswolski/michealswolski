#!/usr/bin/env python3
"""Generate the GitHub stat cards used by the profile README.

Why these are generated rather than embedded from a hosted service:

The README used to pull its stats, language breakdown, streak, activity graph
and trophies from community-run instances (github-readme-stats.vercel.app,
streak-stats.demolab.com, github-profile-trophy.vercel.app). Those are shared
free deployments — they rate-limit under load, cold-start slowly, and return
502s often enough that a visitor regularly sees broken images on the profile.
There is no way to fix that from this side, because the rendering happens on
someone else's server.

These cards render here instead, from the public GitHub API, and are published
to the `output` branch by the same workflow that builds the contribution snake.
They are served from this repository, so they load as reliably as any other
asset and match the palette in build_assets.py exactly.

Failure behaviour is deliberate: if the API can't be reached, the script exits
non-zero and the workflow stops *before* publishing. The previously generated
cards stay on the `output` branch, so the README keeps showing the last good
data rather than breaking. Stale numbers beat broken images.

Usage:
    python3 tools/build_stats.py [output_dir]
    python3 tools/build_stats.py [output_dir] --fixture   # render sample data
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_assets import MONO, SANS, THEMES  # noqa: E402

USER = "michealswolski"
API = "https://api.github.com"

# Domain taxonomy for the focus card. Keyed by repository name so the counts
# stay honest — this is a grouping of work that exists, not a wish list.
DOMAINS = [
    ("Automotive &amp; Embedded", "cyan", [
        "obd2-diagnostic-scanner", "secure-boot-research", "ford-ecu-detector",
        "s650-mustang-mod-tracker",
    ]),
    ("AI Agent Security", "green", [
        "ai-agent-governance", "365-whitepaper-agent", "document-analyzer-ai",
        "agentforge",
    ]),
    ("Detection &amp; SIEM", "blue", [
        "splunk-siem-lab", "python-log-automation", "network-traffic-analysis",
    ]),
    ("Offensive &amp; Vuln Mgmt", "amber", [
        "offensive-security-lab", "web-app-security-lab", "openvas-scanning",
        "homelab-vuln-management", "system-hardening-lab", "firewall-vpn-lab",
        "pki-ca-research", "hacked-terminal-wallpaper",
    ]),
    ("Full-Stack &amp; Platform", "cyan_l", [
        "auto-job-intel", "forecast-ai", "Project-database",
        "bosch-project-dashboard", "bosch-project-database",
        "wolski-command-center", "meshlink-ios", "network-utility-tool",
        "gameprep-pro", "depass-grading-website", "michealswolski.github.io",
    ]),
]


# --------------------------------------------------------------------- fetch

def _get(url: str):
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USER}-profile-cards",
        **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
           if os.environ.get("GITHUB_TOKEN") else {}),
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def fetch_data() -> dict:
    user = _get(f"{API}/users/{USER}")

    repos = []
    for page in range(1, 6):
        batch = _get(f"{API}/users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break

    owned = [r for r in repos if not r["fork"]]
    active = [r for r in owned if not r["archived"]]

    # Language bytes, summed across every non-fork repo. Byte counts are a far
    # better picture than counting repos: a one-file research repo and a
    # 60-file application should not weigh the same.
    languages: dict[str, int] = {}
    for repo in owned:
        try:
            for name, size in _get(f"{API}/repos/{USER}/{repo['name']}/languages").items():
                languages[name] = languages.get(name, 0) + size
        except urllib.error.HTTPError:
            continue  # a repo with no classified language just contributes nothing

    # Repos pushed to within the last year. Counted here rather than shown as a
    # streak, because a streak measures how often you open GitHub and this
    # measures how much of the work is still moving.
    recent = _recent_count(owned)

    return {
        "repos": len(active),
        "archived": len(owned) - len(active),
        "code_bytes": sum(languages.values()),
        "recent": recent,
        "languages": dict(sorted(languages.items(), key=lambda kv: -kv[1])),
        "repo_names": [r["name"] for r in owned],
    }


def _recent_count(repos: list) -> int:
    """Repos pushed to in the last 365 days, by ISO date string comparison."""
    from datetime import datetime, timedelta, timezone
    cutoff = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")
    return sum(1 for r in repos if (r.get("pushed_at") or "")[:10] >= cutoff)


FIXTURE = {
    "repos": 29, "archived": 2, "code_bytes": 929_000, "recent": 23,
    "languages": {"JavaScript": 486_000, "TypeScript": 214_000, "HTML": 96_000,
                  "PowerShell": 71_000, "CSS": 44_000, "Python": 18_000},
    "repo_names": [n for _, _, names in DOMAINS for n in names],
}


# -------------------------------------------------------------------- shared

def _shell(t: dict, w: int, h: int, title: str, aria: str) -> list[str]:
    """Card background, border, and corner accent — shared by every card."""
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{aria}">',
        f'  <title>{title}</title>',
        '  <defs>',
        f'    <linearGradient id="cBg" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{t["bg0"]}"/>'
        f'<stop offset="60%" stop-color="{t["bg1"]}"/>'
        f'<stop offset="100%" stop-color="{t["bg2"]}"/></linearGradient>',
        f'    <linearGradient id="cEdge" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{t["cyan"]}" stop-opacity="0.9"/>'
        f'<stop offset="100%" stop-color="{t["green"]}" stop-opacity="0.25"/></linearGradient>',
        '  </defs>',
        f'  <rect width="{w}" height="{h}" rx="14" fill="url(#cBg)"/>',
        f'  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="13.5" fill="none" '
        f'stroke="{t["stroke"]}"/>',
        f'  <rect x="18" y="0" width="86" height="2" fill="url(#cEdge)"/>',
    ]


def _heading(t: dict, x: int, y: int, text: str) -> str:
    return (f'  <text x="{x}" y="{y}" font-family="{MONO}" font-size="11" '
            f'letter-spacing="1.6" fill="{t["cyan"]}">{text}</text>')


# --------------------------------------------------------------------- stats

SW, SH = 440, 196


def _kb(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    return f"{round(n / 1000):,}K"


def stats(t: dict, d: dict) -> str:
    """Deliberately no star or follower counts.

    Both are popularity metrics rather than engineering ones, and on a working
    portfolio that nobody has starred yet they read as a weakness the profile
    volunteers about itself. Every number here describes the work instead.
    """
    code = _kb(d["code_bytes"])
    p = _shell(t, SW, SH, "GitHub statistics",
               f'GitHub statistics: {d["repos"]} public repositories, '
               f'{len(d["languages"])} languages, {code} of code, '
               f'{d["recent"]} repositories updated in the last year.')
    add = p.append
    add(_heading(t, 24, 34, "GITHUB  STATS"))

    cells = [
        (str(d["repos"]), "Public repos", "cyan"),
        (str(len(d["languages"])), "Languages", "green"),
        (code, "Of code", "blue"),
        (str(d["recent"]), "Active this year", "amber"),
    ]
    for i, (value, label, colour) in enumerate(cells):
        cx = 24 + (i % 2) * 208
        cy = 78 + (i // 2) * 60
        add(f'  <text x="{cx}" y="{cy}" font-family="{SANS}" font-size="29" font-weight="700" '
            f'fill="{t[colour]}">{value}</text>')
        add(f'  <text x="{cx}" y="{cy + 19}" font-family="{SANS}" font-size="12" '
            f'fill="{t["dim"]}">{label}</text>')

    add('</svg>')
    return "\n".join(p) + "\n"


# ----------------------------------------------------------------- languages

LW, LH = 440, 196
LANG_COLOURS = ("cyan", "green", "blue", "amber", "cyan_l", "dim")


def languages(t: dict, d: dict) -> str:
    top = list(d["languages"].items())[:6]
    total = sum(size for _, size in top) or 1

    p = _shell(t, LW, LH, "Most used languages",
               "Most used languages by bytes of code across public repositories: "
               + ", ".join(f"{n} {size * 100 // total}%" for n, size in top) + ".")
    add = p.append
    add(_heading(t, 24, 34, "LANGUAGES  ·  BY  BYTES"))

    # Stacked bar. Rounded ends come from a clip path so segments stay square
    # against each other but the bar itself reads as one pill.
    bar_x, bar_y, bar_w, bar_h = 24, 52, LW - 48, 12
    add(f'  <defs><clipPath id="lBar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" '
        f'height="{bar_h}" rx="6"/></clipPath></defs>')
    add(f'  <g clip-path="url(#lBar)">')
    x = float(bar_x)
    for i, (_, size) in enumerate(top):
        seg = bar_w * size / total
        add(f'    <rect x="{x:.1f}" y="{bar_y}" width="{seg:.1f}" height="{bar_h}" '
            f'fill="{t[LANG_COLOURS[i % len(LANG_COLOURS)]]}"/>')
        x += seg
    add('  </g>')

    # Two-column legend. The percentage is right-aligned to a fixed column edge
    # rather than offset from an estimated text width — estimating produced
    # "HTML10.3%" with no gap on the shorter names.
    col_w = 196
    for i, (name, size) in enumerate(top):
        col, row = i % 2, i // 2
        lx = 24 + col * col_w
        ly = 100 + row * 28
        add(f'  <circle cx="{lx + 5}" cy="{ly - 4}" r="5" '
            f'fill="{t[LANG_COLOURS[i % len(LANG_COLOURS)]]}"/>')
        add(f'  <text x="{lx + 17}" y="{ly}" font-family="{SANS}" font-size="12.5" '
            f'fill="{t["text"]}">{name}</text>')
        add(f'  <text x="{lx + col_w - 26}" y="{ly}" text-anchor="end" font-family="{MONO}" '
            f'font-size="11" fill="{t["faint"]}">{size * 100 / total:.1f}%</text>')

    add('</svg>')
    return "\n".join(p) + "\n"


# --------------------------------------------------------------------- focus

FW, FH = 900, 224


def focus(t: dict, d: dict) -> str:
    owned = set(d["repo_names"])
    rows = [(label, colour, len([n for n in names if n in owned]))
            for label, colour, names in DOMAINS]
    rows = [r for r in rows if r[2] > 0]
    peak = max((n for _, _, n in rows), default=1)

    p = _shell(t, FW, FH, "Where the work sits",
               "Public repositories by security domain: "
               + ", ".join(f'{lbl.replace("&amp;", "and")} {n}' for lbl, _, n in rows) + ".")
    add = p.append
    add(_heading(t, 26, 34, "WHERE  THE  WORK  SITS"))
    add(f'  <text x="{FW - 26}" y="34" text-anchor="end" font-family="{MONO}" font-size="10" '
        f'fill="{t["faint"]}">public repositories by domain</text>')

    label_w, track_x = 210, 262
    track_w = FW - track_x - 60
    for i, (label, colour, count) in enumerate(rows):
        y = 68 + i * 27
        add(f'  <text x="26" y="{y + 4}" font-family="{SANS}" font-size="13" '
            f'fill="{t["text"]}">{label}</text>')
        add(f'  <rect x="{track_x}" y="{y - 6}" width="{track_w}" height="11" rx="5.5" '
            f'fill="{t[colour]}" opacity="0.14"/>')
        fill_w = max(track_w * count / peak, 11)
        add(f'  <rect x="{track_x}" y="{y - 6}" width="{fill_w:.1f}" height="11" rx="5.5" '
            f'fill="{t[colour]}"/>')
        add(f'  <text x="{FW - 34}" y="{y + 4}" text-anchor="end" font-family="{MONO}" '
            f'font-size="12" fill="{t["dim"]}">{count}</text>')

    add(f'  <text x="26" y="{FH - 14}" font-family="{MONO}" font-size="9.5" '
        f'fill="{t["faint"]}">counted from public repositories — see each repo for what it '
        f'contains</text>')
    add('</svg>')
    return "\n".join(p) + "\n"


# ---------------------------------------------------------------------- main

CARDS = {"stats": stats, "languages": languages, "focus": focus}


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = Path(args[0] if args else "assets")
    out.mkdir(parents=True, exist_ok=True)

    if "--fixture" in sys.argv:
        data = FIXTURE
        print("using fixture data")
    else:
        try:
            data = fetch_data()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as err:
            # Exit non-zero on purpose: the workflow stops before publishing, so
            # the cards already on the output branch survive untouched.
            print(f"error: GitHub API unreachable ({err}); "
                  f"keeping previously published cards", file=sys.stderr)
            sys.exit(1)
        print(f"fetched {data['repos']} repos, {len(data['languages'])} languages")

    for theme in THEMES.values():
        for stem, fn in CARDS.items():
            path = out / (f"{stem}{theme['suffix']}.svg")
            path.write_text(fn(theme, data), encoding="utf-8")
            print("wrote", path)


if __name__ == "__main__":
    main()
