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
    "Cybersecurity Engineer  ·  Automotive &amp; Product Security",
    "Automotive &amp; Embedded  ·  CAN / UDS / secure boot",
    "AI Agent Security  ·  guardrails, audit trails, human approval",
    "Full-Stack &amp; Automation  ·  ship the whole system",
]

PILLS_A = ["Threat Modeling", "CAN / UDS", "AI Agent Security", "Secure Boot", "PKI"]
PILLS_B = ["SIEM &amp; Detection", "Vulnerability Mgmt", "Python", "TypeScript", "C / C++"]

DOT_COLORS = ("cyan", "green", "blue")


def _pill_width(label: str) -> float:
    """Rough advance width for 13px semibold sans, plus horizontal padding."""
    return round(len(label.replace("&amp;", "&")) * 7.15 + 30, 1)


# --------------------------------------------------------------------------- hero

HERO_W, HERO_H = 1280, 440
EMB_CX, EMB_CY = 1058, 182
CMD = "./whoami --role engineer --scope full"
MONO_ADVANCE = 0.6  # every face in the MONO stack is 0.6em per glyph
CMD_X, CMD_SIZE = 14, 14.5
CARET_GAP = 5
CMD_W = len(CMD) * CMD_SIZE * MONO_ADVANCE


def hero(t: dict) -> str:
    p = []
    add = p.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{HERO_W}" height="{HERO_H}" '
        f'viewBox="0 0 {HERO_W} {HERO_H}" role="img" '
        f'aria-label="Micheal Wolski — Cybersecurity Engineer. Automotive and product security, '
        f'AI agent security, detection engineering, full-stack development.">')
    add('  <title>Micheal Wolski — Cybersecurity &amp; Automotive Product Security</title>')

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
    add(f'        <text x="{CMD_X}" y="34" font-size="{CMD_SIZE}" fill="{t["text"]}">{CMD}</text>')
    add('      </g>')
    add(f'      <rect class="caret" x="{CMD_X + CMD_W + CARET_GAP:.1f}" y="21" width="8.5" height="17" '
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

CRED_W, CRED_H = 460, 580
ANCHOR_X, ANCHOR_Y = 230, 16
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
CRED_WIDE = ("FOCUS", "AUTOMOTIVE · EMBEDDED · AI AGENTS")

BARCODE = [2, 1, 3, 1, 2, 4, 1, 2, 1, 3, 2, 1, 4, 1, 2, 3, 1, 2, 1, 3, 2, 4, 1, 2, 1, 3, 1, 2]


def credential(t: dict) -> str:
    p = []
    add = p.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CRED_W}" height="{CRED_H}" '
        f'viewBox="0 0 {CRED_W} {CRED_H}" role="img" '
        f'aria-label="Security credential badge for Micheal Wolski, cybersecurity and automotive product security">')
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
    pivx = f"translate({ANCHOR_X}px,"
    add('  <style>')
    add('    .swing{animation:settle 4.2s cubic-bezier(.33,0,.2,1) both, '
        'sway 6s ease-in-out 4.2s infinite}')
    add('    .holo{animation:holo 6.5s ease-in-out infinite}')
    add('    .breathe{animation:breathe 4.5s ease-in-out infinite}')
    add('    .led{animation:led 2s ease-in-out infinite}')
    add('    .scanbar{animation:scanbar 3.4s ease-in-out infinite}')
    add('    .chipflow{stroke-dasharray:5 7;animation:chipflow 2.4s linear infinite}')
    add('    .rise{animation:rise .6s ease-out backwards}')
    add(f'    @keyframes settle{{0%{{transform:{piv} rotate(11deg)}}'
        f'28%{{transform:{piv} rotate(-7.5deg)}}52%{{transform:{piv} rotate(4.6deg)}}'
        f'72%{{transform:{piv} rotate(-2.6deg)}}88%{{transform:{piv} rotate(1.2deg)}}'
        f'100%{{transform:{piv} rotate(-5deg)}}}}')
    # A pendulum hangs lowest as it crosses centre, so the bob rides 4px down at
    # 25%/75% rather than at the extremes.
    add(f'    @keyframes sway{{0%,100%{{transform:{pivx}16px) rotate(-5deg)}}'
        f'25%{{transform:{pivx}20px) rotate(0deg)}}'
        f'50%{{transform:{pivx}16px) rotate(5deg)}}'
        f'75%{{transform:{pivx}20px) rotate(0deg)}}}}')
    add('    @keyframes holo{0%{transform:translate(-300px,-300px);opacity:1}'
        '55%,100%{transform:translate(300px,300px);opacity:1}}')
    add('    @keyframes led{0%,100%{opacity:.3}50%{opacity:1}}')
    add('    @keyframes breathe{0%,100%{opacity:.18}50%{opacity:.5}}')
    add('    @keyframes scanbar{0%,100%{transform:translateX(0);opacity:0}10%{opacity:.9}'
        '50%{transform:translateX(146px);opacity:.9}60%{opacity:0}}')
    add('    @keyframes chipflow{to{stroke-dashoffset:-24}}')
    add('    @keyframes rise{from{opacity:0;transform:translateY(9px)}}')
    add('    @media (prefers-reduced-motion: reduce){')
    add('      .swing,.holo,.led,.scanbar,.chipflow,.rise,.breathe{animation:none}')
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
    add(f'      <rect class="breathe" x="{-HALF - 5}" y="-5" width="{CARD_W + 10}" '
        f'height="{CARD_H + 10}" rx="24" fill="none" stroke="url(#cEdge)" stroke-width="6" '
        f'opacity="0.18"/>')
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
    add(f'          <text x="0" y="189" text-anchor="middle" font-family="{MONO}" font-size="8.5" '
        f'letter-spacing="1.6" fill="{t["cyan"]}">CYBERSECURITY · AUTOMOTIVE</text>')
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



# ------------------------------------------------------------------- compact hero

# The wide hero is 1280 across; on a ~375px phone that is a 0.27x downscale, which
# leaves every element except the name at 3-4px. This variant carries the same
# design language in a stacked layout sized so the body text stays legible there.

CO_W, CO_H = 720, 620
CO_CX = 360
CO_EY = 178
CO_CMD = "./whoami --scope full"
CO_CMD_X, CO_CMD_SIZE = 142, 19

CO_ROLES = [
    "Cybersecurity · Automotive",
    "AI Agent Security",
    "Automotive &amp; Embedded",
    "Detection &amp; Response",
]
CO_PILLS = [["AI Security", "Threat Modeling", "CAN / UDS"],
            ["Secure Boot", "SIEM", "Python"]]


def _co_pill_width(label: str) -> float:
    return round(len(label) * 10.4 + 40, 1)


def hero_compact(t: dict) -> str:
    p = []
    add = p.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{CO_W}" height="{CO_H}" '
        f'viewBox="0 0 {CO_W} {CO_H}" role="img" '
        f'aria-label="Micheal Wolski — Cybersecurity Engineer. Automotive and product security, '
        f'AI agent security, detection engineering, full-stack development.">')
    add('  <title>Micheal Wolski — Cybersecurity &amp; Automotive Product Security</title>')

    add('  <defs>')
    add(f'    <linearGradient id="oBg" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{t["bg0"]}"/><stop offset="52%" stop-color="{t["bg1"]}"/>'
        f'<stop offset="100%" stop-color="{t["bg2"]}"/></linearGradient>')
    add(f'    <linearGradient id="oName" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{t["cyan_l"]}"/><stop offset="48%" stop-color="{t["blue"]}"/>'
        f'<stop offset="100%" stop-color="{t["green"]}"/>'
        f'<animate attributeName="x1" values="-40%;60%;-40%" dur="9s" repeatCount="indefinite"/>'
        f'<animate attributeName="x2" values="60%;160%;60%" dur="9s" repeatCount="indefinite"/>'
        f'</linearGradient>')
    add(f'    <linearGradient id="oEdge" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{t["cyan"]}" stop-opacity="0.85"/>'
        f'<stop offset="50%" stop-color="{t["blue"]}" stop-opacity="0.45"/>'
        f'<stop offset="100%" stop-color="{t["green"]}" stop-opacity="0.8"/></linearGradient>')
    add(f'    <linearGradient id="oRule" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{t["cyan"]}" stop-opacity="0"/>'
        f'<stop offset="50%" stop-color="{t["cyan"]}"/>'
        f'<stop offset="100%" stop-color="{t["green"]}" stop-opacity="0"/></linearGradient>')
    add(f'    <linearGradient id="oSweep" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{t["cyan"]}" stop-opacity="0.30"/>'
        f'<stop offset="100%" stop-color="{t["cyan"]}" stop-opacity="0"/></linearGradient>')
    for gid, col in (("oOrbC", "cyan"), ("oOrbG", "green")):
        add(f'    <radialGradient id="{gid}" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0%" stop-color="{t[col]}" stop-opacity="{t["orb_op"]}"/>'
            f'<stop offset="100%" stop-color="{t[col]}" stop-opacity="0"/></radialGradient>')
    add(f'    <pattern id="oGrid" width="40" height="40" patternUnits="userSpaceOnUse">'
        f'<path d="M40 0H0v40" fill="none" stroke="{t["grid"]}" stroke-opacity="{t["grid_op"]}" '
        f'stroke-width="1"/></pattern>')
    add('    <filter id="oGlow" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="3" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    add('    <filter id="oBlur" x="-60%" y="-60%" width="220%" height="220%">'
        '<feGaussianBlur stdDeviation="24"/></filter>')
    add(f'    <clipPath id="oCard"><rect width="{CO_W}" height="{CO_H}" rx="22"/></clipPath>')
    add('  </defs>')

    add('  <style>')
    add('    .fade{animation:fadeIn .7s ease-out backwards}')
    add('    .type{animation:type 1.3s steps(21,end) .35s backwards}')
    add('    .wipe{animation:wipe .9s cubic-bezier(.16,.9,.24,1) 1.9s backwards}')
    add('    .grow{transform-box:fill-box;transform-origin:center;'
        'animation:grow .8s cubic-bezier(.16,.9,.24,1) 2.5s backwards}')
    add('    .drift-a{animation:driftA 13s ease-in-out infinite}')
    add('    .drift-b{animation:driftB 17s ease-in-out infinite}')
    add('    .grid-pan{animation:gridPan 22s linear infinite}')
    add('    .role{animation:role 17.6s linear infinite}')
    add(f'    .ring-cw{{transform-box:view-box;transform-origin:{CO_CX}px {CO_EY}px;'
        f'animation:spin 26s linear infinite}}')
    add(f'    .ring-ccw{{transform-box:view-box;transform-origin:{CO_CX}px {CO_EY}px;'
        f'animation:spinBack 34s linear infinite}}')
    add(f'    .radar{{transform-box:view-box;transform-origin:{CO_CX}px {CO_EY}px;'
        f'animation:spin 4.6s linear infinite}}')
    add('    .beat{animation:beat 2.6s ease-in-out infinite}')
    add('    .caret{animation:blink 1.06s steps(1,end) 1.65s infinite}')
    add('    .live{animation:live 2.2s ease-in-out infinite}')
    add('    @keyframes fadeIn{from{opacity:0}}')
    add('    @keyframes type{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}')
    add('    @keyframes wipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}')
    add('    @keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}')
    add('    @keyframes driftA{0%,100%{transform:translate(0,0)}50%{transform:translate(20px,-16px)}}')
    add('    @keyframes driftB{0%,100%{transform:translate(0,0)}50%{transform:translate(-22px,14px)}}')
    add('    @keyframes gridPan{to{transform:translate(-40px,-40px)}}')
    add('    @keyframes role{0%,1%{opacity:0}3%,22%{opacity:1}25%,100%{opacity:0}}')
    add('    @keyframes spin{to{transform:rotate(360deg)}}')
    add('    @keyframes spinBack{to{transform:rotate(-360deg)}}')
    add('    @keyframes beat{0%,100%{opacity:.35}50%{opacity:.9}}')
    add('    @keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}')
    add('    @keyframes live{0%,100%{opacity:.35}50%{opacity:1}}')
    add('    @media (prefers-reduced-motion: reduce){')
    add('      .fade,.type,.wipe,.grow,.drift-a,.drift-b,.grid-pan,.role,.ring-cw,.ring-ccw,'
        '.radar,.beat,.caret,.live{animation:none}')
    add('    }')
    add('  </style>')

    add('  <g clip-path="url(#oCard)">')
    add(f'    <rect width="{CO_W}" height="{CO_H}" fill="url(#oBg)"/>')
    add(f'    <g class="grid-pan"><rect x="-40" y="-40" width="{CO_W + 80}" height="{CO_H + 80}" '
        f'fill="url(#oGrid)"/></g>')
    add('    <g filter="url(#oBlur)">')
    add(f'      <circle class="drift-a" cx="{CO_CX}" cy="{CO_EY}" r="150" fill="url(#oOrbC)"/>')
    add(f'      <circle class="drift-b" cx="{CO_CX}" cy="560" r="150" fill="url(#oOrbG)"/>')
    add('    </g>')

    # ---- terminal strip
    add(f'    <g font-family="{MONO}">')
    add(f'      <rect x="40" y="30" width="640" height="44" rx="11" fill="{t["panel"]}" '
        f'fill-opacity="{t["panel_op"]}" stroke="{t["stroke"]}" stroke-width="1"/>')
    add('      <circle cx="64" cy="52" r="5" fill="#FF5F57"/>')
    add('      <circle cx="82" cy="52" r="5" fill="#FEBC2E"/>')
    add('      <circle cx="100" cy="52" r="5" fill="#28C840"/>')
    add(f'      <text x="124" y="59" font-size="19" fill="{t["green"]}">$</text>')
    add('      <g class="type">')
    add(f'        <text x="{CO_CMD_X}" y="59" font-size="{CO_CMD_SIZE}" fill="{t["text"]}">{CO_CMD}</text>')
    add('      </g>')
    add(f'      <rect class="caret" x="{CO_CMD_X + len(CO_CMD) * CO_CMD_SIZE * MONO_ADVANCE + CARET_GAP:.1f}" y="45" width="10" height="19" '
        f'fill="{t["cyan"]}" opacity="0"/>')
    add('    </g>')

    # ---- emblem
    add('    <g>')
    add(f'      <circle class="ring-cw" cx="{CO_CX}" cy="{CO_EY}" r="78" fill="none" '
        f'stroke="{t["cyan"]}" stroke-opacity="0.30" stroke-width="1" stroke-dasharray="3 10"/>')
    add(f'      <circle class="ring-ccw" cx="{CO_CX}" cy="{CO_EY}" r="64" fill="none" '
        f'stroke="{t["blue"]}" stroke-opacity="0.34" stroke-width="1" stroke-dasharray="20 11"/>')
    add(f'      <circle cx="{CO_CX}" cy="{CO_EY}" r="50" fill="none" stroke="{t["green"]}" '
        f'stroke-opacity="0.26" stroke-width="1"/>')
    add(f'      <path class="radar" d="M{CO_CX} {CO_EY} L{CO_CX + 78} {CO_EY - 28} '
        f'A78 78 0 0 1 {CO_CX + 78} {CO_EY + 28} Z" fill="url(#oSweep)"/>')
    add('      <g class="ring-cw">')
    for dx, dy, col in ((78, 0, "cyan"), (-39, 68, "green"), (-39, -68, "blue")):
        add(f'        <circle cx="{CO_CX + dx}" cy="{CO_EY + dy}" r="3.6" fill="{t[col]}"/>')
    add('      </g>')
    hx = (f"M{CO_CX} {CO_EY - 40} L{CO_CX + 34} {CO_EY - 20} L{CO_CX + 34} {CO_EY + 20} "
          f"L{CO_CX} {CO_EY + 40} L{CO_CX - 34} {CO_EY + 20} L{CO_CX - 34} {CO_EY - 20} Z")
    add(f'      <path d="{hx}" fill="{t["panel"]}" fill-opacity="{t["panel_op"]}" '
        f'stroke="url(#oEdge)" stroke-width="1.6"/>')
    add(f'      <path class="beat" d="{hx}" fill="none" stroke="{t["cyan"]}" stroke-width="5" '
        f'stroke-opacity="0.16"/>')
    add(f'      <path d="M{CO_CX - 10} {CO_EY - 5} v-6.5 a10 10 0 0 1 20 0 v6.5" fill="none" '
        f'stroke="{t["cyan_l"]}" stroke-width="2.2" stroke-linecap="round"/>')
    add(f'      <rect x="{CO_CX - 16}" y="{CO_EY - 5}" width="32" height="25" rx="5" fill="none" '
        f'stroke="{t["cyan_l"]}" stroke-width="2.2"/>')
    add(f'      <circle cx="{CO_CX}" cy="{CO_EY + 4}" r="2.6" fill="{t["green"]}"/>')
    add(f'      <path d="M{CO_CX} {CO_EY + 6} v5" stroke="{t["green"]}" stroke-width="2.2" '
        f'stroke-linecap="round"/>')
    add('    </g>')

    # ---- name, rule, roles
    add(f'    <g class="wipe">')
    add(f'      <text x="{CO_CX}" y="318" text-anchor="middle" font-family="{SANS}" font-size="50" '
        f'font-weight="800" letter-spacing="-0.4" fill="url(#oName)" filter="url(#oGlow)">'
        f'MICHEAL WOLSKI</text>')
    add('    </g>')
    add(f'    <rect class="grow" x="{CO_CX - 110}" y="332" width="220" height="3.5" rx="1.75" '
        f'fill="url(#oRule)"/>')
    add(f'    <g font-family="{MONO}" font-size="21" fill="{t["dim"]}">')
    for i, role in enumerate(CO_ROLES):
        add(f'      <text class="role" x="{CO_CX}" y="372" text-anchor="middle" '
            f'opacity="{1 if i == 0 else 0}" style="animation-delay:{round(3.0 + i * 4.4, 2)}s">'
            f'<tspan fill="{t["cyan"]}">&gt;</tspan> {role}</text>')
    add('    </g>')

    # ---- tagline
    add('    <g class="fade" style="animation-delay:2.8s">')
    add(f'      <rect x="70" y="394" width="580" height="46" rx="12" fill="{t["panel"]}" '
        f'fill-opacity="{t["panel_op"]}" stroke="{t["cyan"]}" stroke-opacity="0.28" stroke-width="1"/>')
    add(f'      <text x="{CO_CX}" y="423" text-anchor="middle" font-family="{SANS}" font-size="19" '
        f'fill="{t["text"]}">Security that survives contact with production.</text>')
    add('    </g>')

    # ---- pills, each row centred
    for row, labels in enumerate(CO_PILLS):
        widths = [_co_pill_width(l) for l in labels]
        total = sum(widths) + 12 * (len(labels) - 1)
        x = CO_CX - total / 2
        y = 458 + row * 44
        for i, (label, w) in enumerate(zip(labels, widths)):
            delay = round(3.05 + row * 0.2 + i * 0.09, 2)
            add(f'    <g class="fade" style="animation-delay:{delay}s">')
            add(f'      <rect x="{x:.1f}" y="{y}" width="{w}" height="36" rx="18" fill="{t["panel"]}" '
                f'fill-opacity="{t["panel_op"]}" stroke="{t["stroke"]}" stroke-width="1"/>')
            add(f'      <circle cx="{x + 19:.1f}" cy="{y + 18}" r="3.6" fill="{t[DOT_COLORS[i % 3]]}"/>')
            add(f'      <text x="{x + 32:.1f}" y="{y + 24}" font-family="{SANS}" font-size="19" '
                f'font-weight="600" fill="{t["text"]}">{label}</text>')
            add('    </g>')
            x += w + 12

    # ---- status block
    add('    <g class="fade" style="animation-delay:3.4s">')
    add(f'      <rect x="70" y="548" width="580" height="60" rx="13" fill="{t["panel"]}" '
        f'fill-opacity="{t["panel_op"]}" stroke="{t["stroke"]}" stroke-width="1"/>')
    add(f'      <circle class="live" cx="184" cy="570" r="5" fill="{t["green"]}"/>')
    add(f'      <text x="{CO_CX + 8}" y="576" text-anchor="middle" font-family="{MONO}" '
        f'font-size="20"><tspan fill="{t["green"]}">OPEN TO WORK</tspan>'
        f'<tspan fill="{t["dim"]}"> · Michigan, USA</tspan></text>')
    add(f'      <text x="{CO_CX}" y="600" text-anchor="middle" font-family="{SANS}" font-size="19" '
        f'fill="{t["faint"]}">B.S. Information Assurance &amp; Cyber Defense · EMU</text>')
    add('    </g>')

    add('  </g>')
    add(f'  <rect x="1" y="1" width="{CO_W - 2}" height="{CO_H - 2}" rx="21" fill="none" '
        f'stroke="url(#oEdge)" stroke-width="1.6"/>')
    add('</svg>')
    return "\n".join(p) + "\n"



# ------------------------------------------------------------------ connect chips

# shields.io draws its logos from simple-icons, which no longer carries a
# LinkedIn mark — it was removed at LinkedIn's request — so `logo=linkedin`
# renders a badge with an empty logo slot. These self-hosted chips fix that with
# original glyphs: a globe, a three-node network, a branch. Nobody's trademark is
# reproduced, and the label carries the identification.

CHIP_W, CHIP_H = 236, 52


def _glyph(kind: str, colour: str) -> str:
    """Original line glyphs, drawn on a 24x24 grid centred at (0,0)."""
    st = f'fill="none" stroke="{colour}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "globe":
        return (f'<g {st}><circle cx="0" cy="0" r="9.5"/><ellipse cx="0" cy="0" rx="4" ry="9.5"/>'
                f'<path d="M-9.5 -3h19M-9.5 3h19"/></g>')
    if kind == "network":
        return (f'<g {st}><circle cx="-6.5" cy="-5" r="3"/><circle cx="6.5" cy="-5" r="3"/>'
                f'<circle cx="0" cy="7" r="3"/><path d="M-3.7 -4.2 8.7 -4.2M-5.2 -2.3 -1.3 4.2'
                f'M5.2 -2.3 1.3 4.2"/></g>')
    # branch
    return (f'<g {st}><circle cx="-6" cy="-6.5" r="2.8"/><circle cx="-6" cy="7" r="2.8"/>'
            f'<circle cx="7" cy="-6.5" r="2.8"/><path d="M-6 -3.7v7.9M-3.2 -6.5h7.4'
            f'M7 -3.7c0 5-5 4.2-9.4 6.6"/></g>')


CHIPS = [
    ("connect-portfolio", "Portfolio", "globe", "cyan"),
    ("connect-linkedin", "LinkedIn", "network", "blue"),
    ("connect-github", "GitHub", "branch", "green"),
]


def _chip(t: dict, label: str, kind: str, accent: str) -> str:
    col = t[accent]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CHIP_W}" height="{CHIP_H}" viewBox="0 0 {CHIP_W} {CHIP_H}" role="img" aria-label="{label}">
  <title>{label}</title>
  <defs>
    <linearGradient id="chipEdge" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="{col}" stop-opacity="0.9"/><stop offset="100%" stop-color="{t['green']}" stop-opacity="0.5"/></linearGradient>
    <linearGradient id="chipSheen" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="{col}" stop-opacity="0"/><stop offset="50%" stop-color="{col}" stop-opacity="0.20"/><stop offset="100%" stop-color="{col}" stop-opacity="0"/></linearGradient>
    <clipPath id="chipClip"><rect width="{CHIP_W}" height="{CHIP_H}" rx="{CHIP_H // 2}"/></clipPath>
  </defs>
  <style>
    .sheen{{animation:sheen 5.5s ease-in-out infinite}}
    .dot{{animation:dot 2.6s ease-in-out infinite}}
    @keyframes sheen{{0%{{transform:translateX(-{CHIP_W}px)}}55%,100%{{transform:translateX({CHIP_W}px)}}}}
    @keyframes dot{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
    @media (prefers-reduced-motion: reduce){{.sheen,.dot{{animation:none}}.sheen{{opacity:0}}}}
  </style>
  <g clip-path="url(#chipClip)">
    <rect width="{CHIP_W}" height="{CHIP_H}" rx="{CHIP_H // 2}" fill="{t['panel']}" fill-opacity="{t['panel_op']}"/>
    <rect class="sheen" width="{CHIP_W}" height="{CHIP_H}" fill="url(#chipSheen)"/>
  </g>
  <rect x="1" y="1" width="{CHIP_W - 2}" height="{CHIP_H - 2}" rx="{CHIP_H // 2 - 1}" fill="none" stroke="url(#chipEdge)" stroke-width="1.5"/>
  <g transform="translate(34,{CHIP_H / 2})">{_glyph(kind, col)}</g>
  <text x="60" y="{CHIP_H / 2 + 6}" font-family="{SANS}" font-size="17" font-weight="700" fill="{t['head']}">{label}</text>
  <circle class="dot" cx="{CHIP_W - 26}" cy="{CHIP_H / 2}" r="3.6" fill="{col}"/>
</svg>
"""


# ------------------------------------------------------- two domains, one craft

# Answers the "don't box me into one lane" problem visually: embedded traffic and
# agent traffic run in from opposite sides and meet at the same shield, because
# the discipline underneath them is the same.

DOM_W, DOM_H = 900, 286
DOM_CX = DOM_W // 2


def domains(t: dict) -> str:
    p = []
    add = p.append
    mid = 132

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{DOM_W}" height="{DOM_H}" '
        f'viewBox="0 0 {DOM_W} {DOM_H}" role="img" '
        f'aria-label="Automotive and embedded work on one side, AI agent and software work on the '
        f'other, both validated by the same discipline.">')
    add('  <title>Two domains, one discipline</title>')
    add('  <defs>')
    add(f'    <linearGradient id="dmBg" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{t["bg0"]}"/><stop offset="50%" stop-color="{t["bg1"]}"/>'
        f'<stop offset="100%" stop-color="{t["bg2"]}"/></linearGradient>')
    add(f'    <linearGradient id="dmEdge" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{t["amber"]}" stop-opacity="0.75"/>'
        f'<stop offset="50%" stop-color="{t["cyan"]}" stop-opacity="0.5"/>'
        f'<stop offset="100%" stop-color="{t["blue"]}" stop-opacity="0.75"/></linearGradient>')
    add(f'    <linearGradient id="dmLaneL" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{t["amber"]}" stop-opacity="0"/>'
        f'<stop offset="100%" stop-color="{t["amber"]}" stop-opacity="0.55"/></linearGradient>')
    add(f'    <linearGradient id="dmLaneR" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{t["blue"]}" stop-opacity="0.55"/>'
        f'<stop offset="100%" stop-color="{t["blue"]}" stop-opacity="0"/></linearGradient>')
    add(f'    <radialGradient id="dmHalo" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="{t["cyan"]}" stop-opacity="0.4"/>'
        f'<stop offset="100%" stop-color="{t["cyan"]}" stop-opacity="0"/></radialGradient>')
    add(f'    <pattern id="dmGrid" width="36" height="36" patternUnits="userSpaceOnUse">'
        f'<path d="M36 0H0v36" fill="none" stroke="{t["grid"]}" stroke-opacity="{t["grid_op"]}" '
        f'stroke-width="1"/></pattern>')
    add(f'    <clipPath id="dmCard"><rect width="{DOM_W}" height="{DOM_H}" rx="18"/></clipPath>')
    add('  </defs>')

    add('  <style>')
    add('    .pkt{animation:runR 3.6s linear infinite}')
    add('    .tok{animation:runL 3.6s linear infinite}')
    add('    .pulse{animation:pulse 3.6s ease-in-out infinite}')
    add('    .fade{animation:fadeIn .7s ease-out backwards}')
    add(f'    @keyframes runR{{0%{{transform:translateX(0);opacity:0}}12%{{opacity:1}}'
        f'82%{{opacity:1}}100%{{transform:translateX(268px);opacity:0}}}}')
    add(f'    @keyframes runL{{0%{{transform:translateX(0);opacity:0}}12%{{opacity:1}}'
        f'82%{{opacity:1}}100%{{transform:translateX(-268px);opacity:0}}}}')
    add('    @keyframes pulse{0%,100%{opacity:.30}46%{opacity:.95}}')
    add('    @keyframes fadeIn{from{opacity:0}}')
    add('    @media (prefers-reduced-motion: reduce){')
    add('      .pkt,.tok,.pulse,.fade{animation:none}.pkt,.tok{opacity:.85}')
    add('    }')
    add('  </style>')

    add('  <g clip-path="url(#dmCard)">')
    add(f'    <rect width="{DOM_W}" height="{DOM_H}" fill="url(#dmBg)"/>')
    add(f'    <rect width="{DOM_W}" height="{DOM_H}" fill="url(#dmGrid)"/>')

    # lane rails
    add(f'    <rect x="86" y="{mid - 1}" width="286" height="2" fill="url(#dmLaneL)"/>')
    add(f'    <rect x="{DOM_W - 372}" y="{mid - 1}" width="286" height="2" fill="url(#dmLaneR)"/>')

    # travelling payloads
    for i in range(5):
        d = round(i * 0.72, 2)
        add(f'    <g class="pkt" style="animation-delay:{d}s">'
            f'<rect x="86" y="{mid - 5}" width="16" height="10" rx="2.5" fill="{t["amber"]}"/></g>')
        add(f'    <g class="tok" style="animation-delay:{round(d + 0.36, 2)}s">'
            f'<circle cx="{DOM_W - 86}" cy="{mid}" r="5" fill="{t["blue"]}"/></g>')

    # left domain — embedded
    add('    <g class="fade" style="animation-delay:.1s">')
    add(f'      <rect x="30" y="{mid - 34}" width="58" height="68" rx="11" fill="{t["panel"]}" '
        f'fill-opacity="{t["panel_op"]}" stroke="{t["amber"]}" stroke-opacity="0.6" stroke-width="1.4"/>')
    add(f'      <rect x="46" y="{mid - 16}" width="26" height="32" rx="4" fill="none" '
        f'stroke="{t["amber"]}" stroke-width="1.8"/>')
    for dy in (-9, -1, 7):
        add(f'      <path d="M38 {mid + dy}h8M72 {mid + dy}h8" stroke="{t["amber"]}" '
            f'stroke-width="1.6" stroke-linecap="round"/>')
    add(f'      <text x="59" y="{mid - 48}" text-anchor="middle" font-family="{MONO}" font-size="12" '
        f'letter-spacing="1.2" fill="{t["amber"]}">ECU</text>')
    add('    </g>')
    add(f'    <text x="30" y="{mid + 74}" font-family="{SANS}" font-size="17" font-weight="700" '
        f'fill="{t["head"]}">Automotive &amp; Embedded</text>')
    add(f'    <text x="30" y="{mid + 96}" font-family="{MONO}" font-size="13" fill="{t["dim"]}">'
        f'CAN · UDS · secure boot · TPM</text>')

    # right domain — agents
    add('    <g class="fade" style="animation-delay:.2s">')
    add(f'      <rect x="{DOM_W - 88}" y="{mid - 34}" width="58" height="68" rx="11" '
        f'fill="{t["panel"]}" fill-opacity="{t["panel_op"]}" stroke="{t["blue"]}" '
        f'stroke-opacity="0.6" stroke-width="1.4"/>')
    ax = DOM_W - 59
    add(f'      <circle cx="{ax}" cy="{mid - 10}" r="5.5" fill="none" stroke="{t["blue"]}" stroke-width="1.8"/>')
    add(f'      <circle cx="{ax - 11}" cy="{mid + 11}" r="4.5" fill="none" stroke="{t["blue"]}" stroke-width="1.8"/>')
    add(f'      <circle cx="{ax + 11}" cy="{mid + 11}" r="4.5" fill="none" stroke="{t["blue"]}" stroke-width="1.8"/>')
    add(f'      <path d="M{ax - 3.5} {mid - 5.5} {ax - 8} {mid + 6.5}M{ax + 3.5} {mid - 5.5} '
        f'{ax + 8} {mid + 6.5}" stroke="{t["blue"]}" stroke-width="1.6" stroke-linecap="round"/>')
    add(f'      <text x="{ax}" y="{mid - 48}" text-anchor="middle" font-family="{MONO}" font-size="12" '
        f'letter-spacing="1.2" fill="{t["blue"]}">AGENT</text>')
    add('    </g>')
    add(f'    <text x="{DOM_W - 30}" y="{mid + 74}" text-anchor="end" font-family="{SANS}" '
        f'font-size="17" font-weight="700" fill="{t["head"]}">AI Agents &amp; Software</text>')
    add(f'    <text x="{DOM_W - 30}" y="{mid + 96}" text-anchor="end" font-family="{MONO}" '
        f'font-size="13" fill="{t["dim"]}">guardrails · audit trails · approvals</text>')

    # the shared gate
    add(f'    <circle cx="{DOM_CX}" cy="{mid}" r="74" fill="url(#dmHalo)"/>')
    hx = (f"M{DOM_CX} {mid - 52} L{DOM_CX + 45} {mid - 26} L{DOM_CX + 45} {mid + 26} "
          f"L{DOM_CX} {mid + 52} L{DOM_CX - 45} {mid + 26} L{DOM_CX - 45} {mid - 26} Z")
    add(f'    <path d="{hx}" fill="{t["panel"]}" fill-opacity="{t["panel_op"]}" '
        f'stroke="url(#dmEdge)" stroke-width="1.8"/>')
    add(f'    <path class="pulse" d="{hx}" fill="none" stroke="{t["cyan"]}" stroke-width="7" '
        f'stroke-opacity="0.30"/>')
    add(f'    <path d="M{DOM_CX - 16} {mid + 1} l11 11 l21 -22" fill="none" stroke="{t["green"]}" '
        f'stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')
    add(f'    <text x="{DOM_CX}" y="{mid + 74}" text-anchor="middle" font-family="{MONO}" '
        f'font-size="12" letter-spacing="2.6" fill="{t["cyan"]}">VERIFY BEFORE TRUST</text>')

    add(f'    <line x1="30" y1="{DOM_H - 52}" x2="{DOM_W - 30}" y2="{DOM_H - 52}" '
        f'stroke="{t["stroke"]}" stroke-width="1"/>')
    add(f'    <text x="{DOM_CX}" y="{DOM_H - 24}" text-anchor="middle" font-family="{SANS}" '
        f'font-size="15" fill="{t["text"]}">Two domains, one discipline — the threat model changes, '
        f'the rigour does not.</text>')
    add('  </g>')
    add(f'  <rect x="1" y="1" width="{DOM_W - 2}" height="{DOM_H - 2}" rx="17" fill="none" '
        f'stroke="url(#dmEdge)" stroke-width="1.4"/>')
    add('</svg>')
    return "\n".join(p) + "\n"



# ---------------------------------------------------------------- section headers

# Same language as the connect chips — rounded panel, original line glyph, accent
# bar and a slow sheen — applied to the section headings so the page reads as one
# designed thing rather than art bolted onto default markdown.

HEAD_H = 64
_HEAD_ADVANCE = 12.6   # ~0.57em per glyph for 22px semibold sans


def _head_glyph(kind: str, colour: str) -> str:
    st = (f'fill="none" stroke="{colour}" stroke-width="1.9" stroke-linecap="round" '
          f'stroke-linejoin="round"')
    if kind == "person":
        return (f'<g {st}><circle cx="0" cy="-5" r="4.6"/>'
                f'<path d="M-8.5 9.5c0-4.7 3.8-7.6 8.5-7.6s8.5 2.9 8.5 7.6"/></g>')
    if kind == "briefcase":
        return (f'<g {st}><rect x="-10" y="-4.5" width="20" height="13.5" rx="2.4"/>'
                f'<path d="M-4.5 -4.5v-2.6a2 2 0 0 1 2-2h5a2 2 0 0 1 2 2v2.6M-10 1.5h20"/></g>')
    if kind == "layers":
        return (f'<g {st}><path d="M0 -9.5 10 -4 0 1.5 -10 -4Z"/>'
                f'<path d="M-10 1.5 0 7 10 1.5"/></g>')
    if kind == "flask":
        return (f'<g {st}><path d="M-3.4 -9v6.4L-9 6.2a2.4 2.4 0 0 0 2 3.7h14a2.4 2.4 0 0 0 2-3.7'
                f'L3.4 -2.6V-9"/><path d="M-5.4 -9h10.8M-6.2 3h12.4"/></g>')
    if kind == "pulse":
        return (f'<g {st}><path d="M-10 0h5l3 -7 4 14 3 -7h5"/></g>')
    if kind == "seal":
        return (f'<g {st}><circle cx="0" cy="-2.4" r="6.9"/>'
                f'<path d="M-4.3 3.3 -6.2 10.2 0 7.2 6.2 10.2 4.3 3.3"/>'
                f'<path d="M-2.7 -2.6 -1 -0.8 2.7 -4.5"/></g>')
    # network, matching the LinkedIn chip
    return (f'<g {st}><circle cx="-6.5" cy="-5" r="3"/><circle cx="6.5" cy="-5" r="3"/>'
            f'<circle cx="0" cy="7" r="3"/><path d="M-3.7 -4.2 8.7 -4.2M-5.2 -2.3 -1.3 4.2'
            f'M5.2 -2.3 1.3 4.2"/></g>')


HEADERS = [
    ("head-about", "About", "person", "cyan"),
    ("head-experience", "Industry Experience", "briefcase", "amber"),
    ("head-certs", "Certifications", "seal", "amber"),
    ("head-projects", "Selected Projects", "layers", "blue"),
    ("head-labs", "Security Labs &amp; Research", "flask", "cyan"),
    ("head-activity", "GitHub Activity", "pulse", "green"),
    ("head-connect", "Let\u2019s Connect", "network", "green"),
]


def _header(t: dict, label: str, kind: str, accent: str) -> str:
    plain = label.replace("&amp;", "&")
    w = round(58 + len(plain) * _HEAD_ADVANCE + 34)
    col = t[accent]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{HEAD_H}" viewBox="0 0 {w} {HEAD_H}" role="img" aria-label="{label}">
  <title>{label}</title>
  <defs>
    <linearGradient id="hdEdge" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="{col}" stop-opacity="0.85"/><stop offset="100%" stop-color="{col}" stop-opacity="0.15"/></linearGradient>
    <linearGradient id="hdSheen" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="{col}" stop-opacity="0"/><stop offset="50%" stop-color="{col}" stop-opacity="0.18"/><stop offset="100%" stop-color="{col}" stop-opacity="0"/></linearGradient>
    <clipPath id="hdClip"><rect width="{w}" height="{HEAD_H}" rx="14"/></clipPath>
  </defs>
  <style>
    .sheen{{animation:sheen 6.5s ease-in-out infinite}}
    .dot{{animation:dot 3s ease-in-out infinite}}
    @keyframes sheen{{0%{{transform:translateX(-{w}px)}}55%,100%{{transform:translateX({w}px)}}}}
    @keyframes dot{{0%,100%{{opacity:.3}}50%{{opacity:1}}}}
    @media (prefers-reduced-motion: reduce){{.sheen,.dot{{animation:none}}.sheen{{opacity:0}}}}
  </style>
  <g clip-path="url(#hdClip)">
    <rect width="{w}" height="{HEAD_H}" fill="{t['panel']}" fill-opacity="{t['panel_op']}"/>
    <rect class="sheen" width="{w}" height="{HEAD_H}" fill="url(#hdSheen)"/>
    <rect x="0" y="0" width="5" height="{HEAD_H}" fill="{col}"/>
  </g>
  <rect x="1" y="1" width="{w - 2}" height="{HEAD_H - 2}" rx="13" fill="none" stroke="url(#hdEdge)" stroke-width="1.4"/>
  <g transform="translate(34,{HEAD_H / 2})">{_head_glyph(kind, col)}</g>
  <text x="58" y="{HEAD_H / 2 + 8}" font-family="{SANS}" font-size="22" font-weight="700" fill="{t['head']}">{label}</text>
  <circle class="dot" cx="{w - 22}" cy="{HEAD_H / 2}" r="3.4" fill="{col}"/>
</svg>
"""



# ------------------------------------------------------------------ certifications

# A rack of credential tiles, in the same panel / accent-bar / sheen language as
# the section headings, so it reads as part of the page rather than a badge dump.
#
# Driven off CERTS: the geometry, the canvas width and the per-tile gradients all
# follow the list, so adding or renaming a credential is a one-line edit.
#
# Resting state is the finished state. The entry animation only has a `from`
# keyframe and `animation-fill-mode: backwards`, so the from-values apply during
# the delay and nowhere else — if animations never run (reduced motion, a still
# thumbnail, a renderer with no CSS animation) every tile is already in place.

CERT_TILE_W, CERT_TILE_H = 276, 138
CERT_GAP, CERT_PAD = 24, 12


def _cert_face(kind: str, colour: str) -> str:
    """The mark inside the seal, drawn centred on (0,0)."""
    st = (f'fill="none" stroke="{colour}" stroke-width="1.7" stroke-linecap="round" '
          f'stroke-linejoin="round"')
    if kind == "nodes":
        return (f'<g {st}><circle cx="-4.3" cy="-3" r="1.8"/><circle cx="4.3" cy="-3" r="1.8"/>'
                f'<circle cx="0" cy="4.5" r="1.8"/>'
                f'<path d="M-2.5 -3h5M-3.6 -1.4 -1 2.9M3.6 -1.4 1 2.9"/></g>')
    if kind == "headset":
        return (f'<g {st}><path d="M-6 0.6v-1.2a6 6 0 0 1 12 0v1.2"/>'
                f'<path d="M-6 -0.4h1.5v4.2h-1.5ZM4.5 -0.4h1.5v4.2h-1.5Z"/>'
                f'<path d="M6 3.8v0.8a1.9 1.9 0 0 1 -1.9 1.9h-2"/></g>')
    if kind == "route":
        return (f'<g {st}><path d="M-5.6 -4.2h3.9a2.3 2.3 0 0 1 0 4.6h-4.3a2.3 2.3 0 0 0 0 4.6h3.9"/>'
                f'<circle cx="-5.6" cy="-4.2" r="1.4"/><circle cx="5.2" cy="5" r="1.4"/>'
                f'<path d="M0.5 5h3.3"/></g>')
    return f'<g {st}><path d="M-3.5 0.3 -1 2.9 3.7 -2.3"/></g>'


# title, issuer, seal mark, accent key, area tag
CERTS = [
    ("CCNA", "Cisco Networking Academy", "route", "blue", "NETWORKING"),
    ("IT Help Desk", "IT support &amp; troubleshooting", "headset", "green", "IT SUPPORT"),
]

CERT_W = CERT_PAD * 2 + len(CERTS) * CERT_TILE_W + (len(CERTS) - 1) * CERT_GAP
CERT_H = CERT_PAD * 2 + CERT_TILE_H


def certs(t: dict) -> str:
    defs, tiles, style = [], [], []
    for i, (title, issuer, mark, accent, tag) in enumerate(CERTS):
        col = t[accent]
        x = CERT_PAD + i * (CERT_TILE_W + CERT_GAP)
        defs.append(
            f'    <linearGradient id="cEdge{i}" x1="0%" y1="0%" x2="100%" y2="100%">'
            f'<stop offset="0%" stop-color="{col}" stop-opacity="0.8"/>'
            f'<stop offset="100%" stop-color="{col}" stop-opacity="0.14"/></linearGradient>\n'
            f'    <linearGradient id="cSheen{i}" x1="0%" y1="0%" x2="100%" y2="0%">'
            f'<stop offset="0%" stop-color="{col}" stop-opacity="0"/>'
            f'<stop offset="50%" stop-color="{col}" stop-opacity="0.16"/>'
            f'<stop offset="100%" stop-color="{col}" stop-opacity="0"/></linearGradient>')
        style.append(f'    .t{i}{{animation-delay:{0.08 + i * 0.14:.2f}s}}'
                     f'.s{i}{{animation-delay:{i * 1.1:.2f}s}}'
                     f'.r{i}{{animation-delay:-{i * 2.4:.1f}s}}'
                     f'.p{i}{{animation-delay:{i * 0.5:.2f}s}}')
        tiles.append(f"""  <g transform="translate({x},{CERT_PAD})">
    <g class="tile t{i}">
      <g clip-path="url(#cTile)">
        <rect width="{CERT_TILE_W}" height="{CERT_TILE_H}" fill="{t['panel']}" fill-opacity="{t['panel_op']}"/>
        <rect class="sheen s{i}" width="{CERT_TILE_W}" height="{CERT_TILE_H}" fill="url(#cSheen{i})"/>
        <rect width="5" height="{CERT_TILE_H}" fill="{col}"/>
      </g>
      <rect x="1" y="1" width="{CERT_TILE_W - 2}" height="{CERT_TILE_H - 2}" rx="13" fill="none" stroke="url(#cEdge{i})" stroke-width="1.4"/>
      <g transform="translate(42,44)">
        <g class="ring r{i}"><circle r="15.5" fill="none" stroke="{col}" stroke-opacity="0.55" stroke-width="1.3" stroke-dasharray="5 4.5"/></g>
        <circle r="10.8" fill="{col}" fill-opacity="0.12" stroke="{col}" stroke-opacity="0.45" stroke-width="1.1"/>
        {_cert_face(mark, col)}
      </g>
      <text x="74" y="40" font-family="{SANS}" font-size="17" font-weight="700" fill="{t['head']}">{title}</text>
      <text x="74" y="60" font-family="{SANS}" font-size="12" fill="{t['dim']}">{issuer}</text>
      <path d="M22 86H{CERT_TILE_W - 22}" stroke="{t['stroke']}" stroke-width="1"/>
      <circle class="pip p{i}" cx="30" cy="108" r="3.6" fill="{col}"/>
      <text x="43" y="112" font-family="{MONO}" font-size="10.5" letter-spacing="1.6" fill="{t['faint']}">{tag}</text>
    </g>
  </g>""")

    nl = "\n"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CERT_W}" height="{CERT_H}" viewBox="0 0 {CERT_W} {CERT_H}" role="img" aria-label="Certifications">
  <title>Certifications</title>
  <defs>
    <clipPath id="cTile"><rect width="{CERT_TILE_W}" height="{CERT_TILE_H}" rx="14"/></clipPath>
{nl.join(defs)}
  </defs>
  <style>
    .tile{{animation:cIn .75s cubic-bezier(.2,.7,.3,1) backwards}}
    .sheen{{animation:cSheen 7s ease-in-out infinite}}
    .ring{{animation:cSpin 18s linear infinite}}
    .pip{{animation:cPip 3s ease-in-out infinite}}
{nl.join(style)}
    @keyframes cIn{{from{{opacity:0;transform:translateY(14px)}}}}
    @keyframes cSheen{{0%{{transform:translateX(-{CERT_TILE_W}px)}}55%,100%{{transform:translateX({CERT_TILE_W}px)}}}}
    @keyframes cSpin{{to{{transform:rotate(360deg)}}}}
    @keyframes cPip{{0%,100%{{opacity:.35}}50%{{opacity:1}}}}
    @media (prefers-reduced-motion: reduce){{
      .tile,.sheen,.ring,.pip{{animation:none}}.sheen{{opacity:0}}
    }}
  </style>
{nl.join(tiles)}
</svg>
"""



# ------------------------------------------------------------------ inline icons

# Replacements for the emoji in the README. Emoji render differently on every
# platform and sit oddly against the rest of the art; these are the same line
# vocabulary as the header chips.
#
# Deliberately theme-independent — one file each, no -light twin. Inline images
# in list items and headings would need a <picture> block per icon to switch on
# colour scheme, which is a lot of markup for a 16px mark. These use mid-tone
# accents that hold up on both GitHub themes instead.

ICON_INK = {
    "cyan": "#0E9BC4",
    "blue": "#3B82F6",
    "green": "#10B981",
    "amber": "#E08A0B",
}

ICONS = {
    # about bullets
    "shield":  ("cyan",  'M0 -9.5 8.5 -6v5.4C8.5 4.2 4.8 8 0 9.6-4.8 8-8.5 4.2-8.5 -0.6V-6Z'),
    "work":    ("amber", 'M-9.4 -3.6h18.8v11.4h-18.8ZM-4.2 -3.6v-2.6a2 2 0 0 1 2 -2h4.4'
                         'a2 2 0 0 1 2 2v2.6M-9.4 1.4h18.8'),
    "cap":     ("blue",  'M0 -7.4 10.4 -3 0 1.4 -10.4 -3ZM-6 -1.2v5.1C-6 6 -3.3 7.4 0 7.4S6 6 6 3.9v-5.1'),
    "flask":   ("green", 'M-3.2 -8.4v6L-8.4 5.6a2.2 2.2 0 0 0 1.9 3.4h13a2.2 2.2 0 0 0 1.9 -3.4'
                         'L3.2 -2.4v-6M-5.2 -8.4h10.4M-5.9 2.6h11.8'),
    "pin":     ("cyan",  'M0 9.4C0 9.4 7 2.9 7 -2.2A7 7 0 0 0 -7 -2.2C-7 2.9 0 9.4 0 9.4Z'),
    "mail":    ("green", 'M-9.4 -6.2h18.8v12.4h-18.8ZM-9.4 -6.2 0 1.4 9.4 -6.2'),
    # project cards
    "search":  ("blue",  'M-1.6 -8.4a6.8 6.8 0 1 1 0 13.6 6.8 6.8 0 0 1 0 -13.6ZM3.4 3.4 9.2 9.2'),
    "monitor": ("green", 'M-9.6 -7.6h19.2v12.2h-19.2ZM-3.6 4.6v3.6M3.6 4.6v3.6M-6.4 8.2h12.8'),
    "blocks":  ("blue",  'M-8.6 -8.6h7.2v7.2h-7.2ZM1.4 -8.6h7.2v7.2h-7.2Z'
                         'M-8.6 1.4h7.2v7.2h-7.2ZM1.4 1.4h7.2v7.2h-7.2Z'),
    "doc":     ("cyan",  'M-6.8 -9.4h8.2l5.4 5.4v13.4h-13.6ZM1.4 -9.4v5.4h5.4M-3.8 1.4h7.6M-3.8 5.2h7.6'),
    "bolt":    ("amber", 'M1.8 -9.4 -6.2 1.2h5.6L-2.2 9.4 6.2 -1.6H0.4Z'),
    # certifications
    "seal":    ("amber", 'M0 -9.6a6.6 6.6 0 1 1 0 13.2 6.6 6.6 0 0 1 0 -13.2Z'
                         'M-4.1 3.1 -6 9.7 0 6.9 6 9.7 4.1 3.1M-2.6 -3.2 -0.9 -1.4 2.6 -5'),
    # the snake heading
    "grid":    ("green", 'M-9 -9h5.4v5.4h-5.4ZM-2.7 -9h5.4v5.4h-5.4ZM3.6 -9h5.4v5.4h-5.4Z'
                         'M-9 -2.7h5.4v5.4h-5.4ZM-2.7 -2.7h5.4v5.4h-5.4ZM3.6 -2.7h5.4v5.4h-5.4Z'
                         'M-9 3.6h5.4v5.4h-5.4ZM-2.7 3.6h5.4v5.4h-5.4Z'),
}


def icon(name: str) -> str:
    accent, d = ICONS[name]
    col = ICON_INK[accent]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
            f'role="presentation" aria-hidden="true">\n'
            f'  <g transform="translate(12,12)" fill="none" stroke="{col}" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round">\n'
            f'    <path d="{d}"/>\n'
            f'  </g>\n</svg>\n')


ASSETS = {"hero": hero, "hero-compact": hero_compact, "credential": credential,
          "divider": divider, "domains": domains, "certs": certs}
for _stem, _label, _kind, _accent in CHIPS:
    ASSETS[_stem] = (lambda lb, kd, ac: lambda t: _chip(t, lb, kd, ac))(_label, _kind, _accent)
for _stem, _label, _kind, _accent in HEADERS:
    ASSETS[_stem] = (lambda lb, kd, ac: lambda t: _header(t, lb, kd, ac))(_label, _kind, _accent)


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "assets")
    out.mkdir(parents=True, exist_ok=True)
    for theme in THEMES.values():
        for stem, fn in ASSETS.items():
            path = out / (stem + theme["suffix"] + ".svg")
            path.write_text(fn(theme), encoding="utf-8")
            print("wrote", path)
    for name in ICONS:
        path = out / f"icon-{name}.svg"
        path.write_text(icon(name), encoding="utf-8")
        print("wrote", path)


if __name__ == "__main__":
    main()
