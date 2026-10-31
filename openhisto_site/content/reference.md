# Reference and sources

We maintain the [complete package reference](../reference/index.md) for module
guides, configuration fields, command lines and source-level contracts. Our
short guides provide a starting workflow; the reference covers each backend's
options and limits.

## Public modules

| Module | Main entry points |
|---|---|
| `openhisto.default_datasets` | `discover`, `download`, `import_local`, `verify`, `build_manifest` |
| `openhisto.patch_extraction` | `ExtractionConfig`, `extract_grid`, `extract_mask_centered`, `PatchReader`, `PatchArchiveWriter` |
| `openhisto.stain_transfer` | `DomainSpec`, `TransferConfig`, `create_normalizer`, `normalize` |
| `openhisto.feature_encoder` | `SourceSpec`, `EncoderSpec`, `EncodeConfig`, `encode_slide`, `FeatureReader` |
| `openhisto.segmentation` | `MaskSpec`, `Sample`, `prepare_dataset`, `prepare_model`, `train`, `predict`, `evaluate` |
| `openhisto.vlas` | `SourceSpec`, `ModelSpec`, `DescribeConfig`, `describe_slide`, `DescriptionReader` |
| `openhisto.mil.models.code_bases` | `create_model`, `list_models`, `model_info` |
| `openhisto.mil.classification` | Neural classification heads and fitted classical classifiers |
| `openhisto.mil.survival` | Cox and discrete-hazard heads, losses and training-time calibration |
| `openhisto.mil.heads` | Head attachment, representation specifications and persistence helpers |

We also provide segmentation overlays and prediction exports for visualization.
Our planned dedicated visualization integration is not yet a public workflow.
See [workflows](workflows.md#visualization) for the current boundary and
[research and applications](../research.md) for our work using OpenHisto.

## Official resources

- [GDC API documentation](https://docs.gdc.cancer.gov/API/Users_Guide/Search_and_Retrieval/) explains file/case discovery.
- [TCGA PanCanAtlas](https://gdc.cancer.gov/about-data/publications/pancanatlas) provides the curated clinical resource used by the benchmark.
- [PanNuke](https://warwick.ac.uk/fac/cross_fac/tia/data/pannuke/) provides official folds, citations and dataset terms; its [metric code](https://github.com/TissueImageAnalytics/PanNuke-metrics) defines the native evaluation representation.
- [AnnData](https://anndata.readthedocs.io/en/stable/) documents the annotated matrix format underlying feature stores.
- [Phikon](https://huggingface.co/owkin/phikon) and [Phikon-v2](https://huggingface.co/owkin/phikon-v2) document their source checkpoints, representation and model-specific terms.
- [OpenSlide](https://openslide.org/api/python/#installing) documents native slide-reading installation.
- [PyData Sphinx Theme](https://pydata-sphinx-theme.readthedocs.io/en/stable/) documents the theme we use for this documentation.

We checked these external references on 30 October 2026. Dataset/model terms
belong to their respective sources. Our original code uses MIT; vendored and
adapted implementations retain their own notices. Public availability of a
checkpoint does not replace its model terms or gated-access approval.
