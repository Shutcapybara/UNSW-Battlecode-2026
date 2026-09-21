(() => {
  "use strict";
  const C = globalThis.BattlecodeVersionFilter;
  const storage = (globalThis.browser || globalThis.chrome)?.storage?.local;
  let mounted = null;

  function element(tag, text, attrs = {}) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
    return node;
  }
  function text(node, value) {
    if (node.textContent !== value) node.textContent = value;
  }
  // Retain the site's row structure and CSS classes, never fetched executable HTML.
  function copyRow(source) {
    const allowed = new Set(["TR", "TD", "SPAN", "I", "A", "TIME", "B", "STRONG"]);
    function copy(node) {
      if (node.nodeType === Node.TEXT_NODE) return document.createTextNode(node.textContent);
      if (node.nodeType !== Node.ELEMENT_NODE || !allowed.has(node.tagName)) return document.createTextNode("");
      const result = document.createElement(node.tagName.toLowerCase());
      for (const attr of ["class", "title", "datetime", "aria-label"]) {
        if (node.hasAttribute(attr)) result.setAttribute(attr, node.getAttribute(attr));
      }
      if (node.tagName === "A") {
        const path = C.localPath(node.getAttribute("href"), location.href, /^\/(teams|battles)\/\d+$/);
        if (path) result.setAttribute("href", path);
      }
      const color = node.style.color;
      if (/^var\(--color-tier-[a-z-]+\)$/.test(color)) result.style.color = color;
      for (const child of node.childNodes) result.append(copy(child));
      return result;
    }
    return copy(source);
  }

  function mount(toolbar) {
    const controls = element("span", undefined, { class: "bcvf-controls", "data-bcvf": "controls" });
    const select = element("select", undefined, {
      class: "input input-sm field bcvf-select", "aria-label": "Our bot version",
      title: "Filter battles across all pages by the bot version used"
    });
    const status = element("span", "Loading versions…", { class: "stamp bcvf-status", role: "status", "aria-live": "polite" });
    const retry = element("button", "Retry", { type: "button", class: "chip px-2 py-0.5", hidden: "" });
    controls.append(select, status, retry);
    toolbar.append(controls);
    let disposed = false, controller = null, rows = [], selected = "all", optionsKey = "";
    let nativeTable = null, filteredTable = null, summary = null, hiddenNav = null;
    let ready = false, problem = "", cache = {}, cacheKey = null;
    let renderKey = "", revision = 0;

    function versionCell(row, bot, error) {
      let cell = row.querySelector('[data-bcvf="version"]');
      if (!cell) {
        const header = row.parentElement?.tagName === "THEAD";
        cell = element(header ? "th" : "td", "", { "data-bcvf": "version" });
        cell.className = (row.children[1]?.className || "stamp") + " bcvf-version";
        if (header) cell.setAttribute("scope", "col");
        row.insertBefore(cell, row.children[2] || null);
      }
      const header = cell.tagName === "TH";
      text(cell, header ? "Version" : bot ? `v${bot.version}` : ready ? "—" : "…");
      const title = header ? "Bot submission used in this battle" : bot?.name || error || (ready ? "Version unavailable" : "Looking up version");
      if (cell.title !== title) cell.title = title;
    }
    function restore() {
      nativeTable?.classList.remove("bcvf-hidden");
      hiddenNav?.classList.remove("bcvf-hidden");
      filteredTable?.remove();
      summary?.remove();
      filteredTable = summary = hiddenNav = null;
      renderKey = "";
    }
    function refresh() {
      if (disposed) return;
      const table = document.querySelector('main .battle-table table:not([data-bcvf="results"])');
      if (nativeTable !== table) { restore(); nativeTable = table; }
      const versions = new Map();
      for (const row of rows) if (row.bot) versions.set(row.bot.version, row.bot.name);
      const entries = [...versions].sort((a, b) => b[0] - a[0]);
      const key = JSON.stringify(entries);
      if (key !== optionsKey || !select.options.length) {
        optionsKey = key;
        select.replaceChildren(element("option", "All versions", { value: "all" }));
        for (const [v, name] of entries) select.append(element("option", `v${v}`, { value: String(v), title: name }));
        // Keep the selection stable while retrying or refreshing.
        if (selected !== "all" && selected !== "unknown" && !versions.has(Number(selected))) {
          select.append(element("option", `v${selected}`, { value: selected }));
        }
        select.append(element("option", "Unknown", { value: "unknown" }));
        select.value = selected;
      }
      if (!nativeTable) return;
      const indexed = new Map(rows.map(row => [row.path, row]));
      for (const tr of nativeTable.querySelectorAll("thead tr")) versionCell(tr);
      for (const tr of nativeTable.querySelectorAll("tbody tr")) {
        const path = tr.querySelector('a[href^="/battles/"]')?.getAttribute("href");
        if (!path) continue;
        const row = indexed.get(path);
        versionCell(tr, row?.bot, row?.error);
      }
      if (selected === "all") { restore(); return; }
      const query = toolbar.querySelector('input[aria-label="Search opponents"]')?.value || "";
      const checks = [...toolbar.querySelectorAll('input[type="checkbox"]')];
      const ranked = checks.find(input => C.clean(input.closest("label")?.textContent) === "Ranked")?.checked ?? true;
      const unranked = checks.find(input => C.clean(input.closest("label")?.textContent) === "Unranked")?.checked ?? true;
      const nextKey = JSON.stringify([selected, query, ranked, unranked, revision, ready]);
      const nav = document.querySelector('main nav[aria-label="Pages"]');
      if (hiddenNav !== nav) { hiddenNav?.classList.remove("bcvf-hidden"); hiddenNav = nav; }
      hiddenNav?.classList.add("bcvf-hidden");
      nativeTable.classList.add("bcvf-hidden");
      if (!filteredTable) {
        filteredTable = nativeTable.cloneNode(false);
        filteredTable.removeAttribute("id");
        filteredTable.classList.remove("bcvf-hidden");
        filteredTable.dataset.bcvf = "results";
        filteredTable.append(nativeTable.querySelector("thead").cloneNode(true), element("tbody"));
        nativeTable.after(filteredTable);
        summary = element("p", "", { class: "stamp mt-3", "data-bcvf": "summary", role: "status" });
        nativeTable.closest(".battle-table").after(summary);
      }
      if (nextKey === renderKey) return;
      renderKey = nextKey;
      const filtered = rows.filter(row => C.matches(row, { version: selected, query, ranked, unranked }));
      const fragment = document.createDocumentFragment();
      for (const row of filtered) {
        const tr = row.template.cloneNode(true);
        versionCell(tr, row.bot, row.error);
        fragment.append(tr);
      }
      if (!filtered.length) {
        const tr = element("tr");
        tr.append(element("td", ready ? "No battles match these filters." : "Loading matching battles…", { colspan: "8", class: "text-ink-3" }));
        fragment.append(tr);
      }
      filteredTable.querySelector("tbody").replaceChildren(fragment);
      text(summary, `${filtered.length} of ${rows.length} battles${ready && !problem ? " · all pages" : " · partial results"}`);
    }

    async function getDocument(path, signal) {
      const request = new AbortController();
      const abort = () => request.abort();
      signal.addEventListener("abort", abort, { once: true });
      const timeout = setTimeout(abort, 20000);
      try {
        if (signal.aborted) throw new DOMException("Stopped", "AbortError");
        const response = await fetch(path, { credentials: "same-origin", signal: request.signal });
        if (!response.ok) throw new Error(`Lookup failed (HTTP ${response.status}).`);
        const url = new URL(response.url);
        if (url.origin !== location.origin || url.pathname === "/login") throw new Error("Sign in and reload to load versions.");
        return new DOMParser().parseFromString(await response.text(), "text/html");
      } finally {
        clearTimeout(timeout);
        signal.removeEventListener("abort", abort);
      }
    }
    async function run() {
      if (controller || disposed) return;
      controller = new AbortController();
      const signal = controller.signal;
      ready = false;
      problem = "";
      retry.hidden = true;
      const collected = [];
      try {
        let next = "/team/battles", teamId;
        const pages = new Set(), ids = new Set();
        while (next) {
          if (pages.has(next) || pages.size >= 200) throw new Error("History lookup incomplete.");
          pages.add(next);
          text(status, `Loading page ${pages.size}…`);
          const doc = await getDocument(next, signal);
          if (disposed) return;
          const page = C.parseListing(doc, new URL(next, location.origin).href);
          for (const row of page.rows) {
            teamId ??= row.teamId;
            if (row.teamId !== teamId) throw new Error("Your team changed. Reload the page.");
            if (ids.has(row.id)) continue;
            ids.add(row.id);
            const source = [...doc.querySelectorAll("tbody tr")].find(tr => tr.querySelector(`a[href="${row.path}"]`));
            row.template = copyRow(source);
            collected.push(row);
          }
          next = page.next;
        }
        rows = collected;
        ++revision;
        cacheKey = teamId ? `bcvf-v1-team-${teamId}` : null;
        if (cacheKey && storage) {
          try { cache = (await storage.get(cacheKey))[cacheKey] || {}; } catch { cache = {}; }
        }
        if (disposed) return;
        for (const row of rows) {
          const bot = cache[row.id];
          if (bot && Number.isSafeInteger(bot.version) && typeof bot.name === "string") row.bot = bot;
        }
        const pending = rows.filter(row => !row.bot);
        let cursor = 0, checked = rows.length - pending.length;
        const update = () => { text(status, `Versions ${checked}/${rows.length}…`); ++revision; refresh(); };
        update();
        await Promise.all([0, 1].map(async () => {
          while (cursor < pending.length && !signal.aborted) {
            const row = pending[cursor++];
            try {
              row.bot = C.parseReplay(await getDocument(row.path, signal), row.teamId);
              if (row.bot) cache[row.id] = row.bot;
              else row.error = "Version unavailable on replay page";
            } catch (error) { row.error = error.message; }
            if (disposed) return;
            ++checked;
            update();
          }
        }));
        if (cacheKey && storage && !disposed) {
          const bounded = Object.fromEntries(rows.slice(0, 5000).filter(row => row.bot).map(row => [row.id, row.bot]));
          try { await storage.set({ [cacheKey]: bounded }); } catch { /* Current results remain usable. */ }
        }
      } catch (error) { problem = error.message; }
      finally {
        controller = null;
        if (!disposed) {
          ready = true;
          const unknown = rows.filter(row => !row.bot).length;
          text(status, problem ? "Versions unavailable" : unknown ? `${unknown} unknown` : "");
          status.title = problem || (unknown ? "Some versions could not be identified. Retry to check again." : "");
          retry.hidden = !problem && !unknown;
          ++revision;
          refresh();
        }
      }
    }
    const onFilter = () => refresh();
    select.addEventListener("change", () => { selected = select.value; refresh(); });
    toolbar.addEventListener("input", onFilter);
    toolbar.addEventListener("change", onFilter);
    retry.addEventListener("click", run);
    refresh();
    void run();
    return { toolbar, controls, refresh, dispose() {
      disposed = true;
      controller?.abort();
      restore();
      document.querySelectorAll('[data-bcvf="version"]').forEach(node => node.remove());
      toolbar.removeEventListener("input", onFilter);
      toolbar.removeEventListener("change", onFilter);
      controls.remove();
    } };
  }
  function sync() {
    const onPage = /^\/team\/battles\/?$/.test(location.pathname);
    if (mounted && (!onPage || !mounted.toolbar.isConnected || !mounted.controls.isConnected)) {
      mounted.dispose();
      mounted = null;
    }
    if (!onPage) return;
    if (mounted) { mounted.refresh(); return; }
    const toolbar = document.querySelector('main input[aria-label="Search opponents"]')?.closest(".ui-toolbar");
    if (toolbar) mounted = mount(toolbar);
  }
  let queued = false;
  new MutationObserver(() => {
    if (queued) return;
    queued = true;
    setTimeout(() => { queued = false; sync(); }, 100);
  }).observe(document.documentElement, { childList: true, subtree: true });
  window.addEventListener("popstate", sync);
  sync();
})();
