# hunter-v19-safe-growth-lookahead

C++ fork of `hunter-v18-self-trap-lookahead`. V19 checks safe continuation
depth from each possible first step before choosing a pearl route, so an unsafe
route to one pearl does not hide safe alternatives. Its survival fallback
prefers moves with more safe continuations when their depths are equal.

Build and run from the repository root:

```sh
.venv/bin/unswbc run maps/help.map bots/hunter-v19-safe-growth-lookahead bots/hunter-v16-boost-traps
```
