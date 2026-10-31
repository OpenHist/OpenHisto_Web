# Third-party notices

Our original OpenHisto website code/content is distributed under the
[MIT License](LICENSE), copyright 2026 Abteen Arab. The materials below retain
their own notices; our license does not replace them.

## PyData Sphinx Theme

We build with the released PyData Sphinx Theme package. Its BSD 3-Clause notice,
including copyright 2018 pandas, is preserved in
[LICENSES/pydata-sphinx-theme.txt](LICENSES/pydata-sphinx-theme.txt).
Keep the theme's bundled asset notices when distributing the generated site.
Sphinx and extension dependencies retain the notices supplied in their
installed distributions.

## Self-hosted fonts

We retain the font files and complete SIL Open Font License 1.1 texts under
`openhisto_site/_static/fonts/`:

| Family | Attribution in the supplied notice | License file |
|---|---|---|
| DM Sans | The DM Sans Project Authors | [dmsans-OFL.txt](openhisto_site/_static/fonts/dmsans-OFL.txt) |
| Instrument Serif | The Instrument Serif Project Authors | [instrumentserif-OFL.txt](openhisto_site/_static/fonts/instrumentserif-OFL.txt) |
| IBM Plex Mono | IBM Corp.; reserved font name Plex | [ibmplexmono-OFL.txt](openhisto_site/_static/fonts/ibmplexmono-OFL.txt) |

Keep each license with its font files when distributing the website source or
static assets.

## Package documentation and external sources

We adapt package guides and examples from
[OpenHisto](https://github.com/OpenHist/OpenHistology_Package/tree/main).
The committed [reference provenance](openhisto_site/reference/provenance.json)
and [catalogue metadata](openhisto_site/data/catalogue.json) identify their
source revision and hashes. Package documentation preserves its source links
and relevant upstream attribution.

Links to model cards, software repositories and datasets identify their
respective sources; they do not transfer those artifacts' licenses to our
website or imply endorsement. Refer to the package's own third-party notices
and the linked original sources for incorporated model implementation terms.
No model weights, patient slides or clinical datasets are included here. Our
tissue and mask schematics are generated illustrations, not experimental images.
