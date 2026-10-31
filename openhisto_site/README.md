# Website source and maintenance

This directory is the standalone Sphinx source for the
[OpenHisto website](https://github.com/OpenHist/OpenHisto_Web/tree/main).
For environment setup, local preview and future static-host configuration,
see the [root README](../README.md).

## Commands from the repository root

Use an activated Python 3.12+ environment installed from
`openhisto_site/requirements-site.lock.txt`:

```bash
python openhisto_site/tools/site.py build
python openhisto_site/tools/site.py check
python openhisto_site/tools/site.py serve --port 8050
```

`build` uses committed catalogue/reference snapshots, prepares deterministic
site assets/search content and builds HTML with strict Sphinx warnings. `check`
audits that output without network requests. `serve` previews it on
`127.0.0.1:8050`; if necessary it builds from the same snapshots first. Output is
`openhisto_site/_build/html/`. No package installation, model runtime or Node
tooling is needed.

## Layout

| Location | Purpose |
|---|---|
| `content/` | Authored user guides and current/planned workflow boundaries. |
| `research.md` / `research/` | Standalone research listing and study pages. |
| `data/applications.json` | Project descriptions, resources and disabled/available action states. |
| `reference/` | Committed package-guide snapshots and their provenance. |
| `data/catalogue.json` | Committed component inventory, access metadata, examples and source hashes. |
| `data/workflows.json` | Homepage workflow descriptions and examples. |
| `_templates/` | Page layouts, shared navigation and documentation sidebar. |
| `_static/` | Local CSS/JavaScript, deterministic schematics, fonts and licenses. |
| `tools/` | Snapshot refresh, asset preparation, strict build, preview and checks. |

## Refresh from package source

The [package repository](https://github.com/OpenHist/OpenHistology_Package/tree/main)
is required only when deliberately updating snapshots:

```bash
python openhisto_site/tools/site.py sync --package-root /path/to/OpenHistology_Package
python openhisto_site/tools/site.py build
python openhisto_site/tools/site.py check
```

Sync reads source and Git metadata, not model objects or credentials. Review its
content/provenance changes before committing. Do not make a package checkout a
normal build prerequisite.

## Research and static output

Research status is recorded content, not a live experiment connection. Keep
in-progress paper/code actions disabled until genuine destinations exist.
Snapshots retain their dates, failures and scientific limitations. Schematics
remain labelled as illustrations.

Only the generated HTML directory is a future publish artifact. Our CI builds,
checks and uploads it without deploying. The site has no account flows,
analytics or model-execution controls. Operator research notes outside this
website are not part of the repository or served output.

Preserve [the PyData notice](../LICENSES/pydata-sphinx-theme.txt), all font OFL
files and package-guide attribution; see
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). Our original website
code/content is [MIT](../LICENSE), copyright 2026 Abteen Arab.
