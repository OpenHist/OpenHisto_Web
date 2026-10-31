# OpenHisto website

Created and maintained by **Abteen Arab**.

This repository contains our documentation, component catalogue and research
pages for OpenHisto. We build it as a static Sphinx site using the released
PyData Sphinx Theme, with our own templates, styles and browser interactions.

- [Website source](https://github.com/OpenHist/OpenHisto_Web/tree/main)
- [OpenHisto package](https://github.com/OpenHist/OpenHistology_Package/tree/main)
- [Contributing](CONTRIBUTING.md)

The website builds from committed reference and catalogue snapshots. You do not
need an OpenHisto checkout, scientific extras, model weights or Node tooling to
build it. Examples are rendered as documentation; the build does not execute
them or connect to an experiment.

## Set up and build

Use **Python 3.12+**. From this repository root:

```bash
python3.12 -m venv .venv-site
source .venv-site/bin/activate
python -m pip install -r openhisto_site/requirements-site.lock.txt
python openhisto_site/tools/site.py build
python openhisto_site/tools/site.py check
```

The build runs Sphinx with warnings treated as errors. The checker audits local
links/assets, anchors, catalogue consistency, example syntax and accidental
private-environment details. The complete static output is
`openhisto_site/_build/html/`.

Preview the built site locally:

```bash
python openhisto_site/tools/site.py serve --port 8050
```

Open <http://127.0.0.1:8050/>. The preview binds to loopback; stop it with Ctrl+C.
We use self-hosted fonts and local assets. Catalogue filtering, search and code
copying run in the browser.

## Update package snapshots explicitly

Normal `build`, `check` and `serve` operations use the website's committed files.
To adopt documentation/catalogue changes from a package checkout, run an explicit
sync, review its changes, then rebuild:

```bash
python openhisto_site/tools/site.py sync --package-root /path/to/OpenHistology_Package
python openhisto_site/tools/site.py build
python openhisto_site/tools/site.py check
```

Sync reads package source files and Git metadata without importing model code or
running its examples. Reference provenance and catalogue metadata record their
source revision and hashes. A package checkout is needed only for this optional
maintenance operation; its location is supplied explicitly.

## GitHub Pages deployment

The website is published at <https://openhist.github.io/OpenHisto_Web/>.
GitHub Pages uses **GitHub Actions** as its publishing source. Our workflow
builds and checks the website, then publishes only `openhisto_site/_build/html/`
after a push to `main` or a manual workflow run on `main`. Pull requests build
and validate without deploying. A failed build or check prevents publication.

Do not select **Deploy from a branch** with the repository root: that publishes
the README rather than the website. Deployment status and the live URL are
available in the repository's Actions runs and `github-pages` environment.

## Other static hosting providers

When configuring another provider, use these values from the repository root:

| Setting | Value |
|---|---|
| Python | 3.12 or newer |
| Dependency installation | `python -m pip install -r openhisto_site/requirements-site.lock.txt` |
| Build command | `python openhisto_site/tools/site.py build` |
| Publish directory | `openhisto_site/_build/html` |
| Validation command | `python openhisto_site/tools/site.py check` |

If the provider offers a separate dependency-install step, use the installation
command above before building. If it offers only one build-command field, use
all three commands so a fresh environment installs its dependencies and rejects
a failed build or check:

```bash
python -m pip install -r openhisto_site/requirements-site.lock.txt &&
python openhisto_site/tools/site.py build &&
python openhisto_site/tools/site.py check
```

Serve the contents of the publish directory, including its `_static` files and
fonts, and retain the generated `.nojekyll` file. The published site needs no
Python server, database, model runtime or Node build. Keep the source files and
build output separate. The workflow also retains a downloadable HTML artifact
for review.

## Content and provenance

Authored guides live in `openhisto_site/content/`; generated package reference
pages live in `openhisto_site/reference/`. The catalogue and research metadata
live in `openhisto_site/data/`. See the
[site maintenance guide](openhisto_site/README.md) for the complete layout.

Research entries distinguish current work, dated preparation snapshots and
scientific results. Paper and project-code actions remain disabled until their
actual destinations are available. Dataset resource links do not imply external
adoption of OpenHisto. Schematic images are illustrations, not patient data or
model output.

## License

Our original website code/content uses the [MIT License](LICENSE), copyright
2026 Abteen Arab. We preserve the PyData BSD notice, font OFL licenses and source
attribution for imported package documentation. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
