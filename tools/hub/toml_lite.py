"""Minimal TOML reader used only when `tomllib` is unavailable (Python < 3.11).

Supports the subset the hub writes and reads: comments, `[table]` and `[a.b]` headers, `key = value`
with strings (basic, with escapes), integers (with underscores), floats, booleans, arrays (nested,
multi-line) and inline tables. Anything else raises ValueError.
"""
import re

try:  # pragma: no cover - exercised on 3.11+
    import tomllib as _tomllib
except ModuleNotFoundError:  # pragma: no cover
    _tomllib = None


def loads(text):
    if _tomllib is not None:
        return _tomllib.loads(text)
    return _Parser(text).parse()


class _Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def parse(self):
        root = {}
        current = root
        while True:
            self._skip_ws_and_comments()
            if self.pos >= len(self.text):
                return root
            ch = self.text[self.pos]
            if ch == '[':
                self.pos += 1
                name = self._read_until(']').strip()
                self.pos += 1
                current = root
                for part in name.split('.'):
                    current = current.setdefault(part.strip().strip('"'), {})
                continue
            key = self._read_key()
            self._skip_inline_ws()
            if self.text[self.pos] != '=':
                raise ValueError(f'expected = after key {key!r}')
            self.pos += 1
            self._skip_inline_ws()
            current[key] = self._read_value()

    def _read_until(self, stop):
        end = self.text.index(stop, self.pos)
        value = self.text[self.pos:end]
        self.pos = end
        return value

    def _read_key(self):
        if self.text[self.pos] == '"':
            self.pos += 1
            key = self._read_until('"')
            self.pos += 1
            return key
        m = re.compile(r'[A-Za-z0-9_-]+').match(self.text, self.pos)
        if not m:
            raise ValueError(f'bad key at {self.pos}')
        self.pos = m.end()
        return m.group(0)

    def _skip_inline_ws(self):
        while self.pos < len(self.text) and self.text[self.pos] in ' \t':
            self.pos += 1

    def _skip_ws_and_comments(self):
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch in ' \t\r\n':
                self.pos += 1
            elif ch == '#':
                while self.pos < len(self.text) and self.text[self.pos] != '\n':
                    self.pos += 1
            else:
                return

    def _read_value(self):
        ch = self.text[self.pos]
        if ch == '"':
            return self._read_string()
        if ch == "'":
            self.pos += 1
            value = self._read_until("'")
            self.pos += 1
            return value
        if ch == '[':
            return self._read_array()
        if ch == '{':
            return self._read_inline_table()
        m = re.compile(r'[A-Za-z0-9_+\-.:]+').match(self.text, self.pos)
        if not m:
            raise ValueError(f'bad value at {self.pos}')
        self.pos = m.end()
        token = m.group(0)
        if token == 'true':
            return True
        if token == 'false':
            return False
        if re.fullmatch(r'[+-]?[0-9_]+', token):
            return int(token.replace('_', ''))
        if re.fullmatch(r'[+-]?[0-9_]*\.?[0-9_]+([eE][+-]?[0-9]+)?', token):
            return float(token.replace('_', ''))
        raise ValueError(f'unsupported value {token!r}')

    def _read_string(self):
        self.pos += 1
        out = []
        while True:
            ch = self.text[self.pos]
            if ch == '\\':
                nxt = self.text[self.pos + 1]
                out.append({'n': '\n', 't': '\t', '"': '"', '\\': '\\'}.get(nxt, nxt))
                self.pos += 2
            elif ch == '"':
                self.pos += 1
                return ''.join(out)
            else:
                out.append(ch)
                self.pos += 1

    def _read_array(self):
        self.pos += 1
        items = []
        while True:
            self._skip_ws_and_comments()
            if self.text[self.pos] == ']':
                self.pos += 1
                return items
            items.append(self._read_value())
            self._skip_ws_and_comments()
            if self.text[self.pos] == ',':
                self.pos += 1

    def _read_inline_table(self):
        self.pos += 1
        table = {}
        while True:
            self._skip_inline_ws()
            if self.text[self.pos] == '}':
                self.pos += 1
                return table
            key = self._read_key()
            self._skip_inline_ws()
            assert self.text[self.pos] == '='
            self.pos += 1
            self._skip_inline_ws()
            table[key] = self._read_value()
            self._skip_inline_ws()
            if self.text[self.pos] == ',':
                self.pos += 1
