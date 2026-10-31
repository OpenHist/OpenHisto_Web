"""Prepare local, deterministic illustrations and searchable catalogue text."""

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tissue_svg():
    rng = random.Random(1729)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 520">',
        '<defs><filter id="soft"><feGaussianBlur stdDeviation="0.5"/></filter>',
        '<pattern id="grain" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M2 4 8 7M27 31l6-2" stroke="#b57794" opacity=".12"/></pattern></defs>',
        '<rect width="680" height="520" fill="#f2d8da"/>',
    ]
    for i in range(30):
        x, y = rng.randrange(-20, 700), rng.randrange(-20, 540)
        rx, ry = rng.randrange(30, 100), rng.randrange(12, 36)
        color = rng.choice(["#e4b2c0", "#eac0ca", "#dba6bc", "#e6b4bc", "#f6e5df"])
        parts.append(
            f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" transform="rotate({rng.randrange(-70, 70)} {x} {y})" fill="{color}" opacity=".65"/>'
        )
    for y in range(-12, 550, 22):
        for x in range(-12, 710, 24):
            cx = x + rng.uniform(-11, 11)
            cy = y + rng.uniform(-10, 10)
            # Branching acellular clefts make the schematic read as tissue.
            cleft = abs(cx - (320 + 90 * math.sin(cy / 75))) < 19
            if cleft or rng.random() < 0.12:
                continue
            rx, ry = rng.uniform(3.1, 6.4), rng.uniform(5, 9.1)
            angle = rng.randrange(-85, 85)
            parts.append(
                f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx + 4:.1f}" ry="{ry + 3:.1f}" transform="rotate({angle} {cx:.1f} {cy:.1f})" fill="#dda5bc" opacity=".44"/>'
            )
            parts.append(
                f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" transform="rotate({angle} {cx:.1f} {cy:.1f})" fill="{rng.choice(["#67446e", "#7f4c7f", "#97628f", "#79537f"])}" opacity="{rng.uniform(0.62, 0.94):.2f}"/>'
            )
    parts.extend(['<rect width="680" height="520" fill="url(#grain)"/>', "</svg>"])
    return "".join(parts)


def mask_svg():
    rng = random.Random(1729)
    colors = ["#c2d6bc", "#b8a5c6", "#dfa9bc", "#edd4a8", "#9fb8be"]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 250"><rect width="360" height="250" fill="#eeece5"/>'
    ]
    for y in range(17, 250, 31):
        for x in range(17, 360, 31):
            if rng.random() < 0.12:
                continue
            cx, cy = x + rng.randrange(-7, 8), y + rng.randrange(-7, 8)
            points = []
            for k in range(9):
                angle = k * 2 * math.pi / 9
                radius = rng.uniform(7, 13)
                points.append(
                    f"{cx + radius * math.cos(angle):.1f},{cy + radius * math.sin(angle):.1f}"
                )
            parts.append(
                f'<polygon points="{" ".join(points)}" fill="{rng.choice(colors)}" stroke="#687a64" stroke-width=".7"/>'
            )
    parts.append("</svg>")
    return "".join(parts)


def prepare():
    static = ROOT / "_static"
    (static / "tissue-schematic.svg").write_text(tissue_svg())
    (static / "mask-schematic.svg").write_text(mask_svg())
    data = json.loads((ROOT / "data/catalogue.json").read_text())
    lines = [
        "---",
        "html_theme.sidebar_secondary.remove: true",
        "---",
        "",
        "# Model catalogue",
        "",
        "Explore package components by model name, task, native input contract and access requirements.",
        "",
    ]
    # This text is indexed by Sphinx; the visible explorer uses the same data.
    for entries in data["categories"].values():
        for entry in entries:
            lines.extend(
                [
                    f"**{entry['name']}** (`{entry['id']}`) — {entry['description']}",
                    f"Category: {entry['category']}. Tasks: {', '.join(entry['tasks'])}. Access: {entry['access']}.",
                    "",
                ]
            )
    (ROOT / "catalogue.md").write_text("\n".join(lines))
    applications = json.loads((ROOT / "data/applications.json").read_text())
    research = [
        "---", "html_theme.sidebar_secondary.remove: true", "---", "",
        "# Research & applications", "",
        "Studies and projects built with OpenHisto, with project links and research resources.", "",
    ]
    for project in applications["projects"]:
        research.extend([
            f"## {project['title']}", "",
            f"{project['status']} · {project['category']}", "", project["summary"], "",
            f"[Study overview]({project['detail']}.md)", "",
        ])
        for action in project.get("actions", []):
            research.extend([action["label"], ""])
        for link in project["links"] + project.get("resources", []):
            research.extend([f"[{link['label']}]({link['url']})", ""])
    research.extend([
        "```{toctree}", ":hidden:", ":maxdepth: 1", "",
        *(project["detail"] for project in applications["projects"]), "```", "",
    ])
    (ROOT / "research.md").write_text("\n".join(research))
    print("Prepared illustrations, catalogue and research search content.")


if __name__ == "__main__":
    prepare()
