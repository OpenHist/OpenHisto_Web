# Contributing to the OpenHisto website

We welcome clearer explanations, accurate examples, accessibility improvements
and fixes to navigation or browser behavior. This repository contains the
website; package/API changes belong in the
[OpenHisto package repository](https://github.com/OpenHist/OpenHistology_Package/tree/main).

## Build and check

Follow the [README](README.md#set-up-and-build) to create a Python 3.12+
environment with `openhisto_site/requirements-site.lock.txt`, then run:

```bash
python openhisto_site/tools/site.py build
python openhisto_site/tools/site.py check
```

Both commands work from committed snapshots without an OpenHisto checkout.
Examples must remain documentation, not executable model or data-download jobs.
State the checks you ran in your pull request. For interface changes, preview
the affected pages at desktop and mobile widths, including keyboard navigation,
search, filters, code copying and light/dark modes where relevant.

## Edit the appropriate source

- `openhisto_site/content/`: authored installation and workflow guides.
- `openhisto_site/data/workflows.json`: homepage examples and module descriptions.
- `openhisto_site/data/applications.json`: research projects, resources and action availability.
- `openhisto_site/_templates/`: shared navigation and standalone page layouts.
- `openhisto_site/_static/`: styles, browser JavaScript, images and fonts.
- `openhisto_site/conf.py`: Sphinx configuration and page context.

Generated package guides under `reference/` and `data/catalogue.json` are
snapshots with source identities. Make package-source changes in the package
repository, then refresh explicitly:

```bash
python openhisto_site/tools/site.py sync --package-root /path/to/OpenHistology_Package
python openhisto_site/tools/site.py build
python openhisto_site/tools/site.py check
```

Review generated links, source revisions, hashes and content together. A normal
website build must not silently refresh from an adjacent package checkout.
Dependency updates should update the lock file and repeat the strict build,
site checks and relevant browser checks.

## Scientific and source accuracy

Use the project's voice and describe current behavior precisely. Keep planned
features distinct from available APIs; separate functional tests, actual model
execution and scientific results. A component count is an inventory, not a
validation score. Label dated snapshots as snapshots and schematics as
illustrations.

Keep unavailable paper/code actions disabled. Add a destination only when it is
real and applicable; do not invent publications, project use or model access.
Keep dataset resources separate from research projects using OpenHisto.

Use synthetic examples and sanitized logs. Keep credentials, patient records,
private environment paths and operational research notes out of the website and
its built output. Preserve package/source attribution, the PyData BSD notice
and each font's OFL file. The [third-party notices](THIRD_PARTY_NOTICES.md)
describe the included materials.

## Pull requests

Explain the problem, the changed pages or behavior and how you checked it. Keep
source edits separate from generated output: do not commit virtual environments,
`_build/`, model artifacts or datasets. The website CI produces a build artifact;
contributing a change does not deploy the site.
