# User guide

We develop OpenHisto for computational pathology workflows: slide acquisition,
patch preparation, stain normalization, feature extraction, semantic segmentation,
vision-language descriptions, classification and risk/survival modeling. Our
modules share explicit source identities and geometry so you can connect the
steps your analysis needs.

| Start here | What you will do |
|---|---|
| [Install from a checkout](install.md) | Create a Python environment and choose optional backends. |
| [Try the quickstart](quickstart.md) | Write and inspect a small synthetic patch archive without downloading a model. |
| [Build a workflow](workflows.md) | Prepare images and representations, segment masks, generate descriptions, and build classification or risk/survival models. |
| [Find the reference](reference.md) | Look up detailed package guides, public modules and upstream resources. |

Our core package uses Python 3.12 or newer. We organize optional dependencies
by workflow; some vision-language backends use separate interpreters. See
[installation](install.md) before combining environments.

For visualization, we currently provide segmentation overlays and
QuPath-compatible prediction exports. We plan a dedicated workflow for inspecting
slides, patches and model outputs; that integration is not yet available.

Our examples name inputs and outputs explicitly. Start with the offline
quickstart, then provide your slide files, references and selected model assets
for a real workflow. We distinguish catalogue inspection, synthetic correctness
tests, real checkpoint inference and scientific comparisons in our evidence.
