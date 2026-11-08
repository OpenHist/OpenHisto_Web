# Visualization

Current visualization support consists of segmentation outputs and spatially
aligned exports. A broader workflow for inspecting whole-slide images,
predictions and model attention is planned.

## Available visual outputs

The segmentation workflow exports color-coded semantic masks, RGB image overlays,
GeoJSON polygons and QuPath-compatible annotations. These outputs connect model
predictions with the tissue and coordinates used in the analysis.

| Output | Purpose |
|---|---|
| Palette image | Inspect class regions with a consistent color map. |
| RGB overlay | View a predicted mask together with its original image. |
| GeoJSON / QuPath | Inspect spatial annotations in compatible analysis tools. |
| Label and score arrays | Preserve numeric predictions for further analysis and plotting. |

With a trained segmentation bundle and an image manifest, the following example
exports visualization files alongside numeric labels:

```python
from openhisto.segmentation import export_prediction, predict

for prediction in predict("segmentation-run/best", "images.csv"):
    export_prediction(
        prediction,
        "visualizations",
        formats=("labels", "palette", "overlay", "geojson", "qupath"),
    )
```

The image manifest follows the [segmentation data format](../reference/segmentation.md).
Overlays use the native RGB image. Polygon coordinates use level-zero geometry
when it is present, or image-pixel coordinates otherwise. Valid bounds exclude
padded regions from foreground visualizations.

## Model attention

Some MIL backbones expose attention tensors in their native outputs. These
outputs are retained for model-specific analysis; their shape and interpretation
depend on the selected backbone. See the [MIL reference](../reference/mil.md).

## Planned visualization workflow

An integrated whole-slide viewer and attention-heatmap workflow is planned for a
future release. Current segmentation exports can be used with
external viewers such as QuPath.
