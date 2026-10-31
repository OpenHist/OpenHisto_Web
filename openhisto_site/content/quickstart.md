# Quickstart

Start with a synthetic patch archive, then move to a slide you have selected.
The first example needs no patient files, network request or model weights.
Install the extraction environment described in [installation](install.md).

## Write and inspect an archive

Run this in a working directory where `demo/patches.h5` does not already exist:

```python
from pathlib import Path
import numpy as np
from openhisto.patch_extraction import PatchArchiveWriter, PatchReader

Path("demo").mkdir(exist_ok=True)
rng = np.random.default_rng(1729)

with PatchArchiveWriter(
    "demo/patches.h5",
    patch_size=64,
    metadata={"source_mag": 40, "target_mag": 20},
) as writer:
    for index in range(4):
        rgb = rng.integers(30, 230, (64, 64, 3), dtype=np.uint8)
        writer.append(
            rgb,
            (index * 128, 0),  # level-0 origin, x and y
            (128, 128),        # level-0 footprint, width and height
            (0, 0, 64, 64),    # valid output-pixel bounds
        )

with PatchReader("demo/patches.h5") as reader:
    assert len(reader) == 4
    print(reader.get_coordinates())
    print(reader[0].image.shape)  # (64, 64, 3)
    print(reader[0].footprint_level0)
```

The images are generated values, not tissue or a model-quality test. Coordinates
describe a known synthetic 2:1 source-to-output scale. Existing outputs are
refused by default; use another output path for another example.

## Extract a real slide

Replace `input.svs` with a slide you can access. This operation reads that file
and writes an indexed HDF5 archive:

```python
from openhisto.patch_extraction import ExtractionConfig, extract_grid

summary = extract_grid(
    "input.svs",
    "slide-patches.h5",
    ExtractionConfig(patch_size=512, target_mag=20, foreground_method="HSV"),
)
print(summary.to_dict())
```

Source magnification comes from objective-power metadata. If it is absent,
supply `source_mag` only when you know the source objective. The target cannot
exceed the source magnification. PNG is the default; its lossless guarantee
applies to the extracted RGB after resampling.

## Choose the next output

| You need | Continue with |
|---|---|
| A slide manifest and original metadata | [Dataset acquisition](workflows.md#dataset-acquisition) |
| A reference appearance | [Stain normalization](workflows.md#stain-normalization) |
| Patch vectors in `.h5ad` | [Feature encoding](workflows.md#feature-encoding) |
| Aligned semantic labels | [Semantic segmentation](workflows.md#semantic-segmentation) |
| Prompted patch text | [Patch descriptions](workflows.md#patch-descriptions) |
| A slide-level prediction component | [Multiple-instance learning](workflows.md#multiple-instance-learning) |

Carry the same slide/source identities and geometry between stages. Patch
archives hold technical geometry; clinical targets and cohort splits belong in
external manifests. The [workflow guide](workflows.md) explains those boundaries.
