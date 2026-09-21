const { test } = require('node:test');
const assert = require('node:assert/strict');
const { parseVersion, localPath, matches } = require('../core.js');

test('reads the exact replay version, including names containing punctuation', () => {
  assert.deepEqual(parseVersion(' Your bot: v5 · bot · latest\n'), { version: 5, name: 'bot · latest' });
  assert.equal(parseVersion('Opponent bot: v5 · latest'), null);
  assert.equal(parseVersion('Uploaded v5 at 15:52'), null);
  assert.equal(parseVersion('Your bot: v5'), null);
});

test('only accepts same-origin numeric battle links', () => {
  const base = 'https://game.battlecode.au/team/battles';
  const pattern = /^\/battles\/\d+$/;
  assert.equal(localPath('/battles/3558', base, pattern), '/battles/3558');
  assert.equal(localPath('https://elsewhere.example/battles/3558', base, pattern), null);
  assert.equal(localPath('javascript:alert(1)', base, pattern), null);
  assert.equal(localPath('/battles/not-an-id', base, pattern), null);
});

test('combines version, opponent and battle type without guessing unknowns', () => {
  const row = { bot: { version: 5 }, opponent: 'Heartbreaker 1542', kind: 'Ranked' };
  assert.equal(matches(row, { version: '5', query: ' HEART ' }), true);
  assert.equal(matches(row, { version: '4' }), false);
  assert.equal(matches(row, { ranked: false }), false);
  assert.equal(matches(row, { version: 'unknown' }), false);
  assert.equal(matches({ ...row, bot: null }, { version: '5' }), false);
  assert.equal(matches({ ...row, bot: null }, { version: 'unknown' }), true);
  assert.equal(matches({ ...row, kind: 'Unranked' }, { unranked: false }), false);
});
