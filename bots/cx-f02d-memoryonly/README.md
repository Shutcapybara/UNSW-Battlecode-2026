# cx-f00-base — anna-a02-chassis + the ATLAS_ENABLED switch

C1-F's baseline arm. A byte-for-behaviour copy of `bots/anna-a02-chassis` (copy,
never edit) plus the hard atlas switch the out-of-sample rule requires
(`docs/hub/prompts/2026-09-29-C1-out-of-sample-rule.md` rule 2). With
`ATLAS_ENABLED = true` it is golden-identical to the chassis; the `-noatlas`
twin (`cx-f00-base-noatlas`, the same sources with the switch false) is the
atlas-off arm every fix is also measured as. All cx-f fixes are copies of this
directory with their own switch block appended.
