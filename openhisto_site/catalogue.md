---
html_theme.sidebar_secondary.remove: true
---

# Model catalogue

Explore package components by model name, task, native input contract and access requirements.

**Amazon Nova Multimodal Embeddings** (`nova_multimodal`) — Official checkpoint preprocessing and one image per embedding; one vector per selected patch.
Category: encoders. Tasks: patch_embedding. Access: api.

**Cohere Embed v5 Fast** (`cohere_embed_5_fast`) — Official checkpoint preprocessing and one image per embedding; one vector per selected patch.
Category: encoders. Tasks: patch_embedding. Access: api.

**Cohere Embed v5 Pro** (`cohere_embed_5_pro`) — Official checkpoint preprocessing and one image per embedding; one vector per selected patch.
Category: encoders. Tasks: patch_embedding. Access: api.

**CONCH v1.5 (TITAN patch representation)** (`conch15_titan`) — Official checkpoint preprocessing and attentional_pooler; one vector per selected patch.
Category: encoders. Tasks: patch_embedding. Access: gated.

**Gemini Embedding 2** (`gemini_embedding_2`) — Official checkpoint preprocessing and one image per embedding; one vector per selected patch.
Category: encoders. Tasks: patch_embedding. Access: api.

**Phikon** (`phikon`) — Official checkpoint preprocessing and cls_token; one vector per selected patch.
Category: encoders. Tasks: patch_embedding. Access: public.

**Phikon-v2** (`phikon_v2`) — Official checkpoint preprocessing and cls_token; one vector per selected patch.
Category: encoders. Tasks: patch_embedding. Access: public.

**UNI v1** (`uni_v1`) — Official checkpoint preprocessing and cls_token; one vector per selected patch.
Category: encoders. Tasks: patch_embedding. Access: gated.

**ABMIL** (`abmil`) — Native attention pooling with an explicit feature-to-500 projection when needed.
Category: mil. Tasks: classification. Access: local.

**ACMIL** (`acmil`) — Attention branches and native patch masking; branch outputs remain available.
Category: mil. Tasks: classification. Access: local.

**ASMIL** (`asmil`) — Attention model with a frozen anchor and an explicit update_anchor hook.
Category: mil. Tasks: classification. Access: local.

**CAPRMIL** (`caprmil`) — Native cluster/transformer model with explicit profile options.
Category: mil. Tasks: classification. Access: local.

**CLAM-MB** (`clam_mb`) — Multiple-branch CLAM; class-conditioned representations preserve native class order.
Category: mil. Tasks: classification. Access: local.

**CLAM-SB** (`clam_sb`) — Single-branch CLAM with optional labelled instance-level evaluation and loss.
Category: mil. Tasks: classification. Access: local.

**CS-MIL** (`cs_mil`) — Corresponding three-scale clusters with native independent sigmoid heads.
Category: mil. Tasks: independent_sigmoid. Access: local.

**DGR-MIL** (`dgr_mil`) — Native lesion/center computations and auxiliary outputs remain available.
Category: mil. Tasks: classification. Access: local.

**DSMIL** (`dsmil`) — Dual instance/bag streams; native inference averages their independent sigmoid scores.
Category: mil. Tasks: classification. Access: local.

**DTFD-MIL** (`dtfd_mil`) — Two-tier distillation; pseudo-bag logits and AFS/MaxS/MaxMinS modes remain exposed.
Category: mil. Tasks: classification. Access: local.

**Gated ABMIL** (`gated_abmil`) — Native gated attention pooling and classifier with the same feature projection policy as ABMIL.
Category: mil. Tasks: classification. Access: local.

**GFR-MIL** (`gfr_mil`) — Corresponding low/high features with native coordinate quantization and auxiliary loss; native survival is optional.
Category: mil. Tasks: classification, discrete_survival. Access: local.

**HAG-MIL** (`hag_mil`) — Three native IAT models and a selection cascade with four children per parent.
Category: mil. Tasks: classification. Access: local.

**HIPT** (`hipt`) — Native LGP/GP hierarchy contracts and a separately named no-transformer ablation; generic vectors do not replace DINO.
Category: mil. Tasks: classification. Access: local.

**H²-MIL** (`h2_mil`) — Native hierarchical pooling over ordered root, coarse and fine graph nodes.
Category: mil. Tasks: classification. Access: local.

**ILRA** (`ilra`) — Native low-rank attention model operating on feature bags.
Category: mil. Tasks: classification. Access: local.

**Lin-MIL** (`lin_mil`) — Native linear-attention MIL; optional CUDA attention ablations are outside the CPU profile.
Category: mil. Tasks: classification. Access: local.

**MambaMIL** (`mamba_mil`) — Classification profile using differentiable Torch reference convolution/scan and native SR padding/transposition.
Category: mil. Tasks: classification. Access: local.

**MaxMIL** (`max_mil`) — Featurewise maximum pooling with the package's classifier.
Category: mil. Tasks: classification. Access: local.

**MeanMIL** (`mean_mil`) — Featurewise mean pooling with the package's classifier.
Category: mil. Tasks: classification. Access: local.

**MeanStdMIL** (`mean_std_mil`) — Concatenated mean and population standard deviation; singleton bags remain finite.
Category: mil. Tasks: classification. Access: local.

**MHIM v1** (`mhim_v1`) — MHIM student/EMA teacher with native masking, distillation loss and explicit teacher updates.
Category: mil. Tasks: classification. Access: local.

**MHIM v2** (`mhim_v2`) — Second MHIM source track retaining token merging, masking and checkpointed EMA teacher state.
Category: mil. Tasks: classification. Access: local.

**nnMIL** (`nnmil`) — Native training sampling and evaluation-window ensemble; returned mean window features support attached heads.
Category: mil. Tasks: classification. Access: local.

**PANTHER** (`panther`) — Prototype/EM representation with an added downstream linear classifier; requires training-fitted prototypes.
Category: mil. Tasks: representation, classification_with_adapter_head. Access: local.

**Patch-GCN** (`patch_gcn`) — Prepared graph with native discrete-survival hazards; native num_classes denotes time bins.
Category: mil. Tasks: discrete_survival. Access: local.

**ResGAT** (`resgat`) — Native residual graph-attention computation on a caller-prepared graph.
Category: mil. Tasks: classification. Access: local.

**RRT-MIL / R²T-MIL** (`rrt_mil`) — Native regional transformer; feature bags support none/peg/ppeg positions and attention/average pooling.
Category: mil. Tasks: classification. Access: local.

**SlideGraph+** (`slidegraph_plus`) — Clustered-region graph with released EdgeConv aggregation; GIN is an explicit alternative.
Category: mil. Tasks: classification. Access: local.

**TAD-Graph** (`tad_graph`) — Prepared causal/trivial graphs, normalized edge descriptors and information loss; native survival is optional.
Category: mil. Tasks: classification, discrete_survival. Access: local.

**TransMIL** (`transmil`) — Native transformer MIL computation with a device-local class token.
Category: mil. Tasks: classification. Access: local.

**VarPool** (`varpool`) — Native attention mean/variance pooling with configurable variance readout.
Category: mil. Tasks: classification. Access: local.

**WiKG** (`wikg`) — Learns a graph from feature bags; the released network requires no patch coordinates.
Category: mil. Tasks: classification. Access: local.

**ZoomMIL** (`zoommil`) — Native three-level zoom selection over parent-major multiscale features.
Category: mil. Tasks: classification. Access: local.

**DeepLabV3** (`deeplabv3`) — torchvision pretrained ResNet50 with a replaced class head and pixel cross-entropy.
Category: segmentation. Tasks: binary_semantic_segmentation, multiclass_semantic_segmentation. Access: public_checkpoint.

**Mask2Former** (`mask2former`) — Native query classification with matched mask BCE and Dice; exports summed query-class mask scores, not class logits.
Category: segmentation. Tasks: binary_semantic_segmentation, multiclass_semantic_segmentation. Access: public_checkpoint.

**SAM 2** (`sam2`) — Official prompt-conditioned image model with binary BCE and Dice; explicit prompts are required at inference.
Category: segmentation. Tasks: binary_semantic_segmentation. Access: public_checkpoint.

**SegDiff** (`segdiff`) — Random embedding-conditioned mask diffusion; noise MSE plus CE and Dice, with explicit embedding alignment.
Category: segmentation. Tasks: binary_semantic_segmentation, multiclass_semantic_segmentation. Access: local.

**SegFormer** (`segformer`) — Pretrained semantic backbone with pixel cross-entropy and a task-specific class head.
Category: segmentation. Tasks: binary_semantic_segmentation, multiclass_semantic_segmentation. Access: public_checkpoint.

**UPerNet** (`upernet`) — Random ConvNeXt initialization by default; an explicit model path selects pretrained initialization.
Category: segmentation. Tasks: binary_semantic_segmentation, multiclass_semantic_segmentation. Access: local.

**PA-LLaVA / Pathology-LLaVA** (`pa_llava`) — Our experimental PA-LLaVA integration supports prompt-conditioned patch descriptions using prepared stage-2 adapters, PLIP and an authorized Llama 3 base model.
Category: vla. Tasks: prompted_patch_description. Access: restricted_artifacts.

**PathChat+** (`pathchat_plus`) — We plan to add complete PathChat+ inference support in a future release.
Category: vla. Tasks: prompted_patch_description. Access: unavailable.

**PathGen-LLaVA-13B** (`pathgen_llava`) — Our PathGen-LLaVA integration generates prompt-conditioned patch descriptions with its separate PathGen-CLIP visual encoder and native LLaVA environment.
Category: vla. Tasks: prompted_patch_description. Access: public_with_terms.

**Patho-R1-7B** (`patho_r1_7b`) — Our Patho-R1 integration generates prompt-conditioned patch descriptions through the native Qwen2.5-VL processor and model.
Category: vla. Tasks: prompted_patch_description. Access: public_with_terms.

**Quilt-LLaVA-7B** (`quilt_llava_7b`) — Our Quilt-LLaVA integration connects prompt-conditioned patch descriptions to the native Quilt-LLaVA runtime.
Category: vla. Tasks: prompted_patch_description. Access: public_with_terms.

**BRACS** (`BRACS`) — Registers approved local SVS slides using supplied XLSX/CSV metadata; retains WSI labels, source splits and supplied patient groups; ROIs are excluded.
Category: datasets. Tasks: slide_acquisition, metadata_preservation. Access: approved_local.

**CAMELYON16** (`CAMELYON16`) — Official anonymous AWS inventory and native TIFFs with source training/test labels; optional annotation assets retain their native semantics.
Category: datasets. Tasks: slide_acquisition, metadata_preservation. Access: public.

**KPMP** (`KPMP`) — Public light-microscopic WSIs selected from a user-supplied Atlas repository CSV export; available participant links and clinical tables are retained.
Category: datasets. Tasks: slide_acquisition, metadata_preservation. Access: public_export.

**TCGA** (`TCGA`) — Public diagnostic SVS slides through explicit GDC projects/case/file identifiers; original case-linked clinical entities are preserved, not harmonized into survival endpoints.
Category: datasets. Tasks: slide_acquisition, metadata_preservation. Access: public.

**Histogram matching** (`histogram`) — Fits a destination reference and transforms valid RGB pixels while preserving patch geometry and invalid pixels.
Category: normalization. Tasks: stain_normalization. Access: local_reference.

**Macenko** (`macenko`) — Fits a destination reference and transforms valid RGB pixels while preserving patch geometry and invalid pixels.
Category: normalization. Tasks: stain_normalization. Access: local_reference.

**MultiStain CycleGAN** (`cyclegan`) — Generator-based appearance transfer; checkpoints/domain direction/preprocessing must match. Supports explicit native training and inference.
Category: normalization. Tasks: stain_transfer, generator_training. Access: local_checkpoint.

**pix2pix** (`pix2pix`) — Generator-based appearance transfer; checkpoints/domain direction/preprocessing must match. Supports explicit native training and inference.
Category: normalization. Tasks: stain_transfer, generator_training. Access: local_checkpoint.

**Reinhard** (`reinhard`) — Fits a destination reference and transforms valid RGB pixels while preserving patch geometry and invalid pixels.
Category: normalization. Tasks: stain_normalization. Access: local_reference.

**Vahadane** (`vahadane`) — Fits a destination reference and transforms valid RGB pixels while preserving patch geometry and invalid pixels.
Category: normalization. Tasks: stain_normalization. Access: local_reference.

**Bayesian MLP head** (`bayesian_mlp`) — Variational Gaussian weight posteriors, analytic KL/full-training-size scaling, posterior-mean evaluation and Monte Carlo uncertainty.
Category: heads. Tasks: binary_classification, multiclass_classification. Access: local.

**Linear head** (`linear`) — Differentiable fixed-vector classification head; attach at the profile's declared MIL representation boundary.
Category: heads. Tasks: binary_classification, multiclass_classification. Access: local.

**MLP head** (`mlp`) — Differentiable fixed-vector classification head; attach at the profile's declared MIL representation boundary.
Category: heads. Tasks: binary_classification, multiclass_classification. Access: local.

**Cox proportional hazards** (`cox`) — Linear/MLP log-relative-risk head; cohort risk-set loss with Efron/Breslow ties and training-only Breslow absolute-survival calibration.
Category: survival. Tasks: right_censored_survival. Access: local.

**Discrete hazards** (`discrete_hazard`) — Linear/MLP conditional-hazard logits on a training-fitted positive-width grid; explicit censoring/boundary/truncation semantics.
Category: survival. Tasks: right_censored_survival. Access: local.

**CatBoost** (`catboost`) — CPU fitted classifier on frozen slide vectors; preserves original labels and class-column order.
Category: classifiers. Tasks: binary_classification, multiclass_classification. Access: local.

**Extra Trees** (`extra_trees`) — CPU fitted classifier on frozen slide vectors; preserves original labels and class-column order.
Category: classifiers. Tasks: binary_classification, multiclass_classification. Access: local.

**Gaussian Naive Bayes** (`gaussian_nb`) — CPU fitted classifier on frozen slide vectors; preserves original labels and class-column order.
Category: classifiers. Tasks: binary_classification, multiclass_classification. Access: local.

**Histogram gradient boosting** (`hist_gradient_boosting`) — CPU fitted classifier on frozen slide vectors; preserves original labels and class-column order.
Category: classifiers. Tasks: binary_classification, multiclass_classification. Access: local.

**k-nearest neighbors** (`knn`) — CPU fitted classifier on frozen slide vectors; preserves original labels and class-column order.
Category: classifiers. Tasks: binary_classification, multiclass_classification. Access: local.

**LightGBM** (`lightgbm`) — CPU fitted classifier on frozen slide vectors; preserves original labels and class-column order.
Category: classifiers. Tasks: binary_classification, multiclass_classification. Access: local.

**Logistic regression** (`logistic_regression`) — CPU fitted classifier on frozen slide vectors; preserves original labels and class-column order.
Category: classifiers. Tasks: binary_classification, multiclass_classification. Access: local.

**Random forest** (`random_forest`) — CPU fitted classifier on frozen slide vectors; preserves original labels and class-column order.
Category: classifiers. Tasks: binary_classification, multiclass_classification. Access: local.

**scikit-learn MLP** (`sklearn_mlp`) — CPU fitted classifier on frozen slide vectors; preserves original labels and class-column order.
Category: classifiers. Tasks: binary_classification, multiclass_classification. Access: local.

**SVM** (`svm`) — CPU fitted classifier on frozen slide vectors; preserves original labels and class-column order. Probabilities require explicit calibration folds or held-out calibration data.
Category: classifiers. Tasks: binary_classification, multiclass_classification. Access: local.

**XGBoost** (`xgboost`) — CPU fitted classifier on frozen slide vectors; preserves original labels and class-column order.
Category: classifiers. Tasks: binary_classification, multiclass_classification. Access: local.
