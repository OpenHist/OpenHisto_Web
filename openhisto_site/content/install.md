# Installation

We currently document installation from a source checkout. Use your existing
OpenHisto checkout; the commands below install that source tree in editable mode.

## Create the main environment

From the repository root containing `pyproject.toml`:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[default-datasets,patch-extraction-opencv,stain-transfer]"
```

This selection supports public dataset acquisition, patch extraction and
Reinhard/histogram normalization. Our main package requires **Python 3.12+**.
Foundation-model inference is a separate step with its own selected backend.

## Choose additional workflows

Run the relevant installation command from the same checkout, or create a
separate environment for a larger backend.

| Work | Editable installation extra |
|---|---|
| Acquisition plans and native slide transfers | `.[default-datasets]` |
| Patch extraction in a fresh environment | `.[patch-extraction-opencv]` |
| Extraction with an existing compatible `cv2` | `.[patch-extraction]` |
| Reinhard and histogram normalization | `.[stain-transfer]` |
| Vahadane and Macenko, with SPAMS | `.[stain-transfer-spams]` |
| CycleGAN and Pix2Pix | `.[stain-transfer-gan]` |
| Local patch embedding models | `.[feature-encoder-local]` |
| Gemini / Cohere / AWS embeddings | `.[feature-encoder-google]`, `.[feature-encoder-cohere]`, `.[feature-encoder-aws]` |
| Segmentation data and exports | `.[segmentation]` |
| Segmentation model backends | `.[segmentation-torch]`, `.[segmentation-transformers]`, `.[segmentation-segdiff]` |
| VLA coordinator and result readers | `.[vlas]` |
| All MIL backbone families | `.[mil-backbones]` |
| Classical slide-vector classifiers | `.[mil-classical]`, or a selected boosting extra |

For example:

```bash
python -m pip install -e ".[feature-encoder-local,mil-backbones]"
```

The extraction extra includes OpenSlide bindings and `openslide-bin`. A managed
system OpenSlide installation is another supported route; see the
[OpenSlide installation guide](https://openslide.org/api/python/#installing).
Use one compatible OpenCV distribution in an environment. The base extraction
extra lets an existing `cv2` installation be reused.

We test MIL and stain-transfer GAN workflows on the Torch 2.6 / torchvision
0.21 compatibility line. We record exact reference environments in the MIL
`requirements-tested.lock.txt` files. A GPU environment still needs a
Torch/torchvision build compatible with its driver and runtime.

## Isolated backends

We integrate SAM2 through a separate pinned installation of its official source,
alongside the SAM2 extra. Follow the full segmentation guide in our
[package reference](reference.md) to install the complete runtime.

Vision-language models run in their own environments. The coordinator uses
Python 3.12+, while legacy worker requirements may specify Python 3.10. PathGen
and Quilt have incompatible native `llava` environments, so install the selected
worker's `requirements-*.txt` separately. Our PA-LLaVA integration is experimental
and uses converted stage-2 checkpoints; we plan further validation with real model
artifacts on the target GPU. PathChat+ is not currently available in our
integration. We plan to support it when we can integrate an authorized complete
checkpoint and its matching runtime. See the
[VLA workflow](workflows.md#patch-descriptions).

## Verify the installation

These inspection commands do not run image inference:

```bash
python -m openhisto.patch_extraction --help
python -m openhisto.feature_encoder models
python -m openhisto.segmentation models
python -m openhisto.vlas models
python -m openhisto.mil.models.code_bases list
```

Run commands for the modules whose extras you installed. `prepare`, encoding,
description generation and selected segmentation preparation may download or
load models; catalogue commands are the place to inspect requirements first.

Next, [try the offline quickstart](quickstart.md) or [choose a workflow](workflows.md).
