#!/usr/bin/env python3
"""Audit the built website without network requests or model execution.

Checks published files/anchors, automatic asset loads, private environment
details, catalogue completeness, snapshot labelling and Python example syntax.
Run with the website virtual environment (Beautiful Soup is required).
"""

from __future__ import annotations

import argparse
import ast
import ipaddress
import json
import os
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup, Tag

SITE_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COMPONENTS = 79
PRIVATE_MARKERS = {
    "operator home path": r"/Users/",
    "server workspace path": r"/workspace/",
    "operator temporary path": r"/private/tmp/",
    "SSH identity filename": r"\bid_(?:ed25519|rsa|ecdsa)(?:\.pub)?\b",
    "private key": r"-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----",
    "SSH connection": r"\bssh://|\b(?:ssh|scp)\s+[^\n<]{0,150}@",
    "remote pod hostname": r"\b[\w.-]+\.(?:runpod\.net|proxy\.runpod\.net)\b",
}
IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
CSS_IMPORT = re.compile(r"@import\s+['\"]([^'\"]+)['\"]", re.IGNORECASE)
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
REMOTE_JS = re.compile(
    r"(?:\b(?:fetch|importScripts|WebSocket|EventSource)\s*\(|"
    r"\.sendBeacon\s*\(|\.open\s*\(\s*['\"](?:GET|POST|PUT|HEAD)['\"]\s*,|"
    r"(?:\.src|\.href)\s*=|\bimport\s*\(?)\s*['\"](?:https?:)?//",
    re.IGNORECASE,
)
DEMO_PATH = re.compile(
    r"(?:^|/)(?:webpack[^/]*|examples|user_guide|community|kitchen-sink)(?:/|\.|$)"
)
AUTO_LINK_RELS = {
    "stylesheet",
    "icon",
    "apple-touch-icon",
    "apple-touch-icon-precomposed",
    "mask-icon",
    "preload",
    "prefetch",
    "modulepreload",
    "preconnect",
    "dns-prefetch",
    "manifest",
}


class SiteAudit:
    """Accumulate actionable failures while inspecting one generated website."""

    def __init__(self, source_root: Path, build_root: Path):
        self.source_root = source_root.resolve()
        self.build_root = build_root.resolve()
        self.errors: list[str] = []
        self.counts: Counter[str] = Counter()
        self.pages: dict[Path, BeautifulSoup] = {}

    def label(self, path: Path) -> str:
        """Describe evidence relative to the site, without operator paths."""
        for root in (self.build_root, self.source_root):
            if path.is_relative_to(root):
                return path.relative_to(root).as_posix()
        return path.name

    def fail(self, path: Path, message: str) -> None:
        """Retain an error with its portable evidence location."""
        self.errors.append(f"{self.label(path)}: {message}")

    def local_target(self, owner: Path, link: Tag) -> Path | None:
        """Resolve a navigation destination without requesting external URLs."""
        parts = urlsplit(link.get("href", ""))
        if parts.scheme or parts.netloc or not parts.path:
            return None
        return (
            self.build_root / unquote(parts.path).lstrip("/")
            if parts.path.startswith("/")
            else owner.parent / unquote(parts.path)
        ).resolve()

    def artifacts(self) -> None:
        """Reject build caches, stale pages and private paths in every artifact."""
        if not self.build_root.is_dir():
            self.fail(self.build_root, "HTML artifact directory is missing")
            return
        if not (self.build_root / ".nojekyll").is_file():
            self.fail(self.build_root, "HTML artifact is missing .nojekyll")
        cache_names = {
            ".git",
            ".doctrees",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
            ".cache",
            ".venv",
            "node_modules",
        }
        cache_suffixes = {
            ".pickle",
            ".pkl",
            ".doctree",
            ".pyc",
            ".pyo",
            ".bak",
            ".tmp",
            ".swp",
        }
        for directory, directories, filenames in os.walk(self.build_root):
            for name in list(directories):
                if name in cache_names:
                    self.fail(
                        Path(directory) / name,
                        "build/cache directory is inside the HTML artifact",
                    )
                    directories.remove(name)
            for name in filenames:
                path = Path(directory) / name
                if (
                    path.suffix.lower() in cache_suffixes
                    or name == ".buildinfo"
                    or name == ".env"
                    or name.startswith(".env.")
                ):
                    self.fail(
                        path, "cache, backup or private-environment file is published"
                    )
                payload = path.read_bytes()
                for description, pattern in PRIVATE_MARKERS.items():
                    if re.search(pattern.encode("utf-8"), payload, re.IGNORECASE):
                        self.fail(
                            path, f"private environment detail found ({description})"
                        )
                self.counts["artifact_files"] += 1

        for page in self.build_root.rglob("*.html"):
            relative = page.relative_to(self.build_root)
            if any(part.startswith("_") for part in relative.parts):
                continue
            if relative.as_posix() in {"search.html", "genindex.html"}:
                continue
            if not any(
                (self.source_root / relative.with_suffix(suffix)).is_file()
                for suffix in (".md", ".rst")
            ):
                self.fail(
                    page, "stale product HTML has no corresponding source document"
                )

    def reference(self, owner: Path, value: str, *, automatic: bool = False) -> None:
        """Check a local resource/anchor, allowing ordinary external hyperlinks."""
        value = value.strip()
        if not value:
            return
        parts = urlsplit(value)
        if parts.scheme == "data":
            return
        if parts.scheme == "file":
            self.fail(owner, "file: URL is not a portable published link")
            return
        if parts.scheme or parts.netloc:
            if automatic:
                self.fail(owner, "automatic asset/dependency uses an external URL")
            self.counts["external_links_not_requested"] += 1
            return
        target = (
            self.build_root / unquote(parts.path).lstrip("/")
            if parts.path.startswith("/")
            else owner.parent / unquote(parts.path)
            if parts.path
            else owner
        ).resolve()
        if not target.is_relative_to(self.build_root):
            self.fail(owner, "local reference escapes the published build root")
            return
        if target.is_dir():
            target /= "index.html"
        if not target.is_file():
            self.fail(owner, f"missing published target: {self.label(target)}")
            return
        self.counts["local_references"] += 1
        if owner.suffix == ".html" and DEMO_PATH.search(
            target.relative_to(self.build_root).as_posix()
        ):
            self.fail(
                owner,
                f"link points to an upstream theme/demo page: {self.label(target)}",
            )
        if parts.fragment and target.suffix == ".html":
            soup = self.pages.get(target)
            if soup is None:
                soup = BeautifulSoup(target.read_text(encoding="utf-8"), "html.parser")
            fragment = unquote(parts.fragment)
            if not soup.find(id=fragment) and not soup.find(
                "a", attrs={"name": fragment}
            ):
                self.fail(owner, f"missing anchor: {self.label(target)}#{fragment}")
            self.counts["anchors"] += 1

    def css(self, owner: Path, text: str) -> None:
        """Check CSS imports and font/image URLs relative to their stylesheet."""
        text = CSS_COMMENT.sub("", text)
        for match in CSS_URL.finditer(text):
            self.reference(owner, match[2].strip(), automatic=True)
        for match in CSS_IMPORT.finditer(text):
            self.reference(owner, match[1], automatic=True)

    def javascript(self, owner: Path, text: str) -> None:
        """Detect direct remote requests without rejecting upstream license URLs."""
        if REMOTE_JS.search(text):
            self.fail(owner, "script contains a direct remote network request/load")

    @staticmethod
    def visible(node: Tag) -> bool:
        """Exclude headings explicitly hidden by markup or accessibility classes."""
        for parent in (node, *node.parents):
            if not isinstance(parent, Tag):
                continue
            if parent.has_attr("hidden") or parent.get("aria-hidden") == "true":
                return False
            if {"sr-only", "visually-hidden"}.intersection(parent.get("class", [])):
                return False
            if re.search(
                r"(?:display\s*:\s*none|visibility\s*:\s*hidden)",
                parent.get("style", ""),
            ):
                return False
        return True

    def html(self) -> None:
        """Inspect product pages and all linked assets, without browsing or fetching."""
        paths = sorted(
            path
            for path in self.build_root.rglob("*.html")
            if not any(
                part.startswith("_") for part in path.relative_to(self.build_root).parts
            )
        )
        if not paths:
            self.fail(
                self.build_root, "no built product HTML found; build the site first"
            )
            return
        self.pages = {
            path: BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
            for path in paths
        }
        home = self.pages.get(self.build_root / "index.html")
        if home is not None and not home.select_one('link[rel~="icon"][href]'):
            self.fail(
                self.build_root / "index.html", "root page has no favicon declaration"
            )
        for path, soup in self.pages.items():
            self.counts["html_pages"] += 1
            raw = path.read_text(encoding="utf-8")
            for description, pattern in PRIVATE_MARKERS.items():
                if re.search(pattern, raw, flags=re.IGNORECASE):
                    self.fail(path, f"private environment detail found ({description})")
            for match in IPV4.finditer(raw):
                try:
                    address = ipaddress.ip_address(match[0])
                except ValueError:
                    continue
                if not address.is_loopback and not address.is_unspecified:
                    self.fail(path, "literal operator/server IP address found")
                    break
            headings = [node for node in soup.select("h1") if self.visible(node)]
            if len(headings) != 1:
                self.fail(path, f"expected one visible H1, found {len(headings)}")
            for node in soup.find_all(True):
                for attribute in (
                    "href",
                    "src",
                    "action",
                    "data",
                    "poster",
                    "xlink:href",
                ):
                    value = node.get(attribute)
                    if not isinstance(value, str):
                        continue
                    automatic = (
                        attribute in {"src", "poster", "xlink:href"}
                        or (node.name == "object" and attribute == "data")
                        or (
                            node.name == "link"
                            and bool(AUTO_LINK_RELS.intersection(node.get("rel", [])))
                        )
                    )
                    self.reference(path, value, automatic=automatic)
                if node.get("srcset"):
                    for item in node["srcset"].split(","):
                        if item.strip():
                            self.reference(
                                path, item.strip().split()[0], automatic=True
                            )
                if node.get("ping"):
                    self.fail(path, "hyperlink ping/telemetry is enabled")
                if node.get("style"):
                    self.css(path, node["style"])
                if node.name == "style":
                    self.css(path, node.get_text())
                if node.name == "script" and not node.get("src"):
                    self.javascript(path, node.get_text())
        for path in self.build_root.rglob("*.css"):
            self.css(path, path.read_text(encoding="utf-8"))
            self.counts["css_files"] += 1
        for path in self.build_root.rglob("*.js"):
            self.javascript(path, path.read_text(encoding="utf-8"))
            self.counts["js_files"] += 1

    def python(self, owner: Path, code: str, name: str) -> None:
        """Compile an example to Python's syntax tree without executing any code."""
        try:
            ast.parse(code, filename=name)
        except SyntaxError as exc:
            self.fail(
                owner,
                f"Python example {name!r} has invalid syntax "
                f"at line {exc.lineno}: {exc.msg}",
            )
        self.counts["python_examples"] += 1

    def catalogue(self) -> None:
        """Compare rendered entries, counters and copyable examples to source data."""
        path = self.source_root / "data/catalogue.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = {
            f"model-{category}-{item['id']}": item
            for category, items in data["categories"].items()
            for item in items
        }
        actual_total = sum(len(items) for items in data["categories"].values())
        if len(entries) != actual_total or actual_total != EXPECTED_COMPONENTS:
            self.fail(
                path,
                f"expected {EXPECTED_COMPONENTS} unique components, "
                f"found {len(entries)}/{actual_total}",
            )
        counts = {key: len(items) for key, items in data["categories"].items()}
        if data["summary"] != {"total": actual_total, "counts": counts}:
            self.fail(path, "catalogue summary does not match actual category contents")
        page = self.build_root / "catalogue.html"
        soup = self.pages.get(page)
        if soup is None:
            self.fail(page, "catalogue page is missing")
            return
        rows = soup.select(".oh-model-row")
        ids = [node.get("id") for node in rows]
        if len(set(ids)) != len(ids) or set(ids) != set(entries):
            self.fail(
                page,
                "rendered catalogue IDs are duplicated "
                "or differ from the source catalogue",
            )
        for node in rows:
            item = entries.get(node.get("id"))
            if item is None:
                continue
            code = node.select_one("pre")
            if code is None or code.get_text().strip() != item["example"].strip():
                self.fail(
                    page, f"copyable example differs from source for {node.get('id')}"
                )
        for node in soup.select("[data-category][aria-pressed]"):
            category = node["data-category"]
            expected = actual_total if category == "all" else counts.get(category)
            match = re.search(r"(\d+)\s*$", node.get_text(" ", strip=True))
            if expected is None or not match or int(match[1]) != expected:
                self.fail(page, f"category filter count is incorrect for {category}")
        status = soup.select_one("#oh-result-count")
        if status is None or str(actual_total) not in status.get_text():
            self.fail(page, "initial result count does not match the full catalogue")
        for identifier, item in entries.items():
            self.python(path, item["example"], identifier)
        self.counts["catalogue_components"] = len(entries)

    def workflows(self) -> None:
        """Check workflow source examples and Markdown Python fences."""
        path = self.source_root / "data/workflows.json"
        for item in json.loads(path.read_text(encoding="utf-8")):
            self.python(path, item["code"], item["id"])
        guides = [self.source_root / "catalogue.md"]
        guides.extend(sorted((self.source_root / "content").glob("*.md")))
        for path in guides:
            relative = path.relative_to(self.source_root).as_posix()
            code = None
            marker = None
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1
            ):
                fence = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
                if fence:
                    if marker is None:
                        marker = fence[1]
                        code = (
                            []
                            if fence[2].strip() in {"python", "py", "python3"}
                            else None
                        )
                        start = number + 1
                    elif (
                        fence[1][0] == marker[0]
                        and len(fence[1]) >= len(marker)
                        and not fence[2].strip()
                    ):
                        if code is not None:
                            self.python(path, "\n".join(code), f"{relative}:{start}")
                        marker, code = None, None
                elif code is not None:
                    code.append(line)

    def snapshot(self) -> None:
        """Check the dated benchmark snapshot within its research navigation."""
        path = self.build_root / "research/benchmark.html"
        soup = self.pages.get(path)
        if soup is None:
            self.fail(path, "benchmark detail page is missing")
            return
        text = soup.get_text(" ", strip=True)
        progress = soup.select_one(
            '[role="progressbar"][aria-valuenow="96"][aria-valuemax="897"]'
        )
        if progress is None:
            self.fail(
                path, "supplied campaign snapshot must retain 96/897 patient progress"
            )
        elif "snapshot" not in (progress.get("aria-label", "") + text).lower():
            self.fail(path, "campaign progress is not labelled as a snapshot")
        if not re.search(r"\b30\s+Oct(?:ober)?\s+2026\b", text, re.IGNORECASE):
            self.fail(path, "supplied campaign snapshot is missing its date")
        if "scientific evaluation is not complete" not in text.lower():
            self.fail(
                path,
                "campaign preparation is missing its scientific-completion limitation",
            )

        parent = self.build_root / "research.html"
        applications = self.pages.get(parent)
        if applications is None:
            self.fail(parent, "research and applications parent page is missing")
        elif not any(
            self.local_target(parent, link) == path
            for link in applications.select("a[href]")
        ):
            self.fail(parent, "research page does not link to benchmark detail")

        home = self.build_root / "index.html"
        homepage = self.pages.get(home)
        if homepage is None:
            self.fail(home, "home page is missing")
            return
        navigation = [
            self.local_target(home, link)
            for link in homepage.select("header nav a[href]")
        ]
        if parent not in navigation:
            self.fail(
                home, "primary navigation does not link to research and applications"
            )
        if path in navigation:
            self.fail(
                home, "benchmark detail remains a top-level navigation destination"
            )

    def research(self) -> None:
        """Check standalone project pages against their declared resources."""
        for relative, body_class in (
            ("research.html", "oh-research-page"),
            ("research/benchmark.html", "oh-study-page"),
        ):
            path = self.build_root / relative
            soup = self.pages.get(path)
            if soup is None:
                self.fail(path, "standalone research page is missing")
                continue
            classes = soup.body.get("class", []) if soup.body else []
            if body_class not in classes or "oh-docs" in classes:
                self.fail(path, "research page is using the documentation shell")
            if soup.select_one(
                '.oh-doc-nav, nav[aria-label="Documentation sections"], '
                ".oh-mobile-docbar, .sidebar-toggle.primary-toggle"
            ):
                self.fail(
                    path, "research page contains documentation navigation controls"
                )

        source = self.source_root / "data/applications.json"
        projects = json.loads(source.read_text(encoding="utf-8"))["projects"]
        expected = {project["id"]: project for project in projects}
        if len(expected) != len(projects):
            self.fail(source, "research project IDs are duplicated")
        path = self.build_root / "research.html"
        soup = self.pages.get(path)
        if soup is None:
            return
        nodes = soup.select("article[data-project-id]")
        ids = [node["data-project-id"] for node in nodes]
        if len(set(ids)) != len(ids) or set(ids) != set(expected):
            self.fail(path, "rendered research projects differ from applications data")
        for node in nodes:
            identifier = node["data-project-id"]
            project = expected.get(identifier)
            if project is None:
                continue
            text = " ".join(node.get_text(" ", strip=True).split())
            for key in ("title", "status"):
                if " ".join(project[key].split()) not in text:
                    self.fail(
                        path, f"project {identifier} is missing its declared {key}"
                    )
            detail = self.build_root / (project["detail"] + ".html")
            links = node.select("a[href]")
            if not any(self.local_target(path, link) == detail for link in links):
                self.fail(
                    path, f"project {identifier} does not link to its detail page"
                )
            resources = {
                item["url"]: item
                for item in [*project["links"], *project.get("resources", [])]
            }
            rendered = {
                link["href"]
                for link in links
                if urlsplit(link["href"]).scheme in {"http", "https"}
            }
            if rendered != set(resources):
                self.fail(
                    path,
                    f"project {identifier} resources differ from applications data",
                )
            for url, resource in resources.items():
                parts = urlsplit(url)
                if (
                    parts.scheme != "https"
                    or not parts.hostname
                    or parts.username is not None
                    or parts.password is not None
                    or re.search(r"\s", url)
                ):
                    self.fail(
                        source,
                        f"project {identifier} has an invalid HTTPS resource URL",
                    )
                matches = [link for link in links if link["href"] == url]
                for link in matches:
                    if link.get("target") != "_blank" or "noopener" not in link.get(
                        "rel", []
                    ):
                        self.fail(
                            path,
                            f"project {identifier} resource lacks "
                            "safe new-tab attributes",
                        )
                    if resource["label"] not in link.get_text(" ", strip=True):
                        self.fail(
                            path, f"project {identifier} resource has no declared label"
                        )
                self.counts["research_resources"] += 1
        self.counts["research_projects"] = len(expected)

    def run(self) -> int:
        """Run the audit and print a concise, portable result."""
        self.artifacts()
        self.html()
        for check in (self.catalogue, self.workflows, self.snapshot, self.research):
            try:
                check()
            except (OSError, KeyError, TypeError, ValueError) as exc:
                self.errors.append(
                    f"{check.__name__}: cannot inspect required evidence "
                    f"({type(exc).__name__})"
                )
        summary = ", ".join(
            f"{key}={value}" for key, value in sorted(self.counts.items())
        )
        if self.errors:
            print(f"Site audit FAILED ({len(self.errors)} errors): {summary}")
            for message in sorted(set(self.errors)):
                print(f"  - {message}")
            return 1
        print(f"Site audit PASSED: {summary}")
        print(
            "External hyperlinks were not fetched; checks executed no model examples."
        )
        return 0


def main(argv: list[str] | None = None) -> int:
    """Audit the normal site build or an explicitly supplied source/build pair."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=SITE_ROOT)
    parser.add_argument("--build-root", type=Path, default=SITE_ROOT / "_build/html")
    args = parser.parse_args(argv)
    return SiteAudit(args.source_root, args.build_root).run()


if __name__ == "__main__":
    raise SystemExit(main())
