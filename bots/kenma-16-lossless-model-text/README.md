# Kenma16 — lossless model source text

Parent: kenma-08-lossless-direction, strategy equivalent to03. Store the same32-bit node words as four byte planes in base64 C++ string literals. Decode only each visited word during inference; no whole-model startup decoding, model retraining, quantization or policy change. All thresholds and leaf bits remain exact. The source generator reconstructs every word.

Purpose: recover archive space for the combined encoder/HB direction prior while preserving the existing model needed to provide its HB probability inputs. This is a storage control, not a strength claim. Native node/probability parity and exact-source sandbox turn-cost checks are required before adoption. No reserved seeds or new maps.

Status: verified lossless storage control; not a new strength result. Reproduce with tools/kenma/pack_direction_text.py.

All824,580 decoded C++ nodes match08;21,024 native probability vectors are bit-identical, including1,024 synthetic cases with NaNs. Four sandbox games (Schooltime/UNSW, both seats,seed1) pass: max12,958,553 points, first-turn max12,238,377, zero errors, source zip2,950,863 bytes. Every outcome, round count, length, death record and noncompute gameplay statistic matches08. Runtime e4590915c3ef49df22635a8dde10e45adb711bea3bcabd39d360a3434b6608fa. Evidence main build/kenma/lossless-model-text/report.json and deploy/kenma-16-lossless-model-text/{summary,parent-game-parity}.json.
