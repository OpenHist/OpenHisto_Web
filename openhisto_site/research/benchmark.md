# OpenHisto end-to-end benchmark

This is our first featured project in [Research & applications](../research.md).
We use OpenHisto to connect image preparation, classification, risk and survival,
segmentation and vision-language analysis within a reproducible study. We record
functional tests, real checkpoint execution and scientific comparisons separately.

## Dated campaign snapshot

Our **30 October 2026 snapshot** records the CPU preparation campaign at that
point in time. Counts may advance after this update. Scientific evaluation is not complete.

<div class="oh-study-progress"><div class="oh-progress-label"><span>Patients with completed features</span><strong>96 / 897 · 10.7%</strong></div><div class="oh-progress" role="progressbar" aria-label="Patients with completed features in our 30 October 2026 campaign snapshot" aria-valuemin="0" aria-valuemax="897" aria-valuenow="96"><span style="width:10.7%"></span></div></div>

| Measure | Snapshot |
|---|---:|
| Frozen TCGA renal patients | 897 |
| Verified WSI extractions | 98 |
| Patients with completed feature preparation | 96 / 897 |
| Recorded elapsed runtime | 11.6 hours |
| Failed subjobs retained in the ledger | 1 |
| Prepared official PanNuke patches | 7,901 across all three folds |

Extraction and feature counts describe different stages of a rolling pipeline;
they are not disjoint outcome groups. A failed subjob remains a failure/pending
recovery entry rather than disappearing from the denominator. These counts do
not establish completed cohort training, native-reference parity or held-out
scientific performance.

## Cohorts and partitions

The renal cohort uses public TCGA KIRC, KIRP and KICH diagnostic slides, with one
eligible primary-tumor WSI per patient. Selection uses explicit GDC case/sample/
slide associations, followed by a deterministic file-UUID tie-break. The frozen
cohort contains 513 KIRC, 275 KIRP and 109 KICH patients.

Patient-disjoint roles are train/calibration/validation/test at 60/10/10/20,
stratified by project with deterministic rounding and split seed 1729. All
related renal tasks share that allocation. Training seeds 17, 29 and 43 are
separate from the split seed. Representation fitting excludes calibration,
validation and test patients.

| Task | Target source |
|---|---|
| `renal_histotype_3way` | Explicit KIRC/KIRP/KICH GDC project membership |
| `renal_kirc_vs_other` | KIRC versus the other two renal projects |
| `kirc_overall_survival` | Curated TCGA-CDR `OS` and `OS.time`, in days |

There are 511 eligible KIRC survival targets in the frozen cohort. Missing or
invalid curated outcomes are recorded as survival exclusions without changing
classification membership. The source is the official
[TCGA PanCanAtlas curated resource](https://gdc.cancer.gov/about-data/publications/pancanatlas),
not a reconstruction from arbitrary follow-up records. Configured evaluation
horizons are 365, 1,095 and 1,825 days; unsupported horizons require explicit
unavailable counts/reasons.

PanNuke keeps official fold 1 for training, fold 2 for validation and fold 3 for
testing, matching one of the configurations on the
[official dataset page](https://warwick.ac.uk/fac/cross_fac/tia/data/pannuke/).
No patient mapping or additional calibration partition is invented for it.

## Annotation policy

PanNuke's five native foreground instance channels remain authoritative.
Primary binary labels are their union; primary semantic background is its
complement. Pixels where multiple foreground types overlap use semantic ignore
value 255. VLA type-presence targets mean literal annotated-type presence.

The native sixth background channel is preserved for QA. Its gaps/conflicts
do not automatically censor primary targets or prove missing annotations.
`binary_valid` is explicitly a strict QA/sensitivity mask, with separately
recorded conservative labels and eligibility. Annotation completeness remains
unverified. The versioned policy preserves source facts separately from these
declared analysis choices; the
[official metrics implementation](https://github.com/TissueImageAnalytics/PanNuke-metrics)
evaluates the native five foreground channels.

## Evidence and resource policy

| Layer | What a passing result establishes |
|---|---|
| Functional contract | A declared API, geometry, storage or recovery invariant on controlled fixtures |
| Real-model acceptance | An actual selected checkpoint/backend ran on the declared inputs |
| Scientific comparison | Frozen cohort, representations, fitting protocol and held-out evaluation were completed |

Our CPU campaign prepares raw/Reinhard appearances and public Phikon/Phikon-v2
features. We will compare these vectors with the native model outputs and run
the remaining scientific experiments as separate evaluation stages. Phikon's
[model card](https://huggingface.co/owkin/phikon) and the
[Phikon-v2 model card](https://huggingface.co/owkin/phikon-v2) report TCGA
pretraining; this renal workflow is not evidence of an independently held-out
foundation-model evaluation.

Artifacts carry configuration, source/environment identity, hashes and status.
The raw cache is bounded: only benchmark-owned, verified, reconstructable inputs
may be evicted after downstream publication checks. We preserve local input data. The 500 GB plan assigns 80 GB raw, 100 GB patches, 20 GB segmentation,
50 GB features, 120 GB models/environments, 30 GB checkpoints, 40 GB temporary
space, 10 GB reports and 50 GB reserve.

Paid APIs and gated weights are disabled in this CPU campaign. Full scientific
qualification, dedicated multiscale views and outstanding failure/recovery
evidence remain explicit work. CPU input preparation is not a declaration that
all GPU or scientific workflows have been validated.
