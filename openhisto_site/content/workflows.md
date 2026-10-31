# Workflows

We provide modules for image preparation, representation learning, segmentation,
vision-language descriptions and slide-level classification or risk/survival
modeling. Use them independently or connect them with explicit manifests. Keep
stable slide/source IDs, extraction geometry and cohort split information when
joining patch archives, feature stores and description records.

## Dataset acquisition

Our acquisition API separates catalogue discovery from image transfer. The example
below queries public GDC metadata for at most one matching slide and saves the
plan; it does not download the slide:

```python
from openhisto.default_datasets import discover

plan = discover("TCGA", {"projects": ["TCGA-KIRC"], "limit": 1})
plan.save("tcga-plan.json")
print(plan.expected_bytes, plan.unknown_size_count)
```

After reviewing the selection, native images can be transferred and checked:

```bash
python -m openhisto.default_datasets download tcga-plan.json --root data/tcga
python -m openhisto.default_datasets verify --root data/tcga
```

TCGA uses explicit project/case/file IDs. CAMELYON16 supports public TIFFs and
related annotation assets. KPMP uses an explicit Atlas export. BRACS registers
approved local SVS files with supplied metadata. Local import preserves slides
in place. Source metadata, conflicts, missingness and existing provider splits
are retained; acquisition does not construct survival targets. The
[GDC API guide](https://docs.gdc.cancer.gov/API/Users_Guide/Search_and_Retrieval/)
describes the underlying file/case queries.

## Patch extraction

`extract_grid` and `extract_mask_centered` write one indexed HDF5 archive per
slide. See the [quickstart](quickstart.md) for grid extraction. A binary selection
mask uses an explicit coordinate transform:

```python
from openhisto.patch_extraction import ExtractionConfig, extract_mask_centered

summary = extract_mask_centered(
    "input.svs", "binary-mask.tif", "objects.h5",
    ExtractionConfig(patch_size=512, target_mag=20),
    mask_downsample=(8, 8),
    mask_origin=(0, 0),
)
```

Mask scale is level-0 pixels per mask pixel, in X/Y order. Masks may be boolean,
0/1 or 0/255. Mask-centered extraction selects RGB patches; paired training masks
must be sampled separately at the recorded geometry. `PatchReader` exposes
original index, level-0 origin/footprint and output-pixel valid bounds. Extraction
has no ROI, `max_patches` or resume argument; plan a stride/selection explicitly.

## Stain normalization

Select a method and a destination reference. This example normalizes an existing
archive with Reinhard, retaining patch geometry:

```python
from openhisto.stain_transfer import DomainSpec, TransferConfig, normalize

report = normalize(
    "slide-patches.h5", "slide-reinhard.h5",
    DomainSpec(method="reinhard", references=("reference.png",)),
    TransferConfig(seed=1729),
)
print(report.to_dict())
```

The module also accepts images, folders and CSV/JSONL manifests. Histogram
matching is available in the classical environment; Vahadane/Macenko need SPAMS.
For CycleGAN/Pix2Pix, use an explicit generator checkpoint or train a generator
with our training API. Provide a reference or checkpoint for the appearance you
want to produce. Give each derived
appearance its own identity and retain its parent. Fit references on the training
partition when conducting a held-out comparison.

## Feature encoding

`encode_slide` accepts patch archives and explicit image manifests. It writes
one standard AnnData `.h5ad` per slide, with separate model/magnification runs.
This selected public-model example can download Phikon-v2 weights and performs
CPU inference when run:

```python
from openhisto.feature_encoder import EncodeConfig, SourceSpec, encode_slide

report = encode_slide(
    inputs=[SourceSpec("slide-patches.h5", source_id="grid-20x")],
    output="slide-features.h5ad",
    models=["phikon_v2"],
    config=EncodeConfig(
        slide_id="slide-a", device="cpu", precision="float32", batch_size=8,
        prompt_credentials=False,
    ),
)
print(report.to_dict())
```

Inspect the store without model inference:

```python
from openhisto.feature_encoder import FeatureReader

with FeatureReader("slide-features.h5ad") as reader:
    print(reader.list_runs())
    vectors = reader.features("phikon_v2", mag=20)
    print(vectors.shape)
```

Compatible reruns reuse completed vectors. Optional metadata can be corrected
with `metadata_policy="update"`; content hashes and geometry stay immutable.
Updates may need space for a published-file copy plus `.partial.h5ad` staging.
Use `run_key` if a model/magnification has multiple configurations. See
[AnnData's documentation](https://anndata.readthedocs.io/en/stable/) for the
underlying annotated matrix format.

Phikon and Phikon-v2 have public weights with model-specific terms. UNI and
TITAN/CONCH v1.5 require approval. Gemini, Cohere and Nova send selected patches
to external services and may incur charges. Inspect `models MODEL` and choose
access explicitly; this guide's example selects only Phikon-v2. The
[official Phikon-v2 model card](https://huggingface.co/owkin/phikon-v2) documents
its 1,024-dimensional CLS representation and noncommercial model terms.

## Semantic segmentation

Our segmentation API trains, predicts and evaluates semantic class maps. We
provide six backend profiles with their own initialization and input requirements.
Data preparation is separate from downloading/preparing a model:

```python
from openhisto.segmentation import MaskSpec, prepare_dataset

samples = prepare_dataset(
    "training.csv",
    mask_spec=MaskSpec(kind="indexed", ignore_values=[255]),
    num_classes=6,
)
```

Class IDs are contiguous, background is zero, and ignored source values map to
the configured ignore index. Image/mask CSV fields and mask geometry must match
the package's data contract. Use disjoint training/validation/test inputs before
calling `prepare_model`, `train`, `predict` or `evaluate`; selected pretrained
backends may download weights. SAM2 is prompted binary segmentation, not a
six-class replacement. Our instance-segmentation namespace is reserved; the
implemented training workflow targets semantic masks. See our [reference](reference.md) for mask
formats, training jobs, prediction exports and backend differences.

## Patch descriptions

`openhisto.vlas` reads the same patch archives or manifests as feature encoding.
Catalogue inspection is a useful first step:

```bash
python -m openhisto.vlas models
python -m openhisto.vlas models patho_r1_7b
```

Use `describe_slide` or `describe --job` after configuring the selected worker's
interpreter, checkpoint and prompt. Keep the same `slide_id`, `source_id` and
patch sources as feature encoding; description generation does not run an
embedding model. Native environments and model terms differ. Our PA-LLaVA adapter
is experimental and uses converted stage-2 artifacts; we plan real-checkpoint GPU
validation. PathChat+ is not currently available in our integration. Our planned
support depends on integrating an authorized complete checkpoint and its matching
implementation. We retain generated descriptions as model outputs, separately
from annotation-derived labels and pathologist assessment.

## Multiple-instance learning

Our common MIL API exposes 34 model profiles on CPU float32. Read a selected
feature run, then pass its patch vectors explicitly:

```python
import torch
from openhisto.feature_encoder import FeatureReader
from openhisto.mil.models.code_bases import create_model

with FeatureReader("slide-features.h5ad") as reader:
    vectors = reader.features("phikon_v2", mag=20)

model = create_model("abmil", input_dim=vectors.shape[1], num_classes=2)
model.eval()
with torch.no_grad():
    output = model(torch.from_numpy(vectors).float())
print(output.logits.shape)
```

This constructs an untrained prediction component. Train it for your task before
interpreting its predictions. Graph and hierarchy profiles need their native geometry
and relationships. Generic feature bags cannot silently stand in for those
inputs.

## Classification and risk/survival modeling

We expose neural linear, MLP and Bayesian heads through
`openhisto.mil.classification`, alongside classical classifiers for frozen
slide-level vectors. Use `openhisto.mil.heads` to attach a task head, select the
declared representation boundary and preserve native model outputs and auxiliary
objectives. The complete head guide in our [reference](reference.md) covers
training, calibration, persistence and label ordering.

Our survival API provides Cox and discrete-hazard heads through
`openhisto.mil.survival`. Risk outputs and calibrated survival curves have
different meanings: Cox curves require a fitted training baseline, while
discrete hazards require a fitted training time grid. Keep event/censoring
definitions and time units explicit. We provide these components; cohort
partitioning, training and scientific model selection must follow your study
protocol.

## Visualization

We currently provide segmentation label/probability exports, overlays and
QuPath-compatible semantic polygons. These exports support inspection of model
predictions with their recorded geometry; they are not an instance-segmentation
training workflow.

We plan a dedicated visualization workflow for linked slide, patch and
model-output inspection. That broader integration is not yet available. Our
[research and applications](../research.md) page describes our work with these
components and the evidence available for it.
