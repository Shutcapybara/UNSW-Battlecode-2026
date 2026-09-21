(async () => {
  const C = BattlecodeVersionFilter;
  const parse = text => new DOMParser().parseFromString(text, 'text/html');
  let failed = 0;
  function test(name, fn) {
    const item = document.createElement('li');
    try { fn(); item.textContent = `PASS: ${name}`; }
    catch (error) { ++failed; item.textContent = `FAIL: ${name}: ${error.message}`; }
    document.querySelector('#results').append(item);
  }
  function assert(value) { if (!value) throw new Error('Assertion failed'); }
  const listing = parse(await (await fetch('/team/battles')).text());
  const base = location.origin + '/team/battles';
  test('reads site table columns and follows relative pagination', () => {
    const result = C.parseListing(listing, base);
    assert(result.rows.length === 2 && result.rows[0].teamId === '7');
    assert(result.rows[0].id === '3558' && result.rows[0].kind === 'Unranked');
    assert(result.next === '/team/battles?page=2');
  });
  test('rejects a sign-in page instead of claiming zero battles', () => {
    let thrown = false;
    try { C.parseListing(parse('<h1>Sign in</h1>'), base); } catch { thrown = true; }
    assert(thrown);
  });
  test('distinguishes an empty history from an unsupported layout', () => {
    assert(C.parseListing(parse('<main><h1>Your battles</h1><p>0 battles</p></main>'), base).rows.length === 0);
    let thrown = false;
    try { C.parseListing(parse('<main><h1>Your battles</h1></main>'), base); } catch { thrown = true; }
    assert(thrown);
  });
  test('reads your exact bot label, scoped to the expected team', () => {
    const doc = parse('<main><p class="ui-muted">Your bot: v5 · test &amp; more</p><a href="/teams/7">Our team</a></main>');
    assert(C.parseReplay(doc, '7').name === 'test & more');
    assert(C.parseReplay(doc, '99') === null);
  });
  test('does not mistake scripts or an opponent label for your bot', () => {
    const doc = parse('<main><a href="/teams/7">Team</a><p>Opponent bot: v9 · nope</p><script>"Your bot: v2 · nope"<\/script></main>');
    assert(C.parseReplay(doc, '7') === null);
  });
  document.title = failed ? `${failed} tests failed` : 'All 5 DOM tests passed';
})();
