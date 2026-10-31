# Visualization

We support visual inspection through segmentation outputs and spatially aligned
exports. We are also developing the broader visualization workflow around
whole-slide images, predictions and model attention.

## Available visual outputs

Our segmentation workflow exports color-coded semantic masks, RGB image overlays,
GeoJSON polygons and QuPath-compatible annotations. These outputs connect model
predictions with the tissue and coordinates used in the analysis.

| Output | How we use it |
|---|---|
| Palette image | Inspect class regions with a consistent color map. |
| RGB overlay | View a predicted mask together with its original image. |
| GeoJSON / QuPath | Inspect spatial annotations in compatible analysis tools. |
| Label and score arrays | Preserve numeric predictions for further analysis and plotting. |

With a trained segmentation bundle and an image manifest, we can export the
visual products alongside numeric labels:

```python
from openhisto.segmentation import export_prediction, predict

for prediction in predict("segmentation-run/best", "images.csv"):
    export_prediction(
        prediction,
        "visualizations",
        formats=("labels", "palette", "overlay", "geojson", "qupath"),
    )
```

The image manifest follows our [segmentation data format](../reference/segmentation.md).
Overlays use the native RGB image. Polygon coordinates use level-zero geometry
when it is present, or image-pixel coordinates otherwise. Valid bounds exclude
padded regions from foreground visualizations.

## Model attention

Some MIL backbones expose attention tensors in their native outputs. We retain
those outputs for model-specific analysis; their shape and interpretation depend
on the selected backbone. See the [MIL reference](../reference/mil.md).

## Planned visualization workflow

We plan to add a unified whole-slide viewer and attention-heatmap workflow in a
future release. Our current segmentation exports can already be used with
external viewers such as QuPath.
