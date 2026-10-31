#!/usr/bin/env python3
"""Copy the package's public guides into the standalone Sphinx reference.

This uses only the standard library. It reads Markdown and Git metadata; it
never imports OpenHisto or executes code examples. Run with ``--check`` to
verify that committed/generated reference files match their source guides.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

REPOSITORY = "https://github.com/OpenHist/OpenHistology_Package"
SITE_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Guide:
    """Map one package document to its website page and stable title."""

    source: str
    output: str
    title: str


GUIDES = (
    Guide("README.md", "package.md", "Package overview"),
    Guide("src/openhisto/default_datasets/README.md", "datasets.md", "Datasets"),
    Guide(
        "src/openhisto/patch_extraction/README.md",
        "patch-extraction.md",
        "Patch extraction",
    ),
    Guide(
        "src/openhisto/stain_transfer/README.md",
        "normalization.md",
        "Normalization and stain transfer",
    ),
    Guide("src/openhisto/feature_encoder/README.md", "features.md", "Feature encoding"),
    Guide(
        "src/openhisto/segmentation/README.md",
        "segmentation.md",
        "Semantic segmentation",
    ),
    Guide("src/openhisto/vlas/README.md", "vla.md", "Vision-language descriptions"),
    Guide("src/openhisto/mil/models/code_bases/README.md", "mil.md", "MIL backbones"),
    Guide(
        "src/openhisto/mil/heads/README.md",
        "heads.md",
        "Classification and survival heads",
    ),
    Guide("src/openhisto/mil/classification/README.md", "classifiers.md", "Classifiers"),
    Guide("src/openhisto/mil/survival/README.md", "survival.md", "Survival heads"),
    Guide(
        "src/openhisto/mil/models/code_bases/COVERAGE.md",
        "mil-coverage.md",
        "MIL verification coverage",
    ),
    Guide(
        "src/openhisto/mil/heads/COVERAGE.md",
        "heads-coverage.md",
        "Head verification coverage",
    ),
    Guide(
        "src/openhisto/mil/heads/README_BINDINGS.md",
        "head-bindings.md",
        "MIL representation bindings",
    ),
)

INLINE_LINK = re.compile(
    r"(?P<start>!?\[[^\]\n]*\]\()"
    r"(?P<target><[^>\n]+>|[^\s)]+)"
    r"(?P<end>(?:[ \t]+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\))"
)
REFERENCE_LINK = re.compile(r"^(?P<start>[ \t]{0,3}\[[^\]\n]+\]:[ \t]*)(?P<target><[^>\n]+>|\S+)")
HTML_LINK = re.compile(r"(?P<start>\b(?:href|src)=[\"'])(?P<target>[^\"']+)(?P<end>[\"'])")
FENCE = re.compile(r"^[ \t]{0,3}(?P<fence>`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+)(.*?)\1", re.DOTALL)


def source_url(path: str, source_ref: str, *, query: str = "", fragment: str = "") -> str:
    """Build a repository URL without exposing local filesystem locations."""
    url = f"{REPOSITORY}/blob/{quote(source_ref, safe='')}/{quote(path, safe='/')}"
    return urlunsplit((*urlsplit(url)[:3], query, fragment))


def rewrite_target(target: str, guide: Guide, source_ref: str, mapping: dict[str, str]) -> str:
    """Resolve relative source links against the original README location."""
    angled = target.startswith("<") and target.endswith(">")
    value = target[1:-1] if angled else target
    parts = urlsplit(value)
    if parts.scheme or parts.netloc or not parts.path:
        return target
    if parts.path.startswith("/"):
        # GitHub root-relative links refer to the repository, not this website.
        resolved = posixpath.normpath(unquote(parts.path).lstrip("/"))
    else:
        resolved = posixpath.normpath(
            posixpath.join(posixpath.dirname(guide.source), unquote(parts.path))
        )
    if resolved == ".." or resolved.startswith("../"):
        raise ValueError(f"Link escapes the package source tree in {guide.source}: {value}")
    if resolved in mapping:
        destination = posixpath.relpath(mapping[resolved], posixpath.dirname(guide.output) or ".")
        rewritten = urlunsplit(("", "", destination, parts.query, parts.fragment))
    else:
        rewritten = source_url(resolved, source_ref, query=parts.query, fragment=parts.fragment)
    return f"<{rewritten}>" if angled else rewritten


def rewrite_prose(text: str, guide: Guide, source_ref: str, mapping: dict[str, str]) -> str:
    """Rewrite Markdown and HTML links while retaining literal inline code."""

    def rewrite(match: re.Match[str]) -> str:
        return (
            match["start"]
            + rewrite_target(match["target"], guide, source_ref, mapping)
            + match.groupdict().get("end", "")
        )

    # A Markdown label may contain inline code, e.g. [`module`](README.md).
    # Skip links whose *start* lies in a code span, rather than splitting labels.
    def outside_code(pattern: re.Pattern[str], value: str) -> str:
        spans = [(match.start(), match.end()) for match in INLINE_CODE.finditer(value)]
        return pattern.sub(
            lambda match: (
                match[0]
                if any(start <= match.start() < end for start, end in spans)
                else rewrite(match)
            ),
            value,
        )

    for pattern in (REFERENCE_LINK, INLINE_LINK, HTML_LINK):
        text = outside_code(pattern, text)
    return text


def render_guide(text: str, guide: Guide, source_ref: str, mapping: dict[str, str]) -> str:
    """Preserve a complete source guide with website links and source attribution."""
    lines = text.splitlines(keepends=True)
    rendered = []
    fence = None
    first_heading = True
    for line in lines:
        marker = FENCE.match(line)
        if marker:
            current = marker["fence"]
            if fence is None:
                fence = current
                # Pygments has no built-in CSV lexer. Keep the example bytes,
                # displaying that fence as plain text for warning-free Sphinx.
                if line[marker.end() :].strip() == "csv":
                    line = line[: marker.end()] + "text\n"
            elif (
                current[0] == fence[0]
                and len(current) >= len(fence)
                and not line[marker.end() :].strip()
            ):
                fence = None
            rendered.append(line)
        elif fence is not None:
            rendered.append(line)
        elif first_heading and line.startswith("# "):
            rendered.append(f"# {guide.title}\n")
            first_heading = False
        else:
            rendered.append(rewrite_prose(project_voice(line, guide), guide, source_ref, mapping))
    if first_heading:
        rendered.insert(0, f"# {guide.title}\n\n")
    footer = (
        "\n\n---\n\n"
        f"Source: [{guide.source}]({source_url(guide.source, source_ref)}). "
        "Source and example links point to the private OpenHistology_Package repository "
        "and require repository access.\n"
    )
    return (
        "<!-- Generated by tools/sync_package_docs.py "
        "from the package documentation. -->\n\n" + "".join(rendered).rstrip() + footer
    )


def project_voice(line: str, guide: Guide) -> str:
    """Adapt website prose while retaining examples and upstream attribution."""
    replacements = {
        "package.md": {
            "OpenHisto's original code is maintained by Abteen Arab and distributed under": "We maintain OpenHisto's original code and distribute it under",
        },
        "vla.md": {
            "Authors' complete checkpoint and matching implementation required": "We plan to add complete PathChat+ inference support in a future release",
            "Unavailable; selecting it explains the access requirement": "Planned integration; built-in inference is not yet available",
            "PathChat+ requires direct access from its authors": "Our planned PathChat+ integration depends on restricted model access",
            "the authors' conversion workflow": "the upstream conversion workflow",
            "authors' extracted PLIP directory": "prepared upstream PLIP directory",
            "with the actual author artifacts on the target GPU.": "with the prepared model artifacts on the target GPU.",
        },
    }
    for original, replacement in replacements.get(guide.output, {}).items():
        line = line.replace(original, replacement)
    return line


def render_index() -> str:
    """List every generated guide in the reference navigation."""
    main = "\n".join(guide.output.removesuffix(".md") for guide in GUIDES[:11])
    supporting = "\n".join(guide.output.removesuffix(".md") for guide in GUIDES[11:])
    return f"""# Package reference

The complete package guides cover native Python APIs, command-line usage,
input and output formats, model access, recovery, and verification limits.
Examples are documentation; building this site does not run models or download data.

```{{toctree}}
:maxdepth: 1
:caption: Modules and workflows

{main}
```

```{{toctree}}
:maxdepth: 1
:caption: Verification and representation contracts

{supporting}
```

The source links throughout these guides refer to the private
[OpenHistology_Package repository]({REPOSITORY}) and require repository access.
Third-party source and license notices remain in the module guides.
"""


def discover_ref(package_root: Path) -> str:
    """Pin links to the current source revision when Git metadata is available."""
    try:
        result = subprocess.run(
            ["git", "-C", str(package_root), "rev-parse", "HEAD"],
            check=True,
            text=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "main"
    return result.stdout.strip()


def generate(package_root: Path, source_ref: str) -> dict[str, str]:
    """Render all guides and a deterministic, path-portable provenance manifest."""
    mapping = {guide.source: guide.output for guide in GUIDES}
    outputs = {"index.md": render_index()}
    sources = []
    for guide in GUIDES:
        source = (package_root / guide.source).read_text(encoding="utf-8")
        output = render_guide(source, guide, source_ref, mapping)
        outputs[guide.output] = output
        sources.append(
            {
                "source": guide.source,
                "page": guide.output,
                "title": guide.title,
                "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "page_sha256": hashlib.sha256(output.encode()).hexdigest(),
            }
        )
    outputs["provenance.json"] = (
        json.dumps(
            {
                "schema_version": 1,
                "source_repository": REPOSITORY,
                "source_ref": source_ref,
                "source_access": "private repository; access required",
                "generation": ("Markdown source only; no package imports or example execution"),
                "guides": sources,
            },
            indent=2,
        )
        + "\n"
    )
    return outputs


def main(argv: list[str] | None = None) -> int:
    """Generate the reference pages, or check their freshness without writing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package-root",
        type=Path,
        required=True,
        help="Path to the authorized local OpenHistology_Package checkout.",
    )
    parser.add_argument("--output-dir", type=Path, default=SITE_ROOT / "reference")
    parser.add_argument(
        "--source-ref",
        help=("Git commit/ref for source links; defaults to package HEAD, or main outside Git"),
    )
    parser.add_argument(
        "--check", action="store_true", help="Check freshness without writing files"
    )
    args = parser.parse_args(argv)
    source_ref = args.source_ref or discover_ref(args.package_root)
    outputs = generate(args.package_root, source_ref)
    if args.check:
        stale = [
            name
            for name, content in outputs.items()
            if not (args.output_dir / name).is_file()
            or (args.output_dir / name).read_text(encoding="utf-8") != content
        ]
        if stale:
            print("Reference pages need regeneration: " + ", ".join(stale))
            return 1
        print(f"Reference documentation is current ({len(GUIDES)} source guides).")
        return 0
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        (args.output_dir / name).write_text(content, encoding="utf-8")
    print(f"Generated {len(GUIDES)} source guides, index and provenance manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
