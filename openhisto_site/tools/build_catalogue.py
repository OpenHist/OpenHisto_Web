#!/usr/bin/env python3
"""Build the site catalogue from local package sources, without importing them.

Python's standard library is sufficient. Registry literals are read with AST,
provenance with JSON, and extras with TOML. This command never loads a model,
reads credentials, downloads artifacts, or executes package code.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import inspect
import json
import subprocess
import tomllib
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
EXPECTED = {
    "encoders": 8,
    "mil": 34,
    "segmentation": 6,
    "vla": 5,
    "datasets": 4,
    "normalization": 6,
    "heads": 3,
    "survival": 2,
    "classifiers": 11,
}
REPOSITORY = "https://github.com/OpenHist/OpenHistology_Package"
MIL_NAMES = {
    "abmil": "ABMIL",
    "gated_abmil": "Gated ABMIL",
    "dsmil": "DSMIL",
    "dtfd_mil": "DTFD-MIL",
    "acmil": "ACMIL",
    "asmil": "ASMIL",
    "clam_sb": "CLAM-SB",
    "clam_mb": "CLAM-MB",
    "varpool": "VarPool",
    "panther": "PANTHER",
    "wikg": "WiKG",
    "tad_graph": "TAD-Graph",
    "resgat": "ResGAT",
    "patch_gcn": "Patch-GCN",
    "slidegraph_plus": "SlideGraph+",
    "cs_mil": "CS-MIL",
    "zoommil": "ZoomMIL",
    "hag_mil": "HAG-MIL",
    "gfr_mil": "GFR-MIL",
    "h2_mil": "H²-MIL",
    "hipt": "HIPT",
    "transmil": "TransMIL",
    "ilra": "ILRA",
    "rrt_mil": "RRT-MIL / R²T-MIL",
    "dgr_mil": "DGR-MIL",
    "caprmil": "CAPRMIL",
    "lin_mil": "Lin-MIL",
    "mamba_mil": "MambaMIL",
    "nnmil": "nnMIL",
    "mhim_v1": "MHIM v1",
    "mhim_v2": "MHIM v2",
    "mean_mil": "MeanMIL",
    "max_mil": "MaxMIL",
    "mean_std_mil": "MeanStdMIL",
}
MIL_DESCRIPTIONS = {
    "abmil": "Native attention pooling with an explicit feature-to-500 projection when needed.",
    "gated_abmil": "Native gated attention pooling and classifier with the same feature projection policy as ABMIL.",
    "dsmil": "Dual instance/bag streams; native inference averages their independent sigmoid scores.",
    "dtfd_mil": "Two-tier distillation; pseudo-bag logits and AFS/MaxS/MaxMinS modes remain exposed.",
    "acmil": "Attention branches and native patch masking; branch outputs remain available.",
    "asmil": "Attention model with a frozen anchor and an explicit update_anchor hook.",
    "clam_sb": "Single-branch CLAM with optional labelled instance-level evaluation and loss.",
    "clam_mb": "Multiple-branch CLAM; class-conditioned representations preserve native class order.",
    "varpool": "Native attention mean/variance pooling with configurable variance readout.",
    "panther": "Prototype/EM representation with an added downstream linear classifier; requires training-fitted prototypes.",
    "wikg": "Learns a graph from feature bags; the released network requires no patch coordinates.",
    "tad_graph": "Prepared causal/trivial graphs, normalized edge descriptors and information loss; native survival is optional.",
    "resgat": "Native residual graph-attention computation on a caller-prepared graph.",
    "patch_gcn": "Prepared graph with native discrete-survival hazards; native num_classes denotes time bins.",
    "slidegraph_plus": "Clustered-region graph with released EdgeConv aggregation; GIN is an explicit alternative.",
    "cs_mil": "Corresponding three-scale clusters with native independent sigmoid heads.",
    "zoommil": "Native three-level zoom selection over parent-major multiscale features.",
    "hag_mil": "Three native IAT models and a selection cascade with four children per parent.",
    "gfr_mil": "Corresponding low/high features with native coordinate quantization and auxiliary loss; native survival is optional.",
    "h2_mil": "Native hierarchical pooling over ordered root, coarse and fine graph nodes.",
    "hipt": "Native LGP/GP hierarchy contracts and a separately named no-transformer ablation; generic vectors do not replace DINO.",
    "transmil": "Native transformer MIL computation with a device-local class token.",
    "ilra": "Native low-rank attention model operating on feature bags.",
    "rrt_mil": "Native regional transformer; feature bags support none/peg/ppeg positions and attention/average pooling.",
    "dgr_mil": "Native lesion/center computations and auxiliary outputs remain available.",
    "caprmil": "Native cluster/transformer model with explicit profile options.",
    "lin_mil": "Native linear-attention MIL; optional CUDA attention ablations are outside the CPU profile.",
    "mamba_mil": "Classification profile using differentiable Torch reference convolution/scan and native SR padding/transposition.",
    "nnmil": "Native training sampling and evaluation-window ensemble; returned mean window features support attached heads.",
    "mhim_v1": "MHIM student/EMA teacher with native masking, distillation loss and explicit teacher updates.",
    "mhim_v2": "Second MHIM source track retaining token merging, masking and checkpointed EMA teacher state.",
    "mean_mil": "Featurewise mean pooling with the package's classifier.",
    "max_mil": "Featurewise maximum pooling with the package's classifier.",
    "mean_std_mil": "Concatenated mean and population standard deviation; singleton bags remain finite.",
}
MIL_CONTRACTS = {
    "tad_graph": "PyG Data: x[N,D], long edge_index[2,E], normalized distance/angle edge_attr[E,2] in [0,1]; one graph.",
    "resgat": "PyG Data: x[N,D], long edge_index[2,E]; optional long all-zero batch. Supports [2,0] edges and singleton nodes.",
    "patch_gcn": "PyG Data: x[N,D], long edge_index[2,E]; edge_latent when selected. Supports [2,0] edges and singleton nodes.",
    "slidegraph_plus": "Caller-prepared clustered-region PyG graph with feature-aligned long edges; one graph per call.",
    "h2_mil": "PyG graph plus edge_index_tree_8nb, long node_type 0/1/2, node_tree, normalized x_y_index[N,2]; ordered root/coarse/fine.",
    "cs_mil": "Dictionary: clusters is a list of [P_i,D,3,1] tensors at three corresponding scales; optional mask[1,sum(P_i)].",
    "zoommil": "Dictionary: levels=(low,middle,high), contiguous parent-major ordering with integer child-count ratios.",
    "hag_mil": "Dictionary: levels=(low,middle,high), four contiguous children per parent at both hierarchy levels.",
    "gfr_mil": "Dictionary: features, coords, high_features, high_coords, long region_labels; aligned low/high rows and native 448/3584 coordinates.",
    "hipt": "LGP: raster-ordered native DINO fine features[regions,256,384]; GP: native region features[regions,192]; none ablation: [regions,patches,D].",
    "panther": "Nonempty float32 feature bag[N,D] and finite training-fitted .npy prototype matrix[P,D].",
    "wikg": "Float32 feature bag[N,D], with at least topk instances; no coordinates required by the released network.",
    "dtfd_mil": "Float32 feature bag[N,D], with at least num_groups instances.",
    "clam_sb": "Float32 feature bag[N,D]; instance_eval=True also requires a label and at least k_sample patches.",
    "clam_mb": "Float32 feature bag[N,D]; instance_eval=True also requires a label and at least k_sample patches.",
}


class Sources:
    def __init__(self, package: Path):
        self.package = package
        self.files: dict[str, str] = {}
        self.contents: dict[str, str] = {}
        self.trees: dict[str, ast.Module] = {}

    def read(self, relative: str) -> str:
        if relative in self.contents:
            return self.contents[relative]
        content = (self.package / relative).read_text(encoding="utf-8")
        self.files[relative] = hashlib.sha256(content.encode()).hexdigest()
        self.contents[relative] = content
        return content

    def tree(self, relative: str) -> ast.Module:
        if relative not in self.trees:
            self.trees[relative] = ast.parse(self.read(relative), filename=relative)
        return self.trees[relative]

    def literal(self, relative: str, name: str):
        for node in self.tree(relative).body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == name for target in node.targets
            ):
                return ast.literal_eval(node.value)
        raise ValueError(f"Missing literal {name} in {relative}")

    def descriptors(self, relative: str, positional: tuple[str, ...] = ()):
        output = []
        for node in ast.walk(self.tree(relative)):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "ModelDescriptor"
            ):
                item = {key: ast.literal_eval(value) for key, value in zip(positional, node.args)}
                item.update(
                    {keyword.arg: ast.literal_eval(keyword.value) for keyword in node.keywords}
                )
                output.append(item)
        return output

    def field_default(self, relative: str, class_name: str, field_name: str):
        node = next(
            item for item in self.tree(relative).body if getattr(item, "name", None) == class_name
        )
        field = next(
            item
            for item in node.body
            if isinstance(item, ast.AnnAssign) and item.target.id == field_name
        )
        return ast.literal_eval(field.value)


# Resolve the public lazy wrappers to their implementation signatures. Reading
# these ASTs does not import the corresponding scientific dependencies.
API_TARGETS = {
    "openhisto.mil.models.code_bases.create_model": (
        "mil/models/code_bases/registry.py",
        "create_model",
    ),
    "openhisto.feature_encoder.encode_slide": (
        "feature_encoder/pipeline.py",
        "encode_slide",
    ),
    "openhisto.feature_encoder.EncoderSpec": (
        "feature_encoder/config.py",
        "EncoderSpec",
    ),
    "openhisto.feature_encoder.EncodeConfig": (
        "feature_encoder/config.py",
        "EncodeConfig",
    ),
    "openhisto.feature_encoder.SourceSpec": ("feature_encoder/config.py", "SourceSpec"),
    "openhisto.vlas.describe_slide": ("vlas/pipeline.py", "describe_slide"),
    "openhisto.vlas.model_info": ("vlas/registry.py", "model_info"),
    "openhisto.vlas.ModelSpec": ("vlas/config.py", "ModelSpec"),
    "openhisto.vlas.SourceSpec": ("vlas/config.py", "SourceSpec"),
    "openhisto.vlas.DescribeConfig": ("vlas/config.py", "DescribeConfig"),
    "openhisto.segmentation.ModelConfig": ("segmentation/config.py", "ModelConfig"),
    "openhisto.segmentation.prepare_model": ("segmentation/engine.py", "prepare_model"),
    "openhisto.default_datasets.discover": ("default_datasets/pipeline.py", "discover"),
    "openhisto.default_datasets.download": ("default_datasets/pipeline.py", "download"),
    "openhisto.default_datasets.import_local": (
        "default_datasets/pipeline.py",
        "import_local",
    ),
    "openhisto.stain_transfer.DomainSpec": ("stain_transfer/config.py", "DomainSpec"),
    "openhisto.stain_transfer.TransferConfig": (
        "stain_transfer/config.py",
        "TransferConfig",
    ),
    "openhisto.stain_transfer.normalize": ("stain_transfer/pipeline.py", "normalize"),
    "openhisto.mil.classification.create_neural_head": (
        "mil/classification/neural.py",
        "create_neural_head",
    ),
    "openhisto.mil.classification.create_classifier": (
        "mil/classification/classical.py",
        "create_classifier",
    ),
    "openhisto.mil.heads.attach_head": ("mil/heads/attachment.py", "attach_head"),
    "openhisto.mil.heads.representation_dimension": (
        "mil/heads/bindings.py",
        "representation_dimension",
    ),
    "openhisto.mil.survival.create_survival_head": (
        "mil/survival/__init__.py",
        "create_survival_head",
    ),
}


def signature(sources, relative, symbol):
    nodes = sources.tree("src/openhisto/" + relative).body
    parts = symbol.split(".")
    for part in parts:
        node = next(node for node in nodes if getattr(node, "name", None) == part)
        nodes = getattr(node, "body", [])
    parameters = []
    empty = inspect.Parameter.empty
    if isinstance(node, ast.ClassDef):
        initializer = next(
            (item for item in node.body if getattr(item, "name", None) == "__init__"),
            None,
        )
        if initializer is None:
            for field in node.body:
                if isinstance(field, ast.AnnAssign):
                    parameters.append(
                        inspect.Parameter(
                            field.target.id,
                            inspect.Parameter.POSITIONAL_OR_KEYWORD,
                            default=None if field.value is not None else empty,
                        )
                    )
            return inspect.Signature(parameters)
        node = initializer
    args = node.args
    positional = args.posonlyargs + args.args
    defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)
    for argument, default in zip(positional, defaults):
        if argument.arg == "self":
            continue
        kind = (
            inspect.Parameter.POSITIONAL_ONLY
            if argument in args.posonlyargs
            else inspect.Parameter.POSITIONAL_OR_KEYWORD
        )
        parameters.append(
            inspect.Parameter(argument.arg, kind, default=empty if default is None else None)
        )
    if args.vararg:
        parameters.append(inspect.Parameter(args.vararg.arg, inspect.Parameter.VAR_POSITIONAL))
    for argument, default in zip(args.kwonlyargs, args.kw_defaults):
        parameters.append(
            inspect.Parameter(
                argument.arg,
                inspect.Parameter.KEYWORD_ONLY,
                default=empty if default is None else None,
            )
        )
    if args.kwarg:
        parameters.append(inspect.Parameter(args.kwarg.arg, inspect.Parameter.VAR_KEYWORD))
    return inspect.Signature(parameters)


def validate_example(sources, entry):
    tree = ast.parse(entry["example"], filename=f"{entry['category']}/{entry['id']}.py")
    imports = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                qualified = node.module + "." + alias.name
                if qualified not in API_TARGETS:
                    raise ValueError(f"Unverified example import: {qualified}")
                imports[alias.asname or alias.name] = API_TARGETS[qualified]
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = imports.get(node.func.id) if isinstance(node.func, ast.Name) else None
        if isinstance(node.func, ast.Attribute):
            target = {
                "fit": (
                    "mil/classification/classical.py",
                    "FrozenVectorClassifier.fit",
                ),
                "predict": (
                    "mil/classification/classical.py",
                    "FrozenVectorClassifier.predict",
                ),
                "fit_baseline": ("mil/survival/heads.py", "CoxHead.fit_baseline"),
                "fit_time_grid": (
                    "mil/survival/heads.py",
                    "DiscreteHazardHead.fit_time_grid",
                ),
            }.get(node.func.attr)
        if target:
            signature(sources, *target).bind(
                *[None for _ in node.args],
                **{keyword.arg: None for keyword in node.keywords},
            )


def git_commit(package: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(package), "rev-parse", "HEAD"], text=True
    ).strip()


def make_entry(
    category,
    identifier,
    name,
    family,
    module,
    description,
    contract,
    extra,
    docs,
    **more,
):
    return {
        "id": identifier,
        "name": name,
        "category": category,
        "family": family,
        "module": module,
        "tasks": [],
        "access": "local",
        "access_note": "",
        "dimensions": None,
        "description": description,
        "input_contract": contract,
        "extra": extra,
        "install": f'python -m pip install -e ".[{extra}]"',
        "docs": docs,
        "source": None,
        "example": "",
        **more,
    }


def build(package: Path) -> dict:
    s = Sources(package)
    commit = git_commit(package)
    blob = f"{REPOSITORY}/blob/{commit}/"
    groups = {key: [] for key in EXPECTED}
    mil_root = "src/openhisto/mil/models/code_bases/"
    registry = mil_root + "registry.py"
    for family, profiles in s.literal(registry, "_GROUPS").items():
        for identifier, slug in profiles.items():
            graph = identifier in {
                "tad_graph",
                "resgat",
                "patch_gcn",
                "slidegraph_plus",
                "h2_mil",
            }
            hierarchy = identifier in {
                "cs_mil",
                "zoommil",
                "hag_mil",
                "gfr_mil",
                "hipt",
            }
            variable = (
                "prepared_graph"
                if graph
                else "prepared_hierarchy"
                if hierarchy
                else "patch_features"
            )
            width = 384 if identifier == "hipt" else 768
            classes = 1 if identifier == "cs_mil" else 3
            options = (
                ', prototype_path="training_prototypes.npy"' if identifier == "panther" else ""
            )
            example = (
                "from openhisto.mil.models.code_bases import create_model\n\n"
                f"# Supply {variable} using the documented native input contract.\n"
                f'model = create_model("{identifier}", input_dim={width}, num_classes={classes}, device="cpu"{options})\n'
                f"model.eval()\noutput = model({variable})\n"
            )
            tasks = {
                "patch_gcn": ["discrete_survival"],
                "tad_graph": ["classification", "discrete_survival"],
                "gfr_mil": ["classification", "discrete_survival"],
                "cs_mil": ["independent_sigmoid"],
                "panther": ["representation", "classification_with_adapter_head"],
            }.get(identifier, ["classification"])
            source = json.loads(s.read(mil_root + f"compat/sources/{slug}.json")) if slug else None
            groups["mil"].append(
                make_entry(
                    "mil",
                    identifier,
                    MIL_NAMES[identifier],
                    family,
                    "openhisto.mil.models.code_bases",
                    MIL_DESCRIPTIONS[identifier],
                    MIL_CONTRACTS.get(
                        identifier,
                        "Nonempty float32 feature bag[N,D] or [1,N,D]; native ordering and model-specific minimum sizes apply.",
                    ),
                    "mil" if family == "baselines" else "mil-" + family.replace("_", "-"),
                    blob + mil_root + "README.md",
                    tasks=tasks,
                    source=source["url"] if source else None,
                    source_revision=source["commit"] if source else None,
                    access_note="Vendored source; random initialization unless explicit compatible local weights are supplied. No bundled trained weights.",
                    devices=["cpu"],
                    dtype="float32",
                    input_kind="prepared_graph"
                    if graph
                    else "prepared_hierarchy"
                    if hierarchy
                    else "feature_bag",
                    dimensions={
                        "input": "configurable D",
                        "native_hipt": {"lgp": 384, "gp": 192},
                    }
                    if identifier == "hipt"
                    else {
                        "input": "configurable D",
                        "representation": "resolve with representation_dimension(backbone)",
                    },
                    attached_tasks=[
                        "neural_classification",
                        "frozen_vector_classification",
                        "cox",
                        "discrete_hazard",
                    ],
                    example=example,
                    evidence_sources=[registry, mil_root + "README.md"],
                )
            )

    encoder_registry = "src/openhisto/feature_encoder/registry.py"
    descriptors = s.descriptors(
        encoder_registry,
        ("model_id", "display_name", "provider", "access", "dimension", "model_name"),
    )
    for item in descriptors:
        identifier, provider = item["model_id"], item["provider"]
        extra = {"hf": "local", "google": "google", "cohere": "cohere", "aws": "aws"}[provider]
        preprocessing = item["preprocessing"]
        model_source = (
            "https://huggingface.co/" + item["model_name"]
            if provider == "hf"
            else item.get("license_url")
        )
        groups["encoders"].append(
            make_entry(
                "encoders",
                identifier,
                item["display_name"],
                "pathology_checkpoint" if provider == "hf" else "multimodal_api",
                "openhisto.feature_encoder",
                "Official checkpoint preprocessing and "
                + preprocessing.get("pooling", "one image per embedding")
                + "; one vector per selected patch.",
                "Indexed patch-extraction HDF5 archive or explicit CSV/JSONL RGB patch manifest, with stable source/slide identities and magnification.",
                "feature-encoder-" + extra,
                blob + "src/openhisto/feature_encoder/README.md",
                tasks=["patch_embedding"],
                access=item["access"],
                access_note={
                    "public": "Public checkpoint; an explicit encoding/preparation call may download weights.",
                    "gated": "Approval and matching Hugging Face account authorization are required.",
                    "api": "Provider credentials/entitlement required; selected patches are sent to the provider and requests may incur charges.",
                }[item["access"]],
                dimensions={
                    "default": item["dimension"],
                    "supported": list(item.get("dimensions", (item["dimension"],))),
                    **(
                        {"range": preprocessing["dimension_range"]}
                        if "dimension_range" in preprocessing
                        else {}
                    ),
                },
                provider=provider,
                model_name=item["model_name"],
                source=model_source,
                source_revision=preprocessing.get("default_revision"),
                preprocessing=preprocessing,
                approval_url=item.get("approval_url"),
                license_url=item.get("license_url"),
                example='from openhisto.feature_encoder import EncodeConfig, EncoderSpec, SourceSpec, encode_slide\n\nreport = encode_slide(\n    inputs=[SourceSpec("patches/slide.h5", source_id="grid-20x")],\n    output="features/slide.h5ad",\n    models=[EncoderSpec('
                + repr(identifier)
                + ')],\n    config=EncodeConfig(slide_id="slide-a"),\n)\n',
                evidence_sources=[
                    encoder_registry,
                    "src/openhisto/feature_encoder/README.md",
                ],
            )
        )

    seg_registry = "src/openhisto/segmentation/semantic/registry.py"
    seg_names = {
        "mask2former": "Mask2Former",
        "segformer": "SegFormer",
        "upernet": "UPerNet",
        "deeplabv3": "DeepLabV3",
        "sam2": "SAM 2",
        "segdiff": "SegDiff",
    }
    seg_desc = {
        "mask2former": "Native query classification with matched mask BCE and Dice; exports summed query-class mask scores, not class logits.",
        "segformer": "Pretrained semantic backbone with pixel cross-entropy and a task-specific class head.",
        "upernet": "Random ConvNeXt initialization by default; an explicit model path selects pretrained initialization.",
        "deeplabv3": "torchvision pretrained ResNet50 with a replaced class head and pixel cross-entropy.",
        "sam2": "Official prompt-conditioned image model with binary BCE and Dice; explicit prompts are required at inference.",
        "segdiff": "Random embedding-conditioned mask diffusion; noise MSE plus CE and Dice, with explicit embedding alignment.",
    }
    for identifier, (_, family, dependency, pretrained, logits) in s.literal(
        seg_registry, "_PROFILES"
    ).items():
        extra = "segmentation-" + (
            identifier
            if identifier in {"sam2", "segdiff"}
            else "torch"
            if dependency == "torchvision"
            else "transformers"
        )
        source = (
            "https://huggingface.co/" + pretrained if pretrained and "/" in pretrained else None
        )
        if identifier == "sam2":
            source = "https://github.com/facebookresearch/sam2"
        example = "from openhisto.segmentation import ModelConfig, prepare_model\n\n"
        if identifier == "sam2":
            example += '# Install the pinned source from requirements-sam2.txt first.\nmodel = prepare_model(ModelConfig(\n    model="sam2", num_classes=2,\n    model_name_or_path="facebook/sam2-hiera-large",\n), device="cpu")\n# Prediction samples must provide explicit prompts.\n'
        else:
            example += f'model = prepare_model(ModelConfig(model="{identifier}", num_classes=2), device="cpu")\n'
            if identifier == "segdiff":
                example += (
                    "# Training and prediction samples must supply aligned patch embeddings.\n"
                )
        groups["segmentation"].append(
            make_entry(
                "segmentation",
                identifier,
                seg_names[identifier],
                family,
                "openhisto.segmentation",
                seg_desc[identifier],
                "RGB patches/arrays, explicit manifests or patch archives; labelled masks for training; "
                + (
                    "user-supplied prompts for binary inference."
                    if identifier == "sam2"
                    else "aligned embeddings for SegDiff."
                    if identifier == "segdiff"
                    else "binary/multiclass semantic labels with an explicit mask schema."
                ),
                extra,
                blob + "src/openhisto/segmentation/README.md",
                tasks=["binary_semantic_segmentation"]
                if identifier == "sam2"
                else [
                    "binary_semantic_segmentation",
                    "multiclass_semantic_segmentation",
                ],
                source=source,
                access="public_checkpoint"
                if identifier in {"mask2former", "segformer", "deeplabv3", "sam2"}
                else "local",
                access_note="SAM 2 additionally requires a separately installed pinned official source."
                if identifier == "sam2"
                else "No trained pathology checkpoint is bundled; default initialization is described explicitly.",
                default_initialization="random_convnext"
                if identifier == "upernet"
                else "random_embedding_conditioned_diffusion"
                if identifier == "segdiff"
                else pretrained or "explicit official checkpoint/config",
                dimensions={"output": "labels[H,W]; optional scores/probabilities[C,H,W]"},
                supports_logits=logits,
                example=example,
                evidence_sources=[seg_registry, "src/openhisto/segmentation/README.md"],
            )
        )

    vla_registry = "src/openhisto/vlas/registry.py"
    default_vla_status = s.field_default("src/openhisto/vlas/base.py", "ModelDescriptor", "status")
    vla_descriptions = {
        "patho_r1_7b": "Our Patho-R1 integration generates prompt-conditioned patch descriptions through the native Qwen2.5-VL processor and model.",
        "pathgen_llava": "Our PathGen-LLaVA integration generates prompt-conditioned patch descriptions with its separate PathGen-CLIP visual encoder and native LLaVA environment.",
        "quilt_llava_7b": "Our Quilt-LLaVA integration connects prompt-conditioned patch descriptions to the native Quilt-LLaVA runtime.",
        "pa_llava": "Our experimental PA-LLaVA integration supports prompt-conditioned patch descriptions using prepared stage-2 adapters, PLIP and an authorized Llama 3 base model.",
        "pathchat_plus": "We plan to add complete PathChat+ inference support in a future release.",
    }
    for item in s.descriptors(vla_registry):
        identifier = item["model_id"]
        status = item.get("status", default_vla_status)
        groups["vla"].append(
            make_entry(
                "vla",
                identifier,
                item["display_name"],
                "pathology_vision_language",
                "openhisto.vlas",
                vla_descriptions[identifier],
                "Indexed patch HDF5 archive or explicit RGB patch manifest plus a text prompt; stable patch identities are retained.",
                "vlas",
                blob + "src/openhisto/vlas/README.md",
                tasks=["prompted_patch_description"],
                access="unavailable"
                if status == "unavailable"
                else "restricted_artifacts"
                if identifier == "pa_llava"
                else "public_with_terms",
                access_note=(
                    "This profile currently records model provenance and access requirements. We need the complete checkpoint and compatible inference artifacts before enabling inference."
                    if status == "unavailable"
                    else item["access"]
                    + " This integration is experimental; prepared-asset and real-model validation remain required."
                    if status == "experimental"
                    else item["access"]
                    + " Our integration's real-checkpoint/native-reference acceptance remains unverified."
                ),
                status=status,
                source=item["source_url"],
                source_revision=item["source_revision"],
                checkpoint=item["checkpoint"],
                checkpoint_revision=item["checkpoint_revision"],
                license_note=item["license"],
                required_artifacts=list(item["required_artifacts"]),
                worker_requirements=list(item["dependencies"]),
                example=(
                    'from openhisto.vlas import model_info\n\n# Inspect profile metadata and access requirements.\nprint(model_info("pathchat_plus"))\n'
                    if status == "unavailable"
                    else 'from openhisto.vlas import SourceSpec, ModelSpec, DescribeConfig, describe_slide\n\n# Prepare the model\'s separate native environment/artifacts first.\nreport = describe_slide(\n    inputs=[SourceSpec("patches/slide.h5", source_id="grid-20x")],\n    output="descriptions/slide",\n    models=[ModelSpec('
                    + repr(identifier)
                    + ', python_executable="/path/to/backend/bin/python")],\n    prompt="Describe visible tissue architecture and nuclear morphology.",\n    config=DescribeConfig(slide_id="slide-a"),\n)\n'
                ),
                evidence_sources=[vla_registry, "src/openhisto/vlas/README.md"],
            )
        )

    dataset_file = "src/openhisto/default_datasets/models.py"
    dataset_details = {
        "TCGA": (
            "TCGA",
            "public",
            "Public diagnostic SVS slides through explicit GDC projects/case/file identifiers; original case-linked clinical entities are preserved, not harmonized into survival endpoints.",
            "https://docs.gdc.cancer.gov/API/Users_Guide/Downloading_Files/",
            'plan = discover("TCGA", {"projects": ["TCGA-KIRC"], "limit": 5})',
        ),
        "KPMP": (
            "KPMP",
            "public_export",
            "Public light-microscopic WSIs selected from a user-supplied Atlas repository CSV export; available participant links and clinical tables are retained.",
            "https://www.kpmp.org/help-docs/atlas-repository",
            'plan = discover("KPMP", {"repository_csv": "atlas-export.csv", "include_clinical": True})',
        ),
        "CAMELYON16": (
            "CAMELYON16",
            "public",
            "Official anonymous AWS inventory and native TIFFs with source training/test labels; optional annotation assets retain their native semantics.",
            "https://registry.opendata.aws/camelyon/",
            'plan = discover("CAMELYON16", {"split": "train", "limit": 5})',
        ),
        "BRACS": (
            "BRACS",
            "approved_local",
            "Registers approved local SVS slides using supplied XLSX/CSV metadata; retains WSI labels, source splits and supplied patient groups; ROIs are excluded.",
            "https://www.bracs.icar.cnr.it/details/",
            'report = import_local("BRACS", "/path/to/bracs", "metadata.xlsx")',
        ),
    }
    for identifier in s.literal(dataset_file, "DATASETS"):
        name, access, description, source, operation = dataset_details[identifier]
        example = (
            "from openhisto.default_datasets import discover, download, import_local\n\n"
            + operation
            + "\n"
        )
        if identifier != "BRACS":
            example += (
                '# Discovery transfers metadata only; downloading slides is explicit.\nreport = download(plan, "/path/to/data/'
                + identifier.lower()
                + '")\n'
            )
        groups["datasets"].append(
            make_entry(
                "datasets",
                identifier,
                name,
                "whole_slide_provider",
                "openhisto.default_datasets",
                description,
                "Explicit cohort selection or approved local files plus provider metadata; native WSI formats and original associations are preserved.",
                "default-datasets",
                blob + "src/openhisto/default_datasets/README.md",
                tasks=["slide_acquisition", "metadata_preservation"],
                access=access,
                access_note="Obtain approved data from the provider before local import; the package does not accept agreements or implement authenticated acquisition."
                if identifier == "BRACS"
                else "Public download path only; controlled data requires authorized acquisition outside this module.",
                source=source,
                example=example,
                evidence_sources=[
                    dataset_file,
                    "src/openhisto/default_datasets/README.md",
                ],
            )
        )

    normalizers_file = "src/openhisto/stain_transfer/config.py"
    normalizer_names = {
        "vahadane": "Vahadane",
        "macenko": "Macenko",
        "reinhard": "Reinhard",
        "histogram": "Histogram matching",
        "cyclegan": "MultiStain CycleGAN",
        "pix2pix": "pix2pix",
    }
    for identifier in s.literal(normalizers_file, "METHODS"):
        gan = identifier in {"cyclegan", "pix2pix"}
        spams = identifier in {"vahadane", "macenko"}
        extra = (
            "stain-transfer-gan" if gan else "stain-transfer-spams" if spams else "stain-transfer"
        )
        destination = (
            f'DomainSpec(method="{identifier}", checkpoint="generator_AtoB.pth")'
            if gan
            else f'DomainSpec(method="{identifier}", references=("reference.png",))'
        )
        groups["normalization"].append(
            make_entry(
                "normalization",
                identifier,
                normalizer_names[identifier],
                "generative_stain_transfer" if gan else "statistical_stain_normalization",
                "openhisto.stain_transfer",
                (
                    "Generator-based appearance transfer; checkpoints/domain direction/preprocessing must match. Supports explicit native training and inference."
                    if gan
                    else "Fits a destination reference and transforms valid RGB pixels while preserving patch geometry and invalid pixels."
                ),
                "uint8 RGB[H,W,3]; individual images, recursive folders, CSV/JSONL manifests or native patch archives.",
                extra,
                blob + "src/openhisto/stain_transfer/README.md",
                tasks=["stain_transfer", "generator_training"] if gan else ["stain_normalization"],
                access="local_checkpoint" if gan else "local_reference",
                access_note="No reference images or trained weights are bundled.",
                dimensions={
                    "input": "RGB[H,W,3]",
                    "output": "RGB[H,W,3], unchanged geometry",
                },
                example="from openhisto.stain_transfer import DomainSpec, TransferConfig, normalize\n\ndestination = "
                + destination
                + '\nreport = normalize("patches.h5", "normalized.h5", destination, TransferConfig())\n',
                evidence_sources=[
                    normalizers_file,
                    "src/openhisto/stain_transfer/README.md",
                ],
            )
        )

    classification_file = "src/openhisto/mil/classification/__init__.py"
    classification_docs = blob + "src/openhisto/mil/heads/README.md"
    for identifier in s.literal(classification_file, "_NEURAL"):
        names = {
            "linear": "Linear head",
            "mlp": "MLP head",
            "bayesian_mlp": "Bayesian MLP head",
        }
        groups["heads"].append(
            make_entry(
                "heads",
                identifier,
                names[identifier],
                "neural_classification",
                "openhisto.mil.classification",
                "Variational Gaussian weight posteriors, analytic KL/full-training-size scaling, posterior-mean evaluation and Monte Carlo uncertainty."
                if identifier == "bayesian_mlp"
                else "Differentiable fixed-vector classification head; attach at the profile's declared MIL representation boundary.",
                "CPU float32 slide vectors[N,D]; binary or multiclass single-label targets.",
                "mil",
                classification_docs,
                tasks=["binary_classification", "multiclass_classification"],
                access_note="Local CPU float32 neural head; fitting uses caller-supplied slide vectors and labels. No pretrained head weights are bundled.",
                devices=["cpu"],
                dtype="float32",
                dimensions={"input": "configurable D", "output": "logits[N,C]"},
                example='from openhisto.mil.classification import create_neural_head\nfrom openhisto.mil.heads import attach_head, representation_dimension\n\n# backbone is a constructed MIL profile.\nhead = create_neural_head("'
                + identifier
                + '", input_dim=representation_dimension(backbone), num_classes=3)\nmodel = attach_head(backbone, head, train_backbone=False)\n',
                evidence_sources=[
                    classification_file,
                    "src/openhisto/mil/heads/README.md",
                ],
            )
        )
    classifier_names = {
        "logistic_regression": "Logistic regression",
        "random_forest": "Random forest",
        "extra_trees": "Extra Trees",
        "hist_gradient_boosting": "Histogram gradient boosting",
        "svm": "SVM",
        "knn": "k-nearest neighbors",
        "gaussian_nb": "Gaussian Naive Bayes",
        "sklearn_mlp": "scikit-learn MLP",
        "xgboost": "XGBoost",
        "lightgbm": "LightGBM",
        "catboost": "CatBoost",
    }
    for identifier in s.literal(classification_file, "_CLASSICAL"):
        extra = (
            "mil-classical-" + identifier
            if identifier in {"xgboost", "lightgbm", "catboost"}
            else "mil-classical"
        )
        example = (
            'from openhisto.mil.classification import create_classifier\n\n# train_vectors/test_vectors are fixed slide vectors; labels are training labels.\nclassifier = create_classifier("'
            + identifier
            + '")\nclassifier.fit(train_vectors, labels)\npredictions = classifier.predict(test_vectors)\n'
        )
        groups["classifiers"].append(
            make_entry(
                "classifiers",
                identifier,
                classifier_names[identifier],
                "frozen_vector_classification",
                "openhisto.mil.classification",
                "CPU fitted classifier on frozen slide vectors; preserves original labels and class-column order."
                + (
                    " Probabilities require explicit calibration folds or held-out calibration data."
                    if identifier == "svm"
                    else ""
                ),
                "Finite fixed-width slide vectors[N,D] and original numeric/string/byte labels; no backbone gradients.",
                extra,
                classification_docs,
                tasks=["binary_classification", "multiclass_classification"],
                devices=["cpu"],
                dtype="package float64 vector policy",
                access_note="Local CPU estimator fitted on caller-supplied frozen slide vectors; install the selected backend extra. SVM probabilities additionally require explicit calibration data/folds."
                if identifier == "svm"
                else "Local CPU estimator fitted on caller-supplied frozen slide vectors; install the selected backend extra. No pretrained classifier is bundled.",
                dimensions={
                    "input": "fixed D",
                    "output": "predictions[N]; fitted probabilities[N,C] when supported/calibrated",
                },
                example=example,
                evidence_sources=[
                    classification_file,
                    "src/openhisto/mil/heads/README.md",
                ],
            )
        )

    survival_file = "src/openhisto/mil/survival/__init__.py"
    # The two public family IDs are verified against their literal factory dispatch.
    survival_source = s.read(survival_file)
    for identifier in ("cox", "discrete_hazard"):
        if (
            repr(identifier) not in survival_source
            and json.dumps(identifier) not in survival_source
        ):
            raise ValueError("Survival catalogue differs from the public factory")
        cox = identifier == "cox"
        groups["survival"].append(
            make_entry(
                "survival",
                identifier,
                "Cox proportional hazards" if cox else "Discrete hazards",
                "right_censored_survival",
                "openhisto.mil.survival",
                "Linear/MLP log-relative-risk head; cohort risk-set loss with Efron/Breslow ties and training-only Breslow absolute-survival calibration."
                if cox
                else "Linear/MLP conditional-hazard logits on a training-fitted positive-width grid; explicit censoring/boundary/truncation semantics.",
                "CPU float32 slide embeddings[N,D]; finite nonnegative durations in a consistent unit; event=1 observed, event=0 right-censored.",
                "mil",
                blob + "src/openhisto/mil/survival/README.md",
                tasks=["right_censored_survival"],
                devices=["cpu"],
                dtype="float32",
                networks=["linear", "mlp"],
                access_note="Local CPU float32 linear/MLP head. Fit with caller-supplied outcomes and use training-only baseline/grid calibration; no pretrained head is bundled.",
                dimensions={
                    "input": "configurable D",
                    "output": "scalar log-relative risk"
                    if cox
                    else "num_bins conditional-hazard logits",
                },
                example='from openhisto.mil.survival import create_survival_head\n\nhead = create_survival_head("'
                + identifier
                + '", input_dim=768, network="mlp"'
                + ("" if cox else ", num_bins=20")
                + ")\n"
                + (
                    '# After training, fit absolute-survival calibration on training data only.\nhead.fit_baseline(training_embeddings, durations, events, split="train")\n'
                    if cox
                    else 'head.fit_time_grid(training_durations, events, split="train")\n'
                ),
                evidence_sources=[
                    survival_file,
                    "src/openhisto/mil/survival/README.md",
                ],
            )
        )

    extras = tomllib.loads(s.read("pyproject.toml"))["project"]["optional-dependencies"]
    for category, entries in groups.items():
        entries.sort(key=lambda entry: entry["name"].casefold())
        if len(entries) != EXPECTED[category] or len({entry["id"] for entry in entries}) != len(
            entries
        ):
            raise ValueError(f"Unexpected {category} catalogue cardinality")
        for entry in entries:
            if entry["extra"] not in extras:
                raise ValueError(f"Unknown install extra: {entry['extra']}")
            validate_example(s, entry)
            for source in entry["evidence_sources"]:
                if not (package / source).is_file():
                    raise ValueError(f"Missing evidence source: {source}")
                s.read(source)
    version = s.literal("src/openhisto/__init__.py", "__version__")
    return {
        "schema_version": 1,
        "generated_from": {
            "repository": REPOSITORY,
            "commit": commit,
            "package_version": version,
            "method": "static AST/JSON/TOML inspection; no package imports, model loads, network or credential lookup",
            "source_sha256": dict(sorted(s.files.items())),
        },
        "summary": {"total": sum(EXPECTED.values()), "counts": EXPECTED},
        "notes": [
            "Catalogue support describes package interfaces, not pretrained scientific accuracy.",
            "Install commands run from an authorized local OpenHisto package checkout; they do not assume a published PyPI release.",
            "Examples require the caller-supplied inputs/artifacts noted in their comments and input contracts; they are not scientific training recipes.",
            "MIL profiles and shared task heads run on CPU float32; fitted classical classifiers retain their own numeric policy.",
            "Native MIL tasks and attached shared-head tasks are reported separately.",
            "79 entries include datasets, normalization methods and heads as well as model backends.",
            "Checkpoint access and license/use terms are separate; consult the linked source terms.",
        ],
        "categories": groups,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package",
        type=Path,
        required=True,
        help="Path to the authorized local OpenHistology_Package checkout.",
    )
    parser.add_argument("--output", type=Path, default=SITE / "data" / "catalogue.json")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that the existing JSON matches the current static sources.",
    )
    args = parser.parse_args()
    catalogue = build(args.package.resolve())
    encoded = json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if args.output.read_text(encoding="utf-8") != encoded:
            raise SystemExit("Catalogue is stale; run build_catalogue.py to regenerate it.")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(f"Validated {catalogue['summary']['total']} entries across {len(EXPECTED)} categories.")


if __name__ == "__main__":
    main()
