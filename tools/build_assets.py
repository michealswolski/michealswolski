#!/usr/bin/env python3
"""Generate the animated SVG assets used by the profile README.

One source of truth per asset; each is emitted in a dark and a light palette so
the README can serve the right one via <picture media="(prefers-color-scheme:...)">.

Two rules keep these safe wherever they are rendered:

  * Every animated reveal has a *visible* resting state. If animations never run
    -- reduced-motion preference, a renderer without SMIL, a still thumbnail --
    the artwork still reads correctly. Nothing important is hidden behind an
    animation that may not play.
  * Perpetual loops use CSS so they can be switched off inside a
    @media (prefers-reduced-motion: reduce) block. One-shot intros use SMIL with
    fill="freeze" and a leading hold, so they settle into the base state.

Usage: python3 tools/build_assets.py [output_dir]
"""

import sys
from pathlib import Path

SANS = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
MONO = "'SF Mono', 'JetBrains Mono', Consolas, 'Courier New', monospace"

THEMES = {
    "dark": {
        "suffix": "",
        "bg0": "#050B16", "bg1": "#0A1526", "bg2": "#0F1F35",
        "grid": "#3B82F6", "grid_op": "0.075",
        "text": "#E2E8F0", "head": "#F8FAFC",
        "dim": "#94A3B8", "faint": "#64748B",
        "cyan": "#22D3EE", "cyan_l": "#67E8F9",
        "blue": "#3B82F6", "green": "#34D399", "amber": "#FBBF24",
        "panel": "#0B1526", "panel_op": "0.72",
        "stroke": "#1E293B",
        "orb_op": "0.50", "scan_op": "0.40",
        "shine": "#FFFFFF", "shine_op": "0.26",
        "clasp": "#475569", "clasp_edge": "#94A3B8", "strap_text": "#F0FDFF",
    },
    "light": {
        "suffix": "-light",
        "bg0": "#F7FBFE", "bg1": "#EAF3FA", "bg2": "#DDEBF6",
        "grid": "#0E7490", "grid_op": "0.10",
        "text": "#1E293B", "head": "#0F172A",
        "dim": "#475569", "faint": "#64748B",
        "cyan": "#0E7490", "cyan_l": "#0891B2",
        "blue": "#1D4ED8", "green": "#047857", "amber": "#B45309",
        "panel": "#FFFFFF", "panel_op": "0.82",
        "stroke": "#CBD5E1",
        "orb_op": "0.26", "scan_op": "0.16",
        "shine": "#FFFFFF", "shine_op": "0.60",
        "clasp": "#94A3B8", "clasp_edge": "#64748B", "strap_text": "#F8FEFF",
    },
}

ROLES = [
    "Cybersecurity Engineer  ·  secure by construction",
    "AI Agent Security  ·  guardrails, audit trails, human approval",
    "Automotive &amp; Embedded  ·  CAN / UDS / secure boot",
    "Full-Stack &amp; Automation  ·  ship the whole system",
]

PILLS_A = ["Threat Modeling", "AI Agent Security", "CAN / UDS", "Secure Boot", "PKI"]
PILLS_B = ["SIEM &amp; Detection", "Vulnerability Mgmt", "Python", "TypeScript", "C / C++"]

DOT_COLORS = ("cyan", "green", "blue")


def _pill_width(label: str) -> float:
    """Rough advance width for 13px semibold sans, plus horizontal padding."""
    return round(len(label.replace("&amp;", "&")) * 7.15 + 30, 1)


# --------------------------------------------------------------------------- hero

HERO_W, HERO_H = 1280, 440
EMB_CX, EMB_CY = 1058, 182
CMD = "./whoami --role engineer --scope full"
CMD_W = 268.0


def hero(t: dict) -> str:
    p = []
    add = p.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{HERO_W}" height="{HERO_H}" '
        f'viewBox="0 0 {HERO_W} {HERO_H}" role="img" '
        f'aria-label="Micheal Wolski — Cybersecurity Engineer. AI agent security, automotive and '
        f'embedded security, full-stack development.">')
    add('  <title>Micheal Wolski — Cybersecurity Engineer</title>')

    # ------------------------------------------------------------------ defs
    add('  <defs>')
    add(f'    <linearGradient id="hBg" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{t["bg0"]}"/><stop offset="52%" stop-color="{t["bg1"]}"/>'
        f'<stop offset="100%" stop-color="{t["bg2"]}"/></linearGradient>')
    add(f'    <linearGradient id="hName" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{t["cyan_l"]}"/><stop offset="48%" stop-color="{t["blue"]}"/>'
        f'<stop offset="100%" stop-color="{t["green"]}"/>'
        f'<animate attributeName="x1" values="-40%;60%;-40%" dur="9s" repeatCount="indefinite"/>'
        f'<animate attributeName="x2" values="60%;160%;60%" dur="9s" repeatCount="indefinite"/>'
        f'</linearGradient>')
    add(f'    <linearGradient id="hEdge" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{t["cyan"]}" stop-opacity="0.85"/>'
        f'<stop offset="50%" stop-color="{t["blue"]}" stop-opacity="0.45"/>'
        f'<stop offset="100%" stop-color="{t["green"]}" stop-opacity="0.8"/></linearGradient>')
    add(f'    <linearGradient id="hRule" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{t["cyan"]}"/>'
        f'<stop offset="100%" stop-color="{t["green"]}" stop-opacity="0"/></linearGradient>')
    add(f'    <linearGradient id="hScan" x1="0%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" stop-color="{t["cyan_l"]}" stop-opacity="0"/>'
        f'<stop offset="50%" stop-color="{t["cyan_l"]}" stop-opacity="{t["scan_op"]}"/>'
        f'<stop offset="100%" stop-color="{t["cyan_l"]}" stop-opacity="0"/></linearGradient>')
    add(f'    <linearGradient id="hSweep" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{t["cyan"]}" stop-opacity="0.30"/>'
        f'<stop offset="100%" stop-color="{t["cyan"]}" stop-opacity="0"/></linearGradient>')
    for gid, col in (("hOrbC", "cyan"), ("hOrbG", "green"), ("hOrbB", "blue")):
        add(f'    <radialGradient id="{gid}" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0%" stop-color="{t[col]}" stop-opacity="{t["orb_op"]}"/>'
            f'<stop offset="100%" stop-color="{t[col]}" stop-opacity="0"/></radialGradient>')
    add(f'    <pattern id="hGrid" width="40" height="40" patternUnits="userSpaceOnUse">'
        f'<path d="M40 0H0v40" fill="none" stroke="{t["grid"]}" stroke-opacity="{t["grid_op"]}" '
        f'stroke-width="1"/></pattern>')
    add('    <filter id="hGlow" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="3.4" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    add('    <filter id="hBlur" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="26"/></filter>')
    add(f'    <clipPath id="hCard"><rect width="{HERO_W}" height="{HERO_H}" rx="24"/></clipPath>')
    add('    <clipPath id="hWaveClip"><rect x="0" y="0" width="216" height="30"/></clipPath>')
    add('  </defs>')

    # ----------------------------------------------------------------- style
    # Reveal animations use fill-mode `backwards`: the from-state applies only
    # during the delay, so with animations disabled every element sits at its
    # natural, visible value.
    add('  <style>')
    add('    .fade{animation:fadeIn .7s ease-out backwards}')
    add('    .type{animation:type 1.45s steps(24,end) .35s backwards}')
    add('    .wipe{animation:wipe .95s cubic-bezier(.16,.9,.24,1) 2.05s backwards}')
    add('    .grow{transform-box:fill-box;transform-origin:left center;'
        'animation:grow .8s cubic-bezier(.16,.9,.24,1) 2.75s backwards}')
    add('    .drift-a{animation:driftA 13s ease-in-out infinite}')
    add('    .drift-b{animation:driftB 17s ease-in-out infinite}')
    add('    .drift-c{animation:driftC 11s ease-in-out infinite}')
    add('    .grid-pan{animation:gridPan 22s linear infinite}')
    add('    .scan{animation:scan 7.5s cubic-bezier(.5,0,.5,1) infinite}')
    add('    .spark{animation:spark 6s ease-in-out infinite}')
    add('    .role{animation:role 17.6s linear infinite}')
    add(f'    .ring-cw{{transform-box:view-box;transform-origin:{EMB_CX}px {EMB_CY}px;'
        f'animation:spin 26s linear infinite}}')
    add(f'    .ring-ccw{{transform-box:view-box;transform-origin:{EMB_CX}px {EMB_CY}px;'
        f'animation:spinBack 34s linear infinite}}')
    add(f'    .radar{{transform-box:view-box;transform-origin:{EMB_CX}px {EMB_CY}px;'
        f'animation:spin 4.6s linear infinite}}')
    add('    .beat{animation:beat 2.6s ease-in-out infinite}')
    add('    .caret{animation:blink 1.06s steps(1,end) 1.8s infinite}')
    add('    .wave{animation:wave 5.5s linear infinite}')
    add('    .live{animation:live 2.2s ease-in-out infinite}')
    add('    @keyframes fadeIn{from{opacity:0}}')
    add('    @keyframes type{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}')
    add('    @keyframes wipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}')
    add('    @keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}')
    add('    @keyframes driftA{0%,100%{transform:translate(0,0)}50%{transform:translate(26px,-20px)}}')
    add('    @keyframes driftB{0%,100%{transform:translate(0,0)}50%{transform:translate(-30px,18px)}}')
    add('    @keyframes driftC{0%,100%{transform:translate(0,0)}50%{transform:translate(16px,24px)}}')
    add('    @keyframes gridPan{to{transform:translate(-40px,-40px)}}')
    add(f'    @keyframes scan{{0%{{transform:translateY(-90px);opacity:1}}'
        f'100%{{transform:translateY({HERO_H + 90}px);opacity:1}}}}')
    add('    @keyframes spark{0%{opacity:0;transform:translateY(0)}18%{opacity:.85}'
        '100%{opacity:0;transform:translateY(-96px)}}')
    add('    @keyframes role{0%,1%{opacity:0}3%,22%{opacity:1}25%,100%{opacity:0}}')
    add('    @keyframes spin{to{transform:rotate(360deg)}}')
    add('    @keyframes spinBack{to{transform:rotate(-360deg)}}')
    add('    @keyframes beat{0%,100%{opacity:.35}50%{opacity:.9}}')
    add('    @keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}')
    add('    @keyframes wave{to{transform:translateX(-216px)}}')
    add('    @keyframes live{0%,100%{opacity:.35}50%{opacity:1}}')
    add('    @media (prefers-reduced-motion: reduce){')
    add('      .fade,.type,.wipe,.grow,.drift-a,.drift-b,.drift-c,.grid-pan,.scan,.spark,'
        '.ring-cw,.ring-ccw,.radar,.beat,.caret,.wave,.live,.role{animation:none}')
    add('    }')
    add('  </style>')

    # ------------------------------------------------------------------ body
    add('  <g clip-path="url(#hCard)">')
    add(f'    <rect width="{HERO_W}" height="{HERO_H}" fill="url(#hBg)"/>')
    add(f'    <g class="grid-pan"><rect x="-40" y="-40" width="{HERO_W + 80}" height="{HERO_H + 80}" '
        f'fill="url(#hGrid)"/></g>')

    add('    <g filter="url(#hBlur)">')
    add('      <circle class="drift-a" cx="150" cy="120" r="150" fill="url(#hOrbC)"/>')
    add(f'      <circle class="drift-b" cx="{EMB_CX}" cy="{EMB_CY + 40}" r="180" fill="url(#hOrbB)"/>')
    add('      <circle class="drift-c" cx="560" cy="420" r="150" fill="url(#hOrbG)"/>')
    add('    </g>')

    # rising sparks — hidden at rest, the keyframes drive them
    sparks = [(120, 400, 2.2, "cyan", 0.0), (300, 430, 1.7, "green", 1.4), (470, 410, 2.0, "cyan", 2.6),
              (700, 435, 1.6, "blue", 0.8), (880, 415, 2.1, "green", 3.4), (1210, 400, 1.9, "cyan", 2.0),
              (960, 440, 1.5, "blue", 4.2)]
    add('    <g>')
    for x, y, r, col, delay in sparks:
        add(f'      <circle class="spark" cx="{x}" cy="{y}" r="{r}" fill="{t[col]}" opacity="0" '
            f'style="animation-delay:{delay}s"/>')
    add('    </g>')

    add(f'    <rect class="scan" x="0" y="0" width="{HERO_W}" height="88" fill="url(#hScan)" opacity="0"/>')

    # -------------------------------------------------------------- emblem
    add('    <g>')
    add(f'      <circle class="ring-cw" cx="{EMB_CX}" cy="{EMB_CY}" r="116" fill="none" '
        f'stroke="{t["cyan"]}" stroke-opacity="0.30" stroke-width="1" stroke-dasharray="3 11"/>')
    add(f'      <circle class="ring-ccw" cx="{EMB_CX}" cy="{EMB_CY}" r="96" fill="none" '
        f'stroke="{t["blue"]}" stroke-opacity="0.34" stroke-width="1" stroke-dasharray="26 14"/>')
    add(f'      <circle cx="{EMB_CX}" cy="{EMB_CY}" r="74" fill="none" stroke="{t["green"]}" '
        f'stroke-opacity="0.26" stroke-width="1"/>')
    add(f'      <path class="radar" d="M{EMB_CX} {EMB_CY} L{EMB_CX + 116} {EMB_CY - 42} '
        f'A116 116 0 0 1 {EMB_CX + 116} {EMB_CY + 42} Z" fill="url(#hSweep)"/>')
    add('      <g class="ring-cw">')
    for dx, dy, col in ((116, 0, "cyan"), (-58, 100, "green"), (-58, -100, "blue")):
        add(f'        <circle cx="{EMB_CX + dx}" cy="{EMB_CY + dy}" r="4" fill="{t[col]}"/>')
    add('      </g>')
    add('      <g class="ring-ccw">')
    for dx, dy, col in ((0, -96, "cyan"), (83, 48, "green")):
        add(f'        <circle cx="{EMB_CX + dx}" cy="{EMB_CY + dy}" r="3.2" fill="{t[col]}" opacity="0.9"/>')
    add('      </g>')
    hx = (f"M{EMB_CX} {EMB_CY - 58} L{EMB_CX + 50} {EMB_CY - 29} L{EMB_CX + 50} {EMB_CY + 29} "
          f"L{EMB_CX} {EMB_CY + 58} L{EMB_CX - 50} {EMB_CY + 29} L{EMB_CX - 50} {EMB_CY - 29} Z")
    add(f'      <path d="{hx}" fill="{t["panel"]}" fill-opacity="{t["panel_op"]}" '
        f'stroke="url(#hEdge)" stroke-width="1.8"/>')
    add(f'      <path class="beat" d="{hx}" fill="none" stroke="{t["cyan"]}" stroke-width="6" '
        f'stroke-opacity="0.16"/>')
    add(f'      <path d="M{EMB_CX - 14} {EMB_CY - 6} v-9 a14 14 0 0 1 28 0 v9" fill="none" '
        f'stroke="{t["cyan_l"]}" stroke-width="2.4" stroke-linecap="round"/>')
    add(f'      <rect x="{EMB_CX - 22}" y="{EMB_CY - 6}" width="44" height="34" rx="7" fill="none" '
        f'stroke="{t["cyan_l"]}" stroke-width="2.4"/>')
    add(f'      <circle cx="{EMB_CX}" cy="{EMB_CY + 8}" r="3.4" fill="{t["green"]}"/>')
    add(f'      <path d="M{EMB_CX} {EMB_CY + 11} v7" stroke="{t["green"]}" stroke-width="2.4" '
        f'stroke-linecap="round"/>')
    add(f'      <text x="{EMB_CX}" y="{EMB_CY + 98}" text-anchor="middle" font-family="{MONO}" '
        f'font-size="10.5" letter-spacing="3.4" fill="{t["faint"]}">TRUST · VERIFY · SHIP</text>')
    add('    </g>')

    # ------------------------------------------------------------ terminal
    add(f'    <g transform="translate(56,52)" font-family="{MONO}">')
    add(f'      <rect x="-14" y="-24" width="360" height="34" rx="9" fill="{t["panel"]}" '
        f'fill-opacity="{t["panel_op"]}" stroke="{t["stroke"]}" stroke-width="1"/>')
    add('      <circle cx="2" cy="-7" r="4.1" fill="#FF5F57"/>')
    add('      <circle cx="17" cy="-7" r="4.1" fill="#FEBC2E"/>')
    add('      <circle cx="32" cy="-7" r="4.1" fill="#28C840"/>')
    add(f'      <text x="52" y="-3" font-size="12.5" fill="{t["dim"]}">micheal@secops — zsh</text>')
    add(f'      <text x="0" y="34" font-size="14.5" fill="{t["green"]}">$</text>')
    add('      <g class="type">')
    add(f'        <text x="14" y="34" font-size="14.5" fill="{t["text"]}">{CMD}</text>')
    add('      </g>')
    add(f'      <rect class="caret" x="{CMD_W + 12}" y="21" width="8.5" height="17" '
        f'fill="{t["cyan"]}" opacity="0"/>')
    add('    </g>')

    # -------------------------------------------------------- name and roles
    add('    <g class="wipe" transform="translate(56,158)">')
    add(f'      <text x="0" y="0" font-family="{SANS}" font-size="60" font-weight="800" '
        f'letter-spacing="-0.5" fill="url(#hName)" filter="url(#hGlow)">MICHEAL WOLSKI</text>')
    add('    </g>')
    add('    <rect class="grow" x="56" y="176" width="300" height="4" rx="2" fill="url(#hRule)"/>')

    add(f'    <g transform="translate(58,212)" font-family="{MONO}" font-size="16.5" fill="{t["dim"]}">')
    for i, role in enumerate(ROLES):
        # role 1 is the resting state; the rest stay hidden unless the cycle runs
        add(f'      <text class="role" x="0" y="0" opacity="{1 if i == 0 else 0}" '
            f'style="animation-delay:{round(3.2 + i * 4.4, 2)}s">'
            f'<tspan fill="{t["cyan"]}">&gt;</tspan> {role}</text>')
    add('    </g>')

    # ------------------------------------------------------------- tagline
    add('    <g class="fade" style="animation-delay:3.0s">')
    add(f'      <rect x="56" y="234" width="600" height="42" rx="11" fill="{t["panel"]}" '
        f'fill-opacity="{t["panel_op"]}" stroke="{t["cyan"]}" stroke-opacity="0.28" stroke-width="1"/>')
    add(f'      <text x="76" y="261" font-family="{SANS}" font-size="15" fill="{t["text"]}">'
        f'Security that survives contact with production — not just the threat model.</text>')
    add('    </g>')

    # --------------------------------------------------------------- pills
    for row, (pills, y) in enumerate(((PILLS_A, 296), (PILLS_B, 334))):
        x = 56.0
        for i, label in enumerate(pills):
            w = _pill_width(label)
            delay = round(3.35 + row * 0.22 + i * 0.09, 2)
            add(f'    <g class="fade" style="animation-delay:{delay}s">')
            add(f'      <rect x="{x}" y="{y}" width="{w}" height="30" rx="15" fill="{t["panel"]}" '
                f'fill-opacity="{t["panel_op"]}" stroke="{t["stroke"]}" stroke-width="1"/>')
            add(f'      <circle cx="{x + 15}" cy="{y + 15}" r="3" fill="{t[DOT_COLORS[i % 3]]}"/>')
            add(f'      <text x="{x + 26}" y="{y + 20}" font-family="{SANS}" font-size="13" '
                f'font-weight="600" fill="{t["text"]}">{label}</text>')
            add('    </g>')
            x += w + 10

    # ------------------------------------------------------------- HUD bar
    add('    <g class="fade" style="animation-delay:3.7s">')
    add(f'      <rect x="40" y="382" width="1200" height="44" rx="13" fill="{t["panel"]}" '
        f'fill-opacity="{t["panel_op"]}" stroke="{t["stroke"]}" stroke-width="1"/>')
    add(f'      <circle class="live" cx="66" cy="404" r="4.2" fill="{t["green"]}"/>')
    add(f'      <text x="80" y="409" font-family="{MONO}" font-size="12" letter-spacing="1.6" '
        f'fill="{t["green"]}">OPEN TO WORK</text>')
    add(f'      <line x1="204" y1="393" x2="204" y2="415" stroke="{t["stroke"]}" stroke-width="1"/>')
    add(f'      <text x="222" y="409" font-family="{MONO}" font-size="12" fill="{t["dim"]}">Michigan, USA</text>')
    add(f'      <line x1="342" y1="393" x2="342" y2="415" stroke="{t["stroke"]}" stroke-width="1"/>')
    add(f'      <text x="360" y="409" font-family="{MONO}" font-size="12" fill="{t["dim"]}">'
        f'B.S. Information Assurance &amp; Cyber Defense — EMU, Cum Laude</text>')
    add('      <g transform="translate(1004,393)">')
    add('        <g clip-path="url(#hWaveClip)">')
    seg = ("M0 22 h12 V8 h16 V22 h10 V8 h8 V22 h20 V8 h12 V22 h14 V8 h18 V22 h10 V8 h14 V22 "
           "h16 V8 h10 V22 h16 V8 h12 V22 h8")
    add('          <g class="wave">')
    add(f'            <path d="{seg}" fill="none" stroke="{t["cyan"]}" stroke-opacity="0.85" stroke-width="1.6"/>')
    add(f'            <g transform="translate(216,0)"><path d="{seg}" fill="none" stroke="{t["cyan"]}" '
        f'stroke-opacity="0.85" stroke-width="1.6"/></g>')
    add('          </g>')
    add('        </g>')
    add(f'        <text x="216" y="2" text-anchor="end" font-family="{MONO}" font-size="9" '
        f'letter-spacing="2" fill="{t["faint"]}">CAN 500 kbps</text>')
    add('      </g>')
    add('    </g>')

    add('  </g>')
    add(f'  <rect x="1" y="1" width="{HERO_W - 2}" height="{HERO_H - 2}" rx="23" fill="none" '
        f'stroke="url(#hEdge)" stroke-width="1.6"/>')
    add('</svg>')
    return "\n".join(p) + "\n"


# --------------------------------------------------------------- credential badge

CRED_W, CRED_H = 400, 580
ANCHOR_X, ANCHOR_Y = 200, 16
CARD_Y = 160
CARD_W, CARD_H = 236, 366
HALF = CARD_W // 2

# Two-up fields stay inside a 96px column; the wide one gets its own row so the
# longer value can never collide with the column beside it.
CRED_FIELDS = [
    ("ID", "MW-0xC5"),
    ("CLEARANCE", "ENGINEER"),
    ("STATUS", "ACTIVE"),
    ("REGION", "MI · USA"),
]
CRED_WIDE = ("FOCUS", "AI AGENTS · AUTOMOTIVE · APPSEC")

BARCODE = [2, 1, 3, 1, 2, 4, 1, 2, 1, 3, 2, 1, 4, 1, 2, 3, 1, 2, 1, 3, 2, 4, 1, 2, 1, 3, 1, 2]


def credential(t: dict) -> str:
    p = []
    add = p.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CRED_W}" height="{CRED_H}" '
        f'viewBox="0 0 {CRED_W} {CRED_H}" role="img" '
        f'aria-label="Security credential badge for Micheal Wolski, Cybersecurity Engineer">')
    add('  <title>Micheal Wolski — security credential</title>')

    add('  <defs>')
    add(f'    <linearGradient id="cStrap" x1="0%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" stop-color="{t["cyan"]}"/><stop offset="100%" stop-color="{t["green"]}"/></linearGradient>')
    add(f'    <linearGradient id="cCard" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{t["bg1"]}"/><stop offset="100%" stop-color="{t["bg2"]}"/></linearGradient>')
    add(f'    <linearGradient id="cEdge" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{t["cyan"]}"/><stop offset="55%" stop-color="{t["blue"]}"/>'
        f'<stop offset="100%" stop-color="{t["green"]}"/></linearGradient>')
    add(f'    <linearGradient id="cHolo" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{t["shine"]}" stop-opacity="0"/>'
        f'<stop offset="42%" stop-color="{t["shine"]}" stop-opacity="{t["shine_op"]}"/>'
        f'<stop offset="58%" stop-color="{t["cyan_l"]}" stop-opacity="{t["shine_op"]}"/>'
        f'<stop offset="100%" stop-color="{t["shine"]}" stop-opacity="0"/></linearGradient>')
    add(f'    <radialGradient id="cHalo" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="{t["cyan"]}" stop-opacity="0.34"/>'
        f'<stop offset="100%" stop-color="{t["cyan"]}" stop-opacity="0"/></radialGradient>')
    add(f'    <pattern id="cWeave" width="8" height="8" patternUnits="userSpaceOnUse">'
        f'<path d="M0 8 L8 0" stroke="{t["bg0"]}" stroke-opacity="0.30" stroke-width="2"/></pattern>')
    add(f'    <clipPath id="cCardClip"><rect x="{-HALF}" y="0" width="{CARD_W}" height="{CARD_H}" rx="20"/></clipPath>')
    add('  </defs>')

    # Swing amplitude is capped so the card never leaves the viewBox: the card
    # corner sits ~500px from the pivot, so 5deg moves it ~44px — well inside
    # the 200px half-width once the 118px card half-width is accounted for.
    # Every keyframe below repeats the translate that the transform attribute
    # supplies at rest: a CSS transform animation REPLACES that attribute rather
    # than composing with it, so omitting it would fling the badge to the origin.
    piv = f"translate({ANCHOR_X}px,{ANCHOR_Y}px)"
    add('  <style>')
    add('    .swing{animation:settle 5s cubic-bezier(.33,0,.2,1) both, '
        'sway 7s ease-in-out 5s infinite}')
    add('    .holo{animation:holo 6.5s ease-in-out infinite}')
    add('    .led{animation:led 2s ease-in-out infinite}')
    add('    .scanbar{animation:scanbar 3.4s ease-in-out infinite}')
    add('    .chipflow{stroke-dasharray:5 7;animation:chipflow 2.4s linear infinite}')
    add('    .rise{animation:rise .6s ease-out backwards}')
    add(f'    @keyframes settle{{0%{{transform:{piv} rotate(5deg)}}'
        f'30%{{transform:{piv} rotate(-3.4deg)}}55%{{transform:{piv} rotate(2deg)}}'
        f'75%{{transform:{piv} rotate(-1.1deg)}}90%{{transform:{piv} rotate(.4deg)}}'
        f'100%{{transform:{piv} rotate(0)}}}}')
    add(f'    @keyframes sway{{0%,100%{{transform:{piv} rotate(-2.2deg)}}'
        f'50%{{transform:{piv} rotate(2.2deg)}}}}')
    add('    @keyframes holo{0%{transform:translate(-300px,-300px);opacity:1}'
        '55%,100%{transform:translate(300px,300px);opacity:1}}')
    add('    @keyframes led{0%,100%{opacity:.3}50%{opacity:1}}')
    add('    @keyframes scanbar{0%,100%{transform:translateX(0);opacity:0}10%{opacity:.9}'
        '50%{transform:translateX(146px);opacity:.9}60%{opacity:0}}')
    add('    @keyframes chipflow{to{stroke-dashoffset:-24}}')
    add('    @keyframes rise{from{opacity:0;transform:translateY(9px)}}')
    add('    @media (prefers-reduced-motion: reduce){')
    add('      .swing,.holo,.led,.scanbar,.chipflow,.rise{animation:none}')
    add('    }')
    add('  </style>')

    add(f'  <g class="swing" transform="translate({ANCHOR_X},{ANCHOR_Y})">')
    add('    <circle cx="0" cy="0" r="7.5" fill="none" stroke="url(#cEdge)" stroke-width="2.4"/>')

    strap = f"M-10 5 C-10 56 -15 92 -7 {CARD_Y - 28} L7 {CARD_Y - 28} C15 92 10 56 10 5 Z"
    add(f'    <path d="{strap}" fill="url(#cStrap)"/>')
    add(f'    <path d="{strap}" fill="url(#cWeave)"/>')
    # rotate(a cx cy) rather than the transform-origin property: the attribute form
    # is understood by every SVG renderer, the CSS property is not.
    for sy in (48, 104):
        add(f'    <text x="0" y="{sy}" text-anchor="middle" font-family="{MONO}" font-size="7.5" '
            f'letter-spacing="1.1" fill="{t["strap_text"]}" opacity="0.92" '
            f'transform="rotate(90 0 {sy})">AUTHORIZED</text>')

    add(f'    <g transform="translate(0,{CARD_Y - 28})">')
    add(f'      <rect x="-14" y="0" width="28" height="16" rx="4" fill="{t["clasp"]}" '
        f'stroke="{t["clasp_edge"]}" stroke-width="1"/>')
    add(f'      <circle cx="0" cy="19" r="7.5" fill="none" stroke="{t["clasp_edge"]}" stroke-width="3"/>')
    add('    </g>')

    add(f'    <g transform="translate(0,{CARD_Y})">')
    add(f'      <rect x="{-HALF}" y="0" width="{CARD_W}" height="{CARD_H}" rx="20" fill="url(#cCard)" '
        f'stroke="url(#cEdge)" stroke-width="2"/>')
    add('      <g clip-path="url(#cCardClip)">')

    add(f'        <rect x="{-HALF}" y="0" width="{CARD_W}" height="36" fill="{t["cyan"]}" opacity="0.16"/>')
    add(f'        <text x="0" y="23" text-anchor="middle" font-family="{MONO}" font-size="10" '
        f'letter-spacing="2.6" fill="{t["cyan_l"]}">SECURITY CREDENTIAL</text>')
    add(f'        <line x1="{-HALF}" y1="36" x2="{HALF}" y2="36" stroke="{t["cyan"]}" '
        f'stroke-opacity="0.35" stroke-width="1"/>')

    add('        <circle cx="0" cy="96" r="46" fill="url(#cHalo)"/>')
    add('        <g transform="translate(0,96)">')
    add('        <g class="rise" style="animation-delay:.35s">')
    add(f'          <path d="M0 -36 L31 -18 L31 18 L0 36 L-31 18 L-31 -18 Z" fill="{t["bg0"]}" '
        f'fill-opacity="0.45" stroke="url(#cEdge)" stroke-width="1.8"/>')
    add(f'          <text x="0" y="9" text-anchor="middle" font-family="{SANS}" font-size="24" '
        f'font-weight="800" fill="url(#cEdge)">MW</text>')
    add('        </g>')
    add('        </g>')

    add('        <g class="rise" style="animation-delay:.5s">')
    add(f'          <text x="0" y="170" text-anchor="middle" font-family="{SANS}" font-size="17" '
        f'font-weight="800" letter-spacing="0.4" fill="{t["head"]}">MICHEAL WOLSKI</text>')
    add(f'          <text x="0" y="189" text-anchor="middle" font-family="{MONO}" font-size="9.5" '
        f'letter-spacing="2.2" fill="{t["cyan"]}">CYBERSECURITY ENGINEER</text>')
    add('        </g>')
    add(f'        <line x1="-86" y1="203" x2="86" y2="203" stroke="{t["stroke"]}" stroke-width="1"/>')

    for i, (k, v) in enumerate(CRED_FIELDS):
        fx = -96 + (i % 2) * 96
        fy = 223 + (i // 2) * 31
        add(f'        <g class="rise" style="animation-delay:{round(0.6 + i * 0.07, 2)}s">')
        add(f'          <text x="{fx}" y="{fy}" font-family="{MONO}" font-size="7.5" '
            f'letter-spacing="1.5" fill="{t["faint"]}">{k}</text>')
        add(f'          <text x="{fx}" y="{fy + 13}" font-family="{MONO}" font-size="9.5" '
            f'font-weight="600" fill="{t["text"]}">{v}</text>')
        add('        </g>')

    wk, wv = CRED_WIDE
    add('        <g class="rise" style="animation-delay:0.88s">')
    add(f'          <text x="-96" y="285" font-family="{MONO}" font-size="7.5" letter-spacing="1.5" '
        f'fill="{t["faint"]}">{wk}</text>')
    add(f'          <text x="-96" y="298" font-family="{MONO}" font-size="8.6" font-weight="600" '
        f'fill="{t["text"]}">{wv}</text>')
    add('        </g>')

    add('        <g transform="translate(-98,318)">')
    add(f'          <rect x="0" y="0" width="34" height="26" rx="5" fill="{t["amber"]}" '
        f'fill-opacity="0.20" stroke="{t["amber"]}" stroke-opacity="0.75" stroke-width="1"/>')
    add(f'          <g class="chipflow" stroke="{t["amber"]}" stroke-opacity="0.9" stroke-width="1" fill="none">')
    add('            <path d="M0 9h11M23 9h11M0 17h11M23 17h11M11 0v26M23 0v26"/>')
    add('          </g>')
    add('        </g>')

    add('        <g transform="translate(-52,318)">')
    bx = 0
    for w in BARCODE:
        add(f'          <rect x="{bx}" y="0" width="{w}" height="20" fill="{t["text"]}" opacity="0.82"/>')
        bx += w + 2
    add(f'          <text x="0" y="30" font-family="{MONO}" font-size="7" letter-spacing="1.4" '
        f'fill="{t["faint"]}">MW · EMU · MI · USA</text>')
    add(f'          <rect class="scanbar" x="0" y="-3" width="2.4" height="26" fill="{t["cyan_l"]}" opacity="0"/>')
    add('        </g>')

    add(f'        <circle class="led" cx="{HALF - 22}" cy="18" r="4" fill="{t["green"]}"/>')
    add(f'        <rect class="holo" x="{-HALF - 40}" y="-40" width="{CARD_W + 80}" '
        f'height="{CARD_H + 80}" fill="url(#cHolo)" opacity="0"/>')

    add('      </g>')
    add('    </g>')
    add('  </g>')
    add('</svg>')
    return "\n".join(p) + "\n"


# ------------------------------------------------------------------- section rule

DIV_W, DIV_H = 900, 28


def divider(t: dict) -> str:
    p = []
    add = p.append
    mid = DIV_H / 2

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{DIV_W}" height="{DIV_H}" '
        f'viewBox="0 0 {DIV_W} {DIV_H}" role="presentation" aria-hidden="true">')
    add('  <defs>')
    add(f'    <linearGradient id="dLine" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{t["cyan"]}" stop-opacity="0"/>'
        f'<stop offset="18%" stop-color="{t["cyan"]}" stop-opacity="0.8"/>'
        f'<stop offset="50%" stop-color="{t["blue"]}" stop-opacity="0.8"/>'
        f'<stop offset="82%" stop-color="{t["green"]}" stop-opacity="0.8"/>'
        f'<stop offset="100%" stop-color="{t["green"]}" stop-opacity="0"/></linearGradient>')
    add(f'    <radialGradient id="dPulse" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="{t["cyan_l"]}" stop-opacity="0.95"/>'
        f'<stop offset="100%" stop-color="{t["cyan_l"]}" stop-opacity="0"/></radialGradient>')
    add('  </defs>')
    add('  <style>')
    add('    .pulse{animation:travel 6s cubic-bezier(.55,0,.45,1) infinite}')
    add('    .tick{animation:twinkle 3.4s ease-in-out infinite}')
    add(f'    @keyframes travel{{0%{{transform:translateX(40px);opacity:1}}'
        f'100%{{transform:translateX({DIV_W - 40}px);opacity:1}}}}')
    add('    @keyframes twinkle{0%,100%{opacity:.25}50%{opacity:.8}}')
    add('    @media (prefers-reduced-motion: reduce){.pulse,.tick{animation:none}}')
    add('  </style>')
    add(f'  <line x1="0" y1="{mid}" x2="{DIV_W}" y2="{mid}" stroke="url(#dLine)" stroke-width="1.4"/>')
    for i in range(9):
        add(f'  <rect class="tick" x="{90 + i * 90}" y="{mid - 4}" width="1.4" height="8" '
            f'fill="{t["cyan"]}" opacity="0.28" style="animation-delay:{round(i * 0.28, 2)}s"/>')
    add(f'  <g class="pulse" opacity="0"><circle cx="0" cy="{mid}" r="11" fill="url(#dPulse)"/>'
        f'<circle cx="0" cy="{mid}" r="2.6" fill="{t["cyan_l"]}"/></g>')
    add(f'  <path d="M8 {mid - 7} v14 M14 {mid - 4} v8" stroke="{t["cyan"]}" stroke-opacity="0.75" '
        f'stroke-width="1.4"/>')
    add(f'  <path d="M{DIV_W - 8} {mid - 7} v14 M{DIV_W - 14} {mid - 4} v8" stroke="{t["green"]}" '
        f'stroke-opacity="0.75" stroke-width="1.4"/>')
    add('</svg>')
    return "\n".join(p) + "\n"


ASSETS = {"hero": hero, "credential": credential, "divider": divider}


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "assets")
    out.mkdir(parents=True, exist_ok=True)
    for theme in THEMES.values():
        for stem, fn in ASSETS.items():
            path = out / (stem + theme["suffix"] + ".svg")
            path.write_text(fn(theme), encoding="utf-8")
            print("wrote", path)


if __name__ == "__main__":
    main()
