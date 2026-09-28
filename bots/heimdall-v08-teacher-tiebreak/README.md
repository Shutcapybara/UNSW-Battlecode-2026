# Heimdall v08 — Loki teacher tie-break

V08 starts from v05, currently the best balanced core screen. It adds Loki's
trained action scorer at quarter scale. The model only reranks actions already
produced by Heimdall; its optimized sparse inference skips candidates that
cannot overtake the base leader. All sonar and bed-timing behavior remains
from v05.
