"""Local OpenHisto documentation; examples are rendered, never executed."""

import json
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

ROOT = Path(__file__).parent.resolve()
project = "OpenHisto"
author = "Abteen Arab"
copyright = "2026, Abteen Arab"
version = release = json.loads((ROOT / "data/catalogue.json").read_text())[
    "generated_from"
]["package_version"]
extensions = ["myst_parser", "sphinx_copybutton", "sphinx_design"]
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
master_doc = "index"
exclude_patterns = ["_build", "tools", "data", "**/.DS_Store", "README.md"]
myst_enable_extensions = ["colon_fence", "deflist", "fieldlist"]
myst_heading_anchors = 6
templates_path = ["_templates"]
html_theme = "pydata_sphinx_theme"
html_title = "OpenHisto"
html_short_title = "OpenHisto"
html_static_path = ["_static"]
html_css_files = ["fonts/fonts.css", "openhisto.css"]
html_js_files = ["openhisto.js"]
html_favicon = "_static/mark.svg"
html_show_sourcelink = False
html_show_sphinx = False
html_show_copyright = False
html_theme_options = {
    "show_prev_next": False,
    "navigation_depth": 3,
    "show_nav_level": 1,
    "show_toc_level": 2,
    "header_links_before_dropdown": 6,
    "navbar_start": ["navbar-logo"],
    "navbar_center": [],
    "navbar_end": [],
    "navbar_persistent": [],
    "footer_start": [],
    "footer_end": [],
    "secondary_sidebar_items": ["page-toc"],
    "primary_sidebar_end": [],
    "article_header_start": ["breadcrumbs"],
    "article_header_end": [],
    "article_footer_items": [],
    "pygment_light_style": "friendly",
    "pygment_dark_style": "native",
}
html_sidebars = {
    "index": [],
    "catalogue": [],
    "research": [],
    "research/benchmark": [],
    "**": ["search-field.html", "openhisto-sidebar.html"],
}
html_context = {"default_mode": "light"}
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
copybutton_remove_prompts = True
copybutton_selector = "body.oh-docs div.highlight pre"

CATEGORY_NAMES = {
    "encoders": "Feature encoders",
    "mil": "MIL backbones",
    "segmentation": "Segmentation",
    "normalization": "Stain normalization",
    "datasets": "Datasets",
    "vla": "Vision-language",
    "heads": "Neural heads",
    "classifiers": "Classical classifiers",
    "survival": "Survival heads",
}
CATEGORY_DOCS = {
    "encoders": "features",
    "mil": "mil",
    "segmentation": "segmentation",
    "normalization": "normalization",
    "datasets": "datasets",
    "vla": "vla",
    "heads": "heads",
    "classifiers": "classifiers",
    "survival": "survival",
}
ACCESS_LABELS = {
    "public": "Public access",
    "gated": "Approval required",
    "api": "API access",
    "local": "Local",
    "public_checkpoint": "Public checkpoint",
    "restricted_artifacts": "Restricted artifacts",
    "unavailable": "Unavailable",
    "public_with_terms": "Public · terms apply",
    "approved_local": "Approved local data",
    "public_export": "Public data export",
    "local_reference": "Local reference",
    "local_checkpoint": "Local checkpoint",
}


def page_context(app, pagename, templatename, context, doctree):
    catalogue = json.loads((ROOT / "data/catalogue.json").read_text())
    workflows = json.loads((ROOT / "data/workflows.json").read_text())
    for item in workflows:
        item["highlighted"] = highlight(
            item["code"], PythonLexer(), HtmlFormatter(cssclass="highlight")
        )
    entries = []
    for category, models in catalogue["categories"].items():
        for model in models:
            item = dict(model)
            item["category_label"] = CATEGORY_NAMES[category]
            item["local_docs"] = "reference/" + CATEGORY_DOCS[category]
            access = item["access"]
            item["access_label"] = ACCESS_LABELS.get(
                access, access.replace("_", " ").capitalize()
            )
            item["highlighted"] = highlight(
                item["example"], PythonLexer(), HtmlFormatter(cssclass="highlight")
            )
            item["search_text"] = " ".join(
                str(item.get(k, ""))
                for k in (
                    "id",
                    "name",
                    "family",
                    "description",
                    "input_contract",
                    "tasks",
                    "extra",
                    "category_label",
                )
            ).lower()
            entries.append(item)
    context.update(
        oh_version=version,
        oh_page=pagename,
        oh_catalogue=catalogue,
        oh_category_names=CATEGORY_NAMES,
        oh_category_docs=CATEGORY_DOCS,
        oh_entries=entries,
        oh_workflows=workflows,
        oh_access_labels=ACCESS_LABELS,
        oh_applications=json.loads((ROOT / "data/applications.json").read_text()),
    )
    standalone_templates = {
        "index": "home-content.html",
        "catalogue": "catalogue-content.html",
        "research": "research-content.html",
    }
    if pagename in standalone_templates or pagename.startswith("research/"):
        if pagename == "index":
            context["title"] = "One package for computational pathology"
        context["theme_secondary_sidebar_items"] = []
        context["secondary_sidebar_items"] = []
        context["sidebars"] = []
        context["body"] = app.builder.templates.render(
            standalone_templates.get(pagename, "research-detail.html"),
            context,
        )
    return None


def setup(app):
    app.connect("html-page-context", page_context)
