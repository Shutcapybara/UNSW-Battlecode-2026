/* Shared, dependency-free parsing. Never execute HTML returned by the site. */
(() => {
  "use strict";
  const clean = text => (text || "").replace(/\s+/g, " ").trim();

  function localPath(href, base, pattern) {
    try {
      const url = new URL(href, base);
      return url.origin === new URL(base).origin && pattern.test(url.pathname)
        ? url.pathname + url.search : null;
    } catch { return null; }
  }

  function parseVersion(text) {
    const match = clean(text).match(/^Your bot:\s*v(\d+)\s*·\s*(.+)$/i);
    return match ? { version: Number(match[1]), name: match[2] } : null;
  }

  function parseReplay(doc, teamId) {
    const team = [...doc.querySelectorAll('main a[href]')].some(a =>
      a.getAttribute("href") === `/teams/${teamId}`);
    if (!team) return null;
    for (const p of doc.querySelectorAll("main p")) {
      const version = parseVersion(p.textContent);
      if (version) return version;
    }
    return null;
  }

  function parseListing(doc, base) {
    if (clean(doc.querySelector("h1")?.textContent) !== "Your battles") {
      throw new Error("Could not read your battles. Check that you are signed in, then retry.");
    }
    const table = [...doc.querySelectorAll("table")].find(t =>
      [...t.querySelectorAll("th")].some(th => clean(th.textContent) === "Your team"));
    const rows = [];
    for (const tr of table?.querySelectorAll("tbody tr") || []) {
      const cells = [...tr.querySelectorAll("td")];
      const replay = tr.querySelector('a[href^="/battles/"]');
      if (!replay) continue;
      const path = localPath(replay.getAttribute("href"), base, /^\/battles\/\d+$/);
      const teamLink = cells[3]?.querySelector('a[href^="/teams/"]');
      const teamId = teamLink?.getAttribute("href").match(/^\/teams\/(\d+)$/)?.[1];
      const opponent = cells[5]?.querySelector('a[href^="/teams/"]');
      if (!path || !teamId || !opponent || cells.length !== 7) {
        throw new Error("The battles table has changed; unable to read it safely.");
      }
      rows.push({
        id: path.split("/").pop(), path, teamId,
        datetime: tr.querySelector("time")?.getAttribute("datetime") || "",
        time: clean(cells[0].textContent), kind: clean(cells[1].textContent),
        delta: clean(cells[2].textContent), team: clean(teamLink.textContent),
        score: clean(cells[4].textContent), opponent: clean(opponent.textContent),
        opponentPath: localPath(opponent.getAttribute("href"), base, /^\/teams\/\d+$/)
      });
    }
    const next = [...doc.querySelectorAll('nav[aria-label="Pages"] a[href]')]
      .find(a => clean(a.textContent) === "Next");
    const nextPath = next ? localPath(next.getAttribute("href"), base, /^\/team\/battles\/?$/) : null;
    if (next && !nextPath) throw new Error("Unexpected pagination link.");
    // A missing table is legitimate only when the site explicitly reports no battles.
    if (!table && !/(?:^|\D)0 battles\b|no battles/i.test(doc.querySelector("main")?.textContent || "")) {
      throw new Error("Could not find the battles table; the site layout may have changed.");
    }
    return { rows, next: nextPath };
  }

  function matches(row, { version = "all", query = "", ranked = true, unranked = true }) {
    if (version === "unknown" && row.bot) return false;
    if (version !== "all" && version !== "unknown" && String(row.bot?.version) !== version) return false;
    if (row.kind === "Ranked" && !ranked || row.kind === "Unranked" && !unranked) return false;
    return row.opponent.toLocaleLowerCase().includes(query.trim().toLocaleLowerCase());
  }

  const api = { clean, localPath, parseVersion, parseReplay, parseListing, matches };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else globalThis.BattlecodeVersionFilter = api;
})();
