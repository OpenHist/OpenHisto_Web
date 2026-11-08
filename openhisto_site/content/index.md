# User guide

OpenHisto provides modules for computational pathology: slide acquisition,
patch preparation, stain normalization, feature extraction, semantic segmentation,
vision-language descriptions, classification and risk/survival modeling. The
modules retain explicit source identities and geometry when passing data between
analysis stages.

| Start here | What you will do |
|---|---|
| [Install from a checkout](install.md) | Create a Python environment and choose optional backends. |
| [Synthetic archive example](quickstart.md) | Write and inspect a small synthetic patch archive without downloading a model. |
| [Workflow guide](workflows.md) | Prepare images and representations, segment masks, generate descriptions, and build classification or risk/survival models. |
| [Package reference](reference.md) | Look up detailed package guides, public modules and upstream resources. |

The core package uses Python 3.12 or newer. Optional dependencies are organized
by workflow; some vision-language backends use separate interpreters. See
[installation](install.md) before combining environments.

Current visualization outputs include segmentation overlays and
QuPath-compatible prediction exports. A dedicated workflow for inspecting
slides, patches and model outputs is planned; that integration is not yet
available.

The examples name inputs and outputs explicitly. Start with the offline
quickstart, then provide your slide files, references and selected model assets
for an analysis. The documentation distinguishes catalogue inspection, synthetic
correctness tests, real checkpoint inference and scientific comparisons.
