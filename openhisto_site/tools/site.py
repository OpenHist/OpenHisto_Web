"""Build, sync or preview the standalone OpenHisto website locally."""

import shutil
import subprocess
import sys
from argparse import ArgumentParser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "_build/html"
DOCTREES = ROOT / "_build/doctrees"


def build():
    """Build committed documentation snapshots without a package checkout."""
    if BUILD.exists():
        shutil.rmtree(BUILD)
    subprocess.run([sys.executable, str(ROOT / "tools/prepare_site.py")], check=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-n",
            "-W",
            "--keep-going",
            "-E",
            "-a",
            "-d",
            str(DOCTREES),
            "-b",
            "html",
            str(ROOT),
            str(BUILD),
        ],
        check=True,
    )
    (BUILD / ".buildinfo").unlink(missing_ok=True)
    (BUILD / ".nojekyll").write_text("", encoding="utf-8")


def sync(package_root):
    """Refresh committed snapshots from an explicitly selected local package."""
    for script, option in (
        ("sync_package_docs.py", "--package-root"),
        ("build_catalogue.py", "--package"),
    ):
        subprocess.run(
            [sys.executable, str(ROOT / "tools" / script), option, str(package_root)],
            check=True,
        )
    subprocess.run([sys.executable, str(ROOT / "tools/prepare_site.py")], check=True)


def main():
    """Run a local build, explicit source sync, artifact check or preview."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["build", "sync", "serve", "check"])
    parser.add_argument("--port", type=int, default=8050)
    parser.add_argument(
        "--package-root", type=Path, help="Local package checkout for the sync command"
    )
    args = parser.parse_args()
    if args.command == "build":
        build()
    elif args.command == "sync":
        if args.package_root is None:
            parser.error("sync requires --package-root PATH")
        sync(args.package_root.resolve())
    elif args.command == "check":
        subprocess.run([sys.executable, str(ROOT / "tools/check_site.py")], check=True)
    else:
        if not (BUILD / "index.html").is_file():
            build()
        address = ("127.0.0.1", args.port)
        server = ThreadingHTTPServer(
            address, partial(SimpleHTTPRequestHandler, directory=str(BUILD))
        )
        print(f"OpenHisto local preview: http://127.0.0.1:{args.port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
