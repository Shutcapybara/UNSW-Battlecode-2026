# hunter-v18-self-trap-lookahead

C++ fork of `hunter-v17-portal-first-traps`. V18 checks six moves ahead before
following a growth route, rejecting routes that end in a short pocket enclosed
by the dragon's own body. Its survival fallback prefers moves with longer safe
continuations.

Build and run from the repository root:

```sh
.venv/bin/unswbc run maps/help.map bots/hunter-v18-self-trap-lookahead bots/hunter-v16-boost-traps
```
