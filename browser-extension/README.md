# Battlecode Bot Version Filter

A Chrome / Firefox extension for <https://game.battlecode.au/team/battles>.
It adds an **Our bot version** dropdown and a bot-version column, using the exact
`Your bot: vN · name` label on each replay page. It does not infer versions from
upload times, so switching back to an older submission is handled correctly.

## Install in Chrome

1. Open `chrome://extensions` and enable **Developer mode**.
2. Click **Load unpacked** and select this `browser-extension` directory (the
   directory containing `manifest.json`). If using the ZIP, extract it first.
3. Reload the Battlecode battles page.

See [Chrome's official instructions](https://developer.chrome.com/docs/extensions/get-started/tutorial/hello-world#load-unpacked).

## Install in Firefox

1. Open `about:debugging#/runtime/this-firefox`.
2. Click **Load Temporary Add-on…** and select this directory's `manifest.json`.
3. Reload the Battlecode battles page. Allow access to game.battlecode.au if
   Firefox asks for the site's permission.

This development install lasts until Firefox restarts. A permanent install in
standard Firefox requires signing through Mozilla; this package is unsigned.
Firefox 140 or newer is required by this manifest.
See [Mozilla's temporary installation instructions](https://www.extensionworkshop.com/documentation/develop/temporary-installation-in-firefox/).

## Use

Versions load automatically when you open **Your battles**. The extension adds a
**Version** column after Type and a compact **All versions** dropdown beside the
website's existing opponent and ranked/unranked controls. It uses the website's
own table and control styles; there is no separate panel.

- **All versions** keeps the original battle list and pagination.
- Selecting a version shows matching battles across all history pages, using the
  same table styling and the existing opponent/ranked/unranked controls.
- Hover over `v5`, for example, to see the full submission name.
- `…` means a lookup is pending; `—` means the version is unavailable.
- **Unknown** shows battles whose version could not be identified.
- **Retry** appears only when a lookup fails or leaves unknown versions.
- Return to **All versions** to restore the native paginated list.

The first scan may take a minute or two. A small progress label appears beside
the dropdown while it runs. Successful lookups are cached. Reload the battles
page to include newly completed battles. Leaving the page cancels active lookups.

To update an existing unpacked install, reload the extension on your browser's
extensions/debugging page, then reload the Battlecode page. If you installed an
extracted ZIP, replace its contents with the updated ZIP first.

## Data and permissions

Only game.battlecode.au pages are accessible. The content script is registered for
the whole site so it also works when navigating to Your battles without a full
reload, but the interface only mounts on `/team/battles`.

The extension sends ordinary, read-only page requests to Battlecode using your
existing signed-in session. It does not read or store your password or cookies,
upload bots, change the active submission, or download replay files. There is no
analytics or third-party service. Successful battle ID → version/name lookups are
stored in extension-local storage, separated by team ID, capped at 5,000 entries
per team. Removing the extension removes its cache.

Pagination is capped at 200 pages. Missing labels, changed layouts, and failures
are reported rather than guessed. Battle history may change during a scan;
refresh to include newly completed battles.

## Verification and limitations

The signed-in site's table, pagination, and exact replay bot label were inspected
on 21 September 2026. Node tests and browser DOM tests pass. Browser fixture checks
cover automatic version annotations, native pagination, combined filters across
pages, unknown versions, and restoring the original table. The original parser
tests also cover malformed layouts and missing version labels.

The package has **not yet been installed and tested against the authenticated
site in Chrome or Firefox**. Live operation depends on the site returning the
inspected table and bot label in its fetched HTML. If the server omits those
labels or its markup changes, the extension reports unknown versions or a layout
error instead of attributing battles to the wrong bot.

No build tools or downloaded dependencies are required. From the repository root:

```sh
node --test browser-extension/tests/core.test.cjs
python3 browser-extension/tests/server.py
```

Open `http://127.0.0.1:8765/tests/dom.html` for DOM parser tests or
`http://127.0.0.1:8765/team/battles` for the interactive fixture. The fixture's
scenario links exercise errors and cancellation. Test files are excluded from
the distributable ZIP.
