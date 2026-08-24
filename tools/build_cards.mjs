#!/usr/bin/env node
/**
 * Render the GitHub activity cards the README used to pull from third-party
 * widget hosts (github-readme-stats, streak-stats, activity-graph, trophies).
 *
 * Those services rate-limit and go down, which shows up as broken images on the
 * profile. These cards are built from the GitHub GraphQL API in CI and published
 * to the `output` branch next to the contribution snake, so every image on the
 * profile is served by GitHub itself.
 *
 *   node tools/build_cards.mjs <outDir>            # live, needs GITHUB_TOKEN
 *   node tools/build_cards.mjs <outDir> --mock     # fixture data, for layout work
 *
 * Cards are authored 600px wide and carry no width attribute in the README, so
 * they render 1:1 on desktop and shrink under `max-width:100%` on a phone while
 * keeping every label above ~9px.
 */

const LOGIN = process.env.PROFILE_LOGIN || "michealswolski";
const W = 600;

const SANS = "'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif";
const MONO = "'SF Mono', 'JetBrains Mono', Consolas, 'Courier New', monospace";

const THEMES = {
  dark: {
    suffix: "", bg0: "#050B16", bg1: "#0A1526", bg2: "#0F1F35",
    text: "#E2E8F0", head: "#F8FAFC", dim: "#94A3B8", faint: "#64748B",
    cyan: "#22D3EE", cyanL: "#67E8F9", blue: "#3B82F6", green: "#34D399", amber: "#FBBF24",
    panel: "#0B1526", panelOp: "0.55", stroke: "#1E293B", grid: "#3B82F6", gridOp: "0.075",
  },
  light: {
    suffix: "-light", bg0: "#F7FBFE", bg1: "#EAF3FA", bg2: "#DDEBF6",
    text: "#1E293B", head: "#0F172A", dim: "#475569", faint: "#64748B",
    cyan: "#0E7490", cyanL: "#0891B2", blue: "#1D4ED8", green: "#047857", amber: "#B45309",
    panel: "#FFFFFF", panelOp: "0.75", stroke: "#CBD5E1", grid: "#0E7490", gridOp: "0.10",
  },
};

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const compact = (n) =>
  n >= 1000000 ? (n / 1000000).toFixed(1).replace(/\.0$/, "") + "M"
  : n >= 1000 ? (n / 1000).toFixed(1).replace(/\.0$/, "") + "k"
  : String(n);

/* ------------------------------------------------------------------ data --- */

const QUERY = `
query($login:String!){
  user(login:$login){
    followers{totalCount}
    repositories(first:100, ownerAffiliations:OWNER, isFork:false, orderBy:{field:PUSHED_AT,direction:DESC}){
      totalCount
      nodes{
        stargazerCount
        languages(first:10, orderBy:{field:SIZE,direction:DESC}){ edges{ size node{ name color } } }
      }
    }
    contributionsCollection{
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount } }
      }
    }
  }
}`;

async function fetchUser() {
  // The default workflow GITHUB_TOKEN is a GitHub App installation token, which
  // frequently cannot read `contributionsCollection` for a user. PROFILE_TOKEN
  // (a classic PAT with read:user) is preferred when the repo defines it.
  const token = process.env.PROFILE_TOKEN || process.env.GITHUB_TOKEN;
  if (!token) throw new Error("neither PROFILE_TOKEN nor GITHUB_TOKEN is set");
  const res = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      Authorization: `bearer ${token}`,
      "Content-Type": "application/json",
      "User-Agent": `${LOGIN}-profile-cards`,
    },
    body: JSON.stringify({ query: QUERY, variables: { login: LOGIN } }),
  });
  if (!res.ok) throw new Error(`GitHub API returned HTTP ${res.status}`);
  const json = await res.json();
  if (json.errors?.length) throw new Error("GraphQL: " + json.errors.map((e) => e.message).join("; "));
  if (!json.data?.user) throw new Error(`no such user: ${LOGIN}`);
  return json.data.user;
}

/** Longest / current run of consecutive days with at least one contribution. */
function streaks(days) {
  let longest = 0, run = 0;
  for (const d of days) {
    run = d.count > 0 ? run + 1 : 0;
    if (run > longest) longest = run;
  }
  let current = 0;
  for (let i = days.length - 1; i >= 0; i--) {
    // today may legitimately be empty this early in the day; don't break the streak on it
    if (days[i].count === 0) { if (i === days.length - 1) continue; break; }
    current++;
  }
  return { longest, current };
}

const TOKEN_HINT =
  "the token could not read this field. The default GITHUB_TOKEN is an App " +
  "installation token and often cannot; add a repository secret PROFILE_TOKEN " +
  "holding a classic PAT with the read:user scope.";

function shape(user) {
  const cc = user.contributionsCollection;
  if (!cc?.contributionCalendar?.weeks?.length) {
    throw new Error(`contributionsCollection came back empty — ${TOKEN_HINT}`);
  }
  if (!user.repositories) throw new Error(`repositories came back empty — ${TOKEN_HINT}`);

  const repos = user.repositories.nodes ?? [];
  const stars = repos.reduce((a, r) => a + r.stargazerCount, 0);

  const byLang = new Map();
  for (const r of repos) {
    for (const e of r.languages?.edges ?? []) {
      const cur = byLang.get(e.node.name) ?? { size: 0, color: e.node.color };
      cur.size += e.size;
      if (!cur.color && e.node.color) cur.color = e.node.color;
      byLang.set(e.node.name, cur);
    }
  }
  const totalBytes = [...byLang.values()].reduce((a, l) => a + l.size, 0) || 1;
  const langs = [...byLang.entries()]
    .map(([name, v]) => ({ name, pct: (v.size / totalBytes) * 100, color: v.color }))
    .sort((a, b) => b.pct - a.pct)
    .slice(0, 8);

  const cal = cc.contributionCalendar;
  const days = cal.weeks.flatMap((w) => w.contributionDays).map((d) => ({ date: d.date, count: d.contributionCount }));
  const weeks = cal.weeks.map((w) => ({
    date: w.contributionDays[0]?.date,
    total: w.contributionDays.reduce((a, d) => a + d.contributionCount, 0),
  }));

  return {
    repos: user.repositories.totalCount,
    stars,
    followers: user.followers.totalCount,
    commits: cc.totalCommitContributions ?? 0,
    prs: cc.totalPullRequestContributions ?? 0,
    issues: cc.totalIssueContributions ?? 0,
    contributions: cal.totalContributions,
    ...streaks(days),
    langs,
    weeks,
  };
}

/* ----------------------------------------------------------------- chrome --- */

function open(t, h, label, extraDefs = "", extraStyle = "") {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${h}" viewBox="0 0 ${W} ${h}" role="img" aria-label="${esc(label)}">
  <title>${esc(label)}</title>
  <defs>
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="${t.bg0}"/><stop offset="55%" stop-color="${t.bg1}"/><stop offset="100%" stop-color="${t.bg2}"/></linearGradient>
    <linearGradient id="edge" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="${t.cyan}" stop-opacity="0.8"/><stop offset="50%" stop-color="${t.blue}" stop-opacity="0.4"/><stop offset="100%" stop-color="${t.green}" stop-opacity="0.75"/></linearGradient>
    <pattern id="grid" width="34" height="34" patternUnits="userSpaceOnUse"><path d="M34 0H0v34" fill="none" stroke="${t.grid}" stroke-opacity="${t.gridOp}" stroke-width="1"/></pattern>
    <clipPath id="card"><rect width="${W}" height="${h}" rx="16"/></clipPath>${extraDefs}
  </defs>
  <style>
    .fade{animation:fadeIn .6s ease-out backwards}
    .grow{transform-box:fill-box;transform-origin:left center;animation:grow .9s cubic-bezier(.16,.9,.24,1) backwards}
    .rise{animation:rise .7s cubic-bezier(.16,.9,.24,1) backwards}
    .reveal{animation:reveal 1.1s cubic-bezier(.16,.9,.24,1) backwards}
    @keyframes fadeIn{from{opacity:0}}
    @keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
    @keyframes rise{from{opacity:0;transform:translateY(8px)}}
    @keyframes reveal{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
    @media (prefers-reduced-motion: reduce){.fade,.grow,.rise,.reveal{animation:none}}${extraStyle}
  </style>
  <g clip-path="url(#card)">
    <rect width="${W}" height="${h}" fill="url(#cardBg)"/>
    <rect width="${W}" height="${h}" fill="url(#grid)"/>`;
}

const close = (h) =>
  `  </g>
  <rect x="1" y="1" width="${W - 2}" height="${h - 2}" rx="15" fill="none" stroke="url(#edge)" stroke-width="1.4"/>
</svg>
`;

const heading = (t, txt) =>
  `    <text x="18" y="34" font-family="${MONO}" font-size="17" letter-spacing="2.2" fill="${t.cyan}">${esc(txt)}</text>`;

/* ------------------------------------------------------------------ cards --- */

function statsCard(t, d) {
  const h = 272;
  const tiles = [
    ["REPOSITORIES", compact(d.repos), t.cyan],
    ["TOTAL STARS", compact(d.stars), t.amber],
    ["FOLLOWERS", compact(d.followers), t.blue],
    ["CONTRIBUTIONS", compact(d.contributions), t.green],
    ["CURRENT STREAK", `${d.current}d`, t.cyan],
    ["LONGEST STREAK", `${d.longest}d`, t.green],
  ];
  const tw = 180, gap = 12, x0 = 18;
  let out = open(t, h, `GitHub statistics for ${LOGIN}`) + "\n" + heading(t, "GITHUB · STATS");
  out += `\n    <text x="${W - 18}" y="34" text-anchor="end" font-family="${MONO}" font-size="14" fill="${t.faint}">last 12 months</text>`;
  tiles.forEach(([label, value, colour], i) => {
    const x = x0 + (i % 3) * (tw + gap);
    const y = 56 + Math.floor(i / 3) * 92;
    out += `
    <g class="rise" style="animation-delay:${(0.08 + i * 0.06).toFixed(2)}s">
      <rect x="${x}" y="${y}" width="${tw}" height="80" rx="12" fill="${t.panel}" fill-opacity="${t.panelOp}" stroke="${t.stroke}" stroke-width="1"/>
      <rect x="${x}" y="${y}" width="4" height="80" rx="2" fill="${colour}"/>
      <text x="${x + 18}" y="${y + 42}" font-family="${SANS}" font-size="30" font-weight="800" fill="${t.head}">${esc(value)}</text>
      <text x="${x + 18}" y="${y + 66}" font-family="${MONO}" font-size="16" letter-spacing="0.6" fill="${t.dim}">${esc(label)}</text>
    </g>`;
  });
  out += `
    <text x="18" y="${h - 18}" font-family="${MONO}" font-size="15" fill="${t.faint}">${d.commits} commits · ${d.prs} pull requests · ${d.issues} issues opened</text>`;
  return out + "\n" + close(h);
}

function langsCard(t, d) {
  const h = 60 + 34 + 28 + Math.ceil(d.langs.length / 2) * 26;
  const barW = W - 36;
  const barDefs = `
    <clipPath id="barClip"><rect x="18" y="56" width="${barW}" height="22" rx="11"/></clipPath>`;
  let out = open(t, h, `Most used languages for ${LOGIN}`, barDefs) + "\n" + heading(t, "GITHUB · LANGUAGES");

  out += `\n    <g clip-path="url(#barClip)"><g class="grow" style="animation-delay:.15s">`;
  let x = 18;
  d.langs.forEach((l, i) => {
    const w = Math.max((l.pct / 100) * barW, 2);
    out += `
      <rect x="${x.toFixed(1)}" y="56" width="${w.toFixed(1)}" height="22" fill="${l.color || t.blue}"/>`;
    x += w;
  });
  out += `
    </g></g>
    <rect x="18" y="56" width="${barW}" height="22" rx="11" fill="none" stroke="${t.stroke}" stroke-width="1"/>`;

  d.langs.forEach((l, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const lx = 18 + col * (barW / 2), ly = 112 + row * 26;
    out += `
    <g class="fade" style="animation-delay:${(0.3 + i * 0.05).toFixed(2)}s">
      <circle cx="${lx + 6}" cy="${ly - 5}" r="6" fill="${l.color || t.blue}"/>
      <text x="${lx + 20}" y="${ly}" font-family="${SANS}" font-size="16" fill="${t.text}">${esc(l.name)}</text>
      <text x="${lx + barW / 2 - 18}" y="${ly}" text-anchor="end" font-family="${MONO}" font-size="15" fill="${t.dim}">${l.pct.toFixed(1)}%</text>
    </g>`;
  });
  return out + "\n" + close(h);
}

function activityCard(t, d) {
  const h = 244;
  const x0 = 18, x1 = W - 18, yTop = 62, yBot = 176;
  const pts = d.weeks;
  const max = Math.max(1, ...pts.map((p) => p.total));
  const sx = (i) => x0 + (i / Math.max(1, pts.length - 1)) * (x1 - x0);
  const sy = (v) => yBot - (v / max) * (yBot - yTop);

  const line = pts.map((p, i) => `${i ? "L" : "M"}${sx(i).toFixed(1)} ${sy(p.total).toFixed(1)}`).join(" ");
  const area = `${line} L${x1} ${yBot} L${x0} ${yBot} Z`;

  const extraDefs = `
    <linearGradient id="area" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="${t.cyan}" stop-opacity="0.42"/><stop offset="100%" stop-color="${t.cyan}" stop-opacity="0"/></linearGradient>`;

  let out = open(t, h, `Contribution activity for ${LOGIN}`, extraDefs) + "\n" + heading(t, "GITHUB · ACTIVITY");
  out += `\n    <text x="${W - 18}" y="34" text-anchor="end" font-family="${MONO}" font-size="14" fill="${t.faint}">peak ${max}/week</text>`;

  for (let i = 0; i <= 3; i++) {
    const y = yTop + (i / 3) * (yBot - yTop);
    out += `
    <line x1="${x0}" y1="${y.toFixed(1)}" x2="${x1}" y2="${y.toFixed(1)}" stroke="${t.stroke}" stroke-width="1" stroke-opacity="0.7"/>`;
  }
  out += `
    <g class="reveal">
      <path d="${area}" fill="url(#area)"/>
      <path d="${line}" fill="none" stroke="${t.cyan}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
    </g>`;

  // month ticks, first week of each month
  let lastMonth = null, lastX = -Infinity;
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  pts.forEach((p, i) => {
    if (!p.date) return;
    const m = new Date(p.date + "T00:00:00Z").getUTCMonth();
    if (m === lastMonth) return;
    lastMonth = m;
    const x = sx(i);
    // drop a tick that would collide with the previous one or run off the right edge
    if (x - lastX < 40 || x > x1 - 26) return;
    lastX = x;
    out += `
    <text x="${x.toFixed(1)}" y="${yBot + 24}" font-family="${MONO}" font-size="15" fill="${t.faint}">${months[m]}</text>`;
  });

  out += `
    <text x="18" y="${h - 16}" font-family="${MONO}" font-size="15" fill="${t.faint}">${d.contributions} contributions across the last year</text>`;
  return out + "\n" + close(h);
}

/* ------------------------------------------------------------------- main --- */

function mock() {
  const weeks = [];
  const start = Date.UTC(2025, 7, 25);
  for (let i = 0; i < 53; i++) {
    weeks.push({
      date: new Date(start + i * 7 * 86400000).toISOString().slice(0, 10),
      total: Math.round(14 + 13 * Math.sin(i / 4) + (i % 5) * 2),
    });
  }
  return {
    repos: 31, stars: 2, followers: 4, commits: 412, prs: 18, issues: 7,
    contributions: 947, current: 6, longest: 24,
    langs: [
      { name: "JavaScript", pct: 31.4, color: "#f1e05a" },
      { name: "TypeScript", pct: 22.1, color: "#3178c6" },
      { name: "Python", pct: 17.8, color: "#3572A5" },
      { name: "PowerShell", pct: 9.6, color: "#012456" },
      { name: "C", pct: 7.2, color: "#555555" },
      { name: "HTML", pct: 6.0, color: "#e34c26" },
      { name: "Swift", pct: 3.5, color: "#F05138" },
      { name: "Shell", pct: 2.4, color: "#89e051" },
    ],
    weeks,
  };
}

/**
 * Cards rendered without any API call. The README references these six URLs
 * unconditionally, so CI publishes this set rather than leaving the profile
 * pointing at files that do not exist — a missing card is the broken image this
 * whole change set out to remove. It states plainly that data is pending rather
 * than inventing numbers.
 */
function placeholder(t, title, h = 150) {
  return open(t, h, `${title} — awaiting first successful refresh`) +
    "\n" + heading(t, title) + `
    <text x="18" y="${h / 2 + 12}" font-family="${SANS}" font-size="18" fill="${t.dim}">Awaiting the next scheduled refresh.</text>
    <text x="18" y="${h - 20}" font-family="${MONO}" font-size="14" fill="${t.faint}">github.com/${LOGIN}</text>` +
    "\n" + close(h);
}

function writeAll(outDir, render) {
  const { mkdirSync, writeFileSync } = fsMod;
  mkdirSync(outDir, { recursive: true });
  for (const t of Object.values(THEMES)) {
    for (const stem of ["stats", "langs", "activity"]) {
      const p = pathMod.join(outDir, `${stem}${t.suffix}.svg`);
      writeFileSync(p, render(t, stem), "utf8");
      console.log("wrote", p);
    }
  }
}

let fsMod, pathMod;

async function main() {
  fsMod = await import("node:fs");
  pathMod = await import("node:path");
  const outDir = process.argv[2];
  if (!outDir) { console.error("usage: build_cards.mjs <outDir> [--mock|--fallback]"); process.exit(2); }

  const TITLES = { stats: "GITHUB · STATS", langs: "GITHUB · LANGUAGES", activity: "GITHUB · ACTIVITY" };

  if (process.argv.includes("--fallback")) {
    writeAll(outDir, (t, stem) => placeholder(t, TITLES[stem]));
    return;
  }

  const data = process.argv.includes("--mock") ? mock() : shape(await fetchUser());
  const byStem = { stats: statsCard, langs: langsCard, activity: activityCard };
  writeAll(outDir, (t, stem) => byStem[stem](t, data));
}

main().catch((e) => { console.error("card generation failed:", e.message); process.exit(1); });
