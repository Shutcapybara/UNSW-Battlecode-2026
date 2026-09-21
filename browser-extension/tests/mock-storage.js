// Only loaded by the localhost fixture, never by the extension manifest.
if (new URLSearchParams(location.search).has('clear-cache')) localStorage.clear();
globalThis.chrome = { storage: { local: {
  async get(key) { return { [key]: JSON.parse(localStorage.getItem(key) || 'null') }; },
  async set(items) { for (const [key, value] of Object.entries(items)) localStorage.setItem(key, JSON.stringify(value)); }
} } };
